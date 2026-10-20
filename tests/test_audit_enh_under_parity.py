"""Adversarial inputs: refuse invented prices/outcomes and favourable accounting."""
from copy import deepcopy
from enhancement_fixtures import IDENTITY, contract_pick
from datetime import datetime, timezone
import math

import pytest

from scripts import audit_enh_under_parity as audit
from edgefactory.enh_registry import check_enhancement_hit

UTC = timezone.utc
DECISION = datetime(2026, 10, 18, 14, tzinfo=UTC)
KICKOFF = datetime(2026, 10, 18, 16, tzinfo=UTC)


def quote(**overrides):
    return {"source": "oddspapi", "bookmaker": "Pinnacle", "market": "ou_3.5",
            "selection": "under", "odds": "1.40", "schema_version": "3",
            "captured_at": "2026-10-18T13:59:00+00:00", "kickoff": KICKOFF.isoformat(),
            **overrides}


@pytest.mark.parametrize("overrides, reason", [
    ({"captured_at": "2026-10-18T14:01:00Z"}, "after_decision"),
    ({"captured_at": "2026-10-18T13:59:00"}, "timestamp_missing"),
    ({"kickoff": "2026-10-18T16:30:00Z"}, "kickoff_mismatch"),
    ({"schema_version": "2"}, "old_schema"),
    ({"schema_version": "3.1"}, "old_schema"),
    ({"captured_at": "2026-10-18T09:59:00Z"}, "stale_oddspapi"),
    ({"odds": "nan"}, "invalid_price"),
    ({"odds": "inf"}, "invalid_price"),
    ({"odds": True}, "invalid_price"),
    ({"bookmaker": ""}, "no_book"),
    ({"source": "fair_donor"}, "source"),
])
def test_strict_quote_guards(overrides, reason):
    assert audit.valid_quote(quote(**overrides), "oddspapi", DECISION, KICKOFF) == reason


def test_post_kickoff_quote_cannot_enter_even_with_late_decision():
    late = datetime(2026, 10, 18, 17, tzinfo=UTC)
    assert audit.valid_quote(quote(captured_at=KICKOFF.isoformat()), "oddspapi", late, KICKOFF) == "after_kickoff"


def test_latest_available_quote_not_largest_past_or_future_quote():
    row = {"as_of": DECISION.isoformat(), "kickoff_utc": KICKOFF.isoformat()}
    raws = [("oddspapi", quote(captured_at="2026-10-18T13:00:00Z", odds="1.9")),
            ("oddspapi", quote(captured_at="2026-10-18T13:59:00Z", odds="1.4")),
            ("oddspapi", quote(captured_at="2026-10-18T14:10:00Z", odds="2.5"))]
    counts = audit.Counter()
    got = audit.quotes_for(row, raws, counts)
    assert got[("ou_3.5", "under")]["price"] == 1.4
    assert counts["after_decision"] == 1
    # A contradictory price at the SAME instant is ambiguous, not best-of.
    raws.append(("oddspapi", quote(captured_at="2026-10-18T13:59:00Z", odds="1.7")))
    assert audit.quotes_for(row, raws, audit.Counter()) == {}


def test_do_not_make_unders_from_winner_stats_or_stated_probabilities():
    assert audit.snapshot_rates({"statistical_comment": "Under 3.5: 99.0%",
                                 "enhancement_probability": .99,
                                 "recommended_enhancement": "match_under_35"}) == {}
    assert audit.snapshot_rates({"event_notes": [{"market": "match_over_25",
                                 "probability": .7, "engine": "hybrid_cohort"}]}) == {}
    rates = audit.snapshot_rates({"event_notes": [{"market": "match_over_25", "cohort_rate": .3}]})
    assert rates["match_under_25"] == pytest.approx(.7)
    assert audit.snapshot_rates({"event_notes": [{"market": "match_over_25", "cohort_rate": .3},
                                 {"market": "match_under_25", "cohort_rate": .3}]}) == {}


