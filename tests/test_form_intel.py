"""The offline form/H2H extractor's contract, including the leak discipline.

Every fixture here is synthetic and written into tmp_path: the tests exercise
the same loader/feature/comparator code paths the measurement bundle runs, but
they never read or write the repository's own localdata.
"""
from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import pytest

from edgefactory import form_intel as fi

HEADER = ["date", "kickoff", "country", "league", "home", "away", "hs", "gs",
          "ht_hs", "ht_gs", "match_url", "event_id", "fetched_at"]


def _csv(results, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADER)
        for row in results:
            writer.writerow([row["date"], "12:00", "England", row.get("league", "L1"),
                             row["home"], row["away"], row["hs"], row["gs"],
                             "", "", "", "", "2026-10-01T00:00:00Z"])


def _settled(results, path: Path) -> None:
    path.write_text(json.dumps({"schema": "x", "window_days": 90, "rows": [
        {"date": r["date"], "home": r["home"], "away": r["away"],
         "hs": r["hs"], "gs": r["gs"],
         "outcome": "home" if r["hs"] > r["gs"] else "away" if r["gs"] > r["hs"] else "draw",
         "src": "betexplorer_settled"} for r in results]}), encoding="utf-8")


def _round(day: int, home: str, away: str, hs: int, gs: int, league: str = "L1") -> dict:
    return {"date": f"2026-01-{day:02d}", "home": home, "away": away,
            "hs": hs, "gs": gs, "league": league}


def _archive(tmp_path: Path, monthly, settled=None) -> fi.ResultsArchive:
    _csv(monthly, tmp_path / "betexplorer_results_2026-01.csv.gz")
    if settled is not None:
        _settled(settled, tmp_path / "settled_results.json")
    return fi.load_archive(tmp_path)


# -- loading ---------------------------------------------------------------

def test_loader_reads_both_sources_and_the_monthly_league_label_wins(tmp_path):
    dup = _round(3, "Alpha", "Beta", 2, 1)
    archive = _archive(tmp_path, [dup], [dict(dup, league="STALE")])
    assert len(archive.rows) == 1
    assert archive.rows[0]["league"] == "L1"
    assert archive.rows[0]["source"] == "betexplorer_results_2026-01.csv.gz"


def test_loader_skips_rows_that_cannot_be_a_played_result(tmp_path):
    bad = _round(4, "Alpha", "Beta", 1, 1)
    bad["hs"] = ""
    good = _round(5, "Alpha", "Beta", 1, 1)
    archive = _archive(tmp_path, [bad, good])
    assert [r["date"] for r in archive.rows] == ["2026-01-05"]


def test_loader_keeps_two_squads_that_share_a_normalised_key(tmp_path):
    """The senior and U21 editions of one club can play on the same date.

    ``norm_team`` folds the squad marker away, so a normalised-key identity
    deletes one of the two matches; the canonical ``source_team_key`` keeps
    the marker, and the score keeps same-day same-key results apart.
    """
    senior = _round(2, "Coventry", "Beta", 1, 0)
    reserve = _round(2, "Coventry U21", "Beta", 4, 1)
    archive = _archive(tmp_path, [senior, reserve])
    assert len(archive.rows) == 2
    assert [r["hs"] for r in archive.rows] == [1, 4]


def test_senior_form_never_reads_the_reserve_squads_rows(tmp_path):
    rows = [_round(1, "Coventry", "Beta", 1, 0),
            _round(2, "Coventry U21", "Beta", 4, 1),
            _round(3, "Coventry", "Gamma", 2, 2)]
    archive = _archive(tmp_path, rows)
    form = fi.team_form(archive, "Coventry", "2026-01-04")
    assert form["n"] == 2 and form["goals_for"] == 3
    assert [m["opponent"] for m in form["matches"]] == ["Beta", "Gamma"]
    # the reserve side is a different canonical identity, not a bucket-mate
    # the guard has to filter out; nothing under the senior key is excluded
    assert archive.squad_excluded("Coventry") == []
    assert {r["home"] for r in archive.team_rows("Coventry")} == {"Coventry"}
    # the pair lookup is guarded the same way
    assert len(archive.pair_rows("Coventry", "Beta", "2026-01-04")) == 1


