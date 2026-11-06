"""Bookings prices must never be normalized, forecast or settled as goals.

Retained monthly census metadata supplies the observed catalog labels/types;
constructed odds payloads exercise the parser without claiming native capture.
"""

import csv
import gzip
import json
from datetime import datetime
from pathlib import Path

import pytest

import scripts.capture_oddspapi as cap
import scripts.picks_today as pt
from edgefactory.sources import oddspapi_odds as op


@pytest.fixture
def evidence():
    return json.loads((Path(__file__).parent / 'fixtures/oddspapi_bookings_2026-11-04.json').read_text())


def entry_from_census(row):
    return {'name': row['label'], 'marketType': row['market_type'],
            'period': row['period'], 'handicap': row['handicap'], 'playerProp': False}


def test_retained_census_exposes_bookings_not_goal_prices(evidence):
    witnesses = {r['outcome_key']: r for r in evidence['normalized_quote_witnesses']}
    assert witnesses['101074']['market'] == 'tt_away_3.5'
    assert witnesses['101074']['odds'] == '19.0'
    assert evidence['market_census']['101074']['label'] == 'Bookings - Over Under Team 2'
    assert witnesses['10926']['market'] == 'ou_3.5'
    assert evidence['market_census']['10926']['label'] == 'Bookings - Over Under Full Time'
    assert len(evidence['market_census']) == 46
    for row in evidence['market_census'].values():
        assert op._classify_catalog_entry(entry_from_census(row)).startswith('unsupported_')


@pytest.mark.parametrize('name,kind,reason', [
    ('Bookings - Over Under Full Time', 'totals-bookings', 'cards'),
    ('Bookings - Over Under Team 1', 'teamtotals-bookings-team1', 'cards'),
    ('Bookings - Over Under Team 2', 'teamtotals-bookings-team2', 'cards'),
    ('Over Under Full Time', 'totals-bookings', 'cards'),
    ('Over Under Team 2', 'teamtotals-bookings-team2', 'cards'),
    ('Bookings - Over Under Team 2', 'totals', 'cards'),
    ('Booking Points - Over Under', 'totals', 'cards'),
    ('Over Under Full Time', 'totals-corners', 'corners'),
    ('Shots - Over Under Team 2', 'teamtotals-team2', 'non_goal'),
    ('Over Under Full Time', 'totals-shots', 'non_goal'),
    ('Offsides - Over Under Full Time', 'totals', 'non_goal'),
    ('2Up - Full Time Result', '2up', 'early_payout'),
    ('Full Time Result', '2up', 'early_payout'),
])
def test_non_goal_or_nonstandard_catalog_family_cannot_borrow_goal_semantics(name, kind, reason):
    assert op._classify_catalog_entry({'name': name, 'marketType': kind, 'period': 'fulltime'}) == f'unsupported_{reason}'


@pytest.mark.parametrize('mid', ['101074', '10926'])
def test_stale_type_map_cannot_override_explicit_bookings_catalog(evidence, mid):
    entry = entry_from_census(evidence['market_census'][mid])
    entry['outcomes'] = {mid: 'Over'}  # Constructed catalog outcome, not a native witness.
    payload = {'startTime': '2026-11-04T17:45:00Z', 'bookmakerOdds': {'bet365': {'markets': {
        mid: {'marketActive': True, 'outcomes': {mid: {'players': {'0': {
            'price': 19., 'active': True, 'playerName': 'Over 3.5',
        }}}}},
    }}}}
    stats = {}
    assert op.rows_from_odds_response(
        payload, home='AEK Athens', away='Real Madrid', market_type_map={mid: evidence['market_census'][mid]['type']},
        market_catalog={mid: entry}, stats=stats,
    ) == []
    assert stats == {'market_unsupported_cards': 1}


def test_real_goals_catalog_still_parses_and_retains_market_metadata():
    fixtures = Path(__file__).parent / 'fixtures'
    catalog = json.loads((fixtures / 'oddspapi_markets_catalog.json').read_text())
    entries = op._market_catalog_entries(catalog)
    payload = json.loads((fixtures / 'oddspapi_odds_documented_shape.json').read_text())
    rows = op.rows_from_odds_response(
        payload, home='Croatia', away='England', market_catalog=entries,
        market_type_map={k: op._classify_catalog_entry(v) for k, v in entries.items()},
    )
    assert any(r['market'] == 'ou_2.5' for r in rows)
    for row in rows:
        entry = entries[row['provider_market_id']]
        assert row['provider_market_name'] == entry['name']
        assert row['provider_market_type'] == entry['marketType']
        assert row['provider_period'] == entry['period'] == 'fulltime'


def test_actual_generation_three_quotes_are_counted_stale_in_main_reader(tmp_path, monkeypatch, evidence):
    path = tmp_path / 'oddspapi_odds_2026-11.csv.gz'
    rows = evidence['normalized_quote_witnesses']
    with gzip.open(path, 'wt', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    before = path.read_bytes()
    monkeypatch.setattr(pt, 'LOCALDATA', tmp_path)
    stats = {}
    pt.oddspapi_odds_bundle('2026-11-04', not_after=datetime.fromisoformat('2026-11-04T13:27:00Z'), stats=stats)
    assert stats['raw_rows'] == stats['stale_schema_rows'] == 2
    assert stats['usable_rows'] == 0
    assert path.read_bytes() == before
    assert cap.SCHEMA_VERSION == pt.ODDSPAPI_MIN_SCHEMA_VERSION == 4


def test_appending_new_generation_never_promotes_legacy_rows(tmp_path, monkeypatch, evidence):
    monkeypatch.setattr(cap, 'OUT_DIR', tmp_path)
    day = evidence['date']
    path = tmp_path / 'oddspapi_odds_2026-11.csv.gz'
    rows = evidence['normalized_quote_witnesses']
    with gzip.open(path, 'wt', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    new = dict(rows[0], market='ou_2.5', odds='1.8', provider_market_id='10194',
               provider_market_name='Over Under Full Time', provider_market_type='totals', provider_period='fulltime')
    cap._append_rows([new], day)
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as fh:
        written = list(csv.DictReader(fh))
    assert len(written) == 3
    assert [r['schema_version'] for r in written] == ['3', '3', '4']
    assert [{k: r[k] for k in rows[0]} for r in written[:2]] == rows
    assert all(not r['provider_market_id'] for r in written[:2])
    assert written[-1]['provider_market_id'] == '10194'
