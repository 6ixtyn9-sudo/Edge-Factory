"""card_enrich lane: budget math, point-in-time discipline and zero-noise wiring.

Offline only. Fixtures are the provider's DOCUMENTED /head-to-head contract and a
fabricated card, so the pre-registered bars (docs/operator/
SOURCE-INTERROGATION-MATRIX-2026-10-10.md) are exercised as *guards* - nothing in
this file registers a rule, activates a model, or touches the pick path.
"""
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from edgefactory import context_rules
from edgefactory.sources import boggio
import scripts.capture_card_enrich as ce

FIXTURES = Path(__file__).resolve().parent / "fixtures"
H2H_DOC = json.loads((FIXTURES / "boggio_head_to_head_documented.json").read_text())
CARD_DAY = "2026-10-11"
CAPTURED = "2026-10-11T06:00:00+00:00"   # strictly before the 14:00Z kickoff
# Every scripted run pins "now" inside the card day, pre-kickoff. Without this the
# suite would rot the moment 2026-10-11 passed, because the freshness guard reads
# the clock rather than the fixture date.
NOW = datetime(2026, 10, 11, 4, 0, tzinfo=timezone.utc)
# Every scripted run pins "now" inside the card day, pre-kickoff. Without this the
NOW = datetime(2026, 10, 11, 4, 0, tzinfo=timezone.utc)
FIXTURE = {"home": "Real Sociedad", "away": "Barcelona",
           "kickoff_utc": "2026-10-11T14:00:00+00:00"}


def _fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _card(localdata):
    localdata.mkdir(parents=True, exist_ok=True)
    (localdata / "picks_today.json").write_text(json.dumps(_fixture("card_enrich_slate_2026-10-11.json")))
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(
        json.dumps(_fixture("boggio_shadow_2026-10-11.json")))
    return localdata


# --------------------------------------------------------------------------------------
# the H2H derivation itself
# --------------------------------------------------------------------------------------

def test_documented_contract_yields_the_dormant_feature_and_drops_offside_rows():
    snap = boggio.parse_head_to_head(H2H_DOC, fixture=FIXTURE, captured_at=CAPTURED)
    assert snap["identity_verified"] is True and snap["usable"] is True
    # three dated encounters, one undated, one dated after the kickoff is irrelevant
    # here; the 2019 row is outside the lookback and the unparseable date is dropped.
    dates = sorted(row["date"] for row in snap["encounters"])
    assert dates == ["2024-09-15", "2025-01-15", "2025-04-20"]
    assert snap["encounters_dropped"] == {"undated": 1, "not_before_kickoff": 0, "too_old": 1}
    assert snap["features"]["h2h_dominance"] == 1 - 8          # home.won - away.won
    # draw share is OURS to derive (both kept encounters finished level); the
    # documented contract publishes no auditable overall draw count.
    assert snap["features"]["h2h_draw_share"] == round(1/3, 4)   # 1 drawn of 3 kept
    assert snap["encounters"][0]["fulltime"] == [2, 1]
    assert [row["date"] for row in snap["encounters"]] == ["2025-04-20", "2024-09-15", "2025-01-15"][:3]
    assert snap["encounters"][0]["first_half"] == [1, 0]


def test_encounter_dates_must_precede_the_target_kickoff():
    fixture = dict(FIXTURE, kickoff_utc="2024-10-01T14:00:00+00:00")
    snap = boggio.parse_head_to_head(H2H_DOC, fixture=fixture, captured_at="2024-09-30T06:00:00+00:00")
    # 2025-04-20 and 2025-01-15 are both AFTER that (earlier) kickoff -> offside;
    # 2019-05-20 predates the lookback window; the undated row is never guessed.
    assert [row["date"] for row in snap["encounters"]] == ["2024-09-15"]
    assert snap["usable"] is True and snap["encounters_dropped"] == {
        "undated": 1, "not_before_kickoff": 2, "too_old": 1}
    # ...and the draw share refuses to exist on a single kept encounter.
    assert "h2h_draw_share" not in snap["features"]


def test_dated_rows_carry_an_as_of_that_is_an_observation_time_not_a_match_date():
    snap = boggio.parse_head_to_head(H2H_DOC, fixture=FIXTURE, captured_at=CAPTURED)
    for row in snap["encounters"]:
        assert row["as_of"] == CAPTURED
        assert "no per-row history timestamp" in row["as_of_basis"]


def test_capture_at_or_after_kickoff_is_ineligible_not_repaired():
    late = dict(FIXTURE, kickoff_utc="2026-10-11T05:00:00+00:00")
    snap = boggio.parse_head_to_head(H2H_DOC, fixture=late, captured_at=CAPTURED)
    assert snap["usable"] is False and snap["reason"] == "captured_at_or_after_kickoff"


def test_missing_kickoff_stamp_fails_closed():
    snap = boggio.parse_head_to_head(
        H2H_DOC, fixture={"home": "Real Sociedad", "away": "Barcelona"}, captured_at=CAPTURED)
    assert snap["usable"] is False and snap["reason"] == "kickoff_unknown"
    # ...but the feature is still derived, so the row stays inspectable.
    assert snap["features"]["h2h_dominance"] == -7


def test_payload_about_other_clubs_is_unverified_identity():
    other = json.loads(json.dumps(H2H_DOC))
    for row in other["data"]["encounters"]:
        row["home_team"], row["away_team"] = "Once Caldas", "Llaneros"
    snap = boggio.parse_head_to_head(other, fixture=FIXTURE, captured_at=CAPTURED)
    assert snap["identity_verified"] is False and snap["usable"] is False
    assert snap["reason"] == "unverified_identity"


