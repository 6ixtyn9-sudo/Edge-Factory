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
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.util import norm_team
from edgefactory.market_registry import get_odds_tier
from edgefactory.assay import weighted_consensus_score

EDGES_PATH = ROOT / "localdata" / "edges_consensus.json"
PURITY_PATH = ROOT / "localdata" / "purity_registry.json"
LOCALDATA = ROOT / "localdata"
BZZOIRO_ODDS_SOURCE = "bzzoiro_odds"

# Odds feeds and prediction feeds sometimes use different country/team labels.
# Keep this local to odds matching so certified mining/team joins remain unchanged.
ODDS_TEAM_ALIASES = {
    "caboverde": "capeverde",  # bzzoiro: Cabo Verde; prediction feeds: Cape Verde Islands
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
    BUCKET_WL_ODDS: "WATCHLIST — NO ODDS",
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


_QUALIFIED_TOKENS = ("min_p", "home-only", "away-only", "odds-", "bc-confirms")

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


def lookup_context(purity: dict, pick: dict) -> dict:
    """Build context keys and return verdicts plus raw diagnostics."""
    ctx = purity.get("contexts", {}) if purity else {}
    league_ctx = ctx.get("league", {})
    team_ctx = ctx.get("team", {})
    odds_ctx = ctx.get("odds_band", {})

    sport = pick.get("sport", "soccer")
    league = pick.get("league") or "UNKNOWN"
    market = pick.get("market", "1x2")
    rule = pick.get("edge_rule") or pick.get("rule", "?")
    sel = pick.get("pick", "?")

    home = pick.get("home", "")
    away = pick.get("away", "")
    home_norm = norm_team(home)
    away_norm = norm_team(away)

    league_key = f"{sport}|{league}|{market}|{rule}|{sel}"
    league_v = league_ctx.get(league_key, {}).get("verdict", "UNKNOWN")

    team_h_key = f"{sport}|{home_norm}|{league}|{market}|home"
    team_a_key = f"{sport}|{away_norm}|{league}|{market}|away"
    team_h_v = team_ctx.get(team_h_key, {}).get("verdict", "UNKNOWN")
    team_a_v = team_ctx.get(team_a_key, {}).get("verdict", "UNKNOWN")

    odds = pick.get("odds")
    band = odds_band(odds)
    odds_key = f"{sport}|{market}|{rule}|{band}"
    odds_v = odds_ctx.get(odds_key, {}).get("verdict", "UNKNOWN")

    return {
        "league": league_v,
        "team_h": team_h_v,
        "team_a": team_a_v,
        "odds_band": odds_v,
        "league_raw": league,
        "home_norm": home_norm,
        "away_norm": away_norm,
        "odds_band_name": band,
        "_keys": {
            "league": league_key,
            "team_h": team_h_key,
            "team_a": team_a_key,
            "odds_band": odds_key,
        }
    }


def bucket_pick(pick: dict, ctx: dict, edge_status: str = "certified",
                decay_verdict: str = "HEALTHY") -> str:
    """Bucket pick (unchanged top-level logic)."""
    if edge_status == "benched":
        return BUCKET_SKIP_DEAD
    if decay_verdict in ("DEAD", "DECAYING"):
        return BUCKET_SKIP_DEAD
    if "VETO" in (ctx.get("league"), ctx.get("team_h"), ctx.get("team_a"), ctx.get("odds_band")):
        return BUCKET_SKIP_VETO
    if pick.get("odds") is None:
        return BUCKET_WL_ODDS
    if ctx.get("league") == "UNKNOWN":
        return BUCKET_WL_CTX
    vals = [ctx.get("league"), ctx.get("team_h"), ctx.get("team_a"), ctx.get("odds_band")]
    if "CAUTION" in vals:
        return BUCKET_CAUTION
    return BUCKET_CERTIFIED


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
            k = (norm_team(home), norm_team(away))
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


def odds_team_key(name: object) -> str:
    """Team key for odds enrichment only; does not affect certified mining joins."""
    key = norm_team(str(name or ""))
    return ODDS_TEAM_ALIASES.get(key, key)


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


def bzzoiro_odds_index(
    day: str,
    *,
    live: bool = True,
    stats: dict | None = None,
) -> dict[tuple[str, str, str, str, str], dict]:
    """Best available bzzoiro_odds row per date/team/market/selection.

    Cache-first: if localdata/bzzoiro_odds_YYYY-MM.csv.gz has rows for `day`,
    do not hit the API again unless BZZOIRO_ODDS_REFRESH=1. This keeps nightly
    output clean because capture_daily already refreshed the odds cache.
    """
    cached_rows = _read_cached_bzzoiro_odds(day)
    live_rows: list[dict] = []
    if live and (_refresh_bzzoiro_odds() or not cached_rows):
        live_rows = _fetch_live_bzzoiro_odds(day)

    rows = cached_rows + live_rows
    out: dict[tuple[str, str, str, str, str], dict] = {}
    valid_rows = 0
    for row in rows:
        odds = _valid_decimal_odds(row.get("odds"))
        if odds is None:
            continue
        key = _odds_row_key(row)
        if key is None:
            continue
        valid_rows += 1
        normalized = dict(row)
        normalized["odds"] = odds
        if _prefer_odds_row(normalized, out.get(key)):
            out[key] = normalized

    if stats is not None:
        stats.update({
            "cached_rows": len(cached_rows),
            "live_rows": len(live_rows),
            "raw_rows": len(rows),
            "valid_rows": valid_rows,
            "valid_keys": len(out),
            "refreshed": bool(live_rows),
        })
    return out


def enrich_with_bzzoiro_odds(picks: list[dict], odds_index: dict) -> int:
    """Prefer matching bzzoiro real-book odds before purity bucketing.

    If a matching bzzoiro_odds row exists, use it even when Forebet supplied a
    price, because real book prices are the operational price source. If no row
    matches, keep the existing Forebet price or leave the pick as no-odds.
    """
    enriched = 0
    for pick in picks:
        key = (
            str(pick.get("date") or ""),
            odds_team_key(pick.get("home") or ""),
            odds_team_key(pick.get("away") or ""),
            str(pick.get("market") or ""),
            str(pick.get("pick") or ""),
        )
        row = odds_index.get(key)
        if not row:
            if pick.get("odds") is not None:
                pick.setdefault("odds_source", "forebet_best")
            else:
                pick.setdefault("odds_source", None)
            continue
        previous_odds = pick.get("odds")
        previous_source = pick.get("odds_source") or ("forebet_best" if previous_odds is not None else None)
        pick["odds"] = _valid_decimal_odds(row.get("odds"))
        pick["odds_source"] = BZZOIRO_ODDS_SOURCE
        pick["bookmaker"] = row.get("bookmaker")
        pick["odds_captured_at"] = row.get("captured_at")
        pick["odds_league"] = row.get("league")
        if previous_odds is not None and previous_source != BZZOIRO_ODDS_SOURCE:
            pick["odds_replaced"] = {"source": previous_source, "odds": previous_odds}
        enriched += 1
    return enriched


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
        avg_p = mean(ps) * 100.0

        # Weighted consensus score — uses per-source Wilson LB as vote weight.
        # Falls back to uniform weights (lb=1.0 each) if no weights loaded.
        votes = [(sel, source_weights.get(s, 1.0)) for s, sel in zip(used, sels)]
        _, w_score, _ = weighted_consensus_score(votes)

        if avg_p < thr:
            continue
        fb = data.get("forebet", {}).get(k) or {}
        zb = data.get("zulubet", {}).get(k) or {}
        bz = data.get("bzzoiro", {}).get(k) or {}
        vb = data.get("vitibet", {}).get(k) or {}
        anchor = fb or next(data[s][k] for s in used if k in data.get(s, {}))
        sel = sels[0]
        # Cascade: forebet best-odds → zulubet odds → None (bzzoiro_odds enriched later)
        _odds_map = {"home": "odd1", "draw": "oddx", "away": "odd2"}
        _col = _odds_map[sel]
        odds = _f(fb.get(_col)) or _f(zb.get(_col)) or None
        odds_src = ("forebet_best" if _f(fb.get(_col)) is not None
                    else "zulubet" if _f(zb.get(_col)) is not None
                    else None)
        home = anchor.get("home")
        away = anchor.get("away")
        picks.append({
            "date": day, "market": "1x2",
            "match": f"{home} vs {away}",
            "home": home, "away": away,
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
        if len(used) < max(2, n_req):
            continue
        if len(set(sels)) > 1:
            continue
        avg_p = mean(confs) * 100.0
        if avg_p < thr:
            continue
        fb = data.get("forebet", {}).get(k) or {}
        bz = data.get("bzzoiro", {}).get(k) or {}
        anchor = fb or next(data[s][k] for s in used if k in data.get(s, {}))
        sel = sels[0]
        odds = _f(fb.get(outcome_odds[sel])) if fb else None
        home = anchor.get("home")
        away = anchor.get("away")
        picks.append({
            "date": day, "market": market,
            "match": f"{home} vs {away}",
            "home": home, "away": away,
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
    return picks, vetoes, n_up


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
                o = "@None"
            ctx = p.get("ctx", {})
            ctx_str = (
                f"  league={ctx.get('league_raw','UNKNOWN')}:{ctx.get('league','?')}  "
                f"team={ctx.get('home_norm','?')}:{ctx.get('team_h','?')}/"
                f"{ctx.get('away_norm','?')}:{ctx.get('team_a','?')}  "
                f"odds_band={ctx.get('odds_band_name','?')}:{ctx.get('odds_band','?')}"
            )
            market = p.get("market_type", p.get("market", "?"))
            tier = p.get("odds_tier", "?")
            label = p.get("display_rule") or p.get("rule", "?")
            w_str = f"  w={p['w_score']:.2f}" if p.get("w_score") is not None else ""
            print(f"  [{label}] {p['match'][:45]:45s} -> {p['pick'].upper():5s}  avg {p['avg_p']:.0f}%{w_str} {o}  [{market}/{tier}]")
            if ctx:
                print(ctx_str)
        print()
    print("⚠️  Flat stakes only. Best odds inflate ROI (~halve it).")
    print("⚠️  Bet only what you can afford to lose.")


def main():
    days = sys.argv[1:] or [
        date.today().isoformat(),
        (date.today() + timedelta(days=1)).isoformat(),
    ]
    t1x2, ou_edge, btts_edge, fallback = load_thresholds()
    edge_meta = load_edge_meta()
    purity = load_purity()
    purity_missing = not bool(purity)

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
        picks, vetoes, n_up = run_day(day, t1x2, ou_edge, btts_edge,
                                      source_weights_1x2=source_weights_1x2)
        total_vetoes += vetoes
        total_upcoming += n_up

        odds_stats: dict = {}
        odds_idx = bzzoiro_odds_index(day, stats=odds_stats)
        enriched_n = enrich_with_bzzoiro_odds(picks, odds_idx)
        if odds_stats.get("raw_rows") or enriched_n:
            print(
                f"bzzoiro_odds enrichment {day}: "
                f"cached_rows={odds_stats.get('cached_rows', 0)} "
                f"live_rows={odds_stats.get('live_rows', 0)} "
                f"valid_keys={odds_stats.get('valid_keys', len(odds_idx))} "
                f"enriched={enriched_n}",
                file=sys.stderr,
            )

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

        all_picks.extend(picks)

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

    # Write JSON
    _json_path = ROOT / "localdata" / "picks_today.json"
    _json_path.parent.mkdir(parents=True, exist_ok=True)
    _json_path.write_text(json.dumps(all_picks, indent=2))


if __name__ == "__main__":
    main()
