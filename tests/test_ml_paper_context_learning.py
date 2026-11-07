"""Conditional source learner: actual factor learning, frozen inputs and causality."""
from copy import deepcopy
from datetime import timedelta
import json
import math

import pytest

from edgefactory import ml_paper as mp
from edgefactory.form_intel import ResultsArchive
from test_ml_paper import NOW, candidate, receipt, pick, capture

DAY = '2026-11-01'
STAMP = NOW - timedelta(days=1)


def contextual(i, *, day=DAY, high=True, factor='league'):
    c = candidate(i, date=day, p=.6)
    at = STAMP if day == DAY else NOW
    c.update(price_at=at.isoformat(), price_source='pinnapi_odds', odds=2., book='Pinnacle')
    c['context'] = dict(schema='source_market_context_v1', as_of=at.isoformat(),
                        league='League', country='Country', country_sources=[], parent_confidence=.7, parent_selection='home',
                        form_as_of_exclusive=None, form_values={})
    if factor in ('league', 'country'):
        c['context'][factor] = 'Group A' if high else 'Group B'
    elif factor == 'confidence':
        c['context']['parent_confidence'] = .95 if high else .45
    elif factor == 'source':
        c['ml_inputs']['sources'] = ['statarea'] if high else ['vitibet']
    elif factor == 'odds':
        c['odds'] = 1.4 if high else 3.6
    elif factor in ('home_form_gf', 'away_form_ga'):
        c['context']['form_values'] = {factor: 3. if high else .2}
        c['context']['form_as_of_exclusive'] = DAY
    elif factor in ('forecast_xg_home_mean', 'forecast_1x2_home_spread'):
        c['ml_inputs']['values'][factor] = (.8 if high else .1)
    return c


def fit_signal(factor, *, reverse=False, n=64):
    rows = [contextual(i, high=i % 2 == 0, factor=factor) for i in range(n)]
    return mp.learn([receipt(DAY, rows)], NOW,
                    lambda c: (2, 0) if (int(c['candidate_id']) % 2 == 0) != reverse else (0, 2))


@pytest.mark.parametrize('factor', ['league', 'country', 'confidence', 'source', 'odds',
                                    'home_form_gf', 'away_form_ga', 'forecast_xg_home_mean',
                                    'forecast_1x2_home_spread'])
def test_each_observed_factor_learns_a_conditional_correction_not_just_one_power(factor):
    m = fit_signal(factor)
    a = contextual(1001, day=NOW.date().isoformat(), factor=factor, high=True)
    b = contextual(1002, day=NOW.date().isoformat(), factor=factor, high=False)
    assert a['base_partition'] == b['base_partition']
    mp.apply_learning([a, b], json.loads(json.dumps(m)))
    assert a['probability'] > b['probability'] + .001
    assert m['parameters'] == 1 + len(m['context_model']['coef']) > 1
    # The same signal can correct in the opposite direction when outcomes do.
    mp.apply_learning([a, b], fit_signal(factor, reverse=True))
    assert a['probability'] < b['probability'] - .001


def test_role_learning_can_correct_home_away_bias_and_reverse_source_ranking():
    rows = [candidate(i, date=DAY, p=.8) for i in range(80)]
    m = mp.learn([receipt(DAY, rows)], NOW, lambda c: (0, 2))
    home = candidate(100)
    away = deepcopy(home)
    away.update(candidate_id='away', selection='away', base_probability=away['base_partition'][2][2])
    # The shared partition, not the old displayed probability, is authoritative.
    mp.apply_learning([home, away], m)
    assert away['probability'] > home['probability']


