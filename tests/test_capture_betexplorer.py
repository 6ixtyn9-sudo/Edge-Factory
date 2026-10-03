from __future__ import annotations

import json

import scripts.capture_betexplorer as capture


def test_candidate_reader_is_1x2_only_deduplicated_and_score_ordered(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    rows = [
        {"date": "2026-10-03", "home": "Bravo", "away": "Zulu", "market": "1x2", "avg_p": 60},
        {"date": "2026-10-03", "home": "Alpha", "away": "Beta", "market": "1x2", "avg_p": 80},
        {"date": "2026-10-03", "home": "Alpha", "away": "Beta", "market": "1x2", "avg_p": 70},
        {"date": "2026-10-03", "home": "Skip", "away": "Me", "market": "btts", "avg_p": 99},
        {"date": "2026-10-04", "home": "Tomorrow", "away": "No", "market": "1x2", "avg_p": 99},
    ]
    (tmp_path / "picks_2026-10-03.json").write_text(json.dumps(rows))
    candidates = capture._candidate_rows("2026-10-03")
    assert [(row["home"], row["away"]) for row in candidates] == [
        ("Alpha", "Beta"), ("Bravo", "Zulu"),
    ]
