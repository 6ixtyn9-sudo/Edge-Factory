"""Offline tests for the theoddsapi adapter. No network, no API key."""

from __future__ import annotations

import json

from edgefactory.sources import theoddsapi


SPORTS = [
    {"key": "soccer_sweden_allsvenskan", "group": "Soccer", "title": "Allsvenskan", "active": True},
    {"key": "soccer_norway_eliteserien", "group": "Soccer", "title": "Eliteserien", "active": True},
    {"key": "soccer_epl", "group": "Soccer", "title": "EPL", "active": True},
]

PICK = {
    "home": "Halmstad", "away": "Sirius",
    "league": "Sweden Allsvenskan", "date": "2026-08-03", "kickoff": "03-08, 18:00",
}

EVENTS = [
    {"id": "evt_swapped", "commence_time": "2026-08-03T16:00:00Z",
     "home_team": "IK Sirius", "away_team": "Halmstads BK"},
    {"id": "evt_right", "commence_time": "2026-08-03T16:00:00Z",
     "home_team": "Halmstads BK", "away_team": "IK Sirius"},
    {"id": "evt_other_day", "commence_time": "2026-08-05T16:00:00Z",
     "home_team": "Halmstads BK", "away_team": "Djurgarden"},
]

PAYLOAD = {
    "id": "evt_right", "sport_key": "soccer_sweden_allsvenskan", "sport_title": "Allsvenskan",
    "bookmakers": [
        {"key": "pinnacle", "title": "Pinnacle", "markets": [
            {"key": "h2h", "outcomes": [
                {"name": "Halmstads BK", "price": 2.10},
                {"name": "Draw", "price": 3.40},
                {"name": "IK Sirius", "price": 3.25}]},
            {"key": "totals", "outcomes": [
                {"name": "Over", "price": 1.95, "point": 2.5},
                {"name": "Under", "price": 1.85, "point": 2.5},
                {"name": "Over", "price": 9.0, "point": 4.5}]},
        ]},
        {"key": "betsson", "title": "Betsson", "markets": [
            {"key": "h2h", "outcomes": [
                {"name": "Halmstads BK", "price": 2.05},
                {"name": "Draw", "price": 3.35},
                {"name": "IK Sirius", "price": 3.30},
                {"name": "Halmstads BK", "price": "not-a-price"}]},
        ]},
    ],
}


def test_league_resolution():
    assert theoddsapi.sport_key_for_league("Sweden Allsvenskan", SPORTS) == "soccer_sweden_allsvenskan"
    assert theoddsapi.sport_key_for_league("Eliteserien", SPORTS) == "soccer_norway_eliteserien"
    assert theoddsapi.sport_key_for_league("Belarus Vysshaya Liga", SPORTS) is None
    assert theoddsapi.sport_key_for_league("", SPORTS) is None
    # regression (2026-08-03 live): "Ie2" -> norm "ie" must NOT containment-hit
    # anything (false-positive on "...premiership..." keys, wasted a free events call)
    sports_with_spl = SPORTS + [{"key": "soccer_spl", "group": "Soccer",
                                 "title": "Scottish Premiership", "active": True}]
    assert theoddsapi.sport_key_for_league("Ie2", sports_with_spl) is None


def test_match_event_pair_constrained():
    ev = theoddsapi.match_event(PICK, EVENTS)
    assert ev is not None and ev["id"] == "evt_right"


def test_match_event_no_result():
    ghost = dict(PICK, home="No Such", away="Teams FC")
    assert theoddsapi.match_event(ghost, EVENTS) is None


def test_rows_parse_and_filter():
    rows = theoddsapi.rows_from_event_odds(PICK, EVENTS[1], PAYLOAD)
    # Pinnacle: 3x h2h + 3x totals@2.5/4.5 (TOTAL_POINTS default keeps 1.5-4.5)
    # Betsson:  3x h2h (one malformed price dropped)
    assert len(rows) == 9
    prices = {(r["market"], r["selection"], r["bookmaker"]): r["odds"] for r in rows}
    assert prices[("1x2", "home", "Pinnacle")] == 2.10
    assert prices[("1x2", "draw", "Pinnacle")] == 3.40
    assert prices[("ou_2.5", "under", "Pinnacle")] == 1.85
    assert prices[("ou_4.5", "over", "Pinnacle")] == 9.0
    assert prices[("1x2", "away", "Betsson")] == 3.30
    assert all(r["market"] in {"1x2", "ou_2.5", "ou_4.5"} for r in rows)
    assert all(set(theoddsapi.COLUMNS) == set(r.keys()) for r in rows)
    assert all(r["source"] == "theoddsapi" and r["source_type"] == "odds" for r in rows)


