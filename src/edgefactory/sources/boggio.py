"""Boggio Analytics - approved AVERAGE-BOOKMAKER price donor.

Role change (operator decision, 2026-10-03)
-------------------------------------------
Boggio was a voice-only shadow whose ``odds`` object was retained as
provenance and never used. The operator has explicitly promoted it to an
approved price donor. What that does and does not mean:

- its ``odds`` object is an **average across bookmakers**, so it is labelled
  ``odds_kind="provider_average"`` with ``bookmaker="average_bookie_aggregate"``;
- it is **not a named bookmaker**: ``named_bookmaker`` is always ``False`` and
  its independence family is ``boggio_average``, so it can never stand in for
  named-book corroboration;
- it may supply a printed price only while
  ``EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR`` is enabled.

Timestamp safeguards are unchanged and still enforced here, not downstream:
the free tier publishes predictions up to 12 hours ahead, so ``published_at``
and ``captured_at`` are both retained and a row published *after* it was
captured is marked ``timestamp_suspect`` and loses price eligibility. A
lookahead observation must never become either settled evidence or a price.
"""
from __future__ import annotations
import json, os, re, threading, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edgefactory.odds_normalization import canonical_market_selection

SOURCE="boggio"; BASE="https://football-prediction-api.p.rapidapi.com"; API_HOST="football-prediction-api.p.rapidapi.com"; KEY_ENV="RAPIDAPI_KEY"
MIN_INTERVAL_S=float(os.environ.get("EDGE_FACTORY_BOGGIO_MIN_INTERVAL_S","10")); MAX_CALLS_PER_RUN=1
LOCALDATA=Path(os.environ.get("EDGE_FACTORY_LOCALDATA",Path(__file__).resolve().parents[3]/"localdata"))
RETRYABLE_ZERO_ROW_STATUSES={"auth","quota","unavailable","blocked","error","cooldown"}
_lock=threading.Lock(); _last=0.0; _calls=0; _429=0; _cooling=False; _DIAG:dict[str,Any]={}
class UpstreamBlocked(RuntimeError): pass

def reset_state():
 global _last,_calls,_429,_cooling
 _last=0.0; _calls=0; _429=0; _cooling=False
def diagnostics(): return dict(_DIAG)
def _set_diag(x): _DIAG.update(x); return x
def _key(): return os.environ.get(KEY_ENV, "").strip() or None
def predictions_url(day): return BASE+"/api/v2/predictions?"+urllib.parse.urlencode({"iso_date":day,"market":"classic"})
def _headers(h): return {str(k):str(v) for k,v in (h.items() if hasattr(h,"items") else []) if "ratelimit" in str(k).lower() or str(k).lower()=="retry-after"}
def _status(code): return "auth" if code in (401,403) else "quota" if code in (402,429,509) else "unavailable"

def get_json(url, *, timeout=30):
 global _last,_calls,_429,_cooling
 if _cooling: raise UpstreamBlocked("boggio: run cooling down after repeated HTTP 429 responses")
 if not _key(): raise UpstreamBlocked(f"{KEY_ENV} not set; shadow capture skipped")
 if _calls>=MAX_CALLS_PER_RUN: raise UpstreamBlocked("boggio: per-run call budget reached")
 with _lock:
  wait=MIN_INTERVAL_S-(time.monotonic()-_last)
  if wait>0: time.sleep(wait)
  _last=time.monotonic(); _calls+=1
 req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"EdgeFactory-cooperative-shadow/1.0 (+operator review)","X-RapidAPI-Key":_key() or "","X-RapidAPI-Host":API_HOST})
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r:
   body=r.read(8_000_000).decode("utf-8","replace")
   try: data=json.loads(body) if body else None
   except json.JSONDecodeError: data=None
   return int(getattr(r,"status",200)),data,_headers(r.headers)
 except urllib.error.HTTPError as e:
  if e.code==429:
   _429+=1
   if _429>=2: _cooling=True; raise UpstreamBlocked("boggio: repeated HTTP 429; cooling down") from e
   retry=e.headers.get("Retry-After") if e.headers else None
   try: time.sleep(max(1,min(60,float(retry or 5))))
   except ValueError: time.sleep(5)
   return get_json(url,timeout=timeout)
  raise UpstreamBlocked(f"boggio: HTTP {e.code} {e.reason}") from e
 except Exception as e: raise UpstreamBlocked(f"boggio: {type(e).__name__}: {e}") from e

