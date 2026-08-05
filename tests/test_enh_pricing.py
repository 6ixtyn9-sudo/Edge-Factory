"""Enhancement pricing join tests — real-price attachment, constraints, fail-soft."""
import csv
import gzip
import math

from edgefactory.enh_pricing import (MARKET_PRICE_MAP, attach_enhancement_price,
                                     load_prices_index)

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
    base = {"source": "bzzoiro", "source_type": "odds", "sport": "soccer",
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
    assert idx == {"pairs": {}, "spread": {}, "names": {}}
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


def test_divergence_flagged_when_sources_disagree_over_10pct(tmp_path):
    _write_month(tmp_path, [_row(odds=1.49, bookmaker="Nordic Bet")])
    _write_ss_month(tmp_path, [_ss_row(odd_o25=1.70)])  # +14.1% spread
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(), idx)
    assert p["enhancement_price"] == 1.70 and p["enhancement_price_source"] == "scoutingstats"
    div = p.get("enhancement_price_divergence")
    assert div is not None
    assert div["theoddsapi"] == 1.49 and div["scoutingstats"] == 1.70
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
