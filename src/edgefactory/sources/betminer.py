"""BetMiner adapter - prediction voice donor, conditional price donor.

Endpoint contract (repaired 2026-10-03)
---------------------------------------
The adapter used to call ``GET /matches/{date}``. That path is no longer part
of the published RapidAPI contract; the listing exposes::

    GET /value-bets/{dateFrom}/{dateTo}
    GET /accumulators/{dateFrom}/{dateTo}
    GET /acca-builder
    GET /edge-analysis/{date}

The documented same-day request is ``/value-bets/{date}/{date}`` (the
provider's date-range contract). The legacy ``/matches/{date}`` response
shape is still parsed, because the repository holds a captured receipt for it
(``tests/fixtures/betminer_matches_2026-10-03.json``) and a cached ledger
written under the old contract must keep parsing; it is never *requested* any
more.

HTTP 404 is classified as an **endpoint-contract failure**
(``reason=http_404_endpoint_contract``) rather than a generic outage, so the
next contract drift is visible in the health line instead of silently looking
like an empty slate.

Price role
----------
BetMiner is a *conditional* price donor and is never execution-eligible: a
value-bet number only becomes a quote when the response identifies its
provenance. Without a bookmaker name it is labelled ``provider_average`` and
is evidence only - it must never be printed as a named-book execution price.

Resilience contract (mirrors bzzoiro_odds.py / betexplorer_odds.py):
cache-first per date; single-flight throttle; one retry on 429 with a
Retry-After-first 30-60s backoff; a second 429 trips run-scoped cool-down;
401/403 classify as ``auth``; 402/429/430/509 classify as ``quota``; 404 and
5xx/network classify as ``unavailable`` (fail-closed: an unexpected shape is
NEVER interpreted as an empty slate). Zero-row days whose status is
auth/quota/unavailable/blocked/cooldown stay RETRYABLE.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from edgefactory.odds_normalization import canonical_market_selection

SOURCE = "betminer"
BASE = "https://betminer.p.rapidapi.com"
#: Current published contract.
ENDPOINT_VALUE_BETS = "/value-bets"
#: Obsolete contract; parsed for cached ledgers, never requested.
ENDPOINT_LEGACY_MATCHES = "/matches"
API_HOST = "betminer.p.rapidapi.com"
KEY_ENV = "RAPIDAPI_KEY"
UA = "EdgeFactory-cooperative-shadow/1.0 (+operator review)"
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_BETMINER_MIN_INTERVAL_S", "2.0"))
MAX_CALLS_PER_RUN = int(os.environ.get("EDGE_FACTORY_BETMINER_MAX_CALLS", "4"))
FREE_TIER_DAILY_CALL_CAP = 5
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))

_LOCK = threading.Lock()
_LAST_REQUEST = 0.0
_429S = 0
_COOLING_DOWN = False
_CALLS_THIS_RUN = 0
_DIAG: dict[str, Any] = {}

# Zero-row days with these statuses stay RETRYABLE (never terminal "empty").
RETRYABLE_ZERO_ROW_STATUSES = {"auth", "quota", "unavailable", "blocked", "error", "cooldown"}

# predictions.result (docs) -> our vote-schema selection vocabulary.
_RESULT_SELECTION = {
    "home_win": "home",
    "away_win": "away",
    "draw": "draw",
    "home_or_draw": "1x",
    "away_or_draw": "x2",
    "home_or_away": "12",
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


def value_bets_url(day: str) -> str:
    """The current contract: one same-day range call returns the board."""
    return f"{BASE}{ENDPOINT_VALUE_BETS}/{day}/{day}"


def matches_url(day: str) -> str:
    """Legacy ``/matches/{date}`` path.

    Retained only so cached ledgers and the captured legacy receipt stay
    explicable. ``capture_day`` never requests it.
    """
    return f"{BASE}{ENDPOINT_LEGACY_MATCHES}/{day}"


def capture_url(day: str) -> str:
    """The endpoint ``capture_day`` actually calls (configurable, fail-safe).

    The documented default is a date range. An explicit endpoint override is
    treated as a path prefix and remains one call; it is never an implicit
    ladder.
    """
    configured = os.environ.get("BETMINER_ENDPOINT")
    if not configured or not configured.strip():
        return value_bets_url(day)
    endpoint = configured.strip()
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    return f"{BASE}{endpoint}/{day}"


def _sanitize_headers(headers: Any) -> dict[str, str]:
    """Keep only rate-limit signals; never echo auth material."""
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
    """One RapidAPI GET as JSON. Raises UpstreamBlocked on 429/auth walls.

    Never raises for HTTP error codes otherwise - the status code is returned
    and the caller classifies. One 429 retry with Retry-After-first backoff;
    a second 429 (or a retry on a cool-down) trips run-scoped cool-down.
    """
    global _429S, _COOLING_DOWN, _CALLS_THIS_RUN
    if _COOLING_DOWN:
        raise UpstreamBlocked("betminer: run cooling down after repeated HTTP 429 responses")
    key = _api_key()
    if not key:
        raise UpstreamBlocked(f"betminer: {KEY_ENV} not set; shadow capture skipped")
    for attempt in range(2):
        if _CALLS_THIS_RUN >= MAX_CALLS_PER_RUN:
            raise UpstreamBlocked(
                f"betminer: per-run call budget {MAX_CALLS_PER_RUN} reached; no further calls this run")
        _throttle()
        _CALLS_THIS_RUN += 1
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": UA,
                "Accept": "application/json",
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": API_HOST,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = int(getattr(response, "status", 200))
                body = response.read(4_000_000).decode("utf-8", "replace")
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
                    raise UpstreamBlocked("betminer: repeated HTTP 429; cooling down for the rest of this run") from exc
                wait = _retry_after_seconds(exc.headers.get("Retry-After") if exc.headers else None)
                time.sleep(wait)
                continue
            snippet = ""
            try:
                snippet = exc.read(200).decode("utf-8", "replace")
            except Exception:
                pass
            raise UpstreamBlocked(f"betminer: HTTP {exc.code} {exc.reason}; {snippet[:120]}") from exc
        except Exception as exc:
            raise UpstreamBlocked(f"betminer: {type(exc).__name__}: {exc}") from exc
    raise UpstreamBlocked("betminer: exhausted retries")


def _num(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _result_probability(probabilities: dict[str, Any], selection: str) -> float | None:
    if selection == "home":
        return _num(probabilities.get("home_win"))
    if selection == "away":
        return _num(probabilities.get("away_win"))
    if selection == "draw":
        return _num(probabilities.get("draw"))
    if selection == "1x":
        home, draw = _num(probabilities.get("home_win")), _num(probabilities.get("draw"))
        return home + draw if home is not None and draw is not None else None
    if selection == "x2":
        away, draw = _num(probabilities.get("away_win")), _num(probabilities.get("draw"))
        return away + draw if away is not None and draw is not None else None
    if selection == "12":
        home, away = _num(probabilities.get("home_win")), _num(probabilities.get("away_win"))
        return home + away if home is not None and away is not None else None
    return None


def parse_match(match: dict[str, Any], *, day: str, captured_at: str) -> dict[str, Any] | None:
    """Map one docs-schema match object to a vote-schema shadow row."""
    home = (match.get("home_team") or {}).get("name")
    away = (match.get("away_team") or {}).get("name")
    competition = match.get("competition") or {}
    probabilities = match.get("probabilities") or {}
    predictions = match.get("predictions") or {}
    if not home or not away:
        return None
    result_key = str(predictions.get("result") or "").strip().lower()
    selection = _RESULT_SELECTION.get(result_key)
    row: dict[str, Any] = {
        "source": SOURCE,
        "date": day,
        "kickoff": match.get("kickoff"),
        "league": competition.get("name"),
        "country": competition.get("country"),
        "league_slug": competition.get("slug"),
        "home": home,
        "away": away,
        "match_id": match.get("match_id"),
        "fixture_slug": match.get("fixture_slug"),
        "match_status": match.get("status"),
        "predicted_score": predictions.get("correct_score"),
        "htft": predictions.get("htft"),
        "1x2_selection": selection,
        "1x2_probability": _result_probability(probabilities, selection) if selection else None,
        "btts_selection": None,
        "btts_probability": _num(probabilities.get("btts")),
        "ou_25_selection": None,
        "ou_25_probability": _num(probabilities.get("over_25")),
        # Raw subobjects retained as provenance. The odds object has NO
        # bookmaker identity: provenance only, never price evidence.
        "probabilities_raw": dict(probabilities),
        "odds_raw": dict(match.get("odds") or {}),
        "captured_at": captured_at,
    }
    if "btts" in predictions and predictions.get("btts") is not None:
        row["btts_selection"] = "yes" if predictions.get("btts") else "no"
    if "over_25" in predictions and predictions.get("over_25") is not None:
        row["ou_25_selection"] = "over" if predictions.get("over_25") else "under"
    return row


def parse_matches(payload: Any, *, day: str) -> list[dict[str, Any]]:
    """Parse the documented ``{success, data, meta}`` wrapper into rows."""
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows: list[dict[str, Any]] = []
    for match in data:
        if not isinstance(match, dict):
            continue
        parsed = parse_match(match, day=day, captured_at=captured_at)
        if parsed is not None:
            rows.append(parsed)
    return rows


# --- current contract: /value-bets/{date} ---------------------------------
#
# Field names below are ALIASES observed across the provider's own
# documentation and playground, not invented schema: the parser accepts a
# value only when it can also say where the value came from. Anything it
# cannot label is dropped rather than guessed.

_VALUE_BET_LIST_KEYS = ("value_bets", "valueBets", "data", "bets", "results", "value-bets")
_HOME_KEYS = ("home", "home_team", "homeTeam", "home_name")
_AWAY_KEYS = ("away", "away_team", "awayTeam", "away_name")
_ODDS_KEYS = ("odds", "price", "bookmaker_odds", "bookmakerOdds", "best_odds", "bestOdds", "decimal_odds")
_FAIR_ODDS_KEYS = ("fair_odds", "fairOdds", "true_odds", "trueOdds", "model_odds")
_BOOKMAKER_KEYS = ("bookmaker", "bookie", "book", "bookmaker_name", "bookmakerName")
_SELECTION_KEYS = ("selection", "bet", "pick", "tip", "outcome", "prediction")
_MARKET_KEYS = ("market", "market_name", "bet_type", "betType")
_PROBABILITY_KEYS = ("probability", "prob", "model_probability", "modelProbability", "confidence")
_KICKOFF_KEYS = ("kickoff", "kick_off", "start_time", "startTime", "date_time", "commence_time")
_PUBLISHED_KEYS = ("published_at", "publishedAt", "updated_at", "updatedAt", "last_update_at")

_VALUE_BET_SELECTIONS = {
    "1": "home", "home": "home", "home_win": "home", "h": "home",
    "x": "draw", "draw": "draw", "d": "draw",
    "2": "away", "away": "away", "away_win": "away", "a": "away",
    "1x": "1x", "x2": "x2", "12": "12",
}


def _first(item: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return item[key]
    return None


def _team_name(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("name") or value.get("team") or value.get("title")
    text = str(value or "").strip()
    return text or None


def value_bet_rows(payload: Any) -> list[dict[str, Any]] | None:
    """Locate the value-bet list in the response wrapper, or ``None``."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return None
    for key in _VALUE_BET_LIST_KEYS:
        candidate = payload.get(key)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
    return None


