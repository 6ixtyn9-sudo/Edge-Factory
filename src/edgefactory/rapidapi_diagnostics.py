"""Tell apart the several different failures RapidAPI hides behind HTTP 404.

Why this module exists
----------------------
Two price providers -- ``betminer`` and ``sharpapi_odds`` -- have returned
HTTP 404 on every attempt, both recorded as ``http_404_endpoint_contract``,
i.e. "the path we ask for is not the path the provider publishes".

That label was an assumption, not an observation. RapidAPI's gateway answers
with 404 in at least three unrelated situations:

1. the path is not routed in the API's gateway configuration  -> fix our URL
2. the key is not subscribed *to that particular API*         -> fix billing
3. the key is malformed or missing                            -> fix secrets

The operator action is completely different in each case, and the status code
alone cannot separate them. The response *body* can: RapidAPI states the
reason in plain English. Both adapters were discarding that body, so five days
of probe receipts recorded only "404" and nothing anyone could act on.

A note on (2): subscription is **per API**, not per account. The same
``RAPIDAPI_KEY`` is used by three adapters here, and ``boggio`` succeeds with
it -- so the credential itself is demonstrably valid, and "no key" is not a
candidate explanation for the other two.

Design rule
-----------
Silence is never upgraded into a diagnosis. If the provider did not say
something we recognise, we return the ``_unconfirmed`` variant rather than
guessing, because guessing sends the operator to the wrong place.
"""
from __future__ import annotations

import re

#: RapidAPI's subscription wall.
NOT_SUBSCRIBED_MARKERS = (
    "not subscribed",
    "is not subscribed",
    "subscribe to this api",
)
#: RapidAPI / upstream routing failure.
ENDPOINT_MISSING_MARKERS = (
    "does not exist",
    "endpoint not found",
    "no route matched",
    "cannot get",
    "not found on this server",
)
#: Credential material rejected outright.
INVALID_KEY_MARKERS = (
    "invalid api key",
    "invalid rapidapi key",
    "missing rapidapi",
    "api key is invalid",
)

REASON_NOT_SUBSCRIBED = "http_404_not_subscribed"
REASON_ENDPOINT_CONTRACT = "http_404_endpoint_contract"
REASON_INVALID_KEY = "http_404_invalid_key"
REASON_UNCONFIRMED = "http_404_endpoint_contract_unconfirmed"

#: Reasons an operator can act on immediately, for health-line emphasis.
ACTIONABLE_404_REASONS = frozenset(
    {REASON_NOT_SUBSCRIBED, REASON_ENDPOINT_CONTRACT, REASON_INVALID_KEY}
)


def classify_404(provider_message: str | None) -> str:
    """Map the provider's own words onto a health-line reason token.

    Order matters: a key problem is checked before a subscription problem
    because "invalid key" responses sometimes also mention subscriptions.
    """
    text = str(provider_message or "").strip().lower()
    if not text:
        return REASON_UNCONFIRMED
    if any(marker in text for marker in INVALID_KEY_MARKERS):
        return REASON_INVALID_KEY
    if any(marker in text for marker in NOT_SUBSCRIBED_MARKERS):
        return REASON_NOT_SUBSCRIBED
    if any(marker in text for marker in ENDPOINT_MISSING_MARKERS):
        return REASON_ENDPOINT_CONTRACT
    return REASON_UNCONFIRMED


def provider_snippet(message: str | None) -> str | None:
    """Recover the provider's body from an ``UpstreamBlocked`` message.

    Adapters raise ``"<source>: HTTP <code> <reason>; <body>"``. Returns None
    when no body was captured, so an undiagnosed 404 stays visibly undiagnosed.
    """
    match = re.search(r"HTTP \d{3}[^;]*;\s*(.+)$", str(message or ""), re.S)
    if not match:
        return None
    return match.group(1).strip() or None


def explain(reason: str) -> str:
    """One plain-English line an operator can act on."""
    return {
        REASON_NOT_SUBSCRIBED:
            "The key is valid but this API has no active subscription on the "
            "RapidAPI account. Subscribe to this specific API (subscription is "
            "per API, not per account).",
        REASON_ENDPOINT_CONTRACT:
            "The key is fine; the path we request is not routed by the "
            "provider. Update the adapter's endpoint to a published one.",
        REASON_INVALID_KEY:
            "The credential itself was rejected. Check RAPIDAPI_KEY.",
        REASON_UNCONFIRMED:
            "The provider returned 404 without a recognisable explanation. "
            "Cause not yet established - do not act until a probe captures a "
            "response body.",
    }.get(reason, "Unrecognised reason token.")
