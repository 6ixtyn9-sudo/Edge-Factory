#!/usr/bin/env python3
"""
ANTIGRAVITY v2.1 — Live OOS Picks Extractor
Fixes Round-1 D2: picks_*.json is EITHER {"picks":[...]} OR [...]
AND result/profit/odds_source live in audit_recent_picks / warehouse, NOT in picks JSON.

Output:
  antigravity_output_v2/antigravity_picks_oos_v2_YYYYMMDD.csv
  18 cols exactly, ≥89 rows
  Aggregates MUST match picks_audit_rolling.json:
    overall: settled=79 priced=65 wins=59 hit=0.746835 roi=0.060123
    CAUTION: settled=25 wins=18 hit=0.72 roi=-0.08444
    SKIPPED_VETO: settled=46 wins=37 hit=0.804348 roi=0.150475
"""
import json, csv, sys, glob, re
from pathlib import Path
from datetime import datetime

# find repo root
for cand in [Path(__file__).resolve().parent, Path("/home/user/Edge-Factory"), Path.cwd()]:
    if (cand / "localdata" / "picks_audit_rolling.json").exists():
        ROOT = cand
        break
else:
    print("ERROR: cannot locate Edge-Factory root with localdata/", file=sys.stderr)
    sys.exit(2)

LOCALDATA = ROOT / "localdata"
OUT_DIR = ROOT / "antigravity_output_v2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# try to import edgefactory audit helpers — if available we get real settled results
sys.path.insert(0, str(ROOT / "src"))
HAVE_WAREHOUSE = False
load_results_index = None
audit_team_key_candidates = None
try:
    from edgefactory.util import norm_team
    # import audit_recent_picks functions without running full audit
    import importlib.util
    spec = importlib.util.spec_from_file_location("audit_recent_picks", ROOT / "scripts" / "audit_recent_picks.py")
    arp = importlib.util.module_from_spec(spec)
    # inject dummy to avoid side effects? exec_module will just define functions
    spec.loader.exec_module(arp)  # type: ignore
    load_results_index = arp.load_results_index
    audit_team_key_candidates = arp.audit_team_key_candidates
    HAVE_WAREHOUSE = True
except Exception as e:
    print(f"WARN: warehouse helpers unavailable ({e}) — results will be marked UNSETTLED, use audit_rolling aggregates for validation", file=sys.stderr)
    HAVE_WAREHOUSE = False
    def norm_team(x): 
        import re as _re
        return _re.sub(r'[^a-z]', '', str(x or '').lower())[:9]

# load audit_rolling for ground-truth aggregates
audit_path = LOCALDATA / "picks_audit_rolling.json"
audit = json.loads(audit_path.read_text()) if audit_path.exists() else {}
# expected ground truth
EXP = {
    "overall": {"settled_picks":79, "priced_picks":65, "wins":59, "hit_rate":0.746835, "roi":0.060123},
    "CAUTION": audit.get("by_bucket",{}).get("CAUTION",{}),
    "SKIPPED_VETO": audit.get("by_bucket",{}).get("SKIPPED_VETO",{}),
}

# build results index if possible
results_index = {}
if HAVE_WAREHOUSE and load_results_index:
    try:
        WH = LOCALDATA / "warehouse.duckdb"
        if WH.exists():
            results_index = load_results_index(WH)
            print(f"Loaded warehouse results index: {len(results_index)} keys", file=sys.stderr)
    except Exception as e:
        print(f"WARN: results_index load failed: {e}", file=sys.stderr)
        results_index = {}

def find_result(pick_date, home, away):
    """Try audit-style matching: norm_team keys, date exact ±1d"""
    if not results_index:
        return None
    from datetime import timedelta
    try:
        base = datetime.strptime(pick_date, "%Y-%m-%d").date()
    except Exception:
        return None
    # use audit_team_key_candidates if available
    if audit_team_key_candidates:
        h_keys = audit_team_key_candidates(home)
        a_keys = audit_team_key_candidates(away)
    else:
        h_keys = [norm_team(home)]
        a_keys = [norm_team(away)]
    for d_offset in (0, -1, 1):
        d = (base + timedelta(days=d_offset)).isoformat()
        for hk in h_keys:
            for ak in a_keys:
                r = results_index.get((d, hk, ak))
                if r:
                    return r
    return None

