"""Synthetic semantic HTML contracts, NOT a captured StatsHub native fixture.

The successful Actions receipt retained a hash, not its body. These tests prove
fail-closed extraction rules only. Reader popup examples are labelled separately.
"""
from __future__ import annotations

import copy
import json
import socket
from pathlib import Path

import pytest

from edgefactory.sources.bookmaker_context_snapshot import (
    COLUMNS,
    PREFIX,
    context_slate_coverage,
    parse_context_batch,
    parse_context_excerpt,
    parse_native_context_html,
    validate_context_url,
)

URL=PREFIX+'match/72478680'
TEAM1=PREFIX+'sport/1/team/2835?seasonId=142176&tournamentId=8'
TEAM2=PREFIX+'sport/1/team/2829?seasonId=142176&tournamentId=8'
POPUP=Path(__file__).parent/'fixtures/bookmaker_context_popup_reader_2026-11-01.json'


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args,**kwargs): raise AssertionError('no HTTP in decoder tests')
    monkeypatch.setattr(socket,'socket',deny)
    monkeypatch.setattr(socket,'create_connection',deny)


def table(caption='LaLiga 26/27', form=True):
    columns=COLUMNS if form else COLUMNS[:-1]
    rows=[(TEAM2,'Real Madrid',[3,10,8,0,2,25,10,15,24]),
          (TEAM1,'Racing Santander',[15,10,3,2,5,15,26,-11,11])]
    output='<table>'+(f'<caption>{caption}</caption>' if caption is not None else '')
    output+='<thead><tr>'+''.join(f'<th>{x}</th>' for x in columns)+'</tr></thead><tbody>'
    for url,name,nums in rows:
        cells=[str(nums[0]),f'<a href="{url}">{name}</a>',*map(str,nums[1:])]
        if form: cells.append('WDL')
        output+='<tr>'+''.join(f'<td>{x}</td>' for x in cells)+'</tr>'
    return output+'</tbody></table>'


def document(content=None, canonical=URL, header=True):
    html='<html><head><link rel="canonical" href="'+canonical+'"></head><body>'
    if header:
        html+=f'<a href="{TEAM1}">Racing Santander</a><a href="{TEAM2}">Real Madrid</a>'
    html+=f'<a href="{URL}">Overview</a>'
    html+=table() if content is None else content
    return (html+'</body></html>').encode()


def test_synthetic_native_fields_not_reader_or_production():
    result=parse_native_context_html(document(),URL)
    assert result['status']=='native_semantic_standings_decoded_diagnostic_only'
    assert result['evidence_kind']=='native_html_semantic_inspection'
    assert result['decoded_context_row_count']==2
    assert result['fixture_route_and_header_bound']
    assert result['standings_tables'][0]['rows'][0]['points']==24
    assert result['standings_tables'][0]['rows'][1]['goals_against']==26
    assert result['standings_tables'][0]['contains_both_fixture_teams']
    assert result['kickoff_utc'] is None and result['admitted_rows']==0
    assert result['native_results_and_h2h_status']=='not_implemented'
    assert result['field_validation_status']=='retained_native_fixture_not_available'


@pytest.mark.parametrize('form',[True,False])
def test_only_two_observed_column_layouts(form):
    result=parse_native_context_html(document(table(form=form)),URL)
    assert result['decoded_context_row_count']==2


def test_popup_statistics_route_is_same_event_not_private_api():
    stats_url=URL+'/statistics'
    assert validate_context_url(stats_url)==stats_url
    data=document(canonical=stats_url)
    assert parse_native_context_html(data,stats_url)['decoded_context_row_count']==2
    assert parse_native_context_html(document(),stats_url)['decoded_context_row_count']==2
    assert parse_native_context_html(data,URL)['decoded_context_row_count']==2


def test_relative_public_links_supported_without_fetching_them():
    body=document().replace(PREFIX.encode(),b'/sportpesa/en/')
    result=parse_native_context_html(body,URL)
    assert result['decoded_context_row_count']==2
    assert result['standings_tables'][0]['rows'][0]['team_url']==TEAM2


@pytest.mark.parametrize('change',[
    lambda b:b.replace(URL.encode(),(PREFIX+'match/999').encode(),1),
    lambda b:b.replace(b'rel="canonical"',b'rel="alternate"'),
    lambda b:b.replace(b'>Overview<',b'>Wrong page<'),
    lambda b:b.replace(TEAM2.encode(),TEAM1.encode(),1),
    lambda b:b.replace(b'<a href="'+TEAM2.encode()+b'">Real Madrid</a>',b'',1),
    lambda b:b.replace(b'seasonId=142176',b'seasonId=999',1),
])
def test_unknown_header_or_canonical_binding_never_yields_rows(change):
    result=parse_native_context_html(change(document()),URL)
    assert result['decoded_context_row_count']==0
    assert result['standings_tables']==[]


