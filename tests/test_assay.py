"""The math must never silently break. Run: pytest"""
from edgefactory.assay import (BetStats, decay_verdict, grade,
                               should_bench, wilson_lower_bound)


def test_wilson_basics():
    assert wilson_lower_bound(0, 0) == 0.0
    # 9/10 looks great but small n gets punished
    assert wilson_lower_bound(9, 10) < 0.75
    # 900/1000 barely punished
    assert wilson_lower_bound(900, 1000) > 0.88
    # monotone in n at same rate
    assert wilson_lower_bound(90, 100) < wilson_lower_bound(900, 1000)


def test_grades():
    assert grade(0.90) == "PLATINUM"
    assert grade(0.75) == "GOLD"
    assert grade(0.30) == "CHARCOAL"


def test_betstats_roi():
    s = BetStats()
    s.add(True, 2.0)    # +1.0
    s.add(False, 2.0)   # -1.0
    s.add(True, 3.0)    # +2.0
    assert s.n == 3 and s.wins == 2
    assert abs(s.pl_units - 2.0) < 1e-9
    assert abs(s.roi_pct - (2.0 / 3 * 100)) < 1e-6


def test_betstats_unpriced_excluded_from_roi():
    s = BetStats()
    s.add(True, None)
    assert s.roi_pct is None and s.n == 1


def test_decay_verdicts():
    assert decay_verdict([5, 5]) == "unknown"            # too short
    assert decay_verdict([0, 0, 10, 12]) == "growing"
    assert decay_verdict([10, 12, 9, 11]) == "stable"
    assert decay_verdict([20, 18, 2, 1]) == "decaying"
    assert decay_verdict([20, 18, -5, -8]) == "dead"


def test_should_bench():
    # not enough live data -> never bench
    assert not should_bench(5, 10, 0.80)
    # live collapsed well below certificate -> bench
    assert should_bench(30, 100, 0.80)
    # live tracking certificate -> keep (upper bound can't be below cert)
    assert not should_bench(78, 100, 0.80)
    assert not should_bench(312, 400, 0.80)
    # moderately bad but maybe noise (65/100 vs 0.80 cert) -> still benched,
    # because even best-case 65% + CI is below 75%
    assert should_bench(65, 100, 0.80)
