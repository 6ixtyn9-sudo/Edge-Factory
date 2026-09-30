"""Distinguishing a genuinely single-source fixture from an alias failure.

Under-matching gives a thin slate. Over-matching fuses two different
matches and manufactures a false pick, which is much worse. So the bar
for calling a pair safe is deliberately high, and the dangerous
lookalikes — reversed orientation, women's/reserve/youth sides — are
refused outright rather than scored.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from edgefactory import fixture_reconciliation as fr   # noqa: E402

DAY = "2026-10-01"


def _fx(source, home, away, league="Premier League",
        kickoff="2026-10-01T18:00:00+00:00"):
    return {"event_date": DAY, "source": source, "home": home, "away": away,
            "league": league, "kickoff": kickoff}


# --- the dangerous cases, refused outright --------------------------------


def test_a_reversed_fixture_is_never_merged():
    """Merging a reversal silently inverts the selection."""
    result = fr.compare_fixtures(
        _fx("zulubet", "Panama", "New Zealand"),
        _fx("vitibet", "New Zealand", "Panama"))

    assert result["risk"] == fr.BLOCKED_REVERSAL_RISK
    assert fr.R_REVERSAL in result["reasons"]
    assert "invert the selection" in result["detail"]


@pytest.mark.parametrize("a,b", [
    ("Arsenal", "Arsenal Women"),
    ("Chelsea", "Chelsea U21"),
    ("Real Madrid", "Real Madrid Reserves"),
    ("Bayern Munich", "Bayern Munich II"),
    ("Ajax", "Ajax Youth"),
])
def test_a_squad_qualifier_difference_is_never_merged(a, b):
    result = fr.compare_fixtures(_fx("zulubet", a, "Spurs"),
                                 _fx("vitibet", b, "Spurs"))
    assert result["risk"] == fr.BLOCKED_AMBIGUOUS
    assert fr.R_SQUAD_QUALIFIER in result["reasons"]
    assert "different teams" in result["detail"]


def test_matching_qualifiers_on_both_sides_are_not_penalised():
    result = fr.compare_fixtures(
        _fx("zulubet", "Arsenal Women", "Chelsea Women"),
        _fx("vitibet", "Arsenal Women", "Chelsea Women"))
    assert result["risk"] == fr.SAFE_DETERMINISTIC


def test_unrelated_fixtures_are_not_suggested():
    result = fr.compare_fixtures(_fx("zulubet", "Panama", "New Zealand"),
                                 _fx("vitibet", "Brazil", "Argentina"))
    assert result["risk"] == fr.BLOCKED_AMBIGUOUS
    assert fr.R_INSUFFICIENT in result["reasons"]


def test_different_dates_never_merge():
    left = _fx("zulubet", "Panama", "New Zealand")
    right = dict(_fx("vitibet", "Panama", "New Zealand"),
                 event_date="2026-10-02")
    result = fr.compare_fixtures(left, right)
    assert result["risk"] == fr.BLOCKED_AMBIGUOUS


# --- evidence that must support a merge -----------------------------------


def test_identical_names_with_consistent_context_are_deterministic():
    result = fr.compare_fixtures(_fx("zulubet", "Panama", "New Zealand"),
                                 _fx("vitibet", "Panama", "New Zealand"))
    assert result["risk"] == fr.SAFE_DETERMINISTIC
    assert result["sources_agreeing"] == ["vitibet", "zulubet"]


def test_a_league_mismatch_blocks_an_otherwise_identical_pair():
    result = fr.compare_fixtures(
        _fx("zulubet", "Rangers", "Celtic", league="Scottish Premiership"),
        _fx("vitibet", "Rangers", "Celtic", league="Australia NPL"))
    assert result["risk"] == fr.BLOCKED_AMBIGUOUS
    assert fr.R_LEAGUE_MISMATCH in result["reasons"]


def test_a_distant_kickoff_blocks_a_merge():
    result = fr.compare_fixtures(
        _fx("zulubet", "Panama", "New Zealand",
            kickoff="2026-10-01T06:10:00+00:00"),
        _fx("vitibet", "Panama", "New Zealand",
            kickoff="2026-10-01T18:00:00+00:00"))
    assert result["risk"] == fr.BLOCKED_AMBIGUOUS
    assert fr.R_KICKOFF_MISMATCH in result["reasons"]


def test_a_close_kickoff_is_tolerated():
    result = fr.compare_fixtures(
        _fx("zulubet", "Panama", "New Zealand",
            kickoff="2026-10-01T18:00:00+00:00"),
        _fx("vitibet", "Panama", "New Zealand",
            kickoff="2026-10-01T18:15:00+00:00"))
    assert result["risk"] == fr.SAFE_DETERMINISTIC
    assert result["kickoff_delta_minutes"] == 15


def test_a_missing_kickoff_does_not_manufacture_agreement():
    result = fr.compare_fixtures(
        _fx("zulubet", "Manchester United", "Liverpool", kickoff=None),
        _fx("vitibet", "Man United", "Liverpool", kickoff=None))
    assert result["kickoff_delta_minutes"] is None
    assert result["risk"] == fr.NEEDS_REVIEW


# --- name relationships ----------------------------------------------------


def test_an_abbreviated_name_is_suggested_for_review_not_merged():
    result = fr.compare_fixtures(
        _fx("zulubet", "Manchester United", "Liverpool"),
        _fx("vitibet", "Man United", "Liverpool"))
    assert result["risk"] == fr.NEEDS_REVIEW
    assert fr.R_ALIAS_MISSING in result["reasons"]
    assert result["canonical_candidate"]["home"] == "Manchester United"


def test_an_initialism_is_recognised_but_still_reviewed():
    result = fr.compare_fixtures(
        _fx("zulubet", "PSG", "Lyon"),
        _fx("vitibet", "Paris Saint Germain", "Lyon"))
    assert result["risk"] == fr.NEEDS_REVIEW
    assert fr.R_ABBREVIATION in result["reasons"]


def test_ornamental_tokens_do_not_block_a_match():
    result = fr.compare_fixtures(_fx("zulubet", "Arsenal FC", "Chelsea FC"),
                                 _fx("vitibet", "Arsenal", "Chelsea"))
    assert result["risk"] == fr.NEEDS_REVIEW
    assert fr.R_ALIAS_MISSING in result["reasons"]


def test_nothing_is_ever_labelled_deterministic_without_identical_names():
    """Only an exact name pair may be called deterministic."""
    result = fr.compare_fixtures(
        _fx("zulubet", "Manchester United", "Liverpool"),
        _fx("vitibet", "Man United", "Liverpool"))
    assert result["risk"] != fr.SAFE_DETERMINISTIC


# --- aggregation -----------------------------------------------------------


def _group(source, home, away, **over):
    group = {"event_date": DAY, "sources": [source],
             "fixture": f"{home} vs {away}", "home": home, "away": away,
             "league": "Premier League",
             "kickoffs": ["2026-10-01T18:00:00+00:00"],
             "fixture_group_key": f"{home}|{away}"}
    group.update(over)
    return group


def test_only_single_source_groups_are_examined():
    groups = [_group("zulubet", "Panama", "New Zealand"),
              dict(_group("vitibet", "Brazil", "Argentina"),
                   sources=["vitibet", "statarea"])]
    result = fr.build_reconciliation(groups)
    assert result["single_source_fixtures"] == 1


def test_a_probable_alias_failure_is_surfaced():
    groups = [_group("zulubet", "Manchester United", "Liverpool"),
              _group("vitibet", "Man United", "Liverpool")]
    result = fr.build_reconciliation(groups)

    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["risk"] == fr.NEEDS_REVIEW


def test_genuinely_single_source_fixtures_produce_no_suggestions():
    groups = [_group("zulubet", "Panama", "New Zealand"),
              _group("vitibet", "Brazil", "Argentina")]
    result = fr.build_reconciliation(groups)

    assert result["suggestions"] == []
    text = "\n".join(fr.render_reconciliation_lines(result))
    assert "appear genuinely single-source" in text


def test_two_fixtures_from_one_source_are_not_a_match_failure():
    groups = [_group("zulubet", "Arsenal", "Chelsea"),
              _group("zulubet", "Arsenal FC", "Chelsea FC")]
    assert fr.build_reconciliation(groups)["suggestions"] == []


def test_a_reversal_is_reported_rather_than_hidden():
    groups = [_group("zulubet", "Panama", "New Zealand"),
              _group("vitibet", "New Zealand", "Panama")]
    result = fr.build_reconciliation(groups)
    assert result["counts_by_risk"] == {fr.BLOCKED_REVERSAL_RISK: 1}


def test_the_report_states_it_merges_nothing():
    text = "\n".join(fr.render_reconciliation_lines(
        fr.build_reconciliation([_group("zulubet", "A Team", "B Team")])))
    assert "no alias is added and no fixture is merged" in text


def test_the_module_never_writes_an_alias():
    src = (ROOT / "src" / "edgefactory" /
           "fixture_reconciliation.py").read_text()
    for forbidden in ("write_text", "alias_registry", "ALIASES[",
                      "json.dump", "open("):
        assert forbidden not in src


@pytest.mark.parametrize("a,b", [
    ("Man City", "Manchester United"),     # same prefix, different club
    ("Real Madrid", "Real Sociedad"),
    ("Sporting Lisbon", "Sporting Gijon"),
    ("Atletico Madrid", "Athletic Bilbao"),
])
def test_similar_looking_different_clubs_are_not_matched(a, b):
    """The failure mode that would manufacture a false pick."""
    result = fr.compare_fixtures(_fx("zulubet", a, "Spurs"),
                                 _fx("vitibet", b, "Spurs"))
    assert result["risk"] != fr.SAFE_DETERMINISTIC
    assert result["risk"] != fr.NEEDS_REVIEW


def test_token_prefix_requires_a_shared_exact_token():
    result = fr.compare_fixtures(
        _fx("zulubet", "Man United", "Liverpool"),
        _fx("vitibet", "Manchester United", "Liverpool"))
    assert result["risk"] == fr.NEEDS_REVIEW
    assert fr.R_ALIAS_MISSING in result["reasons"]


@pytest.mark.parametrize("mens,womens", [
    ("Vittsjo", "Vittsjo W"),
    ("Vittsjo Gik", "Vittsjo Gik (w)"),
    ("Arsenal", "Arsenal Women"),
    ("Lyon", "Lyon Feminin"),
])
def test_a_womens_side_is_never_matched_to_the_mens_side(mens, womens):
    """The single most dangerous merge these feeds can produce."""
    result = fr.compare_fixtures(_fx("statarea", mens, "Spurs"),
                                 _fx("forebet", womens, "Spurs"))
    assert result["risk"] == fr.BLOCKED_AMBIGUOUS
    assert fr.R_SQUAD_QUALIFIER in result["reasons"]


def test_two_womens_sides_still_match_each_other():
    result = fr.compare_fixtures(
        _fx("statarea", "Vittsjo W", "Kristianstads W"),
        _fx("forebet", "Vittsjo W", "Kristianstads W"))
    assert result["risk"] == fr.SAFE_DETERMINISTIC
