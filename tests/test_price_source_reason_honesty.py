"""Rejection-reason honesty for vote-only price sources.

`spec()` resolves VOTE_ONLY_SOURCES to a vote-donor spec with
`execution_eligible=False`; `known()` consults REGISTRY only. `auto_tickets`
gated on `known()` *before* `can_execute()`, so a vote donor carrying an odds
column was reported as `price_source_unregistered` — "we have never heard of
this source" — when the truth is "this source is registered and is
deliberately not allowed to price a ticket".

The leg is rejected either way. These tests pin that the *reason* is accurate
and, critically, that no leg became playable as a result.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory import price_sources as psrc  # noqa: E402


def _auto_tickets():
    spec = importlib.util.spec_from_file_location(
        "auto_tickets_reason", ROOT / "scripts" / "auto_tickets.py"
    )
    mod = importlib.util.module_from_spec(spec)
    saved = sys.argv
    sys.argv = ["auto_tickets"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


# --------------------------------------------------------------------------
# registry-level contract
# --------------------------------------------------------------------------

def test_known_and_spec_disagree_on_vote_only_sources():
    """The underlying disagreement this fix is about. Pinned so nobody
    'simplifies' resolvable() back into known()."""
    assert not psrc.known("zulubet")
    assert psrc.spec("zulubet").role == psrc.ROLE_VOTE_DONOR
    assert psrc.spec("zulubet").execution_eligible is False


def test_resolvable_covers_registry_and_vote_only():
    assert psrc.resolvable("theoddsapi")          # REGISTRY
    assert psrc.resolvable("zulubet")             # VOTE_ONLY_SOURCES
    assert psrc.resolvable("statarea")
    assert not psrc.resolvable("some_feed_we_never_heard_of")
    assert not psrc.resolvable(None)
    assert not psrc.resolvable("")


def test_resolvable_never_grants_execution():
    """The whole point: relabelling must not promote anything."""
    for name in sorted(psrc.VOTE_ONLY_SOURCES):
        assert psrc.resolvable(name)
        assert psrc.spec(name).can_execute() is False


def test_known_is_unchanged_for_its_own_callers():
    """known() still means 'is in REGISTRY' — picks_today's donor ranking and
    the shadow ledger depend on that reading."""
    for name in sorted(psrc.VOTE_ONLY_SOURCES):
        assert not psrc.known(name)
    assert psrc.known("forebet_best")  # registered historical fallback


# --------------------------------------------------------------------------
# leg-level contract
# --------------------------------------------------------------------------

def _leg(source, odds=1.50):
    return {
        "date": "2026-10-06", "market": "1x2", "pick": "home",
        "home": "A Team", "away": "B Team", "odds": odds,
        "odds_source": source, "bucket": "CERTIFIED_CLEAN",
        "kickoff": "2026-10-06T23:30:00+00:00",
    }


@pytest.mark.parametrize("source", ["zulubet", "statarea", "vitibet", "betclan"])
def test_vote_donor_leg_reports_not_execution_eligible(source):
    at = _auto_tickets()
    reason = at.playable_leg_rejection(
        _leg(source), day="2026-10-06", execution_safe=True
    )
    assert reason is not None, "a vote donor must never price a ticket"
    assert reason[0] == "price_source_not_execution_eligible"
    assert source in reason[1]


def test_genuinely_unknown_source_still_reports_unregistered():
    at = _auto_tickets()
    reason = at.playable_leg_rejection(
        _leg("totally_made_up_feed"), day="2026-10-06", execution_safe=True
    )
    assert reason is not None
    assert reason[0] == "price_source_unregistered"


def test_missing_source_still_reports_unregistered():
    at = _auto_tickets()
    reason = at.playable_leg_rejection(
        _leg(None), day="2026-10-06", execution_safe=True
    )
    assert reason is not None
    assert reason[0] == "price_source_unregistered"


def test_relabelling_recovers_zero_legs():
    """Load-bearing guard. If this ever fails, the 'diagnostic honesty only'
    claim is void and the change has become a live betting change."""
    at = _auto_tickets()
    for source in sorted(psrc.VOTE_ONLY_SOURCES):
        assert at.playable_leg_rejection(
            _leg(source), day="2026-10-06", execution_safe=True
        ) is not None
