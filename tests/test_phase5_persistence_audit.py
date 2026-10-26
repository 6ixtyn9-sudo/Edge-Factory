from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from edgefactory.phase5_shadow import append_capture_attempt, append_shadow_rows

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "daily.yml"
LEDGER = "localdata/phase5_shadow/rows.jsonl"
ATTEMPTS = "localdata/phase5_shadow/attempts.jsonl"


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo, check=check,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def _configure(repo: Path) -> None:
    _git(repo, "config", "user.name", "Phase5 Persistence Test")
    _git(repo, "config", "user.email", "phase5-persistence-test@example.invalid")


def _append_fixture(root: Path, team: str, day: str = "2026-10-07") -> None:
    append_shadow_rows(
        "vitibet",
        [{
            "date": day,
            "home": f"{team} Home FC",
            "away": f"{team} Away FC",
            "p1": 0.7, "px": 0.2, "p2": 0.1,
            "kickoff": f"{day}T20:00:00Z",
        }],
        capture_day=day,
        captured_at=f"{day}T10:00:00Z",
        capture_context="official_daily_pipeline",
        root=root / "localdata",
    )


def _append_attempt(root: Path, actor: str, second: int) -> None:
    stamp = f"2026-10-07T10:00:{second:02d}Z"
    append_capture_attempt(
        "vitibet",
        capture_day="2026-10-07",
        status="ok",
        started_at=stamp,
        completed_at=stamp,
        source_status=actor,
        capture_context="official_daily_pipeline",
        rows_fetched=1,
        root=root / "localdata",
    )


def _seed_repo(root: Path) -> None:
    _git(root, "init", "-q", "--initial-branch=main")
    _configure(root)
    shutil.copy2(ROOT / ".gitignore", root / ".gitignore")
    _append_fixture(root, "Seed")
    localdata = root / "localdata"
    localdata.mkdir(exist_ok=True)
    (localdata / "edges_consensus.json").write_text('{"edges":[]}\n', encoding="utf-8")
    _git(root, "add", ".gitignore", LEDGER, "localdata/edges_consensus.json")
    _git(root, "commit", "-qm", "seed committed Phase 5 row")


def _persistence_module():
    name = "phase5_persistence_audit_module"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "phase5_persistence.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_first_capture_successful_commit_and_cache_loss_restore_are_isolated(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)

    committed = _git(repo, "show", f"HEAD:{LEDGER}").stdout.splitlines()
    assert len(committed) == 1
    assert _git(repo, "ls-files", LEDGER).stdout.strip() == LEDGER
    assert _git(repo, "check-ignore", "--no-index", "-q", LEDGER, check=False).returncode == 1

    # Simulate an empty/lost runner cache: Git restores the committed evidence.
    (repo / LEDGER).unlink()
    result = _persistence_module().restore_committed_localdata(repo)
    assert result["phase5_ledgers"][LEDGER] == 1
    assert len((repo / LEDGER).read_text(encoding="utf-8").splitlines()) == 1


