"""Red-team regressions for the 2026-10-15 main-lane acca #1 mispricing.

What happened: acca #1 was printed at @13.36 = 4.00 x 3.34. The public market
was about 1.33 x 1.36 (~1.8). Four independent faults let it through:

  1. The relay served a side-market event ("UEFA - Europa League Bookings",
     team names "AZ Alkmaar (Bookings)") whose money line was read as the
     match 1X2.
  2. The coherence gate grouped that event with the real match (same team
     keys after the 9-character fold) and built a 1X2 trio across both events.
  3. A Pinnacle quote captured 13 Oct (37h before the card) was priced as
     today's price. The same-day gate existed but was never called.
  4. Nothing compared the chosen price with the independent quotes that were
     available on the same fixture.

Each test below pins one layer, so a regression in any single layer is
caught even when the other layers would still have refused the price.
"""
from __future__ import annotations

import pytest

import scripts.picks_today as pt
from edgefactory import price_sources as psrc
from edgefactory.sources import pinnapi_odds as pa

DAY = "2026-10-15"
HOME = "AZ Alkmaar"
AWAY = "Hapoel Beer Sheva"


@pytest.fixture(autouse=True)
def _donors_enabled(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", "1")
    monkeypatch.setenv("EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR", "1")
    monkeypatch.delenv("EDGE_FACTORY_FAIR_PRICE_STAKEABLE", raising=False)
    monkeypatch.delenv("EDGE_FACTORY_REQUIRE_PRICE_CORROBORATION", raising=False)
    monkeypatch.delenv("EDGE_FACTORY_REQUIRE_NAMED_BOOK_CORROBORATION", raising=False)
    yield


def _pick(**extra):
    out = {"date": DAY, "home": HOME, "away": AWAY, "market": "1x2",
           "pick": "home", "kickoff_utc": f"{DAY}T16:45:00+00:00"}
    out.update(extra)
    return out


def _pinnacle_row(selection, odds, captured_at, **extra):
    out = {"source": "pinnapi_odds", "provider": "pinnapi_odds",
           "bookmaker": "Pinnacle", "date": DAY, "home": HOME, "away": AWAY,
           "market": "1x2", "selection": selection, "odds": odds,
           "kickoff": f"{DAY}T16:45:00Z", "captured_at": captured_at,
           "league": "UEFA - Europa League"}
    out.update(extra)
    return out


def _bundle(source, rows):
    return pt._odds_bundle_from_rows(
        [psrc.annotate_row(dict(r), source=source) for r in rows], provider=source)


def _run(pick, pinnacle_rows, extra_bundles=()):
    primary = _bundle("pinnapi_odds", pinnacle_rows)
    pt.enrich_with_live_odds([pick], primary, None, list(extra_bundles))
    return pick


# --- layer 3: staleness ----------------------------------------------------

def test_quote_captured_days_before_the_card_is_refused_not_priced():
    """The 13 Oct 22:20 Pinnacle quote priced the 15 Oct card. It must not."""
    pick = _pick()
    rows = [_pinnacle_row("home", 4.0, "2026-10-13T22:20:27+00:00"),
            _pinnacle_row("draw", 5.83, "2026-10-13T22:20:27+00:00"),
            _pinnacle_row("away", 8.9, "2026-10-13T22:20:27+00:00")]
    _run(pick, rows)
    assert pick.get("odds") is None
    assert pick.get("price_push_eligible") is False
    assert pick.get("price_quarantine_reason") == "stale_quote"


def test_undated_quote_is_refused():
    pick = _pick()
    rows = [_pinnacle_row("home", 1.29, None)]
    _run(pick, rows)
    assert pick.get("odds") is None
    assert pick.get("price_push_eligible") is False
    assert pick.get("price_quarantine_reason") == "undated_quote"


def test_quote_captured_on_the_card_day_is_priced():
    pick = _pick()
    rows = [_pinnacle_row("home", 1.2933, f"{DAY}T04:00:00+00:00")]
    _run(pick, rows)
    assert pick.get("odds") == 1.2933
    assert pick.get("price_push_eligible") is True


def test_staleness_is_measured_from_the_card_day_so_replays_still_price():
    """A past card must judge its own quotes by its own day, not wall clock."""
    pick = _pick(date="2026-08-05")
    fresh = _pinnacle_row("home", 1.9, "2026-08-05T09:00:00+00:00", date="2026-08-05",
                          kickoff="2026-08-05T16:00:00Z")
    _run(pick, [fresh])
    assert pick.get("odds") == 1.9


def test_quote_from_two_days_before_a_past_card_is_still_refused():
    pick = _pick(date="2026-08-05")
    old = _pinnacle_row("home", 1.9, "2026-08-02T09:00:00+00:00", date="2026-08-05",
                        kickoff="2026-08-05T16:00:00Z")
    _run(pick, [old])
    assert pick.get("odds") is None
    assert pick.get("price_quarantine_reason") == "stale_quote"


def test_max_age_bound_is_24h_from_card_day_midnight():
    assert pt.MAX_PRICE_AGE_HOURS == 24.0
    pick = _pick()
    ok_row = _pinnacle_row("home", 1.9, "2026-10-14T00:30:00+00:00")   # 23.5h before
    bad_row = _pinnacle_row("home", 1.9, "2026-10-13T23:30:00+00:00")  # 24.5h before
    assert pt._row_age_hours(ok_row, pick) == pytest.approx(23.5)
    assert pt._row_age_hours(bad_row, pick) == pytest.approx(24.5)


# --- layer 4: consensus ----------------------------------------------------

def test_named_book_price_contradicting_independent_quotes_is_quarantined():
    """4.00 against a 1.33 market (ratio 3.0) must not become the price."""
    pick = _pick()
    pinnacle = [_pinnacle_row("home", 4.0, f"{DAY}T04:00:00+00:00")]
    scouting = [{"source": "scoutingstats_odds", "provider": "scoutingstats_odds",
                 "bookmaker": "ScoutingStats", "date": DAY, "home": HOME, "away": AWAY,
                 "market": "1x2", "selection": "home", "odds": 1.33,
                 "kickoff": f"{DAY}T16:45:00Z", "captured_at": f"{DAY}T16:45:00Z",
                 "league": "Europa League"}]
    _run(pick, pinnacle, extra_bundles=[_bundle("scoutingstats_odds", scouting)])
    assert pick.get("odds") is None
    assert pick.get("price_evidence") == pt.PRICE_EVIDENCE_SUSPECT_SOURCE_CONFLICT
    assert pick.get("price_quarantine_reason") == "source_conflict"
    assert pick.get("price_push_eligible") is False
    assert pick["suspect_price"]["conflict"]["ratio"] == pytest.approx(3.008, abs=0.01)


def test_consensus_tolerates_ordinary_book_to_book_spread():
    pick = _pick()
    pinnacle = [_pinnacle_row("home", 1.90, f"{DAY}T04:00:00+00:00")]
    scouting = [{"source": "scoutingstats_odds", "provider": "scoutingstats_odds",
                 "bookmaker": "ScoutingStats", "date": DAY, "home": HOME, "away": AWAY,
                 "market": "1x2", "selection": "home", "odds": 1.80,
                 "kickoff": f"{DAY}T16:45:00Z", "captured_at": f"{DAY}T16:45:00Z",
                 "league": "Europa League"}]
    _run(pick, pinnacle, extra_bundles=[_bundle("scoutingstats_odds", scouting)])
    assert pick.get("odds") == 1.90


def test_same_book_twice_is_not_treated_as_corroboration():
    """Two boards quoting Pinnacle are one opinion; they cannot vouch for each other."""
    assert pt._source_conflict(4.0, []) is None
    assert pt._source_conflict(4.0, [1.33]) == {
        "median": 1.33, "independent_quotes": 1, "ratio": 3.008, "bound": 1.6}
    assert pt._source_conflict(1.9, [1.8]) is None


# --- layer 2: coherence gate ----------------------------------------------

def _gate_row(league, event_id, selection, odds, bookmaker="Pinnacle"):
    return {"source": "pinnapi_odds", "provider": "pinnapi_odds", "date": DAY,
            "home": HOME, "away": AWAY, "market": "1x2", "selection": selection,
            "odds": odds, "bookmaker": bookmaker, "captured_at": f"{DAY}T04:00:00+00:00",
            "league": league, "event_id": event_id}


def test_gate_refuses_a_trio_built_across_two_events():
    """Two events under one fixture key must not yield a trio, even one in band."""
    real = [_gate_row("UEFA - Europa League", 1, "home", 1.2933),
            _gate_row("UEFA - Europa League", 1, "draw", 5.83),
            _gate_row("UEFA - Europa League", 1, "away", 8.9)]
    side = [_gate_row("UEFA - Europa League Bookings", 2, "home", 4.0),
            _gate_row("UEFA - Europa League Bookings", 2, "away", 1.6)]
    kept, refused, summary = pt._gate_one_x_two_rows(real + side)
    assert kept == []
    assert {r["price_coherence"] for r in refused} == {pt._WITHHELD_MIXED_EVENTS}
    assert summary["withheld_fixtures"] == 1


def test_gate_still_prices_a_single_event_book():
    rows = [_gate_row("UEFA - Europa League", 1, "home", 1.2933),
            _gate_row("UEFA - Europa League", 1, "draw", 5.83),
            _gate_row("UEFA - Europa League", 1, "away", 8.9)]
    kept, refused, _summary = pt._gate_one_x_two_rows(rows)
    assert len(kept) == 3 and refused == []


# --- layer 1: source ------------------------------------------------------

def _documented_event(event_id, league, home_name, away_name, money):
    return {"id": event_id, "home": home_name, "away": away_name,
            "league": league, "start_at": "2026-10-15T16:45:00Z",
            "periods": {"num_0": {"money_line": money}}}


def test_relay_side_market_event_never_reaches_the_1x2_index():
    payload = {"events": [
        _documented_event(1, "UEFA - Europa League", HOME, AWAY,
                          {"home": 1.2933, "draw": 5.83, "away": 8.9}),
        _documented_event(2, "UEFA - Europa League Bookings",
                          f"{HOME} (Bookings)", f"{AWAY} (Bookings)",
                          {"home": 4.0, "draw": 4.5, "away": 2.1}),
    ]}
    rows, ok = pa.parse_snapshot(payload, day=DAY)
    assert ok
    assert {r["event_id"] for r in rows} == {1}
    assert {r["odds"] for r in rows if r["selection"] == "home"} == {1.2933}
    # The drop is counted, not silent.
    assert pa.canonicalization_drop_reasons().get("non_match_event") == 1


def test_non_match_qualifier_detection_is_whole_word():
    assert pa._non_match_event("UEFA - Europa League Bookings", HOME, AWAY)
    assert pa._non_match_event("Premier League", f"{HOME} (Corners)", AWAY)
    # A bare word in a real club name is not a side market.
    assert not pa._non_match_event("Premier League", "Cardiff City", "Card United")
    assert not pa._non_match_event("Premier League", "Corner FC", "Specials Town")
    assert not pa._non_match_event("UEFA - Europa League", HOME, AWAY)


def test_side_market_annotation_is_a_squad_marker_so_the_join_refuses_it():
    from edgefactory import identity
    assert identity.squad_markers(f"{HOME} (Bookings)") == frozenset({"non_match"})
    assert identity.squad_markers(HOME) == frozenset()
    assert identity.squad_marker_mismatch(f"{HOME} (Bookings)", HOME)


# --- layer 5: quarantine reasons do not outlive their price --------------

def test_stale_quarantine_reason_from_an_earlier_run_is_cleared():
    pick = _pick(price_quarantine_reason="stale_quote", price_evidence="UNMATCHED")
    rows = [_pinnacle_row("home", 1.2933, f"{DAY}T04:00:00+00:00")]
    _run(pick, rows)
    assert pick.get("odds") == 1.2933
    assert pick.get("price_quarantine_reason") in (None, "")
