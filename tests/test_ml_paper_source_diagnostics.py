"""Derived-only source diagnostics: no frozen-schema, decision or sizing changes."""

import json
import math
from copy import deepcopy
from datetime import timedelta

import pytest
from test_ml_paper import DAY, FREEZE, candidate, capture, receipt

from edgefactory import ml_paper as mp


def with_source(i=1, *, model=0.7, source=0.4, bucket="SKIPPED_VETO", **kwargs):
    c = candidate(i, p=model, bucket=bucket, **kwargs)
    c["ml_inputs"] = {"values": {"forecast_1x2_home_mean": source}}
    return c


@pytest.mark.parametrize("side, expected", [("home", 0.5), ("draw", 0.3), ("away", 0.2)])
def test_source_matches_exact_1x2_side(side, expected):
    c = candidate(1)
    c["selection"] = side
    c["ml_inputs"] = {"values": {"forecast_1x2_home_mean": 0.5,
                                  "forecast_1x2_draw_mean": 0.3,
                                  "forecast_1x2_away_mean": 0.2}}
    assert mp.source_forecast_probability(c) == expected


@pytest.mark.parametrize("line", ["1.5", "2.5", "3.5", "4.5"])
@pytest.mark.parametrize("side", ["over", "under"])
def test_totals_only_use_same_line_and_correct_side(line, side):
    c = candidate(1, market=f"match_{side}_{line.replace('.', '')}")
    c["selection"] = side
    c["ml_inputs"] = {"values": {f"forecast_ou_{line}_over_mean": 0.8,
                                  "forecast_1x2_home_mean": 0.1}}
    assert mp.source_forecast_probability(c) == pytest.approx(0.8 if side == "over" else 0.2)


@pytest.mark.parametrize("side", ["yes", "no"])
def test_btts_uses_yes_mean_or_its_complement(side):
    c = candidate(1, market=f"btts_{side}")
    c["selection"] = side
    c["ml_inputs"] = {"values": {"forecast_btts_yes_mean": 0.6}}
    assert mp.source_forecast_probability(c) == pytest.approx(0.6 if side == "yes" else 0.4)


@pytest.mark.parametrize("side, expected", [
    ("1x", 0.8), ("home", 0.8), ("x2", 0.5), ("away", 0.5), ("12", 0.7), ("draw", 0.7),
])
def test_double_chance_sums_named_outcomes_not_a_single_outcome(side, expected):
    c = candidate(1, market="double_chance")
    c["selection"] = side
    c["ml_inputs"] = {"values": {"forecast_1x2_home_mean": 0.5,
                                  "forecast_1x2_draw_mean": 0.3,
                                  "forecast_1x2_away_mean": 0.2}}
    assert mp.source_forecast_probability(c) == pytest.approx(expected)


@pytest.mark.parametrize("source", [None, True, "0.4", float("nan"), float("inf"), -0.1, 1.1])
def test_invalid_or_missing_source_stays_unavailable(source):
    assert mp.source_forecast_probability(with_source(source=source)) is None


@pytest.mark.parametrize("inputs", [None, [], {}, {"values": None}, {"values": []}])
def test_legacy_or_malformed_optional_inputs_stay_missing(inputs):
    c = candidate(1)
    c["ml_inputs"] = inputs
    assert mp.source_forecast_probability(c) is None


@pytest.mark.parametrize("market, side", [
    ("home_over_15", "over"), ("away_under_25", "under"),
    ("match_over_25", "under"), ("btts_no", "yes"), ("1x2", "1x"),
    ("double_chance", "unknown"), ("match_over_55", "over"),
])
def test_unsupported_or_mismatched_markets_never_borrow_another_forecast(market, side):
    c = with_source(market=market)
    c["selection"] = side
    c["ml_inputs"]["values"].update({"forecast_ou_2.5_over_mean": 0.8, "forecast_btts_yes_mean": 0.6})
    assert mp.source_forecast_probability(c) is None


def test_missing_same_line_never_substitutes_confidence_or_another_total():
    c = candidate(1, market="match_over_25")
    c["selection"] = "over"
    c["ml_inputs"] = {"values": {"confidence": 0.9, "forecast_ou_3.5_over_mean": 0.8}}
    assert mp.source_forecast_probability(c) is None


