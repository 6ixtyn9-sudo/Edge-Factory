#!/usr/bin/env python3
"""Probe Boggio's documented RapidAPI endpoint without leaking secrets."""
from __future__ import annotations
import json, os, urllib.error, urllib.parse, urllib.request, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT/'src'))
from edgefactory.identity import source_team_key

def coverage_report(data, slate):
    items=data.get('data',[]) if isinstance(data,dict) else []
    priced={(source_team_key(x.get('home_team')),source_team_key(x.get('away_team'))) for x in items if isinstance(x,dict)}
    missing=[f"{x.get('home')} v {x.get('away')}" for x in slate if (source_team_key(x.get('home')),source_team_key(x.get('away'))) not in priced]
    matched=len(slate)-len(missing)
    return {'slate':len(slate),'matched':matched,'coverage_pct':round(100*matched/len(slate),1) if slate else 0.0,'unmatched_examples':missing[:5]}
from datetime import datetime, timezone
BASE="https://football-prediction-api.p.rapidapi.com"; HOST="football-prediction-api.p.rapidapi.com"
def main():
 key=os.environ.get("RAPIDAPI_KEY","").strip(); print(f"RAPIDAPI_KEY present: {'yes' if key else 'no'}")
 if not key:return 0
 day=datetime.now(timezone.utc).date().isoformat(); url=BASE+"/api/v2/predictions?"+urllib.parse.urlencode({"iso_date":day,"market":"classic"})
 req=urllib.request.Request(url,headers={"Accept":"application/json","X-RapidAPI-Key":key,"X-RapidAPI-Host":HOST})
 try:
  with urllib.request.urlopen(req,timeout=20) as r:
   body=r.read(2000000).decode("utf-8","replace"); print(f"status={r.status}"); print("rate_limit_headers="+repr({str(k):str(v) for k,v in r.headers.items() if 'ratelimit' in str(k).lower() or str(k).lower()=='retry-after'})); print("body_sample="+body.replace(key,"[REDACTED]")[:200])
   data=json.loads(body) if body else None; items=data.get("data",[]) if isinstance(data,dict) else []
   if items and isinstance(items[0],dict):
    first=items[0]; print("first_keys_types="+repr({k:type(v).__name__ for k,v in list(first.items())[:24]})); print("publication_lag_hours="+repr(_lag(first)))
   slate_path=Path(os.environ.get('EDGE_FACTORY_SLATE',str(ROOT/'localdata'/'picks_today.json')))
   try:
    payload=json.loads(slate_path.read_text()); slate=payload if isinstance(payload,list) else payload.get('rows',[])
   except (OSError,ValueError,TypeError): slate=[]
   cov=coverage_report(data,slate); print(f"coverage_pct={cov['coverage_pct']} slate={cov['slate']} matched={cov['matched']}"); print(f"unmatched_examples={cov['unmatched_examples']}"); print('projection: shared-fixture target >=30; coverage is diagnostic only and is not persisted.')
 except urllib.error.HTTPError as e:
  sample=e.read(200).decode("utf-8","replace") if e.fp else ""; print(f"status={e.code} error_class=HTTPError body_sample={sample.replace(key,'[REDACTED]')[:200]}")
 except Exception as e: print(f"status=error error_class={type(e).__name__}")
 return 0
def _lag(row):
 try:return round((datetime.fromisoformat(str(row['start_date']).replace('Z','+00:00'))-datetime.now(timezone.utc)).total_seconds()/3600,1)
 except Exception:return None
if __name__=='__main__':raise SystemExit(main())
