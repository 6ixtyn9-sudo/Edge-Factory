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
              after_auto_tickets: bool = True) -> list[dict]:
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
    summary_notification = production_summary.read_notification_result(
        run_date, localdata).get("outcome")

    kwargs: dict[str, Any] = {
        "summary_published": summary_published,
        "summary_notification_outcome": summary_notification,
        "plan": plan, "census": census, "sync_manifest": manifest,
        "ticket_outcomes": outcomes, "notifier_result": notifier,
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
