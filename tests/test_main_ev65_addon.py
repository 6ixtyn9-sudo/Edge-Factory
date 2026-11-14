"""Explicit EV65/add-one recipe remains replayable; it is not the live default."""
import copy
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'src')]
import auto_tickets as at
import replay_harness as rh

DAY = '2026-11-01'


@pytest.fixture(autouse=True)
def explicit_trial_settings(monkeypatch):
    # Preserve every opt-in recipe assertion after changing the live defaults.
    for key, value in dict(MAIN_RANK='ev', MAIN_MIN_PROB=.65,
                           MAIN_ADDON_FLOOR=1.20, MAIN_ADDON_CEILING=1.30,
                           MAIN_ADDON_MIN_PROB=.65, MAIN_ADDON_RANK='ev').items():
        monkeypatch.setattr(at, key, value)


def row(tag, prob=.70, odds=1.5, **changes):
    r = dict(date=DAY, home=f'Home {tag}', away=f'Away {tag}', market='1x2',
             pick='home', avg_p=prob * 100, odds=odds, bucket='CERTIFIED_CLEAN',
             kickoff=DAY + 'T20:00:00+02:00', odds_source='bzzoiro_odds',
             bookmaker='Test Book', price_push_eligible=True,
             price_corroboration_sufficient=True, price_evidence='TEST')
    r.update(changes)
    return r


def pool(rows):
    return at.playable_legs(rows, day=DAY, floor=1.20, execution_safe=True)


def rows():
    return [row('A', .70, 1.8), row('B', .72, 1.7),
            row('C', .75, 1.6), row('D', .80, 1.4),
            row('extra-EV', .72, 1.29), row('extra-prob', .76, 1.20)]


def context(rs=None, **policy):
    rs = rows() if rs is None else rs
    policies = dict(pnl_weights={}, slice_policy={}, gate_labels=[])
    policies.update(policy)
    return at.ticket_decision_context(
        'main', DAY, at.datetime.fromisoformat(DAY + 'T09:05:00+02:00'),
        rs, pool(rs), 100., policy=policies, bank=100.,
        bank_state=dict(bank=100., open_slips=[]))


def doubles_options():
    return {k: v for k, v in at.ticket_planner_options('main').items()
            if not k.startswith('addon_')}


def test_explicit_trial_options_and_enh_are_independent():
    main, enh = at.ticket_planner_options('main'), at.ticket_planner_options('enh')
    assert (main['rank'], main['min_prob'], main['floor']) == ('ev', .65, 1.30)
    assert (main['legs_per_acca'], main['max_accas']) == (2, 2)
    assert (main['addon_floor'], main['addon_ceiling'], main['addon_min_prob'],
            main['addon_rank']) == (1.20, 1.30, .65, 'ev')
    assert (main['stake_mode'], main['stake_per_acca'], main['stake_frac']) == ('per_acca', .125, .25)
    assert enh['rank'] == at.ENHANCEMENT_RANK == 'prob'
    assert enh['max_accas'] == 3 and enh['floor'] == 1.30
    assert not ({'min_prob', 'addon_floor', 'addon_ceiling', 'addon_min_prob', 'addon_rank'} & enh.keys())
    assert enh['model_min_prob'] == .60


def test_both_accas_get_an_ev_ranked_extra_without_rebuilding_or_resizing():
    p = pool(rows())
    base = at.plan_day(p, 100., **doubles_options())
    actual = at.plan_day(p, 100., **at.ticket_planner_options('main'))
    assert len(base) == len(actual) == 2
    assert [len(a['legs']) for a in actual] == [3, 3]
    assert [a['legs'][-1]['match'] for a in actual] == [
        'Home extra-EV vs Away extra-EV', 'Home extra-prob vs Away extra-prob']
    for a, b in zip(actual, base):
        assert a['legs'][:2] == b['legs']
        assert a['stake_pct'] == b['stake_pct'] == 12.5
        assert a['odds'] == round(math.prod(l['odds'] for l in a['legs']), 2)
    assert sum(a['stake_pct'] for a in actual) == 25.
    assert len({at._fixture_key(l) for a in actual for l in a['legs']}) == 6


@pytest.mark.parametrize('extras,shape', [(0, [2, 2]), (1, [3, 2]), (2, [3, 3])])
def test_shortage_keeps_doubles_and_unused_stakes_are_not_redistributed(extras, shape):
    p = pool(rows()[:4 + extras])
    plan = at.plan_day(p, 100., **at.ticket_planner_options('main'))
    assert [len(a['legs']) for a in plan] == shape
    assert [a['stake_pct'] for a in plan] == [12.5, 12.5]
    single = at.plan_day(pool(rows()[:2] + rows()[4:4 + extras]), 100.,
                         **at.ticket_planner_options('main'))
    assert len(single) == 1 and single[0]['stake_pct'] == 12.5


