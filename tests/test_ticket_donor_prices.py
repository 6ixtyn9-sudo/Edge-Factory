"""Ticket construction under the promoted-donor price policy (2026-10-03).

The point of these tests is that the builder can now use an approved donor
price WITHOUT ever claiming it came from a named bookmaker, and that none of
the abstention safeguards were removed to make a ticket appear.
"""
from __future__ import annotations

import pytest

import scripts.auto_tickets as at


@pytest.fixture(autouse=True)
def _default_policy(monkeypatch):
    monkeypatch.delenv("EDGE_FACTORY_REQUIRE_PRICE_CORROBORATION", raising=False)
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", "1")
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR", "1")
    yield


DAY = "2026-10-03"


def _row(home, away, **extra):
    out = {
        "date": DAY, "home": home, "away": away, "market": "1x2", "pick": "home",
        "avg_p": 70.0, "odds": 1.80, "bucket": "CAUTION", "quarantine": "none",
        "price_push_eligible": True, "odds_source": "boggio",
        "price_odds_kind": "provider_average",
        "price_donor_role": "average_bookmaker_price_donor",
        "bookmaker": "average_bookie_aggregate",
    }
    out.update(extra)
    return out


def test_two_donor_priced_legs_qualify_under_the_enabled_policy():
    rows = [_row("Alpha", "Beta"), _row("Gamma", "Delta")]
    pool = at.playable_legs(rows, day=DAY, execution_safe=True)
    assert len(pool) == 2


def test_an_ineligible_donor_leg_does_not_qualify():
    rows = [_row("Alpha", "Beta"),
            _row("Gamma", "Delta", price_push_eligible=False)]
    assert len(at.playable_legs(rows, day=DAY, execution_safe=True)) == 1


def test_a_suspect_or_fuzzy_price_still_cannot_build_a_ticket():
    rows = [_row("Alpha", "Beta", price_evidence="SUSPECT_ALIAS_FUZZY"),
            _row("Gamma", "Delta", quarantine="alias_fuzzy")]
    assert at.playable_legs(rows, day=DAY, execution_safe=True) == []


def test_a_malformed_row_cannot_create_a_ticket():
    rows = [_row("Alpha", "Beta", odds=None),
            _row("Gamma", "Delta", odds="not-a-number"),
            _row("Eps", "Zeta", avg_p=None)]
    assert at.playable_legs(rows, day=DAY, execution_safe=True) == []


def test_odds_floor_still_excludes_a_donor_price():
    rows = [_row("Alpha", "Beta", odds=1.01)]
    assert at.playable_legs(rows, day=DAY, execution_safe=True) == []


def test_wrong_day_rows_are_never_borrowed():
    rows = [_row("Alpha", "Beta", date="2026-09-01")]
    assert at.playable_legs(rows, day=DAY, execution_safe=True) == []


# --- disclosure -----------------------------------------------------------

def test_leg_price_disclosure_names_the_donor_type():
    fair = {"row": {"odds_source": "betbetter", "bookmaker": None}}
    avg = {"row": {"odds_source": "boggio", "bookmaker": "average_bookie_aggregate"}}
    book = {"row": {"odds_source": "bzzoiro_odds", "bookmaker": "Bet365"}}
    assert "fair-price donor" in at.leg_price_disclosure(fair)
    assert "not a named-book execution quote" in at.leg_price_disclosure(fair)
    assert "average-bookmaker price donor" in at.leg_price_disclosure(avg)
    assert "not a named-book execution quote" in at.leg_price_disclosure(avg)
    assert "named-book" in at.leg_price_disclosure(book)
    assert "not a named-book execution quote" not in at.leg_price_disclosure(book)


def test_disclosure_prefers_the_stamped_pick_label():
    leg = {"row": {"odds_source": "boggio", "price_disclosure": "custom label"}}
    assert at.leg_price_disclosure(leg) == "custom label"


# --- abstention diagnostics ----------------------------------------------

