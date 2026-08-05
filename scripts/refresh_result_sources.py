#!/usr/bin/env python3
"""Refresh final-score rows from existing result-capable source adapters.

This is intentionally narrower than capture_daily: it re-reads only one
already-completed calendar date from known result donors, preserves existing
prediction fields, and updates only final-score or positive terminal-event
status fields. It is used by
the autonomous intraday path before backfill_results/build_warehouse/export so
late-finishing matches become auditable on the next cadence without a D30
full-capture sweep.

Examples:
    PYTHONPATH=src python3 scripts/refresh_result_sources.py --date 2026-08-04
    PYTHONPATH=src python3 scripts/refresh_result_sources.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import gzip
import importlib
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
RESULT_SOURCES = (
    "forebet",
    "zulubet",
    "statarea",
    "vitibet",
    "scoutingstats",
    "bettingclosed",
)
SCORE_FIELDS = ("hs", "gs", "ht_hs", "ht_gs")

sys.path.insert(0, str(ROOT / "src"))
from edgefactory.settlement import terminal_event_disposition  # noqa: E402
from edgefactory.util import compact_key  # noqa: E402


def _has_value(value: object) -> bool:
    return value not in (None, "")


def has_final_score(row: dict[str, Any]) -> bool:
    """A score is usable only when both sides parse as non-negative integers."""
    try:
        return int(row.get("hs")) >= 0 and int(row.get("gs")) >= 0
    except (TypeError, ValueError):
        return False


def row_key(row: dict[str, Any]) -> tuple[str, str, str]:
    """Strict source-row identity. Do not use legacy nine-character miner keys
    here: a result refresher must never merge different source fixtures."""
    return (
        str(row.get("date") or "")[:10],
        compact_key(row.get("home")),
        compact_key(row.get("away")),
    )


def read_rows(path: Path) -> tuple[list[str], dict[tuple[str, str, str], dict[str, str]]]:
    if not path.exists():
        return [], {}
    try:
        with gzip.open(path, "rt", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = list(reader.fieldnames or [])
            rows = {
                row_key(row): dict(row)
                for row in reader
                if row_key(row) != ("", "", "")
            }
            return columns, rows
    except Exception:
        return [], {}


def has_terminal_event_status(row: dict[str, Any]) -> bool:
    return terminal_event_disposition(row.get("status")) is not None


def merge_terminal_update(existing: dict[str, str], fresh: dict[str, Any]) -> tuple[dict[str, str], bool]:
    """Preserve pick-time prediction fields while adding a final score or
    positive terminal no-score status.

    ``scheduled``/blank/live statuses do nothing. A terminal event status is
    retained for audit disposition but never masquerades as a score.
    """
    merged = dict(existing)
    scored = has_final_score(fresh)
    terminal = has_terminal_event_status(fresh)
    if not (scored or terminal):
        return merged, False

    changed = False
    if scored:
        for field in SCORE_FIELDS:
            value = fresh.get(field)
            if _has_value(value):
                text = str(value)
                if merged.get(field) != text:
                    merged[field] = text
                    changed = True

    if _has_value(fresh.get("status")):
        text = str(fresh["status"])
        if merged.get("status") != text:
            merged["status"] = text
            changed = True
    return merged, changed


# Compatibility name retained for focused callers/tests.
def merge_final_score(existing: dict[str, str], fresh: dict[str, Any]) -> tuple[dict[str, str], bool]:
    return merge_terminal_update(existing, fresh)


def _write_rows(path: Path, columns: list[str], rows: dict[tuple[str, str, str], dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="", compresslevel=6, encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in sorted(rows.values(), key=lambda item: (item.get("date", ""), item.get("home", ""), item.get("away", ""))):
            writer.writerow({column: row.get(column, "") for column in columns})


def refresh_source(source: str, day: str, *, localdata: Path = LOCALDATA) -> dict[str, Any]:
    """Fetch one completed day and upsert scores or terminal event statuses."""
    try:
        module = importlib.import_module(f"edgefactory.sources.{source}")
        fetched = list(module.fetch_day(day) or [])
    except Exception as exc:  # noqa: BLE001 - report the source class, never abort the batch
        return {"source": source, "status": f"ERROR:{type(exc).__name__}", "raw": 0, "scored": 0, "terminal_status": 0, "new": 0, "updated": 0}

    terminal_rows = [
        row for row in fetched
        if isinstance(row, dict)
        and str(row.get("date") or "")[:10] == day
        and row_key(row) != ("", "", "")
        and (has_final_score(row) or has_terminal_event_status(row))
    ]
    scored_rows = sum(1 for row in terminal_rows if has_final_score(row))
    disposition_rows = sum(1 for row in terminal_rows if not has_final_score(row) and has_terminal_event_status(row))

    path = localdata / f"{source}_{day[:7]}.csv.gz"
    columns, existing = read_rows(path)
    source_columns = list(getattr(module, "COLUMNS", []) or [])
    all_columns = list(dict.fromkeys(columns + source_columns + [key for row in terminal_rows for key in row]))

    new_rows = 0
    updated_rows = 0
    for row in terminal_rows:
        key = row_key(row)
        if key not in existing:
            existing[key] = {column: "" if row.get(column) is None else str(row.get(column, "")) for column in all_columns}
            new_rows += 1
            continue
        merged, changed = merge_terminal_update(existing[key], row)
        existing[key] = merged
        updated_rows += int(changed)

    if terminal_rows and all_columns:
        _write_rows(path, all_columns, existing)

    return {
        "source": source,
        "status": "OK",
        "raw": len(fetched),
        "scored": scored_rows,
        "terminal_status": disposition_rows,
        "new": new_rows,
        "updated": updated_rows,
    }


def self_test() -> int:
    baseline = {
        "date": "2026-08-04", "home": "Carabobo FC", "away": "Trujillanos FC",
        "p1": "0.66", "px": "0.21", "p2": "0.13", "hs": "", "gs": "",
    }
    fresh = {
        "date": "2026-08-04", "home": "Carabobo FC", "away": "Trujillanos FC",
        "p1": None, "px": None, "p2": None, "hs": 2, "gs": 0, "status": "FT",
    }
    merged, changed = merge_final_score(baseline, fresh)
    ok = (
        changed
        and merged["p1"] == "0.66"
        and merged["px"] == "0.21"
        and merged["p2"] == "0.13"
        and merged["hs"] == "2"
        and merged["gs"] == "0"
        and merged["status"] == "FT"
        and has_final_score(fresh)
        and not has_final_score({"hs": "", "gs": "0"})
        and row_key({"date": "2026-08-04", "home": "Carabobo FC", "away": "Trujillanos FC"})
        == row_key({"date": "2026-08-04", "home": "Carabobo FC", "away": "Trujillanos FC"})
    )
    postponed, postponed_changed = merge_terminal_update(
        baseline,
        {"date": "2026-08-04", "home": "Carabobo FC", "away": "Trujillanos FC", "hs": None, "gs": None, "status": "Postp."},
    )
    ok = ok and postponed_changed and postponed["status"] == "Postp." and postponed["p1"] == "0.66"
    ok = ok and has_terminal_event_status({"status": "Postponed"})
    ok = ok and not has_terminal_event_status({"status": "scheduled"})
    print(f"refresh_result_sources self-test: ok={ok}")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh final-score and terminal-status rows from existing result donors.")
    parser.add_argument(
        "--date",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Completed calendar day to refresh (default: yesterday).",
    )
    parser.add_argument(
        "--sources",
        default=",".join(RESULT_SOURCES),
        help="Optional comma-separated result donor keys.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run offline merge test; no source calls.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    try:
        date.fromisoformat(args.date)
    except ValueError:
        parser.error("--date must be YYYY-MM-DD")

    sources = tuple(item.strip() for item in args.sources.split(",") if item.strip())
    failures = 0
    print(f"Result-donor refresh: {args.date}")
    for source in sources:
        receipt = refresh_source(source, args.date)
        print(
            f"{receipt['source']}: status={receipt['status']} raw={receipt['raw']} "
            f"scored={receipt['scored']} terminal_status={receipt['terminal_status']} "
            f"new={receipt['new']} updated={receipt['updated']}"
        )
        failures += not str(receipt["status"]).startswith("OK")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
