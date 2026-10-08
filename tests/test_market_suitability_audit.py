from collections import Counter
from pathlib import Path

from scripts.market_suitability_audit import (
    aggregate_cell,
    build_breakdowns,
    build_ml_records,
    ticket_leg_count_for_selection,
)


def test_draw_predictions_count_hits_and_misses_separately():
    rows = [
        {
            "result_status": "settled",
            "outcome_category": "",
            "market_1x2_result": "win",
        },
        {
            "result_status": "settled",
            "outcome_category": "",
            "market_1x2_result": "loss",
        },
        {
            "result_status": "pending",
            "outcome_category": "",
            "market_1x2_result": "",
        },
    ]

    cell = aggregate_cell("ml-meta_draw", "overall", "all", rows)

    assert cell["n"] == 3
    assert cell["n_scored"] == 2
    assert cell["n_pending"] == 1
    assert cell["draw_prediction_hits"] == 1
    assert cell["draw_prediction_misses"] == 1
    assert cell["market_1x2_win"] == 1
    assert cell["market_1x2_loss"] == 1
    assert cell["double_chance_win"] == ""
    assert cell["avoid_defeat_n"] == ""


def test_selected_side_breakdown_keeps_home_and_away_outcomes_separate():
    common = {
        "population": "operational_30d",
        "pre_kickoff_analysis_eligible": True,
        "time_status": "pre_kickoff_verified",
        "primary_rule": "rule-a",
        "probability_band": "60-<70",
        "publication_stage": "no_retained_receipt",
        "ticketed": False,
        "decision_week": "2026-09-07..2026-09-13",
        "source_era": "era-a",
    }
    rows = [
        {
            **common,
            "selection_side": "home",
            "result_status": "settled",
            "outcome_category": "win",
            "market_1x2_result": "win",
            "double_chance_result": "win",
            "dnb_asian0_result": "win",
            "asian_plus0_5_result": "win",
            "asian_plus1_result": "win",
        },
        {
            **common,
            "selection_side": "home",
            "result_status": "pending",
            "outcome_category": "",
        },
        {
            **common,
            "selection_side": "away",
            "result_status": "settled",
            "outcome_category": "loss_by_one",
            "market_1x2_result": "loss",
            "double_chance_result": "win",
            "dnb_asian0_result": "loss",
            "asian_plus0_5_result": "win",
            "asian_plus1_result": "push",
        },
        {
            **common,
            "selection_side": "away",
            "result_status": "ambiguous",
            "outcome_category": "",
        },
    ]

    cells = build_breakdowns(rows, "2026-09-08", "2026-10-07")
    sides = {
        row["cell"]: row
        for row in cells
        if row["population"] == "operational_30d"
        and row["dimension"] == "selected_team_side"
    }

    assert sides["home"]["n"] == 2
    assert sides["home"]["n_scored"] == 1
    assert sides["home"]["n_pending"] == 1
    assert sides["home"]["win"] == 1
    assert sides["home"]["market_1x2_win"] == 1
    assert sides["away"]["n"] == 2
    assert sides["away"]["n_ambiguous"] == 1
    assert sides["away"]["loss_by_one"] == 1
    assert sides["away"]["asian_plus1_push"] == 1


def test_ml_breakdowns_use_hyphenated_population_names():
    base = {
        "record_type": "ml_research_prediction",
        "pre_kickoff_analysis_eligible": True,
        "time_status": "pre_kickoff_verified",
        "result_status": "settled",
        "market_1x2_result": "win",
        "double_chance_result": "win",
        "dnb_asian0_result": "win",
        "asian_plus0_5_result": "win",
        "asian_plus1_result": "win",
        "outcome_category": "win",
        "probability_band": "60-<70",
        "decision_week": "2026-10-05..2026-10-11",
        "model_key": "model-a",
        "model_keys_seen": "model-a;model-b",
        "selection_side": "home",
        "linked_operational_side_relation": "no_operational_fixture_link",
        "linked_operational_publication_stage": "no_link",
        "linked_operational_ticketed": "not_attributed",
    }
    records = [
        {**base, "population": "ml-meta_team"},
        {**base, "population": "ml-fade_team"},
    ]

    cells = build_breakdowns(records, "2026-09-08", "2026-10-07")
    overall = {
        row["population"]: row
        for row in cells
        if row["dimension"] == "overall_pre_kickoff"
    }

    assert overall["ml-meta_team"]["n"] == 1
    assert overall["ml-meta_team"]["win"] == 1
    assert overall["ml-fade_team"]["n"] == 1
    assert overall["ml-fade_team"]["win"] == 1
    side_cells = {
        row["population"]: row
        for row in cells
        if row["dimension"] == "selected_team_side"
    }
    assert side_cells["ml-meta_team"]["cell"] == "home"
    assert side_cells["ml-meta_team"]["n"] == 1
    assert side_cells["ml-fade_team"]["cell"] == "home"
    assert side_cells["ml-fade_team"]["n"] == 1


