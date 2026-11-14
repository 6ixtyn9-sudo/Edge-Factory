"""1X2 odds orientation: a selection only ever receives its own side's price.

Incident 2026-09-25, FC Dordrecht vs Almere City, pick AWAY. The reported
bookmaker board was home 2.05 / draw 3.00 / away 1.03; the automatic slip
printed AWAY @ 2.00 from an unverified ScoutingStats-only quote. These tests
pin the whole chain: odd1->home, oddx->draw, odd2->away; the complete
side-keyed board; selection identity when marking the chosen row; the
orientation of fuzzy joins; and the live ticket gate on
price_push_eligible=False (while replay keeps its frozen legacy pool).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import scripts.picks_today as pt  # noqa: E402

DAY = "2026-09-25"
KICKOFF = "2026-09-25T19:00:00Z"
BOARD = {"home": 2.05, "draw": 3.00, "away": 1.03}


def _source_row(home="FC Dordrecht", away="Almere City", odd1=2.05, oddx=3.00, odd2=1.03):
    """A raw ScoutingStats-shaped capture row (odd1/oddx/odd2 columns)."""
    return {"date": DAY, "kickoff": KICKOFF, "league": "Eerste Divisie",
            "home": home, "away": away, "hs": "",
            "odd1": odd1, "oddx": oddx, "odd2": odd2}


def _pick(**extra):
    out = {"date": DAY, "home": "FC Dordrecht", "away": "Almere City",
           "match": "FC Dordrecht vs Almere City", "market": "1x2",
           "pick": "away", "avg_p": 74.0, "odds": None, "odds_source": None,
           "bookmaker": None, "kickoff": KICKOFF,
           "bucket": "WATCHLIST_UNCORROBORATED_PRICE"}
    out.update(extra)
    return out


def _bundle(source_rows, provider=None):
    provider = provider or pt.SCOUTINGSTATS_ODDS_SOURCE
    return pt._odds_bundle_from_rows(pt._scoutingstats_rows_to_odds(source_rows),
                                     provider=provider)


def _empty_primary():
    return pt._odds_bundle_from_rows([], provider=pt.BZZOIRO_ODDS_SOURCE)


# ---------------- column -> side mapping ----------------

def test_odd1_oddx_odd2_map_to_home_draw_away():
    rows = pt._scoutingstats_rows_to_odds([_source_row()])
    assert {r["selection"]: r["odds"] for r in rows if r["market"] == "1x2"} == BOARD


def test_each_selection_gets_its_own_side_keyed_price():
    bundle = _bundle([_source_row()])
    for side, price in BOARD.items():
        row, method = pt.find_odds_row(_pick(pick=side), bundle)
        assert method == "exact"
        assert row["selection"] == side and row["odds"] == price


# ---------------- end-to-end enrichment (no monkeypatching) ----------------

def test_away_pick_is_priced_at_away_quote_with_complete_board():
    pick = _pick()
    assert pt.enrich_with_live_odds([pick], _empty_primary(), _bundle([_source_row()])) == 1

    assert pick["odds"] == 1.03            # never the home 2.05
    board = pick["price_board"]
    assert [(e["selection"], e["odds"]) for e in board] == [
        ("home", 2.05), ("draw", 3.00), ("away", 1.03)]
    chosen = [e for e in board if e.get("chosen")]
    assert len(chosen) == 1 and chosen[0]["selection"] == "away"
    assert chosen[0]["odds"] == 1.03
    # ScoutingStats alone is still not an execution-safe bookmaker price.
    assert pick["price_push_eligible"] is False
    assert pick["price_evidence"] == pt.PRICE_EVIDENCE_SCOUTINGSTATS_SOLE


def test_chosen_marker_requires_selection_identity():
    # Home and away quoted at the SAME price by the same book: odds+bookmaker
    # alone would mark the home row as the away pick's chosen price.
    pick = _pick()
    pt.enrich_with_live_odds([pick], _empty_primary(),
                             _bundle([_source_row(odd1=1.90, odd2=1.90)]))
    chosen = [e for e in pick["price_board"] if e.get("chosen")]
    assert [(e["selection"], e["odds"]) for e in chosen] == [("away", 1.90)]


def test_plain_index_board_also_captures_all_three_sides():
    bundle = _bundle([_source_row()])
    board = pt._collect_price_board(_pick(), bundle["exact"])
    assert {(e["selection"], e["odds"]) for e in board} == set(BOARD.items())


def test_primary_bzzoiro_board_is_side_keyed_and_push_eligible():
    rows = [
        {"date": DAY, "kickoff": KICKOFF, "league": "Eerste Divisie",
         "home": "FC Dordrecht", "away": "Almere City", "market": "1x2",
         "selection": side, "odds": price, "bookmaker": "BookOne",
         "captured_at": "2026-09-25T08:00:00Z"}
        for side, price in BOARD.items()
    ]
    primary = pt._odds_bundle_from_rows(rows, provider=pt.BZZOIRO_ODDS_SOURCE)
    pick = _pick()
    pt.enrich_with_live_odds([pick], primary, None)
    assert pick["odds"] == 1.03 and pick["price_push_eligible"] is True
    assert [e["selection"] for e in pick["price_board"]] == ["home", "draw", "away"]


# ---------------- hard backstops ----------------

def test_row_labelled_for_another_side_is_never_assigned(monkeypatch):
    home_row = {"date": DAY, "home": "FC Dordrecht", "away": "Almere City",
                "market": "1x2", "selection": "home", "odds": 2.05,
                "bookmaker": "BookOne"}
    monkeypatch.setattr(pt, "find_odds_row", lambda *_: (home_row, "exact"))
    pick = _pick(odds=None)
    pt.enrich_with_live_odds([pick], {"provider": pt.BZZOIRO_ODDS_SOURCE, "exact": {}},
                             None)
    assert pick.get("odds") is None
    assert pick["price_push_eligible"] is False
    assert not any(e.get("chosen") for e in pick.get("price_board") or [])


def test_fuzzy_join_rejects_a_reversed_fixture_listing():
    # Only a reversed listing exists ("Almere City vs FC Dordrecht"); its
    # AWAY quote is Dordrecht's price. Bigram similarity alone scores ~1.0.
    reversed_row = _source_row(home="Almere City", away="FC Dordrecht",
                               odd1=1.03, oddx=3.00, odd2=2.05)
    bundle = _bundle([reversed_row])
    # Well above the 0.40 fuzzy-join threshold: without the orientation
    # guard this reversed row would have been accepted.
    assert pt.char_ngram_similarity("FC Dordrecht Almere City",
                                    "Almere City FC Dordrecht") > 0.8
    row, method = pt.find_odds_row(_pick(), bundle)
    assert row is None and method is None


def test_fuzzy_join_still_accepts_same_orientation_spelling_variant():
    bundle = _bundle([_source_row(home="Dordrecht FC", away="Almere City FC")])
    row, method = pt.find_odds_row(_pick(), bundle)
    if method == "alias_fuzzy":  # alias tables may already resolve it exactly
        assert row["selection"] == "away" and row["odds"] == 1.03
    else:
        assert row is not None and row["odds"] == 1.03


# ---------------- live ticket gate vs frozen replay ----------------

def test_unverified_scoutingstats_away_2_00_is_audit_only():
    """The incident row: kept (with its evidence) for audit, never ticketed."""
    pick = _pick()
    pt.enrich_with_live_odds([pick], _empty_primary(),
                             _bundle([_source_row(odd1=2.05, odd2=2.00)]))
    assert pick["odds"] == 2.00                      # evidence retained on the row
    assert pick["price_quarantine_reason"] == "scoutingstats_sole_source"
    assert pick["price_push_eligible"] is False

    assert at.playable_legs([pick], day=DAY, execution_safe=True) == []
    # Historical replay/audit callers keep the legacy pool (frozen parity).
    legacy = at.playable_legs([pick], day=DAY)
    assert len(legacy) == 1 and legacy[0]["odds"] == 2.00


def test_validated_away_quote_is_ticketed_at_its_own_price():
    pick = _pick(odds=1.45, odds_source="betexplorer_odds",
                 price_evidence="BETEXPLORER_RESCUE", price_push_eligible=True,
                 bucket="CAUTION")
    legs = at.playable_legs([pick], day=DAY, execution_safe=True)
    assert len(legs) == 1
    assert legs[0]["pick"] == "AWAY" and legs[0]["odds"] == 1.45


def test_validated_away_1_03_is_still_below_the_leg_floor():
    # Even a validated AWAY @ 1.03 never reaches a slip: the validated
    # MIN_LEG_ODDS floor excludes it. It must not be re-priced upward either.
    assert at.MIN_LEG_ODDS > 1.03
    pick = _pick(odds=1.03, odds_source="betexplorer_odds",
                 price_evidence="BETEXPLORER_RESCUE", price_push_eligible=True,
                 bucket="CAUTION")
    assert at.playable_legs([pick], day=DAY, execution_safe=True) == []
