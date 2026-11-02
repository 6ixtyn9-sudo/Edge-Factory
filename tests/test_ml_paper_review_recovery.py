"""Recovery never resets frozen paper capital or publishes a premature freeze."""

import hashlib
import json
from copy import deepcopy
from datetime import timedelta

import pytest
from test_ml_paper import DAY, FREEZE, NOW, capture, context, pick, run_capture
from test_ml_paper_redteam import _git, _persistence_module, _seed_repo
from test_ml_paper_uniformity import legacy_draft

from edgefactory import ml_paper as mp


def next_capture(root):
    tomorrow = NOW + timedelta(days=1)
    return run_capture(root, dict(context([]), date=tomorrow.date().isoformat(),
                                  build_at=tomorrow.isoformat()), now=tomorrow)


@pytest.mark.parametrize('damage', ['json', 'checksum', 'schema'])
def test_corruption_quarantines_before_cutoff_without_early_or_late_selection(tmp_path, monkeypatch, damage):
    run_capture(tmp_path, context([pick(1), pick(2)]))
    path = mp.state_path(tmp_path)
    if damage == 'json':
        path.write_bytes(b'{broken-state')
    else:
        state = json.loads(path.read_bytes())
        if damage == 'checksum':
            state['pending_by_date'][DAY]['sha256'] = '0' * 64
        else:
            state['schema'] = 'unknown'
        path.write_text(json.dumps(state))
    original = path.read_bytes()

    def forbidden(*args, **kwargs):
        raise AssertionError('damaged day must not select or train')

    monkeypatch.setattr(mp, 'candidates', forbidden)
    monkeypatch.setattr(mp, 'learn', forbidden)
    assert run_capture(tmp_path, {}, now=NOW) is None
    assert path.read_bytes() == original
    assert not mp.receipt_path(tmp_path, DAY).exists()
    sha = hashlib.sha256(original).hexdigest()
    archive = tmp_path / f'autobets_ML_conflicts/draft_{DAY}.{sha}.bin'
    assert archive.read_bytes() == original
    sealed = run_capture(tmp_path, {}, now=FREEZE)
    assert sealed['status'] == 'missed_freeze_no_paper_bet'
    mp.validate_record(sealed, DAY)
    assert path.read_bytes() == original
    assert mp.performance(mp.receipts(tmp_path), lambda c: None)['paper_bank_units'] == 100


def test_acknowledged_corruption_recovers_only_next_day_and_keeps_receipt(tmp_path):
    path = mp.state_path(tmp_path)
    path.write_bytes(b'{bad')
    sealed = run_capture(tmp_path, {}, now=FREEZE)
    frozen = mp.receipt_path(tmp_path, DAY).read_bytes()
    assert run_capture(tmp_path, {}, now=FREEZE + timedelta(hours=1)) is None
    assert path.read_bytes() == b'{bad'
    pending = next_capture(tmp_path)
    assert pending['status'] == 'draft_not_yet_frozen'
    state = mp._read_state(tmp_path)
    assert set(state['pending_by_date']) == {pending['date']}
    assert mp.state_recovery_acknowledges(tmp_path, state, b'{bad')
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == frozen
    assert (tmp_path / sealed['draft_integrity_error']['quarantine']).read_bytes() == b'{bad'


@pytest.mark.parametrize('damage', ['quarantine', 'receipt_hash', 'unacknowledged_bytes'])
def test_tampered_or_unacknowledged_corruption_cannot_recover(tmp_path, damage):
    path = mp.state_path(tmp_path)
    path.write_bytes(b'{bad')
    sealed = run_capture(tmp_path, {}, now=FREEZE)
    if damage == 'quarantine':
        (tmp_path / sealed['draft_integrity_error']['quarantine']).write_bytes(b'changed')
    elif damage == 'receipt_hash':
        p = mp.receipt_path(tmp_path, DAY)
        row = json.loads(p.read_text());row['sha256'] = '0' * 64
        p.write_text(json.dumps(row))
    else:
        path.write_bytes(b'{different bad state')
    original = path.read_bytes()
    if damage == 'receipt_hash':
        with pytest.raises(ValueError):
            next_capture(tmp_path)
    else:
        assert next_capture(tmp_path) is None
    assert path.read_bytes() == original


def test_recovery_publication_failure_retains_original_and_allows_retry(tmp_path, monkeypatch):
    path = mp.state_path(tmp_path)
    path.write_bytes(b'{bad')
    run_capture(tmp_path, {}, now=FREEZE)
    original_save = mp._save_state

    def fail(*args):
        raise OSError('simulated disk failure')

    monkeypatch.setattr(mp, '_save_state', fail)
    with pytest.raises(OSError):
        next_capture(tmp_path)
    assert path.read_bytes() == b'{bad'
    monkeypatch.setattr(mp, '_save_state', original_save)
    assert next_capture(tmp_path)['status'] == 'draft_not_yet_frozen'


@pytest.mark.parametrize('legacy_damage', ['equal_time', 'invalid_json'])
def test_frozen_day_legacy_is_archived_and_does_not_block_later_days(tmp_path, legacy_damage):
    capture(tmp_path)
    frozen = mp.receipt_path(tmp_path, DAY).read_bytes()
    row = deepcopy(mp._read_state(tmp_path)['pending_by_date'][DAY])
    row['rejections']['different_payload'] = 1
    row['sha256'] = mp.digest({k:v for k,v in row.items() if k != 'sha256'})
    path, _ = legacy_draft(tmp_path, row)
    if legacy_damage == 'invalid_json':
        path.write_bytes(b'{old broken legacy')
    original = path.read_bytes()
    assert next_capture(tmp_path)['status'] == 'draft_not_yet_frozen'
    sha = hashlib.sha256(original).hexdigest()
    assert (tmp_path / f'autobets_ML_conflicts/legacy_superseded_{DAY}.{sha}.bin').read_bytes() == original
    assert not path.exists()
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == frozen


