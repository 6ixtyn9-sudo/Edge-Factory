from __future__ import annotations

import copy
import gzip
import importlib.util
import json
import sys
from pathlib import Path

import duckdb
import pytest

from edgefactory.phase5_activation import initialize_activation_state
from edgefactory.phase5_registry_guard import (
    inspect_operational_registry,
    preserve_live_ml_payload,
)

ROOT = Path(__file__).resolve().parent.parent


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _model(offset: float = 0.0) -> dict:
    return {
        "coef": [0.25 + offset, -0.10],
        "intercept": -0.4,
        "feature_cols": ["fb_p", "zb_p"],
    }


def _edge(rule: str, *, status: str = "certified", n: int = 420) -> dict:
    return {
        "rule": rule,
        "status": status,
        "market": "1x2",
        "sport": "soccer",
        "view": "ml_meta_settled" if rule.startswith("ml-meta") else "v_consensus2",
        "where": "ml_p*100 >= 55" if rule == "ml-meta avg_p>=55" else "avg_p >= 60",
        "train": {"n": n, "wins": int(n * 0.7), "roi": 0.1},
        "valid": {"n": 150, "wins": 108, "roi": 0.08},
        "decay": {"verdict": "HEALTHY", "recent": {"n": 40}},
    }


def _fixture(tmp_path: Path) -> tuple[dict, Path]:
    source = tmp_path / "baseline_source.json"
    baseline = {
        "split": "2025-06-01",
        "gates": {"min_n_train": 340},
        "ml_model": _model(),
        "edges": [
            _edge("ml-meta avg_p>=55"),
            _edge("ml-meta avg_p>=60", status="benched"),
            _edge("ml-meta avg_p>=65", status="candidate"),
            _edge("ml-fade avg_p>=55", status="candidate"),
            {"rule": "2way avg_p>=60", "status": "certified", "train": {"n": 200}},
        ],
    }
    source.write_text(json.dumps(baseline), encoding="utf-8")
    activation_root = tmp_path / "phase5_activation"
    initialize_activation_state(activation_root, source)
    # The live registry is exactly the protected baseline at fixture creation.
    return baseline, activation_root


def _wire_miner(monkeypatch, tmp_path: Path, activation_root: Path):
    miner = _load_script("phase5_test_mine_consensus", "scripts/mine_consensus.py")
    out = tmp_path / "edges_consensus.json"
    research = tmp_path / "edges_consensus_research.json"
    return miner, out, research


def _candidate_from(baseline: dict, *, non_ml_n: int = 240) -> dict:
    changed_model = _model(offset=0.12)
    edges = []
    for old in baseline["edges"]:
        edge = copy.deepcopy(old)
        if edge["rule"].startswith("ml-meta"):
            edge["where"] = "ml_p*100 >= 50"
            edge["status"] = "certified"
            edge["train"] = {"n": 999, "wins": 950, "roi": 0.9}
        elif edge["rule"].startswith("ml-fade"):
            edge["status"] = "certified"
        else:
            edge["train"] = {"n": non_ml_n}
        edges.append(edge)
    return {
        "split": "2025-06-01",
        "gates": {"min_n_train": 340},
        "ml_model": changed_model,
        "edges": edges,
    }


def test_operational_writer_keeps_legacy_fit_research_only_and_updates_non_ml(
    tmp_path, monkeypatch
):
    baseline, activation_root = _fixture(tmp_path)
    miner, out, research = _wire_miner(monkeypatch, tmp_path, activation_root)
    monkeypatch.setattr(miner, "OUT", out)
    monkeypatch.setattr(miner, "RESEARCH_OUT", research)
    monkeypatch.setattr(miner, "ACTIVATION_ROOT", activation_root)
    out.write_text(json.dumps(baseline), encoding="utf-8")

    candidate = _candidate_from(baseline)
    assert miner.write_registry(candidate) is True
    operational = json.loads(out.read_text(encoding="utf-8"))
    research_only = json.loads(research.read_text(encoding="utf-8"))

    assert operational["ml_model"] == baseline["ml_model"]
    assert research_only["ml_model"] == candidate["ml_model"]
    live = {edge["rule"]: edge for edge in operational["edges"]}
    candidate_edges = {edge["rule"]: edge for edge in candidate["edges"]}
    # Both incumbent ML families, definitions, statuses and historical benches
    # are carried forward; a legacy status promotion or cut rewrite is ignored.
    for edge in baseline["edges"]:
        if edge["rule"].startswith(("ml-meta", "ml-fade")):
            assert live[edge["rule"]] == edge
    assert live["2way avg_p>=60"]["train"] == candidate_edges["2way avg_p>=60"]["train"]
    assert inspect_operational_registry(operational, activation_root)["ok"] is True


