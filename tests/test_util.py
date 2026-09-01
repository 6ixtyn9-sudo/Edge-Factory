"""Unit tests for shared normalization helpers (kickoff_date)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.util import kickoff_date  # noqa: E402


def test_kickoff_date_iso_forms():
    assert kickoff_date("2026-08-23 01:30:00") == "2026-08-23"
    assert kickoff_date("2026-08-02T17:00:00+02:00") == "2026-08-02"
    assert kickoff_date("2026-08-02T19:00:00Z") == "2026-08-02"
    # Date is searched anywhere in the string, matching the legacy archive
    # behaviour (kickoffs occasionally arrive with a prefix/suffix).
    assert kickoff_date("Scheduled 2026-08-23 20:15") == "2026-08-23"


def test_kickoff_date_european_dmy():
    assert kickoff_date("30-08, 16:00", "2026-08-29") == "2026-08-30"
    assert kickoff_date("03.08 18:00", "2026-08-02") == "2026-08-03"
    assert kickoff_date("31/08/2026") == "2026-08-31"
    assert kickoff_date("01-09-26") == "2026-09-01"  # two-digit year -> 20YY


def test_kickoff_date_year_rollover():
    assert kickoff_date("01-01", "2026-12-30") == "2027-01-01"
    assert kickoff_date("31-12", "2026-01-01") == "2025-12-31"


def test_kickoff_date_bare_time_and_junk_return_none():
    # A bare time cannot name a calendar day — callers must fall back to the
    # pick's own date field rather than invent one.
    assert kickoff_date("11:00", "2026-08-29") is None
    assert kickoff_date("11:00") is None
    assert kickoff_date("") is None
    assert kickoff_date(None) is None
    assert kickoff_date("not a date") is None
    assert kickoff_date("32-13") is None  # invalid day/month
