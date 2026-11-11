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
  betexplorer_capture_DATE.json, betexplorer_odds_cache_DATE.json,
  betexplorer_match_detail_DATE.json                    bounded price snapshots
                                                        and per-match, per-market
                                                        detail
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

Any filename cited by ``docs/operator/DATED-CLAIMS.md`` is retained with no
age limit. A citation is a durability contract: the prune must never break a
claim it cannot see. On 2026-11-09 the 30-day pass deleted eleven 2026-10-10
files, one of them cited by six ledger rows, and all six stopped resolving.

The CLI first rolls older durable daily families into
``archive/<family>/<year>/<month>/`` without changing their bytes. The same
30-day hot window is retained at the root; readers support both layouts.
Unknown files, monthly raw archives and financial state are never relocated.
The public pruning helpers below retain their existing telemetry contract.

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
from edgefactory.util import (
    cited_basenames as _cited_basenames,
    cited_paths,
    resolve_dated_claims_ledger,
)
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
sys.path.insert(0, str(ROOT / "src"))
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
        rf"^betexplorer_capture_{_DATE}\.json$",
        rf"^betexplorer_odds_cache_{_DATE}\.json$",
        rf"^betexplorer_match_detail_{_DATE}\.json$",
        rf"^supabase_sync_manifest_{_DATE}\.json$",
        rf"^official_run_{_DATE}\.json$",
        rf"^picks_{_DATE}\.txt$",
        rf"^picks_audit_{_DATE}\.md$",
        # Shadow capture ledgers (<source>_shadow_DATE.json, seven writers:
        # betbetter, betminer, boggio, futbolpronosticos, pinnapi_odds,
        # sharpapi_odds, sportytrader_odds). Committed since 2026-10-10 as the
        # raw evidence for join-miss triage (Bet Better's raw selection
        # fields live nowhere else). Every reader is day-scoped and
        # cache-first: a ledger older than yesterday is never read again, so
        # the same 30-day window that bounds the other telemetry bounds
        # these without changing any read.
        rf"^betbetter_shadow_{_DATE}\.json$",
        rf"^betminer_shadow_{_DATE}\.json$",
        rf"^boggio_shadow_{_DATE}\.json$",
        rf"^futbolpronosticos_shadow_{_DATE}\.json$",
        rf"^pinnapi_odds_shadow_{_DATE}\.json$",
        rf"^sharpapi_odds_shadow_{_DATE}\.json$",
        rf"^sportytrader_odds_shadow_{_DATE}\.json$",
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


DATED_CLAIMS_LEDGER = ROOT / "docs" / "operator" / "DATED-CLAIMS.md"
_CITED_PATH = re.compile(r"localdata/[A-Za-z0-9_./-]+\.(?:json|jsonl|txt|md|csv|gz)")


def cited_basenames(ledger: Path | None = None) -> set[str] | None:
    """Basenames the dated-claims ledger cites as backing evidence.

    A cited path is what tests/test_dated_claims_ledger.py asserts resolves,
    so pruning one manufactures a broken claim. Returns None when the
    ledger exists but cannot be read: unknown citations must not authorise a
    deletion, so the caller prunes nothing at all (morning_archive_is_
    redundant fails closed in exactly the same way).
    """
    if ledger is None:
        ledger = DATED_CLAIMS_LEDGER
    return _cited_basenames(ledger)


def files_to_prune(
    root: Path = LOCALDATA,
    *,
    keep_days: int = DEFAULT_KEEP_DAYS,
    today: date | None = None,
    ledger: Path | None = None,
) -> list[Path]:
    """Return old known telemetry files; never unknown or durable data."""
    if keep_days < 1:
        raise ValueError("keep_days must be at least 1")
    root = Path(root)
    today = today or date.today()
    cutoff = today - timedelta(days=keep_days - 1)  # oldest retained day
    stale: list[Path] = []
    ledger_path = resolve_dated_claims_ledger(root, ledger)
    cited = cited_basenames(ledger_path)
    for path in sorted(root.iterdir()) if root.exists() else ():
        if not path.is_file() or path.is_symlink():
            continue
        if cited is None or path.name in cited:
            continue  # cited evidence, or the ledger could not be read
        day = _telemetry_day(path.name)
        if day is not None:
            if day < cutoff:
                stale.append(path)
            continue
        morning_day = _file_day(MORNING_PATTERN, path.name)
        if (morning_day is not None and morning_day < cutoff
                and morning_archive_is_redundant(root, morning_day.isoformat())):
            stale.append(path)

    # ML paper intermediate timestamped run receipts (autobets_ML_<DATE>_<TIMESTAMP>.json).
    # Prune runs older than the retention window; canonical autobets_ML_<DATE>.json is kept.
    ml_receipt_dir = root / "phase5_reconciliation" / "ml_paper_receipts"
    if ml_receipt_dir.is_dir():
        ts_pattern = re.compile(rf"^autobets_ML_{_DATE}_\d{{8}}T\d{{12}}Z\.json$")
        for path in sorted(ml_receipt_dir.iterdir()):
            if not path.is_file() or path.is_symlink():
                continue
            if cited is None or path.name in cited:
                continue
            match = ts_pattern.match(path.name)
            if match:
                try:
                    file_day = date.fromisoformat(match.group("day"))
                    if file_day < cutoff:
                        stale.append(path)
                except ValueError:
                    continue

    return stale


def clean_localdata(
    root: Path = LOCALDATA,
    *,
    keep_days: int = DEFAULT_KEEP_DAYS,
    today: date | None = None,
    dry_run: bool = False,
    ledger: Path | None = None,
) -> list[Path]:
    """Delete (or with ``dry_run`` only list) stale telemetry; return paths."""
    removed = files_to_prune(root, keep_days=keep_days, today=today, ledger=ledger)
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
    parser.add_argument("--ledger", type=Path, default=None,
                        help="dated-claims ledger path (default: auto-detected)")
    args = parser.parse_args(argv)
    print(f"Cleaning dated localdata telemetry (keeping {args.keep_days} days) ...")
    # Archive durable daily families before the old telemetry-pruning pass.
    # In particular, morning evidence now survives even when parity would
    # have allowed deletion. Public pruning helpers retain their old contract.
    from edgefactory.util import archive_dated_artifacts
    archived = archive_dated_artifacts(args.localdata, keep_days=args.keep_days,
                                       today=args.today, dry_run=args.dry_run,
                                       ledger=args.ledger)
    print(f"  {'would archive' if args.dry_run else 'archived'} {len(archived)} dated artifacts")
    removed = clean_localdata(args.localdata, keep_days=args.keep_days,
                              today=args.today, dry_run=args.dry_run,
                              ledger=args.ledger)
    remaining = sum(1 for _ in args.localdata.iterdir()) if args.localdata.exists() else 0
    verb = "Would remove" if args.dry_run else "Removed"
    print(f"Done. {verb} {len(removed)} file(s); {remaining} entries in {args.localdata.name}/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
