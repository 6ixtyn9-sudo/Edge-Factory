"""Replacement production path: real quote guards, synthetic source observations."""
from copy import deepcopy
from datetime import timedelta
import json
import math

import pytest
from edgefactory import ml_paper as mp
from test_ml_paper import NOW, DAY, candidate, pick, capture, receipt
from test_ml_paper_dynamic_learning import model
from test_ml_paper_rolling import slate, run


def emitted(i=1):
    row=pick(i)
    inputs=row['statistical_profile']['ml_inputs']
    row['enhancement_source_features']=deepcopy(inputs['values'])
    row['enhancement_feature_sources']=inputs['sources'][:]
    row['enhancement_input_status']='available'
    row.pop('statistical_profile')
    return row


def test_raw_emitted_sources_collect_and_publish_without_any_enh_model(tmp_path):
    rows=[emitted(1),emitted(2)]
    before=deepcopy(rows)
    r=capture(tmp_path,rows)
    assert rows == before
    assert r['accas'] and r['learning']['method'] == 'source_market'
    assert all(m['schema'] == 'source_market_v1' for m in r['models'].values())
    assert all(c['probability'] == pytest.approx(.7) for c in r['candidates'])
    assert mp.receipts(tmp_path) == [r]


@pytest.mark.parametrize('damage',['absent','coef','n','date','schema'])
def test_enh_fitted_state_is_not_a_predictor_or_admission_dependency(tmp_path,damage):
    rows=[pick(1),pick(2)]
    for row in rows:
        profile=row['statistical_profile']
        if damage=='absent':profile.pop('ml_model')
        elif damage=='coef':profile['ml_model']['coef']=[[99999]]
        elif damage=='n':profile['ml_model']['n']=0
        elif damage=='date':profile['ml_model']['train_last_date']='2099-01-01'
        else:profile['ml_model']['schema']='not-a-model'
    r=capture(tmp_path,rows)
    assert r['accas'] and len(r['candidates']) == 2
    assert all(c['probability'] == pytest.approx(.7) for c in r['candidates'])


@pytest.mark.parametrize('damage',['missing_values','missing_sources','unknown_source','duplicate_source',
    'unavailable','wrong_contract','wrong_fixture','nan','probability_scale'])
def test_malformed_sources_cannot_fall_back_to_old_score_model(tmp_path,damage):
    rows=[pick(1),pick(2)]
    for row in rows:
        inputs=row['statistical_profile']['ml_inputs']
        if damage=='missing_values':inputs.pop('values')
        elif damage=='missing_sources':inputs.pop('sources')
        elif damage=='unknown_source':inputs['sources']=['forebet']
        elif damage=='duplicate_source':inputs['sources']=['statarea','statarea']
        elif damage=='wrong_contract':inputs['contract_id']='another'
        elif damage=='wrong_fixture':inputs['fixture'][1]='another'
        elif damage=='nan':inputs['values']['forecast_1x2_home_mean']=float('nan')
        elif damage=='unavailable':
            row['enhancement_source_features']=None
            row['enhancement_input_status']='unavailable'
        else:inputs['values']['forecast_1x2_home_mean']=70
    r=capture(tmp_path,rows)
    assert not r['candidates'] and not r['accas']


@pytest.mark.parametrize('family',['home','away'])
@pytest.mark.parametrize('direction',['over','under'])
@pytest.mark.parametrize('line',['05','15','25','35','45'])
def test_source_model_never_invents_unobserved_team_total_probabilities(family,direction,line):
    inputs=pick()['statistical_profile']['ml_inputs']
    assert mp.probability(inputs,f'{family}_{direction}_{line}',direction) is None


@pytest.mark.parametrize('total',[.94,1.06,2.0])
def test_invalid_complete_1x2_vector_is_not_rescued_by_quote_side_normalization(total):
    inputs=pick()['statistical_profile']['ml_inputs']
    for side in ('home','draw','away'):inputs['values'][f'forecast_1x2_{side}_mean']=total/3
    assert mp.probability(inputs,'1x2','home') is None


