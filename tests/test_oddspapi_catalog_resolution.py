"""OddsPAPI catalog-driven resolution regressions (round 3, 2026-10-03).

Grounded in run 662c99f1's parse-skip census:

    outcome_inactive=10366  market_id_unknown=5433  unresolved_totals=1010
    market_inactive=913     unresolved_double_chance=577
    unresolved_1x2=238      unresolved_team_totals_home=207
    unresolved_team_totals_away=204  unresolved_btts=134

Root cause: the /odds payload carries neither outcome names nor lines for
most books (``playerName`` is null on team-level markets per the provider's
own websocket example), and the parser threw away the one identity the
payload DOES carry - the outcome dict key - while the /markets catalog's
own ``marketType`` / ``period`` / ``handicap`` / ``outcomes[]`` fields went
unread. These tests pin the catalog-driven repair, all from documented
shapes.
"""
from __future__ import annotations

import json
from pathlib import Path

from edgefactory.sources.oddspapi_odds import (
    _classify_catalog_entry,
    load_market_type_map,
    market_catalog_entries,
    rows_from_odds_response,
)
from edgefactory.sources import oddspapi_odds as op

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str):
    return json.loads((FIXTURES / name).read_text())


CATALOG = _load("oddspapi_markets_catalog.json")
CATALOG_ENTRIES = op._market_catalog_entries(CATALOG)
CATALOG_TYPES = {
    mid: _classify_catalog_entry(entry)
    for mid, entry in CATALOG_ENTRIES.items()
}


# ---------------------------------------------------------------------------
# Classification from the catalog's DOCUMENTED fields (not label guessing)
# ---------------------------------------------------------------------------


def test_catalog_fields_classify_the_observed_market_ids():
    """The id/type/label triples actually present in the run's payload.

    101 = Full Time Result (1x2), 10194 = Over Under Full Time (2.5),
    10262 = Over Under First Half (first half -> explicitly unsupported).
    """
    assert CATALOG_TYPES["101"] == "1x2"
    assert CATALOG_TYPES["104"] == "btts"
    assert CATALOG_TYPES["106"] == "totals"
    assert CATALOG_TYPES["10194"] == "totals"
    # A first-half market is NOT a full-time totals market even though its
    # marketType says "totals": period is checked before type.
    assert CATALOG_TYPES["10262"] == "unsupported_period"
    assert CATALOG_TYPES["10701"] == "unsupported_handicap"


def test_unpriced_families_are_word_token_matched_not_substring():
    """'Odd' must not match inside another word; 'Over Under' must not
    collide with any family."""
    assert _classify_catalog_entry(
        {"name": "Odd Even", "marketType": "x", "period": "fulltime"}) == "unsupported_odd_even"
    assert _classify_catalog_entry(
        {"name": "Double Chance", "marketType": "x", "period": "fulltime"}) == "unsupported_double_chance"
    assert _classify_catalog_entry(
        {"name": "Correct Score", "marketType": "x", "period": "fulltime"}) == "unsupported_correct_score"
    assert _classify_catalog_entry(
        {"name": "Over Under Full Time", "marketType": "totals", "period": "fulltime"}) == "totals"
    assert _classify_catalog_entry(
        {"name": "Draw No Bet", "marketType": "x", "period": "fulltime"}) == "unsupported_draw_no_bet"


# ---------------------------------------------------------------------------
# Outcome-key resolution: the identity the /odds payload actually carries
# ---------------------------------------------------------------------------


def test_unnamed_outcomes_resolve_from_catalog_outcome_names():
    """The 238 unresolved 1X2 outcomes: playerName null, but the outcome key
    is the provider's documented outcome id (101=1, 102=X, 103=2)."""
    payload = _load("oddspapi_odds_documented_shape.json")
    stats: dict = {}
    rows = rows_from_odds_response(
        payload, CATALOG_TYPES, home="Croatia", away="England",
        stats=stats, market_catalog=CATALOG_ENTRIES,
    )
    cloudbet = [r for r in rows if r["bookmaker"] == "cloudbet"]
    by_ms = {(r["market"], r["selection"]): r["odds"] for r in cloudbet}

    # Three DISTINCT 1X2 sides from outcome keys alone.
    assert by_ms[("1x2", "home")] == 4.3
    assert by_ms[("1x2", "draw")] == 3.2
    assert by_ms[("1x2", "away")] == 1.625
    # Totals resolve to ou_2.5 from the catalog's documented handicap.
    assert by_ms[("ou_2.5", "over")] == 1.98
    assert by_ms[("ou_2.5", "under")] == 1.86
    # Nothing silently dropped: first-half and Asian handicap are counted
    # unsupported misses, and the id absent from the catalog stays unknown.
    assert stats["market_unsupported_period"] == 1
    assert stats["market_unsupported_handicap"] == 1
    assert stats["market_id_unknown"] == 1


