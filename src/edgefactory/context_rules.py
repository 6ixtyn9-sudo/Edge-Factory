"""Dormant context-rule vocabulary. No registry or pick-path integration.

All inputs must be timestamped pre-kickoff observations; missing values fail closed.
These predicates alone are not a certification or an activation mechanism.
Activation bars and decay thresholds are pre-registered as DATA with basis in receipt.
"""

from __future__ import annotations

import math
import re

# Explicit whitelist — no arbitrary h2h_* widening (test forbids h2h_goals)
_ALLOWED_FEATURES = (
    "h2h_dominance",
    "form_gap",
    "venue_split",
    "rest_days",
    "h2h_draw_share",
    "h2h_over25_share",
    "h2h_btts_share",
    "h2h_clean_sheet_rate",
    "h2h_first_half_draw_share",
    "h2h_first_half_share",
    "h2h_competition_diversity",
    "h2h_same_competition_share",
    "h2h_season_diversity",
    "h2h_same_season_share",
    "h2h_recent_365d_share",
    "h2h_host_minus_visitor",
    "h2h_home_at_home",
    "h2h_away_at_home",
    "h2h_home_at_away",
    "h2h_away_at_away",
    "h2h_home_form",
    "h2h_away_form",
    # Encounter count as real feature (not hidden >=3 gate)
    "h2h_encounter_count",
    # Over thresholds
    "h2h_over05_share",
    "h2h_over15_share",
    "h2h_over35_share",
    "h2h_over05_share_recomputed",
    "h2h_over15_share_recomputed",
    "h2h_over25_share_recomputed",
    "h2h_over35_share_recomputed",
    "h2h_btts_share_recomputed",
    "h2h_clean_sheet_rate_recomputed",
    "h2h_draw_share_recomputed",
    "h2h_total_goals_recomputed",
    "h2h_avg_goals_per_match_recomputed",
    # First-half
    "h2h_first_half_home_win_share",
    "h2h_first_half_away_win_share",
    "h2h_first_half_win_share",
    "h2h_first_half_lost_share",
    # Bookie draw prior
    "h2h_avg_bookie_draw_chance",
    "h2h_bookie_draw_prior",
    "h2h_bookie_home_win_prior",
    "h2h_bookie_away_win_prior",
    # W-D-L recomputed
    "h2h_home_wins_recomputed",
    "h2h_away_wins_recomputed",
)

_PATTERN = re.compile(
    r"^(%s)\s*(>=|<=)\s*(\d+(?:\.\d+)?)$" % "|".join(re.escape(f) for f in _ALLOWED_FEATURES)
)

# DORMANT rules — computed, persisted, not applied to stakes until activation bars clear
# Thresholds here are PREDICATE thresholds, not activation bars. Activation bars below.
DORMANT_H2H_RULES = (
    "h2h_dominance>=2",
    "h2h_dominance<=-2",
    "rest_days>=30",
    "venue_split>=1",
    "form_gap>=2",
    "h2h_over25_share>=0.6",
    "h2h_btts_share>=0.6",
)

