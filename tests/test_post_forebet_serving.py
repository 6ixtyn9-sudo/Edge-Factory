"""Red-team the shared operational contract (all evidence here is synthetic)."""
from __future__ import annotations

from copy import deepcopy
from datetime import date
import gzip
import json

import duckdb
import pandas as pd
import pytest

import scripts.mine_consensus as miner
import scripts.picks_today as picker
import scripts.assay_purity as assay
import scripts.decay_monitor as decay
from edgefactory import consensus_contracts as cc
from edgefactory.warehouse import _src_view

START, SPLIT, END, DAY = "2026-06-13", "2026-09-21", "2026-10-19", "2026-10-20"


def observation(day=DAY, name="Live Alpha", **extra):
    return dict(date=day, home=name, away="Bravo United", league="Test League",
                kickoff=f"{day}T16:00:00Z", p1=.7, px=.2, p2=.1,
                p_o15=.8, p_o25=.8, p_o35=.8, p_gg=.8,
                odd1=1.7, oddx=3.5, odd2=4.5, odd_o15=1.7, odd_u15=8.,
                odd_o25=1.7, odd_u25=8., odd_o35=1.7, odd_u35=8.,
                odd_gg=1.7, odd_ng=8., hs=None, gs=None) | extra


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    db, registry = tmp_path / "warehouse.duckdb", tmp_path / "edges_consensus.json"
    with duckdb.connect(str(db)) as con:
        rows = [observation("2026-09-01" if i < 340 else "2026-10-01",
                            f"Alpha Town {i:04d}", hs=4, gs=1) for i in range(460)]
        rows.append(observation(odd1=999.))
        frame = pd.DataFrame(rows)
        con.register("seed", frame)
        con.execute("CREATE TABLE scoutingstats AS SELECT * FROM seed")
        report = miner.remine_current_sources(con, start=START, split=SPLIT, as_of=END)
    assert any(e["statistical_gates_passed"] for e in report["edges"])
    # Keep one validated operating point per market; other tests exercise
    # the unmodified full grid and all strategy branches separately.
    report["edges"] = [e for e in report["edges"] if e["threshold"] == 65]
    original = {"ml_model": {"frozen": True}, "edges": [
        {"rule": "2way-unanimous avg_p>=65", "status": "certified"},
        {"rule": "ml-meta avg_p>=55", "status": "benched", "decay": {"verdict": "DEAD"}},
        {"rule": "ml-fade avg_p>=55", "status": "candidate"},
    ]}
    registry.write_text(json.dumps(original))
    class ActivationDate(date):
        @classmethod
        def today(cls):
            return cls.fromisoformat(END)
    # Simulate approval on END; activation may never be backdated by --as-of.
    monkeypatch.setattr(miner, "date", ActivationDate)
    monkeypatch.setattr(miner, "OUT", registry)
    monkeypatch.setattr(picker, "EDGES_PATH", registry)
    monkeypatch.setattr(picker, "LOCALDATA", tmp_path)
    monkeypatch.setattr(assay, "REG", registry)
    monkeypatch.setattr(assay, "DB", db)
    monkeypatch.setattr(assay, "OUT", tmp_path / "purity_registry.json")
    monkeypatch.setattr(decay, "REG", registry)
    monkeypatch.setattr(decay, "DB", db)
    return db, registry, report, original


def activate(prepared):
    db, path, report, _ = prepared
    with duckdb.connect(str(db)) as con:
        assert miner.activate_post_forebet_contracts(con, report)
    return json.loads(path.read_text())


