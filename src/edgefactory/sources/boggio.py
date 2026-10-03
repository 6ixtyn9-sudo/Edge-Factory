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
import json, os, threading, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from edgefactory.odds_normalization import (
    canonical_market_selection,
    parse_declared_zone_timestamp,
    parse_zoned_timestamp,
    provider_kickoff_date,
)

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

# The v2 feed's documented timestamp contract. start_date and last_update_at
# are NAIVE ISO stamps ("2018-12-06T19:00:00", "2018-12-04T20:11:57.506000")
# whose wall clock is the API server's Europe/London (GMT/BST) time:
# "The GMT/BST start date of the predicted event", "Day starts at 00:00
# London Timezone" (developer.boggio-analytics.com, API endpoints + how-tos;
# the official examples localize with pytz Europe/London).
#
# Rounds 1-2 assumed a "YYYY-MM-DD HH:MM:SS UTC" suffix instead. That shape
# appears nowhere in the provider's documentation, the shared parser (rightly)
# refused the zone-free stamps the feed actually emits, and every Boggio row
# kept joining with no date. The zone below is the provider's own contract,
# not an assumption on our side; the shared parser still fails closed for
# every provider that does not document one.
DECLARED_ZONE = "Europe/London"

# The provider's London clock face runs up to +1h ahead of UTC (BST). A
# published_at that is ahead of our capture clock by no more than that face
# difference is the same instant written on the provider's clock, not a
# lookahead artefact; anything further ahead cannot be explained by the zone.
_DECLARED_ZONE_MAX_SKEW = timedelta(hours=1)


def price_donor_enabled() -> bool:
    """Operator switch that lets Boggio's average price reach a ticket."""
    raw = os.environ.get("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR")
    if raw is None or not raw.strip():
        return True  # operator-requested default-on
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_stamp(value):
    """Parse a Boggio stamp under the provider's documented zone contract.

    Zone-bearing shapes (if the feed ever emits them) are honoured as written
    through the shared parser. A naive stamp is localised to the documented
    Europe/London zone. Anything else - including a date with no time -
    returns ``None``; this adapter never falls back to the capture date or
    the capture machine's locale.
    """
    return parse_declared_zone_timestamp(value, DECLARED_ZONE)


def timestamp_suspect(published_at, captured_at) -> bool:
    """True when the row claims to have been published after we saw it.

    A future publication stamp is the signature of a lookahead artefact. It
    is never an error we can correct, so the row stays visible but loses
    price eligibility.

    A ``published_at`` that names its own zone is an absolute claim and is
    compared strictly. A naive ``published_at`` carries the provider's
    documented London clock face, which can sit up to +1h (BST) ahead of
    UTC; exactly that documented face difference is allowed and nothing
    more, so the zone contract cannot manufacture a false suspicion and a
    genuine lookahead still fails.
    """
    published, captured = _parse_stamp(published_at), _parse_stamp(captured_at)
    if published is None or captured is None:
        return False
    if parse_zoned_timestamp(published_at) is not None:
        return published > captured
    return published > captured + _DECLARED_ZONE_MAX_SKEW


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
  canonical, failure = canonical_market_selection(
    raw_market, prediction, home=home, away=away,
  )
  # An unmappable prediction (the feed answers "1X"/"12"/"X2" whenever its
  # model declines a single side) used to be dropped here.  A dropped row
  # cannot be counted, so the join-miss report could never show why Boggio
  # contributed nothing.  Keep the row with its RAW provider vocabulary and
  # mark it non-priceable; the shared bundle boundary buckets it by reason.
  mappable = canonical is not None
  market = canonical.market if mappable else raw_market
  selection = canonical.selection if mappable else prediction
  average_price=_selection_odds(odds,prediction)
  suspect=timestamp_suspect(published,stamp)
  kickoff=item.get("start_date")
  kickoff_text=str(kickoff or "")
  # The provider's documented zone contract (see DECLARED_ZONE) resolves the
  # naive London stamps the v2 feed actually emits. A stamp that violates
  # even that contract still fails closed to a missing join date.
  event_day=provider_kickoff_date(kickoff_text,declared_zone=DECLARED_ZONE)
  rows.append({
    "source":SOURCE,
    "date":event_day,
    "home":home,
    "away":away,
    "kickoff":kickoff,
    "market":market,
    "selection":selection,
    "raw_market":raw_market,
    "raw_selection":prediction,
    "canonicalization_mappable":mappable,
    "canonicalization_reason":(failure.reason if failure is not None else None),
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
    "price_push_eligible":bool(event_day and mappable and average_price is not None and price_donor_enabled() and not suspect),
    "timestamp_suspect":suspect,
    "odds_provenance":odds,
    "published_at":published,
    "captured_at":stamp,
    "lookahead_note":LOOKAHEAD_NOTE,
  })
 return rows,shaped


