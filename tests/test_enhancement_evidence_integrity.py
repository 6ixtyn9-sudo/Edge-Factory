"""Roma incident: model 82% -> calibrated 87.35% is NOT realized evidence."""
from copy import deepcopy
import json
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from edgefactory import consensus_contracts as cc
from edgefactory.enh_registry import enhancement_cohort_evidence
from enhancement_fixtures import with_evidence
import scripts.auto_tickets as at
import scripts.picks_today as pt


def edge(market='1x2', **updates):
    recipe = dict(sources=['scoutingstats'], market=market, strategy='single',
                  follow_source=None, threshold=65, status='certified',
                  mining_window=dict(start='2026-06-13', split='2026-09-01',
                                     as_of_exclusive='2026-10-01'),
                  activated_as_of='2026-10-01', contract_schema=cc.SCHEMA, **updates)
    identity = cc.contract_identity(recipe)
    return dict(recipe, contract_id=identity, rule=identity, view=identity, where='1=1')


def observations(n=100):
    return [dict(date='2026-09-10', home=f'Alpha Town {i:04d}', away='Bravo United',
                 p1=.8, px=.1, p2=.1, p1_ht=.8, px_ht=.1, p2_ht=.1,
                 p_o15=.8, p_o25=.8, p_o35=.8, p_o45=.8, p_gg=.8,
                 p_o15_ht=.8, p_o25_ht=.8, ht_hs=0 if i % 2 else 2,
                 ht_gs=0, hs=0 if i % 2 else 4, gs=1 if i % 2 else 0)
            for i in range(n)]


def connection(rows):
    con = duckdb.connect(':memory:')
    frame = pd.DataFrame(rows)
    con.register('seed', frame)
    con.execute('CREATE TABLE scoutingstats AS SELECT * FROM seed')
    return con


def parent(recipe):
    return dict(date='2026-10-20', home='Alpha Town', away='Bravo United', market=recipe['market'],
                pick='home', avg_p=80., sources_used=recipe['sources'],
                contract_schema=cc.SCHEMA, contract_id=recipe['contract_id'],
                edge_rule=recipe['contract_id'])


def test_cohort_includes_losing_parents_and_excludes_today_future_forebet():
    rows = observations()
    rows += [dict(rows[0], date=day) for day in ('2026-10-20', '2026-10-21')]
    rows += [dict(rows[0])]  # identical capture is not another observation
    con = connection(rows)
    con.execute('CREATE TABLE forebet_settled AS SELECT *, 999 AS ignored FROM scoutingstats')
    cohort = cc.enhancement_cohort(con, edge(), as_of='2026-10-20', selection='home')
    assert cohort['n'] == 100
    assert cohort['h_o25'] == .5  # winner-only would misleadingly give 100%
    assert cohort['a_o15'] == 0
    assert cohort['over25'] == .5
    assert cohort['as_of_exclusive'] == '2026-10-20'


@pytest.mark.parametrize('market', cc.REMINE_MARKETS)
def test_all_parent_markets_share_exact_contract_population(market):
    selection = 'home' if market.endswith('1x2') else 'yes' if market == 'btts' else 'over'
    result = cc.enhancement_cohort(connection(observations()), edge(market),
                                   as_of='2026-10-20', selection=selection)
    assert result['n'] == 100
    assert result['h_o25'] == .5


def test_no_forebet_result_donor_or_conflicting_prediction_can_fill_sample():
    rows = observations()
    rows[0]['hs'] = rows[0]['gs'] = None
    rows += [dict(rows[1], p1=.7, px=.2)]  # quarantine this fixture's source
    con = connection(rows)
    con.execute('CREATE TABLE forebet_settled AS SELECT * REPLACE (4 AS hs, 0 AS gs) FROM scoutingstats')
    assert cc.enhancement_cohort(con, edge(), as_of='2026-10-20', selection='home') is None
    assert cc.enhancement_cohort(con, edge(), as_of='2026-10-20', selection='home', min_n=1)['n'] == 98


def test_live_fetch_requires_real_active_parent_not_display_label_or_nway(monkeypatch):
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    con = connection(observations())
    row = parent(recipe)
    assert pt.fetch_match_cohort(con, 'home', 80., 3, pick=row)['n'] == 100
    for field, value in [('contract_id', None), ('sources_used', ['forebet']),
                         ('market', 'ou_2.5'), ('edge_rule', '3way-unanimous avg_p>=65')]:
        assert pt.fetch_match_cohort(con, 'home', 80., 3, pick=dict(row, **{field: value})) is None
    recipe['status'] = 'benched'
    assert pt.fetch_match_cohort(con, 'home', 80., 3, pick=row) is None


def evidence():
    return with_evidence(dict(home='AS Roma', away='Slovan Bratislava', date='2026-10-20',
                              recommended_enhancement='home_under_25', enhancement_probability=.8,
                              enhancement_price=2.49))


@pytest.mark.parametrize('field,value', [('cohort_rate', None), ('cohort_rate', True),
    ('cohort_rate', float('nan')), ('cohort_rate', float('inf')), ('cohort_rate', -1),
    ('cohort_n', 29), ('cohort_n', True), ('cohort_n', 100.5), ('engine', 'model'),
    ('market', 'away_under_25'), ('cohort_contract_id', 'forebet-era'),
    ('cohort_as_of_exclusive', '2026-10-21')])
def test_both_boundaries_reject_wrong_or_missing_evidence(field, value):
    row = evidence()
    row['event_notes'][0][field] = value
    assert enhancement_cohort_evidence(row) is None
    assert at.enhancement_legs([row])[0]['verdict'] == 'no_cohort_evidence'
    assert 'no bet:' in pt.enhancement_board_line(row)


def test_duplicates_and_another_market_cannot_lend_their_evidence():
    row = evidence()
    row['event_notes'].append(deepcopy(row['event_notes'][0]))
    assert enhancement_cohort_evidence(row) is None
    row = evidence()
    row['enhancement_probability'] = .8735
    assert enhancement_cohort_evidence(row) is None
    row = evidence()
    row['event_notes'] = None
    assert enhancement_cohort_evidence(row) is None


def test_actual_roma_archive_is_rejected_without_mutating_its_frozen_artifact():
    root = Path(__file__).resolve().parents[1]
    source = root / 'localdata/picks_2026-10-20.json'
    if not source.exists():
        pytest.skip('production audit fixture not present')
    roma = next(p for p in json.loads(source.read_text()) if p['home'] == 'AS Roma')
    before = deepcopy(roma)
    assert roma['enhancement_probability'] == .8735
    note = next(n for n in roma['event_notes'] if n['market'] == 'home_under_25')
    assert note['engine'] == 'model' and note['cohort_rate'] is None
    assert enhancement_cohort_evidence(roma) is None
    assert at.enhancement_legs([roma])[0]['verdict'] == 'no_cohort_evidence'
    assert 'no bet:' in pt.enhancement_board_line(roma)
    assert roma == before


