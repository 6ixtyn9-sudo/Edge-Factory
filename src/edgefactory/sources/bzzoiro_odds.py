"""bzzoiro_odds adapter — live odds + Polymarket from BSD API (Phase 5).

Reuses existing BZZOIRO_TOKEN + auth pattern from bzzoiro.py.
Fetches current-day and next-day odds for 1x2, OU, BTTS across 14+ books + Polymarket.

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
import time
import urllib.request
from datetime import date as _date, timedelta
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


def _market_rows(event: dict, comparison: dict) -> list[dict]:
    """Convert /odds/comparison response into flat selection rows."""
    rows = []
    ev = event.get("event", event)
    home = ev.get("home_team") or ev.get("home")
    away = ev.get("away_team") or ev.get("away")
    league = ev.get("league_name") or ev.get("league")
    dt = (ev.get("event_date") or "")[:10]
    captured = event.get("captured_at") or ""

    # 1x2
    for outcome in comparison.get("best_odds", []):
        if outcome.get("market") != "1x2":
            continue
        sel = {"HOME": "home", "DRAW": "draw", "AWAY": "away"}.get(
            outcome.get("outcome"), outcome.get("outcome_name", "").lower()
        )
        if sel not in ("home", "draw", "away"):
            continue
        rows.append(
            {
                "source": "bzzoiro",
                "source_type": "odds",
                "sport": "soccer",
                "date": dt,
                "league": league,
                "home": home,
                "away": away,
                "market": "1x2",
                "selection": sel,
                "odds": outcome.get("decimal_odds"),
                "bookmaker": outcome.get("bookmaker_name") or outcome.get("bookmaker_slug"),
                "captured_at": captured,
            }
        )

    # Over/Under 2.5 (best odds)
    for outcome in comparison.get("best_odds", []):
        if outcome.get("market") != "over_under":
            continue
        sel = outcome.get("outcome_name", "").lower()
        if sel not in ("over", "under"):
            continue
        rows.append(
            {
                "source": "bzzoiro",
                "source_type": "odds",
                "sport": "soccer",
                "date": dt,
                "league": league,
                "home": home,
                "away": away,
                "market": "ou_2.5",
                "selection": sel,
                "odds": outcome.get("decimal_odds"),
                "bookmaker": outcome.get("bookmaker_name") or outcome.get("bookmaker_slug"),
                "captured_at": captured,
            }
        )

    # BTTS
    for outcome in comparison.get("best_odds", []):
        if outcome.get("market") != "btts":
            continue
        sel = {"YES": "yes", "NO": "no"}.get(
            outcome.get("outcome"), outcome.get("outcome_name", "").lower()
        )
        if sel not in ("yes", "no"):
            continue
        rows.append(
            {
                "source": "bzzoiro",
                "source_type": "odds",
                "sport": "soccer",
                "date": dt,
                "league": league,
                "home": home,
                "away": away,
                "market": "btts",
                "selection": sel,
                "odds": outcome.get("decimal_odds"),
                "bookmaker": outcome.get("bookmaker_name") or outcome.get("bookmaker_slug"),
                "captured_at": captured,
            }
        )

    # Polymarket (if present)
    pm = comparison.get("polymarket", {})
    if pm:
        for outcome in pm.get("outcomes", []):
            sel = outcome.get("name", "").lower()
            if sel in ("home", "draw", "away"):
                rows.append(
                    {
                        "source": "bzzoiro",
                        "source_type": "odds",
                        "sport": "soccer",
                        "date": dt,
                        "league": league,
                        "home": home,
                        "away": away,
                        "market": "1x2",
                        "selection": sel,
                        "odds": outcome.get("price"),
                        "bookmaker": "Polymarket",
                        "captured_at": captured,
                    }
                )

    return rows


def fetch_day(date: str) -> list[dict]:
    """Fetch odds for a specific date (today or tomorrow supported)."""
    if not TOKEN:
        return []

    # Use /odds/best/?date_from=...&date_to=... for efficiency
    start = date
    end = ( _date.fromisoformat(date) + timedelta(days=1) ).isoformat()
    url = f"{BASE}/odds/best/?date_from={start}&date_to={end}&limit=200"

    try:
        data = _get(url)
        out = []
        for item in data.get("results", []):
            ev = item.get("event", {})
            comp = item.get("comparison", {})
            out.extend(_market_rows(ev, comp))
        return out
    except Exception:
        return []


# Convenience: fetch both today and tomorrow (used by picks_today enrichment)
def fetch_today_tomorrow() -> list[dict]:
    today = _date.today().isoformat()
    tomorrow = (_date.today() + timedelta(days=1)).isoformat()
    return fetch_day(today) + fetch_day(tomorrow)
