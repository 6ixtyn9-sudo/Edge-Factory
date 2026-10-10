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


def parse_page(body: str) -> dict:
    """Conservative observation: uncertain fields stay null, never inferred from tabs."""
    parser = _Text()
    parser.feed(body)
    text = html.unescape(" ".join(parser.parts))
    text = re.sub(r"\s+", " ", text)
    # Only the match header, not H2H or standings, can identify the fixture.
    header = re.search(r"Home\s+Football\s+(.{2,90}?)\s+(.{2,90}?)\s+-\s+(.{2,90}?)\s+(\d{2}\.\d{2}\.\d{4})", text)
    score = re.search(r"\b(\d{1,2}):(\d{1,2})\b", text[:1200])
    h2h = re.search(r"Head to Head: Last \d+.*?(\d+) wins\s+(\d+) draws\s+(\d+) win", text)
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