def test_budget_hard_stop(tmp_path, monkeypatch):
    ledger = tmp_path / "usage.json"
    monkeypatch.setattr(theoddsapi, "USAGE_FILE", ledger)
    monkeypatch.setattr(theoddsapi, "MONTHLY_BUDGET", 10)
    fp = theoddsapi._key_fp("fake-key")
    assert theoddsapi._budget_ok(4, fp, day="2026-08-03")
    theoddsapi._record_charge(4, fp, {}, day="2026-08-03")
    theoddsapi._record_charge(4, fp, {}, day="2026-08-03")
    assert not theoddsapi._budget_ok(4, fp, day="2026-08-03")  # 8 + 4 > 10 -> stop
    data = json.loads(ledger.read_text())
    assert data["keys"][fp]["months"]["2026-08"]["credits"] == 8


def test_server_remaining_overrides_local(tmp_path, monkeypatch):
    ledger = tmp_path / "usage.json"
    fp = theoddsapi._key_fp("fake-key")
    ledger.write_text(json.dumps({"version": 2, "keys": {fp: {
        "months": {}, "last_server_used": 499, "last_server_remaining": 1,
        "exhausted": False, "exhausted_reason": None, "exhausted_at": None}}}))
    monkeypatch.setattr(theoddsapi, "USAGE_FILE", ledger)
    monkeypatch.setattr(theoddsapi, "MONTHLY_BUDGET", 480)
    assert not theoddsapi._budget_ok(2, fp, day="2026-08-03")


def test_key_ring_rotation(tmp_path, monkeypatch):
    ledger = tmp_path / "usage.json"
    monkeypatch.setattr(theoddsapi, "USAGE_FILE", ledger)
    monkeypatch.setattr(theoddsapi, "API_KEYS", ("k1", "k2", "k3"))
    assert len(theoddsapi._key_ring()) == 3
    assert set(theoddsapi._key_ring()) == {"k1", "k2", "k3"}
    # daily offset spreads wear deterministically across the ring
    assert theoddsapi._key_ring() == theoddsapi._key_ring()
    fp1 = theoddsapi._key_fp("k1")
    # every ring key is initially active-eligible
    assert theoddsapi._active_key(day="2026-08-03") in ("k1", "k2", "k3")
    # exhaust ring keys one by one; active always picks a live one
    for k in theoddsapi._key_ring():
        theoddsapi._mark_exhausted(theoddsapi._key_fp(k), "test")
    assert theoddsapi._active_key(day="2026-08-03") is None
    theoddsapi.unmark_exhausted()
    assert theoddsapi._active_key(day="2026-08-03") in ("k1", "k2", "k3")
    slot = json.loads(ledger.read_text())["keys"][fp1]
    assert slot["exhausted"] is False


def test_budget_stop_marks_active_key_unusable(tmp_path, monkeypatch):
    ledger = tmp_path / "usage.json"
    monkeypatch.setattr(theoddsapi, "USAGE_FILE", ledger)
    monkeypatch.setattr(theoddsapi, "MONTHLY_BUDGET", 3)
    monkeypatch.setattr(theoddsapi, "API_KEYS", ("k1", "k2"))
    spent = theoddsapi._key_ring()[0]
    theoddsapi._record_charge(3, theoddsapi._key_fp(spent), {}, day="2026-08-03")
    # spent key is over-budget -> active_key must return the other ring key
    active = theoddsapi._active_key(day="2026-08-03")
    assert active is not None and active != spent


def test_shortlist_reads_frozen_archive(tmp_path, monkeypatch):
    (tmp_path / "picks_2026-08-03.json").write_text(json.dumps([
        {"home": "Halmstad", "away": "Sirius", "league": "Sweden Allsvenskan",
         "date": "2026-08-03", "kickoff": "03-08, 18:00"},
        {"home": "Halmstad", "away": "Sirius", "league": "Sweden Allsvenskan",
         "date": "2026-08-03", "kickoff": "03-08, 18:00"},
        {"home": "", "away": "Broken Row"},
    ]))
    monkeypatch.setattr(theoddsapi, "LOCALDATA", tmp_path)
    fixtures = theoddsapi.shortlist("2026-08-03")
    assert len(fixtures) == 1
    assert fixtures[0]["home"] == "Halmstad"
    assert theoddsapi.shortlist("2026-01-01") == []


