"""Option C price-quality gate (2026-10-02, operator sign-off).

A real-money leg needs price CORROBORATION: a second, distinct source quoting
the same market+selection within 7% of the chosen price. Receipt that drove
it: the 2026-10-01 money card rode 4/4 single-source BETEXPLORER_RESCUE
quotes after the primary board delivered nothing — a sole-source quote is
audit evidence, not an execution price.

Pins: _stamp_price_corroboration semantics (in-band corroborates, dissenting/
missing/other-side does not, chosen source never corroborates itself) and the
execution_safe money-lane gate in playable_legs (corroborated=False dropped,
corroborated=True kept, legacy archives without the field keep parity).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import scripts.picks_today as pt  # noqa: E402

BE = "betexplorer_odds"
BZZ = "bzzoiro_odds"
SS = "scoutingstats_odds"


def _board_entry(source, selection, odds, market="1x2"):
    return {"source": source, "selection": selection, "odds": odds,
            "market": market, "bookmaker": "Book", "captured_at": "2026-10-02T08:00:00Z"}


def _pick(**extra):
    out = {
        "date": "2026-10-02", "home": "Alpha United", "away": "Beta City",
        "match": "Alpha United vs Beta City", "market": "1x2", "pick": "home",
        "avg_p": 72.0, "odds": 1.50, "odds_source": BE,
        "price_board": [], "price_push_eligible": True,
    }
    out.update(extra)
    return out


# ---- stamping ----

def test_second_source_within_band_corroborates():
    p = _pick(price_board=[_board_entry(BE, "home", 1.50),
                           _board_entry(BZZ, "home", 1.55),   # +3.3%: corroborates
                           _board_entry(SS, "home", 1.90)])   # +27%: does not
    n = pt._stamp_price_corroboration([p])
    assert n == 1
    assert p["price_corroborated"] is True
    assert p["price_corroborators"] == [BZZ]


def test_all_board_entries_out_of_band_is_sole_source():
    p = _pick(price_board=[_board_entry(BE, "home", 1.50),
                           _board_entry(SS, "home", 1.62)])    # +8% > 7% band
    n = pt._stamp_price_corroboration([p])
    assert n == 0
    assert p["price_corroborated"] is False
    assert p["price_corroborators"] == []


def test_empty_board_means_uncorroborated():
    p = _pick()
    pt._stamp_price_corroboration([p])
    assert p["price_corroborated"] is False


def test_other_side_or_market_does_not_corroborate():
    p = _pick(price_board=[_board_entry(BZZ, "away", 1.50),          # wrong side
                           _board_entry(BZZ, "home", 1.50, market="ou_2.5")])  # wrong market
    pt._stamp_price_corroboration([p])
    assert p["price_corroborated"] is False


def test_chosen_source_never_corroborates_itself():
    p = _pick(price_board=[_board_entry(BE, "home", 1.49),
                           _board_entry(BE, "home", 1.52, )])
    pt._stamp_price_corroboration([p])
    assert p["price_corroborated"] is False


def test_unpriced_pick_is_uncorroborated():
    p = _pick(odds=None, price_board=[_board_entry(BZZ, "home", 1.50)])
    pt._stamp_price_corroboration([p])
    assert p["price_corroborated"] is False


# ---- money-lane gate (execution_safe) ----

def _card_row(**extra):
    out = {"date": "2026-10-02", "home": "Alpha United", "away": "Beta City",
           "market": "1x2", "pick": "home", "avg_p": 72.0, "odds": 1.50,
           "bucket": "CAUTION", "quarantine": "none", "price_push_eligible": True}
    out.update(extra)
    return out


def test_execution_safe_drops_uncorroborated_money_price():
    rows = [_card_row(price_corroborated=False), _card_row(price_corroborated=True)]
    pool = at.playable_legs(rows, day="2026-10-02", execution_safe=True)
    assert len(pool) == 1


def test_replay_parity_keeps_uncorroborated_rows():
    rows = [_card_row(price_corroborated=False)]
    assert len(at.playable_legs(rows, day="2026-10-02", execution_safe=False)) == 1
    # legacy archives without the field (None) keep parity in both modes
    rows2 = [_card_row()]
    assert len(at.playable_legs(rows2, day="2026-10-02", execution_safe=True)) == 1
    assert len(at.playable_legs(rows2, day="2026-10-02", execution_safe=False)) == 1
