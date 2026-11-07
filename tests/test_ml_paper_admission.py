"""Current-policy adversarial tests, distinct from pre-policy financial replay.

All fixtures below are synthetic. Counts are unique fixtures, never books.
No stubs disable admission, publication validation, or the portfolio allocator.
"""
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import json
import math

import pytest

from edgefactory import ml_paper as mp
from edgefactory.consensus_contracts import enhancement_fixture_identity
import scripts.auto_tickets as at
from test_ml_paper import candidate, pick, receipt

NOW = datetime(2026, 11, 8, 6, tzinfo=UTC)
PAST = '2026-11-06'


def history(n=120, *, btts=False, p=.7):
    rows = []
    for i in range(n):
        c = candidate(10000+i, date=PAST, p=p)
        c.update(price_source='pinnapi_odds', price_at=PAST+'T06:00:00Z')
        if btts:
            c['ml_inputs']['values']['forecast_btts_yes_mean'] = p
            other = deepcopy(c)
            other.update(candidate_id='btts-'+c['candidate_id'], market='btts_yes', selection='yes')
            rows.append(other)
        rows.append(c)
    return [receipt(PAST, rows)]


def score(c):
    return (2, 0) if c['date'] == PAST else None


def next_candidate(i=1, *, p=.7, odds=2., market='1x2', side='home'):
    c = candidate(i, date=NOW.date().isoformat(), p=p, odds=odds)
    c.update(price_source='pinnapi_odds', price_at=NOW.isoformat(), market=market, selection=side)
    if market == 'btts_yes':
        c['ml_inputs']['values']['forecast_btts_yes_mean'] = p
    c['base_partition'] = mp._base_partition(c['ml_inputs'], market)
    c['base_probability'] = mp.probability(c['ml_inputs'], market, side)
    return c


def predicted(rows, h=None, lookup=score):
    model = mp.learn(history() if h is None else h, NOW, lookup)
    mp.apply_learning(rows, model)
    mp.apply_admission(rows, json.loads(json.dumps(model)))
    return model


def current_pick(i):
    r = pick(i)
    r.update(date=NOW.date().isoformat(), as_of=NOW.isoformat(),
             kickoff_utc=(NOW+timedelta(hours=4)).isoformat(),
             odds_captured_at=NOW.isoformat())
    r['statistical_profile']['as_of_exclusive'] = r['date']
    r['statistical_profile']['ml_inputs']['fixture'] = enhancement_fixture_identity(r)
    return r


def freeze(root, *, h=None, rows=None, now=NOW, clock=None):
    if h:
        for r in h:
            r = deepcopy(r)
            r['sha256'] = mp.digest(r)
            assert mp._write_once(mp.receipt_path(root, r['date']), r)
    return mp.capture_rolling(
        {'build_at': now.isoformat(), 'slate': [current_pick(1), current_pick(2)] if rows is None else rows},
        root=root, score_lookup=score, kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection, index={}, now=now if clock is None else None,
        **({} if clock is None else {'clock': clock}))


def test_current_cold_start_publishes_forecasts_but_no_bank_exposure(tmp_path):
    before = [current_pick(1), current_pick(2)]
    unchanged = deepcopy(before)
    r = freeze(tmp_path, rows=before)
    assert before == unchanged
    assert r['candidates'] and not r['accas'] and r['status'] == 'no_paper_bet'
    assert all(c['admission']['reason'] == 'no_local_evidence' for c in r['candidates'])
    assert all(c['context']['schema'] == 'source_market_context_v2' for c in r['candidates'])
    assert r['policy']['admission'] == mp.ADMISSION_POLICY
    assert mp.receipts(tmp_path) == [r]
    assert 'no local evidence' in mp.render_card(r)
    report = mp.performance([r], lambda c: None)
    assert report['paper_bank_units'] == report['paper_free_units'] == 100
    assert report['paper_committed_units'] == 0


