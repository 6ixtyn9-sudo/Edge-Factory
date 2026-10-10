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
import hashlib, json, os, re, threading, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from edgefactory.identity import source_team_key
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

_active_key_index=0
_logical_calls=0

def configured_keys():
 """Ordered, de-duplicated ring. Singular key is fallback, never appended."""
 raw=os.environ.get("RAPIDAPI_KEYS") or os.environ.get(KEY_ENV) or ""
 return tuple(dict.fromkeys(k.strip() for k in raw.split(",") if k.strip()))

def reset_state():
 global _last,_calls,_429,_cooling,_active_key_index,_logical_calls
 _last=0.0; _calls=0; _429=0; _cooling=False; _active_key_index=0; _logical_calls=0; _DIAG.clear()

def diagnostics(): return dict(_DIAG)
def _set_diag(x): _DIAG.update(x); return x
def _key():
 keys=configured_keys()
 return keys[_active_key_index] if _active_key_index<len(keys) else None
def predictions_url(day): return BASE+"/api/v2/predictions?"+urllib.parse.urlencode({"iso_date":day,"market":"classic"})
def _headers(h): return {str(k):str(v) for k,v in (h.items() if hasattr(h,"items") else []) if "ratelimit" in str(k).lower() or str(k).lower()=="retry-after"}
def _status(code): return "auth" if code in (401,403) else "quota" if code in (402,429,509) else "unavailable"

def request_with_key(url, key, *, timeout=30):
 """One physical HTTP call, no retry; response/exception never exposes key."""
 global _last,_calls
 with _lock:
  wait=MIN_INTERVAL_S-(time.monotonic()-_last)
  if wait>0: time.sleep(wait)
  _last=time.monotonic(); _calls+=1
 req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"EdgeFactory-cooperative-shadow/1.0 (+operator review)","X-RapidAPI-Key":key,"X-RapidAPI-Host":API_HOST})
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r:
   body=r.read(8_000_000).decode("utf-8","replace")
   try: data=json.loads(body) if body else None
   except json.JSONDecodeError: data=None
   return int(getattr(r,"status",200)),data,_headers(r.headers)
 except urllib.error.HTTPError as e:
  return e.code,None,_headers(e.headers)
 except Exception as e:
  raise UpstreamBlocked(f"boggio: transport {type(e).__name__}") from None

