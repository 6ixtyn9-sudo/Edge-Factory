"""The deployment must not silently override a code default.

This guards the defect class that hid the SharpAPI endpoint bug for three
days: the adapter's default was corrected, the workflow pinned a different
value, and both halves were internally consistent so nothing failed. Only
the PAIR was wrong, and nothing in the repository compared the pair.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "audit_env_drift", ROOT / "scripts" / "audit_env_drift.py")
audit = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(audit)


def test_no_unreviewed_divergence_between_workflow_and_code():
    rows = audit.drift()
    unreviewed = sorted({
        f"{name}: deployment {pinned!r} at {where} vs code {value!r} at {loc}"
        for name, pinned, value, loc, where in rows
        if name not in audit.ACCEPTED and name not in audit.PENDING_WORKFLOW_APPLY
    })
    assert unreviewed == [], (
        "A deployment setting contradicts a code default. Fix one side, or "
        "record it in ACCEPTED with a reason:\n  " + "\n  ".join(unreviewed))


def test_every_accepted_divergence_carries_a_reason():
    """An allowlist without reasons becomes a place to hide the next bug."""
    for name, reason in audit.ACCEPTED.items():
        assert isinstance(reason, str) and len(reason) > 20, name
    for name, reason in audit.PENDING_WORKFLOW_APPLY.items():
        assert isinstance(reason, str) and len(reason) > 20, name


def test_accepted_and_pending_are_kept_distinct():
    """An approval and an unpaid debt must not look alike."""
    assert not (set(audit.ACCEPTED) & set(audit.PENDING_WORKFLOW_APPLY))


def test_allowlist_entries_still_describe_a_real_divergence():
    """A stale entry is worse than none: it silently approves a future bug.

    If someone aligns the two sides, the entry must be deleted rather than
    left behind where it would pre-approve a fresh divergence on the same
    variable.
    """
    live = {name for name, *_ in audit.drift()}
    stale = sorted((set(audit.ACCEPTED) | set(audit.PENDING_WORKFLOW_APPLY)) - live)
    assert stale == [], (
        f"These no longer diverge and must be removed from the allowlist: {stale}")


def test_the_blind_spot_does_not_hide_a_deployed_variable():
    """Unresolvable defaults are tolerable only while none are deployed.

    The script cannot resolve a default that is computed at runtime. That is
    acceptable precisely as long as no workflow sets those variables - the
    moment one does, this check can no longer prove the pair agrees and must
    say so instead of quietly passing.
    """
    _defaults, blind = audit.code_defaults()
    deployed = sorted(blind & set(audit.workflow_env()))
    assert deployed == [], (
        "These have a runtime-computed default AND are set by a workflow, so "
        f"agreement is unverifiable: {deployed}")


def test_the_audit_actually_detects_a_planted_divergence(monkeypatch, tmp_path):
    """A detector nobody has watched fire is not known to work."""
    wf = tmp_path / "workflows"
    wf.mkdir()
    (wf / "planted.yml").write_text(
        "jobs:\n  x:\n    env:\n"
        "      EDGE_FACTORY_PLANTED: ${{ secrets.S || 'wrong-value' }}\n")
    src = tmp_path / "src"
    src.mkdir()
    (src / "mod.py").write_text(
        'import os\nVALUE = os.environ.get("EDGE_FACTORY_PLANTED", "right-value")\n')
    (tmp_path / "scripts").mkdir()
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "WORKFLOWS", wf)

    rows = audit.drift()
    assert [(r[0], r[1], r[2]) for r in rows] == [
        ("EDGE_FACTORY_PLANTED", "wrong-value", "right-value")]


def test_a_matching_pair_is_not_reported(monkeypatch, tmp_path):
    """The complement: agreement must stay silent, or the signal is noise."""
    wf = tmp_path / "workflows"
    wf.mkdir()
    (wf / "ok.yml").write_text(
        "jobs:\n  x:\n    env:\n"
        "      EDGE_FACTORY_PLANTED: ${{ secrets.S || 'same' }}\n")
    src = tmp_path / "src"
    src.mkdir()
    (src / "mod.py").write_text(
        'import os\nVALUE = os.environ.get("EDGE_FACTORY_PLANTED", "same")\n')
    (tmp_path / "scripts").mkdir()
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "WORKFLOWS", wf)
    assert audit.drift() == []


def test_a_constant_default_is_resolved_not_skipped(monkeypatch, tmp_path):
    """The SharpAPI bug used a module constant; a literal-only scan misses it."""
    wf = tmp_path / "workflows"
    wf.mkdir()
    (wf / "c.yml").write_text(
        "jobs:\n  x:\n    env:\n"
        "      EDGE_FACTORY_PLANTED: ${{ secrets.S || '/relay/path' }}\n")
    src = tmp_path / "src"
    src.mkdir()
    (src / "mod.py").write_text(
        'import os\nDEFAULT_PATH = "/api/v1/odds"\n'
        'VALUE = os.environ.get("EDGE_FACTORY_PLANTED") or DEFAULT_PATH\n')
    (tmp_path / "scripts").mkdir()
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "WORKFLOWS", wf)
    rows = audit.drift()
    assert [(r[1], r[2]) for r in rows] == [("/relay/path", "/api/v1/odds")]


def test_a_credential_fallback_chain_is_not_a_blind_spot(monkeypatch, tmp_path):
    """KEYS or KEY or "" has no literal default to contradict."""
    wf = tmp_path / "workflows"
    wf.mkdir()
    (wf / "k.yml").write_text(
        "jobs:\n  x:\n    env:\n      EDGE_FACTORY_KEYS: ${{ secrets.S }}\n")
    src = tmp_path / "src"
    src.mkdir()
    (src / "mod.py").write_text(
        'import os\nRAW = os.environ.get("EDGE_FACTORY_KEYS") or '
        'os.environ.get("EDGE_FACTORY_KEY") or ""\n')
    (tmp_path / "scripts").mkdir()
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "WORKFLOWS", wf)
    _defaults, blind = audit.code_defaults()
    assert "EDGE_FACTORY_KEYS" not in blind


def test_a_credential_chain_named_by_a_constant_is_not_a_blind_spot(monkeypatch, tmp_path):
    """The regression this audit was blind to.

    ``os.environ.get("RAPIDAPI_KEYS") or os.environ.get(KEY_ENV) or ""`` is the
    same ring read as the test above, with the fallback's NAME held in a module
    constant. The chain's last element is a literal, so resolving the fallback
    only ever happens through this name lookup - and until it resolved, the
    fallback was neither a literal nor a recognised env read, the name landed in
    the BLIND set, and a workflow setting it (both the probe shim and daily.yml)
    tripped the blind-spot guard instead of passing. Fixing the RESOLVER, not the
    guard: the guard still refuses to certify a pair it cannot read.
    """
    wf = tmp_path / "workflows"
    wf.mkdir()
    (wf / "k.yml").write_text(
        "jobs:\n  x:\n    env:\n      EDGE_FACTORY_KEYS: ${{ secrets.S }}\n")
    src = tmp_path / "src"
    src.mkdir()
    (src / "mod.py").write_text(
        'import os\nKEY_ENV = "EDGE_FACTORY_KEY"\n'
        'RAW = os.environ.get("EDGE_FACTORY_KEYS") or os.environ.get(KEY_ENV) or ""\n')
    (tmp_path / "scripts").mkdir()
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "WORKFLOWS", wf)
    _defaults, blind = audit.code_defaults()
    assert "EDGE_FACTORY_KEYS" not in blind
    assert "EDGE_FACTORY_KEYS" not in dict(_defaults)   # no default to contradict
    assert audit.drift() == []                           # and no invented divergence