def test_ml_stage_attribution_excludes_archive_only_links():
    operational = [
        {
            "record_type": "operational_selection",
            "population": "operational_30d",
            "market": "1x2",
            "fixture_date": "2026-10-03",
            "home": "North Town",
            "away": "South Town",
            "selection_side": "home",
            "selection_id": "verified-selection",
            "publication_stage": "main_receipt_only",
            "ticketed": True,
        },
        {
            "record_type": "operational_selection",
            "population": "legacy_archive_inventory",
            "market": "1x2",
            "fixture_date": "2026-10-03",
            "home": "North Town",
            "away": "South Town",
            "selection_side": "home",
            "selection_id": "archive-only-selection",
            "publication_stage": "shadow_receipt_only",
            "ticketed": True,
        },
    ]
    ledger = {
        "rows": [
            {
                "event_key": "ml-event-1",
                "family": "ml-meta",
                "date": "2026-10-03",
                "home": "North Town",
                "away": "South Town",
                "market": "1x2",
                "pick": "home",
                "ml_p": 0.62,
                "first_seen_at": "2026-10-03T10:00:00+02:00",
                "kickoff": "2026-10-03 18:00",
                "status": "settled",
                "score": {"hs": 2, "gs": 1},
            }
        ]
    }

    [row] = build_ml_records(ledger, operational)

    assert row["linked_operational_side_relation"] == (
        "same_side_exact_fixture_link"
    )
    assert row["linked_verified_operational_selection_ids"] == (
        "verified-selection"
    )
    assert row["linked_archive_only_selection_ids"] == (
        "archive-only-selection"
    )
    assert row["linked_operational_publication_stage"] == "main_receipt_only"
    assert row["linked_operational_ticketed"] is True


def test_ticket_alias_collision_attribution_is_one_to_one():
    alias_key = (
        "2026-09-13",
        "viking",
        "kristiansund",
        "1x2",
        "home",
    )
    alias_counts = Counter({alias_key: 1})
    alias_multiplicity = Counter({alias_key: 2})
    exact_counts = Counter({
        (
            "2026-09-13",
            "viking fk",
            "kristiansund bk",
            "1x2",
            "home",
        ): 1
    })
    ticketed = {
        "fixture_date": "2026-09-13",
        "home": "Viking FK",
        "away": "Kristiansund BK",
        "market": "1x2",
        "selection_side": "home",
    }
    alias_only = {**ticketed, "home": "Viking"}

    assert ticket_leg_count_for_selection(
        ticketed, alias_counts, exact_counts, alias_multiplicity
    ) == 1
    assert ticket_leg_count_for_selection(
        alias_only, alias_counts, exact_counts, alias_multiplicity
    ) == 0


def test_ticket_alias_fallback_requires_a_unique_selection():
    alias_key = (
        "2026-09-13",
        "viking",
        "kristiansund",
        "1x2",
        "home",
    )
    alias_counts = Counter({alias_key: 1})
    exact_counts = Counter()
    record = {
        "fixture_date": "2026-09-13",
        "home": "Viking FK",
        "away": "Kristiansund BK",
        "market": "1x2",
        "selection_side": "home",
    }

    assert ticket_leg_count_for_selection(
        record, alias_counts, exact_counts, Counter({alias_key: 1})
    ) == 1
    assert ticket_leg_count_for_selection(
        record, alias_counts, exact_counts, Counter({alias_key: 2})
    ) == 0


def test_daily_workflow_uploads_scored_candidate_jsonl():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github/workflows/daily.yml").read_text(encoding="utf-8")

    assert "localdata/scored_candidate_shadow_*.jsonl" in workflow
    assert "if-no-files-found: ignore" in workflow
