"""Is a source withheld on purpose, or quietly broken?

Both look identical from a row count, which is how an under-utilised
source stays invisible. This audit separates them by comparing what the
registry declares a source can supply against what its rows actually
contain.

It promotes nothing. Capture volume is not accuracy, and the most it
produces is a review shortlist with the missing evidence named.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from edgefactory import source_registry as sr        # noqa: E402
from edgefactory import source_utilisation as su     # noqa: E402


def _summary(source, **over):
    base = {"source": source, "raw_rows": 10, "fixture_count": 10,
            "rows_with_1x2": 0, "rows_with_ou": 0, "rows_with_btts": 0,
            "rows_with_price": 0, "already_settled_rows": 0,
            "rows_without_fixture_identity": 0}
    base.update(over)
    return base


# --- the core discrimination ----------------------------------------------


def test_a_declared_market_present_in_rows_is_working():
    markets = su.compare_markets("zulubet", _summary("zulubet",
                                                     rows_with_1x2=10))
    assert markets["1x2"] == su.U_WORKING


def test_a_declared_market_absent_from_rows_is_a_parser_gap():
    """The registry promises 1X2 and no row has it: a defect, not policy."""
    markets = su.compare_markets("zulubet", _summary("zulubet",
                                                     rows_with_1x2=0))
    assert markets["1x2"] == su.U_PARSER_GAP

    audit = su.audit_source("zulubet", _summary("zulubet", rows_with_1x2=0))
    assert su.B_PARSER_MISSING in audit["blockers"]
    assert audit["declared_but_missing"] == ["1x2"]


def test_a_market_present_but_undeclared_is_a_config_gap():
    """Capability the pipeline captures and then ignores."""
    markets = su.compare_markets("zulubet", _summary("zulubet",
                                                     rows_with_1x2=10,
                                                     rows_with_price=10))
    assert "odds" not in sr.get("zulubet").markets
    assert markets["odds"] == su.U_CONFIG_GAP

    audit = su.audit_source("zulubet", _summary("zulubet", rows_with_1x2=10,
                                                rows_with_price=10))
    assert audit["unused_capability"] == ["odds"]


def test_no_rows_is_never_reported_as_a_parser_gap():
    """Absence of rows is not evidence of a broken parser."""
    audit = su.audit_source("vitibet", _summary("vitibet", raw_rows=0,
                                                fixture_count=0))
    assert audit["market_utilisation"]["1x2"] == su.U_NO_ROWS
    assert audit["declared_but_missing"] == []
    assert su.B_PARSER_MISSING not in audit["blockers"]
    assert su.B_NO_ROWS in audit["blockers"]


def test_identity_less_rows_are_not_called_a_parser_gap():
    """betexplorer_odds: rows exist but cannot be tied to a fixture."""
    audit = su.audit_source("betexplorer_odds", _summary(
        "betexplorer_odds", raw_rows=174, fixture_count=0,
        rows_without_fixture_identity=174))
    assert audit["market_utilisation"]["odds"] == su.U_IDENTITY_GAP
    assert audit["declared_but_missing"] == []


# --- the specific sources the operator asked about ------------------------


def test_scoutingstats_is_not_configured_as_a_1x2_source():
    """It is OU/BTTS/results by configuration, not a 1X2 voter."""
    cap = sr.get("scoutingstats")
    assert "1x2" not in cap.markets
    assert set(cap.markets) >= {"ou", "btts"}

    audit = su.audit_source("scoutingstats", _summary(
        "scoutingstats", rows_with_ou=10, rows_with_btts=10))
    assert audit["market_utilisation"]["ou"] == su.U_WORKING
    assert audit["market_utilisation"]["btts"] == su.U_WORKING


def test_scoutingstats_carrying_1x2_rows_is_surfaced_as_a_config_gap():
    """If the rows do carry 1X2, that is capability going unspent."""
    audit = su.audit_source("scoutingstats", _summary(
        "scoutingstats", rows_with_1x2=10, rows_with_ou=10))
    assert audit["market_utilisation"]["1x2"] == su.U_CONFIG_GAP
    assert "1x2" in audit["unused_capability"]


def test_betclan_is_blocked_by_kickoff_not_by_tier():
    cap = sr.get("betclan")
    assert cap.tier == sr.TIER_LIVE
    assert cap.provides_kickoff is False

    audit = su.audit_source("betclan", _summary("betclan", rows_with_1x2=60))
    assert su.B_NO_TRUSTED_KICKOFF in audit["blockers"]
    assert su.B_TIER_SHADOW not in audit["blockers"]


def test_prosoccer_is_shadow_and_says_so():
    audit = su.audit_source("prosoccer", _summary("prosoccer",
                                                  rows_with_1x2=15))
    assert audit["tier"] == sr.TIER_SHADOW
    assert su.B_TIER_SHADOW in audit["blockers"]
    assert su.B_PARSER_MISSING not in audit["blockers"]


def test_a_donor_and_a_pricing_source_are_labelled_as_such():
    donor = su.audit_source("bettingclosed", _summary("bettingclosed"))
    pricing = su.audit_source("theoddsapi_odds", _summary("theoddsapi_odds"))
    assert su.B_DONOR_ONLY in donor["blockers"]
    assert su.B_ODDS_ONLY in pricing["blockers"]


def test_a_parked_source_is_reported_parked_not_broken():
    audit = su.audit_source("forebet", _summary("forebet", rows_with_1x2=157))
    assert su.B_PARKED in audit["blockers"]
    assert audit["market_utilisation"]["1x2"] == su.U_WORKING


# --- validation evidence ---------------------------------------------------


def test_an_unvalidated_source_is_blocked_on_evidence():
    audit = su.audit_source("prosoccer", _summary("prosoccer",
                                                  rows_with_1x2=15),
                            validation_states={"prosoccer": "unknown"})
    assert su.B_NOT_SETTLEMENT_VALIDATED in audit["blockers"]


def test_validation_state_is_reported_verbatim():
    audit = su.audit_source("prosoccer", _summary("prosoccer"),
                            validation_states={"prosoccer": "partial"})
    assert audit["settlement_validation"] == "partial"


# --- promotion candidates are a shortlist, never an action ----------------


def test_a_promotion_candidate_names_its_outstanding_evidence():
    audits = [su.audit_source("prosoccer",
                              _summary("prosoccer", rows_with_1x2=15),
                              validation_states={"prosoccer": "unknown"})]
    candidates = su.promotion_candidates(audits)

    assert len(candidates) == 1
    assert candidates[0]["source"] == "prosoccer"
    assert su.B_NOT_SETTLEMENT_VALIDATED in candidates[0]["outstanding_evidence"]
    assert "capture volume is not accuracy" in candidates[0]["note"]


def test_a_source_with_a_parser_gap_is_not_a_promotion_candidate():
    """Fix the parser before discussing promotion."""
    audits = [su.audit_source("prosoccer",
                              _summary("prosoccer", rows_with_1x2=0),
                              validation_states={"prosoccer": "unknown"})]
    assert su.promotion_candidates(audits) == []


def test_a_zero_row_source_is_not_a_promotion_candidate():
    audits = [su.audit_source("prosoccer",
                              _summary("prosoccer", raw_rows=0,
                                       fixture_count=0),
                              validation_states={"prosoccer": "unknown"})]
    assert su.promotion_candidates(audits) == []


def test_a_live_source_is_not_offered_for_promotion():
    audits = [su.audit_source("zulubet", _summary("zulubet",
                                                  rows_with_1x2=10))]
    assert su.promotion_candidates(audits) == []


def test_the_report_states_it_promotes_nothing():
    audits = [su.audit_source("prosoccer",
                              _summary("prosoccer", rows_with_1x2=15),
                              validation_states={"prosoccer": "unknown"})]
    text = "\n".join(su.render_utilisation_lines(
        su.build_utilisation([_summary("prosoccer", rows_with_1x2=15)],
                             validation_states={"prosoccer": "unknown"})))
    assert "review only, never automatic" in text
    assert "no source is promoted, certified or enabled by this report" in text


def test_the_module_cannot_change_a_source_role():
    src = (ROOT / "src" / "edgefactory" / "source_utilisation.py").read_text()
    for forbidden in ("write_text", "REGISTRY[", "cap.tier = ",
                      "append(SourceCapability", "REGISTRY.append"):
        assert forbidden not in src


# --- aggregation -----------------------------------------------------------


def test_a_missing_result_is_not_a_parser_gap():
    """Results arrive after the match; absence is the normal state."""
    audit = su.audit_source("zulubet", _summary("zulubet", rows_with_1x2=10,
                                                already_settled_rows=0))
    assert "results" in sr.get("zulubet").markets
    assert audit["declared_but_missing"] == []


def test_build_utilisation_groups_the_gaps():
    summaries = [
        _summary("zulubet", rows_with_1x2=10, rows_with_price=10),
        _summary("vitibet", rows_with_1x2=0),
    ]
    utilisation = su.build_utilisation(summaries)

    assert utilisation["config_gaps"] == ["zulubet"]
    assert utilisation["parser_gaps"] == ["vitibet"]
    # zulubet supplies its declared 1X2, so it is not a parser gap.
    assert "zulubet" not in utilisation["parser_gaps"]


def test_render_marks_each_market_state_distinctly():
    text = "\n".join(su.render_utilisation_lines(su.build_utilisation([
        _summary("zulubet", rows_with_1x2=10, rows_with_price=10),
        _summary("vitibet", rows_with_1x2=0),
        _summary("betclan", raw_rows=0, fixture_count=0),
    ])))
    assert "UNUSED" in text     # present, undeclared
    assert "MISSING" in text    # declared, absent
    assert "no_rows" in text    # nothing to judge


def test_the_census_cli_emits_the_utilisation_audit():
    src = (ROOT / "scripts" / "source_fixture_census.py").read_text()
    assert "source_utilisation.build_utilisation" in src
    assert "render_utilisation_lines" in src
    # A diagnostic must never break the run it is diagnosing.
    assert "diagnostics never break" in src
