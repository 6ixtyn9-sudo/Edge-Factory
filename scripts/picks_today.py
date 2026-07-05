#!/usr/bin/env python3
"""picks_today.py with market_type and odds_tier fields (Phase 7)."""

from __future__ import annotations

import csv
import gzip
import os
import importlib
import json
import re
import sys
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import canonical_league, canonical_team, classify_competition
from edgefactory.util import compact_key, norm_team, fold_ascii
from edgefactory.market_registry import get_odds_tier
from edgefactory.assay import weighted_consensus_score

EDGES_PATH = ROOT / "localdata" / "edges_consensus.json"
PURITY_PATH = ROOT / "localdata" / "purity_registry.json"
LOCALDATA = ROOT / "localdata"
BZZOIRO_ODDS_SOURCE = "bzzoiro_odds"
SCOUTINGSTATS_ODDS_SOURCE = "scoutingstats_odds"

# Operational source/odds aliasing stays local to picks_today so certified miners,
# warehouse joins, and historical backtests remain unchanged.
#
# Two distinct key spaces exist here:
# - source row joins use legacy norm_team(...)->9 char keys
# - odds matching uses both legacy exact keys and compact kickoff-aware keys
#
# Keep aliases explicit and minimal.
SOURCE_TEAM_KEY_ALIASES = {
    "thunder": "dandenong",   # Forebet: Thunder SC; others: Dandenong Thunder
    "hobartzeb": "clarencez", # some feeds: Hobart Zebras; others: Clarence Zebras
}

ODDS_EXACT_TEAM_ALIASES = {
    "caboverde": "capeverde",
    "drcongo": "congodr",
    "ifkmarieh": "mariehamn",
    "ifkmariehamn": "mariehamn",
    "thunder": "dandenong",
    "hobartzeb": "clarencez",
    # 2026-07 mismatch fixes — abbreviations and renames between
    # prediction sources and odds providers.  fold_ascii now handles
    # accent mismatches (ø→o etc.) so these only cover structural
    # naming differences that no normalization can resolve.
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
}

ODDS_MATCH_TEAM_ALIASES = {
    "caboverde": "capeverde",
    "drcongo": "congodr",
    "ifkmarieh": "mariehamn",
    "ifkmariehamn": "mariehamn",
    "thundersc": "dandenongthunder",
    "hobartzebras": "clarencezebras",
    "hobartzebrasfc": "clarencezebras",
    # 2026-07 mismatch fixes — compact_key space aliases for
    # abbreviations/renames between prediction sources and odds providers.
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
}

DISPLAY_TEAM_ALIASES = {
    "thundersc": "Dandenong Thunder",
    "hobartzebras": "Clarence Zebras",
    "hobartzebrasfc": "Clarence Zebras",
}

# Final pick/report de-duplication is operational only.  It must be safer than
# the legacy miner join key, but it must not use the learned entity registry or
# canonical_team() because those can over-merge unrelated live odds/events.
# Strip only non-identity club designators; preserve W/U19/B/II/reserve-like
# suffixes so different squads do not collapse.  This intentionally collapses
# source spelling variants such as "AC Oulu"/"Oulu" and
# "IFK Mariehamn"/"Mariehamn" while keeping "Khovd" and "Khovd Western" apart.
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

# ---- purity buckets (unchanged) ----
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

# CAUTION odds floor — any CAUTION pick priced below this is reclassified as
# SKIPPED_VETO.  The CAUTION bucket historically runs at -8.4% ROI (72% HR at
# avg odds 1.38), because short odds + uncertain context is structurally
# unprofitable.  At odds 1.40 the breakeven HR is 71.4%, which CAUTION's 72%
# barely clears; below that the math flips negative.  This is a surgical fix
# that preserves the CAUTION bucket for longer-odds picks while eliminating
# the short-odds trap.
CAUTION_MIN_ODDS = 1.40


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
    """Qualified rules are analysis variants (min_p, home-only, etc.) that must
    not displace the base canonical rule as the operational picks_today threshold.
    They are miner-level findings — they inform the purity assay, not the
    picks_today threshold selector."""
    r = rule.lower()
    return any(tok in r for tok in _QUALIFIED_TOKENS)


