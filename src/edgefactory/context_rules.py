"""Dormant context-rule vocabulary. No registry or pick-path integration.

All inputs must be timestamped pre-kickoff observations; missing values fail closed.
These predicates alone are not a certification or an activation mechanism.
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
)

_PATTERN = re.compile(
    r"^(%s)\s*(>=|<=)\s*(\d+(?:\.\d+)?)$" % "|".join(re.escape(f) for f in _ALLOWED_FEATURES)
)

# DORMANT rules used by picks_today / auto_tickets wiring — computed, persisted, not applied to stakes
DORMANT_H2H_RULES = (
    "h2h_dominance>=2",
    "h2h_dominance<=-2",
    "rest_days>=30",
    "venue_split>=1",
    "form_gap>=2",
    "h2h_over25_share>=0.6",
    "h2h_btts_share>=0.6",
)


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
