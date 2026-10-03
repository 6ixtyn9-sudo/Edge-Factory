from __future__ import annotations

import json

from edgefactory import source_health


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
