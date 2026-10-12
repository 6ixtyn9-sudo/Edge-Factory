#!/usr/bin/env python3
"""Round-5 measurement driver: W3 coverage, W5 signal gate (offline, no network).

Runs on the committed archives only:

    localdata/betexplorer_results_*.csv.gz   monthly results archive
    localdata/settled_results.json           settlement path's 90-day window
    localdata/enhancement_registry.json      the lane's 409 settled records
    localdata/picks_<date>.json              the model's stated probabilities

Writes raw output next to this file:

    w3_coverage.txt      coverage of the settled population, per month + league
    w5_signal.txt        Brier / log loss tables for model, blend, market

Usage:  PYTHONPATH=src .venv/bin/python handoff/round5_form_h2h_2026-10-12/intel_report.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, "src")

from edgefactory import form_intel as fi            # noqa: E402
from edgefactory.util import norm_team              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALDATA = "localdata"

# Market -> label, exactly as scripts/picks_today.py writes the label for the
# market (raw_candidates). Used to join the registry record to the pick that
# carried the model's stated probability for the same selection.
LABEL_BY_MARKET = {
    "match_over_15": "Match Over 1.5 Goals",
    "match_over_25": "Match Over 2.5 Goals",
    "match_over_35": "Match Over 3.5 Goals",
    "match_over_45": "Match Over 4.5 Goals",
    "btts_yes": "Both Teams to Score - Yes (BTTS-Yes)",
    "away_under_25": "Away Team Under 2.5 Goals",
    "away_under_35": "Away Team Under 3.5 Goals",
}
SHORT_NAME = {
    "match_over_15": "over_15", "match_over_25": "over_25",
    "match_over_35": "over_35", "match_over_45": "over_45",
    "btts_yes": "btts_yes", "away_under_25": "away_under_25",
    "away_under_35": "away_under_35",
}
MARKET_ORDER = ("match_over_25", "match_over_15", "match_over_35", "btts_yes",
                "away_under_25", "away_under_35", "match_over_45")


def load_records(localdata: str) -> list[dict]:
    reg = json.load(open(os.path.join(localdata, "enhancement_registry.json")))
    out = []
    for key, block in reg["markets"].items():
        market = key.split("@")[0]
        for rec in block.get("records") or []:
            home, away = [s.strip() for s in str(rec.get("match") or "").split(" vs ")]
            out.append({"market": market, "date": rec["date"], "home": home,
                        "away": away, "price": rec.get("price"),
                        "hit": bool(rec.get("hit")), "source": rec.get("source")})
    return out


def load_picks(localdata: str, dates: set[str]) -> dict:
    """(date, home_key, away_key, market) -> {p, label, league, path}.

    The pick's own market key is ``recommended_enhancement`` (the display
    ``enhancement_label`` is sometimes a combo phrase, e.g. "Home Win + Over
    2.5", which cannot be matched label-for-label). The evening file is read
    first and wins where both files carry the same pick.
    """
    index = {}
    for date in sorted(dates):
        for prefix in ("picks", "picks_morning"):
            path = os.path.join(localdata, f"{prefix}_{date}.json")
            if not os.path.exists(path):
                continue
            doc = json.load(open(path))
            picks = doc.get("picks") if isinstance(doc, dict) else doc
            for pick in picks or []:
                if not isinstance(pick, dict):
                    continue
                market = pick.get("recommended_enhancement")
                p = pick.get("enhancement_probability")
                if not market or p is None:
                    continue
                key = (date, norm_team(pick.get("home") or ""),
                       norm_team(pick.get("away") or ""), market)
                ctx = pick.get("ctx") or {}
                index.setdefault(key, {"p": float(p), "path": path,
                                       "label": pick.get("enhancement_label"),
                                       "league": str(ctx.get("league_raw") or "unknown")})
    return index


def join_records(records: list[dict], picks: dict) -> tuple[list[dict], Counter]:
    stats = Counter()
    joined = []
    for rec in records:
        key = (rec["date"], norm_team(rec["home"]), norm_team(rec["away"]), rec["market"])
        hit = picks.get(key)
        row = {**rec, "p_model": None, "p_form": None, "p_blend": None,
               "p_market": None, "league": "unknown", "pick_path": None}
        if hit is None:
            stats["unjoined"] += 1
        else:
            stats["joined"] += 1
            stats["from_morning" if "/picks_morning_" in hit["path"] else "from_evening"] += 1
            stats["combo_label" if hit["label"] != LABEL_BY_MARKET.get(rec["market"])
                  else "plain_label"] += 1
            row.update({"p_model": hit["p"], "league": hit["league"],
                        "pick_path": hit["path"], "pick_label": hit["label"]})
        joined.append(row)
    return joined, stats


def _brier_pairs(rows: list[dict], field: str) -> list[tuple[float, bool]]:
    return [(r[field], r["hit"]) for r in rows if r.get(field) is not None]


def metric_row(rows: list[dict], field: str) -> dict:
    pairs = _brier_pairs(rows, field)
    losses = [fi.brier([pair]) for pair in pairs]
    lls = [fi.log_loss([pair]) for pair in pairs]
    return {"n": len(pairs), "brier": fi.brier(pairs),
            "brier_ci": fi.bootstrap_ci(losses), "log_loss": fi.log_loss(pairs),
            "log_loss_ci": fi.bootstrap_ci(lls)}


def fmt_metric(name: str, row: dict) -> str:
    if not row["n"]:
        return f"  {name:<20} n=0"
    b, bl, bh = row["brier"], row["brier_ci"]["lo"], row["brier_ci"]["hi"]
    ll, ll_, lh = row["log_loss"], row["log_loss_ci"]["lo"], row["log_loss_ci"]["hi"]
    return (f"  {name:<20} n={row['n']:<4} Brier {b:.4f} [{bl:.4f},{bh:.4f}]   "
            f"log loss {ll:.4f} [{ll_:.4f},{lh:.4f}]")


def blend_field(rows: list[dict], w: float) -> None:
    for r in rows:
        if r.get("p_model") is None:
            continue
        r["p_blend"] = (r["p_model"] + w * (r["p_form"] - r["p_model"])
                        if r.get("p_form") is not None else r["p_model"])


def choose_weight(train: list[dict]) -> float:
    best_w, best_brier = 0.0, None
    for i in range(0, 21):
        w = i / 20
        blend_field(train, w)
        score = fi.brier(_brier_pairs(train, "p_blend"))
        if score is not None and (best_brier is None or score < best_brier):
            best_brier, best_w = score, w
    return best_w


def time_split(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Deterministic split on sorted fixture dates: first 60% train, rest test."""
    days = sorted({r["date"] for r in rows})
    if len(days) < 5:
        return [], []
    cut = days[int(len(days) * 0.6) - 1]
    return [r for r in rows if r["date"] <= cut], [r for r in rows if r["date"] > cut]


