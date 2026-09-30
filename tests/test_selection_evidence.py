"""A rule_id is a claim about evidence. These tests hold it to that claim.

``1x2_two_source_p55_unanimous`` asserts two sources agreed. If the
selection cannot show two eligible voters, the name describes something
that did not happen, and the selection is withheld rather than dispatched
under a false label.

Eligibility is tier-derived from the capability registry and, by operator
decision, covers both live and shadow 1X2 predictors: shadow means a
settlement record still accruing, not an opinion that is discarded. This
matches ``fresh_production_voters()``, so the census and the dispatch
plan count the same voters. Parked, donor and pricing sources carry no
eligible 1X2 vote.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from edgefactory import selection_evidence as se     # noqa: E402
from edgefactory import source_registry              # noqa: E402


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fp = _load("fresh_production_evidence_under_test", "fresh_production.py")


def _pick(**over):
    base = {
        "date": "2026-10-01", "event_date": "2026-10-01",
        "home": "Panama", "away": "New Zealand",
        "pick": "home", "selection": "home",
        "rule_id": "1x2_two_source_p55_unanimous",
        "source_voters": ["bzzoiro", "prosoccer"],
        "timing_source": "bzzoiro", "odds": 2.25,
        "pricing_source": "source_embedded_odds",
    }
    base.update(over)
    return base


# --- what the rule id claims ----------------------------------------------


def test_required_voter_count_is_read_from_the_rule_id():
    assert se.required_voter_count("1x2_two_source_p55_unanimous") == 2
    assert se.required_voter_count("1x2_three_source_p60_unanimous") == 3
    assert se.required_voter_count("1x2_four_source_p55") == 4
    assert se.required_voter_count("fresh_1x2_v2_p55") == 2


def test_a_rule_making_no_voter_claim_is_not_second_guessed():
    assert se.required_voter_count("ml_meta_calibrated_p60") is None
    assert se.required_voter_count(None) is None
    assert se.required_voter_count("") is None


# --- eligibility is tier-derived, never hardcoded -------------------------


def test_live_and_shadow_1x2_sources_are_production_eligible():
    eligible = se.eligible_1x2_voters(
        ["bzzoiro", "prosoccer", "bettingclosed", "theoddsapi_odds"])
    assert "bzzoiro" in eligible                # live
    assert "prosoccer" in eligible              # shadow still votes
    assert "bettingclosed" not in eligible      # donor: no 1X2 opinion
    assert "theoddsapi_odds" not in eligible    # pricing: no 1X2 opinion


def test_a_parked_predictor_never_votes():
    """Parked is an availability decision, and it is honoured here."""
    assert source_registry.PARKED_PREDICTORS
    for name in source_registry.PARKED_PREDICTORS:
        assert se.eligible_1x2_voters([name]) == []


def test_eligibility_matches_the_lane_that_forms_the_vote():
    """Census and dispatch plan must not count different voters."""
    lane = set(fp.fresh_production_voters())
    derived = set(se.eligible_1x2_voters(source_registry.names()))
    assert derived == lane


def test_eligibility_tracks_the_registry_not_a_literal_list():
    for name in se.eligible_1x2_voters(source_registry.names()):
        cap = source_registry.get(name)
        assert cap.tier in (source_registry.TIER_LIVE,
                            source_registry.TIER_SHADOW)
        assert "1x2" in cap.markets
        assert name not in source_registry.PARKED_PREDICTORS


def test_an_unregistered_source_is_never_silently_counted():
    roles = se.classify_voters(["bzzoiro", "not_a_real_source"])
    assert roles["production_eligible_1x2_voters"] == ["bzzoiro"]
    assert roles["unregistered_sources"] == ["not_a_real_source"]


# --- the Panama regression -------------------------------------------------


def test_panama_shape_reconciles_and_shows_its_shadow_share():
    """bzzoiro live + prosoccer shadow is two eligible voters.

    The selection is valid, but the lineage must still make plain that
    half its quorum came from a shadow-tier source.
    """
    lineage = se.build_lineage(_pick())

    assert lineage["status"] == se.RECONCILED
    assert lineage["production_eligible_1x2_voters"] == ["bzzoiro", "prosoccer"]
    assert lineage["live_1x2_voters"] == ["bzzoiro"]
    assert lineage["shadow_1x2_sources"] == ["prosoccer"]
    assert lineage["eligible_voter_count"] == 2
    assert lineage["required_eligible_voters"] == 2
    assert lineage["reasons"] == []


def test_two_live_voters_reconcile():
    lineage = se.build_lineage(_pick(source_voters=["bzzoiro", "zulubet"]))
    assert lineage["status"] == se.RECONCILED
    assert lineage["eligible_voter_count"] == 2
    assert lineage["reasons"] == []


def test_a_selection_with_no_voters_cannot_be_reconstructed():
    lineage = se.build_lineage(_pick(source_voters=[]))
    assert lineage["status"] == se.BLOCKED_NO_EVIDENCE
    assert "cannot be reconstructed" in " ".join(lineage["reasons"])


def test_shadow_sources_can_form_a_quorum_between_themselves():
    lineage = se.build_lineage(
        _pick(source_voters=["prosoccer", "windrawwin", "predictz"]))
    assert lineage["status"] == se.RECONCILED
    assert lineage["eligible_voter_count"] == 3
    assert lineage["live_1x2_voters"] == []


def test_a_single_voter_still_cannot_satisfy_a_two_source_rule():
    """The invariant still bites where the claim is genuinely false."""
    lineage = se.build_lineage(_pick(source_voters=["bzzoiro"]))
    assert lineage["status"] == se.BLOCKED_INSUFFICIENT_VOTERS
    assert "claims 2 source(s) but only 1" in " ".join(lineage["reasons"])


def test_donor_and_pricing_rows_cannot_pad_a_quorum():
    lineage = se.build_lineage(
        _pick(source_voters=["bzzoiro", "bettingclosed", "theoddsapi_odds"]))
    assert lineage["status"] == se.BLOCKED_INSUFFICIENT_VOTERS
    assert lineage["production_eligible_1x2_voters"] == ["bzzoiro"]
    detail = " ".join(lineage["reasons"])
    assert "carries no eligible 1X2 vote" in detail


def test_lineage_records_price_and_kickoff_provenance():
    lineage = se.build_lineage(_pick(
        price_quarantine_reason="suspect_outlier", odds_replaced=True))
    assert lineage["price_source"] == "source_embedded_odds"
    assert lineage["odds"] == 2.25
    assert lineage["price_quarantine_reason"] == "suspect_outlier"
    assert lineage["odds_replaced"] is True
    assert lineage["kickoff_source"] == "bzzoiro"
    assert lineage["source_tiers"] == {"bzzoiro": "live", "prosoccer": "shadow"}


# --- enforcement in the dispatch plan -------------------------------------


def test_the_dispatch_plan_withholds_an_unsupported_selection():
    plan = fp.build_dispatch_plan(
        run_date="2026-09-30", same_day_rows=[],
        horizon_rows=[_pick(source_voters=["bzzoiro"])],
        horizon={"horizon_end": "2026-10-02", "max_lead_hours": 48,
                 "min_lead_minutes": 30})

    assert plan["horizon_picks"] == []
    assert plan["horizon_pick_count"] == 0
    assert plan["blocked_selection_count"] == 1
    blocked = plan["blocked_selections"][0]
    assert blocked["dispatch_blocked_reason"] == se.BLOCKED_INSUFFICIENT_VOTERS
    assert blocked["home"] == "Panama"
    # Nothing is announced for a date with no admissible pick.
    assert plan["notification_action"] == "empty_slate"
    assert plan["event_dates"] == []


def test_the_dispatch_plan_keeps_a_supported_selection():
    plan = fp.build_dispatch_plan(
        run_date="2026-09-30", same_day_rows=[],
        horizon_rows=[_pick(source_voters=["bzzoiro", "zulubet"])],
        horizon={"horizon_end": "2026-10-02", "max_lead_hours": 48,
                 "min_lead_minutes": 30})

    assert plan["horizon_pick_count"] == 1
    assert plan["blocked_selection_count"] == 0
    assert plan["notification_action"] == "future_pick"
    lineage = plan["horizon_picks"][0]["evidence_lineage"]
    assert lineage["status"] == se.RECONCILED


def test_a_blocked_selection_is_not_published_or_announced():
    """Blocking must remove it from every downstream surface."""
    plan = fp.build_dispatch_plan(
        run_date="2026-09-30", same_day_rows=[],
        horizon_rows=[_pick(source_voters=["bzzoiro"])],
        horizon={"horizon_end": "2026-10-02", "max_lead_hours": 48,
                 "min_lead_minutes": 30})

    assert plan["same_day_picks"] == []
    assert plan["horizon_picks"] == []
    assert plan["future_event_dates"] == []
    assert plan["sync_dates"] == ["2026-09-30"]
    published = plan["same_day_picks"] + plan["horizon_picks"]
    assert not any(p.get("home") == "Panama" for p in published)


def test_blocking_preserves_the_evidence_rather_than_discarding_it():
    plan = fp.build_dispatch_plan(
        run_date="2026-09-30", same_day_rows=[],
        horizon_rows=[_pick(source_voters=["bzzoiro"])],
        horizon={"horizon_end": "2026-10-02", "max_lead_hours": 48,
                 "min_lead_minutes": 30})
    blocked = plan["blocked_selections"][0]
    assert blocked["evidence_lineage"]["production_eligible_1x2_voters"] \
        == ["bzzoiro"]
    assert blocked["odds"] == 2.25
    assert blocked["rule_id"] == "1x2_two_source_p55_unanimous"


# --- reporting -------------------------------------------------------------


def test_lineage_renders_for_the_operator():
    lines = se.render_lineage_lines([se.build_lineage(_pick())])
    text = "\n".join(lines)
    assert "PRODUCTION SELECTION EVIDENCE LINEAGE" in text
    assert "Panama vs New Zealand" in text
    assert "production_eligible_1x2_voters: bzzoiro, prosoccer" in text
    assert "shadow_1x2_sources: prosoccer" in text
    assert "source_tiers: bzzoiro=live, prosoccer=shadow" in text
    assert se.RECONCILED in text


def test_a_blocked_lineage_renders_its_reason():
    lines = se.render_lineage_lines(
        [se.build_lineage(_pick(source_voters=["bzzoiro"]))])
    text = "\n".join(lines)
    assert se.BLOCKED_INSUFFICIENT_VOTERS in text
    assert "reason:" in text


def test_empty_lineage_renders_without_pretending():
    text = "\n".join(se.render_lineage_lines([]))
    assert "no production selections to reconcile" in text


def test_blocking_helper_selects_only_blocked_lineages():
    lineages = se.reconcile_selections(
        [_pick(source_voters=["bzzoiro"]),
         _pick(source_voters=["bzzoiro", "zulubet"])])
    blocked = se.blocking(lineages)
    assert len(blocked) == 1
    assert blocked[0]["status"] == se.BLOCKED_INSUFFICIENT_VOTERS


def test_the_module_does_not_size_stakes_or_form_tickets():
    src = (ROOT / "src" / "edgefactory" / "selection_evidence.py").read_text()
    for forbidden in ("stake_units", "bankroll", "kelly", "select_accas",
                      "compute_bucket", "1u"):
        assert forbidden not in src


# ===========================================================================
# Price coverage taxonomy
#
# "no price" was doing too much work. A fixture nobody quotes, one priced
# only by a shadow source, and one whose feed cannot be joined are three
# different problems, and only some bear on execution safety.
# ===========================================================================


def test_a_missing_price_with_no_source_is_no_eligible_source():
    result = se.classify_price(_pick(odds=None, pricing_source=None))
    assert se.P_NO_ELIGIBLE_SOURCE in result["states"]
    assert result["execution_safe"] is False


def test_a_missing_price_with_a_named_source_is_a_join_failure():
    result = se.classify_price(_pick(odds=None,
                                     pricing_source="betexplorer_odds"))
    assert se.P_JOIN_FAILED in result["states"]
    assert result["execution_safe"] is False


def test_an_identity_less_feed_makes_price_unknown_not_absent():
    """Unknown and absent are different claims."""
    result = se.classify_price(_pick(odds=None), price_join_available=False)
    assert se.P_ODDS_ONLY_NO_IDENTITY in result["states"]
    assert se.P_UNKNOWN in result["states"]
    assert se.P_NO_ELIGIBLE_SOURCE not in result["states"]


def test_an_embedded_shadow_price_is_named_as_such():
    """The real shape: pricing_source is generic, bookmaker is not."""
    result = se.classify_price(_pick(
        odds=2.25, pricing_source="source_embedded_odds",
        bookmaker="prosoccer_embedded"))

    assert result["price_owner"] == "prosoccer"
    assert se.P_EMBEDDED in result["states"]
    assert se.P_SHADOW_SOURCE in result["states"]


def test_a_live_source_price_is_not_flagged_shadow():
    result = se.classify_price(_pick(odds=2.25,
                                     pricing_source="bzzoiro_odds"))
    assert se.P_SHADOW_SOURCE not in result["states"]
    assert se.P_SAFE in result["states"]


def test_a_quarantined_price_is_never_execution_safe():
    result = se.classify_price(_pick(
        odds=2.25, price_quarantine_reason="outlier_vs_consensus"))
    assert se.P_QUARANTINED in result["states"]
    assert se.P_SAFE not in result["states"]
    assert result["execution_safe"] is False


def test_a_suspect_price_is_never_execution_safe():
    result = se.classify_price(_pick(odds=2.25, price_suspect=True))
    assert se.P_SUSPECT in result["states"]
    assert result["execution_safe"] is False


def test_price_states_are_attached_to_the_lineage():
    lineage = se.build_lineage(_pick(
        odds=2.25, pricing_source="source_embedded_odds",
        bookmaker="prosoccer_embedded"))
    assert lineage["price"]["price_owner"] == "prosoccer"
    text = "\n".join(se.render_lineage_lines([lineage]))
    assert "price_states:" in text
    assert "execution_safe: yes" in text
    assert se.P_SHADOW_SOURCE in text


def test_an_unsafe_price_renders_as_unsafe():
    lineage = se.build_lineage(_pick(
        odds=2.25, price_quarantine_reason="outlier_vs_consensus"))
    text = "\n".join(se.render_lineage_lines([lineage]))
    assert "execution_safe: no" in text
