"""Enhancement pricing join tests — real-price attachment, constraints, fail-soft."""
import csv
import gzip
import json
import math
from pathlib import Path

import pytest

from edgefactory.enh_pricing import (BETEXPLORER_SOURCE, ENH_BOARD_FLAG,
                                     MARKET_PRICE_MAP, attach_enhancement_price,
                                     load_prices_index)

ROOT = Path(__file__).resolve().parents[1]

COLS = ["source", "source_type", "sport", "date", "kickoff", "league", "home", "away",
        "market", "selection", "odds", "bookmaker", "captured_at"]


def _row(**kw):
    base = {"source": "theoddsapi", "source_type": "odds", "sport": "soccer",
            "date": "2026-08-03", "kickoff": "2026-08-03T17:00:00Z",
            "league": "Sweden Allsvenskan", "home": "Halmstads BK", "away": "IK Sirius",
            "market": "ou_2.5", "selection": "over", "odds": 1.44,
            "bookmaker": "BookA", "captured_at": "2026-08-03T10:57:00+00:00"}
    base.update(kw)
    return base


def _write_month(root, rows, month="2026-08"):
    ld = root / "localdata"
    ld.mkdir(parents=True, exist_ok=True)
    path = ld / f"theoddsapi_odds_{month}.csv.gz"
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path


SS_COLS = ["date", "kickoff", "league", "country", "home", "away", "hs", "gs", "status",
           "p1", "px", "p2", "p_o15", "p_o25", "p_o35", "p_gg", "p_ng",
           "odd1", "oddx", "odd2", "odd_o15", "odd_u15", "odd_o25", "odd_u25",
           "odd_o35", "odd_u35", "odd_gg", "odd_ng"]


def _ss_row(**kw):
    base = {"date": "2026-08-03", "kickoff": "2026-08-03 18:00:00",
            "league": "Sweden Allsvenskan", "country": "Sweden",
            "home": "Halmstads BK", "away": "IK Sirius", "hs": "", "gs": "",
            "status": "", "p1": 30, "px": 25, "p2": 45, "p_o15": 80, "p_o25": 55,
            "p_o35": 30, "p_gg": 52, "p_ng": 48, "odd1": 2.9, "oddx": 3.4,
            "odd2": 2.3, "odd_o15": 1.14, "odd_u15": 5.40, "odd_o25": 1.55,
            "odd_u25": 2.50, "odd_o35": 2.20, "odd_u35": 1.65,
            "odd_gg": 1.83, "odd_ng": 1.87}
    base.update(kw)
    return base


def _write_ss_month(root, rows, month="2026-08"):
    ld = root / "localdata"
    ld.mkdir(parents=True, exist_ok=True)
    path = ld / f"scoutingstats_{month}.csv.gz"
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SS_COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path


def _bzz_row(**kw):
    base = {"source": "bzzoiro_odds", "source_type": "odds", "sport": "soccer",
            "date": "2026-08-03", "kickoff": "2026-08-03T16:00:00Z",
            "league": "Sweden Allsvenskan", "home": "Halmstads BK", "away": "IK Sirius",
            "market": "btts", "selection": "yes", "odds": 1.95,
            "bookmaker": "BzBook", "captured_at": "2026-08-03T12:00:00+00:00"}
    base.update(kw)
    return base


def _write_bzz_month(root, rows, month="2026-08"):
    ld = root / "localdata"
    ld.mkdir(parents=True, exist_ok=True)
    path = ld / f"bzzoiro_odds_{month}.csv.gz"
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path


def _pick(**kw):
    base = {"home": "Halmstad", "away": "Sirius", "match": "Halmstad vs Sirius",
            "date": "2026-08-03", "recommended_enhancement": "match_over_25",
            "enhancement_probability": 0.709}
    base.update(kw)
    return base


def test_best_price_attached(tmp_path):
    _write_month(tmp_path, [
        _row(odds=1.44, bookmaker="BookA"),
        _row(odds=1.49, bookmaker="Nordic Bet"),
        _row(market="ou_2.5", selection="under", odds=2.62, bookmaker="BookC"),
        _row(market="1x2", selection="away", odds=1.40, bookmaker="BookA"),
    ])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_priced"] is True
    assert p["enhancement_price"] == 1.49 and p["enhancement_price_book"] == "Nordic Bet"
    assert p["enhancement_price_source"] == "theoddsapi"
    assert p["enhancement_mapped"] is True
    assert p["enhancement_breakeven"] == round(1 / 1.49, 4)
    assert p["enhancement_edge_sample"] == round(0.709 * 1.49 - 1.0, 4)


