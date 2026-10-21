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
    ('cohort_n', 99), ('cohort_n', True), ('cohort_n', 100.5), ('engine', 'model'),
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
    # Price everything above the floor: only the original n>=100 gate blocks it.
    def price(row, _index):
        row.update(enhancement_price=1.8, enhancement_priced=True)
    monkeypatch.setattr(pt, 'attach_enhancement_price', price)
    out = pt.compute_dynamic_enhancement(connection(observations(20)), parent(recipe), {})
    assert out['statistical_profile']['n'] == 20
    assert 'n=20' in out['statistical_comment']
    assert out['recommended_enhancement'] is None and out['event_notes'] == []
    assert pt.HYBRID_MIN_N == 100


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
