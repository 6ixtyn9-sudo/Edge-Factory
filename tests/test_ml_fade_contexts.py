"""Conditional ml-fade slice research — contracts pinned here.

1. Context conditions (league / comp type / fade side / odds & ml_p bands)
   filter on PRE-KICKOFF fields only; outcome, scores and closing info are
   structurally unusable as conditions.
2. Walk-forward separation: train / validation / confirmation windows are
   disjoint, and grading mirrors mine_consensus.stats accounting byte for
   byte (verified against the production function on a synthetic warehouse).
3. Sample gates: the production certification gates are applied verbatim
   and NEVER relaxed; the research promotion bar is a strict superset, and
   its pass class can never alias the production `certified` status that
   picks/auto-tickets consume.
4. The candidate grid is finite, predeclared and uniquely named — every
   candidate is graded and reported (no hidden failures); dedup collapses
   only identical-evidence gate-passers and never hides failures.
5. The fade is priced at its OWN opposing-side odds everywhere; the parent
   pick/price cannot leak into fade accounting.
6. Empty slices and longshot tails behave: unpriced rows count in n but
   never in ROI, NaN prices don't corrupt, sparse data is labelled sparse.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import mine_consensus as mc

from edgefactory import fade_research as fr
from edgefactory.assay import wilson_lb
from edgefactory.config import BEST_ODDS_HAIRCUT, GATES
from edgefactory.entities import canonical_league, classify_competition
from edgefactory.fade import ml_fade_settled_sql

SPLIT = "2025-06-01"
CONFIRM = "2026-01-01"


def mk_row(**kw) -> dict:
    row = {
        "date": "2025-01-10",
        "sport": "soccer",
        "home": "A",
        "away": "B",
        "outcome": "home",
        "parent_pick": "away",
        "pick": "home",
        "ml_p": 0.70,
        "pick_odds": 5.0,
        "parent_pick_odds": 1.6,
        "league": "epl",
    }
    row.update(kw)
    # enrich AFTER overrides; explicit precomputed kwargs still win (scanner contract)
    row["league_canonical"] = kw.get("league_canonical") or canonical_league(row["league"])
    row["comp_type_pre"] = kw.get("comp_type_pre") or classify_competition(row["league"])
    return row


def win(n: int, wins: int, pnl: float, priced: int, days: int = 60) -> dict:
    """A finished window in the exact grade_rows() shape."""
    roi = pnl / priced if priced else None
    return {
        "n": n,
        "wins": wins,
        "hit": round(wins / n, 4) if n else 0.0,
        "wilson_lb": round(wilson_lb(wins, n), 4),
        "avg_odds": 2.5 if priced else None,
        "roi": round(roi, 4) if roi is not None else None,
        "roi_realistic": round(roi * BEST_ODDS_HAIRCUT, 4) if roi is not None else None,
        "n_priced": priced,
        "n_days": days,
    }


def graded(train=None, train_early=None, train_late=None, valid=None, confirm=None) -> dict:
    """Fixture clearing production gates + research bars unless overridden."""
    return {
        "train_early": train_early or win(200, 115, 25.0, 200),
        "train_late": train_late or win(200, 115, 25.0, 200),
        "train": train or win(400, 230, 50.0, 400),
        "valid": valid or win(200, 116, 30.0, 200),
        "confirm": confirm or win(100, 58, 12.0, 100),
    }


def result_of(cand: fr.Candidate, rows: list[dict], prod: bool) -> dict:
    """Result entry in the exact shape scripts/research_ml_fade_contexts.py emits."""
    return {
        "candidate": cand.name(),
        "dim": cand.dim(),
        "threshold": cand.threshold,
        "provenance": cand.provenance(),
        "graded": fr.grade_rows(rows, cand, SPLIT, CONFIRM),
        "production_gates_pass": prod,
    }


# --------------------------------------------------------------------------
# 1. Context conditions & filtering
# --------------------------------------------------------------------------
def test_fade_side_condition_filters():
    cond = fr.Condition("fade_side", "fade_side", "home")
    assert cond.matches(mk_row(pick="home"))
    assert not cond.matches(mk_row(pick="away"))
    assert not cond.matches(mk_row(pick=None))


def test_league_condition_uses_canonical_and_precomputed():
    cond = fr.Condition("league", "league", "epl")
    assert cond.matches(mk_row(league="epl"))
    assert not cond.matches(mk_row(league="it1"))
    # the scanner's precomputed canonical name wins over the raw string
    assert cond.matches(mk_row(league="English Premier League", league_canonical="epl"))


def test_comp_type_condition():
    cond = fr.Condition("comp_type", "comp_type", "league")
    assert cond.matches(mk_row(league="epl"))
    assert not cond.matches(mk_row(league="Friendly International"))


def test_odds_and_mlp_bands_are_half_open():
    odds = fr.Condition("odds_band", "pick_odds", (4.5, 6.5))
    assert odds.matches(mk_row(pick_odds=4.5))
    assert odds.matches(mk_row(pick_odds=6.4999))
    assert not odds.matches(mk_row(pick_odds=6.5))  # hi exclusive
    assert not odds.matches(mk_row(pick_odds=4.49))
    assert not odds.matches(mk_row(pick_odds=None))
    band = fr.Condition("ml_p_band", "ml_p", (0.60, 0.65))
    assert band.matches(mk_row(ml_p=0.60))
    assert not band.matches(mk_row(ml_p=0.65))
    assert fr.Condition("odds_band", "pick_odds", (10.0, 1e9)).matches(
        mk_row(pick_odds=500.0)
    )  # longshot tail is open-ended


def test_candidate_threshold_on_parent_confidence():
    cand55 = fr.Candidate(55)
    cand75 = fr.Candidate(75)
    assert cand55.matches(mk_row(ml_p=0.55))
    assert not cand55.matches(mk_row(ml_p=0.5499))
    assert not cand75.matches(mk_row(ml_p=0.70))
    assert not cand55.matches(mk_row(ml_p=None))
    assert not cand55.matches(mk_row(ml_p=float("nan")))


# --------------------------------------------------------------------------
# 2. No leakage — conditions cannot read results; fade prices its own side
# --------------------------------------------------------------------------
def test_allowed_condition_fields_exclude_results():
    banned = {
        "outcome",
        "hs",
        "gs",
        "closing_odds",
        "closing",
        "result",
        "ft_score",
        "result_home",
        "result_away",
    }
    assert banned.isdisjoint(fr.ALLOWED_CONDITION_FIELDS)
    assert {"date", "league", "parent_pick", "pick", "ml_p", "pick_odds"}.issubset(
        fr.ALLOWED_CONDITION_FIELDS
    )


def test_condition_cannot_resolve_outcome_or_closing():
    with pytest.raises(KeyError):
        fr.Condition("hack", "outcome", "home").matches(mk_row())
    with pytest.raises(KeyError):
        fr.Condition("hack", "closing_odds", (1.0, 9.0)).matches(mk_row())


def test_membership_never_depends_on_outcome():
    cand = fr.Candidate(65, (fr.Condition("odds_band", "pick_odds", (2.0, 8.0)),))
    assert cand.matches(mk_row(outcome="home")) == cand.matches(mk_row(outcome="away"))


def test_grading_priced_at_fades_own_odds_not_parents():
    base = mk_row(pick="away", outcome="away", pick_odds=3.0)
    rows = [dict(base, parent_pick_odds=1.01), dict(base, parent_pick_odds=99.0)]
    g = fr.grade_rows(rows, fr.Candidate(55), SPLIT, CONFIRM)
    # both rows priced 3.0 and both won -> roi exactly 2.0; parent price invisible
    assert g["train"]["roi"] == 2.0
    assert g["train"]["n_priced"] == 2


def test_realistic_roi_uses_halve_it_haircut():
    g = fr.grade_rows([mk_row(pick_odds=3.0)], fr.Candidate(55), SPLIT, CONFIRM)
    assert g["train"]["roi"] == 2.0
    assert g["train"]["roi_realistic"] == round(2.0 * BEST_ODDS_HAIRCUT, 4)


# --------------------------------------------------------------------------
# 3. Walk-forward separation + parity with the production stats function
# --------------------------------------------------------------------------
def test_windows_are_disjoint_and_partition_dates():
    rows = [
        mk_row(date="2025-05-31"),
        mk_row(date="2025-06-01"),
        mk_row(date="2025-12-31"),
        mk_row(date="2026-01-01"),
        mk_row(date="2026-03-01"),
    ]
    g = fr.grade_rows(rows, fr.Candidate(0.0), SPLIT, CONFIRM)
    assert g["train"]["n"] == 1  # split date itself belongs to valid
    assert g["valid"]["n"] == 2  # [split, confirm_start)
    assert g["confirm"]["n"] == 2  # confirm start belongs to confirm
    assert sum(g[w]["n"] for w in ("train", "valid", "confirm")) == len(rows)


def test_train_halves_cover_train_and_are_chronological():
    rows = [
        mk_row(date=f"2024-{m:02d}-15", pick_odds=2.0, outcome="home" if m < 7 else "away")
        for m in range(1, 13)
    ]
    g = fr.grade_rows(rows, fr.Candidate(0.0), SPLIT, CONFIRM)
    e, l = g["train_early"], g["train_late"]
    assert e["n"] + l["n"] == g["train"]["n"] == 12
    assert e["roi"] == 1.0 and l["roi"] == -1.0  # early all wins, late all losses


def _synthetic_warehouse():
    """Mini tables shaped exactly like the real L1 view inputs."""
    c3 = pd.DataFrame(
        {
            "sport": ["soccer"] * 6,
            "date": [
                "2025-01-10",
                "2025-01-11",
                "2025-02-01",
                "2025-07-01",
                "2025-08-01",
                "2025-09-01",
            ],
            "home": ["A", "C", "E", "G", "I", "K"],
            "away": ["B", "D", "F", "H", "J", "L"],
            "outcome": ["home", "away", "draw", "home", "away", "draw"],
            "pick_odds": [1.6, 2.4, 3.1, 1.5, 2.5, 3.3],
            "league": ["epl"] * 6,
        }
    )
    fb = pd.DataFrame(
        {
            "date": c3["date"],
            "home": c3["home"],
            "away": c3["away"],
            "odd1": [9.5, 2.0, 2.8, 8.0, 1.9, 2.6],
            "odd2": [1.3, 3.4, 2.9, 1.2, 4.4, 3.0],
        }
    )
    ml = pd.DataFrame(
        {
            "date": c3["date"],
            "home": c3["home"],
            "away": c3["away"],
            "ml_p": [0.80, 0.72, 0.66, 0.90, 0.60, 0.10],
            "pick": ["away", "home", "away", "away", "home", "home"],
        }
    )
    con = duckdb.connect()
    con.register("consensus3_df", c3)
    con.register("fb_df", fb)
    con.register("ml_meta_raw_df", ml)
    con.execute("CREATE TABLE consensus3 AS SELECT * FROM consensus3_df")
    con.execute("CREATE TABLE forebet_settled AS SELECT * FROM fb_df")
    con.execute("CREATE VIEW ml_meta_raw AS SELECT * FROM ml_meta_raw_df")
    con.execute(ml_fade_settled_sql("ml_meta_raw"))
    return con


def test_grade_rows_matches_production_stats_byte_for_byte():
    """The claim 'same accounting as mine_consensus' is enforced, not asserted.

    No confirm window here (confirm_start pushed past the data) so the
    research `valid` window equals production's date>=split window, making
    the numbers directly comparable function-to-function.
    """
    con = _synthetic_warehouse()
    rows = con.sql("SELECT * FROM ml_fade_settled").fetchdf().to_dict("records")
    for r in rows:
        r["date"] = str(r["date"])[:10]
    for thr, side in ((55, "away"), (70, "home")):
        where = f"pick='{side}' AND ml_p*100 >= {thr}"
        cand = fr.Candidate(thr, (fr.Condition("fade_side", "fade_side", side),))
        g = fr.grade_rows(rows, cand, SPLIT, "2100-01-01")
        for key, period in (("train", "train"), ("valid", "valid")):
            theirs = mc.stats(con, "ml_fade_settled", where, SPLIT, period)
            ours = g[key]
            assert theirs["n"] == ours["n"], (thr, side, key)
            assert theirs["wins"] == ours["wins"]
            assert theirs["n_priced"] == ours["n_priced"]
            assert theirs["wilson_lb"] == ours["wilson_lb"]
            assert (theirs["roi"] is None) == (ours["roi"] is None)
            if theirs["roi"] is not None:
                assert theirs["roi"] == pytest.approx(ours["roi"], abs=1e-4)
            else:
                assert (theirs["avg_odds"] is not None) == (ours["avg_odds"] is not None)


def test_graded_windows_are_json_serializable():
    g = fr.grade_rows([mk_row(), mk_row(date="2026-03-01")], fr.Candidate(55), SPLIT, CONFIRM)
    json.dumps(g)  # no sets / dataclasses leak into results


# --------------------------------------------------------------------------
# 4. Finite predeclared grid & candidate identity
# --------------------------------------------------------------------------
def test_grid_is_finite_recorded_and_uniquely_named():
    leagues = [f"lg{i:02d}" for i in range(20)]
    grid = fr.build_grid(leagues)
    assert len(grid) == len(fr.THRESHOLDS) * (1 + 2 + 6 + 6 + 5 + 20 + 12 + 10)
    assert len(grid) == 434
    names = [c.name() for c in grid]
    assert len(set(names)) == len(grid)  # every candidate distinguishable
    assert {c.dim() for c in grid} == set(fr.GRID_DIMENSIONS)
    assert all(n.startswith("ml-fade ") and "avg_p>=" in n for n in names)


def test_grid_has_no_arbitrary_combos():
    """Grid size moves predictably with league count — no ad-hoc space."""
    assert len(fr.build_grid([f"l{i}" for i in range(3)])) == len(fr.THRESHOLDS) * (
        1 + 2 + 6 + 6 + 5 + 3 + 12 + 10
    )
    composite = [c for c in fr.build_grid([]) if len(c.conditions) == 2]
    assert {c.dim() for c in composite} == {"fade_side_odds", "fade_side_comp"}


def test_select_top_leagues_train_only_and_stable():
    train = [mk_row(league="epl")] * 5 + [mk_row(league="it1")] * 3 + [mk_row(league="es1")] * 3
    assert fr.select_top_leagues(train, 3) == ["epl", "es1", "it1"]  # tie: name
    assert fr.select_top_leagues(train, 1) == ["epl"]
    assert fr.select_top_leagues([], 3) == []


# --------------------------------------------------------------------------
# 5. Sample gates (production verbatim) & the strict-superset promotion bar
# --------------------------------------------------------------------------
def test_production_gates_verbatim_boundaries():
    g = graded(train=win(339, 195, 30.0, 339), valid=win(700, 430, 10.0, 700))
    ok, reasons = fr.production_gates_pass(g)
    assert not ok and any("train n 339" in r for r in reasons)
    g = graded(train=win(340, 195, 30.0, 340), valid=win(119, 70, 10.0, 119))
    ok, reasons = fr.production_gates_pass(g)
    assert not ok and any("valid n 119" in r for r in reasons)
    g = graded(train=win(340, 195, 30.0, 340), valid=win(120, 64, 10.0, 120))
    ok, reasons = fr.production_gates_pass(g)
    assert not ok and any("wilson" in r for r in reasons)  # hit 0.533 too thin
    g = graded(train=win(340, 330, -60.0, 340))  # train roi ≈ -17.6% < -10%
    ok, reasons = fr.production_gates_pass(g)
    assert not ok and any("train roi" in r for r in reasons)
    g = graded(valid=win(200, 115, -1.0, 200))  # valid roi ≈ -0.5% < 0
    ok, reasons = fr.production_gates_pass(g)
    assert not ok and any("valid roi" in r for r in reasons)


def test_production_gate_numbers_match_config():
    """Pins the global gates the scan must NOT be wider than."""
    assert (GATES.min_n_train, GATES.min_n_valid) == (340, 120)
    assert GATES.min_roi_valid == 0.0
    ok, _ = fr.production_gates_pass(graded())
    assert ok  # the default fixture clears the production bar


def test_research_certified_needs_the_full_bar():
    status, _ = fr.decide_promotion(graded())
    assert status == "research-certified"


def test_confirm_window_is_load_bearing():
    g = graded(confirm=win(100, 55, -10.0, 100))  # confirm roi -10% < 0
    status, reasons = fr.decide_promotion(g)
    assert status == "exploratory-positive"
    assert any("confirm" in r for r in reasons)
    g = graded(confirm=win(29, 20, 10.0, 29))  # too little confirm data
    assert fr.decide_promotion(g)[0] == "exploratory-positive"


def test_persistence_requires_both_train_halves_and_valid_days():
    g = graded(train_early=win(200, 140, -5.0, 200))  # early half loses
    assert fr.decide_promotion(g)[0] == "exploratory-positive"
    g = graded(train_early=win(50, 30, 10.0, 50))  # half too thin to trust
    assert fr.decide_promotion(g)[0] == "exploratory-positive"
    g = graded(valid=win(200, 116, 30.0, 200, days=25))  # too few valid days
    assert fr.decide_promotion(g)[0] == "exploratory-positive"


def test_decisively_negative_is_rejected_not_certified():
    g = graded(valid=win(200, 100, -80.0, 200))
    status, reasons = fr.decide_promotion(g)
    assert status == "rejected"
    assert any("valid roi" in r for r in reasons)


def test_sparse_when_not_enough_evidence():
    g = graded(
        train=win(100, 60, 10.0, 100),
        train_early=win(50, 30, 5.0, 50),
        train_late=win(50, 30, 5.0, 50),
        valid=win(50, 30, 10.0, 50),
        confirm=win(0, 0, 0.0, 0),
    )
    assert fr.decide_promotion(g)[0] == "sparse"
    g = fr.grade_rows([], fr.Candidate(55), SPLIT, CONFIRM)
    assert fr.decide_promotion(g)[0] == "sparse"


def test_promotion_bar_is_strict_superset_of_production():
    """research-certified ⇒ production gates pass, on a battery of shapes;
    a production failure can never be research-certified."""
    shapes = [
        graded(),
        graded(train=win(339, 195, 30.0, 339)),
        graded(valid=win(200, 100, -1.0, 200)),
        graded(confirm=win(100, 50, -5.0, 100)),
        graded(train=win(340, 330, -60.0, 340)),
        graded(valid=win(120, 64, 10.0, 120)),
    ]
    for g in shapes:
        status, _ = fr.decide_promotion(g)
        ok, _ = fr.production_gates_pass(g)
        assert (status == "research-certified") <= bool(ok)


def test_pass_class_can_never_be_production_certified():
    """picks_today / auto-tickets act on registry status=='certified'. The
    research pass class is a different string, so nothing research-side can
    become bettable without the production re-mine."""
    for g in (
        graded(),
        graded(valid=win(200, 100, -1.0, 200)),
        graded(confirm=win(100, 50, -5.0, 100)),
    ):
        assert fr.decide_promotion(g)[0] != "certified"
        assert "certified" not in fr.Candidate(55).provenance().values()


# --------------------------------------------------------------------------
# 6. Provenance, reconstruction ("replay") and dedup
# --------------------------------------------------------------------------
def _rebuild_from_provenance(prov: dict) -> fr.Candidate:
    field_dim = {
        "fade_side": "fade_side",
        "pick_odds": "odds_band",
        "ml_p": "ml_p_band",
        "league": "league",
        "comp_type": "comp_type",
    }
    conds = []
    for field_name, value in prov["conditions"].items():
        v = tuple(value) if isinstance(value, list) else value
        conds.append(fr.Condition(field_dim[field_name], field_name, v))
    return fr.Candidate(prov["parent_threshold"], tuple(conds))


def test_every_grid_candidate_round_trips_its_provenance():
    grid = fr.build_grid(["epl", "it1"])
    rows = [
        mk_row(),
        mk_row(pick="away", pick_odds=3.2, league="it1", date="2026-04-01", outcome="away"),
    ]
    for cand in grid:
        prov = json.loads(json.dumps(cand.provenance()))  # JSON-safe
        assert prov["edge_family"] == "ml-fade"
        assert prov["parent_family"] == "ml-meta"
        assert prov["derivation"] == "inverse-selection"
        assert prov["scan"] == "research"
        rebuilt = _rebuild_from_provenance(prov)
        assert rebuilt.name() == cand.name()
        assert fr.grade_rows(rows, rebuilt, SPLIT, CONFIRM) == fr.grade_rows(
            rows, cand, SPLIT, CONFIRM
        )


def test_dedupe_collapses_identical_evidence_keeps_canonical():
    rows = [mk_row(ml_p=0.60 + i / 100, date=f"2025-0{i % 4 + 1}-15") for i in range(5)]
    overall = fr.Candidate(55)
    side = fr.Candidate(55, (fr.Condition("fade_side", "fade_side", "home"),))
    comp = fr.Candidate(
        55,
        (
            fr.Condition("fade_side", "fade_side", "home"),
            fr.Condition("comp_type", "comp_type", "league"),
        ),
    )
    results = [result_of(c, rows, True) for c in (side, comp, overall)]
    kept, removed = fr.dedupe_by_evidence(results)
    assert len(kept) == 1 and len(removed) == 2
    # identical evidence -> the plain `ml-fade avg_p>=55` (fewest conditions) wins
    assert kept[0]["candidate"] == "ml-fade avg_p>=55"
    assert all(r["deduped_into"] == "ml-fade avg_p>=55" for r in removed)


def test_dedupe_never_hides_failing_or_distinct_evidence():
    rows = [mk_row(outcome="away"), mk_row(date="2026-04-01", outcome="home")]
    loser = fr.Candidate(55)
    distinct = fr.Candidate(65, (fr.Condition("odds_band", "pick_odds", (1.0, 6.0)),))
    results = [result_of(loser, rows, False), result_of(distinct, rows, False)]
    kept, removed = fr.dedupe_by_evidence(results)
    assert removed == [] and len(kept) == 2  # non-passers are ALL kept visible


# --------------------------------------------------------------------------
# 7. Empty slices, sparse leagues, longshot tails
# --------------------------------------------------------------------------
def test_empty_and_absent_contexts_grade_safely():
    rows = [mk_row(league="epl")]
    empty_league = fr.Candidate(55, (fr.Condition("league", "league", "xx9"),))
    g = fr.grade_rows(rows, empty_league, SPLIT, CONFIRM)
    assert g["train"]["n"] == 0 and g["train"]["roi"] is None
    assert g["train"]["wilson_lb"] == 0.0
    assert fr.decide_promotion(g)[0] == "sparse"
    # a comp type nobody has classifies all rows out, windows stay well-formed
    women = fr.Candidate(55, (fr.Condition("comp_type", "comp_type", "women"),))
    assert fr.grade_rows(rows, women, SPLIT, CONFIRM)["valid"]["n"] == 0


def test_unpriced_rows_count_in_n_never_in_roi():
    rows = [mk_row(pick_odds=None), mk_row(pick_odds=float("nan")), mk_row(pick_odds="not-a-price")]
    g = fr.grade_rows(rows, fr.Candidate(55), SPLIT, CONFIRM)
    assert g["train"]["n"] == 3
    assert g["train"]["n_priced"] == 0
    assert g["train"]["roi"] is None and g["train"]["avg_odds"] is None
    # wilson/hit still computed over all rows, exactly like production
    assert g["train"]["wins"] == 3


def test_longshot_tail_band_extremes():
    cand = fr.Candidate(55, (fr.Condition("odds_band", "pick_odds", (10.0, 1e9)),))
    rows = [
        mk_row(pick_odds=9.99),  # below band
        mk_row(pick_odds=10.0),  # win  -> +9.0
        mk_row(pick_odds=101.0, outcome="away"),
    ]  # loss -> -1.0
    g = fr.grade_rows(rows, cand, SPLIT, CONFIRM)
    assert g["train"]["n"] == 2
    assert g["train"]["roi"] == pytest.approx(4.0, abs=1e-3)
    assert g["train"]["avg_odds"] == pytest.approx(55.5, abs=1e-3)


def test_half_open_band_edges_hit_exactly_one_band():
    for price, expected in (
        (2.0, (2.0, 3.0)),
        (2.9999, (2.0, 3.0)),
        (3.0, (3.0, 4.5)),
        (6.5, (6.5, 10.0)),
        (10.0, (10.0, 1e9)),
    ):
        hits = [
            b
            for b in fr.ODDS_BANDS
            if fr.Condition("odds_band", "pick_odds", b).matches(mk_row(pick_odds=price))
        ]
        assert hits == [expected]