def test_supported_current_publication_exercises_allocator_and_original_bank_caps(tmp_path):
    r = freeze(tmp_path, h=history())
    assert r['accas'] and all(c['admission']['status'] == 'eligible' for c in r['candidates'])
    assert r['paper_bank_at_decision'] == 100  # warm-up forecasts staked nothing
    assert sum(a['stake_units'] for a in r['accas']) <= 25
    assert all(a['stake_units'] <= 5 for a in r['accas'])
    for a in r['accas']:
        assert a['probability_basis'] == mp.ADMISSION_JOINT_BASIS
        assert a['probability_estimate'] < a['model_probability_estimate']
        assert a['estimated_ev'] > 0
    assert len(mp.receipts(tmp_path)) == 2
    text = mp.render_card(r)
    assert 'Joint admission envelope' in text and 'required source probability' in text


@pytest.mark.parametrize('p', [.08, .60, .99])
def test_no_fixed_probability_overrides_absent_evidence(p):
    c = next_candidate(p=p, odds=100.)
    predicted([c], h=[])
    assert c['admission']['status'] == 'abstain'
    assert c['admission']['probability_lower'] == 0
    assert c['probability'] > 0  # point estimate remains separately visible


def test_market_specific_performance_not_overall_win_rate_controls_admission():
    home, btts = next_candidate(1), next_candidate(2, market='btts_yes', side='yes')
    predicted([home, btts], history(btts=True))
    assert home['admission']['fixtures'] == btts['admission']['fixtures'] == 120
    assert home['admission']['wins'] == 120 and btts['admission']['wins'] == 0
    assert home['admission']['status'] == 'eligible'
    assert btts['admission']['status'] == 'abstain'
    assert home['admission']['required_source_probability'] < .7
    assert btts['admission']['required_source_probability'] > .7


def test_sparse_perfect_run_is_not_certification_and_evidence_accumulates():
    low, high = next_candidate(1), next_candidate(2)
    predicted([low], history(n=3))
    predicted([high], history(n=120))
    assert low['admission']['wins'] == low['admission']['fixtures'] == 3
    assert low['admission']['status'] == 'abstain'
    assert high['admission']['status'] == 'eligible'
    assert high['admission']['required_source_probability'] < low['admission']['required_source_probability']


def test_probability_band_price_band_and_source_cohort_cannot_borrow_other_cells():
    known = next_candidate(1)
    different_p = next_candidate(2, p=.08, odds=20)
    different_price = next_candidate(3, odds=10)
    different_source = next_candidate(4)
    different_source['ml_inputs']['sources'] = ['vitibet']
    predicted([known, different_p, different_price, different_source])
    assert known['admission']['status'] == 'eligible'
    assert all(c['admission']['fixtures'] == 0 and c['admission']['status'] == 'abstain'
               for c in (different_p, different_price, different_source))


def test_fitted_optimism_is_not_used_as_validation_evidence():
    c = next_candidate(p=.08, odds=20)
    model = mp.learn(history(n=120, p=.08), NOW, score)
    mp.apply_learning([c], model)
    # Deliberately exaggerate the fitted point. Admission can never treat it
    # as 120 correctly forecast high-confidence predictions.
    c['probability'] = .999
    mp.apply_admission([c], model)
    assert c['admission']['source_probability'] == pytest.approx(.08)
    assert c['admission']['probability_lower'] <= .08


def test_book_snapshot_and_complement_replication_never_manufacture_fixture_counts():
    original = history(n=8)
    replicated = deepcopy(original)
    replicated[0]['candidates'] += [dict(c, candidate_id=f'zz-{i}-{c["candidate_id"]}', book=f'Book{i}')
                                     for c in original[0]['candidates'] for i in range(30)]
    a = mp.learn(original, NOW, score)
    b = mp.learn(replicated+deepcopy(replicated), NOW, score)
    assert a['admission'] == b['admission']
    assert all(cell['fixtures'] == 8 for cell in b['admission']['cells'].values())


