"""Synthetic tests of the offline goal learner, NOT native forecast evidence."""
from copy import deepcopy
from datetime import UTC, datetime
import json
import math

import pytest
from scipy.stats import poisson

from edgefactory import ml_paper as mp
from edgefactory.consensus_contracts import ENH_OPTIONAL_FEATURES, enhancement_fixture_identity
from test_ml_paper import candidate, receipt

NOW = datetime(2026, 11, 6, 6, tzinfo=UTC)


def observed(i, day="2026-11-03", **kwargs):
    c = candidate(i, date=day, **kwargs)
    c.update(model_key="synthetic-legacy-binding", contract_id="synthetic-contract",
             price_source="theoddsapi")
    c["fixture"] = enhancement_fixture_identity(c)[:3]
    c["ml_inputs"] = {"fixture": enhancement_fixture_identity(c),
                      "model_key": c["model_key"], "contract_id": c["contract_id"],
                      "sources": ["statarea"],
                      "values": {"forecast_1x2_home_mean": 0.3 + i * 0.05,
                                 "home_form_gf": 1.0 + i / 10}}
    return c


def seal(cs, *, day=None, captured=None):
    r = receipt(day or cs[0]["date"], cs)
    if captured:
        r["captured_at"] = captured
    r["sha256"] = mp.digest(r)
    return r


def lookup(c):
    i = int(c["candidate_id"].split("-")[0])
    return (i % 3, (i + 1) % 3)


def fit(cs=None, history=None):
    return mp.learn(history if history is not None else [seal(cs or [observed(i) for i in range(1, 7)])],
                    NOW, lookup, method="poisson")


def resign(model):
    model["model_key"] = mp.digest({k: v for k, v in model.items() if k != "model_key"})
    return model


def test_fit_targets_goals_one_weight_per_fixture_and_preserves_evidence():
    h = [seal([observed(i) for i in range(1, 7)])]
    before = deepcopy(h)
    model = fit(history=h)
    assert h == before
    assert model["status"] == "fitted_prior_goal_results"
    assert model["fixtures"] == model["observations"] == 6
    assert model["offline_only"] is True
    assert model["target"] == ["regulation_home_goals", "regulation_away_goals"]
    assert set(model["columns"]) <= set(ENH_OPTIONAL_FEATURES)
    assert not {"success_tilt", "smoothing_factor"} & model.keys()
    assert model["training_sha256"] == mp.digest(model["training_outcomes"])
    assert [o["score"] for o in model["training_outcomes"]] == [list(lookup(observed(i))) for i in range(1, 7)]
    assert model["model_key"] == mp.digest({k: v for k, v in model.items() if k != "model_key"})


def test_quote_market_bucket_and_old_fits_do_not_manufacture_training_rows():
    cs = [observed(i) for i in range(1, 7)]
    variants = []
    for c in cs:
        for j in range(4):
            v = deepcopy(c)
            v.update(candidate_id=f"{c['candidate_id']}-{j}", odds=9 + j, bucket=f"unused-{j}",
                     book=f"Book-{j}", market="btts_yes", selection="yes",
                     base_probability=0.001 + j / 10, probability=0.99 - j / 10)
            v["ml_inputs"]["values"].update(confidence=0.99, hs=99, odds=100, old_coef=1e6)
            variants.append(v)
    a, b = fit(cs), fit(variants)
    assert a["fixtures"] == b["fixtures"] == 6
    for key in ("columns", "means", "scales", "coef", "intercept"):
        assert a[key] == b[key]


def test_earliest_frozen_state_and_conflicts_are_not_resolved_by_best_model_or_result():
    first = [seal([observed(i) for i in range(1, 7)])]
    later = deepcopy(first[0])
    later["captured_at"] = later["draft_persisted_at"] = "2026-11-03T06:30:00+00:00"
    for c in later["candidates"]:
        c["ml_inputs"]["values"]["home_form_gf"] = 99
    later.pop("sha256")
    later["sha256"] = mp.digest(later)
    a, b = fit(history=first), fit(history=[later, *first])
    assert a == b
    conflict = deepcopy(first[0]["candidates"][0])
    conflict["candidate_id"] = "1-conflict"
    conflict["ml_inputs"]["values"]["home_form_gf"] = 99
    model = fit([*first[0]["candidates"], conflict])
    assert model["fixtures"] == 5
    assert model["training_admission"]["conflicting_earliest_fixture_inputs"] == 1
    assert ["2026-11-03", "home1", "away1"] not in [o["fixture"] for o in model["training_outcomes"]]


def test_historical_quote_floor_is_applied_before_outcome_lookup():
    bad = observed(1)
    bad.update(price_source="oddspapi", price_provenance=None)
    def forbidden(c):
        raise AssertionError("quarantined quote reached outcome lookup")
    model = mp.learn([seal([bad])], NOW, forbidden, method="poisson")
    assert model["fixtures"] == 0
    assert model["training_admission"]["oddspapi_legacy_or_unproven_quote_generation"] == 1


