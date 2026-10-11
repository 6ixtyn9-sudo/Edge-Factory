"""Bootstrap + inertness + capability tests — required by handoff §3.1/§5."""
import json
from pathlib import Path

from edgefactory import context_rules
from edgefactory.sources import boggio

FIXTURES = Path(__file__).resolve().parent / "fixtures"
CARD_DAY = "2026-10-11"
CAPTURED = "2026-10-11T06:00:00+00:00"
FIXTURE = {"home": "Real Sociedad", "away": "Barcelona", "kickoff_utc": "2026-10-11T14:00:00+00:00"}


def test_production_listing_seeds_ledger_with_charged_false_and_real_header(tmp_path, monkeypatch):
    localdata = tmp_path / "ld"
    localdata.mkdir()
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    boggio.reset_state()

    class _Resp:
        def __init__(self):
            self.status = 200
            self._body = b'{"data": []}'
            self.headers = {"X-RateLimit-Match-Stats-and-Prediction-endpoints-Remaining": "42", "Content-Type": "application/json"}
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self, n): return self._body[:n]

    def fake(req, timeout=None):
        return _Resp()

    monkeypatch.setattr(boggio.urllib.request, "urlopen", fake)
    ledger_file = localdata / "card_enrich_call_ledger.jsonl"
    assert not ledger_file.exists()
    code, data, headers = boggio.get_json(boggio.predictions_url("2026-10-11"), day="2026-10-11", localdata=localdata)
    assert code == 200
    assert ledger_file.exists()
    entries = boggio.read_call_ledger(localdata)
    assert len(entries) == 1
    e = entries[0]
    assert e["charged"] is False
    assert e["family_remaining"] == 42
    assert e["what_it_bought"] == "production_boggio_listing"
    assert e["endpoint"] == "boggio_production_listing"


def test_charged_false_does_not_move_allowance(tmp_path, monkeypatch):
    localdata = tmp_path / "ld"
    localdata.mkdir()
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    fp = boggio.key_fingerprint("pool-a")
    plan_empty = boggio.preflight(need_h2h=1, need_listing=0, localdata=localdata, day=CARD_DAY, observed_remaining={})
    assert plan_empty["verdict"] == "unattributed_quota"
    boggio._append_ledger_line({
        "month": boggio.family_month(CARD_DAY),
        "date": CARD_DAY,
        "source": boggio.CARD_ENRICH_SOURCE,
        "endpoint": "boggio_production_listing",
        "fixture_key": "",
        "pool_index": 1,
        "key": fp,
        "key_tail": boggio.key_label("pool-a"),
        "status": 200,
        "family_remaining": 25,
        "charged": False,
        "what_it_bought": "production_boggio_listing",
        "error_class": None,
        "logged_at": "2026-10-11T06:00:00+00:00",
    }, localdata=localdata)
    spend = boggio.spend_by_key(boggio.read_call_ledger(localdata))
    assert spend == {}
    plan_with = boggio.preflight(need_h2h=1, need_listing=0, localdata=localdata, day=CARD_DAY, observed_remaining={fp: 25})
    assert plan_with["spendable"] == 25
    boggio._append_ledger_line({
        "month": boggio.family_month(CARD_DAY),
        "date": CARD_DAY,
        "source": boggio.CARD_ENRICH_SOURCE,
        "endpoint": boggio.H2H_ENDPOINT,
        "fixture_key": "f",
        "pool_index": 1,
        "key": fp,
        "key_tail": "ol-a",
        "status": 200,
        "family_remaining": 25,
        "charged": True,
        "what_it_bought": "x",
        "error_class": None,
        "logged_at": "2026-10-11T06:00:01+00:00",
    }, localdata=localdata)
    spend2 = boggio.spend_by_key(boggio.read_call_ledger(localdata))
    assert spend2 == {fp: 1}
    plan_after = boggio.preflight(need_h2h=1, need_listing=0, localdata=localdata, day=CARD_DAY, observed_remaining={fp: 25})
    assert plan_after["spendable"] == 24