def test_cache_restore_unions_committed_rows_and_preserves_untracked_phase5_evidence(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)

    # A newer cache contains an append that failed to reach Git on the prior
    # run. The merge must happen before tracked-file restoration or git clean.
    _append_fixture(repo, "Cached")
    _append_attempt(repo, "Cached", 3)
    attempts_path = repo / ATTEMPTS
    assert attempts_path.exists()
    assert _git(repo, "check-ignore", "--no-index", "-q", ATTEMPTS, check=False).returncode == 1

    candidate_path = repo / "localdata" / "scored_candidate_shadow_2026-10-08.jsonl"
    candidate_payload = '{"captured_at":"2026-10-08T10:00:00Z","candidate":"cached"}\n'
    candidate_path.write_text(candidate_payload, encoding="utf-8")
    reconciliation_path = (
        repo / "localdata" / "phase5_reconciliation" / "20261008T-incumbent-reconcile-01" / "audit.json"
    )
    reconciliation_payload = '{"status":"read_only_audit","preserved":true}\n'
    reconciliation_path.parent.mkdir(parents=True)
    reconciliation_path.write_text(reconciliation_payload, encoding="utf-8")

    # card_enrich receipts are intentionally unignored so persist_localdata can
    # commit them, but the restore-time git clean must not erase a cache copy
    # before the next capture has had a chance to use it.
    card_ledger = repo / "localdata" / "card_enrich_call_ledger.jsonl"
    card_ledger_payload = '{"charged":false,"family_remaining":31}\n'
    card_ledger.write_text(card_ledger_payload, encoding="utf-8")
    card_shadow = repo / "localdata" / "card_enrich_shadow_2026-10-08.json"
    card_shadow_payload = '{"schema":1,"snapshots":[]}\n'
    card_shadow.write_text(card_shadow_payload, encoding="utf-8")

    for evidence_path in (candidate_path, reconciliation_path, card_ledger, card_shadow):
        relative = evidence_path.relative_to(repo).as_posix()
        assert _git(repo, "check-ignore", "--no-index", "-q", relative, check=False).returncode == (0 if evidence_path == candidate_path else 1)

    stale_core = repo / "localdata" / "edges_consensus.json"
    stale_core.write_text('{"edges":[{"rule":"stale-cache"}]}\n', encoding="utf-8")

    result = _persistence_module().restore_committed_localdata(repo)
    rows = (repo / LEDGER).read_text(encoding="utf-8").splitlines()
    attempts = [json.loads(line) for line in attempts_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    assert "Cached Home FC" in "\n".join(rows)
    assert len(attempts) == 1 and attempts[0]["source_status"] == "Cached"
    assert stale_core.read_text(encoding="utf-8") == '{"edges":[]}\n'
    assert candidate_path.read_text(encoding="utf-8") == candidate_payload
    assert reconciliation_path.read_text(encoding="utf-8") == reconciliation_payload
    assert card_ledger.read_text(encoding="utf-8") == card_ledger_payload
    assert card_shadow.read_text(encoding="utf-8") == card_shadow_payload
    assert (repo / "localdata" / "phase5_shadow").exists()
    assert result["phase5_ledgers"][LEDGER] == 2
    assert result["phase5_ledgers"][ATTEMPTS] == 1


def test_concurrent_append_conflict_is_unioned_rebased_and_pushed(tmp_path):
    repo = tmp_path / "runner"
    repo.mkdir()
    _seed_repo(repo)

    bare = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "--initial-branch=main", str(bare))
    _git(repo, "remote", "add", "origin", str(bare))
    _git(repo, "push", "-q", "-u", "origin", "main")
    concurrent = tmp_path / "concurrent"
    _git(tmp_path, "clone", "-q", str(bare), str(concurrent))
    _configure(concurrent)

    # Two runner snapshots append to the same end position. Include a first-time
    # attempts.jsonl add/add conflict as well as a rows.jsonl append conflict.
    _append_fixture(repo, "Runner")
    _append_attempt(repo, "Runner", 1)
    _append_fixture(concurrent, "Concurrent")
    _append_attempt(concurrent, "Concurrent", 2)
    _git(concurrent, "add", "-A", "localdata/")
    _git(concurrent, "commit", "-qm", "concurrent forward capture")
    _git(concurrent, "push", "-q", "origin", "main")

    result = _persistence_module().persist_localdata(repo, run_id="runner-capture")
    assert result["status"] == "pushed"

    remote_rows = _git(repo, "show", f"origin/main:{LEDGER}").stdout
    assert remote_rows.count("Seed Home FC") == 1
    assert remote_rows.count("Runner Home FC") == 1
    assert remote_rows.count("Concurrent Home FC") == 1
    remote_attempts = [
        json.loads(line)
        for line in _git(repo, "show", f"origin/main:{ATTEMPTS}").stdout.splitlines()
    ]
    assert {record["source_status"] for record in remote_attempts} == {"Runner", "Concurrent"}
    assert _git(repo, "status", "--short").stdout.strip() == ""


def test_upload_artifact_patterns_cover_nested_phase5_evidence():
    yaml = WORKFLOW.read_text(encoding="utf-8")
    upload = yaml.split("- name: Upload Pick Ledgers & Reports as Artifacts", 1)[1]
    upload = upload.split("retention-days:", 1)[0]
    assert "localdata/*.json" in upload
    assert "localdata/phase5_shadow/**" in upload
    assert "localdata/phase5_activation/**" in upload
    assert "localdata/phase5_reconciliation/**" in upload
    assert "retention-days: 7" in yaml
    scored_candidates = yaml.split("- name: Upload Scored-Candidate Audit Ledgers", 1)[1]
    assert "localdata/scored_candidate_shadow_*.jsonl" in scored_candidates
    persistence = yaml.split("- name: Persist pipeline state to git", 1)[1]
    assert "scripts/phase5_persistence.py persist" in persistence
    assert "dropping regenerable state commit" not in persistence