def test_uncaptured_opposite_price_is_not_invented_as_validation_evidence():
    model = mp.learn(history(), NOW, score)
    c = next_candidate(side='away')
    mp.apply_learning([c], model)
    mp.apply_admission([c], model)
    assert c['admission']['fixtures'] == 0  # source partition is complete, quote board isn't


def test_unknown_and_same_day_results_are_not_losses_or_validation_evidence():
    c = next_candidate()
    predicted([c], history(), lambda c: None)
    assert c['admission']['fixtures'] == 0
    future = history(n=5)
    future[0].update(date=NOW.date().isoformat(), captured_at=NOW.isoformat(), persisted_at=NOW.isoformat())
    model = mp.learn(history(n=5)+future, NOW, score)
    assert all(v['fixtures'] == 5 for v in model['admission']['cells'].values())


def admitted_rows(n, p, odds):
    # Synthetic, explicitly labelled helper evidence to isolate the ticket
    # arithmetic. Full real gate/publication paths are exercised above.
    rows = [next_candidate(i, p=p, odds=odds) for i in range(n)]
    for c in rows:
        c['admission'] = dict(policy=mp.ADMISSION_POLICY, status='eligible', probability_lower=p)
    return rows


def test_five_sixty_percent_legs_cannot_create_an_eight_percent_lottery_ticket():
    rows = admitted_rows(5, .6, 2.)
    proposals = mp.acca_proposals(rows)
    # Even pairs have lower joint envelope .2, with odds 4: not positive EV.
    assert proposals == []
    assert math.prod(c['probability'] for c in rows) == pytest.approx(.07776)


def test_conservative_ticket_probability_drives_growth_and_quarter_kelly():
    rows = admitted_rows(2, .8, 2.)
    plan = mp.select_accas(rows, 100., concentration={'total_bank_units': 100.,
                                                   'prior_open_fixture_micro_units': {}})
    assert plan
    a = plan[0]
    assert a['probability_estimate'] == pytest.approx(.6)
    assert a['model_probability_estimate'] == pytest.approx(.64)
    assert a['estimated_ev'] == pytest.approx(1.4)
    assert a['model_kelly_fraction'] == pytest.approx((.6*4-1)/3)
    assert a['stake_units'] <= 5  # original fixture cap still wins


def test_mixed_undeclared_candidates_cannot_enter_gated_search():
    rows = admitted_rows(2, .8, 2.)
    del rows[1]['admission']
    with pytest.raises(ValueError, match='mixed declared'):
        mp.acca_proposals(rows)


@pytest.mark.parametrize('damage', ['candidate', 'counts', 'policy', 'learner', 'basis', 'joint'])
def test_rehashing_outer_receipt_cannot_bypass_gate_or_joint_risk(tmp_path, damage):
    r = freeze(tmp_path, h=history())
    bad = deepcopy(r)
    if damage == 'candidate':
        bad['candidates'][0]['admission']['probability_lower'] = .999
    elif damage == 'counts':
        cell = next(iter(bad['learning']['admission']['cells'].values()))
        cell['fixtures'] *= 100
        bad['learning']['model_key'] = mp.digest({k: v for k, v in bad['learning'].items() if k != 'model_key'})
    elif damage == 'policy':
        del bad['policy']['admission']
    elif damage == 'learner':
        del bad['learning']['admission']
    elif damage == 'basis':
        bad['accas'][0]['probability_basis'] = 'product_assumes_cross_fixture_independence_not_validated'
    else:
        bad['accas'][0]['probability_estimate'] = bad['accas'][0]['model_probability_estimate']
    bad['sha256'] = mp.digest({k: v for k, v in bad.items() if k != 'sha256'})
    with pytest.raises(ValueError):
        mp.validate_record(bad, bad['date'])


