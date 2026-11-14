"""Rescheduled fixtures settle on the match actually played; youth/reserve/women's
sides are never confused with the senior club; disagreeing nearby rows are held."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import audit_recent_picks as aud  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402


def _audit_row(home, away, hs, gs, outcome, origin="warehouse"):
    return {"hs": hs, "gs": gs, "outcome": outcome, "home": home, "away": away, "origin": origin}


def test_audit_settles_a_rescheduled_pick_when_every_row_agrees():
    pick = {"date": "2026-09-21", "home": "Inter Miami", "away": "San Diego",
            "match": "Inter Miami vs San Diego", "pick": "home", "odds": 1.4}
    results = {("2026-09-20", norm_team("Inter Miami CF"), norm_team("San Diego")):
               _audit_row("Inter Miami CF", "San Diego", 2, 2, "draw")}
    status, hit = aud._rescheduled_outcome(pick, "2026-09-21", results)
    assert status == "settled" and hit["outcome"] == "draw"


def test_audit_holds_a_rescheduled_pick_when_nearby_rows_disagree():
    pick = {"date": "2026-09-27", "home": "Isidro Metapán", "away": "Cacahuatique",
            "match": "Isidro Metapán vs Cacahuatique", "pick": "home", "odds": 1.6}
    results = {
        ("2026-09-27", norm_team("A.D. Isidro Meta"), norm_team("Cacahuatique")):
            _audit_row("A.D. Isidro Meta", "Cacahuatique", 2, 0, "home"),
        ("2026-09-26", norm_team("Isidro Metapán"), norm_team("Cacahuatique")):
            _audit_row("Isidro Metapán", "Cacahuatique", 1, 1, "draw"),
    }
    # same-day row is excluded; the only nearby row is a single outcome -> settled
    status, _ = aud._rescheduled_outcome(pick, "2026-09-27", results)
    assert status == "settled"
    results[("2026-09-28", norm_team("Isidro Metapán"), norm_team("Cacahuatique"))] = \
        _audit_row("Isidro Metapán", "Cacahuatique", 2, 0, "home")
    status, hit = aud._rescheduled_outcome(pick, "2026-09-27", results)
    assert status == "conflict" and hit is None


def test_audit_alias_scan_does_not_treat_a_youth_side_as_the_senior_club():
    results_on_date = [{"home": "Slovan Bratislava U19", "away": "Stuttgart U19",
                        "hs": 1, "gs": 0, "outcome": "home"}]
    assert aud.find_fuzzy_result_matches("Slovan Bratislava", "VfB Stuttgart", results_on_date) == []
    assert aud._alias_candidate_results("Slovan Bratislava", "VfB Stuttgart", "2026-10-14",
                                        {"2026-10-14": results_on_date}) == []


def test_grader_alias_conflict_ignores_a_youth_spelling_of_the_same_club():
    entries = {"2026-10-14": [
        {"home": "Slovan Bratislav", "away": "VfB Stuttgart", "outcome": "away"},
        {"home": "Slovan Bratislava U19", "away": "Stuttgart U19", "outcome": "home"}]}
    pick = {"date": "2026-10-14", "home": "Slovan Bratislava", "away": "VfB Stuttgart", "pick": "away"}
    assert at.alias_outcome_conflict(pick, entries) is False


def test_grader_rescheduled_leg_settles_on_agreement_and_holds_on_conflict():
    hk, ak = at._result_write_keys("Inter Miami CF", "San Diego")[0]
    settled = {("2026-09-20", hk, ak): "draw"}
    pick = {"date": "2026-09-21", "home": "Inter Miami CF", "away": "San Diego", "pick": "home"}
    assert at._rescheduled_leg_result("2026-09-21", pick, settled) == "loss"
    settled_conflict = {("2026-09-20", hk, ak): "draw", ("2026-09-22", hk, ak): "home"}
    assert at._rescheduled_leg_result("2026-09-21", pick, settled_conflict) == "conflict"
    assert at._rescheduled_leg_result("2026-09-21", pick, {}) is None


def test_enhancement_leg_prefers_the_staked_day_and_holds_nearby_disagreement():
    leg = {"market": "match_over_25", "pick": "over", "match": "Alpha FC vs Beta FC",
           "fixture_key": ["2026-10-12", "Alpha FC", "Beta FC"]}
    keys_nearby = at._result_write_keys("Alpha FC", "Beta FC")
    hk, ak = keys_nearby[0]
    scores = {("2026-10-11", hk, ak): (3, 0), ("2026-10-12", hk, ak): (1, 0)}
    # the staked day has the score -> it decides, even though a nearby day exists
    assert at.enhancement_leg_result(leg, "2026-10-12", scores) == "loss"
    # no staked-day score: nearby days must agree
    scores2 = {("2026-10-11", hk, ak): (3, 0), ("2026-10-13", hk, ak): (0, 0)}
    assert at.enhancement_leg_result(leg, "2026-10-12", scores2) == "conflict"
