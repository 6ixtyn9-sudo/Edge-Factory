"""Recover prediction CSV history without rolling back operational state.

Called by the existing persistence helper/workflow, not a miner or registry.
The runner temporarily restores an exact historical Actions cache at its original
path/version; only allowlisted prediction CSV rows may leave that donor tree.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import os
import re
import shutil
from datetime import date, timedelta
from pathlib import Path

SOURCES = ('zulubet', 'statarea', 'vitibet', 'scoutingstats', 'prosoccer', 'betclan',
           'bzzoiro', 'predictz', 'windrawwin', 'soccervista', 'bettingclosed',
           'freesupertips', 'afootballreport')
PATTERN = re.compile(r'(' + '|'.join(SOURCES) + r')(?:_(\d{4}-\d{2}))?\.csv\.gz$')
REFERENCE_KEY = 'localdata-v2-39371954018'
KEYS = 'prediction_history_keys.json.gz'
RECEIPT = 'prediction_history_guard.json'


def _atomic(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.history.tmp')
    tmp.write_bytes(raw)
    os.replace(tmp, path)


def _read(path):
    if path.is_symlink():
        raise ValueError(f'prediction symlink refused: {path.name}')
    with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(set(fields)) != len(fields) or not {'date', 'home', 'away'} <= set(fields):
            raise ValueError(f'invalid prediction schema: {path.name}')
        rows = list(reader)
    if any(None in r for r in rows):
        raise ValueError(f'extra CSV cells: {path.name}')
    return fields, [{k: v or '' for k, v in r.items()} for r in rows]


def _files(root):
    return sorted(p for p in root.glob('*.csv.gz') if (m := PATTERN.fullmatch(p.name))
                  and (m[2] is not None or m[1] in ('zulubet', 'statarea')))


def _inventory(root, cutoff):
    """Stable FULL raw-name fixture keys; no fuzzy/width-limited row collapse.

    Scores/prices can settle/update without deleting a historical fixture.
    Full prediction rows (including conflicting forecasts) are preserved by
    the separate lossless merge, never resolved here in favour of a pass.
    """
    date.fromisoformat(cutoff)
    identities, coverage = {}, {}
    split = (date.fromisoformat(cutoff) - timedelta(days=28)).isoformat()
    for path in _files(root):
        source = PATTERN.fullmatch(path.name)[1]
        _, rows = _read(path)
        keys = identities.setdefault(source, set())
        dates = []
        train = set()
        for row in rows:
            day = row['date'][:10]
            try:
                valid = date.fromisoformat(day).isoformat() == day
            except ValueError:
                valid = False
            if not valid or day >= cutoff or not row['home'] or not row['away']:
                continue
            key = hashlib.sha256(json.dumps([day, row['home'], row['away']],
                                            ensure_ascii=False).encode()).hexdigest()
            keys.add(key)
            dates.append(day)
            if '2026-06-13' <= day < split:
                train.add(key)
        coverage[path.name] = {'source': source, 'rows': len(rows),
                               'earliest': min(dates) if dates else None,
                               'latest': max(dates) if dates else None,
                               'train_unique': len(train)}
    return identities, coverage


def prepare(repo):
    repo = Path(repo)
    stage = repo / '.cache/prediction-history'
    current = stage / 'current'
    if current.exists():
        raise ValueError('previous recovery snapshot exists; refuse to overwrite it')
    if not (repo / 'localdata').is_dir() or (repo / 'localdata').is_symlink():
        raise ValueError('current localdata directory missing or symlinked')
    stage.mkdir(parents=True, exist_ok=True)
    _atomic(stage / 'plan.json', json.dumps({'reference_key': REFERENCE_KEY}).encode())
    os.replace(repo / 'localdata', current)
    return {'status': 'current_operational_state_staged', 'reference_key': REFERENCE_KEY}


def recover(repo, *, reference_hit, cutoff=None):
    """Always restore CURRENT state, even when donor download/validation fails."""
    repo = Path(repo)
    stage = repo / '.cache/prediction-history'
    current, donor = stage / 'current', repo / 'localdata'
    if not current.is_dir():
        raise ValueError('no staged current state; no recovery performed')
    cutoff = cutoff or date.today().isoformat()
    outputs = stage / 'outputs'
    try:
        if outputs.exists():
            shutil.rmtree(outputs)
        if not reference_hit:
            raise ValueError(f'exact reference cache {REFERENCE_KEY} was not restored')
        reference, coverage = _inventory(donor, cutoff)
        # Sanity check the known reference, NOT statistical certification.
        for source in ('scoutingstats', 'statarea', 'vitibet'):
            cells = [v for v in coverage.values() if v['source'] == source]
            if sum(v['train_unique'] for v in cells) < 340:
                raise ValueError(f'reference lacks retained training history: {source}')
        outputs.mkdir(exist_ok=True)
        inserted = {}
        for old in _files(donor):
            fields, old_rows = _read(old)
            latest = current / old.name
            latest_fields, latest_rows = _read(latest) if latest.exists() else ([], [])
            fields = list(dict.fromkeys(latest_fields + fields))
            result, seen = [], set()
            # Lossless exact-row union: keep forecast/result conflicts for the
            # shared miner's quarantine. Never pick the version with better ROI.
            for row in latest_rows + old_rows:
                values = tuple(row.get(k, '') for k in fields)
                if values not in seen:
                    seen.add(values)
                    result.append(values)
            inserted[old.name] = len(result) - len({tuple(r.get(k, '') for k in fields) for r in latest_rows})
            if latest.exists() and not inserted[old.name] and fields == latest_fields:
                continue  # preserve byte-identical committed core CSVs on a no-op
            text = io.StringIO(newline='')
            writer = csv.writer(text)
            writer.writerow(fields)
            writer.writerows(result)
            _atomic(outputs / old.name, gzip.compress(text.getvalue().encode(), mtime=0))
    finally:
        # No old bank/registry/ticket/warehouse/ledger is allowed out of donor.
        if donor.exists():
            shutil.rmtree(donor)
        os.replace(current, donor)
    for output in _files(outputs):
        os.replace(output, donor / output.name)
    merged, _ = _inventory(donor, cutoff)
    for source, keys in reference.items():
        if not keys <= merged.get(source, set()):
            raise ValueError(f'recovery lost reference fixtures: {source}')
    previous = donor / KEYS
    if previous.exists():
        old_keys = json.loads(gzip.decompress(previous.read_bytes()))
        _check_keys(merged, old_keys['keys'])
    baseline = {'schema': 1, 'cutoff': cutoff, 'reference_key': REFERENCE_KEY,
                'keys': {s: sorted(keys) for s, keys in merged.items()}}
    _atomic(donor / KEYS, gzip.compress(json.dumps(baseline).encode(), mtime=0))
    receipt = {'schema': 1, 'reference_key': REFERENCE_KEY, 'cutoff': cutoff,
               'run_id': os.environ.get('GITHUB_RUN_ID'),
               'source_fixture_counts': {s: len(k) for s, k in merged.items()},
               'reference_files': coverage, 'inserted_rows': inserted,
               'operational_state': 'current tree restored; only prediction CSVs merged',
               'certification': 'none; existing miner/activation gates still required'}
    _atomic(donor / RECEIPT, json.dumps(receipt, indent=2).encode())
    return receipt


def _check_keys(actual, expected):
    missing = {s: len(set(keys) - actual.get(s, set())) for s, keys in expected.items()}
    missing = {s: n for s, n in missing.items() if n}
    if missing:
        raise ValueError('prediction history loss; refuse publication: ' + json.dumps(missing))


def check(repo):
    root = Path(repo) / 'localdata'
    if not (root / KEYS).exists() or not (root / RECEIPT).exists():
        raise ValueError('unverified prediction cache: run recover_and_rebuild before mining/serving')
    baseline = json.loads(gzip.decompress((root / KEYS).read_bytes()))
    if baseline.get('schema') != 1 or baseline.get('reference_key') != REFERENCE_KEY or not baseline.get('keys'):
        raise ValueError('invalid prediction-history baseline')
    actual, _ = _inventory(root, date.today().isoformat())
    _check_keys(actual, baseline['keys'])
    return {'status': 'history_completeness_verified',
            'source_fixture_counts': {s: len(k) for s, k in actual.items()}}
