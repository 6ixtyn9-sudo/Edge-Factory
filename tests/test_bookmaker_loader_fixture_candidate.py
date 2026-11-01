"""Consolidated synthetic fixture extraction, never native stats or admission proof."""
from __future__ import annotations

import copy
import json
import socket

import pytest

from edgefactory.sources.bookmaker_context_snapshot import (
    _extract_loader_fixture_candidate,
    _loader_protocol_fields,
    inspect_native_loader_state,
)

URL = 'https://statshub.sportradar.com/sportpesa/en/match/75879092'
OBSERVED = '2026-11-01T09:00:00Z'
SECRET = 'NEVER_EXPORT_STATE_OR_NAMES'


def envelope(status=0):
    return {'match': {
        '_doc': 'match', '_id': 75879092, '_sid': 1, '_rcid': 2, '_tid': 41488,
        '_utid': 444, '_seasonid': 147882,
        '_dt': {'uts': 1793527200, 'tz': 'UTC', 'date': SECRET, 'time': SECRET},
        'teams': {'home': {'_id': 1200717, 'uid': 11, 'name': SECRET + ' home'},
                  'away': {'_id': 624538, 'uid': 12, 'name': SECRET + ' away'}},
        'periods': {'p1': {'home': 0, 'away': 0}},
        'result': {'home': 0, 'away': 0}, 'status': {'_id': status, 'name': SECRET},
        'updated_uts': 1793523540,
    }, 'sport': {'_id': 1}, 'realcategory': {'_id': 2}, 'tournament': {'_id': 41488},
        'uniquetournament': {'_id': 444}, 'season': {'_id': 147882}}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('fixture extraction is pure embedded-state handling')
    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'create_connection', deny)


def extract(*data, observed=OBSERVED, limit=False, errors=False):
    result = _extract_loader_fixture_candidate(
        [(d['match'], d) for d in data], '75879092', limit, source_url=URL,
        observed_at_utc=observed, page_errors=errors)
    assert SECRET not in json.dumps(result)
    for hold in ('independent_fixture_corroboration_required', 'freshness_not_verified',
                 'collection_permission_unresolved', 'historical_form_not_extracted',
                 'standings_not_extracted', 'regulation_results_not_verified',
                 'production_admission_not_implemented'):
        assert hold in result['hold_reasons']
    return result


def test_extracts_one_deduplicated_requested_fixture_with_selected_normalized_fields():
    first, second, third = envelope(), envelope(), envelope()
    # Sparse cache copies may lack sibling objects, but may not disagree.
    second.pop('season')
    third = {'match': third['match']}
    r = extract(first, second, third)
    assert r['status'] == 'extracted_unadmitted_fixture_candidate'
    assert r['candidate_fixture_count'] == 1 and r['pre_match_candidate']
    assert r['fixture'] == {
        'event_id': '75879092', 'source_url': URL, 'kickoff_utc': '2026-11-01T10:00:00+00:00',
        'observed_at_utc': '2026-11-01T09:00:00+00:00',
        'source_status': 'not_started', 'source_lifecycle': 'pre_match',
        'source_update_age_seconds': 60,
        'home': {'team_id': '1200717', 'team_uid': '11'},
        'away': {'team_id': '624538', 'team_uid': '12'},
        '_seasonid': '147882', '_sid': '1', '_tid': '41488', '_utid': '444', '_rcid': '2'}
    assert 'result' not in r['fixture'] and 'periods' not in r['fixture']


@pytest.mark.parametrize('code,name', [(6, 'first_half'), (7, 'second_half'), (20, 'started'),
                                      (31, 'halftime'), (32, 'awaiting_extra_time'),
                                      (41, 'first_extra'), (50, 'penalties')])
def test_live_fixtures_are_extracted_but_explicitly_not_pre_match(code, name):
    r = extract(envelope(code))
    assert r['candidate_fixture_count'] == 1 and not r['pre_match_candidate']
    assert r['fixture']['source_status'] == name
    assert r['fixture']['source_lifecycle'] == 'live'
    assert 'source_status_not_pre_match' in r['hold_reasons']


@pytest.mark.parametrize('code', [99, 100, 110, 120])
def test_finished_status_does_not_promote_displayed_or_period_scores_to_regulation(code):
    r = extract(envelope(code))
    assert r['fixture']['source_lifecycle'] == 'finished' and not r['pre_match_candidate']
    assert 'regulation_results_not_verified' in r['hold_reasons']
    assert 'score' not in r['fixture']


@pytest.mark.parametrize('code', [60, 61, 70, 80, 81, 90, 91])
def test_inactive_statuses_never_become_pre_match_from_future_kickoff(code):
    r = extract(envelope(code))
    assert r['fixture']['source_lifecycle'] == 'inactive' and not r['pre_match_candidate']


@pytest.mark.parametrize('flag', ['postponed', 'cancelled', 'canceled', 'walkover',
                                  'tobeannounced', 'removed', 'decidedbyfa'])
def test_source_exception_flags_override_not_started_status(flag):
    data = envelope()
    data['match'][flag] = True
    r = extract(data)
    assert not r['pre_match_candidate'] and r['fixture']['source_lifecycle'] == 'inactive'


@pytest.mark.parametrize('value', [True, False, '7', 7.0, None, -1, 999999])
def test_unknown_or_wrong_type_statuses_are_held_not_guessed(value):
    r = extract(envelope(value))
    assert r['candidate_fixture_count'] == 0 and r['fixture'] is None
    assert 'candidate_status_unknown_or_conflicting' in r['hold_reasons']


