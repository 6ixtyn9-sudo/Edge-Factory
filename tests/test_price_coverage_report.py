"""Focused tests for archive price-coverage competition labels."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "price_coverage_report", ROOT / "scripts" / "price_coverage_report.py")
report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(report)


def _write_archive(localdata: Path, rows: list[dict]) -> None:
    localdata.mkdir(parents=True, exist_ok=True)
    (localdata / "picks_2026-10-04.json").write_text(json.dumps(rows))


def test_competition_label_collapses_known_fragments_for_reporting_only(tmp_path):
    _write_archive(tmp_path, [
        {"home": "A", "away": "B", "league": "Fr1", "match": "A vs B"},
        {"home": "C", "away": "D", "league": "France,Ligue 1", "match": "C vs D"},
        {"home": "E", "away": "F", "league": "UCL", "match": "E vs F"},
        {"home": "G", "away": "H", "league": "World UEFA Champions League", "match": "G vs H"},
        {"home": "I", "away": "J", "league": "UNL", "match": "I vs J"},
        {"home": "K", "away": "L", "league": "World UEFA Nations League", "match": "K vs L"},
    ])

    rows = {row["competition"]: row for row in report.coverage_table(tmp_path)}
    assert rows["France,Ligue 1"]["picks"] == 2
    assert rows["World UEFA Champions League"]["picks"] == 2
    assert rows["World UEFA Nations League"]["picks"] == 2


def test_womens_fixture_does_not_pollute_mens_laliga_bucket(tmp_path):
    _write_archive(tmp_path, [
        {"home": "Barcelona (w)", "away": "Real Madrid (w)", "league": "Spain La Liga",
         "match": "Barcelona (w) vs Real Madrid (w)"},
        {"home": "Barcelona", "away": "Real Madrid", "league": "Spain La Liga",
         "match": "Barcelona vs Real Madrid"},
        {"home": "West Ham (w)", "away": "Chelsea (w)", "league": "England,Wsl",
         "match": "West Ham (w) vs Chelsea (w)"},
    ])

    rows = {row["competition"]: row for row in report.coverage_table(tmp_path)}
    assert rows["Spain Liga F"]["picks"] == 1
    assert rows["Spain La Liga"]["picks"] == 1
    assert rows["England WSL"]["picks"] == 1


def test_europa_league_does_not_collapse_into_conference_league():
    assert (report.canonical_competition_label("World UEFA Europa Conference League")
            == "World UEFA Europa Conference League")
    assert (report.canonical_competition_label("World UEFA Europa League")
            == "World UEFA Europa League")
