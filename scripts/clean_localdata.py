#!/usr/bin/env python3
"""Prune dated runtime artifacts from ``localdata/``.

``localdata`` is a runtime cache, not an ever-growing source tree.  The daily
workflow commits a bounded recent telemetry window so the GitHub directory
remains browsable; pick archives, rolling ledgers, and monthly source archives
remain durable history because replay and audit use them. Files are only
removed when their names contain an ISO date and they belong to a known
telemetry family. Unknown files and durable pick/state data are left alone by
design.

Usage::

    python scripts/clean_localdata.py              # keep the latest 30 days
    python scripts/clean_localdata.py --keep-days 14

The function is deliberately usable from the workflow and from tests without
shelling out to git.  The workflow's subsequent ``git add -A localdata/`` then
records removals of old tracked artifacts while leaving ignored runtime data
alone in a developer checkout.
"""

from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

# These are append-per-day outputs.  Daily JSON pick archives are durable
# replay inputs and are intentionally retained; their text/morning/audit
# mirrors are telemetry and may be pruned. Rolling summaries, state, monthly
# archives, and current/future aliases are also intentionally left alone.
DAILY_PREFIXES = (
    "auto_tickets_",
    "clv_report_",
    "clv_unmatched_",
    "official_run_",
    "picks_audit_",
    "picks_morning_",
    "sent_ledger_",
    "shadow_sent_ledger_",
    "supabase_sync_manifest_",
    "theoddsapi_attempts_",
    "notify_delivery_failures_",
)

# A dated pick text report is the one daily-pick family not covered by a
# prefix above.  Keep the JSON archive used by replay, prune this display-only
# mirror with the other telemetry.
PICK_TEXT_RE = re.compile(r"^picks_20\d{2}-\d{2}-\d{2}\.txt$")

# A date-bearing name must also match one of these shapes.  This prevents a
# future file such as ``model_2026-09-25.bin`` from being deleted by cleanup.
DATE_RE = re.compile(r"(?<!\d)(20\d{2}-\d{2}-\d{2})(?!\d)")


def _dated_daily_file(path: Path) -> bool:
    if not path.is_file():
        return False
    return (
        (path.name.startswith(DAILY_PREFIXES) and bool(DATE_RE.search(path.name)))
        or bool(PICK_TEXT_RE.match(path.name))
    )


def files_to_prune(
    root: Path = LOCALDATA,
    *,
    keep_days: int = 30,
    today: date | None = None,
) -> list[Path]:
    """Return old, known daily artifacts without touching anything else."""
    if keep_days < 1:
        raise ValueError("keep_days must be at least 1")
    today = today or date.today()
    cutoff = today - timedelta(days=keep_days - 1)
    stale: list[Path] = []
    for path in (root.iterdir() if root.exists() else ()):
        if not _dated_daily_file(path):
            continue
        match = DATE_RE.search(path.name)
        if not match:
            continue
        try:
            file_day = date.fromisoformat(match.group(1))
        except ValueError:
            # A malformed date-shaped filename is not safe to classify.
            continue
        if file_day < cutoff:
            stale.append(path)
    return sorted(stale)


def clean_localdata(
    root: Path = LOCALDATA,
    *,
    keep_days: int = 30,
    today: date | None = None,
) -> list[Path]:
    """Delete stale known daily artifacts and return the deleted paths."""
    removed = files_to_prune(root, keep_days=keep_days, today=today)
    for path in removed:
        print(f"  Removing stale daily artifact: {path.name}")
        path.unlink()
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep-days",
        type=int,
        default=30,
        help="number of recent calendar days to retain (default: 30)",
    )
    args = parser.parse_args()
    print(f"Cleaning dated localdata artifacts (keeping {args.keep_days} days) ...")
    removed = clean_localdata(keep_days=args.keep_days)
    print(f"Done. Removed {len(removed)} file(s).")


if __name__ == "__main__":
    main()
