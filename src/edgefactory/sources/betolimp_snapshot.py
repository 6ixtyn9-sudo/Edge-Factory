"""Offline BetOlimp reader-excerpt diagnostic; NOT a native HTML/live adapter.

Consumes deliberately labelled saved page-reader transcriptions only. No HTTP,
credentials, ledger writer, production registration or admission switch exists.
Reuses the existing market normalizer, timestamp parser and identity guards.
A readable price is an observation, never a vote or an executable quote.
"""
from __future__ import annotations

import hashlib
import re
from datetime import date
from decimal import Decimal
from urllib.parse import urlsplit

from edgefactory.identity import (
    canonical_league_key,
    source_team_key,
    squad_marker_mismatch,
)
from edgefactory.odds_normalization import canonicalize_row, parse_zoned_timestamp

MAX_BYTES = 128 * 1024
PRICE = r"(?:0|[1-9]\d{0,3})\.\d{1,3}"
_EVENT_PATH = re.compile(r"/sports/soccer-betting/([a-z0-9-]+)/([a-z0-9-]+)-(\d{1,12})")
_LEAGUE_PATH = re.compile(r"/sports/soccer-betting/([a-z0-9-]+)")
HOLDS = (
    "reader_transcription_not_native_response",
    "collection_permission_unresolved",
    "odds_view_profile_unverified",
    "absolute_kickoff_unverified",
    "quote_update_time_unverified",
    "fixture_not_independently_corroborated",
    "production_admission_not_implemented",
)


def _url(value: str, *, event: bool) -> re.Match:
    if not isinstance(value, str) or any(c.isspace() for c in value):
        raise ValueError("invalid source URL")
    p = urlsplit(value)
    if (p.scheme != "https" or p.netloc != "betolimp.co.za"
            or p.query or p.fragment or "%" in p.path):
        raise ValueError("not an exact plain BetOlimp source URL")
    match = (_EVENT_PATH if event else _LEAGUE_PATH).fullmatch(p.path)
    if match is None:
        raise ValueError("wrong source path")
    return match


def validate_event_url(value: str) -> str:
    """Validate an exact public event URL for the manual probe; never fetch it."""
    _url(value, event=True)
    return value


def _quote(market: str, selection: str, price: str, *, line=None) -> dict:
    # No +1 heuristic. Decimal-like display is NOT a verified odds-view profile.
    if not re.fullmatch(PRICE, price) or not Decimal(price).is_finite() or Decimal(price) <= 1:
        raise ValueError("invalid displayed price")
    row, reason = canonicalize_row({
        "market": market, "selection": selection, "line": line,
        "display_price": price,
    })
    if row is None:
        raise ValueError(reason)
    return row


