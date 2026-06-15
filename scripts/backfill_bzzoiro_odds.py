#!/usr/bin/env python3
"""Force/retry bzzoiro_odds cache backfill for a date range.

This is a data-job helper only: it writes localdata/bzzoiro_odds_YYYY-MM.csv.gz
and localdata/state_bzzoiro_odds.json through the existing local_backfill.py
path. It does not touch git, the warehouse, edge certification, or Supabase.

Use this after adapter/parser fixes because earlier zero-row captures may have
marked dates as done in state.

Examples:
    PYTHONPATH=src python scripts/backfill_bzzoiro_odds.py 2026-06-01 2026-06-16 --max-seconds 3600
    PYTHONPATH=src python scripts/backfill_bzzoiro_odds.py 2026-06-15 2026-06-16 --no-reset-state
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
STATE = LOCALDATA / "state_bzzoiro_odds.json"


def dates_between(start_s: str, end_s: str) -> list[str]:
    start = date.fromisoformat(start_s)
    end = date.fromisoformat(end_s)
    if end < start:
        raise ValueError("end date must be >= start date")
    out = []
    d = start
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def reset_state_file(path: Path, dates: set[str]) -> int:
    """Remove dates from local_backfill state. Returns number removed."""
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text())
    except Exception:
        return 0
    done = list(data.get("done", []))
    kept = [d for d in done if d not in dates]
    data["done"] = kept
    path.write_text(json.dumps(data))
    return len(done) - len(kept)


def summarize_cache(start_s: str, end_s: str) -> dict[str, int]:
    wanted = set(dates_between(start_s, end_s))
    counts = {d: 0 for d in sorted(wanted)}
    for path in sorted(LOCALDATA.glob("bzzoiro_odds_*.csv.gz")):
        try:
            with gzip.open(path, "rt", newline="") as fh:
                for row in csv.DictReader(fh):
                    day = row.get("date")
                    if day in wanted:
                        counts[day] += 1
        except Exception:
            continue
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Force/retry bzzoiro_odds cache backfill")
    ap.add_argument("start", help="YYYY-MM-DD")
    ap.add_argument("end", help="YYYY-MM-DD")
    ap.add_argument("--max-seconds", type=int, default=3600)
    ap.add_argument("--no-reset-state", action="store_true", help="do not remove range from state before fetching")
    args = ap.parse_args()

    LOCALDATA.mkdir(exist_ok=True)
    days = set(dates_between(args.start, args.end))
    if not args.no_reset_state:
        removed = reset_state_file(STATE, days)
        print(f"bzzoiro_odds state reset: removed {removed} done day(s) from {STATE}")

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "local_backfill.py"),
        "bzzoiro_odds",
        args.start,
        args.end,
        "--max-seconds",
        str(args.max_seconds),
        "--workers",
        "1",
    ]
    print("running:", " ".join(cmd))
    rc = subprocess.run(cmd, cwd=ROOT).returncode

    counts = summarize_cache(args.start, args.end)
    total = sum(counts.values())
    print("bzzoiro_odds cache summary:")
    for day, n in counts.items():
        print(f"  {day}: {n} rows")
    print(f"total rows in range: {total}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
