"""Kickoff-divergence guard tests for capture_theodds.plan_auto."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

from edgefactory.sources.theoddsapi import _pick_kickoff_utc, _team_names_match

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
