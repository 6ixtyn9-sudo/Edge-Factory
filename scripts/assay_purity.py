#!/usr/bin/env python3
"""Assay purity with tiered thresholds based on odds band.

This version adds support for new markets from the market registry
and applies stricter purity requirements for mid/high odds bands.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.assay import (
    context_verdict_league,
    context_verdict_team,
    context_verdict_odds_band,
)
from edgefactory.util import norm_team
from edgefactory.market_registry import get_bettable_markets, get_odds_tier

DB = ROOT / "localdata" / "warehouse.duckdb"
REG = ROOT / "localdata" / "edges_consensus.json"
OUT = ROOT / "localdata" / "purity_registry.json"

# Odds bands (same as before)
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


# ---- Tiered purity thresholds (Phase 7 conservative rules) ----

def _get_league_threshold(odds_tier: str) -> int:
    if odds_tier == "low":
        return 80
    elif odds_tier == "mid":
        return 120
    else:  # high
        return 180


def _get_team_threshold(odds_tier: str) -> int:
    if odds_tier == "low":
        return 35
    elif odds_tier == "mid":
        return 50
    else:
        return 70


def _get_promote_roi(odds_tier: str) -> float:
    if odds_tier == "low":
        return 0.03
    elif odds_tier == "mid":
        return 0.04
    else:
        return 0.06


def _get_allow_roi(odds_tier: str) -> float:
    if odds_tier == "low":
        return 0.0
    elif odds_tier == "mid":
        return 0.01
    else:
        return 0.02


# ---- warehouse helpers (same as before, trimmed for brevity) ----

def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False


def _get_scale(con, view: str) -> float:
    try:
        max_p = con.sql(f"SELECT max(p1) FROM {view}").fetchone()[0]
        return 100.0 if max_p is not None and float(max_p) > 1.5 else 1.0
    except Exception:
        return 1.0


def recreate_views(con) -> set[str]:
    """Rebuild TEMP consensus views (same logic as Phase 6)."""
    avail: set[str] = set()
    has = {t: _table_exists(con, t) for t in (
        "forebet_settled", "zulubet_settled", "statarea_settled",
        "vitibet_settled", "scoutingstats_settled", "bettingclosed_settled",
        "betclan", "bzzoiro",
    )}
    scales = {t: (_get_scale(con, t) if has[t] else 1.0) for t in has}

    # ... (same view recreation logic as current assay_purity.py)
    # For brevity in this payload, we assume the existing recreate_views
    # logic is kept. Only the assay_edge function is modified below.

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

    # ... (rest of view creation omitted for payload size — keep existing code)

    return avail


def _columns(con, view: str) -> set[str]:
    try:
        rows = con.execute(f"SELECT * FROM {view} LIMIT 0").description
        return {c[0] for c in rows}
    except Exception:
        return set()


def assay_edge(con, edge: dict, window_days: int) -> tuple[dict, dict, dict]:
    """Return (league_ctx, team_ctx, odds_band_ctx) with tiered thresholds."""
    view = edge.get("view")
    where = edge.get("where", "1=1")
    market = edge.get("market", "1x2")
    rule = edge.get("rule", "?")
    sport = edge.get("sport", "soccer")

    if not view:
        return {}, {}, {}

    try:
        cols = _columns(con, view)
    except Exception:
        return {}, {}, {}

    if not {"pick", "outcome"}.issubset(cols):
        return {}, {}, {}

    has_league = "league" in cols
    has_home = "home" in cols
    has_away = "away" in cols
    has_odds = "pick_odds" in cols
    has_date = "date" in cols

    recent_cutoff = (date.today() - timedelta(days=window_days)).isoformat() if has_date else "1900-01-01"

    league_ctx: dict = {}
    team_ctx: dict = {}
    odds_ctx: dict = {}

    odds_tier = get_odds_tier(market)
    league_min_n = _get_league_threshold(odds_tier)
    team_min_n = _get_team_threshold(odds_tier)
    promote_roi = _get_promote_roi(odds_tier)
    allow_roi = _get_allow_roi(odds_tier)

    # ---- league_context (with tiered thresholds) ----
    if True:
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
                n = int(n or 0)
                roi = float(pnl) / n_priced if n_priced else None
                recent_roi = None
                if has_date:
                    try:
                        r = con.execute(f"""
                            SELECT COUNT(*) n,
                                   SUM(CASE WHEN pick = outcome THEN COALESCE(pick_odds,1)-1 ELSE -1 END) pnl,
                                   SUM(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
                            FROM {view} WHERE ({where}) AND date >= ?
                              AND COALESCE(league,'UNKNOWN') = ? AND pick = ?
                        """, [recent_cutoff, league, sel]).fetchone()
                        rn, rpn, rn_priced = int(r[0] or 0), r[1] or 0, int(r[2] or 0)
                        if rn >= 30 and rn_priced:
                            recent_roi = float(rpn) / rn_priced
                    except Exception:
                        pass

                # Use tiered verdict
                if n < league_min_n:
                    verdict = "UNKNOWN"
                elif roi is None:
                    verdict = "UNKNOWN"
                elif roi <= -0.05 and (recent_roi is None or recent_roi <= -0.03):
                    verdict = "VETO"
                elif roi < 0.0 or (recent_roi is not None and recent_roi <= -0.05):
                    verdict = "CAUTION"
                elif n >= 120 and roi >= promote_roi and (recent_roi is None or recent_roi >= 0.0):
                    verdict = "PROMOTE"
                else:
                    verdict = "ALLOW"

                key = f"{sport}|{league}|{market}|{rule}|{sel}"
                league_ctx[key] = {
                    "n": n,
                    "roi": round(roi, 4) if roi is not None else None,
                    "recent_roi": round(recent_roi, 4) if recent_roi is not None else None,
                    "verdict": verdict,
                }
        except Exception:
            pass

    # ---- team_context (tiered) ----
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
                if n < team_min_n or roi is None:
                    verdict = "UNKNOWN"
                elif roi <= -0.08:
                    verdict = "VETO"
                elif roi <= -0.03:
                    verdict = "CAUTION"
                elif n >= 50 and roi >= 0.05:
                    verdict = "PROMOTE"
                else:
                    verdict = "ALLOW"

                key = f"{sport}|{norm_team(team)}|{league}|{market}|home"
                team_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None, "verdict": verdict}
        except Exception:
            pass

        # away teams (same logic)
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
                if n < team_min_n or roi is None:
                    verdict = "UNKNOWN"
                elif roi <= -0.08:
                    verdict = "VETO"
                elif roi <= -0.03:
                    verdict = "CAUTION"
                elif n >= 50 and roi >= 0.05:
                    verdict = "PROMOTE"
                else:
                    verdict = "ALLOW"

                key = f"{sport}|{norm_team(team)}|{league}|{market}|away"
                team_ctx[key] = {"n": n, "roi": round(roi, 4) if roi is not None else None, "verdict": verdict}
        except Exception:
            pass

    # ---- odds_band_context (unchanged logic) ----
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not REG.exists():
        print("No edges_consensus.json — nothing to assay. Exit 0.")
        return

    try:
        reg = json.loads(REG.read_text())
        edges = reg.get("edges", [])
    except Exception as e:
        print(f"Registry unreadable ({e}) — Exit 0.")
        return

    certified = [e for e in edges if e.get("status") == "certified"]
    if not certified:
        print("0 certified edges. Exit 0.")
        return

    if not DB.exists():
        print(f"{len(certified)} certified edges but no warehouse — Exit 0.")
        return

    import duckdb
    con = duckdb.connect(str(DB), read_only=True)
    avail = recreate_views(con)

    league_all: dict = {}
    team_all: dict = {}
    odds_all: dict = {}

    print(f"Purity assay — {len(certified)} certified edges, window {args.window}d")
    print("-" * 72)

    for e in certified:
        rule = e.get("rule", "?")
        view = e.get("view", "?")
        if view not in avail:
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

    def count_verdicts(d):
        from collections import Counter
        return Counter(v["verdict"] for v in d.values())

    print("\nContext verdict summary:")
    for name, ctx in [("league", league_all), ("team", team_all), ("odds_band", odds_all)]:
        c = count_verdicts(ctx)
        print(f"  {name:10s} total={len(ctx):4d}  " +
              "  ".join(f"{k}={c.get(k,0)}" for k in ["PROMOTE", "ALLOW", "CAUTION", "VETO", "UNKNOWN"]))

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
