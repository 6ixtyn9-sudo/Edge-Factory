"""Task 6 — credential-blocked sources report an accurate zero-row reason.

Diagnostics only. Nothing here attempts to reach a provider, and no reason
token may contain a key, a header, a URL or any part of a payload: every
token is derived from a status string and an HTTP status code.
"""
from __future__ import annotations

from edgefactory import source_health as sh


def test_auth_rejection_names_the_observed_code():
    assert sh.zero_row_reason("auth", [403], "auth_or_quota") == "http_403_auth"
    assert sh.zero_row_reason("auth", [401], "auth_or_quota") == "http_401_auth"
    # No observed code: say so rather than inventing 403.
    assert sh.zero_row_reason("auth", [], "auth_or_quota") == "credential_rejected_auth"


def test_authenticated_but_empty_is_valid_empty_not_unavailable():
    """pinnapi_odds: status=empty http=200 is a WORKING integration."""
    assert sh.zero_row_reason("empty", [200]) == "valid_empty_http_200"
    # Malformed/unreachable stays a different, non-empty classification.
    assert sh.zero_row_reason("unavailable", [404]) == "http_404_unavailable"
    assert sh.zero_row_reason("quota", [429]) == "http_429_quota"
    assert sh.zero_row_reason("not_run", []) == "credential_absent_not_run"


def test_blocked_status_token_carries_the_reason(tmp_path, monkeypatch):
    monkeypatch.setattr(sh, "LOCALDATA", tmp_path)
    sh.persist_daily_source_health("2026-10-04", {
        "bzzoiro_odds": {
            "status": "auth", "fetched": True, "rows": 0,
            "can_fetch_today": False, "can_price": False, "can_vote": False,
            "reason": sh.zero_row_reason("auth", [403], "auth_or_quota"),
        },
        "pinnapi_odds": {
            "status": "empty", "fetched": True, "rows": 0,
            "pa_raw": 0, "pa_scored": 0, "pa_matched": 0,
            "can_fetch_today": True, "can_price": False, "can_vote": False,
            "reason": sh.zero_row_reason("empty", [200]),
        },
        "betminer": {
            "status": "unavailable", "bm_raw": 0, "bm_scored": 0, "bm_matched": 0,
            "can_fetch_today": False, "can_price": False, "can_vote": False,
            "reason": "http_404_endpoint_contract",
        },
        "sharpapi_odds": {
            "status": "unavailable", "sa_raw": 0, "sa_scored": 0, "sa_matched": 0,
            "can_fetch_today": False, "can_price": False, "can_vote": False,
            "reason": "http_404_endpoint_contract",
        },
    })
    line = sh.daily_status_block("2026-10-04")
    assert "bzzoiro_odds=BLOCKED[reason=http_403_auth]" in line
    assert "pinnapi=pa_raw0/pa_matched0[reason=valid_empty_http_200]" in line
    assert "betminer=bm_raw0/bm_scored0[reason=http_404_endpoint_contract]" in line
    assert "sharpapi=sa_raw0/sa_matched0[reason=http_404_endpoint_contract]" in line


def test_reason_tokens_are_count_and_status_derived_only():
    """A reason can never carry credential material by construction."""
    for status in ("auth", "quota", "empty", "unavailable", "not_run", "cooldown", "ok"):
        reason = sh.zero_row_reason(status, [403, 429, 200], "auth_or_quota")
        if reason is None:
            continue
        assert reason.replace("_", "").isalnum()
        assert "://" not in reason and " " not in reason
