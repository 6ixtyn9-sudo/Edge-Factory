"""Historical-load optimizations must preserve every period/identity refusal."""
from datetime import date
import random

import duckdb
import pytest

from edgefactory import settlement as st
from edgefactory import util
import scripts.auto_tickets as at


def _reference_filter(rows, period_holds=()):
    """Pre-optimization all-row identity scan (deliberately not optimized)."""
    rows = [r for r in rows if st._result_identity_valid(r)]
    risk = {st.regulation_fixture_key(r): r for r in period_holds
            if st._result_identity_valid(r)}
    for row in rows:
        if st.non_regulation_status(row.get('status')) or st.non_regulation_status(row.get('score_period')):
            risk.setdefault(st.regulation_fixture_key(row), row)
    accepted = []
    for row in rows:
        pair = st.regulation_score(row)
        if pair is None or (st.regulation_fixture_key(row) in risk
                            and st.explicit_regulation_score(row) is None):
            continue
        hs, gs = pair
        accepted.append(dict(row, date=str(row['date'])[:10], hs=hs, gs=gs,
                             outcome='home' if hs > gs else 'away' if hs < gs else 'draw'))
    holds = [dict({k: str(row.get(k) or '') for k in ('home', 'away', 'status', 'score_period')},
                  date=str(row.get('date') or '')[:10]) for row in risk.values()]
    return accepted, holds


@pytest.mark.parametrize('seed', range(10))
def test_date_shortcut_matches_full_identity_scan_including_order(seed):
    rng = random.Random(seed)
    rows = []
    for i in range(200):
        rows.append(dict(date=f'2026-10-{i % 28 + 1:02}',
                         home=rng.choice(['RSD Alcalá', 'RSD Alcala', 'RSD Alcalá U19',
                                          'Alpha Women', 'Alpha', 'Alpha II']),
                         away=rng.choice(['Las Palmas', 'Las Palmas U19', 'Beta']),
                         hs=rng.choice([None, 0, 1, 2, 1.5, -1]), gs=rng.choice([0, 1, 3, None]),
                         status=rng.choice(['FT', '', 'AET', 'PEN', 'LIVE', 'Postponed']),
                         score_period=rng.choice(['', '90', 'AET']),
                         regulation_hs=rng.choice([None, '', 1]),
                         regulation_gs=rng.choice([None, '', 1, 'invalid'])))
    rows += [dict(date='invalid', home='A', away='B', hs=1, gs=0), {}, None]
    holds = [dict(date='2026-10-27', home='RSD Alcala', away='Las Palmas', status='PEN'),
             dict(date='not-a-date', home='Bad', away='Date', status='AET')]
    assert st.filter_regulation_rows(rows, holds) == _reference_filter(rows, holds)


def test_no_period_risk_does_not_normalize_any_fixture(monkeypatch):
    rows = [dict(date=f'2026-10-{i % 28 + 1:02}', home=f'Club {i}', away='Away', hs=2, gs=0)
            for i in range(1000)]
    expected = _reference_filter(rows)
    def forbidden(row):
        pytest.fail('no risk evidence exists: fixture identity is unnecessary')
    monkeypatch.setattr(st, 'regulation_fixture_key', forbidden)
    assert st.filter_regulation_rows(rows) == expected


def test_only_risk_dates_normalized_but_all_results_retained(monkeypatch):
    rows = [dict(date=date(2026, 10, 26), home='RSD Alcala', away='Las Palmas', hs=1, gs=3),
            dict(date='2026-10-27T20:00:00Z', home='RSD Alcalá', away='Las Palmas', hs=1, gs=3),
            dict(date='2026-10-27', home='RSD Alcalá U19', away='Las Palmas U19', hs=1, gs=3),
            dict(date='2026-10-27', home='RSD Alcala', away='Las Palmas', hs=1, gs=3,
                 regulation_hs=1, regulation_gs=1)]
    holds = [dict(date='2026-10-27', home='RSD Alcala', away='Las Palmas', status='AET')]
    expected = _reference_filter(rows, holds)
    original = st.regulation_fixture_key
    visited = []
    def counted(row):
        visited.append(str(row['date'])[:10])
        return original(row)
    monkeypatch.setattr(st, 'regulation_fixture_key', counted)
    actual = st.filter_regulation_rows(rows, holds)
    assert actual == expected
    assert set(visited) == {'2026-10-27'}
    assert len(actual[0]) == 3  # prior day + youth + explicit 90-minute draw
    assert actual[0][-1]['outcome'] == 'draw'


