"""Git-sized storage preserves exact decision evidence, not a smaller replay."""
import gzip
import hashlib
import json
import os
import random

import pytest

from edgefactory import util


@pytest.fixture
def small_limit(monkeypatch):
    monkeypatch.setattr(util, 'TICKET_RECEIPT_MAX_FILE_BYTES', 4096)
    monkeypatch.setattr(util, '_TICKET_RECEIPT_PART_BYTES', 1024)


def payload(seed=1):
    return json.dumps({'status': 'frozen', 'noise': random.Random(seed).randbytes(9000).hex()},
                      sort_keys=True, separators=(',', ':')).encode()


def manifest(path):
    return json.loads(path.read_bytes()[len(util._TICKET_RECEIPT_PARTS_MAGIC):])


def parts(path):
    return sorted(path.parent.glob(path.name + '.part-*'))


def test_legacy_json_and_small_gzip_remain_byte_compatible(tmp_path):
    raw = b'{ "status": "frozen", "sha256": "untouched whitespace" }\n'
    for name in ('legacy.json', 'canonical.json.gz'):
        path = tmp_path / name
        util.write_ticket_receipt(path, raw)
        assert util.ticket_receipt_bytes(path) == raw
        assert path.read_bytes() == util.encode_ticket_receipt(path, raw)
        assert not parts(path)


def test_multipart_roundtrip_preserves_raw_json_compressed_bytes_and_discovery(tmp_path, small_limit):
    path = util.ticket_receipt_path(tmp_path, 'auto_tickets_2026-11-01_decision.json')
    raw = payload()
    expected = util.encode_ticket_receipt(path, raw)
    util.write_ticket_receipt(path, raw)
    assert util.ticket_receipt_bytes(path) == raw
    assert util.read_ticket_receipt(path) == json.loads(raw)
    assert util._ticket_receipt_stored_bytes(path, path.read_bytes()) == expected
    assert manifest(path)['sha256'] == hashlib.sha256(expected).hexdigest()
    assert parts(path) and max(p.stat().st_size for p in [path, *parts(path)]) <= 4096
    assert util.ticket_receipt_files(tmp_path, 'auto_tickets') == [path]
    assert util.ticket_receipt_files(tmp_path, 'auto_tickets', conflicts=True) == []


@pytest.mark.parametrize('delta', [0, -1])
def test_exact_size_boundary(tmp_path, monkeypatch, delta):
    path = tmp_path / 'receipt.json.gz'
    raw = payload()
    encoded = util.encode_ticket_receipt(path, raw)
    monkeypatch.setattr(util, 'TICKET_RECEIPT_MAX_FILE_BYTES', len(encoded) + delta)
    util.write_ticket_receipt(path, raw)
    assert util.ticket_receipt_bytes(path) == raw
    assert bool(parts(path)) is (delta == -1)
    assert all(p.stat().st_size <= len(encoded) + delta for p in [path, *parts(path)])


@pytest.mark.parametrize('damage', ['missing', 'truncated', 'changed'])
def test_missing_or_corrupt_part_fails_closed(tmp_path, small_limit, damage):
    path = tmp_path / 'receipt.json.gz'
    util.write_ticket_receipt(path, payload())
    chunk = parts(path)[0]
    if damage == 'missing':
        chunk.unlink()
    elif damage == 'truncated':
        chunk.write_bytes(chunk.read_bytes()[:-1])
    else:
        raw = chunk.read_bytes()
        chunk.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
    with pytest.raises(ValueError, match='multipart ticket receipt'):
        util.read_ticket_receipt(path)


@pytest.mark.parametrize('damage', ['schema', 'schema_bool', 'encoding', 'path', 'size', 'bool_size',
                                    'total', 'digest', 'order', 'empty', 'truncated', 'oversized'])
