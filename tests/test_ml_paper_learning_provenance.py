"""Historical quote quarantine affects refits/validation, never frozen finances."""

from copy import deepcopy
from datetime import datetime, UTC
import json
from pathlib import Path

import pytest

from edgefactory import ml_paper as mp
from test_ml_paper import NOW, candidate, receipt

DAY = "2026-11-01"
REASON = "oddspapi_legacy_or_unproven_quote_generation"


def quoted(i=1, *, source="theoddsapi", generation=None, **kwargs):
    c = candidate(i, date=DAY, **kwargs)
    c["price_source"] = source
    c["price_provenance"] = None if generation is None else {
        "schema": "normalized_odds_quote_v1", "row": {"schema_version": generation},
    }
    return c


@pytest.mark.parametrize("source", ["oddspapi", "oddspapi_odds", "ODDSPAPI"])
@pytest.mark.parametrize("generation", [None, 0, 1, 2, 3, "3", "invalid", True])
def test_legacy_family_cannot_reenter_learning_via_frozen_receipts(source, generation):
    bad = quoted(source=source, generation=generation)
    history = [receipt(DAY, [bad])]
    before = deepcopy(history)

    def forbidden_lookup(c):
        raise AssertionError("an ineligible quote must be filtered before outcome lookup")

    learner = mp.learn(history, NOW, forbidden_lookup)
    assert learner["observations"] == learner["fixtures"] == 0
    assert learner["status"] == "awaiting_prior_paper_results"
    assert not {"success_tilt", "coef", "intercept"} & learner.keys()
    audit = learner["training_admission"]
    assert audit["excluded_candidate_occurrences"] == audit["excluded_fixture_count"] == 1
    assert audit["excluded_by_reason"] == {REASON: 1}
    assert audit["oddspapi_min_schema_version"] == mp.ODDSPAPI_MIN_SCHEMA_VERSION
    assert history == before


@pytest.mark.parametrize("provenance", [{}, {"schema": "other", "row": {"schema_version": 4}},
                                       {"schema": "normalized_odds_quote_v1"},
                                       {"schema": "normalized_odds_quote_v1", "row": None}])
def test_missing_generation_witness_is_not_silently_rehabilitated(provenance):
    c = quoted(source="oddspapi")
    c["price_provenance"] = provenance
    assert mp.learn([receipt(DAY, [c])], NOW, lambda c: (2, 0))["observations"] == 0


@pytest.mark.parametrize("source", ["oddspapi", "oddspapi_odds"])
@pytest.mark.parametrize("generation", [4, "4", 5])
def test_current_generation_uses_the_existing_supply_floor(source, generation):
    # Synthetic parser-generation witness, not evidence of authentic native prices.
    c = quoted(source=source, generation=generation)
    learner = mp.learn([receipt(DAY, [c])], NOW, lambda c: (0, 1))
    assert learner["observations"] == learner["fixtures"] == 1
    assert learner["training_outcomes"][0]["hit"] == 0  # genuine loss retained
    assert learner["training_admission"]["excluded_by_reason"] == {}


@pytest.mark.parametrize("source", ["theoddsapi", "betexplorer", "betexplorer_odds", "pinnapi_odds"])
def test_unaffected_sources_keep_both_wins_and_losses(source):
    cs = [quoted(1, source=source), quoted(2, source=source)]
    learner = mp.learn([receipt(DAY, cs)], NOW, lambda c: (2, 0) if c["candidate_id"] == "1" else (0, 2))
    assert learner["observations"] == 2
    assert {x["hit"] for x in learner["training_outcomes"]} == {0, 1}
    assert learner["status"] == "fitted_source_market_temperature"


@pytest.mark.parametrize("source", [42, True, [], {}])
def test_malformed_source_metadata_is_excluded_not_a_lane_failure(source):
    c = quoted(source=source)
    model = mp.learn([receipt(DAY, [c])], NOW, lambda c: (2, 0))
    assert model["observations"] == 0
    assert model["training_admission"]["excluded_by_reason"] == {"malformed_learning_price_source": 1}


def without_audit(model):
    return {k: v for k, v in model.items() if k not in {"training_admission", "model_key"}}


def test_filter_precedes_dedup_and_does_not_discard_an_eligible_companion():
    bad = quoted(1, source="oddspapi")
    good = deepcopy(bad)
    good.update(candidate_id="other-book", book="OtherBook", price_source="theoddsapi")
    history = [receipt(DAY, [bad, good, deepcopy(good)])]
    before = deepcopy(history)
    learner = mp.learn(history, NOW, lambda c: (0, 1))
    direct = mp.learn([receipt(DAY, [good])], NOW, lambda c: (0, 1))
    assert without_audit(learner) == without_audit(direct)
    assert learner["observations"] == 1
    assert learner["training_outcomes"][0]["candidate_id"] == "other-book"
    assert history == before


