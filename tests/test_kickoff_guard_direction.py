"""The pre-match lead guard may only ever err EARLY (round 2, Task 3).

Measured on the 2026-10-03 card, the zone-free display renderings are:

    statarea  bare "HH:MM"        -> UTC-5  (35 rows), UTC-7 (3 rows)
    zulubet   "DD-MM, HH:MM"      -> UTC+1  (13 rows)
    (zoned ISO rows)              -> exact  (4 rows)

Every one of those sits BEHIND SAST, so reading them as local time made the
guard believe kickoff was sooner than it was — the safe direction, but by
accident of which sites were scraped, not by construction. A renderer ahead
of SAST (say UTC+5) would have made the guard read LATE and admit a pick
that had already kicked off.

These tests use the raw feed strings exactly as captured.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import scripts.picks_today as pt  # noqa: E402

DAY = "2026-10-03"
SAST = timezone(timedelta(hours=2))


def _pick(**overrides) -> dict:
    pick = {"date": DAY, "home": "Spain", "away": "Czech Republic",
            "market": "1x2", "pick": "home"}
    pick.update(overrides)
    return pick


def _eligible(pick, as_of, min_lead=30):
    return pt.operational_pick_eligibility(pick, as_of=as_of, min_lead=min_lead)


# --- the observed renderings, verbatim from localdata/picks_2026-10-03.json --

@pytest.mark.parametrize("raw,kickoff_utc,witness", [
    # statarea bare HH:MM rendered at UTC-5; true kickoff 20:45 SAST
    ("13:45", "2026-10-03T18:45:00+00:00", "scoutingstats"),
    ("09:00", "2026-10-03T14:00:00+00:00", "bzzoiro"),
    ("18:30", "2026-10-03T23:30:00+00:00", "bzzoiro"),
    # statarea bare HH:MM rendered at UTC-7
    ("13:00", "2026-10-03T20:00:00+00:00", "bzzoiro"),
    # zulubet DD-MM, HH:MM rendered at UTC+1; true kickoff 18:00 SAST
    ("03-10, 17:00", "2026-10-03T16:00:00+00:00", "bzzoiro"),
])
def test_observed_renderings_never_make_the_guard_read_late(raw, kickoff_utc, witness):
    """For every real row, the guard's instant is <= the true kickoff."""
    pick = _pick(kickoff=raw, kickoff_utc=kickoff_utc,
                 kickoff_witness=f"{witness} kickoff {kickoff_utc!r}")
    truth = datetime.fromisoformat(kickoff_utc)

    # Sweep the day: the guard must never say "eligible" once we are inside
    # the lead window of the TRUE kickoff.
    probe = truth - timedelta(minutes=29)
    ok, _reason = _eligible(pick, probe)
    assert ok is False, f"{raw!r} admitted a pick 29m before real kickoff"

    ok, _reason = _eligible(pick, truth + timedelta(minutes=1))
    assert ok is False, f"{raw!r} admitted a pick after real kickoff"


@pytest.mark.parametrize("match,raw,kickoff_utc,witness", [
    # Both of these were ADMITTED by the 2026-10-03 15:13 build's lead guard
    # although they had kicked off 12.7 h and 13.2 h earlier. They survived
    # only because the price lane quarantined them (SCOUTINGSTATS_SOLE,
    # push_eligible=False) — the lead guard itself read late.
    ("Boca Juniors vs Union Santa Fe", "17:30",
     "2026-10-03T00:30:00+00:00", "scoutingstats"),
    ("Colombia vs Paraguay", "19:00",
     "2026-10-03T00:00:00+00:00", "bzzoiro"),
])
def test_late_night_americas_fixtures_are_no_longer_admitted_after_kickoff(
        match, raw, kickoff_utc, witness):
    """A bare HH:MM carries no date.

    These fixtures kick off just after midnight UTC, so in the renderer's own
    zone (UTC-5/UTC-7) the clock face belongs to the PREVIOUS day. Re-attaching
    it to the pick's 2026-10-03 date moved kickoff ~15 h later than reality —
    the unsafe direction, and the one case the "every renderer is behind SAST"
    reasoning does not cover.
    """
    pick = _pick(match=match, kickoff=raw, kickoff_utc=kickoff_utc,
                 kickoff_witness=f"{witness} kickoff {kickoff_utc!r}")
    build = datetime(2026, 10, 3, 15, 13, tzinfo=SAST)

    naive = pt.parse_kickoff_dt(raw, DAY).replace(tzinfo=SAST)
    assert (naive - build).total_seconds() > 0, (
        "precondition: the raw reading placed this fixture in the future")

    ok, reason = _eligible(pick, build)
    assert ok is False, f"{match}: admitted ~13 h after kickoff"
    assert reason == "inside_30m_lead_or_started"