@pytest.mark.parametrize("status,expected", [
    ("pushed", 0), ("no_changes", 0), ("not_persisted", 1), ("unexpected", 1),
])
def test_persistence_cli_only_reports_actual_publication_success(tmp_path, monkeypatch, status, expected):
    module = _persistence_module()
    calls = []

    def persist(repo, *, run_id):
        calls.append((repo, run_id))
        return {"status": status}

    monkeypatch.setattr(module, "persist_localdata", persist)
    assert module.main(["persist", "--repo", str(tmp_path), "--run-id", "publication-test"]) == expected
    assert calls == [(tmp_path, "publication-test")]


def test_rejected_git_push_fails_workflow_cli_and_preserves_local_evidence(tmp_path):
    repo = tmp_path / "runner"
    repo.mkdir()
    _seed_repo(repo)
    bare = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "--initial-branch=main", str(bare))
    _git(repo, "remote", "add", "origin", str(bare))
    _git(repo, "push", "-q", "-u", "origin", "main")
    before = _git(bare, "rev-parse", "main").stdout
    hook = bare / "hooks/pre-receive"
    hook.write_text("#!/bin/sh\necho 'test publication rejection' >&2\nexit 1\n")
    hook.chmod(0o755)
    _append_fixture(repo, "Unpublished")
    evidence = (repo / LEDGER).read_bytes()

    cli = subprocess.run([
        sys.executable, str(ROOT / "scripts/phase5_persistence.py"),
        "persist", "--repo", str(repo), "--run-id", "rejected-publication",
    ], text=True, capture_output=True)
    assert cli.returncode == 1, cli.stdout + cli.stderr
    assert "Pipeline state commit was not pushed" in cli.stdout
    assert "PHASE5_PERSISTENCE pushed" not in cli.stdout
    assert _git(bare, "rev-parse", "main").stdout == before
    assert (repo / LEDGER).read_bytes() == evidence
    assert b"Unpublished Home FC" in evidence  # retained for always-uploaded artifacts


def test_raw_candidate_updates_stay_in_cache_not_git(tmp_path):
    repo = tmp_path / 'runner'
    repo.mkdir()
    _seed_repo(repo)
    relative = 'localdata/scored_candidate_shadow_2026-10-24.jsonl'
    raw = repo / relative
    raw.write_text('old tracked snapshot\n')
    _git(repo, 'add', '-f', relative)
    _git(repo, 'commit', '-qm', 'legacy raw snapshot')
    raw.write_text('new raw evidence that may exceed GitHub blob limits\n')
    new_raw = repo / 'localdata/scored_candidate_shadow_2026-10-25.jsonl'
    new_raw.write_text('new day evidence\n')
    assert _persistence_module().persist_localdata(repo)['status'] == 'no_changes'
    assert _git(repo, 'show', f'HEAD:{relative}').stdout == 'old tracked snapshot\n'
    assert raw.read_text().startswith('new raw evidence')
    assert new_raw.read_text() == 'new day evidence\n'
    assert _git(repo, 'diff', '--cached', '--name-only').stdout == ''


def test_terminal_push_rejection_is_not_retried_and_keeps_detail(tmp_path, monkeypatch):
    repo = tmp_path / 'runner'
    repo.mkdir()
    _seed_repo(repo)
    _append_fixture(repo, 'Unpublished')
    module = _persistence_module()
    real_run = module._run
    pushes = []
    def run(repo, *args, **kwargs):
        if args[0] == 'pull':
            return subprocess.CompletedProcess(args, 0, b'', b'')
        if args[0] == 'push':
            pushes.append(args)
            return subprocess.CompletedProcess(args, 1, b'', b'remote: GH001 file exceeds 100 MB\n! [remote rejected] main (pre-receive hook declined)')
        return real_run(repo, *args, **kwargs)
    monkeypatch.setattr(module, '_run', run)
    result = module.persist_localdata(repo)
    assert len(pushes) == 1
    assert 'GH001' in result['reason']
    assert 'push race' not in result['reason']


