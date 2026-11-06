"""Complete outcome partitions, including unquoted sides, are not extra bets."""
from copy import deepcopy
import json
import math
from pathlib import Path

import pytest

from edgefactory import ml_paper as mp
from test_ml_paper import candidate, NOW
from test_ml_paper_rolling import run, slate

FIXTURE = Path(__file__).parent / "fixtures/ml_probability_partitions_2026-11-06.json"
WEIGHTS = [(h, a, (h + 1) * (a + 2)) for h in range(7) for a in range(7)]
LEARNER = {"status": "fitted_prior_paper_errors", "intercept": .1,
           "columns": [], "coef": [.6], "smoothing_factor": .8,
           "success_tilt": {}}


def event(market, side):
    c = candidate(1, market=market)
    c.update(selection=side, base_probability=mp.probability(WEIGHTS, market, side),
             base_partition=mp._base_partition(WEIGHTS, market))
    c["probability"] = c["base_probability"]
    return c


def test_actual_retained_example_exposes_and_repairs_over_100_percent():
    f = json.loads(FIXTURE.read_text())
    rows = deepcopy(f["candidates"])
    for c in rows:
        peers = [p for p in rows if p["fixture"] == c["fixture"]]
        if c["market"] == "1x2":
            partition = [(p["market"], p["selection"], p["base_probability"])
                         for p in peers if p["market"] == "1x2"]
        else:
            partition = [(p["market"], p["selection"], p["base_probability"])
                         for p in peers if p["market"] != "1x2"]
        c["base_partition"] = partition
    for fixture in {tuple(c["fixture"]) for c in rows}:
        three = [c for c in rows if tuple(c["fixture"]) == fixture and c["market"] == "1x2"]
        assert sum(c["probability"] for c in three) > 1.13
    mp.apply_learning(rows, f["learning"])
    for fixture in {tuple(c["fixture"]) for c in rows}:
        for categorical in (True, False):
            group = [c for c in rows if tuple(c["fixture"]) == fixture
                     and (c["market"] == "1x2") == categorical]
            assert sum(c["probability"] for c in group) == pytest.approx(1, abs=1e-12)
    draw = next(c for c in rows if c["fixture"][1] == "motorlublin" and c["selection"] == "draw")
    assert draw["pre_normalized_probability"] == pytest.approx(.4122192062548207)
    assert draw["probability"] == pytest.approx(.3570777698003118, abs=1e-12)
    assert json.loads(FIXTURE.read_text()) == f  # no rewrite of the evidence


@pytest.mark.parametrize("family", ["match", "home", "away"])
@pytest.mark.parametrize("line", ["05", "15", "25", "35", "45"])
def test_binary_totals_complements_sum_to_one(family, line):
    rows = [event(f"{family}_{direction}_{line}", direction) for direction in ("over", "under")]
    mp.apply_learning(rows, LEARNER)
    assert math.fsum(c["probability"] for c in rows) == pytest.approx(1, abs=1e-12)


def test_btts_yes_and_no_are_one_complete_partition():
    rows = [event("btts_yes", "yes"), event("btts_no", "no")]
    mp.apply_learning(rows, LEARNER)
    assert sum(c["probability"] for c in rows) == pytest.approx(1, abs=1e-12)


@pytest.mark.parametrize("market,side", [("1x2", "home"), ("1x2", "draw"),
    ("1x2", "away"), ("match_under_25", "under"), ("btts_no", "no"),
    ("double_chance", "1x"), ("double_chance", "x2"), ("double_chance", "12")])
def test_unquoted_outcomes_and_duplicate_books_cannot_change_denominator(market, side):
    single = [event(market, side)]
    board = [event("1x2", s) for s in ("home", "draw", "away")]
    board += [event("match_over_25", "over"), event("match_under_25", "under"),
              event("btts_yes", "yes"), event("btts_no", "no"), event(market, side)]
    duplicate = deepcopy(board[-1]); duplicate["book"] = "Another book"
    board.append(duplicate)
    mp.apply_learning(single, LEARNER); mp.apply_learning(board, LEARNER)
    assert board[-1]["probability"] == board[-2]["probability"] == single[0]["probability"]


@pytest.mark.parametrize("side,components", [("1x", ("home", "draw")),
    ("x2", ("draw", "away")), ("12", ("home", "away"))])
def test_double_chance_is_sum_of_normalized_1x2(side, components):
    rows = [event("1x2", s) for s in ("home", "draw", "away")]
    rows.append(event("double_chance", side))
    mp.apply_learning(rows, LEARNER)
    expected = sum(c["probability"] for c in rows[:-1] if c["selection"] in components)
    assert rows[-1]["probability"] == pytest.approx(expected)


def test_no_results_preserves_base_probabilities_exactly():
    rows = [event("1x2", s) for s in ("home", "draw", "away")]
    before = deepcopy(rows)
    mp.apply_learning(rows, {"status": "awaiting_prior_paper_results"})
    assert rows == before


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -.1, 1.1, True, None])
def test_malformed_partition_fails_closed(bad):
    c = event("1x2", "draw"); c["base_partition"][0][2] = bad
    with pytest.raises(ValueError, match="probability partition"):
        mp.apply_learning([c], LEARNER)


def test_incomplete_partition_is_not_normalized_over_available_sides():
    c = event("1x2", "draw"); c["base_partition"].pop()
    with pytest.raises(ValueError, match="probability partition"):
        mp.apply_learning([c], LEARNER)


def test_real_candidate_path_stores_unquoted_sides_before_learning(tmp_path, monkeypatch):
    monkeypatch.setattr(mp, "learn", lambda *args: deepcopy(LEARNER))
    record = run(tmp_path, NOW, slate())
    for c in record["candidates"]:
        assert len(c["base_partition"]) == 3
        assert c["probability_normalization"] == "complete_score_model_partition_v1"
        assert c["pre_normalized_probability"] > c["probability"]
    assert mp.receipts(tmp_path) == [record]


def test_selected_base_must_match_the_partition():
    c = event("1x2", "draw")
    c["base_probability"] += .01
    with pytest.raises(ValueError, match="candidate differs"):
        mp.apply_learning([c], LEARNER)


def test_complete_mass_on_wrong_outcomes_cannot_pass_as_a_partition():
    c = event("1x2", "draw")
    c["base_partition"][0][1] = "not_home"
    with pytest.raises(ValueError, match="incomplete base probability partition"):
        mp.apply_learning([c], LEARNER)


def test_duplicate_outcomes_cannot_pass_as_a_partition():
    c = event("1x2", "draw")
    c["base_partition"].append(deepcopy(c["base_partition"][0]))
    with pytest.raises(ValueError, match="incomplete base probability partition"):
        mp.apply_learning([c], LEARNER)
