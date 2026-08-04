"""Offline coverage tests for the read-only OddsPapi market probe."""
from __future__ import annotations

import importlib.util
import json
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "probe_oddspapi_markets.py"
spec = importlib.util.spec_from_file_location("probe_oddspapi_markets", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def test_exact_pair_match_strips_club_noise_and_accepts_swap():
    target = {"home": "AS Roma", "away": "GNK Dinamo Zagreb"}
    direct = {"participant1Name": "Roma", "participant2Name": "Dinamo Zagreb"}
    swapped = {"participant1Name": "Dinamo Zagreb", "participant2Name": "AS Roma"}
    wrong = {"participant1Name": "Roma", "participant2Name": "Dinamo Minsk"}
    assert probe.match_fixture(target, direct) == "exact_pair"
    assert probe.match_fixture(target, swapped) == "exact_pair_swapped"
    assert probe.match_fixture(target, wrong) is None


def test_target_loader_dedupes_fixture_pairs_and_honours_window(tmp_path):
    source = tmp_path / "picks.json"
    source.write_text(json.dumps([
        {"date": "2026-08-05", "home": "AS Roma", "away": "GNK Dinamo Zagreb", "match": "Roma vs Dinamo"},
        {"date": "2026-08-05", "home": "AS Roma", "away": "GNK Dinamo Zagreb", "match": "duplicate"},
        {"date": "2026-08-06", "home": "Alpha", "away": "Beta"},
        {"date": "2026-08-08", "home": "outside", "away": "window"},
    ]))
    targets = probe.load_targets(source, "2026-08-05", 2, 10)
    assert len(targets) == 2
    assert targets[0]["match"] == "Roma vs Dinamo"


def test_market_summary_preserves_ids_labels_categories_and_target_book_flag():
    payload = {
        "fixtureId": "f-1",
        "participant1Name": "Roma",
        "participant2Name": "Dinamo Zagreb",
        "bookmakerOdds": {
            "book_a": {
                "fixturePath": "https://example.invalid/f-1",
                "markets": {
                    "101": {"outcomes": {"a": {}, "b": {}, "c": {}}},
                    "700": {"outcomes": {"d": {}, "e": {}}},
                    "800": {"outcomes": {"f": {}, "g": {}}},
                },
            }
        },
    }
    summary = probe.summarize_odds(
        payload,
        {"101": "1X2", "700": "Away Team Total Goals", "800": "Both Teams To Score"},
        {"book_a"},
    )
    book = summary["bookmakers"][0]
    assert book["target_book"] is True
    assert book["market_count"] == 3 and book["outcome_count"] == 7
    assert {"team_totals", "btts"}.issubset(book["categories"])
    assert book["market_ids"] == ["101", "700", "800"]


def test_market_catalog_parser_degrades_for_unknown_shapes():
    assert probe._market_catalog_map({"data": [{"marketId": 101, "marketName": "1X2"}]}) == {"101": "1X2"}
    assert probe._market_catalog_map({"unexpected": "shape"}) == {}


def test_key_ring_prefers_plural_strips_spaces_and_dedupes(monkeypatch):
    monkeypatch.setenv("ODDSPAPI_API_KEYS", " k1, k2,k1 ,, k3 ")
    monkeypatch.setenv("ODDSPAPI_API_KEY", "legacy")
    assert probe.oddspapi_odds.api_keys() == ("k1", "k2", "k3")
    monkeypatch.delenv("ODDSPAPI_API_KEYS")
    assert probe.oddspapi_odds.api_keys() == ("legacy",)


def test_key_ring_fails_over_on_http_quota_without_exposing_key(monkeypatch):
    monkeypatch.setenv("ODDSPAPI_API_KEYS", "first,second")
    calls = []

    def fake_get(url, retries=3):
        calls.append(url)
        if "apiKey=first" in url:
            raise urllib.error.HTTPError(url, 429, "quota", {}, None)
        return {"ok": True}

    monkeypatch.setattr(probe.oddspapi_odds, "_get_json", fake_get)
    assert probe.oddspapi_odds.fetch_json("/fixtures", {"sportId": 10}) == {"ok": True}
    assert len(calls) == 2
    assert "apiKey=second" in calls[-1]
