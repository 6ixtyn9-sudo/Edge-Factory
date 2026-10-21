#!/usr/bin/env python3
"""O2.5 research tracker — grades the goals surface on LIVE localdata.
Read-only: no engine interaction. Reports the checkpoint-3 gate:
  priced 50-60% band: n>=30 AND hit>=70% AND flat ROI>0 -> PASS
Run:  PYTHONPATH=src python3 scripts/o25_tracker.py
"""
import json, glob, re, sys, collections
from pathlib import Path
from datetime import datetime, timedelta
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "src"))
import auto_tickets as at
from edgefactory.util import norm_team, finite_probability, pick_probability_pct

def is_o25_enhancement(pick):
    market = pick.get("recommended_enhancement")
    if market:
        return market == "match_over_25"
    return "over 2.5" in str(pick.get("enhancement_label") or "").lower()


def is_o25_primary(pick):
    return pick.get("market") == "ou_2.5" and str(pick.get("pick")).lower() == "over"


def tracked_probability(pick):
    """Use the recorded O2.5 probability only; never borrow another market."""
    if is_o25_enhancement(pick):
        return finite_probability(pick.get("enhancement_probability"))
    if is_o25_primary(pick):
        observed = pick_probability_pct(pick)
        return observed / 100.0 if observed is not None else None
    return None


def main(root=ROOT):
    # score index with the engine's tolerant join (accents, +-1 day)
    raw = json.loads((root/"localdata/settled_results.json").read_text())["rows"]
    exact, folded = {}, collections.defaultdict(list)
    for r in raw:
        d = str(r.get("date"))[:10]
        h, a = norm_team(r.get("home") or ""), norm_team(r.get("away") or "")
        exact[(d, h, a)] = (r.get("hs"), r.get("gs"))
        folded[d].append((at._fold(h), at._fold(a), r.get("hs"), r.get("gs")))

    def score_for(day, home, away):
        h, a = norm_team(home), norm_team(away)
        if (day, h, a) in exact: return exact[(day, h, a)]
        try: base = datetime.strptime(day, "%Y-%m-%d").date()
        except ValueError: return None
        cands = [day, str(base - timedelta(days=1)), str(base + timedelta(days=1))]
        for d in cands:
            for fh, fa, hs, gs in folded.get(d, ()):
                if at._fold(h) == fh and at._fold(a) == fa: return (hs, gs)
        return None

    bets = []
    for f in sorted(glob.glob(str(root/"localdata/picks_2026-*.json"))):
        day = re.match(r"picks_(\S+-\d+-\d+)\.json", f.split("/")[-1]).group(1)
        for p in json.loads(open(f).read()):
            rule = str(p.get('edge_rule') or p.get('rule') or '')
            if not (is_o25_enhancement(p) or is_o25_primary(p)):
                continue
            sc = score_for(day, p.get("home"), p.get("away"))
            bets.append({"day": day,
                         "prob": tracked_probability(p),
                         "price": p.get("enhancement_price") if is_o25_enhancement(p) else p.get("odds"),
                         "src": p.get("enhancement_price_source") if is_o25_enhancement(p) else p.get("odds_source"),
                         "rule": rule[:34], "bucket": str(p.get("bucket") or "-"),
                         "sc": sc, "win": (sc[0]+sc[1] >= 3) if sc and all(v is not None for v in sc) else None})

    graded = [b for b in bets if b["win"] is not None]
    SHARP = {"theoddsapi", "betexplorer_odds"}
    window = f"{min(b['day'] for b in bets)}..{max(b['day'] for b in bets)}" if bets else "no listed overs"
    print(f"O2.5 TRACKER — graded {len(graded)}/{len(bets)} listed overs (window {window})")
    print(f"\n{'cut':34s} {'n':>4s} {'hit':>6s} {'stated':>11s} {'p_n':>4s} {'ROI':>7s}")
    def row(label, sel):
        rs = [b for b in graded if sel(b) and b["price"]]
        if not rs:
            print(f"{label:34s}    0      -       -       -"); return None
        n = len(rs); w = sum(1 for b in rs if b["win"])
        ret = sum(float(b["price"]) for b in rs if b["win"])
        known = [b['prob'] for b in rs if b['prob'] is not None]
        stated = f"{sum(known)/len(known):.0%}" if known else "unavailable"
        print(f"{label:34s} {n:4d} {w/n:6.0%} {stated:>11s} {len(known):4d} {(ret-n)/n:+7.1%}")
        return n, w/n, (ret-n)/n
    row("ALL priced", lambda b: True)
    row("band 50-60%", lambda b: b["prob"] is not None and 0.50 <= b["prob"] < 0.60)
    row("band <50%", lambda b: b["prob"] is not None and b["prob"] < 0.50)
    row("band >=60%", lambda b: b["prob"] is not None and b["prob"] >= 0.60)
    row("SHARP-priced (theoddsapi/betexpl)", lambda b: b["src"] in SHARP)
    row("SOFT-priced (scoutingstats)", lambda b: b["src"] == "scoutingstats")
    print("\n--- goals surface by rule ---")
    for rn in sorted({b["rule"] for b in graded}):
        row(f"rule {rn}", lambda b, rn=rn: b["rule"] == rn)
    print("--- goals surface by bucket ---")
    for bk in sorted({b["bucket"] for b in graded}):
        row(f"bucket {bk}", lambda b, bk=bk: b["bucket"] == bk)
    gate = row("GATE cut: 50-60% AND sharp", lambda b: b["prob"] is not None and 0.50 <= b["prob"] < 0.60 and b["src"] in SHARP)
    print("\nCHECKPOINT 3 GATE (50-60% band, priced):")
    g = row("   band 50-60% priced", lambda b: b["prob"] is not None and 0.50 <= b["prob"] < 0.60 and b["price"])
    if g:
        n, hit, roi = g
        need = []
        if n < 30: need.append(f"{30-n} more graded")
        if hit < 0.70: need.append(f"hit {hit:.0%} < 70%")
        if roi <= 0: need.append(f"ROI {roi:+.1%} <= 0")
        print("   STATUS: " + ("PASS — earns walk-forward inclusion" if not need else "PENDING — " + ", ".join(need)))
    pend = [b for b in bets if b["win"] is None and b["price"]]
    print(f"\npending priced overs (results not yet filed): {len(pend)}")
    for b in pend[-10:]:
        stated = f"{b['prob']:.0%}" if b['prob'] is not None else "unavailable"
        print(f"   {b['day']} {stated} @ {b['price']} ({b['src']})")


if __name__ == "__main__":
    main()
