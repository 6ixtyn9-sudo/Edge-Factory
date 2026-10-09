"""Default-OFF MCP audit collector: explicit temporary-storage development only.

No operational consumer reads these records. There is deliberately no production
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
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "mcp-audit/development-v1"
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
    validate_wrapper(wrapper)
    if wrapper["state"] == "observed":
        value = wrapper["value"]
        if value["logical_name"] != entry["logical_name"]:
            raise ValueError("inconsistent dependency name")
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
        self._scopes = 0
        self._spool = None
        self._loss_unknown = False
        self._emissions = Counter()
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
        if (platform.python_implementation() != "CPython" or sys.platform != "linux"
                or sys.version != "3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]"
                or not getattr(sys, "_is_gil_enabled", lambda: True)()):
            return
        self._root = Path(temporary_directory.name)
        from edgefactory.ml_consensus_storage import TemporarySpool
        self._spool = TemporarySpool(temporary_directory)
        self.state = "STARTING"
        try:
            self._thread = threading.Thread(target=self._run, name="mcp-temporary-audit", daemon=True)
            self._thread.start()
        except Exception:
            self.state = "FAILED"
            self.done.set()

    @property
    def state(self):
        return "ABORTED" if getattr(self, "_abort", False) else self._state

    @state.setter
    def state(self, value):
        self._state = value

    def _drop(self, reason):
        # Best-effort bounded enum counters; no caller waits for shared locks.
        if self._lock.acquire(blocking=False):
            try:
                self.dropped[reason] += 1
            finally:
                self._lock.release()
        else:
            self._loss_unknown = True

    def try_capture(self, stage, receipt):
        self.capture_factory(stage, lambda: receipt)

    def capture_factory(self, stage, factory):
        # A single audit-only critical section owns admission, copying and
        # publication. Producers never wait; the worker may wait for copying.
        if self.state == "DISABLED":
            return
        if not self._producer.acquire(False):
            self._drop("queue_contention")
            return
        reserved = False
        try:
            if self.state != "READY" or self._close:
                self._drop("startup_not_ready" if self.state == "STARTING" else "closing")
                return
            if self._count >= 128 or self._reserved + MAX_RESERVATION > POOL_BYTES:
                self._drop("budget_exceeded")
                return
            self._reserved += MAX_RESERVATION
            self._count += 1
            reserved = True
            private, charge, size = freeze(factory())
            if self._close or self._abort:
                self._drop("closing")
                return
            self._queue.append((stage, private, charge, size))
            self._reserved -= MAX_RESERVATION - charge
            reserved = False
        except Exception:
            self._drop("capture_error")
        finally:
            if reserved:
                self._reserved -= MAX_RESERVATION
                self._count -= 1
            self._producer.release()

    def try_close(self) -> None:
        self._close = True

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
            raise RuntimeError("serialization estimate exceeded")
        limit = STREAM_BYTES if kind == "build_close" else STREAM_BYTES - CONTROL_BYTES
        count_limit = RECORD_LIMIT if kind == "build_close" else RECORD_LIMIT - 1
        if self._sequence >= count_limit or self._bytes + len(raw) > limit:
            raise RuntimeError("stream budget exceeded")
        if self._spool is not None:
            self._spool.check_growth(len(raw))
        self._file.write(raw)
        self._bytes += len(raw)
        self._counts[kind] += 1
        self._sequence += 1
        return raw

    def _run(self):
        try:
            self.build_id = "mcb1:" + identity_hash("mcp-build-v1", self._build_material)
            self._directory = self._spool.reserve(self.build_id)
            self._sequence = self._bytes = 0
            self._counts = Counter()
            with (self._directory / "records-000001.jsonl").open("xb") as self._file:
                self._emit("build_open", {
                    **self._build_material, "dirty_patch_sha256": missing(),
                    "runtime": {"python": sys.version, "platform": sys.platform,
                                "allocation_calibrated": False},
                    "audit_config": {"temporary_only": True, "export_route_state": "unprovisioned"},
                    "input_manifest": dependency_inventory(), "coverage_scope": ["development_hooks_partial"],
                    "operational_comparator_contract": missing(),
                })
                with self._producer:
                    if self._abort:
                        return
                    self.state = "READY"
                self.ready.set()
                while not self._abort:
                    if not self._queue and not self._close:
                        self._wake.wait(0.005)
                    with self._producer:
                        item = self._queue.popleft() if self._queue else None
                        closing = self._close and item is None
                        if closing:
                            self.state = "CLOSING"
                    if item is not None:
                        try:
                            stage, private, charge, size = item
                            payload = thaw(private)
                            body, kind = self._prepare(stage, payload)
                            self._emit(kind, body, size)
                        except (CaptureLimit, ValueError, TypeError, KeyError):
                            self._drop("serialization_error")
                        finally:
                            item = private = payload = body = None
                            with self._producer:
                                self._reserved -= charge
                                self._count -= 1
                    if closing:
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
                    "coverage": "unknown" if self._loss_unknown else "partial", "close_reason": "temporary_development",
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
            manifest_raw = canonical(manifest) + "\n"
            if len(manifest_raw.encode("utf-8")) > CONTROL_BYTES:
                raise CaptureLimit("manifest limit")
            self._spool.check_growth(len(manifest_raw.encode("utf-8")))
            temporary.write_text(manifest_raw, encoding="utf-8")
            if self._abort:
                return
            temporary.replace(self._directory / "build-manifest.json")
            if not self._abort:
                self.state = "CLOSED"
        except Exception:
            if not self._abort:
                self.state = "FAILED"
            self._drop("writer_error")
        finally:
            with self._producer:
                self._queue.clear()
                self._count = 0
                self._reserved = CONTROL_BYTES
            if self._spool is not None:
                self._spool.close()
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
        if stage in ("emission", "collapse_choice", "collapse_final", "decision"):
            if stage == "emission" and "path" in payload:
                self._emissions[payload["path"]] += 1
            return payload, {"emission": "emission_observation",
                             "collapse_choice": "collapse_observation", "collapse_final": "collapse_final",
                             "decision": "decision_observation"}[stage]
        if stage == "inference":
            if len(payload["model"]["x"]) > 512:
                raise CaptureLimit("feature limit")
            occurrence, selection = self._occurrence(payload)
            ordinal = payload["attempt"]
            identifier = "mci1:" + identity_hash("mcp-inference-v1", {
                "build_id": self.build_id, "inference_attempt_ordinal": ordinal})
            body = {"inference_id": identifier, "inference_attempt_ordinal": ordinal,
                    "occurrence_ref": occurrence, "target_selection_ref": selection,
                    "execution_state": "executed", "model_receipt": observed(payload["model"]),
                    "input_snapshot_refs": dependency_inventory()}
            body["evidence_sha256"] = content_hash("mcp-inference-evidence-v1", evidence_projection(body, True))
            return body, "inference_observation"
        raise ValueError("unknown capture stage")


def safe_capture(handle, stage, payload_factory) -> None:
    """No payload construction in default-OFF mode; audit exceptions fail soft."""
    try:
        if handle is None or getattr(handle, "state", "DISABLED") == "DISABLED":
            return
        if hasattr(handle, "capture_factory"):
            handle.capture_factory(stage, payload_factory)
        else:
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


def read_temporary_build(directory):
    """Offline integrity reader for development receipts, not v1 validation.

    Requires a finalized manifest and verifies every segment before returning
    records. Never used by operational scoring, settlement or archive code.
    """
    directory = Path(directory)
    manifest_path = directory / 'build-manifest.json'
    if manifest_path.is_symlink() or manifest_path.stat().st_size > CONTROL_BYTES:
        raise ValueError('unsafe manifest')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('schema_version') != SCHEMA:
        raise ValueError('unsupported schema')
    files = manifest['files']
    if not isinstance(files, list) or not 1 <= len(files) <= 64:
        raise ValueError('invalid inventory')
    records, names, identities = [], set(), {}
    total = 0
    for entry in files:
        name = entry['name']
        if (type(name) is not str or '/' in name or '\\' in name
                or not name.startswith('records-') or not name.endswith('.jsonl') or name in names):
            raise ValueError('unsafe or duplicate segment')
        names.add(name)
        path = directory / name
        total += entry['size_bytes']
        if total > STREAM_BYTES or path.is_symlink() or path.stat().st_size != entry['size_bytes']:
            raise ValueError('segment size mismatch')
        if file_digest(path) != entry['sha256']:
            raise ValueError('segment digest mismatch')
        with path.open('rb') as stream:
            while raw := stream.readline(MAX_RECORD_BYTES + 1):
                if len(raw) > MAX_RECORD_BYTES or not raw.endswith(b'\n'):
                    raise ValueError('oversized or unterminated record')
                record = json.loads(raw)
                if (canonical(record) + '\n').encode('utf-8') != raw:
                    raise ValueError('noncanonical record')
                if (record['schema_version'] != SCHEMA or record['build_id'] != manifest['build_id']
                        or record['sequence'] != len(records)):
                    raise ValueError('record envelope mismatch')
                for key in ('inference_id', 'observation_id'):
                    identifier = record['body'].get(key)
                    if identifier is not None:
                        if identifier in identities:
                            raise ValueError('duplicate identity')
                        identities[identifier] = raw
                validate_development_record(record)
                records.append(record)
                if len(records) > RECORD_LIMIT:
                    raise ValueError('record count exceeded')
    if records[0]['record_type'] != 'build_open' or records[-1]['record_type'] != 'build_close':
        raise ValueError('unclosed build')
    close = records[-1]['body']
    if close['segments'] != files[:-1] or close['segment_bytes'] != sum(e['size_bytes'] for e in files[:-1]):
        raise ValueError('close inventory mismatch')
    if close['last_sequence'] != records[-1]['sequence']:
        raise ValueError('close sequence mismatch')
    if close['counts_by_record_type'] != dict(Counter(r['record_type'] for r in records)):
        raise ValueError('close counts mismatch')
    return manifest, records


DEPENDENCIES = (
    "source_snapshots", "date_eligibility", "model_bytes", "guard_activation",
    "feature_contract", "rolling_hit_rate", "registry", "entity_overrides",
    "purity_context_debias_veto", "competition_prices", "ticket_bank_ladder_freeze",
)


def dependency_inventory():
    return [{"logical_name": name, "receipt": missing("dependency_unavailable")}
            for name in DEPENDENCIES]


class _Scope:
    def __init__(self, handle, ordinal):
        self.handle, self.ordinal = handle, ordinal

    @property
    def state(self):
        return self.handle.state

    def capture_factory(self, stage, factory):
        def scoped():
            payload = factory()
            # Declared coordinates: no inference from surviving labels/rows.
            payload["evaluation_ordinal"] = self.ordinal
            for field in ("fixture", "attempt", "row", "inference"):
                if field in payload:
                    value = payload[field]
                    if type(value) is not int or not 0 <= value < RECORD_LIMIT:
                        raise CaptureLimit("local ordinal limit")
                    payload[field] = self.ordinal * RECORD_LIMIT + value
            return payload
        self.handle.capture_factory(stage, scoped)

    def _drop(self, reason):
        self.handle._drop(reason)


def evaluation_scope(handle):
    """Read-only evaluation namespace; even dropped receipts cannot reuse IDs."""
    try:
        if not isinstance(handle, TemporaryAudit):
            return handle
        if handle.state == "DISABLED":
            return None
        if not handle._producer.acquire(False):
            handle._drop("queue_contention")
            return None
        try:
            if handle._scopes >= RECORD_LIMIT:
                handle._drop("budget_exceeded")
                return None
            ordinal = handle._scopes
            handle._scopes += 1
            return _Scope(handle, ordinal)
        finally:
            handle._producer.release()
    except Exception:
        return None


def emitted_fields(row):
    # Positive projection, never a whole-pick traversal or provenance mutation.
    return {key: row.get(key) for key in (
        "date", "home", "away", "league", "kickoff", "market", "pick",
        "avg_p", "w_score", "odds", "odds_source", "rule", "n_way", "edge_n_way")}


RECORD_FIELDS = {
    "build_open": {"trading_date", "producer", "invocation_id", "code_sha", "runtime", "audit_config", "input_manifest"},
    "inference_observation": {"inference_id", "inference_attempt_ordinal", "occurrence_ref", "target_selection_ref", "execution_state", "model_receipt", "input_snapshot_refs", "evidence_sha256"},
    "emission_observation": {"row"},
    "decision_observation": {"stage"},
    "collapse_observation": {"members", "representative", "pre_sort_output"},
    "collapse_final": {"pre_sort_ordinals", "link_state", "reason"},
    "build_close": {"last_sequence", "counts_by_record_type", "segments", "segment_bytes", "coverage", "replay_capabilities", "export_route_state"},
}


def validate_development_record(record):
    """Strict development envelope/integrity validation; rejects v1 inputs."""
    keys = {"schema_version", "record_type", "build_id", "record_id", "sequence", "recorded_at_utc", "body"}
    if type(record) is not dict or set(record) != keys or record['schema_version'] != SCHEMA:
        raise ValueError('unsupported envelope')
    kind, body = record['record_type'], record['body']
    if kind not in RECORD_FIELDS or type(body) is not dict or not RECORD_FIELDS[kind] <= body.keys():
        raise ValueError('invalid record body')
    if type(record['sequence']) is not int or record['sequence'] < 0:
        raise ValueError('invalid sequence')
    preimage = {k: v for k, v in record.items() if k != 'record_id'}
    if record['record_id'] != 'mcr1:' + content_hash('mcp-record-v1', preimage):
        raise ValueError('record digest mismatch')
    if kind == 'inference_observation':
        if body['execution_state'] != 'executed':
            raise ValueError('invalid execution')
        for key in ('occurrence_ref', 'target_selection_ref', 'model_receipt'):
            validate_wrapper(body[key])
        if body['evidence_sha256'] != content_hash('mcp-inference-evidence-v1', evidence_projection(body, True)):
            raise ValueError('inference evidence mismatch')
    if kind == 'build_close' and body['coverage'] not in ('partial', 'unknown'):
        raise ValueError('development build cannot claim complete coverage')


def validate_wrapper(wrapper):
    if type(wrapper) is not dict or set(wrapper) != {'state', 'value', 'reason'}:
        raise ValueError('invalid evidence wrapper')
    state = wrapper['state']
    if state == 'observed':
        if wrapper['reason'] is not None:
            raise ValueError('observed reason')
    elif state in ('missing', 'failed', 'not_applicable'):
        if wrapper['value'] is not None or wrapper['reason'] not in REASONS:
            raise ValueError('invalid missing evidence')
    else:
        raise ValueError('unknown evidence state')


REASONS = frozenset((
    'hook_not_reached', 'receipt_not_exposed', 'dependency_unavailable', 'ambiguous_identity',
    'no_inference', 'path_not_applicable', 'serialization_error', 'size_limit', 'writer_error',
    'budget_exceeded', 'capture_error', 'startup_not_ready', 'queue_contention', 'closing',
    'fallback_origin_unavailable', 'dependency_expired', 'abandoned_build', 'quota_unavailable',
    'invariant_breach',
))
