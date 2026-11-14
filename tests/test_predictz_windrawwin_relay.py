from __future__ import annotations

import pytest

from edgefactory.sources import predictz, public_relay, windrawwin

PREDICTZ_HTML = """
<html><title>PredictZ</title><body>
<div class="pttr ptcnt"><div class="pttd ptlg"><h2><a>England Premier League Tips</a></h2></div></div>
<div class="pttr ptcnt"><div class="pttd ptgame"><a>Alpha v Beta</a></div>
<div class="ptpredboxsml">Home 2-1</div>
<div class="pttd ptodds"><a>1.80</a></div><div class="pttd ptodds"><a>3.40</a></div><div class="pttd ptodds"><a>4.20</a></div></div>
</body></html>
"""

WDW_HTML = """
<html><title>WinDrawWin</title><body>
<div class="wttr"><a href="https://www.windrawwin.com/predictions/england-premier-league/">England Premier League</a></div>
<div class="wttr"><a class="wtdesklnk">Alpha v Beta</a>
<div class="wttd wtprd">Home Win</div><div class="wttd wtstk">Medium</div><div class="wttd wtsc">2-1</div></div>
</body></html>
"""


def test_predictz_falls_back_to_operator_relay(monkeypatch):
    monkeypatch.setattr(predictz, "cffi_get", lambda _url: (_ for _ in ()).throw(RuntimeError("HTTP 403")))
    monkeypatch.setattr(
        public_relay,
        "fetches",
        lambda url, *, timeout=40: iter([("https://worker", PREDICTZ_HTML.encode())]),
    )

    rows = predictz.fetch_day("2026-09-30")
    assert len(rows) == 1
    assert rows[0]["home"] == "Alpha"
    assert rows[0]["pick"] == "home"


def test_predictz_rejects_unvalidated_relay_body(monkeypatch):
    monkeypatch.setattr(predictz, "cffi_get", lambda _url: (_ for _ in ()).throw(RuntimeError("HTTP 403")))
    monkeypatch.setattr(
        public_relay,
        "fetches",
        lambda url, *, timeout=40: iter([("https://worker", b"<html>wrong host</html>")]),
    )

    with pytest.raises(RuntimeError, match="PredictZ GET failed"):
        predictz._get("https://www.predictz.com/predictions/20260930/")


def test_windrawwin_falls_back_to_operator_relay(monkeypatch):
    monkeypatch.setattr(windrawwin, "cffi_get", lambda _url: (_ for _ in ()).throw(RuntimeError("HTTP 403")))
    monkeypatch.setattr(
        public_relay,
        "fetches",
        lambda url, *, timeout=40: iter([("https://worker", WDW_HTML.encode())]),
    )

    rows = windrawwin.fetch_day(__import__("datetime").date.today().isoformat())
    assert len(rows) == 1
    assert rows[0]["home"] == "Alpha"
    assert rows[0]["pick"] == "home"


def test_windrawwin_rejects_unvalidated_relay_body(monkeypatch):
    monkeypatch.setattr(windrawwin, "cffi_get", lambda _url: (_ for _ in ()).throw(RuntimeError("HTTP 403")))
    monkeypatch.setattr(
        public_relay,
        "fetches",
        lambda url, *, timeout=40: iter([("https://worker", b"<html>wrong host</html>")]),
    )

    with pytest.raises(RuntimeError, match="WinDrawWin GET failed"):
        windrawwin._get("https://www.windrawwin.com/predictions/today/")
