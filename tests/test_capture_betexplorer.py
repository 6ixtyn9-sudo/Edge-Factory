from __future__ import annotations

import json

import scripts.capture_betexplorer as capture


def test_candidate_reader_prefers_fresh_picks_today_and_confidence_order(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    # Stale archive has a higher-confidence fixture, but the fresh candidate
    # slate must win when it is same-day.
    (tmp_path / "picks_2026-10-03.json").write_text(json.dumps([
        {"date": "2026-10-03", "home": "Archive", "away": "Only", "market": "1x2", "avg_p": 99},
    ]))
    rows = [
        {"date": "2026-10-03", "home": "Bravo", "away": "Zulu", "market": "1x2", "avg_p": 60},
        {"date": "2026-10-03", "home": "Alpha", "away": "Beta", "market": "1x2", "avg_p": 80, "w_score": 0.1},
        {"date": "2026-10-03", "home": "Alpha", "away": "Beta", "market": "1x2", "avg_p": 70},
        {"date": "2026-10-03", "home": "Skip", "away": "Me", "market": "btts", "avg_p": 99},
        {"date": "2026-10-04", "home": "Tomorrow", "away": "No", "market": "1x2", "avg_p": 99},
    ]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    candidates = capture._candidate_rows("2026-10-03")
    assert [(row["home"], row["away"]) for row in candidates] == [
        ("Alpha", "Beta"), ("Bravo", "Zulu"),
    ]


def test_candidate_reader_falls_back_to_same_day_archive(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    (tmp_path / "picks_today.json").write_text(json.dumps([
        {"date": "2026-10-04", "home": "Stale", "away": "Slate", "market": "1x2", "avg_p": 99},
    ]))
    (tmp_path / "picks_2026-10-03.json").write_text(json.dumps([
        {"date": "2026-10-03", "home": "Archive", "away": "Fallback", "market": "1x2", "avg_p": 70},
    ]))
    candidates = capture._candidate_rows("2026-10-03")
    assert [(row["home"], row["away"]) for row in candidates] == [("Archive", "Fallback")]


def test_capture_respects_raised_ceiling_and_persists_fixture_receipt(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(capture, "MAX_FIXTURES_CEILING", 24)
    rows = [
        {"date": "2026-10-03", "home": f"Home{i}", "away": f"Away{i}", "market": "1x2", "avg_p": 100 - i}
        for i in range(30)
    ]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))

    from edgefactory.sources import betexplorer_odds as be

    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "reset_fetch_count", lambda: None)
    monkeypatch.setattr(
        be,
        "betexplorer_odds_rows_for_pick",
        lambda pick, day, norm_team_fn=None: [
            {"date": day, "home": pick["home"], "away": pick["away"], "market": "1x2", "selection": "home", "odds": 2.0}
        ],
    )
    monkeypatch.setattr(be, "run_stats", lambda: {"be_429": 0, "be_cooling_down": False, "be_cached": 0, "be_fetches": 0})
    receipt = capture.capture("2026-10-03", max_fixtures=99)
    assert receipt["attempted"] == 24
    assert receipt["fixtures_with_rows"] == 24
    payload = json.loads((tmp_path / "betexplorer_capture_2026-10-03.json").read_text())
    assert len(payload["attempted_fixtures"]) == 24
    assert payload["attempted_fixtures"][0]["home"] == "Home0"
