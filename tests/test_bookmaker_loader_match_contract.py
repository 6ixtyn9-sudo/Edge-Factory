"""Client-mapped synthetic candidates; not native captures or admitted context."""
from __future__ import annotations

import copy
import json
import socket

import pytest

from edgefactory.sources.bookmaker_context_snapshot import (
    _inspect_loader_payload_evidence,
    inspect_native_loader_state,
)

URL = 'https://statshub.sportradar.com/sportpesa/en/match/75879092'
SECRET = 'DO_NOT_EXPORT'


def envelope():
    return {'match': {
        '_doc': 'sh_match', '_id': 75879092, '_sid': 1, '_rcid': 2,
        '_tid': 41488, '_utid': 444, '_seasonid': 147882,
        '_dt': {'uts': 1793527200, 'tz': 'UTC', 'date': '01/11/26', 'time': '10:00'},
        'teams': {'home': {'_id': 1200717, 'uid': 11, 'name': SECRET + ' home'},
                  'away': {'_id': 624538, 'uid': 12, 'name': SECRET + ' away'}},
        'periods': {'ft': {'home': 1, 'away': 1}}, 'result': {'home': 4, 'away': 3, 'period': 'ap'},
        'status': {'_id': 120, 'name': SECRET},
    }, 'sport': {'_id': 1}, 'realcategory': {'_id': 2}, 'tournament': {'_id': 41488},
        'uniquetournament': {'_id': 444}, 'season': {'_id': 147882}}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('pure client-mapped checks must not make requests')
    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'create_connection', deny)


def inspect(*envelopes):
    state = {'loaderData': {'root': {'cache': list(envelopes), 'cctx': {
        'match': envelope()['match'], 'fishnetToken': SECRET}}}}
    evidence = _inspect_loader_payload_evidence(state, URL)
    assert not evidence['fixture_identity_verified']
    assert not evidence['team_competition_season_binding_verified']
    assert not evidence['regulation_periods_verified']
    assert not evidence['freshness_verified']
    assert not evidence['record_schema_verified']
    assert SECRET not in json.dumps(evidence)
    for value in ('1200717', '624538', '147882', '41488', '1793527200', '01/11/26'):
        assert value not in json.dumps(evidence)
    return evidence['match_candidate_validation']


def checks(value):
    return inspect(value)['candidate_checks'][0]


def test_client_mapped_fields_validate_and_remain_unadmitted():
    data = envelope()
    report = inspect(data, copy.deepcopy(data))
    assert report['requested_event_candidate_count'] == 2
    assert report['other_event_candidate_count'] == report['unsupported_event_id_candidate_count'] == 0
    assert all(v == 'consistent' for v in report['cross_copy_consistency'].values())
    c = report['candidate_checks'][0]
    assert c['client_match_document_tag'] and c['soccer_sport_id']
    assert c['kickoff_epoch_seconds_supported'] and c['kickoff_timezone_recognized']
    assert c['wall_clock_crosscheck_status'] == 'format_not_established'
    assert all(c[k] for k in ('team_ids_distinct', 'team_uids_distinct', 'team_names_distinct'))
    assert all(v['agreement'] == 'equal' for v in c['sibling_metadata_checks'].values())
    assert c['displayed_result_numeric_pair'] and c['displayed_result_marked_ap']
    assert c['status_class'] == 'after_penalties'
    assert c['period_checks']['ft_numeric_pair']
    assert not c['period_checks']['regulation_score_usable']
    assert not report['independent_fixture_corroboration']


@pytest.mark.parametrize('value', [True, False, None, 0, -1, '1793527200', 1793527200.0,
                                  1793527200000, 4102444800, SECRET])
def test_epoch_is_not_coerced_or_rescaled(value):
    data = envelope()
    data['match']['_dt']['uts'] = value
    assert not checks(data)['kickoff_epoch_seconds_supported']
    assert inspect(data)['cross_copy_consistency']['kickoff'] == 'incomplete'


@pytest.mark.parametrize('value', [None, True, 0, SECRET, '/etc/passwd', '../UTC', 'Etc:UTC',
                                  ' ', 'A' * 200])
def test_unknown_or_path_like_timezone_not_assumed_utc(value):
    data = envelope()
    data['match']['_dt']['tz'] = value
    assert not checks(data)['kickoff_timezone_recognized']
    assert checks(data)['kickoff_epoch_seconds_supported']


@pytest.mark.parametrize('value', ['UTC', 'Etc/UTC', 'Africa/Johannesburg'])
def test_explicit_supported_zone_can_be_recognized_without_claiming_wall_clock_agreement(value):
    data = envelope()
    data['match']['_dt']['tz'] = value
    assert checks(data)['kickoff_timezone_recognized']
    assert checks(data)['wall_clock_crosscheck_status'] == 'format_not_established'


@pytest.mark.parametrize('key,sibling', [('_sid', 'sport'), ('_rcid', 'realcategory'),
                                        ('_tid', 'tournament'), ('_utid', 'uniquetournament'),
                                        ('_seasonid', 'season')])
def test_sibling_metadata_conflicts_are_not_ignored(key, sibling):
    data = envelope()
    data[sibling]['_id'] += 1
    c = checks(data)['sibling_metadata_checks'][key]
    assert c['match_id_supported'] and c['sibling_id_supported']
    assert c['agreement'] == 'conflicting'


@pytest.mark.parametrize('value', [None, True, 147882.0, '0147882', 0, SECRET])
def test_invalid_season_id_never_becomes_zero_or_default_identity(value):
    data = envelope()
    data['match']['_seasonid'] = value
    c = checks(data)['sibling_metadata_checks']['_seasonid']
    assert not c['match_id_supported'] and c['agreement'] == 'missing_or_unsupported'
    assert inspect(data)['cross_copy_consistency']['_seasonid'] == 'incomplete'