def test_one_fixture_recorded_under_two_spellings_counts_once(tmp_path):
    """Both rows are the one fixture (2026-01-22, Carmarthen Town 2-4 Treowen).

    One comes from each source; the canonical key does not join "Treowen" to
    "Treowen Stars", so without the per-date-scoreline collapse the club's
    history would hold the same match twice and every window would be false.
    """
    rows = [_round(22, "Carmarthen Town", "Treowen", 2, 4),
            _round(22, "Carmarthen Town", "Treowen Stars", 2, 4)]
    archive = _archive(tmp_path, rows)
    assert len(archive.rows) == 2          # the raw union keeps both spellings
    kept = archive.team_rows("Carmarthen Town")
    assert len(kept) == 1 and kept[0]["away"] == "Treowen"


def test_two_scorelines_on_one_date_are_not_collapsed(tmp_path):
    rows = [_round(9, "Alpha", "Beta", 1, 0), _round(9, "Alpha", "Gamma", 2, 0)]
    archive = _archive(tmp_path, rows)
    assert len(archive.team_rows("Alpha")) == 2


def test_two_clubs_that_share_a_normalised_key_never_mix(tmp_path):
    """``norm_team`` truncates to nine characters, so City and United collide.

    identity.py's own ruling is that such collisions mis-attach wrong-match
    evidence; the canonical key keeps the two clubs' histories apart.
    """
    rows = [_round(1, "Manchester City", "Alpha", 3, 0),
            _round(2, "Manchester Utd", "Beta", 1, 0)]
    archive = _archive(tmp_path, rows)
    assert [r["away"] for r in archive.team_rows("Manchester City")] == ["Alpha"]
    form = fi.team_form(archive, "Manchester City", "2026-01-03")
    assert form["n"] == 1 and form["goals_for"] == 3
    assert [r["away"] for r in archive.team_rows("Manchester Utd")] == ["Beta"]


def test_loader_keeps_a_womens_fixture_the_normalised_key_collides_with(tmp_path):
    rows = [_round(2, "Vitoria Guimaraes", "Braga", 2, 1),
            _round(2, "Vitoria Guimaraes W", "Braga W", 2, 1)]
    archive = _archive(tmp_path, rows)
    assert len(archive.rows) == 2
    assert [r["home"] for r in archive.team_rows("Vitoria Guimaraes")] == ["Vitoria Guimaraes"]


def test_curated_alias_spellings_read_as_one_club(tmp_path):
    """The curated table joins "Leeds" and "Leeds United" - not a fuzzy rule."""
    rows = [_round(1, "Leeds", "Alpha", 2, 0), _round(2, "Leeds United", "Beta", 1, 0)]
    archive = _archive(tmp_path, rows)
    assert len(archive.team_rows("Leeds United")) == 2
    assert fi.team_form(archive, "Leeds United", "2026-01-03")["n"] == 2


def test_prior_rows_are_strictly_before_the_fixture_date(tmp_path):
    rows = [_round(1, "Alpha", "Beta", 1, 0), _round(2, "Alpha", "Beta", 2, 0),
            _round(3, "Alpha", "Beta", 3, 0)]
    archive = _archive(tmp_path, rows)
    assert len(archive.prior_rows("Alpha", "2026-01-03")) == 2
    assert len(archive.pair_rows("Alpha", "Beta", "2026-01-03")) == 2


# -- the leak discipline ---------------------------------------------------

def test_a_rows_own_result_never_enters_its_own_features(tmp_path):
    """Flip the row's score: its own features must not move; later ones must."""
    rows = [_round(1, "Alpha", "Beta", 1, 0), _round(2, "Alpha", "Gamma", 2, 2),
            _round(3, "Beta", "Alpha", 0, 1), _round(4, "Alpha", "Delta", 3, 0)]
    archive = _archive(tmp_path, rows)
    before_own = fi.team_form(archive, "Alpha", "2026-01-04")
    before_later = fi.form_market_probability(archive, "Alpha", "Delta", "2026-01-05",
                                              "match_over_25")

    flipped = [dict(r) for r in rows]
    flipped[3].update({"hs": 0, "gs": 0})
    other = fi.load_archive(_write(tmp_path / "second", flipped))
    after_own = fi.team_form(other, "Alpha", "2026-01-04")
    after_later = fi.form_market_probability(other, "Alpha", "Delta", "2026-01-05",
                                             "match_over_25")

    assert after_own == before_own            # the row is excluded from its own view
    assert after_later != before_later        # but it is used where it belongs


