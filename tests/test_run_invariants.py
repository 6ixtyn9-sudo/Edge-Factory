"""Cross-artifact invariants: the check that catches the next contradiction.

Every contradiction found in this pipeline had the same shape — two
artifacts, each defensible alone, disagreeing with each other. These
tests encode each one that actually occurred, so it cannot recur
silently, plus the general rules that would catch its relatives.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from edgefactory import run_invariants as ri          # noqa: E402
from edgefactory import selection_evidence as se      # noqa: E402

RUN_DATE = "2026-09-30"
EVENT_DATE = "2026-10-01"
DECLINE = "declined_insufficient_legs"


def _pick(**over):
    pick = {
        "event_date": EVENT_DATE, "date": EVENT_DATE,
        "home": "Panama", "away": "New Zealand",
        "pick": "home", "selection": "home",
        "rule_id": "1x2_two_source_p55_unanimous",
        "source_voters": ["bzzoiro", "prosoccer"],
    }
    pick.update(over)
    pick.setdefault("evidence_lineage", se.build_lineage(pick))
    return pick


def _plan(picks=None, **over):
    plan = {"run_date": RUN_DATE, "same_day_picks": [],
            "horizon_picks": list(picks or []),
            "event_dates": [EVENT_DATE] if picks else []}
    plan.update(over)
    return plan


def _codes(violations):
    return {v["code"] for v in violations}


# --- a clean run -----------------------------------------------------------


def test_a_consistent_run_reports_no_contradictions():
    violations = ri.check_run(
        plan=_plan([_pick()]),
        summary_published={RUN_DATE: 1},
        sync_manifest={"row_count": 1},
        clv_rows=[{"event_date": EVENT_DATE, "ticket_status": DECLINE}],
        ticket_outcomes={EVENT_DATE: {"status": DECLINE}},
        summary_notification_outcome="sent_this_run",
        notifier_result={"outcome": "sent_this_run"})

    assert violations == []
    assert ri.has_errors(violations) is False
    assert "no contradictions found" in "\n".join(
        ri.render_invariant_lines(violations))


def test_an_empty_run_is_not_a_contradiction():
    assert ri.check_run(plan=_plan()) == []


# --- evidence lineage ------------------------------------------------------


def test_a_selection_without_lineage_is_a_violation():
    pick = _pick()
    pick.pop("evidence_lineage")
    violations = ri.check_selection_evidence(_plan([pick]))
    assert _codes(violations) == {ri.V_NO_LINEAGE}
    assert "Panama" in violations[0]["where"]


def test_a_rule_claiming_more_voters_than_evidence_is_a_violation():
    pick = _pick(source_voters=["bzzoiro"])
    violations = ri.check_selection_evidence(_plan([pick]))
    assert _codes(violations) == {ri.V_RULE_VOTERS}
    assert "claims 2 eligible voter(s) but the lineage shows 1" in \
        violations[0]["detail"]


def test_a_satisfied_rule_passes():
    assert ri.check_selection_evidence(_plan([_pick()])) == []


# --- retired rule ids ------------------------------------------------------


@pytest.mark.parametrize("rule_id", [
    "fresh_1x2_v2_p55", "fresh_production_rule", "1x2_v1_p55", "x_v3_p60",
])
def test_retired_rule_id_forms_are_rejected(rule_id):
    violations = ri.check_rule_ids(_plan([_pick(rule_id=rule_id)]))
    assert _codes(violations) == {ri.V_STALE_RULE_ID}


def test_the_canonical_rule_id_is_accepted():
    assert ri.check_rule_ids(_plan([_pick()])) == []


# --- staking stays with auto_tickets --------------------------------------


@pytest.mark.parametrize("marker", ["stake_units", "units"])
def test_a_pick_carrying_a_stake_size_is_a_violation(marker):
    violations = ri.check_no_stake_from_pick_engine(
        _plan([_pick(**{marker: 1.0})]))
    assert _codes(violations) == {ri.V_PICK_STAKE}
    assert "auto_tickets" in violations[0]["detail"]


def test_a_delegation_marker_is_not_a_stake_size():
    pick = _pick(staking_owner="auto_tickets",
                 staking_policy="handled_by_auto_tickets")
    assert ri.check_no_stake_from_pick_engine(_plan([pick])) == []


# --- Supabase --------------------------------------------------------------


def test_summary_disagreeing_with_the_manifest_is_a_violation():
    violations = ri.check_supabase({RUN_DATE: 0}, {"row_count": 1})
    assert _codes(violations) == {ri.V_SUPABASE}
    assert "reports 0 published row(s) but the sync manifest records 1" in \
        violations[0]["detail"]


def test_a_publish_claimed_without_a_manifest_is_a_violation():
    violations = ri.check_supabase({RUN_DATE: 1}, None)
    assert _codes(violations) == {ri.V_SUPABASE}
    assert "no sync manifest exists" in violations[0]["detail"]


def test_matching_counts_pass():
    assert ri.check_supabase({RUN_DATE: 1}, {"row_count": 1}) == []


def test_an_unsupplied_summary_figure_asserts_nothing():
    """Absent is not the same as zero."""
    assert ri.check_supabase(None, {"row_count": 1}) == []


# --- CLV -------------------------------------------------------------------


def test_clv_left_pending_after_a_verdict_is_a_violation():
    violations = ri.check_clv_status(
        [{"event_date": EVENT_DATE, "pick_id": "p1",
          "ticket_status": "pending_auto_tickets"}],
        {EVENT_DATE: {"status": DECLINE}})
    assert _codes(violations) == {ri.V_CLV_PENDING}
    assert DECLINE in violations[0]["detail"]


def test_clv_left_unknown_after_a_verdict_is_a_violation():
    violations = ri.check_clv_status(
        [{"event_date": EVENT_DATE, "pick_id": "p1",
          "ticket_status": "unknown"}],
        {EVENT_DATE: {"status": DECLINE}})
    assert _codes(violations) == {ri.V_CLV_PENDING}


def test_a_blank_clv_status_after_a_verdict_is_a_violation():
    """The exact shape of the original defect: the field never written."""
    violations = ri.check_clv_status(
        [{"event_date": EVENT_DATE, "pick_id": "p1", "ticket_status": ""}],
        {EVENT_DATE: {"status": DECLINE}})
    assert _codes(violations) == {ri.V_CLV_PENDING}


def test_clv_contradicting_the_verdict_is_a_violation():
    violations = ri.check_clv_status(
        [{"event_date": EVENT_DATE, "pick_id": "p1",
          "ticket_status": "ticket_created"}],
        {EVENT_DATE: {"status": DECLINE}})
    assert _codes(violations) == {ri.V_CLV_STATUS}


def test_clv_matching_the_verdict_passes():
    assert ri.check_clv_status(
        [{"event_date": EVENT_DATE, "ticket_status": DECLINE}],
        {EVENT_DATE: {"status": DECLINE}}) == []


def test_clv_pending_before_auto_tickets_is_not_a_violation():
    """Pending is correct until the verdict exists."""
    assert ri.check_clv_status(
        [{"event_date": EVENT_DATE, "ticket_status": "pending_auto_tickets"}],
        {EVENT_DATE: {"status": DECLINE}}, after_auto_tickets=False) == []


# --- notification ----------------------------------------------------------


def test_summary_claiming_a_send_the_notifier_deduped_is_a_violation():
    """The exact contradiction from the run log."""
    violations = ri.check_notification(
        "sent_this_run", {"outcome": "deduped_already_sent"})
    assert _codes(violations) == {ri.V_NOTIFY}


def test_agreeing_notification_outcomes_pass():
    assert ri.check_notification(
        "deduped_already_sent", {"outcome": "deduped_already_sent"}) == []


# --- census vs plan --------------------------------------------------------


def _census(voter_count, quorum, **over):
    payload = {
        "per_date": {EVENT_DATE: {"fixture_groups": [{
            "fixture": "Panama vs New Zealand",
            "voter_count_1x2": voter_count,
            "quorum_met": quorum,
            "blockers": [] if quorum else ["fewer_than_2_live_voters"],
        }]}}}
    payload.update(over)
    return payload


def test_census_blocking_a_dispatched_selection_is_a_violation():
    """The Panama contradiction, encoded."""
    violations = ri.check_census_agrees_with_plan(
        _census(1, False), _plan([_pick()]))
    assert _codes(violations) == {ri.V_CENSUS_BLOCKED}
    assert "fewer_than_2_live_voters" in violations[0]["detail"]


def test_census_agreeing_with_the_plan_passes():
    assert ri.check_census_agrees_with_plan(
        _census(2, True), _plan([_pick()])) == []


def test_a_census_claiming_current_ticket_status_too_early_is_a_violation():
    violations = ri.check_census_status_provenance(
        {"ticket_status_is_current_run": True}, ran_before_auto_tickets=True)
    assert _codes(violations) == {ri.V_CENSUS_PRETICKET}


def test_a_census_labelling_status_as_previous_passes():
    assert ri.check_census_status_provenance(
        {"ticket_status_is_current_run": False}) == []


# --- reading a real run ----------------------------------------------------


def test_reading_artifacts_from_disk_never_writes(tmp_path):
    (tmp_path / f"fresh_production_dispatch_plan_{RUN_DATE}.json").write_text(
        json.dumps(_plan([_pick()])))
    (tmp_path / f"supabase_sync_manifest_{RUN_DATE}.json").write_text(
        json.dumps({"target_date": RUN_DATE, "row_count": 1}))
    before = sorted(p.name for p in tmp_path.iterdir())

    violations = ri.check_run_from_localdata(RUN_DATE, tmp_path)

    assert sorted(p.name for p in tmp_path.iterdir()) == before
    assert not ri.has_errors(violations)


def test_missing_artifacts_do_not_invent_violations(tmp_path):
    assert ri.check_run_from_localdata(RUN_DATE, tmp_path) == []


def test_render_lists_every_violation_with_its_reason():
    violations = ri.check_run(
        plan=_plan([_pick(source_voters=["bzzoiro"])]),
        summary_published={RUN_DATE: 0}, sync_manifest={"row_count": 1})
    text = "\n".join(ri.render_invariant_lines(violations))

    assert "RUN INVARIANT CHECK" in text
    assert ri.V_RULE_VOTERS in text
    assert ri.V_SUPABASE in text
    assert "resolve it before trusting either" in text
    assert ri.has_errors(violations) is True


def test_the_checker_only_reads():
    src = (ROOT / "src" / "edgefactory" / "run_invariants.py").read_text()
    for forbidden in ("write_text", "mkdir", "unlink", "to_csv", "upsert"):
        assert forbidden not in src


def test_the_checker_runs_in_the_daily_pipeline_after_every_stage():
    src = (ROOT / "scripts" / "daily.py").read_text()
    assert "scripts/check_run_invariants.py" in src
    # It must see what the other stages wrote, so it runs after them.
    for earlier in ("auto_tickets.py", "sync_official_archive",
                    "print_final_production_summary(target_date)"):
        assert src.index(earlier) < src.index("scripts/check_run_invariants.py")
    # run_soft: a diagnostic must never fail the official run.
    assert "def run_soft" in src


def test_the_cli_is_non_fatal_unless_strict(tmp_path, capsys):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_run_invariants_under_test",
        ROOT / "scripts" / "check_run_invariants.py")
    cli = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = cli
    spec.loader.exec_module(cli)

    plan = _plan([_pick(source_voters=["bzzoiro"])])
    (tmp_path / f"fresh_production_dispatch_plan_{RUN_DATE}.json").write_text(
        json.dumps(plan))

    assert cli.main(["--date", RUN_DATE, "--localdata", str(tmp_path)]) == 0
    assert ri.V_RULE_VOTERS in capsys.readouterr().out

    assert cli.main(["--date", RUN_DATE, "--localdata", str(tmp_path),
                     "--strict"]) == 1


# ===========================================================================
# Invariants added after run 36783344791
#
# That run reported "no contradictions found" while mis-stating its
# Supabase breakdown, its CLV final statuses, its notification coverage,
# its voter terminology and its price provenance. Each test below feeds
# the checker the exact shape it passed, and requires it to fail.
# ===========================================================================


def _clv_snapshots():
    rows = []
    for i, final in enumerate(["deferred_before_build_hour",
                               "deferred_before_build_hour",
                               "ticket_created", "ticket_created"]):
        rows.append({"pick_id": f"p{i}", "captured_at_utc": "1",
                     "ticket_status": "pending_auto_tickets"})
        rows.append({"pick_id": f"p{i}", "captured_at_utc": "2",
                     "ticket_status": final})
    return rows


def test_a_publish_attributed_to_the_wrong_date_is_caught():
    violations = ri.check_supabase_dates(
        {"2026-10-01": 4},
        {"row_count": 4,
         "row_counts_by_event_date": {"2026-10-01": 2, "2026-10-02": 2}})

    assert _codes(violations) == {ri.V_SUPABASE_DATES}


def test_a_matching_publish_breakdown_passes():
    assert ri.check_supabase_dates(
        {"2026-10-01": 2, "2026-10-02": 2},
        {"row_count": 4,
         "row_counts_by_event_date": {"2026-10-01": 2, "2026-10-02": 2}}) == []


def test_a_manifest_without_a_breakdown_asserts_nothing():
    assert ri.check_supabase_dates({"2026-10-01": 4},
                                   {"row_count": 4}) == []


def test_superseded_clv_statuses_reported_as_final_are_caught():
    violations = ri.check_clv_latest_status(
        _clv_snapshots(),
        {"deferred_before_build_hour": 2, "pending_auto_tickets": 4,
         "ticket_created": 2},
        4)

    assert ri.V_CLV_STALE_STATUS in _codes(violations)
    assert ri.V_CLV_INFLATED in _codes(violations)


def test_latest_clv_statuses_pass():
    assert ri.check_clv_latest_status(
        _clv_snapshots(),
        {"deferred_before_build_hour": 2, "ticket_created": 2}, 4) == []


def test_a_summary_leaving_selections_unaccounted_for_is_caught():
    violations = ri.check_notification_coverage(
        {"total_selections": 4, "notified": 2, "not_notified": 0})

    assert _codes(violations) == {ri.V_NOTIFY_COVERAGE}


def test_full_notification_coverage_passes():
    assert ri.check_notification_coverage(
        {"total_selections": 4, "notified": 2, "not_notified": 2}) == []


def test_a_production_voter_called_non_dispatchable_is_caught():
    from edgefactory import source_census as sc

    violations = ri.check_voter_terminology({"per_date": {EVENT_DATE: {
        "sources": [{"source": "prosoccer",
                     "production_role": sc.ROLE_SHADOW_VOTER,
                     "blockers": [sc.B_TIER_NOT_DISPATCHABLE]}]}}})

    assert _codes(violations) == {ri.V_VOTER_MISLABELLED}


def test_a_shadow_voter_labelled_production_eligible_passes():
    from edgefactory import source_census as sc

    assert ri.check_voter_terminology({"per_date": {EVENT_DATE: {
        "sources": [{"source": "prosoccer",
                     "production_role": sc.ROLE_SHADOW_VOTER,
                     "blockers": [],
                     "tier_note": sc.B_SHADOW_PRODUCTION_ELIGIBLE}]}}}) == []


def test_a_non_voter_may_still_be_called_non_dispatchable():
    from edgefactory import source_census as sc

    assert ri.check_voter_terminology({"per_date": {EVENT_DATE: {
        "sources": [{"source": "betexplorer_odds",
                     "production_role": sc.ROLE_ODDS_ONLY,
                     "blockers": [sc.B_TIER_NOT_DISPATCHABLE]}]}}}) == []


def test_an_embedded_price_without_an_origin_is_caught(monkeypatch):
    from edgefactory import selection_evidence as se

    monkeypatch.setattr(se, "_price_owner", lambda *_: None)
    violations = ri.check_price_origin(_plan([{
        **_pick(), "odds": 2.05, "pricing_source": "source_embedded_odds",
        "bookmaker": "prosoccer_embedded"}]))

    assert _codes(violations) == {ri.V_PRICE_ORIGIN}


def test_an_embedded_price_naming_its_origin_passes():
    assert ri.check_price_origin(_plan([{
        **_pick(), "odds": 2.05, "pricing_source": "source_embedded_odds",
        "bookmaker": "prosoccer_embedded"}])) == []


def test_missing_selection_detail_lines_are_caught():
    violations = ri.check_selection_detail_count(
        {"same_day_pick_count": 2, "horizon_pick_count": 2}, 2)

    assert _codes(violations) == {ri.V_SELECTION_DETAIL}


def test_a_detail_line_per_selection_passes():
    assert ri.check_selection_detail_count(
        {"same_day_pick_count": 2, "horizon_pick_count": 2}, 4) == []


def test_an_unsupplied_detail_count_asserts_nothing():
    assert ri.check_selection_detail_count(
        {"same_day_pick_count": 2, "horizon_pick_count": 2}, None) == []


# ===========================================================================
# End to end: the run-36783344791 shape, corrected
# ===========================================================================


def _run_36783344791(tmp_path):
    """The four selections that run actually produced."""
    picks = [
        {"home": "Panama", "away": "New Zealand", "event_date": "2026-10-01",
         "pick": "HOME", "odds": 2.05, "pricing_source": "source_embedded_odds",
         "bookmaker": "prosoccer_embedded",
         "source_voters": ["bzzoiro", "prosoccer"], "rule_id": _pick()["rule_id"]},
        {"home": "Ecuador", "away": "Canada", "event_date": "2026-10-01",
         "pick": "HOME", "odds": 1.95, "pricing_source": "source_embedded_odds",
         "bookmaker": "prosoccer_embedded",
         "source_voters": ["bzzoiro", "prosoccer"], "rule_id": _pick()["rule_id"]},
        {"home": "Belgium", "away": "Turkey", "event_date": "2026-10-02",
         "pick": "HOME", "odds": 1.75, "pricing_source": "source_embedded_odds",
         "bookmaker": "prosoccer_embedded",
         "source_voters": ["bzzoiro", "prosoccer"], "rule_id": _pick()["rule_id"]},
        {"home": "Hungary", "away": "Georgia", "event_date": "2026-10-02",
         "pick": "HOME", "odds": 1.85, "pricing_source": "source_embedded_odds",
         "bookmaker": "prosoccer_embedded",
         "source_voters": ["bzzoiro", "prosoccer"], "rule_id": _pick()["rule_id"]},
    ]
    for pick in picks:
        pick["evidence_lineage"] = se.build_lineage(pick)
    plan = {"run_date": RUN_DATE,
            "same_day_picks": picks[:2], "horizon_picks": picks[2:],
            "same_day_pick_count": 2, "horizon_pick_count": 2,
            "event_dates": ["2026-10-01", "2026-10-02"]}
    (tmp_path / f"fresh_production_dispatch_plan_{RUN_DATE}.json").write_text(
        json.dumps(plan))
    return plan


def test_the_corrected_run_shape_has_no_contradictions(tmp_path):
    _run_36783344791(tmp_path)
    (tmp_path / f"supabase_sync_manifest_{RUN_DATE}.json").write_text(
        json.dumps({"target_date": RUN_DATE, "row_count": 4,
                    "row_counts_by_event_date": {"2026-10-01": 2,
                                                 "2026-10-02": 2}}))

    violations = ri.check_run_from_localdata(RUN_DATE, tmp_path)

    assert violations == [], violations


def test_the_defective_publish_attribution_is_caught_end_to_end(tmp_path):
    """The exact wrong figure the run printed: 4 (2026-10-01=4)."""
    plan = _run_36783344791(tmp_path)

    violations = ri.check_run(
        plan=plan,
        summary_published={"2026-10-01": 4},
        sync_manifest={"row_count": 4,
                       "row_counts_by_event_date": {"2026-10-01": 2,
                                                    "2026-10-02": 2}},
        summary_selection_detail_count=4)

    assert ri.V_SUPABASE_DATES in _codes(violations)


def test_the_defective_clv_and_coverage_accounting_is_caught_end_to_end(tmp_path):
    plan = _run_36783344791(tmp_path)

    violations = ri.check_run(
        plan=plan,
        clv_rows=_clv_snapshots(),
        summary_clv_status_counts={"deferred_before_build_hour": 2,
                                   "pending_auto_tickets": 4,
                                   "ticket_created": 2},
        notification_coverage={"total_selections": 4, "notified": 2,
                               "not_notified": 0},
        summary_selection_detail_count=2)

    codes = _codes(violations)
    assert ri.V_CLV_STALE_STATUS in codes
    assert ri.V_CLV_INFLATED in codes
    assert ri.V_NOTIFY_COVERAGE in codes
    assert ri.V_SELECTION_DETAIL in codes


def test_a_multi_date_publish_without_a_breakdown_is_flagged():
    """Unproven, not proven wrong: a warning, so the run is not blocked."""
    violations = ri.check_supabase_dates(
        {"2026-10-01": 4}, {"row_count": 4},
        ["2026-10-01", "2026-10-02"])

    assert _codes(violations) == {ri.V_SUPABASE_NO_BREAKDOWN}
    assert not ri.has_errors(violations)


def test_a_single_date_publish_without_a_breakdown_is_fine():
    assert ri.check_supabase_dates(
        {"2026-10-01": 4}, {"row_count": 4}, ["2026-10-01"]) == []


# ===========================================================================
# Future-dated tickets and bucket canonicality
# ===========================================================================


def test_a_future_dated_ticket_backed_by_a_horizon_pick_is_intended():
    """Run 36783344791 carded 2026-10-02 from two real horizon picks."""
    plan = {"same_day_picks": [{"event_date": "2026-10-01"}],
            "horizon_picks": [{"event_date": "2026-10-02",
                               "home": "Belgium", "away": "Turkey"},
                              {"event_date": "2026-10-02",
                               "home": "Hungary", "away": "Georgia"}]}

    assert ri.check_ticket_dates(
        plan, {"2026-10-01": {"status": "deferred_before_build_hour"},
               "2026-10-02": {"status": "ticket_created"}}) == []


def test_a_ticket_for_a_date_with_no_selection_is_caught():
    """What planner output leaking into the slate would look like."""
    plan = {"same_day_picks": [{"event_date": "2026-10-01"}],
            "horizon_picks": []}

    violations = ri.check_ticket_dates(
        plan, {"2026-10-02": {"status": "ticket_created"}})

    assert _codes(violations) == {ri.V_TICKET_DATE_UNBACKED}


def test_a_lane_specific_bucket_is_caught():
    violations = ri.check_buckets_are_canonical(
        {"horizon_picks": [{"home": "Belgium", "away": "Turkey",
                            "bucket": "PRODUCTION_CERTIFIED"}]})

    assert _codes(violations) == {ri.V_NON_CANONICAL_BUCKET}


def test_canonical_buckets_pass():
    assert ri.check_buckets_are_canonical(
        {"same_day_picks": [{"bucket": "CERTIFIED_CLEAN"}],
         "horizon_picks": [{"bucket": "WATCHLIST_SUSPECT_PRICE"}]}) == []


def test_the_invariant_taxonomy_matches_the_auto_ticket_allowlist():
    import scripts.auto_tickets as at

    assert at.BUCKETS <= ri.CANONICAL_BUCKETS


# ===========================================================================
# The official target date owns the card
#
# A future card is not a future forecast. It skips the build-hour and
# freeze gates (both written target == today) and commits bank as an open
# slip before the event day: on 2026-10-01 it locked 21.1% of capital
# behind a draft that could never freeze.
# ===========================================================================


def test_carding_a_future_date_in_the_daily_run_is_caught():
    plan = {"same_day_picks": [{"event_date": "2026-10-01"}],
            "horizon_picks": [{"event_date": "2026-10-02",
                               "home": "Belgium", "away": "Turkey"}]}

    violations = ri.check_ticket_dates(
        plan,
        {"2026-10-01": {"status": "deferred_before_build_hour"},
         "2026-10-02": {"status": "ticket_created"}},
        target_date="2026-10-01")

    # A real dispatched selection backs it, yet it is still refused.
    assert _codes(violations) == {ri.V_TICKET_DATE_NOT_TARGET}


def test_a_real_horizon_selection_does_not_excuse_a_future_card():
    """Backing is necessary, not sufficient."""
    plan = {"horizon_picks": [{"event_date": "2026-10-02"}]}

    assert ri.check_ticket_dates(
        plan, {"2026-10-02": {"status": "ticket_created"}},
        target_date="2026-10-01") != []


def test_an_explicit_future_ticket_mode_is_allowed():
    plan = {"horizon_picks": [{"event_date": "2026-10-02"}]}

    assert ri.check_ticket_dates(
        plan, {"2026-10-02": {"status": "ticket_created"}},
        target_date="2026-10-01", future_ticket_mode=True) == []


def test_carding_only_the_target_date_passes():
    plan = {"same_day_picks": [{"event_date": "2026-10-01"}],
            "horizon_picks": [{"event_date": "2026-10-02"}]}

    assert ri.check_ticket_dates(
        plan, {"2026-10-01": {"status": "deferred_before_build_hour"}},
        target_date="2026-10-01") == []


def test_without_a_target_date_the_check_asserts_nothing_new():
    plan = {"horizon_picks": [{"event_date": "2026-10-02"}]}

    assert ri.check_ticket_dates(
        plan, {"2026-10-02": {"status": "ticket_created"}}) == []


# ===========================================================================
# An open slip is committed capital, not just a file
# ===========================================================================


def test_a_future_open_slip_committing_bank_is_caught():
    """The 21.116% the 2026-10-02 draft locked a day early."""
    state = {"open_slips": [{"date": "2026-09-27", "staked_pct": 15.5364},
                            {"date": "2026-10-02", "staked_pct": 21.116}]}

    violations = ri.check_open_slip_dates(state, target_date="2026-10-01")

    assert _codes(violations) == {ri.V_OPEN_SLIP_NOT_TARGET}
    assert "21.116" in violations[0]["detail"]


def test_a_past_open_slip_does_not_trip_the_check():
    state = {"open_slips": [{"date": "2026-09-27", "staked_pct": 15.5364}]}

    assert ri.check_open_slip_dates(state, target_date="2026-10-01") == []


def test_an_explicit_future_ticket_run_may_commit_bank():
    state = {"open_slips": [{"date": "2026-10-02", "staked_pct": 21.116}]}

    assert ri.check_open_slip_dates(
        state, target_date="2026-10-01", future_ticket_mode=True) == []


def test_the_cleaned_state_passes_every_date_check():
    """The real post-cleanup shape."""
    state = {"bank": 184.46, "open_slips": [{"date": "2026-09-27",
                                             "staked_pct": 15.5364}]}

    assert ri.check_open_slip_dates(state, target_date="2026-10-01") == []


# ===========================================================================
# Thin edge on a proxy capture timestamp
#
# The dispatch floor dropped 0.02 -> 0.0 so the assayer can grade thin
# selections. That makes freshness decisive: a +0.005 edge on a verified
# line is not the same bet as one priced off a kickoff-as-captured_at.
# ===========================================================================


def _priced(edge, source="scoutingstats_odds"):
    return {"home": "Germany", "away": "Serbia", "edge": edge,
            "odds_source": source}


def test_a_thin_edge_on_a_proxy_capture_is_flagged():
    violations = ri.check_price_capture_proxy([_priced(0.005)])

    assert _codes(violations) == {ri.V_PRICE_CAPTURE_PROXY}
    assert violations[0]["severity"] == ri.WARNING


def test_wales_at_its_actual_edge_is_flagged():
    assert ri.check_price_capture_proxy([_priced(0.0194)]) != []


def test_a_healthy_edge_on_a_proxy_capture_is_not_flagged():
    """Above the thin band the price timing no longer decides the bet."""
    assert ri.check_price_capture_proxy([_priced(0.08)]) == []


def test_a_thin_edge_on_a_real_capture_is_not_flagged():
    assert ri.check_price_capture_proxy(
        [_priced(0.005, source="bzzoiro_odds")]) == []


def test_a_negative_edge_is_not_this_checks_business():
    """Negative edge is vetoed upstream; this check is about freshness."""
    assert ri.check_price_capture_proxy([_priced(-0.03)]) == []


def test_an_unparseable_edge_is_not_guessed():
    assert ri.check_price_capture_proxy([_priced(None)]) == []


def test_the_proxy_source_list_is_documented():
    doc = (ROOT / "docs" / "operator" / "captured-at-followup.md")
    assert doc.exists()
    text = doc.read_text()
    for source in ri.PROXY_CAPTURE_SOURCES:
        assert source in text
    assert "enh_pricing" in text and "replay_harness" in text


def test_the_proxy_capture_flag_is_emitted_at_the_source():
    """The value stays (3 consumers need it) but is labelled, not implied."""
    src = (ROOT / "scripts" / "picks_today.py").read_text()
    block = src.split("def _scoutingstats_rows_to_odds", 1)[1][:1400]
    assert '"captured_at_is_kickoff_proxy": True' in block
    assert '"captured_at_provenance": "kickoff_proxy_no_fetch_time"' in block
    # It must still carry the kickoff: enh_pricing._fresh_row,
    # auto_tickets and replay_harness resolve kickoffs through it.
    assert '"captured_at": row.get("kickoff")' in block


def test_a_flagged_row_is_still_caught_by_the_thin_edge_warning():
    row = {"home": "Germany", "away": "Serbia", "edge": 0.005,
           "odds_source": "scoutingstats_odds",
           "captured_at_is_kickoff_proxy": True}

    assert _codes(ri.check_price_capture_proxy([row])) == {
        ri.V_PRICE_CAPTURE_PROXY}


# ===========================================================================
# A selection must not contradict its own earlier snapshot
#
# Run 736d2d9 raised clv_ticket_status_disagrees_with_auto_ticket_outcome
# for Guinea vs Kenya and Maccabi Bnei Raina: both were ticketed, but each
# had an earlier pick_time row reading declined_no_selections. Plan
# scoping cannot fix this -- both fixtures ARE in the plan.
# ===========================================================================


def _snapshot(home, status, label, stamp):
    return {"event_date": "2026-10-01", "home": home, "away": "Opponent",
            "selection": "home", "ticket_status": status,
            "snapshot_label": label, "captured_at_utc": stamp,
            "pick_id": f"2026-10-01|{home}|opponent|1x2|home|rule".lower()}


def test_an_earlier_snapshot_does_not_contradict_the_final_status():
    rows = [
        _snapshot("Guinea", "declined_no_selections", "pick_time",
                  "2026-10-01T06:00:00Z"),
        _snapshot("Guinea", "ticket_created", "end_of_run",
                  "2026-10-01T09:30:00Z"),
        _snapshot("Maccabi Bnei Raina", "declined_no_selections", "pick_time",
                  "2026-10-01T06:00:00Z"),
        _snapshot("Maccabi Bnei Raina", "ticket_created", "end_of_run",
                  "2026-10-01T09:30:00Z"),
    ]

    violations = ri.check_clv_status(
        rows, {"2026-10-01": {"status": "ticket_created"}})

    assert violations == [], \
        "a selection cannot contradict its own superseded snapshot"


def test_a_genuinely_wrong_final_status_is_still_caught():
    rows = [
        _snapshot("Guinea", "ticket_created", "pick_time",
                  "2026-10-01T06:00:00Z"),
        _snapshot("Guinea", "declined_no_selections", "end_of_run",
                  "2026-10-01T09:30:00Z"),
    ]

    violations = ri.check_clv_status(
        rows, {"2026-10-01": {"status": "ticket_created"}})

    assert _codes(violations) == {ri.V_CLV_STATUS}


def test_a_final_row_left_pending_is_still_caught():
    rows = [_snapshot("Guinea", "pending_auto_tickets", "end_of_run",
                      "2026-10-01T09:30:00Z")]

    violations = ri.check_clv_status(
        rows, {"2026-10-01": {"status": "ticket_created"}})

    assert _codes(violations) == {ri.V_CLV_PENDING}


# ===========================================================================
# A frozen slip freezes a DATE, not every later selection
#
# Run 84619f7: the frozen slip held Bnei Yehuda and Envigado, the slate
# then changed, and Maccabi Bnei Raina -- never carded -- was reported as
# ticket_frozen purely because the date was frozen.
# ===========================================================================


FROZEN_LEGS = ["bnei yehuda|maccabi kiryat gat|home",
               "envigado|orsomarso|home"]


def _frozen_outcome(status="ticket_frozen", keys=FROZEN_LEGS):
    out = {"status": status}
    if keys is not None:
        out["frozen_leg_keys"] = keys
    return {"2026-10-01": out}


def test_a_selection_absent_from_the_frozen_card_is_caught():
    plan = {"same_day_picks": [{"event_date": "2026-10-01",
                                "home": "Maccabi Bnei Raina",
                                "away": "Hapoel Kfar Shalem",
                                "selection": "home"}]}

    violations = ri.check_ticketed_selections_are_on_the_card(
        plan, _frozen_outcome())

    assert _codes(violations) == {ri.V_FROZEN_STATUS_LEAK}


def test_a_selection_inside_the_frozen_card_is_fine():
    plan = {"same_day_picks": [{"event_date": "2026-10-01",
                                "home": "Envigado", "away": "Orsomarso",
                                "selection": "home"}]}

    assert ri.check_ticketed_selections_are_on_the_card(
        plan, _frozen_outcome()) == []


def test_an_outcome_without_leg_records_asserts_nothing():
    """Older artifacts cannot prove membership either way."""
    plan = {"same_day_picks": [{"event_date": "2026-10-01",
                                "home": "Anything", "away": "At All",
                                "selection": "home"}]}

    assert ri.check_ticketed_selections_are_on_the_card(
        plan, _frozen_outcome(keys=None)) == []


def test_a_declined_date_is_not_this_checks_business():
    plan = {"same_day_picks": [{"event_date": "2026-10-01",
                                "home": "Maccabi Bnei Raina",
                                "away": "Hapoel Kfar Shalem",
                                "selection": "home"}]}

    assert ri.check_ticketed_selections_are_on_the_card(
        plan, _frozen_outcome(status="declined_insufficient_legs")) == []


# ===========================================================================
# Run 926e99a: CLV was fixed but the outcome object stayed date-level
#
# CLV said declined_frozen_card_already_locked, auto_tickets said
# ticket_frozen, and the two contradicted each other.
# ===========================================================================


LEGS = ["bnei yehuda|maccabi kiryat gat|home", "envigado|orsomarso|home"]
MACCABI = {"event_date": "2026-10-01", "home": "Maccabi Bnei Raina",
           "away": "Hapoel Kfar Shalem", "pick": "home",
           "ticket_status": "declined_frozen_card_already_locked",
           "snapshot_label": "end_of_run",
           "captured_at_utc": "2026-10-01T09:30:00Z",
           "pick_id": "2026-10-01|maccabi-bnei-raina|hapoel|1x2|home|rule"}
OUTCOME = {"2026-10-01": {
    "status": "ticket_frozen", "frozen_leg_keys": LEGS,
    "selection_statuses": {
        "maccabi bnei raina|hapoel kfar shalem|home":
            "declined_frozen_card_already_locked",
        "envigado|orsomarso|home": "ticket_frozen"}}}


def test_clv_and_the_outcome_now_agree_for_the_locked_out_selection():
    assert ri.check_clv_status([MACCABI], OUTCOME) == []


def test_the_outcome_reports_the_selection_not_the_date():
    assert ri.outcome_status_for(MACCABI, OUTCOME["2026-10-01"]) == \
        "declined_frozen_card_already_locked"
    on_card = {"home": "Envigado", "away": "Orsomarso", "pick": "home"}
    assert ri.outcome_status_for(on_card, OUTCOME["2026-10-01"]) == \
        "ticket_frozen"


def test_a_per_selection_status_passes_the_card_membership_check():
    plan = {"same_day_picks": [MACCABI]}
    assert ri.check_ticketed_selections_are_on_the_card(plan, OUTCOME) == []


def test_a_legacy_date_level_claim_is_still_challenged():
    """No per-selection record: the date's claim covers the selection."""
    plan = {"same_day_picks": [MACCABI]}
    legacy = {"2026-10-01": {"status": "ticket_frozen",
                             "frozen_leg_keys": LEGS}}

    assert _codes(ri.check_ticketed_selections_are_on_the_card(
        plan, legacy)) == {ri.V_FROZEN_STATUS_LEAK}


def test_a_dishonest_per_selection_claim_is_caught():
    """Claiming ticketed for a selection absent from the card."""
    plan = {"same_day_picks": [MACCABI]}
    lying = {"2026-10-01": {
        "status": "ticket_frozen", "frozen_leg_keys": LEGS,
        "selection_statuses": {
            "maccabi bnei raina|hapoel kfar shalem|home": "ticket_frozen"}}}

    assert _codes(ri.check_ticketed_selections_are_on_the_card(
        plan, lying)) == {ri.V_FROZEN_STATUS_LEAK}
