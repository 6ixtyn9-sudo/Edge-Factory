"""Join-layer repair regressions (2026-10-03).

Every fixture in this module is **raw provider vocabulary**, exactly as it
appears in a captured payload. The previous suite passed while all four
donor lanes contributed zero rows precisely because its fixtures were
pre-canonicalised (``market="1x2"``, ``selection="home"``), so the
canonicalisation and date-attribution defects were invisible to it.

Three contracts are asserted here:

1. each donor produces a NON-ZERO matched count against a realistic slate
   built from its own raw vocabulary;
2. an unmapped market or selection is COUNTED as a miss, never dropped;
3. the counted miss names the provider token, so the next run can
   enumerate a feed's vocabulary without a live discovery call.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.picks_today as pt
from edgefactory.odds_normalization import canonical_market_selection, provider_kickoff_date
from edgefactory.sources import betbetter as bb
from edgefactory.sources import boggio
from edgefactory.sources.oddspapi_odds import rows_from_odds_response

FIXTURES = Path(__file__).parent / "fixtures"
DAY = "2026-10-03"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def _pick(home: str, away: str, market: str, selection: str, day: str = DAY) -> dict:
    return {
        "date": day, "home": home, "away": away,
        "market": market, "pick": selection, "kickoff": f"{day}T16:00:00Z",
    }


# ---------------------------------------------------------------------------
# Task 1 — Bet Better market vocabulary (raw strings, not "1x2")
# ---------------------------------------------------------------------------


def test_betbetter_raw_market_strings_map_or_are_explicitly_unsupported():
    """The three market strings present in the captured Brazil payload."""
    assert canonical_market_selection("Head to Head", "Alpha FC",
                                      home="Alpha FC", away="Beta FC")[0].market == "1x2"
    assert canonical_market_selection("Both Teams to Score", "Yes")[0].market == "btts"

    # Recognised, deliberately not priced -> explicit unsupported, still a miss.
    result, failure = canonical_market_selection(
        "Draw No Bet", "Cruzeiro", home="Bragantino-SP", away="Cruzeiro")
    assert result is None
    assert failure.kind == "unsupported_market"
    assert failure.raw == "draw_no_bet"


def test_betbetter_unmappable_market_is_kept_and_counted_not_dropped():
    payload = _load("betbetter_brazil_serie_a.json")
    rows = bb.parse_picks(payload, day="2026-10-02", slug="brazil-serie-a")
    # Three picks in; the ticker-shaped game string fails closed, the other
    # two SURVIVE - including the unmappable Draw No Bet row.
    assert len(rows) == 2
    unmappable = [r for r in rows if r["canonicalization_mappable"] is False]
    assert len(unmappable) == 1
    assert unmappable[0]["raw_market"] == "Draw No Bet"
    assert unmappable[0]["market"] == "Draw No Bet"  # raw vocabulary preserved
    assert unmappable[0]["canonicalization_reason"] == "unsupported_market:draw_no_bet"
    assert unmappable[0]["price_push_eligible"] is False


def test_betbetter_matches_a_realistic_slate_from_raw_vocabulary():
    day = "2026-10-05"
    raw_payload = {
        "attribution": "Bet Better — https://betbetter.world",
        "licence": "CC BY 4.0",
        "picks": [
            {"game": "Away United @ Home City", "gameTimeUtc": f"{day}T18:00:00.0000000Z",
             "market": "Head to Head", "selection": "Home City", "line": None,
             "winProbabilityPct": 55.0, "fairOdds": 1.82, "confidence": "LEAN"},
            {"game": "Visitors FC @ Hosts FC", "gameTimeUtc": f"{day}T19:00:00.0000000Z",
             "market": "Both Teams to Score", "selection": "Yes", "line": None,
             "winProbabilityPct": 61.9, "fairOdds": 2.01, "confidence": "LEAN"},
            {"game": "Other FC @ Another FC", "gameTimeUtc": f"{day}T20:00:00.0000000Z",
             "market": "Draw No Bet", "selection": "Other FC", "line": None,
             "winProbabilityPct": 52.9, "fairOdds": 2.64, "confidence": "LEAN"},
        ],
    }
    rows = bb.parse_picks(raw_payload, day=day, slug="epl")
    bundle = pt._odds_bundle_from_rows(rows, provider="betbetter")
    picks = [
        _pick("Home City", "Away United", "1x2", "home", day=day),
        _pick("Hosts FC", "Visitors FC", "btts", "yes", day=day),
        _pick("Another FC", "Other FC", "1x2", "home", day=day),
    ]
    report = pt.donor_join_diagnostics(picks, [bundle])["betbetter"]

    assert report["matched_rows"] == 2, "raw Bet Better vocabulary must join"
    # The third row is not lost: it is an explicitly counted, named miss.
    assert report["miss_counts"] == {"market_unsupported": 1}
    assert report["unmapped_vocabulary"] == {"unsupported_market:draw_no_bet": 1}


def test_betbetter_feed_is_multi_day_so_off_slate_rows_are_out_of_window():
    """Task 4: the captured board really does publish future fixtures."""
    payload = _load("betbetter_brazil_serie_a.json")
    captured_on = payload["updatedUtc"][:10]
    rows = bb.parse_picks(payload, day=captured_on, slug="brazil-serie-a")
    event_days = {r["date"] for r in rows}
    assert captured_on == "2026-10-02"
    assert event_days == {"2026-10-13", "2026-10-10"}, "upcoming board, not a day board"

    bundle = pt._odds_bundle_from_rows(rows, provider="betbetter")
    picks = [_pick("Vasco da Gama", "Remo", "btts", "yes", day=captured_on)]
    report = pt.donor_join_diagnostics(picks, [bundle])["betbetter"]
    # A legitimate future fixture is OUT OF WINDOW. Calling it date_mismatch
    # implied a date-attribution defect that is not there.
    assert report["miss_counts"].get("out_of_window") == 1
    assert "date_mismatch" not in report["miss_counts"]


# ---------------------------------------------------------------------------
# Task 2 — Boggio selection vocabulary (1 / X / 2, not home / draw / away)
# ---------------------------------------------------------------------------


def test_boggio_raw_classic_tokens_canonicalise_and_keep_their_date():
    payload = _load("boggio_predictions_classic.json")
    rows, shaped = boggio.parse_predictions(payload, day=DAY)
    assert shaped
    # Nothing is dropped: three predictions in, three rows out.
    assert len(rows) == 3
    by_home = {r["home"]: r for r in rows}

    assert (by_home["Alpha FC"]["market"], by_home["Alpha FC"]["selection"]) == ("1x2", "home")
    assert (by_home["Gamma FC"]["market"], by_home["Gamma FC"]["selection"]) == ("1x2", "draw")
    # The provider's own "YYYY-MM-DD HH:MM:SS UTC" stamp must resolve: this
    # is what made every Boggio row land with an empty join date.
    assert by_home["Alpha FC"]["date"] == DAY
    assert by_home["Alpha FC"]["raw_selection"] == "1"


def test_boggio_double_chance_is_counted_as_a_miss_not_dropped():
    payload = _load("boggio_predictions_classic.json")
    rows, _shaped = boggio.parse_predictions(payload, day=DAY)
    dc = [r for r in rows if r["home"] == "Epsilon FC"][0]
    assert dc["canonicalization_mappable"] is False
    assert dc["raw_selection"] == "1X"
    assert dc["selection"] == "1X"  # raw vocabulary preserved for the census
    assert dc["canonicalization_reason"] == "unsupported_selection:1x"
    assert dc["price_push_eligible"] is False


def test_boggio_matches_a_realistic_slate_and_counts_the_rest():
    payload = _load("boggio_predictions_classic.json")
    rows, _shaped = boggio.parse_predictions(payload, day=DAY)
    bundle = pt._odds_bundle_from_rows(rows, provider="boggio")
    picks = [
        _pick("Alpha FC", "Beta FC", "1x2", "home"),
        _pick("Gamma FC", "Delta FC", "1x2", "draw"),
        _pick("Epsilon FC", "Zeta FC", "1x2", "home"),
    ]
    report = pt.donor_join_diagnostics(picks, [bundle])["boggio"]

    assert report["matched_rows"] == 2, "boggio must contribute a non-zero match count"
    assert report["miss_counts"] == {"selection_unsupported": 1}
    assert report["unmapped_vocabulary"] == {"unsupported_selection:1x": 1}


def test_boggio_kickoff_without_a_zone_still_fails_closed():
    """The repair must not reintroduce capture-date defaulting."""
    assert provider_kickoff_date("2026-10-03 16:00:00 UTC") == "2026-10-03"
    assert provider_kickoff_date("2026-10-03 16:00:00") is None
    assert provider_kickoff_date("16:00") is None
    assert provider_kickoff_date(None) is None

    payload = _load("boggio_predictions_classic.json")
    payload["data"][0]["start_date"] = "2026-10-03 16:00:00"
    rows, _shaped = boggio.parse_predictions(payload, day=DAY)
    naive = [r for r in rows if r["home"] == "Alpha FC"][0]
    assert naive["date"] is None
    assert naive["price_push_eligible"] is False


# ---------------------------------------------------------------------------
# Task 3 — OddsPAPI: nested outcomes, fixture identity, instrumentation
# ---------------------------------------------------------------------------


def test_oddspapi_payload_without_participants_emits_nothing_and_says_why():
    """The 2026-10-03 defect: 414 rows all written as 1x2/home with no teams."""
    payload = _load("oddspapi_odds_fixture.json")
    stats: dict = {}
    rows = rows_from_odds_response(payload, market_type_map={"101": "1x2"}, stats=stats)
    assert rows == []
    assert stats == {"fixture_identity_missing": 1}


def test_oddspapi_extracts_nested_player_prices_with_fixture_identity():
    payload = _load("oddspapi_odds_fixture.json")
    stats: dict = {}
    rows = rows_from_odds_response(
        payload,
        market_type_map={"101": "1x2", "10194": "totals"},
        home="Croatia", away="England", stats=stats,
    )
    by_selection = {(r["market"], r["selection"]): r for r in rows}

    # Three DISTINCT 1x2 sides, not three copies of "home".
    assert by_selection[("1x2", "home")]["odds"] == 4.3
    assert by_selection[("1x2", "draw")]["odds"] == 3.2
    assert by_selection[("1x2", "away")]["odds"] == 1.625
    assert all(r["home"] == "Croatia" and r["away"] == "England" for r in rows)

    # Totals come off the nested players[] too, and only the main line.
    assert by_selection[("ou_2.5", "over")]["odds"] == 1.98
    assert by_selection[("ou_2.5", "under")]["odds"] == 1.86
    assert ("ou_3.5", "over") not in by_selection
    assert stats.get("alt_line_skipped") == 1

    # Provider stamps are preserved; captured_at stays OUR capture clock.
    row = by_selection[("1x2", "home")]
    assert row["published_at"] == "2026-10-03T09:50:00.000Z"
    assert row["provider_changed_at"] == "2026-10-03T09:51:00.000Z"
    assert row["captured_at"] != row["published_at"]


def test_oddspapi_never_labels_an_unnamed_outcome_as_home():
    payload = _load("oddspapi_odds_fixture.json")
    market = payload["bookmakerOdds"]["bodog.eu"]["markets"]["101"]
    for outcome in market["outcomes"].values():
        outcome["players"]["0"].pop("playerName")
    stats: dict = {}
    rows = rows_from_odds_response(
        payload, market_type_map={"101": "1x2"},
        home="Croatia", away="England", stats=stats,
    )
    assert rows == []
    assert stats["unresolved_1x2"] == 3


def test_oddspapi_lookahead_quote_is_refused_at_the_boundary():
    payload = _load("oddspapi_odds_fixture.json")
    market = payload["bookmakerOdds"]["bodog.eu"]["markets"]["101"]
    for outcome in market["outcomes"].values():
        outcome["players"]["0"]["bookmakerChangedAt"] = "2999-01-01T00:00:00.000Z"
    stats: dict = {}
    rows = rows_from_odds_response(
        payload, market_type_map={"101": "1x2"},
        home="Croatia", away="England", stats=stats,
    )
    assert [r for r in rows if r["market"] == "1x2"] == []
    assert stats["published_after_capture"] == 3


def test_oddspapi_gets_the_same_per_reason_miss_buckets_as_the_donors():
    payload = _load("oddspapi_odds_fixture.json")
    rows = rows_from_odds_response(
        payload, market_type_map={"101": "1x2", "10194": "totals"},
        home="Croatia", away="England",
    )
    # A persisted row that lost its fixture identity (the 2026-10-03 shape)
    # must be reported as an identity defect, not an uncovered fixture.
    rows.append(dict(rows[0], home="", away=""))
    bundle = pt._odds_bundle_from_rows(rows, provider=pt.ODDSPAPI_ODDS_SOURCE)
    picks = [_pick("Croatia", "England", "1x2", "away")]
    report = pt.donor_join_diagnostics(picks, [bundle])[pt.ODDSPAPI_ODDS_SOURCE]

    assert report["matched_rows"] == 1, "oddspapi must contribute a non-zero match count"
    assert report["miss_counts"]["fixture_identity_missing"] == 1
    assert report["miss_counts"]["no_pick_for_fixture"] == 4
    line = pt.donor_join_miss_lines(report and {pt.ODDSPAPI_ODDS_SOURCE: report})[0]
    assert line.startswith("donor join misses oddspapi_odds:")


# ---------------------------------------------------------------------------
# Cross-cutting: a miss is never silent, and it names the provider token
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("row", "bucket", "token"), [
    ({"market": "Draw No Bet", "selection": "Cruzeiro"},
     "market_unsupported", "unsupported_market:draw_no_bet"),
    ({"market": "Provider Mystery", "selection": "Home FC"},
     "market_unmapped", "unknown_market:provider_mystery"),
    ({"market": "classic", "selection": "1X"},
     "selection_unsupported", "unsupported_selection:1x"),
    ({"market": "classic", "selection": "mystery side"},
     "selection_unmapped", "unknown_selection:mystery_side"),
])
def test_every_unmapped_token_is_counted_and_named(row, bucket, token):
    base = {
        "date": DAY, "home": "Home FC", "away": "Away FC", "odds": 1.80,
        "kickoff": f"{DAY}T16:00:00Z",
    }
    bundle = pt._odds_bundle_from_rows([{**base, **row}], provider="betbetter")
    report = pt.donor_join_diagnostics(
        [_pick("Home FC", "Away FC", "1x2", "home")], [bundle])["betbetter"]

    assert report["raw_rows"] == 1, "the row must survive to be counted"
    assert report["miss_counts"] == {bucket: 1}
    assert report["unmapped_vocabulary"] == {token: 1}
    assert pt.donor_vocabulary_lines({"betbetter": report})[0].startswith(
        "donor unmapped vocabulary betbetter:")


def test_board_rejected_before_the_bundle_still_reports_a_counted_reason(tmp_path, monkeypatch):
    """414 rows thrown away wholesale must not print as ``none=0``."""
    import csv
    import gzip

    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    path = tmp_path / "oddspapi_odds_2026-10.csv.gz"
    cols = ["source", "source_type", "sport", "date", "kickoff", "league",
            "home", "away", "market", "selection", "odds", "bookmaker",
            "captured_at"]
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        # Exactly the 2026-10-03 shape: priced, booked, and with no teams.
        for odds in (4.3, 4.75, 1.532):
            writer.writerow({
                "source": "oddspapi", "source_type": "odds", "sport": "soccer",
                "date": DAY, "kickoff": f"{DAY}T09:00:00.000Z", "league": "",
                "home": "", "away": "", "market": "1x2", "selection": "home",
                "odds": odds, "bookmaker": "bodog.eu",
                "captured_at": f"{DAY}T13:13:33+00:00",
            })
    stats: dict = {}
    from datetime import datetime, timezone
    bundle = pt.oddspapi_odds_bundle(
        DAY,
        not_after=datetime(2026, 10, 3, 15, 0, tzinfo=timezone.utc),
        stats=stats,
    )
    assert stats["raw_rows"] == 3
    assert stats["usable_rows"] == 0, "teamless rows were never usable supply"
    # These rows predate the generation marker, so they are refused on the
    # generation — the cause — rather than on blank participants, which is
    # only the symptom that generation happened to show.
    assert stats["stale_schema_rows"] == 3

    report = pt.donor_join_diagnostics(
        [_pick("Croatia", "England", "1x2", "home")], [bundle],
    )[pt.ODDSPAPI_ODDS_SOURCE]
    assert report["miss_counts"] == {"stale_schema": 3}
    assert report["raw_rows"] == 3
    line = pt.donor_join_miss_lines({pt.ODDSPAPI_ODDS_SOURCE: report})[0]
    assert "stale_schema=3" in line
