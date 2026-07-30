#!/usr/bin/env python3
"""picks_today.py with market_type, odds_tier fields, and integrated ML Meta-Classifier (Phase 7)."""

from __future__ import annotations

import csv
import gzip
import os
import importlib
import json
import re
import sys
import math
from collections import Counter
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import canonical_league, canonical_team, classify_competition
from edgefactory.util import char_ngram_similarity, compact_key, norm_team, fold_ascii
from edgefactory.market_registry import get_odds_tier
from edgefactory.assay import weighted_consensus_score

EDGES_PATH = ROOT / "localdata" / "edges_consensus.json"
PURITY_PATH = ROOT / "localdata" / "purity_registry.json"
LOCALDATA = ROOT / "localdata"
BZZOIRO_ODDS_SOURCE = "bzzoiro_odds"
SCOUTINGSTATS_ODDS_SOURCE = "scoutingstats_odds"

# Operational source/odds aliasing stays local to picks_today so certified miners,
# warehouse joins, and historical backtests remain unchanged.
SOURCE_TEAM_KEY_ALIASES = {
    "thunder": "dandenong",   # Forebet: Thunder SC; others: Dandenong Thunder
    "hobartzeb": "clarencez", # some feeds: Hobart Zebras; others: Clarence Zebras
    "neftchi": "neftchife",   # Neftchi -> Neftchi Fergana (Uzbekistan)
    "dila": "dilagori",       # Dila -> Dila Gori (Georgia ECL)
}

ODDS_EXACT_TEAM_ALIASES = {
    "dila": "dilagori",              # Dila -> Dila Gori (Georgia)
    "neftchi": "neftchife",          # Neftchi -> Neftchi Fergana (Uzbekistan)
    "caboverde": "capeverde",
    "drcongo": "congodr",
    "ifkmarieh": "mariehamn",
    "ifkmariehamn": "mariehamn",
    "thunder": "dandenong",
    "hobartzeb": "clarencez",
    "ulsanhyun": "ulsanhd",          # Ulsan Hyundai → Ulsan HD (K League 1)
    "sirius": "iksirius",            # Sirius → IK Sirius (Allsvenskan)
    "kpvj": "kpvkokkol",             # KPV-j → KPV Kokkola (Finland Ykkönen)
    "vestur": "vestursor",           # 07 Vestur → 07 Vestur Sorvag (Faroe Islands)
    "eidsvold": "eidsvoldt",         # Eidsvold → Eidsvold Turn (Norway 2.Div)
    "mlvitebsk": "maxlinero",        # ML Vitebsk → Maxline Rogachev (Belarus PL, renamed club)
    "vitebsk": "fkvitebsk",          # Vitebsk → FK Vitebsk (Belarus PL)
    "ivorycoas": "cotedivoi",        # Ivory Coast → Côte d'Ivoire (World Cup)
    "hodd": "ilhodd",                # Hodd → IL Hodd (Norway 1.Div)
    "naftan": "naftannov",           # Naftan → Naftan Novopolotsk (Belarus PL)
    "lions": "queenslan",            # Lions → Queensland Lions FC (NPL Queensland)
    "belshina": "belshinab",         # Belshina → Belshina Bobruisk (Belarus)
    "thorakure": "thor",             # Thor Akureyri → Thór (Iceland Besta Deildin)
}

ODDS_MATCH_TEAM_ALIASES = {
    "dila": "dilagori",                  # Dila -> Dila Gori (Georgia)
    "caboverde": "capeverde",
    "drcongo": "congodr",
    "ifkmarieh": "mariehamn",
    "ifkmariehamn": "mariehamn",
    "thundersc": "dandenongthunder",
    "hobartzebras": "clarencezebras",
    "hobartzebrasfc": "clarencezebras",
    "ulsanhyundai": "ulsanhd",           # Ulsan Hyundai → Ulsan HD (K League 1)
    "sirius": "iksirius",                # Sirius → IK Sirius (Allsvenskan)
    "kpvj": "kpvkokkola",               # KPV-j → KPV Kokkola (Finland Ykkönen)
    "07vestur": "07vestursorvag",        # 07 Vestur → 07 Vestur Sorvag (Faroe Islands)
    "eidsvold": "eidsvoldturn",          # Eidsvold → Eidsvold Turn (Norway 2.Div)
    "mlvitebsk": "maxlinerogachev",      # ML Vitebsk → Maxline Rogachev (Belarus PL, renamed club)
    "vitebsk": "fkvitebsk",             # Vitebsk → FK Vitebsk (Belarus PL)
    "ivorycoast": "cotedivoire",         # Ivory Coast → Côte d'Ivoire (World Cup)
    "hodd": "ilhodd",                    # Hodd → IL Hodd (Norway 1.Div)
    "naftan": "naftannovopolotsk",       # Naftan → Naftan Novopolotsk (Belarus PL)
    "lions": "queenslandlionsfc",        # Lions → Queensland Lions FC (NPL Queensland)
    "olympic": "olympicfc",              # Olympic → Olympic FC (NPL Queensland)
    "saburtalo": "fcsaburtalo",          # Saburtalo → FC Saburtalo (Georgia)
    "capeverdeislands": "capeverde",     # Cape Verde Islands → Cape Verde (World Cup)
    "dinamominsk": "fcdinamominsk",      # Dinamo Minsk → FC Dinamo Minsk (Belarus PL)
    "belshina": "belshinabobruisk",      # Belshina → Belshina Bobruisk (Belarus)
    "thorakureyri": "thor",              # Thor Akureyri → Thór (Iceland Besta Deildin)
}

DISPLAY_TEAM_ALIASES = {
    "thundersc": "Dandenong Thunder",
    "hobartzebras": "Clarence Zebras",
    "hobartzebrasfc": "Clarence Zebras",
}

OPERATIONAL_CLUB_TOKENS = {
    "fc", "afc", "cf", "sc", "ac", "cd", "ca", "fk", "ifk", "bk", "sk",
    "club",
}
LOW_PRIORITY_BOOKMAKER_TOKENS = ("polymarket", "consensus")

SOURCES_1X2 = ["forebet", "zulubet", "statarea", "vitibet", "betclan", "bzzoiro"]
SOURCES_OU = ["forebet", "statarea", "scoutingstats", "bzzoiro"]
SOURCES_BTTS = ["forebet", "scoutingstats", "bzzoiro"]
ALL_SOURCES = ["forebet", "zulubet", "statarea", "vitibet", "betclan",
               "bzzoiro", "scoutingstats"]

OU_COL = {"forebet": "p_over", "statarea": "p_o25",
          "scoutingstats": "p_o25", "bzzoiro": "p_o25"}
BTTS_COL = {"forebet": "p_gg", "scoutingstats": "p_gg", "bzzoiro": "p_gg"}

FALLBACK_1X2 = {2: 70.0, 3: 65.0}

_RULE_NWAY = re.compile(r"(\d+)\s*way")
_RULE_THR = re.compile(r"avg_p\s*>=?\s*([\d.]+)")
_TIME_RE = re.compile(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)")
DEFAULT_LOCAL_TZ = "Africa/Johannesburg"
DEFAULT_MIN_LEAD_MINUTES = 30


def _local_tz() -> ZoneInfo:
    name = os.environ.get("EDGE_FACTORY_TZ", DEFAULT_LOCAL_TZ).strip() or DEFAULT_LOCAL_TZ
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo(DEFAULT_LOCAL_TZ)


def _parse_as_of(value: object | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=_local_tz())
    return parsed.astimezone(_local_tz())


def pick_run_as_of() -> datetime:
    return _parse_as_of(os.environ.get("EDGE_FACTORY_RUN_AS_OF")) or datetime.now(_local_tz())


def min_lead_minutes() -> int:
    raw = os.environ.get("EDGE_FACTORY_MIN_LEAD_MINUTES", str(DEFAULT_MIN_LEAD_MINUTES))
    try:
        return max(0, int(raw))
    except (TypeError, ValueError):
        return DEFAULT_MIN_LEAD_MINUTES

# ---- purity buckets ----
BUCKET_CERTIFIED = "CERTIFIED_CLEAN"
BUCKET_CAUTION = "CAUTION"
BUCKET_WL_ODDS = "WATCHLIST_NO_ODDS"
BUCKET_WL_CTX = "WATCHLIST_UNKNOWN_CTX"
BUCKET_SKIP_VETO = "SKIPPED_VETO"
BUCKET_SKIP_DEAD = "SKIPPED_DEAD_EDGE"

BUCKET_ORDER = [
    BUCKET_CERTIFIED,
    BUCKET_CAUTION,
    BUCKET_WL_ODDS,
    BUCKET_WL_CTX,
    BUCKET_SKIP_VETO,
    BUCKET_SKIP_DEAD,
]

BUCKET_LABELS = {
    BUCKET_CERTIFIED: "CERTIFIED CLEAN PICKS",
    BUCKET_CAUTION: "CAUTION PICKS",
    BUCKET_WL_ODDS: "WATCHLIST — NO MATCHED ODDS",
    BUCKET_WL_CTX: "WATCHLIST — UNKNOWN CONTEXT",
    BUCKET_SKIP_VETO: "SKIPPED — VETO CONTEXT",
    BUCKET_SKIP_DEAD: "SKIPPED — DEAD EDGE",
}

# Odds bands
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
    try:
        o = float(odds)
    except (TypeError, ValueError):
        return "NO_ODDS"
    for lo, hi, name in ODDS_BANDS:
        if lo <= o < hi or (lo == 0.0 and o < hi):
            return name
    return "2.50+"


# Market Expression Policy Constants (Phase-1)
MARKET_EXPRESSION_VERSION = "phase1-warning-only"
MARKET_EXPRESSION_POLICY = [
    (0.0, 1.20, "keep_1x2", "LOW", "short odds, acceptable draw risk"),
    (1.20, 1.25, "keep_1x2", "MEDIUM", "upper short-odds zone, narrow surviving niche"),
    (1.25, 1.35, "avoid_raw_1x2", "HIGH", "historically unstable out of sample above 1.25"),
    (1.35, 1.50, "avoid_raw_1x2", "HIGH", "draw-risk / medium-odds negative-EV zone"),
    (1.50, 1.75, "avoid_raw_1x2", "EXTREME", "high draw risk and weak signal for raw 1X2"),
    (1.75, 999.0, "avoid_raw_1x2", "EXTREME", "price vs hit-rate math broken for 1X2")
]

SHORT_ODDS_SNIPER_MAX = 1.25
TOXIC_SHORT_ODDS_LEAGUES = {
    "estonia meistriliiga",  # keep config-driven expansion later; conservative starter set
}

# CAUTION odds floor
CAUTION_MIN_ODDS = 1.30


def fetch_historical_profile(con, selection: str, avg_p: float, n_way: int) -> str | None:
    """Dynamically query the local database to generate 100% accurate, non-static realized stats."""
    view_name = "consensus3" if n_way >= 3 else "consensus2"
    try:
        max_p = con.execute(f"SELECT MAX(avg_p) FROM {view_name}").fetchone()[0]
        is_scaled = max_p is not None and float(max_p) > 1.5
    except Exception:
        is_scaled = True
        
    p_val = float(avg_p)
    if not is_scaled and p_val > 1.5:
        p_val /= 100.0
        
    p_min = p_val - (5.0 if is_scaled else 0.05)
    p_max = p_val + (5.0 if is_scaled else 0.05)
    
    sel = str(selection).lower()
    if sel not in ("home", "away", "draw"):
        return None
        
    if view_name == "consensus3":
        agree_cond = "c.fb_pick = ? AND c.zb_pick = ? AND c.sa_pick = ?"
        params = [sel, sel, sel]
    else:
        agree_cond = "c.fb_pick = ? AND c.zb_pick = ?"
        params = [sel, sel]
        
    q = f"""
        SELECT 
            COUNT(*) AS n,
            AVG(f.hs + f.gs) AS avg_total_goals,
            AVG(CASE WHEN f.hs + f.gs >= 3 THEN 1.0 ELSE 0.0 END) AS over25_rate,
            AVG(CASE WHEN f.hs > 0 AND f.gs > 0 THEN 1.0 ELSE 0.0 END) AS btts_rate,
            AVG(CASE WHEN f.hs >= 2 THEN 1.0 ELSE 0.0 END) AS home_o15_rate,
            AVG(CASE WHEN f.gs >= 2 THEN 1.0 ELSE 0.0 END) AS away_o15_rate
        FROM {view_name} c
        JOIN forebet_settled f ON c.date = f.date AND c.home = f.home AND c.away = f.away
        WHERE c.outcome = ? AND {agree_cond}
          AND c.avg_p BETWEEN ? AND ?
    """
    try:
        row = con.execute(q, [sel, *params, p_min, p_max]).fetchone()
        if not row or not row[0] or row[0] < 5:
            return None
            
        n, avg_goals, over25, btts, home_o15, away_o15 = row
        
        # Extract top 2 scorelines
        score_q = f"""
            SELECT f.hs || '-' || f.gs AS scoreline, COUNT(*) as cnt
            FROM {view_name} c
            JOIN forebet_settled f ON c.date = f.date AND c.home = f.home AND c.away = f.away
            WHERE c.outcome = ? AND {agree_cond}
              AND c.avg_p BETWEEN ? AND ?
            GROUP BY 1
            ORDER BY cnt DESC
            LIMIT 2
        """
        score_rows = con.execute(score_q, [sel, *params, p_min, p_max]).fetchall()
        score_strs = []
        for s, c in score_rows:
            score_strs.append(f"{s} ({c/n:.1%})")
            
        score_display = ", ".join(score_strs) if score_strs else "n/a"
        
        comment = f"📊 Realized Stats on {sel.capitalize()} Win (n={n}): Avg Goals: {avg_goals:.2f} | Over 2.5: {over25:.1%} | BTTS: {btts:.1%} | Home Over 1.5 Goals: {home_o15:.1%} | Away Over 1.5 Goals: {away_o15:.1%} | Top Scores: {score_display}"
        return comment
    except Exception:
        return None