def test_garbage_payloads_never_become_features():
    for payload in ({}, {"data": None}, {"data": []}, [], "nope", {"data": {"stats": {}, "encounters": "x"}}):
        snap = boggio.parse_head_to_head(payload, fixture=FIXTURE, captured_at=CAPTURED)
        assert snap["usable"] is False and snap["features"] == {}


def test_snapshot_satisfies_the_dormant_predicate_schema_but_activates_nothing():
    """The captured shape is consumable by the pre-registered vocabulary; the
    vocabulary itself stays unregistered and the bar is what gates activation."""
    snap = boggio.parse_head_to_head(H2H_DOC, fixture=FIXTURE, captured_at=CAPTURED)
    row = dict(snap["features"], identity_verified=snap["identity_verified"],
               captured_at=snap["captured_at"])
    kickoff = FIXTURE["kickoff_utc"]
    assert snap["features"]["h2h_dominance"] == -7
    # A NEGATIVE bar is unrepresentable by design: the dormant vocabulary accepts
    # non-negative thresholds only, so this lane can never seed a home-team-
    # disadvantage predicate. That is a real constraint of the pre-registered
    # grammar, not a bug to paper over - the snapshot stays, the rule does not.
    assert context_rules.holds("h2h_dominance>=0", row, kickoff=kickoff) is False
    with pytest.raises(ValueError):
        context_rules.parse_predicate("h2h_dominance>=-7")
    with pytest.raises(ValueError):
        context_rules.parse_predicate("h2h_goals>=2.5")   # no vocabulary widening


# --------------------------------------------------------------------------------------
# selection: top-6 by proximity to consensus certification
# --------------------------------------------------------------------------------------

def test_ranking_is_by_margin_and_skips_below_threshold_and_squad_pairs():
    card = _fixture("card_enrich_slate_2026-10-11.json")
    chosen, census = ce.select_candidates([r for r in card if r["date"] == CARD_DAY], limit=6)
    assert [(c["home"], c["margin"]) for c in chosen] == [("Real Sociedad", 0.2), ("Athletic Club", 7.0)]
    skipped = census[-1]["skipped_census"]
    assert skipped.get("below_threshold") == 1        # Sevilla 69.4 against a 70 bar
    assert skipped.get("squad_marker_pair") == 1       # Real Sociedad B vs Barcelona
    assert skipped.get("unrankable_rule") == 1         # rule text with no avg_p>= bar


def test_one_call_budget_per_fixture_not_per_market_row():
    card = _fixture("card_enrich_slate_2026-10-11.json")
    row = dict(card[0], market="totals", avg_p=55.4)   # same fixture, second market
    chosen, _ = ce.select_candidates(card + [row], limit=6)
    assert sum(1 for c in chosen if c["fixture_key"] == "realsociedad|barcelona") == 1
    assert [c for c in chosen if c["fixture_key"] == "realsociedad|barcelona"][0]["margin"] == 0.2


def test_limit_bounds_the_slate_selection():
    card = _fixture("card_enrich_slate_2026-10-11.json")
    day_rows = [r for r in card if r["date"] == CARD_DAY] + [
        dict(card[1], home="Girona", away="Elche", league="Spain,Laliga",
             date=CARD_DAY, avg_p=65.1, rule="ml-meta avg_p>=65",
             edge_rule="ml-meta avg_p>=65",
             kickoff_utc="2026-10-11T19:00:00+00:00"),
        dict(card[2], home="Sevilla", away="Valencia", league="Spain,Laliga",
             date=CARD_DAY, avg_p=70.1, rule="2way-unanimous avg_p>=70",
             edge_rule="2way-unanimous avg_p>=70",
             kickoff_utc="2026-10-11T20:00:00+00:00")]
    chosen, _ = ce.select_candidates(day_rows, limit=2)
    # the two tightest bars win; the 7.0-point row is real but not needed
    assert [c["margin"] for c in chosen] == [0.1, 0.1]
    assert [c["home"] for c in chosen] == ["Girona", "Sevilla"]
    chosen_all, _ = ce.select_candidates(day_rows, limit=6)
    assert [c["home"] for c in chosen_all][-1] == "Athletic Club"


# --------------------------------------------------------------------------------------
# ledger, budget and the mandatory pre-flight line
# --------------------------------------------------------------------------------------

def test_quota_header_parsing_and_opaque_pool_labels():
    headers = {"X-RateLimit-Match-Stats-and-Prediction-endpoints-Remaining": "31"}
    assert boggio.quota_remaining(headers) == 31
    assert boggio.quota_remaining({}) is None and boggio.quota_remaining(None) is None
    assert boggio.quota_remaining({"x-ratelimit-other-endpoints-remaining": "9"}) is None
    key = "0123456789abcdef-0123456789abcdef"
    assert boggio.key_fingerprint(key) != key and boggio.key_label(key) == "cdef"
    assert key not in json.dumps({"f": boggio.key_fingerprint(key), "t": boggio.key_label(key)})


def test_h2h_endpoint_whitelist_rejects_any_other_id_shape():
    assert boggio.h2h_url(423169).endswith("/api/v2/head-to-head/423169")
    for bad in (0, -1, True, "423169; DROP", None, 1.5):
        with pytest.raises(ValueError):
            boggio.h2h_url(bad)


