from __future__ import annotations

import csv
import gzip
import importlib.util
import json
from pathlib import Path

from edgefactory.remine import (
    fetch_gap_only,
    merge_existing_wins,
    overlap_report,
    source_row_key,
)


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "coverage_inventory.py"
_spec = importlib.util.spec_from_file_location("coverage_inventory", SCRIPT)
assert _spec and _spec.loader
coverage_inventory = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(coverage_inventory)


def _row(day: str, home: str = "Alpha FC", away: str = "Beta FC", pick: str = "home", outcome: str = "home") -> dict:
    return {"date": day, "home": home, "away": away, "market": "1x2", "pick": pick, "outcome": outcome}


def test_gap_fetch_never_calls_callback_for_held_days() -> None:
    inventory = {
        "sources": {
            "demo": {
                "per_day_row_counts": {"2026-01-01": 1},
                "date_range": {"missing_internal_days": ["2026-01-02"]},
            }
        }
    }
    called: list[str] = []

    result = fetch_gap_only(
        inventory,
        "demo",
        ["2026-01-01", "2026-01-02"],
        lambda day: called.append(day) or [{"date": day}],
    )

    assert called == ["2026-01-02"]
    assert list(result) == ["2026-01-02"]


def test_gap_fetch_fails_closed_when_inventory_marks_held_day_as_gap() -> None:
    inventory = {
        "sources": {
            "demo": {
                "per_day_row_counts": {"2026-01-01": 1},
                "date_range": {"missing_internal_days": ["2026-01-01"]},
            }
        }
    }
    try:
        fetch_gap_only(inventory, "demo", None, lambda day: [])
    except ValueError as exc:
        assert "held dates marked as gaps" in str(exc)
    else:  # pragma: no cover - assertion makes the safety fence explicit
        raise AssertionError("held day was accepted as a crawl gap")


def test_merge_collision_keeps_committed_existing_row() -> None:
    existing = [_row("2026-01-01", pick="home", outcome="away")]
    incoming = [
        _row("2026-01-01", pick="away", outcome="away"),
        _row("2026-01-02", pick="away", outcome="away"),
        _row("2026-01-02", pick="home", outcome="home"),
    ]

    merged, audit = merge_existing_wins("demo", existing, incoming)

    assert merged[0]["pick"] == "home"
    assert [row["date"] for row in merged] == ["2026-01-01", "2026-01-02"]
    assert audit["incoming_collision_rows_skipped"] == 1
    assert audit["incoming_duplicate_rows_skipped"] == 1
    assert audit["collision_keys"][0]["action"] == "existing_wins"
    assert source_row_key("demo", merged[0]) == source_row_key("demo", existing[0])


def test_overlap_report_emits_joint_table_phi_and_convergence_gate() -> None:
    new_rows = []
    donor_rows = []
    outcomes = ["home", "away", "home", "away"] * 8  # 32 shared settled fixtures
    for index, outcome in enumerate(outcomes):
        day = f"2026-01-{index + 1:02d}"
        # Same signal on every fixture: eligible and convergent. Explicit hit
        # flags make all four joint-hit cells populated so phi is defined.
        pick = "home" if index % 2 == 0 else "away"
        new_rows.append({**_row(day, pick=pick, outcome=outcome), "hit": index % 4 in (0, 1)})
        donor_rows.append({**_row(day, pick=pick, outcome=outcome), "hit": index % 4 in (0, 2)})

    report = overlap_report("new", new_rows, "statarea", donor_rows, min_shared=30)

    assert report["eligible"] is True
    assert report["shared_settled_fixtures"] == 32
    assert sum(report["joint_hit_table"].values()) == 32
    assert report["phi"] == 0.0
    assert report["same_pick_rate"] == 1.0
    assert report["convergent"] is True
    assert report["voice_credit"] == 0


def test_inventory_fixture_is_reproducible_and_lists_internal_gap(tmp_path: Path) -> None:
    root = tmp_path
    localdata = root / "localdata"
    localdata.mkdir()
    path = localdata / "demo.csv.gz"
    rows = [
        {"date": "2026-01-01", "home": "Alpha & Co", "away": "Beta FC", "market": "1x2", "p1": "55"},
        {"date": "2026-01-01", "home": "Alpha and Co", "away": "Beta FC", "market": "1x2", "p1": "55"},
        {"date": "2026-01-03", "home": "Alpha and Co", "away": "Beta FC", "market": "1x2", "p1": "55"},
    ]
    with gzip.open(path, "wt", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    old_root, old_localdata = coverage_inventory.ROOT, coverage_inventory.LOCALDATA
    try:
        coverage_inventory.ROOT = root
        coverage_inventory.LOCALDATA = localdata
        spec = {
            "patterns": ["demo.csv.gz"],
            "date_fields": ["date"],
            "warehouse_tables": ["demo"],
            "market_groups": {"1x2_probability": ("p1",)},
        }
        first = coverage_inventory.inventory_one("demo", spec, {"localdata/demo.csv.gz"})
        second = coverage_inventory.inventory_one("demo", spec, {"localdata/demo.csv.gz"})
    finally:
        coverage_inventory.ROOT, coverage_inventory.LOCALDATA = old_root, old_localdata

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["date_range"]["missing_internal_days"] == ["2026-01-02"]
    assert first["duplicate_keys"]["duplicate_row_count"] == 1
    assert first["status"] == "committed"
