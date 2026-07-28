"""The math must never silently break. Run: pytest"""
from edgefactory.assay import (wilson_lb, wilson_ub, grade,
                               decay_verdict, should_bench, roi,
                               context_verdict_league, context_verdict_team,
                               context_verdict_odds_band, context_verdict_niche,
                               weighted_consensus_score)

def test_wilson_basics():
    assert wilson_lb(0, 0) == 0.0
    # 9/10 looks great but small n gets punished
    assert wilson_lb(9, 10) < 0.75
    # 900/1000 barely punished
    assert wilson_lb(900, 1000) > 0.87
    # monotone in n at same rate
    assert wilson_lb(90, 100) < wilson_lb(900, 1000)

def test_grades():
    assert grade(90, 100) == "PLATINUM"
    assert grade(75, 100) == "SILVER"
    assert grade(30, 100) == "CHARCOAL"

def test_roi():
    # wins=2, n=3, avg_odds=2.0 => ROI = (4.0 - 3) / 3 = 1/3 = 0.333
    assert abs(roi(2, 3, 2.0) - 0.33333333) < 1e-6
    assert roi(0, 0, 2.0) == 0.0

def test_decay_verdicts():
    # baseline: 80/100 (LB ~0.71)
    # recent: 5/5 -> WATCH (n < 30)
    rep = decay_verdict(80, 100, 5, 5)
    assert rep.verdict == "WATCH"

    # recent: 30/30 (LB ~0.89) -> HEALTHY
    rep2 = decay_verdict(80, 100, 30, 30)
    assert rep2.verdict == "HEALTHY"

    # recent: 20/100 (UB ~0.29 < 0.71) -> DEAD
    rep3 = decay_verdict(80, 100, 20, 100)
    assert rep3.verdict == "DEAD"

def test_should_bench():
    # DEAD -> True
    rep_dead = decay_verdict(80, 100, 20, 100)
    assert should_bench(rep_dead)

    # HEALTHY -> False
    rep_healthy = decay_verdict(80, 100, 80, 100)
    assert not should_bench(rep_healthy)

    # HEALTHY but ROI < -0.05 -> True
    assert should_bench(rep_healthy, recent_roi=-0.06)


def test_context_verdicts():
    # ---- league ----
    # n < 12 -> UNKNOWN regardless of ROI
    assert context_verdict_league(10, 0.05) == "UNKNOWN"
    # roi=None -> UNKNOWN
    assert context_verdict_league(100, None) == "UNKNOWN"
    # roi <= -0.05 AND recent_roi <= -0.03 -> VETO
    assert context_verdict_league(100, -0.06, recent_roi=-0.04) == "VETO"
    # roi <= -0.05 but recent_roi None -> VETO (recent unknown = treat as bad)
    assert context_verdict_league(100, -0.06, recent_roi=None) == "VETO"
    # roi < 0 -> CAUTION
    assert context_verdict_league(100, -0.02) == "CAUTION"
    # recent_roi <= -0.05 -> CAUTION even if full-history roi >= 0
    assert context_verdict_league(100, 0.01, recent_roi=-0.06) == "CAUTION"
    # n >= 100, roi >= 0.03, recent_roi >= 0 -> BOOST
    assert context_verdict_league(130, 0.04, recent_roi=0.01) == "BOOST"
    # sufficient n and roi but below BOOST thresholds -> ALLOW
    assert context_verdict_league(90, 0.01) == "ALLOW"

    # ---- team ----
    # n < 8 -> UNKNOWN
    assert context_verdict_team(5, -0.10) == "UNKNOWN"
    # roi=None -> UNKNOWN
    assert context_verdict_team(40, None) == "UNKNOWN"
    # roi <= -0.08 -> VETO
    assert context_verdict_team(40, -0.09) == "VETO"
    # roi <= -0.03 -> CAUTION
    assert context_verdict_team(40, -0.04) == "CAUTION"
    # n >= 45, roi >= 0.05 -> BOOST
    assert context_verdict_team(55, 0.06) == "BOOST"
    # sufficient n, mild positive roi -> ALLOW
    assert context_verdict_team(40, 0.02) == "ALLOW"

    # ---- odds_band ----
    # n < 20 -> UNKNOWN
    assert context_verdict_odds_band(10, 0.05) == "UNKNOWN"
    # roi=None -> UNKNOWN
    assert context_verdict_odds_band(110, None) == "UNKNOWN"
    # roi <= -0.02 -> VETO
    assert context_verdict_odds_band(110, -0.03) == "VETO"
    # roi <= 0.0 -> CAUTION
    assert context_verdict_odds_band(110, -0.01) == "CAUTION"
    # n >= 150, roi >= 0.02 -> BOOST
    assert context_verdict_odds_band(160, 0.03) == "BOOST"
    # sufficient n, roi just above 0 but below BOOST -> ALLOW
    assert context_verdict_odds_band(110, 0.01) == "ALLOW"

    # ---- niche ----
    assert context_verdict_niche(5, -0.20, strict_short_odds=True) == "UNKNOWN"
    assert context_verdict_niche(10, -0.09, strict_short_odds=True) == "VETO"
    assert context_verdict_niche(12, 0.04, strict_short_odds=True) == "BOOST"
    assert context_verdict_niche(16, -0.01, strict_short_odds=False) == "CAUTION"
    assert context_verdict_niche(11, 0.01, strict_short_odds=False) == "ALLOW"