def parse_value_bet(item: dict[str, Any], *, day: str, captured_at: str) -> dict[str, Any] | None:
    """Normalize one value-bet object. Returns ``None`` when unlabelable."""
    home = _team_name(_first(item, _HOME_KEYS))
    away = _team_name(_first(item, _AWAY_KEYS))
    if not home or not away:
        # Some payloads carry a single "match"/"fixture" string instead.
        fixture = str(_first(item, ("match", "fixture", "event", "game")) or "")
        for separator in (" vs ", " v ", " - "):
            if separator in fixture:
                home, _, away = fixture.partition(separator)
                home, away = home.strip() or None, away.strip() or None
                break
    if not home or not away:
        return None

    selection_raw = _first(item, _SELECTION_KEYS)
    market_raw = str(_first(item, _MARKET_KEYS) or "").strip() or "1x2"
    canonical, _failure = canonical_market_selection(
        market_raw, selection_raw, home=home, away=away,
        line=_first(item, ("line", "total", "points")),
    )
    if canonical is None:
        return None
    market = canonical.market
    selection = canonical.selection

    bookmaker = _first(item, _BOOKMAKER_KEYS)
    bookmaker = str(bookmaker).strip() if bookmaker not in (None, "") else None
    odds = _num(_first(item, _ODDS_KEYS))
    fair_odds = _num(_first(item, _FAIR_ODDS_KEYS))
    if odds is not None and odds <= 1.0:
        odds = None
    if fair_odds is not None and fair_odds <= 1.0:
        fair_odds = None

    # Provenance decides the label, never convenience. A number with no book
    # name is a provider aggregate; a model number is fair, not executable.
    if odds is not None and bookmaker:
        odds_kind: str | None = "bookmaker"
    elif odds is not None:
        odds_kind = "provider_average"
    elif fair_odds is not None:
        odds, odds_kind = fair_odds, "fair"
    else:
        odds, odds_kind = None, None

    probability = _num(_first(item, _PROBABILITY_KEYS))
    if probability is not None and probability > 1.5:
        probability = probability / 100.0

    return {
        "source": SOURCE,
        "date": day,
        "home": home,
        "away": away,
        "kickoff": _first(item, _KICKOFF_KEYS),
        "league": _team_name(_first(item, ("league", "competition", "league_name"))),
        "market": market,
        "selection": selection,
        "raw_market": market_raw,
        "raw_selection": selection_raw,
        "probability": probability,
        "odds": odds,
        "odds_kind": odds_kind,
        "fair_odds": fair_odds,
        "bookmaker": bookmaker,
        "named_bookmaker": bool(bookmaker),
        "value_pct": _num(_first(item, ("value", "value_pct", "edge", "edge_pct"))),
        "published_at": _first(item, _PUBLISHED_KEYS),
        "captured_at": captured_at,
        "schema_shape": "value_bets",
    }


