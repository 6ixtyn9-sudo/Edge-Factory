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
    min_decay_n: int = 15,
    recent_roi: float | None = None,
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
        # Insufficient n → never return HEALTHY, but still allow DEAD and
        # DECAYING when signal is strong enough that one more match wouldn't
        # change the story. Use a lower threshold min_decay_n for these to
        # avoid false positives from tiny samples where Wilson bounds are
        # too wide to be meaningful.
        r_p = recent_wins / recent_n
        if recent_n >= min_decay_n:
            if r_ub < b_lb:
                return DecayReport("DEAD", b_lb, r_lb, r_ub, recent_n)
            if r_p < b_lb and r_lb < 0.90 * b_lb:
                return DecayReport("DECAYING", b_lb, r_lb, r_ub, recent_n)
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

    # Red-Team ROI-Aware Decay Enforcement:
    # An edge cannot be healthy if it has a negative ROI over a meaningful sample.
    if recent_roi is not None and recent_n >= min_recent:
        if recent_roi < -0.03:
            v = "DECAYING"
        elif recent_roi < 0.0:
            if v == "HEALTHY":
                v = "WATCH"

    return DecayReport(v, b_lb, r_lb, r_ub, recent_n)

def should_bench(report: DecayReport, recent_roi: float | None = None) -> bool:
    """Bench an edge if decay says so, or recent ROI has gone materially negative.

    Five benching gates (any one triggers):
      1. DEAD or DECAYING verdict  → structural decay confirmed
      2. n >= 30 AND roi < -5%     → original moderate-ROI bail
      3. n >= 20 AND roi < -10%    → deep-ROI bail (catches n=25-29 blowouts)
      4. WATCH verdict AND n >= 20 AND roi < -5%  →WATCH + moderate negative ROI
      5. n >= 40 AND roi < -3%     → large-sample shallow-ROI bail
    """
    if report.verdict in ("DEAD", "DECAYING"):
        return True
    if recent_roi is not None and report.n_recent >= 30 and recent_roi < -0.05:
        return True
    if recent_roi is not None and report.n_recent >= 20 and recent_roi < -0.10:
        return True
    if recent_roi is not None and report.verdict == "WATCH" and report.n_recent >= 20 and recent_roi < -0.05:
        return True
    if recent_roi is not None and report.n_recent >= 40 and recent_roi < -0.03:
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
    if roi is None:
        return "UNKNOWN"
        
    # Early Veto / Caution / Allow gates for smaller sample size (12 to 39)
    if 12 <= n < 40:
        if roi <= -0.10:
            return "VETO"
        if roi <= -0.04:
            return "CAUTION"
        if roi >= 0.01:
            return "ALLOW"
        return "UNKNOWN"
        
    if n < 12:
        return "UNKNOWN"
        
    # Standard gates for n >= 40
    if roi <= -0.05 and (recent_roi is None or recent_roi <= -0.03):
        return "VETO"
    if roi < 0.0 or (recent_roi is not None and recent_roi <= -0.05):
        return "CAUTION"
    if n >= 100 and roi >= 0.03 and (recent_roi is None or recent_roi >= 0.0):
        return "BOOST"
    return "ALLOW"


def context_verdict_team(n: int, roi: float | None) -> str:
    """Verdict for a team/role/league/market context group.

    n   = total settled bets where this team appeared in this role
    roi = full-history ROI for those bets
    """
    if roi is None:
        return "UNKNOWN"
        
    # Early Veto / Caution / Allow gates for smaller sample size (8 to 24)
    if 8 <= n < 25:
        if roi <= -0.12:
            return "VETO"
        if roi <= -0.05:
            return "CAUTION"
        if roi >= 0.02:
            return "ALLOW"
        return "UNKNOWN"
        
    if n < 8:
        return "UNKNOWN"
        
    # Standard gates for n >= 25
    if roi <= -0.08:
        return "VETO"
    if roi <= -0.03:
        return "CAUTION"
    if n >= 45 and roi >= 0.05:
        return "BOOST"
    return "ALLOW"


