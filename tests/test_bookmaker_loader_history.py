"""Synthetic record contracts, not native form coverage or regulation proof."""
from __future__ import annotations

import copy
import json
import socket

import pytest

from edgefactory.sources.bookmaker_context_snapshot import (
    _extract_loader_fixture_candidate,
    _extract_loader_history,
    inspect_native_loader_state,
)

URL = 'https://statshub.sportradar.com/sportpesa/en/match/75879092'
OBSERVED = '2026-11-01T09:00:00Z'
SECRET = 'DO_NOT_EXPORT_PRIVATE_STATE'


def envelope(event=75879092, *, history=False):
    return {'match': {
        '_doc': 'match', '_id': event, '_sid': 1, '_rcid': 2, '_tid': 3,
        '_utid': 4, '_seasonid': 5,
        '_dt': {'uts': 1793437200 if history else 1793527200, 'tz': 'UTC'},
        'teams': {'home': {'_id': 10, 'uid': 100, 'name': SECRET + ' home'},
                  'away': {'_id': 20, 'uid': 200, 'name': SECRET + ' away'}},
        'status': {'_id': 100 if history else 0, 'name': SECRET},
        'periods': {'ft': {'home': 0, 'away': 1}},
        'result': {'home': 0, 'away': 1}, 'ended_uts': 1793444400,
        'updated_uts': 1793523540,
    }, 'sport': {'_id': 1}, 'realcategory': {'_id': 2}, 'tournament': {'_id': 3},
        'uniquetournament': {'_id': 4}, 'season': {'_id': 5}}


def history(event=123):
    return envelope(event, history=True)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('offline source-record handling must not use a socket')
    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'create_connection', deny)


def fixture_candidate():
    target = envelope()
    return _extract_loader_fixture_candidate(
        [(target['match'], target)], '75879092', False,
        source_url=URL, observed_at_utc=OBSERVED)


def extract(*records, observed=OBSERVED, candidate=None, extra=None, errors=None):
    state = {'loaderData': {'target': envelope(), 'records': list(records), **(extra or {})},
             'errors': errors}
    result = _extract_loader_history(
        state, fixture_candidate() if candidate is None else candidate, observed_at_utc=observed)
    assert SECRET not in json.dumps(result)
    assert result['usable_form_rows'] == result['admitted_rows'] == 0
    assert 'regulation_results_not_verified' in result['hold_reasons']
    return result


def test_extracts_actual_deduplicated_source_score_row_not_an_aggregate_or_admission():
    row = history()
    result = extract(row, copy.deepcopy(row))
    assert result['status'] == 'extracted_unadmitted_history_score_candidates'
    assert result['candidate_record_count'] == 1
    assert result['scan_complete'] and not result['held_event_count']
    record = result['records'][0]
    assert record['event_id'] == '123'
    assert record['source_ft_score'] == {'home': 0, 'away': 1}
    assert record['ended_at_utc'] == '2026-10-31T11:00:00+00:00'
    assert record['fixture_team_bindings'] == [
        {'fixture_side': 'home', 'record_side': 'home'},
        {'fixture_side': 'away', 'record_side': 'away'}]
    assert record['regulation_verified'] is record['admitted'] is False
    assert 'form' not in record
    assert 'result' not in record and 'periods' not in record


def test_no_rows_is_unsupported_structure_not_zero_form_or_absence_proof():
    result = extract()
    assert result['status'] == 'no_supported_embedded_history_rows'
    assert result['records'] == [] and result['scan_complete']
    assert 'historical_sample_completeness_unverified' in result['hold_reasons']


@pytest.mark.parametrize('observed', [None, '', SECRET, True, '2026-11-01T09:00:00'])
def test_capture_time_must_be_explicit_and_zoned(observed):
    result = extract(history(), observed=observed)
    assert not result['records'] and not result['scan_complete']
    assert result['status'] == 'history_fixture_or_observation_unresolved'


def test_held_anchor_cannot_bind_history():
    assert not extract(history(), candidate={'fixture': None})['records']


@pytest.mark.parametrize('code', [0, 6, 7, 20, 60, 70, 90, 91, 99, 110, 120])
def test_live_inactive_result_only_extra_time_and_penalties_are_not_ordinary_finished_history(code):
    row = history()
    row['match']['status']['_id'] = code
    assert not extract(row)['records']


@pytest.mark.parametrize('flag', ['postponed', 'cancelled', 'canceled', 'walkover',
                                  'tobeannounced', 'removed', 'decidedbyfa'])
def test_exception_flags_prevent_history_extraction(flag):
    row = history()
    row['match'][flag] = True
    assert not extract(row)['records']


