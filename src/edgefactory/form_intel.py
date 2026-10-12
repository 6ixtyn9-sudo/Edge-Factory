"""Offline form/H2H features from the committed results archives — no network.

The own-card capture already retains each priced fixture's page observations —
the H2H list (dated scores and the historical closing 1x2 odds), the two
labelled last-results blocks and the league table — and nothing read them: the
only consumers were a capture-side counter and the localdata pruner. This
module is the reader. It works only on what is already on disk:

    localdata/betexplorer_results_YYYY-MM.csv.gz   monthly results archive
                                                   (date, league, full-time and
                                                   half-time score, event id)
    localdata/settled_results.json                 the settlement path's
                                                   90-day result window

Both are needed: the monthly files stop where they are most recent (their last
month is nearly empty), while the settlement window reaches back only 90 days;
neither alone covers the fixtures the enhancement lane actually settled.

Rules this module holds itself to:

* **No lookahead.** A feature for a fixture dated D is computed from matches
  dated strictly before D, so a match's own result can never enter its own
  features. The leak test regenerates a historical row, flips its score and
  shows the row's own features unmoved (while later fixtures' features move).
* **Coverage is output, not an assumption.** A team with fewer than
  ``MIN_HISTORY`` prior matches reports ``insufficient_history``; callers see
  the count instead of a thin number.
* **No magic constants.** Rates are Laplace-smoothed ((hits + 1) / (n + 2)) and
  combined as an equal-weight mean of the available components (each side's
  own form, plus the pair's H2H record once it has ``H2H_MIN_MEETINGS``
  meetings). Nothing here is fitted, tuned or thresholded on outcomes.
* **Nothing is priced.** This module never touches odds, floors, or the money
  path; prices stay the only thing that sets value.
"""
from __future__ import annotations

import csv
import gzip
import json
from bisect import bisect_left
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .identity import (canonical_league_key, source_team_key, squad_marker_mismatch,
                       squad_markers)
from .util import norm_team

RESULTS_GLOB = "betexplorer_results_*.csv.gz"
SETTLED_RESULTS = "settled_results.json"
FORM_WINDOWS = (5, 10)
MIN_HISTORY = 5
H2H_MIN_MEETINGS = 3

# Enhancement market -> ("over" total-goals line | "btts"). Markets outside this
# map (team totals, unders) are deliberately unsupported here: the registry's
# settled population is these four families plus three singletons, and a
# half-guessed outcome would be worse than an explicit "unsupported_market".
MARKET_OUTCOMES: Mapping[str, tuple[str, float | None]] = {
    "match_over_15": ("over", 1.5),
    "match_over_25": ("over", 2.5),
    "match_over_35": ("over", 3.5),
    "match_over_45": ("over", 4.5),
    "btts_yes": ("btts", None),
}


def goal_market_hit(hs: int, gs: int, market: str) -> bool | None:
    """Whether a finished match hits the market; None when unsupported."""
    spec = MARKET_OUTCOMES.get(market)
    if spec is None:
        return None
    outcome, line = spec
    if outcome == "over":
        return (int(hs) + int(gs)) > float(line)  # type: ignore[arg-type]
    if outcome == "btts":
        return int(hs) > 0 and int(gs) > 0
    return None


def _result_row(raw: Mapping[str, Any], *, source: str) -> dict | None:
    try:
        hs, gs = int(raw.get("hs")), int(raw.get("gs"))
    except (TypeError, ValueError):
        return None
    if hs < 0 or gs < 0:
        return None
    day = str(raw.get("date") or "")[:10]
    home, away = str(raw.get("home") or ""), str(raw.get("away") or "")
    if len(day) != 10 or not norm_team(home) or not norm_team(away):
        return None
    return {"date": day, "home": home, "away": away, "hs": hs, "gs": gs,
            "league": str(raw.get("league") or ""), "source": source}


def _settled_row(raw: Mapping[str, Any]) -> dict | None:
    return _result_row(raw, source="settled_results")