def test_budget_unset_fails_closed_even_with_a_full_pool(tmp_path, monkeypatch):
    monkeypatch.delenv(boggio.CARD_ENRICH_BUDGET_ENV, raising=False)
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    plan = boggio.preflight(need_h2h=6, need_listing=0, localdata=tmp_path, day=CARD_DAY,
                            observed_remaining={boggio.key_label("pool-a"): 99,
                                                boggio.key_label("pool-b"): 99})
    assert plan["verdict"] == "budget_disabled" and plan["allowed_calls"] == 0
    assert plan["spendable"] == 0
    assert "calls=6" in plan["math"]     # the arithmetic is printed, not hidden


def test_unmeasured_pool_gets_no_allowance(tmp_path, monkeypatch):
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    plan = boggio.preflight(need_h2h=6, need_listing=0, localdata=tmp_path, day=CARD_DAY)
    assert plan["verdict"] == "unattributed_quota" and plan["allowed_calls"] == 0


def test_monthly_cap_spans_both_pools_and_reserve_is_held_for_production(monkeypatch):
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "10")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "20")
    keys = ("pool-a", "pool-b")
    allowance = boggio.allowance_per_key({}, keys=keys, observed_remaining={
        boggio.key_label("pool-a"): 31, boggio.key_label("pool-b"): 99})
    assert sum(allowance.values()) == 10                     # ring-wide ceiling, not per pool
    assert max(allowance.values()) <= 11                      # pool A: 31 - 20 reserve
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "200")  # cap off: headers rule
    allowance = boggio.allowance_per_key({}, keys=keys, observed_remaining={
        boggio.key_label("pool-a"): 31, boggio.key_label("pool-b"): 99})
    assert allowance == {boggio.key_fingerprint("pool-a"): 11, boggio.key_fingerprint("pool-b"): 79}


def test_month_spend_depletes_the_allowance_across_runs(tmp_path, monkeypatch):
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    fingerprint = boggio.key_fingerprint("pool-a")
    entries = [boggio.record_call([], day=CARD_DAY, fixture_key="f", endpoint=boggio.H2H_ENDPOINT,
                                  pool_index=0, key="pool-a", status=200, remaining=25, spent=True,
                                  what_bought="x") for _ in range(9)]
    boggio.write_call_ledger(entries, tmp_path)
    spend = boggio.spend_by_key(boggio.read_call_ledger(tmp_path, month=boggio.family_month(CARD_DAY)))
    assert spend == {fingerprint: 9}
    plan = boggio.preflight(need_h2h=6, need_listing=0, localdata=tmp_path, day=CARD_DAY,
                            observed_remaining={fingerprint: 25})
    # Deliberately conservative: our own attributed spend is charged AGAINST the
    # provider's remaining reading as well as against the cap, so a stale header
    # cannot re-authorise calls we already made. 25 remain, 9 of them are ours,
    # the cap says 30 - 9 = 21 -> min(25 - 9, 21) = 16.
    assert plan["month_spend_by_key"] == {fingerprint: 9}
    assert plan["allowance_by_key"] == {fingerprint: 16}
    assert plan["verdict"] == "approved"


def test_ledger_prunes_to_its_retention_window(tmp_path, monkeypatch):
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    old = {"month": "2025-11", "charged": True, "key": "deadbeef", "date": "2025-11-01",
           "endpoint": boggio.H2H_ENDPOINT}
    fresh = {"month": boggio.family_month(CARD_DAY), "charged": True, "key": "cafebabe",
             "date": CARD_DAY, "endpoint": boggio.H2H_ENDPOINT}
    assert boggio.write_call_ledger([old, fresh], tmp_path, today=datetime(2026, 10, 11).date()) == 1
    assert boggio.spend_by_key(boggio.read_call_ledger(tmp_path)) == {"cafebabe": 1}


# --------------------------------------------------------------------------------------
# cadence: staleness skip, and the plan/execute boundary
# --------------------------------------------------------------------------------------

def test_staleness_skip_suppresses_a_second_call_inside_the_window(tmp_path, monkeypatch):
    localdata = _card(tmp_path / "ld")
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    # Live snapshot must have usable=True to suppress — dead snapshots must NOT block (poison-window fix)
    snapshots = {"realsociedad|barcelona": {"captured_at": "2026-10-08T06:00:00+00:00", "usable": True}}
    assert boggio.needs_capture("realsociedad|barcelona", snapshots, day=CARD_DAY) is False
    assert boggio.needs_capture("realsociedad|barcelona", snapshots, day="2026-10-15") is True
    assert boggio.needs_capture("athleticclub|getafe", snapshots, day=CARD_DAY) is True
    boggio.persist_snapshots(CARD_DAY, [{"fixture_key": "realsociedad|barcelona", "home": "Real Sociedad",
                                         "away": "Barcelona", "kickoff_utc": FIXTURE["kickoff_utc"],
                                         "captured_at": "2026-10-08T06:00:00+00:00", "usable": True,
                                         "identity_verified": True, "encounters": [], "features": {}}],
                             {"verdict": "approved"}, localdata=localdata)
    plan = ce.plan_run(CARD_DAY, localdata=localdata, limit=6,
                       bootstrap={boggio.key_label("pool-a"): 31, boggio.key_label("pool-b"): 99})
    by_key = {c["fixture_key"]: c for c in plan["candidates"]}
    assert by_key["realsociedad|barcelona"]["stale_skip"] is True
    assert by_key["realsociedad|barcelona"]["needs_call"] is False
    assert by_key["athletic|getafe"]["needs_call"] is True
    assert plan["need_h2h"] == 1     # the skipped fixture costs nothing, which is why weekly fits


