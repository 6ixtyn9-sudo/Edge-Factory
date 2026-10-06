"""SharpAPI adapter - current RapidAPI endpoint contract (2026-10-03 repair).

All transport is monkeypatched; CI never fetches and no credential is ever
written into an assertion message.
"""
from __future__ import annotations

import json

import pytest

from edgefactory.sources import sharpapi_odds as sa
from scripts import probe_sharpapi


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch, tmp_path):
    for name in ("SHARPAPI_ENDPOINT", "SHARPAPI_SPORT", "SHARPAPI_LIMIT",
                 "SHARPAPI_BOOK", "SHARPAPI_MARKET", "SHARPAPI_DATE_PARAM",
                 "SHARPAPI_LEAGUE", "SHARPAPI_KEY", "RAPIDAPI_KEY"):
        monkeypatch.delenv(name, raising=False)
    # One credential, sent to the vendor's own host. The marketplace gateway
    # key is not merely unused now - it must be absent, so a test cannot pass
    # on a credential the adapter no longer sends.
    monkeypatch.setenv("SHARPAPI_KEY", "sharp-test-key")
    # Every transport test must opt into the provider's required sport filter;
    # the adapter must not guess it in production.
    monkeypatch.setenv("SHARPAPI_SPORT", "soccer")
    monkeypatch.setattr(sa, "LOCALDATA", tmp_path)
    sa.reset_state()
    yield


def _payload():
    return {
        "events": [
            {
                "home_team": "Boston Celtics",
                "away_team": "Miami Heat",
                "start_at": "2026-10-03T23:00:00Z",
                "bookmakers": [
                    {
                        "name": "Pinnacle",
                        "markets": [
                            {"market": "1x2", "selection": "home", "price": 1.72},
                            {"market": "1x2", "selection": "away", "price": 2.20},
                        ],
                    },
                    {
                        "bookmaker": "Bet365",
                        "odds": [
                            {"name": "1x2", "label": "home", "value": 1.70},
                        ],
                    },
                ],
            }
        ]
    }


# --- endpoint and query contract -----------------------------------------

def test_default_endpoint_is_the_documented_api_v1_odds():
    assert sa.endpoint() == "/api/v1/odds"
    assert sa.odds_url("2026-10-03") == "https://api.sharpapi.io/api/v1/odds?sport=soccer"


def test_probe_confirms_documented_soccer_identifier_from_sports_response():
    # Fields mirror the provider's documented GET /api/v1/sports object.
    payload = {"data": [
        {"id": "basketball", "name": "Basketball", "leagues": ["NBA"]},
        {"id": "soccer", "name": "Soccer", "leagues": ["EPL", "MLS"]},
    ]}
    assert probe_sharpapi.soccer_identifier(payload) == "soccer"
    assert probe_sharpapi.soccer_identifier({"data": []}) is None


def test_date_is_not_sent_unless_the_operator_confirms_the_parameter():
    # The published example filters by sport/limit only. Guessing a `date`
    # filter is how a healthy source starts looking empty.
    assert "date" not in sa.odds_url("2026-10-03")


def test_query_parameters_are_configurable(monkeypatch):
    monkeypatch.setenv("SHARPAPI_SPORT", "basketball_nba")
    monkeypatch.setenv("SHARPAPI_LIMIT", "5")
    monkeypatch.setenv("SHARPAPI_BOOK", "pinnacle")
    monkeypatch.setenv("SHARPAPI_MARKET", "h2h")
    url = sa.odds_url("2026-10-03")
    assert url.startswith("https://api.sharpapi.io/api/v1/odds?")
    assert "sport=basketball_nba" in url and "limit=5" in url
    assert "book=pinnacle" in url and "market=h2h" in url


def test_confirmed_date_parameter_is_honoured(monkeypatch):
    monkeypatch.setenv("SHARPAPI_DATE_PARAM", "gameDate")
    assert "gameDate=2026-10-03" in sa.odds_url("2026-10-03")


