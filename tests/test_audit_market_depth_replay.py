"""Comprehensive tests for tools/audit_market_depth_replay.py (Phase 1)."""
from datetime import datetime
from zoneinfo import ZoneInfo
from tools.audit_market_depth_replay import (
    audit_detail_files,
    parse_iso_utc,
    parse_kickoff_instant,
    TZ_UTC
)


def test_parse_iso_utc_behavior():
    # Valid UTC and offsets
    assert parse_iso_utc("2026-10-21T06:30:00Z") == datetime(2026, 10, 21, 6, 30, tzinfo=TZ_UTC)
    assert parse_iso_utc("2026-10-21T08:30:00+02:00") == datetime(2026, 10, 21, 6, 30, tzinfo=TZ_UTC)
    # Naive strings must be rejected as None (fail-closed)
    assert parse_iso_utc("2026-10-21 06:30:00") is None
    # Invalid strings / None
    assert parse_iso_utc("garbage") is None
    assert parse_iso_utc(None) is None
    assert parse_iso_utc(12345) is None


def test_parse_kickoff_instant_behavior():
    # Valid HH:MM string with date
    dt = parse_kickoff_instant("2026-10-21", "18:00")
    assert dt == datetime(2026, 10, 21, 18, 0, tzinfo=TZ_UTC)
    # Malformed strings
    assert parse_kickoff_instant("2026-10-21", "invalid") is None
    assert parse_kickoff_instant("2026-10-21", None) is None


def test_audit_market_depth_timing_and_named_quotes():
    rep = audit_detail_files()
    assert rep["files_count"] == 10
    assert rep["total_fixtures"] == 116
    assert rep["unique_fixture_keys"] == 116

    # Verify timing classifications strictly distinguish pre-cutoff from post-cutoff and post-kickoff
    timing = rep["timing_classification"]
    assert timing["pre_cutoff"] + timing["post_cutoff_pre_kickoff"] + timing["post_kickoff"] == 116
    # 5 fixtures were captured post-kickoff and must be excluded from decision-time replays
    assert timing["post_kickoff"] == 5
    assert timing["pre_cutoff"] == 66

    # Verify named book quotes inspection
    named = rep["named_book_inspection"]
    assert named["total_quotes_checked"] > 5000
    assert named["valid_named_quotes"] > 5000
    assert named["missing_bookmaker"] == 0
    # Exactly 14 quote rows with non-finite / null values detected and accounted for
    assert named["non_finite_odds"] == 14
