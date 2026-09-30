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
clean = _load("clean_localdata_harness_under_test", "clean_localdata.py")

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
    rows = at._production_slate_rows(_plan())
    harness.check_production_artifact(rows, context="auto ticket payload")


# --------------------------------------------------------------------------
# 9-12. Staking ownership
# --------------------------------------------------------------------------


def test_pick_engine_emits_no_stake_size():
    plan = _plan()
    harness.assert_pick_engine_does_not_emit_stake_size(
        plan["horizon_picks"], context="dispatched selection")
    harness.assert_pick_engine_does_not_emit_stake_size(
        plan["same_day_picks"], context="same-day selection")


def test_pick_engine_emits_a_staking_delegation_marker():
    harness.assert_staking_delegated_to_auto_tickets(
        _plan()["horizon_picks"], context="dispatched selection")
    assert fp.STAKING_POLICY == "handled_by_auto_tickets"
    assert fp.STAKING_OWNER == "auto_tickets"


def test_auto_tickets_is_the_only_staking_engine():
    """No parallel staking path may exist beside plan_day()."""
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    assert "def apply_ticket_staking" not in src, (
        "a flat-unit staking helper is a second staking engine; "
        "plan_day() owns sizing")
    assert src.count("\n    upsert_slip(st,") == 1
    harness.assert_auto_ticket_staking_owns_stake(at)


def test_auto_ticket_stakes_stay_percentage_of_capital():
    """main's contract is percent of capital, never unit notation."""
    pool = [{"match": "A vs B", "pick": "HOME", "prob": 0.72, "odds": 2.25,
             "row": {"bucket": fp.BUCKET_CERTIFIED_CLEAN}},
            {"match": "C vs D", "pick": "HOME", "prob": 0.68, "odds": 1.90,
             "row": {"bucket": fp.BUCKET_CERTIFIED_CLEAN}}]
    plan = at.plan_day(pool, 100.0)
    assert plan, "two qualifying legs should form a card"
    staked = sum(a["stake_pct"] for a in plan)
    assert 0 < staked <= 100.0 * at.STAKE_FRAC + 1e-6
    for acca in plan:
        assert "stake_pct" in acca and "stake_units" not in acca
    # Sizing scales with the bank: that is what "percent of capital" means.
    half = at.plan_day(pool, 50.0)
    assert sum(a["stake_pct"] for a in half) == pytest.approx(staked / 2, rel=1e-6)


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


def _run_tickets(tmp_path, picks, *, run_date=RUN_DATE, force=True,
                 now=None, settled=None, monkey=None):
    """Drive the real auto-ticket engine over a dispatch plan."""
    localdata = tmp_path / "localdata"
    localdata.mkdir(exist_ok=True)
    pl.dispatch_plan_path(run_date, localdata).write_text(json.dumps(_plan(picks)))

    class Args:
        date = run_date
        force = True

    state = at.fresh_state()
    outcomes = {}
    with patch.object(at, "LOCALDATA", localdata), \
         patch.object(at, "STATE_FILE", localdata / "state.json"), \
         patch.object(at, "BUCKET_PNL_FILE", localdata / "pnl.json"), \
         patch.object(at, "load_settled", lambda *a, **k: settled or {}), \
         patch.object(at, "load_archived_picks", lambda *a, **k: []), \
         patch.object(at, "datetime", _FrozenDatetime(now or _DEFAULT_NOW)):
        at.cmd_today(Args(), state)
        outcomes = at.load_ticket_outcomes(run_date, localdata)
    return outcomes, state, localdata


_DEFAULT_NOW = datetime(2026, 9, 30, 10, 0, tzinfo=timezone(timedelta(hours=2)))


class _FrozenDatetime:
    """Stand-in for the datetime module attribute with a pinned now().

    Build-hour and freeze-hour gates read datetime.now(TZ); pinning it keeps
    every ticket assertion deterministic instead of wall-clock dependent.
    """

    def __init__(self, pinned):
        self._pinned = pinned

    def now(self, tz=None):
        return self._pinned if tz is None else self._pinned.astimezone(tz)

    def __getattr__(self, name):
        return getattr(datetime, name)


@patch.dict(os.environ, FRESH)
def test_a_single_future_selection_declines_with_insufficient_legs(tmp_path):
    """One selection is not a bet: the recipe needs two legs per acca."""
    outcomes, state, _ = _run_tickets(tmp_path, [_pick()])

    assert EVENT_DATE in outcomes, "the future event date must be evaluated"
    assert outcomes[EVENT_DATE]["status"] == at.DECLINED_INSUFFICIENT_LEGS
    assert outcomes[EVENT_DATE]["selections"] == 1
    assert not state["open_slips"], "no slip may be opened for a declined card"


