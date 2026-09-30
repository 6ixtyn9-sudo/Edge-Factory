"""Evidence lineage for production selections, and the invariants it must satisfy.

A production selection carries a rule_id that makes a claim about its own
evidence. ``1x2_two_source_p55_unanimous`` claims two sources agreed. If
the selection cannot show two *production-eligible* voters, the rule name
is not describing reality and the selection must not dispatch.

This module answers one question per selection: can the claim in the
rule_id be reconstructed from the sources that actually voted? It derives
eligibility from the capability registry and never from a hardcoded list.

It does not size stakes, form tickets, price anything or decide edges. It
only reconciles a claim against its evidence, and blocks when it cannot.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from . import source_registry

# Statuses ------------------------------------------------------------------
RECONCILED = "reconciled"
BLOCKED_INSUFFICIENT_VOTERS = "blocked_insufficient_eligible_voters"
BLOCKED_RULE_EVIDENCE_MISMATCH = "blocked_rule_evidence_mismatch"
BLOCKED_NO_EVIDENCE = "blocked_no_evidence_lineage"

BLOCKING_STATUSES = (
    BLOCKED_INSUFFICIENT_VOTERS,
    BLOCKED_RULE_EVIDENCE_MISMATCH,
    BLOCKED_NO_EVIDENCE,
)

# Voter-count words as they appear in canonical rule ids.
_VOTER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
}


def required_voter_count(rule_id: str | None) -> int | None:
    """How many voters the rule_id claims, or None if it makes no claim."""
    if not rule_id:
        return None
    for word, count in _VOTER_WORDS.items():
        if re.search(rf"(^|_){word}_source(_|$)", rule_id):
            return count
    # Legacy numeric form, e.g. fresh_1x2_v2_p55.
    match = re.search(r"(^|_)v(\d+)_p\d+", rule_id)
    if match:
        return int(match.group(2))
    return None


def eligible_1x2_voters(sources: Iterable[str]) -> list[str]:
    """Sources that may carry a production 1X2 vote.

    Eligibility is tier-derived, and by operator decision it covers both
    live and shadow 1X2 predictors: a shadow source is a source whose
    settlement record is still accruing, not one whose opinion is
    discarded. This matches ``fresh_production_voters()``, which is the
    lane that actually forms the vote, so the census and the dispatch
    plan count the same voters.

    Parked predictors are excluded: parked is an availability decision.
    Donor and pricing tiers are excluded because they carry no 1X2
    opinion at all.
    """
    out = []
    for name in sources:
        cap = source_registry.get(name)
        if cap is None:
            continue
        if "1x2" not in cap.markets:
            continue
        if cap.name in source_registry.PARKED_PREDICTORS:
            continue
        if cap.tier not in (source_registry.TIER_LIVE,
                            source_registry.TIER_SHADOW):
            continue
        out.append(name)
    return sorted(set(out))


def classify_voters(sources: Iterable[str]) -> dict[str, list[str]]:
    """Split the voters a selection used into their registry roles."""
    seen = sorted(set(str(s) for s in sources if s))
    eligible, shadow, unregistered, other = [], [], [], []
    live, parked = [], []
    for name in seen:
        cap = source_registry.get(name)
        if cap is None:
            unregistered.append(name)
        elif "1x2" not in cap.markets:
            other.append(name)
        elif cap.name in source_registry.PARKED_PREDICTORS:
            parked.append(name)
        elif cap.tier == source_registry.TIER_LIVE:
            eligible.append(name)
            live.append(name)
        elif cap.tier == source_registry.TIER_SHADOW:
            # Counted toward quorum, and still reported separately so the
            # shadow share of any selection stays visible.
            eligible.append(name)
            shadow.append(name)
        else:
            other.append(name)
    return {
        "sources_seen": seen,
        "production_eligible_1x2_voters": sorted(eligible),
        "live_1x2_voters": sorted(live),
        "shadow_1x2_sources": sorted(shadow),
        "parked_sources": sorted(parked),
        "non_voter_sources": sorted(other),
        "unregistered_sources": sorted(unregistered),
    }


def _tiers(sources: Iterable[str]) -> dict[str, str]:
    tiers = {}
    for name in sources:
        cap = source_registry.get(name)
        tiers[name] = cap.tier if cap is not None else "unregistered"
    return tiers


def build_lineage(pick: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct, from the pick itself, the evidence its rule claims."""
    rule_id = pick.get("rule_id") or pick.get("edge_rule")
    voters = pick.get("source_voters") or []
    roles = classify_voters(voters)
    required = required_voter_count(rule_id)
    eligible = roles["production_eligible_1x2_voters"]

    lineage: dict[str, Any] = {
        "event_date": pick.get("event_date") or pick.get("date"),
        "home": pick.get("home"),
        "away": pick.get("away"),
        "selection": pick.get("selection") or pick.get("pick"),
        "rule_id": rule_id,
        "required_eligible_voters": required,
        "eligible_voter_count": len(eligible),
        "source_tiers": _tiers(roles["sources_seen"]),
        "ml_anchor_sources": sorted(
            s for s in roles["sources_seen"]
            if source_registry.has_ml_feature_support(s)),
        "kickoff_source": pick.get("timing_source"),
        "price_source": pick.get("pricing_source") or pick.get("odds_source"),
        "price_evidence": pick.get("price_evidence"),
        "price_quarantine_reason": pick.get("price_quarantine_reason"),
        "odds_replaced": pick.get("odds_replaced"),
        "price_push_eligible": pick.get("price_push_eligible"),
        "odds": pick.get("odds"),
    }
    lineage.update(roles)

    status, reasons = RECONCILED, []
    if not voters:
        status = BLOCKED_NO_EVIDENCE
        reasons.append("the selection records no source voters, so its rule "
                       "claim cannot be reconstructed")
    elif required is not None and len(eligible) < required:
        status = BLOCKED_INSUFFICIENT_VOTERS
        shadow = roles["shadow_1x2_sources"]
        detail = (f"rule {rule_id} claims {required} source(s) but only "
                  f"{len(eligible)} production-eligible 1X2 voter(s) "
                  f"({', '.join(eligible) or 'none'}) support it")
        ignored = roles["non_voter_sources"] + roles["parked_sources"]
        if ignored:
            detail += (f"; {', '.join(ignored)} contributed rows but "
                       f"carries no eligible 1X2 vote")
        reasons.append(detail)

    lineage["status"] = status
    lineage["reasons"] = reasons
    return lineage


