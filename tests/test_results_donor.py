from __future__ import annotations

import csv
import gzip
from pathlib import Path

from edgefactory import warehouse


def _write(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_predictz_settles_from_non_forebet_results_donor(monkeypatch, tmp_path):
    _write(
        tmp_path / "statarea_2026-09.csv.gz",
        [
            "date", "home", "away", "hs", "gs", "p1", "px", "p2",
            "ht_hs", "ht_gs", "p1_ht", "px_ht", "p2_ht",
            "p_o15", "p_o25", "p_o35", "tip", "league",
        ],
        [{
            "date": "2026-09-29", "home": "Alpha FC", "away": "Beta FC",
            "hs": "2", "gs": "1", "p1": "60", "px": "22", "p2": "18",
            "ht_hs": "1", "ht_gs": "0", "p1_ht": "50", "px_ht": "30",
            "p2_ht": "20", "p_o15": "70", "p_o25": "55", "p_o35": "30",
            "tip": "1", "league": "Test League",
        }],
    )
    _write(
        tmp_path / "predictz_2026-09.csv.gz",
        ["date", "league", "home", "away", "pick", "pred_score", "odd1", "oddx", "odd2"],
        [{
            "date": "2026-09-29", "league": "Test League",
            "home": "Alpha FC", "away": "Beta FC", "pick": "home",
            "pred_score": "2-1", "odd1": "1.8", "oddx": "3.4", "odd2": "4.5",
        }],
    )
    monkeypatch.setattr(warehouse, "LOCALDATA", tmp_path)

    con = warehouse.connect()
    try:
        donor = con.execute(
            "SELECT hs, gs, result_source FROM results_donor"
        ).fetchone()
        settled = con.execute(
            "SELECT hs, gs, outcome, result_source FROM predictz_settled"
        ).fetchone()
    finally:
        con.close()

    assert donor == (2, 1, "statarea")
    assert settled == (2, 1, "home", "statarea")
