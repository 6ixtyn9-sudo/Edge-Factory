"""Repair boundaries: temporal index isolation, per-book receipts, safe failures."""
from copy import deepcopy
import csv
import gzip
import json

import pytest

from edgefactory.enh_pricing import attach_enhancement_price, load_prices_index
from edgefactory.kickoff_corroboration import load_schedule_witnesses
from scripts import auto_tickets as at, picks_today as pt
from enhancement_fixtures import with_evidence, compute_with_fixture_cohort, contract_pick
from test_betexplorer_board_admission import board_only, isolated, SUPPORTED_BE_MARKETS  # noqa: F401
from test_betexplorer_red_team_2026_10_23 import make_pair
from test_enh_pricing import BE_DAY, _be_pick, _write_be_ledger, _be_fixture, FULL_BE_MARKETS
from test_enh_selection_equality import _StubCon


@pytest.mark.parametrize('reverse', [False, True])
def test_one_index_supports_different_decisions_without_order_dependence(tmp_path, reverse):
    path, fixture = board_only(tmp_path)
    _write_be_ledger(tmp_path, {'event': fixture})
    board = json.loads(path.read_text())
    board['boards'][BE_DAY]['fetched_at'] = f'{BE_DAY}T06:45:00Z'
    board['boards'][BE_DAY]['fixtures'][0]['startTime'] = f'{BE_DAY}T19:00:00Z'
    path.write_text(json.dumps(board))
    index = load_prices_index(tmp_path, BE_DAY)
    decisions = ['06:30:00', '06:50:00']
    if reverse:
        decisions.reverse()
    for instant in decisions * 2:
        row = attach_enhancement_price(_be_pick('btts_no', as_of=f'{BE_DAY}T{instant}Z'), index)
        assert row['enhancement_price'] == (2.25 if instant == '06:30:00' else None)


def test_future_only_witness_can_price_only_after_it_is_observed(tmp_path):
    board_only(tmp_path, board_changes={'fetched_at': f'{BE_DAY}T06:45:00Z'})
    index = load_prices_index(tmp_path, BE_DAY)
    for instant, expected in [('06:30:00', None), ('06:45:00', None), ('06:50:00', 2.25)]:
        row = attach_enhancement_price(_be_pick('btts_no', as_of=f'{BE_DAY}T{instant}Z'), index)
        assert row['enhancement_price'] == expected


@pytest.mark.parametrize('source', ['oddspapi', 'theoddsapi'])
def test_corrupt_relevant_month_remains_closed_with_diagnostics(tmp_path, source):
    board_only(tmp_path)
    (tmp_path / f'localdata/{source}_odds_2026-10.csv.gz').write_bytes(b'not gzip')
    index = load_prices_index(tmp_path, BE_DAY)
    assert index['betexplorer_admission']['rejections']['schedule_archive_unavailable'] == 1
    assert any(r.get('error') == 'unreadable_schedule_archive'
               for r in index['betexplorer_context']['inputs'])
    row = attach_enhancement_price(_be_pick('btts_no'), index)
    assert not row['enhancement_priced']


def test_calendar_boundary_does_not_hide_a_relevant_corrupt_previous_month(tmp_path):
    local = tmp_path / 'localdata'
    local.mkdir()
    (local / 'oddspapi_odds_2026-09.csv.gz').write_bytes(b'not gzip')
    witnesses, receipts = load_schedule_witnesses([dict(home='A', away='B',
        data_dt=[1, 10, 2026, 21, 0])], localdata=local)
    assert not witnesses
    assert receipts[0]['error'] == 'unreadable_schedule_archive'


