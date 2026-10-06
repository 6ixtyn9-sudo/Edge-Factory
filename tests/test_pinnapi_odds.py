"""pinnapi Pinnacle price shadow (SHADOW-01 T3) — offline contracts.

Named-book price shadow only: never a vote, corroboration default-off, and
the freshness gate (same-day rows only, else ABSTAIN) is pinned here so a
future corroborator cannot quietly use stale prices. All transport is
monkeypatched; CI never fetches.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from edgefactory.sources import pinnapi_odds as pa

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _localdata(tmp_path, monkeypatch):
    monkeypatch.setattr(pa, "LOCALDATA", tmp_path)
    yield tmp_path


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setenv("PINNAPI_KEY", "test-pinnapi-key")
    yield


def _payload():
    return json.loads((FIXTURES / "pinnapi_soccer_prematch.json").read_text())


def test_parse_snapshot_normalizes_markets_and_filters_junk_prices():
    rows, schema_match = pa.parse_snapshot(_payload(), day="2026-10-03")
    assert schema_match is True
    # 6 mapped markets from event 1; event 2 keeps moneyline->1x2 rows.
    # Unmappable corner-market selections are dropped by the shared
    # canonicalizer; the 0.95 price (<= 1.0) is also dropped.
    assert len(rows) == 8
    eerste = [r for r in rows if r["home"] == "Helmond Sport"]
    assert {(r["market"], r["selection"]) for r in eerste} >= {
        ("1x2", "home"), ("1x2", "draw"), ("1x2", "away"),
        ("ou_2.5", "over"), ("ou_2.5", "under"),
    }
    # The shared canonical vocabulary deliberately has no spread market;
    # that unmappable provider row is counted and withheld.
    assert all(r["book"] == "Pinnacle" and r["bookmaker"] == "Pinnacle" for r in rows)
    assert all(r["odds"] > 1.0 for r in rows)
    # moneyline alias + x->draw normalization
    brondby = [r for r in rows if r["home"] == "Brøndby IF"]
    assert ("1x2", "draw") in {(r["market"], r["selection"]) for r in brondby}
    # Unknown market names are not silently re-mapped into the canonical
    # price board.
    assert not any(r.get("market") == "corner_kick_race" for r in brondby)
    assert {r["league"] for r in eerste} == {"Eerste Divisie"}


def test_parse_snapshot_unrecognized_shape_fails_closed():
    rows, schema_match = pa.parse_snapshot({"unexpected": {"nested": True}}, day="2026-10-03")
    assert rows == []
    assert schema_match is False


def test_capture_without_key_is_inert_not_run(monkeypatch):
    monkeypatch.delenv("PINNAPI_KEY", raising=False)

    def fail(url, timeout=30, auth="header"):
        raise AssertionError("keyless run must not fetch")

    monkeypatch.setattr(pa, "get_json", fail)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "not_run"
    assert "PINNAPI_KEY not set" in stats["blocker"]


def test_capture_ok_counts_and_is_cache_first(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, timeout=30, auth="header"):
        calls.append(url)
        return 200, _payload(), {"x-ratelimit-remaining": "77"}

    monkeypatch.setattr(pa, "get_json", fake_get)
    rows, stats = pa.capture_day("2026-10-03")
    assert stats["status"] == "ok"
    assert stats["pa_raw"] == 2       # distinct fixtures
    assert stats["pa_matched"] == 8  # canonical price rows
    assert stats["schema_match"] is True
    path = pa.persist_shadow("2026-10-03", rows, stats, localdata=tmp_path)
    ledger = json.loads(path.read_text())
    assert "never a vote" in ledger["role"]
    assert ledger["provenance"]["unofficial_feed"].startswith("Pinnacle public API closed")
    # Cache-first: a held date is never refetched.
    rows2, stats2 = pa.capture_day("2026-10-03")
    assert stats2["status"] == "cache_only"
    assert stats2["requests"] == 0
    assert rows2 == rows
    assert len(calls) == 1


def test_schema_mismatch_is_unavailable_with_raw_sample_retained(monkeypatch):
    def fake_get(url, timeout=30, auth="header"):
        return 200, {"totally": "different"}, {}

    monkeypatch.setattr(pa, "get_json", fake_get)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "unavailable"
    assert stats["schema_match"] is False
    assert stats["status"] in pa.RETRYABLE_ZERO_ROW_STATUSES
    assert "probe_pinnapi" in stats["blocker"]
    assert stats["sample_event"] == {"top_keys": ["totally"]}


def test_auth_403_is_retryable_zero(monkeypatch):
    def fake_get(url, timeout=30, auth="header"):
        return 403, {"message": "Forbidden"}, {}

    monkeypatch.setattr(pa, "get_json", fake_get)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "auth"
    assert stats["quota_hint"] == "auth_or_quota"
    assert stats["status"] in pa.RETRYABLE_ZERO_ROW_STATUSES


def test_same_day_rows_gate_stale_prices_abstain():
    fresh = [{"home": "A", "away": "B", "captured_at": "2026-10-03T08:00:00+00:00", "odds": 1.9}]
    stale = [{"home": "C", "away": "D", "captured_at": "2026-10-01T08:00:00+00:00", "odds": 2.1}]
    rows = pa.same_day_rows(fresh + stale, "2026-10-03")
    # The stale row must ABSTAIN - a future corroborator may not use it.
    assert [r["home"] for r in rows] == ["A"]
    assert pa.same_day_rows(fresh + stale, "2026-10-05") == []


def test_budget_cap_is_classified_quota(monkeypatch):
    monkeypatch.setattr(pa, "MAX_CALLS_PER_RUN", 0)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "quota"
    assert stats["quota_hint"] == "budget_reached"


def test_get_json_refuses_requests_that_carry_no_credential():
    """The guard moved with the contract; its intent did not.

    It used to assert ``key=`` was in the URL. The key now travels in the
    ``x-portal-apikey`` header, so that spelling no longer tests anything -
    but the invariant is unchanged: a request that carries the key by
    NEITHER mechanism is refused before it leaves the process.
    """
    with pytest.raises(pa.UpstreamBlocked, match="unauthenticated"):
        pa.get_json("https://pinnapi.com/kit/v1/markets?sport_id=1&event_type=prematch",
                    auth="query")


def test_header_auth_is_accepted_by_the_guard(monkeypatch):
    """A key-less URL is fine when the header carries the credential."""
    sent = {}

    def fake_urlopen(request, timeout=30):
        sent["headers"] = dict(request.headers)
        sent["url"] = request.full_url
        raise AssertionError("stop before the network")

    monkeypatch.setattr(pa.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(pa.UpstreamBlocked) as excinfo:
        pa.get_json(pa.markets_url())
    assert "unauthenticated" not in str(excinfo.value)
    # urllib title-cases header names; compare case-insensitively.
    headers = {k.lower(): v for k, v in sent["headers"].items()}
    assert headers["x-portal-apikey"] == "test-pinnapi-key"
    assert "key=" not in sent["url"]


def test_dedupe_existing_committed_rows_win():
    rows, _ = pa.parse_snapshot(_payload(), day="2026-10-03")
    committed = [dict(rows[0], odds=99.9)]
    merged = pa.merge_with_committed(rows, committed)
    assert len(merged) == len(rows)
    assert any(row.get("odds") == 99.9 for row in merged)


def test_diagnostics_never_leak_the_key(monkeypatch):
    def fake_get(url, timeout=30, auth="header"):
        return 200, _payload(), {}

    monkeypatch.setattr(pa, "get_json", fake_get)
    pa.capture_day("2026-10-03")
    dumped = json.dumps(pa.diagnostics())
    assert "test-pinnapi-key" not in dumped
    # The default (header) request URL carries no credential at all.
    assert pa.markets_url().endswith("sport_id=1&event_type=prematch")
    assert "key=" not in pa.markets_url()
    # Only the 401 fallback puts the key in the query string.
    assert pa.markets_url(auth="query").endswith(
        "sport_id=1&event_type=prematch&key=test-pinnapi-key")
    # Header sanitization drops auth material.
    sanitized = pa._sanitize_headers({"X-RateLimit-Remaining": "4", "Authorization": "Bearer x"})
    assert "Authorization" not in sanitized


# --- dict-shaped markets block (WO-1) -------------------------------------
# The provider sends the markets block either as a list of entries that each
# name their own market, or as a dict keyed by market name. Reading only the
# list form discarded every event of the second shape while still reporting
# schema_match=True, so the source looked healthy and delivered nothing.


def _event(markets):
    return {"events": [{"id": "e1", "home": "Arsenal", "away": "Chelsea",
                        "start_at": "2026-10-07T18:00:00Z",
                        "league": {"name": "Premier League"},
                        "markets": markets}]}


def test_dict_shaped_markets_block_yields_rows():
    payload = _event({"moneyline": [
        {"selection": "home", "price": 2.10},
        {"selection": "draw", "price": 3.40},
        {"selection": "away", "price": 3.20},
    ]})
    rows, schema = pa.parse_snapshot(payload, day="2026-10-07")
    assert schema is True
    assert len(rows) == 3
    assert {r["selection"] for r in rows} == {"home", "draw", "away"}
    assert {r["market"] for r in rows} == {"1x2"}
    assert sorted(r["odds"] for r in rows) == [2.10, 3.20, 3.40]


def test_dict_key_supplies_the_market_name():
    """The market name lives in the key; without it every row is marketless."""
    payload = _event({"moneyline": [{"selection": "home", "price": 2.10}]})
    rows, _ = pa.parse_snapshot(payload, day="2026-10-07")
    assert rows and rows[0]["market"] == "1x2"


def test_entry_market_is_not_overwritten_by_its_group_key():
    payload = _event({"ignored_group": [
        {"market": "moneyline", "selection": "home", "price": 2.10}]})
    rows, _ = pa.parse_snapshot(payload, day="2026-10-07")
    assert rows and rows[0]["raw_market"] == "moneyline"


def test_unwrapped_single_selection_is_read():
    payload = _event({"moneyline": {"selection": "home", "price": 2.10}})
    rows, _ = pa.parse_snapshot(payload, day="2026-10-07")
    assert len(rows) == 1


def test_list_shaped_markets_block_still_works():
    """The original shape must keep parsing; this is a widening, not a swap."""
    payload = _event([{"market": "moneyline", "selection": "home", "price": 2.10}])
    rows, schema = pa.parse_snapshot(payload, day="2026-10-07")
    assert schema is True and len(rows) == 1


# --- every discard is counted ---------------------------------------------


def test_unusable_markets_container_is_counted():
    payload = _event("not-a-container")
    rows, _ = pa.parse_snapshot(payload, day="2026-10-07")
    reasons = pa.canonicalization_drop_reasons()
    assert rows == []
    assert reasons, "an event was discarded with no reason recorded"
    assert any("markets_container" in k for k in reasons)
    assert "str" in " ".join(reasons), "the reason should name what arrived"


def test_price_under_an_unexpected_key_is_counted():
    payload = _event([{"market": "moneyline", "selection": "home",
                       "decimal": 2.10}])
    rows, _ = pa.parse_snapshot(payload, day="2026-10-07")
    assert rows == []
    assert pa.canonicalization_drop_reasons().get("price_unreadable") == 1


def test_implausible_price_is_counted_separately():
    payload = _event([{"market": "moneyline", "selection": "home", "price": 1.0}])
    rows, _ = pa.parse_snapshot(payload, day="2026-10-07")
    assert rows == []
    assert pa.canonicalization_drop_reasons().get(
        "price_not_above_one") == 1


def test_drop_reasons_reset_between_parses():
    pa.parse_snapshot(_event("not-a-container"), day="2026-10-07")
    assert pa.canonicalization_drop_reasons()
    pa.parse_snapshot(
        _event([{"market": "moneyline", "selection": "home", "price": 2.10}]),
        day="2026-10-07")
    assert pa.canonicalization_drop_reasons() == {}


def test_a_good_row_survives_alongside_a_dropped_one():
    payload = _event([{"market": "moneyline", "selection": "home", "decimal": 2.1},
                      {"market": "moneyline", "selection": "away", "price": 3.2}])
    rows, _ = pa.parse_snapshot(payload, day="2026-10-07")
    assert len(rows) == 1 and rows[0]["selection"] == "away"
    assert pa.canonicalization_drop_reasons().get("price_unreadable") == 1


# --- REST request contract (WO-8) -----------------------------------------
# Two things were wrong at once: the adapter asked for the wrong sport and
# authenticated the wrong way. Soccer is sport_id=1, and REST auth is the
# x-portal-apikey header; the key= query form survives only as a 401
# fallback. Everything below is proved against mocked responses - this
# sandbox has no network and no live call was ever made.


class _Recorder:
    """Stands in for get_json, recording how each attempt was built."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, timeout=30, auth="header"):
        self.calls.append({"url": url, "auth": auth,
                           "headers": pa.request_headers(auth)})
        return self.responses[min(len(self.calls) - 1, len(self.responses) - 1)]


