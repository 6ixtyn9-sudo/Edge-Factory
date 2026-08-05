"""OddsPapi live odds helper.

This module is intentionally used as a targeted fallback only.
It is not wired into capture_daily because free-tier quota is too small for
broad polling. Operational usage should be limited to unmatched same-day picks.
"""

from __future__ import annotations

import json
import os
import re
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


# OddsPapi market-id -> type is NOT hard-coded: the provider's ids are not
# stable/guaranteed, so we fetch the /markets catalog at runtime and classify
# each label (same logic as the probe's _category). Unknown ids are skipped,
# never guessed. "101" is the one universally-observed 1x2 id and is used as
# a safe fallback when the catalog is unavailable.
_FALLBACK_ID_TO_TYPE = {"101": "1x2"}
_MARKET_ID_TO_TYPE = dict(_FALLBACK_ID_TO_TYPE)
_MARKET_CATALOG: dict[str, str] = {}  # id -> raw label (for diagnosis)


_NON_GOAL = ("corner", "card", "throw", "offside", "shot", "penalt", "foul",
             "booking", "save", "free kick", "goal kick", "red card", "yellow",
             "inning", "margin", "period", "quarter")
_GOAL_WORDS = ("goal", "btts", "both teams", "total", "over", "under",
               "1x2", "match winner", "full time result", "double chance",
               "correct score", "winner")


def _classify_label(label: str) -> str:
    """Map a market label to a type; GOALS-ONLY, evidence-driven.

    Rules (derived from the observed /markets catalog 2026-08-05):
    - "ng"/"gg" bare substrings are NOT used (they matched "winning"/"innings");
      btts is matched on "both teams" / "btts" only.
    - "full time" alone is NOT a 1x2 signal ("Over Under Full Time" is a
      totals market); 1x2 requires "1x2" / "match winner" / "full time result".
    - Team totals arrive as "Over Under Team 1" / "Over Under Team 2" (the
      side lives in the LABEL, not the outcome name), so the type carries the
      side: "team_totals_home" / "team_totals_away".
    """
    text = label.lower()
    if any(w in text for w in _NON_GOAL):
        return ""  # corners/cards/margins/innings — not a market we price
    if not any(w in text for w in _GOAL_WORDS):
        return ""  # not clearly a goal market — never guess
    is_team = "team" in text and "both teams" not in text
    if is_team and ("over" in text or "under" in text or "total" in text):
        if "team 1" in text or "team1" in text or "home" in text:
            return "team_totals_home"
        if "team 2" in text or "team2" in text or "away" in text:
            return "team_totals_away"
        return ""  # team total but side unresolvable — skip, never guess
    if "both teams" in text or "btts" in text:
        return "btts"
    if "double chance" in text:
        return "double_chance"
    if "1x2" in text or "match winner" in text or "full time result" in text or "winner" in text:
        return "1x2"
    if "correct score" in text or "exact" in text:
        return ""
    if "total" in text or "over" in text or "under" in text:
        return "totals"
    return ""


def _market_catalog_map(payload: object) -> dict[str, str]:
    """id -> label from the optional /markets endpoint (same as the probe)."""
    rows = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        rows = payload.get("markets") if isinstance(payload, dict) else None
    out: dict[str, str] = {}
    if not isinstance(rows, list):
        return out
    for item in rows:
        if not isinstance(item, dict):
            continue
        ident = item.get("marketId") or item.get("id")
        label = item.get("marketName") or item.get("name") or item.get("label")
        if ident is not None and label:
            out[str(ident)] = str(label)
    return out


def load_market_type_map() -> dict[str, str]:
    """Fetch the /markets catalog once and map ids -> types.

    Never raises: any failure keeps the fallback (101 -> 1x2 only).
    """
    global _MARKET_ID_TO_TYPE
    try:
        payload = fetch_json("/markets", {"sportId": SPORT_ID_SOCCER, "language": "en"})
        catalog = _market_catalog_map(payload)
        mapped: dict[str, str] = {}
        for mid, label in catalog.items():
            mtype = _classify_label(label)
            if mtype:
                mapped[mid] = mtype
        if mapped:
            _MARKET_ID_TO_TYPE = {**_FALLBACK_ID_TO_TYPE, **mapped}
            _MARKET_CATALOG.update(catalog)
    except Exception:  # noqa: BLE001 - optional endpoint; fail soft
        pass
    return dict(_MARKET_ID_TO_TYPE)


def market_catalog() -> dict[str, str]:
    """id -> raw label from the last catalog fetch (diagnosis only)."""
    return dict(_MARKET_CATALOG)