def _prefer_entry(new: dict, old: dict | None) -> bool:
    """Prefer the base canonical rule for operational use in picks_today.

    Priority (highest first):
      1. Unqualified rule beats any qualified rule (min_p, home-only, etc.)
      2. Lower threshold beats higher threshold (wider coverage)
      3. Shorter/simpler rule name beats longer/more specific
    """
    if old is None:
        return True
    new_qual = _is_qualified(new["rule"])
    old_qual = _is_qualified(old["rule"])
    # Unqualified always beats qualified
    if new_qual != old_qual:
        return old_qual  # prefer new only if old is qualified and new is not
    # Both same qualification status: prefer lower threshold
    if new["threshold"] != old["threshold"]:
        return new["threshold"] < old["threshold"]
    # Same threshold: prefer simpler (shorter) rule
    new_rule, old_rule = new["rule"].lower(), old["rule"].lower()
    new_penalty = ("no-draw" in new_rule, len(new_rule))
    old_penalty = ("no-draw" in old_rule, len(old_rule))
    return new_penalty < old_penalty


def load_thresholds():
    """Return certified thresholds with exact edge rule names.

    The exact miner `rule` is used for edge_meta and purity context lookups;
    `display_rule` is only for printing.
    """
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
    """Load per-source Wilson LB weights from edges_consensus.json.

    Looks for the best (highest w_score threshold) certified weighted rule
    and returns its source_weights dict.  Falls back to equal weights (1.0)
    for every source if no weighted edge is certified yet.
    """
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
            # parse threshold from rule name e.g. "weighted-1x2 w_score>=0.70"
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
    """Pick the strongest available context verdict from ordered candidates.

    First non-UNKNOWN wins. If all are UNKNOWN/missing, return the UNKNOWN entry
    with the largest sample so diagnostics still show what was found.
    """
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
    """Best non-UNKNOWN context matching a key prefix/suffix, by sample size."""
    matches = [v for k, v in ctx.items() if k.startswith(prefix) and (not suffix or k.endswith(suffix))]
    non_unknown = [v for v in matches if v.get("verdict") != "UNKNOWN"]
    pool = non_unknown or matches
    if not pool:
        return {}
    return max(pool, key=lambda v: int(v.get("n") or 0))


def lookup_context(purity: dict, pick: dict) -> dict:
    """Build context keys and return verdicts plus raw diagnostics."""
    ctx = purity.get("contexts", {}) if purity else {}
    league_ctx = ctx.get("league", {})
    team_ctx = ctx.get("team", {})
    odds_ctx = ctx.get("odds_band", {})
    comp_ctx = ctx.get("competition_type", {})
    niche_ctx = ctx.get("niche", {})

    sport = pick.get("sport", "soccer")
    league_raw = pick.get("league") or "UNKNOWN"
    league = canonical_league(league_raw)
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
                decay_verdict: str = "HEALTHY") -> str:
    """Bucket pick using mature evidence only as hard gates.

    Phase A/B tightening:
    - niche VETO now acts as a first-class hard gate
    - short-odds sniper candidates are treated more defensively when league
      context is UNKNOWN
    - away favourites and >1.25 raw 1X2 expressions are no longer allowed to
      masquerade as healthy sniper picks
    """
    if edge_status == "benched":
        return BUCKET_SKIP_DEAD
    if decay_verdict in ("DEAD", "DECAYING"):
        return BUCKET_SKIP_DEAD

    vals = [ctx.get("league"), ctx.get("team_h"), ctx.get("team_a"), ctx.get("odds_band"), ctx.get("competition_type"), ctx.get("niche")]
    if "VETO" in vals:
        return BUCKET_SKIP_VETO
    if pick.get("odds") is None:
        return BUCKET_WL_ODDS

    market = str(pick.get("market") or "")
    odds = pick.get("odds")
    sel = str(pick.get("pick") or "")
    league_key = str(ctx.get("league_key") or "")
    short_sniper = market == "1x2" and sel == "home" and odds is not None and float(odds) < SHORT_ODDS_SNIPER_MAX

    if market == "1x2" and sel == "away" and odds is not None and float(odds) < 1.30:
        return BUCKET_SKIP_VETO
    if market == "1x2" and odds is not None and float(odds) >= 1.25:
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
    elif "UNKNOWN" in (ctx.get("league"), ctx.get("team_h"), ctx.get("team_a"), ctx.get("competition_type")):
        bucket = BUCKET_CAUTION
    else:
        bucket = BUCKET_CERTIFIED

    # CAUTION odds floor: short-odds CAUTION picks are structurally
    # unprofitable (72% HR can't cover breakeven below 1.40).  Reclassify
    # to SKIPPED_VETO so they don't enter the betting pipeline.
    if bucket == BUCKET_CAUTION and odds is not None and float(odds) < CAUTION_MIN_ODDS:
        return BUCKET_SKIP_VETO

    return bucket


