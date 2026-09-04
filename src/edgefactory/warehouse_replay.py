"""Warehouse-reconstruction FEASIBILITY auditor (research only, default OFF).

The question this module exists to answer is NOT "what would the engine have
earned over 2024-2026". It is the prior question:

    Can the live engine's picks be faithfully reconstructed from the data in
    ``localdata/`` at all — which of the live rules, from which sources, over
    which date range?

Nothing here is imported by, or reachable from, the live betting path.
``scripts/auto_tickets.py`` does not import this module; the only entry point
is ``scripts/replay_harness.py --warehouse-replay``, which is opt-in.
:data:`ENABLED_BY_DEFAULT` is ``False`` and is asserted by the test suite.

Why the gate exists (read before "improving" any number below)
--------------------------------------------------------------
A reconstruction that recovers a small, biased slice of the live picks is not
a cheaper version of the engine — it is a *different strategy*, and every
growth/drawdown number it produces is fiction that reads like evidence. The
2026-09-04 session lost time to exactly that: a ``consensus2`` proxy found
~1.3 qualifying legs a day against a live in-season 11.5, and produced a
confident -0.0233 log/day. That number describes the proxy, not the engine.

So: measure recovery FIRST, and refuse to replay until recovery clears a
stated bar. "Cannot be reconstructed faithfully, here is exactly what is
missing" is a complete answer.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

# Research switch. The feasibility audit never runs unless a caller asks for
# it explicitly. Pinned OFF by tests/test_warehouse_replay.py.
ENABLED_BY_DEFAULT = False

# The archive of what the engine actually picked. Any reconstruction has to be
# graded against these days, because they are the only days where ground truth
# ("what did the live engine choose") exists.
ARCHIVE_FIRST_DAY = "2026-06-19"
ARCHIVE_LAST_DAY = "2026-09-06"

# --------------------------------------------------------------------------
# The pass bar, stated up front so the verdict cannot be negotiated after the
# fact. These are deliberately generous: an honest reconstruction of a
# deterministic rule engine from its own inputs should be near-perfect.
# --------------------------------------------------------------------------
GATE_MIN_LEG_RECALL = 0.90       # of live playable legs, recovered
GATE_MIN_LEG_PRECISION = 0.90    # of reconstructed legs, real
GATE_MAX_ODDS_MISMATCH = 0.05    # share of matched legs whose odds differ >1%
GATE_MIN_COVERED_DAYS = 0.90     # share of archived days with any input rows


# --------------------------------------------------------------------------
# What each live rule needs, and where that lives on disk.
# --------------------------------------------------------------------------
# Prediction sources with committed history in localdata/*.csv.gz.
ON_DISK_PREDICTION_SOURCES = frozenset({"forebet", "zulubet", "statarea"})

# Odds sources with any committed history at all. betexplorer_odds is present
# but CLOSING and only 2026-01..2026-06; the engine bets ~30+ minutes before
# kickoff at forebet_best, so the two must never be silently mixed.
ON_DISK_ODDS_SOURCES = frozenset({"forebet_best", "zulubet"})
CLOSING_ONLY_ODDS_SOURCES = frozenset({"betexplorer_odds"})

# Sources the live engine consults that have NO history file in localdata/.
MISSING_PREDICTION_SOURCES = ("vitibet", "bzzoiro", "betclan", "scoutingstats")
MISSING_ODDS_SOURCES = ("scoutingstats_odds", "bzzoiro_odds")


@dataclass(frozen=True)
class RuleSpec:
    """How one live rule would have to be rebuilt from the warehouse."""

    rule: str
    kind: str                       # "source-vote" | "ml-meta"
    needs_sources: tuple[str, ...]  # prediction sources the rule votes over
    view: str | None                # warehouse view that implements it, if any
    note: str = ""


# The four rules that dominate the archive, plus the qualified variants.
RULE_SPECS: tuple[RuleSpec, ...] = (
    RuleSpec("ml-meta avg_p>=55", "ml-meta", ("forebet", "zulubet", "statarea"),
             "consensus3",
             "logistic meta-model; features include in-match half-time score"),
    RuleSpec("2way-unanimous avg_p>=70", "source-vote", ("forebet", "zulubet"),
             "consensus2",
             "warehouse view votes forebet+zulubet only; live votes any 2 of 7"),
    RuleSpec("3way-unanimous avg_p>=65", "source-vote",
             ("forebet", "zulubet", "statarea"), "consensus3",
             "warehouse view votes forebet+zulubet+statarea only"),
    RuleSpec("ml-meta avg_p>=60", "ml-meta", ("forebet", "zulubet", "statarea"),
             "consensus3",
             "same model, higher threshold"),
)


# --------------------------------------------------------------------------
# Look-ahead audit of the ml-meta feature vector.
#
# "pre_kickoff"  - the value is knowable before the ball is kicked
# "post_kickoff" - the value is only knowable during/after the match
# "revised"      - knowable before kickoff in principle, but the stored value
#                  has no capture timestamp, so we cannot prove the archived
#                  value is the pre-kickoff one
# --------------------------------------------------------------------------
ML_META_FEATURE_AVAILABILITY: dict[str, str] = {
    "fb_p": "revised", "zb_p": "revised", "sa_p": "revised",
    "avg_p": "revised", "min_p": "revised", "std_p": "revised",
    "pick_odds": "revised",
    "is_home": "pre_kickoff", "is_away": "pre_kickoff",
    "cat_friendly": "pre_kickoff", "cat_youth": "pre_kickoff",
    "cat_women": "pre_kickoff", "cat_cup": "pre_kickoff",
    "cat_league": "pre_kickoff",
    "rolling_hit_rate": "pre_kickoff",
    "ht_p": "revised",
    "ht_diff": "post_kickoff",     # actual half-time goal difference
    "ht_total": "post_kickoff",    # actual half-time goals scored
    "kelly": "revised",
    "pred_total": "revised", "pred_diff": "revised",
    "goalsavg": "revised",
    "p_ng": "revised", "p_under": "revised", "p_gg": "revised",
    "sa_ht_p": "revised",
}


def classify_ml_features(feature_cols, coefs) -> list[dict]:
    """Tag each trained ml-meta feature with when its value becomes knowable."""
    out = []
    for name, coef in zip(feature_cols, coefs):
        out.append({
            "feature": name,
            "coef": float(coef),
            "availability": ML_META_FEATURE_AVAILABILITY.get(name, "unknown"),
        })
    return sorted(out, key=lambda r: -abs(r["coef"]))


def leak_logit_swing(features: list[dict], ht_diff: float = 2.0,
                     ht_total: float = 2.0) -> float:
    """Logit shift a post-kickoff feature set injects for a given HT score.

    A warehouse replay reads real ``ht_hs``/``ht_gs`` from the settled row, so
    a 2-0 half-time lead would push the model's logit by this much — an edge
    that did not exist at bet time. Live inference has no scores yet and feeds
    zeros, so this is pure replay contamination.
    """
    swing = 0.0
    for f in features:
        if f["availability"] != "post_kickoff":
            continue
        if f["feature"] == "ht_diff":
            swing += f["coef"] * ht_diff
        elif f["feature"] == "ht_total":
            swing += f["coef"] * ht_total
    return swing


# --------------------------------------------------------------------------
# Warehouse inventory
# --------------------------------------------------------------------------
def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False


INVENTORY_TABLES = (
    "forebet_settled", "zulubet_settled", "statarea_settled",
    "vitibet_settled", "bzzoiro", "betclan", "scoutingstats_settled",
    "bettingclosed_settled", "betexplorer_settled",
    "consensus2", "consensus3", "consensus4",
)


def warehouse_inventory(con, tables=INVENTORY_TABLES) -> list[dict]:
    """Per-table presence, row count and date span."""
    rows = []
    for t in tables:
        if not _table_exists(con, t):
            rows.append({"table": t, "present": False, "rows": 0,
                         "first": None, "last": None})
            continue
        try:
            n, lo, hi = con.execute(
                f"SELECT count(*), min(date), max(date) FROM {t}"
            ).fetchone()
        except Exception:
            n, lo, hi = 0, None, None
        rows.append({"table": t, "present": True, "rows": int(n or 0),
                     "first": str(lo) if lo else None,
                     "last": str(hi) if hi else None})
    return rows


def input_coverage(con, days) -> dict:
    """How many archived days have ANY prediction rows in the warehouse.

    This is the first thing to check and the cheapest. If the prediction
    sources do not cover the days the archive covers, the validation gate has
    no inputs and nothing downstream can be measured.
    """
    covered = {}
    for view in ("forebet", "zulubet", "statarea"):
        settled = f"{view}_settled"
        if not _table_exists(con, settled):
            covered[view] = set()
            continue
        got = con.execute(
            f"SELECT DISTINCT date FROM {settled} "
            "WHERE date >= ? AND date <= ?",
            [min(days), max(days)],
        ).fetchall()
        covered[view] = {str(r[0])[:10] for r in got}
    any_cov = set().union(*covered.values()) if covered else set()
    return {
        "days": list(days),
        "per_source": {k: len(v & set(days)) for k, v in covered.items()},
        "days_with_any_input": len(any_cov & set(days)),
        "coverage_frac": (len(any_cov & set(days)) / len(days)) if days else 0.0,
    }


# --------------------------------------------------------------------------
# Dependency census over the live archive
# --------------------------------------------------------------------------
@dataclass
class Census:
    legs: int = 0
    by_rule: dict = field(default_factory=dict)
    by_odds_source: dict = field(default_factory=dict)
    source_hits: dict = field(default_factory=dict)
    source_vote: int = 0
    on_disk_sources: int = 0
    historical_odds: int = 0
    ceiling: int = 0


def dependency_census(legs) -> Census:
    """What the live legs actually depended on.

    ``legs`` are rows from ``auto_tickets.playable_legs`` (each carrying the
    original archived pick under ``row``). The census answers: of the legs the
    engine could really bet, how many are even *addressable* by on-disk data?
    """
    c = Census()
    for leg in legs:
        p = leg["row"] if "row" in leg else leg
        c.legs += 1
        rule = str(p.get("rule") or "unknown")
        c.by_rule[rule] = c.by_rule.get(rule, 0) + 1
        osrc = p.get("odds_source") or "none"
        c.by_odds_source[osrc] = c.by_odds_source.get(osrc, 0) + 1
        used = set(p.get("sources_used") or [])
        for s in used:
            c.source_hits[s] = c.source_hits.get(s, 0) + 1
        is_vote = not rule.startswith("ml-meta")
        on_disk = bool(used) and used <= ON_DISK_PREDICTION_SOURCES
        hist_odds = osrc in ON_DISK_ODDS_SOURCES
        c.source_vote += int(is_vote)
        c.on_disk_sources += int(on_disk)
        c.historical_odds += int(hist_odds)
        c.ceiling += int(is_vote and on_disk and hist_odds)
    return c


# --------------------------------------------------------------------------
# The reconstruction itself
# --------------------------------------------------------------------------
def reconstruct_legs(con, day: str, floor: float, *,
                     two_way_threshold: float = 70.0,
                     three_way_threshold: float = 65.0) -> list[dict]:
    """Rebuild the SOURCE-VOTE legs for one day from warehouse views alone.

    ml-meta rules are deliberately NOT reconstructed. Their feature vector
    contains actual half-time scores (see :data:`ML_META_FEATURE_AVAILABILITY`),
    so replaying them against settled warehouse rows would feed the model the
    result of the first half of the match it is being asked to predict. Legs
    are excluded rather than guessed — see the module docstring.

    Odds are ``forebet_best`` (the pick's forebet 1X2 price), which is the
    price family the engine bets at. BetExplorer closing odds are never mixed
    in here.
    """
    out: list[dict] = []
    if _table_exists(con, "consensus2"):
        rows = con.execute(
            "SELECT home, away, fb_pick, avg_p, pick_odds FROM consensus2 "
            "WHERE date = ? AND fb_pick = zb_pick AND avg_p >= ? "
            "AND pick_odds IS NOT NULL AND pick_odds >= ?",
            [day, two_way_threshold, floor],
        ).fetchall()
        for home, away, pick, avg_p, odds in rows:
            out.append({"match": f"{home} vs {away}", "home": home, "away": away,
                        "pick": str(pick).upper(), "prob": float(avg_p) / 100.0,
                        "odds": float(odds),
                        "rule": f"2way-unanimous avg_p>={two_way_threshold:g}"})
    if _table_exists(con, "consensus3"):
        rows = con.execute(
            "SELECT home, away, fb_pick, avg_p, pick_odds FROM consensus3 "
            "WHERE date = ? AND fb_pick = zb_pick AND zb_pick = sa_pick "
            "AND avg_p >= ? AND pick_odds IS NOT NULL AND pick_odds >= ?",
            [day, three_way_threshold, floor],
        ).fetchall()
        for home, away, pick, avg_p, odds in rows:
            out.append({"match": f"{home} vs {away}", "home": home, "away": away,
                        "pick": str(pick).upper(), "prob": float(avg_p) / 100.0,
                        "odds": float(odds),
                        "rule": f"3way-unanimous avg_p>={three_way_threshold:g}"})
    # one leg per fixture, strongest stated probability wins (live collapses
    # duplicate rules the same way)
    best: dict[tuple, dict] = {}
    for leg in out:
        key = (leg["match"], leg["pick"])
        if key not in best or leg["prob"] > best[key]["prob"]:
            best[key] = leg
    return sorted(best.values(), key=lambda l: (-l["prob"], -l["odds"]))


def _key(norm_team, match: str, pick: str) -> tuple:
    home, _, away = str(match).partition(" vs ")
    return (norm_team(home), norm_team(away), str(pick).upper())


def validation_gate(con, universe_legs_by_day, floor, norm_team) -> dict:
    """Reconstruct each archived day and score it against the live archive.

    ``universe_legs_by_day`` maps day -> live playable legs. Returns per-day
    precision/recall on exact legs (fixture, side) plus the distribution of
    odds differences on the legs that DID match.
    """
    per_day = []
    odds_diffs: list[float] = []
    tp = fp = fn = 0
    for day in sorted(universe_legs_by_day):
        live = universe_legs_by_day[day]
        recon = reconstruct_legs(con, day, floor)
        live_map = {_key(norm_team, l["match"], l["pick"]): l for l in live}
        recon_map = {_key(norm_team, l["match"], l["pick"]): l for l in recon}
        hit = set(live_map) & set(recon_map)
        for k in hit:
            lo, ro = live_map[k]["odds"], recon_map[k]["odds"]
            if lo:
                odds_diffs.append((ro - lo) / lo)
        tp += len(hit)
        fp += len(set(recon_map) - set(live_map))
        fn += len(set(live_map) - set(recon_map))
        per_day.append({
            "day": day,
            "live_legs": len(live),
            "recon_legs": len(recon),
            "matched": len(hit),
            "recall": (len(hit) / len(live)) if live else None,
            "precision": (len(hit) / len(recon)) if recon else None,
        })
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    mismatch = ([d for d in odds_diffs if abs(d) > 0.01])
    return {
        "per_day": per_day,
        "tp": tp, "fp": fp, "fn": fn,
        "recall": recall, "precision": precision,
        "odds_diffs": odds_diffs,
        "odds_mismatch_frac": (len(mismatch) / len(odds_diffs)) if odds_diffs else None,
        "odds_diff_median": statistics.median(odds_diffs) if odds_diffs else None,
        "live_legs_per_day": (
            statistics.mean([d["live_legs"] for d in per_day]) if per_day else 0.0),
        "recon_legs_per_day": (
            statistics.mean([d["recon_legs"] for d in per_day]) if per_day else 0.0),
    }


def gate_verdict(coverage: dict, gate: dict) -> tuple[bool, list[str]]:
    """PASS/FAIL against the pre-stated bar, with the reasons."""
    reasons = []
    ok = True
    if coverage["coverage_frac"] < GATE_MIN_COVERED_DAYS:
        ok = False
        reasons.append(
            f"input coverage {coverage['coverage_frac']:.0%} of archived days "
            f"< {GATE_MIN_COVERED_DAYS:.0%} required — the prediction sources "
            "do not span the days the engine actually bet")
    if gate["recall"] < GATE_MIN_LEG_RECALL:
        ok = False
        reasons.append(
            f"leg recall {gate['recall']:.1%} < {GATE_MIN_LEG_RECALL:.0%} required")
    if gate["precision"] < GATE_MIN_LEG_PRECISION:
        ok = False
        reasons.append(
            f"leg precision {gate['precision']:.1%} < "
            f"{GATE_MIN_LEG_PRECISION:.0%} required")
    if (gate["odds_mismatch_frac"] is not None
            and gate["odds_mismatch_frac"] > GATE_MAX_ODDS_MISMATCH):
        ok = False
        reasons.append(
            f"odds mismatch {gate['odds_mismatch_frac']:.1%} of matched legs "
            f"> {GATE_MAX_ODDS_MISMATCH:.0%} allowed")
    if ok:
        reasons.append("all bar criteria met")
    return ok, reasons
