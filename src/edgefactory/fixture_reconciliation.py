"""Which unmatched fixtures are probably the same match?

"Seen by one source only" is sometimes true and sometimes an alias
failure wearing a disguise. Under-matching produces a thin slate;
over-matching fuses two different matches and manufactures a false pick,
which is far worse. So this audit suggests and explains, and merges
nothing on its own authority.

A suggestion is only ever ``safe_deterministic`` when the evidence is
overwhelming: same date, same orientation, compatible league, compatible
kickoff, and a name relationship that is a containment or abbreviation
rather than a guess. Anything touching women's, reserve, youth or B-team
markers is refused outright, because those are exactly the pairs that
look similar and are not the same fixture.

No fuzzy distance threshold is used to authorise a merge. Nothing here
edits an alias registry.
"""

from __future__ import annotations

import re
from itertools import combinations
from typing import Any, Iterable

# Risk labels ---------------------------------------------------------------
SAFE_DETERMINISTIC = "safe_deterministic"
NEEDS_REVIEW = "needs_review"
BLOCKED_REVERSAL_RISK = "blocked_reversal_risk"
BLOCKED_AMBIGUOUS = "blocked_ambiguous"

# Reasons a pair did not merge ---------------------------------------------
R_ALIAS_MISSING = "alias_missing"
R_LEAGUE_MISMATCH = "league_mismatch"
R_KICKOFF_MISMATCH = "kickoff_mismatch"
R_REVERSAL = "home_away_reversal_risk"
R_SQUAD_QUALIFIER = "squad_qualifier_mismatch"
R_ABBREVIATION = "source_name_abbreviation"
R_INSUFFICIENT = "insufficient_evidence_to_merge"

# Qualifiers that change which team a name refers to. A mismatch on any
# of these is disqualifying, never a stylistic difference.
SQUAD_QUALIFIERS = (
    # "w" and "(w)" are the most common women's markers in these feeds,
    # and are exactly the difference that must never be normalised away.
    "w", "wom", "women", "womens", "ladies", "feminine", "feminin",
    "frauen", "femenino", "femminile", "dames",
    "u14", "u15", "u16", "u17", "u18", "u19", "u20", "u21", "u23",
    "reserve", "reserves", "ii", "b", "youth", "academy", "juniors",
)

# Ornamental tokens that genuinely do not change identity.
_NOISE = ("fc", "afc", "cf", "sc", "ac", "club", "cd", "sv", "fk", "if",
          "the", "de", "1", "calcio")

_MAX_KICKOFF_DELTA_MINUTES = 30


def normalise(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(name or "").lower())


def tokens(name: str) -> list[str]:
    raw = re.split(r"[^a-z0-9]+", str(name or "").lower())
    return [t for t in raw if t and t not in _NOISE]


def squad_qualifiers(name: str) -> set[str]:
    """Qualifiers present in a name, e.g. women / U21 / reserves."""
    found = {t for t in re.split(r"[^a-z0-9]+", str(name or "").lower())
             if t in SQUAD_QUALIFIERS}
    # A trailing standalone "II"/"B" is a reserve marker.
    trailing = re.search(r"\b(ii|b)\s*$", str(name or "").strip().lower())
    if trailing:
        found.add(trailing.group(1))
    return found


def _name_relationship(a: str, b: str) -> str | None:
    """How two names relate, or None when the relationship is not safe."""
    na, nb = normalise(a), normalise(b)
    if not na or not nb:
        return None
    if na == nb:
        return "identical"
    if na.startswith(nb) or nb.startswith(na):
        return "containment"
    ta, tb = set(tokens(a)), set(tokens(b))
    if ta and tb and (ta <= tb or tb <= ta):
        return "token_subset"
    # Initialism: "psg" against "paris saint germain".
    for short, long in ((na, tokens(b)), (nb, tokens(a))):
        if len(long) >= 2 and short == "".join(t[0] for t in long):
            return "abbreviation"
    # Token-by-token truncation: "man united" against "manchester united".
    # Every token must align in order and each must be a prefix of its
    # counterpart, with at least one exact token in common, so "man city"
    # never aligns with "manchester united".
    la, lb = tokens(a), tokens(b)
    if len(la) == len(lb) and la and any(x == y for x, y in zip(la, lb)):
        if all(x.startswith(y) or y.startswith(x) for x, y in zip(la, lb)):
            return "token_prefix"
    return None


