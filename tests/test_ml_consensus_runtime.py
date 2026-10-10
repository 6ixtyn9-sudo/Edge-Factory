"""Unstubbed admission-policy controls, separate from synthetic worker tests."""
from types import SimpleNamespace
import tempfile
from pathlib import Path

import pytest
from edgefactory import ml_consensus_audit as audit

PINNED = '3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]'


@pytest.mark.parametrize('implementation,platform,version,gil,supported', [
    ('CPython', 'linux', PINNED, None, True),
    ('CPython', 'linux', PINNED, True, True),
    ('CPython', 'linux', PINNED, False, False),
    ('PyPy', 'linux', PINNED, True, False),
    ('CPython', 'darwin', PINNED, True, False),
    ('CPython', 'linux', '3.13.16', True, False),
    ('CPython', 'linux', '3.11.2 (different build)', True, False),
])
def test_runtime_policy(monkeypatch, implementation, platform, version, gil, supported):
    runtime = SimpleNamespace(platform=platform, version=version)
    if gil is not None:
        runtime._is_gil_enabled = lambda: gil
    monkeypatch.setattr(audit, 'sys', runtime)
    monkeypatch.setattr(audit, 'platform', SimpleNamespace(
        python_implementation=lambda: implementation))
    assert audit._runtime_supported() is supported
    if supported:
        return  # Worker lifecycle is exercised separately, not calibrated here.
    monkeypatch.setenv('EDGE_FACTORY_MCP_AUDIT', '1')
    from edgefactory import ml_consensus_storage as storage

    def forbidden(*args, **kwargs):
        pytest.fail('unsupported runtime performed audit work')

    monkeypatch.setattr(storage, 'TemporarySpool', forbidden)
    owner = tempfile.TemporaryDirectory()
    try:
        handle = audit.TemporaryAudit(owner, trading_date='2026-06-01',
                                      invocation_id='refusal', code_sha='0'*40)
        assert handle.state == 'DISABLED'
        assert handle._thread is None
        audit.safe_capture(handle, 'inference', forbidden)
        assert not list(Path(owner.name).iterdir())
    finally:
        owner.cleanup()
