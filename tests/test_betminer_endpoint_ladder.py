"""Betminer dated-board probe ladder (2026-11-14 contract repair).

On 2026-11-09 the RapidAPI gateway started answering the documented
``/matches/{date}`` board with ``{"message":"Endpoint ... does not exist"}``
- a ROUTE REMOVAL, not an outage: the same message continued for eight
consecutive daily probe receipts (``localdata/betminer_probe_2026-11-*.json``)
and the provider's published route list no longer carries ``/matches``. The
dated board that IS published is the betting-system route
``/value-bets/{date}`` plus its range form.

This file pins the repair:

* the first (and usually only) probe goes to ``/value-bets/{date}``;
* only a ROUTING 404 earns one second probe of the range form;
* a subscription wall, a silent 404, auth, quota or transport failure cannot
  be fixed by another path, so one call is all they get;
* an operator ``BETMINER_ENDPOINT`` override is exactly one path, no ladder;
* a probe receipt recorded against a path the adapter no longer probes must
  not suppress the re-probe that confirms the repaired contract.

All transport is monkeypatched; nothing here touches the network.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from edgefactory.sources import betminer as bm

DAY = "2026-11-16"
VALUE_BETS = f"https://betminer.p.rapidapi.com/value-bets/{DAY}"
RANGE_FORM = f"https://betminer.p.rapidapi.com/value-bets/{DAY}/{DAY}"
ROUTING_404 = (
    "betminer: HTTP 404 Not Found; "
    '{"message":"Endpoint \'/value-bets/%s\' does not exist"}'
)


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(bm, "LOCALDATA", tmp_path)
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key-material")
    monkeypatch.delenv("BETMINER_ENDPOINT", raising=False)
    bm.reset_state()
    yield tmp_path


def _count_call():
    """Mirror what the real transport does inside get_json: one call consumed
    per attempt, so the stats accounting assertions below are meaningful."""
    bm._CALLS_THIS_RUN += 1


def _value_bets_payload():
    return {
        "success": True,
        "value_bets": [
            {
                "home_team": "Ajax",
                "away_team": "PSV",
                "league": "Eredivisie",
                "kickoff": f"{DAY}T18:45:00Z",
                "market": "1x2",
                "selection": "2",
                "probability": 48,
                "odds": 2.35,
                "bookmaker": "Bet365",
                "published_at": f"{DAY}T08:00:00Z",
            }
        ],
    }


def _routing_404(message_path: str):
    raise bm.UpstreamBlocked(ROUTING_404 % message_path)


# --------------------------------------------------------------------------
# probe order
# --------------------------------------------------------------------------

def test_default_probe_order_is_single_then_range_form():
    assert bm.capture_url(DAY) == VALUE_BETS
    assert bm._candidate_urls(DAY) == [VALUE_BETS, RANGE_FORM]


def test_operator_override_is_exactly_one_path(monkeypatch):
    monkeypatch.setenv("BETMINER_ENDPOINT", "/matches/{date}")
    assert bm._candidate_urls(DAY) == [f"https://betminer.p.rapidapi.com/matches/{DAY}"]


def test_success_on_the_first_path_spends_exactly_one_call(monkeypatch):
    seen = []

    def fake_get(url, timeout=30):
        _count_call()
        seen.append(url)
        return 200, _value_bets_payload(), {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY)
    assert seen == [VALUE_BETS]
    assert stats["status"] == "ok"
    assert stats["schema_shape"] == "value_bets"
    assert stats["requests"] == 1
    assert rows[0]["home"] == "Ajax"
    assert rows[0]["odds_kind"] == "bookmaker"


# --------------------------------------------------------------------------
# the ladder
# --------------------------------------------------------------------------

def test_routing_404_earns_one_range_form_probe(monkeypatch):
    seen = []

    def fake_get(url, timeout=30):
        _count_call()
        seen.append(url)
        if url == VALUE_BETS:
            _routing_404(f"\\/value-bets\\/{DAY}")
        return 200, _value_bets_payload(), {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY)
    assert seen == [VALUE_BETS, RANGE_FORM]
    assert stats["status"] == "ok"
    assert stats["requests"] == 2
    assert stats["http_statuses"] == [404, 200]
    assert stats["endpoint"] == f"https://betminer.p.rapidapi.com/value-bets/{{date}}/{{date}}"
    assert len(rows) == 1


def test_routing_404_on_both_forms_writes_one_receipt_for_the_range_form(monkeypatch, tmp_path):
    def fake_get(url, timeout=30):
        _count_call()
        _routing_404(url.split("betminer.p.rapidapi.com")[-1].replace("/", "\\/"))

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY, localdata=tmp_path)
    assert rows == []
    assert stats["status"] == "unavailable"
    assert stats["reason"] == "http_404_endpoint_contract"
    assert stats["requests"] == 2
    # Multiplicity is the signal: both published dated forms are unrouted.
    assert stats["http_statuses"] == [404, 404]
    assert stats["probe_receipt"] is True
    receipt = json.loads((tmp_path / f"betminer_probe_{DAY}.json").read_text())
    assert receipt["endpoint"] == RANGE_FORM
    assert receipt["http_status"] == 404
    assert "Endpoint" in receipt["provider_message"]
    assert "test-key-material" not in json.dumps(receipt)


def test_subscription_wall_404_does_not_ladder(monkeypatch, tmp_path):
    seen = []

    def fake_get(url, timeout=30):
        _count_call()
        seen.append(url)
        raise bm.UpstreamBlocked(
            'betminer: HTTP 404 Not Found; {"message":"You are not subscribed to this API."}'
        )

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY, localdata=tmp_path)
    assert seen == [VALUE_BETS]
    assert rows == []
    assert stats["reason"] == "http_404_not_subscribed"
    assert stats["requests"] == 1


def test_silent_404_does_not_ladder(monkeypatch, tmp_path):
    seen = []

    def fake_get(url, timeout=30):
        _count_call()
        seen.append(url)
        raise bm.UpstreamBlocked("betminer: HTTP 404 Not Found; ")

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY, localdata=tmp_path)
    assert seen == [VALUE_BETS]
    assert rows == []
    assert stats["reason"] == "http_404_endpoint_contract_unconfirmed"
    assert stats["requests"] == 1


def test_auth_failure_does_not_ladder(monkeypatch):
    seen = []

    def fake_get(url, timeout=30):
        _count_call()
        seen.append(url)
        raise bm.UpstreamBlocked("betminer: HTTP 403 Forbidden; {\"message\":\"blocked\"}")

    monkeypatch.setattr(bm, "get_json", fake_get)
    _, stats = bm.capture_day(DAY)
    assert seen == [VALUE_BETS]
    assert stats["status"] == "auth"
    assert stats["requests"] == 1


def test_override_path_404_is_terminal_without_a_second_probe(monkeypatch, tmp_path):
    monkeypatch.setenv("BETMINER_ENDPOINT", "/matches/{date}")
    seen = []

    def fake_get(url, timeout=30):
        _count_call()
        seen.append(url)
        _routing_404(f"\\/matches\\/{DAY}")

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY, localdata=tmp_path)
    assert seen == [f"https://betminer.p.rapidapi.com/matches/{DAY}"]
    assert rows == []
    assert stats["reason"] == "http_404_endpoint_contract"
    assert stats["requests"] == 1


# --------------------------------------------------------------------------
# receipts across the endpoint change
# --------------------------------------------------------------------------

def test_stale_receipt_from_the_removed_route_does_not_suppress_the_reprobe(monkeypatch, tmp_path):
    # A receipt written while /matches was still the contract describes a
    # path this adapter will never ask for again; binding it would hide the
    # first observation of the REPAIRED contract for up to 24 h.
    bm._persist_probe_receipt(
        DAY,
        endpoint=f"https://betminer.p.rapidapi.com/matches/{DAY}",
        http_status=404,
        reason="http_404_endpoint_contract",
        provider_message=f'{{"message":"Endpoint \'/matches/{DAY}\' does not exist"}}',
        localdata=tmp_path,
    )
    seen = []

    def fake_get(url, timeout=30):
        _count_call()
        seen.append(url)
        return 200, _value_bets_payload(), {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY, localdata=tmp_path)
    assert seen == [VALUE_BETS]
    assert stats["status"] == "ok"
    assert len(rows) == 1


def test_receipt_for_the_current_route_still_suppresses_same_day_reprobe(monkeypatch, tmp_path):
    bm._persist_probe_receipt(
        DAY,
        endpoint=VALUE_BETS,
        http_status=404,
        reason="http_404_endpoint_contract",
        provider_message=f'{{"message":"Endpoint \'/value-bets/{DAY}\' does not exist"}}',
        localdata=tmp_path,
    )

    def should_not_probe(url, timeout=30):
        raise AssertionError("a binding receipt for the current route must short-circuit")

    monkeypatch.setattr(bm, "get_json", should_not_probe)
    rows, stats = bm.capture_day(DAY, localdata=tmp_path)
    assert rows == []
    assert stats["probe_receipt"] is True
    assert stats["requests"] == 0


def test_legacy_match_object_payload_still_parses_on_the_new_route(monkeypatch):
    """The route changed; payloads did not promise to. The dated Match Object
    parser stays wired so a provider that still serves the old wrapper keeps
    producing rows instead of a schema_unrecognized outage."""
    fixture = json.loads(
        (Path(__file__).parent / "fixtures" / "betminer_matches_2026-10-03.json").read_text()
    )

    def fake_get(url, timeout=30):
        _count_call()
        return 200, fixture, {}

    monkeypatch.setattr(bm, "get_json", fake_get)
    rows, stats = bm.capture_day(DAY)
    assert stats["status"] == "ok"
    assert stats["schema_shape"] == "match_objects"
    assert len(rows) == 2
