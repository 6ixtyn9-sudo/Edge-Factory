from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.whatsapp import (
    BUCKET_CAUTION,
    BUCKET_CLEAN,
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
