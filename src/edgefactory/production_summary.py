"""The authoritative, operator-facing production summary.

Everything here is read *after* the downstream stages have run. The pick
engine emits a preliminary planning block while it is still working, and
that block cannot know what auto_tickets, Supabase, CLV or the notifier
later did. Reporting a guess there produced a real audit defect: a future
production selection that auto_tickets had evaluated and declined was
printed as "auto-ticket action: not evaluated / assayer action: not run".

This module fixes that by deriving every downstream field from the artifact
the stage actually wrote:

    dispatch plan        fresh_production_dispatch_plan_<run_date>.json
    ticket verdict       auto_ticket_outcomes_<run_date>.json
    Supabase publish     supabase_sync_manifest_<event_date>.json
    CLV capture          clv_snapshots_<YYYY-MM>.csv.gz
    notification         sent_ledger_<run_date>.json

A stage that did not run is reported as "did not run", never as a verdict.
"""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import Any

from . import production_lane

STAKING_OWNER = "auto_tickets"
STAKING_POLICY = "handled_by_auto_tickets"

FUTURE_PICK_MARKER_PREFIX = "__future_pick__"

TICKET_CREATED = "ticket_created"


# ---------------------------------------------------------------------------
# readers — each returns evidence, or None when the stage left none
# ---------------------------------------------------------------------------


def read_ticket_outcomes(run_date: str, localdata: Path) -> dict | None:
    """Per-event-date auto-ticket verdicts, or None if auto_tickets never ran."""
    path = Path(localdata) / f"auto_ticket_outcomes_{run_date}.json"
    if not path.exists():
        return None
    try:
        return dict(json.loads(path.read_text()).get("outcomes") or {})
    except (OSError, ValueError):
        return None


def _read_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def read_supabase_published(event_dates, localdata: Path,
                            run_date: str | None = None) -> dict[str, int]:
    """Rows published, from the sync manifests that actually exist.

    sync_supabase writes a single manifest named for the run date, whose
    row_count covers every pick published by that run — including
    future-dated ones. Looking only for a manifest per event date finds
    nothing and makes a successful publish read as "no manifest found",
    so the run-date manifest is consulted as well.
    """
    published: dict[str, int] = {}
    for day in event_dates:
        manifest = _read_manifest(
            Path(localdata) / f"supabase_sync_manifest_{day}.json")
        if manifest is None:
            continue
        try:
            published[day] = int(manifest.get("row_count") or 0)
        except (TypeError, ValueError):
            continue

    if published or not run_date:
        return published

    manifest = _read_manifest(
        Path(localdata) / f"supabase_sync_manifest_{run_date}.json")
    if manifest is None:
        return published
    try:
        total = int(manifest.get("row_count") or 0)
    except (TypeError, ValueError):
        return published
    # Prefer the breakdown the sync recorded. Attributing the whole
    # total to the run date reports "4 (2026-10-01=4)" for a run that
    # published 2 for 2026-10-01 and 2 for 2026-10-02.
    breakdown = manifest.get("row_counts_by_event_date")
    if isinstance(breakdown, dict) and breakdown:
        for day, count in breakdown.items():
            try:
                published[str(day)[:10]] = int(count)
            except (TypeError, ValueError):
                continue
        if published:
            return published

    # No breakdown recorded (older manifest). A single total is not a
    # per-date split, so do not invent one.
    published[str(manifest.get("target_date") or run_date)] = total
    return published


def read_clv_rows(run_date: str, localdata: Path) -> list[dict[str, Any]]:
    """CLV snapshot rows captured for this run, keyed by dispatch plan id."""
    path = Path(localdata) / f"clv_snapshots_{str(run_date)[:7]}.csv.gz"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with gzip.open(path, "rt", newline="") as fh:
            for row in csv.DictReader(fh):
                if str(row.get("dispatch_plan_id") or "") == run_date or \
                        str(row.get("run_date") or "") == run_date:
                    rows.append(row)
    except (OSError, ValueError):
        return []
    return rows


def clv_ticket_status_counts(rows) -> dict[str, int]:
    """How many captured CLV *snapshot rows* ended in each ticket status.

    This counts rows, not selections. A selection is snapshotted more
    than once per run, so these counts must never be presented as a
    count of picks.
    """
    counts: dict[str, int] = {}
    for row in rows or ():
        status = str(row.get("ticket_status") or "").strip() or "unknown"
        counts[status] = counts.get(status, 0) + 1
    return counts


