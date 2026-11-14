#!/usr/bin/env python3
"""Emit cheap daily Phase 5 clause status; never fit or emit a pick."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.phase5_certifier import run_status  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "localdata")
    parser.add_argument("--findings", type=Path, default=ROOT / "docs/operator/FINDINGS-2026-10-07.md")
    parser.add_argument("--as-of", type=date.fromisoformat, default=None)
    args = parser.parse_args()

    status = run_status(args.root, as_of=args.as_of, findings_path=args.findings)
    realized = ",".join(status["realized_s"]) or "none"
    projected = status["projected_90_day_maturity"] or "unavailable"
    print(
        f"PHASE5_CERTIFIER status={status['overall_status']} "
        f"realized_S={realized} projected_90d={projected} "
        f"full_eval={status['full_evaluation_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
