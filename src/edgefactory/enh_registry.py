"""Enhancement certification registry — SHADOW -> PAPER -> ELIGIBLE -> BENCHED.

Each enhancement market type (versioned "<type>@v1") lives in exactly one state:

    SHADOW    known but unpriced/untested — never presented as a recommendation
    PAPER     real-priced outcomes accumulating from settled picks (paper trades)
    ELIGIBLE  Wilson LB95 hit-rate >= mean breakeven of the prices actually paid
              (i.e. clears real prices with statistical margin) on n >= MIN_PRICED_N;
              only ELIGIBLE types may be presented as recommendations
    BENCHED   was ELIGIBLE, then rolling BENCH_WINDOW_DAYS evidence turned
              unprofitable (circuit breaker — mirrors the decay monitor). There is
              NO automatic re-entry (RT-5): a benched market returns to PAPER only
              by an explicit operator reset after a fresh re-validation review.

Unpriced outcomes NEVER advance certification: probability without price is not
evidence of value (the 2026-08-03 audit lesson).

State persists in localdata/enhancement_registry.json (git-tracked so it rides the
persist-to-git loop). Writes hold a POSIX advisory flock across the full
read-modify-write and land via tmp + os.replace (the quota-ledger race lesson).
The flock is placed on a STABLE sidecar file (enhancement_registry.lock), never on
the json itself: flock is per-inode, and os.replace swaps the json's inode on every
write — locking the data file silently loses mutual exclusion the instant a write
lands (measured: only 8-15/40 concurrent records survived before this fix).
All public functions are fail-soft: audit/picks paths must never crash on registry.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
import time
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REGISTRY_FILENAME = "enhancement_registry.json"
REGISTRY_VERSION = "v1"
MIN_PRICED_N = 30
# Governance N5 (Addendum 27.11, 2026-08-05): PAPER->ELIGIBLE additionally
# requires this fraction of the priced outcomes to have been priced by
# >=2 DISTINCT sources (multi-source verification). Single-source prices
# still accrue toward n and the Wilson math (per Addendum 27.7) but cannot
# certify a market to the staking level. ceil(n * frac) at n=30 -> 8.
MIN_MULTI_SOURCE_FRAC = 0.25
WILSON_Z = 1.959963984540054
BENCH_WINDOW_DAYS = 60
BENCH_MIN_N = 20
MAX_RECORDS_PER_MARKET = None  # retain all measured evidence; no count cap
MAX_PROCESSED_KEYS = 1600


# ---------------------------------------------------------------------------
# Minimum acceptable price per enhancement market — "the floor".
#
# Operator ruling 2026-10-12, verbatim: "betting on ev will lead us to not bet
# at all, we have the track record of enhanced, we know what wins more, we just
# need prices above a certain threshold, like how autobets does it."
#
# There is deliberately NO EV veto anywhere on this path. The row's
# ``enhancement_breakeven`` and ``enhancement_edge_sample`` stay attached as
# INFORMATION ONLY and gate nothing.
#
# Each floor is the market's break-even price (1 / settled hit-rate) plus a
# margin, read off the settled registry on 2026-10-12:
#
#   market            n   hits   rate   breakeven   floor   profit(u)
#   match_over_25   350    231  66.0%     1.515      1.60    +2.297
#   match_over_15    33     24  72.7%     1.375      1.45    -5.780
#   match_over_35    16      5  31.2%     3.200      3.30    -2.200
#   btts_yes          7      4  57.1%     1.750      1.85    +1.990
#
# These are plain numeric literals (repo convention: daily.yml keeps its caps as
# literal '90' / '20') and they are a STARTING POINT to be re-derived from the
# settled slices, not gospel — match_over_15 clears its break-even on hit rate
# alone while being NEGATIVE in profit, which is exactly why the floor is
# per-market rather than one constant.
#
# A market with no floor listed here does not fire: with no settled evidence
# there is no threshold to clear, and inventing one would be the unvalidated
# betting the registry exists to prevent. Adding a market is a one-line diff
# once its slice justifies a number.
ENHANCEMENT_PRICE_FLOORS: dict[str, float] = {
    "match_over_25": 1.60,
    "match_over_15": 1.45,
    "match_over_35": 3.30,
    "btts_yes": 1.85,
    # Match unders (added 2026-10-13). The registry holds ZERO under records, so
    # these cannot come from settled evidence. They are the base-rate floor:
    # 1 / Wilson-LB95 of the realised hit rate in the 2026-01..09 BetExplorer
    # results (107,356 matches) + ENHANCEMENT_FLOOR_MARGIN (0.10). Base rates:
    # under 1.5 = 23.2% (LB 23.0%), under 2.5 = 44.2% (LB 43.9%), under 3.5 =
    # 65.3% (LB 65.0%). A price below the floor means the under does not pay
    # for its base-rate hit chance. The model's stated under probabilities
    # (85%+) sit far above these rates, so the floor is the control, not the
    # stated probability.
    "match_under_15": 4.45,
    "match_under_25": 2.38,
    "match_under_35": 1.64,
}

# Price CEILINGS (added 2026-10-13 for a small-stake live test): a leg priced above
# its market's ceiling does not fire. Tighten-only, like the derived floors.
# Evidence: match_over_25 priced at 1.85 or more, 52 settled legs, flat ROI
# -14.9%, losing in both halves of the record (-14.2% / -15.6%). The 1.85 cut
# was chosen after looking at that record, so it is a forward test, not a
# validated edge: judge it on legs settled after 2026-10-13.
ENHANCEMENT_PRICE_CEILINGS: dict[str, float] = {
    "match_over_25": 1.85,
}


def ceiling_for(market: str | None) -> float | None:
    """The maximum acceptable price for `market`, or None when it has none."""
    if not market:
        return None
    return ENHANCEMENT_PRICE_CEILINGS.get(str(market).strip())

# The absolute margin over break-even that ``derive_floors`` adds to a slice's
# derived price (1 / wilson_lb + margin). It is the SAME margin the operator's
# table above already implies — 1.60 over a 1.515 break-even is +0.085, 1.45
# over 1.375 is +0.075, 3.30 over 3.20 is +0.10, 1.85 over 1.75 is +0.10 — so
# 0.10 is the table's own upper margin, never a new invention. The derivation
# prints the margin it used, and the harness A/B (see
# ``scripts/replay_harness.py``) is what may change it; nothing loosens because
# this number moves, because the derivation is tighten-only either way.
ENHANCEMENT_FLOOR_MARGIN = 0.10


def derive_floors_for_day(root: Path | None = None, as_of: str | None = None, *,
                          margin: float = ENHANCEMENT_FLOOR_MARGIN,
                          parent_floors: dict | None = None,
                          min_n: int = MIN_PRICED_N) -> dict:
    """Read the registry and derive the day's floor table (fail-soft).

    The thin convenience around ``derive_floors``: it resolves the registry and
    the operator's parent table, and on ANY failure answers an empty table
    (``{"rows": [], "floors": {}, ...}``) — a lane must never crash because a
    registry is unreadable, and an empty table means every leg falls back to the
    operator's floor, which is the pre-R2 behaviour.
    """
    as_of = str(as_of or date.today().isoformat())[:10]
    parents = ENHANCEMENT_PRICE_FLOORS if parent_floors is None else parent_floors
    try:
        root = root or Path(__file__).resolve().parents[2]
        reg = _read(registry_path(root))
        if not isinstance(reg, dict) or not reg:
            raise ValueError("empty registry")
        return derive_floors(reg, as_of, parent_floors=parents, margin=margin,
                             min_n=min_n)
    except Exception:
        return {"as_of": as_of, "margin": float(margin), "min_n": int(min_n),
                "rows": [], "floors": {},
                "counts": {"market": 0, "league": 0, "team": 0, "inherited": 0,
                           "market_basis": 0, "league_basis": 0, "team_basis": 0,
                           "team_slices": 0},
                "coverage": {"records": 0, "priced": 0, "with_league": 0,
                             "with_keys": 0, "league_pct": 0.0, "keys_pct": 0.0}}


# ---------------------------------------------------------------------------
# Market scoring: what counts as a HIT for a settled enhancement market
#
# One definition, shared: the audit certifies the registry from it, and the
# ticket engine grades a frozen enhancement leg from it. Kept next to the
# floors because the floor and the hit definition answer the same question
# from opposite sides (what price is enough / what actually landed).
# ---------------------------------------------------------------------------
def check_enhancement_hit(enh_type: str, selection: str, hs: int, gs: int) -> bool | None:
    if hs is None or gs is None:
        return None
    sel = selection.lower()
    if enh_type == "match_over_15":
        # FIX-2 (2026-08-03, Addendum 12): plain-market scoring. The promised %
        # rendered for this market and the price captured for it are both the
        # PLAIN total, so the hit must be selection-independent. The removed
        # Win+Over combo branches measured a different market than the one
        # priced, deflating every hit-rate (and any future registry
        # certification) built on them.
        return (hs + gs) >= 2
    elif enh_type == "match_over_25":
        # FIX-2: plain-market scoring (see match_over_15).
        return (hs + gs) >= 3
    elif enh_type == "match_under_15":
        return (hs + gs) <= 1
    elif enh_type == "match_under_25":
        return (hs + gs) <= 2
    elif enh_type == "match_under_35":
        return (hs + gs) <= 3
    elif enh_type == "btts_yes":
        # FIX-2: plain-market scoring (see match_over_15).
        return hs > 0 and gs > 0
    elif enh_type == "btts_no":
        return hs == 0 or gs == 0
    elif enh_type in ("team_over_05", "home_over_05"):
        return hs >= 1 if (enh_type == "home_over_05" or sel == "home") else gs >= 1
    elif enh_type in ("team_over_15", "home_over_15"):
        return hs >= 2 if (enh_type == "home_over_15" or sel == "home") else gs >= 2
    elif enh_type == "home_over_25":
        return hs >= 3
    elif enh_type == "home_over_35":
        return hs >= 4
    elif enh_type == "home_over_45":
        return hs >= 5
    elif enh_type == "home_under_05":
        return hs == 0
    elif enh_type == "home_under_15":
        return hs <= 1
    elif enh_type == "home_under_25":
        return hs <= 2
    elif enh_type == "home_under_35":
        return hs <= 3
    elif enh_type == "home_under_45":
        return hs <= 4
    elif enh_type == "away_over_05":
        return gs >= 1
    elif enh_type == "away_over_15":
        return gs >= 2
    elif enh_type == "away_over_25":
        return gs >= 3
    elif enh_type == "away_over_35":
        return gs >= 4
    elif enh_type == "away_over_45":
        return gs >= 5
    elif enh_type == "away_under_05":
        return gs == 0
    elif enh_type == "away_under_15":
        return gs <= 1
    elif enh_type == "away_under_25":
        return gs <= 2
    elif enh_type == "away_under_35":
        return gs <= 3
    elif enh_type == "away_under_45":
        return gs <= 4
    elif enh_type == "goal_range_0_1":
        return (hs + gs) in [0, 1]
    elif enh_type == "goal_range_2_3":
        return (hs + gs) in [2, 3]
    elif enh_type == "goal_range_4_5":
        return (hs + gs) in [4, 5]
    elif enh_type == "goal_range_4_6":
        return (hs + gs) in [4, 5, 6]
    elif enh_type == "goal_range_6_plus":
        return (hs + gs) >= 6
    elif enh_type == "goal_range_7_plus":
        return (hs + gs) >= 7
    elif enh_type == "exact_0":
        return (hs + gs) == 0
    elif enh_type == "exact_1":
        return (hs + gs) == 1
    elif enh_type == "exact_2":
        return (hs + gs) == 2
    elif enh_type == "exact_3":
        return (hs + gs) == 3
    elif enh_type == "exact_4":
        return (hs + gs) == 4
    elif enh_type == "exact_5":
        return (hs + gs) == 5
    elif enh_type == "match_over_05":
        return (hs + gs) >= 1
    elif enh_type == "match_over_35":
        return (hs + gs) >= 4
    elif enh_type == "match_over_45":
        return (hs + gs) >= 5
    elif enh_type == "match_over_55":
        return (hs + gs) >= 6
    elif enh_type == "match_under_05":
        return (hs + gs) == 0
    elif enh_type == "match_under_45":
        return (hs + gs) <= 4
    elif enh_type == "match_under_55":
        return (hs + gs) <= 5
    elif enh_type == "double_chance":
        if sel == "home": # 1X
            return hs >= gs
        elif sel == "away": # X2
            return gs >= hs
        elif sel == "draw": # 12
            return hs != gs
    return None


def floor_for(market: str | None) -> float | None:
    """The minimum acceptable price for `market`, or None when it has none.

    This is the operator's PARENT floor — the root of the floor hierarchy
    ``market -> league -> team`` (see ``derive_floors``). It is a plain number
    and never consults evidence; the per-slice derivation only ever tightens
    what this returns.
    """
    if not market:
        return None
    return ENHANCEMENT_PRICE_FLOORS.get(str(market).strip())


def clears_floor(market: str | None, price: object, *,
                 floor: object = None) -> bool:
    """True when `price` is at or above the market's floor.

    False for a market with no floor (no threshold exists), and False for
    anything that is not a real number > 1.0 — the same definition of "is a
    price" the render and the capture boundary use (RT-2), so a string or a
    bool can never stand in for a decimal price. A leg BELOW its floor is not a
    bet — not paper, not shadow.

    ``floor`` overrides the static lookup with a derived per-slice floor
    (``derive_floors`` -> ``floor_for_slice``), so the gate has ONE validity
    rule whether the number came from the operator's table or from the
    evidence. Passing ``floor=None`` (the default) is the operator's table —
    unchanged behaviour, byte for byte.
    """
    gate = floor_for(market) if floor is None else floor
    if gate is None:
        return False
    if isinstance(gate, bool) or not isinstance(gate, (int, float)):
        return False
    if not math.isfinite(float(gate)):
        return False
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return False
    value = float(price)
    return math.isfinite(value) and value > 1.0 and value >= float(gate)


# ---------------------------------------------------------------------------
# Dynamic floors (round 6, R2): the floor hierarchy market -> league -> team.
#
# The operator's ruling fixed the ROOT of the hierarchy (ENHANCEMENT_PRICE_FLOORS,
# one number per market). R2 adds the levels below it, derived from the settled
# registry itself with the statistic the registry already certifies with
# (``wilson_lb``), and the rules are deliberately blunt:
#
#   * a slice INHERITS its parent's floor unless its own evidence unlocks a
#     deviation;
#   * the evidence gate is n >= MIN_PRICED_N AND a usable Wilson lower bound —
#     the same statistic as the PAPER -> ELIGIBLE transition;
#   * the derived number is 1 / wilson_lb + margin, and it is applied through
#     max(parent, derived): TIGHTEN-ONLY, always. A slice can never lower its
#     parent's floor; loosening is an operator ruling, not a derivation;
#   * a team slice NEVER deviates (it is report-only: too thin to certify), and
#     a market with no operator floor never gains one — it stays floorless, so
#     it still cannot fire;
#   * no lookahead: day D's floors use only records dated strictly before D. The
#     derivation is pure — registry in, table out, no clock and no I/O — so the
#     day's floors are re-derivable from the registry commit plus the inputs
#     printed into the slip;
#   * records written before the slice fields existed are reported as
#     ``unattributed`` and inherit; nothing is guessed at.
# ---------------------------------------------------------------------------
FLOOR_BASIS_INHERITED = "inherited"
FLOOR_BASIS_MARKET = "market"
FLOOR_BASIS_LEAGUE = "league"
FLOOR_BASIS_TEAM = "team"          # report-only: the row's evidence is shown, never applied
UNATTRIBUTED_LEAGUE = "unattributed"


def _priced_records_before(records: object, as_of: str) -> list[dict]:
    """Priced records dated strictly before ``as_of`` (the no-lookahead rule).

    "Priced" is the same test ``slice_records`` and the certification path use:
    a finite real number > 1.0. A record without a usable date is excluded —
    an undated record cannot be shown to precede the day being derived.
    """
    out = []
    for rec in records or []:
        try:
            if not isinstance(rec, dict):
                continue
            day = str(rec.get("date") or "")[:10]
            if not day or day >= as_of:
                continue
            price = rec.get("price")
            if isinstance(price, bool) or not isinstance(price, (int, float)):
                continue
            if not math.isfinite(float(price)) or float(price) <= 1.0:
                continue
            out.append(rec)
        except Exception:
            continue
    out.sort(key=lambda r: (str(r.get("date") or ""), str(r.get("match") or "")))
    return out


def _slice_evidence(recs: list[dict]) -> dict:
    """n / hits / rate / Wilson LB for one priced record slice."""
    n = len(recs)
    hits = sum(1 for r in recs if r.get("hit"))
    rate = (hits / n) if n else 0.0
    lb = wilson_lb(hits, n) if n else 0.0
    return {"n": n, "hits": hits, "rate": rate, "wilson_lb": lb,
            "breakeven": (1.0 / rate) if rate else None}


def _candidate_floor(evidence: dict, margin: float, min_n: int) -> float | None:
    """1 / wilson_lb + margin — the one derived number — or None when gated.

    Gate: n >= min_n AND a strictly positive lower bound (a slice whose LB
    rounds to 0 has no usable lower bound, so it cannot raise anything).
    """
    if evidence["n"] < min_n or evidence["wilson_lb"] <= 0.0:
        return None
    return 1.0 / evidence["wilson_lb"] + float(margin)


def derive_floors(registry: dict, as_of: str, *, parent_floors: dict,
                  margin: float, min_n: int = MIN_PRICED_N) -> dict:
    """Derive the day's per-slice floor table from the settled registry.

    ``registry`` is the parsed ``enhancement_registry.json`` payload (any
    version; unknown versions simply yield no records), ``as_of`` is the day
    being derived for (only records dated strictly before it count),
    ``parent_floors`` is the operator's root table (``ENHANCEMENT_PRICE_FLOORS``)
    and ``margin`` the operator's absolute margin over break-even. ``min_n``
    defaults to ``MIN_PRICED_N`` — pass it, never a new literal.

    Returns::

        {"as_of", "margin", "min_n",
         "rows": [ {level, market, league, team, name, n, hits, rate,
                    wilson_lb, breakeven, candidate_floor, parent_floor,
                    floor, basis, gate, reason} ],
         "floors": {"<market>": {"floor", "basis"},
                    "<market>|<league>": {"floor", "basis"}},
         "counts": {"market": i, "league": l, "team": t, "inherited": h,
                    "team_slices": evaluated},
         "coverage": {"records": n, "priced": n, "with_league": n,
                      "with_keys": n, "league_pct": f, "keys_pct": f}}

    Pure and deterministic: same inputs -> same output, no clock, no I/O.
    ``basis`` on a row is where the APPLIED floor came from; a team row whose
    own evidence clears the gate is labelled ``basis="team"`` and still carries
    the parent's floor — its ``candidate_floor`` is the number its evidence
    would give, reported, never applied.
    """
    as_of = str(as_of)[:10]
    market_rows: list[dict] = []
    league_rows: list[dict] = []
    team_rows: list[dict] = []
    team_slices_seen = 0

    markets = registry.get("markets") if isinstance(registry, dict) else None
    markets = markets if isinstance(markets, dict) else {}
    priced_total = 0
    with_league = 0
    with_keys = 0

    def _team_keys(rec: dict) -> list[tuple[str, str]]:
        keys = []
        for side in ("home", "away"):
            key = str(rec.get(f"{side}_key") or "").strip()
            name = str(rec.get(side) or "").strip()
            if key:
                keys.append((key, name))
        return keys

    for mkey, entry in sorted(markets.items()):
        plain = mkey[: -len(f"@{REGISTRY_VERSION}")] if mkey.endswith(f"@{REGISTRY_VERSION}") else mkey
        complete = isinstance(entry, dict) and evidence_complete(entry)
        recs = _priced_records_before(entry.get("records") if complete else None, as_of)
        priced_total += len(recs)
        with_league += sum(1 for r in recs if str(r.get("league") or "").strip())
        with_keys += sum(1 for r in recs
                         if str(r.get("home_key") or "").strip() and str(r.get("away_key") or "").strip())
        parent = (parent_floors or {}).get(plain)
        evidence = _slice_evidence(recs)
        candidate = _candidate_floor(evidence, margin, min_n)
        applied = parent
        basis = FLOOR_BASIS_INHERITED
        gate = candidate is not None
        if parent is None:
            reason = "no operator floor for this market — stays floorless, cannot fire"
        elif gate and candidate > parent:
            applied, basis = candidate, FLOOR_BASIS_MARKET
            reason = (f"market evidence n={evidence['n']} wilsonLB={evidence['wilson_lb']:.4f} "
                      f"-> {candidate:.4f} > parent {parent:.2f}")
        elif gate:
            reason = (f"market evidence n={evidence['n']} wilsonLB={evidence['wilson_lb']:.4f} "
                      f"-> {candidate:.4f} <= parent {parent:.2f} (clamped)")
        else:
            reason = (f"market evidence thin or unbounded (n={evidence['n']} of {min_n}) "
                      "— inherits parent")
        market_rows.append({
            "level": "market", "market": plain, "league": None, "team": None,
            "name": plain, **evidence, "candidate_floor": candidate,
            "parent_floor": parent, "floor": applied, "basis": basis,
            "gate": gate, "reason": reason,
        })

        leagues: dict[str, list[dict]] = {}
        for rec in recs:
            leagues.setdefault(str(rec.get("league") or "").strip() or UNATTRIBUTED_LEAGUE, []).append(rec)
        for league, lrecs in sorted(leagues.items()):
            lev = _slice_evidence(lrecs)
            recorded = league != UNATTRIBUTED_LEAGUE
            lcand = _candidate_floor(lev, margin, min_n) if recorded else None
            # The parent of a league slice is the MARKET's APPLIED floor (which
            # may itself have been tightened), never the operator's root: a
            # slice tightens its parent, and its parent is what actually gates.
            lparent = applied
            lapplied, lbasis = lparent, FLOOR_BASIS_INHERITED
            lgate = lcand is not None
            if not recorded:
                # No league recorded for these records: they are not a league
                # slice, they are the absence of one. They inherit the market
                # floor and can never unlock a deviation.
                lcand = None
                lreason = ("no league recorded on these records — inherits the market "
                           "floor (a backfill is how a league slice appears)")
            elif lparent is None:
                lreason = "market floorless — no league floor to raise"
            elif lgate and lcand > lparent:
                lapplied, lbasis = lcand, FLOOR_BASIS_LEAGUE
                lreason = (f"league evidence n={lev['n']} wilsonLB={lev['wilson_lb']:.4f} "
                           f"-> {lcand:.4f} > market {lparent:.4f}")
            elif lgate:
                lreason = (f"league evidence n={lev['n']} wilsonLB={lev['wilson_lb']:.4f} "
                           f"-> {lcand:.4f} <= market {lparent:.4f} (clamped)")
            else:
                lreason = (f"league evidence thin or unbounded (n={lev['n']} of {min_n}) "
                           "— inherits market")
            league_rows.append({
                "level": "league", "market": plain, "league": league, "team": None,
                "name": league, **lev, "candidate_floor": lcand,
                "parent_floor": lparent, "floor": lapplied, "basis": lbasis,
                "gate": lgate, "reason": lreason,
            })

            teams: dict[str, dict] = {}
            for rec in lrecs:
                for key, name in _team_keys(rec):
                    slot = teams.setdefault(key, {"names": [], "recs": []})
                    slot["recs"].append(rec)
                    if name and name not in slot["names"]:
                        slot["names"].append(name)
            for key, slot in sorted(teams.items()):
                team_slices_seen += 1
                tev = _slice_evidence(slot["recs"])
                tcand = _candidate_floor(tev, margin, min_n)
                tgate = tcand is not None
                if tgate:
                    treason = (f"team evidence n={tev['n']} wilsonLB={tev['wilson_lb']:.4f} "
                               f"-> {tcand:.4f} REPORTED, not applied: a team slice never "
                               "deviates (too thin to certify)")
                else:
                    treason = (f"team evidence thin or unbounded (n={tev['n']} of {min_n}) "
                               "— report-only, inherits")
                if tev["n"] < min_n and not tgate:
                    continue          # a thin team slice is not worth a table row
                team_rows.append({
                    "level": "team", "market": plain, "league": league, "team": key,
                    "name": sorted(slot["names"])[0] if slot["names"] else key,
                    **tev, "candidate_floor": tcand, "parent_floor": lapplied,
                    "floor": lapplied,
                    "basis": FLOOR_BASIS_TEAM if tgate else FLOOR_BASIS_INHERITED,
                    "gate": tgate, "reason": treason,
                })

    floors: dict[str, dict] = {}
    for row in market_rows:
        floors[row["market"]] = {"floor": row["floor"], "basis": row["basis"]}
    for row in league_rows:
        floors[f"{row['market']}|{row['league']}"] = {"floor": row["floor"],
                                                      "basis": row["basis"]}
    counts = {
        "market": len(market_rows),
        "league": len(league_rows),
        "team": len(team_rows),
        "inherited": sum(1 for r in market_rows + league_rows + team_rows
                         if r["basis"] == FLOOR_BASIS_INHERITED),
        "market_basis": sum(1 for r in market_rows if r["basis"] == FLOOR_BASIS_MARKET),
        "league_basis": sum(1 for r in league_rows if r["basis"] == FLOOR_BASIS_LEAGUE),
        "team_basis": sum(1 for r in team_rows if r["basis"] == FLOOR_BASIS_TEAM),
        "team_slices": team_slices_seen,
    }
    coverage = {
        "records": priced_total, "priced": priced_total,
        "with_league": with_league, "with_keys": with_keys,
        "league_pct": (100.0 * with_league / priced_total) if priced_total else 0.0,
        "keys_pct": (100.0 * with_keys / priced_total) if priced_total else 0.0,
    }
    return {"as_of": as_of, "margin": float(margin), "min_n": int(min_n),
            "rows": market_rows + league_rows + team_rows,
            "floors": floors, "counts": counts, "coverage": coverage}


def floor_for_slice(derived: dict, market: str | None,
                    league: str | None = None, *,
                    parent_floors: dict | None = None) -> tuple[float | None, str]:
    """(floor, basis) applied to one leg: its league slice, else the market root.

    A leg with no league (or one the registry has never seen) inherits the
    market root. Team slices are report-only and are therefore never consulted
    here. Returns ``(None, "inherited")`` for a market with no floor.
    """
    market = str(market or "").strip()
    floors = (derived or {}).get("floors") if isinstance(derived, dict) else None
    floors = floors if isinstance(floors, dict) else {}
    league = str(league or "").strip()
    if league:
        slot = floors.get(f"{market}|{league}")
        if isinstance(slot, dict) and slot.get("floor") is not None:
            return float(slot["floor"]), str(slot.get("basis") or FLOOR_BASIS_INHERITED)
    slot = floors.get(market)
    if isinstance(slot, dict) and slot.get("floor") is not None:
        return float(slot["floor"]), str(slot.get("basis") or FLOOR_BASIS_INHERITED)
    # No derived row for this market (no settled records, e.g. the match unders):
    # the operator's root floor applies. Without this fallback a parent floor
    # with no registry row would silently never bind.
    parent = (floor_for(market) if parent_floors is None
              else parent_floors.get(market))
    if parent is not None:
        return float(parent), FLOOR_BASIS_INHERITED
    return None, FLOOR_BASIS_INHERITED


def registry_path(root: Path) -> Path:
    return Path(root) / "localdata" / REGISTRY_FILENAME


def versioned(market: str | None) -> str | None:
    return f"{market}@{REGISTRY_VERSION}" if market else None


@contextmanager
def _locked(root: Path):
    """Serialize registry read-modify-write across processes and threads.

    Locks a DEDICATED sidecar file that is appended to but never replaced, keeping
    the locked inode constant (mirrors the quota-ledger's USAGE_LOCK_FILE pattern).
    Advisory: only processes using this helper respect it; non-fatal where flock is
    unavailable."""
    lock_path = registry_path(root).with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "a")  # noqa: PTH123
    try:
        try:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        except Exception:
            pass
        yield
    finally:
        try:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        fh.close()


def _read(path: Path) -> dict:
    """Parse the registry; on corruption QUARANTINE the bad file (recoverable,
    auditable) and return a fresh structure — never silently lose history (RT-4)."""
    try:
        if path.exists():
            try:
                with open(path, "rb") as fh:
                    data = json.loads(fh.read().decode("utf-8"))
                if isinstance(data, dict) and isinstance(data.get("markets"), dict):
                    return data
            except Exception:
                try:
                    quarantine = path.with_name(
                        f"{path.stem}.corrupt-{int(time.time())}{path.suffix}")
                    os.replace(path, quarantine)
                except Exception:
                    pass
    except Exception:
        pass
    return {"version": 2, "markets": {}}


def _write_atomic(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(json.dumps(data, indent=1, sort_keys=True).encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def _blank() -> dict:
    return {"status": "SHADOW", "n": 0, "hits": 0, "profit": 0.0,
            "inv_price_sum": 0.0, "processed": [], "records": [],
            "multi_n": 0,  # governance N5: outcomes priced by >=2 distinct sources
            "status_since": None, "status_reason": None}


def wilson_lb(hits: int, n: int, z: float = WILSON_Z) -> float:
    if n <= 0:
        return 0.0
    p = hits / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = p + z2 / (2.0 * n)
    margin = z * ((p * (1.0 - p) + z2 / (4.0 * n)) / n) ** 0.5
    return (centre - margin) / denom


def evidence_complete(entry: dict) -> bool:
    """Cumulative counters cannot certify a truncated or inconsistent ledger."""
    return not entry.get("records_truncated") and int(entry.get("n") or 0) == len(entry.get("records") or [])


def _evaluate(entry: dict, today: str) -> None:
    if entry.get("status") not in {"SHADOW", "PAPER", "ELIGIBLE", "BENCHED"}:
        entry["status"] = "SHADOW"
    n, hits = entry.get("n", 0), entry.get("hits", 0)
    if not evidence_complete(entry):
        entry.update(status="PAPER", records_truncated=True,
                     status_reason="incomplete retained evidence; certification and derived floors blocked")
        return

    if entry["status"] == "SHADOW" and n >= 1:
        entry.update(status="PAPER", status_since=today,
                     status_reason="first priced outcome recorded")

    if entry["status"] == "PAPER" and n >= MIN_PRICED_N:
        mean_be = (entry.get("inv_price_sum", 0.0) / n) if n else None
        lb = wilson_lb(hits, n)
        if mean_be and lb >= mean_be:
            multi_n = entry.get("multi_n", 0)
            multi_req = max(1, math.ceil(n * MIN_MULTI_SOURCE_FRAC))
            if multi_n >= multi_req:
                entry.update(status="ELIGIBLE", status_since=today,
                             status_reason=f"n={n} wilsonLB95={lb:.4f} >= mean breakeven {mean_be:.4f}, multi-source {multi_n}/{multi_req}")
            else:
                # Governance N5: Wilson evidence clears but verification does not.
                # Stay PAPER with a transparent reason (never silently stall).
                entry.update(status_reason=f"n={n} wilsonLB95={lb:.4f} >= mean breakeven {mean_be:.4f} but multi-source verification {multi_n}/{multi_req} not met")

    if entry["status"] == "ELIGIBLE":
        try:
            cutoff = (date.fromisoformat(today) - timedelta(days=BENCH_WINDOW_DAYS)).isoformat()
        except Exception:
            cutoff = today
        recs = [r for r in entry.get("records", [])
                if cutoff <= (r.get("date") or "") <= today and (r.get("price") or 0) > 1.0]
        if len(recs) >= BENCH_MIN_N:
            roi = sum((float(r["price"]) - 1.0) if r.get("hit") else -1.0 for r in recs) / len(recs)
            if roi < 0.0:
                entry.update(status="BENCHED", status_since=today,
                             status_reason=f"rolling {BENCH_WINDOW_DAYS}d roi={roi:+.4f} on n={len(recs)} (circuit breaker)")


def processed_window_is_safe(keys_in_window: int, *, cap: int = MAX_PROCESSED_KEYS) -> bool:
    """Trim-safety (round 6D): can ``processed`` dedupe a whole rescan window?

    ``processed`` is the registry's dedup list. Since 2026-10-21 it is retained
    in full (the cap is no longer applied by ``record_outcome``), so dedup is
    exact; this bound is kept as the guard the cap would need if trimming ever
    returns. It is safe only while a
    key can never be re-encountered by a later run after being trimmed: a
    trimmed key that is still inside a rescan window would be recorded again,
    and if it was priced the certification counters would double-count.

    The invariant is therefore: the keys ONE market can present inside any
    rescan window are fewer than the cap, so the trim can never reach inside the
    window. This function is that test, in one place, for the callers (and the
    suite) that must check it as the archives grow.

    Measured 2026-10-12 over the committed archives (118 pick files): the worst
    per-market 30-day window is 428 keys (``match_over_25``) and the
    whole-archive window is 702 — both below 1600. If a market ever crosses, the
    unpriced keys have to move to their own capped list rather than sharing
    ``processed``.
    """
    return int(keys_in_window) < int(cap)


def record_outcome(root: Path, *, date_: str, match: str, market: str | None,
                   price: float | None, hit: bool, source: str = "",
                   today: str | None = None, multi_source: bool = False,
                   bucket: str = "", rule: str = "", stated: float | None = None,
                   league: str = "", home: str = "", away: str = "",
                   home_key: str = "", away_key: str = "",
                   cohort_rate: float | None = None,
                   price_context: dict | None = None) -> dict:
    """Idempotently record one settled enhancement outcome.

    Dedupes on "date|match|<market>@v1" so repeated audit runs cannot double-count.
    Unpriced outcomes are recorded as processed but never advance certification.
    ``today`` injects the evaluation date (default: real system date) so the
    rolling BENCH window is deterministic in tests and batch replay.
    ``multi_source`` (governance N5): True when >=2 distinct sources priced this
    outcome; increments the market's multi_n used by the ELIGIBLE floor.

    Slice provenance (2026-10-12), recorded so the settled track record can
    answer "do enhancement bets pay better out of SKIPPED_VETO picks?":
    ``bucket`` is the parent pick's bucket, ``rule`` its rule id, ``stated`` the
    enhancement's own probability as stated at pick time. They are PROVENANCE,
    not gates — nothing here reads them. All three are optional, so every record
    written before this change renders as ``unattributed`` in a slice instead of
    being guessed at, and the dedup key is unchanged.

    Floor-slice provenance (round 6, R2): ``league`` is the parent pick's league
    as written, ``home``/``away`` the settled fixture's team names and
    ``home_key``/``away_key`` their identity keys — the inputs ``derive_floors``
    slices on. Additive and optional: a record written without them inherits its
    parent floor (``unattributed`` league), and the dedup key is unchanged. Keys
    are derived from the names through ``source_team_key`` unless the caller
    already has them.

    Returns {"status": str|None, "recorded": bool}. Never raises."""
    try:
        mkey = versioned(market)
        if not mkey or not match:
            return {"status": None, "recorded": False}
        path = registry_path(root)
        today = today or date.today().isoformat()
        pkey = f"{date_}|{match}|{mkey}"
        with _locked(root):
            reg = _read(path)
            entry = reg["markets"].setdefault(mkey, _blank())
            if (pkey in set(entry.get("processed", [])) or any(
                    r.get("date") == date_ and r.get("match") == match
                    for r in entry.get("records", []))):
                return {"status": entry.get("status"), "recorded": False}
            entry.setdefault("processed", []).append(pkey)
            # RT-2: NaN/infinite prices must never advance certification.
            if price and math.isfinite(float(price)) and float(price) > 1.0:
                price_f = float(price)
                entry["n"] = entry.get("n", 0) + 1
                entry["hits"] = entry.get("hits", 0) + (1 if hit else 0)
                entry["profit"] = round(entry.get("profit", 0.0) + ((price_f - 1.0) if hit else -1.0), 6)
                entry["inv_price_sum"] = entry.get("inv_price_sum", 0.0) + 1.0 / price_f
                if not (home_key and away_key) and (home or away):
                    try:
                        from edgefactory.identity import source_team_key
                        home_key = home_key or source_team_key(home)
                        away_key = away_key or source_team_key(away)
                    except Exception:
                        pass
                entry.setdefault("records", []).append(
                    {"date": date_, "match": match, "price": price_f,
                     "hit": bool(hit), "source": source or "",
                     "multi_source": bool(multi_source),
                     # Original predecision quote/context, never reconstructed.
                     "price_context": dict(price_context or {}),
                     "recorded_at": datetime.now(timezone.utc).isoformat(),
                     # Slice provenance (2026-10-12). "" / None means
                     # unattributed, never a guess.
                     "bucket": str(bucket or ""),
                     "rule": str(rule or ""),
                     "stated": (float(stated) if isinstance(stated, (int, float))
                                and not isinstance(stated, bool)
                                and math.isfinite(float(stated)) else None),
                     # Floor-slice provenance (round 6, R2). Additive; empty
                     # means "inherit", never a guess.
                     "league": str(league or ""),
                     "home": str(home or ""),
                     "away": str(away or ""),
                     "home_key": str(home_key or ""),
                     "away_key": str(away_key or ""),
                     # Realized cohort rate (forward-only). Never the stated probability.
                     "cohort_rate": (round(float(cohort_rate), 4)
                                    if isinstance(cohort_rate, (int, float))
                                    and not isinstance(cohort_rate, bool)
                                    and math.isfinite(float(cohort_rate))
                                    and 0.0 < float(cohort_rate) < 1.0 else None)})
                # Retain every priced observation, including idempotency keys.
                # Increasing retention cannot repair records already lost.

                if multi_source:
                    entry["multi_n"] = entry.get("multi_n", 0) + 1
            reg["generated_at"] = today
            reg["evidence_schema_version"] = 1
            _evaluate(entry, today)
            _write_atomic(path, reg)
            return {"status": entry.get("status"), "recorded": True}
    except Exception:
        return {"status": None, "recorded": False}


UNATTRIBUTED = "unattributed"


def market_track_record(root: Path | None = None,
                        market: str | None = None) -> list[dict]:
    """Settled per-market rows for the settlement tables.

    ``[{market, status, n, hits, rate, breakeven, profit}]`` where ``breakeven``
    is 1/rate — the price at which the settled hit rate exactly pays for itself
    (the number the floors in ``ENHANCEMENT_PRICE_FLOORS`` are derived from).
    ``market`` selects one unversioned market; None returns every market, most
    settled first. Fail-soft: [] on any error.
    """
    try:
        root = root or Path(__file__).resolve().parents[2]
        reg = _read(registry_path(root))
        suffix = f"@{REGISTRY_VERSION}"
        rows = []
        for key, entry in (reg.get("markets") or {}).items():
            plain = key[: -len(suffix)] if key.endswith(suffix) else key
            if market is not None and plain != market:
                continue
            n = int(entry.get("n") or 0)
            hits = int(entry.get("hits") or 0)
            rate = (hits / n) if n else 0.0
            rows.append({
                "market": plain,
                "status": entry.get("status") or "SHADOW",
                "n": n,
                "hits": hits,
                "rate": rate,
                "breakeven": (1.0 / rate) if rate else None,
                "profit": float(entry.get("profit") or 0.0),
                "floor": floor_for(plain),
                "retained_n": len(entry.get("records") or []),
                "records_truncated": not evidence_complete(entry),
                "evidence_complete": evidence_complete(entry),
            })
        rows.sort(key=lambda r: (-r["n"], r["market"]))
        return rows
    except Exception:
        return []


def slice_records(records: list[dict], key: str) -> dict[str, dict]:
    """Group settled records by a provenance key ("bucket" or "rule").

    Returns ``{value: {n, hits, rate, profit}}`` sorted most-settled first.
    Records written before slice provenance existed have no such field and are
    reported as ``UNATTRIBUTED`` — never guessed at.
    """
    out: dict[str, dict] = {}
    for rec in records or []:
        try:
            value = str(rec.get(key) or "").strip() or UNATTRIBUTED
            slot = out.setdefault(value, {"n": 0, "hits": 0, "profit": 0.0})
            price = rec.get("price")
            if not isinstance(price, (int, float)) or isinstance(price, bool):
                continue
            if not math.isfinite(float(price)) or float(price) <= 1.0:
                continue
            slot["n"] += 1
            slot["hits"] += 1 if rec.get("hit") else 0
            slot["profit"] = round(
                slot["profit"] + ((float(price) - 1.0) if rec.get("hit") else -1.0), 6)
        except Exception:
            continue
    for slot in out.values():
        slot["rate"] = (slot["hits"] / slot["n"]) if slot["n"] else 0.0
    return dict(sorted(out.items(), key=lambda kv: (-kv[1]["n"], kv[0])))


def slice_for_market(root: Path | None = None, market: str | None = None,
                     key: str = "bucket") -> dict[str, dict]:
    """``slice_records`` over one market's settled history, newest markets first.

    Fail-soft: {} on any error.
    """
    try:
        root = root or Path(__file__).resolve().parents[2]
        entry = _read(registry_path(root))["markets"].get(versioned(market)) or {}
        return slice_records(entry.get("records") or [], key)
    except Exception:
        return {}


def status_for(market: str | None, root: Path | None = None) -> str:
    """Read-only status lookup for presentation. Fail-soft 'SHADOW'."""
    if not market:
        return "SHADOW"
    try:
        root = root or Path(__file__).resolve().parents[2]
        entry = _read(registry_path(root))["markets"].get(versioned(market))
        if entry and not evidence_complete(entry):
            return "PAPER"
        return (entry or {}).get("status") or "SHADOW"
    except Exception:
        return "SHADOW"


def all_statuses(root: Path | None = None) -> dict[str, str]:
    """{unversioned_market: status} for reporting. Fail-soft {}."""
    try:
        root = root or Path(__file__).resolve().parents[2]
        reg = _read(registry_path(root))
        suffix = f"@{REGISTRY_VERSION}"
        return {k[: -len(suffix)] if k.endswith(suffix) else k: ((v or {}).get("status", "SHADOW") if evidence_complete(v or {}) else "PAPER")
                for k, v in reg.get("markets", {}).items()}
    except Exception:
        return {}


MIN_COHORT_N = 30


def enhancement_cohort_evidence(pick: dict, *, priced: bool = False,
                                root: Path | None = None) -> dict | None:
    """Validate the selected market's REALIZED evidence at board/slip seams.

    A model estimate, global calibration, winner-only prose, another market's
    evidence, or an inherited Forebet cohort is not a realized contract rate.
    With priced=True, attach the current executable quote and the existing
    Wilson lower endpoint of the exact-parent cohort. This is a historical
    cohort payout screen, not a quote-conditioned rate or fixture forecast.
    ``root`` remains accepted for existing live/replay/audit callers; admission
    no longer depends on accumulated priced registry records.
    """
    from edgefactory.consensus_contracts import SCHEMA
    try:
        market = pick['recommended_enhancement']
        identity = pick['contract_id']
        if (pick.get('contract_schema') != SCHEMA or not isinstance(identity, str)
                or not identity.startswith('pfc_') or len(identity) != 28):
            return None
        notes = [r for r in pick.get('event_notes', [])
                 if isinstance(r, dict) and r.get('market') == market]
        if len(notes) != 1:
            return None
        note = notes[0]
        rate, n = note.get('cohort_rate'), note.get('cohort_n')
        if (note.get('engine') != 'hybrid_cohort' or type(n) is not int or n < MIN_COHORT_N
                or type(rate) not in (int, float) or not math.isfinite(rate) or not 0 <= rate <= 1
                or note.get('cohort_contract_id') != identity
                or note.get('cohort_as_of_exclusive') != pick.get('date')
                or pick.get('enhancement_cohort_contract_id') != identity
                or pick.get('enhancement_cohort_n') != n
                or pick.get('enhancement_cohort_as_of_exclusive') != pick.get('date')):
            return None
        date.fromisoformat(pick['date'])
        for value in (pick.get('enhancement_cohort_rate'),):
            if (type(value) not in (int, float) or not math.isfinite(value)
                    or abs(value - rate) > 0.000051):
                return None
        # Legacy archived fields must still agree with the descriptive rate;
        # new rows leave the unsupported fixture forecast explicitly null.
        value = pick.get('enhancement_probability')
        if value is not None and (type(value) not in (int, float)
                or not math.isfinite(value) or abs(value - rate) > 0.000051):
            return None
        evidence = {'rate': rate, 'n': n, 'contract_id': identity,
                    'as_of_exclusive': pick['date'], 'market': market,
                    'basis': 'descriptive_exact_parent'}
        if not priced:
            return evidence
        # Price the existing exact-parent all-outcome cohort, not a new cell
        # per bookmaker/league/exact quote. Historical quote records remain
        # useful for realized ROI auditing, but are not a bootstrap gate.
        context = enhancement_price_context(pick)
        if context is None or not 0.60 <= rate <= 0.90:
            return None
        # Persisted cohort rates are rounded to four decimals. Use the lowest
        # integer hit count compatible with that rounding, NEVER round up the
        # evidence or pretend this is an observed quote-conditioned frequency.
        min_hits = max(0, math.ceil((rate - 0.00005) * n - 1e-9))
        max_hits = min(n, math.floor((rate + 0.00005) * n + 1e-9))
        if min_hits > max_hits:
            return None
        evidence.update(cohort_min_hits=min_hits,
                        cohort_lower_bound=wilson_lb(min_hits, n),
                        price_context=context, basis='cohort_payout_bound')
        return evidence
    except (KeyError, TypeError, ValueError, OSError, AttributeError):
        return None


def enhancement_ml_probability(pick: dict, market: str) -> float | None:
    """Optional ML ordering only; NEVER substitutes for measured admission.

    Recompute from the retained compact model and this parent's own confidence.
    All market probabilities sum one common score distribution, not independent
    binary classifiers or multiplied marginal probabilities for an accumulator.
    """
    if os.environ.get('EDGE_FACTORY_ENH_ML', '1') != '1':
        return None
    try:
        import hashlib
        profile = pick.get('statistical_profile') or {}
        model = profile.get('ml_model') or {}
        unsigned = {k: v for k, v in model.items() if k != 'model_key'}
        if (model.get('schema') not in ('enh_score_logit_v1', 'enh_score_logit_v2')
                or model.get('model_key') != hashlib.sha256(json.dumps(
                    unsigned, sort_keys=True, allow_nan=False).encode()).hexdigest()
                or model['contract_id'] != pick['contract_id']
                or profile['contract_id'] != pick['contract_id']
                or model['selection'] != pick['pick']
                or profile['selection'] != pick['pick']
                or model['as_of_exclusive'] != pick['date']
                or profile['as_of_exclusive'] != pick['date']
                or not model['train_last_date'] < pick['date']
                or type(model['n']) is not int or not MIN_COHORT_N <= model['n'] <= profile['n']):
            return None
        probability = pick.get('avg_p')
        if (type(probability) not in (int, float) or not math.isfinite(probability)
                or not 0 <= probability <= 100):
            return None
        x = probability / 100
        if not model['feature_min'] <= x <= model['feature_max']:
            return None  # no extrapolated or fabricated missing features
        vector = [x]
        if model['schema'] == 'enh_score_logit_v2':
            from edgefactory.consensus_contracts import enhancement_feature_vector
            receipt = profile.get('ml_inputs')
            features = {}
            if receipt is not None:
                from edgefactory.identity import source_team_key
                if (receipt['contract_id'] != pick['contract_id'] or receipt['fixture'] !=
                        [pick['date'], source_team_key(pick['home']), source_team_key(pick['away'])]):
                    return None
                features.update(receipt['values'])
            features['confidence'] = x  # never inherit another fixture's confidence
            vector = enhancement_feature_vector(features, model)
        classes, coef, intercept = model['classes'], model['coef'], model['intercept']
        if len(classes) < 2 or len(coef) != len(intercept):
            return None
        if (any(len(c) != len(vector) or any(type(v) not in (int, float) or not math.isfinite(v) for v in c)
                for c in coef) or any(type(b) not in (int, float) or not math.isfinite(b) for b in intercept)):
            return None
        logits = [b + sum(w * v for w, v in zip(c, vector)) for b, c in zip(intercept, coef)]
        if len(classes) == 2 and len(logits) == 1:
            logits = [0., logits[0]]  # sklearn's binary logistic encoding
        if len(logits) != len(classes) or not all(math.isfinite(v) for v in logits):
            return None
        weights = [math.exp(v - max(logits)) for v in logits]
        hits, pairs = [], []
        for label in classes:
            values = label.split(':')
            if len(values) != 2 or not all(v.isdigit() for v in values):
                return None
            pair = tuple(map(int, values))
            pairs.append(pair)
            hit = check_enhancement_hit(market, pick['pick'], *pair)
            if hit is None:
                return None
            hits.append(hit)
        if len(set(pairs)) != len(pairs):
            return None
        return sum(w for w, hit in zip(weights, hits) if hit) / sum(weights)
    except (KeyError, TypeError, ValueError, AttributeError, ArithmeticError):
        return None


def enhancement_price_context(pick: dict) -> dict | None:
    """Only original, executable predecision quotes may condition evidence.

    Missing data stays missing. Exchange commission/acca support is not in the
    current capture contract, so an exchange quote cannot certify a net payout.
    This validates the CURRENT quote only; it does not define a historical
    sampling cell or certify a calibrated fixture forecast.
    """
    from edgefactory import price_sources as psrc
    try:
        price = pick['enhancement_price']
        book = pick['enhancement_price_book'].strip()
        source = pick['enhancement_price_source']
        captured, decision, kickoff = (datetime.fromisoformat(pick[k]) for k in
                                      ('enhancement_price_at', 'as_of', 'enhancement_price_kickoff'))
        if (type(price) not in (int, float) or not math.isfinite(price) or price <= 1
                or not book or not psrc.spec(source).named_bookmaker
                or any(exchange in book.casefold() for exchange in ('matchbook', 'betfair', 'smarkets', 'betdaq'))
                or not pick.get('league') or not pick.get('pick')
                or any(t.tzinfo is None for t in (captured, decision, kickoff))
                or not captured <= decision < kickoff
                or decision.date().isoformat() != pick['date']):
            return None
        return dict(contract_id=pick['contract_id'], selection=pick['pick'],
                    league=pick['league'], book=book, source=source, price=price,
                    captured_at=captured.isoformat(), decision_at=decision.isoformat(),
                    kickoff=kickoff.isoformat())
    except (KeyError, TypeError, ValueError, AttributeError):
        return None
