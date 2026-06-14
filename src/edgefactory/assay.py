"""Assay core: Wilson bounds, grading, decay verdicts.
The non-negotiables:
- Wilson lower bound, never raw hit rate, for any certification decision.
- Walk-forward only. No mini-backtests.
- ROI alongside hit rate, always.
"""

from __future__ import annotations
import math
from dataclasses import dataclass

Z95 = 1.959963984540054

def wilson_bounds(wins: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval (lower, upper) for a binomial proportion."""
    if n <= 0:
        return 0.0, 0.0
    p = wins / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return (centre - spread) / denom, (centre + spread) / denom

def wilson_lb(wins: int, n: int, z: float = Z95) -> float:
    return wilson_bounds(wins, n, z)[0]

def wilson_ub(wins: int, n: int, z: float = Z95) -> float:
    return wilson_bounds(wins, n, z)[1]

# ---- grading -----------------------------------------------------------

GRADES = [
    (0.80, "PLATINUM"),
    (0.70, "GOLD"),
    (0.60, "SILVER"),
    (0.52, "BRONZE"),
    (0.45, "COPPER"),
]

def grade(wins: int, n: int, min_n: int = 30) -> str:
    """Grade a rule by its Wilson lower bound. Small n => UNGRADED, never inflated."""
    if n < min_n:
        return "UNGRADED"
    lb = wilson_lb(wins, n)
    for threshold, name in GRADES:
        if lb >= threshold:
            return name
    return "CHARCOAL"

# ---- decay -------------------------------------------------------------

@dataclass
class DecayReport:
    verdict: str          # HEALTHY | WATCH | DECAYING | DEAD
    baseline_lb: float
    recent_lb: float
    recent_ub: float
    n_recent: int

def decay_verdict(
    baseline_wins: int,
    baseline_n: int,
    recent_wins: int,
    recent_n: int,
    min_recent: int = 30,
) -> DecayReport:
    """Compare recent window against certified baseline.
    DEAD:     recent Wilson UB below baseline LB (recent can't even touch the old floor)
    DECAYING: recent LB below 90% of baseline LB and recent point estimate below baseline LB
    WATCH:    recent point estimate below baseline LB
    HEALTHY:  otherwise (or insufficient recent n -> WATCH, never HEALTHY by default)
    """
    b_lb = wilson_lb(baseline_wins, baseline_n)
    r_lb, r_ub = wilson_bounds(recent_wins, recent_n)

    if recent_n < min_recent:
        return DecayReport("WATCH", b_lb, r_lb, r_ub, recent_n)

    r_p = recent_wins / recent_n
    if r_ub < b_lb:
        v = "DEAD"
    elif r_p < b_lb and r_lb < 0.90 * b_lb:
        v = "DECAYING"
    elif r_p < b_lb:
        v = "WATCH"
    else:
        v = "HEALTHY"

    return DecayReport(v, b_lb, r_lb, r_ub, recent_n)

def should_bench(report: DecayReport, recent_roi: float | None = None) -> bool:
    """Bench an edge if decay says so, or recent ROI has gone materially negative."""
    if report.verdict in ("DEAD", "DECAYING"):
        return True
    if recent_roi is not None and report.n_recent >= 30 and recent_roi < -0.05:
        return True
    return False

# ---- context verdict -------------------------------------------------------
# Two independent layers:
#   Edge health  (decay_verdict):  HEALTHY / WATCH / DECAYING / DEAD
#   Context purity (below):        BOOST / ALLOW / CAUTION / VETO / UNKNOWN
#
# Context verdict answers: "Is this league/team/odds-band safe for this edge?"
# Used by: scripts/assay_purity.py → localdata/purity_registry.json
#          scripts/picks_today.py  → pick bucketing

CONTEXT_VERDICTS = ("BOOST", "ALLOW", "CAUTION", "VETO", "UNKNOWN")


def context_verdict_league(
    n: int,
    roi: float | None,
    recent_roi: float | None = None,
) -> str:
    """Verdict for a league/market/edge-family/selection-role context group.

    n          = total settled bets in this group (full history)
    roi        = full-history ROI (decimal: +0.03 = +3%)
    recent_roi = recent-window ROI (same scale); None if < 30 recent bets
    """
    if n < 80 or roi is None:
        return "UNKNOWN"
    if roi <= -0.05 and (recent_roi is None or recent_roi <= -0.03):
        return "VETO"
    if roi < 0.0 or (recent_roi is not None and recent_roi <= -0.05):
        return "CAUTION"
    if n >= 120 and roi >= 0.03 and (recent_roi is None or recent_roi >= 0.0):
        return "BOOST"
    return "ALLOW"


def context_verdict_team(n: int, roi: float | None) -> str:
    """Verdict for a team/role/league/market context group.

    n   = total settled bets where this team appeared in this role
    roi = full-history ROI for those bets
    """
    if n < 35 or roi is None:
        return "UNKNOWN"
    if roi <= -0.08:
        return "VETO"
    if roi <= -0.03:
        return "CAUTION"
    if n >= 50 and roi >= 0.05:
        return "BOOST"
    return "ALLOW"


def context_verdict_odds_band(n: int, roi: float | None) -> str:
    """Verdict for a sport/market/edge-family/odds-band context group.

    n   = total settled bets in this odds band
    roi = full-history ROI for those bets
    """
    if n < 100 or roi is None:
        return "UNKNOWN"
    if roi <= -0.02:
        return "VETO"
    if roi <= 0.0:
        return "CAUTION"
    if n >= 150 and roi >= 0.02:
        return "BOOST"
    return "ALLOW"

def roi(wins: int, n: int, avg_odds: float) -> float:
    """Flat-stake ROI given wins, total bets and average decimal odds."""
    if n <= 0:
        return 0.0
    return (wins * avg_odds - n) / n
