#!/usr/bin/env python3
"""Diagnostic-only SharpAPI probe; never prints the RapidAPI key or query URL."""
from __future__ import annotations
import json, os, urllib.error, urllib.parse, urllib.request
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
from edgefactory.identity import source_team_key

def coverage_report(data, slate):
    items=data if isinstance(data,list) else (data.get('data',[]) if isinstance(data,dict) else [])
    priced={(source_team_key(x.get('home') or x.get('home_team')), source_team_key(x.get('away') or x.get('away_team'))) for x in items if isinstance(x,dict)}
    missing=[f"{x.get('home')} v {x.get('away')}" for x in slate if (source_team_key(x.get('home')),source_team_key(x.get('away'))) not in priced]
    return {'slate':len(slate),'matched':len(slate)-len(missing),'coverage_pct':round(100*(len(slate)-len(missing))/len(slate),1) if slate else 0.0,'unmatched_examples':missing[:5]}
from datetime import datetime, timezone
BASE = "https://sharpapi1.p.rapidapi.com"
HOST = "sharpapi1.p.rapidapi.com"
ENDPOINT = os.environ.get("SHARPAPI_ENDPOINT", "/odds")

def main() -> int:
    key = os.environ.get("RAPIDAPI_KEY", "").strip()
    print(f"RAPIDAPI_KEY present: {'yes' if key else 'no'}")
    if not key: return 0
    url = BASE + ENDPOINT + "?" + urllib.parse.urlencode({"date": datetime.now(timezone.utc).date().isoformat()})
    req = urllib.request.Request(url, headers={"Accept":"application/json", "X-RapidAPI-Key":key, "X-RapidAPI-Host":HOST})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read(2_000_000).decode("utf-8", "replace")
            print(f"status={response.status}")
            print("rate_limit_headers=" + repr({str(k):str(v) for k,v in response.headers.items() if 'ratelimit' in str(k).lower() or str(k).lower() == 'retry-after'}))
            print("body_sample=" + body[:200].replace(key, "[REDACTED]"))
            try: data = json.loads(body)
            except json.JSONDecodeError: data = None
            if isinstance(data, dict): print("top_keys=" + repr(list(data)[:20]))
            if isinstance(data, list) and data and isinstance(data[0], dict): print("first_object_keys_types=" + repr({k:type(v).__name__ for k,v in list(data[0].items())[:20]}))
            slate_path=Path(os.environ.get('EDGE_FACTORY_SLATE',str(ROOT/'localdata'/'picks_today.json')))
            try:
                payload=json.loads(slate_path.read_text()); slate=payload if isinstance(payload,list) else payload.get('rows',[])
            except (OSError,ValueError,TypeError): slate=[]
            cov=coverage_report(data,slate); print(f"coverage_pct={cov['coverage_pct']} slate={cov['slate']} matched={cov['matched']}"); print(f"unmatched_examples={cov['unmatched_examples']}"); print('projection: shared-fixture target >=30; coverage is diagnostic only and is not persisted.')
    except urllib.error.HTTPError as exc:
        sample = exc.read(200).decode("utf-8", "replace") if exc.fp else ""
        print(f"status={exc.code} error_class=HTTPError body_sample={sample.replace(key, '[REDACTED]')[:200]}")
    except Exception as exc: print(f"status=error error_class={type(exc).__name__}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
