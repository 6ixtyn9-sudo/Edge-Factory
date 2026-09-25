#!/usr/bin/env python3
"""Prune old dated telemetry from ``localdata/`` (bounded retention).

``localdata`` is committed by the daily workflow, and GitHub's directory view
stops listing entries after 1,000. Most of the growth is per-day telemetry
that nothing reads after its own day. This script removes those files once
they are older than the retention window (default 30 days) and leaves
everything else alone.

What is pruned (exact filename shapes only, see ``TELEMETRY_PATTERNS``):
  clv_report_DATE.md, clv_unmatched_DATE.json            CLV reports
  sent_ledger_DATE.json, shadow_sent_ledger_DATE.json,
  discovery_sent_ledger_DATE.json,
  notify_delivery_failures_DATE.json                     notification ledgers
  theoddsapi_attempts_DATE.json                          odds-attempt logs
  supabase_sync_manifest_DATE.json                       sync manifests
  official_run_DATE.json                                 official-run markers
  picks_DATE.txt                                         pick text reports
  picks_audit_DATE.md                                    pick audit display
  picks_morning_DATE.json                                pick morning files,
                                                         ONLY when redundant

Each reader of these families was checked: all of them read only the current
run date (dedup ledgers, attempt blocks, run markers) or only write the file
(reports, manifests). The edge-firing tripwire reads morning files within 14
days, inside the 30-day window.

``picks_morning_DATE.json`` is not display-only. The rolling audit
(``audit_recent_picks.load_archived_picks_with_receipt``) uses it as the
immutable morning baseline and falls back to ``picks_DATE.json`` when it is
missing. On dates where the regular ledger was later overwritten, the morning
file is the only faithful record. So a morning file is pruned only when the
audit loader gives byte-identical output for that date without it. Anything
else is kept.

Deliberately retained, with no age limit:
  picks_DATE.json            durable replay/audit archive (replay parity input)
  auto_tickets_DATE.txt      printed slips; seed_slice_ledger() rebuilds the
                             selection-ladder evidence from them
  rolling ledgers/state, monthly source archives (*_YYYY-MM.csv.gz),
  warehouse data, and any file whose name does not match a known pattern.

Unknown files are never deleted. Retaining every daily pick archive means
``localdata`` still grows by about 2 entries per day (picks_DATE.json and
auto_tickets_DATE.txt) plus non-redundant morning files. That growth is linear
but slow; compacting those archives would need the replay/audit loaders to
read a new format first.

Usage::

    python scripts/clean_localdata.py                  # keep the latest 30 days
    python scripts/clean_localdata.py --keep-days 14
    python scripts/clean_localdata.py --dry-run        # list, delete nothing
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
DEFAULT_KEEP_DAYS = 30

_DATE = r"(?P<day>20\d{2}-\d{2}-\d{2})"

# Exact shapes. A new file family is kept until it is added here on purpose.
TELEMETRY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p)
    for p in (
        rf"^clv_report_{_DATE}\.md$",
        rf"^clv_unmatched_{_DATE}\.json$",
        rf"^sent_ledger_{_DATE}\.json$",
        rf"^shadow_sent_ledger_{_DATE}\.json$",
        rf"^discovery_sent_ledger_{_DATE}\.json$",
        rf"^notify_delivery_failures_{_DATE}\.json$",
        rf"^theoddsapi_attempts_{_DATE}\.json$",
        rf"^supabase_sync_manifest_{_DATE}\.json$",
        rf"^official_run_{_DATE}\.json$",
        rf"^picks_{_DATE}\.txt$",
        rf"^picks_audit_{_DATE}\.md$",
    )
)

# Pruned only after the audit-parity proof in ``morning_archive_is_redundant``.
MORNING_PATTERN = re.compile(rf"^picks_morning_{_DATE}\.json$")


def _file_day(pattern: re.Pattern[str], name: str) -> date | None:
    match = pattern.match(name)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group("day"))
    except ValueError:
        return None  # malformed date-shaped name: not safe to classify


def _telemetry_day(name: str) -> date | None:
    for pattern in TELEMETRY_PATTERNS:
        day = _file_day(pattern, name)
        if day is not None:
            return day
    return None


def _audit_loader():
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import audit_recent_picks  # noqa: PLC0415 - lazy: only needed for morning files

    return audit_recent_picks.load_archived_picks_with_receipt


def morning_archive_is_redundant(root: Path, day: str) -> bool:
    """True only if deleting ``picks_morning_{day}.json`` changes nothing.

    Runs the audit's own loader for ``day`` twice: once on ``root`` and once
    on a scratch directory holding only the regular ``picks_{day}.json``.
    Byte-identical output means the audit (and every morning-file reader)
    loses no information. Any failure counts as "not redundant".
    """
    try:
        loader = _audit_loader()
        with_morning, _ = loader(day, day, localdata=root)
        with tempfile.TemporaryDirectory() as scratch:
            regular = root / f"picks_{day}.json"
            if regular.exists():
                shutil.copy2(regular, Path(scratch) / regular.name)
            without_morning, _ = loader(day, day, localdata=Path(scratch))
    except Exception as exc:  # fail closed: keep the file
        print(f"  keeping picks_morning_{day}.json (parity check failed: {exc})")
        return False

    def dump(rows):
        return json.dumps(rows, sort_keys=True, ensure_ascii=False, default=str)

    return dump(with_morning) == dump(without_morning)


def files_to_prune(
    root: Path = LOCALDATA,
    *,
    keep_days: int = DEFAULT_KEEP_DAYS,
    today: date | None = None,
) -> list[Path]:
    """Return old known telemetry files; never unknown or durable data."""
    if keep_days < 1:
        raise ValueError("keep_days must be at least 1")
    root = Path(root)
    today = today or date.today()
    cutoff = today - timedelta(days=keep_days - 1)  # oldest retained day
    stale: list[Path] = []
    for path in sorted(root.iterdir()) if root.exists() else ():
        if not path.is_file() or path.is_symlink():
            continue
        day = _telemetry_day(path.name)
        if day is not None:
            if day < cutoff:
                stale.append(path)
            continue
        morning_day = _file_day(MORNING_PATTERN, path.name)
        if (morning_day is not None and morning_day < cutoff
                and morning_archive_is_redundant(root, morning_day.isoformat())):
            stale.append(path)
    return stale


def clean_localdata(
    root: Path = LOCALDATA,
    *,
    keep_days: int = DEFAULT_KEEP_DAYS,
    today: date | None = None,
    dry_run: bool = False,
) -> list[Path]:
    """Delete (or with ``dry_run`` only list) stale telemetry; return paths."""
    removed = files_to_prune(root, keep_days=keep_days, today=today)
    for path in removed:
        print(f"  {'would remove' if dry_run else 'removing'} stale telemetry: {path.name}")
        if not dry_run:
            path.unlink()
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prune old dated telemetry from localdata/ (bounded retention).")
    parser.add_argument("--keep-days", type=int, default=DEFAULT_KEEP_DAYS,
                        help=f"recent calendar days to retain (default: {DEFAULT_KEEP_DAYS})")
    parser.add_argument("--today", type=date.fromisoformat, default=None,
                        help="reference date YYYY-MM-DD (default: today)")
    parser.add_argument("--localdata", type=Path, default=LOCALDATA,
                        help="directory to clean (default: repo localdata/)")
    parser.add_argument("--dry-run", action="store_true",
                        help="list what would be removed without deleting")
    args = parser.parse_args(argv)
    print(f"Cleaning dated localdata telemetry (keeping {args.keep_days} days) ...")
    removed = clean_localdata(args.localdata, keep_days=args.keep_days,
                              today=args.today, dry_run=args.dry_run)
    remaining = sum(1 for _ in args.localdata.iterdir()) if args.localdata.exists() else 0
    verb = "Would remove" if args.dry_run else "Removed"
    print(f"Done. {verb} {len(removed)} file(s); {remaining} entries in {args.localdata.name}/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
