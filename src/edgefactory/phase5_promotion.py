"""Promote an activated Phase 5 era into the served registry — and back out.

Activation writes the era config under ``localdata/phase5_activation/`` and
nothing else in the repository moves a model into ``localdata/edges_consensus
.json``. The operational guard then reports the live registry as unverified
(the active mode is no longer the dormant incumbent) and ML scoring goes
fail-closed — so activation would otherwise have no effect except switching ML
off. This module is that missing bridge, deliberately narrow:

* it never decides that an activation happened. It reads the activation
  registry and refuses unless the era was activated with a certificate whose
  model key and cut digest match the active config, and unless a matching
  ``activation`` record exists;
* it verifies the POST-state with the operational guard before writing
  (``inspect_operational_registry`` on the registry it is about to write), so a
  promotion the guard would reject cannot reach disk;
* it writes atomically, keeping a byte-for-byte backup of the previous
  registry under ``localdata/phase5_reconciliation/``;
* it benches the ``ml-fade`` family, because those cuts were derived from the
  INCUMBENT model's selection and their certified statistics do not describe
  the new era's selections;
* ``restore_incumbent`` writes the frozen baseline model and cuts back, which
  is the state the guard expects once the era is reverted or the kill switch
  is engaged.

The miner can never do this: ``preserve_live_ml_payload`` carries the live ML
payload forward by design. Only an activated era, verified here, moves it.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edgefactory.phase5_activation import (
    _digest,
    _read_registry,
    _repo_model_key,
    load_incumbent_state,
)
from edgefactory.phase5_k import payload_problems
from edgefactory.phase5_registry_guard import (
    inspect_operational_registry,
    is_ml_rule,
)

DEFAULT_BACKUP_DIRNAME = "phase5_reconciliation"

FADE_BENCH_REASON_PROMOTION = (
    "model era changed: ml-fade cuts were derived from the incumbent "
    "selection and must be re-mined for the activated model"
)
FADE_BENCH_REASON_RESTORE = (
    "incumbent era restored: re-mine ml-fade cuts against the live model"
)


class Phase5PromotionError(RuntimeError):
    """Unsafe or unverifiable promotion/restore input."""


def _utc_now(value: datetime | None = None) -> datetime:
    now = value or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _timestamp(value: datetime | None = None) -> str:
    return _utc_now(value).isoformat(timespec="seconds")


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase5PromotionError(f"registry unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise Phase5PromotionError("registry must be a JSON object")
    return data


def _edges(registry: dict) -> list[dict]:
    edges = registry.get("edges")
    if not isinstance(edges, list):
        raise Phase5PromotionError("registry edges is not a list")
    return [edge for edge in edges if isinstance(edge, dict)]


def _activation_record(records: list[dict], *, era_id: str,
                       model_key: str, cuts_sha256: str) -> dict | None:
    for record in reversed(records):
        if (
            record.get("record_type") == "activation"
            and record.get("era_id") == era_id
            and record.get("candidate_model_key") == model_key
            and record.get("candidate_cuts_sha256") == cuts_sha256
        ):
            return record
    return None


def _benched(edges: list[dict], *, reason: str, at: str) -> list[dict]:
    out = []
    for edge in edges:
        clone = copy.deepcopy(edge)
        clone["status"] = "benched"
        clone["benched_at"] = at
        clone["benched_reason"] = reason
        out.append(clone)
    return out


def _atomic_write_with_backup(path: Path, payload: dict, *,
                              backup_dir: Path, label: str) -> dict:
    path = Path(path)
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = None
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = backup_dir / f"{path.name}.{label}.{stamp}.bak"
        backup.write_bytes(path.read_bytes())
    body = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(body, encoding="utf-8")
    os.replace(temporary, path)
    return {
        "backup": str(backup) if backup else None,
        "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }


def build_promoted_registry(activation_root: Path | str, registry_path: Path | str,
                            *, era_id: str | None = None,
                            now: datetime | None = None) -> tuple[dict, dict]:
    """Return (promoted registry payload, report) without writing anything."""
    activation_root = Path(activation_root)
    baseline, config = load_incumbent_state(activation_root)
    if config.get("mode") != "candidate":
        raise Phase5PromotionError(
            "no activated era is configured (mode is "
            f"{config.get('mode')!r}); activate before promoting"
        )
    if config.get("kill_switch") is not False:
        raise Phase5PromotionError("kill switch is engaged; promotion is refused")
    active_era = str(config.get("era_id") or "")
    if not active_era:
        raise Phase5PromotionError("active era has no era_id")
    if era_id is not None and era_id != active_era:
        raise Phase5PromotionError(
            f"requested era {era_id!r} is not the active era {active_era!r}"
        )

    model = config.get("candidate_model_payload")
    means = config.get("fallback_means")
    method = config.get("fallback_method")
    cuts = config.get("candidate_cuts")
    if not isinstance(cuts, list) or not cuts:
        raise Phase5PromotionError("active era carries no candidate cuts")
    if method != "era_train_slice_mean":
        raise Phase5PromotionError(f"unexpected fallback method: {method!r}")
    problems = payload_problems(model, fallback_means=means, require_fallbacks=True)
    if problems:
        raise Phase5PromotionError("candidate payload invalid: " + "; ".join(problems))
    model_key = _repo_model_key(model)
    if model_key != config.get("active_model_key"):
        raise Phase5PromotionError("candidate payload does not match active_model_key")
    cuts_sha = _digest(cuts)
    if cuts_sha != config.get("active_cuts_sha256"):
        raise Phase5PromotionError("candidate cuts do not match active_cuts_sha256")
    if model_key == baseline.get("incumbent_model_key"):
        raise Phase5PromotionError("active model key equals the incumbent; nothing to promote")

    records = _read_registry(activation_root)
    record = _activation_record(records, era_id=active_era, model_key=model_key,
                               cuts_sha256=cuts_sha)
    if record is None:
        raise Phase5PromotionError(
            "no activation record matches this era, model key and cut digest"
        )

    current = _read_json(registry_path)
    at = _timestamp(now)
    promoted = copy.deepcopy(current)
    promoted["ml_model"] = copy.deepcopy(model)
    promoted["fallback_method"] = method
    promoted["fallback_means"] = copy.deepcopy(means)
    promoted["phase5_era"] = {
        "era_id": active_era,
        "model_key": model_key,
        "promoted_at": at,
        "activation_record_sha256": record.get("record_sha256"),
    }

    non_ml: list[dict] = []
    faded: list[dict] = []
    for edge in _edges(current):
        rule = str(edge.get("rule") or "")
        if not is_ml_rule(rule):
            non_ml.append(copy.deepcopy(edge))
        elif rule.strip().lower().startswith("ml-fade"):
            faded.append(edge)
    promoted["edges"] = non_ml + [copy.deepcopy(edge) for edge in cuts] + _benched(
        faded, reason=FADE_BENCH_REASON_PROMOTION, at=at
    )

    report = {
        "era_id": active_era,
        "model_key": model_key,
        "incumbent_model_key": baseline.get("incumbent_model_key"),
        "candidate_cuts": len(cuts),
        "ml_fade_benched": len(faded),
        "non_ml_edges": len(non_ml),
        "activation_record_sha256": record.get("record_sha256"),
    }
    return promoted, report


def promote_activated_candidate(activation_root: Path | str, registry_path: Path | str,
                                *, era_id: str | None = None, write: bool = False,
                                backup_root: Path | str | None = None,
                                now: datetime | None = None) -> dict:
    """Verify, then (optionally) write, the activated era into the registry."""
    payload, report = build_promoted_registry(
        activation_root, registry_path, era_id=era_id, now=now
    )
    guard = inspect_operational_registry(payload, activation_root)
    if not guard.get("ok"):
        raise Phase5PromotionError(
            f"post-state verification failed: {guard.get('reason')}"
        )
    report["guard"] = guard
    report["written"] = False
    if write:
        registry_path = Path(registry_path)
        backup_dir = Path(backup_root) if backup_root is not None else (
            registry_path.parent / DEFAULT_BACKUP_DIRNAME
        )
        report["write"] = _atomic_write_with_backup(
            registry_path, payload, backup_dir=backup_dir, label="promotion"
        )
        report["written"] = True
    return report


def build_restored_registry(activation_root: Path | str, registry_path: Path | str,
                            *, now: datetime | None = None) -> tuple[dict, dict]:
    """Return (registry payload restored to the frozen incumbent, report)."""
    activation_root = Path(activation_root)
    baseline, _config = load_incumbent_state(activation_root)
    model = baseline.get("incumbent_model")
    cuts = baseline.get("incumbent_cuts")
    if not isinstance(model, dict) or not isinstance(cuts, list) or not cuts:
        raise Phase5PromotionError("immutable baseline lacks a frozen model or cuts")

    current = _read_json(registry_path)
    at = _timestamp(now)
    restored = copy.deepcopy(current)
    restored["ml_model"] = copy.deepcopy(model)
    restored.pop("fallback_means", None)
    restored.pop("fallback_method", None)
    restored["phase5_era"] = {
        "era_id": "incumbent",
        "model_key": baseline.get("incumbent_model_key"),
        "promoted_at": at,
        "restored_at": at,
    }
    non_ml: list[dict] = []
    faded: list[dict] = []
    for edge in _edges(current):
        rule = str(edge.get("rule") or "")
        if not is_ml_rule(rule):
            non_ml.append(copy.deepcopy(edge))
        elif rule.strip().lower().startswith("ml-fade"):
            faded.append(edge)
    restored["edges"] = non_ml + [copy.deepcopy(edge) for edge in cuts] + _benched(
        faded, reason=FADE_BENCH_REASON_RESTORE, at=at
    )
    report = {
        "era_id": "incumbent",
        "model_key": baseline.get("incumbent_model_key"),
        "incumbent_cuts": len(cuts),
        "ml_fade_benched": len(faded),
        "non_ml_edges": len(non_ml),
    }
    return restored, report


def restore_incumbent(activation_root: Path | str, registry_path: Path | str,
                      *, write: bool = False, backup_root: Path | str | None = None,
                      now: datetime | None = None) -> dict:
    """Verify, then (optionally) write, the frozen incumbent back to the registry."""
    payload, report = build_restored_registry(activation_root, registry_path, now=now)
    guard = inspect_operational_registry(payload, activation_root)
    if not guard.get("ok"):
        raise Phase5PromotionError(
            f"post-state verification failed: {guard.get('reason')}"
        )
    report["guard"] = guard
    report["written"] = False
    if write:
        registry_path = Path(registry_path)
        backup_dir = Path(backup_root) if backup_root is not None else (
            registry_path.parent / DEFAULT_BACKUP_DIRNAME
        )
        report["write"] = _atomic_write_with_backup(
            registry_path, payload, backup_dir=backup_dir, label="restore"
        )
        report["written"] = True
    return report
