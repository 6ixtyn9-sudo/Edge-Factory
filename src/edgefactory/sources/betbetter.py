"""Bet Better keyless benchmark shadow adapter (SHADOW-01 T4).

Bet Better exposes an open, **keyless** JSON feed of its model's win
probabilities and fair odds under CC BY 4.0 (docs: betbetter.world/api/; the
licence and attribution strings are embedded in every payload). Coverage is
eight top soccer leagues.

Role change (operator decision, 2026-10-03)
-------------------------------------------
Bet Better was benchmark-only and never a price donor. The operator has
explicitly promoted it to an approved **fair-price donor**. Its numbers are
labelled for what they are:

- ``odds_kind="fair"`` - a model's no-vig price, NOT a market quote;
- ``provider_role="model_fair_price_donor"``;
- ``bookmaker=None`` and ``named_bookmaker=False`` - there is no book behind
  this number, so it can never satisfy named-book corroboration;
- ``price_independence_family="betbetter_fair"``.

It still earns zero voice credit: a fair price is price evidence, not a vote.
Execution eligibility is controlled by
``EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR`` (default on, operator-requested) and
the separate ``EDGE_FACTORY_FAIR_PRICE_STAKEABLE`` switch. A fair price must
never be printed as though a bookmaker were offering it.

Politeness/refresh contract: one request per league per date, min-interval
throttle, single retry on 429 then run-scoped cool-down (the betexplorer
pattern). Capture is cache-first per date: a date whose committed rows we
hold is never refetched (gap-aware rule; the first run of a day captures,
later runs the same day are cache-only). The required attribution string and
licence are stored in the ledger provenance on every persist.
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

SOURCE = "betbetter"
BASE = "https://betbetter.world"
UA = "EdgeFactory-cooperative-shadow/1.0 (+operator review)"
# The eight soccer competitions the open feed covers (site sport picker).
LEAGUE_SLUGS = (
    "epl", "la-liga", "bundesliga", "serie-a", "ligue-1",
    "mls", "brazil-serie-a", "efl-championship",
)
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_BETBETTER_MIN_INTERVAL_S", "1.5"))
MAX_CALLS_PER_RUN = int(os.environ.get("EDGE_FACTORY_BETBETTER_MAX_CALLS", "10"))
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))

_LOCK = threading.Lock()
_LAST_REQUEST = 0.0
_429S = 0
_COOLING_DOWN = False
_DIAG: dict[str, Any] = {}

# Statuses whose zero-row days must stay RETRYABLE (never terminal "empty").
RETRYABLE_ZERO_ROW_STATUSES = {"auth", "quota", "unavailable", "blocked", "error", "cooldown"}


def reset_state() -> None:
    global _LAST_REQUEST, _429S, _COOLING_DOWN
    _LAST_REQUEST = 0.0
    _429S = 0
    _COOLING_DOWN = False


def _set_diag(stats: dict[str, Any]) -> dict[str, Any]:
    _DIAG.update(stats)
    return stats


def _enabled() -> bool:
    return os.environ.get("EDGE_FACTORY_BETBETTER", "on").strip().lower() not in {"0", "off", "false", "no"}


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


def get_json(url: str, *, timeout: int = 30) -> tuple[int, Any, dict[str, str]]:
    """Fetch one URL as JSON. Never raises; caller inspects the status.

    Single-flight throttle; one retry on 429 with a Retry-After-first
    30-60s backoff; a second 429 trips run-scoped cool-down.
    """
    global _429S, _COOLING_DOWN
    if _COOLING_DOWN:
        raise _CoolingDown("betbetter: run cooling down after repeated HTTP 429 responses")
    for attempt in range(2):
        _throttle()
        request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = int(getattr(response, "status", 200))
                body = response.read(4_000_000).decode("utf-8", "replace")
                try:
                    payload = json.loads(body) if body else None
                except json.JSONDecodeError:
                    payload = None
                return status, payload, {str(k): str(v) for k, v in response.headers.items()}
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                _429S += 1
                if _429S >= 2 or attempt > 0:
                    _COOLING_DOWN = True
                    raise _RateLimited("betbetter: repeated HTTP 429; cooling down for the rest of this run") from exc
                wait = _retry_after_seconds(exc.headers.get("Retry-After") if exc.headers else None)
                time.sleep(wait)
                continue
            snippet = ""
            try:
                snippet = exc.read(200).decode("utf-8", "replace")
            except Exception:
                pass
            raise _UpstreamError(f"betbetter: HTTP {exc.code} {exc.reason}; {snippet[:120]}") from exc
        except Exception as exc:  # network/timeout family
            raise _UpstreamError(f"betbetter: {type(exc).__name__}: {exc}") from exc
    raise _UpstreamError("betbetter: exhausted retries")


class _RateLimited(RuntimeError):
    pass


class _CoolingDown(RuntimeError):
    pass


class _UpstreamError(RuntimeError):
    pass


def league_url(slug: str) -> str:
    return f"{BASE}/soccer/{slug}/picks?format=json"


def parse_game(value: object) -> tuple[str | None, str | None]:
    """Split ``Away @ Home`` into (home, away). Fail-closed on odd shapes."""
    text = str(value or "").strip()
    if " @ " not in text:
        return None, None
    away, _, home = text.partition(" @ ")
    home = home.strip()
    away = away.strip()
    if not home or not away:
        return None, None
    return home, away


def parse_picks(payload: Any, *, day: str, slug: str, url: str | None = None) -> list[dict[str, Any]]:
    """Map one league payload into benchmark shadow rows."""
    if not isinstance(payload, dict) or not isinstance(payload.get("picks"), list):
        return []
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows: list[dict[str, Any]] = []
    for pick in payload["picks"]:
        if not isinstance(pick, dict):
            continue
        home, away = parse_game(pick.get("game"))
        if not home or not away:
            continue
        kickoff = str(pick.get("gameTimeUtc") or "") or None
        # The endpoint is an upcoming board, not a day-scoped board.  Labelling
        # every returned fixture with the capture day made future matches look
        # joinable to today's slate.  Use the provider's gameTimeUtc calendar
        # date when present; retain ``day`` only for malformed/missing stamps.
        event_day = kickoff[:10] if kickoff and re.match(r"^\d{4}-\d{2}-\d{2}", kickoff) else day
        probability = pick.get("winProbabilityPct")
        if probability is None:
            probability = pick.get("modelProbabilityPct")
        try:
            probability = float(probability) if probability is not None else None
        except (TypeError, ValueError):
            probability = None
        try:
            fair_odds = float(pick.get("fairOdds")) if pick.get("fairOdds") is not None else None
        except (TypeError, ValueError):
            fair_odds = None
        raw_market = str(pick.get("market") or "").strip()
        raw_selection = str(pick.get("selection") or "").strip()
        canonical, _failure = canonical_market_selection(
            raw_market, raw_selection, home=home, away=away, line=pick.get("line"),
        )
        canonicalization_mappable = canonical is not None
        # Keep an unmappable provider row in the shadow ledger as raw evidence,
        # but mark it non-priceable. The shared bundle boundary drops it from
        # joins and reports the reason; preserving the capture is what makes
        # raw/scored/matched accounting auditable.
        canonical_market = canonical.market if canonical is not None else raw_market
        canonical_selection = canonical.selection if canonical is not None else raw_selection
        canonical_line = canonical.line if canonical is not None else pick.get("line")
        rows.append({
            "source": SOURCE,
            "date": event_day,
            "league_slug": slug,
            "home": home,
            "away": away,
            "kickoff": kickoff,
            "market": canonical_market,
            "selection": canonical_selection,
            "raw_market": raw_market,
            "raw_selection": raw_selection,
            "canonicalization_mappable": canonicalization_mappable,
            "line": canonical_line,
            "probability": probability,
            "fair_odds": fair_odds,
            # --- fair-price donor fields (operator promotion 2026-10-03) ---
            # `odds` carries the model fair price so the price board can see
            # it, and `odds_kind` makes sure nobody can mistake it for a
            # bookmaker quote.
            "odds": fair_odds,
            "odds_kind": "fair",
            "provider_role": "model_fair_price_donor",
            "bookmaker": None,
            "named_bookmaker": False,
            "price_independence_family": "betbetter_fair",
            "price_push_eligible": bool(
                canonicalization_mappable and fair_odds is not None and fair_price_donor_enabled()),
            "confidence": pick.get("confidence"),
            "attribution": str(payload.get("attribution") or "Bet Better — https://betbetter.world"),
            "licence": str(payload.get("licence") or "CC BY 4.0 — free to use with attribution to Bet Better (https://betbetter.world)"),
            "captured_at": captured_at,
        })
    return rows


def fair_price_donor_enabled() -> bool:
    """Operator switch that lets Bet Better's fair price reach a ticket."""
    raw = os.environ.get("EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR")
    if raw is None or not raw.strip():
        return True  # operator-requested default-on
    return raw.strip().lower() in {"1", "true", "yes", "on"}


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
    """Gap-aware dedupe key: source+date+home+away+market (selection-agnostic)."""

    def clean(value: object) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())

    return (
        str(row.get("source") or SOURCE),
        str(row.get("date") or ""),
        clean(row.get("home")),
        clean(row.get("away")),
        clean(row.get("market")),
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


def capture_day(day: str, *, localdata: Path | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Capture the benchmark board for one date. Cache-first, budget-capped."""
    global _429S
    stats: dict[str, Any] = {
        "status": "not_run", "bb_raw": 0, "bb_scored": 0, "requests": 0,
        "cache_hits": 0, "http_429": 0, "errors": [], "blocker": None,
        "budget": MAX_CALLS_PER_RUN, "enabled": _enabled(),
        "attribution": None, "licence": None, "canonicalization_dropped": 0,
    }
    reset_state()
    if not _enabled():
        stats["status"] = "disabled"
        stats["blocker"] = "EDGE_FACTORY_BETBETTER=off"
        return [], _set_diag(stats)
    committed = _load_ledger_rows(day, localdata=localdata)
    if committed:
        # Gap-aware: we hold committed rows for this date - never refetch.
        stats["status"] = "cache_only"
        stats["cache_hits"] = 1
        stats["bb_scored"] = len(committed)
        stats["bb_raw"] = len(committed)
        stats["attribution"] = str(committed[0].get("attribution") or "") or None
        stats["licence"] = str(committed[0].get("licence") or "") or None
        return list(committed), _set_diag(stats)
    rows: list[dict[str, Any]] = []
    for slug in LEAGUE_SLUGS:
        if stats["requests"] >= MAX_CALLS_PER_RUN:
            stats["errors"].append(f"per-run call budget {MAX_CALLS_PER_RUN} reached; remaining leagues skipped")
            break
        url = league_url(slug)
        try:
            status, payload, _headers = get_json(url)
            stats["requests"] += 1
            if status != 200 or payload is None:
                stats["errors"].append(f"{slug}: HTTP {status} or non-JSON payload")
                continue
            league_rows = parse_picks(payload, day=day, slug=slug, url=url)
            raw_picks = payload.get("picks") if isinstance(payload, dict) else None
            if isinstance(raw_picks, list):
                stats["canonicalization_dropped"] += sum(
                    1 for row in league_rows
                    if row.get("canonicalization_mappable") is False
                ) + max(0, len(raw_picks) - len(league_rows))
            rows.extend(league_rows)
            if league_rows:
                stats["attribution"] = str(payload.get("attribution") or "") or stats["attribution"]
                stats["licence"] = str(payload.get("licence") or "") or stats["licence"]
        except _CoolingDown as exc:
            stats["status"] = "cooldown"
            stats["blocker"] = str(exc)
            stats["http_429"] = _429S
            return [], _set_diag(stats)
        except _RateLimited as exc:
            stats["status"] = "blocked"
            stats["blocker"] = str(exc)
            stats["http_429"] = _429S
            return [], _set_diag(stats)
        except _UpstreamError as exc:
            stats["errors"].append(str(exc)[:180])
        except urllib.error.HTTPError as exc:
            # Defensive: the transport normally translates these; if a raw
            # HTTPError escapes anyway, classify it instead of crashing the run.
            if exc.code == 429:
                _429S += 1
                stats["status"] = "blocked"
                stats["blocker"] = f"betbetter: HTTP 429 on {slug}"
                stats["http_429"] = _429S
                return [], _set_diag(stats)
            stats["errors"].append(f"{slug}: HTTP {exc.code}")
    stats["bb_raw"] = len(rows)
    stats["bb_scored"] = len(rows)
    stats["status"] = "ok" if rows else "empty"
    return rows, _set_diag(stats)


def persist_shadow(day: str, rows: list[dict[str, Any]], stats: dict[str, Any], *, localdata: Path | None = None) -> Path:
    localdata = _resolve_localdata(localdata)
    localdata.mkdir(parents=True, exist_ok=True)
    path = localdata / f"{SOURCE}_shadow_{day}.json"
    payload = {
        "schema": 1,
        "source": SOURCE,
        "date": day,
        "role": (
            "approved fair-price donor (operator promotion 2026-10-03); model "
            "fair odds, NOT executable bookmaker quotes; zero voice credit"
        ),
        "provenance": {
            "attribution": stats.get("attribution"),
            "licence": stats.get("licence"),
            "docs": "https://betbetter.world/api/",
            "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "stats": stats,
        "rows": rows,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    return path


def diagnostics() -> dict[str, Any]:
    """Safe operational diagnostics for the last capture; never secrets."""
    return {
        "status": _DIAG.get("status"),
        "requests": _DIAG.get("requests"),
        "cache_hits": _DIAG.get("cache_hits"),
        "http_429": _429S,
        "cooling_down": _COOLING_DOWN,
        "budget": MAX_CALLS_PER_RUN,
        "errors": list(_DIAG.get("errors") or []),
    }


def fetch_day(date: str) -> list[dict]:
    return capture_day(date)[0]
