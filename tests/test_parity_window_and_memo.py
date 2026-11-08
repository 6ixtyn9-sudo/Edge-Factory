"""Bounded routine parity audit + settlement-facts reuse.

Two demonstrated repeated costs on 2026-11-08 (run 42432286562 cancelled with
runner shutdown ~18 min into the replay-parity step; run 42444982103 spent
26m54s there):

 1. ``decision_parity_report`` replayed every retained receipt every run. The
    retained ENH receipts are multi-part: the logical ``*.json.gz`` is a
    ~545-byte manifest and the payload lives in 19-21 sibling ``.part-<sha>``
    chunks totalling 200-607 MB per day. Manifest size therefore says nothing
    about validation cost. A routine window bounds the WORST case; it is
    containment, not a claim that full history is small.

 2. ``_collect_settled_facts`` rebuilt the whole settlement index on every
    call (3-4x per run). It also CLEARS module-level refusal inventories
    (``AMBIGUOUS_SETTLEMENT_KEYS``, ``EMPTY_KEY_TIERS_DROPPED``,
    ``EMPTY_KEY_FIXTURES``) as a side effect, so a naive cache would leave the
    operator-visible evidence describing an older load. The memo below rebuilds
    the derived maps but re-applies the full refusal/ambiguity semantics on
    every call.
"""
from __future__ import annotations

import gzip
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import scripts.auto_tickets as at
import scripts.replay_harness as rh


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _receipt_name(prefix: str, day: str) -> str:
    return f"{prefix}_{day}_decision.json"


def _seed_window_receipts(tmp_path: Path, *, prefix: str = "auto_tickets",
                          days=("2026-11-01", "2026-11-05", "2026-11-07", "2026-11-08")):
    """Minimal receipts carrying only what the window filter reads.

    The window filter runs BEFORE replay, so these need no valid decision
    payload; a receipt that survives selection is expected to fail replay.
    """
    base = tmp_path / "localdata"
    (base / at.TICKET_RECEIPT_SUBDIR if hasattr(at, "TICKET_RECEIPT_SUBDIR")
     else base / "phase5_reconciliation" / "ticket_decisions").mkdir(parents=True, exist_ok=True)
    sub = base / "phase5_reconciliation" / "ticket_decisions"
    for day in days:
        payload = dict(schema=1, boundary=rh.decision_parity_report.__doc__ and
                       "execution_safe_admission_to_ticket",
                       status="no_bet", plan=[], context=dict(date=day, lane="main",
                       build_at=f"{day}T06:00:00+00:00", bank_eff=1.0, bank_total=1.0))
        raw = json.dumps(payload).encode()
        path = sub / (_receipt_name(prefix, day) + ".gz")
        with gzip.GzipFile(filename="", mode="wb", fileobj=open(path, "wb"), mtime=0) as fh:
            fh.write(raw)
    return base


def _walks(monkeypatch):
    """Count how many receipts the report actually replays."""
    seen = []
    real = rh.read_ticket_receipt
    monkeypatch.setattr(rh, "read_ticket_receipt", lambda p: (seen.append(Path(p).name), real(p))[1])
    return seen


# ---------------------------------------------------------------------------
# window selection
# ---------------------------------------------------------------------------
def test_full_history_is_the_default_scope(tmp_path, monkeypatch):
    _seed_window_receipts(tmp_path)
    walked = _walks(monkeypatch)
    report = rh.decision_parity_report(tmp_path)
    assert len(walked) == 4, "default must still be full history"
    assert report["scope"]["mode"] == "full_history"
    assert report["scope"]["selected_receipts"] == 4


def test_window_selects_only_recent_receipts(tmp_path, monkeypatch):
    _seed_window_receipts(tmp_path)
    walked = _walks(monkeypatch)
    report = rh.decision_parity_report(
        tmp_path, window_days=3, reference=datetime(2026, 11, 8, 12, tzinfo=timezone.utc))
    selected = sorted(walked)
    # cutoff = 11-08 minus 3 days = 11-05, inclusive.
    assert len(selected) == 3, f"window=3 from 11-08 should keep 11-05..11-08, got {selected}"
    assert report["scope"]["mode"] == "window"
    assert report["scope"]["window_days"] == 3
    assert report["scope"]["selected_receipts"] == 3
    assert report["scope"]["excluded_receipts"] == 1


def test_window_is_inclusive_of_the_boundary_day(tmp_path, monkeypatch):
    _seed_window_receipts(tmp_path, days=("2026-11-05", "2026-11-06"))
    walked = _walks(monkeypatch)
    rh.decision_parity_report(tmp_path, window_days=3,
                              reference=datetime(2026, 11, 8, 12, tzinfo=timezone.utc))
    # reference 11-08 minus 3 days = 11-05, which must be INCLUDED.
    assert len(walked) == 2, "boundary day must be inclusive, not dropped"


