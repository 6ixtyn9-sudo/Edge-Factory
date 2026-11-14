#!/usr/bin/env python3
"""Summarize source capture freshness from local CSV.gz state.

This is deliberately local and dashboard-free. It uses exact source filename
patterns (so ``bzzoiro`` never consumes ``bzzoiro_odds``), reports retryable
failure state, and checks whether the latest materialized warehouse contains a
relation for each source.

    PYTHONPATH=src python3 scripts/audit_source_availability.py \
        --date 2026-09-30 --days 30
"""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

DEFAULT_SOURCES = (
    "forebet",
    "prosoccer",
    "soccervista",
    "predictz",
    "windrawwin",
    "scoutingstats",
    "vitibet",
    "zulubet",
    "statarea",
    "bettingclosed",
    "freesupertips",
    "betclan",
    "afootballreport",
    "bzzoiro",
    "bzzoiro_odds",
    "theoddsapi_odds",
    "oddspapi_odds",
)

WAREHOUSE_RELATIONS = {
    "forebet": ("forebet_settled",),
    "prosoccer": ("prosoccer", "prosoccer_settled"),
    "soccervista": ("soccervista",),
    "predictz": ("predictz_settled",),
    "windrawwin": ("windrawwin",),
    "scoutingstats": ("scoutingstats_settled",),
    "vitibet": ("vitibet", "vitibet_settled"),
    "zulubet": ("zulubet_settled",),
    "statarea": ("statarea_settled",),
    "bettingclosed": ("bettingclosed_settled",),
    "freesupertips": ("freesupertips",),
    "betclan": ("betclan",),
    "afootballreport": ("afootballreport",),
    "bzzoiro": ("bzzoiro",),
}

CONSENSUS_ROLE = {
    "forebet": "parked/core-history",
    "prosoccer": "weighted-gated",
    "soccervista": "shadow-confirm",
    "predictz": "shadow-confirm",
    "windrawwin": "shadow-confirm",
    "scoutingstats": "weighted-gated",
    "vitibet": "weighted-gated",
    "zulubet": "weighted-gated",
    "statarea": "weighted-gated",
    "bettingclosed": "confirm/results",
    "freesupertips": "shadow/not-ready",
    "betclan": "candidate-gated",
    "afootballreport": "research",
    "bzzoiro": "candidate-gated",
    "bzzoiro_odds": "pricing-only",
    "theoddsapi_odds": "pricing-only",
    "oddspapi_odds": "pricing-only",
}


@dataclass(frozen=True)
class Availability:
    source: str
    in_capture_jobs: bool
    file_count: int
    latest_date: str | None
    target_rows: int
    rolling_rows: int
    target_done: bool
    recent_failures: tuple[tuple[str, str], ...]
    read_errors: tuple[str, ...]
    warehouse: bool


def capture_job_sources(script_path: Path | None = None) -> set[str]:
    """Load source keys from capture_daily without duplicating its registry."""
    path = script_path or ROOT / "scripts" / "capture_daily.py"
    spec = importlib.util.spec_from_file_location("edgefactory_capture_daily_audit", path)
    if spec is None or spec.loader is None:
        return set()
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {str(job[0]) for job in module.JOBS}


def source_files(localdata: Path, source: str) -> list[Path]:
    """Return exact legacy/monthly files for one source."""
    monthly = sorted(localdata.glob(f"{source}_[0-9][0-9][0-9][0-9]-[0-9][0-9].csv.gz"))
    legacy = localdata / f"{source}.csv.gz"
    return ([legacy] if legacy.exists() else []) + monthly


def _row_day(row: dict[str, str]) -> str | None:
    raw = str(row.get("date") or "").strip()[:10]
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        return None


def warehouse_relations(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        import duckdb

        con = duckdb.connect(str(path), read_only=True)
        try:
            rows = con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            ).fetchall()
            return {str(row[0]) for row in rows}
        finally:
            con.close()
    except Exception:
        return set()