def test_production_writer_refuses_undeclared_new_position_even_if_reader_markers_are_stripped(tmp_path):
    r = freeze(tmp_path, h=history())
    bad = deepcopy(r)
    del bad['policy']['admission']
    bad['sha256'] = mp.digest({k: v for k, v in bad.items() if k != 'sha256'})
    with pytest.raises(ValueError, match='admission'):
        mp._publish_receipt(tmp_path/'not-published.json', bad)
    assert not (tmp_path/'not-published.json').exists()


def test_unavailable_uncertainty_fails_atomically_not_as_a_permissive_fallback(monkeypatch):
    import scipy.stats
    rows = [next_candidate(1), next_candidate(2)]
    model = mp.learn(history(), NOW, score)
    mp.apply_learning(rows, model)
    before = deepcopy(rows)
    monkeypatch.setattr(scipy.stats.beta, 'ppf', lambda *a: float('nan'))
    with pytest.raises(ValueError, match='uncertainty unavailable'):
        mp.apply_admission(rows, model)
    assert rows == before


def test_source_cell_evidence_uses_actual_quote_bands_not_a_synthetic_median_price():
    h = history(n=5)
    first = h[0]['candidates'][0]
    first['odds'] = 1.4
    h[0]['candidates'].append(dict(first, candidate_id='other-price', odds=2.4, book='Other'))
    model = mp.learn(h, NOW, score)
    bands = {v['odds_band'] for v in model['admission']['cells'].values()}
    assert '1.30-1.49' in bands and '2.20-2.99' in bands
    assert all(v['fixtures'] <= 5 for v in model['admission']['cells'].values())


def test_activation_boundary_is_explicit_and_preserves_prepolicy_decision_replay():
    old = NOW.replace(year=2026, month=11, day=6)
    new = NOW.replace(year=2026, month=11, day=7)
    assert 'admission' not in mp.learn([], old, lambda c: None)
    assert 'admission' in mp.learn([], new, lambda c: None)
    assert mp._candidate_context(current_pick(1), old)['schema'] == 'source_market_context_v1'
    assert mp._candidate_context(current_pick(1), new)['schema'] == 'source_market_context_v2'


def test_better_prices_lower_the_derived_requirement_only_within_supported_price_band():
    a, b = next_candidate(1, odds=2.), next_candidate(2, odds=2.1)
    predicted([a, b])
    assert a['admission']['fixtures'] == b['admission']['fixtures'] == 120
    assert b['admission']['required_source_probability'] < a['admission']['required_source_probability']
    assert all(c['admission']['required_source_probability'] >= 1/c['odds'] for c in (a, b))


def test_new_losses_raise_the_requirement_instead_of_selecting_a_winning_subset():
    good, worse = next_candidate(1), next_candidate(2)
    predicted([good])
    def mixed(c):
        if c['date'] != PAST:
            return None
        return (2, 0) if int(c['candidate_id']) % 3 else (0, 2)
    predicted([worse], lookup=mixed)
    assert worse['admission']['fixtures'] == 120
    assert worse['admission']['wins'] == 80
    assert worse['admission']['required_source_probability'] > good['admission']['required_source_probability']
    assert worse['admission']['status'] == 'abstain'


@pytest.mark.parametrize('kind', ['future', 'stale', 'fair', 'old_generation', 'conflict', 'unbound'])
def test_ineligible_quote_inventory_is_not_validation_support(kind):
    h = history(n=5)
    for c in h[0]['candidates']:
        if kind == 'future':
            c['price_at'] = PAST+'T08:00:00Z'
        elif kind == 'stale':
            c['price_at'] = '2026-11-05T06:00:00Z'
        elif kind == 'fair':
            c['price_source'] = 'betbetter'
        elif kind == 'old_generation':
            c.update(price_source='oddspapi', price_provenance=None)
        elif kind == 'unbound':
            c['home'] = 'Different Club'
    if kind == 'conflict':
        h[0]['candidates'] += [dict(c, candidate_id='conflict-'+c['candidate_id'], odds=3)
                                for c in list(h[0]['candidates'])]
    model = mp.learn(h, NOW, score)
    assert model['admission']['cells'] == {}


