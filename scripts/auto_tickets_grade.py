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
      - legacy "singles" tolerated (v1-v3 era only — operator's current
        plan has no singles).
    Returns (tickets, legacy_dates). legacy_dates is the set of slip
    dates whose JSON either has a "singles" array (v1-v3) or lacks
    a "stakes_frac" field (pre-b1c1946 era, the adaptive-deployment
    generator). The grader treats those dates honestly: the per-day
    display reports "stake not recorded" with a transparent
    "(pre-adaptive slip, see bookmaker history)" note because the
    actual rand amount is not recoverable from the slip alone.
    New slips (with stakes_frac) display normally as
    percent-of-capital.

    The per-ticket stake is read from stakes_frac when present, and
    is None for legacy slips. The 526116e "staked 100% of capital"
    bug came from rendering a unit 1.0 stake as a percent; we now
    refuse to render a percent for legacy dates. No currency
    amounts anywhere; the operator's directive is "38% is a
    ceiling, not a target" and "all slips as percent of capital" —
    we honour both by refusing to invent numbers the slip does not
    record.
    """
    tickets = []
    legacy_dates: set[str] = set()
    for f in sorted(LOCALDATA.glob("auto_tickets_*.json")):
        d = f.name.replace("auto_tickets_", "").replace(".json", "")
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        # legacy singles (v1-v3 only) — stake was R1 fixed, but the
        # current operator plan has no singles, so the unit 1.0 is
        # NOT rendered as a percent of capital (would be meaningless).
        # The legacy_dates set ensures the per-day display says
        # "stake not recorded" for v1-v3 days too.
        singles = data.get("singles") or []
        if singles:
            legacy_dates.add(d)
            for l in singles:
                tickets.append({"date": d, "type": "single", "legs": [_leg_dict(l)],
                                "stake": None, "odds": float(l.get("odds") or 1.0)})
        sf = data.get("stakes_frac") or {}
        if not sf:
            # Pre-b1c1946 acca slip: the actual rand amount is not
            # recoverable from the slip alone (the adaptive pool_factor
            # was not recorded). Mark the date so the display says so.
            legacy_dates.add(d)
        acca2_entries = [e for e in (data.get("acca2") or [])
                         if isinstance(e, list) and e and isinstance(e[0], list)
                         and e[0]]
        acca10_legs = data.get("acca10") or []
        for entry in acca2_entries:
            legs, prod = entry[0], (entry[1] if len(entry) > 1 else None)
            stake = (float(sf.get("acca2_per_ticket"))
                     if sf.get("acca2_per_ticket") is not None else None)
            tickets.append({"date": d, "type": "acca2", "legs": [_leg_dict(l) for l in legs],
                            "stake": stake,
                            "odds": float(prod) if prod else None})
        if acca10_legs:
            stake = (float(sf.get("acca10"))
                     if sf.get("acca10") is not None else None)
            tickets.append({"date": d, "type": "acca10", "legs": [_leg_dict(l) for l in acca10_legs],
                            "stake": stake,
                            "odds": float(data.get("acca10_odds") or 0.0) or None})
    return tickets, legacy_dates


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
    tickets, legacy_dates = load_tickets()
    if args.since:
        tickets = [t for t in tickets if t["date"] >= args.since]

    per_day = defaultdict(lambda: {"n": 0, "wins": 0, "pending": 0, "losses": 0, "staked": 0.0, "returned": 0.0})
    per_type = defaultdict(lambda: {"n": 0, "wins": 0, "pending": 0, "losses": 0, "staked": 0.0, "returned": 0.0})
    detail = []
    for t in tickets:
        res, mult = grade(t, settled)
        st = per_day[t["date"]]
        tp = per_type[t["type"]]
        # Legacy tickets have stake=None; their per-day display says
        # "stake not recorded" and we omit them from the numeric
        # aggregates so the ROI calc isn't poisoned by invented stakes.
        stake_for_agg = t["stake"] if t["stake"] is not None else 0.0
        for bucket in (st, tp):
            bucket["n"] += 1
            bucket["staked"] += stake_for_agg
            if res == "WIN":
                bucket["wins"] += 1
                bucket["returned"] += stake_for_agg * mult
            elif res == "PENDING":
                bucket["pending"] += 1
            else:
                bucket["losses"] += 1
        detail.append({"date": t["date"], "type": t["type"], "result": res,
                       "odds": t["odds"], "stake": t["stake"],
                       "returned": stake_for_agg * mult if res == "WIN" else 0.0,
                       "legs": [f"{l['home']} vs {l['away']} {l['pick']} @{l['odds']:.2f}" for l in t["legs"]]})

    lines = ["AUTO-TICKET GRADING", "=" * 60]
    total_staked = total_ret = total_n = total_wins = total_pend = 0
    lines.append("\n--- per day ---")
    for d in sorted(per_day):
        s = per_day[d]
        roi = (s["returned"] - s["staked"]) / s["staked"] if s["staked"] else 0.0
        if d in legacy_dates:
            stake_txt = "stake not recorded (pre-adaptive slip, see bookmaker history)"
            ret_txt = "n/a"
            roi_txt = "n/a"
        else:
            stake_txt = f"staked {s['staked']:.2%} of capital"
            ret_txt = f"returned {s['returned']:.2%}"
            roi_txt = f"ROI {roi:+.1%}"
        lines.append(f"  {d}: {s['n']} tickets ({s['wins']}W/{s['losses']}L/{s['pending']}P) "
                     f"{stake_txt} {ret_txt} {roi_txt}")
        total_staked += s["staked"]; total_ret += s["returned"]
        total_n += s["n"]; total_wins += s["wins"]; total_pend += s["pending"]
    lines.append("\n--- per type ---")
    # Per-type ROI only makes sense for new slips (where stakes_frac
    # is recorded). For legacy slips the stakes are unknown so the
    # per-type aggregate is "stake not recorded" too.
    has_any_legacy = bool(legacy_dates)
    for tp in ("single", "acca2", "acca10"):
        s = per_type[tp]
        if not s["n"]:
            continue
        if has_any_legacy:
            # If ANY day is legacy, all per-type aggregates that
            # include legacy tickets are mixed. For new-only days the
            # aggregate is clean; for mixed we say "stake not recorded"
            # when the type includes at least one legacy ticket.
            # Simpler: if any legacy exists, every type reports
            # "stake not recorded" (the operator can audit per-day).
            lines.append(f"  {TICKET_TYPES[tp]:12s}: {s['n']} tickets ({s['wins']}W/{s['losses']}L/{s['pending']}P) "
                         f"hit {s['wins']/s['n'] if s['n'] else 0:.0%} ROI n/a (includes legacy slip)")
        else:
            roi = (s["returned"] - s["staked"]) / s["staked"] if s["staked"] else 0.0
            lines.append(f"  {TICKET_TYPES[tp]:12s}: {s['n']} tickets ({s['wins']}W/{s['losses']}L/{s['pending']}P) "
                         f"hit {s['wins']/s['n'] if s['n'] else 0:.0%} ROI {roi:+.1%}")
    settled_n = total_n - total_pend
    if has_any_legacy:
        # Total ROI is mixed (some new, some legacy); report what's
        # known and flag the rest.
        total_roi = (total_ret - total_staked) / total_staked if total_staked else 0.0
        lines.append(f"\nTOTAL: {total_n} tickets, {total_wins}W, {total_pend} pending, "
                     f"settled hit {total_wins/settled_n if settled_n else 0:.1%}, "
                     f"new-slip ROI {total_roi:+.1%} (legacy slip stake not recorded)")
    else:
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
            # Returned amount is stake * odds. For new slips that's a
            # known percent of capital; for legacy slips it's omitted.
            if t["stake"] is not None:
                ret_pct = float(t["returned"]) if t["stake"] > 0 else 0.0
                # Note: t["stake"] is the per-ticket stake (a fraction
                # of capital for new slips), and t["returned"] is the
                # payout (stake * odds). For percent display we want
                # stake_pct = stake (already a fraction), returned_pct
                # = stake * odds. We have t["returned"] = stake * odds
                # directly, so the display is just that fraction.
                lines.append(f"  ✅ {t['date']} {t['type']:6s} @{(t['odds'] or 0.0):.2f} -> {ret_pct:.2%} of capital returned")
            else:
                lines.append(f"  ✅ {t['date']} {t['type']:6s} @{(t['odds'] or 0.0):.2f} -> returned (stake not recorded)")
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
    (LOCALDATA / "auto_tickets_performance.txt").write_text(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
