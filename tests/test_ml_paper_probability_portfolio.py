"""Operator-approved multiple chance-first accas share one PAPER risk budget.

No added probability floor: every pair still needs the existing local evidence.
Selection is best-remaining-pair first, not a global portfolio-profit optimiser.
"""

import itertools
import math
import random
from copy import deepcopy
from datetime import timedelta

import pytest
from test_ml_paper_hit_probability import DAY, NOW, new_slate, signature, supported, warm
from test_ml_paper_rolling import run

from edgefactory import ml_paper as mp
from edgefactory import ml_paper_probability as hp

OBJECTIVE = "highest_ticket_hit_probability_disjoint_v2"
LEGACY_OBJECTIVE = "highest_ticket_hit_probability_v1"


def choose(rows, *, bank=100., available=None, prior=None, objective=OBJECTIVE):
    diagnostics = {}
    result = mp.select_accas(
        rows, bank if available is None else available, diagnostics=diagnostics,
        concentration={"total_bank_units": bank, "prior_open_fixture_micro_units": prior or {}},
        objective=objective,
    )
    return result, diagnostics


def multi_slate(now=NOW, ids=(1, 2, 3, 4, 5, 6)):
    rows = new_slate(now, ids=ids)
    for i, row in enumerate(rows):
        p = .95 - i * .035
        row["odds"] = 1.01
        row["statistical_profile"]["ml_inputs"]["values"].update(
            forecast_1x2_home_mean=p, forecast_1x2_draw_mean=(1-p)/3,
            forecast_1x2_away_mean=(1-p)*2/3,
        )
    return rows


def test_builds_all_supported_disjoint_pairs_not_just_one_and_no_new_hit_floor():
    rows = [supported(i, p=p, odds=1.02, lower=.1)
            for i, p in enumerate((.96, .95, .8, .6, .3, .2), 1)]
    before = deepcopy(rows)
    plan, diagnostics = choose(rows)
    assert [signature(a) for a in plan] == [("1", "2"), ("3", "4"), ("5", "6")]
    assert [a["selection_rank"] for a in plan] == [1, 2, 3]
    assert [mp._stake_micro_units(a["stake_units"]) for a in plan] == [33334, 33333, 33333]
    assert sum(mp._stake_micro_units(a["stake_units"]) for a in plan) == 100000
    assert all(len(a["legs"]) == 2 and a["estimated_ev"] < 0 for a in plan)
    assert plan[-1]["probability_estimate"] == pytest.approx(.06)  # no invented 50% gate
    assert len({tuple(c["fixture"]) for a in plan for c in a["legs"]}) == 6
    assert diagnostics["shared_publication_budget_micro_units"] == 100000
    assert diagnostics["selection_optimality"] == "each_best_remaining_pair_exact_not_global_portfolio_optimality"
    assert rows == before


def test_more_tickets_split_the_budget_instead_of_multiplying_exposure():
    rows = [supported(i, p=.99-i/100, lower=.1) for i in range(1, 9)]
    single, _ = choose(rows[:2])
    multiple, _ = choose(rows)
    assert len(single) == 1 and len(multiple) == 4
    assert single[0]["stake_units"] == .1
    assert all(a["stake_units"] == .025 for a in multiple)
    assert sum(mp._stake_micro_units(a["stake_units"]) for a in multiple) == 100000
    assert signature(single[0]) == signature(multiple[0])


def test_other_books_and_other_markets_cannot_reuse_an_already_selected_fixture():
    rows = [supported(i, p=.99-i/100) for i in range(1, 7)]
    alternative = deepcopy(rows[0])
    alternative.update(candidate_id="alternative-book", book="Second book", probability=.999)
    other = deepcopy(rows[2])
    other.update(candidate_id="other-market", probability=.1, market="btts_yes", selection="yes")
    rows += [alternative, supported(99, p=.999, book="Second book"), other]
    plan, _ = choose(rows)
    assert signature(plan[0]) == ("99", "alternative-book")
    fixtures = [tuple(c["fixture"]) for a in plan for c in a["legs"]]
    assert len(fixtures) == len(set(fixtures))
    assert "1" not in {c["candidate_id"] for a in plan for c in a["legs"]}
    assert "other-market" not in {c["candidate_id"] for a in plan for c in a["legs"]}


