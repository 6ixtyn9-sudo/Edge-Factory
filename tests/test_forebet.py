from __future__ import annotations

import json
import threading

import pytest

from edgefactory.sources import forebet, public_relay


_AUTHORIZATION_CREDENTIALS = [
    pytest.param("Token synthetic-sensitive-value", id="token"),
    pytest.param(
        'Digest username="synthetic-sensitive-value", '
        'nonce="synthetic-nonce-value", response="synthetic-response-value"',
        id="digest",
    ),
    pytest.param(
        "AWS4-HMAC-SHA256 Credential=synthetic-sensitive-value, "
        "SignedHeaders=host;x-amz-date, Signature=synthetic-signature-value",
        id="aws",
    ),
]


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


def test_decode_payload_rejects_malformed_forebet_rows():
    with pytest.raises(ValueError, match="row shape"):
        forebet._decode_payload(_raw([_row(), "not a match row"]))


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


def test_relay_wrapper_requires_exact_source_and_single_marker():
    source = "https://www.forebet.com/scripts/getrs.php?x=1"
    wrapped = f"Title: \n\nURL Source: {source}\n\n{forebet.RELAY_MARKER}".encode() + _raw([_row()])
    assert forebet._unwrap_relay(wrapped, source) == _raw([_row()])

    with pytest.raises(ValueError, match="source URL mismatch"):
        forebet._unwrap_relay(wrapped, source + "&other=1")
    with pytest.raises(ValueError, match="marker count"):
        forebet._unwrap_relay(b"no wrapper", source)



def _browser_envelope(source_url, **fields):
    payload = {
        "operation": forebet.BROWSER_OPERATION,
        "transport": forebet.BROWSER_TRANSPORT,
        "source_url": source_url,
        "status": 200,
        "body_shape": "forebet_getrs",
        "body": _raw([_row()]).decode(),
    }
    payload.update(fields)
    return json.dumps(payload).encode()


class _RelayResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def read(self, _limit):
        return self._payload


def test_browser_get_accepts_only_identified_browser_run_envelope(monkeypatch):
    source = "https://www.forebet.com/scripts/getrs.php?ln=en&tp=1x2&in=2026-09-30&ord=0&tz=0&tzs=&tze=&output=1"
    monkeypatch.setenv(public_relay.URLS_ENV, "https://worker")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "secret")
    monkeypatch.setattr(
        forebet.urllib.request,
        "urlopen",
        lambda _request, timeout: _RelayResponse(_browser_envelope(source)),
    )

    assert forebet._browser_get(source) == _raw([_row()])


def test_browser_get_rejects_legacy_generic_relay_envelope(monkeypatch):
    source = "https://www.forebet.com/scripts/getrs.php?ln=en&tp=1x2&in=2026-09-30&ord=0&tz=0&tzs=&tze=&output=1"
    legacy = json.dumps({
        "source_url": source,
        "status": 200,
        "body": _raw([_row()]).decode(),
    }).encode()
    monkeypatch.setenv(public_relay.URLS_ENV, "https://worker")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "secret")
    monkeypatch.setattr(
        forebet.urllib.request,
        "urlopen",
        lambda _request, timeout: _RelayResponse(legacy),
    )

    with pytest.raises(ValueError, match="operation marker mismatch"):
        forebet._browser_get(source)

def test_browser_run_operation_sits_above_plain_relays_when_enabled(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(forebet.BROWSER_ENV, "on")
    monkeypatch.setenv(public_relay.URLS_ENV, "https://worker")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "secret")
    calls = []
    monkeypatch.setattr(
        forebet,
        "_browser_get",
        lambda url: calls.append(("browser", url)) or _raw([_row()]),
    )
    monkeypatch.setattr(
        public_relay,
        "fetches",
        lambda _url: (_ for _ in ()).throw(AssertionError("plain relay called")),
    )

    rows = forebet._get("1x2", "2026-08-20")
    assert len(rows) == 1
    assert calls and calls[0][0] == "browser"
    assert "output=1" in calls[0][1]


