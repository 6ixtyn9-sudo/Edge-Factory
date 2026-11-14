"""Selected widened-window defaults and replay-safe model-floor semantics."""
import copy
import sys
from pathlib import Path

import pytest

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'scripts'),
                str(Path(__file__).resolve().parents[1] / 'src')]
import auto_tickets as at

DAY = '2026-11-01'


def leg(i, prob=.8, score=.7, odds=1.5):
    row = dict(date=DAY, home=f'Home {i}', away=f'Away {i}',
               kickoff=DAY + 'T20:00:00+02:00', bucket='CERTIFIED_CLEAN')
    return dict(match=f'Home {i} vs Away {i}', pick='over', prob=prob,
                odds=odds, ml_rank_probability=score, row=row,
                market='match_over_15', price_book='Test Book',
                price_source='theoddsapi',
                cohort_evidence={'basis': 'cohort_payout_bound',
                    'price_context': {'book': 'Test Book', 'source': 'theoddsapi'}})


def test_live_defaults_are_the_fully_graded_widened_recipes(monkeypatch):
    monkeypatch.delenv('EDGE_FACTORY_ENH_ML', raising=False)
    main, enh = at.ticket_planner_options('main'), at.ticket_planner_options('enh')
    assert (main['rank'], main['min_prob'], main['max_accas']) == ('prob', 0., 2)
    assert main['addon_floor'] is None and main['addon_ceiling'] is None
    assert at._main_pool_floor() == main['floor'] == enh['floor'] == 1.3
    assert (enh['rank'], enh['ml_enabled'], enh['model_min_prob'], enh['max_accas']) == ('prob', False, .6, 3)
    for options in (main, enh):
        assert (options['pairing'], options['legs_per_acca']) == ('barbell', 2)
        assert (options['stake_mode'], options['stake_frac'], options['stake_per_acca']) == ('per_acca', .25, .125)


def test_main_has_no_added_probability_floor_and_does_not_append(monkeypatch):
    monkeypatch.delenv('EDGE_FACTORY_ENH_ML', raising=False)
    pool = [leg(i, prob=p, odds=o) for i, (p, o) in enumerate([
        (.8, 1.3), (.75, 1.4), (.7, 1.5), (.64, 2.), (.6, 2.1), (.95, 1.25)])]
    for l in pool:
        l['pick'] = 'HOME'
    card = at.plan_day(pool, 100., **at.ticket_planner_options('main'))
    assert len(card) == 2 and all(len(a['legs']) == 2 for a in card)
    chosen = [l for a in card for l in a['legs']]
    assert any(l['prob'] == .64 for l in chosen)
    assert all(l['odds'] >= 1.3 for l in chosen)
    assert all(a['stake_pct'] == 12.5 for a in card)


def test_enh_cohort_orders_while_model_score_only_gates(monkeypatch):
    monkeypatch.delenv('EDGE_FACTORY_ENH_ML', raising=False)
    pool = [leg(i, prob=.9-i*.02, score=.6+i*.06) for i in range(6)]
    pool += [leg('missing', prob=.99, score=None), leg('low', prob=.98, score=.59999)]
    context = dict(lane='enh', options=at.ticket_planner_options('enh'), bank_eff=100.)
    card = at.plan_ticket_decision(context, prepared=dict(pool=pool))
    assert len(card) == 3 and sum(a['stake_pct'] for a in card) <= 25.0001
    chosen = [l for a in card for l in a['legs']]
    assert {l['match'] for l in chosen} == {l['match'] for l in pool[:6]}
    assert card[0]['legs'][0]['match'] == 'Home 0 vs Away 0'
    assert all(l['ranking_basis'] == 'cohort' and not l['ml_ordering_active'] for l in chosen)
    assert all(l['ml_rank_probability'] >= .6 for l in chosen)


@pytest.mark.parametrize('score', [None, float('nan'), float('inf'), -1., 1.1, .59999])
def test_unavailable_or_invalid_model_score_cannot_cross_the_floor(score):
    pool = [leg('bad', prob=.99, score=score), leg('good', score=.8)]
    assert at.plan_day(pool, 100., **at.ticket_planner_options('enh')) == []


def test_prepare_floor_is_auditable_and_absent_on_legacy_receipts():
    raw = []
    for i, score in enumerate([None, .59999, .6, .9]):
        p = leg(i, score=score)
        raw.append(dict(p, home=p['row']['home'], away=p['row']['away'],
                        verdict='fire', probability=p['prob'], price=p['odds']))
    context = at.ticket_decision_context('enh', DAY,
        at.datetime.fromisoformat(DAY+'T09:00:00+02:00'), [], raw, 100.,
        known_results=[None]*4, bank=100.)
    prepared = at.prepare_ticket_pool(context)
    assert [l['ml_rank_probability'] for l in prepared['pool']] == [.6, .9]
    assert [l['verdict'] for l in prepared['legs'][:2]] == ['below_model_probability_floor']*2
    assert sum(len(names) for names in prepared['withdrawn'].values()) == 2
    legacy = copy.deepcopy(context)
    legacy['options'].pop('model_min_prob')
    assert len(at.prepare_ticket_pool(legacy)['pool']) == 4
    assert all(l['verdict'] == 'fire' for l in context['pool'])  # no mutation


@pytest.mark.parametrize('minimum', [-.01, 1.01, float('nan'), float('inf')])
def test_invalid_model_floor_fails_closed(minimum):
    with pytest.raises(ValueError):
        at.plan_day([leg(0), leg(1)], 100., enhancements=True, model_min_prob=minimum)


def test_model_floor_is_enh_only_and_old_generic_calls_are_unchanged():
    with pytest.raises(ValueError):
        at.plan_day([leg(0), leg(1)], 100., model_min_prob=.6)
    pool = [leg(0, score=None), leg(1, score=None)]
    assert at.plan_day(pool, 100., enhancements=True, ml_enabled=False)
    assert at.plan_day(pool, 100., enhancements=True, model_min_prob=.6) == []
