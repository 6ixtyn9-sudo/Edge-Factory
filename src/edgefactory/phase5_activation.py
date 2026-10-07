"""Fail-closed Phase 5 activation state machine.

This module is deliberately dormant: production pick/ticket paths do not import
it. It owns one active-era config and a hash-chained append-only research
registry, snapshots the incumbent model/cuts without modifying the production
registry, and permits a candidate config only from a complete passing verdict.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DECLARED_SOURCE_ORDER = ("vitibet", "bzzoiro", "betclan", "scoutingstats", "betminer")
BASE_FEATURES = (
    "fb_p", "zb_p", "sa_p", "avg_p", "min_p", "std_p", "pick_odds",
    "is_home", "is_away", "cat_friendly", "cat_youth", "cat_women",
    "cat_cup", "cat_league", "rolling_hit_rate", "kelly", "pred_total",
    "pred_diff", "goalsavg", "p_ng", "p_under", "p_gg",
)
K_FEATURES = BASE_FEATURES + tuple(
    feature
    for source in DECLARED_SOURCE_ORDER
    for feature in (f"{source}_p", f"{source}_available")
)
PASS_STATUSES = {"pass", "pass_with_source_exclusions"}
REGISTRY_EVENT_TYPES = {
    "revert_dry_run", "activation", "kill_switch", "revert",
}
COOLDOWN = timedelta(days=30)
REVERT_DRY_RUN_MAX_AGE = timedelta(hours=24)


class Phase5ActivationError(ValueError):
    """Invalid activation state or a failed safety precondition."""


class Phase5NotYetDue(Phase5ActivationError):
    """No complete passing certification verdict exists yet."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest(value: Any) -> str:
    return _sha256_bytes(_canonical(value))