def _num(x):
 try: return float(x)
 except (TypeError,ValueError): return None

AVERAGE_BOOK_LABEL = "average_bookie_aggregate"
PRICE_INDEPENDENCE_FAMILY = "boggio_average"
PROVIDER_ROLE = "average_bookmaker_price_donor"
LOOKAHEAD_NOTE = (
    "Free tier publishes up to 12h pre-kickoff; consumers must enforce "
    "published_at <= captured_at and never use future observations."
)


def price_donor_enabled() -> bool:
    """Operator switch that lets Boggio's average price reach a ticket."""
    raw = os.environ.get("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR")
    if raw is None or not raw.strip():
        return True  # operator-requested default-on
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_stamp(value):
    try:
        text = str(value or "").strip().replace("Z", "+00:00")
        if not text:
            return None
        stamp = datetime.fromisoformat(text)
        return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def timestamp_suspect(published_at, captured_at) -> bool:
    """True when the row claims to have been published after we saw it.

    A future publication stamp is the signature of a lookahead artefact. It
    is never an error we can correct, so the row stays visible but loses
    price eligibility.
    """
    published, captured = _parse_stamp(published_at), _parse_stamp(captured_at)
    if published is None or captured is None:
        return False
    return published > captured


def _selection_odds(odds, prediction):
    """The average-book price for the predicted selection, if it is quoted."""
    if not isinstance(odds, dict):
        return None
    for key in (prediction, str(prediction)):
        if key in odds:
            value = _num(odds[key])
            if value is not None and value > 1.0:
                return value
    return None


def parse_predictions(payload:Any, *, day:str):
 data=payload.get("data") if isinstance(payload,dict) else payload
 if not isinstance(data,list): return [],False
 stamp=datetime.now(timezone.utc).isoformat(timespec="seconds"); rows=[]; shaped=False
 for item in data:
  if not isinstance(item,dict): continue
  home=str(item.get("home_team") or "").strip(); away=str(item.get("away_team") or "").strip()
  if not home or not away or not item.get("prediction"): continue
  shaped=True; published=item.get("last_update_at") or item.get("published_at") or item.get("updated_at")
  probs=item.get("probabilities") if isinstance(item.get("probabilities"),dict) else {}
  odds=item.get("odds") if isinstance(item.get("odds"),dict) else {}
  prediction=item.get("prediction")
  raw_market=item.get("market") or "classic"
  canonical, _failure = canonical_market_selection(
    raw_market, prediction, home=home, away=away,
  )
  if canonical is None:
   continue
  average_price=_selection_odds(odds,prediction)
  suspect=timestamp_suspect(published,stamp)
  kickoff=item.get("start_date")
  kickoff_text=str(kickoff or "")
  event_day=kickoff_text[:10] if re.match(r"^\d{4}-\d{2}-\d{2}",kickoff_text) else day
  rows.append({
    "source":SOURCE,
    "date":event_day,
    "home":home,
    "away":away,
    "kickoff":kickoff,
    "market":canonical.market,
    "selection":canonical.selection,
    "raw_market":raw_market,
    "raw_selection":prediction,
    "probability":_num(probs.get(str(prediction)) or probs.get(prediction)),
    # --- price donor fields (operator promotion 2026-10-03) ---
    "odds":average_price,
    "odds_kind":"provider_average",
    "provider_role":PROVIDER_ROLE,
    "bookmaker":AVERAGE_BOOK_LABEL,
    "named_bookmaker":False,
    "price_independence_family":PRICE_INDEPENDENCE_FAMILY,
    # Eligible only when the operator switch is on, a price exists, and the
    # publication stamp is not in the future relative to capture.
    "price_push_eligible":bool(average_price is not None and price_donor_enabled() and not suspect),
    "timestamp_suspect":suspect,
    "odds_provenance":odds,
    "published_at":published,
    "captured_at":stamp,
    "lookahead_note":LOOKAHEAD_NOTE,
  })
 return rows,shaped


