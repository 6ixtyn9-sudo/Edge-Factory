"""Operator confirmed none placed: withdraw only this date, never bank/history."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml

import scripts.auto_tickets as at

DAY = '2026-10-20'
OLD = b'ENHANCEMENT TICKETS\nFROZEN AT 10:41 - FINAL\n'
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def setup(tmp_path, monkeypatch):
    local = tmp_path / 'localdata'
    local.mkdir()
    monkeypatch.setattr(at, 'LOCALDATA', local)
    monkeypatch.setattr(at, 'ENHANCEMENT_LANE', at.Lane(local / 'enhancement_tickets_state.json',
                                                     'autobets_enh_tickets', 'ENH', at.STAKE_FRAC))
    receipt = dict(schema=1, action='reset_unplaced_enhancement', lane='enh', date=DAY,
                   approved_at='2026-10-20T10:00:00Z', confirmed_none_placed=True,
                   withdrawn_ticket_sha256=hashlib.sha256(OLD).hexdigest())
    path = local / f'autobets_enh_tickets_{DAY}_reset.json'
    path.write_text(json.dumps(receipt))
    slip = local / f'autobets_enh_tickets_{DAY}.txt'
    slip.write_bytes(OLD)
    marker = local / f'autobets_enh_tickets_{DAY}.frozen'
    marker.write_text('legacy freeze')
    state = dict(bank=137., base_pct=100., cycle_base=125.,
                 history=[dict(date='2026-10-19', returned_pct=12.)], events=[{'keep': True}],
                 open_slips=[dict(date=DAY, accas=[{'stake_pct': 12.5}], staked_pct=12.5),
                             dict(date='2026-10-19', accas=[], staked_pct=1.)],
                 frozen_by_date={DAY: {'frozen_at': '2026-10-20T10:41:00+02:00'},
                                 '2026-10-19': {'frozen_at': '2026-10-19T10:00:00Z'}},
                 superseded_by_date={DAY: {'result': 'NO BET'}, '2026-10-19': {'keep': True}})
    at.save_state(state, at.ENHANCEMENT_LANE)
    return local, path, receipt, state


def test_reset_removes_only_unplaced_target_and_keeps_audit_and_bank(setup):
    local, _, _, original = setup
    st = at.load_state(at.ENHANCEMENT_LANE)
    for field in ('bank', 'base_pct', 'cycle_base', 'history', 'events'):
        assert st[field] == original[field]
    assert st['open_slips'] == original['open_slips'][1:]
    assert DAY not in st['frozen_by_date'] and DAY not in st['superseded_by_date']
    assert st['frozen_by_date']['2026-10-19'] == original['frozen_by_date']['2026-10-19']
    record = st['unplaced_enhancement_resets'][DAY]
    assert record['removed_open_slips'] == original['open_slips'][:1]
    assert record['previous_freeze'] == original['frozen_by_date'][DAY]
    assert not (local / f'autobets_enh_tickets_{DAY}.txt').exists()
    assert not (local / f'autobets_enh_tickets_{DAY}.frozen').exists()
    assert at.load_state(at.ENHANCEMENT_LANE) == st
    assert json.loads(at.ENHANCEMENT_LANE.state_file.read_text()) == st


def test_stale_cache_reapplication_and_new_replacement_are_both_safe(setup):
    local, _, _, old = setup
    at.load_state(at.ENHANCEMENT_LANE)
    # Restore the old cache again: receipt, not cache order, remains authoritative.
    at.save_state(old, at.ENHANCEMENT_LANE)
    (local / f'autobets_enh_tickets_{DAY}.txt').write_bytes(OLD)
    reset = at.load_state(at.ENHANCEMENT_LANE)
    assert all(s['date'] != DAY for s in reset['open_slips'])
    # A valid later rebuild is not deleted on the next load.
    reset['open_slips'].append(dict(date=DAY, accas=['replacement']))
    reset['frozen_by_date'][DAY] = {'frozen_at': '2026-10-20T10:01:00Z'}
    at.save_state(reset, at.ENHANCEMENT_LANE)
    active = local / f'autobets_enh_tickets_{DAY}.txt'
    active.write_text('replacement')
    assert at.load_state(at.ENHANCEMENT_LANE) == reset
    # Even a newer cache without our acknowledgement retains a later freeze.
    reset.pop('unplaced_enhancement_resets')
    at.save_state(reset, at.ENHANCEMENT_LANE)
    assert at.load_state(at.ENHANCEMENT_LANE) == reset
    assert active.read_text() == 'replacement'


def test_main_lane_is_never_touched(setup, monkeypatch):
    local, _, _, original = setup
    main = at.Lane(local / 'auto_tickets_state.json', 'auto_tickets', 'MAIN', at.STAKE_FRAC)
    monkeypatch.setattr(at, 'MAIN_LANE', main)
    monkeypatch.setattr(at, 'STATE_FILE', main.state_file)
    at.save_state(original, main)
    before = main.state_file.read_bytes()
    assert at.load_state(main) == original
    assert main.state_file.read_bytes() == before
    assert (local / f'autobets_enh_tickets_{DAY}.txt').exists()


@pytest.mark.parametrize('change', [{'confirmed_none_placed': False}, {'confirmed_none_placed': 'true'},
    {'lane': 'main'}, {'schema': 2}, {'action': 'reset_bank'}, {'date': '2026-10-21'},
    {'approved_at': '2026-10-20T10:00:00'}, {'withdrawn_ticket_sha256': 'bad'}])
def test_malformed_or_unapproved_receipt_fails_before_mutating(setup, change):
    local, path, receipt, _ = setup
    path.write_text(json.dumps({**receipt, **change}))
    before = at.ENHANCEMENT_LANE.state_file.read_bytes()
    with pytest.raises((ValueError, KeyError, TypeError)):
        at.load_state(at.ENHANCEMENT_LANE)
    assert at.ENHANCEMENT_LANE.state_file.read_bytes() == before
    assert (local / f'autobets_enh_tickets_{DAY}.txt').read_bytes() == OLD


def test_settled_or_unknown_replacement_is_not_erased(setup):
    local, _, _, original = setup
    original['history'].append({'date': DAY, 'returned_pct': 50.})
    at.save_state(original, at.ENHANCEMENT_LANE)
    before = at.ENHANCEMENT_LANE.state_file.read_bytes()
    with pytest.raises(ValueError, match='settled history'):
        at.load_state(at.ENHANCEMENT_LANE)
    assert at.ENHANCEMENT_LANE.state_file.read_bytes() == before
    original['history'].pop()
    at.save_state(original, at.ENHANCEMENT_LANE)
    (local / f'autobets_enh_tickets_{DAY}.txt').write_text('unknown replacement')
    with pytest.raises(ValueError, match='differs'):
        at.load_state(at.ENHANCEMENT_LANE)


def test_no_cached_state_does_not_invent_a_bank_or_performance_history(setup):
    local, _, _, _ = setup
    at.ENHANCEMENT_LANE.state_file.unlink()
    assert at.load_state(at.ENHANCEMENT_LANE) == {}
    assert not at.ENHANCEMENT_LANE.state_file.exists()
    assert not (local / f'autobets_enh_tickets_{DAY}.txt').exists()


def test_housekeeping_cli_does_not_capture_settle_build_or_load_results(setup, monkeypatch):
    monkeypatch.setenv(at.ENH_BOARD_FLAG, '1')
    monkeypatch.setattr(sys, 'argv', ['auto_tickets.py', '--enhancements', '--apply-unplaced-resets'])
    def forbidden(*args, **kwargs):
        pytest.fail('housekeeping called a settlement/build/results path')
    for name in ('settle_open_slips', 'cmd_enhancement', 'load_settled'):
        monkeypatch.setattr(at, name, forbidden)
    assert at.main() == 0
    st = json.loads(at.ENHANCEMENT_LANE.state_file.read_text())
    assert all(row['date'] != DAY for row in st['open_slips'])
    assert st['bank'] == 137.


def test_reset_receipt_is_stageable():
    result = subprocess.run(['git', 'check-ignore', '-q',
        'localdata/autobets_enh_tickets_2099-01-01_reset.json'], cwd=ROOT)
    assert result.returncode == 1


@pytest.fixture
def rebuild_clock(monkeypatch):
    from datetime import datetime

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 20, 13, tzinfo=tz)

    monkeypatch.setattr(at, 'datetime', Clock)
    monkeypatch.setenv('EDGE_FACTORY_ENH_BOARD', '1')
    return SimpleNamespace(date=DAY, force=False, rebuild_unplaced=True)


def test_rebuild_zero_contracts_publishes_no_bet_not_old_slate(setup, rebuild_clock, monkeypatch):
    local, _, _, _ = setup
    st = at.load_state(at.ENHANCEMENT_LANE)
    (local / 'edges_consensus.json').write_text(json.dumps({'edges': []}))
    (local / 'picks_today.json').write_text('[{"rule":"retired Forebet"}]')
    before = at.ENHANCEMENT_LANE.state_file.read_bytes()
    monkeypatch.setattr(at.subprocess, 'run', lambda *a, **k: pytest.fail('no capture/build on zero contracts'))
    monkeypatch.setattr(at, 'settle_open_slips', lambda *a, **k: pytest.fail('must not settle'))
    assert at.cmd_rebuild_unplaced_enhancement(rebuild_clock, st) == 0
    artifact = (local / f'autobets_enh_tickets_{DAY}.txt').read_text()
    assert 'NO BET' in artifact and 'zero active validated post-Forebet' in artifact
    assert 'FROZEN AT ' not in artifact and 'ACCA #' not in artifact
    assert at.ENHANCEMENT_LANE.state_file.read_bytes() == before


def test_rebuild_without_current_bank_never_initializes_bank(setup, rebuild_clock):
    local, _, _, _ = setup
    at.load_state(at.ENHANCEMENT_LANE)
    at.ENHANCEMENT_LANE.state_file.unlink()
    assert at.cmd_rebuild_unplaced_enhancement(rebuild_clock, {}) == 0
    assert not at.ENHANCEMENT_LANE.state_file.exists()
    assert 'bank state unavailable' in (local / f'autobets_enh_tickets_{DAY}.txt').read_text()


def test_rebuild_reprices_fresh_all_market_slate_and_persists_no_plan(setup, rebuild_clock, monkeypatch):
    import edgefactory.prediction_history as history
    import edgefactory.enh_registry as registry
    import edgefactory.enh_team_floors as team

    local, _, _, _ = setup
    st = at.load_state(at.ENHANCEMENT_LANE)
    before = at.ENHANCEMENT_LANE.state_file.read_bytes()
    (local / 'edges_consensus.json').write_text(json.dumps({
        'operating_contract': 'post_forebet_v1',
        'edges': [{'contract_schema': 'post_forebet_v1', 'status': 'certified'}]}))
    (local / "warehouse.duckdb").touch()  # build stub below owns its contents
    fresh = [{'market': x, 'date': DAY} for x in ('1x2', 'ou25', 'btts')]
    checks, calls = [], []
    monkeypatch.setattr(history, 'check', lambda root: checks.append(root))

    def build(argv, **kwargs):
        calls.append(argv)
        assert argv[-2:] == ['--date', DAY]
        assert kwargs['check'] is True
        assert kwargs['env']['EDGE_FACTORY_OFFLINE_REBUILD'] == '1'
        assert kwargs['env']['EDGE_FACTORY_CANDIDATE_ONLY'] == '0'
        (local / 'picks_today.json').write_text(json.dumps(fresh))

    def legs(slate, **kwargs):
        assert slate == fresh  # all competing markets, not old card/O2.5-only
        return []

    monkeypatch.setattr(at.subprocess, 'run', build)
    monkeypatch.setattr(at, 'enhancement_legs', legs)
    monkeypatch.setattr(at, 'settle_open_slips', lambda *a, **k: pytest.fail('must not settle'))
    monkeypatch.setattr(at, 'load_settled_scores', lambda: {})
    monkeypatch.setattr(registry, 'derive_floors_for_day', lambda *a: {})
    monkeypatch.setattr(team, 'team_under_floors', lambda *a: {})
    assert at.cmd_rebuild_unplaced_enhancement(rebuild_clock, st) == 0
    assert len(calls) == len(checks) == 1
    assert 'NO BET' in (local / f'autobets_enh_tickets_{DAY}.txt').read_text()
    assert at.ENHANCEMENT_LANE.state_file.read_bytes() == before


def test_rebuild_needs_approved_today_and_never_unfreezes_newer_card(setup, rebuild_clock, monkeypatch):
    local, path, _, _ = setup
    st = at.load_state(at.ENHANCEMENT_LANE)
    path.unlink()
    with pytest.raises(ValueError, match='approved none-placed'):
        at.cmd_rebuild_unplaced_enhancement(rebuild_clock, st)
    rebuild_clock.date = '2026-10-19'
    with pytest.raises(ValueError, match="today"):
        at.cmd_rebuild_unplaced_enhancement(rebuild_clock, st)
    rebuild_clock.date = DAY
    path.write_text('{}')  # call uses state already validated/applied by load_state
    st['frozen_by_date'][DAY] = {'frozen_at': '2026-10-20T11:00:00Z'}
    artifact = local / f'autobets_enh_tickets_{DAY}.txt'
    artifact.write_text('NEW REPLACEMENT\nFROZEN AT 13:00 — FINAL')
    monkeypatch.setattr(at.subprocess, 'run', lambda *a, **k: pytest.fail('new frozen card preserved'))
    assert at.cmd_rebuild_unplaced_enhancement(rebuild_clock, st) == 0
    assert artifact.read_text() == 'NEW REPLACEMENT\nFROZEN AT 13:00 — FINAL'


def test_missing_warehouse_is_explicit_no_bet_without_erasing_main_slate(setup, rebuild_clock, monkeypatch):
    local, _, _, _ = setup
    st = at.load_state(at.ENHANCEMENT_LANE)
    (local / 'edges_consensus.json').write_text(json.dumps({
        'operating_contract': 'post_forebet_v1',
        'edges': [{'contract_schema': 'post_forebet_v1', 'status': 'certified'}]}))
    board = local / 'picks_today.json'
    board.write_text('[{"main":"keep"}]')
    before = at.ENHANCEMENT_LANE.state_file.read_bytes()
    monkeypatch.setattr(at.subprocess, 'run', lambda *a, **k: pytest.fail('must not erase shared slate'))
    assert at.cmd_rebuild_unplaced_enhancement(rebuild_clock, st) == 0
    assert 'NO BET' in (local / f'autobets_enh_tickets_{DAY}.txt').read_text()
    assert 'warehouse unavailable' in (local / f'autobets_enh_tickets_{DAY}.txt').read_text()
    assert board.read_text() == '[{"main":"keep"}]'
    assert at.ENHANCEMENT_LANE.state_file.read_bytes() == before
