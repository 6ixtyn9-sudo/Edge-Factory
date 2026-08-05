"""OddsPapi -> enhancement pricing wiring tests (Addendum 27.7, operator override).

Covers: multi-market parsing (1x2/btts/dc/team_totals/totals), unified
schema, the unified-store merge into `load_prices_index`, and real-price
attachment for markets that were previously "synthetic/none".
"""
import csv
import gzip

from edgefactory.enh_pricing import (ODDSPAPI_SOURCE, attach_enhancement_price,
                                     load_prices_index)
from edgefactory.sources.oddspapi_odds import rows_from_odds_response

COLS = ["source", "source_type", "sport", "date", "kickoff", "league", "home", "away",
        "market", "selection", "odds", "bookmaker", "captured_at"]


def _odds_payload(**over):
    data = {
        "fixtureId": "fx_1",
        "participant1Name": "Halmstads BK",
        "participant2Name": "IK Sirius",
        "startTime": "2026-08-03T17:00:00Z",
        "tournamentName": "Allsvenskan",
        "categoryName": "Sweden",
        "bookmakerOdds": {
            "Pinnacle": {"markets": {
                "101": {"outcomes": {
                    "o1": {"players": {"0": {"bookmakerOutcomeId": "home", "price": 2.10}}},
                    "ox": {"players": {"0": {"bookmakerOutcomeId": "draw", "price": 3.40}}},
                    "o2": {"players": {"0": {"bookmakerOutcomeId": "away", "price": 3.25}}},
                }},
                "103": {"outcomes": {
                    "b1": {"players": {"0": {"name": "Yes", "price": 1.95}}},
                }},
                "108": {"outcomes": {
                    "d1": {"players": {"0": {"name": "HomeOrDraw", "price": 1.05}}},
                }},
                "115": {"outcomes": {
                    "t1": {"players": {"0": {"name": "Halmstads BK Over 1.5", "price": 1.30}}},
                }},
                "107": {"outcomes": {
                    "t3": {"players": {"0": {"name": "Over 2.5", "price": 1.85}}},
                }},
            }},
        },
    }
    data.update(over)
    return data


def _write_oddspapi_month(root, rows, month="2026-08"):
    ld = root / "localdata"
    ld.mkdir(parents=True, exist_ok=True)
    path = ld / f"oddspapi_odds_{month}.csv.gz"
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path


def _pick(**kw):
    base = {"home": "Halmstad", "away": "Sirius", "match": "Halmstad vs Sirius",
            "date": "2026-08-03", "recommended_enhancement": "match_over_25",
            "enhancement_probability": 0.709, "pick": "home"}
    base.update(kw)
    return base


def test_oddspapi_parser_multimarket():
    rows = rows_from_odds_response(_odds_payload())
    markets = {(r["market"], r["selection"]) for r in rows}
    assert ("1x2", "home") in markets and ("1x2", "draw") in markets and ("1x2", "away") in markets
    assert ("btts", "yes") in markets
    assert ("dc", "1x") in markets
    assert ("tt_home_1.5", "over") in markets
    assert ("ou_2.5", "over") in markets
    assert all(r["source"] == "oddspapi" for r in rows)
    assert all(set(COLS) <= set(r.keys()) for r in rows)


def test_oddspapi_unknown_market_ids_skipped():
    payload = _odds_payload()
    payload["bookmakerOdds"]["Pinnacle"]["markets"]["999"] = {
        "outcomes": {"x": {"players": {"0": {"name": "Mystery", "price": 5.0}}}}}
    rows = rows_from_odds_response(payload)
    assert all(r["market"] != "?" for r in rows)
    assert all(("999" not in str(r["market"])) for r in rows)


def test_oddspapi_team_totals_side_matching():
    # swapped outcome order must still map to the right side
    payload = _odds_payload()
    payload["bookmakerOdds"]["Pinnacle"]["markets"]["115"] = {"outcomes": {
        "t2": {"players": {"0": {"name": "IK Sirius Under 1.5", "price": 2.10}}}}}
    rows = rows_from_odds_response(payload)
    assert ("tt_away_1.5", "under") in {(r["market"], r["selection"]) for r in rows}


def test_enh_pricing_oddspapi_is_4th_source(tmp_path):
    # oddspapi prices a market that theoddsapi does not: team totals over 1.5
    rows = rows_from_odds_response(_odds_payload())
    _write_oddspapi_month(tmp_path, rows)
    idx = load_prices_index(tmp_path, "2026-08-03")
    # team-totals price present, attributed to oddspapi
    p = attach_enhancement_price(
        _pick(recommended_enhancement="home_over_15", enhancement_probability=0.85), idx)
    assert p["enhancement_priced"] is True
    assert p["enhancement_price"] == 1.30
    assert p["enhancement_price_source"] == ODDSPAPI_SOURCE
    # double_chance: pick-side derived (home -> 1x)
    p2 = attach_enhancement_price(
        _pick(recommended_enhancement="double_chance", enhancement_probability=0.95), idx)
    assert p2["enhancement_priced"] is True
    assert p2["enhancement_price"] == 1.05
    assert p2["enhancement_price_source"] == ODDSPAPI_SOURCE


def test_enh_pricing_missing_oddspapi_file_is_noop(tmp_path):
    idx = load_prices_index(tmp_path, "2026-08-03")  # no oddspapi file
    p = attach_enhancement_price(_pick(recommended_enhancement="home_over_15"), idx)
    assert p["enhancement_priced"] is False
    assert p["enhancement_price"] is None