def parse_value_bets(payload: Any, *, day: str) -> tuple[list[dict[str, Any]], bool]:
    """Parse a ``/value-bets/{date}`` payload.

    Returns ``(rows, shaped)``. ``shaped`` separates a VALID EMPTY day (the
    provider returned a recognizable but empty list) from an UNRECOGNIZED
    payload - conflating those is how a contract break turns into a silent
    "no bets today".
    """
    items = value_bet_rows(payload)
    if items is None:
        return [], False
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows: list[dict[str, Any]] = []
    for item in items:
        parsed = parse_value_bet(item, day=day, captured_at=captured_at)
        if parsed is not None:
            rows.append(parsed)
    return rows, True


def parse_payload(payload: Any, *, day: str) -> tuple[list[dict[str, Any]], str | None]:
    """Dispatch across the supported shapes. Returns ``(rows, shape)``.

    ``shape`` is ``None`` when nothing recognizable was found, which the
    caller must treat as a contract failure, not an empty slate.
    """
    if isinstance(payload, dict) and isinstance(payload.get("data"), list) and any(
        isinstance(item, dict) and ("home_team" in item or "probabilities" in item)
        for item in payload["data"]
    ):
        legacy = parse_matches(payload, day=day)
        if legacy:
            return legacy, "legacy_matches"
    rows, shaped = parse_value_bets(payload, day=day)
    if shaped:
        return rows, "value_bets"
    legacy = parse_matches(payload, day=day)
    if legacy:
        return legacy, "legacy_matches"
    return [], None


