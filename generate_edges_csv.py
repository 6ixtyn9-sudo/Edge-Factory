import json, csv

with open('localdata/edges_consensus.json') as f:
    data = json.load(f)

edges = data.get('edges', [])
rows = []

flags_list = []
counts = {"certified": 0, "benched": 0, "candidate": 0}
# Assuming edge objects have 'train' and 'valid' dicts
for e in edges:
    rule = e.get('rule', '')
    view = e.get('view', '')
    status = e.get('status', 'candidate')
    counts[status] = counts.get(status, 0) + 1
    
    train = e.get('train', {})
    valid = e.get('valid', {})
    decay = e.get('decay', {})
    
    t_n = train.get('n', 0)
    t_hit = train.get('hit_rate', 0.0)
    t_lb = train.get('wilson_lb', 0.0)
    t_roi = train.get('roi', 0.0)
    t_odds = train.get('avg_odds', 0.0)
    
    v_n = valid.get('n', 0)
    v_hit = valid.get('hit_rate', 0.0)
    v_lb = valid.get('wilson_lb', 0.0)
    v_roi = valid.get('roi', 0.0)
    v_odds = valid.get('avg_odds', 0.0)
    
    d_verdict = decay.get('verdict', '')
    r_n = decay.get('recent', {}).get('n', 0)
    r_hit = decay.get('recent', {}).get('hit_rate', 0.0)
    r_roi = decay.get('recent', {}).get('roi', 0.0)
    benched_at = e.get('benched_at', '')

    roi_delta = v_roi - t_roi
    hit_delta = v_hit - t_hit
    lb_delta = v_lb - t_lb
    sample_ratio = v_n / t_n if t_n > 0 else 0
    
    flags = []
    if v_roi < 0: flags.append('valid_ROI<0')
    if t_roi > v_roi + 0.05: flags.append('overfit_ROI_drop>5pp')
    if v_n < 120: flags.append('n_valid<120')
    if v_lb < 0.70: flags.append('valid_Wilson<0.70')
    if v_odds < 1.20 and v_odds > 0: flags.append('avg_odds<1.20')
    
    if "away-only" in rule and v_roi > 0 and status == "certified": flags.append('CRITICAL_POLICY_BREACH_away_positive')
    if "ou_2.5" in view and v_roi > 0 and status == "certified": flags.append('CRITICAL_POLICY_BREACH_ou25_positive')
    if "draw" in rule.lower() and v_roi > 0 and status == "certified": flags.append('CRITICAL_POLICY_BREACH_draw_positive')
    
    rows.append({
        'rule': rule, 'view': view, 'status': status,
        'train_n': t_n, 'train_hit': t_hit, 'train_wilson': t_lb, 'train_roi': t_roi, 'train_odds': t_odds,
        'valid_n': v_n, 'valid_hit': v_hit, 'valid_wilson': v_lb, 'valid_roi': v_roi, 'valid_odds': v_odds,
        'roi_delta': roi_delta, 'hit_delta': hit_delta, 'lb_delta': lb_delta, 'sample_ratio': sample_ratio,
        'decay_verdict': d_verdict, 'recent_n': r_n, 'recent_hit': r_hit, 'recent_roi': r_roi, 'benched_at': benched_at,
        'flags': '|'.join(flags)
    })

rows.sort(key=lambda x: x['valid_roi'], reverse=True)

with open('antigravity_output/antigravity_edges_full.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(json.dumps(counts))
