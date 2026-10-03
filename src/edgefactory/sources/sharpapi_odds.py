"""SharpAPI named-book price source.

Endpoint contract (repaired 2026-10-03)
---------------------------------------
The adapter used to call ``/odds``. The published RapidAPI contract is::

    GET https://sharpapi1.p.rapidapi.com/api/v1/odds?sport=basketball_nba&limit=5

so ``/api/v1/odds`` is now the default endpoint. The query is built from
explicit configuration rather than assumption - in particular ``date`` is NOT
sent unless ``SHARPAPI_DATE_PARAM`` names a parameter the provider actually
documents. Sending an unsupported filter is how a healthy source starts
looking empty.

Configuration (all explicit; ``SHARPAPI_SPORT`` is required for capture)::

    SHARPAPI_ENDPOINT=/api/v1/odds
    SHARPAPI_SPORT=soccer
    SHARPAPI_LIMIT=...
    SHARPAPI_BOOK=...
    SHARPAPI_MARKET=...
    SHARPAPI_DATE_PARAM=...   # only when the provider confirms a date filter

Failure classification is deliberately granular: 401 is auth, 403 is
auth/plan, 429 is quota, and a VALID EMPTY result is never confused with an
unrecognized schema. The host stays pinned to the operator hunt receipt
(``sharpapi1.p.rapidapi.com``) and no credential is ever logged.
"""
from __future__ import annotations
import json, os, re, threading, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edgefactory.odds_normalization import canonical_market_selection

SOURCE = "sharpapi_odds"
BASE = "https://sharpapi1.p.rapidapi.com"
API_HOST = "sharpapi1.p.rapidapi.com"
DEFAULT_ENDPOINT = "/api/v1/odds"


def endpoint() -> str:
    """Current endpoint path, normalized to a leading slash."""
    value = (os.environ.get("SHARPAPI_ENDPOINT") or DEFAULT_ENDPOINT).strip() or DEFAULT_ENDPOINT
    return value if value.startswith("/") else "/" + value


def query_params(day: str | None = None) -> dict[str, str]:
    """The documented, configurable request contract.

    ``date`` is intentionally absent by default: the published example filters
    by ``sport`` and ``limit`` only. An operator who has confirmed a date
    filter in the playground sets ``SHARPAPI_DATE_PARAM`` to its real name.
    """
    params: dict[str, str] = {}
    for env_name, param in (
        ("SHARPAPI_SPORT", "sport"),
        ("SHARPAPI_LIMIT", "limit"),
        ("SHARPAPI_BOOK", "book"),
        ("SHARPAPI_MARKET", "market"),
    ):
        value = (os.environ.get(env_name) or "").strip()
        if value:
            params[param] = value
    date_param = (os.environ.get("SHARPAPI_DATE_PARAM") or "").strip()
    if date_param and day:
        params[date_param] = str(day)
    return params
KEY_ENV = "RAPIDAPI_KEY"
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_SHARPAPI_MIN_INTERVAL_S", "5"))
MAX_CALLS_PER_RUN = int(os.environ.get("EDGE_FACTORY_SHARPAPI_MAX_CALLS", "1"))
RETRYABLE_ZERO_ROW_STATUSES = {"auth", "quota", "unavailable", "blocked", "error", "cooldown"}
_lock = threading.Lock(); _last = 0.0; _calls = 0; _429 = 0; _cooling = False; _DIAG: dict[str, Any] = {}
_CANONICALIZATION_DROP_REASONS: dict[str, int] = {}

class UpstreamBlocked(RuntimeError): pass

def reset_state() -> None:
    global _last, _calls, _429, _cooling
    _last = 0.0; _calls = 0; _429 = 0; _cooling = False

def diagnostics() -> dict[str, Any]: return dict(_DIAG)
def _set_diag(value: dict[str, Any]) -> dict[str, Any]: _DIAG.update(value); return value
def _key() -> str | None:
    value = os.environ.get(KEY_ENV, "").strip(); return value or None

def odds_url(day: str | None = None) -> str:
    params = query_params(day)
    query = urllib.parse.urlencode(sorted(params.items()))
    return BASE + endpoint() + (f"?{query}" if query else "")

def _headers(headers: Any) -> dict[str, str]:
    return {str(k): str(v) for k, v in (headers.items() if hasattr(headers, "items") else [])
            if "ratelimit" in str(k).lower() or str(k).lower() == "retry-after"}

def _wait(value: str | None) -> float:
    try: return max(1.0, min(60.0, float(value or 5)))
    except ValueError: return 5.0