def get_json(url, *, timeout=30):
 global _active_key_index,_logical_calls,_cooling,_429
 keys=configured_keys()
 if not keys: raise UpstreamBlocked("RAPIDAPI_KEYS/RAPIDAPI_KEY not set; shadow capture skipped")
 if _cooling: raise UpstreamBlocked("boggio: ring exhausted; run cooling down")
 if _logical_calls>=MAX_CALLS_PER_RUN: raise UpstreamBlocked("boggio: per-run logical call budget reached")
 _logical_calls+=1
 while _active_key_index<len(keys):
  index=_active_key_index
  code,data,headers=request_with_key(url,keys[index],timeout=timeout)
  _DIAG.setdefault("key_attempts",[]).append({"key_index":index+1,"status":code,"rate_limit_headers":headers})
  if code in (401,402,403,429,509):
   if code==429: _429+=1
   _active_key_index+=1
   continue
  if code>=400: raise UpstreamBlocked(f"boggio: HTTP {code}")
  return code,data,headers
 _cooling=True
 raise UpstreamBlocked("boggio: no eligible key in ring")

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
  # Additive (2026-10-10, card_enrich wire): retain the provider's fixture id from
  # the listing we ALREADY pay for. That is what lets a stats lane resolve fixture
  # ids out of the shadow ledger instead of spending a second family call on the
  # default listing. Nothing downstream reads it today; no row is dropped or
  # reordered because of it, and a row without an id simply reports event_id=None.
  provider_id=item.get("id")
  event_id=provider_id if isinstance(provider_id,int) and not isinstance(provider_id,bool) and provider_id>0 else None
  # The provider's documented zone contract (see DECLARED_ZONE) resolves the
  # naive London stamps the v2 feed actually emits. A stamp that violates
  # even that contract still fails closed to a missing join date.
  event_day=provider_kickoff_date(kickoff_text,declared_zone=DECLARED_ZONE)
  rows.append({
    "source":SOURCE,
    "event_id":event_id,
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
    # A ledger cached before the id was retained has no id to recover; mark it
    # explicitly absent so the enrichment lane reports "unresolved" rather than
    # silently treating a cached row as if it carried provider identity.
    out.setdefault("event_id", None)
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


# --------------------------------------------------------------------------------------
# card_enrich (Phase 2, approved 2026-10-10): ONE silent, budget-ledgered H2H lane.
#
# Shape fixed by the operator ruling - top-6 card fixtures by proximity to consensus
# certification, the /head-to-head/:id endpoint ONLY, one call per fixture, staleness
# skip (a snapshot captured < STALENESS_DAYS ago is not refetched), a hard monthly
# budget that spans every key in the ring, and pre-flight budget math printed on
# EVERY receipt. It never runs nightly: 6 calls x 7 days = 180/month does not fit a
# 100/key/month family, ~24-30 does at weekly cadence with staleness skips.
#
# This lane is capture-only. It writes a shadow ledger of pre-kickoff, identity-
# verified observations for the dormant context vocabulary in
# ``edgefactory.context_rules`` (``h2h_dominance`` today; ``form_gap``/``venue_split``/
# ``rest_days`` stay uncaptured). No rule is registered, no predicate is evaluated
# here, no pick path, display column, gate or notification reads or is changed by it.
# Activation authority is the pre-registered certification bars, not this file.
# --------------------------------------------------------------------------------------

H2H_ENDPOINT = "head-to-head"
CARD_ENRICH_SOURCE = "boggio_h2h"
CARD_ENRICH_STALENESS_DAYS = 7
CARD_ENRICH_BUDGET_ENV = "EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS"
CARD_ENRICH_RESERVE_ENV = "EDGE_FACTORY_CARD_ENRICH_RESERVE"
CARD_ENRICH_RESERVE_DEFAULT = 20
# A share computed from one or two encounters is noise, not a signal.
_MIN_SHARE_ENCOUNTERS = 3
QUOTA_REMAINING_HEADER = "x-ratelimit-match-stats-and-prediction-endpoints-remaining"


def _env_int(name, default):
    """Integer knob; unset, blank, or junk all fail closed to ``default``."""
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        value = int(str(raw).strip())
    except ValueError:
        return default
    return value if value >= 0 else default


def quota_remaining(headers):
    """The provider's own family-remaining counter, or ``None`` when unreported.

    ``X-RateLimit-Match-Stats-and-Prediction-endpoints-Remaining`` is the only
    trustworthy reading of a pool: our counters can only be as good as the calls
    we happened to observe. An absent header is recorded as UNKNOWN and spends
    nothing, never assumed to be a full pot.
    """
    if not isinstance(headers, dict):
        return None
    for key, value in headers.items():
        if str(key).strip().lower() == QUOTA_REMAINING_HEADER:
            try:
                remaining = int(str(value).strip())
            except (TypeError, ValueError):
                return None
            return remaining if remaining >= 0 else None
    return None


def key_fingerprint(key):
    """8-hex opaque pool identity. The ledger spans runs, so it must never hold
    a key value or a prefix of one - a digest only."""
    return hashlib.sha256(str(key or "").encode("utf-8")).hexdigest()[:8]


def key_label(key):
    """Last 4 characters of the secret, for OPERATOR RECOGNITION ONLY.

    A head prefix would be a usable credential fragment; a tail is not, and it
    is what lets an operator read a rate-limit header off a run and hand back
    "pool *******xyz = 31" without ever pasting a key into a receipt, ledger,
    log, or commit. Empty-safe.
    """
    return str(key or "")[-4:]


def _allowance_lookup(allowances, fingerprint):
    """Accept a fingerprint or a key tail when a reading is supplied by hand."""
    if fingerprint in allowances:
        return allowances[fingerprint]
    matches = [value for key, value in allowances.items()
               if isinstance(key, str) and len(str(fingerprint)) >= 3 and key.endswith(str(fingerprint))]
    return matches[0] if len(matches) == 1 else None


def family_month(day):
    """The boggio family's accounting window: a calendar month, not a calendar day."""
    return str(day or "")[:7]


def ledger_path(localdata=None):
    return (localdata or LOCALDATA) / "card_enrich_call_ledger.jsonl"


def read_call_ledger(localdata=None, *, month=None):
    """Append-only per-call ledger. Corrupt lines are skipped, never fatal: a
    half-written tail must not disable the budget that protects the quota."""
    path = ledger_path(localdata)
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []
    entries = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict) and (month is None or entry.get("month") == month):
            entries.append(entry)
    return entries


def write_call_ledger(entries, localdata=None, *, retention_days=120, today=None):
    """Rewrite the ledger keeping the trailing ``retention_days`` of months.

    Bounded retention is a deliberate part of the design: the ledger is the
    budget, but a file that outlives every reset window would only ever be
    read by an accounting rule that has already rolled over.
    """
    path = ledger_path(localdata)
    day = today or datetime.now(timezone.utc).date()
    try:
        keep_from = (day - timedelta(days=retention_days)).isoformat()[:7]
    except (TypeError, ValueError):
        keep_from = None
    kept = [e for e in entries if keep_from is None or str(e.get("month") or "") >= keep_from]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in kept))
    tmp.replace(path)
    return len(kept)


