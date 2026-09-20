#!/usr/bin/env python3
"""Conditional ml-fade slice scan — read-only research driver.

    python3 scripts/research_ml_fade_contexts.py                    # defaults
    python3 scripts/research_ml_fade_contexts.py --confirm-start 2026-01-01

Question: does a PROFITABLE ml-fade slice hide inside a well-defined context
(league / competition type / odds band / model-probability band / fade side /
combinations of side with the two categorical dims), at any parent-confidence
threshold? The aggregate ml-fade family loses money at every threshold, so
any conditional winner must survive:

  1. the production certification gates verbatim (edgefactory.config.GATES —
     never altered), on accounting identical to mine_consensus.stats;
  2. research-only tightening (valid-day count, non-negative train halves);
  3. an untouched confirmation window (default date >= 2026-01-01, predeclared);
  4. realistic pricing (raw ROI x BEST_ODDS_HAIRCUT, the repo's halve-it
     convention) reported alongside raw figures;
  5. full-disclosure multiple testing: the finite predeclared grid
     (edgefactory.fade_research) is graded COMPLETELY and every result is
     written out — nothing hidden, overlapping variants deduped.

Controls reported per promising candidate: aggregate ml-fade at the same
threshold, the ml-meta PARENT at the same threshold, the unconditional
context slice (no threshold), the parent graded without fading in the same
context, and the fade-everything market baseline.

This script promotes NOTHING: the production registry is never read for
decisions and never written. Outputs: localdata/ml_fade_context_scan.json
(machine) and localdata/ml_fade_context_scan.md (human). A research-certified
candidate would still need re-mining through the production path to be a rule.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb

from edgefactory import fade_research as fr
from edgefactory.config import BEST_ODDS_HAIRCUT, GATES
from edgefactory.entities import canonical_league, classify_competition
from edgefactory.fade import ml_fade_settled_sql

FADE_VIEW = "ml_fade_settled"
ML_PREDS = ROOT / "localdata" / "ml_meta_predictions.csv.gz"
WAREHOUSE = ROOT / "localdata" / "warehouse.duckdb"

# A candidate becomes "promising" (per-context controls + report highlight)
# when it clears the production gates OR is non-negative out of sample with
# a reviewable sample. Reporting threshold only — classification
# (fr.decide_promotion) is independent of it.
PROMISING_MIN_VALID_N = 30


# --------------------------------------------------------------------------
# Data access — recreate the same L1 view chain the monitors use, once.
# --------------------------------------------------------------------------
def load_rows(con: duckdb.DuckDBPyConnection) -> list[dict]:
    if not ML_PREDS.exists():
        raise SystemExit(f"missing {ML_PREDS} — run scripts/mine_consensus.py first")
    con.execute(f"""
        CREATE OR REPLACE TEMP VIEW ml_meta_raw AS
        SELECT date, home, away, TRY_CAST(ml_p AS DOUBLE) AS ml_p, pick
        FROM read_csv_auto('{ML_PREDS}', all_varchar=true, union_by_name=true)
    """)
    con.execute(ml_fade_settled_sql("ml_meta_raw"))
    rows = (
        con.sql(f"""
        SELECT CAST(date AS VARCHAR) AS date, home, away, sport, league,
               outcome, parent_pick, pick, ml_p, pick_odds, parent_pick_odds
        FROM {FADE_VIEW}
    """)
        .fetchdf()
        .to_dict("records")
    )
    for r in rows:
        # precompute once per row (leakage-safe: league is pre-kickoff info)
        r["league_canonical"] = canonical_league(r.get("league")) or "UNKNOWN"
        r["comp_type_pre"] = classify_competition(r.get("league"))
    return rows


def grade(rows: list[dict], candidate: fr.Candidate, split: str, confirm_start: str) -> dict:
    graded = fr.grade_rows(rows, candidate, split, confirm_start)
    prod_ok, _ = fr.production_gates_pass(graded)
    status, reasons = fr.decide_promotion(graded)
    return {
        "candidate": candidate.name(),
        "dim": candidate.dim(),
        "threshold": candidate.threshold,
        "provenance": candidate.provenance(),
        "graded": graded,
        "production_gates_pass": prod_ok,
        "status": status,
        "reasons": reasons,
    }


def as_parent_rows(rows: list[dict]) -> list[dict]:
    """Remap each fade row to its parent selection for parent controls:
    pick becomes the ml-meta selection priced at ITS own odds."""
    return [{**r, "pick": r["parent_pick"], "pick_odds": r["parent_pick_odds"]} for r in rows]


# --------------------------------------------------------------------------
# Reporting helpers
# --------------------------------------------------------------------------
def _roi(x: float | None) -> str:
    return f"{x * 100:+.1f}%" if x is not None else "—"


def _n(w: dict) -> str:
    return f"{w['n']}/{w['n_priced']}"


def _row_md(res: dict, extra_class: str | None = None) -> str:
    g = res["graded"]
    tr, va, cf = g["train"], g["valid"], g["confirm"]
    return (
        f"| {res['candidate']} | {res['dim']} | "
        f"{_n(tr)} {_roi(tr['roi'])} | {_n(va)} {_roi(va['roi'])} "
        f"({va['n_days']}d, lb {va['wilson_lb']:.2f}) | "
        f"{_n(cf)} {_roi(cf['roi'])} | {_roi(va['roi_realistic'])} | "
        f"{extra_class or res['status']} |"
    )


def is_promising(res: dict) -> bool:
    va = res["graded"]["valid"]
    return res["production_gates_pass"] or (
        va["n"] >= PROMISING_MIN_VALID_N and va["roi"] is not None and va["roi"] > 0
    )


def _roi_row(graded: dict | None) -> str:
    if graded is None:
        return "— | — | —"
    return (
        f"{_roi(graded['train']['roi'])} | {_roi(graded['valid']['roi'])} | "
        f"{_roi(graded['confirm']['roi'])}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--split",
        default=GATES.walkforward_split,
        help="train/validation split (production default)",
    )
    ap.add_argument(
        "--confirm-start",
        default=fr.DEFAULT_CONFIRM_START,
        help="untouched confirmation window start (predeclared)",
    )
    ap.add_argument(
        "--top-leagues",
        type=int,
        default=fr.TOP_LEAGUES,
        help="league dimension size (ranked by TRAIN rows only)",
    )
    ap.add_argument("--warehouse", default=str(WAREHOUSE))
    ap.add_argument("--out-json", default=str(ROOT / "localdata" / "ml_fade_context_scan.json"))
    ap.add_argument("--out-md", default=str(ROOT / "localdata" / "ml_fade_context_scan.md"))
    args = ap.parse_args()
    if not (args.split < args.confirm_start):
        raise SystemExit("--split must precede --confirm-start")

    con = duckdb.connect(args.warehouse, read_only=True)
    rows = load_rows(con)
    span = con.sql(
        f"SELECT min(CAST(date AS VARCHAR)), max(CAST(date AS VARCHAR)) FROM {FADE_VIEW}"
    ).fetchone()
    train_rows = [r for r in rows if r["date"][:10] < args.split]
    top_leagues = fr.select_top_leagues(train_rows, args.top_leagues)
    grid = fr.build_grid(top_leagues)

    results = [grade(rows, c, args.split, args.confirm_start) for c in grid]
    results, removed = fr.dedupe_by_evidence(results)
    by_name = {c.name(): c for c in grid}

    print(
        f"fade rows: {len(rows)} (span {span[0]}..{span[1]}), "
        f"train {len(train_rows)}, top-{args.top_leagues} leagues from train only"
    )
    print(
        f"predeclared grid: {len(grid)} candidates "
        f"({len(fr.THRESHOLDS)} thresholds x {len(grid) // len(fr.THRESHOLDS)} contexts)"
    )

    statuses: dict[str, int] = {}
    by_dim: dict[tuple[str, str], int] = {}
    for res in results:
        statuses[res["status"]] = statuses.get(res["status"], 0) + 1
        key = (res["dim"], res["status"])
        by_dim[key] = by_dim.get(key, 0) + 1

    promising = [r for r in results if is_promising(r)]
    promising.sort(key=lambda r: (-(r["graded"]["valid"]["roi"] or -9), -r["graded"]["valid"]["n"]))
    certified = [r for r in results if r["status"] == "research-certified"]

    # Controls — every control graded with the SAME walk-forward accounting.
    parent_rows = as_parent_rows(rows)
    parent_overall = {
        int(t): fr.grade_rows(parent_rows, fr.Candidate(t), args.split, args.confirm_start)
        for t in fr.THRESHOLDS
    }
    fade_everything = fr.grade_rows(rows, fr.Candidate(0.0), args.split, args.confirm_start)
    per_candidate_controls: dict[str, dict] = {}
    for res in promising[:10]:
        cand = by_name[res["candidate"]]
        uncond = (
            fr.grade_rows(rows, fr.Candidate(0.0, cand.conditions), args.split, args.confirm_start)
            if cand.conditions
            else None
        )
        per_candidate_controls[res["candidate"]] = {
            "unconditional_context": uncond,
            "parent_same_context": fr.grade_rows(parent_rows, cand, args.split, args.confirm_start),
        }
    overall_by_thr = {r["threshold"]: r for r in results if r["dim"] == "overall"}

    controls = {
        "fade_everything": fade_everything,
        "parent_overall": parent_overall,
        "per_candidate": per_candidate_controls,
    }

    # ---------------- machine-readable output ---------------------------
    payload = {
        "generated_at": datetime.now(UTC).date().isoformat(),
        "question": "do profitable conditional ml-fade slices exist?",
        "split": args.split,
        "confirm_start": args.confirm_start,
        "warehouse": str(args.warehouse),
        "fade_rows": len(rows),
        "span": list(span),
        "train_rows": len(train_rows),
        "top_leagues_train_only": top_leagues,
        "grid_dimensions": list(fr.GRID_DIMENSIONS),
        "candidate_count": len(grid),
        "status_counts": statuses,
        "production_gates": {
            "min_n_train": GATES.min_n_train,
            "min_n_valid": GATES.min_n_valid,
            "min_roi_train": GATES.min_roi_train,
            "min_roi_valid": GATES.min_roi_valid,
            "wilson_lb": 0.5,
        },
        "research_tightening": {
            "min_valid_days": fr.MIN_VALID_DAYS,
            "confirm_min_n": fr.CONFIRM_MIN_N,
            "train_half_min_n": fr.TRAIN_HALF_MIN_N,
        },
        "realistic_price_haircut": BEST_ODDS_HAIRCUT,
        "promising_report_threshold_valid_n": PROMISING_MIN_VALID_N,
        "results": results,
        "deduped_away": removed,
        "controls": controls,
    }
    Path(args.out_json).write_text(json.dumps(payload, indent=2, default=str))

    # ---------------- human-readable report -----------------------------
    md: list[str] = []
    md.append("# Conditional ml-fade slice scan (research, read-only)\n")
    md.append(
        f"- generated: {payload['generated_at']}  |  split: `{args.split}` "
        f"| confirmation (untouched): `>= {args.confirm_start}`"
    )
    md.append(
        f"- warehouse span: {span[0]} → {span[1]}, fade rows: {len(rows)} (train {len(train_rows)})"
    )
    md.append(
        f"- candidates searched: **{len(grid)}** across dimensions "
        f"`{', '.join(fr.GRID_DIMENSIONS)}` (top-{args.top_leagues} leagues "
        f"ranked by TRAIN rows only)"
    )
    md.append(
        f"- realistic ROI = raw × {BEST_ODDS_HAIRCUT} (BEST_ODDS_HAIRCUT); "
        f"ROI over priced rows, flat 1u at the fade's own opposing-side odds\n"
    )

    md.append("## Verdict\n")
    md.append(
        "- classification counts: " + ", ".join(f"**{k}** {v}" for k, v in sorted(statuses.items()))
    )
    if certified:
        md.append(
            f"- **{len(certified)} research-certified** — still exploratory "
            "until re-mined through the production path (this scan certifies nothing)"
        )
    else:
        md.append(
            "- **no candidate is research-certified.** Nothing is promoted; "
            "the live rule set is unchanged."
        )
    md.append("")

    md.append("## Aggregate baselines (the family to beat)\n")
    md.append(
        "| rule | dim | train n/p roi | valid n/p roi (days, wilson lb) "
        "| confirm n/p roi | realistic valid roi | class |"
    )
    md.append("|---|---|---|---|---|---|---|")
    for res in results:
        if res["dim"] == "overall":
            md.append(_row_md(res, extra_class="baseline"))
    md.append("")
    md.append("ml-meta parent (same thresholds, backed side at its own odds):\n")
    md.append("| parent thr | train roi | valid roi | confirm roi |")
    md.append("|---|---|---|---|")
    for thr in fr.THRESHOLDS:
        md.append(f"| avg_p>={int(thr)} | {_roi_row(parent_overall[int(thr)])} |")
    md.append(
        f"\nFade-EVERYTHING market baseline (thr 0): "
        f"train {_roi(fade_everything['train']['roi'])} "
        f"(n {fade_everything['train']['n']}), "
        f"valid {_roi(fade_everything['valid']['roi'])}, "
        f"confirm {_roi(fade_everything['confirm']['roi'])}\n"
    )

    md.append(f"## Top slices by untouched validation ROI (valid n ≥ {PROMISING_MIN_VALID_N})\n")
    md.append(
        "| candidate | dim | train n/p roi | valid n/p roi (days, lb) "
        "| confirm n/p roi | realistic valid roi | class |"
    )
    md.append("|---|---|---|---|---|---|---|")
    ranked = [r for r in results if r["graded"]["valid"]["n"] >= PROMISING_MIN_VALID_N]
    ranked.sort(key=lambda r: (-(r["graded"]["valid"]["roi"] or -9), -r["graded"]["valid"]["n"]))
    for res in ranked[:20]:
        md.append(_row_md(res))
    md.append("")
    md.append("## Status x dimension (nothing hidden — full JSON has every row)\n")
    md.append("| dimension | " + " | ".join(sorted(statuses)) + " |")
    md.append("|---|" + "---|" * len(statuses))
    for dim in fr.GRID_DIMENSIONS:
        cells = [str(by_dim.get((dim, s), 0)) for s in sorted(statuses)]
        md.append(f"| {dim} | " + " | ".join(cells) + " |")
    md.append("")
    if removed:
        md.append("## Deduped equivalent variants (production-gate passers only)\n")
        for r in removed:
            md.append(f"- `{r['candidate']}` ≡ `{r['deduped_into']}`")
        md.append("")
    if promising:
        md.append("## Controls for promising slices\n")
        md.append("| candidate | ctrl | train roi | valid roi | confirm roi |")
        md.append("|---|---|---|---|---|")
        for res in promising[:10]:
            per = per_candidate_controls.get(res["candidate"], {})
            overall_res = overall_by_thr.get(res["threshold"])
            md.append(f"| {res['candidate']} | slice (faded) | " + _roi_row(res["graded"]) + " |")
            md.append(
                f"| {res['candidate']} | context, no threshold (faded) | "
                + _roi_row(per.get("unconditional_context"))
                + " |"
            )
            md.append(
                f"| {res['candidate']} | parent same context (not faded) | "
                + _roi_row(per.get("parent_same_context"))
                + " |"
            )
            md.append(
                f"| {res['candidate']} | overall ml-fade same thr | "
                + _roi_row(overall_res["graded"] if overall_res else None)
                + " |"
            )
            md.append(
                f"| {res['candidate']} | parent overall same thr | "
                + _roi_row(parent_overall[int(res["threshold"])])
                + " |"
            )
        md.append("")
    md.append("## Method notes\n")
    md.append(
        "- grid, gates and promotion bar: `src/edgefactory/fade_research.py` "
        f"(research tightening: valid days ≥ {fr.MIN_VALID_DAYS}, "
        f"confirm n ≥ {fr.CONFIRM_MIN_N} with roi ≥ 0, "
        "non-negative ROI in both chronological train halves)"
    )
    md.append(
        "- conditions reference pre-kickoff fields only "
        "(ml_p, fade side, fade's own odds, league/date-derived context); "
        "outcome is used solely to grade, exactly like mine_consensus"
    )
    md.append(
        f"- with {len(grid)} candidates tested, α-level luck is expected "
        "(a handful of false positives at p=0.01 under the null); only "
        "persistence across validation AND the untouched confirmation "
        "window separates a real slice from noise — see classes above"
    )
    md.append("- every searched candidate is in ml_fade_context_scan.json; nothing failed silently")
    Path(args.out_md).write_text("\n".join(md) + "\n")
    print(f"wrote {args.out_json} and {args.out_md}")
    print("verdict:", ", ".join(f"{k}={v}" for k, v in sorted(statuses.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
