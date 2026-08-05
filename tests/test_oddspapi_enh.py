"""OddsPapi -> enhancement pricing wiring tests (Addendum 27.7, operator override).

Hermetic flag: this file exercises the oddspapi price path, so the
EDGE_FACTORY_ODDSPAPI_PRICES flag is set for every test here (the flag-gate
test manages its own env). The global conftest strips it by default.
"""
import pytest


@pytest.fixture(autouse=True)
def _oddspapi_enabled(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ODDSPAPI_PRICES", "1")


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
    rows = rows_from_odds_response(_odds_payload(), market_type_map={
    "101": "1x2", "103": "btts", "108": "double_chance",
    "115": "team_totals", "107": "totals"})
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
    rows = rows_from_odds_response(payload, market_type_map={"101": "1x2"})
    assert all(r["market"] != "?" for r in rows)
    assert all(("999" not in str(r["market"])) for r in rows)


def test_oddspapi_team_totals_side_matching():
    # swapped outcome order must still map to the right side
    payload = _odds_payload()
    payload["bookmakerOdds"]["Pinnacle"]["markets"]["115"] = {"outcomes": {
        "t2": {"players": {"0": {"name": "IK Sirius Under 1.5", "price": 2.10}}}}}
    rows = rows_from_odds_response(payload, market_type_map={"101": "1x2", "115": "team_totals"})
    assert ("tt_away_1.5", "under") in {(r["market"], r["selection"]) for r in rows}


def test_enh_pricing_oddspapi_is_4th_source(tmp_path):
    # oddspapi prices a market that theoddsapi does not: team totals over 1.5
    rows = rows_from_odds_response(_odds_payload(), market_type_map={
    "101": "1x2", "103": "btts", "108": "double_chance",
    "115": "team_totals", "107": "totals"})
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


def test_classify_label_goals_only():
    from edgefactory.sources.oddspapi_odds import _classify_label
    # goal markets classify
    assert _classify_label("Total Goals Over/Under 2.5") == "totals"
    assert _classify_label("Over Under Full Time") == "totals"
    assert _classify_label("Both Teams To Score") == "btts"
    assert _classify_label("Both Teams To Score First Half") == "btts"
    assert _classify_label("Double Chance Full Time") == "double_chance"
    assert _classify_label("1X2") == "1x2"
    assert _classify_label("Full Time Result") == "1x2"
    assert _classify_label("Match Winner") == "1x2"
    # team totals: side lives in the LABEL ("Over Under Team 1/2")
    assert _classify_label("Over Under Team 1") == "team_totals_home"
    assert _classify_label("Over Under Team 2") == "team_totals_away"
    assert _classify_label("Team Total Goals (Home)") == "team_totals_home"
    # the "ng" substring bug: "winning"/"innings" must NOT become btts
    assert _classify_label("Winning Margin Full Time") == ""
    assert _classify_label("Over Under (incl. extra innings)") == ""
    # non-goal markets are REJECTED (never guessed into the unified schema)
    assert _classify_label("Total Corners Over/Under 8.5") == ""
    assert _classify_label("Total Cards Over/Under 4.5") == ""
    assert _classify_label("Match Shots On Target") == ""
    # ambiguous labels are not guessed
    assert _classify_label("Random Market") == ""


def test_totals_line_in_separate_field():
    # Real OddsPapi shape: outcome name may be just "Over"/"Under" with the
    # line in a separate field (line/point/value). Must still parse.
    from edgefactory.sources.oddspapi_odds import rows_from_odds_response
    payload = {
        "fixtureId": "fx_line", "participant1Name": "Halmstads BK",
        "participant2Name": "IK Sirius", "startTime": "2026-08-03T17:00:00Z",
        "tournamentName": "Allsvenskan", "categoryName": "Sweden",
        "bookmakerOdds": {"Pinnacle": {"markets": {
            "106": {"outcomes": {
                "o1": {"players": {"0": {"name": "Over", "price": 1.85, "line": 2.5}}},
                "o2": {"players": {"0": {"name": "Under", "price": 1.95, "line": 2.5}}},
            }},
            "10224": {"outcomes": {
                "t1": {"players": {"0": {"name": "Over", "price": 1.70, "line": 1.5}}},
            }},
            "101": {"outcomes": {
                "x1": {"players": {"0": {"bookmakerOutcomeId": "home", "price": 2.10}}},
            }},
        }}},
    }
    rows = rows_from_odds_response(payload, market_type_map={
        "101": "1x2", "106": "totals", "10224": "team_totals_home"})
    markets = {(r["market"], r["selection"]) for r in rows}
    assert ("ou_2.5", "over") in markets
    assert ("ou_2.5", "under") in markets
    assert ("tt_home_1.5", "over") in markets
    assert ("1x2", "home") in markets


# --- Red-team fixes (2026-08-05) ---


def test_oddspapi_flag_gate_controls_merge(tmp_path, monkeypatch):
    # F6: the oddspapi store must NOT merge without EDGE_FACTORY_ODDSPAPI_PRICES=1
    rows = rows_from_odds_response(_odds_payload(), market_type_map={
        "101": "1x2", "103": "btts", "108": "double_chance",
        "115": "team_totals", "107": "totals"})
    _write_oddspapi_month(tmp_path, rows)
    monkeypatch.delenv("EDGE_FACTORY_ODDSPAPI_PRICES", raising=False)
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(recommended_enhancement="home_over_15"), idx)
    assert p["enhancement_priced"] is False  # store ignored without flag
    monkeypatch.setenv("EDGE_FACTORY_ODDSPAPI_PRICES", "1")
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(_pick(recommended_enhancement="home_over_15"), idx)
    assert p["enhancement_priced"] is True and p["enhancement_price_source"] == ODDSPAPI_SOURCE


