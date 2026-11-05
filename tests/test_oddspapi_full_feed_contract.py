"""Full retained vocabulary + adversarial native-shape contract regressions.

These exercise stored catalogs and constructed odds payloads, not live provider
calls, native-response authenticity or historical bookmaker settlement.
"""
import gzip
import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path

import pytest

from edgefactory.sources import oddspapi_odds as op

ROOT = Path(__file__).resolve().parents[1]
PRICED = {'1x2', 'btts', 'totals', 'team_totals_home', 'team_totals_away'}


@pytest.fixture(scope='module', params=['2026-10-03', '2026-10-14'])
def vocabulary(request):
    path = ROOT / f'localdata/source_health/odds_vocabulary/{request.param}+oddspapi.json.gz'
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        return json.load(fh)


def test_entire_retained_vocabulary_integrity_and_period_boundary(vocabulary):
    markets = vocabulary['markets']
    assert len(markets) == vocabulary['catalog_size']
    assert hashlib.sha256(json.dumps(markets, sort_keys=True).encode()).hexdigest() == vocabulary['digest']
    outcome_ids = [oid for e in markets.values() for oid in e.get('outcomes', {})]
    assert len(set(outcome_ids)) == len(outcome_ids)
    for e in markets.values():
        kind = op._classify_catalog_entry(e)
        if kind in PRICED:
            assert e['period'] == 'fulltime'
            assert not e.get('playerProp')
            assert not any(word in e['name'].lower() for word in ('bookings', 'corner', 'half', 'overtime', 'round'))
    if vocabulary['day'] == '2026-10-14':
        assert len(markets) == 1122
        admitted = [e for e in markets.values() if op._classify_catalog_entry(e) in PRICED]
        assert len(admitted) == 96  # Entire retained catalog, not the 756-ID census.
        assert {e['name'] for e in admitted} == {
            'Full Time Result', 'Both Teams To Score', 'Over Under Full Time',
            'Over Under Team 1', 'Over Under Team 2',
        }


def test_every_retained_admitted_catalog_outcome_maps_to_correct_side_and_line(vocabulary):
    checked = 0
    for mid, entry in vocabulary['markets'].items():
        kind = op._classify_catalog_entry(entry)
        if kind not in PRICED:
            continue
        for oid, label in entry.get('outcomes', {}).items():
            label = label.lower()
            if kind == '1x2':
                selection = {'1': 'home', 'x': 'draw', '2': 'away'}.get(label)
                if selection is None:
                    continue  # Explicit unsupported outcome labels stay unpriced.
                expected = ('1x2', selection, None)
            elif kind == 'btts':
                if label not in ('yes', 'no'):
                    continue
                expected = ('btts', label, None)
            else:
                if label not in ('over', 'under'):
                    continue
                line = entry.get('handicap')
                if type(line) not in (int, float) or not math.isfinite(line) or line < 0:
                    continue
                prefix = {'totals': 'ou', 'team_totals_home': 'tt_home', 'team_totals_away': 'tt_away'}[kind]
                expected = (f'{prefix}_{line:g}', label, None)
            assert op._market_selection(
                kind, '', 'Home', 'Away', None, catalog_entry=entry, outcome_key=oid, market_id=mid,
            ) == expected
            checked += 1
    assert checked >= 193  # All supported outcomes in the smaller soccer catalog.


@pytest.fixture
def goal_case():
    payload = json.loads((ROOT / 'tests/fixtures/oddspapi_odds_documented_shape.json').read_text())
    payload['bookmakerOdds'] = {'cloudbet': {'markets': {
        '10194': deepcopy(payload['bookmakerOdds']['cloudbet']['markets']['10194']),
    }}}
    payload.update(fixtureId='native-fx', sportId=10, statusId=0)
    catalog = json.loads((ROOT / 'tests/fixtures/oddspapi_markets_catalog.json').read_text())
    entries = op._market_catalog_entries(catalog)
    return payload, entries


def parse(case, **kwargs):
    payload, entries = case
    stats = {}
    rows = op.rows_from_odds_response(
        payload, {'10194': 'totals'}, home='Croatia', away='England', fixture_id='native-fx',
        expected_kickoff='2026-10-03T16:00:00Z', market_catalog=entries, stats=stats, **kwargs,
    )
    return rows, stats


