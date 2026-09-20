#!/usr/bin/env python3
"""Home-fade ml-fade price-robustness study — read-only, exploratory driver.

    python3 scripts/research_ml_fade_price_study.py

Continuation of the conditional ml-fade scan (see research_ml_fade_contexts.py).
Subject: the home-fade ladder, PREDECLARED from that scan's honest evidence
(train+validation; the confirmation window start 2026-01-01 was declared
before selection). Question now: does the signal survive realistic pricing,
outlier removal, concentration and persistence stress tests?

Price sources (ALL pre-kickoff captures, no closing prices):
- fb: forebet odd1/odd2 — the production fade price (what the settled view
  uses; consensus3.pick_odds prices the PARENT side, not the fade);
- zb: zulubet odd1/odd2 — an independent second capture from
  zulubet_settled (66,808 rows); coverage on the home-fade ladder is partial
  and EVERY source variant reports its own priced-row count;
- best/worst/mid: max / min / harmonic-mean of available quotes.

Transforms (all recorded per variant): repo haircut roi x BEST_ODDS_HAIRCUT
(0.5), conservative haircut roi x 0.25, price-space haircut o' = 1+(o-1)*0.5,
maximum-odds caps 5/10/20, predeclared bands 1.20-2.00 / 2.00-3.00 /
3.00-5.00 / 5.00-10.00 / 10+, and both-sources-only evidence (mid and worst
over rows where BOTH captures exist).

Outputs: localdata/ml_fade_price_study.{json,md} (gitignored artifacts).
This script promotes NOTHING and never touches the production registry,
gates, picks, tickets, settlement or dedup code.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb

from edgefactory import fade_research as fr
from edgefactory.config import BEST_ODDS_HAIRCUT, GATES
from edgefactory.entities import canonical_league, classify_competition

ML_PREDS = ROOT / "localdata" / "ml_meta_predictions.csv.gz"
WAREHOUSE = ROOT / "localdata" / "warehouse.duckdb"

VARIANTS_GRADED = 0  # honesty counter: every pnl_stats by_window call


def load_rows(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """The ml_fade_settled slice extended with the second price capture and the
    full fb book. Same join/dedup semantics as the production view (DISTINCT ON
    date/home/away), plus zb quotes and fb odd1/oddx/odd2 for the implied
    baseline. NULL prices stay NULL — nothing is silently substituted."""
    if not ML_PREDS.exists():
        raise SystemExit(f"missing {ML_PREDS} — run scripts/mine_consensus.py first")
    con.execute(f"""
        CREATE OR REPLACE TEMP VIEW ml_meta_raw AS
        SELECT date, home, away, TRY_CAST(ml_p AS DOUBLE) AS ml_p, pick
        FROM read_csv_auto('{ML_PREDS}', all_varchar=true, union_by_name=true)
    """)
    con.execute("""
        CREATE OR REPLACE TEMP VIEW study_rows AS
        WITH ml AS (SELECT DISTINCT ON (date, home, away) * FROM ml_meta_raw),
             c3 AS (SELECT DISTINCT ON (date, home, away) * FROM consensus3),
             fb AS (SELECT DISTINCT ON (date, home, away) date, home, away,
                           odd1, oddx, odd2 FROM forebet_settled),
             zb AS (SELECT DISTINCT ON (date, home, away) date, home, away,
                           odd1 AS zb_odd1, odd2 AS zb_odd2 FROM zulubet_settled)
        SELECT CAST(c3.date AS VARCHAR) AS date, c3.home, c3.away, c3.sport,
               c3.league, c3.outcome,
               ml.pick AS parent_pick,
               CASE ml.pick WHEN 'home' THEN 'away' ELSE 'home' END AS pick,
               ml.ml_p,
               CASE ml.pick WHEN 'home' THEN fb.odd2 ELSE fb.odd1 END AS fb_odds,
               CASE ml.pick WHEN 'home' THEN zb.zb_odd2 ELSE zb.zb_odd1 END AS zb_odds,
               c3.pick_odds AS parent_pick_odds,
               fb.odd1, fb.oddx, fb.odd2
        FROM c3 JOIN ml USING (date, home, away)
                LEFT JOIN fb USING (date, home, away)
                LEFT JOIN zb USING (date, home, away)
        WHERE ml.pick IN ('home', 'away')
    """)
    rows = con.sql("SELECT * FROM study_rows").fetchdf().to_dict("records")
    for r in rows:
        r["date"] = str(r["date"])[:10]
        r["league_canonical"] = canonical_league(r.get("league")) or "UNKNOWN"
        r["comp_type_pre"] = classify_competition(r.get("league"))
    return rows


def slim(stats: dict) -> dict:
    """JSON-safe copy of pnl_stats output (drops row references)."""
    return {k: v for k, v in stats.items() if k != "rows_priced"}


def counted_by_window(matched: list[dict], source: str, split: str, confirm: str, **kw) -> dict:
    global VARIANTS_GRADED
    VARIANTS_GRADED += 1
    return fr.by_window(matched, source, split, confirm, **kw)


def _roi(x) -> str:
    return f"{x * 100:+.1f}%" if isinstance(x, float) and not math.isnan(x) else "—"


def _num(v) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def _in_window(d: str, w: str, split: str, confirm: str) -> bool:
    if w == "confirm":
        return d >= confirm
    if w == "train":
        return d < split
    return split <= d < confirm


def _fb_overround(rows: list[dict], w: str, split: str, confirm: str) -> float | None:
    tot = n = 0
    for r in rows:
        if not _in_window(r["date"], w, split, confirm):
            continue
        o1, ox, o2 = (_num(r.get(k)) for k in ("odd1", "oddx", "odd2"))
        if o1 and ox and o2:
            tot += 1 / o1 + 1 / ox + 1 / o2 - 1
            n += 1
    return round(tot / n, 4) if n else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--split", default=GATES.walkforward_split)
    ap.add_argument("--confirm-start", default=fr.DEFAULT_CONFIRM_START)
    ap.add_argument("--warehouse", default=str(WAREHOUSE))
    ap.add_argument("--out-json", default=str(ROOT / "localdata" / "ml_fade_price_study.json"))
    ap.add_argument("--out-md", default=str(ROOT / "localdata" / "ml_fade_price_study.md"))
    args = ap.parse_args()

    con = duckdb.connect(args.warehouse, read_only=True)
    rows = load_rows(con)
    ladder = {
        thr: fr.Candidate(thr, (fr.HOME_FADE_CONDITION,)) for thr in fr.PRICE_STUDY_THRESHOLDS
    }
    matched = {thr: [r for r in rows if c.matches(r)] for thr, c in ladder.items()}
    primary = fr.PRIMARY_STUDY_THRESHOLD

    out: dict = {
        "meta": {},
        "baseline_fb": {},
        "sources": {},
        "transforms": {},
        "concentration": {},
        "bootstrap": {},
        "persistence": {},
        "controls": {},
        "wilson": {},
    }

    # ---- 1. baseline reproduction (production price source fb) -----------
    for thr in fr.PRICE_STUDY_THRESHOLDS:
        out["baseline_fb"][str(thr)] = slim_all(
            counted_by_window(matched[thr], "fb", args.split, args.confirm_start)
        )
    # rows_priced kept aside for deep analysis
    primary_windows = fr.by_window(matched[primary], "fb", args.split, args.confirm_start)

    # ---- 2. price-source matrix ------------------------------------------
    for thr in fr.PRICE_STUDY_THRESHOLDS:
        out["sources"][str(thr)] = {
            s: slim_all(counted_by_window(matched[thr], s, args.split, args.confirm_start))
            for s in fr.PRICE_SOURCES
        }

    # ---- 3. transforms on the primary candidate ---------------------------
    tr = {}
    tr["roi_scale_0.5"] = slim_all(
        counted_by_window(
            matched[primary], "fb", args.split, args.confirm_start, roi_scale=BEST_ODDS_HAIRCUT
        )
    )
    tr["roi_scale_0.25"] = slim_all(
        counted_by_window(
            matched[primary],
            "fb",
            args.split,
            args.confirm_start,
            roi_scale=fr.CONSERVATIVE_ROI_SCALE,
        )
    )
    tr["price_adjust_0.5"] = slim_all(
        counted_by_window(
            matched[primary], "fb", args.split, args.confirm_start, adjust_k=fr.PRICE_ADJUST_K
        )
    )
    for cap in fr.ODDS_CAPS:
        tr[f"cap_{cap:g}"] = slim_all(
            counted_by_window(matched[primary], "fb", args.split, args.confirm_start, cap=cap)
        )
    for lo, hi in fr.PRICE_STUDY_BANDS:
        tr[f"band_{lo:g}_{'+inf' if hi >= 1e9 else f'{hi:g}'}"] = slim_all(
            counted_by_window(matched[primary], "fb", args.split, args.confirm_start, band=(lo, hi))
        )
    both = [
        r
        for r in matched[primary]
        if fr.price_of(r, "fb") is not None and fr.price_of(r, "zb") is not None
    ]
    tr["both_sources_mid"] = slim_all(
        counted_by_window(both, "mid", args.split, args.confirm_start)
    )
    tr["both_sources_worst"] = slim_all(
        counted_by_window(both, "worst", args.split, args.confirm_start)
    )
    out["transforms"] = tr
    out["meta"]["both_sources_rows"] = len(both)

    # ---- 4. concentration + bootstrap -------------------------------------
    for thr in fr.PRICE_STUDY_THRESHOLDS:
        windows = fr.by_window(matched[thr], "fb", args.split, args.confirm_start)
        out["concentration"][str(thr)] = {
            w: fr.concentration(s["rows_priced"]) for w, s in windows.items()
        }
        out["bootstrap"][str(thr)] = {
            w: fr.bootstrap_roi_ci([p for _, _, p in s["rows_priced"]]) for w, s in windows.items()
        }

    deep = {}
    for wname, s in primary_windows.items():
        rp = s["rows_priced"]
        deep[wname] = {
            "months": fr.contribution_by(rp, fr.month_key),
            "quarters": fr.contribution_by(rp, fr.quarter_key),
            "leagues": fr.contribution_by(rp, fr.league_key),
            "bands": fr.contribution_by(rp, fr.band_key()),
            "implied": fr.implied_baseline(rp),
            "top_winners": [
                {
                    "date": r["date"],
                    "home": r["home"],
                    "away": r["away"],
                    "league": r["league_canonical"],
                    "fb_odds": round(o, 2),
                    "pnl": round(p, 3),
                }
                for r, o, p in sorted((x for x in rp if x[2] > 0), key=lambda x: -x[2])[:8]
            ],
        }
    out["deep_primary"] = deep
    out["meta"]["fb_overround_primary"] = {
        w: _fb_overround(matched[primary], w, args.split, args.confirm_start)
        for w in ("train", "valid", "confirm")
    }

    # ---- 5. persistence counters ------------------------------------------
    for thr in fr.PRICE_STUDY_THRESHOLDS:
        windows = fr.by_window(matched[thr], "fb", args.split, args.confirm_start)
        pers = {}
        for wname, s in windows.items():
            months = fr.contribution_by(s["rows_priced"], fr.month_key)
            judged = [m for m in months if m["n_priced"] >= fr.MIN_MONTH_N]
            pers[wname] = {
                "n_days": s["n_days"],
                "months_total": len(months),
                "months_judged": len(judged),
                "months_judged_positive": sum(1 for m in judged if m["pnl"] > 0),
                "months_any_positive": sum(1 for m in months if m["pnl"] > 0),
            }
        out["persistence"][str(thr)] = pers

    # ---- 6. controls (primary threshold, fb price) ------------------------
    ctrl = {}
    ctrl["aggregate_ml_fade"] = slim_all(
        counted_by_window(
            [r for r in rows if fr.Candidate(primary).matches(r)],
            "fb",
            args.split,
            args.confirm_start,
        )
    )
    ctrl["away_fade"] = slim_all(
        counted_by_window(
            [
                r
                for r in rows
                if fr.Candidate(primary, (fr.Condition("fade_side", "fade_side", "away"),)).matches(
                    r
                )
            ],
            "fb",
            args.split,
            args.confirm_start,
        )
    )
    parent_rows = [
        {**r, "pick": r["parent_pick"], "fb_odds": r["parent_pick_odds"], "zb_odds": None}
        for r in matched[primary]
    ]
    ctrl["parent_same_rows"] = slim_all(
        counted_by_window(parent_rows, "fb", args.split, args.confirm_start)
    )
    ctrl["unfiltered_home_fade"] = slim_all(
        counted_by_window(
            [r for r in rows if fr.Candidate(0.0, (fr.HOME_FADE_CONDITION,)).matches(r)],
            "fb",
            args.split,
            args.confirm_start,
        )
    )
    thr0 = [r for r in rows if fr.Candidate(0.0, (fr.HOME_FADE_CONDITION,)).matches(r)]
    ctrl["same_bands_no_ml_condition"] = {
        f"{lo:g}_{'+inf' if hi >= 1e9 else f'{hi:g}'}": slim_all(
            counted_by_window(thr0, "fb", args.split, args.confirm_start, band=(lo, hi))
        )
        for lo, hi in fr.PRICE_STUDY_BANDS
    }
    ctrl["implied_baseline_primary"] = {
        w: deep[w]["implied"] for w in ("train", "valid", "confirm")
    }
    out["controls"] = ctrl

    # ---- 7. Wilson gate math ----------------------------------------------
    for thr in fr.PRICE_STUDY_THRESHOLDS:
        v = out["baseline_fb"][str(thr)]["valid"]
        out["wilson"][str(thr)] = fr.wilson_gate_analysis(v["hit"], v["n"])

    # ---- 7b. strength classification (predeclared decision rule) ----------
    price_variants = {
        src: {w: out["sources"][str(primary)][src][w]["roi"] for w in ("valid", "confirm")}
        for src in fr.PRICE_TEST_SOURCES
    }
    label, reasons = fr.classify_signal_strength(
        valid=out["baseline_fb"][str(primary)]["valid"],
        confirm=out["baseline_fb"][str(primary)]["confirm"],
        concentration_valid=out["concentration"][str(primary)]["valid"],
        concentration_confirm=out["concentration"][str(primary)]["confirm"],
        bootstrap_valid=out["bootstrap"][str(primary)]["valid"],
        bootstrap_confirm=out["bootstrap"][str(primary)]["confirm"],
        persistence_valid=out["persistence"][str(primary)]["valid"],
        persistence_confirm=out["persistence"][str(primary)]["confirm"],
        price_variants=price_variants,
    )
    out["audit"] = {
        "subject": ladder[primary].name(),
        "classification": label,
        "reasons": reasons,
        "price_variant_inputs": price_variants,
        "robust_thresholds": {
            "min_p_positive": fr.ROBUST_MIN_P_POSITIVE,
            "top3_min_roi": fr.ROBUST_TOP3_MIN_ROI,
            "min_month_share_positive": fr.ROBUST_MIN_MONTH_SHARE_POSITIVE,
            "min_judged_months": fr.ROBUST_MIN_JUDGED_MONTHS,
            "price_test_sources": list(fr.PRICE_TEST_SOURCES),
        },
        "note": "research-strength classification only; production certification is untouched",
    }

    # ---- 8. meta ------------------------------------------------------------
    out["meta"].update(
        {
            "generated_at": datetime.now(UTC).date().isoformat(),
            "subject": "home-fade ladder, predeclared from the context scan "
            "(train+valid evidence; confirmation window declared before selection)",
            "split": args.split,
            "confirm_start": args.confirm_start,
            "rows_total": len(rows),
            "matched_per_threshold": {t: len(matched[t]) for t in matched},
            "price_sources": {
                s: "forebet odd1/odd2 (production)"
                if s == "fb"
                else "zulubet odd1/odd2 (independent capture)"
                if s == "zb"
                else "max of available quotes"
                if s == "best"
                else "min of available quotes"
                if s == "worst"
                else "harmonic mean of available quotes"
                for s in fr.PRICE_SOURCES
            },
            "transforms": {
                "roi_scale_0.5": "repo BEST_ODDS_HAIRCUT convention",
                "roi_scale_0.25": "harsher conservative haircut",
                "price_adjust_0.5": "o' = 1 + (o-1)*0.5 on winners",
                "caps": list(fr.ODDS_CAPS),
                "bands": [list(b) for b in fr.PRICE_STUDY_BANDS],
                "both_sources": "rows having BOTH fb and zb quotes",
            },
            "candidates_searched": len(ladder),
            "variants_graded": VARIANTS_GRADED,
            "bootstrap": {"n": fr.BOOTSTRAP_N, "seed": fr.BOOTSTRAP_SEED},
            "production_gates_unchanged": True,
            "registry_touched": False,
        }
    )

    Path(args.out_json).write_text(json.dumps(out, indent=2, default=str))
    md = render_md(out, primary)
    Path(args.out_md).write_text(md)
    print(f"rows: {len(rows)}, subject ladder: {list(fr.PRICE_STUDY_THRESHOLDS)}")
    print(f"variants graded: {VARIANTS_GRADED}")
    print(f"audit classification: {out['audit']['classification']}")
    print(f"wrote {args.out_json} and {args.out_md}")
    return 0


def slim_all(window_map: dict) -> dict:
    return {w: slim(s) for w, s in window_map.items()}


def render_md(out: dict, primary: int):
    thr_l = list(fr.PRICE_STUDY_THRESHOLDS)
    m = []
    m.append("# Home-fade ml-fade — price-robustness study (exploratory, read-only)\n")
    m.append(
        f"- generated: {out['meta']['generated_at']} | split `{out['meta']['split']}` "
        f"| confirmation (untouched, predeclared): `>= {out['meta']['confirm_start']}`"
    )
    m.append(
        f"- rows in fade slice: {out['meta']['rows_total']:,}; "
        f"candidates searched: {out['meta']['candidates_searched']} (home-fade "
        f"thr {thr_l}); variants graded: {out['meta']['variants_graded']}"
    )
    m.append("- production gates UNCHANGED; nothing certified, emitted or integrated\n")
    m.append(
        f"**Strength classification (predeclared decision rule, "
        f"`fade_research.classify_signal_strength`): {out['audit']['classification']}**"
    )
    for r in out["audit"]["reasons"]:
        m.append(f"- {r}")
    m.append("")

    m.append("## 1. Baseline reproduction (production price source: forebet)\n")
    m.append(
        "| thr | train n/priced hit roi | valid n/priced hit roi (wilson) "
        "| confirm n/priced hit roi |"
    )
    m.append("|---|---|---|---|")
    for thr in thr_l:
        b = out["baseline_fb"][str(thr)]
        t, v, c = b["train"], b["valid"], b["confirm"]
        m.append(
            f"| {thr} | {t['n']}/{t['n_priced']} {t['hit']:.3f} {_roi(t['roi'])} | "
            f"{v['n']}/{v['n_priced']} {v['hit']:.3f} {_roi(v['roi'])} "
            f"(lb {v['wilson_lb']:.3f}) | "
            f"{c['n']}/{c['n_priced']} {c['hit']:.3f} {_roi(c['roi'])} |"
        )
    m.append("")

    m.append("## 2. Price-source matrix (ROI; priced n in parens)\n")
    for wname in ("train", "valid", "confirm"):
        m.append(f"### {wname}\n")
        m.append("| thr | fb | zb | best | worst | mid |")
        m.append("|---|---|---|---|---|---|")
        for thr in thr_l:
            src = out["sources"][str(thr)]
            cells = []
            for s in fr.PRICE_SOURCES:
                st = src[s][wname]
                cells.append(f"{_roi(st['roi'])} ({st['n_priced']})")
            m.append(f"| {thr} | " + " | ".join(cells) + " |")
        m.append("")

    m.append(f"## 3. Transforms on the primary candidate (thr {primary})\n")
    m.append("| variant | train n/p roi | valid n/p roi | confirm n/p roi |")
    m.append("|---|---|---|---|")
    for name, tw in out["transforms"].items():
        t, v, c = tw["train"], tw["valid"], tw["confirm"]
        m.append(
            f"| {name} | {t['n']}/{t['n_priced']} {_roi(t['roi'])} | "
            f"{v['n']}/{v['n_priced']} {_roi(v['roi'])} | "
            f"{c['n']}/{c['n_priced']} {_roi(c['roi'])} |"
        )
    m.append(
        f"\nRows with BOTH fb and zb quotes (primary, pooled): {out['meta']['both_sources_rows']}"
    )
    m.append(
        "fb overround (avg 1/o1+1/ox+1/o2−1): "
        + ", ".join(
            f"{w} {out['meta']['fb_overround_primary'][w]}" for w in ("train", "valid", "confirm")
        )
        + "\n"
    )

    m.append("## 4. Concentration (fb price)\n")
    m.append(
        "| thr | window | n p | top-1 removed | top-2 | top-3 | "
        "median bet | winners | win events | leagues(win/overall) |"
    )
    m.append("|---|---|---|---|---|---|---|---|---|---|")
    for thr in thr_l:
        for wname in ("train", "valid", "confirm"):
            k = out["concentration"][str(thr)][wname]
            m.append(
                f"| {thr} | {wname} | {k['n_priced']} | "
                f"{_roi(k['roi_wo_top1'])} | {_roi(k['roi_wo_top2'])} | "
                f"{_roi(k['roi_wo_top3'])} | {k['median_bet_return']} | "
                f"{k['n_winners']} | {k['distinct_win_events']} | "
                f"{k['distinct_win_leagues']}/{k['distinct_leagues']} |"
            )
    m.append("")
    m.append("Bootstrap CI (percentile, per-bet pnl mean = roi):\n")
    m.append("| thr | window | point | 2.5% | 97.5% | P(roi>0) |")
    m.append("|---|---|---|---|---|---|")
    for thr in thr_l:
        for wname in ("train", "valid", "confirm"):
            b = out["bootstrap"][str(thr)][wname]
            m.append(
                f"| {thr} | {wname} | {_roi(b['point'])} | {_roi(b['ci_lo'])} "
                f"| {_roi(b['ci_hi'])} | {b['p_positive']} |"
            )
    m.append("")

    m.append(f"## 5. Persistence (fb price; judged months = n≥{fr.MIN_MONTH_N})\n")
    m.append("| thr | window | days | judged months | positive | all months +/− |")
    m.append("|---|---|---|---|---|---|")
    for thr in thr_l:
        for wname in ("train", "valid", "confirm"):
            p = out["persistence"][str(thr)][wname]
            m.append(
                f"| {thr} | {wname} | {p['n_days']} | {p['months_judged']} | "
                f"{p['months_judged_positive']} | "
                f"{p['months_any_positive']}/{p['months_total']} |"
            )
    m.append("")
    m.append(f"### Primary thr {primary}: monthly detail\n")
    for wname in ("train", "valid", "confirm"):
        months = out["deep_primary"][wname]["months"]
        m.append(
            f"**{wname}**: "
            + ", ".join(f"{mo['key']} {mo['n_priced']}p {_roi(mo['roi'])}" for mo in months)
        )
        m.append("")
    m.append(f"### Primary thr {primary}: league and band contributions (pnl share)\n")
    for wname in ("valid", "confirm"):
        m.append(
            f"**{wname} leagues**: "
            + "; ".join(
                f"{lg['key']} {lg['n_priced']}p {_roi(lg['roi'])} ({lg['pnl_share']})"
                for lg in out["deep_primary"][wname]["leagues"][:8]
            )
        )
        m.append("")
        m.append(
            f"**{wname} bands**: "
            + "; ".join(
                f"{b['key']} {b['n_priced']}p {_roi(b['roi'])} ({b['pnl_share']})"
                for b in out["deep_primary"][wname]["bands"]
            )
        )
        m.append("")
    m.append(f"### Primary thr {primary}: largest winner returns\n")
    for wname in ("valid", "confirm"):
        for w in out["deep_primary"][wname]["top_winners"]:
            m.append(
                f"- {wname} {w['date']} {w['home']} v {w['away']} "
                f"[{w['league']}] @{w['fb_odds']} → +{w['pnl']}"
            )
    m.append("")

    m.append("## 6. Controls (primary threshold, fb price)\n")
    m.append("| control | train n/p roi | valid n/p roi | confirm n/p roi |")
    m.append("|---|---|---|---|")
    for name, tw in out["controls"].items():
        if name in ("same_bands_no_ml_condition", "implied_baseline_primary"):
            continue
        t, v, c = tw["train"], tw["valid"], tw["confirm"]
        m.append(
            f"| {name} | {t['n']}/{t['n_priced']} {_roi(t['roi'])} | "
            f"{v['n']}/{v['n_priced']} {_roi(v['roi'])} | "
            f"{c['n']}/{c['n_priced']} {_roi(c['roi'])} |"
        )
    m.append("\nUnconditional bands (home-fade thr 0, no ML condition):\n")
    m.append("| band | train n/p roi | valid n/p roi | confirm n/p roi |")
    m.append("|---|---|---|---|")
    for name, tw in out["controls"]["same_bands_no_ml_condition"].items():
        t, v, c = tw["train"], tw["valid"], tw["confirm"]
        m.append(
            f"| {name} | {t['n']}/{t['n_priced']} {_roi(t['roi'])} | "
            f"{v['n']}/{v['n_priced']} {_roi(v['roi'])} | "
            f"{c['n']}/{c['n_priced']} {_roi(c['roi'])} |"
        )
    m.append("\nImplied-probability baseline (avg 1/odds vs observed hit):\n")
    m.append("| window | priced | avg implied | observed hit | delta |")
    m.append("|---|---|---|---|---|")
    for wname, im in out["controls"]["implied_baseline_primary"].items():
        m.append(
            f"| {wname} | {im['n_priced']} | {im['avg_implied_prob']} | "
            f"{im['observed_hit']} | {im['hit_minus_implied']} |"
        )
    m.append("")

    m.append("## 7. Wilson gate math (unchanged production gate)\n")
    m.append(
        "| thr | valid hit | wilson lb | required hit at this n | fair-odds ceiling | required n |"
    )
    m.append("|---|---|---|---|---|---|")
    for thr in thr_l:
        wg = out["wilson"][str(thr)]
        req = wg["required_n"] if wg["required_n"] is not None else "impossible"
        m.append(
            f"| {thr} | {wg['hit']:.4f} | {wg['wilson_lb']:.4f} | "
            f"{wg['required_hit_at_n']} | {wg['fair_odds_ceiling_for_gate']} | {req} |"
        )
    low = out["wilson"][str(thr_l[0])]
    m.append(
        f"\nNote: {low.get('impossible_reason') or ''} "
        "(same monotone argument applies to every threshold below hit 0.5).\n"
    )
    m.append("## 8. Method notes\n")
    m.append(
        "- conditions use bet-time info only (ml_p, fade side, league, date); "
        "outcome is used solely for grading; no closing prices anywhere"
    )
    m.append(
        "- subject chosen from the PRIOR scan's train+valid evidence; the "
        "confirmation window start was declared before any slice was selected"
    )
    m.append(
        "- every variant reports its own priced-row count; unpriced rows "
        "never inherit a price; nothing is silently substituted"
    )
    m.append(
        "- all 6 ladder candidates x all variants are in the JSON; the "
        "strongest-looking combination remains exploratory"
    )
    m.append("- artifacts: localdata/ml_fade_price_study.{json,md} (gitignored)")
    return "\n".join(m) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