def test_endpoint_override_is_normalized(monkeypatch):
    monkeypatch.setenv("SHARPAPI_ENDPOINT", "api/v1/odds/live")
    assert sa.endpoint() == "/api/v1/odds/live"


def test_request_goes_direct_to_the_vendor_host(monkeypatch):
    captured = {}

    class _Response:
        status = 200
        headers: dict[str, str] = {}

        def read(self, _n=0):
            return b'{"events": []}'

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout=30):
        captured["headers"] = dict(request.headers)
        captured["url"] = request.full_url
        return _Response()

    monkeypatch.setattr(sa.urllib.request, "urlopen", fake_urlopen)
    sa.get_json(sa.odds_url("2026-10-03"))
    assert captured["url"].startswith("https://api.sharpapi.io/")
    assert "rapidapi" not in captured["url"]
    assert captured["headers"]["X-api-key"] == "sharp-test-key"
    assert captured["url"].split("?", 1)[0].endswith("/api/v1/odds")
    assert "sport=soccer" in captured["url"]


# --- failure classification ----------------------------------------------

@pytest.mark.parametrize("code,status,reason", [
    (401, "auth", "http_401_auth"),
    (403, "auth", "http_403_auth_plan"),
    (429, "quota", "http_429_quota"),
    # A 404 with no captured body states no cause -- see
    # edgefactory.rapidapi_diagnostics.
    (404, "unavailable", "http_404_endpoint_contract_unconfirmed"),
])
def test_http_failures_are_classified_distinctly(monkeypatch, code, status, reason):
    monkeypatch.setattr(sa, "get_json", lambda url, timeout=30: (code, None, {}))
    rows, stats = sa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == status
    assert stats["reason"] == reason
    assert stats["status"] in sa.RETRYABLE_ZERO_ROW_STATUSES


def test_valid_empty_payload_is_not_malformed(monkeypatch):
    monkeypatch.setattr(sa, "get_json", lambda url, timeout=30: (200, {"events": []}, {}))
    rows, stats = sa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "empty"
    assert stats["reason"] == "provider_empty_slate"
    # Recognizable-but-empty must never be reported as a schema failure.
    assert stats["schema_match"] is True


def test_malformed_payload_fails_closed(monkeypatch):
    monkeypatch.setattr(sa, "get_json", lambda url, timeout=30: (200, {"nope": 1}, {}))
    rows, stats = sa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "unavailable"
    assert stats["reason"] == "schema_unrecognized"
    assert stats["schema_match"] is False


# --- parsing --------------------------------------------------------------

def test_event_book_market_payload_parses_with_named_book_provenance():
    rows, shaped = sa.parse_snapshot(_payload(), day="2026-10-03")
    assert shaped and len(rows) == 3
    assert {r["bookmaker"] for r in rows} == {"Pinnacle", "Bet365"}
    for row in rows:
        assert row["odds_kind"] == "bookmaker"
        assert row["named_bookmaker"] is True
        assert row["home"] == "Boston Celtics" and row["away"] == "Miami Heat"


def test_capture_ok_counts_events_and_rows(monkeypatch):
    monkeypatch.setattr(sa, "get_json", lambda url, timeout=30: (200, _payload(), {}))
    rows, stats = sa.capture_day("2026-10-03")
    assert stats["status"] == "ok"
    assert stats["sa_raw"] == 1 and stats["sa_matched"] == 3
    assert stats["endpoint"] == "/api/v1/odds"
    assert len(rows) == 3


def test_diagnostics_never_leak_the_key(monkeypatch):
    monkeypatch.setenv("SHARPAPI_KEY", "leak-me-not")

    def boom(url, timeout=30):
        raise sa.UpstreamBlocked("sharpapi: HTTP 500 upstream (key leak-me-not)")

    monkeypatch.setattr(sa, "get_json", boom)
    sa.capture_day("2026-10-03")
    blob = json.dumps(sa.diagnostics())
    assert "leak-me-not" not in blob
    assert "[REDACTED]" in blob


