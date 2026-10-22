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

def test_prior_shrinkage_and_imputed_model_path_are_retired():
    import inspect
    assert not hasattr(pt, "_hybrid_shrink")
    assert not hasattr(pt, "HYBRID_SHRINK_K")
    source = inspect.getsource(pt.compute_dynamic_enhancement)
    assert "forebet_settled" not in source
    assert "poisson(" not in source
    assert "league_stats" not in source
    assert "home_stats" not in source
    assert "away_stats" not in source


def test_hybrid_pick_n_way():
    assert pt._hybrid_pick_n_way({"edge_rule": "3way-unanimous avg_p>=65"}) == 3
    assert pt._hybrid_pick_n_way({"edge_rule": "2way-unanimous avg_p>=70"}) == 2
    assert pt._hybrid_pick_n_way({}) == 3
    assert pt._hybrid_pick_n_way({"edge_rule": None}) == 3


# --------------------------------------------------------------------------
# compute_dynamic_enhancement — end-to-end over an empty-stats warehouse
# --------------------------------------------------------------------------

from enhancement_fixtures import compute_with_fixture_cohort


def _compute(con, row, prices):
    return compute_with_fixture_cohort(pt, con, row, prices)


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
    notes = _compute(_empty_warehouse(), _pick(), _priced_index())["event_notes"]
    assert notes == [], "model priors must never authorize a realized-cohort bet"
    assert all(n["engine"] == "model" for n in notes)
    assert all(n["cohort_n"] is None for n in notes)
    assert all(0.0 < n["cohort_rate"] <= 1.0 for n in notes)
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
        return {n["market"]: n for n in _compute(con, _pick(), _priced_index())["event_notes"]}

    base = run(None)
    assert base == {}, "no model-only recommendations"

    n_c = 150
    cohort = {"n": n_c, "avg_goals": 1.1, "over15": 0.99, "over25": 0.72,
              "over35": 0.40, "over45": 0.10, "btts": 0.41,
              "h_o05": 0.95, "h_o15": 0.62, "h_o25": 0.20, "h_o35": 0.05,
              "a_o05": 0.90, "a_o15": 0.55, "a_o25": 0.15, "a_o35": 0.03}
    hyb = run(cohort)
    assert hyb, "cohort run must emit candidates"
    assert all(n["probability"] is None for n in hyb.values())
    assert all(n["engine"] == "hybrid_cohort" and n["cohort_n"] == n_c
               for n in hyb.values())
    assert all(0.0 < n["cohort_rate"] <= 1.0 for n in hyb.values())

    # No raw/model priors remain; only actual realized cohort rates
    # are used to select/rank. No model-only baseline can place a bet.
    for market, note in hyb.items():
        assert note['cohort_rate'] == pytest.approx(pt.cohort_realized_rate(cohort, market))
        assert note['raw_probability'] is None
    if 'btts_yes' in hyb and 'btts_no' in hyb:
        assert hyb['btts_yes']['cohort_rate'] + hyb['btts_no']['cohort_rate'] == pytest.approx(1.0)

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
    markets = {n["market"] for n in _compute(con, _pick(), _priced_index())["event_notes"]}
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
    notes = _compute(con, _pick(), _priced_index())["event_notes"]
    # Production ranks the persisted four-decimal rate; complements such as
    # 1-.7 can differ from .3 by a floating-point epsilon before persistence.
    ranked = [n["cohort_rate"] for n in notes]
    assert ranked == pytest.approx([pt.cohort_realized_rate(COHORT, n["market"]) for n in notes])
    assert len(ranked) >= 2, "need at least two candidates to order"
    assert ranked == sorted(ranked, reverse=True)