def test_soccer_is_sport_id_one():
    assert pa.SPORT_ID == 1
    assert pa.sport_id() == 1
    assert "sport_id=1" in pa.markets_url()


def test_sport_id_is_env_overridable(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_PINNAPI_SPORT_ID", "9")
    assert pa.sport_id() == 9
    assert "sport_id=9" in pa.markets_url()
    # A junk override falls back to the constant rather than sending garbage.
    monkeypatch.setenv("EDGE_FACTORY_PINNAPI_SPORT_ID", "soccer")
    assert pa.sport_id() == 1


def test_request_carries_the_portal_api_key_header():
    headers = pa.request_headers()
    assert headers[pa.AUTH_HEADER] == "test-pinnapi-key"
    assert pa.AUTH_HEADER == "x-portal-apikey"
    # The fallback form carries it in the URL instead, never in both.
    assert pa.AUTH_HEADER not in pa.request_headers(auth="query")


def test_header_auth_is_tried_first_and_recorded(monkeypatch):
    recorder = _Recorder((200, _payload(), {}))
    monkeypatch.setattr(pa, "get_json", recorder)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows
    assert [c["auth"] for c in recorder.calls] == ["header"]
    assert recorder.calls[0]["headers"][pa.AUTH_HEADER] == "test-pinnapi-key"
    assert "key=" not in recorder.calls[0]["url"]
    assert "sport_id=1" in recorder.calls[0]["url"]
    assert "event_type=prematch" in recorder.calls[0]["url"]
    assert stats["auth_mechanism"] == "header"
    assert stats["auth_attempts"] == [{"auth": "header", "status": 200}]
    assert stats["sport_id"] == 1 and stats["event_type"] == "prematch"


def test_401_on_header_auth_falls_back_to_the_query_form(monkeypatch):
    recorder = _Recorder((401, {"message": "unauthorized"}, {}),
                         (200, _payload(), {}))
    monkeypatch.setattr(pa, "get_json", recorder)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows, "the fallback answer must still be parsed"
    assert [c["auth"] for c in recorder.calls] == ["header", "query"]
    assert "key=test-pinnapi-key" in recorder.calls[1]["url"]
    assert stats["status"] == "ok"
    assert stats["auth_mechanism"] == "query"
    assert stats["auth_attempts"] == [{"auth": "header", "status": 401},
                                      {"auth": "query", "status": 200}]
    assert stats["requests"] == 2


def test_401_raised_as_upstream_blocked_also_falls_back(monkeypatch):
    """A real 401 arrives as an HTTPError, not as a returned status."""
    calls = []

    def fake_get(url, timeout=30, auth="header"):
        calls.append(auth)
        if auth == "header":
            raise pa.UpstreamBlocked("pinnapi: HTTP 401 Unauthorized; ")
        return 200, _payload(), {}

    monkeypatch.setattr(pa, "get_json", fake_get)
    rows, stats = pa.capture_day("2026-10-03")
    assert calls == ["header", "query"]
    assert rows and stats["auth_mechanism"] == "query"
    assert stats["auth_attempts"] == [{"auth": "header", "status": 401},
                                      {"auth": "query", "status": 200}]


def test_both_mechanisms_rejected_is_a_retryable_auth_zero(monkeypatch):
    recorder = _Recorder((401, {"message": "unauthorized"}, {}))
    monkeypatch.setattr(pa, "get_json", recorder)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "auth"
    assert stats["status"] in pa.RETRYABLE_ZERO_ROW_STATUSES
    assert stats["auth_mechanism"] is None, "nothing succeeded; claim nothing"
    assert [a["auth"] for a in stats["auth_attempts"]] == ["header", "query"]


def test_non_401_failure_does_not_spend_a_second_call(monkeypatch):
    """Only 401 is an auth-mechanism question. 500 is not; do not re-ask."""
    recorder = _Recorder((500, {"message": "boom"}, {}))
    monkeypatch.setattr(pa, "get_json", recorder)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert len(recorder.calls) == 1
    assert stats["status"] == "unavailable"


def test_zero_row_prematch_records_the_payload_shape(monkeypatch):
    """A 200 with nothing usable must describe what arrived.

    Recording the shape is the whole deliverable in that case: the next
    step is an operator decision on an observed payload, not a parser
    invented for one nobody has seen.
    """
    payload = {"events": [{"id": "e1", "home": "Arsenal", "away": "Chelsea",
                           "markets": {"corner_race": [
                               {"selection": "home", "price": 2.1}]}}]}

    def fake_get(url, timeout=30, auth="header"):
        return 200, payload, {}

    monkeypatch.setattr(pa, "get_json", fake_get)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "empty"
    shape = stats["response_shape"]
    assert shape["event_count"] == 1
    assert shape["events_key"] == "events"
    assert "home" in shape["event_keys"] and "markets" in shape["event_keys"]
    assert shape["markets_type"] == "dict"
    assert shape["market_group_keys"] == ["corner_race"]
    assert shape["market_entry_keys"] == ["price", "selection"] or set(
        shape["market_entry_keys"]) == {"selection", "price"}
    assert shape["drop_reasons"], "the reason rows vanished must be named"
    assert "zero usable rows" in stats["blocker"]


def test_empty_event_list_records_a_shape_too(monkeypatch):
    """An empty board is unrecognizable from an unrecognized board.

    It keeps the pre-existing fail-closed, retryable classification - the
    change here is only that the observed shape is written down.
    """
    def fake_get(url, timeout=30, auth="header"):
        return 200, {"events": [], "meta": {"page": 1}}, {}

    monkeypatch.setattr(pa, "get_json", fake_get)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == [] and stats["status"] == "unavailable"
    assert stats["status"] in pa.RETRYABLE_ZERO_ROW_STATUSES
    assert stats["response_shape"]["event_count"] == 0
    assert set(stats["response_shape"]["top_keys"]) == {"events", "meta"}


def test_the_key_never_reaches_diagnostics_or_the_ledger(monkeypatch, tmp_path):
    """Trap 2: moving the key into a header must not leak it elsewhere.

    _sanitize_headers covers RESPONSE headers; nothing we SEND may be
    recorded, so the stats are checked as a whole, including the ledger
    written to disk.
    """
    recorder = _Recorder((401, {"error": "bad key test-pinnapi-key"}, {}),
                         (200, _payload(), {}))
    monkeypatch.setattr(pa, "get_json", recorder)
    rows, stats = pa.capture_day("2026-10-03")
    path = pa.persist_shadow("2026-10-03", rows, stats, localdata=tmp_path)
    assert "test-pinnapi-key" not in json.dumps(pa.diagnostics())
    assert "test-pinnapi-key" not in json.dumps(stats)
    assert "test-pinnapi-key" not in path.read_text()
    assert "x-portal-apikey" in json.loads(path.read_text())["provenance"]["auth"]


def test_shadow_role_is_unchanged_by_the_contract_fix(tmp_path):
    """Parsing what the vendor sends is a bug fix, not a promotion."""
    rows, _ = pa.parse_snapshot(_payload(), day="2026-10-03")
    ledger = json.loads(pa.persist_shadow(
        "2026-10-03", rows, {"status": "ok"}, localdata=tmp_path).read_text())
    assert "never a vote" in ledger["role"]
    assert ledger["role"].startswith("price-shadow")
