"""No numeric stand-ins at display, persistence or legacy-report boundaries."""
import json

import pytest

from edgefactory.util import finite_probability, pick_probability_pct, format_pick_probability
from edgefactory.notifier import _tg_pick_card, _format_shadow_pick_line, format_whatsapp_summary
from edgefactory.scored_candidate_shadow import scored_event
from scripts import auto_tickets as at, o25_tracker as tracker, picks_today as pt
from scripts.sync_supabase import build_pick_rows, event_source_ref


@pytest.mark.parametrize('value', [None, True, False, '0', '75', float('nan'), float('inf'), -1, 101, 10**400])
def test_invalid_or_missing_pct_is_never_zero(value):
    pick = dict(home='Alpha', away='Bravo', market='1x2', pick='home',
                avg_p=value, date='2026-10-21', edge_rule='measured-rule', bucket='CAUTION')
    assert pick_probability_pct(pick) is None
    assert format_pick_probability(pick) == 'unavailable'
    event = scored_event(pick, trading_date='2026-10-21', run_id='test', stage='scored')
    assert event['probability'] is None
    assert 'unavailable' in _tg_pick_card(pick)
    assert 'unavailable' in _format_shadow_pick_line(pick)
    assert 'unavailable' in format_whatsapp_summary('2026-10-21', [pick])
    rows, _ = build_pick_rows([pick], {'measured-rule': 'edge'},
                             {event_source_ref(pick): 'event'},
                             {'measured-rule': 'measured-rule'},
                             target_date='2026-10-21', picks_path=None)
    assert rows[0]['probability'] is None


@pytest.mark.parametrize('value', [0, 75, 100])
def test_measured_pct_and_explicit_unavailability(value):
    pick = {'avg_p': value}
    assert pick_probability_pct(pick) == value
    assert format_pick_probability(pick) == f'{value}%'
    assert pick_probability_pct(dict(pick, probability_available=False)) is None
    assert format_pick_probability(dict(pick, probability_available=False)) == 'unavailable'


@pytest.mark.parametrize('value', [None, True, '0.5', -0.1, 1.1, float('nan'), float('inf')])
def test_fraction_requires_actual_finite_observation(value):
    assert finite_probability(value) is None


def test_legacy_slice_records_do_not_write_missing_as_zero():
    assert at._slice_clean_row({})['prob_stated'] is None
    assert at._slice_clean_row({'prob_stated': 0})['prob_stated'] == 0
    assert at._printed_prob_value(None) is None
    assert at._printed_prob_value(0) == 0
    assert at._slice_row_from_archive('2026-10-21', 'A vs B', 'home', None, 2,
                                       {})['prob_stated'] is None


@pytest.mark.parametrize('entries', [None, {}, 'bad', [None], [42], ['bad']])
def test_malformed_post_forebet_registry_fails_closed(entries, monkeypatch, tmp_path):
    monkeypatch.setattr(pt, 'LOCALDATA', tmp_path)
    assert pt.eval_post_forebet('2026-10-21', {'edges': entries}) == ([], 0, 0, {})


def test_tracker_uses_only_target_market_probability():
    assert tracker.tracked_probability({'avg_p': 90, 'enhancement_label': 'Match Over 2.5'}) is None
    assert tracker.tracked_probability({'enhancement_probability': .9, 'recommended_enhancement': 'match_under_25'}) is None
    assert tracker.tracked_probability({'market': 'ou_2.5', 'pick': 'over', 'avg_p': 0}) == 0
    assert tracker.tracked_probability({'market': 'ou_2.5', 'pick': 'over', 'avg_p': 90,
                                        'probability_available': False}) is None
    assert tracker.tracked_probability({'recommended_enhancement': 'match_over_25',
                                        'enhancement_probability': 0}) == 0
    assert tracker.tracked_probability({'recommended_enhancement': 'match_under_25',
                                        'enhancement_probability': .8, 'market': 'ou_2.5',
                                        'pick': 'over', 'avg_p': 60}) == .6


def tracker_root(tmp_path, picks):
    data = tmp_path / 'localdata'
    data.mkdir()
    (data / 'settled_results.json').write_text(json.dumps({'rows': [
        dict(date='2026-10-20', home='Alpha', away='Bravo', hs=3, gs=1)]}))
    (data / 'picks_2026-10-20.json').write_text(json.dumps(picks))
    return tmp_path


def test_tracker_unknown_denominator_and_no_cross_market_price(tmp_path, capsys):
    common = dict(home='Alpha', away='Bravo', enhancement_label='Match Over 2.5',
                  enhancement_price=2, enhancement_price_source='theoddsapi')
    root = tracker_root(tmp_path, [dict(common, avg_p=99),
                                    dict(common, enhancement_probability=.55),
                                    dict(common, enhancement_probability=0),
                                    dict(common, enhancement_price=None, odds=99)])
    tracker.main(root)
    lines = capsys.readouterr().out.splitlines()
    all_priced = next(line for line in lines if line.startswith('ALL priced'))
    assert all_priced.split()[2:] == ['3', '100%', '28%', '2', '+100.0%']
    band = next(line for line in lines if line.startswith('band 50-60%'))
    assert band.split()[2] == '1'  # unknowns and measured zero are not in the band