def test_later_winning_snapshot_cannot_replace_earliest_forecast_or_price_band():
    early = history(n=5)
    later = deepcopy(early)
    later[0]['captured_at'] = PAST+'T08:00:00Z'
    later[0]['persisted_at'] = PAST+'T09:00:00Z'
    for c in later[0]['candidates']:
        c.update(price_at=PAST+'T08:00:00Z', odds=10)
        c['ml_inputs']['values']['forecast_1x2_home_mean'] = .99
        c['ml_inputs']['values']['forecast_1x2_draw_mean'] = .005
        c['ml_inputs']['values']['forecast_1x2_away_mean'] = .005
    a = mp.learn(early, NOW, score)
    b = mp.learn(later+early, NOW, score)
    assert a['admission'] == b['admission']


def test_fixed_namespace_and_repeated_look_error_budget_are_not_roi_tuned():
    m = mp.learn(history(n=3), NOW, score)['admission']
    assert m['cell_budget'] == 17_692_560  # v1: 36 events x 10 deciles x 6 bands x 8191 source sets
    assert m['alpha'] == .05
    assert sum(1/(n*(n+1)) for n in range(1, 10000)) < 1
    assert 'not_verified' in m['assumptions']


@pytest.mark.parametrize('lower', [True, None, -.01, 1.01, float('nan'), float('inf')])
def test_bad_candidate_envelopes_are_rejected_before_search(lower):
    rows = admitted_rows(2, .8, 2.)
    rows[0]['admission']['probability_lower'] = lower
    with pytest.raises(ValueError):
        mp.acca_proposals(rows)


def test_new_reader_witnesses_survive_policy_and_learner_declaration_stripping(tmp_path):
    r = freeze(tmp_path)
    bad = deepcopy(r)
    del bad['policy']['admission']
    del bad['learning']['admission']
    for c in bad['candidates']:
        del c['admission']
    # Owned input schema v2 is itself a witness, even with no ticket.
    assert all(m['schema'] == 'source_market_context_v2' for m in bad['models'].values())
    with pytest.raises(ValueError, match='declared policy'):
        mp._validate_admission(bad)


def test_gate_inventory_remains_learnable_when_prior_decisions_abstained(tmp_path):
    first = freeze(tmp_path)
    assert not first['accas']
    tomorrow = NOW + timedelta(days=1)
    model = mp.learn([first], tomorrow, lambda c: (2, 0))
    assert model['fixtures'] == 2
    assert any(cell['fixtures'] == 2 for cell in model['admission']['cells'].values())


def test_supported_current_publication_respects_existing_reserved_fixture_budget(tmp_path):
    first = freeze(tmp_path, h=history())
    assert first['accas']
    later = NOW + timedelta(hours=1)
    rows = [current_pick(1), current_pick(2)]
    for r in rows:
        r.update(as_of=later.isoformat(), odds_captured_at=later.isoformat())
    second = mp.capture_rolling({'build_at': later.isoformat(), 'slate': rows}, root=tmp_path,
        score_lookup=score, kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection, index={}, now=later)
    total = sum(a['stake_units'] for a in first['accas'])
    if second is not None:
        total += sum(a['stake_units'] for a in second['accas'])
    assert total <= 5.000001
    assert mp.receipts(tmp_path)[0]['accas'] == []  # historical warmup remains no-bet
    assert mp.receipts(tmp_path)[1] == first  # prior open positions never resized/refilled


def test_same_quotes_and_forecasts_cannot_refill_with_new_admission_metadata(tmp_path):
    first = freeze(tmp_path, h=history())
    later = NOW + timedelta(minutes=5)
    rows = [current_pick(1), current_pick(2)]
    for r in rows:
        r['as_of'] = later.isoformat()  # original quote timestamps retained
    second = mp.capture_rolling({'build_at': later.isoformat(), 'slate': rows}, root=tmp_path,
        score_lookup=score, kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection, index={}, now=later)
    assert second is not None and not second['accas']
    assert second['search']['opportunity_replay']['dropped_acca_count'] > 0
    assert mp.receipts(tmp_path)[1] == first


