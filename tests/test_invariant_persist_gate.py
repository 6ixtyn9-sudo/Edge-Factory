"""The invariant gate must stop contradictory state being committed.

Withholding the official-run marker is not a gate: the workflow's
persist step runs with ``if: always()`` and would push the bad state
anyway, which is how contradictory generated state shipped before.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DAILY = (ROOT / "scripts" / "daily.py").read_text()
WORKFLOW = (ROOT / ".github" / "workflows" / "daily.yml").read_text()
SENTINEL = ".invariant_failure"


def test_the_checker_runs_in_strict_mode():
    assert "check_run_invariants.py --date {target_date} --strict" in DAILY \
        or "--strict" in DAILY


def test_daily_writes_a_sentinel_on_invariant_errors():
    assert "INVARIANT_FAILURE_SENTINEL" in DAILY
    assert f'INVARIANT_FAILURE_SENTINEL = "{SENTINEL}"' in DAILY


def test_the_sentinel_lives_outside_localdata():
    """Otherwise it would be committed as part of the state it blocks."""
    assert "localdata" not in SENTINEL
    assert f'"localdata/{SENTINEL}"' not in DAILY


def test_each_run_clears_the_previous_sentinel():
    assert "def clear_invariant_sentinel" in DAILY
    main = DAILY.split("def main() -> None:", 1)[1][:400]
    assert "clear_invariant_sentinel()" in main, \
        "a stale sentinel would block an otherwise clean run"


def test_the_completion_marker_is_withheld_on_errors():
    assert "if not picks_only and invariants_clean:" in DAILY


def _persist_step():
    step = WORKFLOW.split("Persist pipeline state to git", 1)[1]
    if SENTINEL not in step.split("git add -A localdata/", 1)[0]:
        pytest.skip(
            "workflow guard not applied yet - see "
            "docs/operator/invariant-persist-gate.md (the agent cannot "
            "push workflow files without the workflows permission)")
    return step


def test_the_operator_patch_is_documented():
    """The one piece the agent cannot push must not be silently missing."""
    doc = ROOT / "docs" / "operator" / "invariant-persist-gate.md"
    assert doc.exists()
    text = doc.read_text()
    assert SENTINEL in text and "Persist pipeline state to git" in text


def test_the_persist_step_refuses_to_commit_bad_state():
    step = _persist_step()
    guard = step.split("git add -A localdata/", 1)[0]
    assert f"[ -f {SENTINEL} ]" in guard, \
        "the sentinel check must precede staging localdata"
    assert "exit 1" in guard


def test_the_guard_runs_before_any_commit():
    step = _persist_step()
    assert step.index(SENTINEL) < step.index("git commit")


def test_artifacts_are_still_uploaded_for_inspection():
    """Blocking the commit must not hide the evidence."""
    assert "upload-artifact" in WORKFLOW
    upload = WORKFLOW.split("Upload Pick Ledgers", 1)[1][:200]
    assert "if: always()" in upload


def test_run_soft_reports_its_status():
    sig = re.search(r"def run_soft\(.*?\) -> (\w+):", DAILY)
    assert sig and sig.group(1) == "bool"
