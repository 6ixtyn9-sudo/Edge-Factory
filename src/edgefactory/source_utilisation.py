"""Why is each source in the role it is in?

A source that is captured but not consumed is either correctly withheld
or quietly broken, and the two look identical from a row count. This
audit separates them by comparing what the registry *declares* a source
can provide against what its rows *actually* contain:

  declared and present      -> working as configured
  declared but absent       -> parser or capture gap, worth fixing
  present but not declared  -> config gap; the data exists and is ignored
  neither                   -> correctly modelled

It recommends nothing and promotes nothing. Promotion needs settlement
evidence and operator sign-off, and a capture count is not evidence of
accuracy. The most this produces is a promotion *candidate* list, with
the evidence still outstanding stated explicitly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from . import source_registry

# Utilisation findings ------------------------------------------------------
U_WORKING = "declared_and_present"
U_PARSER_GAP = "declared_but_absent_from_rows"
U_CONFIG_GAP = "present_in_rows_but_not_declared"
U_NOT_APPLICABLE = "not_declared_and_not_present"
U_NO_ROWS = "no_rows_to_judge"
U_IDENTITY_GAP = "rows_present_but_carry_no_fixture_identity"

# Objective blockers --------------------------------------------------------
B_NOT_SETTLEMENT_VALIDATED = "not_settlement_validated"
B_NO_COVERAGE = "no_prediction_to_result_coverage"
B_PARSER_MISSING = "parser_missing_probability_fields"
B_NO_TRUSTED_KICKOFF = "no_trusted_kickoff"
B_TIER_SHADOW = "source_tier_shadow"
B_DONOR_ONLY = "donor_only"
B_ODDS_ONLY = "odds_only"
B_TRANSPORT = "transport_unavailable"
B_PARKED = "parked_or_disabled"
B_CONFIG_EXCLUDES = "config_excludes_source"
B_NO_ROWS = "no_rows_captured"

MARKETS = ("1x2", "ou", "btts", "odds", "results")


def _present_markets(summary: dict) -> dict[str, bool]:
    """What the rows actually contained, per market."""
    return {
        "1x2": bool(summary.get("rows_with_1x2")),
        "ou": bool(summary.get("rows_with_ou")),
        "btts": bool(summary.get("rows_with_btts")),
        "odds": bool(summary.get("rows_with_price")),
        "results": bool(summary.get("already_settled_rows")),
    }


def compare_markets(source: str, summary: dict) -> dict[str, str]:
    """Declared capability against observed rows, one verdict per market."""
    cap = source_registry.get(source)
    declared = set(cap.markets) if cap is not None else set()
    present = _present_markets(summary)
    raw_rows = int(summary.get("raw_rows") or 0)
    # A source that captured nothing cannot demonstrate a capability, and
    # absence of rows is not evidence of a broken parser.
    identity_less = (raw_rows and not int(summary.get("fixture_count") or 0)
                     and int(summary.get("rows_without_fixture_identity")
                             or 0))
    out: dict[str, str] = {}
    for market in MARKETS:
        is_declared = market in declared
        is_present = present.get(market, False)
        if not raw_rows:
            out[market] = U_NO_ROWS if is_declared else U_NOT_APPLICABLE
            continue
        if is_declared and not is_present and identity_less:
            # The rows exist but cannot be tied to a fixture, so the
            # market cannot be observed either way from here.
            out[market] = U_IDENTITY_GAP
            continue
        if is_declared and is_present:
            out[market] = U_WORKING
        elif is_declared and not is_present:
            out[market] = U_PARSER_GAP
        elif is_present and not is_declared:
            out[market] = U_CONFIG_GAP
        else:
            out[market] = U_NOT_APPLICABLE
    return out


def audit_source(source: str, summary: dict, *,
                 validation_states: dict[str, str] | None = None,
                 eligible_voters: Iterable[str] = ()) -> dict[str, Any]:
    """One source's role, what it supplies, and why it is not used further."""
    cap = source_registry.get(source)
    states = validation_states or {}
    markets = compare_markets(source, summary)
    raw_rows = int(summary.get("raw_rows") or 0)
    validation = str(states.get(source) or "unknown")

    blockers: list[str] = []
    if cap is None:
        blockers.append(B_CONFIG_EXCLUDES)
    else:
        if source in source_registry.PARKED_PREDICTORS:
            blockers.append(B_PARKED)
        if cap.tier == source_registry.TIER_DONOR:
            blockers.append(B_DONOR_ONLY)
        if cap.tier == source_registry.TIER_PRICING:
            blockers.append(B_ODDS_ONLY)
        if cap.tier == source_registry.TIER_SHADOW:
            blockers.append(B_TIER_SHADOW)
        if "1x2" in cap.markets and markets["1x2"] == U_PARSER_GAP and raw_rows:
            # The registry says this source offers 1X2 and the rows say
            # otherwise. That is a defect, not a policy decision.
            blockers.append(B_PARSER_MISSING)
        if "1x2" in cap.markets and not cap.provides_kickoff:
            blockers.append(B_NO_TRUSTED_KICKOFF)

    if not raw_rows:
        blockers.append(B_NO_ROWS)
    if validation in ("unknown", "", "insufficient"):
        blockers.append(B_NOT_SETTLEMENT_VALIDATED)
    elif validation in ("no_coverage", "uncovered"):
        blockers.append(B_NO_COVERAGE)

    # Anything the rows carry that the configuration does not claim is
    # capability the pipeline is paying for and not spending.
    unused = sorted(m for m, verdict in markets.items()
                    if verdict == U_CONFIG_GAP)
    # "results" is excluded: a result arrives after the match, so its
    # absence from a same-day row is the normal state of the world, not
    # a parser gap.
    broken = sorted(m for m, verdict in markets.items()
                    if verdict == U_PARSER_GAP and raw_rows
                    and m != "results")

    return {
        "source": source,
        "tier": cap.tier if cap is not None else "unregistered",
        "registered": cap is not None,
        "raw_rows": raw_rows,
        "fixture_count": int(summary.get("fixture_count") or 0),
        "declared_markets": list(cap.markets) if cap is not None else [],
        "market_utilisation": markets,
        "unused_capability": unused,
        "declared_but_missing": broken,
        "provides_kickoff": bool(cap.provides_kickoff) if cap else False,
        "ml_feature_provider": bool(cap.ml_feature_provider) if cap else False,
        "is_production_eligible_voter": source in set(eligible_voters),
        "settlement_validation": validation,
        "blockers": sorted(set(blockers)),
    }


