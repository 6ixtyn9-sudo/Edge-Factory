"""Narrow, audited reconciliation of the operational ML incumbent.

This module can restore only the frozen Phase 5 ML model/cut payload. It never
copies the complete baseline registry, promotes a missing/benched/candidate
cut, or changes non-ML rules, tickets, settlements, or bank state.
"""
from __future__ import annotations

import copy
import csv
import gzip
import hashlib
import json
import os
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edgefactory.ml_fade_research import model_key
from edgefactory.phase5_activation import (
    Phase5ActivationError,
    load_incumbent_state,
)
from edgefactory.phase5_registry_guard import inspect_operational_registry

EXPECTED_INCUMBENT_MODEL_KEY = "a45beab0c878"
_DYNAMIC_CUT_FIELDS = frozenset({"status", "decay", "benched_at"})
_RESTRICTIVE_STATUSES = frozenset({"candidate", "benched"})


class Phase5ReconciliationError(RuntimeError):
    """Unsafe or unverifiable incumbent reconciliation input."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _independent_model_key(model: object) -> str | None:
    """Recompute the model identity without calling the repository helper."""
    if not isinstance(model, dict) or not model:
        return None
    return _sha256_bytes(_canonical_json(model).encode("utf-8"))[:12]


def _independent_cut_digest(cuts: object) -> str:
    payload = json.dumps(
        cuts, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return _sha256_bytes(payload)


def verify_designated_baseline(
    activation_root: Path | str,
    *,
    expected_model_key: str = EXPECTED_INCUMBENT_MODEL_KEY,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    """Load and independently verify the one designated, dormant incumbent."""
    try:
        baseline, config = load_incumbent_state(activation_root)
    except (Phase5ActivationError, OSError, ValueError, TypeError) as exc:
        raise Phase5ReconciliationError(
            f"immutable Phase 5 baseline could not be validated: {type(exc).__name__}: {exc}"
        ) from exc

    payload = baseline.get("incumbent_model")
    helper_key = model_key(payload)
    independent_key = _independent_model_key(payload)
    stored_key = baseline.get("incumbent_model_key")
    checks = {
        "designated_key": expected_model_key,
        "stored_key": str(stored_key or ""),
        "repository_model_key": str(helper_key or ""),
        "independent_model_key": str(independent_key or ""),
    }
    if any(value != expected_model_key for value in checks.values()):
        raise Phase5ReconciliationError(
            "frozen model identity does not independently match the designated incumbent: "
            + json.dumps(checks, sort_keys=True)
        )

    cuts = baseline.get("incumbent_cuts")
    cut_digest = _independent_cut_digest(cuts)
    if (
        not isinstance(cuts, list)
        or not cuts
        or cut_digest != baseline.get("incumbent_cuts_sha256")
        or config.get("mode") != "incumbent"
        or config.get("kill_switch") is not False
        or config.get("active_model_key") != expected_model_key
        or config.get("active_cuts_sha256") != cut_digest
        or baseline.get("immutable") is not True
    ):
        raise Phase5ReconciliationError(
            "frozen cut/config identity is not the verified dormant incumbent"
        )
    return baseline, config, checks


def _is_meta_rule(rule: object) -> bool:
    return str(rule or "").strip().lower().startswith("ml-meta")


def _meta_edges(edges: object, *, strict: bool) -> dict[str, dict[str, Any]]:
    if not isinstance(edges, list):
        raise Phase5ReconciliationError("registry edges must be a list")
    found: dict[str, dict[str, Any]] = {}
    for edge in edges:
        if not isinstance(edge, dict) or not _is_meta_rule(edge.get("rule")):
            continue
        rule = edge.get("rule")
        if not isinstance(rule, str) or not rule.strip():
            raise Phase5ReconciliationError("ML-meta edge has no rule identity")
        if rule in found:
            raise Phase5ReconciliationError(f"duplicate live ML-meta rule: {rule}")
        found[rule] = edge
    if strict and any(not isinstance(edge, dict) for edge in edges):
        # Preserve opaque non-ML rows, but do not permit them to obscure a
        # protected ML identity during an audited reconciliation.
        raise Phase5ReconciliationError("registry contains a non-object edge record")
    return found


def _json_differences(before: Any, after: Any, path: str) -> list[dict[str, Any]]:
    differences: list[dict[str, Any]] = []
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(set(before) | set(after)):
            child = f"{path}.{key}" if path else key
            if key not in before:
                differences.append({"path": child, "before": "<missing>", "after": after[key]})
            elif key not in after:
                differences.append({"path": child, "before": before[key], "after": "<missing>"})
            else:
                differences.extend(_json_differences(before[key], after[key], child))
    elif isinstance(before, list) and isinstance(after, list) and len(before) == len(after):
        for index, (old, new) in enumerate(zip(before, after)):
            differences.extend(_json_differences(old, new, f"{path}[{index}]"))
    elif before != after:
        differences.append({"path": path, "before": before, "after": after})
    return differences


def _safe_status(baseline_status: object, live_status: object, *, missing: bool) -> object:
    """Keep every existing no-emission state; never promote a protected cut."""
    if missing or not isinstance(live_status, str) or not live_status:
        return "benched" if baseline_status == "certified" else baseline_status
    if baseline_status == "benched" or live_status == "benched":
        return "benched"
    if baseline_status == "candidate" or live_status == "candidate":
        return "candidate"
    if baseline_status == live_status == "certified":
        return "certified"
    # Preserve an unfamiliar current state as-is; the operational verifier
    # fails closed on it instead of treating it as a certification.
    return live_status


def _reconcile_cut(
    baseline_edge: dict[str, Any],
    live_edge: dict[str, Any] | None,
) -> dict[str, Any]:
    if live_edge is None:
        result = copy.deepcopy(baseline_edge)
    else:
        # Keep the operational file's existing field order. Replace only the
        # protected static values, retain dynamic bench metadata, and drop
        # unrecognized live fields; append newly restored baseline fields.
        result = {}
        for field, live_value in live_edge.items():
            if field in _DYNAMIC_CUT_FIELDS:
                result[field] = copy.deepcopy(live_value)
            elif field in baseline_edge:
                result[field] = copy.deepcopy(baseline_edge[field])
        for field, baseline_value in baseline_edge.items():
            if field not in result:
                result[field] = copy.deepcopy(baseline_value)
    result["status"] = _safe_status(
        baseline_edge.get("status"),
        live_edge.get("status") if live_edge is not None else None,
        missing=live_edge is None,
    )
    if live_edge is not None:
        for field in ("decay", "benched_at"):
            if field in live_edge:
                result[field] = copy.deepcopy(live_edge[field])
    return result


def _edge_diff_report(
    baseline_edges: dict[str, dict[str, Any]],
    live_edges: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    for rule in sorted(set(baseline_edges) | set(live_edges)):
        expected = baseline_edges.get(rule)
        current = live_edges.get(rule)
        if expected is None:
            report.append({"rule": rule, "kind": "extra_live_cut", "live": current})
            continue
        if current is None:
            report.append({
                "rule": rule,
                "kind": "missing_live_cut",
                "baseline_status": expected.get("status"),
                "disposition": "restore_definition_benched_if_baseline_was_certified",
            })
            continue
        definition_diffs = _json_differences(
            {key: value for key, value in expected.items() if key not in _DYNAMIC_CUT_FIELDS},
            {key: value for key, value in current.items() if key not in _DYNAMIC_CUT_FIELDS},
            "",
        )
        status_diff = (
            {
                "baseline": expected.get("status", "<missing>"),
                "live": current.get("status", "<missing>"),
            }
            if current.get("status") != expected.get("status") else None
        )
        baseline_dynamic = {key: value for key, value in expected.items()
                            if key in {"decay", "benched_at"}}
        live_dynamic = {key: value for key, value in current.items()
                        if key in {"decay", "benched_at"}}
        dynamic_diffs = _json_differences(
            baseline_dynamic, live_dynamic, "dynamic"
        )
        if definition_diffs or status_diff or dynamic_diffs:
            report.append({
                "rule": rule,
                "kind": "definition_status_or_dynamic_metadata_difference",
                "definition_differences": definition_diffs,
                "status_difference": status_diff,
                "dynamic_decay_and_bench_differences": dynamic_diffs,
                "live_status_preserved_as": _safe_status(
                    expected.get("status"), current.get("status"), missing=False
                ),
                "dynamic_decay_and_bench_metadata": "preserved_from_live_registry",
            })
    return report


def build_reconciliation_plan(
    current_registry: dict[str, Any],
    baseline: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Restore only the baseline model/protected cuts; preserve all other rules."""
    if not isinstance(current_registry, dict):
        raise Phase5ReconciliationError("operational registry must be a JSON object")
    current_edges = current_registry.get("edges")
    baseline_cuts = baseline.get("incumbent_cuts")
    baseline_edges = _meta_edges(baseline_cuts, strict=True)
    live_edges = _meta_edges(current_edges, strict=True)
    if not baseline_edges:
        raise Phase5ReconciliationError("verified baseline has no ML-meta cuts")

    reconciled = copy.deepcopy(current_registry)
    reconciled["ml_model"] = copy.deepcopy(baseline["incumbent_model"])
    output_edges: list[Any] = []
    emitted: set[str] = set()
    for edge in current_edges:
        if not isinstance(edge, dict) or not _is_meta_rule(edge.get("rule")):
            output_edges.append(copy.deepcopy(edge))
            continue
        rule = edge.get("rule")
        if rule not in baseline_edges:
            # The full displaced registry remains in the audit copy.
            continue
        output_edges.append(_reconcile_cut(baseline_edges[rule], live_edges[rule]))
        emitted.add(rule)
    for rule in sorted(set(baseline_edges) - emitted):
        # A missing certified cut is restored only as benched, never active.
        output_edges.append(_reconcile_cut(baseline_edges[rule], None))
    reconciled["edges"] = output_edges

    before_non_ml = [
        edge for edge in current_edges
        if not _is_meta_rule(edge.get("rule"))
        and not str(edge.get("rule", "")).strip().lower().startswith("ml-fade")
    ]
    after_non_ml = [
        edge for edge in reconciled["edges"]
        if not _is_meta_rule(edge.get("rule"))
        and not str(edge.get("rule", "")).strip().lower().startswith("ml-fade")
    ]
    if before_non_ml != after_non_ml:
        raise Phase5ReconciliationError("plan changed a non-ML operational edge")

    before_fade = [edge for edge in current_edges if isinstance(edge, dict)
                   and str(edge.get("rule", "")).strip().lower().startswith("ml-fade")]
    after_fade = [edge for edge in reconciled["edges"] if isinstance(edge, dict)
                  and str(edge.get("rule", "")).strip().lower().startswith("ml-fade")]
    if before_fade != after_fade:
        raise Phase5ReconciliationError("plan changed an ML-fade edge outside the frozen cut set")

    report = {
        "before_model_key": model_key(current_registry.get("ml_model")),
        "after_model_key": model_key(reconciled.get("ml_model")),
        "model_differences": _json_differences(
            current_registry.get("ml_model"), baseline.get("incumbent_model"), "ml_model"
        ),
        "protected_cut_differences": _edge_diff_report(baseline_edges, live_edges),
        "extra_ml_meta_rules_removed": sorted(set(live_edges) - set(baseline_edges)),
        "missing_ml_meta_rules_added_benched_or_baseline_status": sorted(
            set(baseline_edges) - set(live_edges)
        ),
        "preserved_statuses": {
            rule: reconciled_edge.get("status")
            for rule, reconciled_edge in (
                (edge["rule"], edge)
                for edge in reconciled["edges"]
                if isinstance(edge, dict) and edge.get("rule") in baseline_edges
            )
        },
        "preserved_non_ml_edge_count": len(after_non_ml),
        "preserved_ml_fade_edge_count": len(after_fade),
        "registry": reconciled,
    }
    return reconciled, report


