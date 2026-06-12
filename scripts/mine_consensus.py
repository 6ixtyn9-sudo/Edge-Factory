#!/usr/bin/env python3
"""Walk-forward consensus miner on the DuckDB warehouse.

Re-validates the certified rules and scans the threshold grid, all with the
standard gates (no mini-backtests, Wilson LB, ROI alongside hit rate).

    python3 scripts/mine_consensus.py --split 2025-06-01
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb  # noqa: E402

from edgefactory.assay import wilson_lb  # noqa: E402
from edgefactory.config import GATES  # noqa: E402

DB = ROOT / "localdata" / "warehouse.duckdb"
OUT = ROOT / "localdata" / "edges_consensus.json"


def stats(con, view, where, split, period):
    cmp = "<" if period == "train" else ">="
    q = f"""
        SELECT count(*) n,
               sum(CASE WHEN fb_pick = outcome THEN 1 ELSE 0 END) wins,
               avg(pick_odds) avg_odds,
               sum(CASE WHEN pick_odds IS NOT NULL THEN
                     CASE WHEN fb_pick = outcome THEN pick_odds - 1 ELSE -1 END
                   ELSE 0 END) pnl,
               sum(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
        FROM {view} WHERE ({where}) AND date {cmp} '{split}'
    """
    n, wins, avg_odds, pnl, n_priced = con.sql(q).fetchone()
    n, wins = int(n or 0), int(wins or 0)
    hit = wins / n if n else 0.0
    roi = (pnl / n_priced) if n_priced else None
    return {
        "n": n, "wins": wins, "hit": round(hit, 4),
        "wilson_lb": round(wilson_lb(wins, n), 4),
        "avg_odds": round(avg_odds, 3) if avg_odds else None,
        "roi": round(roi, 4) if roi is not None else None,
        "n_priced": int(n_priced or 0),
    }


def evaluate(con, name, view, where, split):
    tr = stats(con, view, where, split, "train")
    va = stats(con, view, where, split, "valid")
    certified = (
        tr["n"] >= GATES.min_n_train
        and va["n"] >= GATES.min_n_valid
        and (tr["roi"] is None or tr["roi"] >= GATES.min_roi_train)
        and (va["roi"] is None or va["roi"] >= GATES.min_roi_valid)
        and va["wilson_lb"] >= 0.5
    )
    return {"rule": name, "view": view, "where": where,
            "train": tr, "valid": va,
            "status": "certified" if certified else "candidate"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default=GATES.walkforward_split)
    args = ap.parse_args()

    con = duckdb.connect(str(DB), read_only=True)
    results = []

    # --- 2-way unanimous grid ---
    for thr in (60, 65, 70, 75, 80):
        results.append(evaluate(
            con, f"2way-unanimous avg_p>={thr}", "consensus2",
            f"fb_pick = zb_pick AND avg_p >= {thr}", args.split))

    # --- 3-way unanimous grid ---
    for thr in (60, 65, 70, 75):
        results.append(evaluate(
            con, f"3way-unanimous avg_p>={thr}", "consensus3",
            f"fb_pick = zb_pick AND zb_pick = sa_pick AND avg_p >= {thr}",
            args.split))

    # --- veto sanity: disagreement = poison (expect ~33-40%) ---
    results.append(evaluate(
        con, "VETO-CHECK disagree, follow forebet", "consensus2",
        "fb_pick != zb_pick", args.split))

    # --- non-draw filters (draws never work) ---
    for thr in (65, 70):
        results.append(evaluate(
            con, f"2way-unanimous no-draw avg_p>={thr}", "consensus2",
            f"fb_pick = zb_pick AND fb_pick != 'draw' AND avg_p >= {thr}",
            args.split))

    hdr = f"{'rule':42s} {'TRAIN n/hit/LB/roi':>26s}   {'VALID n/hit/LB/roi':>26s}  status"
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        t, v = r["train"], r["valid"]

        def fmt(s):
            roi = f"{s['roi']:+.1%}" if s["roi"] is not None else "  n/a"
            return f"{s['n']:>6d} {s['hit']:.1%} {s['wilson_lb']:.3f} {roi}"

        flag = "🏆" if r["status"] == "certified" else "  "
        print(f"{r['rule']:42s} {fmt(t):>26s}   {fmt(v):>26s}  {flag} {r['status']}")

    OUT.write_text(json.dumps(
        {"split": args.split, "gates": vars(GATES), "edges": results}, indent=2))
    print(f"\nwritten -> {OUT}")


if __name__ == "__main__":
    main()
