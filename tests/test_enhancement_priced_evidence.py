"""Cohort-backed admission without exact-price-history bootstrapping."""
from copy import deepcopy
import json

import pytest

from enhancement_fixtures import with_evidence
from edgefactory import enh_registry as reg
import scripts.auto_tickets as at


def pick(rate=.9, price=1.8):
    return with_evidence(dict(home='Alpha', away='Beta', pick='home', league='League',
        date='2026-10-22', as_of='2026-10-22T06:00:00+00:00',
        recommended_enhancement='match_over_25', enhancement_probability=rate,
        enhancement_price=price, enhancement_price_book='Pinnacle',
        enhancement_price_source='theoddsapi', enhancement_price_at='2026-10-22T05:00:00+00:00',
        enhancement_price_kickoff='2026-10-22T18:00:00+00:00'))


def test_empty_registry_can_admit_complete_acca_without_any_placed_bets(tmp_path):
    rows = [pick(), dict(pick(), home='Gamma')]
    before = deepcopy(rows)
    legs = at.enhancement_legs(rows, registry_root=tmp_path, execution_safe=True)
    assert [l['verdict'] for l in legs] == ['fire', 'fire']
    plan = at.plan_day(at.enhancement_pool(legs), 80.1656, enhancements=True)
    assert len(plan) == 1 and len(plan[0]['legs']) == 2
    assert rows == before
    assert not reg.registry_path(tmp_path).exists()
    evidence = legs[0]['cohort_evidence']
    assert evidence['basis'] == 'cohort_payout_bound'
    assert evidence['cohort_lower_bound'] == pytest.approx(reg.wilson_lb(180, 200))
    assert 'conditional_rate' not in evidence and 'priced_n' not in evidence


@pytest.mark.parametrize('rate,price,expected', [(.59, 1.8, 'payout_not_supported'),
    (.59, 2.0, 'fire'), (.9, 1.3, 'fire'), (.74, 1.3, 'payout_not_supported')])
def test_actual_quote_must_pay_for_cohort_uncertainty(tmp_path, rate, price, expected):
    row = pick(rate, price)
    row['enhancement_probability'] = None
    assert at.enhancement_legs([row], registry_root=tmp_path, execution_safe=True)[0]['verdict'] == expected


@pytest.mark.parametrize('key,value', [('league', 'Other'), ('pick', 'away'),
    ('enhancement_price', 2.2), ('enhancement_price_book', 'Other'),
    ('enhancement_price_source', 'oddspapi')])
def test_quote_context_does_not_fragment_historical_cohort(tmp_path, key, value):
    row = dict(pick(), **{key: value})
    e = reg.enhancement_cohort_evidence(row, priced=True, root=tmp_path)
    assert e['n'] == 200 and e['rate'] == .9
    assert e['price_context']['price'] == row['enhancement_price']
    assert e['cohort_lower_bound'] == pytest.approx(reg.wilson_lb(180, 200))


@pytest.mark.parametrize('key,value', [('as_of', '2026-10-22T04:00:00+00:00'),
    ('as_of', '2026-10-22T19:00:00+00:00'), ('enhancement_price_book', 'Matchbook'),
    ('enhancement_price_book', ''), ('enhancement_price_at', None),
    ('enhancement_price_kickoff', None), ('enhancement_price_source', 'unknown'),
    ('enhancement_price_at', '2026-10-22T05:00:00')])
def test_invalid_current_quote_is_not_repaired_by_cohort(tmp_path, key, value):
    row = dict(pick(), **{key: value})
    assert reg.enhancement_cohort_evidence(row, priced=True, root=tmp_path) is None
    assert at.enhancement_legs([row], registry_root=tmp_path, execution_safe=True)[0]['verdict'] != 'fire'


@pytest.mark.parametrize('n,rate,min_hits', [(3022, .5913, 1787), (100000, .5913, 59125),
                                           (200, 0., 0), (200, 1., 200)])
def test_rounded_rate_uses_lowest_compatible_hit_count(n, rate, min_hits):
    row = pick(rate)
    row['enhancement_cohort_n'] = n
    row['event_notes'][0]['cohort_n'] = n
    e = reg.enhancement_cohort_evidence(row, priced=True)
    assert e['cohort_min_hits'] == min_hits
    assert e['cohort_lower_bound'] == pytest.approx(reg.wilson_lb(min_hits, n))


def test_impossible_rate_and_count_fail_closed():
    assert reg.enhancement_cohort_evidence(pick(.5913), priced=True) is None


def test_registry_cannot_promote_or_demote_the_parent_cohort(tmp_path):
    path = reg.registry_path(tmp_path)
    path.parent.mkdir(parents=True)
    row = pick()
    baseline = reg.enhancement_cohort_evidence(row, priced=True, root=tmp_path)
    for payload in ({'markets': {}}, {'markets': {'match_over_25@v1': {
            'n': 99999, 'hits': 99999, 'records_truncated': True, 'status': 'BENCHED'}}}):
        path.write_text(json.dumps(payload))
        assert reg.enhancement_cohort_evidence(row, priced=True, root=tmp_path) == baseline
    # A favourable legacy market registry never substitutes for an absent parent.
    row['event_notes'][0]['engine'] = 'model'
    assert reg.enhancement_cohort_evidence(row, priced=True, root=tmp_path) is None


def leg(name, lower=.8, odds=1.8, book='Pinnacle', market='match_over_25'):
    return dict(match=f'{name} vs Away', market=market, price_book=book, pick=market,
                prob=.9, odds=odds, row=dict(date='2026-10-22', home=name, away='Away'),
                cohort_evidence=dict(basis='cohort_payout_bound', cohort_lower_bound=lower,
                                     price_context=dict(book=book, source='theoddsapi')))


