"""Shared market/selection normalization for odds donor adapters.

Provider feeds do not agree on the vocabulary used for the same market.  The
pick engine, however, joins on a deliberately small canonical vocabulary.  A
row is only normalized when the mapping is explicit; an unknown token is
returned as a counted reason and must not be guessed into a ticket.

Three outcomes, never two
-------------------------
``mapped``       the provider token has an explicit internal equivalent;
``unsupported``  the token is *recognised* provider vocabulary that this
                 pipeline deliberately does not price (draw-no-bet, double
                 chance, handicaps, correct score, team totals, ...);
``unknown``      the token has never been seen and cannot be classified.

The last two are both **counted misses**.  Neither is ever a silent drop:
``NormalizationFailure`` always carries the raw token so the join-miss
report can print the provider's actual vocabulary without a live call.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class CanonicalMarketSelection:
    market: str
    selection: str
    line: Any = None


@dataclass(frozen=True)
class NormalizationFailure:
    """Why a provider row could not be canonicalised.

    ``reason`` keeps the historic ``"<kind>:<token>"`` rendering so existing
    callers and receipts are unchanged.  ``kind`` and ``raw`` are the
    machine-readable split: ``kind`` selects the miss bucket and ``raw`` is
    the provider token that belongs in the vocabulary census.
    """

    reason: str
    kind: str = "unknown_market"
    raw: str = ""

    @property
    def is_market(self) -> bool:
        return self.kind.endswith("_market")

    @property
    def is_unsupported(self) -> bool:
        return self.kind.startswith("unsupported_")


# Zone suffixes some providers append to an otherwise naive stamp.  Boggio's
# RapidAPI feed publishes ``"2026-10-03 16:00:00 UTC"``; that string *does*
# name its zone, so accepting it is not the banned "assume the capture zone"
# behaviour.  Anything without a zone still fails closed.
_NAMED_UTC_ZONES = ("UTC", "GMT", "Z")


def parse_zoned_timestamp(value: Any) -> datetime | None:
    """Parse an absolute, zone-bearing timestamp. Zone-free values fail closed.

    Accepted shapes (all observed in captured provider payloads):

    * ``2026-10-03T16:00:00+00:00`` / ``...Z`` (ISO 8601, theoddsapi, betbetter)
    * ``2026-10-03T16:00:00.0000000Z`` (betbetter's 7-digit fractional seconds)
    * ``2026-10-03 16:00:00 UTC`` (boggio / football-prediction-api v2)

    A naive string names no zone and returns ``None``: the pipeline must never
    silently stamp a wall clock with the capture timezone.
    """

    text = str(value or "").strip()
    if not text:
        return None
    for suffix in _NAMED_UTC_ZONES:
        if suffix != "Z" and text.upper().endswith(" " + suffix):
            text = text[: -(len(suffix) + 1)].strip() + "+00:00"
            break
    else:
        if text.endswith("Z") or text.endswith("z"):
            text = text[:-1] + "+00:00"
    # Python's fromisoformat accepts at most 6 fractional digits before 3.11
    # and rejects 7 ("...00.0000000+00:00") on every version we support.
    text = re.sub(r"(\.\d{6})\d+", r"\1", text)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def provider_kickoff_date(value: Any, *, declared_zone: str | None = None) -> str | None:
    """Return the provider-declared date for an absolute ISO kickoff.

    The lexical date is intentional: an event at 00:30+02:00 belongs to the
    provider's declared local date even though its UTC instant is on the prior
    day. Missing, malformed, or timezone-free values fail closed.

    ``declared_zone`` is the one sanctioned exception to that fail-closed
    rule: a zone key fixed by the provider's OWN documented payload contract
    (not by us, and not by the capture machine's locale). Only an adapter
    that has such a contract may pass it; see
    :func:`parse_declared_zone_timestamp`.
    """

    parsed = (
        parse_declared_zone_timestamp(value, declared_zone)
        if declared_zone
        else parse_zoned_timestamp(value)
    )
    if parsed is None:
        return None
    return parsed.date().isoformat()


def parse_declared_zone_timestamp(value: Any, zone_key: str | None) -> datetime | None:
    """Parse a naive stamp whose zone is fixed by the provider's contract.

    This is NOT the banned "assume the capture zone" behaviour. The zone must
    come from the provider's own published payload documentation, and only
    the adapter for that provider may pass its key here. Anything the string
    itself names (ISO offset, ``Z``, ``UTC``/``GMT`` suffix) is honoured as
    written via :func:`parse_zoned_timestamp`; a value with no time-of-day
    component, or a value that is not a well-formed naive ISO datetime, still
    fails closed to ``None``.

    Grounding (2026-10-03): football-prediction-api v2 (Boggio) documents
    ``start_date``/``last_update_at`` as ``"2018-12-06T19:00:00"``-shaped
    naive stamps whose wall clock is GMT/BST — "The GMT/BST start date of the
    predicted event", "Day starts at 00:00 London Timezone"
    (developer.boggio-analytics.com). Rounds 1–2 assumed a
    ``"YYYY-MM-DD HH:MM:SS UTC"`` suffix that appears nowhere in the
    provider's documentation, which is why the date repair never moved a row.
    """
    if not zone_key:
        return parse_zoned_timestamp(value)
    zoned = parse_zoned_timestamp(value)
    if zoned is not None:
        return zoned
    text = str(value or "").strip()
    # A date with no time-of-day names no kick-off instant; refuse it rather
    # than stamping midnight in the declared zone.
    if not text or ":" not in text:
        return None
    try:
        naive = datetime.fromisoformat(text)
    except ValueError:
        return None
    if naive.tzinfo is not None:  # pragma: no cover - parse_zoned_timestamp handled it
        return None
    try:
        from zoneinfo import ZoneInfo

        zone = ZoneInfo(str(zone_key))
    except Exception:  # noqa: BLE001 - unknown zone key must fail closed
        return None
    return naive.replace(tzinfo=zone)


def _token(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _compact(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", _token(value))


def _line_from(value: object) -> str | None:
    match = re.search(r"(?<!\d)(\d+(?:[._]\d+)?)(?!\d)", str(value or ""))
    if not match:
        return None
    return match.group(1).replace("_", ".")


# --- provider vocabulary -------------------------------------------------
#
# Every token below was read off a captured payload, a committed capture
# receipt, or the provider's own published payload documentation; never
# invented:
#   * Bet Better (``tests/fixtures/betbetter_brazil_serie_a.json``, the
#     league picks feed it mirrors, and the live keyless board observed
#     2026-10-03): "Head to Head", "Head to Head 3-Way", "Both Teams to
#     Score", "Total Goals", "Draw No Bet", "Spread".
#   * Boggio / football-prediction-api v2: market "classic"; predictions
#     "1" / "X" / "2" and the double-chance "1X" / "12" / "X2".
#   * OddsPAPI: the unified market strings its own writer emits -- "1x2",
#     "btts", "dc", "ou_<line>", "tt_home_<line>", "tt_away_<line>".
#   * The Odds API: "h2h", "totals", "btts".

_1X2_TOKENS = {
    "1x2", "12", "classic", "h2h", "head_to_head", "moneyline", "money_line",
    "match_winner", "full_time_result", "three_way", "3way", "3_way",
    "winner", "match_odds", "match_result", "win_draw_win", "1x2_full_time",
    "full_time_1x2", "to_win_match",
    # Bet Better publishes the three-way variant alongside the two-way one
    # (captured board 2026-10-03, e.g. "Hull City @ Fulham" / "Head to Head
    # 3-Way" / selection "Hull City"). It is the same 1X2 market this
    # pipeline prices; the two-way "Head to Head" token above was already
    # mapped and the three-way spelling was dropping 115 fair-price rows.
    "head_to_head_3_way",
}
_BTTS_TOKENS = {
    "btts", "both_teams_to_score", "both_teams_score", "gg_ng",
    "both_teams_to_score_yes_no", "btts_yes_no",
}
_OU_TOKENS = {
    "ou", "totals", "total", "total_goals", "over_under", "overunder",
    "goals_over_under", "goals", "match_total_goals", "total_goals_over_under",
}

# Recognised provider vocabulary this pipeline deliberately does not price.
# Keeping it explicit is the difference between "we know what this is and we
# do not bet it" and "we have never seen this token".  Both stay counted
# misses; only the bucket differs.
_UNSUPPORTED_MARKET_TOKENS = {
    "draw_no_bet", "dnb", "double_chance", "dc", "asian_handicap",
    "handicap", "european_handicap", "goal_line", "correct_score",
    "exact_goals", "exact_score", "half_time_full_time", "ht_ft",
    "first_half_result", "second_half_result", "halftime_result",
    "1x2_first_half", "clean_sheet", "win_to_nil", "odd_even",
    "odd_or_even", "anytime_goalscorer", "first_goalscorer",
    "last_goalscorer", "to_qualify", "to_advance", "outright",
    "team_total", "team_totals", "player_props", "corners", "cards",
    "both_teams_to_score_and_win", "btts_and_win", "scorecast",
    "winning_margin", "race_to_goals", "method_of_victory",
    # Bet Better's "Spread" (captured board 2026-10-03): point-spread /
    # Asian-handicap shaped, with quarter lines (-1.75, -2.25) and a 0 line
    # the two-way markets render as draw-no-bet. This pipeline prices no
    # handicap market, so it is recognised-but-unpriced vocabulary -- an
    # explicit `unsupported` classification, not an unexamined `unknown`.
    "spread",
}
_UNSUPPORTED_MARKET_PREFIXES = ("tt_home", "tt_away", "team_total")


def market_support(market: object) -> str:
    """``"mapped"`` / ``"unsupported"`` / ``"unknown"`` for a provider market."""
    key, reason = canonical_market(market)
    if key is not None:
        return "mapped"
    return "unsupported" if str(reason or "").startswith("unsupported_") else "unknown"


def canonical_market(market: object, line: object = None) -> tuple[str | None, str | None]:
    """Return ``(market, normalized_line)`` or ``(None, reason)``.

    ``ou`` is rendered as ``ou_<line>`` when a line is explicitly present so
    it remains join-compatible with the existing ``ou_2.5`` pick vocabulary.
    A line-less totals market remains the generic ``ou`` key.

    An explicitly unsupported market returns ``unsupported_market:<token>``;
    a never-seen one returns ``unknown_market:<token>``.  Both are misses.
    """
    raw = _token(market)
    compact = _compact(market)
    # Unsupported is tested first: "Draw No Bet" contains neither an
    # over/under nor a head-to-head token, but "Double Chance" and the team
    # totals must not be swept into 1x2/ou by a substring rule below.
    if raw in _UNSUPPORTED_MARKET_TOKENS or any(
        raw.startswith(prefix) for prefix in _UNSUPPORTED_MARKET_PREFIXES
    ):
        return None, f"unsupported_market:{raw or 'empty'}"
    if raw in _1X2_TOKENS or compact in {"1x2", "12", "headtohead", "headtohead3way", "matchodds"}:
        return "1x2", None
    if raw in _BTTS_TOKENS or "bothteamstoscore" in compact:
        return "btts", None
    if raw in _OU_TOKENS or raw.startswith("ou_") or "overunder" in compact:
        normalized_line = _line_from(line) or _line_from(market)
        return (f"ou_{normalized_line}" if normalized_line else "ou"), normalized_line
    return None, f"unknown_market:{raw or 'empty'}"


# Double chance arrives on the *selection* side too (Boggio's classic market
# answers "1X" when its model will not pick a single side).  It is recognised
# vocabulary with no internal equivalent, so it is an unsupported selection
# rather than an unknown one.
_DOUBLE_CHANCE_SELECTIONS = {
    "1x", "x1", "x2", "2x", "12", "21",
    "homeordraw", "draworhome", "awayordraw", "draworaway", "homeoraway",
    "1or2", "1orx", "xor2",
}


def _team_side(selection: object, home: object, away: object) -> str | None:
    compact = _compact(selection)
    if compact in {"1", "home", "h", "homewin", "team1", "hometeam"}:
        return "home"
    if compact in {"x", "draw", "d", "tie"}:
        return "draw"
    if compact in {"2", "away", "a", "awaywin", "team2", "awayteam"}:
        return "away"
    selected = _compact(selection)
    if selected and selected == _compact(home):
        return "home"
    if selected and selected == _compact(away):
        return "away"
    return None


def canonical_selection(
    market: str,
    selection: object,
    *,
    home: object = None,
    away: object = None,
) -> tuple[str | None, str | None]:
    """Return a canonical selection or an explicit unmappable reason."""
    if market == "1x2":
        value = _team_side(selection, home, away)
        if value:
            return value, None
        if _compact(selection) in _DOUBLE_CHANCE_SELECTIONS:
            return None, f"unsupported_selection:{_token(selection) or 'empty'}"
        return None, f"unknown_selection:{_token(selection) or 'empty'}"
    if market == "btts":
        token = _compact(selection)
        if token in {"yes", "y", "true", "gg", "both"}:
            return "yes", None
        if token in {"no", "n", "false", "ng", "notboth"}:
            return "no", None
        return None, f"unknown_selection:{_token(selection) or 'empty'}"
    if market.startswith("ou"):
        token = _compact(selection)
        if token in {"over", "o", "more", "yes"}:
            return "over", None
        if token in {"under", "u", "less", "no"}:
            return "under", None
        return None, f"unknown_selection:{_token(selection) or 'empty'}"
    return None, f"unsupported_market:{market}"


def _failure(reason: str) -> NormalizationFailure:
    kind, _, raw = str(reason or "").partition(":")
    return NormalizationFailure(reason=reason, kind=kind or "unknown_market", raw=raw)


def canonical_market_selection(
    market: object,
    selection: object,
    *,
    home: object = None,
    away: object = None,
    line: object = None,
) -> tuple[CanonicalMarketSelection | None, NormalizationFailure | None]:
    """Normalize a provider pair without inventing a side or market."""
    market_key, market_reason = canonical_market(market, line)
    if market_key is None:
        return None, _failure(market_reason or "unknown_market:empty")
    selection_key, selection_reason = canonical_selection(
        market_key, selection, home=home, away=away,
    )
    if selection_key is None:
        return None, _failure(selection_reason or "unknown_selection:empty")
    normalized_line = _line_from(line) or _line_from(market) if market_key.startswith("ou_") else line
    return CanonicalMarketSelection(market_key, selection_key, normalized_line), None


def canonicalize_row(row: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Return a copied row with canonical market/selection, or a reason."""
    result, failure = canonical_market_selection(
        row.get("market"), row.get("selection"),
        home=row.get("home"), away=row.get("away"), line=row.get("line"),
    )
    if result is None:
        return None, failure.reason if failure else "unmappable"
    normalized = dict(row)
    normalized["market"] = result.market
    normalized["selection"] = result.selection
    if result.line is not None:
        normalized["line"] = result.line
    normalized["raw_market"] = row.get("market")
    normalized["raw_selection"] = row.get("selection")
    return normalized, None


def miss_bucket(reason: object) -> str:
    """Map a normalization reason onto its stable join-miss bucket name."""
    kind = str(reason or "").partition(":")[0]
    return {
        "unknown_market": "market_unmapped",
        "unsupported_market": "market_unsupported",
        "unknown_selection": "selection_unmapped",
        "unsupported_selection": "selection_unsupported",
    }.get(kind, "market_unmapped")


def miss_vocabulary_token(reason: object) -> str:
    """The provider token behind a miss, for the vocabulary census.

    Counts only -- the token is a market/selection name, never a payload,
    an identifier, or anything credential-bearing.
    """
    kind, _, raw = str(reason or "").partition(":")
    return f"{kind}:{raw}" if raw else str(kind or "unknown")


__all__ = [
    "CanonicalMarketSelection",
    "NormalizationFailure",
    "canonical_market",
    "canonical_selection",
    "canonical_market_selection",
    "canonicalize_row",
    "market_support",
    "miss_bucket",
    "miss_vocabulary_token",
    "parse_declared_zone_timestamp",
    "parse_zoned_timestamp",
    "provider_kickoff_date",
]
