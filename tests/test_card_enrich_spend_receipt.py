"""card_enrich spend receipt: what a charged run bought must survive the log.

The 2026-10-12 first live run paid one listing, resolved neither of the fixtures
it was bought for, and left that fact only in stdout. These tests pin the
durable form of it: the whitelisted ``card_enrich_shadow_<day>.json`` receipt
carries the run's own census (counts and reasons, never a payload or a secret),
and the plan records the facts that decision rested on.

Offline only, and every fixture is the lane's own documented shape
(``tests/fixtures/``).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from edgefactory.sources import boggio
import scripts.capture_card_enrich as ce

FIXTURES = Path(__file__).resolve().parent / "fixtures"
CARD_DAY = "2026-10-11"
NOW = datetime(2026, 10, 11, 4, 0, tzinfo=timezone.utc)   # pinned, pre-kickoff


def _card(localdata):
    localdata.mkdir(parents=True, exist_ok=True)
    (localdata / "picks_today.json").write_text(
        (FIXTURES / "card_enrich_slate_2026-10-11.json").read_text(encoding="utf-8"))
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(
        (FIXTURES / "boggio_shadow_2026-10-11.json").read_text(encoding="utf-8"))
    return localdata


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


def _budget(monkeypatch, *, cap="30", reserve="0"):
    monkeypatch.setattr(boggio, "MIN_INTERVAL_S", 0)
    monkeypatch.setenv(boggio.CARD_ENRICH_BUDGET_ENV, cap)
    monkeypatch.setenv(boggio.CARD_ENRICH_RESERVE_ENV, reserve)
    monkeypatch.setenv("RAPIDAPI_KEYS", "pool-a,pool-b")
    boggio.reset_state()


def _receipt(localdata):
    return json.loads((localdata / f"card_enrich_shadow_{CARD_DAY}.json").read_text(encoding="utf-8"))


def test_plan_records_the_retained_id_facts_its_decision_rested_on(tmp_path, monkeypatch):
    localdata = _card(tmp_path)
    _budget(monkeypatch)
    boot = {boggio.key_label("pool-a"): 31, boggio.key_label("pool-b"): 99}
    plan = ce.plan_run(CARD_DAY, localdata=localdata, limit=6, bootstrap=boot, now=NOW)
    # the fixture shadow carries three id-bearing rows; they resolve both ranked
    # fixtures for free, so no listing is planned and no vendor call is owed
    assert plan["shadow_file_present"] is True
    assert plan["retained_pairs"] == 3
    assert plan["free_listing_recorded_today"] is False
    assert plan["unresolved"] == [] and plan["need_listing"] == 0


def test_a_charged_zero_yield_run_records_its_census_in_the_receipt(tmp_path, monkeypatch, capsys):
    """The 2026-10-12 shape: the listing is paid, nothing resolves, and the
    receipt - not just the log - has to say so."""
    localdata = _card(tmp_path)
    _budget(monkeypatch)
    # No retained ids at all: both ranked fixtures need the listing, which then
    # resolves none of them (one pending row for a different fixture).
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(
        json.dumps({"schema": 1, "rows": []}), encoding="utf-8")
    listing = {"data": [{"id": 424009, "home_team": "Sevilla", "away_team": "Valencia",
                         "status": "pending", "is_expired": False,
                         "start_date": "2099-01-01T12:00:00"}]}
    seen = []
    monkeypatch.setattr(boggio.urllib.request, "urlopen",
                        _fake_transport({"predictions": listing}, seen))
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31",
                    "--pool-remaining", f"{boggio.key_label('pool-b')}=99",
                    "--execute"], now=NOW) == 0
    out = capsys.readouterr().out
    assert "mode=execute calls_spent=1 usable_snapshots=0" in out

    payload = _receipt(localdata)
    assert payload["stats"] == {"snapshots": 0, "usable": 0}
    outcome = payload["outcome"]
    assert outcome["calls_charged"] == 1 and outcome["usable_snapshots"] == 0
    assert outcome["retained_pairs"] == 0
    assert outcome["shadow_file_present"] is True          # the file exists; it holds no ids
    assert outcome["free_listing_recorded_today"] is False
    # the paid listing did resolve one pending row - just not ours
    assert outcome["listing"]["charged"] is True
    assert outcome["listing"]["resolved_pairs"] == 1
    assert outcome["listing"]["outcome"] == "charged"
    assert outcome["decisions"]["unresolved_id"] == 2
    assert outcome["decisions"]["captured"] == 0
    # the mismatch is named, bounded, and never a payload: no retained row shares
    # a team key with either loser, and neither does the listing row that was bought
    assert [row["retained_pairs_sharing_a_key"] for row in outcome["unresolved"]] == [0, 0]
    assert [row["listing_pairs_sharing_a_key"] for row in outcome["unresolved"]] == [0, 0]
    assert all(row["nearest_retained"] == [] for row in outcome["unresolved"])
    # ...and the ledger, which is the budget, agrees: one charged call, the listing
    ledger = [json.loads(line) for line in
              (localdata / "card_enrich_call_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(e["endpoint"], e["charged"]) for e in ledger] == [(boggio.H2H_ENDPOINT + ":listing", True)]
    assert "pool-a" not in json.dumps(payload) and "pool-a" not in json.dumps(ledger)


def test_a_free_production_listing_suppresses_the_paid_rebuy(tmp_path, monkeypatch, capsys):
    """The 2026-10-12 spend: the production lane had already bought this exact
    listing payload once today. Re-buying it cannot resolve the fixtures and
    costs a unit, so the lane refuses - by name, in the log and in the receipt."""
    localdata = _card(tmp_path)
    _budget(monkeypatch)
    # day rows exist but hold none of the ranked pairs
    (localdata / f"boggio_shadow_{CARD_DAY}.json").write_text(
        json.dumps({"schema": 1, "rows": [{"source": "boggio", "event_id": 999,
                                           "home": "Sevilla", "away": "Valencia"}]}),
        encoding="utf-8")
    entries = []
    boggio.record_call(entries, day=CARD_DAY, fixture_key="", endpoint="boggio_production_listing",
                       pool_index=0, key="pool-a", status=200, remaining=25, spent=False,
                       what_bought="production_boggio_listing")
    boggio.write_call_ledger(entries, localdata)

    def explode(req, timeout=None):
        raise AssertionError("the paid listing must not be re-bought")

    monkeypatch.setattr(boggio.urllib.request, "urlopen", explode)
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31",
                    "--pool-remaining", f"{boggio.key_label('pool-b')}=99",
                    "--execute"], now=NOW) == 0
    out = capsys.readouterr().out
    assert "decision=free_listing_present_zero_matches" in out
    assert "verdict=suppressed reason=free_listing_present_zero_matches" in out
    assert "verdict=nothing_to_capture" in out

    outcome = _receipt(localdata)["outcome"]
    assert outcome["calls_charged"] == 0 and outcome["usable_snapshots"] == 0
    assert outcome["free_listing_recorded_today"] is True
    assert outcome["shadow_file_present"] is True and outcome["retained_pairs"] == 1
    assert outcome["listing"]["charged"] is False
    assert outcome["listing"]["reason"] == "free_listing_present_zero_matches"
    assert outcome["decisions"]["unresolved_id"] == 2
    # the ledger is unchanged: its only entry is the production lane's free one
    ledger = [json.loads(line) for line in
              (localdata / "card_enrich_call_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [(e["endpoint"], e["charged"]) for e in ledger] == [("boggio_production_listing", False)]


def test_a_missing_day_shadow_keeps_the_paid_listing_with_a_named_reason(tmp_path, monkeypatch):
    """Cache eviction is the one case where paying is honest: no day rows exist
    to resolve from - and the receipt says exactly that."""
    localdata = _card(tmp_path)
    _budget(monkeypatch)
    (localdata / f"boggio_shadow_{CARD_DAY}.json").unlink()
    entries = []
    boggio.record_call(entries, day=CARD_DAY, fixture_key="", endpoint="boggio_production_listing",
                       pool_index=0, key="pool-a", status=200, remaining=25, spent=False,
                       what_bought="production_boggio_listing")
    boggio.write_call_ledger(entries, localdata)
    h2h_doc = json.loads((FIXTURES / "boggio_head_to_head_documented.json").read_text(encoding="utf-8"))
    listing = {"data": [
        {"id": 424001, "home_team": "Real Sociedad", "away_team": "Barcelona", "status": "pending",
         "is_expired": False, "start_date": "2099-01-01T12:00:00"},
        {"id": 424002, "home_team": "Athletic Club", "away_team": "Getafe", "status": "pending",
         "is_expired": False, "start_date": "2099-01-01T14:00:00"}]}
    seen = []
    monkeypatch.setattr(boggio.urllib.request, "urlopen", _fake_transport(
        {"424001": h2h_doc, "424002": h2h_doc, "predictions": listing}, seen))
    assert ce.main(["--date", CARD_DAY, "--localdata", str(localdata),
                    "--pool-remaining", f"{boggio.key_label('pool-a')}=31",
                    "--pool-remaining", f"{boggio.key_label('pool-b')}=99",
                    "--execute"], now=NOW) == 0
    outcome = _receipt(localdata)["outcome"]
    assert outcome["shadow_file_present"] is False
    assert outcome["listing"]["charged"] is True
    assert outcome["listing"]["resolved_pairs"] == 2
    assert outcome["listing"]["reason"] == "shadow_file_absent"
    assert outcome["decisions"]["captured"] == 2
