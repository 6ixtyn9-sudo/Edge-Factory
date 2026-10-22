"""Phase 3: live secondary admission, adversarial receipts, no real captures."""
from copy import deepcopy
from datetime import datetime, timezone
import csv
import gzip

import pytest

from edgefactory.enh_pricing import (
    BETEXPLORER_SOURCE, attach_enhancement_price, betexplorer_price_rejection, load_prices_index,
)
from edgefactory.kickoff_corroboration import load_schedule_witnesses
from edgefactory.sources import theoddsapi as oa
from scripts import auto_tickets as at, capture_theodds as capture_oa
from enhancement_fixtures import with_evidence
from test_enh_pricing import (
    BE_DAY, FULL_BE_MARKETS, _be_fixture, _be_pick, _be_block, _be_row, _write_be_ledger,
)
from test_theoddsapi import EVENTS, PAYLOAD, PICK


@pytest.fixture(autouse=True)
def clocks_and_board(monkeypatch, tmp_path):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path / "localdata")
    monkeypatch.setenv('EDGE_FACTORY_ENH_BOARD', '1')
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 12, 6, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(at, 'datetime', Clock)


def priced(root):
    _write_be_ledger(root, {'event': _be_fixture(deepcopy(FULL_BE_MARKETS))})
    return attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(root, BE_DAY))


def live_verdict(pick):
    pick = dict(pick, league="Synthetic League", pick="home")
    return at.enhancement_legs([with_evidence(pick)], execution_safe=True)[0]['verdict']


@pytest.mark.parametrize('changes', [
    {'data_dt': None}, {'data_dt': [12, 10, 2026, True, 0]},
    {'data_dt': [12, 10, 2026, 21]}, {'data_dt': [12, 10, 2026, '21', 0]},
    {'data_dt': [12, 10, 2026, 25, 0]}, {'kickoff': '20:00'},
    {'kickoff_date': '2026-10-11'}, {'captured_at': None},
    {'captured_at': f'{BE_DAY}T06:00:00'}, {'captured_at': f'{BE_DAY}T07:00:00Z'},
    {'captured_at': f'{BE_DAY}T09:00:00Z'}, {'captured_at': f'{BE_DAY}T20:01:00Z'},
])
def test_bad_page_or_capture_never_reaches_price_index(tmp_path, changes):
    fixture = dict(_be_fixture(FULL_BE_MARKETS), **changes)
    _write_be_ledger(tmp_path, {'event': fixture})
    assert load_prices_index(tmp_path, BE_DAY)['pairs'] == {}


@pytest.mark.parametrize('columns,odds,book,line', [
    (['Over', 'Under'], [3.4], 'Book', '2.50'),
    (['Over', 'Under'], [3.4, 1.5, 9.9], 'Book', '2.50'),
    (['Over', 'Under'], [3.4, float('nan')], 'Book', '2.50'),
    (['Over', 'Under'], [3.4, float('inf')], 'Book', '2.50'),
    (['Over', 'Under'], [3.4, 1.0], 'Book', '2.50'),
    (['Over', 'Under'], [3.4, None], 'Book', '2.50'),
    (['Over', 'Over'], [3.4, 1.5], 'Book', '2.50'),
    (['Over', 'Other'], [3.4, 1.5], 'Book', '2.50'),
    (['Over', 'Under'], [3.4, 1.5], ' ', '2.50'),
    (['Over', 'Under'], [3.4, 1.5], 'Book', None),
    (['Over', 'Under'], [3.4, 1.5], 'Book', '3.50'),
])
def test_incomplete_row_cannot_donate_its_good_cell(tmp_path, columns, odds, book, line):
    markets = {'ou': _be_block(columns, ['2.50'], [_be_row(book, line, odds)])}
    _write_be_ledger(tmp_path, {'event': _be_fixture(markets)})
    assert load_prices_index(tmp_path, BE_DAY)['pairs'] == {}


@pytest.mark.parametrize('changes', [
    {'as_of': None}, {'as_of': f'{BE_DAY}T06:30:00'},
    {'as_of': f'{BE_DAY}T05:59:59Z'}, {'as_of': f'{BE_DAY}T20:00:00Z'},
    {'kickoff_utc': None}, {'kickoff_utc': f'{BE_DAY}T20:16:00Z'},
    {'home': 'Coventry U21'}, {'home': 'Newcastle Utd', 'away': 'Coventry'},
])
def test_pick_identity_time_and_asof_are_required_at_attachment(tmp_path, changes):
    _write_be_ledger(tmp_path, {'event': _be_fixture(FULL_BE_MARKETS)})
    row = attach_enhancement_price(dict(_be_pick('match_over_25'), **changes), load_prices_index(tmp_path, BE_DAY))
    assert not row['enhancement_priced']
    assert row['enhancement_price_provenance'] is None


