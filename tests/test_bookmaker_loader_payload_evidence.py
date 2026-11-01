"""Synthetic candidate shapes only; none is an asserted native StatsHub schema."""
from __future__ import annotations

import json
import socket

import pytest

from edgefactory.sources.bookmaker_context_snapshot import (
    _inspect_loader_payload_evidence,
    inspect_native_loader_state,
)

URL = 'https://statshub.sportradar.com/sportpesa/en/match/75879092'
SECRET = 'DO_NOT_EXPORT_NATIVE_VALUES'


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('embedded evidence must not make requests')
    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'create_connection', deny)


def inspect(payload, url=URL):
    state = {'loaderData': {'root': {
        'cctx': {'fishnetToken': SECRET}, 'cache': payload}}, 'errors': None}
    body = ('<script type="application/json">' + json.dumps(state) + '</script>').encode()
    receipt = inspect_native_loader_state(body, url)
    assert receipt['decoded_loader_state_count'] == 1
    assert receipt['admitted_rows'] == receipt['decoded_context_row_count'] == 0
    assert receipt['fixture_binding_status'] == 'not_verified'
    assert receipt['kickoff_utc'] is None
    assert not receipt['javascript_executed'] and receipt['api_requests_made'] == 0
    evidence = receipt['payload_evidence']
    assert evidence['status'] == 'candidate_shape_and_field_syntax_only'
    for field in ('record_schema_verified', 'fixture_identity_verified',
                  'team_competition_season_binding_verified', 'regulation_periods_verified',
                  'freshness_verified', 'collection_permission_verified'):
        assert evidence[field] is False
    assert SECRET not in json.dumps(receipt)
    return evidence


def section(evidence, name):
    return next(s for s in evidence['sections'] if s['section'] == name)


def field(evidence, name, path):
    return next(s for s in section(evidence, name)['shape'] if s['path'] == path)


def test_query_cache_sections_produce_safe_schema_and_selected_field_checks():
    payload = {'dehydratedState': {'queries': [{
        'queryKey': [SECRET], 'queryHash': SECRET,
        'state': {'data': {'match': {
            '_id': 75879092, 'name': SECRET,
            'seasonId': '147882', 'tournamentId': 41488,
            'kickoff': '2026-11-01T10:00:00Z',
            'teams': {'home': {'_id': 1200717, 'name': SECRET},
                      'away': {'_id': 624538, 'name': SECRET}},
            'results': {'AP': {'home': 4, 'away': 3}, 'FT': {'home': 1, 'away': 1}},
        }}}}]}}
    evidence = inspect(payload)
    assert field(evidence, 'match', ['_id'])['equals_requested_event_id']
    assert field(evidence, 'match', ['kickoff'])['explicit_zone_timestamp_syntax']
    assert field(evidence, 'match', ['seasonId'])['positive_decimal_id_syntax']
    assert field(evidence, 'teams', ['home', '_id'])['positive_decimal_id_syntax']
    assert field(evidence, 'results', ['AP', 'home'])['nonnegative_integer_score_syntax']
    assert {'queries', 'match', 'teams', 'results'} <= {s['section'] for s in evidence['sections']}
    encoded = json.dumps(evidence)
    for private in ('75879092', '147882', '41488', '1200717', '624538', '2026-11-01',
                    'queryKey', 'queryHash'):
        assert private not in encoded


@pytest.mark.parametrize('value,valid,equal', [
    (75879092, True, True), ('75879092', True, True),
    (75879093, True, False), ('75879093', True, False),
    (True, False, False), (False, False, False), (75879092.0, False, False),
    (None, False, False), (0, False, False), (-1, False, False),
    ('075879092', False, False), ('75879092 ', False, False),
    ('+75879092', False, False), ('1e3', False, False),
    (10**12, False, False), ('1000000000000', False, False),
    (SECRET, False, False),
])
def test_candidate_id_syntax_never_coerces_unavailable_or_conflicting_id(value, valid, equal):
    entry = field(inspect({'match': {'id': value}}), 'match', ['id'])
    assert entry['positive_decimal_id_syntax'] is valid
    assert entry['equals_requested_event_id'] is equal


def test_conflicting_ids_are_both_visible_and_never_promoted_to_binding():
    evidence = inspect({'match': {'id': 75879092, 'eventId': 99}}, URL + '/statistics')
    assert field(evidence, 'match', ['id'])['equals_requested_event_id']
    assert not field(evidence, 'match', ['eventId'])['equals_requested_event_id']


@pytest.mark.parametrize('value,valid', [
    ('2026-11-01T10:00:00Z', True), ('2026-11-01T12:00:00+02:00', True),
    ('2026-11-01T10:00:00', False), ('2026-11-01', False),
    ('10:00 AM', False), (1793527200, False), (1793527200000, False),
    (True, False), (None, False), (SECRET, False), ('x' * 129, False),
    ('2026-02-30T10:00:00Z', False),
])
def test_timestamp_syntax_requires_explicit_zone_not_epoch_guesses(value, valid):
    entry = field(inspect({'match': {'kickoff': value}}), 'match', ['kickoff'])
    assert entry['explicit_zone_timestamp_syntax'] is valid