def test_plan_mode_never_calls_the_transport(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    calls = []

    def explode(*a, **k):
        calls.append(a)
        raise AssertionError("plan mode must not open a socket")

    monkeypatch.setattr(boggio.urllib.request, "urlopen", explode)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata)], now=NOW) == 0
    assert calls == []
    out = capsys.readouterr().out
    assert "ledger=card_enrich_preflight calls=" in out           # mandatory math line
    assert "mode=plan_only calls_spent=0" in out
    assert not list(localdata.glob("card_enrich_call_ledger.jsonl"))
    assert "key_tail=***" in out                                   # operator-usable pool label


def test_nothing_to_capture_still_prunes_twenty_day_shadow_file(tmp_path, monkeypatch, capsys):
    localdata = tmp_path / "ld"
    localdata.mkdir()
    card = [{"home": "Real Sociedad", "away": "Barcelona", "date": CARD_DAY,
             "kickoff_utc": "2026-10-11T14:00:00+00:00",
             "rule": "ml-meta avg_p>=55", "avg_p": 55.2}]
    (localdata / "picks_today.json").write_text(json.dumps(card))
    stale_shadow = localdata / "card_enrich_shadow_2026-09-21.json"
    stale_shadow.write_text(json.dumps({"schema": 1, "snapshots": []}))
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "20")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    calls = []

    def unexpected_transport(*args, **kwargs):
        calls.append(args)
        raise AssertionError("nothing_to_capture must not open a socket")

    monkeypatch.setattr(boggio.urllib.request, "urlopen", unexpected_transport)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=21", "--execute"], now=NOW) == 0

    out = capsys.readouterr().out
    assert "verdict=nothing_to_capture" in out
    assert "ledger=card_enrich_prune removed=1 retention_days=14" in out
    assert not stale_shadow.exists()
    assert calls == []


def test_listing_is_auto_credited_only_when_preflight_can_pay_for_h2h_too(tmp_path, monkeypatch):
    localdata = _card(tmp_path)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boot = {boggio.key_label("pool-a"): 31, boggio.key_label("pool-b"): 99}
    with_ids = ce.plan_run(CARD_DAY, localdata=localdata, limit=6, bootstrap=boot, now=NOW)
    # A fixture whose provider id was retained from the paid listing needs no
    # extra call; the two ranked fixtures each need one H2H call.
    assert with_ids["unresolved"] == [] and with_ids["need_listing"] == 0
    assert with_ids["need_h2h"] == 2

    # Remove one retained id. The normal offline preflight now credits one
    # listing and charges both it and the H2H it can unlock before any spend.
    shadow = localdata / f"boggio_shadow_{CARD_DAY}.json"
    payload = json.loads(shadow.read_text())
    payload["rows"] = [r for r in payload["rows"] if r["event_id"] != 424002]
    shadow.write_text(json.dumps(payload))
    auto = ce.plan_run(CARD_DAY, localdata=localdata, limit=6, bootstrap=boot, now=NOW)
    assert auto["unresolved"] == ["athletic|getafe"] and auto["need_listing"] == 1
    assert auto["need_h2h"] == 2
    assert auto["preflight"]["need_total"] == 3
    assert auto["preflight"]["verdict"] == "approved"

    # A single spendable call is not enough to buy a listing that cannot unlock
    # an H2H. Keep the direct fixture's known-id H2H eligible, with no listing.
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "1")
    one_call = ce.plan_run(CARD_DAY, localdata=localdata, limit=6, bootstrap=boot, now=NOW)
    assert one_call["need_listing"] == 0
    assert one_call["need_h2h"] == 1
    assert one_call["preflight"]["allowed_calls"] == 1


def test_paid_listing_is_not_repeated_on_the_same_date(tmp_path, monkeypatch):
    localdata = _card(tmp_path)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(json.dumps({"schema": 1, "rows": []}))
    boot = {boggio.key_label("pool-a"): 31, boggio.key_label("pool-b"): 99}
    first = ce.plan_run(CARD_DAY, localdata=localdata, limit=6, bootstrap=boot, now=NOW)
    assert first["need_listing"] == 1

    entries = []
    boggio.record_call(entries, day=CARD_DAY, fixture_key="listing",
                       endpoint=boggio.H2H_ENDPOINT + ":listing", pool_index=0, key="pool-a",
                       status=200, remaining=30, spent=True, what_bought="fixture-id resolution")
    boggio.write_call_ledger(entries, localdata)
    repeated = ce.plan_run(CARD_DAY, localdata=localdata, limit=6, bootstrap=boot, now=NOW)
    assert repeated["listing_used_today"] is True
    assert repeated["need_listing"] == 0 and repeated["need_h2h"] == 0
    assert repeated["preflight"]["need_total"] == 0


# --------------------------------------------------------------------------------------
# execution against a faked transport: attribution, fail-closed, no leakage
# --------------------------------------------------------------------------------------

class _Response:
    def __init__(self, payload, remaining):
        self.status, self._body = 200, json.dumps(payload).encode()
        self.headers = {"X-RateLimit-Match-Stats-and-Prediction-endpoints-Remaining": str(remaining),
                        "Content-Type": "application/json"}

    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self, n): return self._body[:n]


def _fake_transport(payloads, seen):
    def fake(req, timeout=None):
        url = req.full_url
        seen.append(url)
        for needle, payload in payloads.items():
            if needle in url:
                return _Response(payload, 30)
        return _Response({"data": []}, 30)
    return fake


