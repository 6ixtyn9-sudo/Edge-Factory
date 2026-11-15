"""bzzoiro_odds 4xx disambiguation: the body explains the 403.

On 2026-11-15 every bzzoiro_odds call failed with HTTP 403 while the
operator's dashboard showed 221/7,500 daily requests used and a healthy
history - the plan was demonstrably not exhausted, and the run receipt could
not say what the 403 actually meant, because ``str(HTTPError)`` is only
"HTTP Error 403: Forbidden" and the adapter discarded the response body.

This pins the repair: the body is retained (scrubbed, capped) in
``diagnostics()['error_bodies']`` and mapped onto an operator-actionable
``auth_reason``. The safety property, same as the RapidAPI disambiguation:
silence is never upgraded to a diagnosis.

All transport is monkeypatched; nothing here touches the network, and no
test may retain the token anywhere in diagnostics.
"""
from __future__ import annotations

import io
import json
import urllib.error

import pytest

from edgefactory.sources import bzzoiro_odds as bz

TEST_TOKEN = "test-token-secret-material"
URL = "https://sports.bzzoiro.com/api/v2/odds/best/"


@pytest.fixture(autouse=True)
def _state(monkeypatch):
    monkeypatch.setattr(bz, "TOKEN", TEST_TOKEN)
    bz._reset_diagnostics()
    yield
    bz._reset_diagnostics()


def _http_error(status: int, body: bytes = b"", content_type: str = "application/json",
                url: str = URL) -> urllib.error.HTTPError:
    headers = {"Content-Type": content_type} if content_type else {}
    return urllib.error.HTTPError(url, status, "reason", headers, io.BytesIO(body))


# --------------------------------------------------------------------------
# classification
# --------------------------------------------------------------------------

@pytest.mark.parametrize("body,expected", [
    # DRF's own words for a rejected credential.
    ('{"detail":"Invalid token."}', "token_rejected"),
    ('{"detail":"Authentication credentials were not provided."}', "token_rejected"),
    # DRF permission wall / plan gating.
    ('{"detail":"You do not have permission to perform this action."}', "plan_gated"),
    ('{"detail":"This feature is not included in your plan."}', "plan_gated"),
    ('{"detail":"Upgrade to access odds comparison."}', "plan_gated"),
    # Throughput/budget rejection.
    ('{"detail":"Request was throttled. Expected available in 1 second."}',
     "rate_limited_or_quota"),
    ('{"detail":"Daily request quota exceeded."}', "rate_limited_or_quota"),
    # Edge/WAF block pages - the fix is egress, not billing.
    ('<html><head><title>Attention Required! | Cloudflare</title></head></html>',
     "edge_waf_blocked"),
    ('<center><h1>Sorry, you have been blocked</h1>Cloudflare Ray ID: abc</center>',
     "edge_waf_blocked"),
])
def test_classify_auth_body_reads_the_providers_own_words(body, expected):
    ctype = "text/html" if body.lstrip().startswith("<") else "application/json"
    assert bz.classify_auth_body(ctype, body) == expected


@pytest.mark.parametrize("content_type,body", [
    (None, None),
    ("application/json", ""),
    ("application/json", "   "),
    ("application/json", '{"error":"something we have never seen"}'),
    ("text/plain", "???"),
])
def test_silence_is_never_upgraded_to_a_diagnosis(content_type, body):
    assert bz.classify_auth_body(content_type, body) == "auth_or_quota_unconfirmed"


def test_edge_markers_win_even_in_json_content_type():
    # A WAF block can arrive mislabelled; the page's own words decide.
    body = "cf-chl-verify: please verify you are human"
    assert bz.classify_auth_body("application/json", body) == "edge_waf_blocked"


# --------------------------------------------------------------------------
# capture into diagnostics
# --------------------------------------------------------------------------

