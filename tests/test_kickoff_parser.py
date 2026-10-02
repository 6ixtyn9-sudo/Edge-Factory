"""Regression tests for the kickoff parser day/month repair (2026-10-02).

`picks_today.parse_kickoff_dt` read naive ``"DD-MM, HH:MM"`` feed values as
MM-DD. The feeds publish day first: zulubet renders ``2024-07-24`` as
``"24-07, 14:00"``. Consequences before the fix, each now pinned below:

- day > 12 (e.g. the 30th): ``datetime(year, 30, ...)`` raised -> ``None``
  -> ``operational_pick_eligibility`` rejected the pick as
  ``missing_kickoff_same_day`` (the 2026-09-30 funnel's eight phantom
  same-day kickoff gaps);
- day <= 12 with the swapped month *behind* the run month (``"02-10,
  18:00"`` on 2 Oct -> February): the lead is months negative and the pick
  is wrongly rejected as ``inside_30m_lead_or_started`` — silent same-day
  coverage loss;
- day <= 12 with the swapped month *ahead* of the run month (``"12-06,
  07:00"`` on 12 Jun -> December): the lead reads months ahead, so the
  pre-match guard could not fire and an **already-started fixture stayed
  playable** — a live safety hole;
- bare ``"HH:MM"`` values were stamped with the wall-clock date rather
  than the fixture's own date;
- the year came from the wall clock, so a 31 December run read a
  1 January fixture as the *previous* January.

The repair (ported from the canonical fix proven on the unmerged PR #18
branch): day-first unpacking, the fixture's own date as the calendar
reference, and year-boundary rollover. The zoned ``kickoff_utc``
normalisation path was never affected and is out of scope here.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from picks_today import (  # noqa: E402
    operational_pick_eligibility,
    parse_kickoff_dt,
)

SAST = ZoneInfo("Africa/Johannesburg")
MIN_LEAD = 30


def _pick(day: str, kickoff: str | None) -> dict:
    row = {"date": day, "home": "Alpha", "away": "Beta"}
    if kickoff is not None:
        row["kickoff"] = kickoff
    return row


# --- direct parsing: the field order is DD-MM, matching the feeds ---------


def test_dd_mm_parses_day_first() -> None:
    dt = parse_kickoff_dt("24-07, 14:00", "2026-07-24")
    assert dt is not None and (dt.year, dt.month, dt.day, dt.hour, dt.minute) == (
        2026,
        7,
        24,
        14,
        0,
    )


def test_dd_mm_after_the_12th_parses_instead_of_dropping() -> None:
    # "30-09, 08:10" used to return None (datetime(year, 30, 9) is invalid),
    # which the eligibility guard reported as a missing kickoff.
    dt = parse_kickoff_dt("30-09, 08:10", "2026-09-30")
    assert dt is not None
    assert (dt.month, dt.day) == (9, 30)


@pytest.mark.parametrize("day", list(range(13, 32)))
def test_every_day_after_the_12th_parses(day: int) -> None:
    dt = parse_kickoff_dt(f"{day:02d}-10, 19:45", f"2026-10-{min(day, 28):02d}")
    assert dt is not None, f"day {day} must parse"
    assert (dt.month, dt.day) == (10, day)


def test_dd_mm_early_month_is_not_swapped_into_january() -> None:
    # "01-10, 06:10" used to become 10 January — nine months out.
    dt = parse_kickoff_dt("01-10, 06:10", "2026-10-01")
    assert dt is not None
    assert (dt.month, dt.day) == (10, 1)


# --- the eligibility guard: coverage restored, safety restored ------------


def test_same_day_upcoming_fixture_is_kept() -> None:
    # 18:00 kickoff, judged at 09:00 the same day: 9h ahead, must be kept.
    # Before the fix this parsed to February and was rejected as
    # "inside_30m_lead_or_started".
    as_of = datetime(2026, 10, 2, 9, 0, tzinfo=SAST)
    ok, reason = operational_pick_eligibility(
        _pick("2026-10-02", "02-10, 18:00"), as_of=as_of, min_lead=MIN_LEAD
    )
    assert (ok, reason) == (True, None)


def test_started_fixture_is_rejected() -> None:
    # 09:00 kickoff judged at noon the same day: already started. Before the
    # fix (when the swapped month landed ahead of the run month) the lead
    # read as ~30 days and the guard could not fire.
    as_of = datetime(2026, 10, 11, 12, 0, tzinfo=SAST)
    ok, reason = operational_pick_eligibility(
        _pick("2026-10-11", "11-10, 09:00"), as_of=as_of, min_lead=MIN_LEAD
    )
    assert (ok, reason) == (False, f"inside_{MIN_LEAD}m_lead_or_started")


def test_inside_lead_window_is_rejected() -> None:
    as_of = datetime(2026, 10, 2, 17, 45, tzinfo=SAST)
    ok, reason = operational_pick_eligibility(
        _pick("2026-10-02", "02-10, 18:00"), as_of=as_of, min_lead=MIN_LEAD
    )
    assert (ok, reason) == (False, f"inside_{MIN_LEAD}m_lead_or_started")


def test_missing_kickoff_still_fails_closed() -> None:
    as_of = datetime(2026, 10, 2, 9, 0, tzinfo=SAST)
    ok, reason = operational_pick_eligibility(
        _pick("2026-10-02", None), as_of=as_of, min_lead=MIN_LEAD
    )
    assert (ok, reason) == (False, "missing_kickoff_same_day")


def test_future_dated_pick_is_not_kickoff_gated() -> None:
    as_of = datetime(2026, 10, 2, 9, 0, tzinfo=SAST)
    ok, reason = operational_pick_eligibility(
        _pick("2026-10-05", None), as_of=as_of, min_lead=MIN_LEAD
    )
    assert (ok, reason) == (True, None)


# --- calendar reference comes from the fixture, not the wall clock --------


def test_bare_time_uses_the_fixture_date() -> None:
    dt = parse_kickoff_dt("14:30", "2026-12-05")
    assert dt is not None
    assert (dt.year, dt.month, dt.day) == (2026, 12, 5)


def test_bare_time_without_reference_falls_back_to_today() -> None:
    dt = parse_kickoff_dt("14:30")
    assert dt is not None
    assert dt.date() == datetime.now(SAST).date()


def test_december_run_rolls_a_january_fixture_forward() -> None:
    # Used to land on the *previous* January.
    dt = parse_kickoff_dt("01-01, 18:00", "2026-12-31")
    assert dt is not None
    assert (dt.year, dt.month, dt.day) == (2027, 1, 1)


def test_january_run_reads_a_december_fixture_back() -> None:
    dt = parse_kickoff_dt("30-12, 20:00", "2026-01-02")
    assert dt is not None
    assert (dt.year, dt.month, dt.day) == (2025, 12, 30)


def test_reference_date_accepts_date_objects_and_datetimes() -> None:
    a = parse_kickoff_dt("05-11, 12:00", date(2026, 11, 5))
    b = parse_kickoff_dt("05-11, 12:00", datetime(2026, 1, 1, 8, 0))
    assert a is not None and (a.year, a.month, a.day) == (2026, 11, 5)
    assert b is not None and b.year == 2026


def test_no_reference_uses_current_year_day_first() -> None:
    dt = parse_kickoff_dt("05-11, 12:00")
    now = datetime.now(SAST)
    assert dt is not None
    assert (dt.year, dt.month, dt.day) == (now.year, 11, 5)


# --- untouched behaviours ---------------------------------------------------


def test_iso_with_offset_is_unchanged() -> None:
    dt = parse_kickoff_dt("2026-08-08T21:00:00+02:00")
    assert dt is not None and (dt.month, dt.day, dt.hour) == (8, 8, 21)


def test_zulu_is_converted_to_sast() -> None:
    dt = parse_kickoff_dt("2026-08-08T19:00:00Z")
    assert dt is not None
    assert dt.hour == 21 and (dt.utcoffset() == timedelta(hours=2))


@pytest.mark.parametrize(
    "value",
    ["", None, "not a kickoff", "32-10, 12:00", "10-13, 12:00", "05-10, 25:00"],
)
def test_invalid_values_return_none(value: object) -> None:
    assert parse_kickoff_dt(value, "2026-10-02") is None