@patch.dict(os.environ, FRESH)
def test_two_eligible_future_selections_form_a_real_auto_ticket(tmp_path):
    """The bridge must reach select_accas/plan_day, not a parallel engine."""
    second = _pick(home="Guatemala", away="Suriname", odds=1.95,
                   probability=0.66, kickoff=f"{EVENT_DATE} 09:00")
    outcomes, state, _ = _run_tickets(tmp_path, [_pick(), second])

    assert outcomes[EVENT_DATE]["status"] == at.TICKET_CREATED
    assert outcomes[EVENT_DATE]["accas"] == 1
    # Percentage-of-capital sizing, from plan_day — not units.
    assert outcomes[EVENT_DATE]["staked_pct_of_capital"] > 0
    # The slip is booked under the EVENT date, not the run date.
    assert any(e["date"] == EVENT_DATE for e in state["open_slips"]), (
        "the slip must be booked under the event date, not the run date")


@patch.dict(os.environ, FRESH)
def test_a_production_selection_is_not_automatically_a_ticket(tmp_path):
    outcomes, _state, _ = _run_tickets(tmp_path, [_pick()])
    harness.assert_production_selection_not_automatically_ticket(
        _plan([_pick()]), outcomes)


@patch.dict(os.environ, FRESH)
def test_suspect_price_blocks_ticketing(tmp_path):
    """A quarantined quote must never reach a ticket."""
    a = _pick(price_quarantine_reason="suspect")
    b = _pick(home="Guatemala", away="Suriname", odds=1.95,
              price_quarantine_reason="suspect")
    outcomes, state, _ = _run_tickets(tmp_path, [a, b])

    assert outcomes[EVENT_DATE]["status"] == at.DECLINED_PRICE_INTEGRITY
    assert outcomes[EVENT_DATE]["playable_legs"] == 0
    assert not state["open_slips"]


@patch.dict(os.environ, FRESH)
def test_audit_only_price_blocks_ticketing(tmp_path):
    """price_push_eligible=False is an audit quote, not an execution price."""
    a = _pick(price_push_eligible=False)
    b = _pick(home="Guatemala", away="Suriname", odds=1.95,
              price_push_eligible=False)
    outcomes, _state, _ = _run_tickets(tmp_path, [a, b])
    assert outcomes[EVENT_DATE]["status"] == at.DECLINED_PRICE_INTEGRITY


@patch.dict(os.environ, FRESH)
def test_odds_floor_blocks_ticketing(tmp_path):
    a = _pick(odds=1.05)
    b = _pick(home="Guatemala", away="Suriname", odds=1.02)
    outcomes, _state, _ = _run_tickets(tmp_path, [a, b])
    assert outcomes[EVENT_DATE]["status"] == at.DECLINED_PRICE_INTEGRITY


@patch.dict(os.environ, FRESH)
def test_kickoff_guard_blocks_an_already_started_selection(tmp_path):
    """A fixture already under way at build time cannot be ticketed."""
    started = datetime(2026, 10, 1, 12, 0, tzinfo=timezone(timedelta(hours=2)))
    a = _pick(kickoff=f"{EVENT_DATE} 08:10")
    b = _pick(home="Guatemala", away="Suriname", odds=1.95,
              kickoff=f"{EVENT_DATE} 09:00")
    outcomes, state, _ = _run_tickets(tmp_path, [a, b], now=started)

    assert outcomes[EVENT_DATE]["status"] in (
        at.DECLINED_KICKOFF_GUARD, at.DECLINED_INSUFFICIENT_LEGS)
    assert not state["open_slips"], "a started fixture must not be staked"


@patch.dict(os.environ, FRESH)
def test_a_pnl_benched_bucket_cannot_become_a_ticket(tmp_path):
    """The P&L tripwire closes the door before selection sees the pool."""
    second = _pick(home="Guatemala", away="Suriname", odds=1.95)
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(
        json.dumps(_plan([_pick(), second])))

    class Args:
        date = RUN_DATE
        force = True

    benched = ({fp.BUCKET_CERTIFIED_CLEAN: 0.0},
               {fp.BUCKET_CERTIFIED_CLEAN: {"verdict": "VETO", "weight": 0.0,
                                       "streak": 4, "n": 40, "roi": -0.2,
                                       "grade": "F", "gap": 0.1, "z": -2.0}})
    state = at.fresh_state()
    with patch.object(at, "LOCALDATA", localdata), \
         patch.object(at, "STATE_FILE", localdata / "state.json"), \
         patch.object(at, "load_settled", lambda *a, **k: {}), \
         patch.object(at, "load_archived_picks", lambda *a, **k: []), \
         patch.object(at, "compute_bucket_pnl", lambda *a, **k: benched), \
         patch.object(at, "datetime", _FrozenDatetime(_DEFAULT_NOW)):
        at.cmd_today(Args(), state)
        outcomes = at.load_ticket_outcomes(RUN_DATE, localdata)

    assert outcomes[EVENT_DATE]["status"] == at.DECLINED_BUCKET_PNL_BENCHED
    assert fp.BUCKET_CERTIFIED_CLEAN in outcomes[EVENT_DATE]["benched_buckets"]
    harness.assert_benching_state_respected(outcomes[EVENT_DATE])
    assert not state["open_slips"]


