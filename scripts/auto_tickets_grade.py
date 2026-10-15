#!/usr/bin/env python3
"""Report the ROLLING auto-tickets performance — PERCENT-ONLY (no amounts).

Settles anything settleable via the engine, then writes a report for one lane:

  --lane main (default)  localdata/auto_tickets_performance.txt/.json
  --lane enh             localdata/autobets_enh_performance.txt/.json

Each report gives bank as % of capital, performance multiple, acca record,
and any TAKE-PROFIT NOTIFICATION events. The enhancement lane's state is
gitignored runtime state, so its report only exists where that state is.

Usage:
  PYTHONPATH=src python3 scripts/auto_tickets_grade.py
  PYTHONPATH=src python3 scripts/auto_tickets_grade.py --lane enh
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402

LOCALDATA = ROOT / "localdata"

# lane name -> (state lane object or None for main, report label, report file stem)
LANES = {
    "main": (None, "AUTO-TICKETS (ROLLING)", "auto_tickets_performance"),
    "enh": (at.ENHANCEMENT_LANE, "ENHANCEMENT TICKETS (ROLLING)", "autobets_enh_performance"),
}


_RESULT_TAG = {"win": "WON ", "loss": "LOST", "void": "VOID", "conflict": "HELD",
               None: "open"}


def _leg_text(leg, result):
    """One leg line: result, match, pick and price, and the leg's own label."""
    pick = str(leg.get("pick") or "").upper()
    if leg.get("label"):
        pick = str(leg["label"])
    odds = leg.get("odds")
    price = f" @{float(odds):.2f}" if isinstance(odds, (int, float)) else ""
    return f"      {_RESULT_TAG.get(result, 'open'):4s}  {str(leg.get('match') or ''):44s} {pick}{price}"


def _acca_detail(a, held=False):
    """Stake, outcome and legs for one acca, as printed under its bet-day."""
    stake = a.get("stake_pct")
    if held:
        head = f"   ACCA @{a['odds']:.2f}  stake {stake:.1f}%  HELD (not settled)"
    elif a.get("won") is None:
        head = f"   ACCA @{a['odds']:.2f}  stake {stake:.1f}%  open"
    else:
        ret = a.get("returned_pct")
        if ret is None:
            ret = round(stake * a["odds"], 4) if a["won"] and stake is not None else 0.0
        net = ret - stake if stake is not None else None
        verdict = "WON " if a["won"] else "LOST"
        head = (f"   ACCA @{a['odds']:.2f}  stake {stake:.1f}%  {verdict}  net {net:+.1f}%"
                if stake is not None else f"   ACCA @{a['odds']:.2f}  {verdict}")
    out = [head]
    legs = a.get("legs")
    results = a.get("results")
    if legs is None:
        # Settlements from before leg detail was recorded: the header says so.
        return out
    # Held accas carry results beside the legs; settled history carries each
    # leg's own result on the leg record.
    res = [results[i] if results is not None and i < len(results)
           else (leg.get("result") if isinstance(leg, dict) else None)
           for i, leg in enumerate(legs)]
    for leg, r in zip(legs, res):
        out.append(_leg_text(leg, r))
    if not held and a.get("won") is False:
        culprit = next((l for l, r in zip(legs, res) if r == "loss"), None)
        if culprit is not None:
            out.append(f"      -> lost on: {culprit.get('match')} ({culprit.get('pick') or culprit.get('label')})")
    return out