def test_caps_reduce_only_the_affected_share_and_never_refill_other_accas():
    rows = [supported(i, p=.99-i/100) for i in range(1, 5)]
    prior = {tuple(rows[0]["fixture"]): 4_990_000}
    plan, _ = choose(rows, prior=prior)
    assert [a["stake_units"] for a in plan] == [.01, .05]
    blocked, _ = choose(rows, prior={tuple(rows[0]["fixture"]): 5_000_000})
    assert len(blocked) == 1 and signature(blocked[0]) == ("3", "4")
    assert blocked[0]["selection_rank"] == 2 and blocked[0]["stake_units"] == .05


def test_micro_unit_precision_can_limit_count_but_never_round_budget_up():
    rows = [supported(i, p=.99-i/100) for i in range(1, 9)]
    plan, _ = choose(rows, bank=.003)
    assert len(plan) == 3
    assert [a["selection_rank"] for a in plan] == [1, 2, 3]
    assert [a["stake_units"] for a in plan] == [.000001]*3
    assert not choose(rows, bank=.0009)[0]
    free_limited, _ = choose(rows, available=.000002)
    assert len(free_limited) == 2 and sum(mp._stake_micro_units(a["stake_units"]) for a in free_limited) == 2


def test_every_rank_matches_exhaustive_best_remaining_oracle_under_shuffles():
    rng = random.Random(131126)
    for _ in range(15):
        rows = [supported(i, p=rng.uniform(.1, .99), odds=rng.uniform(1.01, 20.),
                          lower=.05, book="Book A" if i % 3 else "Book B")
                for i in range(16)]
        rows[4]["fixture"] = list(rows[1]["fixture"])
        rows[7]["fixture"][1] = rows[2]["fixture"][1]
        remaining, expected = list(rows), []
        while True:
            pairs = [pair for pair in itertools.combinations(remaining, 2)
                     if pair[0]["book"].casefold() == pair[1]["book"].casefold()
                     and not set(pair[0]["fixture"][1:]) & set(pair[1]["fixture"][1:])]
            if not pairs:
                break
            best = min(pairs, key=lambda pair: (
                -math.prod(c["probability"] for c in pair), -math.prod(c["odds"] for c in pair),
                tuple(sorted(c["candidate_id"] for c in pair)), pair[0]["book"].casefold()))
            expected.append(tuple(sorted(c["candidate_id"] for c in best)))
            used = {tuple(c["fixture"]) for c in best}
            remaining = [c for c in remaining if tuple(c["fixture"]) not in used]
        for _ in range(3):
            rng.shuffle(rows)
            plan, _ = choose(rows)
            assert [signature(a) for a in plan] == expected
            assert [a["probability_estimate"] for a in plan] == sorted(
                (a["probability_estimate"] for a in plan), reverse=True)


def test_missing_evidence_and_unpairable_leftovers_never_become_extra_tickets():
    a, b = supported(1, p=.9), supported(2, p=.8)
    unsupported = supported(3, p=.999)
    unsupported["admission"].update(fixtures=0, reason="no_local_evidence", probability_lower=0.)
    rows = [a, b, unsupported, supported(4, book="Unpaired book")]
    plan, _ = choose(rows)
    assert len(plan) == 1 and signature(plan[0]) == ("1", "2")
    assert plan[0]["stake_units"] == .1
    assert not choose([unsupported, rows[-1]])[0]


def test_replay_drops_a_share_without_rebuilding_or_funding_weaker_pairs():
    rows = [supported(i, p=.99-i/100) for i in range(1, 7)]
    original, _ = choose(rows)
    pending = dict(original[0], profit_units=None)
    report = {"paper_bank_units": 100., "paper_committed_units": pending["stake_units"],
              "paper_free_units": 100.-pending["stake_units"], "history": [{"accas": [pending]}]}
    diagnostics = {}
    plan, audit = mp._size_publication_accas(rows, report, diagnostics, objective=OBJECTIVE)
    assert [a["selection_rank"] for a in plan] == [2, 3]
    assert [a["stake_units"] for a in plan] == [.033333, .033333]
    assert diagnostics["opportunity_replay"]["dropped_acca_count"] == 1
    assert diagnostics["opportunity_replay"]["released_stake_units"] == .033334
    assert audit["published_stake_micro_units"] == 66666