def test_unmapped_type_never_priced(tmp_path):
    _write_month(tmp_path, [_row()])
    assert MARKET_PRICE_MAP["goal_range_2_3"] is None
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(recommended_enhancement="goal_range_2_3"), idx)
    assert p["enhancement_mapped"] is False
    assert p["enhancement_priced"] is False
    assert p["enhancement_price"] is None


def test_missing_file_fail_soft(tmp_path):
    idx = load_prices_index(tmp_path, "2026-08-03")
    assert idx == {"pairs": {}, "spread": {}, "names": {}, "fixture_quotes": {}}
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_price"] is None  # explicit null, no raise


def test_pair_constrained_no_cross_contamination(tmp_path):
    # Decoy: away team matches but home does not -> must NOT attach the decoy price.
    _write_month(tmp_path, [
        _row(home="Hammarby", away="IK Sirius", odds=9.99, bookmaker="Decoy"),
        _row(home="Halmstads BK", away="IK Sirius", odds=1.49, bookmaker="Nordic Bet"),
    ])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_priced"] is True
    assert p["enhancement_price"] == 1.49 and p["enhancement_price_book"] == "Nordic Bet"


def test_swapped_orientation_matches(tmp_path):
    _write_month(tmp_path, [_row(home="IK Sirius", away="Halmstads BK", odds=1.49)])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_priced"] is True
    assert p["enhancement_price"] == 1.49


def test_no_probability_prices_without_edge(tmp_path):
    _write_month(tmp_path, [_row(odds=1.49)])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(enhancement_probability=None), idx)
    assert p["enhancement_priced"] is True
    assert p["enhancement_price"] == 1.49
    assert "enhancement_edge_sample" not in p


def test_hostile_odds_rows_rejected(tmp_path):
    # RT-2: NaN/inf slip past naive comparisons; 0/1.0/negatives/garbage are not prices.
    _write_month(tmp_path, [
        _row(odds="nan", bookmaker="NaNBook"),
        _row(odds="inf", bookmaker="InfBook"),
        _row(odds="1.0", bookmaker="FlatBook"),
        _row(odds="0", bookmaker="ZeroBook"),
        _row(odds="-2.5", bookmaker="NegBook"),
        _row(odds="garbage", bookmaker="JunkBook"),
        _row(odds="", bookmaker="EmptyBook"),
        _row(odds=1.49, bookmaker="Nordic Bet"),
    ])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_priced"] is True
    assert p["enhancement_price"] == 1.49 and p["enhancement_price_book"] == "Nordic Bet"
    assert math.isfinite(p["enhancement_breakeven"])
    assert math.isfinite(p["enhancement_edge_sample"])


def test_hostile_only_rows_leave_pick_unpriced(tmp_path):
    _write_month(tmp_path, [_row(odds="nan"), _row(odds="inf"), _row(odds="0")])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_priced"] is False and p["enhancement_price"] is None


def test_stale_fields_cleared_on_every_early_return(tmp_path):
    # RT-3: previously-derived price/breakeven/edge must NEVER survive a rerun that
    # can no longer derive them (mapping change, rotated index, missing selection).
    _write_month(tmp_path, [_row(odds=1.49)])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_priced"] is True
    attach_enhancement_price(p, idx)  # idempotent re-derive keeps the price
    assert p["enhancement_price"] == 1.49
    # (a) market becomes unmapped
    p["recommended_enhancement"] = "goal_range_2_3"
    attach_enhancement_price(p, idx)
    assert p["enhancement_price"] is None and p["enhancement_priced"] is False
    assert "enhancement_breakeven" not in p and "enhancement_edge_sample" not in p
    # (b) mapped but the day's pair is not in the index (stale archive field present)
    p["recommended_enhancement"] = "match_over_25"
    p["enhancement_price"] = 1.49
    p["enhancement_breakeven"] = 0.67
    attach_enhancement_price(p, {"pairs": {}, "names": {}})
    assert p["enhancement_price"] is None and p["enhancement_priced"] is False
    assert "enhancement_breakeven" not in p
    # (c) mapped + file exists, but rows are scoped to another day / mapped selection absent
    _write_month(tmp_path, [_row(market="1x2", selection="away", odds=1.40)], month="2026-09")
    idx2 = load_prices_index(tmp_path, "2026-09-01")
    p2 = _pick(date="2026-09-01")
    p2["enhancement_price"] = 1.49
    attach_enhancement_price(p2, idx2)
    assert p2["enhancement_price"] is None and p2["enhancement_priced"] is False