def test_missing_sport_filter_is_inert(monkeypatch):
    monkeypatch.delenv("SHARPAPI_SPORT", raising=False)
    monkeypatch.setattr(
        sa, "get_json",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("missing sport must not fetch")))
    rows, stats = sa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "not_run"
    assert stats["reason"] == "missing_sport_filter"
    assert "sport" in str(stats["blocker"])


def test_missing_key_is_inert(monkeypatch):
    monkeypatch.delenv("SHARPAPI_KEY", raising=False)
    monkeypatch.setattr(
        sa, "get_json",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("keyless run must not fetch")))
    rows, stats = sa.capture_day("2026-10-03")
    assert rows == [] and stats["status"] == "not_run"


# --- the single X-API-Key credential --------------------------------------
# The adapter used to route through the RapidAPI marketplace and send two
# credentials. That produced 401 {"error":{"code":"disabled_api_key"}} in
# production on 2026-10-06. The vendor playground shows the operator's
# account is a direct one: one host, one header. These tests pin that the
# gateway headers are GONE, not merely optional - a request that still
# carries them is the bug that wasted a fortnight.


def _capture_headers(monkeypatch):
    """Run one request through a fake transport and return the sent headers."""
    captured: dict = {}

    class _Response:
        status = 200
        headers: dict[str, str] = {}

        def read(self, _n=0):
            return b'{"events": []}'

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout=30):
        captured["headers"] = dict(request.headers)
        return _Response()

    monkeypatch.setattr(sa.urllib.request, "urlopen", fake_urlopen)
    sa.get_json(sa.odds_url("2026-10-07"))
    return captured["headers"]


def test_origin_key_is_sent_as_x_api_key(monkeypatch):
    monkeypatch.setenv("SHARPAPI_KEY", "origin-key")
    headers = _capture_headers(monkeypatch)
    # urllib title-cases header names.
    assert headers["X-api-key"] == "origin-key"


def test_the_marketplace_gateway_headers_are_gone(monkeypatch):
    """No gateway credential may survive, even if one is left in the env."""
    monkeypatch.setenv("RAPIDAPI_KEY", "gateway-key")
    monkeypatch.setenv("SHARPAPI_KEY", "origin-key")
    headers = sa.auth_headers()
    assert headers == {"X-API-Key": "origin-key"}
    sent = _capture_headers(monkeypatch)
    assert not any(k.lower().startswith("x-rapidapi") for k in sent)
    assert "gateway-key" not in json.dumps(sent)


def test_unset_key_never_reaches_the_network_at_all(monkeypatch):
    """Without a credential the adapter must not spend a call to find out."""
    monkeypatch.delenv("SHARPAPI_KEY", raising=False)
    monkeypatch.setattr(
        sa.urllib.request, "urlopen",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("keyless run must not fetch")))
    with pytest.raises(sa.UpstreamBlocked):
        sa.get_json(sa.odds_url())


def test_blank_key_is_treated_as_absent(monkeypatch):
    """Whitespace is not a credential; it must not buy a request either."""
    monkeypatch.setenv("SHARPAPI_KEY", "   ")
    assert sa._key() is None
    with pytest.raises(sa.UpstreamBlocked):
        sa.get_json(sa.odds_url())


def test_diagnostics_never_leak_the_origin_key(monkeypatch):
    """Providers quote the offending credential in auth errors; redact it."""
    monkeypatch.setenv("RAPIDAPI_KEY", "gateway-key")
    monkeypatch.setenv("SHARPAPI_KEY", "origin-leak-me-not")

    def boom(url, timeout=30):
        raise sa.UpstreamBlocked(
            'sharpapi: HTTP 401 Unauthorized; {"error":{"code":"disabled_api_key",'
            '"key":"origin-leak-me-not"}}')

    monkeypatch.setattr(sa, "get_json", boom)
    monkeypatch.setenv("SHARPAPI_SPORT", "soccer")
    sa.capture_day("2026-10-07")
    blob = json.dumps(sa.diagnostics())
    assert "origin-leak-me-not" not in blob
    assert "[REDACTED]" in blob


# --- unmappable markets must count, not crash -----------------------------


