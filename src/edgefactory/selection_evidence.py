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

    lineage["price"] = classify_price(pick)
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
        out.extend(render_price_lines(lineage["price"]))
        out.append(f"    status: {lineage['status']}")
        for reason in lineage["reasons"]:
            out.append(f"    reason: {reason}")
    return out


# ---------------------------------------------------------------------------
# price coverage
#
# "no price" was doing too much work. A fixture nobody quotes, a fixture
# priced only by a shadow source, and a fixture whose price feed cannot
# be joined are three different problems with three different fixes, and
# only some of them bear on whether a price is safe to bet.
# ---------------------------------------------------------------------------

P_NO_ELIGIBLE_SOURCE = "no_eligible_price_source"
P_SHADOW_SOURCE = "price_present_from_shadow_source"
P_EMBEDDED = "price_present_from_embedded_source"
P_JOIN_FAILED = "price_join_failed"
P_ODDS_ONLY_NO_IDENTITY = "odds_only_source_has_no_fixture_identity"
P_UNKNOWN = "price_unknown"
P_QUARANTINED = "price_quarantined"
P_SUSPECT = "price_suspect"
P_SAFE = "price_safe_for_execution"

_EMBEDDED_MARKERS = ("embedded", "source_embedded")


def _price_owner(label: str) -> str | None:
    """The registered source a price label refers to, if any."""
    cleaned = str(label or "").lower().strip()
    for suffix in ("_embedded_odds", "_embedded", "_odds"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
            break
    return cleaned if source_registry.get(cleaned) is not None else None


def classify_price(pick: dict[str, Any], *,
                   price_join_available: bool | None = None) -> dict[str, Any]:
    """Describe a selection's price provenance and execution safety.

    Execution safety is not inferred from the presence of a number. A
    price is only called safe when it exists, is not quarantined, is not
    flagged suspect, and comes from a path the price-integrity policy
    already permits.
    """
    odds = pick.get("odds")
    source = str(pick.get("pricing_source") or pick.get("odds_source") or "")
    quarantine = pick.get("price_quarantine_reason")
    evidence = pick.get("price_evidence")

    classification: dict[str, Any] = {
        "odds": odds,
        "price_source": source or None,
        "price_evidence": evidence,
        "price_quarantine_reason": quarantine,
        "odds_replaced": pick.get("odds_replaced"),
        "price_push_eligible": pick.get("price_push_eligible"),
        "price_tier": pick.get("price_tier"),
    }

    states: list[str] = []
    if odds in (None, "", 0):
        if price_join_available is False:
            states.append(P_ODDS_ONLY_NO_IDENTITY)
            states.append(P_UNKNOWN)
        elif source:
            states.append(P_JOIN_FAILED)
        else:
            states.append(P_NO_ELIGIBLE_SOURCE)
        classification["states"] = states
        classification["execution_safe"] = False
        return classification

    # pricing_source is often generic ("source_embedded_odds"), so the
    # bookmaker field is consulted too: it names the predictor the quote
    # actually came from, which is what decides whether the price is
    # leaning on a shadow-tier source.
    bookmaker = str(pick.get("bookmaker") or "")
    embedded = any(marker in text.lower()
                   for text in (source, bookmaker)
                   for marker in _EMBEDDED_MARKERS)
    if embedded:
        states.append(P_EMBEDDED)
    owner = _price_owner(bookmaker) or _price_owner(source)
    if owner:
        classification["price_owner"] = owner
        cap = source_registry.get(owner)
        if cap is not None and cap.tier == source_registry.TIER_SHADOW:
            states.append(P_SHADOW_SOURCE)

    if quarantine:
        states.append(P_QUARANTINED)
    if pick.get("price_suspect"):
        states.append(P_SUSPECT)

    safe = not quarantine and not pick.get("price_suspect")
    if safe:
        states.append(P_SAFE)
    classification["states"] = states
    classification["execution_safe"] = safe
    return classification


def render_price_lines(classification: dict) -> list[str]:
    return [
        f"    price: {classification['odds'] if classification['odds'] is not None else '-'}"
        f" | source={classification['price_source'] or '-'}"
        f" | tier={classification['price_tier'] or '-'}",
        f"    price_states: {', '.join(classification['states']) or '-'}",
        f"    execution_safe: "
        f"{'yes' if classification['execution_safe'] else 'no'}",
    ]