# ---------------------------------------------------------------- EXT v2 (multi-source)


def test_scoutingstats_wide_row_maps_ladder_and_btts(tmp_path):
    # Money-on-table: ss publishes 1.5/3.5 ladders + BTTS that theoddsapi lacks.
    _write_ss_month(tmp_path, [_ss_row()])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(recommended_enhancement="match_over_15"), idx)
    assert p["enhancement_price"] == 1.14 and p["enhancement_price_source"] == "scoutingstats"
    p = attach_enhancement_price(_pick(recommended_enhancement="match_under_15"), idx)
    assert p["enhancement_price"] == 5.40
    p = attach_enhancement_price(_pick(recommended_enhancement="match_over_35"), idx)
    assert p["enhancement_price"] == 2.20 and p["enhancement_price_book"] is None  # no book col
    p = attach_enhancement_price(_pick(recommended_enhancement="btts_yes"), idx)
    assert p["enhancement_price"] == 1.83 and p["enhancement_price_source"] == "scoutingstats"
    p = attach_enhancement_price(_pick(recommended_enhancement="btts_no"), idx)
    assert p["enhancement_price"] == 1.87
    assert "enhancement_price_divergence" not in p  # single source -> no spread record


def test_bzzoiro_unified_rows_price_btts_with_book(tmp_path):
    _write_bzz_month(tmp_path, [
        _bzz_row(selection="yes", odds=1.95, bookmaker="BzBook"),
        _bzz_row(selection="no", odds=1.80, bookmaker="BzOther"),
    ])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(recommended_enhancement="btts_yes"), idx)
    assert p["enhancement_price"] == 1.95
    assert p["enhancement_price_source"] == "bzzoiro_odds"
    assert p["enhancement_price_book"] == "BzBook"


def test_best_across_sources_wins_with_attribution_no_divergence(tmp_path):
    _write_month(tmp_path, [_row(odds=1.49, bookmaker="Nordic Bet")])
    _write_ss_month(tmp_path, [_ss_row(odd_o25=1.55)])  # +4% spread vs 1.49 -> under threshold
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_price"] == 1.55 and p["enhancement_price_source"] == "scoutingstats"
    assert p["enhancement_price_book"] is None
    assert "enhancement_price_divergence" not in p  # 4.03% < 10% -> not flagged
    # Governance N5: two AGREEING sources still count as multi-source verified
    # (the divergence flag is about disagreement, not verification)
    assert p["enhancement_multi_source"] is True


def test_divergence_flagged_when_sources_disagree_over_10pct(tmp_path):
    _write_month(tmp_path, [_row(odds=1.49, bookmaker="Nordic Bet")])
    _write_ss_month(tmp_path, [_ss_row(odd_o25=1.70)])  # +14.1% spread
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_price"] == 1.70 and p["enhancement_price_source"] == "scoutingstats"
    div = p.get("enhancement_price_divergence")
    assert div is not None
    assert div["theoddsapi"] == 1.49 and div["scoutingstats"] == 1.70
    assert p["enhancement_multi_source"] is True  # N5: >=2 sources priced it
    assert abs(div["spread_pct"] - round(1.70 / 1.49 - 1.0, 4)) < 1e-9  # stored rounded(4dp)
    # ...and the divergence record does not survive an unmapped re-derive (RT-3)
    p["recommended_enhancement"] = "goal_range_2_3"
    attach_enhancement_price(p, idx)
    assert "enhancement_price_divergence" not in p and p["enhancement_price"] is None


def test_each_source_day_scoped_independently(tmp_path):
    _write_ss_month(tmp_path, [_ss_row(date="2026-08-02", odd_gg=9.99)])  # wrong day
    _write_bzz_month(tmp_path, [_bzz_row(date="2026-08-04", odds=9.99)])  # wrong day
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(recommended_enhancement="btts_yes"), idx)
    assert p["enhancement_priced"] is False and p["enhancement_price"] is None


def test_swapped_orientation_matches_per_source(tmp_path):
    _write_ss_month(tmp_path, [_ss_row(home="IK Sirius", away="Halmstads BK", odd_gg=1.83)])
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(recommended_enhancement="btts_yes"), idx)
    assert p["enhancement_priced"] is True and p["enhancement_price"] == 1.83
    assert p["enhancement_multi_source"] is False  # scoutingstats is the only source here


