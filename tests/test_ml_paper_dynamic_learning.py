"""Dynamic probability engine: calibration + success tilt from first results."""

from copy import deepcopy

from test_ml_paper import NOW, candidate, receipt

from edgefactory import ml_paper as mp

YESTERDAY = "2026-11-01"


def test_calibration_fits_from_first_resolved_fixtures_no_gate():
    cs = [candidate(i, date=YESTERDAY, p=0.8) for i in range(4)]
    lookup = lambda c: (2, 0) if int(c["candidate_id"]) % 4 == 0 else (0, 2)
    learner = mp.learn([receipt(YESTERDAY, cs)], NOW, lookup)
    assert learner["status"] == "fitted_prior_paper_errors"
    assert learner["fixtures"] == 4
    assert learner["learning_policy"] == mp.DYNAMIC_LEARNING_POLICY
    assert learner["evidence_gate"] == "none_from_first_resolved_prior_day_results_evidence_smoothed"
    rows = [candidate(50, p=0.8)]
    mp.apply_learning(rows, learner)
    assert rows[0]["probability"] < 0.8  # 80% predictions were wrong 75% of the time


def test_success_tilt_only_before_both_outcome_classes_seen():
    cs = [candidate(i, date=YESTERDAY, p=0.5) for i in range(2)]
    learner = mp.learn([receipt(YESTERDAY, cs)], NOW, lambda c: (2, 0))
    assert learner["status"] == "dynamic_success_tilt_only"
    assert learner["success_tilt"]["bucket:CAUTION"]["tilt_logit"] > 0
    rows = [candidate(50, p=0.5)]
    mp.apply_learning(rows, learner)
    assert 0.5 < rows[0]["probability"] < 0.70  # bounded total tilt (<=0.75 logit)


def test_success_tilt_moves_away_from_losing_groups():
    cs = [candidate(i, date=YESTERDAY, p=0.5) for i in range(2)]
    learner = mp.learn([receipt(YESTERDAY, cs)], NOW, lambda c: (0, 2))
    assert learner["success_tilt"]["bucket:CAUTION"]["tilt_logit"] < 0
    rows = [candidate(50, p=0.5)]
    mp.apply_learning(rows, learner)
    assert rows[0]["probability"] < 0.5


def test_success_tilt_is_bounded_and_auditable():
    cs = [candidate(i, date=YESTERDAY, p=0.9) for i in range(3)]
    learner = mp.learn([receipt(YESTERDAY, cs)], NOW, lambda c: (2, 0))
    for entry in learner["success_tilt"].values():
        assert -mp.SUCCESS_TILT_GROUP_LIMIT_LOGIT <= entry["tilt_logit"] <= mp.SUCCESS_TILT_GROUP_LIMIT_LOGIT
        assert entry["weighted_hit_rate"] == 1.0
        assert entry["excess"] > 0
    rows = [candidate(50, p=0.9)]
    mp.apply_learning(rows, learner)
    assert rows[0]["probability"] < 0.95  # total tilt clamped, never runaway


def test_recency_weighting_discounts_old_results():
    old = [candidate(1, date="2026-10-18", p=0.5)]
    fresh = [candidate(2, date=YESTERDAY, p=0.5)]
    old_model = mp.learn([receipt("2026-10-18", old)], NOW, lambda c: (2, 0))
    fresh_model = mp.learn([receipt(YESTERDAY, fresh)], NOW, lambda c: (2, 0))
    old_weight = old_model["success_tilt"]["bucket:CAUTION"]["weighted_observations"]
    fresh_weight = fresh_model["success_tilt"]["bucket:CAUTION"]["weighted_observations"]
    assert old_weight < fresh_weight < 1.0


def test_no_results_retains_existing_model_probability():
    learner = mp.learn([], NOW, lambda c: None)
    assert learner["status"] == "awaiting_prior_paper_results"
    assert learner["success_tilt"] == {}
    rows = [candidate(50, p=0.7)]
    before = deepcopy(rows)
    mp.apply_learning(rows, learner)
    assert rows == before


def test_learning_never_trains_on_todays_outcomes():
    today_cs = [candidate(i, date="2026-11-02", p=0.5) for i in range(2)]
    learner = mp.learn([receipt("2026-11-02", today_cs)], NOW, lambda c: (2, 0))
    assert learner["fixtures"] == 0
    assert learner["status"] == "awaiting_prior_paper_results"


def test_evidence_smoothing_softens_early_swings():
    few = [candidate(i, date=YESTERDAY, p=0.5) for i in range(2)]
    many = [candidate(i, date=YESTERDAY, p=0.5) for i in range(40)]
    few_model = mp.learn([receipt(YESTERDAY, few)], NOW, lambda c: (2, 0))
    many_model = mp.learn([receipt(YESTERDAY, many)], NOW,
                          lambda c: (2, 0) if int(c["candidate_id"]) % 4 else (0, 2))
    assert few_model["smoothing_factor"] == 2 / 7
    assert many_model["smoothing_factor"] == 40 / 45
    few_rows, many_rows = [candidate(90, p=0.5)], [candidate(91, p=0.5)]
    mp.apply_learning(few_rows, few_model)
    mp.apply_learning(many_rows, many_model)
    # Same direction, but the thin-evidence shift is much gentler.
    assert 0.5 < few_rows[0]["probability"] < many_rows[0]["probability"]
