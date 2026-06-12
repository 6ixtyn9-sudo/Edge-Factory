#!/usr/bin/env python3
"""Daily capture for ALL sources — run once per day (cron/Actions).
Backfillable sources append yesterday+today (results settle), capture-forward
sources snapshot today+tomorrow (predictions before they're wiped).
    python3 scripts/capture_daily.py
"""

from __future__ import annotations
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TODAY = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
D3 = (date.today() - timedelta(days=3)).isoformat()

# (source, start, end) — ranges deliberately small; backfiller skips done days,
# but we FORCE re-fetch of the recent window so results/settlements update.
JOBS = [
    # deep-history sources: re-pull last 3 days for settlement + today/tomorrow
    ("forebet", D3, TOMORROW),
    ("zulubet", D3, TODAY),
    ("statarea", D3, TODAY),
    ("vitibet", D3, TOMORROW),          # archive serves results; probs only live
    ("scoutingstats", D3, TODAY),
    ("predictz", D3, TODAY),

    # capture-forward only
    ("windrawwin", TODAY, TOMORROW),
    ("afootballreport", TODAY, TODAY),
    ("betclan", TODAY, TODAY),
    ("freesupertips", TODAY, TOMORROW),
    ("bzzoiro", TODAY, TODAY),           # snapshots ALL upcoming (~7 weeks ahead)
    ("bettingclosed", D3, TODAY),
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
    window = [D3, YESTERDAY, (date.today() - timedelta(days=2)).isoformat(),
              TODAY, TOMORROW]
    failures = []
    for source, start, end in JOBS:
        reset_recent_state(source, window)
        cmd = [sys.executable, str(ROOT / "scripts" / "local_backfill.py"),
               source, start, end, "--max-seconds", "240", "--workers", "4"]
        print(f"\n=== {source} {start}..{end} ===", flush=True)
        rc = subprocess.run(cmd, cwd=ROOT).returncode
        if rc != 0:
            failures.append(source)

    print("\nRebuilding warehouse...")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_warehouse.py")],
                   cwd=ROOT)

    if failures:
        print("FAILED:", failures)
        sys.exit(1)
    print("capture complete ✅")

if __name__ == "__main__":
    main()
