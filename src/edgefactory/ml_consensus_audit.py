"""Default-OFF MCP audit collector: explicit temporary-storage development only.

No operational consumer reads this module. There is deliberately no production
storage default, environment path, uploader, Git integration or enablement in
run_day. Callers may supply a handle to the optional evaluator/collapse hooks.
All hashes/JSON/disk writes occur on the writer, never the scoring thread.

NOT implementation acceptance: dependency/contract capture and production
filesystem/quota calibration remain incomplete. Every development build is
partial, unprovisioned and non-replayable. Oversized evidence is dropped, never
truncated or recomputed. No component reassembly bypasses capture limits.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import threading
import time
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "mcp-audit/v1"
MAX_NODES = 4096
MAX_CHARS = 1024
MAX_DEPTH = 12
MAX_RESERVATION = 1024 + 256 * MAX_NODES + 8 * MAX_CHARS
POOL_BYTES = 8 * 1024 * 1024
CONTROL_BYTES = 64 * 1024
MAX_RECORD_BYTES = 256 * 1024
STREAM_BYTES = 32 * 1024 * 1024
RECORD_LIMIT = 10_000


class CaptureLimit(ValueError):
    pass


def observed(value: Any) -> dict:
    return {"state": "observed", "value": value, "reason": None}


def missing(reason: str = "receipt_not_exposed") -> dict:
    return {"state": "missing", "value": None, "reason": reason}


def not_applicable() -> dict:
    return {"state": "not_applicable", "value": None, "reason": "path_not_applicable"}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def content_hash(tag: str, value: Any) -> str:
    return hashlib.sha256((tag + "\n" + canonical(value)).encode("utf-8")).hexdigest()


def identity_hash(tag: str, value: Any) -> str:
    def validate(v):
        if type(v) is float:
            raise ValueError("floats are not logical identity material")
        if type(v) is dict:
            for k, item in v.items():
                if type(k) is not str:
                    raise ValueError("identity keys must be strings")
                validate(item)
        elif type(v) in (list, tuple):
            for item in v:
                validate(item)
        elif v is not None and type(v) not in (str, bool, int):
            raise ValueError("invalid identity type")
        elif type(v) is int and not -(2**63) <= v < 2**63:
            raise ValueError("identity integer out of range")
    validate(value)
    return content_hash(tag, value)


def freeze(value: Any) -> tuple[Any, int, int]:
    """One bounded copy into tagged immutable tuples; retains no containers.

    Returns (private copy, accounted resident charge, serialized upper bound).
    This is admission accounting, not a calibrated whole-process RSS bound.
    """
    nodes = chars = utf8_bytes = 0
    active: set[int] = set()

    def walk(v, depth=0, key=False):
        nonlocal nodes, chars, utf8_bytes
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            raise CaptureLimit("node/depth limit")
        kind = type(v)
        if kind is str:
            chars += len(v)
            if len(v) > (128 if key else MAX_CHARS) or chars > MAX_CHARS:
                raise CaptureLimit("string limit")
            # Length bounded before encoding, so no unbounded temporary bytes.
            utf8_bytes += len(v.encode("utf-8", errors="strict"))
            if utf8_bytes > 4096:
                raise CaptureLimit("UTF-8 limit")
            return v
        if v is None or kind is bool:
            return v
        if kind is int:
            if not -(2**63) <= v < 2**63:
                raise CaptureLimit("integer limit")
            return v
        if kind is float:
            if not math.isfinite(v):
                raise CaptureLimit("nonfinite")
            return v
        if kind not in (dict, list, tuple):
            raise CaptureLimit("non-primitive or subclass")
        if id(v) in active or len(v) > MAX_NODES:
            raise CaptureLimit("cycle/collection limit")
        active.add(id(v))
        try:
            if kind is dict:
                result = []
                for k, item in v.items():
                    if type(k) is not str:
                        raise CaptureLimit("non-string key")
                    result.append((walk(k, depth + 1, True), walk(item, depth + 1)))
                return ("object", tuple(result))
            return ("array", tuple(walk(item, depth + 1) for item in v))
        finally:
            active.remove(id(v))

    private = walk(value)
    return private, 1024 + 256 * nodes + 8 * chars, 32 * nodes + 6 * chars + 1024


def thaw(value):
    if type(value) is tuple:
        tag, items = value
        if tag == "object":
            return {key: thaw(item) for key, item in items}
        return [thaw(item) for item in items]
    return value


def _dependency_projection(entry):
    wrapper = entry["receipt"]
    if wrapper["state"] == "observed":
        value = wrapper["value"]
        wrapper = observed({k: value[k] for k in (
            "logical_name", "version", "sha256", "size_bytes", "as_of_utc", "missing_members"
        )})
    return {"logical_name": entry["logical_name"], "receipt": wrapper}


def evidence_projection(body: dict, inference=False) -> dict:
    keys = ("occurrence_ref", "target_selection_ref", "execution_state", "model_receipt") \
        if inference else (
            "identity_complete", "occurrence_ref", "selection_ref", "emission_path",
            "rule_receipt", "model_receipt", "consensus_receipt", "fade_receipt",
            "context_price_receipt",
        )
    result = {key: body[key] for key in keys}
    if not inference and body["fade_receipt"]["state"] == "observed":
        value = dict(body["fade_receipt"]["value"])
        del value["parent_observation_ref"]
        del value["parent_inference_ref"]
        result["fade_receipt"] = observed(value)
    entries = body["input_snapshot_refs"]
    names = [entry["logical_name"] for entry in entries]
    if len(set(names)) != len(names):
        raise ValueError("duplicate dependency names")
    result["inputs"] = sorted((_dependency_projection(e) for e in entries),
                              key=lambda e: e["logical_name"])
    return result


def _utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class TemporaryAudit:
    """Explicit development handle. OFF unless the new flag is exactly '1'.

    root must be inside a caller-owned TemporaryDirectory; its lifetime belongs
    to the caller. No production paths are accepted. Runtime calibration and
    durable export are NOT claimed; production construction is unavailable.
    """

    def __init__(self, temporary_directory, *, trading_date: str,
                 invocation_id: str, code_sha: str):
        self.state = "DISABLED"
        self._lock = threading.Lock()
        self._producer = threading.Lock()
        self._queue = deque()
        self._reserved = CONTROL_BYTES
        self._count = 0
        self._close = False
        self._abort = False
        self.dropped = Counter()
        self._wake = threading.Event()
        self.ready = threading.Event()  # Tests may wait; scoring hooks never do.
        self.done = threading.Event()
        self._emissions = Counter()
        self._rows: dict[int, str] = {}  # Writer-only, bounded by RECORD_LIMIT.
        self._inferences: dict[int, str] = {}
        self._thread = None
        self._root = None
        self.build_id = None
        self._build_material = {"producer": "temporary-development", "invocation_id": invocation_id,
                                "trading_date": trading_date, "code_sha": code_sha}
        if os.environ.get("EDGE_FACTORY_MCP_AUDIT") != "1":
            return
        # Type checking prevents arbitrary path-like callbacks or production paths.
        import tempfile
        if type(temporary_directory) is not tempfile.TemporaryDirectory:
            raise ValueError("only caller-owned TemporaryDirectory storage is supported")
        if platform.python_implementation() != "CPython" or sys.platform != "linux":
            return
        self._root = Path(temporary_directory.name)
        self.state = "STARTING"
        try:
            self._thread = threading.Thread(target=self._run, name="mcp-temporary-audit", daemon=True)
            self._thread.start()
        except Exception:
            self.state = "FAILED"
            self.done.set()

    def _drop(self, reason):
        # Best-effort bounded enum counters; no caller waits for shared locks.
        if self._lock.acquire(blocking=False):
            try:
                self.dropped[reason] += 1
            finally:
                self._lock.release()

    def try_capture(self, stage: str, receipt: dict) -> None:
        if self.state == "DISABLED":
            return
        if not self._producer.acquire(blocking=False):
            self._drop("queue_contention")
            return
        reserved = False
        try:
            if getattr(self, "_mailbox", None) is not None or getattr(self, "_cancelled", False):
                self._drop("queue_contention")
                return
            if not self._lock.acquire(blocking=False):
                self._drop("queue_contention")
                return
            try:
                if self.state != "READY" or self._close:
                    self.dropped["startup_not_ready" if self.state == "STARTING" else "closing"] += 1
                    return
                if self._count >= 128 or self._reserved + MAX_RESERVATION > POOL_BYTES:
                    self.dropped["budget_exceeded"] += 1
                    return
                self._reserved += MAX_RESERVATION
                self._count += 1
                reserved = True
            finally:
                self._lock.release()
            private, charge, size = freeze(receipt)
            # A competing writer can briefly own the audit lock. Producer NEVER
            # blocks: publish/refund via its single-owner mailbox instead.
            self._mailbox = (stage, private, charge, size)
            reserved = False
            self._wake.set()
        except Exception:
            self._drop("capture_error")
        finally:
            if reserved:
                # Single producer mailbox also conveys cancellation/refund.
                self._mailbox = None
                self._cancelled = True
                self._wake.set()
            self._producer.release()

    def try_close(self) -> None:
        self._close = True
        self._wake.set()

    def finish(self, timeout: float = 1.0) -> None:
        """Teardown/test-only, outside scoring; never used by evaluator hooks."""
        self.try_close()
        if self._thread and not self.done.wait(min(max(timeout, 0), 1.0)):
            self._abort = True
            self.state = "ABORTED"

    def _emit(self, kind, body, maximum=None):
        envelope = {"schema_version": SCHEMA, "record_type": kind,
                    "build_id": self.build_id, "sequence": self._sequence,
                    "recorded_at_utc": _utc(), "body": body}
        envelope["record_id"] = "mcr1:" + content_hash("mcp-record-v1", envelope)
        raw = (canonical(envelope) + "\n").encode("utf-8")
        if len(raw) > MAX_RECORD_BYTES or (maximum is not None and len(raw) > maximum):
            raise CaptureLimit("serialization estimate exceeded")
        if self._sequence >= RECORD_LIMIT or self._bytes + len(raw) > STREAM_BYTES - CONTROL_BYTES:
            raise CaptureLimit("stream budget exceeded")
        self._file.write(raw)
        self._bytes += len(raw)
        self._counts[kind] += 1
        self._sequence += 1
        return raw

    def _run(self):
        try:
            self.build_id = "mcb1:" + identity_hash("mcp-build-v1", self._build_material)
            self._directory = self._root / self.build_id
            self._directory.mkdir(exist_ok=False)
            self._sequence = self._bytes = 0
            self._counts = Counter()
            with (self._directory / "records-000001.jsonl").open("xb") as self._file:
                self._emit("build_open", {
                    **self._build_material, "dirty_patch_sha256": missing(),
                    "runtime": {"python": sys.version, "platform": sys.platform,
                                "allocation_calibrated": False},
                    "audit_config": {"temporary_only": True, "export_route_state": "unprovisioned"},
                    "input_manifest": [], "coverage_scope": ["development_hooks_partial"],
                    "operational_comparator_contract": missing(),
                })
                self.state = "READY"
                self.ready.set()
                while not self._abort:
                    self._wake.wait(0.01)
                    self._wake.clear()
                    # Mailbox is single-owner until consumed. Producers use the
                    # producer lock; writer can wait, producer never waits.
                    with self._producer:
                        if getattr(self, "_cancelled", False):
                            with self._lock:
                                self._reserved -= MAX_RESERVATION
                                self._count -= 1
                            self._cancelled = False
                        item = getattr(self, "_mailbox", None)
                        self._mailbox = None
                    if item is not None:
                        stage, private, charge, size = item
                        with self._lock:
                            self._reserved -= MAX_RESERVATION - charge
                        try:
                            payload = thaw(private)
                            body, kind = self._prepare(stage, payload)
                            self._emit(kind, body, size)
                        finally:
                            del private
                            item = None
                            with self._lock:
                                self._reserved -= charge
                                self._count -= 1
                    if self._close:
                        with self._producer:
                            if getattr(self, "_mailbox", None) is not None:
                                continue
                            self.state = "CLOSING"
                        break
                if self._abort:
                    return
            preceding = self._directory / "records-000001.jsonl"
            digest = file_digest(preceding)
            with (self._directory / "records-000002.jsonl").open("xb") as self._file:
                self._emit("build_close", {
                    "last_sequence": self._sequence, "counts_by_record_type": {
                        **self._counts, "build_close": 1},
                    "inference_attempts_observed": self._counts["inference_observation"],
                    "emissions_by_path": dict(self._emissions), "dropped_counts_by_reason": dict(self.dropped),
                    "coverage": "partial", "close_reason": "temporary_development",
                    "replay_capabilities": {c: "non_replayable" for c in (
                        "scoring", "selection_context", "full_policy", "ticket")},
                    "export_route_state": "unprovisioned", "segment_bytes": preceding.stat().st_size,
                    "segments": [{"name": preceding.name, "sha256": digest, "size_bytes": preceding.stat().st_size}],
                    "persistence_state": "local_only",
                })
            inventory = []
            for p in sorted(self._directory.glob("records-*.jsonl")):
                inventory.append({"name": p.name, "sha256": file_digest(p),
                                  "size_bytes": p.stat().st_size})
            manifest = {"schema_version": SCHEMA, "build_id": self.build_id,
                        "coverage": "partial", "export_route_state": "unprovisioned",
                        "replay_capabilities": "non_replayable", "files": inventory}
            temporary = self._directory / ".manifest.tmp"
            temporary.write_text(canonical(manifest) + "\n", encoding="utf-8")
            temporary.replace(self._directory / "build-manifest.json")
            if not self._abort:
                self.state = "CLOSED"
        except Exception:
            if not self._abort:
                self.state = "FAILED"
            self._drop("writer_error")
        finally:
            self.ready.set()
            self.done.set()

    def _occurrence(self, payload):
        # No invented team/squad normalization, model contract or entity receipt.
        material = {"identity_contract": "unknown:identity_contract", "entity_map_sha256": None,
                    "trading_date": self._build_material["trading_date"],
                    "home_entity_key": None, "away_entity_key": None, "competition_key": None,
                    "squad_discriminators": {"home": None, "away": None},
                    "kickoff_anchor": {"utc": None, "timezone": None, "normalization_contract": None},
                    "partial_scope": {"build_id": self.build_id, "fixture_input_ordinal": payload["fixture"]}}
        occurrence = "mco1:" + identity_hash("mcp-occurrence-v1", material)
        receipt = observed({"id": occurrence, "material": material, "strength": "partial",
                            "missing_identity_members": ["/entity_map_sha256", "/home_entity_key",
                                "/away_entity_key", "/competition_key", "/squad_discriminators", "/kickoff_anchor"],
                            "raw_identity": {k: payload.get(k) for k in ("date", "home", "away", "competition", "kickoff")}})
        selection = "mcq1:" + identity_hash("mcp-selection-v1", {
            "occurrence_id": occurrence, "market": "1X2", "selection": payload["selection"], "line": None})
        return receipt, observed(selection)

    def _prepare(self, stage, payload):
        if not hasattr(self, "_emissions"):
            self._emissions = Counter()
        if stage == "inference":
            occurrence, selection = self._occurrence(payload)
            ordinal = payload["attempt"]
            identifier = "mci1:" + identity_hash("mcp-inference-v1", {
                "build_id": self.build_id, "inference_attempt_ordinal": ordinal})
            body = {"inference_id": identifier, "inference_attempt_ordinal": ordinal,
                    "occurrence_ref": occurrence, "target_selection_ref": selection,
                    "execution_state": "executed", "model_receipt": observed(payload["model"]),
                    "input_snapshot_refs": []}
            body["evidence_sha256"] = content_hash("mcp-inference-evidence-v1", evidence_projection(body, True))
            self._inferences[ordinal] = identifier
            return body, "inference_observation"
        if stage == "signal":
            occurrence, selection = self._occurrence(payload)
            ordinal = payload["attempt"]
            contract_fields = ("rule_contract_id", "model_contract_id", "feature_contract_id",
                               "election_contract_id", "qualification_contract_id")
            preimage = {"selection_ref": selection["value"], "emission_path": payload["path"],
                        **{k: "unknown:" + k for k in contract_fields},
                        "partial_scope": {"build_id": self.build_id, "emission_attempt_ordinal": ordinal}}
            if payload["path"] == "consensus_unanimous":
                preimage["model_contract_id"] = preimage["feature_contract_id"] = None
            signal = "mcs1:" + identity_hash("mcp-signal-v1", preimage)
            identifier = "mcv1:" + identity_hash("mcp-observation-v1", {
                "build_id": self.build_id, "signal_id": signal, "emission_attempt_ordinal": ordinal})
            parent = self._inferences.get(payload.get("inference"))
            body = {"observation_id": identifier, "signal_id": signal, "identity_complete": False,
                    "occurrence_ref": occurrence, "selection_ref": selection,
                    "emission_path": payload["path"], "emission_attempt_ordinal": ordinal,
                    "input_order": payload["fixture"], "rule_receipt": observed(payload["rule"]),
                    "model_receipt": missing() if parent else not_applicable(),
                    "consensus_receipt": observed(payload["consensus"]) if "consensus" in payload else not_applicable(),
                    "fade_receipt": observed(payload["fade"]) if "fade" in payload else not_applicable(),
                    "context_price_receipt": missing("hook_not_reached"), "input_snapshot_refs": [],
                    "inference_attempt_ref": observed(parent) if parent else missing("hook_not_reached"),
                    "baseline_decision": {"state": "emitted", "reason_code": "baseline",
                                          "emitted_row_ordinal": payload["row"]},
                    "operational_links": missing()}
            body["evidence_sha256"] = content_hash("mcp-evidence-v1", evidence_projection(body))
            self._rows[payload["row"]] = identifier
            self._emissions[payload["path"]] += 1
            return body, "signal_observation"
        if stage == "collapse":
            members = payload["members"]
            body = {"collapse_contract_ref": "incumbent_input_order",
                    "input_row_ordinals": members,
                    "supporting_observation_ids": [self._rows[n] for n in members if n in self._rows],
                    "unlinked_input_ordinals": [n for n in members if n not in self._rows],
                    "representative_input_ordinal": observed(payload["representative"]),
                    "output_row_ordinal": payload["output"], "operational_identity": missing(),
                    "precollapse_row_sha256": missing(), "final_whole_row_sha256": missing(),
                    "link_state": "partial", "reason_codes": ["receipt_not_exposed"]}
            return body, "representative_link"
        raise ValueError("unknown capture stage")


def safe_capture(handle, stage, payload_factory) -> None:
    """No payload construction in default-OFF mode; audit exceptions fail soft."""
    if handle is None or getattr(handle, "state", "DISABLED") == "DISABLED":
        return
    try:
        handle.try_capture(stage, payload_factory())
    except Exception:
        # Does not intercept exceptions outside this audit-only call boundary.
        try:
            handle._drop("capture_error")
        except Exception:
            pass


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
