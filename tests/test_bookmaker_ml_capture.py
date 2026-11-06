"""Existing bookmaker-price collection guards. Offline only; retired ML is not scheduled."""

import json
from datetime import UTC, datetime, timedelta

import pytest

import scripts.capture_betexplorer as capture
from edgefactory.sources import betexplorer_odds as be
from scripts import daily

DAY = "2026-11-02"
NOW = datetime(2026, 11, 2, 4, 36, tzinfo=UTC)
FREEZE = datetime(2026, 11, 2, 7, tzinfo=UTC)
OLD = NOW - timedelta(hours=6, minutes=20)


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)

    monkeypatch.setattr(be, "datetime", Clock)
    be.reset_fetch_count()
    # All network must be explicitly replaced by each test.
    def forbidden(*args, **kwargs):
        raise AssertionError("no live provider calls in regressions")

    monkeypatch.setattr(be, "_fetch", forbidden)
    yield
    be.reset_fetch_count()


def pick(**changes):
    row = {"date": DAY, "home": "Alpha United", "away": "Bravo City", "market": "btts", "pick": "yes",
           "kickoff_utc": f"{DAY}T17:00:00+00:00", "avg_p": 75,
           "statistical_profile": {"ml_model": {"schema": "enh_score_logit_v2", "n": 60}}}
    return dict(row, **changes)


def cache(row, *, stamp=OLD, rows=None):
    quote = dict(row, market="1x2", selection="home", odds=2.0,
                 kickoff=row["kickoff_utc"], captured_at=stamp.isoformat())
    be._write_fixture_cache(row, DAY, [quote] if rows is None else rows, detail=True)
    return be._fixture_cache_entry(row, DAY)


def due(row, *, now=NOW, freeze=FREEZE):
    return be.ml_price_refresh_needed(row, DAY, freeze_at=freeze, now=now)


def test_model_totals_and_btts_reach_same_fixture_collector_once(tmp_path):
    rows = [pick(), pick(market="ou_2.5"), pick(market="1x2"),
            pick(home="Other United", statistical_profile={}),
            pick(home="Future United", date="2026-11-03")]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    assert len(capture._candidate_rows(DAY)) == 1
    selected = capture._candidate_rows(DAY, ml_precutoff=True)
    assert len(selected) == 1 and selected[0]["home"] == "Alpha United"


@pytest.mark.parametrize("kickoff", [None, DAY + "T17:00:00", DAY + "T01:00:00+00:00",
                                    (FREEZE + timedelta(minutes=29)).isoformat()])
def test_ml_only_collection_does_not_spend_on_unusable_kickoffs(tmp_path, kickoff):
    (tmp_path / "picks_today.json").write_text(json.dumps([pick(kickoff_utc=kickoff)]))
    assert capture._candidate_rows(DAY, ml_precutoff=True) == []


def test_main_parent_cannot_hide_model_bound_alternative_for_same_fixture(tmp_path):
    rows = [pick(market="1x2", avg_p=99, statistical_profile={}), pick(avg_p=65)]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    selected = capture._candidate_rows(DAY, ml_precutoff=True)
    assert len(selected) == 1 and selected[0]["market"] == "btts"
    assert capture._candidate_rows(DAY)[0]["market"] == "1x2"


@pytest.mark.parametrize("stamp", [OLD, None, NOW + timedelta(minutes=1)])
def test_quote_clock_not_cache_write_clock_controls_refresh(stamp):
    row = pick()
    entry = cache(row)
    entry["rows"][0]["captured_at"] = stamp.isoformat() if stamp else None
    be._store_fixture_cache_entry(row, DAY, entry)
    assert due(row)


@pytest.mark.parametrize("case", ["fresh", "empty", "poisoned", "wrong_date", "naive_kickoff",
                                  "no_kickoff", "close", "late", "early", "naive_now",
                                  "wrong_freeze", "attempted"])
def test_refresh_does_not_bypass_collection_guards(case):
    row = pick()
    entry = cache(row)
    now, freeze = NOW, FREEZE
    if case == "fresh":
        entry["rows"][0]["captured_at"] = NOW.isoformat()
    elif case == "empty":
        entry["rows"] = []
    elif case == "poisoned":
        entry["rows"][0]["home"] = "Unrelated Club"
    elif case == "wrong_date":
        entry["rows"][0]["date"] = "2026-11-01"
    elif case == "naive_kickoff":
        row["kickoff_utc"] = DAY + "T17:00:00"
    elif case == "no_kickoff":
        row.pop("kickoff_utc")
    elif case == "close":
        row["kickoff_utc"] = (FREEZE + timedelta(minutes=29)).isoformat()
    elif case == "late":
        now = FREEZE
    elif case == "early":
        now = FREEZE - timedelta(hours=6, seconds=1)
    elif case == "naive_now":
        now = NOW.replace(tzinfo=None)
    elif case == "wrong_freeze":
        freeze = FREEZE + timedelta(minutes=1)
    elif case == "attempted":
        entry["ml_refresh_attempted_at"] = NOW.isoformat()
    be._store_fixture_cache_entry(pick(), DAY, entry)
    assert not due(row, now=now, freeze=freeze)