def get_statistical_comment(con, pick: str, avg_p: float, n_way: int) -> str | None:
    if not con:
        return None
    try:
        return fetch_historical_profile(con, pick, avg_p, n_way)
    except Exception:
        return None


AUDIT_ROLLING_PATH = LOCALDATA / "picks_audit_rolling.json"


def load_rolling_audit_hit_rates() -> dict[str, float]:
    try:
        if AUDIT_ROLLING_PATH.exists():
            data = json.loads(AUDIT_ROLLING_PATH.read_text())
            by_enh = data.get("enhancements_audit", {}).get("by_enhancement", {})
            out = {}
            for enh, stats in by_enh.items():
                if stats.get("recommended", 0) >= 5:
                    out[enh] = float(stats.get("hit_rate", 1.0))
            return out
    except Exception:
        pass
    return {}


def compute_dynamic_enhancement(con, pick: dict) -> dict:
    """Query the local database to find deep league & team context and determine the single highest probable enhancement."""
    out = {
        "recommended_enhancement": None,
        "enhancement_probability": 0.0,
        "enhancement_reason": None,
        "enhancement_label": None,
        "event_notes": []
    }
    if not con:
        return out
        
    home = pick.get("home")
    away = pick.get("away")
    if not home or not away:
        return out
        
    hkey = source_team_key(home)
    akey = source_team_key(away)
    
    # 1. Find the league code
    league_code = None
    try:
        row_l = con.execute("""
            SELECT league, COUNT(*) 
            FROM forebet_settled 
            WHERE hkey = ? OR akey = ? 
            GROUP BY 1 
            ORDER BY 2 DESC 
            LIMIT 1
        """, [hkey, akey]).fetchone()
        if row_l:
            league_code = row_l[0]
    except Exception:
        pass
        
    # 2. League stats
    league_stats = {}
    if league_code:
        try:
            row = con.execute("""
                SELECT 
                    COUNT(*) AS n,
                    AVG(hs + gs) AS avg_goals,
                    AVG(CASE WHEN hs + gs >= 2 THEN 1.0 ELSE 0.0 END) AS over15_rate,
                    AVG(CASE WHEN hs + gs >= 3 THEN 1.0 ELSE 0.0 END) AS over25_rate,
                    AVG(CASE WHEN hs + gs <= 3 THEN 1.0 ELSE 0.0 END) AS under35_rate,
                    AVG(CASE WHEN hs > 0 AND gs > 0 THEN 1.0 ELSE 0.0 END) AS btts_rate,
                    AVG(CASE WHEN hs >= 1 THEN 1.0 ELSE 0.0 END) AS home_score_o05,
                    AVG(CASE WHEN gs >= 1 THEN 1.0 ELSE 0.0 END) AS away_score_o05,
                    AVG(CASE WHEN hs >= 2 THEN 1.0 ELSE 0.0 END) AS home_score_o15,
                    AVG(CASE WHEN gs >= 2 THEN 1.0 ELSE 0.0 END) AS away_score_o15,
                    AVG(CASE WHEN hs >= 3 THEN 1.0 ELSE 0.0 END) AS home_score_o25,
                    AVG(CASE WHEN gs >= 3 THEN 1.0 ELSE 0.0 END) AS away_score_o25,
                    AVG(CASE WHEN hs >= 4 THEN 1.0 ELSE 0.0 END) AS home_score_o35,
                    AVG(CASE WHEN gs >= 4 THEN 1.0 ELSE 0.0 END) AS away_score_o35,
                    AVG(CASE WHEN hs >= 5 THEN 1.0 ELSE 0.0 END) AS home_score_o45,
                    AVG(CASE WHEN gs >= 5 THEN 1.0 ELSE 0.0 END) AS away_score_o45,
                    AVG(CASE WHEN hs >= gs THEN 1.0 ELSE 0.0 END) AS home_1x_rate,
                    AVG(CASE WHEN gs >= hs THEN 1.0 ELSE 0.0 END) AS away_x2_rate,
                    AVG(CASE WHEN gs = 0 THEN 1.0 ELSE 0.0 END) AS home_cs_rate,
                    AVG(CASE WHEN hs = 0 THEN 1.0 ELSE 0.0 END) AS away_cs_rate
                FROM forebet_settled
                WHERE league = ?
            """, [league_code]).fetchone()
            if row and row[0] >= 10:
                keys = [
                    "n", "avg_goals", "over15_rate", "over25_rate", "under35_rate", "btts_rate",
                    "home_score_o05", "away_score_o05", "home_score_o15", "away_score_o15",
                    "home_score_o25", "away_score_o25",
                    "home_score_o35", "away_score_o35",
                    "home_score_o45", "away_score_o45",
                    "home_1x_rate", "away_x2_rate", "home_cs_rate", "away_cs_rate"
                ]
                league_stats = dict(zip(keys, row))
        except Exception:
            pass
            
    # 3. Home team stats
    home_stats = {}
    try:
        row = con.execute("""
            SELECT 
                COUNT(*) AS n,
                AVG(hs + gs) AS avg_goals,
                AVG(CASE WHEN hs + gs >= 2 THEN 1.0 ELSE 0.0 END) AS over15_rate,
                AVG(CASE WHEN hs + gs >= 3 THEN 1.0 ELSE 0.0 END) AS over25_rate,
                AVG(CASE WHEN hs + gs <= 3 THEN 1.0 ELSE 0.0 END) AS under35_rate,
                AVG(CASE WHEN hs > 0 AND gs > 0 THEN 1.0 ELSE 0.0 END) AS btts_rate,
                AVG(CASE WHEN hs >= 1 THEN 1.0 ELSE 0.0 END) AS score_o05,
                AVG(CASE WHEN hs >= 2 THEN 1.0 ELSE 0.0 END) AS score_o15,
                AVG(CASE WHEN hs >= 3 THEN 1.0 ELSE 0.0 END) AS score_o25,
                AVG(CASE WHEN hs >= 4 THEN 1.0 ELSE 0.0 END) AS score_o35,
                AVG(CASE WHEN hs >= 5 THEN 1.0 ELSE 0.0 END) AS score_o45,
                AVG(CASE WHEN hs >= gs THEN 1.0 ELSE 0.0 END) AS rate_1x,
                AVG(CASE WHEN gs = 0 THEN 1.0 ELSE 0.0 END) AS cs_rate
            FROM forebet_settled
            WHERE hkey = ?
        """, [hkey]).fetchone()
        if row and row[0] >= 5:
            keys = [
                "n", "avg_goals", "over15_rate", "over25_rate", "under35_rate", "btts_rate",
                "score_o05", "score_o15", "score_o25", "score_o35", "score_o45",
                "rate_1x", "cs_rate"
            ]
            home_stats = dict(zip(keys, row))
    except Exception:
        pass
        
    # 4. Away team stats
    away_stats = {}
    try:
        row = con.execute("""
            SELECT 
                COUNT(*) AS n,
                AVG(hs + gs) AS avg_goals,
                AVG(CASE WHEN hs + gs >= 2 THEN 1.0 ELSE 0.0 END) AS over15_rate,
                AVG(CASE WHEN hs + gs >= 3 THEN 1.0 ELSE 0.0 END) AS over25_rate,
                AVG(CASE WHEN hs + gs <= 3 THEN 1.0 ELSE 0.0 END) AS under35_rate,
                AVG(CASE WHEN hs > 0 AND gs > 0 THEN 1.0 ELSE 0.0 END) AS btts_rate,
                AVG(CASE WHEN gs >= 1 THEN 1.0 ELSE 0.0 END) AS score_o05,
                AVG(CASE WHEN gs >= 2 THEN 1.0 ELSE 0.0 END) AS score_o15,
                AVG(CASE WHEN gs >= 3 THEN 1.0 ELSE 0.0 END) AS score_o25,
                AVG(CASE WHEN gs >= 4 THEN 1.0 ELSE 0.0 END) AS score_o35,
                AVG(CASE WHEN gs >= 5 THEN 1.0 ELSE 0.0 END) AS score_o45,
                AVG(CASE WHEN gs >= hs THEN 1.0 ELSE 0.0 END) AS rate_x2,
                AVG(CASE WHEN hs = 0 THEN 1.0 ELSE 0.0 END) AS cs_rate
            FROM forebet_settled
            WHERE akey = ?
        """, [akey]).fetchone()
        if row and row[0] >= 5:
            keys = [
                "n", "avg_goals", "over15_rate", "over25_rate", "under35_rate", "btts_rate",
                "score_o05", "score_o15", "score_o25", "score_o35", "score_o45",
                "rate_x2", "cs_rate"
            ]
            away_stats = dict(zip(keys, row))
    except Exception:
        pass

    # 5. Gather components with fallbacks
    l_o15 = league_stats.get("over15_rate", 0.75)
    l_o25 = league_stats.get("over25_rate", 0.50)
    l_btts = league_stats.get("btts_rate", 0.52)
    l_h_o05 = league_stats.get("home_score_o05", 0.72)
    l_a_o05 = league_stats.get("away_score_o05", 0.72)
    l_h_o15 = league_stats.get("home_score_o15", 0.45)
    l_a_o15 = league_stats.get("away_score_o15", 0.45)
    l_h_o25 = league_stats.get("home_score_o25", 0.18)
    l_a_o25 = league_stats.get("away_score_o25", 0.18)
    l_h_o35 = league_stats.get("home_score_o35", 0.05)
    l_a_o35 = league_stats.get("away_score_o35", 0.05)
    l_h_o45 = league_stats.get("home_score_o45", 0.01)
    l_a_o45 = league_stats.get("away_score_o45", 0.01)
    l_1x = league_stats.get("home_1x_rate", 0.70)
    l_x2 = league_stats.get("away_x2_rate", 0.70)
    l_h_cs = league_stats.get("home_cs_rate", 0.28)
    l_a_cs = league_stats.get("away_cs_rate", 0.28)
    l_u35 = league_stats.get("under35_rate", 0.70)

    h_o15 = home_stats.get("over15_rate", l_o15)
    h_o25 = home_stats.get("over25_rate", l_o25)
    h_btts = home_stats.get("btts_rate", l_btts)
    h_score_o05 = home_stats.get("score_o05", l_h_o05)
    h_score_o15 = home_stats.get("score_o15", l_h_o15)
    h_score_o25 = home_stats.get("score_o25", l_h_o25)
    h_score_o35 = home_stats.get("score_o35", l_h_o35)
    h_score_o45 = home_stats.get("score_o45", l_h_o45)
    h_1x = home_stats.get("rate_1x", l_1x)
    h_cs = home_stats.get("cs_rate", l_h_cs)
    h_u35 = home_stats.get("under35_rate", l_u35)

    a_o15 = away_stats.get("over15_rate", l_o15)
    a_o25 = away_stats.get("over25_rate", l_o25)
    a_btts = away_stats.get("btts_rate", l_btts)
    a_score_o05 = away_stats.get("score_o05", l_a_o05)
    a_score_o15 = away_stats.get("score_o15", l_a_o15)
    a_score_o25 = away_stats.get("score_o25", l_a_o25)
    a_score_o35 = away_stats.get("score_o35", l_a_o35)
    a_score_o45 = away_stats.get("score_o45", l_a_o45)
    a_x2 = away_stats.get("rate_x2", l_x2)
    a_cs = away_stats.get("cs_rate", l_a_cs)
    a_u35 = away_stats.get("under35_rate", l_u35)

    import math
    def poisson(k, lam):
        try:
            return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)
        except:
            return 0.0

    # Calculate expected goals (lambda)
    lam = 0.4 * league_stats.get("avg_goals", 2.5) + 0.6 * ((home_stats.get("avg_goals", 2.5) + away_stats.get("avg_goals", 2.5)) / 2.0)
    
    p_0 = poisson(0, lam)
    p_1 = poisson(1, lam)
    p_2 = poisson(2, lam)
    p_3 = poisson(3, lam)
    p_4 = poisson(4, lam)
    p_5 = poisson(5, lam)
    p_6 = poisson(6, lam)
    p_7plus = max(0.0, 1.0 - (p_0 + p_1 + p_2 + p_3 + p_4 + p_5 + p_6))

    prob_goal_range_0_1 = p_0 + p_1
    prob_goal_range_2_3 = p_2 + p_3
    prob_goal_range_4_5 = p_4 + p_5
    prob_goal_range_4_6 = p_4 + p_5 + p_6
    prob_goal_range_6_plus = p_6 + p_7plus
    prob_goal_range_7_plus = p_7plus

    prob_exact_0 = p_0
    prob_exact_1 = p_1
    prob_exact_2 = p_2
    prob_exact_3 = p_3
    prob_exact_4 = p_4
    prob_exact_5 = p_5
    
    prob_over_35_poisson = 1.0 - (p_0 + p_1 + p_2 + p_3)
    prob_over_45_poisson = 1.0 - (p_0 + p_1 + p_2 + p_3 + p_4)

    prob_o15 = 0.4 * l_o15 + 0.6 * (h_o15 + a_o15) / 2.0
    prob_o25 = 0.4 * l_o25 + 0.6 * (h_o25 + a_o25) / 2.0
    prob_btts_yes = 0.4 * l_btts + 0.6 * (h_btts + a_btts) / 2.0
    prob_btts_no = 1.0 - prob_btts_yes
    
    prob_u15 = 1.0 - prob_o15
    prob_u25 = 1.0 - prob_o25
    prob_u35 = 0.4 * l_u35 + 0.6 * (h_u35 + a_u35) / 2.0

    pick_sel = str(pick.get("pick") or "").lower()
    
    prob_double_chance = 0.0
    if pick_sel == "home":
        prob_double_chance = 0.4 * l_1x + 0.6 * (h_1x + (1.0 - a_x2)) / 2.0
    elif pick_sel == "away":
        prob_double_chance = 0.4 * l_x2 + 0.6 * (a_x2 + (1.0 - h_1x)) / 2.0
    else:
        prob_double_chance = 0.70

    prob_h_o05 = 0.4 * l_h_o05 + 0.6 * h_score_o05
    prob_h_o15 = 0.4 * l_h_o15 + 0.6 * h_score_o15
    prob_h_o25 = 0.4 * l_h_o25 + 0.6 * h_score_o25
    prob_h_o35 = 0.4 * l_h_o35 + 0.6 * h_score_o35
    prob_h_o45 = 0.4 * l_h_o45 + 0.6 * h_score_o45
    prob_h_u05 = 1.0 - prob_h_o05
    prob_h_u15 = 1.0 - prob_h_o15
    prob_h_u25 = 1.0 - prob_h_o25
    prob_h_u35 = 1.0 - prob_h_o35
    prob_h_u45 = 1.0 - prob_h_o45
    
    prob_a_o05 = 0.4 * l_a_o05 + 0.6 * a_score_o05
    prob_a_o15 = 0.4 * l_a_o15 + 0.6 * a_score_o15
    prob_a_o25 = 0.4 * l_a_o25 + 0.6 * a_score_o25
    prob_a_o35 = 0.4 * l_a_o35 + 0.6 * a_score_o35
    prob_a_o45 = 0.4 * l_a_o45 + 0.6 * a_score_o45
    prob_a_u05 = 1.0 - prob_a_o05
    prob_a_u15 = 1.0 - prob_a_o15
    prob_a_u25 = 1.0 - prob_a_o25
    prob_a_u35 = 1.0 - prob_a_o35
    prob_a_u45 = 1.0 - prob_a_o45

    LINE_THRESHOLDS = {
        "match_over_15": 0.80,
        "match_under_15": 0.80,
        "home_over_05": 0.80,
        "home_over_15": 0.80,
        "home_under_05": 0.80,
        "home_under_15": 0.80,
        "away_over_05": 0.80,
        "away_over_15": 0.80,
        "away_under_05": 0.80,
        "away_under_15": 0.80,
        "double_chance": 0.80,
        "btts_yes": 0.85,
        "btts_no": 0.85,
        "match_over_25": 0.85,
        "match_under_25": 0.85,
        "home_over_25": 0.85,
        "home_under_25": 0.85,
        "away_over_25": 0.85,
        "away_under_25": 0.85,
        "match_under_35": 0.90,
        "home_over_35": 0.90,
        "home_under_35": 0.90,
        "away_over_35": 0.90,
        "away_under_35": 0.90,
        "goal_range_0_1": 0.30,
        "goal_range_2_3": 0.42,
        "goal_range_4_5": 0.25,
        "goal_range_4_6": 0.28,
        "goal_range_6_plus": 0.15,
        "goal_range_7_plus": 0.10,
        "exact_0": 0.10,
        "exact_1": 0.20,
        "exact_2": 0.22,
        "exact_3": 0.22,
        "exact_4": 0.15,
        "exact_5": 0.10,
        "match_over_35": 0.30,
        "match_over_45": 0.18,
    }

    raw_candidates = [
        ("match_over_15", prob_o15, "Match Over 1.5 Goals", f"League Over 1.5 is {l_o15:.1%}, Home Over 1.5 is {h_o15:.1%}, Away Over 1.5 is {a_o15:.1%}"),
        ("match_under_15", prob_u15, "Match Under 1.5 Goals", f"Extremely defensive context: Combined Under 1.5 is {prob_u15:.1%}"),
        ("match_under_25", prob_u25, "Match Under 2.5 Goals", f"Highly defensive context: Combined Under 2.5 is {prob_u25:.1%}"),
        ("match_under_35", prob_u35, "Match Under 3.5 Goals", f"Safe low-scoring expectation: Combined Under 3.5 is {prob_u35:.1%}"),
        ("match_over_25", prob_o25, "Match Over 2.5 Goals", f"League Over 2.5 is {l_o25:.1%}, Home Over 2.5 is {h_o25:.1%}, Away Over 2.5 is {a_o25:.1%}"),
        ("btts_yes", prob_btts_yes, "Both Teams to Score (BTTS)", f"League BTTS is {l_btts:.1%}, Home BTTS is {h_btts:.1%}, Away BTTS is {a_btts:.1%}"),
        ("btts_no", prob_btts_no, "Both Teams to Score - No (BTTS-No)", f"League BTTS is {l_btts:.1%}, Home BTTS is {h_btts:.1%}, Away BTTS is {a_btts:.1%}"),
        ("home_over_05", prob_h_o05, "Home Team Over 0.5 Goals", f"Home scoring rate is {h_score_o05:.1%}"),
        ("home_over_15", prob_h_o15, "Home Team Over 1.5 Goals", f"Home multi-goal rate is {h_score_o15:.1%}"),
        ("home_over_25", prob_h_o25, "Home Team Over 2.5 Goals", f"Home ultra-high goal rate is {h_score_o25:.1%}"),
        ("home_over_35", prob_h_o35, "Home Team Over 3.5 Goals", f"Home extremely high goal rate is {h_score_o35:.1%}"),
        ("home_under_05", prob_h_u05, "Home Team Under 0.5 Goals", f"Combined Under 0.5 is {prob_h_u05:.1%}"),
        ("home_under_15", prob_h_u15, "Home Team Under 1.5 Goals", f"Combined Under 1.5 is {prob_h_u15:.1%}"),
        ("home_under_25", prob_h_u25, "Home Team Under 2.5 Goals", f"Combined Under 2.5 is {prob_h_u25:.1%}"),
        ("home_under_35", prob_h_u35, "Home Team Under 3.5 Goals", f"Combined Under 3.5 is {prob_h_u35:.1%}"),
        ("away_over_05", prob_a_o05, "Away Team Over 0.5 Goals", f"Away scoring rate is {a_score_o05:.1%}"),
        ("away_over_15", prob_a_o15, "Away Team Over 1.5 Goals", f"Away multi-goal rate is {a_score_o15:.1%}"),
        ("away_over_25", prob_a_o25, "Away Team Over 2.5 Goals", f"Away ultra-high goal rate is {a_score_o25:.1%}"),
        ("away_over_35", prob_a_o35, "Away Team Over 3.5 Goals", f"Away extremely high goal rate is {a_score_o35:.1%}"),
        ("away_under_05", prob_a_u05, "Away Team Under 0.5 Goals", f"Combined Under 0.5 is {prob_a_u05:.1%}"),
        ("away_under_15", prob_a_u15, "Away Team Under 1.5 Goals", f"Combined Under 1.5 is {prob_a_u15:.1%}"),
        ("away_under_25", prob_a_u25, "Away Team Under 2.5 Goals", f"Combined Under 2.5 is {prob_a_u25:.1%}"),
        ("away_under_35", prob_a_u35, "Away Team Under 3.5 Goals", f"Combined Under 3.5 is {prob_a_u35:.1%}"),
        ("goal_range_0_1", prob_goal_range_0_1, "Goal Range 0-1", f"Poisson expected hit rate is {prob_goal_range_0_1:.1%}"),
        ("goal_range_2_3", prob_goal_range_2_3, "Goal Range 2-3", f"Poisson expected hit rate is {prob_goal_range_2_3:.1%}"),
        ("goal_range_4_5", prob_goal_range_4_5, "Goal Range 4-5", f"Poisson expected hit rate is {prob_goal_range_4_5:.1%}"),
        ("goal_range_4_6", prob_goal_range_4_6, "Goal Range 4-6", f"Poisson expected hit rate is {prob_goal_range_4_6:.1%}"),
        ("goal_range_6_plus", prob_goal_range_6_plus, "Goal Range 6+", f"Poisson expected hit rate is {prob_goal_range_6_plus:.1%}"),
        ("goal_range_7_plus", prob_goal_range_7_plus, "Goal Range 7+", f"Poisson expected hit rate is {prob_goal_range_7_plus:.1%}"),
        ("exact_0", prob_exact_0, "Exact Goals: 0", f"Poisson expected hit rate is {prob_exact_0:.1%}"),
        ("exact_1", prob_exact_1, "Exact Goals: 1", f"Poisson expected hit rate is {prob_exact_1:.1%}"),
        ("exact_2", prob_exact_2, "Exact Goals: 2", f"Poisson expected hit rate is {prob_exact_2:.1%}"),
        ("exact_3", prob_exact_3, "Exact Goals: 3", f"Poisson expected hit rate is {prob_exact_3:.1%}"),
        ("exact_4", prob_exact_4, "Exact Goals: 4", f"Poisson expected hit rate is {prob_exact_4:.1%}"),
        ("exact_5", prob_exact_5, "Exact Goals: 5", f"Poisson expected hit rate is {prob_exact_5:.1%}"),
        ("match_over_35", prob_over_35_poisson, "Match Over 3.5 Goals", f"Poisson expected hit rate is {prob_over_35_poisson:.1%}"),
        ("match_over_45", prob_over_45_poisson, "Match Over 4.5 Goals", f"Poisson expected hit rate is {prob_over_45_poisson:.1%}"),
    ]
    
    dc_label = "1X" if pick_sel == "home" else "X2" if pick_sel == "away" else "12"
    raw_candidates.append(
        ("double_chance", prob_double_chance, f"Double Chance {dc_label}", f"Combined double-chance expectation is {prob_double_chance:.1%}")
    )

    rolling_hit_rates = load_rolling_audit_hit_rates()
    candidates = []
    
    for market, prob, label, reason in raw_candidates:
        hr = rolling_hit_rates.get(market, 1.0)
        prob_adjusted = prob * hr
        
        thr = LINE_THRESHOLDS.get(market, 0.80)
        if prob_adjusted >= thr:
            candidates.append({
                "market": market,
                "probability": prob_adjusted,
                "raw_probability": prob,
                "label": label,
                "reason": reason + (f" (Performance feedback: HR={hr:.1%}, Adjusted Prob: {prob_adjusted:.1%})" if hr < 1.0 else "")
            })

    if candidates:
        # Sort by expected EV to surface lucrative picks first.
        # This maps markets to typical estimated odds to ensure juicy bets win when viable
        EST_ODDS = {
            "goal_range_0_1": 3.50,
            "goal_range_2_3": 2.05,
            "goal_range_4_5": 4.50,
            "goal_range_4_6": 3.00,
            "goal_range_6_plus": 8.00,
            "goal_range_7_plus": 12.00,
            "exact_0": 9.00,
            "exact_1": 4.50,
            "exact_2": 3.60,
            "exact_3": 4.00,
            "exact_4": 5.50,
            "exact_5": 8.00,
            "match_over_25": 1.85,
            "match_over_35": 3.00,
            "match_over_45": 5.00,
            "btts_yes": 1.75
        }
        
        # Rank by probability * estimated odds (value proxy)
        # Apply a 1.2x multiplier to juicy markets so they successfully outrank 1.05 safety odds when viable.
        candidates.sort(key=lambda x: -(x["probability"] * EST_ODDS.get(x["market"], 1.05) * (1.2 if x["market"] in EST_ODDS else 1.0)))
        out["event_notes"] = candidates
        best = candidates[0]
        out.update({
            "recommended_enhancement": best["market"],
            "enhancement_probability": round(best["probability"], 4),
            "enhancement_reason": best["reason"],
            "enhancement_label": best["label"]
        })
        
    return out



