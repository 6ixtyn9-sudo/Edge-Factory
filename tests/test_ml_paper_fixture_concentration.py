"""Approved forward-only gross fixture stake budget; all writes are temp-only."""

import json
import math
import random
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from test_ml_paper import DAY, FREEZE, NOW, candidate, context, pick, receipt, run_capture
from test_ml_paper_redteam import sign
from test_ml_paper_rolling import run, slate

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp
from edgefactory.identity import source_team_key

ROOT = Path(__file__).resolve().parents[1]


def leg(i, *, fixture_id=None, book="Pinnacle", market="1x2", selection="home", odds=2.0, p=0.7):
    """A canonical leg; fixture_id may intentionally repeat across accas/books."""
    fixture_id = i if fixture_id is None else fixture_id
    home, away = f"Home Club {fixture_id}", f"Away Club {fixture_id}"
    c = candidate(i, odds=odds, p=p, market=market, book=book)
    c.update(home=home, away=away, selection=selection,
             fixture=[DAY, source_team_key(home), source_team_key(away)])
    return c


def acca(stake, legs):
    return {
        "legs": legs, "stake_units": stake, "book": legs[0]["book"],
        "odds": math.prod(c["odds"] for c in legs),
        "probability_estimate": math.prod(c["probability"] for c in legs),
    }


def exposure(plan):
    out = {}
    for a in plan:
        for f in {tuple(c["fixture"]) for c in a["legs"]}:
            out[f] = out.get(f, 0) + mp._stake_micro_units(a["stake_units"])
    return out


def seed_prior(root, *, fixture_id=90, stake=24.0, day="2026-11-01"):
    cs = [candidate(900 + j, date=day) for j in range(2)]
    for j, c in enumerate(cs):
        home, away = f"Home Club {fixture_id + j}", f"Away Club {fixture_id + j}"
        c.update(home=home, away=away,
                 fixture=[day, source_team_key(home), source_team_key(away)])
    row = receipt(day, cs, [{"legs": cs, "odds": 4.0, "stake_units": stake}])
    row["sha256"] = mp.digest(row)
    path = mp.receipt_path(root, day)
    mp._write_once(path, row)
    return path, path.read_bytes(), row


def signature(a):
    return tuple(sorted(c["candidate_id"] for c in a["legs"]))


def test_same_outcome_across_accas_and_books_counts_gross_stake():
    shared = [leg(10 + i, fixture_id=1, book=b) for i, b in enumerate(("A", "B", "C"))]
    plan = [acca(stake, [shared[i], leg(20 + i, book=b)])
            for i, (stake, b) in enumerate(zip((4.0, 3.0, 2.0), ("A", "B", "C")))]
    projected, audit = mp.project_fixture_stakes(plan, total_bank_units=100.0)
    fixture = tuple(shared[0]["fixture"])
    assert exposure(projected)[fixture] == 4_999_999
    assert [a["stake_units"] for a in projected] == [2.222222, 1.666666, 1.111111]
    assert audit["released_stake_micro_units"] == 4_000_001
    assert all(a["stake_units"] <= b["stake_units"] for a, b in zip(projected, plan))


def test_different_markets_and_opposite_sides_do_not_net():
    f = 1
    legs = [
        leg(1, fixture_id=f, market="1x2", selection="home"),
        leg(2, fixture_id=f, market="1x2", selection="away"),
        leg(3, fixture_id=f, market="btts_yes", selection="yes"),
    ]
    plan = [acca(3.0, [legs[0], leg(4)]), acca(3.0, [legs[1], leg(5)]),
            acca(1.0, [legs[2], leg(6)])]
    projected, _ = mp.project_fixture_stakes(plan, total_bank_units=100.0)
    assert exposure(projected)[tuple(legs[0]["fixture"])] == 4_999_999
    assert len(projected) == 3  # reuse remains allowed; it is not one-acca-per-fixture


def test_single_oversized_acca_is_still_capped():
    plan = [acca(13.0, [leg(1), leg(2)])]
    projected, audit = mp.project_fixture_stakes(plan, total_bank_units=100.0)
    assert projected[0]["stake_units"] == 5.0
    assert audit["published_stake_micro_units"] == 5_000_000
    assert audit["released_stake_micro_units"] == 8_000_000


