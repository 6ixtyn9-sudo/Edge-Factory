"""Pure bookmaker context decoders and own-card diagnostic.

SportPesa-branded Sportradar public match pages only. No HTTP, registration,
state writer, odds, probabilities or admission path. Shares existing identity
and timestamp guards. Reader and native evidence are never interchangeable.
Native support is limited to explicitly bound semantic standings tables.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from edgefactory.identity import (
    canonical_league_key,
    source_team_key,
    squad_marker_mismatch,
    squad_markers,
)
from edgefactory.odds_normalization import parse_zoned_timestamp

MAX_CONTEXT_BYTES = 128 * 1024
MAX_CONTEXT_PAGES = 100
PREFIX = "https://statshub.sportradar.com/sportpesa/en/"
MATCH_URL = re.compile(re.escape(PREFIX) + r"match/[1-9]\d{0,11}")
CONTEXT_URL = re.compile(MATCH_URL.pattern + r"(?:/statistics)?")
TEAM_URL = re.escape(PREFIX) + r"sport/1/team/([1-9]\d{0,11})\?seasonId=(\d{1,12})&tournamentId=(\d{1,12})"
TEAM_LINK = re.compile(r"\[([^\[\]]{1,240})\]\((" + TEAM_URL + r")\)")
MATCH_LINK = re.compile(r"\[([^\[\]]{1,1600})\]\((" + MATCH_URL.pattern + r")\)")
COLUMNS = ["#", "Team", "P", "W", "D", "L", "GF", "GA", "DIFF", "PTS", "Form"]
# Both layouts observed: CAF women omits Form, never a numeric core column.
STANDINGS_LAYOUTS = (COLUMNS, COLUMNS[:-1])
MONTH_DATE = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}\b")
HOLDS = (
    "reader_transcription_not_native_response", "collection_permission_unresolved",
    "third_party_supplier_not_independent_bookmaker_data", "absolute_kickoff_unverified",
    "native_context_decoding_unimplemented", "result_periods_not_verified_for_regulation",
    "production_admission_not_implemented", "fixture_not_independently_corroborated",
)


def validate_context_url(value: str) -> str:
    """Observed Overview/Statistics routes, fixed tenant; no API/private paths."""
    if not isinstance(value, str) or CONTEXT_URL.fullmatch(value) is None:
        raise ValueError("not a plain SportPesa-branded public match URL")
    return value


def _clean(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", html.unescape(text))
    return (text.replace("\\<br>", " ").replace("<br>", " ").replace("\\", "")
            .replace("\u200c", "").replace("\u200e", "").replace("\u200f", ""))


def _date(text: str) -> str | None:
    found = MONTH_DATE.search(text)
    if found:
        try:
            return datetime.strptime(found[0], "%b %d, %Y").date().isoformat()
        except ValueError:
            pass
    return None


def _team(match: re.Match) -> dict:
    aliases = list(dict.fromkeys(s.strip() for s in match[1].splitlines() if s.strip()))
    return {"names": aliases, "team_url": match[2], "team_id": match[3],
            "season_id": match[4], "tournament_id": match[5]}


def _standings_values(cells: list[str]) -> dict:
    """One arithmetic contract shared by reader and native table diagnostics."""
    if len(cells) not in (10, 11):
        raise ValueError("wrong standings columns")
    values = [int(cells[i]) for i in (0, 2, 3, 4, 5, 6, 7, 8, 9)]
    rank, played, wins, draws, losses, gf, ga, diff, points = values
    if (not 1 <= rank <= 100 or any(not 0 <= n <= 999 for n in
            (played, wins, draws, losses, gf, ga)) or not -999 <= points <= 999
            or played != wins + draws + losses or diff != gf - ga):
        raise ValueError("inconsistent standings arithmetic")
    return {"rank": rank, "played": played, "wins": wins, "draws": draws,
            "losses": losses, "goals_for": gf, "goals_against": ga,
            "goal_difference": diff, "points": points}


def _tables(text: str) -> tuple[list[dict], int]:
    tables, invalid = [], 0
    label, table = None, None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith("|"):
            table = None
            if line not in {"TotalHomeAwayComplete", "Full Time1st half2nd half"}:
                heading = re.fullmatch(r"### Table \[\|?\s*([^\]]+)\]\([^)]*\)", line)
                label = (heading[1] if heading else line)[:240]
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells in STANDINGS_LAYOUTS:
            width = len(cells)
            table = {"label": label, "rows": []}
            tables.append(table)
            if len(tables) > 8:
                raise ValueError("context table limit")
            continue
        if table is None or all(re.fullmatch(r"[-:]+", c) for c in cells):
            continue
        if len(tables) > 8 or len(table["rows"]) >= 40:
            raise ValueError("context table limit")
        if len(cells) != width or TEAM_LINK.fullmatch(cells[1]) is None:
            invalid += 1
            continue
        try:
            values = _standings_values(cells)
        except ValueError:
            invalid += 1
            continue
        table["rows"].append({**_team(TEAM_LINK.fullmatch(cells[1])), **values})
    return tables, invalid


def parse_context_excerpt(raw: dict) -> dict:
    required = {"evidence_kind", "source_url", "observed_at_utc", "excerpt_scope", "text"}
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("expected an explicitly labelled reader document")
    if raw["evidence_kind"] != "reader_transcription" or raw["excerpt_scope"] not in {
            "selected_sections", "full_page"}:
        raise ValueError("native evidence cannot be relabelled as reader input")
    url = validate_context_url(raw["source_url"])
    observed = parse_zoned_timestamp(raw["observed_at_utc"])
    body = raw["text"]
    if (observed is None or not isinstance(body, str) or not body.strip()
            or len(body.encode("utf-8")) > MAX_CONTEXT_BYTES):
        raise ValueError("invalid or oversized reader document")
    text = _clean(body).strip()
    # Only the fixture header, never team links in old results or standings.
    header = text.split("[Overview]", 1)[0] if "[Overview]" in text else ""
    teams = {}
    for match in TEAM_LINK.finditer(header):
        team = _team(match)
        key = (team["team_id"], team["season_id"], team["tournament_id"])
        if key in teams and teams[key] != team:
            raise ValueError("conflicting responsive header identities")
        teams[key] = team
    ordered = list(teams.values())
    identified = (len(ordered) == 2 and all(t["names"] for t in ordered) and ordered[0]["team_id"] != ordered[1]["team_id"]
                  and all(ordered[0][k] == ordered[1][k] for k in ("season_id", "tournament_id")))
    fixture_date = _date(header.splitlines()[0]) if header.splitlines() else None
    tables, invalid = _tables(text)
    if identified and any(row[k] != ordered[0][k] for table in tables for row in table["rows"]
                          for k in ("season_id", "tournament_id")):
        invalid += 1
    labels = list(dict.fromkeys(table["label"] for table in tables if table["label"]))
    # Only explicit competition gender/age labels. "Group B" never means reserves.
    scope_text = " ".join(labels).casefold()
    scope = set(re.findall(r"\bu(?:17|18|19|20|21|22|23|25)\b", scope_text))
    if re.search(r"\b(?:women|women's|womens|femenina|frauen)\b", scope_text):
        scope.add("women")
    h2h = re.search(r"(?m)^### Matches played - (\d{1,4})\s*\|", text)
    results, unparsed = [], 0
    for section in re.split(r"(?m)^### ", text)[1:]:
        if not section.startswith("Last matches "):
            continue
        owner = TEAM_LINK.search(section.splitlines()[0])
        if not owner or owner[3] not in {team["team_id"] for team in ordered}:
            unparsed += 1
            continue
        for match in MATCH_LINK.finditer(section):
            nodes = [s.strip() for s in match[1].splitlines() if s.strip()]
            when = _date(match[1])
            if (len(nodes) < 5 or not when or nodes[-1] not in {"FT", "AP", "AET"}
                    or not all(re.fullmatch(r"\d{1,2}", n) for n in nodes[-3:-1])):
                unparsed += 1
                continue
            if len(results) >= 80:
                raise ValueError("context result limit")
            results.append({"owner_team_id": owner[3] if owner else None,
                            "date": when, "home": nodes[-5], "away": nodes[-4],
                            "score": [int(n) for n in nodes[-3:-1]], "period": nodes[-1],
                            "source_url": match[2], "regulation_usable": False,
                            "strictly_before_fixture_date": bool(fixture_date and when < fixture_date)})
    live = bool(re.search(r"(?mi)^(?:Live|Halftime|1st half|2nd half|Ended|END|FT|AP|AET)$", header)
                or re.search(r"\b\d{1,3}[’']", header))
    return {"source": "sportpesa-statshub", "bookmaker_brand": "sportpesa",
            "identified_context_supplier": "sportradar", "evidence_kind": "reader_transcription",
            "source_url": url, "observed_at_utc": observed.astimezone(UTC).isoformat(),
            "excerpt_scope": raw["excerpt_scope"],
            "transcription_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "fixture_structure_recognized": bool(identified and fixture_date),
            "teams": ordered if identified else [], "fixture_date": fixture_date,
            "kickoff_utc": None, "competition_labels": labels,
            "competition_squad_scope": sorted(scope), "fixture_live_or_ended_hint": live,
            "standings_tables": tables, "invalid_standings_rows": invalid,
            "h2h_encounters_displayed": int(h2h[1]) if h2h else None,
            "recent_results": results, "unparsed_recent_result_links": unparsed,
            "native_decoded_context_rows": 0, "admitted_rows": 0,
            "hold_reasons": list(HOLDS)}


def parse_context_batch(raw: list) -> list[dict]:
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_CONTEXT_PAGES:
        raise ValueError("expected one to 100 bounded reader pages")
    pages = [parse_context_excerpt(item) for item in raw]
    if len({p["source_url"].removesuffix("/statistics") for p in pages}) != len(pages):
        raise ValueError("duplicate event snapshots require explicit operator reconciliation")
    return pages


def _scoped_name(name: str, scope: list[str]) -> str | None:
    markers = squad_markers(name)
    ages = {s for s in scope if s.startswith("u")}
    if len(ages) > 1 or (ages and any(m.startswith("u") and m not in ages for m in markers)):
        return None
    additions = (["W"] if "women" in scope and "women" not in markers else [])
    additions += sorted(ages - markers)
    return " ".join([name, *additions])


def _side_matches(card_name: str, team: dict, scope: list[str]) -> bool:
    spellings = [_scoped_name(name, scope) for name in team["names"]]
    # A short responsive spelling may omit a competition-declared W/U19, but
    # never let an unqualified alias erase B/II/third-team or conflicting ages.
    if any(name is None for name in spellings) or len({squad_markers(n) for n in spellings}) != 1:
        return False
    return any(source_team_key(card_name) == source_team_key(candidate)
               and not squad_marker_mismatch(card_name, candidate) for candidate in spellings)


def context_slate_coverage(card: list[dict], pages: list[dict], as_of: datetime) -> dict:
    """All card rows, not just successes. Candidate diagnostics, never admission.

    Same-team spelling variants are allowed only when the SAME observed team
    link supplies them. No fuzzy matching, new aliases, forced league/date/zone
    repairs, or generic reserve/age folding. Scope completion is diagnostic-only
    and explicitly based on the printed competition label.
    """
    if (not isinstance(card, list) or len(card) > 5000 or any(not isinstance(r, dict) for r in card)
            or not isinstance(as_of, datetime) or as_of.tzinfo is None):
        raise ValueError("invalid card or zone-free as-of")
    rows, by_league, queue = [], {}, []
    future_candidates = 0
    for index, row in enumerate(card):
        candidates = []
        valid = all(isinstance(row.get(k), str) and row[k].strip() for k in ("home", "away", "league"))
        kickoff = parse_zoned_timestamp(row.get("kickoff_utc"))
        for page in pages if valid else []:
            if (not page["fixture_structure_recognized"] or not all(
                    _side_matches(row[side], page["teams"][i], page["competition_squad_scope"])
                    for i, side in enumerate(("home", "away")))):
                continue
            holds = list(HOLDS)
            date_match = bool(kickoff and kickoff.date().isoformat() == page["fixture_date"])
            league_match = any(canonical_league_key(row["league"]) == canonical_league_key(label)
                               for label in page["competition_labels"])
            if not league_match:
                holds.append("literal_competition_join_unresolved")
            if not date_match:
                holds.append("calendar_date_unresolved")
            observed = parse_zoned_timestamp(page["observed_at_utc"])
            if observed > as_of:
                holds.append("observation_after_as_of")
            if kickoff is None:
                holds.append("card_absolute_kickoff_missing")
            elif kickoff <= as_of or observed >= kickoff:
                holds.append("not_a_predecision_capture_for_card_kickoff")
            if page["fixture_live_or_ended_hint"]:
                holds.append("source_fixture_live_or_ended_hint")
            if page["invalid_standings_rows"]:
                holds.append("standings_structure_inconsistent")
            context_rows = sum(len(t["rows"]) for t in page["standings_tables"]) + len(page["recent_results"])
            candidates.append({"source_url": page["source_url"], "calendar_date_candidate": date_match,
                               "literal_league_match": league_match, "reader_context_rows": context_rows,
                               "competition_squad_scope": page["competition_squad_scope"],
                               "hold_reasons": holds, "admitted": False})
        status = ("invalid_card_identity" if not valid else "not_observed_in_supplied_pages"
                  if not candidates else "ambiguous_source_fixture" if len(candidates) > 1
                  else "reader_candidate_only")
        if len(candidates) == 1:
            c = candidates[0]
            if (kickoff and kickoff > as_of and c["calendar_date_candidate"]
                    and not any(h in c["hold_reasons"] for h in (
                        "observation_after_as_of", "source_fixture_live_or_ended_hint",
                        "not_a_predecision_capture_for_card_kickoff"))):
                queue.append(c["source_url"])
                future_candidates += 1
        rows.append({"card_index": index, "home": row.get("home"), "away": row.get("away"),
                     "league": row.get("league"), "kickoff_utc": row.get("kickoff_utc"),
                     "status": status, "candidates": candidates, "admitted": False,
                     "card_time_status": "unknown_kickoff" if kickoff is None else
                     "future_kickoff" if kickoff > as_of else "at_or_after_kickoff"})
        group = by_league.setdefault(str(row.get("league") or "unknown"),
                                    {"card_rows": 0, "candidate_rows": 0, "unobserved_rows": 0})
        group["card_rows"] += 1
        group["candidate_rows"] += bool(candidates)
        group["unobserved_rows"] += not candidates
    urls = list(dict.fromkeys(queue))
    joined = {c["source_url"] for r in rows for c in r["candidates"]}
    return {"mode": "offline_bookmaker_context_slate_diagnostic", "network_requests": 0,
            "writes": 0, "admitted_rows": 0, "native_decoded_context_rows": 0,
            "as_of_utc": as_of.astimezone(UTC).isoformat(), "card_rows_examined": len(card),
            "reader_pages_examined": len(pages), "rows": rows, "by_league": by_league,
            "unjoined_reader_pages": [{"source_url": p["source_url"], "teams": p["teams"],
                                       "competition_labels": p["competition_labels"]}
                                      for p in pages if p["source_url"] not in joined],
            "date_candidate_card_rows": sum(any(c["calendar_date_candidate"] for c in r["candidates"])
                                            for r in rows),
            "card_future_rows": sum(r["card_time_status"] == "future_kickoff" for r in rows),
            "future_candidate_card_rows": future_candidates,
            "pending_native_url_count": len(urls),
            "candidate_card_rows": sum(bool(r["candidates"]) for r in rows),
            "unobserved_card_rows": sum(not r["candidates"] for r in rows),
            "ambiguous_card_rows": sum(len(r["candidates"]) > 1 for r in rows),
            "coverage_status": "reader_candidates_only_not_native_or_usable_slate_coverage",
            "pending_native_batches_not_executed": [urls[i:i + 3] for i in range(0, len(urls), 3)],
            "snapshots": pages}


# Standard semantic HTML only. No guessed CSS selectors, JS evaluation,
# hydration-key guesses, widget/API fetches or browser session state.
_NATIVE_LIMIT = 2 * 1024 * 1024
_NATIVE_TEAM = re.compile(TEAM_URL)
_VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
         'meta', 'param', 'source', 'track', 'wbr'}
_STRUCTURAL = {'a', 'table', 'tr', 'td', 'th', 'caption'}
_SAFE_LABEL = re.compile(r"[\w .,'’&()+:/|–—-]{1,160}")


def _native_label(value: str) -> str | None:
    label = ' '.join(value.split())
    if (_SAFE_LABEL.fullmatch(label) is None or 'http' in label.casefold()
            or any(ord(c) < 32 or 0x202A <= ord(c) <= 0x202E
                   or 0x2066 <= ord(c) <= 0x2069 for c in label)):
        return None
    return label


class _NativeContextHTML(HTMLParser):
    """Bounded semantic shape collector; arbitrary text/attributes never exported."""

    def __init__(self, source_url: str):
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        self.fixture_url = source_url.removesuffix("/statistics")
        self.stack = []
        self.nodes = 0
        self.counts = dict.fromkeys(('table', 'tr', 'th', 'td', 'a', 'time', 'script'), 0)
        self.roles = dict.fromkeys(('table', 'row', 'columnheader', 'cell', 'gridcell'), 0)
        self.script_counts = dict.fromkeys(('inert_json', 'json_ld', 'external', 'inline'), 0)
        self.canonical = set()
        self.canonical_conflict = False
        self.overview = False
        self.header_teams = {}
        self.anchor = None
        self.table = self.row = self.cell = None
        self.caption = None
        self.tables = []

    def _public_url(self, value):
        if not isinstance(value, str) or any(c.isspace() for c in value):
            return None
        url = urljoin(self.source_url, value)
        return url if CONTEXT_URL.fullmatch(url) or _NATIVE_TEAM.fullmatch(url) else None

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > 40000 or len(self.stack) >= 96:
            raise ValueError('HTML structure limit')
        attrs = dict(attrs)
        if tag in self.counts:
            self.counts[tag] += 1
        if attrs.get('role') in self.roles:
            self.roles[attrs['role']] += 1
        if tag == 'script':
            kind = (attrs.get('type') or '').strip().casefold()
            group = ('inert_json' if kind == 'application/json' else 'json_ld'
                     if kind == 'application/ld+json' else 'external' if 'src' in attrs else 'inline')
            self.script_counts[group] += 1
        style = re.sub(r'\s+', '', attrs.get('style') or '').casefold()
        hidden = (bool(self.stack and self.stack[-1][1]) or tag in
                  {'script', 'style', 'template', 'noscript'} or 'hidden' in attrs
                  or (attrs.get('aria-hidden') or '').casefold() == 'true'
                  or 'display:none' in style or 'visibility:hidden' in style)
        if tag not in _VOID:
            self.stack.append((tag, hidden))
        if hidden:
            return
        if tag == 'link' and 'canonical' in (attrs.get('rel') or '').casefold().split():
            url = self._public_url(attrs.get('href'))
            if url in {self.fixture_url, self.fixture_url + "/statistics"}:
                self.canonical.add(url)
            else:
                self.canonical_conflict = True
        if tag == 'a':
            if self.anchor is not None:
                raise ValueError('nested anchor')
            self.anchor = {'url': self._public_url(attrs.get('href')), 'text': ''}
        if tag == 'table' and self.overview:
            if self.table is not None or len(self.tables) >= 8:
                raise ValueError('native table limit or nesting')
            self.table = {'caption': None, 'rows': []}
        if self.table is not None:
            if tag == 'caption':
                self.caption = ''
            if tag == 'tr':
                if self.row is not None or len(self.table['rows']) >= 41:
                    raise ValueError('native row limit or nesting')
                self.row = []
            if tag in {'td', 'th'}:
                if self.row is None or self.cell is not None or len(self.row) >= 11:
                    raise ValueError('native cell limit or nesting')
                self.cell = {'tag': tag, 'text': '', 'teams': []}

    def handle_data(self, data):
        if not self.stack or self.stack[-1][1]:
            return
        for target, key, limit in ((self.anchor, 'text', 512), (self.cell, 'text', 1024)):
            if target is not None:
                target[key] += ' ' + data
                if len(target[key]) > limit:
                    raise ValueError('native text limit')
        if self.caption is not None:
            self.caption += data
            if len(self.caption) > 160:
                raise ValueError('native caption limit')

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        found = next((i for i in range(len(self.stack) - 1, -1, -1)
                      if self.stack[i][0] == tag), None)
        if found is None:
            if tag in _STRUCTURAL:
                raise ValueError('unmatched semantic close')
            return
        if any(t in _STRUCTURAL for t, _ in self.stack[found + 1:]):
            raise ValueError('implicitly closed semantic structure')
        hidden = self.stack[found][1]
        del self.stack[found:]
        if hidden:
            return
        if tag == 'a' and self.anchor is not None:
            anchor, self.anchor = self.anchor, None
            label = _native_label(anchor['text'])
            match = _NATIVE_TEAM.fullmatch(anchor['url'] or '')
            if label and match:
                team = {'names': [label], 'team_url': anchor['url'], 'team_id': match[1],
                        'season_id': match[2], 'tournament_id': match[3]}
                if not self.overview:
                    key = (match[1], match[2], match[3])
                    previous = self.header_teams.setdefault(key, team)
                    if label not in previous['names']:
                        previous['names'].append(label)
                if self.cell is not None:
                    self.cell['teams'].append(team)
            if anchor['url'] == self.fixture_url and label == 'Overview':
                self.overview = True
        if tag in {'th', 'td'} and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.table['rows'].append(self.row)
            self.row = None
        if tag == 'caption' and self.caption is not None:
            self.table['caption'] = _native_label(self.caption)
            self.caption = None
        if tag == 'table' and self.table is not None:
            if self.cell is not None or self.row is not None:
                raise ValueError('unclosed native table row')
            self.tables.append(self.table)
            self.table = None


def parse_native_context_html(body: bytes, source_url: str) -> dict:
    """Inspect one complete native response, without reconstructing reader input.

    This supports only strictly checked semantic standings tables with the exact
    observed columns, canonical event binding, a two-team Overview header and
    matching provider season/tournament/team IDs. Not site-CSS verification or
    a complete context adapter. Native dates/results/H2H and admission stay held.
    """
    validate_context_url(source_url)
    if not isinstance(body, bytes) or len(body) > _NATIVE_LIMIT:
        raise ValueError('invalid native context bytes')
    result = {'evidence_kind': 'native_html_semantic_inspection',
              'status': 'no_supported_semantic_tables', 'decoded_context_row_count': 0,
              'standings_tables': [], 'admitted_rows': 0, 'kickoff_utc': None,
              'native_results_and_h2h_status': 'not_implemented',
              'field_validation_status': 'retained_native_fixture_not_available'}
    parser = _NativeContextHTML(source_url)
    try:
        parser.feed(body.decode('utf-8'))
        parser.close()
        if parser.table is not None or parser.anchor is not None or parser.row is not None:
            raise ValueError('incomplete native structure')
    except (UnicodeError, ValueError, AssertionError, RecursionError):
        return {**result, 'status': 'unsupported_or_malformed_native_structure'}
    result['markup_counts'] = parser.counts
    result['role_counts'] = parser.roles
    result['script_counts'] = parser.script_counts
    teams = list(parser.header_teams.values())
    bound = (bool(parser.canonical) and not parser.canonical_conflict
             and parser.overview and len(teams) == 2 and teams[0]['team_id'] != teams[1]['team_id']
             and all(teams[0][k] == teams[1][k] for k in ('season_id', 'tournament_id')))
    result['fixture_route_and_header_bound'] = bool(bound)
    supported = [table for table in parser.tables if table['rows'] and
                 [c['text'].strip() for c in table['rows'][0]] in STANDINGS_LAYOUTS and
                 all(c['tag'] == 'th' for c in table['rows'][0])]
    result['supported_semantic_table_count'] = len(supported)
    if not supported:
        return result
    if not bound:
        return {**result, 'status': 'native_fixture_binding_unresolved'}
    if len(supported) > 1 and (any(not t['caption'] for t in supported)
                             or len({t['caption'] for t in supported}) != len(supported)):
        return {**result, 'status': 'native_table_phase_ambiguous'}
    tables = []
    try:
        for table in supported:
            rows = []
            seen = set()
            for cells in table['rows'][1:]:
                if len(cells) != len(table['rows'][0]) or len(cells[1]['teams']) != 1:
                    raise ValueError('unsupported native row')
                team = cells[1]['teams'][0]
                if (team['team_id'] in seen or any(team[k] != teams[0][k] for k in ('season_id', 'tournament_id'))):
                    raise ValueError('unbound or duplicate native team row')
                seen.add(team['team_id'])
                rows.append({**team, **_standings_values([c['text'].strip() for c in cells])})
            tables.append({'phase_label': table['caption'], 'rows': rows,
                           'contains_both_fixture_teams': {t['team_id'] for t in teams} <= seen})
        if not any(t['contains_both_fixture_teams'] for t in tables):
            raise ValueError('incomplete native fixture tables')
    except (ValueError, TypeError, KeyError):
        return {**result, 'status': 'native_standings_structure_inconsistent'}
    return {**result, 'status': 'native_semantic_standings_decoded_diagnostic_only',
            'standings_tables': tables, 'decoded_context_row_count': sum(len(t['rows']) for t in tables)}


# Static evidence only: these names are research leads, not an endpoint registry.
_DISCOVERY_OPERATIONS = (
    "match_info_statshub", "stats_match_get", "stats_match_head2head",
    "stats_team_lastx", "stats_team_nextx", "stats_team_versus",
    "stats_season_tables", "config_tree_mini", "event_get",
    # Observed in the page-referenced feeds bundle, not guessed API routes.
    "stats_match_form", "stats_match_tableslice", "stats_team_versusrecent",
    "stats_team_lastxextended", "stats_uniquetournament_fixtures",
    "stats_season_teamfixtures", "stats_season_fixtures2", "stats_season_meta",
    "livescore_season_fixtures",
)
_DISCOVERY_CONFIG_REFERENCES = (
    "cctxInitValues", "__reactRouterContext", "__reactRouterManifest",
    "fishnetUrl", "fishnetClientAlias", "fishnetToken",
)
_DISCOVERY_FIELDS = frozenset({
    "data", "props", "pageProps", "state", "events", "matches", "teams",
    "standings", "tables", "results", "home", "away", "seasonId", "tournamentId",
})
_SCRIPT_URL = re.compile(r"https://statshub\.sportradar\.com/assets/[A-Za-z0-9_-]{1,160}\.js")


def validate_discovery_asset_url(url: str) -> str:
    """Only fixed-origin static JS; queries, private paths and other tenants excluded."""
    if not isinstance(url, str) or _SCRIPT_URL.fullmatch(url) is None:
        raise ValueError("unsupported public script asset")
    return url


def _rank_discovery_assets(assets: list[str]) -> list[str]:
    """Prioritize observed feed/context assets, never manufacture a hashed URL.

    A field run spent both asset GETs on manifest/jsx-runtime while the document
    referenced feeds and root farther down the list. Rank before truncation so
    reference order cannot hide those modules beyond the sixteen-item receipt.
    Stable fallback preserves reference order; the HTTP budget remains three.
    """
    priority = {"feeds": 0, "root": 1, "cctx": 2}
    return sorted(dict.fromkeys(assets), key=lambda url: priority.get(
        url.rsplit("/", 1)[-1].split("-", 1)[0], 3))


class _DataLoadingHTML(HTMLParser):
    def __init__(self, source_url):
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        self.scripts = []
        self.preloads = []
        self.assets = []
        self.current = None
        self.nodes = 0
        self.unsupported_assets = 0
        self.inert_depth = 0

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > 40000:
            raise ValueError("discovery node limit")
        attrs = dict(attrs)
        if tag in {"template", "noscript"}:
            self.inert_depth += 1
        if tag == "script":
            if len(self.scripts) >= 64 or self.current is not None:
                raise ValueError("discovery script limit or nesting")
            self.current = {"json": (attrs.get("type") or "").strip().lower()
                            in {"application/json", "application/ld+json"}, "text": "",
                            "loader_json": (attrs.get("type") or "").strip().lower() == "application/json",
                            "loader_executable": (attrs.get("type") or "").strip().lower()
                            in {"", "module", "application/javascript", "text/javascript"},
                            "loader_eligible": "src" not in attrs and not self.inert_depth}
            self.scripts.append(self.current)
        value = attrs.get("src") if tag == "script" else attrs.get("href") if (
            tag == "link" and "modulepreload" in (attrs.get("rel") or "").split()) else None
        if value is not None:
            target = urljoin(self.source_url, value)
            if _SCRIPT_URL.fullmatch(target):
                dest = self.assets if tag == "script" else self.preloads
                if target not in dest:
                    if len(self.assets) + len(self.preloads) >= 256:
                        raise ValueError("discovery asset reference limit")
                    dest.append(target)
            else:
                self.unsupported_assets += 1

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data

    def handle_endtag(self, tag):
        if tag in {"template", "noscript"}:
            self.inert_depth = max(0, self.inert_depth - 1)
        if tag == "script":
            self.current = None


def inspect_native_data_loading(body: bytes, source_url: str, *, is_script: bool = False) -> dict:
    """Describe referenced assets/JSON/API markers, without execution or URL replay.

    Never exports script bodies, arbitrary JSON keys/values, request parameters,
    credentials or signed URLs. A marker is not a verified API endpoint/schema.
    """
    (validate_discovery_asset_url if is_script else validate_context_url)(source_url)
    if not isinstance(body, bytes) or len(body) > _NATIVE_LIMIT:
        raise ValueError("invalid discovery body")
    result = {"evidence_kind": "native_static_data_loading_inspection",
              "status": "inspected_not_api_verified",
              "coverage_status": "static_references_only_runtime_xhr_not_observed",
              "script_asset_urls": [],
              "asset_selection_policy": "observed_feeds_root_context_then_reference_order",
              "referenced_script_asset_count": 0,
              "runtime_config_reference_hints": [],
              "unsupported_asset_reference_count": 0, "embedded_json_shapes": [],
              "api_operation_reference_hints": [], "sportradar_host_reference_hints": [],
              "gismo_reference_present": False,
              "signed_query_reference_present": False, "javascript_executed": False,
              "api_requests_made": 0, "admitted_rows": 0}
    try:
        text = body.decode("utf-8")
        if is_script:
            scripts = [{"json": False, "text": text}]
        else:
            parser = _DataLoadingHTML(source_url)
            parser.feed(text)
            parser.close()
            if parser.current is not None:
                raise ValueError("unclosed script")
            ranked = _rank_discovery_assets(parser.assets + parser.preloads)
            result["referenced_script_asset_count"] = len(ranked)
            result["script_asset_urls"] = ranked[:16]
            result["unsupported_asset_reference_count"] = parser.unsupported_assets
            scripts = parser.scripts
        # Only script text, never a link/menu labelled with a supposed endpoint.
        combined = "\n".join(s["text"] for s in scripts)
        result["api_operation_reference_hints"] = [op for op in _DISCOVERY_OPERATIONS
            if re.search(r"\b" + re.escape(op) + r"\b", combined)]
        result["runtime_config_reference_hints"] = [name for name in _DISCOVERY_CONFIG_REFERENCES
            if re.search(r"\b" + re.escape(name) + r"\b", combined)]
        result["sportradar_host_reference_hints"] = sorted(set(re.findall(
            r"https://((?:[A-Za-z0-9-]+\.)*sportradar\.com)(?=[/\s\"'?:]|$)", combined)))[:8]
        result["gismo_reference_present"] = bool(re.search(r"\bgismo\b", combined))
        result["signed_query_reference_present"] = bool(re.search(r"[?&]T=", combined))
        for script in scripts:
            if not script["json"]:
                continue
            try:
                data = json.loads(script["text"])
                shape = {"json_type": "object" if isinstance(data, dict) else "array"
                         if isinstance(data, list) else "scalar"}
                if isinstance(data, (dict, list)):
                    shape["entry_count"] = len(data)
                if isinstance(data, dict):
                    shape["recognized_root_fields"] = sorted(_DISCOVERY_FIELDS.intersection(data))
            except (ValueError, RecursionError):
                shape = {"json_type": "invalid_or_unsupported"}
            result["embedded_json_shapes"].append(shape)
    except (ValueError, UnicodeError, RecursionError, AssertionError):
        return {**result, "status": "unsupported_or_malformed_static_payload", "script_asset_urls": []}
    if not is_script:
        result["loader_state"] = inspect_native_loader_state(body, source_url)
    return result


# React Router's documented StreamTransfer framing and vendored turbo-stream v2
# JSON reference format. Nonfinite values/holes remain opaque, not numeric defaults:
# https://github.com/remix-run/react-router/tree/4e6ff03752ac96d0de3e8052d9d9ba3037e45b6d/packages/react-router/vendor/turbo-stream-v2
# No JavaScript evaluation, constructors, plugins, promises, cycles or HTTP replay.
_LOADER_MAX_BYTES = 512 * 1024
_LOADER_MAX_NODES = 40000
_LOADER_UNDEFINED = object()
# Stock v2 wire sentinels, also observed in the page's shipped client decoder.
# Preserve unavailable/nonfinite values distinctly; NEVER substitute 0 or null.
_LOADER_HOLE = object()
_LOADER_NAN = object()
_LOADER_NEGATIVE_INFINITY = object()
_LOADER_POSITIVE_INFINITY = object()
_LOADER_SPECIAL_REFERENCES = {
    -2: _LOADER_NAN, -3: _LOADER_NEGATIVE_INFINITY,
    -6: _LOADER_POSITIVE_INFINITY,
}
_LOADER_SPECIAL_NAMES = {
    id(_LOADER_UNDEFINED): "undefined", id(_LOADER_HOLE): "array_hole",
    id(_LOADER_NAN): "nan", id(_LOADER_NEGATIVE_INFINITY): "negative_infinity",
    id(_LOADER_POSITIVE_INFINITY): "positive_infinity",
}
_LOADER_ENQUEUE = re.compile(
    r"window\s*\.\s*__reactRouterContext\s*\.\s*streamController\s*\.\s*enqueue\s*\(")
_LOADER_KNOWN_ORIGINS = frozenset({
    "https://widgets.fn.sportradar.com", "https://sh.fn.sportradar.com",
    "https://lmt.fn.sportradar.com", "https://mud.sportradar.com",
})


class _LoaderReject(ValueError):
    """Fixed diagnostic enums only; never constructed from source text."""

    def __init__(self, status, reference_failure_kind=None):
        super().__init__(status)
        self.reference_failure_kind = reference_failure_kind


def _loader_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _LoaderReject("duplicate_json_keys")
        result[key] = value
    return result


def _loader_constant(_):
    raise _LoaderReject("nonfinite_json")


def _loader_json(text):
    return json.loads(text, object_pairs_hook=_loader_pairs, parse_constant=_loader_constant)


def _check_loader_tree(value):
    stack = [(value, 0)]
    nodes = 0
    while stack:
        node, depth = stack.pop()
        nodes += 1
        if nodes > _LOADER_MAX_NODES or depth > 64:
            raise _LoaderReject("loader_structure_limit")
        if isinstance(node, float) and not math.isfinite(node):
            raise _LoaderReject("nonfinite_json")
        children = node.values() if isinstance(node, dict) else node if isinstance(node, list) else ()
        stack.extend((child, depth + 1) for child in children)


def _unpack_loader_v2(values):
    """Bounded memoized graph decoder; references are never copied exponentially."""
    if not isinstance(values, list) or not values or len(values) > 20000:
        raise _LoaderReject("unsupported_reference_graph")
    memo, active = {}, set()
    edges = 0

    def resolve(index, depth=0):
        nonlocal edges
        edges += 1
        if edges > 100000 or depth > 64:
            raise _LoaderReject("loader_structure_limit")
        if type(index) is not int:
            raise _LoaderReject("invalid_reference", "noninteger_reference")
        if index == -5:
            return None
        if index == -7:
            return _LOADER_UNDEFINED
        if index == -4:
            return -0.0
        if index in _LOADER_SPECIAL_REFERENCES:
            return _LOADER_SPECIAL_REFERENCES[index]
        if not 0 <= index < len(values):
            reason = ("array_hole_outside_array" if index == -1 else
                      "unknown_negative_reference" if index < 0 else "reference_out_of_range")
            raise _LoaderReject("invalid_reference", reason)
        if index in active:
            raise _LoaderReject("cyclic_reference_graph")
        if index in memo:
            return memo[index]
        active.add(index)
        node = values[index]
        if isinstance(node, dict):
            result = {}
            for key, ref in node.items():
                if re.fullmatch(r"_(?:0|[1-9]\d{0,5})", key) is None:
                    raise _LoaderReject("unsupported_reference_graph")
                name = resolve(int(key[1:]), depth + 1)
                if not isinstance(name, str) or name in result:
                    raise _LoaderReject("invalid_reference_key")
                result[name] = resolve(ref, depth + 1)
        elif isinstance(node, list):
            if node and isinstance(node[0], str):
                raise _LoaderReject("unsupported_tagged_or_deferred_value")
            # HOLE is valid only in array slots. Distinct from undefined/null,
            # retaining positions without creating false zero-valued statistics.
            result = [_LOADER_HOLE if type(ref) is int and ref == -1 else resolve(ref, depth + 1)
                      for ref in node]
        else:
            result = node
        active.remove(index)
        memo[index] = result
        return result

    return resolve(0)


def _summarize_loader_state(state):
    if not isinstance(state, dict) or not isinstance(state.get("loaderData"), dict):
        raise _LoaderReject("loader_state_structure_unresolved")
    loaders = state["loaderData"]
    root = loaders.get("root")
    context = root.get("cctx") if isinstance(root, dict) else None
    context = context if isinstance(context, dict) else {}
    origin = None
    base = context.get("fishnetUrl")
    if isinstance(base, str) and len(base) <= 256 and not any(ord(c) <= 32 for c in base):
        try:
            parsed = urlsplit(base)
        except ValueError:
            parsed = urlsplit("")
        # Exact known public origins only; never export userinfo, paths or queries.
        candidate = "https://" + (parsed.netloc or "")
        if (candidate in _LOADER_KNOWN_ORIGINS and parsed.scheme == "https"
                and parsed.path in {"", "/"} and not parsed.query and not parsed.fragment):
            origin = candidate
    token = context.get("fishnetToken")
    alias = context.get("fishnetClientAlias")
    token_present = (isinstance(token, str) and 0 < len(token) <= 8192
                     and all(33 <= ord(c) <= 126 for c in token))
    alias_valid = isinstance(alias, str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", alias) is not None
    brand_bound = context.get("clientId") == "sportpesa"
    language_bound = context.get("language") == "en"
    counts = dict.fromkeys(("doc0_data_envelopes", "match", "teams", "results", "standings", "tables", "queries"), 0)
    stack, seen = [(loaders, 0)], set()
    specials = dict.fromkeys((*_LOADER_SPECIAL_NAMES.values(), "negative_zero"), 0)
    nodes = 0
    while stack:
        node, depth = stack.pop()
        nodes += 1
        if nodes > 100000 or depth > 64:
            raise _LoaderReject("loader_structure_limit")
        special = _LOADER_SPECIAL_NAMES.get(id(node))
        if special:
            specials[special] += 1
        elif isinstance(node, float) and node == 0 and math.copysign(1, node) < 0:
            specials["negative_zero"] += 1
        if not isinstance(node, (dict, list)) or id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, dict):
            for key in counts:
                if key != "doc0_data_envelopes" and key in node:
                    counts[key] += 1
            doc = node.get("doc")
            if isinstance(doc, list) and doc and isinstance(doc[0], dict) and "data" in doc[0]:
                counts["doc0_data_envelopes"] += 1
            stack.extend((child, depth + 1) for child in node.values())
        else:
            stack.extend((child, depth + 1) for child in node)
    return {"loader_route_count": len(loaders), "root_context_present": bool(context),
            "page_loader_errors_present": state.get("errors") not in (None, _LOADER_UNDEFINED),
            "feed_config": {"feed_origin": origin,
                "client_brand_bound": brand_bound, "language_bound": language_bound,
                "client_alias_has_supported_syntax": bool(alias_valid),
                "token_present_nonempty_text": token_present,
                "syntactically_complete": bool(origin and alias_valid and token_present and brand_bound and language_bound)},
            "payload_structure_counts": counts, "wire_special_value_counts": specials}


# Receipt vocabulary only: never print arbitrary provider keys, route names,
# query keys/hashes, strings, IDs or values. These names describe candidates,
# NOT an asserted StatsHub record schema or authority to admit records.
_LOADER_SECTIONS = frozenset({"match", "teams", "results", "standings", "tables", "queries"})
_LOADER_SHAPE_KEYS = _LOADER_SECTIONS | frozenset({
    "data", "state", "dehydratedState", "cache", "doc", "home", "away",
    "id", "_id", "uid", "matchId", "eventId", "teamId", "seasonId", "tournamentId",
    "season", "tournament", "competition", "competitionId", "name", "title",
    "date", "time", "kickoff", "kickoff_utc", "startTime", "updatedAt", "dataUpdatedAt",
    "_dt", "uts", "tz", "dateiso", "status", "period", "periods", "score",
    "FT", "HT", "AP", "AET", "fulltime", "halftime", "regularTime",
    "played", "wins", "draws", "losses", "points", "rank", "rows", "total",
    "goalsFor", "goalsAgainst", "value", "_dob", "_maxage",
})
_LOADER_PRIVATE_BRANCHES = frozenset({
    "cctx", "errors", "actiondata", "querykey", "queryhash", "meta",
    "token", "fishnettoken", "authorization", "credentials", "headers", "cookie",
})
_LOADER_ID_FIELDS = frozenset({
    "id", "_id", "uid", "matchId", "eventId", "teamId", "seasonId",
    "tournamentId", "competitionId",
})
_LOADER_TIME_FIELDS = frozenset({
    "date", "time", "kickoff", "kickoff_utc", "startTime", "updatedAt", "dateiso",
})
_LOADER_SCORE_FIELDS = frozenset({"home", "away", "score", "value"})


def _loader_value_kind(value):
    special = _LOADER_SPECIAL_NAMES.get(id(value))
    if special:
        return special
    if value is None:
        return "null"
    return {dict: "object", list: "array", str: "text", bool: "boolean",
            int: "integer", float: "number"}.get(type(value), "unsupported")


def _loader_positive_id(value):
    # No bool/float coercion, signs, zero, leading zero, or default identities.
    return ((type(value) is int and 0 < value < 10**12)
            or (isinstance(value, str) and re.fullmatch(r"[1-9]\d{0,11}", value) is not None))


def _loader_section_evidence(section, value, requested_id):
    """Bounded sampled shape and field syntax; no values or semantic validation.

    List samples are explicit, not representative record counts. No score period,
    team pairing, epoch unit, competition or season semantics is inferred here.
    """
    shape, pending, seen = [], [(value, (), 0)], set()
    truncated = False
    while pending and len(shape) < 48:
        node, path, depth = pending.pop()
        entry = {"path": list(path), "kind": _loader_value_kind(node)}
        if isinstance(node, (dict, list)):
            if id(node) in seen:
                entry["shared_reference"] = True
                shape.append(entry)
                continue
            seen.add(id(node))
            if isinstance(node, dict):
                entry["field_count"] = len(node)
                entry["unlisted_field_count"] = sum(k not in _LOADER_SHAPE_KEYS for k in node)
                children = [(k, v) for k, v in node.items() if k in _LOADER_SHAPE_KEYS]
                opaque = [v for k, v in node.items()
                          if k not in _LOADER_SHAPE_KEYS
                          and k.casefold() not in _LOADER_PRIVATE_BRANCHES]
                entry["unlisted_sampled_field_count"] = min(3, len(opaque)) if depth < 4 else 0
                children.extend(("opaque", v) for v in opaque[:3])
                truncated |= len(opaque) > 3
            else:
                entry["length"] = len(node)
                entry["sampled_item_count"] = min(3, len(node)) if depth < 4 else 0
                children = [("[]", v) for v in node[:3]]
                truncated |= len(node) > 3
            if depth < 4:
                pending.extend((v, (*path, k), depth + 1) for k, v in reversed(children))
            else:
                truncated |= bool(children)
        elif path:
            key = path[-1]
            if key in _LOADER_ID_FIELDS:
                entry["positive_decimal_id_syntax"] = _loader_positive_id(node)
                if section == "match" and len(path) == 1 and key in {"id", "_id", "matchId", "eventId"}:
                    entry["equals_requested_event_id"] = (_loader_positive_id(node)
                                                          and str(node) == requested_id)
            if key in _LOADER_TIME_FIELDS:
                # Numeric epochs and wall clocks stay unresolved, not assumed UTC.
                entry["explicit_zone_timestamp_syntax"] = (
                    isinstance(node, str) and len(node) <= 128
                    and parse_zoned_timestamp(node) is not None)
            if section == "results" and key in _LOADER_SCORE_FIELDS:
                entry["nonnegative_integer_score_syntax"] = type(node) is int and 0 <= node <= 999
        shape.append(entry)
    return {"section": section, "shape": shape,
            "shape_truncated_or_sampled": bool(truncated or pending)}


def _inspect_loader_payload_evidence(state, source_url):
    """Locate embedded candidates, excluding runtime credentials and query keys.

    Private loader state stays inside this call. Opaque ancestry is made explicit
    rather than exporting unknown names or asserting that a query belongs to the
    requested event. Even matching IDs are only lexical evidence, never binding.
    """
    requested_id = source_url.removesuffix("/statistics").rsplit("/", 1)[-1]
    loaders = state["loaderData"]
    pending = [(value, ("route",), 0) for value in reversed(list(loaders.values()))]
    seen, sections, visited = set(), [], 0
    truncated = False
    while pending:
        node, path, depth = pending.pop()
        visited += 1
        if visited > 100000 or depth > 64:
            raise _LoaderReject("loader_structure_limit")
        if not isinstance(node, (dict, list)) or id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, list):
            pending.extend((v, (*path, "[]")[-12:], depth + 1) for v in reversed(node))
            continue
        for key, value in node.items():
            if key.casefold() in _LOADER_PRIVATE_BRANCHES:
                continue
            child_path = (*path, key if key in _LOADER_SHAPE_KEYS else "opaque")[-12:]
            if key in _LOADER_SECTIONS:
                if len(sections) < 24:
                    sections.append({"location": list(child_path),
                                     **_loader_section_evidence(key, value, requested_id)})
                else:
                    truncated = True
            pending.append((value, child_path, depth + 1))
    return {"status": "candidate_shape_and_field_syntax_only", "sections": sections,
            "section_limit_reached": truncated,
            "record_schema_verified": False, "fixture_identity_verified": False,
            "team_competition_season_binding_verified": False,
            "regulation_periods_verified": False, "freshness_verified": False,
            "collection_permission_verified": False}


def inspect_native_loader_state(body: bytes, source_url: str) -> dict:
    """Capture/decode supported embedded loader data, exporting a safe validation receipt.

    Not a StatsHub payload adapter. Decoded loader/config data is local to this
    call, never returned, persisted, executed or used to construct requests.
    Candidate payload shapes/field syntax are not a verified native record schema.
    """
    validate_context_url(source_url)
    if not isinstance(body, bytes) or len(body) > _NATIVE_LIMIT:
        raise ValueError("invalid native loader bytes")
    result = {"evidence_kind": "native_embedded_loader_state_inspection",
              "status": "no_supported_transfer_found", "serialization_format": None,
              "transfer_chunk_count": 0, "decoded_loader_state_count": 0,
              "decoded_context_row_count": 0, "admitted_rows": 0,
              "api_requests_made": 0, "javascript_executed": False,
              "fixture_binding_status": "not_verified", "kickoff_utc": None,
              "field_validation_status": "native_loader_fixture_not_available"}
    try:
        parser = _DataLoadingHTML(source_url)
        parser.feed(body.decode("utf-8"))
        parser.close()
        if parser.current is not None:
            raise _LoaderReject("incomplete_html_script")
        chunks, direct = [], []
        closed = False
        for script in parser.scripts:
            if not script["loader_eligible"]:
                continue
            text = script["text"].strip()
            if script["loader_json"]:
                if len(text.encode("utf-8")) > _LOADER_MAX_BYTES:
                    raise _LoaderReject("loader_byte_limit")
                data = _loader_json(text)
                _check_loader_tree(data)
                if isinstance(data, dict) and "loaderData" in data:
                    direct.append(data)
            elif script["loader_executable"] and _LOADER_ENQUEUE.search(text):
                while text:
                    call = _LOADER_ENQUEUE.match(text)
                    if call is None or closed:
                        raise _LoaderReject("unsupported_transfer_script")
                    tail = text[call.end():].lstrip()
                    value, end = json.JSONDecoder().raw_decode(tail)
                    if not isinstance(value, str):
                        raise _LoaderReject("transfer_argument_not_json_string")
                    tail = tail[end:].lstrip()
                    ending = re.match(r"\)\s*;", tail)
                    if ending is None:
                        raise _LoaderReject("unsupported_transfer_script")
                    chunks.append(value)
                    if len(chunks) > 64 or sum(len(c.encode("utf-8")) for c in chunks) > _LOADER_MAX_BYTES:
                        raise _LoaderReject("loader_byte_limit")
                    text = tail[ending.end():].strip()
            elif script["loader_executable"] and re.fullmatch(
                    r"window\.__reactRouterContext\.streamController\.close\(\);", text):
                if closed:
                    raise _LoaderReject("ambiguous_loader_state")
                closed = True
        result["transfer_chunk_count"] = len(chunks)
        if len(direct) > 1 or (direct and chunks):
            raise _LoaderReject("ambiguous_loader_state")
        if chunks:
            if not closed:
                raise _LoaderReject("incomplete_loader_stream")
            result["serialization_format"] = "react_router_turbo_stream_v2_json_subset"
            data = _loader_json("".join(chunks))  # Reject deferred/multiple frames, never stitch promises.
            _check_loader_tree(data)
            state = _unpack_loader_v2(data)
        elif direct:
            result["serialization_format"] = "application_json_loader_data"
            state = direct[0]
        else:
            return result
        summary = _summarize_loader_state(state)
        return {**result, **summary,
                "payload_evidence": _inspect_loader_payload_evidence(state, source_url),
                "status": "decoded_supported_loader_state",
                "decoded_loader_state_count": 1}
    except _LoaderReject as error:
        failure = {**result, "status": str(error)}
        if error.reference_failure_kind is not None:
            # Category only, never an index, field name, value or source snippet.
            failure["reference_failure_kind"] = error.reference_failure_kind
        return failure
    except (ValueError, UnicodeError, RecursionError, AssertionError):
        return {**result, "status": "invalid_or_unsupported_loader_serialization"}
