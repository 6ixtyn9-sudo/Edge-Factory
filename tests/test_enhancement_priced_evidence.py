"""Actual registry evidence and shared live/replay selection, no admission mocks."""
from copy import deepcopy
from datetime import datetime, timezone
import json

import pytest

from enhancement_fixtures import with_evidence
from edgefactory import enh_registry as reg
import scripts.auto_tickets as at
import scripts.picks_today as pt


def pick():
    return with_evidence(dict(home='Alpha', away='Beta', pick='home', league='League',
        date='2026-10-22', as_of='2026-10-22T06:00:00+00:00',
        recommended_enhancement='match_over_25', enhancement_probability=.59,
        enhancement_price=1.8, enhancement_price_book='Pinnacle',
        enhancement_price_source='theoddsapi', enhancement_price_at='2026-10-22T05:00:00+00:00',
        enhancement_price_kickoff='2026-10-22T18:00:00+00:00'))


def seed(root, row=None, hits=30):
    row = row or pick()
    context = reg.enhancement_price_context(row)
    assert context
    records = []
    for i in range(30):
        old = dict(context, captured_at='2026-10-20T05:00:00+00:00',
                   decision_at='2026-10-20T06:00:00+00:00', kickoff='2026-10-20T18:00:00+00:00')
        records.append(dict(date='2026-10-20', match=f'H{i} vs A', home=f'H{i}', away='A',
                            price=1.8, source='theoddsapi', hit=i < hits, price_context=old,
                            recorded_at='2026-10-21T06:00:00+00:00'))
    payload = dict(markets={'match_over_25@v1': dict(n=30, records=records, status='PAPER')})
    path = reg.registry_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))
    return payload


def test_descriptive_rate_cannot_authorize_quote(tmp_path):
    row = pick()
    assert reg.enhancement_cohort_evidence(row)['rate'] == .59
    assert reg.enhancement_cohort_evidence(row, priced=True, root=tmp_path) is None
    row['enhancement_probability'] = None
    assert reg.enhancement_cohort_evidence(row)['rate'] == .59
    assert at.enhancement_legs([row], registry_root=tmp_path, execution_safe=True)[0]['verdict'] == 'no_priced_context_evidence'


def test_exact_context_quote_uses_own_records_not_global_rate(tmp_path):
    seed(tmp_path)
    e = reg.enhancement_cohort_evidence(pick(), priced=True, root=tmp_path)
    assert e['rate'] == .59
    assert e['conditional_rate'] == 1
    assert e['priced_n'] == 30
    assert e['price_lower_bound'] == pytest.approx(reg.wilson_lb(30, 30))
    assert at.enhancement_legs([pick()], registry_root=tmp_path, execution_safe=True)[0]['verdict'] == 'fire'


@pytest.mark.parametrize('key,value', [('league', 'Other'), ('pick', 'away'),
    ('enhancement_price', 2.2), ('enhancement_price_book', 'Other'),
    ('enhancement_price_source', 'oddspapi'), ('as_of', '2026-10-22T04:00:00+00:00'),
    ('enhancement_price_book', 'Matchbook')])
def test_no_context_or_timing_fallback(tmp_path, key, value):
    seed(tmp_path)
    row = dict(pick(), **{key: value})
    assert reg.enhancement_cohort_evidence(row, priced=True, root=tmp_path) is None


@pytest.mark.parametrize('mutation', ['future', 'late_record', 'legacy', 'truncated', 'benched', 'duplicate'])
def test_bad_retained_evidence_never_certifies(tmp_path, mutation):
    payload = seed(tmp_path)
    entry = payload['markets']['match_over_25@v1']
    if mutation == 'truncated':
        entry['records_truncated'] = True
    elif mutation == 'benched':
        entry['status'] = 'BENCHED'
    else:
        for rec in entry['records']:
            if mutation == 'future': rec['date'] = '2026-10-22'
            if mutation == 'late_record': rec['recorded_at'] = '2026-10-22T07:00:00+00:00'
            if mutation == 'legacy': rec.pop('price_context')
            if mutation == 'duplicate': rec['home'] = 'Same'
    reg.registry_path(tmp_path).write_text(json.dumps(payload))
    assert reg.enhancement_cohort_evidence(pick(), priced=True, root=tmp_path) is None


def leg(name, lower=.8, odds=1.8, book='Pinnacle', market='match_over_25'):
    return dict(match=f'{name} vs Away', market=market, price_book=book, pick=market,
                prob=.9, odds=odds, row=dict(date='2026-10-22', home=name, away='Away'),
                cohort_evidence=dict(basis='exact_context_priced_sample', price_lower_bound=lower,
                                     price_context=dict(book=book, source='theoddsapi')))


def test_complete_acca_does_not_multiply_marginals():
    # Both individually clear 1/.6; independence would admit their product.
    pool = [leg('A', lower=.6), leg('B', lower=.6)]
    assert at.select_accas(pool, enhancements=True) == []
    assert at.select_accas(pool)  # Main's selection recipe is unchanged.


def test_full_pool_can_replace_unfundable_top_pair_and_compete_alternate_markets():
    pool = [leg('A', book='Other'), leg('B'), leg('C'), leg('D')]
    selected = at.select_accas(pool, enhancements=True, max_accas=1)
    assert len(selected) == 1
    assert all(l['price_book'] == 'Pinnacle' for l in selected[0])
    # Preserve an alternative market on A until same-book complete tickets compete.
    alternative = leg('A', book='Pinnacle', market='btts_yes')
    assert at.select_accas([pool[0], alternative, pool[1]], enhancements=True)
    assert at.select_accas([alternative, leg('A')], enhancements=True) == []


def test_staking_arithmetic_unchanged_after_admission():
    pool = [leg('A'), leg('B'), leg('C'), leg('D')]
    baseline = at.plan_day(pool, 80.1656, max_accas=3)
    supported = at.plan_day(pool, 80.1656, max_accas=3, enhancements=True)
    assert at.STAKE_FRAC == .25
    assert [a['stake_pct'] for a in baseline] == [a['stake_pct'] for a in supported]


def test_high_frequency_can_still_fail_actual_payout(tmp_path):
    seed(tmp_path, hits=22)
    row = pick()
    row['enhancement_price'] = 1.3
    payload = json.loads(reg.registry_path(tmp_path).read_text())
    for rec in payload['markets']['match_over_25@v1']['records']:
        rec['price_context']['price'] = 1.3
        rec['price'] = 1.3
    reg.registry_path(tmp_path).write_text(json.dumps(payload))
    assert at.enhancement_legs([row], registry_root=tmp_path, execution_safe=True)[0]['verdict'] == 'payout_not_supported'


def test_alternative_uses_own_cohort_not_selected_markets_legacy_probability(tmp_path):
    row = pick()
    note = dict(row['event_notes'][0], market='btts_yes', cohort_rate=.7)
    for key in ('enhancement_price', 'enhancement_price_book', 'enhancement_price_source',
                'enhancement_price_at', 'enhancement_price_kickoff'):
        note[key] = row[key]
    row['event_notes'].append(note)
    legs = at.enhancement_legs([row], registry_root=tmp_path, execution_safe=True)
    assert len(legs) == 2
    alternative = next(l for l in legs if l['market'] == 'btts_yes')
    assert alternative['cohort_evidence']['rate'] == .7
    assert alternative['verdict'] == 'no_priced_context_evidence'