@pytest.mark.parametrize("change", [
    {"fixture": ["2026-11-03", "wrong", "awayclub1", [], []]},
    {"model_key": "different"}, {"contract_id": "different"},
    {"sources": ["forebet"]}, {"sources": [True]}, {"sources": []},
    {"values": {"home_form_gf": -1}}, {"values": {"home_form_gf": True}},
    {"values": {"forecast_1x2_home_mean": 65}}, {"values": {"confidence": 0.9}},
])
def test_bad_or_missing_source_binding_never_enters_fit(change):
    c = observed(1)
    c["ml_inputs"].update(change)
    model = fit([c])
    assert model["fixtures"] == 0
    assert model["training_admission"]["invalid_source_input_binding_or_values"] == 1


@pytest.mark.parametrize("score", [None, (1, None), (True, 1), (-1, 2), (1.5, 2), (1, 2, 3), "2-1"])
def test_no_invented_targets_from_invalid_results(score):
    model = mp.learn([seal([observed(1)])], NOW, lambda c: score, method="poisson")
    assert model["fixtures"] == 0


def test_zero_mean_has_no_fabricated_epsilon_or_old_prediction_fallback():
    model = mp.learn([seal([observed(1)])], NOW, lambda c: (2, 0), method="poisson")
    assert model["status"] == "zero_mean_goal_target"
    c = observed(9, "2026-11-07")
    before = deepcopy(c)
    with pytest.raises(ValueError, match="unavailable"):
        mp.apply_learning([c], model)
    assert c == before


def test_corrupt_receipt_is_error_not_smaller_training_set():
    r = seal([observed(1)])
    r["candidates"][0]["ml_inputs"]["values"]["home_form_gf"] = 42
    with pytest.raises(ValueError, match="checksum"):
        fit(history=[r])


def test_prior_day_cutoff_and_training_only_preprocessing():
    past = seal([observed(i) for i in range(1, 7)])
    future = seal([observed(8, "2026-11-07")])
    same_day = seal([observed(9, "2026-11-06")])
    same_day["persisted_at"] = same_day["captured_at"]
    mixed, prior = fit(history=[past, future, same_day]), fit(history=[past])
    for key in ("training_outcomes", "columns", "means", "scales", "coef", "intercept"):
        assert mixed[key] == prior[key]
    model = fit(history=[past])
    assert model["means"] == pytest.approx([0.475, 1.35])
    assert model["scales"] == pytest.approx([math.sqrt(0.007291666666666667), math.sqrt(0.029166666666666667)])
    c = observed(9, "2026-11-07")
    c["ml_inputs"]["values"]["forecast_1x2_home_mean"] = None
    vector = mp._vector(c, model["columns"], means=model["means"], scales=model["scales"])
    assert vector[0] == 0 and vector[2:] == [1.0, 0.0]


def test_serialized_model_replays_and_does_not_use_old_predictions_in_serving():
    model = json.loads(json.dumps(fit(), allow_nan=False))
    a = observed(9, "2026-11-07")
    b = deepcopy(a)
    b.update(base_probability=0.9999, probability=0.0001, odds=100, bucket="not-used")
    b["ml_inputs"]["values"]["confidence"] = 0.0001
    original = deepcopy(a)
    mp.apply_learning([a, b], model)
    assert a["probability"] == b["probability"]
    assert a["base_probability"] == original["base_probability"]
    assert a["forecast_model_key"] == model["model_key"]
    assert a["probability_normalization"] == "independent_poisson_goals"
    x = mp._vector(original, model["columns"], means=model["means"], scales=model["scales"])
    assert a["forecast_goal_means"] == pytest.approx([
        math.exp(intercept + sum(w * v for w, v in zip(coef, x)))
        for intercept, coef in zip(model["intercept"], model["coef"])])


@pytest.mark.parametrize("change", [
    {"coef": [[1], [1]]}, {"intercept": [1]}, {"scales": [0, 1]},
    {"means": [0]}, {"columns": ["confidence", "odds"]},
    {"columns": ["home_form_gf", "home_form_gf"]},
    {"training_last_date": "2026-11-06"}, {"status": "fitted_prior_paper_errors"},
])
def test_malformed_resigned_model_is_rejected(change):
    model = fit()
    model.update(change)
    resign(model)
    with pytest.raises(ValueError):
        mp.apply_learning([observed(9, "2026-11-07")], model)


def test_modified_model_checksum_and_nonforward_inputs_are_rejected_atomically():
    model = fit()
    tampered = deepcopy(model)
    tampered["coef"][0][0] += 1
    cs = [observed(8, "2026-11-07"), observed(9, "2026-11-07")]
    before = deepcopy(cs)
    with pytest.raises(ValueError):
        mp.apply_learning(cs, tampered)
    assert cs == before
    cs[1]["ml_inputs"]["fixture"][1] = "wrong"
    before = deepcopy(cs)
    with pytest.raises(ValueError):
        mp.apply_learning(cs, model)
    assert cs == before
    with pytest.raises(ValueError, match="forward"):
        mp.apply_learning([observed(1)], model)


