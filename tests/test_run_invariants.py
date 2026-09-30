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