def test_warehouse_raw_rows_only_normalized_for_positive_period_evidence(monkeypatch):
    con = duckdb.connect(':memory:')
    con.execute('CREATE TABLE forebet_settled(date VARCHAR,home VARCHAR,away VARCHAR,hs INT,gs INT)')
    con.execute("INSERT INTO forebet_settled VALUES ('2026-10-26','Alpha','Beta',1,0)")
    con.execute('CREATE TABLE vitibet(date VARCHAR,home VARCHAR,away VARCHAR,status VARCHAR,score_period VARCHAR)')
    con.executemany('INSERT INTO vitibet VALUES (?,?,?,?,?)',
                    [('2024-01-01', f'Old Club {i}', 'Other', 'FT', '') for i in range(1000)]
                    + [('2026-10-27', 'Cup Club', 'Opponent', '', 'PEN')])
    original = st.regulation_fixture_key
    visited = []
    def counted(row):
        visited.append(str(row['date'])[:10])
        return original(row)
    monkeypatch.setattr(st, 'regulation_fixture_key', counted)
    rows, holds = st.warehouse_regulation_rows(con)
    assert rows == [dict(date='2026-10-26',home='Alpha',away='Beta',hs=1,gs=0,
                         src='forebet_settled',outcome='home')]
    assert len(holds) == 1 and holds[0]['score_period'] == 'PEN'
    assert set(visited) == {'2026-10-27'}
    con.close()


@pytest.mark.parametrize('name', ['Beşiktaş', 'Ajax U21', 'Ha Noi 2 W', 'Alpha III',
                                 'Primavera EC', 'Alpha Women', 'B.93', 'Athletic Club',
                                 '', None, ['unhashable', 'name']])
@pytest.mark.parametrize('legacy', [False, True])
@pytest.mark.parametrize('width', [9, 24])
def test_team_spelling_memo_matches_original_calculation(name, legacy, width):
    suffix = util.squad_marker_suffix(name)
    if legacy and not suffix:
        expected = util.norm_team_legacy(str(name or ''), width)
    else:
        stem = util.strip_squad_markers(name)
        expected = (util.norm_team_legacy if legacy else util.norm_team)(stem, width) + suffix
    assert at._squad_aware_norm_key(name, legacy=legacy, width=width) == expected


def test_spelling_memo_is_per_team_and_reuses_only_pure_work(monkeypatch):
    at._squad_aware_norm_key_cached.cache_clear()
    original = util.squad_marker_suffix
    calls = []
    def counted(name):
        calls.append(name)
        return original(name)
    monkeypatch.setattr(util, 'squad_marker_suffix', counted)
    for _ in range(1000):
        assert at._squad_aware_norm_key('Alpha U21', width=24).endswith('_u21')
    assert calls == ['Alpha U21']
    assert at._squad_aware_norm_key_cached.cache_info().maxsize == 200_000
    at._squad_aware_norm_key_cached.cache_clear()


def test_collector_resolves_holds_only_on_relevant_dates_without_dropping_history(tmp_path, monkeypatch):
    import json
    local = tmp_path / 'localdata'
    local.mkdir()
    (tmp_path / 'Config').mkdir()
    historical = dict(date='2024-01-01', home='Historical Club', away='Old Opponent', hs=2, gs=0)
    resolved = dict(date='2026-10-27', home='Cup Club', away='Opponent', hs=3, gs=1,
                    regulation_hs=1, regulation_gs=1)
    holds = [dict(date='2026-10-27', home='Cup Club', away='Opponent', status='AET'),
             dict(date='2026-10-27', home='Cup Club U19', away='Opponent U19', status='AET')]
    (local / 'settled_results.json').write_text(json.dumps(dict(rows=[historical, resolved],
                                                               period_holds=holds)))
    original = st.regulation_fixture_key
    visited = []
    def counted(row):
        visited.append(str(row['date'])[:10])
        return original(row)
    monkeypatch.setattr(st, 'regulation_fixture_key', counted)
    facts = at.load_settled(root=tmp_path)
    assert set(visited) == {'2026-10-27'}
    assert set(facts.entries) == {'2024-01-01', '2026-10-27'}
    assert facts.entries['2026-10-27'][0]['outcome'] == 'draw'
    assert len(facts.period_blocks) == 1 and facts.period_blocks[0]['home'] == 'Cup Club U19'
    assert at.pick_result(dict(historical, pick='home'), facts) == 'win'
    assert at.pick_result(dict(resolved, pick='draw'), facts) == 'win'


def test_later_load_still_observes_new_period_evidence(tmp_path):
    import json
    local = tmp_path / 'localdata'
    local.mkdir()
    (tmp_path / 'Config').mkdir()
    row = dict(date='2026-10-27', home='Cup Club', away='Opponent', hs=1, gs=3)
    path = local / 'settled_results.json'
    path.write_text(json.dumps(dict(rows=[row])))
    first = at.load_settled(root=tmp_path)
    assert at.pick_result(dict(row, pick='away'), first) == 'win'
    path.write_text(json.dumps(dict(rows=[row], period_holds=[dict(row, status='AET')])))
    second = at.load_settled(root=tmp_path)
    assert not second and len(second.period_blocks) == 1
    assert at.pick_result(dict(row, pick='away'), second) is None
    assert first is not second
