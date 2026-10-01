"""The production summary must report what actually happened.

The defect these tests lock out: a future-dated production selection that
auto_tickets had evaluated and declined was reported to the operator as
"auto-ticket action: not evaluated / assayer action: not run (no selections
reached the ticket engine)". The selection had reached the ticket engine.

The rule is one of authority: a stage's outcome may only be reported from
the artifact that stage wrote. The pick engine's block is preliminary by
construction; the final summary is rendered afterwards.
"""

from __future__ import annotations

import csv
import gzip
import importlib.util
import io
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


fp = _load("fresh_production_summary_under_test", "fresh_production.py")
at = _load("auto_tickets_summary_under_test", "auto_tickets.py")
notify = _load("notify_summary_under_test", "notify.py")
clv = _load("audit_clv_summary_under_test", "audit_clv.py")

from edgefactory import production_lane as pl          # noqa: E402
from edgefactory import production_summary as ps       # noqa: E402

RUN_DATE = "2026-09-30"
EVENT_DATE = "2026-10-01"
RULE = "1x2_two_source_p55_unanimous"
FRESH = {"EDGE_FACTORY_PRODUCTION_LANE": "fresh_production"}
DECLINE = "declined_insufficient_legs"

_NOW = datetime(2026, 9, 30, 10, 0, tzinfo=timezone(timedelta(hours=2)))


class _FrozenDatetime:
    """datetime stand-in with a pinned now(), for deterministic build hours."""

    def __init__(self, pinned):
        self._pinned = pinned

    def now(self, tz=None):
        return self._pinned if tz is None else self._pinned.astimezone(tz)

    def __getattr__(self, name):
        return getattr(datetime, name)


def _pick(**overrides):
    row = {
        "date": EVENT_DATE, "event_date": EVENT_DATE,
        "kickoff": f"{EVENT_DATE} 08:10", "league": "World Cup Qualification",
        "home": "Panama", "away": "New Zealand", "selection": "home",
        "rule_id": RULE, "probability": 0.72, "odds": 2.25,
        "implied_probability": 0.4444, "edge": 0.1403, "dispatchable": True,
        "internal_stake_units": 1.0, "dispatch_method": "certified_rule",
        "pricing_source": "bzzoiro", "timing_source": "zulubet",
        "source_voters": ["zulubet", "vitibet"], "price_match_method": "exact",
        "price_tier": "dedicated_pricing_feed", "bookmaker": "bet365",
        "model_version": "m1", "feature_schema_version": "s1",
        "walkforward_evidence": {}, "price_push_eligible": True,
        "staking_policy": fp.STAKING_POLICY, "staking_owner": fp.STAKING_OWNER,
    }
    row.update(overrides)
    return row


def _plan(picks=None, *, same_day=False):
    """A dispatch plan whose selections are same-day or future-dated.

    same_day=True models the ordinary case the daily run cards: the
    selections fall on the run date itself.
    """
    picks = [_pick()] if picks is None else picks
    if same_day:
        # Same shaping the lane applies to any dispatch row; only the
        # event date differs, which is the whole point of the fixture.
        shaped = fp.horizon_pick_rows(
            {"generated_for": RUN_DATE, "picks": picks})
        rows = [dict(r, date=RUN_DATE, event_date=RUN_DATE,
                     kickoff=f"{RUN_DATE} 20:00") for r in shaped]
        empty_horizon = {"generated_for": RUN_DATE, "horizon_end": RUN_DATE,
                         "min_lead_minutes": 30, "max_lead_hours": 48,
                         "eligible_pick_count": 0, "picks": []}
        return fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=rows,
                                      horizon_rows=[], horizon=empty_horizon)
    horizon = {"generated_for": RUN_DATE, "horizon_end": "2026-10-02",
               "min_lead_minutes": 30, "max_lead_hours": 48,
               "eligible_pick_count": len(picks), "picks": picks}
    return fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)


def _localdata(tmp_path, picks=None, *, same_day=False):
    """The 2026-09-30 run shape: empty same-day file, one future selection."""
    d = tmp_path / "localdata"
    d.mkdir(exist_ok=True)
    (d / f"fresh_production_production_picks_{RUN_DATE}.json").write_text("[]")
    pl.dispatch_plan_path(RUN_DATE, d).write_text(
        json.dumps(_plan(picks, same_day=same_day)))
    return d


def _run_auto_tickets(localdata):
    """Drive the real ticket engine over the plan, as the pipeline does."""

    class Args:
        # The bare daily invocation: auto_tickets targets local today.
        date = RUN_DATE
        force = True

    state = at.fresh_state()
    with patch.object(at, "LOCALDATA", localdata), \
         patch.object(at, "STATE_FILE", localdata / "state.json"), \
         patch.object(at, "BUCKET_PNL_FILE", localdata / "pnl.json"), \
         patch.object(at, "load_settled", lambda *a, **k: {}), \
         patch.object(at, "load_archived_picks", lambda *a, **k: []), \
         patch.object(at, "datetime", _FrozenDatetime(_NOW)):
        at.cmd_today(Args(), state)
    return state


def _write_supabase_manifest(localdata, event_date=EVENT_DATE, rows=1):
    (localdata / f"supabase_sync_manifest_{event_date}.json").write_text(
        json.dumps({"target_date": event_date, "row_count": rows,
                    "sync_mode": "authoritative_replace"}))


