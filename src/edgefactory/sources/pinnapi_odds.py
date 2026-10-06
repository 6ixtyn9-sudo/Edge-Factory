"""pinnapi Pinnacle price shadow adapter (SHADOW-01 T3, HUNT-01 shortlist #3).

Named-book price donor candidate: pinnapi relays **Pinnacle** pre-match
snapshots (live+prematch REST, free tier 100 requests/day, no card) after
Pinnacle closed its own public API on 2025-07-23. It is an **unofficial
third-party feed** - expect death without notice; the adapter is disposable
by design and fail-closed on anything unexpected.

Hard role rules (until an explicit operator promotion after the promotion
criteria in docs/operator/TICKETS-OPEN.md are met):

- SHADOW ONLY: rows land in a per-date ledger; nothing in the pick path,
  consensus, or the price-corroboration stamp reads them. There is no flag
  that can turn them on short of new operator-approved code.
- **Never a vote.**
- Corroboration semantics (documented contract for the future promoter):
  pinnapi may corroborate ONLY same-day-fetched prices - ``same_day_rows``
  is the gate any future corroborator must call; stale or missing means
  ABSTAIN, and SCOUTINGSTATS_SOLE push=False behavior is unaffected while
  this source is down or stale.

Verified vs unverified (HUNT-01 SOURCE-HUNT-2026-10 section 5.7):
- VERIFIED: free tier exists (100 REST requests/day, no card), endpoints
  /kit/v1/markets (bulk snapshot per sport), /kit/v1/details, /health.
- KNOWN FROM THE VENDOR'S PANEL PLAYGROUND (supersedes this adapter's
  original assumption): REST authenticates with an ``x-portal-apikey``
  **request header**, and soccer is ``sport_id=1``. The earlier text here
  said the SSE docs' ``key=`` query auth was assumed to apply to REST and
  that soccer was ``sport_id=2``; both were wrong, and the sport id was
  additionally written down as if it were a receipt. The ``key=`` query
  form is retained ONLY as a fallback retried on HTTP 401, and the ledger
  stats record which mechanism actually answered.
- STILL UNVERIFIED: the response schema, and whether a prematch snapshot
  returns anything for our fixtures at all. Any non-200 or unrecognized
  shape stays ``unavailable`` (fail-closed, retryable); a 200 that yields
  no usable rows records the observed payload shape rather than guessing a
  parser for it. scripts/probe_pinnapi.py is the acceptance tool that
  reconciles auth + schema before any promotion discussion; a trimmed raw
  sample is retained in the ledger stats so a parser adjustment needs no
  new crawl.

Resilience contract mirrors bzzoiro_odds.py / betexplorer_odds.py: cache-
first per date (a held date is never refetched), single-flight throttle,
Retry-After-first 30-60s backoff, run-scoped cool-down after repeated 429s,
hard per-run call budget, and zero-row auth/quota/unavailable days stay
RETRYABLE - never terminal.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from edgefactory.odds_normalization import canonical_market_selection

SOURCE = "pinnapi_odds"
BASE = os.environ.get("PINNAPI_BASE_URL", "https://pinnapi.com").rstrip("/")
KEY_ENV = "PINNAPI_KEY"
# Soccer is sport_id=1 (vendor panel playground). Overridable without a code
# change if the vendor renumbers its sports; a /sports introspection response
# has never been captured, so the override is the escape hatch, not a comment.
SPORT_ID_ENV = "EDGE_FACTORY_PINNAPI_SPORT_ID"
SPORT_ID = 1
EVENT_TYPE = "prematch"
# REST auth is a request header, not a query parameter. The query form below
# is kept only as a 401 fallback; see fetch_markets().
AUTH_HEADER = "x-portal-apikey"
AUTH_HEADER_FIRST = "header"
AUTH_QUERY_FALLBACK = "query"
# HTTP codes that are a question about the auth MECHANISM, so the other form
# is worth one retry. 403 is included because cheap relays use it for a
# rejected credential as readily as 401; if it turns out to be a plan
# restriction instead, the second attempt says so in the record.
AUTH_FALLBACK_STATUSES = (401, 403)
BOOK = "Pinnacle"
UA = "EdgeFactory-cooperative-shadow/1.0 (+operator review)"
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_PINNAPI_MIN_INTERVAL_S", "2.0"))
MAX_CALLS_PER_RUN = int(os.environ.get("EDGE_FACTORY_PINNAPI_MAX_CALLS", "4"))
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))

_LOCK = threading.Lock()
_LAST_REQUEST = 0.0
_429S = 0
_COOLING_DOWN = False
_CALLS_THIS_RUN = 0
_DIAG: dict[str, Any] = {}
_CANONICALIZATION_DROP_REASONS: dict[str, int] = {}
# Which auth mechanism was tried, and what each attempt answered. Recorded so
# the next operator reads the answer instead of re-deriving it.
_AUTH_ATTEMPTS: list[dict[str, Any]] = []
_AUTH_MECHANISM: str | None = None
# Run-scoped memory: once the header form has been rejected as unauthorized,
# later captures in the same process go straight to the fallback instead of
# spending a call rediscovering the same 401. Deliberately NOT cleared by
# reset_state(), which is per-capture; see reset_auth_memory().
_HEADER_AUTH_REJECTED = False
# MAX_CALLS_PER_RUN is enforced per CAPTURE, not per run: capture_day calls
# reset_state() on entry, which zeroes the counter. With one capture per run
# (the only caller today) the two are the same thing; across several captures
# there is no run-level ceiling at all. Rather than silently change a cap
# this work order was told not to touch, the real spend is counted here and
# reported, so the discrepancy is visible to the operator who owns the cap.
_CALLS_THIS_PROCESS = 0

# Zero-row days with these statuses stay RETRYABLE (never terminal "empty").
RETRYABLE_ZERO_ROW_STATUSES = {"auth", "quota", "unavailable", "blocked", "error", "cooldown"}

# Market-name aliases -> canonical market names. Unknown names are kept
# verbatim (lowercased) so nothing is silently mis-mapped.
_MARKET_ALIASES = {
    "1x2": "1x2",
    "moneyline": "1x2",
    "12": "1x2",
    "totals": "totals",
    "over_under": "totals",
    "total": "totals",
    "spreads": "spreads",
    "handicap": "spreads",
    "asian_handicap": "spreads",
    "ah": "spreads",
}


class UpstreamBlocked(RuntimeError):
    """Polite abort: rate limit, auth wall, or cool-down."""


def reset_state() -> None:
    global _LAST_REQUEST, _429S, _COOLING_DOWN, _CALLS_THIS_RUN
    global _AUTH_ATTEMPTS, _AUTH_MECHANISM
    _LAST_REQUEST = 0.0
    _429S = 0
    _COOLING_DOWN = False
    _CALLS_THIS_RUN = 0
    _AUTH_ATTEMPTS = []
    _AUTH_MECHANISM = None


def _api_key() -> str | None:
    value = os.environ.get(KEY_ENV)
    return value.strip() if value and value.strip() else None


def sport_id() -> int:
    """Soccer sport id, env-overridable (``EDGE_FACTORY_PINNAPI_SPORT_ID``).

    Soccer is 1. This used to be 2, carried by a comment that read like a
    captured receipt; nothing had been captured, and the wrong id silently
    cost four days. An unparseable override falls back to the constant
    rather than sending garbage upstream.
    """
    raw = os.environ.get(SPORT_ID_ENV)
    if raw is None or not str(raw).strip():
        return SPORT_ID
    try:
        return int(str(raw).strip())
    except ValueError:
        return SPORT_ID


def reset_auth_memory() -> None:
    """Start a fresh run: forget the 401 memory and the run call tally.

    reset_state() intentionally leaves both alone: the per-capture state
    resets every call, but "the header form was rejected" is a fact about
    the run, and re-learning it costs a call out of a budget of four.
    """
    global _HEADER_AUTH_REJECTED, _CALLS_THIS_PROCESS
    _HEADER_AUTH_REJECTED = False
    _CALLS_THIS_PROCESS = 0


def calls_this_process() -> int:
    """Calls actually issued since the run began, across all captures."""
    return _CALLS_THIS_PROCESS
# MAX_CALLS_PER_RUN is enforced per CAPTURE, not per run: capture_day calls
# reset_state() on entry, which zeroes the counter. With one capture per run
# (the only caller today) the two are the same thing; across several captures
# there is no run-level ceiling at all. Rather than silently change a cap
# this work order was told not to touch, the real spend is counted here and
# reported, so the discrepancy is visible to the operator who owns the cap.
_CALLS_THIS_PROCESS = 0


def header_auth_rejected() -> bool:
    """True once header auth has answered 401 anywhere in this run."""
    return _HEADER_AUTH_REJECTED


def auth_mechanism() -> str | None:
    """Mechanism that carried the last successful snapshot, if any."""
    return _AUTH_MECHANISM


def auth_attempts() -> list[dict[str, Any]]:
    """Per-attempt record of (mechanism, HTTP status). Never the key."""
    return [dict(attempt) for attempt in _AUTH_ATTEMPTS]


def _set_diag(stats: dict[str, Any]) -> dict[str, Any]:
    _DIAG.update(stats)
    return stats


def diagnostics() -> dict[str, Any]:
    """Safe operational diagnostics for the last capture; never the key."""
    return dict(_DIAG)


def _retry_after_seconds(value: str | None) -> float:
    if not value:
        return 30.0
    try:
        return max(30.0, min(60.0, float(value)))
    except ValueError:
        try:
            stamp = parsedate_to_datetime(value)
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            return max(30.0, min(60.0, stamp.timestamp() - datetime.now(timezone.utc).timestamp()))
        except Exception:
            return 30.0


def _throttle() -> None:
    global _LAST_REQUEST
    with _LOCK:
        wait = MIN_INTERVAL_S - (time.monotonic() - _LAST_REQUEST)
        if wait > 0:
            time.sleep(wait)
        _LAST_REQUEST = time.monotonic()


def markets_url(auth: str = AUTH_HEADER_FIRST) -> str:
    """Bulk pre-match soccer snapshot URL (one call = the whole board).

    Under header auth (the real contract) the key is NOT in the URL. The
    query form is built only for the 401 fallback.
    """
    query = {"sport_id": sport_id(), "event_type": EVENT_TYPE}
    if auth == AUTH_QUERY_FALLBACK:
        query["key"] = _api_key() or ""
    return BASE + "/kit/v1/markets?" + urllib.parse.urlencode(query)


def request_headers(auth: str = AUTH_HEADER_FIRST) -> dict[str, str]:
    """Headers for one snapshot request.

    Under header auth this dict carries the key, so it must never be
    logged, echoed into diagnostics, or persisted. ``_sanitize_headers``
    protects RESPONSE headers only and is no help here.
    """
    headers = {"User-Agent": UA, "Accept": "application/json"}
    key = _api_key()
    if auth == AUTH_HEADER_FIRST and key:
        headers[AUTH_HEADER] = key
    return headers


def _carries_credentials(url: str, headers: dict[str, str]) -> bool:
    """True iff this request authenticates by SOME mechanism.

    The original guard asserted ``"key=" in url``, which stopped being a
    test of authentication the moment the key moved into a header. The
    invariant it protected is unchanged: never issue an unauthenticated
    request.
    """
    if str(headers.get(AUTH_HEADER) or "").strip():
        return True
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    return any(str(value).strip() for value in query.get("key", []))


_ERROR_ENVELOPE_KEYS = ("error", "errors", "message", "detail", "error_message",
                        "errorMessage", "msg", "status_message")
# Phrases that mean "your credential was refused". This list matches PROSE
# from a vendor whose wording nobody here has seen, so it is deliberately
# short and deliberately fail-safe: an unmatched body (say
# {"status":"ERR","code":4001}) is recorded as an error envelope, no
# fallback fires, and no mechanism is claimed. That is the safe direction.
# DO NOT add more phrases before a real run has shown the vendor's actual
# wording - the scrubbed body is recorded precisely so the first run
# teaches it. Guessing phrasings here is the same mistake as inventing a
# parser for a payload nobody has seen.
_AUTH_FLAVOURED = re.compile(
    r"api[_ -]?key|apikey|unauthor|unauthenticat|forbidden|invalid\s+key|"
    r"\btoken\b|credential|\bauth\b|not\s+permitted|access\s+denied", re.I)


def _error_envelope_raw(payload: Any) -> str | None:
    """Unscrubbed error text from a 200 body, for CLASSIFICATION only.

    Never record this. Redaction can remove the very words the classifier
    reads - a short key redacted out of "invalid api key" leaves text that
    no longer blames the credential - so the order matters: classify the
    raw text, scrub what gets written down.
    """
    events, _key = _envelope(payload)
    if events is not None or not isinstance(payload, dict):
        return None
    for key in _ERROR_ENVELOPE_KEYS:
        value = payload.get(key)
        if isinstance(value, dict):
            value = value.get("message") or value.get("detail") or value.get("text")
        if isinstance(value, list) and value:
            value = value[0] if isinstance(value[0], str) else None
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def error_envelope_text(payload: Any) -> str | None:
    """Scrubbed error text when a 200 body is an error envelope, for the record.

    Cheap relays answer a rejected credential with HTTP 200 and a body like
    ``{"error": "invalid api key"}``. That parses, carries no event
    collection, and would otherwise be filed as an unreadable payload - a
    parser problem - when the real cause is authentication. Detecting it is
    what keeps the zero-row classification honest.
    """
    raw = _error_envelope_raw(payload)
    return str(_scrub_secret(raw))[:200] if raw else None


def looks_like_auth_error(text: str | None) -> bool:
    """True when an error envelope blames the credential, not the request."""
    return bool(text and _AUTH_FLAVOURED.search(text))


def error_envelope_blames_credential(payload: Any) -> bool:
    """Whether a 200 error body blames the credential. Reads the raw text."""
    return looks_like_auth_error(_error_envelope_raw(payload))


def _http_code_in(message: str) -> int | None:
    match = re.search(r"HTTP (\d{3})", message)
    return int(match.group(1)) if match else None


def _record_attempt(mechanism: str, status: int | None,
                    *, error_envelope: str | None = None) -> None:
    attempt: dict[str, Any] = {"auth": mechanism, "status": status}
    if error_envelope:
        # Already scrubbed by error_envelope_text; a vendor that echoes the
        # key back must not get it written into the ledger.
        attempt["error_envelope"] = error_envelope
    _AUTH_ATTEMPTS.append(attempt)


def _auth_memory_note(attempts: list[dict[str, Any]]) -> str | None:
    """Say so only when the header attempt was SKIPPED on remembered grounds.

    Learning the 401 during this capture is not the same event as acting on
    it later, and conflating them would make the field useless.
    """
    if _HEADER_AUTH_REJECTED and not any(
            a.get("auth") == AUTH_HEADER_FIRST for a in attempts):
        return "header form rejected earlier this run; went straight to the query form"
    return None


def _sanitize_headers(headers: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        items = headers.items()
    except Exception:
        return out
    for key, value in items:
        name = str(key)
        if "ratelimit" in name.lower() or name.lower() == "retry-after":
            out[name] = str(value)
    return out


def get_json(url: str, *, timeout: int = 30, auth: str = AUTH_HEADER_FIRST) -> tuple[int, Any, dict[str, str]]:
    """One GET as JSON; raises UpstreamBlocked on 429/auth walls/budget.

    ``auth="header"`` sends the key as ``x-portal-apikey`` (the real REST
    contract); ``auth="query"`` is the legacy ``key=`` form, used only as a
    401 fallback. Either way the request must carry credentials or it is
    refused before it leaves the process. The URL never appears in
    diagnostics, and request headers are never logged. One 429 retry with
    Retry-After-first backoff; a second 429 trips run-scoped cool-down.
    """
    global _429S, _COOLING_DOWN, _CALLS_THIS_RUN, _CALLS_THIS_PROCESS
    if _COOLING_DOWN:
        raise UpstreamBlocked("pinnapi: run cooling down after repeated HTTP 429 responses")
    if not _api_key():
        raise UpstreamBlocked(f"pinnapi: {KEY_ENV} not set; shadow capture skipped")
    headers = request_headers(auth)
    if not _carries_credentials(url, headers):
        # Defensive: never issue an unauthenticated snapshot request - by
        # header or by query parameter, the credential must be present.
        raise UpstreamBlocked("pinnapi: refusing unauthenticated request")
    for attempt in range(2):
        if _CALLS_THIS_RUN >= MAX_CALLS_PER_RUN:
            raise UpstreamBlocked(f"pinnapi: per-run call budget {MAX_CALLS_PER_RUN} reached; no further calls this run")
        _throttle()
        _CALLS_THIS_RUN += 1
        _CALLS_THIS_PROCESS += 1
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = int(getattr(response, "status", 200))
                body = response.read(8_000_000).decode("utf-8", "replace")
                try:
                    payload = json.loads(body) if body else None
                except json.JSONDecodeError:
                    payload = None
                return status, payload, _sanitize_headers(response.headers)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                _429S += 1
                if _429S >= 2 or attempt > 0:
                    _COOLING_DOWN = True
                    raise UpstreamBlocked("pinnapi: repeated HTTP 429; cooling down for the rest of this run") from exc
                wait = _retry_after_seconds(exc.headers.get("Retry-After") if exc.headers else None)
                time.sleep(wait)
                continue
            snippet = ""
            try:
                snippet = exc.read(200).decode("utf-8", "replace")
            except Exception:
                pass
            raise UpstreamBlocked(f"pinnapi: HTTP {exc.code} {exc.reason}; {snippet[:120]}") from exc
        except Exception as exc:
            raise UpstreamBlocked(f"pinnapi: {type(exc).__name__}: {exc}") from exc
    raise UpstreamBlocked("pinnapi: exhausted retries")


def fetch_markets(*, timeout: int = 30) -> tuple[int, Any, dict[str, str], str]:
    """One snapshot: header auth first, ``key=`` query retried only on 401.

    Returns ``(status, payload, rate_limit_headers, mechanism)`` and records
    every attempt as (mechanism, status) so the ledger states which form the
    vendor actually accepted instead of leaving the next operator to guess.

    Budget arithmetic, stated so nobody is surprised by it: a fallback
    attempt is a real call and counts against ``MAX_CALLS_PER_RUN``, so a
    capture where the header form is rejected fetches at most two boards,
    not four. Once rejected, the rejection is remembered for the rest of the
    run and later captures spend one call, not two.
    """
    global _AUTH_MECHANISM, _HEADER_AUTH_REJECTED
    order = ((AUTH_QUERY_FALLBACK,) if _HEADER_AUTH_REJECTED
             else (AUTH_HEADER_FIRST, AUTH_QUERY_FALLBACK))
    result: tuple[int, Any, dict[str, str], str] | None = None
    for mechanism in order:
        try:
            status, payload, rate_headers = get_json(
                markets_url(auth=mechanism), timeout=timeout, auth=mechanism)
        except UpstreamBlocked as exc:
            code = _http_code_in(str(exc))
            _record_attempt(mechanism, code)
            if code in AUTH_FALLBACK_STATUSES and mechanism == AUTH_HEADER_FIRST:
                _HEADER_AUTH_REJECTED = True
                continue  # credential rejected: try the legacy form once
            raise
        # A 200 can still be a rejected credential: some relays answer with
        # an error envelope and a success code. Treat that as a rejection
        # rather than recording it as "this mechanism worked".
        envelope_error = error_envelope_text(payload)
        rejected = error_envelope_blames_credential(payload)
        _record_attempt(mechanism, status,
                        error_envelope=envelope_error if envelope_error else None)
        result = (status, payload, rate_headers, mechanism)
        if (status in AUTH_FALLBACK_STATUSES or rejected) and mechanism == AUTH_HEADER_FIRST:
            _HEADER_AUTH_REJECTED = True
            continue
        _AUTH_MECHANISM = mechanism if status == 200 and not rejected else None
        return result
    if result is None:  # pragma: no cover - loop always returns or raises
        raise UpstreamBlocked("pinnapi: no snapshot attempt completed")
    return result


def _num(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _team_name(value: object) -> str | None:
    if isinstance(value, dict):
        value = value.get("name")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _normalize_market(name: object) -> str:
    raw = str(name or "").strip().lower()
    return _MARKET_ALIASES.get(raw, raw)


def _normalize_selection(market: str, selection: object) -> str:
    raw = str(selection or "").strip().lower()
    if market == "1x2":
        aliases = {"home": "home", "1": "home", "h": "home",
                   "draw": "draw", "x": "draw", "tie": "draw",
                   "away": "away", "2": "away", "a": "away"}
        return aliases.get(raw, raw)
    if market == "totals":
        aliases = {"over": "over", "o": "over", "under": "under", "u": "under"}
        return aliases.get(raw, raw)
    return raw


def _market_entries(markets: Any) -> tuple[list[dict[str, Any]], str | None]:
    """Flatten the markets container into a list of per-selection entries.

    The provider sends this block in EITHER of two shapes:

    * a LIST of entries, each naming its own market::

          [{"market": "moneyline", "selection": "home", "price": 2.10}, ...]

    * a DICT keyed by market name, whose values list the selections::

          {"moneyline": [{"selection": "home", "price": 2.10}, ...]}

    The dict form carries the market name in the KEY, not in the entry, so it
    has to be injected into each selection. Reading it as a list instead -
    which is what the adapter used to do - discarded every event that arrived
    this way, while still reporting schema_match=True because the team names
    parsed. That is the production signature: the source looks healthy and
    delivers nothing.

    Returns ``(entries, drop_reason)``. ``drop_reason`` is non-None when the
    container itself is unusable, so the caller counts it rather than
    dropping the event in silence.
    """
    if isinstance(markets, list):
        entries = [m for m in markets if isinstance(m, dict)]
        malformed = len(markets) - len(entries)
        return entries, (f"market_entry_not_an_object_x{malformed}"
                         if malformed else None)
    if isinstance(markets, dict):
        entries = []
        unusable = 0
        for name, value in markets.items():
            # A single selection may arrive unwrapped rather than in a list.
            selections = [value] if isinstance(value, dict) else value
            if not isinstance(selections, list):
                unusable += 1
                continue
            for selection in selections:
                if not isinstance(selection, dict):
                    unusable += 1
                    continue
                entry = dict(selection)
                # Never overwrite a market the entry already names for itself.
                if not entry.get("market") and not entry.get("name"):
                    entry["market"] = name
                entries.append(entry)
        return entries, (f"market_group_unreadable_x{unusable}"
                         if unusable else None)
    # Neither shape. Record what actually arrived so the next outage names
    # itself instead of looking like an empty slate.
    return [], f"markets_container_not_list_or_dict:{type(markets).__name__}"


def canonicalization_drop_reasons() -> dict[str, int]:
    """Named reasons for rows discarded during the last parse, with counts.

    Every ``continue`` on the parsing path increments one of these. A silent
    discard is indistinguishable from a provider with nothing to offer, which
    is precisely how this source went unnoticed while dropping everything.
    """
    return dict(_CANONICALIZATION_DROP_REASONS)


def _count_drop(reason: str) -> None:
    _CANONICALIZATION_DROP_REASONS[reason] = (
        _CANONICALIZATION_DROP_REASONS.get(reason, 0) + 1
    )


def _envelope(payload: Any) -> tuple[list[Any] | None, str | None]:
    """Locate the event list. Returns ``(events, key)``; ``(None, None)``
    when the payload carries no envelope this adapter recognizes.

    An envelope holding zero events and no envelope at all are different
    answers with opposite diagnoses - a board that was genuinely empty (or
    a wrong sport id) versus a payload shape we cannot read - so they are
    distinguished here rather than collapsed into one zero.
    """
    if isinstance(payload, dict):
        for key in ("events", "data", "matches"):
            if isinstance(payload.get(key), list):
                return payload[key], key
        return None, None
    if isinstance(payload, list):
        return payload, None
    return None, None


def parse_snapshot(payload: Any, *, day: str) -> tuple[list[dict[str, Any]], bool]:
    """Map a snapshot into price-ledger rows. Returns (rows, schema_match).

    schema_match is False when the payload does not look like the documented
    event/market shape - in that case NO rows are returned (fail-closed) and
    the caller retains a trimmed raw sample for operator review.
    """
    events, _key = _envelope(payload)
    if not isinstance(events, list):
        return [], False
    global _CANONICALIZATION_DROP_REASONS
    _CANONICALIZATION_DROP_REASONS = {}
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows: list[dict[str, Any]] = []
    matched_shape = False
    for event in events:
        if not isinstance(event, dict):
            continue
        home = _team_name(event.get("home") or event.get("team_home"))
        away = _team_name(event.get("away") or event.get("team_away"))
        if not home or not away:
            continue
        matched_shape = True
        kickoff = event.get("start_at") or event.get("kickoff") or event.get("starts_at")
        league = event.get("league") or event.get("tournament") or event.get("competition")
        if isinstance(league, dict):
            league = league.get("name")
        markets = event.get("markets") or event.get("odds") or []
        market_entries, container_problem = _market_entries(markets)
        if container_problem:
            _count_drop(container_problem)
        for market_entry in market_entries:
            raw_price = market_entry.get("price")
            if raw_price is None:
                raw_price = market_entry.get("odds")
            price = _num(raw_price)
            if price is None:
                # The price sits under a key this adapter does not read, or is
                # not a number. Either way it is a contract gap, not an absence
                # of odds, and it must be visible as one.
                _count_drop("price_unreadable")
                continue
            if price <= 1.0:
                # Decimal odds of 1.0 or less pay nothing; treat as a bad value
                # rather than a real quote, but still account for it.
                _count_drop("price_not_above_one")
                continue
            raw_market = market_entry.get("market") or market_entry.get("name")
            raw_selection = market_entry.get("selection") or market_entry.get("label")
            canonical, _failure = canonical_market_selection(
                raw_market, raw_selection, home=home, away=away,
                line=market_entry.get("line"),
            )
            if canonical is None:
                reason = _failure.reason if _failure is not None else "unmappable"
                _CANONICALIZATION_DROP_REASONS[reason] = (
                    _CANONICALIZATION_DROP_REASONS.get(reason, 0) + 1
                )
                continue
            rows.append({
                "source": SOURCE,
                "date": day,
                "kickoff": kickoff,
                "league": league,
                "home": home,
                "away": away,
                "event_id": event.get("id"),
                "market": canonical.market,
                "selection": canonical.selection,
                "raw_market": raw_market,
                "raw_selection": raw_selection,
                "line": canonical.line,
                "odds": price,
                "book": BOOK,
                "bookmaker": BOOK,
                "captured_at": captured_at,
            })
    return rows, matched_shape


def same_day_rows(rows: list[dict[str, Any]], day: str) -> list[dict[str, Any]]:
    """Corroboration freshness gate.

    pinnapi may corroborate ONLY same-day-fetched prices: a row qualifies
    iff its ``captured_at`` stamp falls on ``day``. Stale or missing means
    ABSTAIN - a future corroborator must call this gate and may not fall
    back to older prices.
    """
    return [row for row in rows if str(row.get("captured_at") or "").startswith(str(day))]


def _resolve_localdata(localdata: Path | None) -> Path:
    return localdata if localdata is not None else LOCALDATA


def _ledger_path(day: str, *, localdata: Path | None = None) -> Path:
    return _resolve_localdata(localdata) / f"{SOURCE}_shadow_{day}.json"


def _load_ledger_rows(day: str, *, localdata: Path | None = None) -> list[dict[str, Any]]:
    try:
        payload = json.loads(_ledger_path(day, localdata=localdata).read_text())
        rows = payload.get("rows")
        return list(rows) if isinstance(rows, list) else []
    except (OSError, ValueError, TypeError):
        return []


def dedupe_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    """Gap-aware dedupe key: source+date+home+away+market(+selection+line)."""

    def clean(value: object) -> str:
        return re.sub(r"[^a-z0-9.]+", "", str(value or "").lower())

    return (
        str(row.get("source") or SOURCE),
        str(row.get("date") or ""),
        clean(row.get("home")),
        clean(row.get("away")),
        f"{clean(row.get('market'))}:{clean(row.get('selection'))}:{clean(row.get('line'))}",
    )


def merge_with_committed(rows: list[dict[str, Any]], committed: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Existing committed rows win; only genuinely new rows are appended."""
    held = {dedupe_key(row) for row in committed}
    out = list(committed)
    for row in rows:
        if dedupe_key(row) not in held:
            held.add(dedupe_key(row))
            out.append(row)
    return out