@pytest.mark.parametrize('ended', [True, False, None, 0, '1793444400', 1793444400.0,
                                  1793444400000, 1793437200, 1793437100,
                                  1793523600, 1793527200])
def test_completion_not_inferred_from_kickoff_status_boolean_or_capture(ended):
    row = history()
    row['match']['ended_uts'] = ended
    result = extract(row)
    assert not result['records']
    assert result['held_reasons'] == {'history_completion_not_before_cutoff': 1}


def test_target_kickoff_also_bounds_history_when_capture_is_later():
    row = history()
    row['match']['ended_uts'] = 1793527200
    assert not extract(row, observed='2026-11-02T09:00:00Z')['records']


def test_disagreeing_completion_times_reject_event_not_just_one_copy():
    first, second = history(), history()
    second['match']['ended_uts'] += 1
    assert not extract(first, second)['records']


@pytest.mark.parametrize('ft', [None, {}, {'home': 0}, {'home': False, 'away': 1},
                               {'home': '0', 'away': 1}, {'home': -1, 'away': 1},
                               {'home': 1000, 'away': 1}, {'home': 0.0, 'away': 1}])
def test_ft_score_is_required_and_not_coerced_or_defaulted(ft):
    row = history()
    row['match']['periods']['ft'] = ft
    assert not extract(row)['records']


@pytest.mark.parametrize('periods', [None, {}, {'p1': {'home': 0, 'away': 1}},
                                    {'FT': {'home': 0, 'away': 1}}])
def test_display_score_or_first_period_never_substitutes_for_ft(periods):
    row = history()
    row['match']['periods'] = periods
    assert not extract(row)['records']


@pytest.mark.parametrize('key', ['ot', 'ap'])
def test_extra_period_presence_is_held_even_if_null_or_scores_look_final(key):
    row = history()
    row['match']['periods'][key] = None
    assert not extract(row)['records']


def test_displayed_result_must_agree_with_explicit_ft_and_all_copies():
    first, second = history(), history()
    first['match']['result']['away'] = 2
    assert not extract(first)['records']
    second['match']['periods']['ft']['away'] = 2
    second['match']['result']['away'] = 2
    assert not extract(history(), second)['records']


def test_shared_uid_is_binding_domain_not_season_specific_team_id():
    row = history()
    row['match']['teams']['home']['uid'] = 999
    row['match']['teams']['away']['uid'] = 998
    # Both _ids still match the target. That is insufficient.
    assert not extract(row)['records']


def test_same_season_uid_with_conflicting_team_id_is_held():
    row = history()
    row['match']['teams']['home']['_id'] = 999
    assert not extract(row)['records']


def test_different_season_team_id_can_change_without_conflating_domains():
    row = history()
    row['match']['_seasonid'] = 6
    row['season']['_id'] = 6
    row['match']['teams']['home']['_id'] = 999
    row['match']['teams']['away']['_id'] = 998
    result = extract(row)
    assert result['candidate_record_count'] == 1
    assert result['records'][0]['_seasonid'] == '6'
    assert result['records'][0]['home'] == {'team_id': '999', 'team_uid': '100'}


def test_one_fixture_team_can_be_on_the_other_side_against_an_outside_opponent():
    row = history()
    row['match']['teams']['home'] = {'_id': 30, 'uid': 300, 'name': SECRET + ' third'}
    row['match']['teams']['away'] = copy.deepcopy(envelope()['match']['teams']['home'])
    result = extract(row)
    assert result['records'][0]['fixture_team_bindings'] == [
        {'fixture_side': 'home', 'record_side': 'away'}]


@pytest.mark.parametrize('domain', ['season', 'sport', 'realcategory', 'tournament', 'uniquetournament'])
def test_historical_sibling_domain_conflicts_are_not_borrowed_from_target(domain):
    row = history()
    row[domain]['_id'] = 999
    assert not extract(row)['records']


def test_incomplete_parents_are_not_stitched_together():
    first, second = history(), history()
    del first['season']
    del second['sport']
    assert not extract(first, second)['records']


def test_sparse_duplicate_copy_is_allowed_only_with_complete_consistent_parent():
    row = history()
    assert extract(row, {'match': copy.deepcopy(row['match'])})['candidate_record_count'] == 1


@pytest.mark.parametrize('field', ['_seasonid', '_tid', '_utid', '_sid', '_rcid'])
def test_cross_copy_identity_conflicts_hold_entire_event(field):
    first, second = history(), history()
    second['match'][field] = 999
    assert not extract(first, second)['records']