def test_refit_recomputes_fixture_weights_columns_smoothing_and_crossfit_from_eligible_rows():
    good = [quoted(1, p=0.8), quoted(2, p=0.7)]
    bad = quoted(3, source="oddspapi", bucket="BAD_ONLY")
    sibling = deepcopy(good[0])
    sibling.update(candidate_id="sibling", market="match_over_25", selection="over",
                   price_source="oddspapi", bucket="BAD_ONLY")
    history = [receipt(DAY, [bad, good[0], sibling, good[1]])]
    before = deepcopy(history)
    lookup = lambda c: (2, 0) if c["candidate_id"] == "1" else (0, 2)
    learner = mp.learn(history, NOW, lookup)
    expected = mp.learn([receipt(DAY, good)], NOW, lookup)
    assert without_audit(learner) == without_audit(expected)
    assert learner["fixtures"] == 2 and learner["parameters"] == 1
    assert not {"columns", "success_tilt", "smoothing_factor"} & learner.keys()
    assert learner["training_admission"]["excluded_candidate_occurrences"] == 2
    assert history == before


def test_repeated_legacy_book_quotes_are_occurrences_not_independent_training_evidence():
    bad = quoted(source="oddspapi")
    copies = [dict(bad, candidate_id=str(i), book=f"Book{i}") for i in range(25)]
    model = mp.learn([receipt(DAY, copies)], NOW, lambda c: (2, 0))
    assert model["observations"] == 0
    audit = model["training_admission"]
    assert audit["excluded_candidate_occurrences"] == 25
    assert audit["excluded_fixture_count"] == 1


def test_today_future_and_unresolved_candidates_do_not_supply_training_or_fake_losses():
    old = quoted(1)
    today = candidate(2)
    future = candidate(3, date="2026-11-03")
    history = [receipt(DAY, [old]), receipt("2026-11-02", [today]), receipt("2026-11-03", [future])]
    model = mp.learn(history, NOW, lambda c: None)
    assert model["observations"] == 0
    assert model["training_outcomes"] == []
    assert model["training_admission"]["excluded_candidate_occurrences"] == 0


def test_old_adjusted_predictions_and_stored_coefficients_are_not_carried_into_refit():
    cs = [quoted(1, p=0.8), quoted(2, p=0.7)]
    history = [receipt(DAY, cs)]
    changed = deepcopy(history)
    changed[0]["learning"].update(status="fitted_source_market_temperature", coef=[9999], intercept=-9999)
    for c in changed[0]["candidates"]:
        c["probability"] = 0.00001
    lookup = lambda c: (2, 0) if c["candidate_id"] == "1" else (0, 2)
    a = mp.learn(history, NOW, lookup)
    b = mp.learn(changed, NOW, lookup)
    # Only source partitions and outcomes define training; old fitted outputs
    # and adjusted predictions are not model inputs or training-hash inputs.
    assert a["training_sha256"] == b["training_sha256"]
    for field in ("power", "training_outcomes", "training_outcomes_sha256"):
        assert a[field] == b[field]


def test_calibration_validation_quarantines_bad_quotes_but_finances_keep_every_position(monkeypatch):
    cs = [quoted(1, source="oddspapi"), quoted(2), quoted(3)]
    acca = {"legs": cs[:2], "odds": cs[0]["odds"] * cs[1]["odds"], "stake_units": 3.0}
    history = [receipt(DAY, cs, [acca])]
    before = deepcopy(history)
    lookup = lambda c: (0, 2) if c["candidate_id"] == "1" else (2, 0)
    with monkeypatch.context() as m:
        m.setattr(mp, "_learning_quote_rejection", lambda c: None)
        original = mp.performance(history, lookup)
    filtered = mp.performance(history, lookup)
    assert {k: v for k, v in original.items() if k != "calibration"} == {
        k: v for k, v in filtered.items() if k != "calibration"}
    assert filtered["profit_units"] == -3.0
    assert filtered["losses"] == 1
    assert filtered["paper_bank_units"] == 97.0
    assert original["calibration"]["all_candidates"]["resolved_observations"] == 3
    assert filtered["calibration"]["all_candidates"]["resolved_observations"] == 2
    assert filtered["calibration"]["candidate_admission"]["excluded_candidate_occurrences"] == 1
    rendered = mp.render_performance(filtered)
    assert "1 ineligible-quote candidate occurrences excluded from paired errors" in rendered
    assert "Historical P&L and frozen predictions unchanged; not a clean-refit backtest." in rendered
    assert history == before


def test_actual_retained_bookings_outlier_is_not_future_learning_inventory():
    path = Path(__file__).parent / "fixtures/ml_outlier_2026-11-04.json"
    blob = path.read_bytes()
    c = json.loads(blob)["candidate"]
    history = [receipt(c["date"], [c])]
    before = deepcopy(history)
    learner = mp.learn(history, datetime(2026, 11, 5, 12, tzinfo=UTC), lambda c: (2, 3))
    assert learner["observations"] == 0
    assert learner["training_admission"]["excluded_by_reason"] == {REASON: 1}
    assert history == before
    assert path.read_bytes() == blob


def test_clean_only_training_hash_and_outcomes_remain_reproducible():
    cs = [quoted(1), quoted(2)]
    h = [receipt(DAY, cs)]
    first = mp.learn(h, NOW, lambda c: (2, 0) if c["candidate_id"] == "1" else (0, 2))
    scores = {x["candidate_id"]: tuple(x["score"]) for x in first["training_outcomes"]}
    second = mp.learn(h, NOW, lambda c: scores[c["candidate_id"]])
    assert first == second
