#!/usr/bin/env python3
"""export_settled_results.py — share settled match facts across machines.

Why (Addendum 21, 2026-08-04): warehouses are machine-local (CI cache on
GitHub Actions / disk on the laptop). audit_recent_picks can only settle a
pick whose score row THE SAME MACHINE captured, so cloud and laptop audits
diverge on thin-coverage leagues. Receipt: NPL Tasmania — "South Hobart vs
Ulverstone" 2026-07-11 and "Clarence Zebras vs Ulverstone" 2026-08-02 settled
fine on the Mac but were "unmatched_result" in the cloud audit, because the
cloud warehouse never captured those rows. Settled scores are FACTS, not
memory: this script exports a compact rolling window that the bot persists to
git, and the audit settles from warehouse ∪ overlay.

Reads:  localdata/warehouse.duckdb (the six *_settled views only)
Writes: localdata/settled_results.json — atomic (tmp + replace). Each export
        UNIONS the inbound shared file (rows other machines contributed,
        delivered by git) with this machine's warehouse rows — dedup by
        normalized pair, warehouse wins on conflict, stale inbound dropped —
        so the shared file converges to the union of BOTH machines' memories
        no matter which machine ran last (Addendum 21 convergence loop).
        Bot-owned via the .gitignore negation; humans never hand-edit it.

Usage:
    PYTHONPATH=src python3 scripts/export_settled_results.py             # export
    PYTHONPATH=src python3 scripts/export_settled_results.py --self-test # offline
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA") or (REPO / "localdata"))
WINDOW_DAYS = int(os.environ.get("SETTLED_OVERLAY_DAYS", "90") or 90)
OUT_FILE = LOCALDATA / "settled_results.json"

# Same settled views and priority order as audit_recent_picks.load_results_index.
SETTLED_SOURCES = [
    (1, "forebet_settled"),
    (2, "bettingclosed_settled"),
    (3, "zulubet_settled"),
    (4, "statarea_settled"),
    (5, "scoutingstats_settled"),
    (6, "vitibet_settled"),
]


def build_overlay_rows(con, window_start: str) -> list[dict]:
    """Priority-deduped settled rows on/after window_start (facts only)."""
    from edgefactory.util import norm_team_sql

    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    active = [(prio, name) for prio, name in SETTLED_SOURCES if name in tables]
    if not active:
        return []
    nh, na = norm_team_sql("home", 14), norm_team_sql("away", 14)
    union_sql = " UNION ALL ".join(
        f"SELECT {prio} AS prio, '{name}' AS src, date, home, away, "
        f"{nh} AS hk, {na} AS ak, hs, gs, outcome FROM {name} "
        "WHERE hs IS NOT NULL AND gs IS NOT NULL "
        f"AND substr(CAST(date AS VARCHAR), 1, 10) >= '{window_start}'"
        for prio, name in active
    )
    sql = (
        f"WITH allr AS ({union_sql}), ranked AS ("
        " SELECT *, ROW_NUMBER() OVER ("
        "   PARTITION BY substr(CAST(date AS VARCHAR), 1, 10), hk, ak"
        "   ORDER BY prio) AS rn FROM allr)"
        " SELECT substr(CAST(date AS VARCHAR), 1, 10) AS day, home, away,"
        "        hs, gs, outcome, src"
        " FROM ranked WHERE rn = 1 ORDER BY day, home, away"
    )
    return [
        {
            "date": str(day),
            "home": str(home),
            "away": str(away),
            "hs": int(hs),
            "gs": int(gs),
            "outcome": str(outcome),
            "src": str(src),
        }
        for day, home, away, hs, gs, outcome, src in con.execute(sql).fetchall()
    ]


def load_inbound_rows(path: Path) -> list[dict]:
    """Rows from the shared overlay file as pulled from git — other machines'
    memory. Malformed/missing files degrade to 'no inbound rows'."""
    try:
        payload = json.loads(path.read_text())
        rows = payload.get("rows") or []
    except Exception:
        return []
    out = []
    for r in rows:
        try:
            out.append(
                {
                    "date": str(r["date"])[:10],
                    "home": str(r["home"]),
                    "away": str(r["away"]),
                    "hs": int(r["hs"]),
                    "gs": int(r["gs"]),
                    "outcome": str(r["outcome"]),
                    "src": str(r.get("src") or "overlay"),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
    return out


def merge_overlay_rows(warehouse_rows: list[dict], inbound_rows: list[dict], window_start: str) -> tuple[list[dict], int]:
    """Union with dedup by (date, norm14 pair). Warehouse wins on conflict —
    this machine's freshest memory outranks the last shared snapshot. Inbound
    rows outside the rolling window are dropped (keeps the shared file
    bounded). Returns (rows, n_carried_from_inbound_only)."""
    from edgefactory.util import norm_team

    def key(r: dict) -> tuple:
        return (r["date"], norm_team(r["home"], 14), norm_team(r["away"], 14))

    merged: dict[tuple, dict] = {}
    inbound_only: set[tuple] = set()
    for r in inbound_rows:
        if r["date"] < window_start:
            continue
        k = key(r)
        merged[k] = r
        inbound_only.add(k)
    for r in warehouse_rows:
        k = key(r)
        merged[k] = r
        inbound_only.discard(k)
    rows = sorted(merged.values(), key=lambda x: (x["date"], x["home"], x["away"]))
    return rows, len(inbound_only)


def self_test() -> int:
    import duckdb

    con = duckdb.connect(":memory:")
    ddl = "(date VARCHAR, home VARCHAR, away VARCHAR, hs INTEGER, gs INTEGER, outcome VARCHAR)"
    con.execute(f"CREATE TABLE forebet_settled {ddl}")
    con.execute(f"CREATE TABLE zulubet_settled {ddl}")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-08-02','South Hobart','Ulverstone',2,0,'home')")
    con.execute("INSERT INTO zulubet_settled  VALUES ('2026-08-02','South Hobart','Ulverstone',9,9,'away')")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-01-01','Old','Club',1,0,'home')")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-08-03','Null','Score',NULL,NULL,NULL)")
    rows = build_overlay_rows(con, "2026-07-01")
    ok = (
        len(rows) == 1
        and rows[0]["src"] == "forebet_settled"
        and rows[0]["hs"] == 2
        and rows[0]["date"] == "2026-08-02"
    )
    inbound = [
        # conflict with a warehouse row -> warehouse must win
        {"date": "2026-08-02", "home": "South Hobart", "away": "Ulverstone", "hs": 9, "gs": 9, "outcome": "away", "src": "zulubet_settled"},
        # inbound-only row -> must be carried forward
        {"date": "2026-08-02", "home": "Hobart Zebras", "away": "Ulverstone", "hs": 1, "gs": 0, "outcome": "home", "src": "forebet_settled"},
        # outside the rolling window -> must be dropped
        {"date": "2026-01-02", "home": "Too", "away": "Old", "hs": 0, "gs": 0, "outcome": "draw", "src": "overlay"},
    ]
    merged, carried = merge_overlay_rows(rows, inbound, "2026-07-01")
    ok = ok and len(merged) == 2 and carried == 1
    ok = ok and any(r["home"] == "Hobart Zebras" for r in merged)
    ok = ok and all(r["hs"] != 9 for r in merged)
    print(f"export_settled_results self-test: rows={len(merged)} carried={carried} ok={ok}")
    return 0 if ok else 1


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    wh = LOCALDATA / "warehouse.duckdb"
    if not wh.exists():
        print(f"warehouse not found: {wh} (nothing to export)", file=sys.stderr)
        return 2
    import duckdb

    con = duckdb.connect(str(wh), read_only=True)
    window_start = (date.today() - timedelta(days=WINDOW_DAYS)).isoformat()
    wh_rows = build_overlay_rows(con, window_start)
    con.close()
    # Convergence loop: carry other machines' facts forward (inbound file came
    # down via git pull), then this machine's freshest memory overwrites dupes.
    inbound = load_inbound_rows(OUT_FILE)
    rows, carried = merge_overlay_rows(wh_rows, inbound, window_start)
    payload = {
        "schema": 1,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "window_days": WINDOW_DAYS,
        "rows": rows,
    }
    LOCALDATA.mkdir(parents=True, exist_ok=True)
    tmp = OUT_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=1) + "\n")
    tmp.replace(OUT_FILE)
    print(
        f"settled overlay exported: {len(rows)} rows (>= {window_start}; "
        f"{len(wh_rows)} from this warehouse + {carried} carried from shared file) -> {OUT_FILE}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