def test_shared_aggregate_headroom_scales_all_shares_down_with_no_refill():
    rows = [supported(i, p=.99-i/100) for i in range(1, 7)]
    older, _ = choose([supported(90), supported(91)])
    pending = dict(older[0], stake_units=24.999997, profit_units=None)
    report = {"paper_bank_units": 100., "paper_committed_units": pending["stake_units"],
              "paper_free_units": 100.-pending["stake_units"], "history": [{"accas": [pending]}]}
    plan, audit = mp._size_publication_accas(rows, report, {}, objective=OBJECTIVE)
    assert [a["stake_units"] for a in plan] == [.000001]
    # Integer proportional floors leave the remainder idle, never refill.
    assert audit["published_stake_micro_units"] == 1
    assert plan[0]["selection_rank"] == 1
    report.update(paper_committed_units=25., paper_free_units=75.)
    assert not mp._size_publication_accas(rows, report, {}, objective=OBJECTIVE)[0]


def test_v1_helpers_keep_one_ticket_and_their_original_risk_semantics():
    rows = [supported(i, p=.99-i/100) for i in range(1, 7)]
    plan, _ = choose(rows, objective=LEGACY_OBJECTIVE)
    assert len(plan) == 1 and plan[0]["stake_units"] == .1
    assert signature(plan[0]) == ("1", "2")
    assert hp.policy(LEGACY_OBJECTIVE)["max_accas_per_publication"] == 1
    assert hp.policy(OBJECTIVE)["max_accas_per_publication"] is None
    assert "risk_budget_scope" not in hp.policy(LEGACY_OBJECTIVE)


def test_production_publication_replays_all_pairs_and_reports_shared_risk(tmp_path):
    from test_ml_paper_admission import score
    warm(tmp_path)
    row = run(tmp_path, NOW, multi_slate(), lookup=score)
    assert row["policy"]["selection_objective"] == OBJECTIVE
    assert row["policy"]["minimum_ticket_hit_probability"] is None
    assert len(row["accas"]) == 3
    assert [a["selection_rank"] for a in row["accas"]] == [1, 2, 3]
    assert sum(mp._stake_micro_units(a["stake_units"]) for a in row["accas"]) == 100000
    assert mp.receipts(tmp_path)[-1] == row
    report = mp.performance(mp.receipts(tmp_path), score)
    assert report["pending_accas"] == 3 and report["paper_committed_units"] == .1
    text = mp.render_daily_card([row], report)
    assert text.count("[PAPER ACCA #") == 3
    assert text.count("estimated hit") == text.count("estimated miss") == 3
    assert "shared across" in text and "per publication" in text
    assert "independence assumed; not calibrated or guaranteed" in text
    assert "shared across" in mp.render_card(row)
    assert "shared across" in mp.render_performance(report)


def test_frozen_single_ticket_receipts_stay_readable_when_v2_is_active(tmp_path, monkeypatch):
    from test_ml_paper_admission import score
    warm(tmp_path)
    with monkeypatch.context() as legacy:
        legacy.setattr(mp, "_selection_objective", lambda _: LEGACY_OBJECTIVE)
        old = run(tmp_path, NOW, multi_slate(), lookup=score)
    old_path = mp.rolling_receipt_path(tmp_path, old)
    original_bytes = old_path.read_bytes()
    assert len(old["accas"]) == 1 and old["accas"][0]["stake_units"] == .1
    later = NOW + timedelta(minutes=1)
    new = run(tmp_path, later, multi_slate(later, ids=(11, 12, 13, 14, 15, 16)), lookup=score)
    assert len(new["accas"]) == 3 and new["policy"]["selection_objective"] == OBJECTIVE
    assert old in mp.receipts(tmp_path) and old_path.read_bytes() == original_bytes
    assert "Chance-first" in mp.render_card(old)
    assert "Frozen model" not in mp.render_daily_card([old])
    with pytest.raises(ValueError, match="current portfolio policy"):
        mp._publish_receipt(tmp_path / "forged-new-v1.json", old)