def test_unmappable_market_is_counted_not_crashed():
    """Reachable only once auth succeeds: an unknown market used to raise
    NameError and abort the whole snapshot instead of dropping one row."""
    payload = {"events": [{"home": "A", "away": "B", "bookmakers": [
        {"name": "bk", "markets": [
            {"market": "TOTALLY_UNKNOWN", "selection": "???", "price": 2.0},
            {"market": "1X2", "selection": "A", "price": 2.5},
        ]}]}]}
    rows, shaped = sa.parse_snapshot(payload, day="2026-10-07")
    assert shaped is True
    # The good row survives; the unmappable one is accounted for, not fatal.
    assert len(rows) == 1
    assert sum(sa._CANONICALIZATION_DROP_REASONS.values()) == 1


# --- the flat board the vendor actually sends -----------------------------
# Captured from the vendor playground on 2026-10-06 (soccer, 50 rows): the
# response is NOT nested event->bookmakers->markets. It is one record per
# selection. The old parser looked for a "bookmakers" list, never found one,
# and reported "schema not recognized" - so even a perfectly authenticated
# request would have produced zero rows. Auth was only the first of two bugs.


def _flat(**over):
    row = {"event_id": "soccer_x_2026-10-06_kazakhstan_moldova_x1",
           "event_uuid": "u-1", "home_team": "Moldova U21",
           "away_team": "Kazakhstan U21", "league": "uefa_-_nations_league",
           "sportsbook": "fanduel", "market_type": "moneyline",
           "selection": "Moldova U21", "selection_type": "home",
           "odds_decimal": 2.1, "odds_american": 110, "is_live": False,
           "event_start_time": "2026-10-06T18:45:00Z"}
    row.update(over)
    return row


def test_flat_selection_rows_are_parsed():
    rows, shaped = sa.parse_snapshot({"data": [_flat()]}, day="2026-10-06")
    assert shaped and len(rows) == 1
    assert rows[0]["market"] == "1x2" and rows[0]["selection"] == "home"
    assert rows[0]["odds"] == 2.1 and rows[0]["book"] == "fanduel"
    assert rows[0]["named_bookmaker"] is True


def test_the_three_way_draw_survives():
    """The draw is the whole reason this vendor is worth probing."""
    rows, _ = sa.parse_snapshot(
        {"data": [_flat(selection="Draw", selection_type="draw", odds_decimal=3.4)]},
        day="2026-10-06")
    assert [r["selection"] for r in rows] == ["draw"]


def test_total_goals_becomes_a_canonical_over_under_line():
    rows, _ = sa.parse_snapshot(
        {"data": [_flat(market_type="total_goals", selection="Over 2.5",
                        selection_type="over", line=2.5, odds_decimal=1.91)]},
        day="2026-10-06")
    assert rows[0]["market"] == "ou_2.5" and rows[0]["selection"] == "over"
    # The shared normalizer emits the line as a string; matched here rather
    # than special-cased, so this source stores what every other source does.
    assert str(rows[0]["line"]) == "2.5"


def test_sides_come_from_the_declared_fields_not_the_event_id_slug():
    """The slug does not encode orientation and must never be trusted.

    Both fixtures below carry Kazakhstan FIRST in the identifier, yet one is
    a Moldova home fixture and the other a Kazakhstan home fixture. A parser
    keyed off the slug inverts one of them - and an inverted side still
    prices cleanly, so nothing downstream would ever notice.
    """
    rows, _ = sa.parse_snapshot({"data": [
        _flat(event_id="soccer_x_kazakhstan_moldova_x1",
              home_team="Moldova U21", away_team="Kazakhstan U21"),
        _flat(event_id="soccer_x_faroeislands_kazakhstan_x2",
              home_team="Kazakhstan", away_team="Faroe Islands",
              selection="Kazakhstan"),
    ]}, day="2026-10-06")
    assert [(r["home"], r["away"]) for r in rows] == [
        ("Moldova U21", "Kazakhstan U21"), ("Kazakhstan", "Faroe Islands")]