def _path(day,localdata=None): return (localdata or LOCALDATA)/f"{SOURCE}_shadow_{day}.json"

def reattribute_shadow_row(row):
    """Re-derive the stamp-dependent fields of a cached shadow row.

    A cached ledger can predate a stamp-contract repair: its rows then hold
    ``date=None`` and ``price_push_eligible=False`` even though the raw
    ``kickoff``/``published_at`` values they retained are perfectly
    parseable under the current contract. Re-deriving from the RAW fields
    makes a cached row exactly what a fresh capture would have produced -
    the ledger self-heals instead of pinning pre-repair verdicts for the
    rest of the day. Raw values are never rewritten; only derived fields
    move, and only to what the current code derives from them.
    """
    out=dict(row)
    home=out.get("home"); away=out.get("away")
    raw_market=out.get("raw_market") or out.get("market") or "classic"
    raw_selection=out.get("raw_selection") or out.get("selection")
    canonical,_failure=canonical_market_selection(raw_market,raw_selection,home=home,away=away)
    mappable=canonical is not None
    event_day=provider_kickoff_date(out.get("kickoff"),declared_zone=DECLARED_ZONE)
    suspect=timestamp_suspect(out.get("published_at"),out.get("captured_at"))
    # Ledgers cached before the price-donor promotion carry no ``odds`` key,
    # only the raw ``odds_provenance`` object; re-derive the average price
    # from it exactly as a fresh capture would have.
    odds=_num(out.get("odds")) if out.get("odds") is not None else (
        _selection_odds(out.get("odds_provenance"),raw_selection) if isinstance(out.get("odds_provenance"),dict) else None)
    out["odds"]=odds
    out["date"]=event_day
    out["timestamp_suspect"]=suspect
    out["price_push_eligible"]=bool(event_day and mappable and odds is not None and odds>1.0 and price_donor_enabled() and not suspect)
    return out

def capture_day(day,*,localdata=None):
 stats={"status":"not_run","bg_raw":0,"bg_scored":0,"requests":0,"http_statuses":[],"http_429":0,"errors":[],"blocker":None,"schema_match":None,"budget":1}
 reset_state()
 if not _key(): stats["blocker"]=f"{KEY_ENV} not set; shadow capture skipped"; return [],_set_diag(stats)
 try:
  held=json.loads(_path(day,localdata).read_text()).get("rows",[])
  if held:
   # Heal the cache before serving it: rows cached by a pre-repair parser
   # keep their raw evidence but regain the derived fields the current
   # contract produces. persist_shadow (called by the capture orchestrator)
   # writes the healed rows back, so the ledger converges without a refetch.
   held=[reattribute_shadow_row(r) for r in held if isinstance(r,dict)]
   stats.update(status="cache_only",cache_hits=1,bg_raw=len(held),bg_scored=len(held),schema_match=True); return held,_set_diag(stats)
 except (OSError,ValueError,TypeError): pass
 try:
  code,payload,headers=get_json(predictions_url(day)); stats.update(requests=1,http_statuses=[code],rate_limit_headers=headers)
  if code!=200 or payload is None: stats.update(status=_status(code),blocker=f"boggio: HTTP {code} or non-JSON payload"); return [],_set_diag(stats)
  rows,shape=parse_predictions(payload,day=day); stats["schema_match"]=shape; stats["sample"]=_sample(payload)
  if not shape: stats.update(status="unavailable",blocker="boggio: snapshot schema not recognized; raw sample retained"); return [],_set_diag(stats)
  source_items = payload.get("data") if isinstance(payload, dict) else payload
  # Unmappable rows are retained (never dropped) so they stay countable.
  # "dropped" now means "captured but not priceable", with a reason census.
  stats["canonicalization_dropped"] = sum(1 for r in rows if r.get("canonicalization_mappable") is False) + (
    max(0, len(source_items) - len(rows)) if isinstance(source_items, list) else 0)
  reasons: dict[str, int] = {}
  for r in rows:
   reason = r.get("canonicalization_reason")
   if reason:
    reasons[str(reason)] = reasons.get(str(reason), 0) + 1
  stats["canonicalization_drop_reasons"] = dict(sorted(reasons.items()))
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