def _path(day,localdata=None): return (localdata or LOCALDATA)/f"{SOURCE}_shadow_{day}.json"
def capture_day(day,*,localdata=None):
 stats={"status":"not_run","bg_raw":0,"bg_scored":0,"requests":0,"http_statuses":[],"http_429":0,"errors":[],"blocker":None,"schema_match":None,"budget":1}
 reset_state()
 if not _key(): stats["blocker"]=f"{KEY_ENV} not set; shadow capture skipped"; return [],_set_diag(stats)
 try:
  held=json.loads(_path(day,localdata).read_text()).get("rows",[])
  if held: stats.update(status="cache_only",cache_hits=1,bg_raw=len(held),bg_scored=len(held),schema_match=True); return held,_set_diag(stats)
 except (OSError,ValueError,TypeError): pass
 try:
  code,payload,headers=get_json(predictions_url(day)); stats.update(requests=1,http_statuses=[code],rate_limit_headers=headers)
  if code!=200 or payload is None: stats.update(status=_status(code),blocker=f"boggio: HTTP {code} or non-JSON payload"); return [],_set_diag(stats)
  rows,shape=parse_predictions(payload,day=day); stats["schema_match"]=shape; stats["sample"]=_sample(payload)
  if not shape: stats.update(status="unavailable",blocker="boggio: snapshot schema not recognized; raw sample retained"); return [],_set_diag(stats)
  source_items = payload.get("data") if isinstance(payload, dict) else payload
  stats["canonicalization_dropped"] = max(0, len(source_items or []) - len(rows)) if isinstance(source_items, list) else 0
  stats["bg_raw"]=len({(r["home"],r["away"]) for r in rows}); stats["bg_scored"]=len(rows); stats["status"]="ok" if rows else "empty"; return rows,_set_diag(stats)
 except UpstreamBlocked as e:
  msg=str(e); stats["http_429"]=_429; stats["status"]="cooldown" if _cooling else ("quota" if "429" in msg or "budget" in msg else _status(None)); stats["blocker"]=msg[:180]; stats["errors"]=[msg[:180]]; return [],_set_diag(stats)
def _scrub(value):
 secret=_key()
 if isinstance(value,str): return value.replace(secret,"[REDACTED]") if secret else value
 if isinstance(value,dict): return {str(k):_scrub(v) for k,v in value.items()}
 if isinstance(value,list): return [_scrub(v) for v in value]
 return value

def _sample(payload):
 data=payload.get("data") if isinstance(payload,dict) else payload
 return _scrub(data[0] if isinstance(data,list) and data else {"top_keys":list(payload)[:12]} if isinstance(payload,dict) else None)

def persist_shadow(day,rows,stats,*,localdata=None):
 root=localdata or LOCALDATA; root.mkdir(parents=True,exist_ok=True); path=_path(day,root)
 payload={"schema":1,"source":SOURCE,"date":day,"role":"approved average-bookmaker price donor (operator promotion 2026-10-03); NOT a named bookmaker, never counts as named-book corroboration","provenance":{"api":BASE+"/api/v2/predictions","hunt":"docs/operator/SOURCE-HUNT-2026-10.md#54","publication_lag":"free tier exposes predictions up to 12h ahead; published_at and captured_at are retained"},"stats":stats,"rows":rows}
 tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)); tmp.replace(path); return path