def _historical_model_inventory(localdata: Path) -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for name in ("ml_meta_predictions.csv.gz", "ml_meta_predictions_research.csv.gz"):
        path = localdata / name
        if not path.exists():
            inventory[name] = {"present": False}
            continue
        counts: Counter[str] = Counter()
        fieldnames: list[str] | None = None
        try:
            with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                fieldnames = reader.fieldnames
                if "model_key" in (fieldnames or []):
                    counts.update(row.get("model_key") or "<missing>" for row in reader)
            inventory[name] = {
                "present": True,
                "sha256": _sha256_bytes(path.read_bytes()),
                "fieldnames": fieldnames,
                "rows_by_model_key": dict(sorted(counts.items())),
            }
        except (OSError, EOFError, UnicodeDecodeError, csv.Error) as exc:
            inventory[name] = {
                "present": True,
                "sha256": _sha256_bytes(path.read_bytes()),
                "read_error": type(exc).__name__,
            }

    ledger = localdata / "ml_fade_research_ledger.json"
    if not ledger.exists():
        inventory[ledger.name] = {"present": False}
    else:
        try:
            payload = json.loads(ledger.read_text(encoding="utf-8"))
            rows = payload.get("rows", []) if isinstance(payload, dict) else []
            counts = Counter(
                str(row.get("model_key") or "<missing>")
                for row in rows if isinstance(row, dict)
            )
            inventory[ledger.name] = {
                "present": True,
                "sha256": _sha256_bytes(ledger.read_bytes()),
                "rows": len(rows),
                "rows_by_model_key": dict(sorted(counts.items())),
            }
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
            inventory[ledger.name] = {
                "present": True,
                "sha256": _sha256_bytes(ledger.read_bytes()),
                "read_error": type(exc).__name__,
            }
    return inventory


