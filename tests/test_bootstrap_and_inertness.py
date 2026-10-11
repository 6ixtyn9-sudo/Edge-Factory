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


def test_differential_inertness_payload_builder_byte_identical():
    picks_path = Path(__file__).resolve().parents[1] / "scripts" / "picks_today.py"
    content = picks_path.read_text()
    assert "load_snapshots" not in content
    assert "card_enrich" not in content
    assert "h2h_dominance" not in content
    auto_path = Path(__file__).resolve().parents[1] / "scripts" / "auto_tickets.py"
    auto_content = auto_path.read_text()
    # Ensure no H2H wiring remains (zero delta vs main)
    assert "h2h_features" not in auto_content
    assert "DORMANT_H2H" not in auto_content
    registry = (Path(__file__).resolve().parents[1] / "src" / "edgefactory" / "enh_registry.py").read_text()
    assert "h2h_dominance" not in registry
