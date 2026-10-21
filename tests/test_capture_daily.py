from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "capture_daily.py"
SPEC = importlib.util.spec_from_file_location("capture_daily", SCRIPT)
capture_daily = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(capture_daily)


def test_forebet_resilience_group_expands_to_expected_sources():
    selected = capture_daily.resolve_selected_sources(None, ["forebet-resilience"])

    assert selected == set(capture_daily.FOREBET_RESILIENCE_SOURCES)
    assert "forebet" not in selected
    assert {
        "prosoccer",
        "soccervista",
        "predictz",
        "windrawwin",
        "scoutingstats",
        "vitibet",
        "zulubet",
        "statarea",
        "bettingclosed",
        "freesupertips",
        "betclan",
        "afootballreport",
        "bzzoiro",
        "bzzoiro_odds",
    } == selected


def test_group_and_explicit_sources_are_additive():
    selected = capture_daily.resolve_selected_sources(
        "forebet",
        ["forebet-resilience"],
    )

    assert selected == set(capture_daily.FOREBET_RESILIENCE_SOURCES) | {"forebet"}


def test_unknown_source_and_group_fail_clearly():
    with pytest.raises(ValueError, match="unknown capture source group.*mystery"):
        capture_daily.resolve_selected_sources(None, ["mystery"])

    with pytest.raises(ValueError, match="unknown capture source.*mystery"):
        capture_daily.resolve_selected_sources("mystery", None)


def test_forward_recapture_does_not_refetch_completed_result_donor_day(monkeypatch):
    from types import SimpleNamespace
    calls, resets = [], []
    monkeypatch.setattr(capture_daily.sys, 'argv', [
        'capture_daily.py', '--sources', 'prosoccer', '--skip-build', '--forward-only'])
    def run(cmd, **kwargs):
        calls.append(cmd)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(capture_daily.subprocess, 'run', run)
    monkeypatch.setattr(capture_daily, 'reset_recent_state',
                        lambda source, days: resets.append((source, days)))
    capture_daily.main()
    assert len(calls) == 1
    assert calls[0][2:5] == ['prosoccer', capture_daily.TODAY, capture_daily.TOMORROW]
    assert capture_daily.YESTERDAY not in resets[0][1]
