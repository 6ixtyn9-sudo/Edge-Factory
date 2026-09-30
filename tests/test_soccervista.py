from __future__ import annotations

from datetime import date as _date

import pytest

from edgefactory.sources import public_relay, soccervista

TODAY = _date.today().isoformat()
_TODAY_DD = _date.today()
_MARKER = _TODAY_DD.strftime("%b") + " " + str(_TODAY_DD.day)

PAGE = """<!doctype html><html><head><title>SoccerVista - Today's Football Betting Predictions &amp; Statistics</title></head>
<body>
<div id="calendar">Matches by date __MARKER__ September 2026</div>
<table class="main">
<thead><tr><th></th><th></th><th></th><th></th><th>1</th><th>X</th><th>2</th><th>1X2</th><th>Goals</th><th>Score</th></tr></thead>
<tbody>
<tr><td colspan="10"><img src="/images/flags/us.png" alt="Country flag"/>
<a href="https://www.soccervista.com/usa/mls/CQv5qrFt/">USA: MLS</a></td></tr>
<tr>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/">19:30</a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/">W<br>W<br>L<br>D<br>L<br>New York Red Bulls</a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/"
 title="View details for New York Red Bulls vs St. Louis City">&gt;&gt;</a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/">St. Louis City<br>W<br>W<br>W<br>D<br>W</a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/">2.45</a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/">3.8</a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/">2.35</a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/"><b>2</b></a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/"><b>O</b></a></td>
<td><a href="/event/new-york-red-bulls-st-louis-city/6VEYBeYP/"><b>1:9</b></a></td>
</tr>
<tr><td colspan="10"><img src="/images/flags/world.png" alt="Country flag"/>
<a href="https://www.soccervista.com/africa/africa-cup-of-nations/8bP2bXmH/">Africa: Africa Cup of Nations</a></td></tr>
<tr>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/">12:00</a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/">D<br>W<br>W<br>L<br>D<br>Eritrea</a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/">&gt;&gt;</a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/">South Africa<br>W<br>L<br>W<br>D<br>L</a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/" title="Eritrea vs South Africa"><img src="/images/odds.png" alt=""/></a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/" title="Eritrea vs South Africa"><img src="/images/odds.png" alt=""/></a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/" title="Eritrea vs South Africa"><img src="/images/odds.png" alt=""/></a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/"><b>1</b></a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/"><b>U</b></a></td>
<td><a href="/event/eritrea-south-africa/WUlqTSd2/"><b>2:1</b></a></td>
</tr>
<tr>
<td><a href="/event/poland-sweden/EPXWrki4/">12:00</a></td>
<td><a href="/event/poland-sweden/EPXWrki4/">W<br>W<br>W<br>W<br>W<br>Poland U21</a></td>
<td><a href="/event/poland-sweden/EPXWrki4/">&gt;&gt;</a></td>
<td><a href="/event/poland-sweden/EPXWrki4/">Sweden U21<br>L<br>L<br>D<br>W<br>W</a></td>
<td><a href="/event/poland-sweden/EPXWrki4/">1.90</a></td>
<td><a href="/event/poland-sweden/EPXWrki4/">3.60</a></td>
<td><a href="/event/poland-sweden/EPXWrki4/">4.20</a></td>
<td><a href="/event/poland-sweden/EPXWrki4/"><b>1</b></a></td>
<td><a href="/event/poland-sweden/EPXWrki4/"><b>O</b></a></td>
<td><a href="/event/poland-sweden/EPXWrki4/"><b>2:1</b></a></td>
</tr>
<tr>
<td><a href="/event/broken-fixture/ZZZZ/">13:00</a></td>
<td><a href="/event/broken-fixture/ZZZZ/"></a></td>
<td><a href="/event/broken-fixture/ZZZZ/">&gt;&gt;</a></td>
<td><a href="/event/broken-fixture/ZZZZ/"></a></td>
<td></td><td></td><td></td><td></td><td></td><td></td>
</tr>
</tbody>
</table>
</body></html>"""


def _page(marker: str = _MARKER) -> str:
    return PAGE.replace("__MARKER__", marker)


