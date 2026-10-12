#!/usr/bin/env python3
"""R2 — the lane on the real slate, printing the derived floors and the verdicts.

Read-only demo of the shipped path: it drives the same calls the
`--enhancements` command makes (derive the day's floors, build the legs, render
the artifact) on the real slate in this workspace, with every localdata write
redirected to scratch by `handoff/scratch_localdata.py`. Nothing here is a
vendor call and nothing here writes the repository's state.

Writes `handoff/r2_lane_demo.txt`.
"""
from __future__ import annotations

import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import io
import json
import os
import pathlib
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

os.environ.setdefault("EDGE_FACTORY_ENH_BOARD", "1")


def main() -> int:
    out = io.StringIO()

    def say(line: str = "") -> None:
        out.write(line + "\n")

    from edgefactory.enh_registry import ENHANCEMENT_FLOOR_MARGIN, derive_floors_for_day
    from scripts import auto_tickets as at

    say("== R2 lane demo: derived floors on the real slate ==")
    say(f"  flag                : EDGE_FACTORY_ENH_BOARD={os.environ.get('EDGE_FACTORY_ENH_BOARD')} "
        f"(lane enabled: {at.enhancement_board_enabled()})")
    say(f"  margin              : ENHANCEMENT_FLOOR_MARGIN={ENHANCEMENT_FLOOR_MARGIN}")

    slate_path = at.LOCALDATA / "picks_today.json"
    slate = json.loads(slate_path.read_text())
    target = str((slate[0].get("date") if slate else "") or "")[:10] or "2026-10-11"
    say(f"  slate               : {slate_path} ({len(slate)} row(s), date {target})")

    floors = derive_floors_for_day(ROOT, target)
    say(f"  derived for         : {floors['as_of']} · margin {floors['margin']} · "
        f"min_n {floors['min_n']}")
    say(f"  registry coverage   : {json.dumps(floors['coverage'], sort_keys=True)}")
    say(f"  applied floors      : {json.dumps({k: v for k, v in sorted(floors['floors'].items()) if '|' not in k}, sort_keys=True)}")

    legs = at.enhancement_legs(slate, floors=floors)
    say("")
    say("-- every leg the lane saw, with the floor it was gated against --")
    for leg in legs:
        price = f"{leg['price']:.2f}" if leg["price"] is not None else "-"
        floor = f"{leg['floor']:.4f}" if leg["floor"] is not None else "none"
        say(f"  {leg['verdict']:12s} {str(leg['match'])[:34]:34s} {leg['market']:16s} "
            f"price {price:>5s} floor {floor:>8s} basis {leg['floor_basis']:9s} "
            f"league {str(leg.get('league'))[:28]}")

    st = at.load_state(at.ENHANCEMENT_LANE) or at.fresh_state()
    bank_eff = at.effective_bank(st, exclude_date=target)
    say("")
    say(f"-- the artifact the lane renders (state bank {st['bank']:.1f}%, "
        f"free {bank_eff:.1f}%) --")
    txt = at.render_enhancement_tickets(
        st, target, legs, [], datetime.now(at.TZ), should_freeze=False,
        freeze_record=None, bank_eff=bank_eff, fixture_report={}, floors=floors)
    say(txt)

    say("")
    say("-- what the lane would persist for the day --")
    table = {k: floors.get(k) for k in ("as_of", "margin", "min_n", "floors", "counts",
                                        "coverage")}
    say(f"  state key 'enh_floor_table' keys: {sorted(table)}")
    say(f"  deviating slices: {json.dumps(floors['counts'], sort_keys=True)}")

    text = out.getvalue()
    print(text, end="")
    (ROOT / "handoff/r2_lane_demo.txt").write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
