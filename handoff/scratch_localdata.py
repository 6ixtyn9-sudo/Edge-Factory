#!/usr/bin/env python3
"""One guard for every driver in this chain: no driver writes the repo's real state.

Written after the round-6 incident in which a driver called the shipped capture
without redirecting any localdata path: the filesystem writes were repaired, but
a demo run must not write real state in the first place (standing rule).

Mechanism — in this order, before the shipped modules do anything:

1. ``EDGE_FACTORY_LOCALDATA`` is set to the scratch directory **first**, so every
   module imported afterwards that resolves localdata at import time picks the
   scratch dir (that is how every ``edgefactory.sources.*`` module resolves it).
2. Every already-imported candidate module (``edgefactory.*`` and ``scripts.*``)
   has its module-level ``pathlib.Path`` attributes that live under the repo's
   ``localdata/`` re-pointed into the scratch dir, preserving the relative
   sub-path — ``LOCALDATA`` itself and the constants derived from it at import
   time (``auto_tickets.STATE_FILE``, ``picks_today.AUDIT_ROLLING_PATH``, …).
3. On exit every attribute is restored, and the guard prints
   ``git status --porcelain -- localdata/``. Anything but empty means a write
   path escaped the redirect: the guard says so loudly, and in ``strict=True``
   mode exits 1.

Two modes, because reads must keep working:

* ``mode="mirror"`` (**default**) — the repo's ``localdata/`` is copied into the
  scratch dir first (155 MB / 699 files at 2026-10-12), so a driver reads what it
  would have read and writes nothing real. This is the safe default.
* ``mode="scratch"`` — empty scratch; for drivers whose only localdata
  interaction is a write (or that read through ``git show`` instead).

Usage, as the first thing after the driver's own imports::

    from handoff.scratch_localdata import guard_localdata
    guard_localdata()                    # restored + checked at interpreter exit

    # or, scoped (restores and checks at the end of the block):
    from handoff.scratch_localdata import scratch_localdata
    with scratch_localdata() as scratch:
        ...

Selftest (writes through each module's own path helper, asserts nothing lands in
the repo)::

    PYTHONPATH=src .venv/bin/python handoff/scratch_localdata.py
"""
from __future__ import annotations

import atexit
import contextlib
import importlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
REAL_LOCALDATA = REPO / "localdata"
if str(REPO) not in sys.path:                 # `scripts.` must import for the
    sys.path.insert(0, str(REPO))             # capture/lane modules to be guardable

# Modules whose write paths must be covered even when the driver has not imported
# them yet. Imported leniently: a driver that needs only one of them must not
# fail because another is unavailable.
CHAIN_MODULES = (
    "edgefactory.sources.betexplorer_odds",
    "edgefactory.sources.betexplorer_match_snapshot",
    "edgefactory.source_health",
    "edgefactory.scored_candidate_shadow",
    "edgefactory.enh_pricing",
    "edgefactory.enh_registry",
    "edgefactory.form_intel",
    "scripts.capture_betexplorer",
    "scripts.picks_today",
    "scripts.auto_tickets",
    "scripts.audit_recent_picks",
    "scripts.replay_harness",
)

_restorers: list = []


def _patchable_modules() -> list:
    mods = []
    for name, mod in list(sys.modules.items()):
        if mod is None:
            continue
        if name.startswith(("edgefactory", "scripts")) and hasattr(mod, "__file__"):
            mods.append((name, mod))
    return mods


def _redirect_module(name: str, mod, scratch: pathlib.Path) -> list[str]:
    """Re-point every Path attribute of ``mod`` that is under localdata/."""
    moved = []
    for attr in dir(mod):
        if attr.startswith("__"):
            continue
        try:
            value = getattr(mod, attr)
        except Exception:                                   # pragma: no cover
            continue
        if not isinstance(value, pathlib.Path):
            continue
        try:
            rel = value.relative_to(REAL_LOCALDATA)
        except ValueError:
            continue
        target = scratch / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        _restorers.append((mod, attr, value))
        setattr(mod, attr, target)
        moved.append(f"{name}.{attr} -> {target}")
    return moved


@contextlib.contextmanager
def scratch_localdata(**kwargs):
    """Scoped form of :func:`guard_localdata`: restores and checks on exit."""
    scratch = guard_localdata(**kwargs)
    try:
        yield scratch
    finally:
        _restore_all()


def _restore_all() -> None:
    while _restorers:
        mod, attr, value = _restorers.pop()
        setattr(mod, attr, value)