def test_execute_pays_at_most_the_pre_flight_allowance_and_ledgers_every_call(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "20")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boggio.reset_state()
    seen = []
    other = json.loads(json.dumps(H2H_DOC))
    for row in other["data"]["encounters"]:
        row["home_team"], row["away_team"] = "Sevilla", "Villarreal"
    monkeypatch.setattr(boggio.urllib.request, "urlopen", _fake_transport(
        {"424001": H2H_DOC, "424002": other}, seen))
    boot = {boggio.key_label("pool-a"): 31, boggio.key_label("pool-b"): 99}
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31",
                    "--pool-remaining", f"{boggio.key_label('pool-b')}=99", "--execute"], now=NOW) == 0
    assert len(seen) == 2 and all("/head-to-head/" in url for url in seen)
    out = capsys.readouterr().out
    assert "ledger=card_enrich_preflight calls=2" in out
    assert "mode=execute calls_spent=2 usable_snapshots=1" in out

    entries = boggio.read_call_ledger(localdata)
    assert len(entries) == 2 and all(e["charged"] and e["endpoint"] == boggio.H2H_ENDPOINT for e in entries)
    assert {e["key_tail"] for e in entries} == {"pool-a"[-4:], "pool-b"[-4:]}  # ring spread, not one pool
    assert all(e["family_remaining"] == 30 for e in entries)
    usable = [e for e in entries if "identity_verified=True" in e["what_it_bought"]]
    assert len(usable) == 1 and "h2h_dominance" in usable[0]["what_it_bought"]
    assert "pool-a" not in json.dumps(entries) and "pool-b" not in json.dumps(entries)

    snapshot_file = localdata / f"card_enrich_shadow_{CARD_DAY}.json"
    payload = json.loads(snapshot_file.read_text())
    assert payload["preflight"]["verdict"] == "approved"
    snap = payload["snapshots"][0]
    assert snap["usable"] is True and snap["features"]["h2h_dominance"] == -7
    assert snap["selection"]["margin"] == 0.2 and snap["event_id"] == 424001
    assert payload["provenance"]["cadence"].startswith("weekly at most")


def test_execute_stops_when_the_budget_says_zero_and_spends_nothing(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    seen = []
    monkeypatch.setattr(boggio.urllib.request, "urlopen",
                        _fake_transport({"head-to-head": H2H_DOC}, seen))
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0
    assert seen == [] and "calls_spent=0 verdict=budget_disabled" in capsys.readouterr().out


def test_a_refusal_still_costs_a_ledger_line(tmp_path, monkeypatch):
    """A rejected key is an attributed spend, never an unexplained gap."""
    localdata = _card(tmp_path)
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boggio.reset_state()

    def refuse(req, timeout=None):
        raise boggio.UpstreamBlocked("boggio: 402 quota")

    monkeypatch.setattr(boggio.urllib.request, "urlopen", refuse)
    entries = boggio.read_call_ledger(localdata)
    boggio.record_call(entries, day=CARD_DAY, fixture_key="x", endpoint=boggio.H2H_ENDPOINT,
                       pool_index=0, key="pool-a", status=402, remaining=None, spent=False,
                       what_bought="rejected", error=RuntimeError("x"))
    assert entries[0]["charged"] is False and entries[0]["error_class"] == "RuntimeError"
    assert "pool-a" not in json.dumps(entries)


def test_a_transport_failure_is_still_attributed_to_a_named_pool(tmp_path, monkeypatch, capsys):
    """The crash that this path used to have, and the lie it would have told.

    A URLError raised before any response arrives appends nothing to the ring's
    attempt list, so pool attribution has to come from the loop cursor. If it
    comes from the attempt list instead the run dies mid-capture (UnboundLocalError)
    or books the spend against no pool at all - unattributed depletion, the one
    thing the budget rules forbid.
    """
    localdata = _card(tmp_path)
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "20")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boggio.reset_state()
    import urllib.error

    def die(req, timeout=None):
        raise urllib.error.URLError("no route to host")

    monkeypatch.setattr(boggio.urllib.request, "urlopen", die)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata), "--execute",
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31",
                    "--pool-remaining", f"{boggio.key_label('pool-b')}=99"], now=NOW) == 0
    entries = boggio.read_call_ledger(localdata)
    assert len(entries) == 2
    assert all(e["charged"] is True and e["error_class"] == "UpstreamBlocked" for e in entries)
    # Both failures land on the pool the ring cursor was pointing at, and the
    # cursor only advances on a DELIVERED response - so a pool that never answers
    # is not silently credited with the next fixture's spend either.
    assert [e["pool_index"] for e in entries] == [1, 1]          # named, not guessed
    assert [e["key_tail"] for e in entries] == ["ol-a", "ol-a"]
    blob = json.dumps(entries) + (localdata / f"card_enrich_shadow_{CARD_DAY}.json").read_text()
    assert "no route to host" not in blob                        # transport noise stays out
    assert "URLError" not in blob
    assert "pool-a" not in json.dumps(entries)
    # the ledger is durable (it is the budget), the snapshot is a runtime file
    assert (localdata / "card_enrich_call_ledger.jsonl").exists()
    assert "calls_spent=2 usable_snapshots=0" in capsys.readouterr().out


