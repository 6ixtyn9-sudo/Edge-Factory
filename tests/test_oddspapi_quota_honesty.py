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
import urllib.request
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
    # The 429 is raised by the TRANSPORT, so the real fixtures call runs and
    # op._get_json records the provider's headers the way production does.
    #
    # The earlier version monkeypatched cap.fetch_fixtures to raise the
    # exception directly, which skipped the recorder: the receipt's rate_limit
    # then carried whatever the PREVIOUS test in this file had recorded, so the
    # assertion only held in file order. Found 2026-10-12 - the file passes
    # alone, fails when the tests are shuffled (and on the pristine base too:
    # the coupling predates this round's work). Stubbing the transport instead
    # keeps the assertion meaningful: transport -> recorder -> receipt.
    monkeypatch.setenv("ODDSPAPI_API_KEYS", "k1")
    real_fetch_fixtures = cap.fetch_fixtures
    calls = {"fixtures": 0}

    def counted(day):
        calls["fixtures"] += 1
        return real_fetch_fixtures(day)

    def boom(req, timeout=None, **kwargs):
        raise _http_error(429, {"Retry-After": "3600"})

    monkeypatch.setattr(cap, "fetch_fixtures", counted)
    monkeypatch.setattr(urllib.request, "urlopen", boom)
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


def test_a_429_raised_at_the_seam_still_leaves_its_evidence(tmp_path, monkeypatch):
    """The handler records what it caught, not what an earlier call recorded.

    Production reaches these handlers through the transport, which records
    first - so the handler's added call re-records identical values. This test
    covers the bypassed case: a 429 raised directly at the seam must still
    leave the provider's headers on the receipt, and must WIN over an earlier,
    unrelated 429 (the way a quota day could otherwise read as a quiet slate,
    2026-10-10). Both handler sites are in the receipt path this exercises.
    """
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    monkeypatch.setattr(cap, "api_keys", lambda: ("k1",))
    saved = dict(op._RATE_LIMIT_DIAG)
    op._RATE_LIMIT_DIAG.clear()
    try:
        # an earlier, unrelated 429 in the same run (the catalogue fetch)
        op._record_rate_limit(_http_error(429, {"Retry-After": "60"}))

        def board(day):
            raise _http_error(429, {"Retry-After": "3600"})

        monkeypatch.setattr(cap, "fetch_fixtures", board)
        monkeypatch.setattr(
            cap, "fetch_odds",
            lambda fid: (_ for _ in ()).throw(AssertionError("must not be called")))
        receipt = cap.capture("2026-10-10")
        assert receipt["status"] == "quota"
        assert receipt["attempted"] == 0
        # the exception this handler caught, not the stale one
        assert receipt["rate_limit"]["retry_after_s"] == "3600"
    finally:
        op._RATE_LIMIT_DIAG.clear()
        op._RATE_LIMIT_DIAG.update(saved)


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