def test_unknown_dependence_does_not_veto_individually_admitted_legs():
    pool = [leg('A', lower=.6), leg('B', lower=.6)]
    assert at.select_accas(pool, enhancements=True) == at.select_accas(pool)
    assert all('joint_probability' not in l for pair in at.select_accas(pool, enhancements=True) for l in pair)


def test_full_pool_can_replace_unfundable_top_pair_and_compete_alternate_markets():
    pool = [leg('A', book='Other'), leg('B'), leg('C'), leg('D')]
    selected = at.select_accas(pool, enhancements=True, max_accas=1)
    assert len(selected) == 1
    assert all(l['price_book'] == 'Pinnacle' for l in selected[0])
    alternative = leg('A', book='Pinnacle', market='btts_yes')
    assert at.select_accas([pool[0], alternative, pool[1]], enhancements=True)
    assert at.select_accas([alternative, leg('A')], enhancements=True) == []


def test_staking_arithmetic_unchanged_after_admission():
    pool = [leg('A'), leg('B'), leg('C'), leg('D')]
    baseline = at.plan_day(pool, 80.1656, max_accas=3)
    supported = at.plan_day(pool, 80.1656, max_accas=3, enhancements=True)
    assert at.STAKE_FRAC == .25
    assert [a['stake_pct'] for a in baseline] == [a['stake_pct'] for a in supported]


def test_alternative_uses_own_cohort_not_selected_markets_legacy_probability(tmp_path):
    row = pick()
    note = dict(row['event_notes'][0], market='btts_yes', cohort_rate=.7)
    for key in ('enhancement_price', 'enhancement_price_book', 'enhancement_price_source',
                'enhancement_price_at', 'enhancement_price_kickoff'):
        note[key] = row[key]
    row['event_notes'].append(note)
    legs = at.enhancement_legs([row], registry_root=tmp_path, execution_safe=True)
    alternative = next(l for l in legs if l['market'] == 'btts_yes')
    assert alternative['cohort_evidence']['rate'] == .7
    assert alternative['verdict'] == 'fire'


def test_selected_market_evidence_cannot_be_overwritten_by_another_over():
    chosen = leg('A', market='match_over_25')
    alternative = leg('A', market='match_over_35', lower=.7)
    partner = leg('B')
    for l in (chosen, alternative, partner):
        l['pick'] = 'over'
        l['label'] = l['market']
    pool = [chosen, alternative, partner]
    plan = at.plan_day(pool, 100., enhancements=True, max_accas=1)
    at._carry_lane_evidence(plan, pool)
    selected = next(l for l in plan[0]['legs'] if l['match'] == chosen['match'])
    assert selected['market'] == 'match_over_25'
    assert selected['cohort_evidence']['cohort_lower_bound'] == .8


@pytest.mark.parametrize('pairing', ['barbell', 'consecutive'])
def test_single_book_uses_shared_pairing_and_rank(pairing):
    pool = [dict(leg(str(i), lower=.6), prob=.8 - i * .01) for i in range(6)]
    assert at.select_accas(pool, enhancements=True, pairing=pairing) == at.select_accas(pool, pairing=pairing)


def test_quote_source_and_book_still_must_match():
    a, b = leg('A'), leg('B')
    b['cohort_evidence']['price_context']['source'] = 'oddspapi'
    assert at.select_accas([a, b], enhancements=True) == []
    b = leg('B', book='Other')
    assert at.select_accas([a, b], enhancements=True) == []


def test_alternative_book_can_supply_pair_without_duplicate_fixture_on_card():
    pool = [leg('A', book='Other'), leg('A'), leg('B'), leg('C'), leg('D')]
    accas = at.select_accas(pool, enhancements=True)
    assert len(accas) == 2
    keys = [at._fixture_key(l) for pair in accas for l in pair]
    assert len(set(keys)) == len(keys)
    assert all(l['price_book'] == 'Pinnacle' for pair in accas for l in pair)


def test_real_captured_pafos_lech_pair_no_longer_requires_worst_case_return(tmp_path):
    # Actual captured rates/counts/prices from audit blob 3fd9e9d8; not a claim
    # that these historical quotes remain executable now.
    rows = []
    for home, away, n, rate, odds in [('Pafos FC', 'Riga', 3022, .5913, 1.81),
                                     ('Lech Poznań', 'Sunderland', 1064, .5771, 1.88)]:
        row = pick(rate, odds)
        row.update(home=home, away=away, enhancement_probability=None,
                   enhancement_price_book='LeoVegas (SE)', enhancement_cohort_n=n)
        row['event_notes'][0]['cohort_n'] = n
        rows.append(row)
    legs = at.enhancement_legs(rows, registry_root=tmp_path, execution_safe=True)
    assert all(l['verdict'] == 'fire' for l in legs)
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, 80.1656, enhancements=True)
    at._carry_lane_evidence(plan, pool)
    assert len(plan) == 1 and plan[0]['odds'] == 3.4
    assert {l['match'] for l in plan[0]['legs']} == {'Pafos FC vs Riga', 'Lech Poznań vs Sunderland'}


def test_alternative_source_survives_until_executable_pair_competes():
    unavailable_partner = leg('A')
    unavailable_partner['cohort_evidence']['price_context']['source'] = 'oddspapi'
    valid_a, valid_b = leg('A'), leg('B')
    selected = at.select_accas([unavailable_partner, valid_a, valid_b], enhancements=True)
    assert len(selected) == 1
    assert all(l['cohort_evidence']['price_context']['source'] == 'theoddsapi' for l in selected[0])
