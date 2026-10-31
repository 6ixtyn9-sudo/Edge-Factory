from edgefactory.settlement import ABANDONED, CANCELLED, POSTPONED, terminal_event_disposition


def test_terminal_event_disposition_is_positive_evidence_only():
    assert terminal_event_disposition("Postp.") == POSTPONED
    assert terminal_event_disposition("Postponed") == POSTPONED
    assert terminal_event_disposition("Cancelled") == CANCELLED
    assert terminal_event_disposition("Abandoned") == ABANDONED
    assert terminal_event_disposition("scheduled") is None
    assert terminal_event_disposition("live") is None
    assert terminal_event_disposition("") is None


def test_load_verified_results_parses_and_fails_closed(tmp_path):
    import json

    from edgefactory.settlement import load_verified_results

    p = tmp_path / "verified_results.json"
    p.write_text(json.dumps({"rows": [
        {"date": "2026-08-27", "home": "Pafos", "away": "Dinamo Tirana",
         "hs": 4, "gs": 2, "outcome": "home", "src": "operator_verified"},
        # bad outcome -> dropped
        {"date": "2026-08-27", "home": "Bad", "away": "Row",
         "hs": 1, "gs": 0, "outcome": "sideways"},
        # missing score -> dropped
        {"date": "2026-08-27", "home": "No", "away": "Score",
         "hs": None, "gs": 0, "outcome": "home"},
    ]}))
    rows = load_verified_results(p)
    assert rows == [{"date": "2026-08-27", "home": "Pafos", "away": "Dinamo Tirana",
                     "hs": 4, "gs": 2, "outcome": "home", "src": "operator_verified"}]


def test_load_verified_results_missing_file_is_empty(tmp_path):
    from edgefactory.settlement import load_verified_results

    assert load_verified_results(tmp_path / "nope.json") == []


import pytest
from edgefactory.settlement import (regulation_score, non_regulation_status,
                                    warehouse_regulation_rows, filter_regulation_rows)


@pytest.mark.parametrize('status', ['AET', 'a.e.t.', 'After extra-time', 'ET', 'PEN',
                                    'FT_PENS', 'After penalties', 'penalty shoot-out', 'a.p.'])
def test_extra_time_and_penalty_aggregate_is_never_a_regulation_score(status):
    assert non_regulation_status(status)
    assert regulation_score(dict(hs=1, gs=3, status=status)) is None


@pytest.mark.parametrize('status', ['FT', '', '90+7', "90'+12", 'Full time'])
def test_stoppage_time_is_still_regulation(status):
    assert regulation_score(dict(hs=1, gs=3, status=status)) == (1, 3)


@pytest.mark.parametrize('bad', [True, False, -1, 1.5, float('nan'), float('inf'), 'bad'])
def test_invalid_explicit_period_pair_cannot_fall_back_to_aggregate(bad):
    assert regulation_score(dict(hs=1, gs=3, status='AET', regulation_hs=bad, regulation_gs=1)) is None


def test_explicit_90_minute_pair_is_not_aggregate_or_shootout():
    assert regulation_score(dict(hs=1, gs=3, status='AET', regulation_hs=1, regulation_gs=1)) == (1, 1)
    assert regulation_score(dict(hs=1, gs=1, status='PEN', score_period='regulation')) == (1, 1)


def test_cross_donor_period_veto_cannot_be_laundered_by_priority_or_squad():
    import duckdb
    con = duckdb.connect(':memory:')
    con.execute('CREATE TABLE bettingclosed_settled(date VARCHAR,home VARCHAR,away VARCHAR,hs INT,gs INT,outcome VARCHAR)')
    con.execute("INSERT INTO bettingclosed_settled VALUES ('2026-10-27','RSD Alcala','Las Palmas',1,3,'away')")
    con.execute('CREATE TABLE vitibet(date VARCHAR,home VARCHAR,away VARCHAR,status VARCHAR)')
    con.execute("INSERT INTO vitibet VALUES ('2026-10-27','RSD Alcalá','Las Palmas','AET')")
    rows, holds = warehouse_regulation_rows(con)
    assert not rows and len(holds) == 1
    # A low-priority/differently accented AET donor blocks the high-priority
    # aggregate and a plain-status shared overlay row too.
    assert not filter_regulation_rows([dict(date='2026-10-27', home='RSD Alcala', away='Las Palmas', hs=1, gs=3)], holds)[0]
    con.execute('DELETE FROM vitibet')
    con.execute("INSERT INTO vitibet VALUES ('2026-10-27','RSD Alcalá U19','Las Palmas U19','AET')")
    rows, _ = warehouse_regulation_rows(con)
    assert rows[0]['outcome'] == 'away'  # a different squad cannot veto the men