@pytest.mark.parametrize('side', ['home', 'away'])
@pytest.mark.parametrize('key', ['_id', 'uid', 'name'])
def test_missing_team_field_is_unavailable_not_a_default(side, key):
    data = envelope()
    del data['match']['teams'][side][key]
    assert inspect(data)['cross_copy_consistency']['teams'] == 'incomplete'


def test_team_id_and_uid_domains_are_not_interchanged():
    data = envelope()
    data['match']['teams']['home']['uid'] = data['match']['teams']['away']['_id']
    assert checks(data)['team_ids_distinct'] and checks(data)['team_uids_distinct']
    data['match']['teams']['away']['uid'] = data['match']['teams']['home']['uid']
    assert not checks(data)['team_uids_distinct']
    assert checks(data)['team_ids_distinct']


def test_same_team_pair_never_becomes_valid_distinct_opponents():
    data = envelope()
    data['match']['teams']['away'] = copy.deepcopy(data['match']['teams']['home'])
    c = checks(data)
    assert not c['team_ids_distinct'] and not c['team_uids_distinct'] and not c['team_names_distinct']


@pytest.mark.parametrize('domain', ['kickoff', 'teams', '_sid', '_rcid', '_tid', '_utid', '_seasonid'])
def test_requested_match_copies_with_conflicting_identity_or_time_are_flagged(domain):
    first, second = envelope(), envelope()
    if domain == 'kickoff':
        second['match']['_dt']['uts'] += 1
    elif domain == 'teams':
        second['match']['teams']['home'], second['match']['teams']['away'] = (
            second['match']['teams']['away'], second['match']['teams']['home'])
    else:
        second['match'][domain] += 1
    assert inspect(first, second)['cross_copy_consistency'][domain] == 'conflicting'


def test_history_and_invalid_ids_are_accounted_for_but_not_projected_as_requested_match():
    target, history, bad = envelope(), envelope(), envelope()
    history['match']['_id'] = 99
    bad['match']['_id'] = True
    report = inspect(target, history, bad)
    assert report['requested_event_candidate_count'] == 1
    assert report['other_event_candidate_count'] == 1
    assert report['unsupported_event_id_candidate_count'] == 1
    assert all(v == 'single_candidate' for v in report['cross_copy_consistency'].values())


@pytest.mark.parametrize('value', [None, True, '4', 4.0, -1, 1000])
def test_displayed_result_is_strict_and_never_substituted_for_ft(value):
    data = envelope()
    data['match']['result']['home'] = value
    c = checks(data)
    assert not c['displayed_result_numeric_pair']
    assert c['period_checks']['ft_numeric_pair']
    assert not c['period_checks']['regulation_score_usable']


def test_unknown_or_extra_time_periods_are_reported_without_semantic_promotion():
    data = envelope()
    data['match']['periods'] = {'ot': {'home': 1, 'away': 0}, 'ap': {'home': 4, 'away': 3},
                                SECRET: {'home': 2, 'away': 1}}
    c = checks(data)['period_checks']
    assert c['ot_present'] and c['ap_present'] and c['other_period_key_count'] == 1
    assert not c['ft_present'] and not c['ft_numeric_pair'] and not c['regulation_score_usable']


@pytest.mark.parametrize('value,label', [(0, 'not_started'), (100, 'ended'),
                                        (110, 'after_extra_time'), (120, 'after_penalties'),
                                        (True, 'unresolved'), ('100', 'unresolved'),
                                        (None, 'unresolved'), (99, 'unresolved')])
def test_client_status_codes_do_not_coerce_or_assert_a_regulation_result(value, label):
    data = envelope()
    data['match']['status']['_id'] = value
    assert checks(data)['status_class'] == label
    assert not checks(data)['period_checks']['regulation_score_usable']


def test_candidate_cap_does_not_report_complete_cross_copy_consistency():
    report = inspect(*(envelope() for _ in range(25)))
    assert report['candidate_limit_reached']
    assert report['requested_event_candidate_count'] == 24
    assert len(report['candidate_checks']) == 24
    assert all(v == 'incomplete' for v in report['cross_copy_consistency'].values())


def test_public_decoder_exports_no_native_values_and_keeps_all_holds():
    state = {'loaderData': {'route-name-with-' + SECRET: {'value': {'data': envelope()}}}}
    body = ('<script type="application/json">' + json.dumps(state) + '</script>').encode()
    receipt = inspect_native_loader_state(body, URL + '/statistics')
    assert receipt['decoded_loader_state_count'] == 1
    assert receipt['decoded_context_row_count'] == receipt['admitted_rows'] == receipt['api_requests_made'] == 0
    assert receipt['kickoff_utc'] is None and receipt['fixture_binding_status'] == 'not_verified'
    assert not receipt['javascript_executed']
    assert receipt['payload_evidence']['match_candidate_validation']['requested_event_candidate_count'] == 1
    assert SECRET not in json.dumps(receipt)


def test_client_mapped_names_are_visible_not_replaced_with_opaque():
    state = {'loaderData': {'root': {'data': envelope()}}}
    evidence = _inspect_loader_payload_evidence(state, URL)
    shape = next(s['shape'] for s in evidence['sections'] if s['section'] == 'match')
    paths = [e['path'] for e in shape]
    for key in ('_doc', '_sid', '_rcid', '_tid', '_utid', '_seasonid', 'result'):
        assert [key] in paths
