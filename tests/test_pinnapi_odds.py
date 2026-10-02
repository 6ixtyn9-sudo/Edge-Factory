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
    # 6 mapped markets from event 1; event 2 keeps moneyline->1x2 rows and
    # the unknown corner market verbatim; the 0.95 price (<= 1.0) is dropped.
    assert len(rows) == 10
    eerste = [r for r in rows if r["home"] == "Helmond Sport"]
    assert {(r["market"], r["selection"]) for r in eerste} >= {
        ("1x2", "home"), ("1x2", "draw"), ("1x2", "away"),
        ("totals", "over"), ("totals", "under"), ("spreads", "away"),
    }
    assert all(r["book"] == "Pinnacle" and r["bookmaker"] == "Pinnacle" for r in rows)
    assert all(r["odds"] > 1.0 for r in rows)
    # moneyline alias + x->draw normalization
    brondby = [r for r in rows if r["home"] == "Brøndby IF"]
    assert ("1x2", "draw") in {(r["market"], r["selection"]) for r in brondby}
    # Unknown market names are kept verbatim, never silently re-mapped.
    assert any(r["market"] == "corner_kick_race" for r in brondby)
    assert {r["league"] for r in eerste} == {"Eerste Divisie"}


def test_parse_snapshot_unrecognized_shape_fails_closed():
    rows, schema_match = pa.parse_snapshot({"unexpected": {"nested": True}}, day="2026-10-03")
    assert rows == []
    assert schema_match is False


def test_capture_without_key_is_inert_not_run(monkeypatch):
    monkeypatch.delenv("PINNAPI_KEY", raising=False)

    def fail(url, timeout=30):
        raise AssertionError("keyless run must not fetch")

    monkeypatch.setattr(pa, "get_json", fail)
    rows, stats = pa.capture_day("2026-10-03")
    assert rows == []
    assert stats["status"] == "not_run"
    assert "PINNAPI_KEY not set" in stats["blocker"]


def test_capture_ok_counts_and_is_cache_first(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, timeout=30):
        calls.append(url)
        return 200, _payload(), {"x-ratelimit-remaining": "77"}

    monkeypatch.setattr(pa, "get_json", fake_get)
    rows, stats = pa.capture_day("2026-10-03")
    assert stats["status"] == "ok"
    assert stats["pa_raw"] == 2       # distinct fixtures
    assert stats["pa_matched"] == 10  # price rows
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
    def fake_get(url, timeout=30):
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
    def fake_get(url, timeout=30):
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


def test_get_json_refuses_unauthenticated_urls():
    with pytest.raises(pa.UpstreamBlocked, match="unauthenticated"):
        pa.get_json("https://pinnapi.com/kit/v1/markets?sport=soccer&mode=prematch")


def test_dedupe_existing_committed_rows_win():
    rows, _ = pa.parse_snapshot(_payload(), day="2026-10-03")
    committed = [dict(rows[0], odds=99.9)]
    merged = pa.merge_with_committed(rows, committed)
    assert len(merged) == len(rows)
    assert any(row.get("odds") == 99.9 for row in merged)


def test_diagnostics_never_leak_the_key(monkeypatch):
    def fake_get(url, timeout=30):
        return 200, _payload(), {}

    monkeypatch.setattr(pa, "get_json", fake_get)
    pa.capture_day("2026-10-03")
    dumped = json.dumps(pa.diagnostics())
    assert "test-pinnapi-key" not in dumped
    assert pa.markets_url().endswith("key=test-pinnapi-key")
    # Header sanitization drops auth material.
    sanitized = pa._sanitize_headers({"X-RateLimit-Remaining": "4", "Authorization": "Bearer x"})
    assert "Authorization" not in sanitized