def test_browser_run_failure_falls_back_to_plain_relay(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(forebet.BROWSER_ENV, "on")
    monkeypatch.setenv(public_relay.URLS_ENV, "https://worker")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "secret")
    monkeypatch.setattr(
        forebet,
        "_browser_get",
        lambda _url: (_ for _ in ()).throw(ValueError("challenge")),
    )
    monkeypatch.setattr(
        public_relay,
        "fetches",
        lambda url: iter([("https://worker", _raw([_row("relay")]))]),
    )

    rows = forebet._get("1x2", "2026-08-20")
    assert len(rows) == 1
    assert rows[0]["id"] == "relay"


def test_optional_playwright_fallback_sits_between_browser_and_plain_relays(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(forebet.BROWSER_ENV, "on")
    monkeypatch.setenv(forebet.PLAYWRIGHT_ENV, "1")
    monkeypatch.setenv(public_relay.URLS_ENV, "https://worker")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "secret")
    calls = []
    monkeypatch.setattr(
        forebet,
        "_browser_get",
        lambda _url: calls.append("browser") or (_ for _ in ()).throw(ValueError("challenge")),
    )
    monkeypatch.setattr(
        forebet,
        "_playwright_get",
        lambda _url: calls.append("playwright") or _raw([_row("pw")]),
    )
    monkeypatch.setattr(
        public_relay,
        "fetches",
        lambda _url: (_ for _ in ()).throw(AssertionError("plain relay called")),
    )

    rows = forebet._get("1x2", forebet._today().isoformat())
    assert len(rows) == 1
    assert rows[0]["id"] == "pw"
    assert calls == ["browser", "playwright"]