# double-chance outcome-name -> selection
_DC_SELECTION = {
    "homeordraw": "1x", "awayordraw": "x2", "homeoraway": "12",
    "1x": "1x", "x2": "x2", "12": "12",
}


def _selection_from_name(name: object, home: object, away: object) -> str | None:
    """Map an outcome name to a canonical selection for 1x2 / totals / btts."""
    n = str(name or "").strip()
    low = n.lower()
    if low in {"over", "under", "yes", "no"}:
        return low
    if low in {"draw", "tie", "x"}:
        return "draw"
    if low == str(home or "").strip().lower():
        return "home"
    if low == str(away or "").strip().lower():
        return "away"
    return None


def rows_from_odds_response(data: dict, market_type_map: dict[str, str] | None = None) -> list[dict]:
    """Convert OddsPapi odds payload to flat unified-schema rows.

    Handles 1x2, btts, double_chance, team_totals and totals when the
    market-id is known. Unknown market ids are skipped (never guessed).
    ``market_type_map`` overrides the built-in id vocabulary (e.g. from a
    live catalog); keys are market-id strings, values are the types above.
    """
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
    type_map = dict(market_type_map) if market_type_map else dict(_MARKET_ID_TO_TYPE)
    if not type_map:
        type_map = dict(_FALLBACK_ID_TO_TYPE)
    for bookmaker, book_data in bookmaker_odds.items():
        if not isinstance(book_data, dict):
            continue
        markets = book_data.get("markets") or {}
        if not isinstance(markets, dict):
            continue
        for mid, mkt in markets.items():
            mtype = type_map.get(str(mid))
            if not mtype or not isinstance(mkt, dict):
                continue
            outcomes = mkt.get("outcomes") or {}
            if not isinstance(outcomes, dict):
                continue
            for outcome in outcomes.values():
                if not isinstance(outcome, dict):
                    continue
                players = outcome.get("players") or {}
                player0 = players.get("0") if isinstance(players, dict) else None
                if not isinstance(player0, dict):
                    continue
                price = player0.get("price")
                if price is None:
                    continue
                name = player0.get("name") or outcome.get("name")
                market, selection = _market_selection(
                    mtype, name, home, away, player0.get("bookmakerOutcomeId"))
                if not market or not selection:
                    continue
                # Unified schema only (same shape as theoddsapi/bzzoiro stores)
                # so enh_pricing can merge this source with zero special-casing.
                rows.append({
                    "source": "oddspapi",
                    "source_type": "odds",
                    "sport": "soccer",
                    "date": day,
                    "kickoff": kickoff,
                    "league": league,
                    "home": home,
                    "away": away,
                    "market": market,
                    "selection": selection,
                    "odds": price,
                    "bookmaker": bookmaker,
                    "captured_at": captured_at,
                })
    return rows


def _market_selection(mtype: str, name: object, home: object, away: object,
                      outcome_id: object) -> tuple[str | None, str | None]:
    """Resolve (unified market, selection) for a parsed outcome."""
    if mtype == "1x2":
        sel = OUTCOME_TO_SELECTION.get(str(outcome_id or "").lower()) or _selection_from_name(name, home, away)
        return ("1x2", sel) if sel else (None, None)
    if mtype == "btts":
        sel = _selection_from_name(name, home, away)
        return ("btts", sel) if sel in {"yes", "no"} else (None, None)
    if mtype == "double_chance":
        low = str(name or "").strip().lower().replace(" ", "")
        sel = _DC_SELECTION.get(low)
        return ("dc", sel) if sel else (None, None)
    if mtype in ("totals", "team_totals", "team_totals_home", "team_totals_away"):
        # name like "Over 2.5" / "Under 1.5" or "Halmstads BK Over 1.5"
        s = str(name or "")
        m = re.search(r"(?i)\b(over|under)\s+([0-9]+(?:\.[0-9]+)?)", s)
        if not m:
            return (None, None)
        side = m.group(1).lower()
        try:
            pstr = f"{float(m.group(2)):g}"
        except ValueError:
            return (None, None)
        if mtype == "totals":
            return (f"ou_{pstr}", side)
        if mtype == "team_totals_home":
            return (f"tt_home_{pstr}", side)
        if mtype == "team_totals_away":
            return (f"tt_away_{pstr}", side)
        # generic team_totals: side must come from the outcome name's team
        team_part = s[: m.start()].strip()
        n = _norm_full(team_part)
        if not n:
            return (None, None)
        if n == _norm_full(home):
            tside = "home"
        elif n == _norm_full(away):
            tside = "away"
        else:
            return (None, None)
        return (f"tt_{tside}_{pstr}", side)
    return (None, None)


def _norm_full(name: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name or "").lower())
