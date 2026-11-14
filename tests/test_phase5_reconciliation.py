from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

from edgefactory.ml_fade_research import model_key
from edgefactory.phase5_activation import initialize_activation_state
from edgefactory.phase5_reconciliation import (
    EXPECTED_INCUMBENT_MODEL_KEY,
    Phase5ReconciliationError,
    apply_reconciliation,
    build_reconciliation_plan,
    verify_designated_baseline,
)
from edgefactory.phase5_registry_guard import inspect_operational_registry

ROOT = Path(__file__).resolve().parents[1]


def _model(offset: float = 0.0) -> dict:
    return {"coef": [0.3 + offset, -0.1], "intercept": -0.7, "feature_cols": ["fb_p", "zb_p"]}


def _edge(rule: str, *, status: str = "certified") -> dict:
    return {
        "rule": rule,
        "status": status,
        "market": "1x2",
        "view": "ml_meta_settled",
        "where": "ml_p*100 >= 55",
        "train": {"n": 500, "wins": 350, "roi": 0.2},
        "valid": {"n": 180, "wins": 132, "roi": 0.18},
        "decay": {"verdict": "HEALTHY", "recent": {"n": 32}},
    }


def _fixture(tmp_path: Path) -> tuple[dict, Path]:
    source = tmp_path / "baseline_source.json"
    source.write_text(json.dumps({
        "ml_model": _model(),
        "edges": [
            _edge("ml-meta avg_p>=55"),
            _edge("ml-meta avg_p>=60"),
            _edge("ml-meta avg_p>=65", status="benched"),
            _edge("ml-meta avg_p>=70", status="candidate"),
            {"rule": "2way avg_p>=60", "status": "certified", "train": {"n": 200}},
        ],
    }), encoding="utf-8")
    activation = tmp_path / "phase5_activation"
    initialize_activation_state(activation, source)
    baseline = json.loads((activation / "registry.jsonl").read_text().splitlines()[0])
    return baseline, activation