def test_reference_objects_are_flattened():
    rows, _ = sa.parse_snapshot({"data": [{
        "home": {"name": "Gibraltar U21"}, "away": {"name": "Wales U21"},
        "sportsbook_ref": {"name": "fanduel"}, "market_type": "moneyline",
        "selection_type": "away", "odds_decimal": 1.3, "is_live": False}]},
        day="2026-10-06")
    assert rows[0]["home"] == "Gibraltar U21" and rows[0]["book"] == "fanduel"
    assert rows[0]["selection"] == "away"


@pytest.mark.parametrize("flag,reason", [
    ("is_live", "live_price"),
    ("is_stale_pregame_price", "stale_pregame_price"),
    ("is_player_prop", "player_prop"),
])
def test_non_prematch_prices_are_refused_and_counted(flag, reason):
    """An in-play price is not a worse prematch price - it is another thing."""
    rows, shaped = sa.parse_snapshot({"data": [_flat(**{flag: True})]},
                                     day="2026-10-06")
    assert rows == [] and shaped is True
    assert sa._PREMATCH_DROP_REASONS == {reason: 1}


def test_an_all_live_board_is_not_reported_as_an_empty_slate(monkeypatch):
    """Opposite diagnoses: 'no games' vs 'we captured too late'."""
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": [_flat(is_live=True)]}, {}))
    rows, stats = sa.capture_day("2026-10-06")
    assert rows == [] and stats["status"] == "empty"
    assert stats["reason"] == "all_rows_live_or_stale"
    assert stats["prematch_dropped"] == 1
    assert stats["prematch_drop_reasons"] == {"live_price": 1}


def test_an_empty_board_still_reads_as_an_empty_slate(monkeypatch):
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": []}, {}))
    rows, stats = sa.capture_day("2026-10-06")
    assert rows == [] and stats["reason"] == "provider_empty_slate"
    assert stats["prematch_dropped"] == 0


def test_an_unmappable_board_is_distinguished_from_both(monkeypatch):
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (
        200, {"data": [_flat(market_type="correct_score", selection="1-5",
                             selection_type=None)]}, {}))
    rows, stats = sa.capture_day("2026-10-06")
    assert rows == [] and stats["reason"] == "all_rows_unmappable"
    assert stats["canonicalization_dropped"] == 1


def test_a_mixed_board_keeps_only_the_prematch_rows(monkeypatch):
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": [
        _flat(), _flat(is_live=True), _flat(selection="Draw",
                                            selection_type="draw",
                                            odds_decimal=3.4)]}, {}))
    rows, stats = sa.capture_day("2026-10-06")
    assert len(rows) == 2 and stats["status"] == "ok"
    assert stats["sa_raw"] == 1 and stats["sa_matched"] == 2
    assert stats["prematch_dropped"] == 1


def test_the_league_filter_is_sent_when_configured(monkeypatch):
    monkeypatch.setenv("SHARPAPI_LEAGUE", "uefa_-_nations_league")
    assert "league=uefa_-_nations_league" in sa.odds_url("2026-10-06")


def test_the_league_filter_is_absent_by_default():
    assert "league=" not in sa.odds_url("2026-10-06")


def test_the_nested_legacy_shape_still_parses():
    """Back-compat: a nested payload must not regress to the flat branch."""
    rows, shaped = sa.parse_snapshot({"events": [{
        "home": "A", "away": "B", "bookmakers": [{"name": "pinnacle",
        "markets": [{"market": "1x2", "selection": "A", "price": 2.0}]}]}]},
        day="2026-10-06")
    assert shaped and len(rows) == 1 and rows[0]["book"] == "pinnacle"


def test_the_key_never_appears_in_a_flat_capture(monkeypatch):
    monkeypatch.setenv("SHARPAPI_KEY", "flat-secret")
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": [_flat()]}, {}))
    rows, stats = sa.capture_day("2026-10-06")
    assert rows and "flat-secret" not in json.dumps(stats)
    assert "flat-secret" not in json.dumps(sa.diagnostics())


def test_the_default_endpoint_is_the_direct_host_path():
    """The gateway-relative '/odds' is wrong for api.sharpapi.io."""
    assert sa.DEFAULT_ENDPOINT == "/api/v1/odds"
    assert sa.BASE == "https://api.sharpapi.io"


