"""Use the already-fetched fixture board, not another provider's odds purchase.

All clocks, fixtures, bookmaker odds and cohorts here are synthetic. No network.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json

import pytest

from edgefactory.enh_pricing import attach_enhancement_price, betexplorer_price_rejection, load_prices_index
from edgefactory.kickoff_corroboration import load_schedule_witnesses
from scripts import auto_tickets as at
from enhancement_fixtures import with_evidence
from test_enh_pricing import BE_DAY, FULL_BE_MARKETS, _be_fixture, _be_pick, _write_be_ledger


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.setenv('EDGE_FACTORY_ENH_BOARD', '1')
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path / 'localdata')
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 12, 6, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(at, 'datetime', Clock)


def board_only(root, *, fixture_changes=None, board_changes=None):
    fixture = _be_fixture(deepcopy(FULL_BE_MARKETS))
    _write_be_ledger(root, {'event': fixture})
    # No odds from either witness provider. BE is the sole quote donor.
    (root / 'localdata/oddspapi_odds_2026-10.csv.gz').unlink()
    record = dict(fixtureId='provider-event', startTime=f'{BE_DAY}T20:00:00Z',
                  participant1Name=fixture['home'], participant2Name=fixture['away'])
    record.update(fixture_changes or {})
    board = dict(fetched_at=f'{BE_DAY}T05:30:00Z', fixtures=[record])
    board.update(board_changes or {})
    path = root / 'localdata/oddspapi_fixture_state.json'
    path.write_text(json.dumps({'boards': {BE_DAY: board}, 'captured': {}}))
    return path, fixture


@pytest.mark.parametrize('market,price', [('btts_yes', 1.57), ('btts_no', 2.25),
    ('match_over_25', 3.4), ('match_under_25', 1.3)])
def test_board_alone_corroborates_betexplorer_quotes(tmp_path, market, price):
    board_only(tmp_path)
    index = load_prices_index(tmp_path, BE_DAY)
    row = attach_enhancement_price(_be_pick(market), index)
    assert row['enhancement_price_source'] == 'betexplorer'
    assert row['enhancement_price'] == price
    assert betexplorer_price_rejection(row) is None
    receipt = row['enhancement_price_provenance']['resolution']['witnesses'][0]
    assert receipt['file'] == 'oddspapi_fixture_state.json'
    assert receipt['provider_event_id'] == 'provider-event'
    assert receipt['json_pointer'] == f'/boards/{BE_DAY}/fixtures/0'
    assert index['betexplorer_admission']['admitted_cells'] == 7


@pytest.mark.parametrize('changes', [
    {'fixtureId': ''}, {'startTime': None}, {'startTime': f'{BE_DAY}T20:00:00'},
    {'startTime': f'{BE_DAY}T19:00:00Z'}, {'startTime': 'bad'},
    {'participant1Name': 'Coventry U21'}, {'participant1Name': 'Coventry SRL'},
    {'participant1Name': ''}, {'participant2Name': 'Different Club'},
    {'participant1Name': 'Newcastle Utd', 'participant2Name': 'Coventry'},
])
def test_invalid_or_wrong_fixture_board_cannot_price(tmp_path, changes):
    board_only(tmp_path, fixture_changes=changes)
    row = attach_enhancement_price(_be_pick('btts_yes'), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']


@pytest.mark.parametrize('stamp', [None, '', 'bad', f'{BE_DAY}T05:30:00',
    f'{BE_DAY}T07:00:00Z', f'{BE_DAY}T21:00:00Z'])
def test_unproven_or_late_board_is_not_schedule_evidence(tmp_path, stamp):
    board_only(tmp_path, board_changes={'fetched_at': stamp})
    row = attach_enhancement_price(_be_pick('btts_yes'), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']


def test_board_after_actual_decision_cannot_retroactively_price(tmp_path):
    board_only(tmp_path, board_changes={'fetched_at': f'{BE_DAY}T06:45:00Z'})
    row = attach_enhancement_price(_be_pick('btts_yes'), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']


def test_board_and_odds_schedule_conflict_remains_closed(tmp_path):
    path, fixture = board_only(tmp_path)
    # Reuse the existing genuine-format synthetic CSV writer, but disagree.
    _write_be_ledger(tmp_path, {'event': fixture})
    data = json.loads(path.read_text())
    data['boards'][BE_DAY]['fixtures'][0]['startTime'] = f'{BE_DAY}T19:00:00Z'
    path.write_text(json.dumps(data))
    row = attach_enhancement_price(_be_pick('btts_yes'), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']
    index = load_prices_index(tmp_path, BE_DAY)
    assert index['betexplorer_admission']['rejections']['conflicting_schedule_witnesses'] == 1


@pytest.mark.parametrize('field,value', [
    ('provider_event_id', 'other'), ('provider_event_id', ''),
    ('json_pointer', '/boards/2026-10-12/fixtures/-1'), ('json_pointer', '/wrong/0'),
    ('row_sha256', '0' * 64), ('file_sha256', None),
    ('fixture_identity_origin', 'pick_fallback'), ('kickoff_origin', 'pick_fallback'),
    ('board_fetched_at', f'{BE_DAY}T04:00:00Z'),
    ('board_fixture.startTime', f'{BE_DAY}T19:00:00Z'),
    ('board_fixture.participant1Name', 'Coventry SRL'),
])
def test_persisted_board_receipt_is_revalidated_at_live_door(tmp_path, field, value):
    board_only(tmp_path)
    row = attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(tmp_path, BE_DAY))
    assert betexplorer_price_rejection(row) is None
    proof = row['enhancement_price_provenance']['resolution']['witnesses'][0]
    parts = field.split('.')
    target = proof
    for key in parts[:-1]:
        target = target[key]
    target[parts[-1]] = value
    verdict = at.enhancement_legs([with_evidence(dict(row, pick='home'))], execution_safe=True)[0]['verdict']
    assert verdict != 'fire'
    assert betexplorer_price_rejection(row) is not None


@pytest.mark.parametrize('market', ['match_over_25', 'btts_no'])
def test_board_quote_can_reach_existing_complete_ticket_recipe(tmp_path, market):
    board_only(tmp_path)
    row = attach_enhancement_price(_be_pick(market), load_prices_index(tmp_path, BE_DAY))
    # Distinct synthetic fixture, independently corroborated through the same board.
    path = tmp_path / 'localdata/betexplorer_match_detail_2026-10-12.json'
    data = json.loads(path.read_text())
    second = deepcopy(data['fixtures']['event'])
    second.update(home='Other Home', away='Other Away')
    data['fixtures']['second'] = second
    path.write_text(json.dumps(data))
    path = tmp_path / 'localdata/oddspapi_fixture_state.json'
    data = json.loads(path.read_text())
    second = dict(data['boards'][BE_DAY]['fixtures'][0], fixtureId='second',
                  participant1Name='Other Home', participant2Name='Other Away')
    data['boards'][BE_DAY]['fixtures'].append(second)
    path.write_text(json.dumps(data))
    other = attach_enhancement_price(_be_pick(market, home='Other Home', away='Other Away',
        match='Other Home vs Other Away'), load_prices_index(tmp_path, BE_DAY))
    legs = at.enhancement_legs([with_evidence(dict(p, pick='home', league='Synthetic League')) for p in (row, other)], execution_safe=True)
    assert len(legs) == 2 and all(l['verdict'] == 'fire' for l in legs), [(l['match'], l['verdict']) for l in legs]
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, 100, stake_frac=at.ENHANCEMENT_LANE.stake_frac,
        max_accas=at.ENH_MAX_ACCAS, rank=at.ENHANCEMENT_RANK, enhancements=True)
    at._carry_lane_evidence(plan, pool)
    assert len(plan) == 1 and len(plan[0]['legs']) == 2
    assert {l['price_source'] for l in plan[0]['legs']} == {'betexplorer'}


@pytest.mark.parametrize('contents', ['{bad', 'null', '[]', '{"boards": []}',
    '{"boards": {"2026-10-12": null}}'])
def test_malformed_board_does_not_erase_existing_csv_witness(tmp_path, contents):
    path, fixture = board_only(tmp_path)
    _write_be_ledger(tmp_path, {'event': fixture})
    path.write_text(contents)
    row = attach_enhancement_price(_be_pick('btts_no'), load_prices_index(tmp_path, BE_DAY))
    assert row['enhancement_price'] == 2.25
    assert betexplorer_price_rejection(row) is None


def test_duplicate_conflicting_board_schedules_remain_closed(tmp_path):
    path, _ = board_only(tmp_path)
    data = json.loads(path.read_text())
    board = data['boards'][BE_DAY]
    board['fixtures'].append(dict(board['fixtures'][0], startTime=f'{BE_DAY}T19:00:00Z'))
    path.write_text(json.dumps(data))
    row = attach_enhancement_price(_be_pick('btts_no'), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']


def test_witness_reader_binds_existing_board_bytes_and_location(tmp_path):
    import hashlib
    path, fixture = board_only(tmp_path)
    witnesses, inputs = load_schedule_witnesses([fixture], localdata=path.parent)
    assert inputs == [dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        source_family='oddspapi', rows_scanned=1, matched_identity_rows=1,
        witness_records=1, rejections={})]
    proof, = next(iter(witnesses.values()))
    assert proof['board_fixture'] == json.loads(path.read_text())['boards'][BE_DAY]['fixtures'][0]