def test_tracker_empty_archives_are_honest(tmp_path, capsys):
    tracker.main(tracker_root(tmp_path, []))
    text = capsys.readouterr().out
    assert 'graded 0/0' in text
    assert 'no listed overs' in text


@pytest.mark.parametrize('value', [None, True, '0.5', float('nan'), 1.1])
def test_enhancement_notifications_do_not_coerce_unknown(value):
    pick = dict(home='Alpha', away='Bravo', pick='home', bucket='CAUTION', avg_p=70,
                enhancement_label='Match Over 2.5', enhancement_probability=value,
                enhancement_priced=True, enhancement_price=1.8)
    assert 'unavailable' in _tg_pick_card(pick)
    assert 'unavailable' in _format_shadow_pick_line(pick)
    assert 'unavailable' in format_whatsapp_summary('2026-10-21', [pick])


def test_missing_legacy_overlap_registry_has_no_operating_points(monkeypatch, tmp_path):
    from scripts import mine_betexplorer as miner
    monkeypatch.setattr(miner, 'EDGES_PATH', tmp_path / 'missing.json')
    assert miner.load_operational_thresholds() == {}


def test_missing_rolling_history_is_unknown_not_75(monkeypatch, tmp_path):
    import duckdb
    monkeypatch.setattr(pt, 'LOCALDATA', tmp_path)
    assert pt.get_rolling_hit_rate_last_14d('2026-10-21') is None
    con = duckdb.connect(str(tmp_path / 'warehouse.duckdb'))
    con.execute('CREATE TABLE consensus3(date DATE, fb_pick VARCHAR, outcome VARCHAR)')
    con.execute("INSERT INTO consensus3 VALUES ('2026-10-20', 'home', 'away')")
    con.close()
    assert pt.get_rolling_hit_rate_last_14d('2026-10-21') == 0


@pytest.mark.parametrize('value', [None, True, False, '0.7', float('nan'),
                                   float('inf'), -.1, 1.1, 10**400])
def test_event_note_unknown_probability_is_not_cohort_rate(value):
    from edgefactory.util import format_event_note
    note = {'label': 'Match Over 2.5 Goals', 'probability': value,
            'cohort_rate': .591, 'cohort_n': 3022}
    assert format_event_note(note) == (
        'Match Over 2.5: fixture probability unavailable; '
        'descriptive cohort rate 59.1% (n=3022)')


@pytest.mark.parametrize('value', [None, True, '0.7', float('nan'), float('inf'), -1, 2])
def test_event_note_invalid_cohort_rate_has_no_numeric_standin(value):
    from edgefactory.util import format_event_note
    assert format_event_note({'label': 'BTTS', 'cohort_rate': value}) == (
        'BTTS: fixture probability unavailable')


@pytest.mark.parametrize('value', [0, .7, 1])
def test_event_note_legacy_numbers_are_labelled_recorded_not_calibrated(value):
    from edgefactory.util import format_event_note
    assert format_event_note({'label': 'BTTS', 'probability': value}) == (
        f'BTTS: recorded probability {value:.1%}')


@pytest.mark.parametrize('bucket', ['CAUTION', 'SKIPPED_VETO'])
def test_current_null_event_notes_render_in_console_and_daily_report(
        bucket, monkeypatch, tmp_path, capsys):
    from copy import deepcopy
    from scripts import daily
    monkeypatch.setattr(pt, 'bzzoiro_status_line', lambda: None)
    monkeypatch.setattr(pt, 'daily_status_block', lambda day: 'test source health')
    monkeypatch.setattr(daily, 'REPORT_DIR', tmp_path)
    pick = dict(date='2026-10-22', home='Alpha', away='Bravo', match='Alpha vs Bravo',
                pick='home', avg_p=70, bucket=bucket, event_notes=[
                    {'label': 'Match Over 2.5 Goals', 'probability': None,
                     'raw_probability': None, 'cohort_rate': .591, 'cohort_n': 3022},
                    {'label': 'BTTS'},
                    {'label': 'Away Over 0.5 Goals', 'probability': 0}])
    before = deepcopy(pick)
    pt.print_buckets({bucket: [pick]}, title_date='2026-10-22')
    console = capsys.readouterr().out
    path = daily.generate_daily_report('2026-10-22', source_picks=[pick])
    assert path is not None  # report must not quietly swallow the same exception
    for text in (console, path.read_text()):
        assert 'Match Over 2.5: fixture probability unavailable; descriptive cohort rate 59.1% (n=3022)' in text
        assert 'BTTS: fixture probability unavailable' in text
        assert 'Away Over 0.5: recorded probability 0.0%' in text
        assert ('[SHADOW — paper]' in text) == (bucket == 'SKIPPED_VETO')
        assert 'Match Over 2.5: 59.1%' not in text
    assert pick == before  # display must not enrich/mutate admission evidence
