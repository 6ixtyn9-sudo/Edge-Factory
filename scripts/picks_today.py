#!/usr/bin/env python3
"""Daily picks: fetch today+tomorrow live from forebet/zulubet/statarea,
apply ONLY certified rules (consensus unanimous + veto), emit a slip.

    python3 scripts/picks_today.py            # today + tomorrow
    python3 scripts/picks_today.py 2026-06-12 # specific day
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.sources import forebet, statarea, zulubet  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402

# Certified consensus thresholds (walk-forward survivors, re-validated 2026-06-11)
T2 = 70.0   # 2-way unanimous avg prob — VALID 87.0% (LB .823), +4.7% ROI, n=247
T3 = 65.0   # 3-way unanimous avg prob — VALID 81.8% (LB .777), n=401


def top_pick(p1, px, p2):
    if p1 is None:
        return None, None
    best = max(p1, px, p2)
    sel = "home" if best == p1 else ("draw" if best == px else "away")
    return sel, best


def key(home, away):
    return norm_team(home), norm_team(away)


def run_day(day: str):
    fb = {key(r["home"], r["away"]): r for r in forebet.fetch_day(day)
          if r.get("status") != "FT"}
    zb = {key(r["home"], r["away"]): r for r in zulubet.fetch_day(day)
          if r.get("hs") is None}
    sa = {key(r["home"], r["away"]): r for r in statarea.fetch_day(day)
          if r.get("hs") is None}

    picks, vetoes = [], 0
    for k, f in fb.items():
        if len(k[0]) < 4 or len(k[1]) < 4 or k not in zb:
            continue
        fsel, fp = top_pick(f.get("p1"), f.get("px"), f.get("p2"))
        z = zb[k]
        zsel, zp = top_pick(z.get("p1"), z.get("px"), z.get("p2"))
        if fsel is None or zsel is None:
            continue
        if fsel != zsel:
            vetoes += 1
            continue  # VETO: disagreement = 33% land, never bet
        s = sa.get(k)
        ssel = sp = None
        if s:
            ssel, sp = top_pick(s.get("p1"), s.get("px"), s.get("p2"))
        n_way = 3 if (ssel == fsel and sp is not None) else 2
        avg_p = (fp + zp + sp) / 3 if n_way == 3 else (fp + zp) / 2
        rule = None
        if n_way == 3 and avg_p >= T3:
            rule = f"3WAY-UNANIMOUS≥{T3:.0f}"
        elif avg_p >= T2:
            rule = f"2WAY-UNANIMOUS≥{T2:.0f}"
        if not rule:
            continue
        odds = {"home": f.get("odd1"), "draw": f.get("oddx"),
                "away": f.get("odd2")}.get(fsel)
        picks.append({
            "date": day, "match": f"{f['home']} vs {f['away']}",
            "league": f.get("league"), "pick": fsel, "avg_p": round(avg_p, 1),
            "odds": odds, "rule": rule, "n_way": n_way,
        })
    picks.sort(key=lambda r: -r["avg_p"])
    return picks, vetoes, len(fb)


def main():
    days = sys.argv[1:] or [
        date.today().isoformat(),
        (date.today() + timedelta(days=1)).isoformat(),
    ]
    all_picks = []
    for day in days:
        picks, vetoes, n_fb = run_day(day)
        print(f"\n=== {day} — {len(picks)} certified picks "
              f"({vetoes} vetoed by disagreement, {n_fb} upcoming fb matches) ===")
        for p in picks:
            o = f"@{p['odds']:.2f}" if p.get("odds") else "@n/a"
            print(f"  [{p['rule']}] {p['match']:45s} -> {p['pick'].upper():5s} "
                  f"avg {p['avg_p']:.0f}% {o}  ({p['league']})")
        all_picks += picks
    if not all_picks:
        print("\nNo certified picks. That is a feature, not a bug — no edge, no bet.")
    print("\n⚠️  'Best odds' overstate realizable ROI (~halve it at a real book)."
          "\n⚠️  Flat stakes, never chase. Bet only what you can afford to lose.")


if __name__ == "__main__":
    main()