@pytest.mark.parametrize("damage", ["budget", "refill", "order", "rank", "reuse", "weaker", "count", "policy"])
def test_rehashed_v2_receipts_cannot_forge_ranked_selection_or_shared_risk(tmp_path, damage):
    from test_ml_paper_admission import score
    warm(tmp_path)
    row = run(tmp_path, NOW, multi_slate(), lookup=score)
    assert len(row["accas"]) == 3
    bad = deepcopy(row)
    if damage == "budget":
        bad["search"]["shared_publication_budget_micro_units"] *= 2
        for a in bad["accas"]:
            a["portfolio_allocation"]["shared_publication_budget_micro_units"] *= 2
            a["portfolio_allocation"]["pre_cap_share_micro_units"] *= 2
            a["stake_units"] *= 2
    elif damage == "refill":
        bad["accas"] = bad["accas"][1:]
        bad["accas"][0]["stake_units"] = .066667
    elif damage == "order":
        bad["accas"].reverse()
    elif damage == "rank":
        bad["accas"][1]["selection_rank"] = True
    elif damage in {"reuse", "weaker"}:
        legs = [bad["accas"][0]["legs"][0], bad["accas"][1]["legs"][1]]
        replacement = hp.best_acca(legs)
        target = bad["accas"][1 if damage == "reuse" else 0]
        target.update(replacement)
    elif damage == "count":
        for a in bad["accas"]:
            a["portfolio_allocation"]["supported_acca_count"] = 2
    else:
        bad["policy"]["max_accas_per_publication"] = 1
    # Rebuild generic concentration proofs to exercise independent selection /
    # shared allocation checks, not merely an unchanged checksum or total.
    bad["accas"], audit = mp.project_fixture_stakes(bad["accas"], total_bank_units=100.)
    bad["accas"], bad["fixture_concentration"] = mp._scale_aggregate_stakes(
        bad["accas"], audit, bank=100., committed=0., available=100.)
    bad["sha256"] = mp.digest({k: v for k, v in bad.items() if k != "sha256"})
    with pytest.raises(ValueError):
        mp.validate_record(bad, DAY)


def test_daily_multi_draft_seal_keeps_probability_rank_and_never_increases_risk(tmp_path):
    from test_ml_paper_admission import score

    import scripts.auto_tickets as at
    warm(tmp_path)
    before_cutoff = NOW.replace(hour=6)
    draft = mp.capture(
        {"date": DAY, "build_at": before_cutoff.isoformat(), "slate": multi_slate(before_cutoff)},
        root=tmp_path, now=before_cutoff, index={}, score_lookup=score,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection,
    )
    assert draft["status"] == "draft_not_yet_frozen" and len(draft["accas"]) == 3
    frozen = mp.capture(
        {}, root=tmp_path, now=NOW, index={}, score_lookup=score,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection,
    )
    assert frozen["draft_sha256"] == draft["sha256"]
    assert [signature(a) for a in frozen["accas"]] == [signature(a) for a in draft["accas"]]
    assert [a["selection_rank"] for a in frozen["accas"]] == [1, 2, 3]
    assert sum(mp._stake_micro_units(a["stake_units"]) for a in frozen["accas"]) <= 100000
    assert mp.receipts(tmp_path)[-1] == frozen


