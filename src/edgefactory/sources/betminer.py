"""Betminer shadow voice adapter (SHADOW-01 T2, HUNT-01 winner).

Zero voice credit until settled evidence: this adapter only captures a
per-date shadow ledger. It never enters consensus weights, the pick path, or
price corroboration, and promotion happens only through the echo test
(>=30 shared settled fixtures vs existing donors) plus an explicit operator
decision - see docs/operator/TICKETS-OPEN.md (c).

Facts pinned by HUNT-01 (docs/operator/SOURCE-HUNT-2026-10.md section 5.1):

- RapidAPI free tier: 5 requests/day, no card, all endpoints; the free budget
  is tiny, so this adapter is **cache-first per date** (the first successful
  capture of a day is the committed capture; later runs the same day are
  cache-only and make no request) and hard-caps calls per run.
- ``GET /matches/{date}`` returns the whole day of predictions in ONE call:
  1X2/BTTS/over-under probabilities (integers 0-100), a six-outcome result
  prediction (1/X/2/1X/X2/12), correct score, HT/FT, and an odds object.
- The odds carry **no bookmaker identity** in the schema: Betminer is a voice
  donor only and is NEVER a price donor under the standing "no book name, no
  price donor" rule. The odds object is retained in rows as provenance only.

Resilience contract (mirrors bzzoiro_odds.py / betexplorer_odds.py):
single-flight throttle; one retry on 429 with a Retry-After-first 30-60s
backoff; a second 429 trips run-scoped cool-down; 401/403 classify as
``auth`` (plan/key problem - never retried harder); 402/429/430/509 classify
as ``quota``; 404 and 5xx/network classify as ``unavailable`` (fail-closed:
an unexpected shape is NEVER interpreted as an empty slate). Zero-row days
whose status is auth/quota/unavailable/blocked/cooldown stay RETRYABLE - they
are never terminal, so a later run may try again (OP-01 T4 lesson).
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

SOURCE = "betminer"
BASE = "https://betminer.p.rapidapi.com"
API_HOST = "betminer.p.rapidapi.com"
KEY_ENV = "RAPIDAPI_KEY"
UA = "EdgeFactory-cooperative-shadow/1.0 (+operator review)"
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_BETMINER_MIN_INTERVAL_S", "2.0"))
MAX_CALLS_PER_RUN = int(os.environ.get("EDGE_FACTORY_BETMINER_MAX_CALLS", "4"))
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


def matches_url(day: str) -> str:
    return f"{BASE}/matches/{day}"


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
    try:
        status, payload, rate_headers = get_json(matches_url(day))
        stats["requests"] += 1
        stats["http_statuses"].append(status)
        stats["rate_limit_headers"] = rate_headers
        if status == 200 and payload is not None:
            if payload.get("success") is False:
                stats["status"] = "unavailable"
                stats["blocker"] = f"betminer: success=false payload: {str(payload.get('error'))[:160]}"
                return [], _set_diag(stats)
            rows = parse_matches(payload, day=day)
            stats["bm_raw"] = len(rows)
            stats["bm_scored"] = len(rows)
            stats["status"] = "ok" if rows else "empty"
            stats["quota_hint"] = _quota_hint_from_headers(rate_headers)
            return rows, _set_diag(stats)
        stats["status"] = _status_for_http(status)
        stats["quota_hint"] = _quota_hint_for_status(stats["status"])
        stats["blocker"] = f"betminer: HTTP {status} or non-JSON payload"
        return [], _set_diag(stats)
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
            code = _http_code_in(message)
            stats["status"] = _status_for_http(code)
            stats["quota_hint"] = _quota_hint_for_status(stats["status"])
        stats["blocker"] = message[:180]
        stats["errors"].append(message[:180])
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
        "role": "voice-shadow (zero credit until echo test; never a price donor - odds carry no bookmaker identity)",
        "provenance": {
            "api": "RapidAPI betminer.p.rapidapi.com /matches/{date}",
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