def test_invalid_frozen_receipt_does_not_authorize_discarding_legacy(tmp_path):
    capture(tmp_path)
    row = mp._read_state(tmp_path)['pending_by_date'][DAY]
    path, original = legacy_draft(tmp_path, row)
    mp.receipt_path(tmp_path, DAY).write_text('{}')
    with pytest.raises(ValueError):
        next_capture(tmp_path)
    assert path.read_bytes() == original


@pytest.mark.parametrize('offset', ['same', 'equivalent_timezone'])
def test_equal_capture_different_persisted_time_is_a_conflict(tmp_path, offset):
    row = run_capture(tmp_path, context([pick(1), pick(2)]))
    head = mp._read_state(tmp_path)
    cache = deepcopy(head)
    changed = cache['pending_by_date'][DAY]
    changed['draft_persisted_at'] = (NOW + timedelta(minutes=1)).isoformat()
    if offset == 'equivalent_timezone':
        changed['captured_at'] = NOW.astimezone(mp.LOCAL_TZ).isoformat()
    changed['sha256'] = mp.digest({k:v for k,v in changed.items() if k != 'sha256'})
    assert row['sha256'] != changed['sha256']
    with pytest.raises(ValueError, match='equal-capture-time'):
        mp.merge_pending_states(head, cache)


@pytest.mark.parametrize('tamper', ['none', 'quarantine', 'recovery_proof'])
def test_real_restore_accepts_only_receipt_bound_recovery(tmp_path, tamper):
    repo = tmp_path / 'repo';repo.mkdir();_seed_repo(repo)
    root = repo / 'localdata';path = mp.state_path(root)
    path.write_bytes(b'{bad')
    _git(repo, 'add', str(path.relative_to(repo)))
    _git(repo, 'commit', '-qm', 'corrupt pending store')
    sealed = run_capture(root, {}, now=FREEZE)
    next_capture(root)
    recovered = path.read_bytes()
    if tamper == 'quarantine':
        (root / sealed['draft_integrity_error']['quarantine']).write_bytes(b'not original')
    if tamper == 'recovery_proof':
        state = mp._read_state(root)
        next(iter(state['recoveries'].values()))['receipt_sha256'] = '0' * 64
        mp._save_state(root, state)
        recovered = path.read_bytes()
    _persistence_module().restore_committed_localdata(repo)
    marker = root / 'autobets_ML_integrity_block.json'
    if tamper != 'none':
        assert marker.exists()
        assert any(p.read_bytes() == recovered for p in (root / 'autobets_ML_conflicts').glob('*.json'))
    else:
        assert not marker.exists()
        assert path.read_bytes() == recovered
        assert mp.receipts(root) == [sealed]


def test_existing_integrity_block_is_never_cleared_by_recovery(tmp_path):
    mp.state_path(tmp_path).write_bytes(b'{bad')
    run_capture(tmp_path, {}, now=FREEZE)
    marker = tmp_path / 'autobets_ML_integrity_block.json'
    marker.write_text('{"unresolved":"frozen conflict"}')
    original = marker.read_bytes()
    with pytest.raises(ValueError, match='paper lane blocked'):
        next_capture(tmp_path)
    assert marker.read_bytes() == original
    assert mp.state_path(tmp_path).read_bytes() == b'{bad'


def test_recovery_preserves_real_prior_paper_losses_not_a_fresh_bank(tmp_path):
    frozen = capture(tmp_path)
    original = mp.receipt_path(tmp_path, DAY).read_bytes()
    mp.state_path(tmp_path).write_bytes(b'{bad')
    damaged_day = FREEZE + timedelta(days=1)
    missed = run_capture(tmp_path, {}, now=damaged_day)
    assert missed['status'] == 'missed_freeze_no_paper_bet'
    recovered_at = NOW + timedelta(days=2)
    row = run_capture(tmp_path, dict(context([]), date=recovered_at.date().isoformat(),
                                     build_at=recovered_at.isoformat()), now=recovered_at,
                      lookup=lambda c:(0,1))
    expected = 100 - sum(a['stake_units'] for a in frozen['accas'])
    assert expected < 100
    assert row['paper_bank_at_decision'] == pytest.approx(expected)
    assert row['paper_available_at_decision'] == pytest.approx(expected)
    assert row['paper_pending_reserved_at_decision'] == 0
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == original


def test_restore_can_retain_repaired_head_against_exact_old_damaged_cache(tmp_path):
    repo = tmp_path/'repo';repo.mkdir();_seed_repo(repo)
    root = repo/'localdata';path = mp.state_path(root)
    path.write_bytes(b'{bad')
    run_capture(root, {}, now=FREEZE)
    next_capture(root)
    expected = path.read_bytes()
    _git(repo,'add',str(path.relative_to(repo)))
    _git(repo,'commit','-qm','acknowledged recovered pending store')
    path.write_bytes(b'{bad')
    _persistence_module().restore_committed_localdata(repo)
    assert path.read_bytes() == expected
    assert not (root/'autobets_ML_integrity_block.json').exists()


def test_failed_superseded_legacy_archive_never_unlinks_original(tmp_path,monkeypatch):
    capture(tmp_path)
    frozen = mp.receipt_path(tmp_path, DAY).read_bytes()
    path, original = legacy_draft(tmp_path,mp._read_state(tmp_path)['pending_by_date'][DAY])

    def fail(*args):
        raise OSError('archive publication failed')

    monkeypatch.setattr(mp,'_archive_bytes',fail)
    with pytest.raises(OSError):
        next_capture(tmp_path)
    assert path.read_bytes() == original
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == frozen