@patch.dict(os.environ, FRESH)
def test_a_selection_ladder_benched_bucket_cannot_become_a_ticket(tmp_path):
    second = _pick(home="Guatemala", away="Suriname", odds=1.95)
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(
        json.dumps(_plan([_pick(), second])))

    class Args:
        date = RUN_DATE
        force = True

    state = at.fresh_state()
    with patch.object(at, "LOCALDATA", localdata), \
         patch.object(at, "STATE_FILE", localdata / "state.json"), \
         patch.object(at, "load_settled", lambda *a, **k: {}), \
         patch.object(at, "load_archived_picks", lambda *a, **k: []), \
         patch.object(at, "compute_bucket_slice",
                      lambda *a, **k: (
                          {"bench_buckets": [fp.BUCKET_CERTIFIED_CLEAN],
                           "rank_caps": {}},
                          {b: {"verdict": "VETO", "action": "BENCHED",
                               "n": 30, "roi": -0.3, "recent_roi": -0.3,
                               "grade": "F", "demote_streak": 2,
                               "bench_streak": 4, "rank_cap": None}
                           for b in at.BUCKETS})), \
         patch.object(at, "datetime", _FrozenDatetime(_DEFAULT_NOW)):
        at.cmd_today(Args(), state)
        outcomes = at.load_ticket_outcomes(RUN_DATE, localdata)

    assert outcomes[EVENT_DATE]["status"] == at.DECLINED_SELECTION_LADDER_BENCHED
    harness.assert_benching_state_respected(outcomes[EVENT_DATE])
    assert not state["open_slips"]


def test_the_assayer_is_on_the_production_ticket_path():
    harness.assert_auto_tickets_assayer_not_bypassed(at)


def test_the_production_bucket_is_a_scored_door():
    """An unregistered bucket is invisible to playable_legs and to benching."""
    assert fp.BUCKET_CERTIFIED_CLEAN in at.BUCKETS, (
        "production selections must belong to a bucket the assayer scores, "
        "otherwise benching can never apply to them")
    assert not fp.BUCKET_CERTIFIED_CLEAN.lower().startswith("fresh_")
    # The lane must never mint a bucket of its own.
    assert not any(b.startswith("PRODUCTION") for b in at.BUCKETS)


@patch.dict(os.environ, FRESH)
def test_same_day_only_policy_declines_with_an_explicit_reason(tmp_path, capsys):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(_plan()))

    class Args:
        date = RUN_DATE
        force = True

    with patch.object(at, "LOCALDATA", localdata), \
         patch.object(at, "HORIZON_TICKET_POLICY", "same_day_only"), \
         patch.object(at, "STATE_FILE", localdata / "state.json"), \
         patch.object(at, "load_settled", lambda *a, **k: {}), \
         patch.object(at, "load_archived_picks", lambda *a, **k: []), \
         patch.object(at, "datetime", _FrozenDatetime(_DEFAULT_NOW)):
        at.cmd_today(Args(), at.fresh_state())
    out = capsys.readouterr().out
    assert "future-dated production selection exists, but auto-tickets are " \
           "same-day-only" in out
    assert at.DECLINED_SAME_DAY_ONLY_POLICY in out


@patch.dict(os.environ, FRESH)
def test_an_empty_same_day_file_never_prints_a_bare_no_bet_today(tmp_path, capsys):
    """The exact defect from the live run."""
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / f"fresh_production_production_picks_{RUN_DATE}.json").write_text("[]")
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(_plan()))

    class Args:
        date = RUN_DATE
        force = True

    with patch.object(at, "LOCALDATA", localdata), \
         patch.object(at, "STATE_FILE", localdata / "state.json"), \
         patch.object(at, "load_settled", lambda *a, **k: {}), \
         patch.object(at, "load_archived_picks", lambda *a, **k: []), \
         patch.object(at, "datetime", _FrozenDatetime(_DEFAULT_NOW)):
        at.cmd_today(Args(), at.fresh_state())
    out = capsys.readouterr().out
    assert "NO BET TODAY" not in out
    assert EVENT_DATE in out
    assert at.DECLINED_INSUFFICIENT_LEGS in out