def _row_key(row: Mapping[str, Any]) -> tuple[str, str, str, int, int]:
    """Identity of one result: date, both clubs' canonical keys, and the score.

    ``source_team_key`` is the repository's own identity for exactly this job
    (identity.py: the width-9 ``norm_team`` "makes unrelated teams collide on
    one voter key ... Colliding keys mis-attach wrong-match evidence").
    Measured in localdata (handoff/round5_form_h2h_2026-10-12/
    w3_identity_census.txt): the width-9 dedup key merges 4,106 same-date,
    same-score groups whose canonical identities differ — 4,531 rows beyond
    the first — so a senior side and its own women's/U20 edition that share a
    key, a date and a score ("Vitoria Guimaraes W 2-1 Braga W" vs "Vitoria
    Guimaraes 2-1 Braga") would share one stored row. The canonical key keeps
    squad distinguishers and applies the curated same-club aliases, so the two
    sources' spelling of one fixture still collapses (subject to the score).
    """
    return (row["date"], source_team_key(row["home"]), source_team_key(row["away"]),
            int(row["hs"]), int(row["gs"]))


def _same_squad(name: object, query: object) -> bool:
    """Whether a row's side can be the queried side of the same club.

    The canonical key keeps squad distinguishers ("coventryu21",
    "arsenalw") and the curated alias table deliberately maps a few reserve
    pairs onto one identity ("FC Porto B" <-> "Porto II"); the repository's
    own veto for the latter is ``squad_marker_mismatch``, applied on the side
    that matched. It compares squad CLASSES, not spellings, so a senior side
    never reads a reserve's, an age-grade's or a women's rows.
    """
    return not squad_marker_mismatch(name, query)