@pytest.mark.parametrize('path,value', [
    ('enhancement_price_provenance', None),
    ('enhancement_price', 4.0), ('enhancement_price_book', 'Different Book'),
    ('enhancement_price_at', f'{BE_DAY}T05:00:00Z'),
    ('enhancement_price_kickoff', f'{BE_DAY}T19:00:00Z'),
    ('recommended_enhancement', 'btts_yes'), ('home', 'Coventry U21'),
    ('enhancement_price_provenance.kind', 'approved'),
    ('enhancement_price_provenance.data_dt', [12, 10, 2026, 20, 0]),
    ('enhancement_price_provenance.raw_kickoff', '20:00'),
    ('enhancement_price_provenance.decision_day', '2026-10-11'),
    ('enhancement_price_provenance.quote_evidence', None),
    ('enhancement_price_provenance.quote_evidence.row_sha256', None),
    ('enhancement_price_provenance.quote_evidence.column_index', 1),
    ('enhancement_price_provenance.quote_evidence.row.odds', [4.0, 1.3]),
    ('enhancement_price_provenance.ledger_sha256', None),
    ('enhancement_price_provenance.ledger_file', 'different.json'),
    ('enhancement_price_provenance.resolution.status', 'unresolved'),
    ('enhancement_price_provenance.resolution.witnesses', []),
])
def test_persisted_contradictory_receipt_is_refused_by_actual_live_gate(tmp_path, path, value):
    row = priced(tmp_path)
    assert betexplorer_price_rejection(row) is None
    assert live_verdict(row) == 'fire'
    node = row
    parts = path.split('.')
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = value
    assert betexplorer_price_rejection(row) is not None
    assert live_verdict(row) != 'fire'
    # Historical inspection remains descriptive; no bank/history rewrite.
    if path != 'recommended_enhancement':
        assert at.enhancement_legs([with_evidence(row)])[0]['verdict'] == 'fire'


@pytest.mark.parametrize('key,value', [
    ('source', 'betexplorer'), ('file_sha256', 'not-a-digest'), ('row_sha256', None),
    ('csv_data_row', 0), ('csv_data_row', True), ('kickoff_origin', 'pick_fallback'),
    ('observed_at_utc', f'{BE_DAY}T06:45:00Z'),
    ('home', 'Coventry U21'), ('kickoff_utc', f'{BE_DAY}T19:00:00Z'),
])
def test_witness_receipt_is_revalidated_not_just_a_boolean(tmp_path, key, value):
    row = priced(tmp_path)
    row['enhancement_price_provenance']['resolution']['witnesses'][0][key] = value
    assert live_verdict(row) != 'fire'