def join_coverage(records: list[dict], localdata: str) -> str:
    """Why each settled record did or did not pick up the model's probability.

    B-4 of the round-5 brief. A verdict resting on a join has to say how much
    of the registry it actually saw, and what the rest was: a missing day file,
    a fixture the day's files spell differently, a different market key, or a
    pick with no ``enhancement_probability`` recorded. No substitute guess is
    made anywhere.
    """
    reasons: Counter = Counter()
    for rec in records:
        date = rec["date"]
        files = [os.path.join(localdata, f"{prefix}_{date}.json")
                 for prefix in ("picks", "picks_morning")]
        files = [p for p in files if os.path.exists(p)]
        if not files:
            reasons["no pick file for the date"] += 1
            continue
        fixture = (norm_team(rec["home"]), norm_team(rec["away"]))
        state = "fixture absent from the date's files"
        for path in files:
            doc = json.load(open(path))
            picks = doc.get("picks") if isinstance(doc, dict) else doc
            for pick in picks or []:
                if not isinstance(pick, dict):
                    continue
                if (norm_team(pick.get("home") or ""),
                        norm_team(pick.get("away") or "")) != fixture:
                    continue
                state = "fixture present, recommended_enhancement differs"
                if pick.get("recommended_enhancement") == rec["market"]:
                    state = "fixture and market present, no enhancement_probability"
                    if pick.get("enhancement_probability") is not None:
                        state = "joined"
                    break
            if state == "joined":
                break
        reasons[state] += 1
    joined = reasons["joined"]
    out = [f"join coverage: {joined}/{len(records)} settled records carry the model's "
           f"stated probability",
           f"  reasons for the other {len(records) - joined}:"]
    others = [(reason, count) for reason, count in reasons.most_common()
              if reason != "joined"]
    if others:
        for reason, count in others:
            out.append(f"    {count:>4}  {reason}")
    else:
        out.append("    (none)")
    return "\n".join(out)