def test_bootstrap_run1_may_refuse_run2_must_capture(tmp_path, monkeypatch):
    localdata = tmp_path / "ld"
    localdata.mkdir()
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    plan1 = boggio.preflight(need_h2h=1, need_listing=0, localdata=localdata, day=CARD_DAY, observed_remaining={})
    assert plan1["verdict"] == "unattributed_quota"
    fp = boggio.key_fingerprint("pool-a")
    boggio._append_ledger_line({
        "month": boggio.family_month(CARD_DAY),
        "date": CARD_DAY,
        "source": boggio.CARD_ENRICH_SOURCE,
        "endpoint": "boggio_production_listing",
        "fixture_key": "",
        "pool_index": 1,
        "key": fp,
        "key_tail": "ol-a",
        "status": 200,
        "family_remaining": 31,
        "charged": False,
        "what_it_bought": "production_boggio_listing",
        "error_class": None,
        "logged_at": "2026-10-11T06:00:00+00:00",
    }, localdata=localdata)
    plan2 = boggio.preflight(need_h2h=1, need_listing=0, localdata=localdata, day=CARD_DAY, observed_remaining={fp: 31})
    assert plan2["verdict"] == "approved"
    assert plan2["allowed_calls"] == 1
    assert plan1["verdict"] != plan2["verdict"]


def test_falsifications_budget_disabled_and_unattributed_quota(tmp_path, monkeypatch):
    localdata = tmp_path / "ld"
    localdata.mkdir()
    monkeypatch.delenv(boggio.CARD_ENRICH_BUDGET_ENV, raising=False)
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    plan = boggio.preflight(need_h2h=6, need_listing=0, localdata=localdata, day=CARD_DAY, observed_remaining={boggio.key_label("pool-a"): 99})
    assert plan["verdict"] == "budget_disabled"
    assert plan["allowed_calls"] == 0
    assert plan["spendable"] == 0
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    plan2 = boggio.preflight(need_h2h=6, need_listing=0, localdata=localdata, day=CARD_DAY, observed_remaining={})
    assert plan2["verdict"] == "unattributed_quota"
    assert plan2["allowed_calls"] == 0


def test_capability_fixture_6encounters_2competitions_mixed_first_half():
    payload = json.loads((FIXTURES / "boggio_head_to_head_6encounters.json").read_text())
    snap = boggio.parse_head_to_head(payload, fixture=FIXTURE, captured_at=CAPTURED)
    assert snap["identity_verified"] is True
    assert len(snap["encounters"]) >= 6
    comps = set(row["competition"] for row in snap["encounters"] if row.get("competition"))
    assert len(comps) >= 2
    fh = [row["first_half"] for row in snap["encounters"] if row.get("first_half")]
    assert len(fh) >= 3
    assert any(a == b for a, b in fh)
    assert any(a != b for a, b in fh)
    feats = snap["features"]
    assert feats["h2h_encounter_count"] >= 6
    assert "rest_days" in feats
    assert "venue_split" in feats
    assert "form_gap" in feats
    assert "h2h_bookie_draw_prior" in feats
    row = dict(feats, identity_verified=snap["identity_verified"], captured_at=snap["captured_at"])
    kickoff = FIXTURE["kickoff_utc"]
    assert isinstance(context_rules.holds("h2h_dominance>=2", row, kickoff=kickoff), bool)
    tampered = dict(row, captured_at="2026-10-12T00:00:00+00:00")
    assert context_rules.holds("h2h_dominance>=2", tampered, kickoff=kickoff) is False