def promotion_candidates(audits: list[dict]) -> list[dict]:
    """Sources whose only remaining blocker is evidence, not capability.

    This is a shortlist for human review. It is never a promotion, and
    the outstanding evidence is named so nobody mistakes it for one.
    """
    out = []
    for audit in audits:
        if audit["tier"] != source_registry.TIER_SHADOW:
            continue
        if not audit["raw_rows"]:
            continue
        if B_PARSER_MISSING in audit["blockers"]:
            continue
        outstanding = [b for b in audit["blockers"]
                       if b in (B_NOT_SETTLEMENT_VALIDATED, B_NO_COVERAGE)]
        if not outstanding:
            continue
        out.append({
            "source": audit["source"],
            "raw_rows": audit["raw_rows"],
            "supplies": [m for m, v in audit["market_utilisation"].items()
                         if v == U_WORKING],
            "outstanding_evidence": outstanding,
            "note": ("capture volume is not accuracy; promotion requires "
                     "settlement evidence and operator sign-off"),
        })
    return out


def build_utilisation(day_summaries: list[dict], *,
                      validation_states: dict[str, str] | None = None,
                      eligible_voters: Iterable[str] = ()) -> dict[str, Any]:
    audits = [audit_source(s["source"], s,
                           validation_states=validation_states,
                           eligible_voters=eligible_voters)
              for s in day_summaries]
    return {
        "sources": audits,
        "parser_gaps": sorted(a["source"] for a in audits
                              if a["declared_but_missing"]),
        "config_gaps": sorted(a["source"] for a in audits
                              if a["unused_capability"]),
        "promotion_candidates": promotion_candidates(audits),
    }


def render_utilisation_lines(utilisation: dict) -> list[str]:
    out = ["SOURCE UTILISATION AUDIT",
           "  declared capability vs what the rows actually contained"]
    header = ("  source", "tier", "rows", "1x2", "ou", "btts", "odds",
              "eligible", "validation", "blockers")
    out.append("  " + " | ".join(header).strip())
    for audit in utilisation["sources"]:
        markets = audit["market_utilisation"]

        def mark(name: str) -> str:
            return {U_WORKING: "yes", U_PARSER_GAP: "MISSING",
                    U_CONFIG_GAP: "UNUSED", U_NO_ROWS: "no_rows",
                    U_IDENTITY_GAP: "no_identity",
                    U_NOT_APPLICABLE: "-"}[markets[name]]

        out.append(
            f"  {audit['source']} | {audit['tier']} | {audit['raw_rows']} | "
            f"{mark('1x2')} | {mark('ou')} | {mark('btts')} | {mark('odds')} | "
            f"{'yes' if audit['is_production_eligible_voter'] else 'no'} | "
            f"{audit['settlement_validation']} | "
            f"{', '.join(audit['blockers']) or '-'}")

    if utilisation["parser_gaps"]:
        out.append("  DECLARED BUT ABSENT (parser or capture gap, fixable):")
        for source in utilisation["parser_gaps"]:
            audit = next(a for a in utilisation["sources"]
                         if a["source"] == source)
            out.append(f"    {source}: registry declares "
                       f"{', '.join(audit['declared_but_missing'])} but no "
                       f"row carried it")
    if utilisation["config_gaps"]:
        out.append("  PRESENT BUT NOT DECLARED (capability not being spent):")
        for source in utilisation["config_gaps"]:
            audit = next(a for a in utilisation["sources"]
                         if a["source"] == source)
            out.append(f"    {source}: rows carry "
                       f"{', '.join(audit['unused_capability'])} which the "
                       f"registry does not claim")

    candidates = utilisation["promotion_candidates"]
    out.append("  PROMOTION CANDIDATES (review only, never automatic):")
    if not candidates:
        out.append("    none")
    for candidate in candidates:
        out.append(f"    {candidate['source']}: supplies "
                   f"{', '.join(candidate['supplies']) or 'nothing usable'}; "
                   f"outstanding: "
                   f"{', '.join(candidate['outstanding_evidence'])}")
    out.append("  no source is promoted, certified or enabled by this report")
    return out