def test_market_side_and_evidence_survive_planning_and_renderer_does_not_relabel_models():
    rows = [evidence(), dict(evidence(), home='Other Home', away='Other Away')]
    legs = at.enhancement_legs(rows)
    assert all(l['verdict'] == 'fire' for l in legs)
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, 100.)
    at._carry_lane_evidence(plan, pool)
    for acca in plan:
        for leg in acca['legs']:
            assert leg['cohort_evidence']['market'] == leg['market'] == 'home_under_25'
            assert leg['cohort_evidence']['n'] == 200


def test_roma_kickoff_mismatch_cannot_price_any_market_or_contaminate_corroboration():
    from edgefactory.enh_pricing import attach_enhancement_price, norm_team
    pair = (norm_team('AS Roma'), norm_team('Slovan Bratislava'))
    slot = ('tt_home_2.5', 'under')
    wrong = (2.49, 'admiralbet.ba', '2026-10-20T07:43:02+00:00', 'oddspapi',
             '2026-10-20T12:00:00Z')
    right = (1.60, 'correct book', '2026-10-20T07:44:00+00:00', 'theoddsapi',
             '2026-10-20T19:00:00Z')
    index = dict(pairs={pair: {slot: wrong[:4]}}, names={}, spread={pair: {slot: {
        'oddspapi': 2.49, 'theoddsapi': 1.60}}}, quotes={pair: {slot: [2.49, 1.60]}},
        fixture_quotes={pair: {slot: [wrong]}})
    row = dict(evidence(), kickoff_utc='2026-10-20T19:00:00Z', as_of='2026-10-20T07:48:00Z')
    assert attach_enhancement_price(row, index)['enhancement_priced'] is False
    assert row['enhancement_price'] is None
    index['fixture_quotes'][pair][slot].append(right)
    assert attach_enhancement_price(row, index)['enhancement_price'] == 1.60
    assert row['enhancement_price_book'] == 'correct book'
    assert row['enhancement_price_kickoff'] == right[4]
    assert row['enhancement_consensus_price'] == 1.60
    assert row['enhancement_multi_source'] is False
    assert 'enhancement_price_divergence' not in row


@pytest.mark.parametrize('kickoff,capture', [(None, '2026-10-20T07:43:00Z'),
    ('2026-10-20T19:00:00', '2026-10-20T07:43:00Z'),
    ('2026-10-20T19:00:00Z', None),
    ('2026-10-20T19:00:00Z', '2026-10-20T07:49:00Z'),
    ('2026-10-20T19:00:00Z', '2026-10-20T19:01:00Z')])
def test_missing_naive_future_or_post_kickoff_price_witnesses_fail_closed(kickoff, capture):
    from edgefactory.enh_pricing import attach_enhancement_price, norm_team
    pair = (norm_team('AS Roma'), norm_team('Slovan Bratislava'))
    slot = ('tt_home_2.5', 'under')
    quote = (2.49, 'book', capture, 'oddspapi', kickoff)
    index = dict(pairs={pair: {slot: quote[:4]}}, names={},
                 fixture_quotes={pair: {slot: [quote]}})
    row = dict(evidence(), kickoff_utc='2026-10-20T19:00:00Z', as_of='2026-10-20T07:48:00Z')
    assert attach_enhancement_price(row, index)['enhancement_priced'] is False


def test_latest_offer_not_best_past_offer_and_same_time_conflicts_quarantine():
    from edgefactory.enh_pricing import attach_enhancement_price, norm_team
    pair = (norm_team('AS Roma'), norm_team('Slovan Bratislava'))
    slot = ('tt_home_2.5', 'under')
    old = (2.49, 'book', '2026-10-20T07:43:00Z', 'oddspapi', '2026-10-20T19:00:00Z')
    new = (1.60, 'book', '2026-10-20T07:44:00Z', 'oddspapi', old[4])
    index = dict(pairs={pair: {slot: old[:4]}}, names={}, fixture_quotes={pair: {slot: [old, new]}})
    row = dict(evidence(), kickoff_utc=old[4], as_of='2026-10-20T07:48:00Z')
    assert attach_enhancement_price(row, index)['enhancement_price'] == 1.60
    index['fixture_quotes'][pair][slot].append((1.70, *new[1:]))
    assert attach_enhancement_price(row, index)['enhancement_priced'] is False
    row.pop('kickoff_utc')  # a post-Forebet row cannot bypass timing via missing kickoff
    assert attach_enhancement_price(row, index)['enhancement_priced'] is False


def test_real_production_quote_has_no_matching_kickoff_witness(monkeypatch):
    from edgefactory.enh_pricing import load_prices_index, attach_enhancement_price
    root = Path(__file__).resolve().parents[1]
    if not (root / 'localdata/oddspapi_odds_2026-10.csv.gz').exists():
        pytest.skip('production price audit fixture not present')
    row = next(p for p in json.loads((root / 'localdata/picks_2026-10-20.json').read_text())
               if p.get('home') == 'AS Roma')
    row = deepcopy(row)
    monkeypatch.setenv('EDGE_FACTORY_ODDSPAPI_PRICES', '1')
    index = load_prices_index(root, '2026-10-20')
    assert attach_enhancement_price(row, index)['enhancement_priced'] is False
    assert row['enhancement_price_rejection'] == 'no_matching_kickoff_and_capture_witness'


def test_exact_stats_visible_without_a_quote_and_include_losses(monkeypatch):
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    con = connection(observations())
    out = pt.compute_dynamic_enhancement(con, parent(recipe), {})
    profile = out['statistical_profile']
    assert profile['n'] == 100
    assert profile['parent_hits'] == 50 and profile['parent_hit_rate'] == .5
    assert profile['over25'] == .5 and profile['h_o15'] == .5
    assert 'n=100' in out['statistical_comment']
    assert 'Parent hit rate: 50.0% (50/100)' in out['statistical_comment']
    for label in ('Over 1.5', 'Under 1.5', 'Over 2.5', 'Under 2.5',
                  'Over 3.5', 'Under 3.5', 'Over 4.5', 'Under 4.5',
                  'BTTS:', 'BTTS-No:', 'Home Over 0.5', 'Away Under 3.5'):
        assert label in out['statistical_comment']
    assert recipe['contract_id'] in out['statistical_comment']
    assert 'before 2026-10-20' in out['statistical_comment']
    assert 'All parent outcomes' in out['statistical_comment']
    assert out['statistical_profile_status'] == 'available'
    assert out['recommended_enhancement'] is None and not out['event_notes']
    # Display cannot depend on an invented probability for a categorical vote.
    other = pt.compute_dynamic_enhancement(con, dict(parent(recipe), avg_p=None), {})
    assert other['statistical_profile'] == profile


