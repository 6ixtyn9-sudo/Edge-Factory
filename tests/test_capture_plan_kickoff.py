"""Kickoff-divergence guard tests for capture_theodds.plan_auto."""
import importlib.util
from datetime import datetime
from pathlib import Path

from edgefactory.sources.theoddsapi import (
    _pick_kickoff_utc,
    _pick_kickoff_with_source,
    _team_names_match,
)

_spec = importlib.util.spec_from_file_location(
    "capture_theodds", Path(__file__).resolve().parents[1] / "scripts" / "capture_theodds.py")
capture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(capture)

FIXTURE = {"home": "Halmstad", "away": "Sirius", "kickoff": "03-08, 18:00",
           "date": "2026-08-03"}  # listing: 18:00 SAST -> 16:00Z


def _row(api_kickoff):
    return {"home": "Halmstads BK", "away": "IK Sirius", "market": "1x2",
            "selection": "home", "odds": 1.50, "kickoff": api_kickoff}


def _plan(now_iso, api_kickoff):
    now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
    due, updates, skips = capture.plan_auto(
        [FIXTURE], [_row(api_kickoff)], {}, now=now,
        kickoff_fn=_pick_kickoff_utc, match_fn=_team_names_match)
    return due, updates, skips


def test_warn_emitted_and_close_fires_on_earlier_planning():
    # API says 17:00Z, listing says 16:00Z (60m divergence) -> WARN + window from 16:00Z.
    due, updates, skips = _plan("2026-08-03T15:50:00Z", "2026-08-03T17:00:00Z")
    assert any(s.startswith("WARN kickoff-mismatch") for s in skips)
    assert any("Δ=60m" in s for s in skips)
    assert due and updates.get("Halmstad|Sirius") == "close_at"


def test_api_earlier_protects_against_post_kickoff_capture():
    # API says 15:00Z (TRUE ko), listing claims 16:00Z. At 15:35Z the listing would
    # happily fire inside its fake window; the guard plans from 15:00Z -> started.
    due, updates, skips = _plan("2026-08-03T15:35:00Z", "2026-08-03T15:00:00Z")
    assert any(s.startswith("WARN kickoff-mismatch") for s in skips)
    assert due == []
    assert any("kickoff already passed" in s for s in skips)


def test_small_divergence_does_not_warn():
    # 10-minute divergence is under the 15-minute threshold -> silent, normal planning.
    due, updates, skips = _plan("2026-08-03T15:50:00Z", "2026-08-03T16:10:00Z")
    assert not any("kickoff-mismatch" in s for s in skips)


def test_skip_reason_counts_are_stable_due_gate_receipt_keys():
    counts = capture._skip_reason_counts([
        "WARN kickoff-mismatch A|B: pick lists 16:00Z, captured rows say 17:00Z (Δ=60m; planning from the earlier)",
        "A|B (priced, close window not open)",
        "C|D (retry cooldown (6h after failed attempt))",
        "E|F (kickoff already passed)",
        "G|H (too close to kickoff for first capture)",
        "West Ham (w)|Chelsea (w) (priced)",
        "Chicago Red Stars (w)|Denver Summit Fc (w) (priced)",
    ])
    assert counts == {
        "kickoff_mismatch": 1,
        "priced_close_window_not_open": 1,
        "retry_cooldown": 1,
        "kickoff_already_passed": 1,
        "too_close_for_first_capture": 1,
        "priced": 2,
    }


def test_kickoff_utc_prevents_display_timezone_mismatch_warning():
    fixture = dict(FIXTURE, kickoff="05-10, 19:45",
                   kickoff_utc="2026-10-05T18:45:00+00:00",
                   date="2026-10-05")
    now = datetime.fromisoformat("2026-10-05T18:05:00+00:00")
    due, updates, skips = capture.plan_auto(
        [fixture], [_row("2026-10-05T18:45:00Z")], {}, now=now,
        kickoff_fn=_pick_kickoff_utc, match_fn=_team_names_match)
    assert not any("kickoff-mismatch" in s for s in skips)
    assert due and updates.get("Halmstad|Sirius") == "close_at"


def test_kickoff_utc_mismatch_warning_still_fires_on_row_disagreement():
    fixture = dict(FIXTURE, kickoff="05-10, 19:45",
                   kickoff_utc="2026-10-05T18:45:00+00:00",
                   date="2026-10-05")
    now = datetime.fromisoformat("2026-10-05T18:05:00+00:00")
    due, updates, skips = capture.plan_auto(
        [fixture], [_row("2026-10-05T19:45:00Z")], {}, now=now,
        kickoff_fn=_pick_kickoff_utc, match_fn=_team_names_match)
    assert any(s.startswith("WARN kickoff-mismatch") for s in skips)
    assert any("pick lists 18:45Z" in s and "captured rows say 19:45Z" in s
               and "Δ=60m" in s for s in skips)
    assert due and updates.get("Halmstad|Sirius") == "close_at"