def test_oddspapi_inactive_outcomes_dropped():
    # F2: marketActive=False and player active=False must be dropped
    payload = _odds_payload()
    payload["bookmakerOdds"]["Pinnacle"]["markets"]["101"] = {
        "marketActive": False, "outcomes": {
            "o1": {"players": {"0": {"bookmakerOutcomeId": "home", "price": 2.10}}}}}
    payload["bookmakerOdds"]["Pinnacle"]["markets"]["103"] = {"outcomes": {
        "b1": {"players": {"0": {"name": "Yes", "price": 1.95, "active": False}}}}}
    rows = rows_from_odds_response(payload, market_type_map={
        "101": "1x2", "103": "btts", "108": "double_chance",
        "115": "team_totals", "107": "totals"})
    markets = {(r["market"], r["selection"]) for r in rows}
    assert ("1x2", "home") not in markets   # market inactive
    assert ("btts", "yes") not in markets   # outcome inactive


def test_oddspapi_captured_at_is_capture_time():
    # F2: captured_at must be OUR capture time, not the provider updatedAt
    payload = _odds_payload()
    payload["updatedAt"] = "2020-01-01T00:00:00Z"  # stale provider stamp
    rows = rows_from_odds_response(payload, market_type_map={
        "101": "1x2", "103": "btts", "108": "double_chance",
        "115": "team_totals", "107": "totals"})
    # capture time, not the provider's stale 2020 stamp (audit N3: no
    # hardcoded month — assert it is NOT the provider stamp and is recent)
    import datetime as _dt
    assert rows and not rows[0]["captured_at"].startswith("2020")
    ts = _dt.datetime.fromisoformat(rows[0]["captured_at"])
    assert (_dt.datetime.now(_dt.timezone.utc) - ts).total_seconds() < 3600


def test_oddspapi_dedupe_excludes_captured_at(tmp_path):
    # F7: re-appending the same rows (new captured_at) must dedupe to 0 added
    import scripts.capture_oddspapi as cap
    rows = rows_from_odds_response(_odds_payload(), market_type_map={
        "101": "1x2", "103": "btts", "108": "double_chance",
        "115": "team_totals", "107": "totals"})
    orig = cap.OUT_DIR
    cap.OUT_DIR = tmp_path
    try:
        a1 = cap._append_rows(rows, "2026-08-03")
        a2 = cap._append_rows(rows, "2026-08-03")  # same rows, new captured_at
    finally:
        cap.OUT_DIR = orig
    assert a1 > 0 and a2 == 0


def test_double_chance_draw_is_unpriced(tmp_path):
    # F5: a draw pick cannot be hedged with "12"; leave it unpriced
    from edgefactory.enh_pricing import load_prices_index
    rows = rows_from_odds_response(_odds_payload(), market_type_map={
        "101": "1x2", "103": "btts", "108": "double_chance",
        "115": "team_totals", "107": "totals"})
    _write_oddspapi_month(tmp_path, rows)
    idx = load_prices_index(tmp_path, "2026-08-03")
    p = attach_enhancement_price(
        _pick(recommended_enhancement="double_chance", enhancement_probability=0.5, pick="draw"), idx)
    assert p["enhancement_priced"] is False


def test_classify_label_set_winner_rejected():
    # F8: "Set Winner" (non-soccer vocabulary) must not classify as 1x2
    from edgefactory.sources.oddspapi_odds import _classify_label
    assert _classify_label("Set Winner") == ""


def test_real_payload_shape_totals_dropped():
    # Audit N2: the REAL OddsPapi payload carries no name/line on totals
    # outcomes (only mainLine). Totals/team-totals must be DROPPED (honest
    # safe-fail per 27.8), and 1x2/btts/dc must still flow.
    payload = {
        "fixtureId": "fx_real", "participant1Name": "Halmstads BK",
        "participant2Name": "IK Sirius", "startTime": "2026-08-03T17:00:00Z",
        "tournamentName": "Allsvenskan", "categoryName": "Sweden",
        "bookmakerOdds": {"Pinnacle": {"markets": {
            "101": {"outcomes": {"a": {"players": {"0": {"bookmakerOutcomeId": "home", "price": 2.10}}}}},
            "106": {"outcomes": {"b": {"players": {"0": {"mainLine": True, "price": 1.85}}}}},
            "103": {"outcomes": {"c": {"players": {"0": {"name": "Yes", "price": 1.95}}}}},
            "101902": {"outcomes": {"d": {"players": {"0": {"name": "HomeOrDraw", "price": 1.05}}}}},
        }}},
    }
    rows = rows_from_odds_response(payload, market_type_map={
        "101": "1x2", "106": "totals", "103": "btts", "101902": "double_chance"})
    markets = {(r["market"], r["selection"]) for r in rows}
    assert ("1x2", "home") in markets
    assert ("btts", "yes") in markets
    assert ("dc", "1x") in markets
    # totals outcome has mainLine but no name/line -> dropped, never guessed
    assert not any(m.startswith("ou_") for m, _ in markets)
