#!/usr/bin/env python3
"""
ANTIGRAVITY v2.1 — Edge Registry Extractor
Correct field mapping for Edge Factory edges_consensus.json
Fixes Round-1 D1: train.hit NOT train.hit_rate etc.
Output: antigravity_output_v2/antigravity_edges_full_v2.csv
- 29 rows expected: certified=8, benched=2, candidate=19
- Top valid_roi MUST be 2way-unanimous avg_p>=70 -> 0.0397
"""
import json, csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# support running from repo root or /home/user
for cand in [ROOT, ROOT / "Edge-Factory", Path("/home/user/Edge-Factory")]:
    f = cand / "localdata" / "edges_consensus.json"
    if f.exists():
        EDGE_PATH = f
        OUT_DIR = cand / "antigravity_output_v2"
        break
else:
    print("ERROR: localdata/edges_consensus.json not found", file=sys.stderr)
    sys.exit(2)

OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / "antigravity_edges_full_v2.csv"

with open(EDGE_PATH) as fh:
    data = json.load(fh)

edges = data.get("edges", [])
rows = []
counts = {"certified":0, "benched":0, "candidate":0, "other":0}

def g(d, *keys, default=0):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur if cur is not None else default

for e in edges:
    rule = e.get("rule","")
    view = e.get("view","")
    status = e.get("status","candidate")
    market = e.get("market","")
    counts[status] = counts.get(status,0)+1 if status in counts else counts.setdefault("other",0)+1 or 1

    train = e.get("train",{})
    valid = e.get("valid",{})
    decay = e.get("decay",{})
    recent = decay.get("recent",{})

    t_n = g(train,"n",default=0)
    t_wins = g(train,"wins",default=0)
    t_hit = g(train,"hit",default=0.0)
    t_lb = g(train,"wilson_lb",default=0.0)
    t_roi = g(train,"roi",default=0.0)
    t_odds = g(train,"avg_odds",default=0.0)
    t_priced = g(train,"n_priced",default=t_n)

    v_n = g(valid,"n",default=0)
    v_wins = g(valid,"wins",default=0)
    v_hit = g(valid,"hit",default=0.0)
    v_lb = g(valid,"wilson_lb",default=0.0)
    v_roi = g(valid,"roi",default=0.0)
    v_odds = g(valid,"avg_odds",default=0.0)
    v_priced = g(valid,"n_priced",default=v_n)

    roi_delta = v_roi - t_roi
    hit_delta = v_hit - t_hit
    lb_delta = v_lb - t_lb
    sample_ratio = (v_n / t_n) if t_n else 0.0

    d_verdict = decay.get("verdict","")
    d_checked = decay.get("checked_at","")
    r_n = g(recent,"n",default=0)
    r_wins = g(recent,"wins",default=0)
    r_hit = g(recent,"hit",default=g(recent,"hit_rate",default=0.0))
    r_lb = g(recent,"wilson_lb",default=0.0)
    r_roi = g(recent,"roi",default=0.0)

    benched_at = e.get("benched_at","")

    flags = []
    if v_roi < 0: flags.append("valid_ROI_lt_0")
    if t_roi > v_roi + 0.05: flags.append("overfit_ROI_drop_gt_5pp")
    if 0 < v_n < 120: flags.append("n_valid_lt_120")
    if 0 < v_lb < 0.70: flags.append("valid_Wilson_lt_0.70")
    if 0 < v_odds < 1.20: flags.append("avg_odds_lt_1.20")

    rl = rule.lower()
    vw = (view or "").lower()
    # policy breach checks — must never be certified positive
    if "away-only" in rl and v_roi > 0 and status=="certified":
        flags.append("CRITICAL_POLICY_BREACH_away_positive")
    if "ou25" in vw or "ou_2.5" in vw or "ou25" in rl:
        if v_roi > 0 and status=="certified":
            flags.append("CRITICAL_POLICY_BREACH_ou25_positive")
    if "draw" in rl and "no-draw" not in rl and v_roi > 0 and status=="certified":
        flags.append("CRITICAL_POLICY_BREACH_draw_positive")

    rows.append({
        "rule": rule,
        "view": view,
        "status": status,
        "market": market,
        "train_n": t_n,
        "train_wins": t_wins,
        "train_hit": t_hit,
        "train_wilson_lb": t_lb,
        "train_roi": t_roi,
        "train_avg_odds": t_odds,
        "train_n_priced": t_priced,
        "valid_n": v_n,
        "valid_wins": v_wins,
        "valid_hit": v_hit,
        "valid_wilson_lb": v_lb,
        "valid_roi": v_roi,
        "valid_avg_odds": v_odds,
        "valid_n_priced": v_priced,
        "roi_delta_valid_minus_train": roi_delta,
        "hit_delta": hit_delta,
        "lb_delta": lb_delta,
        "sample_ratio_valid_over_train": sample_ratio,
        "decay_verdict": d_verdict,
        "decay_checked_at": d_checked,
        "recent_n": r_n,
        "recent_wins": r_wins,
        "recent_hit": r_hit,
        "recent_wilson_lb": r_lb,
        "recent_roi": r_roi,
        "benched_at": benched_at,
        "flags": "|".join(flags)
    })