def test_parse_extracts_fixtures_and_leagues():
    rows = soccervista._parse(PAGE, TODAY)
    assert len(rows) == 3

    r0 = rows[0]
    assert r0["date"] == TODAY
    assert r0["kickoff"] == "19:30"
    assert r0["league"] == "USA: MLS"
    assert r0["home"] == "New York Red Bulls"
    assert r0["away"] == "St. Louis City"
    assert r0["pick"] == "away"
    assert r0["goals_tip"] == "over"
    assert r0["pred_score"] == "1:9"
    assert (r0["odd1"], r0["oddx"], r0["odd2"]) == (2.45, 3.8, 2.35)
    assert r0["event_id"] == "6VEYBeYP"
    assert r0["url"] == "/event/new-york-red-bulls-st-louis-city/6VEYBeYP/"

    # second league header propagates
    assert rows[1]["league"] == "Africa: Africa Cup of Nations"


def test_parse_missing_odds_become_none():
    rows = soccervista._parse(PAGE, TODAY)
    eritrea = rows[1]
    assert eritrea["home"] == "Eritrea"
    assert eritrea["away"] == "South Africa"
    assert (eritrea["odd1"], eritrea["oddx"], eritrea["odd2"]) == (None, None, None)
    assert eritrea["pick"] == "home"
    assert eritrea["goals_tip"] == "under"
    assert eritrea["pred_score"] == "2:1"


def test_parse_falls_back_to_form_cells_when_details_missing():
    rows = soccervista._parse(PAGE, TODAY)
    # Poland row has no "View details for ..." title: names come from the
    # form+name cells (form letters stripped from home tail / away head).
    poland = rows[2]
    assert poland["home"] == "Poland U21"
    assert poland["away"] == "Sweden U21"
    assert poland["pick"] == "home"


def test_parse_skips_rows_without_teams():
    # the "broken fixture" row in PAGE has a time cell but no team text at all
    rows = soccervista._parse(PAGE, TODAY)
    assert {r["event_id"] for r in rows} == {"6VEYBeYP", "WUlqTSd2", "EPXWrki4"}


def test_parse_empty_page_is_empty():
    assert soccervista._parse("<html><body>no tables here</body></html>", TODAY) == []


def test_fetch_day_non_today_never_fetches(monkeypatch):
    def boom(_url, retries=3):
        raise AssertionError("network must not be attempted for non-today dates")

    monkeypatch.setattr(soccervista, "_get", boom)
    assert soccervista.fetch_day("2001-01-01") == []
    assert soccervista.fetch_day("2999-01-01") == []


def test_fetch_day_today_happy_path(monkeypatch):
    monkeypatch.setattr(soccervista, "_get", lambda url, retries=3: _page())
    rows = soccervista.fetch_day(TODAY)
    assert len(rows) == 3
    assert {r["date"] for r in rows} == {TODAY}


def test_fetch_day_drops_day_rollover_drift(monkeypatch):
    other = _TODAY_DD + __import__("datetime").timedelta(days=1)
    drifted = _page(marker=other.strftime("%b") + " " + str(other.day))
    monkeypatch.setattr(soccervista, "_get", lambda url, retries=3: drifted)
    assert soccervista.fetch_day(TODAY) == []


def test_fetch_day_accepts_missing_day_marker(monkeypatch):
    markerless = _page().replace("Matches by date " + _MARKER, "Matches")
    monkeypatch.setattr(soccervista, "_get", lambda url, retries=3: markerless)
    rows = soccervista.fetch_day(TODAY)
    assert len(rows) == 3


def test_served_day_parses_marker_variants():
    assert soccervista.served_day(_page()) == (_TODAY_DD.month, _TODAY_DD.day)
    assert soccervista.served_day(_page("Oct 3")) == (10, 3)
    assert soccervista.served_day("<html><body>Matches</body></html>") is None


def test_fetch_day_propagates_get_transport_failures(monkeypatch):
    monkeypatch.setattr(
        soccervista, "_get",
        lambda url, retries=3: (_ for _ in ()).throw(RuntimeError("SoccerVista GET failed")),
    )
    with pytest.raises(RuntimeError, match="SoccerVista GET failed"):
        soccervista.fetch_day(TODAY)


