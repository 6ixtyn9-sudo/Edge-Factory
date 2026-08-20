from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "edge_firing_tripwire.py"
SPEC = importlib.util.spec_from_file_location("edge_firing_tripwire", SCRIPT)
tripwire = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules["edge_firing_tripwire"] = tripwire
SPEC.loader.exec_module(tripwire)


def _edge(rule: str, market: str = "1x2") -> dict:
    return {
        "rule": rule,
        "market": market,
        "status": "certified",
        "decay": {"verdict": "WATCH"},
    }


def _write_gz(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "home", "away"])
        writer.writeheader()
        writer.writerows(rows)


def test_operational_scope_excludes_qualified_analysis_variants():
    edges = [
        _edge("ml-meta avg_p>=80"),
        _edge("2way-unanimous avg_p>=70"),
        _edge("3way-unanimous avg_p>=65"),
        _edge("2way-unanimous min_p>=60 avg_p>=70"),
        _edge("3way-unanimous home-only avg_p>=65"),
    ]

    monitored, ignored = tripwire._operational_edge_rules(edges)
    monitored_rules = {edge["rule"] for edge in monitored}

    assert monitored_rules == {
        "ml-meta avg_p>=80",
        "2way-unanimous avg_p>=70",
        "3way-unanimous avg_p>=65",
    }
    assert ignored == [
        "2way-unanimous min_p>=60 avg_p>=70",
        "3way-unanimous home-only avg_p>=65",
    ]


def test_future_forecast_rows_do_not_count_as_historical_firings(tmp_path):
    today = date(2026, 8, 20)
    future = (today + timedelta(days=1)).isoformat()
    current = today.isoformat()
    (tmp_path / "picks_2026-08-21.json").write_text(
        json.dumps([{"date": future, "rule": "2way-unanimous avg_p>=70"}])
    )
    (tmp_path / "picks_2026-08-20.json").write_text(
        json.dumps([{"date": current, "rule": "3way-unanimous avg_p>=65"}])
    )
    rules = [
        _edge("2way-unanimous avg_p>=70"),
        _edge("3way-unanimous avg_p>=65"),
    ]

    findings = tripwire._scan_edge_firing(tmp_path, rules, 14, today)
    by_rule = {item["rule"]: item for item in findings}

    assert by_rule["2way-unanimous avg_p>=70"]["silent"] is True
    assert by_rule["2way-unanimous avg_p>=70"]["last_fired"] is None
    assert by_rule["3way-unanimous avg_p>=65"]["silent"] is False
    assert by_rule["3way-unanimous avg_p>=65"]["last_fired"] == current


def test_exact_source_file_pattern_never_conflates_bzzoiro_and_odds(tmp_path):
    _write_gz(
        tmp_path / "bzzoiro_2026-08.csv.gz",
        [{"date": "2026-08-20", "home": "A", "away": "B"}],
    )
    _write_gz(
        tmp_path / "bzzoiro_odds_2026-08.csv.gz",
        [{"date": "2099-01-01", "home": "X", "away": "Y"}],
    )

    newest_date, newest_file = tripwire._newest_source_date(
        tmp_path, "bzzoiro", "date"
    )

    assert newest_date == "2026-08-20"
    assert newest_file == "bzzoiro_2026-08.csv.gz"


def test_ceiling_is_a_single_specific_classification(tmp_path, monkeypatch):
    today = date.today().isoformat()
    (tmp_path / "edges_consensus.json").write_text(
        json.dumps(
            {
                "edges": [
                    _edge("ml-meta avg_p>=80"),
                    _edge("2way-unanimous avg_p>=70"),
                    _edge("2way-unanimous min_p>=60 avg_p>=70"),
                ]
            }
        )
    )
    (tmp_path / "picks_today.json").write_text(
        json.dumps([{"date": today, "rule": "2way-unanimous avg_p>=70"}])
    )
    (tmp_path / "ml_meta_state.json").write_text(
        json.dumps({"date": today, "max_ml_p": 0.616, "thresholds": [80]})
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["edge_firing_tripwire.py", "--localdata", str(tmp_path)],
    )
    assert tripwire.main() == 0
    result = json.loads((tmp_path / "edge_firing_tripwire.json").read_text())

    assert result["warn_count"] == 1
    assert [item["rule"] for item in result["ceilings"]] == ["ml-meta avg_p>=80"]
    assert result["ignored_non_operational_rules"] == [
        "2way-unanimous min_p>=60 avg_p>=70"
    ]
