"""Rolling PAPER only: real candidate guards/search, immutable evidence and bank."""

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from test_ml_paper import DAY, FREEZE, NOW, capture, pick
from test_ml_paper_redteam import sign
from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp
from edgefactory.consensus_contracts import enhancement_fixture_identity


def slate(now=NOW, ids=(1, 2), *, kickoff=None):
    kickoff = kickoff or now + timedelta(hours=4)
    rows = []
    for i in ids:
        row = pick(i)
        day = kickoff.astimezone(mp.LOCAL_TZ).date().isoformat()
        row.update(
            date=day,
            as_of=now.isoformat(),
            built_at_utc=now.isoformat(),
            kickoff_utc=kickoff.isoformat(),
            odds_captured_at=(now - timedelta(minutes=10)).isoformat(),
        )
        profile = row["statistical_profile"]
        model = profile["ml_model"]
        model.update(
            as_of_exclusive=day,
            train_last_date=(now.astimezone(mp.LOCAL_TZ).date() - timedelta(days=1)).isoformat(),
        )
        model.pop("model_key")
        model["model_key"] = hashlib.sha256(
            json.dumps(model, sort_keys=True, allow_nan=False).encode()
        ).hexdigest()
        profile.update(as_of_exclusive=day)
        profile["ml_inputs"].update(
            fixture=enhancement_fixture_identity(row), model_key=model["model_key"]
        )
        rows.append(row)
    return rows


def run(root, now=NOW, rows=None, lookup=lambda c: None, **kwargs):
    return mp.capture_rolling(
        {"build_at": now.isoformat(), "slate": slate(now) if rows is None else rows},
        root=root,
        score_lookup=lookup,
        kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection,
        now=now,
        index={},
        **kwargs,
    )


@pytest.mark.parametrize("hour", [0, 3, 5, 6, 8, 9, 17, 23])
def test_every_hour_freezes_immediately_without_a_draft(tmp_path, hour):
    now = NOW.astimezone(mp.LOCAL_TZ).replace(hour=hour)
    # Keep fixture UTC/SAST calendar unambiguous, including midnight decisions.
    row = run(tmp_path, now, slate(now, kickoff=now + timedelta(hours=4)))
    assert row["accas"] and row["status"] == "paper_accas"
    assert row["freeze_basis"] == mp.ROLLING_FREEZE
    assert row["frozen_at"] == row["persisted_at"] == row["captured_at"] == now.isoformat()
    assert not mp.state_path(tmp_path).exists()
    assert mp.receipts(tmp_path) == [row]


def test_next_day_overnight_quotes_are_eligible_from_previous_evening(tmp_path):
    now = NOW.astimezone(mp.LOCAL_TZ).replace(hour=23)
    kickoff = (now + timedelta(days=1)).replace(hour=3)
    row = run(tmp_path, now, slate(now, kickoff=kickoff))
    assert row["accas"] and {c["date"] for c in row["candidates"]} == {"2026-11-03"}
    assert row["date"] == DAY
    assert row["window_end"] == (now + timedelta(hours=24)).isoformat()
    card = mp.render_card(row)
    assert "2026-11-03 03:00 SAST" in card and "next 24 hours" in card
    # Kickoff sits next to its matchup on the same line: one header line
    # per leg, so legs are countable at a glance.
    assert "   Home Club 1 vs Away Club 1 · KICKOFF 2026-11-03 03:00 SAST\n" in card
    assert card.count("KICKOFF ") == sum(len(a["legs"]) for a in row["accas"])


@pytest.mark.parametrize("delta,allowed", [(29, False), (30, True), (1440, True), (1441, False)])
def test_exact_rolling_window_and_existing_lead(tmp_path, delta, allowed):
    row = run(tmp_path, rows=slate(kickoff=NOW + timedelta(minutes=delta)))
    assert bool(row["accas"]) is allowed