# Pre-registered activation bars — per operator ruling 2026-10-10, locked before first evaluation
# ≥200 distinct settled outcomes per predicate, ≥30 capture dates, ≥50 fixtures per holdout window,
# positive net lift lower95>0 after multiplicity, no worsening risk/gate.
ACTIVATION_BARS = {
    "h2h_dominance>=2": {
        "min_observations": 200,
        "min_capture_dates": 30,
        "min_fixtures_per_holdout": 50,
        "min_coverage": 0.5,
        "min_shadow_roi": 0.02,
        "basis": "pre-registered 2026-10-10: ≥200 settled outcomes, ≥30 dates, ≥50 fixtures/holdout, lower95>0 after multiplicity",
    },
    "h2h_dominance<=-2": {
        "min_observations": 200,
        "min_capture_dates": 30,
        "min_fixtures_per_holdout": 50,
        "min_coverage": 0.5,
        "min_shadow_roi": 0.02,
        "basis": "pre-registered 2026-10-10: same as above, symmetric",
    },
    "rest_days>=30": {
        "min_observations": 200,
        "min_capture_dates": 30,
        "min_fixtures_per_holdout": 50,
        "min_coverage": 0.3,
        "min_shadow_roi": 0.01,
        "basis": "pre-registered: rest_days long layoff, needs ≥200 outcomes, lower95>0",
    },
    "venue_split>=1": {
        "min_observations": 200,
        "min_capture_dates": 30,
        "min_fixtures_per_holdout": 50,
        "min_coverage": 0.4,
        "min_shadow_roi": 0.015,
        "basis": "pre-registered: venue_split home advantage, ≥200 outcomes",
    },
    "form_gap>=2": {
        "min_observations": 200,
        "min_capture_dates": 30,
        "min_fixtures_per_holdout": 50,
        "min_coverage": 0.4,
        "min_shadow_roi": 0.02,
        "basis": "pre-registered: form_gap comeback/collapse, ≥200 outcomes",
    },
    "h2h_over25_share>=0.6": {
        "min_observations": 200,
        "min_capture_dates": 30,
        "min_fixtures_per_holdout": 50,
        "min_coverage": 0.5,
        "min_shadow_roi": 0.015,
        "basis": "pre-registered: over25 share, ≥200 outcomes",
    },
    "h2h_btts_share>=0.6": {
        "min_observations": 200,
        "min_capture_dates": 30,
        "min_fixtures_per_holdout": 50,
        "min_coverage": 0.5,
        "min_shadow_roi": 0.015,
        "basis": "pre-registered: btts share, ≥200 outcomes",
    },
}

# Auto-demote decay thresholds — demote only on pre-registered forward decay after sufficient new outcomes
DECAY_THRESHOLDS = {
    "h2h_dominance>=2": {
        "min_new_observations": 100,
        "decay_roi_below": 0.0,
        "decay_coverage_below": 0.3,
        "basis": "pre-registered decay: if new 100 outcomes ROI<0 or coverage<0.3, demote",
    },
    "h2h_dominance<=-2": {
        "min_new_observations": 100,
        "decay_roi_below": 0.0,
        "decay_coverage_below": 0.3,
        "basis": "pre-registered decay: symmetric",
    },
    "rest_days>=30": {
        "min_new_observations": 100,
        "decay_roi_below": -0.01,
        "decay_coverage_below": 0.2,
        "basis": "pre-registered decay: rest_days",
    },
    "venue_split>=1": {
        "min_new_observations": 100,
        "decay_roi_below": 0.0,
        "decay_coverage_below": 0.25,
        "basis": "pre-registered decay: venue_split",
    },
    "form_gap>=2": {
        "min_new_observations": 100,
        "decay_roi_below": 0.0,
        "decay_coverage_below": 0.25,
        "basis": "pre-registered decay: form_gap",
    },
    "h2h_over25_share>=0.6": {
        "min_new_observations": 100,
        "decay_roi_below": 0.0,
        "decay_coverage_below": 0.3,
        "basis": "pre-registered decay: over25",
    },
    "h2h_btts_share>=0.6": {
        "min_new_observations": 100,
        "decay_roi_below": 0.0,
        "decay_coverage_below": 0.3,
        "basis": "pre-registered decay: btts",
    },
}


def parse_predicate(rule: str) -> tuple[str, str, float]:
    match = _PATTERN.fullmatch(rule.strip())
    if not match:
        raise ValueError("unsupported context predicate")
    return match[1], match[2], float(match[3])


def holds(rule: str, features: dict, *, kickoff: str) -> bool:
    """Only an explicitly pre-kickoff, identity-verified feature can qualify."""
    name, op, threshold = parse_predicate(rule)
    if features.get("identity_verified") is not True:
        return False
    stamp = features.get("captured_at")
    if not isinstance(stamp, str) or not stamp or stamp >= kickoff:
        return False
    raw = features.get(name)
    if isinstance(raw, bool):
        return False
    try:
        value = float(raw)
    except (ValueError, TypeError):
        return False
    if not math.isfinite(value):
        return False
    return value >= threshold if op == ">=" else value <= threshold