def test_a_renderer_ahead_of_sast_cannot_make_the_guard_read_late():
    """The latent defect: display zone AHEAD of SAST.

    Feed text "23:45" from a UTC+5 site for a fixture that truly kicks off
    at 20:45 SAST. Read as local time that is nearly three hours LATE, so
    the naive guard would happily admit an in-play fixture.
    """
    kickoff_utc = "2026-10-03T18:45:00+00:00"  # 20:45 SAST
    truth = datetime.fromisoformat(kickoff_utc)
    pick = _pick(kickoff="23:45", kickoff_utc=kickoff_utc)

    # Ten minutes after the real kickoff.
    as_of = truth + timedelta(minutes=10)

    naive = pt.parse_kickoff_dt("23:45", DAY).replace(tzinfo=SAST)
    assert (naive - as_of).total_seconds() / 60.0 > 30, (
        "precondition: the naive reading alone would have admitted this")

    ok, reason = _eligible(pick, as_of)
    assert ok is False, "guard read a started fixture as pre-match"
    assert reason == "inside_30m_lead_or_started"


def test_the_earlier_of_the_two_readings_always_wins():
    """Monotonicity: adding kickoff_utc can only ever subtract picks."""
    base = datetime(2026, 10, 3, 12, 0, tzinfo=SAST)
    for display, utc in (
        ("13:45", "2026-10-03T18:45:00+00:00"),   # display earlier
        ("23:45", "2026-10-03T18:45:00+00:00"),   # display later
        ("20:45", "2026-10-03T18:45:00+00:00"),   # identical
    ):
        without = _eligible(_pick(kickoff=display), base)[0]
        with_utc = _eligible(_pick(kickoff=display, kickoff_utc=utc), base)[0]
        assert not (with_utc and not without), (
            f"{display!r}: resolving kickoff_utc ADMITTED a pick the raw "
            "reading rejected — the guard moved later")


def test_missing_display_text_stays_a_skip_even_with_a_known_instant():
    """Admitting these would ADD picks; the guard may only subtract."""
    pick = _pick(kickoff=None, kickoff_utc="2026-10-03T18:45:00+00:00")
    ok, reason = _eligible(pick, datetime(2026, 10, 3, 12, 0, tzinfo=SAST))
    assert ok is False
    assert reason == "missing_kickoff_same_day"


def test_an_unresolved_or_malformed_instant_is_ignored_not_trusted():
    base = datetime(2026, 10, 3, 12, 0, tzinfo=SAST)
    for bad in (None, "", "not-a-timestamp", "2026-10-03T18:45:00"):
        pick = _pick(kickoff="20:45", kickoff_utc=bad)
        assert _eligible(pick, base)[0] is True, (
            f"kickoff_utc={bad!r} must fall back to the raw reading")


def test_a_zone_free_instant_is_refused_as_authoritative():
    """kickoff_utc without a zone is not an instant; never compare to it."""
    assert pt._parse_resolved_kickoff_instant(
        {"kickoff_utc": "2026-10-03T18:45:00"}) is None
    assert pt._parse_resolved_kickoff_instant(
        {"kickoff_utc": "2026-10-03T18:45:00Z"}) == datetime(
            2026, 10, 3, 18, 45, tzinfo=timezone.utc)


def test_future_dated_picks_are_untouched_by_the_instant_comparison():
    pick = _pick(date="2026-10-04", kickoff="13:45",
                 kickoff_utc="2026-10-04T18:45:00+00:00")
    ok, reason = _eligible(pick, datetime(2026, 10, 3, 12, 0, tzinfo=SAST))
    assert ok is True and reason is None