@pytest.mark.parametrize("result", ["empty", "exception"])
def test_failed_refresh_keeps_exact_old_clocks_and_is_not_repeated(monkeypatch, result):
    row = pick()
    before = cache(row)
    calls = []

    def fetch(*args, **kwargs):
        calls.append(kwargs)
        # A failed live capture normally writes an empty cache answer.
        be._fixture_cache[be._fixture_cache_key(row, DAY)] = []
        be._write_fixture_cache(row, DAY, [])
        if result == "exception":
            raise OSError("failed transport")
        return []

    monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick", fetch)
    if result == "exception":
        with pytest.raises(OSError):
            be.refresh_ml_prices_for_pick(row, DAY, freeze_at=FREEZE, now=NOW)
    else:
        assert be.refresh_ml_prices_for_pick(row, DAY, freeze_at=FREEZE, now=NOW) == before["rows"]
    after = be._fixture_cache_entry(row, DAY)
    assert after == dict(before, ml_refresh_attempted_at=NOW.isoformat())
    assert calls == [{"norm_team_fn": None, "refresh_prices": True}]
    be.reset_fetch_count()  # another process/run must not repeat the attempt
    assert not due(row)
    be._write_fixture_cache(row, DAY, before["rows"], detail=True)
    assert not due(row)  # ordinary enrichment must not erase the attempt


@pytest.mark.parametrize("guard", ["cooldown", "fixture_budget", "request_budget", "write_failure"])
def test_no_refresh_when_budget_cooldown_or_durable_attempt_write_blocks(monkeypatch, guard):
    row = pick()
    before = cache(row)
    if guard == "cooldown":
        monkeypatch.setattr(be, "_be_cooling_down", True)
    elif guard == "fixture_budget":
        monkeypatch.setattr(be, "_fetch_count", be._MAX_FETCHES_PER_RUN)
    elif guard == "request_budget":
        monkeypatch.setattr(be, "_request_count", be._MAX_REQUESTS_PER_RUN)
    else:
        monkeypatch.setattr(be, "_store_fixture_cache_entry", lambda *args: False)
    assert be.refresh_ml_prices_for_pick(row, DAY, freeze_at=FREEZE, now=NOW) == before["rows"]
    assert be._fixture_cache_entry(row, DAY) == before


@pytest.mark.parametrize("active", [False, True])
def test_refresh_uses_existing_fixture_budget_and_never_relabels_old_quotes(tmp_path, monkeypatch, active):
    row = pick(market="1x2")
    before = cache(row)
    (tmp_path / "picks_today.json").write_text(json.dumps([row]))
    receipt = capture.capture(DAY, max_fixtures=0, ml_precutoff=active, now=NOW)
    assert receipt["network_attempted"] == receipt["ml_refresh_attempted"] == 0
    assert receipt["rows"] == 1
    assert be._fixture_cache_entry(row, DAY) == before
    assert receipt["deferred_fixtures"] == int(active)


@pytest.mark.parametrize("now", [FREEZE, FREEZE - timedelta(hours=7)])
def test_cli_flag_outside_window_keeps_default_candidate_scope(tmp_path, now):
    (tmp_path / "picks_today.json").write_text(json.dumps([pick()]))
    receipt = capture.capture(DAY, ml_precutoff=True, now=now)
    assert not receipt["ml_precutoff_active"]
    assert receipt["candidate_fixtures"] == receipt["network_attempted"] == 0


def test_daily_capture_never_requests_retired_ml_refresh(monkeypatch):
    commands = []
    monkeypatch.setattr(daily, "run_soft", lambda command, label: commands.append(command))
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    daily.capture_betexplorer_snapshot(DAY, "candidate_price_snapshot")
    daily.capture_betexplorer_snapshot(DAY, "end_of_run")
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "0")
    daily.capture_betexplorer_snapshot(DAY, "candidate_price_snapshot")
    assert len(commands) == 3
    assert all("--ml-precutoff" not in command for command in commands)
