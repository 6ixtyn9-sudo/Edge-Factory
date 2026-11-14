"""Uniform lane state, cadence and legacy evidence compatibility; no live runs."""

import json
import subprocess
from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from test_ml_paper import DAY, FREEZE, NOW, capture, context, pick, run_capture
from test_ml_paper_redteam import _git, _persistence_module, _seed_repo

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp


def test_one_lane_state_not_dated_draft_files_even_for_empty_cards(tmp_path):
    draft = run_capture(tmp_path, context([]))
    state = mp._read_state(tmp_path)
    assert mp.state_path(tmp_path).name == "autobets_ML_state.json"
    assert state["pending_by_date"] == {DAY: draft}
    assert not list(tmp_path.glob("autobets_ML_draft_*.json"))
    assert not mp.receipt_path(tmp_path, DAY).exists()
    assert not mp.receipts(tmp_path)
    frozen = run_capture(tmp_path, {}, now=FREEZE)
    assert frozen["status"] == "no_paper_bet"
    assert frozen["draft_sha256"] == draft["sha256"]
    assert mp._read_state(tmp_path) == state
    assert mp.receipts(tmp_path) == [frozen]
    assert not list(tmp_path.glob("autobets_ML_draft_*.json"))


@pytest.mark.parametrize("hour,minute", [(0, 0), (3, 36), (5, 59)])
def test_no_build_or_state_created_before_other_lanes_start(tmp_path, monkeypatch, hour, minute):
    early = NOW.astimezone(at.TZ).replace(hour=hour, minute=minute)

    def forbidden(*args, **kwargs):
        raise AssertionError("selection before the lanes' 06:00 build window")

    monkeypatch.setattr(mp, "candidates", forbidden)
    assert run_capture(tmp_path, context([pick(1), pick(2)]), now=early) is None
    assert not list(tmp_path.glob("*.json"))


def test_exact_six_am_can_build_pending_card(tmp_path):
    start = NOW.astimezone(at.TZ).replace(hour=6, minute=0)
    ctx = dict(context([]), build_at=start.isoformat())
    assert run_capture(tmp_path, ctx, now=start)["status"] == "draft_not_yet_frozen"
    assert mp.state_path(tmp_path).exists()
    assert not mp.receipts(tmp_path)


def test_rolling_cli_before_six_freezes_available_inputs_without_live_state(tmp_path, monkeypatch, capsys):
    early = NOW.astimezone(at.TZ).replace(hour=3, minute=36)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return early

    def forbidden(*args, **kwargs):
        raise AssertionError("live state or legacy daily capture loaded")

    rows = [pick(1), pick(2)]
    for row in rows:
        row.update(as_of=early.isoformat(), odds_captured_at=(early - timedelta(minutes=10)).isoformat(),
                   kickoff_utc=(early + timedelta(hours=4)).isoformat())
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    monkeypatch.setattr(at, "datetime", Clock)
    monkeypatch.setattr(mp, "datetime", Clock)
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    monkeypatch.setattr(at, "load_state", forbidden)
    monkeypatch.setattr(at, "load_settled_scores", forbidden)
    monkeypatch.setattr(mp, "capture", forbidden)
    assert at._run_ml_paper() is True
    frozen = mp.receipts(tmp_path)[0]
    assert frozen["accas"] and frozen["freeze_basis"] == mp.ROLLING_FREEZE
    assert frozen["frozen_at"] == early.isoformat()
    assert not mp.state_path(tmp_path).exists()
    out = capsys.readouterr()
    assert "next 24 hours" in out.out and "NOT YET" not in out.out and not out.err


def test_next_date_keeps_prior_pending_evidence_and_frozen_receipt(tmp_path):
    frozen = capture(tmp_path)
    pending = deepcopy(mp._read_state(tmp_path)["pending_by_date"][DAY])
    frozen_bytes = mp.receipt_path(tmp_path, DAY).read_bytes()
    tomorrow = NOW + timedelta(days=1)
    day = tomorrow.date().isoformat()
    ctx = dict(context([]), date=day, build_at=tomorrow.isoformat())
    next_card = run_capture(tmp_path, ctx, now=tomorrow)
    assert mp._read_state(tmp_path)["pending_by_date"] == {DAY: pending, day: next_card}
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == frozen_bytes
    assert mp.receipts(tmp_path) == [frozen]
    assert mp.latest_card(tmp_path, now=tomorrow) == next_card
    assert mp.latest_card(tmp_path, now=tomorrow + timedelta(days=1)) == frozen
    assert not list(tmp_path.glob("autobets_ML_draft_*.json"))


def legacy_draft(root, row):
    path = root / f"autobets_ML_draft_{row['date']}.json"
    blob = json.dumps(row, sort_keys=True).encode()
    path.write_bytes(blob)
    return path, blob