def test_overlapping_fixture_budgets_hold_simultaneously_and_are_order_independent():
    plan = [acca(6.0, [leg(1), leg(2)]), acca(5.0, [leg(2), leg(3)]),
            acca(4.0, [leg(3), leg(4)]), acca(3.0, [leg(4), leg(1)])]
    projected, audit = mp.project_fixture_stakes(plan, total_bank_units=100.0)
    assert all(v <= 5_000_000 for v in exposure(projected).values())
    assert all(e["published_stake_micro_units"] <= e["residual_budget_micro_units"]
               for e in audit["fixtures"])
    shuffled = deepcopy(plan)
    random.Random(17).shuffle(shuffled)
    other, other_audit = mp.project_fixture_stakes(shuffled, total_bank_units=100.0)
    assert {signature(a): a["stake_units"] for a in projected} == {
        signature(a): a["stake_units"] for a in other}
    assert audit["fixtures"] == other_audit["fixtures"]


@pytest.mark.parametrize("prior", [5_000_000, 6_000_000])
def test_prior_open_exposure_and_grandfathering_leave_zero_new_budget(prior):
    fixture = tuple(leg(1)["fixture"])
    plan = [acca(4.0, [leg(1), leg(2)])]
    projected, audit = mp.project_fixture_stakes(
        plan, total_bank_units=100.0, prior_open_fixture_micro_units={fixture: prior})
    assert projected == []
    entry = next(e for e in audit["fixtures"] if tuple(e["fixture"]) == fixture)
    assert entry["residual_budget_micro_units"] == 0
    assert entry["prior_open_stake_micro_units"] == prior
    assert entry["total_open_stake_micro_units"] == prior  # old position not resized


def test_prior_exposure_mirrors_performance_pending_resolved_and_missing_results():
    cs = [leg(i) for i in range(1, 7)]
    history = [receipt(DAY, cs, [
        {"legs": cs[:2], "odds": 4.0, "stake_units": 2.0},
        {"legs": cs[2:4], "odds": 4.0, "stake_units": 3.0},
        {"legs": cs[4:], "odds": 4.0, "stake_units": 4.0},
    ])]

    def lookup(c):
        i = int(c["candidate_id"])
        if i <= 2:
            return None
        if i == 3:
            return (0, 1)  # known loss settles even though leg 4 is missing
        if i == 4:
            return None
        return (2, 0)

    report = mp.performance(history, lookup)
    assert report["paper_committed_units"] == 2.0
    prior = mp._prior_open_fixture_micro_units(report)
    assert prior == {tuple(cs[0]["fixture"]): 2_000_000, tuple(cs[1]["fixture"]): 2_000_000}


def test_shrinking_bank_uses_total_bank_denominator():
    plan = [acca(13.0, [leg(1), leg(2)])]
    projected, audit = mp.project_fixture_stakes(plan, total_bank_units=50.0)
    assert projected[0]["stake_units"] == 2.5
    assert audit["fixtures"][0]["residual_budget_micro_units"] == 2_500_000


def test_limited_free_capital_and_aggregate_headroom_scale_after_projection(tmp_path):
    path, original, _ = seed_prior(tmp_path, stake=24.0)
    row = run(tmp_path)
    assert row["paper_bank_at_decision"] == 100.0
    assert row["paper_pending_reserved_at_decision"] == 24.0
    assert row["paper_available_at_decision"] == 76.0
    audit = row["fixture_concentration"]
    assert audit["fixture_projected_stake_micro_units"] == 5_000_000
    assert audit["published_stake_micro_units"] == 1_000_000
    assert audit["aggregate_budget_scale"] == pytest.approx(0.2)
    assert sum(a["stake_units"] for a in row["accas"]) == 1.0
    assert path.read_bytes() == original