def reconcile_selections(picks: Iterable[dict]) -> list[dict]:
    return [build_lineage(pick) for pick in picks]


def blocking(lineages: Iterable[dict]) -> list[dict]:
    return [l for l in lineages if l["status"] in BLOCKING_STATUSES]


def render_lineage_lines(lineages: list[dict]) -> list[str]:
    """Operator-readable lineage, printed next to the dispatch plan."""
    out = ["PRODUCTION SELECTION EVIDENCE LINEAGE"]
    if not lineages:
        out.append("  no production selections to reconcile")
        return out
    for lineage in lineages:
        out.append(f"  {lineage['event_date']} | {lineage['home']} vs "
                   f"{lineage['away']} | {lineage['selection']} | "
                   f"rule={lineage['rule_id']}")
        out.append(f"    required_eligible_voters: "
                   f"{lineage['required_eligible_voters']}")
        out.append(f"    production_eligible_1x2_voters: "
                   f"{', '.join(lineage['production_eligible_1x2_voters']) or '-'}")
        out.append(f"    shadow_1x2_sources: "
                   f"{', '.join(lineage['shadow_1x2_sources']) or '-'}")
        out.append(f"    non_voter_sources: "
                   f"{', '.join(lineage['non_voter_sources']) or '-'}")
        out.append(f"    source_tiers: " + (", ".join(
            f"{k}={v}" for k, v in sorted(lineage["source_tiers"].items()))
            or "-"))
        out.append(f"    ml_anchor_sources: "
                   f"{', '.join(lineage['ml_anchor_sources']) or '-'}")
        out.append(f"    kickoff_source: {lineage['kickoff_source'] or '-'}")
        out.append(f"    price_source: {lineage['price_source'] or '-'} | "
                   f"odds={lineage['odds'] if lineage['odds'] is not None else '-'} | "
                   f"quarantine={lineage['price_quarantine_reason'] or '-'}")
        out.append(f"    status: {lineage['status']}")
        for reason in lineage["reasons"]:
            out.append(f"    reason: {reason}")
    return out
