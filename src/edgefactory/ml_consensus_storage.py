"""Worker-only Linux temporary-spool ownership and refusal-only quota accounting.

No cleanup, publisher, export or production path entry point. The authoritative
inventory is rescanned under flock; there is no optimistically trusted cache.
"""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import stat

QUOTA = 512 * 1024 * 1024
SLOT = 37 * 1024 * 1024 + 64 * 1024
ROOT_CHARGE = 64 * 1024
CONTROL_LIMIT = 64 * 1024
_FDS = set()


def _after_fork():
    for fd in tuple(_FDS):
        try:
            os.close(fd)
        except OSError:
            pass
    _FDS.clear()


os.register_at_fork(after_in_child=_after_fork)


class QuotaUnavailable(OSError):
    pass


def _open_lock(path):
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise QuotaUnavailable('unsafe lock')
    _FDS.add(fd)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        _release(fd)
        raise
    return fd


def _release(fd):
    if fd is not None and fd in _FDS:
        _FDS.remove(fd)
        os.close(fd)


def usage(directory):
    """Bounded inventory; logical allowance must dominate measured allocation."""
    total = 0
    files = directories = 0
    pending = [directory]
    while pending:
        path = pending.pop()
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode):
            directories += 1
            if directories > 8:
                raise QuotaUnavailable('directory count')
            planned = 8192
            with os.scandir(path) as entries:
                for entry in entries:
                    files += 1
                    if files > 64:
                        raise QuotaUnavailable('entry count')
                    pending.append(Path(entry.path))
        elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
            planned = ((info.st_size + 4095) // 4096) * 4096 + 8192
        else:
            raise QuotaUnavailable('unsafe object')
        measured = info.st_blocks * 512
        if measured > planned:
            raise QuotaUnavailable('allocation invariant')
        total += max(planned, measured)
    return total


def _atomic_json(path, value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()
    if len(raw) > CONTROL_LIMIT:
        raise QuotaUnavailable('control size')
    temporary = path.with_suffix('.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
    finally:
        if temporary.exists():
            temporary.unlink()


class TemporarySpool:
    """One full reservation per live build; unexported bytes are never evicted.

    Only use on an exclusively caller-owned TemporaryDirectory. This is not a
    validated production-filesystem profile and cannot enable production audit.
    """
    def __init__(self, owner):
        import tempfile
        if type(owner) is not tempfile.TemporaryDirectory:
            raise ValueError('temporary ownership required')
        self.root = Path(owner.name)
        if self.root.is_symlink() or not self.root.is_dir():
            raise QuotaUnavailable('unsafe root')
        self.owner_fd = None
        self.directory = None

    def _accounted(self):
        total = ROOT_CHARGE
        count = 0
        with os.scandir(self.root) as entries:
            for entry in entries:
                if entry.name == 'quota.lock':
                    continue
                count += 1
                if count > 4096 or not entry.name.startswith('mcb1:') or not entry.is_dir(follow_symlinks=False):
                    raise QuotaUnavailable('unknown spool entry')
                directory = Path(entry.path)
                actual = usage(directory)
                lock = directory / 'owner.lock'
                if not lock.exists():
                    raise QuotaUnavailable('missing ownership evidence')
                fd = None
                try:
                    fd = _open_lock(lock)
                except BlockingIOError:
                    # Even a corrupt/missing reservation cannot let a live
                    # writer spend someone else's capacity.
                    total += max(SLOT, actual)
                else:
                    # Explicit ownership acquired: finalized OR abandoned.
                    # Reconcile unused capacity, never delete retained bytes.
                    total += actual
                finally:
                    _release(fd)
        return total

    def reserve(self, build_id):
        if len(build_id) != 69 or not build_id.startswith('mcb1:') or any(c not in '0123456789abcdef' for c in build_id[5:]):
            raise ValueError('invalid build id')
        quota_fd = _open_lock(self.root / 'quota.lock')
        try:
            if self._accounted() + SLOT > QUOTA:
                raise QuotaUnavailable('quota unavailable')
            self.directory = self.root / build_id
            self.directory.mkdir(mode=0o700)
            self.owner_fd = _open_lock(self.directory / 'owner.lock')
            _atomic_json(self.directory / 'reservation.json', {
                'build_id': build_id, 'allocation': SLOT,
                'pid': os.getpid(), 'host': os.uname().nodename,
                'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                'state': 'live', 'export': 'unprovisioned',
            })
            return self.directory
        finally:
            _release(quota_fd)

    def check_growth(self, logical_bytes):
        if self.owner_fd not in _FDS or self.directory is None:
            raise QuotaUnavailable('no reservation')
        if logical_bytes < 0 or usage(self.directory) + logical_bytes + 16384 > SLOT:
            raise QuotaUnavailable('slot exceeded')

    def close(self):
        fd, self.owner_fd = self.owner_fd, None
        _release(fd)