def test_weighted_consensus_score():
    # ---- empty / degenerate inputs ----
    pick, score, unanimous = weighted_consensus_score([])
    assert pick is None and score == 0.0 and unanimous is False

    # All below min_lb floor -> no valid votes
    pick, score, unanimous = weighted_consensus_score(
        [("home", 0.40), ("home", 0.45)], min_lb=0.50)
    assert pick is None and score == 0.0 and unanimous is False

    # ---- perfect unanimity (all same pick) ----
    votes = [("home", 0.82), ("home", 0.70), ("home", 0.55)]
    pick, score, unanimous = weighted_consensus_score(votes)
    assert pick == "home"
    assert score == 1.0       # all weight goes to "home"
    assert unanimous is True

    # ---- 50/50 split on equal weights ----
    votes = [("home", 0.70), ("away", 0.70)]
    pick, score, unanimous = weighted_consensus_score(votes)
    assert score == 0.5
    assert unanimous is False

    # ---- majority by weight (stronger source wins even outnumbered) ----
    # forebet LB=0.82 votes "home"; two weaker sources (LB=0.55 each) vote "away"
    votes = [("home", 0.82), ("away", 0.55), ("away", 0.55)]
    pick, score, unanimous = weighted_consensus_score(votes)
    total = 0.82 + 0.55 + 0.55
    # "away" has 1.10, "home" has 0.82 — so away wins by weight
    assert pick == "away"
    # score is rounded to 4dp by assay.py — compare at that precision
    assert abs(score - round(1.10 / total, 4)) < 1e-9
    assert unanimous is False

    # ---- high-confidence unanimity: score should be 1.0 regardless of LB values ----
    votes = [("draw", 0.60), ("draw", 0.75), ("draw", 0.80)]
    pick, score, unanimous = weighted_consensus_score(votes)
    assert pick == "draw" and score == 1.0 and unanimous is True

    # ---- min_lb filter removes low-quality sources before vote ----
    # source C has lb=0.40 (below 0.50 floor) and votes "away" — should be ignored
    votes = [("home", 0.75), ("home", 0.80), ("away", 0.40)]
    pick, score, unanimous = weighted_consensus_score(votes, min_lb=0.50)
    assert pick == "home" and score == 1.0 and unanimous is True

    # ---- three-way split always has a winner by weight, never unanimous ----
    votes = [("home", 0.80), ("draw", 0.70), ("away", 0.60)]
    pick, score, unanimous = weighted_consensus_score(votes)
    assert pick == "home"
    assert unanimous is False
    total = 0.80 + 0.70 + 0.60
    # score is rounded to 4dp by assay.py — compare at that precision
    assert abs(score - round(0.80 / total, 4)) < 1e-9
