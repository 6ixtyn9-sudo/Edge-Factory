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
#
# The report shows what was stored. Nothing here recomputes the bank: each
# bet-day line carries its stored close. Bank breaks in the history are
# documented in docs/operator/BANK-HISTORY-2026-10-16.md, not re-derived here.
# ---------------------------------------------------------------------------

def _close(h) -> float:
    """A bet-day's stored end-of-day bank. Rows written before ``close_pct``
    existed carry only the settlement snapshot in ``bank_pct``."""
    return h.get("close_pct", h["bank_pct"])


def _day_line(h) -> str:
    accas = h.get("accas") or []
    wins = sum(1 for a in accas if a.get("won"))
    record = f"{wins}W/{len(accas) - wins}L" if accas else "-"
    staked = h.get("staked_pct", 0.0)
    returned = h.get("returned_pct", 0.0)
    return (f"  {h['date']}   {record:<7} staked {staked:5.1f}%   returned {returned:5.1f}%   "
            f"net {returned - staked:+6.1f}%   bank {_close(h):6.1f}%")


def _held_lines(slip, a):
    """One held acca: its stake, then its legs. Held accas have no result yet."""
    odds = a.get("odds")
    odds_txt = f"@{odds:.2f}" if isinstance(odds, (int, float)) else "@n/a"
    stake = a.get("stake_pct")
    stake_txt = f"stake {stake:.1f}%" if stake is not None else "stake not recorded"
    out = [f"  {slip['date']}   ACCA {odds_txt}   {stake_txt}   HELD (not settled)"]
    res = a.get("results") or []
    for leg in a.get("legs") or []:
        pick = str(leg.get("label") or leg.get("pick") or "").upper()
        price = leg.get("odds")
        price_txt = f"@{float(price):.2f}" if isinstance(price, (int, float)) else ""
        out.append(f"      {pick} {price_txt}".rstrip())
    if "conflict" in res:
        out.append("      reason: donor spellings disagree on the outcome of one leg")
    return out


def render_lines(st, label, last, held, accas, wins, generated):
    """The performance report: summary, one line per bet-day in date order,
    held accas, take-profit notices and a short notes block. ``last`` limits the
    bet-day table to the most recent N days; 0 or less shows every day."""
    multiple = st["bank"] / st["base_pct"]
    history = st["history"]
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
    ordered = sorted(history, key=lambda h: h["date"])  # stored order is not guaranteed
    start = max(0, len(ordered) - last) if last > 0 else 0
    shown = ordered[start:]
    add(f"BET-DAYS, oldest first ({len(shown)} of {len(history)})")
    for h in shown:
        add(_day_line(h))
    add("")
    if held:
        add("HELD (not yet settled; stake counted as committed)")
        for slip, a in held:
            rows.extend(_held_lines(slip, a))
        add("")
    events = st.get("events", [])
    if events:
        add("TAKE-PROFIT NOTICES")
        for e in events:
            add(f"  {e['date']}   +{e['gain_pct']:.1f}% that cycle   "
                f"-> bank {e['bank_after_pct']:.1f}%, next target {e['next_target_pct']:.1f}%")
        add("")
    add("NOTES")
    add("  Stake, returned and net are % of capital. Bank is the stored close for each day.")
    add("  Bank breaks in the history are documented in docs/operator/BANK-HISTORY-2026-10-16.md.")
    add("  Bet-days recorded before leg detail was kept show the acca result only.")
    return [r.rstrip() for r in rows]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lane", choices=sorted(LANES), default="main",
                    help="which lane to report (default: main)")
    ap.add_argument("--last", type=int, default=0, help="bet-days to show in the txt report (0 = all)")
    ap.add_argument("--no-settle", action="store_true", help="render current lane state only; no settlements")
    args = ap.parse_args(argv)

    lane, label, stem = LANES[args.lane]
    st = at.load_state(lane)
    if not st:
        if lane is None:
            print("no rolling state yet — run scripts/auto_tickets.py first")
        else:
            print(f"no {args.lane} lane state yet — nothing to report")
        return 0
    if not args.no_settle:
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
