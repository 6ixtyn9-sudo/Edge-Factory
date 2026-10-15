"""Pinnacle ledger reuse must not republish yesterday's prices as today's.

2026-10-15: capture_day was cache-first per date. Once any row was stored under
a card date it returned those rows as ``cache_only`` and never fetched again,
whatever their capture stamps said. The 15 Oct card therefore priced from a
13 Oct capture. These tests pin the freshness rule and the cache decision.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.picks_today as pt
from edgefactory.sources import pinnapi_odds as pa

DAY = "2026-10-15"
FIXTURE = Path(__file__).parent / "fixtures" / "pinnapi_prematch_documented.json"


def _row(captured_at, **extra):
    out = {"source": "pinnapi_odds", "date": DAY, "home": "AZ Alkmaar",
           "away": "Hapoel Beer Sheva", "market": "1x2", "selection": "home",
           "odds": 1.2933, "captured_at": captured_at}
    out.update(extra)
    return out


# --- the freshness rule ----------------------------------------------------

def test_capture_from_the_previous_evening_is_current_for_the_card_day():
    assert pa.ledger_is_current([_row("2026-10-14T10:00:00+00:00")], DAY)


def test_capture_from_two_days_before_is_not_current():
    assert not pa.ledger_is_current([_row("2026-10-13T22:20:27+00:00")], DAY)


def test_one_stale_row_makes_the_whole_ledger_stale():
    rows = [_row("2026-10-15T04:00:00+00:00"), _row("2026-10-13T22:20:27+00:00")]
    assert not pa.ledger_is_current(rows, DAY)


def test_empty_or_undated_ledger_is_not_current():
    assert not pa.ledger_is_current([], DAY)
    assert not pa.ledger_is_current([_row(None)], DAY)
    assert not pa.ledger_is_current([_row("not-a-time")], DAY)


def test_bad_card_day_is_not_current():
    assert not pa.ledger_is_current([_row("2026-10-15T04:00:00+00:00")], "bogus")


def test_bound_matches_the_pricing_gate():
    """Two copies of one rule must not drift apart."""
    assert pa.LEDGER_MAX_AGE_HOURS == pt.MAX_PRICE_AGE_HOURS


# --- the cache decision in capture_day ------------------------------------

@pytest.fixture
def capture_env(monkeypatch, tmp_path):
    monkeypatch.setattr(pa, "_api_key", lambda: "test-key")
    calls = {"fetch": 0}
    payload = json.loads(FIXTURE.read_text())

    def fake_fetch(**_kwargs):
        calls["fetch"] += 1
        return 200, payload, {}, "test"

    monkeypatch.setattr(pa, "fetch_markets", fake_fetch)
    return calls, tmp_path


def test_stale_ledger_triggers_a_refetch_not_a_cache_hit(monkeypatch, capture_env):
    calls, tmp_path = capture_env
    stale = [_row("2026-10-13T22:20:27+00:00")]
    monkeypatch.setattr(pa, "_load_ledger_rows", lambda day, localdata=None: stale)
    _rows, stats = pa.capture_day(DAY, localdata=tmp_path)
    assert calls["fetch"] == 1
    assert stats["status"] != "cache_only"
    assert stats["stale_ledger_rows"] == 1


def test_current_ledger_is_still_reused_without_a_fetch(monkeypatch, capture_env):
    calls, tmp_path = capture_env
    current = [_row("2026-10-14T10:00:00+00:00")]
    monkeypatch.setattr(pa, "_load_ledger_rows", lambda day, localdata=None: current)
    rows, stats = pa.capture_day(DAY, localdata=tmp_path)
    assert calls["fetch"] == 0
    assert stats["status"] == "cache_only"
    assert rows == current


def test_refetched_rows_carry_their_own_fresh_stamps(monkeypatch, capture_env):
    """A refetch must not re-adopt the stale rows it replaced."""
    calls, tmp_path = capture_env
    stale = [_row("2026-10-13T22:20:27+00:00", odds=4.0)]
    monkeypatch.setattr(pa, "_load_ledger_rows", lambda day, localdata=None: stale)
    rows, _stats = pa.capture_day(DAY, localdata=tmp_path)
    assert calls["fetch"] == 1
    assert rows, "documented fixture must yield rows"
    assert all(str(r["captured_at"]).startswith("2026-") for r in rows)
    assert not any(r.get("captured_at") == "2026-10-13T22:20:27+00:00" for r in rows)
    assert not any(r.get("odds") == 4.0 for r in rows)