def _write(root: Path, results) -> Path:
    _csv(results, root / "betexplorer_results_2026-01.csv.gz")
    return root


# -- features --------------------------------------------------------------

def test_team_form_reads_the_last_window_only(tmp_path):
    rows = [_round(1, "Alpha", "Beta", 1, 0), _round(2, "Alpha", "Beta", 2, 1),
            _round(3, "Alpha", "Beta", 0, 0), _round(4, "Alpha", "Beta", 1, 3),
            _round(5, "Alpha", "Beta", 4, 0), _round(6, "Alpha", "Beta", 2, 2)]
    archive = _archive(tmp_path, rows)
    form = fi.team_form(archive, "Alpha", "2026-01-06", window=3)
    assert form["n"] == 3
    assert (form["wins"], form["draws"], form["losses"]) == (1, 1, 1)
    assert (form["goals_for"], form["goals_against"]) == (5, 3)   # 0-0, 1-3, 4-0
    assert form["over_25_hits"] == 2                              # 1-3 and 4-0
    assert form["btts_hits"] == 1                                 # only 1-3
    assert form["ppg"] == round(4 / 3, 3)
    assert form["home_split"] == {"n": 3, "points": 4}


def test_insufficient_history_is_reported_not_estimated(tmp_path):
    rows = [_round(1, "Alpha", "Beta", 1, 0), _round(2, "Alpha", "Beta", 2, 1),
            _round(3, "Alpha", "Beta", 1, 1)]
    archive = _archive(tmp_path, rows)
    estimate = fi.form_market_probability(archive, "Alpha", "Beta", "2026-01-04", "match_over_25")
    assert estimate["insufficient_history"] is True
    assert estimate["p"] is None and estimate["reason"] == "insufficient_history"
    assert estimate["components"]["home_form"] is not None  # transparency kept


def test_form_probability_is_the_equal_weight_mean_of_available_components(tmp_path):
    rows = [
        _round(1, "Alpha", "Gamma", 1, 0),      # H2H meetings: total 1 -> no over 2.5
        _round(2, "Alpha", "Gamma", 1, 0),
        _round(3, "Alpha", "Gamma", 1, 0),
        _round(6, "Alpha", "Beta", 3, 1),       # Alpha's own window: 5 matches
        _round(7, "Alpha", "Beta", 3, 1),
        _round(6, "Gamma", "Delta", 0, 0),      # Gamma's own window: 5 matches
        _round(7, "Gamma", "Delta", 0, 0),
    ]
    archive = _archive(tmp_path, rows)
    estimate = fi.form_market_probability(archive, "Alpha", "Gamma", "2026-01-10",
                                          "match_over_25")
    assert estimate["insufficient_history"] is False
    assert estimate["components"] == {
        "home_form": 3 / 7,                     # 2 overs in 5 -> (2+1)/(5+2)
        "away_form": 1 / 7,                     # 0 overs in 5 -> (0+1)/(5+2)
        "h2h": 0.2,                             # 0 overs in 3 meetings -> 1/5
    }
    assert estimate["p"] == pytest.approx((3 / 7 + 1 / 7 + 0.2) / 3)


def test_h2h_component_waits_for_three_meetings(tmp_path):
    rows = [_round(1, "Alpha", "Gamma", 1, 0), _round(2, "Alpha", "Gamma", 1, 0),
            _round(3, "Alpha", "Gamma", 1, 0)]           # 3 prior -> component joins
    archive = _archive(tmp_path, rows)
    three = fi.form_market_probability(archive, "Alpha", "Gamma", "2026-01-04",
                                       "match_over_25")
    assert three["components"]["h2h"] == 0.2
    two = fi.form_market_probability(archive, "Alpha", "Gamma", "2026-01-03",
                                     "match_over_25")
    assert two["components"]["h2h"] is None
    assert two["components"]["home_form"] is not None


def test_unsupported_market_says_so(tmp_path):
    archive = _archive(tmp_path, [_round(1, "Alpha", "Beta", 1, 0)])
    estimate = fi.form_market_probability(archive, "Alpha", "Beta", "2026-01-02",
                                          "home_under_15")
    assert estimate["p"] is None and estimate["reason"] == "unsupported_market"