def spend_by_key(entries):
    """Attributed, actually-charged calls per key in the current window."""
    spend: dict[str, int] = {}
    for entry in entries:
        if not entry.get("charged"):
            continue
        fingerprint = str(entry.get("key") or "unknown")
        spend[fingerprint] = spend.get(fingerprint, 0) + 1
    return spend


def month_budget():
    """Hard monthly ceiling across BOTH pools. Unset or 0 = disabled (fail closed):
    a capture that cannot prove its own budget is not allowed to spend quota."""
    return _env_int(CARD_ENRICH_BUDGET_ENV, 0)


def allowance_per_key(month_spend, *, keys=None, observed_remaining=None):
    """Per-key remaining allowance for this month, from provider headers first.

    ``observed_remaining`` maps key fingerprint -> the last family-remaining
    counter the provider actually reported. That reading, minus the reserve we
    hold back for the production price donor, is the pool's real headroom; the
    env ceiling then clamps the WHOLE ring, so the sum can never exceed it.
    A key with no header reading gets no allowance at all.
    """
    keys = tuple(keys if keys is not None else configured_keys())
    reserve = _env_int(CARD_ENRICH_RESERVE_ENV, CARD_ENRICH_RESERVE_DEFAULT)
    ceiling = month_budget()
    observed = dict(observed_remaining or {})
    labels = {key_fingerprint(key): key_label(key) for key in keys}
    allowances: list[int] = []
    for key in keys:
        fingerprint = key_fingerprint(key)
        remaining = _allowance_lookup(observed, fingerprint)
        if remaining is None:
            remaining = _allowance_lookup(observed, labels[fingerprint])
        if remaining is None:
            # No provider reading for this pool = no allowance. An unmeasured
            # pot is never assumed to be a full one.
            allowances.append(0)
            continue
        headroom = int(remaining) - reserve - int(month_spend.get(fingerprint, 0))
        if ceiling:
            headroom = min(headroom, max(0, ceiling - sum(allowances)))
        allowances.append(max(0, headroom))
    if not ceiling:
        return {}
    total = min(ceiling, sum(allowances))
    # Spread the ring-wide ceiling back over the keys in ring order.
    left, out = total, {}
    for key, allowance in zip(keys, allowances):
        take = min(allowance, left)
        if take > 0:
            out[key_fingerprint(key)] = take
            left -= take
    return out


