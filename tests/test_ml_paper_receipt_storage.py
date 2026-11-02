"""ML daily cards are TXT; frozen machine evidence lives in the internal audit tree."""

import json
import subprocess
from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from test_ml_paper import DAY, FREEZE, capture, context, pick, run_capture
from test_ml_paper_redteam import _git, _persistence_module, _seed_repo, sign

import scripts.auto_tickets_grade as grade
from edgefactory import ml_paper as mp


def legacy_path(root, day=DAY):
    return root / f"{mp.PREFIX}_{day}.json"


def make_legacy(root):
    row = capture(root)
    canonical = mp.receipt_path(root, DAY)
    blob = canonical.read_bytes()
    old = legacy_path(root)
    old.write_bytes(blob)
    canonical.unlink()
    return row, blob


def test_new_freeze_only_exposes_txt_as_daily_ticket(tmp_path):
    row = capture(tmp_path)
    assert mp.receipt_path(tmp_path, DAY).parent == tmp_path / mp.RECEIPT_DIR
    assert not legacy_path(tmp_path).exists()
    mp.publish(tmp_path, lambda leg: None)
    assert (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text() == mp.render_card(row)
    assert not list(tmp_path.glob(f"{mp.PREFIX}_????-??-??.json"))


def test_legacy_read_is_nonmutating_and_migration_is_byte_exact_idempotent(tmp_path):
    row, blob = make_legacy(tmp_path)
    state = mp.state_path(tmp_path).read_bytes()
    assert mp.receipts(tmp_path) == [row]
    assert mp.has_receipt(tmp_path, DAY)
    assert legacy_path(tmp_path).read_bytes() == blob
    assert not mp.receipt_path(tmp_path, DAY).exists()
    assert mp.migrate_receipts(tmp_path) == 1
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob
    assert not legacy_path(tmp_path).exists()
    assert mp.migrate_receipts(tmp_path) == 0
    assert mp.receipts(tmp_path) == [row]
    assert mp.state_path(tmp_path).read_bytes() == state


def test_migration_never_reselects_settles_trains_or_changes_sibling_files(tmp_path, monkeypatch):
    row, blob = make_legacy(tmp_path)
    siblings = [tmp_path / name for name in (
        "auto_tickets_state.json", "enhancement_tickets_state.json",
        "autobets_ML_state.json", f"autobets_ML_{DAY}.txt",
        "settled_results.json", "autobets_ML_performance.json",
    )]
    for p in siblings:
        if not p.exists():
            p.write_bytes(b"sibling evidence unchanged")
    before = {p: p.read_bytes() for p in siblings}

    def forbidden(*args, **kwargs):
        raise AssertionError("storage migration cannot run decision machinery")

    for name in ("candidates", "learn", "performance", "select_accas", "capture"):
        monkeypatch.setattr(mp, name, forbidden)
    mp.migrate_receipts(tmp_path)
    assert all(p.read_bytes() == data for p, data in before.items())
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob
    assert mp.receipts(tmp_path) == [row]


def test_identical_duplicate_is_counted_once_then_legacy_copy_removed(tmp_path):
    row = capture(tmp_path)
    blob = mp.receipt_path(tmp_path, DAY).read_bytes()
    legacy_path(tmp_path).write_bytes(blob)
    assert mp.receipts(tmp_path) == [row]
    assert mp.performance(mp.receipts(tmp_path), lambda leg: None)["receipt_days"] == 1
    mp.migrate_receipts(tmp_path)
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob
    assert not legacy_path(tmp_path).exists()


@pytest.mark.parametrize("damage", ["checksum", "different_valid_receipt", "format_only"])
def test_bad_or_conflicting_legacy_copy_cannot_be_discarded(tmp_path, damage):
    row = capture(tmp_path)
    canonical = mp.receipt_path(tmp_path, DAY)
    original = canonical.read_bytes()
    if damage == "checksum":
        row["sha256"] = "0" * 64
        changed = json.dumps(row).encode()
    elif damage == "different_valid_receipt":
        row["accas"][0]["stake_units"] /= 2
        changed = json.dumps(sign(row)).encode()
    else:
        changed = json.dumps(row, indent=2).encode()
    legacy_path(tmp_path).write_bytes(changed)
    with pytest.raises(ValueError):
        mp.migrate_receipts(tmp_path)
    assert canonical.read_bytes() == original
    assert legacy_path(tmp_path).read_bytes() == changed


def test_all_receipts_validate_before_any_migration(tmp_path):
    _, blob = make_legacy(tmp_path)
    bad = legacy_path(tmp_path, "2026-11-03")
    bad.write_bytes(b"{}")
    with pytest.raises(ValueError):
        mp.migrate_receipts(tmp_path)
    assert legacy_path(tmp_path).read_bytes() == blob
    assert not mp.receipt_path(tmp_path, DAY).exists()
    assert bad.read_bytes() == b"{}"


def test_failed_durable_copy_leaves_legacy_receipt_and_retry_succeeds(tmp_path, monkeypatch):
    row, blob = make_legacy(tmp_path)
    original = mp._archive_bytes

    def fail(*args):
        raise OSError("disk write failed")

    monkeypatch.setattr(mp, "_archive_bytes", fail)
    with pytest.raises(OSError, match="disk write failed"):
        mp.migrate_receipts(tmp_path)
    assert legacy_path(tmp_path).read_bytes() == blob
    monkeypatch.setattr(mp, "_archive_bytes", original)
    mp.migrate_receipts(tmp_path)
    assert mp.receipts(tmp_path) == [row]
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob


def test_interrupted_unlink_is_retryable_without_double_counting(tmp_path, monkeypatch):
    row, blob = make_legacy(tmp_path)
    path_type = type(tmp_path)
    original = path_type.unlink

    def fail(path, *args, **kwargs):
        if path == legacy_path(tmp_path):
            raise OSError("unlink interrupted")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(path_type, "unlink", fail)
    with pytest.raises(OSError, match="unlink interrupted"):
        mp.migrate_receipts(tmp_path)
    assert mp.receipts(tmp_path) == [row]
    assert legacy_path(tmp_path).read_bytes() == blob
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob
    monkeypatch.setattr(path_type, "unlink", original)
    assert mp.migrate_receipts(tmp_path) == 1


def test_publisher_migrates_without_changing_forward_card(tmp_path):
    row, blob = make_legacy(tmp_path)
    before = mp.performance([row], lambda leg: None)
    report = mp.publish(tmp_path, lambda leg: None)
    assert report == before
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob
    assert not legacy_path(tmp_path).exists()
    assert (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text() == mp.render_card(row)


def test_capture_of_legacy_frozen_day_never_uses_new_inputs(tmp_path, monkeypatch):
    row, blob = make_legacy(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("frozen day must not be reselected")

    monkeypatch.setattr(mp, "candidates", forbidden)
    assert run_capture(tmp_path, context([pick(9)]), now=FREEZE + timedelta(hours=1)) is None
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob
    assert mp.receipts(tmp_path) == [row]


@pytest.mark.parametrize("layout", ["legacy", "internal"])
def test_grader_loads_results_with_either_receipt_layout(tmp_path, monkeypatch, layout):
    row = capture(tmp_path)
    if layout == "legacy":
        canonical = mp.receipt_path(tmp_path, DAY)
        legacy_path(tmp_path).write_bytes(canonical.read_bytes())
        canonical.unlink()
    sentinel = {"result": "existing score lookup"}
    calls = []
    monkeypatch.setattr(grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(grade.at, "load_settled_scores", lambda: calls.append("scores") or sentinel)
    monkeypatch.setattr(grade.at, "ml_paper_score_lookup", lambda scores: (
        calls.append(scores) or (lambda leg: None)
    ))
    grade.publish_ml_paper()
    assert calls == ["scores", sentinel]
    assert mp.receipts(tmp_path) == [row]
    assert not legacy_path(tmp_path).exists()


@pytest.mark.parametrize("head_layout", ["legacy", "internal"])
@pytest.mark.parametrize("cache_layout", ["legacy", "internal"])
@pytest.mark.parametrize("conflict", [False, True])
def test_cache_restore_retains_both_layouts_and_blocks_conflicts_only_for_paper(
    tmp_path, head_layout, cache_layout, conflict,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    root = repo / "localdata"
    row = capture(root)
    canonical = mp.receipt_path(root, DAY)
    original = canonical.read_bytes()
    head = canonical if head_layout == "internal" else legacy_path(root)
    if head != canonical:
        head.write_bytes(original)
        canonical.unlink()
    _git(repo, "add", "-f", str(head.relative_to(repo)))
    _git(repo, "commit", "-qm", "frozen paper evidence")
    head.unlink()
    cached = canonical if cache_layout == "internal" else legacy_path(root)
    changed = deepcopy(row)
    if conflict:
        changed["accas"][0]["stake_units"] /= 2
    blob = json.dumps(sign(changed)).encode() if conflict else original
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(blob)
    ordinary = root / "edges_consensus.json"
    ordinary_before = ordinary.read_bytes()
    ordinary.write_text('{"dirty":true}')
    _persistence_module().restore_committed_localdata(repo)
    assert ordinary.read_bytes() == ordinary_before
    if conflict:
        assert (root / "autobets_ML_integrity_block.json").exists()
        copies = [p.read_bytes() for p in mp.receipt_files(root)]
        copies.extend(p.read_bytes() for p in (root / "autobets_ML_conflicts").glob("*.json"))
        assert original in copies and blob in copies
        with pytest.raises(ValueError, match="paper lane blocked"):
            mp.receipts(root)
    else:
        assert canonical.read_bytes() == original
        assert not legacy_path(root).exists()
        assert mp.receipts(root) == [row]
        _persistence_module().restore_committed_localdata(repo)
        assert mp.receipts(root) == [row]
        assert not legacy_path(root).exists()


def test_internal_receipts_are_git_persistable_and_daily_json_is_ignored():
    internal = f"localdata/{mp.RECEIPT_DIR}/{mp.PREFIX}_{DAY}.json"
    legacy = f"localdata/{mp.PREFIX}_{DAY}.json"
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"],
        input=f"{internal}\n{legacy}\nlocaldata/{mp.PREFIX}_{DAY}.txt\n",
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert result.stdout.splitlines() == [legacy]


@pytest.mark.parametrize("layout", ["legacy", "internal"])
def test_cli_frozen_guard_does_not_reload_slate_in_either_layout(tmp_path, monkeypatch, layout):
    row = capture(tmp_path)
    canonical = mp.receipt_path(tmp_path, DAY)
    original = canonical.read_bytes()
    if layout == "legacy":
        legacy_path(tmp_path).write_bytes(original)
        canonical.unlink()
    decision = FREEZE + timedelta(hours=1)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return decision

    def forbidden(*args, **kwargs):
        raise AssertionError("frozen day must not reload inputs, reselect or touch live state")

    monkeypatch.setattr(grade.at, "datetime", Clock)
    monkeypatch.setattr(mp, "datetime", Clock)
    monkeypatch.setattr(grade.at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(grade.at, "load_settled_scores", dict)
    monkeypatch.setattr(grade.at, "load_state", forbidden)
    monkeypatch.setattr(mp, "candidates", forbidden)
    monkeypatch.setattr(mp, "learn", forbidden)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    # No picks_today.json exists: attempting to load current inputs must fail.
    assert grade.at._run_ml_paper() is True
    assert mp.receipts(tmp_path) == [row]
    assert canonical.read_bytes() == original
    assert not legacy_path(tmp_path).exists()


def test_concurrent_migration_and_capture_cannot_replace_frozen_receipt(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    row, blob = make_legacy(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as executor:
        migration = executor.submit(mp.migrate_receipts, tmp_path)
        repeat = executor.submit(run_capture, tmp_path, {}, now=FREEZE)
        migration.result()
        assert repeat.result() is None
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == blob
    assert not legacy_path(tmp_path).exists()
    assert mp.receipts(tmp_path) == [row]


def test_mixed_history_stays_chronological_with_identical_learning_and_performance(tmp_path):
    first, original = make_legacy(tmp_path)
    next_day = FREEZE + timedelta(days=1)
    # A separate synthetic fixture keeps the initial day in the old layout.
    other = tmp_path / "synthetic"
    later = run_capture(other, {"date": next_day.date().isoformat(), "slate": []}, now=next_day)
    destination = mp.receipt_path(tmp_path, later["date"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(mp.receipt_path(other, later["date"]).read_bytes())
    history = mp.receipts(tmp_path)
    assert history == [first, later]
    decision = next_day + timedelta(days=1)
    def results(leg):
        return (2, 0)
    report = mp.performance(history, results)
    learning = mp.learn(history, decision, results)
    mp.migrate_receipts(tmp_path)
    assert mp.receipts(tmp_path) == history
    assert mp.performance(mp.receipts(tmp_path), results) == report
    assert mp.learn(mp.receipts(tmp_path), decision, results) == learning
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == original



def test_reader_survives_legacy_move_after_directory_listing(tmp_path, monkeypatch):
    row, blob = make_legacy(tmp_path)
    legacy = legacy_path(tmp_path)
    canonical = mp.receipt_path(tmp_path, DAY)
    original = type(tmp_path).read_bytes
    moved = False

    def read(path):
        nonlocal moved
        if path == legacy and not moved:
            moved = True
            canonical.parent.mkdir(parents=True, exist_ok=True)
            canonical.write_bytes(blob)
            legacy.unlink()
        return original(path)

    monkeypatch.setattr(type(tmp_path), "read_bytes", read)
    assert mp.receipts(tmp_path) == [row]
    assert moved


def test_frozen_guard_checks_legacy_before_internal_during_move(tmp_path, monkeypatch):
    _, blob = make_legacy(tmp_path)
    legacy = legacy_path(tmp_path)
    canonical = mp.receipt_path(tmp_path, DAY)
    original = type(tmp_path).exists
    checked = []

    def exists(path):
        checked.append(path)
        if path == legacy:
            canonical.write_bytes(blob)
            legacy.unlink()
        return original(path)

    monkeypatch.setattr(type(tmp_path), "exists", exists)
    assert mp.has_receipt(tmp_path, DAY)
    assert checked == [legacy, canonical]



def test_nested_directory_entries_are_durable_before_legacy_unlink(tmp_path, monkeypatch):
    make_legacy(tmp_path)
    events = []
    original_sync = mp._sync_directory
    original_unlink = type(tmp_path).unlink

    def sync(path):
        events.append(("sync", path))
        original_sync(path)

    def unlink(path, *args, **kwargs):
        events.append(("unlink", path))
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(mp, "_sync_directory", sync)
    monkeypatch.setattr(type(tmp_path), "unlink", unlink)
    mp.migrate_receipts(tmp_path)
    index = events.index(("unlink", legacy_path(tmp_path)))
    before_unlink = events[:index]
    leaf = mp.receipt_path(tmp_path, DAY).parent
    leaf_sync = before_unlink.index(("sync", leaf))
    parent_sync = before_unlink.index(("sync", leaf.parent))
    assert leaf_sync < parent_sync
    assert ("sync", tmp_path) in before_unlink[parent_sync + 1:]