def test_coverage_counts_months_and_leagues(tmp_path):
    rows = [_round(d, "Alpha", "Beta", 1, 0) for d in range(1, 11)]
    archive = _archive(tmp_path, rows)
    fixtures = [{"date": "2026-01-11", "home": "Alpha", "away": "Beta", "league": "Cup"},
                {"date": "2026-01-02", "home": "Alpha", "away": "Beta", "league": "Cup"}]
    table = fi.coverage(archive, fixtures)
    assert table["total"] == 2 and table["sufficient"] == 1 and table["insufficient"] == 1
    assert table["by_month"]["2026-01"] == {"total": 2, "sufficient": 1, "insufficient": 1}
    assert table["by_league"]["Cup"]["sufficient"] == 1


def test_coverage_labels_a_thin_side_with_its_squad_class(tmp_path):
    """A-3: a reserve/youth/women's side has thin history because the archive
    covers that class of competition far less, so the verdict names it."""
    rows = [_round(d, "Alpha", "Beta", 1, 0) for d in range(1, 11)]
    archive = _archive(tmp_path, rows)
    fixtures = [{"date": "2026-01-11", "home": "Alpha", "away": "Beta", "league": "Cup"},
                {"date": "2026-01-12", "home": "Alpha", "away": "Alpha II", "league": "Cup"},
                {"date": "2026-01-13", "home": "Alpha W", "away": "Beta", "league": "Cup"},
                {"date": "2026-01-14", "home": "Gamma", "away": "Beta", "league": "Cup"}]
    table = fi.coverage(archive, fixtures)
    thin = {(side["team"], side["class"]) for side in table["insufficient_sides"]}
    assert ("Alpha II", "reserve") in thin
    assert ("Alpha W", "women") in thin
    assert ("Gamma", "senior") in thin
    assert table["non_senior_sides"] == 2
    assert fi.squad_class("Alpha") == "senior"
    assert fi.squad_class("Alpha U23") == "u23"


# -- page blocks vs the archive -------------------------------------------

def _page_row(day: str, text: str, hs: int, gs: int, label: str) -> dict:
    return {"date": day, "score": [hs, gs], "odds": None, "text": text, "label": label}


def test_page_blocks_are_read_by_their_own_labels(tmp_path):
    page = {"last_results_rows": [
        _page_row("2026-01-05", "05.01.2026 Alpha 1 : 0 Beta", 1, 0, "Alpha"),
        _page_row("2026-01-01", "01.01.2026 Beta 2 : 2 Alpha", 2, 2, "Alpha"),
        _page_row("2026-01-04", "04.01.2026 Beta 0 : 1 Gamma", 0, 1, "Beta"),
    ]}
    blocks = fi.page_team_rows(page)
    assert sorted(blocks) == ["Alpha", "Beta"]
    assert len(fi.page_h2h_rows({"h2h_rows": [{"date": "2020-01-01"}]})) == 1


def test_page_label_matching_refuses_an_ambiguous_normalised_key():
    blocks = {"Manchester Utd": [{"date": "2026-01-01"}],
              "Manchester City": [{"date": "2026-01-02"}]}
    assert fi._label_for(blocks, "Manchester City") == "Manchester City"
    assert fi._label_for(blocks, "Manchester Town") is None


def test_page_label_matching_accepts_one_loose_match():
    blocks = {"Newcastle Utd": [{"date": "2026-01-01"}]}
    assert fi._label_for(blocks, "Newcastle United") == "Newcastle Utd"


def test_comparator_classifies_every_difference(tmp_path):
    rows = [
        _round(1, "Alpha", "Beta", 1, 0),
        _round(2, "Alpha", "Gamma", 2, 2, league="Cup"),      # cup: page omits it
        _round(3, "Alpha", "Delta", 3, 0),
        _round(4, "Alpha", "Delta", 0, 1),                    # no page row within 2 days
    ]
    archive = _archive(tmp_path, rows)
    page_rows = [
        _page_row("2026-01-03", "03.01.2026 Alpha 3 : 0 Delta", 3, 0, "Alpha"),
        _page_row("2026-01-01", "01.01.2026 Alpha 1 : 0 Beta", 1, 0, "Alpha"),
    ]
    verdict = fi.compare_team_window(archive, "Alpha", "2026-01-06", page_rows,
                                     window=5, league="L1")
    assert verdict["matched"] == 2
    assert [v["verdict"] for v in verdict["archive_only"]] == \
        ["competition_filter", "reschedule"]
    assert verdict["archive_only"][0]["league"] == "Cup"


