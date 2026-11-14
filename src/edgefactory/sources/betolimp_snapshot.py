"""BetOlimp display observations and opt-in native-layout candidate decoding.

Reader transcriptions and native bytes have separate entry points/provenance.
No HTTP, credentials, ledger writer, production registration or admission switch.
The native layout is synthetic-tested, not verified against an origin capture.
Reuses existing market vocabulary, timestamp parsing and identity guards.
A readable price is an observation, never a vote or an executable quote.
"""
from __future__ import annotations

import hashlib
import re
from datetime import date
from decimal import Decimal
from html.parser import HTMLParser
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


def _event(lines: list[str], url: str, match: re.Match, *, expanded: bool = False) -> dict:
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
    unsupported = []
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
            if not m or (not expanded and m[1] not in {"2.5", "3.5"}):
                raise ValueError("unverified main total line or incomplete pair")
            if not 0 < Decimal(m[1]) <= Decimal("99.5"):
                raise ValueError("invalid main total line")
            quotes = [_quote(heading, side, price, line=m[1])
                      for side, price in zip(("under", "over"), m.groups()[1:])]
            if expanded and Decimal(m[1]) % 1 != Decimal("0.5"):
                unsupported.extend({**q, "reason": "non_half_line_settlement_not_supported"} for q in quotes)
            else:
                observed.extend(quotes)
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
    if expanded:
        observed, extra_unsupported = _expanded_markets(lines, home, away, observed)
        unsupported.extend(extra_unsupported)
    return {"event_id": match[3], "coupon_id": lines[1][1:], "home": home, "away": away,
            "league": None, "raw_competition_slug": match[1],
            "kickoff_display": f"{lines[3]} {lines[4]}", "source_url": url,
            "identity_evidence": "event_header_ordered_teams_only",
            "observations": observed,
            **({"unsupported_observations": unsupported} if expanded else {})}


def _expanded_markets(lines: list[str], home: str, away: str, primary: list[dict]) -> tuple[list, list]:
    """Observed v2 full-time vocabulary only; integer lines remain held.

    Explicit pairs must consume their ENTIRE section line, so partial prices,
    promo/half/handicap text and another team's totals cannot leak through.
    The shared normalizer deliberately refuses DC/team-total votes: these
    source-specific PRICE observations use the existing price-board vocabulary
    without changing that prediction/vote contract.
    """
    observations = list(primary)
    unsupported = []
    headings = {"Double Chance", "Alternative Total Goals", "Team Total"}
    seen = set()
    for i, heading in enumerate(lines):
        if heading not in headings:
            continue
        if heading in seen or i + 1 >= len(lines):
            raise ValueError("duplicate or incomplete expanded market block")
        seen.add(heading)
        if heading == "Double Chance":
            pattern = (rf"{re.escape(home)} or Draw({PRICE})No draw({PRICE})"
                       rf"Draw or {re.escape(away)}({PRICE})")
            pair = re.fullmatch(pattern, lines[i + 1])
            if not pair:
                raise ValueError("incomplete full-time double-chance board")
            for side, price in zip(("1x", "12", "x2"), pair.groups()):
                quote = _quote("1x2", "home", price)
                observations.append({**quote, "market": "dc", "selection": side,
                                     "raw_market": heading, "raw_selection": side})
            continue
        text_lines = [lines[i + 1]]
        if heading == "Team Total":
            # Only the two observed ordered-team lines belong to this block.
            if i + 2 >= len(lines):
                raise ValueError("missing away team-total line")
            text_lines.append(lines[i + 2])
        for index, text in enumerate(text_lines):
            team = (home, away)[index] if heading == "Team Total" else "Total"
            prefix = re.escape(team)
            pattern = re.compile(rf"{prefix} \((\d+(?:\.\d+)?)\) under({PRICE})"
                                 rf"{prefix} \(\1\) over({PRICE})")
            offset, seen_lines = 0, set()
            for pair in pattern.finditer(text):
                if pair.start() != offset:
                    raise ValueError("unconsumed total-market content")
                offset = pair.end()
                line = Decimal(pair[1])
                if not 0 < line <= Decimal("99.5") or line in seen_lines:
                    raise ValueError("invalid or duplicate total line")
                seen_lines.add(line)
                for side, price in zip(("under", "over"), pair.groups()[1:]):
                    quote = _quote("Total Goals", side, price, line=pair[1])
                    if heading == "Team Total":
                        quote["market"] = f"tt_{('home', 'away')[index]}_{quote['line']}"
                    quote["raw_market"] = heading
                    if line % 1 != Decimal("0.5"):
                        unsupported.append({**quote, "reason": "non_half_line_settlement_not_supported"})
                    else:
                        observations.append(quote)
            if not offset or offset != len(text):
                raise ValueError("incomplete or unsupported total-market pair")
    keys = [(q["market"], q["selection"]) for q in observations]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate or conflicting market selection")
    return observations, unsupported


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
    if profile not in {"betolimp_event_reader_v1", "betolimp_event_reader_v2", "betolimp_league_reader_v1"}:
        raise ValueError("unsupported excerpt profile")
    text = envelope.get("text")
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("invalid or oversized excerpt")
    observed_on = envelope.get("observed_on")
    if not isinstance(observed_on, str) or date.fromisoformat(observed_on).isoformat() != observed_on:
        raise ValueError("observation date must be ISO date")
    match = _url(envelope.get("source_url"), event=profile in {"betolimp_event_reader_v1", "betolimp_event_reader_v2"})
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if profile in {"betolimp_event_reader_v1", "betolimp_event_reader_v2"}:
        league = None
        if lines and lines[0].startswith('[Soccer]('):
            league = _event_breadcrumb(lines[0], envelope["source_url"])
            lines = lines[1:]
        result = _event(lines, envelope["source_url"], match,
                        expanded=profile == "betolimp_event_reader_v2")
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