def test_hostile_rows_rejected_at_every_source(tmp_path):
    _write_month(tmp_path, [_row(odds="inf"), _row(odds="garbage")])
    _write_ss_month(tmp_path, [_ss_row(odd_o15="nan", odd_gg="1.0", odd_o25="")])
    _write_bzz_month(tmp_path, [_bzz_row(odds="-1.5")])
    idx = load_prices_index(tmp_path, "2026-08-03")
    for mkt in ("match_over_25", "match_over_15", "btts_yes"):
        p = attach_enhancement_price(_pick(recommended_enhancement=mkt), idx)
        assert p["enhancement_priced"] is False, (mkt, p.get("enhancement_price"))


def test_unmapped_types_stay_unpriced_despite_feeds(tmp_path):
    # Operator override 2026-08-05 (Addendum 27.7): team totals / double
    # chance / ou_4.5 are now MAPPED to the OddsPapi capture (real prices);
    # goal ranges remain unmapped (no feed offers a banded market).
    _write_ss_month(tmp_path, [_ss_row()])
    _write_bzz_month(tmp_path, [_bzz_row()])
    idx = load_prices_index(tmp_path, "2026-08-03")
    for mkt in ("goal_range_2_3",):
        p = attach_enhancement_price(_pick(recommended_enhancement=mkt), idx)
        assert p["enhancement_mapped"] is False and p["enhancement_price"] is None, mkt


# ------------------------------------------------------------- betexplorer ---
# Stage 1: the schema-2 detail ledger the BetExplorer lane writes for every
# fixture it prices (localdata/betexplorer_match_detail_<day>.json) is a price
# source in its own right — multi-book O/U lines, BTTS and double chance from
# the comparison responses the priced lane already fetched. Reader:
# enh_pricing._accumulate_betexplorer. Zero network: the file is local.

BE_DAY = "2026-10-12"
BE_HOME, BE_AWAY = "Coventry", "Newcastle Utd"


@pytest.fixture(autouse=True)
def _enhancement_board_on(monkeypatch):
    """The board's own switch is ON for this module's assertions.

    Everything here describes what the board does; the switch itself is pinned
    by ``test_betexplorer_prices_are_behind_the_enhancement_board_flag`` below.
    """
    monkeypatch.setenv(ENH_BOARD_FLAG, "1")


def _be_key():
    from edgefactory.util import norm_team
    return (norm_team(BE_HOME), norm_team(BE_AWAY))


def _be_row(book, line, odds, *, best=False, created=None):
    return {"bookmaker": book, "bookmaker_id": None, "line": line, "source": "table",
            "odds": list(odds), "pos": [None] * len(odds),
            "created": list(created or [None] * len(odds)),
            "movement": [None] * len(odds), "best": best}


def _be_block(columns, lines, rows):
    return {"columns": list(columns), "lines": list(lines), "rows": list(rows),
            "rows_count": len(rows), "named_rows": len(rows),
            "bookmakers": sorted({row["bookmaker"] for row in rows}),
            "average": None, "average_by_line": None}


def _be_fixture(markets, *, home=BE_HOME, away=BE_AWAY, league="England: Premier League"):
    return {"event_id": "tW4rOkzg", "match_url": "https://www.betexplorer.com/x/",
            "kickoff": "21:00", "data_dt": [12, 10, 2026, 21, 0], "home": home, "away": away, "league": league,
            "captured_at": f"{BE_DAY}T06:00:00+00:00", "page_param": "1",
            "best_1x2": {"odd1": 3.10, "oddx": 3.60, "odd2": 2.20},
            "markets": markets, "market_failures": [], "page": None}


def _write_be_ledger(root, fixtures, *, day=BE_DAY, schema=2):
    ld = root / "localdata"
    ld.mkdir(parents=True, exist_ok=True)
    path = ld / f"betexplorer_match_detail_{day}.json"
    path.write_text(json.dumps({"schema": schema, "date": day,
                                "captured_at": f"{day}T09:05:00+00:00",
                                "fixtures": fixtures}))
    _write_be_witness(root, fixtures.values())
    return path