def test_cost_model(monkeypatch):
    monkeypatch.setattr(theoddsapi, "MARKETS", ("h2h", "totals"))
    monkeypatch.setattr(theoddsapi, "REGIONS", ("eu",))
    assert theoddsapi.cost_per_event() == 2
    monkeypatch.setattr(theoddsapi, "MARKETS", ("h2h", "totals", "btts"))
    assert theoddsapi.cost_per_event() == 3


# --- red-team 2026-08-03: year-boundary bug fix -----------------------------


def test_kickoff_year_comes_from_pick_date_not_wall_clock():
    from datetime import datetime as _dt, timezone as _tz
    p = {"kickoff": "01-01, 12:00", "date": "2027-01-01"}
    assert theoddsapi._pick_kickoff_utc(p) == _dt(2027, 1, 1, 10, 0, tzinfo=_tz.utc)
    p2 = {"kickoff": "31-12, 23:00", "date": "2026-12-31"}
    assert theoddsapi._pick_kickoff_utc(p2) == _dt(2026, 12, 31, 21, 0, tzinfo=_tz.utc)
    # forward slate crossing New Year: run in Dec, fixture in Jan
    p3 = {"kickoff": "02-01, 19:00", "date": "2027-01-02"}
    assert theoddsapi._pick_kickoff_utc(p3) == _dt(2027, 1, 2, 17, 0, tzinfo=_tz.utc)
    # missing date degrades to current year but still parses
    p4 = {"kickoff": "03-08, 18:00"}
    assert theoddsapi._pick_kickoff_utc(p4).year == _dt.now(_tz.utc).year


# --- red-team 2026-08-03: atomic + serialized ledger writes -----------------


def test_ledger_writes_atomic_and_no_tmp_litter(tmp_path, monkeypatch):
    ledger = tmp_path / "usage.json"
    monkeypatch.setattr(theoddsapi, "USAGE_FILE", ledger)
    monkeypatch.setattr(theoddsapi, "USAGE_LOCK_FILE", tmp_path / "usage.lock")
    fp = theoddsapi._key_fp("k")
    theoddsapi._record_charge(2, fp, {}, day="2026-08-03")
    data = json.loads(ledger.read_text())
    assert data["keys"][fp]["months"]["2026-08"]["credits"] == 2
    assert not (tmp_path / "usage.json.tmp").exists()


def test_ledger_concurrent_writers_never_torn(tmp_path, monkeypatch):
    import threading
    ledger = tmp_path / "usage.json"
    monkeypatch.setattr(theoddsapi, "USAGE_FILE", ledger)
    monkeypatch.setattr(theoddsapi, "USAGE_LOCK_FILE", tmp_path / "usage.lock")
    fp = theoddsapi._key_fp("k")
    errors = []

    def writer():
        try:
            for _ in range(15):
                theoddsapi._record_charge(1, fp, {}, day="2026-08-03")
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=writer) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    data = json.loads(ledger.read_text())  # parses: no torn writes
    # advisory lock + atomic replace => all 45 charges survived
    assert data["keys"][fp]["months"]["2026-08"]["credits"] == 45


def test_ledger_recovers_from_corruption(tmp_path, monkeypatch):
    ledger = tmp_path / "usage.json"
    ledger.write_text("{broken json,,,")
    monkeypatch.setattr(theoddsapi, "USAGE_FILE", ledger)
    monkeypatch.setattr(theoddsapi, "USAGE_LOCK_FILE", tmp_path / "usage.lock")
    fp = theoddsapi._key_fp("k")
    theoddsapi._record_charge(2, fp, {}, day="2026-08-03")
    data = json.loads(ledger.read_text())
    assert data["keys"][fp]["months"]["2026-08"]["credits"] == 2


# --- enhancement pricing wiring (2026-08-05): btts market is captured by default ---


def test_btts_rows_parsed_from_payload():
    payload = {
        "id": "evt_right", "sport_key": "soccer_sweden_allsvenskan", "sport_title": "Allsvenskan",
        "bookmakers": [{"key": "pinnacle", "title": "Pinnacle", "markets": [
            {"key": "h2h", "outcomes": [
                {"name": "Halmstads BK", "price": 2.10},
                {"name": "Draw", "price": 3.40},
                {"name": "IK Sirius", "price": 3.25}]},
            {"key": "btts", "outcomes": [
                {"name": "Yes", "price": 1.95},
                {"name": "No", "price": 1.80}]},
        ]}],
    }
    rows = theoddsapi.rows_from_event_odds(PICK, EVENTS[1], payload)
    sel = {(r["market"], r["selection"]): r["odds"] for r in rows}
    assert sel.get(("btts", "yes")) == 1.95
    assert sel.get(("btts", "no")) == 1.80
    # h2h still parsed alongside btts
    assert sel.get(("1x2", "home")) == 2.10
    # rows carry the unified schema columns
    assert {"market", "selection", "odds", "bookmaker", "captured_at"} <= set(rows[0].keys())