def test_thin_sample_is_real_display_evidence_but_cannot_authorize_a_bet(monkeypatch):
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    # Price everything above the floor: only the n>=30 gate blocks it.
    def price(row, _index):
        row.update(enhancement_price=1.8, enhancement_priced=True)
    monkeypatch.setattr(pt, 'attach_enhancement_price', price)
    out = pt.compute_dynamic_enhancement(connection(observations(20)), parent(recipe), {})
    assert out['statistical_profile']['n'] == 20
    assert 'n=20' in out['statistical_comment']
    assert out['recommended_enhancement'] is None and out['event_notes'] == []
    assert pt.HYBRID_MIN_N == 30


@pytest.mark.parametrize('missing', ['warehouse', 'contract', 'results'])
def test_no_placeholder_or_forebet_proxy_when_exact_numbers_unavailable(monkeypatch, missing):
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry',
                        lambda: {'edges': [] if missing == 'contract' else [recipe]})
    rows = observations()
    if missing == 'results':
        rows = [dict(r, hs=None, gs=None) for r in rows]
    con = None if missing == 'warehouse' else connection(rows)
    row = dict(parent(recipe), statistical_comment='old placeholder')
    out = pt.compute_dynamic_enhancement(con, row, {})
    assert out['statistical_comment'] is None and out['statistical_profile'] is None
    assert out['statistical_profile_status'] == 'unavailable_exact_contract_cohort'
    assert not out['event_notes'] and out['recommended_enhancement'] is None


def test_build_scoped_cache_matches_uncached_numbers_and_avoids_rescans(monkeypatch):
    recipe = edge()
    con = connection(observations())
    cache, calls = {}, []
    original = cc.collect_observations
    def counted(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)
    monkeypatch.setattr(cc, 'collect_observations', counted)
    kwargs = dict(as_of='2026-10-20', selection='home', min_n=1)
    plain = cc.enhancement_cohort(con, recipe, **kwargs)
    calls.clear()
    first = cc.enhancement_cohort(con, recipe, cache=cache, **kwargs)
    assert first == plain
    first['over25'] = 999  # caller cannot poison the next row's cached profile
    assert cc.enhancement_cohort(con, recipe, cache=cache, **kwargs) == plain
    # Another market/side/threshold uses its own exact projection, same snapshot.
    other = edge('ou_2.5')
    cc.enhancement_cohort(con, other, cache=cache, **dict(kwargs, selection='over'))
    assert len(calls) == 1
    cc.enhancement_cohort(con, recipe, cache=cache, **dict(kwargs, as_of='2026-10-21'))
    assert len(calls) == 2
    cc.enhancement_cohort(connection(observations()), recipe, cache=cache, **kwargs)
    assert len(calls) == 3  # different warehouse connection cannot borrow a result
    cc.enhancement_cohort(con, recipe, cache={}, **kwargs)
    assert len(calls) == 4  # next invocation starts fresh
    with pytest.raises(ValueError):
        cc.enhancement_cohort(con, dict(recipe, contract_id='pfc_forged'), cache=cache, **kwargs)
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    assert pt.fetch_match_cohort(con, 'home', 80., 3, pick=parent(recipe), cache=cache)
    recipe['status'] = 'benched'
    assert pt.fetch_match_cohort(con, 'home', 80., 3, pick=parent(recipe), cache=cache) is None


def test_display_numbers_cannot_rerank_duplicate_operational_contracts():
    row = dict(parent(edge()), rule=edge()['rule'], odds=1.8,
               bucket='CAUTION', statistical_comment='old constant comment')
    before = pt._representative_score(row)
    profile = cc.enhancement_cohort(connection(observations()), edge(),
                                    as_of=row['date'], selection='home')
    row['statistical_comment'] = pt.format_contract_profile(profile)
    row['statistical_profile'] = profile
    assert pt._representative_score(row) == before
    row['statistical_comment'] = None
    assert pt._representative_score(row) == before


def test_retained_archives_no_longer_render_the_retired_placeholder():
    from edgefactory.util import strip_retired_top_scores
    comment = 'Exact post-Forebet contract; searched validation is not untouched forward proof.'
    row = {'statistical_comment': comment}
    assert strip_retired_top_scores(row['statistical_comment']) == ''
    assert row['statistical_comment'] == comment  # decision-time audit unchanged
    partial = dict(n=200, contract_id='pfc_test', as_of_exclusive='2026-10-20', over25=.6)
    numeric = pt.format_contract_profile(partial)
    assert strip_retired_top_scores(numeric) == numeric
    assert 'Over 2.5: 60.0%' in numeric and 'Under 2.5: 40.0%' in numeric
    assert 'Avg Goals' not in numeric and 'BTTS:' not in numeric  # no invented fields


def test_resolved_cohort_and_captured_quotes_can_start_without_priced_history(tmp_path, monkeypatch):
    """Exercise real resolver -> price join -> notes -> live leg -> full acca.

    Synthetic source observations/quotes, not claimed production performance.
    No fabricated cohort notes or historical priced cells seed admission.
    """
    from edgefactory.enh_pricing import load_prices_index
    from edgefactory.enh_registry import registry_path
    from test_enh_pricing import _row, _write_month
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    history = [dict(r, hs=4 if i < 90 else 0, gs=0 if i < 90 else 1)
               for i, r in enumerate(observations())]
    con = connection(history)
    parents = [dict(parent(recipe), home=h, away=a, league='Synthetic League',
                    as_of='2026-10-20T06:00:00+00:00', kickoff_utc='2026-10-20T18:00:00Z')
               for h, a in [('Alpha Town', 'Bravo United'), ('Gamma Town', 'Delta United')]]
    _write_month(tmp_path, [_row(date=r['date'], home=r['home'], away=r['away'],
        league=r['league'], kickoff=r['kickoff_utc'], captured_at='2026-10-20T05:00:00+00:00',
        odds=1.8, bookmaker='BookA') for r in parents], month='2026-10')
    index = load_prices_index(tmp_path, '2026-10-20')
    rows = [dict(r, **pt.compute_dynamic_enhancement(con, r, index)) for r in parents]
    assert all(r['enhancement_probability'] is None for r in rows)
    assert all(r['enhancement_cohort_rate'] == .9 and r['enhancement_cohort_n'] == 100 for r in rows)
    legs = at.enhancement_legs(rows, registry_root=tmp_path, execution_safe=True)
    assert all(l['verdict'] == 'fire' for l in legs)
    plan = at.plan_day(at.enhancement_pool(legs), 80.1656, enhancements=True)
    assert len(plan) == 1 and len(plan[0]['legs']) == 2
    assert not registry_path(tmp_path).exists()


@pytest.mark.parametrize('side,direction,line',
    [(s, d, line) for s in ['home', 'away'] for d in ['over', 'under'] for line in [.5, 1.5, 2.5, 3.5]]
    + [('match', d, line) for d in ['over', 'under'] for line in [1.5, 2.5, 3.5, 4.5]]
    + [('btts', 'yes', None), ('btts', 'no', None)])
