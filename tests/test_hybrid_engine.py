"""Hermetic tests for the hybrid empirical-cohort engine (Addendum 17).

Two layers pinned with exact math:
1. fetch_match_cohort() — the outcome-UNCONDITIONED cohort SQL (fixture has no
   outcome column at all: an accidental outcome condition would crash).
2. compute_dynamic_enhancement() — the override math, provenance tags and
   complement coherence, verified by running the function twice (cohort
   absent vs present) over an empty-stats warehouse so every prior is a
   deterministic default.
"""
import json
import math

import duckdb
import pytest

import scripts.picks_today as pt


# --------------------------------------------------------------------------
# fetch_match_cohort — real SQL over a tiny warehouse
# --------------------------------------------------------------------------

def _cohort_con():
    con = duckdb.connect(":memory:")
    con.execute(
        "CREATE TABLE consensus3 (date VARCHAR, home VARCHAR, away VARCHAR, "
        "fb_pick VARCHAR, zb_pick VARCHAR, sa_pick VARCHAR, avg_p DOUBLE)"
    )
    con.execute(
        "CREATE TABLE forebet_settled (date VARCHAR, home VARCHAR, away VARCHAR, "
        "hs INTEGER, gs INTEGER)"
    )
    rows = [
        # in cohort: unanimous 'home', avg_p inside the 62 ± 5 band
        ("2026-01-01", "A", "B", "home", "home", "home", 62.0, 2, 1),
        ("2026-01-02", "C", "D", "home", "home", "home", 60.0, 0, 0),
        ("2026-01-03", "E", "F", "home", "home", "home", 66.0, 3, 2),
        # excluded: not unanimous
        ("2026-01-04", "G", "H", "home", "away", "home", 63.0, 5, 0),
        # excluded: avg_p outside the band
        ("2026-01-05", "I", "J", "home", "home", "home", 80.0, 4, 1),
    ]
    for d, h, a, fb, zb, sa, p, hs, gs in rows:
        con.execute("INSERT INTO consensus3 VALUES (?,?,?,?,?,?,?)", [d, h, a, fb, zb, sa, p])
        con.execute("INSERT INTO forebet_settled VALUES (?,?,?,?,?)", [d, h, a, hs, gs])
    return con


def test_fetch_match_cohort_rates(monkeypatch):
    monkeypatch.setattr(pt, "HYBRID_MIN_N", 3)
    c = pt.fetch_match_cohort(_cohort_con(), "home", 62.0, 3)
    assert c is not None and c["n"] == 3
    # totals 3 / 0 / 5 goals; hs 2,0,3; gs 1,0,2
    assert c["avg_goals"] == pytest.approx(8 / 3)
    assert c["over15"] == pytest.approx(2 / 3)
    assert c["over25"] == pytest.approx(2 / 3)
    assert c["over35"] == pytest.approx(1 / 3)
    assert c["over45"] == pytest.approx(1 / 3)
    assert c["btts"] == pytest.approx(2 / 3)
    assert c["h_o05"] == pytest.approx(2 / 3)
    assert c["h_o15"] == pytest.approx(2 / 3)
    assert c["h_o25"] == pytest.approx(1 / 3)
    assert c["h_o35"] == pytest.approx(0.0)
    assert c["a_o05"] == pytest.approx(2 / 3)
    assert c["a_o15"] == pytest.approx(1 / 3)
    assert c["a_o25"] == pytest.approx(0.0)
    assert c["a_o35"] == pytest.approx(0.0)


def test_fetch_match_cohort_gate_and_bad_input():
    # cohort exists (n=3) but is far thinner than the unpatched HYBRID_MIN_N=100
    assert pt.fetch_match_cohort(_cohort_con(), "home", 62.0, 3) is None
    # no unanimous-draw rows at all
    assert pt.fetch_match_cohort(_cohort_con(), "draw", 62.0, 3) is None
    # garbage selection short-circuits
    assert pt.fetch_match_cohort(_cohort_con(), "banana", 62.0, 3) is None
    # broken connection never raises
    assert pt.fetch_match_cohort(None, "home", 62.0, 3) is None


# --------------------------------------------------------------------------
# _hybrid_shrink / _hybrid_pick_n_way — pure math
# --------------------------------------------------------------------------