def _event(lines: list[str], url: str, match: re.Match) -> dict:
    if len(lines) < 8 or not re.fullmatch(r"#\d+", lines[1]):
        raise ValueError("event excerpt must start at title and coupon ID")
    home, away = lines[2], lines[5]
    if (not source_team_key(home) or not source_team_key(away)
            or source_team_key(home) == source_team_key(away)
            or lines[0] != f"{home} - {away}"
            or not re.fullmatch(r"\d{2} [A-Z][a-z]{2}", lines[3])
            or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", lines[4])
            or lines[6] != "Full Time Result"):
        raise ValueError("ambiguous event identity/header")
    observed = []
    seen = set()
    for i in range(6, len(lines)):
        heading = lines[i]
        if heading not in {"Full Time Result", "Total Goals", "Teams To Score"}:
            continue
        if heading in seen or i + 1 >= len(lines):
            raise ValueError("duplicate or incomplete market block")
        seen.add(heading)
        if heading == "Full Time Result":
            m = re.fullmatch(rf"{re.escape(home)}({PRICE})Draw({PRICE}){re.escape(away)}({PRICE})",
                             lines[i + 1])
            if not m:
                raise ValueError("incomplete full-time three-way prices")
            observed.extend(_quote(heading, side, price)
                            for side, price in zip(("home", "draw", "away"), m.groups()))
        elif heading == "Total Goals":
            m = re.fullmatch(rf"Total \((\d+(?:\.\d+)?)\) under({PRICE})"
                             rf"Total \(\1\) over({PRICE})", lines[i + 1])
            if not m or m[1] not in {"2.5", "3.5"}:
                raise ValueError("unverified main total line or incomplete pair")
            observed.extend(_quote(heading, side, price, line=m[1])
                            for side, price in zip(("under", "over"), m.groups()[1:]))
        else:
            # Team scoring Yes/No is not BTTS. Require the exact whole line,
            # inside this section, before the next non-selection heading.
            candidates = []
            for text in lines[i + 1:]:
                if text.startswith((f"{home} to score:", f"{away} to score:")):
                    continue
                m = re.fullmatch(rf"Both teams to score: yes({PRICE})"
                                 rf"Both teams to score: no({PRICE})", text)
                if m:
                    candidates.append(m)
                else:
                    break
            if len(candidates) != 1:
                raise ValueError("missing or ambiguous BTTS pair")
            observed.extend(_quote("Both teams to score", side, price)
                            for side, price in zip(("yes", "no"), candidates[0].groups()))
    return {"event_id": match[3], "coupon_id": lines[1][1:], "home": home, "away": away,
            "league": None, "raw_competition_slug": match[1],
            "kickoff_display": f"{lines[3]} {lines[4]}", "source_url": url,
            "identity_evidence": "event_header_ordered_teams_only",
            "observations": observed}


def _league(lines: list[str], url: str) -> dict:
    # Excerpt must begin at the actual league table, NOT at a shared carousel.
    m = re.fullmatch(r"\[([^\[\]]+)\]\(([^)]+)\)", lines[0]) if lines else None
    header = ["1", "X", "2", "Handicap 1", "Handicap 2", "Total", "U", "O", "1"]
    if not m or m[2] != url or lines[1:10] != header or len(lines) != 25:
        raise ValueError("expected a single exact league-row excerpt")
    link = re.fullmatch(r"\[([^\[\]]+)\]\(([^)]+)\)", lines[10])
    if not link:
        raise ValueError("missing fixture link")
    event_match = _url(link[2], event=True)
    if urlsplit(link[2]).path.rsplit("/", 1)[0] != urlsplit(url).path:
        raise ValueError("fixture linked from wrong competition")
    if (not re.fullmatch(r"\d{2} [A-Z][a-z]{2} (?:[01]\d|2[0-3]):[0-5]\d", lines[11])
            or not re.fullmatch(r"#\d+", lines[12]) or lines[23] != "+"
            or not lines[24].isdigit()):
        raise ValueError("invalid fixture date/coupon/row boundary")
    # Handicap columns are retained as unparsed diagnostics, never mislabeled
    # as match odds. Full exact row length makes column shifts fail closed.
    if not all(re.fullmatch(r"-?\d+(?:\.\d+)?", x) for x in lines[16:23]):
        raise ValueError("invalid handicap/total columns")
    if not re.fullmatch(r"\d{1,2}\.5", lines[20]):
        raise ValueError("unverified league total line")
    # Validate even the unparsed handicap prices; never shift columns.
    for price in (lines[17], lines[19]):
        _quote("1x2", "home", price)
    observed = [_quote("1x2", side, price)
                for side, price in zip(("home", "draw", "away"), lines[13:16])]
    observed.extend(_quote("Total Goals", side, price, line=lines[20])
                    for side, price in zip(("under", "over"), lines[21:23]))
    return {"event_id": event_match[3], "coupon_id": lines[12][1:], "home": None,
            "away": None, "league": m[1], "display_label": link[1],
            "kickoff_display": lines[11], "source_url": link[2],
            "identity_evidence": "concatenated_label_not_split_into_teams",
            "raw_other_columns": lines[16:23], "observations": observed}