def w5(joined: list[dict], archive: fi.ResultsArchive, records: list[dict],
       localdata: str) -> str:
    head = [f"identity: source_team_key (canonical, curated aliases); "
            f"archive rows {len(archive.rows)}",
            "",
            "features tested here are ARCHIVE-derived (deep where old, stale where",
            "recent). The page-block variant (5 rows per team, fresh, league-scoped)",
            "is untested by construction: the match-page ledger is not in production.",
            ""]
    out = []
    for market in MARKET_ORDER:
        rows = [r for r in joined if r["market"] == market]
        if not rows:
            continue
        noise = "   [NOISE: n<30, no conclusion]" if len(rows) < 30 else ""
        out.append(f"== {SHORT_NAME[market]} ({market}) — settled n={len(rows)}  "
                   f"hits {sum(1 for r in rows if r['hit'])}/{len(rows)}{noise}")
        out.append(f"  model p joined: {sum(1 for r in rows if r['p_model'] is not None)}/{len(rows)}"
                   f"   form estimate available: {sum(1 for r in rows if r['p_form'] is not None)}/{len(rows)}")
        for r in rows:
            if r.get("price"):
                r["p_market"] = 1.0 / float(r["price"])
        train, test = time_split(rows)
        if not train:
            blend_field(rows, 0.5)
            body, label = rows, "ALL rows (split not possible)"
            out.append("  split not possible; blend evaluated in-sample at w=0.50")
        else:
            w = choose_weight(train)
            blend_field(train, w)
            blend_field(test, w)
            body, label = test, "TEST rows (out-of-sample)"
            out.append(f"  w* = {w:.2f} chosen on train {train[0]['date']}..{train[-1]['date']} "
                       f"(n={len(train)}); evaluated on {test[0]['date']}..{test[-1]['date']} (n={len(test)})")
        out.append(f"  {label}:")
        for field, name in (("p_model", "model (a)"), ("p_blend", "model+form (b)"),
                            ("p_market", "market 1/price (c)")):
            out.append(fmt_metric(name, metric_row(body, field)))
        d = fi.paired_bootstrap_delta(_brier_pairs(body, "p_model"),
                                      _brier_pairs(body, "p_blend"), metric="brier")
        d2 = fi.paired_bootstrap_delta(_brier_pairs(body, "p_model"),
                                       _brier_pairs(body, "p_market"), metric="brier")
        out.append(f"  paired delta Brier (b)-(a): {d['delta']:+.4f} "
                   f"[{d['lo']:+.4f},{d['hi']:+.4f}] n={d['n']}")
        out.append(f"  paired delta Brier (c)-(a): {d2['delta']:+.4f} "
                   f"[{d2['lo']:+.4f},{d2['hi']:+.4f}] n={d2['n']}")
        hits = sum(1 for r in body if r["hit"])
        base = (hits / len(body)) * (1 - hits / len(body)) if body else float("nan")
        out.append(f"  base rate on the same slice: hits {hits}/{len(body)} -> constant-"
                   f"predictor Brier h(1-h) = {base:.4f}  "
                   f"(the minimum bar; above it is a calibration red flag)")
        # The same constant row on the slice the weight was CHOSEN on. The
        # reported bar belongs to the test slice, so a reader cannot see
        # whether "above the bar" is a property of this market or of the
        # split; printing both makes that visible without tuning anything.
        if train:
            tr_hits = sum(1 for r in train if r["hit"])
            tr_base = (tr_hits / len(train)) * (1 - tr_hits / len(train))
            out.append(f"  base rate on the TRAINING slice: hits {tr_hits}/{len(train)} -> "
                       f"constant-predictor Brier h(1-h) = {tr_base:.4f}  "
                       f"(the same bar on the window w* was chosen on)")
        else:
            out.append("  base rate on the TRAINING slice: not applicable "
                       "(the split is not possible for this market)")
        verdict = ("blend better, not significant on this sample" if d["delta"] < 0
                   else "blend no better" if d["delta"] > 0 else "blend identical")
        market_verdict = ("market scores better, not significantly on this sample"
                          if d2["delta"] < 0 else "market no better")
        out.append(f"  reading: (b) vs (a) {verdict}; (c) vs (a) {market_verdict}.")
        out.append("")
    return "\n".join(head + out)


def _norm_bucket_spellings(archive: fi.ResultsArchive) -> dict:
    """Every side spelling seen, grouped by the width-9 ``norm_team`` bucket."""
    from collections import Counter, defaultdict

    from edgefactory.util import norm_team

    out: dict = defaultdict(Counter)
    for row in archive.rows:
        for side in ("home", "away"):
            out[norm_team(row[side])][row[side]] += 1
    return dict(out)


def _unjoined_spellings(spellings: dict, archive: fi.ResultsArchive, team: str) -> str:
    """The spellings of ``team``'s width-9 bucket the canonical key rejects."""
    from edgefactory.identity import source_team_key
    from edgefactory.util import norm_team

    key = source_team_key(team)
    parts = []
    for name, count in spellings.get(norm_team(team), {}).most_common():
        if source_team_key(name) != key:
            parts.append(f"{name!r} x{count}")
        if len(parts) >= 5:
            break
    return ", ".join(parts) if parts else "(none in the width-9 bucket)"


