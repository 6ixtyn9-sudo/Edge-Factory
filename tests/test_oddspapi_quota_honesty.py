"""OddsPapi quota/auth days must be diagnosable, not silent multipliers.

Run 38027657811: one configured key answered HTTP 429 on the fixtures board;
the capture receipt carried a bare error string, attempted 0, and the health
line read "no pre-build OddsPAPI rows" — indistinguishable from a quiet
slate. The per-fixture loop also kept calling into a daily bucket that was
already empty.
"""

from __future__ import annotations

import json
import urllib.error
from pathlib import Path

from edgefactory.sources import oddspapi_odds as op
import scripts.capture_oddspapi as cap


def _http_error(code: int, headers: dict | None = None) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://api.oddspapi.io/v4/fixtures", code, "Too Many Requests",
        hdrs=(headers or {}), fp=None)


def test_rate_limit_headers_are_recorded_not_lost():
    exc = _http_error(429, {"Retry-After": "3600", "X-RateLimit-Remaining-Day": "0"})
    op._record_rate_limit(exc)
    diag = op.rate_limit_diagnostics()
    assert diag["http_status"] == 429
    assert diag["retry_after_s"] == "3600"
    assert diag["rate_limit_remaining"] == "0"


def test_429_on_the_board_stops_the_capture_and_writes_quota_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)  # keep receipts out of repo localdata
    monkeypatch.setattr(cap, "api_keys", lambda: ("k1",))
    calls = {"fixtures": 0}

    def boom(day):
        calls["fixtures"] += 1
        raise _http_error(429, {"Retry-After": "3600"})

    monkeypatch.setattr(cap, "fetch_fixtures", boom)
    monkeypatch.setattr(cap, "fetch_odds",
                        lambda fid: (_ for _ in ()).throw(AssertionError("must not be called")))
    receipt = cap.capture("2026-10-10")
    assert calls["fixtures"] == 1
    assert receipt["status"] == "quota"
    assert receipt["http_status"] == 429
    assert receipt["rate_limit"]["retry_after_s"] == "3600"
    assert receipt["attempted"] == 0
    # receipt persisted for the health line to read
    persisted = json.loads(
        (Path(cap.OUT_DIR) / "oddspapi_capture_2026-10-10.json").read_text())
    assert persisted["status"] == "quota"


def test_429_on_a_fixture_call_stops_the_whole_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)  # keep receipts out of repo localdata
    monkeypatch.setattr(cap, "api_keys", lambda: ("k1",))
    fixtures = [{"fixtureId": f"f{i}", "participant1Name": "A", "participant2Name": "B"}
                for i in range(5)]
    monkeypatch.setattr(cap, "fetch_fixtures", lambda day: fixtures)
    odds_calls = {"n": 0}

    def boom(fid):
        odds_calls["n"] += 1
        raise _http_error(429)

    monkeypatch.setattr(cap, "fetch_odds", boom)
    receipt = cap.capture("2026-10-10")
    # exactly ONE per-fixture call, then the pass stops: a daily bucket does
    # not recover mid-run and continuing would multiply requests.
    assert odds_calls["n"] == 1
    assert receipt["status"] == "quota"
    assert receipt["attempted"] == 1
    assert any("capture stopped" in e for e in receipt["errors"])


def test_5xx_on_the_board_is_unavailable_not_a_credential_story(tmp_path, monkeypatch):
    # Negative control for the receipt classification: a server-side 500 on
    # the fixtures board stops the pass (daily-bucket discipline) but must
    # never be reported as auth/quota — the health line would otherwise name
    # a credential fix for a provider outage.
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    monkeypatch.setattr(cap, "api_keys", lambda: ("k1",))

    def server_error(day):
        raise _http_error(500)

    monkeypatch.setattr(cap, "fetch_fixtures", server_error)
    monkeypatch.setattr(cap, "fetch_odds",
                        lambda fid: (_ for _ in ()).throw(AssertionError("must not be called")))
    receipt = cap.capture("2026-10-10")
    assert receipt["status"] == "unavailable"
    assert receipt["http_status"] == 500
    assert receipt["attempted"] == 0
    persisted = json.loads(
        (Path(cap.OUT_DIR) / "oddspapi_capture_2026-10-10.json").read_text())
    assert persisted["status"] == "unavailable"
    # and the health-line classifier maps it to the unavailable reason family
    from edgefactory.source_health import zero_row_reason
    assert zero_row_reason("unavailable", [500]) == "http_500_unavailable"
