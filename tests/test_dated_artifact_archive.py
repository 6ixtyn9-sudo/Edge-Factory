"""Cold daily evidence is identical, discoverable and survives runner restore."""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import pytest

from edgefactory.util import (
    DATED_ARCHIVE_FAMILIES,
    archive_dated_artifacts,
    dated_archive_path,
    dated_artifact_files,
    dated_artifact_path,
)

TODAY = date(2026, 11, 4)
OLD = "2026-09-01"


def put(root, name, payload=b"original\x00\xff\n"):
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_bytes(payload)
    return path


@pytest.mark.parametrize("family,ext", [(f, e) for f, es in DATED_ARCHIVE_FAMILIES.items()
                                       for e in sorted(es)])
def test_all_known_families_relocate_exact_bytes_and_keep_active_paths(tmp_path, family, ext):
    name = f"{family}_{OLD}.{ext}"
    source = put(tmp_path, name)
    before = source.read_bytes()
    recent = put(tmp_path, f"{family}_2026-11-04.{ext}", b"active")
    moved = archive_dated_artifacts(tmp_path, today=TODAY)
    target = dated_archive_path(tmp_path, name)
    assert moved == [(source, target)]
    assert not source.exists() and target.read_bytes() == before
    assert recent.read_bytes() == b"active"
    assert dated_artifact_path(tmp_path, name) == target
    assert dated_artifact_path(tmp_path, recent.name) == recent
    assert archive_dated_artifacts(tmp_path, today=TODAY) == []


def test_boundary_future_unknown_monthly_state_and_special_receipts_stay(tmp_path):
    names = ["picks_2026-10-06.json", "picks_2026-11-05.json", "picks_2026-02-31.json",
             "auto_tickets_state.json", "autobets_ML_state.json", "settled_results.json",
             "forebet_2026-01.csv.gz", "auto_tickets_2026-09-01.json",
             "autobets_enh_tickets_2026-09-01_reset.json",
             "auto_tickets_2026-09-01_force_recut.txt", "unknown_2026-09-01.json"]
    for name in names:
        put(tmp_path, name)
    old = put(tmp_path, "picks_2026-10-05.json")
    archive_dated_artifacts(tmp_path, today=TODAY)
    assert not old.exists()
    assert all((tmp_path / name).exists() for name in names)


def test_latest_human_card_is_kept_even_after_a_long_gap(tmp_path):
    for prefix in ("auto_tickets", "autobets_enh_tickets", "autobets_ML"):
        older = put(tmp_path, f"{prefix}_2026-08-01.txt")
        latest = put(tmp_path, f"{prefix}_2026-08-02.txt")
        archive_dated_artifacts(tmp_path, today=TODAY)
        assert not older.exists()
        assert latest.exists()


def test_dry_run_creates_no_archive_or_lock(tmp_path):
    source = put(tmp_path, f"picks_{OLD}.json")
    assert archive_dated_artifacts(tmp_path, today=TODAY, dry_run=True)
    assert source.exists() and not (tmp_path / "archive").exists()
    with pytest.raises(ValueError):
        archive_dated_artifacts(tmp_path, today=TODAY, keep_days=0)


def test_duplicate_cache_copy_is_one_logical_artifact_and_conflict_fails_closed(tmp_path):
    name = f"picks_{OLD}.json"
    source = put(tmp_path, name)
    original = source.read_bytes()
    archive_dated_artifacts(tmp_path, today=TODAY)
    target = dated_artifact_path(tmp_path, name)
    put(tmp_path, name, original)
    assert dated_artifact_files(tmp_path, "picks_*.json") == [target]
    source.write_bytes(b"DIFFERENT")
    with pytest.raises(ValueError, match="conflicting"):
        dated_artifact_files(tmp_path, "picks_*.json")
    with pytest.raises(ValueError, match="conflicting"):
        archive_dated_artifacts(tmp_path, today=TODAY)
    assert source.read_bytes() == b"DIFFERENT" and target.read_bytes() == original


def test_ordering_matches_the_old_flat_glob_without_duplicate_rows(tmp_path):
    names = ["picks_morning_2026-09-01.json", "picks_2026-09-01.json",
             "picks_2026-11-04.json", "picks_today.json", "picks_next_2days.json"]
    for name in names:
        put(tmp_path, name, b"[]")
    archive_dated_artifacts(tmp_path, today=TODAY)
    assert [p.name for p in dated_artifact_files(tmp_path, "picks_*.json")] == sorted(names)


