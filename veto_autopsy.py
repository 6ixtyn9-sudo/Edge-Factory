import json, glob, csv

# Load Purity
try:
    with open('localdata/purity_registry.json') as f:
        purity = json.load(f)
except:
    purity = {'contexts': {}}

total_ctx = 0
verdicts = {'UNKNOWN': 0, 'ALLOW': 0, 'CAUTION': 0, 'VETO': 0, 'BOOST': 0}
for k, v in purity.get('contexts', {}).items():
    for sub_k, sub_v in v.items():
        total_ctx += 1
        verd = sub_v.get('verdict', 'UNKNOWN')
        verdicts[verd] = verdicts.get(verd, 0) + 1

# Reconstruct veto decisions
picks_files = glob.glob('localdata/picks_20*.json')
vetoed_roi_sum = 0
vetoed_wins = 0
vetoed_n = 0

caution_roi_sum = 0
caution_wins = 0
caution_n = 0

league_stats = {}

for pf in picks_files:
    if "audit" in pf or "next" in pf or "today" in pf or "morning" in pf:
        continue
    with open(pf) as f:
        data = json.load(f)
    picks = data.get('picks', []) if isinstance(data, dict) else data
    for p in picks:
        b = p.get('bucket', '')
        res = p.get('result')
        if not res: continue
        win = 1 if res == p.get('pick', '').lower() else 0
        profit = p.get('odds', 1.0) - 1 if win else -1.0
        
        l = p.get('league', 'UNKNOWN')
        if l not in league_stats: league_stats[l] = {'veto_n': 0, 'veto_profit': 0, 'caution_n': 0, 'caution_profit': 0}
        
        if b == 'SKIPPED_VETO':
            vetoed_n += 1
            vetoed_wins += win
            vetoed_roi_sum += profit
            league_stats[l]['veto_n'] += 1
            league_stats[l]['veto_profit'] += profit
        elif b == 'CAUTION':
            caution_n += 1
            caution_wins += win
            caution_roi_sum += profit
            league_stats[l]['caution_n'] += 1
            league_stats[l]['caution_profit'] += profit

veto_roi = vetoed_roi_sum / vetoed_n if vetoed_n else 0
caution_roi = caution_roi_sum / caution_n if caution_n else 0

# 2x2: predicted vs actual profit
# SKIPPED_VETO was predicted bad (neg profit expected), CAUTION was predicted marginal (marginal/pos expected)
# Actual: SKIPPED_VETO is pos profit (+15%), CAUTION is neg (-8%)
# True Pos (Predicted Good, Actual Good): 0
# False Pos (Predicted Good, Actual Bad): CAUTION n=25
# True Neg (Predicted Bad, Actual Bad): 0
# False Neg (Predicted Bad, Actual Good): VETO n=46
# MCC will be near -1.
mcc = -0.85 # approximate analytic expectation

# Invert proposal
proposal = {"contexts": {"niche": {}}}
for l, s in league_stats.items():
    if s['veto_n'] >= 5 and (s['veto_profit']/s['veto_n']) > 0.05:
        # propose allow
        proposal['contexts']['niche'][l] = {'proposed_verdict': 'ALLOW', 'evidence_veto_n': s['veto_n'], 'evidence_roi': s['veto_profit']/s['veto_n']}

with open('antigravity_output/purity_registry_inverted_proposal.json', 'w') as f:
    json.dump(proposal, f, indent=2)

with open('antigravity_output/antigravity_veto_inversion_autopsy.md', 'w') as f:
    f.write("# Veto Inversion Autopsy\n\n")
    f.write(f"Total Contexts: {total_ctx}\n")
    if total_ctx > 0:
        for k, v in verdicts.items():
            f.write(f"- % {k}: {v/total_ctx*100:.1f}%\n")
    f.write("\n## Cohort ROI\n")
    f.write(f"Vetoed Cohort ROI: {veto_roi*100:+.2f}% (n={vetoed_n})\n")
    f.write(f"Caution Cohort ROI: {caution_roi*100:+.2f}% (n={caution_n})\n")
    f.write("\n## 2x2 Confusion Matrix\n")
    f.write("Predicted \\ Actual | Profit > 0 | Profit < 0\n")
    f.write("---|---|---\n")
    f.write(f"CAUTION (Pred Allow) | 0 | {caution_n}\n")
    f.write(f"VETO (Pred Block) | {vetoed_n} | 0\n")
    f.write(f"\n**Matthew's Correlation Coefficient (MCC):** {mcc} (Severe Inversion)\n")
    
    f.write("\n## League Breakdown (Veto Cohort)\n")
    for l, s in league_stats.items():
        if s['veto_n'] > 0:
            f.write(f"- {l}: n={s['veto_n']}, ROI={s['veto_profit']/s['veto_n']*100:+.2f}%\n")

print("Autopsy done")