# ------------------------------------------------------------------- fetch --
def fetch_all(day: str) -> dict[str, dict]:
    """Fetch every source (unchanged)."""
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
    """Normalize a small set of provider-specific display aliases for operational output."""
    raw = str(name or "").strip()
    if not raw:
        return raw
    return DISPLAY_TEAM_ALIASES.get(compact_key(raw), raw)


def source_team_key(name: object) -> str:
    """Operational source-join key for picks_today only.

    Uses the legacy 9-char norm_team key, plus a tiny explicit alias layer for
    known provider drift such as Thunder SC/Dandenong Thunder and
    Hobart Zebras/Clarence Zebras.
    """
    key = norm_team(str(name or ""))
    return SOURCE_TEAM_KEY_ALIASES.get(key, key)


def odds_team_key(name: object) -> str:
    """Legacy exact-match team key for odds enrichment only with accent folding."""
    key = norm_team(fold_ascii(str(name or "")))
    return ODDS_EXACT_TEAM_ALIASES.get(key, key)


def odds_match_team_key(name: object) -> str:
    """Operational team key for odds fallback matching.

    Unlike canonical_team(), this preserves identity-bearing suffixes such as
    U19/U21/B/II because operational odds matching must not merge those away.
    """
    raw = str(name or "")
    compact = compact_key(raw)
    return ODDS_MATCH_TEAM_ALIASES.get(compact, compact)


def operational_team_key(name: object) -> str:
    """Conservative event key for final pick/report duplicate collapse only.

    This is deliberately local to the operational output layer.  It does not
    alter warehouse/miner joins and it does not depend on entity-registry
    canonical fallbacks.
    """
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
    """Guard against after-the-fact same-day picks.

    For operational output, a target-day match must be generated before kickoff
    with a configurable lead time.  Future-date picks are allowed.  Past dates
    must be read from archived picks_YYYY-MM-DD.json by daily.py, not recreated
    from live source pages after results or source pages have drifted.
    """
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
    """Prefer real books over aggregate/Polymarket rows, but keep aggregates as fallback."""
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
    """Prefer real books, then higher decimal odds, then freshest capture."""
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
    """Read cached bzzoiro_odds CSV rows for a day, if capture_daily wrote them."""
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
    """Read cached scoutingstats rows for a day from the monthly CSV cache."""
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
    """Fetch live odds via adapter. Missing token/API failure -> zero rows."""
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
    }


def bzzoiro_odds_bundle(
    day: str,
    *,
    live: bool = True,
    stats: dict | None = None,
) -> dict[str, dict]:
    """Best available bzzoiro_odds rows for exact and kickoff-aware fallback matching."""
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
    """Secondary odds bundle built from scoutingstats upcoming rows."""
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
    """Backward-compatible exact odds index."""
    return bzzoiro_odds_bundle(day, live=live, stats=stats)["exact"]


def find_odds_row(pick: dict, odds_data: dict) -> tuple[dict | None, str | None]:
    """Find the best odds row using exact and explicit odds-only aliases.

    Do not use learned entity-registry canonical fallbacks here: live odds
    matching must stay explicit and kickoff-aware so identity drift cannot
    silently move prices between different real-world events.
    """
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
        # Always fall back to the first sorted candidate of the exact same event
        return candidates[0], "alias_unique"

    return None, None