@pytest.mark.parametrize(
    "field", ["as_of", "built_at_utc", "odds_captured_at", "model", "unproven", "ambiguous_date"]
)
def test_no_future_or_unproven_inputs_rescued_by_tomorrows_date(tmp_path, field):
    now = NOW.astimezone(mp.LOCAL_TZ).replace(hour=23)
    rows = slate(now, kickoff=(now + timedelta(days=1)).replace(hour=3))
    for row in rows:
        if field == "model":
            model = row["statistical_profile"]["ml_model"]
            model["train_last_date"] = DAY
            model.pop("model_key")
            model["model_key"] = hashlib.sha256(
                json.dumps(model, sort_keys=True, allow_nan=False).encode()
            ).hexdigest()
            row["statistical_profile"]["ml_inputs"]["model_key"] = model["model_key"]
        elif field == "unproven":
            row.pop("kickoff_utc")
        elif field == "ambiguous_date":
            row["kickoff_utc"] = (
                now + timedelta(hours=1)
            ).isoformat()  # 00:00 SAST / previous UTC day
        else:
            row[field] = (now + timedelta(seconds=1)).isoformat()
    row = run(tmp_path, now, rows)
    assert not row["accas"] and not row["candidates"]


@pytest.mark.parametrize("source,hours", [("theoddsapi", 12), ("oddspapi", 6)])
@pytest.mark.parametrize("extra,allowed", [(0, True), (1, False)])
def test_original_source_quote_age_limits_retained(tmp_path, source, hours, extra, allowed):
    rows = slate()
    for row in rows:
        row.update(
            odds_source=source,
            odds_captured_at=(NOW - timedelta(hours=hours, seconds=extra)).isoformat(),
        )
        from test_ml_paper import synthetic_oddspapi_provenance
        row["odds_provenance"] = synthetic_oddspapi_provenance(row)
    assert bool(run(tmp_path, rows=rows)["accas"]) is allowed


def test_repeats_and_concurrency_never_recommit_published_fixtures(tmp_path):
    with ThreadPoolExecutor(max_workers=2) as pool:
        decisions = list(pool.map(lambda _: run(tmp_path), range(2)))
    assert sum(r is not None for r in decisions) == 1
    frozen = mp.receipts(tmp_path)[0]
    path = mp.rolling_receipt_path(tmp_path, frozen)
    raw = path.read_bytes()
    # Better prices or another market on a committed fixture cannot reopen it.
    rows = slate(NOW + timedelta(minutes=1))
    for row in rows:
        row["odds"] = 3.0
    assert run(tmp_path, NOW + timedelta(minutes=1), rows) is None
    assert mp.receipts(tmp_path) == [frozen] and path.read_bytes() == raw