def _load_script(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_tracked_frozen_baseline_independently_hashes_to_designated_incumbent():
    baseline, config, checks = verify_designated_baseline(
        ROOT / "localdata" / "phase5_activation"
    )
    assert checks["designated_key"] == EXPECTED_INCUMBENT_MODEL_KEY
    assert checks["stored_key"] == checks["repository_model_key"]
    assert checks["independent_model_key"] == checks["stored_key"]
    assert baseline["immutable"] is True
    assert config["mode"] == "incumbent" and config["kill_switch"] is False


def test_untrusted_or_changed_baseline_is_rejected_before_any_registry_write(tmp_path):
    baseline, activation = _fixture(tmp_path)
    current = {
        "ml_model": _model(offset=0.2),
        "edges": copy.deepcopy(baseline["incumbent_cuts"]) + [
            {"rule": "2way avg_p>=60", "status": "certified"}
        ],
    }
    registry = tmp_path / "edges_consensus.json"
    original = json.dumps(current).encode()
    registry.write_bytes(original)
    with pytest.raises(Phase5ReconciliationError, match="designated incumbent"):
        apply_reconciliation(registry, activation, tmp_path / "audit", audit_id="reject")
    assert registry.read_bytes() == original
    assert not (tmp_path / "audit").exists()

    # Corrupting the frozen chain/config also fails closed with the real key.
    real_activation = tmp_path / "bad_real_activation"
    real_activation.mkdir()
    source_activation = ROOT / "localdata" / "phase5_activation"
    for name in ("active_era.json", "registry.jsonl"):
        shutil.copy2(source_activation / name, real_activation / name)
    registry_lines = (real_activation / "registry.jsonl").read_text().splitlines()
    record = json.loads(registry_lines[0])
    record["incumbent_model"]["coef"][0] += 0.01
    registry_lines[0] = json.dumps(record, sort_keys=True, separators=(",", ":"))
    (real_activation / "registry.jsonl").write_text("\n".join(registry_lines) + "\n")
    with pytest.raises(Phase5ReconciliationError):
        verify_designated_baseline(real_activation)


def test_plan_restores_only_model_and_frozen_cut_definitions_without_promotions(tmp_path):
    baseline, _activation = _fixture(tmp_path)
    baseline_edges = {edge["rule"]: edge for edge in baseline["incumbent_cuts"]}
    current_edges = []
    for rule, baseline_edge in baseline_edges.items():
        if rule == "ml-meta avg_p>=65":
            continue  # missing protected cut must return non-emitting
        edge = copy.deepcopy(baseline_edge)
        edge["train"] = {"n": 999, "wins": 990, "roi": 9.9}
        edge["status"] = "certified" if baseline_edge["status"] == "benched" else baseline_edge["status"]
        if rule == "ml-meta avg_p>=55":
            edge["status"] = "benched"
            edge["benched_at"] = "2026-10-08"
            edge["decay"] = {"verdict": "DECAYING", "recent": {"n": 32}}
        elif rule == "ml-meta avg_p>=60":
            edge["status"] = "candidate"
        current_edges.append(edge)
    current_edges.extend([
        _edge("ml-meta avg_p>=90"),  # unexpected rule is removed and kept in audit
        {"rule": "ml-fade avg_p>=55", "status": "candidate", "where": "unchanged"},
        {"rule": "2way avg_p>=60", "status": "certified", "train": {"n": 777}},
    ])
    live_model = _model(offset=0.15)
    registry = {"ml_model": live_model, "edges": current_edges, "other": {"keep": True}}

    planned, report = build_reconciliation_plan(registry, baseline)
    protected = {edge["rule"]: edge for edge in planned["edges"]
                 if isinstance(edge, dict) and str(edge.get("rule", "")).startswith("ml-meta ")}
    assert model_key(planned["ml_model"]) == baseline["incumbent_model_key"]
    assert planned["other"] == registry["other"]
    assert [e for e in planned["edges"] if e.get("rule") == "2way avg_p>=60"] == [
        e for e in registry["edges"] if e.get("rule") == "2way avg_p>=60"
    ]
    assert next(e for e in planned["edges"] if e.get("rule") == "ml-fade avg_p>=55") == next(
        e for e in registry["edges"] if e.get("rule") == "ml-fade avg_p>=55"
    )
    assert "ml-meta avg_p>=90" not in protected
    assert protected["ml-meta avg_p>=55"]["status"] == "benched"
    assert protected["ml-meta avg_p>=55"]["decay"]["verdict"] == "DECAYING"
    assert protected["ml-meta avg_p>=55"]["train"] == baseline_edges["ml-meta avg_p>=55"]["train"]
    assert protected["ml-meta avg_p>=60"]["status"] == "candidate"
    assert protected["ml-meta avg_p>=65"]["status"] == "benched"
    assert protected["ml-meta avg_p>=70"]["status"] == "candidate"
    assert report["model_differences"]
    assert report["extra_ml_meta_rules_removed"] == ["ml-meta avg_p>=90"]
    assert report["missing_ml_meta_rules_added_benched_or_baseline_status"] == ["ml-meta avg_p>=65"]
    assert inspect_operational_registry(planned, tmp_path / "phase5_activation")["ok"] is True


def test_applied_reconciliation_preserves_before_image_and_historical_model_eras(tmp_path):
    baseline, activation = _fixture(tmp_path)
    registry = tmp_path / "edges_consensus.json"
    live_model = _model(offset=0.22)
    live_edges = copy.deepcopy(baseline["incumbent_cuts"])
    for edge in live_edges:
        edge["train"] = {"n": 888, "wins": 800, "roi": 0.7}
    live_edges.append({"rule": "2way avg_p>=60", "status": "certified", "train": {"n": 400}})
    original = {"ml_model": live_model, "edges": live_edges, "gates": {"keep": True}}
    original_bytes = (json.dumps(original, indent=2) + "\n").encode()
    registry.write_bytes(original_bytes)

    historical = tmp_path / "ml_fade_research_ledger.json"
    historical.write_text(json.dumps({"rows": [
        {"model_key": model_key(live_model)},
        {"model_key": baseline["incumbent_model_key"]},
    ]}), encoding="utf-8")
    import hashlib
    historical_before = historical.read_bytes()
    historical_hash = hashlib.sha256(historical_before).hexdigest()

    result = apply_reconciliation(
        registry, activation, tmp_path / "audit", expected_model_key=model_key(baseline["incumbent_model"]),
        audit_id="restoration-test",
    )
    after_bytes = registry.read_bytes()
    after = json.loads(after_bytes.decode("utf-8"))
    assert after_bytes == (json.dumps(after, indent=2, sort_keys=False) + "\n").encode("utf-8")
    audit_dir = Path(result["audit_dir"])
    receipt = json.loads((audit_dir / "reconciliation_receipt.json").read_text(encoding="utf-8"))
    assert (audit_dir / "displaced_edges_consensus.json").read_bytes() == original_bytes
    assert receipt["displaced_registry"]["ml_model_key"] == model_key(live_model)
    assert receipt["planned_registry"]["ml_model_key"] == baseline["incumbent_model_key"]
    assert receipt["historical_model_era_inventory_unchanged_by_this_operation"][historical.name]["rows_by_model_key"] == {
        baseline["incumbent_model_key"]: 1,
        model_key(live_model): 1,
    }
    assert historical.read_bytes() == historical_before
    assert hashlib.sha256(historical.read_bytes()).hexdigest() == historical_hash
    assert after["gates"] == original["gates"]
    assert next(e for e in after["edges"] if e["rule"] == "2way avg_p>=60") == next(
        e for e in original["edges"] if e["rule"] == "2way avg_p>=60"
    )
    assert inspect_operational_registry(after, activation)["ok"] is True


def test_legacy_mining_cannot_install_a_displaced_candidate_as_live_model(tmp_path, monkeypatch):
    baseline, _config, _checks = verify_designated_baseline(
        ROOT / "localdata" / "phase5_activation"
    )
    activation = ROOT / "localdata" / "phase5_activation"
    displaced_model = _model(offset=0.9)
    displaced_key = model_key(displaced_model)
    assert displaced_key != baseline["incumbent_model_key"]

    current = json.loads((ROOT / "localdata" / "edges_consensus.json").read_text(encoding="utf-8"))
    registry_path = tmp_path / "edges_consensus.json"
    research_path = tmp_path / "edges_consensus_research.json"
    registry_path.write_text(json.dumps(current), encoding="utf-8")
    miner = _load_script("phase5_reconciliation_miner", "scripts/mine_consensus.py")
    monkeypatch.setattr(miner, "OUT", registry_path)
    monkeypatch.setattr(miner, "RESEARCH_OUT", research_path)
    monkeypatch.setattr(miner, "ACTIVATION_ROOT", activation)
    candidate = copy.deepcopy(current)
    candidate["ml_model"] = copy.deepcopy(displaced_model)
    candidate["edges"].append({"rule": "2way avg_p>=65", "status": "certified", "train": {"n": 300}})

    assert miner.write_registry(candidate) is True
    after = json.loads(registry_path.read_text(encoding="utf-8"))
    assert model_key(after["ml_model"]) == baseline["incumbent_model_key"]
    assert model_key(json.loads(research_path.read_text(encoding="utf-8"))["ml_model"]) == displaced_key
    assert inspect_operational_registry(after, activation)["ok"] is True


def test_baseline_verification_rejects_mismatched_model_after_live_registry_is_reconciled():
    # Existing C1 loader coverage is complemented by an explicit read-path
    # assertion: a future legacy replacement still fails closed after restore.
    from edgefactory.phase5_registry_guard import inspect_operational_registry

    baseline, _config, _checks = verify_designated_baseline(ROOT / "localdata" / "phase5_activation")
    mismatched = {"ml_model": _model(offset=0.5), "edges": copy.deepcopy(baseline["incumbent_cuts"])}
    assert inspect_operational_registry(mismatched, ROOT / "localdata" / "phase5_activation")["ok"] is False
