"""A cached, priced BetExplorer fixture must still have its match detail retained.

Cache hits used to return before the match page was fetched, so a price cached
before the detail tabs existed never had its O/U tabs written to the day's detail
ledger. These tests pin the re-read: only for priced legacy entries (no detail
flag), at most once per run, never at the cost of the cached price, and never
for an entry a detail-tab visit already wrote (one visit per fixture per day).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest  # noqa: E402

from edgefactory.sources import betexplorer_odds as be  # noqa: E402

DAY = "2026-10-13"
PICK = {"home": "Germany W", "away": "Japan W", "date": DAY, "kickoff": "16:45"}
MATCHED = {
    "event_id": "E1",
    "match_url": "https://www.betexplorer.com/football/x/germany-japan/E1/",
    "kickoff": "16:45",
    "home": "Germany W",
    "away": "Japan W",
    "country": "World",
    "league": "Friendly",
}
ODDS = {"odd1": 1.74, "oddx": 3.6, "odd2": 3.9}


def _rows(price: float = 1.74) -> list[dict]:
    return [{
        "date": DAY, "kickoff": "16:45", "league": "World: Friendly",
        "home": "Germany W", "away": "Japan W", "market": "1x2",
        "selection": "home", "odds": price, "bookmaker": "betexplorer_best",
        "captured_at": "2026-10-13T05:00:00+00:00",
    }]


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "MARKET_TABS_ENABLED", True)
    monkeypatch.setattr(be, "_fixture_cache", {})
    monkeypatch.setattr(be, "_detail_attempted", set(), raising=False)
    monkeypatch.setattr(be, "_orientation_marker_clean_guard", lambda m, p: True)
    monkeypatch.setattr(be, "filter_rows_for_pick", lambda rows, p, d, **k: (list(rows), {}))
    monkeypatch.setattr(be, "fetch_day_matches", lambda d: [MATCHED])
    monkeypatch.setattr(be, "match_pick_to_betexplorer",
                        lambda p, ms, **k: dict(MATCHED, home=p["home"], away=p["away"]))
    calls = {"n": 0, "detail": True, "odds": ODDS}

    def fake_fetch(url, event_id):
        calls["n"] += 1
        if calls["detail"]:
            be.LAST_MATCH_DETAIL = {
                "captured_at": "2026-10-13T06:00:00+00:00",
                "page_param": "1",
                "markets": {},
                "page": {},
            }
        else:
            be.LAST_MATCH_DETAIL = None
        return calls["odds"]

    monkeypatch.setattr(be, "fetch_match_odds", fake_fetch)
    monkeypatch.setattr(be, "reset_fetch_count", be.reset_fetch_count)
    be.reset_fetch_count()
    return tmp_path, calls


def _seed_cache(rows, *, detail: bool = False):
    """Seed a same-day cache entry. detail=False is a legacy entry."""
    be._fixture_cache.clear()
    be._write_fixture_cache(PICK, DAY, rows, detail=detail)
    be._fixture_cache[be._fixture_cache_key(PICK, DAY)] = list(rows)


def _ledger_has_fixture() -> bool:
    path = be._match_detail_path(DAY)
    if not path.exists():
        return False
    payload = json.loads(path.read_text())
    return be._fixture_cache_key(PICK, DAY) in (payload.get("fixtures") or {})


def test_cached_priced_fixture_without_detail_is_reread(env):
    _, calls = env
    _seed_cache(_rows(1.70))

    rows = be.betexplorer_odds_rows_for_pick(PICK, DAY)

    assert calls["n"] == 1, "a priced cache hit with no retained detail must re-read the page"
    assert _ledger_has_fixture(), "the re-read must write the detail ledger entry"
    assert rows and rows[0]["odds"] == 1.74, "the fresh price replaces the cached one"


def test_cached_fixture_visited_under_detail_tabs_is_served_from_cache(env):
    _, calls = env
    _seed_cache(_rows(1.70), detail=True)

    rows = be.betexplorer_odds_rows_for_pick(PICK, DAY)

    assert calls["n"] == 0
    assert rows and rows[0]["odds"] == 1.70


def test_empty_cache_entry_is_not_reread(env):
    _, calls = env
    _seed_cache([])

    assert be.betexplorer_odds_rows_for_pick(PICK, DAY) == []
    assert calls["n"] == 0, "a refusal or a day with no odds has no detail to fetch"


def test_tabs_disabled_means_no_reread(env, monkeypatch):
    _, calls = env
    monkeypatch.setattr(be, "MARKET_TABS_ENABLED", False)
    _seed_cache(_rows(1.70))

    rows = be.betexplorer_odds_rows_for_pick(PICK, DAY)

    assert calls["n"] == 0
    assert rows and rows[0]["odds"] == 1.70


def test_failed_reread_keeps_the_cached_price(env):
    _, calls = env
    _seed_cache(_rows(1.70))
    calls["odds"] = None  # the live re-read returns nothing

    rows = be.betexplorer_odds_rows_for_pick(PICK, DAY)

    assert calls["n"] == 1
    assert rows and rows[0]["odds"] == 1.70, "a failed re-read must not drop the price"
    cached = be._read_fixture_cache(PICK, DAY)
    assert cached and cached[0]["odds"] == 1.70, "nor overwrite the cache with an empty entry"


def test_failed_reread_is_attempted_once_per_run(env):
    _, calls = env
    calls["odds"] = None  # every live re-read comes back empty
    _seed_cache(_rows(1.70))

    be.betexplorer_odds_rows_for_pick(PICK, DAY)
    be.betexplorer_odds_rows_for_pick(PICK, DAY)

    assert calls["n"] == 1, "a fixture whose re-read keeps failing is not re-requested in the run"


def test_visited_fixture_is_not_reread_across_runs(env):
    _, calls = env
    _seed_cache(_rows(1.70))
    be.betexplorer_odds_rows_for_pick(PICK, DAY)  # the one re-read, flags the entry
    assert calls["n"] == 1

    be.reset_fetch_count()  # a new run
    rows = be.betexplorer_odds_rows_for_pick(PICK, DAY)

    assert calls["n"] == 1, "a visit under the detail tabs is final for the day"
    assert rows and rows[0]["odds"] == 1.74


def test_rereads_do_not_spend_the_fixture_budget(env):
    """Re-reads must not use up the fixture budget that later cache reads depend on."""
    _, calls = env
    other = {"home": "Other FC", "away": "Team B", "date": DAY, "kickoff": "16:45"}
    _seed_cache(_rows(1.70))
    other_rows = [dict(row, home=other["home"], away=other["away"]) for row in _rows(1.70)]
    be._fixture_cache[be._fixture_cache_key(other, DAY)] = other_rows
    be._write_fixture_cache(other, DAY, other_rows)

    be.betexplorer_odds_rows_for_pick(PICK, DAY)
    be.betexplorer_odds_rows_for_pick(other, DAY)

    assert calls["n"] == 2, "both legacy fixtures are re-read"
    assert be._fetch_count == 0, "re-reads leave the fixture budget untouched"