def test_real_warehouse_views_exclude_aggregate_but_retain_predictions(tmp_path, monkeypatch):
    import csv,gzip
    from edgefactory import warehouse
    fields = ['date','home','away','hs','gs','p1','px','p2','odd1','oddx','odd2','tip','league','status']
    path = tmp_path / 'zulubet_2026-10.csv.gz'
    with gzip.open(path,'wt') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow(dict(date='2026-10-27',home='Cup Club',away='Away Club',hs=1,gs=3,p1=.2,px=.2,p2=.6,status='AET'))
        writer.writerow(dict(date='2026-10-26',home='Other Club',away='Another Club',hs=1,gs=3,p1=.2,px=.2,p2=.6,status='FT'))
    monkeypatch.setattr(warehouse,'LOCALDATA',tmp_path)
    con = warehouse.connect()
    assert con.execute('SELECT hs,gs,p2 FROM zulubet ORDER BY date DESC').fetchall()[0] == (None,None,.6)
    assert con.execute('SELECT count(*) FROM zulubet_settled').fetchone()[0] == 1
    con.close()


def test_bettingclosed_preserves_period_flag_from_actual_result_cell(monkeypatch):
    from edgefactory.sources import bettingclosed as bc
    html = '''<tr class="rowincontri"><td><a href="/prediction/1/cup-club">Cup Club - Away Club <span></span></a></td>
    <td class="resultMt">1-3 <abbr title="After extra time">a.e.t.</abbr></td><td class="predMt">2</td></tr>'''
    monkeypatch.setattr(bc,'get',lambda url: html)
    rows = bc.fetch_day('2026-10-27')
    assert rows[0]['status'] == 'AET'
    assert 'status' in bc.COLUMNS
    assert regulation_score(rows[0]) is None


def test_malformed_period_identity_cannot_crash_settlement_clock():
    good = dict(date='2026-10-27',home='A',away='B',hs=1,gs=0)
    bad = dict(date='invalid',home='A',away='B',status='AET')
    rows, holds = filter_regulation_rows([good,bad], [bad])
    assert len(rows) == 1 and holds == []


@pytest.mark.parametrize('row', [
    dict(hs=1,gs=3,status='A.E.T.'),
    dict(hs=1,gs=1,status='PEN',score_period='regulation'),
    dict(hs=1,gs=3,status='AET',regulation_hs=1,regulation_gs=1),
    dict(hs=1,gs=3,status='FT',regulation_hs=1,regulation_gs=None),
    dict(hs=1,gs=3,status='CANCELLED',regulation_hs=1,regulation_gs=1),
    dict(hs=1,gs=3,status='IN_PLAY'),
    dict(hs=1,gs=3,status='90+5'),
    dict(hs=1,gs=2147483648,status='FT'),
    dict(hs=1,gs=1.5,status='FT'),
])
def test_python_and_raw_sql_agree_on_regulation_score(row):
    import duckdb
    from edgefactory.settlement import regulation_sql_goals
    fields = ['hs','gs','status','score_period','regulation_hs','regulation_gs']
    with duckdb.connect(':memory:') as con:
        con.execute('CREATE TABLE donor ('+','.join(f+' VARCHAR' for f in fields)+')')
        con.execute('INSERT INTO donor VALUES (?,?,?,?,?,?)', [row.get(f) for f in fields])
        pair = con.execute('SELECT '+','.join(regulation_sql_goals(set(fields)))+' FROM donor').fetchone()
        assert (None if pair == (None,None) else pair) == regulation_score(row)


@pytest.mark.parametrize('label', ['Postp.', 'Postponed', 'Cancelled', 'Abandoned'])
def test_bettingclosed_preserves_terminal_event_not_placeholder_score(monkeypatch, label):
    from edgefactory.sources import bettingclosed as bc
    html = f'''<tr class="rowincontri"><td><a href="/prediction/1/cup-club">Cup Club - Away Club <span></span></a></td>
    <td class="resultMt">0-0 <span>{label}</span></td><td class="predMt">2</td></tr>'''
    monkeypatch.setattr(bc, 'get', lambda url: html)
    row = bc.fetch_day('2026-10-28')[0]
    assert row['status'] == terminal_event_disposition(label)
    assert row['hs'] is row['gs'] is None
    assert regulation_score(row) is None


def test_bettingclosed_later_market_cannot_resurrect_postponed_placeholder(monkeypatch):
    from edgefactory.sources import bettingclosed as bc
    def html(cell):
        return f'''<tr class="rowincontri"><td><a href="/prediction/1/cup-club">Cup Club - Away Club <span></span></a></td>
        <td class="resultMt">{cell}</td><td class="predMt">2</td></tr>'''
    pages = iter([html('Postponed'), html('0-0'), html('0-0')])
    monkeypatch.setattr(bc, 'get', lambda url: next(pages))
    row = bc.fetch_day('2026-10-28')[0]
    assert row['status'] == 'POSTPONED'
    assert row['hs'] is row['gs'] is None