# sort valid_roi DESC
rows.sort(key=lambda x: float(x["valid_roi"] or 0), reverse=True)

if not rows:
    print("ERROR: 0 edges parsed — check field mapping", file=sys.stderr)
    sys.exit(3)

fieldnames = list(rows[0].keys())
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    # summary footer as comments
    f.write(f"# SUMMARY,certified,{counts.get('certified',0)},benched,{counts.get('benched',0)},candidate,{counts.get('candidate',0)},total,{len(rows)}\n")
    f.write(f"# TOP_VALID_ROI,{rows[0]['rule']},{rows[0]['valid_roi']}\n")

# validation gates — Antigravity v2.1 VC-03
errors = []
if len(rows) != 29:
    errors.append(f"row_count {len(rows)} != 29")
if counts.get("certified",0) != 8:
    errors.append(f"certified {counts.get('certified',0)} != 8")
if counts.get("benched",0) != 2:
    errors.append(f"benched {counts.get('benched',0)} != 2")
if counts.get("candidate",0) != 19:
    errors.append(f"candidate {counts.get('candidate',0)} != 19")
top_rule = rows[0]["rule"]
top_roi = float(rows[0]["valid_roi"] or 0)
if top_rule != "2way-unanimous odds-1.20-1.75 avg_p>=70" or abs(top_roi - 0.063) > 0.002:
    errors.append(f"top_valid_roi mismatch: got {top_rule} {top_roi} expected 2way-unanimous odds-1.20-1.75 avg_p>=70 0.063")

# policy breach fail-fast
policy_breaches = [r for r in rows if "CRITICAL_POLICY_BREACH" in r["flags"]]
if policy_breaches:
    errors.append(f"POLICY_BREACH found in {len(policy_breaches)} rows: {[r['rule'] for r in policy_breaches]}")

if errors:
    fail_path = OUT_DIR / "antigravity_edges_full_v2.FAILED.txt"
    with open(fail_path,"w") as ff:
        ff.write("EDGE REGISTRY VALIDATION FAILED — ANTIGRAVITY v2.1 VC-03\n")
        for er in errors:
            ff.write(f"- {er}\n")
        ff.write(f"\ncounts={counts}\n")
    print("FAILED:", "; ".join(errors), file=sys.stderr)
    print(f"Wrote {fail_path}", file=sys.stderr)
    sys.exit(4)

print(json.dumps({
    "status": "OK",
    "output": str(OUT_CSV),
    "rows": len(rows),
    "counts": counts,
    "top_valid_roi": {"rule": top_rule, "roi": top_roi}
}, indent=2))
print(f"✅ Wrote {OUT_CSV} — {len(rows)} edges — certified={counts.get('certified',0)} benched={counts.get('benched',0)} candidate={counts.get('candidate',0)}", file=sys.stderr)