@pytest.mark.parametrize("bank,limit", [
    (91.803197, 4_590_159), (100.0, 5_000_000), (0.000399, 19), (0.0004, 20),
    (19.999999, 999_999), (0.0, 0),
])
def test_exact_micro_unit_floor_boundaries(bank, limit):
    assert mp._fixture_limit_micro_units(bank) == limit
    assert mp._fixture_concentration_policy(bank)["fixture_limit_units"] == limit / 1e6


def test_non_grid_new_stake_is_rejected_not_silently_rounded_up():
    with pytest.raises(ValueError, match="micro-unit grid"):
        mp.project_fixture_stakes([acca(1.0000001, [leg(1), leg(2)])], total_bank_units=100.0)


def test_no_increase_or_refill_after_projection_then_aggregate_scaling():
    plan = [acca(6.0, [leg(1), leg(2)]), acca(6.0, [leg(2), leg(3)])]
    projected, audit = mp.project_fixture_stakes(plan, total_bank_units=100.0)
    final, final_audit = mp._scale_aggregate_stakes(
        projected, audit, bank=100.0, committed=24.0, available=76.0)
    assert 0 < final_audit["published_stake_micro_units"] <= 1_000_000
    assert all(a["stake_units"] <= b["stake_units"] for a, b in zip(final, projected))
    assert all(v <= 5_000_000 for v in exposure(final).values())
    assert final_audit["released_stake_micro_units"] == (
        12_000_000 - final_audit["published_stake_micro_units"])


def test_zero_aggregate_headroom_drops_stake_without_refill_or_error():
    plan = [acca(5.0, [leg(1), leg(2)])]
    projected, audit = mp.project_fixture_stakes(plan, total_bank_units=100.0)
    final, final_audit = mp._scale_aggregate_stakes(
        projected, audit, bank=100.0, committed=100.0, available=0.0)
    assert final == []
    assert final_audit["published_stake_micro_units"] == 0
    assert final_audit["released_stake_micro_units"] == 5_000_000
    assert final_audit["dropped_acca_count"] == 1


def test_rolling_writer_enforces_declares_and_validates_policy(tmp_path):
    row = run(tmp_path)
    mp.validate_record(row, DAY)
    policy = row["policy"]["fixture_concentration"]
    assert policy["id"] == mp.FIXTURE_CONCENTRATION_POLICY
    assert policy["max_fixture_stake_fraction"] == 0.05
    assert policy["denominator"] == "total_paper_bank_at_decision"
    assert policy["fixture_limit_micro_units"] == 5_000_000
    assert row["search"]["published_portfolio_optimality_proven"] is False
    assert "fixture_concentration" not in row["accas"][0]["portfolio_allocation"]
    assert "4.590159" not in mp.render_card(row)  # this bank is 100, not the incident bank
    assert "5.0% of TOTAL paper bank" in mp.render_card(row)


def test_legacy_first_freeze_writer_enforces_policy(tmp_path):
    when = FREEZE + timedelta(minutes=5)
    rows = [pick(1), pick(2)]
    for row in rows:
        row.update(as_of=when.isoformat(), kickoff_utc=(when + timedelta(hours=3)).isoformat(),
                   odds_captured_at=(when - timedelta(minutes=1)).isoformat())
    frozen = run_capture(tmp_path, dict(context(rows), build_at=when.isoformat()), now=when)
    assert frozen["freeze_basis"] == mp.ACTUAL_RUN_FREEZE
    assert frozen["policy"]["fixture_concentration"]["fixture_limit_micro_units"] == 5_000_000
    assert all(v <= 5_000_000 for v in exposure(frozen["accas"]).values())
    mp.validate_record(frozen, DAY)


def test_legacy_freeze_reserves_earlier_same_day_rolling_commitments(tmp_path):
    first = run(tmp_path)
    when = FREEZE + timedelta(minutes=5)
    rows = [pick(3), pick(4)]
    for row in rows:
        row.update(as_of=when.isoformat(), kickoff_utc=(when + timedelta(hours=3)).isoformat(),
                   odds_captured_at=(when - timedelta(minutes=1)).isoformat())
    frozen = run_capture(tmp_path, dict(context(rows), build_at=when.isoformat()), now=when)
    assert frozen["paper_pending_reserved_at_decision"] == sum(
        a["stake_units"] for a in first["accas"])
    assert frozen["policy"]["fixture_concentration"]["fixture_limit_micro_units"] == 5_000_000
    mp.validate_record(frozen, DAY)