def test_missing_live_registry_is_not_reconstructed_from_candidate_or_baseline(
    tmp_path, monkeypatch
):
    baseline, activation_root = _fixture(tmp_path)
    miner, out, research = _wire_miner(monkeypatch, tmp_path, activation_root)
    monkeypatch.setattr(miner, "OUT", out)
    monkeypatch.setattr(miner, "RESEARCH_OUT", research)
    monkeypatch.setattr(miner, "ACTIVATION_ROOT", activation_root)

    candidate = _candidate_from(baseline)
    assert miner.write_registry(candidate) is False
    assert not out.exists()
    assert json.loads(research.read_text(encoding="utf-8"))["ml_model"] == candidate["ml_model"]


def test_benched_incumbent_stays_benched_across_next_legacy_mining_run(
    tmp_path, monkeypatch
):
    baseline, activation_root = _fixture(tmp_path)
    miner, out, research = _wire_miner(monkeypatch, tmp_path, activation_root)
    monkeypatch.setattr(miner, "OUT", out)
    monkeypatch.setattr(miner, "RESEARCH_OUT", research)
    monkeypatch.setattr(miner, "ACTIVATION_ROOT", activation_root)
    current = copy.deepcopy(baseline)
    protected = next(e for e in current["edges"] if e["rule"] == "ml-meta avg_p>=55")
    protected["status"] = "benched"  # risk-reducing decay monitor transition
    protected["benched_at"] = "2026-10-08"
    protected["decay"] = {"verdict": "DECAYING", "checked_at": "2026-10-08"}
    out.write_text(json.dumps(current), encoding="utf-8")

    attempted = _candidate_from(baseline)
    assert miner.write_registry(attempted) is True
    after = json.loads(out.read_text(encoding="utf-8"))
    live = next(e for e in after["edges"] if e["rule"] == "ml-meta avg_p>=55")
    assert live["status"] == "benched"
    assert live["benched_at"] == "2026-10-08"
    assert live["decay"]["verdict"] == "DECAYING"
    rules, model = inspect_operational_registry(after, activation_root)["ok"], after["ml_model"]
    assert rules is True and model == baseline["ml_model"]


def test_baseline_mismatch_preserved_and_blocks_ml_but_not_non_ml_pick_path(
    tmp_path, monkeypatch, capsys
):
    baseline, activation_root = _fixture(tmp_path)
    miner, out, research = _wire_miner(monkeypatch, tmp_path, activation_root)
    monkeypatch.setattr(miner, "OUT", out)
    monkeypatch.setattr(miner, "RESEARCH_OUT", research)
    monkeypatch.setattr(miner, "ACTIVATION_ROOT", activation_root)
    mismatched = copy.deepcopy(baseline)
    mismatched["ml_model"] = _model(offset=0.2)
    # Keep the cuts as they were at the persisted run; the model itself proves
    # the mismatch. No production code may overwrite it with the frozen copy.
    out.write_text(json.dumps(mismatched), encoding="utf-8")
    attempted = _candidate_from(baseline, non_ml_n=333)

    assert miner.write_registry(attempted) is True
    after = json.loads(out.read_text(encoding="utf-8"))
    assert after["ml_model"] == mismatched["ml_model"]
    assert inspect_operational_registry(after, activation_root)["ok"] is False
    assert next(e for e in after["edges"] if e["rule"] == "2way avg_p>=60")["train"]["n"] == 333
    assert "BASELINE MISMATCH" in capsys.readouterr().out

    picks = _load_script("phase5_test_picks_today", "scripts/picks_today.py")
    monkeypatch.setattr(picks, "EDGES_PATH", out)
    monkeypatch.setattr(picks, "PHASE5_ACTIVATION_ROOT", activation_root)
    ml_rules, live_model = picks.load_ml_rules_and_model()
    assert ml_rules == [] and live_model is None
    assert picks.load_ml_fade_rules() == []
    guarded_thresholds, _ou, _btts, _fallback = picks.load_thresholds()
    assert all(not str(edge.get("rule", "")).startswith("ml-meta")
               for edge in guarded_thresholds.values())
    assert guarded_thresholds[2]["rule"] == "2way avg_p>=60"

    # Provider data is injected as fixtures, so this proves unrelated 2-way
    # scoring continues while the mismatched ML families cannot emit.
    day = "2099-01-01"
    key = (picks.source_team_key("Alpha FC"), picks.source_team_key("Beta FC"))
    row = {
        "date": day, "home": "Alpha FC", "away": "Beta FC",
        "p1": 0.82, "px": 0.10, "p2": 0.08,
        "kickoff": "2099-01-01T20:00:00Z", "league": "Test League",
    }
    monkeypatch.setattr(picks, "fetch_all", lambda _day: {
        "vitibet": {key: dict(row)}, "betclan": {key: dict(row)},
    })
    thresholds = {2: {
        "n_way": 2, "threshold": 60.0,
        "rule": "2way avg_p>=60", "display_rule": "2WAY>=60",
    }}
    emitted, _vetoes, _upcoming, _ = picks.run_day(
        day, thresholds, None, None, source_weights_1x2={}
    )
    assert emitted and all(not str(pick.get("rule", "")).startswith("ml-") for pick in emitted)


