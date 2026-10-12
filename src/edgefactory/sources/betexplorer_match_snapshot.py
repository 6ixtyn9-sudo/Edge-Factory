"""Bounded, opt-in own-card match-page observation; never an odds/pick input."""
from __future__ import annotations

import hashlib
import html
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse

from edgefactory.identity import source_team_key, squad_marker_mismatch

UA = "EdgeFactory-own-card-personal-snapshot/1.0 (+operator review)"


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag in ("td", "th", "h1", "h2", "h3", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        if tag in ("td", "th", "h1", "h2", "h3", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def validated_url(url: str) -> str:
    p = urlparse(url)
    if (p.scheme != "https" or p.hostname != "www.betexplorer.com"
            or p.query or p.fragment or not re.fullmatch(
                r"/football/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9-]+/[A-Za-z0-9]+/", p.path)):
        raise ValueError("not an approved plain BetExplorer football match URL")
    return url


def identity_match(card: dict, page: dict) -> bool:
    return (all(source_team_key(card.get(side)) and
                source_team_key(card.get(side)) == source_team_key(page.get(side)) and
                not squad_marker_mismatch(card.get(side), page.get(side))
                for side in ("home", "away")) and
            str(card.get("date", ""))[:10] == str(page.get("date", ""))[:10] and
            bool(card.get("league")) and
            source_team_key(card.get("league")) == source_team_key(page.get("league")))


def flatten_text(body: str) -> str:
    """Collapse a page body to single-spaced visible text.

    One flattener for every text-derived reading, so the odds adapter and this
    module observe the same strings (the page's own markup, not a re-render).
    """
    parser = _Text()
    parser.feed(body)
    return re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts)))


_H2H_NAME = re.compile(r"Head to Head: Last (\d+)")
# The record line reads "0 wins 1 draw 5 wins" on a live page (singular
# "draw" for one) — the older plural-only grammar missed that row entirely.
_H2H_RECORD = re.compile(r"(\d+) wins?\s+(\d+) draws?\s+(\d+) wins?")
_RESULT_DATE = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")
_RESULT_SCORE = re.compile(r"\b(\d{1,2})\s*:\s*(\d{1,2})\b")
_RESULT_ODDS = re.compile(r"\b(\d{1,2}\.\d{2})\s+(\d{1,2}\.\d{2})\s+(\d{1,2}\.\d{2})\b")
_H2H_STOPS = ("Show more matches", "Odds Comparison", "Standings")
_BLOCK_TEXT_CHARS = 96
# The H2H list and the league table are served in the response at their own
# length, so these caps bound a pathological page rather than the page's own
# list. Measured 2026-10-12 on a Premier League match page (Coventry vs
# Newcastle Utd): 20 H2H dated rows and the full 20-rank table were served,
# the form block serves its active view only ("5 results", five dated rows per
# side, closing 1x2 odds on each). Every expander in this region is a JS
# control with no href - the form view strip, "Show more matches" and "Show
# full table" carry no URL at all. The only hrefs are "Show all" (the
# mutual-matches/?home= list) and the standings tabs (standings/?...as-ajax=1),
# both on the standing never-fetch list, so there is nothing fetchable here
# that is not already banned; no request is made for any of them.
_MAX_H2H_ROWS = 40
_MAX_STANDINGS_ROWS = 40
# The standings header is the page's own column list (e.g.
# "# Team MP W D L G GD Pts Form"), read as labels, never as values.
_STANDINGS_HEADER = re.compile(r"#\s*Team\b.{0,80}?\bPts\b(?:\s+Form)?", re.S)
# One table row: rank. Team, then the page's own numeric tail
# (MP W D L GF:GA GD Pts). The team group is lazy so digit-leading club
# names ("1899 Hoffenheim", "1. FC Koln") stay in the team field.
_STANDINGS_ROW = re.compile(
    r"(?P<rank>\d{1,2})\.\s+(?P<team>.{2,60}?)\s+"
    r"(?P<mp>\d{1,3})\s+(?P<wins>\d{1,3})\s+(?P<draws>\d{1,3})\s+(?P<losses>\d{1,3})\s+"
    r"(?P<goals>\d{1,3})\s*:\s*(?P<conceded>\d{1,3})\s+"
    r"(?P<gd>-?\d{1,3})\s+(?P<points>\d{1,3})\b",
    re.S,
)


def _result_rows(region: str, *, limit: int) -> list[dict]:
    """Date/score/(optional odds) rows out of a results-style text region.

    Rows are keyed on the page's date marker so a malformed stretch is skipped
    instead of shifting every later row; ``text`` is a bounded excerpt of what
    was read, never a reconstruction.
    """
    marks = list(_RESULT_DATE.finditer(region))
    rows: list[dict] = []
    for index, mark in enumerate(marks):
        if len(rows) >= limit:
            break
        end = marks[index + 1].start() if index + 1 < len(marks) else len(region)
        chunk = region[mark.start():min(end, mark.start() + 240)]
        score = _RESULT_SCORE.search(chunk)
        if score is None:
            continue
        odds = _RESULT_ODDS.search(chunk, score.end())
        rows.append({
            "date": f"{mark.group(3)}-{mark.group(2)}-{mark.group(1)}",
            "score": [int(score.group(1)), int(score.group(2))],
            "odds": [float(odds.group(1)), float(odds.group(2)), float(odds.group(3))]
                    if odds else None,
            "text": re.sub(r"\s+", " ", chunk).strip()[:_BLOCK_TEXT_CHARS],
        })
    return rows