def test_counterfactual_selection_never_needs_result_and_requires_real_quote():
    rates = {"match_over_25": .6, "match_under_35": .8}
    quotes = {("ou_2.5", "over"): {"price": 1.5}, ("ou_3.5", "under"): {"price": 1.3}}
    thresholds = audit.legacy_thresholds()
    assert audit.choose(rates, quotes, thresholds, False)["market"] == "match_over_25"
    assert audit.choose(rates, quotes, thresholds, True)["market"] == "match_under_35"
    assert audit.choose(rates, {}, thresholds, True) is None
    assert audit.choose({"match_under_35": .91}, quotes, thresholds, True) is None
    assert audit.choose(rates, {("ou_3.5", "under"): {"price": 1.29}}, thresholds, True) is None


def card_case():
    metadata, plan, scores = {}, [], {}
    for i in range(2):
        match = f"Home{i} vs Away{i}"
        row = {"date": "2026-10-18", "home": f"Home{i}", "away": f"Away{i}"}
        metadata[(match, "under")] = {"market": "match_under_45", "row": row}
        scores[audit.identity(row)] = {(2, 2)}
        plan.append({"stake_pct": 12.5, "odds": 2.0,
                     "legs": [{"match": match, "pick": "under", "odds": 2.0}]})
    return plan, metadata, scores


def test_same_day_ticket_pnl_is_added_not_compounded():
    plan, metadata, scores = card_case()
    out = audit.evaluate_card(plan, metadata, scores)
    assert out["stake"] == 25
    assert out["net"] == 25
    assert out["log_growth"] == pytest.approx(math.log(1.25))
    # Wrong replay arithmetic would produce log(1.125 * 1.125).
    assert out["log_growth"] != pytest.approx(math.log(1.125**2))
    stressed = audit.evaluate_card(plan, metadata, scores, haircut=.05)
    assert stressed["net"] == pytest.approx(22.5)


def test_unknown_and_conflicting_scores_do_not_become_wins_or_drop_from_card():
    plan, metadata, scores = card_case()
    key = next(iter(scores))
    del scores[key]
    out = audit.evaluate_card(plan, metadata, scores)
    assert (out["bets"], out["resolved"], out["unknown"]) == (2, 1, 1)
    assert out["worst_net"] == 0
    assert out["best_net"] == 25
    assert out["log_growth"] is None
    scores[key] = {(2, 2), (4, 2)}
    assert audit.evaluate_card(plan, metadata, scores)["unknown"] == 1
    # Swapped sides / neighbouring dates are not substituted.
    row = deepcopy(metadata[next(iter(metadata))]["row"])
    row["home"], row["away"] = row["away"], row["home"]
    scores[audit.identity(row)] = {(0, 0)}
    assert audit.evaluate_card(plan, metadata, scores)["unknown"] == 1


def test_identical_arms_refuse_bootstrap_instead_of_claiming_precision():
    plan, metadata, scores = card_case()
    days = {"2026-10-18": audit.evaluate_card(plan, metadata, scores)}
    result = audit.paired_bootstrap(days, days)
    assert result["status"] == "NO_OP"
    assert result["valid_replicates"] == 0
    assert result["roi_gap_95pct"] is None


@pytest.mark.parametrize("total", range(12))
def test_new_under_45_has_a_real_settlement_rule_and_complements_over(total):
    for home in range(total + 1):
        away = total - home
        under = check_enhancement_hit("match_under_45", "home", home, away)
        over = check_enhancement_hit("match_over_45", "away", home, away)
        assert under is (total <= 4)
        assert over is (not under)


def archived_row(**overrides):
    return contract_pick({"date": "2026-10-18", "home": "A", "away": "B", "pick": "home", "avg_p": 65.0,
            "event_notes": [{"cohort_n": 200, "cohort_contract_id": IDENTITY,
                             "cohort_as_of_exclusive": "2026-10-18", "engine": "hybrid_cohort"}], **overrides})


def test_actual_selector_replay_uses_archived_rates_not_priors_or_current_warehouse():
    row = archived_row()
    rates = {"btts_yes": .60, "match_under_25": .75}
    quotes = {("btts", "yes"): {"price": 1.8}, ("ou_2.5", "under"): {"price": 1.4}}
    assert audit.production_choice(row, rates, quotes, False)["market"] == "btts_yes"
    out = audit.production_choice(row, rates, quotes, True)
    assert out["market"] == "match_under_25" and out["rate"] == .75
    assert audit.production_choice(row, rates, {}, True) is None
    # A missing counterpart price is NOT assigned a synthetic fair price.
    assert audit.production_choice(row, rates, {("ou_3.5", "under"): {"price": 10}}, True) is None