def render_lines(st, label, last, held, accas, wins):
    """The performance report, one block per bet-day with each acca broken out."""
    multiple = st["bank"] / st["base_pct"]
    n_held = len(held)
    lines = [f"{label} PERFORMANCE — percentages of capital only", "=" * 62,
             f"generated {datetime.now().isoformat(timespec='seconds')}",
             f"bank {st['bank']:.1f}% of capital (x{multiple:.2f}) · "
             f"cycle baseline {st['cycle_base']:.1f}% · "
             f"next take-profit notification at {at.take_profit_target(st):.1f}% "
             f"(+{at.TAKE_PROFIT_GAIN:.0%} per cycle)",
             (f"bet-days {len(st['history'])} · accas {wins}W/{len(accas)-wins}L "
              f"(hit {wins/len(accas):.1%})") if accas else "no settled accas yet",
             f"open slips {len(st['open_slips'])} · held accas {n_held} · "
             f"{len(st.get('events', []))} take-profit notification(s) to date",
             "",
             "Each acca is listed on its bet-day with its stake and net result in",
             "percent of capital. Leg rows show WON / LOST / VOID / HELD for each leg;",
             "'-> lost on' names the leg that decided the acca. Bet-days from before",
             "leg detail was recorded show the acca result only.",
             "",
             "--- bet-days (most recent first) ---"]
    for h in reversed(st["history"][-last:]):
        staked = h.get("staked_pct", 0.0)
        returned = h.get("returned_pct", 0.0)
        before = h["bank_pct"] - returned + staked
        lines.append(f"  {h['date']}  staked {staked:.1f}% · returned {returned:.1f}% · "
                     f"net {returned - staked:+.1f}% · bank {before:.1f}% -> {h['bank_pct']:.1f}%")
        for a in h["accas"]:
            lines.extend(_acca_detail(a))
        lines.append("")
    if held:
        lines.append("--- held accas (not yet settled; stake counted as committed until it settles) ---")
        for slip, a in held:
            lines.append(f"  {slip['date']}")
            lines.extend(_acca_detail(dict(a, won=None, stake_pct=a["stake_pct"]), held=True))
            conflicts = [l.get("match") for l, r in zip(a["legs"], a.get("results") or []) if r == "conflict"]
            if conflicts:
                lines.append("      reason: donor spellings disagree on the outcome of "
                             + ", ".join(str(c) for c in conflicts))
        lines.append("")
    for e in st.get("events", []):
        lines.append(f"  🔔 {e['date']}: TAKE-PROFIT NOTIFICATION — +{e['gain_pct']:.1f}% that cycle "
                     f"(bank {e['bank_after_pct']:.1f}%, next target {e['next_target_pct']:.1f}%)")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lane", choices=sorted(LANES), default="main",
                    help="which lane to report (default: main)")
    ap.add_argument("--last", type=int, default=15, help="bet-days to show in the txt report")
    args = ap.parse_args(argv)

    lane, label, stem = LANES[args.lane]
    st = at.load_state(lane)
    if not st:
        if lane is None:
            print("no rolling state yet — run scripts/auto_tickets.py first")
        else:
            print(f"no {args.lane} lane state yet — nothing to report")
        return 0
    for line in at.settle_open_slips(st, at.load_settled(), lane=lane):
        print(line)

    accas = [a for h in st["history"] for a in h["accas"]]
    wins = sum(1 for a in accas if a["won"])
    held = [(slip, a) for slip in st["open_slips"] for a in slip["accas"]]
    lines = render_lines(st, label, args.last, held, accas, wins)
    multiple = st["bank"] / st["base_pct"]

    txt = "\n".join(lines)
    print()
    print(txt)
    (LOCALDATA / f"{stem}.txt").write_text(txt + "\n")
    (LOCALDATA / f"{stem}.json").write_text(json.dumps({
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "lane": args.lane,
        "unit": "percent_of_capital",
        "base_pct": st["base_pct"], "bank_pct": st["bank"], "multiple": multiple,
        "cycle_base_pct": st["cycle_base"],
        "next_take_profit_pct": round(at.take_profit_target(st), 2),
        "bet_days": len(st["history"]),
        "accas": {"wins": wins, "losses": len(accas) - wins},
        "open_slips": [{"date": s["date"], "staked_pct": s["staked_pct"]} for s in st["open_slips"]],
        "events": st.get("events", []),
        "history": st["history"],
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
