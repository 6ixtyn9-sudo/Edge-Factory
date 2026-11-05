"""Mechanical replay is NOT statistical validation of this suspect forecast.

The fixture retains an actual frozen model/inputs and normalized quote rows.
No native OddsPapi body was retained here: these tests cannot certify its
original market mapping, the score forecast's accuracy or a tradable edge.
"""

import csv
import gzip
import hashlib
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from test_ml_paper import candidate, receipt

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp
from edgefactory.consensus_contracts import enhancement_feature_vector
from edgefactory.enh_pricing import load_prices_index
from edgefactory.enh_registry import enhancement_ml_score_weights
from edgefactory.util import norm_team


@pytest.fixture
def evidence():
    return json.loads((Path(__file__).parent / 'fixtures/ml_outlier_2026-11-04.json').read_text())


def bound_pick(evidence):
    c, m = evidence['candidate'], evidence['model']
    return {
        'date': c['date'], 'home': c['home'], 'away': c['away'], 'sport': 'soccer',
        'pick': m['selection'], 'market': 'ou_2.5', 'bucket': c['bucket'],
        'league': 'Synthetic replay context; league was not retained in this candidate',
        'avg_p': 100 * c['ml_inputs']['values']['confidence'], 'contract_id': c['contract_id'],
        'kickoff_utc': c['kickoff_utc'], 'as_of': evidence['source_receipt']['captured_at'],
        'statistical_profile': {'ml_model': m, 'ml_inputs': c['ml_inputs'], 'n': m['n'],
                                 'contract_id': m['contract_id'], 'selection': m['selection'],
                                 'as_of_exclusive': m['as_of_exclusive']},
    }


def test_actual_multifeature_score_distribution_matches_native_sklearn(evidence):
    """Catch serialization, feature standardization and softmax interpretation errors."""
    before = deepcopy(evidence)
    m = evidence['model']
    native = LogisticRegression()
    native.classes_ = np.array(m['classes'])
    native.coef_ = np.array(m['coef'])
    native.intercept_ = np.array(m['intercept'])
    vector = enhancement_feature_vector(evidence['candidate']['ml_inputs']['values'], m)
    native.n_features_in_ = len(vector)
    expected = native.predict_proba([vector])[0]
    weights = enhancement_ml_score_weights(bound_pick(evidence))
    assert weights is not None
    total = sum(w for _, _, w in weights)
    assert [w / total for _, _, w in weights] == pytest.approx(expected, abs=1e-12)
    assert [f'{h}:{a}' for h, a, _ in weights] == m['classes']
    # Independent outcome predicate, not a second call to the shared hit helper.
    away_four_plus = sum(p for label, p in zip(m['classes'], expected) if int(label.split(':')[1]) >= 4)
    assert away_four_plus == pytest.approx(evidence['candidate']['base_probability'], abs=1e-12)
    assert mp.probability(weights, 'away_over_35', 'over') == pytest.approx(away_four_plus)
    assert evidence == before


def test_learning_reduced_not_created_this_extreme_forecast(evidence):
    before = deepcopy(evidence)
    c = deepcopy(evidence['candidate'])
    c['probability'] = c['base_probability']
    mp.apply_learning([c], evidence['learning'])
    assert c['probability'] == pytest.approx(evidence['candidate']['probability'], abs=1e-12)
    assert c['probability'] < c['base_probability']
    assert c['base_probability'] > 9 * (1 / c['odds'])
    assert evidence == before


