"""Kickoff-divergence guard tests for capture_theodds.plan_auto."""
import importlib.util
from datetime import datetime
from pathlib import Path

from edgefactory.sources.theoddsapi import _pick_kickoff_utc, _pick_kickoff_with_source, _team_names_match

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
    which is untouched); it is a parallel, additive breakdown."""
    lines = [
        "WARN kickoff-mismatch A|B: pick kickoff_utc says 18:45Z, captured rows say "
        "19:45Z (\u0394=60m; planning from the earlier real UTC witness)",
        "WARN kickoff-mismatch C|D: pick legacy display says 17:45Z, captured rows say "
        "18:45Z (\u0394=60m; planning from captured UTC witness, display-fallback override)",
        "WARN kickoff-mismatch E|F: pick lists 16:00Z, captured rows say 17:00Z "
        "(\u0394=60m; planning from the earlier, legacy-grade provenance only)",
    ]
    detail = capture._kickoff_mismatch_detail_counts(lines)
    assert detail == {
        "kickoff_mismatch_planned_from_earlier_utc": 1,
        "kickoff_mismatch_display_fallback_overridden": 1,
        "kickoff_mismatch_legacy_only": 1,
    }
    # And the pre-existing aggregate counter still sees all three as one bucket.
    aggregate = capture._skip_reason_counts(lines)
    assert aggregate == {"kickoff_mismatch": 3}