@pytest.mark.parametrize("draw", [None, 0.8])
def test_double_chance_requires_both_valid_components_and_probability_at_most_one(draw):
    c = with_source(market="double_chance", source=0.5)
    c["selection"] = "1x"
    c["ml_inputs"]["values"]["forecast_1x2_draw_mean"] = draw
    assert mp.source_forecast_probability(c) is None


def test_paired_metrics_use_identical_resolved_observations_and_explicit_missing_counts():
    win = with_source(1, model=0.7, source=0.4)
    loss = with_source(2, model=0.3, source=0.6, bucket="CAUTION")
    missing = candidate(3)
    pending = with_source(4)
    rows = [win, loss, missing, pending]
    r = receipt(DAY, rows)

    def lookup(c):
        return None if c is pending else (0, 1) if c is loss else (2, 0)

    d = mp.calibration_diagnostics([r], lookup)["source_comparison"]
    paired = d["all_candidates"]
    assert paired["paired_fixtures"] == paired["paired_observations"] == 2
    assert paired["missing_source_fixtures"] == paired["missing_source_observations"] == 1
    assert paired["model_brier"] == pytest.approx(0.09)
    assert paired["source_brier"] == pytest.approx(0.36)
    assert paired["model_logloss"] == pytest.approx(-math.log(0.7))
    assert paired["source_logloss"] == pytest.approx(-math.log(0.4))
    assert d["by_board_bucket"]["SKIPPED_VETO"]["paired_observations"] == 1
    assert d["by_model_source_gap"]["unavailable"]["missing_source_observations"] == 1


def test_book_and_bucket_duplicates_do_not_reweight_overall_paired_errors():
    a = with_source(1)
    b = with_source(2, model=0.4, source=0.5)
    r = receipt(DAY, [a, b])
    before = mp.calibration_diagnostics([r], lambda c: (2, 0))["source_comparison"]
    duplicate = deepcopy(a)
    duplicate.update(book="Other book", bucket="CAUTION", candidate_id="duplicate")
    r["candidates"].extend([duplicate, deepcopy(a)])
    after = mp.calibration_diagnostics([r], lambda c: (2, 0))["source_comparison"]
    assert before["all_candidates"] == after["all_candidates"]
    assert before["by_model_source_gap"] == after["by_model_source_gap"]
    assert after["by_board_bucket"]["CAUTION"]["paired_observations"] == 1


def test_fixture_weighting_and_different_source_values_are_not_silently_collapsed():
    a = with_source(1, model=0.9, source=0.1)
    b = deepcopy(a)
    b.update(candidate_id="another-model", probability=0.8, base_probability=0.8, model_key="other")
    other_fixture = with_source(2, model=0.5, source=0.5)
    r = receipt(DAY, [a, b, other_fixture])
    stats = mp.calibration_diagnostics([r], lambda c: (2, 0))["source_comparison"]["all_candidates"]
    assert stats["paired_observations"] == 3 and stats["paired_fixtures"] == 2
    assert stats["model_brier"] == pytest.approx(((0.01 + 0.04) / 2 + 0.25) / 2)
    b["ml_inputs"]["values"]["forecast_1x2_home_mean"] = 0.2
    assert mp.calibration_diagnostics([r], lambda c: (2, 0))["source_comparison"]["all_candidates"]["source_brier"] != stats["source_brier"]


@pytest.mark.parametrize("model, expected", [
    (0.599, "lt_10pp"), (0.6, "10_to_lt_20pp"), (0.699, "10_to_lt_20pp"),
    (0.7, "ge_20pp"), (0.3, "ge_20pp"),
])
def test_gap_bands_have_stable_absolute_percentage_point_boundaries(model, expected):
    r = receipt(DAY, [with_source(model=model, source=0.5)])
    bands = mp.calibration_diagnostics([r], lambda c: (2, 0))["source_comparison"]["by_model_source_gap"]
    assert bands[expected]["paired_observations"] == 1
    assert sum(s["paired_observations"] for s in bands.values()) == 1


