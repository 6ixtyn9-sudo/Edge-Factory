"""OddsPapi live odds helper.

This module is intentionally used as a targeted fallback only.
It is not wired into capture_daily because free-tier quota is too small for
broad polling. Operational usage should be limited to unmatched same-day picks.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import date as _date, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "application/json",
}

TOKEN = os.environ.get("ODDSPAPI_API_KEY")
BASE = "https://api.oddspapi.io/v4"
SPORT_ID_SOCCER = 10

OUTCOME_TO_SELECTION = {
    "home": "home",
    "draw": "draw",
    "away": "away",
}


def _get_json(url: str, retries: int = 3):
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (401, 403):
                raise
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
        except Exception as exc:  # noqa: BLE001 - keep helper dependency-free
            last = exc
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    if last is not None:
        raise last
    return None


def enabled() -> bool:
    return bool(TOKEN)


def fetch_fixtures(day: str) -> list[dict]:
    """Fetch same-day soccer fixtures with odds available."""
    if not TOKEN:
        return []
    start = f"{day}T00:00:00Z"
    end = (_date.fromisoformat(day) + timedelta(days=1)).isoformat() + "T00:00:00Z"
    qs = urllib.parse.urlencode(
        {
            "apiKey": TOKEN,
            "sportId": SPORT_ID_SOCCER,
            "from": start,
            "to": end,
            "statusId": 0,
            "hasOdds": "true",
        }
    )
    data = _get_json(f"{BASE}/fixtures?{qs}")
    return data if isinstance(data, list) else []


def fetch_odds(fixture_id: str) -> dict:
    """Fetch detailed bookmaker odds for one fixture."""
    if not TOKEN:
        return {}
    qs = urllib.parse.urlencode(
        {
            "apiKey": TOKEN,
            "fixtureId": fixture_id,
            "language": "en",
            "verbosity": 1,
        }
    )
    data = _get_json(f"{BASE}/odds?{qs}")
    return data if isinstance(data, dict) else {}


def rows_from_odds_response(data: dict) -> list[dict]:
    """Convert OddsPapi odds payload to flat 1x2 odds rows."""
    fixture_id = str(data.get("fixtureId") or "")
    home = data.get("participant1Name")
    away = data.get("participant2Name")
    kickoff = data.get("startTime")
    day = str(kickoff or "")[:10]
    league = data.get("tournamentName") or data.get("categoryName")
    captured_at = data.get("updatedAt") or kickoff
    rows: list[dict] = []
    bookmaker_odds = data.get("bookmakerOdds") or {}
    if not isinstance(bookmaker_odds, dict):
        return rows
    for bookmaker, book_data in bookmaker_odds.items():
        if not isinstance(book_data, dict):
            continue
        markets = book_data.get("markets") or {}
        market_101 = markets.get("101") if isinstance(markets, dict) else None
        if not isinstance(market_101, dict):
            continue
        outcomes = market_101.get("outcomes") or {}
        if not isinstance(outcomes, dict):
            continue
        for outcome in outcomes.values():
            if not isinstance(outcome, dict):
                continue
            players = outcome.get("players") or {}
            player0 = players.get("0") if isinstance(players, dict) else None
            if not isinstance(player0, dict):
                continue
            selection = OUTCOME_TO_SELECTION.get(str(player0.get("bookmakerOutcomeId") or "").lower())
            if not selection:
                continue
            price = player0.get("price")
            if price is None:
                continue
            rows.append(
                {
                    "source": "oddspapi",
                    "source_type": "odds",
                    "provider": "oddspapi_odds",
                    "fixture_id": fixture_id,
                    "sport": "soccer",
                    "date": day,
                    "kickoff": kickoff,
                    "league": league,
                    "home": home,
                    "away": away,
                    "market": "1x2",
                    "selection": selection,
                    "odds": price,
                    "bookmaker": bookmaker,
                    "captured_at": captured_at,
                }
            )
    return rows