def test_bad_relevant_archive_never_publishes_partial_schedule_rows(tmp_path):
    _, fixture = board_only(tmp_path)
    _write_be_ledger(tmp_path, {'event': fixture})
    path = tmp_path / 'localdata/oddspapi_odds_2026-10.csv.gz'
    # The CSV is readable, but the gzip footer is missing. Do not publish its
    # earlier rows as if the entire schedule archive had been verified.
    path.write_bytes(path.read_bytes()[:-8])
    witnesses, receipts = load_schedule_witnesses([fixture], localdata=path.parent)
    assert any(r.get('error') for r in receipts)
    assert all(w['file'] == 'oddspapi_fixture_state.json' for ws in witnesses.values() for w in ws)
    assert not attach_enhancement_price(_be_pick('btts_no'), load_prices_index(tmp_path, BE_DAY))['enhancement_priced']


def test_non_be_donor_is_not_removed_when_be_schedule_source_is_bad(tmp_path):
    _, fixture = board_only(tmp_path)
    row = dict(date=BE_DAY, home=fixture['home'], away=fixture['away'], market='btts',
        selection='no', odds=3., bookmaker='Other Book', source='theoddsapi',
        kickoff=f'{BE_DAY}T20:00:00Z', captured_at=f'{BE_DAY}T06:00:00Z')
    with gzip.open(tmp_path / 'localdata/theoddsapi_odds_2026-10.csv.gz', 'wt', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(row)); w.writeheader(); w.writerow(row)
    (tmp_path / 'localdata/oddspapi_odds_2026-10.csv.gz').write_bytes(b'not gzip')
    got = attach_enhancement_price(_be_pick('btts_no'), load_prices_index(tmp_path, BE_DAY))
    assert got['enhancement_price_source'] == 'theoddsapi'
    assert got['enhancement_price'] == 3.


@pytest.mark.parametrize('field,value', [
    ('enhancement_price', 9.9), ('enhancement_price_book', 'Forged Book'),
    ('enhancement_price_provenance', None), ('enhancement_price_at', 'bad'),
    ('enhancement_priced', False), ('enhancement_price_rejection', 'rejected'),
])
def test_common_book_variants_cannot_bypass_live_receipt_checks(tmp_path, field, value):
    plan, rows = make_pair(tmp_path, competing=True)
    assert plan  # the intact common-book pair actually fires
    for row in rows:
        alternative, = row['enhancement_quote_alternatives']
        alternative[field] = value
    legs = at.enhancement_legs([with_evidence(dict(r, league='Synthetic League')) for r in rows], execution_safe=True)
    assert not any(l['verdict'] == 'fire' and l['price_book'] == 'Common Book' for l in legs)
    pool = at.enhancement_pool(legs)
    assert not at.plan_day(pool, 100, stake_frac=at.ENHANCEMENT_LANE.stake_frac,
        max_accas=at.ENH_MAX_ACCAS, rank=at.ENHANCEMENT_RANK, enhancements=True)


@pytest.mark.parametrize('low_primary', [False, True])
def test_candidates_preserve_common_book_through_real_note_generation_and_json(tmp_path, monkeypatch, low_primary):
    _, rows = make_pair(tmp_path, competing=True)
    if low_primary:
        path = tmp_path / f'localdata/betexplorer_match_detail_{BE_DAY}.json'
        payload = json.loads(path.read_text())
        for fixture in payload['fixtures'].values():
            offer = fixture['markets']['ou']['rows'][-1]
            offer.update(odds=[1.2, 1.2], best=True)
        path.write_text(json.dumps(payload))
    index = load_prices_index(tmp_path, BE_DAY)
    profile = dict(n=200, avg_goals=2.5, over15=.8, over25=.75, over35=.5, over45=.25,
        btts=.6, h_o05=.7, h_o15=.6, h_o25=.4, h_o35=.2,
        a_o05=.7, a_o15=.6, a_o25=.4, a_o35=.2)
    monkeypatch.setattr(pt, 'fetch_match_cohort', lambda *a, **k: profile)
    generated = []
    for row in rows:
        parent = contract_pick(dict(row, league='Synthetic League', market='1x2', avg_p=62, n_way=1, pick='home'))
        overlay = compute_with_fixture_cohort(pt, _StubCon(), parent, index)
        assert any(n.get('enhancement_quote_alternatives') for n in overlay['event_notes'])
        generated.append(dict(parent, **overlay))
    generated = json.loads(json.dumps(generated))
    legs = at.enhancement_legs(generated, execution_safe=True)
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, 100, stake_frac=at.ENHANCEMENT_LANE.stake_frac,
        max_accas=at.ENH_MAX_ACCAS, rank=at.ENHANCEMENT_RANK, enhancements=True)
    at._carry_lane_evidence(plan, pool)
    assert plan
    assert {l['price_book'] for a in plan for l in a['legs']} == {'Common Book'}
    assert all(l['price_provenance']['bookmaker'] == 'Common Book' for a in plan for l in a['legs'])