def context_verdict_odds_band(n: int, roi: float | None) -> str:
    """Verdict for a sport/market/edge-family/odds-band context group.

    n   = total settled bets in this odds band
    roi = full-history ROI for those bets
    """
    if roi is None:
        return "UNKNOWN"
        
    # Early Veto / Caution / Allow gates for smaller sample size (20 to 59)
    if 20 <= n < 60:
        if roi <= -0.05:
            return "VETO"
        if roi <= -0.01:
            return "CAUTION"
        if roi >= 0.01:
            return "ALLOW"
        return "UNKNOWN"
        
    if n < 20:
        return "UNKNOWN"
        
    # Standard gates for n >= 60
    if roi <= -0.02:
        return "VETO"
    if roi <= 0.0:
        return "CAUTION"
    if n >= 120 and roi >= 0.02:
        return "BOOST"
    return "ALLOW"


def context_verdict_niche(
    n: int,
    roi: float | None,
    *,
    recent_roi: float | None = None,
    hit_rate: float | None = None,
    strict_short_odds: bool = False,
) -> str:
    """Aggressive verdict for narrow niche contexts such as short-odds home favourites.

    Designed to defend sparse but high-impact contexts where waiting for n>=50
    before a veto is too permissive. This is a parallel niche-sensitive layer,
    not a replacement for the generic verdict functions.
    """
    if roi is None or n <= 0:
        return "UNKNOWN"

    early_veto_n = 10 if strict_short_odds else 12
    early_boost_n = 12 if strict_short_odds else 15

    if n >= early_veto_n and roi <= -0.08:
        return "VETO"
    if recent_roi is not None and n >= early_veto_n and recent_roi <= -0.08:
        return "VETO"
    if hit_rate is not None and strict_short_odds and n >= early_veto_n and hit_rate < 0.80:
        return "VETO"

    if n >= 20 and roi <= -0.04 and (recent_roi is None or recent_roi <= -0.02):
        return "VETO"
    if n >= 15 and roi < 0.0:
        return "CAUTION"

    if n >= early_boost_n and roi >= 0.03 and (recent_roi is None or recent_roi >= 0.0):
        return "BOOST"
    if n >= 10 and roi > 0.0:
        return "ALLOW"
    return "UNKNOWN"


def roi(wins: int, n: int, avg_odds: float) -> float:
    """Flat-stake ROI given wins, total bets and average decimal odds."""
    if n <= 0:
        return 0.0
    return (wins * avg_odds - n) / n


# ---- weighted consensus ------------------------------------------------
# Instead of counting heads (N sources agree) we weight each source's vote
# by its Wilson lower bound on the specific market/league combination.
# A source with LB=0.82 gets nearly 3x the vote of one with LB=0.52.
# The winning pick is the one with the highest total weight; the score is
# that sum divided by the total weight across all sources (0–1 scale).
# Disagreement is penalised automatically: if sources split, the winner
# gets only a fraction of the total weight → lower score → fails threshold.

def weighted_consensus_score(
    votes: list[tuple[str, float]],
    *,
    min_lb: float = 0.50,
) -> tuple[str | None, float, bool]:
    """Weighted consensus from a list of (pick, wilson_lb) pairs.

    Parameters
    ----------
    votes     : [(pick, wilson_lb), ...]  — one entry per contributing source.
                wilson_lb should be the source's validated LB on this market.
                Sources with lb < min_lb are excluded (not yet trustworthy).
    min_lb    : floor below which a source's vote is excluded (default 0.50).

    Returns
    -------
    (winning_pick, w_score, is_unanimous)
      winning_pick  – pick with highest weighted vote, or None if no valid votes.
      w_score       – weighted agreement score in [0, 1]; 1.0 = perfect unanimity.
      is_unanimous  – True when all valid-weight sources agree on the same pick.

    Maths
    -----
    weight_i = lb_i  (each source's Wilson LB is its stake in the vote)
    W_total  = sum(weight_i for all valid votes)
    W_pick   = sum(weight_i for votes == winning_pick)
    w_score  = W_pick / W_total

    When all sources agree:  w_score = 1.0
    When sources split 50/50 on equal weights: w_score = 0.5
    """
    if not votes:
        return None, 0.0, False

    # filter below-floor sources
    valid = [(pick, lb) for pick, lb in votes if lb >= min_lb]
    if not valid:
        return None, 0.0, False

    # tally weights per pick
    tally: dict[str, float] = {}
    for pick, lb in valid:
        tally[pick] = tally.get(pick, 0.0) + lb

    total_w = sum(tally.values())
    if total_w <= 0:
        return None, 0.0, False

    winning_pick = max(tally, key=lambda p: tally[p])
    w_score = tally[winning_pick] / total_w
    is_unanimous = len(tally) == 1  # all valid votes cast for same pick

    return winning_pick, round(w_score, 4), is_unanimous
