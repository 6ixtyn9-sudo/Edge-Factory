"""Thin artifacts are lossless recovery, not silent exclusions or a cache claim."""

import gzip
import json

import pytest
import yaml

from edgefactory import util
from test_phase5_persistence_audit import (
    WORKFLOW, _git, _large_decision_blob, _multipart_receipt_limits,
    _persistence_module, _seed_repo,
)


def published_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    remote = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-q", "--initial-branch=main", str(remote))
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-qu", "origin", "main")
    return repo


def bundle_path(repo):
    return repo / ".cache" / "edgefactory-reports"


def entries_by_path(manifest):
    return {entry["path"]: entry for entry in manifest["files"]}


def test_published_history_can_be_referenced_but_every_byte_is_reconstructible(tmp_path):
    repo = published_repo(tmp_path)
    module = _persistence_module()
    nested = repo / "localdata/phase5_reconciliation/nested.json"
    nested.parent.mkdir(parents=True, exist_ok=True)
    nested.write_bytes(b'{"frozen":true,"exact":[-0.0,1e-20]}\n')
    _git(repo, "add", "-f", "localdata")
    _git(repo, "commit", "-qm", "published evidence")
    _git(repo, "push", "-q", "origin", "main")
    original = nested.read_bytes()
    money = repo / "localdata/auto_tickets_state.json"
    money.write_bytes(b'{"bank":123.000001,"history":[],"open_slips":[]}\n')
    manifest = module.prepare_report_artifact(repo, bundle_path(repo), run_id="test")
    entries = entries_by_path(manifest)
    assert entries[str(nested.relative_to(repo))]["source"] == "git"
    assert entries[str(money.relative_to(repo))]["source"] == "artifact"
    assert manifest["totals"]["git_bytes"] >= len(original)
    restored = tmp_path / "recovered"
    module.restore_report_artifact(repo, bundle_path(repo), restored)
    assert (restored / nested.relative_to(repo)).read_bytes() == original
    assert (restored / money.relative_to(repo)).read_bytes() == money.read_bytes()
    assert nested.read_bytes() == original
    with pytest.raises(FileExistsError):
        module.restore_report_artifact(repo, bundle_path(repo), restored)


def test_unpushed_commit_is_not_a_durable_replacement_for_upload(tmp_path):
    repo = published_repo(tmp_path)
    path = repo / "localdata/phase5_reconciliation/new.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"not":"pushed"}')
    _git(repo, "add", "-f", "localdata")
    _git(repo, "commit", "-qm", "local commit from failed persist")
    manifest = _persistence_module().prepare_report_artifact(repo, bundle_path(repo))
    assert entries_by_path(manifest)[str(path.relative_to(repo))]["source"] == "artifact"
    assert manifest["published_git_commit"] != _git(repo, "rev-parse", "HEAD").stdout.strip()


def test_no_remote_means_full_payload_not_an_unverified_git_pointer(tmp_path):
    _seed_repo(tmp_path)
    manifest = _persistence_module().prepare_report_artifact(tmp_path, bundle_path(tmp_path))
    assert manifest["published_git_commit"] is None
    assert all(entry["source"] == "artifact" for entry in manifest["files"])


def test_large_text_is_lossless_gzip_once_and_duplicate_payloads_are_not_reuploaded(tmp_path):
    _seed_repo(tmp_path)
    root = tmp_path / "localdata"
    original = (b'{"exact":"  whitespace \\u00e9", "values":[-0.0,1e-20]}\n' * 40000)
    for name in ("first.json", "second.json"):
        (root / name).write_bytes(original)
    manifest = _persistence_module().prepare_report_artifact(tmp_path, bundle_path(tmp_path))
    entries = entries_by_path(manifest)
    one, two = entries["localdata/first.json"], entries["localdata/second.json"]
    assert one["file"] == two["file"] and one["encoding"] == "gzip"
    assert gzip.decompress((bundle_path(tmp_path) / one["file"]).read_bytes()) == original
    assert manifest["totals"]["duplicate_bytes"] == len(original)
    assert manifest["totals"]["payload_bytes"] < len(original) // 10
    restored = tmp_path / "recovered"
    _persistence_module().restore_report_artifact(tmp_path, bundle_path(tmp_path), restored)
    assert (restored / "localdata/first.json").read_bytes() == original
    assert (restored / "localdata/second.json").read_bytes() == original
    assert (root / "first.json").read_bytes() == original