def test_freshness_uses_existing_source_policy_and_checks_execution_clock(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    row = priced(tmp_path)
    monkeypatch.setattr(be, 'CACHE_FRESHNESS_H', .25)
    assert betexplorer_price_rejection(row) == 'betexplorer_capture_stale'
    monkeypatch.setattr(be, 'CACHE_FRESHNESS_H', 1)
    assert betexplorer_price_rejection(row) is None
    assert betexplorer_price_rejection(row, execution_at=datetime(2026, 10, 12, 8, tzinfo=timezone.utc)) == 'betexplorer_capture_stale'
    monkeypatch.setattr(be, 'CACHE_FRESHNESS_H', 24)
    assert betexplorer_price_rejection(row, execution_at=datetime(2026, 10, 12, 20, tzinfo=timezone.utc)) == 'betexplorer_execution_time_ineligible'


@pytest.mark.parametrize('modern', [True, False])
def test_legacy_be_aggregate_cannot_bypass_proof(tmp_path, modern):
    row = priced(tmp_path)
    index = load_prices_index(tmp_path, BE_DAY)
    index.pop('fixture_quotes')
    if not modern:
        row.pop('kickoff_utc')
        row.pop('as_of')
    result = attach_enhancement_price(row, index)
    assert result['enhancement_price'] is None
    assert result['enhancement_price_provenance'] is None


@pytest.mark.parametrize('stamp,origin', [
    ('2026-08-03T16:00:00Z', 'provider_commence_time'),
    ('2026-08-03T18:00:00+02:00', 'provider_commence_time'),
    ('2026-08-03T16:00:00', 'provider_unverified_clock'),
    ('bad clock', 'provider_unverified_clock'), (None, 'pick_fallback'), ('', 'pick_fallback'),
])
def test_producer_tags_only_real_aware_provider_clock(stamp, origin):
    rows = oa.rows_from_event_odds(PICK, dict(EVENTS[1], commence_time=stamp), PAYLOAD)
    assert rows
    assert all(row['kickoff_origin'] == origin and row['provider_commence_time'] == stamp for row in rows)
    assert all(row['fixture_identity_origin'] == 'provider_participants' for row in rows)
    assert all(row['provider_event_id'] == 'evt_right' for row in rows)
    fallback = oa.rows_from_event_odds(PICK, {'commence_time': stamp}, PAYLOAD)
    assert fallback and all(row['fixture_identity_origin'] == 'pick_fallback' for row in fallback)


def test_monthly_schema_evolution_does_not_backfill_legacy_origin(tmp_path, monkeypatch):
    local = tmp_path / 'localdata'
    local.mkdir()
    monkeypatch.setattr(capture_oa, 'LOCALDATA', local)
    rows = oa.rows_from_event_odds(PICK, EVENTS[1], PAYLOAD)
    extra = {'kickoff_origin', 'provider_event_id', 'provider_commence_time', 'fixture_identity_origin'}
    legacy = {key: value for key, value in rows[0].items() if key not in extra}
    assert capture_oa.append_rows('2026-08-03', [legacy], [c for c in oa.COLUMNS if c not in extra]) == 1
    assert capture_oa.append_rows('2026-08-03', rows, oa.COLUMNS) == len(rows)
    with gzip.open(local / 'theoddsapi_odds_2026-08.csv.gz', 'rt') as fh:
        saved = list(csv.DictReader(fh))
    old, = [row for row in saved if not row['kickoff_origin']]
    assert all(old[key] == '' for key in extra)
    assert capture_oa.append_rows('2026-08-03', rows, oa.COLUMNS) == 0


def test_origin_label_alone_does_not_make_provider_participants_independent(tmp_path, monkeypatch):
    local = tmp_path / 'localdata'
    local.mkdir()
    monkeypatch.setattr(capture_oa, 'LOCALDATA', local)
    rows = oa.rows_from_event_odds(PICK, {'commence_time': EVENTS[1]['commence_time']}, PAYLOAD)
    assert capture_oa.append_rows('2026-08-03', rows, oa.COLUMNS)
    witnesses, receipts = load_schedule_witnesses([PICK], localdata=local)
    assert witnesses == {}
    assert receipts[0]['rejections']['provider_event_identity_or_clock_unproven'] == len(rows)


@pytest.mark.parametrize('alias', ['betexplorer', 'betexplorer_odds'])
def test_persisted_source_alias_cannot_evade_the_live_guard(tmp_path, alias):
    row = priced(tmp_path)
    row['enhancement_price_source'] = alias
    assert live_verdict(row) == 'fire'
    row['enhancement_price_provenance'] = None
    assert live_verdict(row) == 'betexplorer_admission_receipt_missing'


def test_changing_price_and_its_label_together_cannot_rebind_original_quote(tmp_path):
    row = priced(tmp_path)
    row['enhancement_price'] = row['enhancement_price_provenance']['price'] = 4.0
    assert live_verdict(row) == 'betexplorer_quote_row_binding_mismatch'


@pytest.mark.parametrize('same_instant', [False, True])
def test_be_latest_offer_not_best_past_offer_and_conflicts_quarantine(tmp_path, same_instant):
    old = _be_fixture(deepcopy(FULL_BE_MARKETS))
    new = deepcopy(old)
    new['markets']['ou']['rows'][0]['odds'][0] = 2.0
    if not same_instant:
        new['captured_at'] = f'{BE_DAY}T06:10:00Z'
    _write_be_ledger(tmp_path, {'old': old, 'new': new})
    row = attach_enhancement_price(_be_pick('match_over_25'), load_prices_index(tmp_path, BE_DAY))
    assert row['enhancement_price'] == (None if same_instant else 2.0)


def test_run_asof_is_stamped_before_live_candidate_pricing():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / 'scripts/picks_today.py').read_text()
    main = source.index('def main(')
    stamp = source.index('p["as_of"] = as_of.isoformat(timespec="seconds")', main)
    assert stamp < source.index('enh = compute_dynamic_enhancement(con, p, prices_index,', main)