def test_many_additions_share_one_aggregate_exposure_limit(tmp_path):
    originals = {}
    for i in range(10):
        now = NOW + timedelta(minutes=i)
        row = run(tmp_path, now, slate(now, ids=(2 * i + 1, 2 * i + 2)))
        assert row is not None
        path = mp.rolling_receipt_path(tmp_path, row)
        originals[path] = path.read_bytes()
        history = mp.receipts(tmp_path)
        report = mp.performance(history, lambda c: None)
        assert report["paper_bank_units"] == 100
        assert report["paper_committed_units"] <= 25 + 1e-6
        assert all(p.read_bytes() == blob for p, blob in originals.items())
    assert len(history) == 10 and sum(bool(r["accas"]) for r in history) > 1
    # The approved 5% fixture budget binds before the shared 25% ceiling:
    # five distinct-fixture publications reserve 5u each; later ones are NO BET.
    assert report["receipt_days"] == report["bet_days"] == 1
    assert report["no_bet_days"] == 0 and report["decision_receipts"] == 10
    assert sum(bool(r["accas"]) for r in history) == 5
    assert report["paper_committed_units"] == pytest.approx(25, abs=1e-6)
    assert all(
        e["published_stake_micro_units"] <= e["residual_budget_micro_units"]
        for r in history for e in r["fixture_concentration"]["fixtures"]
    )
    assert any(r["fixture_concentration"]["released_stake_micro_units"] for r in history)
    mp.publish(tmp_path, lambda c: None)
    text = (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text()
    audit = (tmp_path / mp.RECEIPT_DIR / "reports" / f"{mp.PREFIX}_{DAY}_audit.txt").read_text()
    assert all(r["decision_id"] in text for r in history if r["accas"])
    assert all(r["decision_id"] in audit for r in history)
    assert text.count("[PAPER ACCA #") == sum(len(r["accas"]) for r in history)
    assert not list(tmp_path.glob("autobets_ML_????-??-??*.json"))


def test_empty_or_one_leg_decision_does_not_block_later_opportunities(tmp_path):
    first = run(tmp_path, rows=[])
    original = mp.rolling_receipt_path(tmp_path, first).read_bytes()
    assert not first["accas"] and run(tmp_path, NOW + timedelta(seconds=1), []) is None
    one = run(tmp_path, NOW + timedelta(minutes=1), slate(NOW, ids=(1,)))
    assert not one["accas"] and one["candidates"]
    last = run(tmp_path, NOW + timedelta(minutes=2), slate(NOW))
    assert last["accas"]
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == original
    assert len(mp.receipts(tmp_path)) == 3


def test_legacy_receipt_and_pending_state_survive_and_reserve_capital(tmp_path):
    old = capture(tmp_path, [pick(1), pick(2)])
    path, state = mp.receipt_path(tmp_path, DAY), mp.state_path(tmp_path)
    originals = (path.read_bytes(), state.read_bytes())
    now = FREEZE + timedelta(minutes=10)
    row = run(tmp_path, now, slate(now, ids=(3, 4)))
    assert row["accas"]
    assert row["paper_pending_reserved_at_decision"] == sum(a["stake_units"] for a in old["accas"])
    assert mp.performance(mp.receipts(tmp_path), lambda c: None)["paper_committed_units"] <= 25
    assert (path.read_bytes(), state.read_bytes()) == originals
    # No re-entry even on a different day after a result becomes available.
    assert run(tmp_path, now + timedelta(minutes=1), slate(now)) is None


def test_settlement_changes_own_bank_without_refilling_or_resizing_old_stakes(tmp_path):
    first = run(tmp_path)
    before = mp.rolling_receipt_path(tmp_path, first).read_bytes()

    def loss(c):
        return (0, 1) if c["home"] in {"Home Club 1", "Home Club 2"} else None

    second = run(tmp_path, NOW + timedelta(minutes=1), slate(NOW, ids=(3, 4)), lookup=loss)
    report = mp.performance([first], loss)
    assert second["paper_bank_at_decision"] == report["paper_bank_units"] < 100
    assert second["paper_pending_reserved_at_decision"] == 0
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == before
    assert sum(a["stake_units"] for a in second["accas"]) <= second["paper_bank_at_decision"] * 0.25


def test_pending_corruption_still_fails_closed(tmp_path):
    mp.state_path(tmp_path).write_text("{broken state")
    with pytest.raises(ValueError):
        run(tmp_path)
    assert not mp.receipt_files(tmp_path)
    assert mp.state_path(tmp_path).read_text() == "{broken state"


@pytest.mark.parametrize(
    "damage", ["publication", "window", "capital", "model", "lead", "identity"]
)
def test_signed_but_false_rolling_timing_and_capital_fail_validation(tmp_path, damage):
    row = deepcopy(run(tmp_path))
    if damage == "publication":
        row["persisted_at"] = (NOW - timedelta(seconds=1)).isoformat()
    if damage == "window":
        row["window_end"] = (NOW + timedelta(hours=25)).isoformat()
    if damage == "capital":
        row["paper_pending_reserved_at_decision"] = 99
    if damage == "model":
        next(iter(row["models"].values()))["train_last_date"] = DAY
    if damage == "lead":
        row["candidates"][0]["kickoff_utc"] = (NOW + timedelta(minutes=29)).isoformat()
    if damage == "identity":
        row["decision_id"] = "wrong"
    with pytest.raises(ValueError):
        mp.validate_record(sign(row), DAY)


def test_learning_never_uses_today_fixture_from_yesterdays_rolling_decision(tmp_path):
    now = NOW.astimezone(mp.LOCAL_TZ).replace(hour=23)
    row = run(tmp_path, now, slate(now, kickoff=(now + timedelta(days=1)).replace(hour=3)))
    today = now + timedelta(days=1)
    assert mp.learn([row], today, lambda c: (1, 0))["fixtures"] == 0
    assert mp.learn([row], today + timedelta(days=1), lambda c: (1, 0))["fixtures"] == 2


def test_daily_drawdown_groups_all_publications_not_intraday_marks(tmp_path):
    first = run(tmp_path)
    second = run(tmp_path, NOW + timedelta(minutes=1), slate(NOW, ids=(3, 4)))

    def lookup(c):
        return (0, 1) if c["home"] in {"Home Club 1", "Home Club 2"} else (1, 0)

    report = mp.performance([first, second], lookup)
    # Same day net positive: a receipt-order loss must not invent daily drawdown.
    assert report["profit_units"] > 0 and report["max_daily_close_drawdown_units"] == 0


@pytest.mark.parametrize("conflict", [False, True])
def test_cache_restore_keeps_multiple_rolling_decisions_and_blocks_exact_conflict(
    tmp_path, conflict
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    root = repo / "localdata"
    first = run(root)
    path = mp.rolling_receipt_path(root, first)
    original = path.read_bytes()
    _git(repo, "add", "-f", str(path.relative_to(repo)))
    _git(repo, "commit", "-qm", "first rolling decision")
    second = run(root, NOW + timedelta(minutes=1), slate(NOW, ids=(3, 4)))
    path2 = mp.rolling_receipt_path(root, second)
    raw2 = path2.read_bytes()
    if conflict:
        altered = deepcopy(first)
        altered["rejections"]["different"] = 1
        path.write_text(json.dumps(sign(altered)))
    _persistence_module().restore_committed_localdata(repo)
    assert path.read_bytes() == original and path2.read_bytes() == raw2
    if conflict:
        with pytest.raises(ValueError, match="conflict"):
            mp.receipts(root)
        assert list((root / "autobets_ML_conflicts").glob("*.json"))
    else:
        assert mp.receipts(root) == [first, second]
        assert not (root / "autobets_ML_integrity_block.json").exists()


def test_cli_combines_current_and_future_existing_slates_and_never_live_state(
    tmp_path, monkeypatch
):
    now = NOW.astimezone(mp.LOCAL_TZ).replace(hour=23)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    monkeypatch.setattr(at, "datetime", Clock)
    monkeypatch.setattr(mp, "datetime", Clock)
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")

    def forbidden(*args, **kwargs):
        raise AssertionError("live state loaded")

    monkeypatch.setattr(at, "load_state", forbidden)
    current = slate(now, ids=(1,), kickoff=now + timedelta(minutes=45))
    future = slate(now, ids=(2,), kickoff=(now + timedelta(days=1)).replace(hour=3))
    (tmp_path / "picks_today.json").write_text(json.dumps(current))
    (tmp_path / "picks_next_2days.json").write_text(json.dumps(future))
    assert at._run_ml_paper() is True
    row = mp.receipts(tmp_path)[0]
    assert row["accas"] and {c["date"] for c in row["candidates"]} == {DAY, "2026-11-03"}


@pytest.mark.parametrize("expiry", ["quote", "kickoff", "midnight"])
def test_slow_search_uses_actual_publication_time_and_never_backdates(
    tmp_path, monkeypatch, expiry
):
    start = NOW if expiry != "midnight" else NOW.astimezone(mp.LOCAL_TZ).replace(hour=23, minute=59)
    published = start + timedelta(minutes=2)
    rows = slate(start)
    for row in rows:
        if expiry == "quote":
            row["odds_captured_at"] = (
                start - timedelta(hours=12) + timedelta(minutes=1)
            ).isoformat()
        elif expiry == "kickoff":
            row["kickoff_utc"] = (start + timedelta(minutes=31)).isoformat()
    times = iter([start, published, published])

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(times)

    monkeypatch.setattr(mp, "datetime", Clock)
    row = mp.capture_rolling(
        {"build_at": start.isoformat(), "slate": rows},
        root=tmp_path,
        score_lookup=lambda c: None,
        kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection,
        index={},
    )
    if expiry == "midnight":
        assert row is None and not mp.receipt_files(tmp_path)
    else:
        assert (
            row["captured_at"] == start.isoformat() and row["persisted_at"] == published.isoformat()
        )
        assert not row["accas"] and not row["candidates"]
        assert row["rejections"]["quote_or_kickoff_expired_during_build"] == 2


def test_missing_prior_capital_evidence_cannot_be_treated_as_fresh_bank(tmp_path):
    first = run(tmp_path)
    second = run(tmp_path, NOW + timedelta(minutes=1), slate(NOW, ids=(3, 4)))
    assert second["prior_receipt_sha256s"] == [first["sha256"]]
    mp.rolling_receipt_path(tmp_path, first).unlink()
    with pytest.raises(ValueError, match="missing capital evidence"):
        mp.receipts(tmp_path)
    with pytest.raises(ValueError, match="missing capital evidence"):
        run(tmp_path, NOW + timedelta(minutes=2), slate(NOW, ids=(5, 6)))


def test_independent_history_forks_fail_closed_on_cache_union(tmp_path):
    # Simulates two independent runners that each saw an empty history.
    other = tmp_path / "other"
    first = run(tmp_path)
    second = run(other, NOW + timedelta(minutes=1), slate(NOW, ids=(3, 4)))
    target = mp.rolling_receipt_path(tmp_path, second)
    target.write_bytes(mp.rolling_receipt_path(other, second).read_bytes())
    assert first["prior_receipt_sha256s"] == second["prior_receipt_sha256s"] == []
    with pytest.raises(ValueError, match="history fork"):
        mp.receipts(tmp_path)


def test_next_day_addition_reserves_yesterdays_open_overnight_positions(tmp_path):
    now = NOW.astimezone(mp.LOCAL_TZ).replace(hour=23)
    kickoff = (now + timedelta(days=1)).replace(hour=3)
    first = run(tmp_path, now, slate(now, kickoff=kickoff))
    next_run = (now + timedelta(days=1)).replace(hour=2)
    second = run(
        tmp_path, next_run, slate(next_run, ids=(3, 4), kickoff=kickoff + timedelta(hours=1))
    )
    assert first["date"] != second["date"] and second["accas"]
    assert second["paper_pending_reserved_at_decision"] == sum(
        a["stake_units"] for a in first["accas"]
    )
    assert mp.performance(mp.receipts(tmp_path), lambda c: None)["paper_committed_units"] <= 25


def test_prior_drafts_are_not_committed_fixtures(tmp_path):
    from test_ml_paper import context, run_capture

    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    raw = mp.state_path(tmp_path).read_bytes()
    row = run(tmp_path, NOW + timedelta(minutes=1))
    assert row["accas"] and {tuple(c["fixture"]) for c in row["candidates"]} == {
        tuple(c["fixture"]) for c in draft["candidates"]
    }
    assert mp.state_path(tmp_path).read_bytes() == raw


def test_future_planner_invokes_existing_ml_only_after_writing_forecasts(tmp_path, monkeypatch):
    from scripts import daily

    now = NOW.astimezone(mp.LOCAL_TZ).replace(hour=23)
    current = slate(now, ids=(1,), kickoff=now + timedelta(minutes=45))
    future = slate(now, ids=(2,), kickoff=(now + timedelta(days=1)).replace(hour=3))
    picks = tmp_path / "picks_today.json"
    picks.write_text(json.dumps(future))
    monkeypatch.setattr(daily, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(daily, "PICKS_TODAY_FILE", picks)
    monkeypatch.setattr(daily, "run_capture", lambda *a, **kw: "")
    monkeypatch.setattr(daily, "print_pick_run_summary", lambda *a: None)
    monkeypatch.setattr(daily, "load_picks_file", lambda: future)
    monkeypatch.setattr(daily, "generate_daily_report", lambda *a, **kw: None)
    calls = []

    def ml():
        content = json.loads((tmp_path / "picks_next_2days.json").read_text())
        calls.append({p["date"] for p in content})

    monkeypatch.setattr(daily, "run_ml_paper", ml)
    daily.run_future_planner(DAY, 2, current, now.isoformat())
    assert calls == [{DAY, "2026-11-03"}]


def test_cli_repeated_report_shows_all_frozen_publications(tmp_path, monkeypatch, capsys):
    now = NOW

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    monkeypatch.setattr(at, "datetime", Clock)
    monkeypatch.setattr(mp, "datetime", Clock)
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "load_settled_scores", dict)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    path = tmp_path / "picks_today.json"
    path.write_text(json.dumps(slate(now)))
    assert at._run_ml_paper() is True
    capsys.readouterr()
    now += timedelta(minutes=1)
    path.write_text(json.dumps(slate(now, ids=(3, 4))))
    assert at._run_ml_paper() is True
    output = capsys.readouterr().out
    assert all(r["decision_id"] in output for r in mp.receipts(tmp_path))
    assert all(f"Home Club {i}" in output for i in range(1, 5))


@pytest.mark.parametrize("bad_input", ["{broken", '{"not": "a list"}'])
def test_cli_bad_refresh_cannot_replace_or_reset_frozen_evidence(
    tmp_path, monkeypatch, capsys, bad_input
):
    first = run(tmp_path)
    frozen_path = mp.rolling_receipt_path(tmp_path, first)
    original = frozen_path.read_bytes()
    decision = NOW + timedelta(minutes=1)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return decision

    monkeypatch.setattr(at, "datetime", Clock)
    monkeypatch.setattr(mp, "datetime", Clock)
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "load_settled_scores", dict)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    (tmp_path / "picks_today.json").write_text(bad_input)
    assert at._run_ml_paper() is False
    assert "live lanes unchanged" in capsys.readouterr().err
    assert mp.receipts(tmp_path) == [first] and frozen_path.read_bytes() == original
    assert not mp.state_path(tmp_path).exists()
