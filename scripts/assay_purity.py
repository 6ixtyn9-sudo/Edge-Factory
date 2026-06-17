#!/usr/bin/env python3
"""Assay purity: context verdicts per league / team / odds_band.

For every CERTIFIED edge in localdata/edges_consensus.json, compute
context purity verdicts (BOOST / ALLOW / CAUTION / VETO / UNKNOWN)
across three dimensions, write localdata/purity_registry.json

    python3 scripts/assay_purity.py                # all-history recent_roi window
    python3 scripts/assay_purity.py --window 90
    python3 scripts/assay_purity.py --dry-run      # report only, no write

Output schema (purity_registry.json):
{
  "generated_at": "2026-06-13T06:01:00",
  "window_days": 60,
  "contexts": {
    "league": {
      "soccer|Premier League|1x2|3WAY-UNANIMOUS≥65|home": {
        "n": 234, "roi": 0.034, "recent_roi": 0.012, "verdict": "BOOST"
      }
    },
    "team": {
      "soccer|colo_colo|Primera Division|1x2|home": {
        "n": 41, "roi": 0.06, "verdict": "BOOST"
      }
    },
    "odds_band": {
      "soccer|1x2|3WAY-UNANIMOUS≥65|1.20-1.35": {
        "n": 312, "roi": -0.04, "verdict": "BOOST"
      }
    }
  }
}

MUST work with completely empty localdata/: missing warehouse or registry
or zero certified edges -> report and exit 0.
Run order: capture_daily -> build_warehouse -> mine_consensus -> decay_monitor -> assay_purity -> picks_today
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.assay import (  # noqa: E402
    context_verdict_league,
    context_verdict_team,
    context_verdict_odds_band,
)
from edgefactory.entities import canonical_league, canonical_team  # noqa: E402

DB = ROOT / "localdata" / "warehouse.duckdb"
REG = ROOT / "localdata" / "edges_consensus.json"
OUT = ROOT / "localdata" / "purity_registry.json"

# Odds bands – string keys exact, per implementation plan
ODDS_BANDS = [
    (0.0, 1.10, "1.00-1.10"),
    (1.10, 1.20, "1.10-1.20"),
    (1.20, 1.35, "1.20-1.35"),
    (1.35, 1.50, "1.35-1.50"),
    (1.50, 1.75, "1.50-1.75"),
    (1.75, 2.00, "1.75-2.00"),
    (2.00, 2.50, "2.00-2.50"),
    (2.50, 999.0, "2.50+"),
]

def odds_band(odds: float | None) -> str:
    if odds is None:
        return "NO_ODDS"
    for lo, hi, name in ODDS_BANDS:
        if lo <= odds < hi or (lo == 0.0 and odds < hi):
            return name
    return "2.50+"


# ---- warehouse helpers (copied from decay_monitor.py, do not import) ----

def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False


def _get_scale(con, view: str) -> float:
    try:
        max_p = con.sql(f"SELECT max(p1) FROM {view}").fetchone()[0]
        if max_p is not None and float(max_p) > 1.5:
            return 100.0
        return 1.0
    except Exception:
        return 1.0


def recreate_views(con) -> set[str]:
    """Rebuild the TEMP consensus views mine_consensus.py uses.
    Copied from scripts/decay_monitor.py – keep in sync.
    Returns the set of available view names.
    """
    avail: set[str] = set()
    has = {t: _table_exists(con, t) for t in (
        "forebet_settled", "zulubet_settled", "statarea_settled",
        "vitibet_settled", "scoutingstats_settled", "bettingclosed_settled",
        "betclan", "bzzoiro",
    )}
    scales = {t: (_get_scale(con, t) if has[t] else 1.0) for t in has}

    if has["forebet_settled"] and has["zulubet_settled"] and _table_exists(con, "consensus2"):
        try:
            con.execute("CREATE OR REPLACE TEMP VIEW v_consensus2 AS "
                        "SELECT *, fb_pick AS pick FROM consensus2")
            avail.add("v_consensus2")
        except Exception:
            pass

    if (has["forebet_settled"] and has["zulubet_settled"]
            and has["statarea_settled"] and _table_exists(con, "consensus3")):
        try:
            con.execute("CREATE OR REPLACE TEMP VIEW v_consensus3 AS "
                        "SELECT *, fb_pick AS pick FROM consensus3")
            avail.add("v_consensus3")
        except Exception:
            pass

    if has["betclan"] and has["forebet_settled"]:
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW betclan_settled AS
                WITH bc AS (SELECT DISTINCT ON (date, hkey, akey) * FROM betclan),
                     fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                            FROM forebet_settled)
                SELECT bc.*, fb.hs, fb.gs,
                       CASE WHEN bc.p1 >= bc.px AND bc.p1 >= bc.p2 THEN 'home'
                            WHEN bc.p2 >= bc.px THEN 'away' ELSE 'draw' END AS pick,
                       GREATEST(bc.p1, bc.px, bc.p2) AS pmax,
                       CASE WHEN fb.hs > fb.gs THEN 'home' WHEN fb.hs < fb.gs THEN 'away'
                            ELSE 'draw' END AS outcome
                FROM bc JOIN fb USING (date, hkey, akey)
            """)
            scales["betclan_settled"] = scales["betclan"]
            avail.add("betclan_settled")
        except Exception:
            pass

    if has["bzzoiro"] and has["forebet_settled"]:
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW bzzoiro_settled AS
                WITH bz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM bzzoiro),
                     fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                            FROM forebet_settled)
                SELECT bz.*, fb.hs, fb.gs,
                       CASE WHEN bz.p1 >= bz.px AND bz.p1 >= bz.p2 THEN 'home'
                            WHEN bz.p2 >= bz.px THEN 'away' ELSE 'draw' END AS pick,
                       GREATEST(bz.p1, bz.px, bz.p2) AS pmax,
                       CASE WHEN fb.hs > fb.gs THEN 'home' WHEN fb.hs < fb.gs THEN 'away'
                            ELSE 'draw' END AS outcome
                FROM bz JOIN fb USING (date, hkey, akey)
            """)
            scales["bzzoiro_settled"] = scales["bzzoiro"]
            avail.add("bzzoiro_settled")
        except Exception:
            pass

    # consensus4, consensus2_bc, consensus2_bz, consensus_ou, consensus_btts
    # (same as decay_monitor.py – trimmed for brevity, only the views
    # needed to make edge["view"] resolvable are required; the full set
    # is recreated here for completeness)
    if all(has[t] for t in ("forebet_settled", "zulubet_settled",
                            "statarea_settled", "vitibet_settled")):
        sfb, szb = scales["forebet_settled"], scales["zulubet_settled"]
        ssa, svb = scales["statarea_settled"], scales["vitibet_settled"]
        try:
            con.execute(f"""
                CREATE OR REPLACE TEMP VIEW consensus4 AS
                WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                     zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled),
                     sa AS (SELECT DISTINCT ON (date, hkey, akey) * FROM statarea_settled),
                     vb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM vitibet_settled)
                SELECT fb.sport, fb.date, fb.home, fb.away, fb.outcome,
                       fb.pick AS pick, fb.pick AS fb_pick, zb.pick AS zb_pick,
                       sa.pick AS sa_pick, vb.pick AS vb_pick,
                       ((fb.pmax/{sfb} + zb.pmax/{szb} + sa.pmax/{ssa} + vb.pmax/{svb})/4)*100 AS avg_p,
                       CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx
                            ELSE fb.odd2 END AS pick_odds,
                       fb.league
                FROM fb JOIN zb USING (date, hkey, akey)
                        JOIN sa USING (date, hkey, akey)
                        JOIN vb USING (date, hkey, akey)
                WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
            """)
            avail.add("consensus4")
        except Exception:
            pass

    if has["forebet_settled"] and "betclan_settled" in avail:
        sfb, sbc = scales["forebet_settled"], scales["betclan_settled"]
        try:
            con.execute(f"""
                CREATE OR REPLACE TEMP VIEW consensus2_bc AS
                WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                     bc AS (SELECT DISTINCT ON (date, hkey, akey) * FROM betclan_settled)
                SELECT fb.date, fb.outcome,
                       fb.pick AS pick, fb.pick AS fb_pick, bc.pick AS bc_pick,
                       ((fb.pmax/{sfb} + bc.pmax/{sbc})/2)*100 AS avg_p,
                       CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx
                            ELSE fb.odd2 END AS pick_odds
                FROM fb JOIN bc USING (date, hkey, akey)
                WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
            """)
            avail.add("consensus2_bc")
        except Exception:
            pass

    if has["forebet_settled"] and "bzzoiro_settled" in avail:
        sfb, sbz = scales["forebet_settled"], scales["bzzoiro_settled"]
        try:
            con.execute(f"""
                CREATE OR REPLACE TEMP VIEW consensus2_bz AS
                WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                     bz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM bzzoiro_settled)
                SELECT fb.date, fb.outcome,
                       fb.pick AS pick, fb.pick AS fb_pick, bz.pick AS bz_pick,
                       ((fb.pmax/{sfb} + bz.pmax/{sbz})/2)*100 AS avg_p,
                       CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx
                            ELSE fb.odd2 END AS pick_odds
                FROM fb JOIN bz USING (date, hkey, akey)
                WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
            """)
            avail.add("consensus2_bz")
        except Exception:
            pass


    # consensus2_bc_confirm: v_consensus2 confirmed by bettingclosed_settled.
    # Joins on (date, home, away) -- consensus2 does not expose hkey/akey.
    if _table_exists(con, "v_consensus2") and has["bettingclosed_settled"]:
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW consensus2_bc_confirm AS
                WITH c2 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus2),
                     bc AS (SELECT DISTINCT ON (date, home, away)
                                   date, home, away,
                                   CASE pick_1x2
                                     WHEN '1' THEN 'home'
                                     WHEN '2' THEN 'away'
                                     WHEN 'x' THEN 'draw'
                                   END AS bc_pick
                            FROM bettingclosed_settled
                            WHERE pick_1x2 IN ('1','2','x'))
                SELECT c2.*, bc.bc_pick
                FROM c2 JOIN bc USING (date, home, away)
            """)
            avail.add("consensus2_bc_confirm")
        except Exception:
            pass



    # Phase A confirmation views: unused 1x2 sources confirming existing
    # consensus rows. Must mirror mine_consensus.py (L1).
    if _table_exists(con, "predictz_settled"):
        try:
            if _table_exists(con, "v_consensus2"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus2_predictz_confirm AS
                    WITH c2 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus2),
                         pz AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, pick AS pz_pick
                                FROM predictz_settled
                                WHERE pick IN ('home','draw','away'))
                    SELECT c2.*, pz.pz_pick
                    FROM c2 JOIN pz USING (date, home, away)
                """)
                avail.add("consensus2_predictz_confirm")
            if _table_exists(con, "v_consensus3"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus3_predictz_confirm AS
                    WITH c3 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus3),
                         pz AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, pick AS pz_pick
                                FROM predictz_settled
                                WHERE pick IN ('home','draw','away'))
                    SELECT c3.*, pz.pz_pick
                    FROM c3 JOIN pz USING (date, home, away)
                """)
                avail.add("consensus3_predictz_confirm")
        except Exception:
            pass

    if _table_exists(con, "windrawwin") and has.get("forebet_settled"):
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW windrawwin_settled AS
                WITH ww AS (SELECT DISTINCT ON (date, hkey, akey) * FROM windrawwin
                            WHERE pick IN ('home','draw','away')),
                     fb AS (SELECT DISTINCT ON (date, hkey, akey)
                                   date, hkey, akey, hs, gs
                            FROM forebet_settled)
                SELECT ww.*, fb.hs, fb.gs,
                       ww.pick AS ww_pick,
                       CASE WHEN fb.hs > fb.gs THEN 'home'
                            WHEN fb.hs < fb.gs THEN 'away' ELSE 'draw' END AS outcome
                FROM ww JOIN fb USING (date, hkey, akey)
            """)
            avail.add("windrawwin_settled")
            if _table_exists(con, "v_consensus2"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus2_windrawwin_confirm AS
                    WITH c2 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus2),
                         ww AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, ww_pick
                                FROM windrawwin_settled)
                    SELECT c2.*, ww.ww_pick
                    FROM c2 JOIN ww USING (date, home, away)
                """)
                avail.add("consensus2_windrawwin_confirm")
            if _table_exists(con, "v_consensus3"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus3_windrawwin_confirm AS
                    WITH c3 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus3),
                         ww AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, ww_pick
                                FROM windrawwin_settled)
                    SELECT c3.*, ww.ww_pick
                    FROM c3 JOIN ww USING (date, home, away)
                """)
                avail.add("consensus3_windrawwin_confirm")
        except Exception:
            pass

    # OU / BTTS
    if has["forebet_settled"]:
        sfb = scales["forebet_settled"]
        ou_parts, ou_joins, ou_avg = [], "FROM fb", []
        sql = (f"WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) *, "
               f"CASE WHEN p_over/{sfb} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
               f"FROM forebet_settled)")
        ou_avg.append(f"CASE WHEN fb.pick_ou = 'over' THEN fb.p_over/{sfb} "
                      f"ELSE fb.p_under/{sfb} END")
        n_ou = 1
        if has["statarea_settled"]:
            ssa = scales["statarea_settled"]
            sql += (f", sa AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_o25/{ssa} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
                    f"FROM statarea_settled)")
            ou_joins += " JOIN sa USING (date, hkey, akey)"
            ou_avg.append(f"CASE WHEN sa.pick_ou = 'over' THEN sa.p_o25/{ssa} "
                          f"ELSE (1.0 - sa.p_o25/{ssa}) END")
            n_ou += 1
        if has["scoutingstats_settled"]:
            sss = scales["scoutingstats_settled"]
            sql += (f", ss AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_o25/{sss} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
                    f"FROM scoutingstats_settled)")
            ou_joins += " JOIN ss USING (date, hkey, akey)"
            ou_avg.append(f"CASE WHEN ss.pick_ou = 'over' THEN ss.p_o25/{sss} "
                          f"ELSE (1.0 - ss.p_o25/{sss}) END")
            n_ou += 1
        if "bzzoiro_settled" in avail:
            sbz = scales["bzzoiro_settled"]
            sql += (f", bz AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_o25/{sbz} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
                    f"FROM bzzoiro_settled)")
            ou_joins += " JOIN bz USING (date, hkey, akey)"
            ou_avg.append(f"CASE WHEN bz.pick_ou = 'over' THEN bz.p_o25/{sbz} "
                          f"ELSE (1.0 - bz.p_o25/{sbz}) END")
            n_ou += 1
        if n_ou >= 2:
            try:
                con.execute(
                    f"CREATE OR REPLACE TEMP VIEW consensus_ou AS {sql} "
                    f"SELECT fb.date, "
                    f"CASE WHEN fb.hs + fb.gs >= 3 THEN 'over' ELSE 'under' END AS outcome, "
                    f"fb.pick_ou AS pick, "
                    f"CASE fb.pick_ou WHEN 'over' THEN fb.odd_over ELSE fb.odd_under END AS pick_odds "
                    f"{ou_joins}"
                )
                avail.add("consensus_ou")
            except Exception:
                pass

        btts_avg, btts_joins, n_btts = [], "FROM fb", 1
        sql = (f"WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) *, "
               f"CASE WHEN p_gg/{sfb} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts "
               f"FROM forebet_settled)")
        btts_avg.append(f"CASE WHEN fb.pick_btts = 'yes' THEN fb.p_gg/{sfb} "
                        f"ELSE fb.p_ng/{sfb} END")
        if has["scoutingstats_settled"]:
            sss = scales["scoutingstats_settled"]
            sql += (f", ss AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_gg/{sss} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts "
                    f"FROM scoutingstats_settled)")
            btts_joins += " JOIN ss USING (date, hkey, akey)"
            btts_avg.append(f"CASE WHEN ss.pick_btts = 'yes' THEN ss.p_gg/{sss} "
                            f"ELSE (1.0 - ss.p_gg/{sss}) END")
            n_btts += 1
        if "bzzoiro_settled" in avail:
            sbz = scales["bzzoiro_settled"]
            sql += (f", bz AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_gg/{sbz} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts "
                    f"FROM bzzoiro_settled)")
            btts_joins += " JOIN bz USING (date, hkey, akey)"
            btts_avg.append(f"CASE WHEN bz.pick_btts = 'yes' THEN bz.p_gg/{sbz} "
                            f"ELSE (1.0 - bz.p_gg/{sbz}) END")
            n_btts += 1
        if n_btts >= 2:
            try:
                con.execute(
                    f"CREATE OR REPLACE TEMP VIEW consensus_btts AS {sql} "
                    f"SELECT fb.date, "
                    f"CASE WHEN fb.hs > 0 AND fb.gs > 0 THEN 'yes' ELSE 'no' END AS outcome, "
                    f"fb.pick_btts AS pick, "
                    f"CASE fb.pick_btts WHEN 'yes' THEN fb.odd_gg ELSE fb.odd_ng END AS pick_odds "
                    f"{btts_joins}"
                )
                avail.add("consensus_btts")
            except Exception:
                pass

    return avail


def _columns(con, view: str) -> set[str]:
    try:
        rows = con.execute(f"SELECT * FROM {view} LIMIT 0").description
        return {c[0] for c in rows}
    except Exception:
        return set()


def _safe_ident(s: str) -> str:
    # very small allowlist – views are internal, but be defensive
    if not s.replace("_", "").isalnum():
        raise ValueError(f"bad identifier: {s}")
    return s


def assay_edge(con, edge: dict, window_days: int) -> tuple[dict, dict, dict]:
    """Return (league_ctx, team_ctx, odds_band_ctx) dicts for one edge.
    Each maps context_key -> {n, roi, recent_roi?, verdict}
    Never raises – missing columns / query errors → empty dicts.
    """
    view = edge.get("view")
    where = edge.get("where", "1=1")
    market = edge.get("market", "1x2")
    rule = edge.get("rule", "?")
    sport = edge.get("sport", "soccer")

    if not view:
        return {}, {}, {}

    try:
        _safe_ident(view)
        cols = _columns(con, view)
    except Exception:
        return {}, {}, {}

    # required columns
    if not {"pick", "outcome"}.issubset(cols):
        return {}, {}, {}

    has_league = "league" in cols
    has_home = "home" in cols
    has_away = "away" in cols
    has_odds = "pick_odds" in cols
    has_date = "date" in cols

    # recent window cutoff
    recent_cutoff = (date.today() - timedelta(days=window_days)).isoformat() if has_date else "1900-01-01"

    league_ctx: dict = {}
    team_ctx: dict = {}
    odds_ctx: dict = {}

    # ---- league_context: sport|league|market|edge_family|selection_role ----
    if True:  # always try, fall back to UNKNOWN league name
        league_sql_col = "COALESCE(league, 'UNKNOWN')" if has_league else "'UNKNOWN'"
        sql = f"""
            SELECT {league_sql_col} AS league, pick AS sel,
                   COUNT(*) AS n,
                   SUM(CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END) AS pnl,
                   SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) AS n_priced
            FROM {view} WHERE ({where})
            GROUP BY 1,2
        """
        try:
            for league, sel, n, pnl, n_priced in con.execute(sql).fetchall():
                raw_league = league or "UNKNOWN"
                league_key_name = canonical_league(raw_league)
                n = int(n or 0)
                roi = float(pnl) / n_priced if n_priced else None
                # recent roi. With the default max window this is effectively
                # all available history, but explicit --window still works.
                recent_roi = None
                if has_date:
                    try:
                        r = con.execute(f"""
                            SELECT COUNT(*) n,
                                   SUM(CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END) pnl,
                                   SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
                            FROM {view} WHERE ({where}) AND date >= ?
                              AND COALESCE(league,'UNKNOWN') = ? AND pick = ?
                        """, [recent_cutoff, raw_league, sel]).fetchone()
                        rn, rpn, rn_priced = int(r[0] or 0), r[1] or 0, int(r[2] or 0)
                        if rn >= 30 and rn_priced:
                            recent_roi = float(rpn) / rn_priced
                    except Exception:
                        pass
                verdict = context_verdict_league(n, roi, recent_roi)
                key = f"{sport}|{league_key_name}|{market}|{rule}|{sel}"
                league_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None,
                                   "recent_roi": round(recent_roi, 4) if recent_roi is not None else None,
                                   "verdict": verdict, "raw": raw_league}
        except Exception:
            pass

    # ---- team_context: sport|team|league|market|role ----
    if has_home and has_away:
        league_sql = "COALESCE(league, 'UNKNOWN')" if has_league else "'UNKNOWN'"
        # home teams
        try:
            sql = f"""
                SELECT home AS team, {league_sql} AS league, COUNT(*) n,
                       SUM(CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END) pnl,
                       SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
                FROM {view} WHERE ({where})
                GROUP BY home, {league_sql if has_league else '1'}
            """
            for team, league, n, pnl, n_priced in con.execute(sql).fetchall():
                n = int(n or 0)
                roi = float(pnl) / n_priced if n_priced else None
                verdict = context_verdict_team(n, roi)
                key = f"{sport}|{canonical_team(team)}|{canonical_league(league)}|{market}|home"
                team_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None, "verdict": verdict}
        except Exception:
            pass
        # away teams
        try:
            sql = f"""
                SELECT away AS team, {league_sql} AS league, COUNT(*) n,
                       SUM(CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END) pnl,
                       SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
                FROM {view} WHERE ({where})
                GROUP BY away, {league_sql if has_league else '1'}
            """
            for team, league, n, pnl, n_priced in con.execute(sql).fetchall():
                n = int(n or 0)
                roi = float(pnl) / n_priced if n_priced else None
                verdict = context_verdict_team(n, roi)
                key = f"{sport}|{canonical_team(team)}|{canonical_league(league)}|{market}|away"
                team_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None, "verdict": verdict}
        except Exception:
            pass


    # ---- team_context fallback: sport|team|*|market|role ----
    # This pools a team's history across league label variants and competitions.
    # picks_today tries exact league first, then this wildcard fallback.
    if has_home and has_away:
        try:
            sql = f"""
                SELECT home AS team, COUNT(*) n,
                       SUM(CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END) pnl,
                       SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
                FROM {view} WHERE ({where})
                GROUP BY home
            """
            for team, n, pnl, n_priced in con.execute(sql).fetchall():
                n = int(n or 0)
                roi = float(pnl) / n_priced if n_priced else None
                verdict = context_verdict_team(n, roi)
                key = f"{sport}|{canonical_team(team)}|*|{market}|home"
                team_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None,
                                 "verdict": verdict, "scope": "team_any_league"}
        except Exception:
            pass
        try:
            sql = f"""
                SELECT away AS team, COUNT(*) n,
                       SUM(CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END) pnl,
                       SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
                FROM {view} WHERE ({where})
                GROUP BY away
            """
            for team, n, pnl, n_priced in con.execute(sql).fetchall():
                n = int(n or 0)
                roi = float(pnl) / n_priced if n_priced else None
                verdict = context_verdict_team(n, roi)
                key = f"{sport}|{canonical_team(team)}|*|{market}|away"
                team_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None,
                                 "verdict": verdict, "scope": "team_any_league"}
        except Exception:
            pass

    # ---- odds_band_context: sport|market|edge_family|odds_band ----
    if has_odds:
        try:
            rows = con.execute(f"""
                SELECT pick_odds,
                       CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END AS pnl
                FROM {view} WHERE ({where}) AND pick_odds IS NOT NULL
            """).fetchall()
            buckets: dict[str, list[float]] = {}
            for odds, pnl in rows:
                try:
                    b = odds_band(float(odds))
                except Exception:
                    b = "NO_ODDS"
                buckets.setdefault(b, []).append(float(pnl))
            for band, pnls in buckets.items():
                n = len(pnls)
                roi = sum(pnls) / n if n else None
                verdict = context_verdict_odds_band(n, roi)
                key = f"{sport}|{market}|{rule}|{band}"
                odds_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None, "verdict": verdict}
        except Exception:
            pass

    return league_ctx, team_ctx, odds_ctx


def main():
    ap = argparse.ArgumentParser(description="Assay purity: build context verdict registry")
    ap.add_argument("--window", type=int, default=36500, help="recent_roi lookback in days (default: max/all available history)")
    ap.add_argument("--dry-run", action="store_true", help="print verdicts, do not write registry")
    args = ap.parse_args()

    if not REG.exists():
        print("No edges_consensus.json — nothing to assay. Run mine_consensus.py first. Exit 0.")
        return

    try:
        reg = json.loads(REG.read_text())
        edges = reg.get("edges", [])
    except Exception as e:
        print(f"Registry unreadable ({e}) — nothing to assay. Exit 0.")
        return

    certified = [e for e in edges if e.get("status") == "certified"]
    if not certified:
        print("0 certified edges in registry. Nothing to assay. Exit 0.")
        return

    if not DB.exists():
        print(f"{len(certified)} certified edges but no warehouse — cannot assay, exit 0.")
        return

    import duckdb
    con = duckdb.connect(str(DB), read_only=True)
    avail = recreate_views(con)

    # High-density base fallback views to resolve purity context sparsity
    high_density_bases = []
    if "v_consensus2" in avail:
        high_density_bases.append({
            "rule": "v_consensus2_base",
            "view": "v_consensus2",
            "where": "1=1",
            "market": "1x2",
            "sport": "soccer",
        })
    if "v_consensus3" in avail:
        high_density_bases.append({
            "rule": "v_consensus3_base",
            "view": "v_consensus3",
            "where": "1=1",
            "market": "1x2",
            "sport": "soccer",
        })
    if "consensus_ou" in avail:
        high_density_bases.append({
            "rule": "consensus_ou_base",
            "view": "consensus_ou",
            "where": "1=1",
            "market": "ou_2.5",
            "sport": "soccer",
        })
    if "consensus_btts" in avail:
        high_density_bases.append({
            "rule": "consensus_btts_base",
            "view": "consensus_btts",
            "where": "1=1",
            "market": "btts",
            "sport": "soccer",
        })

    league_all: dict = {}
    team_all: dict = {}
    odds_all: dict = {}

    print(f"Purity assay — {len(certified)} certified edges + {len(high_density_bases)} base views, window {args.window}d (max/all-history default)")
    print("-" * 72)
    for e in certified + high_density_bases:
        rule = e.get("rule", "?")
        view = e.get("view", "?")
        if view not in avail:
            # try direct view name (consensus2 / consensus3 live in warehouse, not TEMP)
            try:
                con.execute(f"SELECT 1 FROM {view} LIMIT 0")
            except Exception:
                print(f"{rule:45s}  SKIP – view {view} unavailable")
                continue
        l_ctx, t_ctx, o_ctx = assay_edge(con, e, args.window)
        league_all.update(l_ctx)
        team_all.update(t_ctx)
        odds_all.update(o_ctx)
        print(f"{rule:45s}  league:{len(l_ctx):3d}  team:{len(t_ctx):3d}  odds:{len(o_ctx):3d}")

    # summary counts
    def count_verdicts(d):
        from collections import Counter
        return Counter(v["verdict"] for v in d.values())

    print("\nContext verdict summary:")
    for name, ctx in [("league", league_all), ("team", team_all), ("odds_band", odds_all)]:
        c = count_verdicts(ctx)
        print(f"  {name:10s} total={len(ctx):4d}  " + "  ".join(f"{k}={c.get(k,0)}" for k in ["BOOST","ALLOW","CAUTION","VETO","UNKNOWN"]))

    registry = {
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "window_days": args.window,
        "contexts": {
            "league": league_all,
            "team": team_all,
            "odds_band": odds_all,
        },
    }

    if args.dry_run:
        print("\n--dry-run: registry NOT written.")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(registry, indent=2))
    print(f"\nwrote {OUT}  ({len(league_all)} league, {len(team_all)} team, {len(odds_all)} odds_band contexts)")


if __name__ == "__main__":
    main()