def test_symlinks_cannot_move_or_escape_archive(tmp_path):
    external = put(tmp_path / "external", "outside", b"outside")
    (tmp_path / f"picks_{OLD}.json").symlink_to(external)
    assert archive_dated_artifacts(tmp_path, today=TODAY) == []
    (tmp_path / "archive").symlink_to(tmp_path / "external", target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        dated_artifact_path(tmp_path, f"picks_{OLD}.json")
    assert external.read_bytes() == b"outside"


def test_interrupted_copy_never_unlinks_the_only_original(tmp_path, monkeypatch):
    import shutil
    source = put(tmp_path, f"picks_{OLD}.json")
    original = source.read_bytes()

    def fail_copy(*args, **kwargs):
        raise OSError("simulated storage failure")

    monkeypatch.setattr(shutil, "copy2", fail_copy)
    with pytest.raises(OSError):
        archive_dated_artifacts(tmp_path, today=TODAY)
    assert source.read_bytes() == original
    assert not dated_archive_path(tmp_path, source.name).exists()


def test_source_change_during_copy_preserves_both_versions(tmp_path, monkeypatch):
    import shutil
    source = put(tmp_path, f"picks_{OLD}.json")
    original = source.read_bytes()
    copy = shutil.copy2

    def changing_copy(src, dst):
        copy(src, dst)
        Path(src).write_bytes(b"new revision")

    monkeypatch.setattr(shutil, "copy2", changing_copy)
    with pytest.raises(ValueError, match="changed"):
        archive_dated_artifacts(tmp_path, today=TODAY)
    assert source.read_bytes() == b"new revision"
    assert dated_archive_path(tmp_path, source.name).read_bytes() == original


def test_concurrent_rollover_is_idempotent(tmp_path):
    original = {}
    for i in range(1, 15):
        name = f"picks_2026-09-{i:02d}.json"
        original[name] = put(tmp_path, name, str(i).encode()).read_bytes()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: archive_dated_artifacts(tmp_path, today=TODAY), range(4)))
    for name, payload in original.items():
        assert dated_artifact_path(tmp_path, name).read_bytes() == payload
        assert not (tmp_path / name).exists()


def test_replay_and_audit_keep_distinct_morning_and_regular_generations(tmp_path, monkeypatch):
    import scripts.audit_recent_picks as audit
    import scripts.auto_tickets as tickets
    import scripts.replay_harness as replay
    from scripts.edge_firing_tripwire import _load_pick_rows
    from scripts.price_coverage_report import pick_archives
    from scripts.report_sportytrader_7pct import build_report

    baseline = {"date": OLD, "home": "Home", "away": "Away", "market": "1x2",
                "pick": "home", "avg_p": 75, "odds": 1.5}
    regular = dict(baseline, avg_p=65, odds=1.7)
    put(tmp_path, f"picks_morning_{OLD}.json", json.dumps([baseline]).encode())
    put(tmp_path, f"picks_{OLD}.json", json.dumps([regular]).encode())
    monkeypatch.setattr(tickets, "LOCALDATA", tmp_path)
    monkeypatch.setattr(replay, "LOCALDATA", tmp_path)
    before_rows = tickets.load_archived_picks()
    before_replay = replay.slate_generation()
    before_audit = audit.load_archived_picks_with_receipt(OLD, OLD, localdata=tmp_path)[0]
    archive_dated_artifacts(tmp_path, today=TODAY)
    assert tickets.load_archived_picks() == before_rows
    assert replay.slate_generation() == before_replay
    assert audit.load_archived_picks_with_receipt(OLD, OLD, localdata=tmp_path)[0] == before_audit
    assert len(_load_pick_rows(tmp_path)) == 2
    assert len(pick_archives(tmp_path)) == 1
    assert build_report(tmp_path)["window_days"] == [OLD]
    assert build_report(tmp_path)["n_archives"] == 1


def test_historical_shortlist_and_frozen_morning_lookup_use_archive(tmp_path, monkeypatch):
    from edgefactory.sources import theoddsapi
    from scripts import notify
    put(tmp_path, f"picks_morning_{OLD}.json", b"[]")
    archive_dated_artifacts(tmp_path, today=TODAY)
    monkeypatch.setattr(notify, "LOCALDATA", tmp_path)
    monkeypatch.setattr(theoddsapi, "LOCALDATA", tmp_path)
    assert notify._morning_baseline_file(OLD) == dated_artifact_path(tmp_path, f"picks_morning_{OLD}.json")
    assert theoddsapi._shortlist_file(OLD) == dated_artifact_path(tmp_path, f"picks_morning_{OLD}.json")


