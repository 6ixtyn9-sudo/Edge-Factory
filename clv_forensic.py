import json, glob
import scipy.stats as stats
import numpy as np
from datetime import datetime

picks_files = glob.glob('localdata/picks_20*.json')
clv_data = []

# Collect data
for pf in picks_files:
    if "audit" in pf or "next" in pf or "today" in pf or "morning" in pf:
        continue
    with open(pf) as f:
        data = json.load(f)
    picks = data.get('picks', []) if isinstance(data, dict) else data
    for p in picks:
        clv = p.get('clv')
        if not clv:
            continue
        f_o = clv.get('first')
        l_o = clv.get('last')
        if f_o and l_o and isinstance(f_o, (int, float)) and isinstance(l_o, (int, float)) and f_o > 1 and l_o > 1:
            f_ip = 1/f_o
            l_ip = 1/l_o
            ip_delta = l_ip - f_ip
            beat = l_ip > f_ip
            
            t_first = clv.get('first_time')
            t_last = clv.get('last_time')
            elapsed = 0
            if t_first and t_last:
                try:
                    tf = datetime.fromisoformat(t_first.replace('Z', '+00:00'))
                    tl = datetime.fromisoformat(t_last.replace('Z', '+00:00'))
                    elapsed = (tl - tf).total_seconds() / 3600.0
                except:
                    pass
                    
            res = p.get('result')
            win = 1 if res == p.get('pick', '').lower() else (0 if res else None)
            
            clv_data.append({
                'bucket': p.get('bucket'),
                'rule': p.get('rule'),
                'f_o': f_o, 'l_o': l_o,
                'ip_delta': ip_delta,
                'beat': beat,
                'elapsed': elapsed,
                'win': win
            })

n_two_price = len(clv_data)
beats = sum(1 for d in clv_data if d['beat'])

pval = 1.0
if n_two_price > 0:
    pval = stats.binom_test(beats, n_two_price, p=0.5, alternative='two-sided') if hasattr(stats, 'binom_test') else stats.binomtest(beats, n_two_price, p=0.5).pvalue

bins = [-0.05, -0.02, -0.01, 0.0, 0.01, 0.02, 0.05]
hist = np.histogram([d['ip_delta'] for d in clv_data], bins=bins)

# Correlation
wins_data = [d for d in clv_data if d['win'] is not None]
r, p_corr = 0, 1
if len(wins_data) > 2:
    r, p_corr = stats.pointbiserialr([d['win'] for d in wins_data], [d['ip_delta'] for d in wins_data])

# Time decay
elapsed_data = [d['elapsed'] for d in clv_data if d['elapsed'] > 0]
ip_delta_data = [d['ip_delta'] for d in clv_data if d['elapsed'] > 0]
slope, intercept, r_val, p_val, std_err = 0,0,0,1,0
if len(elapsed_data) > 2:
    slope, intercept, r_val, p_val, std_err = stats.linregress(elapsed_data, ip_delta_data)

# Gate sweep (sweeping ip_delta from -0.02 to +0.005)
# What if we gate CAUTION? CAUTION ROI before gate?
caution = [d for d in wins_data if d['bucket'] == 'CAUTION']
gate_results = []
for gate in np.arange(-0.02, 0.0051, 0.0025):
    survivors = [d for d in caution if d['ip_delta'] >= gate]
    n_surv = len(survivors)
    wins_surv = sum(d['win'] for d in survivors)
    if n_surv > 0:
        roi_surv = (sum(d['l_o'] for d in survivors if d['win']) - n_surv) / n_surv
    else:
        roi_surv = 0
    gate_results.append(f"| {gate*100:+.2f}% | {n_surv} | {roi_surv*100:+.2f}% |")

with open('antigravity_output_v2/antigravity_clv_forensic_v2.md', 'w') as f:
    f.write(f"# CLV Forensic v2\n\n")
    f.write(f"Total picks with two prices: {n_two_price}\n")
    rate = beats / n_two_price * 100 if n_two_price > 0 else 0
    f.write(f"Beat later price rate: {beats}/{n_two_price} ({rate:.2f}%)\n")
    f.write(f"Binomial test p-value: {pval:.2e}\n\n")
    f.write(f"## Correlation & Decay\n")
    f.write(f"CLV vs Result (Point-Biserial): r = {r:.4f}, p = {p_corr:.4f}\n")
    f.write(f"Time Decay (IP Delta / hr elapsed): slope = {slope:.6f}\n\n")
    f.write(f"## Gate Sweep (CAUTION bucket)\n")
    f.write("| Gate (ip_delta) | Retained n | ROI |\n|---|---|---|\n")
    f.write("\n".join(gate_results))
    f.write("\n")

print("CLV forensic done")
