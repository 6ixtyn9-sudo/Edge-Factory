from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import duckdb

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "mine_consensus.py"
SPEC = importlib.util.spec_from_file_location("mine_consensus_weighted_test", SCRIPT)
miner = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(miner)


def test_weighted_consensus_accepts_probability_source_without_odds(monkeypatch):
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE zulubet_settled (
            date VARCHAR, hkey VARCHAR, akey VARCHAR, home VARCHAR, away VARCHAR,
            outcome VARCHAR, league VARCHAR, pick VARCHAR, pmax DOUBLE,
            odd1 DOUBLE, oddx DOUBLE, odd2 DOUBLE
        );
        CREATE TABLE statarea_settled (
            date VARCHAR, hkey VARCHAR, akey VARCHAR, home VARCHAR, away VARCHAR,
            outcome VARCHAR, league VARCHAR, pick VARCHAR, pmax DOUBLE
        );
    """)
    rows = [
        ("2024-01-01", "alphateam", "betateam", "Alpha", "Beta", "home", "L", "home", 0.70),
        ("2026-01-01", "gammateam", "deltateam", "Gamma", "Delta", "away", "L", "away", 0.72),
    ]
    con.executemany(
        "INSERT INTO statarea_settled VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    con.executemany(
        "INSERT INTO zulubet_settled VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [row + (1.50, 3.50, 5.00) for row in rows],
    )

    monkeypatch.setattr(miner, "GATES", SimpleNamespace(
        min_overlap_n=1,
        min_n_train=1,
        min_n_valid=1,
        min_roi_train=-1.0,
        min_roi_valid=-1.0,
    ))
    results: list[dict] = []
    miner._run_weighted_consensus(
        con,
        "2025-06-01",
        {"zulubet": {"1x2": 0.70}, "statarea": {"1x2": 0.70}},
        results,
        {"zulubet_settled": 1.0, "statarea_settled": 1.0},
    )

    assert results
    assert all(result["view"] == "weighted_1x2" for result in results)
    assert all(result["sources"] == ["zulubet", "statarea"] for result in results)
    assert all(result["train"]["n"] == 1 for result in results)
    assert all(result["valid"]["n"] == 1 for result in results)
    con.close()
