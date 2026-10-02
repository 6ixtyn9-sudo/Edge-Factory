from __future__ import annotations

import copy
import json

import scripts.picks_today as pt


def test_sportytrader_flag_off_is_byte_identical(monkeypatch, tmp_path):
    pick = {
        "date": "2026-10-02", "home": "Alpha", "away": "Beta", "market": "1x2",
        "pick": "home", "odds": 1.50, "price_board": [], "bucket": "CLEAN",
    }
    before = json.dumps([pick], sort_keys=True, separators=(",", ":"))
    monkeypatch.delenv("SPORTYTRADER_CORROBORATOR", raising=False)
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    pt._apply_sportytrader_corroborator([pick], "2026-10-02")
    after = json.dumps([pick], sort_keys=True, separators=(",", ":"))
    assert after == before


def test_sportytrader_flag_on_only_adds_shadow_board(monkeypatch, tmp_path):
    (tmp_path / "sportytrader_odds_shadow_2026-10-02.json").write_text(json.dumps({"rows": [{
        "date": "2026-10-02", "home": "Alpha", "away": "Beta", "market": "1x2",
        "selection": "home", "odds": 1.55, "bookmaker": "Bet365", "captured_at": "now",
    }]}))
    pick = {
        "date": "2026-10-02", "home": "Alpha", "away": "Beta", "market": "1x2",
        "pick": "home", "odds": 1.50, "price_board": [],
    }
    monkeypatch.setenv("SPORTYTRADER_CORROBORATOR", "on")
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    added, _ = pt._apply_sportytrader_corroborator([pick], "2026-10-02")
    assert added == 1
    assert pick["price_board"][0]["source"] == "sportytrader_odds"
