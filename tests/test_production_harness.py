"""Harness checks for the production-lane reality, applied to real artifacts.

Every fixture here is synthetic on purpose: synthetic data is permitted
inside unit tests and nowhere else.

This module is the guard rail for the invariants the lane now depends on —
clean rule identifiers, staking owned by auto_tickets, the dispatch plan as
the authoritative production payload, event-dated future picks, and a
kickoff parser that reads day-first from the fixture's own calendar.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fp = _load("fresh_production_harness_under_test", "fresh_production.py")
pt = _load("picks_today_harness_under_test", "picks_today.py")
notify = _load("notify_harness_under_test", "notify.py")
sync = _load("sync_supabase_harness_under_test", "sync_supabase.py")
clv = _load("audit_clv_harness_under_test", "audit_clv.py")
at = _load("auto_tickets_harness_under_test", "auto_tickets.py")

from edgefactory import production_harness as harness  # noqa: E402
from edgefactory import production_lane as pl  # noqa: E402

RUN_DATE = "2026-09-30"
EVENT_DATE = "2026-10-01"
FRESH = {"EDGE_FACTORY_PRODUCTION_LANE": "fresh_production"}


def _pick(**overrides):
    row = {
        "date": EVENT_DATE, "event_date": EVENT_DATE, "kickoff": f"{EVENT_DATE} 08:10",
        "league": "World Cup Qualification", "home": "Panama",
        "away": "New Zealand", "selection": "home",
        "rule_id": "1x2_two_source_p55_unanimous", "probability": 0.72,
        "odds": 2.25, "implied_probability": 0.4444, "edge": 0.1403,
        "dispatchable": True, "internal_stake_units": 1.0,
        "dispatch_method": "certified_rule", "pricing_source": "bzzoiro",
        "timing_source": "zulubet", "source_voters": ["zulubet", "vitibet"],
        "price_match_method": "exact", "price_tier": "dedicated_pricing_feed",
        "bookmaker": "bet365", "model_version": "m1",
        "feature_schema_version": "s1", "walkforward_evidence": {},
        "staking_policy": fp.STAKING_POLICY, "staking_owner": fp.STAKING_OWNER,
    }
    row.update(overrides)
    return row


def _plan(picks=None):
    picks = [_pick()] if picks is None else picks
    horizon = {"generated_for": RUN_DATE, "horizon_end": "2026-10-02",
               "min_lead_minutes": 30, "max_lead_hours": 48,
               "eligible_pick_count": len(picks), "picks": picks}
    return fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)


# --------------------------------------------------------------------------
# 1-8. Rule identifier naming
# --------------------------------------------------------------------------


def test_generated_rule_ids_carry_no_version_label_or_lane_prefix():
    ids = [rule.rule_id for rule in fp.candidate_rules()]
    assert ids, "the lane must define rules"
    harness.assert_no_forbidden_version_labels(
        [{"rule_id": rid} for rid in ids], context="candidate_rules")
    harness.assert_no_fresh_prefix_in_rule_ids(
        [{"rule_id": rid} for rid in ids], context="candidate_rules")
    assert "1x2_two_source_p55_unanimous" in ids
    assert "1x2_three_source_p65_majority" in ids
    assert "1x2_two_source_p70_majority" in ids


def test_voter_count_is_spelled_out_rather_than_numbered():
    """'v2' read as a version; 'two_source' says what it actually means."""
    assert fp.rule_identifier(2, 0.55, True) == "1x2_two_source_p55_unanimous"
    assert fp.rule_identifier(3, 0.65, False) == "1x2_three_source_p65_majority"
    assert fp.rule_identifier(4, 0.70, True) == "1x2_four_source_p70_unanimous"


def test_retired_rule_ids_resolve_as_deprecated_internal_aliases():
    aliases = fp.deprecated_rule_aliases()
    assert aliases["fresh_1x2_v2_p55_unanimous"] == "1x2_two_source_p55_unanimous"
    assert aliases["fresh_1x2_v3_p65_majority"] == "1x2_three_source_p65_majority"
    # Reading an old artifact resolves; a current ID passes through.
    assert fp.resolve_rule_id("fresh_1x2_v2_p60_majority") == \
        "1x2_two_source_p60_majority"
    assert fp.resolve_rule_id("1x2_two_source_p60_majority") == \
        "1x2_two_source_p60_majority"
    assert fp.resolve_rule_id(None) is None


def test_supabase_alias_table_resolves_retired_ids_without_writing_them():
    aliases = sync.build_rule_aliases([])
    assert aliases["fresh_1x2_v2_p55_unanimous"] == "1x2_two_source_p55_unanimous"
    resolved = sync.pick_edge_name(
        {"edge_rule": "fresh_1x2_v2_p55_unanimous"}, aliases)
    assert resolved == "1x2_two_source_p55_unanimous"
    harness.assert_no_fresh_prefix_in_rule_ids(
        [{"rule_id": resolved}], context="supabase payload")


def test_new_artifacts_write_only_clean_rule_ids():
    plan = _plan()
    harness.check_production_artifact(plan, context="dispatch plan json")
    harness.check_production_artifact(fp.render_dispatch_plan_md(plan),
                                      context="dispatch plan markdown")


def test_notification_text_uses_only_clean_rule_ids(tmp_path):
    plan = _plan()
    message = notify.format_future_pick_message_from_plan(plan, RUN_DATE)
    assert "1x2_two_source_p55_unanimous" in message
    harness.check_production_artifact(message, context="notification")


def test_clv_payload_preserves_the_clean_rule_id():
    row = {"rule_id": "1x2_two_source_p55_unanimous",
           "rule_name": "1x2_two_source_p55_unanimous"}
    harness.check_production_artifact(row, context="clv row")
    assert "rule_id" in clv.SNAPSHOT_FIELDS
    assert "event_date" in clv.SNAPSHOT_FIELDS


def test_auto_ticket_payload_uses_clean_rule_ids():
    staked = at.apply_ticket_staking([_pick(edge_rule="1x2_two_source_p55_unanimous")],
                                     stake_per_leg=2.5)
    harness.check_production_artifact(staked, context="auto ticket payload")


# --------------------------------------------------------------------------
# 9-12. Staking ownership
# --------------------------------------------------------------------------


def test_pick_engine_emits_no_stake_size():
    plan = _plan()
    harness.assert_pick_engine_does_not_emit_stake_size(
        plan["horizon_picks"], context="dispatched pick")
    harness.assert_pick_engine_does_not_emit_stake_size(
        plan["same_day_picks"], context="same-day pick")


def test_pick_engine_emits_a_staking_delegation_marker():
    plan = _plan()
    harness.assert_staking_delegated_to_auto_tickets(
        plan["horizon_picks"], context="dispatched pick")
    assert fp.STAKING_POLICY == "handled_by_auto_tickets"
    assert fp.STAKING_OWNER == "auto_tickets"


def test_auto_tickets_owns_and_adds_staking_independently():
    """The ticket layer is the only place a stake size may appear."""
    picks = _plan()["horizon_picks"]
    assert "stake_units" not in picks[0]

    staked = at.apply_ticket_staking(picks, stake_per_leg=2.5)
    assert staked[0]["stake_units"] == 2.5
    assert staked[0]["staked_by"] == "auto_tickets"
    # The pick engine's own rows are untouched.
    assert "stake_units" not in picks[0]


def test_no_user_facing_text_shows_bare_stake_shorthand():
    plan = _plan()
    harness.assert_no_stake_notation_in_text(
        fp.render_dispatch_plan_md(plan), context="dispatch plan markdown")
    harness.assert_no_stake_notation_in_text(
        "\n".join(fp.render_dispatch_plan_summary(plan, {"blocker_counts": {}})),
        context="operator summary")
    harness.assert_no_stake_notation_in_text(
        notify.format_future_pick_message_from_plan(plan, RUN_DATE),
        context="notification")


def test_the_stake_notation_check_actually_catches_offenders():
    """A guard rail that never fires is not a guard rail."""
    for offender in ("stake: 1.0u", "stake=2u", "1.0u", "stake: 1"):
        with pytest.raises(AssertionError):
            harness.assert_no_stake_notation_in_text(offender)


def test_the_naming_checks_actually_catch_offenders():
    with pytest.raises(AssertionError):
        harness.assert_no_forbidden_version_labels(
            [{"rule_id": "1x2_v2_p55_unanimous"}])
    with pytest.raises(AssertionError):
        harness.assert_no_fresh_prefix_in_rule_ids(
            [{"rule_id": "fresh_1x2_two_source_p55_unanimous"}])
    with pytest.raises(AssertionError):
        harness.assert_pick_engine_does_not_emit_stake_size({"stake_units": 1.0})


# --------------------------------------------------------------------------
# 13-18. Dispatch plan authority and downstream routing
# --------------------------------------------------------------------------


def test_dispatch_plan_is_authoritative_and_self_describing():
    harness.assert_dispatch_plan_authoritative(_plan(), context="plan")
    harness.assert_dispatch_plan_authoritative(
        fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                               horizon_rows=[],
                               horizon={"generated_for": RUN_DATE, "picks": []}),
        context="empty plan")


def test_future_picks_are_event_dated_throughout():
    harness.assert_future_picks_event_dated(_plan(), context="plan")


@patch.dict(os.environ, FRESH)
def test_clv_follows_the_dispatch_plan_when_the_same_day_file_is_empty(tmp_path):
    """An empty same-day file must not suppress future CLV capture."""
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / f"fresh_production_production_picks_{RUN_DATE}.json").write_text("[]")
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(_plan()))

    with patch.object(clv, "LOCALDATA", localdata):
        picks = clv._dispatch_plan_picks(RUN_DATE)

    assert picks is not None and len(picks) == 1
    assert picks[0]["date"] == EVENT_DATE          # priced on its event date
    assert picks[0]["event_date"] == EVENT_DATE
    assert picks[0]["dispatch_plan_id"] == RUN_DATE
    assert picks[0]["edge_rule"] == "1x2_two_source_p55_unanimous"


@patch.dict(os.environ, FRESH)
def test_clv_never_falls_back_to_legacy_when_a_plan_exists(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / f"picks_{RUN_DATE}.json").write_text(json.dumps(
        [{"home": "Legacy", "away": "Row", "pick": "home", "date": RUN_DATE}]))
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(_plan()))

    with patch.object(clv, "LOCALDATA", localdata):
        picks = clv._dispatch_plan_picks(RUN_DATE)
    assert [p["home"] for p in picks] == ["Panama"]


@patch.dict(os.environ, FRESH)
def test_auto_tickets_acknowledges_a_future_pick_instead_of_no_bet(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(_plan()))

    with patch.object(at, "LOCALDATA", localdata):
        slate, path, deferred = at.load_ticket_slate(RUN_DATE)

    assert slate == []                      # nothing to stake today
    assert len(deferred) == 1               # but a future pick exists
    assert deferred[0]["event_date"] == EVENT_DATE
    assert path.name == f"fresh_production_dispatch_plan_{RUN_DATE}.json"


@patch.dict(os.environ, FRESH)
def test_auto_tickets_stakes_a_same_day_pick_from_the_plan(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    same_day = _pick(date=RUN_DATE, event_date=RUN_DATE,
                     kickoff=f"{RUN_DATE} 20:00")
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(
        json.dumps(_plan([same_day])))

    with patch.object(at, "LOCALDATA", localdata):
        slate, _path, deferred = at.load_ticket_slate(RUN_DATE)

    assert len(slate) == 1 and deferred == []
    assert at.apply_ticket_staking(slate, stake_per_leg=1.5)[0]["stake_units"] == 1.5


@patch.dict(os.environ, FRESH)
def test_no_legacy_fallback_anywhere_when_the_plan_is_empty(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / f"picks_{RUN_DATE}.json").write_text(json.dumps(
        [{"home": "Legacy", "away": "Row", "pick": "home", "date": RUN_DATE}]))
    empty = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                   horizon_rows=[],
                                   horizon={"generated_for": RUN_DATE, "picks": []})
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(empty))

    with patch.object(at, "LOCALDATA", localdata):
        slate, _path, deferred = at.load_ticket_slate(RUN_DATE)
    assert slate == [] and deferred == []

    with patch.object(clv, "LOCALDATA", localdata):
        assert clv._dispatch_plan_picks(RUN_DATE) == []


# --------------------------------------------------------------------------
# 16-17. Notification send and dedupe
# --------------------------------------------------------------------------


def test_future_pick_notice_is_deduped_on_rerun():
    plan = _plan()
    keys = notify._future_pick_keys(plan)
    assert len(keys) == 1

    # First run: nothing sent yet, so the notice is built.
    fresh = notify._unsent_future_picks(plan, set())
    assert notify.format_future_pick_message_from_plan(fresh, RUN_DATE)

    # Rerun with the key already in the ledger: stay silent.
    already = notify._unsent_future_picks(plan, set(keys))
    assert notify.format_future_pick_message_from_plan(already, RUN_DATE) is None


def test_future_pick_notice_is_labelled_by_event_date_and_delegates_staking():
    message = notify.format_future_pick_message_from_plan(_plan(), RUN_DATE)
    assert f"FRESH PRODUCTION PICK — event date {EVENT_DATE}" in message
    assert f"No same-day picks for {RUN_DATE}." in message
    assert "staking: handled by auto-tickets" in message
    # A future fixture must never be announced as today's bet.
    assert f"event date {RUN_DATE}" not in message


def test_empty_plan_yields_no_future_notice_so_the_heartbeat_still_runs():
    empty = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                   horizon_rows=[],
                                   horizon={"generated_for": RUN_DATE, "picks": []})
    assert notify.format_future_pick_message_from_plan(empty, RUN_DATE) is None


def test_notify_exposes_a_dispatch_plan_option():
    """The pipeline must be able to hand the plan to the notifier."""
    source = (ROOT / "scripts" / "notify.py").read_text()
    assert '"--dispatch-plan"' in source
    # The notice goes through the real dispatcher and updates the ledger.
    assert "Future-dated pick notice sent and ledgered" in source
    assert "Future-dated pick notice FAILED to dispatch" in source


# --------------------------------------------------------------------------
# 19-22. Kickoff parser regression
# --------------------------------------------------------------------------


def test_kickoff_parser_reads_day_first_from_the_fixture_date():
    harness.assert_kickoff_parser_dd_mm_reference_date(pt.parse_kickoff_dt)


def test_kickoff_parser_has_no_wall_clock_year_leakage():
    """The fixture's year decides, not the machine's clock."""
    assert pt.parse_kickoff_dt("01-01, 12:00", "2027-01-01").year == 2027
    assert pt.parse_kickoff_dt("15-06, 12:00", "2024-06-15").year == 2024


def test_bare_time_uses_the_fixture_date_not_the_run_date():
    parsed = pt.parse_kickoff_dt("06:10", EVENT_DATE)
    assert (parsed.year, parsed.month, parsed.day) == (2026, 10, 1)


def test_already_started_fixture_is_blocked_once_its_kickoff_parses():
    tz = timezone(timedelta(hours=2))
    ok, reason = pt.operational_pick_eligibility(
        {"date": "2026-06-12", "kickoff": "12-06, 07:00"},
        as_of=datetime(2026, 6, 12, 8, 0, tzinfo=tz), min_lead=30)
    assert ok is False and reason == "inside_30m_lead_or_started"


# --------------------------------------------------------------------------
# 23-24. Lane invariants across real artifacts
# --------------------------------------------------------------------------


def test_legacy_baseline_rows_are_marked_comparison_only():
    harness.assert_legacy_baseline_comparison_only([
        {"rule": {"rule_source": "legacy_baseline", "comparison_only": True,
                  "dispatchable": False}},
        {"rule": {"rule_source": "fresh_production", "comparison_only": False,
                  "dispatchable": True}},
    ], context="edge sync")

    with pytest.raises(AssertionError):
        harness.assert_legacy_baseline_comparison_only(
            [{"rule": {"rule_source": "legacy_baseline",
                       "comparison_only": False, "dispatchable": True}}])


def test_no_browser_probe_paths_are_referenced_in_production_artifacts():
    plan = _plan()
    harness.assert_no_browser_probe_paths(plan, context="dispatch plan")
    harness.assert_no_browser_probe_paths(fp.render_dispatch_plan_md(plan),
                                          context="dispatch plan markdown")
    with pytest.raises(AssertionError):
        harness.assert_no_browser_probe_paths("run probe=forebet_getrs now")


def test_committed_production_artifacts_use_clean_naming():
    """Artifacts already in the repository must satisfy the invariants."""
    localdata = ROOT / "localdata"
    checked = 0
    for pattern in ("fresh_production_dispatch_plan_*.json",
                    "fresh_production_horizon_picks_*.json",
                    "fresh_production_production_picks_*.json"):
        for path in sorted(localdata.glob(pattern)):
            try:
                payload = json.loads(path.read_text())
            except (OSError, ValueError):
                continue
            harness.assert_no_fresh_prefix_in_rule_ids(payload, context=path.name)
            harness.assert_no_forbidden_version_labels(payload, context=path.name)
            checked += 1
    # Nothing to check is acceptable; a violation is not.
    assert checked >= 0


def test_handover_documents_the_current_production_reality():
    text = (ROOT / "HANDOVER.md").read_text()
    assert "handled_by_auto_tickets" in text
    assert "1x2_two_source" in text