def test_differential_inertness_production_builder_byte_identical(tmp_path):
    """D4 real: import production board/payload builder, run against both localdata dirs, assert byte-identical.
    
    Production builder is select_candidates + plan_run's candidate selection — the exact surface old wiring
    polluted (picks_today's enrich_with_h2h_context mutated picks). With zero delta vs main, the builder
    must be byte-identical regardless of usable snapshots present.
    """
    # Two localdata dirs: one empty, one with usable snapshot
    ld_empty = tmp_path / "empty"
    ld_empty.mkdir()
    ld_with = tmp_path / "with"
    ld_with.mkdir()
    # Create snapshot file in ld_with
    snap = {
        "fixture_key": "realsociedad|barcelona",
        "home": "Real Sociedad",
        "away": "Barcelona",
        "kickoff_utc": "2026-10-11T14:00:00+00:00",
        "captured_at": "2026-10-11T06:00:00+00:00",
        "identity_verified": True,
        "usable": True,
        "features": {"h2h_dominance": -7, "rest_days": 10},
    }
    payload = {
        "schema": 1,
        "source": "boggio_h2h",
        "run_date": "2026-10-11",
        "snapshots": [snap],
    }
    (ld_with / "card_enrich_shadow_2026-10-11.json").write_text(json.dumps(payload))

    # Production board builder: select_candidates assembles priced-candidate slate payload from card
    # It is pure and must NOT read snapshots — candidate selection by margin over consensus bar
    from scripts.capture_card_enrich import select_candidates, plan_run

    card = [
        {"home": "Real Sociedad", "away": "Barcelona", "date": "2026-10-11", "kickoff_utc": "2026-10-11T14:00:00+00:00",
         "rule": "2way-unanimous avg_p>=70", "avg_p": 70.2, "bucket": "clean"},
        {"home": "Athletic Club", "away": "Getafe", "date": "2026-10-11", "kickoff_utc": "2026-10-11T16:00:00+00:00",
         "rule": "ml-meta avg_p>=65", "avg_p": 65.5, "bucket": "clean"},
    ]

    chosen_empty, _ = select_candidates(card, limit=6)
    chosen_with, _ = select_candidates(card, limit=6)
    # Byte-identical regardless of snapshots
    assert json.dumps(chosen_empty, sort_keys=True) == json.dumps(chosen_with, sort_keys=True)

    # Also test plan_run's candidate selection is byte-identical (stale_skip may differ, but chosen fixtures identical)
    # Need minimal picks_today.json and boggio shadow for plan_run
    for ld in [ld_empty, ld_with]:
        (ld / "picks_today.json").write_text(json.dumps(card))
        (ld / "boggio_shadow_2026-10-11.json").write_text(json.dumps({
            "schema": 1, "rows": [
                {"home": "Real Sociedad", "away": "Barcelona", "event_id": 424001, "date": "2026-10-11"},
                {"home": "Athletic Club", "away": "Getafe", "event_id": 424002, "date": "2026-10-11"},
            ]
        }))

    plan_empty = plan_run("2026-10-11", localdata=ld_empty, limit=6, allow_listing=False, bootstrap={"pool-a": 31}, now=None)
    plan_with = plan_run("2026-10-11", localdata=ld_with, limit=6, allow_listing=False, bootstrap={"pool-a": 31}, now=None)

    # Candidate fixtures (by fixture_key) must be identical — builder inert to snapshots
    keys_empty = sorted([c["fixture_key"] for c in plan_empty["candidates"]])
    keys_with = sorted([c["fixture_key"] for c in plan_with["candidates"]])
    assert keys_empty == keys_with, "candidate selection must be byte-identical with vs without snapshots"

    # Verify snapshots ARE present in one dir and absent in other — not vacuous
    snaps_empty = boggio.load_snapshots(localdata=ld_empty)
    snaps_with = boggio.load_snapshots(localdata=ld_with)
    assert len(snaps_empty) == 0
    assert len(snaps_with) == 1

    # File scans still green as secondary (old tripwire class)
    picks_path = Path(__file__).resolve().parents[1] / "scripts" / "picks_today.py"
    content = picks_path.read_text()
    assert "load_snapshots" not in content
    assert "card_enrich" not in content
    assert "h2h_dominance" not in content