def test_old_runner_draft_migrates_exact_decision_even_after_cutoff(tmp_path, monkeypatch):
    pending = run_capture(tmp_path, context([pick(1), pick(2)]))
    legacy, original = legacy_draft(tmp_path, pending)
    mp.state_path(tmp_path).unlink()

    def forbidden(*args, **kwargs):
        raise AssertionError("migration must not select or learn from later data")

    monkeypatch.setattr(mp, "candidates", forbidden)
    monkeypatch.setattr(mp, "learn", forbidden)
    frozen = run_capture(tmp_path, {}, now=FREEZE + timedelta(hours=2), lookup=forbidden)
    assert frozen["accas"] == pending["accas"]
    assert frozen["draft_sha256"] == pending["sha256"]
    assert frozen["captured_at"] == pending["captured_at"]
    assert mp._read_state(tmp_path)["pending_by_date"][DAY] == json.loads(original)
    assert not legacy.exists()
    before = mp.receipt_path(tmp_path, DAY).read_bytes()
    assert run_capture(tmp_path, {}, now=FREEZE + timedelta(hours=3)) is None
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == before


@pytest.mark.parametrize("damage", ["checksum", "json", "write_failure"])
def test_failed_migration_never_deletes_old_evidence(tmp_path, monkeypatch, damage):
    pending = run_capture(tmp_path, context([pick(1), pick(2)]))
    legacy, _ = legacy_draft(tmp_path, pending)
    mp.state_path(tmp_path).unlink()
    if damage == "checksum":
        pending["sha256"] = "0" * 64
        legacy.write_text(json.dumps(pending))
    elif damage == "json":
        legacy.write_bytes(b"{original damaged evidence")
    else:
        def forbidden(*args):
            raise OSError("simulated persistence failure")
        monkeypatch.setattr(mp, "_save_state", forbidden)
    original = legacy.read_bytes()
    with pytest.raises((ValueError, OSError)):
        run_capture(tmp_path, {}, now=FREEZE)
    assert legacy.read_bytes() == original
    assert not mp.state_path(tmp_path).exists()
    assert not mp.receipt_path(tmp_path, DAY).exists()


def test_equal_time_legacy_conflict_preserves_both_versions(tmp_path):
    one = run_capture(tmp_path, context([pick(1), pick(2)]))
    run_capture(tmp_path / "other", context([pick(3), pick(4)]))
    other = mp._read_state(tmp_path / "other")["pending_by_date"][DAY]
    assert one["sha256"] != other["sha256"]
    legacy, blob = legacy_draft(tmp_path, other)
    before = mp.state_path(tmp_path).read_bytes()
    with pytest.raises(ValueError, match="equal-time"):
        run_capture(tmp_path, {}, now=FREEZE)
    assert legacy.read_bytes() == blob
    assert mp.state_path(tmp_path).read_bytes() == before
    assert not mp.receipt_path(tmp_path, DAY).exists()


def test_cached_state_union_retains_all_dates_and_latest_pre_cutoff_card(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    root = repo / "localdata"
    first = run_capture(root, context([pick(1), pick(2)]))
    path = mp.state_path(root)
    _git(repo, "add", str(path.relative_to(repo)))
    _git(repo, "commit", "-qm", "pending lane state")
    later = NOW + timedelta(minutes=20)
    second = run_capture(root, dict(context([pick(3), pick(4)]), build_at=later.isoformat()), now=later)
    tomorrow = NOW + timedelta(days=1)
    day = tomorrow.date().isoformat()
    next_card = run_capture(root, dict(context([]), date=day, build_at=tomorrow.isoformat()), now=tomorrow)
    state = mp._read_state(root)
    state["pending_by_date"].pop(DAY)
    mp._save_state(root, state)  # cache lost yesterday: committed evidence must survive
    _persistence_module().restore_committed_localdata(repo)
    assert mp._read_state(root)["pending_by_date"] == {DAY: first, day: next_card}
    # A legitimate newer cached observation wins without losing the other date.
    state = mp._read_state(root)
    state["pending_by_date"][DAY] = second
    mp._save_state(root, state)
    _persistence_module().restore_committed_localdata(repo)
    assert mp._read_state(root)["pending_by_date"] == {DAY: second, day: next_card}
    assert run_capture(root, {}, now=FREEZE)["accas"] == second["accas"]


def test_equal_time_cached_state_conflict_blocks_paper_only_and_keeps_exact_bytes(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    root = repo / "localdata"
    run_capture(root, context([pick(1), pick(2)]))
    path = mp.state_path(root)
    committed = path.read_bytes()
    _git(repo, "add", str(path.relative_to(repo)))
    _git(repo, "commit", "-qm", "pending lane state")
    other = tmp_path / "other"
    run_capture(other, context([pick(3), pick(4)]))
    cached = mp.state_path(other).read_bytes()
    path.write_bytes(cached)
    ordinary = root / "edges_consensus.json"
    original = ordinary.read_bytes()
    ordinary.write_text('{"dirty":true}')
    _persistence_module().restore_committed_localdata(repo)
    assert path.read_bytes() == committed
    assert ordinary.read_bytes() == original
    assert any(p.read_bytes() == cached for p in (root / "autobets_ML_conflicts").glob("*.json"))
    with pytest.raises(ValueError, match="paper lane blocked"):
        run_capture(root, {}, now=FREEZE)


def test_old_draft_pattern_is_no_longer_publishable():
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"],
        input="localdata/autobets_ML_draft_2026-11-02.json\nlocaldata/autobets_ML_state.json\n",
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert result.stdout.splitlines() == ["localdata/autobets_ML_draft_2026-11-02.json"]
