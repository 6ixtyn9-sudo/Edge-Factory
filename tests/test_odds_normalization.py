"""Raw-provider vocabulary must join only through the shared canonicalizer."""
from __future__ import annotations

from edgefactory.odds_normalization import canonical_market_selection, canonicalize_row


def test_raw_1x2_tokens_and_team_names_are_canonical():
    result, failure = canonical_market_selection(
        "classic", "1", home="Home FC", away="Away FC"
    )
    assert failure is None
    assert (result.market, result.selection) == ("1x2", "home")

    result, failure = canonical_market_selection(
        "match winner", "Away FC", home="Home FC", away="Away FC"
    )
    assert failure is None
    assert (result.market, result.selection) == ("1x2", "away")

    # Bet Better's captured provider vocabulary; this must not be replaced by
    # a pre-canonicalised test fixture.
    result, failure = canonical_market_selection(
        "Head to Head", "Away FC", home="Home FC", away="Away FC"
    )
    assert failure is None
    assert (result.market, result.selection) == ("1x2", "away")


def test_raw_btts_and_totals_tokens_are_canonical():
    result, failure = canonical_market_selection("Both Teams to Score", "Yes")
    assert failure is None
    assert (result.market, result.selection) == ("btts", "yes")

    result, failure = canonical_market_selection("Over/Under", "Under", line="2.5")
    assert failure is None
    assert (result.market, result.selection) == ("ou_2.5", "under")


def test_unmappable_tokens_fail_closed_with_a_reason():
    # "Draw No Bet" is RECOGNISED Bet Better vocabulary the pipeline does not
    # price: an explicit unsupported classification, still a counted miss.
    result, failure = canonical_market_selection("Draw No Bet", "Home FC", home="Home FC", away="Away FC")
    assert result is None
    assert failure is not None
    assert failure.reason == "unsupported_market:draw_no_bet"
    assert failure.kind == "unsupported_market"
    assert failure.raw == "draw_no_bet"

    # A token nobody has ever seen stays "unknown", a different bucket.
    result, failure = canonical_market_selection("Provider Mystery", "Home FC")
    assert result is None
    assert failure.reason.startswith("unknown_market:")

    row, reason = canonicalize_row({
        "date": "2026-10-03", "home": "A", "away": "B",
        "market": "classic", "selection": "mystery side", "odds": 2.0,
    })
    assert row is None
    assert reason == "unknown_selection:mystery_side"
