"""Adversarial and comprehensive tests for tools/audit_market_depth_replay.py (Phase 1)."""
from datetime import datetime
from zoneinfo import ZoneInfo
from tools.audit_market_depth_replay import (
    audit_detail_files,
    parse_iso_utc,
    parse_kickoff_instant,
    validate_quote_row,
    TZ_UTC
)


def test_parse_iso_utc_adversarial():
    # Valid UTC and offsets
    assert parse_iso_utc("2026-10-21T06:30:00Z") == datetime(2026, 10, 21, 6, 30, tzinfo=TZ_UTC)
    assert parse_iso_utc("2026-10-21T08:30:00+02:00") == datetime(2026, 10, 21, 6, 30, tzinfo=TZ_UTC)
    # Naive strings must be rejected as None (fail-closed)
    assert parse_iso_utc("2026-10-21 06:30:00") is None
    # Invalid strings / malformed / non-string
    assert parse_iso_utc("garbage") is None
    assert parse_iso_utc(None) is None
    assert parse_iso_utc(12345) is None
    assert parse_iso_utc("") is None


def test_parse_kickoff_instant_provenance_and_strict_regex():
    # Full ISO format
    dt, prov = parse_kickoff_instant("2026-10-21", "2026-10-21T18:00:00Z")
    assert dt == datetime(2026, 10, 21, 18, 0, tzinfo=TZ_UTC)
    assert prov == "verified_aware_iso"

    # Bare clock (HH:MM) - must be flagged as unverified_local_clock
    dt, prov = parse_kickoff_instant("2026-10-21", "18:00")
    assert dt == datetime(2026, 10, 21, 18, 0, tzinfo=TZ_UTC)
    assert prov == "unverified_local_clock"

    # Strict regex: partial / garbage clocks like 18:00:garbage must be rejected
    dt, prov = parse_kickoff_instant("2026-10-21", "18:00:garbage")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "99:99")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "invalid")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "")
    assert dt is None and prov == "missing_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", None)
    assert dt is None and prov == "missing_clock"