def _write_be_witness(root, fixtures):
    # Synthetic provider observations, deliberately separate from BE's page.
    rows = [{"source": "oddspapi", "source_type": "odds", "sport": "soccer",
             "home": f["home"], "away": f["away"], "kickoff": f"{BE_DAY}T20:00:00Z",
             "captured_at": f"{BE_DAY}T05:30:00Z"} for f in fixtures]
    if rows:
        with gzip.open(root / "localdata" / "oddspapi_odds_2026-10.csv.gz", "wt", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def _be_pick(market, **kw):
    base = {"home": BE_HOME, "away": BE_AWAY, "date": BE_DAY,
            "match": f"{BE_HOME} vs {BE_AWAY}", "recommended_enhancement": market,
            "enhancement_probability": 0.62, "kickoff_utc": f"{BE_DAY}T20:00:00Z",
            "as_of": f"{BE_DAY}T06:30:00Z"}
    base.update(kw)
    return base


FULL_BE_MARKETS = {
    "1x2": _be_block(["1", "X", "2"], ["0"], [_be_row("Stake.com", "0", [3.10, 3.60, 2.20])]),
    "ou": _be_block(["Over", "Under"], ["2.50"], [_be_row("Stake.com", "2.50", [3.40, 1.30],
                                                          best=True)]),
    "bts": _be_block(["Yes", "No"], ["0"], [_be_row("bet365.us", "0", [1.57, 2.25])]),
    "dc": _be_block(["1X", "12", "X2"], ["0"], [_be_row("bet365.us", "0", [1.26, 1.36, 2.05])]),
}


def test_betexplorer_ledger_prices_totals_btts_and_double_chance(tmp_path):
    _write_be_ledger(tmp_path, {"2026-10-12|coventry|newcastleutd": _be_fixture(FULL_BE_MARKETS)})
    index = load_prices_index(tmp_path, BE_DAY)
    key = _be_key()

    over = index["pairs"][key][("ou_2.5", "over")]
    assert over[0] == 3.40 and over[1] == "Stake.com" and over[3] == BETEXPLORER_SOURCE
    assert index["pairs"][key][("ou_2.5", "under")][:2] == (1.30, "Stake.com")
    assert index["pairs"][key][("btts", "yes")][:2] == (1.57, "bet365.us")
    assert index["pairs"][key][("btts", "no")][:2] == (2.25, "bet365.us")
    assert index["pairs"][key][("dc", "1x")][:2] == (1.26, "bet365.us")
    # 1x2 / ah / ha are retained evidence only: no enhancement maps to them.
    assert not [slot for slot in index["pairs"][key] if slot[0] in {"1x2", "ah", "ha"}]

    for market, price, book in (("match_over_25", 3.40, "Stake.com"),
                               ("match_under_25", 1.30, "Stake.com"),
                               ("btts_yes", 1.57, "bet365.us"),
                               ("double_chance", 1.26, "bet365.us")):
        pick = attach_enhancement_price(_be_pick(market, pick="home"), index)
        assert pick["enhancement_priced"] is True, market
        assert pick["enhancement_price"] == price, market
        assert pick["enhancement_price_source"] == BETEXPLORER_SOURCE, market
        assert pick["enhancement_price_book"] == book, market


def test_betexplorer_best_flagged_row_wins_else_the_highest_retained_row(tmp_path):
    """The site's own best-price flag decides; without one, the highest wins."""
    _write_be_ledger(tmp_path, {"k": _be_fixture({"ou": _be_block(
        ["Over", "Under"], ["2.50", "3.50"], [
            _be_row("BookHigh", "2.50", [4.20, 1.22]),               # higher, unflagged
            _be_row("BookFlagged", "2.50", [3.60, 1.32], best=True),  # the flag wins
            _be_row("BookLow", "3.50", [2.20, 1.70]),
            _be_row("BookTop", "3.50", [2.50, 1.55]),                # no flag on 3.50
        ])})})
    index = load_prices_index(tmp_path, BE_DAY)
    key = _be_key()
    assert index["pairs"][key][("ou_2.5", "over")][:2] == (3.60, "BookFlagged")
    assert index["pairs"][key][("ou_2.5", "under")][:2] == (1.32, "BookFlagged")
    assert index["pairs"][key][("ou_3.5", "over")][:2] == (2.50, "BookTop")
    assert index["pairs"][key][("ou_3.5", "under")][:2] == (1.70, "BookLow")


def test_betexplorer_column_order_comes_from_the_blocks_own_columns(tmp_path):
    # Reversed column order, same prices: positional reading would swap Over
    # and Under. The capture keeps the site's labels, so the labels decide.
    _write_be_ledger(tmp_path, {"k": _be_fixture({"ou": _be_block(["Under", "Over"], ["2.50"], [
        _be_row("BookA", "2.50", [1.30, 3.40])])})})
    index = load_prices_index(tmp_path, BE_DAY)
    key = _be_key()
    assert index["pairs"][key][("ou_2.5", "over")][:2] == (3.40, "BookA")
    assert index["pairs"][key][("ou_2.5", "under")][:2] == (1.30, "BookA")

    # An unknown/incomplete column set invalidates the entire block.
    _write_be_ledger(tmp_path, {"k": _be_fixture({"bts": _be_block(["GG", "Yes"], ["0"], [
        _be_row("BookA", "0", [9.90, 1.80])])})})
    index = load_prices_index(tmp_path, BE_DAY)
    assert index["pairs"] == {}  # an incomplete/unknown column set invalidates the block


def test_betexplorer_line_outside_the_blocks_lines_prices_nothing(tmp_path):
    """A line the capture did not retain has no evidence to price from.

    ``lines`` is the capture's own record of what survived its per-market cap;
    a row whose line is absent from it is dropped here, so nothing is priced
    off a line the ledger does not claim to hold.
    """
    _write_be_ledger(tmp_path, {"k": _be_fixture({"ou": _be_block(["Over", "Under"], ["2.50"], [
        _be_row("BookA", "2.50", [3.30, 1.35]),
        _be_row("BookB", "4.50", [9.00, 1.06]),
    ])})})
    index = load_prices_index(tmp_path, BE_DAY)
    key = _be_key()
    assert ("ou_2.5", "over") in index["pairs"][key]
    assert ("ou_4.5", "over") not in index["pairs"][key]
    assert load_prices_index(tmp_path, BE_DAY)["pairs"][key].get(("ou_4.5", "under")) is None


def test_betexplorer_ledger_cannot_price_team_totals(tmp_path):
    """Team totals are not among the six retained tabs — they stay unpriced.

    Nothing in this source may price them: the slots the overlay maps team
    totals to (tt_home_0.5, tt_away_1.5, ...) are never written here, and a
    slug the ledger does not define is ignored outright.
    """
    markets = dict(FULL_BE_MARKETS)
    markets["tt"] = _be_block(["Over", "Under"], ["0.50"], [_be_row("BookA", "0.50", [1.10, 7.5])])
    _write_be_ledger(tmp_path, {"k": _be_fixture(markets)})
    index = load_prices_index(tmp_path, BE_DAY)
    key = _be_key()
    assert not [slot for slot in index["pairs"][key] if slot[0].startswith("tt_")]
    for market in ("home_over_05", "away_over_15", "home_under_25", "away_under_35"):
        pick = attach_enhancement_price(_be_pick(market), index)
        assert pick["enhancement_mapped"] is True, market   # a real market, just not from here
        assert pick["enhancement_priced"] is False, market
        assert pick["enhancement_price_source"] is None, market


def test_betexplorer_ledger_fail_soft_on_missing_corrupt_or_foreign_files(tmp_path):
    # No ledger at all.
    assert load_prices_index(tmp_path, BE_DAY)["pairs"] == {}
    ld = tmp_path / "localdata"
    ld.mkdir(parents=True, exist_ok=True)
    ledger = ld / f"betexplorer_match_detail_{BE_DAY}.json"
    # Unreadable JSON.
    ledger.write_text("{not json")
    assert load_prices_index(tmp_path, BE_DAY)["pairs"] == {}
    # A foreign schema generation is not read (the capture writes 2).
    _write_be_ledger(tmp_path, {"k": _be_fixture(FULL_BE_MARKETS)}, schema=1)
    assert load_prices_index(tmp_path, BE_DAY)["pairs"] == {}
    # Right file name, wrong day inside: another day's fixtures price nothing.
    ledger.write_text(json.dumps({"schema": 2, "date": "2026-10-11",
                                  "fixtures": {"k": _be_fixture(FULL_BE_MARKETS)}}))
    assert load_prices_index(tmp_path, BE_DAY)["pairs"] == {}
    # fixtures missing / not a mapping / an entry without teams.
    ledger.write_text(json.dumps({"schema": 2, "date": BE_DAY}))
    assert load_prices_index(tmp_path, BE_DAY)["pairs"] == {}
    ledger.write_text(json.dumps({"schema": 2, "date": BE_DAY, "fixtures": []}))
    assert load_prices_index(tmp_path, BE_DAY)["pairs"] == {}
    ledger.write_text(json.dumps({"schema": 2, "date": BE_DAY, "fixtures": {
        "k": {"markets": FULL_BE_MARKETS}}}))
    assert load_prices_index(tmp_path, BE_DAY)["pairs"] == {}


def test_betexplorer_price_merges_with_the_other_sources_by_best_price(tmp_path):
    """One index, several sources: the best price wins and keeps its own book."""
    _write_month(tmp_path, [_row(date=BE_DAY, home=BE_HOME, away=BE_AWAY,
                                 odds=2.60, bookmaker="BookA")], month="2026-10")
    _write_be_ledger(tmp_path, {"k": _be_fixture(FULL_BE_MARKETS)})
    index = load_prices_index(tmp_path, BE_DAY)
    key = _be_key()
    over = index["pairs"][key][("ou_2.5", "over")]
    assert (over[0], over[1], over[3]) == (3.40, "Stake.com", BETEXPLORER_SOURCE)
    assert index["spread"][key][("ou_2.5", "over")] == {"theoddsapi": 2.60,
                                                        BETEXPLORER_SOURCE: 3.40}


def test_betexplorer_below_floor_price_is_priced_but_refused_by_the_gate(tmp_path):
    """The reader carries no EV or floor veto; the floor gate is the arbiter.

    A real 1.55 over-2.5 price is attached with its attribution and then
    refused by the Stage 2 gate — betting on EV "will lead us to not bet at
    all", so the floor decides, not the reader.
    """
    from edgefactory.enh_registry import clears_floor
    _write_be_ledger(tmp_path, {"k": _be_fixture({"ou": _be_block(["Over", "Under"], ["2.50"], [
        _be_row("BookA", "2.50", [1.55, 2.45], best=True)])})})
    index = load_prices_index(tmp_path, BE_DAY)
    pick = attach_enhancement_price(_be_pick("match_over_25"), index)
    assert pick["enhancement_priced"] is True and pick["enhancement_price"] == 1.55
    assert pick["enhancement_price_source"] == BETEXPLORER_SOURCE
    assert clears_floor("match_over_25", pick["enhancement_price"]) is False


def test_betexplorer_ledger_round_trips_through_the_capture_writer(tmp_path, monkeypatch):
    """Producer -> consumer: the capture lane's own ledger, read by this reader.

    The reader must not be trusted because it matches a written spec. This test
    drives the REAL producer — the capture lane's recorded markup through
    betexplorer_odds_rows_for_pick, which retains the ledger as a side effect —
    and then the REAL reader, and asserts the prices that come out are the ones
    the markup showed. It also proves the read adds no request: the adapter's
    transport is replaced by one that fails the test if called.
    """
    import test_betexplorer_match_detail as produced

    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(be, "LOCALDATA", tmp_path / "localdata")
    from datetime import datetime, timezone
    class SnapshotClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 12, 6, tzinfo=timezone.utc)
    monkeypatch.setattr(be, "datetime", SnapshotClock)
    rows = produced._run_pick()
    # Real provider producer -> actual monthly gzip writer -> shared loader.
    # The clock is synthetic and explicit; no historical operational data is written.
    from edgefactory.sources import theoddsapi as oa
    from scripts import capture_theodds as capture_oa
    class ProviderClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 12, 5, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(oa, "datetime", ProviderClock)
    monkeypatch.setattr(capture_oa, "LOCALDATA", tmp_path / "localdata")
    event = dict(id="synthetic-independent-event", home_team=produced.PICK["home"],
                 away_team=produced.PICK["away"], commence_time=f"{BE_DAY}T20:00:00Z")
    payload = dict(bookmakers=[dict(title="Provider Book", markets=[dict(key="totals", outcomes=[
        dict(name="Over", point=2.5, price=1.8), dict(name="Under", point=2.5, price=1.9)])])])
    provider_rows = oa.rows_from_event_odds(produced.PICK, event, payload)
    assert capture_oa.append_rows(BE_DAY, provider_rows, oa.COLUMNS) == 2
    assert [row["market"] for row in rows] == ["1x2"] * 3       # the priced lane is unchanged
    assert (tmp_path / "localdata" / produced.LEDGER).exists()

    def _no_request(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("pricing from the ledger must make no request")

    monkeypatch.setattr(be, "_fetch", _no_request)
    index = load_prices_index(tmp_path, BE_DAY)
    key = _be_key()

    over = index["pairs"][key][("ou_2.5", "over")]
    # Line 2.50 from the capture's all-bookmakers block (Stake.com 3.40/1.30).
    assert (over[0], over[1], over[3]) == (3.40, "Stake.com", BETEXPLORER_SOURCE)
    assert index["pairs"][key][("ou_2.5", "under")][:2] == (1.90, "Provider Book")
    assert any(q[:2] == (1.30, "Stake.com") for q in index["fixture_quotes"][key][("ou_2.5", "under")])
    assert index["pairs"][key][("btts", "yes")][:2] == (1.57, "bet365.us")
    assert index["pairs"][key][("btts", "no")][:2] == (2.25, "bet365.us")
    assert index["pairs"][key][("dc", "1x")][:2] == (1.26, "bet365.us")
    # The fixture's page carries no 1.5 line: nothing is invented for it.
    assert ("ou_1.5", "over") not in index["pairs"][key]

    pick = attach_enhancement_price(
        _be_pick("match_over_25", home=produced.PICK["home"], away=produced.PICK["away"]), index)
    assert pick["enhancement_priced"] is True
    assert pick["enhancement_price"] == 3.40
    assert pick["enhancement_price_source"] == BETEXPLORER_SOURCE
    receipt = pick["enhancement_price_provenance"]
    assert receipt["resolution"]["witnesses"][0]["source"] == "theoddsapi"
    assert pick["enhancement_price_at"] == f"{BE_DAY}T06:00:00+00:00"
    # Actual live gate and recipe carry: not merely audit eligibility.
    from scripts import auto_tickets as at
    from enhancement_fixtures import with_evidence
    class DecisionClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 12, 6, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(at, "datetime", DecisionClock)
    pick = with_evidence(pick)
    other = with_evidence(dict(pick, home="Other Home", away="Other Away", match="Other Match",
                               enhancement_price_source="oddspapi", enhancement_price_provenance=None))
    legs = at.enhancement_legs([pick, other], execution_safe=True)
    assert all(leg["verdict"] == "fire" for leg in legs)
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, 100.)
    at._carry_lane_evidence(plan, pool)
    assert any(leg["price_provenance"] == receipt for acca in plan for leg in acca["legs"])


