"""bzzoiro_odds adapter — live odds + Polymarket from BSD API.

Reuses existing BZZOIRO_TOKEN + auth pattern from bzzoiro.py.
Fetches current-day and next-day odds for 1x2, OU2.5, BTTS across real books
(+ Polymarket when present).

Failure disambiguation: a bare HTTP 403 used to collapse to
``quota_hint=auth_or_quota`` with the response body discarded. The 2026-11-15
run 403'd on every call against a dashboard showing 221/7,500 requests used -
the plan was demonstrably not the cause, and the receipt could not say what
was. Rejected responses now retain a scrubbed body snippet
(``error_bodies``) and classify into ``auth_reason``: ``token_rejected``,
``plan_gated``, ``rate_limited_or_quota``, ``edge_waf_blocked``, or
``auth_or_quota_unconfirmed`` when the provider said nothing recognizable.

Standard adapter contract:
    fetch_day(date: str) -> list[dict]
    COLUMNS = [...]

Output fields:
    source, source_type="odds", sport, date, kickoff, league, home, away,
    market, selection, odds, bookmaker, captured_at
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date as _date, datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("BZZOIRO_TOKEN")
BASE_V2 = "https://sports.bzzoiro.com/api/v2"
BASE_V1 = "https://sports.bzzoiro.com/api"

# Query each supported market explicitly. /odds/best defaults to 1x2,
# but relying on that made zero-row captures hard to diagnose.
MARKET_PARAMS = ("1x2", "over_under_25", "btts")

# The per-event comparison fallback is one HTTP call per event. 80-event days
# blew through the 240s source budget on 2026-09-30 before producing rows, so
# keep the default bounded; operators can raise it for a manual deep probe.
MAX_EVENT_COMPARISON = int(os.environ.get("BZZOIRO_ODDS_MAX_EVENTS", "20"))

COLUMNS = [
    "source", "source_type", "sport", "date", "kickoff", "league", "home", "away",
    "market", "selection", "odds", "bookmaker", "captured_at",
]


_DIAG: dict[str, object] = {}


def _reset_diagnostics() -> None:
    global _DIAG
    _DIAG = {
        "status": "not_run",
        "http_statuses": [],
        "errors": [],
        # Scrubbed response bodies of rejected requests (max 4, 240 chars
        # each): the status code alone could not separate "bad key" from
        # "plan-gated endpoint" from "edge WAF blocked the runner IP" on
        # 2026-11-15, when every call 403'd against a healthy dashboard.
        "error_bodies": [],
        "auth_reason": None,
        "quota_hint": "none",
        "requests": 0,
        "ok_responses": 0,
        "max_event_comparison": MAX_EVENT_COMPARISON,
        # Lets the receipt distinguish "the stage never ran" from "the
        # credential is genuinely absent". A bare not_run used to be rendered
        # credential_absent_not_run, which asserted an unverified cause.
        "credential_configured": bool(TOKEN),
    }


def diagnostics() -> dict[str, object]:
    """Return safe upstream diagnostics; never includes the API token."""
    out = dict(_DIAG)
    out["http_statuses"] = list(_DIAG.get("http_statuses") or [])
    out["errors"] = list(_DIAG.get("errors") or [])
    out["error_bodies"] = [dict(entry) for entry in (_DIAG.get("error_bodies") or [])]
    return out


def _scrub(value: str) -> str:
    """Never retain the credential; collapse whitespace for receipt storage."""
    if TOKEN:
        value = value.replace(TOKEN, "[REDACTED]")
    return " ".join(value.split())[:240]


def _http_error_body(exc: urllib.error.HTTPError) -> tuple[str | None, str | None]:
    """Read (once, defensively) a failed response's content-type and body.

    ``str(HTTPError)`` is only "HTTP Error 403: Forbidden" - the reason lives
    in the body. Tests construct HTTPError with fp=None, and real error
    streams can be consumed by earlier readers, so every step is guarded.
    """
    content_type = None
    try:
        content_type = exc.headers.get("Content-Type") if exc.headers else None
    except Exception:
        pass
    body = None
    try:
        raw = exc.read(512) if getattr(exc, "fp", None) is not None else b""
        if raw:
            body = _scrub(raw.decode("utf-8", "replace"))
    except Exception:
        pass
    return (str(content_type) if content_type else None), (body or None)


_CONTENT_EDGE_MARKERS = (
    "cf-chl", "cloudflare ray", "attention required", "access denied",
    "captcha", "verify you are human", "you have been blocked",
    "checking your browser", "enable javascript",
)
#: The provider's own words for "wrong credential" - never inferred.
_CONTENT_TOKEN_MARKERS = (
    "invalid token", "invalid api token", "token is invalid", "token expired",
    "expired token", "credentials were not provided", "invalid credentials",
    "authentication credentials",
)
#: Plan/feature gating - the fix is subscription scope, not the key.
_CONTENT_PLAN_MARKERS = (
    "do not have permission", "not permitted", "not allowed",
    "upgrade", "your plan", "subscription", "subscribe", "not included",
    "available on", "feature is not",
)
#: Throughput/budget words - the fix is pacing or quota, not the key.
_CONTENT_QUOTA_MARKERS = (
    "throttl", "too many requests", "rate limit", "ratelimit",
    "quota", "exceeded", "request limit",
)


def classify_auth_body(content_type: str | None, body: str | None) -> str:
    """Map a 401/403 response's own words onto an operator-actionable reason.

    Silence is never upgraded into a diagnosis: an empty or unrecognized body
    stays ``auth_or_quota_unconfirmed`` rather than guessing, because guessing
    sends the operator to billing when the edge WAF blocked the runner IP, or
    vice versa. Order matters: edge/WAF HTML is checked first (a Cloudflare
    "you have been blocked" page can also contain quota-flavoured words), then
    credential rejection, then plan gating, then throughput.
    """
    text = str(body or "").strip()
    if not text:
        return "auth_or_quota_unconfirmed"
    lowered = text.lower()
    is_html = "html" in str(content_type or "").lower() or "<html" in lowered or "<!doctype" in lowered
    if is_html or any(marker in lowered for marker in _CONTENT_EDGE_MARKERS):
        return "edge_waf_blocked"
    if any(marker in lowered for marker in _CONTENT_TOKEN_MARKERS):
        return "token_rejected"
    if any(marker in lowered for marker in _CONTENT_PLAN_MARKERS):
        return "plan_gated"
    if any(marker in lowered for marker in _CONTENT_QUOTA_MARKERS):
        return "rate_limited_or_quota"
    return "auth_or_quota_unconfirmed"


def _record_error(exc: Exception) -> None:
    errors = _DIAG.setdefault("errors", [])
    if not isinstance(errors, list):
        errors = []
        _DIAG["errors"] = errors
    message = str(exc).replace("\n", " ")[:180] or type(exc).__name__
    if len(errors) < 8 and message not in errors:
        errors.append(message)
    if isinstance(exc, urllib.error.HTTPError):
        statuses = _DIAG.setdefault("http_statuses", [])
        if exc.code not in statuses:
            statuses.append(exc.code)
        content_type, body = _http_error_body(exc)
        if body is not None:
            bodies = _DIAG.setdefault("error_bodies", [])
            if not isinstance(bodies, list):
                bodies = []
                _DIAG["error_bodies"] = bodies
            entry = {"status": int(exc.code), "content_type": content_type, "body": body}
            if len(bodies) < 4 and entry not in bodies:
                bodies.append(entry)
        if exc.code in {401, 403}:
            _DIAG["quota_hint"] = "auth_or_quota"
            reason = classify_auth_body(content_type, body)
            # One run, one explanation to act on: a confirmed reason is never
            # overwritten by a later one, but ANY confirmed reason upgrades an
            # earlier unconfirmed one (information only ever accumulates).
            if _DIAG.get("auth_reason") in (None, "auth_or_quota_unconfirmed"):
                _DIAG["auth_reason"] = reason
        elif exc.code in {402, 429, 430, 509}:
            _DIAG["quota_hint"] = "rate_limit_or_quota"


def _verbose() -> bool:
    return os.environ.get("BZZOIRO_ODDS_VERBOSE", "").strip().lower() in {"1", "true", "yes", "on"}


def _log(message: str, *, verbose: bool = False) -> None:
    if not verbose or _verbose():
        print(message, file=sys.stderr)


def _get(url: str, retries: int = 3):
    for attempt in range(retries):
        _DIAG["requests"] = int(_DIAG.get("requests", 0)) + 1
        try:
            req = urllib.request.Request(
                url, headers={"Authorization": f"Token {TOKEN}"}
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                _DIAG["ok_responses"] = int(_DIAG.get("ok_responses", 0)) + 1
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            _record_error(exc)
            # Keep the observed status, but do not retry the same rejected
            # request. Other endpoints retain their independent eligibility.
            if (400 <= exc.code < 500 and exc.code != 408) or exc.code == 509:
                raise
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
        except Exception as exc:
            _record_error(exc)
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))


def _market_name(raw: object) -> str | None:
    s = str(raw or "").strip().lower().replace("-", "_").replace(" ", "_")
    if s in {"1x2", "match_winner", "match_result", "winner", "full_time_result"}:
        return "1x2"
    if s in {
        "over_under", "over_under_25", "over_under_2_5", "ou", "ou_25",
        "ou_2_5", "ou_2.5", "total_goals", "total_goals_25",
        "goals_over_under", "goals_over_under_25",
    }:
        return "ou_2.5"
    if s in {"btts", "both_teams_to_score", "both_teams_score"}:
        return "btts"
    return None


def _selection(raw_outcome: object, raw_name: object, market: str | None) -> str | None:
    outcome = str(raw_outcome or "").strip().upper().replace(" ", "_")
    name = str(raw_name or "").strip().lower()

    if market == "1x2":
        if outcome in {"HOME", "1", "H"}:
            return "home"
        if outcome in {"DRAW", "X", "D"}:
            return "draw"
        if outcome in {"AWAY", "2", "A"}:
            return "away"
        if name in {"home", "draw", "away"}:
            return name
        return None

    if market == "ou_2.5":
        combined = f"{outcome} {name}".lower()
        if "under" in combined:
            return "under"
        if "over" in combined:
            return "over"
        return None

    if market == "btts":
        if outcome in {"YES", "Y"} or name in {"yes", "both teams to score - yes"}:
            return "yes"
        if outcome in {"NO", "N"} or name in {"no", "both teams to score - no"}:
            return "no"
        return None

    return None


def _decimal_odds(outcome: dict):
    return (
        outcome.get("decimal_odds")
        or outcome.get("odds")
        or outcome.get("price_decimal")
        or outcome.get("price")
    )


def _event_fields(item: dict) -> tuple[str | None, str | None, str | None, str, str | None, str]:
    """Return (home, away, league, event_date, kickoff, captured_at) from flat/nested shapes."""
    ev = item.get("event") if isinstance(item.get("event"), dict) else item
    home = ev.get("home_team") or ev.get("home")
    away = ev.get("away_team") or ev.get("away")
    league = ev.get("league_name") or ev.get("league")
    kickoff = ev.get("event_date") or ev.get("date") or item.get("event_date") or item.get("date")
    event_date = str(kickoff or "")[:10]
    captured = (
        item.get("captured_at")
        or item.get("updated_at")
        or datetime.now(timezone.utc).isoformat()
    )
    return home, away, league, event_date, kickoff, captured


def _row(item: dict, outcome: dict, market: str, selection: str) -> dict:
    home, away, league, dt, kickoff, captured = _event_fields(item)
    return {
        "source": "bzzoiro",
        "source_type": "odds",
        "sport": "soccer",
        "date": dt,
        "kickoff": kickoff,
        "league": league,
        "home": home,
        "away": away,
        "market": market,
        "selection": selection,
        "odds": _decimal_odds(outcome),
        "bookmaker": (
            outcome.get("bookmaker_name")
            or outcome.get("bookmaker")
            or outcome.get("bookmaker_slug")
            or outcome.get("bookmaker_code")
        ),
        "captured_at": captured,
    }


def _is_odds_leaf(node: dict) -> bool:
    return _decimal_odds(node) is not None and any(
        node.get(k) for k in ("bookmaker_name", "bookmaker", "bookmaker_slug", "bookmaker_code")
    )


def _comparison_market_rows(item: dict) -> list[dict]:
    """Parse /events/{id}/odds/comparison/ markets recursively.

    The comparison endpoint is the capability-proven source on this token. Its
    `markets` object may be keyed by market -> outcome -> bookmaker rows, or it
    may contain best_odds/odds lists at different levels. Walk it defensively.
    """
    markets = item.get("markets")
    if not isinstance(markets, dict):
        return []

    rows: list[dict] = []

    def walk(node, market_hint: str | None = None, outcome_hint: object = None) -> None:
        if isinstance(node, list):
            for child in node:
                walk(child, market_hint, outcome_hint)
            return
        if not isinstance(node, dict):
            return

        market = _market_name(node.get("market")) or market_hint

        def emit_or_walk(child: dict, child_market: str | None, child_outcome: object) -> None:
            sel = _selection(
                child.get("outcome") if child.get("outcome") is not None else child_outcome,
                child.get("outcome_name") or child.get("name") or child.get("selection"),
                child_market,
            )
            if child_market in {"1x2", "ou_2.5", "btts"} and sel is not None and _is_odds_leaf(child):
                rows.append(_row(item, child, child_market, sel))
            else:
                walk(child, child_market, child_outcome)

        for list_key in ("best_odds", "odds", "bookmakers", "prices"):
            value = node.get(list_key)
            if isinstance(value, list):
                for child in value:
                    if not isinstance(child, dict):
                        continue
                    child_market = _market_name(child.get("market")) or market
                    emit_or_walk(child, child_market, outcome_hint)
            elif isinstance(value, dict):
                if _is_odds_leaf(value):
                    emit_or_walk(value, _market_name(value.get("market")) or market, outcome_hint)
                else:
                    for sub_key, sub_child in value.items():
                        child_market = market
                        child_outcome = outcome_hint
                        if child_market and _selection(sub_key, None, child_market) is not None:
                            child_outcome = sub_key
                        if isinstance(sub_child, dict):
                            child = dict(sub_child)
                            if list_key in {"bookmakers", "prices"}:
                                child.setdefault("bookmaker", sub_key)
                            elif child_market and _selection(sub_key, None, child_market) is not None:
                                child.setdefault("outcome", sub_key)
                            emit_or_walk(child, _market_name(child.get("market")) or child_market, child_outcome)
                        elif list_key in {"bookmakers", "prices"} and sub_child is not None:
                            emit_or_walk(
                                {"decimal_odds": sub_child, "bookmaker": sub_key},
                                child_market,
                                child_outcome,
                            )

        if _is_odds_leaf(node):
            sel = _selection(
                node.get("outcome") if node.get("outcome") is not None else outcome_hint,
                node.get("outcome_name") or node.get("name") or node.get("selection"),
                market,
            )
            if market in {"1x2", "ou_2.5", "btts"} and sel is not None:
                rows.append(_row(item, node, market, sel))

        for key, child in node.items():
            if key in {"best_odds", "odds", "bookmakers", "prices"}:
                continue
            key_market = _market_name(key)
            next_market = key_market or market
            next_outcome = None if key_market else outcome_hint
            if next_market and _selection(key, None, next_market) is not None:
                next_outcome = key
            walk(child, next_market, next_outcome)

    walk(markets)
    return rows


def _polymarket_rows(item: dict, pm: dict) -> list[dict]:
    rows: list[dict] = []
    for outcome in pm.get("outcomes", []) or []:
        sel = _selection(outcome.get("outcome"), outcome.get("name"), "1x2")
        if sel not in ("home", "draw", "away"):
            continue
        rows.append(_row(item, {**outcome, "bookmaker_name": "Polymarket"}, "1x2", sel))
    return rows


def _market_rows(item: dict) -> list[dict]:
    """Convert /odds/best response item into flat selection rows.

    Handles both documented flat items:
      {event_date, home_team, away_team, market, best_odds:[...]}
    and older nested comparison items:
      {event:{...}, comparison:{best_odds:[...], polymarket:{...}}}
    """
    rows: list[dict] = []
    rows.extend(_comparison_market_rows(item))

    comparison = item.get("comparison") if isinstance(item.get("comparison"), dict) else item
    if comparison is not item:
        comparison_item = dict(item)
        comparison_item.update(comparison)
        rows.extend(_comparison_market_rows(comparison_item))
    item_market = _market_name(item.get("market") or comparison.get("market"))

    for outcome in comparison.get("best_odds", []) or []:
        market = _market_name(outcome.get("market")) or item_market
        if market not in {"1x2", "ou_2.5", "btts"}:
            continue
        sel = _selection(outcome.get("outcome"), outcome.get("outcome_name"), market)
        if sel is None:
            continue
        rows.append(_row(item, outcome, market, sel))

    pm = comparison.get("polymarket") if isinstance(comparison.get("polymarket"), dict) else {}
    if pm:
        rows.extend(_polymarket_rows(item, pm))

    return rows


def _results(data) -> list[dict]:
    """Return result items from common API envelope shapes."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []
    for key in ("results", "events", "data", "odds"):
        value = data.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
    return []