def _write_exclusive(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def apply_reconciliation(
    registry_path: Path | str,
    activation_root: Path | str,
    audit_root: Path | str,
    *,
    expected_model_key: str = EXPECTED_INCUMBENT_MODEL_KEY,
    audit_id: str | None = None,
) -> dict[str, Any]:
    """Write an exclusive before-image/receipt, then atomically reconcile ML only."""
    registry_path = Path(registry_path)
    audit_root = Path(audit_root)
    baseline, config, checks = verify_designated_baseline(
        activation_root, expected_model_key=expected_model_key
    )
    try:
        original_bytes = registry_path.read_bytes()
        current = json.loads(original_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase5ReconciliationError(
            f"operational registry cannot be read: {type(exc).__name__}"
        ) from exc
    planned, report = build_reconciliation_plan(current, baseline)
    guard = inspect_operational_registry(planned, activation_root)
    if not guard["ok"]:
        raise Phase5ReconciliationError(
            f"reconciled ML registry would remain blocked: {guard['reason']}"
        )

    audit_id = audit_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit_dir = audit_root / audit_id
    audit_dir.mkdir(parents=True, exist_ok=False)
    before_name = "displaced_edges_consensus.json"
    _write_exclusive(audit_dir / before_name, original_bytes)
    planned_bytes = (json.dumps(planned, indent=2, sort_keys=False) + "\n").encode("utf-8")
    receipt = {
        "schema": 1,
        "record_type": "phase5_incumbent_reconciliation_receipt",
        "audit_id": audit_id,
        "prepared_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "state": "prepared_before_operational_write",
        "designated_incumbent_model_key": expected_model_key,
        "baseline_verification": checks,
        "baseline_cuts_sha256": baseline.get("incumbent_cuts_sha256"),
        "active_config": {
            "mode": config.get("mode"),
            "kill_switch": config.get("kill_switch"),
            "active_model_key": config.get("active_model_key"),
            "active_cuts_sha256": config.get("active_cuts_sha256"),
        },
        "displaced_registry": {
            "path": str(registry_path),
            "sha256": _sha256_bytes(original_bytes),
            "audit_copy": before_name,
            "ml_model_key": report["before_model_key"],
            "protected_cut_differences": report["protected_cut_differences"],
            "model_differences": report["model_differences"],
        },
        "planned_registry": {
            "sha256": _sha256_bytes(planned_bytes),
            "ml_model_key": report["after_model_key"],
            "preserved_statuses": report["preserved_statuses"],
            "removed_extra_ml_meta_rules": report["extra_ml_meta_rules_removed"],
            "added_missing_ml_meta_rules": report["missing_ml_meta_rules_added_benched_or_baseline_status"],
            "non_ml_edge_count": report["preserved_non_ml_edge_count"],
            "ml_fade_edge_count": report["preserved_ml_fade_edge_count"],
            "guard": guard,
        },
        "historical_model_era_inventory_unchanged_by_this_operation": _historical_model_inventory(
            registry_path.parent
        ),
        "full_plan": report,
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _write_exclusive(audit_dir / "reconciliation_receipt.json", receipt_bytes)

    temporary = registry_path.with_name(
        f".{registry_path.name}.{audit_id}.tmp"
    )
    _write_exclusive(temporary, planned_bytes)
    os.replace(temporary, registry_path)
    final_bytes = registry_path.read_bytes()
    applied = {
        "schema": 1,
        "record_type": "phase5_incumbent_reconciliation_applied",
        "audit_id": audit_id,
        "applied_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "registry_sha256": _sha256_bytes(final_bytes),
        "registry_model_key": model_key(json.loads(final_bytes).get("ml_model")),
        "baseline_model_key": expected_model_key,
        "guard": inspect_operational_registry(json.loads(final_bytes), activation_root),
        "historical_model_era_inventory_after": _historical_model_inventory(registry_path.parent),
    }
    _write_exclusive(
        audit_dir / "applied_receipt.json",
        (json.dumps(applied, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    if applied["registry_model_key"] != expected_model_key or not applied["guard"]["ok"]:
        raise Phase5ReconciliationError("post-write registry failed incumbent readback")
    return {"audit_dir": str(audit_dir), "prepared": receipt, "applied": applied}
