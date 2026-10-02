"""PR #21 BetExplorer politeness/thermal-state contracts."""
from __future__ import annotations

import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.sources import betexplorer_odds as be  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_be(tmp_path, monkeypatch):
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "CACHE_FRESHNESS_H", 24.0)
    be.reset_fetch_count()
    yield
    be.reset_fetch_count()


def _http_429(retry_after: str | None = None):
    headers = {"Retry-After": retry_after} if retry_after is not None else {}
    return urllib.error.HTTPError(
        "https://www.betexplorer.com/example", 429, "rate limited", headers,
        io.BytesIO(b""),
    )


def test_first_429_honors_retry_after_and_uses_30_second_floor(monkeypatch):
    calls = []
    sleeps = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"ok"

    def urlopen(_request, timeout=20):
        calls.append(timeout)
        if len(calls) == 1:
            raise _http_429("31")
        return Response()

    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(be, "_throttle", lambda: None)
    monkeypatch.setattr(be.time, "sleep", lambda seconds: sleeps.append(seconds))

    assert be._fetch("https://www.betexplorer.com/example") == "ok"
    assert len(calls) == 2
    assert sleeps == [31.0]
    assert be.run_stats() == {"be_429": 1, "be_cooling_down": False, "be_cached": 0}


def test_second_429_cools_run_and_makes_no_third_request(monkeypatch):
    calls = []

    def urlopen(*_args, **_kwargs):
        calls.append(1)
        raise _http_429()

    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(be, "_throttle", lambda: None)
    monkeypatch.setattr(be.time, "sleep", lambda _seconds: None)

    with pytest.raises(be.BetExplorerCoolingDown):
        be._fetch("https://www.betexplorer.com/example", retries=5)
    assert len(calls) == 2
    assert be.run_stats()["be_429"] == 2
    assert be.run_stats()["be_cooling_down"] is True

    with pytest.raises(be.BetExplorerCoolingDown):
        be._fetch("https://www.betexplorer.com/another", retries=1)
    assert len(calls) == 2, "cooling-down is run scoped: no further request"


def test_same_day_fixture_cache_dedupes_requests_and_survives_run_reset(monkeypatch):
    pick = {"date": "2026-10-02", "home": "Alpha FC", "away": "Beta United"}
    match = {
        "date": "2026-10-02", "kickoff": "18:00", "country": "X",
        "league": "Test", "home": "Alpha FC", "away": "Beta United",
        "match_url": "https://www.betexplorer.com/m/abc/", "event_id": "abc",
    }
    match_calls = []
    odds_calls = []

    def matches(day):
        match_calls.append(day)
        return [match] if day == "2026-10-02" else []

    def odds(url, event_id):
        odds_calls.append((url, event_id))
        return {"odd1": 1.80, "oddx": 3.60, "odd2": 4.20}

    monkeypatch.setattr(be, "fetch_day_matches", matches)
    monkeypatch.setattr(be, "fetch_match_odds", odds)

    first = be.betexplorer_odds_rows_for_pick(pick, "2026-10-02")
    second = be.betexplorer_odds_rows_for_pick(pick, "2026-10-02")
    assert len(first) == 3 and second == first
    assert len(odds_calls) == 1
    assert len(match_calls) == 2  # adjacent-day search stops when target matches
    assert be.run_stats()["be_cached"] == 1

    cache = Path(be.LOCALDATA) / "betexplorer_odds_cache_2026-10-02.json"
    payload = json.loads(cache.read_text())
    assert payload["fixtures"]

    # A new run has no in-memory state, but the fresh same-day persisted cache
    # prevents another request and supplies the exact same rows.
    be.reset_fetch_count()
    monkeypatch.setattr(be, "fetch_day_matches", lambda _day: (_ for _ in ()).throw(AssertionError("network")))
    assert be.betexplorer_odds_rows_for_pick(pick, "2026-10-02") == first
    assert be.run_stats()["be_cached"] == 1