def test_real_gates_shared_recreation_and_live_prices(prepared, monkeypatch):
    registry = activate(prepared)
    assert registry["operating_contract"] == cc.SCHEMA
    contracts = [e for e in registry["edges"] if e.get("contract_schema") == cc.SCHEMA]
    assert {e["market"] for e in contracts} >= {"1x2", "ou_1.5", "ou_2.5", "ou_3.5", "btts"}
    for e in contracts:
        assert e["train"]["n_priced"] == 340 and e["valid"]["n_priced"] == 120
        assert e["status"] == "certified" and not e["holds"]
    monkeypatch.setattr(picker, "fetch_all", lambda _: pytest.fail("legacy/network fetch"))
    assert picker.load_thresholds() == ({}, None, None, False)
    picks, _, _, _ = picker.run_day(DAY, {}, None, None)
    assert {p["market"] for p in picks} == {e["market"] for e in contracts}
    assert all(p["odds"] is None and p["odds_source"] is None for p in picks)
    assert all(p["contract_id"] == p["rule"] == p["edge_rule"] for p in picks)
    assert all(p["sources_used"] == ["scoutingstats"] for p in picks)
    assert registry["ml_model"] == prepared[3]["ml_model"]
    for old in prepared[3]["edges"][1:]:
        assert old in registry["edges"]
    assert next(e for e in registry["edges"] if e["rule"].startswith("2way"))["status"] == "retired"
    # Historical re-runs before activation cannot rewrite earlier selections.
    assert not picker.run_day("2026-10-18", {}, None, None)[0]


@pytest.mark.parametrize("period,field,value", [
    ("train", "n", 339), ("valid", "n", 119),
    ("train", "n_priced", 339), ("valid", "n_priced", 119),
    ("train", "roi", -.101), ("valid", "roi", -.001),
    ("valid", "wilson_lb", .499), ("valid", "roi", None),
    ("valid", "roi", float("nan")),
])
def test_gate_rejection_never_mutates_incumbent(prepared, period, field, value):
    db, path, report, _ = prepared
    report["edges"] = [deepcopy(report["edges"][0])]
    report["edges"][0][period][field] = value
    before = path.read_bytes()
    with duckdb.connect(str(db)) as con:
        assert not miner.activate_post_forebet_contracts(con, report)
    assert path.read_bytes() == before


def test_forged_passing_statistics_are_rejected_before_atomic_write(prepared):
    db, path, report, _ = prepared
    report["edges"][0]["valid"]["roi"] = 99.
    before = path.read_bytes()
    with duckdb.connect(str(db)) as con, pytest.raises(RuntimeError, match="statistics mismatch"):
        miner.activate_post_forebet_contracts(con, report)
    assert path.read_bytes() == before


@pytest.mark.parametrize("bad", ["forebet", "unknown"])
def test_retired_or_unknown_electorate_cannot_activate(prepared, bad):
    db, path, report, _ = prepared
    report["edges"][0]["sources"] = [bad]
    before = path.read_bytes()
    with duckdb.connect(str(db)) as con, pytest.raises(ValueError):
        miner.activate_post_forebet_contracts(con, report)
    assert path.read_bytes() == before


def test_bench_and_baseline_survive_daily_revalidation(prepared):
    registry = activate(prepared)
    db, path, report, _ = prepared
    contract = next(e for e in registry["edges"] if e.get("contract_schema") == cc.SCHEMA)
    contract.update(status="benched", benched_at=END, decay={"verdict": "DEAD"})
    saved = deepcopy(contract)
    path.write_text(json.dumps(registry))
    report["as_of_exclusive"] = DAY
    class NextDate(date):
        @classmethod
        def today(cls):
            return cls.fromisoformat(DAY)
    miner.date = NextDate  # restored by the fixture's monkeypatch teardown
    with duckdb.connect(str(db)) as con:
        assert miner.activate_post_forebet_contracts(con, report)
    after = json.loads(path.read_text())
    assert saved in after["edges"]
    assert all(p["rule"] != saved["rule"] for p in picker.run_day(DAY, {}, None, None)[0])


def test_empty_or_missing_capture_never_resurrects_legacy_fallback(prepared):
    registry = activate(prepared)
    for edge in registry["edges"]:
        if edge.get("contract_schema") == cc.SCHEMA:
            edge["status"] = "benched"
    prepared[1].write_text(json.dumps(registry))
    assert picker.load_thresholds() == ({}, None, None, False)
    assert not picker.run_day(DAY, {}, None, None)[0]