def _dedupe_rows(rows: list[dict]) -> list[dict]:
    out: dict[tuple, dict] = {}
    for row in rows:
        key = (
            row.get("date"), row.get("kickoff"), row.get("home"), row.get("away"),
            row.get("market"), row.get("selection"), row.get("bookmaker"),
        )
        out[key] = row
    return list(out.values())


def _fetch_url(url: str, date: str, label: str) -> tuple[int, list[dict]]:
    """Fetch one URL, parse rows, and print diagnostics. Never raises."""
    try:
        data = _get(url)
    except Exception as exc:
        _log(f"bzzoiro_odds {date}: {label} failed: {exc}", verbose=True)
        return 0, []

    items = _results(data)
    rows: list[dict] = []
    for item in items:
        rows.extend(_market_rows(item))
    # v1 /odds/best/?days=N can span multiple dates; keep requested day only.
    rows = [r for r in rows if not r.get("date") or r.get("date") == date]
    _log(f"bzzoiro_odds {date}: {label} api_results={len(items)} rows={len(rows)}", verbose=True)
    return len(items), rows


def _days_window(date: str) -> int:
    target = _date.fromisoformat(date)
    today = _date.today()
    return max(1, min(14, (target - today).days + 2))


def _event_ids_for_day(day: str) -> list[str]:
    """Fetch event ids for a date window; follows pagination defensively."""
    end = (_date.fromisoformat(day) + timedelta(days=1)).isoformat()
    url = f"{BASE_V2}/events/?{urllib.parse.urlencode({'date_from': day, 'date_to': end, 'limit': 200})}"
    ids: list[str] = []
    pages = 0
    while url and pages < 10 and len(ids) < MAX_EVENT_COMPARISON:
        pages += 1
        try:
            data = _get(url)
        except Exception as exc:
            _log(f"bzzoiro_odds {day}: events page failed: {exc}", verbose=True)
            break
        items = _results(data)
        for item in items:
            eid = item.get("id") or item.get("event_id")
            if eid is not None and str(eid) not in ids:
                ids.append(str(eid))
                if len(ids) >= MAX_EVENT_COMPARISON:
                    break
        next_url = data.get("next") if isinstance(data, dict) else None
        url = next_url if isinstance(next_url, str) and next_url else None
    _log(f"bzzoiro_odds {day}: events ids={len(ids)} pages={pages}", verbose=True)
    return ids