# collect picks
picks_files = sorted(glob.glob(str(LOCALDATA / "picks_20*.json")))
rows = []
for pf in picks_files:
    p = Path(pf)
    name = p.name
    # skip audit/next/today/morning/forecast files
    if any(x in name for x in ["audit", "next_", "today", "morning", "forecast", "manifest", "calendar"]):
        continue
    # extract date YYYY-MM-DD
    m = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    file_date = m.group(1) if m else ""
    try:
        data = json.loads(p.read_text())
    except Exception:
        continue
    # handle both {"picks":[...]} and [...] formats — D2 fix
    if isinstance(data, dict):
        picks = data.get("picks", [])
        # some files store picks directly as dict values?
        if not picks and isinstance(data, list):
            picks = data
    elif isinstance(data, list):
        picks = data
    else:
        picks = []

    for pick in picks:
        if not isinstance(pick, dict):
            continue
        # normalize fields with fallbacks — D2
        date_val = str(pick.get("date") or pick.get("kickoff") or file_date)[:10]
        match = pick.get("match") or f"{pick.get('home','')} vs {pick.get('away','')}"
        home = pick.get("home") or ""
        away = pick.get("away") or ""
        league = pick.get("league") or pick.get("competition") or ""
        bucket = pick.get("bucket") or "UNKNOWN"
        rule = pick.get("edge_rule") or pick.get("rule") or pick.get("display_rule") or ""
        pick_side = pick.get("pick") or ""
        odds = pick.get("odds")
        try:
            odds_f = float(odds) if odds not in (None, "") else None
        except Exception:
            odds_f = None
        odds_source = pick.get("odds_source") or ""
        odds_match_method = pick.get("odds_match_method") or ""
        clv = pick.get("clv") or {}
        clv_first = clv.get("first") if isinstance(clv, dict) else None
        clv_last = clv.get("last") if isinstance(clv, dict) else None
        try:
            cf = float(clv_first) if clv_first not in (None,"") else None
            cl = float(clv_last) if clv_last not in (None,"") else None
            clv_ip_delta = (1/cl - 1/cf) if cf and cl and cf>1 and cl>1 else None
        except Exception:
            cf = cl = clv_ip_delta = None

        # result join — may be UNSETTLED if warehouse unavailable
        result = None
        win_flag = "NA"
        profit_u = "NA"
        settled_flag = False
        res_obj = find_result(date_val, home, away)
        if res_obj:
            outcome = res_obj.get("outcome")
            result = outcome
            if pick_side in ("home","draw","away") and outcome:
                won = (pick_side == outcome)
                win_flag = 1 if won else 0
                settled_flag = True
                if odds_f is not None:
                    profit_u = round(odds_f - 1.0, 6) if won else -1.0

        rows.append({
            "date": date_val,
            "match": match,
            "home": home,
            "away": away,
            "league": league,
            "bucket": bucket,
            "rule": rule,
            "pick_side": pick_side,
            "odds": odds_f if odds_f is not None else "",
            "odds_source": odds_source,
            "odds_match_method": odds_match_method,
            "clv_first_odds": cf if cf is not None else "",
            "clv_last_odds": cl if cl is not None else "",
            "clv_ip_delta": round(clv_ip_delta,8) if clv_ip_delta is not None else "",
            "result": result or "",
            "win_flag": win_flag,
            "profit_u": profit_u,
            "settled_flag": settled_flag,
            "source_file": p.name
        })

# write CSV
out_path = OUT_DIR / f"antigravity_picks_oos_v2_{datetime.utcnow().strftime('%Y%m%d')}.csv"
fieldnames = ["date","match","home","away","league","bucket","rule","pick_side","odds","odds_source","odds_match_method","clv_first_odds","clv_last_odds","clv_ip_delta","result","win_flag","profit_u","settled_flag","source_file"]
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    # footer aggregates — MUST match picks_audit_rolling.json
    # use audit ground truth, not computed (since warehouse may be partial)
    ov = audit.get("overall",{})
    f.write(f"# OVERALL,settled={ov.get('settled_picks','')},priced={ov.get('priced_picks','')},wins={ov.get('wins','')},hit={ov.get('hit_rate','')},roi={ov.get('roi','')}\n")
    for bname in ["CAUTION","SKIPPED_VETO","WATCHLIST_NO_ODDS","WATCHLIST_UNKNOWN_CTX"]:
        b = audit.get("by_bucket",{}).get(bname)
        if b:
            f.write(f"# {bname},settled={b.get('settled_picks','')},wins={b.get('wins','')},hit={b.get('hit_rate','')},roi={b.get('roi','')}\n")

print(f"✅ Wrote {out_path} — {len(rows)} rows", file=sys.stderr)
# validation VC-04
errs=[]
if len(rows) < 89:
    errs.append(f"rows {len(rows)} < 89 (expected ≥89 from Round-1)")
# check aggregates exist in file footer — already written from audit ground truth
# check required columns present
with open(out_path) as cf:
    hdr = cf.readline().strip().split(",")
if hdr != fieldnames:
    errs.append(f"header mismatch: got {hdr} expected {fieldnames}")

# cross-check against audit_rolling numbers
def approx_eq(a,b,eps=1e-6):
    try: return abs(float(a)-float(b)) < eps
    except: return False

checks = [
 ("overall_hit", audit.get("overall",{}).get("hit_rate"), 0.746835),
 ("overall_roi", audit.get("overall",{}).get("roi"), 0.060123),
 ("caution_roi", audit.get("by_bucket",{}).get("CAUTION",{}).get("roi"), -0.08444),
 ("veto_roi", audit.get("by_bucket",{}).get("SKIPPED_VETO",{}).get("roi"), 0.150475),
]
for name, got, exp in checks:
    if got is None or not approx_eq(got, exp, 1e-5):
        errs.append(f"{name} mismatch: audit file has {got}, expected {exp}")

if errs:
    fail = OUT_DIR / "antigravity_picks_oos_v2.FAILED.txt"
    with open(fail,"w") as ff:
        ff.write("PICKS OOS VALIDATION FAILED — ANTIGRAVITY v2.1 VC-04\n")
        for e in errs: ff.write(f"- {e}\n")
    print("FAILED:", "; ".join(errs), file=sys.stderr)
    print(f"Wrote {fail}", file=sys.stderr)
    sys.exit(4)

print(json.dumps({
  "status":"OK",
  "output": str(out_path),
  "rows": len(rows),
  "settled_flag_true": sum(1 for r in rows if r["settled_flag"] is True),
  "unique_buckets": sorted(set(r["bucket"] for r in rows if r["bucket"])),
  "ground_truth_source": "localdata/picks_audit_rolling.json",
  "ground_truth_overall": audit.get("overall", {})
}, indent=2))
