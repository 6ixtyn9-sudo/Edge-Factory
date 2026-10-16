#!/usr/bin/env python3
"""Report the ROLLING auto-tickets performance — PERCENT-ONLY (no amounts).

Settles anything settleable via the engine, then writes a report for one lane:

  --lane main (default)  localdata/auto_tickets_performance.txt/.json
  --lane enh             localdata/autobets_enh_tickets_performance.txt/.json

Each report gives bank as % of capital, performance multiple, acca record,
and any TAKE-PROFIT NOTIFICATION events. Both lanes share one layout.
The enhancement lane's state is gitignored runtime state, so its report only
exists where that state is.

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
    "enh": (at.ENHANCEMENT_LANE, "ENHANCEMENT TICKETS (ROLLING)", "autobets_enh_tickets_performance"),
}


# ---------------------------------------------------------------------------
# One layout for both lanes; only the label and file stem differ.
# ---------------------------------------------------------------------------

_LEG_TAG = {"win": "WON", "loss": "LOST", "void": "VOID", "conflict": "HELD"}


def _leg_results(a):
    """Per-leg result tags for an acca: stored results first, then the leg record."""
    legs = a.get("legs") or []
    results = a.get("results")
    out = []
    for i, leg in enumerate(legs):
        if results is not None and i < len(results):
            out.append(results[i])
        else:
            out.append(leg.get("result") if isinstance(leg, dict) else None)
    return out


def _main_acca_block(a, held=False):
    """One acca: its stake and result on one line, then its legs indented under it."""
    odds = a.get("odds")
    odds_txt = f"@{odds:.2f}" if isinstance(odds, (int, float)) else "@n/a"
    stake = a.get("stake_pct")
    stake_txt = f"stake {stake:.1f}%" if stake is not None else "stake not recorded"
    if held:
        head = f"    ACCA {odds_txt:<7} {stake_txt:<20} HELD (not settled)"
    elif a.get("won") is None:
        head = f"    ACCA {odds_txt:<7} {stake_txt:<20} open"
    else:
        verdict = "WON" if a["won"] else "LOST"
        ret = a.get("returned_pct")
        if ret is None:
            ret = (round(stake * odds, 4)
                   if a["won"] and stake is not None and isinstance(odds, (int, float)) else 0.0)
        net_txt = f"net {ret - stake:+.1f}%" if stake is not None else ""
        head = f"    ACCA {odds_txt:<7} {stake_txt:<20} {verdict:<4}  {net_txt}"
    out = [head]
    legs = a.get("legs")
    if legs is None:
        return out  # settled before leg detail was recorded
    res = _leg_results(a)
    for leg, r in zip(legs, res):
        if leg.get("label"):
            pick = str(leg["label"])
        else:
            pick = str(leg.get("pick") or "").upper()
        price = leg.get("odds")
        price_txt = f"@{float(price):.2f}" if isinstance(price, (int, float)) else ""
        tag = _LEG_TAG.get(r, "open")
        out.append(f"      {tag:<5}{str(leg.get('match') or ''):<48} {pick} {price_txt}")
    if not held and a.get("won") is False:
        culprit = next((l for l, r in zip(legs, res) if r == "loss"), None)
        if culprit is not None:
            out.append(f"      lost on: {culprit.get('match')} "
                       f"({culprit.get('pick') or culprit.get('label')})")
    return out


def _bank_breaks(history):
    """Index -> (previous close, this day's open) wherever the stored bank does not carry over."""
    breaks = {}
    for i in range(1, len(history)):
        prev_end = history[i - 1]["bank_pct"]
        h = history[i]
        staked = h.get("staked_pct", 0.0)
        returned = h.get("returned_pct", 0.0)
        opens = h["bank_pct"] - returned + staked
        if abs(opens - prev_end) > 0.05:
            breaks[i] = (prev_end, opens)
    return breaks


def render_lines(st, label, last, held, accas, wins, generated):
    """The performance report: summary block, then bet-days newest first."""
    multiple = st["bank"] / st["base_pct"]
    history = st["history"]
    breaks = _bank_breaks(history)
    rows = []
    add = rows.append
    add(f"{label} — performance, percent of capital")
    add("=" * 62)
    add(f"generated {generated}")
    add("")
    add(f"BANK     {st['bank']:.1f}%   x{multiple:.2f} of the {st['base_pct']:.0f}% base")
    add(f"CYCLE    baseline {st['cycle_base']:.1f}%   next take-profit notice at "
        f"{at.take_profit_target(st):.1f}%   (+{at.TAKE_PROFIT_GAIN:.0%} per cycle)")
    if accas:
        add(f"RECORD   {wins}W / {len(accas) - wins}L   ({wins / len(accas):.1%} hit)   "
            f"over {len(history)} bet-days")
    else:
        add("RECORD   no settled accas yet")
    add(f"OPEN     {len(st['open_slips'])} open slips   {len(held)} held accas   "
        f"{len(st.get('events', []))} take-profit notice(s) to date")
    add("")
    start = max(0, len(history) - last)
    add(f"BET-DAYS, newest first (last {len(history) - start})")
    for i in reversed(range(start, len(history))):
        h = history[i]
        staked = h.get("staked_pct", 0.0)
        returned = h.get("returned_pct", 0.0)
        opens = h["bank_pct"] - returned + staked
        add(f"  {h['date']}   staked {staked:5.1f}%   returned {returned:5.1f}%   "
            f"net {returned - staked:+6.1f}%   bank {opens:.1f}% -> {h['bank_pct']:.1f}%")
        if i in breaks:
            prev_end, opens_at = breaks[i]
            add(f"  ! bank break: previous bet-day closed at {prev_end:.1f}%, this one opens at "
                f"{opens_at:.1f}% (gap {opens_at - prev_end:+.1f} pts). Stored bank values disagree.")
        for a in h["accas"]:
            rows.extend(_main_acca_block(a))
        add("")
    if held:
        add("HELD (not yet settled; stake counted as committed)")
        for slip, a in held:
            add(f"  {slip['date']}")
            rows.extend(_main_acca_block(dict(a, won=None), held=True))
            conflicts = [l.get("match") for l, r in zip(a["legs"], a.get("results") or [])
                         if r == "conflict"]
            if conflicts:
                add("      reason: donor spellings disagree on the outcome of "
                    + ", ".join(str(c) for c in conflicts))
        add("")
    events = st.get("events", [])
    if events:
        add("TAKE-PROFIT NOTICES")
        for e in events:
            add(f"  {e['date']}   +{e['gain_pct']:.1f}% that cycle   "
                f"-> bank {e['bank_after_pct']:.1f}%, next target {e['next_target_pct']:.1f}%")
        add("")
    add("KEY  Stake and returned are % of capital. Each leg reads WON / LOST / VOID / HELD.")
    add("     'lost on' names the leg that decided an acca. '!' marks a bank break.")
    add("     Bet-days recorded before leg detail was kept show the acca result only.")
    return [r.rstrip() for r in rows]


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
    generated = datetime.now().isoformat(timespec="seconds")
    lines = render_lines(st, label, args.last, held, accas, wins, generated)
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
