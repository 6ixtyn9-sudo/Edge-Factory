#!/usr/bin/env python3
"""Write the per-source, per-day fixture census. Diagnostic only.

Answers "which matches does each source see on each date, and why can the
production lane not use them?". It reads capture caches only, never the
network, and writes nothing except its own artifacts.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from edgefactory import source_census  # noqa: E402

TZ = ZoneInfo("Africa/Johannesburg")


def load_picks_engine():
    """Share the live engine's normalization and gates, never a copy."""
    path = ROOT / "scripts" / "picks_today.py"
    spec = importlib.util.spec_from_file_location(
        "edgefactory_picks_today_census", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _read_json(path: Path):
    try:
        return json.loads(path.read_text()) if path.exists() else None
    except (OSError, ValueError):
        return None


def write_census(census: dict, *, localdata: Path, run_date: str,
                 write_csv: bool = True) -> list[Path]:
    written = []
    json_path = localdata / f"source_fixture_census_{run_date}.json"
    json_path.write_text(json.dumps(census, indent=2, sort_keys=True,
                                    default=str))
    written.append(json_path)

    md_path = localdata / f"source_fixture_census_{run_date}.md"
    md_path.write_text(source_census.render_markdown(census))
    written.append(md_path)

    if write_csv:
        csv_path = localdata / f"source_fixture_census_{run_date}.csv.gz"
        rows = source_census.render_csv_rows(census)
        with gzip.open(csv_path, "wt", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=source_census.CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        written.append(csv_path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="run date YYYY-MM-DD")
    parser.add_argument("--horizon-days", type=int, default=2,
                        help="future days to cover in addition to the run date")
    parser.add_argument("--min-lead", type=int,
                        default=source_census.DEFAULT_MIN_LEAD)
    parser.add_argument("--as-of", default=None,
                        help="ISO timestamp used for the pre-match guard")
    parser.add_argument("--localdata", type=Path, default=LOCALDATA)
    parser.add_argument("--no-csv", action="store_true")
    args = parser.parse_args(argv)

    engine = load_picks_engine()
    if engine is None:
        print("source census skipped: picks engine unavailable")
        return 0

    as_of = (datetime.fromisoformat(args.as_of) if args.as_of
             else datetime.now(TZ))
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=TZ)

    from edgefactory import production_lane

    plan = production_lane.load_dispatch_plan(args.date, args.localdata)
    outcomes = (_read_json(
        args.localdata / f"auto_ticket_outcomes_{args.date}.json") or {}
    ).get("outcomes") or {}

    census = source_census.build_census(
        run_date=args.date, localdata=args.localdata, engine=engine,
        as_of=as_of, horizon_days=args.horizon_days, min_lead=args.min_lead,
        dispatch_plan=plan, ticket_outcomes=outcomes)

    written = write_census(census, localdata=args.localdata,
                           run_date=args.date, write_csv=not args.no_csv)
    for day, payload in census["per_date"].items():
        totals = payload["totals"]
        print(f"census {day}: {totals['unique_fixture_groups']} fixture "
              f"group(s), {totals['groups_with_quorum']} with >=2 live 1X2 "
              f"voters, {totals['ml_scoreable_groups']} ML-scoreable, "
              f"{totals['prematch_eligible_ml_scoreable']} pre-match eligible")
    print("source census: " + ", ".join(p.name for p in written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