def test_documented_101_outcome_keys_resolve_without_any_catalog():
    """Even with no catalog at all, market 101's documented outcome keys
    (101 home / 102 draw / 103 away) resolve - the provider publishes this
    mapping in its own tutorial."""
    payload = _load("oddspapi_odds_documented_shape.json")
    only_101 = {
        "startTime": payload["startTime"],
        "bookmakerOdds": {
            "cloudbet": {
                "markets": {"101": payload["bookmakerOdds"]["cloudbet"]["markets"]["101"]},
            },
        },
    }
    stats: dict = {}
    rows = rows_from_odds_response(only_101, {"101": "1x2"},
                                   home="Croatia", away="England", stats=stats)
    assert {(r["selection"], r["odds"]) for r in rows} == {
        ("home", 4.3), ("draw", 3.2), ("away", 1.625)}
    assert not stats


def test_disagreeing_evidence_is_ambiguity_and_never_priced():
    """Outcome key 101 says HOME, playerName says 'England' (away): two
    independent evidence paths disagree. The outcome is skipped - a wrong
    selection label here can stake the wrong side."""
    payload = _load("oddspapi_odds_documented_shape.json")
    stats: dict = {}
    rows = rows_from_odds_response(
        payload, CATALOG_TYPES, home="Croatia", away="England",
        stats=stats, market_catalog=CATALOG_ENTRIES,
    )
    bodog = [r for r in rows if r["bookmaker"] == "bodog.eu"]
    assert bodog == [], "an ambiguous outcome must never be priced"
    assert stats["ambiguous_1x2"] == 1
    # The diagnosis sample names the exact provider tuple behind the miss.
    sample = stats["_unresolved_1x2_samples"][0]
    assert sample["market_id"] == "101"
    assert sample["outcome_key"] == "101"
    assert sample["player_name"] == "England"
    assert sample["reason"] == "ambiguous_1x2"


def test_line_disagreement_between_name_and_catalog_is_ambiguity():
    """Outcome named 'Over 2.5' on a catalog market whose documented
    handicap is 2.5 joins; the same name on a 3.5 market is ambiguous."""
    catalog = dict(CATALOG_ENTRIES)
    entry_35 = dict(catalog["10194"], handicap=3.5)
    payload = _load("oddspapi_odds_documented_shape.json")
    market = payload["bookmakerOdds"]["cloudbet"]["markets"]["10194"]
    for outcome in market["outcomes"].values():
        outcome["players"]["0"]["playerName"] = "Over 2.5"

    ok_stats: dict = {}
    rows = rows_from_odds_response(
        payload, CATALOG_TYPES, home="Croatia", away="England",
        stats=ok_stats, market_catalog=catalog,
    )
    assert any(r["market"] == "ou_2.5" and r["selection"] == "over" for r in rows)

    bad_stats: dict = {}
    rows = rows_from_odds_response(
        payload, CATALOG_TYPES, home="Croatia", away="England",
        stats=bad_stats, market_catalog={**catalog, "10194": entry_35},
    )
    assert not any(r["market"] == "ou_2.5" and r["bookmaker"] == "cloudbet" for r in rows)
    assert bad_stats["ambiguous_totals"] == 2


# ---------------------------------------------------------------------------
# outcome_inactive / market_inactive: provider-documented state, expected
# ---------------------------------------------------------------------------


