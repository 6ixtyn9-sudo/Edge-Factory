"""Engine-aware debias tests — fixture JSON per Addendum 19's unit-test rule.

Covers: source preference (by_market, not by_enhancement), min-n gating,
hybrid-vs-model gating, model/legacy cell fallback, and the never-boost rule.
"""
import json

from edgefactory.debias import (MIN_ENGINE_N, MIN_MARKET_N,
                                load_engine_aware_debias_map, resolve_debias_hr)


def _slot(n, hits, realized, promised):
    return {"n": n, "hits": hits, "realized": realized,
            "mean_promised": promised, "delta": round(realized - promised, 6)}


def _write_fixture(tmp_path, by_market, by_engine_by_market=None,
                   by_enhancement=None):
    notes = {"event_notes_audit": {
        "by_market": by_market,
        "by_engine_by_market": by_engine_by_market or {},
    }}
    if by_enhancement is not None:
        notes["enhancements_audit"] = {"by_enhancement": by_enhancement}
    p = tmp_path / "picks_audit_rolling.json"
    p.write_text(json.dumps(notes))
    return p


def test_missing_or_corrupt_file_returns_empty_map(tmp_path):
    assert load_engine_aware_debias_map(tmp_path / "nope.json") == {}
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json")
    assert load_engine_aware_debias_map(bad) == {}


def test_source_preference_is_by_market_not_by_enhancement(tmp_path):
    # by_enhancement says match_over_25 has a strong recommendation record,
    # but by_market has no n>=15 cell -> the engine-aware map must NOT use it.
    p = _write_fixture(
        tmp_path,
        by_market={"match_over_25": _slot(14, 8, 0.57, 0.55)},
        by_enhancement={"match_over_25": {"recommended": 9, "hits": 5,
                                          "hit_rate": 0.556}},
    )
    m = load_engine_aware_debias_map(p)
    assert "match_over_25" not in m


def test_market_min_n_gate(tmp_path):
    p = _write_fixture(tmp_path, by_market={
        "thin": _slot(MIN_MARKET_N - 1, 2, 0.10, 0.50),
        "ok": _slot(MIN_MARKET_N, 8, 0.50, 0.50),
    })
    m = load_engine_aware_debias_map(p)
    assert "thin" not in m
    assert "ok" in m


def test_never_boosts(tmp_path):
    p = _write_fixture(tmp_path, by_market={
        "match_over_25": _slot(17, 11, 0.647, 0.544),  # over-performs
    })
    m = load_engine_aware_debias_map(p)
    assert m["match_over_25"]["pooled"] == 1.0
    assert resolve_debias_hr("match_over_25", "legacy", m) == 1.0


def test_damp_is_realized_over_promised_capped(tmp_path):
    p = _write_fixture(tmp_path, by_market={
        "goal_range_2_3": _slot(26, 8, 0.308, 0.461),
    })
    m = load_engine_aware_debias_map(p)
    expected = 0.308 / 0.461
    assert abs(m["goal_range_2_3"]["pooled"] - expected) < 1e-9
    assert resolve_debias_hr("goal_range_2_3", "legacy", m) == expected


def test_hybrid_gated_when_not_worse_than_model(tmp_path):
    # hybrid |delta| 0.05 <= model |delta| 0.10 -> hr=1.0 (no double-damp)
    p = _write_fixture(
        tmp_path,
        by_market={"match_over_25": _slot(17, 9, 0.60, 0.568)},
        by_engine_by_market={
            "hybrid_cohort": {"match_over_25": _slot(7, 3, 0.45, 0.50)},
            "model": {"match_over_25": _slot(6, 2, 0.40, 0.50)},
        },
    )
    m = load_engine_aware_debias_map(p)
    assert resolve_debias_hr("match_over_25", "hybrid_cohort", m) == 1.0


def test_hybrid_damped_when_worse_than_model(tmp_path):
    # hybrid |delta| 0.10 > model |delta| 0.05 -> damped by its own cell
    p = _write_fixture(
        tmp_path,
        by_market={"match_over_25": _slot(17, 9, 0.60, 0.568)},
        by_engine_by_market={
            "hybrid_cohort": {"match_over_25": _slot(7, 2, 0.40, 0.50)},
            "model": {"match_over_25": _slot(6, 3, 0.45, 0.50)},
        },
    )
    m = load_engine_aware_debias_map(p)
    assert resolve_debias_hr("match_over_25", "hybrid_cohort", m) == 0.8


def test_hybrid_without_model_cell_is_gated(tmp_path):
    p = _write_fixture(
        tmp_path,
        by_market={"btts_yes": _slot(28, 13, 0.464, 0.514)},
        by_engine_by_market={
            "hybrid_cohort": {"btts_yes": _slot(6, 2, 0.33, 0.50)},
        },
    )
    m = load_engine_aware_debias_map(p)
    assert resolve_debias_hr("btts_yes", "hybrid_cohort", m) == 1.0


def test_model_uses_own_cell_else_pooled_else_one(tmp_path):
    p = _write_fixture(
        tmp_path,
        by_market={
            "with_cell": _slot(16, 6, 0.30, 0.45),
            "pooled_only": _slot(16, 6, 0.30, 0.45),
            "no_evidence": _slot(5, 1, 0.20, 0.40),
        },
        by_engine_by_market={
            "model": {"with_cell": _slot(6, 2, 0.25, 0.50)},
            "legacy": {"with_cell": _slot(6, 2, 0.25, 0.50)},
        },
    )
    m = load_engine_aware_debias_map(p)
    # model has its own cell on with_cell -> cell damp
    assert resolve_debias_hr("with_cell", "model", m) == 0.5
    # no model cell on pooled_only -> pooled damp
    assert abs(resolve_debias_hr("pooled_only", "model", m) - 0.30 / 0.45) < 1e-9
    # no cell and no pooled evidence -> 1.0
    assert resolve_debias_hr("no_evidence", "model", m) == 1.0
    # legacy falls back the same way
    assert abs(resolve_debias_hr("pooled_only", "legacy", m) - 0.30 / 0.45) < 1e-9


def test_engine_cell_min_n_gate(tmp_path):
    p = _write_fixture(
        tmp_path,
        by_market={"match_over_25": _slot(17, 9, 0.60, 0.568)},
        by_engine_by_market={
            # thin cell: below MIN_ENGINE_N -> not an engine cell
            "model": {"match_over_25": _slot(MIN_ENGINE_N - 1, 2, 0.40, 0.50)},
        },
    )
    m = load_engine_aware_debias_map(p)
    assert "model" not in m["match_over_25"]["engines"]
    assert resolve_debias_hr("match_over_25", "model", m) == 1.0  # pooled is 1.0 (over-performs)


def test_missing_market_resolves_to_one(tmp_path):
    m = load_engine_aware_debias_map(_write_fixture(tmp_path, by_market={}))
    assert resolve_debias_hr("anything", "model", m) == 1.0
    assert resolve_debias_hr("anything", "hybrid_cohort", m) == 1.0