def test_reusing_pick_clears_old_quote_variants(tmp_path):
    _, rows = make_pair(tmp_path, competing=True)
    row = rows[0]
    assert row['enhancement_quote_alternatives']
    attach_enhancement_price(dict(row), {})  # separate call does not mutate original
    attach_enhancement_price(row, {})
    assert 'enhancement_quote_alternatives' not in row
    assert not row['enhancement_priced']


@pytest.mark.parametrize('market', SUPPORTED_BE_MARKETS)
def test_book_diverse_complete_competition_for_every_supported_market(tmp_path, market):
    plan, rows = make_pair(tmp_path, competing=True, market=market)
    assert len(plan) == 1
    assert all(r['enhancement_price_book'] != 'Common Book' for r in rows)
    # Individually best displayed quotes stay intact; only the complete pair
    # uses the retained lower-priced common bookmaker.
    assert all(r['enhancement_price'] == 2.5 for r in rows)
    assert all(a['odds'] == round(2.25 * 2.25, 2) for a in plan)


def test_invalid_deflate_stream_is_diagnosed_and_not_silently_accepted(tmp_path):
    board_only(tmp_path)
    path = tmp_path / 'localdata/oddspapi_odds_2026-10.csv.gz'
    path.write_bytes(b'\x1f\x8b\x08\x00' + b'\x00' * 6 + b'\x07' + b'\x00' * 8)
    index = load_prices_index(tmp_path, BE_DAY)
    assert index['betexplorer_admission']['rejections']['schedule_archive_unavailable'] == 1
    assert not attach_enhancement_price(_be_pick('btts_no'), index)['enhancement_priced']


@pytest.mark.parametrize('malformed', [42, 'bad', {'price': 2.25}, None])
def test_malformed_alternative_container_does_not_crash_live_builder(tmp_path, malformed):
    _, rows = make_pair(tmp_path, competing=True)
    for row in rows:
        row['enhancement_quote_alternatives'] = malformed
    legs = at.enhancement_legs([with_evidence(dict(r, league='Synthetic League')) for r in rows], execution_safe=True)
    assert len(legs) == 2
    assert all(l['price_book'] != 'Common Book' for l in legs)


def test_evidence_quarantine_clears_unproven_selected_quote_alternatives(tmp_path):
    from scripts.picks_today import stamp_pick_evidence
    _, rows = make_pair(tmp_path, competing=True)
    row = rows[0]
    assert row['enhancement_quote_alternatives']
    assert stamp_pick_evidence([row], git_sha='repair-test', built_at='2026-10-23T06:30:00Z')
    assert row['recommended_enhancement'] is None
    assert row['enhancement_quote_alternatives'] is None
    assert not at.enhancement_legs([row], execution_safe=True)


@pytest.mark.parametrize('name', ['oddspapi_odds_2026-99.csv.gz',
                                  'oddspapi_odds_0000-01.csv.gz',
                                  'oddspapi_odds_unknown.csv.gz'])
def test_noncanonical_archive_name_is_not_proven_irrelevant(tmp_path, name):
    board_only(tmp_path)
    (tmp_path / 'localdata' / name).write_bytes(b'not gzip')
    index = load_prices_index(tmp_path, BE_DAY)
    assert index['betexplorer_admission']['rejections']['schedule_archive_unavailable'] == 1
    assert not attach_enhancement_price(_be_pick('btts_no'), index)['enhancement_priced']
