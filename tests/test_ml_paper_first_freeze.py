"""First-run freeze parity with Main/ENH; synthetic local inputs, no live runs."""

import json
from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from test_ml_paper import DAY, FREEZE, NOW, context, pick, run_capture

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp


def current_context(when, rows=None):
    rows = [pick(1), pick(2)] if rows is None else rows
    for row in rows:
        row.update(as_of=when.isoformat(),
                   kickoff_utc=(when + timedelta(hours=3)).isoformat())
    return dict(context(rows), build_at=when.isoformat())


@pytest.mark.parametrize("delay", [0, 1, 15, 60, 180])
@pytest.mark.parametrize("prior_draft", ["none", "empty", "different"])
def test_first_run_after_nine_selects_current_inputs_at_actual_time(tmp_path, delay, prior_draft):
    pending = None
    if prior_draft != "none":
        run_capture(tmp_path, context([] if prior_draft == "empty" else [pick(8), pick(9)]))
        pending = mp.state_path(tmp_path).read_bytes()
    decision = FREEZE + timedelta(minutes=delay)
    ctx = current_context(decision)
    # A quote learned after 09:00 is eligible for a truthful later decision,
    # not for an already-frozen card or a claimed 09:00 decision.
    for row in ctx["slate"]:
        row["odds_captured_at"] = (decision - timedelta(seconds=1)).isoformat()
    frozen = run_capture(tmp_path, ctx, now=decision)
    assert frozen["status"] == "paper_accas" and frozen["accas"]
    assert frozen["captured_at"] == frozen["persisted_at"] == frozen["frozen_at"] == decision.isoformat()
    assert frozen["freeze_at"] == DAY + "T09:00:00+02:00"  # scheduled threshold, not backdating
    assert frozen["freeze_basis"] == mp.ACTUAL_RUN_FREEZE
    assert "draft_sha256" not in frozen and "draft_persisted_at" not in frozen
    assert {c["home"] for c in frozen["candidates"]} == {"Home Club 1", "Home Club 2"}
    assert all(c["price_age_seconds_at_freeze"] == 1 for c in frozen["candidates"])
    assert mp.receipts(tmp_path) == [frozen]
    assert decision.isoformat() in mp.render_card(frozen)
    if pending is not None:
        assert mp.state_path(tmp_path).read_bytes() == pending
    else:
        assert not mp.state_path(tmp_path).exists()  # no fake draft manufactured
    before = mp.receipt_path(tmp_path, DAY).read_bytes()
    assert run_capture(tmp_path, current_context(decision + timedelta(minutes=1)),
                       now=decision + timedelta(minutes=1)) is None
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == before


@pytest.mark.parametrize("source,limit", [("theoddsapi", 12), ("oddspapi", 6), ("oddspapi_odds", 6)])
@pytest.mark.parametrize("extra_seconds,allowed", [(0, True), (1, False)])
def test_post_nine_quote_age_is_measured_at_actual_decision_not_scheduled_nine(
    tmp_path, source, limit, extra_seconds, allowed
):
    decision = FREEZE + timedelta(hours=1)
    ctx = current_context(decision)
    for row in ctx["slate"]:
        row.update(odds_source=source,
                   odds_captured_at=(decision - timedelta(hours=limit, seconds=extra_seconds)).isoformat())
    frozen = run_capture(tmp_path, ctx, now=decision)
    assert bool(frozen["candidates"]) is allowed
    assert bool(frozen["accas"]) is allowed
    assert frozen["status"] == ("paper_accas" if allowed else "no_paper_bet")


@pytest.mark.parametrize("lead,allowed", [(-1, False), (0, False), (29, False), (30, True)])
def test_post_nine_kickoff_lead_is_relative_to_actual_decision(tmp_path, lead, allowed):
    decision = FREEZE + timedelta(hours=1)
    ctx = current_context(decision)
    for row in ctx["slate"]:
        row["kickoff_utc"] = (decision + timedelta(minutes=lead)).isoformat()
    frozen = run_capture(tmp_path, ctx, now=decision)
    assert bool(frozen["accas"]) is allowed


@pytest.mark.parametrize("field", ["as_of", "built_at_utc", "odds_captured_at"])
def test_post_nine_future_information_is_still_rejected(tmp_path, field):
    decision = FREEZE + timedelta(minutes=15)
    ctx = current_context(decision)
    for row in ctx["slate"]:
        row[field] = (decision + timedelta(seconds=1)).isoformat()
    frozen = run_capture(tmp_path, ctx, now=decision)
    assert not frozen["candidates"] and not frozen["accas"]


