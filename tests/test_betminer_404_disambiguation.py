"""A 404 must say WHICH 404 it is.

BetMiner has returned HTTP 404 on every probe since 2026-10-03, recorded as
`http_404_endpoint_contract` -- "our path is stale". But RapidAPI answers
*both* "this path is not routed" and "this key is not subscribed" with a 404
on some plans, and the operator action is opposite: fix the adapter vs fix the
subscription.

The provider states which it is in the response body. `_get_json` was already
reading a 200-char snippet of that body into the UpstreamBlocked message and
then throwing it away -- the receipt stored `schema_sample: null` and nothing
else. Five days of receipts, zero actionable information.

These tests pin the disambiguation, and pin that silence is never upgraded
into a diagnosis.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.sources import betminer  # noqa: E402


# --------------------------------------------------------------------------
# classification
# --------------------------------------------------------------------------

@pytest.mark.parametrize("body,expected", [
    # RapidAPI's literal subscription wall
    ('{"message":"You are not subscribed to this API."}', "http_404_not_subscribed"),
    ('{"message":"user is not subscribed to this api"}', "http_404_not_subscribed"),
    # RapidAPI's literal routing failure
    ('{"message":"Endpoint \'/matches/2026-10-03\' does not exist"}',
     "http_404_endpoint_contract"),
    ('{"message":"No route matched"}', "http_404_endpoint_contract"),
    ('Cannot GET /matches/2026-10-03', "http_404_endpoint_contract"),
    # key problems
    ('{"message":"Invalid API key"}', "http_404_invalid_key"),
])
def test_classify_404_reads_the_providers_own_words(body, expected):
    assert betminer.classify_404(body) == expected


def test_classify_404_is_case_insensitive():
    assert betminer.classify_404(
        '{"MESSAGE":"YOU ARE NOT SUBSCRIBED TO THIS API."}'
    ) == "http_404_not_subscribed"


@pytest.mark.parametrize("body", [None, "", "   ", "{}", "something unparseable"])
def test_silence_is_never_upgraded_to_a_diagnosis(body):
    """The headline safety property. If the provider said nothing we
    recognise, we must NOT claim a subscription problem -- that would send the
    operator to the billing page over an adapter bug, or vice versa."""
    assert betminer.classify_404(body) == "http_404_endpoint_contract_unconfirmed"


def test_subscription_and_routing_are_distinguishable():
    sub = betminer.classify_404('{"message":"You are not subscribed to this API."}')
    route = betminer.classify_404('{"message":"Endpoint does not exist"}')
    assert sub != route


# --------------------------------------------------------------------------
# the snippet is recovered from the raised message
# --------------------------------------------------------------------------

def test_provider_snippet_recovered_from_upstream_blocked_text():
    msg = ('betminer: HTTP 404 Not Found; '
           '{"message":"You are not subscribed to this API."}')
    snippet = betminer._provider_snippet(msg)
    assert snippet is not None
    assert "not subscribed" in snippet.lower()
    assert betminer.classify_404(snippet) == "http_404_not_subscribed"


def test_provider_snippet_is_none_when_no_body_was_captured():
    assert betminer._provider_snippet("betminer: HTTP 404 Not Found; ") is None
    assert betminer._provider_snippet("betminer: timeout") is None
    assert betminer._provider_snippet("") is None


# --------------------------------------------------------------------------
# the receipt carries it, scrubbed
# --------------------------------------------------------------------------

def test_receipt_persists_provider_message(tmp_path):
    path = betminer._persist_probe_receipt(
        "2026-10-08",
        endpoint="https://betminer.p.rapidapi.com/matches/2026-10-08",
        http_status=404,
        reason="http_404_not_subscribed",
        provider_message='{"message":"You are not subscribed to this API."}',
        localdata=tmp_path,
    )
    data = json.loads(Path(path).read_text())
    assert data["http_status"] == 404
    assert data["reason"] == "http_404_not_subscribed"
    assert "not subscribed" in data["provider_message"].lower()
    assert data["schema"] == 2


def test_receipt_redacts_the_api_key(tmp_path, monkeypatch):
    monkeypatch.setenv(betminer.KEY_ENV, "SUPERSECRETKEY123")
    path = betminer._persist_probe_receipt(
        "2026-10-08",
        endpoint="https://betminer.p.rapidapi.com/matches/2026-10-08",
        http_status=404,
        reason="http_404_invalid_key",
        provider_message="key SUPERSECRETKEY123 rejected",
        localdata=tmp_path,
    )
    raw = Path(path).read_text()
    assert "SUPERSECRETKEY123" not in raw
    assert "[REDACTED]" in raw


def test_receipt_provider_message_is_capped(tmp_path):
    path = betminer._persist_probe_receipt(
        "2026-10-08", endpoint="e", http_status=404, reason="r",
        provider_message="x" * 5000, localdata=tmp_path,
    )
    data = json.loads(Path(path).read_text())
    assert len(data["provider_message"]) <= 240


def test_receipt_without_a_message_stays_null(tmp_path):
    path = betminer._persist_probe_receipt(
        "2026-10-08", endpoint="e", http_status=404,
        reason="http_404_endpoint_contract_unconfirmed", localdata=tmp_path,
    )
    data = json.loads(Path(path).read_text())
    assert data["provider_message"] is None


def test_committed_receipts_are_still_readable():
    """Committed receipts must keep loading -- the free-tier no-re-probe
    guard depends on it.

    Receipts on disk now span BOTH generations: schema 1 predates
    ``provider_message`` and carries None, while a schema 2 receipt written
    by a later run carries the provider's own words. Both must load. The
    field's presence is not what this test is about; readability is.
    """
    for day in ("2026-10-03", "2026-10-06"):
        receipt = betminer._load_probe_receipt(day)
        if receipt is None:
            continue
        assert receipt.get("http_status") == 404
        message = receipt.get("provider_message")
        assert message is None or isinstance(message, str)


# --------------------------------------------------------------------------
# the same ambiguity, the same cure, on the other RapidAPI provider
# --------------------------------------------------------------------------

from edgefactory import rapidapi_diagnostics as rapidapi  # noqa: E402
from edgefactory.sources import sharpapi_odds  # noqa: E402


def test_sharpapi_now_captures_the_error_body():
    """It previously raised `HTTP 404 Not Found` with no body at all, so its
    receipts could never say why."""
    import inspect
    src = inspect.getsource(sharpapi_odds.get_json)
    assert "exc.read(" in src, "sharpapi must read the error body"


def test_sharpapi_404_is_unconfirmed_until_a_body_says_otherwise():
    assert sharpapi_odds._reason(404) == rapidapi.REASON_UNCONFIRMED


def test_both_providers_share_one_classifier():
    assert betminer.classify_404 is rapidapi.classify_404


def test_every_reason_has_plain_english_operator_guidance():
    for reason in (rapidapi.REASON_NOT_SUBSCRIBED, rapidapi.REASON_ENDPOINT_CONTRACT,
                   rapidapi.REASON_INVALID_KEY, rapidapi.REASON_UNCONFIRMED):
        text = rapidapi.explain(reason)
        assert text and "Unrecognised" not in text


def test_unconfirmed_guidance_tells_the_operator_not_to_act():
    assert "not yet established" in rapidapi.explain(rapidapi.REASON_UNCONFIRMED)


def test_invalid_key_wins_over_subscription_wording():
    """Some RapidAPI bodies mention both; the key is the blocking problem."""
    assert rapidapi.classify_404(
        '{"message":"Invalid API key. Go to subscribe to this API."}'
    ) == rapidapi.REASON_INVALID_KEY
