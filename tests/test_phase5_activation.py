from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from edgefactory.phase5_activation import (
    K_FEATURES,
    Phase5ActivationError,
    Phase5NotYetDue,
    activate_candidate,
    activation_status,
    dry_run_revert,
    initialize_activation_state,
    resolve_effective_state,
    revert_to_incumbent,
    set_kill_switch,
)
from edgefactory.ml_fade_research import model_key


def _now(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _incumbent_registry(tmp_path: Path) -> Path:
    model = {
        "coef": [0.01] * 26,
        "intercept": -0.15,
        "feature_cols": [f"incumbent_{i}" for i in range(26)],
    }
    registry = {
        "split": "2025-06-01",
        "gates": {"min_n_train": 340, "min_n_valid": 120},
        "ml_model": model,
        "edges": [
            {"rule": f"ml-meta avg_p>={threshold}", "status": "certified"}
            for threshold in (55, 60, 65, 70, 75, 80, 85)
        ] + [{"rule": "unrelated incumbent edge", "status": "certified"}],
    }
    path = tmp_path / "edges_consensus.json"
    path.write_text(json.dumps(registry, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _candidate_certificate(path: Path, *, era_id: str, weight: float = 0.025) -> Path:
    model = {
        "coef": [weight + (i / 1000) for i in range(len(K_FEATURES))],
        "intercept": -0.05,
        "feature_cols": list(K_FEATURES),
    }
    certificate = {
        "schema": 1,
        "record_type": "phase5_certification_verdict",
        "overall_status": "pass",
        "era_id": era_id,
        "clauses": {
            str(i): {"status": "pass_with_source_exclusions" if i == 2 else "pass"}
            for i in range(1, 10)
        },
        "candidate_fit_performed": True,
        "candidate_model_payload": model,
        "candidate_cuts": [{"rule": f"procedure-cut-{era_id}", "status": "pass"}],
        "fallback_method": "era_train_slice_mean",
        "fallback_means": {feature: 0.37 + i / 1000 for i, feature in enumerate(K_FEATURES)},
    }
    path.write_text(json.dumps(certificate, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _initialize(tmp_path: Path, now: str = "2026-10-07T10:00:00Z"):
    incumbent_path = _incumbent_registry(tmp_path)
    state_root = tmp_path / "phase5_activation"
    config = initialize_activation_state(
        state_root, incumbent_path, now=_now(now)
    )
    return state_root, incumbent_path, config


def test_initial_state_freezes_incumbent_without_modifying_production_registry(tmp_path):
    incumbent_path = _incumbent_registry(tmp_path)
    before = incumbent_path.read_bytes()
    state_root = tmp_path / "phase5_activation"

    config = initialize_activation_state(
        state_root, incumbent_path, now=_now("2026-10-07T10:00:00Z")
    )
    events = [json.loads(line) for line in (state_root / "registry.jsonl").read_text().splitlines()]
    baseline = events[0]

    assert config["mode"] == "incumbent"
    assert config["era_id"] is None
    assert config["active_model_key"] == model_key(json.loads(before)["ml_model"])
    assert config["kill_switch"] is False
    assert len(events) == 1
    assert baseline["record_type"] == "incumbent_baseline"
    assert baseline["immutable"] is True
    assert len(baseline["incumbent_cuts"]) == 7
    assert incumbent_path.read_bytes() == before


def test_blocked_or_missing_verdict_is_not_yet_due_and_changes_no_activation_state(tmp_path):
    root, _, initial = _initialize(tmp_path)
    before_registry = (root / "registry.jsonl").read_bytes()
    before_active = (root / "active_era.json").read_bytes()
    blocked = tmp_path / "blocked.json"
    blocked.write_text(json.dumps({
        "record_type": "phase5_full_evaluation_preflight",
        "status": "blocked",
    }))

    with pytest.raises(Phase5NotYetDue):
        dry_run_revert(root, blocked, era_id="era-1")
    with pytest.raises(Phase5NotYetDue):
        activate_candidate(
            root, blocked, tmp_path / "edges_consensus.json",
            era_id="era-1", confirmed=True,
        )
    assert (root / "registry.jsonl").read_bytes() == before_registry
    assert (root / "active_era.json").read_bytes() == before_active
    assert activation_status(root)["effective_model_key"] == initial["active_model_key"]


def test_revert_dry_run_activation_kill_switch_and_revert_use_exact_incumbent_fallback(tmp_path):
    root, incumbent_path, initial = _initialize(tmp_path)
    certificate = _candidate_certificate(tmp_path / "cert.json", era_id="era-2026-10")
    now = _now("2026-10-08T10:00:00Z")

    dry = dry_run_revert(
        root, certificate, era_id="era-2026-10", now=now
    )
    assert dry["status"] == "pass"
    assert dry["effective_model_key_after_kill"] == initial["active_model_key"]
    assert dry["effective_model_key_after_revert"] == initial["active_model_key"]
    activated = activate_candidate(
        root, certificate, incumbent_path, era_id="era-2026-10",
        confirmed=True, now=_now("2026-10-08T11:00:00Z"),
    )
    assert activated["candidate_model_key"] == model_key(
        json.loads(certificate.read_text())["candidate_model_payload"]
    )
    candidate_one = resolve_effective_state(root)
    candidate_two = resolve_effective_state(root)
    assert candidate_one == candidate_two
    assert candidate_one["effective_mode"] == "candidate"
    assert candidate_one["effective_model_key"] == activated["candidate_model_key"]
    assert candidate_one["fallback_means"] == json.loads(certificate.read_text())["fallback_means"]

    killed = set_kill_switch(root, now=_now("2026-10-08T12:00:00Z"))
    assert killed["effective_model_key"] == initial["active_model_key"]
    effective_after_kill = resolve_effective_state(root)
    assert effective_after_kill["effective_mode"] == "incumbent"
    assert effective_after_kill["reason"] == "kill_switch"
    assert effective_after_kill["model_payload"] == json.loads(incumbent_path.read_text())["ml_model"]
    assert effective_after_kill["cuts"] == json.loads((root / "registry.jsonl").read_text().splitlines()[0])["incumbent_cuts"]

    reverted = revert_to_incumbent(root, now=_now("2026-10-08T13:00:00Z"))
    assert reverted["status"] == "reverted"
    assert resolve_effective_state(root)["effective_model_key"] == initial["active_model_key"]
    with pytest.raises(Phase5ActivationError, match="one activation per era"):
        activate_candidate(
            root, certificate, incumbent_path, era_id="era-2026-10",
            confirmed=True, now=_now("2026-10-08T14:00:00Z"),
        )


def test_30_day_cooldown_is_enforced_but_expires_at_30_days(tmp_path):
    root, incumbent_path, _ = _initialize(tmp_path)
    cert_one = _candidate_certificate(tmp_path / "one.json", era_id="era-one", weight=0.02)
    dry_run_revert(root, cert_one, era_id="era-one", now=_now("2026-10-10T10:00:00Z"))
    activate_candidate(
        root, cert_one, incumbent_path, era_id="era-one", confirmed=True,
        now=_now("2026-10-10T11:00:00Z"),
    )
    revert_to_incumbent(root, now=_now("2026-10-10T12:00:00Z"))

    cert_two = _candidate_certificate(tmp_path / "two.json", era_id="era-two", weight=0.03)
    dry_run_revert(root, cert_two, era_id="era-two", now=_now("2026-10-20T10:00:00Z"))
    with pytest.raises(Phase5ActivationError, match="30-day activation cooldown"):
        activate_candidate(
            root, cert_two, incumbent_path, era_id="era-two", confirmed=True,
            now=_now("2026-10-20T11:00:00Z"),
        )

    cert_three = _candidate_certificate(tmp_path / "three.json", era_id="era-three", weight=0.04)
    dry_run_revert(root, cert_three, era_id="era-three", now=_now("2026-11-09T10:00:00Z"))
    accepted = activate_candidate(
        root, cert_three, incumbent_path, era_id="era-three", confirmed=True,
        now=_now("2026-11-09T11:00:00Z"),
    )
    assert accepted["status"] == "activated"


def test_registry_tamper_and_active_baseline_mutation_fail_closed(tmp_path):
    root, incumbent_path, _ = _initialize(tmp_path)
    config_path = root / "active_era.json"
    config = json.loads(config_path.read_text())
    config["incumbent_cuts_sha256"] = "0" * 64
    config_path.write_text(json.dumps(config))
    with pytest.raises(Phase5ActivationError, match="immutable incumbent baseline"):
        resolve_effective_state(root)

    # Mutate the immutable genesis row without resealing it in an independent state root.
    other = tmp_path / "other"
    other.mkdir()
    other_registry = _incumbent_registry(other)
    other_state = other / "phase5_activation"
    initialize_activation_state(other_state, other_registry)
    registry_path = other_state / "registry.jsonl"
    baseline = json.loads(registry_path.read_text().splitlines()[0])
    baseline["incumbent_cuts"][0]["rule"] = "mutated cut"
    registry_path.write_text(json.dumps(baseline) + "\n")
    with pytest.raises(Phase5ActivationError, match="hash-chain corruption"):
        resolve_effective_state(other_state)