def test_run_ceiling_refuses_an_unplanned_burst(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    seen = []
    monkeypatch.setattr(boggio.urllib.request, "urlopen", _fake_transport({"head-to-head": H2H_DOC}, seen))
    fingerprint = boggio.key_fingerprint("pool-a")
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata), "--limit", "9",
                    "--pool-remaining", f"{fingerprint}=25", "--max-requests", "1",
                    "--execute"], now=NOW) == 0
    out = capsys.readouterr().out
    assert "verdict=run_ceiling" in out or "calls_spent=1" in out
    assert len(seen) <= 1


def test_pre_flight_count_equals_what_the_run_actually_pays(tmp_path, monkeypatch, capsys):
    """The number on the receipt must BE the number of calls, not a subset.

    A listing call unlocks H2H calls, so it also owes them to the pre-flight;
    under-counting there is how a bounded capture ends up spending 7 against a
    printed plan of 1.
    """
    localdata = _card(tmp_path)
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boggio.reset_state()
    # neither fixture has a retained id -> the listing is the only route, and it
    # must pre-pay for everything it unlocks
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(json.dumps({"schema": 1, "rows": []}))
    seen = []
    listing = {"data": [
        {"id": 424001, "home_team": "Real Sociedad", "away_team": "Barcelona", "status": "pending",
         "is_expired": False, "start_date": "2099-01-01T12:00:00"},
        {"id": 424002, "home_team": "Athletic Club", "away_team": "Getafe", "status": "pending",
         "is_expired": False, "start_date": "2099-01-01T14:00:00"},
        # an expired sample row must NEVER become a stats key (live-verified lesson)
        {"id": 424009, "home_team": "Sevilla", "away_team": "Valencia", "status": "expired",
         "is_expired": True, "start_date": "2020-01-01T12:00:00"}]}
    monkeypatch.setattr(boggio.urllib.request, "urlopen",
                        _fake_transport({"head-to-head": H2H_DOC, "predictions": listing}, seen))
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31",
                    "--pool-remaining", f"{boggio.key_label('pool-b')}=99",
                    "--execute"], now=NOW) == 0
    out = capsys.readouterr().out
    planned = int(out.split("ledger=card_enrich_preflight calls=")[1].split(" ")[0])
    spent = int(out.split("calls_spent=")[1].split(" ")[0])
    assert planned == 3 and spent == planned      # 1 listing + 2 unlocked h2h
    assert len(seen) == spent
    assert sum(1 for url in seen if "/head-to-head/" in url) == 2


def test_a_tight_budget_degrades_the_plan_and_never_overspends_it(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "2")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    boggio.reset_state()
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(json.dumps({"schema": 1, "rows": []}))
    seen = []
    listing = {"data": [{"id": 424001, "home_team": "Real Sociedad", "away_team": "Barcelona",
                         "status": "pending", "is_expired": False, "start_date": "2099-01-01T12:00:00"},
                        {"id": 424002, "home_team": "Athletic Club", "away_team": "Getafe",
                         "status": "pending", "is_expired": False, "start_date": "2099-01-01T14:00:00"}]}
    monkeypatch.setattr(boggio.urllib.request, "urlopen",
                        _fake_transport({"head-to-head": H2H_DOC, "predictions": listing}, seen))
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0
    out = capsys.readouterr().out
    assert "verdict=budget_degraded" in out
    planned = int(out.split("ledger=card_enrich_preflight calls=")[1].split(" ")[0])
    # affordable=2 of needed=3. The 2nd call would be an H2H, but the 1st is the
    # listing that makes any H2H possible - so the pair is (listing, one H2H).
    assert planned == 3 and "calls_spent=2" in out
    assert "decision=budget_stop" in out                # and it said so for the third
    assert len(seen) == 2
    # and one notch tighter (allowed=1) must spend NOTHING rather than buy an
    # unusable listing: no id, no snapshot, still charged.
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "1")
    seen.clear()
    capsys.readouterr()
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0
    assert seen == []
    assert "calls_spent=0" in capsys.readouterr().out


def test_failed_listing_consumes_its_preflight_unit_before_h2h_calls(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    card = [
        {"home": "Real Sociedad", "away": "Barcelona", "date": CARD_DAY,
         "kickoff_utc": "2026-10-11T14:00:00+00:00", "rule": "ml-meta avg_p>=55", "avg_p": 55.2},
        {"home": "Athletic Club", "away": "Getafe", "date": CARD_DAY,
         "kickoff_utc": "2026-10-11T16:30:00+00:00", "rule": "ml-meta avg_p>=65", "avg_p": 72.0},
        {"home": "Sevilla", "away": "Villarreal", "date": CARD_DAY,
         "kickoff_utc": "2026-10-11T18:00:00+00:00", "rule": "2way-unanimous avg_p>=60", "avg_p": 60.1},
    ]
    (localdata / "picks_today.json").write_text(json.dumps(card))
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(json.dumps({"schema": 1, "rows": [
        {"home": "Real Sociedad", "away": "Barcelona", "event_id": 424001},
        {"home": "Athletic Club", "away": "Getafe", "event_id": 424002},
    ]}))
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "2")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    boggio.reset_state()
    seen = []

    def fake_transport(req, timeout=None):
        seen.append(req.full_url)
        if "/predictions?" in req.full_url:
            raise OSError("offline listing failure fixture")
        return _Response(H2H_DOC, 30)

    monkeypatch.setattr(boggio.urllib.request, "urlopen", fake_transport)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0

    out = capsys.readouterr().out
    assert "ledger=card_enrich_preflight calls=4" in out
    assert "verdict=budget_degraded" in out and "calls_spent=2" in out
    assert len(seen) == 2 and "/predictions?" in seen[0]
    entries = boggio.read_call_ledger(localdata)
    assert len(entries) == 2 and entries[0]["endpoint"] == boggio.H2H_ENDPOINT + ":listing"
    assert entries[0]["error_class"] == "UpstreamBlocked" and entries[0]["charged"] is True
    assert entries[1]["endpoint"] == boggio.H2H_ENDPOINT and entries[1]["charged"] is True


