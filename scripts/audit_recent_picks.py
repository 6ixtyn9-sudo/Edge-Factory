#!/usr/bin/env python3
"""Audit recent archived daily picks against settled warehouse results."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
WAREHOUSE = LOCALDATA / "warehouse.duckdb"
DEFAULT_LOCAL_TZ = "Africa/Johannesburg"

import sys
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import canonical_team  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402


@dataclass
class SettledPick:
    date: str
    rule_name: str
    bucket: str
    odds_source: str
    odds_match_method: str
    market: str
    pick: str
    outcome: str
    won: bool
    odds: float | None
    pnl: float | None


def local_today() -> str:
    try:
        return datetime.now(ZoneInfo(DEFAULT_LOCAL_TZ)).date().isoformat()
    except Exception:
        return date.today().isoformat()


def daterange(start: str, end: str):
    d = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    while d <= e:
        yield d.isoformat()
        d += timedelta(days=1)


def archived_picks_path(day: str) -> Path:
    # Prefer the immutable morning snapshot. The regular picks file may be
    # replaced by later forecast reruns and would introduce state drift.
    morning = LOCALDATA / f"picks_morning_{day}.json"
    if morning.exists():
        return morning
    return LOCALDATA / f"picks_{day}.json"


def load_archived_picks(start: str, end: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for day in daterange(start, end):
        path = archived_picks_path(day)
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for row in data:
            if isinstance(row, dict):
                row = dict(row)
                row.setdefault("date", day)
                out.append(row)
    return out


def dedupe_archived_picks(picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate frozen pick rows without replacing them with later state.

    The first row from the selected frozen snapshot is authoritative. Do not
    choose by statistical sample size, because that can replace pick-time
    stats with a later regenerated state.
    """
    best: dict[tuple, dict[str, Any]] = {}
    for p in picks:
        home = norm_team(p.get("home") or "")
        away = norm_team(p.get("away") or "")
        day = str(p.get("date") or "")[:10]
        market = str(p.get("market") or "")
        sel = str(p.get("pick") or "")
        if not (home and away):
            continue
        key = (day, home, away, market, sel)

        comment = p.get("statistical_comment") or ""
        mu = re.search(r"n=(\d+)", comment)
        n_current = int(mu.group(1)) if mu else 0

        existing = best.get(key)
        if existing:
            # Preserve the first archived pick-time row. Never replace it with
            # a later row merely because it has a larger stats sample.
            continue

        if existing:
            e_comment = existing.get("statistical_comment") or ""
            e_mu = re.search(r"n=(\d+)", e_comment)
            n_existing = int(e_mu.group(1)) if e_mu else 0
            if n_current <= n_existing:
                continue

        best[key] = p

    return list(best.values())


def _dedupe_keys(keys: list[str]) -> list[str]:
    out: list[str] = []
    for key in keys:
        key = str(key or "")
        if key and key not in out:
            out.append(key)
    return out


def char_ngram_similarity(s1: str, s2: str, n: int = 2) -> float:
    def get_ngrams(s: str) -> set[str]:
        clean = re.sub(r"[^a-z0-9]", "", s.lower())
        return {clean[i : i + n] for i in range(len(clean) - n + 1)} if len(clean) >= n else set()

    g1 = get_ngrams(s1)
    g2 = get_ngrams(s2)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)


def audit_team_key_candidates(raw: object) -> list[str]:
    text = str(raw or "")
    keys = [norm_team(text)]
    try:
        canon = canonical_team(text)
        keys.append(norm_team(canon))
        _DISAMBIG = {
            "launcesto": 14,
        }
        base9 = norm_team(text)
        if base9 in _DISAMBIG:
            keys.append(norm_team(canon, width=_DISAMBIG[base9]))
    except Exception:
        pass

    manual: dict[str, list[str]] = {
        "kpvj": ["kpvkokkol"],
        "kpvjk": ["kpvkokkol"],
        "guangzhou": ["guangdong"],
        "hebeikung": ["shijiazhu", "poweshiji"],
        "meizhouke": ["meizhouwu", "meizhouha"],
        "fcdunavru": ["dunavruse"],
        "csvolunta": ["voluntari"],
        "rfs": ["rigasfs"],
        "rigasfutb": ["rigasfs"],
        "rgasfs": ["rigasfs"],
        "fktukums": ["tukums"],
        "tukumsii": ["tukums"],
        "rigaii": ["rigafcii"],
        "valmierab": ["valmiera"],
        "neftchi": ["neftchife"],
        "dila": ["dilagori"],
    }
    base = norm_team(text)
    if base in manual:
        keys.extend(manual[base])

    return _dedupe_keys(keys)


