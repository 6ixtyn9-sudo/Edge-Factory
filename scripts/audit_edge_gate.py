#!/usr/bin/env python3
"""Edge-gate EVIDENCE audit (read-only): stated edge vs realized result.

Answers one question for the operator's gate decision: "if carded legs had
been filtered on their OWN stated edge (prob x captured odds - 1) at print
time, what would the ledger have done?" NOTHING is gated by this script —
it reads the committed slice ledger (localdata/auto_tickets_slice_ledger.jsonl)
and grades each leg with the SAME settlement machinery the tickets use
(auto_tickets.load_settled + pick_result), then prints markdown evidence.

Populations:
  - slip   (src=="slip", seeded==False): legs that actually rode on cards.
  - replay (src=="replay", seeded==True): backfill reconstruction — context
    for calibration only, never money.

Output: `python3 scripts/audit_edge_gate.py` (markdown to stdout).
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402

LEDGER = ROOT / "localdata" / "auto_tickets_slice_ledger.jsonl"
EDGE_BUCKETS = [(-1.0, -0.05, "< -5 pts"), (-0.05, 0.0, "-5..0 pts"),
                (0.0, 0.02, "0..+2 pts"), (0.02, 0.05, "+2..+5 pts"),
                (0.05, 9.0, "> +5 pts")]
GATE_THRESHOLDS = [None, 0.00, 0.02, 0.05]


def _grade(rows, settled, entries_by_date):
    out = []
    for r in rows:
        pick = {"date": r["date"], "home": r["home"], "away": r["away"],
                "kickoff": "", "pick": str(r["pick"]).lower()}
        if at.alias_outcome_conflict(pick, entries_by_date):
            result = "conflict"
        else:
            result = at.pick_result(pick, settled) or "open"
        out.append({**r, "edge": r["prob_stated"] * r["odds"] - 1.0,
                    "result": result})
    return out


def _flat_roi(legs):
    g = [l for l in legs if l["result"] in ("win", "loss")]
    if not g:
        return 0, 0.0
    pnl = sum((l["odds"] - 1.0) if l["result"] == "win" else -1.0 for l in g)
    return len(g), pnl / len(g)


def _bucket_table(legs):
    print("| stated edge | legs | graded | hit% | avg stated prob | flat ROI/leg |")
    print("|---|---|---|---|---|---|")
    for lo, hi, label in EDGE_BUCKETS:
        grp = [l for l in legs if lo <= l["edge"] < hi or (label == "> +5 pts" and l["edge"] >= lo)]
        if not grp:
            print(f"| {label} | 0 | 0 | – | – | – |")
            continue
        g = [l for l in grp if l["result"] in ("win", "loss")]
        hit = f"{100 * sum(1 for l in g if l['result'] == 'win') / len(g):.1f}%" if g else "–"
        n, roi = _flat_roi(grp)
        avg_p = f"{sum(l['prob_stated'] for l in grp) / len(grp) * 100:.1f}%"
        print(f"| {label} | {len(grp)} | {len(g)} | {hit} | {avg_p} | "
              f"{roi * 100:+.1f}% |" if n else f"| {label} | {len(grp)} | 0 | – | {avg_p} | – |")


def _gate_table(legs):
    print("| min stated edge | legs kept | graded | hit% | flat ROI/leg | dropped-legs ROI |")
    print("|---|---|---|---|---|---|")
    for g0 in GATE_THRESHOLDS:
        if g0 is None:
            kept, dropped = legs, []
            label = "none (status quo)"
        else:
            kept = [l for l in legs if l["edge"] >= g0]
            dropped = [l for l in legs if l["edge"] < g0]
            label = f"≥ {g0 * 100:+.0f} pts"
        ng, roi = _flat_roi(kept)
        _, droi = _flat_roi(dropped)
        g = [l for l in kept if l["result"] in ("win", "loss")]
        hit = f"{100 * sum(1 for l in g if l['result'] == 'win') / len(g):.1f}%" if g else "–"
        print(f"| {label} | {len(kept)} | {ng} | {hit} | {roi * 100:+.1f}% | "
              f"{droi * 100:+.1f}% |")


def _leg_table(legs):
    print("| date | match | pick | prob | odds | stated edge | result | flat 1u |")
    print("|---|---|---|---|---|---|---|---|")
    for l in sorted(legs, key=lambda x: (x["date"], x["match"])):
        res = l["result"]
        pnl = f"{(l['odds'] - 1.0):+.2f}" if res == "win" else ("-1.00" if res == "loss" else "–")
        print(f"| {l['date']} | {l['match']} | {l['pick']} | {l['prob_stated'] * 100:.0f}% "
              f"| {l['odds']:.2f} | {l['edge'] * 100:+.1f} pts | {res} | {pnl} |")


def main():
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
    settled = at.load_settled()
    entries = at.load_settled_entries()
    pops = {
        "slip": _grade([r for r in rows if r.get("src") == "slip" and not r.get("seeded") and not r.get("shadow")],
                       settled, entries),
        "replay": _grade([r for r in rows if r.get("src") == "replay"],
                         settled, entries),
    }
    from datetime import date as _date
    print(f"# Edge-gate evidence — generated {_date.today().isoformat()} by scripts/audit_edge_gate.py")
    print()
    for name, legs in pops.items():
        title = ("Real-money slip legs (src=slip)" if name == "slip"
                 else "Replay-seeded legs (context only, not money)")
        counts = defaultdict(int)
        for l in legs:
            counts[l["result"]] += 1
        neg = sum(1 for l in legs if l["edge"] < 0)
        print(f"## {title}: {len(legs)} legs; graded {counts['win'] + counts['loss']}, "
              f"open {counts['open']}, void {counts['void']}, conflict-held {counts['conflict']}; "
              f"{neg} legs carded with NEGATIVE own-stated edge")
        print()
        print("### Stated-edge buckets\n")
        _bucket_table(legs)
        print("\n### Gate counterfactuals (leg-level flat staking, no re-pairing simulation)\n")
        _gate_table(legs)
        print()
        if name == "slip":
            print("### Full slip-leg detail\n")
            _leg_table(legs)
            print()


if __name__ == "__main__":
    main()