def _write_clv_snapshot(localdata, ticket_status=DECLINE, rows=1,
                        event_date=EVENT_DATE):
    path = localdata / f"clv_snapshots_{RUN_DATE[:7]}.csv.gz"
    fields = ["run_date", "event_date", "home", "away", "selection", "odds",
              "pricing_source", "dispatch_plan_id", "rule_id", "ticket_status"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for i in range(rows):
        writer.writerow({
            "run_date": RUN_DATE, "event_date": event_date,
            "home": f"Panama{i or ''}", "away": "New Zealand",
            "selection": "home", "odds": "2.25", "pricing_source": "bzzoiro",
            "dispatch_plan_id": RUN_DATE, "rule_id": RULE,
            "ticket_status": ticket_status})
    with gzip.open(path, "wt", newline="") as fh:
        fh.write(buf.getvalue())
    return path


def _write_sent_ledger(localdata, keys=None):
    keys = keys or [f"__future_pick__|{EVENT_DATE}|Panama|New Zealand|home"]
    (localdata / f"sent_ledger_{RUN_DATE}.json").write_text(json.dumps(keys))


# ===========================================================================
# A. The final summary must reflect the post-auto-ticket state
# ===========================================================================


@patch.dict(os.environ, FRESH)
def test_final_summary_reports_the_actual_auto_ticket_verdict(tmp_path):
    """The exact run 36767213800 shape, end to end."""
    localdata = _localdata(tmp_path, same_day=True)
    _run_auto_tickets(localdata)
    _write_supabase_manifest(localdata, event_date=RUN_DATE)
    _write_clv_snapshot(localdata, event_date=RUN_DATE)
    _write_sent_ledger(localdata)

    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))

    assert "FINAL PRODUCTION SUMMARY" in text
    assert "production selections:         1" in text
    assert f"event dates:                   {RUN_DATE}" in text
    assert "Supabase selections published: 1" in text
    assert "CLV snapshots captured:        1 row(s)" in text
    assert "CLV latest production selections: 1" in text
    assert f"CLV latest ticket_status:      {DECLINE}=1" in text
    # A ledger entry alone proves a notice exists, not that this run
    # sent it, so the summary reports the ledger without claiming a send.
    assert "ledgered_run_unknown" in text
    assert f"auto-ticket action:            {RUN_DATE}: {DECLINE}" in text
    assert DECLINE in text
    assert "staking owner:                 auto_tickets" in text
    assert "staking assigned:              no" in text


@patch.dict(os.environ, FRESH)
def test_final_summary_never_calls_an_evaluated_selection_unevaluated(tmp_path):
    """The defect itself: the selection did reach the ticket engine."""
    localdata = _localdata(tmp_path, same_day=True)
    _run_auto_tickets(localdata)
    _write_supabase_manifest(localdata, event_date=RUN_DATE)
    _write_clv_snapshot(localdata, event_date=RUN_DATE)
    _write_sent_ledger(localdata)

    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))

    assert "auto-ticket action:            not evaluated" not in text
    assert "not run (no selections reached the ticket engine)" not in text
    assert "assayer action:                did not run" not in text
    # It ran, and it says so.
    assert "assayer action:                ran" in text


@patch.dict(os.environ, FRESH)
def test_final_summary_lists_the_selection_with_its_ticket_verdict(tmp_path):
    localdata = _localdata(tmp_path, same_day=True)
    _run_auto_tickets(localdata)
    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))
    assert f"SELECTION {RUN_DATE}" in text
    assert "Panama vs New Zealand" in text
    assert f"auto-ticket: {DECLINE}" in text
    assert RULE in text


@patch.dict(os.environ, FRESH)
def test_final_summary_reports_a_created_ticket_as_created(tmp_path):
    """Two eligible legs clear the 2-leg contract and the summary says so."""
    second = _pick(home="Guatemala", away="Suriname", odds=1.95,
                   probability=0.66)
    localdata = _localdata(tmp_path, [_pick(), second], same_day=True)
    _run_auto_tickets(localdata)

    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))
    assert f"auto-ticket action:            {RUN_DATE}: ticket_created" in text
    assert "ticket status:                 1 ticket(s) created" in text
    assert "staking assigned:              percentage of capital / free bank" in text
    assert DECLINE not in text


def test_final_summary_says_a_stage_did_not_run_rather_than_guessing(tmp_path):
    """No auto-ticket artifact means no verdict may be invented."""
    localdata = _localdata(tmp_path)   # auto_tickets deliberately not run
    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))

    assert "auto-ticket action:            did not run" in text
    assert "assayer action:                did not run" in text
    assert "Supabase selections published: 0 (no sync manifest found)" in text
    assert "notification:                  did not run" in text
    # "did not run" is an honest absence; "not evaluated" reads as a verdict.
    assert "nothing to evaluate" not in text


# ===========================================================================
# B. The pre-ticket block must not pose as the verdict
# ===========================================================================


def test_pre_ticket_block_is_labelled_preliminary():
    plan = _plan()
    text = "\n".join(fp.render_dispatch_plan_summary(plan, {"blocker_counts": {}}))
    assert "PRELIMINARY (pre-ticket)" in text
    assert "auto-ticket action:            pending" in text
    assert "FINAL PRODUCTION SUMMARY" in text   # points at the real verdict


def test_pre_ticket_block_omits_every_downstream_result_field():
    """It runs before those stages, so it cannot report them."""
    plan = _plan()
    text = "\n".join(fp.render_dispatch_plan_summary(plan, {"blocker_counts": {}}))
    for field in ("ticket status:", "assayer action:", "benching action:",
                  "staking assigned:", "CLV snapshots captured:",
                  "Supabase selections published:"):
        assert field not in text, f"pre-ticket block must not report {field!r}"


def test_pre_ticket_block_never_says_not_evaluated_or_not_run():
    plan = _plan()
    text = "\n".join(fp.render_dispatch_plan_summary(plan, {"blocker_counts": {}}))
    assert "not evaluated" not in text
    assert "no selections reached the ticket engine" not in text