def annotate_market_recommendation(pick: dict):
    """Add Phase-1 market expression guidance to 1X2 picks."""
    pick["market_expression_version"] = MARKET_EXPRESSION_VERSION
    if pick.get("market", "") != "1x2":
        return

    odds = pick.get("odds")
    if odds is None:
        pick["recommended_market"] = "unknown"
        pick["draw_risk_flag"] = "UNKNOWN"
        pick["market_recommendation_reason"] = "no odds available"
        return

    for lo, hi, rec, risk, reason in MARKET_EXPRESSION_POLICY:
        if lo <= odds < hi or (lo == 0.0 and odds < hi):
            pick["recommended_market"] = rec
            pick["draw_risk_flag"] = risk
            pick["market_recommendation_reason"] = reason
            break


# ---------------------------------------------------------------- registry --
def display_rule(market: str, n_way: int, threshold: float) -> str:
    """Short human label; edge_rule remains the exact miner rule for lookups."""
    if "ml-meta" in market or n_way == 0:
        return f"ML-META≥{threshold:.0f}"
    if market == "1x2":
        return f"{n_way}WAY-UNANIMOUS≥{threshold:.0f}"
    if market == "ou_2.5":
        return f"OU25-UNANIMOUS-{n_way}WAY≥{threshold:.0f}"
    if market == "btts":
        return f"BTTS-UNANIMOUS-{n_way}WAY≥{threshold:.0f}"
    return f"{market.upper()}-{n_way}WAY≥{threshold:.0f}"