def test_bad_event_does_not_hide_an_independent_good_history_event():
    good, bad = history(123), history(124)
    bad['match']['ended_uts'] = True
    result = extract(good, bad)
    assert result['candidate_record_count'] == result['held_event_count'] == 1
    assert result['records'][0]['event_id'] == '123'


def test_history_private_branches_and_query_keys_are_never_used_as_data():
    for key in ('cctx', 'errors', 'queryKey', 'queryHash', 'meta', 'headers', 'credentials'):
        assert not extract(extra={key: history()})['records']


def test_excess_copies_or_scan_limit_never_yield_partial_success():
    assert not extract(*[history() for _ in range(25)])['records']
    result = extract(*[history(i + 1) for i in range(257)])
    assert not result['scan_complete'] and not result['records']
    assert result['status'] == 'history_scan_limit'


def test_loader_page_errors_hold_rows():
    assert not extract(history(), errors={'opaque': SECRET})['records']


def test_target_match_is_never_its_own_history_even_if_finished():
    assert not extract(envelope(history=True))['records']


def test_newest_first_ordering_deterministic_not_provider_array_order():
    old, new = history(100), history(200)
    new['match']['_dt']['uts'] += 100
    new['match']['ended_uts'] += 100
    assert [r['event_id'] for r in extract(old, new)['records']] == ['200', '100']


def test_inspector_exports_bounded_numeric_records_from_same_body_without_raw_state():
    state = {'loaderData': {'root': {'cctx': {'fishnetToken': SECRET}},
                            'page': envelope(), 'history': [history()]}}
    body = ('<script type="application/json">' + json.dumps(state) + '</script>').encode()
    result = inspect_native_loader_state(body, URL, observed_at_utc=OBSERVED)
    assert result['decoded_loader_state_count'] == 1
    assert result['historical_result_candidates']['candidate_record_count'] == 1
    assert result['semantic_standings_candidates']['standings_tables'] == []
    assert result['api_requests_made'] == result['admitted_rows'] == 0
    assert not result['javascript_executed']
    assert SECRET not in json.dumps(result)


def semantic_document(*, season=5, tournament=4, uids=(100, 200)):
    columns = ['#', 'Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'DIFF', 'PTS']
    links = [f'https://statshub.sportradar.com/sportpesa/en/sport/1/team/{uid}'
             f'?seasonId={season}&tournamentId={tournament}' for uid in uids]
    header = f'<link rel="canonical" href="{URL}">' + ''.join(
        f'<a href="{link}">Public team {i}</a>' for i, link in enumerate(links))
    header += f'<a href="{URL}">Overview</a>'
    table = '<table><tr>' + ''.join(f'<th>{c}</th>' for c in columns) + '</tr>'
    for i, link in enumerate(links):
        cells = [str(i+1), f'<a href="{link}">Public team {i}</a>', '1', '0', '1', '0', '0', '0', '0', '1']
        table += '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'
    return header + table + '</table>'


def inspect_with_table(html):
    state = {'loaderData': {'page': envelope()}}
    body = (html + '<script type="application/json">' + json.dumps(state) + '</script>').encode()
    return inspect_native_loader_state(body, URL, observed_at_utc=OBSERVED)


def test_semantic_standings_are_bound_to_loader_uid_and_utid_not_internal_ids():
    result = inspect_with_table(semantic_document())
    standings = result['semantic_standings_candidates']
    assert standings['decoded_context_row_count'] == 2
    assert standings['loader_identity_domains_agree']
    assert standings['team_link_identity_domain'] == 'uid'
    assert standings['tournament_link_identity_domain'] == '_utid'
    assert not standings['freshness_verified'] and not standings['collection_permission_verified']
    assert standings['standings_tables'][0]['rows'][0]['played'] == 1
    assert result['admitted_rows'] == standings['admitted_rows'] == 0


@pytest.mark.parametrize('overrides', [
    {'uids': (10, 20)}, {'uids': (100, 300)}, {'season': 6}, {'tournament': 3}])
def test_semantic_standings_cannot_bind_on_same_looking_header_or_wrong_id_domain(overrides):
    result = inspect_with_table(semantic_document(**overrides))
    standings = result['semantic_standings_candidates']
    assert standings['status'] == 'native_loader_standings_identity_unresolved'
    assert standings['decoded_context_row_count'] == 0 and not standings['standings_tables']


def test_semantic_standings_cannot_export_rows_without_valid_loader_anchor():
    from edgefactory.sources.bookmaker_context_snapshot import _loader_standings
    result = _loader_standings(semantic_document().encode(), URL, {'fixture': None})
    assert result['status'] == 'native_loader_standings_identity_unresolved'
    assert not result['standings_tables']
