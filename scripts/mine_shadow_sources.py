#!/usr/bin/env python3
"""mine_shadow_sources.py — Dynamic retrospective mining of shadow sources (PredictZ, Windrawwin).

Analyzes historical performance inside warehouse.duckdb to identify
niche segments where shadow sources produce highly profitable signals.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb
from edgefactory.entities import classify_competition
from edgefactory.util import fold_ascii

DB_PATH = ROOT / "localdata" / "warehouse.duckdb"
OUT_PATH = ROOT / "localdata" / "shadow_mining_report.json"


def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False


def analyze_shadow_source(con, table_name: str, source_label: str) -> dict:
    if not _table_exists(con, table_name):
        return {"status": "skipped", "reason": f"table '{table_name}' does not exist"}

    print(f"\nAnalyzing historical shadow source: {source_label} ({table_name})")
    print("=" * 60)

    # 1. Overall Performance
    q_overall = f"""
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN pick = outcome THEN 1 ELSE 0 END) AS wins,
               AVG(pick_odds) AS avg_odds,
               SUM(CASE WHEN pick_odds IS NOT NULL THEN
                     CASE WHEN pick = outcome THEN pick_odds - 1 ELSE -1 END
                   ELSE 0 END) AS pnl,
               SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) AS priced_n
        FROM {table_name}
    """
    row = con.execute(q_overall).fetchone()
    total, wins, avg_odds, pnl, priced_n = row
    total, wins, priced_n = int(total or 0), int(wins or 0), int(priced_n or 0)
    hit_rate = wins / total if total else 0.0
    roi = pnl / priced_n if priced_n else 0.0

    print(f"Overall Metrics:")
    print(f"  Total Rows : {total:,}")
    print(f"  Hit Rate   : {hit_rate:.1%}")
    print(f"  Avg Odds   : {avg_odds:.2f}" if avg_odds else "  Avg Odds   : n/a")
    print(f"  Realized ROI: {roi:+.1%}" if priced_n else "  Realized ROI: n/a")

    # 2. Performance by Selection (Home/Away/Draw splits)
    q_sel = f"""
        SELECT pick,
               COUNT(*) AS total,
               SUM(CASE WHEN pick = outcome THEN 1 ELSE 0 END) AS wins,
               SUM(CASE WHEN pick_odds IS NOT NULL THEN
                     CASE WHEN pick = outcome THEN pick_odds - 1 ELSE -1 END
                   ELSE 0 END) AS pnl,
               SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) AS priced_n
        FROM {table_name}
        GROUP BY pick
        ORDER BY total DESC
    """
    selection_splits = []
    print(f"\nSelection splits:")
    for pick, t, w, p, pn in con.execute(q_sel).fetchall():
        t, w, pn = int(t or 0), int(w or 0), int(pn or 0)
        h = w / t if t else 0.0
        r = p / pn if pn else 0.0
        print(f"  {pick:10s} : n={t:5d}  hit={h:.1%}  ROI={r:+.1%}")
        selection_splits.append({"selection": pick, "total": t, "wins": w, "roi": r})

    # 3. Performance by Competition Type
    # Run the classification function dynamically on the rows
    q_all_rows = f"SELECT league, pick, outcome, pick_odds FROM {table_name}"
    comp_groups = {}
    for league, pick, outcome, pick_odds in con.execute(q_all_rows).fetchall():
        comp_type = classify_competition(league)
        comp_groups.setdefault(comp_type, []).append((pick, outcome, pick_odds))

    comp_splits = []
    print(f"\nCompetition-Type splits (classified dynamically):")
    for comp, rows in sorted(comp_groups.items()):
        t = len(rows)
        w = sum(1 for r in rows if r[0] == r[1])
        priced_rows = [r for r in rows if r[2] is not None]
        pn = len(priced_rows)
        p = sum((r[2] - 1) if r[0] == r[1] else -1 for r in priced_rows)
        h = w / t if t else 0.0
        r = p / pn if pn else 0.0
        print(f"  {comp:12s} : n={t:5d}  hit={h:.1%}  ROI={r:+.1%}")
        comp_splits.append({"competition_type": comp, "total": t, "wins": w, "roi": r})

    return {
        "status": "mined",
        "total": total,
        "hit_rate": hit_rate,
        "roi": roi,
        "selection_splits": selection_splits,
        "competition_splits": comp_splits,
    }


def main():
    if not DB_PATH.exists():
        print("Warehouse does not exist, exiting research utility gracefully.", file=sys.stderr)
        return

    con = duckdb.connect(str(DB_PATH), read_only=True)
    con.create_function("classify_competition", classify_competition)

    results = {}
    results["predictz"] = analyze_shadow_source(con, "predictz_settled", "PredictZ")
    results["windrawwin"] = analyze_shadow_source(con, "windrawwin_settled", "Windrawwin")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"\nRetrospective shadow source analysis written to -> {OUT_PATH}")


if __name__ == "__main__":
    main()
