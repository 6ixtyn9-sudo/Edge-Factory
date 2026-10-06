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
                 "SHARPAPI_BOOK", "SHARPAPI_MARKET", "SHARPAPI_DATE_PARAM"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("RAPIDAPI_KEY", "sharp-test-key")
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
    assert sa.odds_url("2026-10-03") == "https://sharpapi1.p.rapidapi.com/api/v1/odds?sport=soccer"


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
    assert url.startswith("https://sharpapi1.p.rapidapi.com/api/v1/odds?")
    assert "sport=basketball_nba" in url and "limit=5" in url
    assert "book=pinnacle" in url and "market=h2h" in url


def test_confirmed_date_parameter_is_honoured(monkeypatch):
    monkeypatch.setenv("SHARPAPI_DATE_PARAM", "gameDate")
    assert "gameDate=2026-10-03" in sa.odds_url("2026-10-03")


def test_endpoint_override_is_normalized(monkeypatch):
    monkeypatch.setenv("SHARPAPI_ENDPOINT", "api/v1/odds/live")
    assert sa.endpoint() == "/api/v1/odds/live"


def test_rapidapi_host_header_is_pinned(monkeypatch):
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
    assert captured["headers"]["X-rapidapi-host"] == "sharpapi1.p.rapidapi.com"
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
    monkeypatch.setenv("RAPIDAPI_KEY", "leak-me-not")

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
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    monkeypatch.setattr(
        sa, "get_json",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("keyless run must not fetch")))
    rows, stats = sa.capture_day("2026-10-03")
    assert rows == [] and stats["status"] == "not_run"