def test_all_goal_markets_reach_real_cohort_pricing_and_complete_acca(tmp_path, monkeypatch, side, direction, line):
    """Offline source payload -> CSV -> price index -> resolver -> live acca.

    Includes a competing O2.5 quote above the minimum. Team evidence is computed
    from synthetic settled scores, not injected cohort notes/probabilities.
    """
    import csv
    import gzip
    from datetime import datetime, timezone
    from edgefactory.sources import theoddsapi
    from edgefactory.enh_pricing import load_prices_index
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 20, 5, tzinfo=timezone.utc)
    monkeypatch.setattr(theoddsapi, 'datetime', Clock)
    hit = None if side == 'btts' else int(line) + (1 if direction == 'over' else 0)
    miss = None if side == 'btts' else int(line) + (0 if direction == 'over' else 1)
    history = []
    for i, r in enumerate(observations()):
        if side == 'btts':
            both_score = (i < 80) if direction == 'yes' else (i >= 80)
            history.append(dict(r, hs=1, gs=int(both_score)))
        else:
            goals = hit if i < 80 else miss
            history.append(dict(r, hs=goals if side in ['home', 'match'] else 0,
                                gs=goals if side == 'away' else 0))
    con = connection(history)
    parents, quotes = [], []
    for home, away in [('Alpha Town', 'Bravo United'), ('Gamma Town', 'Delta United')]:
        row = dict(parent(recipe), home=home, away=away, league='Synthetic League',
                   as_of='2026-10-20T06:00:00+00:00', kickoff_utc='2026-10-20T18:00:00Z')
        parents.append(row)
        event = dict(home_team=home, away_team=away, id=home, commence_time=row['kickoff_utc'])
        outcome = {'name': direction.title(), 'price': 1.5}
        if side != 'btts':
            outcome['point'] = line
            if side != 'match':
                outcome['description'] = home if side == 'home' else away
        key = 'btts' if side == 'btts' else 'alternate_totals' if side == 'match' else 'alternate_team_totals'
        markets = [{'key': key, 'outcomes': [outcome]}]
        if (side, direction, line) != ('match', 'over', 2.5):
            markets.append({'key': 'totals', 'outcomes': [{'name': 'Over', 'point': 2.5, 'price': 1.31}]})
        payload = {'bookmakers': [{'title': 'BookA', 'markets': markets}]}
        quotes.extend(theoddsapi.rows_from_event_odds(row, event, payload))
    path = tmp_path / 'localdata/theoddsapi_odds_2026-10.csv.gz'
    path.parent.mkdir()
    with gzip.open(path, 'wt') as handle:
        writer = csv.DictWriter(handle, fieldnames=theoddsapi.COLUMNS)
        writer.writeheader()
        writer.writerows(quotes)
    index = load_prices_index(tmp_path, '2026-10-20')
    rows = [dict(r, **pt.compute_dynamic_enhancement(con, r, index)) for r in parents]
    con.close()
    expected = f'btts_{direction}' if side == 'btts' else f'{side}_{direction}_{str(line).replace(".", "")}'
    assert all(r['recommended_enhancement'] == expected for r in rows)
    assert all(r['enhancement_cohort_rate'] == .8 and r['enhancement_probability'] is None for r in rows)
    legs = at.enhancement_legs(rows, registry_root=tmp_path, execution_safe=True)
    plan = at.plan_day(at.enhancement_pool(legs), 80.1656, enhancements=True)
    at._carry_lane_evidence(plan, at.enhancement_pool(legs))
    assert len(plan) == 1
    assert {l['market'] for l in plan[0]['legs']} == {expected}
    assert all(l['price_source'] == 'theoddsapi' for l in plan[0]['legs'])


@pytest.mark.parametrize('status', [
    'POSTPONED', 'Cancelled', 'ABANDONED', 'AET', 'PEN',
    'After extra time', 'After penalties',
])
def test_live_enh_cohort_cannot_count_disposition_or_unseparated_period(status, monkeypatch):
    rows = observations(30)
    rows[0]['status'] = status
    con = connection(rows)
    recipe = edge()
    # The shared collector's default/main contract population is unchanged.
    _, obs, ambiguous, resolved, _ = cc.collect_observations(
        con, start='2026-06-13', as_of='2026-10-20')
    assert len(list(cc.contract_rows(obs, ambiguous, resolved, recipe))) == 30
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    # This is the production caller, not an audit-only resolver. With one
    # disputed label removed, 29 cannot manufacture the existing N30 gate.
    pick = parent(recipe)
    assert pt.fetch_match_cohort(con, 'home', 80., 1, pick=pick) is None
    emitted = pt.compute_dynamic_enhancement(con, dict(pick), {})
    # The existing descriptive display may show n=29; it must not lend that
    # thin sample to any executable-market candidate.
    assert emitted['statistical_profile_status'] == 'available'
    assert emitted['statistical_profile']['n'] == 29
    assert emitted['event_notes'] == []
    assert emitted['recommended_enhancement'] is None
    assert {c['reason'] for c in emitted['enh_candidate_log']} == {'no_realized_cohort'}
    clean = cc.enhancement_cohort(con, recipe, as_of=pick['date'],
                                  selection='home', min_n=1)
    assert clean['n'] == 29
    assert clean['over25'] == pytest.approx(14 / 29)
    assert clean['h_o25'] == pytest.approx(14 / 29)
    assert clean['btts'] == 0


def test_live_enh_status_conflict_is_not_resolved_by_donor_order():
    rows = observations()
    rows[0]['status'] = 'FT'
    # Equal score values do not resolve the occurrence/status contradiction.
    rows.append(dict(rows[0], status='POSTPONED'))
    for ordered in (rows, list(reversed(rows))):
        cohort = cc.enhancement_cohort(connection(ordered), edge(),
                                       as_of='2026-10-20', selection='home', min_n=1)
        assert cohort['n'] == 99
        assert cohort['over25'] == pytest.approx(49 / 99)


def test_live_enh_boolean_goals_are_not_a_valid_score():
    # Keep a native BOOLEAN warehouse column, rather than coercing a mixed
    # Python bool/int series to integer before the production reader sees it.
    rows = [dict(r, hs=True) for r in observations()]
    assert cc.enhancement_cohort(connection(rows), edge(),
                                 as_of='2026-10-20', selection='home', min_n=1) is None


def test_live_enh_clean_scores_keep_existing_rates_and_build_cache():
    rows = [dict(r, status='FT') for r in observations()]
    con = connection(rows)
    kwargs = dict(as_of='2026-10-20', selection='home', min_n=30)
    cohort = cc.enhancement_cohort(con, edge(), cache={}, **kwargs)
    assert cohort == cc.enhancement_cohort(con, edge(), **kwargs)
    assert cohort['n'] == 100 and cohort['over25'] == .5