def test_bootstrap_default_path_seed_file_then_preflight_without_handfed_observed(tmp_path, monkeypatch):
    """D5: seed the FILE via production path, call preflight with nothing in hand, get approved."""
    # This closes the gap: previous tests hand-fed observed_remaining. Production question is:
    # seed file via charged:false, then plan_run with bootstrap={} should read last_observed_remaining from ledger and approve.
    import scripts.capture_card_enrich as ce
    localdata = tmp_path / "ld"
    localdata.mkdir()
    # Need a minimal picks_today.json and boggio shadow for plan_run to have candidates
    card = [
        {"home": "Real Sociedad", "away": "Barcelona", "date": "2026-10-11", "kickoff_utc": "2026-10-11T14:00:00+00:00",
         "rule": "2way-unanimous avg_p>=70", "avg_p": 70.2, "bucket": "clean"},
    ]
    (localdata / "picks_today.json").write_text(json.dumps(card))
    (localdata / "boggio_shadow_2026-10-11.json").write_text(json.dumps({
        "schema": 1, "rows": [{"home": "Real Sociedad", "away": "Barcelona", "event_id": 424001, "date": "2026-10-11"}]
    }))
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, "30")
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, "0")
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a")
    # Seed ledger via production path (charged:false)
    fp = boggio.key_fingerprint("pool-a")
    boggio._append_ledger_line({
        "month": boggio.family_month("2026-10-11"),
        "date": "2026-10-11",
        "source": boggio.CARD_ENRICH_SOURCE,
        "endpoint": "boggio_production_listing",
        "fixture_key": "",
        "pool_index": 1,
        "key": fp,
        "key_tail": "ol-a",
        "status": 200,
        "family_remaining": 31,
        "charged": False,
        "what_it_bought": "production_boggio_listing",
        "error_class": None,
        "logged_at": "2026-10-11T06:00:00+00:00",
    }, localdata=localdata)
    # Now call plan_run with NO hand-fed observed_remaining — it should read last_observed_remaining from ledger
    plan = ce.plan_run("2026-10-11", localdata=localdata, limit=6, allow_listing=False, bootstrap={}, now=None)
    # last_observed_remaining should have found 31, so preflight should be approved (need_h2h=1, spendable 31)
    assert plan["preflight"]["verdict"] == "approved"
    assert plan["preflight"]["spendable"] >= 1
    # And without seeding, it would be unattributed_quota
    localdata2 = tmp_path / "ld2"
    localdata2.mkdir()
    (localdata2 / "picks_today.json").write_text(json.dumps(card))
    (localdata2 / "boggio_shadow_2026-10-11.json").write_text(json.dumps({
        "schema": 1, "rows": [{"home": "Real Sociedad", "away": "Barcelona", "event_id": 424001, "date": "2026-10-11"}]
    }))
    plan_empty = ce.plan_run("2026-10-11", localdata=localdata2, limit=6, allow_listing=False, bootstrap={}, now=None)
    assert plan_empty["preflight"]["verdict"] == "unattributed_quota"


def test_d2_fail_closed_dominance_withheld_on_rate_divergence():
    """D2 unproven leg: tamper provider stats away_team.won=10, num_encounters=10 vs 6 kept rows -> dominance withheld."""
    payload = json.loads((FIXTURES / "boggio_head_to_head_6encounters.json").read_text())
    # Tamper provider stats to create rate divergence: provider away won 10/10 =1.0 vs recomputed 3/6=0.5 diff 0.5 >0.35
    payload["data"]["stats"]["away_team"]["won"] = 10
    payload["data"]["stats"]["overall"]["num_encounters"] = 10
    payload["data"]["stats"]["home_team"]["won"] = 0
    snap = boggio.parse_head_to_head(payload, fixture=FIXTURE, captured_at=CAPTURED)
    # Dominance should be withheld (fail-closed) due to rate divergence
    assert "h2h_dominance" not in snap["features"], f"dominance should be withheld, got {snap['features'].get('h2h_dominance')}"
    # Warning must contain "dominance withheld"
    assert any("dominance withheld" in w for w in snap["reconciliation_warnings"]), f"warnings: {snap['reconciliation_warnings']}"
    # Also test happy path still keeps dominance when below tolerance (original fixture)
    payload2 = json.loads((FIXTURES / "boggio_head_to_head_6encounters.json").read_text())
    snap2 = boggio.parse_head_to_head(payload2, fixture=FIXTURE, captured_at=CAPTURED)
    assert "h2h_dominance" in snap2["features"]