def test_malformed_manifest_cannot_escape_directory_or_silently_drop_evidence(
        tmp_path, small_limit, damage):
    path = tmp_path / 'receipt.json.gz'
    util.write_ticket_receipt(path, payload())
    data = manifest(path)
    if damage == 'schema':
        data['schema'] = 2
    elif damage == 'schema_bool':
        data['schema'] = True
    elif damage == 'encoding':
        data['encoding'] = 'pickle'
    elif damage == 'path':
        data['parts'][0]['sha256'] = '../../other-file'
    elif damage == 'size':
        data['parts'][0]['size'] = -1
    elif damage == 'bool_size':
        data['parts'][0]['size'] = True
    elif damage == 'total':
        data['size'] += 1
    elif damage == 'digest':
        data['sha256'] = '0' * 64
    elif damage == 'order':
        data['parts'].reverse()
    elif damage == 'empty':
        data['parts'] = []
    encoded = json.dumps(data).encode() if damage != 'truncated' else b'{'
    if damage == 'oversized':
        encoded = b' ' * (1024 * 1024 + 1)
    path.write_bytes(util._TICKET_RECEIPT_PARTS_MAGIC + encoded)
    with pytest.raises(ValueError, match='multipart ticket receipt'):
        util.ticket_receipt_bytes(path)


@pytest.mark.parametrize('old_multipart', [False, True])
def test_interrupted_publication_preserves_old_complete_receipt(
        tmp_path, small_limit, monkeypatch, old_multipart):
    path = tmp_path / 'receipt.json.gz'
    old = payload(1) if old_multipart else b'{"status":"draft"}'
    util.write_ticket_receipt(path, old)
    old_files = {p: p.read_bytes() for p in [path, *parts(path)]}
    replace = os.replace
    def interrupted(source, destination):
        if destination == path:
            raise OSError('simulated interruption before envelope publication')
        return replace(source, destination)
    monkeypatch.setattr(os, 'replace', interrupted)
    with pytest.raises(OSError, match='simulated interruption'):
        util.write_ticket_receipt(path, payload(2))
    assert util.ticket_receipt_bytes(path) == old
    assert all(p.read_bytes() == blob for p, blob in old_files.items())
    assert not list(tmp_path.glob('*.tmp'))
    monkeypatch.setattr(os, 'replace', replace)
    util.write_ticket_receipt(path, payload(2))
    assert util.ticket_receipt_bytes(path) == payload(2)
    util.write_ticket_receipt(path, b'{"status":"draft"}')
    assert all(p.exists() for p in old_files)  # never delete old evidence parts


def test_compaction_converts_oversized_cached_gzip_without_recompressing(tmp_path, small_limit):
    path = util.ticket_receipt_path(tmp_path, 'autobets_enh_tickets_2026-11-01_decision.json')
    path.parent.mkdir(parents=True)
    # Noncanonical gzip timestamp/compression: even those original bytes survive.
    raw = payload()
    stored = gzip.compress(raw, compresslevel=1, mtime=1234)
    path.write_bytes(stored)
    assert util.compact_ticket_receipts(tmp_path) == 1
    assert util._ticket_receipt_stored_bytes(path, path.read_bytes()) == stored
    assert util.ticket_receipt_bytes(path) == raw
    snapshot = {p: p.read_bytes() for p in [path, *parts(path)]}
    assert util.compact_ticket_receipts(tmp_path) == 0
    assert all(p.read_bytes() == blob for p, blob in snapshot.items())
    parts(path)[0].unlink()
    with pytest.raises(ValueError, match='multipart ticket receipt'):
        util.compact_ticket_receipts(tmp_path)


def test_tree_reader_resolves_parts_from_the_same_snapshot(tmp_path, small_limit):
    path = tmp_path / 'receipt.json.gz'
    raw = payload()
    bundle = util.encode_ticket_receipt_files(path, raw)
    assert util.ticket_receipt_bytes(path, raw=bundle[path],
                                    read_part=lambda name: bundle[path.with_name(name)]) == raw
    assert not path.exists()  # no worktree dependencies, as during HEAD restore