def test_identity_tamper_fails_closed_in_selection_and_recreation(prepared):
    registry = activate(prepared)
    for edge in registry["edges"]:
        if edge.get("contract_schema") == cc.SCHEMA:
            edge["threshold"] = 90  # identity still describes 65
    prepared[1].write_text(json.dumps(registry))
    assert not picker.run_day(DAY, {}, None, None)[0]
    with duckdb.connect(str(prepared[0])) as con:
        assert cc.recreate_contract_views(con, registry["edges"], as_of=DAY) == set()


def test_missing_vote_or_conflicting_same_source_is_not_substituted(prepared):
    registry = activate(prepared)
    db = prepared[0]
    with duckdb.connect(str(db)) as con:
        # A second conflicting prediction of the same fixture/source/market
        # cannot win by row order. An unrelated source cannot replace it.
        con.execute("INSERT INTO scoutingstats SELECT * REPLACE(.1 AS p1, .7 AS p2, .2 AS px, .2 AS p_o15, .2 AS p_o25, .2 AS p_o35, .2 AS p_gg) FROM scoutingstats WHERE date=?", [DAY])
    assert not picker.run_day(DAY, {}, None, None)[0]


def test_assay_is_exact_priced_and_decay_is_untouched_forward(prepared, monkeypatch):
    registry = activate(prepared)
    monkeypatch.setattr(assay.sys, "argv", ["assay_purity.py"])
    assay.main()
    purity = json.loads(assay.OUT.read_text())
    contracts = [e for e in registry["edges"] if e.get("contract_schema") == cc.SCHEMA]
    assert set(purity["contract_contexts"]) == {e["rule"] for e in contracts}
    for edge in contracts:
        scoped = purity["contract_contexts"][edge["rule"]]
        assert scoped["league"] and scoped["odds_band"]
        assert next(iter(scoped["league"].values()))["n"] == 460
    picks = picker.run_day(DAY, {}, None, None)[0]
    for pick in picks:
        assert picker.lookup_context(purity, pick)["league"] != "UNKNOWN"
    monkeypatch.setattr(decay.sys, "argv", ["decay_monitor.py"])
    decay.main()
    after = json.loads(prepared[1].read_text())
    for edge in after["edges"]:
        if edge.get("contract_schema") == cc.SCHEMA:
            assert edge["decay"]["recent"]["n"] == 0  # no validation reuse
            assert edge["decay"]["verdict"] == "WATCH"
    # Add genuine post-activation losses, not validation rows.
    with duckdb.connect(str(prepared[0])) as con:
        frame = pd.DataFrame([observation(END, f"Forward Town {i:03d}", hs=0, gs=0) for i in range(40)])
        con.register("forward", frame)
        con.execute("INSERT INTO scoutingstats SELECT * FROM forward")
    decay.main()
    after = json.loads(prepared[1].read_text())
    assert any(e.get("status") == "benched" for e in after["edges"] if e.get("contract_schema") == cc.SCHEMA)


def test_purity_cannot_inherit_other_contract_or_fuzzy_league():
    pick = dict(contract_schema=cc.SCHEMA, rule="pfc_exact", edge_rule="pfc_exact",
                league="Egypt Premier", home="Alpha Town", away="Bravo Town", market="1x2", pick="home")
    legacy = {"contexts": {"league": {"soccer|egypt premier|1x2|old|home": {"verdict": "BOOST", "n": 999}}}}
    assert picker.lookup_context(legacy, pick)["league"] == "UNKNOWN"
    legacy["contract_contexts"] = {"pfc_other": legacy["contexts"]}
    assert picker.lookup_context(legacy, pick)["league"] == "UNKNOWN"


def test_assay_fail_paths_always_return_five_context_maps():
    with duckdb.connect() as con:
        assert assay.assay_edge(con, {"view": None}, 60) == ({}, {}, {}, {}, {})
        assert assay.assay_edge(con, {"view": "missing"}, 60) == ({}, {}, {}, {}, {})


