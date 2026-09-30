from __future__ import annotations

from datetime import date as _date
from datetime import timedelta

import pytest

from edgefactory.sources import prosoccer, public_relay


def _page(h1_date: str, table: str) -> str:
    return f"""<!doctype html><html><head><title>ProSoccer | Free Football Predictions Today</title></head>
<body>
<h1>Intelligent Football Predictions for {h1_date}</h1>
<div class="info">Displaying 1 - 5 out of 2 soccer matches</div>
{table}
</body></html>"""


TABLE = """
<table id="tblPredictions" class="tablesaw">
<thead><tr><th>League</th><th>UTC</th><th>Match</th><th>1</th><th>X</th><th>2</th>
<th>Tips</th><th>1</th><th>X</th><th>2</th><th>Pred</th><th>Pred</th><th>U</th><th>O</th><th>Final</th></tr></thead>
<tbody>
<tr><td>JPL</td><td>11:00</td><td>SAGAN TOSU - TOKYO VERDY</td>
<td>31</td><td>28</td><td>41</td><td>f21</td>
<td>3.20</td><td>3.30</td><td>2.10</td>
<td>0-<b>1</b></td><td>0-2</td><td>54</td><td>46</td><td>1 - 1</td></tr>
<tr class="tablesaw-child"><td colspan="15"><div class="extra">Per-corner stats here</div></td></tr>
<tr><td>FGC</td><td>14:00</td><td>JAGIELLONIA - SUDUVA</td>
<td>53</td><td>31</td><td>16</td><td>c1X-1</td>
<td></td><td></td><td></td>
<td>2-<b>0</b></td><td>1-<b>0</b></td><td>46</td><td>54</td><td></td></tr>
<tr><td>EUN</td><td>16:59</td><td>FINLAND - BELARUS</td>
<td>72</td><td>20</td><td>8</td><td>f1</td>
<td>1.80</td><td>3.25</td><td>4.55</td>
<td>2-<b>0</b></td><td><b>1</b>-0</td><td>42</td><td>58</td><td>Postp.</td></tr>
<tr><td colspan="4"><div class="ad">advertisement</div></td></tr>
</tbody>
</table>
"""

TODAY = _date.today().isoformat()


def test_parse_extracts_full_schema():
    rows = prosoccer._parse(_page("Tuesday 29 September 2026", TABLE), "2026-09-29")
    assert len(rows) == 3

    r0 = rows[0]
    assert r0["date"] == "2026-09-29"
    assert r0["kickoff"] == "11:00"
    assert r0["league"] == "JPL"
    assert r0["home"] == "SAGAN TOSU"
    assert r0["away"] == "TOKYO VERDY"
    assert (r0["p1"], r0["px"], r0["p2"]) == (31.0, 28.0, 41.0)
    assert r0["tip"] == "f21"
    assert (r0["odd1"], r0["oddx"], r0["odd2"]) == (3.20, 3.30, 2.10)
    assert r0["pred_score1"] == "0-1"
    assert r0["pred_score2"] == "0-2"
    assert (r0["p_u25"], r0["p_o25"]) == (54.0, 46.0)
    assert (r0["hs"], r0["gs"]) == (1, 1)
    assert r0["status"] == "FT"

    # unfinished fixture: no odds, no final score
    r1 = rows[1]
    assert (r1["odd1"], r1["oddx"], r1["odd2"]) == (None, None, None)
    assert (r1["hs"], r1["gs"]) == (None, None)
    assert r1["status"] is None
    assert r1["pred_score1"] == "2-0"

    # postponed fixture keeps a terminal status, never a phantom score
    r2 = rows[2]
    assert (r2["hs"], r2["gs"]) == (None, None)
    assert r2["status"] == "Postp."


def test_parse_skips_malformed_rows():
    malformed = """
    <table id="tblPredictions">
    <tr><td>US1</td><td>bad</td><td>COLUMBUS - MIAMI FC</td>
    <td>33</td><td>28</td><td>39</td><td>c21-1</td><td>2.70</td><td>3.85</td><td>2.15</td></tr>
    <tr><td>US1</td><td>00:00</td><td>ONLYHOME</td>
    <td>33</td><td>28</td><td>39</td><td>c21-1</td><td>2.70</td><td>3.85</td><td>2.15</td></tr>
    <tr><td>US1</td><td>00:00</td><td>COLUMBUS - MIAMI FC</td>
    <td>xx</td><td>28</td><td>39</td><td>c21-1</td><td>2.70</td><td>3.85</td><td>2.15</td></tr>
    <tr><td>US1</td><td>00:05</td><td>FORTALEZA BOGOTA - DEPORTES TOLIMA</td>
    <td>22</td><td>28</td><td>50</td><td>c2X-X</td><td>3.10</td><td>3.05</td><td>2.25</td>
    <td>0-1</td><td>0-2</td><td>52</td><td>48</td><td>2 - 2</td></tr>
    </table>"""
    rows = prosoccer._parse(_page("Monday 28 September 2026", malformed), "2026-09-28")
    assert len(rows) == 1
    assert rows[0]["home"] == "FORTALEZA BOGOTA"
    assert (rows[0]["hs"], rows[0]["gs"]) == (2, 2)


