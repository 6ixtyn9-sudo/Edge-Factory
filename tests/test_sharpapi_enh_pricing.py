"""SharpAPI shadow ledger -> enhancement price index (over/under totals only)."""
import json

import pytest

from edgefactory.enh_pricing import (ENH_BOARD_FLAG, SHARPAPI_SOURCE,
                                     load_prices_index)
from edgefactory.util import norm_team

DAY = "2026-10-13"
HOME, AWAY = "USM Alger", "JS Saoura"


def _row(**over):
    base = {
        "source": SHARPAPI_SOURCE, "date": DAY, "home": HOME, "away": AWAY,
        "kickoff": f"{DAY}T18:00:00+00:00", "market": "ou_2.5",
        "selection": "over", "line": 2.5, "odds": 1.90,
        "bookmaker": "Pinnacle-like", "book": "Pinnacle-like",
        "captured_at": f"{DAY}T10:00:00+00:00", "odds_kind": "bookmaker",
        "named_bookmaker": True,
    }
    base.update(over)
    return base


def _write(root, rows, day=DAY):
    root.mkdir(parents=True, exist_ok=True)
    (root / f"sharpapi_odds_shadow_{day}.json").write_text(
        json.dumps({"schema": 1, "source": SHARPAPI_SOURCE, "date": day,
                    "rows": rows}))


def _slot(idx, market="ou_2.5", sel="over", home=HOME, away=AWAY):
    return idx["pairs"].get((norm_team(home), norm_team(away)), {}).get((market, sel))


def test_flag_off_prices_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv(ENH_BOARD_FLAG, raising=False)
    _write(tmp_path / "localdata", [_row()])
    assert _slot(load_prices_index(tmp_path, DAY)) is None


def test_flag_on_prices_over_under_totals(tmp_path, monkeypatch):
    monkeypatch.setenv(ENH_BOARD_FLAG, "1")
    _write(tmp_path / "localdata", [_row(), _row(selection="under", odds=1.95)])
    idx = load_prices_index(tmp_path, DAY)
    price, book, at, source = _slot(idx)
    assert (price, source) == (1.90, SHARPAPI_SOURCE)
    assert _slot(idx, sel="under")[0] == 1.95


def test_rejects_wrong_market_selection_source_and_date(tmp_path, monkeypatch):
    monkeypatch.setenv(ENH_BOARD_FLAG, "1")
    _write(tmp_path / "localdata", [
        _row(market="1x2", selection="home"),
        _row(market="moneyline", selection="home"),
        _row(source="oddspapi"),
        _row(date="2026-10-12"),
        _row(selection="draw"),
    ])
    idx = load_prices_index(tmp_path, DAY)
    assert _slot(idx) is None
    assert _slot(idx, market="1x2", sel="home") is None


def test_rejects_in_play_and_stale_rows(tmp_path, monkeypatch):
    monkeypatch.setenv(ENH_BOARD_FLAG, "1")
    _write(tmp_path / "localdata", [
        _row(captured_at=f"{DAY}T19:00:00+00:00"),        # after kickoff
        _row(captured_at="2026-10-08T10:00:00+00:00"),    # >72h before kickoff
    ])
    assert _slot(load_prices_index(tmp_path, DAY)) is None


@pytest.mark.parametrize("odds", ["nan", "inf", "0", "1.0", None, "junk"])
def test_hostile_odds_rejected(tmp_path, monkeypatch, odds):
    monkeypatch.setenv(ENH_BOARD_FLAG, "1")
    _write(tmp_path / "localdata", [_row(odds=odds)])
    assert _slot(load_prices_index(tmp_path, DAY)) is None


def test_missing_or_corrupt_ledger_fails_soft(tmp_path, monkeypatch):
    monkeypatch.setenv(ENH_BOARD_FLAG, "1")
    assert _slot(load_prices_index(tmp_path, DAY)) is None
    d = tmp_path / "localdata"
    d.mkdir()
    (d / f"sharpapi_odds_shadow_{DAY}.json").write_text("{not json")
    assert _slot(load_prices_index(tmp_path, DAY)) is None