@pytest.mark.parametrize("damage", ["future_capture", "wrong_frozen_at", "fake_draft", "wrong_day", "unknown_basis"])
def test_actual_run_receipt_validation_rejects_rehashed_false_timing(tmp_path, damage):
    decision = FREEZE + timedelta(minutes=10)
    row = deepcopy(run_capture(tmp_path, current_context(decision), now=decision))
    if damage == "future_capture":
        row["captured_at"] = (decision + timedelta(seconds=1)).isoformat()
    elif damage == "wrong_frozen_at":
        row["frozen_at"] = FREEZE.isoformat()
    elif damage == "fake_draft":
        row["draft_persisted_at"] = NOW.isoformat()
        row["draft_sha256"] = "0" * 64
    elif damage == "wrong_day":
        row["persisted_at"] = row["frozen_at"] = (decision + timedelta(days=1)).isoformat()
    else:
        row["freeze_basis"] = "unknown"
    row["sha256"] = mp.digest({k: v for k, v in row.items() if k != "sha256"})
    with pytest.raises(ValueError):
        mp.validate_record(row, DAY)


@pytest.mark.parametrize("expiry", ["quote", "kickoff"])
def test_slow_build_rechecks_quote_expiry_and_kickoff_at_publication(tmp_path, monkeypatch, expiry):
    start = FREEZE + timedelta(minutes=5)
    published = start + timedelta(minutes=2)
    ctx = current_context(start)
    for row in ctx["slate"]:
        if expiry == "quote":
            row["odds_captured_at"] = (start - timedelta(hours=12) + timedelta(minutes=1)).isoformat()
        else:
            row["kickoff_utc"] = (start + timedelta(minutes=31)).isoformat()
    times = iter([start, published])

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(times)

    monkeypatch.setattr(mp, "datetime", Clock)
    frozen = run_capture(tmp_path, ctx, now=None)
    assert frozen["status"] == "no_paper_bet"
    assert not frozen["candidates"] and not frozen["accas"]
    assert frozen["rejections"]["quote_or_kickoff_expired_during_build"] == 2
    assert frozen["captured_at"] == start.isoformat()
    assert frozen["frozen_at"] == published.isoformat()
    assert frozen["coverage"]["candidate_count"] == 0
    mp.validate_record(frozen, DAY)


def test_concurrent_current_first_freezes_publish_only_one_card(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    decision = FREEZE + timedelta(minutes=5)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(
            lambda i: run_capture(tmp_path, current_context(decision, [pick(i), pick(i + 1)]), now=decision),
            (1, 8),
        ))
    assert sum(r is not None for r in results) == 1
    assert mp.receipts(tmp_path) == [next(r for r in results if r is not None)]


def test_cli_loads_current_slate_after_nine_but_never_reselects_frozen_card(tmp_path, monkeypatch):
    decision = FREEZE + timedelta(minutes=15)
    path = tmp_path / "picks_today.json"
    path.write_text(json.dumps(current_context(decision)["slate"]))

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return decision

    monkeypatch.setattr(at, "datetime", Clock)
    monkeypatch.setattr(mp, "datetime", Clock)
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    monkeypatch.setattr(at, "load_settled_scores", dict)
    # The CLI must not touch either live lane's state/bank.
    def forbidden(*args, **kwargs):
        raise AssertionError("live state or reselection touched")
    monkeypatch.setattr(at, "load_state", forbidden)
    assert at._run_ml_paper() is True
    frozen = mp.receipts(tmp_path)[0]
    assert frozen["accas"] and frozen["captured_at"] == decision.isoformat()
    before = mp.receipt_path(tmp_path, DAY).read_bytes()
    path.write_text("{do not reload a newer slate after freeze")
    monkeypatch.setattr(mp, "candidates", forbidden)
    monkeypatch.setattr(mp, "learn", forbidden)
    assert at._run_ml_paper() is True
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == before


def test_fsync_crossing_nine_freezes_current_build_without_creating_late_draft(tmp_path, monkeypatch):
    start = FREEZE - timedelta(seconds=1)
    published = FREEZE + timedelta(seconds=1)
    times = iter([start, start, published])

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(times)

    monkeypatch.setattr(mp, "datetime", Clock)
    frozen = run_capture(tmp_path, current_context(start), now=None)
    assert frozen["accas"] and frozen["freeze_basis"] == mp.ACTUAL_RUN_FREEZE
    assert frozen["captured_at"] == start.isoformat()
    assert frozen["frozen_at"] == frozen["persisted_at"] == published.isoformat()
    assert not mp.state_path(tmp_path).exists()
    assert not list(tmp_path.glob(".ml-paper-*.tmp"))
    mp.validate_record(frozen, DAY)


def test_alignment_never_uses_new_inputs_to_bypass_corrupt_pending_evidence(tmp_path, monkeypatch):
    path = mp.state_path(tmp_path)
    path.write_bytes(b"{damaged original")

    def forbidden(*args, **kwargs):
        raise AssertionError("must not bypass damaged evidence with a fresh selection")

    monkeypatch.setattr(mp, "candidates", forbidden)
    decision = FREEZE + timedelta(minutes=1)
    frozen = run_capture(tmp_path, current_context(decision), now=decision)
    assert frozen["status"] == "missed_freeze_no_paper_bet"
    assert not frozen["accas"]
    assert path.read_bytes() == b"{damaged original"
    assert (tmp_path / frozen["draft_integrity_error"]["quarantine"]).read_bytes() == path.read_bytes()