def ml_observations(n=100):
    rows = observations(n)
    for i, r in enumerate(rows):
        high = i % 5 != 0
        r.update(p1=.9 if high else .7, px=.05 if high else .15,
                 p2=.05 if high else .15, hs=4 if high else 0, gs=0 if high else 1)
    return rows


def test_enh_ml_fits_real_score_target_is_cached_and_has_coherent_markets(monkeypatch):
    from sklearn.linear_model import LogisticRegression
    from edgefactory.enh_registry import enhancement_ml_probability as score
    recipe, cache = edge(), {}
    con = connection(ml_observations())
    fits, original = [], LogisticRegression.fit
    def counted(self, *args, **kwargs):
        fits.append(1)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(LogisticRegression, 'fit', counted)
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    p = parent(recipe)
    cohort = pt.fetch_match_cohort(con, 'home', 90., 1, pick=p, cache=cache)
    assert cohort['ml_status'] == 'fitted' and len(fits) == 1
    assert cohort['ml_model']['classes'] == ['0:1', '4:0']  # not 1X2 correctness
    same = pt.fetch_match_cohort(con, 'home', 70., 1, pick=p, cache=cache)
    assert same == cohort and len(fits) == 1
    # Returned model parameters cannot poison build-scoped shared cache.
    same['ml_model']['coef'][0][0] = 999
    assert pt.fetch_match_cohort(con, 'home', 90., 1, pick=p, cache=cache) == cohort
    high = dict(p, avg_p=90., statistical_profile=cohort)
    low = dict(p, avg_p=70., statistical_profile=cohort)
    assert score(high, 'match_over_25') > score(low, 'match_over_25')
    for over, under in [('match_over_25', 'match_under_25'),
                        ('home_over_15', 'home_under_15'),
                        ('away_over_05', 'away_under_05'), ('btts_yes', 'btts_no')]:
        assert score(high, over) + score(high, under) == pytest.approx(1.)
    assert score(high, 'match_over_45') <= score(high, 'match_over_35') <= score(high, 'match_over_25')
    assert score(high, 'unrecognized') is None
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '0')
    assert score(high, 'match_over_25') is None
    assert pt.fetch_match_cohort(con, 'home', 90., 1, pick=p, cache=cache).get('ml_model') is None


@pytest.mark.parametrize('field,value', [('avg_p', None), ('avg_p', True),
    ('avg_p', float('nan')), ('avg_p', 101.), ('avg_p', 50.),
    ('date', '2026-10-19'), ('pick', 'away'), ('contract_id', 'another-contract')])
def test_enh_ml_cannot_borrow_model_or_invent_missing_features(field, value):
    from edgefactory.enh_registry import enhancement_ml_probability as score
    cohort = cc.enhancement_cohort(connection(ml_observations()), edge(),
                                   as_of='2026-10-20', selection='home', fit_ml=True)
    p = dict(parent(edge()), avg_p=80., statistical_profile=cohort)
    assert score(p, 'match_over_25') is not None
    assert score(dict(p, **{field: value}), 'match_over_25') is None
    changed = deepcopy(p)
    changed['statistical_profile']['ml_model']['coef'][0][0] += 1
    assert score(changed, 'match_over_25') is None


def test_enh_ml_training_excludes_future_duplicate_conflicted_and_disposition_rows():
    rows = ml_observations()
    recipe = edge()
    base = cc.enhancement_cohort(connection(rows), recipe,
                                as_of='2026-10-20', selection='home', fit_ml=True)
    same = cc.enhancement_cohort(connection(rows + [rows[0]] +
        [dict(rows[0], date=d, hs=9) for d in ('2026-10-20', '2026-10-21')]), recipe,
        as_of='2026-10-20', selection='home', fit_ml=True)
    assert same['ml_model'] == base['ml_model']
    disputed = [dict(rows[0], hs=8), dict(rows[1], status='POSTPONED')]
    clean = cc.enhancement_cohort(connection(rows + disputed), recipe,
                                 as_of='2026-10-20', selection='home', min_n=1, fit_ml=True)
    assert clean['n'] == clean['ml_model']['n'] == 98
    assert clean['ml_model']['train_last_date'] < '2026-10-20'
    reverse = cc.enhancement_cohort(connection(list(reversed(rows + disputed))), recipe,
                                   as_of='2026-10-20', selection='home', min_n=1, fit_ml=True)
    assert reverse['ml_model'] == clean['ml_model']


@pytest.mark.parametrize('rows', [observations(), ml_observations(29)])
def test_enh_ml_unavailable_is_explicit_and_keeps_measured_baseline(rows):
    cohort = cc.enhancement_cohort(connection(rows), edge(), as_of='2026-10-20',
                                   selection='home', min_n=1, fit_ml=True)
    assert cohort['ml_status'] == 'insufficient_or_constant_training_data'
    assert 'ml_model' not in cohort and cohort['n'] == len(rows)


def test_enh_ml_changes_complete_live_pair_not_admission_staking_or_main(monkeypatch):
    from edgefactory.enh_registry import enhancement_ml_probability as score
    recipe = edge()
    cohort = cc.enhancement_cohort(connection(ml_observations()), recipe,
                                   as_of='2026-10-20', selection='home', fit_ml=True)
    rows = []
    for name, confidence, price in [('High', 90., 1.6), ('Middle', 80., 1.7), ('Low', 70., 1.8)]:
        p = dict(parent(recipe), home=name, away='Opponent', league='League',
            avg_p=confidence, statistical_profile=deepcopy(cohort),
            as_of='2026-10-20T06:00:00+00:00',
            recommended_enhancement='match_over_25', enhancement_probability=None,
            enhancement_cohort_rate=.8, enhancement_cohort_n=100,
            enhancement_cohort_contract_id=recipe['contract_id'],
            enhancement_cohort_as_of_exclusive='2026-10-20',
            enhancement_price=price, enhancement_price_book='Pinnacle',
            enhancement_price_source='theoddsapi', enhancement_price_at='2026-10-20T05:00:00+00:00',
            enhancement_price_kickoff='2026-10-20T18:00:00+00:00',
            event_notes=[dict(market='match_over_25', engine='hybrid_cohort',
                cohort_rate=.8, cohort_n=100, cohort_contract_id=recipe['contract_id'],
                cohort_as_of_exclusive='2026-10-20')])
        rows.append(p)
    before = deepcopy(rows)
    legs = at.enhancement_legs(rows, execution_safe=True)
    assert all(l['verdict'] == 'fire' and l['probability'] == .8 for l in legs)
    assert len({l['ml_rank_probability'] for l in legs}) == 3
    pool = at.enhancement_pool(legs)
    knobs = dict(max_accas=1, min_accas=1, legs_per_acca=2, pairing='consecutive')
    ml_pair = at.select_accas(pool, enhancements=True, **knobs)[0]
    assert [l['row']['home'] for l in ml_pair] == ['High', 'Middle']
    main_pair = at.select_accas(pool, enhancements=False, **knobs)[0]
    assert [l['row']['home'] for l in main_pair] == ['Low', 'Middle']
    plan = at.plan_day(pool, 100., enhancements=True, **knobs)
    at._carry_lane_evidence(plan, pool)
    assert all(leg['ml_model_key'] == cohort['ml_model']['model_key']
               and leg['ml_rank_probability'] is not None for leg in plan[0]['legs'])
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '0')
    baseline_pair = at.select_accas(pool, enhancements=True, **knobs)[0]
    assert [l['row']['home'] for l in baseline_pair] == ['Low', 'Middle']
    assert at.STAKE_FRAC == .25 and rows == before
    # Model probability cannot rescue an unsupported measured cohort/quote.
    for bad in [dict(rows[0], enhancement_cohort_n=29),
                dict(rows[0], enhancement_price_book='Matchbook')]:
        assert at.enhancement_legs([bad], execution_safe=True)[0]['verdict'] != 'fire'


