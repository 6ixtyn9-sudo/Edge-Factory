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

# Parse-skip reasons that are EXPECTED provider behaviour (or our own
# documented policy), not defects and not lost supply: `active` and
# `marketActive` are provider-documented state flags ("whether the odds are
# currently active"), mainLine skipping and the internal/demo feed exclusion
# are documented capture policies. Everything else (market_id_unknown,
# unresolved_*, ambiguous_*, no_price, published_after_capture, ...) is a
# defect-or-coverage signal and stays visible as loss/diagnosis.
EXPECTED_PARSE_SKIPS = frozenset({
    "outcome_inactive",
    "market_inactive",
    "alt_line_skipped",
    "internal_feed_bookmaker",
})

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
# stable/guaranteed. The /markets catalog is fetched at runtime and each
# entry is classified from the fields the provider DOCUMENTS on it
# (oddspapi.io docs, GET /markets): marketId, marketName, marketType,
# period, handicap (the line for over/under markets), playerProp and
# outcomes[] (outcomeId -> outcomeName). "101" is the one universally
# observed 1x2 id and is kept as a safe fallback when the catalog is
# unavailable. Unknown ids are skipped, never guessed.
_FALLBACK_ID_TO_TYPE = {"101": "1x2"}
_MARKET_ID_TO_TYPE = dict(_FALLBACK_ID_TO_TYPE)
_MARKET_CATALOG: dict[str, str] = {}  # id -> raw label (for diagnosis)
# id -> the catalog entry itself (name, marketType, period, handicap,
# playerProp, outcomes). This is what selection resolution and totals lines
# are built from - the /odds payload alone carries neither outcome names
# nor lines for most books.
_MARKET_CATALOG_ENTRIES: dict[str, dict] = {}


_NON_GOAL = ("corner", "card", "throw", "offside", "shot", "penalt", "foul",
             "booking", "save", "free kick", "goal kick", "red card", "yellow",
             "inning", "margin", "period", "quarter", "set winner")
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


