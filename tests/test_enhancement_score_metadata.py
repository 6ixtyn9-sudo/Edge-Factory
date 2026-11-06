"""Prospective score-model donor repair; raw/financial/Main paths unchanged."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from edgefactory import consensus_contracts as cc
from edgefactory.settlement import regulation_score

FIXTURE = json.loads((Path(__file__).parent / 'fixtures' /
    'betexplorer_competition_score_metadata_2026-11-06.json').read_text())
ROWS = [r['row'] for r in FIXTURE['rows']]


def connection(rows, predictions=()):
    con = duckdb.connect(':memory:')
    for name, data in [('betexplorer', rows), ('scoutingstats', predictions)]:
        if data:
            con.register('seed', pd.DataFrame(data))
            con.execute(f'CREATE TABLE {name} AS SELECT * FROM seed')
            con.unregister('seed')
    return con


def snapshot(con, **kw):
    return cc.collect_observations(con, start='2026-06-13', as_of='2026-11-06',
        regulation_only=True, include_form_names=True, **kw)


@pytest.mark.parametrize('row', ROWS)
def test_authentic_metadata_score_no_longer_becomes_training_label_or_form(row):
    original = deepcopy(row)
    con = connection([row])
    coverage, _, _, resolved, scores = snapshot(con)
    key = cc._remine_key(row)
    assert 'ft' not in resolved.get(key, {})
    assert not scores.get(key, {}).get('ft')
    assert not cc._enhancement_archive(con, '2026-06-13', '2026-11-06', resolved, {}).rows
    audit = coverage['betexplorer']['score_admission']
    assert audit['excluded_donor_period_occurrences'] == audit['excluded_fixtures'] == 1
    assert audit['excluded_by_period'] == {'ft': 1}
    assert len(audit['evidence_sha256']) == 64
    assert row == original
    # No shared settlement rewrite or Main remine intervention.
    assert regulation_score(row) == (int(row['hs']), int(row['gs']))
    main = cc.collect_observations(con, start='2026-06-13', as_of='2026-11-06')[3]
    assert main[key]['ft'] == (int(row['hs']), int(row['gs']))


@pytest.mark.parametrize('url', [
    '', 'https://other.example/football/gabon/d1-2025-2026/bitam-usoyem/id/',
    'https://betexplorer.com.evil.example/football/gabon/d1-2025-2026/a/b/',
    'https://www.betexplorer.com/basketball/gabon/d1-2025-2026/a/b/',
    'https://www.betexplorer.com/football/gabon/d1/club-2025/id2026/',
    'https://www.betexplorer.com/football/gabon/d1/a/b/?season=2025-2026',
    'https://www.betexplorer.com/football/gabon/d1/a/b/#2025-2026',
    'https://[broken/football/gabon/d1-2025-2026/a/b/',
])
def test_no_year_evidence_is_not_permission_for_an_arbitrary_score_cap(url):
    row = dict(ROWS[0], match_url=url)
    assert not cc._betexplorer_score_is_competition_metadata(row, (1, 2025))
    assert snapshot(connection([row]))[3][cc._remine_key(row)]['ft'] == (1, 2025)


@pytest.mark.parametrize('pair', [(0, 0), (1, 2), (19, 0), (99, 1), (2024, 0)])
def test_only_score_matching_observed_competition_year_is_excluded(pair):
    row = dict(ROWS[0], hs=pair[0], gs=pair[1])
    assert snapshot(connection([row]))[3][cc._remine_key(row)]['ft'] == pair


def test_bad_donor_does_not_veto_a_clean_independent_result_or_prediction():
    bad = ROWS[0]
    clean = dict(bad, hs=1, gs=0, p1=.8, px=.1, p2=.1)
    con = connection([bad], [clean])
    _, observations, _, resolved, _ = snapshot(con)
    key = cc._remine_key(clean)
    assert resolved[key]['ft'] == (1, 0)
    assert observations[(key, '1x2')]['scoutingstats']['probs']['home'] == .8
    assert cc._enhancement_archive(con, '2026-06-13', '2026-11-06', resolved, {}).rows[0]['gs'] == 0


def test_half_time_is_separate_and_duplicate_rejection_audit_is_order_stable():
    bad = dict(ROWS[0], ht_hs=0, ht_gs=0)
    good = dict(ROWS[1], hs=1, gs=0, ht_hs=2025, ht_gs=2026)
    results = [snapshot(connection(rows)) for rows in ([bad, good, bad], [good, bad, bad])]
    assert results[0][0] == results[1][0]
    assert results[0][3] == results[1][3]
    coverage, _, _, resolved, _ = results[0]
    assert resolved[cc._remine_key(bad)]['ht'] == (0, 0)
    assert 'ft' not in resolved[cc._remine_key(bad)]
    assert resolved[cc._remine_key(good)]['ft'] == (1, 0)
    assert 'ht' not in resolved[cc._remine_key(good)]
    assert coverage['betexplorer']['score_admission']['excluded_by_period'] == {'ft': 2, 'ht': 1}


def test_reviewed_result_still_restores_authentic_score(monkeypatch):
    from edgefactory import settlement
    bad = ROWS[0]
    monkeypatch.setattr(settlement, 'load_verified_results', lambda: [dict(
        date=bad['date'], home=bad['home'], away=bad['away'], hs=1, gs=0,
        verified_at='2026-11-05', outcome='home')])
    assert snapshot(connection([bad]))[3][cc._remine_key(bad)]['ft'] == (1, 0)


def recipe():
    r = dict(sources=['scoutingstats'], market='1x2', strategy='single',
        follow_source=None, threshold=65, status='certified',
        mining_window=dict(start='2026-06-13', split='2026-09-01',
                           as_of_exclusive='2026-10-01'),
        activated_as_of='2026-10-01', contract_schema=cc.SCHEMA)
    ident = cc.contract_identity(r)
    return dict(r, contract_id=ident, rule=ident, view=ident, where='1=1')


def fitting_inputs():
    # Synthetic fit population; real contaminated donor remains exact fixture bytes.
    # Prior clean scores establish sufficient form; same-day labels never enter it.
    prior = [dict(date=f'2026-09-{i:02d}', home='Bitam', away=f'Prior Team {i}',
                  hs=2, gs=1, match_url='') for i in range(1, 7)]
    prior += [dict(date=f'2026-09-{i:02d}', home='Clean Home', away=f'Clean Prior {i}',
                   hs=1, gs=2, match_url='') for i in range(1, 7)]
    train = [dict(date='2026-09-10', home='Bitam' if i % 2 else 'Clean Home', away=f'Fit Team {i}',
                  hs=2 if i % 2 else 0, gs=0 if i % 2 else 1,
                  p1=.7 + (i % 3) / 100, px=.1, p2=.2 - (i % 3) / 100)
             for i in range(120)]
    return prior, train


def test_actual_fit_excludes_bad_history_without_rewriting_training_targets(monkeypatch):
    prior, train = fitting_inputs()
    bad = ROWS[0]
    con = connection(prior + [bad], train)
    corrected = cc.enhancement_cohort(con, recipe(), as_of='2026-11-06', selection='home', fit_ml=True)
    assert corrected['ml_status'] == 'fitted'
    assert corrected['ml_model']['n'] == 120
    assert corrected['ml_model']['feature_means']['home_form_ga'] == 1.5
    monkeypatch.setattr(cc, '_betexplorer_score_is_competition_metadata', lambda *args: False)
    before = cc.enhancement_cohort(con, recipe(), as_of='2026-11-06', selection='home', fit_ml=True)
    assert before['ml_model']['feature_means']['home_form_ga'] == pytest.approx(((6 + 2025) / 7 + 2) / 2)
    assert before['ml_model']['classes'] == corrected['ml_model']['classes']
    assert before['ml_model']['n'] == corrected['ml_model']['n']
    assert before['ml_model']['model_key'] != corrected['ml_model']['model_key']
    assert corrected['result_score_admission']['excluded_fixtures'] == 1


def test_uncontaminated_fit_and_main_entire_snapshot_unchanged(monkeypatch):
    prior, train = fitting_inputs()
    con = connection(prior, train)
    corrected = cc.enhancement_cohort(con, recipe(), as_of='2026-11-06', selection='home', fit_ml=True)
    main = cc.collect_observations(con, start='2026-06-13', as_of='2026-11-06')
    monkeypatch.setattr(cc, '_betexplorer_score_is_competition_metadata', lambda *args: False)
    baseline = cc.enhancement_cohort(con, recipe(), as_of='2026-11-06', selection='home', fit_ml=True)
    assert corrected == baseline
    assert cc.collect_observations(con, start='2026-06-13', as_of='2026-11-06') == main
    unsigned = {k:v for k,v in corrected['ml_model'].items() if k != 'model_key'}
    assert hashlib.sha256(json.dumps(unsigned, sort_keys=True, allow_nan=False).encode()).hexdigest() == corrected['ml_model']['model_key']