def test_enh_ml_multiclass_inference_matches_sklearn_not_binary_shortcut():
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from edgefactory.enh_registry import enhancement_ml_probability as score, check_enhancement_hit
    rows = observations(90)
    for i, r in enumerate(rows):
        confidence, pair = [(.7, (0, 0)), (.8, (1, 1)), (.9, (4, 0))][i % 3]
        r.update(p1=confidence, px=(1-confidence)/2, p2=(1-confidence)/2,
                 hs=pair[0], gs=pair[1])
    cohort = cc.enhancement_cohort(connection(rows), edge(), as_of='2026-10-20',
                                   selection='home', min_n=1, fit_ml=True)
    payload = cohort['ml_model']
    native = LogisticRegression()
    native.classes_ = np.array(payload['classes'])
    native.coef_ = np.array(payload['coef'])
    native.intercept_ = np.array(payload['intercept'])
    native.n_features_in_ = 1
    probabilities = native.predict_proba([[.8]])[0]
    p = dict(parent(edge()), avg_p=80., statistical_profile=cohort)
    for market in ('btts_yes', 'match_under_25', 'home_over_15', 'away_under_15'):
        expected = sum(w for w, label in zip(probabilities, payload['classes'])
                       if check_enhancement_hit(market, 'home', *map(int, label.split(':'))))
        assert score(p, market) == pytest.approx(expected)


@pytest.mark.parametrize("fit_error", [ValueError, TypeError, AttributeError])
def test_enh_ml_failed_fit_falls_back_without_relabelling_cohort(monkeypatch, fit_error):
    from sklearn.linear_model import LogisticRegression
    def fail(*args, **kwargs):
        raise fit_error('synthetic fitting failure')
    monkeypatch.setattr(LogisticRegression, 'fit', fail)
    result = cc.enhancement_cohort(connection(ml_observations()), edge(),
                                   as_of='2026-10-20', selection='home', fit_ml=True)
    assert result['ml_status'] == 'fit_unavailable'
    assert 'ml_model' not in result and result['over25'] == .8 and result['n'] == 100
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    live = pt.fetch_match_cohort(connection(ml_observations()), 'home', 80., 1,
                                 pick=parent(recipe))
    assert live['n'] == 100 and live['ml_status'] == 'fit_unavailable'


@pytest.mark.parametrize('fallback_ml', [None, float('nan'), float('inf'), True, -0.1, 1.1])
def test_enh_ml_rank_groups_do_not_compare_model_scores_with_cohort_rates(monkeypatch, fallback_ml):
    # Already-admitted pool: isolate selection, not the earlier quote gates.
    def leg(name, cohort_rate, ml):
        return dict(match=name, pick='over', prob=cohort_rate, odds=2.,
            ml_rank_probability=ml, market='match_over_25', price_book='Book',
            row=dict(date='2026-10-20', home=name, away='Opponent'),
            cohort_evidence=dict(basis='cohort_payout_bound',
                price_context=dict(book='Book', source='theoddsapi')))
    pool = [leg('Fallback high', .9, fallback_ml), leg('Model low', .6, .0),
            leg('Fallback next', .8, None), leg('Model high', .6, .55)]
    before = deepcopy(pool)
    knobs = dict(max_accas=2, min_accas=1, legs_per_acca=2, pairing='consecutive')
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '1')
    pairs = at.select_accas(pool, enhancements=True, **knobs)
    assert [[l['match'] for l in pair] for pair in pairs] == [
        ['Model high', 'Model low'], ['Fallback high', 'Fallback next']]
    baseline = at.select_accas(pool, enhancements=False, **knobs)
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '0')
    assert at.select_accas(pool, enhancements=True, **knobs) == baseline
    # NaN is deliberately in one case; compare unchanged object identity/value
    # fields rather than NaN == NaN across copies.
    assert [(l['match'], l['prob'], l['odds']) for l in pool] == [
        (l['match'], l['prob'], l['odds']) for l in before]


def test_enh_ml_recommendation_uses_same_separate_rank_groups(monkeypatch):
    from edgefactory import enh_registry
    recipe = edge()
    monkeypatch.setattr(pt, 'load_post_forebet_registry', lambda: {'edges': [recipe]})
    def price(pick, index):
        pick.update(enhancement_price=2., enhancement_priced=True,
                    enhancement_price_book='Book', enhancement_price_source='theoddsapi')
    monkeypatch.setattr(pt, 'attach_enhancement_price', price)
    # Controlled scorer output isolates rank policy, while cohort and candidate
    # eligibility still traverse the production warehouse/contract machinery.
    monkeypatch.setattr(enh_registry, 'enhancement_ml_probability',
                        lambda pick, market: .55 if market == 'home_over_05' else None)
    emitted = pt.compute_dynamic_enhancement(connection(ml_observations()), parent(recipe), {})
    assert emitted['recommended_enhancement'] == 'home_over_05'
    assert emitted['event_notes'][0]['ml_rank_probability'] == .55
    assert len(emitted['event_notes']) > 1
    assert all(n['ml_rank_probability'] is None for n in emitted['event_notes'][1:])
    assert all(n['cohort_rate'] > .55 for n in emitted['event_notes'])


def _overlapping_book_leg(name, book):
    return dict(match=name, pick='over', prob={'A': .7, 'B': .7, 'C': .9, 'D': .89, 'E': .85, 'F': .84}[name],
        odds=2., market='match_over_25', price_book=book,
        ml_rank_probability={'A': .95, 'B': .94}.get(name),
        row=dict(date='2026-10-24', home=name, away='Opponent'),
        cohort_evidence=dict(basis='cohort_payout_bound',
            price_context=dict(book=book, source='theoddsapi')))


