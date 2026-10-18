"""alternate_totals (the provider's key for alternate over/under lines).

No network: the HTTP layer is replaced. Production requests are unchanged; the
override is only used by the opt-in diagnostic.
"""
import sys
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from edgefactory.sources import theoddsapi as tha  # noqa: E402

PICK = {"home": "Alpha FC", "away": "Beta United", "date": "2026-10-18",
        "league": "Test League", "kickoff": "20:00"}
EVENT = {"id": "ev1", "home_team": "Alpha FC", "away_team": "Beta United",
         "commence_time": "2026-10-18T18:00:00Z"}


def _payload(market_key: str, points):
    outcomes = []
    for pt in points:
        outcomes.append({"name": "Over", "price": 1.2, "point": pt})
        outcomes.append({"name": "Under", "price": 4.0, "point": pt})
    return {"bookmakers": [{"key": "bk1", "title": "Book One",
                            "markets": [{"key": market_key, "outcomes": outcomes}]}]}


def test_alternate_totals_rows_keep_1_5_line(monkeypatch):
    monkeypatch.setattr(tha, "TOTAL_POINTS", ("1.5", "2.5"))
    rows = tha.rows_from_event_odds(PICK, EVENT, _payload("alternate_totals", [1.5, 2.5]))
    markets = {r["market"] for r in rows}
    assert "ou_1.5" in markets
    assert "ou_2.5" in markets


def test_legacy_totals_alt_key_still_parsed(monkeypatch):
    monkeypatch.setattr(tha, "TOTAL_POINTS", ("1.5",))
    rows = tha.rows_from_event_odds(PICK, EVENT, _payload("totals_alt", [1.5]))
    assert any(r["market"] == "ou_1.5" for r in rows)


def test_default_request_markets_unchanged(monkeypatch):
    calls = []

    def fake_get(path, params, cost=None, day=None):
        calls.append((path, dict(params), cost))
        return {}, None

    monkeypatch.setattr(tha, "_get_json", fake_get)
    monkeypatch.setattr(tha, "MARKETS", ("h2h", "totals", "team_totals"))
    tha.fetch_event_odds("soccer_x", "ev1")
    _, params, cost = calls[0]
    assert params["markets"] == "h2h,totals,team_totals"
    assert cost == tha.cost_per_event()


def test_override_requests_only_alternate_totals_and_costs_one_per_region(monkeypatch):
    calls = []

    def fake_get(path, params, cost=None, day=None):
        calls.append((path, dict(params), cost))
        return {}, None

    monkeypatch.setattr(tha, "_get_json", fake_get)
    monkeypatch.setattr(tha, "MARKETS", ("h2h", "totals", "team_totals"))
    monkeypatch.setattr(tha, "REGIONS", ("eu",))
    tha.fetch_event_odds("soccer_x", "ev1", markets=("alternate_totals",))
    _, params, cost = calls[0]
    assert params["markets"] == "alternate_totals"
    assert cost == 1


def test_production_default_requests_no_alternate_or_fake_totals_key():
    """Production requests stay on real, requested-today markets: neither the
    fake key totals_alt nor alternate_totals is in the default request list.
    (conftest clears ODDS_API_MARKETS, so this is the code default.)"""
    assert "totals_alt" not in tha.MARKETS
    assert "alternate_totals" not in tha.MARKETS
    assert "totals" in tha.MARKETS