def test_comparator_flags_a_page_row_the_archive_does_not_have(tmp_path):
    rows = [_round(1, "Alpha", "Beta", 1, 0)]
    archive = _archive(tmp_path, rows)
    page_rows = [_page_row("2026-02-20", "20.02.2026 Alpha 2 : 0 Delta", 2, 0, "Alpha"),
                 _page_row("2026-01-01", "01.01.2026 Alpha 1 : 0 Beta", 1, 0, "Alpha")]
    verdict = fi.compare_team_window(archive, "Alpha", "2026-03-01", page_rows, window=5)
    by_date = {v["date"]: v["verdict"] for v in verdict["verdicts"]}
    assert by_date["2026-01-01"] == "matched"
    assert by_date["2026-02-20"] == "archive_month_gap"


def test_comparator_names_an_unmatched_identity_apart_from_a_month_gap(tmp_path):
    """A name with no rows under its seam key is named ``unmatched_identity``.

    The example is "Newcastle Town" (a different club from "Newcastle
    United", and not in the alias table). The earlier version of this test
    used "Newcastle Utd", which the A-2 fold of the 2026-10-12 adjudication
    now joins to the archive's "Newcastle" - that join is the point of the
    change, so the example had to move to a name that is still unmatched;
    the property under test is unchanged.
    """
    rows = [_round(1, "Newcastle", "Beta", 1, 0)]
    archive = _archive(tmp_path, rows)
    page_rows = [_page_row("2026-02-20", "20.02.2026 Newcastle Town 2 : 1 Delta", 2, 1,
                           "Newcastle Town")]
    strict = fi.compare_team_window(archive, "Newcastle Town", "2026-03-01", page_rows)
    assert strict["verdicts"][0]["verdict"] == "unmatched_identity"
    loose = fi.compare_team_window(archive, "Newcastle", "2026-03-01", page_rows)
    assert loose["verdicts"][0]["verdict"] == "archive_month_gap"


def test_the_module_has_no_network_surface():
    """W6: this reader works only on what is already on disk.

    The page readers take the capture's own saved blocks; a change that adds a
    request to this module has to fail here first.
    """
    source = Path(fi.__file__).read_text(encoding="utf-8")
    for banned in ("import requests", "import httpx", "import urllib", "import socket",
                   "urlopen(", "requests.get", "requests.post"):
        assert banned not in source


def test_whole_fixture_comparison_reports_unmatched_labels(tmp_path):
    rows = [_round(1, "Alpha", "Beta", 1, 0)]
    archive = _archive(tmp_path, rows)
    page = {"last_results_rows": [
        _page_row("2026-01-01", "01.01.2026 Alpha 1 : 0 Beta", 1, 0, "Alpha")]}
    report = fi.compare_page_to_archive(archive, page, as_of="2026-01-05",
                                        home="Alpha", away="Beta")
    assert report["unmatched_labels"] == 1
    assert report["teams"]["Alpha"]["matched"] == 1
    assert report["teams"]["Beta"]["unmatched_label"] is True


# -- metrics ---------------------------------------------------------------

def test_metrics_are_plain_and_deterministic():
    assert fi.brier([(1.0, True), (0.0, False)]) == 0.0
    assert fi.brier([(0.5, True), (0.5, False)]) == 0.25
    assert fi.log_loss([(1.0, True), (0.0, False)]) == pytest.approx(0.0, abs=1e-12)
    assert fi.log_loss([(0.5, True), (0.5, False)]) == pytest.approx(0.69314718, abs=1e-6)
    a = fi.bootstrap_ci([0.1, 0.2, 0.3], seed=7)
    b = fi.bootstrap_ci([0.1, 0.2, 0.3], seed=7)
    assert a == b and a["lo"] <= a["mean"] <= a["hi"]
    delta = fi.paired_bootstrap_delta([(0.5, True)] * 4, [(0.7, True)] * 4)
    assert delta["delta"] == pytest.approx(-0.16)
    assert delta["lo"] <= delta["delta"] <= delta["hi"]