def test_protected_cut_payload_mismatch_blocks_both_ml_loaders(tmp_path, monkeypatch, capsys):
    baseline, activation_root = _fixture(tmp_path)
    current = copy.deepcopy(baseline)
    protected = next(e for e in current["edges"] if e["rule"] == "ml-meta avg_p>=55")
    protected["where"] = "ml_p*100 >= 50"
    assert inspect_operational_registry(current, activation_root)["ok"] is False

    picks = _load_script("phase5_test_picks_cut_mismatch", "scripts/picks_today.py")
    registry_path = tmp_path / "edges_consensus.json"
    registry_path.write_text(json.dumps(current), encoding="utf-8")
    monkeypatch.setattr(picks, "EDGES_PATH", registry_path)
    monkeypatch.setattr(picks, "PHASE5_ACTIVATION_ROOT", activation_root)

    assert picks.load_ml_rules_and_model() == ([], None)
    assert picks.load_ml_fade_rules() == []
    thresholds, _ou, _btts, _fallback = picks.load_thresholds()
    assert all(not str(edge.get("rule", "")).startswith("ml-meta")
               for edge in thresholds.values())
    assert "PHASE5_REGISTRY_GUARD ML_META_RULES_BLOCKED" in capsys.readouterr().err


def test_guard_accepts_only_risk_reducing_status_demotion(tmp_path):
    baseline, activation_root = _fixture(tmp_path)
    current = copy.deepcopy(baseline)
    by_rule = {edge["rule"]: edge for edge in current["edges"]}
    by_rule["ml-meta avg_p>=55"]["status"] = "candidate"
    by_rule["ml-meta avg_p>=65"]["status"] = "benched"
    assert inspect_operational_registry(current, activation_root)["ok"] is True

    promoted_baseline_bench = copy.deepcopy(current)
    by_rule = {edge["rule"]: edge for edge in promoted_baseline_bench["edges"]}
    by_rule["ml-meta avg_p>=60"]["status"] = "candidate"
    assert inspect_operational_registry(promoted_baseline_bench, activation_root)["ok"] is False

    promoted_candidate = copy.deepcopy(current)
    by_rule = {edge["rule"]: edge for edge in promoted_candidate["edges"]}
    by_rule["ml-meta avg_p>=65"]["status"] = "certified"
    assert inspect_operational_registry(promoted_candidate, activation_root)["ok"] is False


def test_red_green_model_overwrite_mutation_is_detected_then_guarded(tmp_path):
    baseline, activation_root = _fixture(tmp_path)
    candidate = _candidate_from(baseline)

    # RED: an unguarded legacy replacement fails the baseline assertion.
    unguarded = copy.deepcopy(candidate)
    with pytest.raises(AssertionError):
        assert inspect_operational_registry(unguarded, activation_root)["ok"] is True

    # GREEN: the production merge rejects the candidate model/cuts while
    # retaining its allowed non-ML refresh.
    guarded, report = preserve_live_ml_payload(candidate, baseline)
    assert guarded["ml_model"] == baseline["ml_model"]
    assert report["candidate_model_key"] != report["preserved_model_key"]
    assert inspect_operational_registry(guarded, activation_root)["ok"] is True
    assert next(e for e in guarded["edges"] if e["rule"] == "2way avg_p>=60")["train"]["n"] == 240


def test_decay_monitor_refuses_unprovenanced_or_candidate_model_export(tmp_path, monkeypatch):
    monitor = _load_script("phase5_test_decay_monitor", "scripts/decay_monitor.py")
    monkeypatch.setattr(monitor, "ROOT", tmp_path)
    path = tmp_path / "localdata" / "ml_meta_predictions.csv.gz"
    path.parent.mkdir(parents=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        handle.write("date,home,away,ml_p,pick,model_key\n")
        handle.write("2026-10-08,A,B,0.7,home,candidate-key\n")

    con = duckdb.connect(":memory:")
    con.execute("""CREATE TABLE consensus3 (
        sport VARCHAR, date VARCHAR, home VARCHAR, away VARCHAR,
        outcome VARCHAR, pick_odds DOUBLE, league VARCHAR
    )""")
    con.execute("INSERT INTO consensus3 VALUES ('soccer','2026-10-08','A','B','home',1.8,'L')")

    blocked = monitor.recreate_views(
        con, expected_model_key="incumbent-key", require_ml_provenance=True
    )
    assert "ml_meta_settled" not in blocked

    allowed = monitor.recreate_views(
        con, expected_model_key="candidate-key", require_ml_provenance=True
    )
    assert "ml_meta_settled" in allowed

    with gzip.open(path, "at", encoding="utf-8", newline="") as handle:
        handle.write("2026-10-08,C,D,0.6,home,\n")
    partial = monitor.recreate_views(
        con, expected_model_key="candidate-key", require_ml_provenance=True
    )
    assert "ml_meta_settled" not in partial
    con.close()
