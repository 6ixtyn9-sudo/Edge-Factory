"""Single low-dimensional source market learner; no old calibration or tilt."""
from copy import deepcopy
from datetime import timedelta
import math

import pytest
from test_ml_paper import NOW, candidate, receipt
from edgefactory import ml_paper as mp

DAY = "2026-11-01"


def model(power=.8):
    m = mp.learn([], NOW, lambda c: None)
    m['power'] = power
    m['model_key'] = mp.digest({k:v for k,v in m.items() if k != 'model_key'})
    return m


def test_one_parameter_fit_from_first_resolved_fixture_and_prior_day_only():
    cs = [candidate(i, date=DAY, p=.8) for i in range(4)]
    l = mp.learn([receipt(DAY,cs)],NOW,lambda c:(0,2))
    assert l['status'] == 'fitted_source_market_temperature'
    assert l['parameters'] == 1 and l['fixtures'] == l['observations'] == 4
    assert 0 < l['power'] < 1
    c = candidate(8,p=.8)
    mp.apply_learning([c],l)
    assert 1/3 < c['probability'] < .8
    assert mp.learn([receipt(NOW.date().isoformat(),cs)],NOW,lambda c:(0,2))['fixtures'] == 0


@pytest.mark.parametrize('p',[.05,.2,.5,.8,.99])
@pytest.mark.parametrize('power',[0.,.25,.5,.75,1.])
def test_temperature_cannot_sharpen_or_reverse_complete_partition(p,power):
    c=candidate(8,p=p)
    before=deepcopy(c)
    mp.apply_learning([c],model(power))
    weights=[v**power for _,_,v in before['base_partition']]
    assert c['probability'] == pytest.approx(weights[0]/sum(weights))
    if power == 1: assert c['probability'] == pytest.approx(p)
    if power == 0: assert c['probability'] == pytest.approx(1/3)
    assert c['base_probability'] == before['base_probability']


def test_no_results_uses_source_anchor_not_old_base_or_neutral_prediction():
    c=candidate(1)
    l=mp.learn([],NOW,lambda c:None)
    assert l['power'] == 1 and l['observations'] == 0
    mp.apply_learning([c],l)
    assert c['probability'] == pytest.approx(.7)
    assert not {'coef','success_tilt','smoothing_factor','columns'} & l.keys()


def test_book_bucket_confidence_old_probabilities_do_not_enter_fit():
    cs=[candidate(i,date=DAY,p=.8) for i in range(6)]
    changed=deepcopy(cs)
    for c in changed:
        c.update(base_probability=.01,probability=.99,bucket='different',odds=99)
        c['ml_inputs']['values'].update(confidence=.01,home_form_gf=999)
    lookup=lambda c:(2,0) if int(c['candidate_id'])%2 else (0,2)
    a=mp.learn([receipt(DAY,cs)],NOW,lookup)
    b=mp.learn([receipt(DAY,changed)],NOW,lookup)
    assert a == b
    duplicated=deepcopy(cs)+[dict(c,book='Other') for c in cs]
    assert mp.learn([receipt(DAY,duplicated)],NOW,lookup) == a


def test_missing_source_never_uses_old_base_as_fallback():
    c=candidate(1,date=DAY)
    c.pop('ml_inputs')
    l=mp.learn([receipt(DAY,[c])],NOW,lambda c:(2,0))
    assert l['fixtures'] == 0
    assert l['training_admission']['excluded_by_reason'] == {'source_partition_unavailable_or_unbound':1}


@pytest.mark.parametrize('score',[None,(1,None),(True,2),(-1,2),(1.5,2),(1,2,3)])
def test_invalid_or_unresolved_regulation_labels_are_not_invented(score):
    l=mp.learn([receipt(DAY,[candidate(1,date=DAY)])],NOW,lambda c:score)
    assert l['fixtures'] == l['observations'] == 0


def test_earliest_conflicting_partitions_are_not_selected_by_outcome_or_old_model_n():
    a=candidate(1,date=DAY,p=.8)
    b=deepcopy(a);b['candidate_id']='other'
    b['ml_inputs']['values'].update(forecast_1x2_home_mean=.6,forecast_1x2_draw_mean=.2,forecast_1x2_away_mean=.2)
    l=mp.learn([receipt(DAY,[a,b])],NOW,lambda c:(2,0))
    assert l['fixtures'] == 0
    assert l['training_admission']['excluded_by_reason'] == {'conflicting_earliest_source_partition':1}


def test_later_snapshots_cannot_replace_earliest_training_inputs():
    a=receipt(DAY,[candidate(1,date=DAY,p=.8)])
    b=receipt(DAY,[candidate(1,date=DAY,p=.6)])
    b['captured_at']=DAY+'T06:30:00+00:00'
    l=mp.learn([b,a],NOW,lambda c:(2,0))
    assert l == mp.learn([a],NOW,lambda c:(2,0))


def test_no_model_choice_and_fit_failure_never_reverts_to_legacy(monkeypatch):
    import scipy.optimize
    class Failed:
        success=False
        x=.5
    monkeypatch.setattr(scipy.optimize,'minimize_scalar',lambda *a,**kw:Failed())
    with pytest.raises(ValueError,match='no old-model fallback'):
        mp.learn([receipt(DAY,[candidate(1,date=DAY)])],NOW,lambda c:(2,0))
    with pytest.raises(TypeError):
        mp.learn([],NOW,lambda c:None,method='poisson')
    with pytest.raises(ValueError,match='aware'):
        mp.learn([],NOW.replace(tzinfo=None),lambda c:None)


@pytest.mark.parametrize('bad',[True,-.1,1.1,float('nan'),float('inf'),None,'0.5'])
def test_invalid_or_tampered_single_parameter_model_fails_closed(bad):
    m=model();m['power']=bad
    with pytest.raises((ValueError,TypeError)):
        mp.apply_learning([candidate(1)],m)


def test_json_serialization_and_atomic_batch_rejection():
    import json
    m=json.loads(json.dumps(model()))
    a,b=candidate(1),candidate(2)
    b['base_partition'][0][2]=1.1
    before=deepcopy([a,b])
    with pytest.raises(ValueError):mp.apply_learning([a,b],m)
    assert [a,b] == before
    mp.apply_learning([a],m)
    assert a['forecast_model_key'] == m['model_key']
