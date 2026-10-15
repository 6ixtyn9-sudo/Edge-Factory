"""Tests for the per-step timing helper (observability only)."""

from __future__ import annotations

import pytest

from edgefactory import step_timing


@pytest.fixture(autouse=True)
def _clean_totals():
    step_timing._TOTALS.clear()
    yield
    step_timing._TOTALS.clear()


def test_timed_step_records_ok_and_prints(capsys):
    with step_timing.timed_step("unit: ok block"):
        pass
    out = capsys.readouterr().out
    assert "STEP_TIMING label=unit: ok block status=ok seconds=" in out
    calls, total = step_timing._TOTALS["unit: ok block"]
    assert calls == 1 and total >= 0.0


def test_timed_step_records_error_and_reraises(capsys):
    with pytest.raises(ValueError, match="boom"):
        with step_timing.timed_step("unit: failing block"):
            raise ValueError("boom")
    out = capsys.readouterr().out
    assert "label=unit: failing block status=error" in out
    assert step_timing._TOTALS["unit: failing block"][0] == 1


def test_decorator_returns_value_and_defaults_to_qualname(capsys):
    @step_timing.timed()
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    assert add.__name__ == "add"
    label = next(iter(step_timing._TOTALS))
    assert label.endswith("add")
    assert step_timing._TOTALS[label][0] == 1


def test_decorator_propagates_exceptions():
    @step_timing.timed("unit: decorated failure")
    def explode():
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError, match="nope"):
        explode()
    assert step_timing._TOTALS["unit: decorated failure"][0] == 1


def test_labels_are_clipped_and_whitespace_collapsed():
    long_label = "run:   " + ("x" * 400)
    with step_timing.timed_step(long_label):
        pass
    (label,) = step_timing._TOTALS.keys()
    assert len(label) <= step_timing._LABEL_MAX
    assert "  " not in label


def test_summary_prints_ranked_totals(capsys):
    step_timing._TOTALS["slow"] = [2.0, 90.0]
    step_timing._TOTALS["fast"] = [5.0, 1.0]
    step_timing.print_summary()
    lines = [l for l in capsys.readouterr().out.splitlines() if "STEP_TIMING_SUMMARY label=" in l]
    assert lines[0].split("label=")[1].startswith("slow")
    assert "calls=2 total_seconds=90.0" in lines[0]


def test_summary_is_silent_when_nothing_timed(capsys):
    step_timing.print_summary()
    assert capsys.readouterr().out == ""