def test_binary_complements_and_categorical_dc_remain_coherent():
    inputs=pick()['statistical_profile']['ml_inputs']
    for power in (0.,.4,1.):
        rows=[]
        for side in ('home','draw','away'):
            c=candidate(len(rows)+1);c.update(selection=side)
            c['base_partition']=mp._base_partition(inputs,'1x2')
            c['base_probability']=mp.probability(inputs,'1x2',side)
            rows.append(c)
        for side in ('1x','x2','12'):
            c=candidate(10+len(rows));c.update(market='double_chance',selection=side)
            c['base_partition']=mp._base_partition(inputs,'double_chance')
            c['base_probability']=mp.probability(inputs,'double_chance',side)
            rows.append(c)
        mp.apply_learning(rows,model(power))
        assert sum(c['probability'] for c in rows[:3]) == pytest.approx(1)
        for c,sides in zip(rows[3:],[(0,1),(1,2),(0,2)]):
            assert c['probability'] == pytest.approx(sum(rows[i]['probability'] for i in sides))


def test_retained_real_base_uplift_is_not_inherited_by_replacement(tmp_path):
    r=pick(1);r2=pick(2)
    for row in (r,r2):
        row['odds']=5.02
        row['statistical_profile']['ml_inputs']['values'].update(
            forecast_1x2_home_mean=.218,forecast_1x2_draw_mean=.282,forecast_1x2_away_mean=.5)
    record=capture(tmp_path,[r,r2])
    assert all(c['base_probability'] == pytest.approx(.218) for c in record['candidates'])
    assert all(c['probability'] != pytest.approx(.42232560452787143) for c in record['candidates'])


def test_frozen_replacement_forecast_cannot_be_changed_even_after_resigning(tmp_path):
    r=run(tmp_path)
    for c in r['candidates']:c['probability']+=.001
    for a in r['accas']:
        for c in a['legs']:c['probability']+=.001  # in-memory references may share; both remain inconsistent
    r['sha256']=mp.digest({k:v for k,v in r.items() if k!='sha256'})
    with pytest.raises(ValueError):mp.validate_record(r,r['date'])


def test_training_uses_prior_published_inputs_and_rejects_unknown_source():
    c=candidate(1,date='2026-11-01')
    r=receipt(c['date'],[c])
    r['persisted_at']='2026-11-02T12:00:00+00:00'
    assert mp.learn([r],NOW,lambda c:(2,0))['fixtures'] == 0
    r=receipt(c['date'],[c]);c['ml_inputs']['sources']=['forebet']
    assert mp.learn([r],NOW,lambda c:(2,0))['fixtures'] == 0


def test_training_partition_duplicates_and_complements_do_not_inflate_fixture_count():
    c=candidate(1,date='2026-11-01')
    variants=[c]
    for i,side in enumerate(('home','draw','away')):
        d=deepcopy(c);d.update(candidate_id=str(i+10),selection=side,book=f'Book{i}')
        variants.append(d)
    d=deepcopy(c);d.update(candidate_id='dc',market='double_chance',selection='1x');variants.append(d)
    l=mp.learn([receipt(c['date'],variants)],NOW,lambda c:(2,0))
    assert l['fixtures'] == l['observations'] == 1


def test_training_labels_cannot_leak_from_day_of_decision():
    cs=[candidate(1,date=DAY)]
    def forbidden(c):raise AssertionError('decision-day result leaked')
    l=mp.learn([receipt(DAY,cs)],NOW,forbidden)
    assert l['fixtures'] == 0 and l['power'] == 1


def test_model_serialization_tampering_and_future_cutoff_rejected():
    m=model()
    for changes in ({'power':.1},{'training_last_date':DAY}):
        bad=deepcopy(m);bad.update(changes)
        if 'training_last_date' in changes:bad['model_key']=mp.digest({k:v for k,v in bad.items() if k!='model_key'})
        with pytest.raises(ValueError):mp.apply_learning([candidate(1)],bad)


def test_unused_old_prediction_and_bucket_fields_do_not_admit_or_exclude_training():
    c=candidate(1,date='2026-11-01')
    old=mp.learn([receipt(c['date'],[c])],NOW,lambda c:(2,0))
    c['base_probability']=None
    c.pop('bucket')
    new=mp.learn([receipt(c['date'],[c])],NOW,lambda c:(2,0))
    assert new == old


def test_unused_form_confidence_recipe_noise_does_not_mint_opportunity(tmp_path):
    from test_ml_paper_rolling_residual_budget import modest_edge_slate
    rows=modest_edge_slate()
    first=run(tmp_path,rows=rows)
    stake=first['accas'][0]['stake_units']
    for row in rows:
        row['statistical_profile']['ml_inputs']['values'].update(confidence=.01,home_form_gf=999)
        row['bucket']='SKIPPED_VETO'
    second=run(tmp_path,NOW+timedelta(minutes=2),rows)
    assert second is not None and not second['accas']
    assert mp.performance(mp.receipts(tmp_path),lambda c:None)['paper_committed_units'] == stake
