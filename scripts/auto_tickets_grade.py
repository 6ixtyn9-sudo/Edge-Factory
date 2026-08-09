#!/usr/bin/env python3
"""Auto-grade the tickets that auto_tickets.py generated.

Joins every auto_tickets_<date>.json with settled_results.json:
  - ticket = all legs settled? all wins -> WIN ; any loss -> LOSS ; else PENDING
  - draws count as loss (1x2)
  - aggregates per date, per ticket type (single / acca2 / acca10):
    staked, returned, hit rate, ROI — plus a cumulative rolling total.
Writes localdata/auto_tickets_performance.json and prints a report.

Usage:
  PYTHONPATH=src python3 scripts/auto_tickets_grade.py
  PYTHONPATH=src python3 scripts/auto_tickets_grade.py --since 2026-08-09
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
LOCALDATA = ROOT / "localdata"

TICKET_TYPES = {"single": "single", "acca2": "2-odd acca", "acca10": "10-odd acca"}


def load_settled():
    from edgefactory.util import norm_team
    try:
        data = json.loads((LOCALDATA / "settled_results.json").read_text())
    except Exception:
        return {}
    out = {}
    for r in data.get("rows", []):
        key = (str(r.get("date") or "")[:10], norm_team(r.get("home") or ""), norm_team(r.get("away") or ""))
        out[key] = r.get("outcome")
    return out


def _leg_dict(l):
    match = str(l.get("match") or "")
    parts = match.split(" vs ")
    return {
        "home": l.get("home") or (parts[0] if parts else ""),
        "away": l.get("away") or (parts[1] if len(parts) > 1 else ""),
        "pick": str(l.get("pick") or "").lower(),
        "odds": float(l.get("odds") or 1.0),
    }


def load_tickets():
    """auto_tickets_<date>.json -> list of (date, type, legs, stake, odds)

    Handles the v4 schema:
      - "acca2":   list of [ [leg, leg], product ]  (pairs with their total odds)
      - "acca10":  list of legs (total odds in "acca10_odds")
      - legacy "singles" tolerated.
    """
    tickets = []
    for f in sorted(LOCALDATA.glob("auto_tickets_*.json")):
        d = f.name.replace("auto_tickets_", "").replace(".json", "")
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        # legacy singles (v1-v3 only)
        for l in (data.get("singles") or []):
            tickets.append({"date": d, "type": "single", "legs": [_leg_dict(l)],
                            "stake": 1.0, "odds": float(l.get("odds") or 1.0)})
        # acca2 entries: [ [legs...], product ]
        for entry in (data.get("acca2") or []):
            if isinstance(entry, list) and entry and isinstance(entry[0], list):
                legs, prod = entry[0], (entry[1] if len(entry) > 1 else None)
            elif isinstance(entry, list):
                legs, prod = entry, None
            else:
                continue
            if not legs:
                continue
            tickets.append({"date": d, "type": "acca2", "legs": [_leg_dict(l) for l in legs],
                            "stake": 1.0, "odds": float(prod) if prod else None})
        # acca10 legs
        legs = data.get("acca10") or []
        if legs:
            tickets.append({"date": d, "type": "acca10", "legs": [_leg_dict(l) for l in legs],
                            "stake": 1.0,
                            "odds": float(data.get("acca10_odds") or 0.0) or None})
    return tickets


def grade(ticket, settled):
    """-> ('WIN'|'LOSS'|'PENDING', payout_multiplier)"""
    from edgefactory.util import norm_team
    for leg in ticket["legs"]:
        key = (ticket["date"], norm_team(leg["home"]), norm_team(leg["away"]))
        outcome = settled.get(key)
        if outcome is None:
            return "PENDING", 0.0
        sel = leg["pick"]
        if outcome == "draw":
            return "LOSS", 0.0
        if outcome != sel:
            return "LOSS", 0.0
    return "WIN", ticket["odds"] or 1.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None, help="only grade tickets on/after this date")
    args = ap.parse_args()

    settled = load_settled()
    tickets = load_tickets()
    if args.since:
        tickets = [t for t in tickets if t["date"] >= args.since]

    per_day = defaultdict(lambda: {"n": 0, "wins": 0, "pending": 0, "losses": 0, "staked": 0.0, "returned": 0.0})
    per_type = defaultdict(lambda: {"n": 0, "wins": 0, "pending": 0, "losses": 0, "staked": 0.0, "returned": 0.0})
    detail = []
    for t in tickets:
        res, mult = grade(t, settled)
        st = per_day[t["date"]]
        tp = per_type[t["type"]]
        for bucket in (st, tp):
            bucket["n"] += 1
            bucket["staked"] += t["stake"]
            if res == "WIN":
                bucket["wins"] += 1
                bucket["returned"] += t["stake"] * mult
            elif res == "PENDING":
                bucket["pending"] += 1
            else:
                bucket["losses"] += 1
        detail.append({"date": t["date"], "type": t["type"], "result": res,
                       "odds": t["odds"], "stake": t["stake"],
                       "returned": t["stake"] * mult if res == "WIN" else 0.0,
                       "legs": [f"{l['home']} vs {l['away']} {l['pick']} @{l['odds']:.2f}" for l in t["legs"]]})

    lines = ["AUTO-TICKET GRADING", "=" * 60]
    total_staked = total_ret = total_n = total_wins = total_pend = 0
    lines.append(f"\n--- per day ---")
    for d in sorted(per_day):
        s = per_day[d]
        roi = (s["returned"] - s["staked"]) / s["staked"] if s["staked"] else 0.0
        lines.append(f"  {d}: {s['n']} tickets ({s['wins']}W/{s['losses']}L/{s['pending']}P) "
                     f"staked R{s['staked']:.2f} returned R{s['returned']:.2f} ROI {roi:+.1%}")
        total_staked += s["staked"]; total_ret += s["returned"]
        total_n += s["n"]; total_wins += s["wins"]; total_pend += s["pending"]
    lines.append(f"\n--- per type ---")
    for tp in ("single", "acca2", "acca10"):
        s = per_type[tp]
        if not s["n"]:
            continue
        roi = (s["returned"] - s["staked"]) / s["staked"] if s["staked"] else 0.0
        lines.append(f"  {TICKET_TYPES[tp]:12s}: {s['n']} tickets ({s['wins']}W/{s['losses']}L/{s['pending']}P) "
                     f"hit {s['wins']/s['n'] if s['n'] else 0:.0%} ROI {roi:+.1%}")
    settled_n = total_n - total_pend
    total_roi = (total_ret - total_staked) / total_staked if total_staked else 0.0
    lines.append(f"\nTOTAL: {total_n} tickets, {total_wins}W, {total_pend} pending, "
                 f"settled hit {total_wins/settled_n if settled_n else 0:.1%}, ROI {total_roi:+.1%}")
    if total_pend:
        lines.append(f"({total_pend} still pending settlement — grader re-runs each day)")
    lines.append("")
    for t in detail:
        if t["result"] == "PENDING":
            lines.append(f"  ⏳ {t['date']} {t['type']:6s} @{(t['odds'] or 0.0):.2f} — awaiting results")
    for t in detail:
        if t["result"] == "WIN":
            lines.append(f"  ✅ {t['date']} {t['type']:6s} @{(t['odds'] or 0.0):.2f} -> R{t['returned']:.2f}")
    for t in detail:
        if t["result"] == "LOSS":
            lines.append(f"  ❌ {t['date']} {t['type']:6s} @{(t['odds'] or 0.0):.2f}")

    txt = "\n".join(lines)
    print(txt)
    (LOCALDATA / "auto_tickets_performance.json").write_text(json.dumps({
        "generated_at": date.today().isoformat(),
        "total_tickets": total_n, "total_wins": total_wins, "total_pending": total_pend,
        "total_staked": total_staked, "total_returned": total_ret,
        "total_roi": (total_ret - total_staked) / total_staked if total_staked else 0.0,
        "per_day": per_day, "per_type": per_type, "detail": detail,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