def _kickoff_delta_minutes(a: str | None, b: str | None) -> float | None:
    from datetime import datetime
    if not a or not b:
        return None
    try:
        da = datetime.fromisoformat(str(a))
        db = datetime.fromisoformat(str(b))
    except ValueError:
        return None
    if (da.tzinfo is None) != (db.tzinfo is None):
        return None
    return abs((da - db).total_seconds()) / 60.0


def compare_fixtures(left: dict, right: dict) -> dict[str, Any]:
    """Assess one unmatched pair. Suggests; never merges."""
    suggestion: dict[str, Any] = {
        "event_date": left.get("event_date"),
        "left": {"source": left.get("source"), "home": left.get("home"),
                 "away": left.get("away"), "league": left.get("league"),
                 "kickoff": left.get("kickoff")},
        "right": {"source": right.get("source"), "home": right.get("home"),
                  "away": right.get("away"), "league": right.get("league"),
                  "kickoff": right.get("kickoff")},
        "reasons": [],
    }
    reasons: list[str] = []

    if str(left.get("event_date")) != str(right.get("event_date")):
        suggestion["risk"] = BLOCKED_AMBIGUOUS
        suggestion["reasons"] = ["different event dates"]
        return suggestion

    # Orientation first. A reversed pairing is the single most dangerous
    # merge, because it silently inverts the selection.
    straight = (_name_relationship(left.get("home"), right.get("home")),
                _name_relationship(left.get("away"), right.get("away")))
    crossed = (_name_relationship(left.get("home"), right.get("away")),
               _name_relationship(left.get("away"), right.get("home")))

    if all(crossed) and not all(straight):
        suggestion["risk"] = BLOCKED_REVERSAL_RISK
        suggestion["reasons"] = [R_REVERSAL]
        suggestion["detail"] = (
            "the teams match only when home and away are swapped; merging "
            "would invert the selection")
        return suggestion

    if not all(straight):
        suggestion["risk"] = BLOCKED_AMBIGUOUS
        suggestion["reasons"] = [R_INSUFFICIENT]
        suggestion["detail"] = "the team names have no safe relationship"
        return suggestion

    # Squad qualifiers must agree exactly on both sides.
    for side in ("home", "away"):
        if squad_qualifiers(left.get(side)) != squad_qualifiers(
                right.get(side)):
            suggestion["risk"] = BLOCKED_AMBIGUOUS
            suggestion["reasons"] = [R_SQUAD_QUALIFIER]
            suggestion["detail"] = (
                f"the {side} names differ by a squad qualifier (women, "
                f"reserve, youth or age group); these are different teams")
            return suggestion

    if "abbreviation" in straight:
        reasons.append(R_ABBREVIATION)
    if any(r in ("containment", "token_subset", "token_prefix")
           for r in straight):
        reasons.append(R_ALIAS_MISSING)

    league_ok = True
    ll, rl = normalise(left.get("league")), normalise(right.get("league"))
    if ll and rl and ll != rl:
        if not (ll.startswith(rl) or rl.startswith(ll)):
            league_ok = False
            reasons.append(R_LEAGUE_MISMATCH)

    kickoff_ok = True
    delta = _kickoff_delta_minutes(left.get("kickoff"), right.get("kickoff"))
    suggestion["kickoff_delta_minutes"] = delta
    if delta is not None and delta > _MAX_KICKOFF_DELTA_MINUTES:
        kickoff_ok = False
        reasons.append(R_KICKOFF_MISMATCH)

    # Only an exact-name pair with nothing contradicting it is called
    # deterministic. Everything else is a suggestion for a human.
    if straight == ("identical", "identical") and league_ok and kickoff_ok:
        suggestion["risk"] = SAFE_DETERMINISTIC
    elif league_ok and kickoff_ok:
        suggestion["risk"] = NEEDS_REVIEW
    else:
        suggestion["risk"] = BLOCKED_AMBIGUOUS

    suggestion["reasons"] = reasons or [R_INSUFFICIENT]
    suggestion["canonical_candidate"] = {
        "home": max((left.get("home") or "", right.get("home") or ""),
                    key=len),
        "away": max((left.get("away") or "", right.get("away") or ""),
                    key=len),
    }
    suggestion["sources_agreeing"] = sorted(
        {str(left.get("source")), str(right.get("source"))})
    return suggestion