@pytest.mark.parametrize('value,valid', [
    (0, True), (3, True), (999, True), (1000, False), (-1, False),
    (True, False), (False, False), (None, False), ('3', False), (3.0, False),
])
def test_result_syntax_does_not_assert_regulation_or_convert_missing_to_zero(value, valid):
    evidence = inspect({'results': {'AET': {'home': value}}})
    assert field(evidence, 'results', ['AET', 'home'])['nonnegative_integer_score_syntax'] is valid
    assert not evidence['regulation_periods_verified']


def test_sensitive_branches_and_arbitrary_route_keys_never_become_payload_evidence():
    state = {'loaderData': {SECRET: {
        'cctx': {'match': {'id': 75879092}},
        'queryKey': {'teams': []}, 'queryHash': {'standings': []},
        'Authorization': {'results': []}, 'TOKEN': {'tables': []},
        SECRET: {'match': {'id': 99, SECRET: SECRET}},
    }}}
    evidence = _inspect_loader_payload_evidence(state, URL)
    assert len(evidence['sections']) == 1
    assert section(evidence, 'match')['location'] == ['route', 'opaque', 'match']
    assert SECRET not in json.dumps(evidence)
    assert field(evidence, 'match', [])['unlisted_field_count'] == 1


def test_unknown_keys_are_counted_not_exported_and_not_used_for_identity():
    evidence = inspect({'match': {SECRET: 75879092, 'teams': {SECRET: SECRET}}})
    assert field(evidence, 'match', [])['unlisted_field_count'] == 1
    assert not any('equals_requested_event_id' in e for e in section(evidence, 'match')['shape'])


def test_samples_and_section_caps_are_explicit_and_output_bounded():
    evidence = inspect({'queries': [{'match': {'id': i}} for i in range(1000)]})
    assert evidence['section_limit_reached']
    assert len(evidence['sections']) == 24
    queries = section(evidence, 'queries')
    assert queries['shape_truncated_or_sampled']
    assert queries['shape'][0]['length'] == 1000
    assert queries['shape'][0]['sampled_item_count'] == 3
    assert all(len(s['shape']) <= 48 for s in evidence['sections'])
    assert len(json.dumps(evidence)) < 40000


def test_depth_and_wide_shape_truncation_are_explicit():
    nested = {'home': {'home': {'home': {'home': {'home': {'id': 1}}}}}}
    evidence = inspect({'match': nested})
    assert section(evidence, 'match')['shape_truncated_or_sampled']
    assert all(len(e['path']) <= 4 for e in section(evidence, 'match')['shape'])


def test_special_wire_values_remain_distinct_in_evidence():
    from edgefactory.sources.bookmaker_context_snapshot import (
        _LOADER_HOLE,
        _LOADER_NAN,
        _LOADER_POSITIVE_INFINITY,
        _LOADER_UNDEFINED,
    )
    state = {'loaderData': {'root': {'match': {
        'id': _LOADER_UNDEFINED, 'seasonId': _LOADER_NAN,
        'tournamentId': _LOADER_POSITIVE_INFINITY, 'teams': [_LOADER_HOLE, None],
    }}}}
    evidence = _inspect_loader_payload_evidence(state, URL)
    for path, kind in [(['id'], 'undefined'), (['seasonId'], 'nan'),
                       (['tournamentId'], 'positive_infinity')]:
        entry = field(evidence, 'match', path)
        assert entry['kind'] == kind and not entry['positive_decimal_id_syntax']
    shapes = section(evidence, 'teams')['shape']
    assert [e['kind'] for e in shapes] == ['array', 'array_hole', 'null']


def test_shared_aliases_do_not_expand_exponentially_or_claim_multiple_records():
    node = {'match': {'id': 75879092}}
    for _ in range(40):
        node = [node, node]
    evidence = _inspect_loader_payload_evidence({'loaderData': {'root': node}}, URL)
    assert len(evidence['sections']) == 1
    assert len(section(evidence, 'match')['location']) <= 12


def test_unknown_field_values_have_bounded_anonymous_shapes_not_lost_evidence():
    evidence = inspect({'match': {
        SECRET: {'home': {'id': 7}, 'away': {'id': 8}},
        'Authorization': {'results': {'FT': 999}},
    }})
    assert field(evidence, 'match', ['opaque', 'home', 'id'])['positive_decimal_id_syntax']
    assert field(evidence, 'match', ['opaque', 'away', 'id'])['positive_decimal_id_syntax']
    assert not any('FT' in e['path'] for e in section(evidence, 'match')['shape'])
    assert field(evidence, 'match', [])['unlisted_sampled_field_count'] == 1


def test_many_unknown_keys_do_not_inflate_receipt_or_leak_names():
    evidence = inspect({'match': {f'{SECRET}{i}': i for i in range(1000)}})
    root = field(evidence, 'match', [])
    assert root['unlisted_field_count'] == 1000
    assert root['unlisted_sampled_field_count'] == 3
    assert section(evidence, 'match')['shape_truncated_or_sampled']
    assert len(section(evidence, 'match')['shape']) == 4
