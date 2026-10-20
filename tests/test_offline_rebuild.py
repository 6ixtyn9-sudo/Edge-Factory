import json
import sys
from pathlib import Path

import pytest
import scripts.picks_today as picks
import scripts.auto_tickets_grade as grade


def test_offline_build_refuses_legacy_route_before_any_capture(monkeypatch):
    monkeypatch.setenv('EDGE_FACTORY_OFFLINE_REBUILD', '1')
    monkeypatch.setattr(sys, 'argv', ['picks_today.py', '--date', '2026-10-20'])
    monkeypatch.setattr(picks, 'load_post_forebet_registry', lambda: None)
    monkeypatch.setattr(picks, 'load_thresholds', lambda: pytest.fail('legacy route'))
    with pytest.raises(SystemExit, match='no legacy fallback'):
        picks.main()


def test_offline_shadow_and_live_price_helpers_make_no_capture(monkeypatch):
    monkeypatch.setenv('EDGE_FACTORY_OFFLINE_REBUILD', '1')
    monkeypatch.setenv('EDGE_FACTORY_CANDIDATE_ONLY', '0')
    monkeypatch.setattr(picks, '_read_cached_bzzoiro_odds', lambda day: [])
    monkeypatch.setattr(picks, '_fetch_live_bzzoiro_odds', lambda *a, **k: pytest.fail('live price call'))
    assert picks._capture_shadow_candidates('2026-10-20')['betminer']['status'] == 'cache_only'
    stats = {}
    picks.bzzoiro_odds_bundle('2026-10-20', live=True, stats=stats)
    assert stats['live_rows'] == 0


def test_grade_no_settle_is_readonly_finance(tmp_path, monkeypatch):
    st = grade.at.fresh_state()
    monkeypatch.setattr(grade.at, 'load_state', lambda lane: st)
    monkeypatch.setattr(grade.at, 'settle_open_slips', lambda *a, **k: pytest.fail('settlement forbidden'))
    monkeypatch.setattr(grade, 'LOCALDATA', tmp_path)
    before = json.dumps(st, sort_keys=True)
    assert grade.main(['--lane', 'enh', '--no-settle']) == 0
    assert json.dumps(st, sort_keys=True) == before
    assert (tmp_path / 'autobets_enh_tickets_performance.json').exists()