@pytest.mark.parametrize('field,value,reason', [
    ('fixtureId', 'another-fixture', 'fixture_id_mismatch'),
    ('participant1Name', 'England', 'fixture_participant_disagreement'),
    ('participant2Name', 'Croatia', 'fixture_participant_disagreement'),
    ('participant1Name', 'Croatia U19', 'fixture_participant_disagreement'),
    ('sportId', 2, 'fixture_sport_mismatch'),
    ('statusId', 1, 'fixture_not_prematch'),
    ('startTime', None, 'fixture_kickoff_invalid'),
    ('startTime', '2026-10-03T16:00:00', 'fixture_kickoff_invalid'),
    ('startTime', '2026-10-03T17:00:00Z', 'fixture_kickoff_disagreement'),
])
def test_odds_body_cannot_override_request_identity_sport_or_kickoff(goal_case, field, value, reason):
    goal_case[0][field] = value
    rows, stats = parse(goal_case)
    assert rows == [] and stats == {reason: 1}


def test_healthy_fixture_identity_and_metadata_survive(goal_case):
    rows, _ = parse(goal_case)
    assert len(rows) == 2
    assert all(r['provider_fixture_id'] == 'native-fx' for r in rows)
    assert all(r['provider_sport_id'] == '10' for r in rows)
    assert {(r['market'], r['selection']) for r in rows} == {('ou_2.5', 'over'), ('ou_2.5', 'under')}


@pytest.mark.parametrize('name,period', [
    ('First Half Result', None), ('Second Half Winner', None),
    ('First Half Result', 'fulltime'), ('Over Under Second Half', 'fulltime'),
    ('Total', None), ('Over Under Team 2', None),
])
def test_missing_or_contradictory_period_is_not_fulltime(name, period):
    assert op._classify_catalog_entry({'name': name, 'marketType': 'totals', 'period': period}) == 'unsupported_period'


@pytest.mark.parametrize('name,kind', [
    ('Will There Be Overtime', 'overtime'), ('Total Rounds', 'totals'),
    ('Total Games', 'totals'), ('Total Sets', 'totals'), ('Total Maps', 'totals'),
])
def test_non_goal_units_and_overtime_rejected(name, kind):
    assert op._classify_catalog_entry({'name': name, 'marketType': kind, 'period': 'fulltime'}) == 'unsupported_non_goal'


def test_catalog_sport_cannot_borrow_soccer_goal_semantics(goal_case):
    goal_case[1]['10194']['sportId'] = 2
    rows, stats = parse(goal_case)
    assert rows == [] and stats == {'market_unsupported_sport': 1}


def test_catalog_type_overrules_wrong_team_side_map(goal_case):
    payload, _ = goal_case
    entry = {'name': 'Over Under Team 2', 'marketType': 'teamtotals-team2', 'period': 'fulltime',
             'handicap': 2.5, 'outcomes': {'10194': 'Over', '10195': 'Under'}}
    stats = {}
    rows = op.rows_from_odds_response(payload, {'10194': 'team_totals_home'}, home='Croatia', away='England',
                                      market_catalog={'10194': entry}, stats=stats)
    assert {r['market'] for r in rows} == {'tt_away_2.5'}
    assert stats['market_type_map_disagreement'] == 1


@pytest.mark.parametrize('player,outcome,failure', [
    ({'line': 0}, {}, 'ambiguous'),
    ({'line': 2.5}, {'line': 1.5}, 'ambiguous'),
    ({'line': 2.5, 'total': 1.5}, {}, 'ambiguous'),
    ({'line': float('nan')}, {}, 'unresolved'),
    ({'line': float('inf')}, {}, 'unresolved'),
    ({'line': -1}, {}, 'unresolved'),
    ({'line': True}, {}, 'unresolved'),
])
def test_all_line_evidence_is_checked_including_zero(player, outcome, failure):
    entry = {'handicap': 2.5, 'outcomes': {'10194': 'Over'}}
    assert op._market_selection('totals', 'Over', 'Home', 'Away', None,
                                player0=player, outcome=outcome, catalog_entry=entry, outcome_key='10194') == (None, None, failure)


def test_valid_zero_line_is_preserved_not_replaced():
    assert op._market_selection('totals', 'Over 0', 'Home', 'Away', None,
                                player0={'line': 0}, outcome={'line': '0.0'},
                                catalog_entry={'handicap': 0}) == ('ou_0', 'over', None)


@pytest.mark.parametrize('price', [True, False, float('nan'), float('inf'), -2, 0, 1, 'junk'])
def test_invalid_decimal_prices_cannot_be_counted_as_supply(goal_case, price):
    for outcome in goal_case[0]['bookmakerOdds']['cloudbet']['markets']['10194']['outcomes'].values():
        outcome['players']['0']['price'] = price
    rows, stats = parse(goal_case)
    assert rows == [] and stats == {'invalid_price': 2}


@pytest.mark.parametrize('price', [1.006, 19., 1000.])
def test_valid_prices_are_not_rejected_by_an_odds_band(goal_case, price):
    for outcome in goal_case[0]['bookmakerOdds']['cloudbet']['markets']['10194']['outcomes'].values():
        outcome['players']['0']['price'] = price
    rows, _ = parse(goal_case)
    assert len(rows) == 2 and all(r['odds'] == price for r in rows)


