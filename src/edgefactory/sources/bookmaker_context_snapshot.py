"""Pure saved-reader bookmaker context decoder and own-card diagnostic.

SportPesa-branded Sportradar public match pages only. No HTTP, registration,
state writer, odds, probabilities or admission path. Shares existing identity
and timestamp guards. Reader structure is not verified native availability.
"""
from __future__ import annotations

import hashlib
import html
import re
from datetime import UTC, datetime

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
TEAM_URL = re.escape(PREFIX) + r"sport/1/team/([1-9]\d{0,11})\?seasonId=(\d{1,12})&tournamentId=(\d{1,12})"
TEAM_LINK = re.compile(r"\[([^\[\]]{1,240})\]\((" + TEAM_URL + r")\)")
MATCH_LINK = re.compile(r"\[([^\[\]]{1,1600})\]\((" + MATCH_URL.pattern + r")\)")
COLUMNS = ["#", "Team", "P", "W", "D", "L", "GF", "GA", "DIFF", "PTS", "Form"]
MONTH_DATE = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}\b")
HOLDS = (
    "reader_transcription_not_native_response", "collection_permission_unresolved",
    "third_party_supplier_not_independent_bookmaker_data", "absolute_kickoff_unverified",
    "native_context_decoding_unimplemented", "result_periods_not_verified_for_regulation",
    "production_admission_not_implemented", "fixture_not_independently_corroborated",
)


def validate_context_url(value: str) -> str:
    """Known ordinary public match route, fixed tenant; no API/private paths."""
    if not isinstance(value, str) or MATCH_URL.fullmatch(value) is None:
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
        if cells == COLUMNS:
            table = {"label": label, "rows": []}
            tables.append(table)
            if len(tables) > 8:
                raise ValueError("context table limit")
            continue
        if table is None or all(re.fullmatch(r"[-:]+", c) for c in cells):
            continue
        if len(tables) > 8 or len(table["rows"]) >= 40:
            raise ValueError("context table limit")
        if len(cells) != 11 or TEAM_LINK.fullmatch(cells[1]) is None:
            invalid += 1
            continue
        try:
            values = [int(cells[i]) for i in (0, 2, 3, 4, 5, 6, 7, 8, 9)]
        except ValueError:
            invalid += 1
            continue
        rank, played, wins, draws, losses, gf, ga, diff, points = values
        if (not 1 <= rank <= 100 or any(not 0 <= n <= 999 for n in
                (played, wins, draws, losses, gf, ga)) or not -999 <= points <= 999
                or played != wins + draws + losses or diff != gf - ga):
            invalid += 1
            continue
        table["rows"].append({**_team(TEAM_LINK.fullmatch(cells[1])),
                              "rank": rank, "played": played, "wins": wins,
                              "draws": draws, "losses": losses, "goals_for": gf,
                              "goals_against": ga, "goal_difference": diff, "points": points})
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
    if len({p["source_url"] for p in pages}) != len(pages):
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