@pytest.mark.parametrize('observed', [None, '', SECRET, True, '2026-11-01T09:00:00'])
def test_missing_or_zone_free_observation_never_produces_pre_match_eligibility(observed):
    r = extract(envelope(), observed=observed)
    assert r['candidate_fixture_count'] == 1 and not r['pre_match_candidate']
    assert r['fixture']['observed_at_utc'] is None
    assert 'observation_time_unavailable' in r['hold_reasons']


@pytest.mark.parametrize('observed', ['2026-11-01T10:00:00Z', '2026-11-02T09:00:00Z'])
def test_past_or_equal_kickoff_held_even_with_source_not_started(observed):
    r = extract(envelope(), observed=observed)
    assert not r['pre_match_candidate']
    assert 'kickoff_not_after_observation' in r['hold_reasons']


@pytest.mark.parametrize('update', [True, False, None, 0, '1793523540', 1793523540.0,
                                   1793523540000])
def test_invalid_or_fallback_source_update_remains_unavailable(update):
    data = envelope()
    data['match']['updated_uts'] = update
    assert extract(data)['fixture']['source_update_age_seconds'] is None


def test_future_source_update_is_not_silently_fresh():
    data = envelope()
    data['match']['updated_uts'] += 120
    r = extract(data)
    assert r['fixture']['source_update_age_seconds'] == -60 and not r['pre_match_candidate']
    assert 'source_update_after_observation' in r['hold_reasons']


def test_disagreeing_update_timestamps_are_not_replaced_by_capture_time():
    first, second = envelope(), envelope()
    second['match']['updated_uts'] -= 1
    assert extract(first, second)['fixture']['source_update_age_seconds'] is None


@pytest.mark.parametrize('domain', ['kickoff', 'teams', '_seasonid', '_tid', 'status'])
def test_conflicting_copies_do_not_select_first_or_majority(domain):
    first, second = envelope(), envelope()
    if domain == 'kickoff':
        second['match']['_dt']['uts'] += 1
    elif domain == 'teams':
        second['match']['teams']['home']['_id'] += 1
    elif domain == 'status':
        second['match']['status']['_id'] = 7
    else:
        second['match'][domain] += 1
    r = extract(first, second, copy.deepcopy(first))
    assert r['candidate_fixture_count'] == 0 and r['fixture'] is None


def test_even_one_conflicting_sibling_blocks_an_otherwise_complete_envelope():
    first, second = envelope(), envelope()
    second['season']['_id'] += 1
    assert 'sibling_metadata_conflict' in extract(first, second)['hold_reasons']


def test_one_complete_envelope_is_required_not_merged_from_different_parents():
    first, second = envelope(), envelope()
    first.pop('season')
    second.pop('sport')
    r = extract(first, second)
    assert 'complete_sibling_binding_missing' in r['hold_reasons']
    assert r['candidate_fixture_count'] == 0


@pytest.mark.parametrize('tag', ['match', 'sh_match'])
def test_fixed_document_tag_vocabulary_not_arbitrary_values(tag):
    data = envelope()
    data['match']['_doc'] = tag
    assert extract(data)['candidate_fixture_count'] == 1
    data['match']['_doc'] = SECRET
    assert 'unsupported_document_or_sport' in extract(data)['hold_reasons']


@pytest.mark.parametrize('field', ['_id', 'uid', 'name'])
def test_identical_opponents_do_not_extract(field):
    data = envelope()
    data['match']['teams']['away'][field] = data['match']['teams']['home'][field]
    assert 'candidate_team_or_timestamp_invalid' in extract(data)['hold_reasons']


@pytest.mark.parametrize('kwargs', [{'limit': True}, {'errors': True}])
def test_truncation_or_page_errors_never_yield_candidate(kwargs):
    assert extract(envelope(), **kwargs)['candidate_fixture_count'] == 0


def test_other_events_are_not_admitted_or_mistaken_for_requested_match():
    data = envelope()
    data['match']['_id'] = 99
    assert extract(data)['candidate_fixture_count'] == 0
    assert extract(data, envelope())['candidate_fixture_count'] == 1


def test_finite_period_key_classification_never_exports_unknown_keys_or_scores():
    data = envelope()['match']
    data['periods'] = {'HT': {'home': 1, 'away': 2}, 'p1': {}, SECRET: {SECRET: SECRET}}
    fields = _loader_protocol_fields(data)
    assert fields['recognized_period_keys'] == ['ht', 'p1']
    assert fields['unrecognized_period_key_count'] == 1
    assert SECRET not in json.dumps(fields)


def test_public_receipt_separates_value_free_evidence_from_selected_candidate_fields():
    state = {'loaderData': {'root': {'data': envelope(), 'cctx': {'fishnetToken': SECRET}}}}
    body = ('<script type="application/json">' + json.dumps(state) + '</script>').encode()
    r = inspect_native_loader_state(body, URL, observed_at_utc=OBSERVED)
    assert r['decoded_loader_state_count'] == 1
    assert r['fixture_candidate']['candidate_fixture_count'] == 1
    assert r['decoded_context_row_count'] == r['admitted_rows'] == r['api_requests_made'] == 0
    assert r['kickoff_utc'] is None and r['fixture_binding_status'] == 'not_verified'
    assert not r['javascript_executed'] and SECRET not in json.dumps(r)
    assert '1200717' not in json.dumps(r['payload_evidence'])
    assert r['fixture_candidate']['fixture']['home']['team_id'] == '1200717'
