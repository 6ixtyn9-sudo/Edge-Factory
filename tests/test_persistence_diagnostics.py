"""Read-only inventory and bounded canonical hashing preserve persistence guards."""

import hashlib
import json
import random
import subprocess

import pytest
from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo


def test_root_inventory_counts_index_directories_not_ignored_cache(tmp_path, capsys):
    _seed_repo(tmp_path)
    root = tmp_path / 'localdata'
    (tmp_path / '.gitignore').write_text((tmp_path / '.gitignore').read_text() + '\nlocaldata/cache-*\n')
    for i in range(905):
        (root / f'cache-{i}').write_text('retained, not deleted')
    archive = root / 'archive' / 'picks' / '2026' / '09'
    archive.mkdir(parents=True)
    for i in range(4):
        (archive / f'picks-{i}.json').write_text('{}')
    (root / 'new.json').write_text('{}')
    _git(tmp_path, 'add', '-f', str(archive.relative_to(tmp_path)), 'localdata/new.json')
    indexed = _git(tmp_path, 'ls-files', '-z', '--', 'localdata/').stdout.split('\0')
    expected = len({p.split('/')[1] for p in indexed if p})
    result = _persistence_module()._report_localdata_root_entries(tmp_path)
    output = capsys.readouterr().out
    assert result['indexed'] == expected < 900
    assert result['filesystem'] > 900
    assert '::warning::' not in output
    assert 'indexed includes directory entries' in output
    assert len(list(root.glob('cache-*'))) == 905


def test_actual_large_index_still_warns(tmp_path, capsys):
    _seed_repo(tmp_path)
    root = tmp_path / 'localdata'
    for i in range(900):
        (root / f'extra-{i}.json').write_text('{}')
    _git(tmp_path, 'add', '-f', 'localdata')
    result = _persistence_module()._report_localdata_root_entries(tmp_path)
    assert result['indexed'] >= 900
    assert 'indexed root entries' in capsys.readouterr().out


def test_inventory_failure_is_not_a_false_zero(tmp_path, monkeypatch, capsys):
    module = _persistence_module()
    monkeypatch.setattr(module, '_run', lambda *a: subprocess.CompletedProcess(a, 1, b'', b'failure'))
    result = module._report_localdata_root_entries(tmp_path)
    assert result == {'filesystem': 0, 'indexed': None}
    assert 'Git listing size was not verified' in capsys.readouterr().out


def expected_digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


@pytest.mark.parametrize('payload', [
    {}, {'empty': [{}, []]}, {'unicode': 'Fenerbahçe \u2028 😀', 'escape': '\n\t"\\'},
    {'numbers': [0, -0.0, 1.7e-200, 1e200, -123456789012345678901234567890, True, False, None]},
    {'large_list': list(range(5000))},
    {'large_dict': {str(i): {'a': i / 13, 'b': [True, None, -0.0]} for i in range(900)}},
    {'long_string': '\\ü\n' * 25000},
    {'nested': [[{'é': i / 37, 'z': [i, None]} for i in range(75)] for _ in range(25)]},
])
def test_batched_hash_is_exactly_the_original_canonical_json(payload):
    before = json.dumps(payload)
    assert _persistence_module()._receipt_payload_sha256(payload) == expected_digest(payload)
    assert json.dumps(payload) == before


def test_randomized_batched_digest_equivalence():
    rng = random.Random(91)
    for _ in range(30):
        payload = {str(i): [{'v': rng.random(), 'name': 'Aliança', 'nil': None}
                            for _ in range(rng.randrange(100))] for i in range(rng.randrange(35))}
        assert _persistence_module()._receipt_payload_sha256(payload) == expected_digest(payload)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf')])
def test_batched_digest_still_rejects_nonfinite_values(value):
    with pytest.raises(ValueError):
        _persistence_module()._receipt_payload_sha256({'rows': [0] * 1200 + [value]})


def test_hash_encoder_never_serializes_the_whole_large_graph(monkeypatch):
    module = _persistence_module()
    payload = {'rows': [{'features': list(range(90)), 'name': str(i)} for i in range(6000)]}
    expected = expected_digest(payload)
    original = module.json.dumps

    def bounded(value, **kwargs):
        assert value is not payload and value is not payload['rows']
        return original(value, **kwargs)

    monkeypatch.setattr(module.json, 'dumps', bounded)
    assert module._receipt_payload_sha256(payload) == expected