def test_future_provider_change_is_not_a_valid_capture(goal_case):
    for outcome in goal_case[0]['bookmakerOdds']['cloudbet']['markets']['10194']['outcomes'].values():
        outcome['players']['0']['changedAt'] = '2099-01-01T00:00:00Z'
    rows, stats = parse(goal_case)
    assert rows == [] and stats == {'provider_changed_after_capture': 2}


def test_inactive_outcome_cannot_be_rescued_by_active_player(goal_case):
    for outcome in goal_case[0]['bookmakerOdds']['cloudbet']['markets']['10194']['outcomes'].values():
        outcome.update(active=False)
        outcome['players']['0']['active'] = True
    rows, stats = parse(goal_case)
    assert rows == [] and stats == {'outcome_inactive': 2}


@pytest.mark.parametrize('override', [
    {'sportId': 2}, {'statusId': 1}, {'startTime': '2026-10-03T16:00:00'},
])
def test_bad_fixture_board_does_not_spend_an_odds_request(override):
    from datetime import datetime

    import scripts.capture_oddspapi as cap
    fixture = {'fixtureId': 'native-fx', 'startTime': '2026-10-03T16:00:00Z',
               'participant1Name': 'Croatia', 'participant2Name': 'England',
               'sportId': 10, 'statusId': 0, **override}
    cached = cap._board_entry(fixture)
    assert cap._pending_fixtures([cached], {}, datetime.fromisoformat('2026-10-03T14:00:00Z')) == []
    assert all(cached.get(k) == fixture[k] for k in ('sportId', 'statusId'))


@pytest.mark.parametrize('name,failure', [('Over -1.5', 'unresolved'), ('Over NaN', 'unresolved'),
                                         ('Over infinity', 'unresolved'), ('Over 2.5e1', 'ambiguous')])
def test_explicit_invalid_or_different_named_line_cannot_hide_behind_catalog(name, failure):
    assert op._market_selection('totals', name, 'Home', 'Away', None,
                                catalog_entry={'handicap': 2.5}) == (None, None, failure)


def test_self_fixture_identity_is_never_price_supply(goal_case):
    payload, entries = goal_case
    stats = {}
    assert op.rows_from_odds_response(payload, {'10194': 'totals'}, home='Same Club', away='Same Club',
                                      market_catalog=entries, stats=stats) == []
    assert stats == {'fixture_identity_invalid': 1}


@pytest.mark.parametrize('name,kind', [
    ('Over Under Team 1', 'teamtotals-team2'),
    ('Over Under Team 2', 'teamtotals-team1'),
    ('Full Time Result', 'bothteamsscore'),
    ('Both Teams To Score', '1x2'),
    ('Full Time Result', 'totals'),
])
def test_conflicting_catalog_label_and_structured_family_never_choose_a_side(name, kind):
    assert op._classify_catalog_entry({'name': name, 'marketType': kind, 'period': 'fulltime'}) == 'unsupported_catalog_conflict'


def test_unknown_structured_type_cannot_borrow_familiar_goal_label():
    assert op._classify_catalog_entry({'name': 'Over Under Full Time', 'marketType': 'unreviewed-unit',
                                       'period': 'fulltime'}) == 'unsupported_market_type'


def test_explicit_team_type_rejects_conflicting_total_label_but_can_resolve_missing_label():
    assert op._classify_catalog_entry({'name': 'Over Under Full Time', 'marketType': 'teamtotals-team2',
                                       'period': 'fulltime'}) == 'unsupported_catalog_conflict'
    assert op._classify_catalog_entry({'name': '', 'marketType': 'teamtotals-team2',
                                       'period': 'fulltime'}) == 'team_totals_away'


def test_explicit_catalog_scope_never_inherits_process_global_entries(monkeypatch, goal_case):
    monkeypatch.setattr(op, '_MARKET_CATALOG_ENTRIES', {
        '10194': {'name': 'Bookings - Over Under Full Time', 'marketType': 'totals-bookings',
                  'period': 'fulltime', 'handicap': 2.5},
    })
    assert op._catalog_entry('10194', {}) == {}
    assert op._catalog_entry('10194', {'other': {}}) == {}
    assert op._catalog_entry('10194', None)['marketType'] == 'totals-bookings'
    # An explicit scoped real catalog, not a process-global stale entry,
    # determines the quote family and retains healthy documented supply.
    rows, _ = parse(goal_case)
    assert len(rows) == 2 and all(r['market'] == 'ou_2.5' for r in rows)