def test_complements_dc_and_books_share_one_context_prediction_even_across_recipes():
    m = fit_signal('confidence')
    home = contextual(1000, day=NOW.date().isoformat())
    rows = [home]
    for j, side in enumerate(('draw', 'away')):
        c = deepcopy(home)
        c.update(candidate_id=str(1001 + j), selection=side, base_probability=c['base_partition'][j+1][2])
        c['context']['parent_confidence'] = .1  # not an independent model per side
        rows.append(c)
    dc = deepcopy(home)
    dc.update(candidate_id='dc', market='double_chance', selection='1x',
              base_probability=home['base_partition'][0][2] + home['base_partition'][1][2])
    duplicate = deepcopy(home)
    duplicate.update(candidate_id='other-book', book='Other', odds=2.2)
    rows.extend([dc, duplicate])
    mp.apply_learning(rows, m)
    assert sum(c['probability'] for c in rows[:3]) == pytest.approx(1)
    assert dc['probability'] == pytest.approx(rows[0]['probability'] + rows[1]['probability'])
    assert duplicate['probability'] == pytest.approx(home['probability'])
    before = [c['probability'] for c in rows]
    mp.apply_learning(list(reversed(rows)), m)
    assert [c['probability'] for c in rows] == before


def test_existing_form_builder_uses_prior_days_and_minimum_history_not_target_goals():
    c = contextual(100, day=NOW.date().isoformat())
    historic = [dict(date=f'2026-10-{20+i:02}', home=c['home'], away=f'Visitor {i}', hs=2, gs=1, league='League')
                for i in range(5)]
    target = dict(date=c['date'], home=c['home'], away=c['away'], hs=90, gs=0, league='League')
    features = mp._context_features(c, c['base_partition'], ResultsArchive(historic), NOW, {})
    after = mp._context_features(c, c['base_partition'], ResultsArchive(historic + [target]), NOW, {})
    assert features == after
    assert features[0]['value:home_form_gf:1x2:home'] == pytest.approx(2 / 3)
    assert features[0]['value:home_form_goal_difference:1x2:home'] == pytest.approx(.5)
    insufficient = mp._context_features(c, c['base_partition'], ResultsArchive(historic[:4]), NOW, {})
    assert 'value:home_form_gf:1x2:home' not in insufficient[0]
    assert insufficient[0]['missing:home_form_gf:1x2:home'] == 1
    # Senior form cannot inherit a youth team's results.
    youth = [dict(r, home=c['home'] + ' U21') for r in historic]
    guarded = mp._context_features(c, c['base_partition'], ResultsArchive(youth), NOW, {})
    assert 'value:home_form_gf:1x2:home' not in guarded[0]


def test_unobserved_factors_do_not_multiply_role_intercepts_or_invent_country():
    cs = [candidate(i, date=DAY) for i in range(6)]
    m = mp.learn([receipt(DAY, cs)], NOW, lambda c: (2, 0))
    assert m['context_model']['feature_cols'] == ['role:1x2:away', 'role:1x2:draw', 'role:1x2:home']
    assert m['context_model']['factor_coverage']['country'] == 0
    context = mp._candidate_context(dict(pick(), league='Bundesliga', ctx={'league': 'CAUTION'}), NOW)
    assert context['country'] is None and context['league'] == 'Bundesliga'


def test_price_features_are_timestamped_duplicate_safe_and_not_legacy_band_labels():
    c = contextual(1)
    c['ctx'] = {'odds_band_name': 'invented'}
    at = mp._context_prices([c], STAMP)
    assert at == mp._context_prices([c, deepcopy(c)], STAMP)
    future = dict(c, price_at=(STAMP + timedelta(seconds=1)).isoformat(), odds=99)
    stale = dict(c, price_at=(STAMP - timedelta(hours=13)).isoformat(), odds=99)
    assert at == mp._context_prices([c, future, stale], STAMP)
    conflict = dict(c, odds=99)
    assert mp._context_prices([c, conflict], STAMP) == {}
    features = mp._context_features(c, c['base_partition'], ResultsArchive([]), STAMP, at)
    assert 'odds:1.80-2.19:1x2:home' in features[0]
    assert not any('invented' in key for key in features[0])


def test_sparse_categories_shrink_towards_pooled_prediction():
    m = fit_signal('league')
    # One independent fixture of evidence must not produce a league certainty.
    row = contextual(999, factor='league')
    row['context']['league'] = 'One fixture league'
    source = [contextual(i, factor='league') for i in range(64)] + [row]
    fitted = mp.learn([receipt(DAY, source)], NOW, lambda c: (2, 0))
    coefs = dict(zip(fitted['context_model']['feature_cols'], fitted['context_model']['coef']))
    rare = [abs(v) for k, v in coefs.items() if k.startswith('league:one fixture league:')]
    assert rare and max(rare) < .1
    assert m['context_model']['regularization'] > 0