def test_archive_allowlist_persists_files_but_not_locks(tmp_path):
    from test_phase5_persistence_audit import _git, _seed_repo
    _seed_repo(tmp_path)
    paths = [f"localdata/archive/picks/2026/09/picks_{OLD}.json",
             "localdata/archive/.rollover.lock", "localdata/archive/picks/2026/09/.rollover-temp"]
    result = _git(tmp_path, "check-ignore", "--no-index", *paths, check=False)
    assert result.stdout.splitlines() == paths[1:]


def test_cached_archive_union_survives_restore_and_conflicts_preserve_inputs(tmp_path):
    from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo
    _seed_repo(tmp_path)
    module = _persistence_module()
    base = tmp_path / "localdata"
    name = f"picks_{OLD}.json"
    target = dated_archive_path(base, name)
    target.parent.mkdir(parents=True)
    target.write_bytes(b"[]")
    _git(tmp_path, "add", target.relative_to(tmp_path).as_posix())
    _git(tmp_path, "commit", "-qm", "archived evidence")
    # Pre-upgrade cache resurrected a duplicate at the old location.
    put(base, name, b"[]")
    extra = dated_archive_path(base, "picks_2026-09-02.json")
    extra.write_bytes(b"[1]")
    module.restore_committed_localdata(tmp_path)
    assert target.read_bytes() == b"[]" and extra.read_bytes() == b"[1]"
    assert dated_artifact_files(base, "picks_*.json") == [target, extra]
    target.write_bytes(b"different cache version")
    before = target.read_bytes()
    with pytest.raises(module.EvidenceMergeError, match="conflicting"):
        module.restore_committed_localdata(tmp_path)
    assert target.read_bytes() == before
    assert _git(tmp_path, "show", "HEAD:" + target.relative_to(tmp_path).as_posix()).stdout == "[]"


def test_daily_cli_archives_before_morning_parity_can_delete_evidence(tmp_path):
    from scripts.clean_localdata import main
    name = f"picks_morning_{OLD}.json"
    original = json.dumps([{"date": OLD, "home": "A", "away": "B"}]).encode()
    put(tmp_path, name, original)
    put(tmp_path, f"picks_{OLD}.json", original)
    assert main(["--today", TODAY.isoformat(), "--localdata", str(tmp_path)]) == 0
    assert dated_artifact_path(tmp_path, name).read_bytes() == original
    assert dated_artifact_path(tmp_path, f"picks_{OLD}.json").read_bytes() == original


def test_persistence_rolls_over_and_stages_archives_without_workflow_changes(tmp_path, monkeypatch):
    import subprocess

    from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo
    _seed_repo(tmp_path)
    module = _persistence_module()
    base = tmp_path / "localdata"
    name = f"picks_{OLD}.json"
    original = put(base, name, b"[]").read_bytes()
    _git(tmp_path, "add", "localdata/" + name)
    _git(tmp_path, "commit", "-qm", "original evidence")
    run = module._run
    network_commands = []

    def isolated_run(repo, *args, **kwargs):
        if args[0] in {"pull", "push"}:
            network_commands.append(args)
            return subprocess.CompletedProcess(args, 0, stdout=b"", stderr=b"")
        return run(repo, *args, **kwargs)

    monkeypatch.setattr(module, "_run", isolated_run)
    monkeypatch.setattr(module, "archive_dated_artifacts",
                        lambda root: archive_dated_artifacts(root, today=TODAY))
    outcome = module.persist_localdata(tmp_path, run_id="test-archive")
    assert outcome["status"] == "pushed"  # local stub, not a real push
    target = dated_archive_path(base, name)
    assert target.read_bytes() == original and not (base / name).exists()
    assert _git(tmp_path, "show", "HEAD:" + target.relative_to(tmp_path).as_posix()).stdout == "[]"
    assert network_commands == [("pull", "--rebase", "--autostash"), ("push",)]


def test_stale_pre_upgrade_head_and_archived_cache_conflict_fails_before_restore(tmp_path):
    from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo
    _seed_repo(tmp_path)
    base = tmp_path / "localdata"
    name = f"picks_{OLD}.json"
    put(base, name, b"[]")
    _git(tmp_path, "add", "localdata/" + name)
    _git(tmp_path, "commit", "-qm", "pre-archive head")
    archived = dated_archive_path(base, name)
    archived.parent.mkdir(parents=True)
    archived.write_bytes(b"different")
    with pytest.raises((ValueError, RuntimeError), match="conflicting"):
        _persistence_module().restore_committed_localdata(tmp_path)
    assert archived.read_bytes() == b"different" and (base / name).read_bytes() == b"[]"