def preflight(*, need_h2h, need_listing, keys=None, localdata=None, day=None, observed_remaining=None):
    """MANDATORY pre-flight arithmetic, on every run, before a single call.

    Returns the plan even when the answer is zero: ``budget_disabled`` and
    ``unattributed_quota`` are receipts, not silence.
    """
    day = day or datetime.now(timezone.utc).date().isoformat()
    keys = tuple(keys if keys is not None else configured_keys())
    month_spend = spend_by_key(read_call_ledger(localdata, month=family_month(day)))
    allowances = allowance_per_key(month_spend, keys=keys,
                                   observed_remaining=observed_remaining)
    spendable = sum(allowances.values())
    needed = max(0, int(need_h2h)) + max(0, int(need_listing))
    if month_budget() <= 0:
        verdict, allowed = "budget_disabled", 0
    elif not keys:
        verdict, allowed = "no_keys", 0
    elif not allowances:
        verdict, allowed = "unattributed_quota", 0
    elif spendable <= 0:
        verdict, allowed = "budget_exhausted", 0
    elif needed > spendable:
        verdict, allowed = "budget_degraded", spendable
    else:
        verdict, allowed = "approved", needed
    return {
        "pool_labels": {key_fingerprint(key): key_label(key) for key in keys},
        "budget_env": CARD_ENRICH_BUDGET_ENV,
        "budget_monthly": month_budget(),
        "reserve_per_key": _env_int(CARD_ENRICH_RESERVE_ENV, CARD_ENRICH_RESERVE_DEFAULT),
        "ring_keys": len(keys),
        "month": family_month(day),
        "month_spend_by_key": dict(sorted(month_spend.items())),
        "allowance_by_key": dict(sorted(allowances.items())),
        "spendable": spendable,
        "need_h2h": int(need_h2h),
        "need_listing": int(need_listing),
        "need_total": needed,
        "allowed_calls": allowed,
        "verdict": verdict,
        "math": (f"calls={needed} (h2h={int(need_h2h)} + listing={int(need_listing)}) "
                 f"x 1 family-unit vs spendable={spendable} "
                 f"[pools={len(keys)} cap={month_budget()} reserve={_env_int(CARD_ENRICH_RESERVE_ENV, CARD_ENRICH_RESERVE_DEFAULT)} "
                 f"spent={sum(month_spend.values())} month={family_month(day)}] -> {verdict}"),
    }


def print_preflight(plan, *, log=print):
    """The pre-flight budget math line is not optional in any caller."""
    log(f"ledger=card_enrich_preflight {plan['math']}")
    log(f"ledger=card_enrich_preflight detail month_spend={plan['month_spend_by_key']} "
        f"allowance={plan['allowance_by_key']} needed={plan['need_total']} allowed={plan['allowed_calls']} "
        f"pools={ {fp: f'***{tail}' for fp, tail in plan['pool_labels'].items()} }")


def h2h_url(fixture_id):
    if not isinstance(fixture_id, int) or isinstance(fixture_id, bool) or fixture_id <= 0:
        raise ValueError("boggio fixture id must be a positive integer")
    return BASE + f"/api/v2/{H2H_ENDPOINT}/{fixture_id}"


def _parse_score(text):
    """'2 - 1' / '2-1' -> (2, 1). Anything else is an unknown score, never a guess."""
    match = re.match(r"^\s*(\d{1,2})\s*[-:]\s*(\d{1,2})\s*$", str(text or ""))
    if not match:
        return None
    return (int(match[1]), int(match[2]))


