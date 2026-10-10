#!/usr/bin/env python3
"""Probe Boggio's documented RapidAPI endpoint without leaking secrets."""
from __future__ import annotations
import argparse, json, os, urllib.error, urllib.parse, urllib.request, sys
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
 parser=argparse.ArgumentParser(description="Bounded Boggio prediction or fixture-stats probe")
 parser.add_argument('--endpoint', choices=('home-league-stats','away-league-stats','head-to-head','home-last-10','away-last-10','predictions'), default=None)
 parser.add_argument('--match-id', type=int, default=None)
 args=parser.parse_args()
 if args.endpoint:
  if args.match_id is None or args.match_id <= 0: parser.error('--endpoint requires a positive --match-id')
  key=os.environ.get('RAPIDAPI_KEY','').strip()
  print(f"RAPIDAPI_KEY present: {'yes' if key else 'no'}")
  if not key:return 0
  path=f"/api/v2/{args.endpoint}/{args.match_id}"
  url=BASE+path
  req=urllib.request.Request(url,headers={'Accept':'application/json','X-RapidAPI-Key':key,'X-RapidAPI-Host':HOST})
  try:
   with urllib.request.urlopen(req,timeout=20) as r:
    payload=json.loads(r.read(2_000_000).decode('utf-8','replace'))
    sample=payload.get('data') if isinstance(payload,dict) else None
    print(f"ledger=boggio_stats endpoint={args.endpoint} match_id={args.match_id} calls=1 status={r.status}")
    print('data_type='+type(sample).__name__)
    if isinstance(sample,dict):
     print('data_keys='+repr(list(sample)[:40]))
     for name,value in list(sample.items())[:12]:
      if isinstance(value,dict): print(f"{name}_keys={list(value)[:40]}")
      elif isinstance(value,list):
       print(f"{name}_count={len(value)}")
       if value and isinstance(value[0],dict):print(f"{name}_first_keys={list(value[0])[:40]}")
    elif isinstance(sample,list):
     print(f"data_count={len(sample)}")
     if sample and isinstance(sample[0],dict): print('first_keys='+repr(list(sample[0])[:40]))
    print('rate_limit_headers='+repr({str(k):str(v) for k,v in r.headers.items() if 'ratelimit' in str(k).lower()}))
  except urllib.error.HTTPError as e:
   print(f"ledger=boggio_stats endpoint={args.endpoint} match_id={args.match_id} calls=1 status={e.code} error_class=HTTPError")
  except Exception as e:
   print(f"ledger=boggio_stats endpoint={args.endpoint} match_id={args.match_id} calls=1 status=unknown error_class={type(e).__name__}")
  return 0
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