def test_probability_and_band_boundaries_cannot_make_low_odds_base_legs_or_singles():
    rs = [row('base-A', .65, 1.40), row('base-B', .66, 1.50),
          row('below-prob', .64999, 9.0), row('below-extra-prob', .64999, 1.29),
          row('below-band', .90, 1.19999), row('lower-bound', .65, 1.20)]
    plan = at.plan_day(pool(rs), 100., **at.ticket_planner_options('main'))
    assert len(plan) == 1 and len(plan[0]['legs']) == 3
    assert all(l['odds'] >= 1.30 and l['prob'] >= .65 for l in plan[0]['legs'][:2])
    assert plan[0]['legs'][-1]['match'] == 'Home lower-bound vs Away lower-bound'
    assert at.plan_day(pool([row('one-base'), row('extra', .80, 1.25)]), 100.,
                       **at.ticket_planner_options('main')) == []
    # The 1.30 boundary may be a BASE leg, but must never be appended.
    p = pool(rows()[:4] + [row('upper-bound', .65, 1.30)])
    assert all(len(a['legs']) == 2 for a in at.plan_day(
        p, 100., **at.ticket_planner_options('main')))


def test_base_fixtures_and_opposite_side_extra_quotes_cannot_be_reused():
    rs = rows()[:4] + [row('A', .90, 1.25), row('extra', .75, 1.25),
                       row('extra', .70, 1.29, pick='away')]
    plan = at.plan_day(pool(rs), 100., **at.ticket_planner_options('main'))
    fixtures = [at._fixture_key(l) for a in plan for l in a['legs']]
    assert len(fixtures) == len(set(fixtures)) == 5
    assert [len(a['legs']) for a in plan] == [3, 2]


@pytest.mark.parametrize('change', [dict(price_push_eligible=False), dict(quarantine='alias_fuzzy'),
    dict(kickoff=DAY + 'T08:00:00+02:00'), dict(bucket='CAUTION'),
    dict(price_evidence='BLOCKED'), dict(avg_p=64.9)])
def test_extra_must_clear_execution_timing_probability_and_policy_gates(change):
    rs = rows()[:4] + [row('extra', .75, 1.25, **change)]
    ctx = context(rs, pnl_weights={'CAUTION': 0.0}, gate_labels=['BLOCKED'])
    plan = at.plan_ticket_decision(ctx)
    assert len(plan) == 2 and all(len(a['legs']) == 2 for a in plan)


def test_slice_bench_and_already_known_results_apply_to_subfloor_candidates():
    rs = rows()[:4] + [row('extra', .75, 1.25, bucket='CAUTION')]
    ctx = context(rs, slice_policy=dict(bench_buckets=['CAUTION']))
    assert all(len(a['legs']) == 2 for a in at.plan_ticket_decision(ctx))
    ctx = context(rs)
    next(l for l in ctx['pool'] if l['odds'] < 1.30)['result'] = 'win'
    assert all(len(a['legs']) == 2 for a in at.plan_ticket_decision(ctx))


def test_outcomes_never_influence_the_selected_card():
    p = pool(rows())
    expected = at.plan_day(p, 100., **at.ticket_planner_options('main'))
    changed = copy.deepcopy(p)
    for i, l in enumerate(changed):
        l['result'] = 'win' if i % 2 else 'loss'
    actual = at.plan_day(changed, 100., **at.ticket_planner_options('main'))
    assert at.ticket_card_identity(actual) == at.ticket_card_identity(expected)


def test_receipt_carries_new_policy_and_replays_without_reading_new_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path)
    ctx = context()
    plan = at.plan_ticket_decision(ctx)
    assert [len(a['legs']) for a in plan] == [3, 3]
    assert all(l['price_book'] == 'Test Book' for a in plan for l in a['legs'])
    at.write_decision_receipt(ctx, plan, frozen=True)
    saved = at.read_ticket_receipt(at.decision_receipt_path(DAY))
    monkeypatch.setattr(at, 'MAIN_RANK', 'prob')
    monkeypatch.setattr(at, 'MAIN_MIN_PROB', .99)
    replayed = at.plan_ticket_decision(saved['context'])
    assert at.ticket_card_identity(replayed) == at.ticket_card_identity(saved['plan'])
    assert saved['context']['options']['addon_min_prob'] == .65


