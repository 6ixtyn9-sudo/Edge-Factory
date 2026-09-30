"""Cross-artifact invariants for an official run.

Every contradiction found so far had the same shape: two artifacts that
each looked correct on their own and disagreed with each other. A summary
claimed a publish the manifest did not support; a rule name claimed
evidence the plan did not carry; a status said unknown after the verdict
was known.

This module reads the artifacts a run produced and reports where they
contradict one another. It is read-only: it fixes nothing, writes
nothing, and decides nothing about betting. Its output is a list of
violations, and an empty list is the only passing result.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from . import selection_evidence

# Severities ----------------------------------------------------------------
ERROR = "error"
WARNING = "warning"

# Violation codes -----------------------------------------------------------
V_NO_LINEAGE = "selection_without_evidence_lineage"
V_RULE_VOTERS = "rule_claims_more_voters_than_evidence_shows"
V_SUPABASE = "summary_supabase_count_disagrees_with_manifest"
V_CLV_STATUS = "clv_ticket_status_disagrees_with_auto_ticket_outcome"
V_CLV_PENDING = "clv_left_pending_after_auto_tickets_decided"
V_NOTIFY = "summary_notification_status_disagrees_with_notifier"
V_CENSUS_BLOCKED = "census_blocks_a_selection_the_plan_dispatched"
V_CENSUS_PRETICKET = "census_claims_current_run_ticket_status_too_early"
V_STALE_RULE_ID = "retired_rule_id_prefix_in_use"
V_PICK_STAKE = "pick_engine_emitted_a_stake_size"
# Added after a run passed every invariant above while mis-stating its
# own final accounting. Each of these encodes a defect that shipped.
V_SUPABASE_DATES = "summary_publish_dates_disagree_with_manifest_breakdown"
V_CLV_STALE_STATUS = "summary_presents_superseded_clv_status_as_final"
V_CLV_INFLATED = "clv_status_counts_exceed_the_production_selection_count"
V_NOTIFY_COVERAGE = "summary_does_not_account_for_every_selection"
V_VOTER_MISLABELLED = "production_eligible_voter_labelled_non_dispatchable"
V_PRICE_ORIGIN = "embedded_price_does_not_name_its_origin_source"
V_SELECTION_DETAIL = "summary_selection_lines_disagree_with_selection_count"

# A pick may delegate staking; it may never size it.
_STAKE_MARKERS = ("stake_units", "stake_u", "units")
_RETIRED_RULE_PREFIXES = ("fresh_",)
_RETIRED_RULE_PATTERNS = ("_v1_", "_v2_", "_v3_")


def _violation(code: str, detail: str, *, severity: str = ERROR,
               where: str = "") -> dict[str, Any]:
    return {"code": code, "severity": severity, "detail": detail,
            "where": where}


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text()) if path.exists() else None
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# individual invariants
# ---------------------------------------------------------------------------


def check_selection_evidence(plan: dict | None) -> list[dict]:
    """Every dispatched selection must be able to justify its own rule."""
    out: list[dict] = []
    if not plan:
        return out
    picks = list(plan.get("same_day_picks") or []) + \
        list(plan.get("horizon_picks") or [])
    for pick in picks:
        where = (f"{pick.get('event_date')} {pick.get('home')} vs "
                 f"{pick.get('away')}")
        lineage = pick.get("evidence_lineage")
        if not lineage:
            out.append(_violation(
                V_NO_LINEAGE,
                "a dispatched selection carries no evidence lineage, so its "
                "rule claim cannot be checked", where=where))
            continue
        required = lineage.get("required_eligible_voters")
        actual = lineage.get("eligible_voter_count") or 0
        if required is not None and actual < required:
            out.append(_violation(
                V_RULE_VOTERS,
                f"rule {lineage.get('rule_id')} claims {required} eligible "
                f"voter(s) but the lineage shows {actual}", where=where))
    return out


def check_rule_ids(plan: dict | None) -> list[dict]:
    """Retired rule-id forms must not reappear in dispatched picks."""
    out: list[dict] = []
    if not plan:
        return out
    picks = list(plan.get("same_day_picks") or []) + \
        list(plan.get("horizon_picks") or [])
    for pick in picks:
        rule_id = str(pick.get("rule_id") or "")
        if not rule_id:
            continue
        bad = [p for p in _RETIRED_RULE_PREFIXES if rule_id.startswith(p)]
        bad += [p for p in _RETIRED_RULE_PATTERNS if p in rule_id]
        if bad:
            out.append(_violation(
                V_STALE_RULE_ID,
                f"rule_id '{rule_id}' uses a retired form ({', '.join(bad)})",
                where=f"{pick.get('event_date')} {pick.get('home')}"))
    return out


def check_no_stake_from_pick_engine(plan: dict | None) -> list[dict]:
    """The pick engine delegates staking; it never sizes it."""
    out: list[dict] = []
    if not plan:
        return out
    picks = list(plan.get("same_day_picks") or []) + \
        list(plan.get("horizon_picks") or [])
    for pick in picks:
        for marker in _STAKE_MARKERS:
            if marker in pick and pick.get(marker) not in (None, ""):
                out.append(_violation(
                    V_PICK_STAKE,
                    f"a production selection carries '{marker}'; staking "
                    f"belongs to auto_tickets",
                    where=f"{pick.get('event_date')} {pick.get('home')}"))
    return out


def check_supabase(summary_published: dict[str, int] | None,
                   manifest: dict | None) -> list[dict]:
    """The summary's publish count must match the manifest that proves it.

    ``None`` means the summary's figure was not supplied, which is not
    the same as the summary reporting zero; nothing is asserted then.
    """
    out: list[dict] = []
    if summary_published is None:
        return out
    reported = sum(summary_published.values())
    if manifest is None:
        if reported:
            out.append(_violation(
                V_SUPABASE,
                f"the summary reports {reported} published row(s) but no "
                f"sync manifest exists to support it"))
        return out
    try:
        actual = int(manifest.get("row_count") or 0)
    except (TypeError, ValueError):
        return out
    if reported != actual:
        out.append(_violation(
            V_SUPABASE,
            f"the summary reports {reported} published row(s) but the sync "
            f"manifest records {actual}"))
    return out


def check_supabase_dates(summary_published: dict[str, int] | None,
                         manifest: dict | None) -> list[dict]:
    """The per-date breakdown must match the one the sync recorded.

    A manifest named for the run date covers future-dated selections
    too. Attributing its total to the run date made a run that published
    2 for each of two dates report "4 (run_date=4)".
    """
    out: list[dict] = []
    if summary_published is None or not manifest:
        return out
    breakdown = manifest.get("row_counts_by_event_date")
    if not isinstance(breakdown, dict) or not breakdown:
        return out
    recorded = {}
    for day, count in breakdown.items():
        try:
            recorded[str(day)[:10]] = int(count)
        except (TypeError, ValueError):
            return out
    reported = {str(k)[:10]: int(v) for k, v in summary_published.items()}
    if reported != recorded:
        out.append(_violation(
            V_SUPABASE_DATES,
            f"the summary attributes publishes as {reported} but the sync "
            f"manifest records {recorded}"))
    return out


def check_clv_latest_status(clv_rows: Iterable[dict] | None,
                            reported_counts: dict[str, int] | None,
                            selection_count: int | None = None) -> list[dict]:
    """Final status must be the latest per selection, not every snapshot.

    A selection is snapshotted several times per run and its status
    advances between captures, so counting rows reported superseded
    states beside the ones that replaced them, over an inflated pick
    count.
    """
    out: list[dict] = []
    if reported_counts is None:
        return out
    rows = list(clv_rows or [])
    if not rows:
        return out
    from . import production_summary
    latest = production_summary.clv_ticket_status_counts(
        production_summary.clv_latest_rows(rows))
    if dict(reported_counts) != dict(latest):
        out.append(_violation(
            V_CLV_STALE_STATUS,
            f"the summary reports final CLV statuses {dict(reported_counts)} "
            f"but the latest snapshot per selection gives {latest}"))
    total = sum(int(v) for v in reported_counts.values())
    if selection_count is not None and total > int(selection_count):
        out.append(_violation(
            V_CLV_INFLATED,
            f"CLV status counts total {total} over {selection_count} "
            f"production selection(s)"))
    return out


def check_notification_coverage(coverage: dict | None) -> list[dict]:
    """Every production selection must be accounted for, sent or not."""
    out: list[dict] = []
    if not coverage:
        return out
    total = int(coverage.get("total_selections") or 0)
    if not total:
        return out
    accounted = (int(coverage.get("notified") or 0)
                 + int(coverage.get("not_notified") or 0))
    if accounted != total:
        out.append(_violation(
            V_NOTIFY_COVERAGE,
            f"{total} production selection(s) but the summary accounts for "
            f"{accounted}"))
    return out


def check_voter_terminology(census: dict | None) -> list[dict]:
    """No source production votes with may be called non-dispatchable.

    The census called shadow-tier 1X2 predictors
    source_tier_not_dispatchable while the production lane counted them
    toward quorum. Non-dispatchable wording is reserved for parked,
    donor-only, odds-only and audit-only sources.
    """
    out: list[dict] = []
    if not census:
        return out
    from . import source_census
    for day, payload in (census.get("per_date") or {}).items():
        for summary in (payload or {}).get("sources") or []:
            role = str(summary.get("production_role") or "")
            if role not in (source_census.ROLE_LIVE_VOTER,
                            source_census.ROLE_SHADOW_VOTER):
                continue
            blockers = list(summary.get("blockers") or [])
            if source_census.B_TIER_NOT_DISPATCHABLE in blockers:
                out.append(_violation(
                    V_VOTER_MISLABELLED,
                    f"{summary.get('source')} votes in production as "
                    f"'{role}' but the census labels it "
                    f"'{source_census.B_TIER_NOT_DISPATCHABLE}'",
                    where=str(day)))
    return out


def check_price_origin(plan: dict | None) -> list[dict]:
    """An embedded price must name the source that produced it.

    pricing_source is a mechanism; on its own it hides that a quote came
    from a shadow-tier predictor.
    """
    out: list[dict] = []
    if not plan:
        return out
    picks = list(plan.get("same_day_picks") or []) + \
        list(plan.get("horizon_picks") or [])
    for pick in picks:
        if pick.get("odds") in (None, "", 0):
            continue
        price = selection_evidence.classify_price(pick)
        if selection_evidence.P_EMBEDDED not in price.get("states", ()):
            continue
        if not price.get("price_origin_source"):
            out.append(_violation(
                V_PRICE_ORIGIN,
                f"this selection carries an embedded price but names no "
                f"origin source (mechanism "
                f"'{price.get('price_mechanism') or 'unknown'}')",
                where=f"{pick.get('home')} vs {pick.get('away')}"))
        elif not price.get("price_origin_tier"):
            out.append(_violation(
                V_PRICE_ORIGIN,
                f"price origin '{price['price_origin_source']}' carries no "
                f"tier",
                where=f"{pick.get('home')} vs {pick.get('away')}"))
    return out


def check_selection_detail_count(plan: dict | None,
                                 detail_count: int | None) -> list[dict]:
    """The per-selection lines must reconcile with the selection count."""
    out: list[dict] = []
    if not plan or detail_count is None:
        return out
    # Prefer the pick lists themselves; the count fields are a summary
    # of them and an absent count must not assert a zero.
    listed = (len(plan.get("same_day_picks") or [])
              + len(plan.get("horizon_picks") or []))
    total = (int(plan.get("same_day_pick_count") or 0)
             + int(plan.get("horizon_pick_count") or 0)) or listed
    if detail_count != total:
        out.append(_violation(
            V_SELECTION_DETAIL,
            f"the summary reports {total} production selection(s) but "
            f"prints {detail_count} selection detail line(s)"))
    return out


def check_clv_status(clv_rows: Iterable[dict] | None,
                     ticket_outcomes: dict | None,
                     *, pending_status: str = "pending_auto_tickets",
                     after_auto_tickets: bool = True) -> list[dict]:
    """A settled ticket verdict must reach the CLV rows it describes."""
    out: list[dict] = []
    outcomes = ticket_outcomes or {}
    if not outcomes or not after_auto_tickets:
        return out
    for row in clv_rows or []:
        event_date = str(row.get("event_date") or row.get("match_date") or "")
        decided = (outcomes.get(event_date) or {}).get("status")
        if not decided:
            continue
        status = str(row.get("ticket_status") or "").strip()
        where = f"{event_date} {row.get('pick_id')}"
        if not status or status == "unknown" or status == pending_status:
            out.append(_violation(
                V_CLV_PENDING,
                f"auto_tickets decided '{decided}' but this CLV row still "
                f"reads '{status or 'blank'}'", where=where))
        elif status != decided:
            out.append(_violation(
                V_CLV_STATUS,
                f"CLV records '{status}' but auto_tickets decided "
                f"'{decided}'", where=where))
    return out


def check_notification(summary_outcome: str | None,
                       notifier_result: dict | None) -> list[dict]:
    """The summary must report the outcome the notifier recorded."""
    out: list[dict] = []
    if not notifier_result:
        return out
    recorded = str(notifier_result.get("outcome") or "").strip()
    reported = str(summary_outcome or "").strip()
    if recorded and reported and recorded != reported:
        out.append(_violation(
            V_NOTIFY,
            f"the summary reports notification '{reported}' but the "
            f"notifier recorded '{recorded}'"))
    return out


def check_census_agrees_with_plan(census: dict | None,
                                  plan: dict | None) -> list[dict]:
    """The census must not call a dispatched selection blocked."""
    out: list[dict] = []
    if not census or not plan:
        return out
    picks = list(plan.get("same_day_picks") or []) + \
        list(plan.get("horizon_picks") or [])
    if not picks:
        return out

    per_date = census.get("per_date") or {}
    for pick in picks:
        day = str(pick.get("event_date") or pick.get("date") or "")
        payload = per_date.get(day)
        if not payload:
            continue
        home = str(pick.get("home") or "")
        away = str(pick.get("away") or "")
        for group in payload.get("fixture_groups") or []:
            if group.get("fixture") != f"{home} vs {away}":
                continue
            if group.get("quorum_met"):
                break
            out.append(_violation(
                V_CENSUS_BLOCKED,
                f"the plan dispatched this selection but the census reports "
                f"only {group.get('voter_count_1x2')} eligible voter(s) "
                f"({', '.join(group.get('blockers') or []) or 'no reason given'})",
                where=f"{day} {home} vs {away}"))
            break
    return out


def check_census_status_provenance(census: dict | None,
                                   *, ran_before_auto_tickets: bool = True
                                   ) -> list[dict]:
    """A census printed before auto_tickets cannot report its verdict."""
    out: list[dict] = []
    if not census:
        return out
    if ran_before_auto_tickets and census.get("ticket_status_is_current_run"):
        out.append(_violation(
            V_CENSUS_PRETICKET,
            "the census claims its ticket status is this run's, but it ran "
            "before auto_tickets decided"))
    return out


# ---------------------------------------------------------------------------
# aggregation
# ---------------------------------------------------------------------------


def check_run(*, plan: dict | None = None,
              census: dict | None = None,
              summary_published: dict[str, int] | None = None,
              sync_manifest: dict | None = None,
              clv_rows: Iterable[dict] | None = None,
              ticket_outcomes: dict | None = None,
              summary_notification_outcome: str | None = None,
              notifier_result: dict | None = None,
              census_ran_before_auto_tickets: bool = True,
              after_auto_tickets: bool = True,
              summary_clv_status_counts: dict[str, int] | None = None,
              notification_coverage: dict | None = None,
              summary_selection_detail_count: int | None = None) -> list[dict]:
    """Every invariant, against whatever artifacts were supplied."""
    violations: list[dict] = []
    violations += check_selection_evidence(plan)
    violations += check_rule_ids(plan)
    violations += check_no_stake_from_pick_engine(plan)
    violations += check_supabase(summary_published, sync_manifest)
    violations += check_clv_status(clv_rows, ticket_outcomes,
                                   after_auto_tickets=after_auto_tickets)
    violations += check_notification(summary_notification_outcome,
                                     notifier_result)
    violations += check_census_agrees_with_plan(census, plan)
    violations += check_census_status_provenance(
        census, ran_before_auto_tickets=census_ran_before_auto_tickets)
    violations += check_supabase_dates(summary_published, sync_manifest)
    violations += check_clv_latest_status(
        clv_rows, summary_clv_status_counts,
        (int((plan or {}).get("same_day_pick_count") or 0)
         + int((plan or {}).get("horizon_pick_count") or 0)) or None)
    violations += check_notification_coverage(notification_coverage)
    violations += check_voter_terminology(census)
    violations += check_price_origin(plan)
    violations += check_selection_detail_count(
        plan, summary_selection_detail_count)
    return violations


def check_run_from_localdata(run_date: str, localdata: Path,
                             **overrides) -> list[dict]:
    """Load a run's artifacts from disk and check them. Never writes."""
    localdata = Path(localdata)
    plan = _read_json(
        localdata / f"fresh_production_dispatch_plan_{run_date}.json")
    census = _read_json(
        localdata / f"source_fixture_census_{run_date}.json")
    manifest = _read_json(
        localdata / f"supabase_sync_manifest_{run_date}.json")
    outcomes = (_read_json(
        localdata / f"auto_ticket_outcomes_{run_date}.json") or {}
    ).get("outcomes")
    notifier = _read_json(
        localdata / f"notification_result_{run_date}.json")

    # Ask the summary what it would actually report, so the comparison is
    # against the real rendered figure rather than an assumption.
    from . import production_summary
    event_dates = list((plan or {}).get("event_dates") or [])
    summary_published = production_summary.read_supabase_published(
        event_dates, localdata, run_date=run_date)
    notification = production_summary.read_notification_result(
        run_date, localdata)
    summary_notification = notification.get("outcome")

    # The accounting the summary would actually print, so the checks
    # compare against the rendered figures rather than assumptions.
    clv_rows = production_summary.read_clv_rows(run_date, localdata)
    summary_clv_counts = production_summary.clv_latest_status_counts(clv_rows)
    coverage = production_summary.notification_coverage(
        plan or {}, notification,
        production_summary.clv_latest_rows(clv_rows))
    detail_count = sum(
        1 for line in production_summary.render_final_summary(
            production_summary.collect_production_status(run_date, localdata))
        if line.strip().startswith("SELECTION "))

    kwargs: dict[str, Any] = {
        "summary_published": summary_published,
        "summary_notification_outcome": summary_notification,
        "plan": plan, "census": census, "sync_manifest": manifest,
        "ticket_outcomes": outcomes, "notifier_result": notifier,
        "clv_rows": clv_rows,
        "summary_clv_status_counts": summary_clv_counts,
        "notification_coverage": coverage,
        "summary_selection_detail_count": detail_count,
    }
    kwargs.update(overrides)
    return check_run(**kwargs)


def render_invariant_lines(violations: list[dict]) -> list[str]:
    out = ["RUN INVARIANT CHECK"]
    if not violations:
        out.append("  no contradictions found across the run's artifacts")
        return out
    errors = sum(1 for v in violations if v["severity"] == ERROR)
    out.append(f"  {len(violations)} contradiction(s) found, {errors} error(s)")
    for violation in violations:
        where = f" [{violation['where']}]" if violation.get("where") else ""
        out.append(f"  {violation['severity'].upper()}: "
                   f"{violation['code']}{where}")
        out.append(f"    {violation['detail']}")
    out.append("  a contradiction means two artifacts disagree; resolve it "
               "before trusting either")
    return out


def has_errors(violations: list[dict]) -> bool:
    return any(v["severity"] == ERROR for v in violations)
