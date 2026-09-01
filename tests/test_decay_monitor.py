"""Regression tests for the decay monitor's view rebuild graph.

The OU2.5 / BTTS certified edges store their `view` as `consensus_ou_dense`
and `consensus_btts_sparse` (mine_consensus.py). The decay monitor used to
rebuild only the base `consensus_ou`/`consensus_btts` (selected-side) views,
so every OU/BTTS edge fell through to UNKNOWN ("view unavailable or baseline
missing") and had no decay oversight. These tests pin that the dense/sparse
views now rebuild — with the miner's PRIMARY-side avg_p semantics — so the
decay monitor grades exactly the population the walk-forward certified.
"""
from __future__ import annotations

import duckdb

import scripts.decay_monitor as dm


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