def test_default_markets_include_btts():
    # Pins the wiring: the capture default now requests btts so the
    # enhancement overlay can price btts_yes/btts_no from real captured odds.
    import os
    env_was = os.environ.get("ODDS_API_MARKETS")
    try:
        os.environ.pop("ODDS_API_MARKETS", None)
        import importlib
        import edgefactory.sources.theoddsapi as mod
        importlib.reload(mod)
        assert "btts" in mod.MARKETS
    finally:
        if env_was is not None:
            os.environ["ODDS_API_MARKETS"] = env_was
        else:
            os.environ.pop("ODDS_API_MARKETS", None)


def test_shortlist_reads_vetoed_picks_from_forecast_archive(tmp_path, monkeypatch):
    # Evidence-on-all-buckets (2026-08-05): the capture shortlist must read
    # ALL buckets from a forecast archive — including SKIPPED_VETO, the
    # audit's best ROI bucket — so their prices get captured and their
    # enhancements get scored.
    from edgefactory.sources import theoddsapi
    import json as _json

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    monkeypatch.setattr(theoddsapi, "LOCALDATA", localdata)

    archive = localdata / "picks_2026-08-06.json"
    archive.write_text(_json.dumps([
        {"date": "2026-08-06", "home": "Paide", "away": "Rapid Vienna",
         "kickoff": "2026-08-06T17:00:00Z", "bucket": "SKIPPED_VETO",
         "league": "World UEFA Europa Conference League"},
        {"date": "2026-08-06", "home": "Ajax", "away": "Shelbourne",
         "kickoff": "2026-08-06T19:00:00Z", "bucket": "CAUTION",
         "league": "World UEFA Europa Conference League"},
    ]))
    fixtures = theoddsapi.shortlist("2026-08-06")
    assert len(fixtures) == 2
    pairs = {(f["home"], f["away"]) for f in fixtures}
    assert ("Paide", "Rapid Vienna") in pairs   # vetoed pick IS in the shortlist
    assert ("Ajax", "Shelbourne") in pairs


# ------------------------------------------------- league resolution integrity (2026-08-06)

OFFSEASON_SPORTS = [
    {"key": "soccer_england_league1", "group": "Soccer", "title": "League 1", "active": True},
    {"key": "soccer_england_league2", "group": "Soccer", "title": "League 2", "active": True},
    {"key": "soccer_efl_champ", "group": "Soccer", "title": "Championship", "active": True},
    {"key": "soccer_argentina_primera_division", "group": "Soccer", "title": "Primera División - Argentina", "active": True},
    {"key": "soccer_korea_kleague1", "group": "Soccer", "title": "K League 1", "active": True},
    {"key": "soccer_uefa_champs_league_qualification", "group": "Soccer", "title": "UEFA Champions League Qualification", "active": True},
    {"key": "soccer_spl", "group": "Soccer", "title": "Premiership - Scotland", "active": True},
    {"key": "soccer_sweden_superettan", "group": "Soccer", "title": "Superettan - Sweden", "active": True},
]


def test_league_resolution_never_wrong_competition():
    # 2026-08-06 incident: 13 archived labels junk-resolved to soccer_england_league2
    # via a 6-char "league" token (digit-stripped "League 2"). A wrong competition
    # must always lose to None — provenance fabrication is worse than unpriced.
    for label in ("World UEFA Europa Conference League", "World: UEFA Europa Conference League",
                  "World UEFA Europa League", "World: UEFA Europa League",
                  "Bulgaria First League", "Belarus: Premier League",
                  "Kuwait,Premier League Championship Round", "Scotland League Cup",
                  "Uzbekistan Super League", "Argentina Primera B Metropolitana",
                  "World Friendlies Clubs"):
        assert theoddsapi.sport_key_for_league(label, OFFSEASON_SPORTS) is None, label


