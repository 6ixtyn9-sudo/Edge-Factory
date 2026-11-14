"""Betminer voice shadow (SHADOW-01 T2) — offline contracts.

Zero voice credit until the echo test passes and the operator promotes.
Voice-only: the odds object carries no bookmaker identity, so Betminer is
never a price donor. All transport is monkeypatched; CI never fetches.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from edgefactory.sources import betminer as bm

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _localdata(tmp_path, monkeypatch):
    monkeypatch.setattr(bm, "LOCALDATA", tmp_path)
    yield tmp_path


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key-material")
    yield


def _payload():
    return json.loads((FIXTURES / "betminer_matches_2026-10-03.json").read_text())


def test_parse_matches_maps_vote_schema_and_keeps_provenance():
    rows = bm.parse_matches(_payload(), day="2026-10-03")
    assert len(rows) == 2
    epl, eerste = rows
    assert (epl["home"], epl["away"], epl["league"], epl["country"]) == (
        "Manchester United", "Liverpool", "Premier League", "England")
    assert epl["1x2_selection"] == "home"
    assert epl["1x2_probability"] == 45.0
    assert epl["btts_selection"] == "yes"
    assert epl["btts_probability"] == 68.0
    assert epl["ou_25_selection"] == "over"
    assert epl["ou_25_probability"] == 62.0
    assert epl["predicted_score"] == "2-1"
    # Composite double-chance probability is derived, not invented.
    assert eerste["1x2_selection"] == "x2"
    assert eerste["1x2_probability"] == 84.0  # draw 25 + away 59
    # Odds are retained as provenance ONLY (no bookmaker identity).
    assert eerste["odds_raw"]["away_win"] == "1.55"
    assert "bookmaker" not in json.dumps(eerste["odds_raw"]).lower()


def test_capture_without_key_is_inert_not_run(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)

    def fail(url, timeout=30):
        raise AssertionError("keyless run must not fetch")

    monkeypatch.setattr(bm, "get_json", fail)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "not_run"
    assert "RAPIDAPI_KEY not set" in stats["blocker"]
    assert stats["key_present"] is False


def test_capture_ok_persists_and_is_cache_first(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, timeout=30):
        calls.append(url)
        return 200, _payload(), {
            "x-ratelimit-requests-limit": "5",
            "x-ratelimit-requests-remaining": "3",
        }

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert stats["status"] == "ok"
    assert stats["bm_raw"] == 2 and stats["bm_scored"] == 2
    assert stats["requests"] == 1
    assert stats["quota_hint"] == "none_observed"
    assert stats["rate_limit_headers"]["x-ratelimit-requests-remaining"] == "3"
    path = bm.persist_shadow("2026-10-03", rows, stats, localdata=tmp_path)
    ledger = json.loads(path.read_text())
    assert ledger["source"] == "betminer"
    assert "never execution-eligible" in ledger["role"]
    assert ledger["provenance"]["docs"].startswith("https://betminer.co.uk")

    # Second capture the same date: cache-only, zero requests.
    rows2, stats2 = bm.capture_day("2026-10-03")
    assert stats2["status"] == "cache_only"
    assert stats2["requests"] == 0
    assert rows2 == rows
    assert len(calls) == 1


def test_quota_hint_flags_nearly_exhausted_budget(monkeypatch):
    def fake_get(url, timeout=30):
        return 200, _payload(), {"x-ratelimit-requests-remaining": "1"}

    monkeypatch.setattr(bm, "get_json", fake_get)
    _rows, stats = bm.capture_day("2026-10-03")
    assert stats["quota_hint"] == "nearly_exhausted"


def test_auth_403_is_retryable_zero_not_empty(monkeypatch):
    def fake_get(url, timeout=30):
        return 403, {"message": "Key is invalid"}, {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "auth"
    assert stats["quota_hint"] == "auth_or_quota"
    assert stats["status"] in bm.RETRYABLE_ZERO_ROW_STATUSES


def test_404_is_unavailable_fail_closed_never_empty(monkeypatch):
    def fake_get(url, timeout=30):
        return 404, None, {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "unavailable"
    assert stats["status"] in bm.RETRYABLE_ZERO_ROW_STATUSES


def test_success_false_payload_is_unavailable(monkeypatch):
    def fake_get(url, timeout=30):
        return 200, {"success": False, "error": {"code": "MATCH_NOT_FOUND", "message": "No match found"}}, {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "unavailable"
    assert "MATCH_NOT_FOUND" in stats["blocker"]


def test_repeated_429_trips_cooldown_and_budget_classification(monkeypatch):
    from edgefactory.sources.betminer import UpstreamBlocked

    def fake_get(url, timeout=30):
        # Mirror the real transport: a second 429 sets run-scoped cool-down
        # before raising (capture_day's reset_state() has already run).
        bm._COOLING_DOWN = True
        raise UpstreamBlocked("betminer: repeated HTTP 429; cooling down for the rest of this run")

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "cooldown"
    assert stats["quota_hint"] == "rate_limit_or_quota"
    assert stats["status"] in bm.RETRYABLE_ZERO_ROW_STATUSES
    # A first-429 (no cool-down) classifies as plain quota instead.
    bm.reset_state()

    def fake_get_once(url, timeout=30):
        raise UpstreamBlocked("betminer: HTTP 429 Too Many Requests; waited 30s")

    monkeypatch.setattr(bm, "get_json", fake_get_once)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "quota"
    assert stats["quota_hint"] == "rate_limit_or_quota"


def test_budget_cap_is_classified_quota(monkeypatch):
    from edgefactory.sources.betminer import UpstreamBlocked

    monkeypatch.setattr(bm, "get_json", lambda url, timeout=30: (_ for _ in ()).throw(
        UpstreamBlocked("betminer: per-run call budget 0 reached; no further calls this run")))
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "quota"
    assert stats["quota_hint"] == "budget_reached"


def test_hard_call_budget_blocks_get_json(monkeypatch):
    monkeypatch.setattr(bm, "MAX_CALLS_PER_RUN", 0)
    with pytest.raises(bm.UpstreamBlocked, match="budget"):
        bm.get_json(bm.matches_url("2026-10-03"))
    # And capture_day classifies that as a retryable quota day.
    rows, stats = bm.capture_day("2026-10-03")
    assert stats["status"] == "quota"
    assert stats["quota_hint"] == "budget_reached"


def test_zero_rows_after_retryable_failure_are_refetched_next_run(monkeypatch, tmp_path):
    """A failed day must NOT create a committed-rows ledger that would block
    the retry (zero-row days stay retryable)."""
    state = {"fail": True}

    def fake_get(url, timeout=30):
        if state["fail"]:
            return 403, {"message": "blocked"}, {}
        return 200, _payload(), {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == [] and stats["status"] == "auth"
    # picks_today persists the failure ledger for evidence...
    bm.persist_shadow("2026-10-03", rows, stats, localdata=tmp_path)
    # ...but a later run retries and succeeds (no committed rows held).
    state["fail"] = False
    rows2, stats2 = bm.capture_day("2026-10-03")
    assert stats2["status"] == "ok"
    assert len(rows2) == 2


def test_dedupe_existing_committed_rows_win():
    rows = bm.parse_matches(_payload(), day="2026-10-03")
    committed = [dict(rows[0], **{"1x2_probability": 99.9})]
    merged = bm.merge_with_committed(rows, committed)
    assert len(merged) == 2
    assert any(row.get("1x2_probability") == 99.9 for row in merged)


def test_settlement_coverage_uses_existing_warehouse_facts():
    rows = bm.parse_matches(_payload(), day="2026-10-03")
    settled = [
        {"date": "2026-10-03", "home": "Manchester United", "away": "Liverpool", "hs": 2, "gs": 1},
    ]
    coverage = bm.settlement_coverage(rows, settled)
    assert coverage["captured"] == 2
    assert coverage["settled"] == 1
    assert coverage["unmatched"] == 1
    assert coverage["mismatch"] is True
    assert coverage["settlement_source"] == "existing warehouse-score backfill"


def test_diagnostics_and_payloads_never_leak_the_key(monkeypatch):
    def fake_get(url, timeout=30):
        return 200, _payload(), {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    bm.capture_day("2026-10-03")
    diag = json.dumps(bm.diagnostics())
    assert "test-key-material" not in diag
    # Rate-limit header sanitization keeps only limit signals.
    sanitized = bm._sanitize_headers({"X-RateLimit-Remaining": "4", "Authorization": "Bearer x", "Retry-After": "9"})
    assert "Authorization" not in sanitized
    assert sanitized["X-RateLimit-Remaining"] == "4"


# --- current endpoint contract: /matches/{date} (V3 docs + captured sample) ----


def _value_bet_payload():
    return {
        "success": True,
        "value_bets": [
            {
                "home_team": "Ajax",
                "away_team": "PSV",
                "league": "Eredivisie",
                "kickoff": "2026-10-03T18:45:00Z",
                "market": "1x2",
                "selection": "2",
                "probability": 48,
                "odds": 2.35,
                "bookmaker": "Bet365",
                "value": 12.8,
                "published_at": "2026-10-03T08:00:00Z",
            },
            {
                "home_team": "Feyenoord",
                "away_team": "AZ",
                "market": "1x2",
                "selection": "1",
                "probability": 52,
                "odds": 1.95,
                "published_at": "2026-10-03T08:00:00Z",
            },
            {
                "home_team": "Twente",
                "away_team": "Utrecht",
                "market": "1x2",
                "selection": "X",
                "fair_odds": 3.40,
            },
        ],
    }


def test_capture_calls_the_documented_matches_endpoint_once(monkeypatch):
    seen = []

    def fake_get(url, timeout=30):
        seen.append(url)
        return 200, _payload(), {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert seen == ["https://betminer.p.rapidapi.com/matches/2026-10-03"]
    assert all("/value-bets/" not in url for url in seen)
    assert stats["status"] == "ok"
    assert stats["schema_shape"] == "match_objects"
    assert len(rows) == 2


def test_value_bet_rows_label_price_provenance_truthfully():
    rows, shaped = bm.parse_value_bets(_value_bet_payload(), day="2026-10-03")
    assert shaped
    booked, aggregate, fair = rows
    # A named book is the only thing that may be called a bookmaker price.
    assert (booked["odds"], booked["odds_kind"], booked["bookmaker"]) == (2.35, "bookmaker", "Bet365")
    assert booked["named_bookmaker"] is True
    assert booked["selection"] == "away"
    # No book name -> provider aggregate, never a named-book quote.
    assert (aggregate["odds_kind"], aggregate["bookmaker"]) == ("provider_average", None)
    assert aggregate["named_bookmaker"] is False
    # A model number is fair, not executable.
    assert (fair["odds"], fair["odds_kind"]) == (3.40, "fair")
    assert fair["selection"] == "draw"
    # Probabilities are normalized to a 0-1 scale, never invented.
    assert booked["probability"] == 0.48
    assert rows[0]["published_at"] == "2026-10-03T08:00:00Z"
    assert rows[0]["captured_at"]


def test_rapidapi_headers_are_sent_for_the_betminer_host(monkeypatch):
    captured = {}

    class _Response:
        status = 200
        headers: dict[str, str] = {}

        def read(self, _n=0):
            return b'{"value_bets": []}'

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.headers)
        return _Response()

    monkeypatch.setattr(bm.urllib.request, "urlopen", fake_urlopen)
    bm.reset_state()
    status, payload, _headers = bm.get_json(bm.capture_url("2026-10-03"))
    assert status == 200 and payload == {"value_bets": []}
    assert captured["headers"]["X-rapidapi-host"] == "betminer.p.rapidapi.com"
    assert captured["headers"]["X-rapidapi-key"] == "test-key-material"


def test_http_404_without_a_body_is_not_claimed_as_a_contract_failure(monkeypatch):
    """Superseded assertion. This used to assert the blanket label
    `http_404_endpoint_contract`, which asserted a *cause* ("our path is
    stale") the response never evidenced. A bodyless 404 is undiagnosed."""
    def fake_get(url, timeout=30):
        raise bm.UpstreamBlocked("betminer: HTTP 404 Not Found; ")

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "unavailable"
    assert stats["reason"] == "http_404_endpoint_contract_unconfirmed"
    assert stats["status"] in bm.RETRYABLE_ZERO_ROW_STATUSES


def test_http_404_with_a_routing_body_is_a_contract_failure(monkeypatch):
    def fake_get(url, timeout=30):
        raise bm.UpstreamBlocked(
            "betminer: HTTP 404 Not Found; "
            "{\"message\":\"Endpoint '/matches/2026-10-03' does not exist\"}")

    monkeypatch.setattr(bm, "get_json", fake_get)
    _, stats = bm.capture_day("2026-10-03")
    assert stats["reason"] == "http_404_endpoint_contract"


def test_http_404_with_a_subscription_body_points_at_billing(monkeypatch):
    def fake_get(url, timeout=30):
        raise bm.UpstreamBlocked(
            "betminer: HTTP 404 Not Found; "
            "{\"message\":\"You are not subscribed to this API.\"}")

    monkeypatch.setattr(bm, "get_json", fake_get)
    _, stats = bm.capture_day("2026-10-03")
    assert stats["reason"] == "http_404_not_subscribed"


def test_404_probe_receipt_is_write_once_for_the_day(monkeypatch, tmp_path):
    calls = []

    def first_probe(url, timeout=30):
        calls.append(url)
        return 404, None, {}

    monkeypatch.setattr(bm, "get_json", first_probe)
    rows, first = bm.capture_day("2026-10-03", localdata=tmp_path)
    assert rows == []
    assert first["probe_receipt"] is True
    receipt_path = tmp_path / "betminer_probe_2026-10-03.json"
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text())
    assert receipt["endpoint"].endswith("/matches/2026-10-03")
    assert receipt["http_status"] == 404
    assert "test-key-material" not in receipt_path.read_text()

    def should_not_probe(url, timeout=30):
        raise AssertionError("same-day probe receipt must short-circuit transport")

    monkeypatch.setattr(bm, "get_json", should_not_probe)
    rows2, second = bm.capture_day("2026-10-03", localdata=tmp_path)
    assert rows2 == []
    assert second["probe_receipt"] is True
    assert second["requests"] == 0
    assert len(calls) == 1


def test_valid_empty_day_is_not_a_schema_failure(monkeypatch):
    monkeypatch.setattr(bm, "get_json", lambda url, timeout=30: (200, {"value_bets": []}, {}))
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "empty"
    assert stats["schema_match"] is True
    assert stats["reason"] == "provider_empty_slate"


def test_unrecognized_payload_fails_closed_with_a_scrubbed_sample(monkeypatch):
    monkeypatch.setattr(bm, "get_json", lambda url, timeout=30: (200, {"surprise": 1}, {}))
    rows, stats = bm.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "unavailable"
    assert stats["reason"] == "schema_unrecognized"
    assert stats["schema_sample"] == {"top_keys": ["surprise"]}


def test_documented_match_object_fixture_parses():
    rows, shape = bm.parse_payload(_payload(), day="2026-10-03")
    assert shape == "match_objects"
    assert len(rows) == 2


def test_diagnostics_never_leak_the_api_key(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_KEY", "super-secret-key")
    monkeypatch.setattr(
        bm, "get_json",
        lambda url, timeout=30: (200, {"note": "key super-secret-key used"}, {}))
    bm.capture_day("2026-10-03")
    assert "super-secret-key" not in json.dumps(bm.diagnostics())