def _clv_selection_key(row) -> tuple:
    """Identify the logical selection a snapshot row belongs to."""
    pick_id = str(row.get("pick_id") or "").strip()
    if pick_id:
        return ("pick_id", pick_id)
    return (
        "fixture",
        str(row.get("match_date") or row.get("event_date") or "").strip(),
        str(row.get("home") or "").strip().casefold(),
        str(row.get("away") or "").strip().casefold(),
        str(row.get("pick") or row.get("selection") or "").strip().casefold(),
    )


def clv_latest_rows(rows) -> list[dict[str, Any]]:
    """The most recent snapshot per logical selection.

    A selection is captured at several points in a run, and its
    ticket_status changes as the ticket engine works. Counting every
    snapshot reports superseded states — a pick that became
    ticket_created still shows its earlier pending row — and inflates
    the apparent number of picks.
    """
    latest: dict[tuple, dict[str, Any]] = {}
    order: dict[tuple, int] = {}
    for index, row in enumerate(rows or ()):
        key = _clv_selection_key(row)
        stamp = str(row.get("captured_at_utc") or "")
        current = latest.get(key)
        if current is None:
            latest[key], order[key] = row, index
            continue
        if (stamp, index) >= (str(current.get("captured_at_utc") or ""),
                              order[key]):
            latest[key], order[key] = row, index
    return list(latest.values())


def clv_latest_status_counts(rows) -> dict[str, int]:
    """Ticket status per logical selection, using each one's latest row."""
    return clv_ticket_status_counts(clv_latest_rows(rows))


NOTIFY_SENT_THIS_RUN = "sent_this_run"
NOTIFY_DEDUPED = "deduped_already_sent"
NOTIFY_SKIPPED_NO_PICKS = "skipped_no_picks"
NOTIFY_FAILED = "failed"
NOTIFY_DID_NOT_RUN = "did_not_run"


def read_notification_result(run_date: str, localdata: Path) -> dict:
    """What the notifier actually did this run.

    notify writes an explicit outcome, because the sent ledger is
    cumulative: it can show a notice exists without showing whether this
    run sent it, which made a suppressed notice read as a fresh send.
    """
    explicit = _read_manifest(
        Path(localdata) / f"notification_result_{run_date}.json")
    if explicit is not None:
        outcome = str(explicit.get("outcome") or "").strip() or NOTIFY_DID_NOT_RUN
        return {
            "ran": outcome != NOTIFY_DID_NOT_RUN,
            "outcome": outcome,
            "future_notices": int(explicit.get("future_notices") or 0),
            "detail": str(explicit.get("detail") or ""),
        }

    path = Path(localdata) / f"sent_ledger_{run_date}.json"
    if not path.exists():
        return {"ran": False, "outcome": NOTIFY_DID_NOT_RUN,
                "future_notices": 0}
    try:
        keys = json.loads(path.read_text())
    except (OSError, ValueError):
        return {"ran": False, "outcome": NOTIFY_DID_NOT_RUN,
                "future_notices": 0}
    if isinstance(keys, dict):
        keys = list(keys.get("keys") or keys.keys())
    future = [k for k in keys if str(k).startswith(FUTURE_PICK_MARKER_PREFIX)]
    # Fallback only: a ledger entry proves a notice exists, not that this
    # run sent it, so the outcome is reported as indeterminate rather
    # than claimed as a send.
    return {"ran": True, "outcome": "ledgered_run_unknown",
            "future_notices": len(future), "keys": sorted(future)}


def notification_coverage(plan: dict, notification: dict,
                          latest_rows=None) -> dict:
    """Account for every production selection, notified or not.

    The notifier announces future-dated selections only, so a run with 4
    selections and 2 future ones reports 2 notices. Reporting the notice
    count alone leaves the other 2 selections unexplained, which reads
    as under-delivery rather than as the deliberate same-day path.
    """
    plan = plan or {}
    same_day = int(plan.get("same_day_pick_count") or 0)
    future = int(plan.get("horizon_pick_count") or 0)
    notices = int((notification or {}).get("future_notices") or 0)
    outcome = str((notification or {}).get("outcome") or "").strip()

    # Why the same-day selections were not announced, taken from their
    # own recorded status rather than assumed.
    reasons: dict[str, int] = {}
    future_keys = {
        _clv_selection_key(row)
        for row in (plan.get("horizon_picks") or ())
    }
    for row in latest_rows or ():
        if _clv_selection_key(row) in future_keys:
            continue
        status = str(row.get("ticket_status") or "").strip()
        if status:
            reasons[status] = reasons.get(status, 0) + 1

    return {
        "total_selections": same_day + future,
        "future_selections": future,
        "same_day_selections": same_day,
        "notified": notices,
        "notify_outcome": outcome,
        "not_notified": max((same_day + future) - notices, 0),
        "same_day_reasons": reasons,
    }


