from __future__ import annotations

import json

import pytest

from edgefactory.sources import forebet


def _raw(rows):
    return json.dumps([rows, {"meta": True}]).encode()


def _row(match_id="1"):
    return {
        "id": match_id,
        "HOST_NAME": "Alpha",
        "GUEST_NAME": "Beta",
        "Pred_1": "55",
        "Pred_X": "25",
        "Pred_2": "20",
    }


def test_decode_payload_accepts_forebet_shape_and_honest_empty():
    assert forebet._decode_payload(_raw([_row()]))[0]["id"] == "1"
    assert forebet._decode_payload(_raw([])) == []


@pytest.mark.parametrize("raw", [b"<html>challenge</html>", b"{}", b"[]"])
def test_decode_payload_rejects_challenge_or_wrong_shape(raw):
    with pytest.raises((json.JSONDecodeError, ValueError)):
        forebet._decode_payload(raw)


def test_get_falls_back_to_browser_transport(monkeypatch):
    calls = []

    def blocked(_url):
        calls.append("urllib")
        raise RuntimeError("blocked")

    def browser(_url, identity):
        calls.append(identity)
        return _raw([_row()])

    monkeypatch.setattr(forebet, "_urllib_get", blocked)
    monkeypatch.setattr(forebet, "_cffi_get", browser)
    monkeypatch.setattr(forebet.time, "sleep", lambda _seconds: None)

    rows = forebet._get("1x2", "2026-08-20")
    assert len(rows) == 1
    assert calls == ["urllib", "safari17_0"]


def test_get_raises_after_all_transports_fail(monkeypatch):
    monkeypatch.setattr(
        forebet, "_urllib_get", lambda _url: (_ for _ in ()).throw(RuntimeError("blocked"))
    )
    monkeypatch.setattr(
        forebet,
        "_cffi_get",
        lambda _url, _identity: (_ for _ in ()).throw(RuntimeError("blocked")),
    )
    monkeypatch.setattr(forebet.time, "sleep", lambda _seconds: None)

    with pytest.raises(RuntimeError, match="failed across transports"):
        forebet._get("1x2", "2026-08-20")


def test_fetch_day_does_not_turn_total_transport_failure_into_empty(monkeypatch):
    monkeypatch.setattr(
        forebet,
        "_get",
        lambda _market, _day: (_ for _ in ()).throw(RuntimeError("blocked")),
    )

    with pytest.raises(RuntimeError, match="no usable rows"):
        forebet.fetch_day("2026-08-20", sleep=0)


def test_fetch_day_allows_genuinely_empty_valid_payloads(monkeypatch):
    monkeypatch.setattr(forebet, "_get", lambda _market, _day: [])
    assert forebet.fetch_day("2026-08-20", sleep=0) == []


def test_fetch_day_preserves_partial_market_capture(monkeypatch, capsys):
    def fetch(market, _day):
        if market == "1x2":
            return [_row()]
        raise RuntimeError("blocked")

    monkeypatch.setattr(forebet, "_get", fetch)
    rows = forebet.fetch_day("2026-08-20", sleep=0)

    assert len(rows) == 1
    assert rows[0]["home"] == "Alpha"
    assert "partial capture" in capsys.readouterr().err
