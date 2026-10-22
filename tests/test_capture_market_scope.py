"""Market-scope upgrades use the existing planner/ledger, never quota bypasses."""
from datetime import datetime, timezone
from types import SimpleNamespace

from test_capture_plan_kickoff import capture, _team_names_match, _pick_kickoff_with_source

NOW = datetime(2026, 10, 23, 10, tzinfo=timezone.utc)
F = dict(home="Alpha", away="Beta", date="2026-10-23",
         kickoff_utc="2026-10-23T18:00:00Z")
ROW = dict(F, market="1x2", selection="home", odds=1.5)
KEY = "Alpha|Beta"


def plan(rows, attempts, fixture=None):
    return capture.plan_auto([fixture or F], rows, attempts, now=NOW,
                             kickoff_source_fn=_pick_kickoff_with_source,
                             match_fn=_team_names_match, requested_scope="expanded")


def test_legacy_priced_fixture_is_due_once_for_expanded_scope():
    attempts = {KEY: {"first_at": "2026-10-23T00:00:00Z"}}
    due, updates, _ = plan([ROW], attempts)
    assert due == [F] and updates == {KEY: "scope_at"}
    capture.record_attempts(due, updates, attempts, [ROW], _team_names_match,
                            "expanded", NOW.isoformat())
    # Only h2h returned: lack of team totals or BTTS must not rebuy every run.
    assert plan([ROW], attempts)[0] == []
    assert attempts[KEY]["capture_scope"] == "expanded"


def test_changed_scope_not_same_scope_requeues():
    assert plan([ROW], {KEY: {"capture_scope": "expanded"}})[0] == []
    assert plan([ROW], {KEY: {"capture_scope": "old"}})[0] == [F]


def test_scope_upgrade_respects_both_failure_cooldowns():
    for field in ("fail_at", "close_fail_at"):
        assert plan([ROW], {KEY: {field: NOW.isoformat()}})[0] == []


def test_scope_upgrade_respects_kickoff_guard():
    past = dict(F, kickoff_utc="2026-10-23T09:00:00Z")
    assert plan([], {}, past)[0] == []
    imminent = dict(F, kickoff_utc="2026-10-23T10:20:00Z")
    # Existing close window semantics are retained, not bypassed by scope.
    assert plan([], {}, imminent)[1] == {KEY: "close_at"}


def test_empty_or_partial_batch_does_not_stamp_unprocessed_success():
    other = dict(F, home="Gamma", away="Delta")
    attempts = {}
    capture.record_attempts([F, other], {KEY: "scope_at", "Gamma|Delta": "first_at"},
                            attempts, [ROW], _team_names_match, "expanded", NOW.isoformat())
    assert attempts[KEY]["capture_scope"] == "expanded"
    assert attempts["Gamma|Delta"] == {"fail_at": NOW.isoformat()}
    empty = {}
    capture.record_attempts([F], {KEY: "first_at"}, empty, [], _team_names_match,
                            "expanded", NOW.isoformat())
    assert "first_at" not in empty[KEY]
    assert plan([], empty)[0] == []


def test_other_date_rows_do_not_prove_success():
    attempts = {}
    capture.record_attempts([F], {KEY: "scope_at"}, attempts,
                            [dict(ROW, date="2026-10-22")], _team_names_match,
                            "expanded", NOW.isoformat())
    assert "capture_scope" not in attempts[KEY]


def test_scope_covers_btts_team_markets_points_regions_and_books():
    base = dict(MARKETS=("h2h", "btts", "alternate_team_totals"), REGIONS=("eu",),
                TOTAL_POINTS=("0.5", "1.5"), BOOKMAKERS=())
    scope = capture.capture_scope(SimpleNamespace(**base))
    assert scope == capture.capture_scope(SimpleNamespace(**dict(base, MARKETS=tuple(reversed(base["MARKETS"])))))
    for field, value in (("MARKETS", ("h2h",)), ("REGIONS", ("uk",)),
                         ("TOTAL_POINTS", ("2.5",)), ("BOOKMAKERS", ("test",))):
        assert scope != capture.capture_scope(SimpleNamespace(**dict(base, **{field: value})))


def test_live_entrypoint_persists_scope_and_stops_rebuying(tmp_path, monkeypatch):
    from edgefactory.sources import theoddsapi as mod
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(mod, "shortlist", lambda day: [F])
    monkeypatch.setattr(mod, "enabled", lambda: True)
    monkeypatch.setattr(mod, "ledger_status", lambda: dict(credits_local=7, budget=480,
                                                          n_keys=1, server_remaining=473))
    monkeypatch.setattr(capture.sys, "argv", ["capture_theodds.py", "--auto", "--date", F["date"]])
    original_plan = capture.plan_auto
    monkeypatch.setattr(capture, "plan_auto", lambda *a, **kw: original_plan(*a, **kw, now=NOW))
    capture._save_attempts(F["date"], {KEY: {"first_at": "2026-10-23T00:00:00Z"}})
    calls = []
    def fetch(fixtures, **kw):
        calls.append(fixtures)
        return [ROW], [], 1
    monkeypatch.setattr(mod, "fetch_fixtures", fetch)
    assert capture.main() == 0
    assert capture.main() == 0
    assert calls == [[F]]
    attempts = capture._load_attempts(F["date"])
    assert attempts[KEY]["capture_scope"] == capture.capture_scope(mod)
    receipt = __import__("json").loads(capture._receipt_path(F["date"]).read_text())
    assert receipt["status"] == "not_due"
    assert "btts" in receipt["requested_markets"]
    assert "alternate_team_totals" in receipt["requested_markets"]


def test_aborted_live_fetch_records_failure_not_success(tmp_path, monkeypatch):
    from edgefactory.sources import theoddsapi as mod
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(mod, "shortlist", lambda day: [F])
    monkeypatch.setattr(mod, "enabled", lambda: True)
    monkeypatch.setattr(capture.sys, "argv", ["capture_theodds.py", "--auto", "--date", F["date"]])
    original_plan = capture.plan_auto
    monkeypatch.setattr(capture, "plan_auto", lambda *a, **kw: original_plan(*a, **kw, now=NOW))
    def fail(*a, **kw):
        raise RuntimeError("offline test abort")
    monkeypatch.setattr(mod, "fetch_fixtures", fail)
    assert capture.main() == 1
    rec = capture._load_attempts(F["date"])[KEY]
    assert "fail_at" in rec and "first_at" not in rec and "capture_scope" not in rec