def render_notification_coverage(coverage: dict) -> list[str]:
    """One line per cohort, so every selection is accounted for."""
    total = int(coverage.get("total_selections") or 0)
    if not total:
        return []
    notified = int(coverage.get("notified") or 0)
    outcome = str(coverage.get("notify_outcome") or "") or "no outcome recorded"
    lines = [f"  notification coverage:         {total} production "
             f"selection(s)"]
    if notified:
        lines.append(f"    {outcome} future ticket notice: {notified}")
    not_notified = int(coverage.get("not_notified") or 0)
    if not_notified:
        reasons = coverage.get("same_day_reasons") or {}
        if reasons:
            for status, count in sorted(reasons.items()):
                lines.append(f"    {status}: {count} not sent "
                             f"/ pending build window")
        else:
            lines.append(f"    same-day selections: {not_notified} not sent "
                         f"/ pending build window")
    return lines


# ---------------------------------------------------------------------------
# collection + rendering
# ---------------------------------------------------------------------------


def collect_production_status(run_date: str, localdata: Path | str) -> dict:
    """Gather the real post-run state of every production stage."""
    localdata = Path(localdata)
    plan = production_lane.load_dispatch_plan(run_date, localdata) or {}
    event_dates = list(plan.get("event_dates") or [])
    clv_rows = read_clv_rows(run_date, localdata)
    return {
        "run_date": run_date,
        "plan": plan,
        "ticket_outcomes": read_ticket_outcomes(run_date, localdata),
        "supabase_published": read_supabase_published(
            event_dates, localdata, run_date=run_date),
        "clv_rows": clv_rows,
        "clv_ticket_status_counts": clv_ticket_status_counts(clv_rows),
        "clv_latest_rows": clv_latest_rows(clv_rows),
        "clv_latest_status_counts": clv_latest_status_counts(clv_rows),
        "notification": read_notification_result(run_date, localdata),
    }


def _ticket_lines(plan: dict, outcomes: dict | None) -> list[str]:
    """Report the ticket engine's verdict per event date, or that it did not run."""
    total = int(plan.get("same_day_pick_count") or 0) + \
        int(plan.get("horizon_pick_count") or 0)
    if outcomes is None:
        state = ("did not run" if total
                 else "did not run (no selections to evaluate)")
        return [f"  auto-ticket action:            {state}",
                f"  ticket status:                 no ticket",
                f"  assayer action:                did not run",
                f"  benching action:               unknown (assayer did not run)",
                f"  staking assigned:              no"]

    scored = {d: o for d, o in outcomes.items() if (o or {}).get("selections")}
    if not scored:
        return ["  auto-ticket action:            "
                "nothing to evaluate (no selections reached the ticket engine)",
                "  ticket status:                 no ticket",
                "  assayer action:                not run (nothing to assay)",
                "  benching action:               none",
                "  staking assigned:              no"]

    actions, statuses = [], []
    for day in sorted(scored):
        status = str(scored[day].get("status") or "unknown")
        actions.append(f"{day}: {status}")
        statuses.append(status)
    created = [s for s in statuses if s == TICKET_CREATED]

    benched = sorted({b for o in scored.values()
                      for b in list(o.get("benched_buckets") or ())
                      + list(o.get("slice_benched_buckets") or ())})
    assayed = any(o.get("assayer_ran") for o in scored.values())

    if created:
        ticket_status = f"{len(created)} ticket(s) created"
        staking_assigned = "percentage of capital / free bank"
    else:
        # Name the decline rather than the absence of a bet.
        ticket_status = "; ".join(sorted(set(statuses))) + " / no ticket created"
        staking_assigned = "no"

    return [
        f"  auto-ticket action:            {'; '.join(actions)}",
        f"  ticket status:                 {ticket_status}",
        f"  assayer action:                "
        + ("ran; no bucket diminished" if assayed and not benched
           else f"ran; benched {', '.join(benched)}" if benched
           else "not run (no selection survived the pre-assay gates)"),
        f"  benching action:               "
        + (f"{', '.join(benched)} excluded from selection" if benched
           else "none"),
        f"  staking assigned:              {staking_assigned}",
    ]


