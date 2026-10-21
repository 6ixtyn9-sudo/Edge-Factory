"""Settlement speed must not change winners, identity guards or bank history."""
from copy import deepcopy
from datetime import date, timedelta
import random
from types import SimpleNamespace

import pytest

import scripts.auto_tickets as at


@pytest.mark.parametrize('seed', range(6))
def test_date_index_preserves_full_scan_order_and_results(seed, monkeypatch):
    rng = random.Random(seed)
    day = date(2026, 10, 20)
    rows = [((str(day + timedelta(days=offset)), home, away), outcome)
            for offset in range(-6, 7)
            for home, away, outcome in [
                ('alphaunited', 'betacity', 'home'),
                ('alphaunitd', 'betacity', 'away'),
                ('otherclub', 'betacity', 'draw')]]
    rng.shuffle(rows)  # donor insertion order need not be date order
    plain = dict(rows)
    indexed = at._SettledOutcomes(plain, {}, {})
    days = {str(day + timedelta(days=n)) for n in range(-3, 4)}
    assert list(indexed.items_for_dates(days)) == [
        (key, value) for key, value in plain.items() if key[0] in days]
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {})
    for home in ('alphaunited', 'alphaunit', 'missing'):
        assert at._lookup_fallback(indexed, str(day), home, 'betacity') == (
            at._lookup_fallback(plain, str(day), home, 'betacity'))
    assert dict(indexed) == plain
    with pytest.raises(TypeError):
        indexed[(str(day), 'new', 'club')] = 'home'


def test_equal_fuzzy_scores_keep_original_donor_winner(monkeypatch):
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {})
    # Date-sorting would incorrectly change this tied winner to 'home'.
    plain = {('2026-10-21', 'alpha', 'beta'): 'away',
             ('2026-10-19', 'alpha', 'beta'): 'home'}
    indexed = at._SettledOutcomes(plain, {}, {})
    assert at._lookup_fallback(indexed, '2026-10-20', 'alpha', 'beta') == 'away'
    assert at._lookup_fallback(plain, '2026-10-20', 'alpha', 'beta') == 'away'


def test_fallback_does_not_traverse_out_of_window_history(monkeypatch):
    plain = {(f'2024-01-{i % 28 + 1:02}', f'oldhome{i}', 'oldaway'): 'home'
             for i in range(10_000)}
    plain[('2026-10-23', 'alpha', 'beta')] = 'away'  # inclusive +3 days
    plain[('2026-10-24', 'alpha', 'beta')] = 'home'  # +4 excluded
    indexed = at._SettledOutcomes(plain, {}, {})
    def no_full_scan():
        pytest.fail('indexed lookup scanned the entire settlement corpus')
    monkeypatch.setattr(indexed, 'items', no_full_scan)
    visited = []
    def guard(mh, ma, d, h, a):
        visited.append(d)
        return False
    monkeypatch.setattr(at, '_marker_boundary_blocks', guard)
    assert at._lookup_fallback(indexed, '2026-10-20', 'alpha', 'beta') == 'away'
    assert visited == ['2026-10-23']


def test_index_keeps_marker_boundary_and_invalid_date_refusal(monkeypatch):
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {
        ('2026-10-20', 'alpha', 'beta'): {('Alpha Women', 'Beta Women')}})
    plain = {('2026-10-20', 'alpha', 'beta'): 'home'}
    for settled in (plain, at._SettledOutcomes(plain, {}, {})):
        assert at._lookup_fallback(settled, '2026-10-20', 'alpha', 'beta') is None
        assert at._lookup_fallback(settled, 'not-a-date', 'alpha', 'beta') is None


def test_settlement_reuses_snapshot_without_rebuilding_donors(tmp_path, monkeypatch):
    day = '2026-10-19'
    leg = {'home': 'Alpha', 'away': 'Beta', 'match': 'Alpha vs Beta',
           'pick': 'home', 'market': 'match_over_25', 'odds': 1.5}
    state = at.fresh_state()
    state['open_slips'] = [{'date': day, 'staked_pct': 12.5,
                           'accas': [{'stake_pct': 12.5, 'odds': 1.5, 'legs': [leg]}]}]
    entries = {day: [{'home': 'Alpha', 'away': 'Beta', 'outcome': 'home'}]}
    keys = at._result_write_keys('Alpha', 'Beta')
    outcomes = {(day, h, a): 'home' for h, a in keys}
    scores = {(day, h, a): (3, 0) for h, a in keys}
    snapshot = at._SettledOutcomes(outcomes, entries, scores)
    def rebuild_forbidden():
        pytest.fail('settlement rebuilt facts already present in its snapshot')
    monkeypatch.setattr(at, 'load_settled_entries', rebuild_forbidden)
    monkeypatch.setattr(at, 'load_settled_scores', rebuild_forbidden)
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {})
    lane = at.Lane(tmp_path / 'state.json', 'scratch', 'scratch', at.STAKE_FRAC)
    # Compare full accounting/state, not merely a leg outcome.
    expected = deepcopy(state)
    expected_lines = at.settle_open_slips(expected, outcomes, archives=[],
                                           entries_by_date=entries, scores=scores, lane=lane)
    actual_lines = at.settle_open_slips(state, snapshot, archives=[], lane=lane)
    assert actual_lines == expected_lines
    assert state == expected
    assert state['open_slips'] == []
    assert len(state['history']) == 1


