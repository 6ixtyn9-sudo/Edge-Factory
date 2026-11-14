from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit_source_availability.py"
SPEC = importlib.util.spec_from_file_location("audit_source_availability", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "home", "away"])
        writer.writeheader()
        writer.writerows(rows)


def test_scan_counts_target_and_rolling_rows(tmp_path):
    _write_rows(
        tmp_path / "vitibet_2026-09.csv.gz",
        [
            {"date": "2026-08-31", "home": "Old", "away": "Old"},
            {"date": "2026-09-01", "home": "A", "away": "B"},
            {"date": "2026-09-30", "home": "C", "away": "D"},
            {"date": "2026-09-30", "home": "E", "away": "F"},
        ],
    )
    (tmp_path / "state_vitibet.json").write_text(json.dumps({
        "done": ["2026-09-30"],
        "failures": {"2026-09-15": "HTTP 503", "2026-08-01": "old"},
    }))

    row = audit.scan_source(
        "vitibet",
        localdata=tmp_path,
        target=date(2026, 9, 30),
        days=30,
        capture_jobs={"vitibet"},
        warehouse_tables={"vitibet"},
    )

    assert row.file_count == 1
    assert row.latest_date == "2026-09-30"
    assert row.target_rows == 2
    assert row.rolling_rows == 4
    assert row.target_done is True
    assert row.recent_failures == (("2026-09-15", "HTTP 503"),)
    assert row.in_capture_jobs is True
    assert row.warehouse is True


def test_missing_source_files_are_reported_without_crashing(tmp_path):
    row = audit.scan_source(
        "soccervista",
        localdata=tmp_path,
        target=date(2026, 9, 30),
        days=30,
        capture_jobs={"soccervista"},
        warehouse_tables=set(),
    )

    assert row.file_count == 0
    assert row.latest_date is None
    assert row.target_rows == 0
    assert row.rolling_rows == 0
    assert "no local files" in audit._notes(row)
    assert "pending" in audit._notes(row)


def test_exact_source_pattern_does_not_mix_bzzoiro_odds(tmp_path):
    _write_rows(
        tmp_path / "bzzoiro_odds_2026-09.csv.gz",
        [{"date": "2026-09-30", "home": "A", "away": "B"}],
    )
    _write_rows(
        tmp_path / "bzzoiro_2026-09.csv.gz",
        [{"date": "2026-09-29", "home": "C", "away": "D"}],
    )

    prediction = audit.scan_source(
        "bzzoiro",
        localdata=tmp_path,
        target=date(2026, 9, 30),
        days=30,
        capture_jobs={"bzzoiro"},
    )
    odds = audit.scan_source(
        "bzzoiro_odds",
        localdata=tmp_path,
        target=date(2026, 9, 30),
        days=30,
        capture_jobs={"bzzoiro_odds"},
    )

    assert prediction.target_rows == 0
    assert prediction.rolling_rows == 1
    assert odds.target_rows == 1


def test_capture_job_detection_reads_registry(tmp_path):
    script = tmp_path / "capture_daily.py"
    script.write_text("JOBS = [('alpha', '2026-01-01', '2026-01-02'), ('beta', 'x', 'y')]\n")

    assert audit.capture_job_sources(script) == {"alpha", "beta"}
