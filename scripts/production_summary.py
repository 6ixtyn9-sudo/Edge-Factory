#!/usr/bin/env python3
"""Print the authoritative production summary for a run date.

Run this last, after auto_tickets, Supabase sync, CLV capture and
notification, so every field reflects what those stages actually did
rather than what the pick engine expected them to do.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.production_summary import production_final_summary  # noqa: E402

LOCALDATA = ROOT / "localdata"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="run date YYYY-MM-DD (default: today)")
    parser.add_argument("--localdata", type=Path, default=LOCALDATA)
    args = parser.parse_args(argv)
    print("\n".join(production_final_summary(args.date, args.localdata)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
