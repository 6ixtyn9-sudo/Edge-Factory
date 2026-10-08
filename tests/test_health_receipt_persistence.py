"""Runtime receipt allowlists and workflow ordering are load-bearing."""
from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _is_ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", path], cwd=ROOT, check=False,
    )
    return result.returncode == 0


def test_health_and_probe_receipts_are_stageable_not_ignored():
    assert not _is_ignored("localdata/source_health_2099-01-01.json")
    assert not _is_ignored("localdata/source_health_state.json")
    assert not _is_ignored("localdata/betminer_probe_2099-01-01.json")
    assert _is_ignored("localdata/unallowlisted_runtime_blob.json")


def test_cleanup_precedes_run_and_state_commit_follows_run():
    """Restore/clean stays before execution; persistence staging stays after it."""
    workflow = (ROOT / ".github" / "workflows" / "daily.yml").read_text()
    helper = (ROOT / "scripts" / "phase5_persistence.py").read_text()
    restore_at = workflow.index("name: Restore committed data")
    execute_at = workflow.index("name: Execute Autonomous Smart Schedule")
    state_commit_at = workflow.index("name: Persist pipeline state to git")
    persist_call_at = workflow.index("scripts/phase5_persistence.py persist", state_commit_at)
    restore_logic_at = helper.index("def restore_committed_localdata")
    clean_at = helper.index('"clean", "-fd", "localdata/"', restore_logic_at)
    persist_logic_at = helper.index("def persist_localdata")
    add_at = helper.index('"add", "-A", "localdata/"', persist_logic_at)
    assert restore_at < execute_at < state_commit_at < persist_call_at
    assert clean_at > restore_logic_at
    assert add_at > persist_logic_at