@pytest.mark.parametrize('change',[
    lambda t:t.replace('<th>P</th>','<th>Unknown</th>'),
    lambda t:t.replace('<th>PTS</th>','<th>PTS</th><th>Extra</th>'),
    lambda t:t.replace('<th>PTS</th>',''),
    lambda t:t.replace('<th>','<td>').replace('</th>','</td>'),
    lambda t:t.replace('<td>10</td>','<td>11</td>',1),
    lambda t:t.replace('<td>15</td>','<td>16</td>',1),
    lambda t:t.replace('<td>24</td>','<td>NaN</td>'),
    lambda t:t.replace('<td>24</td>','<td>2<span>4</span></td>'),
    lambda t:t.replace('<td>24</td>','<td>2.4</td>'),
    lambda t:t.replace(TEAM2,TEAM2+'&token=secret'),
    lambda t:t.replace('tournamentId=8','tournamentId=9'),
    lambda t:t.replace('seasonId=142176','seasonId=999'),
    lambda t:t.replace(TEAM2,TEAM1),
])
def test_malformed_or_unbound_rows_never_partial_success(change):
    result=parse_native_context_html(document(change(table())),URL)
    assert result['decoded_context_row_count']==0
    assert result['standings_tables']==[]


def test_labels_and_div_roles_are_not_numeric_rows():
    html=('<h2>League Position</h2><p>Overall Form H2H</p>'
          '<div role="table"><div role="row"><div role="cell">33</div></div></div>')
    result=parse_native_context_html(document(html),URL)
    assert result['decoded_context_row_count']==0
    assert result['role_counts']['table']==1
    assert result['markup_counts']['table']==0


def test_script_counts_no_script_state_execution_or_leak():
    html=('<script type="application/json">{"token":"TOP_SECRET"}</script>'
          '<script type="application/ld+json">{"token":"TOP_SECRET"}</script>'
          '<script src="https://secret.example/secret.js"></script>'
          '<script>throw new Error("TOP_SECRET")</script>')
    result=parse_native_context_html(document(html+table()),URL)
    assert result['decoded_context_row_count']==2
    assert result['script_counts']=={'inert_json':1,'json_ld':1,'external':1,'inline':1}
    assert 'TOP_SECRET' not in json.dumps(result) and 'secret.example' not in json.dumps(result)


@pytest.mark.parametrize('wrapper',[
    '<script>{}</script>','<style>{}</style>','<template>{}</template>',
    '<noscript>{}</noscript>','<div hidden>{}</div>',
    '<div aria-hidden="true">{}</div>','<div style="display: none">{}</div>',
    '<div style="visibility: hidden">{}</div>',
])
def test_explicitly_hidden_tables_do_not_become_data(wrapper):
    result=parse_native_context_html(document(wrapper.format(table())),URL)
    assert result['decoded_context_row_count']==0


def test_phase_tables_separate_never_fused():
    result=parse_native_context_html(document(table('Preliminary Group A')+table('Current Group B')),URL)
    assert result['decoded_context_row_count']==4
    assert [t['phase_label'] for t in result['standings_tables']]==['Preliminary Group A','Current Group B']


@pytest.mark.parametrize('content',[table(None)+table(None),table('Group A')+table('Group A')])
def test_unlabelled_or_duplicate_phase_tables_are_ambiguous(content):
    result=parse_native_context_html(document(content),URL)
    assert result['status']=='native_table_phase_ambiguous'
    assert result['decoded_context_row_count']==0


def test_full_same_competition_group_table_can_contain_other_teams():
    extra=('<tr><td>4</td><td><a href="'+PREFIX+'sport/1/team/999?seasonId=142176&tournamentId=8">'
           'Other FC</a></td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td>'
           '<td>0</td><td>0</td><td></td></tr>')
    result=parse_native_context_html(document(table().replace('</tbody>',extra+'</tbody>')),URL)
    assert result['decoded_context_row_count']==3


@pytest.mark.parametrize('content',[
    b'\xff', b'<table><tr><td>', b'<div>'*100, b'<br>'*40001,
    document(table()*9), document(table().replace('<td>24</td>','<td>'+'9'*1100+'</td>')),
    document(table().replace('</table>','')),
])
def test_decode_depth_node_size_and_unclosed_markup_limits(content):
    result=parse_native_context_html(content,URL)
    assert result['decoded_context_row_count']==0


def test_native_byte_limit_before_parse():
    with pytest.raises(ValueError):parse_native_context_html(b'x'*(2*1024*1024+1),URL)


