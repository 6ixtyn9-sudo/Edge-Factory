#!/usr/bin/env python3
"""Daily capture for source adapters — run once per day (cron/Actions).

Backfillable sources append yesterday+today (results settle), while
capture-forward sources snapshot today+tomorrow (predictions before they are
wiped). The ``forebet-resilience`` group deliberately parks Forebet and is the
production recovery path::

    python3 scripts/capture_daily.py --source-group forebet-resilience
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TODAY = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
D30 = (date.today() - timedelta(days=30)).isoformat()

# (source, start, end) — widened to 30 days for better context maturity
JOBS = [
    # deep-history sources: re-pull last 30 days for settlement + today/tomorrow
    ("forebet", D30, TOMORROW),
    ("zulubet", D30, TODAY),
    ("statarea", D30, TODAY),
    ("vitibet", D30, TOMORROW),          # archive serves results; probs only live
    ("scoutingstats", D30, TODAY),
    ("predictz", D30, TODAY),

    # capture-forward only
    ("windrawwin", TODAY, TOMORROW),
    ("afootballreport", TODAY, TODAY),
    ("betclan", TODAY, TODAY),
    ("freesupertips", TODAY, TOMORROW),
    ("bzzoiro", TODAY, TODAY),           # snapshots ALL upcoming (~7 weeks ahead)
    ("bzzoiro_odds", TODAY, TOMORROW),   # live real-book odds for pick enrichment
    ("bettingclosed", D30, TODAY),
    # rolling prediction week only (yesterday settles + today/tomorrow probs);
    # weekday pages beyond tomorrow are out of the picks horizon.
    ("prosoccer", YESTERDAY, TOMORROW),
    # today-only (JS day picker; no plain-GET archive)
    ("soccervista", TODAY, TODAY),
]

FOREBET_RESILIENCE_SOURCES = (
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
)

SOURCE_GROUPS = {
    "forebet-resilience": FOREBET_RESILIENCE_SOURCES,
}

# Piggyback only the four authorized response-backed sources already in the
# daily capture plan. BetMiner's existing request path lives in picks_today.
PHASE5_BACKFILL_SOURCES = frozenset({
    "vitibet", "bzzoiro", "betclan", "scoutingstats",
})


def _csv_sources(value: str | None) -> set[str]:
    return {part.strip() for part in (value or "").split(",") if part.strip()}


def resolve_selected_sources(
    sources: str | None,
    source_groups: list[str] | None,
) -> set[str] | None:
    """Resolve explicit sources and named groups into one union.

    ``None`` means the legacy all-source plan. Supplying both options is
    intentionally additive, so operators can start with a safe group and add a
    bounded explicit adapter without silently replacing the group.
    """
    if not sources and not source_groups:
        return None

    known = {job[0] for job in JOBS}
    selected = _csv_sources(sources)
    unknown_groups = sorted(set(source_groups or []) - set(SOURCE_GROUPS))
    if unknown_groups:
        raise ValueError(f"unknown capture source group(s): {', '.join(unknown_groups)}")

    for group in source_groups or []:
        selected.update(SOURCE_GROUPS[group])

    unknown_sources = sorted(selected - known)
    if unknown_sources:
        raise ValueError(f"unknown capture source(s): {', '.join(unknown_sources)}")
    if not selected:
        raise ValueError("no capture sources selected")
    return selected


def reset_recent_state(source: str, days: list[str]) -> None:
    """Drop recent days from state so they re-fetch (results settle late)."""
    p = ROOT / "localdata" / f"state_{source}.json"
    if not p.exists():
        return
    try:
        st = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return
    st["done"] = [d for d in st.get("done", []) if d not in days]
    failures = st.get("failures")
    if isinstance(failures, dict):
        st["failures"] = {d: msg for d, msg in failures.items() if d not in days}
    p.write_text(json.dumps(st, sort_keys=True))


def main() -> None:
    ap = argparse.ArgumentParser(description="Daily capture for source adapters")
    ap.add_argument(
        "--skip-build",
        action="store_true",
        help="capture only; caller will run scripts/build_warehouse.py explicitly",
    )
    ap.add_argument(
        "--sources",
        help="optional comma-separated source keys for bounded recaptures",
    )
    ap.add_argument(
        "--source-group",
        action="append",
        dest="source_groups",
        help=(
            "named source group (repeatable); known groups: "
            + ", ".join(sorted(SOURCE_GROUPS))
            + "; combines with --sources"
        ),
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero after all adapters run if any source failed",
    )
    ap.add_argument(
        "--phase5-shadow",
        action="store_true",
        help=(
            "append forward-only Phase 5 rows from existing authorized responses; "
            "never adds a source request"
        ),
    )
    args = ap.parse_args()

    try:
        selected = resolve_selected_sources(args.sources, args.source_groups)
    except ValueError as exc:
        ap.error(str(exc))

    jobs = [job for job in JOBS if selected is None or job[0] in selected]
    phase5_capture_day = None
    phase5_context = os.environ.get(
        "EDGE_FACTORY_PHASE5_RUN_CONTEXT", "manual_or_unspecified"
    )
    phase5_authorized = (
        args.phase5_shadow and phase5_context == "official_daily_pipeline"
    )
    if args.phase5_shadow and not phase5_authorized:
        print(
            "PHASE5_CAPTURE status=skipped_by_mode "
            f"reason=official_daily_pipeline_required context={phase5_context}"
        )
    if phase5_authorized:
        if not any(source in PHASE5_BACKFILL_SOURCES for source, _start, _end in jobs):
            ap.error("--phase5-shadow requires an authorized backfill source in the selected jobs")
        sys.path.insert(0, str(ROOT / "src"))
        from edgefactory.phase5_shadow import local_capture_date

        phase5_capture_day = local_capture_date()

    window = [
        D30,
        YESTERDAY,
        (date.today() - timedelta(days=2)).isoformat(),
        TODAY,
        TOMORROW,
    ]
    failures = []
    summaries = []
    for source, start, end in jobs:
        reset_recent_state(source, window)
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "local_backfill.py"),
            source,
            start,
            end,
            "--max-seconds",
            "240",
            "--workers",
            "4",
        ]
        if phase5_authorized and source in PHASE5_BACKFILL_SOURCES:
            cmd.extend(["--phase5-shadow", "--capture-day", phase5_capture_day])
        print(f"\n=== {source} {start}..{end} ===", flush=True)
        rc = subprocess.run(cmd, cwd=ROOT).returncode
        status = "ok" if rc == 0 else f"failed(rc={rc})"
        summaries.append((source, start, end, status))
        print(f"SOURCE SUMMARY {source}: {status} range={start}..{end}", flush=True)
        if rc != 0:
            failures.append(source)

    if summaries:
        print("\nCapture source summaries:")
        for source, start, end, status in summaries:
            print(f"  {source}: {status} ({start}..{end})")

    if args.skip_build:
        print("\nSkipping warehouse rebuild (--skip-build); caller must run build_warehouse.py next.")
    else:
        print("\nRebuilding warehouse...")
        rc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_warehouse.py")],
            cwd=ROOT,
        ).returncode
        if rc != 0:
            print("Warehouse build failed")
            sys.exit(1)

    if failures:
        print(f"CAPTURE PARTIAL: {', '.join(failures)} failed and remain retryable")
        if args.strict:
            sys.exit(1)
        print("Continuing in resilience mode; successful sources remain usable.")
    else:
        print("capture complete ✅")


if __name__ == "__main__":
    main()
