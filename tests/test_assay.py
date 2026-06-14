"""The math must never silently break. Run: pytest"""
from edgefactory.assay import (wilson_lb, wilson_ub, grade,
                               decay_verdict, should_bench, roi,
                               context_verdict_league, context_verdict_team,
                               context_verdict_odds_band)

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
    # n < 80 -> UNKNOWN regardless of ROI
    assert context_verdict_league(30, 0.05) == "UNKNOWN"
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
    # n >= 120, roi >= 0.03, recent_roi >= 0 -> BOOST
    assert context_verdict_league(130, 0.04, recent_roi=0.01) == "BOOST"
    # sufficient n and roi but below BOOST thresholds -> ALLOW
    assert context_verdict_league(90, 0.01) == "ALLOW"

    # ---- team ----
    # n < 35 -> UNKNOWN
    assert context_verdict_team(20, -0.10) == "UNKNOWN"
    # roi=None -> UNKNOWN
    assert context_verdict_team(40, None) == "UNKNOWN"
    # roi <= -0.08 -> VETO
    assert context_verdict_team(40, -0.09) == "VETO"
    # roi <= -0.03 -> CAUTION
    assert context_verdict_team(40, -0.04) == "CAUTION"
    # n >= 50, roi >= 0.05 -> BOOST
    assert context_verdict_team(55, 0.06) == "BOOST"
    # sufficient n, mild positive roi -> ALLOW
    assert context_verdict_team(40, 0.02) == "ALLOW"

    # ---- odds_band ----
    # n < 100 -> UNKNOWN
    assert context_verdict_odds_band(50, 0.05) == "UNKNOWN"
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