def test_legacy_draft_seal_enforces_policy_and_preserves_draft_hash(tmp_path):
    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    frozen = run_capture(tmp_path, {}, now=FREEZE)
    assert frozen["draft_sha256"] == draft["sha256"]
    assert frozen["policy"]["fixture_concentration"]["fixture_limit_micro_units"] == 5_000_000
    assert all(v <= 5_000_000 for v in exposure(frozen["accas"]).values())
    mp.validate_record(frozen, DAY)


def test_pre_policy_concentrated_draft_is_reduced_only_at_new_publication(tmp_path):
    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    # Simulate a genuine pre-policy draft: no declaration, original concentrated stake.
    draft["policy"].pop("fixture_concentration")
    draft.pop("fixture_concentration")
    draft["accas"][0]["stake_units"] = 13.0
    draft["accas"][0]["stake_fraction_of_free_bank"] = 0.13
    draft["sha256"] = mp.digest({k: v for k, v in draft.items() if k != "sha256"})
    state = mp._read_state(tmp_path)
    state["pending_by_date"][DAY] = draft
    mp.state_path(tmp_path).write_text(json.dumps(state))
    draft_bytes = mp.state_path(tmp_path).read_bytes()
    frozen = run_capture(tmp_path, {}, now=FREEZE)
    assert frozen["draft_sha256"] == draft["sha256"]
    assert frozen["accas"][0]["stake_units"] == 5.0
    assert frozen["fixture_concentration"]["released_stake_micro_units"] == 8_000_000
    assert mp.state_path(tmp_path).read_bytes() == draft_bytes


def test_legacy_seal_with_exhausted_shared_capital_publishes_capped_no_bet(tmp_path):
    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    path, original, _ = seed_prior(tmp_path, fixture_id=90, stake=100.0)
    frozen = run_capture(tmp_path, {}, now=FREEZE)
    assert frozen["status"] == "no_paper_bet" and not frozen["accas"]
    assert frozen["draft_sha256"] == draft["sha256"]
    assert frozen["paper_pending_reserved_at_decision"] == 100.0
    assert frozen["paper_available_at_decision"] == 0.0
    assert frozen["fixture_concentration"]["published_stake_micro_units"] == 0
    assert path.read_bytes() == original
    mp.validate_record(frozen, DAY)


def test_missed_freeze_writer_declares_empty_policy(tmp_path):
    frozen = run_capture(tmp_path, context([pick(1), pick(2)]), now=FREEZE + timedelta(hours=4))
    assert frozen["status"] == "missed_freeze_no_paper_bet"
    assert frozen["policy"]["fixture_concentration"]["fixture_limit_micro_units"] == 5_000_000
    assert frozen["fixture_concentration"]["published_stake_micro_units"] == 0
    mp.validate_record(frozen, DAY)


def test_rolling_expiry_rebuild_still_enforces_policy(tmp_path, monkeypatch):
    start, published = NOW, NOW + timedelta(minutes=2)
    rows = slate(start, ids=(1, 2, 3))
    rows[0]["odds_captured_at"] = (start - timedelta(hours=12) + timedelta(minutes=1)).isoformat()
    times = iter([start, published, published])

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(times)

    monkeypatch.setattr(mp, "datetime", Clock)
    row = mp.capture_rolling(
        {"build_at": start.isoformat(), "slate": rows}, root=tmp_path,
        score_lookup=lambda c: None, kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection, index={})
    assert row["rejections"]["quote_or_kickoff_expired_during_build"] == 1
    assert len(row["candidates"]) == 2
    assert row["policy"]["fixture_concentration"]["fixture_limit_micro_units"] == 5_000_000
    assert all(v <= 5_000_000 for v in exposure(row["accas"]).values())
    mp.validate_record(row, DAY)


