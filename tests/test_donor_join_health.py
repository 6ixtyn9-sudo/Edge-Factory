from __future__ import annotations

import json

from edgefactory import source_health
import scripts.picks_today as pt


def test_health_contract_exposes_captured_scored_and_matched_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(source_health, "LOCALDATA", tmp_path)
    payload = source_health.persist_daily_source_health(
        "2026-10-03",
        {
            "betbetter": {
                "status": "cache_only", "fetched": True,
                "rows": 1324, "bb_raw": 1324, "bb_scored": 1324,
                "bb_matched": 0, "can_fetch_today": True, "can_price": True,
            },
            "boggio": {
                "status": "cache_only", "fetched": True,
                "rows": 20, "bg_raw": 20, "bg_scored": 20,
                "bg_matched": 0, "can_fetch_today": True, "can_price": True,
            },
        },
    )
    assert payload["sources"]["betbetter"]["bb_matched"] == 0
    assert payload["sources"]["boggio"]["bg_matched"] == 0
    line = source_health.daily_status_block("2026-10-03")
    assert "bb_raw1324/bb_scored1324" in line and "/bb_matched0" in line
    assert "bg_raw20/bg_scored20" in line and "/bg_matched0" in line
    # cache_only with usable rows remains available to the role contract.
    assert payload["sources"]["betbetter"]["can_fetch_today"] is True


def test_theodds_health_receipt_keeps_capture_validation_and_join_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(source_health, "LOCALDATA", tmp_path)
    payload = source_health.persist_daily_source_health(
        "2026-10-03",
        {
            "theoddsapi": {
                "status": "cache_only", "fetched": False, "rows": 404,
                "oa_raw": 404, "oa_usable": 404, "oa_matched": 6,
                "can_fetch_today": False, "can_price": True, "can_vote": False,
            },
        },
    )
    receipt = payload["sources"]["theoddsapi"]
    assert (receipt["oa_raw"], receipt["oa_usable"], receipt["oa_matched"]) == (404, 404, 6)
    assert "theoddsapi=raw404/usable404/matched6" in source_health.daily_status_block("2026-10-03")
    assert "theoddsapi: healthy named-book price source" in source_health.source_role_lines("2026-10-03")


def test_oddspapi_health_receipt_keeps_capture_validation_and_join_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(source_health, "LOCALDATA", tmp_path)
    payload = source_health.persist_daily_source_health(
        "2026-10-03",
        {
            "oddspapi_odds": {
                "status": "cache_only", "fetched": False, "rows": 8,
                "op_raw": 12, "op_usable": 8, "op_matched": 2,
                "can_fetch_today": False, "can_price": True, "can_vote": False,
            },
        },
    )
    receipt = payload["sources"]["oddspapi_odds"]
    assert (receipt["op_raw"], receipt["op_usable"], receipt["op_matched"]) == (12, 8, 2)
    assert "oddspapi=raw12/usable8/matched2" in source_health.daily_status_block("2026-10-03")
    assert "oddspapi_odds: healthy named-book price source" in source_health.source_role_lines("2026-10-03")


def test_betexplorer_health_receipt_keeps_snapshot_and_join_counts(tmp_path, monkeypatch):
    monkeypatch.setattr(source_health, "LOCALDATA", tmp_path)
    payload = source_health.persist_daily_source_health(
        "2026-10-03",
        {
            "betexplorer": {
                "status": "cache_only", "fetched": False, "rows": 9,
                "be_raw": 12, "be_usable": 9, "be_matched": 3,
                "can_fetch_today": False, "can_price": True, "can_vote": False,
            },
        },
    )
    receipt = payload["sources"]["betexplorer"]
    assert (receipt["be_raw"], receipt["be_usable"], receipt["be_matched"]) == (12, 9, 3)
    assert "betexplorer=raw12/usable9/matched3" in source_health.daily_status_block("2026-10-03")
    assert "betexplorer: healthy named-book price source" in source_health.source_role_lines("2026-10-03")


def test_raw_donor_rows_are_bucketed_by_exact_join_failure():
    day = "2026-10-03"
    pick = {
        "date": day, "home": "Home FC", "away": "Away FC",
        "market": "1x2", "pick": "home", "kickoff": f"{day}T16:00:00Z",
    }
    base = {
        "date": day, "home": "Home FC", "away": "Away FC",
        "market": "classic", "selection": "1", "odds": 1.80,
        "kickoff": f"{day}T16:00:00Z",
    }
    # Every row is provider vocabulary, not a pre-canonicalised fixture.
    rows = [
        dict(base),
        dict(base, date="2026-10-04"),
        dict(base, market="provider mystery"),
        dict(base, selection="mystery side"),
        dict(base, home="Other FC", away="Another FC"),
        dict(base, selection="2"),
        dict(base, timestamp_suspect=True),
    ]
    bundle = pt._odds_bundle_from_rows(rows, provider="boggio")
    report = pt.donor_join_diagnostics([pick], [bundle])["boggio"]
    assert report["matched_rows"] == 1
    assert report["miss_counts"] == {
        "date_mismatch": 1,
        "fixture_key_miss": 1,
        "market_unmapped": 1,
        "no_pick_for_fixture": 1,
        "selection_unmapped": 1,
        "timestamp_rejected": 1,
    }
    line = pt.donor_join_miss_lines({"boggio": report}, limit=6)[0]
    assert "donor join misses boggio:" in line
    assert "fixture_key_miss=1" in line


def test_join_miss_counts_persist_as_count_only_health_data(tmp_path, monkeypatch):
    monkeypatch.setattr(source_health, "LOCALDATA", tmp_path)
    payload = source_health.persist_daily_source_health(
        "2026-10-03",
        {"boggio": {
            "status": "cache_only", "bg_raw": 20, "bg_scored": 20,
            "bg_matched": 1, "can_fetch_today": True, "can_price": True,
            "join_miss_counts": {"fixture_key_miss": 18, "market_unmapped": 1},
            "join_matched_rows": 1,
        }},
    )
    receipt = payload["sources"]["boggio"]
    assert receipt["join_miss_counts"] == {
        "fixture_key_miss": 18, "market_unmapped": 1,
    }
    assert receipt["join_matched_rows"] == 1
