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
- UNVERIFIED: exact REST auth mechanism and response schema. The docs show
  ``key=`` query-parameter auth on the SSE endpoints; this adapter uses the
  same on REST and treats any non-200 or unrecognized shape as
  ``unavailable`` (fail-closed, stays retryable). scripts/probe_pinnapi.py
  is the acceptance tool that reconciles auth + schema before any promotion
  discussion; a trimmed raw sample is retained in the ledger stats so a
  parser adjustment needs no new crawl.

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
# Panel receipt 2026-10-02: soccer is sport_id=2 and the playground uses
# event_type=prematch. Keep the constant as a fail-safe until a future /sports
# introspection response is independently captured.
SPORT_ID = 2
EVENT_TYPE = "prematch"
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
    _LAST_REQUEST = 0.0
    _429S = 0
    _COOLING_DOWN = False
    _CALLS_THIS_RUN = 0


def _api_key() -> str | None:
    value = os.environ.get(KEY_ENV)
    return value.strip() if value and value.strip() else None


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


def markets_url() -> str:
    """Bulk pre-match soccer snapshot URL (one call = the whole board)."""
    return BASE + "/kit/v1/markets?" + urllib.parse.urlencode({
        "sport_id": SPORT_ID, "event_type": EVENT_TYPE, "key": _api_key() or ""
    })


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


def get_json(url: str, *, timeout: int = 30) -> tuple[int, Any, dict[str, str]]:
    """One GET as JSON; raises UpstreamBlocked on 429/auth walls/budget.

    The key travels as a ``key=`` query parameter (the auth mechanism shown
    in pinnapi's own SSE docs) - which is also why the URL never appears in
    diagnostics output. One 429 retry with Retry-After-first backoff; a
    second 429 trips run-scoped cool-down.
    """
    global _429S, _COOLING_DOWN, _CALLS_THIS_RUN
    if _COOLING_DOWN:
        raise UpstreamBlocked("pinnapi: run cooling down after repeated HTTP 429 responses")
    if not _api_key():
        raise UpstreamBlocked(f"pinnapi: {KEY_ENV} not set; shadow capture skipped")
    if "key=" not in url:
        # Defensive: never issue an unauthenticated snapshot request.
        raise UpstreamBlocked("pinnapi: refusing unauthenticated request")
    for attempt in range(2):
        if _CALLS_THIS_RUN >= MAX_CALLS_PER_RUN:
            raise UpstreamBlocked(f"pinnapi: per-run call budget {MAX_CALLS_PER_RUN} reached; no further calls this run")
        _throttle()
        _CALLS_THIS_RUN += 1
        request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
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


def parse_snapshot(payload: Any, *, day: str) -> tuple[list[dict[str, Any]], bool]:
    """Map a snapshot into price-ledger rows. Returns (rows, schema_match).

    schema_match is False when the payload does not look like the documented
    event/market shape - in that case NO rows are returned (fail-closed) and
    the caller retains a trimmed raw sample for operator review.
    """
    if isinstance(payload, dict):
        events = None
        for key in ("events", "data", "matches"):
            if isinstance(payload.get(key), list):
                events = payload[key]
                break
    elif isinstance(payload, list):
        events = payload
    else:
        return [], False
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
        if not isinstance(markets, list):
            continue
        for market_entry in markets:
            if not isinstance(market_entry, dict):
                continue
            price = _num(market_entry.get("price") or market_entry.get("odds"))
            if price is None or price <= 1.0:
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
        status, payload, rate_headers = get_json(markets_url())
        stats["requests"] += 1
        stats["http_statuses"].append(status)
        stats["rate_limit_headers"] = rate_headers
        if status != 200 or payload is None:
            stats["status"] = _status_for_http(status)
            stats["quota_hint"] = "auth_or_quota" if stats["status"] == "auth" else (
                "rate_limit_or_quota" if stats["status"] == "quota" else "none_observed")
            stats["blocker"] = f"pinnapi: HTTP {status} or non-JSON payload"
            return [], _set_diag(stats)
        rows, schema_match = parse_snapshot(payload, day=day)
        stats["schema_match"] = schema_match
        stats["canonicalization_drop_reasons"] = dict(_CANONICALIZATION_DROP_REASONS)
        stats["canonicalization_dropped"] = sum(_CANONICALIZATION_DROP_REASONS.values())
        stats["sample_event"] = _trim_event_sample(payload)
        if not schema_match:
            # Fail-closed: keep the raw sample, map nothing, stay retryable.
            stats["status"] = "unavailable"
            stats["quota_hint"] = "none_observed"
            stats["blocker"] = (
                "pinnapi: snapshot schema not recognized; raw sample retained for operator review "
                "(run scripts/probe_pinnapi.py to reconcile auth + schema)")
            return [], _set_diag(stats)
        stats["pa_raw"] = len({(row["home"], row["away"]) for row in rows})
        stats["pa_matched"] = len(rows)
        stats["status"] = "ok" if rows else "empty"
        return rows, _set_diag(stats)
    except UpstreamBlocked as exc:
        message = str(exc)
        stats["http_429"] = _429S
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
            "api": f"{BASE}/kit/v1/markets (sport_id={SPORT_ID}, event_type={EVENT_TYPE})",
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