def test_pre_ticket_block_still_shows_the_selection_and_staking_owner():
    """Relabelling must not cost the operator the planning information."""
    text = "\n".join(fp.render_dispatch_plan_summary(_plan(),
                                                     {"blocker_counts": {}}))
    assert "production selections:         1" in text
    assert f"FUTURE {EVENT_DATE}" in text
    assert "staking owner:                 auto_tickets" in text
    assert "stake_units" not in text and "1.0u" not in text


# ===========================================================================
# C. CLV ticket_status is captured, counted and auditable
# ===========================================================================


@patch.dict(os.environ, FRESH)
def test_clv_captures_the_selection_even_when_auto_tickets_declines(tmp_path):
    localdata = _localdata(tmp_path, same_day=True)
    _run_auto_tickets(localdata)

    with patch.object(clv, "LOCALDATA", localdata):
        picks = clv._dispatch_plan_picks(RUN_DATE)

    assert len(picks) == 1, "a declined selection is still captured"
    assert picks[0]["ticket_status"] == DECLINE
    assert picks[0]["date"] == RUN_DATE       # dispatch-time price, event date
    assert picks[0]["edge_rule"] == RULE


def test_clv_ticket_status_is_a_snapshot_column():
    assert "ticket_status" in clv.SNAPSHOT_FIELDS
    assert "dispatch_plan_id" in clv.SNAPSHOT_FIELDS
    assert "event_date" in clv.SNAPSHOT_FIELDS


def test_clv_ticket_status_counts_are_computed():
    rows = [{"ticket_status": DECLINE}, {"ticket_status": DECLINE},
            {"ticket_status": "ticket_created"}, {"ticket_status": ""}]
    counts = clv.ticket_status_counts(rows)
    assert counts == {DECLINE: 2, "ticket_created": 1, "unknown": 1}


def test_clv_capture_logs_a_ticket_status_count():
    src = (ROOT / "scripts" / "audit_clv.py").read_text()
    assert "CLV latest ticket_status: " in src


@patch.dict(os.environ, FRESH)
def test_pending_at_pick_time_becomes_final_at_end_of_run(tmp_path):
    """Before auto_tickets the status is pending; afterwards it is the verdict.

    'unknown' conflated "not decided yet" with "we lost track"; pending
    says which one it is.
    """
    localdata = _localdata(tmp_path, same_day=True)

    with patch.object(clv, "LOCALDATA", localdata):
        early = clv._dispatch_plan_picks(RUN_DATE)
    assert early[0]["ticket_status"] == clv.PENDING_TICKET_STATUS

    _run_auto_tickets(localdata)
    with patch.object(clv, "LOCALDATA", localdata):
        late = clv._dispatch_plan_picks(RUN_DATE)
    assert late[0]["ticket_status"] == DECLINE


def test_clv_counts_do_not_inflate_unique_selections(tmp_path):
    """One selection stays one row, whatever its ticket status."""
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    _write_clv_snapshot(localdata, rows=1)
    status = ps.collect_production_status(RUN_DATE, localdata)
    assert len(status["clv_rows"]) == 1
    assert status["clv_ticket_status_counts"] == {DECLINE: 1}


# ===========================================================================
# D. Notification keeps selection/ticket distinct
# ===========================================================================


def test_notification_says_selection_not_ticket_when_declined():
    message = notify.format_future_pick_message_from_plan(
        _plan(), RUN_DATE, {EVENT_DATE: {"status": DECLINE}})
    assert f"PRODUCTION SELECTION — event date {EVENT_DATE}" in message
    assert "PRODUCTION TICKET" not in message
    assert f"auto-ticket action: {DECLINE}" in message
    assert "staking: not assigned because no ticket was created" in message


def test_notification_shows_no_stake_size():
    message = notify.format_future_pick_message_from_plan(
        _plan(), RUN_DATE, {EVENT_DATE: {"status": DECLINE}})
    for forbidden in ("1.0u", "1u", "stake: 1", "stake_units", "stake_size"):
        assert forbidden not in message
    assert RULE in message
    assert "fresh_" not in message
    for label in ("_v1_", "_v2_", "_v3_"):
        assert label not in message


# ===========================================================================
# E. The summary must not become a second source of truth
# ===========================================================================


def test_only_the_final_summary_reports_downstream_results():
    """Exactly one renderer may state the verdict."""
    engine = (ROOT / "scripts" / "fresh_production.py").read_text()
    assert "FINAL PRODUCTION SUMMARY" not in engine.replace(
        "FINAL PRODUCTION SUMMARY after auto_tickets", "")
    assert "auto-ticket action:            pending" in engine


def test_daily_prints_the_final_summary_after_the_downstream_stages():
    src = (ROOT / "scripts" / "daily.py").read_text()
    assert "print_final_production_summary(target_date)" in src
    order = [src.index("auto_tickets (ticket formation, staking, freeze)"),
             src.index("audit_clv.py capture --date {target_date} --label end_of_run"),
             src.index('_notify(target_date, "notify (Smart Dispatch'),
             src.index("print_final_production_summary(target_date)")]
    assert order == sorted(order), (
        "the final summary must be printed after auto_tickets, CLV and notify")


def test_final_summary_carries_no_stake_size(tmp_path):
    localdata = _localdata(tmp_path)
    _run_auto_tickets(localdata)
    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))
    for forbidden in ("1.0u", " 1u", "stake_units", "stake_size", "stake: 1"):
        assert forbidden not in text
    assert "staking owner:                 auto_tickets" in text