def test_exhausted_push_race_keeps_last_rejection(tmp_path, monkeypatch):
    repo = tmp_path / 'runner'
    repo.mkdir()
    _seed_repo(repo)
    _append_fixture(repo, 'Unpublished')
    module = _persistence_module()
    real_run = module._run
    def run(repo, *args, **kwargs):
        if args[0] == 'pull':
            return subprocess.CompletedProcess(args, 0, b'', b'')
        if args[0] == 'push':
            return subprocess.CompletedProcess(args, 1, b'', b'! [rejected] main (fetch first); diagnostic retained')
        return real_run(repo, *args, **kwargs)
    monkeypatch.setattr(module, '_run', run)
    result = module.persist_localdata(repo, max_push_attempts=2)
    assert '2 bounded' in result['reason']
    assert 'diagnostic retained' in result['reason']


def test_transient_upstream_error_is_retried_in_place(tmp_path, monkeypatch):
    """A remote 500 must not turn a finished settlement step into a dead run.

    2026-10-25: `git push` was rejected with "remote: Internal Server Error".
    The pushed state was correct and complete; the run only had to try again.
    """
    repo = tmp_path / 'runner'
    repo.mkdir()
    _seed_repo(repo)
    _append_fixture(repo, 'Unpublished')
    module = _persistence_module()
    real_run = module._run
    pushes = []

    def run(repo, *args, **kwargs):
        if args[0] == 'pull':
            return subprocess.CompletedProcess(args, 0, b'', b'')
        if args[0] == 'push':
            pushes.append(args)
            if len(pushes) < 3:
                return subprocess.CompletedProcess(
                    args, 1, b'', b'remote: Internal Server Error\n'
                    b'! [remote rejected] main -> main (Internal Server Error)')
            return subprocess.CompletedProcess(args, 0, b'', b'')
        return real_run(repo, *args, **kwargs)

    monkeypatch.setattr(module, '_run', run)
    result = module.persist_localdata(repo, push_backoff=(0, 0, 0))
    assert result['status'] == 'pushed' and result['attempt'] == 3
    assert len(pushes) == 3


def test_exhausted_transient_failure_is_named_and_not_a_race(tmp_path, monkeypatch):
    repo = tmp_path / 'runner'
    repo.mkdir()
    _seed_repo(repo)
    _append_fixture(repo, 'Unpublished')
    module = _persistence_module()
    real_run = module._run

    def run(repo, *args, **kwargs):
        if args[0] == 'pull':
            return subprocess.CompletedProcess(args, 0, b'', b'')
        if args[0] == 'push':
            return subprocess.CompletedProcess(
                args, 1, b'', b'remote: Internal Server Error')
        return real_run(repo, *args, **kwargs)

    monkeypatch.setattr(module, '_run', run)
    result = module.persist_localdata(repo, max_push_attempts=2, push_backoff=(0, 0))
    assert result['status'] == 'not_persisted'
    assert 'transient push failure' in result['reason']
    assert 'push race' not in result['reason']
    assert 'Internal Server Error' in result['reason']


@pytest.mark.parametrize('source', ['scoutingstats', 'vitibet'])
def test_committed_schedule_recovery_overrides_stale_runner_cache(tmp_path, source):
    repo = tmp_path / 'runner'
    repo.mkdir()
    _seed_repo(repo)
    relative = f'localdata/schedule_{source}_2026-10.csv.gz'
    destination = repo / relative
    shutil.copy2(ROOT / relative, destination)
    expected = destination.read_bytes()
    _git(repo, 'add', relative)
    _git(repo, 'commit', '-qm', 'preserve original source schedule evidence')
    destination.write_bytes(b'stale runner cache')
    _persistence_module().restore_committed_localdata(repo)
    assert destination.read_bytes() == expected
    destination.unlink()
    _persistence_module().restore_committed_localdata(repo)
    assert destination.read_bytes() == expected


def test_queued_workflow_resolves_requested_branch_before_cache_restore():
    import yaml

    workflow = yaml.safe_load(WORKFLOW.read_text())
    assert workflow['concurrency'] == {'group': 'edge-factory-main', 'cancel-in-progress': False}
    for job_name in ('run-autonomous-agent', 'regression-tests'):
        steps = workflow['jobs'][job_name]['steps']
        checkout = next(i for i, s in enumerate(steps) if s.get('uses') == 'actions/checkout@v4')
        assert steps[checkout]['with']['ref'] == '${{ github.ref }}'
        assert 'github.sha' not in str(steps[checkout])
        for i, step in enumerate(steps):
            if step.get('uses') == 'actions/cache/restore@v4' or 'phase5_persistence.py restore' in step.get('run', ''):
                assert checkout < i
    # The copy/paste replacement must not reintroduce the old event-SHA race.
    doc = (ROOT / 'docs/operator/POST-FOREBET-RECOVERY.md').read_text()
    replacement = yaml.safe_load(doc.split('```yaml\n', 1)[1].rsplit('\n```', 1)[0])
    for job_name in ('run-autonomous-agent', 'regression-tests'):
        checkout = next(s for s in replacement['jobs'][job_name]['steps']
                        if s.get('uses') == 'actions/checkout@v4')
        assert checkout['with']['ref'] == '${{ github.ref }}'


