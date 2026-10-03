"""Shared market/selection normalization for odds donor adapters.

Provider feeds do not agree on the vocabulary used for the same market.  The
pick engine, however, joins on a deliberately small canonical vocabulary.  A
row is only normalized when the mapping is explicit; an unknown token is
returned as a counted reason and must not be guessed into a ticket.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CanonicalMarketSelection:
    market: str
    selection: str
    line: Any = None


@dataclass(frozen=True)
class NormalizationFailure:
    reason: str


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


def canonical_market(market: object, line: object = None) -> tuple[str | None, str | None]:
    """Return ``(market, normalized_line)`` or ``(None, reason)``.

    ``ou`` is rendered as ``ou_<line>`` when a line is explicitly present so
    it remains join-compatible with the existing ``ou_2.5`` pick vocabulary.
    A line-less totals market remains the generic ``ou`` key.
    """
    raw = _token(market)
    compact = _compact(market)
    if raw in {"1x2", "12", "classic", "h2h", "head_to_head", "moneyline",
               "match_winner", "full_time_result", "three_way", "3way", "3_way",
               "winner"} or compact in {"1x2", "12", "headtohead"}:
        return "1x2", None
    if raw in {"btts", "both_teams_to_score", "both_teams_score", "gg_ng",
               "both_teams_to_score_yes_no"} or "bothteamstoscore" in compact:
        return "btts", None
    if raw in {"ou", "totals", "total", "total_goals", "over_under", "overunder",
               "goals_over_under", "goals"} or raw.startswith("ou_") or "overunder" in compact:
        normalized_line = _line_from(line) or _line_from(market)
        return (f"ou_{normalized_line}" if normalized_line else "ou"), normalized_line
    return None, f"unknown_market:{raw or 'empty'}"


def _team_side(selection: object, home: object, away: object) -> str | None:
    compact = _compact(selection)
    if compact in {"1", "home", "h", "homewin", "team1"}:
        return "home"
    if compact in {"x", "draw", "d", "tie"}:
        return "draw"
    if compact in {"2", "away", "a", "awaywin", "team2"}:
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
        return (value, None) if value else (None, f"unknown_selection:{_token(selection) or 'empty'}")
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
        return None, NormalizationFailure(market_reason or "unknown_market")
    selection_key, selection_reason = canonical_selection(
        market_key, selection, home=home, away=away,
    )
    if selection_key is None:
        return None, NormalizationFailure(selection_reason or "unknown_selection")
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


__all__ = [
    "CanonicalMarketSelection",
    "NormalizationFailure",
    "canonical_market",
    "canonical_selection",
    "canonical_market_selection",
    "canonicalize_row",
]