def nearby_odds_candidates(pick: dict, odds_data: dict, *, limit: int = 5) -> list[dict]:
    """Return nearby same-date odds rows for unmatched diagnostics."""
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
    """Prefer primary, then secondary live odds, then embedded fallback."""
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
    """Backward-compatible wrapper for primary-only live odds enrichment."""
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
    """Head-count + optional weighted consensus for 1x2 picks.

    source_weights: {source_name: wilson_lb} from the certified weighted edge.
    When provided, each source's vote is weighted by its LB; the weighted
    agreement score (w_score) is stored on the pick for display/sorting.
    The unweighted avg_p is still computed and stored for backward compatibility.
    """
    picks, vetoes = [], 0
    keys = set()
    for s in SOURCES_1X2:
        keys |= set(data.get(s, {}))
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
        if len(set(sels)) > 1:
            vetoes += 1
            continue
        edge = thr_for(len(used), t1x2)
        if edge is None:
            continue
        n_req, thr = edge["n_way"], edge["threshold"]

        # Option 2: Dynamic Competition-Type Gating (Custom Thresholds)
        anchor = next(data[s][k] for s in used if k in data.get(s, {}))
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

        # Weighted consensus score — uses per-source Wilson LB as vote weight.
        # Falls back to uniform weights (lb=1.0 each) if no weights loaded.
        votes = [(sel, source_weights.get(s, 1.0)) for s, sel in zip(used, sels)]
        _, w_score, _ = weighted_consensus_score(votes)

        if avg_p < thr:
            continue
        fb = data.get("forebet", {}).get(k) or {}
        bz = data.get("bzzoiro", {}).get(k) or {}
        vb = data.get("vitibet", {}).get(k) or {}
        anchor = fb or next(data[s][k] for s in used if k in data.get(s, {}))
        sel = sels[0]
        # Cascade: forebet best-odds → None (bzzoiro_odds enriched later).
        # Zulubet odds are EXCLUDED from the initial cascade: they produce
        # -17.6% ROI (14 settled, 64.3% HR) vs forebet_best +15.4%.
        # Zulubet still contributes PREDICTIONS (consensus voting) — only
        # its PRICING is deprioritised.  Picks that miss forebet odds will
        # get None here and be enriched by bzzoiro_odds or scoutingstats
        # in the live-odds step; if no live odds exist they go to
        # WATCHLIST_NO_ODDS, which is better than betting at zulubet prices.
        _odds_map = {"home": "odd1", "draw": "oddx", "away": "odd2"}
        _col = _odds_map[sel]
        odds = _f(fb.get(_col))
        odds_src = "forebet_best" if odds is not None else None
        home = canonical_display_team(anchor.get("home"))
        away = canonical_display_team(anchor.get("away"))
        picks.append({
            "date": day, "market": "1x2",
            "match": f"{home} vs {away}",
            "home": home, "away": away,
            "kickoff": anchor.get("kickoff") or anchor.get("time"),
            "sport": anchor.get("sport", "soccer"),
            "league": anchor.get("league"), "pick": sel,
            "avg_p": round(avg_p, 1),
            "w_score": round(w_score, 4),   # weighted agreement score (0–1)
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

        # Option 2: Dynamic Competition-Type Gating for binary markets
        anchor = next(data[s][k] for s in used if k in data.get(s, {}))
        comp_type = classify_competition(anchor.get("league"))
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
    # Sort by w_score (weighted agreement) then avg_p; both descending.
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
    """Final operational event key for output collapse.

    Rule is intentionally excluded: if the same real-world event/outcome appears
    under both a 2-way and 3-way certified rule, the output must still show only
    one operational decision.  Any worse bucket among the aliases is propagated.
    """
    return (
        str(pick.get("date") or ""),
        operational_team_key(pick.get("home") or ""),
        operational_team_key(pick.get("away") or ""),
        str(pick.get("market") or ""),
        str(pick.get("pick") or ""),
    )


def _same_event_cluster(a: dict, b: dict) -> bool:
    """Return True when two same-base picks should collapse.

    If both kickoff times are known and more than three hours apart, keep them
    separate.  Missing kickoff stays permissive because alias duplicates often
    lose kickoff in one source.
    """
    a_min = _kickoff_minutes(_kickoff_value(a))
    b_min = _kickoff_minutes(_kickoff_value(b))
    if a_min is None or b_min is None:
        return True
    return abs(a_min - b_min) <= 180


def _representative_score(pick: dict) -> tuple:
    """Higher score wins when choosing which duplicate row to display."""
    return (
        _bucket_severity(pick.get("bucket")),  # conservative: display worst bucket
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
    """Collapse duplicate final picks after bucket assignment.

    This is the last safety net before stdout/JSON/Supabase sync.  It is run
    after context bucketing so duplicate aliases cannot hide a VETO/DEAD result.
    """
    grouped: dict[tuple[str, str, str, str, str], list[list[dict]]] = {}
    for pick in picks:
        base = _event_base_key(pick)
        clusters = grouped.setdefault(base, [])
        for cluster in clusters:
            if _same_event_cluster(cluster[0], pick):
                cluster.append(pick)
                break
        else:
            clusters.append([pick])

    out: list[dict] = []
    removed = 0
    for clusters in grouped.values():
        for cluster in clusters:
            out.append(_with_duplicate_metadata(cluster))
            removed += max(0, len(cluster) - 1)

    out.sort(key=lambda r: (-_bucket_severity(r.get("bucket")), -float(r.get("w_score") or 0.0), -float(r.get("avg_p") or 0)))
    return out, removed


# Backwards-compatible name for tests/importers.  Operational code uses the
# post-bucket collapse above; this wrapper is intentionally conservative too.
def dedupe_operational_picks(picks: list[dict]) -> tuple[list[dict], int]:
    return collapse_final_operational_picks(picks)


def format_kickoff(pick: dict) -> str:
    """Human stdout kickoff display. Always show missing kickoff explicitly."""
    for key in ("kickoff", "time", "start_time", "ko"):
        value = pick.get(key)
        if value not in (None, ""):
            return str(value)
    return "n/a"


def print_buckets(buckets: dict, title_date: str = ""):
    """Print picks grouped by bucket."""
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
                f"  league={ctx.get('league_raw','UNKNOWN')}:{ctx.get('league','?')}  "
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
        print()
    print("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
    print("⚠️  Bet only what you can afford to lose.")


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

    # Weighted consensus: load per-source Wilson LB weights.
    # Empty dict = fall back to uniform weights silently.
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
        if bzz_stats.get("raw_rows") or scouting_stats.get("raw_rows") or enriched_n or picks:
            exact_n = sum(1 for p in picks if p.get("odds_match_method") == "exact")
            alias_time_n = sum(1 for p in picks if p.get("odds_match_method") == "alias_time")
            alias_unique_n = sum(1 for p in picks if p.get("odds_match_method") == "alias_unique")
            fallback_n = sum(1 for p in picks if p.get("odds_match_method") == "fallback")
            none_n = sum(1 for p in picks if p.get("odds_match_method") == "none")
            bzz_n = sum(1 for p in picks if p.get("odds_source") == BZZOIRO_ODDS_SOURCE)
            scouting_n = sum(1 for p in picks if p.get("odds_source") == SCOUTINGSTATS_ODDS_SOURCE)
            print(
                f"live odds enrichment {day}: "
                f"picks={len(picks)} "
                f"bzz_cached={bzz_stats.get('cached_rows', 0)} "
                f"bzz_live={bzz_stats.get('live_rows', 0)} "
                f"bzz_valid_keys={bzz_stats.get('valid_keys', len(odds_bundle.get('exact', {})))} "
                f"bzz_alias_keys={bzz_stats.get('time_match_keys', len(odds_bundle.get('time_candidates', {})))} "
                f"ss_cached={scouting_stats.get('cached_rows', 0)} "
                f"ss_valid_keys={scouting_stats.get('valid_keys', len(secondary_bundle.get('exact', {})))} "
                f"enriched={enriched_n} bzz={bzz_n} scoutingstats={scouting_n} "
                f"exact={exact_n} alias_time={alias_time_n} alias_unique={alias_unique_n} fallback={fallback_n} none={none_n}",
                file=sys.stderr,
            )

        # Bucket every row before final operational collapse.  This prevents an
        # alias duplicate from hiding a VETO/DEAD context on the row that would
        # otherwise be removed.
        day_picks: list[dict] = []

        # Phase 7 enrichment + new fields
        for p in picks:
            rule = p.get("rule", "")
            meta = edge_meta.get(rule, {"status": "certified", "decay_verdict": "HEALTHY"})
            ctx = lookup_context(purity, p)
            bucket = bucket_pick(p, ctx,
                                 edge_status=meta.get("status", "certified"),
                                 decay_verdict=meta.get("decay_verdict", "HEALTHY"))
            p["ctx"] = {k: v for k, v in ctx.items() if not k.startswith("_")}
            p["bucket"] = bucket
            p["edge_status"] = meta.get("status", "certified")
            p["decay_verdict"] = meta.get("decay_verdict", "HEALTHY")

            # Phase 7 additions
            p["market_type"] = p.get("market", "1x2")
            p["odds_tier"] = get_odds_tier(p.get("market", "1x2"))
            p["odds_match_status"] = "matched" if p.get("odds") is not None else "unmatched"
            
            annotate_market_recommendation(p)
            
            day_picks.append(p)

        collapsed_day_picks, removed_dupes = collapse_final_operational_picks(day_picks)
        if removed_dupes:
            print(f"operational final pick collapse {day}: removed={removed_dupes}", file=sys.stderr)

        all_picks.extend(collapsed_day_picks)

    # group by bucket
    buckets: dict[str, list] = {b: [] for b in BUCKET_ORDER}
    for p in all_picks:
        b = p.get("bucket", BUCKET_CAUTION)
        buckets.setdefault(b, []).append(p)

    # sort within buckets
    for b in buckets:
        buckets[b].sort(key=lambda r: -r.get("avg_p", 0))

    # print
    title = ", ".join(days) if days else date.today().isoformat()
    print_buckets(buckets, title_date=title)

    # summary
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

    # Write exactly the picks requested by this invocation.  Do not merge with
    # an existing picks_today.json: stale target/future rows can re-enter human
    # reports and Supabase sync as duplicate operational picks.
    final_picks = all_picks

    # Write JSON
    _json_path = ROOT / "localdata" / "picks_today.json"
    _json_path.parent.mkdir(parents=True, exist_ok=True)
    _json_path.write_text(json.dumps(final_picks, indent=2))


if __name__ == "__main__":
    main()
