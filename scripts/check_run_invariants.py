#!/usr/bin/env python3
"""Report contradictions between the artifacts an official run produced.

Read-only. It fixes nothing and decides nothing about betting; it only
says where two artifacts disagree. Exit code 0 always by default so a
diagnostic can never fail the pipeline, unless --strict is given.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from edgefactory import run_invariants  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--localdata", type=Path, default=ROOT / "localdata")
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero when an error-level "
                             "contradiction is found")
    args = parser.parse_args(argv)

    violations = run_invariants.check_run_from_localdata(
        args.date, args.localdata)
    for line in run_invariants.render_invariant_lines(violations):
        print(line)

    if args.strict and run_invariants.has_errors(violations):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
