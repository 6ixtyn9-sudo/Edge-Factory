"""Contract tests for the offline research script's leakage/pairing guards.

These pin the machine-checked guarantees the FEATURE-AUDIT relies on; they do
not run the experiment (that needs the full archives and is exercised by the
committed manifest hashes instead).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import research_beyond_consensus as rc  # noqa: E402


def test_forbidden_columns_are_rejected_in_feature_groups():
    # Any future edit that slips an outcome-conditioned column into a feature
    # group must fail here before a run can happen.
    leaked = dict(rc.FEATURE_GROUPS)
    leaked["cheat"] = ["outcome"]
    saved = rc.FEATURE_GROUPS
    try:
        rc.FEATURE_GROUPS = leaked
        with pytest.raises(AssertionError):
            rc._leakage_guards(
                pd.DataFrame({"outcome": ["home"], "lg_draw_rate": [0.25],
                              "lg_home_rate": [0.45]}),
                {"train": pd.DataFrame(), "validation": pd.DataFrame(),
                 "test": pd.DataFrame()})
    finally:
        rc.FEATURE_GROUPS = saved


def test_leakage_guards_reject_fixture_straddling_splits():
    panel = pd.DataFrame({
        "date": ["2025-01-01", "2026-02-01"],
        "key": ["k1", "k1"],  # same fixture in two splits
        "outcome": ["home", "draw"],
        "lg_draw_rate": [0.25, 0.25],
        "lg_home_rate": [0.45, 0.45],
    })
    frames = {
        "train": panel.iloc[[0]],
        "validation": panel.iloc[[1]],
        "test": panel.iloc[[]],
    }
    with pytest.raises(AssertionError):
        rc._leakage_guards(panel, frames)


def test_paired_delta_ci_is_zero_for_identical_predictions():
    rng = np.random.default_rng(7)
    y = np.array(rng.choice(rc.CLASSES, size=400))
    P = rng.dirichlet([2, 1, 1], size=400)
    dates = np.array([f"2026-03-{1 + i // 20:02d}" for i in range(400)])
    out = rc._paired_delta_ci(y, P, y, P.copy(), dates, n_boot=200)
    assert out["delta_mean"] == 0.0
    assert out["ci95"] == [0.0, 0.0]
    assert out["paired_n"] == 400 and out["rows_identical"] is True
    assert out["resample_unit"] == "calendar_day" and out["n_days"] == 20


def test_paired_delta_ci_rejects_misaligned_rows():
    y = np.array(["home", "draw", "away"])
    P = np.full((3, 3), 1 / 3)
    with pytest.raises(AssertionError):
        rc._paired_delta_ci(y, P, y[:2], P[:2], np.array(["2026-03-01"] * 3))


def test_extras_group_is_quarantined_from_the_strict_tier():
    strict_cols = {c for groups in rc.ABLATIONS.values() for c in groups}
    assert "forebet_extras" not in strict_cols
    for groups in rc.ABLATIONS.values():
        assert "forebet_extras" not in groups
    # and the exploratory tier is the only place it may appear
    explor_cols = {c for groups in rc.EXPLORATORY_ABLATIONS.values()
                   for c in groups}
    assert "forebet_extras" in explor_cols
