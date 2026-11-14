#!/usr/bin/env python3
"""Run offline Phase 5 mutation checks and append a compact JSONL receipt."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECEIPTS = ROOT / "localdata" / "phase5_activation" / "mutation_receipts.jsonl"

CASES = (
    {
        "name": "zero_weight_mutation",
        "tests": [
            "tests/test_phase5_activation.py::test_zero_weight_mutation_invalidates_candidate_and_uses_incumbent",
        ],
        "mutation": "set the active candidate's vitibet_p coefficient to zero without updating its model key",
    },
    {
        "name": "certifier_and_shadow_isolation",
        "tests": [
            "tests/test_phase5_certifier.py::test_certifier_code_is_structurally_separate_from_pick_and_ticket_paths",
            "tests/test_phase5_shadow_isolation.py::test_shadow_ledger_cannot_vote_or_emit_picks",
            "tests/test_phase5_shadow_isolation.py::test_phase5_rows_cannot_create_acca_or_change_bank",
            "tests/test_phase5_shadow_isolation.py::test_warehouse_mining_input_ignores_phase5_directory_even_if_mutated",
        ],
        "mutation": "inject hostile shadow-shaped predictions and nested source files; a control vote is shown to emit, while shadow data remains excluded",
    },
    {
        "name": "immediate_kill_switch",
        "tests": [
            "tests/test_phase5_activation.py::test_revert_dry_run_activation_kill_switch_and_revert_use_exact_incumbent_fallback",
        ],
        "mutation": "activate a synthetic candidate, set kill_switch, and resolve again without process restart",
    },
    {
        "name": "fallback_determinism",
        "tests": [
            "tests/test_phase5_activation.py::test_revert_dry_run_activation_kill_switch_and_revert_use_exact_incumbent_fallback",
            "tests/test_phase5_activation.py::test_registry_tamper_and_active_baseline_mutation_fail_closed",
        ],
        "mutation": "repeat candidate resolution and tamper the active baseline reference; results remain stable or fail closed to the immutable incumbent",
    },
)


def _append_receipt(receipt: dict) -> None:
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    unsigned = dict(receipt)
    unsigned["receipt_sha256"] = hashlib.sha256(
        json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    line = json.dumps(unsigned, sort_keys=True, separators=(",", ":")) + "\n"
    with RECEIPTS.open("a", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def main() -> int:
    results = []
    for case in CASES:
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", *case["tests"]],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        summary = re.search(r"(\d+ passed(?:, [^\n]+)?)", completed.stdout)
        passed = completed.returncode == 0 and summary is not None
        results.append({
            "name": case["name"],
            "result": "pass" if passed else "fail",
            "tests": case["tests"],
            "test_summary": summary.group(1) if summary else "no pytest pass summary",
            "mutation": case["mutation"],
        })
        print(f"{case['name']}={'PASS' if passed else 'FAIL'}: {results[-1]['test_summary']}")
        if not passed:
            if completed.stdout:
                print(completed.stdout)
            if completed.stderr:
                print(completed.stderr, file=sys.stderr)
            return 1

    state_root = ROOT / "localdata" / "phase5_activation"
    active_path = state_root / "active_era.json"
    registry_path = state_root / "registry.jsonl"
    active_before = active_path.read_bytes()
    registry_before = registry_path.read_bytes()
    dry_run = subprocess.run(
        [
            sys.executable, "scripts/phase5_activate.py", "dry-run-revert",
            "--era-id", "phase5-forward-era-2026",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        dry_run_result = json.loads(dry_run.stdout)
    except json.JSONDecodeError:
        dry_run_result = {}
    dry_run_passed = (
        dry_run.returncode == 0
        and dry_run_result.get("status") == "not_yet_due"
        and active_path.read_bytes() == active_before
        and registry_path.read_bytes() == registry_before
    )
    print(
        "activation_dry_run_not_yet_due="
        f"{'PASS' if dry_run_passed else 'FAIL'}: {dry_run_result.get('status', 'invalid response')}"
    )
    if not dry_run_passed:
        if dry_run.stdout:
            print(dry_run.stdout)
        if dry_run.stderr:
            print(dry_run.stderr, file=sys.stderr)
        return 1

    receipt = {
        "schema": 1,
        "record_type": "phase5_mutation_verification_receipt",
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "baseline": "2,395 pre-Phase-5 full-suite tests; current source tree also runs the added Phase 5 tests",
        "offline": True,
        "source_calls_performed": False,
        "live_activation_performed": False,
        "synthetic_activation_tested": True,
        "cases": results,
        "activation_dry_run": {
            "result": "not_yet_due",
            "command": "phase5_activate.py dry-run-revert --era-id phase5-forward-era-2026",
            "active_config_unchanged": True,
            "append_only_registry_unchanged": True,
        },
        "overall_result": "pass",
    }
    _append_receipt(receipt)
    print(f"receipt_appended={RECEIPTS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
