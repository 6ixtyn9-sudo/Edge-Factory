"""Promotion bridge: an activated era reaches the served registry, verifiably.

The guard's job is to stop the MINER from replacing the live model. An era
activated through the Phase 5 gate is a deliberate, audited replacement, and
these tests pin the difference:

* promotion refuses while no era is activated, and while the kill switch is on;
* the promoted registry is verified by the guard BEFORE it is written, so the
  active config and the live registry cannot disagree;
* the frozen incumbent remains immutable history, and once the kill switch is
  engaged the guard expects the incumbent again — restore puts it back.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from edgefactory.ml_fade_research import model_key
from edgefactory.phase5_activation import (
    K_FEATURES,
    activate_candidate,
    dry_run_revert,
    initialize_activation_state,
    revert_to_incumbent,
    set_kill_switch,
)
from edgefactory.phase5_k import feature_vector
from edgefactory.phase5_promotion import (
    Phase5PromotionError,
    build_promoted_registry,
    promote_activated_candidate,
    restore_incumbent,
)
from edgefactory.phase5_registry_guard import inspect_operational_registry


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
            {"rule": f"ml-meta avg_p>={threshold}", "status": "certified",
             "market": "1x2"}
            for threshold in (55, 60, 65, 80)
        ] + [
            {"rule": "ml-fade avg_p>=55", "status": "certified", "market": "1x2"},
            {"rule": "2way-unanimous avg_p>=70", "status": "certified",
             "market": "1x2"},
        ],
    }
    path = tmp_path / "edges_consensus.json"
    path.write_text(json.dumps(registry, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _candidate_certificate(path: Path, *, era_id: str) -> Path:
    model = {
        "coef": [0.02 + (i / 1000) for i in range(len(K_FEATURES))],
        "intercept": -0.11,
        "feature_cols": list(K_FEATURES),
    }
    certificate = {
        "schema": 1,
        "record_type": "phase5_certification_verdict",
        "overall_status": "pass",
        "era_id": era_id,
        "clauses": {str(i): {"status": "pass"} for i in range(1, 10)},
        "candidate_fit_performed": True,
        "candidate_model_payload": model,
        "candidate_cuts": [
            {"rule": "ml-meta avg_p>=55", "status": "certified", "market": "1x2"},
            {"rule": "ml-meta avg_p>=60", "status": "certified", "market": "1x2"},
        ],
        "fallback_method": "era_train_slice_mean",
        "fallback_means": {feature: 0.33 + i / 100 for i, feature in enumerate(K_FEATURES)},
    }
    path.write_text(json.dumps(certificate, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _activated(tmp_path: Path, era_id: str = "era-2026q4"):
    registry_path = _incumbent_registry(tmp_path)
    state_root = tmp_path / "phase5_activation"
    initialize_activation_state(state_root, registry_path, now=_now("2026-10-07T10:00:00Z"))
    certificate = _candidate_certificate(tmp_path / "certification.json", era_id=era_id)
    dry_run_revert(state_root, certificate, era_id=era_id,
                   now=_now("2026-10-08T09:00:00Z"))
    activate_candidate(state_root, certificate, registry_path, era_id=era_id,
                       confirmed=True, now=_now("2026-10-08T10:00:00Z"))
    return state_root, registry_path


def test_promotion_is_refused_while_the_incumbent_is_dormant(tmp_path):
    registry_path = _incumbent_registry(tmp_path)
    state_root = tmp_path / "phase5_activation"
    initialize_activation_state(state_root, registry_path, now=_now("2026-10-07T10:00:00Z"))
    with pytest.raises(Phase5PromotionError, match="no activated era"):
        build_promoted_registry(state_root, registry_path)
    # the incumbent registry is untouched by a refused promotion
    assert model_key(json.loads(registry_path.read_text())["ml_model"]) == model_key(
        {"coef": [0.01] * 26, "intercept": -0.15,
         "feature_cols": [f"incumbent_{i}" for i in range(26)]}
    )


def test_promotion_writes_a_guard_verified_registry(tmp_path):
    state_root, registry_path = _activated(tmp_path)
    report = promote_activated_candidate(state_root, registry_path, era_id="era-2026q4",
                                         write=True, now=_now("2026-10-08T11:00:00Z"))
    assert report["written"] is True
    assert report["guard"]["ok"] is True
    assert report["guard"]["reason"] == "activated era era-2026q4 model/cuts verified"

    promoted = json.loads(registry_path.read_text())
    certificate = json.loads((tmp_path / "certification.json").read_text())
    assert promoted["ml_model"] == certificate["candidate_model_payload"]
    assert promoted["fallback_means"] == certificate["fallback_means"]
    assert promoted["fallback_method"] == "era_train_slice_mean"
    # cuts: the era's set is live, the incumbent's extra cuts are gone
    live_rules = {e["rule"] for e in promoted["edges"] if e["rule"].startswith("ml-meta")}
    assert live_rules == {"ml-meta avg_p>=55", "ml-meta avg_p>=60"}
    # the fade family is benched (derived from the incumbent's selection)
    fade = [e for e in promoted["edges"] if e["rule"].startswith("ml-fade")]
    assert fade and all(e["status"] == "benched" for e in fade)
    # non-ML surface survives
    assert any(e["rule"] == "2way-unanimous avg_p>=70" for e in promoted["edges"])
    # a backup of the previous registry was kept
    assert report["write"]["backup"] is not None
    assert Path(report["write"]["backup"]).exists()

    # the served loop can now score the promoted model with its own means
    vector, imputed = feature_vector(
        {"fb_p": 0.6}, {"feature_cols": promoted["ml_model"]["feature_cols"],
                        "fallback_means": promoted["fallback_means"]}
    )
    assert len(vector) == len(K_FEATURES)
    assert len(imputed) == len(K_FEATURES) - 1


def test_guard_still_rejects_the_miner_after_promotion(tmp_path):
    state_root, registry_path = _activated(tmp_path)
    promote_activated_candidate(state_root, registry_path, era_id="era-2026q4",
                                write=True, now=_now("2026-10-08T11:00:00Z"))
    # a legacy miner write that carries the OLD model forward must be rejected
    stale = json.loads(registry_path.read_text())
    stale["ml_model"] = {"coef": [0.01] * 26, "intercept": -0.15,
                         "feature_cols": [f"incumbent_{i}" for i in range(26)]}
    assert inspect_operational_registry(stale, state_root)["ok"] is False


def test_kill_switch_returns_the_expectation_to_the_incumbent(tmp_path):
    state_root, registry_path = _activated(tmp_path)
    promote_activated_candidate(state_root, registry_path, era_id="era-2026q4",
                                write=True, now=_now("2026-10-08T11:00:00Z"))
    set_kill_switch(state_root)
    # with the switch engaged the guard expects the incumbent again, so the
    # promoted registry fails closed and restore is the way back
    promoted = json.loads(registry_path.read_text())
    assert inspect_operational_registry(promoted, state_root)["ok"] is False
    report = restore_incumbent(state_root, registry_path, write=True,
                              now=_now("2026-10-08T12:00:00Z"))
    assert report["written"] is True
    assert report["guard"]["ok"] is True
    restored = json.loads(registry_path.read_text())
    assert "fallback_means" not in restored
    assert {e["rule"] for e in restored["edges"] if e["rule"].startswith("ml-meta")} == {
        "ml-meta avg_p>=55", "ml-meta avg_p>=60", "ml-meta avg_p>=65",
        "ml-meta avg_p>=80",
    }


def test_promotion_refuses_a_mismatched_era_id(tmp_path):
    state_root, registry_path = _activated(tmp_path)
    with pytest.raises(Phase5PromotionError, match="not the active era"):
        build_promoted_registry(state_root, registry_path, era_id="some-other-era")


def test_revert_does_not_require_a_registry_write(tmp_path):
    """Reverting the era config alone is enough for the guard to want the
    incumbent back; restore is then a verification, not a blind write."""
    state_root, registry_path = _activated(tmp_path)
    revert_to_incumbent(state_root)
    report = restore_incumbent(state_root, registry_path, write=False)
    assert report["guard"]["ok"] is True
    # dry run must not have touched the file
    assert json.loads(registry_path.read_text())["ml_model"]["feature_cols"][0] == "incumbent_0"