def _event_comparison_rows(day: str) -> list[dict]:
    """Fallback to per-event odds comparison, proven by probe_bzzoiro_odds."""
    ids = _event_ids_for_day(day)
    rows: list[dict] = []
    ok = 0
    failed = 0
    for eid in ids:
        url = f"{BASE_V2}/events/{eid}/odds/comparison/"
        try:
            data = _get(url)
            ok += 1
        except Exception as exc:
            failed += 1
            _log(f"bzzoiro_odds {day}: event {eid} comparison failed: {exc}", verbose=True)
            continue
        if isinstance(data, dict):
            rows.extend(_market_rows(data))
    rows = [r for r in rows if not r.get("date") or r.get("date") == day]
    out = _dedupe_rows(rows)
    _log(
        f"bzzoiro_odds {day}: event_comparison events={len(ids)} ok={ok} failed={failed} rows={len(out)}",
        verbose=True,
    )
    return out


def fetch_day(date: str) -> list[dict]:
    """Fetch odds for a specific date (today or tomorrow supported)."""
    _reset_diagnostics()
    if not TOKEN:
        _DIAG["status"] = "auth"
        _DIAG["quota_hint"] = "token_missing"
        _DIAG["errors"] = ["BZZOIRO_TOKEN missing"]
        raise RuntimeError("bzzoiro_odds: BZZOIRO_TOKEN missing")

    start = date
    end = (_date.fromisoformat(date) + timedelta(days=1)).isoformat()
    all_rows: list[dict] = []
    total_results = 0

    for market in MARKET_PARAMS:
        qs = urllib.parse.urlencode({
            "market": market,
            "date_from": start,
            "date_to": end,
            "limit": 200,
        })
        n, rows = _fetch_url(f"{BASE_V2}/odds/best/?{qs}", date, f"v2 market={market}")
        total_results += n
        all_rows.extend(rows)

    # Compatibility fallback: the public docs also expose /api/odds/best/?market=...&days=N.
    # Use it only when v2 returns no items for the date window.
    if total_results == 0:
        days = _days_window(date)
        for market in MARKET_PARAMS:
            qs = urllib.parse.urlencode({"market": market, "days": days})
            n, rows = _fetch_url(f"{BASE_V1}/odds/best/?{qs}", date, f"v1 market={market}")
            total_results += n
            all_rows.extend(rows)

    comparison_rows = []
    if not all_rows:
        comparison_rows = _event_comparison_rows(date)
        all_rows.extend(comparison_rows)

    out = _dedupe_rows(all_rows)
    _DIAG["best_results"] = total_results
    _DIAG["comparison_rows"] = len(comparison_rows)
    _DIAG["rows"] = len(out)
    if out:
        _DIAG["status"] = "ok"
    elif _DIAG.get("errors"):
        statuses = set(_DIAG.get("http_statuses") or [])
        if statuses and statuses <= {401, 403}:
            _DIAG["status"] = "auth"
        elif statuses & {402, 429, 430, 509}:
            _DIAG["status"] = "quota"
        else:
            _DIAG["status"] = "unavailable"
    else:
        _DIAG["status"] = "empty"
        _DIAG["quota_hint"] = "none_observed"
    auth_reason_note = f" auth_reason={_DIAG.get('auth_reason')}" if _DIAG.get("auth_reason") else ""
    _log(
        f"bzzoiro_odds {date}: best_results={total_results} "
        f"comparison_rows={len(comparison_rows)} rows={len(out)} "
        f"status={_DIAG.get('status')} http={','.join(str(x) for x in (_DIAG.get('http_statuses') or [])) or 'none'} "
        f"errors={len(_DIAG.get('errors') or [])} quota_hint={_DIAG.get('quota_hint')}"
        f"{auth_reason_note} "
        f"comparison_cap={MAX_EVENT_COMPARISON}"
    )
    return out


# Convenience: fetch both today and tomorrow (used by picks_today enrichment)
def fetch_today_tomorrow() -> list[dict]:
    today = _date.today().isoformat()
    tomorrow = (_date.today() + timedelta(days=1)).isoformat()
    return fetch_day(today) + fetch_day(tomorrow)