def _edge_entry(edge: dict) -> dict | None:
    rule = edge.get("rule", "")
    market = edge.get("market", "1x2")
    mn, mt = _RULE_NWAY.search(rule), _RULE_THR.search(rule)
    if not mn or not mt:
        if "ml-meta" in rule:
            mt = _RULE_THR.search(rule)
            if mt:
                threshold = float(mt.group(1))
                return {
                    "n_way": 3,
                    "threshold": threshold,
                    "rule": rule,
                    "display_rule": f"ML-META≥{threshold:.0f}",
                    "market": market,
                }
        return None
    n_way, threshold = int(mn.group(1)), float(mt.group(1))
    return {
        "n_way": n_way,
        "threshold": threshold,
        "rule": rule,
        "display_rule": display_rule(market, n_way, threshold),
        "market": market,
    }


_QUALIFIED_TOKENS = ("min_p", "home-only", "away-only", "odds-", "bc-confirms", "predictz-confirms", "windrawwin-confirms", "freesupertips-confirms")

def _is_qualified(rule: str) -> bool:
    r = rule.lower()
    return any(tok in r for tok in _QUALIFIED_TOKENS)


def _prefer_entry(new: dict, old: dict | None) -> bool:
    if old is None:
        return True
    new_qual = _is_qualified(new["rule"])
    old_qual = _is_qualified(old["rule"])
    if new_qual != old_qual:
        return old_qual
    if new["threshold"] != old["threshold"]:
        return new["threshold"] < old["threshold"]
    new_rule, old_rule = new["rule"].lower(), old["rule"].lower()
    new_penalty = ("no-draw" in new_rule, len(new_rule))
    old_penalty = ("no-draw" in old_rule, len(old_rule))
    return new_penalty < old_penalty


def load_thresholds():
    edges = []
    try:
        data = json.loads(EDGES_PATH.read_text())
        edges = [e for e in data.get("edges", [])
                 if e.get("status") == "certified"]
    except (OSError, json.JSONDecodeError, AttributeError):
        edges = []

    if not edges:
        return {
            k: {
                "n_way": k,
                "threshold": v,
                "rule": display_rule("1x2", k, v),
                "display_rule": display_rule("1x2", k, v),
                "market": "1x2",
            }
            for k, v in FALLBACK_1X2.items()
        }, None, None, True

    t1x2: dict[int, dict] = {}
    ou_best = btts_best = None
    for e in edges:
        entry = _edge_entry(e)
        if entry is None:
            continue
        market = entry["market"]
        n_way = entry["n_way"]
        if market == "1x2":
            if _prefer_entry(entry, t1x2.get(n_way)):
                t1x2[n_way] = entry
        elif market == "ou_2.5":
            if _prefer_entry(entry, ou_best):
                ou_best = entry
        elif market == "btts":
            if _prefer_entry(entry, btts_best):
                btts_best = entry

    if not t1x2:
        t1x2 = {
            k: {
                "n_way": k,
                "threshold": v,
                "rule": display_rule("1x2", k, v),
                "display_rule": display_rule("1x2", k, v),
                "market": "1x2",
            }
            for k, v in FALLBACK_1X2.items()
        }
    return t1x2, ou_best, btts_best, not bool(edges)


def load_ml_rules_and_model() -> tuple[list[dict], dict | None]:
    try:
        data = json.loads(EDGES_PATH.read_text())
        edges = data.get("edges", [])
        rules = [e for e in edges if e.get("status") == "certified" and "ml-meta" in e.get("rule", "")]
        model = data.get("ml_model")
        return rules, model
    except Exception:
        return [], None


def get_rolling_hit_rate_last_14d(target_date_str: str) -> float:
    try:
        import duckdb
        con = duckdb.connect(str(LOCALDATA / "warehouse.duckdb"), read_only=True)
        q = f"""
            SELECT COUNT(*) AS n,
                   SUM(CASE WHEN fb_pick = outcome THEN 1 ELSE 0 END) AS wins
            FROM consensus3
            WHERE date >= CAST('{target_date_str}' AS DATE) - INTERVAL 14 DAY
              AND date < '{target_date_str}'
              AND outcome IS NOT NULL
        """
        row = con.execute(q).fetchone()
        con.close()
        if row and row[0] and row[0] > 0:
            return float(row[1] / row[0])
    except Exception:
        pass
    return 0.75


def load_edge_meta():
    """Return edge metadata keyed by exact miner rule and display alias."""
    try:
        data = json.loads(EDGES_PATH.read_text())
        out = {}
        for e in data.get("edges", []):
            rule = e.get("rule")
            if not rule:
                continue
            status = e.get("status", "certified")
            decay = e.get("decay", {})
            verdict = decay.get("verdict", "HEALTHY")
            meta = {"status": status, "decay_verdict": verdict}
            out[rule] = meta
            entry = _edge_entry(e)
            if entry:
                out[entry["display_rule"]] = meta
        return out
    except Exception:
        return {}


def thr_for(n_sources: int, t1x2: dict[int, dict]):
    eligible = [k for k in t1x2 if k <= n_sources]
    if not eligible:
        return None
    return t1x2[max(eligible)]


def load_source_weights(market: str = "1x2") -> dict[str, float]:
    try:
        data = json.loads(EDGES_PATH.read_text())
        best_thr = -1.0
        best_weights: dict[str, float] = {}
        for e in data.get("edges", []):
            if not e.get("weighted"):
                continue
            if e.get("market") != market:
                continue
            if e.get("status") != "certified":
                continue
            m = re.search(r">=\s*([\d.]+)", e.get("rule", ""))
            if not m:
                continue
            thr = float(m.group(1))
            if thr > best_thr and e.get("source_weights"):
                best_thr = thr
                best_weights = e["source_weights"]
        return best_weights
    except Exception:
        return {}