@pytest.mark.parametrize('field,bad', [('fixtures', True), ('fixtures', 1.0), ('wins', 1.0)])
def test_integer_count_encoding_cannot_be_replaced_by_bool_or_float(field, bad):
    model = mp.learn(history(n=1), NOW, score)
    cell = next(iter(model['admission']['cells'].values()))
    assert cell[field] == 1
    cell[field] = bad
    model['model_key'] = mp.digest({k: v for k, v in model.items() if k != 'model_key'})
    c = next_candidate()
    mp.apply_learning([c], model)
    with pytest.raises(ValueError, match='admission evidence/model binding'):
        mp.apply_admission([c], model)


def test_roundoff_cannot_manufacture_a_positive_joint_envelope_at_huge_odds():
    rows = [next_candidate(i, p=p, odds=1e6) for i, p in enumerate((.3, .8, .9))]
    for c in rows:
        c['admission'] = dict(policy=mp.ADMISSION_POLICY, status='eligible',
                              probability_lower=c['probability'])
    # Declared decimal lower probabilities sum to exactly two. Three-way
    # Frechet lower envelope is zero, regardless of attractive product odds.
    proposals = mp.acca_proposals(rows)
    assert not any(len(a['legs']) == 3 for a in proposals)


def test_roundoff_cannot_turn_zero_leg_support_into_an_edge_at_huge_odds(monkeypatch):
    import scipy.stats
    h = history(n=120, p=.2)
    for c in h[0]['candidates']:
        c['odds'] = 1e18
    model = mp.learn(h, NOW, score)
    c = next_candidate(p=.2, odds=1e18)
    mp.apply_learning([c], model)
    # Valid, deliberately conservative numeric solver output: decimal lower
    # support .1 plus source .2 minus the band's .3 upper boundary is zero.
    monkeypatch.setattr(scipy.stats.beta, 'ppf', lambda *a: .10000000000001)
    mp.apply_admission([c], model)
    assert c['admission']['probability_lower'] == 0
    assert c['admission']['status'] == 'abstain'


def test_old_draft_cannot_be_late_trained_or_publish_new_ungated_exposure(tmp_path, monkeypatch):
    kwargs = dict(root=tmp_path, score_lookup=score, kickoff_fn=at.parse_kickoff_proven,
                  source_guard=at.execution_source_rejection, index={})
    early = NOW - timedelta(hours=1)
    rows = [current_pick(1), current_pick(2)]
    for row in rows:
        row.update(as_of=early.isoformat(), odds_captured_at=early.isoformat())
    # Real pre-upgrade draft construction, not a forged receipt or a gate stub.
    with monkeypatch.context() as old_release:
        old_release.setattr(mp, 'ADMISSION_ACTIVATED_AS_OF', '2099-01-01')
        mp.capture({'date': NOW.date().isoformat(), 'build_at': early.isoformat(),
                    'slate': rows}, now=early, **kwargs)
    path = mp.state_path(tmp_path)
    before = path.read_bytes()
    draft = mp._read_state(tmp_path)['pending_by_date'][NOW.date().isoformat()]
    assert draft['accas'] and 'admission' not in draft['learning']

    def no_late_training(*args, **kwargs):
        raise AssertionError('old draft must not be refitted to pass the new gate')
    monkeypatch.setattr(mp, 'learn', no_late_training)
    with pytest.raises(ValueError, match='new admission evidence requires declared policy'):
        mp.capture({}, now=NOW+timedelta(hours=2), **kwargs)
    assert path.read_bytes() == before
    assert not mp.receipt_files(tmp_path)