def test_picks_today_loads_the_price_index_after_the_betexplorer_rescue():
    """Same-run ordering, pinned where it matters: at the call site.

    The rescue's fetch retains the day's detail ledger; the ledger is a price
    source. Loading the index before the rescue would read the file as it stood
    when the run started, so a fixture rescued in this very run could never
    price — and no later step re-reads the index. Pinned by source position
    because the alternative (driving the whole main() card build) measures
    everything except this ordering.
    """
    source = (ROOT / "scripts/picks_today.py").read_text()
    rescue = source.index("be_enriched = enrich_unmatched_with_betexplorer(")
    load = source.index("prices_index = load_prices_index(ROOT, day)")
    assert rescue < load


def test_betexplorer_prices_are_behind_the_enhancement_board_flag(tmp_path, monkeypatch):
    """Round-2 ruling (2026-10-12): the ledger prices only while the board is on.

    Same input, same bytes. With EDGE_FACTORY_ENH_BOARD unset the day's detail
    ledger contributes nothing at all — the index is exactly the index the
    pipeline built before this source existed, so the board renders as it does
    today. With the switch on the same file prices the same cells.
    """
    _write_be_ledger(tmp_path, {"2026-10-12|coventry|newcastleutd": _be_fixture(FULL_BE_MARKETS)})
    key = _be_key()

    monkeypatch.setenv(ENH_BOARD_FLAG, "1")
    on = load_prices_index(tmp_path, BE_DAY)
    monkeypatch.delenv(ENH_BOARD_FLAG)
    off = load_prices_index(tmp_path, BE_DAY)

    assert on["pairs"][key][("ou_2.5", "over")][0] == 3.40
    assert on["spread"][key][("ou_2.5", "over")][BETEXPLORER_SOURCE] == 3.40
    assert off["pairs"] == {} and off["spread"] == {} and off["names"] == {}

    # And the gate is the price path itself, not just the index shape: the same
    # pick is priced from the ledger with the switch on, and unpriced with it off.
    priced = attach_enhancement_price(_be_pick("match_over_25"), on)
    assert priced["enhancement_priced"] is True
    assert priced["enhancement_price"] == 3.40
    assert priced["enhancement_price_source"] == BETEXPLORER_SOURCE
    unpriced = attach_enhancement_price(_be_pick("match_over_25"), off)
    assert unpriced["enhancement_price"] is None
    assert unpriced["enhancement_priced"] is False
    assert unpriced["enhancement_mapped"] is True