def test_cross_publication_recommit_exclusion_survives_settlement(tmp_path):
    first = run(tmp_path)
    original = mp.rolling_receipt_path(tmp_path, first).read_bytes()
    later = NOW + timedelta(minutes=1)
    assert run(tmp_path, later, slate(NOW), lookup=lambda c: (2, 0)) is None
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == original


def test_repeated_input_deduplication_and_prior_exposure_identity(tmp_path):
    run(tmp_path, rows=[])
    assert run(tmp_path, NOW + timedelta(seconds=1), []) is None
    left, right = tmp_path / "left", tmp_path / "right"
    seed_prior(left, fixture_id=90, stake=1.0)
    seed_prior(right, fixture_id=95, stake=1.0)
    a = run(left)
    b = run(right)
    assert a["paper_bank_at_decision"] == b["paper_bank_at_decision"]
    assert a["paper_pending_reserved_at_decision"] == b["paper_pending_reserved_at_decision"]
    assert a["snapshot_sha256"] != b["snapshot_sha256"]


@pytest.mark.parametrize("damage", [
    "fraction", "policy_id", "limit", "missing_audit", "exposure", "order", "count",
])
def test_malformed_new_policy_metadata_fails_closed(tmp_path, damage):
    row = deepcopy(run(tmp_path))
    policy = row["policy"]["fixture_concentration"]
    if damage == "fraction":
        policy["max_fixture_stake_fraction"] = 0.10
    elif damage == "policy_id":
        policy["id"] = "unknown"
    elif damage == "limit":
        policy["fixture_limit_micro_units"] += 1
    elif damage == "missing_audit":
        row.pop("fixture_concentration")
    elif damage == "exposure":
        row["fixture_concentration"]["fixtures"][0]["published_stake_micro_units"] += 1
    elif damage == "order":
        row["fixture_concentration"]["fixtures"].reverse()
    elif damage == "count":
        row["fixture_concentration"]["dropped_acca_count"] += 1
    with pytest.raises(ValueError):
        mp.validate_record(sign(row), DAY)


def test_production_writer_cannot_publish_an_undeclared_legacy_portfolio(tmp_path):
    row = deepcopy(run(tmp_path))
    row["policy"].pop("fixture_concentration")
    row.pop("fixture_concentration")
    row = sign(row)
    mp.validate_record(row, DAY)  # historical reader remains compatible
    path = mp.rolling_receipt_path(tmp_path / "new", row)
    with pytest.raises(ValueError, match="lacks fixture concentration policy"):
        mp._publish_receipt(path, row)
    assert not path.exists()


@pytest.mark.parametrize("name", [
    "autobets_ML_2026-11-03_20261103T060852964169Z.json",
    "autobets_ML_2026-11-03_20261103T061028343859Z.json",
])
def test_frozen_incident_receipts_remain_readable_and_byte_identical(name):
    path = ROOT / "localdata" / mp.RECEIPT_DIR / name
    original = path.read_bytes()
    row = json.loads(original)
    mp.validate_record(row, row["date"])
    assert "fixture_concentration" not in row.get("policy", {})
    assert "LEGACY STAKING" in mp.render_card(row)
    assert path.read_bytes() == original


def test_equivalent_candidate_ordering_has_identical_capped_allocation():
    rows = [candidate(i, p=0.72, odds=2.1, book=("A" if i < 4 else "B")) for i in range(1, 7)]
    concentration = {"total_bank_units": 100.0, "prior_open_fixture_micro_units": {}}
    first = mp.select_accas(rows, 100.0, concentration=concentration)
    shuffled = deepcopy(rows)
    random.Random(23).shuffle(shuffled)
    second = mp.select_accas(shuffled, 100.0, concentration=concentration)
    assert {signature(a): a["stake_units"] for a in first} == {
        signature(a): a["stake_units"] for a in second}


def test_large_incidence_projection_remains_bounded():
    plan = [acca(1.0, [leg(2 * i, fixture_id=(2 * i) % 100),
                       leg(2 * i + 1, fixture_id=(2 * i + 1) % 100)]) for i in range(3000)]
    projected, audit = mp.project_fixture_stakes(plan, total_bank_units=100.0)
    assert len(projected) == 3000
    assert len(audit["fixtures"]) == 100
    assert all(v <= 5_000_000 for v in exposure(projected).values())


