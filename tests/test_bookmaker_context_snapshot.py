"""Reader-only shape/whole-card contracts. Never native or production coverage."""
from __future__ import annotations

import copy
import importlib.util
import json
import socket
from datetime import UTC, datetime
from pathlib import Path

import pytest

from edgefactory.sources.bookmaker_context_snapshot import (
    MAX_CONTEXT_BYTES,
    PREFIX,
    context_slate_coverage,
    parse_context_batch,
    parse_context_excerpt,
    validate_context_url,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/bookmaker_context_reader_2026-11-01.json'
ASOF = datetime(2026, 11, 1, 13, 45, tzinfo=UTC)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('external HTTP forbidden')
    monkeypatch.setattr(socket, 'socket', deny)
    monkeypatch.setattr(socket, 'create_connection', deny)


@pytest.fixture
def saved():
    return json.loads(FIXTURE.read_text())


@pytest.fixture
def probe():
    spec = importlib.util.spec_from_file_location('context_probe_test', ROOT / 'scripts/probe_betolimp.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(home='Charlton Athletic W', away='Chelsea W', league="Women's Super League",
        kickoff='2026-11-01T14:30:00Z'):
    return {"home": home, "away": away, "league": league, "kickoff_utc": kickoff}


def test_actual_reader_structure_not_native_or_probabilities(saved):
    pages = parse_context_batch(saved)
    assert len(pages) == 10
    assert all(p['fixture_structure_recognized'] for p in pages)
    assert all(p['invalid_standings_rows'] == 0 for p in pages)
    assert [p['h2h_encounters_displayed'] for p in pages] == [22,None,36,2,5,2,2,3,15,4]
    assert all(p['native_decoded_context_rows'] == p['admitted_rows'] == 0 for p in pages)
    assert all(p['kickoff_utc'] is None and p['evidence_kind'] == 'reader_transcription' for p in pages)
    assert all(p['identified_context_supplier'] == 'sportradar' for p in pages)
    assert 'probability' not in json.dumps(pages)
    assert len(pages[6]['recent_results']) == 2
    assert pages[6]['recent_results'][0]['score'] == [1,2]
    assert pages[6]['standings_tables'][0]['rows'][0]['points'] == 19
    assert pages[6]['teams'][0]['names'] == ['Charlton','Charlton Athletic']


def test_100_pages_and_all_40_card_rows_not_first_three_or_ten(saved):
    raw, card = [], []
    for i in range(40):
        sample = copy.deepcopy(saved[6])
        sample['source_url'] = PREFIX + 'match/' + str(90000000 + i)
        sample['text'] = sample['text'].replace('Charlton', f'Home{i}').replace('Chelsea', f'Away{i}')
        raw.append(sample)
        card.append(row(f'Home{i} W',f'Away{i} W'))
    pages = parse_context_batch(raw)
    result = context_slate_coverage(card, pages, ASOF)
    assert result['card_rows_examined'] == len(result['rows']) == 40
    assert result['candidate_card_rows'] == result['date_candidate_card_rows'] == 40
    assert result['unobserved_card_rows'] == result['ambiguous_card_rows'] == 0
    batches = result['pending_native_batches_not_executed']
    assert sum(map(len,batches)) == 40 and all(1 <= len(b) <= 3 for b in batches)
    assert len({url for b in batches for url in b}) == 40
    assert result['network_requests'] == result['writes'] == result['admitted_rows'] == 0
    assert all(not r['admitted'] for r in result['rows'])
    assert sum(g['card_rows'] for g in result['by_league'].values()) == 40
    assert len(parse_context_batch(raw + [dict(raw[0], source_url=PREFIX+'match/'+str(90000100+i))
                                         for i in range(60)])) == 100
    with pytest.raises(ValueError):
        parse_context_batch(raw * 3)


def test_missing_rows_and_unjoined_source_pages_stay_visible(saved):
    pages = parse_context_batch(saved)
    card = [row(), row('Unseen','Opponent','Unknown league'), {'home':None}]
    result = context_slate_coverage(card,pages,ASOF)
    assert result['candidate_card_rows'] == 1 and result['unobserved_card_rows'] == 2
    assert [r['card_index'] for r in result['rows']] == [0,1,2]
    assert result['rows'][1]['status'] == 'not_observed_in_supplied_pages'
    assert result['rows'][2]['status'] == 'invalid_card_identity'
    assert len(result['unjoined_reader_pages']) == 9
    assert 'not_native_or_usable' in result['coverage_status']


@pytest.mark.parametrize('home,away,league,index', [
    ('Cittadella','Treviso','Serie C, Girone A',4),
    ('Dolomiti Bellunesi','Lecco','Serie C, Girone A',5),
    ('Campobasso FC','Forlì','Serie C, Girone B',9),
    ('Charlton Athletic W','Chelsea W',"Women's Super League",6),
    ('Arsenal W','Aston Villa W',"Women's Super League",8),
])
def test_only_same_link_supplied_name_variants_and_explicit_scope(saved,home,away,league,index):
    result=context_slate_coverage([row(home,away,league)],parse_context_batch([saved[index]]),ASOF)
    assert result['candidate_card_rows'] == 1
    c=result['rows'][0]['candidates'][0]
    assert not c['literal_league_match']
    assert 'literal_competition_join_unresolved' in c['hold_reasons']
    assert not c['admitted']


@pytest.mark.parametrize('home,away', [
    ('Charlton Athletic','Chelsea'),
    ('Charlton Athletic U21 W','Chelsea U21 W'),
    ('Chelsea W','Charlton Athletic W'),
    ('Charlton Athletic B W','Chelsea B W'),
    ('Charlton Athletics W','Chelsea W'),
])
def test_no_senior_age_reserve_reversed_or_fuzzy_join(saved,home,away):
    r=context_slate_coverage([row(home,away)],parse_context_batch([saved[6]]),ASOF)
    assert r['candidate_card_rows'] == 0
    assert not r['pending_native_batches_not_executed']


def test_group_b_is_not_a_reserve_marker(saved):
    p=parse_context_excerpt(saved[9])
    assert p['competition_squad_scope'] == []


@pytest.mark.parametrize('suffix,expected', [(' U19',1),('',0),(' U21',0),(' U23',0),(' B',0)])
def test_youth_exact_age_never_generic_youth_or_senior(saved,suffix,expected):
    r=context_slate_coverage([row('Bansander'+suffix,'Roces'+suffix,'Youth')],
                             parse_context_batch([saved[3]]),ASOF)
    assert r['candidate_card_rows'] == expected


def test_alias_cannot_erase_reserve_class(saved):
    sample=copy.deepcopy(saved[6])
    sample['text']=sample['text'].replace('Charlton\n\nCharlton Athletic','Charlton B\n\nCharlton Athletic')
    r=context_slate_coverage([row()],parse_context_batch([sample]),ASOF)
    assert r['candidate_card_rows'] == 0


def test_never_strip_brighton_words_to_force_coverage(saved):
    r=context_slate_coverage([row('Brighton W','Crystal Palace W')],parse_context_batch([saved[7]]),ASOF)
    assert r['candidate_card_rows'] == 0
    assert r['unjoined_reader_pages']


@pytest.mark.parametrize('kickoff,asof,marker', [
    ('2026-11-01T12:00:00Z',ASOF,'not_a_predecision_capture_for_card_kickoff'),
    (None,ASOF,'card_absolute_kickoff_missing'),
    ('2026-11-02T14:30:00Z',ASOF,'calendar_date_unresolved'),
    ('2026-11-01T14:30:00',ASOF,'card_absolute_kickoff_missing'),
    ('2026-11-01T14:30:00Z',datetime(2026,11,1,12,tzinfo=UTC),'observation_after_as_of'),
])
def test_date_time_asof_holds_and_no_requests(saved,kickoff,asof,marker):
    r=context_slate_coverage([row(kickoff=kickoff)],parse_context_batch([saved[6]]),asof)
    assert marker in r['rows'][0]['candidates'][0]['hold_reasons']
    assert not r['pending_native_batches_not_executed']
    assert r['admitted_rows'] == 0


def test_live_arsenal_kept_in_denominator_not_queued(saved):
    r=context_slate_coverage([row('Arsenal W','Aston Villa W')],parse_context_batch([saved[8]]),ASOF)
    assert r['candidate_card_rows'] == 1
    assert r['future_candidate_card_rows'] == r['pending_native_url_count'] == 0
    assert 'source_fixture_live_or_ended_hint' in r['rows'][0]['candidates'][0]['hold_reasons']
    assert not r['pending_native_batches_not_executed']


def test_duplicate_card_rows_preserved_requests_deduplicated(saved):
    r=context_slate_coverage([row(),row()],parse_context_batch([saved[6]]),ASOF)
    assert len(r['rows']) == r['candidate_card_rows'] == r['future_candidate_card_rows'] == 2
    assert r['card_future_rows'] == 2 and r['pending_native_url_count'] == 1
    assert len(r['pending_native_batches_not_executed']) == 1
    assert len(r['pending_native_batches_not_executed'][0]) == 1


def test_two_source_fixtures_never_choose_first_or_freshest(saved):
    sample=copy.deepcopy(saved[6]); sample['source_url']=PREFIX+'match/99999999'
    r=context_slate_coverage([row()],parse_context_batch([saved[6],sample]),ASOF)
    assert r['ambiguous_card_rows'] == 1
    assert r['rows'][0]['status'] == 'ambiguous_source_fixture'
    assert not r['pending_native_batches_not_executed']


def test_scores_never_promoted_to_regulation(saved):
    pages=parse_context_batch(saved)
    assert pages[0]['recent_results'][1]['period'] == 'AP'
    assert pages[0]['recent_results'][1]['score'] == [4,2]
    assert all(not r['regulation_usable'] for p in pages for r in p['recent_results'])
    assert pages[1]['recent_results'][0]['date'] == '2026-03-28'


def test_multiple_phases_not_merged_or_zero_imputed(saved):
    sample=copy.deepcopy(saved[1])
    table=sample['text'][sample['text'].index('### Table'):].split('### Last matches')[0]
    sample['text'] += '\n### Group Table\n\nAFC Champions League Women Preliminary Group A\n'+table.split('TotalHomeAwayComplete')[1]
    p=parse_context_excerpt(sample)
    assert len(p['standings_tables']) == 2
    assert all(t['rows'] for t in p['standings_tables'])
    assert p['h2h_encounters_displayed'] is None


def test_reader_images_and_escaped_breaks_inside_table_cells(saved):
    sample=copy.deepcopy(saved[6])
    sample['text']=sample['text'].replace('| [Chelsea]',r'| [![shadow](https://example.test/x.png)\<br>\<br>Chelsea]')
    p=parse_context_excerpt(sample)
    assert p['invalid_standings_rows'] == 0
    assert len(p['standings_tables'][0]['rows']) == 2


@pytest.mark.parametrize('old,new', [('7 | 6 | 1 | 0','8 | 6 | 1 | 0'),('21 | 4 | 17','21 | 4 | 18'),('19 | WWWWWW','word | WWWWWW')])
def test_inconsistent_table_cannot_look_valid(saved,old,new):
    sample=copy.deepcopy(saved[6]); sample['text']=sample['text'].replace(old,new)
    p=parse_context_excerpt(sample)
    assert p['invalid_standings_rows'] == 1
    r=context_slate_coverage([row()],[p],ASOF)
    assert 'standings_structure_inconsistent' in r['rows'][0]['candidates'][0]['hold_reasons']


def test_labels_only_are_not_context_or_fixture_identity(saved):
    sample=copy.deepcopy(saved[6]); sample['text']='Head to Head\nStats Hub\nLast matches\nOverall Form'
    p=parse_context_excerpt(sample)
    assert not p['fixture_structure_recognized']
    assert not p['recent_results'] and not p['standings_tables']
    assert context_slate_coverage([row()],[p],ASOF)['candidate_card_rows'] == 0


@pytest.mark.parametrize('bad', [
    PREFIX+'match/1?token=x',PREFIX+'match/1#x',PREFIX+'match/1/report',PREFIX+'match/1/statistics',
    PREFIX+'match/1/',PREFIX+'match/0',PREFIX+'match/1234567890123',PREFIX+'match/1\n',
    PREFIX.replace('https://','http://')+'match/1',
    PREFIX.replace('/sportpesa/','/other/')+'match/1',
    PREFIX.replace('https://','https://user@')+'match/1',
    PREFIX.replace('.com/','.com:443/')+'match/1',
    'https://127.0.0.1/match/1',None,123,
])
def test_url_fixed_tenant_no_private_paths_or_credentials(bad):
    with pytest.raises(ValueError): validate_context_url(bad)


@pytest.mark.parametrize('mutation', ['native','unlabelled','oversized','naive_time','empty','extra_claim','scope'])
def test_bad_document_rejected_all_or_nothing(saved,mutation):
    sample=copy.deepcopy(saved[6])
    if mutation=='native': sample['evidence_kind']='native_http_response'
    if mutation=='unlabelled': del sample['evidence_kind']
    if mutation=='oversized': sample['text']='é'*MAX_CONTEXT_BYTES
    if mutation=='naive_time': sample['observed_at_utc']='2026-11-01T12:30:00'
    if mutation=='empty': sample['text']=''
    if mutation=='extra_claim': sample['permission_cleared']=True
    if mutation=='scope': sample['excerpt_scope']='unknown'
    with pytest.raises(ValueError): parse_context_batch([saved[0],sample])


def test_duplicate_snapshot_not_silently_resolved(saved):
    with pytest.raises(ValueError): parse_context_batch([saved[0],saved[0]])


def test_cli_requires_card_and_rejects_zone_free_cutoff(probe,tmp_path,capsys,saved):
    with pytest.raises(SystemExit): probe.main(['--context-input',str(FIXTURE)])
    card=tmp_path/'card.json'; card.write_text(json.dumps([row()]))
    assert probe.main(['--context-input',str(FIXTURE),'--card',str(card),'--as-of','2026-11-01T13:00:00'])==2
    assert 'invalid_offline_input' in capsys.readouterr().err
    assert probe.main(['--context-input',str(FIXTURE),'--card',str(card),'--as-of',ASOF.isoformat()])==0
    result=json.loads(capsys.readouterr().out)
    assert result['card_rows_examined']==result['candidate_card_rows']==1
    assert result['network_requests']==result['writes']==result['admitted_rows']==0


def test_card_and_asof_shapes_fail_closed(saved):
    pages=parse_context_batch(saved)
    for bad in (None,{},[1],[{}]*5001):
        with pytest.raises(ValueError): context_slate_coverage(bad,pages,ASOF)
    with pytest.raises(ValueError): context_slate_coverage([row()],pages,ASOF.replace(tzinfo=None))


def test_asof_utc_output_normalized_without_inventing_fixture_zone(saved):
    cutoff=datetime.fromisoformat('2026-11-01T15:45:00+02:00')
    result=context_slate_coverage([row()],parse_context_batch([saved[6]]),cutoff)
    assert result['as_of_utc']==ASOF.isoformat()
    assert result['snapshots'][0]['kickoff_utc'] is None


def test_blank_header_names_do_not_identify_fixture(saved):
    sample=copy.deepcopy(saved[6])
    sample['text']=sample['text'].replace('[Charlton\n\nCharlton Athletic]','[   ]')
    assert not parse_context_excerpt(sample)['fixture_structure_recognized']
