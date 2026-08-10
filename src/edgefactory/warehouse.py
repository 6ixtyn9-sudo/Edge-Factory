"""DuckDB analytics layer.

DuckDB = "SQLite for analytics": a zero-server, single-file (or in-memory)
SQL engine that reads csv.gz/parquet directly and crunches millions of rows
in milliseconds. Supabase stays the system-of-record for edges/picks/live ops;
DuckDB is where ALL mining and backtesting happens.

Usage:
from edgefactory.warehouse import connect
con = connect() # views: forebet, zulubet, statarea, consensus2, consensus3, consensus4
con.sql("SELECT count(*) FROM statarea").show()
"""
from __future__ import annotations

from pathlib import Path

import duckdb

from .util import norm_team_sql

ROOT = Path(__file__).resolve().parent.parent.parent
LOCALDATA = ROOT / "localdata"

def _prob(col: str) -> str:
    """Cast probability column: NaN -> NULL, 0 allowed."""
    return (
        f"CASE WHEN isnan(TRY_CAST({col} AS DOUBLE)) THEN NULL "
        f"ELSE TRY_CAST({col} AS DOUBLE) END"
    )

def _odds(col: str) -> str:
    """Cast odds column: NaN -> NULL, and odds <= 1.0 are junk -> NULL."""
    return (
        f"CASE WHEN isnan(TRY_CAST({col} AS DOUBLE)) "
        f"OR TRY_CAST({col} AS DOUBLE) <= 1.0 THEN NULL "
        f"ELSE TRY_CAST({col} AS DOUBLE) END"
    )

def _src_view(con, name: str, glob: str, select: str) -> None:
    con.execute(
        f"CREATE OR REPLACE VIEW {name} AS SELECT {select} "
        f"FROM read_csv_auto('{glob}', all_varchar=true, union_by_name=true)"
    )

def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False