def test_multi_replacement_of_v1_releases_old_reservation_without_increasing_risk(tmp_path, monkeypatch):
    from test_ml_paper_admission import score
    warm(tmp_path)
    with monkeypatch.context() as legacy:
        legacy.setattr(mp, "_selection_objective", lambda _: LEGACY_OBJECTIVE)
        old = run(tmp_path, NOW, multi_slate(), lookup=score)
    old_path = mp.rolling_receipt_path(tmp_path, old)
    before = old_path.read_bytes()
    later = NOW + timedelta(minutes=1)
    new = run(tmp_path, later, multi_slate(later), lookup=score,
              supersede=[{"receipt_sha256": old["sha256"], "acca_index": 1}],
              replacement_reason="Operator chose multiple evidence-supported chance-first accas.")
    assert len(new["accas"]) == 3 and new["paper_pending_reserved_at_decision"] == 0.
    report = mp.performance(mp.receipts(tmp_path), score)
    assert report["paper_committed_units"] == .1 and report["pending_accas"] == 3
    assert report["superseded_accas"] == 1 and report["profit_units"] == 0
    assert old_path.read_bytes() == before
    active, withdrawn = mp.render_daily_card([old, new], report).split("SUPERSEDED BEFORE KICKOFF", 1)
    assert active.count("[PAPER ACCA #") == 3
    assert "not a win or loss" in withdrawn


@pytest.mark.parametrize("settled_score", [(0, 2), (2, 0)])
def test_sealing_multi_draft_rechecks_bank_but_never_increases_original_shares(tmp_path, settled_score):
    from test_ml_paper import candidate, receipt
    from test_ml_paper_admission import score

    import scripts.auto_tickets as at
    warm(tmp_path)
    loss_day = "2026-11-10"
    legs = [candidate(i, date=loss_day) for i in (90, 91)]
    prior = receipt(loss_day, legs, [{"legs": legs, "odds": 4., "stake_units": 10.}])
    prior["sha256"] = mp.digest(prior)
    mp._write_once(mp.receipt_path(tmp_path, loss_day), prior)
    before_cutoff = NOW.replace(hour=6)
    draft = mp.capture(
        {"date": DAY, "build_at": before_cutoff.isoformat(), "slate": multi_slate(before_cutoff)},
        root=tmp_path, now=before_cutoff, index={}, score_lookup=score,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection,
    )
    assert len(draft["accas"]) == 3 and draft["paper_bank_at_decision"] == 100.
    lookup = lambda c: settled_score if c["date"] == loss_day else score(c)
    frozen = mp.capture(
        {}, root=tmp_path, now=NOW, index={}, score_lookup=lookup,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection,
    )
    expected_budget = 90000 if settled_score == (0, 2) else 100000
    assert frozen["paper_bank_at_decision"] == (90. if settled_score == (0, 2) else 130.)
    assert sum(mp._stake_micro_units(a["stake_units"]) for a in frozen["accas"]) == expected_budget
    assert all(a["stake_units"] <= d["stake_units"] for a, d in zip(frozen["accas"], draft["accas"]))
    assert mp.receipts(tmp_path)[-1] == frozen


@pytest.mark.parametrize("bad", [None, 1, "bad", [DAY, [], "away"], [DAY, "same", "same"]])
def test_malformed_fixture_leftovers_never_break_valid_extra_pairs(bad):
    rows = [supported(i) for i in range(1, 5)]
    broken = supported(99, p=.999)
    broken["fixture"] = bad
    plan, _ = choose([*rows, broken])
    assert len(plan) == 2
    assert "99" not in {c["candidate_id"] for a in plan for c in a["legs"]}


@pytest.mark.parametrize("count,budget", [(True, 100), (2, True), (-1, 10), (2, -1), (2, float("inf"))])
def test_shared_budget_helper_rejects_bad_numeric_inputs(count, budget):
    with pytest.raises(ValueError, match="shared budget"):
        hp.budget_shares(count, budget)


def test_publisher_does_not_reload_large_history_after_rolling_reports_are_written(tmp_path, monkeypatch):
    from test_ml_paper_admission import score
    warm(tmp_path)
    row = run(tmp_path, NOW, multi_slate(), lookup=score)
    read = mp.receipts
    calls = []

    def counted(root):
        calls.append(root)
        assert len(calls) <= 2, "publisher must not reload all receipts while retaining its validated history"
        return read(root)

    monkeypatch.setattr(mp, "receipts", counted)
    report = mp.publish(tmp_path, score)
    assert len(calls) == 2  # migration validation, then the report's own snapshot
    assert report["pending_accas"] == 3
    assert (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text() == mp.render_daily_card([row], report)