def write_archive(tmp_path, evidence):
    rows = evidence['normalized_quote_witnesses']
    path = tmp_path / 'localdata/oddspapi_odds_2026-11.csv.gz'
    path.parent.mkdir()
    with gzip.open(path, 'wt', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_actual_legacy_bookings_rows_cannot_price_new_decisions(tmp_path, monkeypatch, evidence):
    monkeypatch.setenv('EDGE_FACTORY_ODDSPAPI_PRICES', '1')
    path = write_archive(tmp_path, evidence)
    before = path.read_bytes()
    row = bound_pick(evidence)
    index = load_prices_index(tmp_path, row['date'])
    assert index['fixture_quotes'] == {}
    cs, _, _ = mp.candidates(
        [row], row['date'], datetime.fromisoformat(row['as_of']), index,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection, min_leg_odds=1.0,
    )
    assert cs == []
    assert path.read_bytes() == before


def test_current_goals_quote_retains_provider_lineage_without_altering_price(tmp_path, monkeypatch, evidence):
    """Synthetic current-generation goal quotes, NOT rehabilitated historical bookings."""
    monkeypatch.setenv('EDGE_FACTORY_ODDSPAPI_PRICES', '1')
    goal_rows = evidence['normalized_quote_witnesses']
    for row in goal_rows:
        row.update(schema_version='4', outcome_key='synthetic-goal-outcome',
                   bookmaker_market_id='synthetic-book-market', provider_market_id='synthetic-goal-market',
                   provider_market_name='Over Under Full Time' if row['market'].startswith('ou_') else 'Over Under Team 2',
                   provider_market_type='totals' if row['market'].startswith('ou_') else 'teamtotals-team2',
                   provider_period='fulltime')
    path = write_archive(tmp_path, evidence)
    before = path.read_bytes()
    row = bound_pick(evidence)
    index = load_prices_index(tmp_path, row['date'])
    cs, _, rejected = mp.candidates(
        [row], row['date'], datetime.fromisoformat(row['as_of']), index,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection, min_leg_odds=1.0,
    )
    assert {c['market']: c['odds'] for c in cs} == {'match_over_35': 2.2, 'away_over_35': 19.0}, rejected
    for c in cs:
        proof = c['price_provenance']
        witness = proof['row']
        assert proof['schema'] == 'normalized_odds_quote_v1'
        assert proof['evidence_scope'] == 'normalized_archive_row_not_native_provider_payload'
        assert proof['archive'] == path.name
        assert witness in goal_rows
        assert witness['market'] == ('tt_away_3.5' if c['market'] == 'away_over_35' else 'ou_3.5')
        assert witness['selection'] == c['selection'] == 'over'
        assert float(witness['odds']) == c['odds']
        assert (witness['home'], witness['away']) == (c['home'], c['away'])
        assert witness['captured_at'] == c['price_at']
        assert proof['row_sha256'] == hashlib.sha256(json.dumps(
            witness, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False,
        ).encode()).hexdigest()
    assert path.read_bytes() == before
    key = (norm_team(row['home']), norm_team(row['away']))
    assert index['pairs'][key][('tt_away_3.5', 'over')][:2] == (19.0, 'bet365')
    for slots in index['fixture_quotes'].values():
        for quotes in slots.values():
            quotes[:] = [(*q[:5], None, q[6]) for q in quotes]
    legacy, _, _ = mp.candidates(
        [row], row['date'], datetime.fromisoformat(row['as_of']), index,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection, min_leg_odds=1.0,
    )
    assert legacy == []  # Missing generation witness is never new supply.


def test_audit_exposes_base_learning_move_and_price_break_even_without_mutation(evidence):
    c = evidence['candidate']
    second = candidate(2, date=c['date'], book=c['book'])
    r = receipt(c['date'], [c, second], [{
        'legs': [c, second], 'odds': c['odds'] * second['odds'], 'stake_units': 1.0, 'book': c['book'],
    }])
    r['captured_at'] = evidence['source_receipt']['captured_at']
    before = deepcopy(r)
    compact = mp.render_daily_card([r])
    audit = mp.render_daily_card([r], audit=True)
    assert 'base 51.4% → adjusted 49.3% · learning move -2.2 pp' in audit
    assert 'price break-even 5.3% (1/odds, not a fair probability or proof of value)' in audit
    assert 'base 51.4%' not in compact  # Preserve the compact daily UX.
    assert r == before
    del c['base_probability']
    assert 'base probability unavailable' in mp.render_daily_card([r], audit=True)


@pytest.mark.parametrize('base,adjusted,label', [
    (.8, .6, 'adjusted worse on both metrics'),
    (.6, .8, 'adjusted better on both metrics'),
    (.8, .8, 'unchanged errors'),
])
def test_forward_report_shows_paired_base_and_adjusted_errors(base, adjusted, label):
    cs = [candidate(i, p=base) for i in (1, 2)]
    for c in cs:
        c['probability'] = adjusted
    r = receipt(cs[0]['date'], cs, [{'legs': cs, 'odds': 4., 'stake_units': 1., 'book': cs[0]['book']}])
    report = mp.performance([r], lambda c: (2, 0))
    before = deepcopy((r, report))
    text = mp.render_performance(report)
    assert f'FORWARD POOL: Brier {(base - 1) ** 2:.4f} → {(adjusted - 1) ** 2:.4f}' in text
    assert 'FORWARD SELECTED: Brier' in text
    assert text.count(label) == 2
    assert '2 fixtures / 2 observations' in text
    assert 'descriptive, not significance or a policy gate' in text
    assert (r, report) == before


def test_unresolved_forward_errors_are_not_reported_as_success():
    c = candidate(1)
    report = mp.performance([receipt(c['date'], [c])], lambda c: None)
    text = mp.render_performance(report)
    assert 'FORWARD POOL: no resolved paired base/adjusted errors yet' in text
    assert 'FORWARD SELECTED: no resolved paired base/adjusted errors yet' in text
    assert 'adjusted better' not in text and 'unchanged errors' not in text


@pytest.mark.parametrize('field,value', [
    ('schema_version', '2'),
    ('captured_at', '2026-11-03T13:18:30+00:00'),
    ('captured_at', '2026-11-04T18:18:30+00:00'),
    ('source', 'other_source'),
])
def test_quote_witness_does_not_relax_existing_archive_admission(tmp_path, monkeypatch, evidence, field, value):
    monkeypatch.setenv('EDGE_FACTORY_ODDSPAPI_PRICES', '1')
    for row in evidence['normalized_quote_witnesses']:
        row['schema_version'] = '4'
        row[field] = value
    write_archive(tmp_path, evidence)
    assert load_prices_index(tmp_path, evidence['candidate']['date'])['fixture_quotes'] == {}


def test_quote_witness_does_not_enable_flagged_off_source(tmp_path, evidence):
    write_archive(tmp_path, evidence)
    assert load_prices_index(tmp_path, evidence['candidate']['date'])['fixture_quotes'] == {}


@pytest.mark.parametrize('path', ['primary', 'board', 'fixture_index'])
@pytest.mark.parametrize('generation,allowed', [(None, False), ('3', False), ('4', True)])
def test_unproven_legacy_context_cannot_bypass_current_store_floor(path, generation, allowed):
    from test_ml_paper import DAY, NOW, pick, synthetic_oddspapi_provenance
    from test_ml_paper_freshness import offer
    row = pick()
    row['odds_source'] = 'oddspapi'
    proof = synthetic_oddspapi_provenance(row) if generation is not None else None
    if proof:
        proof['row']['schema_version'] = generation
    row['odds_provenance'] = proof
    index = {}
    if path == 'board':
        row['price_board'] = [offer(row, 'oddspapi', row['odds_captured_at'])]
        row['odds'] = None
    elif path == 'fixture_index':
        pair = (norm_team(row['home']), norm_team(row['away']))
        index = {'fixture_quotes': {pair: {('ou_2.5', 'over'): [
            (2., 'Pinnacle', row['odds_captured_at'], 'oddspapi', row['kickoff_utc'], proof,
             (row['home'], row['away'])),
        ]}}}
        row['odds'] = None
    cs, _, _ = mp.candidates(
        [row], DAY, NOW, index, kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection, min_leg_odds=1.,
    )
    assert bool(cs) is allowed


def test_legacy_unfrozen_draft_cannot_publish_after_parser_boundary(tmp_path):
    from test_ml_paper import DAY, FREEZE, context, pick, run_capture
    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    state = json.loads(mp.state_path(tmp_path).read_text())
    pending = state['pending_by_date'][DAY]
    for c in [*pending['candidates'], *(c for a in pending['accas'] for c in a['legs'])]:
        c.update(price_source='oddspapi', price_provenance=None)
    pending['sha256'] = mp.digest({k: v for k, v in pending.items() if k != 'sha256'})
    mp.state_path(tmp_path).write_text(json.dumps(state))
    before = mp.state_path(tmp_path).read_bytes()
    assert draft['accas']
    assert run_capture(tmp_path, {}, now=FREEZE) is None
    assert not mp.receipt_path(tmp_path, DAY).exists()
    assert mp.state_path(tmp_path).read_bytes() == before


def test_production_writer_refuses_legacy_quote_but_frozen_history_stays_readable(tmp_path):
    from test_ml_paper import DAY, capture
    r = capture(tmp_path)
    for c in [*r['candidates'], *(c for a in r['accas'] for c in a['legs'])]:
        c.update(price_source='oddspapi', price_provenance=None)
    r['sha256'] = mp.digest({k: v for k, v in r.items() if k != 'sha256'})
    path = tmp_path / 'hypothetical-new-receipt.json'
    with pytest.raises(ValueError, match='OddsPapi parser generation'):
        mp._publish_receipt(path, r)
    assert not path.exists()
    # Low-level historical replay remains byte-preserving/readable, not a
    # production writer or permission to make a new bet with these quotes.
    historical = tmp_path / 'historical.json'
    assert mp._write_once(historical, r)
    before = historical.read_bytes()
    mp.validate_record(json.loads(before), DAY)
    assert historical.read_bytes() == before


@pytest.mark.parametrize('selection,outcome', [('home', '101'), ('draw', '102'), ('away', '103')])
def test_current_generation_index_preserves_healthy_1x2_supply(tmp_path, monkeypatch, evidence, selection, outcome):
    """Requiring lineage must not silently ban OddsPapi's supported 1X2 market."""
    monkeypatch.setenv('EDGE_FACTORY_ODDSPAPI_PRICES', '1')
    row = dict(evidence['normalized_quote_witnesses'][0], market='1x2', selection=selection, odds='2.0',
               schema_version='4', outcome_key=outcome, provider_market_id='101',
               provider_market_name='Full Time Result', provider_market_type='1x2', provider_period='fulltime')
    evidence['normalized_quote_witnesses'] = [row]
    write_archive(tmp_path, evidence)
    pick_row = bound_pick(evidence)
    cs, _, _ = mp.candidates(
        [pick_row], pick_row['date'], datetime.fromisoformat(pick_row['as_of']),
        load_prices_index(tmp_path, pick_row['date']), kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection, min_leg_odds=1.,
    )
    assert len(cs) == 1
    c = cs[0]
    assert (c['market'], c['selection'], c['odds']) == ('1x2', selection, 2.)
    assert c['price_provenance']['row'] == row