@pytest.mark.parametrize("source", [0.0, 1.0])
def test_endpoint_source_probabilities_have_finite_logloss_and_exact_brier(source):
    r = receipt(DAY, [with_source(source=source)])
    stats = mp.calibration_diagnostics([r], lambda c: (2, 0))["source_comparison"]["all_candidates"]
    assert math.isfinite(stats["source_logloss"])
    assert stats["source_brier"] == (source - 1) ** 2


def test_selected_source_pairs_deduplicate_book_variants_and_unselected_stay_measured():
    a, b, unused = [with_source(i) for i in (1, 2, 3)]
    duplicate = deepcopy(a)
    duplicate.update(book="Other book", candidate_id="another-book")
    r = receipt(DAY, [a, b, duplicate, unused], [
        {"legs": [a, b], "odds": 4.0, "stake_units": 1.0},
        {"legs": [duplicate, b], "odds": 4.0, "stake_units": 1.0},
    ])
    d = mp.calibration_diagnostics([r], lambda c: (2, 0))
    assert d["source_comparison"]["selected_candidates"]["paired_observations"] == 2
    assert d["source_comparison"]["all_candidates"]["paired_observations"] == 3
    assert d["selected_candidates"]["resolved_observations"] == 2


def test_no_results_means_no_invented_accuracy():
    r = receipt(DAY, [with_source()])
    d = mp.calibration_diagnostics([r], lambda c: None)["source_comparison"]
    assert d["all_candidates"]["paired_fixtures"] == 0
    assert d["all_candidates"]["model_brier"] is None
    assert d["all_candidates"]["source_logloss"] is None
    assert all(v["paired_observations"] == 0 for v in d["by_model_source_gap"].values())


@pytest.mark.parametrize("quote", [None, "bad", "2026-11-02T08:00:00+00:00"])
def test_quote_age_missing_invalid_or_future_remains_unavailable(quote):
    c = with_source()
    c["price_at"] = quote
    assert mp.quote_age_at_decision(c, {"captured_at": FREEZE.isoformat()}) is None


def test_age_and_gap_rendered_from_original_inputs_without_clock_or_receipt_mutation():
    c = with_source(model=0.696, source=0.425)
    c["price_at"] = (FREEZE - timedelta(hours=9)).isoformat()
    b = with_source(2)
    r = receipt(DAY, [c, b], [{"legs": [c, b], "odds": 4.0, "stake_units": 1.0, "book": c["book"]}])
    r["captured_at"] = FREEZE.isoformat()
    before = deepcopy(r)
    text = mp.render_card(r)
    assert "Source forecast 42.5% · gap +27.1 pp · quote age 9.00h at decision" in text
    assert "intentionally paper-eligible" in text
    assert mp.quote_age_at_decision(c, r) == 32400
    assert r == before


def test_last_decision_learning_gate_is_not_confused_with_selected_leg_count():
    r = receipt(DAY, [with_source(1), with_source(2)])
    r["learning"].update(fixtures=2, observations=100)
    report = mp.performance([r], lambda c: (2, 0))
    text = mp.render_performance(report)
    assert "0 resolved selected observations / 0 fixtures · pool 2 resolved fixtures" in text
    assert "last decision: 2 resolved prior-day fixtures" in text
    assert "dynamic calibration + success tilt from first results" in text
    assert "not an automatic review/promotion trigger" in text
    assert "PAIRED   2 fixtures / 2 observations" in text


def test_new_diagnostics_and_refresh_cannot_change_frozen_or_financial_evidence(tmp_path):
    row = capture(tmp_path)
    frozen = mp.receipt_path(tmp_path, DAY)
    state = mp.state_path(tmp_path)
    before = {p: p.read_bytes() for p in (frozen, state)}
    predictions = json.dumps(row, sort_keys=True)
    mp.calibration_diagnostics([row], lambda c: (2, 0))
    mp.render_card(row)
    mp.publish(tmp_path, lambda c: (2, 0))
    assert all(p.read_bytes() == data for p, data in before.items())
    assert json.dumps(row, sort_keys=True) == predictions
    assert mp.receipts(tmp_path) == [row]