def test_final_summary_uses_clean_rule_ids(tmp_path):
    localdata = _localdata(tmp_path)
    _run_auto_tickets(localdata)
    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))
    assert RULE in text
    assert "fresh_1x2_" not in text
    for label in ("_v1_", "_v2_", "_v3_"):
        assert label not in text


def test_production_certified_stays_registered_for_assay_and_bench():
    assert fp.BUCKET_CERTIFIED_CLEAN in at.BUCKETS


def test_a_single_selection_still_declines_under_the_two_leg_contract(tmp_path):
    """The betting contract is unchanged by the reporting fix."""
    assert at.LEGS_PER_ACCA == 2
    localdata = _localdata(tmp_path, same_day=True)
    state = _run_auto_tickets(localdata)
    outcomes = at.load_ticket_outcomes(RUN_DATE, localdata)
    assert outcomes[RUN_DATE]["status"] == DECLINE
    assert not state["open_slips"]


# ---------------------------------------------------------------------------
# Supabase manifest lookup
#
# sync_supabase writes ONE manifest, named for the run date, whose
# row_count covers every pick that run published including future-dated
# ones. Looking only for a per-event-date manifest found nothing and
# reported a successful publish as "no sync manifest found".
# ---------------------------------------------------------------------------


def test_run_date_manifest_is_found_for_a_future_event_date(tmp_path):
    (tmp_path / "supabase_sync_manifest_2026-09-30.json").write_text(json.dumps(
        {"target_date": "2026-09-30", "row_count": 1,
         "sync_mode": "authoritative_replace"}))

    published = ps.read_supabase_published(
        ["2026-10-01"], tmp_path, run_date="2026-09-30")

    assert published == {"2026-09-30": 1}
    assert sum(published.values()) == 1


def test_a_per_event_date_manifest_still_wins_when_present(tmp_path):
    (tmp_path / "supabase_sync_manifest_2026-10-01.json").write_text(
        json.dumps({"target_date": "2026-10-01", "row_count": 2}))
    (tmp_path / "supabase_sync_manifest_2026-09-30.json").write_text(
        json.dumps({"target_date": "2026-09-30", "row_count": 9}))

    published = ps.read_supabase_published(
        ["2026-10-01"], tmp_path, run_date="2026-09-30")

    assert published == {"2026-10-01": 2}


def test_a_genuinely_absent_manifest_is_still_reported_absent(tmp_path):
    published = ps.read_supabase_published(
        ["2026-10-01"], tmp_path, run_date="2026-09-30")
    assert published == {}


def test_summary_reports_the_published_count_it_actually_found(tmp_path):
    (tmp_path / "supabase_sync_manifest_2026-09-30.json").write_text(
        json.dumps({"target_date": "2026-09-30", "row_count": 1}))
    published = ps.read_supabase_published(
        ["2026-10-01"], tmp_path, run_date="2026-09-30")
    assert "no sync manifest found" not in str(published)
    assert published


# ---------------------------------------------------------------------------
# CLV ticket_status persistence
#
# ticket_status was declared in FIELDS but never written into the row, so
# every snapshot persisted blank and every report read "unknown". And a
# second capture skipped the row as a duplicate, so a verdict reached
# after pick time could never land on the row it belonged to.
# ---------------------------------------------------------------------------


def test_capture_row_actually_carries_ticket_status():
    src = (ROOT / "scripts" / "audit_clv.py").read_text()
    build = src.split('"dispatch_plan_id":')[1].split("rows.append")[0]
    assert '"ticket_status"' in build, "the written row must set ticket_status"


def test_a_later_capture_updates_status_instead_of_skipping(tmp_path):
    """Deduplication must not freeze a row's status."""
    path = tmp_path / "clv_snapshots_2026-09.csv.gz"
    existing = {"pick_id": "p1", "snapshot_label": "pick_time",
                "source_run_date": RUN_DATE, "run_date": RUN_DATE,
                "ticket_status": clv.PENDING_TICKET_STATUS}
    merged = {clv._dedupe_key(existing): dict(existing)}

    incoming = dict(existing, ticket_status=DECLINE)
    key = clv._dedupe_key(incoming)
    assert key in merged

    row = merged[key]
    for field in clv.MUTABLE_FIELDS:
        new = str(incoming.get(field) or "").strip()
        if new and new != str(row.get(field) or "").strip():
            row[field] = new

    assert merged[key]["ticket_status"] == DECLINE
    assert len(merged) == 1, "updating must not add a logical pick"


def test_a_settled_verdict_is_never_regressed_to_pending():
    src = (ROOT / "scripts" / "audit_clv.py").read_text()
    assert "Never regress a settled verdict back to pending" in src
    assert "new_value == PENDING_TICKET_STATUS and old_value" in src


def test_capture_reports_updates_separately_from_duplicates():
    src = (ROOT / "scripts" / "audit_clv.py").read_text()
    assert "rows updated:" in src
    assert "duplicates unchanged:" in src


def test_status_counts_cover_the_runs_persisted_rows():
    """A verdict already settled must show even when no new row is added."""
    src = (ROOT / "scripts" / "audit_clv.py").read_text()
    assert 'str(r.get("run_date") or "") == run_date' in src


def test_ticket_status_counts_treat_blank_as_unknown():
    assert clv.ticket_status_counts([{"ticket_status": ""}]) == {"unknown": 1}
    assert clv.ticket_status_counts(
        [{"ticket_status": DECLINE}, {"ticket_status": DECLINE}]) == {DECLINE: 2}


# ---------------------------------------------------------------------------
# Notification outcome accuracy
#
# notify logged "Nothing new to send. Staying silent." while the final
# summary reported "PRODUCTION SELECTION notice sent and ledgered". The
# sent ledger is cumulative, so it cannot distinguish a notice this run
# dispatched from one an earlier run did.
# ---------------------------------------------------------------------------


