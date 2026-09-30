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

from edgefactory import fixture_reconciliation  # noqa: E402
from edgefactory import selection_evidence  # noqa: E402
from edgefactory import source_census  # noqa: E402
from edgefactory import source_registry  # noqa: E402
from edgefactory import source_utilisation  # noqa: E402

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
    parser.add_argument("--no-log", action="store_true",
                        help="write artifacts without printing the log")
    parser.add_argument("--no-group-markers", action="store_true",
                        help="plain headings instead of ::group:: markers")
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

    # Why is each source in the role it is in? Same rows, different
    # question: the census says what a source saw, this says whether the
    # pipeline is using what it saw.
    try:
        first_day = census["dates"][0]
        census["utilisation"] = source_utilisation.build_utilisation(
            census["per_date"][first_day]["sources"],
            validation_states=source_registry.load_validation_states(
                args.localdata),
            eligible_voters=selection_evidence.eligible_1x2_voters(
                source_registry.names()))
    except Exception as exc:  # pragma: no cover - diagnostics never break
        census["utilisation"] = {"error": str(exc)}

    # Which "single-source" fixtures are actually alias failures?
    try:
        census["fixture_reconciliation"] = {
            day: fixture_reconciliation.build_reconciliation(
                census["per_date"][day]["fixture_groups"])
            for day in census["dates"]}
    except Exception as exc:  # pragma: no cover - diagnostics never break
        census["fixture_reconciliation"] = {"error": str(exc)}

    written = write_census(census, localdata=args.localdata,
                           run_date=args.date, write_csv=not args.no_csv)

    if not args.no_log:
        # The artifacts are complete, but the operator reads the Actions
        # log. Emit every fixture there too, with completeness counters.
        for line in source_census.render_log(
                census, group_markers=not args.no_group_markers,
                artifact_paths=[str(path.relative_to(ROOT))
                                if path.is_relative_to(ROOT) else str(path)
                                for path in written]):
            print(line)
        utilisation = census.get("utilisation") or {}
        if utilisation.get("sources"):
            print("")
            for line in source_utilisation.render_utilisation_lines(
                    utilisation):
                print(line)
        for day, reconciliation in (
                census.get("fixture_reconciliation") or {}).items():
            if not isinstance(reconciliation, dict) or \
                    "single_source_fixtures" not in reconciliation:
                continue
            print("")
            print(f"-- {day}")
            for line in fixture_reconciliation.render_reconciliation_lines(
                    reconciliation):
                print(line)
    else:
        print("source fixture census: "
              + ", ".join(path.name for path in written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