@pytest.mark.parametrize('relative', [
    'localdata/enhancement_tickets_state.json', 'localdata/auto_tickets_state.json',
])
def test_queued_old_sha_new_frozen_cache_race_fixed_by_branch_checkout(tmp_path, relative):
    """Real Git reproduction: never make the financial guard accept unknown stakes."""
    publisher = tmp_path / 'publisher'
    publisher.mkdir()
    _seed_repo(publisher)
    state = dict(base_pct=100., bank=39.0372, cycle_base=100., history=[], events=[],
                 open_slips=[], frozen_by_date={})
    (publisher / relative).write_text(json.dumps(state))
    _git(publisher, 'add', relative)
    _git(publisher, 'commit', '-qm', 'state when next workflow event was queued')
    event_sha = _git(publisher, 'rev-parse', 'HEAD').stdout.strip()
    bare = tmp_path / 'origin.git'
    _git(tmp_path, 'init', '-q', '--bare', '--initial-branch=main', str(bare))
    _git(publisher, 'remote', 'add', 'origin', str(bare))
    _git(publisher, 'push', '-qu', 'origin', 'main')
    stale, fresh = tmp_path / 'event-checkout', tmp_path / 'branch-checkout'
    for runner in (stale, fresh):
        _git(tmp_path, 'clone', '-q', str(bare), str(runner))
        _git(runner, 'checkout', '-q', '--detach', event_sha)

    frozen = dict(state, open_slips=[dict(date='2026-10-26', staked_pct=4.8796,
        accas=[dict(stake_pct=4.8796, odds=2.41, legs=[
            dict(match='Alpha vs Beta', market='match_over_15', odds=1.30),
            dict(match='Gamma vs Delta', market='match_over_25', odds=1.85)])])],
        frozen_by_date={'2026-10-26': dict(frozen_at='2026-10-26T11:54:14+02:00', final=True)})
    payload = json.dumps(frozen).encode()
    (publisher / relative).write_bytes(payload)
    _git(publisher, 'add', relative)
    _git(publisher, 'commit', '-qm', 'preceding run persists its frozen slip')
    _git(publisher, 'push', '-q', 'origin', 'main')
    committed_sha = _git(publisher, 'rev-parse', 'HEAD').stdout.strip()

    # Former default checkout: the event SHA plus a cache from the preceding run.
    (stale / relative).write_bytes(payload)
    with pytest.raises(_persistence_module().EvidenceMergeError, match='divergent enhancement financial histories'):
        _persistence_module().restore_committed_localdata(stale)
    assert (stale / relative).read_bytes() == payload

    # Explicit branch ref: resolve current origin/main BEFORE cache extraction.
    _git(fresh, 'fetch', '-q', 'origin', '+refs/heads/main:refs/remotes/origin/main')
    _git(fresh, 'checkout', '-q', '-B', 'main', 'refs/remotes/origin/main')
    assert _git(fresh, 'rev-parse', 'HEAD').stdout.strip() == committed_sha != event_sha
    (fresh / relative).write_bytes(payload)
    _append_fixture(fresh, 'Cached evidence')
    _persistence_module().restore_committed_localdata(fresh)
    retained = json.loads((fresh / relative).read_bytes())
    assert retained == frozen
    assert retained['bank'] == state['bank'] and retained['history'] == state['history']
    assert retained['frozen_by_date']['2026-10-26']['final'] is True
    assert 'Cached evidence Home FC' in (fresh / LEDGER).read_text()

    # A genuinely different cached stake remains fatal even at the latest tip.
    divergent = json.loads(payload)
    divergent['open_slips'][0]['accas'][0]['stake_pct'] += 1
    (fresh / relative).write_text(json.dumps(divergent))
    with pytest.raises(_persistence_module().EvidenceMergeError):
        _persistence_module().restore_committed_localdata(fresh)
    assert json.loads((fresh / relative).read_text()) == divergent