def test_with_a_cohort_every_candidate_is_its_realized_rate(monkeypatch):
    """Descriptive cohort rates never become fixture probabilities: each candidate carries a rate
    for its market, raw_probability stays unavailable, and markets the
    cohort cannot speak to (double chance, exact scores) are not candidates."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: COHORT)
    notes = _compute(con, _pick(), _priced_index())["event_notes"]
    assert notes, "the cohort should leave at least one candidate"
    for n in notes:
        assert n["cohort_rate"] == pytest.approx(
            pt.cohort_realized_rate(COHORT, n["market"]))
        assert n["raw_probability"] is None  # no invented model diagnostics
        assert n["market"] not in {"double_chance"} and not n["market"].startswith("exact_")


def test_without_a_cohort_the_stated_path_cannot_place_a_bet(monkeypatch):
    """No cohort means no invented probability, candidate or recommendation."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: None)
    out = _compute(con, _pick(), _priced_index())
    assert out["event_notes"] == []
    assert out["recommended_enhancement"] is None


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
    out = _compute(con, _pick(), index)
    assert out["recommended_enhancement"] == "match_over_25"
    assert all(n["enhancement_price"] >= 1.30 for n in out["event_notes"])  # MIN_LEG_ODDS


def test_no_recommendation_when_nothing_is_priced_at_the_minimum(monkeypatch):
    """No candidate priced at or above the minimum means no recommendation, not
    an unpriced fallback (the old path picked 98-99% unders at 1.02)."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: COHORT)
    out = _compute(con, _pick(), _priced_index(default=1.05))
    assert out["recommended_enhancement"] is None
    assert out["event_notes"] == []


def test_no_prices_means_no_recommendation(monkeypatch):
    """Without a price index nothing can be eligible, so nothing is recommended."""
    con = _empty_warehouse()
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: COHORT)
    out = _compute(con, _pick(), None)
    assert out["recommended_enhancement"] is None


@pytest.mark.parametrize("market, rate", [
    ("match_under_15", 0.70),
    ("match_under_25", 0.80),
    ("match_under_35", 0.85),
    ("match_under_45", 0.90),
    ("home_under_15", 0.70),
    ("home_under_25", 0.80),
    ("away_under_15", 0.70),
    ("away_under_35", 0.85),
])
def test_under_competes_at_shared_minimum_without_legacy_line_filter(monkeypatch, market, rate):
    """A priced under below its old threshold can beat a lower-rate over.

    All other quotes are below 1.30: no fallback prices, no free unders.
    """
    monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, "1")
    cohort = dict(COHORT, over15=0.30, over25=0.20, over35=0.15, over45=0.10,
                  h_o15=0.30, h_o25=0.20, a_o15=0.30, a_o35=0.15)
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: cohort)
    index = _priced_index({market: 1.30, "match_over_15": 1.50}, default=1.10)
    out = _compute(_empty_warehouse(), _pick(), index)
    assert out["recommended_enhancement"] == market
    assert out["enhancement_cohort_rate"] == pytest.approx(rate)
    assert out["enhancement_price"] == 1.30
    assert out["event_notes"][0]["market"] == market
    log = next(e for e in out["enh_candidate_log"] if e["market"] == market)
    assert log["status"] == "recommended"


@pytest.mark.parametrize("price, over35, reason", [
    (1.29, 0.20, "below_min_leg_odds"),
    (1.30, 0.09, "prob_outside_band"),  # 91%: existing ceiling still applies
    (1.30, 0.80, "below_line_threshold"),  # 20%: existing lower bound
])
def test_under_still_respects_price_and_rate_band(monkeypatch, price, over35, reason):
    monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, "1")
    cohort = dict(COHORT, over35=over35)
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: cohort)
    out = _compute(
        _empty_warehouse(), _pick(),
        _priced_index({"match_under_35": price}, default=1.10))
    assert out["recommended_enhancement"] is None
    log = next(e for e in out["enh_candidate_log"] if e["market"] == "match_under_35")
    assert log["reason"] == reason


def test_realized_display_pairs_from_real_sql_remain_winner_only():
    """Exercise new SQL columns and complements, not just a mocked tuple."""
    from scripts.audit_recent_picks import parse_statistical_comment
    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE consensus3 (date VARCHAR, home VARCHAR, away VARCHAR, "
                "avg_p DOUBLE, outcome VARCHAR, fb_pick VARCHAR, zb_pick VARCHAR, sa_pick VARCHAR)")
    con.execute("CREATE TABLE forebet_settled (date VARCHAR, home VARCHAR, away VARCHAR, "
                "hs INTEGER, gs INTEGER)")
    for i, (hs, gs) in enumerate(((0, 0), (1, 0), (2, 0), (2, 1), (3, 1), (4, 1))):
        outcome = "draw" if hs == gs else "home"
        con.execute("INSERT INTO consensus3 VALUES ('2026-10-01', ?, 'Beta', 70, ?, 'home', 'home', 'home')",
                    [f"Alpha{i}", outcome])
        con.execute("INSERT INTO forebet_settled VALUES ('2026-10-01', ?, 'Beta', ?, ?)",
                    [f"Alpha{i}", hs, gs])
    comment = pt.fetch_historical_profile(con, "home", 70.0, 3)
    assert "Win (n=5)" in comment
    for line, over, under in (("1.5", "80.0", "20.0"), ("2.5", "60.0", "40.0"),
                              ("3.5", "40.0", "60.0"), ("4.5", "20.0", "80.0")):
        assert f"Over {line}: {over}% | Under {line}: {under}%" in comment
    parsed = parse_statistical_comment(comment)
    assert parsed["over25"] == pytest.approx(0.60)
    assert parsed["home_o15"] == pytest.approx(0.80)
    assert parsed["btts"] == pytest.approx(0.60)
    assert parsed["avg_goals"] == 3.0
    con.close()


def test_cohort_parity_default_on_with_explicit_legacy_rollback(monkeypatch):
    monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, "0")
    cohort = dict(COHORT, over15=0.30, over25=0.20, over35=0.15, over45=0.10)
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: cohort)
    index = _priced_index({"match_under_25": 1.30, "match_under_45": 1.30}, default=1.10)
    baseline = _compute(_empty_warehouse(), _pick(), index)
    assert baseline["recommended_enhancement"] is None
    assert not any(e["market"] == "match_under_45" for e in baseline["enh_candidate_log"])
    monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
    research = _compute(_empty_warehouse(), _pick(), index)
    assert research["recommended_enhancement"] == "match_under_45"
    assert research["enhancement_cohort_rate"] == pytest.approx(0.90)


def test_cohort_switch_does_not_relax_the_model_only_path(monkeypatch):
    monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: None)
    monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
    baseline = _compute(_empty_warehouse(), _pick(), _priced_index())
    monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, "0")
    assert _compute(_empty_warehouse(), _pick(), _priced_index()) == baseline


def test_default_selection_stress_coherent_rates_and_random_prices(monkeypatch):
    """100 coherent score distributions: no synthetic ROI, just numeric invariants."""
    import random
    from edgefactory.enh_pricing import MARKET_PRICE_MAP
    rng = random.Random(20261019)
    monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
    con = _empty_warehouse()
    for _ in range(100):
        scores = [(rng.randrange(5), rng.randrange(4)) for _ in range(200)]
        cohort = {"n": 200, "avg_goals": sum(h+a for h, a in scores)/200,
                  "btts": sum(h > 0 and a > 0 for h, a in scores)/200}
        for k in (1, 2, 3, 4):
            cohort[f"over{k}5"] = sum(h+a > k for h, a in scores)/200
        for side, index in (("h", 0), ("a", 1)):
            for k in range(4):
                cohort[f"{side}_o{k}5"] = sum(s[index] > k for s in scores)/200
        prices = {m: round(rng.uniform(1.02, 3.0), 2) for m in MARKET_PRICE_MAP}
        monkeypatch.setattr(pt, "fetch_match_cohort", lambda *a, **k: cohort)
        out = _compute(con, _pick(), _priced_index(prices))
        expected = []
        for market in set(pt.COHORT_DIRECT_KEYS) | set(pt.COHORT_COMPLEMENT_KEYS):
            rate = pt.cohort_realized_rate(cohort, market)
            if MARKET_PRICE_MAP.get(market) and .25 <= rate <= .90 and prices[market] >= 1.30:
                expected.append((rate, prices[market], market))
        if not expected:
            assert out["recommended_enhancement"] is None
            continue
        best_rate, best_price, _ = max(expected)
        assert out["enhancement_cohort_rate"] == pytest.approx(best_rate, abs=.000051)
        assert out["enhancement_price"] == best_price
        assert out["enhancement_price"] >= 1.30
        assert all(.25 <= n["cohort_rate"] <= .90 for n in out["event_notes"])
    con.close()


@pytest.mark.parametrize('rate, price, eligible, reason', [
    (.80, 1.40, False, 'below_line_threshold'),
    (.8499, 1.40, False, 'below_line_threshold'),
    (.85, 1.40, True, None),
    (.90, 1.40, True, None),
    (.9001, 1.40, False, 'prob_outside_band'),
    (.85, 1.29, False, 'below_min_leg_odds'),
])
def test_legacy_rollback_under25_threshold_and_price_boundaries(monkeypatch, rate, price, eligible, reason):
    monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, "0")
    cohort = _under25_boundary_cohort(rate)
    monkeypatch.setattr(pt, 'fetch_match_cohort', lambda *a, **k: cohort)
    con = _empty_warehouse()
    try:
        out = _compute(
            con, _pick(), _priced_index({'match_under_25': price}, default=1.10))
    finally:
        con.close()
    assert (out['recommended_enhancement'] == 'match_under_25') is eligible
    log = next(e for e in out['enh_candidate_log'] if e['market'] == 'match_under_25')
    assert log['status'] == ('recommended' if eligible else 'excluded')
    assert log['reason'] == reason


def _under25_boundary_cohort(rate):
    # Coherent two-score population: rate finish 1-0, remainder finish 3-0.
    return {'n': 10000, 'avg_goals': 3-2*rate, 'over15': 1-rate,
            'over25': 1-rate, 'over35': 0., 'over45': 0., 'btts': 0.,
            'h_o05': 1., 'h_o15': 1-rate, 'h_o25': 1-rate, 'h_o35': 0.,
            'a_o05': 0., 'a_o15': 0., 'a_o25': 0., 'a_o35': 0.}


def test_default_eighty_percent_under25_at_one_point_four(monkeypatch):
    monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
    monkeypatch.setattr(pt, 'fetch_match_cohort', lambda *a, **k: _under25_boundary_cohort(.8))
    con = _empty_warehouse()
    try:
        out = _compute(
            con, _pick(), _priced_index({'match_under_25': 1.40}, default=1.10))
    finally:
        con.close()
    assert out['recommended_enhancement'] == 'match_under_25'
    assert out['enhancement_cohort_rate'] == pytest.approx(.80)
    assert out['enhancement_price'] == 1.40


@pytest.mark.parametrize('scenario, parity, expected', [
    ('higher_competitor', False, 'home_over_05'),
    ('higher_competitor', True, 'home_over_05'),
    ('under_displaces_btts', False, 'btts_yes'),
    ('under_displaces_btts', True, 'match_under_25'),
    ('higher_roi_btts', True, 'match_under_25'),
    ('under_below_price_floor', True, 'btts_yes'),
    ('equal_rate_price_tiebreak', True, 'btts_yes'),
])
def test_full_market_contention_not_under25_in_isolation(monkeypatch, scenario, parity, expected):
    """Admitting a market is not selecting it; ranking is rate, then price, not EV."""
    if parity:
        monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
    else:
        monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, '0')
    if scenario == 'higher_competitor':
        # U2.5=80%, home scores=83%. Both probabilities come from the same scores.
        scores = [(0, 0)] * 17 + [(1, 0)] * 63 + [(2, 1)] * 20
        prices = {'match_under_25': 1.40, 'home_over_05': 1.35}
    elif scenario == 'equal_rate_price_tiebreak':
        scores = [(1, 1)] * 60 + [(0, 0)] * 20 + [(2, 1)] * 20
        prices = {'match_under_25': 1.40, 'btts_yes': 1.50}
    else:
        # U2.5=80%, BTTS=60%; legacy admits BTTS but excludes U2.5.
        scores = [(1, 1)] * 40 + [(0, 0)] * 40 + [(2, 1)] * 20
        prices = {'match_under_25': 1.29 if scenario == 'under_below_price_floor' else 1.40,
                  'btts_yes': 2.10 if scenario == 'higher_roi_btts' else 1.80}
    n = len(scores)
    cohort = {'n': n, 'avg_goals': sum(h+a for h, a in scores)/n,
              'btts': sum(h > 0 and a > 0 for h, a in scores)/n}
    for k in (1, 2, 3, 4):
        cohort[f'over{k}5'] = sum(h+a > k for h, a in scores)/n
    for side, index in (('h', 0), ('a', 1)):
        for k in range(4):
            cohort[f'{side}_o{k}5'] = sum(s[index] > k for s in scores)/n
    monkeypatch.setattr(pt, 'fetch_match_cohort', lambda *a, **k: cohort)
    con = _empty_warehouse()
    try:
        out = _compute(con, _pick(), _priced_index(prices, default=1.10))
    finally:
        con.close()
    assert out['recommended_enhancement'] == expected
    if scenario == 'higher_roi_btts':
        # 60%*2.10-1=26% exceeds 80%*1.40-1=12%; existing hit-rate policy still takes U2.5.
        assert .60 * prices['btts_yes'] - 1 > .80 * prices['match_under_25'] - 1


@pytest.mark.parametrize('rate, eligible', [
    (.2499, False), (.25, True), (.7499, True), (.75, True), (.80, True),
    (.90, True), (.9001, False),
])
def test_authorized_default_has_one_shared_cohort_band_not_a_new_75pct_floor(monkeypatch, rate, eligible):
    monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
    monkeypatch.setattr(pt, 'fetch_match_cohort', lambda *a, **k: _under25_boundary_cohort(rate))
    con = _empty_warehouse()
    try:
        out = _compute(
            con, _pick(), _priced_index({'match_under_25': 1.40}, default=1.10))
    finally:
        con.close()
    assert (out['recommended_enhancement'] == 'match_under_25') is eligible
    if eligible:
        assert out['enhancement_cohort_rate'] == pytest.approx(rate)
        assert out['event_notes'][0]['cohort_n'] == 10000


def test_default_and_explicit_on_identical_with_a_cohort(monkeypatch):
    monkeypatch.setattr(pt, 'fetch_match_cohort', lambda *a, **k: _under25_boundary_cohort(.75))
    index = _priced_index({'match_under_25': 1.40, 'btts_no': 1.50}, default=1.10)
    con = _empty_warehouse()
    try:
        monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
        default = _compute(con, _pick(), index)
        monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, '1')
        assert _compute(con, _pick(), index) == default
        monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, '0')
        legacy = _compute(con, _pick(), index)
        assert default['recommended_enhancement'] == 'match_under_25'
        assert legacy['recommended_enhancement'] is None
    finally:
        con.close()


def test_authorized_75pct_under_displaces_60pct_btts_with_both_priced(monkeypatch):
    # 35% 1-1, 40% 0-0, 25% 2-1: U2.5=75%, BTTS=60%, n=100.
    cohort = {'n': 100, 'avg_goals': 1.45, 'over15': .60, 'over25': .25,
              'over35': 0., 'over45': 0., 'btts': .60,
              'h_o05': .60, 'h_o15': .25, 'h_o25': 0., 'h_o35': 0.,
              'a_o05': .60, 'a_o15': 0., 'a_o25': 0., 'a_o35': 0.}
    monkeypatch.setattr(pt, 'fetch_match_cohort', lambda *a, **k: cohort)
    prices = _priced_index({'match_under_25': 1.40, 'btts_yes': 1.80}, default=1.10)
    con = _empty_warehouse()
    try:
        monkeypatch.setenv(pt.ENH_COHORT_PARITY_ENV, '0')
        assert _compute(con, _pick(), prices)['recommended_enhancement'] == 'btts_yes'
        monkeypatch.delenv(pt.ENH_COHORT_PARITY_ENV, raising=False)
        out = _compute(con, _pick(), prices)
    finally:
        con.close()
    assert out['recommended_enhancement'] == 'match_under_25'
    assert out['enhancement_cohort_rate'] == .75
    assert next(e for e in out['enh_candidate_log'] if e['market'] == 'btts_yes')['status'] == 'eligible_not_selected'