def _write_notify_result(localdata, outcome, notices=1, detail=""):
    (localdata / f"notification_result_{RUN_DATE}.json").write_text(json.dumps(
        {"run_date": RUN_DATE, "outcome": outcome,
         "future_notices": notices, "detail": detail}))


def test_a_deduped_notice_is_never_reported_as_sent(tmp_path):
    _write_notify_result(tmp_path, ps.NOTIFY_DEDUPED)
    result = ps.read_notification_result(RUN_DATE, tmp_path)

    assert result["outcome"] == ps.NOTIFY_DEDUPED
    assert result["ran"] is True


def test_the_four_outcomes_render_distinctly(tmp_path):
    seen = set()
    for outcome in (ps.NOTIFY_SENT_THIS_RUN, ps.NOTIFY_DEDUPED,
                    ps.NOTIFY_SKIPPED_NO_PICKS, ps.NOTIFY_FAILED):
        _write_notify_result(tmp_path, outcome)
        status = {"run_date": RUN_DATE, "plan": {}, "ticket_outcomes": {},
                  "supabase_published": {}, "clv_rows": [],
                  "clv_ticket_status_counts": {},
                  "notification": ps.read_notification_result(RUN_DATE, tmp_path)}
        line = [l for l in ps.render_final_summary(status)
                if "notification:" in l][0]
        assert outcome in line, f"{outcome} not named in: {line}"
        seen.add(line)
    assert len(seen) == 4, "outcomes must not render identically"


def test_a_failed_send_is_not_presented_as_success(tmp_path):
    _write_notify_result(tmp_path, ps.NOTIFY_FAILED)
    status = {"run_date": RUN_DATE, "plan": {}, "ticket_outcomes": {},
              "supabase_published": {}, "clv_rows": [],
              "clv_ticket_status_counts": {},
              "notification": ps.read_notification_result(RUN_DATE, tmp_path)}
    line = [l for l in ps.render_final_summary(status)
            if "notification:" in l][0]
    assert "do not assume the message arrived" in line
    assert "sent_this_run" not in line


def test_an_absent_result_and_ledger_reports_did_not_run(tmp_path):
    result = ps.read_notification_result(RUN_DATE, tmp_path)
    assert result["ran"] is False
    assert result["outcome"] == ps.NOTIFY_DID_NOT_RUN


def test_notify_records_its_own_outcome():
    src = (ROOT / "scripts" / "notify.py").read_text()
    assert "def write_notification_result" in src
    # Both the silent path and the dispatch path must record what happened.
    assert "NOTIFY_DEDUPED if had_candidates else NOTIFY_SKIPPED_NO_PICKS" in src
    assert "NOTIFY_FAILED if any_failed else NOTIFY_SENT_THIS_RUN" in src


# ===========================================================================
# Supabase per-event-date attribution
#
# A run publishes future-dated selections alongside same-day ones under a
# manifest named for the run date. Reporting the total against the run
# date alone claims every selection was for that date.
# ===========================================================================


def test_publish_breakdown_follows_the_event_dates_the_sync_recorded(tmp_path):
    localdata = _localdata(tmp_path)
    (localdata / f"supabase_sync_manifest_{RUN_DATE}.json").write_text(
        json.dumps({"target_date": RUN_DATE, "row_count": 4,
                    "row_counts_by_event_date": {"2026-10-01": 2,
                                                 "2026-10-02": 2},
                    "sync_mode": "authoritative_replace"}))

    published = ps.read_supabase_published(
        ["2026-10-01", "2026-10-02"], localdata, run_date=RUN_DATE)

    assert published == {"2026-10-01": 2, "2026-10-02": 2}
    assert sum(published.values()) == 4


def test_the_summary_prints_every_event_date_it_published_to(tmp_path):
    localdata = _localdata(tmp_path)
    (localdata / f"supabase_sync_manifest_{RUN_DATE}.json").write_text(
        json.dumps({"target_date": RUN_DATE, "row_count": 4,
                    "row_counts_by_event_date": {"2026-10-01": 2,
                                                 "2026-10-02": 2}}))

    line = next(ln for ln in ps.render_final_summary({
        "run_date": RUN_DATE,
        "plan": {"same_day_pick_count": 2, "horizon_pick_count": 2,
                 "event_dates": ["2026-10-01", "2026-10-02"]},
        "supabase_published": ps.read_supabase_published(
            ["2026-10-01", "2026-10-02"], localdata, run_date=RUN_DATE),
    }) if "Supabase selections published" in ln)

    assert "4 (2026-10-01=2, 2026-10-02=2)" in line


def test_a_total_without_a_breakdown_is_not_split_across_dates(tmp_path):
    """An old manifest states a total only; inventing a split would lie."""
    localdata = _localdata(tmp_path)
    (localdata / f"supabase_sync_manifest_{RUN_DATE}.json").write_text(
        json.dumps({"target_date": RUN_DATE, "row_count": 4}))

    published = ps.read_supabase_published(
        ["2026-10-01", "2026-10-02"], localdata, run_date=RUN_DATE)

    assert published == {RUN_DATE: 4}


# ===========================================================================
# CLV latest status vs raw snapshots
#
# Run 36783344791 captured 8 snapshots for 4 selections and reported
# deferred_before_build_hour=2, pending_auto_tickets=4, ticket_created=2
# — superseded states presented as final, over an inflated pick count.
# ===========================================================================