def test_window_never_hides_an_undated_receipt(tmp_path, monkeypatch):
    """A receipt with no usable build_at must be audited and surfaced."""
    base = _seed_window_receipts(tmp_path)
    sub = base / "phase5_reconciliation" / "ticket_decisions"
    # Filename still matches the receipt glob (`????-??-??`) but is not an ISO
    # date, so the pre-read window filter cannot place it. It must be audited.
    bad = dict(schema=1, boundary="execution_safe_admission_to_ticket", status="no_bet",
               plan=[], context=dict(date="2026-10-01", lane="main", build_at="not-a-timestamp",
                                     bank_eff=1.0, bank_total=1.0))
    path = sub / (_receipt_name("auto_tickets", "2026-13-99") + ".gz")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(path, "wb"), mtime=0) as fh:
        fh.write(json.dumps(bad).encode())
    report = rh.decision_parity_report(
        tmp_path, window_days=1, reference=datetime(2026, 11, 8, 12, tzinfo=timezone.utc))
    scope = report["scope"]
    assert scope["undated_receipts"], "undated receipt must be listed, never silently excluded"
    walked = [r["file"] for r in report["lanes"]["main"]["receipts"]]
    assert any("2026-13-99" in f for f in walked), "undated receipt must still be audited"


def test_window_scope_labels_the_claim_as_partial(tmp_path):
    _seed_window_receipts(tmp_path)
    report = rh.decision_parity_report(
        tmp_path, window_days=2, reference=datetime(2026, 11, 8, 12, tzinfo=timezone.utc))
    assert "NOT" in report["scope"]["coverage_caveat"]
    assert report["scope"]["coverage_caveat"]


# ---------------------------------------------------------------------------
# time budget: must never report PASS
# ---------------------------------------------------------------------------
def test_exhausted_budget_reports_incomplete_not_pass(tmp_path, monkeypatch):
    _seed_window_receipts(tmp_path)
    report = rh.decision_parity_report(tmp_path, window_days=30,
                                       reference=datetime(2026, 11, 8, 12, tzinfo=timezone.utc),
                                       time_budget_seconds=0)
    assert report["status"] == "INCOMPLETE_TIME_BUDGET"
    assert report["status"] != "PASS"


def test_incomplete_budget_is_not_reported_as_a_failure(tmp_path):
    _seed_window_receipts(tmp_path)
    report = rh.decision_parity_report(tmp_path, time_budget_seconds=0)
    assert report["status"] == "INCOMPLETE_TIME_BUDGET"
    assert report["budget"]["exhausted"] is True


# ---------------------------------------------------------------------------
# settlement facts: reuse must not disturb refusal semantics
# ---------------------------------------------------------------------------
def _seed_settlement_root(tmp_path: Path) -> Path:
    base = tmp_path / "localdata"
    base.mkdir(parents=True)
    (tmp_path / "Config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "Config" / "verified_results.json").write_text("[]")
    return base


def _write_settled(base: Path, home: str) -> None:
    rows = [dict(date="2026-11-01", home=home, away="Away", status="FT",
                 hs=1, gs=0, outcome="home")]
    # Both spellings serialise to the SAME byte length: a (size, mtime) key
    # cannot see this rewrite, which is why identity is content-hashed.
    (base / "settled_results.json").write_text(
        json.dumps({"rows": rows, "period_holds": []}))


def _count_builds(monkeypatch):
    calls = {"n": 0}
    real = at._build_settled_facts

    def counting(*a, **k):
        calls["n"] += 1
        return real(*a, **k)

    monkeypatch.setattr(at, "_build_settled_facts", counting)
    at.invalidate_settled_facts()
    return calls


def test_identical_inputs_build_once(tmp_path, monkeypatch):
    """The collector ran 3-4x per run; unchanged inputs must not rebuild."""
    base = _seed_settlement_root(tmp_path)
    _write_settled(base, "HomeA")
    calls = _count_builds(monkeypatch)
    at.load_settled(root=tmp_path)
    at.load_settled(root=tmp_path)
    at.load_settled(root=tmp_path)
    assert calls["n"] == 1, f"expected a single build, got {calls['n']}"


def test_same_size_rewrite_invalidates(tmp_path, monkeypatch):
    """Content identity, not size+mtime: a same-length rewrite must rebuild."""
    base = _seed_settlement_root(tmp_path)
    _write_settled(base, "HomeA")
    calls = _count_builds(monkeypatch)
    first = at.load_settled(root=tmp_path)
    _write_settled(base, "HomeB")
    second = at.load_settled(root=tmp_path)
    assert calls["n"] == 2
    assert first != second


def test_reuse_republishes_refusal_inventories(tmp_path, monkeypatch):
    """Reuse must not leave operator-visible evidence from an older load."""
    base = _seed_settlement_root(tmp_path)
    _write_settled(base, "HomeA")
    calls = _count_builds(monkeypatch)
    at.load_settled(root=tmp_path)
    at.AMBIGUOUS_SETTLEMENT_KEYS.clear()
    at.AMBIGUOUS_SETTLEMENT_KEYS.append(("sentinel",))
    at.load_settled(root=tmp_path)
    assert calls["n"] == 1, "derived maps should be reused"
    assert ("sentinel",) not in at.AMBIGUOUS_SETTLEMENT_KEYS, (
        "a reused load must republish its own refusal inventory, not inherit caller mutation")