def test_inactive_outcomes_are_expected_skips_not_losses():
    """`active` is a documented boolean on every price entry ("whether the
    odds are currently active"); a suspended quote is not a price. The skip
    stays counted, and the capture classifies it as expected."""
    payload = _load("oddspapi_odds_documented_shape.json")
    market = payload["bookmakerOdds"]["cloudbet"]["markets"]["101"]
    market["outcomes"]["102"]["players"]["0"]["active"] = False
    payload["bookmakerOdds"]["cloudbet"]["markets"]["10194"]["marketActive"] = False
    stats: dict = {}
    rows = rows_from_odds_response(
        payload, CATALOG_TYPES, home="Croatia", away="England",
        stats=stats, market_catalog=CATALOG_ENTRIES,
    )
    assert stats["outcome_inactive"] == 1
    assert stats["market_inactive"] == 1
    assert ("1x2", "draw") not in {(r["market"], r["selection"]) for r in rows}
    # The expected-skip classification the capture reports from.
    assert "outcome_inactive" in op.EXPECTED_PARSE_SKIPS
    assert "market_inactive" in op.EXPECTED_PARSE_SKIPS
    assert "market_id_unknown" not in op.EXPECTED_PARSE_SKIPS


def test_internal_demo_feeds_are_excluded_and_counted():
    """OddsPapi publishes internal feeds (pinnacle+0x / pinnacle+2x /
    pinnacle+live) and a demo board alongside real bookmakers; they are not
    bookmaker prices. The fixture's ``demo`` book quotes 9.99 on the same
    outcome - it must never become supply, and the skip must be counted."""
    payload = _load("oddspapi_odds_documented_shape.json")
    stats: dict = {}
    rows = rows_from_odds_response(
        payload, CATALOG_TYPES, home="Croatia", away="England",
        stats=stats, market_catalog=CATALOG_ENTRIES,
    )
    assert not any(r["bookmaker"] == "demo" for r in rows)
    assert stats["internal_feed_bookmaker"] == 1
    assert not any(r["odds"] == 9.99 for r in rows)


def test_rows_retain_the_provider_outcome_key_and_market_id():
    """Generation 3 keeps the provider's outcome key + market id so every
    written selection can be re-audited from the CSV alone (the exact
    evidence generation 2 failed to retain)."""
    payload = _load("oddspapi_odds_documented_shape.json")
    stats: dict = {}
    rows = rows_from_odds_response(
        payload, CATALOG_TYPES, home="Croatia", away="England",
        stats=stats, market_catalog=CATALOG_ENTRIES,
    )
    cloudbet = {(r["market"], r["selection"]): r for r in rows
                if r["bookmaker"] == "cloudbet"}
    home_row = cloudbet[("1x2", "home")]
    assert home_row["outcome_key"] == "101"
    assert home_row["bookmaker_market_id"] == "bm-101"
    over_row = cloudbet[("ou_2.5", "over")]
    assert over_row["outcome_key"] == "10194"
    assert over_row["bookmaker_market_id"] == "bm-10194-ou"


def test_load_market_type_map_uses_the_documented_catalog_fields(monkeypatch):
    """load_market_type_map classifies from marketType/period/playerProp and
    keeps the entries (outcome names + handicap) for resolution."""
    captured: dict = {}

    def fake_fetch_json(path, params, **_kwargs):
        captured["path"] = path
        return CATALOG

    monkeypatch.setattr(op, "fetch_json", fake_fetch_json)
    op._MARKET_ID_TO_TYPE = dict(op._FALLBACK_ID_TO_TYPE)
    op._MARKET_CATALOG_ENTRIES = {}
    op._MARKET_CATALOG = {}
    try:
        type_map = load_market_type_map()
        entries = market_catalog_entries()
    finally:
        # restore the module-level caches the test mutated
        op._MARKET_ID_TO_TYPE = dict(op._FALLBACK_ID_TO_TYPE)
        op._MARKET_CATALOG_ENTRIES = {}
        op._MARKET_CATALOG = {}
    assert captured["path"] == "/markets"
    assert type_map["101"] == "1x2"
    assert type_map["10194"] == "totals"
    assert type_map["10262"] == "unsupported_period"
    assert entries["101"]["outcomes"] == {"101": "1", "102": "X", "103": "2"}
    assert entries["10194"]["handicap"] == 2.5