def test_league_resolution_uefa_chains_follow_listing():
    # off-season: the main UCL key is unlisted; the qualifiers key is live
    assert (theoddsapi.sport_key_for_league("World UEFA Champions League", OFFSEASON_SPORTS)
            == "soccer_uefa_champs_league_qualification")
    assert (theoddsapi.sport_key_for_league("UCL", OFFSEASON_SPORTS)
            == "soccer_uefa_champs_league_qualification")
    both = OFFSEASON_SPORTS + [{"key": "soccer_uefa_champs_league", "group": "Soccer",
                                "title": "UEFA Champions League", "active": True}]
    assert (theoddsapi.sport_key_for_league("World UEFA Champions League", both)
            == "soccer_uefa_champs_league")
    uecl = OFFSEASON_SPORTS + [{"key": "soccer_uefa_europa_conference_league", "group": "Soccer",
                                "title": "UEFA Europa Conference League", "active": True}]
    assert (theoddsapi.sport_key_for_league("World UEFA Europa Conference League", uecl)
            == "soccer_uefa_europa_conference_league")
    # conference key must NOT absorb the Europa League (distinct competitions)
    assert theoddsapi.sport_key_for_league("World UEFA Europa League", uecl) is None


def test_league_short_codes_exact_and_tier_preserving():
    uecl = [{"key": "soccer_uefa_europa_conference_league", "group": "Soccer",
             "title": "UEFA Europa Conference League", "active": True}]
    assert theoddsapi.sport_key_for_league("ECL", uecl) == "soccer_uefa_europa_conference_league"
    fin = OFFSEASON_SPORTS + [{"key": "soccer_finland_veikkausliiga", "group": "Soccer",
                               "title": "Veikkausliiga - Finland", "active": True}]
    assert theoddsapi.sport_key_for_league("Fi1", fin) == "soccer_finland_veikkausliiga"
    assert theoddsapi.sport_key_for_league("Se2", OFFSEASON_SPORTS) == "soccer_sweden_superettan"
    # digit preserved at code stage: "Se4" (Division 2) must NOT hit Superettan
    assert theoddsapi.sport_key_for_league("Se4", OFFSEASON_SPORTS) is None
    assert theoddsapi.sport_key_for_league("Ie2", OFFSEASON_SPORTS) is None
    # digit-preserving matching: second-tier labels never inherit the top tier
    assert theoddsapi.sport_key_for_league("Korea K League 2", OFFSEASON_SPORTS) is None
    j1 = [{"key": "soccer_japan_j_league", "group": "Soccer", "title": "J League", "active": True}]
    assert theoddsapi.sport_key_for_league("Japan J2 League", j1) is None
    assert theoddsapi.sport_key_for_league("South Korea K League 1", OFFSEASON_SPORTS) == "soccer_korea_kleague1"


def test_containment_fallback_requires_real_overlap():
    sports = OFFSEASON_SPORTS + [
        {"key": "soccer_finland_veikkausliiga", "group": "Soccer", "title": "Veikkausliiga - Finland", "active": True},
        {"key": "soccer_mexico_ligamx", "group": "Soccer", "title": "Liga MX", "active": True},
    ]
    # full-token containment still resolves legitimately
    assert theoddsapi.sport_key_for_league("Finland Veikkausliiga", sports) == "soccer_finland_veikkausliiga"
    assert theoddsapi.sport_key_for_league("Mexico,Liga Mx Apertura", sports) == "soccer_mexico_ligamx"
    # a generic "championship"/"league" token never suffices on its own
    assert theoddsapi.sport_key_for_league("Kuwait Premier League Championship Round", sports) is None


def test_fetch_fixtures_refreshes_stale_sports_cache(monkeypatch):
    # comp availability swaps at season boundaries faster than the 7-day cache
    # rolls; one free /sports refresh must re-resolve stale misses.
    stale = [{"key": "soccer_sweden_allsvenskan", "group": "Soccer", "title": "Allsvenskan", "active": True}]
    fresh = stale + [{"key": "soccer_uefa_europa_conference_league", "group": "Soccer",
                      "title": "UEFA Europa Conference League", "active": True}]
    calls = {"refresh": 0}

    def fake_load_sports(*, refresh=False):
        if refresh:
            calls["refresh"] += 1
            return fresh
        return stale

    fixture = {"home": "Halmstad", "away": "Sirius",
               "league": "World UEFA Europa Conference League",
               "date": "2026-08-03", "kickoff": "03-08, 18:00"}
    monkeypatch.setattr(theoddsapi, "API_KEYS", ("test-key",))
    monkeypatch.setattr(theoddsapi, "load_sports", fake_load_sports)
    monkeypatch.setattr(theoddsapi, "fetch_events", lambda key: EVENTS)
    monkeypatch.setattr(theoddsapi, "fetch_event_odds", lambda key, event_id, day=None: PAYLOAD)
    rows, unmatched, matched = theoddsapi.fetch_fixtures([fixture], day="2026-08-03")
    assert calls["refresh"] == 1                    # exactly one free refresh
    assert matched == 1 and not unmatched           # stale-cache miss healed
    assert rows                                     # real rows out of the payload
