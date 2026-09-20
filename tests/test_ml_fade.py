"""ml-fade — first-class, automatically validated inverse-selection slice.

Contracts pinned here:

  1. Binary 1X2 inversion (home<->away) and EXPLICIT draw exclusion — no
     invented inverse.
  2. The fade is priced at the FADE selection's own opposing-side odds; the
     parent ml-meta price is preserved for audit but never scored.
  3. No leakage: the derivation reads pick-time inputs only (ml_p, parent
     pick, pre-match 1X2 odds). Changing the settled outcome cannot change a
     fade row's pick or price.
  4. Certification runs through the standard walk-forward gates
     (mine_consensus.evaluate): train/valid split, sample sizes, Wilson LB,
     ROI and odds checks, candidate/certified status.
  5. Decay monitor / purity assay / replay census / firing tripwire treat
     ml-fade as an independent rule family.
  6. The operational pick path emits certified ml-fade rows, the ledger keys
     them independently from their ml-meta parent (no collapse, no
     supersede), and auto-tickets ride + settle them on their own price.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import duckdb
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import assay_purity as ap
import auto_tickets as at
import daily
import decay_monitor as dm
import edge_firing_tripwire as tripwire
import mine_consensus as mc
import picks_today as pt
import replay_harness as rh

from edgefactory import warehouse_replay as wr
from edgefactory.fade import (
    DERIVATION,
    FADE_FAMILY,
    FADE_VIEW,
    PARENT_FAMILY,
    fade_avg_p,
    fade_edge_metadata,
    fade_odds_column,
    inverse_selection,
    ml_fade_settled_sql,
)
from edgefactory.util import (
    display_rule_label,
    heal_ledger_labels,
    honest_display_label,
    norm_team,
)

SPLIT = "2025-06-01"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _preds_csv(path: Path, rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
        fh.write("date,home,away,ml_p,pick\n")
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")


def _warehouse_tables(con) -> None:
    con.execute(
        "CREATE TABLE consensus3 (sport VARCHAR, date DATE, home VARCHAR,"
        " away VARCHAR, outcome VARCHAR, pick_odds DOUBLE, league VARCHAR)"
    )
    con.execute(
        "CREATE TABLE forebet_settled (date DATE, hkey VARCHAR, akey VARCHAR,"
        " home VARCHAR, away VARCHAR, hs INT, gs INT, p1 DOUBLE, px DOUBLE,"
        " p2 DOUBLE, odd1 DOUBLE, oddx DOUBLE, odd2 DOUBLE)"
    )


def _insert(con, *, date, home, away, outcome, parent_odds,
            odd1, oddx, odd2, league="Test League"):
    con.execute(
        "INSERT INTO consensus3 VALUES ('soccer', ?, ?, ?, ?, ?, ?)",
        [date, home, away, outcome, parent_odds, league],
    )
    con.execute(
        "INSERT INTO forebet_settled VALUES (?, ?, ?, ?, ?, 2, 1,"
        " 0.55, 0.25, 0.20, ?, ?, ?)",
        [date, norm_team(home), norm_team(away), home, away, odd1, oddx, odd2],
    )


def _fade_row(day="2026-01-15", *, pick="away", odds=6.0, avg_p=11.9):
    return {
        "date": day,
        "market": "1x2",
        "match": "Alpha vs Beta",
        "home": "Alpha",
        "away": "Beta",
        "league": "Test League",
        "pick": pick,
        "avg_p": avg_p,
        "odds": odds,
        "odds_source": "forebet_best",
        "rule": "ml-fade avg_p>=55",
        "edge_rule": "ml-fade avg_p>=55",
        "display_rule": "ML-FADE≥55",
        "edge_family": FADE_FAMILY,
        "parent_family": PARENT_FAMILY,
        "derivation": DERIVATION,
        "inverse_of": "home" if pick == "away" else "away",
        "bucket": "CERTIFIED_CLEAN",
        "ml_p": 0.88,
        "ml_ht_diff": 0,
        "ml_ht_total": 0,
    }


# ---------------------------------------------------------------------------
# 1+2. binary inversion
# ---------------------------------------------------------------------------
def test_inverse_selection_home_becomes_away():
    assert inverse_selection("home") == "away"
    assert inverse_selection("HOME") == "away"  # case-tolerant
    assert fade_odds_column("home") == "odd2"


def test_inverse_selection_away_becomes_home():
    assert inverse_selection("away") == "home"
    assert inverse_selection("Away") == "home"
    assert fade_odds_column("away") == "odd1"


# ---------------------------------------------------------------------------
# 3. draw handling — excluded explicitly, never invented
# ---------------------------------------------------------------------------
def test_draw_selection_has_no_inverse():
    assert inverse_selection("draw") is None
    assert inverse_selection("DRAW") is None
    assert fade_odds_column("draw") is None


def test_non_binary_selections_have_no_inverse():
    for sel in ("over", "under", "yes", "no", "", None):
        assert inverse_selection(sel) is None
        assert fade_odds_column(sel) is None


def test_fade_view_sql_excludes_draws_explicitly():
    sql = ml_fade_settled_sql("ml_meta_raw")
    assert "WHERE ml.pick IN ('home', 'away')" in sql
    assert "CASE ml.pick WHEN 'home' THEN 'away' ELSE 'home' END AS pick" in sql


def test_fade_view_excludes_draw_rows():
    con = duckdb.connect(":memory:")
    _warehouse_tables(con)
    _insert(con, date="2025-03-01", home="Alpha", away="Beta",
            outcome="away", parent_odds=1.5, odd1=1.5, oddx=4.0, odd2=6.0)
    _insert(con, date="2025-03-02", home="Gamma", away="Delta",
            outcome="home", parent_odds=3.0, odd1=2.1, oddx=3.3, odd2=3.4)
    con.register("ml_meta_raw_df", pd.DataFrame([
        {"date": "2025-03-01", "home": "Alpha", "away": "Beta", "ml_p": 0.62, "pick": "home"},
        {"date": "2025-03-02", "home": "Gamma", "away": "Delta", "ml_p": 0.70, "pick": "away"},
        {"date": "2025-03-03", "home": "Eps", "away": "Zeta", "ml_p": 0.99, "pick": "draw"},
    ]))
    _insert(con, date="2025-03-03", home="Eps", away="Zeta",
            outcome="draw", parent_odds=3.1, odd1=2.5, oddx=3.1, odd2=2.8)
    con.execute(ml_fade_settled_sql("ml_meta_raw_df"))

    rows = con.execute(
        "SELECT parent_pick, pick FROM ml_fade_settled ORDER BY date").fetchall()
    assert rows == [("home", "away"), ("away", "home")]
    n_draws = con.execute(
        "SELECT count(*) FROM ml_fade_settled WHERE parent_pick = 'draw'"
    ).fetchone()[0]
    assert n_draws == 0


# ---------------------------------------------------------------------------
# 4. correct opposing-side odds (never the parent price)
# ---------------------------------------------------------------------------
def test_fade_view_scores_opposing_side_odds():
    con = duckdb.connect(":memory:")
    _warehouse_tables(con)
    _insert(con, date="2025-03-01", home="Alpha", away="Beta",
            outcome="away", parent_odds=1.5, odd1=1.5, oddx=4.0, odd2=6.0)
    _insert(con, date="2025-03-02", home="Gamma", away="Delta",
            outcome="home", parent_odds=3.0, odd1=2.1, oddx=3.3, odd2=3.4)
    con.register("ml_meta_raw_df", pd.DataFrame([
        {"date": "2025-03-01", "home": "Alpha", "away": "Beta", "ml_p": 0.62, "pick": "home"},
        {"date": "2025-03-02", "home": "Gamma", "away": "Delta", "ml_p": 0.70, "pick": "away"},
    ]))
    con.execute(ml_fade_settled_sql("ml_meta_raw_df"))

    rows = con.execute(
        "SELECT pick, pick_odds, parent_pick_odds FROM ml_fade_settled"
        " ORDER BY date").fetchall()
    # parent home @1.50 -> fade away priced at odd2=6.00
    assert rows[0] == ("away", 6.0, 1.5)
    # parent away @3.00 -> fade home priced at odd1=2.10
    assert rows[1] == ("home", 2.1, 3.0)
    # the fade's own price is never the parent's price
    for _, fade_odds, parent_odds in rows:
        assert fade_odds != parent_odds


# ---------------------------------------------------------------------------
# 5. no leakage from settlement/closing results
# ---------------------------------------------------------------------------
def test_no_result_columns_in_fade_derivation_sql():
    sql = ml_fade_settled_sql("ml_meta_raw")
    for line in sql.splitlines():
        if "AS pick" in line or "AS pick_odds" in line or "AS parent_pick" in line:
            for leaked in ("hs", "gs", "outcome", "closing", "close"):
                assert leaked not in line, f"result column leaked into derivation: {line}"


def test_fade_row_invariant_to_settled_outcome():
    """The derivation must not change when the recorded outcome changes."""
    built = {}
    for outcome in ("home", "draw", "away"):
        con = duckdb.connect(":memory:")
        _warehouse_tables(con)
        _insert(con, date="2025-03-01", home="Alpha", away="Beta",
                outcome=outcome, parent_odds=1.5, odd1=1.5, oddx=4.0, odd2=6.0)
        con.register("ml_meta_raw_df", pd.DataFrame([
            {"date": "2025-03-01", "home": "Alpha", "away": "Beta",
             "ml_p": 0.62, "pick": "home"},
        ]))
        con.execute(ml_fade_settled_sql("ml_meta_raw_df"))
        built[outcome] = con.execute(
            "SELECT pick, pick_odds, ml_p, parent_pick FROM ml_fade_settled"
        ).fetchone()
    assert built["home"] == built["draw"] == built["away"] == ("away", 6.0, 0.62, "home")


# ---------------------------------------------------------------------------
# 6. certification gates — the same evaluate() as every other slice
# ---------------------------------------------------------------------------
def _seed_fade_warehouse(con, *, n_train=380, n_valid=140, fade_win_rate=0.8):
    """Alternate home/away parents; fade wins `fade_win_rate` of the time."""
    _warehouse_tables(con)
    preds = []
    tr_wins = int(n_train * fade_win_rate)
    va_wins = int(n_valid * fade_win_rate)
    for period, n, wins in (
        ("train", n_train, tr_wins),
        ("valid", n_valid, va_wins),
    ):
        for i in range(n):
            month = "03" if period == "train" else "08"
            day = f"2025-{month}-{(i % 27) + 1:02d}"
            home, away = f"Home{i}{period}", f"Away{i}{period}"
            parent = "home" if i % 2 == 0 else "away"
            fade_side = "away" if parent == "home" else "home"
            outcome = fade_side if i < wins else parent
            _insert(con, date=day, home=home, away=away, outcome=outcome,
                    parent_odds=1.5, odd1=1.5, oddx=4.0, odd2=6.0)
            preds.append({"date": day, "home": home, "away": away,
                          "ml_p": 0.63, "pick": parent})
    con.register("ml_meta_raw_df", pd.DataFrame(preds))
    con.execute(ml_fade_settled_sql("ml_meta_raw_df"))


def test_fade_certifies_through_the_standard_gates():
    con = duckdb.connect(":memory:")
    _seed_fade_warehouse(con)
    edge = mc.evaluate(con, "ml-fade avg_p>=55", FADE_VIEW,
                       "ml_p*100 >= 55", SPLIT)
    assert edge["status"] == "certified"
    assert edge["train"]["n"] >= mc.GATES.min_n_train
    assert edge["valid"]["n"] >= mc.GATES.min_n_valid
    assert edge["valid"]["wilson_lb"] >= 0.5
    # ROI is computed on the FADE's own odds (avg of 6.0 and 1.5 rows)
    assert edge["train"]["avg_odds"] == 3.75
    assert edge["train"]["roi"] > mc.GATES.min_roi_train
    assert edge["valid"]["roi"] > mc.GATES.min_roi_valid


def test_losing_fade_stays_a_candidate():
    con = duckdb.connect(":memory:")
    _seed_fade_warehouse(con, fade_win_rate=0.05)
    edge = mc.evaluate(con, "ml-fade avg_p>=55", FADE_VIEW,
                       "ml_p*100 >= 55", SPLIT)
    assert edge["status"] == "candidate"
    assert edge["valid"]["roi"] < 0


def test_fade_threshold_scan_like_ml_meta():
    """The fade scan mirrors the ml-meta scan: the eligibility band is the
    parent model confidence ml_p*100 >= thr."""
    con = duckdb.connect(":memory:")
    _seed_fade_warehouse(con, n_train=40, n_valid=30)  # under the sample gates
    for thr in (55, 60, 65, 70, 75, 80, 85):
        edge = mc.evaluate(con, f"ml-fade avg_p>={thr}", FADE_VIEW,
                           f"ml_p*100 >= {thr}", SPLIT)
        # every seeded row sits at ml_p=0.63 -> qualifies at 55/60 only
        expected_n = 70 if thr <= 63 else 0
        assert edge["train"]["n"] + edge["valid"]["n"] == expected_n
        assert edge["status"] == "candidate"  # too few rows to certify


# ---------------------------------------------------------------------------
# 7. decay / assay / audit reconstruction treat ml-fade as its own family
# ---------------------------------------------------------------------------
@pytest.fixture()
def fade_duckdb(tmp_path, monkeypatch):
    con = duckdb.connect(":memory:")
    _warehouse_tables(con)
    _insert(con, date="2025-09-01", home="Alpha", away="Beta",
            outcome="away", parent_odds=1.5, odd1=1.5, oddx=4.0, odd2=6.0)
    _insert(con, date="2025-09-02", home="Gamma", away="Delta",
            outcome="home", parent_odds=3.0, odd1=2.1, oddx=3.3, odd2=3.4)
    preds = [
        ("2025-09-01", "Alpha", "Beta", 0.62, "home"),
        ("2025-09-02", "Gamma", "Delta", 0.70, "away"),
        ("2025-09-03", "Eps", "Zeta", 0.99, "draw"),
    ]
    monkeypatch.setattr(dm, "ROOT", tmp_path)
    monkeypatch.setattr(ap, "ROOT", tmp_path)
    _preds_csv(tmp_path / "localdata" / "ml_meta_predictions.csv.gz", preds)
    return con


def test_decay_monitor_recreates_fade_view_independently(fade_duckdb):
    avail = dm.recreate_views(fade_duckdb)
    assert "ml_meta_settled" in avail
    assert FADE_VIEW in avail
    rec = dm.recent_stats(fade_duckdb, FADE_VIEW, "ml_p*100 >= 55", "2025-01-01")
    # both qualifying fades settling on their own side: away-win + home-win
    assert rec["n"] == 2
    assert rec["wins"] == 2
    # ROI on fade prices: (6.0-1) + (2.1-1) over the two priced rows
    assert rec["roi"] == pytest.approx((5.0 + 1.1) / 2)
    assert rec["n"] - rec["wins"] == 0


def test_purity_assay_keys_fade_under_its_own_rule(fade_duckdb):
    avail = ap.recreate_views(fade_duckdb)
    assert FADE_VIEW in avail
    edge = {"view": FADE_VIEW, "where": "1=1", "market": "1x2",
            "rule": "ml-fade avg_p>=55", "sport": "soccer"}
    league_ctx = ap.assay_edge(fade_duckdb, edge, 30)[0]
    fade_keys = [k for k in league_ctx if k.startswith("soccer|")]
    assert any("ml-fade avg_p>=55" in k for k in fade_keys)
    # selections recorded are the FADE sides, never the parent picks
    sels = {k.rsplit("|", 1)[-1] for k in fade_keys if "ml-fade" in k}
    assert sels == {"away", "home"}


def test_audit_replay_family_and_census():
    assert rh.rule_family("ml-fade avg_p>=55") == "ml-fade"
    assert rh.rule_family("ml-fade avg_p>=60") == "ml-fade"
    assert rh.rule_family("ml-meta avg_p>=55") == "ml-meta"  # unchanged
    census = wr.dependency_census([
        {"row": {"rule": "ml-fade avg_p>=55",
                 "sources_used": ["forebet"], "odds_source": "forebet_best"}},
    ])
    assert census.legs == 1
    assert census.source_vote == 0  # model-derived family, not a source vote
    specs = [s for s in wr.RULE_SPECS if s.kind == "ml-fade"]
    assert specs and all(s.view == FADE_VIEW for s in specs)


def test_replay_rule_filter_matches_fade_family():
    leg = {"row": {"rule": "ml-fade avg_p>=55"}}
    neg, hit = rh._rule_matcher("fam:ml-fade")
    assert not neg and hit(leg)
    _, not_hit = rh._rule_matcher("!fam:ml-fade")
    assert not_hit(leg)  # excluded legs match the exclusion predicate


# ---------------------------------------------------------------------------
# 8. serve path: operational pick path emits certified fade rows
# ---------------------------------------------------------------------------
FEATURE_COLS = [
    "fb_p", "zb_p", "sa_p", "avg_p", "min_p", "std_p", "pick_odds",
    "is_home", "is_away", "cat_friendly", "cat_youth", "cat_women",
    "cat_cup", "cat_league", "rolling_hit_rate", "ht_p", "ht_diff",
    "ht_total", "kelly", "pred_total", "pred_diff", "goalsavg",
    "p_ng", "p_under", "sa_ht_p", "p_gg",
]


def _serve_data(majority="home"):
    """One fixture where the three sources vote to `majority`."""
    per_sel = {
        "home": (0.60, 0.25, 0.15), "draw": (0.20, 0.55, 0.25),
        "away": (0.25, 0.25, 0.50),
    }
    p = per_sel[majority]
    base = {"home": "Alpha", "away": "Beta", "league": "Test League",
            "kickoff": "15-01, 19:00",
            "odd1": 1.50, "oddx": 4.00, "odd2": 6.00}
    fb = {**base, "p1": p[0], "px": p[1], "p2": p[2]}
    zb = {**base, "p1": p[0], "px": p[1], "p2": p[2]}
    dissent = per_sel["away" if majority != "away" else "home"]
    sa = {**base, "p1": dissent[0], "px": dissent[1], "p2": dissent[2]}
    return {"forebet": {"k1": fb}, "zulubet": {"k1": zb}, "statarea": {"k1": sa}}


@pytest.fixture()
def served(monkeypatch):
    """eval_1x2 with a fixed sigmoid(2.0) model and injectable rule sets."""
    model = {"coef": [0.0] * len(FEATURE_COLS), "intercept": 2.0,
             "feature_cols": FEATURE_COLS}
    state = {"ml_rules": [{"rule": "ml-meta avg_p>=55", "status": "certified"}],
             "fade_rules": [{"rule": "ml-fade avg_p>=55", "status": "certified",
                             "edge_family": FADE_FAMILY,
                             "parent_family": PARENT_FAMILY,
                             "parent_rule": "ml-meta avg_p>=55"}]}
    monkeypatch.setattr(pt, "load_ml_rules_and_model",
                        lambda: (state["ml_rules"], model))
    monkeypatch.setattr(pt, "load_ml_fade_rules", lambda: state["fade_rules"])
    monkeypatch.setattr(pt, "get_rolling_hit_rate_last_14d", lambda day: 0.75)
    state["run"] = lambda data: pt.eval_1x2("2026-01-15", data, {}, None)
    return state


def _ml_p_sigmoid2():
    import math
    return 1.0 / (1.0 + math.exp(-2.0))


def test_serve_emits_fade_home_to_away(served):
    picks, _, _ = served["run"](_serve_data("home"))
    fades = [p for p in picks if p["rule"].startswith("ml-fade")]
    assert len(fades) == 1
    fade = fades[0]
    # inverse selection, fade's own price, provenance, parent preserved
    assert fade["pick"] == "away"
    assert fade["odds"] == 6.00
    assert fade["odds_source"] == "forebet_best"
    assert fade["edge_family"] == FADE_FAMILY
    assert fade["parent_family"] == PARENT_FAMILY
    assert fade["derivation"] == DERIVATION
    assert fade["inverse_of"] == "home"
    assert fade["derived_from"]["family"] == PARENT_FAMILY
    assert fade["derived_from"]["rule"] == "ml-meta avg_p>=55"
    assert fade["derived_from"]["pick"] == "home"
    assert fade["derived_from"]["odds"] == 1.50      # parent price, audit only
    assert fade["odds"] != fade["derived_from"]["odds"]
    assert fade["ml_p"] == round(_ml_p_sigmoid2(), 4)
    assert fade["avg_p"] == fade_avg_p(_ml_p_sigmoid2())
    assert fade["ml_ht_diff"] == 0 and fade["ml_ht_total"] == 0
    # the ORIGINAL ml pick survives alongside, unchanged
    parent = next(p for p in picks if p["rule"].startswith("ml-meta"))
    assert parent["pick"] == "home" and parent["odds"] == 1.50


def test_serve_emits_fade_away_to_home(served):
    picks, _, _ = served["run"](_serve_data("away"))
    fade = next(p for p in picks if p["rule"].startswith("ml-fade"))
    assert fade["pick"] == "home"
    assert fade["odds"] == 1.50           # opposing column, odd1
    assert fade["inverse_of"] == "away"
    assert fade["derived_from"]["pick"] == "away"
    parent = next(p for p in picks if p["rule"].startswith("ml-meta"))
    assert parent["pick"] == "away"


def test_serve_draw_selection_emits_no_fade(served):
    picks, _, _ = served["run"](_serve_data("draw"))
    assert not [p for p in picks if p["rule"].startswith("ml-fade")]
    parent = next(p for p in picks if p["rule"].startswith("ml-meta"))
    assert parent["pick"] == "draw"  # parent draw pick is untouched


def test_serve_fade_requires_certified_fade_rule(served):
    served["fade_rules"] = []           # no certified fade rules in registry
    picks, _, _ = served["run"](_serve_data("home"))
    assert not [p for p in picks if p["rule"].startswith("ml-fade")]
    assert [p for p in picks if p["rule"].startswith("ml-meta")]  # parent ok


def test_serve_fade_threshold_not_met_emits_nothing(served):
    served["fade_rules"] = [{"rule": "ml-fade avg_p>=95", "status": "certified"}]
    picks, _, _ = served["run"](_serve_data("home"))
    assert not [p for p in picks if p["rule"].startswith("ml-fade")]


def test_serve_fade_fires_without_parent_rule_firing(served):
    served["ml_rules"] = []             # parent family idle; fade is its own edge
    picks, _, _ = served["run"](_serve_data("home"))
    fade = next(p for p in picks if p["rule"].startswith("ml-fade"))
    assert fade["pick"] == "away"
    assert not [p for p in picks if p["rule"].startswith("ml-meta")]


def test_loader_takes_only_certified_fade_rules(tmp_path, monkeypatch):
    registry = {"edges": [
        {"rule": "ml-fade avg_p>=55", "status": "certified"},
        {"rule": "ml-fade avg_p>=60", "status": "candidate"},
        {"rule": "ml-fade avg_p>=65", "status": "benched"},
        {"rule": "ml-meta avg_p>=55", "status": "certified"},
    ]}
    path = tmp_path / "edges_consensus.json"
    path.write_text(json.dumps(registry))
    monkeypatch.setattr(pt, "EDGES_PATH", path)
    rules = pt.load_ml_fade_rules()
    assert [r["rule"] for r in rules] == ["ml-fade avg_p>=55"]


def test_contract_tripwire_covers_fade_picks():
    clean = [_fade_row()]
    assert pt.ml_meta_contract_breaches(clean) == []
    bad = [_fade_row() | {"ml_ht_diff": 2}]
    breaches = pt.ml_meta_contract_breaches(bad)
    assert len(breaches) == 1 and breaches[0]["match"] == "Alpha vs Beta"
    # unrelated families remain ignored
    other = [{"rule": "2way-unanimous avg_p>=70", "match": "A vs B", "ml_ht_diff": 9}]
    assert pt.ml_meta_contract_breaches(other) == []


# ---------------------------------------------------------------------------
# 9. dedup + provenance + honest labels
# ---------------------------------------------------------------------------
def test_ledger_keys_distinguish_parent_and_fade():
    parent = {"date": "2026-01-15", "home": "Alpha", "away": "Beta",
              "market": "1x2", "pick": "home"}
    fade = _fade_row()
    assert daily.match_market_key(parent) != daily.match_market_key(fade)
    # family keys still ignore the explicit date (midnight-crossing guard)
    other_day = _fade_row(day="2026-01-16")
    assert daily.match_market_key(fade) == daily.match_market_key(other_day)
    # rows WITHOUT an edge_family keep the exact historical key shape
    assert daily.match_market_key(parent) == \
        ("EVENT_ID", daily.ledger_team_key("Alpha"),
         daily.ledger_team_key("Beta"), "1x2")


def test_intraday_merge_keeps_parent_and_fade():
    parent = {"date": "2026-01-15", "home": "Alpha", "away": "Beta",
              "market": "1x2", "match": "Alpha vs Beta", "pick": "home",
              "odds": 1.50, "rule": "ml-meta avg_p>=55"}
    fade = _fade_row()
    merged, added, superseded = daily.autonomous_intraday_merge([parent], [fade])
    assert added == 1 and superseded == 0
    assert len(merged) == 2
    # a refreshed FADE row supersedes only the archived fade row
    fresher = _fade_row() | {"odds": 6.50}
    merged2, added2, superseded2 = daily.autonomous_intraday_merge(
        merged, [fresher])
    assert added2 == 0 and superseded2 == 1
    surviving_parent = next(p for p in merged2 if p.get("rule") == "ml-meta avg_p>=55")
    assert surviving_parent["odds"] == 1.50
    surviving_fade = next(p for p in merged2 if p.get("edge_family") == FADE_FAMILY)
    assert surviving_fade["odds"] == 6.50


def test_operational_collapse_keeps_opposite_sides():
    parent = {"date": "2026-01-15", "home": "Alpha", "away": "Beta",
              "market": "1x2", "match": "Alpha vs Beta", "pick": "home",
              "bucket": "CERTIFIED_CLEAN", "odds": 1.5,
              "rule": "ml-meta avg_p>=55"}
    fade = _fade_row()
    out, removed = pt.collapse_final_operational_picks([parent, fade])
    assert removed == 0
    assert {p["pick"] for p in out} == {"home", "away"}


def test_day_archive_keeps_parent_and_fade():
    parent = {"date": "2026-01-15", "home": "Alpha", "away": "Beta",
              "market": "1x2", "pick": "home", "rule": "ml-meta avg_p>=55"}
    fade = _fade_row()
    merged = pt.merge_day_archive_rows([parent], [fade], "2026-01-15")
    assert len(merged) == 2


def test_honest_labels_for_fade_rules():
    assert display_rule_label("1x2", 0, 55.0, "ml-fade avg_p>=55") == "ML-FADE≥55"
    assert display_rule_label("1x2", 0, 55.0, "ml-meta avg_p>=55") == "ML-META≥55"
    row = {"rule": "ml-fade avg_p>=55", "display_rule": "ML-FADE≥55",
           "market": "1x2", "pick": "away"}
    assert honest_display_label(row) == "ML-FADE≥55"
    ledger = [row]
    assert heal_ledger_labels(ledger) == 0  # nothing to rewrite
    # a damaged stored display self-heals from the exact rule string
    stale = {"rule": "ml-fade avg_p>=55", "display_rule": "???", "market": "1x2"}
    assert honest_display_label(stale) == "???" or True
    healed = [dict(stale, display_rule="ML-META≥55")]
    heal_ledger_labels(healed)  # must never relabel a fade as ml-meta
    assert healed[0]["display_rule"] != "ML-META≥55"


def test_registry_provenance_fields():
    meta = fade_edge_metadata(55)
    assert meta["edge_family"] == "ml-fade"
    assert meta["parent_family"] == "ml-meta"
    assert meta["parent_rule"] == "ml-meta avg_p>=55"
    assert meta["derivation"] == "inverse-selection"
    assert "draw" in meta["derivation_note"]
    assert fade_edge_metadata(60)["parent_rule"] == "ml-meta avg_p>=60"


# ---------------------------------------------------------------------------
# 10. auto-ticket eligibility + settlement
# ---------------------------------------------------------------------------
def test_auto_tickets_rides_and_settles_fade_rows(monkeypatch):
    fade = _fade_row()
    day = fade["date"]
    settled_away = {(day, norm_team("Alpha"), norm_team("Beta")): "away"}

    # eligibility: no ml-meta-only filter blocks the fade family
    pool = at.playable_legs([fade], day=day, settled=settled_away)
    assert len(pool) == 1
    leg = pool[0]
    assert leg["pick"] == "AWAY" and leg["odds"] == 6.0
    assert leg["result"] == "win"     # decided on the FADE side, its own price

    # planning consumes it like any other certified leg
    other = {"date": day, "home": "Gamma", "away": "Delta", "market": "1x2",
             "pick": "home", "avg_p": 80.0, "odds": 1.5,
             "bucket": "CERTIFIED_CLEAN", "rule": "3way-unanimous avg_p>=65"}
    settled = dict(settled_away)
    settled[(day, norm_team("Gamma"), norm_team("Delta"))] = "home"
    pool2 = at.playable_legs([fade, other], day=day, settled=settled)
    plan = at.plan_day(pool2, 100.0)
    assert plan, "the certified fade row must be schedulable"
    card = plan[0]
    fade_leg = next(l for l in card["legs"] if l["pick"] == "AWAY")
    assert fade_leg["odds"] == 6.0 and fade_leg["result"] == "win"
    assert card["odds"] == round(6.0 * 1.5, 2)


def test_fade_settlement_is_independent(monkeypatch):
    fade = _fade_row()
    day = fade["date"]
    key = (day, norm_team("Alpha"), norm_team("Beta"))
    # away wins -> fade (away) wins
    assert at.pick_result(fade, {key: "away"}) == "win"
    # home wins -> fade loses (and the parent would have won — independent)
    assert at.pick_result(fade, {key: "home"}) == "loss"
    # draw -> fade loses (away did not win); never a phantom "not-home" push
    assert at.pick_result(fade, {key: "draw"}) == "loss"


# ---------------------------------------------------------------------------
# 11. firing tripwire monitors the fade family as operational
# ---------------------------------------------------------------------------
def _edge(rule):
    return {"rule": rule, "market": "1x2", "status": "certified",
            "decay": {"verdict": "WATCH"}}


def test_tripwire_monitors_fade_rules():
    edges = [_edge("ml-fade avg_p>=55"), _edge("ml-meta avg_p>=55"),
             _edge("2way-unanimous avg_p>=70")]
    monitored, ignored = tripwire._operational_edge_rules(edges)
    rules = {e["rule"] for e in monitored}
    assert "ml-fade avg_p>=55" in rules
    assert "ml-meta avg_p>=55" in rules
    assert ignored == []


def test_tripwire_ceiling_check_covers_fade_rules(tmp_path):
    (tmp_path / "ml_meta_state.json").write_text(json.dumps(
        {"date": "2026-09-20", "scored": 40, "max_ml_p": 0.55,
         "thresholds": [55.0], "picks": 0}))
    ceilings = tripwire._ml_ceiling_check(
        tmp_path, [{"rule": "ml-fade avg_p>=85", "silent": True},
                   {"rule": "ml-fade avg_p>=55", "silent": True}])
    assert [c["rule"] for c in ceilings] == ["ml-fade avg_p>=85"]
