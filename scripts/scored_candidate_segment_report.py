#!/usr/bin/env python3
"""Segment analysis CLI for the scored-candidate shadow ledger.

AUDIT RECOMMENDATION — NOT LIVE STAKING LOGIC.
No live betting behavior changed. Promotion requires separate explicit
implementation and review.

Reads persisted shadow ledgers only (no price fetching, no backfill, no
mutation of historical events) and prints a ranked, anti-overfit promotion
map: which scored-but-not-promoted segments made money, under which price
class, and what the recommended (non-live) action is.

Usage:
  python scripts/scored_candidate_segment_report.py --date 2026-09-06
  python scripts/scored_candidate_segment_report.py --from 2026-09-01 --to 2026-09-07
  python scripts/scored_candidate_segment_report.py --windows 7,14,30 --to 2026-10-07
  ... [--json] [--min-settled N] [--min-days N] [--min-fixtures N]
      [--all-runs] [--root PATH] [--top N]

--windows runs rolling multi-window survival analysis anchored at --to:
each window length gets its own (stricter-with-length) threshold profile,
and only an EXECUTION_SAFE_PROMOTION_CANDIDATE that survives EVERY window
is listed as promotion-proposal ready (still a label, never a behavior
change). Passing explicit threshold flags with --windows overrides every
window and the report flags the override.

With --root, settled facts come ONLY from that root's settled_results.json
overlay (hermetic, same semantics as scored_candidate_shadow_report.py).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgefactory import scored_candidate_segments as seg  # noqa: E402
from edgefactory import scored_candidate_shadow as scs  # noqa: E402


def _settled_for(root: Path | None):
    if root is not None:
        return scs.load_settled_overlay(root)
    try:
        import auto_tickets  # noqa: PLC0415
        return {
            (str(r.get("date") or "")[:10],
             scs.norm_team(r.get("home")), scs.norm_team(r.get("away"))):
            str(r.get("outcome"))
            for r in auto_tickets.load_settled().get("rows", [])
        }
    except Exception as exc:  # pragma: no cover - fallback path
        print(f"warn: full settled loader unavailable ({exc}); "
              "using overlay only", file=sys.stderr)
        return scs.load_settled_overlay(None)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date")
    p.add_argument("--from", dest="day_from")
    p.add_argument("--to", dest="day_to")
    p.add_argument("--windows",
                   help="comma-separated window lengths in days (e.g. "
                        "7,14,30) anchored at --to; rolling survival mode")
    p.add_argument("--json", action="store_true")
    p.add_argument("--min-settled", type=int, default=None)
    p.add_argument("--min-days", type=int, default=None)
    p.add_argument("--min-fixtures", type=int, default=None)
    # Guard knobs default to None so EXPLICIT use is detectable: in
    # --windows mode any explicit relaxation (sample threshold OR guard)
    # demotes survivors to exploratory-only.
    p.add_argument("--watch-min-settled", type=int, default=None)
    p.add_argument("--max-day-concentration", type=float, default=None)
    p.add_argument("--max-fixture-concentration", type=float, default=None)
    p.add_argument("--max-pending-share", type=float, default=None)
    p.add_argument("--top", type=int, default=15)
    p.add_argument("--all-runs", action="store_true")
    p.add_argument("--root", type=Path, default=None)
    args = p.parse_args(argv)

    if args.date and (args.day_from or args.day_to):
        p.error("use either --date or --from/--to, not both")
    if args.windows and (args.date or args.day_from):
        p.error("--windows takes only --to as anchor (no --date/--from)")

    settled = _settled_for(args.root)
    guard_flags = dict(watch_min_settled=args.watch_min_settled,
                       max_day_concentration=args.max_day_concentration,
                       max_fixture_concentration=args.max_fixture_concentration,
                       max_pending_share=args.max_pending_share)
    guards_overridden = any(v is not None for v in guard_flags.values())
    # explicit values where given, module defaults otherwise
    common = {k: v for k, v in guard_flags.items() if v is not None}

    if args.windows:
        if not args.day_to:
            p.error("--windows requires --to as the anchor date")
        try:
            windows = [int(w) for w in str(args.windows).split(",") if w]
        except ValueError:
            p.error("--windows must be comma-separated integers")
        if not windows or any(w < 1 for w in windows):
            p.error("--windows lengths must be positive integers")
        overrides = {k: v for k, v in (
            ("min_settled", args.min_settled), ("min_days", args.min_days),
            ("min_fixtures", args.min_fixtures)) if v is not None}
        report = seg.build_rolling_report(
            args.day_to, windows=windows, root=args.root, settled=settled,
            all_runs=args.all_runs, threshold_overrides=overrides or None,
            guards_overridden=guards_overridden,
            top_n=args.top, **common)
        if args.json:
            print(json.dumps(report, indent=2, default=str, sort_keys=True))
        else:
            print(seg.render_rolling_report(report))
        return 0

    if args.date:
        days = [str(args.date)[:10]]
    elif args.day_from and args.day_to:
        days = seg.date_range(args.day_from, args.day_to)
    else:
        p.error("provide --date, both --from and --to, or --windows + --to")

    report = seg.build_segment_report(
        days, root=args.root, settled=settled, all_runs=args.all_runs,
        min_settled=(args.min_settled if args.min_settled is not None else 30),
        min_days=(args.min_days if args.min_days is not None else 3),
        min_fixtures=(args.min_fixtures if args.min_fixtures is not None
                      else 20),
        top_n=args.top, **common)

    if args.json:
        print(json.dumps(report, indent=2, default=str, sort_keys=True))
    else:
        print(seg.render_segment_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
