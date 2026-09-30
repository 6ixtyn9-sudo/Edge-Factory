"""Tests for the per-source settlement/matching audit.

The point of the audit is that it must be conservative: ambiguity is rejected,
a source never validates itself, orientation risk is flagged, and future rows
never enter the denominator.
"""
from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit_source_settlement_coverage.py"
SPEC = importlib.util.spec_from_file_location("audit_source_settlement_coverage", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)

FIELDS = ["date", "home", "away", "hs", "gs"]


def _write(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _overlay(localdata: Path, rows: list[dict]) -> None:
    (localdata / "settled_results.json").write_text(json.dumps({"schema": 1, "rows": rows}))


def _audit(localdata: Path, source: str, *, end="2026-09-30", days=30):
    donors = audit.build_donor_index(
        localdata, (date.fromisoformat(end) - __import__("datetime").timedelta(days=days)).isoformat(),
        end, use_warehouse=False,
    )
    start = (date.fromisoformat(end) - __import__("datetime").timedelta(days=days)).isoformat()
    return audit.audit_source(source, localdata=localdata, donors=donors, start=start, end=end)


def test_exact_match_and_source_score_agreement(tmp_path):
    _write(tmp_path / "betclan_2026-09.csv.gz", [
        {"date": "2026-09-10", "home": "Arsenal", "away": "Chelsea", "hs": "2", "gs": "1"},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-10", "home": "Arsenal", "away": "Chelsea", "hs": 2, "gs": 1,
         "src": "forebet_settled"},
    ])
    row = _audit(tmp_path, "betclan")
    assert row.prediction_fixtures == 1
    assert row.source_score_present == 1
    assert row.independent_donor_exact_matches == 1
    assert row.matched_total == 1
    assert row.source_score_matches_donor == 1
    assert row.source_score_conflicts_donor == 0
    assert row.unmatched == 0
    assert row.coverage_pct == 100.0
    assert row.conflict_pct == 0.0


def test_source_score_conflicts_with_donor(tmp_path):
    _write(tmp_path / "betclan_2026-09.csv.gz", [
        {"date": "2026-09-10", "home": "Arsenal", "away": "Chelsea", "hs": "0", "gs": "0"},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-10", "home": "Arsenal", "away": "Chelsea", "hs": 2, "gs": 1,
         "src": "forebet_settled"},
    ])
    row = _audit(tmp_path, "betclan")
    assert row.source_score_conflicts_donor == 1
    assert row.source_score_matches_donor == 0
    assert row.conflict_pct == 100.0
    assert row.examples["conflict"][0]["donor_score"] == "2-1"


def test_unmatched_when_no_independent_donor(tmp_path):
    _write(tmp_path / "windrawwin_2026-09.csv.gz", [
        {"date": "2026-09-11", "home": "Somewhere FC", "away": "Nowhere FC", "hs": "", "gs": ""},
    ])
    _overlay(tmp_path, [])
    row = _audit(tmp_path, "windrawwin")
    assert row.unmatched == 1
    assert row.matched_total == 0
    assert row.coverage_pct == 0.0
    assert row.verdict == "unproven"
    assert row.examples["unmatched"][0]["home"] == "Somewhere FC"


def test_ambiguous_duplicate_donor_candidates_are_rejected(tmp_path):
    # Two distinct donor fixtures fold onto one alias key; exact key misses.
    _write(tmp_path / "bzzoiro_2026-09.csv.gz", [
        {"date": "2026-09-12", "home": "FC Porto", "away": "Benfica", "hs": "", "gs": ""},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-12", "home": "Porto", "away": "Benfica", "hs": 1, "gs": 0,
         "src": "forebet_settled"},
        {"date": "2026-09-12", "home": "Porto FC", "away": "Benfica", "hs": 2, "gs": 0,
         "src": "statarea_settled"},
    ])
    row = _audit(tmp_path, "bzzoiro")
    assert row.ambiguous == 1
    assert row.matched_total == 0
    assert row.unmatched == 0
    assert row.examples["ambiguous"][0]["reason"] == "multiple alias donor candidates"


def test_reversed_home_away_candidate_flagged(tmp_path):
    _write(tmp_path / "soccervista_2026-09.csv.gz", [
        {"date": "2026-09-13", "home": "Marsaxlokk", "away": "Hamrun Spartans", "hs": "", "gs": ""},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-13", "home": "Hamrun Spartans", "away": "Marsaxlokk", "hs": 1, "gs": 1,
         "src": "forebet_settled"},
    ])
    row = _audit(tmp_path, "soccervista")
    assert row.reversed_candidates == 1
    assert row.unmatched == 1
    assert row.matched_total == 0
    assert row.examples["reversed_candidate"][0]["donor_score"] == "1-1"