def _singles(groups: Iterable[dict]) -> list[dict]:
    out = []
    for group in groups:
        sources = list(group.get("sources") or [])
        if len(set(sources)) != 1:
            continue
        out.append({
            "event_date": group.get("event_date"),
            "source": sources[0],
            "home": group.get("home") or (group.get("fixture") or " vs ")
                    .split(" vs ")[0],
            "away": group.get("away") or (group.get("fixture") or " vs ")
                    .split(" vs ")[-1],
            "league": group.get("league"),
            "kickoff": (group.get("kickoffs") or [None])[0],
            "fixture_group_key": group.get("fixture_group_key"),
        })
    return out


def build_reconciliation(fixture_groups: list[dict]) -> dict[str, Any]:
    """Look for probable same-fixture pairs among single-source groups."""
    singles = _singles(fixture_groups)
    suggestions = []
    for left, right in combinations(singles, 2):
        if left["source"] == right["source"]:
            # One source listing two fixtures is not a match failure.
            continue
        result = compare_fixtures(left, right)
        if result["risk"] == BLOCKED_AMBIGUOUS and \
                R_INSUFFICIENT in result.get("reasons", []):
            continue          # unrelated fixtures: not worth reporting
        suggestions.append(result)

    by_risk: dict[str, int] = {}
    for suggestion in suggestions:
        by_risk[suggestion["risk"]] = by_risk.get(suggestion["risk"], 0) + 1

    return {
        "single_source_fixtures": len(singles),
        "suggestions": suggestions,
        "counts_by_risk": by_risk,
        "truly_single_source": len(singles) - len({
            id(s) for suggestion in suggestions for s in ()}),
        "note": ("suggestions only; no alias is added and no fixture is "
                 "merged by this report"),
    }


def render_reconciliation_lines(reconciliation: dict) -> list[str]:
    out = ["FIXTURE IDENTITY RECONCILIATION",
           f"  single-source fixtures examined: "
           f"{reconciliation['single_source_fixtures']}"]
    suggestions = reconciliation["suggestions"]
    if not suggestions:
        out.append("  no probable same-fixture pairs found; the "
                   "single-source fixtures appear genuinely single-source")
        out.append(f"  {reconciliation['note']}")
        return out

    for risk, count in sorted(reconciliation["counts_by_risk"].items()):
        out.append(f"  {risk}: {count}")
    for suggestion in suggestions:
        left, right = suggestion["left"], suggestion["right"]
        out.append(f"  [{suggestion['risk']}] {suggestion['event_date']}")
        out.append(f"    {left['source']}: \"{left['home']}\" vs "
                   f"\"{left['away']}\" | league={left['league'] or '-'} | "
                   f"ko={left['kickoff'] or '-'}")
        out.append(f"    {right['source']}: \"{right['home']}\" vs "
                   f"\"{right['away']}\" | league={right['league'] or '-'} | "
                   f"ko={right['kickoff'] or '-'}")
        if suggestion.get("kickoff_delta_minutes") is not None:
            out.append(f"    kickoff delta: "
                       f"{suggestion['kickoff_delta_minutes']:.0f} min")
        out.append(f"    reasons: {', '.join(suggestion['reasons'])}")
        if suggestion.get("detail"):
            out.append(f"    detail: {suggestion['detail']}")
    out.append(f"  {reconciliation['note']}")
    return out