def _scrub_secret(value: Any) -> Any:
    """Redact key material from retained upstream diagnostics."""
    secret = _api_key()
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]") if secret else value
    if isinstance(value, dict):
        return {str(k): _scrub_secret(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrub_secret(v) for v in value]
    return value


def _trim_event_sample(payload: Any) -> Any:
    """One trimmed, secret-scrubbed event retained for operator schema review."""
    events = None
    if isinstance(payload, dict):
        for key in ("events", "data", "matches"):
            if isinstance(payload.get(key), list):
                events = payload[key]
                break
    elif isinstance(payload, list):
        events = payload
    if isinstance(events, list) and events:
        sample = events[0]
        text = json.dumps(sample, sort_keys=True)
        return _scrub_secret(json.loads(text[:20000]) if len(text) > 20000 else sample)
    return _scrub_secret({"top_keys": [str(k) for k in list(payload.keys())[:12]]} if isinstance(payload, dict) else None)


def classify_zero_rows(payload: Any, rows: list[dict[str, Any]], schema_match: bool) -> str | None:
    """Name WHY a 200 produced nothing. ``None`` when it produced rows.

    Four zero-row answers with four different next actions:

    * ``error_envelope``       - a 200 whose body is an error, not a board.
      Usually the credential. NOT a parser question, though it parses like
      one, which is exactly why it is named separately.
    * ``unrecognized_shape``   - no envelope we can read. A parser question.
    * ``empty_board``          - a readable envelope holding zero fixtures.
      NOT a parser question: either the sport id is wrong or the board was
      genuinely empty at this hour. Zero events means nothing without the
      day's fixture count beside it.
    * ``events_without_teams`` - fixtures arrived but none exposed both
      team names; shape drift inside the event, not in the envelope.
    * ``no_usable_rows``       - fixtures parsed, every price discarded;
      the named drop reasons say which.
    """
    if rows:
        return None
    if error_envelope_text(payload):
        return "error_envelope"
    events, _key = _envelope(payload)
    if not isinstance(events, list):
        return "unrecognized_shape"
    if not events:
        return "empty_board"
    if not schema_match:
        return "events_without_teams"
    return "no_usable_rows"


_ZERO_ROW_DIAGNOSIS = {
    "error_envelope": (
        "the body is an error, not a board - a 200 status does not mean the request "
        "was accepted. Read the recorded error text: if it blames the credential, "
        "this is an auth answer wearing a success code, not a parser question"),
    "unrecognized_shape": (
        "no recognizable event envelope; this is a parser question - capture the "
        "recorded shape and run scripts/probe_pinnapi.py before changing any mapping"),
    "empty_board": (
        "a readable envelope holding zero fixtures; this is NOT a parser question - "
        "either the sport id is wrong or the board was empty at this hour. Compare "
        "against the day's fixture count before concluding anything"),
    "events_without_teams": (
        "fixtures returned but none exposed both team names; shape drift inside the "
        "event, not in the envelope"),
    "no_usable_rows": (
        "fixtures parsed but every price was discarded; see the named drop reasons"),
}


def _payload_shape(payload: Any) -> dict[str, Any]:
    """Describe what actually arrived - container types and key names only.

    Recorded whenever a 200 yields no usable rows. The point is to make the
    next decision from an observed payload instead of an imagined one: no
    parser is written for a shape nobody has seen.
    """
    shape: dict[str, Any] = {"json_type": type(payload).__name__}
    if isinstance(payload, dict):
        shape["top_keys"] = [str(key) for key in list(payload.keys())[:12]]
    events, envelope_key = _envelope(payload)
    shape["envelope_found"] = events is not None
    if envelope_key:
        shape["events_key"] = envelope_key
    shape["event_count"] = len(events) if isinstance(events, list) else 0
    if isinstance(events, list):
        # Fixture-count context: a bare zero is unreadable without it.
        dicts = [e for e in events if isinstance(e, dict)]
        shape["events_with_teams"] = sum(
            1 for e in dicts
            if _team_name(e.get("home") or e.get("team_home"))
            and _team_name(e.get("away") or e.get("team_away")))
        shape["events_with_markets"] = sum(
            1 for e in dicts if e.get("markets") or e.get("odds"))
    first = events[0] if isinstance(events, list) and events else None
    if isinstance(first, dict):
        shape["event_keys"] = [str(key) for key in list(first.keys())[:20]]
        markets = first.get("markets") or first.get("odds")
        shape["markets_type"] = type(markets).__name__
        entry: Any = None
        if isinstance(markets, dict):
            shape["market_group_keys"] = [str(k) for k in list(markets.keys())[:12]]
            entry = next(iter(markets.values()), None)
        elif isinstance(markets, list):
            entry = markets[0] if markets else None
        if isinstance(entry, list):
            entry = entry[0] if entry else None
        if isinstance(entry, dict):
            shape["market_entry_keys"] = [str(k) for k in list(entry.keys())[:20]]
    envelope_error = error_envelope_text(payload)
    if envelope_error:
        shape["error_text"] = envelope_error
        shape["error_blames_credential"] = error_envelope_blames_credential(payload)
    shape["drop_reasons"] = dict(_CANONICALIZATION_DROP_REASONS)
    return _scrub_secret(shape)


def _status_for_http(status: int | None) -> str:
    if status in {401, 403}:
        return "auth"
    if status in {402, 429, 430, 509}:
        return "quota"
    return "unavailable"


def capture_day(day: str, *, localdata: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Capture one dated Pinnacle pre-match snapshot. Cache-first, inert
    without ``PINNAPI_KEY`` (status ``not_run``), fail-closed on shape."""
    stats: dict[str, Any] = {
        "status": "not_run", "pa_raw": 0, "pa_matched": 0, "requests": 0,
        "cache_hits": 0, "http_statuses": [], "http_429": 0, "errors": [],
        "quota_hint": "none", "blocker": None, "budget": MAX_CALLS_PER_RUN,
        "rate_limit_headers": {}, "schema_match": None,
        "sample_event": None, "key_present": _api_key() is not None,
        "canonicalization_dropped": 0, "canonicalization_drop_reasons": {},
        # Request contract actually used, so the ledger answers "how did we
        # ask?" without anyone re-reading the adapter.
        "sport_id": sport_id(), "event_type": EVENT_TYPE,
        "auth_header_name": AUTH_HEADER, "auth_mechanism": None,
        "auth_attempts": [], "auth_memory": None,
        "response_shape": None, "zero_row_kind": None,
        "calls_this_run_so_far": 0,
    }
    reset_state()
    if not _api_key():
        stats["blocker"] = f"{KEY_ENV} not set; shadow capture skipped (inert)"
        return [], _set_diag(stats)
    committed = _load_ledger_rows(day, localdata=localdata)
    if committed:
        # Gap-aware: we hold committed rows for this date - never refetch.
        stats["status"] = "cache_only"
        stats["cache_hits"] = 1
        stats["pa_raw"] = len(committed)
        stats["pa_matched"] = len(committed)
        stats["schema_match"] = True
        return list(committed), _set_diag(stats)
    try:
        status, payload, rate_headers, mechanism = fetch_markets()
        stats["auth_attempts"] = auth_attempts()
        stats["requests"] = len(stats["auth_attempts"]) or 1
        stats["http_statuses"] = [a["status"] for a in stats["auth_attempts"]]
        stats["auth_mechanism"] = auth_mechanism()
        stats["auth_memory"] = _auth_memory_note(stats["auth_attempts"])
        stats["calls_this_run_so_far"] = calls_this_process()
        stats["rate_limit_headers"] = rate_headers
        if status != 200 or payload is None:
            stats["status"] = _status_for_http(status)
            stats["quota_hint"] = "auth_or_quota" if stats["status"] == "auth" else (
                "rate_limit_or_quota" if stats["status"] == "quota" else "none_observed")
            stats["blocker"] = f"pinnapi: HTTP {status} or non-JSON payload"
            return [], _set_diag(stats)
        envelope_error = error_envelope_text(payload)
        if envelope_error:
            # HTTP 200 carrying an error body. It parses, so it would
            # otherwise be filed as an unreadable payload - a parser
            # question - when the usual cause is the credential.
            blames_credential = error_envelope_blames_credential(payload)
            stats["status"] = "auth" if blames_credential else "unavailable"
            stats["quota_hint"] = "auth_or_quota" if blames_credential else "none_observed"
            stats["zero_row_kind"] = "error_envelope"
            stats["response_shape"] = _payload_shape(payload)
            stats["blocker"] = (
                f"pinnapi: HTTP 200 with an error body [{envelope_error}] - "
                f"{_ZERO_ROW_DIAGNOSIS['error_envelope']}")
            stats["errors"].append(f"http_200_error_envelope: {envelope_error}"[:180])
            return [], _set_diag(stats)
        rows, schema_match = parse_snapshot(payload, day=day)
        stats["schema_match"] = schema_match
        stats["canonicalization_drop_reasons"] = dict(_CANONICALIZATION_DROP_REASONS)
        stats["canonicalization_dropped"] = sum(_CANONICALIZATION_DROP_REASONS.values())
        stats["sample_event"] = _trim_event_sample(payload)
        if not schema_match:
            # Fail-closed: keep the raw sample, map nothing, stay retryable.
            # An unreadable envelope and a readable-but-empty board both land
            # here with zero rows; they are told apart by zero_row_kind
            # because their diagnoses are opposite (parser vs sport id).
            kind = classify_zero_rows(payload, rows, schema_match)
            stats["status"] = "unavailable"
            stats["quota_hint"] = "none_observed"
            stats["response_shape"] = _payload_shape(payload)
            stats["zero_row_kind"] = kind
            stats["blocker"] = (
                f"pinnapi: HTTP 200 for sport_id={sport_id()} event_type={EVENT_TYPE} "
                f"produced zero rows [{kind}] - {_ZERO_ROW_DIAGNOSIS[kind]}")
            return [], _set_diag(stats)
        stats["pa_raw"] = len({(row["home"], row["away"]) for row in rows})
        stats["pa_matched"] = len(rows)
        stats["status"] = "ok" if rows else "empty"
        if not rows:
            # A recognized shape that produced nothing. Record the observed
            # payload shape and stop: the next step is an operator decision
            # on an observed payload, not a parser invented for one that has
            # never been seen.
            kind = classify_zero_rows(payload, rows, schema_match)
            stats["response_shape"] = _payload_shape(payload)
            stats["zero_row_kind"] = kind
            stats["blocker"] = (
                f"pinnapi: HTTP 200 for sport_id={sport_id()} event_type={EVENT_TYPE} "
                f"produced zero usable rows [{kind}] - {_ZERO_ROW_DIAGNOSIS[kind]}; "
                "observed payload shape recorded - do not extend the parser without "
                "a captured sample")
        return rows, _set_diag(stats)
    except UpstreamBlocked as exc:
        message = str(exc)
        stats["http_429"] = _429S
        stats["auth_attempts"] = auth_attempts()
        stats["requests"] = len(stats["auth_attempts"])
        stats["http_statuses"] = [
            a["status"] for a in stats["auth_attempts"] if a["status"] is not None]
        stats["auth_mechanism"] = auth_mechanism()
        stats["auth_memory"] = _auth_memory_note(stats["auth_attempts"])
        stats["calls_this_run_so_far"] = calls_this_process()
        if "429" in message:
            stats["status"] = "cooldown" if _COOLING_DOWN else "quota"
            stats["quota_hint"] = "rate_limit_or_quota"
        elif "budget" in message:
            stats["status"] = "quota"
            stats["quota_hint"] = "budget_reached"
        elif "not set" in message:
            stats["status"] = "not_run"
        else:
            match = re.search(r"HTTP (\d{3})", message)
            stats["status"] = _status_for_http(int(match.group(1)) if match else None)
            stats["quota_hint"] = "auth_or_quota" if stats["status"] == "auth" else "none_observed"
        stats["blocker"] = message[:180]
        stats["errors"].append(message[:180])
        return [], _set_diag(stats)


def persist_shadow(day: str, rows: list[dict[str, Any]], stats: dict[str, Any], *, localdata: Path | None = None) -> Path:
    localdata = _resolve_localdata(localdata)
    localdata.mkdir(parents=True, exist_ok=True)
    path = localdata / f"{SOURCE}_shadow_{day}.json"
    payload = {
        "schema": 1,
        "source": SOURCE,
        "date": day,
        "role": (
            "price-shadow (Pinnacle named-book; never a vote; corroboration default-off; "
            "may corroborate only same-day-fetched prices - see same_day_rows)"
        ),
        "provenance": {
            "api": f"{BASE}/kit/v1/markets (sport_id={sport_id()}, event_type={EVENT_TYPE})",
            "auth": (
                f"{AUTH_HEADER} request header; the legacy key= query parameter is "
                "retried only on HTTP 401 (stats.auth_mechanism records which answered)"),
            "hunt": "docs/operator/SOURCE-HUNT-2026-10.md#57",
            "unofficial_feed": "Pinnacle public API closed 2025-07-23; pinnapi is an independent relay - expect death without notice",
            "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "stats": stats,
        "rows": rows,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    return path


def fetch_day(date: str) -> list[dict]:
    return capture_day(date)[0]