def test_403_body_is_retained_scrubbed_and_classified(monkeypatch):
    body = json.dumps({"detail": f"Invalid token. ({TEST_TOKEN})"}).encode()

    def rejected(request, timeout):
        raise _http_error(403, body)

    monkeypatch.setattr(bz.urllib.request, "urlopen", rejected)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL, retries=1)

    diag = bz.diagnostics()
    assert diag["quota_hint"] == "auth_or_quota"
    assert diag["auth_reason"] == "token_rejected"
    assert diag["error_bodies"] == [
        {"status": 403, "content_type": "application/json",
         "body": f'{{"detail": "Invalid token. ([REDACTED])"}}'}
    ]
    assert TEST_TOKEN not in str(diag)


def test_bodyless_403_stays_unconfirmed_but_is_not_lost(monkeypatch):
    def rejected(request, timeout):
        raise _http_error(403, b"")

    monkeypatch.setattr(bz.urllib.request, "urlopen", rejected)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL, retries=1)

    diag = bz.diagnostics()
    assert diag["auth_reason"] == "auth_or_quota_unconfirmed"
    assert diag["error_bodies"] == []


def test_any_confirmed_reason_upgrades_an_earlier_unconfirmed_one(monkeypatch):
    """Information only accumulates: unconfirmed -> confirmed, never back."""
    def rejected(request, timeout):
        if "second" in request.full_url:
            raise _http_error(403, b'{"detail":"You do not have permission to perform this action."}')
        raise _http_error(403, b"")

    monkeypatch.setattr(bz.urllib.request, "urlopen", rejected)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL, retries=1)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL + "second/", retries=1)
    assert bz.diagnostics()["auth_reason"] == "plan_gated"


def test_a_confirmed_reason_is_never_overwritten(monkeypatch):
    def rejected(request, timeout):
        if "second" in request.full_url:
            raise _http_error(403, b"really odd unrecognized words here")
        raise _http_error(403, b'{"detail":"Invalid token."}')

    monkeypatch.setattr(bz.urllib.request, "urlopen", rejected)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL, retries=1)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL + "second/", retries=1)
    assert bz.diagnostics()["auth_reason"] == "token_rejected"


def test_quota_statuses_keep_their_existing_hint(monkeypatch):
    def rejected(request, timeout):
        raise _http_error(429, b'{"detail":"Request was throttled."}')

    monkeypatch.setattr(bz.urllib.request, "urlopen", rejected)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL, retries=1)

    diag = bz.diagnostics()
    assert diag["quota_hint"] == "rate_limit_or_quota"
    # auth_reason is a 401/403 concept; a 429 must not set it.
    assert diag["auth_reason"] is None
    assert diag["error_bodies"][0]["body"] == '{"detail":"Request was throttled."}'


# --------------------------------------------------------------------------
# end to end through fetch_day
# --------------------------------------------------------------------------

def test_fetch_day_auth_failure_names_the_reason(monkeypatch):
    body = b'{"detail":"You do not have permission to perform this action."}'

    def rejected(request, timeout):
        raise _http_error(403, body, url=request.full_url)

    monkeypatch.setattr(bz.urllib.request, "urlopen", rejected)
    rows = bz.fetch_day("2026-11-15")
    assert rows == []
    diag = bz.diagnostics()
    assert diag["status"] == "auth"
    assert diag["auth_reason"] == "plan_gated"
    assert diag["http_statuses"] == [403]
    assert diag["error_bodies"]
    assert TEST_TOKEN not in str(diag)


def test_diagnostics_returns_copies_of_error_bodies(monkeypatch):
    def rejected(request, timeout):
        raise _http_error(403, b'{"detail":"Invalid token."}')

    monkeypatch.setattr(bz.urllib.request, "urlopen", rejected)
    with pytest.raises(urllib.error.HTTPError):
        bz._get(URL, retries=1)
    out = bz.diagnostics()
    out["error_bodies"].append({"status": 999})
    assert len(bz.diagnostics()["error_bodies"]) == 1