@pytest.mark.parametrize("market,side,fields,expected", [
    ("1x2", "away", {"odd1": 9, "odd2": 1.7}, 1.7),
    ("ou_1.5", "under", {"odd_u15": 1.7, "odd_o25": 9}, 1.7),
    ("ou_3.5", "over", {"odd_o35": 1.7, "odd_over": 9}, 1.7),
    ("ou_4.5", "under", {"odd_u45": 1.7}, 1.7),
    ("ht_1x2", "away", {"odd2_ht": 1.7, "odd2": 9}, 1.7),
    ("ht_ou_1.5", "under", {"odd_u15_ht": 1.7, "odd_u15": 9}, 1.7),
    ("ht_ou_2.5", "over", {"odd_o25": 9}, None),
    ("btts", "no", {"odd_ng": 1.7, "odd_gg": 9}, 1.7),
])
def test_price_is_never_another_side_line_or_period(market, side, fields, expected):
    assert cc._remine_odds([fields], market, side) == expected


def vote(side, p=.7):
    other = (1-p)/2
    return {"side": side, "probs": {s: p if s == side else other for s in ("home", "draw", "away")}}


def test_majority_dissent_unanimity_missing_and_categorical_predicates():
    votes = {"zulubet": vote("home"), "statarea": vote("home"), "vitibet": vote("away")}
    sources = sorted(votes)
    assert cc.project_votes(votes, sources, "unanimous") is None
    side, p = cc.project_votes(votes, sources, "majority")
    assert side == "home" and p == pytest.approx((.7+.7+.15)/3*100)
    assert cc.project_votes(votes, sources, "disagree_follow", "vitibet") == ("away", 70.)
    assert cc.project_votes(votes, ["statarea", "zulubet"], "unanimous") == ("home", 70.)
    assert cc.project_votes(votes, ["zulubet", "vitibet"], "majority") is None
    assert cc.project_votes(votes, ["zulubet", "prosoccer"], "unanimous") is None
    categorical = {"zulubet": {"side": "home", "probs": None, "row": observation()}}
    observations = {((DAY, "livealpha", "bravounited"), "1x2"): categorical}
    edge = dict(sources=["zulubet"], market="1x2", strategy="single", follow_source=None, threshold=0)
    assert list(cc.contract_rows(observations, set(), {}, edge, settled=False))[0]["avg_p"] is None
    edge["threshold"] = 35
    assert not list(cc.contract_rows(observations, set(), {}, edge, settled=False))


def test_optional_warehouse_timing_and_explicit_line_prices_survive(tmp_path):
    path = tmp_path / "rows.csv.gz"
    with gzip.open(path, "wt") as stream:
        stream.write("home,away,kickoff,odd_o15,result_source\nAlpha,Bravo,2026-10-20T16:00:00Z,1.7,zulubet\n")
    with duckdb.connect() as con:
        _src_view(con, "source", str(path), "home, away")
        assert con.execute("SELECT kickoff, odd_o15, result_source FROM source").fetchone() == ("2026-10-20T16:00:00Z", "1.7", "zulubet")
    # Older schemas without optional fields continue to bind.
    with gzip.open(path, "wt") as stream:
        stream.write("home,away\nAlpha,Bravo\n")
    with duckdb.connect() as con:
        _src_view(con, "source", str(path), "home, away")
        assert con.execute("SELECT * FROM source").fetchone() == ("Alpha", "Bravo")


def test_activation_is_not_backdated_by_historical_as_of(prepared, monkeypatch):
    class Later(date):
        @classmethod
        def today(cls):
            return cls.fromisoformat(DAY)
    monkeypatch.setattr(miner, "date", Later)
    registry = activate(prepared)
    assert all(e["activated_as_of"] == DAY for e in registry["edges"] if e.get("contract_schema") == cc.SCHEMA)
    assert not picker.run_day(END, {}, None, None)[0]


def test_contract_fixture_audit_reconciles_without_legacy_inference(prepared):
    activate(prepared)
    audit_rows = []
    picks, _, n_up, _ = picker.run_day(DAY, {}, None, None, fixture_audit=audit_rows)
    assert len(audit_rows) == n_up == 1
    decision = audit_rows[0]["decision_diagnostics"]
    assert decision["scope"] == cc.SCHEMA
    assert decision["emitted_candidate_count"] == len(picks)
    assert decision["primary_reason"] == "candidate_emitted"
    assert {r["source"] for r in decision["source_votes"]} == set(cc.REMINE_SOURCES)