def test_parse_missing_table_raises_unless_page_not_found():
    with pytest.raises(RuntimeError):
        prosoccer._parse("<html><body>cf-challenge-wrapper</body></html>", TODAY)
    gone = "<html><head><title>ProSoccer | Page Not Found</title></head><body>Page not found</body></html>"
    assert prosoccer._parse(gone, TODAY) == []


def test_page_date_parses_h1():
    html = _page("Thursday 01 October 2026", TABLE)
    assert prosoccer.page_date(html) == "2026-10-01"
    assert prosoccer.page_date("<html><body>no heading</body></html>") is None


def test_url_for_routes_only_prediction_week():
    assert prosoccer.url_for("2026-09-29", today="2026-09-29") == prosoccer.BASE
    assert prosoccer.url_for("2026-09-28", today="2026-09-29").endswith("yesterday.html")
    assert prosoccer.url_for("2026-09-30", today="2026-09-29").endswith("tomorrow.html")
    # a nearby weekday routes to its weekday page ...
    assert prosoccer.url_for("2026-10-01", today="2026-09-29").endswith("Thursday.html")
    # ... and anything beyond the window is out of coverage without a fetch
    assert prosoccer.url_for("2026-10-20", today="2026-09-29") is None
    assert prosoccer.url_for("2026-09-10", today="2026-09-29") is None


def test_fetch_day_out_of_window_never_fetches(monkeypatch):
    def boom(_url, retries=3):
        raise AssertionError("network must not be attempted for out-of-window dates")

    monkeypatch.setattr(prosoccer, "_get", boom)
    assert prosoccer.fetch_day("2001-01-01") == []
    assert prosoccer.fetch_day("2999-01-01") == []


def test_fetch_day_rejects_h1_mismatch(monkeypatch):
    tomorrow = (_date.today() + timedelta(days=1))
    served = tomorrow.strftime("%A %d %B %Y")
    monkeypatch.setattr(prosoccer, "_get", lambda url, retries=3: _page(served, TABLE))
    with pytest.raises(prosoccer.NotServedYet, match="no candidate page serves"):
        prosoccer.fetch_day(_date.today().isoformat())


def test_fetch_day_tries_tomorrow_alias_during_utc_lag(monkeypatch):
    today = _date.today()
    yesterday = today - timedelta(days=1)
    calls = []

    def get(url, retries=3):
        calls.append(url)
        if url.endswith("tomorrow.html"):
            return _page(today.strftime("%A %d %B %Y"), TABLE)
        return _page(yesterday.strftime("%A %d %B %Y"), TABLE)

    monkeypatch.setattr(prosoccer, "_get", get)
    rows = prosoccer.fetch_day(today.isoformat())
    assert len(rows) == 3
    assert calls[0] == prosoccer.BASE
    assert calls[1].endswith("tomorrow.html")


def test_fetch_day_happy_path(monkeypatch):
    today = _date.today()
    served = today.strftime("%A %d %B %Y")
    monkeypatch.setattr(prosoccer, "_get", lambda url, retries=3: _page(served, TABLE))
    rows = prosoccer.fetch_day(today.isoformat())
    assert len(rows) == 3
    assert {r["date"] for r in rows} == {today.isoformat()}


def test_get_ladders_to_cffi_then_relay(monkeypatch):
    calls = []

    def urllib_fail(url):
        calls.append(("urllib", url))
        raise OSError("tls cut")

    def cffi_ok(url, identity):
        calls.append((f"cffi:{identity}", url))
        return "<html>tblPredictions</html>"

    monkeypatch.setattr(prosoccer, "_urllib_get", urllib_fail)
    monkeypatch.setattr(prosoccer, "_cffi_get", cffi_ok)
    monkeypatch.setattr(prosoccer.time, "sleep", lambda *_a: None)
    html = prosoccer._get("https://www.prosoccer.gr/en/football/predictions/")
    assert html == "<html>tblPredictions</html>"
    assert calls[0][0] == "urllib"

    def cffi_fail(url, identity):
        raise OSError("blocked")

    def relay(url, *, timeout=40):
        yield "https://worker-relay", b"<html>tblPredictions ok</html>"

    monkeypatch.setattr(prosoccer, "_cffi_get", cffi_fail)
    monkeypatch.setattr(public_relay, "fetches", relay)
    html = prosoccer._get("https://www.prosoccer.gr/en/football/predictions/")
    assert html == "<html>tblPredictions ok</html>"


def test_get_raises_when_all_transports_fail(monkeypatch):
    monkeypatch.setattr(prosoccer, "_urllib_get", lambda _u: (_ for _ in ()).throw(OSError("x")))
    monkeypatch.setattr(prosoccer, "_cffi_get", lambda _u, _i: (_ for _ in ()).throw(OSError("y")))
    monkeypatch.setattr(prosoccer.time, "sleep", lambda *_a: None)
    monkeypatch.setattr(public_relay, "fetches", lambda url, *, timeout=40: iter(()))
    with pytest.raises(RuntimeError):
        prosoccer._get("https://www.prosoccer.gr/en/football/predictions/")


def test_columns_cover_row_keys():
    rows = prosoccer._parse(_page("Tuesday 29 September 2026", TABLE), "2026-09-29")
    assert rows
    for row in rows:
        assert set(row) == set(prosoccer.COLUMNS)