@pytest.mark.parametrize("notes", [[], [{"cohort_n": 99}], [{"cohort_n": True}],
                                   [{"cohort_n": 200}, {"cohort_n": 201}]])
def test_actual_selector_replay_refuses_missing_small_or_conflicting_n(notes):
    with pytest.raises(ValueError, match="cohort sample size"):
        audit.production_choice(archived_row(event_notes=notes), {"match_under_25": .75}, {}, True)


def test_actual_selector_replay_refuses_missing_conditioning_inputs():
    for change in ({"avg_p": None}, {"avg_p": "65"}, {"pick": ""}):
        with pytest.raises(ValueError):
            audit.production_choice(archived_row(**change), {"match_under_25": .75}, {}, True)


def test_actual_selector_replay_does_not_depend_on_rates_dictionary_tie_order():
    row = archived_row()
    quotes = {("btts", "yes"): {"price": 1.5}, ("ou_2.5", "under"): {"price": 1.5}}
    a = audit.production_choice(row, {"btts_yes": .8, "match_under_25": .8}, quotes, True)
    b = audit.production_choice(row, {"match_under_25": .8, "btts_yes": .8}, quotes, True)
    assert a == b and a["market"] == "match_under_25"


def test_actual_selector_replay_restores_environment_and_module_bindings_on_failure(monkeypatch):
    import os
    original = audit.pt.fetch_match_cohort
    monkeypatch.setenv(audit.pt.ENH_COHORT_PARITY_ENV, "sentinel")
    monkeypatch.setattr(audit.pt, "compute_dynamic_enhancement", lambda *a: 1/0)
    with pytest.raises(ZeroDivisionError):
        audit.production_choice(archived_row(), {"match_under_25": .75}, {}, True)
    assert os.environ[audit.pt.ENH_COHORT_PARITY_ENV] == "sentinel"
    assert audit.pt.fetch_match_cohort is original


def test_preselection_slippage_reselects_and_rebuilds_complete_cards():
    cases = []
    for home in ("A", "C"):
        row = archived_row(home=home)
        cases.append((row, {"btts_yes": .6, "match_under_25": .75},
                      {("btts", "yes"): {"price": 1.30}, ("ou_2.5", "under"): {"price": 2.0}}))
    out = audit.reselect_price_stress(cases, ["2026-10-18"], {}, .02)
    assert len(out["changed_fixture_choices"]) == 2
    assert all(c["baseline"] is None and c["proposed"]["market"] == "match_under_25"
               for c in out["changed_fixture_choices"])
    assert out["baseline"]["accas"] == 0
    assert out["proposed"]["accas"] == 1 and out["proposed"]["unknown"] == 1
    assert out["changed_card_dates"] == ["2026-10-18"]
    assert out["changed_card_net_difference_bounds"][0] < 0 < out["changed_card_net_difference_bounds"][1]
    assert out["paired"]["valid_replicates"] == 0


def test_summary_exposes_all_stakes_and_unknown_bounds_not_only_winners():
    plan, metadata, scores = card_case()
    del scores[next(iter(scores))]
    summary = audit.summarize([audit.evaluate_card(plan, metadata, scores)])
    assert summary["total_planned_stake"] == 25
    assert summary["stake"] == 12.5  # legacy alias is the resolved subset only
    assert summary["total_net_bounds"] == [0, 25]


def write_archives(tmp_path, final_rows, morning_rows):
    import json
    local = tmp_path / "localdata"
    local.mkdir(exist_ok=True)
    (local / "picks_2026-10-18.json").write_text(json.dumps(final_rows))
    (local / "picks_morning_2026-10-18.json").write_text(json.dumps(morning_rows))


def snapshot_row(at="2026-10-18T12:00:00Z", rate=.6):
    return archived_row(as_of=at, kickoff_utc="2026-10-18T16:00:00Z",
                        event_notes=[{"cohort_n": 200, "market": "match_over_25", "cohort_rate": rate,
                                      "cohort_contract_id": IDENTITY, "engine": "hybrid_cohort",
                                      "cohort_as_of_exclusive": "2026-10-18"}])