def connect(db: str | None = None) -> duckdb.DuckDBPyConnection:
    """Open DuckDB (in-memory by default) with all source views + join keys."""
    import glob as _glob
    con = duckdb.connect(db or ":memory:")
    nh, na = norm_team_sql("home"), norm_team_sql("away")
    common = (
        "'soccer' AS sport, "
        f"date, home, away, {nh} AS hkey, {na} AS akey, "
        "TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs, "
        f"{_prob('p1')} AS p1, {_prob('px')} AS px, {_prob('p2')} AS p2"
    )
    if _glob.glob(f"{LOCALDATA}/forebet*.csv.gz"):
        _src_view(
            con, "forebet", f"{LOCALDATA}/forebet*.csv.gz",
            common + f", {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx,"
            f" {_odds('odd2')} AS odd2,"
            " TRY_CAST(ht_hs AS INT) AS ht_hs, TRY_CAST(ht_gs AS INT) AS ht_gs,"
            f" {_prob('p_under')} AS p_under, {_prob('p_over')} AS p_over,"
            f" {_odds('odd_under')} AS odd_under, {_odds('odd_over')} AS odd_over,"
            f" {_prob('p_gg')} AS p_gg, {_prob('p_ng')} AS p_ng,"
            f" {_odds('odd_gg')} AS odd_gg, {_odds('odd_ng')} AS odd_ng,"
            # Addendum (orphaned-data harvest): forebet ships HT probs, Kelly,
            # predicted scores and goalsavg in the same CSV — they were loaded
            # into the raw view but never carried into the settled/consensus
            # layers, so the ML-meta classifier never saw them. Surface them here
            # so the trainer + live feature path can consume them.
            f" {_prob('p1_ht')} AS p1_ht, {_prob('px_ht')} AS px_ht,"
            f" {_prob('p2_ht')} AS p2_ht,"
            f" {_prob('kelly')} AS kelly,"
            " TRY_CAST(pred_hs AS INT) AS pred_hs, TRY_CAST(pred_gs AS INT) AS pred_gs,"
            f" {_prob('goalsavg')} AS goalsavg,"
            " league, status",
        )
    if _glob.glob(f"{LOCALDATA}/zulubet*.csv.gz"):
        _src_view(
            con, "zulubet", f"{LOCALDATA}/zulubet*.csv.gz",
            common + f", {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx,"
            f" {_odds('odd2')} AS odd2, tip, league",
        )
    if _glob.glob(f"{LOCALDATA}/statarea*.csv.gz"):
        _src_view(
            con, "statarea", f"{LOCALDATA}/statarea*.csv.gz",
            common + ", TRY_CAST(ht_hs AS INT) AS ht_hs, TRY_CAST(ht_gs AS INT) AS ht_gs,"
            f" {_prob('p1_ht')} AS p1_ht, {_prob('px_ht')} AS px_ht,"
            f" {_prob('p2_ht')} AS p2_ht,"
            f" {_prob('p_o15')} AS p_o15, {_prob('p_o25')} AS p_o25,"
            f" {_prob('p_o35')} AS p_o35, tip, league",
        )

    # settled-only convenience views with outcome + each model's top pick
    pick = (
        "CASE WHEN p1 >= px AND p1 >= p2 THEN 'home' "
        "WHEN p2 >= px THEN 'away' ELSE 'draw' END"
    )
    outcome = (
        "CASE WHEN hs > gs THEN 'home' WHEN hs < gs THEN 'away' ELSE 'draw' END"
    )
    for v in ("forebet", "zulubet", "statarea"):
        if _table_exists(con, v):
            con.execute(
                f"CREATE OR REPLACE VIEW {v}_settled AS "
                f"SELECT *, {pick} AS pick, GREATEST(p1, px, p2) AS pmax, {outcome} AS outcome "
                f"FROM {v} WHERE hs IS NOT NULL AND gs IS NOT NULL "
                f"AND p1 IS NOT NULL AND px IS NOT NULL AND p2 IS NOT NULL"
            )

    # predictz: categorical picks + odds (no probs). Settled by joining scores
    # from forebet (results donor) on (date, hkey, akey).
    if _glob.glob(f"{LOCALDATA}/predictz_*.csv.gz"):
        _src_view(
            con, "predictz_raw", f"{LOCALDATA}/predictz_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, league, pick, pred_score,"
            f" {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx, {_odds('odd2')} AS odd2",
        )
        # Guard: predictz_settled joins against forebet for results — skip if
        # forebet data is unavailable (e.g. partial cache restore on CI).
        if _table_exists(con, "forebet"):
            con.execute("""
                CREATE OR REPLACE VIEW predictz_settled AS
                WITH pz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM predictz_raw
                            WHERE pick IS NOT NULL),
                     fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                            FROM forebet WHERE hs IS NOT NULL)
                SELECT pz.*, fb.hs, fb.gs,
                       CASE WHEN fb.hs > fb.gs THEN 'home'
                            WHEN fb.hs < fb.gs THEN 'away' ELSE 'draw' END AS outcome,
                       CASE pz.pick WHEN 'home' THEN pz.odd1
                                    WHEN 'draw' THEN pz.oddx ELSE pz.odd2 END AS pick_odds
                FROM pz JOIN fb USING (date, hkey, akey)
                WHERE length(pz.hkey) >= 4 AND length(pz.akey) >= 4
            """)

    if _glob.glob(f"{LOCALDATA}/scoutingstats_*.csv.gz"):
        _src_view(
            con, "scoutingstats", f"{LOCALDATA}/scoutingstats_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, league, country, status,"
            " TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs,"
            f" {_prob('p1')} AS p1, {_prob('px')} AS px, {_prob('p2')} AS p2,"
            f" {_prob('p_o15')} AS p_o15, {_prob('p_o25')} AS p_o25,"
            f" {_prob('p_o35')} AS p_o35, {_prob('p_gg')} AS p_gg, {_prob('p_ng')} AS p_ng,"
            f" {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx, {_odds('odd2')} AS odd2,"
            f" {_odds('odd_o25')} AS odd_o25, {_odds('odd_u25')} AS odd_u25,"
            f" {_odds('odd_gg')} AS odd_gg, {_odds('odd_ng')} AS odd_ng",
        )
        con.execute("""
            CREATE OR REPLACE VIEW scoutingstats_settled AS
            SELECT *,
                   CASE WHEN p1 >= px AND p1 >= p2 THEN 'home'
                        WHEN p2 >= px THEN 'away' ELSE 'draw' END AS pick,
                   GREATEST(p1, px, p2) AS pmax,
                   CASE WHEN hs > gs THEN 'home' WHEN hs < gs THEN 'away'
                        ELSE 'draw' END AS outcome
            FROM scoutingstats
            WHERE hs IS NOT NULL AND p1 IS NOT NULL AND px IS NOT NULL
              AND p2 IS NOT NULL
        """)

    if _glob.glob(f"{LOCALDATA}/bettingclosed_*.csv.gz"):
        _src_view(
            con, "bettingclosed", f"{LOCALDATA}/bettingclosed_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey,"
            " TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs,"
            f" {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx, {_odds('odd2')} AS odd2,"
            f" {_odds('odd_under')} AS odd_under, {_odds('odd_over')} AS odd_over,"
            " lower(pick_1x2) AS pick_1x2,"
            f" {_odds('odd_pick_1x2')} AS odd_pick_1x2,"
            " lower(pick_ou) AS pick_ou,"
            f" {_odds('odd_pick_ou')} AS odd_pick_ou,"
            " lower(pick_btts) AS pick_btts,"
            f" {_odds('odd_pick_btts')} AS odd_pick_btts",
        )
        con.execute("""
            CREATE OR REPLACE VIEW bettingclosed_settled AS
            SELECT *,
                CASE WHEN hs > gs THEN 'home' WHEN hs < gs THEN 'away'
                     ELSE 'draw' END AS outcome,
                -- 1x2 picks incl. double chance: 1, x, 2, 1x, 12, x2
                CASE pick_1x2
                  WHEN '1'  THEN (hs > gs)
                  WHEN '2'  THEN (hs < gs)
                  WHEN 'x'  THEN (hs = gs)
                  WHEN '1x' THEN (hs >= gs)
                  WHEN 'x2' THEN (hs <= gs)
                  WHEN '12' THEN (hs != gs)
                END AS won_1x2,
                CASE
                  WHEN pick_ou LIKE 'over%'  THEN (hs + gs >= 3)
                  WHEN pick_ou LIKE 'under%' THEN (hs + gs <= 2)
                END AS won_ou,
                CASE pick_btts
                  WHEN 'gol'   THEN (hs > 0 AND gs > 0)
                  WHEN 'nogol' THEN (hs = 0 OR gs = 0)
                END AS won_btts
            FROM bettingclosed
            WHERE hs IS NOT NULL AND gs IS NOT NULL
              AND length(hkey) >= 4 AND length(akey) >= 4
        """)

    # ---- additional 6 sources (vitibet, afootballreport, betclan, freesupertips, windrawwin, bzzoiro) ----
    # vitibet: 1x2 probs are % (0-100), convert to 0-1 for consistency
    if _glob.glob(f"{LOCALDATA}/vitibet_*.csv.gz"):
        def _p100(col): return f"TRY_CAST({col} AS DOUBLE)/100.0"
        _src_view(
            con, "vitibet", f"{LOCALDATA}/vitibet_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs, "
            f"{_p100('p1')} AS p1, {_p100('px')} AS px, {_p100('p2')} AS p2, "
            "tip, pred_hs, pred_gs, status, kickoff"
        )
        con.execute(f"""
            CREATE OR REPLACE VIEW vitibet_settled AS
            SELECT *, {pick} AS pick, GREATEST(p1, px, p2) AS pmax, {outcome} AS outcome
            FROM vitibet WHERE hs IS NOT NULL AND gs IS NOT NULL
              AND p1 IS NOT NULL AND px IS NOT NULL AND p2 IS NOT NULL
        """)

    # betclan: 1x2 probs are % (0-100)
    if _glob.glob(f"{LOCALDATA}/betclan_*.csv.gz"):
        def _p100(col): return f"TRY_CAST({col} AS DOUBLE)/100.0"
        _src_view(
            con, "betclan", f"{LOCALDATA}/betclan_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, "
            f"{_p100('p1')} AS p1, {_p100('px')} AS px, {_p100('p2')} AS p2, "
            "winner, match_id, url"
        )

    # bzzoiro: ML model, probs are 0-1, includes xG and OU probs
    if _glob.glob(f"{LOCALDATA}/bzzoiro_*.csv.gz"):
        _src_view(
            con, "bzzoiro", f"{LOCALDATA}/bzzoiro_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, league, event_id, "
            f"{_prob('p1')} AS p1, {_prob('px')} AS px, {_prob('p2')} AS p2, "
            f"{_prob('p_o15')} AS p_o15, {_prob('p_o25')} AS p_o25, {_prob('p_o35')} AS p_o35, "
            f"{_prob('p_gg')} AS p_gg, "
            "TRY_CAST(xg_home AS DOUBLE) AS xg_home, TRY_CAST(xg_away AS DOUBLE) AS xg_away, "
            "predicted, pred_score, rec_bet_favorite, rec_winner, "
            "TRY_CAST(confidence AS DOUBLE) AS confidence, model_version, kickoff, captured_at"
        )

    # freesupertips: tipster picks with odds/confidence, no 1x2 probs
    if _glob.glob(f"{LOCALDATA}/freesupertips_*.csv.gz"):
        _src_view(
            con, "freesupertips", f"{LOCALDATA}/freesupertips_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "tip, " + _odds('odds') + " AS odds, "
            "TRY_CAST(confidence AS INT) AS confidence, stake, kickoff"
        )

    # afootballreport: streak-based OU/BTTS tips, pseudo_prob 0-1
    if _glob.glob(f"{LOCALDATA}/afootballreport_*.csv.gz"):
        _src_view(
            con, "afootballreport", f"{LOCALDATA}/afootballreport_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "market, tip, "
            "TRY_CAST(streak_pct AS INT) AS streak_pct, "
            "TRY_CAST(streak_n AS INT) AS streak_n, "
            f"{_prob('pseudo_prob')} AS pseudo_prob, kickoff"
        )

    # windrawwin: categorical pick + stake confidence
    if _glob.glob(f"{LOCALDATA}/windrawwin_*.csv.gz"):
        _src_view(
            con, "windrawwin", f"{LOCALDATA}/windrawwin_*.csv.gz",
            f"'soccer' AS sport, date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "lower(pick) AS pick, stake, pred_score"
        )

    # 2-way consensus: forebet x zulubet
    if _table_exists(con, "forebet_settled") and _table_exists(con, "zulubet_settled"):
        con.execute("""
            CREATE OR REPLACE VIEW consensus2 AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled)
            SELECT fb.sport, fb.date, fb.home, fb.away, fb.outcome,
                   fb.pick AS fb_pick, zb.pick AS zb_pick,
                   fb.pmax AS fb_p, zb.pmax AS zb_p,
                   (fb.pmax + zb.pmax)/2 AS avg_p,
                   fb.odd1, fb.oddx, fb.odd2,
                   CASE fb.pick WHEN 'home' THEN fb.odd1
                                WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds,
                   fb.league
            FROM fb JOIN zb USING (date, hkey, akey)
            WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
        """)

    # 3-way consensus: + statarea
    if _table_exists(con, "forebet_settled") and _table_exists(con, "zulubet_settled") and _table_exists(con, "statarea_settled"):
        con.execute("""
            CREATE OR REPLACE VIEW consensus3 AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled),
                 sa AS (SELECT DISTINCT ON (date, hkey, akey) * FROM statarea_settled)
            SELECT fb.sport, fb.date, fb.home, fb.away, fb.outcome,
                   fb.pick AS fb_pick, zb.pick AS zb_pick, sa.pick AS sa_pick,
                   fb.pmax AS fb_p, zb.pmax AS zb_p, sa.pmax AS sa_p,
                   (fb.pmax + zb.pmax + sa.pmax)/3 AS avg_p,
                   CASE fb.pick WHEN 'home' THEN fb.odd1
                                WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds,
                   fb.league,
                   -- orphaned-data harvest: HT probs, HT scores, Kelly, predicted
                   -- scores, goalsavg, BTTS-no, under probs (forebet) + HT probs
                   -- (statarea) — surfaced so the ML-meta classifier can use them.
                   fb.ht_hs, fb.ht_gs, fb.p1_ht, fb.px_ht, fb.p2_ht,
                   fb.kelly, fb.pred_hs, fb.pred_gs, fb.goalsavg,
                   fb.p_ng, fb.p_under, fb.p_over,
                   sa.p1_ht AS sa_p1_ht, sa.px_ht AS sa_px_ht, sa.p2_ht AS sa_p2_ht
            FROM fb JOIN zb USING (date, hkey, akey)
                    JOIN sa USING (date, hkey, akey)
            WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
        """)

    # 4-way consensus: + vitibet. Keep context columns on the warehouse view
    # itself so miners/monitors/purity assays do not have to reconstruct them.
    if (_table_exists(con, "forebet_settled") and _table_exists(con, "zulubet_settled")
            and _table_exists(con, "statarea_settled") and _table_exists(con, "vitibet_settled")):
        con.execute("""
            CREATE OR REPLACE VIEW consensus4 AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled),
                 sa AS (SELECT DISTINCT ON (date, hkey, akey) * FROM statarea_settled),
                 vb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM vitibet_settled)
            SELECT fb.sport, fb.date, fb.home, fb.away, fb.outcome,
                   fb.pick AS pick,
                   fb.pick AS fb_pick, zb.pick AS zb_pick, sa.pick AS sa_pick,
                   vb.pick AS vb_pick,
                   fb.pmax AS fb_p, zb.pmax AS zb_p, sa.pmax AS sa_p,
                   vb.pmax AS vb_p,
                   ((CASE WHEN fb.pmax > 1.5 THEN fb.pmax ELSE fb.pmax*100 END)
                    + (CASE WHEN zb.pmax > 1.5 THEN zb.pmax ELSE zb.pmax*100 END)
                    + (CASE WHEN sa.pmax > 1.5 THEN sa.pmax ELSE sa.pmax*100 END)
                    + (CASE WHEN vb.pmax > 1.5 THEN vb.pmax ELSE vb.pmax*100 END))/4 AS avg_p,
                   CASE fb.pick WHEN 'home' THEN fb.odd1
                                WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds,
                   fb.league
            FROM fb JOIN zb USING (date, hkey, akey)
                    JOIN sa USING (date, hkey, akey)
                    JOIN vb USING (date, hkey, akey)
            WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
        """)
    return con
