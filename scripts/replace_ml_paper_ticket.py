#!/usr/bin/env python3
"""Replace one explicitly named, still-unstarted PAPER ticket, never a live bet.

Uses the existing local forecast slates and price evidence at ACTUAL runtime.
Does not fetch providers, retimestamp quotes, edit old receipts, or reset banks.
If no supported fresh pair remains, the withdrawal is recorded without making
up a replacement. The original reservation is released, not scored as W/L.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at

from edgefactory import ml_paper


def load_existing_slate(root):
    rows, found = [], False
    for path in [root / "picks_today.json", *sorted(root.glob("picks_next_*days.json"))]:
        if not path.exists():
            continue
        source = json.loads(path.read_text())
        if not isinstance(source, list):
            raise TypeError(f"invalid existing forecast slate: {path.name}")
        rows.extend(source)
        found = True
    if not found:
        raise ValueError("no existing local forecast slate; no paper ticket changed")
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt-sha256", required=True, help="Exact ORIGINAL frozen paper receipt hash")
    parser.add_argument("--acca-index", type=int, required=True, help="Original publication-local ticket index (1-based)")
    parser.add_argument("--reason", required=True, help="Explicit operator reason, retained in the immutable replacement")
    args = parser.parse_args(argv)
    root = ROOT / "localdata"
    try:
        slate = load_existing_slate(root)
        lookup = at.ml_paper_score_lookup(at.load_settled_scores())
        row = ml_paper.capture_rolling(
            {"build_at": datetime.now(UTC).isoformat(), "slate": slate},
            root=root, score_lookup=lookup, kickoff_fn=at.parse_kickoff_proven,
            source_guard=at.execution_source_rejection,
            supersede=[{"receipt_sha256": args.receipt_sha256, "acca_index": args.acca_index}],
            replacement_reason=args.reason,
        )
        if row is None:
            raise ValueError("no replacement was published; original paper evidence is unchanged")
        ml_paper.publish(root, lookup)
        # publish already rendered the daily card. Do not load the entire
        # frozen history AGAIN just to print it (hundreds of MB in production).
        print((root / f"{ml_paper.PREFIX}_{row['date']}.txt").read_text())
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(f"PAPER replacement refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
