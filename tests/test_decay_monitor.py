"""Regression tests for the decay monitor's view rebuild graph.

The OU2.5 / BTTS certified edges store their `view` as `consensus_ou_dense`
and `consensus_btts_sparse` (mine_consensus.py). The decay monitor used to
rebuild only the base `consensus_ou`/`consensus_btts` (selected-side) views,
so every OU/BTTS edge fell through to UNKNOWN ("view unavailable or baseline
missing") and had no decay oversight. These tests pin that the dense/sparse
views now rebuild — with the miner's PRIMARY-side avg_p semantics — so the
decay monitor grades exactly the population the walk-forward certified.

The second half pins the bench rule: a negative ROI only benches when it was
measured over at least GATES.min_recent_n PRICED legs, and the registry records
which evidence the decision used.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

import duckdb

import scripts.decay_monitor as dm
from edgefactory import consensus_contracts as cc


def _make_warehouse(con) -> None:
    con.execute("""
        CREATE TABLE forebet_settled (
            date VARCHAR, hkey VARCHAR, akey VARCHAR,
            home VARCHAR, away VARCHAR, hs INTEGER, gs INTEGER,
            p_over DOUBLE, p_under DOUBLE, p_gg DOUBLE, p_ng DOUBLE,
            odd_over DOUBLE, odd_under DOUBLE, odd_gg DOUBLE, odd_ng DOUBLE
        )
    """)
    con.execute("""
        CREATE TABLE statarea_settled (
            date VARCHAR, hkey VARCHAR, akey VARCHAR, p_o25 DOUBLE
        )
    """)
    con.execute("""
        CREATE TABLE scoutingstats_settled (
            date VARCHAR, hkey VARCHAR, akey VARCHAR, p_gg DOUBLE
        )
    """)
    # OVER fixture (2-1) and UNDER fixture (0-0), both unanimity-eligible.
    con.execute("""
        INSERT INTO forebet_settled VALUES
        ('2026-08-31','uxbridge','wimborne','Uxbridge','Wimborne Town',2,1,
         0.75,0.25,0.70,0.30, 1.80,2.00, 1.90,1.80),
        ('2026-08-31','fortaleza','operario','Fortaleza','Operario PR',0,0,
         0.25,0.75,0.30,0.70, 2.00,1.70, 1.80,1.90)
    """)
    con.execute("""
        INSERT INTO statarea_settled VALUES
        ('2026-08-31','uxbridge','wimborne',0.72),
        ('2026-08-31','fortaleza','operario',0.22)
    """)
    con.execute("""
        INSERT INTO scoutingstats_settled VALUES
        ('2026-08-31','uxbridge','wimborne',0.71),
        ('2026-08-31','fortaleza','operario',0.29)
    """)


def test_recreate_views_builds_ou_dense_and_btts_sparse():
    con = duckdb.connect()
    _make_warehouse(con)
    avail = dm.recreate_views(con)
    assert "consensus_ou_dense" in avail
    assert "consensus_btts_sparse" in avail


def test_ou_dense_view_matches_miner_primary_side_semantics():
    con = duckdb.connect()
    _make_warehouse(con)
    dm.recreate_views(con)

    # avg_p is the OVER probability (miner's definition), so the under fixture
    # must sit BELOW the >=70 threshold even though both sources agree "under".
    rows = con.execute(
        "SELECT pick, avg_p FROM consensus_ou_dense "
        "WHERE fb_pick_ou = sa_pick_ou AND avg_p >= 70 ORDER BY pick"
    ).fetchall()
    assert rows == [("over", 73.5)]

    # The under fixture is present but with primary-side avg_p = 23.5.
    under = con.execute(
        "SELECT pick, avg_p FROM consensus_ou_dense "
        "WHERE home = 'Fortaleza'"
    ).fetchone()
    assert under[0] == "under"
    assert abs(under[1] - 23.5) < 1e-6


def test_btts_sparse_view_primary_side_only():
    con = duckdb.connect()
    _make_warehouse(con)
    dm.recreate_views(con)

    rows = con.execute(
        "SELECT pick, avg_p FROM consensus_btts_sparse "
        "WHERE avg_p >= 70 ORDER BY pick"
    ).fetchall()
    assert rows == [("yes", 70.5)]

    no_side = con.execute(
        "SELECT pick, avg_p FROM consensus_btts_sparse WHERE pick = 'no'"
    ).fetchone()
    assert no_side[0] == "no"
    assert abs(no_side[1] - 29.5) < 1e-6


# ---- bench rule ---------------------------------------------------------
# Regression: on 2026-10-21 the monitor benched pfc_5954379f (baseline 443 legs
# at 70.0%, LB 0.655) on a 9-leg window at -5.3% ROI. Benching is a circuit
# breaker that removes an edge from selection, so it needs a priced sample that
# can carry the claim; the ROI's denominator is n_priced, not the settled count.

def _prepare_registry(tmp_path, monkeypatch, rows: int):
    """A certified contract whose recent window holds `rows` priced losses."""
    db, reg = tmp_path / "warehouse.duckdb", tmp_path / "edges_consensus.json"
    day = (date.today() - timedelta(days=2)).isoformat()
    with duckdb.connect(str(db)) as con:
        con.execute("CREATE TABLE v_test (date VARCHAR, pick VARCHAR, "
                    "outcome VARCHAR, pick_odds DOUBLE)")
        con.executemany("INSERT INTO v_test VALUES (?, 'home', 'away', 1.7)",
                        [(day,)] * rows)
    reg.write_text(json.dumps({"edges": [{
        "rule": "pfc_test_contract", "market": "1x2", "view": "v_test",
        "where": "1=1", "contract_schema": "post_forebet_v1",
        "activated_as_of": (date.today() - timedelta(days=10)).isoformat(),
        "status": "certified",
        "valid": {"n": 443, "wins": 310, "hit": 0.6998, "wilson_lb": 0.655},
    }]}))
    monkeypatch.setattr(dm, "DB", db)
    monkeypatch.setattr(dm, "REG", reg)
    monkeypatch.setattr(dm, "recreate_views", lambda con, **kw: {"v_test"})
    monkeypatch.setattr(cc, "recreate_contract_views", lambda *a, **kw: set())
    monkeypatch.setattr(dm.sys, "argv", ["decay_monitor.py"])
    return db, reg


def test_thin_priced_window_is_reported_not_benched(tmp_path, monkeypatch, capsys):
    db, reg = _prepare_registry(tmp_path, monkeypatch, 9)
    dm.main()
    edge = json.loads(reg.read_text())["edges"][0]
    assert edge["status"] == "certified"            # NOT benched
    assert edge["decay"]["recent"]["n"] == 9
    assert edge["decay"]["recent"]["n_priced"] == 9
    assert edge["decay"]["recent"]["roi"] == -1.0
    assert edge["decay"]["verdict"] == "WATCH"      # n < min_decay_n: no DEAD
    assert edge["decay"]["bench"] is False
    assert edge["decay"]["bench_reason"] == "recent_roi_n_below_floor"
    assert edge["decay"]["bench_min_priced_n"] == 30
    out = capsys.readouterr().out
    assert "9<30: not benched" in out
    assert "1 negative-ROI decision(s) held" in out


def test_sufficient_priced_window_still_benches(tmp_path, monkeypatch):
    db, reg = _prepare_registry(tmp_path, monkeypatch, 30)
    dm.main()
    edge = json.loads(reg.read_text())["edges"][0]
    assert edge["decay"]["recent"]["n_priced"] == 30
    assert edge["decay"]["bench"] is True
    assert edge["decay"]["bench_reason"] == "verdict_dead"
    assert edge["status"] == "benched"


def test_thin_window_can_still_bench_on_structural_decay(tmp_path, monkeypatch):
    """The priced floor gates the ROI branch only; DEAD still benches at n=20."""
    db, reg = _prepare_registry(tmp_path, monkeypatch, 20)
    dm.main()
    edge = json.loads(reg.read_text())["edges"][0]
    assert edge["decay"]["recent"]["n_priced"] == 20
    assert edge["decay"]["bench_reason"] == "verdict_dead"
    assert edge["status"] == "benched"


def test_recent_stats_reports_an_unreadable_roi_as_unavailable():
    con = duckdb.connect()
    con.execute("CREATE TABLE v_nan (date VARCHAR, pick VARCHAR, "
                "outcome VARCHAR, pick_odds DOUBLE)")
    con.execute("INSERT INTO v_nan VALUES ('2026-10-01','home','home','nan'::DOUBLE)")
    rec = dm.recent_stats(con, "v_nan", "1=1", "2026-01-01")
    assert rec["n"] == 1 and rec["n_priced"] == 1
    assert rec["roi"] is None      # NaN is unreadable, not a return


# ---- audit date (--as-of) ----------------------------------------------
# Regression: tests/test_post_forebet_serving.py hard-coded its forward rows on
# 2026-10-19 while the monitor read date.today(); on 2026-11-19 the 30-day
# window started at 2026-10-20 and the suite went red with no code change.
# Every date the audit uses must come from one injectable audit date.

import pytest  # noqa: E402

FIXED = "2026-10-20"


def _registry_on(tmp_path, monkeypatch, rows_by_day, activated="2026-10-10"):
    tmp_path.mkdir(parents=True, exist_ok=True)
    db, reg = tmp_path / "warehouse.duckdb", tmp_path / "edges_consensus.json"
    with duckdb.connect(str(db)) as con:
        con.execute("CREATE TABLE v_test (date VARCHAR, pick VARCHAR, "
                    "outcome VARCHAR, pick_odds DOUBLE)")
        for day, n in rows_by_day.items():
            con.executemany("INSERT INTO v_test VALUES (?, 'home', 'away', 1.7)",
                            [(day,)] * n)
    reg.write_text(json.dumps({"edges": [{
        "rule": "pfc_test_contract", "market": "1x2", "view": "v_test",
        "where": "1=1", "contract_schema": "post_forebet_v1",
        "activated_as_of": activated, "status": "certified",
        "valid": {"n": 443, "wins": 310, "hit": 0.6998, "wilson_lb": 0.655},
    }]}))
    monkeypatch.setattr(dm, "DB", db)
    monkeypatch.setattr(dm, "REG", reg)
    monkeypatch.setattr(dm, "recreate_views", lambda con, **kw: {"v_test"})
    monkeypatch.setattr(cc, "recreate_contract_views", lambda *a, **kw: set())
    return reg


def test_as_of_fixes_the_window_regardless_of_wall_clock(tmp_path, monkeypatch, capsys):
    reg = _registry_on(tmp_path, monkeypatch, {"2026-10-19": 30})
    dm.main(["--as-of", FIXED])
    edge = json.loads(reg.read_text())["edges"][0]
    assert edge["decay"]["recent"]["n"] == 30
    assert edge["decay"]["checked_at"] == FIXED
    assert edge["status"] == "benched" and edge["benched_at"] == FIXED
    out = capsys.readouterr().out
    assert f"Decay audit {FIXED}, window" in out and "REPLAY" in out


def test_as_of_excludes_rows_after_the_audit_date(tmp_path, monkeypatch):
    """A replay must not see results that did not exist on that day."""
    reg = _registry_on(tmp_path, monkeypatch, {"2026-10-19": 5, "2026-10-21": 30})
    dm.main(["--as-of", FIXED])
    edge = json.loads(reg.read_text())["edges"][0]
    assert edge["decay"]["recent"]["n"] == 5
    assert edge["status"] == "certified"


def test_as_of_window_lower_bound_and_activation_floor(tmp_path, monkeypatch):
    # window 30d from 2026-10-20 starts 2026-09-20; activation floor is 10-10.
    reg = _registry_on(tmp_path / "floor", monkeypatch,
                       {"2026-09-19": 7, "2026-10-09": 11, "2026-10-10": 3})
    dm.main(["--as-of", FIXED, "--window", "30"])
    assert json.loads(reg.read_text())["edges"][0]["decay"]["recent"]["n"] == 3
    reg = _registry_on(tmp_path / "window", monkeypatch, {"2026-09-19": 7, "2026-09-20": 2},
                       activated="2026-01-01")
    dm.main(["--as-of", FIXED, "--window", "30"])
    assert json.loads(reg.read_text())["edges"][0]["decay"]["recent"]["n"] == 2


def test_default_audit_date_is_today(tmp_path, monkeypatch, capsys):
    today = date.today()
    reg = _registry_on(tmp_path, monkeypatch,
                       {today.isoformat(): 4, (today - timedelta(days=1)).isoformat(): 2},
                       activated=(today - timedelta(days=5)).isoformat())
    dm.main([])
    edge = json.loads(reg.read_text())["edges"][0]
    assert edge["decay"]["checked_at"] == today.isoformat()
    assert edge["decay"]["recent"]["n"] == 6      # today's settled rows still count
    assert "REPLAY" not in capsys.readouterr().out


@pytest.mark.parametrize("bad", ["2026-13-01", "yesterday", "20261020"])
def test_as_of_rejects_malformed_dates(bad):
    with pytest.raises(SystemExit):
        dm.main(["--as-of", bad])


def test_as_of_rejects_future_dates(tmp_path, monkeypatch):
    reg = _registry_on(tmp_path, monkeypatch, {"2026-10-19": 30})
    before = reg.read_text()
    with pytest.raises(SystemExit):
        dm.main(["--as-of", (date.today() + timedelta(days=1)).isoformat()])
    assert reg.read_text() == before            # nothing written


def test_recent_stats_until_is_inclusive():
    con = duckdb.connect()
    con.execute("CREATE TABLE v (date VARCHAR, pick VARCHAR, outcome VARCHAR, pick_odds DOUBLE)")
    con.execute("INSERT INTO v VALUES ('2026-10-19','h','h',2.0),('2026-10-20','h','h',2.0),"
                "('2026-10-21','h','h',2.0)")
    assert dm.recent_stats(con, "v", "1=1", "2026-10-19", until="2026-10-20")["n"] == 2
    assert dm.recent_stats(con, "v", "1=1", "2026-10-19")["n"] == 3   # legacy: no upper bound