def test_mutual_exclusivity_keeps_first_drops_overlapping_without_refill():
    plan = [acca(4.0, [leg(1), leg(2)]), acca(3.0, [leg(2), leg(3)]),
            acca(2.0, [leg(4), leg(5)])]
    kept, dropped = mp._mutually_exclusive_accas(plan)
    assert kept == plan[::2] and dropped == 1
    assert [a["stake_units"] for a in kept] == [4.0, 2.0]  # no redistribution
    assert not ({tuple(c["fixture"]) for c in kept[0]["legs"]}
                & {tuple(c["fixture"]) for c in kept[1]["legs"]})


def test_mutual_exclusivity_is_deterministic_and_publish_gate_fails_closed():
    plan = [acca(4.0, [leg(1), leg(2)]), acca(3.0, [leg(1), leg(3)])]
    assert mp._mutually_exclusive_accas(plan) == mp._mutually_exclusive_accas(deepcopy(plan))
    with pytest.raises(ValueError, match="not mutually exclusive"):
        mp._require_mutually_exclusive(plan)


def test_production_sizing_returns_pairwise_disjoint_accas():
    rows = [candidate(i, p=0.72, odds=2.1, book=("A" if i < 4 else "B")) for i in range(1, 7)]
    diagnostics = {}
    plan = mp.select_accas(rows, 100.0, diagnostics=diagnostics, concentration={
        "total_bank_units": 100.0, "prior_open_fixture_micro_units": {}})
    seen = set()
    for a in plan:
        fixtures = {tuple(c["fixture"]) for c in a["legs"]}
        assert not fixtures & seen
        seen |= fixtures
    assert diagnostics["mutual_exclusivity"]["rule"].startswith("pairwise_fixture_disjoint")
    assert (diagnostics["mutual_exclusivity"]["kept_acca_count"]
            + diagnostics["mutual_exclusivity"]["dropped_acca_count"]
            == diagnostics["mutual_exclusivity"]["input_acca_count"])


def test_sealed_pre_policy_draft_drops_overlapping_accas_at_publication(tmp_path):
    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    draft["policy"].pop("fixture_concentration")
    draft.pop("fixture_concentration")
    overlapping = deepcopy(draft["accas"][0])
    overlapping["legs"] = list(reversed(overlapping["legs"]))
    overlapping["stake_units"] = 3.0
    overlapping["stake_fraction_of_free_bank"] = 0.03
    draft["accas"][0]["stake_units"] = 13.0
    draft["accas"][0]["stake_fraction_of_free_bank"] = 0.13
    draft["accas"].append(overlapping)
    payload = {k: v for k, v in draft.items() if k != "sha256"}
    sealed = mp._concentrate_sealed_draft(payload, [], lambda c: None)
    assert len(sealed["accas"]) == 1
    assert sealed["accas"][0]["stake_units"] == 5.0
    assert sealed["search"]["mutual_exclusivity"]["dropped_acca_count"] == 1
    mp._require_mutually_exclusive(sealed["accas"])


def test_rolling_publication_accas_are_mutually_exclusive(tmp_path):
    row = run(tmp_path)
    seen = set()
    for a in row["accas"]:
        fixtures = {tuple(c["fixture"]) for c in a["legs"]}
        assert not fixtures & seen
        seen |= fixtures
    assert row["search"]["mutual_exclusivity"]["kept_acca_count"] == len(row["accas"])


def test_mutual_exclusivity_prefers_highest_stake_not_input_or_book_order():
    small = acca(1.0, [leg(1), leg(2)])
    large = acca(9.0, [leg(2), leg(3)])
    kept, dropped = mp._mutually_exclusive_accas([small, large])
    assert kept == [large] and dropped == 1
    kept2, dropped2 = mp._mutually_exclusive_accas([large, small])
    assert [signature(a) for a in kept2] == [signature(large)] and dropped2 == 1
