"""Kickoff display normalisation and the per-run offset census (Task 5).

The 2026-10-03 card stored Croatia v England as ``"03-10, 17:00"`` while its
``kickoff_utc`` was ``16:00Z`` (= 18:00 SAST). The hypothesis on the table
was a systematic one-hour UK-local/SAST confusion. Measured against the whole
card it is NOT systematic: the ``DD-MM, HH:MM`` renderings sit -60 minutes
from SAST and the bare ``HH:MM`` renderings sit -420/-540 minutes. So the fix
is a single exact rendering derived from the authoritative instant, plus a
census printed every run - never a blanket offset.
"""
from __future__ import annotations

from edgefactory import notifier
import scripts.picks_today as pt


def _pick(kickoff: str, kickoff_utc: str | None) -> dict:
    return {
        "date": "2026-10-03", "home": "Croatia", "away": "England",
        "kickoff": kickoff, "kickoff_utc": kickoff_utc,
    }


def test_kickoff_sast_is_rendered_from_the_authoritative_instant():
    pick = _pick("03-10, 17:00", "2026-10-03T16:00:00+00:00")
    pt.attach_kickoff_display(pick)
    assert pick["kickoff_sast"] == "2026-10-03 18:00 SAST"
    # The raw feed text is the guard's input and is NEVER rewritten: moving
    # it forward would make the pre-match lead guard err late.
    assert pick["kickoff"] == "03-10, 17:00"


def test_kickoff_sast_is_none_when_the_instant_is_unresolved():
    pick = _pick("11:00", None)
    pt.attach_kickoff_display(pick)
    assert pick["kickoff_sast"] is None


def test_offset_census_reports_per_source_rather_than_systematic():
    picks = [
        # UK-local rendering: -60 minutes from SAST.
        _pick("03-10, 17:00", "2026-10-03T16:00:00+00:00"),
        _pick("03-10, 19:45", "2026-10-03T18:45:00+00:00"),
        # Americas-local rendering: -420 minutes from SAST.
        _pick("09:00", "2026-10-03T14:00:00+00:00"),
        _pick("07:00", "2026-10-03T12:00:00+00:00"),
    ]
    census = pt.kickoff_display_offset_census(picks)
    assert census == {
        "bare_hh:mm": {"-420m": 2},
        "dd-mm_hh:mm": {"-60m": 2},
    }
    lines = pt.kickoff_offset_lines(census)
    assert any("per-source (2 distinct offsets)" in line for line in lines)


def test_offset_census_says_systematic_when_it_really_is():
    picks = [
        _pick("03-10, 17:00", "2026-10-03T16:00:00+00:00"),
        _pick("03-10, 14:00", "2026-10-03T13:00:00+00:00"),
    ]
    lines = pt.kickoff_offset_lines(pt.kickoff_display_offset_census(picks))
    assert any(line.endswith("kickoff_sast is rendered from it") for line in lines)
    assert any("verdict: systematic" in line for line in lines)


def test_the_card_shows_the_normalised_rendering_not_the_feed_string():
    pick = _pick("03-10, 17:00", "2026-10-03T16:00:00+00:00")
    pt.attach_kickoff_display(pick)
    assert notifier.format_kickoff(pick) == "2026-10-03 18:00 SAST"
    assert notifier._tg_short_kickoff(notifier.format_kickoff(pick)) == "18:00"


def test_mixed_feed_formats_collapse_to_one_rendering():
    """"03-10, 17:00" and a bare "11:00" must not coexist on one card."""
    picks = [
        _pick("03-10, 17:00", "2026-10-03T16:00:00+00:00"),
        _pick("11:00", "2026-10-03T16:00:00+00:00"),
    ]
    for pick in picks:
        pt.attach_kickoff_display(pick)
    assert {notifier.format_kickoff(p) for p in picks} == {"2026-10-03 18:00 SAST"}


def test_display_normalisation_never_moves_the_guard_input_later():
    """The lead guard still reads the raw text, so it can only err EARLY."""
    pick = _pick("03-10, 17:00", "2026-10-03T16:00:00+00:00")
    pt.attach_kickoff_display(pick)
    guard_dt = pt.parse_kickoff_dt(pt._kickoff_value(pick), pick["date"])
    true_dt = pt.parse_kickoff_dt(pick["kickoff_utc"], pick["date"])
    assert guard_dt <= true_dt
