#!/usr/bin/env python3
"""Report the ROLLING auto-tickets performance — PERCENT-ONLY (no amounts).

Settles anything settleable via the engine, then writes
localdata/auto_tickets_performance.txt/.json: bank as % of capital,
performance multiple, acca record, and any TAKE-PROFIT NOTIFICATION events.

Usage:
  PYTHONPATH=src python3 scripts/auto_tickets_grade.py
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--last", type=int, default=15, help="bet-days to show in the txt report")
    args = ap.parse_args()

    st = at.load_state()
    if not st:
        print("no rolling state yet — run scripts/auto_tickets.py first")
        return 0
    for line in at.settle_open_slips(st, at.load_settled()):
        print(line)

    accas = [a for h in st["history"] for a in h["accas"]]
    wins = sum(1 for a in accas if a["won"])
    multiple = st["bank"] / st["base_pct"]

    lines = ["AUTO-TICKETS (ROLLING) PERFORMANCE — percentages of capital only", "=" * 62,
             f"generated {datetime.now().isoformat(timespec='seconds')}",
             f"bank {st['bank']:.1f}% of capital (x{multiple:.2f}) · "
             f"cycle baseline {st['cycle_base']:.1f}% · "
             f"next take-profit notification at {at.take_profit_target(st):.1f}% "
             f"(+{at.TAKE_PROFIT_GAIN:.0%} per cycle)",
             (f"bet-days {len(st['history'])} · accas {wins}W/{len(accas)-wins}L "
              f"(hit {wins/len(accas):.1%})") if accas else "no settled accas yet",
             f"open slips {len(st['open_slips'])} · "
             f"{len(st.get('events', []))} take-profit notification(s) to date",
             "",
             "--- bet-days (most recent first) ---"]
    for h in reversed(st["history"][-args.last:]):
        acc = " ".join(f"@{a['odds']:.2f}{'W' if a['won'] else 'L'}" for a in h["accas"])
        lines.append(f"  {h['date']}  {acc:44s} bank {h['bank_pct']:7.1f}%")
    for e in st.get("events", []):
        lines.append(f"  🔔 {e['date']}: TAKE-PROFIT NOTIFICATION — +{e['gain_pct']:.1f}% that cycle "
                     f"(bank {e['bank_after_pct']:.1f}%, next target {e['next_target_pct']:.1f}%)")

    txt = "\n".join(lines)
    print()
    print(txt)
    (LOCALDATA / "auto_tickets_performance.txt").write_text(txt + "\n")
    (LOCALDATA / "auto_tickets_performance.json").write_text(json.dumps({
        "generated_at": datetime.now().isoformat(timespec="seconds"),
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