def get_json(url: str, *, timeout: int = 30) -> tuple[int, Any, dict[str, str]]:
    global _last, _calls, _429, _cooling
    if _cooling: raise UpstreamBlocked("sharpapi: run cooling down after repeated HTTP 429 responses")
    if not _key(): raise UpstreamBlocked(f"{KEY_ENV} not set; shadow capture skipped")
    for attempt in range(2):
        if _calls >= MAX_CALLS_PER_RUN: raise UpstreamBlocked("sharpapi: per-run call budget reached")
        with _lock:
            delay = MIN_INTERVAL_S - (time.monotonic() - _last)
            if delay > 0: time.sleep(delay)
            _last = time.monotonic(); _calls += 1
        req = urllib.request.Request(url, headers={"Accept":"application/json", "User-Agent":"EdgeFactory-cooperative-shadow/1.0 (+operator review)", "X-RapidAPI-Key": _key() or "", "X-RapidAPI-Host": API_HOST})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read(8_000_000).decode("utf-8", "replace")
                try: payload = json.loads(body) if body else None
                except json.JSONDecodeError: payload = None
                return int(getattr(response, "status", 200)), payload, _headers(response.headers)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                _429 += 1
                if _429 >= 2 or attempt: _cooling = True; raise UpstreamBlocked("sharpapi: repeated HTTP 429; cooling down") from exc
                time.sleep(_wait(exc.headers.get("Retry-After") if exc.headers else None)); continue
            raise UpstreamBlocked(f"sharpapi: HTTP {exc.code} {exc.reason}") from exc
        except Exception as exc: raise UpstreamBlocked(f"sharpapi: {type(exc).__name__}: {exc}") from exc
    raise UpstreamBlocked("sharpapi: exhausted retries")

def _scrub(value: str) -> str:
    """Never echo credential material into diagnostics or ledgers."""
    secret = _key()
    return value.replace(secret, "[REDACTED]") if secret else value


def _num(x: object) -> float | None:
    try: return float(x)
    except (TypeError, ValueError): return None

def parse_snapshot(payload: Any, *, day: str) -> tuple[list[dict[str, Any]], bool]:
    """Accept only explicit event/bookmaker/market rows; unknown shapes yield no rows."""
    events = payload if isinstance(payload, list) else next((payload.get(k) for k in ("events", "data", "matches", "odds") if isinstance(payload, dict) and isinstance(payload.get(k), list)), None)
    if not isinstance(events, list): return [], False
    # A recognized but EMPTY event list is a valid empty result, not a schema
    # failure: conflating the two turns a quiet slate into a false outage (and
    # a real contract break into a false "no games today").
    global _CANONICALIZATION_DROP_REASONS
    _CANONICALIZATION_DROP_REASONS = {}
    rows: list[dict[str, Any]] = []; shaped = not events; stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for event in events:
        if not isinstance(event, dict): continue
        home = event.get("home") or event.get("home_team"); away = event.get("away") or event.get("away_team")
        if isinstance(home, dict): home = home.get("name")
        if isinstance(away, dict): away = away.get("name")
        books = event.get("bookmakers") or event.get("bookies") or event.get("books")
        if not home or not away or not isinstance(books, list): continue
        shaped = True
        for book in books:
            if not isinstance(book, dict): continue
            bookmaker = str(book.get("name") or book.get("bookmaker") or book.get("title") or "").strip()
            markets = book.get("markets") or book.get("odds") or []
            if not bookmaker or not isinstance(markets, list): continue
            for market in markets:
                if not isinstance(market, dict): continue
                price = _num(market.get("price") or market.get("odds") or market.get("value"))
                if price is None or price <= 1: continue
                raw_market = str(market.get("market") or market.get("name") or "").strip()
                raw_selection = str(market.get("selection") or market.get("label") or "").strip()
                canonical, _failure = canonical_market_selection(
                    raw_market, raw_selection, home=home, away=away,
                    line=market.get("line"),
                )
                if canonical is None:
                    reason = failure.reason if failure is not None else "unmappable"
                    _CANONICALIZATION_DROP_REASONS[reason] = (
                        _CANONICALIZATION_DROP_REASONS.get(reason, 0) + 1
                    )
                    continue
                rows.append({"source": SOURCE, "date": day, "home": str(home).strip(), "away": str(away).strip(), "kickoff": event.get("kickoff") or event.get("start_at"), "market": canonical.market, "selection": canonical.selection, "line": canonical.line, "raw_market": raw_market, "raw_selection": raw_selection, "odds": price, "book": bookmaker, "bookmaker": bookmaker, "odds_kind": "bookmaker", "named_bookmaker": True, "captured_at": stamp})
    return rows, shaped