def _utc_now(value: datetime | None = None) -> datetime:
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise Phase5ActivationError("activation timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _timestamp(value: datetime | None = None) -> str:
    return _utc_now(value).isoformat(timespec="seconds")


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _repo_model_key(payload: dict[str, Any]) -> str:
    # Use the repository's canonical model identity implementation exactly.
    from edgefactory.ml_fade_research import model_key

    key = model_key(payload)
    if not key:
        raise Phase5ActivationError("model_key() returned no candidate identity")
    return key


def _read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except FileNotFoundError as exc:
        raise Phase5ActivationError(f"required file is missing: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase5ActivationError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Phase5ActivationError(f"expected a JSON object in {path}")
    return value, raw


def _registry_path(root: Path) -> Path:
    return root / "registry.jsonl"


def _active_path(root: Path) -> Path:
    return root / "active_era.json"


def _seal(record: dict[str, Any], previous_digest: str | None) -> dict[str, Any]:
    sealed = dict(record)
    sealed["previous_record_sha256"] = previous_digest
    sealed["record_sha256"] = _digest(sealed)
    return sealed


def _decode_registry(raw: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    previous_digest: str | None = None
    for line_number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            raise Phase5ActivationError(f"blank line in append-only registry at line {line_number}")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Phase5ActivationError(
                f"invalid registry JSON at line {line_number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise Phase5ActivationError(f"registry line {line_number} is not an object")
        supplied_digest = record.get("record_sha256")
        unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
        if supplied_digest != _digest(unsigned):
            raise Phase5ActivationError(f"registry hash-chain corruption at line {line_number}")
        if record.get("previous_record_sha256") != previous_digest:
            raise Phase5ActivationError(f"registry predecessor mismatch at line {line_number}")
        expected_type = "incumbent_baseline" if not records else None
        record_type = record.get("record_type")
        if expected_type and record_type != expected_type:
            raise Phase5ActivationError("registry must begin with exactly one incumbent baseline")
        if not expected_type and record_type not in REGISTRY_EVENT_TYPES:
            raise Phase5ActivationError(f"unexpected registry event at line {line_number}")
        records.append(record)
        previous_digest = supplied_digest
    if records and sum(record.get("record_type") == "incumbent_baseline" for record in records) != 1:
        raise Phase5ActivationError("append-only registry must contain one immutable incumbent baseline")
    return records


def _read_registry(root: Path) -> list[dict[str, Any]]:
    path = _registry_path(root)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return _decode_registry(raw)


def _append_event(root: Path, event: dict[str, Any]) -> dict[str, Any]:
    path = _registry_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        records = _decode_registry(handle.read())
        if not records and event.get("record_type") != "incumbent_baseline":
            raise Phase5ActivationError("initialize the incumbent baseline before appending events")
        if records and event.get("record_type") == "incumbent_baseline":
            raise Phase5ActivationError("incumbent baseline is immutable and may appear only once")
        sealed = _seal(event, records[-1]["record_sha256"] if records else None)
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(sealed, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        return sealed


def _baseline(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records or records[0].get("record_type") != "incumbent_baseline":
        raise Phase5ActivationError("Phase 5 activation is not initialized with an incumbent baseline")
    entry = records[0]
    model = entry.get("incumbent_model")
    cuts = entry.get("incumbent_cuts")
    if not isinstance(model, dict) or not isinstance(cuts, list) or not cuts:
        raise Phase5ActivationError("immutable incumbent model/cuts are missing")
    if _repo_model_key(model) != entry.get("incumbent_model_key"):
        raise Phase5ActivationError("immutable incumbent model key does not match its payload")
    if _digest(cuts) != entry.get("incumbent_cuts_sha256"):
        raise Phase5ActivationError("immutable incumbent cuts do not match their digest")
    if entry.get("record_sha256") != records[0].get("record_sha256"):
        raise Phase5ActivationError("incumbent baseline digest is invalid")
    return entry


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _initial_config(baseline: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    return {
        "schema": 1,
        "record_type": "phase5_active_era_config",
        "mode": "incumbent",
        "era_id": None,
        "active_model_key": baseline["incumbent_model_key"],
        "active_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "incumbent_model_key": baseline["incumbent_model_key"],
        "incumbent_entry_sha256": baseline["record_sha256"],
        "incumbent_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "candidate_model_key": None,
        "candidate_model_payload": None,
        "candidate_cuts": None,
        "candidate_cuts_sha256": None,
        "fallback_method": None,
        "fallback_means": None,
        "kill_switch": False,
        "created_at": _timestamp(now),
        "updated_at": _timestamp(now),
        "activation_record_sha256": None,
    }


def initialize_activation_state(
    root: Path | str,
    incumbent_registry_path: Path | str,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    root = Path(root)
    incumbent_path = Path(incumbent_registry_path)
    source, raw = _read_json(incumbent_path)
    model = source.get("ml_model")
    edges = source.get("edges")
    if not isinstance(model, dict) or not isinstance(edges, list):
        raise Phase5ActivationError("incumbent registry lacks ml_model or edges")
    cuts = [
        edge for edge in edges
        if isinstance(edge, dict) and str(edge.get("rule", "")).lower().startswith("ml-meta ")
    ]
    if not cuts or any(not isinstance(edge.get("rule"), str) for edge in cuts):
        raise Phase5ActivationError("incumbent registry has no complete ml-meta cut set")
    cut_names = [edge["rule"] for edge in cuts]
    if len(cut_names) != len(set(cut_names)):
        raise Phase5ActivationError("incumbent ml-meta cut names are not unique")

    proposed = {
        "schema": 1,
        "record_type": "incumbent_baseline",
        "created_at": _timestamp(now),
        "source_registry_name": incumbent_path.name,
        "source_registry_sha256": _sha256_bytes(raw),
        "incumbent_model_key": _repo_model_key(model),
        "incumbent_model": model,
        "incumbent_cuts": cuts,
        "incumbent_cuts_sha256": _digest(cuts),
        "incumbent_cut_names": cut_names,
        "immutable": True,
    }
    root.mkdir(parents=True, exist_ok=True)
    registry_path = _registry_path(root)
    if not registry_path.exists() or registry_path.stat().st_size == 0:
        if _active_path(root).exists():
            raise Phase5ActivationError("active config exists without its append-only registry")
        _append_event(root, proposed)
    records = _read_registry(root)
    baseline = _baseline(records)
    if (
        baseline.get("source_registry_sha256") != proposed["source_registry_sha256"]
        or baseline.get("incumbent_model_key") != proposed["incumbent_model_key"]
        or baseline.get("incumbent_cuts_sha256") != proposed["incumbent_cuts_sha256"]
    ):
        raise Phase5ActivationError(
            "current incumbent model/cuts differ from the immutable Phase 5 baseline"
        )

    active_path = _active_path(root)
    if active_path.exists():
        active, _ = _read_json(active_path)
        _assert_config_baseline(active, baseline)
        return active
    if len(records) != 1:
        raise Phase5ActivationError(
            "active config is missing after registry events; refusing to guess the active era"
        )
    active = _initial_config(baseline, now=now)
    _atomic_json(active_path, active)
    return active


def _assert_config_baseline(config: dict[str, Any], baseline: dict[str, Any]) -> None:
    if (
        config.get("record_type") != "phase5_active_era_config"
        or config.get("incumbent_entry_sha256") != baseline.get("record_sha256")
        or config.get("incumbent_model_key") != baseline.get("incumbent_model_key")
        or config.get("incumbent_cuts_sha256") != baseline.get("incumbent_cuts_sha256")
    ):
        raise Phase5ActivationError("active config does not reference the immutable incumbent baseline")


def _load_state(root: Path | str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    root = Path(root)
    records = _read_registry(root)
    baseline = _baseline(records)
    config, _ = _read_json(_active_path(root))
    _assert_config_baseline(config, baseline)
    return records, baseline, config


def _cut_snapshot(source: dict[str, Any]) -> list[dict[str, Any]]:
    edges = source.get("edges")
    if not isinstance(edges, list):
        raise Phase5ActivationError("incumbent registry lacks an edge list")
    cuts = [
        edge for edge in edges
        if isinstance(edge, dict) and str(edge.get("rule", "")).lower().startswith("ml-meta ")
    ]
    return cuts


def _assert_live_incumbent_unchanged(
    incumbent_registry_path: Path | str,
    baseline: dict[str, Any],
) -> None:
    source, _ = _read_json(Path(incumbent_registry_path))
    model = source.get("ml_model")
    if not isinstance(model, dict) or _repo_model_key(model) != baseline["incumbent_model_key"]:
        raise Phase5ActivationError("live incumbent model changed since Phase 5 baseline")
    cuts = _cut_snapshot(source)
    if _digest(cuts) != baseline["incumbent_cuts_sha256"]:
        raise Phase5ActivationError("live incumbent cuts changed since Phase 5 baseline")


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _load_passing_certificate(
    path: Path | str,
    *,
    era_id: str,
) -> tuple[dict[str, Any], bytes]:
    certificate_path = Path(path)
    try:
        raw = certificate_path.read_bytes()
    except FileNotFoundError as exc:
        raise Phase5NotYetDue(f"full passing certification artifact is not present: {certificate_path}") from exc
    try:
        certificate = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase5ActivationError(f"certification artifact is invalid JSON: {exc}") from exc
    if not isinstance(certificate, dict):
        raise Phase5ActivationError("certification artifact must be a JSON object")
    if certificate.get("record_type") != "phase5_certification_verdict":
        raise Phase5NotYetDue("no full Phase 5 certification verdict exists yet")
    overall = certificate.get("overall_status")
    if overall in {"blocked", "not_yet_due", "pending"}:
        raise Phase5NotYetDue(f"Phase 5 certification is {overall}; activation is not due")
    if overall != "pass":
        raise Phase5ActivationError("certification verdict is not a full pass")
    clauses = certificate.get("clauses")
    if not isinstance(clauses, dict) or set(clauses) != {str(i) for i in range(1, 10)}:
        raise Phase5ActivationError("full pass must report all nine frozen clauses")
    for clause, result in clauses.items():
        if not isinstance(result, dict) or result.get("status") not in PASS_STATUSES:
            raise Phase5ActivationError(f"clause {clause} did not pass")
    if certificate.get("era_id") != era_id:
        raise Phase5ActivationError("certificate era_id does not match the requested era")
    if certificate.get("candidate_fit_performed") is not True:
        raise Phase5ActivationError("certificate does not attest that the candidate fit was performed")

    model = certificate.get("candidate_model_payload")
    cuts = certificate.get("candidate_cuts")
    fallbacks = certificate.get("fallback_means")
    if not isinstance(model, dict) or not isinstance(cuts, list) or not cuts:
        raise Phase5ActivationError("passing certificate lacks candidate model or procedure cuts")
    if model.get("feature_cols") != list(K_FEATURES):
        raise Phase5ActivationError("candidate feature order differs from frozen 32-column K")
    coefficients = model.get("coef")
    if (
        not isinstance(coefficients, list) or len(coefficients) != len(K_FEATURES)
        or not all(_finite_number(value) for value in coefficients)
        or not _finite_number(model.get("intercept"))
    ):
        raise Phase5ActivationError("candidate coefficients/intercept are not a finite 32-column model")
    if certificate.get("fallback_method") != "era_train_slice_mean":
        raise Phase5ActivationError("candidate fallbacks are not certified era-train-slice means")
    if (
        not isinstance(fallbacks, dict)
        or set(fallbacks) != set(K_FEATURES)
        or not all(_finite_number(value) for value in fallbacks.values())
    ):
        raise Phase5ActivationError("certificate must include finite fallback means for all 32 columns")
    if not all(isinstance(cut, dict) and cut.get("rule") for cut in cuts):
        raise Phase5ActivationError("candidate cuts must be unchanged named procedure outputs")
    return certificate, raw


def _activated_era_records(records: list[dict[str, Any]]) -> set[str]:
    return {
        str(record.get("era_id"))
        for record in records
        if record.get("record_type") == "activation"
    }


def _last_activation(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next(
        (record for record in reversed(records) if record.get("record_type") == "activation"),
        None,
    )


def dry_run_revert(
    root: Path | str,
    certification_path: Path | str,
    *,
    era_id: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    records, baseline, config = _load_state(root)
    if config.get("mode") != "incumbent":
        raise Phase5ActivationError("pre-activation revert dry run requires incumbent mode")
    certificate, raw = _load_passing_certificate(certification_path, era_id=era_id)
    if era_id in _activated_era_records(records):
        raise Phase5ActivationError("this era already has an activation record")

    # Simulate the future candidate config, then prove the immediate kill and
    # one-command revert both resolve to the exact frozen incumbent payload/cuts.
    simulated = {
        "mode": "candidate", "era_id": era_id, "kill_switch": True,
        "incumbent_model_key": baseline["incumbent_model_key"],
        "incumbent_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "candidate_model_payload": certificate["candidate_model_payload"],
        "candidate_cuts": certificate["candidate_cuts"],
        "fallback_means": certificate["fallback_means"],
    }
    effective = _resolve_from_config(simulated, baseline, records)
    reverted_config = {
        **simulated,
        "mode": "incumbent",
        "era_id": None,
        "kill_switch": False,
    }
    after_revert = _resolve_from_config(reverted_config, baseline, records)
    if (
        effective["effective_model_key"] != baseline["incumbent_model_key"]
        or _digest(effective["cuts"]) != baseline["incumbent_cuts_sha256"]
        or effective["reason"] != "kill_switch"
        or after_revert["effective_model_key"] != baseline["incumbent_model_key"]
        or _digest(after_revert["cuts"]) != baseline["incumbent_cuts_sha256"]
        or after_revert["reason"] != "incumbent_config"
    ):
        raise Phase5ActivationError("revert dry run did not resolve exactly to incumbent")

    certificate_sha256 = _sha256_bytes(raw)
    event = _append_event(Path(root), {
        "schema": 1,
        "record_type": "revert_dry_run",
        "era_id": era_id,
        "certificate_sha256": certificate_sha256,
        "result": "pass",
        "incumbent_model_key": baseline["incumbent_model_key"],
        "incumbent_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "ran_at": _timestamp(now),
    })
    return {
        "status": "pass",
        "era_id": era_id,
        "certificate_sha256": certificate_sha256,
        "registry_record_sha256": event["record_sha256"],
        "effective_model_key_after_kill": effective["effective_model_key"],
        "effective_model_key_after_revert": after_revert["effective_model_key"],
    }


def activate_candidate(
    root: Path | str,
    certification_path: Path | str,
    incumbent_registry_path: Path | str,
    *,
    era_id: str,
    confirmed: bool,
    now: datetime | None = None,
) -> dict[str, Any]:
    if not confirmed:
        raise Phase5ActivationError("explicit activation confirmation is required")
    now_utc = _utc_now(now)
    records, baseline, config = _load_state(root)
    if config.get("mode") != "incumbent":
        raise Phase5ActivationError("a candidate is already configured; revert before another activation")
    if not isinstance(era_id, str) or not era_id.strip():
        raise Phase5ActivationError("era_id must be non-empty")
    if era_id in _activated_era_records(records):
        raise Phase5ActivationError("one activation per era is allowed")
    _assert_live_incumbent_unchanged(incumbent_registry_path, baseline)
    certificate, raw = _load_passing_certificate(certification_path, era_id=era_id)
    certificate_sha256 = _sha256_bytes(raw)

    dry_run = next((
        record for record in reversed(records)
        if record.get("record_type") == "revert_dry_run"
        and record.get("era_id") == era_id
        and record.get("certificate_sha256") == certificate_sha256
        and record.get("result") == "pass"
    ), None)
    if dry_run is None:
        raise Phase5ActivationError("run the one-command revert dry run for this exact verdict before activation")
    dry_run_at = _parse_timestamp(dry_run.get("ran_at"))
    if dry_run_at is None or now_utc < dry_run_at or now_utc - dry_run_at > REVERT_DRY_RUN_MAX_AGE:
        raise Phase5ActivationError("revert dry-run receipt is missing, future-dated, or older than 24 hours")

    previous_activation = _last_activation(records)
    if previous_activation is not None:
        previous_at = _parse_timestamp(previous_activation.get("activated_at"))
        if previous_at is None or now_utc < previous_at:
            raise Phase5ActivationError("activation clock is invalid or moved backwards")
        if now_utc - previous_at < COOLDOWN:
            raise Phase5ActivationError("30-day activation cooldown has not elapsed")

    model = certificate["candidate_model_payload"]
    candidate_key = _repo_model_key(model)
    if candidate_key == baseline["incumbent_model_key"]:
        raise Phase5ActivationError("candidate model_key equals incumbent; no activation is permitted")
    cuts = certificate["candidate_cuts"]
    fallbacks = certificate["fallback_means"]
    event = _append_event(Path(root), {
        "schema": 1,
        "record_type": "activation",
        "era_id": era_id,
        "certificate_sha256": certificate_sha256,
        "candidate_model_key": candidate_key,
        "candidate_cuts_sha256": _digest(cuts),
        "fallback_means_sha256": _digest(fallbacks),
        "incumbent_model_key": baseline["incumbent_model_key"],
        "incumbent_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "activated_at": _timestamp(now_utc),
    })
    active = {
        **config,
        "mode": "candidate",
        "era_id": era_id,
        "active_model_key": candidate_key,
        "active_cuts_sha256": _digest(cuts),
        "candidate_model_key": candidate_key,
        "candidate_model_payload": model,
        "candidate_cuts": cuts,
        "candidate_cuts_sha256": _digest(cuts),
        "fallback_method": certificate["fallback_method"],
        "fallback_means": fallbacks,
        "kill_switch": False,
        "kill_switch_set_at": None,
        "updated_at": _timestamp(now_utc),
        "activation_record_sha256": event["record_sha256"],
    }
    _atomic_json(_active_path(Path(root)), active)
    return {
        "status": "activated",
        "era_id": era_id,
        "candidate_model_key": candidate_key,
        "incumbent_model_key": baseline["incumbent_model_key"],
        "activation_record_sha256": event["record_sha256"],
    }


def set_kill_switch(
    root: Path | str,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    records, baseline, config = _load_state(root)
    if config.get("kill_switch") is True:
        return {
            "status": "already_set",
            "effective_model_key": baseline["incumbent_model_key"],
            "era_id": config.get("era_id"),
        }
    now_utc = _utc_now(now)
    updated = {
        **config,
        "kill_switch": True,
        "kill_switch_set_at": _timestamp(now_utc),
        "updated_at": _timestamp(now_utc),
    }
    # Write the fallback switch first. If recording the event fails, the
    # effective model is still the immutable incumbent immediately.
    _atomic_json(_active_path(Path(root)), updated)
    event = _append_event(Path(root), {
        "schema": 1,
        "record_type": "kill_switch",
        "era_id": config.get("era_id"),
        "candidate_model_key": config.get("candidate_model_key"),
        "incumbent_model_key": baseline["incumbent_model_key"],
        "activated_at": _timestamp(now_utc),
        "result": "fallback_to_incumbent",
    })
    return {
        "status": "kill_switch_set",
        "effective_model_key": baseline["incumbent_model_key"],
        "era_id": config.get("era_id"),
        "registry_record_sha256": event["record_sha256"],
    }


def revert_to_incumbent(
    root: Path | str,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    records, baseline, config = _load_state(root)
    if config.get("mode") == "incumbent" and config.get("kill_switch") is not True:
        return {"status": "already_incumbent", "effective_model_key": baseline["incumbent_model_key"]}
    now_utc = _utc_now(now)
    updated = {
        **config,
        "mode": "incumbent",
        "era_id": None,
        "active_model_key": baseline["incumbent_model_key"],
        "active_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "candidate_model_key": None,
        "candidate_model_payload": None,
        "candidate_cuts": None,
        "candidate_cuts_sha256": None,
        "fallback_method": None,
        "fallback_means": None,
        "kill_switch": False,
        "kill_switch_set_at": None,
        "updated_at": _timestamp(now_utc),
        "activation_record_sha256": None,
    }
    # Revert first, so a later append failure cannot leave the candidate active.
    _atomic_json(_active_path(Path(root)), updated)
    event = _append_event(Path(root), {
        "schema": 1,
        "record_type": "revert",
        "era_id": config.get("era_id"),
        "from_model_key": config.get("candidate_model_key"),
        "to_model_key": baseline["incumbent_model_key"],
        "incumbent_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "reverted_at": _timestamp(now_utc),
    })
    return {
        "status": "reverted",
        "effective_model_key": baseline["incumbent_model_key"],
        "registry_record_sha256": event["record_sha256"],
    }


def _resolve_from_config(
    config: dict[str, Any],
    baseline: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    incumbent = {
        "effective_mode": "incumbent",
        "effective_model_key": baseline["incumbent_model_key"],
        "model_payload": baseline["incumbent_model"],
        "cuts": baseline["incumbent_cuts"],
        "fallback_means": None,
    }
    if config.get("kill_switch") is True:
        return {**incumbent, "reason": "kill_switch"}
    if config.get("mode") == "incumbent":
        return {**incumbent, "reason": "incumbent_config"}
    if config.get("mode") != "candidate":
        return {**incumbent, "reason": "invalid_mode_fallback"}

    candidate = config.get("candidate_model_payload")
    cuts = config.get("candidate_cuts")
    fallbacks = config.get("fallback_means")
    try:
        candidate_key = _repo_model_key(candidate)
    except Phase5ActivationError:
        return {**incumbent, "reason": "invalid_candidate_model_fallback"}
    activation = next((
        record for record in records
        if record.get("record_sha256") == config.get("activation_record_sha256")
        and record.get("record_type") == "activation"
    ), None)
    valid = bool(
        candidate_key == config.get("candidate_model_key") == config.get("active_model_key")
        and isinstance(cuts, list) and _digest(cuts) == config.get("candidate_cuts_sha256")
        and _digest(cuts) == config.get("active_cuts_sha256")
        and _digest(cuts) == (activation or {}).get("candidate_cuts_sha256")
        and isinstance(fallbacks, dict) and set(fallbacks) == set(K_FEATURES)
        and config.get("fallback_method") == "era_train_slice_mean"
        and _digest(fallbacks) == (activation or {}).get("fallback_means_sha256")
        and (activation or {}).get("era_id") == config.get("era_id")
        and (activation or {}).get("candidate_model_key") == candidate_key
        and (activation or {}).get("incumbent_model_key") == baseline.get("incumbent_model_key")
        and (activation or {}).get("incumbent_cuts_sha256") == baseline.get("incumbent_cuts_sha256")
    )
    if not valid:
        return {**incumbent, "reason": "invalid_candidate_config_fallback"}
    return {
        "effective_mode": "candidate",
        "effective_model_key": candidate_key,
        "model_payload": candidate,
        "cuts": cuts,
        "fallback_means": fallbacks,
        "reason": "candidate_active",
    }


def resolve_effective_state(root: Path | str) -> dict[str, Any]:
    """Read state on every call; never cache the kill switch or candidate config."""
    records, baseline, config = _load_state(root)
    return _resolve_from_config(config, baseline, records)


def activation_status(root: Path | str) -> dict[str, Any]:
    records, baseline, config = _load_state(root)
    effective = _resolve_from_config(config, baseline, records)
    last = _last_activation(records)
    return {
        "mode": config.get("mode"),
        "era_id": config.get("era_id"),
        "kill_switch": config.get("kill_switch") is True,
        "configured_model_key": config.get("active_model_key"),
        "effective_model_key": effective["effective_model_key"],
        "effective_mode": effective["effective_mode"],
        "resolution_reason": effective["reason"],
        "incumbent_model_key": baseline["incumbent_model_key"],
        "incumbent_cuts_sha256": baseline["incumbent_cuts_sha256"],
        "registry_records": len(records),
        "last_activation_at": last.get("activated_at") if last else None,
    }