# Exact section labels observed on the public event reader. Longest-first
# matching keeps "First Half Total Goals" out of the full-time "Total Goals".
_EVENT_SECTIONS = (
    "Full Time Result", "Double Chance", "Handicap Result", "Total Goals",
    "Exact Score", "Half Time/Full Time", "Teams To Score", "Alternative Handicap Result",
    "Alternative Total Goals", "Team Total", "Number Of Goals In Match", "Exact Total Goals",
    "Exact Total Goals By Team", "Score Draw", "Total Goals / Result", "Team To Score First Goal",
    "Time Of First Goal Brackets", "Team To Score Last Goal", "First Half Goals", "Second Half Goals",
    "Total Goals In Both Halves", "First Half Result", "First Half Double Chance",
    "First Half Handicap Result", "First Half Total Goals", "Second Half Result",
    "Second Half Double Chance", "Second Half Handicap Result", "Second Half Total Goals",
    "Goals In Each Half", "First Half Correct Score", "Multiple Correct Scores", "To Win To Nil",
)


class _NativeEventText(HTMLParser):
    """Bounded visible-text candidate reader, never a browser/JS interpreter."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.parts = []
        self.titles = []
        self.title_start = None
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        hidden = (bool(self.stack and self.stack[-1][1])
                  or tag in {"script", "style", "template", "noscript"}
                  or "hidden" in attrs or attrs.get("aria-hidden") == "true"
                  or re.search(r"(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\s*(?:;|$)",
                               attrs.get("style", ""), re.IGNORECASE) is not None)
        if tag == "link" and not hidden and "canonical" in str(attrs.get("rel", "")).split():
            self.canonicals.append(attrs.get("href"))
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            if len(self.stack) >= 128:
                raise ValueError("native markup nesting limit")
            self.stack.append((tag, hidden))
        if tag == "h1" and not hidden:
            if self.title_start is not None:
                raise ValueError("nested native event title")
            self.title_start = len(self.parts)

    def parse_html_declaration(self, position):
        if self.rawdata.startswith("<![", position):
            return self.parse_marked_section(position)
        return super().parse_html_declaration(position)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "h1" and self.title_start is not None:
            self.titles.append((self.title_start, len(self.parts)))
            self.title_start = None
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        elif any(t == tag for t, _ in self.stack):
            raise ValueError("ambiguous native markup nesting")

    def handle_data(self, data):
        if not (self.stack and self.stack[-1][1]) and data.strip():
            if len(self.parts) >= 50000:
                raise ValueError("native text limit")
            self.parts.append(data)


def inspect_native_event_html(body: bytes, source_url: str) -> dict:
    """Decode opt-in native layout CANDIDATES; never issue executable quotes.

    This conservative text-layout contract is tested synthetically, NOT yet
    verified against a successful origin capture. A canonical URL, one H1,
    ordered header and complete supported section pairs must all agree.
    No copied reader text is labelled native, no JS/config is executed, and
    no source year/zone, odds format, lifecycle or update clock is inferred.
    """
    match = _url(source_url, event=True)
    result = {"status": "native_event_layout_unresolved", "observations": [],
              "unsupported_observations": [], "admitted_rows": 0, "kickoff_utc": None,
              "quoted_at": None, "native_layout_verified": False,
              "hold_reasons": ["native_layout_not_origin_verified", "odds_view_profile_unverified",
                               "absolute_kickoff_unverified", "quote_update_time_unverified",
                               "fixture_not_independently_corroborated", "production_admission_not_implemented"]}
    if not isinstance(body, bytes) or len(body) > 2 * 1024 * 1024:
        raise ValueError("invalid native event bytes")
    try:
        page = _NativeEventText()
        page.feed(body.decode("utf-8", errors="strict"))
        page.close()
        if page.stack or page.canonicals != [source_url] or len(page.titles) != 1:
            return result
        start, end = page.titles[0]
        title = " ".join("".join(page.parts[start:end]).split())
        teams = title.split(" - ")
        if len(teams) != 2 or not all(len(t) <= 160 and source_team_key(t) for t in teams):
            return result
        home, away = teams
        compact = lambda text: re.sub(r"\s+", "", text)
        slug_key = re.sub(r"[^a-z0-9]", "", match[2].lower())
        team_slug = re.sub(r"[^a-z0-9]", "", (home + away).lower())
        if slug_key != team_slug:
            return result
        text = compact("".join(page.parts[end:]))
        header = re.match(rf"#(\d+){re.escape(compact(home))}(\d{{2}}[A-Z][a-z]{{2}})"
                          rf"((?:[01]\d|2[0-3]):[0-5]\d){re.escape(compact(away))}FullTimeResult", text)
        if not header:
            return result
        lines = [title, "#" + header[1], home, header[2][:2] + " " + header[2][2:], header[3], away]
        labels = {compact(label): label for label in _EVENT_SECTIONS}
        sections = list(re.finditer("|".join(re.escape(k) for k in sorted(labels, key=len, reverse=True)), text))
        for i, section in enumerate(sections):
            heading = labels[section[0]]
            value = text[section.end():sections[i + 1].start() if i + 1 < len(sections) else len(text)]
            if heading not in {"Full Time Result", "Total Goals", "Double Chance", "Teams To Score",
                               "Alternative Total Goals", "Team Total"}:
                continue
            if len(value) > 16384:
                return result
            lines.append(heading)
            if heading == "Full Time Result":
                q = re.fullmatch(rf"{re.escape(compact(home))}({PRICE})Draw({PRICE}){re.escape(compact(away))}({PRICE})", value)
                if not q:
                    return result
                lines.append(f"{home}{q[1]}Draw{q[2]}{away}{q[3]}")
            elif heading == "Double Chance":
                q = re.fullmatch(rf"{re.escape(compact(home))}orDraw({PRICE})Nodraw({PRICE})Drawor{re.escape(compact(away))}({PRICE})", value)
                if not q:
                    return result
                lines.append(f"{home} or Draw{q[1]}No draw{q[2]}Draw or {away}{q[3]}")
            elif heading == "Teams To Score":
                q = re.fullmatch(rf"{re.escape(compact(home))}toscore:yes{PRICE}{re.escape(compact(home))}toscore:no{PRICE}"
                                 rf"{re.escape(compact(away))}toscore:yes{PRICE}{re.escape(compact(away))}toscore:no{PRICE}"
                                 rf"Bothteamstoscore:yes({PRICE})Bothteamstoscore:no({PRICE})", value)
                if not q:
                    return result
                lines.append(f"Both teams to score: yes{q[1]}Both teams to score: no{q[2]}")
            else:
                totals = []
                offset = 0
                prefixes = (home, away) if heading == "Team Total" else ("Total",)
                prefix_pattern = "|".join(re.escape(compact(t)) for t in prefixes)
                for q in re.finditer(rf"({prefix_pattern})\((\d+(?:\.\d+)?)\)under({PRICE})\1\(\2\)over({PRICE})", value):
                    if q.start() != offset:
                        return result
                    offset = q.end()
                    prefix = next((t for t in (home, away) if compact(t) == q[1]), None) if heading == "Team Total" else "Total"
                    if prefix is None or (heading != "Team Total" and q[1] != "Total"):
                        return result
                    pair = f"{prefix} ({q[2]}) under{q[3]}{prefix} ({q[2]}) over{q[4]}"
                    totals.append((prefix, pair))
                if not totals or offset != len(value):
                    return result
                if heading == "Team Total":
                    # Require one contiguous block for each ordered club.
                    ordered = [p for p, _ in totals]
                    if ordered != sorted(ordered, key=lambda p: (home, away).index(p)) or set(ordered) != {home, away}:
                        return result
                    lines.extend("".join(pair for prefix, pair in totals if prefix == team) for team in (home, away))
                else:
                    lines.append("".join(pair for _, pair in totals))
        event = _event(lines, source_url, match, expanded=True)
    except (ValueError, AssertionError, UnicodeError, RecursionError):
        return result
    return {**result, "status": "native_event_market_candidates_unadmitted",
            "event_id": event["event_id"], "coupon_id": event["coupon_id"],
            "home": event["home"], "away": event["away"], "kickoff_display": event["kickoff_display"],
            "observations": event["observations"], "unsupported_observations": event["unsupported_observations"]}
