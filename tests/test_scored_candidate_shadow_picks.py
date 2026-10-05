"""Fixture-level scored-universe capture — picks-build integration contracts.

Pins that eval_1x2's optional ``fixture_audit`` list mirrors the EXACT
counters behind ``coverage: scored=`` (the n_up key union and the
ML-inference increment) at their source, and that threading the audit list
through changes nothing about picks, vetoes or the returned counts.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import picks_today as pt  # noqa: E402

DAY = "2026-09-06"


@pytest.fixture(autouse=True)
def _no_ml(monkeypatch):
    """Hermetic eval_1x2: no model/rules files, no warehouse reads."""
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], None))
    monkeypatch.setattr(pt, "load_ml_fade_rules", lambda: [])
    monkeypatch.setattr(pt, "get_rolling_hit_rate_last_14d", lambda day: 0.75)


def _src_row(home, away, **extra):
    row = {"home": home, "away": away, "league": "Portugal,Primeira Liga",
           "kickoff": f"{DAY} 20:30", "sport": "soccer"}
    row.update(extra)
    return row


def _data():
    # 3 unique fixture keys across the 1x2 sources -> n_up == 3
    return {
        "zulubet": {
            "k1": _src_row("Sporting CP", "Portimonense"),
            "k2": _src_row("Benfica", "Gil Vicente"),
        },
        "statarea": {
            "k1": _src_row("Sporting CP", "Portimonense"),
            "k3": _src_row("Porto", "Estoril Praia"),
        },
    }


def test_fixture_audit_mirrors_n_up_at_its_source():
    audit: list = []
    picks, vetoes, n_up = pt.eval_1x2(DAY, _data(), [], fixture_audit=audit)
    upcoming = [e for e in audit if e["kind"] == "upcoming_fixture"]
    assert n_up == 3
    assert len(upcoming) == n_up          # one entry per counted key, exactly
    assert {(e["home"], e["away"]) for e in upcoming} == {
        ("Sporting CP", "Portimonense"), ("Benfica", "Gil Vicente"),
        ("Porto", "Estoril Praia")}


def test_fixture_audit_is_pure_observation_results_identical():
    base = pt.eval_1x2(DAY, _data(), [])
    audit: list = []
    audited = pt.eval_1x2(DAY, _data(), [], fixture_audit=audit)
    assert audited == base                # picks, vetoes, n_up all unchanged
    assert len(audit) == base[2]


def test_ml_scored_entries_append_at_the_inference_increment(monkeypatch):
    """With a serving model and probability-bearing sources, one
    ml_scored_fixture audit entry appears per model-scored fixture — the
    same 1:1 point that feeds research_collector.scored / ml_scored_day."""
    model = {"coef": [0.1], "intercept": 0.0, "feature_cols": ["fb_p"]}
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], model))
    data = {
        "zulubet": {"k1": _src_row("Sporting CP", "Portimonense",
                                   p1=60, px=25, p2=15,
                                   odd1=1.5, oddx=4.0, odd2=6.0)},
        "statarea": {"k1": _src_row("Sporting CP", "Portimonense",
                                    p1=58, px=27, p2=15)},
    }
    audit: list = []
    collector = pt.FadeResearchCollector()
    picks, vetoes, n_up = pt.eval_1x2(DAY, data, [], fixture_audit=audit,
                                      research_collector=collector)
    ml_entries = [e for e in audit if e["kind"] == "ml_scored_fixture"]
    assert len(ml_entries) == 1
    assert collector.scored == len(ml_entries)   # exact 1:1 with ml_scored_day
    entry = ml_entries[0]
    assert entry["home"] == "Sporting CP"
    assert entry["ml_majority_pick"] == "home"
    assert 0.0 < entry["ml_probability"] < 1.0
    # betting intent is persisted at the scoring instant, with the side
    # odds the scorer itself saw (zulubet odd1=1.5; no 1.50 feature-default
    # fabrication — the odds really exist on the source row here)
    assert entry["market"] == "1x2"
    assert entry["selection"] == "home"
    assert entry["selection_team"] == "Sporting CP"
    assert entry["shadow_price"] == 1.5
    assert entry["shadow_price_source"] == "zulubet"
    assert entry["shadow_price_as_of_basis"] == "fetched_this_run"
    assert entry["shadow_price_captured_at_utc"]
    # and the audit changed nothing in the certified-emission path
    base = pt.eval_1x2(DAY, data, [],
                       research_collector=pt.FadeResearchCollector())
    assert (picks, vetoes, n_up) == base


def test_ml_entry_without_source_odds_carries_no_fabricated_price(monkeypatch):
    """The 1.50 pick_odds FEATURE default must never become a shadow price:
    when no source row has odds for the side, shadow_price is None."""
    model = {"coef": [0.1], "intercept": 0.0, "feature_cols": ["fb_p"]}
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], model))
    data = {
        "zulubet": {"k1": _src_row("Sporting CP", "Portimonense",
                                   p1=60, px=25, p2=15)},     # no odds cols
        "statarea": {"k1": _src_row("Sporting CP", "Portimonense",
                                    p1=58, px=27, p2=15)},
    }
    audit: list = []
    pt.eval_1x2(DAY, data, [], fixture_audit=audit,
                research_collector=pt.FadeResearchCollector())
    entry = [e for e in audit if e["kind"] == "ml_scored_fixture"][0]
    assert entry["shadow_price"] is None
    assert entry["shadow_price_source"] is None
