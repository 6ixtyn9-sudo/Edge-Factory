"""Lossless history recovery, current finance preservation and fail-closed seal."""
import csv
import gzip
import io
import json
from pathlib import Path

import pytest

from edgefactory import prediction_history as h

DAY = '2026-10-20'


def write(root, name, rows):
    root.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    out = io.StringIO(newline='')
    w = csv.DictWriter(out, fields)
    w.writeheader()
    w.writerows(rows)
    (root / name).write_bytes(gzip.compress(out.getvalue().encode()))


def baseline(root):
    for source in ('scoutingstats', 'statarea', 'vitibet'):
        write(root, 'statarea.csv.gz' if source == 'statarea' else f'{source}_2026-08.csv.gz', [
            dict(date='2026-08-01', home=f'Historical home {i}', away='Away', p1='60')
            for i in range(340)])
    # Must NOT be merged: donor odds/Forebet/operating artifacts are not predictions.
    (root / 'enhancement_tickets_state.json').write_text('OLD BANK')
    (root / 'edges_consensus.json').write_text('OLD REGISTRY')
    (root / 'bzzoiro_odds_2026-08.csv.gz').write_bytes(b'not a prediction CSV')
    (root / 'forebet_2026-08.csv.gz').write_bytes(b'not a current source')


@pytest.fixture
def staged(tmp_path):
    root = tmp_path / 'localdata'
    root.mkdir()
    ops = {'enhancement_tickets_state.json': b'CURRENT BANK',
           'auto_tickets_state.json': b'MAIN BANK', 'edges_consensus.json': b'CURRENT REGISTRY',
           'autobets_enh_tickets_2026-10-20_reset.json': b'APPROVAL',
           'phase5_shadow/rows.jsonl': b'CURRENT AUDIT', 'warehouse.duckdb': b'CURRENT DB'}
    for name, raw in ops.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    write(root, 'scoutingstats_2026-08.csv.gz', [
        dict(date='2026-08-01', home='Historical home 0', away='Away', p1='65', hs='2'),
        dict(date='2026-08-01', home='New fixture', away='Away', p1='70', hs='')])
    h.prepare(tmp_path)
    return tmp_path, root, ops


def assert_ops(root, ops):
    for name, raw in ops.items():
        assert (root / name).read_bytes() == raw, name


def test_recovery_lossless_no_old_operational_state_or_price_files(staged):
    repo, root, ops = staged
    baseline(root)
    receipt = h.recover(repo, reference_hit=True, cutoff=DAY)
    assert_ops(root, ops)
    fields, rows = h._read(root / 'scoutingstats_2026-08.csv.gz')
    assert {'hs', 'p1'} <= set(fields)
    assert len(rows) == 342  # preserve the conflicting forecast AND latest-only fixture
    assert {r['p1'] for r in rows if r['home'] == 'Historical home 0'} == {'60', '65'}
    assert not (root / 'bzzoiro_odds_2026-08.csv.gz').exists()
    assert not (root / 'forebet_2026-08.csv.gz').exists()
    assert receipt['certification'].startswith('none')
    assert receipt['source_fixture_counts']['scoutingstats'] == 341
    assert h.check(repo)['status'] == 'history_completeness_verified'


@pytest.mark.parametrize('kind', ['cache_miss', 'partial_reference', 'corrupt', 'schema', 'symlink'])
def test_failed_reference_always_restores_current_tree(staged, kind):
    repo, root, ops = staged
    if kind != 'cache_miss':
        baseline(root)
        target = root / 'scoutingstats_2026-08.csv.gz'
        if kind == 'partial_reference':
            (root / 'vitibet_2026-08.csv.gz').unlink()
        elif kind == 'corrupt':
            target.write_bytes(b'not gzip')
        elif kind == 'schema':
            write(root, target.name, [{'date': '2026-08-01', 'home': 'Missing away'}])
        elif kind == 'symlink':
            target.unlink()
            target.symlink_to(root / 'vitibet_2026-08.csv.gz')
    with pytest.raises((ValueError, OSError)):
        h.recover(repo, reference_hit=kind != 'cache_miss', cutoff=DAY)
    assert_ops(root, ops)
    assert len(h._read(root / 'scoutingstats_2026-08.csv.gz')[1]) == 2
    assert not (root / h.RECEIPT).exists()


def test_no_staged_current_refuses_to_touch_data(tmp_path):
    baseline(tmp_path / 'localdata')
    with pytest.raises(ValueError, match='no staged'):
        h.recover(tmp_path, reference_hit=True, cutoff=DAY)
    assert (tmp_path / 'localdata/edges_consensus.json').read_text() == 'OLD REGISTRY'


def test_double_prepare_refused_and_reference_cache_is_exact(staged):
    repo, root, _ = staged
    root.mkdir()
    with pytest.raises(ValueError, match='snapshot exists'):
        h.prepare(repo)
    plan = json.loads((repo / '.cache/prediction-history/plan.json').read_text())
    assert plan['reference_key'] == 'localdata-v2-39371954018'


def test_seal_detects_missing_month_and_partial_truncation(staged):
    repo, root, _ = staged
    baseline(root)
    h.recover(repo, reference_hit=True, cutoff=DAY)
    target = root / 'vitibet_2026-08.csv.gz'
    fields, rows = h._read(target)
    write(root, target.name, rows[:20])
    with pytest.raises(ValueError, match='history loss'):
        h.check(repo)
    target.unlink()
    with pytest.raises(ValueError, match='history loss'):
        h.check(repo)


def test_repeated_recovery_is_idempotent_and_does_not_weaken_prior_seal(staged):
    repo, root, ops = staged
    baseline(root)
    h.recover(repo, reference_hit=True, cutoff=DAY)
    before = (root / 'scoutingstats_2026-08.csv.gz').read_bytes()
    h.prepare(repo)
    baseline(root)
    h.recover(repo, reference_hit=True, cutoff=DAY)
    assert (root / 'scoutingstats_2026-08.csv.gz').read_bytes() == before
    assert_ops(root, ops)
    # Losing a latest-only fixture cannot be disguised by restoring the old reference.
    fields, rows = h._read(root / 'scoutingstats_2026-08.csv.gz')
    write(root, 'scoutingstats_2026-08.csv.gz', [r for r in rows if r['home'] != 'New fixture'])
    h.prepare(repo)
    baseline(root)
    with pytest.raises(ValueError, match='history loss'):
        h.recover(repo, reference_hit=True, cutoff=DAY)
    assert_ops(root, ops)


def test_unsealed_cache_cannot_claim_complete(tmp_path):
    baseline(tmp_path / 'localdata')
    with pytest.raises(ValueError, match='unverified prediction cache'):
        h.check(tmp_path)


def test_noop_preserves_original_compressed_core_bytes(staged):
    repo, root, _ = staged
    current = repo / '.cache/prediction-history/current'
    baseline(current)
    original = (current / 'statarea.csv.gz').read_bytes()
    baseline(root)
    h.recover(repo, reference_hit=True, cutoff=DAY)
    assert (root / 'statarea.csv.gz').read_bytes() == original