def render_final_summary(status: dict) -> list[str]:
    """The authoritative operator-facing verdict for a production run."""
    plan = status.get("plan") or {}
    same_day = int(plan.get("same_day_pick_count") or 0)
    future = int(plan.get("horizon_pick_count") or 0)
    total = same_day + future
    event_dates = list(plan.get("event_dates") or [])

    published = status.get("supabase_published") or {}
    published_total = sum(published.values())
    clv_rows = status.get("clv_rows") or []
    clv_counts = status.get("clv_ticket_status_counts") or {}
    clv_latest = status.get("clv_latest_rows")
    if clv_latest is None:
        clv_latest = clv_latest_rows(clv_rows)
    clv_latest_counts = (status.get("clv_latest_status_counts")
                         or clv_latest_status_counts(clv_rows))
    notification = status.get("notification") or {}

    # The outcome is reported as the notifier recorded it. A notice this
    # run suppressed as already-sent must never read as one it sent.
    outcome = str(notification.get("outcome") or "").strip()
    notices = int(notification.get("future_notices") or 0)
    if not notification.get("ran") or outcome == NOTIFY_DID_NOT_RUN:
        notify_line = "did not run"
    elif outcome == NOTIFY_SENT_THIS_RUN:
        notify_line = (f"sent_this_run — PRODUCTION SELECTION notice "
                       f"dispatched and ledgered ({notices} pick(s))"
                       if notices else
                       "sent_this_run — notice dispatched and ledgered")
    elif outcome == NOTIFY_DEDUPED:
        notify_line = ("deduped_already_sent — nothing dispatched by this "
                       "run; the notice was already in the sent ledger")
    elif outcome == NOTIFY_SKIPPED_NO_PICKS:
        notify_line = "skipped_no_picks — there was nothing to announce"
    elif outcome == NOTIFY_FAILED:
        notify_line = ("failed — one or more channels did not deliver; "
                       "do not assume the message arrived")
    elif notices:
        notify_line = (f"ledgered_run_unknown — {notices} future notice(s) "
                       f"in the ledger; this run's own action was not "
                       f"recorded")
    else:
        notify_line = "no future-selection notice (empty-slate heartbeat path)"

    lines = [
        "FINAL PRODUCTION SUMMARY",
        f"  run date:                      {status.get('run_date')}",
        f"  production selections:         {total}",
        f"  same-day selections:           {same_day}",
        f"  future-dated selections:       {future}",
        f"  event dates:                   {', '.join(event_dates) or 'none'}",
        f"  Supabase selections published: {published_total}"
        + (f" ({', '.join(f'{d}={n}' for d, n in sorted(published.items()))})"
           if published else " (no sync manifest found)"),
        f"  CLV snapshots captured:        {len(clv_rows)} row(s)",
        f"  CLV latest production selections: {len(clv_latest)}",
    ]
    # Snapshot counts and selection counts are different quantities and
    # are labelled as such. Only the latest status per selection is a
    # statement about where a pick actually ended up.
    if clv_latest_counts:
        lines.append("  CLV latest ticket_status:      "
                     + ", ".join(f"{k}={v}"
                                 for k, v in sorted(clv_latest_counts.items())))
    if clv_counts:
        lines.append("  CLV snapshot ticket_status:    "
                     + ", ".join(f"{k}={v}" for k, v in sorted(clv_counts.items()))
                     + " (across all snapshots, not a pick count)")
    lines.append(f"  notification:                  {notify_line}")
    lines += render_notification_coverage(
        notification_coverage(plan, notification, clv_latest))
    lines += _ticket_lines(plan, status.get("ticket_outcomes"))
    lines += [
        f"  staking owner:                 {STAKING_OWNER}",
        f"  staking policy:                {STAKING_POLICY}",
    ]
    for row in plan.get("horizon_picks") or ():
        outcome = ((status.get("ticket_outcomes") or {})
                   .get(str(row.get("event_date"))) or {})
        verdict = str(outcome.get("status") or "not evaluated")
        lines.append(
            f"    SELECTION {row.get('event_date')} "
            f"{row.get('kickoff') or '-'} {row.get('home')} vs {row.get('away')} "
            f"| {row.get('pick')} | odds={row.get('odds')} "
            f"| {row.get('edge_rule')} | auto-ticket: {verdict}")
    return lines


def production_final_summary(run_date: str, localdata: Path | str) -> list[str]:
    """Convenience: collect the run's real state and render the verdict."""
    return render_final_summary(collect_production_status(run_date, localdata))
