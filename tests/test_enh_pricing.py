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
    assert idx == {"pairs": {}, "names": {}}
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