@pytest.mark.parametrize("market,selection", [
    ("1x2", "home"), ("ht_1x2", "away"), ("btts", "no"),
    ("ou_1.5", "under"), ("ou_2.5", "over"), ("ou_3.5", "under"), ("ou_4.5", "over"),
    ("ht_ou_1.5", "over"), ("ht_ou_2.5", "under"),
])
def test_pricing_indexes_keep_every_market_and_period_separate(market, selection):
    from edgefactory.odds_normalization import canonicalize_row
    row = dict(date=DAY, home="Alpha Town", away="Bravo United", market=market,
               selection=selection, odds=1.7, kickoff=f"{DAY}T16:00:00Z", bookmaker="Pinnacle")
    normalized, reason = canonicalize_row(row)
    assert reason is None and normalized["market"] == market
    bundle = picker._odds_bundle_from_rows([row], provider="test")
    assert len(bundle["exact"]) == 1
    assert next(iter(bundle["exact"]))[-2:] == (market, selection)
    # Another period or goals line must never join this key.
    assert picker._odds_row_key(row | {"market": "1x2" if market != "1x2" else "ht_1x2"}) not in bundle["exact"]


def test_half_time_and_full_time_books_cannot_form_a_mixed_trio():
    rows = [dict(date=DAY, home="Alpha Town", away="Bravo United", provider="test", bookmaker="Pinnacle",
                 market=market, selection=side, odds=odd) for market, side, odd in [
                    ("1x2", "home", 2.5), ("1x2", "draw", 3.5),
                    ("ht_1x2", "away", 2.8), ("ht_1x2", "home", 1.5), ("ht_1x2", "home", 1.6)]]
    kept, refused, _ = picker._gate_one_x_two_rows(rows)
    assert len(kept) == 2 and all(r["market"] == "1x2" for r in kept)
    assert len(refused) == 3 and all(r["market"] == "ht_1x2" for r in refused)


def test_unpriced_forward_wins_cannot_earn_clean_health(prepared, monkeypatch):
    activate(prepared)
    with duckdb.connect(str(prepared[0])) as con:
        frame = pd.DataFrame([observation(END, f"Unpriced Town {i:03d}", hs=4, gs=1,
                                        odd1=None, odd_o15=None, odd_o25=None, odd_o35=None,
                                        odd_gg=None) for i in range(40)])
        con.register("forward", frame)
        con.execute("INSERT INTO scoutingstats SELECT * FROM forward")
    monkeypatch.setattr(decay.sys, "argv", ["decay_monitor.py"])
    decay.main()
    after = json.loads(prepared[1].read_text())
    for edge in after["edges"]:
        if edge.get("contract_schema") == cc.SCHEMA:
            assert edge["decay"]["recent"]["n"] == 40
            assert edge["decay"]["recent"]["n_priced"] == 0
            assert edge["decay"]["verdict"] == "WATCH"
    monkeypatch.setattr(assay.sys, "argv", ["assay_purity.py"])
    assay.main()
    contexts = json.loads(assay.OUT.read_text())["contract_contexts"]
    for scoped in contexts.values():
        # The 40 unpriced tips are neither priced wins nor synthetic losses.
        assert next(iter(scoped["league"].values()))["n"] == 460


@pytest.mark.parametrize("reverse", [False, True])
def test_duplicate_quote_updates_cannot_inflate_roi_by_row_order(reverse):
    rows = [observation("2026-10-01", odd1=1.7, hs=4, gs=1),
            observation("2026-10-01", odd1=9.9, hs=4, gs=1)]
    if reverse:
        rows.reverse()
    with duckdb.connect() as con:
        frame = pd.DataFrame(rows)
        con.register("scoutingstats", frame)
        _, observed, ambiguous, resolved, _ = cc.collect_observations(con, start=START, as_of=END)
        edge = dict(sources=["scoutingstats"], market="1x2", strategy="single", follow_source=None, threshold=65)
        projected = list(cc.contract_rows(observed, ambiguous, resolved, edge))
        assert len(projected) == 1 and projected[0]["pick_odds"] == 1.7
