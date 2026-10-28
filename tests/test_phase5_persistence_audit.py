from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from edgefactory.phase5_shadow import append_capture_attempt, append_shadow_rows
from edgefactory.util import ticket_receipt_path, ticket_receipt_bytes, ticket_receipt_files, encode_ticket_receipt

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

    executed = _git(repo, "rev-parse", "HEAD").stdout.strip()
    result = _persistence_module().persist_localdata(repo, run_id="runner-capture")
    assert result["status"] == "pushed"
    message = _git(repo, "log", "-1", "--format=%B").stdout
    assert f"pre_persist_head={executed}" in message
    assert "verified_results_sha256=" in message
    assert "earlier subprocess revisions not inferred" in message
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() != executed

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


def _decision_receipt_blob(status='frozen', stamp='2026-10-27T09:00:00+02:00', **extra):
    import hashlib
    payload = dict(schema=1, status=status, context=dict(lane='main', date='2026-10-27', build_at=stamp), **extra)
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    return json.dumps(dict(payload, sha256=digest)).encode()


def test_cached_untracked_ticket_decision_survives_existing_restore(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    path = repo / 'localdata/auto_tickets_2026-10-27_decision.json'
    blob = _decision_receipt_blob()
    path.write_bytes(blob)
    _persistence_module().restore_committed_localdata(repo)
    compact = ticket_receipt_path(repo / 'localdata', path.name)
    assert not path.exists() and ticket_receipt_bytes(compact) == blob
    assert _git(repo, 'check-ignore', '--no-index', '-q', str(compact.relative_to(repo)), check=False).returncode == 1
    assert _git(repo, 'check-ignore', '--no-index', '-q', str(path.relative_to(repo)), check=False).returncode == 0


def test_cached_frozen_receipt_replaces_draft_only_for_independently_retained_freeze(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    module = _persistence_module()
    relative = 'localdata/auto_tickets_2026-10-27_decision.json'
    path = repo / relative
    path.write_bytes(_decision_receipt_blob('draft'))
    _git(repo, 'add', '-f', relative)
    _git(repo, 'commit', '-qm', 'draft audit')
    frozen = _decision_receipt_blob()
    path.write_bytes(frozen)
    state = dict(frozen_by_date={'2026-10-27': {'frozen_at': '2026-10-27T09:00:00+02:00'}})
    canonical = ticket_receipt_path(repo / 'localdata', path.name)
    destination = str(canonical.relative_to(repo))
    assert module._retain_ticket_decisions(repo, {module.MAIN_STATE: json.dumps(state).encode()}) == {
        destination: encode_ticket_receipt(canonical, frozen)}
    # The audit receipt itself can NEVER authorize finance or a freeze.
    assert module._retain_ticket_decisions(repo, {module.MAIN_STATE: b'{}'}) == {
        destination: encode_ticket_receipt(canonical, _decision_receipt_blob('draft'))}
    assert [ticket_receipt_bytes(p) for p in ticket_receipt_files(repo / 'localdata','auto_tickets',conflicts=True)] == [frozen]


def test_divergent_frozen_decisions_are_quarantined_not_auto_merged(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    relative = 'localdata/auto_tickets_2026-10-27_decision.json'
    path = repo / relative
    committed = _decision_receipt_blob()
    path.write_bytes(committed)
    _git(repo, 'add', '-f', relative)
    _git(repo, 'commit', '-qm', 'frozen audit')
    cached = _decision_receipt_blob(unrecognized_extra='different retained evidence')
    path.write_bytes(cached)
    _persistence_module().restore_committed_localdata(repo)
    assert not path.exists()
    assert ticket_receipt_bytes(ticket_receipt_path(repo / 'localdata', path.name)) == committed
    assert [ticket_receipt_bytes(p) for p in ticket_receipt_files(repo / 'localdata','auto_tickets',conflicts=True)] == [cached]


def test_operator_applied_decision_report_step_reuses_existing_artifacts_and_persistence(tmp_path):
    import yaml
    # The operator applied the workflow separately; this PR does not edit it.
    # Check the applied command, documented step and existing artifact coverage.
    doc = (ROOT / 'HANDOVER.md').read_text()
    step = yaml.safe_load(doc.split('```yaml\n', 1)[1].split('\n```', 1)[0])[0]
    assert 'scripts/replay_harness.py --decision-parity > localdata/replay_parity.json' in step['run']
    assert 'scripts/replay_harness.py --decision-parity > localdata/replay_parity.json' in WORKFLOW.read_text()
    assert step['continue-on-error'] is True
    assert 'exit "$result"' in step['run']
    assert 'localdata/*.json' in WORKFLOW.read_text()
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    for relative in ('localdata/phase5_reconciliation/ticket_decisions/autobets_enh_tickets_2026-10-27_decision.json.gz', 'localdata/replay_parity.json'):
        assert _git(repo, 'check-ignore', '--no-index', '-q', relative, check=False).returncode == 1


@pytest.mark.parametrize('committed_gzip', [False, True])
@pytest.mark.parametrize('candidate_status', ['identical', 'divergent_frozen', 'draft', 'invalid'])
def test_cross_format_cached_receipts_cannot_bypass_committed_freeze(tmp_path, committed_gzip, candidate_status):
    from edgefactory.util import write_ticket_receipt
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    base = repo / 'localdata'
    name = 'auto_tickets_2026-10-27_decision.json'
    canonical = ticket_receipt_path(base, name)
    legacy = base / name
    committed_path, cached_path = (canonical, legacy) if committed_gzip else (legacy, canonical)
    committed = _decision_receipt_blob()
    write_ticket_receipt(committed_path, committed)
    # Legacy files were tracked before the storage migration.
    _git(repo, 'add', '-f', str(committed_path.relative_to(repo)))
    financial = base / 'auto_tickets_state.json'
    financial_raw = json.dumps(dict(bank=123, history=[], open_slips=[], frozen_by_date={}), indent=2).encode()
    financial.write_bytes(financial_raw)
    _git(repo, 'add', str(financial.relative_to(repo)))
    _git(repo, 'commit', '-qm', 'committed frozen evidence and bank')
    cached = {
        'identical': committed,
        'divergent_frozen': _decision_receipt_blob(other='cached, not authoritative'),
        'draft': _decision_receipt_blob(status='draft'),
        'invalid': b'{broken',
    }[candidate_status]
    write_ticket_receipt(cached_path, cached)
    _persistence_module().restore_committed_localdata(repo)
    assert not legacy.exists()
    assert ticket_receipt_bytes(canonical) == committed
    assert financial.read_bytes() == financial_raw
    conflicts = ticket_receipt_files(base, 'auto_tickets', conflicts=True)
    if candidate_status in ('invalid', 'divergent_frozen'):
        assert cached in [ticket_receipt_bytes(p) for p in conflicts]
    else:
        assert not conflicts
    snapshot = {p: p.read_bytes() for p in base.rglob('*') if p.is_file()}
    _persistence_module().restore_committed_localdata(repo)
    assert snapshot == {p: p.read_bytes() for p in base.rglob('*') if p.is_file()}


@pytest.mark.parametrize('committed_gzip', [False, True])
@pytest.mark.parametrize('authorized', [False, True])
def test_cross_format_draft_upgrade_still_requires_independent_financial_freeze(tmp_path, committed_gzip, authorized):
    from edgefactory.util import write_ticket_receipt
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    base = repo / 'localdata'
    name = 'auto_tickets_2026-10-27_decision.json'
    canonical, legacy = ticket_receipt_path(base, name), base / name
    head_path, cache_path = (canonical, legacy) if committed_gzip else (legacy, canonical)
    draft, frozen = _decision_receipt_blob(status='draft'), _decision_receipt_blob()
    write_ticket_receipt(head_path, draft)
    _git(repo, 'add', '-f', str(head_path.relative_to(repo)))
    _git(repo, 'commit', '-qm', 'committed draft')
    write_ticket_receipt(cache_path, frozen)
    finance = {'localdata/auto_tickets_state.json': json.dumps(dict(
        frozen_by_date={'2026-10-27': {'frozen_at': '2026-10-27T09:00:00+02:00'}})).encode()} if authorized else {}
    retained = _persistence_module()._retain_ticket_decisions(repo, finance)
    assert ticket_receipt_bytes(canonical, raw=retained[str(canonical.relative_to(repo))]) == (frozen if authorized else draft)
    assert bool(ticket_receipt_files(base, 'auto_tickets', conflicts=True)) is not authorized


def test_compressed_evidence_is_covered_by_existing_cache_clean_and_artifact_paths(tmp_path):
    from fnmatch import fnmatch
    from edgefactory.util import write_ticket_receipt
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    path = ticket_receipt_path(repo / 'localdata', 'autobets_enh_tickets_2026-10-27_decision.json')
    # Complete real hash-checked receipt; its lane must match its ENH filename.
    payload = json.loads(_decision_receipt_blob())
    payload['context']['lane'] = 'enh'
    payload.pop('sha256')
    import hashlib
    payload['sha256'] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    original = json.dumps(payload).encode()
    write_ticket_receipt(path, original)
    _persistence_module().restore_committed_localdata(repo)
    assert ticket_receipt_bytes(path) == original
    relative = path.relative_to(repo).as_posix()
    assert _git(repo, 'check-ignore', '--no-index', '-q', relative, check=False).returncode == 1
    import yaml
    workflow = yaml.safe_load(WORKFLOW.read_text())
    steps = workflow['jobs']['pipeline']['steps'] if 'pipeline' in workflow['jobs'] else next(iter(workflow['jobs'].values()))['steps']
    report_step = next(s for s in steps if s.get('with', {}).get('name') == 'EdgeFactory-Reports')
    assert any(fnmatch(relative, pattern) for pattern in report_step['with']['path'].splitlines())
    cache_steps = [s for s in steps if 'actions/cache' in s.get('uses', '')]
    assert any(any(fnmatch(relative, pattern.rstrip('/') + '/**') for pattern in s.get('with', {}).get('path', '').splitlines()) for s in cache_steps)


@pytest.mark.parametrize('committed_gzip', [False, True])
def test_corrupt_gzip_cache_is_quarantined_byte_exactly(tmp_path, committed_gzip):
    from edgefactory.util import write_ticket_receipt
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    base = repo / 'localdata'
    name = 'auto_tickets_2026-10-27_decision.json'
    canonical = ticket_receipt_path(base, name)
    head = canonical if committed_gzip else base / name
    original = _decision_receipt_blob()
    write_ticket_receipt(head, original)
    _git(repo, 'add', '-f', str(head.relative_to(repo)))
    _git(repo, 'commit', '-qm', 'committed receipt')
    canonical.parent.mkdir(parents=True, exist_ok=True)
    damaged = b'not a valid gzip stream'
    canonical.write_bytes(damaged)
    _persistence_module().restore_committed_localdata(repo)
    assert ticket_receipt_bytes(canonical) == original
    assert [ticket_receipt_bytes(p) for p in ticket_receipt_files(base, 'auto_tickets', conflicts=True)] == [damaged]


def test_divergent_untracked_format_aliases_remain_visible_as_a_conflict(tmp_path):
    from edgefactory.util import write_ticket_receipt
    repo = tmp_path / 'repo'
    repo.mkdir()
    _seed_repo(repo)
    base = repo / 'localdata'
    name = 'auto_tickets_2026-10-27_decision.json'
    first, second = _decision_receipt_blob(first=True), _decision_receipt_blob(second=True)
    (base / name).write_bytes(first)
    canonical = ticket_receipt_path(base, name)
    write_ticket_receipt(canonical, second)
    _persistence_module().restore_committed_localdata(repo)
    assert ticket_receipt_bytes(canonical) in (first, second)
    conflicts = ticket_receipt_files(base, 'auto_tickets', conflicts=True)
    assert conflicts
    assert {ticket_receipt_bytes(canonical), *(ticket_receipt_bytes(p) for p in conflicts)} == {first, second}


def _approved_freeze_fixture(repo, *, lane='main', seed=True):
    import copy
    import auto_tickets as at
    if seed:
        _seed_repo(repo)
    module = _persistence_module()
    relative = module.MAIN_STATE if lane == 'main' else module.ENH_STATE
    prefix = 'auto_tickets' if lane == 'main' else 'autobets_enh_tickets'
    day, stamp = '2026-10-28', '2026-10-28T10:13:23+02:00'
    plan = [{'legs':[dict(match='Alpha vs Beta',pick='over',market='match_over_25',odds=1.4),
                     dict(match='Gamma vs Delta',pick='under',market='match_under_35',odds=1.5)],
             'odds':2.1,'stake_pct':25.}]
    head = dict(base_pct=100., bank=100., cycle_base=100., history=[],events=[],
                open_slips=[],frozen_by_date={},integrity_recovery={'pending_cached_freeze':dict(
                 status='approved',date=day,source_run_id='40647275279',source_head='abc',
                 frozen_minute='2026-10-28T10:13',card=[[[l['match'],l['pick'],l['market'],l['odds']]
                                                     for l in a['legs']] for a in plan])})
    (repo/relative).write_text(json.dumps(head))
    card = repo/'localdata'/f'{prefix}_{day}.txt'
    card.write_text('OLD DRAFT')
    _git(repo,'add',relative,str(card.relative_to(repo)))
    _git(repo,'commit','-qm','explicit approved freeze recovery, unchanged money')
    cache=copy.deepcopy(head)
    cache['open_slips']=[dict(date=day,accas=plan,staked_pct=25.)]
    cache['frozen_by_date']={day:dict(frozen_at=stamp,final=True,lock_source='state')}
    (repo/relative).write_text(json.dumps(cache))
    context=dict(lane=lane,date=day,build_at='2026-10-28T10:13:23.123456+02:00',bank_total=100.,bank_eff=100.)
    payload=dict(schema=1,status='frozen',context=context,plan=plan,card_identity=at.ticket_card_identity(plan),
                 execution_provenance=dict(run_id='40647275279',checkout_head_at_capture='abc'))
    payload['sha256']=at._decision_digest(payload)
    legacy=repo/'localdata'/f'{prefix}_{day}_decision.json'
    legacy.write_text(json.dumps(payload))
    text='ENHANCEMENT TICKETS\nAlpha vs Beta @ 1.40\nGamma vs Delta @ 1.50\nFROZEN AT 10:13 - FINAL\n'
    card.write_text(text)
    return module,relative,head,cache,legacy,card,text


@pytest.mark.parametrize('lane',['main','enh'])
def test_approved_freeze_recovers_from_existing_cache_without_recut_or_history_change(tmp_path,lane):
    repo=tmp_path/'repo';repo.mkdir()
    module,relative,head,cache,legacy,card,text=_approved_freeze_fixture(repo,lane=lane)
    expected=json.loads(legacy.read_text())
    module.restore_committed_localdata(repo)
    recovered=json.loads((repo/relative).read_text())
    for field in ('bank','base_pct','cycle_base','history','events'):
        assert recovered[field]==head[field]
    assert recovered['open_slips']==cache['open_slips']
    assert recovered['frozen_by_date']==cache['frozen_by_date']
    assert recovered['integrity_recovery']['pending_cached_freeze']['status']=='recovered'
    assert card.read_text()==text
    assert not legacy.exists()
    canonical=ticket_receipt_path(repo/'localdata',legacy.name)
    assert json.loads(ticket_receipt_bytes(canonical))==expected
    assert not ticket_receipt_files(repo/'localdata','auto_tickets' if lane=='main' else 'autobets_enh_tickets',conflicts=True)
    # Commit the recovery, then a normal restore is a read/reprint, not a recut.
    _git(repo,'add','-A','localdata');_git(repo,'commit','-qm','recovered original freeze')
    before=(repo/relative).read_bytes(),card.read_bytes(),canonical.read_bytes()
    module.restore_committed_localdata(repo)
    assert before==((repo/relative).read_bytes(),card.read_bytes(),canonical.read_bytes())


@pytest.mark.parametrize('damage',['no_approval','bank','history','other_lock','other_position','stake','card',
                                    'receipt_hash','source_run','source_head','second','text','missing_receipt',
                                    'missing_lock','missing_state','bad_total','acca_price','legacy_lock',
                                    'committed_frozen_text','lane','date','context_bank','context_free'])
def test_approved_freeze_recovery_refuses_unknown_changes_before_any_checkout(tmp_path,damage):
    import auto_tickets as at
    repo=tmp_path/'repo';repo.mkdir()
    module,relative,head,cache,receipt,card,text=_approved_freeze_fixture(repo)
    if damage=='no_approval':
        head['integrity_recovery'].clear();(repo/relative).write_text(json.dumps(head))
        _git(repo,'add',relative);_git(repo,'commit','-qm','no recovery authorization')
    if damage=='committed_frozen_text':
        card.write_text('FROZEN AT 07:00 - FINAL');_git(repo,'add',str(card.relative_to(repo)))
        _git(repo,'commit','-qm','existing committed frozen text')
        card.write_text(text)
    if damage=='missing_lock': cache['frozen_by_date'].clear()
    if damage=='legacy_lock': (repo/'localdata'/'auto_tickets_2026-10-28.frozen').write_text('existing freeze')
    if damage=='bad_total': cache['open_slips'][0]['staked_pct']=float('nan')
    if damage=='acca_price': cache['open_slips'][0]['accas'][0]['odds']=100.
    if damage=='bank': cache['bank']+=1
    if damage=='history': cache['history']=[dict(date='2026-10-27',staked_pct=1.,returned_pct=0.,accas=[])]
    if damage=='other_lock': cache['frozen_by_date']['2026-10-27']={}
    if damage=='other_position': cache['open_slips'].append(dict(date='2026-10-29',accas=[]))
    if damage=='stake': cache['open_slips'][0]['accas'][0]['stake_pct']+=1
    if damage=='card': cache['open_slips'][0]['accas'][0]['legs'][0]['match']='Other vs Club'
    if damage in ('receipt_hash','source_run','source_head','second','lane','date','context_bank','context_free'):
        payload=json.loads(receipt.read_text());payload.pop('sha256')
        if damage=='source_run': payload['execution_provenance']['run_id']='wrong'
        if damage=='source_head': payload['execution_provenance']['checkout_head_at_capture']='wrong'
        if damage=='second': payload['context']['build_at']='2026-10-28T10:13:24.123456+02:00'
        if damage=='lane': payload['context']['lane']='enh'
        if damage=='date': payload['context']['date']='2026-10-29'
        if damage=='context_bank': payload['context']['bank_total']+=1
        if damage=='context_free': payload['context']['bank_eff']+=1
        payload['sha256']='broken' if damage=='receipt_hash' else at._decision_digest(payload)
        receipt.write_text(json.dumps(payload))
    if damage=='text': card.write_text('different draft')
    if damage=='missing_receipt': receipt.unlink()
    (repo/relative).write_text(json.dumps(cache))
    if damage=='missing_state': (repo/relative).unlink()
    before={p:p.read_bytes() for p in (repo/'localdata').rglob('*') if p.is_file()}
    with pytest.raises(module.EvidenceMergeError): module.restore_committed_localdata(repo)
    assert before=={p:p.read_bytes() for p in (repo/'localdata').rglob('*') if p.is_file()}



def test_both_recovery_lanes_validate_before_changing_any_file(tmp_path):
    repo=tmp_path/'repo';repo.mkdir()
    module,*_=_approved_freeze_fixture(repo,lane='enh')
    _,relative,_,cache,*_=_approved_freeze_fixture(repo,lane='main',seed=False)
    cache['bank']+=1
    (repo/relative).write_text(json.dumps(cache))
    before={p:p.read_bytes() for p in (repo/'localdata').rglob('*') if p.is_file()}
    with pytest.raises(module.EvidenceMergeError,match='unapproved financial change'):
        module.restore_committed_localdata(repo)
    assert before=={p:p.read_bytes() for p in (repo/'localdata').rglob('*') if p.is_file()}


def test_current_run_recovery_approvals_do_not_change_any_committed_financial_field():
    module=_persistence_module()
    for relative in (module.MAIN_STATE,module.ENH_STATE):
        committed=json.loads(_git(ROOT,'show',f'HEAD:{relative}').stdout)
        working=json.loads((ROOT/relative).read_text())
        assert module._financial_fingerprint(committed)==module._financial_fingerprint(working)