def test_fetch_day_genuine_empty_slate_ok(monkeypatch):
    empty = "<html><body>soccervista homepage <table class='main'><tr><td>USA: MLS</td></tr></table></body></html>"
    monkeypatch.setattr(soccervista, "_get", lambda url, retries=3: empty)
    assert soccervista.fetch_day(TODAY) == []


def test_fetch_day_missing_homepage_is_retryable_transport_failure(monkeypatch):
    monkeypatch.setattr(
        soccervista,
        "_get",
        lambda url, retries=3: (_ for _ in ()).throw(RuntimeError("SoccerVista GET failed")),
    )
    with pytest.raises(RuntimeError, match="SoccerVista GET failed"):
        soccervista.fetch_day(TODAY)


def test_get_ladders_to_cffi_then_relay(monkeypatch):
    calls = []

    def urllib_fail(url):
        calls.append(("urllib", url))
        raise OSError("tls cut")

    def cffi_fail(url, identity):
        calls.append((f"cffi:{identity}", url))
        raise OSError("blocked")

    def relay(url, *, timeout=40):
        yield "https://worker-relay", b"<html>soccervista<table></table></html>"

    monkeypatch.setattr(soccervista, "_urllib_get", urllib_fail)
    monkeypatch.setattr(soccervista, "_cffi_get", cffi_fail)
    monkeypatch.setattr(soccervista.time, "sleep", lambda *_a: None)
    monkeypatch.setattr(public_relay, "fetches", relay)
    html = soccervista._get(soccervista.URL)
    assert html == "<html>soccervista<table></table></html>"
    assert calls[0][0] == "urllib" and calls[1][0].startswith("cffi:")


def test_get_escalates_branded_tableless_shell_to_next_transport(monkeypatch):
    calls = []

    def urllib_shell(url):
        calls.append(("urllib", url))
        return "<html><title>SoccerVista</title><body>soccervista consent shell</body></html>"

    def cffi_ok(url, identity):
        calls.append((f"cffi:{identity}", url))
        return _page()

    monkeypatch.setattr(soccervista, "_urllib_get", urllib_shell)
    monkeypatch.setattr(soccervista, "_cffi_get", cffi_ok)
    monkeypatch.setattr(soccervista.time, "sleep", lambda *_a: None)

    html = soccervista._get(soccervista.URL)
    assert html == _page()
    assert [name for name, _url in calls] == ["urllib", "cffi:safari17_0"]


def test_get_raises_when_all_transports_return_tableless_shells(monkeypatch):
    shell = "<html><title>SoccerVista</title><body>soccervista consent shell</body></html>"
    monkeypatch.setattr(soccervista, "_urllib_get", lambda _u: shell)
    monkeypatch.setattr(soccervista, "_cffi_get", lambda _u, _i: shell)
    monkeypatch.setattr(soccervista.time, "sleep", lambda *_a: None)
    monkeypatch.setattr(
        public_relay, "fetches",
        lambda url, *, timeout=40: iter([("https://worker-relay", shell.encode())]),
    )

    with pytest.raises(RuntimeError, match="TransportValidationError"):
        soccervista._get(soccervista.URL)


def test_get_rejects_unvalidated_relay_body(monkeypatch):
    monkeypatch.setattr(soccervista, "_urllib_get", lambda _u: (_ for _ in ()).throw(OSError("x")))
    monkeypatch.setattr(soccervista, "_cffi_get", lambda _u, _i: (_ for _ in ()).throw(OSError("y")))
    monkeypatch.setattr(soccervista.time, "sleep", lambda *_a: None)
    monkeypatch.setattr(
        public_relay, "fetches",
        lambda url, *, timeout=40: iter([("https://worker-relay", b"<html>wrong provenance</html>")]),
    )
    with pytest.raises(RuntimeError):
        soccervista._get(soccervista.URL)


def test_columns_cover_row_keys():
    rows = soccervista._parse(PAGE, TODAY)
    assert rows
    for row in rows:
        assert set(row) == set(soccervista.COLUMNS)
