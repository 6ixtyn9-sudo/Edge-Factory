#!/usr/bin/env python3
"""Read-only comparison with this session's immutable pre-change selection code.

200 seeded stubbed cohorts/price boards, including no-cohort fallbacks. This
proves explicit rollback (env=0) parity, NOT the now-broader default or ROI.
Run in a fresh process: it patches module functions in memory, never on disk.
"""
import subprocess,types,sys,json,random,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(ROOT/'scripts')]
import scripts.picks_today as new
old=types.ModuleType('redteam_baseline');old.__file__=str(ROOT/'scripts/picks_today.py');sys.modules[old.__name__]=old
source=subprocess.check_output(['git','show','8abefc45fc4b4442a2997d0c3f18831cc6bff436:scripts/picks_today.py'],text=True,cwd=ROOT)
exec(compile(source,'baseline_picks_today.py','exec'),old.__dict__)
class Con:
 def execute(self,*a,**k):return self
 def fetchone(self):return None
 def fetchall(self):return []
rng=random.Random(20261019);cases=200
for m in (old,new):
 m.load_rolling_audit_hit_rates=lambda:{}
 m.load_enhancement_calibration=lambda *a,**k:{}
 def attach(p,index,**k):
  price=index.get(p['recommended_enhancement'])
  if price is not None:p.update(enhancement_priced=True,enhancement_price=price,enhancement_price_source='test',enhancement_price_book='test')
  return p
 m.attach_enhancement_price=attach
os.environ[new.ENH_COHORT_PARITY_ENV]="0"
for case in range(cases):
 c={'n':400,'avg_goals':rng.uniform(.5,5)}
 c.update({v:rng.random() for v in new.COHORT_DIRECT_KEYS.values()})
 if case%5==0:c=None
 for m in (old,new):m.fetch_match_cohort=lambda *a,**k:c
 prices={k:round(rng.uniform(1.02,5.0),2) for k in set(new.COHORT_DIRECT_KEYS)|set(new.COHORT_COMPLEMENT_KEYS)}
 p={'home':'Alpha','away':'Beta','pick':'home','avg_p':70,'date':'2026-10-18'}
 a=old.compute_dynamic_enhancement(Con(),dict(p),prices);b=new.compute_dynamic_enhancement(Con(),dict(p),prices)
 # Display function is deliberately changed; selection function must retain parity, logs included.
 assert a==b,(case,a,b)
print(json.dumps({'seed':20261019,'cases':cases,'baseline':'8abefc45fc4b4442a2997d0c3f18831cc6bff436:scripts/picks_today.py','mode':'explicit_legacy_rollback_env_0','legacy_recommendation_and_logs_identical':True}))
