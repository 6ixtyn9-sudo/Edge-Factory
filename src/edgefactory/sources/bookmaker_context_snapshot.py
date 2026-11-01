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
import re
from datetime import UTC, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin

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

    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > 40000:
            raise ValueError("discovery node limit")
        attrs = dict(attrs)
        if tag == "script":
            if len(self.scripts) >= 64 or self.current is not None:
                raise ValueError("discovery script limit or nesting")
            self.current = {"json": (attrs.get("type") or "").strip().lower()
                            in {"application/json", "application/ld+json"}, "text": ""}
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
    return result