@pytest.mark.parametrize('enhancements', [False, True])
def test_cli_shares_one_snapshot_between_settle_and_build(enhancements, monkeypatch):
    snapshot = at._SettledOutcomes({}, {}, {})
    calls = []
    def load_once():
        calls.append('load')
        return snapshot
    def settle(state, settled, **kwargs):
        assert settled is snapshot
        calls.append('settle')
        return []
    def build(args, state, **kwargs):
        if enhancements:
            assert kwargs['scores'] is snapshot.scores
        else:
            assert kwargs['settled'] is snapshot
        calls.append('build')
        return 0
    monkeypatch.setattr(at.sys, 'argv', ['auto_tickets.py'] +
                        (['--enhancements'] if enhancements else []))
    monkeypatch.setattr(at, 'enhancement_board_enabled', lambda: True)
    monkeypatch.setattr(at, 'load_state', lambda *a: at.fresh_state())
    monkeypatch.setattr(at, 'load_settled', load_once)
    monkeypatch.setattr(at, 'settle_open_slips', settle)
    monkeypatch.setattr(at, 'cmd_today', build)
    monkeypatch.setattr(at, 'cmd_enhancement', build)
    assert at.main() == 0
    assert calls == ['load', 'settle', 'build']


def test_cmd_today_uses_explicit_empty_snapshot_without_reloading(tmp_path, monkeypatch):
    snapshot = at._SettledOutcomes({}, {}, {})
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path)
    def forbidden():
        pytest.fail('explicit empty facts must not trigger another donor load')
    monkeypatch.setattr(at, 'load_settled', forbidden)
    monkeypatch.setattr(at, 'is_frozen', lambda *a: False)
    # Deliberately missing slate: fail closed, but do not reload settlement.
    args = SimpleNamespace(date='2026-10-19', force=True)
    assert at.cmd_today(args, at.fresh_state(), settled=snapshot) == 1


def test_later_load_observes_new_result_facts(tmp_path, monkeypatch):
    import json
    import edgefactory.settlement as settlement
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path)
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {})
    monkeypatch.setattr(settlement, 'load_verified_results', lambda: [])
    path = tmp_path / 'settled_results.json'
    row = {'date': '2026-10-19', 'home': 'Alpha', 'away': 'Beta',
           'outcome': 'home', 'hs': 3, 'gs': 0}
    path.write_text(json.dumps({'rows': [row]}))
    first = at.load_settled()
    assert at.pick_result(dict(row, pick='home'), first) == 'win'
    row.update(outcome='away', hs=0, gs=3)
    path.write_text(json.dumps({'rows': [row]}))
    second = at.load_settled()
    assert at.pick_result(dict(row, pick='home'), second) == 'loss'
    assert first is not second
    assert first.scores != second.scores


@pytest.mark.parametrize('selection', ['home', 'draw', 'away'])
@pytest.mark.parametrize('outcome', ['home', 'draw', 'away'])
def test_every_1x2_selection_grades_by_equality_on_exact_and_rescheduled_dates(
    selection, outcome, monkeypatch
):
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {})
    pick = dict(date='2026-10-20', home='Alpha Town', away='Bravo City',
                market='1x2', pick=selection)
    hk, ak = at._result_write_keys(pick['home'], pick['away'])[0]
    expected = 'win' if selection == outcome else 'loss'
    assert at.pick_result(pick, {('2026-10-20', hk, ak): outcome}) == expected
    assert at._rescheduled_leg_result(
        pick['date'], pick, {('2026-10-21', hk, ak): outcome}) == expected


def test_rescheduled_draw_conflicts_and_squad_boundaries_remain_held(monkeypatch):
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {})
    pick = dict(date='2026-10-20', home='Alpha Town', away='Bravo City', pick='draw')
    hk, ak = at._result_write_keys(pick['home'], pick['away'])[0]
    settled = {('2026-10-21', hk, ak): 'draw', ('2026-10-19', hk, ak): 'away'}
    assert at._rescheduled_leg_result(pick['date'], pick, settled) == 'conflict'
    youth = dict(pick, home='Alpha Town U21', away='Bravo City U21')
    assert at._rescheduled_leg_result(pick['date'], youth, settled) is None


@pytest.mark.parametrize('played', ['2026-10-20', '2026-10-21'])
def test_draw_ticket_pays_correct_return_in_scratch_state_only(played, tmp_path, monkeypatch):
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path)
    monkeypatch.setattr(at, 'SETTLED_KEY_NAMES', {})
    day = '2026-10-20'
    pick = dict(date=day, home='Alpha Town', away='Bravo City', pick='draw')
    leg = dict(match='Alpha Town vs Bravo City', home=pick['home'], away=pick['away'],
               pick='draw', odds=3.5)
    state = at.fresh_state()
    state['open_slips'] = [dict(date=day, staked_pct=10., accas=[
        dict(stake_pct=10., odds=3.5, legs=[leg])])]
    hk, ak = at._result_write_keys(pick['home'], pick['away'])[0]
    at.settle_open_slips(state, {(played, hk, ak): 'draw'}, archives=[pick],
                         entries_by_date={played: [dict(pick, date=played, outcome='draw')]},
                         scores={})
    assert state['open_slips'] == []
    assert state['bank'] == pytest.approx(125.)  # 100 - 10 + 10*3.5
    assert state['history'][0]['returned_pct'] == 35.
    assert state['history'][0]['accas'][0]['legs'][0]['result'] == 'win'
