#!/usr/bin/env python3
"""Preserve append-only Phase 5 evidence across cache restore and Git races.

The daily workflow's cache is an optimization, not the source of truth. Before
restoring the remaining tracked localdata, this helper unions the cached and
committed Phase 5 JSONL ledgers. At persistence time it resolves only
append-only Phase 5 JSONL rebase conflicts; any other conflict is left intact
for an explicit warning and the workflow artifact fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

APPEND_ONLY_JSONL_IDS = {
    "localdata/phase5_shadow/rows.jsonl": "row_id",
    "localdata/phase5_shadow/attempts.jsonl": "attempt_id",
    "localdata/phase5_activation/mutation_receipts.jsonl": "receipt_sha256",
}
PHASE5_CLEAN_EXCLUDES = (
    "/localdata/phase5_shadow/",
    "/localdata/phase5_activation/",
    "/localdata/phase5_reconciliation/",
    "/localdata/scored_candidate_shadow_*.jsonl",
)


class EvidenceMergeError(RuntimeError):
    """An append-only evidence file cannot be merged without ambiguity."""


def _run(
    repo: Path,
    *args: str,
    check: bool = False,
    env: dict[str, str] | None = None,
    input_data: bytes | None = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
        env=env,
    )


def _decode_output(value: bytes) -> str:
    return value.decode("utf-8", errors="replace").strip()


def _parse_jsonl(payload: bytes, *, path: str) -> list[tuple[str, dict[str, Any], bytes]]:
    records: list[tuple[str, dict[str, Any], bytes]] = []
    for line_number, raw_line in enumerate(payload.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceMergeError(
                f"{path} line {line_number} is not valid JSON; refusing evidence merge"
            ) from exc
        if not isinstance(value, dict):
            raise EvidenceMergeError(
                f"{path} line {line_number} is not a JSON object; refusing evidence merge"
            )
        records.append((raw_line.decode("utf-8"), value, raw_line))
    return records


def merge_jsonl_payloads(
    first: bytes,
    second: bytes,
    *,
    path: str,
) -> tuple[bytes, int]:
    """Return a stable, duplicate-free union; reject identity collisions.

    ``first`` remains the prefix (committed/upstream in current callers), then
    unseen rows from ``second`` are appended in their original order. Durable
    record IDs deduplicate byte-different encodings of the same event. If a
    record ID maps to different JSON objects, neither version is discarded.
    """
    identity_field = APPEND_ONLY_JSONL_IDS.get(path)
    if identity_field is None:
        raise EvidenceMergeError(f"{path} is not an approved append-only Phase 5 ledger")

    output: list[bytes] = []
    seen: dict[str, dict[str, Any]] = {}
    added = 0
    for payload in (first, second):
        for original_line, record, raw_line in _parse_jsonl(payload, path=path):
            identifier = record.get(identity_field)
            identity = (
                f"{identity_field}:{identifier}"
                if identifier not in (None, "")
                else "line-sha256:" + hashlib.sha256(raw_line).hexdigest()
            )
            previous = seen.get(identity)
            if previous is not None:
                if previous != record:
                    raise EvidenceMergeError(
                        f"{path} has conflicting records for {identity}; preserving both inputs"
                    )
                continue
            seen[identity] = record
            output.append(original_line.encode("utf-8"))
            added += 1

    merged = b"" if not output else b"\n".join(output) + b"\n"
    return merged, added


def _head_blob(repo: Path, path: str) -> bytes:
    result = _run(repo, "show", f"HEAD:{path}")
    return result.stdout if result.returncode == 0 else b""


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.phase5-merge.tmp")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def merge_cached_phase5_evidence(repo: Path | str) -> dict[str, int]:
    """Union cache-restored ledgers with HEAD before the workflow restores files."""
    repo = Path(repo)
    merged_counts: dict[str, int] = {}
    for relative, _identity_field in APPEND_ONLY_JSONL_IDS.items():
        path = repo / relative
        cached = path.read_bytes() if path.exists() else b""
        committed = _head_blob(repo, relative)
        if not cached and not committed:
            continue
        merged, count = merge_jsonl_payloads(committed, cached, path=relative)
        if merged != cached:
            _atomic_write(path, merged)
        merged_counts[relative] = count
    return merged_counts


def _tracked_localdata_paths(repo: Path) -> list[str]:
    result = _run(repo, "ls-files", "-z", "--", "localdata/")
    if result.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {_decode_output(result.stderr)}")
    return [os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def restore_committed_localdata(repo: Path | str) -> dict[str, Any]:
    """Restore ordinary tracked state without overwriting cached append-only evidence."""
    repo = Path(repo)
    try:
        merge_counts = merge_cached_phase5_evidence(repo)
    except (OSError, EvidenceMergeError) as exc:
        # Fail closed: do not check out or clean the Phase 5 directories below.
        # The untouched cache copy is still uploaded by the workflow artifact step.
        merge_counts = {"merge_warning": 1}
        print(f"::warning::Phase 5 cache/HEAD union was not applied: {exc}")

    restored: list[str] = []
    protected = set(APPEND_ONLY_JSONL_IDS)
    for relative in _tracked_localdata_paths(repo):
        if relative in protected:
            continue
        result = _run(repo, "checkout", "HEAD", "--", relative)
        if result.returncode != 0:
            raise RuntimeError(
                f"could not restore committed localdata file {relative}: "
                f"{_decode_output(result.stderr)}"
            )
        restored.append(relative)

    clean = _run(
        repo,
        "clean", "-fd", "localdata/",
        *sum((("-e", pattern) for pattern in PHASE5_CLEAN_EXCLUDES), ()),
    )
    if clean.returncode != 0:
        raise RuntimeError(f"git clean failed: {_decode_output(clean.stderr)}")
    return {
        "phase5_ledgers": merge_counts,
        "restored_tracked_files": len(restored),
        "clean_output": _decode_output(clean.stdout),
    }


def _unmerged_paths(repo: Path) -> list[str]:
    result = _run(repo, "diff", "--name-only", "--diff-filter=U", "-z")
    if result.returncode != 0:
        return []
    return [os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def _stage_blob(repo: Path, stage: int, path: str) -> bytes | None:
    result = _run(repo, "show", f":{stage}:{path}")
    return result.stdout if result.returncode == 0 else None


def resolve_phase5_jsonl_conflicts(repo: Path | str) -> tuple[bool, list[str], str | None]:
    """Resolve only allowlisted Phase 5 JSONL conflicts using index stages."""
    repo = Path(repo)
    paths = _unmerged_paths(repo)
    if not paths:
        return True, [], None
    unsupported = sorted(path for path in paths if path not in APPEND_ONLY_JSONL_IDS)
    if unsupported:
        return False, [], "unsupported conflicts: " + ", ".join(unsupported)

    merged_payloads: dict[str, bytes] = {}
    try:
        for path in paths:
            upstream = _stage_blob(repo, 2, path) or b""
            replayed = _stage_blob(repo, 3, path) or b""
            merged, _count = merge_jsonl_payloads(upstream, replayed, path=path)
            merged_payloads[path] = merged
    except EvidenceMergeError as exc:
        return False, [], str(exc)

    for relative, payload in merged_payloads.items():
        _atomic_write(repo / relative, payload)
    for relative in paths:
        staged = _run(repo, "add", "--", relative)
        if staged.returncode != 0:
            detail = _decode_output(staged.stderr)
            return False, [], f"could not stage merged evidence {relative}: {detail}"
    return True, paths, None


def _rebase_in_progress(repo: Path) -> bool:
    result = _run(repo, "rev-parse", "--git-path", "rebase-merge")
    if result.returncode == 0 and (repo / _decode_output(result.stdout)).exists():
        return True
    result = _run(repo, "rev-parse", "--git-path", "rebase-apply")
    return result.returncode == 0 and (repo / _decode_output(result.stdout)).exists()


def _index_and_worktree_clean(repo: Path) -> bool:
    return (
        _run(repo, "diff", "--quiet").returncode == 0
        and _run(repo, "diff", "--cached", "--quiet").returncode == 0
    )


def finish_rebase(repo: Path | str, *, max_steps: int = 32) -> tuple[bool, str | None]:
    """Continue a rebase, auto-merging only append-only Phase 5 evidence."""
    repo = Path(repo)
    for _ in range(max_steps):
        if not _rebase_in_progress(repo):
            return True, None
        conflicts = _unmerged_paths(repo)
        if conflicts:
            resolved, paths, reason = resolve_phase5_jsonl_conflicts(repo)
            if not resolved:
                return False, reason
            print("PHASE5_PERSISTENCE merged_rebase_conflicts=" + ",".join(paths))

        env = os.environ.copy()
        env["GIT_EDITOR"] = "true"
        continued = _run(repo, "rebase", "--continue", env=env)
        if continued.returncode == 0:
            continue
        if _unmerged_paths(repo):
            continue
        if _index_and_worktree_clean(repo) and _rebase_in_progress(repo):
            # The local patch was a byte/record duplicate of upstream. Skipping
            # its now-empty commit loses no evidence and avoids a false failure.
            skipped = _run(repo, "rebase", "--skip", env=env)
            if skipped.returncode == 0:
                continue
        detail = _decode_output(continued.stderr) or _decode_output(continued.stdout)
        return False, f"git rebase --continue failed: {detail}"
    return False, "rebase exceeded the bounded conflict-resolution step count"


def _warn_not_persisted(reason: str) -> None:
    print(
        "::warning::Pipeline state commit was not pushed. "
        "Phase 5 evidence is included in the always-uploaded artifact. "
        + reason
    )


def persist_localdata(
    repo: Path | str,
    *,
    run_id: str | None = None,
    max_push_attempts: int = 3,
) -> dict[str, Any]:
    """Commit, rebase with safe JSONL unions, and push without force."""
    repo = Path(repo)
    staged = _run(repo, "add", "-A", "localdata/")
    if staged.returncode != 0:
        reason = _decode_output(staged.stderr)
        _warn_not_persisted(f"git add failed: {reason}")
        return {"status": "not_persisted", "reason": reason}
    if _run(repo, "diff", "--cached", "--quiet").returncode == 0:
        print("PHASE5_PERSISTENCE no_localdata_changes")
        return {"status": "no_changes"}

    run_id = run_id or os.environ.get("GITHUB_RUN_ID", "local")
    commit = _run(repo, "commit", "-m", f"chore: persist pipeline state (run {run_id})")
    if commit.returncode != 0:
        reason = _decode_output(commit.stderr) or _decode_output(commit.stdout)
        _warn_not_persisted(f"git commit failed: {reason}")
        return {"status": "not_persisted", "reason": reason}

    for attempt in range(1, max_push_attempts + 1):
        pull = _run(repo, "pull", "--rebase", "--autostash")
        if pull.returncode != 0:
            if not _rebase_in_progress(repo):
                reason = _decode_output(pull.stderr) or _decode_output(pull.stdout)
                _warn_not_persisted(f"git pull --rebase failed: {reason}")
                return {"status": "not_persisted", "reason": reason}
            resolved, reason = finish_rebase(repo)
            if not resolved:
                _run(repo, "rebase", "--abort")
                _warn_not_persisted(reason or "Phase 5 rebase conflict was not safely mergeable")
                return {"status": "not_persisted", "reason": reason}

        pushed = _run(repo, "push")
        if pushed.returncode == 0:
            print(f"PHASE5_PERSISTENCE pushed attempt={attempt}")
            return {"status": "pushed", "attempt": attempt}
        push_error = _decode_output(pushed.stderr) or _decode_output(pushed.stdout)
        lower = push_error.lower()
        if not any(marker in lower for marker in ("non-fast-forward", "fetch first", "rejected")):
            _warn_not_persisted(f"git push failed: {push_error}")
            return {"status": "not_persisted", "reason": push_error}

    reason = f"push race persisted after {max_push_attempts} bounded synchronization attempts"
    _warn_not_persisted(reason)
    return {"status": "not_persisted", "reason": reason}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("restore", "persist"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args(argv)

    if args.action == "restore":
        result = restore_committed_localdata(args.repo)
        print(
            "PHASE5_PERSISTENCE restored "
            f"tracked_files={result['restored_tracked_files']} "
            f"phase5_ledgers={json.dumps(result['phase5_ledgers'], sort_keys=True)}"
        )
        return 0
    result = persist_localdata(args.repo, run_id=args.run_id)
    return 0 if result["status"] in {"pushed", "no_changes", "not_persisted"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
