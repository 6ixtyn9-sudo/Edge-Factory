"""Independent adversarial cases for merged PR141.

Synthetic inputs only, no network/state changes. Known defects are strict xfails:
use --runxfail to reproduce the failing desired-behaviour assertions explicitly.
"""
from copy import deepcopy
import json

import pytest

from edgefactory.enh_pricing import attach_enhancement_price, load_prices_index
from scripts import auto_tickets as at
from enhancement_fixtures import with_evidence
from test_betexplorer_board_admission import board_only, isolated  # noqa: F401
from test_enh_pricing import BE_DAY, _be_pick, _be_block, _be_row, _write_be_ledger


def attach(root, market='btts_no'):
    return attach_enhancement_price(_be_pick(market, pick='home'), load_prices_index(root, BE_DAY))


@pytest.mark.xfail(strict=True, reason='F1: later pre-cutoff board poisons valid earlier-as-of CSV evidence')
@pytest.mark.parametrize('kickoff', ['20:00:00', '19:00:00'])
def test_future_board_must_not_change_an_earlier_supported_decision(tmp_path, kickoff):
    path, fixture = board_only(tmp_path)
    _write_be_ledger(tmp_path, {'event': fixture})
    saved = path.read_text()
    path.unlink()
    assert attach(tmp_path)['enhancement_price'] == 2.25  # eligible at 06:30Z
    data = json.loads(saved)
    data['boards'][BE_DAY]['fetched_at'] = f'{BE_DAY}T06:45:00Z'
    data['boards'][BE_DAY]['fixtures'][0]['startTime'] = f'{BE_DAY}T{kickoff}Z'
    path.write_text(json.dumps(data))
    assert attach(tmp_path)['enhancement_price'] == 2.25  # later evidence is irrelevant


@pytest.mark.parametrize('stamp,expected', [('05:45:00', None), ('07:00:00', 2.25)])
def test_genuine_predecision_conflict_rejects_but_postcutoff_board_is_ignored(tmp_path, stamp, expected):
    path, fixture = board_only(tmp_path)
    _write_be_ledger(tmp_path, {'event': fixture})
    data = json.loads(path.read_text())
    data['boards'][BE_DAY]['fetched_at'] = f'{BE_DAY}T{stamp}Z'
    data['boards'][BE_DAY]['fixtures'][0]['startTime'] = f'{BE_DAY}T19:00:00Z'
    path.write_text(json.dumps(data))
    assert attach(tmp_path)['enhancement_price'] == expected


def make_pair(root, competing):
    markets = {'ou': _be_block(['Over', 'Under'], ['2.50'],
        [_be_row('Common Book', '2.50', [2.25, 2.25])])}
    path, _ = board_only(root, markets=markets)
    ledger = root / f'localdata/betexplorer_match_detail_{BE_DAY}.json'
    data = json.loads(ledger.read_text())
    second = deepcopy(data['fixtures']['event'])
    second.update(home='Other Home', away='Other Away')
    data['fixtures']['second'] = second
    if competing:
        for fixture, book in zip(data['fixtures'].values(), ['Only First Book', 'Only Second Book']):
            fixture['markets']['ou']['rows'].append(_be_row(book, '2.50', [2.5, 2.5]))
            fixture['markets']['ou']['bookmakers'].append(book)
    _write_be_ledger(root, data['fixtures'])  # Independent CSV schedules also exercise the pre-PR141 path.
    board = json.loads(path.read_text())
    board['boards'][BE_DAY]['fixtures'].append(dict(board['boards'][BE_DAY]['fixtures'][0],
        fixtureId='second', participant1Name='Other Home', participant2Name='Other Away'))
    path.write_text(json.dumps(board))
    index = load_prices_index(root, BE_DAY)
    picks = [_be_pick('match_over_25', pick='home'), _be_pick('match_over_25', pick='home',
        home='Other Home', away='Other Away', match='Other Home vs Other Away')]
    priced = [attach_enhancement_price(p, index) for p in picks]
    legs = at.enhancement_legs([with_evidence(dict(p, league='Synthetic League')) for p in priced],
        execution_safe=True)
    assert all(l['verdict'] == 'fire' for l in legs)
    pool = at.enhancement_pool(legs)
    return at.plan_day(pool, 100, stake_frac=at.ENHANCEMENT_LANE.stake_frac,
        max_accas=at.ENH_MAX_ACCAS, rank=at.ENHANCEMENT_RANK, enhancements=True), priced


def test_existing_recipe_accepts_the_common_book_without_competing_offers(tmp_path):
    plan, _ = make_pair(tmp_path, competing=False)
    assert len(plan) == 1


@pytest.mark.xfail(strict=True, reason='F2: loader drops viable common-book offers before complete-ticket competition')
def test_higher_disjoint_book_offers_must_not_erase_a_viable_common_book_pair(tmp_path):
    plan, rows = make_pair(tmp_path, competing=True)
    assert {r['enhancement_price_book'] for r in rows} == {'Only First Book', 'Only Second Book'}
    assert len(plan) >= 1  # Common Book @2.25 x2 is still a supported complete ticket.


@pytest.mark.xfail(strict=True, reason='F3: corrupt unrelated odds archive aborts witness loading before valid cached board')
@pytest.mark.parametrize('with_csv', [False, True])
def test_corrupt_unrelated_odds_month_must_not_disable_valid_board_only_quote(tmp_path, with_csv):
    _, fixture = board_only(tmp_path)
    if with_csv:
        _write_be_ledger(tmp_path, {'event': fixture})
    assert attach(tmp_path)['enhancement_price'] == 2.25
    (tmp_path / 'localdata/oddspapi_odds_2026-09.csv.gz').write_bytes(b'not gzip')
    assert attach(tmp_path)['enhancement_price'] == 2.25


@pytest.mark.parametrize('contents', ['{bad', 'null', '[]'])
def test_bad_board_still_cannot_create_a_quote_without_another_schedule(tmp_path, contents):
    path, _ = board_only(tmp_path)
    path.write_text(contents)
    assert not attach(tmp_path)['enhancement_priced']
