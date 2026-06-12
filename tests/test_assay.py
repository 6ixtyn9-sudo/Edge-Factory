"""The math must never silently break. Run: pytest"""
from edgefactory.assay import (wilson_lb, wilson_ub, grade,
                               decay_verdict, should_bench, roi)

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