def test_the_effective_endpoint_is_recorded_in_the_capture_stats(monkeypatch):
    """An override that silently undoes the fix must be visible afterwards.

    A deployment pinned the endpoint to a gateway-relative path, which
    overrode the adapter's corrected default for weeks without appearing
    anywhere in the diagnostics. Recording what was ACTUALLY called is the
    cheap defence: the health row now names the path, so a wrong override
    shows up as data rather than as a mystery 404.
    """
    monkeypatch.setenv("SHARPAPI_ENDPOINT", "/odds")
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": []}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["endpoint"] == "/odds"


# --- ticket (o): a zero must name which zero it was -----------------------
#
# The 2026-10-06 production run asked for an unfiltered global soccer board
# with a 100-row limit, got HTTP 200, and reported "all rows live or stale".
# That token tells the operator to capture earlier. If the board is sorted
# live-first and the page filled before reaching our fixtures, capturing
# earlier changes nothing and the real remedy is to narrow the request.
# These are opposite actions behind one token, so the token had to split.


def _live_board(count, league=lambda i: f"lg_{i % 7}"):
    """A full page of in-play rows across several competitions."""
    return [_flat(home_team=f"H{i}", away_team=f"A{i}", league=league(i),
                  is_live=True) for i in range(count)]


def test_a_full_page_of_live_rows_asks_to_narrow_not_to_wait(monkeypatch):
    """The page hit its own limit, so the tail was never seen."""
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": _live_board(100)}, {}))
    rows, stats = sa.capture_day("2026-10-06")
    assert rows == []
    assert stats["reason"] == "board_truncated_live_first"
    assert stats["board_truncated"] is True
    assert stats["board_rows"] == 100 and stats["board_fixtures"] == 100
    assert stats["board_non_prematch_rows"] == 100


def test_a_short_all_live_board_still_reads_as_a_late_capture(monkeypatch):
    """The contrast case: the board ended well short of the limit.

    Nothing was cut off, so every game really had started and the original
    advice - capture earlier - is still the right one.
    """
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": _live_board(6)}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["reason"] == "all_rows_live_or_stale"
    assert stats["board_truncated"] is False


def test_a_competition_filter_the_server_ignored_is_not_an_empty_board(monkeypatch):
    """The trap this ticket was written around.

    A competition identifier the vendor does not recognise produces the same
    bare zero as a competition with no games on. They are told apart only by
    reading what the board actually contained: a board carrying several
    OTHER competitions is a filter that was never applied.
    """
    monkeypatch.setenv("SHARPAPI_LEAGUE", "uefa_-_nations_league")
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": _live_board(100)}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["reason"] == "league_filter_not_applied"
    assert stats["league_filter_effective"] is False
    assert stats["league_filter_requested"] is True


def test_a_competition_filter_onto_an_empty_board_says_so(monkeypatch):
    monkeypatch.setenv("SHARPAPI_LEAGUE", "uefa_-_nations_league")
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": []}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["reason"] == "league_filter_returned_empty"
    assert stats["board_rows"] == 0


def test_a_single_unmatched_competition_is_not_called_a_rejected_filter(monkeypatch):
    """Ticket (l) hazard: the vendor spells one competition several ways.

    With exactly one competition on the board and no textual match, "the
    filter was rejected" and "this is the vendor's other spelling" are both
    live explanations. The verdict must stay unknown rather than accuse.
    """
    monkeypatch.setenv("SHARPAPI_LEAGUE", "uefa_-_nations_league")
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (
        200, {"data": [_flat(is_live=True, league="brazil_serie_a")]}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["league_filter_effective"] is None
    assert stats["reason"] != "league_filter_not_applied"


def test_an_alternate_spelling_counts_as_the_filter_working(monkeypatch):
    monkeypatch.setenv("SHARPAPI_LEAGUE", "uefa_-_nations_league")
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (
        200, {"data": [_flat(is_live=True, league="UEFA Nations League A")]}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["league_filter_effective"] is True


def test_board_counts_never_survive_into_an_unrecognized_payload(monkeypatch):
    """A stale count reads as a measurement of the wrong response."""
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": _live_board(9)}, {}))
    _rows, first = sa.capture_day("2026-10-06")
    assert first["board_rows"] == 9
    sa.reset_state()
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"unexpected": "shape"}, {}))
    _rows, second = sa.capture_day("2026-10-07")
    assert second["reason"] == "schema_unrecognized"
    assert second["board_rows"] == 0 and second["board_fixtures"] == 0


