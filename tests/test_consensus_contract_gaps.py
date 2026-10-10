"""Certification-contract tests: the certified label follows the enforced predicate.

Negative cases were operator-authorized 2026-10-09 and FAILED against the
incumbent evaluator by design ("keep the gap visible"); the enforcement
repair was separately authorized by the operator on 2026-10-10 ("I want them
all gone") and implemented in picks_today.eval_1x2 + _edge_entry: every
qualifier in a rule name (min_p>=N, home-only, away-only, odds-LO-HI with
inclusive lower / exclusive upper) is now enforced, and a certified label is
stamped only when the voter set IS the electorate the rule was certified on.
Unsupported emissions keep flowing under honestly-named labels (e.g.
"unanimous[statarea+vitibet] avg_p>=70") -- suppression was never the remedy.
Do not skip/xfail these tests or weaken predicates to keep CI green.

Synthetic temporary registries, one fixture, no serving model/provider/warehouse
or operational-state writes. A forbidden certified label must not be attached
to an unsupported emission; this does not require blanket suppression rather
than a separately approved, honestly named future contract.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import picks_today as pt  # noqa: E402

DAY = "2026-06-01"  # Before Forebet retirement; not a current-day production run.
HISTORICAL_TRIO = ("forebet", "zulubet", "statarea")
HISTORICAL_PAIR = ("forebet", "zulubet")


@pytest.fixture
def evaluate(monkeypatch, tmp_path):
    """Use the real registry parser and eval gate, with model I/O disabled."""
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], None))
    monkeypatch.setattr(pt, "load_ml_fade_rules", lambda: [])
    # Names are already canonical synthetic identities; avoid alias-state I/O.
    monkeypatch.setattr(pt, "canonical_display_team", lambda team: team)
    league = "England,Premier League"
    assert pt.classify_competition(league) not in {"cup", "friendly"}
    registry = tmp_path / "edges_consensus.json"
    monkeypatch.setattr(pt, "EDGES_PATH", registry)

    def run(rule, *, sources=HISTORICAL_TRIO, probabilities=(72, 72, 72),
            selection="home", odds=1.50):
        assert len(sources) == len(probabilities)
        assert len(set(sources)) == len(sources)
        assert set(sources) <= set(pt.SOURCES_1X2)
        assert selection in {"home", "away"}
        registry.write_text(json.dumps({"edges": [{
            "rule": rule, "market": "1x2", "status": "certified",
        }]}))
        thresholds, ou, btts, fallback = pt.load_thresholds()
        assert not fallback and ou is None and btts is None
        assert pt.thr_for(len(sources), thresholds)["rule"] == rule
        data = {}
        for source, prob in zip(sources, probabilities):
            assert 50 < prob < 100
            # Explicit percentages, summing to 100; unanimous on chosen side.
            other = (100 - prob) / 2
            p1, px, p2 = ((prob, other, other) if selection == "home"
                          else (other, other, prob))
            data[source] = {"fixture-1": {
                "home": "Contract Home", "away": "Contract Away",
                "league": league, "sport": "soccer",
                "kickoff": f"{DAY} 18:00:00", "p1": p1, "px": px, "p2": p2,
                "odd1": odds, "oddx": 4.0, "odd2": odds,
            }}
        picks, vetoes, n_up = pt.eval_1x2(DAY, data, thresholds, source_weights={})
        assert vetoes == 0 and n_up == 1  # No unrelated guard masked the test.
        return picks

    return run


@pytest.mark.parametrize("rule,kwargs", [
    ("3way-unanimous min_p>=60 avg_p>=65", {"probabilities": (60, 72, 72)}),
    ("3way-unanimous home-only avg_p>=65", {"selection": "home"}),
    ("3way-unanimous odds-1.20-1.75 avg_p>=65", {"odds": 1.20}),
    ("3way-unanimous odds-1.20-1.75 avg_p>=65", {"odds": 1.74}),
])
def test_qualifier_contract_positive_control(evaluate, rule, kwargs):
    """Valid predicate/eligible historical voters: exactly one baseline row."""
    picks = evaluate(rule, **kwargs)
    assert len(picks) == 1 and picks[0]["rule"] == rule
    assert picks[0]["sources_used"] == list(HISTORICAL_TRIO)


@pytest.mark.parametrize("rule,kwargs", [
    pytest.param("3way-unanimous min_p>=60 avg_p>=65",
                 {"probabilities": (56, 72, 72)}, id="min-p-56-72-72"),
    pytest.param("3way-unanimous home-only avg_p>=65",
                 {"selection": "away"}, id="home-only-away"),
    pytest.param("3way-unanimous odds-1.20-1.75 avg_p>=65",
                 {"odds": 1.19}, id="odds-below-inclusive-lower"),
    pytest.param("3way-unanimous odds-1.20-1.75 avg_p>=65",
                 {"odds": 1.75}, id="odds-at-exclusive-upper"),
])
def test_unsupported_qualifier_must_not_carry_certified_label(evaluate, rule, kwargs):
    # min_p / odds bounds mirror mine_consensus.py's actual predicates;
    # home-only means home, not merely agreement on any side. Average clears
    # 65 in every case: it cannot substitute for the qualified predicate.
    picks = evaluate(rule, **kwargs)
    assert not any(p["rule"] == rule for p in picks), (
        f"Unenforced qualifier still stamped as certified: {rule}; rows={picks}"
    )


@pytest.mark.parametrize("rule,sources", [
    ("3way-unanimous avg_p>=65", HISTORICAL_TRIO),
    ("2way-unanimous avg_p>=70", HISTORICAL_PAIR),
])
def test_historical_electorate_positive_control(evaluate, rule, sources):
    picks = evaluate(rule, sources=sources, probabilities=(72,) * len(sources))
    assert len(picks) == 1 and picks[0]["rule"] == rule
    assert picks[0]["sources_used"] == list(sources)


@pytest.mark.parametrize("rule,sources", [
    pytest.param("3way-unanimous avg_p>=65", ("statarea", "vitibet", "bzzoiro"),
                 id="sa-vb-bz-is-not-fb-zb-sa"),
    pytest.param("2way-unanimous avg_p>=70", ("statarea", "vitibet"),
                 id="sa-vb-is-not-fb-zb"),
])
def test_substitute_electorate_must_not_carry_historical_label(evaluate, rule, sources):
    # mine_consensus.py certifies the named fb/zb and fb/zb/sa predicates,
    # not an arbitrary available pair/trio. No model exists in this fixture.
    picks = evaluate(rule, sources=sources, probabilities=(72,) * len(sources))
    assert not any(p["rule"] == rule for p in picks), (
        f"Substitute electorate {sources} inherited historical label {rule}; rows={picks}"
    )