def test_earliest_snapshot_never_borrows_later_rates(tmp_path):
    late = snapshot_row(at="2026-10-18T14:00:00Z", rate=.7)
    early = snapshot_row(rate=.6)
    write_archives(tmp_path, [late], [early])
    snapshots, counts, _ = audit.archived_snapshots(tmp_path, "2026-10-18", "2026-10-18", snapshot_mode="earliest")
    row, rates = next(iter(snapshots.values()))
    assert row["as_of"] == early["as_of"] and rates["match_over_25"] == .6
    assert counts["duplicate_fixture_rows"] == 1
    assert "picks_morning_" in row["_replay_archive"]
    final, _, _ = audit.archived_snapshots(tmp_path, "2026-10-18", "2026-10-18")
    assert next(iter(final.values()))[1]["match_over_25"] == .7


def test_same_time_conflicting_snapshots_cannot_be_cherry_picked_or_rescued_by_later_data(tmp_path):
    a, b = snapshot_row(rate=.6), snapshot_row(rate=.7)
    later = snapshot_row(at="2026-10-18T14:00:00Z", rate=.8)
    write_archives(tmp_path, [a], [b, later])
    snapshots, counts, _ = audit.archived_snapshots(tmp_path, "2026-10-18", "2026-10-18", snapshot_mode="earliest")
    assert not snapshots
    assert counts["conflicting_same_time_snapshot"] == 1
    assert counts["snapshot_blocked_by_earlier_conflict"] == 1


def test_coherent_earlier_snapshot_can_precede_later_conflicting_evidence(tmp_path):
    a, b = snapshot_row(rate=.6), snapshot_row(rate=.7)
    earlier = snapshot_row(at="2026-10-18T10:00:00Z", rate=.5)
    write_archives(tmp_path, [a], [b, earlier])
    snapshots, _, _ = audit.archived_snapshots(tmp_path, "2026-10-18", "2026-10-18", snapshot_mode="earliest")
    assert next(iter(snapshots.values()))[1]["match_over_25"] == .5


def test_competition_replays_schema2_original_snapshot_and_fails_closed_on_hash_change(tmp_path):
    import hashlib
    import json
    from scripts.audit_enh_market_competition import competition
    row = snapshot_row()
    write_archives(tmp_path, [row], [])
    relative = "localdata/picks_2026-10-18.json"
    report = tmp_path / "audit.json"
    report.write_text(json.dumps({"schema": 2, "inputs_sha256": {
        relative: hashlib.sha256((tmp_path / relative).read_bytes()).hexdigest()},
        "evidence": [{"fixture": list(audit.identity(row)), "as_of": row["as_of"],
                      "kickoff_utc": row["kickoff_utc"], "archive": relative,
                      "cohort_rates": audit.snapshot_rates(row), "baseline": None, "proposed": None}],
        "limitations": []}))
    result = competition(tmp_path, report)
    assert result["coverage"]["snapshots"] == 1 and result["coverage"]["changed_fixture_choices"] == 0
    (tmp_path / relative).write_text("[]")
    with pytest.raises(ValueError, match="input changed"):
        competition(tmp_path, report)


def test_single_changed_day_cannot_produce_a_zero_width_bootstrap_confidence_claim():
    plan, metadata, scores = card_case()
    base = audit.evaluate_card(plan, metadata, scores)
    scores[next(iter(scores))] = {(4, 2)}
    proposed = audit.evaluate_card(plan, metadata, scores)
    out = audit.paired_bootstrap({"day": base}, {"day": proposed}, changed_days=["day"])
    assert out["status"] == "INSUFFICIENT_CHANGED_DAY_SUPPORT"
    assert out["valid_replicates"] == 0 and out["roi_gap_95pct"] is None


def test_bootstrap_cannot_hide_unresolved_changed_cards_behind_unchanged_resolved_days():
    plan, metadata, scores = card_case()
    settled = audit.evaluate_card(plan, metadata, scores)
    del scores[next(iter(scores))]
    pending = audit.evaluate_card(plan, metadata, scores)
    a = {"unchanged": settled, "changed": pending}
    b = {"unchanged": settled, "changed": pending}
    out = audit.paired_bootstrap(a, b, changed_days=["changed"])
    assert out["status"] == "INCOMPLETE_CHANGED_CARDS"
    assert out["valid_replicates"] == 0 and out["roi_gap_95pct"] is None
