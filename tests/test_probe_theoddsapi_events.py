"""The theoddsapi events probe must report match failures and never spend credits."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import probe_theoddsapi_events as probe  # noqa: E402
from edgefactory.sources import theoddsapi as tha  # noqa: E402


def _stub(monkeypatch, fixtures, events_by_key):
    calls = {"odds": 0, "events": []}
    monkeypatch.setattr(tha, "API_KEYS", ["k_test"])
    monkeypatch.setattr(tha, "shortlist", lambda date: fixtures)
    monkeypatch.setattr(tha, "load_sports", lambda refresh=False: [{"key": "soccer_x"}])
    monkeypatch.setattr(tha, "sport_key_for_league",
                        lambda league, sports: "soccer_x" if league == "Known" else None)

    def fake_events(key):
        calls["events"].append(key)
        return events_by_key.get(key, [])

    def fake_odds(*a, **k):  # must never run
        calls["odds"] += 1
        raise AssertionError("probe must not call an odds endpoint")

    monkeypatch.setattr(tha, "fetch_events", fake_events)
    monkeypatch.setattr(tha, "fetch_event_odds", fake_odds)
    return calls


def test_reports_each_outcome_and_spends_no_odds_credits(monkeypatch, capsys):
    fixtures = [
        {"home": "Wolves", "away": "Bolton", "league": "Known", "date": "2026-10-13"},
        {"home": "Germany W", "away": "Japan W", "league": "Unknown", "date": "2026-10-13"},
    ]
    events = {"soccer_x": [{"id": "e1", "home_team": "Wolverhampton Wanderers",
                            "away_team": "Bolton Wanderers",
                            "commence_time": "2026-10-13T18:45:00Z"}]}
    calls = _stub(monkeypatch, fixtures, events)
    rc = probe.main(["--date", "2026-10-13"])
    out = capsys.readouterr().out
    assert rc == 0
    assert calls["odds"] == 0
    assert "league not covered" in out
    assert "no event in soccer_x" in out
    assert "closest=" in out
    assert "summary:" in out


def test_no_keys_is_a_clear_exit(monkeypatch, capsys):
    monkeypatch.setattr(tha, "API_KEYS", [])
    assert probe.main(["--date", "2026-10-13"]) == 1
    assert "no ODDS_API_KEYS" in capsys.readouterr().out


def test_no_card_is_not_an_error(monkeypatch, capsys):
    _stub(monkeypatch, [], {})
    assert probe.main(["--date", "2026-10-13"]) == 0
    assert "no frozen card" in capsys.readouterr().out