def _snapshots():
    rows = []
    for i, (home, away, final) in enumerate([
            ("Panama", "New Zealand", "deferred_before_build_hour"),
            ("Ecuador", "Canada", "deferred_before_build_hour"),
            ("Belgium", "Turkey", "ticket_created"),
            ("Hungary", "Georgia", "ticket_created")]):
        rows.append({"pick_id": f"p{i}", "home": home, "away": away,
                     "captured_at_utc": "2026-10-01T06:00:00Z",
                     "snapshot_label": "dispatch",
                     "ticket_status": "pending_auto_tickets"})
        rows.append({"pick_id": f"p{i}", "home": home, "away": away,
                     "captured_at_utc": "2026-10-01T09:00:00Z",
                     "snapshot_label": "build", "ticket_status": final})
    return rows


def test_latest_status_replaces_superseded_pending_rows():
    rows = _snapshots()
    assert ps.clv_ticket_status_counts(rows) == {
        "pending_auto_tickets": 4, "deferred_before_build_hour": 2,
        "ticket_created": 2}
    assert ps.clv_latest_status_counts(rows) == {
        "deferred_before_build_hour": 2, "ticket_created": 2}


def test_latest_status_does_not_inflate_the_selection_count():
    rows = _snapshots()
    assert len(rows) == 8
    assert len(ps.clv_latest_rows(rows)) == 4
    assert sum(ps.clv_latest_status_counts(rows).values()) == 4


def test_the_summary_separates_snapshots_from_selections():
    text = "\n".join(ps.render_final_summary({
        "run_date": RUN_DATE,
        "plan": {"same_day_pick_count": 2, "horizon_pick_count": 2},
        "clv_rows": _snapshots(),
    }))

    assert "CLV snapshots captured:        8 row(s)" in text
    assert "CLV latest production selections: 4" in text
    assert ("CLV latest ticket_status:      "
            "deferred_before_build_hour=2, ticket_created=2") in text
    # The stale pending state must never be presented as a final status.
    latest = next(ln for ln in text.splitlines()
                  if "CLV latest ticket_status" in ln)
    assert "pending_auto_tickets" not in latest


def test_a_selection_without_a_pick_id_is_still_collapsed_by_fixture():
    rows = [
        {"match_date": "2026-10-02", "home": "Belgium", "away": "Turkey",
         "pick": "HOME", "captured_at_utc": "2026-10-01T06:00:00Z",
         "ticket_status": "pending_auto_tickets"},
        {"match_date": "2026-10-02", "home": "Belgium", "away": "Turkey",
         "pick": "HOME", "captured_at_utc": "2026-10-01T09:00:00Z",
         "ticket_status": "ticket_created"},
    ]
    assert ps.clv_latest_status_counts(rows) == {"ticket_created": 1}


# ===========================================================================
# Notification coverage
#
# The notifier announces future-dated selections only. Reporting just
# the notice count left the same-day selections unexplained.
# ===========================================================================


def _coverage_status():
    return {
        "run_date": RUN_DATE,
        "plan": {
            "same_day_pick_count": 2, "horizon_pick_count": 2,
            "horizon_picks": [
                {"pick_id": "p2", "home": "Belgium", "away": "Turkey"},
                {"pick_id": "p3", "home": "Hungary", "away": "Georgia"}],
        },
        "clv_rows": _snapshots(),
        "notification": {"ran": True, "outcome": ps.NOTIFY_SENT_THIS_RUN,
                         "future_notices": 2},
    }


def test_every_production_selection_is_accounted_for():
    text = "\n".join(ps.render_final_summary(_coverage_status()))

    assert "notification coverage:         4 production selection(s)" in text
    assert "sent_this_run future ticket notice: 2" in text
    assert ("deferred_before_build_hour: 2 not sent "
            "/ pending build window") in text


def test_coverage_totals_reconcile_with_the_selection_count():
    cov = ps.notification_coverage(
        _coverage_status()["plan"],
        _coverage_status()["notification"],
        ps.clv_latest_rows(_snapshots()))

    assert cov["total_selections"] == 4
    assert cov["notified"] + cov["not_notified"] == cov["total_selections"]


def test_no_coverage_line_when_there_were_no_selections():
    assert ps.render_notification_coverage(
        ps.notification_coverage({}, {}, [])) == []


def test_unmatched_snapshots_do_not_attribute_the_wrong_reason():
    """The notified picks must never be listed as not sent.

    When the snapshot rows cannot be matched to the future-dated picks,
    every status lands in the unannounced bucket, which reported the
    selections that WERE announced as pending.
    """
    plan = {"same_day_pick_count": 2, "horizon_pick_count": 2,
            "horizon_picks": [{"home": "Belgium", "away": "Turkey"},
                              {"home": "Hungary", "away": "Georgia"}]}
    cov = ps.notification_coverage(
        plan, {"outcome": ps.NOTIFY_SENT_THIS_RUN, "future_notices": 2},
        ps.clv_latest_rows(_snapshots()))

    assert cov["not_notified"] == 2
    assert cov["same_day_reasons"] == {}
    text = "\n".join(ps.render_notification_coverage(cov))
    assert "ticket_created" not in text
    assert "same-day selections: 2 not sent" in text


def test_the_snapshot_label_breaks_a_timestamp_tie():
    """Two snapshots of one selection can share a captured_at_utc.

    Guinea vs Kenya in run 36783344791 captured pick_time and
    end_of_run at the same second, and file order let the earlier
    pick_time row win, leaving the selection reading pending after the
    run had already deferred it.
    """
    rows = [
        {"pick_id": "g", "snapshot_label": "end_of_run",
         "captured_at_utc": "2026-10-01T16:00:00Z",
         "ticket_status": "deferred_before_build_hour"},
        {"pick_id": "g", "snapshot_label": "pick_time",
         "captured_at_utc": "2026-10-01T16:00:00Z",
         "ticket_status": "pending_auto_tickets"},
    ]

    assert ps.clv_latest_status_counts(rows) == {
        "deferred_before_build_hour": 1}


