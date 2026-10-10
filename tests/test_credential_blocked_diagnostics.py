"""Task 6 — credential-blocked sources report an accurate zero-row reason.

Diagnostics only. Nothing here attempts to reach a provider, and no reason
token may contain a key, a header, a URL or any part of a payload: every
token is derived from a status string and an HTTP status code.
"""
from __future__ import annotations

from edgefactory import source_health as sh


def test_auth_rejection_names_the_observed_code():
    # 403 is returned both for a dead credential and for a live one calling
    # an endpoint outside its plan, so the token must not claim "auth".
    assert sh.zero_row_reason("auth", [403], "auth_or_quota") == "http_403_plan_or_auth"
    # 401 is unambiguous and still says so.
    assert sh.zero_row_reason("auth", [401], "auth_or_quota") == "http_401_auth"
    # No observed code: say so rather than inventing 403.
    assert sh.zero_row_reason("auth", [], "auth_or_quota") == "credential_rejected_auth"


def test_authenticated_but_empty_is_distinct_from_unavailable():
    """status=empty http=200 stays its own classification.

    The token now reports the observation (answered, nothing survived
    parsing) rather than asserting the provider genuinely had nothing -- a
    cause this evidence cannot support, and one that was wrong for Pinnacle
    for days while its parser discarded every row.
    """
    assert sh.zero_row_reason("empty", [200]) == "http_200_zero_rows_after_parse"
    # Malformed/unreachable stays a different, non-empty classification.
    assert sh.zero_row_reason("unavailable", [404]) == "http_404_unavailable"
    assert sh.zero_row_reason("quota", [429]) == "http_429_quota"
    # A stage that did not run may only claim "credential absent" when the
    # caller can see the credential is genuinely unconfigured (2026-10-10:
    # a not_run stage was rendered credential_absent_not_run next to a
    # working capture through the same configured token).
    assert sh.zero_row_reason("not_run", []) == "stage_not_run"
    assert sh.zero_row_reason("not_run", [], credential_configured=True) \
        == "stage_not_run_credential_present"
    assert sh.zero_row_reason("not_run", [], credential_configured=False) \
        == "credential_absent_not_run"


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
    assert "bzzoiro_odds=BLOCKED[reason=http_403_plan_or_auth]" in line
    assert "pinnapi=pa_raw0/pa_matched0[reason=http_200_zero_rows_after_parse]" in line
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


# --- labels must state observations, not assert causes (WO-3) ------------


def test_403_does_not_claim_the_credential_is_dead():
    """Bzzoiro's token returned best_results=12 on a sibling call in the same
    run while the comparison endpoint 403'd. Calling that 'auth' sends the
    operator to rotate a key that is already fine."""
    reason = sh.zero_row_reason("auth", [403], "auth_or_quota")
    assert "plan" in reason
    assert reason != "http_403_auth"


def test_401_remains_unambiguously_auth():
    """The widening must not blur the one code that IS unambiguous."""
    assert sh.zero_row_reason("auth", [401]) == sh.REASON_HTTP_401_AUTH


def test_zero_row_200_does_not_claim_the_provider_was_empty():
    reason = sh.zero_row_reason("empty", [200])
    assert reason == sh.REASON_HTTP_200_ZERO_ROWS
    assert "valid" not in reason, "the token must not assert legitimacy"
    assert "zero_rows" in reason


def test_empty_classification_still_differs_from_other_failures():
    """Renaming must not collapse distinct outcomes into one."""
    distinct = {
        sh.zero_row_reason("empty", [200]),
        sh.zero_row_reason("unavailable", [404]),
        sh.zero_row_reason("quota", [429]),
        sh.zero_row_reason("not_run", []),
        sh.zero_row_reason("auth", [401]),
        sh.zero_row_reason("auth", [403]),
    }
    assert len(distinct) == 6


# --- discarded rows are visible where the operator looks ------------------


def _health(tmp_path, monkeypatch, sources):
    monkeypatch.setattr(sh, "LOCALDATA", tmp_path)
    sh.persist_daily_source_health("2026-10-07", sources)
    return sh.daily_status_block("2026-10-07")


def test_discarded_rows_appear_on_the_health_line(tmp_path, monkeypatch):
    """A source that fetched plenty and kept none is a parser fault, not a
    quiet slate. The bare zero could not tell those apart."""
    line = _health(tmp_path, monkeypatch, {"pinnapi_odds": {
        "status": "ok", "fetched": True, "rows": 0,
        "pa_raw": 40, "pa_scored": 0, "pa_matched": 0,
        "canonicalization_dropped": 40,
        "can_fetch_today": True, "can_price": False, "can_vote": False,
    }})
    assert "dropped40" in line


def test_no_discard_token_when_nothing_was_dropped(tmp_path, monkeypatch):
    line = _health(tmp_path, monkeypatch, {"pinnapi_odds": {
        "status": "ok", "fetched": True, "rows": 3,
        "pa_raw": 3, "pa_scored": 3, "pa_matched": 3,
        "canonicalization_dropped": 0,
        "can_fetch_today": True, "can_price": True, "can_vote": False,
    }})
    assert "dropped" not in line


def test_oddspapi_carries_a_reason_token(tmp_path, monkeypatch):
    """It printed a bare raw0 through four days of hard 429s, which is why
    nobody looked at it."""
    line = _health(tmp_path, monkeypatch, {"oddspapi_odds": {
        "status": "quota", "fetched": True, "rows": 0,
        "op_raw": 0, "op_usable": 0, "op_matched": 0,
        "reason": sh.zero_row_reason("quota", [429]),
        "can_fetch_today": False, "can_price": False, "can_vote": False,
    }})
    assert "oddspapi=" in line
    assert "reason=http_429_quota" in line
