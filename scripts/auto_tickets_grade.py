#!/usr/bin/env python3
"""Auto-grade the ROLLING auto-tickets (replacement for the v4 grader).

The rolling engine (auto_tickets.py) is stateful and settles its own slips;
this script is the report writer the pipeline expects as the second step:
it settles anything settleable, then writes localdata/auto_tickets_performance
.txt/.json from the engine state (bank, withdrawn, wealth, take-profit
events, per-day history).

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
    wealth = at.wealth(st)
    mult = wealth / st["initial_bank"]

    lines = ["AUTO-TICKETS (ROLLING) PERFORMANCE", "=" * 62,
             f"generated {datetime.now().isoformat(timespec='seconds')}",
             f"initial bank {st['initial_bank']:.2f} · bank {st['bank']:.2f} · "
             f"withdrawn {st['withdrawn']:.2f} · wealth {wealth:.2f} (x{mult:.2f})",
             f"bet-days {len(st['history'])} · accas {wins}W/{len(accas)-wins}L "
             f"(hit {wins/len(accas):.1%})" if accas else "no settled accas yet",
             f"open slips {len(st['open_slips'])} · take-profit at "
             f"{st['initial_bank']*at.TAKE_PROFIT_MULT:.2f} "
             f"({len(st.get('events', []))} trigger(s) to date)",
             "",
             "--- bet-days (most recent first) ---"]
    for h in reversed(st["history"][-args.last:]):
        acc = " ".join(f"@{a['odds']:.2f}{'W' if a['won'] else 'L'}" for a in h["accas"])
        lines.append(f"  {h['date']}  {acc:44s} bank {h['bank']:8.2f} (out {h['withdrawn']:7.2f})")
    for e in st.get("events", []):
        lines.append(f"  💰 {e['date']}: TAKE PROFIT — withdrew {e['withdrawn']:.2f}, "
                     f"bank reset to {e['bank_after']:.2f}")

    txt = "\n".join(lines)
    print()
    print(txt)
    (LOCALDATA / "auto_tickets_performance.txt").write_text(txt + "\n")
    (LOCALDATA / "auto_tickets_performance.json").write_text(json.dumps({
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "initial_bank": st["initial_bank"], "bank": st["bank"],
        "withdrawn": st["withdrawn"], "wealth": wealth, "multiple": mult,
        "bet_days": len(st["history"]),
        "accas": {"wins": wins, "losses": len(accas) - wins},
        "open_slips": [{"date": s["date"], "staked": s["staked"]} for s in st["open_slips"]],
        "events": st.get("events", []),
        "history": st["history"],
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
