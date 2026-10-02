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
    assert "never a price donor" in ledger["role"]
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