def w3(archive: fi.ResultsArchive, joined: list[dict]) -> str:
    fixtures = [{"date": r["date"], "home": r["home"], "away": r["away"],
                 "league": r["league"]} for r in joined]
    table = fi.coverage(archive, fixtures)
    out = [f"archive rows: {len(archive.rows)}   settled fixtures: {table['total']}",
           "team identity: source_team_key (canonical, curated aliases, squad classes",
           "vetoed); the width-9 norm_team bucket is reported below but not counted",
           f"with {table['window']}+ prior matches both sides: {table['sufficient']}"
           f"   insufficient_history: {table['insufficient']}", "", "per month:"]
    for month, row in table["by_month"].items():
        out.append(f"  {month}  total {row['total']:>4}  sufficient {row['sufficient']:>4}  "
                   f"insufficient {row['insufficient']:>4}")
    out.append("")
    out.append("per league (top 30 by fixtures):")
    for league, row in list(table["by_league"].items())[:30]:
        out.append(f"  {league[:52]:<52} total {row['total']:>4}  sufficient {row['sufficient']:>4}")
    zero = [(r, len(archive.prior_rows(r["home"], r["date"])),
             len(archive.prior_rows(r["away"], r["date"]))) for r in joined]
    zero = [(r, h, a) for r, h, a in zero if min(h, a) == 0]
    out += ["", f"name-matching misses (a side with 0 archive rows at pick date): {len(zero)}"]
    for r, h, a in zero[:15]:
        out.append(f"  {r['date']} {r['home']} vs {r['away']:<28} priors home={h} away={a}")
    thin = [(r, len(archive.prior_rows(r["home"], r["date"])),
             len(archive.prior_rows(r["away"], r["date"]))) for r in joined]
    thin = [(r, h, a) for r, h, a in thin if 0 < min(h, a) < fi.MIN_HISTORY]
    out += ["", f"insufficient_history rows (0 < priors < {fi.MIN_HISTORY}): {len(thin)}"]
    for r, h, a in thin:
        est = fi.form_market_probability(archive, r["home"], r["away"], r["date"], r["market"])
        classes = [fi.squad_class(r["home"]), fi.squad_class(r["away"])]
        tag = "" if classes == ["senior", "senior"] else f"  squad_class={classes}"
        out.append(f"  {r['date']} {r['home']} vs {r['away']:<28} priors {h}/{a} "
                   f"p={est['p']} reason={est['reason']}{tag}")
    classes = Counter(s["class"] for s in table["insufficient_sides"])
    out += ["", f"thin sides by squad class (of {len(table['insufficient_sides'])} sides): "
            + ", ".join(f"{k} x{v}" for k, v in classes.most_common()),
            "  a non-senior side's thin history is the archive covering that class",
            "  of competition far less; keep such sides out of any floor-deriving slice."]
    spellings = _norm_bucket_spellings(archive)
    out += ["", "unjoined spellings on those sides (width-9 bucket rows the canonical",
            "key rejects - the curated alias table does not join these):"]
    for r in joined:
        for side in ("home", "away"):
            team = r[side]
            priors = len(archive.prior_rows(team, r["date"]))
            if priors >= fi.MIN_HISTORY:
                continue
            out.append(f"  {r['date']} {team:<28} canonical priors {priors:>3}   "
                       f"unjoined: {_unjoined_spellings(spellings, archive, team)}")
    return "\n".join(out)


def main() -> None:
    archive = fi.load_archive(LOCALDATA)
    records = load_records(LOCALDATA)
    picks = load_picks(LOCALDATA, {r["date"] for r in records})
    joined, stats = join_records(records, picks)
    for r in joined:
        est = fi.form_market_probability(archive, r["home"], r["away"], r["date"], r["market"])
        r["p_form"] = est["p"]
        r["form_reason"] = est.get("reason")
    print(f"archive rows: {len(archive.rows)}")
    print(f"registry records: {len(records)}  join: {dict(stats)}")
    print(f"form estimate available: {sum(1 for r in joined if r['p_form'] is not None)}/{len(joined)}")
    with open(os.path.join(HERE, "w5_signal.txt"), "w") as fh:
        fh.write(join_coverage(records, LOCALDATA))
        fh.write("\n\n")
        fh.write(w5(joined, archive, records, LOCALDATA))
    with open(os.path.join(HERE, "w3_coverage.txt"), "w") as fh:
        fh.write(w3(archive, joined))
    print("wrote w3_coverage.txt and w5_signal.txt")


if __name__ == "__main__":
    main()