def test_hybrid_shrink_math():
    K = pt.HYBRID_SHRINK_K
    # exact empirical-Bayes pin
    assert pt._hybrid_shrink(0.41, 220, 0.525) == pytest.approx(
        (220 * 0.41 + K * 0.525) / (220 + K), abs=1e-12)
    # missing cohort rate -> prior untouched
    assert pt._hybrid_shrink(None, 220, 0.525) == 0.525
    # convex combo: stays strictly inside the extremes
    lo = pt._hybrid_shrink(0.0, 500, 0.6)
    hi = pt._hybrid_shrink(1.0, 500, 0.6)
    assert 0.0 < lo < 0.6 < hi < 1.0
    # deeper cohort pulls harder; higher cohort rate ranks higher
    assert pt._hybrid_shrink(0.7, 1000, 0.5) > pt._hybrid_shrink(0.7, 100, 0.5)
    assert pt._hybrid_shrink(0.8, 100, 0.5) > pt._hybrid_shrink(0.6, 100, 0.5)


def test_hybrid_pick_n_way():
    assert pt._hybrid_pick_n_way({"edge_rule": "3way-unanimous avg_p>=65"}) == 3
    assert pt._hybrid_pick_n_way({"edge_rule": "2way-unanimous avg_p>=70"}) == 2
    assert pt._hybrid_pick_n_way({}) == 3
    assert pt._hybrid_pick_n_way({"edge_rule": None}) == 3


# --------------------------------------------------------------------------
# compute_dynamic_enhancement — end-to-end over an empty-stats warehouse
# --------------------------------------------------------------------------

def _empty_warehouse():
    con = duckdb.connect(":memory:")
    con.execute(
        "CREATE TABLE forebet_settled (date VARCHAR, home VARCHAR, away VARCHAR, "
        "hs INTEGER, gs INTEGER)"
    )
    return con


def _pick():
    return {"home": "Alpha", "away": "Beta", "pick": "home", "avg_p": 62.0,
            "edge_rule": "3way-unanimous avg_p>=65", "league": "Test League"}


def _priced_index(prices=None, default=1.50):
    """A prices index for _pick()'s fixture. Every market is priced at `default`
    unless `prices` overrides it by market name."""
    from edgefactory.enh_pricing import MARKET_PRICE_MAP
    from edgefactory.util import norm_team
    prices = prices or {}
    book = {}
    for market, mapping in MARKET_PRICE_MAP.items():
        if mapping is not None:
            book[mapping] = (prices.get(market, default), "testbook",
                             "2026-10-14T00:00", "theoddsapi")
    for sel in ("1x", "12", "x2"):
        book.setdefault(("dc", sel), (default, "testbook", "2026-10-14T00:00", "theoddsapi"))
    key = (norm_team("Alpha"), norm_team("Beta"))
    return {"pairs": {key: book}, "names": {}, "spread": {}}


def test_compute_provenance_and_legacy_parity(monkeypatch):
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: None)
    notes = pt.compute_dynamic_enhancement(_empty_warehouse(), _pick(), _priced_index())["event_notes"]
    assert notes, "defaults must still emit candidates (threshold sanity)"
    assert all(n["engine"] == "model" for n in notes)
    assert all(n["cohort_n"] is None for n in notes)
    assert all(0.0 < n["probability"] <= 1.0 for n in notes)
    json.dumps(notes)  # stays serializable


FIELDMAP = {
    "match_over_15": "over15", "match_over_25": "over25", "match_over_35": "over35",
    "match_over_45": "over45", "btts_yes": "btts",
    "home_over_05": "h_o05", "home_over_15": "h_o15", "home_over_25": "h_o25",
    "home_over_35": "h_o35", "away_over_05": "a_o05", "away_over_15": "a_o15",
    "away_over_25": "a_o25", "away_over_35": "a_o35",
}


