"""Capture-once-per-fixture inside the pre-kickoff window.

No provider calls are made in these tests: every network seam is stubbed.
"""
from __future__ import annotations

import urllib.error
from datetime import datetime, timedelta, timezone

import pytest

import scripts.capture_oddspapi as cap
from edgefactory import enh_pricing

START = datetime(2026, 10, 13, 19, 0, tzinfo=timezone.utc)
DAY = "2026-10-13"


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _fx(fid: str, start: datetime = START) -> dict:
    return {"fixtureId": fid, "participant1Name": "H" + fid,
            "participant2Name": "A" + fid, "startTime": _iso(start)}


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    monkeypatch.setattr(cap, "api_keys", lambda: ("k1",))
    monkeypatch.setattr(cap, "_load_slate_pairs", lambda day: {})
    monkeypatch.setattr(cap, "_append_rows", lambda rows, day: 0)
    monkeypatch.setattr(cap, "_persist_market_census",
                        lambda *a, **k: tmp_path / "census.json")
    monkeypatch.setattr(cap, "_persist_vocabulary_snapshot", lambda day, c: "vocab")
    state = {"board": [], "board_calls": 0, "odds": [], "markets_calls": 0,
             "fail_next": None}

    def fake_board(day):
        state["board_calls"] += 1
        return list(state["board"])

    def fake_odds(fid):
        if state["fail_next"] is not None:
            err, state["fail_next"] = state["fail_next"], None
            raise err
        state["odds"].append(fid)
        return {}

    def fake_markets():
        state["markets_calls"] += 1
        return {}

    monkeypatch.setattr(cap, "fetch_fixtures", fake_board)
    monkeypatch.setattr(cap, "fetch_odds", fake_odds)
    monkeypatch.setattr(cap, "load_market_type_map", fake_markets)
    monkeypatch.setattr(cap, "market_catalog", lambda: {})
    monkeypatch.setattr(cap, "market_catalog_entries", lambda: {})
    return state


def _run(now: datetime, max_fixtures: int = 20) -> dict:
    return cap.capture(DAY, max_fixtures=max_fixtures, now_utc=now)


def test_constants_split_oddspapi_from_sharpapi():
    assert enh_pricing.ODDSPAPI_MAX_AGE_H == 6
    assert enh_pricing.SHARPAPI_MAX_AGE_H == 72
    assert cap.CAPTURE_WINDOW_H == enh_pricing.ODDSPAPI_MAX_AGE_H


def test_no_calls_before_the_window(env):
    env["board"] = [_fx("f1")]
    receipt = _run(START - timedelta(hours=7))
    assert env["odds"] == []
    assert env["markets_calls"] == 0
    assert receipt["status"] == "nothing_pending"


def test_window_edges_are_six_hours_inclusive_to_kickoff(env):
    env["board"] = [_fx("f1")]
    _run(START - timedelta(hours=6))          # opens exactly 6h out
    assert env["odds"] == ["f1"]
    env["board"] = [_fx("f2")]
    _run(START)                               # at kickoff: closed
    assert env["odds"] == ["f1"]


def test_one_snapshot_per_fixture_across_runs(env):
    env["board"] = [_fx("f1")]
    _run(START - timedelta(hours=5))
    _run(START - timedelta(hours=4))
    _run(START - timedelta(hours=2))
    assert env["odds"] == ["f1"]


def test_no_calls_after_kickoff(env):
    env["board"] = [_fx("f1")]
    _run(START + timedelta(minutes=10))
    assert env["odds"] == []


def test_max_fixtures_cap_leaves_the_rest_for_the_next_run(env):
    env["board"] = [_fx("f1"), _fx("f2"), _fx("f3")]
    _run(START - timedelta(hours=5), max_fixtures=2)
    assert len(env["odds"]) == 2
    _run(START - timedelta(hours=4), max_fixtures=2)
    assert sorted(env["odds"]) == ["f1", "f2", "f3"]


def test_board_is_reused_until_it_is_six_hours_old(env):
    env["board"] = [_fx("f1")]
    _run(START - timedelta(hours=11))         # board read; fixture not due yet
    assert env["board_calls"] == 1
    _run(START - timedelta(hours=9))          # board still fresh
    assert env["board_calls"] == 1
    _run(START - timedelta(hours=5))          # board 6h old: re-read, now due
    assert env["board_calls"] == 2
    assert env["odds"] == ["f1"]


def test_quota_stops_the_pass_and_the_fixture_stays_pending(env):
    env["board"] = [_fx("f1")]
    env["fail_next"] = urllib.error.HTTPError(
        "https://api.oddspapi.io/v4/odds", 429, "Too Many Requests", None, None)
    receipt = _run(START - timedelta(hours=5))
    assert receipt["status"] == "quota"
    assert env["odds"] == []
    # Not marked captured, so the next run in the window tries it again.
    receipt = _run(START - timedelta(hours=4))
    assert env["odds"] == ["f1"]


def test_fixture_without_kickoff_time_is_ignored(env):
    env["board"] = [{"fixtureId": "f1", "participant1Name": "H", "participant2Name": "A"}]
    _run(START - timedelta(hours=5))
    assert env["odds"] == []


def test_no_keys_means_no_calls(env, monkeypatch):
    monkeypatch.setattr(cap, "api_keys", lambda: ())
    env["board"] = [_fx("f1")]
    _run(START - timedelta(hours=5))
    assert env["odds"] == []
    assert env["board_calls"] == 0


def test_a_capture_inside_the_window_is_fresh_for_enhancement_pricing():
    # The merge guard keeps rows captured in [kickoff - 6h, kickoff].
    iso = _iso(START - timedelta(hours=5))
    assert enh_pricing._fresh_row({"kickoff": _iso(START), "captured_at": iso},
                                  enh_pricing.ODDSPAPI_MAX_AGE_H)
    late = _iso(START + timedelta(minutes=1))
    assert not enh_pricing._fresh_row({"kickoff": _iso(START), "captured_at": late},
                                      enh_pricing.ODDSPAPI_MAX_AGE_H)