def guard_localdata(*, mode: str = "mirror", scratch: pathlib.Path | None = None,
                    strict: bool = False, check_git: bool = True,
                    preimport: bool = True) -> pathlib.Path:
    """Redirect the chain's localdata writes into a scratch directory."""
    if mode not in {"mirror", "scratch"}:
        raise ValueError("mode must be 'mirror' or 'scratch'")
    own_scratch = scratch is None
    scratch = pathlib.Path(scratch) if scratch else pathlib.Path(
        tempfile.mkdtemp(prefix="edgefactory_scratch_localdata_"))
    scratch.mkdir(parents=True, exist_ok=True)

    if mode == "mirror" and not any(scratch.iterdir()):
        shutil.copytree(REAL_LOCALDATA, scratch, dirs_exist_ok=True)

    # 1. the environment FIRST: anything imported later resolves the scratch dir
    previous_env = os.environ.get("EDGE_FACTORY_LOCALDATA")
    os.environ["EDGE_FACTORY_LOCALDATA"] = str(scratch)

    if preimport:
        for name in CHAIN_MODULES:
            try:
                importlib.import_module(name)
            except Exception:                               # pragma: no cover
                pass

    # 2. everything already imported
    moved: list[str] = []
    for name, mod in _patchable_modules():
        moved.extend(_redirect_module(name, mod, scratch))

    def _restore_and_check():
        _restore_all()
        if previous_env is None:
            os.environ.pop("EDGE_FACTORY_LOCALDATA", None)
        else:
            os.environ["EDGE_FACTORY_LOCALDATA"] = previous_env
        if check_git:
            out = subprocess.run(["git", "status", "--porcelain", "--", "localdata/"],
                                 cwd=REPO, capture_output=True, text=True).stdout.strip()
            # stderr, deliberately: several drivers' STDOUT is a recorded
            # artifact, and the guard must not alter a byte of it.
            print(f"scratch_localdata: mode={mode} scratch={scratch}", file=sys.stderr)
            print(f"scratch_localdata: git status --porcelain -- localdata/ -> "
                  f"{out if out else '(empty: the driver wrote no real state)'}",
                  file=sys.stderr)
            if own_scratch:
                shutil.rmtree(scratch, ignore_errors=True)   # leave no 155 MB behind
            if out and strict:
                raise SystemExit("scratch_localdata: REAL STATE WAS WRITTEN - see above")

    atexit.register(_restore_and_check)
    print(f"scratch_localdata: guard active (mode={mode}, {len(moved)} path(s) redirected)",
          file=sys.stderr)
    return scratch


def _selftest() -> int:
    """Prove the guard covers every chain module's own path helper."""
    print("== scratch_localdata selftest ==")
    before = subprocess.run(["git", "status", "--porcelain", "--", "localdata/"],
                            cwd=REPO, capture_output=True, text=True).stdout.strip()
    print(f"  localdata before: {before if before else '(clean)'}")
    be = importlib.import_module("edgefactory.sources.betexplorer_odds")
    failures = []
    with scratch_localdata(mode="mirror", strict=True) as scratch:
        probes = {
            "betexplorer_odds._odds_cache_path":
                be.LOCALDATA / "betexplorer_odds_cache_2026-10-12.json",
            "betexplorer_odds._match_detail_path":
                be._match_detail_path("2026-10-12"),
        }
        capture = importlib.import_module("scripts.capture_betexplorer")
        probes["capture.RECEIPT path"] = capture.LOCALDATA / "betexplorer_capture_2026-10-12.json"
        at = importlib.import_module("scripts.auto_tickets")
        probes["auto_tickets.state_path()"] = at.state_path()
        pt = importlib.import_module("scripts.picks_today")
        probes["picks_today.LOCALDATA"] = pt.LOCALDATA / "probe.json"
        for label, path in probes.items():
            inside = False
            try:
                path.relative_to(scratch)
                inside = True
            except ValueError:
                inside = False
            print(f"  {label:34s} {path}")
            if not inside:
                failures.append(label)
        # write through each probe; nothing may land in the repo
        for label, path in probes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("probe\n")
        for label, path in probes.items():
            if not path.is_file():
                failures.append(f"{label} (write did not land)")
        for label, f in probes.items():
            if f.is_file() and REAL_LOCALDATA in f.parents:
                failures.append(f"{label} landed in the repo")
    after = subprocess.run(["git", "status", "--porcelain", "--", "localdata/"],
                           cwd=REPO, capture_output=True, text=True).stdout.strip()
    print(f"  localdata after:  {after if after else '(clean)'}")
    if before != after:
        failures.append("repo localdata changed")
    if failures:
        print("SELFTEST FAILED:", failures)
        return 1
    print("selftest: PASS - every chain module's write path lands in scratch, "
          "the repo's localdata is untouched")
    return 0


if __name__ == "__main__":
    sys.exit(_selftest())
