"""Regression tests for decision receipt memory hardening, canonical parity,
and frozen-ticket evidence protection boundaries.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import random
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from edgefactory import util
from edgefactory.util import (
    _TICKET_RECEIPT_PARTS_MAGIC,
    read_ticket_receipt,
    ticket_receipt_bytes,
    write_ticket_receipt,
)
import auto_tickets as at


@pytest.fixture
def small_receipt_limit(monkeypatch):
    monkeypatch.setattr(util, "TICKET_RECEIPT_MAX_FILE_BYTES", 4096)
    monkeypatch.setattr(util, "_TICKET_RECEIPT_PART_BYTES", 1024)


def multipart_payload(seed: int = 1) -> bytes:
    return json.dumps(
        {"status": "frozen", "noise": random.Random(seed).randbytes(9000).hex()},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def get_parts(path: Path) -> list[Path]:
    return sorted(path.parent.glob(path.name + ".part-*"))


def get_manifest(path: Path) -> dict:
    raw = path.read_bytes()
    assert raw.startswith(_TICKET_RECEIPT_PARTS_MAGIC)
    return json.loads(raw[len(_TICKET_RECEIPT_PARTS_MAGIC):])


def build_valid_enh_context(target: str = "2026-11-14") -> dict:
    now = datetime(2026, 11, 14, 8, 30, tzinfo=at.TZ)
    return at.ticket_decision_context(
        lane="enh",
        target=target,
        now=now,
        slate=[],
        pool=[],
        bank_eff=100.0,
    )


def test_decision_digest_streaming_canonical_parity():
    payloads = [
        {"schema": 1, "status": "draft", "context": {"date": "2026-11-14", "lane": "enh"}},
        {
            "schema": 1,
            "boundary": "execution_safe_admission_to_ticket",
            "status": "frozen",
            "provenance": {"sha": "ccd31dc", "run_id": "43597523286"},
            "nested": {
                "teams": ["Lillestrøm SK", "SK Brann", "München 1860"],
                "odds": [1.88, 2.05, 3.40],
                "active": True,
                "null_val": None,
                "counts": {"wins": 10, "losses": 2},
            },
        },
        {"empty_dict": {}, "empty_list": [], "zero": 0, "neg": -42.5},
    ]
    for payload in payloads:
        expected = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).hexdigest()
        assert at._decision_digest(payload) == expected


def test_decision_digest_rejects_non_finite_floats():
    for bad_float in (float("nan"), float("inf"), float("-inf")):
        payload = {"status": "draft", "odds": bad_float}
        with pytest.raises(ValueError, match="Out of range float values"):
            at._decision_digest(payload)


def test_read_ticket_receipt_handles_json_escapes(tmp_path: Path):
    p = tmp_path / "escaped_frozen.json.gz"
    write_ticket_receipt(p, b'{"status":"\\u0066rozen","lane":"enh"}')
    assert read_ticket_receipt(p)["status"] == "frozen"

    p2 = tmp_path / "escaped_key.json.gz"
    write_ticket_receipt(p2, b'{"\\u0073\\u0074\\u0061\\u0074\\u0075\\u0073":"frozen","lane":"enh"}')
    assert read_ticket_receipt(p2)["status"] == "frozen"


def test_read_ticket_receipt_fails_closed_on_malformed_truncated_json(tmp_path: Path):
    p = tmp_path / "truncated.json.gz"
    p.write_bytes(gzip.compress(b'{"status":"draft"', mtime=0))
    with pytest.raises(json.JSONDecodeError):
        read_ticket_receipt(p)


def test_ticket_receipt_gzip_integrity_and_trailers(tmp_path: Path):
    p = tmp_path / "bad_gzip.json.gz"
    full_gzip = gzip.compress(b'{"status":"draft"}', mtime=0)
    p.write_bytes(full_gzip[: len(full_gzip) - 6])
    with pytest.raises(ValueError, match="invalid compressed ticket receipt"):
        ticket_receipt_bytes(p)


def test_ticket_receipt_concatenated_gzip_members(tmp_path: Path):
    p = tmp_path / "concat.json.gz"
    p.write_bytes(gzip.compress(b'{"status":', mtime=0) + gzip.compress(b'"draft"}', mtime=0))
    assert ticket_receipt_bytes(p) == b'{"status":"draft"}'
    assert read_ticket_receipt(p) == {"status": "draft"}


def test_multipart_aggregate_digest_validation(tmp_path: Path, small_receipt_limit):
    p = tmp_path / "autobets_enh_tickets_2026-11-14_decision.json.gz"
    write_ticket_receipt(p, multipart_payload(seed=42))
    parts = get_parts(p)
    assert len(parts) >= 2
    manifest = get_manifest(p)
    manifest["sha256"] = "0" * 64
    p.write_bytes(_TICKET_RECEIPT_PARTS_MAGIC + json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    with pytest.raises(ValueError, match="receipt compressed digest mismatch"):
        ticket_receipt_bytes(p)


def test_multipart_missing_or_corrupted_part_fails_closed(tmp_path: Path, small_receipt_limit):
    p = tmp_path / "autobets_enh_tickets_2026-11-14_decision.json.gz"
    write_ticket_receipt(p, multipart_payload(seed=7))
    parts = get_parts(p)
    assert len(parts) >= 2
    target_part = parts[0]
    orig_bytes = target_part.read_bytes()

    target_part.write_bytes(orig_bytes[:-10] + b"corrupt123")
    with pytest.raises(ValueError, match="receipt part integrity mismatch"):
        ticket_receipt_bytes(p)

    target_part.unlink()
    with pytest.raises(ValueError, match="invalid multipart ticket receipt"):
        ticket_receipt_bytes(p)


@pytest.mark.parametrize("bad_root", [b"[]", b"null", b'"draft"'])
def test_unexpected_root_type_at_writer_boundary_fails_closed(tmp_path: Path, monkeypatch, bad_root):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    context = build_valid_enh_context()
    receipt_dir = tmp_path / "phase5_reconciliation" / "ticket_decisions"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    p = receipt_dir / "autobets_enh_tickets_2026-11-14_decision.json.gz"
    write_ticket_receipt(p, bad_root)
    original_bytes = p.read_bytes()

    captured_stderr = io.StringIO()
    monkeypatch.setattr(sys, "stderr", captured_stderr)

    plan = [{"acca": 1, "odds": 2.10, "stake_pct": 0.05, "legs": []}]
    at.write_decision_receipt(context, plan, frozen=False)

    assert "DECISION RECEIPT NOT PERSISTED: AttributeError" in captured_stderr.getvalue()
    assert p.read_bytes() == original_bytes


def test_write_decision_receipt_updates_non_frozen_draft(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    context = build_valid_enh_context()

    captured_stderr = io.StringIO()
    monkeypatch.setattr(sys, "stderr", captured_stderr)

    plan_v1 = [{"acca": 1, "odds": 2.10, "stake_pct": 0.05, "legs": []}]
    at.write_decision_receipt(context, plan_v1, frozen=False)

    receipt_path = tmp_path / "phase5_reconciliation" / "ticket_decisions" / "autobets_enh_tickets_2026-11-14_decision.json.gz"
    assert receipt_path.exists()
    assert "DECISION RECEIPT NOT PERSISTED" not in captured_stderr.getvalue()

    r1 = read_ticket_receipt(receipt_path)
    assert r1["status"] == "draft"

    captured_stderr = io.StringIO()
    monkeypatch.setattr(sys, "stderr", captured_stderr)

    plan_v2 = [{"acca": 1, "odds": 2.45, "stake_pct": 0.05, "legs": []}]
    at.write_decision_receipt(context, plan_v2, frozen=False)

    assert "DECISION RECEIPT NOT PERSISTED" not in captured_stderr.getvalue()
    r2 = read_ticket_receipt(receipt_path)
    assert r2["status"] == "draft"
    assert r2["sha256"] != r1["sha256"]

    payload_without_sha = {k: v for k, v in r2.items() if k != "sha256"}
    assert at._decision_digest(payload_without_sha) == r2["sha256"]


def test_write_decision_receipt_preserves_frozen_receipt_byte_for_byte(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    context = build_valid_enh_context()

    plan_frozen = [{"acca": 1, "odds": 2.26, "stake_pct": 0.0328, "legs": []}]
    at.write_decision_receipt(context, plan_frozen, frozen=True)

    receipt_path = tmp_path / "phase5_reconciliation" / "ticket_decisions" / "autobets_enh_tickets_2026-11-14_decision.json.gz"
    assert receipt_path.exists()
    original_bytes = receipt_path.read_bytes()
    original_part_bytes = {part: part.read_bytes() for part in get_parts(receipt_path)}

    r_frozen = read_ticket_receipt(receipt_path)
    assert r_frozen["status"] == "frozen"
    payload_without_sha = {k: v for k, v in r_frozen.items() if k != "sha256"}
    assert at._decision_digest(payload_without_sha) == r_frozen["sha256"]

    plan_attempt = [{"acca": 1, "odds": 3.50, "stake_pct": 0.05, "legs": []}]
    at.write_decision_receipt(context, plan_attempt, frozen=False)

    assert receipt_path.read_bytes() == original_bytes
    assert {part: part.read_bytes() for part in get_parts(receipt_path)} == original_part_bytes