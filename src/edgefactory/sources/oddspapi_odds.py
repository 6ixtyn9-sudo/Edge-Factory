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

BASE = "https://api.oddspapi.io/v4"
SPORT_ID_SOCCER = 10

OUTCOME_TO_SELECTION = {
    "home": "home",
    "draw": "draw",
    "away": "away",
}


def api_keys() -> tuple[str, ...]:
    """Read the optional comma-separated probe/fallback key ring.

    `ODDSPAPI_API_KEYS` is the preferred plural contract. The legacy singular
    variable remains a fallback for existing local setups. Values are never
    logged or persisted by this module.
    """
    raw = os.environ.get("ODDSPAPI_API_KEYS") or os.environ.get("ODDSPAPI_API_KEY") or ""
    out: list[str] = []
    for item in raw.split(","):
        key = item.strip()
        if key and key not in out:
            out.append(key)
    return tuple(out)


def _get_json(url: str, retries: int = 3):
    """One authenticated request. Key rotation belongs to fetch_json()."""
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (401, 403, 429):
                raise
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
        except Exception as exc:  # noqa: BLE001 - dependency-free adapter
            last = exc
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    if last is not None:
        raise last
    return None


def fetch_json(path: str, params: dict[str, object], *, retries: int = 3):
    """Request OddsPapi with sequential key failover on auth/quota rejection.

    This is read-only market data. The return value contains no key material;
    callers may inspect its structure but must not print request URLs.
    """
    keys = api_keys()
    if not keys:
        return None
    last: Exception | None = None
    for key in keys:
        query = urllib.parse.urlencode({**params, "apiKey": key})
        try:
            return _get_json(f"{BASE}{path}?{query}", retries=retries)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (401, 403, 429):
                continue
            raise
    if last is not None:
        raise last
    return None


def enabled() -> bool:
    return bool(api_keys())


def fetch_fixtures(day: str) -> list[dict]:
    """Fetch same-day soccer fixtures with odds available."""
    if not enabled():
        return []
    start = f"{day}T00:00:00Z"
    end = (_date.fromisoformat(day) + timedelta(days=1)).isoformat() + "T00:00:00Z"
    data = fetch_json(
        "/fixtures",
        {
            "sportId": SPORT_ID_SOCCER,
            "from": start,
            "to": end,
            "statusId": 0,
            "hasOdds": "true",
        },
    )
    return data if isinstance(data, list) else []


def fetch_odds(fixture_id: str) -> dict:
    """Fetch detailed bookmaker odds for one fixture."""
    if not enabled():
        return {}
    data = fetch_json(
        "/odds",
        {"fixtureId": fixture_id, "language": "en", "verbosity": 1},
    )
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