@pytest.mark.parametrize('overlap', ['three_books', 'hidden_alternatives'])
def test_enh_ml_complete_pair_selection_does_not_strand_an_available_second_acca(monkeypatch, overlap):
    # Already-admitted quotes. Each group's best pair is attractive but can
    # consume fixtures needed by the other groups; a fixed distinct-fixture
    # population alone does NOT prove greedy pair-count invariance.
    slots = ([('A', 'X'), ('B', 'X'), ('A', 'Y'), ('C', 'Y'), ('B', 'Z'), ('D', 'Z')]
             if overlap == 'three_books' else
             [('A', 'X'), ('B', 'X'), ('C', 'X'), ('A', 'Y'), ('B', 'Y'), ('D', 'Y')])
    pool = [_overlapping_book_leg(*slot) for slot in slots]
    before = deepcopy(pool)
    knobs = dict(enhancements=True, max_accas=2, min_accas=1,
                 legs_per_acca=2, pairing='consecutive', gate_mode='off')
    for flag in ('1', '0'):
        monkeypatch.setenv('EDGE_FACTORY_ENH_ML', flag)
        pairs = at.select_accas(pool, **knobs)
        assert len(pairs) == 2
        assert {l['match'] for pair in pairs for l in pair} == {'A', 'B', 'C', 'D'}
        for pair in pairs:
            assert len({l['price_book'] for l in pair}) == 1
        # The existing shared staking function is still bounded at 25%.
        plan = at.plan_day(pool, 100., **knobs)
        assert len(plan) == 2
        assert sum(a['stake_pct'] for a in plan) == pytest.approx(25.)
    assert pool == before


@pytest.mark.parametrize('pairing', ['consecutive', 'barbell'])
def test_enh_ml_two_acca_capacity_matches_exhaustive_fixture_book_oracle(monkeypatch, pairing):
    from itertools import combinations, product

    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '1')
    # Exhaust all 4-fixture/3-book populations with either no quotes or at
    # least 2 distinct fixtures per book. Singleton groups cannot form an
    # edge. This independent oracle enumerates every executable pair, not
    # the production recipe's pair list or its look-ahead implementation.
    subsets = [()] + [g for n in range(2, 5) for g in combinations('ABCD', n)]
    for groups in product(subsets, repeat=3):
        edges = [frozenset(pair) for group in groups for pair in combinations(group, 2)]
        expected = (2 if any(a.isdisjoint(b) for a, b in combinations(edges, 2))
                    else int(bool(edges)))
        pool = [_overlapping_book_leg(name, book)
                for book, group in zip('XYZ', groups) for name in group]
        pairs = at.select_accas(pool, enhancements=True, max_accas=2, min_accas=1,
                               legs_per_acca=2, pairing=pairing, gate_mode='off')
        assert len(pairs) == expected, (pairing, groups)
        fixtures = [l['match'] for pair in pairs for l in pair]
        assert len(fixtures) == len(set(fixtures))
        assert all(len({l['price_book'] for l in pair}) == 1 for pair in pairs)


@pytest.mark.parametrize('flag', ['1', '0'])
def test_enh_ml_two_acca_lookahead_keeps_feasible_original_recipe(monkeypatch, flag):
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', flag)
    pool = [_overlapping_book_leg(name, 'X') for name in 'ABCD']
    for pairing in ('consecutive', 'barbell'):
        ranked = sorted(pool, key=lambda l: (
            l['ml_rank_probability'] is not None,
            l['ml_rank_probability'] if l['ml_rank_probability'] is not None else l['prob'],
            l['prob'], l['odds']), reverse=True) if flag == '1' else at.rank_legs(pool, 'prob')
        # With a single executable book the original recipe already covers
        # all four fixtures, and must not be replaced by arbitrary pairs.
        expected = at.pair_legs(ranked, pairing, 2)
        assert at.select_accas(pool, enhancements=True, max_accas=2, min_accas=1,
            legs_per_acca=2, pairing=pairing, gate_mode='off') == expected
        # Main remains the shared original recipe, independent of ML flag.
        assert at.select_accas(pool, enhancements=False, max_accas=2, min_accas=1,
            legs_per_acca=2, pairing=pairing, gate_mode='off') == at.pair_legs(
                at.rank_legs(pool, 'prob'), pairing, 2)


@pytest.mark.parametrize('flag,scored,expected', [('0', True, 1), ('1', False, 1), ('1', True, 2)])
def test_enh_ml_two_acca_repair_preserves_exact_rollback_and_unscored_recipe(monkeypatch, flag, scored, expected):
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', flag)
    pool = [_overlapping_book_leg(name, book)
            for book, names in [('X', 'ABC'), ('Y', 'ABD')] for name in names]
    # Make cohort order itself encounter the greedy trap. Rollback must
    # preserve that exact old recipe, not silently fix unrelated baseline
    # behavior. Missing ML scores must also retain the old fallback recipe.
    for leg in pool:
        leg['prob'] = {'A': .9, 'B': .89, 'C': .7, 'D': .7}[leg['match']]
        if not scored:
            leg.pop('ml_rank_probability')
    pairs = at.select_accas(pool, enhancements=True, max_accas=2, min_accas=1,
                           legs_per_acca=2, pairing='consecutive', gate_mode='off')
    assert len(pairs) == expected
    if expected == 1:
        assert [[(l['match'], l['price_book']) for l in pair] for pair in pairs] == [[('A', 'X'), ('B', 'X')]]


@pytest.mark.parametrize('pairing', ['consecutive', 'barbell'])
@pytest.mark.parametrize('case,expected', [('two_available', 2), ('three_available', 3), ('hidden_three', 3)])
def test_enh_ml_live_three_acca_limit_preserves_available_capacity(monkeypatch, pairing, case, expected):
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '1')
    slots = ([('A', 'X'), ('B', 'X'), ('C', 'X'), ('A', 'Y'), ('B', 'Y'), ('D', 'Y')]
             if case == 'hidden_three' else
             [('A', 'X'), ('B', 'X'), ('A', 'Y'), ('C', 'Y'), ('B', 'Z'), ('D', 'Z')])
    if expected == 3:
        slots += [('E', 'W'), ('F', 'W')]
    pool = [_overlapping_book_leg(*slot) for slot in slots]
    before = deepcopy(pool)
    assert at.ENH_MAX_ACCAS == 3 and at.MAX_ACCAS == 2
    knobs = dict(enhancements=True, max_accas=at.ENH_MAX_ACCAS,
                 rank=at.ENHANCEMENT_RANK, pairing=pairing, gate_mode='off')
    pairs = at.select_accas(pool, **knobs)
    assert len(pairs) == expected
    names = [l['match'] for pair in pairs for l in pair]
    assert len(names) == len(set(names)) == expected * 2
    for pair in pairs:
        assert len({(l['cohort_evidence']['price_context']['book'],
                     l['cohort_evidence']['price_context']['source']) for l in pair}) == 1
    plan = at.plan_day(pool, 100., stake_frac=at.ENHANCEMENT_LANE.stake_frac, **knobs)
    assert len(plan) == expected
    assert sum(a['stake_pct'] for a in plan) == pytest.approx(25., abs=.001)
    assert pool == before