# ---------------------------------------------------------------------------
# Provenance-aware guard (kickoff_source_fn): a real pick_kickoff_utc witness
# and a legacy Africa/Johannesburg display-string assumption must NOT be
# trusted with equal confidence when they disagree with a captured-row UTC
# witness. These tests exercise plan_auto via kickoff_source_fn, which is what
# scripts/capture_theodds.py::main() now passes in production.
# ---------------------------------------------------------------------------

def _plan_with_source(fixture, now_iso, existing_rows):
    now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
    return capture.plan_auto(
        [fixture], existing_rows, {}, now=now,
        kickoff_source_fn=_pick_kickoff_with_source, match_fn=_team_names_match)


def test_provenance_strict_case_still_fail_closed_on_two_real_utc_witnesses():
    """Acceptance test 1: both sides are real UTC witnesses and disagree by
    60m -> WARN fires, planning uses the EARLIER real UTC time, and once past
    that earlier time's start grace the fixture is skipped as already passed.
    This proves provenance-awareness does not weaken the strict/fail-closed
    path when there is no legacy assumption to discount."""
    fixture = dict(FIXTURE, kickoff="05-10, 20:45",
                   kickoff_utc="2026-10-05T18:45:00+00:00", date="2026-10-05")
    # Real kickoff_utc=18:45Z, captured rows say 19:45Z (Δ=60m). now=19:20Z is
    # 35 minutes after the earlier (18:45Z) real witness -> past START_GRACE_MIN.
    due, updates, skips = _plan_with_source(
        fixture, "2026-10-05T19:20:00Z", [_row("2026-10-05T19:45:00Z")])
    assert any(s.startswith("WARN kickoff-mismatch") for s in skips)
    assert any("pick kickoff_utc says 18:45Z" in s and "captured rows say 19:45Z" in s
               and "earlier real UTC witness" in s for s in skips)
    assert due == []
    assert any("kickoff already passed" in s for s in skips)
    # Never captured after a real kickoff: a post-19:20Z fetch must not sneak in.
    assert updates == {}


def test_provenance_overrides_legacy_display_fallback_to_avoid_starvation():
    """Acceptance test 2: pick has no kickoff_utc (legacy display fallback
    parses to 17:45Z); captured rows say 18:45Z (a real UTC witness); Δ=60m.
    At now=18:05Z the OLD (provenance-blind) guard planned from 17:45Z, which
    is past its own close window at that point ('priced, close window not
    open' -- see the companion non-starving evidence in the final report).
    The NEW guard must warn but plan from the captured real UTC witness
    (18:45Z), so the close window (open 45m before kickoff) still fires."""
    fixture = dict(FIXTURE, kickoff="05-10, 19:45", date="2026-10-05")  # no kickoff_utc
    due, updates, skips = _plan_with_source(
        fixture, "2026-10-05T18:05:00Z", [_row("2026-10-05T18:45:00Z")])
    assert any(s.startswith("WARN kickoff-mismatch") for s in skips)
    assert any("pick legacy display says 17:45Z" in s and "captured rows say 18:45Z" in s
               and "display-fallback override" in s for s in skips)
    assert not any("kickoff already passed" in s for s in skips)
    assert due and updates.get("Halmstad|Sirius") == "close_at"


def test_provenance_legacy_only_still_gates_post_kickoff_capture():
    """Acceptance test 3: no captured row at all (nothing to compare against),
    only the legacy display fallback. No mismatch can fire, but the legacy
    kickoff must still gate first-capture before/after its own start grace --
    provenance-awareness must never relax this."""
    fixture = dict(FIXTURE, kickoff="05-10, 19:45", date="2026-10-05")  # legacy fallback -> 17:45Z
    # 50 minutes before 17:45Z: outside the close window and outside START_GRACE_MIN
    # -> still fires an ordinary first capture off the legacy-fallback time.
    due, updates, skips = _plan_with_source(fixture, "2026-10-05T16:55:00Z", [])
    assert due and updates.get("Halmstad|Sirius") == "first_at"
    assert not any("kickoff-mismatch" in s for s in skips)
    # 35 minutes after 17:45Z: past START_GRACE_MIN -> admits no capture at all.
    due2, updates2, skips2 = _plan_with_source(fixture, "2026-10-05T18:20:00Z", [])
    assert due2 == []
    assert updates2 == {}
    assert any("kickoff already passed" in s for s in skips2)