def test_a_later_timestamp_still_wins_over_an_earlier_label():
    rows = [
        {"pick_id": "g", "snapshot_label": "end_of_run",
         "captured_at_utc": "2026-10-01T10:00:00Z", "ticket_status": "stale"},
        {"pick_id": "g", "snapshot_label": "pick_time",
         "captured_at_utc": "2026-10-01T18:00:00Z", "ticket_status": "fresh"},
    ]

    assert ps.clv_latest_status_counts(rows) == {"fresh": 1}


# ===========================================================================
# Future horizon selections: reported, not ticketed
#
# The daily run must keep future selections visible in the summary,
# Supabase and notification coverage while refusing to card them. No
# run-date outcome file is fabricated for them.
# ===========================================================================


def test_a_future_selection_is_reported_but_not_ticketed(tmp_path):
    localdata = _localdata(tmp_path)          # horizon-dated by default
    _run_auto_tickets(localdata)              # bare daily run, targets RUN_DATE

    assert not (localdata / f"auto_tickets_{EVENT_DATE}.txt").exists(), \
        "the default daily run carded a future date"
    assert not (localdata / f"auto_tickets_{EVENT_DATE}.frozen").exists()

    text = "\n".join(ps.production_final_summary(RUN_DATE, localdata))
    # Still reported.
    assert "production selections:         1" in text
    assert EVENT_DATE in text


def test_no_outcome_file_is_invented_for_the_uncarded_future_date(tmp_path):
    """The bug class is date attribution, so nothing may be mirrored."""
    localdata = _localdata(tmp_path)
    _run_auto_tickets(localdata)

    assert at.load_ticket_outcomes(EVENT_DATE, localdata) == {}
    outcomes = at.load_ticket_outcomes(RUN_DATE, localdata)
    assert EVENT_DATE not in outcomes, \
        "a future date must not appear under the run date's outcomes"


def test_future_selections_stay_in_notification_coverage(tmp_path):
    localdata = _localdata(tmp_path)
    plan = json.loads(pl.dispatch_plan_path(RUN_DATE, localdata).read_text())

    coverage = ps.notification_coverage(
        plan, {"outcome": ps.NOTIFY_SENT_THIS_RUN, "future_notices": 1})

    assert coverage["total_selections"] == 1
    assert coverage["future_selections"] == 1


# ===========================================================================
# CLV is scoped to the run's own selections
#
# Snapshots accumulate for a whole month. The 2026-10-01 run reported
# "CLV latest production selections: 4" over 2 selections, carrying two
# earlier selections' ticket_created statuses forward as if current.
# ===========================================================================


def _snap(event_date, home, away, status, label="end_of_run"):
    return {"event_date": event_date, "home": home, "away": away,
            "selection": "home", "ticket_status": status,
            "snapshot_label": label, "captured_at_utc": f"{event_date}T10:00:00Z",
            "pick_id": f"{event_date}|{home}|{away}|1x2|home|rule".lower()}


def _two_pick_plan():
    return {"same_day_pick_count": 0, "horizon_pick_count": 2,
            "same_day_picks": [],
            "horizon_picks": [
                {"event_date": "2026-10-02", "home": "Belgium",
                 "away": "Turkey", "selection": "home"},
                {"event_date": "2026-10-02", "home": "Hungary",
                 "away": "Georgia", "selection": "home"}]}


def test_stale_snapshots_do_not_inflate_the_selection_count():
    rows = [_snap("2026-10-01", "Guinea", "Kenya", "ticket_created"),
            _snap("2026-10-01", "Panama", "New Zealand", "ticket_created"),
            _snap("2026-10-02", "Belgium", "Turkey", "declined_same_day_only_policy"),
            _snap("2026-10-02", "Hungary", "Georgia", "declined_same_day_only_policy")]

    scoped = ps.clv_rows_in_plan(rows, _two_pick_plan())

    assert len(ps.clv_latest_rows(scoped)) == 2
    assert ps.clv_latest_status_counts(scoped) == {
        "declined_same_day_only_policy": 2}


def test_an_earlier_runs_ticket_created_is_not_carried_forward():
    rows = [_snap("2026-10-01", "Guinea", "Kenya", "ticket_created")]

    assert ps.clv_rows_in_plan(rows, _two_pick_plan()) == []


def test_snapshots_match_the_plan_despite_the_pick_id_difference():
    """Snapshot rows carry pick_id; plan rows do not."""
    rows = [_snap("2026-10-02", "Belgium", "Turkey", "declined_same_day_only_policy")]

    assert len(ps.clv_rows_in_plan(rows, _two_pick_plan())) == 1


def test_partial_plan_knowledge_still_scopes_by_event_date():
    """Partial knowledge must not drop by fixture, but dates are known.

    A plan reporting counts without rows cannot identify every
    selection, so fixture-level filtering would under-report. Earlier
    runs' snapshots on other dates are still excluded -- that is how
    stale declined_no_selections rows contradicted current
    ticket_created outcomes.
    """
    plan = {"same_day_pick_count": 2, "horizon_pick_count": 2,
            "event_dates": ["2026-10-02"],
            "horizon_picks": _two_pick_plan()["horizon_picks"]}
    stale = _snap("2026-09-28", "Guinea", "Kenya", "declined_no_selections")
    current = _snap("2026-10-02", "Belgium", "Turkey", "ticket_created")

    scoped = ps.clv_rows_in_plan([stale, current], plan)

    assert scoped == [current]