def test_cache_only_shards_survive_independent_artifact_recovery_byte_exact(tmp_path, monkeypatch):
    _multipart_receipt_limits(monkeypatch)
    repo = published_repo(tmp_path)
    path = util.ticket_receipt_path(repo / "localdata", "auto_tickets_2026-10-27_decision.json")
    original = _large_decision_blob()
    util.write_ticket_receipt(path, original)
    manifest_bytes = path.read_bytes()
    _git(repo, "add", str(path.relative_to(repo)))
    _git(repo, "commit", "-qm", "published manifest only")
    _git(repo, "push", "-q", "origin", "main")
    parts = sorted(path.parent.glob(path.name + ".part-*"))
    manifest = _persistence_module().prepare_report_artifact(repo, bundle_path(repo))
    entries = entries_by_path(manifest)
    assert entries[str(path.relative_to(repo))]["source"] == "git"
    assert all(entries[str(p.relative_to(repo))]["source"] == "artifact" for p in parts)
    assert not manifest["unavailable_receipt_parts"]
    assert manifest["status"] == "BYTES_INVENTORIED_NOT_AUDITED"
    assert all((bundle_path(repo) / entries[str(p.relative_to(repo))]["file"]).stat().st_ino == p.stat().st_ino
               for p in parts)  # no second multi-GB shard allocation on the same filesystem
    # A cold clone needs no runner cache. Artifact + pinned Git are sufficient.
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", str(tmp_path / "origin.git"), str(clone))
    restored = tmp_path / "recovered"
    _persistence_module().restore_report_artifact(clone, bundle_path(repo), restored)
    canonical = restored / path.relative_to(repo)
    assert canonical.read_bytes() == manifest_bytes
    assert util.ticket_receipt_bytes(canonical) == original
    assert not [name for name in _git(repo, "ls-files").stdout.splitlines() if ".part-" in name]


def test_genuinely_missing_historic_shards_remain_explicitly_incomplete(tmp_path, monkeypatch):
    _multipart_receipt_limits(monkeypatch)
    _seed_repo(tmp_path)
    path = util.ticket_receipt_path(tmp_path / "localdata", "auto_tickets_2026-10-27_decision.json")
    util.write_ticket_receipt(path, _large_decision_blob())
    missing = next(path.parent.glob(path.name + ".part-*"))
    missing.unlink()
    manifest = _persistence_module().prepare_report_artifact(tmp_path, bundle_path(tmp_path))
    assert str(missing.relative_to(tmp_path)) in manifest["unavailable_receipt_parts"]
    restored = tmp_path / "recovered"
    _persistence_module().restore_report_artifact(tmp_path, bundle_path(tmp_path), restored)
    with pytest.raises(ValueError, match="invalid multipart"):
        util.ticket_receipt_bytes(restored / path.relative_to(tmp_path))


@pytest.mark.parametrize("damage", ["payload", "digest", "size", "path", "payload_path", "symlink"])
def test_bundle_recovery_fails_closed_on_corruption_or_unsafe_paths(tmp_path, damage):
    _seed_repo(tmp_path)
    module = _persistence_module()
    manifest = module.prepare_report_artifact(tmp_path, bundle_path(tmp_path))
    entry = next(e for e in manifest["files"] if e["source"] == "artifact")
    payload = bundle_path(tmp_path) / entry["file"]
    if damage == "payload":
        payload.write_bytes(b"damaged bytes")
    elif damage == "digest":
        entry["sha256"] = "0" * 64
    elif damage == "size":
        entry["size"] += 1
    elif damage == "path":
        entry["path"] = "localdata/../../outside.json"
    elif damage == "payload_path":
        entry["file"] = "../outside.json"
    else:
        payload.unlink()
        payload.symlink_to(tmp_path / "localdata/edges_consensus.json")
    (bundle_path(tmp_path) / "recovery_manifest.json").write_text(json.dumps(manifest))
    with pytest.raises((ValueError, OSError)):
        module.restore_report_artifact(tmp_path, bundle_path(tmp_path), tmp_path / "recovered")
    assert (tmp_path / "localdata/edges_consensus.json").read_text() == '{"edges":[]}\n'


def test_bundle_cannot_be_mixed_with_old_output_or_restored_into_live_evidence(tmp_path):
    _seed_repo(tmp_path)
    module = _persistence_module()
    module.prepare_report_artifact(tmp_path, bundle_path(tmp_path))
    with pytest.raises(FileExistsError):
        module.prepare_report_artifact(tmp_path, bundle_path(tmp_path))
    with pytest.raises(ValueError, match="scratch"):
        module.restore_report_artifact(tmp_path, bundle_path(tmp_path), tmp_path / "localdata/overwrite")


def test_manual_workflow_has_full_fallback_and_preserves_the_durability_barrier():
    # The manual deployment was applied; validate the installed workflow, not a
    # duplicate proposal that can drift after the next operational change.
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["run-autonomous-agent"]["steps"]
    names = [step["name"] for step in steps]
    normal = next(s for s in steps if s["name"] == "Upload Pick Ledgers & Reports as Artifacts")
    fallback = next(s for s in steps if s["name"] == "Upload full report recovery fallback")
    assert normal["with"]["compression-level"] == 0
    assert normal["with"]["retention-days"] == fallback["with"]["retention-days"] == 7
    assert "outcome == 'success'" in normal["if"]
    assert "outcome != 'success'" in fallback["if"]
    for pattern in _persistence_module().REPORT_ARTIFACT_PATTERNS:
        assert pattern in fallback["with"]["path"]
    assert names.index("Persist pipeline state to git (single source of truth)") < names.index("Prepare lossless report recovery bundle")
    assert names.index("Ticket decision replay parity (read-only, flag never gate)") > names.index(fallback["name"])