def _pick_diag(pick: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "date": str(pick.get("date") or "")[:10],
        "match": pick.get("match") or f"{pick.get('home')} vs {pick.get('away')}",
        "home": pick.get("home"),
        "away": pick.get("away"),
        "league": pick.get("league"),
        "rule": pick.get("edge_rule") or pick.get("rule") or pick.get("display_rule"),
        "bucket": pick.get("bucket"),
        "pick": pick.get("pick"),
        "odds": pick.get("odds"),
        "reason": reason,
        "home_key_candidates": audit_team_key_candidates(pick.get("home")),
        "away_key_candidates": audit_team_key_candidates(pick.get("away")),
    }


def load_results_index(warehouse_path: Path) -> tuple[dict[tuple[str, str, str], dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    import duckdb

    from edgefactory.util import norm_team_sql

    if not warehouse_path.exists():
        raise FileNotFoundError(f"warehouse not found: {warehouse_path}")

    con = duckdb.connect(str(warehouse_path), read_only=True)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    candidates = [
        (1, "forebet_settled"),
        (2, "bettingclosed_settled"),
        (3, "zulubet_settled"),
        (4, "statarea_settled"),
        (5, "scoutingstats_settled"),
        (6, "vitibet_settled"),
    ]
    active = [(prio, name) for prio, name in candidates if name in tables]
    if not active:
        return {}, {}

    nh9, na9 = norm_team_sql("home", 9), norm_team_sql("away", 9)
    nh14, na14 = norm_team_sql("home", 14), norm_team_sql("away", 14)

    union_sql = " UNION ALL ".join(
        f"SELECT {prio} AS prio, date, home, away, "
        f"{nh9} AS hkey, {na9} AS akey, "
        f"{nh14} AS hkey14, {na14} AS akey14, "
        f"hs, gs, outcome FROM {name} "
        f"WHERE hs IS NOT NULL AND gs IS NOT NULL"
        for prio, name in active
    )
    sql = f"""
    WITH all_results AS (
      {union_sql}
    ), ranked AS (
      SELECT *,
             ROW_NUMBER() OVER (PARTITION BY date, hkey, akey, hkey14, akey14 ORDER BY prio) AS rn
      FROM all_results
    )
    SELECT date, hkey, akey, hkey14, akey14, hs, gs, outcome, home, away
    FROM ranked
    WHERE rn = 1
    """
    rows = con.execute(sql).fetchall()
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    results_by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for day, hkey, akey, hkey14, akey14, hs, gs, outcome, home, away in rows:
        entry = {"hs": int(hs), "gs": int(gs), "outcome": str(outcome), "home": str(home), "away": str(away)}
        d = str(day)[:10]
        # 9-char key (legacy)
        index[(d, str(hkey), str(akey))] = entry
        # 14-char key (disambiguation)
        if str(hkey14) != str(hkey) or str(akey14) != str(akey):
            index[(d, str(hkey14), str(akey14))] = entry
            
        results_by_date[d].append(entry)

    return index, results_by_date


def find_fuzzy_result_match(pick_home: str, pick_away: str, results_on_date: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Fall back to character bigram Jaccard similarity of combined Event string when key mapping fails."""
    pick_str = f"{pick_home} {pick_away}"
    best_match = None
    best_sim = 0.0
    for res in results_on_date:
        res_str = f"{res['home']} {res['away']}"
        sim = char_ngram_similarity(pick_str, res_str, n=2)
        if sim >= 0.40 and sim > best_sim:
            best_sim = sim
            best_match = res
    return best_match


def settle_pick(pick: dict[str, Any], result: dict[str, Any] | None) -> SettledPick | None:
    if not result:
        return None
    market = str(pick.get("market") or "")
    selection = str(pick.get("pick") or "")
    outcome = str(result.get("outcome") or "")
    if market != "1x2":
        return None
    if selection not in {"home", "draw", "away"}:
        return None
    won = selection == outcome
    odds_value = pick.get("odds")
    try:
        odds = float(odds_value) if odds_value not in (None, "") else None
    except (TypeError, ValueError):
        odds = None
    pnl = None if odds is None else (odds - 1.0 if won else -1.0)
    return SettledPick(
        date=str(pick.get("date") or "")[:10],
        rule_name=str(pick.get("edge_rule") or pick.get("rule") or pick.get("display_rule") or "UNKNOWN"),
        bucket=str(pick.get("bucket") or "UNKNOWN"),
        odds_source=str(pick.get("odds_source") or "UNKNOWN"),
        odds_match_method=str(pick.get("odds_match_method") or "UNKNOWN"),
        market=market,
        pick=selection,
        outcome=outcome,
        won=won,
        odds=odds,
        pnl=pnl,
    )


def summarize_scored(rows: list[SettledPick]) -> dict[str, Any]:
    settled = len(rows)
    wins = sum(1 for row in rows if row.won)
    with_odds = [row for row in rows if row.pnl is not None]
    pnl_sum = sum(float(row.pnl or 0.0) for row in with_odds)
    return {
        "settled_picks": settled,
        "wins": wins,
        "hit_rate": round(wins / settled, 6) if settled else None,
        "priced_picks": len(with_odds),
        "roi": round(pnl_sum / len(with_odds), 6) if with_odds else None,
    }


def summarize_by(rows: list[SettledPick], attr: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[SettledPick]] = defaultdict(list)
    for row in rows:
        grouped[str(getattr(row, attr) or "UNKNOWN")].append(row)
    return {name: summarize_scored(group_rows) for name, group_rows in sorted(grouped.items())}


def parse_statistical_comment(comment: str) -> dict[str, Any]:
    out = {
        "over25": None,
        "btts": None,
        "home_o15": None,
        "away_o15": None,
        "top_scores": []
    }
    if not comment:
        return out
        
    m_o25 = re.search(r"Over 2.5:\s*([\d.]+)%", comment)
    if m_o25:
        out["over25"] = float(m_o25.group(1)) / 100.0
        
    m_btts = re.search(r"BTTS:\s*([\d.]+)%", comment)
    if m_btts:
        out["btts"] = float(m_btts.group(1)) / 100.0
        
    m_h_o15 = re.search(r"Home Over 1.5 Goals:\s*([\d.]+)%", comment)
    if m_h_o15:
        out["home_o15"] = float(m_h_o15.group(1)) / 100.0
        
    m_a_o15 = re.search(r"Away Over 1.5 Goals:\s*([\d.]+)%", comment)
    if m_a_o15:
        out["away_o15"] = float(m_a_o15.group(1)) / 100.0
        
    m_scores = re.search(r"Top Scores:\s*(.*)", comment)
    if m_scores:
        scores_str = m_scores.group(1)
        parts = scores_str.split(",")
        for part in parts:
            part = part.strip()
            m = re.match(r"(\d+-\d+)\s*\(([\d.]+)%\)", part)
            if m:
                out["top_scores"].append({
                    "score": m.group(1),
                    "pct": float(m.group(2)) / 100.0
                })
    return out


def check_enhancement_hit(enh_type: str, selection: str, hs: int, gs: int) -> bool | None:
    if hs is None or gs is None:
        return None
    sel = selection.lower()
    if enh_type == "match_over_15":
        hit = (hs + gs) >= 2
        if sel == "home": return hit and (hs > gs)
        if sel in ["away", "2"]: return hit and (gs > hs)
        return hit
    elif enh_type == "match_over_25":
        hit = (hs + gs) >= 3
        if sel == "home": return hit and (hs > gs)
        if sel in ["away", "2"]: return hit and (gs > hs)
        return hit
    elif enh_type == "match_under_15":
        return (hs + gs) <= 1
    elif enh_type == "match_under_25":
        return (hs + gs) <= 2
    elif enh_type == "match_under_35":
        return (hs + gs) <= 3
    elif enh_type == "btts_yes":
        hit = (hs > 0 and gs > 0)
        if sel == "home": return hit and (hs > gs)
        if sel in ["away", "2"]: return hit and (gs > hs)
        return hit
    elif enh_type == "btts_no":
        return hs == 0 or gs == 0
    elif enh_type in ("team_over_05", "home_over_05"):
        return hs >= 1 if (enh_type == "home_over_05" or sel == "home") else gs >= 1
    elif enh_type in ("team_over_15", "home_over_15"):
        return hs >= 2 if (enh_type == "home_over_15" or sel == "home") else gs >= 2
    elif enh_type == "home_over_25":
        return hs >= 3
    elif enh_type == "home_over_35":
        return hs >= 4
    elif enh_type == "home_over_45":
        return hs >= 5
    elif enh_type == "home_under_05":
        return hs == 0
    elif enh_type == "home_under_15":
        return hs <= 1
    elif enh_type == "home_under_25":
        return hs <= 2
    elif enh_type == "home_under_35":
        return hs <= 3
    elif enh_type == "home_under_45":
        return hs <= 4
    elif enh_type == "away_over_05":
        return gs >= 1
    elif enh_type == "away_over_15":
        return gs >= 2
    elif enh_type == "away_over_25":
        return gs >= 3
    elif enh_type == "away_over_35":
        return gs >= 4
    elif enh_type == "away_over_45":
        return gs >= 5
    elif enh_type == "away_under_05":
        return gs == 0
    elif enh_type == "away_under_15":
        return gs <= 1
    elif enh_type == "away_under_25":
        return gs <= 2
    elif enh_type == "away_under_35":
        return gs <= 3
    elif enh_type == "away_under_45":
        return gs <= 4
    elif enh_type == "goal_range_0_1":
        return (hs + gs) in [0, 1]
    elif enh_type == "goal_range_2_3":
        return (hs + gs) in [2, 3]
    elif enh_type == "goal_range_4_5":
        return (hs + gs) in [4, 5]
    elif enh_type == "goal_range_4_6":
        return (hs + gs) in [4, 5, 6]
    elif enh_type == "goal_range_6_plus":
        return (hs + gs) >= 6
    elif enh_type == "goal_range_7_plus":
        return (hs + gs) >= 7
    elif enh_type == "exact_0":
        return (hs + gs) == 0
    elif enh_type == "exact_1":
        return (hs + gs) == 1
    elif enh_type == "exact_2":
        return (hs + gs) == 2
    elif enh_type == "exact_3":
        return (hs + gs) == 3
    elif enh_type == "exact_4":
        return (hs + gs) == 4
    elif enh_type == "exact_5":
        return (hs + gs) == 5
    elif enh_type == "match_over_05":
        return (hs + gs) >= 1
    elif enh_type == "match_over_35":
        return (hs + gs) >= 4
    elif enh_type == "match_over_45":
        return (hs + gs) >= 5
    elif enh_type == "match_over_55":
        return (hs + gs) >= 6
    elif enh_type == "match_under_05":
        return (hs + gs) == 0
    elif enh_type == "match_under_45":
        return (hs + gs) <= 4
    elif enh_type == "match_under_55":
        return (hs + gs) <= 5
    elif enh_type == "double_chance":
        if sel == "home": # 1X
            return hs >= gs
        elif sel == "away": # X2
            return gs >= hs
        elif sel == "draw": # 12
            return hs != gs
    return None


def build_report(start: str, end: str, warehouse_path: Path, *, include_same_day: bool = False) -> dict[str, Any]:
    picks = load_archived_picks(start, end)
    picks = dedupe_archived_picks(picks)
    results, results_by_date = load_results_index(warehouse_path)
    settled_rows: list[SettledPick] = []
    archived_dates = sorted({str(p.get("date") or "")[:10] for p in picks if p.get("date")})
    today_local = local_today()
    same_day_excluded = 0
    eligible_prior_picks = 0
    unmatched_result_examples: list[dict[str, Any]] = []
    ambiguous_result_examples: list[dict[str, Any]] = []

    # Dynamic Secondary Market realized stats counters
    sec_stats = {
        "over25_wins": 0, "over25_total": 0,
        "btts_wins": 0, "btts_total": 0,
        "team_o15_wins": 0, "team_o15_total": 0,
    }

    # Dynamic Enhancement Auditing counters
    enh_stats = {
        "total_recommended": 0,
        "total_hits": 0,
        "by_enhancement": defaultdict(lambda: {"recommended": 0, "hits": 0,
                                               "priced_n": 0, "priced_hits": 0,
                                               "priced_profit": 0.0})
    }
    priced_outcomes: list[dict] = []  # settled outcomes with REAL captured prices (registry feed)

    # RT-1 (red-team 2026-08-03): enhancement scoring must read prices from the
    # IMMUTABLE capture store (localdata/theoddsapi_odds_YYYY-MM.csv.gz), never
    # from archived pick fields. Morning snapshots are frozen before the close
    # capture exists, and the intraday ledger merge retains locked picks verbatim
    # (anti-drift), so archived enhancement_price fields can never carry the close
    # price — scoring off them would starve the registry. Probing raw capture rows
    # per pick-date yields one consistent definition for every metric below and
    # for the registry: best captured theoddsapi price for (date, pair, market).
    try:
        from edgefactory import enh_pricing as _enh_pricing
    except Exception:
        _enh_pricing = None
    _prices_by_day: dict[str, dict] = {}

    # Detailed ledger of settled picks and their granular expectations audits
    settled_ledger = []

    for pick in picks:
        pick_date = str(pick.get("date") or "")[:10]
        if not include_same_day and pick_date >= today_local:
            same_day_excluded += 1
            continue
        market = str(pick.get("market") or "")
        selection = str(pick.get("pick") or "")
        if market != "1x2" or selection not in {"home", "draw", "away"}:
            continue
        eligible_prior_picks += 1

        result = None
        matched_keys: list[tuple[str, str, str]] = []
        for hk in audit_team_key_candidates(pick.get("home")):
            for ak in audit_team_key_candidates(pick.get("away")):
                key = (pick_date, hk, ak)
                candidate = results.get(key)
                if candidate is not None:
                    result = candidate
                    matched_keys.append(key)

        if len(matched_keys) > 1:
            seen = set()
            for key in matched_keys:
                r = results.get(key) or {}
                seen.add((r.get("hs"), r.get("gs"), r.get("outcome")))
            if len(seen) > 1:
                ambiguous_result_examples.append(_pick_diag(pick, "ambiguous_alias_result"))
                continue

        if result is None:
            results_on_date = results_by_date.get(pick_date, [])
            fuzzy_candidate = find_fuzzy_result_match(pick.get("home", ""), pick.get("away", ""), results_on_date)
            if fuzzy_candidate is not None:
                result = fuzzy_candidate
            else:
                unmatched_result_examples.append(_pick_diag(pick, "unmatched_result"))
                continue

        settled = settle_pick(pick, result)
        if settled is not None:
            settled_rows.append(settled)
            
            # Score secondary markets on this settled match
            hs = result.get("hs")
            gs = result.get("gs")
            if hs is not None and gs is not None:
                # 1. Over 2.5 goals
                sec_stats["over25_total"] += 1
                if hs + gs >= 3:
                    sec_stats["over25_wins"] += 1
                    
                # 2. Both teams to score
                sec_stats["btts_total"] += 1
                if hs > 0 and gs > 0:
                    sec_stats["btts_wins"] += 1
                    
                # 3. Selected team over 1.5 goals
                if selection in ("home", "away"):
                    sec_stats["team_o15_total"] += 1
                    selected_goals = hs if selection == "home" else gs
                    if selected_goals >= 2:
                        sec_stats["team_o15_wins"] += 1

                # 4. Recommended enhancement hit check
                enh_type = pick.get("recommended_enhancement")
                if enh_type:
                    hit = check_enhancement_hit(enh_type, selection, hs, gs)
                    if hit is not None:
                        enh_stats["total_recommended"] += 1
                        if hit:
                            enh_stats["total_hits"] += 1
                        
                        slot = enh_stats["by_enhancement"][enh_type]
                        slot["recommended"] += 1
                        if hit:
                            slot["hits"] += 1
                        # Price from the immutable capture store (RT-1 above), not
                        # from the archived presentation-time field.
                        price = None
                        price_source = ""
                        if _enh_pricing is not None and pick_date:
                            if pick_date not in _prices_by_day:
                                _prices_by_day[pick_date] = _enh_pricing.load_prices_index(ROOT, pick_date)
                            probe = {"home": pick.get("home"), "away": pick.get("away"),
                                     "recommended_enhancement": enh_type}
                            _enh_pricing.attach_enhancement_price(probe, _prices_by_day[pick_date])
                            price = probe.get("enhancement_price")
                            price_source = probe.get("enhancement_price_source") or ""
                        if (isinstance(price, (int, float)) and not isinstance(price, bool)
                                and math.isfinite(price) and price > 1.0):
                            slot["priced_n"] += 1
                            if hit:
                                slot["priced_hits"] += 1
                            slot["priced_profit"] += (price - 1.0) if hit else -1.0
                            priced_outcomes.append({
                                "date": str(pick_date), "match": pick.get("match") or "",
                                "market": enh_type, "price": float(price), "hit": bool(hit),
                                "source": price_source,
                            })

                # 5. Granular expectations audit ledger populator
                comment = pick.get("statistical_comment")
                parsed_stats = parse_statistical_comment(comment)
                
                o25_hit = None
                if parsed_stats["over25"] is not None:
                    o25_hit = (hs + gs) >= 3
                    
                btts_hit = None
                if parsed_stats["btts"] is not None:
                    expected_btts_yes = parsed_stats["btts"] >= 50.0
                    actual_btts_yes = hs > 0 and gs > 0
                    btts_hit = actual_btts_yes if expected_btts_yes else not actual_btts_yes
                    
                home_o15_hit = None
                if parsed_stats["home_o15"] is not None:
                    expected_over = parsed_stats["home_o15"] >= 0.50
                    actual_over = hs >= 2
                    home_o15_hit = actual_over if expected_over else not actual_over
                    
                away_o15_hit = None
                if parsed_stats["away_o15"] is not None:
                    expected_over = parsed_stats["away_o15"] >= 0.50
                    actual_over = gs >= 2
                    away_o15_hit = actual_over if expected_over else not actual_over
                    
                top_scores_audited = []
                for item in parsed_stats["top_scores"]:
                    actual_score = f"{hs}-{gs}"
                    hit = item["score"] == actual_score
                    top_scores_audited.append({
                        "score": item["score"],
                        "pct": item["pct"],
                        "hit": hit
                    })
                    
                actual_outcome = result.get("outcome") or ""
                settled_ledger.append({
                    "date": pick_date,
                    "match": pick.get("match") or f"{pick.get('home')} vs {pick.get('away')}",
                    "selection": selection,
                    "avg_p": pick.get("avg_p") or 0.0,
                    "hs": hs,
                    "gs": gs,
                    "outcome": actual_outcome,
                    "won": selection == actual_outcome,
                    "odds": pick.get("odds"),
                    "parsed_stats": {
                        "over25_expected": parsed_stats["over25"],
                        "over25_hit": o25_hit,
                        "btts_expected": parsed_stats["btts"],
                        "btts_hit": btts_hit,
                        "home_o15_expected": parsed_stats["home_o15"],
                        "home_o15_hit": home_o15_hit,
                        "away_o15_expected": parsed_stats["away_o15"],
                        "away_o15_hit": away_o15_hit,
                        "top_scores": top_scores_audited
                    }
                })

    serialized_by_enhancement = {}
    for enh, stats in enh_stats["by_enhancement"].items():
        rec = stats["recommended"]
        hits = stats["hits"]
        p_n = stats.get("priced_n", 0)
        p_profit = stats.get("priced_profit", 0.0)
        serialized_by_enhancement[enh] = {
            "recommended": rec,
            "hits": hits,
            "hit_rate": round(hits / rec, 6) if rec else 0.0,
            "priced_n": p_n,
            "priced_hits": stats.get("priced_hits", 0),
            "priced_roi": round(p_profit / p_n, 6) if p_n else None,
        }

    serialized_enh_audit = {
        "total_recommended": enh_stats["total_recommended"],
        "total_hits": enh_stats["total_hits"],
        "hit_rate": round(enh_stats["total_hits"] / enh_stats["total_recommended"], 6) if enh_stats["total_recommended"] else None,
        "by_enhancement": serialized_by_enhancement
    }

    # Enhancement certification registry: feed priced settled outcomes (idempotent,
    # fail-soft) and snapshot states for the report. Unpriced outcomes never advance
    # certification — probability without price is not evidence of value.
    registry_states: dict[str, str] = {}
    try:
        from edgefactory.enh_registry import all_statuses, record_outcome
        for oc in priced_outcomes:
            record_outcome(ROOT, date_=oc["date"], match=oc["match"], market=oc["market"],
                           price=oc["price"], hit=oc["hit"], source=oc["source"])
        registry_states = all_statuses(ROOT)
    except Exception:
        registry_states = {}

    return {
        "start": start,
        "end": end,
        "archived_pick_rows": len(picks),
        "archived_pick_dates": archived_dates,
        "same_day_excluded": same_day_excluded,
        "same_day_cutoff": today_local,
        "include_same_day": include_same_day,
        "eligible_prior_picks": eligible_prior_picks,
        "unmatched_result_picks": len(unmatched_result_examples),
        "ambiguous_result_picks": len(ambiguous_result_examples),
        "unmatched_examples": unmatched_result_examples[:50],
        "ambiguous_examples": ambiguous_result_examples[:50],
        "overall": summarize_scored(settled_rows),
        "by_rule": summarize_by(settled_rows, "rule_name"),
        "by_bucket": summarize_by(settled_rows, "bucket"),
        "by_odds_source": summarize_by(settled_rows, "odds_source"),
        "by_odds_match_method": summarize_by(settled_rows, "odds_match_method"),
        "secondary_stats": sec_stats,
        "enhancements_audit": serialized_enh_audit,
        "enhancement_registry": registry_states,
        "settled_ledger": settled_ledger,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    overall = report.get("overall", {})
    lines = [
        f"# Edge Factory — Recent picks audit ({report['start']} to {report['end']})",
        "",
        "## Overall",
        "",
        f"- archived pick rows: {report.get('archived_pick_rows', 0)}",
        f"- archived pick dates: {len(report.get('archived_pick_dates', []))}",
        f"- settled picks: {overall.get('settled_picks', 0)}",
        f"- eligible prior 1x2 picks: {report.get('eligible_prior_picks', 0)}",
        f"- unmatched result picks: {report.get('unmatched_result_picks', 0)}",
        f"- ambiguous result picks: {report.get('ambiguous_result_picks', 0)}",
        f"- wins: {overall.get('wins', 0)}",
        f"- hit rate: {overall.get('hit_rate')}",
        f"- priced picks: {overall.get('priced_picks', 0)}",
        f"- ROI: {overall.get('roi')}",
        "",
        "## Settlement policy",
        "",
        f"- include same-day picks: {report.get('include_same_day')}",
        f"- same-day cutoff date: {report.get('same_day_cutoff')}",
        f"- same-day rows excluded: {report.get('same_day_excluded', 0)}",
        "",
    ]
    
    # Render Secondary Market realized stats
    sec = report.get("secondary_stats", {})
    if sec and sec.get("over25_total", 0) > 0:
        over25_wins = sec.get("over25_wins", 0)
        over25_total = sec.get("over25_total", 0)
        over25_pct = over25_wins / over25_total
        
        btts_wins = sec.get("btts_wins", 0)
        btts_total = sec.get("btts_total", 0)
        btts_pct = btts_wins / btts_total
        
        team_o15_wins = sec.get("team_o15_wins", 0)
        team_o15_total = sec.get("team_o15_total", 0)
        team_o15_pct = team_o15_wins / team_o15_total
        
        lines.extend([
            "## Secondary Market Realized Rates",
            "",
            "Metrics scored against actual outcomes of the settled consensus picks in this window:",
            f"- **Over 2.5 Goals**: occurred in {over25_wins} / {over25_total} matches ({over25_pct:.1%})",
            f"- **Both Teams to Score (BTTS)**: occurred in {btts_wins} / {btts_total} matches ({btts_pct:.1%})",
            f"- **Selected Team Over 1.5 Goals**: occurred in {team_o15_wins} / {team_o15_total} matches ({team_o15_pct:.1%})",
            "",
        ])

    # Render Recommended Enhancements Audit
    enh_aud = report.get("enhancements_audit", {})
    if enh_aud and enh_aud.get("total_recommended", 0) > 0:
        total_rec = enh_aud.get("total_recommended", 0)
        total_hits = enh_aud.get("total_hits", 0)
        overall_rate = enh_aud.get("hit_rate", 0.0)
        
        lines.extend([
            "## Recommended Enhancements Audit",
            "",
            "Performance of deep context-derived recommended enhancements overlay:",
            f"- **Total Recommended Enhancements**: {total_rec}",
            f"- **Total Hits**: {total_hits}",
            f"- **Overall Hit Rate**: {overall_rate:.1%}",
            "",
            "### Breakdown by Enhancement Type:",
        ])
        by_enh = enh_aud.get("by_enhancement", {})
        if not by_enh:
            lines.append("- (none)")
        else:
            for key, summary in sorted(by_enh.items()):
                rec = summary.get("recommended", 0)
                hits = summary.get("hits", 0)
                hr = summary.get("hit_rate", 0.0)
                lines.append(f"- `{key}`: recommended={rec}, hits={hits}, hit_rate={hr:.1%}")
        lines.append("")

    lines.extend(["## By rule", ""])
    by_rule = report.get("by_rule", {})
    if not by_rule:
        lines.append("- none")
    else:
        for key, summary in by_rule.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By bucket", ""])
    by_bucket = report.get("by_bucket", {})
    if not by_bucket:
        lines.append("- none")
    else:
        for key, summary in by_bucket.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By odds source", ""])
    by_source = report.get("by_odds_source", {})
    if not by_source:
        lines.append("- none")
    else:
        for key, summary in by_source.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By odds match method", ""])
    by_method = report.get("by_odds_match_method", {})
    if not by_method:
        lines.append("- none")
    else:
        for key, summary in by_method.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    # Render Settled Picks Granular Expectations Audit Ledger
    ledger = report.get("settled_ledger", [])
    if ledger:
        lines.extend([
            "## Settled Picks Granular Expectations Audit",
            "",
            "Visual audit of expected historical stats (from the `📊` line) against actual realized scores:",
            ""
        ])
        granular_cutoff = (
            date.fromisoformat(report["end"]) - timedelta(days=1)
        ).isoformat()

        for item in sorted(ledger, key=lambda x: x["date"], reverse=True):
            if str(item.get("date") or "")[:10] < granular_cutoff:
                continue

            status = "🟢 WON" if item["won"] else "🔴 LOST"
            lines.append(f"### {item['date']}: {item['match']} (Actual Score: **{item['hs']}-{item['gs']}**)")
            lines.append(f"- **1X2 Pick**: Selected `{item['selection'].upper()}` @ {item['odds'] or 'n/a'} -> {status} (Expected prob: {item['avg_p']:.1f}%)")
            
            stats = item["parsed_stats"]
            if stats["over25_expected"] is not None:
                o25_icon = "🟢 HIT" if stats["over25_hit"] else "🔴 MISS"
                lines.append(f"  - [{o25_icon}] **Over 2.5 Goals**: expected {stats['over25_expected']:.1%} (Actual: {item['hs'] + item['gs']} goals)")
                
            if stats["btts_expected"] is not None:
                btts_icon = "🟢 HIT" if stats["btts_hit"] else "🔴 MISS"
                btts_dir = "BTTS-Yes" if stats["btts_expected"] >= 0.50 else "BTTS-No"
                actual_dir = "BTTS-Yes" if item["hs"] > 0 and item["gs"] > 0 else "BTTS-No"
                lines.append(f"  - [{btts_icon}] **{btts_dir}**: expected {stats['btts_expected']:.1%} (Actual: {actual_dir})")
                
            if stats["home_o15_expected"] is not None:
                h_o15_icon = "🟢 HIT" if stats["home_o15_hit"] else "🔴 MISS"
                if stats["home_o15_expected"] >= 0.50:
                    lines.append(f"  - [{h_o15_icon}] **Home Team Over 1.5 Goals**: expected {stats['home_o15_expected']:.1%} (Actual: {item['hs']} goals)")
                else:
                    lines.append(f"  - [{h_o15_icon}] **Home Team Under 1.5 Goals**: expected {1.0 - stats['home_o15_expected']:.1%} (Actual: {item['hs']} goals)")
                
            if stats["away_o15_expected"] is not None:
                a_o15_icon = "🟢 HIT" if stats["away_o15_hit"] else "🔴 MISS"
                if stats["away_o15_expected"] >= 0.50:
                    lines.append(f"  - [{a_o15_icon}] **Away Team Over 1.5 Goals**: expected {stats['away_o15_expected']:.1%} (Actual: {item['gs']} goals)")
                else:
                    lines.append(f"  - [{a_o15_icon}] **Away Team Under 1.5 Goals**: expected {1.0 - stats['away_o15_expected']:.1%} (Actual: {item['gs']} goals)")
                
            if stats["top_scores"]:
                scores_strs = []
                for score_item in stats["top_scores"]:
                    score_icon = "🟢 HIT" if score_item["hit"] else "🔴 MISS"
                    scores_strs.append(f"[{score_icon}] {score_item['score']} ({score_item['pct']:.1%})")
                lines.append(f"  - **Top Scores**: " + ", ".join(scores_strs))
            lines.append("")

    lines.extend(["", "## Unmatched result examples", ""])
    examples = report.get("unmatched_examples", [])
    if not examples:
        lines.append("- none")
    else:
        for ex in examples[:25]:
            lines.append(
                f"- {ex.get('date')} `{ex.get('bucket')}` `{ex.get('rule')}` — {ex.get('match')} -> {str(ex.get('pick')).upper()} @ {ex.get('odds')} ({ex.get('reason')}); keys={ex.get('home_key_candidates')}/{ex.get('away_key_candidates')}"
            )

    lines.extend(["", "## Ambiguous result examples", ""])
    amb = report.get("ambiguous_examples", [])
    if not amb:
        lines.append("- none")
    else:
        for ex in amb[:25]:
            lines.append(f"- {ex.get('date')} `{ex.get('bucket')}` `{ex.get('rule')}` — {ex.get('match')} ({ex.get('reason')})")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit recent archived daily picks against settled warehouse results.")
    ap.add_argument("--end", default=date.today().isoformat(), help="End date inclusive (YYYY-MM-DD).")
    ap.add_argument("--start", default=None, help="Start date inclusive (YYYY-MM-DD). Overrides --days if provided.")
    ap.add_argument("--days", type=int, default=30, help="Rolling window length in days (default: 30). Ignored if --start is provided.")
    ap.add_argument("--warehouse", default=str(WAREHOUSE), help="Path to warehouse.duckdb")
    ap.add_argument(
        "--include-same-day",
        action="store_true",
        help="Allow same-day archived picks to count as settled. Default is OFF to avoid live/in-progress false settlements.",
    )
    args = ap.parse_args()

    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    if args.start:
        start_date = datetime.strptime(args.start, "%Y-%m-%d").date()
        if start_date > end:
            print(f"error: --start {args.start} is after --end {args.end}", file=sys.stderr)
            return 1
        start = start_date.isoformat()
    else:
        start = (end - timedelta(days=max(0, args.days - 1))).isoformat()
    report = build_report(start, end.isoformat(), Path(args.warehouse), include_same_day=args.include_same_day)

    json_path = LOCALDATA / "picks_audit_rolling.json"
    md_path = LOCALDATA / f"picks_audit_{end.isoformat()}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    write_markdown(md_path, report)

    overall = report.get("overall", {})
    print(f"Recent picks audit — {start} to {end.isoformat()}")
    print(f" archived pick rows: {report.get('archived_pick_rows', 0)}")
    print(f" archived pick dates: {len(report.get('archived_pick_dates', []))}")
    print(f" same-day rows excluded: {report.get('same_day_excluded', 0)}")
    print(f" eligible prior 1x2 picks: {report.get('eligible_prior_picks', 0)}")
    print(f" settled picks: {overall.get('settled_picks', 0)}")
    print(f" unmatched result picks: {report.get('unmatched_result_picks', 0)}")
    print(f" ambiguous result picks: {report.get('ambiguous_result_picks', 0)}")
    print(f" hit rate: {overall.get('hit_rate')}")
    print(f" ROI: {overall.get('roi')}")
    print(f" json: {json_path}")
    print(f" markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
