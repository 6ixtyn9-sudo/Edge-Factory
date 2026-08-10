#!/usr/bin/env python3
"""heal_pick_labels.py — one-time sweep: rewrite stale display_rule in all
archived pick ledgers from the exact rule string (self-heal).

Why: rows archived before the honest-label fix (7f573b48ab) can carry a
pre-qualifier display_rule (e.g. "2WAY-UNANIMOUS>=60" for the bc-confirms
variant). The merge layer retains rows exactly, so the stored data stays
stale forever unless scrubbed. daily.py now self-heals on every write; this
script does the one-time historical sweep.

Only touches the display field. Never rule, odds, results, or performance.
Idempotent: re-running heals 0.

Usage:
    python3 scripts/heal_pick_labels.py
    python3 scripts/heal_pick_labels.py --localdata /path/to/localdata
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.util import heal_ledger_labels  # noqa: E402

GLOBS = ("picks_*.json", "picks_today.json", "picks_morning_*.json")


def main() -> int:
    ap = argparse.ArgumentParser(description="Self-heal stale pick display labels")
    ap.add_argument("--localdata", default=str(ROOT / "localdata"),
                    help="localdata dir (default: repo localdata)")
    args = ap.parse_args()

    ld = Path(args.localdata)
    files: list[Path] = []
    for g in GLOBS:
        files.extend(sorted(ld.glob(g)))
    files = sorted(set(files))
    if not files:
        print(f"no pick ledgers found in {ld}")
        return 1

    total_healed = 0
    changed_files = 0
    for path in files:
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"skip {path.name}: {exc}")
            continue
        if not isinstance(data, list):
            continue
        healed = heal_ledger_labels(data)
        if healed:
            path.write_text(json.dumps(data, indent=2, sort_keys=True))
            print(f"{path.name}: healed {healed} row(s)")
            total_healed += healed
            changed_files += 1
    print(f"\ndone: {total_healed} stale label(s) healed across {changed_files} file(s)")
    if total_healed == 0:
        print("everything already truthful")
    return 0


if __name__ == "__main__":
    sys.exit(main())
