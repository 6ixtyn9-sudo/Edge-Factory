"""bzzoiro_odds adapter — live odds + Polymarket from BSD API.

Reuses existing BZZOIRO_TOKEN + auth pattern from bzzoiro.py.
Fetches current-day and next-day odds for 1x2, OU2.5, BTTS across real books
(+ Polymarket when present).

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

MAX_EVENT_COMPARISON = int(os.environ.get("BZZOIRO_ODDS_MAX_EVENTS", "80"))

COLUMNS = [
    "source", "source_type", "sport", "date", "kickoff", "league", "home", "away",
    "market", "selection", "odds", "bookmaker", "captured_at",
]


def _verbose() -> bool:
    return os.environ.get("BZZOIRO_ODDS_VERBOSE", "").strip().lower() in {"1", "true", "yes", "on"}


def _log(message: str, *, verbose: bool = False) -> None:
    if not verbose or _verbose():
        print(message, file=sys.stderr)


def _get(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"Authorization": f"Token {TOKEN}"}
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception:
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
    if not TOKEN:
        _log("bzzoiro_odds: BZZOIRO_TOKEN missing; 0 rows")
        return []

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
    _log(
        f"bzzoiro_odds {date}: best_results={total_results} "
        f"comparison_rows={len(comparison_rows)} rows={len(out)}"
    )
    return out


# Convenience: fetch both today and tomorrow (used by picks_today enrichment)
def fetch_today_tomorrow() -> list[dict]:
    today = _date.today().isoformat()
    tomorrow = (_date.today() + timedelta(days=1)).isoformat()
    return fetch_day(today) + fetch_day(tomorrow)