def scan_source(
    source: str,
    *,
    localdata: Path,
    target: date,
    days: int,
    capture_jobs: set[str],
    warehouse_tables: set[str] | None = None,
) -> Availability:
    if days < 1:
        raise ValueError("days must be >= 1")

    # Match capture_daily/backfill_results semantics: D30 starts exactly 30
    # days before target and includes both endpoints.
    start = target - timedelta(days=days)
    latest: date | None = None
    target_rows = 0
    rolling_rows = 0
    errors: list[str] = []
    files = source_files(localdata, source)

    for path in files:
        try:
            with gzip.open(path, "rt", newline="") as handle:
                for row in csv.DictReader(handle):
                    value = _row_day(row)
                    if value is None:
                        continue
                    row_date = date.fromisoformat(value)
                    latest = row_date if latest is None or row_date > latest else latest
                    if row_date == target:
                        target_rows += 1
                    if start <= row_date <= target:
                        rolling_rows += 1
        except (OSError, csv.Error, UnicodeError) as exc:
            errors.append(f"{path.name}: {type(exc).__name__}: {str(exc)[:100]}")

    target_done = False
    recent_failures: list[tuple[str, str]] = []
    state_path = localdata / f"state_{source}.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
            target_done = target.isoformat() in set(state.get("done", []))
            failures = state.get("failures", {})
            if isinstance(failures, dict):
                recent_failures = sorted(
                    (str(day), str(message))
                    for day, message in failures.items()
                    if start.isoformat() <= str(day) <= target.isoformat()
                )
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            errors.append(f"{state_path.name}: {type(exc).__name__}: {str(exc)[:100]}")

    relations = WAREHOUSE_RELATIONS.get(source, ())
    wh = bool(set(relations) & (warehouse_tables or set()))
    return Availability(
        source=source,
        in_capture_jobs=source in capture_jobs,
        file_count=len(files),
        latest_date=latest.isoformat() if latest else None,
        target_rows=target_rows,
        rolling_rows=rolling_rows,
        target_done=target_done,
        recent_failures=tuple(recent_failures),
        read_errors=tuple(errors),
        warehouse=wh,
    )


def _notes(row: Availability) -> str:
    notes: list[str] = []
    if row.recent_failures:
        day, message = row.recent_failures[-1]
        notes.append(f"retryable_failures={len(row.recent_failures)} last={day}:{message[:55]}")
    elif row.target_done and row.target_rows == 0:
        notes.append("target marked done with 0 rows")
    elif row.in_capture_jobs and not row.target_done:
        notes.append("target pending/not marked done")
    if row.file_count == 0:
        notes.append("no local files")
    if row.read_errors:
        notes.append(f"read_errors={len(row.read_errors)}")
    return "; ".join(notes) or "-"


def render(rows: list[Availability], *, target: date, days: int) -> str:
    headers = ("source", "job", "files", "latest", "target", f"D{days}", "warehouse", "consensus role", "state/notes")
    values = []
    for row in rows:
        values.append((
            row.source,
            "yes" if row.in_capture_jobs else "no",
            str(row.file_count),
            row.latest_date or "-",
            str(row.target_rows),
            str(row.rolling_rows),
            "yes" if row.warehouse else "no",
            CONSENSUS_ROLE.get(row.source, "-"),
            _notes(row),
        ))
    widths = [max(len(headers[i]), *(len(v[i]) for v in values)) for i in range(len(headers))]

    def line(parts: tuple[str, ...]) -> str:
        return "  ".join(value.ljust(widths[i]) for i, value in enumerate(parts))

    output = [
        f"Source availability for {target.isoformat()} (D{days} lookback, inclusive)",
        line(headers),
        line(tuple("-" * width for width in widths)),
    ]
    output.extend(line(row) for row in values)
    return "\n".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit local source freshness and capture state")
    parser.add_argument("--date", default=date.today().isoformat(), help="target date YYYY-MM-DD")
    parser.add_argument("--days", type=int, default=30, help="D-day lookback (both endpoints included)")
    parser.add_argument("--sources", help="optional comma-separated source list")
    parser.add_argument("--localdata", type=Path, default=LOCALDATA, help=argparse.SUPPRESS)
    args = parser.parse_args()

    try:
        target = date.fromisoformat(args.date)
    except ValueError as exc:
        parser.error(str(exc))
    if args.days < 1:
        parser.error("--days must be >= 1")

    sources = tuple(
        part.strip() for part in (args.sources or ",".join(DEFAULT_SOURCES)).split(",")
        if part.strip()
    )
    jobs = capture_job_sources()
    tables = warehouse_relations(args.localdata / "warehouse.duckdb")
    rows = [
        scan_source(
            source,
            localdata=args.localdata,
            target=target,
            days=args.days,
            capture_jobs=jobs,
            warehouse_tables=tables,
        )
        for source in sources
    ]
    print(render(rows, target=target, days=args.days))


if __name__ == "__main__":
    main()
