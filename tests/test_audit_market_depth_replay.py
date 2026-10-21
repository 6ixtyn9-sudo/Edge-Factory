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


def test_parse_kickoff_instant_provenance():
    # Full ISO format
    dt, prov = parse_kickoff_instant("2026-10-21", "2026-10-21T18:00:00Z")
    assert dt == datetime(2026, 10, 21, 18, 0, tzinfo=TZ_UTC)
    assert prov == "verified_aware_iso"

    # Bare clock (HH:MM) - must be flagged as unverified_local_clock
    dt, prov = parse_kickoff_instant("2026-10-21", "18:00")
    assert dt == datetime(2026, 10, 21, 18, 0, tzinfo=TZ_UTC)
    assert prov == "unverified_local_clock"

    # Malformed clocks
    dt, prov = parse_kickoff_instant("2026-10-21", "99:99")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "invalid")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "")
    assert dt is None and prov == "missing_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", None)
    assert dt is None and prov == "missing_clock"


def test_validate_quote_row_adversarial():
    # 1. Valid 1X2 row
    valid_row = {"bookmaker": "BetMGM", "odds": [1.5, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", valid_row)
    assert ok is True and reason == "valid"

    # 2. Empty odds list must be REJECTED
    empty_row = {"bookmaker": "BetMGM", "odds": []}
    ok, reason = validate_quote_row("1x2", empty_row)
    assert ok is False and reason == "empty_odds_list"

    # 3. Scalar odds (non-list) must be REJECTED, not raise TypeError
    scalar_row = {"bookmaker": "BetMGM", "odds": 1.5}
    ok, reason = validate_quote_row("1x2", scalar_row)
    assert ok is False and reason == "odds_not_list"

    # 4. Incomplete market (width mismatch) must be REJECTED
    incomplete_dc = {"bookmaker": "BetMGM", "odds": [1.15]} # DC requires 3 columns
    ok, reason = validate_quote_row("dc", incomplete_dc)
    assert ok is False and reason.startswith("width_mismatch")

    # 5. Missing / whitespace bookmaker name must be REJECTED
    missing_book = {"bookmaker": "   ", "odds": [1.5, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", missing_book)
    assert ok is False and reason == "missing_bookmaker"

    # 6. Non-finite / string / <= 1 odds must be REJECTED
    nan_row = {"bookmaker": "BetMGM", "odds": [1.5, float("nan"), 5.0]}
    ok, reason = validate_quote_row("1x2", nan_row)
    assert ok is False and reason == "non_finite_odds"

    le1_row = {"bookmaker": "BetMGM", "odds": [1.0, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", le1_row)
    assert ok is False and reason == "odds_le_1"


def test_audit_detail_files_reconciliation():
    rep = audit_detail_files()
    assert rep["files_count"] == 10
    assert rep["total_fixtures"] == 116
    assert rep["unique_fixture_keys"] == 116

    # Verify kickoff provenance is explicitly tracked as unverified_local_clock (116)
    assert rep["kickoff_provenance"]["unverified_local_clock"] == 116
    assert rep["kickoff_provenance"]["verified_aware_iso"] == 0

    # Verify timing distinctions:
    # 57 pre_cutoff_upcoming (true decision candidates)
    # 9 pre_cutoff_started_before_cutoff (kickoff <= 07:00 UTC)
    # 45 post_cutoff_pre_kickoff
    # 5 post_kickoff
    timing = rep["timing_classification"]
    assert timing["pre_cutoff_upcoming"] == 57
    assert timing["pre_cutoff_started_before_cutoff"] == 9
    assert timing["post_cutoff_pre_kickoff"] == 45
    assert timing["post_kickoff"] == 5
    assert sum(timing.values()) == 116

    # Verify capture provenance
    assert rep["capture_provenance"]["fixture_timestamp"] == 116
    assert rep["capture_provenance"]["file_fallback"] == 0

    # Verify quote row inspection
    named = rep["named_book_inspection"]
    assert named["total_quotes_checked"] == 5217
    assert named["valid_named_quotes"] == 5203
    assert named["missing_bookmaker"] == 0
    assert named["empty_odds_list"] == 0
    assert named["odds_not_list"] == 0
    assert named["non_finite_odds"] == 14