def test_the_configured_competition_value_never_reaches_the_capture_stats(monkeypatch):
    """The filter arrives from a deployment secret; the record is committed."""
    monkeypatch.setenv("SHARPAPI_LEAGUE", "a-private-competition-id")
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": _live_board(4)}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert "a-private-competition-id" not in json.dumps(stats)
    assert stats["league_filter_requested"] is True


def test_board_context_is_recorded_on_a_successful_capture_too(monkeypatch):
    """A capture that DID price rows still has to say how big the board was.

    Otherwise a narrowing that quietly stopped being applied looks identical
    to one that is still working.
    """
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": [_flat()]}, {}))
    rows, stats = sa.capture_day("2026-10-06")
    assert rows and stats["status"] == "ok"
    assert stats["board_rows"] == 1 and stats["board_priced_rows"] == 1
    assert stats["board_leagues"] == {"uefa_-_nations_league": 1}


# --- ticket (o) follow-up: "refused" is not one fault, it is three --------
#
# The first cut of this classification folded every prematch refusal into
# one live-or-stale token. A board that was entirely player props therefore
# reported itself as live, which is not a missing distinction but a false
# statement about a board with no live rows on it. The refusal groups ask
# for different remedies, so they are reported separately.


def _props_board(count):
    return [_flat(home_team=f"H{i}", away_team=f"A{i}", is_player_prop=True)
            for i in range(count)]


def test_a_board_of_player_props_is_never_reported_as_live(monkeypatch):
    """Nothing on this board was in-play; the token must not say it was."""
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": _props_board(100)}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["reason"] == "board_truncated_player_props"
    assert "live" not in stats["reason"]
    assert stats["prematch_drop_reasons"] == {"player_prop": 100}


