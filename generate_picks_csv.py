import json, csv, glob

picks_files = glob.glob('localdata/picks_20*.json')
out_rows = []

for pf in picks_files:
    if "audit" in pf or "next" in pf or "today" in pf or "morning" in pf:
        continue
    with open(pf) as f:
        data = json.load(f)
    date_str = pf.split('_')[1].split('.')[0]
    
    # Check if data is list or dict
    if isinstance(data, dict):
        picks = data.get('picks', [])
    else:
        picks = data
        
    for p in picks:
        row = {
            'date': date_str,
            'match': p.get('match', ''),
            'bucket': p.get('bucket', ''),
            'rule': p.get('rule', ''),
            'odds_source': p.get('odds_source', ''),
            'odds_match_method': p.get('odds_match_method', ''),
            'odds': p.get('odds', ''),
            'result': p.get('result', ''),
            'profit': p.get('profit', ''),
            'home': p.get('home', ''),
            'away': p.get('away', ''),
            'clv_first': p.get('clv', {}).get('first', ''),
            'clv_last': p.get('clv', {}).get('last', '')
        }
        out_rows.append(row)

if out_rows:
    with open('antigravity_output/antigravity_picks_oos_20260705.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=out_rows[0].keys())
        writer.writeheader()
        writer.writerows(out_rows)

print(f"Exported {len(out_rows)} picks to CSV")
