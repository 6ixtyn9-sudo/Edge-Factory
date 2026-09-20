"""ml-fade research capture — certification independence, deterministic
derivation, stable identity, and no-leakage contracts.

Contracts pinned here:

  1. Capture happens for EVERY model-scored fixture even when NO ml-meta /
     ml-fade rule is certified (the operational emission stays empty).
  2. Binary 1X2 inversion prices the fade at the FADE side's own opposing
     source quotes (forebet/zulubet), never the parent's; draws are excluded
     explicitly and counted.
  3. Event/selection identity is stable across re-runs and spelling variants;
     parent and fade are distinct ledger keys for the same fixture.
  4. Research rows are never operational picks (no rule/bucket fields).
  5. Candidate definition is pick-time only: outcomes and closing prices
     never reach it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import picks_today as pt  # noqa: E402
from edgefactory.fade import DERIVATION, FADE_FAMILY, PARENT_FAMILY  # noqa: E402
from edgefactory.ml_fade_research import (  # noqa: E402
    FROZEN_FEATURE_COLS,
    FadeResearchCollector,
    _num,
    detect_model_drift,
    event_key,
    model_key,
)

FAKE_MODEL = {
    "coef": [0.01 * i for i in range(len(FROZEN_FEATURE_COLS))],
    "intercept": 0.5,
    "feature_cols": list(FROZEN_FEATURE_COLS),
}

FB = {
    "home": "Alpha FC", "away": "Beta United", "league": "Test League",
    "sport": "soccer", "kickoff": "2026-09-21T19:00:00+02:00",
    "p1": 55, "px": 25, "p2": 20,
    "odd1": 2.10, "oddx": 3.30, "odd2": 3.60,
    "p1_ht": 40, "px_ht": 35, "p2_ht": 25,
    "ht_hs": 1.1, "ht_gs": 0.7, "kelly": 0.05, "pred_hs": 1.8, "pred_gs": 0.9,
    "goalsavg": 2.7, "p_ng": 45, "p_under": 52, "p_gg": 48,
}
ZB = {
    "home": "Alpha FC", "away": "Beta United", "league": "Test League",
    "p1": 56, "px": 24, "p2": 20,
    "odd1": 2.05, "oddx": 3.20, "odd2": 3.50,
}
SA = {
    "home": "Alpha FC", "away": "Beta United", "league": "Test League",
    "p1": 54, "px": 26, "p2": 20,
    "p1_ht": 41, "px_ht": 34, "p2_ht": 25,
}


def _eval_data(key: str = "alpha-beta") -> dict:
    return {"forebet": {key: dict(FB)}, "zulubet": {key: dict(ZB)},
            "statarea": {key: dict(SA)}}


@pytest.fixture
def no_certified_ml_rules(monkeypatch, tmp_path):
    """A registry with a serving model but ZERO certified ml rules.

    Patched at the registry FILE seam (EDGES_PATH), exactly like the worst
    realistic future: every ml-meta/ml-fade rule benched while the ml_model
    payload still exists. Then load_ml_rules_and_model -> ([], model),
    load_ml_fade_rules -> [], load_thresholds -> fallback thresholds, and no
    operational ml pick may be emitted — yet research capture MUST keep
    working.
    """
    empty_reg = tmp_path / "edges_consensus.json"
    empty_reg.write_text(json.dumps({"edges": [], "ml_model": dict(FAKE_MODEL)}))
    monkeypatch.setattr(pt, "EDGES_PATH", empty_reg)
    return pt


def test_capture_independent_of_certification(no_certified_ml_rules):
    """No certified ml rules -> no operational ml picks, but research captured."""
    t1x2 = no_certified_ml_rules.load_thresholds()[0]
    collector = FadeResearchCollector()
    picks, _vetoes, _n_up = no_certified_ml_rules.eval_1x2(
        "2026-09-21", _eval_data(), t1x2, source_weights={},
        research_collector=collector)
    assert picks == [], f"uncertified registry emitted picks: {picks!r}"
    # both families captured for the one scored fixture
    families = {r["family"] for r in collector.finalize()}
    assert families == {PARENT_FAMILY, FADE_FAMILY}
    assert collector.scored == 1


def test_research_rows_never_join_operational_picks(no_certified_ml_rules):
    t1x2 = pt.load_thresholds()[0]
    collector = FadeResearchCollector()
    picks, _v, _n = no_certified_ml_rules.eval_1x2(
        "2026-09-21", _eval_data(), t1x2, source_weights={},
        research_collector=collector)
    keys_in_picks = {
        (p.get("home"), p.get("away"), p.get("edge_family"))
        for p in picks
    }
    for row in collector.finalize():
        assert (row["home"], row["away"], row["family"]) not in keys_in_picks
        assert "rule" not in row
        assert "bucket" not in row


def test_home_fade_inversion_and_opposing_prices():
    c = FadeResearchCollector()
    c.record(day="2026-09-21", anchor=dict(FB), fb=dict(FB), zb=dict(ZB),
             used=["forebet", "zulubet", "statarea"], majority_pick="home",
             ml_p=0.62, z_score=0.5, model=dict(FAKE_MODEL))
    rows = {r["family"]: r for r in c.finalize()}
    fade = rows[FADE_FAMILY]
    parent = rows[PARENT_FAMILY]
    assert fade["pick"] == "away"
    assert fade["parent_pick"] == "home"
    assert fade["odds_forebet"] == pytest.approx(3.60)  # opposing odd2
    assert fade["odds_zulubet"] == pytest.approx(3.50)
    assert parent["pick"] == "home"
    assert parent["odds_forebet"] == pytest.approx(2.10)  # parent's own odd1
    assert fade["avg_p"] == pytest.approx((1 - 0.62) * 100, abs=0.05)
    assert fade["parent_family"] == PARENT_FAMILY
    assert fade["edge_family"] == FADE_FAMILY
    assert fade["derivation"] == DERIVATION
    assert fade["market"] == "1x2"
    assert fade["league"] == "Test League"
    assert fade["sport"] == "soccer"
    assert fade["kickoff"] == "2026-09-21T19:00:00+02:00"
    assert fade["model_key"] == model_key(FAKE_MODEL)
    assert fade["ml_ht_diff"] == 0.0 and fade["ml_ht_total"] == 0.0


def test_away_fade_inversion_and_opposing_prices():
    c = FadeResearchCollector()
    c.record(day="2026-09-21", anchor=dict(FB), fb=dict(FB), zb=dict(ZB),
             used=["forebet"], majority_pick="away", ml_p=0.58, z_score=0.3,
             model=dict(FAKE_MODEL))
    fade = [r for r in c.finalize() if r["family"] == FADE_FAMILY][0]
    assert fade["pick"] == "home"
    assert fade["odds_forebet"] == pytest.approx(2.10)  # opposing odd1
    assert fade["odds_zulubet"] == pytest.approx(2.05)


def test_draw_parent_excluded_explicitly():
    c = FadeResearchCollector()
    c.record(day="2026-09-21", anchor=dict(FB), fb=dict(FB), zb=dict(ZB),
             used=["forebet"], majority_pick="draw", ml_p=0.70, z_score=0.9,
             model=dict(FAKE_MODEL))
    rows = c.finalize()
    assert c.draw_excluded == 1
    assert [r["family"] for r in rows] == [PARENT_FAMILY]  # no invented fade


def test_stable_identity_and_spelling_variants():
    k1 = event_key(FADE_FAMILY, "2026-09-21", "Nordsjælland", "Norrköping")
    k2 = event_key(FADE_FAMILY, "2026-09-21", "Nordsjaelland", "Norrkoping")
    assert k1 is not None and k1 == k2
    parent_key = event_key(PARENT_FAMILY, "2026-09-21", "Nordsjælland", "Norrköping")
    assert parent_key != k1  # parent/fade distinct ledger keys
    # riskier inputs fail closed
    assert event_key(FADE_FAMILY, "2026-09-21", "", "X") is None
    assert event_key(FADE_FAMILY, "2026-09-21", "X", "") is None


def test_intraday_duplicate_first_wins():
    c = FadeResearchCollector()
    for zb_odd2 in (3.50, 3.90):  # later scan shows a different quote
        zb = dict(ZB)
        zb["odd2"] = zb_odd2
        c.record(day="2026-09-21", anchor=dict(FB), fb=dict(FB), zb=zb,
                 used=["forebet", "zulubet"], majority_pick="home", ml_p=0.62,
                 z_score=0.5, model=dict(FAKE_MODEL))
    rows = c.finalize()
    assert len(rows) == 2  # parent + fade, once
    fade = [r for r in rows if r["family"] == FADE_FAMILY][0]
    assert fade["odds_zulubet"] == pytest.approx(3.50)  # FIRST observation kept


def test_malformed_identity_skipped_and_counted():
    c = FadeResearchCollector()
    c.record(day="2026-09-21", anchor={"home": "", "away": "X"}, fb=dict(FB),
             zb=dict(ZB), used=["forebet"], majority_pick="home", ml_p=0.6,
             z_score=0.5, model=dict(FAKE_MODEL))
    assert c.finalize() == []
    assert c.identity_skipped == 1
    assert c.scored == 1  # fixture WAS scored; the skip is visible, not silent


def test_odds_cell_parsing_fail_closed():
    assert _num(None) is None
    assert _num("") is None
    assert _num("abc") is None
    assert _num(1.0) is None  # not a real quote
    assert _num(0.95) is None
    assert _num(float("nan")) is None
    assert _num("3,40") == pytest.approx(3.40)  # decimal-comma source cell
    assert _num("3.50") == pytest.approx(3.50)


def test_model_identity_and_method_drift():
    assert model_key(None) is None
    assert model_key(FAKE_MODEL) == model_key(dict(FAKE_MODEL))
    clean = detect_model_drift(FAKE_MODEL)
    assert not clean["drifted"]
    reordered = dict(FAKE_MODEL)
    reordered["feature_cols"] = list(reversed(FROZEN_FEATURE_COLS))
    assert detect_model_drift(reordered)["drifted"]
    extra = dict(FAKE_MODEL)
    extra["feature_cols"] = list(FROZEN_FEATURE_COLS) + ["closing_odds"]
    drift = detect_model_drift(extra)
    assert drift["drifted"] and any("closing_odds" in r for r in drift["reasons"])
    missing = dict(FAKE_MODEL)
    missing["feature_cols"] = [c for c in FROZEN_FEATURE_COLS if c != "ht_diff"]
    assert detect_model_drift(missing)["drifted"]
    none = detect_model_drift(None)
    assert none["drifted"] and none["model_key"] is None


def test_contract_carried_on_rows_for_audit():
    """Checkpoint-⑫ contract fields ride along: a breach would be auditable."""
    c = FadeResearchCollector()
    c.record(day="2026-09-21", anchor=dict(FB), fb=dict(FB), zb=dict(ZB),
             used=["forebet"], majority_pick="home", ml_p=0.6, z_score=0.5,
             model=dict(FAKE_MODEL), ml_ht_diff=1.0, ml_ht_total=2.0)
    row = c.finalize()[0]
    assert row["ml_ht_diff"] == 1.0 and row["ml_ht_total"] == 2.0