def test_a_short_board_of_player_props_is_named_without_truncation(monkeypatch):
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    monkeypatch.setattr(sa, "get_json",
                        lambda *a, **k: (200, {"data": _props_board(6)}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["reason"] == "all_rows_player_props"


def test_live_rows_outrank_player_props_when_both_are_present(monkeypatch):
    """Timing beats market selection.

    An in-play row is a different quantity and would corrupt a closing-line
    measurement, so it invalidates the capture window itself. A prop row is
    only a market we never bet. Reporting the props while live rows are
    also on the board would hide the more serious of the two faults.
    """
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    mixed = ([_flat(home_team=f"L{i}", away_team=f"A{i}", is_live=True)
              for i in range(50)] + _props_board(50))
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": mixed}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["reason"] == "board_truncated_live_first"
    assert stats["prematch_drop_reasons"]["live_price"] == 50
    assert stats["prematch_drop_reasons"]["player_prop"] == 50


def test_a_board_whose_rows_carry_no_usable_price_is_named_separately(monkeypatch):
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (
        200, {"data": [_flat(odds_decimal=None)]}, {}))
    _rows, stats = sa.capture_day("2026-10-06")
    assert stats["reason"] == "all_rows_unpriced"


def test_the_classification_warns_the_next_reader_off_the_empty_map():
    """The inference that was drawn wrongly once, fenced at the site.

    An empty vocabulary-failure map is empty because the prematch refusal
    runs first and nothing reached the mapper. It means untested, never
    agrees. The warning lives at the branch rather than in a document,
    because the branch is where someone reads the empty map.
    """
    import inspect
    source = inspect.getsource(sa._zero_row_reason)
    assert "BEFORE CONCLUDING ANYTHING ABOUT MARKET VOCABULARY" in source
    assert "never" in source and "agrees" in source


# --- ticket (o) follow-up 2: on a global board, whose fixtures are these? --
#
# The request defaults to sport and limit only, so the board is the whole
# world's soccer. Soccer runs continuously somewhere, so in-play rows at the
# top of an unfiltered board are background noise, not a statement about our
# capture window. A board of 100 in-play Brazilian games and a board of 100
# prop-only Japanese games are equally uninformative about whether tonight's
# fixtures were quotable. The overlap between the board and our card is the
# number that decides the next move, so it outranks every refusal token.


def _team_key(name):
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


CARD = [("Scotland", "Portugal"), ("Croatia", "Czechia")]


def _strangers(count, **over):
    return [_flat(home_team=f"Flamengo{i}", away_team=f"Gremio{i}",
                  is_live=True, **over) for i in range(count)]


def _capture(payload, card=CARD, monkeypatch=None):
    monkeypatch.setattr(sa, "get_json", lambda *a, **k: (200, {"data": payload}, {}))
    return sa.capture_day("2026-10-06", card=card, team_key=_team_key)


def test_a_global_board_without_our_fixtures_says_exactly_that(monkeypatch):
    """The refusal tokens describe strangers; the verdict must not."""
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    _rows, stats = _capture(_strangers(100), monkeypatch=monkeypatch)
    assert stats["reason"] == "our_fixtures_absent_from_board"
    assert stats["card_fixtures_on_board"] == 0
    assert stats["card_fixture_count"] == 2


def test_our_own_rows_decide_the_diagnosis_not_the_strangers(monkeypatch):
    """A hundred in-play strangers must not mask what OUR rows were.

    Before the overlap was measured, the board-wide counters won and this
    board reported itself as truncated live-first. Our two fixtures were
    on it, and they were props - a different remedy entirely.
    """
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    payload = _strangers(98) + [
        _flat(home_team="Scotland", away_team="Portugal", is_player_prop=True),
        _flat(home_team="Croatia", away_team="Czechia", is_player_prop=True)]
    _rows, stats = _capture(payload, monkeypatch=monkeypatch)
    assert stats["reason"] == "board_truncated_player_props"
    assert stats["card_fixtures_on_board"] == 2
    assert stats["card_prematch_drop_reasons"] == {"player_prop": 2}
    # the board-wide count still records the strangers, unchanged
    assert stats["prematch_drop_reasons"]["live_price"] == 98


def test_our_fixtures_listed_the_other_way_round_are_not_called_absent(monkeypatch):
    """An inverted board is a different fault from an empty one.

    This vendor is already known to contradict itself on which side is at
    home, so a reversed pair is a live possibility rather than a curiosity.
    """
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    payload = _strangers(99) + [_flat(home_team="Portugal",
                                      away_team="Scotland", is_live=True)]
    _rows, stats = _capture(payload, monkeypatch=monkeypatch)
    assert stats["reason"] == "our_fixtures_absent_sides_reversed"
    assert stats["card_fixtures_reversed"] == 1


def test_an_empty_board_is_not_dressed_up_as_a_coverage_finding(monkeypatch):
    """Absence only means something once something came back."""
    _rows, stats = _capture([], monkeypatch=monkeypatch)
    assert stats["reason"] == "provider_empty_slate"


def test_our_fixtures_priced_reports_them_separately(monkeypatch):
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    payload = _strangers(98) + [_flat(home_team="Scotland", away_team="Portugal"),
                                _flat(home_team="Croatia", away_team="Czechia")]
    rows, stats = _capture(payload, monkeypatch=monkeypatch)
    assert len(rows) == 2 and stats["status"] == "ok"
    assert stats["card_priced_rows"] == 2


def test_without_a_card_the_board_wide_reading_is_unchanged(monkeypatch):
    """Back-compat: callers that pass no card see the previous behaviour."""
    monkeypatch.setenv("SHARPAPI_LIMIT", "100")
    _rows, stats = _capture(_strangers(100), card=None, monkeypatch=monkeypatch)
    assert stats["reason"] == "board_truncated_live_first"
    assert stats["card_fixture_count"] == 0