def test_price_supply_report_separates_supply_from_policy():
    rows = [
        _row("A", "B", odds_source="bzzoiro_odds", price_odds_kind="bookmaker"),
        _row("C", "D", odds_source="boggio", price_odds_kind="provider_average"),
        _row("E", "F", odds_source="betbetter", price_odds_kind="fair"),
        _row("G", "H", odds_source="betbetter", price_odds_kind="fair",
             price_push_eligible=False),
        _row("I", "J", odds=None),
    ]
    block = at.price_supply_report(rows, day=DAY, qualifying=1)
    text = "\n".join(block)
    assert "PRICE SUPPLY:" in text
    assert "named-book execution prices: 1" in text
    assert "average-bookmaker donor prices: 1" in text
    assert "fair-price donor prices: 2" in text
    assert "total donor-priced candidates: 4" in text
    # Fair/model prices remain visible supply but are not directly stakeable
    # unless EDGE_FACTORY_FAIR_PRICE_STAKEABLE=1 is explicitly set.
    assert "execution-safe candidates: 2" in text
    assert "fair_stakeable=off" in text
    assert "qualifying legs: 1" in text
    assert f"required legs: {at.LEGS_PER_ACCA}" in text
    # The active policy is printed with the abstention, never implied.
    assert "PRICE POLICY:" in text


def test_price_supply_report_shows_a_genuinely_empty_board():
    block = at.price_supply_report([], day=DAY, qualifying=0)
    text = "\n".join(block)
    assert "total donor-priced candidates: 0" in text
    assert "qualifying legs: 0" in text


def test_fewer_than_two_qualifying_legs_still_means_no_bet():
    rows = [_row("Alpha", "Beta")]
    pool = at.playable_legs(rows, day=DAY, execution_safe=True)
    assert len(pool) < at.LEGS_PER_ACCA


def test_abstain_with_push_candidate_has_machine_readable_rejection_ledger():
    rows = [_row("Short", "Price", odds=1.16)]
    ledger = at.build_rejection_ledger(
        rows,
        day=DAY,
        default_rule=("stake_ladder_minimum_legs", "one leg cannot form an acca"),
    )
    block = at.price_supply_report(
        rows, day=DAY, qualifying=0, rejection_ledger=ledger,
    )
    text = "\n".join(block)
    assert "PRICE SUPPLY:" in text
    assert "REJECTION LEDGER:" in text
    assert ledger
    assert ledger[0]["rule"] == "min_odds_floor"
    assert '"rule": "min_odds_floor"' in text


def test_2026_10_03_four_named_book_candidates_have_verified_reasons():
    rows = [
        _row("Cuiaba", "Ponte Preta", odds=1.16,
             odds_source="betexplorer_odds", price_odds_kind="bookmaker"),
        _row("Stromsgodset", "Asane", odds=1.15,
             odds_source="betexplorer_odds", price_odds_kind="bookmaker"),
        _row("Iceland", "Bulgaria", odds=1.48,
             odds_source="theoddsapi", price_odds_kind="bookmaker"),
        _row("Croatia", "England", odds=1.78, pick="away",
             odds_source="theoddsapi", price_odds_kind="bookmaker"),
    ]
    ledger = at.build_rejection_ledger(
        rows,
        day=DAY,
        default_rule=(
            "superseded_card_locked",
            "write-once card is already superseded; non-force rerun cannot create replacement legs",
        ),
    )
    reasons = {item["fixture"]: item["rule"] for item in ledger}
    assert reasons == {
        "Cuiaba vs Ponte Preta": "min_odds_floor",
        "Stromsgodset vs Asane": "min_odds_floor",
        "Iceland vs Bulgaria": "superseded_card_locked",
        "Croatia vs England": "superseded_card_locked",
    }
    # The close-window rule belongs to capture scheduling; it is not a ticket
    # eligibility rule and therefore must not be invented as the rejection.
    assert all("close_window" not in item["rule"] for item in ledger)