def _event_breadcrumb(line: str, event_url: str) -> str:
    """Read a displayed league label, never invent an alias from a URL slug.

    This validates the exact observed three-link reader layout, not native DOM
    provenance or real-world fixture identity. No link is ever requested.
    """
    base = "https://betolimp.co.za/sports/soccer-betting"
    links = re.findall(
        r'\[([^\[\]]+)\]\((https://betolimp\.co\.za/sports/soccer-betting(?:/[a-z0-9-]+)?) "([^"\n]+)"\)',
        line,
    )
    if (len(links) != 3
            or line != " ".join(f'[{label}]({url} "{title}")' for label, url, title in links)
            or any(label != title for label, _, title in links)
            or links[0] != ("Soccer", base, "Soccer")
            or not re.fullmatch(re.escape(base) + r"/[a-z0-9-]+", links[1][1])
            or links[2][1] != event_url.rsplit("/", 1)[0]):
        raise ValueError("unverified or conflicting competition breadcrumb")
    return links[2][0]


def parse_saved_excerpt(envelope: dict) -> dict:
    """Parse an explicitly labelled offline transcription; always inadmissible.

    The digest identifies the transcription only, NOT raw-origin bytes.
    Unknown views, HTML and an arbitrary web page are not supported inputs.
    """
    if not isinstance(envelope, dict) or envelope.get("evidence_kind") != "reader_transcription":
        raise ValueError("only labelled reader transcriptions are supported")
    profile = envelope.get("profile")
    if profile not in {"betolimp_event_reader_v1", "betolimp_league_reader_v1"}:
        raise ValueError("unsupported excerpt profile")
    text = envelope.get("text")
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("invalid or oversized excerpt")
    observed_on = envelope.get("observed_on")
    if not isinstance(observed_on, str) or date.fromisoformat(observed_on).isoformat() != observed_on:
        raise ValueError("observation date must be ISO date")
    match = _url(envelope.get("source_url"), event=profile == "betolimp_event_reader_v1")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if profile == "betolimp_event_reader_v1":
        league = None
        if lines and lines[0].startswith('[Soccer]('):
            league = _event_breadcrumb(lines[0], envelope["source_url"])
            lines = lines[1:]
        result = _event(lines, envelope["source_url"], match)
        result["league"] = league
        result["league_evidence"] = "reader_breadcrumb" if league else "unverified"
    else:
        result = _league(lines, envelope["source_url"])
    return {**result, "source": "betolimp_reader_diagnostic", "bookmaker": "BetOlimp",
            "evidence_kind": "reader_transcription", "observed_on": observed_on,
            "transcription_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "status": "diagnostic_only", "admitted_rows": 0, "kickoff_utc": None,
            "quoted_at": None, "hold_reasons": list(HOLDS)}


def compare_card_identity(card: dict, observation: dict) -> dict:
    """Strict diagnostics only; never infer zone, league alias, date or teams.

    Even a perfect match cannot admit a row from this offline-only source.
    """
    teams = all(
        source_team_key(card.get(side))
        and source_team_key(observation.get(side))
        and source_team_key(card.get(side)) == source_team_key(observation.get(side))
        and not squad_marker_mismatch(card.get(side), observation.get(side))
        for side in ("home", "away")
    )
    league = bool(card.get("league") and observation.get("league")) and (
        canonical_league_key(card["league"]) == canonical_league_key(observation["league"]))
    source_time = parse_zoned_timestamp(observation.get("kickoff_utc"))
    card_time = parse_zoned_timestamp(card.get("kickoff_utc"))
    time_matches = source_time is not None and card_time is not None and source_time == card_time
    return {"ordered_teams_match": bool(teams), "league_match": bool(league),
            "absolute_kickoff_match": time_matches, "admitted": False}