def _name_tokens(label: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", str(label or "").lower()) if t]


def _unpriced_family(label: str) -> str | None:
    """Recognised-but-unpriced market family for a catalog label, or None.

    Word-token matching only: "Odd" must not match inside another word, and
    "Over Under Full Time" must not match any family. Returns the stable
    ``unsupported_<family>`` marker used as the market type.
    """
    tokens = set(_name_tokens(label))
    if "handicap" in tokens or "spread" in tokens or "asian" in tokens:
        return "unsupported_handicap"
    if {"draw", "bet"} <= tokens or "dnb" in tokens:
        return "unsupported_draw_no_bet"
    if "double" in tokens and "chance" in tokens:
        return "unsupported_double_chance"
    if ("correct" in tokens and "score" in tokens) or "exact" in tokens:
        return "unsupported_correct_score"
    if "odd" in tokens or "even" in tokens:
        return "unsupported_odd_even"
    if "outright" in tokens:
        return "unsupported_outright"
    if "qualify" in tokens or "advantage" in tokens:
        return "unsupported_to_qualify"
    if "scorer" in tokens or "goalscorer" in tokens:
        return "unsupported_goalscorer"
    if "clean" in tokens and "sheet" in tokens:
        return "unsupported_clean_sheet"
    if "nil" in tokens:
        return "unsupported_win_to_nil"
    if "corners" in tokens or "corner" in tokens:
        return "unsupported_corners"
    if "cards" in tokens or "card" in tokens:
        return "unsupported_cards"
    return None


def _classify_catalog_entry(entry: dict) -> str:
    """Classify one /markets catalog entry from its DOCUMENTED fields.

    Order matters and is deliberately conservative:
      1. ``playerProp`` -> player props are never priced;
      2. ``period`` != fulltime -> a first-half/second-half market is a
         different market even when its marketType says "totals" (e.g. the
         observed "Over Under First Half", id 10262);
      3. a recognised unpriced family in the name (handicap, double chance,
         correct score, ...) -> explicit unsupported;
      4. the priced types, from marketType + name ("Over Under Team 1/2"
         carries the side in the name, observed 2026-08-05);
      5. anything else -> "" (unknown; the capture counts it as
         ``market_id_unknown`` and the census artefact names the id).
    """
    name = str(entry.get("name") or entry.get("label") or "")
    if entry.get("playerProp") is True:
        return "unsupported_player_prop"
    period = str(entry.get("period") or "").strip().lower()
    if period and period not in {"fulltime", "full_time", "full-time", "ft"}:
        return "unsupported_period"
    unpriced = _unpriced_family(name)
    if unpriced:
        return unpriced
    market_type = str(entry.get("marketType") or "").strip().lower()
    tokens = set(_name_tokens(name))
    if market_type == "1x2":
        return "1x2"
    if "both" in tokens and "teams" in tokens and "score" in tokens or "btts" in tokens:
        return "btts"
    is_team = "team" in tokens and not ("both" in tokens and "teams" in tokens)
    if is_team and ("over" in tokens or "under" in tokens or "total" in tokens):
        if "1" in tokens or "home" in tokens:
            return "team_totals_home"
        if "2" in tokens or "away" in tokens:
            return "team_totals_away"
        return ""
    if market_type in {"totals", "overunder", "over_under"} or (
            {"over", "under"} <= tokens) or "total" in tokens or "totals" in tokens:
        return "totals"
    if market_type == "double_chance":
        return "unsupported_double_chance"
    if market_type == "handicap":
        return "unsupported_handicap"
    # Legacy fallback for catalog entries that carry only a label.
    return _classify_label(name)


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


def _market_catalog_entries(payload: object) -> dict[str, dict]:
    """id -> the full documented catalog entry (name/type/period/handicap/
    playerProp/outcomes), or {} when the endpoint did not return the
    documented shape."""
    rows = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        rows = payload.get("markets") if isinstance(payload, dict) else None
    out: dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for item in rows:
        if not isinstance(item, dict):
            continue
        ident = item.get("marketId") or item.get("id")
        if ident is None:
            continue
        outcomes: dict[str, str] = {}
        raw_outcomes = item.get("outcomes")
        if isinstance(raw_outcomes, list):
            for outcome in raw_outcomes:
                if not isinstance(outcome, dict):
                    continue
                oid = outcome.get("outcomeId")
                oname = outcome.get("outcomeName")
                if oid is not None and oname:
                    outcomes[str(oid)] = str(oname)
        out[str(ident)] = {
            "name": str(item.get("marketName") or item.get("name") or item.get("label") or ""),
            "marketType": item.get("marketType"),
            "period": item.get("period"),
            "handicap": item.get("handicap"),
            "playerProp": item.get("playerProp"),
            "outcomes": outcomes,
        }
    return out


def load_market_type_map() -> dict[str, str]:
    """Fetch the /markets catalog once and map ids -> types.

    Types are the priced kinds ("1x2", "btts", "totals", "team_totals_home",
    "team_totals_away"), explicit ``unsupported_<family>`` markers for
    recognised-but-unpriced vocabulary, and - for ids the catalog did not
    return - no entry at all, which the parser counts as ``market_id_unknown``.
    Never raises: any failure keeps the fallback (101 -> 1x2 only).
    """
    global _MARKET_ID_TO_TYPE, _MARKET_CATALOG, _MARKET_CATALOG_ENTRIES
    try:
        payload = fetch_json("/markets", {"sportId": SPORT_ID_SOCCER, "language": "en"})
        catalog = _market_catalog_map(payload)
        entries = _market_catalog_entries(payload)
        mapped: dict[str, str] = {}
        for mid in catalog:
            entry = entries.get(mid, {"name": catalog[mid]})
            mtype = _classify_catalog_entry(entry)
            if mtype:
                mapped[mid] = mtype
        if mapped:
            _MARKET_ID_TO_TYPE = {**_FALLBACK_ID_TO_TYPE, **mapped}
            _MARKET_CATALOG.update(catalog)
            _MARKET_CATALOG_ENTRIES.update(entries)
    except Exception:  # noqa: BLE001 - optional endpoint; fail soft
        pass
    return dict(_MARKET_ID_TO_TYPE)


def market_catalog() -> dict[str, str]:
    """id -> raw label from the last catalog fetch (diagnosis only)."""
    return dict(_MARKET_CATALOG)


def market_catalog_entries() -> dict[str, dict]:
    """id -> documented catalog entry from the last fetch (diagnosis only)."""
    return {mid: dict(entry) for mid, entry in _MARKET_CATALOG_ENTRIES.items()}


def _catalog_entry(market_id: str, catalog: dict[str, dict] | None) -> dict:
    if catalog and market_id in catalog:
        return catalog[market_id]
    return _MARKET_CATALOG_ENTRIES.get(market_id, {})
# double-chance outcome-name -> selection
_DC_SELECTION = {
    "homeordraw": "1x", "awayordraw": "x2", "homeoraway": "12",
    "1x": "1x", "x2": "x2", "12": "12",
}

# The provider documents market 101 (Full Time Result) as carrying outcome
# ids 101 = home / 102 = draw / 103 = away (oddspapi.io tutorial: "Market
# 101 = Full Time Result (1X2); outcomes 101 home, 102 draw, 103 away"; the
# /markets docs example lists outcomeNames 1 / X / 2 for those ids). This is
# the catalog-independent fallback used ONLY inside market 101 when the
# catalog did not supply outcome names.
_1X2_OUTCOME_KEY_SELECTION = {"101": "home", "102": "draw", "103": "away"}
# Catalog outcomeNames for a 1x2 market, as documented ("1", "X", "2").
_1X2_OUTCOME_NAME_SELECTION = {
    "1": "home", "home": "home", "h": "home", "w1": "home",
    "x": "draw", "draw": "draw", "d": "draw", "tie": "draw",
    "2": "away", "away": "away", "a": "away", "w2": "away",
}


# Outcome-name field names actually observed in captured OddsPapi payloads:
# ``name`` (verified 2026-08-05 fixture payload) and ``playerName`` (the
# 2026-10-03 scrubbed schema dump, which carries no ``name`` at all). Nothing
# here is guessed - an unknown shape resolves to no name and the row is
# skipped, never priced.
_OUTCOME_NAME_FIELDS = ("name", "playerName")


def _outcome_name(player0: dict | None, outcome: dict | None) -> str:
    for container in (player0 or {}, outcome or {}):
        if not isinstance(container, dict):
            continue
        for field in _OUTCOME_NAME_FIELDS:
            value = str(container.get(field) or "").strip()
            if value:
                return value
    return ""


def _selection_from_name(name: object, home: object, away: object) -> str | None:
    """Map an outcome name to a canonical selection for 1x2 / totals / btts.

    Fail-closed on an empty name. The 2026-10-03 capture is the reason this
    guard exists: the payload carried no ``name`` and no participant names,
    so ``"" == ""`` matched the home branch and every one of the 414 captured
    rows was written as ``1x2/home``. Three different prices for the same
    fixture were all labelled the home side. An unnamed outcome has no
    resolvable side and must never be priced.
    """
    n = str(name or "").strip()
    if not n:
        return None
    low = n.lower()
    if low in {"over", "under", "yes", "no"}:
        return low
    if low in {"draw", "tie", "x"}:
        return "draw"
    home_name = str(home or "").strip().lower()
    away_name = str(away or "").strip().lower()
    if home_name and low == home_name:
        return "home"
    if away_name and low == away_name:
        return "away"
    return None


def _line_from_name(name: str) -> tuple[str | None, str | None]:
    """(side, line) when the outcome name embeds the line ("Over 2.5")."""
    m = re.search(r"(?i)\b(over|under)\s+([0-9]+(?:\.[0-9]+)?)", str(name or ""))
    if not m:
        return None, None
    return m.group(1).lower(), m.group(2)


def _catalog_outcome_selection(entry: dict, outcome_key: str) -> str | None:
    """Resolve a selection from the catalog's documented outcome names."""
    outcomes = entry.get("outcomes") if isinstance(entry, dict) else None
    if not isinstance(outcomes, dict):
        return None
    name = str(outcomes.get(outcome_key) or "").strip().lower()
    if not name:
        return None
    return _1X2_OUTCOME_NAME_SELECTION.get(name)


def rows_from_odds_response(
    data: dict,
    market_type_map: dict[str, str] | None = None,
    *,
    home: object = None,
    away: object = None,
    stats: dict | None = None,
    market_catalog: dict[str, dict] | None = None,
) -> list[dict]:
    """Convert OddsPapi odds payload to flat unified-schema rows.

    Handles 1x2, btts, double_chance, team_totals and totals when the
    market-id is classified. Unknown market ids are skipped (never guessed);
    ids the catalog classifies as recognised-but-unpriced vocabulary are
    counted as explicit ``market_unsupported_<family>`` skips. ``stats``
    receives per-reason skip counts so no skip is ever silent.

    Selection resolution is catalog-driven first and fail-closed on
    ambiguity: the outcome's identity comes from the catalog's documented
    outcome names (keyed by the outcome id the /odds payload carries), with
    the outcome's own ``playerName`` as the fallback. When BOTH resolve and
    disagree, the outcome is ambiguous and is skipped - a wrong label here
    can stake the wrong side.

    ``market_type_map`` maps market-id strings to types (as before).
    ``market_catalog`` optionally maps market-id strings to the documented
    /markets catalog entries; when absent, the entries from the last
    ``load_market_type_map()`` fetch are used.

    ``home``/``away`` let the caller supply the fixture identity it already
    holds (the /fixtures record) when the /odds payload does not repeat it.
    Fixture identity is REQUIRED: a priced row with no teams can never join
    a pick, and emitting it manufactured 414 unjoinable rows on 2026-10-03.
    """
    counters = stats if isinstance(stats, dict) else {}

    def _skip(reason: str) -> None:
        counters[reason] = int(counters.get(reason) or 0) + 1

    home = home if str(home or "").strip() else data.get("participant1Name")
    away = away if str(away or "").strip() else data.get("participant2Name")
    kickoff = data.get("startTime")
    day = str(kickoff or "")[:10]
    league = data.get("tournamentName") or data.get("categoryName")
    # Red-team F2 (fixed 2026-08-05): captured_at is OUR capture time, not
    # the provider's updatedAt (which can be stale by days). Freshness is
    # then meaningful for enh_pricing/CLV. The provider's own stamps are
    # preserved separately as published_at / provider_changed_at.
    from datetime import datetime as _dt, timezone as _tz
    captured_at = _dt.now(_tz.utc).isoformat()
    captured_dt = _dt.now(_tz.utc)
    rows: list[dict] = []
    bookmaker_odds = data.get("bookmakerOdds") or {}
    if not isinstance(bookmaker_odds, dict):
        _skip("no_bookmaker_odds")
        return rows
    if not str(home or "").strip() or not str(away or "").strip():
        # Fail closed. Without participants the row has no fixture key, so
        # it is priced evidence that can never be audited against a pick.
        _skip("fixture_identity_missing")
        return rows
    type_map = dict(market_type_map) if market_type_map else dict(_MARKET_ID_TO_TYPE)
    if not type_map:
        type_map = dict(_FALLBACK_ID_TO_TYPE)
    for bookmaker, book_data in bookmaker_odds.items():
        if not isinstance(book_data, dict):
            continue
        # OddsPapi publishes internal/demo feeds alongside real bookmaker
        # boards (pinnacle+0x / pinnacle+2x / pinnacle+live and "demo" per
        # the provider's own documentation). They are not bookmaker prices
        # and must never be counted as supply. Counted, named skip.
        book_name = str(bookmaker or "").strip().lower()
        if book_name == "demo" or book_name.startswith("pinnacle+"):
            _skip("internal_feed_bookmaker")
            continue
        markets = book_data.get("markets") or {}
        if not isinstance(markets, dict):
            continue
        for mid, mkt in markets.items():
            mtype = type_map.get(str(mid))
            if not isinstance(mkt, dict):
                continue
            if not mtype:
                # Not in the catalog at all: never seen, never classified.
                _skip("market_id_unknown")
                continue
            if mtype.startswith("unsupported"):
                # Recognised provider vocabulary this pipeline deliberately
                # does not price (handicaps, halves, props, double chance,
                # correct score, ...). A counted, named miss - not a loss
                # and not an unexamined unknown.
                _skip(f"market_{mtype}")
                continue
            # Red-team F2 (fixed 2026-08-05): dead markets/outcomes are
            # dropped at the boundary — never ingested.
            if mkt.get("marketActive") is False:
                _skip("market_inactive")
                continue
            outcomes = mkt.get("outcomes") or {}
            if not isinstance(outcomes, dict):
                continue
            entry = _catalog_entry(str(mid), market_catalog)
            # mainLine: when a market quotes several lines, only the main one
            # is the comparable price. Prefer it when the provider flags it
            # and keep every outcome when it flags none (observed both ways).
            outcome_items = [
                (key, o) for key, o in outcomes.items() if isinstance(o, dict)
            ]
            main_line_items = [(key, o) for key, o in outcome_items if _is_main_line(o)]
            if main_line_items:
                skipped_alt = len(outcome_items) - len(main_line_items)
                if skipped_alt:
                    counters["alt_line_skipped"] = int(
                        counters.get("alt_line_skipped") or 0) + skipped_alt
                outcome_items = main_line_items
            for outcome_key, outcome in outcome_items:
                players = outcome.get("players") or {}
                player0 = players.get("0") if isinstance(players, dict) else None
                if not isinstance(player0, dict):
                    continue
                if player0.get("active") is False:
                    # Provider-documented flag ("whether the odds are
                    # currently active"); a suspended/closed quote is not a
                    # price. Expected skip, reported not as loss.
                    _skip("outcome_inactive")
                    continue
                price = player0.get("price")
                if price is None:
                    _skip("no_price")
                    continue
                published_at = (
                    player0.get("bookmakerChangedAt")
                    or outcome.get("bookmakerChangedAt")
                    or mkt.get("bookmakerChangedAt")
                )
                provider_changed_at = (
                    player0.get("changedAt")
                    or outcome.get("changedAt")
                    or mkt.get("changedAt")
                )
                if _published_after(published_at, captured_dt):
                    # No-lookahead safeguard: a quote that claims to have been
                    # published after we observed it is an artefact, not a
                    # price. Enforced here, at the boundary.
                    _skip("published_after_capture")
                    continue
                name = _outcome_name(player0, outcome)
                market, selection, failure = _market_selection(
                    mtype, name, home, away, player0.get("bookmakerOutcomeId"),
                    outcome=outcome, player0=player0,
                    outcome_key=str(outcome_key), catalog_entry=entry,
                    market_id=str(mid),
                )
                if not market or not selection:
                    # "unresolved" = no evidence resolved the side; the
                    # outcome stays unpriced. "ambiguous" = two independent
                    # evidence paths disagreed; skipped for safety - a wrong
                    # selection label can stake the wrong side.
                    reason = f"{failure or 'unresolved'}_{mtype}"
                    _skip(reason)
                    if mtype == "1x2":
                        # Bounded diagnosis sample for the census artefact:
                        # the exact provider tuple behind a 1X2 miss so the
                        # next run can extend resolution from evidence, not
                        # guesswork. Provider data only, never credentials.
                        samples = counters.setdefault("_unresolved_1x2_samples", [])
                        if len(samples) < 20:
                            samples.append({
                                "reason": reason,
                                "market_id": str(mid),
                                "outcome_key": str(outcome_key),
                                "bookmaker_outcome_id": str(player0.get("bookmakerOutcomeId") or ""),
                                "player_name": str(name or ""),
                                "home": str(home or ""),
                                "away": str(away or ""),
                            })
                    continue
                # Unified schema only (same shape as theoddsapi/bzzoiro stores)
                # so enh_pricing can merge this source with zero special-casing.
                # Generation 3 also retains the provider's outcome key and
                # market id so every selection can be re-audited from the row.
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
                    "published_at": published_at,
                    "provider_changed_at": provider_changed_at,
                    "outcome_key": str(outcome_key),
                    "bookmaker_market_id": str(mkt.get("bookmakerMarketId") or ""),
                })
    return rows


