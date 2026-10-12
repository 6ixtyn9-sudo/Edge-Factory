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


def test_a_line_on_a_1x2_token_is_refused_never_folded_in():
    """A lined 1x2 token is a different market wearing the 1x2 name.

    `canonical_market` used to ignore `line` for every non-ou market, so a
    handicap/draw-no-bet price labelled with a 1x2 token canonicalised to a
    LINE-LESS 1x2 row and could win the same-side maximum-odds tie-break -
    the 2026-10-11 phantom class (Viking vs Bayern: an away quote of 2.06
    printed against a real 1.088, and the same build shipped Galatasaray and
    Arsenal). The line is the provider's own statement that this is not the
    full-time three-way market, so it is recognised vocabulary refused
    loudly, not silently stripped.
    """
    result, failure = canonical_market_selection(
        "1x2", "away", home="Viking", away="Bayern Munich", line=-2.5)
    assert result is None
    assert failure is not None and failure.reason == "unsupported_market:1x2_with_line"

    # A ZERO line is a real marker too: Pinnacle renders draw-no-bet as a zero
    # handicap, and `0 or ""` must not make it look line-less.
    for token in ("1x2", "money_line", "h2h", "Head to Head 3-Way"):
        assert canonical_market_selection(token, "away", line=0)[0] is None
        assert canonical_market_selection(token, "away", line="0")[0] is None

    # The line-less market itself is untouched (this is the whole archive).
    for blank in (None, "", "none", "null"):
        result, failure = canonical_market_selection(
            "money_line", "away", home="Viking", away="Bayern Munich", line=blank)
        assert failure is None
        assert (result.market, result.selection) == ("1x2", "away")

    # And a canonical OU row still carries its line, where the line IS identity.
    result, failure = canonical_market_selection("totals", "over", line=2.5)
    assert failure is None
    assert (result.market, result.selection, result.line) == ("ou_2.5", "over", "2.5")
