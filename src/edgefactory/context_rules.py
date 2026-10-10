"""Dormant context-rule vocabulary. No registry or pick-path integration.

All inputs must be timestamped pre-kickoff observations; missing values fail closed.
These predicates alone are not a certification or an activation mechanism.
"""
from __future__ import annotations

import math
import re

_PATTERN = re.compile(r"^(h2h_dominance|form_gap|venue_split|rest_days)\s*(>=|<=)\s*(\d+(?:\.\d+)?)$")


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