def test_conflicting_donor_scores_are_not_settlement_evidence(tmp_path):
    _write(tmp_path / "betclan_2026-09.csv.gz", [
        {"date": "2026-09-14", "home": "Alpha", "away": "Beta", "hs": "1", "gs": "1"},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-14", "home": "Alpha", "away": "Beta", "hs": 1, "gs": 1,
         "src": "forebet_settled"},
        {"date": "2026-09-14", "home": "Alpha", "away": "Beta", "hs": 3, "gs": 0,
         "src": "statarea_settled"},
    ])
    row = _audit(tmp_path, "betclan")
    assert row.donor_score_conflicts == 1
    assert row.matched_total == 0
    assert row.source_score_matches_donor == 0
    assert row.coverage_pct == 0.0


def test_source_is_never_its_own_independent_donor(tmp_path):
    _write(tmp_path / "vitibet_2026-09.csv.gz", [
        {"date": "2026-09-15", "home": "Alpha", "away": "Beta", "hs": "2", "gs": "0"},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-15", "home": "Alpha", "away": "Beta", "hs": 2, "gs": 0,
         "src": "vitibet_settled"},
    ])
    row = _audit(tmp_path, "vitibet")
    assert row.matched_total == 0
    assert row.unmatched == 1


def test_future_dates_excluded(tmp_path):
    _write(tmp_path / "betclan_2026-10.csv.gz", [
        {"date": "2026-10-05", "home": "Future", "away": "Fixture", "hs": "", "gs": ""},
    ])
    _write(tmp_path / "betclan_2026-09.csv.gz", [
        {"date": "2026-09-20", "home": "Alpha", "away": "Beta", "hs": "1", "gs": "0"},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-20", "home": "Alpha", "away": "Beta", "hs": 1, "gs": 0,
         "src": "forebet_settled"},
    ])
    row = _audit(tmp_path, "betclan")
    assert row.prediction_fixtures == 1
    assert row.coverage_pct == 100.0


def test_pricing_only_source_excluded(tmp_path):
    _write(tmp_path / "bzzoiro_odds_2026-09.csv.gz", [
        {"date": "2026-09-20", "home": "Alpha", "away": "Beta", "hs": "", "gs": ""},
    ])
    row = _audit(tmp_path, "bzzoiro_odds")
    assert row.role == "pricing-only"
    assert row.verdict == "excluded_pricing_only"
    assert row.prediction_fixtures == 0


def test_exact_source_file_matching_does_not_bleed(tmp_path):
    _write(tmp_path / "bzzoiro_odds_2026-09.csv.gz", [
        {"date": "2026-09-21", "home": "X", "away": "Y", "hs": "", "gs": ""},
    ])
    _write(tmp_path / "bzzoiro_2026-09.csv.gz", [
        {"date": "2026-09-21", "home": "Alpha", "away": "Beta", "hs": "", "gs": ""},
    ])
    row = _audit(tmp_path, "bzzoiro")
    assert row.prediction_fixtures == 1


def test_no_data_verdict_and_report_render(tmp_path):
    _overlay(tmp_path, [])
    report = audit.run_audit(
        localdata=tmp_path,
        end_date=date(2026, 9, 30),
        days=30,
        sources=("freesupertips", "bzzoiro_odds"),
        use_warehouse=False,
    )
    rows = report["_rows"]
    assert rows[0].verdict == "no_data"
    markdown = audit.render_markdown(
        rows, start=report["window_start"], end=report["window_end"], donors=report["_donors"],
    )
    assert "Source settlement coverage" in markdown
    assert "freesupertips" in markdown
    assert report["summary"]["no_data"] == ["freesupertips"]


def test_cli_writes_json_and_markdown(tmp_path):
    _write(tmp_path / "betclan_2026-09.csv.gz", [
        {"date": "2026-09-22", "home": "Alpha", "away": "Beta", "hs": "1", "gs": "0"},
    ])
    _overlay(tmp_path, [
        {"date": "2026-09-22", "home": "Alpha", "away": "Beta", "hs": 1, "gs": 0,
         "src": "forebet_settled"},
    ])
    out_json = tmp_path / "out" / "cov.json"
    out_md = tmp_path / "out" / "cov.md"
    rc = audit.main([
        "--end-date", "2026-09-30", "--days", "30", "--sources", "betclan",
        "--localdata", str(tmp_path), "--no-warehouse",
        "--output-json", str(out_json), "--output-md", str(out_md),
    ])
    assert rc == 0
    payload = json.loads(out_json.read_text())
    assert payload["sources"][0]["coverage_pct"] == 100.0
    assert "betclan" in out_md.read_text()


def test_verdict_thresholds_require_volume_and_low_conflict():
    strong = audit.SourceCoverage(
        source="x", prediction_fixtures=500, matched_total=480, coverage_pct=96.0,
        source_score_matches_donor=470, source_score_conflicts_donor=5, conflict_pct=1.05,
    )
    assert audit.classify(strong)[0] == "settlement_validated"
    thin = audit.SourceCoverage(
        source="y", prediction_fixtures=50, matched_total=40, coverage_pct=80.0, conflict_pct=1.0,
    )
    assert audit.classify(thin)[0] == "partial"
    weak = audit.SourceCoverage(
        source="z", prediction_fixtures=500, matched_total=100, coverage_pct=20.0, conflict_pct=0.0,
    )
    assert audit.classify(weak)[0] == "unproven"