def test_legacy_receipt_without_trial_options_keeps_legacy_order_and_shape():
    ctx = context(rows() + [row('legacy-low-prob', .60, 3.0)])
    for k in rh.PLAN_KEYS:
        ctx['options'].pop(k, None)
    ctx['options']['rank'] = 'prob'
    prepared = at.prepare_ticket_pool(ctx)
    expected = at.plan_day(prepared['pool'], 100., **ctx['options'])
    actual = at.plan_ticket_decision(ctx, prepared=prepared)
    assert all(len(a['legs']) == 2 for a in actual)
    assert at.ticket_card_identity(actual, prepared['pool']) == at.ticket_card_identity(expected, prepared['pool'])
    assert any(l['prob'] == .60 for l in prepared['pool'])


def test_existing_replay_cli_forwards_the_same_trial_options_to_the_shared_planner():
    spec = rh.parse_spec('rank=ev,min_prob=.65,addon_floor=1.2,addon_ceiling=1.3,addon_min_prob=.65,addon_rank=ev')
    p = pool(rows())
    for l in p:
        l['result'] = 'win'
    result = rh.replay({DAY: p}, spec)
    assert result[DAY]['accas'] == [rh._graded_acca(a) for a in at.plan_day(
        p, 100., **at.ticket_planner_options('main'))]
    assert all(len(ls) == 3 for ls in result[DAY]['legs'])


@pytest.mark.parametrize('options', [dict(min_prob=float('nan')), dict(min_prob=1.01),
    dict(addon_floor=1.2), dict(addon_floor=1.3, addon_ceiling=1.2),
    dict(addon_floor=1.2, addon_ceiling=1.3, addon_rank='unknown'),
    dict(addon_floor=1.2, addon_ceiling=1.3, enhancements=True),
    dict(addon_floor=1.2, addon_ceiling=1.3, legs_per_acca=3)])
def test_invalid_trial_options_fail_explicitly(options):
    with pytest.raises(ValueError):
        at.plan_day(pool(rows()), 100., **options)


def test_actual_daily_entry_point_admits_extras_freezes_both_trebles_and_never_recuts_them(tmp_path, monkeypatch):
    class Clock(at.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 1, 9, 5, tzinfo=tz or at.TZ)
    monkeypatch.setattr(at, 'datetime', Clock)
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path)
    monkeypatch.setattr(at, 'STATE_FILE', tmp_path / 'state.json')
    monkeypatch.setattr(at, 'BUCKET_PNL_FILE', tmp_path / 'bucket_pnl.json')
    monkeypatch.setattr(at, 'load_archived_picks', lambda: [])
    monkeypatch.setattr(at, 'compute_bucket_pnl', lambda *a, **kw: ({}, {}))
    monkeypatch.setattr(at, 'ensure_slice_seeded', lambda *a, **kw: None)
    verdicts = {b: dict(n=0, n_seeded=0, verdict='UNKNOWN', demote_streak=0,
                        bench_streak=0, action='FULL') for b in at._SLICE_BUCKET_ORDER}
    monkeypatch.setattr(at, 'compute_bucket_slice', lambda *a, **kw: ({}, verdicts))
    monkeypatch.setattr(at.acca_gate, 'refresh', lambda *a: ([], 'test'))
    monkeypatch.setattr(at, 'log_acca_gate_run', lambda *a, **kw: None)
    (tmp_path / 'picks_today.json').write_text(json.dumps(rows()))
    st = at.fresh_state()
    assert at.cmd_today(SimpleNamespace(date=DAY, force=False), st, settled={}) == 0
    assert len(st['open_slips']) == 1
    assert [len(a['legs']) for a in st['open_slips'][0]['accas']] == [3, 3]
    assert st['open_slips'][0]['staked_pct'] == 25.
    payload = at.read_ticket_receipt(at.decision_receipt_path(DAY))
    assert len(payload['context']['pool']) == 6
    assert at.ticket_card_identity(payload['plan']) == at.ticket_card_identity(at.plan_ticket_decision(payload['context']))
    slip = tmp_path / f'auto_tickets_{DAY}.txt'
    receipt = at.decision_receipt_path(DAY)
    frozen = (slip.read_bytes(), receipt.read_bytes(), copy.deepcopy(st))
    (tmp_path / 'picks_today.json').write_text('[]')
    assert at.cmd_today(SimpleNamespace(date=DAY, force=False), st, settled={}) == 0
    assert (slip.read_bytes(), receipt.read_bytes(), st) == frozen