def _scrub(value: Any) -> Any:
    """Redact the API key from anything retained for diagnostics."""
    secret = _api_key()
    if isinstance(value, str):
        return value.replace(secret, "[REDACTED]") if secret else value
    if isinstance(value, dict):
        return {str(k): _scrub(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrub(v) for v in value[:3]]
    return value


def schema_sample(payload: Any) -> Any:
    """A small, scrubbed sample of the response for contract diagnostics."""
    if isinstance(payload, dict):
        items = value_bet_rows(payload)
        if items:
            return _scrub({k: items[0][k] for k in list(items[0])[:12]})
        return _scrub({"top_keys": list(payload)[:12]})
    if isinstance(payload, list) and payload:
        first = payload[0]
        return _scrub({k: first[k] for k in list(first)[:12]} if isinstance(first, dict) else first)
    return None


def _resolve_localdata(localdata: Path | None) -> Path:
    return localdata if localdata is not None else LOCALDATA


def _ledger_path(day: str, *, localdata: Path | None = None) -> Path:
    return _resolve_localdata(localdata) / f"{SOURCE}_shadow_{day}.json"


def _probe_receipt_path(day: str, *, localdata: Path | None = None) -> Path:
    return _resolve_localdata(localdata) / f"{SOURCE}_probe_{day}.json"


def _load_probe_receipt(day: str, *, localdata: Path | None = None) -> dict[str, Any] | None:
    try:
        payload = json.loads(_probe_receipt_path(day, localdata=localdata).read_text())
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError, TypeError):
        return None