def _encounter_date(value):
    """Provider encounter stamps are plain dates; a full ISO stamp is tolerated.

    A date we cannot resolve is dropped rather than defaulted - an undated
    encounter cannot satisfy "strictly before kickoff" and would leak a
    possibly-post-kickoff observation into a pre-match feature.
    """
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _aware(value):
    """ISO stamp to an aware UTC datetime; naive or junk returns None (fail closed)."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp.astimezone(timezone.utc)


def parse_head_to_head(payload, *, fixture, captured_at):
    """Derive the dormant-vocabulary snapshot from one H2H response.

    ``fixture`` supplies the verified identity claim (card team keys + provider
    kickoff). Two guards, both pre-registered:

    * identity is only verified when the provider's own dated encounters name
      BOTH card teams (folded through ``source_team_key``). A payload about two
      other clubs is not this fixture, whatever the request URL said;
    * every encounter is filtered to dates strictly before the target kickoff,
      and the whole snapshot is only eligible while the capture instant precedes
      kickoff. The as-of of a dated row is WHEN WE OBSERVED IT, never the
      encounter date: the provider publishes no per-row history timestamp, so a
      pre-kickoff capture is the strongest point-in-time bound available.
    """
    home_key = source_team_key(fixture.get("home"))
    away_key = source_team_key(fixture.get("away"))
    kickoff = _aware(fixture.get("kickoff_utc"))
    capture = _aware(captured_at)
    data = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(data, dict):
        return {"identity_verified": False, "usable": False, "reason": "no_data_object",
                "captured_at": captured_at, "kickoff_utc": fixture.get("kickoff_utc"),
                "encounters": [], "features": {}, "h2h_stats": None}
    raw_encounters = data.get("encounters")
    raw_encounters = raw_encounters if isinstance(raw_encounters, list) else []
    lookback_days = _env_int("EDGE_FACTORY_CARD_ENRICH_LOOKBACK_DAYS", 1095)
    encounters, identity_hits, dropped = [], 0, {"undated": 0, "not_before_kickoff": 0, "too_old": 0}
    for row in raw_encounters:
        if not isinstance(row, dict):
            continue
        day = _encounter_date(row.get("start_date") or row.get("date"))
        if day is None:
            dropped["undated"] += 1
            continue
        if kickoff is not None and day >= kickoff.date():
            dropped["not_before_kickoff"] += 1
            continue
        if capture is not None and (capture.date() - day).days > lookback_days:
            dropped["too_old"] += 1
            continue
        row_home, row_away = source_team_key(row.get("home_team")), source_team_key(row.get("away_team"))
        if {row_home, row_away} == {home_key, away_key} and home_key and away_key and row_home != row_away:
            identity_hits += 1
        encounters.append({
            "home_team": row.get("home_team"), "away_team": row.get("away_team"),
            "date": day.isoformat(),
            "competition": row.get("competition_name"), "season": row.get("season"),
            "fulltime": list(_parse_score(row.get("fulltime_result"))) if _parse_score(row.get("fulltime_result")) else None,
            "first_half": list(_parse_score(row.get("first_half_result"))) if _parse_score(row.get("first_half_result")) else None,
            # as-of = observation time of the whole row, per the point-in-time rule.
            "as_of": captured_at,
            "as_of_basis": "capture_instant; provider publishes no per-row history timestamp",
        })
    stats = data.get("stats") if isinstance(data.get("stats"), dict) else {}
    overall = stats.get("overall") if isinstance(stats.get("overall"), dict) else {}
    home_stats = stats.get("home_team") if isinstance(stats.get("home_team"), dict) else {}
    away_stats = stats.get("away_team") if isinstance(stats.get("away_team"), dict) else {}
    features: dict[str, object] = {}
    home_won, away_won = home_stats.get("won"), away_stats.get("won")
    if (isinstance(home_won, int) and not isinstance(home_won, bool)
            and isinstance(away_won, int) and not isinstance(away_won, bool)):
        features["h2h_dominance"] = home_won - away_won
    # The documented contract publishes no overall draw count, so the draw
    # share is derived from the rows WE filtered - reproducible from the ledger,
    # never a provider aggregate we cannot audit.
    if len(encounters) >= _MIN_SHARE_ENCOUNTERS:
        draws = sum(1 for row in encounters
                    if row.get("fulltime") and row["fulltime"][0] == row["fulltime"][1])
        features["h2h_draw_share"] = round(draws / len(encounters), 4)
    usable = bool(identity_hits and kickoff is not None and capture is not None and capture < kickoff)
    reason = None
    if not identity_hits:
        reason = "unverified_identity"
    elif kickoff is None:
        reason = "kickoff_unknown"
    elif capture is None:
        reason = "capture_stamp_unparseable"
    elif capture >= kickoff:
        reason = "captured_at_or_after_kickoff"
    elif not encounters:
        reason = "no_usable_encounters"
    return {
        "identity_verified": bool(identity_hits),
        "usable": usable and bool(encounters),
        "reason": reason if (not usable or not encounters) else None,
        "fixture_home": fixture.get("home"), "fixture_away": fixture.get("away"),
        "fixture_home_key": home_key or None, "fixture_away_key": away_key or None,
        "kickoff_utc": fixture.get("kickoff_utc"), "captured_at": captured_at,
        "encounters": encounters, "encounters_dropped": dropped,
        "h2h_stats": {"overall": overall or None, "home_team": home_stats or None, "away_team": away_stats or None},
        "features": features,
    }


def snapshot_path(day, localdata=None):
    return (localdata or LOCALDATA) / f"card_enrich_shadow_{day}.json"


def load_snapshots(localdata=None):
    """fixture key -> last snapshot, so a fresh-enough H2H is never refetched."""
    root = localdata or LOCALDATA
    latest: dict[str, dict] = {}
    try:
        files = sorted(root.glob("card_enrich_shadow_*.json"))
    except OSError:
        return {}
    for path in files:
        try:
            payload = json.loads(path.read_text())
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        for snapshot in payload.get("snapshots", []):
            if isinstance(snapshot, dict) and snapshot.get("fixture_key"):
                latest[str(snapshot["fixture_key"])] = snapshot
    return latest


def needs_capture(fixture_key, snapshots, *, day, staleness_days=CARD_ENRICH_STALENESS_DAYS):
    """True only when no snapshot of this fixture is younger than ``staleness_days``."""
    existing = snapshots.get(str(fixture_key))
    if not isinstance(existing, dict):
        return True
    captured = _aware(existing.get("captured_at")) or _encounter_date(existing.get("captured_at"))
    today = _encounter_date(day)
    if captured is None or today is None:
        return True
    if isinstance(captured, datetime):
        captured = captured.date()
    try:
        age_days = (today - captured).days
    except TypeError:
        return True
    return age_days >= max(1, int(staleness_days))


def h2h_call(fixture_id, *, allow_key_advance=True):
    """One ring-rotated H2H call (the only endpoint this lane may ever hit)."""
    return _ring_call(h2h_url(fixture_id), allow_key_advance=allow_key_advance)


def listing_call(day, *, allow_key_advance=True):
    """One ring-rotated default-listing call, for fixture-id resolution ONLY.

    The default listing draws from the same monthly family pot as the stats
    endpoints (proven 42 -> 41, then 33 -> 32), so no caller reaches this
    without the pre-flight count having already charged it. Prefer the
    retained ``event_id`` in the shadow ledger; this is the last resort.
    """
    return _ring_call(predictions_url(day), allow_key_advance=allow_key_advance)


def _ring_call(url, *, allow_key_advance=True):
    """One ring-rotated family call, with the provider's quota header retained.

    ``attempts`` is recorded in the module diagnostics, exactly as the
    production lane records its own, so a rejected key is attributable without
    printing anything that identifies it. Deliberately NOT ``get_json``: that is
    the production price lane's budget (one logical call per run) and its
    cooldown flag would strand the daily capture. This lane keeps its own per-key
    cursor and paces through the same module-level minimum interval, so both
    lanes share one throttle.
    """
    global _active_key_index
    keys = configured_keys()
    if not keys:
        raise UpstreamBlocked("RAPIDAPI_KEYS/RAPIDAPI_KEY not set; card_enrich skipped")
    start = _active_key_index % len(keys)
    attempts, last_status, touched = [], None, start
    for offset in range(len(keys)):
        index = touched = (start + offset) % len(keys)
        try:
            code, payload, headers = request_with_key(url, keys[index])
        except UpstreamBlocked as failure:
            # A transport that dies before any response exists would otherwise
            # leave the caller with no pool to charge; see ``_attributed``.
            raise _attributed(failure, keys, index, len(attempts)) from None
        attempts.append({"key_index": index + 1, "status": code, "rate_limit_headers": headers})
        last_status = code
        if code in (401, 402, 403, 429, 509):
            continue
        if code >= 400:
            raise _attributed(UpstreamBlocked(f"boggio: HTTP {code}"), keys, index, len(attempts))
        if allow_key_advance:
            # Next caller starts at the next pool: the ring is spread evenly
            # instead of hammering whichever key happens to be current.
            _active_key_index = (index + 1) % len(keys)
        return keys[index], index, code, payload, _scrub(headers)
    _DIAG.setdefault("card_enrich_attempts", []).extend(attempts)
    raise _attributed(UpstreamBlocked(f"boggio: ring failed (last status {last_status})"),
                      keys, touched, len(attempts))


def _attributed(exc: UpstreamBlocked, keys, pool_index: int, attempts: int) -> UpstreamBlocked:
    """Carry the touched pool on the exception so a failure still gets an
    attributed ledger line - the one thing the budget rules forbid losing.

    The pool is taken from the loop cursor rather than from ``attempts``, because
    a transport that dies before any response appends nothing: "one pool was
    touched and I can name it" must survive even a zero-byte failure. The KEY is
    carried for the caller to digest (``record_call`` hashes it); it is never
    rendered into a receipt.
    """
    exc.ring_attempts = max(1, int(attempts))               # type: ignore[attr-defined]
    exc.ring_pool_index = int(pool_index)                  # type: ignore[attr-defined]
    exc.ring_key = keys[int(pool_index) % len(keys)]       # type: ignore[attr-defined]
    return exc


def record_call(entries, *, day, fixture_key, endpoint, pool_index, key, status, remaining,
                spent, what_bought, error=None):
    """Per-call ledger entry: opaque key digest, header readings, and what it bought."""
    entries.append({
        "month": family_month(day), "date": str(day), "source": CARD_ENRICH_SOURCE,
        "endpoint": endpoint, "fixture_key": str(fixture_key or ""),
        "pool_index": int(pool_index) + 1 if isinstance(pool_index, int) else None,
        "key": key_fingerprint(key), "key_tail": key_label(key),
        "status": int(status) if isinstance(status, int) else None,
        "family_remaining": remaining, "charged": bool(spent),
        "what_it_bought": str(what_bought or "")[:200],
        "error_class": type(error).__name__ if error is not None else None,
        "logged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    return entries[-1]


def persist_snapshots(day, snapshots, preflight_plan, *, localdata=None, notes=None):
    """Write this run's day-scoped snapshot ledger (raw payload never stored)."""
    root = localdata or LOCALDATA
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": 1, "source": CARD_ENRICH_SOURCE, "run_date": str(day),
        "role": ("silent pre-kickoff H2H context capture for the dormant context vocabulary; "
                 "NOT a price, NOT a vote, NOT a registered rule"),
        "provenance": {
            "api": BASE + "/api/v2/" + H2H_ENDPOINT + "/:id",
            "cadence": "weekly at most (6x7=180/month does not fit a 100/key/month family; ~24-30 does)",
            "point_in_time": "as_of is the capture instant; provider publishes no per-row history timestamp",
        },
        "preflight": preflight_plan,
        "stats": {"snapshots": len(snapshots), "usable": sum(1 for s in snapshots if s.get("usable"))},
        "notes": list(notes or []),
        "snapshots": snapshots,
    }
    path = snapshot_path(day, root)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    return path