def _is_main_line(outcome: dict) -> bool:
    """True when the provider flags this outcome as the main line."""
    if outcome.get("mainLine") is True:
        return True
    players = outcome.get("players") or {}
    player0 = players.get("0") if isinstance(players, dict) else None
    return isinstance(player0, dict) and player0.get("mainLine") is True


def _published_after(published_at: object, captured_dt) -> bool:
    """True when a provider publication stamp is later than our capture."""
    from edgefactory.odds_normalization import parse_zoned_timestamp

    stamp = parse_zoned_timestamp(published_at)
    if stamp is None:
        return False
    return stamp > captured_dt


def _line_from(obj: dict) -> object:
    """Read a numeric line from any of the field names providers use."""
    for k in ("line", "point", "value", "handicap", "total"):
        v = obj.get(k)
        if v is not None and v != "":
            return v
    return None


def _side_from_name(name: str) -> str | None:
    m = re.search(r"(?i)\b(over|under)\b", name)
    return m.group(1).lower() if m else None


def _market_selection(mtype: str, name: object, home: object, away: object,
                      outcome_id: object, outcome: dict | None = None,
                      player0: dict | None = None, outcome_key: str = "",
                      catalog_entry: dict | None = None,
                      market_id: str = "") -> tuple[str | None, str | None, str | None]:
    """Resolve (unified market, selection, failure) for a parsed outcome.

    Returns ``(market, selection, None)`` on success and
    ``(None, None, "unresolved" | "ambiguous")`` on failure.

    Resolution is evidence-driven and fail-closed on ambiguity:

    * the outcome's identity is resolved from the catalog's DOCUMENTED
      outcome names (outcome id -> outcomeName, e.g. 101 -> "1") when the
      outcome key is present and the catalog covers it; market 101's
      documented 101/102/103 = home/draw/away mapping is the fallback when
      the catalog supplied no outcome names;
    * ``playerName`` on the outcome is the second evidence path (team name,
      "Draw", "Over 2.5", ...);
    * when BOTH resolve and disagree the outcome is AMBIGUOUS and is
      skipped: a wrong selection label here can stake the wrong side, the
      exact hazard round 2 found;
    * totals lines come from the outcome name ("Over 2.5") or the catalog's
      documented ``handicap`` for that market id; a disagreement between the
      two is again ambiguity, never a guess.
    """
    entry = catalog_entry if isinstance(catalog_entry, dict) else {}
    if mtype == "1x2":
        from_name = _selection_from_name(name, home, away)
        from_key = _catalog_outcome_selection(entry, outcome_key)
        if from_key is None and market_id == "101":
            from_key = _1X2_OUTCOME_KEY_SELECTION.get(outcome_key)
        # The 2026-08-05 payload shape spelled the side in bookmakerOutcomeId
        # ("home"/"draw"/"away"); the current payload carries a bookmaker-
        # internal numeric id there, which simply does not match.
        from_outcome_id = OUTCOME_TO_SELECTION.get(str(outcome_id or "").lower())
        evidence = [e for e in (from_name, from_key, from_outcome_id) if e]
        if len(set(evidence)) > 1:
            return None, None, "ambiguous"
        sel = evidence[0] if evidence else None
        return ("1x2", sel, None) if sel else (None, None, "unresolved")
    if mtype == "btts":
        from_name = _selection_from_name(name, home, away)
        from_key = _catalog_outcome_selection(entry, outcome_key)
        if from_name in {"yes", "no"} and from_key in {"yes", "no"} and from_name != from_key:
            return None, None, "ambiguous"
        sel = from_name if from_name in {"yes", "no"} else (
            from_key if from_key in {"yes", "no"} else None)
        return ("btts", sel, None) if sel else (None, None, "unresolved")
    if mtype == "double_chance":
        candidates = [
            _DC_SELECTION.get(str(name or "").strip().lower().replace(" ", "")),
            _DC_SELECTION.get(str((entry.get("outcomes") or {}).get(outcome_key) or "")
                              .strip().lower().replace(" ", "")),
        ]
        resolved = [c for c in candidates if c]
        if len(set(resolved)) > 1:
            return None, None, "ambiguous"
        sel = resolved[0] if resolved else None
        return ("dc", sel, None) if sel else (None, None, "unresolved")
    if mtype in ("totals", "team_totals", "team_totals_home", "team_totals_away"):
        # Line evidence: the outcome name ("Over 2.5"), a line field on the
        # outcome/player, or the catalog's documented handicap for this
        # market id. The /odds payload itself carries no line for most
        # books - which is what made 1010 totals outcomes unresolvable.
        name_side, name_line = _line_from_name(str(name or ""))
        field_line = _line_from(player0 or {}) or _line_from(outcome or {})
        catalog_line = _catalog_line(entry)
        sides = [s for s in (
            name_side,
            _side_from_name(str(name or "")) if not name_side else None,
            _catalog_outcome_side(entry, outcome_key),
        ) if s]
        if len(set(sides)) > 1:
            return None, None, "ambiguous"
        side = sides[0] if sides else None
        lines = [str(l) for l in (name_line, field_line, catalog_line) if l is not None and l != ""]
        if lines and len({_canonical_line(l) for l in lines}) > 1:
            return None, None, "ambiguous"
        line_val = lines[0] if lines else None
        if side is None or line_val is None:
            return None, None, "unresolved"
        try:
            pstr = f"{float(line_val):g}"
        except (TypeError, ValueError):
            return None, None, "unresolved"
        if mtype == "totals":
            return (f"ou_{pstr}", side, None)
        if mtype == "team_totals_home":
            return (f"tt_home_{pstr}", side, None)
        if mtype == "team_totals_away":
            return (f"tt_away_{pstr}", side, None)
        # generic team_totals: side must come from the outcome name's team
        s = str(name or "")
        team_part = s[: re.search(r"(?i)\b(over|under)", s).start()].strip() if re.search(r"(?i)\b(over|under)", s) else s
        n = _norm_full(team_part)
        if not n:
            return None, None, "unresolved"
        if n == _norm_full(home):
            tside = "home"
        elif n == _norm_full(away):
            tside = "away"
        else:
            return None, None, "unresolved"
        return (f"tt_{tside}_{pstr}", side, None)
    return None, None, "unresolved"


def _mid_of(entry: dict) -> object:  # retained for diagnosis helpers
    """The market id of a catalog entry, if it carries one."""
    return entry.get("id") if isinstance(entry, dict) else None


def _catalog_line(entry: dict) -> str | None:
    """The catalog's documented handicap/line for a market id, if any."""
    if not isinstance(entry, dict):
        return None
    value = entry.get("handicap")
    if value is None or value == "":
        return None
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return None


def _canonical_line(value: object) -> str | None:
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return None


def _catalog_outcome_side(entry: dict, outcome_key: str) -> str | None:
    """over/under from the catalog's documented outcome name ("Over"/"Under")."""
    outcomes = entry.get("outcomes") if isinstance(entry, dict) else None
    if not isinstance(outcomes, dict):
        return None
    name = str(outcomes.get(outcome_key) or "").strip().lower()
    if name in {"over", "under"}:
        return name
    return None


def _norm_full(name: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name or "").lower())