def test_compute_cohort_override_math(monkeypatch):
    con = _empty_warehouse()

    def run(cohort):
        monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: cohort)
        return {n["market"]: n for n in pt.compute_dynamic_enhancement(con, _pick(), _priced_index())["event_notes"]}

    base = run(None)
    assert base, "defaults must still emit candidates"

    n_c = 150
    cohort = {"n": n_c, "avg_goals": 1.1, "over15": 0.99, "over25": 0.72,
              "over35": 0.40, "over45": 0.10, "btts": 0.41,
              "h_o05": 0.95, "h_o15": 0.62, "h_o25": 0.20, "h_o35": 0.05,
              "a_o05": 0.90, "a_o15": 0.55, "a_o25": 0.15, "a_o35": 0.03}
    hyb = run(cohort)
    assert hyb, "cohort run must emit candidates"
    assert all(n["engine"] == "hybrid_cohort" and n["cohort_n"] == n_c
               for n in hyb.values())
    assert all(0.0 < n["probability"] <= 1.0 for n in hyb.values())

    K = pt.HYBRID_SHRINK_K
    undermap = {
        "home_under_15": "h_o15", "home_under_25": "h_o25", "home_under_35": "h_o35",
        "away_under_15": "a_o15", "away_under_25": "a_o25", "away_under_35": "a_o35",
    }
    shared = 0
    for mkt, field in list(FIELDMAP.items()) + list(undermap.items()):
        if mkt not in base or mkt not in hyb:
            continue
        expect = (n_c * cohort[field] + K * base[mkt]["raw_probability"]) / (n_c + K)
        if mkt in undermap:
            # Implementation computes under = 1 - shrink(over_rate). Because the
            # legacy under prior is itself the complement of the over prior,
            # this equals shrinking the UNDER rates directly — pinned here:
            base_under_prior = base[mkt]["raw_probability"]
            expect = (n_c * (1.0 - cohort[field]) + K * base_under_prior) / (n_c + K)
        assert hyb[mkt]["raw_probability"] == pytest.approx(expect, abs=1e-9), (
            f"{mkt}: {hyb[mkt]['raw_probability']} != {expect}")
        shared += 1
    # btts complement pair: emitted side must be the exact complement
    if "btts_yes" in hyb and "btts_no" in hyb:
        assert hyb["btts_yes"]["raw_probability"] + hyb["btts_no"]["raw_probability"] == pytest.approx(1.0)
    # the observed failure mode (audit: btts_yes over-promised by -11.3pp) is
    # corrected toward the cohort when the cohort rate is below the prior
    if "btts_yes" in base and "btts_yes" in hyb:
        if base["btts_yes"]["raw_probability"] > cohort["btts"]:
            assert hyb["btts_yes"]["raw_probability"] < base["btts_yes"]["raw_probability"]
    assert shared >= 2, f"too few shared candidates to pin the override math ({shared})"

    # Poisson lambda anchor: empty stats -> model lam = 0.4*2.5 + 0.6*2.5 = 2.5
    # exactly; cohort run anchors it to the shrunk cohort avg_goals.
    if "exact_2" in base and "exact_2" in hyb:
        lam_model = 2.5
        lam_exp = (n_c * cohort["avg_goals"] + K * lam_model) / (n_c + K)
        assert base["exact_2"]["raw_probability"] == pytest.approx(
            math.exp(-lam_model) * lam_model ** 2 / 2, abs=1e-9)
        assert hyb["exact_2"]["raw_probability"] == pytest.approx(
            math.exp(-lam_exp) * lam_exp ** 2 / 2, abs=1e-9)

    json.dumps(hyb)


def test_btts_is_a_recommendable_market_after_the_opt_out_was_lifted(monkeypatch):
    """BTTS was excluded from recommendations by an operator opt-out (2026-08-08),
    lifted 2026-10-14. A high-probability BTTS-yes candidate must now reach the
    recommendation list rather than being filtered out before ranking."""
    con = _empty_warehouse()
    cohort = {"n": 150, "avg_goals": 2.9, "over15": 0.99, "over25": 0.90,
              "over35": 0.70, "over45": 0.40, "btts": 0.90,
              "h_o05": 0.95, "h_o15": 0.70, "h_o25": 0.40, "h_o35": 0.20,
              "a_o05": 0.90, "a_o15": 0.60, "a_o25": 0.30, "a_o35": 0.10}
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: cohort)
    markets = {n["market"] for n in pt.compute_dynamic_enhancement(con, _pick(), _priced_index())["event_notes"]}
    assert "btts_yes" in markets


COHORT = {"n": 400, "avg_goals": 2.6, "over15": 0.60, "over25": 0.55,
          "over35": 0.85, "over45": 0.30, "btts": 0.50,
          "h_o05": 0.90, "h_o15": 0.60, "h_o25": 0.30, "h_o35": 0.10,
          "a_o05": 0.70, "a_o15": 0.30, "a_o25": 0.10, "a_o35": 0.02}