@patch.dict(os.environ, FRESH)
def test_no_legacy_fallback_when_the_plan_is_empty(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / f"picks_{RUN_DATE}.json").write_text(json.dumps(
        [{"home": "Legacy", "away": "Row", "pick": "home", "date": RUN_DATE,
          "bucket": "CERTIFIED_CLEAN", "avg_p": 70, "odds": 2.0}]))
    empty = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                   horizon_rows=[],
                                   horizon={"generated_for": RUN_DATE, "picks": []})
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(empty))

    with patch.object(at, "LOCALDATA", localdata):
        rows, path, dates = at.load_production_slate(RUN_DATE)
    assert rows == [] and dates == []
    assert "dispatch_plan" in path.name
    harness.assert_no_legacy_fallback(rows)

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


def test_a_declined_selection_is_not_announced_as_a_ticket():
    """The notice must not call a selection a bet auto-tickets refused."""
    declined = {EVENT_DATE: {"status": "declined_insufficient_legs"}}
    message = notify.format_future_pick_message_from_plan(
        _plan(), RUN_DATE, declined)
    assert f"PRODUCTION SELECTION — event date {EVENT_DATE}" in message
    assert "PRODUCTION TICKET" not in message
    assert "auto-ticket action: declined_insufficient_legs" in message
    assert "staking: not assigned because no ticket was created" in message
    assert f"No same-day picks for {RUN_DATE}." in message
    assert f"event date {RUN_DATE}" not in message
    harness.check_production_artifact(message, context="declined notice")


def test_an_accepted_selection_is_announced_as_a_ticket():
    created = {EVENT_DATE: {"status": "ticket_created"}}
    message = notify.format_future_pick_message_from_plan(
        _plan(), RUN_DATE, created)
    assert f"PRODUCTION TICKET — event date {EVENT_DATE}" in message
    assert "auto-ticket action: ticket_created" in message
    assert "staking: handled by auto-tickets" in message
    harness.check_production_artifact(message, context="ticket notice")


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


def test_invalid_generated_artifacts_are_deleted_not_backed_up(tmp_path):
    """Wrong artifacts are deleted; a .bak of a wrong file is still wrong."""
    bad = tmp_path / "fresh_production_dispatch_plan_2026-09-30.json"
    bad.write_text(json.dumps({"rule_id": "fresh_1x2_v2_p55_unanimous"}))
    good = tmp_path / "fresh_production_dispatch_plan_2026-10-01.json"
    good.write_text(json.dumps({"rule_id": "1x2_two_source_p55_unanimous"}))
    raw = tmp_path / "capture_zulubet_2026-09-30.csv.gz"
    raw.write_bytes(b"fresh_1x2_v2_p55_unanimous")

    deleted = clean.purge_invalid_generated_artifacts(
        tmp_path, write_manifest=True, today=date(2026, 9, 30))

    assert [e["deleted_file"] for e in deleted] == [bad.name]
    assert not bad.exists()
    assert good.exists(), "a clean artifact must survive"
    assert raw.exists(), "raw evidence is never purged by content"
    harness.assert_no_backup_wrong_artifacts_created(tmp_path)
    harness.assert_wrong_generated_artifacts_deleted([good])

    manifest = json.loads(
        (tmp_path / "invalid_artifact_purge_2026-09-30.json").read_text())
    assert manifest["raw_evidence_preserved"] is True
    assert manifest["backup_created"] is False
    entry = manifest["deleted"][0]
    for field in ("deleted_file", "reason", "replacement_file_if_any",
                  "raw_evidence_preserved", "backup_created"):
        assert field in entry


def test_stake_notation_makes_a_generated_artifact_invalid(tmp_path):
    bad = tmp_path / "fresh_production_horizon_picks_2026-09-30.md"
    bad.write_text("| Panama vs New Zealand | home | stake: 1.0u |")
    deleted = clean.purge_invalid_generated_artifacts(tmp_path)
    assert [e["deleted_file"] for e in deleted] == [bad.name]
    assert not bad.exists()


def test_committed_localdata_holds_no_backups_of_wrong_artifacts():
    harness.assert_no_backup_wrong_artifacts_created(ROOT / "localdata")


def test_handover_documents_the_current_production_reality():
    text = (ROOT / "HANDOVER.md").read_text()
    assert "handled_by_auto_tickets" in text
    assert "1x2_two_source" in text