def _status(code: int | None) -> str:
    if code in (401, 403): return "auth"
    if code in (402, 429, 509): return "quota"
    return "unavailable"


def _reason(code: int | None) -> str:
    """Deterministic zero-row reason suffix for the health line."""
    if code == 401: return "http_401_auth"
    if code == 403: return "http_403_auth_plan"
    if code == 429: return "http_429_quota"
    if code in (402, 509): return f"http_{code}_quota"
    if code == 404: return "http_404_endpoint_contract"
    if code is None: return "transport_error"
    return f"http_{code}_unavailable"

def _path(day: str, localdata: Path | None = None) -> Path: return (localdata or LOCALDATA) / f"{SOURCE}_shadow_{day}.json"
def capture_day(day: str, *, localdata: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stats = {"status":"not_run","sa_raw":0,"sa_matched":0,"requests":0,"http_statuses":[],"http_429":0,"errors":[],"blocker":None,"schema_match":None,"sample_event":None,"budget":MAX_CALLS_PER_RUN,"reason":None,"endpoint":endpoint(),"query_params":sorted(query_params(day)),"canonicalization_dropped":0,"canonicalization_drop_reasons":{}}
    reset_state()
    sport = (os.environ.get("SHARPAPI_SPORT") or "").strip()
    if not sport:
        stats.update(
            status="not_run",
            reason="missing_sport_filter",
            blocker="SHARPAPI_SPORT not set; soccer sport filter is required; capture skipped",
        )
        return [], _set_diag(stats)
    if not _key(): stats["blocker"] = f"{KEY_ENV} not set; shadow capture skipped"; return [], _set_diag(stats)
    try:
        held = json.loads(_path(day, localdata).read_text()).get("rows", [])
        if held: stats.update(status="cache_only", cache_hits=1, sa_raw=len(held), sa_matched=len(held), schema_match=True); return held, _set_diag(stats)
    except (OSError, ValueError, TypeError): pass
    try:
        code, payload, headers = get_json(odds_url(day)); stats["requests"] = 1; stats["http_statuses"] = [code]; stats["rate_limit_headers"] = headers
        if code != 200 or payload is None: stats.update(status=_status(code), reason=_reason(code), blocker=f"sharpapi: HTTP {code} or non-JSON payload"); return [], _set_diag(stats)
        rows, shaped = parse_snapshot(payload, day=day); stats["schema_match"] = shaped
        stats["canonicalization_drop_reasons"] = dict(_CANONICALIZATION_DROP_REASONS)
        stats["canonicalization_dropped"] = sum(_CANONICALIZATION_DROP_REASONS.values())
        # A recognizable but empty event list is a VALID empty result; only an
        # unrecognizable payload is a contract failure.
        if not shaped: stats.update(status="unavailable", reason="schema_unrecognized", blocker="sharpapi: snapshot schema not recognized; raw sample retained"); stats["sample_event"] = _scrub(str(payload)[:200]); return [], _set_diag(stats)
        stats["sa_raw"] = len({(r["home"], r["away"]) for r in rows}); stats["sa_matched"] = len(rows); stats["status"] = "ok" if rows else "empty"
        if not rows: stats["reason"] = "provider_empty_slate"
        return rows, _set_diag(stats)
    except UpstreamBlocked as exc:
        msg = _scrub(str(exc)); stats["http_429"] = _429
        import re as _re
        found = _re.search(r"HTTP (\d{3})", msg)
        code = int(found.group(1)) if found else None
        stats["status"] = "cooldown" if _cooling else ("quota" if "budget" in msg or "429" in msg else _status(code))
        stats["reason"] = "run_cooldown" if _cooling else ("budget_reached" if "budget" in msg else _reason(code))
        stats["blocker"] = msg[:180]; stats["errors"] = [msg[:180]]; return [], _set_diag(stats)

def persist_shadow(day: str, rows: list[dict[str, Any]], stats: dict[str, Any], *, localdata: Path | None = None) -> Path:
    root = localdata or LOCALDATA; root.mkdir(parents=True, exist_ok=True); path = _path(day, root)
    payload = {"schema":1,"source":SOURCE,"date":day,"role":"named-book price source (never a vote; same-day freshness required)","provenance":{"api":BASE + endpoint(),"host":API_HOST,"hunt":"docs/operator/SOURCE-HUNT-2026-10.md#sharpapi"},"stats":stats,"rows":rows}
    tmp = path.with_suffix(path.suffix + ".tmp"); tmp.write_text(json.dumps(payload, indent=2, sort_keys=True)); tmp.replace(path); return path
