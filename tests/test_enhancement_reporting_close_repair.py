"""The witnessed close repair changes reporting fields, never the booked bank."""
import copy
import json
from pathlib import Path

import pytest

import scripts.auto_tickets as at


def stale_state():
    return {
        'bank':39.0372, 'base_pct':100., 'open_slips':[{'date':'2026-10-27','accas':[]}],
        'frozen_by_date':{'2026-10-25':{'frozen_at':'unchanged'}},
        'history':[
            {'date':'2026-10-24','staked_pct':13.1522,'returned_pct':0.,'bank_pct':39.4565,'close_pct':39.4565,'accas':[]},
            {'date':'2026-10-25','staked_pct':9.864,'returned_pct':14.1384,'bank_pct':43.7309,'close_pct':37.5495,
             'accas':[{'won':True,'stake_pct':3.288,'odds':1.88,'returned_pct':6.1814,'legs':[
                 {'match':'Lillestrøm SK vs SK Brann','result':'win','label':'Match Over 2.5 Goals'}]}]},
            {'date':'2026-10-26','staked_pct':4.6937,'returned_pct':0.,'bank_pct':39.0372,'close_pct':32.8558,'accas':[]}]}


def test_exact_historical_offset_is_repaired_without_any_financial_change():
    state = stale_state();before = copy.deepcopy(state)
    assert at.repair_enhancement_reporting_closes(state)
    assert state['history'][1]['close_pct'] == 43.7309
    assert state['history'][2]['close_pct'] == 39.0372
    for key in before:
        if key != 'history':
            assert state[key] == before[key]
    for old,new in zip(before['history'],state['history']):
        assert {k:v for k,v in old.items() if k!='close_pct'} == {k:v for k,v in new.items() if k!='close_pct'}
    snapshot = copy.deepcopy(state)
    assert not at.repair_enhancement_reporting_closes(state)
    assert state == snapshot
    proof = state['integrity_recovery']['reporting_close_correction']
    assert proof['corrections'][0]['before'] == 37.5495
    assert proof['bank_unchanged'] == before['bank']


@pytest.mark.parametrize('damage',['other_offset','not_witnessed','bank_mismatch'])
def test_unknown_discrepancies_are_never_guessed_or_credited(damage):
    state = stale_state()
    if damage == 'other_offset':state['history'][1]['close_pct'] -= 1
    elif damage == 'not_witnessed':state['history'][1]['accas'][0]['returned_pct'] = 5
    else:state['bank'] += 1
    before = copy.deepcopy(state)
    if damage == 'bank_mismatch':
        with pytest.raises(ValueError, match='existing bank'):
            at.repair_enhancement_reporting_closes(state)
    else:
        assert not at.repair_enhancement_reporting_closes(state)
    assert state == before


def test_committed_enhancement_reporting_chain_matches_recorded_ledger():
    root = Path(__file__).resolve().parents[1] / 'localdata'
    state = json.loads((root/'enhancement_tickets_state.json').read_text())
    report = json.loads((root/'autobets_enh_tickets_performance.json').read_text())
    close = state['base_pct']
    for row in sorted(state['history'],key=lambda h:h['date']):
        close += row['returned_pct']-row['staked_pct']
        assert row.get('close_pct',row['bank_pct']) == pytest.approx(close,abs=.001)
    assert close == pytest.approx(state['bank'],abs=.001)
    assert state['history'] == report['history']
    assert state['bank'] == report['bank_pct']


def test_enhancement_load_repairs_stale_cache_but_main_load_does_not(tmp_path, monkeypatch):
    state = at.fresh_state();state.update(stale_state())
    main = tmp_path/'main.json';enh = tmp_path/'enh.json'
    main.write_text(json.dumps(state));enh.write_text(json.dumps(state))
    lane = at.ENHANCEMENT_LANE._replace(state_file=enh)
    monkeypatch.setattr(at,'ENHANCEMENT_LANE',lane)
    monkeypatch.setattr(at,'STATE_FILE',main)
    main_bytes = main.read_bytes()
    repaired = at.load_state(lane)
    assert repaired['bank'] == state['bank']
    assert repaired['history'][-1]['close_pct'] == 39.0372
    assert at.load_state()['history'][-1]['close_pct'] == 32.8558
    assert main.read_bytes() == main_bytes
    assert json.loads(enh.read_bytes()) == repaired
