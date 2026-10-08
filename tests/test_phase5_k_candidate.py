"""Phase 5 K-contract tests: one builder for fit and serve, feed-ready.

These pin the properties that make a returning feed a DATA event rather than a
code change plus retrain:

* the 32-column contract is assembled in one place, in frozen order;
* a dark source is represented (``_available=0.0`` + era mean), never dropped,
  so the schema does not move when the feed returns;
* the served vector never substitutes a bare ``0.0`` for a missing column;
* a fit produced by ``scripts/fit_phase5_candidate.py`` is accepted by the real
  activation gate's payload validation.
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from edgefactory.phase5_activation import (
    DECLARED_SOURCE_ORDER,
    K_FEATURES,
    _load_passing_certificate,
)
from edgefactory.phase5_k import (
    build_k_features,
    default_fallbacks,
    feature_vector,
    majority_pick,
    payload_problems,
    source_columns,
)

ROOT = Path(__file__).resolve().parent.parent


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# The contract itself
# --------------------------------------------------------------------------
def test_k_row_has_every_column_in_frozen_order():
    row = build_k_features(
        base={"fb_p": 0.6, "zb_p": 0.55, "sa_p": 0.5, "avg_p": 0.55, "is_home": 1.0},
        sources={"zulubet": (0.55, True)},
    )
    assert list(row) == list(K_FEATURES)
    assert set(row) == set(K_FEATURES)
    assert all(isinstance(v, float) for v in row.values())
    assert row["is_home"] == 1.0


def test_dark_source_is_represented_not_dropped():
    row = build_k_features(base={}, sources={}, fallbacks={"forebet_p": 0.42})
    for source in DECLARED_SOURCE_ORDER:
        # the column exists, carries the recorded mean, and says "unavailable"
        assert row[f"{source}_p"] == pytest.approx(
            default_fallbacks()[f"{source}_p"] if source != "forebet" else 0.42
        )
        assert row[f"{source}_available"] == 0.0


def test_source_columns_clamp_and_flag():
    cols = source_columns({"vitibet": (65.0, True), "bzzoiro": (None, False)})
    assert cols["vitibet_p"] == 1.0          # percent feed cannot poison the logit
    assert cols["vitibet_available"] == 1.0
    assert cols["bzzoiro_p"] is None          # dark -> imputed by the builder
    assert cols["bzzoiro_available"] == 0.0


def test_returning_feed_does_not_move_the_schema():
    dark = build_k_features(base={"fb_p": 0.5}, sources={"betclan": (None, False)})
    live = build_k_features(base={"fb_p": 0.5}, sources={"betclan": (0.61, True)})
    assert list(dark) == list(live) == list(K_FEATURES)
    assert dark["betclan_available"] == 0.0 and live["betclan_available"] == 1.0
    assert dark["betclan_p"] != live["betclan_p"]


def test_majority_pick_mirrors_the_engine_rule():
    assert majority_pick(["home", "home", "home"]) == "home"
    assert majority_pick(["away", "away", "home"]) == "away"      # first two agree
    assert majority_pick(["away", "home", "home"]) == "home"      # last two agree
    assert majority_pick(["away", "home", "draw"]) == "away"      # engine fallback: first
    assert majority_pick(["draw", None, None]) == "draw"
    assert majority_pick([None, None, None]) is None


# --------------------------------------------------------------------------
# The served vector must never silently become zeros
# --------------------------------------------------------------------------
def test_feature_vector_imputes_recorded_means_not_zero():
    model = {
        "feature_cols": ["fb_p", "vitibet_p", "vitibet_available"],
        "coef": [1.0, 1.0, 1.0],
        "intercept": 0.0,
        "fallback_means": {"fb_p": 0.5, "vitibet_p": 0.47, "vitibet_available": 0.0},
    }
    vector, imputed = feature_vector({"fb_p": 0.62}, model)
    assert vector == [0.62, 0.47, 0.0]
    assert imputed == ["vitibet_p", "vitibet_available"]


def test_feature_vector_is_identity_when_every_column_is_present():
    model = {
        "feature_cols": ["fb_p", "zb_p"],
        "coef": [1.0, -1.0],
        "intercept": 0.1,
        "fallback_means": {"fb_p": 0.5, "zb_p": 0.5},
    }
    vector, imputed = feature_vector({"fb_p": 0.7, "zb_p": 0.3}, model)
    assert vector == [0.7, 0.3]
    assert imputed == []


# --------------------------------------------------------------------------
# The fit: shape, refusal, and acceptance by the real activation gate
# --------------------------------------------------------------------------
def _synthetic_fixtures(days: int = 200, per_day: int = 25) -> dict:
    rng = random.Random(20261008)
    fixtures: dict = {}
    start = date(2026, 1, 1)
    for offset in range(days):
        day = (start + timedelta(days=offset)).isoformat()
        for slot in range(per_day):
            strength = rng.uniform(0.30, 0.75)
            probs = {}
            for source in ("forebet", "zulubet", "statarea"):
                p = min(0.92, max(0.08, strength + rng.gauss(0, 0.06)))
                probs[source] = (p, 1 - p * 0.9, p * 0.5)
            home_p = max(probs["forebet"][0], probs["zulubet"][0], probs["statarea"][0])
            outcome = "home" if rng.random() < home_p else (
                "draw" if rng.random() < 0.25 else "away")
            key = (day, f"home{slot}", f"away{slot}")
            fixtures[key] = {
                "sources": {s: tuple(probs[s]) for s in probs},
                "outcome": outcome,
                "league": "Test League",
                "extras": {"odd1": 1.8, "oddx": 3.4, "odd2": 4.2},
            }
    return fixtures


def test_fit_payload_is_accepted_by_the_activation_gate(tmp_path):
    module = _load_script("fit_phase5_candidate", "scripts/fit_phase5_candidate.py")
    frame = module.build_frame(_synthetic_fixtures())
    assert len(frame) > module.MIN_ERA_TRAIN_ROWS
    assert module._shortfall(frame, module.era_bounds(frame)) == []

    result = module.fit_candidate(frame, module.era_bounds(frame))
    payload = result["candidate_model_payload"]
    assert payload_problems(
        payload, fallback_means=result["fallback_means"], require_fallbacks=True
    ) == []
    assert set(result["fallback_means"]) == set(K_FEATURES)
    assert result["fallback_method"] == "era_train_slice_mean"
    # The three election sources are live; the five declared capture sources
    # are dark in this fixture, and the artefact says so.
    assert result["source_coverage"]["forebet"]["status"] == "live"
    for source in ("vitibet", "bzzoiro", "betclan", "scoutingstats", "betminer"):
        assert result["source_coverage"][source]["status"] == "dark"
        assert result["source_coverage"][source]["share"] == 0.0

    certificate = {
        "record_type": "phase5_certification_verdict",
        "overall_status": "pass",
        "clauses": {str(i): {"status": "pass"} for i in range(1, 10)},
        "era_id": "era-test",
        "candidate_fit_performed": True,
        "candidate_model_payload": payload,
        "candidate_cuts": [{"rule": "ml-meta avg_p>=55"}],
        "fallback_method": result["fallback_method"],
        "fallback_means": result["fallback_means"],
    }
    path = tmp_path / "certification.json"
    path.write_text(json.dumps(certificate))
    loaded, raw = _load_passing_certificate(path, era_id="era-test")
    assert loaded["candidate_model_payload"]["feature_cols"] == list(K_FEATURES)
    assert raw


def test_fit_refuses_below_the_declared_floors():
    module = _load_script("fit_phase5_candidate_floors", "scripts/fit_phase5_candidate.py")
    frame = module.build_frame(_synthetic_fixtures(days=10, per_day=5))
    notes = module._shortfall(frame, module.era_bounds(frame))
    assert any("era-train rows" in note for note in notes)
    assert any("era span" in note for note in notes)


def test_shadow_capture_parsing_marks_only_present_sources(tmp_path):
    module = _load_script("fit_phase5_candidate_shadow", "scripts/fit_phase5_candidate.py")
    rows = [
        {
            "record_type": "phase5_shadow_prediction",
            "source": "vitibet",
            "capture_day": "2026-10-08",
            "identity": {"date": "2026-10-08", "home_key": "alpha", "away_key": "beta"},
            "probabilities": {"1x2.home": 0.5, "1x2.draw": 0.3, "1x2.away": 0.2},
            "raw_fixture": {"home": "Alpha", "away": "Beta"},
            "league": "Test",
        },
        {
            "record_type": "phase5_shadow_prediction",
            "source": "scoutingstats",
            "capture_day": "2026-10-08",
            "identity": {"date": "2026-10-08", "home_key": "alpha", "away_key": "beta"},
            "probabilities": {"1x2.home": 0.44, "1x2.draw": 0.31, "1x2.away": 0.25},
        },
        {"record_type": "phase5_shadow_attempt", "source": "betclan"},
    ]
    path = tmp_path / "rows.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows))
    store = module.load_shadow_fixtures(path, {})
    entry = store[("2026-10-08", "alpha", "beta")]
    assert set(entry["sources"]) == {"vitibet", "scoutingstats"}
    assert entry["sources"]["vitibet"][0] == 0.5
