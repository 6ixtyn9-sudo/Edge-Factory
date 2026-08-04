from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.whatsapp import (
    BUCKET_CAUTION,
    BUCKET_CLEAN,
    callmebot_body_accepted,
    callmebot_body_category,
    format_whatsapp_summary,
    send_callmebot_whatsapp,
    send_meta_whatsapp_cloud,
    send_twilio_whatsapp,
)


def test_format_whatsapp_summary_empty():
    text = format_whatsapp_summary("2026-06-18", [])
    assert "Edge Factory Official Picks" in text
    assert "No matching certified edges found" in text


def test_format_whatsapp_summary_populated():
    picks = [
        {
            "match": "AC Oulu vs IFK Mariehamn",
            "pick": "1",
            "odds": 1.95,
            "odds_source": "bzzoiro_odds",
            "bookmaker": "Bet365",
            "kickoff": "15:00",
            "avg_p": 71.4,
            "w_score": 0.85,
            "bucket": BUCKET_CLEAN,
            "display_rule": "2WAY-UNANIMOUS≥70",
        },
        {
            "match": "Vaprus vs Flora",
            "pick": "X",
            "odds": 3.40,
            "kickoff": "12:00",
            "avg_p": 66.1,
            "w_score": 0.62,
            "bucket": BUCKET_CAUTION,
            "rule": "3way_unanimous_65",
        },
    ]

    text = format_whatsapp_summary("2026-06-18", picks)
    assert "CERTIFIED CLEAN" in text
    assert "AC Oulu vs IFK Mariehamn" in text
    assert "➡️ *1*" in text
    assert "@1.95 (Bet365)" in text
    assert "71%, w=0.85" in text

    assert "CAUTION" in text
    assert "Vaprus vs Flora" in text
    assert "➡️ *X*" in text
    assert "@3.40" in text


@patch("urllib.request.urlopen")
def test_send_meta_whatsapp_cloud(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"messages": [{"id": "wamid.123"}]}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    res = send_meta_whatsapp_cloud("fake_token", "fake_phone_id", "1234567890", "Hello Edge Factory")
    assert res.get("messages")[0].get("id") == "wamid.123"


@patch("urllib.request.urlopen")
def test_send_twilio_whatsapp(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"sid": "SM123"}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    res = send_twilio_whatsapp("AC123", "AUTH123", "1112223333", "1234567890", "Twilio Alert")
    assert res.get("sid") == "SM123"


@patch("urllib.request.urlopen")
def test_send_callmebot_whatsapp(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"Success"
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    res = send_callmebot_whatsapp("APIKEY123", "1234567890", "CallMeBot Alert")
    assert res == "Success"


# --- Addendum 25.2: provider-ack honesty ---------------------------------------

# Verbatim(ish) 2026-08-04 production ack — diagnostic ping response body.
_PROD_ACK = ("<p>Message to: +27733587019<p>Text to send: Edge Factory diagnostic "
             "2026-08-04 - if this arrives, CallMeBot delivery works."
             "<p><b>Message queued.</b> You will receive it in a few seconds.")


def test_callmebot_ack_classifier_accepts_observed_success_class():
    assert callmebot_body_accepted(_PROD_ACK)
    assert callmebot_body_category(_PROD_ACK) == "accepted"
    assert callmebot_body_accepted("Success")  # legacy fixture class


def test_callmebot_ack_classifier_rejects_error_unknown_empty():
    assert not callmebot_body_accepted("<b>ERROR</b>: invalid apikey")
    assert callmebot_body_category("<b>ERROR</b>: invalid apikey") == "error-class"
    assert not callmebot_body_accepted("") and not callmebot_body_accepted(None)
    assert callmebot_body_category("") == "empty-body"
    assert not callmebot_body_accepted("hmm... ok")
    assert callmebot_body_category("hmm... ok") == "unknown-class"


def test_callmebot_ack_classifier_phrase_trap_never_accepts():
    # an error body containing the accept phrase must still be rejected
    assert not callmebot_body_accepted("ERROR: message not queued for delivery")


# --- Addendum 25.2.1: structural acceptance (regression fixtures from the
# independent review — all four falsely ACCEPTED by the 25.2 classifier,
# reproduced on the deployed 9cecbb6 code before this fix) --------------------

_ECHO_SUCCESS_FAKE = "Text to send: Success\nsomething unrecognised happened"
_ECHO_QUEUED_FAKE = "Text to send: message queued\nsomething unrecognised happened"


def test_ack_echoed_text_is_not_acceptance():
    # the body echoes our outbound text; echo must never count as ack
    for fake in (_ECHO_SUCCESS_FAKE, _ECHO_QUEUED_FAKE):
        assert not callmebot_body_accepted(fake)
        assert callmebot_body_category(fake) == "unknown-class"


def test_ack_success_substring_trap_rejected():
    # 'unsuccessful' contains 'success' — substring matching is not acceptance
    assert not callmebot_body_accepted("We were unsuccessful in queueing your request")


def test_ack_requires_structural_tag():
    assert not callmebot_body_accepted("<i>Message queued.</i> wrong tag")
    assert callmebot_body_accepted("<b>Message queued.</b>")                      # tag alone
    assert callmebot_body_accepted("<B>MESSAGE QUEUED</B>")                        # case-insensitive
    assert callmebot_body_accepted("<b>Message queued</b>")                        # period optional
    # echo coexisting with the real tag is fine — the tag is what counts
    assert callmebot_body_accepted("Text to send: Success <b>Message queued.</b> ok")


@patch("urllib.request.urlopen")
def test_send_callmebot_raises_on_rejected_ack_sanitized(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"<b>ERROR</b>: invalid apikey"
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    with pytest.raises(RuntimeError) as exc_info:
        send_callmebot_whatsapp("SECRETKEY999", "1234567890", "hi")
    msg = str(exc_info.value)
    assert "error-class" in msg
    assert "SECRETKEY999" not in msg and "1234567890" not in msg  # no leaks


@patch("urllib.request.urlopen")
def test_send_callmebot_returns_body_on_accepted_ack(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = _PROD_ACK.encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp
    assert "queued" in send_callmebot_whatsapp("K", "1234567890", "hi").lower()


def test_main_slate_combo_marker_is_state_and_price_honest():
    pick = {
        "match": "Alpha FC vs Beta FC",
        "date": "2026-08-05",
        "pick": "home",
        "bucket": "CAUTION",
        "avg_p": 75.0,
        "odds": 1.9,
        "display_rule": "2way-unanimous avg_p>=70",
        "enhancement_label": "Home Win + Over 2.5",
        "enhancement_probability": 0.51,
        "recommended_enhancement": "match_over_25",
    }
    msg = format_whatsapp_summary("2026-08-05", [pick])
    assert "🔬 *Combo:* Home Win + Over 2.5 (51.0%)" in msg
    assert "🔥 *Combo:*" not in msg
    certified = dict(pick, _enh_status="ELIGIBLE", _enh_priced=True)
    msg = format_whatsapp_summary("2026-08-05", [certified])
    assert "🔥 *Combo:* Home Win + Over 2.5 (51.0%)" in msg
