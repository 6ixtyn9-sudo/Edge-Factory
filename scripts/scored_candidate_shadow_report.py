#!/usr/bin/env python3
"""Read-only report over the scored-candidate shadow grading ledger.

Answers, from persisted state only: for a given date, what was the flat-stake
ROI of scored-but-rejected candidates — separately for execution-safe
rejected candidates and by rejection reason?

Usage:
    PYTHONPATH=src python3 scripts/scored_candidate_shadow_report.py --date YYYY-MM-DD
    ... --all-runs            # per-run diagnostics for draft reruns
    ... --json out.json       # also dump the machine-readable report
    ... --write-settlement    # append explicit settlement events to
                              # localdata/scored_candidate_shadow_settlement_<date>.jsonl
                              # (append-only; historical scored records are never mutated)

Settlement facts come from the SAME result donors the ticket grader uses
(warehouse donors + settled_results.json overlay + operator-verified scores),
but the join here is EXACT normalized fixture matching only: no fuzzy
matching, no alias scan, no reschedule window.  Unresolved candidates stay
``pending`` and unmatched ones ``unmatched`` — neither is ever a loss, and
both are excluded from every ROI denominator.

This tool never changes tickets, stakes, or any betting behaviour.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgefactory import scored_candidate_shadow as scs  # noqa: E402


def _settled_map(root: Path | None):
    """Exact settled-fact map. Prefer the full grader facts (warehouse +
    overlay + verified); fall back to the shared overlay file alone.

    When an explicit --root sandbox is given, stay hermetic: read only that
    root's settled_results.json overlay (exact keys), never the live
    warehouse — a test fixture must not be settled by production facts.
    """
    if root is not None:
        return scs.load_settled_overlay(root)
    try:
        import auto_tickets as at
        return at.load_settled()
    except Exception as exc:  # noqa: BLE001 - report must degrade, not die
        print(f"warn: full settled facts unavailable ({exc}); "
              "falling back to settled_results.json overlay only",
              file=sys.stderr)
        return scs.load_settled_overlay(root)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Read-only scored-candidate shadow grading report")
    ap.add_argument("--date", default=None,
                    help="trading date YYYY-MM-DD (default: today)")
    ap.add_argument("--all-runs", action="store_true",
                    help="include per-run diagnostics for draft reruns")
    ap.add_argument("--json", default=None,
                    help="also write the machine-readable report to this path")
    ap.add_argument("--write-settlement", action="store_true",
                    help="append explicit settlement events (append-only "
                         "sidecar file; scored records are never mutated)")
    ap.add_argument("--root", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()

    day = (args.date or date.today().isoformat())[:10]
    root = Path(args.root) if args.root else None

    ledger = scs.ledger_path(day, root)
    if not ledger.exists():
        print(f"no shadow ledger for {day}: {ledger} does not exist")
        print("(the picks build and ticket build append it automatically; "
              "nothing was persisted for this date)")
        return 1

    settled = _settled_map(root)
    report = scs.build_report(day, root=root, settled=settled,
                              all_runs=args.all_runs)
    print(scs.render_report(report))
    if args.all_runs and report.get("all_runs"):
        print("\nALL RUNS (diagnostics):")
        for rid, info in report["all_runs"].items():
            print(f"  {rid}: statuses={info['statuses']} "
                  f"selected_on_ticket={info['selected_on_ticket']}")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True,
                                  default=str))
        print(f"\njson report written: {out}")

    if args.write_settlement:
        events = scs.settlement_events(report)
        path = scs.settlement_path(day, root)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            for e in events:
                fh.write(json.dumps(e, sort_keys=True, default=str) + "\n")
        print(f"settlement events appended: {len(events)} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
