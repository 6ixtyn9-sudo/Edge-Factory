"""Use the already-fetched fixture board, not another provider's odds purchase.

All clocks, fixtures, bookmaker odds and cohorts here are synthetic. No network.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json

import pytest

from edgefactory.enh_pricing import MARKET_PRICE_MAP, attach_enhancement_price, betexplorer_price_rejection, load_prices_index
from edgefactory.kickoff_corroboration import load_schedule_witnesses
from scripts import auto_tickets as at
from enhancement_fixtures import with_evidence
from test_enh_pricing import BE_DAY, FULL_BE_MARKETS, _be_block, _be_row, _be_fixture, _be_pick, _write_be_ledger


# Synthetic prices isolate market wiring from payout differences. Every market
# still needs its own retained comparison cells; no market is inferred from 1X2.
ALL_BE_MARKETS = {
    'ou': _be_block(['Over', 'Under'], ['1.50', '2.50', '3.50', '4.50'],
        [_be_row('Common Book', line, [2.25, 2.25])
         for line in ['1.50', '2.50', '3.50', '4.50']]),
    'bts': _be_block(['Yes', 'No'], ['0'], [_be_row('Common Book', '0', [2.25, 2.25])]),
    'dc': _be_block(['1X', '12', 'X2'], ['0'], [_be_row('Common Book', '0', [2.25, 2.25, 2.25])]),
}
MATCH_TOTALS = [f'match_{side}_{line}' for line in ['15', '25', '35', '45']
                for side in ['over', 'under']]
SUPPORTED_BE_MARKETS = MATCH_TOTALS + ['btts_yes', 'btts_no', 'double_chance']


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.setenv('EDGE_FACTORY_ENH_BOARD', '1')
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path / 'localdata')
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 12, 6, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(at, 'datetime', Clock)


def board_only(root, *, fixture_changes=None, board_changes=None, markets=None):
    fixture = _be_fixture(deepcopy(FULL_BE_MARKETS if markets is None else markets))
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


@pytest.mark.parametrize('market,side,selection',
    [(m, 'home', MARKET_PRICE_MAP[m][1]) for m in MATCH_TOTALS + ['btts_yes', 'btts_no']]
    + [('double_chance', 'home', '1x'), ('double_chance', 'away', 'x2')])
def test_board_alone_corroborates_betexplorer_quotes(tmp_path, market, side, selection):
    board_only(tmp_path, markets=ALL_BE_MARKETS)
    index = load_prices_index(tmp_path, BE_DAY)
    row = attach_enhancement_price(_be_pick(market, pick=side), index)
    assert row['enhancement_price_source'] == 'betexplorer'
    assert row['enhancement_price'] == 2.25
    assert betexplorer_price_rejection(row) is None
    proof = row['enhancement_price_provenance']
    assert proof['selection'] == selection
    assert proof['market'] == (MARKET_PRICE_MAP[market][0])
    receipt = proof['resolution']['witnesses'][0]
    assert receipt['file'] == 'oddspapi_fixture_state.json'
    assert receipt['provider_event_id'] == 'provider-event'
    assert receipt['json_pointer'] == f'/boards/{BE_DAY}/fixtures/0'
    assert index['betexplorer_admission']['admitted_cells'] == 13


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


@pytest.mark.parametrize('market', SUPPORTED_BE_MARKETS)
@pytest.mark.parametrize('schedule_source', [None, 'scoutingstats', 'vitibet'])
def test_board_quote_can_reach_existing_complete_ticket_recipe(tmp_path, market, schedule_source):
    board_only(tmp_path, markets=ALL_BE_MARKETS)
    row = attach_enhancement_price(_be_pick(market, pick='home'), load_prices_index(tmp_path, BE_DAY))
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
    if schedule_source:
        import csv
        import gzip
        records = [dict(date=BE_DAY, home=f['participant1Name'], away=f['participant2Name'],
            kickoff=f['startTime'], captured_at=f'{BE_DAY}T05:30:00Z', source=schedule_source,
            kickoff_origin='provider_explicit_offset', fixture_identity_origin='provider_participants')
            for f in data['boards'][BE_DAY]['fixtures']]
        path.unlink()
        with gzip.open(tmp_path / f'localdata/{schedule_source}_2026-10.csv.gz', 'wt', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)
        row = attach_enhancement_price(_be_pick(market, pick='home'), load_prices_index(tmp_path, BE_DAY))
    other = attach_enhancement_price(_be_pick(market, pick='home', home='Other Home', away='Other Away',
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


@pytest.mark.parametrize('market', [m for m, slot in MARKET_PRICE_MAP.items()
    if slot and slot[0].startswith('tt_')])
def test_match_totals_are_never_substituted_for_missing_team_totals(tmp_path, market):
    board_only(tmp_path, markets=ALL_BE_MARKETS)
    row = attach_enhancement_price(_be_pick(market, pick='home'), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']
    assert row['enhancement_price'] is None


def source_schedule_only(root, source='scoutingstats', *, changes=None):
    """Existing response CSV, no odds-provider schedule and no research reader."""
    import csv
    import gzip
    _, fixture = board_only(root, markets=ALL_BE_MARKETS)
    (root / 'localdata/oddspapi_fixture_state.json').unlink()
    row = dict(date=BE_DAY, home=fixture['home'], away=fixture['away'],
               kickoff=f'{BE_DAY}T20:00:00Z', captured_at=f'{BE_DAY}T05:30:00Z',
               source=source, kickoff_origin='provider_explicit_offset',
               fixture_identity_origin='provider_participants')
    row.update(changes or {})
    with gzip.open(root / f'localdata/{source}_2026-10.csv.gz', 'wt', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    return row


@pytest.mark.parametrize('source', ['scoutingstats', 'vitibet'])
@pytest.mark.parametrize('market', SUPPORTED_BE_MARKETS)
def test_source_schedule_corroborates_without_other_odds_provider(tmp_path, source, market):
    source_schedule_only(tmp_path, source)
    row = attach_enhancement_price(_be_pick(market, pick='home'), load_prices_index(tmp_path, BE_DAY))
    assert row['enhancement_priced']
    assert betexplorer_price_rejection(row) is None
    assert at.enhancement_legs([with_evidence(dict(row, pick='home', league='Synthetic League'))], execution_safe=True)[0]['verdict'] == 'fire'
    witness = row['enhancement_price_provenance']['resolution']['witnesses'][0]
    assert witness['source'] == source
    assert witness['file'] == f'{source}_2026-10.csv.gz'
    assert witness['schedule_row']['captured_at'] == f'{BE_DAY}T05:30:00Z'


@pytest.mark.parametrize('changes', [
    {'captured_at': ''}, {'captured_at': f'{BE_DAY}T05:30:00'},
    {'captured_at': f'{BE_DAY}T07:00:00Z'}, {'captured_at': f'{BE_DAY}T21:00:00Z'},
    {'kickoff': f'{BE_DAY}T20:00:00'}, {'kickoff_origin': 'pick_fallback'},
    {'fixture_identity_origin': 'pick_fallback'}, {'source': 'betexplorer'},
    {'home': 'Coventry U21'}, {'home': 'Coventry Women'},
    {'away': 'Other Club'}, {'home': 'Newcastle Utd', 'away': 'Coventry'},
])
def test_source_schedule_requires_original_identity_and_predecision_clock(tmp_path, changes):
    source_schedule_only(tmp_path, changes=changes)
    row = attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']


def test_source_schedule_after_actual_decision_is_not_backfilled(tmp_path):
    source_schedule_only(tmp_path, changes={'captured_at': f'{BE_DAY}T06:45:00Z'})
    index = load_prices_index(tmp_path, BE_DAY)
    for instant, expected in [('06:30:00', False), ('06:50:00', True)]:
        row = attach_enhancement_price(_be_pick('match_over_25', as_of=f'{BE_DAY}T{instant}Z'), index)
        assert row['enhancement_priced'] is expected


def test_source_schedule_conflicts_do_not_choose_convenient_witness(tmp_path):
    source_schedule_only(tmp_path)
    source_schedule_only(tmp_path, 'vitibet', changes={'kickoff': f'{BE_DAY}T19:00:00Z'})
    index = load_prices_index(tmp_path, BE_DAY)
    assert index['betexplorer_admission']['rejections']['conflicting_schedule_witnesses'] == 1
    assert not attach_enhancement_price(_be_pick('match_over_25'), index)['enhancement_priced']


@pytest.mark.parametrize('field,value', [
    ('schedule_row.kickoff', 'bad'), ('schedule_row.captured_at', 'bad'),
    ('schedule_row.home', 'Coventry U21'), ('schedule_row.source', 'betexplorer'),
    ('fixture_identity_origin', 'pick_fallback'), ('kickoff_origin', 'pick_fallback'),
    ('file', 'picks_2026-10-12.json'), ('row_sha256', '0' * 64),
    ('csv_data_row', 0), ('schedule_row', None),
])
def test_source_schedule_receipt_is_revalidated_at_live_door(tmp_path, field, value):
    source_schedule_only(tmp_path)
    row = attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(tmp_path, BE_DAY))
    proof = row['enhancement_price_provenance']['resolution']['witnesses'][0]
    target = proof
    parts = field.split('.')
    for key in parts[:-1]:
        target = target[key]
    target[parts[-1]] = value
    assert betexplorer_price_rejection(row) is not None
    assert at.enhancement_legs([with_evidence(row)], execution_safe=True)[0]['verdict'] != 'fire'


def test_research_shadow_is_not_an_operational_schedule_input(tmp_path):
    source_schedule_only(tmp_path)
    (tmp_path / 'localdata/scoutingstats_2026-10.csv.gz').unlink()
    shadow = tmp_path / 'localdata/phase5_shadow'
    shadow.mkdir()
    (shadow / 'rows.jsonl').write_text(json.dumps(dict(source='scoutingstats',
        kickoff_at_utc=f'{BE_DAY}T20:00:00Z', captured_at=f'{BE_DAY}T05:30:00Z')) + '\n')
    assert not attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(tmp_path, BE_DAY))['enhancement_priced']


def test_curated_same_club_alias_reaches_its_own_corroborated_quote(tmp_path):
    path, fixture = board_only(tmp_path, markets=ALL_BE_MARKETS)
    ledger = tmp_path / f'localdata/betexplorer_match_detail_{BE_DAY}.json'
    data = json.loads(ledger.read_text())
    data['fixtures']['event'].update(home='Besiktas', away='Basaksehir')
    ledger.write_text(json.dumps(data))
    data = json.loads(path.read_text())
    data['boards'][BE_DAY]['fixtures'][0].update(participant1Name='Beşiktaş', participant2Name='İstanbul Başakşehir')
    path.write_text(json.dumps(data))
    index = load_prices_index(tmp_path, BE_DAY)
    from edgefactory.util import norm_team
    # A schedule-only source's earlier display-name bucket has no prices.
    own = (norm_team('Beşiktaş'), norm_team('İstanbul Başakşehir'))
    index['names'] = {own: ('Beşiktaş', 'İstanbul Başakşehir'), **index['names']}
    index.pop('betexplorer_context', None)  # Preserve this exact test index order.
    pick = _be_pick('match_over_25', home='Beşiktaş', away='İstanbul Başakşehir')
    row = attach_enhancement_price(pick, index)
    assert row['enhancement_priced']
    assert row['enhancement_price_source'] == 'betexplorer'
    assert betexplorer_price_rejection(row) is None
    for other in ['İstanbulspor', 'Başakşehir U21', 'Başakşehir Women']:
        row = attach_enhancement_price(_be_pick('match_over_25', home='Beşiktaş', away=other), index)
        assert not row['enhancement_priced']


def test_source_schedule_history_survives_post_cutoff_refresh_without_backdating(tmp_path):
    import csv
    import gzip
    previous = source_schedule_only(tmp_path)
    current = dict(previous, captured_at=f'{BE_DAY}T08:30:00Z', schedule_history=json.dumps([previous]))
    path = tmp_path / 'localdata/scoutingstats_2026-10.csv.gz'
    with gzip.open(path, 'wt', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(current)); writer.writeheader(); writer.writerow(current)
    row = attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(tmp_path, BE_DAY))
    assert row['enhancement_priced']
    assert betexplorer_price_rejection(row) is None
    witness = row['enhancement_price_provenance']['resolution']['witnesses'][0]
    assert witness['observed_at_utc'] == f'{BE_DAY}T05:30:00+00:00'
    assert witness['csv_history_index'] == 0
    assert witness['schedule_row'] == previous


def test_conflicting_pre_cutoff_schedule_history_stays_closed(tmp_path):
    import csv
    import gzip
    previous = source_schedule_only(tmp_path)
    current = dict(previous, kickoff=f'{BE_DAY}T19:00:00Z', captured_at=f'{BE_DAY}T06:00:00Z',
                   schedule_history=json.dumps([previous]))
    path = tmp_path / 'localdata/scoutingstats_2026-10.csv.gz'
    with gzip.open(path, 'wt', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(current)); writer.writeheader(); writer.writerow(current)
    index = load_prices_index(tmp_path, BE_DAY)
    assert index['betexplorer_admission']['rejections']['conflicting_schedule_witnesses'] == 1
    assert not attach_enhancement_price(_be_pick('match_over_25'), index)['enhancement_priced']


@pytest.mark.parametrize('history', ['bad json', '{}', '[null]'])
def test_corrupt_source_schedule_history_cannot_hide_a_conflict(tmp_path, history):
    import csv
    import gzip
    current = dict(source_schedule_only(tmp_path), schedule_history=history)
    path = tmp_path / 'localdata/scoutingstats_2026-10.csv.gz'
    with gzip.open(path, 'wt', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(current)); writer.writeheader(); writer.writerow(current)
    index = load_prices_index(tmp_path, BE_DAY)
    assert index['betexplorer_admission']['rejections']['schedule_archive_unavailable'] == 1
    assert not attach_enhancement_price(_be_pick('match_over_25'), index)['enhancement_priced']


@pytest.mark.parametrize('source', ['scoutingstats', 'vitibet'])
def test_recovered_schedule_archive_is_an_execution_witness(tmp_path, source):
    source_schedule_only(tmp_path, source)
    original = tmp_path / f'localdata/{source}_2026-10.csv.gz'
    original.rename(tmp_path / f'localdata/schedule_{source}_2026-10.csv.gz')
    row = attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(tmp_path, BE_DAY))
    assert row['enhancement_priced']
    assert betexplorer_price_rejection(row) is None
    witness = row['enhancement_price_provenance']['resolution']['witnesses'][0]
    assert witness['file'] == f'schedule_{source}_2026-10.csv.gz'
    assert at.enhancement_legs([with_evidence(dict(row, pick='home', league='Synthetic League'))],
                               execution_safe=True)[0]['verdict'] == 'fire'


def test_recovered_schedule_archives_do_not_enter_prediction_warehouse(tmp_path, monkeypatch):
    import shutil
    from pathlib import Path
    from edgefactory import warehouse
    root = Path(__file__).resolve().parents[1]
    for source in ['scoutingstats', 'vitibet']:
        shutil.copy2(root / f'localdata/schedule_{source}_2026-10.csv.gz', tmp_path)
    monkeypatch.setattr(warehouse, 'LOCALDATA', tmp_path)
    con = warehouse.connect()
    try:
        names = {r[0] for r in con.execute('SHOW TABLES').fetchall()}
        assert not {'scoutingstats', 'vitibet', 'scoutingstats_settled', 'vitibet_settled'} & names
    finally:
        con.close()


def test_committed_schedule_recovery_preserves_original_capture_identity():
    import csv
    import gzip
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / 'handoff/enh_schedule_repair_2026-10-26.json').read_text())
    originals = {r['row_id']: r for r in evidence['original_source_capture_records']}
    seen = set()
    for source in ['scoutingstats', 'vitibet']:
        with gzip.open(root / f'localdata/schedule_{source}_2026-10.csv.gz', 'rt') as f:
            for row in csv.DictReader(f):
                original = originals[row['original_capture_row_id']]
                assert row['source'] == original['source'] == source
                assert row['captured_at'] == original['captured_at']
                assert row['kickoff'] == original['kickoff_raw']
                assert (row['home'], row['away'], row['date']) == tuple(
                    original['raw_fixture'][k] for k in ['home', 'away', 'date'])
                assert row['original_capture_commit'] == evidence['input_commit']
                assert not {'p1', 'px', 'p2', 'odds', 'hs', 'gs'} & row.keys()
                seen.add(row['original_capture_row_id'])
    assert seen == set(originals)
