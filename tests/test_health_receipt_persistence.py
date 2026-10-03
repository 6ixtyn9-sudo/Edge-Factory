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
    """A receipt written by the run cannot be pruned before state staging."""
    workflow = (ROOT / ".github" / "workflows" / "daily.yml").read_text()
    clean_at = workflow.index("git clean -fd localdata/")
    execute_at = workflow.index("name: Execute Autonomous Smart Schedule")
    state_commit_at = workflow.index("name: Persist pipeline state to git")
    add_at = workflow.index("git add -A localdata/", state_commit_at)
    assert clean_at < execute_at < state_commit_at < add_at
