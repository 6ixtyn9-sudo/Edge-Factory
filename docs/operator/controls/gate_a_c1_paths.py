#!/usr/bin/env python3
"""C1: isolated ignore/staging layout control, not an index publisher.

No dependencies beyond Python and Git. All writes/staging occur in a temporary
repository; no clean, providers, recorder, export or operational state. It
proves path separation only: size/count admission and crash/commit coordination
remain future implementation controls. Run from any directory.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

IGNORE_ADDITION = """!localdata/ml_consensus_index/
localdata/ml_consensus_index/*
!localdata/ml_consensus_index/v1/
localdata/ml_consensus_index/v1/*
!localdata/ml_consensus_index/v1/compact-index_20??-??-??_0[1-8].json
"""


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="gate-a-c1-") as td:
        root = Path(td)

        def git(*args: str) -> str:
            return subprocess.check_output(["git", *args], cwd=root, text=True)

        git("init", "--quiet")
        # Copy the real ignore baseline read-only; append the exact proposed block
        # only in this temporary repository. Do not repeat localdata/* after
        # the real existing exceptions, which would revoke unrelated allowlists.
        baseline = Path(__file__).resolve().parents[3] / ".gitignore"
        (root / ".gitignore").write_text(
            baseline.read_text(encoding="utf-8").rstrip("\n") + "\n" + IGNORE_ADDITION,
            encoding="utf-8",
        )
        bulk = "localdata/ml_consensus_audit/v1/2026-10-09"
        index = "localdata/ml_consensus_index/v1"
        checks = []

        def put(name: str, payload: str) -> None:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload, encoding="utf-8")

        for n in range(1, 10):
            base = f"{bulk}/build-{n:02d}"
            put(f"{base}/build-manifest.json", json.dumps({
                "layout_control_only": True, "filler": "x" * (16384 if n == 9 else 64),
            }) + "\n")
            put(f"{base}/records-000001.jsonl", "{}\n")
            put(f"{base}/reservation.json", "{}\n")
            put(f"{base}/owner.lock", "")
        for n in (1, 9):
            for name in ("build-manifest.json", "records-000001.jsonl",
                         "reservation.json", "owner.lock"):
                checks.append((f"{bulk}/build-{n:02d}/{name}", True))
        # Generic names are NOT admitted slot names. Both remain ignored.
        put(f"{bulk}/build-01/compact-index.json", "{}\n")
        put(f"{index}/compact-index.json", "{}\n")
        checks.extend([(f"{bulk}/build-01/compact-index.json", True),
                       (f"{index}/compact-index.json", True)])
        expected = []
        for n in range(1, 9):
            path = f"{index}/compact-index_2026-10-09_{n:02d}.json"
            put(path, json.dumps({"layout_control_only": True, "slot": n}) + "\n")
            expected.append(path)
            checks.append((path, False))
        for name, payload in (("compact-index_2026-10-09_09.json", "{}\n"),
                              ("candidate_oversized.json", "x" * 16384),
                              ("transaction.json", "{}\n"), ("publisher.lock", "")):
            put(f"{index}/{name}", payload)
            checks.append((f"{index}/{name}", True))

        print("PER-FILE git check-ignore -q (before staging)")
        for path, should_ignore in checks:
            rc = subprocess.run(["git", "check-ignore", "-q", path], cwd=root).returncode
            assert rc in (0, 1), (path, rc)
            assert (rc == 0) == should_ignore, path
            print(f"{'IGNORED' if rc == 0 else 'STAGEABLE'} {path}")
        print("git add -A -n localdata/")
        dry_run = git("add", "-A", "-n", "localdata/")
        print(dry_run, end="")
        assert sorted(dry_run.splitlines()) == sorted(f"add '{p}'" for p in expected)
        git("add", "-A", "localdata/")
        staged = git("diff", "--cached", "--name-only").splitlines()
        assert sorted(staged) == sorted(expected), staged
        print("PASS: 9 detailed manifests ignored (one >8 KiB); exactly 8 compact indices staged.")
        print("PASS: slot 09, generic compact-index.json, candidates, records and controls ignored.")
        print("SCOPE: layout only; no size admission, concurrency, crash recovery or commit barrier proof.")


if __name__ == "__main__":
    main()