def test_kickoff_mismatch_detail_counts_are_additive_and_specific():
    """New, more specific receipt/log detail (kickoff_mismatch_* sub-reasons)
    must not replace or shrink the existing aggregate kickoff_mismatch bucket
    (see test_skip_reason_counts_are_stable_due_gate_receipt_keys above,
    which is untouched); it is a parallel, additive breakdown.

    Uses real lines produced by plan_auto() (not hand-rolled prose) so this
    test actually exercises the stable `[kickoff_mismatch_detail=...]` tag
    plan_auto emits, rather than re-describing it."""
    strict_fixture = dict(FIXTURE, kickoff="05-10, 20:45",
                           kickoff_utc="2026-10-05T18:45:00+00:00", date="2026-10-05")
    _, _, strict_skips = _plan_with_source(
        strict_fixture, "2026-10-05T18:05:00Z", [_row("2026-10-05T19:45:00Z")])

    override_fixture = dict(FIXTURE, kickoff="05-10, 19:45", date="2026-10-05")
    _, _, override_skips = _plan_with_source(
        override_fixture, "2026-10-05T18:05:00Z", [_row("2026-10-05T18:45:00Z")])

    legacy_only_skips = [
        ("WARN kickoff-mismatch E|F: pick lists 16:00Z, captured rows say 17:00Z "
         "(\u0394=60m; planning from the earlier, legacy-grade provenance only) "
         "[kickoff_mismatch_detail=kickoff_mismatch_legacy_only]"),
    ]

    lines = strict_skips + override_skips + legacy_only_skips
    detail = capture._kickoff_mismatch_detail_counts(lines)
    assert detail == {
        "kickoff_mismatch_planned_from_earlier_utc": 1,
        "kickoff_mismatch_display_fallback_overridden": 1,
        "kickoff_mismatch_legacy_only": 1,
    }
    # The pre-existing aggregate counter still sees all three as one bucket --
    # unchanged, regardless of the new bracketed detail tag riding along.
    aggregate = capture._skip_reason_counts(lines)
    assert aggregate == {"kickoff_mismatch": 3}


def test_kickoff_mismatch_detail_is_none_without_the_machine_tag():
    """If a mismatch WARN line doesn't carry the bracketed detail tag (e.g. the
    pre-fix wording, or any future caller that builds its own WARN text),
    `_kickoff_mismatch_detail` must return None rather than guessing from
    prose -- so detail classification degrades to 'unclassified' instead of
    silently mislabeling an unrelated wording change."""
    old_style_line = ("WARN kickoff-mismatch A|B: pick lists 16:00Z, captured rows say "
                       "17:00Z (\u0394=60m; planning from the earlier)")
    assert capture._kickoff_mismatch_detail(old_style_line) is None
    assert capture._kickoff_mismatch_detail_counts([old_style_line]) == {}
    # ...but the aggregate bucket still counts it, same as always.
    assert capture._skip_reason_counts([old_style_line]) == {"kickoff_mismatch": 1}


def test_provenance_tags_stay_in_sync_across_modules():
    """scripts/capture_theodds.py mirrors edgefactory.sources.theoddsapi's
    provenance string tags BY VALUE (not by import) so --help/--self-test stay
    usable without PYTHONPATH=src (see the comment above PICK_KICKOFF_SOURCE_UTC
    in capture_theodds.py). If these two string constants ever drift apart,
    the provenance-aware override silently stops firing (plan_auto falls back
    to the conservative 'unknown provenance' branch) rather than becoming
    unsafe -- but drift would still quietly defeat the whole point of this
    guard, so pin the two sources of truth together here."""
    from edgefactory.sources import theoddsapi
    assert capture.PICK_KICKOFF_SOURCE_UTC == theoddsapi.PICK_KICKOFF_SOURCE_UTC
    assert capture.PICK_KICKOFF_SOURCE_LEGACY == theoddsapi.PICK_KICKOFF_SOURCE_LEGACY
    assert capture.ROW_KICKOFF_SOURCE_UTC == "captured_row_utc"


def test_provenance_override_applies_regardless_of_which_side_is_earlier():
    """The display-fallback override must unconditionally trust the real
    captured-row UTC witness over a legacy display-string guess -- not just
    when the legacy guess happens to be earlier. Here the legacy fallback
    (18:45Z) is LATER than the real captured-row witness (17:45Z, i.e. the
    real kickoff already happened); the guard must still plan from the real
    witness (17:45Z) and, once its own grace has passed, skip as already
    passed -- it must never trust the legacy guess's later time instead."""
    fixture = dict(FIXTURE, kickoff="05-10, 20:45", date="2026-10-05")  # legacy fallback -> 18:45Z
    due, _updates, skips = _plan_with_source(
        fixture, "2026-10-05T18:20:00Z", [_row("2026-10-05T17:45:00Z")])
    assert any(s.startswith("WARN kickoff-mismatch") for s in skips)
    assert any("display-fallback override" in s for s in skips)
    # now=18:20Z is 35 minutes after the real witness (17:45Z) -> already passed,
    # even though the legacy guess (18:45Z) would still have looked "upcoming".
    assert due == []
    assert any("kickoff already passed" in s for s in skips)


