"""Pinnacle team totals: read-only evidence, daily card coverage (approved 2026-10-13).

Nothing here may touch the price ledger, the enhancement quote list or the gate.
"""
from __future__ import annotations

import json

import pytest

from edgefactory.sources import pinnapi_odds as pa

DAY = "2026-10-13"


@pytest.fixture(autouse=True)
def _localdata(tmp_path, monkeypatch):
    monkeypatch.setattr(pa, "LOCALDATA", tmp_path)
    monkeypatch.setenv("PINNAPI_KEY", "test-pinnapi-key")
    yield
    pa.reset_auth_memory()


def _event(team_totals=None, team_total=None):
    main = {"money_line": {"home": 2.0, "draw": 3.2, "away": 3.6}}
    if team_totals is not None:
        main["team_totals"] = team_totals
    if team_total is not None:
        main["team_total"] = team_total
    return {"event_id": 1, "home": "Team A", "away": "Team B", "starts": "2026-10-13T17:00:00Z",
            "league_name": "Test League", "periods": {"num_0": main}}


def _payload():
    return {"sport_id": 1, "events": [_event(team_totals={
        "home": {"2.5": {"points": 2.5, "over": 1.68, "under": 2.15, "max": 100},
                 "3.5": {"points": 3.5, "over": 2.75, "under": 1.41, "max": 100}},
        "away": {"0.5": {"points": 0.5, "over": 1.94, "under": 1.83, "max": 100}},
    })]}


def test_team_totals_keyed_by_line_become_tt_rows():
    rows = pa.team_total_rows(_payload(), day=DAY)
    assert {(r["market"], r["selection"]) for r in rows} == {
        ("tt_home_2.5", "over"), ("tt_home_2.5", "under"),
        ("tt_home_3.5", "over"), ("tt_home_3.5", "under"),
        ("tt_away_0.5", "over"), ("tt_away_0.5", "under"),
    }
    assert all(r["home"] == "Team A" and r["away"] == "Team B" for r in rows)
    assert all(r["source"] == pa.TEAM_TOTAL_EVIDENCE_SOURCE for r in rows)


def test_single_line_team_total_fallback_and_bad_prices_skipped():
    payload = {"events": [_event(team_total={
        "home": {"points": 1.5, "over": 1.9, "under": 1.9},
        "away": {"points": 1.5, "over": 0.9, "under": "n/a"},
    })]}
    rows = pa.team_total_rows(payload, day=DAY)
    assert {(r["market"], r["selection"]) for r in rows} == {
        ("tt_home_1.5", "over"), ("tt_home_1.5", "under")}


def test_capture_writes_evidence_without_adding_price_rows(monkeypatch):
    monkeypatch.setattr(pa, "get_json", lambda url, timeout=30, auth="header":
                        (200, _payload(), {}))
    rows, stats = pa.capture_day(DAY)
    assert stats["status"] == "ok"
    assert not any(str(r.get("market", "")).startswith("tt_") for r in rows)
    body = json.loads((pa.LOCALDATA / f"pinnapi_odds_team_totals_shadow_{DAY}.json").read_text())
    assert body["counts"]["fixtures_with_team_totals"] == 1
    assert body["counts"]["rows"] == 6
    assert "tt_home_2.5" in body["counts"]["markets"]


def _write_evidence(rows):
    (pa.LOCALDATA / f"pinnapi_odds_team_totals_shadow_{DAY}.json").write_text(
        json.dumps({"rows": rows}))


def _row(home, away, market):
    return {"home": home, "away": away, "market": market, "selection": "over", "odds": 1.9}


def test_card_coverage_matches_either_orientation_and_both_sides():
    _write_evidence([_row("Team A", "Team B", "tt_home_2.5"), _row("Team A", "Team B", "tt_away_0.5")])
    card = [{"home": "Team A", "away": "Team B"}, {"home": "Missing", "away": "Other"}]
    out = pa.card_team_total_coverage(DAY, card, localdata=pa.LOCALDATA)
    assert out["status"] == "ok"
    assert out["card_fixtures"] == 2
    assert out["matched"] == 1
    assert out["with_team_totals"] == 1
    assert out["with_both_sides"] == 1
    assert out["unmatched_examples"] == ["Missing v Other"]

    flipped = pa.card_team_total_coverage(DAY, [{"home": "Team B", "away": "Team A"}],
                                          localdata=pa.LOCALDATA)
    assert flipped["matched"] == 1 and flipped["with_both_sides"] == 1

    _write_evidence([_row("Team A", "Team B", "tt_home_2.5")])  # one side only
    one_sided = pa.card_team_total_coverage(DAY, [{"home": "Team A", "away": "Team B"}],
                                            localdata=pa.LOCALDATA)
    assert one_sided["matched"] == 1 and one_sided["with_team_totals"] == 1
    assert one_sided["with_both_sides"] == 0


def test_card_coverage_reports_missing_evidence_without_raising():
    out = pa.card_team_total_coverage(DAY, [{"home": "A", "away": "B"}], localdata=pa.LOCALDATA)
    assert out == {"status": "no_evidence_file"}
