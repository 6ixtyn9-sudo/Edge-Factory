"""The missing hour: a persistent, exactly-60-minute kickoff disagreement.

WHAT WAS MEASURED
-----------------
Across the 190 committed daily pick files, comparing each pick's own display
text against its own authoritative ``kickoff_utc`` rendered into SAST:

    iso            +0m    n=773   e.g. "2026-09-06T16:00:00+02:00"
    dd-mm_hh:mm   -60m    n=143   e.g. "09-09, 15:00" vs 2026-09-09T14:00:00Z
    bare_hh:mm    -60m    n= 24   e.g. "23:00"        vs 2026-09-09T22:00:00Z

The ``dd-mm, HH:MM`` feed is the persistent one. It is not noise and not a
rounding artefact: it is exactly 60 minutes on every affected row, and it
recurs every single day -

    2026-09-24: 4   2026-10-01: 4   2026-10-02: 6   2026-10-03: 13
    2026-10-04: 15  2026-10-05: 5   2026-10-06: 8     (distinct fixtures)

WHAT IT IS
----------
That feed renders kickoff in UTC+1 while SAST is UTC+2, so its text sits one
hour BEHIND the true local wall clock. The hour is not missing from the
instant - ``kickoff_utc`` is correct - it is missing from the rendering.

WHY IT MATTERS EVEN THOUGH NOTHING IS CURRENTLY WRONG
-----------------------------------------------------
``kickoff_sast`` is derived from ``kickoff_utc``, so the display the operator
reads is right and the discrepancy is invisible. That is the fallback hiding
it. Two things make the silence dangerous:

  * UTC+1 is a ZONE, not a constant. The same feed is UTC+1 under British
    summer time and UTC+0 under GMT, so the gap becomes 120 minutes after the
    October changeover - a drift that would appear with no code change.
  * The raw text is still the pre-match lead guard's input whenever
    ``kickoff_utc`` is absent. A feed BEHIND local time makes the guard read
    kickoff as sooner than it is, which is the safe direction - but only by
    accident of which sites were scraped.

This sits next to settlement, where an hour decides a result.

These tests pin DETECTION, not the offset's value: the census must keep
reporting the disagreement, the authoritative rendering must stay exact, and
the guard must keep erring early. None of them assert that -60m is permanent,
because it is not.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import scripts.picks_today as pt  # noqa: E402

SAST = timezone(timedelta(hours=2))


def _pick(raw_kickoff, utc, **extra):
    pick = {"date": "2026-10-03", "home": "Spain", "away": "Czech Republic",
            "market": "1x2", "pick": "home",
            "kickoff": raw_kickoff, "kickoff_utc": utc}
    pick.update(extra)
    return pick


# A real captured row: the text says 15:00, the instant is 16:00 SAST.
SHIFTED = _pick("09-09, 15:00", "2026-09-09T14:00:00+00:00")
EXACT = _pick("2026-09-06T16:00:00+02:00", "2026-09-06T14:00:00+00:00")


# --- the disagreement is detected, not swallowed --------------------------


def test_census_reports_the_sixty_minute_gap():
    census = pt.kickoff_display_offset_census([SHIFTED])
    assert census == {"dd-mm_hh:mm": {"-60m": 1}}


def test_the_gap_is_exactly_an_hour_not_approximately():
    """A rounding artefact would scatter; this is 60 on every affected row."""
    census = pt.kickoff_display_offset_census([SHIFTED])
    offsets = [o for counts in census.values() for o in counts]
    assert offsets == ["-60m"]


def test_zone_bearing_rows_stay_exact():
    assert pt.kickoff_display_offset_census([EXACT]) == {"iso": {"+0m": 1}}


def test_mixed_feeds_are_reported_as_per_source_not_systematic():
    """Collapsing these into one verdict is how a second, different drift
    would hide behind the first."""
    census = pt.kickoff_display_offset_census([SHIFTED, EXACT])
    lines = pt.kickoff_offset_lines(census)
    verdict = [ln for ln in lines if "verdict" in ln]
    assert verdict and "per-source" in verdict[0]
    assert "systematic" not in verdict[0]


def test_a_drifting_feed_cannot_go_silent():
    """The census must keep speaking when the offset CHANGES. UTC+1 is a zone,
    not a constant: after the October changeover the same feed is two hours
    behind SAST, and that must surface rather than be normalised away."""
    # GMT feed: shows 13:00 while SAST is 15:00.
    winter = _pick("09-11, 13:00", "2026-11-09T13:00:00+00:00")
    census = pt.kickoff_display_offset_census([winter])
    assert census == {"dd-mm_hh:mm": {"-120m": 1}}


def test_both_offsets_of_the_same_feed_are_distinguished():
    census = pt.kickoff_display_offset_census([
        SHIFTED, _pick("09-11, 13:00", "2026-11-09T13:00:00+00:00")])
    assert census["dd-mm_hh:mm"] == {"-120m": 1, "-60m": 1}


# --- the authoritative rendering is unaffected ----------------------------


def test_displayed_hour_does_not_leak_into_the_authoritative_rendering():
    """kickoff_sast comes from kickoff_utc. If it ever started trusting the
    display text instead, every affected fixture would move an hour early."""
    pick = dict(SHIFTED)
    pt.attach_kickoff_display(pick)
    assert pick["kickoff_sast"] == "2026-09-09 16:00 SAST"
    assert "15:00" not in pick["kickoff_sast"]


def test_raw_kickoff_text_is_never_rewritten():
    """It is the guard's input and the audit's provenance. Rewriting it could
    move a kickoff LATER - the one direction the lead guard must not move."""
    pick = dict(SHIFTED)
    pt.attach_kickoff_display(pick)
    assert pick["kickoff"] == "09-09, 15:00"


def test_no_authoritative_instant_yields_no_invented_rendering():
    pick = _pick("09-09, 15:00", "")
    pt.attach_kickoff_display(pick)
    assert pick["kickoff_sast"] is None


def test_naive_instant_is_refused_rather_than_assumed_local():
    """Guessing a zone here is how an hour goes missing in the first place."""
    pick = _pick("09-09, 15:00", "2026-09-09T14:00:00")
    pt.attach_kickoff_display(pick)
    assert pick["kickoff_sast"] is None


# --- rows the census must not silently skip -------------------------------


@pytest.mark.parametrize("raw,utc", [
    ("", "2026-09-09T14:00:00+00:00"),
    ("09-09, 15:00", ""),
    ("no clock here", "2026-09-09T14:00:00+00:00"),
    ("09-09, 15:00", "not-a-timestamp"),
])
def test_unmeasurable_rows_are_omitted_not_counted_as_agreeing(raw, utc):
    """A row that cannot be compared must not be reported as +0m: that would
    manufacture agreement the evidence does not support."""
    census = pt.kickoff_display_offset_census([_pick(raw, utc)])
    assert census == {}


# --- direction of error, if the fallback is ever reached ------------------


def test_a_feed_behind_local_time_makes_the_guard_err_early():
    """With no authoritative instant the raw text is read as local. A feed an
    hour BEHIND makes kickoff look sooner - the safe direction. Pinned so a
    renderer AHEAD of SAST cannot quietly invert it and admit a pick that has
    already kicked off."""
    displayed = pt._kickoff_minutes("09-09, 15:00")
    true_sast = 16 * 60
    assert displayed is not None
    assert displayed < true_sast, "the guard must never read kickoff LATE"
    assert true_sast - displayed == 60