def test_user_popup_reader_layout_has_no_form_column():
    raw=json.loads(POPUP.read_text())
    overview,stats=map(parse_context_excerpt,raw)
    assert overview['fixture_structure_recognized']
    assert len(overview['standings_tables'][0]['rows'])==2
    assert overview['competition_squad_scope']==['women']
    assert overview['h2h_encounters_displayed']==1
    assert overview['recent_results'][0]['period']=='AP'
    assert overview['recent_results'][0]['score']==[4,3]
    assert not overview['recent_results'][0]['regulation_usable']
    assert overview['recent_results'][1]['date']=='2024-11-16'
    assert overview['kickoff_utc'] is None
    assert stats['source_url'].endswith('/statistics')
    assert [len(t['rows']) for t in stats['standings_tables']]==[4,4]
    assert stats['standings_tables'][0]['label']!=stats['standings_tables'][1]['label']
    assert all(r['played']==0 for t in stats['standings_tables'] for r in t['rows'])
    assert stats['invalid_standings_rows']==0
    with pytest.raises(ValueError):parse_context_batch(raw)  # Same event's two views, not two fixtures.


def test_popup_female_scope_cannot_be_used_for_mens_sundowns():
    from datetime import UTC, datetime
    doc=json.loads(POPUP.read_text())[0]
    page=parse_context_excerpt(doc)
    card=[{'home':'FC Masar','away':'Mamelodi Sundowns','league':'CAF Champions League',
           'kickoff_utc':'2026-11-01T15:00:00Z'}]
    result=context_slate_coverage(card,[page],datetime(2026,11,1,14,tzinfo=UTC))
    assert result['candidate_card_rows']==0


def test_missing_pts_is_not_optional_form_layout():
    raw=copy.deepcopy(json.loads(POPUP.read_text())[0])
    raw['text']=raw['text'].replace('| DIFF | PTS |','| DIFF |')
    assert parse_context_excerpt(raw)['standings_tables']==[]


def test_static_discovery_reports_shapes_not_private_values():
    from edgefactory.sources.bookmaker_context_snapshot import inspect_native_data_loading
    body=b'''<p>stats_team_lastx</p><script type="application/json">
      {"props":{"secret":"SECRET"}, "SECRET-KEY":"SECRET"}</script>
      <script type="application/json">["SECRET",1]</script>
      <script type="application/ld+json">null</script>
      <script type="application/json">invalid SECRET</script>'''
    r=inspect_native_data_loading(body,URL)
    assert r['api_operation_reference_hints']==[]  # menu/body text is not JS evidence
    assert [s['json_type'] for s in r['embedded_json_shapes']]==['object','array','scalar','invalid_or_unsupported']
    assert r['embedded_json_shapes'][0]['recognized_root_fields']==['props']
    assert 'SECRET' not in json.dumps(r)


@pytest.mark.parametrize('body',[b'\xff',b'<br>'*40001,b'<script></script>'*65,b'<script>unfinished'])
def test_static_discovery_malformed_structure_is_not_absence_evidence(body):
    from edgefactory.sources.bookmaker_context_snapshot import inspect_native_data_loading
    r=inspect_native_data_loading(body,URL)
    assert r['status']=='unsupported_or_malformed_static_payload'
    assert r['script_asset_urls']==[]


def test_static_discovery_limits_and_fixed_asset_binding():
    from edgefactory.sources.bookmaker_context_snapshot import inspect_native_data_loading
    for url in (URL+'?T=SECRET','https://evil.example/assets/app.js'):
        with pytest.raises(ValueError):inspect_native_data_loading(b'',url,is_script=True)
    with pytest.raises(ValueError):inspect_native_data_loading(b'x'*(2*1024*1024+1),URL)


def test_observed_feed_operations_and_config_references_export_no_config_values():
    from edgefactory.sources.bookmaker_context_snapshot import inspect_native_data_loading
    # Selected code-like contracts, NOT the native JS body or a feed response.
    body=b'''const cfg={fishnetUrl:"https://widgets.fn.sportradar.com",fishnetClientAlias:"SECRET",
      fishnetToken:"SECRET"}; window.cctxInitValues={};
      function tables(id){return r("stats_match_tableslice",id)}
      function recent(id){return r("stats_team_lastxextended",id)}
      function fixtures(id){return r("stats_season_fixtures2",id)}'''
    r=inspect_native_data_loading(body,'https://statshub.sportradar.com/assets/feeds-example.js',is_script=True)
    assert r['runtime_config_reference_hints']==['cctxInitValues','fishnetUrl','fishnetClientAlias','fishnetToken']
    assert r['api_operation_reference_hints']==['stats_match_tableslice','stats_team_lastxextended','stats_season_fixtures2']
    assert 'SECRET' not in json.dumps(r)
    assert r['api_requests_made']==r['admitted_rows']==0 and not r['javascript_executed']
    assert r['status']=='inspected_not_api_verified'


def test_static_discovery_asset_reference_limit_is_fail_closed():
    from edgefactory.sources.bookmaker_context_snapshot import inspect_native_data_loading
    body=''.join(f'<link rel="modulepreload" href="/assets/vendor{i}.js">' for i in range(257)).encode()
    r=inspect_native_data_loading(body,URL)
    assert r['status']=='unsupported_or_malformed_static_payload'
    assert r['script_asset_urls']==[]