@pytest.mark.parametrize('damage', ['length', 'missing', 'future_form', 'future_context'])
def test_bad_context_model_or_future_context_fails_atomically(damage):
    m = fit_signal('league')
    a = contextual(1001, day=NOW.date().isoformat())
    b = contextual(1002, day=NOW.date().isoformat())
    if damage == 'length':
        m['context_model']['coef'].append(.1)
    elif damage == 'missing':
        del m['context_model']
    elif damage == 'future_form':
        m['context_model']['form_history'].append(dict(date=NOW.date().isoformat(), home='Home', away='Away', hs=0, gs=0))
    else:
        b['context']['as_of'] = (NOW + timedelta(seconds=1)).isoformat()
    m['model_key'] = mp.digest({k: v for k, v in m.items() if k != 'model_key'})
    before = deepcopy([a, b])
    with pytest.raises(ValueError):
        mp.apply_learning([a, b], m)
    assert [a, b] == before


def test_historical_temperature_serialization_still_replays_without_new_context():
    old = mp.learn([], NOW, lambda c: None)
    del old['context_model']
    old.update(learning_policy='fixture_balanced_source_market_temperature',
               status='fitted_source_market_temperature', power=.7)
    old['model_key'] = mp.digest({k: v for k, v in old.items() if k != 'model_key'})
    c = candidate(1)
    expected = c['base_partition'][0][2] ** .7 / math.fsum(v ** .7 for _, _, v in c['base_partition'])
    mp.apply_learning([c], json.loads(json.dumps(old)))
    assert c['probability'] == expected


def test_frozen_context_bound_into_owned_model_and_no_enh_fit_dependency(tmp_path):
    row = pick()
    row['country'] = 'South Africa'
    r = capture(tmp_path, [row, pick(2)])
    c = next(c for c in r['candidates'] if c['home'] == row['home'])
    assert c['context']['country'] == 'South Africa'
    assert c['context']['form_values']['home_form_gf'] == 2
    assert r['models'][c['model_key']]['context'] == c['context']
    tampered = deepcopy(r)
    tampered['candidates'][0]['context']['country'] = 'Changed'
    # Rehashing an outer receipt cannot rewrite the owned model binding.
    tampered['sha256'] = mp.digest({k: v for k, v in tampered.items() if k != 'sha256'})
    with pytest.raises(ValueError):
        mp._validate_bets(tampered)


def test_chronological_refit_does_not_read_future_labels_or_future_record_features():
    past = [contextual(i) for i in range(10)]
    future = [contextual(i + 50, day='2026-11-03') for i in range(10)]
    seen = []
    def lookup(c):
        seen.append(c['date'])
        assert c['date'] < NOW.date().isoformat()
        return (2, 0)
    a = mp.learn([receipt(DAY, past)], NOW, lookup)
    b = mp.learn([receipt(DAY, past), receipt('2026-11-03', future)], NOW, lookup)
    assert a == b
    assert seen and all(d == DAY for d in seen)


def test_all_retained_frozen_receipts_replay_without_rewriting_history():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / 'localdata'
    paths = mp.receipt_files(root)
    import hashlib
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    history = mp.receipts(root)
    assert history and all(hashlib.sha256(p.read_bytes()).hexdigest() == value for p, value in before.items())


def test_joint_context_solver_failure_is_closed_not_a_temperature_fallback(monkeypatch):
    import scipy.optimize
    class Failed:
        success = False
    monkeypatch.setattr(scipy.optimize, 'minimize', lambda *a, **kw: Failed())
    with pytest.raises(ValueError, match='no old-model fallback'):
        fit_signal('league')


def test_unseen_country_shrinks_to_the_pooled_role_not_a_guessed_country():
    m = fit_signal('country')
    rows = [contextual(1001+i, day=NOW.date().isoformat(), factor='country', high=i==0)
            for i in range(3)]
    rows[2]['context']['country'] = 'Never observed country'
    mp.apply_learning(rows, m)
    assert rows[0]['probability'] > rows[2]['probability'] > rows[1]['probability']


