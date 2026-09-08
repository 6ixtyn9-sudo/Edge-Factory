#!/usr/bin/env python3
"""Regenerate tests/data/engine_parity_baseline.json.

WHEN TO RUN THIS: only after a DELIBERATE, reviewed change to live leg
selection or staking. Never to make a red test go green. The whole value
of the baseline is that it fails when behaviour moves; regenerating it to
silence a failure you cannot explain destroys the only tripwire this
repository has against silent selection drift.

The commit that regenerates MUST name every intentional change folded in.

Day set: deliberately frozen to the days already in the baseline. The
point of the file is detecting unintended drift on a fixed population, not
tracking the archive as it grows -- and never including the current day,
which would be self-invalidating.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "tests" / "data" / "engine_parity_baseline.json"


def _engine():
    spec = importlib.util.spec_from_file_location(
        "at_regen", ROOT / "scripts" / "auto_tickets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def snapshot(mod, archives, days, bank_pct):
    """Must stay byte-identical in shape to _snapshot in the test."""
    out = {}
    for d in days:
        pool = mod.playable_legs(archives, day=d)
        plan = mod.plan_day(pool, bank_pct)
        out[d] = {
            "legs": [[[l["match"], l["pick"], round(l["odds"], 4)] for l in a["legs"]]
                     for a in plan],
            "staked": round(sum(a["stake_pct"] for a in plan), 6),
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--note", required=True,
                    help="what intentional change is being folded in, and why")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    old = json.loads(BASELINE.read_text())
    days = sorted(old["days"])
    bank = old.get("bank_pct", 100.0)
    at = _engine()
    new_days = snapshot(at, at.load_archived_picks(), days, bank)

    moved_legs = [d for d in days if new_days[d]["legs"] != old["days"][d]["legs"]]
    moved_stake = [d for d in days
                   if abs(new_days[d]["staked"] - old["days"][d]["staked"]) > 1e-9]
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()

    print(f"old base_commit : {old.get('base_commit')}")
    print(f"new base_commit : {head}")
    print(f"days            : {len(days)} (frozen)")
    print(f"leg selection moved on : {len(moved_legs)} day(s)")
    print(f"total staked moved on  : {len(moved_stake)} day(s)")
    if moved_legs[:8]:
        print(f"  first few: {moved_legs[:8]}")
    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0

    BASELINE.write_text(json.dumps({
        "bank_pct": bank,
        "base_commit": head,
        "generated_note": args.note,
        "days": new_days,
    }, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {BASELINE.relative_to(ROOT)}")
    print("the tripwire is armed again: any FURTHER selection change now fails.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
