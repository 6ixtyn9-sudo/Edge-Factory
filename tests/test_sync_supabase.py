"""Regression tests for the authoritative Supabase pick sync."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "sync_supabase.py"
SPEC = importlib.util.spec_from_file_location("sync_supabase", SCRIPT)
sync_supabase = importlib.util.module_from_spec(SPEC)
sys.modules["sync_supabase"] = sync_supabase
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(sync_supabase)


def test_event_source_ref_is_accent_safe():
    accented = {
        "date": "2026-08-13",
        "home": "FC Nordsjælland",
        "away": "Valur Reykjavik",
    }
    ascii_alias = {**accented, "home": "FC Nordsjaelland"}

    assert sync_supabase.event_source_ref(accented) == sync_supabase.event_source_ref(
        ascii_alias
    )


def test_build_pick_rows_dedupes_the_database_conflict_key(tmp_path):
    pick = {
        "date": "2026-08-13",
        "home": "FC Nordsjælland",
        "away": "Valur Reykjavik",
        "match": "FC Nordsjælland vs Valur Reykjavik",
        "market": "1x2",
        "pick": "home",
        "edge_rule": "2way-unanimous avg_p>=70",
        "avg_p": 71,
        "odds": 1.12,
        "bucket": "SKIPPED_VETO",
    }
    edge_name = pick["edge_rule"]
    event_ref = sync_supabase.event_source_ref(pick)

    rows, skipped = sync_supabase.build_pick_rows(
        [pick, dict(pick)],
        {edge_name: "edge-1"},
        {event_ref: "event-1"},
        {edge_name: edge_name},
        target_date="2026-08-13",
        picks_path=tmp_path / "picks.json",
    )

    assert len(rows) == 1
    assert len(skipped) == 1
    assert skipped[0]["reason"] == "duplicate_conflict_key"
    assert (
        rows[0]["edge_id"],
        rows[0]["event_id"],
        rows[0]["market"],
        rows[0]["selection"],
    ) == ("edge-1", "event-1", "1x2", "home")