def test_historical_git_ref_backfill_reads_the_archived_committed_version(tmp_path, monkeypatch):
    from test_phase5_persistence_audit import _git, _seed_repo

    import scripts.backfill_registry_slices as backfill
    _seed_repo(tmp_path)
    target = dated_archive_path(tmp_path / "localdata", f"picks_{OLD}.json")
    target.parent.mkdir(parents=True)
    target.write_text('[{"historical": true}]')
    _git(tmp_path, "add", target.relative_to(tmp_path).as_posix())
    _git(tmp_path, "commit", "-qm", "historical snapshot")
    target.write_text('[{"uncommitted": true}]')
    monkeypatch.setattr(backfill, "ROOT", tmp_path)
    assert backfill._picks_for_day("HEAD", OLD) == [{"historical": True}]


def test_multiyear_growth_stays_sharded_with_bounded_hot_directory(tmp_path):
    from datetime import timedelta
    start = date(2025, 1, 1)
    families = ("picks", "picks_morning", "source_health")
    for offset in range(400):
        day = start + timedelta(days=offset)
        for family in families:
            put(tmp_path, f"{family}_{day.isoformat()}.json", b"[]")
        archive_dated_artifacts(tmp_path, today=day)
    assert len(list(tmp_path.iterdir())) == 30 * len(families) + 1
    files = dated_artifact_files(tmp_path, "*.json")
    assert len(files) == 400 * len(families)
    assert all(p.read_bytes() == b"[]" for p in files)
    for directory in (tmp_path / "archive").glob("*/*/*"):
        assert len(list(directory.iterdir())) <= 31


def test_remine_no_match_receipts_and_card_snapshot_readers_preserve_cold_truth(tmp_path, monkeypatch):
    from edgefactory.sources import boggio
    from scripts import coverage_inventory, remine_backfill
    for module in (coverage_inventory, remine_backfill):
        monkeypatch.setattr(module, "LOCALDATA", tmp_path)
    receipt = {"source": "statarea", "date": OLD, "status": "no_matches_day"}
    put(tmp_path, f"remine_audit_{OLD}.jsonl", json.dumps(receipt).encode() + b"\n")
    snapshot = {"fixture_key": "immutable-fixture", "usable": True, "date": OLD}
    put(tmp_path, f"card_enrich_shadow_{OLD}.json", json.dumps({"snapshots": [snapshot]}).encode())
    inventory = {"sources": {"statarea": {"date_range": {"no_matches_days": [OLD]}}}}
    before = coverage_inventory._no_match_days()
    assert remine_backfill._hold_statarea(OLD, inventory, [], dry_run=True) == 1
    assert boggio.load_snapshots(tmp_path) == {"immutable-fixture": snapshot}
    archive_dated_artifacts(tmp_path, today=TODAY)
    assert coverage_inventory._no_match_days() == before == {"statarea": {OLD}}
    assert remine_backfill._hold_statarea(OLD, inventory, [], dry_run=True) == 1
    assert boggio.load_snapshots(tmp_path) == {"immutable-fixture": snapshot}


def test_printed_main_slice_seed_is_identical_after_archival(tmp_path, monkeypatch):
    from scripts import auto_tickets as tickets
    monkeypatch.setattr(tickets, "LOCALDATA", tmp_path)
    row = {"date": OLD, "home": "Alpha", "away": "Beta", "pick": "HOME", "bucket": "sample", "odds": 1.6}
    put(tmp_path, f"picks_{OLD}.json", json.dumps([row]).encode())
    put(tmp_path, f"auto_tickets_{OLD}.txt", b"   Alpha vs Beta HOME @ 1.6 (stated 75%)\n")
    # Keep this older printed card eligible, rather than the latest lane card.
    put(tmp_path, f"auto_tickets_{TODAY.isoformat()}.txt", b"No new positions\n")
    before, missing_before = tickets.seed_slice_ledger(
        settled={}, path=tmp_path / "before.jsonl", today_text=TODAY.isoformat())
    assert len(before) == 1 and missing_before == []
    archive_dated_artifacts(tmp_path, today=TODAY)
    after, missing_after = tickets.seed_slice_ledger(
        settled={}, path=tmp_path / "after.jsonl", today_text=TODAY.isoformat())
    assert after == before and missing_after == missing_before
    assert (tmp_path / "before.jsonl").read_bytes() == (tmp_path / "after.jsonl").read_bytes()