@dataclass
class ResultsArchive:
    """Dated results with the team and pair lookups the features need."""

    rows: list[dict]
    by_team: dict[str, list[dict]] = field(default_factory=dict)
    by_pair: dict[tuple[str, str], list[dict]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        team_idx: dict[str, list[dict]] = defaultdict(list)
        pair_idx: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in self.rows:
            hk, ak = source_team_key(row["home"]), source_team_key(row["away"])
            team_idx[hk].append(row)
            team_idx[ak].append(row)
            pair_idx[tuple(sorted((hk, ak)))].append(row)
        for bucket in list(team_idx.values()) + list(pair_idx.values()):
            bucket.sort(key=lambda r: (r["date"], r["home"], r["away"]))
        self.by_team = dict(team_idx)
        self.by_pair = dict(pair_idx)

    # -- lookups ---------------------------------------------------------
    def team_rows(self, team: str) -> list[dict]:
        """Rows for the club: one per date-and-scoreline.

        The two sources (and the settlement window's own aggregation) record
        one fixture under several spellings ("Sabah" / "Sabah Baku" / "Sabah
        FA"); where the curated alias table cannot join those spellings the
        club's history would hold the same match two or three times and every
        last-N window would be false. A club appears once per date with a
        given scoreline, so the repeats collapse here. The trade-off is
        stated: two genuinely different matches fall on one date with the
        same scoreline only through a canonical-key merge of two clubs
        ("FC Barcelona" and "Barcelona SC" share a key), and a bucket that
        wrong is polluted with or without the collapse.
        """
        key = source_team_key(team)
        out: list[dict] = []
        seen: set[tuple[str, int, int]] = set()
        for row in self.by_team.get(key, []):
            if not _team_side_matches(row, key, team):
                continue
            scored, conceded = _own_goals(row, key)
            signature = (row["date"], scored, conceded)
            if signature in seen:
                continue
            seen.add(signature)
            out.append(row)
        return out

    def squad_excluded(self, team: str) -> list[dict]:
        """Rows under the same canonical key that the squad guard keeps out."""
        key = source_team_key(team)
        return [r for r in self.by_team.get(key, [])
                if not _team_side_matches(r, key, team)]

    def prior_rows(self, team: str, as_of: str) -> list[dict]:
        """Every row for the team dated strictly before ``as_of``."""
        rows = self.team_rows(team)
        days = [r["date"] for r in rows]
        return rows[:bisect_left(days, as_of)]

    def pair_rows(self, home: str, away: str, as_of: str) -> list[dict]:
        """Meetings of the pair (either orientation) dated before ``as_of``."""
        hk, ak = source_team_key(home), source_team_key(away)
        rows = [r for r in self.by_pair.get(tuple(sorted((hk, ak))), [])
                if _pair_matches(r, hk, ak, home, away)]
        days = [r["date"] for r in rows]
        return rows[:bisect_left(days, as_of)]


def _own_goals(row: Mapping[str, Any], key: str) -> tuple[int, int]:
    """The row's scoreline from ``key``'s side: scored, then conceded."""
    if source_team_key(row["home"]) == key:
        return int(row["hs"]), int(row["gs"])
    return int(row["gs"]), int(row["hs"])


def _team_side_matches(row: Mapping[str, Any], key: str, team: object) -> bool:
    if source_team_key(row["home"]) == key:
        return _same_squad(row["home"], team)
    if source_team_key(row["away"]) == key:
        return _same_squad(row["away"], team)
    return False


def _pair_matches(row: Mapping[str, Any], hk: str, ak: str,
                  home: object, away: object) -> bool:
    if source_team_key(row["home"]) == hk and source_team_key(row["away"]) == ak:
        return _same_squad(row["home"], home) and _same_squad(row["away"], away)
    if source_team_key(row["home"]) == ak and source_team_key(row["away"]) == hk:
        return _same_squad(row["home"], away) and _same_squad(row["away"], home)
    return False


def load_archive(localdata: str | Path) -> ResultsArchive:
    """Read every committed result we can see into one dated archive.

    The monthly files are read first so their league labels win the dedup
    against the settlement window's rows (same date + teams + score). Rows
    that cannot be a played result (missing or negative score) are skipped at
    the boundary. The indexes and the row identity are both keyed by the
    canonical ``source_team_key`` — see ``_row_key`` — so a spelling variant
    the curated alias table joins collapses into one fixture, while a
    reserve/women's edition that merely shares the width-9 ``norm_team``
    bucket is kept.
    """
    root = Path(localdata)
    rows: dict[tuple[str, str, str], dict] = {}
    for path in sorted(root.glob(RESULTS_GLOB)):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            for raw in csv.DictReader(fh):
                row = _result_row(raw, source=path.name)
                if row is not None:
                    rows.setdefault(_row_key(row), row)
    settled = root / SETTLED_RESULTS
    if settled.exists():
        doc = json.loads(settled.read_text(encoding="utf-8"))
        for raw in doc.get("rows") or []:
            row = _settled_row(raw)
            if row is not None:
                rows.setdefault(_row_key(row), row)
    return ResultsArchive(sorted(rows.values(), key=_row_key))


# -- per-team features -----------------------------------------------------

def _hits_and_n(matches: Sequence[Mapping[str, Any]], market: str) -> tuple[int, int]:
    hits = 0
    seen = 0
    for row in matches:
        hit = goal_market_hit(row["hs"], row["gs"], market)
        if hit is None:
            continue
        seen += 1
        hits += 1 if hit else 0
    return hits, seen


def _laplace(hits: int, n: int) -> float | None:
    if n <= 0:
        return None
    return (hits + 1) / (n + 2)


def _match_view(row: Mapping[str, Any], key: str) -> dict:
    home_key = source_team_key(row["home"])
    venue = "home" if home_key == key else "away"
    scored, conceded = (row["hs"], row["gs"]) if venue == "home" else (row["gs"], row["hs"])
    return {"date": row["date"], "opponent": row["away"] if venue == "home" else row["home"],
            "venue": venue, "scored": scored, "conceded": conceded,
            "league": row["league"]}


def team_form(archive: ResultsArchive, team: str, as_of: str, *, window: int = 10) -> dict:
    """One team's record over its last ``window`` matches before ``as_of``."""
    key = source_team_key(team)
    all_prior = archive.prior_rows(team, as_of)
    prior = all_prior[-window:]
    wins = draws = losses = gf = ga = 0
    over15 = over25 = over35 = btts = 0
    home_n = home_pts = away_n = away_pts = 0
    for row in prior:
        view = _match_view(row, key)
        if view["venue"] == "home":
            home_n += 1
        else:
            away_n += 1
        if view["scored"] > view["conceded"]:
            wins += 1
            pts = 3
        elif view["scored"] == view["conceded"]:
            draws += 1
            pts = 1
        else:
            losses += 1
            pts = 0
        if view["venue"] == "home":
            home_pts += pts
        else:
            away_pts += pts
        gf += view["scored"]
        ga += view["conceded"]
        total = row["hs"] + row["gs"]
        over15 += 1 if total > 1.5 else 0
        over25 += 1 if total > 2.5 else 0
        over35 += 1 if total > 3.5 else 0
        btts += 1 if (row["hs"] > 0 and row["gs"] > 0) else 0
    n = len(prior)
    points = wins * 3 + draws
    return {
        "team": team, "as_of": as_of, "window": window, "n": n,
        "prior_n": len(all_prior),
        "squad_excluded": len(archive.squad_excluded(team)),
        "insufficient_history": len(all_prior) < MIN_HISTORY,
        "wins": wins, "draws": draws, "losses": losses,
        "goals_for": gf, "goals_against": ga, "points": points,
        "ppg": round(points / n, 3) if n else None,
        "over_15_hits": over15, "over_25_hits": over25, "over_35_hits": over35,
        "btts_hits": btts,
        "home_split": {"n": home_n, "points": home_pts},
        "away_split": {"n": away_n, "points": away_pts},
        "matches": [_match_view(row, key) for row in prior],
    }


def pair_history(archive: ResultsArchive, home: str, away: str, as_of: str, *,
                 window: int = 10) -> dict:
    """The pair's meetings before ``as_of``, read from the fixture's home side."""
    hk = source_team_key(home)
    prior = archive.pair_rows(home, away, as_of)[-window:]
    home_wins = draws = away_wins = 0
    gf_home = gf_away = 0
    over15 = over25 = over35 = btts = 0
    for row in prior:
        view = _match_view(row, hk)
        gf_home += view["scored"]
        gf_away += view["conceded"]
        if view["scored"] > view["conceded"]:
            home_wins += 1
        elif view["scored"] == view["conceded"]:
            draws += 1
        else:
            away_wins += 1
        total = row["hs"] + row["gs"]
        over15 += 1 if total > 1.5 else 0
        over25 += 1 if total > 2.5 else 0
        over35 += 1 if total > 3.5 else 0
        btts += 1 if (row["hs"] > 0 and row["gs"] > 0) else 0
    return {
        "home": home, "away": away, "as_of": as_of, "window": window,
        "n": len(prior), "home_wins": home_wins, "draws": draws,
        "away_wins": away_wins, "goals_for_home": gf_home,
        "goals_for_away": gf_away,
        "over_15_hits": over15, "over_25_hits": over25, "over_35_hits": over35,
        "btts_hits": btts,
        "meetings": [{"date": r["date"], "home": r["home"], "away": r["away"],
                      "hs": r["hs"], "gs": r["gs"], "league": r["league"]}
                     for r in prior],
    }


def _market_hits(form: Mapping[str, Any], market: str) -> tuple[int, int]:
    field_name = {"match_over_15": "over_15_hits", "match_over_25": "over_25_hits",
                  "match_over_35": "over_35_hits", "match_over_45": "over_45_hits",
                  "btts_yes": "btts_hits"}.get(market)
    if field_name is None or field_name not in form:
        return 0, 0
    return int(form[field_name]), int(form["n"])


def form_market_probability(archive: ResultsArchive, home: str, away: str, as_of: str,
                            market: str, *, window: int = 10) -> dict:
    """A Laplace-smoothed, equal-weight form/H2H estimate for one market.

    Components: the home side's own rate, the away side's own rate, and (only
    once the pair has ``H2H_MIN_MEETINGS`` prior meetings) the pair's rate.
    Unsupported markets and teams with no prior matches return ``p=None`` with
    a reason instead of a fabricated number.
    """
    spec = MARKET_OUTCOMES.get(market)
    if spec is None:
        return {"market": market, "home": home, "away": away, "as_of": as_of,
                "p": None, "reason": "unsupported_market", "components": {},
                "insufficient_history": True}
    if market == "match_over_45":
        # No archive market field for 4.5; read it straight from the rows.
        home_hits, home_n = _hits_and_n(archive.prior_rows(home, as_of)[-window:], market)
        away_hits, away_n = _hits_and_n(archive.prior_rows(away, as_of)[-window:], market)
        h2h_hits, h2h_n = _hits_and_n(archive.pair_rows(home, away, as_of)[-window:], market)
    else:
        home_form = team_form(archive, home, as_of, window=window)
        away_form = team_form(archive, away, as_of, window=window)
        history = pair_history(archive, home, away, as_of, window=window)
        home_hits, home_n = _market_hits(home_form, market)
        away_hits, away_n = _market_hits(away_form, market)
        h2h_hits, h2h_n = _market_hits(history, market)
    home_prior = len(archive.prior_rows(home, as_of))
    away_prior = len(archive.prior_rows(away, as_of))
    components = {"home_form": _laplace(home_hits, home_n),
                  "away_form": _laplace(away_hits, away_n),
                  "h2h": _laplace(h2h_hits, h2h_n) if h2h_n >= H2H_MIN_MEETINGS else None}
    available = [p for p in components.values() if p is not None]
    thin = min(home_prior, away_prior) < MIN_HISTORY
    p = None if (thin or not available) else sum(available) / len(available)
    return {"market": market, "home": home, "away": away, "as_of": as_of,
            "p": p, "components": components,
            "windows": {"home_n": home_n, "away_n": away_n, "h2h_n": h2h_n},
            "insufficient_history": thin,
            "reason": ("insufficient_history" if thin else
                       None if p is not None else "no_prior_matches")}


# -- coverage --------------------------------------------------------------

def squad_class(team: object) -> str:
    """The squad class a team name carries: ``senior``, else its marker classes.

    A thin side is often thin because it is a reserve/youth/women's side the
    archive covers far less, so a coverage verdict names the class rather than
    leaving the reader guessing (2026-10-12 adjudication, A-3).
    """
    markers = sorted(squad_markers(team))
    return "+".join(markers) if markers else "senior"


def coverage(archive: ResultsArchive, fixtures: Iterable[Mapping[str, Any]], *,
             window: int = MIN_HISTORY) -> dict:
    """How many fixtures have at least ``window`` prior matches for both sides.

    Returned per month and per league, because the two archives have different
    depth: a fixture can look covered in one month and starved in another.
    Sides below ``window`` are listed with their squad class, so an
    ``insufficient_history`` verdict on a reserve side is explained rather than
    mysterious, and a slice built for floors can exclude them knowingly.
    """
    by_month: dict[str, dict[str, int]] = {}
    by_league: dict[str, dict[str, int]] = {}
    total = sufficient = 0
    thin_sides: list[dict] = []
    for fixture in fixtures:
        day = str(fixture.get("date") or "")
        league = str(fixture.get("league") or "unknown")
        home, away = str(fixture.get("home") or ""), str(fixture.get("away") or "")
        home_n = len(archive.prior_rows(home, day))
        away_n = len(archive.prior_rows(away, day))
        for team, priors in ((home, home_n), (away, away_n)):
            if priors < window:
                thin_sides.append({"date": day, "team": team, "priors": priors,
                                   "class": squad_class(team), "league": league})
        ok = min(home_n, away_n) >= window
        total += 1
        sufficient += 1 if ok else 0
        month = day[:7]
        for bucket, name in ((by_month, month), (by_league, league)):
            entry = bucket.setdefault(name, {"total": 0, "sufficient": 0,
                                             "insufficient": 0})
            entry["total"] += 1
            entry["sufficient" if ok else "insufficient"] += 1
    return {"total": total, "sufficient": sufficient,
            "insufficient": total - sufficient, "window": window,
            "insufficient_sides": thin_sides,
            "non_senior_sides": sum(1 for s in thin_sides if s["class"] != "senior"),
            "by_month": dict(sorted(by_month.items())),
            "by_league": dict(sorted(by_league.items(),
                                     key=lambda kv: (-kv[1]["total"], kv[0])))}


# -- captured page blocks vs the archive (integrity cross-check) -----------

def page_team_rows(page: Mapping[str, Any] | None) -> dict[str, list[dict]]:
    """The captured page's own last-results blocks, keyed by the page's label."""
    out: dict[str, list[dict]] = {}
    for row in (page or {}).get("last_results_rows") or []:
        out.setdefault(str(row.get("label") or ""), []).append(row)
    return out


def page_h2h_rows(page: Mapping[str, Any] | None) -> list[dict]:
    return list((page or {}).get("h2h_rows") or [])


def _archive_row_for(archive: ResultsArchive, team: str, day: str,
                     score: list[int] | None) -> dict | None:
    """The archive's own row for that team/date/score, anywhere in the archive."""
    if score is None:
        return None
    for row in archive.team_rows(team):
        if row["date"] == day and [row["hs"], row["gs"]] == score:
            return row
    return None


def _label_for(blocks: Mapping[str, list[dict]], team: str) -> str | None:
    """The page block belonging to ``team``.

    Canonical equality first. The width-9 fallback is accepted only when it
    names exactly one block: a page whose two sides share the normalised key
    ("Manchester City" / "Manchester Utd") must yield no label rather than
    the opponent's block.
    """
    key = source_team_key(team)
    exact = [label for label in blocks if source_team_key(label) == key]
    if exact:
        return exact[0]
    narrow = norm_team(team)
    loose = [label for label in blocks if norm_team(label) == narrow]
    return loose[0] if len(loose) == 1 else None


def _page_score(row: Mapping[str, Any]) -> list[int] | None:
    score = row.get("score") or []
    if len(score) != 2:
        return None
    try:
        return [int(score[0]), int(score[1])]
    except (TypeError, ValueError):
        return None


def compare_team_window(archive: ResultsArchive, team: str, as_of: str,
                        page_rows: Sequence[Mapping[str, Any]], *, window: int = 5,
                        league: str = "") -> dict:
    """One team's captured block against the archive's last-``window`` rows.

    Every difference gets a named verdict rather than a shrug: a page row the
    archive holds outside the compared window is a window shift (the archive's
    last N differs because it also holds rows the page's league filter hid), a
    page row with no archive counterpart is an archive gap (broken out per
    month, or an unmatched identity when the archive holds no row for that
    spelling at all), an archive row the page omits is a competition-filter
    artefact when its league differs from the fixture's (the page block is
    league-scoped by default), else a reschedule when the page has a nearby
    row, else unexplained.
    """
    archive_rows = archive.prior_rows(team, as_of)[-window:]
    page_seq = list(page_rows)[-window:]
    by_date: dict[str, list[dict]] = defaultdict(list)
    for row in archive_rows:
        by_date[row["date"]].append(row)

    verdicts: list[dict] = []
    matched = 0
    for row in page_seq:
        day = str(row.get("date") or "")
        page_score = _page_score(row)
        entry = {"date": day, "score": page_score, "verdict": "unexplained"}
        candidates = by_date.get(day, [])
        if candidates and page_score is not None:
            same = [c for c in candidates
                    if [c["hs"], c["gs"]] == page_score]
            if same:
                entry["verdict"] = "matched"
                entry["archive"] = {"home": same[0]["home"], "away": same[0]["away"],
                                    "hs": same[0]["hs"], "gs": same[0]["gs"],
                                    "league": same[0]["league"]}
                matched += 1
            else:
                entry["verdict"] = "score_mismatch"
                entry["archive"] = {"home": candidates[0]["home"],
                                    "away": candidates[0]["away"],
                                    "hs": candidates[0]["hs"], "gs": candidates[0]["gs"]}
        else:
            shifted = _archive_row_for(archive, team, day, page_score)
            if shifted is not None:
                entry["verdict"] = "window_shift"
                entry["archive"] = {"home": shifted["home"], "away": shifted["away"],
                                    "hs": shifted["hs"], "gs": shifted["gs"],
                                    "league": shifted["league"]}
            else:
                team_rows = archive.team_rows(team)
                month_rows = [r for r in team_rows if r["date"][:7] == day[:7]]
                entry["verdict"] = ("unmatched_identity" if not team_rows
                                    else "archive_month_gap" if not month_rows
                                    else "archive_gap")
        verdicts.append(entry)

    page_days = {str(r.get("date") or "") for r in page_seq}
    archive_only = []
    for row in archive_rows:
        if row["date"] in page_days:
            continue
        other_league = bool(league) and bool(row["league"]) and \
            canonical_league_key(row["league"]) != canonical_league_key(league)
        nearby = any(abs(_day_index(row["date"]) - _day_index(d)) <= 2
                     for d in page_days if d)
        verdict = ("competition_filter" if other_league else
                   "reschedule" if nearby else "unexplained")
        archive_only.append({"date": row["date"], "home": row["home"], "away": row["away"],
                             "hs": row["hs"], "gs": row["gs"], "league": row["league"],
                             "verdict": verdict})
    return {"team": team, "as_of": as_of, "window": window,
            "page_n": len(page_seq), "archive_n": len(archive_rows),
            "matched": matched, "archive_only": archive_only,
            "verdicts": verdicts}


def _day_index(day: str) -> int:
    """Ordinal index for a YYYY-MM-DD string; missing parts count as zero."""
    try:
        from datetime import date as _date
        y, m, d = (int(part) for part in day.split("-")[:3])
        return _date(y, m, d).toordinal()
    except (TypeError, ValueError):
        return 0


def compare_page_to_archive(archive: ResultsArchive, page: Mapping[str, Any] | None, *,
                            as_of: str, home: str, away: str, league: str = "",
                            window: int = 5) -> dict:
    """The whole block-vs-archive comparison for one fixture."""
    blocks = page_team_rows(page)
    teams: dict[str, Any] = {}
    unmatched = 0
    for team in (home, away):
        label = _label_for(blocks, team)
        if label is None:
            unmatched += 1
            teams[team] = {"team": team, "unmatched_label": True, "page_n": 0}
            continue
        result = compare_team_window(archive, team, as_of, blocks[label],
                                     window=window, league=league)
        result["label"] = label
        teams[team] = result
    return {"as_of": as_of, "home": home, "away": away, "league": league,
            "labels": sorted(blocks), "unmatched_labels": unmatched,
            "teams": teams}


# -- probability metrics (deterministic) -----------------------------------

def brier(pairs: Sequence[tuple[float, bool]]) -> float | None:
    if not pairs:
        return None
    return sum((float(p) - (1.0 if y else 0.0)) ** 2 for p, y in pairs) / len(pairs)


def log_loss(pairs: Sequence[tuple[float, bool]]) -> float | None:
    import math
    if not pairs:
        return None
    total = 0.0
    for p, y in pairs:
        q = min(max(float(p), 1e-15), 1 - 1e-15)
        total += -(math.log(q) if y else math.log(1 - q))
    return total / len(pairs)


def bootstrap_ci(values: Sequence[float], *, resamples: int = 2000, seed: int = 2026,
                  confidence: float = 0.95) -> dict:
    """Percentile bootstrap CI of the mean; deterministic for a fixed seed."""
    import random
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": None, "lo": None, "hi": None}
    rng = random.Random(seed)
    means = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(n):
            total += values[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    lo_i = int((1 - confidence) / 2 * resamples)
    hi_i = min(resamples - 1, int((1 + confidence) / 2 * resamples))
    return {"n": n, "mean": sum(values) / n, "lo": means[lo_i], "hi": means[hi_i],
            "resamples": resamples, "seed": seed}


def paired_bootstrap_delta(pairs_a: Sequence[tuple[float, bool]],
                           pairs_b: Sequence[tuple[float, bool]], *,
                           metric: str = "brier", resamples: int = 2000,
                           seed: int = 2026, confidence: float = 0.95) -> dict:
    """Bootstrap CI of metric(b) - metric(a) over the same fixtures (paired)."""
    import random
    scorer = brier if metric == "brier" else log_loss
    n = min(len(pairs_a), len(pairs_b))
    if n == 0:
        return {"n": 0, "delta": None, "lo": None, "hi": None}
    rng = random.Random(seed)
    deltas = []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        a = scorer([pairs_a[i] for i in idx])
        b = scorer([pairs_b[i] for i in idx])
        deltas.append(float(b) - float(a))
    deltas.sort()
    point = float(scorer(list(pairs_b[:n]))) - float(scorer(list(pairs_a[:n])))
    lo_i = int((1 - confidence) / 2 * resamples)
    hi_i = min(resamples - 1, int((1 + confidence) / 2 * resamples))
    return {"n": n, "delta": point, "lo": deltas[lo_i], "hi": deltas[hi_i],
            "metric": metric, "resamples": resamples, "seed": seed}
