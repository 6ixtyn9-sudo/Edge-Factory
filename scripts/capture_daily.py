#!/usr/bin/env python3
"""Daily capture for ALL sources — run once per day (cron/Actions).
Backfillable sources append yesterday+today (results settle), capture-forward
sources snapshot today+tomorrow (predictions before they're wiped).
    python3 scripts/capture_daily.py
"""

from __future__ import annotations
import argparse
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
    ("bzzoiro_odds", TODAY, TOMORROW),    # live real-book odds for pick enrichment
    ("bettingclosed", D30, TODAY),
    # rolling prediction week only (yesterday settles + today/tomorrow probs);
    # weekday pages beyond tomorrow are out of the picks horizon.
    ("prosoccer", YESTERDAY, TOMORROW),
    # today-only (JS day picker; no plain-GET archive)
    ("soccervista", TODAY, TODAY),
]

def reset_recent_state(source: str, days: list[str]) -> None:
    """Drop recent days from state so they re-fetch (results settle late)."""
    import json
    p = ROOT / "localdata" / f"state_{source}.json"
    if not p.exists():
        return
    st = json.loads(p.read_text())
    st["done"] = [d for d in st["done"] if d not in days]
    p.write_text(json.dumps(st))

def main() -> None:
    ap = argparse.ArgumentParser(description="Daily capture for all sources")
    ap.add_argument(
        "--skip-build",
        action="store_true",
        help="capture only; caller will run scripts/build_warehouse.py explicitly",
    )
    ap.add_argument(
        "--sources",
        help="optional comma-separated source keys for bounded intraday recaptures",
    )
    args = ap.parse_args()

    selected = None
    if args.sources:
        selected = {part.strip() for part in args.sources.split(",") if part.strip()}
    jobs = [job for job in JOBS if selected is None or job[0] in selected]
    if selected:
        known = {job[0] for job in JOBS}
        unknown = sorted(selected - known)
        if unknown:
            print(f"ERROR: unknown capture source(s): {', '.join(unknown)}", file=sys.stderr)
            sys.exit(2)

    window = [D30, YESTERDAY, (date.today() - timedelta(days=2)).isoformat(),
              TODAY, TOMORROW]
    failures = []
    summaries = []
    for source, start, end in jobs:
        reset_recent_state(source, window)
        cmd = [sys.executable, str(ROOT / "scripts" / "local_backfill.py"),
               source, start, end, "--max-seconds", "240", "--workers", "4"]
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
        rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_warehouse.py")],
                       cwd=ROOT).returncode
        if rc != 0:
            print("Warehouse build failed")
            sys.exit(1)

    if failures:
        print("FAILED:", failures)
        sys.exit(1)
    print("capture complete ✅")

if __name__ == "__main__":
    main()