def test_cohort_realized_rate_reads_overs_directly_and_unders_as_complements():
    """The realized cohort is the probability for every market it can speak to.
    Unders are the complement of the matching over or score rate."""
    assert pt.cohort_realized_rate(None, "match_over_25") is None
    assert pt.cohort_realized_rate(COHORT, "match_over_25") == pytest.approx(0.55)
    assert pt.cohort_realized_rate(COHORT, "match_under_25") == pytest.approx(0.45)
    assert pt.cohort_realized_rate(COHORT, "home_under_35") == pytest.approx(0.90)
    assert pt.cohort_realized_rate(COHORT, "btts_no") == pytest.approx(0.50)
    # outside the cohort's columns: no realized rate
    assert pt.cohort_realized_rate(COHORT, "double_chance") is None
    assert pt.cohort_realized_rate(COHORT, "exact_2") is None


def test_event_notes_are_ordered_by_realized_cohort_rate(monkeypatch):
    """The survivors come back sorted by realized cohort rate, highest first,
    not by the enhancement registry or by stated probability."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: COHORT)
    notes = pt.compute_dynamic_enhancement(con, _pick(), _priced_index())["event_notes"]
    ranked = [pt.cohort_realized_rate(COHORT, n["market"]) for n in notes]
    assert len(ranked) >= 2, "need at least two candidates to order"
    assert ranked == sorted(ranked, reverse=True)


def test_with_a_cohort_every_candidate_is_its_realized_rate(monkeypatch):
    """Cohort replaces stated: each candidate's probability is the cohort rate
    for its market, the stated value is kept as raw_probability, and markets the
    cohort cannot speak to (double chance, exact scores) are not candidates."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: COHORT)
    notes = pt.compute_dynamic_enhancement(con, _pick(), _priced_index())["event_notes"]
    assert notes, "the cohort should leave at least one candidate"
    for n in notes:
        assert n["probability"] == pytest.approx(
            pt.cohort_realized_rate(COHORT, n["market"]))
        assert n["raw_probability"] is not None  # stated value kept for audit
        assert n["market"] not in {"double_chance"} and not n["market"].startswith("exact_")


def test_without_a_cohort_the_stated_path_is_unchanged(monkeypatch):
    """No cohort (no warehouse, thin cohort, draw pick) keeps the legacy stated
    probability path, so no candidate is dropped for lack of a realized rate."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: None)
    out = pt.compute_dynamic_enhancement(con, _pick(), _priced_index())
    for n in out["event_notes"]:
        assert "realized cohort" not in n["reason"]


def test_selection_takes_the_highest_hit_rate_among_priced_at_the_minimum(monkeypatch):
    """Operator 2026-10-14: the highest realized hit rate wins, not the highest
    edge. Over 2.5 at 57% and 1.80 must beat Over 3.5 at 35% and 3.03, even
    though Over 3.5 has the larger stated edge."""
    con = _empty_warehouse()
    cohort = dict(COHORT, over25=0.57, over35=0.35)
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: cohort)
    prices = {"match_over_25": 1.80, "match_over_35": 3.03}
    # every other candidate priced under the minimum so the two overs compete
    for m in ("match_over_15", "match_over_45", "btts_yes", "btts_no"):
        prices[m] = 1.10
    index = _priced_index(prices, default=1.10)
    out = pt.compute_dynamic_enhancement(con, _pick(), index)
    assert out["recommended_enhancement"] == "match_over_25"
    assert all(n["enhancement_price"] >= 1.30 for n in out["event_notes"])  # MIN_LEG_ODDS


def test_no_recommendation_when_nothing_is_priced_at_the_minimum(monkeypatch):
    """No candidate priced at or above the minimum means no recommendation, not
    an unpriced fallback (the old path picked 98-99% unders at 1.02)."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: COHORT)
    out = pt.compute_dynamic_enhancement(con, _pick(), _priced_index(default=1.05))
    assert out["recommended_enhancement"] is None
    assert out["event_notes"] == []


def test_no_prices_means_no_recommendation(monkeypatch):
    """Without a price index nothing can be eligible, so nothing is recommended."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: COHORT)
    out = pt.compute_dynamic_enhancement(con, _pick(), None)
    assert out["recommended_enhancement"] is None
