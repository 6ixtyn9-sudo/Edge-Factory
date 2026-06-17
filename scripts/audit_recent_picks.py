#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
WAREHOUSE = LOCALDATA / "warehouse.duckdb"

import sys
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.util import norm_team  # noqa: E402


@dataclass
class SettledPick:
    date: str
    rule_name: str
    bucket: str
    odds_source: str
    odds_match_method: str
    market: str
    pick: str
    outcome: str
    won: bool
    odds: float | None
    pnl: float | None


def daterange(start: str, end: str):
    d = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    while d <= e:
        yield d.isoformat()
        d += timedelta(days=1)


def archived_picks_path(day: str) -> Path:
    return LOCALDATA / f"picks_{day}.json"


def load_archived_picks(start: str, end: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for day in daterange(start, end):
        path = archived_picks_path(day)
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for row in data:
            if isinstance(row, dict):
                row = dict(row)
                row.setdefault("date", day)
                out.append(row)
    return out


def load_results_index(warehouse_path: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    import duckdb

    if not warehouse_path.exists():
        raise FileNotFoundError(f"warehouse not found: {warehouse_path}")

    con = duckdb.connect(str(warehouse_path), read_only=True)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    candidates = [
        (1, "forebet_settled"),
        (2, "bettingclosed_settled"),
        (3, "zulubet_settled"),
        (4, "statarea_settled"),
        (5, "scoutingstats_settled"),
        (6, "vitibet_settled"),
    ]
    active = [(prio, name) for prio, name in candidates if name in tables]
    if not active:
        return {}

    union_sql = " UNION ALL ".join(
        f"SELECT {prio} AS prio, date, hkey, akey, hs, gs, outcome FROM {name} WHERE hs IS NOT NULL AND gs IS NOT NULL"
        for prio, name in active
    )
    sql = f"""
        WITH all_results AS (
            {union_sql}
        ), ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY date, hkey, akey ORDER BY prio) AS rn
            FROM all_results
        )
        SELECT date, hkey, akey, hs, gs, outcome
        FROM ranked
        WHERE rn = 1
    """
    rows = con.execute(sql).fetchall()
    return {
        (str(day)[:10], str(hkey), str(akey)): {
            "hs": int(hs),
            "gs": int(gs),
            "outcome": str(outcome),
        }
        for day, hkey, akey, hs, gs, outcome in rows
    }


def settle_pick(pick: dict[str, Any], result: dict[str, Any] | None) -> SettledPick | None:
    if not result:
        return None
    market = str(pick.get("market") or "")
    selection = str(pick.get("pick") or "")
    outcome = str(result.get("outcome") or "")
    if market != "1x2":
        return None
    if selection not in {"home", "draw", "away"}:
        return None
    won = selection == outcome
    odds_value = pick.get("odds")
    try:
        odds = float(odds_value) if odds_value not in (None, "") else None
    except (TypeError, ValueError):
        odds = None
    pnl = None if odds is None else (odds - 1.0 if won else -1.0)
    return SettledPick(
        date=str(pick.get("date") or "")[:10],
        rule_name=str(pick.get("edge_rule") or pick.get("rule") or pick.get("display_rule") or "UNKNOWN"),
        bucket=str(pick.get("bucket") or "UNKNOWN"),
        odds_source=str(pick.get("odds_source") or "UNKNOWN"),
        odds_match_method=str(pick.get("odds_match_method") or "UNKNOWN"),
        market=market,
        pick=selection,
        outcome=outcome,
        won=won,
        odds=odds,
        pnl=pnl,
    )


def summarize_scored(rows: list[SettledPick]) -> dict[str, Any]:
    settled = len(rows)
    wins = sum(1 for row in rows if row.won)
    with_odds = [row for row in rows if row.pnl is not None]
    pnl_sum = sum(float(row.pnl or 0.0) for row in with_odds)
    return {
        "settled_picks": settled,
        "wins": wins,
        "hit_rate": round(wins / settled, 6) if settled else None,
        "priced_picks": len(with_odds),
        "roi": round(pnl_sum / len(with_odds), 6) if with_odds else None,
    }


def summarize_by(rows: list[SettledPick], attr: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[SettledPick]] = defaultdict(list)
    for row in rows:
        grouped[str(getattr(row, attr) or "UNKNOWN")].append(row)
    return {name: summarize_scored(group_rows) for name, group_rows in sorted(grouped.items())}


def build_report(start: str, end: str, warehouse_path: Path) -> dict[str, Any]:
    picks = load_archived_picks(start, end)
    results = load_results_index(warehouse_path)
    settled_rows: list[SettledPick] = []
    archived_dates = sorted({str(p.get("date") or "")[:10] for p in picks if p.get("date")})

    for pick in picks:
        key = (
            str(pick.get("date") or "")[:10],
            norm_team(str(pick.get("home") or "")),
            norm_team(str(pick.get("away") or "")),
        )
        settled = settle_pick(pick, results.get(key))
        if settled is not None:
            settled_rows.append(settled)

    return {
        "start": start,
        "end": end,
        "archived_pick_rows": len(picks),
        "archived_pick_dates": archived_dates,
        "overall": summarize_scored(settled_rows),
        "by_rule": summarize_by(settled_rows, "rule_name"),
        "by_bucket": summarize_by(settled_rows, "bucket"),
        "by_odds_source": summarize_by(settled_rows, "odds_source"),
        "by_odds_match_method": summarize_by(settled_rows, "odds_match_method"),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    overall = report.get("overall", {})
    lines = [
        f"# Edge Factory — Recent picks audit ({report['start']} to {report['end']})",
        "",
        "## Overall",
        "",
        f"- archived pick rows: {report.get('archived_pick_rows', 0)}",
        f"- archived pick dates: {len(report.get('archived_pick_dates', []))}",
        f"- settled picks: {overall.get('settled_picks', 0)}",
        f"- wins: {overall.get('wins', 0)}",
        f"- hit rate: {overall.get('hit_rate')}",
        f"- priced picks: {overall.get('priced_picks', 0)}",
        f"- ROI: {overall.get('roi')}",
        "",
        "## By rule",
        "",
    ]
    by_rule = report.get("by_rule", {})
    if not by_rule:
        lines.append("- none")
    else:
        for key, summary in by_rule.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By bucket", ""])
    by_bucket = report.get("by_bucket", {})
    if not by_bucket:
        lines.append("- none")
    else:
        for key, summary in by_bucket.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By odds source", ""])
    by_source = report.get("by_odds_source", {})
    if not by_source:
        lines.append("- none")
    else:
        for key, summary in by_source.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By odds match method", ""])
    by_method = report.get("by_odds_match_method", {})
    if not by_method:
        lines.append("- none")
    else:
        for key, summary in by_method.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit recent archived daily picks against settled warehouse results.")
    ap.add_argument("--end", default=date.today().isoformat(), help="End date inclusive (YYYY-MM-DD).")
    ap.add_argument("--days", type=int, default=30, help="Rolling window length in days (default: 30).")
    ap.add_argument("--warehouse", default=str(WAREHOUSE), help="Path to warehouse.duckdb")
    args = ap.parse_args()

    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    start = (end - timedelta(days=max(0, args.days - 1))).isoformat()
    report = build_report(start, end.isoformat(), Path(args.warehouse))

    json_path = LOCALDATA / "picks_audit_rolling.json"
    md_path = LOCALDATA / f"picks_audit_{end.isoformat()}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    write_markdown(md_path, report)

    overall = report.get("overall", {})
    print(f"Recent picks audit — {start} to {end.isoformat()}")
    print(f"  archived pick rows: {report.get('archived_pick_rows', 0)}")
    print(f"  archived pick dates: {len(report.get('archived_pick_dates', []))}")
    print(f"  settled picks: {overall.get('settled_picks', 0)}")
    print(f"  hit rate: {overall.get('hit_rate')}")
    print(f"  ROI: {overall.get('roi')}")
    print(f"  json: {json_path}")
    print(f"  markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