@pytest.mark.parametrize("market", sorted(set(mp.MARKET_PRICE_MAP) | {"1x2"}))
def test_goal_market_probability_matches_existing_score_settlement(market):
    selection = "1x" if market == "double_chance" else "home"
    weights = [(h, a, float(poisson.pmf(h, 1.3) * poisson.pmf(a, 1.7)))
               for h in range(25) for a in range(25)]
    assert mp.probability({"goal_means": [1.3, 1.7]}, market, selection) == pytest.approx(
        mp.probability(weights, market, selection), abs=1e-12)


def test_goal_distribution_is_coherent_across_markets_and_missing_quote_sides():
    weights = {"goal_means": [1.3, 1.7]}
    p = lambda market, side: mp.probability(weights, market, side)
    assert sum(p("1x2", side) for side in ("home", "draw", "away")) == pytest.approx(1)
    assert p("double_chance", "1x") == pytest.approx(p("1x2", "home") + p("1x2", "draw"))
    assert p("btts_yes", "yes") + p("btts_no", "no") == pytest.approx(1)
    for family in ("home", "away", "match"):
        for line in ("15", "25", "35", "45"):
            assert p(f"{family}_over_{line}", "over") + p(f"{family}_under_{line}", "under") == pytest.approx(1)
    assert p("match_over_45", "over") <= p("match_over_35", "over") <= p("match_over_25", "over")
    assert p("handicap", "home") is None


@pytest.mark.parametrize("goals", [[0, 1], [-1, 1], [float("inf"), 1], [float("nan"), 1], [True, 1]])
def test_invalid_goal_means_rejected_not_clipped(goals):
    with pytest.raises(ValueError):
        mp.probability({"goal_means": goals}, "1x2", "home")


def test_default_production_learner_is_unchanged_and_unknown_method_rejected():
    h = [seal([observed(i) for i in range(1, 7)])]
    assert mp.learn(h, NOW, lookup) == mp.learn(h, NOW, lookup, method="calibration")
    with pytest.raises(ValueError, match="unknown"):
        mp.learn(h, NOW, lookup, method="invented")


def test_goal_fit_failure_has_no_fallback_and_requires_aware_decision_time(monkeypatch):
    from sklearn.linear_model import PoissonRegressor
    def unavailable(*args, **kwargs):
        raise ValueError("synthetic fit failure")
    monkeypatch.setattr(PoissonRegressor, "fit", unavailable)
    model = fit()
    assert model["status"] == "goal_fit_unavailable"
    assert "coef" not in model
    with pytest.raises(ValueError, match="unavailable"):
        mp.apply_learning([observed(9, "2026-11-07")], model)
    with pytest.raises(ValueError, match="aware"):
        mp.learn([], NOW.replace(tzinfo=None), lookup, method="poisson")


def test_missing_goal_method_and_mismatched_fixture_day_fail_closed():
    model = fit()
    broken = deepcopy(model)
    broken.pop("method")
    resign(broken)
    with pytest.raises(ValueError, match="method"):
        mp.apply_learning([observed(9, "2026-11-07")], broken)
    c = observed(9, "2026-11-07")
    c["kickoff_utc"] = "2026-11-08T12:00:00+00:00"
    with pytest.raises(ValueError, match="forward"):
        mp.apply_learning([c], model)


def test_goal_predictions_feed_existing_selection_and_all_capital_projections():
    # Pure synthetic composition test, not a new bank, receipt or paper run.
    model = mp.learn([seal([observed(i) for i in range(1, 7)])], NOW,
                     lambda c: (3, 1), method="poisson")
    cs = [observed(i, "2026-11-07") for i in range(1, 7)]
    mp.apply_learning(cs, model)
    prior = {"stake_units": 2.0, "profit_units": None, "legs": [deepcopy(cs[0])]}
    report = {"paper_bank_units": 100.0, "paper_committed_units": 2.0,
              "paper_free_units": 98.0, "history": [{"accas": [prior]}]}
    before = deepcopy(report)
    diagnostics = {}
    plan, audit = mp._size_publication_accas(cs, report, diagnostics)
    assert report == before
    assert plan and all(a["stake_units"] > 0 for a in plan)
    mp._require_mutually_exclusive(plan)
    assert sum(mp._stake_micro_units(a["stake_units"]) for a in plan) <= 23_000_000
    assert all(e["published_stake_micro_units"] <= e["residual_budget_micro_units"]
               for e in audit["fixtures"])
    exposure = mp._fixture_exposure_micro_units(plan)
    for fixture, amount in exposure.items():
        assert amount + (2_000_000 if fixture == tuple(cs[0]["fixture"]) else 0) <= 5_000_000
    assert audit["published_stake_micro_units"] <= audit["input_stake_micro_units"]
