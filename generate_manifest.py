import json, os, hashlib, datetime

def get_file_info(filepath):
    if not os.path.exists(filepath): return None
    stat = os.stat(filepath)
    with open(filepath, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    
    records = None
    if filepath.endswith('.json'):
        with open(filepath) as f:
            try:
                data = json.load(f)
                if isinstance(data, list): records = len(data)
                elif isinstance(data, dict):
                    if 'edges' in data: records = len(data['edges'])
                    elif 'picks' in data: records = len(data['picks'])
                    else: records = len(data.keys())
            except:
                pass
    elif filepath.endswith('.duckdb'):
        records = 'n/a'
        
    return {
        "path": filepath,
        "bytes": stat.st_size,
        "mtime": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "sha256": sha256,
        "records": records
    }

files = [
    "localdata/edges_consensus.json",
    "localdata/clv_report_rolling.json",
    "localdata/picks_audit_rolling.json",
    "localdata/warehouse.duckdb"
]

import glob
picks = sorted(glob.glob("localdata/picks_20*.json"))
files.extend(picks)

manifest = {
    "repo": {
        "sha": "e7313902b88ecf1d89ac5b682c3a4fdbb18f6d00",
        "date": "2026-07-05T03:39:19+02:00",
        "branch": "main",
        "dirty": False
    },
    "tests": {
        "passed": 30,
        "failed": 0,
        "coverage": None
    },
    "artifacts": []
}

for f in files:
    info = get_file_info(f)
    if info:
        manifest["artifacts"].append(info)

with open('antigravity_output/antigravity_manifest_20260705.json', 'w') as f:
    json.dump(manifest, f, indent=2)

print("Manifest written")