def test_a_refusal_we_caused_ourselves_must_not_be_paid_for_twice(tmp_path, monkeypatch, capsys):
    """A local ring guard is not provider contact and must not burn quota."""
    localdata = _card(tmp_path)
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(
        json.dumps({"schema": 1, "rows": []}))
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    boggio.reset_state()
    transport_calls = []

    def local_block(_day):
        raise boggio.UpstreamBlocked("boggio: local guard; no request sent")

    def unexpected_transport(*args, **kwargs):
        transport_calls.append(args)
        raise AssertionError("a local block must not reach the transport")

    monkeypatch.setattr(boggio, "listing_call", local_block)
    monkeypatch.setattr(boggio.urllib.request, "urlopen", unexpected_transport)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0

    out = capsys.readouterr().out
    assert "verdict=lane_blocked_local calls_spent=0" in out
    assert "note=no request was sent; budget untouched" in out
    assert transport_calls == []
    assert boggio.read_call_ledger(localdata) == []
    assert (localdata / "card_enrich_call_ledger.jsonl").read_text() == ""


def test_contacted_listing_failure_spends_one_planned_unit(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(
        json.dumps({"schema": 1, "rows": []}))
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    boggio.reset_state()

    def contacted_rejection(_day):
        exc = boggio.UpstreamBlocked("boggio: HTTP 429")
        exc.ring_attempts = 1
        exc.ring_pool_index = 0
        exc.ring_key = "pool-a"
        raise exc

    monkeypatch.setattr(boggio, "listing_call", contacted_rejection)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0

    out = capsys.readouterr().out
    entries = boggio.read_call_ledger(localdata)
    assert "calls_spent=1" in out
    assert len(entries) == 1 and entries[0]["charged"] is True
    assert entries[0]["endpoint"] == boggio.H2H_ENDPOINT + ":listing"
    assert entries[0]["pool_index"] == 1


def test_local_h2h_block_does_not_spend_or_write_a_receipt(tmp_path, monkeypatch, capsys):
    localdata = _card(tmp_path)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    boggio.reset_state()
    transport_calls = []

    def local_block(_event_id):
        raise boggio.UpstreamBlocked("boggio: ring exhausted; run cooling down")

    def unexpected_transport(*args, **kwargs):
        transport_calls.append(args)
        raise AssertionError("a local H2H block must not reach the transport")

    monkeypatch.setattr(boggio, "h2h_call", local_block)
    monkeypatch.setattr(boggio.urllib.request, "urlopen", unexpected_transport)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0

    out = capsys.readouterr().out
    assert "calls_spent=0 verdict=lane_blocked_local" in out
    assert "decision=lane_blocked_local call_spent=0" in out
    # The pool preflight line is a plan diagnostic; the local-block receipt
    # itself must not claim any pool, key tail, or contacted-attempt count.
    refusal_receipt = "\n".join(line for line in out.splitlines()
                                 if "lane_blocked_local" in line)
    assert refusal_receipt
    assert all(field not in refusal_receipt for field in
               ("pool=", "pool_index=", "key=", "key_tail=", "attempts="))
    assert transport_calls == []
    assert boggio.read_call_ledger(localdata) == []


def test_first_run_auto_pays_for_one_listing_before_attempting_h2h(tmp_path, monkeypatch, capsys):
    """The offline plan credits a listing only when it can also buy H2H context."""
    localdata = _card(tmp_path)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boggio.reset_state()
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(json.dumps({"schema": 1, "rows": []}))
    seen = []
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setattr(boggio.urllib.request, "urlopen",
                        _fake_transport({"head-to-head": H2H_DOC}, seen))
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31", "--execute"], now=NOW) == 0
    out = capsys.readouterr().out
    assert "ledger=card_enrich_preflight calls=3" in out
    assert "need_listing=1" in out and "listing_used_today=0" in out
    assert "decision=unresolved_id" in out and "calls_spent=1" in out
    assert len(seen) == 1 and "/api/v2/predictions?" in seen[0]
    entries = boggio.read_call_ledger(localdata)
    assert len(entries) == 1
    assert entries[0]["endpoint"] == boggio.H2H_ENDPOINT + ":listing"
    assert entries[0]["charged"] is True


def test_a_card_whose_fixtures_have_kicked_off_is_refused_not_billed(tmp_path, monkeypatch, capsys):
    """7 calls for 0 usable rows was the recommended plan; it is now a refusal.

    The provider's stats endpoints are upcoming-fixture-only AND the lane's own
    pre-kickoff rule marks a late capture ineligible - so an evening run against
    a card whose matches already started pays full price for snapshots that can
    never be used. Plan mode warns; --execute declines.
    """
    localdata = _card(tmp_path)
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boggio.reset_state()
    seen = []
    monkeypatch.setattr(boggio.urllib.request, "urlopen",
                        _fake_transport({"head-to-head": H2H_DOC, "predictions": {
                            "data": [{"id": 424001, "home_team": "Real Sociedad", "away_team": "Barcelona",
                                      "status": "pending", "is_expired": False,
                                      "start_date": "2099-01-01T12:00:00"}]}}, seen))
    late = datetime(2026, 10, 11, 20, 0, tzinfo=timezone.utc)   # after the 14:00Z kickoffs
    # Empty the retained-id ledger: now the listing is the only route, i.e. the
    # exact "capture it today" shape (1 listing + 2 H2H) the guard must refuse.
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(json.dumps({"schema": 1, "rows": []}))
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31",
                    "--pool-remaining", f"{boggio.key_label('pool-b')}=99",
                    "--execute"], now=late) == 0
    out = capsys.readouterr().out
    assert "pre_kickoff_now=0/2" in out
    assert "ledger=card_enrich_caution" in out
    assert "would pay up to 3" in out          # the money the guard keeps in the pot
    assert "verdict=all_fixtures_post_kickoff" in out and "calls_spent=0" in out
    assert seen == [] and not (localdata / "card_enrich_call_ledger.jsonl").exists()
    # the same clock, with the refusal lifted, would have spent 3 - which is the
    # money this guard keeps in the pot
    plan = ce.plan_run(CARD_DAY, localdata=localdata, limit=6,
                       bootstrap={boggio.key_label("pool-a"): 31}, now=late)
    assert plan["preflight"]["need_total"] == 3 and plan["pre_kickoff"] == 0


