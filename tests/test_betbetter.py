"""Bet Better keyless benchmark shadow (SHADOW-01 T4) — offline contracts.

Role: benchmark / echo-test counterparty with ZERO voice credit. It never
enters consensus weights or price corroboration; these tests pin that the
capture is polite, cache-first, and provenance-complete.
"""
from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path

import pytest

from edgefactory.sources import betbetter as bb

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _localdata(tmp_path, monkeypatch):
    monkeypatch.setattr(bb, "LOCALDATA", tmp_path)
    yield tmp_path


def _payload():
    return json.loads((FIXTURES / "betbetter_brazil_serie_a.json").read_text())


def test_parse_picks_maps_rows_and_stores_attribution():
    rows = bb.parse_picks(_payload(), day="2026-10-02", slug="brazil-serie-a")
    # The ticker-shaped "SASAN@SPSAO" game string is skipped fail-closed.
    assert len(rows) == 2
    first = rows[0]
    assert (first["home"], first["away"]) == ("Bragantino-SP", "Cruzeiro")
    assert first["market"] == "Draw No Bet"
    assert first["selection"] == "Cruzeiro"
    assert first["probability"] == 52.9
    assert first["fair_odds"] == 2.64
    assert first["kickoff"] == "2026-10-13T00:00:00.0000000Z"
    assert "Bet Better" in first["attribution"]
    assert "CC BY 4.0" in first["licence"]


def test_capture_day_is_ok_and_persists_provenance(monkeypatch, tmp_path):
    payload = _payload()

    def fake_get(url, timeout=30):
        return 200, payload, {}

    monkeypatch.setattr(bb, "get_json", fake_get)
    rows, stats = bb.capture_day("2026-10-02")
    assert stats["status"] == "ok"
    assert stats["requests"] == len(bb.LEAGUE_SLUGS)
    assert stats["bb_scored"] == 2 * len(bb.LEAGUE_SLUGS)
    path = bb.persist_shadow("2026-10-02", rows, stats, localdata=tmp_path)
    ledger = json.loads(path.read_text())
    assert ledger["provenance"]["licence"].startswith("CC BY 4.0")
    assert "betbetter.world" in ledger["provenance"]["attribution"]
    assert ledger["provenance"]["docs"] == "https://betbetter.world/api/"
    assert "benchmark-shadow" in ledger["role"]


def test_capture_day_is_cache_first_never_refetching_a_held_date(monkeypatch, tmp_path):
    payload = _payload()

    def fake_get(url, timeout=30):
        return 200, payload, {}

    monkeypatch.setattr(bb, "get_json", fake_get)
    first_rows, first_stats = bb.capture_day("2026-10-02")
    bb.persist_shadow("2026-10-02", first_rows, first_stats, localdata=tmp_path)

    calls = []

    def no_get(url, timeout=30):
        calls.append(url)
        raise AssertionError("cache-first contract violated: refetch of a held date")

    monkeypatch.setattr(bb, "get_json", no_get)
    rows, stats = bb.capture_day("2026-10-02")
    assert stats["status"] == "cache_only"
    assert stats["requests"] == 0
    assert rows == first_rows
    assert calls == []


def test_429_then_abort_classifies_blocked_and_stays_retryable(monkeypatch):
    calls = []

    def fail(url, timeout=30):
        calls.append(url)
        raise urllib.error.HTTPError(url, 429, "Too Many Requests", {}, io.BytesIO(b""))

    monkeypatch.setattr(bb, "get_json", fail)
    rows, stats = bb.capture_day("2026-10-02")
    assert rows == []
    assert stats["status"] == "blocked"
    assert "429" in stats["blocker"]
    assert stats["status"] in bb.RETRYABLE_ZERO_ROW_STATUSES
    assert len(calls) == 1


def test_off_switch_disables_without_requests(monkeypatch):
    def fail(url, timeout=30):
        raise AssertionError("disabled source must not fetch")

    monkeypatch.setattr(bb, "get_json", fail)
    monkeypatch.setattr(bb, "_enabled", lambda: False)
    rows, stats = bb.capture_day("2026-10-02")
    assert rows == []
    assert stats["status"] == "disabled"


def test_budget_cap_skips_remaining_leagues(monkeypatch):
    payload = _payload()
    monkeypatch.setattr(bb, "MAX_CALLS_PER_RUN", 2)

    def fake_get(url, timeout=30):
        return 200, payload, {}

    monkeypatch.setattr(bb, "get_json", fake_get)
    rows, stats = bb.capture_day("2026-10-02")
    assert stats["requests"] == 2
    assert any("budget" in str(err) for err in stats["errors"])
    assert stats["status"] == "ok"
    assert stats["bb_scored"] == 4


def test_dedupe_existing_committed_rows_win():
    payload = _payload()
    rows = bb.parse_picks(payload, day="2026-10-02", slug="brazil-serie-a")
    committed = [dict(rows[0], probability=99.9, captured_at="2026-10-02T06:00:00+00:00")]
    merged = bb.merge_with_committed(rows, committed)
    keys = [bb.dedupe_key(row) for row in merged]
    assert len(keys) == len(set(keys))
    # The committed row (earlier capture, different probability) survives.
    assert any(row.get("probability") == 99.9 for row in merged)
    assert len(merged) == 2


def test_diagnostics_never_leak_secrets(monkeypatch):
    payload = _payload()
    monkeypatch.setattr(bb, "get_json", lambda url, timeout=30: (200, payload, {}))
    bb.capture_day("2026-10-02")
    diag = bb.diagnostics()
    assert diag["status"] == "ok"
    assert diag["budget"] == bb.MAX_CALLS_PER_RUN
    assert "key" not in json.dumps(diag).lower()
