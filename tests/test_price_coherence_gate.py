"""The coherent-book gate: a 1x2 quote must belong to a real three-way book.

Incident (2026-10-11 -> 2026-10-13): the pinnapi relay returned, for a single
fixture under the single bookmaker "Pinnacle" and a single capture second,
three separate market groups that all canonicalised to `1x2`:

    Viking vs Bayern Munich   18.79 / 14.45 / 1.088   (the full-time book)
                              16.35 / 1.033           (2-way margin 1.0293)
                              1.7813 / 2.06           (2-way margin 1.0468)

The index keys on (date, home, away, market, selection) and resolves a
same-side tie by largest odds, so the away pick took **2.06** - a price no
three-way book contains - and printed, stamped `price_push_eligible` and
banded three real-money Champions League legs off it (the real away quote was
1.088). Galatasaray vs Barcelona (4.21 chosen vs 1.2703 real) and Arsenal vs
Lille (2.2 vs 1.2358) shipped from the same snapshot.

The numbers below are the archived board rows, verbatim.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.picks_today as pt
from edgefactory import source_health

ROOT = Path(__file__).resolve().parent.parent

DAY = "2026-10-13"
STAMP = "2026-10-11T22:14:45+00:00"


def _row(selection, odds, *, home="Viking", away="Bayern Munich", day=DAY,
         captured_at=STAMP, bookmaker="Pinnacle", market="1x2", **extra):
    row = {
        "source": "pinnapi_odds", "date": day, "home": home, "away": away,
        "kickoff": f"{day}T19:00:00Z", "league": "UEFA - Champions League",
        "market": market, "selection": selection, "line": None,
        "raw_market": "money_line", "raw_selection": selection, "odds": odds,
        "book": bookmaker, "bookmaker": bookmaker, "captured_at": captured_at,
    }
    row.update(extra)
    return row


# --- archived boards -------------------------------------------------------

VIKING = [
    _row("home", 18.79), _row("home", 16.35), _row("home", 1.7813),
    _row("draw", 14.45),
    _row("away", 2.06), _row("away", 1.088), _row("away", 1.033),
]

GALATASARAY = [
    _row("home", 8.41, home="Galatasaray", away="Barcelona"),
    _row("home", 7.28, home="Galatasaray", away="Barcelona"),
    _row("home", 1.4348, home="Galatasaray", away="Barcelona"),
    _row("draw", 7.23, home="Galatasaray", away="Barcelona"),
    _row("away", 4.21, home="Galatasaray", away="Barcelona"),
    _row("away", 2.89, home="Galatasaray", away="Barcelona"),
    _row("away", 1.2703, home="Galatasaray", away="Barcelona"),
    _row("away", 1.111, home="Galatasaray", away="Barcelona"),
]

ARSENAL = [
    _row("home", 2.2, home="Arsenal", away="Lille"),
    _row("home", 1.2358, home="Arsenal", away="Lille"),
    _row("home", 1.069, home="Arsenal", away="Lille"),
    _row("draw", 6.56, home="Arsenal", away="Lille"),
    _row("away", 12.12, home="Arsenal", away="Lille"),
    _row("away", 10.22, home="Arsenal", away="Lille"),
    _row("away", 1.6944, home="Arsenal", away="Lille"),
]

ATLETICO = [
    _row("home", 2.1, home="Atletico Nacional", away="Deportivo Pasto",
         day="2026-10-11", captured_at="2026-10-10T08:48:58+00:00"),
    _row("home", 1.074, home="Atletico Nacional", away="Deportivo Pasto",
         day="2026-10-11", captured_at="2026-10-10T08:48:58+00:00"),
    _row("away", 8.35, home="Atletico Nacional", away="Deportivo Pasto",
         day="2026-10-11", captured_at="2026-10-10T08:48:58+00:00"),
    _row("away", 1.7042, home="Atletico Nacional", away="Deportivo Pasto",
         day="2026-10-11", captured_at="2026-10-10T08:48:58+00:00"),
]


def _pick(selection, home, away, day=DAY, market="1x2", **extra):
    pick = {
        "date": day, "home": home, "away": away, "market": market,
        "pick": selection, "kickoff": f"{day}T19:00:00Z",
    }
    pick.update(extra)
    return pick


def _bundle(rows, **kwargs):
    return pt._odds_bundle_from_rows(rows, provider="pinnapi_odds", **kwargs)


def _price(bundle, selection, home, away, day=DAY, market="1x2"):
    row, _method = pt.find_side_keyed_odds_row(
        _pick(selection, home, away, day=day, market=market), bundle)
    return (row or {}).get("odds")


# --- the incident ----------------------------------------------------------

def test_the_viking_away_pick_prices_at_the_coherent_book_not_the_maximum_quote():
    bundle = _bundle(VIKING)
    assert _price(bundle, "away", "Viking", "Bayern Munich") == 1.088
    assert _price(bundle, "home", "Viking", "Bayern Munich") == 18.79
    assert _price(bundle, "draw", "Viking", "Bayern Munich") == 14.45


def test_the_other_two_champions_league_phantoms_reprice_to_their_books():
    gala = _bundle(GALATASARAY)
    assert _price(gala, "away", "Galatasaray", "Barcelona") == 1.2703
    arsenal = _bundle(ARSENAL)
    assert _price(arsenal, "home", "Arsenal", "Lille") == 1.2358


def test_refused_quotes_are_marked_and_left_on_the_board_as_evidence():
    """The observability half: the phantom must be visible in the archive.

    On 2026-10-11 it survived with no marker at all - the board stored the
    canonical market ("1x2") and not the container or line it came from, so
    the quote could not be reconstructed afterwards. Refused rows now keep
    their marker and stay in `market_candidates` (evidence, never a pricing
    tier).
    """
    bundle = _bundle(VIKING)
    refused = [row for group in bundle["market_candidates"].values()
               for row in group if row.get("price_coherence")]
    assert len(refused) == 4  # 16.35, 1.7813, 2.06, 1.033
    assert {row["price_coherence"] for row in refused} == {
        pt._EXCLUDED_NOT_IN_BOOK}
    assert all(row["coherent_trio_overround"] == pytest.approx(1.0415416)
               for row in refused)
    assert bundle["coherence"]["excluded_rows"] == 4
    assert bundle["coherence"]["withheld_fixtures"] == 0
    assert bundle["coherence"]["reason_counts"] == {pt._EXCLUDED_NOT_IN_BOOK: 4}
    # the chosen rows carry no marker
    assert not [row for key, row in bundle["exact"].items() if row.get("price_coherence")]


def test_no_coherent_book_means_withheld_not_best_guess():
    """Atletico Nacional vs Deportivo Pasto, 2026-10-11.

    Two home quotes (2.1, 1.074) and two away quotes (8.35, 1.7042) with NO
    complete three-way book anywhere in the snapshot: every trio is a
    degenerate pair, so there is no coherent answer to prefer. The gate
    withholds the fixture instead of printing a price it cannot justify.
    """
    bundle = _bundle(ATLETICO)
    assert _price(bundle, "home", "Atletico Nacional", "Deportivo Pasto",
                  day="2026-10-11") is None
    assert _price(bundle, "away", "Atletico Nacional", "Deportivo Pasto",
                  day="2026-10-11") is None
    assert bundle["coherence"]["withheld_fixtures"] == 1
    assert bundle["coherence"]["reason_counts"] == {pt._WITHHELD_AMBIGUOUS: 4}
    assert bundle["coherence"]["withheld_fixture_names"] == [
        "Atletico Nacional vs Deportivo Pasto"]
    # every refused row says so, and none of them reached the exact index
    assert all(row.get("price_coherence") == pt._WITHHELD_AMBIGUOUS
               for group in bundle["market_candidates"].values() for row in group)


def test_a_single_quote_per_side_is_left_exactly_as_it_was():
    """268 of the 514 archived priced picks with a board are this case, and
    every non-pinnapi board: one quote per side, nothing to reconcile."""
    bundle = _bundle([_row("home", 18.79), _row("draw", 14.45), _row("away", 1.088)])
    assert _price(bundle, "away", "Viking", "Bayern Munich") == 1.088
    assert _price(bundle, "home", "Viking", "Bayern Munich") == 18.79
    assert bundle["coherence"]["excluded_rows"] == 0
    assert bundle["coherence"]["withheld_fixtures"] == 0


def test_a_two_quote_book_without_a_third_side_is_not_ambiguous():
    """One home quote and one away quote, no draw: indistinguishable from a
    complete book missing a side, so it is NOT withheld. This is the honest
    residual - a provider that ships a bare two-sided group and nothing else
    needs the provider-side rule (three sides or a named drop), which pinnapi
    now has."""
    bundle = _bundle([_row("home", 1.7813), _row("away", 2.06)])
    assert _price(bundle, "away", "Viking", "Bayern Munich") == 2.06
    assert bundle["coherence"]["withheld_fixtures"] == 0
    assert bundle["coherence"]["excluded_rows"] == 0


def test_other_markets_and_other_days_are_untouched():
    bundle = _bundle([
        _row("over", 1.9, market="ou_2.5", day=DAY),
        _row("under", 1.98, market="ou_2.5", day=DAY),
        # same book, same second, different fixture: its own group
        _row("away", 3.3, home="Inter", away="Club Brugge"),
        _row("home", 1.25, home="Inter", away="Club Brugge"),
    ])
    assert _price(bundle, "over", "Viking", "Bayern Munich", market="ou_2.5") == 1.9
    assert _price(bundle, "away", "Inter", "Club Brugge") == 3.3
    assert bundle["coherence"]["excluded_rows"] == 0


def test_a_cached_contaminated_ledger_is_repaired_by_the_gate_not_by_the_adapter():
    """Why the gate exists on top of the adapter rule.

    pinnapi's ledger is cache-first: a day's rows are read back verbatim, so
    a snapshot captured before the adapter rule was fixed still arrives at
    the join exactly as it was recorded. The gate is the only thing standing
    between that cached payload and a printed price.
    """
    bundle = pt._odds_bundle_from_rows(VIKING, provider="pinnapi_odds")
    assert _price(bundle, "away", "Viking", "Bayern Munich") == 1.088


# --- wiring, counters, and the receipt ------------------------------------

def test_the_refusal_counters_reach_the_committed_health_row():
    row = source_health.build_daily_source_health("2026-10-13", {
        "pinnapi_odds": {
            "status": "ok", "pa_raw": 910, "pa_matched": 4,
            "coherence_excluded_rows": 4, "coherence_withheld_fixtures": 1,
            "coherence_reason_counts": {pt._EXCLUDED_NOT_IN_BOOK: 4, pt._WITHHELD_AMBIGUOUS: 1},
        },
    })["sources"]["pinnapi_odds"]
    assert row["coherence_excluded_rows"] == 4
    assert row["coherence_withheld_fixtures"] == 1
    assert row["coherence_reason_counts"][pt._WITHHELD_AMBIGUOUS] == 1


def test_an_absent_counter_is_zero_not_missing():
    row = source_health.build_daily_source_health("2026-10-13", {})["sources"]["pinnapi_odds"]
    assert row["coherence_excluded_rows"] == 0
    assert row["coherence_withheld_fixtures"] == 0
    assert row["coherence_reason_counts"] is None


def test_the_caller_forwards_the_gate_counters_into_the_health_row():
    """Same wiring gap the 2026-10-06 pinnacle answer died of: the health row
    is built by hand, so a counter the caller forgets is a counter nobody
    ever sees."""
    src = (ROOT / "scripts" / "picks_today.py").read_text(encoding="utf-8")
    assert "coherence_observation(shadow_stats.get(source_name) or {})" in src
    assert "coherence_observation_lines(donor_bundles)" in src


def test_the_run_log_names_a_refusing_source():
    lines = pt.coherence_observation_lines([
        {"provider": "pinnapi_odds",
         "coherence": {"excluded_rows": 4, "withheld_fixtures": 1,
                       "withheld_fixture_names": ["Atletico Nacional vs Deportivo Pasto"],
                       "reason_counts": {pt._EXCLUDED_NOT_IN_BOOK: 4,
                                         pt._WITHHELD_AMBIGUOUS: 1}}},
        {"provider": "boggio", "coherence": {"excluded_rows": 0, "withheld_fixtures": 0,
                                             "reason_counts": {}}},
    ])
    assert len(lines) == 1
    assert "pinnapi_odds" in lines[0] and "4 1x2 quote(s) refused" in lines[0]
    assert "1 fixture(s) price-withheld" in lines[0]
    assert "Atletico Nacional vs Deportivo Pasto" in lines[0]


def test_a_refused_quote_never_counts_as_corroboration():
    """A quote the gate refused is not evidence for anything, least of all
    agreement. Before the marker existed, any cross-source copy of the same
    phantom shape would have corroborated a contaminated price."""
    base = {
        "odds": 1.088, "odds_source": "pinnapi_odds", "bookmaker": "Pinnacle",
        "pick": "away", "market": "1x2", "home": "Viking", "away": "Bayern Munich",
    }
    entry = {
        "source": "sharpapi_odds", "market": "1x2", "selection": "away",
        "odds": 1.11, "bookmaker": "Book X", "named_bookmaker": True,
        "price_independence_family": "sharp_book",
    }
    clean = dict(base, price_board=[dict(entry)])
    assert pt._stamp_price_corroboration([clean]) == 1
    assert clean["price_corroborated"] is True

    marked = dict(base, price_board=[dict(entry, price_coherence=pt._EXCLUDED_NOT_IN_BOOK)])
    assert pt._stamp_price_corroboration([marked]) == 0
    assert marked["price_corroborated"] is False


def test_the_board_entry_now_carries_identity_not_only_price():
    """`line` and `raw_market` are what made the 2026-10-11 phantom
    unreconstructible: the archive stored the canonical market only."""
    entry = pt._price_board_entry("pinnapi_odds", _row("away", 2.06))
    assert entry["line"] is None
    assert entry["raw_market"] == "money_line"
    assert entry["raw_selection"] == "away"
    assert entry["price_coherence"] is None


def test_the_archived_boards_replay_to_the_coherent_price():
    """End-to-end pin on the real archive, when it is present in the checkout.

    Rebuilds each source's bundle from the rows the archived board recorded
    and asks the engine for the price it would choose today.
    """
    path = ROOT / "localdata" / "picks_2026-10-13.json"
    if not path.exists():
        pytest.skip("picks archive not in this checkout")
    picks = json.loads(path.read_text())
    expected = {
        "Viking vs Bayern Munich": 1.088,
        "Galatasaray vs Barcelona": 1.2703,
        "Arsenal vs Lille": 1.2358,
    }
    seen = 0
    for pick in picks:
        if pick.get("match") not in expected:
            continue
        rows = [{
            "source": str(e.get("source") or ""), "date": str(pick.get("date") or ""),
            "home": e.get("home"), "away": e.get("away"), "kickoff": e.get("kickoff"),
            "league": e.get("league"), "market": e.get("market"),
            "selection": e.get("selection"), "line": e.get("line"),
            "raw_market": e.get("raw_market"), "odds": e.get("odds"),
            "bookmaker": e.get("bookmaker"), "captured_at": e.get("captured_at"),
        } for e in pick.get("price_board") or []
            if str(e.get("source") or "") == str(pick.get("odds_source") or "")]
        bundle = pt._odds_bundle_from_rows(rows, provider=str(pick.get("odds_source") or ""))
        row, _method = pt.find_side_keyed_odds_row(pick, bundle)
        assert (row or {}).get("odds") == expected[pick["match"]], (
            f"{pick['match']}: picked {(row or {}).get('odds')}, "
            f"archived phantom was {pick.get('odds')}")
        seen += 1
    assert seen == len(expected), "the archived 10-13 slate must still be replayable"


def test_the_printed_pick_board_shows_the_coherent_price_and_the_refusals():
    """What the operator reads: the chosen quote is the coherent one, and the
    quotes the gate threw away are still visible beside it with their verdict."""
    bundle = _bundle(VIKING)
    pick = _pick("away", "Viking", "Bayern Munich")
    row, method = pt.find_side_keyed_odds_row(pick, bundle)
    assert row is not None and method == "exact"
    pt._stamp_price_board(pick, [bundle], chosen_row=row,
                          chosen_source="pinnapi_odds", chosen_method=method)
    board = pick["price_board"]
    chosen = [e for e in board if e.get("chosen")]
    assert len(chosen) == 1
    assert chosen[0]["odds"] == 1.088
    assert chosen[0]["match_method"] == "exact"
    away = {e["odds"]: e for e in board if e["selection"] == "away"}
    assert away[2.06]["price_coherence"] == pt._EXCLUDED_NOT_IN_BOOK
    assert away[1.088]["price_coherence"] is None
    assert away[2.06]["raw_market"] == "money_line"
    assert away[2.06]["line"] is None