def test_github_actions_uses_relay_before_direct_transport(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(forebet.BROWSER_ENV, "off")
    monkeypatch.delenv(forebet.CLOUD_RETRY_ENV, raising=False)
    calls = []
    monkeypatch.setattr(
        forebet,
        "_relay_get",
        lambda url: calls.append(url) or _raw([_row()]),
    )
    monkeypatch.setattr(
        forebet,
        "_urllib_get",
        lambda _url: (_ for _ in ()).throw(AssertionError("direct transport called")),
    )

    rows = forebet._get("1x2", "2026-08-20")
    assert len(rows) == 1
    assert calls and calls[0].startswith(forebet.BASE)
    assert "output=1" in calls[0]


def test_github_actions_skips_known_dead_direct_transport_when_relay_is_challenged(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(forebet.BROWSER_ENV, "off")
    monkeypatch.delenv(forebet.CLOUD_RETRY_ENV, raising=False)
    direct = []
    monkeypatch.setattr(
        forebet,
        "_relay_get",
        lambda _url: (_ for _ in ()).throw(ValueError("challenge")),
    )
    monkeypatch.setattr(
        forebet,
        "_urllib_get",
        lambda url: direct.append(url) or _raw([_row()]),
    )

    with pytest.raises(RuntimeError, match="GitHub direct transport skipped"):
        forebet._get("1x2", "2026-08-20")
    assert direct == []


def test_github_relay_fetches_independent_markets_concurrently(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv(forebet.CLOUD_RETRY_ENV, raising=False)
    barrier = threading.Barrier(len(forebet.DEFAULT_MARKETS))
    calls = []

    def concurrent_get(market, _day):
        calls.append(market)
        barrier.wait(timeout=2)
        return [_row()]

    monkeypatch.setattr(forebet, "_get", concurrent_get)
    rows = forebet.fetch_day("2026-08-20", sleep=0)

    assert len(rows) == 1
    assert set(calls) == set(forebet.DEFAULT_MARKETS)


def test_github_actions_can_be_explicitly_disabled(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(forebet.CLOUD_RETRY_ENV, "off")
    with pytest.raises(RuntimeError, match="explicitly disabled"):
        forebet.fetch_day("2026-08-20", sleep=0)


def test_github_actions_direct_retry_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(forebet.CLOUD_RETRY_ENV, "direct")
    calls = []
    monkeypatch.setattr(
        forebet,
        "_urllib_get",
        lambda url: calls.append(url) or _raw([_row()]),
    )
    monkeypatch.setattr(
        forebet,
        "_relay_get",
        lambda _url: (_ for _ in ()).throw(AssertionError("relay called")),
    )

    rows = forebet._get("1x2", "2026-08-20")
    assert len(rows) == 1
    assert len(calls) == 1


def _failure_mode(monkeypatch, mode):
    monkeypatch.setattr(forebet, "_cloud_fetch_mode", lambda: mode)
    monkeypatch.setattr(forebet, "_browser_enabled_for_date", lambda _day: False)
    monkeypatch.setattr(forebet, "_playwright_enabled_for_date", lambda _day: False)


@pytest.mark.parametrize("mode", ["direct", "relay"])
def test_market_failure_reason_survives_and_deduplicates(monkeypatch, mode):
    _failure_mode(monkeypatch, mode)
    def fail(market, day):
        raise RuntimeError(f"Forebet {market} {day} relay=absent;\n browser=HTTP 403")
    monkeypatch.setattr(forebet, "_get", fail)
    with pytest.raises(RuntimeError) as caught:
        forebet.fetch_day("2026-10-07", sleep=0)
    text = str(caught.value)
    for market in forebet.DEFAULT_MARKETS:
        assert f"{market}:RuntimeError" in text
    assert text.count("relay=absent; browser=HTTP 403") == 1
    assert "\n" not in text
    print("P3 AFTER", mode, text)


@pytest.mark.parametrize("mode", ["direct", "relay"])
def test_partial_failure_summary_is_bounded_and_redacted(monkeypatch, capsys, mode):
    _failure_mode(monkeypatch, mode)
    monkeypatch.setenv(public_relay.TOKEN_ENV, "configured-secret")
    monkeypatch.setenv(public_relay.URLS_ENV, "https://private.example/path-secret")
    def fetch(market, day):
        if market == "1x2":
            return [_row()]
        raise RuntimeError('configured-secret https://private.example/path-secret '
                           'https://user:pass@example.org/?key=hidden '
                           '"token": "echoed-secret" Bearer auth-secret\n' + "x" * 5000)
    monkeypatch.setattr(forebet, "_get", fetch)
    rows = forebet.fetch_day("2026-10-07", sleep=0)
    assert len(rows) == 1 and rows[0]["p1"] == 55
    text = capsys.readouterr().err
    assert "partial capture" in text and "uo:RuntimeError,bts:RuntimeError" in text
    assert len(text.split("failed markets=", 1)[1].strip()) <= forebet._FAILURE_SUMMARY_MAX
    assert len(text.splitlines()) == 1
    for secret in ("configured-secret", "path-secret", "hidden", "user:pass", "echoed-secret", "auth-secret"):
        assert secret not in text
    assert "..." in text


def test_failure_summary_caps_distinct_reasons_and_keeps_empty_prefix(monkeypatch):
    _failure_mode(monkeypatch, "relay")
    def fail(market, day):
        raise ValueError(market + "x" * 5000)
    monkeypatch.setattr(forebet, "_get", fail)
    _, failures = forebet._fetch_market_payloads("2026-10-07", ("1x2", "uo", "bts", "ht"), 0)
    assert len(failures) == 4
    for failure in failures:
        assert len(failure.split(": ", 1)[1]) <= forebet._FAILURE_DETAIL_MAX
    assert len(forebet._failure_summary(failures * 5)) <= forebet._FAILURE_SUMMARY_MAX
    assert forebet._market_failures([("1x2", "RuntimeError", "")]) == ["1x2:RuntimeError"]


def test_refresher_receives_forebet_reason(monkeypatch, tmp_path):
    from scripts import refresh_result_sources as refresh
    _failure_mode(monkeypatch, "direct")
    monkeypatch.setattr(forebet, "_get", lambda *_: (_ for _ in ()).throw(
        RuntimeError("relay=absent; browser=HTTP 403")))
    receipt = refresh.refresh_source("forebet", "2026-10-07", localdata=tmp_path)
    assert "relay=absent; browser=HTTP 403" in receipt["status"]
    assert receipt["raw"] == 0
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("message", [
    "Authorization: Bearer synthetic-secret",
    "authorization=Basic synthetic-secret",
    "{'Authorization': 'Bearer synthetic-secret'}",
    "Bearer synthetic-secret",
])
def test_failure_detail_redacts_authorization_value(message):
    text = forebet._failure_detail(RuntimeError(message), "1x2", "2026-10-07")
    assert "synthetic-secret" not in text
    assert "[redacted]" in text


@pytest.mark.parametrize("credentials", _AUTHORIZATION_CREDENTIALS)
@pytest.mark.parametrize("serialization", ["header", "repr", "json"])
def test_failure_detail_redacts_complete_authorization_header(
    monkeypatch, credentials, serialization,
):
    # Isolate generic header redaction from configured-token replacement.
    monkeypatch.delenv(public_relay.TOKEN_ENV, raising=False)
    monkeypatch.delenv(public_relay.URLS_ENV, raising=False)
    headers = {"Authorization": credentials, "message": "retry limit reached"}
    if serialization == "header":
        message = f"Authorization: {credentials}"
    elif serialization == "repr":
        message = repr(headers)
    else:
        message = json.dumps(headers)
    text = forebet._failure_detail(RuntimeError(f"relay HTTP 403; {message}"))
    assert text.startswith("relay HTTP 403; ")
    assert "[redacted]" in text
    assert "synthetic-" not in text
    if serialization != "header":
        assert "retry limit reached" in text
    assert len(text) <= forebet._FAILURE_DETAIL_MAX
    assert len(text.splitlines()) == 1


def test_failure_detail_redacts_folded_authorization_value(monkeypatch):
    monkeypatch.delenv(public_relay.TOKEN_ENV, raising=False)
    message = (
        "relay HTTP 403; Authorization: Token\n"
        "    synthetic-sensitive-value\n"
        "socket timeout"
    )
    text = forebet._failure_detail(RuntimeError(message))
    assert "synthetic-" not in text
    assert "relay HTTP 403" in text and "socket timeout" in text
    assert len(text.splitlines()) == 1


def test_failure_detail_does_not_trust_redaction_marker_in_header():
    text = forebet._failure_detail(RuntimeError(
        "relay HTTP 403; Authorization: [redacted] synthetic-sensitive-value"
    ))
    assert "synthetic-" not in text
    assert "relay HTTP 403" in text


def test_authorization_redaction_is_idempotent_and_keeps_other_transport_causes():
    first = forebet._safe_failure_text(
        "browser HTTP 403; Authorization: Token synthetic-sensitive-value"
    )
    assert "synthetic-" not in first
    assert forebet._safe_failure_text(first) == first
    combined = first + "; playwright=TimeoutError: navigation timed out"
    assert forebet._safe_failure_text(combined) == combined


def test_real_get_preserves_transport_reason_through_fetch_day(monkeypatch):
    _failure_mode(monkeypatch, "direct")
    monkeypatch.setattr(public_relay, "fetches", lambda _url: iter(()))
    monkeypatch.setattr(forebet.time, "sleep", lambda _seconds: None)

    def fail(_url):
        raise RuntimeError("HTTP 403; distinctive transport reason")

    monkeypatch.setattr(forebet, "_urllib_get", fail)
    monkeypatch.setattr(forebet, "_cffi_get", lambda *_: (_ for _ in ()).throw(
        RuntimeError("TLS unavailable")))
    with pytest.raises(RuntimeError) as caught:
        forebet.fetch_day("2026-10-07", sleep=0)
    text = str(caught.value)
    assert "urllib=RuntimeError: HTTP 403; distinctive transport reason" in text
    assert text.count("distinctive transport reason") == 1


def test_browser_http_failure_never_includes_response_body(monkeypatch):
    import io
    import urllib.error

    monkeypatch.setenv(public_relay.URLS_ENV, "https://private.example/path-secret")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "configured-secret")
    error = urllib.error.HTTPError(
        "https://private.example/path-secret", 403, "Forbidden", {},
        io.BytesIO(b"untrusted body may echo a token or arbitrary credentials"),
    )
    monkeypatch.setattr(forebet.urllib.request, "urlopen", lambda *_args, **_kwargs: (
        _ for _ in ()).throw(error))
    with pytest.raises(RuntimeError) as caught:
        forebet._browser_get("https://www.forebet.com/scripts/getrs.php")
    assert str(caught.value) == "browser relay HTTP 403"


@pytest.mark.parametrize("authorization", [
    pytest.param("Bearer synthetic-secret", id="bearer"),
    *_AUTHORIZATION_CREDENTIALS,
])
def test_get_reports_each_cloud_path_and_redacts_private_endpoints(
    monkeypatch, authorization,
):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "configured-secret")
    monkeypatch.setenv(public_relay.URLS_ENV, "https://private.example/path-secret")
    monkeypatch.setattr(forebet, "_cloud_fetch_mode", lambda: "relay")
    monkeypatch.setattr(forebet, "_browser_enabled_for_date", lambda _day: True)
    monkeypatch.setattr(forebet, "_playwright_enabled_for_date", lambda _day: True)
    monkeypatch.setattr(forebet, "_browser_get", lambda _url: (_ for _ in ()).throw(
        RuntimeError(f"browser relay HTTP 403; Authorization: {authorization}")))
    monkeypatch.setattr(forebet, "_playwright_get", lambda _url: (_ for _ in ()).throw(
        TimeoutError("page navigation timed out")))
    monkeypatch.setattr(public_relay, "fetches", lambda _url: iter([
        ("https://private.example/path-secret", b"not json"),
    ]))
    monkeypatch.setattr(forebet, "_relay_get", lambda _url: (_ for _ in ()).throw(
        RuntimeError("relay HTTP 403; configured-secret")))
    monkeypatch.setattr(forebet, "_urllib_get", lambda _url: pytest.fail(
        "direct transport must still be skipped on GitHub relay mode"))
    with pytest.raises(RuntimeError) as caught:
        forebet._get("1x2", "2026-10-07")
    text = str(caught.value)
    assert "browser=RuntimeError: browser relay HTTP 403" in text
    assert "playwright=TimeoutError: page navigation timed out" in text
    assert "relay=RuntimeError: relay HTTP 403" in text
    assert "operator:[redacted]=JSONDecodeError: Expecting value" in text
    assert "GitHub direct transport skipped" in text
    for secret in ("configured-secret", "synthetic-", "private.example", "path-secret"):
        assert secret not in text
    assert len(text.splitlines()) == 1


@pytest.mark.parametrize("mode", ["direct", "relay"])
def test_different_failure_causes_are_not_deduplicated(monkeypatch, mode):
    _failure_mode(monkeypatch, mode)

    def fail(market, _day):
        if market == "1x2":
            raise RuntimeError("HTTP 403")
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(forebet, "_get", fail)
    with pytest.raises(RuntimeError) as caught:
        forebet.fetch_day("2026-10-07", sleep=0)
    text = str(caught.value)
    assert "1x2:RuntimeError: HTTP 403" in text
    assert "uo:RuntimeError,bts:RuntimeError: network unavailable" in text
    assert text.count("network unavailable") == 1