def _standings_block(text: str) -> dict:
    """The league table the page serves, read from the page's own columns.

    The match page holds the whole table (its own "Show full table" control is a
    JS control with no href; the tab links are AJAX sub-tables this module never
    fetches), so rows are read in full, capped at _MAX_STANDINGS_ROWS for a
    pathological page. Column labels come from the page's own header; the numeric tail of
    each row (MP W D L GF:GA GD Pts) is what makes a row a row, so an
    unlabelled digit run is skipped rather than guessed into a column.
    """
    start = text.find("Standings")
    if start == -1:
        return {}
    end = len(text)
    for marker in ("Show full table", "Last results:"):
        found = text.find(marker, start)
        if found != -1:
            end = min(end, found)
    region = text[start:end]
    header = _STANDINGS_HEADER.search(region)
    if header is None:
        return {}
    rows: list[dict] = []
    for match in _STANDINGS_ROW.finditer(region[header.end():]):
        if len(rows) >= _MAX_STANDINGS_ROWS:
            break
        rows.append({
            "rank": int(match.group("rank")),
            "team": re.sub(r"\s+", " ", match.group("team")).strip(),
            "mp": int(match.group("mp")),
            "wins": int(match.group("wins")),
            "draws": int(match.group("draws")),
            "losses": int(match.group("losses")),
            "goals_for": int(match.group("goals")),
            "goals_against": int(match.group("conceded")),
            "goal_difference": int(match.group("gd")),
            "points": int(match.group("points")),
        })
    if not rows:
        return {}
    return {"standings_columns": header.group(0).split(),
            "standings_rows": rows}


def parse_match_page_blocks(body) -> dict:
    """Match-page observations from the page the odds lane fetches anyway.

    Text-derived only: this records what the page showed (H2H record and rows,
    last-results rows with their own block label, and the league table), never
    what it means. Everything is kept exactly as the fetched response served
    it, up to a bound for a pathological page: the H2H list arrives at its own
    length, and the form block carries only its active view (measured on a
    live page: "5 results", five dated rows per side — the 10/15/all views are
    not in the response). Every expander here is a JS control with no href;
    the only hrefs in the region are the mutual-matches list ("Show all") and
    the standings AJAX tabs, both on the standing never-fetch list, so nothing
    fetchable exists here that is not banned and this module requests none of
    them. Missing structures stay missing; nothing here is consumed by
    pricing, cards, or ML, so an unverified selector can never become a price,
    and no team name is invented for an unlabelled row.
    """
    text = flatten_text(body)
    out: dict = {"blocks": []}

    h2h_head = _H2H_NAME.search(text)
    if h2h_head is not None:
        out["blocks"].append("h2h")
        out["h2h_meetings"] = int(h2h_head.group(1))
        stop = len(text)
        for marker in _H2H_STOPS:
            found = text.find(marker, h2h_head.end())
            if found != -1:
                stop = min(stop, found)
        record = _H2H_RECORD.search(text, h2h_head.end(), stop)
        if record is not None:
            out["h2h_record"] = {"home_wins": int(record.group(1)),
                                 "draws": int(record.group(2)),
                                 "away_wins": int(record.group(3))}
        out["h2h_rows"] = _result_rows(text[h2h_head.end():stop], limit=_MAX_H2H_ROWS)

    # Last-results blocks are found by their own "Last results: <team>" labels,
    # so the observation never needs the caller's spelling of either side.
    labels = list(re.finditer(r"Last results:\s*([^0-9]{2,40})", text))
    last_rows: list[dict] = []
    for index, label in enumerate(labels):
        end = labels[index + 1].start() if index + 1 < len(labels) else len(text)
        heading = re.sub(r"\s+", " ", label.group(1)).split(" Show")[0].strip()[:40]
        for row in _result_rows(text[label.end():end], limit=5):
            last_rows.append({**row, "label": heading})
    if last_rows:
        out["blocks"].append("last_results")
        out["last_results_rows"] = last_rows

    standings = _standings_block(text)
    if standings:
        out["blocks"].append("standings")
        out.update(standings)

    return out


def parse_page(body: str) -> dict:
    """Conservative observation: uncertain fields stay null, never inferred from tabs."""
    text = flatten_text(body)
    # Only the match header, not H2H or standings, can identify the fixture.
    header = re.search(r"Home\s+Football\s+(.{2,90}?)\s+(.{2,90}?)\s+-\s+(.{2,90}?)\s+(\d{2}\.\d{2}\.\d{4})", text)
    score = re.search(r"\b(\d{1,2}):(\d{1,2})\b", text[:1200])
    h2h = re.search(r"Head to Head: Last \d+.*?(\d+) wins?\s+(\d+) draws?\s+(\d+) wins?", text)
    # Prices and positions require independently verified HTML selectors; labels alone are not values.
    return {"score": [int(score[1]), int(score[2])] if score else None,
            "h2h_record": [int(h2h[1]), int(h2h[2]), int(h2h[3])] if h2h else None,
            "standings_position": None, "prices_1x2": None,
            "header_verified": bool(header)}


def fetch_page(url: str) -> tuple[str, str]:
    validated_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=20) as response:
        if response.status != 200:
            raise ValueError("non-200 response")
        body = response.read(512_001)
        if len(body) > 512_000:
            raise ValueError("page exceeds size limit")
        if "text/html" not in response.headers.get("Content-Type", ""):
            raise ValueError("not HTML")
    return body.decode("utf-8", "replace"), hashlib.sha256(body).hexdigest()