def test_validate_quote_row_adversarial_including_non_dict():
    # 1. Non-dict row must receive explicit row_not_dict reason
    ok, reason = validate_quote_row("1x2", "not_a_dict")
    assert ok is False and reason == "row_not_dict"

    ok, reason = validate_quote_row("1x2", None)
    assert ok is False and reason == "row_not_dict"

    # 2. Valid 1X2 row
    valid_row = {"bookmaker": "BetMGM", "odds": [1.5, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", valid_row)
    assert ok is True and reason == "valid"

    # 3. Empty odds list must be REJECTED
    empty_row = {"bookmaker": "BetMGM", "odds": []}
    ok, reason = validate_quote_row("1x2", empty_row)
    assert ok is False and reason == "empty_odds_list"

    # 4. Scalar odds (non-list) must be REJECTED, not raise TypeError
    scalar_row = {"bookmaker": "BetMGM", "odds": 1.5}
    ok, reason = validate_quote_row("1x2", scalar_row)
    assert ok is False and reason == "odds_not_list"

    # 5. Incomplete market (width mismatch) must be REJECTED
    incomplete_dc = {"bookmaker": "BetMGM", "odds": [1.15]} # DC requires 3 columns
    ok, reason = validate_quote_row("dc", incomplete_dc)
    assert ok is False and reason.startswith("width_mismatch")

    # 6. Missing / whitespace bookmaker name must be REJECTED
    missing_book = {"bookmaker": "   ", "odds": [1.5, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", missing_book)
    assert ok is False and reason == "missing_bookmaker"

    # 7. Non-finite / string / <= 1 odds must be REJECTED
    nan_row = {"bookmaker": "BetMGM", "odds": [1.5, float("nan"), 5.0]}
    ok, reason = validate_quote_row("1x2", nan_row)
    assert ok is False and reason == "non_finite_odds"

    le1_row = {"bookmaker": "BetMGM", "odds": [1.0, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", le1_row)
    assert ok is False and reason == "odds_le_1"


def test_audit_detail_files_authoritative_vs_diagnostic():
    rep = audit_detail_files()
    assert rep["files_count"] == 10
    assert rep["total_fixtures"] == 116
    assert rep["unique_fixture_keys"] == 116

    # Verify kickoff provenance is explicitly tracked as unverified_local_clock (116)
    assert rep["kickoff_provenance"]["unverified_local_clock"] == 116
    assert rep["kickoff_provenance"]["verified_aware_iso"] == 0

    # CRITICAL: Authoritative eligibility must be fail-closed!
    # Because all 116 stored kickoffs are unverified clocks, ZERO fixtures are authoritatively eligible
    auth = rep["authoritative_eligibility"]
    assert auth["eligible_pre_match_decision"] == 0
    assert auth["unverified_kickoff_timezone"] == 116

    # Diagnostic assumed-UTC counts are strictly preserved as diagnostic only
    diag = rep["diagnostic_assumed_utc_breakdown"]
    assert diag["pre_cutoff_upcoming"] == 57
    assert diag["pre_cutoff_started_before_cutoff"] == 9
    assert diag["post_cutoff_pre_kickoff"] == 45
    assert diag["post_kickoff"] == 5
    assert sum(diag.values()) == 116

    # Fixture objects must NOT expose an unverified clock as authoritative kickoff_utc
    for fix in rep["fixtures"]:
        assert fix["kickoff_utc"] is None
        assert fix["authoritative_eligibility"] == "unverified_kickoff_timezone"

    # Verify capture provenance
    assert rep["capture_provenance"]["fixture_timestamp"] == 116
    assert rep["capture_provenance"]["file_fallback"] == 0

    # Verify quote row inspection
    named = rep["named_book_inspection"]
    assert named["total_quotes_checked"] == 5217
    assert named["valid_named_quotes"] == 5203
    assert named["row_not_dict"] == 0
    assert named["missing_bookmaker"] == 0
    assert named["empty_odds_list"] == 0
    assert named["odds_not_list"] == 0
    assert named["non_finite_odds"] == 14


def test_authoritative_eligibility_synthetic_branches(tmp_path, monkeypatch):
    import json
    from tools import audit_market_depth_replay as amdr

    # Construct synthetic detail payload with aware ISO kickoffs to exercise all authoritative branches
    synthetic_data = {
        "date": "2026-10-21",
        "captured_at": "2026-10-21T06:00:00Z",
        "fixtures": {
            # 1. Eligible: captured 06:00 < cutoff 07:00 < kickoff 12:00
            "fix_eligible": {
                "home": "Team A", "away": "Team B",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T06:00:00Z",
                "markets": {}
            },
            # 2. Ineligible post-cutoff capture: captured 08:00 >= cutoff 07:00, kickoff 12:00
            "fix_post_cutoff": {
                "home": "Team C", "away": "Team D",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T08:00:00Z",
                "markets": {}
            },
            # 3. Exactly at cutoff boundary: captured 07:00 == cutoff 07:00, kickoff 12:00
            "fix_exact_cutoff": {
                "home": "Team E", "away": "Team F",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T07:00:00Z",
                "markets": {}
            },
            # 4. Ineligible already started: kickoff 06:00 <= cutoff 07:00, captured 05:00
            "fix_already_started": {
                "home": "Team G", "away": "Team H",
                "kickoff": "2026-10-21T06:00:00Z",
                "captured_at": "2026-10-21T05:00:00Z",
                "markets": {}
            },
            # 5. Ineligible post kickoff capture: captured 13:00 >= kickoff 12:00
            "fix_post_kickoff": {
                "home": "Team I", "away": "Team J",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T13:00:00Z",
                "markets": {}
            }
        }
    }

    mock_file = tmp_path / "betexplorer_match_detail_2026-10-21.json"
    mock_file.write_text(json.dumps(synthetic_data))
    monkeypatch.setattr(amdr, "LOCALDATA", tmp_path)

    rep = amdr.audit_detail_files()
    auth = rep["authoritative_eligibility"]
    assert auth["eligible_pre_match_decision"] == 1
    assert auth["ineligible_post_cutoff_capture"] == 2  # fix_post_cutoff (08:00) and fix_exact_cutoff (07:00)
    assert auth["ineligible_already_started"] == 1      # fix_already_started
    assert auth["ineligible_post_kickoff_capture"] == 1 # fix_post_kickoff
    assert auth["unverified_kickoff_timezone"] == 0