def test_provenance_boundary_exactly_at_threshold_does_not_warn():
    """Delta exactly equal to KICKOFF_MISMATCH_MIN (15m) must NOT warn (the
    guard uses a strict '>' comparison); 1 minute over must warn. Exercised
    through both the real-utc-vs-real-utc and legacy-vs-real-utc branches so
    neither branch accidentally loosens the threshold itself."""
    assert capture.KICKOFF_MISMATCH_MIN == 15

    strict_fixture = dict(FIXTURE, kickoff="05-10, 20:45",
                           kickoff_utc="2026-10-05T18:30:00+00:00", date="2026-10-05")
    _, _, at_threshold = _plan_with_source(
        strict_fixture, "2026-10-05T18:00:00Z", [_row("2026-10-05T18:45:00Z")])
    assert not any("kickoff-mismatch" in s for s in at_threshold)

    strict_fixture_over = dict(FIXTURE, kickoff="05-10, 20:45",
                                kickoff_utc="2026-10-05T18:29:00+00:00", date="2026-10-05")
    _, _, over_threshold = _plan_with_source(
        strict_fixture_over, "2026-10-05T18:00:00Z", [_row("2026-10-05T18:45:00Z")])
    assert any("kickoff-mismatch" in s for s in over_threshold)


def test_row_kickoff_leak_is_never_misclassified_as_a_utc_witness():
    """Audit finding: edgefactory.sources.theoddsapi.rows_from_event_odds()
    writes a row's kickoff as `event.get("commence_time") or pick.get("kickoff")`
    -- if commence_time is ever missing/falsy, the stored row 'kickoff' field
    silently becomes the pick's own raw legacy display string (e.g.
    '03-08, 18:00'), NOT an ISO/Z/offset UTC value. The row-side provenance
    guarantee ('a parsed row kickoff is always a real UTC witness') only holds
    because that non-ISO string fails `datetime.fromisoformat` and is dropped
    (see _fixture_row_kickoff's `except Exception: continue`), so it can never
    be mistaken for ROW_KICKOFF_SOURCE_UTC. Pin that down directly."""
    leaked_row = {"home": "Halmstads BK", "away": "IK Sirius", "market": "1x2",
                  "selection": "home", "odds": 1.50, "kickoff": "03-08, 18:00"}
    row_ko = capture._fixture_row_kickoff(FIXTURE, [leaked_row], _team_names_match)
    assert row_ko is None

    # End-to-end through plan_auto: with only a leaked, unparseable row, no
    # mismatch can be detected (nothing to compare against), so the fixture
    # falls through to ordinary legacy-fallback planning instead of silently
    # treating the leaked string as confirmation of anything.
    now = datetime.fromisoformat("2026-08-03T15:00:00+00:00")
    _due, _updates, skips = capture.plan_auto(
        [FIXTURE], [leaked_row], {}, now=now,
        kickoff_source_fn=_pick_kickoff_with_source, match_fn=_team_names_match)
    assert not any("kickoff-mismatch" in s for s in skips)


def test_provenance_unrecognized_source_tag_falls_back_conservatively():
    """Defensive/future-proofing: if kickoff_source_fn ever returns a string
    that isn't one of the two known tags, plan_auto must not guess -- it falls
    back to the original conservative earlier-of-two behavior, exactly like
    the no-kickoff_source_fn path."""
    def weird_source_fn(f):
        return _pick_kickoff_with_source(f)[0], "some_future_source_nobody_recognizes_yet"

    fixture = dict(FIXTURE, kickoff="05-10, 19:45", date="2026-10-05")  # legacy fallback -> 17:45Z
    now = datetime.fromisoformat("2026-10-05T18:05:00+00:00")
    _due, updates, skips = capture.plan_auto(
        [fixture], [_row("2026-10-05T18:45:00Z")], {}, now=now,
        kickoff_source_fn=weird_source_fn, match_fn=_team_names_match)
    assert any("legacy-grade provenance only" in s for s in skips)
    # Conservative earlier-of-two (17:45Z): at 18:05Z that's 20m past, outside
    # the close window computed from 17:45Z -> not "already passed" yet, but
    # also not re-opened into a close capture by the real witness.
    assert not any(upd == "close_at" for upd in updates.values())