def _capacity_graph_pool(edges):
    # One executable book per graph edge. Any simple fixture graph can be
    # represented this way; the oracle need not assume clique-shaped books.
    pool = []
    for i, edge in enumerate(edges):
        for name in edge:
            leg = _overlapping_book_leg('A', f'Book{i}')
            leg.update(match=name, prob=.7,
                       ml_rank_probability={'A': .99, 'B': .98}.get(name, .8))
            leg['row']['home'] = name
            pool.append(leg)
    return pool


def _fixture_graph_capacity(n, edges):
    neighbours = [0] * n
    for a, b in edges:
        neighbours[a] |= 1 << b
        neighbours[b] |= 1 << a
    memo = {0: 0}

    def oracle(vertices):
        # Independent vertex-subset DP: either leave the first fixture
        # unmatched or pair it with each available neighbour. No greedy
        # cover, edge kernel or production helper is used here.
        if vertices not in memo:
            first = vertices & -vertices
            rest = vertices ^ first
            best = oracle(rest)
            options = neighbours[first.bit_length() - 1] & rest
            while options and best < 3:
                other = options & -options
                best = max(best, 1 + oracle(rest ^ other))
                options ^= other
            memo[vertices] = min(3, best)
        return memo[vertices]

    return oracle((1 << n) - 1)


@pytest.mark.parametrize('pairing', ['consecutive', 'barbell'])
def test_enh_ml_three_acca_capacity_matches_all_six_fixture_graphs(monkeypatch, pairing):
    from itertools import combinations

    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '1')
    possible = list(combinations(range(6), 2))
    for mask in range(1 << len(possible)):
        edges = [edge for bit, edge in enumerate(possible) if mask & (1 << bit)]
        pool = _capacity_graph_pool([(chr(65 + a), chr(65 + b)) for a, b in edges])
        pairs = at.select_accas(pool, enhancements=True, max_accas=at.ENH_MAX_ACCAS,
                               pairing=pairing, gate_mode='off')
        assert len(pairs) == _fixture_graph_capacity(6, edges), (pairing, mask, edges)
        names = [l['match'] for pair in pairs for l in pair]
        assert len(names) == len(set(names))
        assert all(len({l['price_book'] for l in pair}) == 1 for pair in pairs)


@pytest.mark.parametrize('pairing', ['consecutive', 'barbell'])
def test_enh_ml_three_acca_larger_shuffled_graphs_match_subset_oracle(monkeypatch, pairing):
    from itertools import combinations
    import random

    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '1')
    rng = random.Random(149)
    for _ in range(300):
        n = rng.randrange(8, 15)
        density = rng.choice([.05, .15, .5, .9])
        edges = [edge for edge in combinations(range(n), 2) if rng.random() < density]
        pool = _capacity_graph_pool([(chr(65 + a), chr(65 + b)) for a, b in edges])
        rng.shuffle(pool)
        pairs = at.select_accas(pool, enhancements=True, max_accas=at.ENH_MAX_ACCAS,
                               pairing=pairing, gate_mode='off')
        assert len(pairs) == _fixture_graph_capacity(n, edges), (pairing, n, edges)
        names = [l['match'] for pair in pairs for l in pair]
        assert len(names) == len(set(names))
        assert all(len({l['price_book'] for l in pair}) == 1 for pair in pairs)


@pytest.mark.parametrize('extra_edge,expected', [(False, 2), (True, 3)])
def test_enh_ml_three_acca_high_degree_kernel_and_source_separation(monkeypatch, extra_edge, expected):
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '1')
    # Greedy starts A/B. All other edges touch A or B, except the optional
    # independent C/F edge. Hundreds of external neighbours force the bounded
    # kernel path; a certificate is A/L0, B/L1 (+C/F), and cover {A,B}
    # proves the negative case cannot produce three.
    edges = [('A', 'B')] + [(c, f'L{i}') for c in 'AB' for i in range(100)]
    if extra_edge:
        edges.append(('C', 'F'))
    pool = _capacity_graph_pool(edges)
    # Same book, different sources: never borrow a partner from another
    # executable context. These are already-admitted synthetic contexts.
    for leg in pool:
        context = leg['cohort_evidence']['price_context']
        context['source'] = leg['price_book']
        context['book'] = leg['price_book'] = 'CommonBook'
    pairs = at.select_accas(pool, enhancements=True, max_accas=at.ENH_MAX_ACCAS,
                           pairing=at.PAIRING, gate_mode='off')
    assert len(pairs) == expected
    names = [l['match'] for pair in pairs for l in pair]
    assert len(names) == len(set(names))
    assert all(len({l['cohort_evidence']['price_context']['source'] for l in pair}) == 1
               for pair in pairs)


@pytest.mark.parametrize('flag,scored,expected', [('0', True, 2), ('1', False, 2), ('1', True, 3)])
def test_enh_ml_three_acca_rollback_and_unscored_recipe_are_exact(monkeypatch, flag, scored, expected):
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', flag)
    pool = _capacity_graph_pool([('A', 'B'), ('A', 'C'), ('B', 'D'), ('E', 'F')])
    for leg in pool:
        leg['prob'] = {'A': .9, 'B': .89}.get(leg['match'], .7)
        if not scored:
            leg.pop('ml_rank_probability')
    pairs = at.select_accas(pool, enhancements=True, max_accas=at.ENH_MAX_ACCAS,
                           pairing=at.PAIRING, gate_mode='off')
    assert len(pairs) == expected
    if expected == 2:
        assert [[(l['match'], l['price_book']) for l in pair] for pair in pairs] == [
            [('A', 'Book0'), ('B', 'Book0')], [('E', 'Book3'), ('F', 'Book3')]]


@pytest.mark.parametrize('pairing', ['consecutive', 'barbell'])
def test_enh_ml_three_acca_keeps_feasible_recipe_and_main_limit(monkeypatch, pairing):
    monkeypatch.setenv('EDGE_FACTORY_ENH_ML', '1')
    pool = [_overlapping_book_leg(name, 'X') for name in 'ABCDEF']
    pairs = at.select_accas(pool, enhancements=True, max_accas=at.ENH_MAX_ACCAS,
                           pairing=pairing, gate_mode='off')
    assert pairs == at.pair_legs(pool, pairing, 2)
    main = at.select_accas(pool, pairing=pairing, gate_mode='off')
    assert main == at.pair_legs(at.rank_legs(pool, 'prob')[:4], pairing, 2)
    assert len(main) == at.MAX_ACCAS == 2