# ---------------------------------------------------------------- purity --
def load_purity():
    try:
        return json.loads(PURITY_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _best_ctx(candidates: list[dict | None]) -> tuple[str, dict]:
    best_unknown: dict = {}
    for entry in candidates:
        if not entry:
            continue
        if int(entry.get("n") or 0) > int(best_unknown.get("n") or 0):
            best_unknown = entry
        verdict = entry.get("verdict", "UNKNOWN")
        if verdict != "UNKNOWN":
            return verdict, entry
    return "UNKNOWN", best_unknown


def _scan_best(ctx: dict, *, prefix: str, suffix: str = "") -> dict:
    """Find best context verdict from the purity registry.

    When scanning for a fallback verdict, prefers rule-specific entries over
    generic base views (v_consensus2_base / v_consensus3_base). A rule-specific
    entry for the actual certified edge (e.g. 'ml-meta avg_p>=70') is a much
    better predictor than the base view which includes all confidence levels
    including low-confidence junk.
    """
    # Collect (key, value) pairs so we can distinguish base views from rules
    matched = [(k, v) for k, v in ctx.items() if k.startswith(prefix) and (not suffix or k.endswith(suffix))]
    if not matched:
        return {}

    # Separate into rule-specific entries and base-view entries
    specific = [(k, v) for k, v in matched if "_base" not in k.split("|")[3]]
    base     = [(k, v) for k, v in matched if "_base"     in k.split("|")[3]]

    def pick_best(pool: list[tuple[str, dict]]) -> dict:
        """Pick the non-UNKNOWN entry with highest n, or highest-n UNKNOWN."""
        non_unknown = [v for _, v in pool if v.get("verdict") != "UNKNOWN"]
        pool_vals = non_unknown or [v for _, v in pool]
        return max(pool_vals, key=lambda v: int(v.get("n") or 0)) if pool_vals else {}

    # Prefer specific rule entries first; only fall back to base views when
    # no specific entry exists.
    result = pick_best(specific)
    if result:
        return result
    return pick_best(base)


def lookup_context(purity: dict, pick: dict) -> dict:
    ctx = purity.get("contexts", {}) if purity else {}
    league_ctx = ctx.get("league", {})
    team_ctx = ctx.get("team", {})
    odds_ctx = ctx.get("odds_band", {})
    comp_ctx = ctx.get("competition_type", {})
    niche_ctx = ctx.get("niche", {})

    sport = pick.get("sport", "soccer")
    league_raw = pick.get("league") or "UNKNOWN"
    league = canonical_league(league_raw)

    # Fuzzy fallback: if the canonical league key has no matches in the
    # purity registry, try fuzzy matching against all known league codes.
    # This catches cases like "World UEFA Europa Conference League" ->
    # norm_league -> "world uefa europa conference league" which the
    # registry only knows as "ecl".
    known_league_keys = {
        k.split("|")[1] for k in league_ctx
        if isinstance(k, str) and k.count("|") >= 1
    }
    if league and known_league_keys:
        league_prefix = f"{sport}|{league}|"
        has_exact = any(k.startswith(league_prefix) for k in league_ctx)
        if not has_exact:
            best_key, best_sim = None, 0.0
            for candidate in known_league_keys:
                sim = char_ngram_similarity(league, candidate, n=2)
                if sim >= 0.55 and sim > best_sim:
                    best_key, best_sim = candidate, sim
            if best_key is not None:
                league = best_key

    market = pick.get("market", "1x2")
    rule = pick.get("edge_rule") or pick.get("rule", "?")
    sel = pick.get("pick", "?")

    home = pick.get("home", "")
    away = pick.get("away", "")
    home_norm = canonical_team(home)
    away_norm = canonical_team(away)

    league_key = f"{sport}|{league}|{market}|{rule}|{sel}"
    league_exact = league_ctx.get(league_key)
    league_fallback = _scan_best(
        league_ctx,
        prefix=f"{sport}|{league}|{market}|",
        suffix=f"|{sel}",
    )
    league_v, league_meta = _best_ctx([league_exact, league_fallback])

    team_h_key = f"{sport}|{home_norm}|{league}|{market}|home"
    team_a_key = f"{sport}|{away_norm}|{league}|{market}|away"
    team_h_exact = team_ctx.get(team_h_key)
    team_a_exact = team_ctx.get(team_a_key)
    team_h_any = team_ctx.get(f"{sport}|{home_norm}|*|{market}|home")
    team_a_any = team_ctx.get(f"{sport}|{away_norm}|*|{market}|away")
    team_h_scan = _scan_best(team_ctx, prefix=f"{sport}|{home_norm}|", suffix=f"|{market}|home")
    team_a_scan = _scan_best(team_ctx, prefix=f"{sport}|{away_norm}|", suffix=f"|{market}|away")
    team_h_v, team_h_meta = _best_ctx([team_h_exact, team_h_any, team_h_scan])
    team_a_v, team_a_meta = _best_ctx([team_a_exact, team_a_any, team_a_scan])

    odds = pick.get("odds")
    band = odds_band(odds)
    odds_key = f"{sport}|{market}|{rule}|{band}"
    odds_exact = odds_ctx.get(odds_key)
    odds_fallback = _scan_best(odds_ctx, prefix=f"{sport}|{market}|{rule}|", suffix=f"|{band}")
    odds_v, odds_meta = _best_ctx([odds_exact, odds_fallback])

    side_role = "home" if sel == "home" else "away" if sel == "away" else "other"
    niche_key = f"{sport}|{league}|{market}|{rule}|{band}|{side_role}"
    niche_exact = niche_ctx.get(niche_key)
    niche_fallback = _scan_best(
        niche_ctx,
        prefix=f"{sport}|{league}|{market}|{rule}|",
        suffix=f"|{side_role}",
    )
    niche_v, niche_meta = _best_ctx([niche_exact, niche_fallback])

    comp_type = classify_competition(league_raw)
    comp_key = f"{sport}|{market}|{rule}|{comp_type}"
    comp_exact = comp_ctx.get(comp_key)
    comp_fallback = _scan_best(comp_ctx, prefix=f"{sport}|{market}|", suffix=f"|{comp_type}")
    comp_v, comp_meta = _best_ctx([comp_exact, comp_fallback])

    return {
        "league": league_v,
        "team_h": team_h_v,
        "team_a": team_a_v,
        "odds_band": odds_v,
        "competition_type": comp_v,
        "niche": niche_v,
        "league_raw": league_raw,
        "league_key": league,
        "home_norm": home_norm,
        "away_norm": away_norm,
        "odds_band_name": band,
        "comp_type_name": comp_type,
        "side_role": side_role,
        "_meta": {
            "league": league_meta,
            "team_h": team_h_meta,
            "team_a": team_a_meta,
            "odds_band": odds_meta,
            "competition_type": comp_meta,
            "niche": niche_meta,
        },
        "_keys": {
            "league": league_key,
            "team_h": team_h_key,
            "team_a": team_a_key,
            "odds_band": odds_key,
            "competition_type": comp_key,
            "niche": niche_key,
        }
    }


def bucket_pick(pick: dict, ctx: dict, edge_status: str = "certified",
                decay_verdict: str = "HEALTHY") -> str | None:
    if edge_status == "benched":
        return BUCKET_SKIP_DEAD
    if decay_verdict in ("DEAD", "DECAYING"):
        return BUCKET_SKIP_DEAD

    vals = [ctx.get("league"), ctx.get("team_h"), ctx.get("team_a"), ctx.get("odds_band"), ctx.get("competition_type"), ctx.get("niche")]
    if "VETO" in vals:
        pick["veto_reason"] = f"context VETO in {[k for k, v in zip(['league','team_h','team_a','odds_band','competition_type','niche'], vals) if v == 'VETO']}"
        return BUCKET_SKIP_VETO
    if pick.get("odds") is None:
        return BUCKET_WL_ODDS

    market = str(pick.get("market") or "")
    odds = pick.get("odds")
    sel = str(pick.get("pick") or "")
    league_key = str(ctx.get("league_key") or "")
    short_sniper = market == "1x2" and sel == "home" and odds is not None and float(odds) < SHORT_ODDS_SNIPER_MAX

    if market == "1x2" and sel == "away" and odds is not None and float(odds) < 1.30:
        pick["veto_reason"] = f"short-odds away favourite {float(odds):.2f}"
        return BUCKET_SKIP_VETO
    if short_sniper and league_key in TOXIC_SHORT_ODDS_LEAGUES:
        return BUCKET_SKIP_VETO
    if short_sniper and ctx.get("niche") == "UNKNOWN":
        ultra_short_home_soft_unknown = (
            sel == "home"
            and odds is not None and float(odds) < 1.20
            and ctx.get("odds_band") in ("ALLOW", "BOOST")
            and ctx.get("competition_type") != "VETO"
            and ctx.get("league") != "VETO"
        )
        if not ultra_short_home_soft_unknown:
            return BUCKET_WL_CTX
    if short_sniper and ctx.get("league") == "UNKNOWN":
        ultra_short_home_soft_unknown = (
            sel == "home"
            and odds is not None and float(odds) < 1.20
            and ctx.get("odds_band") in ("ALLOW", "BOOST")
            and ctx.get("competition_type") != "VETO"
        )
        if not ultra_short_home_soft_unknown:
            return BUCKET_WL_CTX

    if ctx.get("odds_band") == "UNKNOWN":
        bucket = BUCKET_CAUTION
    elif "CAUTION" in vals:
        bucket = BUCKET_CAUTION
    else:
        bucket = BUCKET_CERTIFIED

    if bucket == BUCKET_CAUTION and odds is not None and float(odds) < CAUTION_MIN_ODDS:
        return None

    return bucket


# ------------------------------------------------------------------- fetch --
def fetch_all(day: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name in ALL_SOURCES:
        try:
            mod = importlib.import_module(f"edgefactory.sources.{name}")
            rows = mod.fetch_day(day)
        except Exception as e:
            print(f"skip {name}: {e}", file=sys.stderr)
            continue
        by_key = {}
        for r in rows or []:
            home, away = r.get("home"), r.get("away")
            if not home or not away:
                continue
            if r.get("hs") not in (None, ""):
                continue
            if name == "forebet" and r.get("status") == "FT":
                continue
            k = (source_team_key(home), source_team_key(away))
            if len(k[0]) < 4 or len(k[1]) < 4:
                continue
            by_key[k] = r
        out[name] = by_key
    return out


def _f(v):
    try:
        return None if v is None or v == "" else float(v)
    except (TypeError, ValueError):
        return None


def _valid_decimal_odds(v) -> float | None:
    odds = _f(v)
    if odds is None or odds <= 1.0:
        return None
    return odds


def canonical_display_team(name: object) -> str:
    raw = str(name or "").strip()
    if not raw:
        return raw
    return DISPLAY_TEAM_ALIASES.get(compact_key(raw), raw)


def source_team_key(name: object) -> str:
    key = norm_team(str(name or ""))
    return SOURCE_TEAM_KEY_ALIASES.get(key, key)


def char_ngram_similarity(s1: str, s2: str, n: int = 2) -> float:
    def get_ngrams(s: str) -> set[str]:
        clean = re.sub(r"[^a-z0-9]", "", s.lower())
        return {clean[i:i+n] for i in range(len(clean) - n + 1)} if len(clean) >= n else set()
    g1 = get_ngrams(s1)
    g2 = get_ngrams(s2)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)


def odds_team_key(name: object) -> str:
    key = norm_team(fold_ascii(str(name or "")))
    return ODDS_EXACT_TEAM_ALIASES.get(key, key)


def odds_match_team_key(name: object) -> str:
    raw = str(name or "")
    compact = compact_key(raw)
    return ODDS_MATCH_TEAM_ALIASES.get(compact, compact)


def operational_team_key(name: object) -> str:
    tokens = re.findall(r"[a-z0-9]+", fold_ascii(str(name or "")))
    filtered = [t for t in tokens if t not in OPERATIONAL_CLUB_TOKENS]
    compact = "".join(filtered) or compact_key(name)
    return ODDS_MATCH_TEAM_ALIASES.get(compact, compact)


def _kickoff_value(obj: dict) -> str | None:
    for key in ("kickoff", "time"):
        value = obj.get(key)
        if value:
            return str(value)
    return None


def _kickoff_minutes(value: object) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    match = _TIME_RE.search(text)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour > 23 or minute > 59:
        return None
    return hour * 60 + minute


def _kickoff_delta_minutes(a: object, b: object) -> int | None:
    a_min = _kickoff_minutes(a)
    b_min = _kickoff_minutes(b)
    if a_min is None or b_min is None:
        return None
    return abs(a_min - b_min)


def operational_pick_eligibility(
    pick: dict,
    *,
    as_of: datetime,
    min_lead: int,
) -> tuple[bool, str | None]:
    p_date = str(pick.get("date") or "")[:10]
    try:
        pick_date = datetime.strptime(p_date, "%Y-%m-%d").date()
    except ValueError:
        return False, "bad_date"

    as_of_date = as_of.date()
    if pick_date < as_of_date:
        return False, "past_target_date"
    if pick_date > as_of_date:
        return True, None

    kickoff_min = _kickoff_minutes(_kickoff_value(pick))
    if kickoff_min is None:
        return False, "missing_kickoff_same_day"

    as_of_min = as_of.hour * 60 + as_of.minute
    if kickoff_min - as_of_min < min_lead:
        return False, f"inside_{min_lead}m_lead_or_started"
    return True, None


def filter_operational_pre_match_picks(
    picks: list[dict],
    *,
    as_of: datetime,
    min_lead: int,
) -> tuple[list[dict], dict[str, int]]:
    kept: list[dict] = []
    skipped: dict[str, int] = {}
    as_of_text = as_of.isoformat(timespec="seconds")
    for pick in picks:
        ok, reason = operational_pick_eligibility(pick, as_of=as_of, min_lead=min_lead)
        if not ok:
            skipped[reason or "unknown"] = skipped.get(reason or "unknown", 0) + 1
            continue
        pick["as_of"] = as_of_text
        pick["min_lead_minutes"] = min_lead
        kept.append(pick)
    return kept, skipped


def _bookmaker_priority(bookmaker: object) -> int:
    b = str(bookmaker or "").strip().lower()
    if any(token in b for token in LOW_PRIORITY_BOOKMAKER_TOKENS):
        return 0
    return 1


def _odds_row_key(row: dict) -> tuple[str, str, str, str, str] | None:
    day = str(row.get("date") or "")
    home = odds_team_key(row.get("home") or "")
    away = odds_team_key(row.get("away") or "")
    market = str(row.get("market") or "")
    selection = str(row.get("selection") or "")
    if not (day and home and away and market and selection):
        return None
    return (day, home, away, market, selection)


def _time_match_key(row: dict) -> tuple[str, str, str, str, str] | None:
    day = str(row.get("date") or "")
    home = odds_match_team_key(row.get("home") or "")
    away = odds_match_team_key(row.get("away") or "")
    market = str(row.get("market") or "")
    selection = str(row.get("selection") or "")
    if not (day and home and away and market and selection):
        return None
    return (day, home, away, market, selection)


def _time_pick_key(pick: dict) -> tuple[str, str, str, str, str]:
    return (
        str(pick.get("date") or ""),
        odds_match_team_key(pick.get("home") or ""),
        odds_match_team_key(pick.get("away") or ""),
        str(pick.get("market") or ""),
        str(pick.get("pick") or ""),
    )


def _market_pick_key(obj: dict, *, selection_key: str) -> tuple[str, str, str]:
    return (
        str(obj.get("date") or ""),
        str(obj.get("market") or ""),
        str(obj.get(selection_key) or ""),
    )


def _prefer_odds_row(new: dict, old: dict | None) -> bool:
    if old is None:
        return True
    new_priority = _bookmaker_priority(new.get("bookmaker"))
    old_priority = _bookmaker_priority(old.get("bookmaker"))
    if new_priority != old_priority:
        return new_priority > old_priority
    new_odds = _valid_decimal_odds(new.get("odds")) or 0.0
    old_odds = _valid_decimal_odds(old.get("odds")) or 0.0
    if new_odds != old_odds:
        return new_odds > old_odds
    return str(new.get("captured_at") or "") > str(old.get("captured_at") or "")


def _read_cached_bzzoiro_odds(day: str) -> list[dict]:
    month = day[:7]
    path = LOCALDATA / f"{BZZOIRO_ODDS_SOURCE}_{month}.csv.gz"
    if not path.exists():
        return []
    try:
        with gzip.open(path, "rt", newline="") as fh:
            return [r for r in csv.DictReader(fh) if r.get("date") == day]
    except Exception:
        return []


def _read_cached_scoutingstats(day: str) -> list[dict]:
    month = day[:7]
    path = LOCALDATA / f"scoutingstats_{month}.csv.gz"
    if not path.exists():
        return []
    try:
        with gzip.open(path, "rt", newline="") as fh:
            return [
                r for r in csv.DictReader(fh)
                if r.get("date") == day and r.get("hs") in (None, "")
            ]
    except Exception:
        return []


def _scoutingstats_rows_to_odds(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        base = {
            "date": row.get("date"),
            "kickoff": row.get("kickoff") or row.get("time"),
            "league": row.get("league"),
            "home": row.get("home"),
            "away": row.get("away"),
            "captured_at": row.get("kickoff") or row.get("time") or "",
            "bookmaker": SCOUTINGSTATS_ODDS_SOURCE,
        }
        for market, mapping in (
            ("1x2", {"home": "odd1", "draw": "oddx", "away": "odd2"}),
            ("ou_2.5", {"over": "odd_o25", "under": "odd_u25"}),
            ("btts", {"yes": "odd_gg", "no": "odd_ng"}),
        ):
            for selection, col in mapping.items():
                odds = _valid_decimal_odds(row.get(col))
                if odds is None:
                    continue
                out.append({**base, "market": market, "selection": selection, "odds": odds})
    return out


def _fetch_live_bzzoiro_odds(day: str) -> list[dict]:
    try:
        mod = importlib.import_module("edgefactory.sources.bzzoiro_odds")
        return list(mod.fetch_day(day) or [])
    except Exception as exc:
        print(f"bzzoiro_odds enrichment skipped for {day}: {exc}", file=sys.stderr)
        return []


def _refresh_bzzoiro_odds() -> bool:
    return os.environ.get("BZZOIRO_ODDS_REFRESH", "").strip().lower() in {"1", "true", "yes", "on"}


def _odds_bundle_from_rows(rows: list[dict], *, provider: str, stats: dict | None = None) -> dict[str, dict]:
    exact: dict[tuple[str, str, str, str, str], dict] = {}
    time_candidates: dict[tuple[str, str, str, str, str], list[dict]] = {}
    market_candidates: dict[tuple[str, str, str], list[dict]] = {}
    valid_rows = 0
    for row in rows:
        odds = _valid_decimal_odds(row.get("odds"))
        if odds is None:
            continue
        exact_key = _odds_row_key(row)
        time_key = _time_match_key(row)
        if exact_key is None or time_key is None:
            continue
        valid_rows += 1
        normalized = dict(row)
        normalized["odds"] = odds
        normalized.setdefault("provider", provider)
        if _prefer_odds_row(normalized, exact.get(exact_key)):
            exact[exact_key] = normalized
        time_candidates.setdefault(time_key, []).append(normalized)
        market_candidates.setdefault(_market_pick_key(normalized, selection_key="selection"), []).append(normalized)

    for key, candidates in time_candidates.items():
        candidates.sort(
            key=lambda row: (
                _kickoff_minutes(_kickoff_value(row)) is None,
                _kickoff_minutes(_kickoff_value(row)) or 10**9,
                -_bookmaker_priority(row.get("bookmaker")),
                -(row.get("odds") or 0.0),
            )
        )

    for key, candidates in market_candidates.items():
        candidates.sort(
            key=lambda row: (
                _kickoff_minutes(_kickoff_value(row)) is None,
                _kickoff_minutes(_kickoff_value(row)) or 10**9,
                -_bookmaker_priority(row.get("bookmaker")),
                -(row.get("odds") or 0.0),
            )
        )

    if stats is not None:
        stats.update({
            "raw_rows": len(rows),
            "valid_rows": valid_rows,
            "valid_keys": len(exact),
            "time_match_keys": len(time_candidates),
            "market_candidate_keys": len(market_candidates),
        })

    return {
        "provider": provider,
        "exact": exact,
        "time_candidates": time_candidates,
        "market_candidates": market_candidates,
        "raw_rows_list": list(exact.values()),
    }


def bzzoiro_odds_bundle(
    day: str,
    *,
    live: bool = True,
    stats: dict | None = None,
) -> dict[str, dict]:
    cached_rows = _read_cached_bzzoiro_odds(day)
    live_rows: list[dict] = []
    if live and (_refresh_bzzoiro_odds() or not cached_rows):
        live_rows = _fetch_live_bzzoiro_odds(day)

    bundle = _odds_bundle_from_rows(cached_rows + live_rows, provider=BZZOIRO_ODDS_SOURCE, stats=stats)
    if stats is not None:
        stats.update({
            "cached_rows": len(cached_rows),
            "live_rows": len(live_rows),
            "refreshed": bool(live_rows),
        })
    return bundle


def scoutingstats_odds_bundle(
    day: str,
    *,
    cached_rows: list[dict] | None = None,
    stats: dict | None = None,
) -> dict[str, dict]:
    source_rows = cached_rows if cached_rows is not None else _read_cached_scoutingstats(day)
    odds_rows = _scoutingstats_rows_to_odds(source_rows)
    bundle = _odds_bundle_from_rows(odds_rows, provider=SCOUTINGSTATS_ODDS_SOURCE, stats=stats)
    if stats is not None:
        stats.update({"cached_rows": len(source_rows), "live_rows": 0, "refreshed": False})
    return bundle


def bzzoiro_odds_index(
    day: str,
    *,
    live: bool = True,
    stats: dict | None = None,
) -> dict[tuple[str, str, str, str, str], dict]:
    return bzzoiro_odds_bundle(day, live=live, stats=stats)["exact"]


def find_odds_row(pick: dict, odds_data: dict) -> tuple[dict | None, str | None]:
    if "exact" not in odds_data:
        key = (
            str(pick.get("date") or ""),
            odds_team_key(pick.get("home") or ""),
            odds_team_key(pick.get("away") or ""),
            str(pick.get("market") or ""),
            str(pick.get("pick") or ""),
        )
        row = odds_data.get(key)
        return row, ("exact" if row else None)

    exact_key = (
        str(pick.get("date") or ""),
        odds_team_key(pick.get("home") or ""),
        odds_team_key(pick.get("away") or ""),
        str(pick.get("market") or ""),
        str(pick.get("pick") or ""),
    )
    row = odds_data["exact"].get(exact_key)
    if row:
        return row, "exact"

    candidates = odds_data["time_candidates"].get(_time_pick_key(pick), [])
    if candidates:
        pick_kickoff = _kickoff_value(pick)
        if pick_kickoff:
            bounded = [
                (_kickoff_delta_minutes(pick_kickoff, _kickoff_value(row)), row)
                for row in candidates
            ]
            bounded = [(delta, row) for delta, row in bounded if delta is not None and delta <= 90]
            if bounded:
                bounded.sort(key=lambda item: (item[0], -_bookmaker_priority(item[1].get("bookmaker")), -(item[1].get("odds") or 0.0)))
                return bounded[0][1], "alias_time"
        return candidates[0], "alias_unique"

    # Systematic Fallback: if exact and time candidate joins fail, fallback to Event-String Fuzzy Jaccard Matcher
    raw_list = odds_data.get("raw_rows_list", [])
    if raw_list:
        pick_str = f"{pick.get('home', '')} {pick.get('away', '')}"
        pick_kickoff = _kickoff_value(pick)
        
        best_row = None
        best_sim = 0.0
        
        for row in raw_list:
            if str(row.get("market")) != str(pick.get("market")) or str(row.get("selection")) != str(pick.get("pick")):
                continue
                
            delta = _kickoff_delta_minutes(pick_kickoff, _kickoff_value(row))
            if delta is not None and delta <= 90:
                res_str = f"{row.get('home', '')} {row.get('away', '')}"
                sim = char_ngram_similarity(pick_str, res_str, n=2)
                if sim >= 0.40 and sim > best_sim:
                    best_sim = sim
                    best_row = row
                    
        if best_row is not None:
            return best_row, "alias_fuzzy"

    return None, None


def nearby_odds_candidates(pick: dict, odds_data: dict, *, limit: int = 5) -> list[dict]:
    market_key = _market_pick_key(pick, selection_key="pick")
    candidates = list(odds_data.get("market_candidates", {}).get(market_key, []))
    pick_kickoff = _kickoff_value(pick)
    candidates.sort(
        key=lambda row: (
            _kickoff_delta_minutes(pick_kickoff, _kickoff_value(row)) is None,
            _kickoff_delta_minutes(pick_kickoff, _kickoff_value(row)) or 10**9,
            odds_match_team_key(row.get("home") or "") != odds_match_team_key(pick.get("home") or ""),
            odds_match_team_key(row.get("away") or "") != odds_match_team_key(pick.get("away") or ""),
        )
    )
    out = []
    for row in candidates[:limit]:
        out.append({
            "home": row.get("home"),
            "away": row.get("away"),
            "league": row.get("league"),
            "kickoff": _kickoff_value(row),
            "market": row.get("market"),
            "selection": row.get("selection"),
            "odds": row.get("odds"),
            "bookmaker": row.get("bookmaker"),
            "home_key": odds_match_team_key(row.get("home") or ""),
            "away_key": odds_match_team_key(row.get("away") or ""),
            "kickoff_delta_minutes": _kickoff_delta_minutes(pick_kickoff, _kickoff_value(row)),
        })
    return out


def enrich_with_live_odds(
    picks: list[dict],
    primary_odds: dict,
    secondary_odds: dict | None = None,
) -> int:
    enriched = 0
    for pick in picks:
        row, match_method = find_odds_row(pick, primary_odds)
        provider = primary_odds.get("provider", BZZOIRO_ODDS_SOURCE) if row else None
        if not row and secondary_odds is not None:
            row, match_method = find_odds_row(pick, secondary_odds)
            provider = secondary_odds.get("provider", SCOUTINGSTATS_ODDS_SOURCE) if row else None
        if not row:
            if pick.get("odds") is not None:
                pick.setdefault("odds_source", "forebet_best")
                pick["odds_match_method"] = "fallback"
            else:
                pick.setdefault("odds_source", None)
                pick["odds_match_method"] = "none"
            continue
        previous_odds = pick.get("odds")
        previous_source = pick.get("odds_source") or ("forebet_best" if previous_odds is not None else None)
        pick["odds"] = _valid_decimal_odds(row.get("odds"))
        pick["odds_source"] = provider or BZZOIRO_ODDS_SOURCE
        pick["odds_match_method"] = match_method or "exact"
        pick["bookmaker"] = row.get("bookmaker")
        pick["odds_captured_at"] = row.get("captured_at")
        pick["odds_league"] = row.get("league")
        if previous_odds is not None and previous_source != pick["odds_source"]:
            pick["odds_replaced"] = {"source": previous_source, "odds": previous_odds}
        enriched += 1
    return enriched


def enrich_with_bzzoiro_odds(picks: list[dict], odds_index: dict) -> int:
    return enrich_with_live_odds(picks, odds_index, None)


def probs_1x2(row):
    p1, px, p2 = _f(row.get("p1")), _f(row.get("px")), _f(row.get("p2"))
    if p1 is None or px is None or p2 is None:
        return None
    if p1 > 1.5 or px > 1.5 or p2 > 1.5:
        p1, px, p2 = p1 / 100.0, px / 100.0, p2 / 100.0
    return p1, px, p2


def prob_single(row, col):
    p = _f(row.get(col))
    if p is None:
        return None
    if p > 1.5:
        p /= 100.0
    return p


def top_pick(p1, px, p2):
    best = max(p1, px, p2)
    return ("home" if best == p1 else ("draw" if best == px else "away")), best


# --------------------------------------------------------------- consensus --
def eval_1x2(day, data, t1x2, source_weights: dict[str, float] | None = None):
    picks, vetoes = [], 0
    keys = set()
    for s in SOURCES_1X2:
        keys |= set(data.get(s, {}))
        
    # --- Load ML rules and model ---
    ml_rules, ml_model = load_ml_rules_and_model()
    rolling_hit_rate = None
    if ml_rules and ml_model:
        rolling_hit_rate = get_rolling_hit_rate_last_14d(day)

    for k in keys:
        sels, ps, used = [], [], []
        for s in SOURCES_1X2:
            row = data.get(s, {}).get(k)
            if not row:
                continue
            pr = probs_1x2(row)
            if pr is None:
                continue
            sel, pmax = top_pick(*pr)
            sels.append(sel)
            ps.append(pmax)
            used.append(s)
        if len(used) < 2:
            continue
            
        fb = data.get("forebet", {}).get(k) or {}
        zb = data.get("zulubet", {}).get(k) or {}
        sa = data.get("statarea", {}).get(k) or {}
        bz = data.get("bzzoiro", {}).get(k) or {}
        vb = data.get("vitibet", {}).get(k) or {}
        anchor = fb or zb or sa or next(data[s][k] for s in used if k in data.get(s, {}))
        
        # --- Evaluate ML Rules ---
        if ml_rules and ml_model and fb and zb and sa:
            fb_probs = probs_1x2(fb)
            zb_probs = probs_1x2(zb)
            sa_probs = probs_1x2(sa)
            if fb_probs and zb_probs and sa_probs:
                # Majority pick
                sels_maj = []
                for pr in [fb_probs, zb_probs, sa_probs]:
                    best = max(pr)
                    sel_m = "home" if best == pr[0] else ("draw" if best == pr[1] else "away")
                    sels_maj.append(sel_m)
                p1, p2, p3 = sels_maj
                if p1 == p2 or p1 == p3:
                    majority_pick = p1
                elif p2 == p3:
                    majority_pick = p2
                else:
                    majority_pick = p1
                
                idx_map = {"home": 0, "draw": 1, "away": 2}
                idx = idx_map[majority_pick]
                fb_p_feat = fb_probs[idx]
                zb_p_feat = zb_probs[idx]
                sa_p_feat = sa_probs[idx]
                
                avg_p_feat = (fb_p_feat + zb_p_feat + sa_p_feat) / 3.0
                min_p_feat = min(fb_p_feat, zb_p_feat, sa_p_feat)
                variance = sum((x - avg_p_feat)**2 for x in [fb_p_feat, zb_p_feat, sa_p_feat]) / 3.0
                std_p_feat = math.sqrt(variance)
                
                _odds_map = {"home": "odd1", "draw": "oddx", "away": "odd2"}
                _col = _odds_map[majority_pick]
                pick_odds_feat = _f(fb.get(_col)) or _f(zb.get(_col)) or 1.50
                
                is_home = 1.0 if majority_pick == "home" else 0.0
                is_away = 1.0 if majority_pick == "away" else 0.0
                
                comp_type = classify_competition(anchor.get("league"))
                cat_friendly = 1.0 if comp_type == "friendly" else 0.0
                cat_youth = 1.0 if comp_type == "youth" else 0.0
                cat_women = 1.0 if comp_type == "women" else 0.0
                cat_cup = 1.0 if comp_type == "cup" else 0.0
                cat_league = 1.0 if comp_type == "league" else 0.0
                
                feat_dict = {
                    "fb_p": fb_p_feat, "zb_p": zb_p_feat, "sa_p": sa_p_feat,
                    "avg_p": avg_p_feat, "min_p": min_p_feat, "std_p": std_p_feat,
                    "pick_odds": pick_odds_feat,
                    "is_home": is_home, "is_away": is_away,
                    "cat_friendly": cat_friendly, "cat_youth": cat_youth, "cat_women": cat_women, "cat_cup": cat_cup, "cat_league": cat_league,
                    "rolling_hit_rate": rolling_hit_rate or 0.75
                }
                
                coefs = ml_model["coef"]
                intercept = ml_model["intercept"]
                feature_cols = ml_model["feature_cols"]
                
                x = [feat_dict.get(col, 0.0) for col in feature_cols]
                z = sum(w * val for w, val in zip(coefs, x)) + intercept
                ml_p = 1.0 / (1.0 + math.exp(-z))
                
                # Check certified ML rules
                for rule in ml_rules:
                    m = re.search(r">=\s*([\d.]+)", rule["rule"])
                    if m:
                        thr = float(m.group(1))
                        if ml_p * 100.0 >= thr:
                            home = canonical_display_team(anchor.get("home"))
                            away = canonical_display_team(anchor.get("away"))
                            picks.append({
                                "date": day, "market": "1x2",
                                "match": f"{home} vs {away}",
                                "home": home, "away": away,
                                "kickoff": anchor.get("kickoff") or anchor.get("time"),
                                "sport": anchor.get("sport", "soccer"),
                                "league": anchor.get("league"), "pick": majority_pick,
                                "avg_p": round(ml_p * 100.0, 1),
                                "w_score": round(w_score, 4),
                                "odds": _f(fb.get(_col)) or _f(zb.get(_col)) or None,
                                "odds_source": ("forebet_best" if _f(fb.get(_col)) is not None else "zulubet" if _f(zb.get(_col)) is not None else None),
                                "bookmaker": None,
                                "rule": rule["rule"],
                                "edge_rule": rule["rule"],
                                "display_rule": rule["display_rule"] if "display_rule" in rule else f"ML-META≥{thr:.0f}",
                                "n_way": 3, "edge_n_way": 3,
                                "confidence": _f(bz.get("confidence")) if bz else None,
                                "model_version": bz.get("model_version") if bz else None,
                                "vitibet_index": _f(vb.get("index")) if vb else None,
                                "sources_used": used,
                                "source_weights": source_weights or {},
                                "ml_p": round(ml_p, 4),
                            })

        if len(set(sels)) > 1:
            vetoes += 1
            continue
        edge = thr_for(len(used), t1x2)
        if edge is None:
            continue
        n_req, thr = edge["n_way"], edge["threshold"]

        # Option 2: Dynamic Competition-Type Gating (Custom Thresholds)
        comp_type = classify_competition(anchor.get("league"))
        if comp_type == "cup":
            thr += 5.0
        elif comp_type == "friendly":
            thr += 10.0
            if n_req < 3:
                n_req = 3

        if len(used) < n_req:
            continue

        avg_p = mean(ps) * 100.0
        if avg_p < thr:
            continue
            
        sel = sels[0]
        _odds_map = {"home": "odd1", "draw": "oddx", "away": "odd2"}
        _col = _odds_map[sel]
        odds = _f(fb.get(_col)) or _f(zb.get(_col)) or None
        odds_src = ("forebet_best" if _f(fb.get(_col)) is not None
                    else "zulubet" if _f(zb.get(_col)) is not None
                    else None)
        home = canonical_display_team(anchor.get("home"))
        away = canonical_display_team(anchor.get("away"))
        
        # Weighted consensus score
        votes = [(sel, source_weights.get(s, 1.0)) for s, sel in zip(used, sels)]
        _, w_score, _ = weighted_consensus_score(votes)

        picks.append({
            "date": day, "market": "1x2",
            "match": f"{home} vs {away}",
            "home": home, "away": away,
            "kickoff": anchor.get("kickoff") or anchor.get("time"),
            "sport": anchor.get("sport", "soccer"),
            "league": anchor.get("league"), "pick": sel,
            "avg_p": round(avg_p, 1),
            "w_score": round(w_score, 4),
            "odds": odds,
            "odds_source": odds_src,
            "bookmaker": None,
            "rule": edge["rule"],
            "edge_rule": edge["rule"],
            "display_rule": edge["display_rule"],
            "n_way": len(used), "edge_n_way": n_req,
            "confidence": _f(bz.get("confidence")),
            "model_version": bz.get("model_version"),
            "vitibet_index": _f(vb.get("index")),
            "sources_used": used,
            "source_weights": source_weights or {},
        })
    return picks, vetoes, len(keys)


def eval_binary(day, data, market, sources, col_map, edge, yes_no, outcome_odds):
    if edge is None:
        return []
    n_req, thr = edge["n_way"], edge["threshold"]
    picks = []
    keys = set()
    for s in sources:
        keys |= set(data.get(s, {}))
    for k in keys:
        sels, confs, used = [], [], []
        for s in sources:
            row = data.get(s, {}).get(k)
            if not row:
                continue
            p = prob_single(row, col_map[s])
            if p is None:
                continue
            sel = yes_no[0] if p >= 0.5 else yes_no[1]
            sels.append(sel)
            confs.append(p if sel == yes_no[0] else 1.0 - p)
            used.append(s)
        if len(used) < 2:
            continue
        if len(set(sels)) > 1:
            continue

        comp_type = classify_competition(anchor := next(data[s][k] for s in used if k in data.get(s, {})))
        adj_thr = thr
        adj_n_req = n_req
        if comp_type == "cup":
            adj_thr += 5.0
        elif comp_type == "friendly":
            adj_thr += 10.0
            if adj_n_req < 3:
                adj_n_req = 3

        if len(used) < max(2, adj_n_req):
            continue

        avg_p = mean(confs) * 100.0
        if avg_p < adj_thr:
            continue
        fb = data.get("forebet", {}).get(k) or {}
        bz = data.get("bzzoiro", {}).get(k) or {}
        anchor = fb or next(data[s][k] for s in used if k in data.get(s, {}))
        sel = sels[0]
        odds = _f(fb.get(outcome_odds[sel])) if fb else None
        home = canonical_display_team(anchor.get("home"))
        away = canonical_display_team(anchor.get("away"))
        picks.append({
            "date": day, "market": market,
            "match": f"{home} vs {away}",
            "home": home, "away": away,
            "kickoff": anchor.get("kickoff") or anchor.get("time"),
            "sport": anchor.get("sport", "soccer"),
            "league": anchor.get("league"), "pick": sel,
            "avg_p": round(avg_p, 1), "odds": odds,
            "odds_source": "forebet_best" if odds is not None else None,
            "bookmaker": None,
            "rule": edge["rule"],
            "edge_rule": edge["rule"],
            "display_rule": edge["display_rule"],
            "n_way": len(used), "edge_n_way": n_req,
            "confidence": _f(bz.get("confidence")),
            "model_version": bz.get("model_version"),
            "vitibet_index": None,
            "sources_used": used,
        })
    return picks


# --------------------------------------------------------------------- run --
def run_day(day, t1x2, ou_edge, btts_edge, source_weights_1x2: dict | None = None):
    data = fetch_all(day)
    picks, vetoes, n_up = eval_1x2(day, data, t1x2,
                                   source_weights=source_weights_1x2 or {})
    picks += eval_binary(day, data, "ou_2.5", SOURCES_OU, OU_COL, ou_edge,
                         ("over", "under"),
                         {"over": "odd_over", "under": "odd_under"})
    picks += eval_binary(day, data, "btts", SOURCES_BTTS, BTTS_COL, btts_edge,
                         ("yes", "no"),
                         {"yes": "odd_gg", "no": "odd_ng"})
    picks.sort(key=lambda r: (-r.get("w_score", 0.0), -r.get("avg_p", 0)))
    return picks, vetoes, n_up, data


def _odds_source_rank(source: object) -> int:
    s = str(source or "")
    if s == BZZOIRO_ODDS_SOURCE:
        return 2
    if s == SCOUTINGSTATS_ODDS_SOURCE:
        return 1
    return 0


_BUCKET_SEVERITY = {
    BUCKET_CERTIFIED: 0,
    BUCKET_CAUTION: 10,
    BUCKET_WL_CTX: 20,
    BUCKET_WL_ODDS: 30,
    BUCKET_SKIP_VETO: 50,
    BUCKET_SKIP_DEAD: 60,
}


def _bucket_severity(bucket: object) -> int:
    return _BUCKET_SEVERITY.get(str(bucket or BUCKET_CAUTION), _BUCKET_SEVERITY[BUCKET_CAUTION])


def _event_base_key(pick: dict) -> tuple[str, str, str, str, str]:
    return (
        str(pick.get("date") or ""),
        operational_team_key(pick.get("home") or ""),
        operational_team_key(pick.get("away") or ""),
        str(pick.get("market") or ""),
        str(pick.get("pick") or ""),
    )


def _same_event_cluster(a: dict, b: dict) -> bool:
    a_min = _kickoff_minutes(_kickoff_value(a))
    b_min = _kickoff_minutes(_kickoff_value(b))
    if a_min is None or b_min is None:
        return True
    return abs(a_min - b_min) <= 180


def _representative_score(pick: dict) -> tuple:
    comment = pick.get("statistical_comment") or ""
    mu, sigma = re.search(r"n=(\d+)", comment), re.search(r"Avg Goals: ([\d.]+)", comment)
    has_rich_stats = 2 if (mu and int(mu.group(1)) >= 100 and sigma) else (1 if comment else 0)
    return (
        -has_rich_stats,  # prefer picks with 📊 stats (richer = higher priority)
        _bucket_severity(pick.get("bucket")),
        _kickoff_value(pick) is not None,
        _odds_source_rank(pick.get("odds_source")),
        pick.get("odds_match_method") == "exact",
        pick.get("odds_match_method") == "alias_time",
        float(pick.get("w_score") or 0),
        float(pick.get("avg_p") or 0),
        int(pick.get("n_way") or 0),
        -len(str(pick.get("match") or "")),
    )


def _with_duplicate_metadata(group: list[dict]) -> dict:
    rep = dict(max(group, key=_representative_score))
    if len(group) <= 1:
        return rep

    ctx = dict(rep.get("ctx") or {})
    buckets = [str(p.get("bucket") or BUCKET_CAUTION) for p in group]
    rules = sorted({str(p.get("display_rule") or p.get("rule") or "?") for p in group})
    matches = sorted({str(p.get("match") or "") for p in group if p.get("match")})
    keys = sorted({
        f"{operational_team_key(p.get('home') or '')} vs {operational_team_key(p.get('away') or '')}"
        for p in group
    })

    worst = max(group, key=lambda p: _bucket_severity(p.get("bucket")))
    rep["bucket"] = worst.get("bucket", rep.get("bucket", BUCKET_CAUTION))
    rep["duplicate_rows_collapsed"] = len(group) - 1
    rep["duplicate_bucket_sources"] = sorted(set(buckets), key=_bucket_severity)
    rep["duplicate_rules_collapsed"] = rules
    rep["duplicate_matches_collapsed"] = matches
    ctx["duplicate_alias_collapse"] = "true"
    ctx["duplicate_bucket_sources"] = ",".join(rep["duplicate_bucket_sources"])
    ctx["duplicate_event_keys"] = ",".join(keys)
    rep["ctx"] = ctx
    return rep


def collapse_final_operational_picks(picks: list[dict]) -> tuple[list[dict], int]:
    clusters: list[list[dict]] = []
    for pick in picks:
        matched = False
        pick_home = pick.get("home", "")
        pick_away = pick.get("away", "")
        pick_date = str(pick.get("date") or "")[:10]
        pick_market = str(pick.get("market") or "")
        pick_sel = str(pick.get("pick") or "")
        
        for cluster in clusters:
            rep = cluster[0]
            rep_date = str(rep.get("date") or "")[:10]
            rep_market = str(rep.get("market") or "")
            rep_sel = str(rep.get("pick") or "")
            
            if pick_date == rep_date and pick_market == rep_market and pick_sel == rep_sel:
                # Same date, market, selection. Now check kickoff and fuzzy team similarity
                if _same_event_cluster(rep, pick):
                    # Compute team Jaccard bigram similarity
                    h_sim = char_ngram_similarity(pick_home, rep.get("home", ""), n=2)
                    a_sim = char_ngram_similarity(pick_away, rep.get("away", ""), n=2)
                    
                    # Group if both are similar, or one matches exactly and the other is similar
                    if (h_sim >= 0.40 and a_sim >= 0.40) or (pick_home == rep.get("home") and a_sim >= 0.40) or (pick_away == rep.get("away") and h_sim >= 0.40):
                        cluster.append(pick)
                        matched = True
                        break
                        
        if not matched:
            clusters.append([pick])

    out: list[dict] = []
    removed = 0
    for cluster in clusters:
        out.append(_with_duplicate_metadata(cluster))
        removed += max(0, len(cluster) - 1)

    out.sort(key=lambda r: (-_bucket_severity(r.get("bucket")), -float(r.get("w_score") or 0.0), -float(r.get("avg_p") or 0)))
    return out, removed


def dedupe_operational_picks(picks: list[dict]) -> tuple[list[dict], int]:
    return collapse_final_operational_picks(picks)


def format_kickoff(pick: dict) -> str:
    for key in ("kickoff", "time", "start_time", "ko"):
        value = pick.get(key)
        if value not in (None, ""):
            return str(value)
    return "n/a"


def print_buckets(buckets: dict, title_date: str = ""):
    total_cert = len(buckets.get(BUCKET_CERTIFIED, [])) + len(buckets.get(BUCKET_CAUTION, []))
    print(f"\nEdge Factory Picks — {title_date}" if title_date else "\nEdge Factory Picks")
    print("=" * 60)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    for b in BUCKET_ORDER:
        picks = buckets.get(b, [])
        label = BUCKET_LABELS.get(b, b)
        print(f"{label}")
        print("=" * 60)
        if not picks:
            print("  (none)")
            print()
            continue
        for p in picks:
            if p.get("odds") is not None:
                o = f"@{p['odds']:.2f}"
                if p.get("odds_source") == BZZOIRO_ODDS_SOURCE and p.get("bookmaker"):
                    o += f" {p['bookmaker']}"
            else:
                o = "@n/a"
            ctx = p.get("ctx", {})
            ctx_str = (
                f"  league={ctx.get('league_key','?')}:{ctx.get('league','?')}  "
                f"team={ctx.get('home_norm','?')}:{ctx.get('team_h','?')}/"
                f"{ctx.get('away_norm','?')}:{ctx.get('team_a','?')}  "
                f"odds_band={ctx.get('odds_band_name','?')}:{ctx.get('odds_band','?')}  "
                f"comp_type={ctx.get('comp_type_name','?')}:{ctx.get('competition_type','?')}"
            )
            market = p.get("market_type", p.get("market", "?"))
            tier = p.get("odds_tier", "?")
            label = p.get("display_rule") or p.get("rule", "?")
            kickoff = format_kickoff(p)
            w_str = f"  w={p['w_score']:.2f}" if p.get("w_score") is not None else ""
            
            warn_str = ""
            rec = p.get("recommended_market")
            if rec and rec not in ("keep_1x2", "unknown"):
                risk = p.get("draw_risk_flag", "")
                label_txt = rec.upper().replace('_', ' ')
                if risk == "EXTREME":
                    warn_str = f"  [⛔ {risk} DRAW/PRICE RISK — {label_txt}]"
                else:
                    warn_str = f"  [⚠️ {risk} DRAW RISK — {label_txt}]"
                    
            print(f"  [{label}] {p['match'][:45]:45s} KO {kickoff:5s} -> {p['pick'].upper():5s}  avg {p['avg_p']:.0f}%{w_str} {o}  [{market}/{tier}]{warn_str}")
            if ctx:
                print(ctx_str)
            if p.get("statistical_comment"):
                print(f"     {p['statistical_comment']}")
            notes = p.get("event_notes", [])
            if notes:
                event_text = " | ".join(
                    f"{note['label'].replace(' Goals', '')}: {note['probability']:.1%}"
                    for note in notes
                )
                print(f"     🔥 Possible Events: {event_text}")
        print()
    print("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
    print("⚠️  Bet only what you can afford to lose.")


# ---------------------------------------------------------------- betexplorer --
BETEXPLORER_ODDS_SOURCE = "betexplorer_odds"


def enrich_unmatched_with_betexplorer(
    picks: list[dict],
    day: str,
    *,
    max_fetches: int = 12,
) -> int:
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "edgefactory.sources.betexplorer_odds",
            str(ROOT / "src" / "edgefactory" / "sources" / "betexplorer_odds.py"),
        )
        _be_mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_be_mod)
        betexplorer_odds_rows_for_pick = _be_mod.betexplorer_odds_rows_for_pick
        reset_fetch_count = _be_mod.reset_fetch_count
        _BE_SOURCE = _be_mod.BETEXPLORER_ODDS_SOURCE
    except Exception:
        print("  betexplorer_odds: adapter not available, skipping", file=sys.stderr)
        return 0

    from edgefactory.util import norm_team as _norm_team

    reset_fetch_count()
    enriched = 0
    for pick in picks:
        method = str(pick.get("odds_match_method") or "")
        if method not in ("fallback", "none"):
            continue

        rows = betexplorer_odds_rows_for_pick(pick, day, norm_team_fn=_norm_team)
        if not rows:
            continue

        sel = str(pick.get("pick") or "")
        market = str(pick.get("market") or "")
        matching_row = None
        for r in rows:
            if str(r.get("selection") or "") == sel and str(r.get("market") or "") == market:
                matching_row = r
                break

        if matching_row is None:
            continue

        new_odds = _valid_decimal_odds(matching_row.get("odds"))
        if new_odds is None:
            continue

        previous_odds = pick.get("odds")
        previous_source = pick.get("odds_source")
        pick["odds"] = new_odds
        pick["odds_source"] = _BE_SOURCE
        pick["odds_match_method"] = "betexplorer"
        pick["bookmaker"] = matching_row.get("bookmaker")
        pick["odds_captured_at"] = matching_row.get("captured_at")
        pick["odds_league"] = matching_row.get("league")
        if previous_odds is not None and previous_source != pick["odds_source"]:
            pick["odds_replaced"] = {"source": previous_source, "odds": previous_odds}
        enriched += 1

    return enriched


def main():
    days = sys.argv[1:] or [
        date.today().isoformat(),
    ]
    t1x2, ou_edge, btts_edge, fallback = load_thresholds()
    edge_meta = load_edge_meta()
    purity = load_purity()
    purity_missing = not bool(purity)
    as_of = pick_run_as_of()
    lead_minutes = min_lead_minutes()
    print(
        f"operational as_of={as_of.isoformat(timespec='seconds')} min_lead={lead_minutes}m",
        file=sys.stderr,
    )

    source_weights_1x2 = load_source_weights("1x2")
    if source_weights_1x2:
        print(
            f"Weighted consensus active — source LBs: "
            + ", ".join(f"{s}={lb:.3f}" for s, lb in sorted(source_weights_1x2.items())),
            file=sys.stderr,
        )
    else:
        print(
            "Weighted consensus: no certified weighted edge yet — using uniform weights.",
            file=sys.stderr,
        )

    if fallback:
        print("edge registry missing/empty -> fallback to certified "
              "thresholds: 1x2 2-way>=70 / 3-way>=65 + veto; OU/BTTS skipped",
              file=sys.stderr)
    if purity_missing:
        print("purity_registry.json missing – all contexts will be UNKNOWN → WATCHLIST",
              file=sys.stderr)

    all_picks: list = []
    total_vetoes = 0
    total_upcoming = 0
    
    # Open warehouse connection to dynamically query historical realized stats
    con = None
    try:
        import duckdb
        con = duckdb.connect(str(LOCALDATA / "warehouse.duckdb"), read_only=True)
    except Exception:
        con = None

    for day in days:
        picks, vetoes, n_up, data = run_day(day, t1x2, ou_edge, btts_edge,
                                            source_weights_1x2=source_weights_1x2)
        total_vetoes += vetoes
        total_upcoming += n_up
        picks, pre_match_skips = filter_operational_pre_match_picks(
            picks,
            as_of=as_of,
            min_lead=lead_minutes,
        )
        if pre_match_skips:
            details = ", ".join(f"{k}={v}" for k, v in sorted(pre_match_skips.items()))
            print(f"pre-match guard {day}: skipped {sum(pre_match_skips.values())} ({details})", file=sys.stderr)

        bzz_stats: dict = {}
        scouting_stats: dict = {}
        odds_bundle = bzzoiro_odds_bundle(day, stats=bzz_stats)
        secondary_bundle = scoutingstats_odds_bundle(
            day,
            cached_rows=list(data.get("scoutingstats", {}).values()),
            stats=scouting_stats,
        )
        enriched_n = enrich_with_live_odds(picks, odds_bundle, secondary_bundle)

        be_enriched = enrich_unmatched_with_betexplorer(picks, day)

        if bzz_stats.get("raw_rows") or scouting_stats.get("raw_rows") or enriched_n or picks:
            exact_n = sum(1 for p in picks if p.get("odds_match_method") == "exact")
            alias_time_n = sum(1 for p in picks if p.get("odds_match_method") == "alias_time")
            alias_unique_n = sum(1 for p in picks if p.get("odds_match_method") == "alias_unique")
            fallback_n = sum(1 for p in picks if p.get("odds_match_method") == "fallback")
            none_n = sum(1 for p in picks if p.get("odds_match_method") == "none")
            betexp_n = sum(1 for p in picks if p.get("odds_match_method") == "betexplorer")
            bzz_n = sum(1 for p in picks if p.get("odds_source") == BZZOIRO_ODDS_SOURCE)
            scouting_n = sum(1 for p in picks if p.get("odds_source") == SCOUTINGSTATS_ODDS_SOURCE)
            be_source_n = sum(1 for p in picks if p.get("odds_source") == BETEXPLORER_ODDS_SOURCE)
            print(
                f"live odds enrichment {day}: "
                f"picks={len(picks)} "
                f"bzz_cached={bzz_stats.get('cached_rows', 0)} "
                f"bzz_live={bzz_stats.get('live_rows', 0)} "
                f"bzz_valid_keys={bzz_stats.get('valid_keys', len(odds_bundle.get('exact', {})))} "
                f"bzz_alias_keys={bzz_stats.get('time_match_keys', len(odds_bundle.get('time_candidates', {})))} "
                f"ss_cached={scouting_stats.get('cached_rows', 0)} "
                f"ss_valid_keys={scouting_stats.get('valid_keys', len(secondary_bundle.get('exact', {})))} "
                f"enriched={enriched_n} betexplorer={be_enriched} bzz={bzz_n} scoutingstats={scouting_n} betexplorer_src={be_source_n} "
                f"exact={exact_n} alias_time={alias_time_n} alias_unique={alias_unique_n} fallback={fallback_n} none={none_n} betexplorer_m={betexp_n}",
                file=sys.stderr,
            )

        day_picks: list[dict] = []

        for p in picks:
            rule = p.get("rule", "")
            meta = edge_meta.get(rule, {"status": "certified", "decay_verdict": "HEALTHY"})
            ctx = lookup_context(purity, p)
            bucket = bucket_pick(p, ctx,
                                 edge_status=meta.get("status", "certified"),
                                 decay_verdict=meta.get("decay_verdict", "HEALTHY"))
            if bucket is None:
                continue
            p["ctx"] = {k: v for k, v in ctx.items() if not k.startswith("_")}
            p["bucket"] = bucket
            p["edge_status"] = meta.get("status", "certified")
            p["decay_verdict"] = meta.get("decay_verdict", "HEALTHY")

            p["market_type"] = p.get("market", "1x2")
            p["odds_tier"] = get_odds_tier(p.get("market", "1x2"))
            p["odds_match_status"] = "matched" if p.get("odds") is not None else "unmatched"
            
            annotate_market_recommendation(p)
            
            p["statistical_comment"] = get_statistical_comment(con, p.get("pick"), p.get("avg_p"), p.get("n_way", 3))
            
            # Compute deep dynamic enhancement overlay
            enh = compute_dynamic_enhancement(con, p)
            p.update(enh)
            
            day_picks.append(p)

        collapsed_day_picks, removed_dupes = collapse_final_operational_picks(day_picks)
        if removed_dupes:
            print(f"operational final pick collapse {day}: removed={removed_dupes}", file=sys.stderr)

        all_picks.extend(collapsed_day_picks)

    if con:
        try:
            con.close()
        except Exception:
            pass

    buckets: dict[str, list] = {b: [] for b in BUCKET_ORDER}
    for p in all_picks:
        b = p.get("bucket", BUCKET_CAUTION)
        buckets.setdefault(b, []).append(p)

    for b in buckets:
        buckets[b].sort(key=lambda r: -r.get("avg_p", 0))

    title = ", ".join(days) if days else date.today().isoformat()
    print_buckets(buckets, title_date=title)

    n_clean = len(buckets[BUCKET_CERTIFIED])
    n_caution = len(buckets[BUCKET_CAUTION])
    n_wl_odds = len(buckets[BUCKET_WL_ODDS])
    n_wl_ctx = len(buckets[BUCKET_WL_CTX])
    n_skip_veto = len(buckets[BUCKET_SKIP_VETO])
    n_skip_dead = len(buckets[BUCKET_SKIP_DEAD])
    summary = (f"Summary: CLEAN={n_clean} CAUTION={n_caution} "
               f"WATCHLIST_odds={n_wl_odds} WATCHLIST_ctx={n_wl_ctx} "
               f"SKIPPED_veto={n_skip_veto} SKIPPED_dead={n_skip_dead}  "
               f"({total_vetoes} vetoes, {total_upcoming} matches)")
    print(f"\n{summary}")

    # Layer A: Alert on UNKNOWN league verdicts so missing aliases are caught
    # immediately instead of requiring cross-file manual inspection.
    unknown_leagues: Counter = Counter()
    for p in all_picks:
        ctx = p.get("ctx", {}) or {}
        if str(ctx.get("league") or ctx.get("league_raw") or "") in ("UNKNOWN", "?"):
            unknown_leagues[str(ctx.get("league_raw") or "?")] += 1
    if unknown_leagues:
        print("\n⚠️  UNKNOWN league verdicts (consider adding to entity_overrides.json):")
        for league_raw, count in unknown_leagues.most_common(30):
            print(f"     {count:>3}x  {league_raw}")

    final_picks = all_picks

    _json_path = ROOT / "localdata" / "picks_today.json"
    _json_path.parent.mkdir(parents=True, exist_ok=True)
    _json_path.write_text(json.dumps(final_picks, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