def test_form_target_fields_and_unknown_context_schema_cannot_become_predictors():
    m = fit_signal('league')
    c = contextual(1001, day=NOW.date().isoformat())
    c['context']['form_values'] = {'target_home_goals': 2}
    c['context']['form_as_of_exclusive'] = DAY
    with pytest.raises(ValueError, match='invalid form context value'):
        mp.apply_learning([c], m)
    c['context']['form_values'] = {}
    c['context']['target_score'] = [2, 0]
    with pytest.raises(ValueError, match='invalid frozen ML context'):
        mp.apply_learning([c], m)


@pytest.mark.parametrize('countries,expected', [(['England', 'England'], 'England'),
    (['England', 'Germany'], None), ([None, 'England'], 'England')])
def test_country_emission_uses_only_agreeing_existing_source_evidence(countries, expected):
    from edgefactory import consensus_contracts as cc
    rows = [dict(date=DAY, home='Home Club', away='Away Club', country=country,
                 league='Premier League', kickoff=DAY+'T12:00:00Z') for country in countries]
    votes = {s: dict(side='home', probs=dict(home=.7, draw=.1, away=.2), row=r)
             for s, r in zip(('statarea', 'vitibet'), rows)}
    observations = {((DAY, 'homeclub', 'awayclub'), '1x2'): votes}
    edge = dict(sources=sorted(votes), market='1x2', strategy='unanimous', threshold=0)
    emitted = next(cc.contract_rows(observations, set(), {}, edge,
                                    settled=False, enhancement_features=True))
    assert emitted['enhancement_country'] == expected
    row = dict(pick(), **{k: v for k, v in emitted.items() if k.startswith('enhancement_')})
    context = mp._candidate_context(row, NOW)
    assert context['country'] == expected
    assert context['country_sources'] == emitted['enhancement_country_sources']


def test_missing_or_unbound_country_witness_is_not_fabricated():
    row = dict(pick(), enhancement_country='England', enhancement_country_sources=['vitibet'],
               enhancement_feature_sources=['statarea'])
    assert mp._candidate_context(row, NOW)['country'] is None
    row.update(country='England', ctx={'country': 'Germany'})
    assert mp._candidate_context(row, NOW)['country'] is None


def test_conflicting_fixture_scores_cannot_train_different_market_truths():
    c = contextual(1)
    c['ml_inputs']['values']['forecast_btts_yes_mean'] = .6
    other = deepcopy(c)
    other.update(candidate_id='different-market', market='btts_yes', selection='yes')
    m = mp.learn([receipt(DAY, [c, other])], NOW,
                 lambda r: (2, 0) if r['candidate_id'] == '1' else (2, 1))
    assert m['fixtures'] == m['observations'] == 0
    assert m['training_admission']['excluded_by_reason']['conflicting_resolved_fixture_scores'] == 2
    assert m['context_model']['form_history'] == []


def test_non_bookmaker_fair_prices_are_not_real_odds_context():
    c = contextual(1)
    c['price_source'] = 'betbetter'
    assert mp._context_prices([c], STAMP) == {}


def test_duplicate_source_country_conflicts_do_not_change_parent_votes():
    import duckdb
    import pandas as pd
    from edgefactory import consensus_contracts as cc
    con = duckdb.connect()
    rows = [dict(date=DAY, home='Home Club', away='Away Club', country=country,
                 league='Premier League', kickoff=DAY+'T12:00:00Z',
                 captured_at=DAY+'T06:00:00Z', p1=.7, px=.1, p2=.2)
            for country in ('England', 'Germany')]
    con.register('data', pd.DataFrame(rows))
    con.execute('CREATE TABLE statarea AS SELECT * FROM data')
    _, observations, ambiguous, resolved, _ = cc.collect_observations(con, start=DAY, as_of='2026-11-02')
    edge = dict(sources=['statarea'], market='1x2', strategy='single', threshold=0)
    emitted = next(cc.contract_rows(observations, ambiguous, resolved, edge,
                                    settled=False, enhancement_features=True))
    assert emitted['avg_p'] == 70
    assert emitted['enhancement_source_features']['forecast_1x2_home_mean'] == .7
    assert emitted['enhancement_country'] is None and emitted['enhancement_country_sources'] == []
    con.close()
