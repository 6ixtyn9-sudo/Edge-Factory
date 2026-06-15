"""bzzoiro_odds adapter — live odds + Polymarket from BSD API.

Reuses existing BZZOIRO_TOKEN + auth pattern from bzzoiro.py.
Fetches current-day and next-day odds for 1x2, OU2.5, BTTS across real books
(+ Polymarket when present).

Standard adapter contract:
    fetch_day(date: str) -> list[dict]
    COLUMNS = [...]

Output fields:
    source, source_type="odds", sport, date, league, home, away,
    market, selection, odds, bookmaker, captured_at
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from datetime import date as _date, datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("BZZOIRO_TOKEN")
BASE = "https://sports.bzzoiro.com/api/v2"

COLUMNS = [
    "source", "source_type", "sport", "date", "league", "home", "away",
    "market", "selection", "odds", "bookmaker", "captured_at",
]


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
    if s in {"over_under", "ou", "ou_2_5", "ou_2.5", "total_goals", "goals_over_under"}:
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


def _event_fields(item: dict) -> tuple[str | None, str | None, str | None, str, str]:
    """Return (home, away, league, event_date, captured_at) from flat/nested shapes."""
    ev = item.get("event") if isinstance(item.get("event"), dict) else item
    home = ev.get("home_team") or ev.get("home")
    away = ev.get("away_team") or ev.get("away")
    league = ev.get("league_name") or ev.get("league")
    event_date = (ev.get("event_date") or ev.get("date") or item.get("event_date") or "")[:10]
    captured = (
        item.get("captured_at")
        or item.get("updated_at")
        or datetime.now(timezone.utc).isoformat()
    )
    return home, away, league, event_date, captured


def _row(item: dict, outcome: dict, market: str, selection: str) -> dict:
    home, away, league, dt, captured = _event_fields(item)
    return {
        "source": "bzzoiro",
        "source_type": "odds",
        "sport": "soccer",
        "date": dt,
        "league": league,
        "home": home,
        "away": away,
        "market": market,
        "selection": selection,
        "odds": _decimal_odds(outcome),
        "bookmaker": outcome.get("bookmaker_name") or outcome.get("bookmaker_slug"),
        "captured_at": captured,
    }


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
    comparison = item.get("comparison") if isinstance(item.get("comparison"), dict) else item
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


def fetch_day(date: str) -> list[dict]:
    """Fetch odds for a specific date (today or tomorrow supported)."""
    if not TOKEN:
        print("bzzoiro_odds: BZZOIRO_TOKEN missing; 0 rows", file=sys.stderr)
        return []

    start = date
    end = (_date.fromisoformat(date) + timedelta(days=1)).isoformat()
    url = f"{BASE}/odds/best/?date_from={start}&date_to={end}&limit=200"

    data = _get(url)
    results = data.get("results", []) if isinstance(data, dict) else []
    out: list[dict] = []
    for item in results:
        if isinstance(item, dict):
            out.extend(_market_rows(item))

    print(f"bzzoiro_odds {date}: api_results={len(results)} rows={len(out)}", file=sys.stderr)
    return out


# Convenience: fetch both today and tomorrow (used by picks_today enrichment)
def fetch_today_tomorrow() -> list[dict]:
    today = _date.today().isoformat()
    tomorrow = (_date.today() + timedelta(days=1)).isoformat()
    return fetch_day(today) + fetch_day(tomorrow)