def _persist_probe_receipt(
    day: str,
    *,
    endpoint: str,
    http_status: int | None,
    reason: str | None,
    schema_sample: Any = None,
    localdata: Path | None = None,
) -> Path:
    """Persist one scrubbed endpoint-contract observation for this day."""
    root = _resolve_localdata(localdata)
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": 1,
        "source": SOURCE,
        "date": str(day)[:10],
        "endpoint": endpoint,
        "http_status": http_status,
        "reason": reason,
        "schema_sample": _scrub(schema_sample),
        "probed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    path = _probe_receipt_path(day, localdata=localdata)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str))
    tmp.replace(path)
    return path


def _load_ledger_rows(day: str, *, localdata: Path | None = None) -> list[dict[str, Any]]:
    try:
        payload = json.loads(_ledger_path(day, localdata=localdata).read_text())
        rows = payload.get("rows")
        return list(rows) if isinstance(rows, list) else []
    except (OSError, ValueError, TypeError):
        return []


def dedupe_key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    """Gap-aware dedupe key: source+date+home+away+market."""

    def clean(value: object) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())

    market = row.get("market") or "1x2"
    return (
        str(row.get("source") or SOURCE),
        str(row.get("date") or ""),
        clean(row.get("home")),
        clean(row.get("away")),
        clean(market),
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


def settlement_coverage(rows: list[dict[str, Any]], settled_scores: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare captured fixtures with existing warehouse score facts.

    Settlement is owned by the existing warehouse/backfill path - this donor
    fetches no results itself. A mismatch is an operator warning only.
    """

    def key(row: dict[str, Any]) -> tuple[str, str, str]:
        def clean(value: object) -> str:
            return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())
        return str(row.get("date") or ""), clean(row.get("home")), clean(row.get("away"))

    settled_keys = {
        key(row) for row in settled_scores
        if row.get("hs") is not None or row.get("home_score") is not None
    }
    captured_keys = {key(row) for row in rows}
    matched = len(captured_keys & settled_keys)
    return {
        "captured": len(captured_keys),
        "settled": matched,
        "unmatched": max(0, len(captured_keys) - matched),
        "mismatch": bool(captured_keys and matched != len(captured_keys)),
        "settlement_source": "existing warehouse-score backfill",
    }


def capture_day(day: str, *, localdata: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Capture one dated Betminer slate. Cache-first, budget-capped, inert
    without ``RAPIDAPI_KEY`` (status ``not_run`` with a blocker)."""
    stats: dict[str, Any] = {
        "status": "not_run", "bm_raw": 0, "bm_scored": 0, "requests": 0,
        "cache_hits": 0, "http_statuses": [], "http_429": 0, "errors": [],
        "quota_hint": "none", "blocker": None, "budget": MAX_CALLS_PER_RUN,
        "rate_limit_headers": {}, "key_present": _api_key() is not None,
        "reason": None, "schema_shape": None, "schema_match": None,
        "schema_sample": None, "bm_priced": 0, "canonicalization_dropped": 0,
        "endpoint": capture_url("{date}"), "probe_receipt": False,
        "probe_receipt_path": None, "daily_free_tier_cap": FREE_TIER_DAILY_CALL_CAP,
        "calls_consumed": 0, "calls_remaining": FREE_TIER_DAILY_CALL_CAP,
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
        stats["bm_raw"] = len(committed)
        stats["bm_scored"] = len(committed)
        return list(committed), _set_diag(stats)
    receipt = _load_probe_receipt(day, localdata=localdata)
    if receipt is not None:
        # A contract failure already consumed today's discovery observation.
        # Never re-run an endpoint ladder on a free-tier day; the operator can
        # inspect the scrubbed receipt or explicitly remove it after confirming
        # a new contract.
        stats.update(
            status="unavailable",
            reason=str(receipt.get("reason") or "probe_receipt"),
            endpoint=str(receipt.get("endpoint") or stats["endpoint"]),
            probe_receipt=True,
            probe_receipt_path=str(_probe_receipt_path(day, localdata=localdata)),
            http_statuses=([receipt.get("http_status")]
                           if receipt.get("http_status") is not None else []),
            schema_sample=receipt.get("schema_sample"),
            blocker="betminer: persisted endpoint probe receipt; no re-probe today",
        )
        return [], _set_diag(stats)
    try:
        status, payload, rate_headers = get_json(capture_url(day))
        stats["requests"] += 1
        stats["calls_consumed"] = stats["requests"]
        stats["calls_remaining"] = max(0, FREE_TIER_DAILY_CALL_CAP - stats["calls_consumed"])
        stats["http_statuses"].append(status)
        stats["rate_limit_headers"] = rate_headers
        if status == 200 and payload is not None:
            if isinstance(payload, dict) and payload.get("success") is False:
                stats["status"] = "unavailable"
                stats["reason"] = "provider_error"
                stats["blocker"] = f"betminer: success=false payload: {str(payload.get('error'))[:160]}"
                stats["schema_sample"] = schema_sample(payload)
                return [], _set_diag(stats)
            rows, shape = parse_payload(payload, day=day)
            stats["schema_shape"] = shape
            stats["schema_match"] = shape is not None
            stats["schema_sample"] = schema_sample(payload)
            stats["quota_hint"] = _quota_hint_from_headers(rate_headers)
            source_items = value_bet_rows(payload)
            if isinstance(source_items, list):
                stats["canonicalization_dropped"] = max(0, len(source_items) - len(rows))
            if shape is None:
                # Recognizable-but-empty and unrecognizable are NOT the same
                # thing; only the former may be reported as an empty slate.
                stats["status"] = "unavailable"
                stats["reason"] = "schema_unrecognized"
                stats["blocker"] = "betminer: response schema not recognized; scrubbed sample retained"
                receipt = _persist_probe_receipt(
                    day, endpoint=capture_url(day), http_status=status,
                    reason=stats["reason"], schema_sample=stats["schema_sample"],
                    localdata=localdata,
                )
                stats["probe_receipt"] = True
                stats["probe_receipt_path"] = str(receipt)
                return [], _set_diag(stats)
            stats["bm_raw"] = len(rows)
            stats["bm_scored"] = len(rows)
            stats["bm_priced"] = sum(1 for row in rows if row.get("odds"))
            stats["status"] = "ok" if rows else "empty"
            if not rows:
                stats["reason"] = "provider_empty_slate"
            return rows, _set_diag(stats)
        stats["status"] = _status_for_http(status)
        stats["reason"] = _reason_for_http(status)
        stats["quota_hint"] = _quota_hint_for_status(stats["status"])
        stats["blocker"] = f"betminer: HTTP {status} or non-JSON payload"
        if status == 404:
            receipt = _persist_probe_receipt(
                day, endpoint=capture_url(day), http_status=status,
                reason=stats["reason"], schema_sample=schema_sample(payload),
                localdata=localdata,
            )
            stats["probe_receipt"] = True
            stats["probe_receipt_path"] = str(receipt)
        return [], _set_diag(stats)
    except UpstreamBlocked as exc:
        message = str(exc)
        stats["calls_consumed"] = int(_CALLS_THIS_RUN)
        stats["calls_remaining"] = max(0, FREE_TIER_DAILY_CALL_CAP - stats["calls_consumed"])
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
            code = _http_code_in(message)
            stats["status"] = _status_for_http(code)
            stats["reason"] = _reason_for_http(code)
            stats["quota_hint"] = _quota_hint_for_status(stats["status"])
        stats["blocker"] = message[:180]
        stats["errors"].append(message[:180])
        code = _http_code_in(message)
        if code is not None:
            stats["http_statuses"] = [code]
            stats["requests"] = max(int(stats.get("requests") or 0), int(_CALLS_THIS_RUN))
        if code == 404:
            receipt = _persist_probe_receipt(
                day, endpoint=capture_url(day), http_status=code,
                reason="http_404_endpoint_contract", schema_sample=None,
                localdata=localdata,
            )
            stats["probe_receipt"] = True
            stats["probe_receipt_path"] = str(receipt)
        return [], _set_diag(stats)


def _http_code_in(message: str) -> int | None:
    match = re.search(r"HTTP (\d{3})", message)
    return int(match.group(1)) if match else None


def _status_for_http(status: int | None) -> str:
    if status in {401, 403}:
        return "auth"
    if status in {402, 429, 430, 509}:
        return "quota"
    return "unavailable"


def _reason_for_http(status: int | None) -> str:
    """Deterministic zero-row reason suffix for the health line.

    A 404 on a RapidAPI path is almost never an outage: it means the path we
    are asking for is not the path the provider publishes. Naming that
    explicitly is the difference between "the provider is down" and "our
    endpoint contract is stale" - the exact failure this repair addresses.
    """
    if status == 404:
        return "http_404_endpoint_contract"
    if status in {401, 403}:
        return f"http_{status}_auth"
    if status in {402, 429, 430, 509}:
        return f"http_{status}_quota"
    if status is None:
        return "transport_error"
    return f"http_{status}_unavailable"


def _quota_hint_for_status(status: str) -> str:
    if status == "auth":
        return "auth_or_quota"
    if status == "quota":
        return "rate_limit_or_quota"
    return "none_observed"


def _quota_hint_from_headers(headers: dict[str, str]) -> str:
    remaining = None
    for name, value in headers.items():
        if "remaining" in name.lower():
            try:
                remaining = int(value)
            except ValueError:
                continue
            if remaining <= 1:
                return "nearly_exhausted"
    return "none_observed"


def persist_shadow(day: str, rows: list[dict[str, Any]], stats: dict[str, Any], *, localdata: Path | None = None) -> Path:
    localdata = _resolve_localdata(localdata)
    localdata.mkdir(parents=True, exist_ok=True)
    path = localdata / f"{SOURCE}_shadow_{day}.json"
    payload = {
        "schema": 1,
        "source": SOURCE,
        "date": day,
        "role": (
            "prediction vote donor; conditional provider-price donor - a "
            "value-bet number is a price only when the response identifies "
            "its provenance, and it is never execution-eligible"
        ),
        "provenance": {
            "api": f"RapidAPI {API_HOST} {ENDPOINT_VALUE_BETS}/{{from}}/{{to}}",
            "docs": "https://betminer.co.uk/documentation/",
            "hunt": "docs/operator/SOURCE-HUNT-2026-10.md#51",
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
