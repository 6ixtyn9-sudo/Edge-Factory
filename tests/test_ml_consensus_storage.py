"""Worker-only temporary reservation, accounting and ownership controls."""
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from edgefactory.ml_consensus_storage import TemporarySpool, QuotaUnavailable, QUOTA, SLOT, ROOT_CHARGE, usage


def bid(n):
    return 'mcb1:' + f'{n:064x}'


def test_thirteen_live_reservations_and_refusal():
    owner = tempfile.TemporaryDirectory()
    handles = []
    try:
        for n in range(13):
            spool = TemporarySpool(owner)
            spool.reserve(bid(n))
            handles.append(spool)
        assert ROOT_CHARGE + 13*SLOT <= QUOTA < ROOT_CHARGE + 14*SLOT
        with pytest.raises(QuotaUnavailable):
            TemporarySpool(owner).reserve(bid(13))
        # Releasing ownership reconciles unused capacity, not evidence.
        retained = handles[0].directory / 'retained.jsonl'
        retained.write_text('unexported evidence\n')
        handles[0].close()
        next_spool = TemporarySpool(owner)
        next_spool.reserve(bid(13))
        handles.append(next_spool)
        assert retained.read_text() == 'unexported evidence\n'
    finally:
        for handle in handles:
            handle.close()
        owner.cleanup()


def test_abandoned_retained_and_symlink_refused():
    owner = tempfile.TemporaryDirectory()
    h = TemporarySpool(owner)
    try:
        directory = h.reserve(bid(1))
        evidence = directory / 'partial.jsonl'
        evidence.write_text('partial')
        h.close()
        h2 = TemporarySpool(owner)
        try:
            h2.reserve(bid(2))
            assert evidence.read_text() == 'partial'
        finally:
            h2.close()
        (directory / 'unsafe').symlink_to('/etc/passwd')
        with pytest.raises(QuotaUnavailable):
            TemporarySpool(owner).reserve(bid(3))
        assert evidence.exists()
    finally:
        h.close()
        owner.cleanup()


def test_live_lock_never_reclaimed_even_without_reservation():
    owner = tempfile.TemporaryDirectory()
    h = TemporarySpool(owner)
    try:
        directory = h.reserve(bid(1))
        (directory / 'reservation.json').unlink()
        assert TemporarySpool(owner)._accounted() >= ROOT_CHARGE + SLOT
    finally:
        h.close()
        owner.cleanup()


def test_sparse_allocation_and_slot_overflow():
    owner = tempfile.TemporaryDirectory()
    h = TemporarySpool(owner)
    try:
        directory = h.reserve(bid(1))
        (directory / 'sparse').write_bytes(b'a')
        assert usage(directory) >= 8192*4
        with pytest.raises(QuotaUnavailable):
            h.check_growth(SLOT)
        with pytest.raises(ValueError):
            TemporarySpool(owner).reserve('../bad')
    finally:
        h.close()
        owner.cleanup()


def test_global_lock_contention_is_refusal():
    from edgefactory.ml_consensus_storage import _open_lock, _release
    owner = tempfile.TemporaryDirectory()
    fd = _open_lock(Path(owner.name) / 'quota.lock')
    try:
        with pytest.raises(BlockingIOError):
            TemporarySpool(owner).reserve(bid(1))
    finally:
        _release(fd)
        owner.cleanup()


def test_fork_child_cannot_reuse_inherited_writer():
    import os
    owner = tempfile.TemporaryDirectory()
    h = TemporarySpool(owner)
    try:
        h.reserve(bid(1))
        pid = os.fork()
        if pid == 0:
            try:
                h.check_growth(1)
            except QuotaUnavailable:
                h.close()
                os._exit(0)
            os._exit(1)
        _, status = os.waitpid(pid, 0)
        assert os.waitstatus_to_exitcode(status) == 0
        assert TemporarySpool(owner)._accounted() >= ROOT_CHARGE + SLOT
    finally:
        h.close()
        owner.cleanup()