def test_partial_knowledge_keeps_unidentified_rows_on_a_run_date():
    """Same-date rows survive: they may belong to the uncounted picks."""
    plan = {"same_day_pick_count": 2, "horizon_pick_count": 0,
            "event_dates": ["2026-10-01"]}
    rows = [_snap("2026-10-01", "Guinea", "Kenya", "ticket_created")]

    assert ps.clv_rows_in_plan(rows, plan) == rows


# ===========================================================================
# Run 736d2d9 shape: 2 same-day ticketed + 1 future declined
#
# The official run printed "Supabase selections published: 3
# (2026-10-01=3)" while the sync had published 2 for 2026-10-01 and 1 for
# 2026-10-02, and "CLV latest production selections: 5" against a plan of 3.
# ===========================================================================


def test_publish_breakdown_is_not_collapsed_onto_the_run_date(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / "supabase_sync_manifest_2026-10-01.json").write_text(
        json.dumps({"target_date": "2026-10-01", "row_count": 3,
                    "row_counts_by_event_date": {"2026-10-01": 2,
                                                 "2026-10-02": 1}}))

    published = ps.read_supabase_published(
        ["2026-10-01", "2026-10-02"], localdata, run_date="2026-10-01")

    assert published == {"2026-10-01": 2, "2026-10-02": 1}
    assert sum(published.values()) == 3


def test_a_per_date_manifest_does_not_hide_the_breakdown(tmp_path):
    """The run-date manifest short-circuited before the breakdown."""
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / "supabase_sync_manifest_2026-10-01.json").write_text(
        json.dumps({"target_date": "2026-10-01", "row_count": 3,
                    "row_counts_by_event_date": {"2026-10-01": 2,
                                                 "2026-10-02": 1}}))

    assert ps.read_supabase_published(
        ["2026-10-01"], localdata, run_date="2026-10-01") == {
            "2026-10-01": 2, "2026-10-02": 1}


def test_clv_latest_matches_the_three_selection_plan():
    plan = {"same_day_pick_count": 2, "horizon_pick_count": 1,
            "event_dates": ["2026-10-01", "2026-10-02"],
            "same_day_picks": [
                {"event_date": "2026-10-01", "home": "Guinea",
                 "away": "Kenya", "selection": "home"},
                {"event_date": "2026-10-01", "home": "Maccabi Bnei Raina",
                 "away": "Hapoel Kfar Shalem", "selection": "home"}],
            "horizon_picks": [
                {"event_date": "2026-10-02", "home": "Belgium",
                 "away": "Turkey", "selection": "home"}]}
    rows = [
        # stale rows from earlier runs that contradicted the outcome
        _snap("2026-09-28", "Old", "Fixture", "declined_no_selections"),
        _snap("2026-09-29", "Older", "Fixture", "deferred_before_build_hour"),
        _snap("2026-10-01", "Guinea", "Kenya", "ticket_created"),
        _snap("2026-10-01", "Maccabi Bnei Raina", "Hapoel Kfar Shalem",
              "ticket_created"),
        _snap("2026-10-02", "Belgium", "Turkey",
              "declined_same_day_only_policy"),
    ]

    scoped = ps.clv_rows_in_plan(rows, plan)

    assert len(ps.clv_latest_rows(scoped)) == 3
    assert ps.clv_latest_status_counts(scoped) == {
        "ticket_created": 2, "declined_same_day_only_policy": 1}


# ===========================================================================
# Run 36858371487: 3 same-day ticketed + 2 future declined
#
# Summary said "CLV latest production selections: 6" against a 5-selection
# plan, and "same-day selections: 5 not sent" when 3 were same-day and 2
# were future-dated.
# ===========================================================================


def test_a_fixture_whose_rule_changed_is_one_selection_not_two():
    """pick_id embeds rule_id, so a re-rated fixture looked like two."""
    rows = [
        {"event_date": "2026-10-01", "home": "Wales", "away": "Norway",
         "selection": "away", "ticket_status": "pending_auto_tickets",
         "snapshot_label": "pick_time",
         "captured_at_utc": "2026-10-01T06:00:00Z",
         "pick_id": "2026-10-01|wales|norway|1x2|away|p55-unanimous"},
        {"event_date": "2026-10-01", "home": "Wales", "away": "Norway",
         "selection": "away", "ticket_status": "ticket_created",
         "snapshot_label": "end_of_run",
         "captured_at_utc": "2026-10-01T12:00:00Z",
         "pick_id": "2026-10-01|wales|norway|1x2|away|p60-majority"},
    ]

    by_pick_id = ps.clv_latest_rows(rows)
    by_fixture = ps.clv_latest_rows(rows, key=ps._clv_fixture_key)

    assert len(by_pick_id) == 2        # the inflation
    assert len(by_fixture) == 1
    assert by_fixture[0]["ticket_status"] == "ticket_created"


def test_future_selections_are_not_reported_as_same_day():
    coverage = {"total_selections": 5, "same_day_selections": 3,
                "future_selections": 2, "notified": 0,
                "notify_outcome": "sent_this_run", "not_notified": 5,
                "same_day_reasons": {}}

    lines = ps.render_notification_coverage(coverage)
    text = "\n".join(lines)

    assert "same-day selections: 3 not sent" in text
    assert "future-dated selections: 2 not sent" in text
    assert "same-day selections: 5" not in text


def test_a_single_cohort_still_reads_naturally():
    coverage = {"total_selections": 2, "same_day_selections": 2,
                "future_selections": 0, "notified": 0,
                "notify_outcome": "none", "not_notified": 2,
                "same_day_reasons": {}}

    text = "\n".join(ps.render_notification_coverage(coverage))

    assert "same-day selections: 2 not sent" in text
    assert "future-dated" not in text