def test_no_context_rule_is_registered_and_no_lane_is_wired_into_the_pick_path():
    """Tripwire for the 'silent capture, no noise' ruling: this lane must stay
    invisible to the pick path, and the vocabulary must stay dormant."""
    registry = (Path(__file__).resolve().parents[1] / "src" / "edgefactory" / "enh_registry.py").read_text()
    assert "h2h_dominance" not in registry and "card_enrich" not in registry
    picks = (Path(__file__).resolve().parents[1] / "scripts" / "picks_today.py").read_text()
    assert "card_enrich" not in picks
    assert "h2h_dominance" not in picks
    notifier = (Path(__file__).resolve().parents[1] / "src" / "edgefactory" / "notifier.py").read_text()
    assert "card_enrich" not in notifier


def _post_forebet_card():
    from edgefactory.consensus_contracts import contract_identity
    recipe = dict(sources=['scoutingstats'], market='1x2', strategy='single',
                  follow_source=None, threshold=65, status='certified',
                  mining_window=dict(start='2026-06-13', split='2026-09-01',
                                     as_of_exclusive='2026-10-01'),
                  activated_as_of='2026-10-01', contract_schema='post_forebet_v1')
    identity = contract_identity(recipe)
    recipe.update(contract_id=identity, rule=identity, view=identity, where='1=1')
    row = dict(home='Real Sociedad', away='Barcelona', date=CARD_DAY,
               market='1x2', avg_p=65.2, rule=identity, edge_rule=identity,
               sources_used=['scoutingstats'], contract_schema='post_forebet_v1',
               contract_id=identity, kickoff_utc='2026-10-11T15:00:00+00:00')
    return row, {'operating_contract': 'post_forebet_v1', 'edges': [recipe]}


def test_post_forebet_rank_uses_validated_recipe_not_the_opaque_label():
    row, registry = _post_forebet_card()
    chosen, _ = ce.select_candidates([row], limit=6, registry=registry)
    assert len(chosen) == 1 and chosen[0]['margin'] == .2
    assert ce.margin(dict(row, avg_p=64.9), registry=registry) == -.1
    # A second market on the same fixture must not purchase a second call.
    chosen, _ = ce.select_candidates([row, dict(row, avg_p=66.)], limit=6, registry=registry)
    assert len(chosen) == 1 and chosen[0]['margin'] == .2


@pytest.mark.parametrize('field,value', [
    ('contract_id', 'pfc_forged'), ('edge_rule', '3way-unanimous avg_p>=65'),
    ('market', 'ou_2.5'), ('sources_used', ['forebet']),
    ('contract_schema', None), ('date', '2026-09-30'),
    ('avg_p', None), ('avg_p', True), ('avg_p', float('nan')),
    ('avg_p', float('inf')), ('avg_p', 101.),
])
def test_post_forebet_enrichment_rejects_forged_or_unmeasured_rows(field, value):
    row, registry = _post_forebet_card()
    assert ce.margin(dict(row, **{field: value}), registry=registry) is None


@pytest.mark.parametrize('registry_problem', ['missing', 'benched', 'malformed', 'duplicate'])
def test_post_forebet_enrichment_registry_fail_closed(registry_problem):
    row, registry = _post_forebet_card()
    if registry_problem == 'missing':
        registry = None
    elif registry_problem == 'benched':
        registry['edges'][0]['status'] = 'benched'
    elif registry_problem == 'malformed':
        registry['edges'][0]['threshold'] = 64
    else:
        registry['edges'] *= 2
    assert ce.select_candidates([row], limit=6, registry=registry)[0] == []


def test_post_forebet_plan_loads_existing_registry_without_spending(tmp_path):
    row, registry = _post_forebet_card()
    (tmp_path / 'picks_today.json').write_text(json.dumps([row]))
    (tmp_path / 'edges_consensus.json').write_text(json.dumps(registry))
    plan = ce.plan_run(CARD_DAY, localdata=tmp_path, limit=6, bootstrap={})
    # No key / event mapping / budget manufactured by making the row rankable.
    assert plan['census'] and plan['census'][0]['margin'] == .2


def test_categorical_contract_cannot_rank_on_a_placeholder_zero():
    row, registry = _post_forebet_card()
    assert ce.margin(dict(row, avg_p=0., probability_available=False), registry=registry) is None
    registry.pop('operating_contract')
    assert ce.margin(row, registry=registry) is None
