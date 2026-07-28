#!/usr/bin/env python3
"""Audit recent archived daily picks against settled warehouse results."""

from __future__ import annotations

import argparse
import json
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


def build_report(start: str, end: str, warehouse_path: Path, *, include_same_day: bool = False) -> dict[str, Any]:
    picks = load_archived_picks(start, end)
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
    ap.add_argument("--days", type=int, default=30, help="Rolling window length in days (default: 30).")
    ap.add_argument("--warehouse", default=str(WAREHOUSE), help="Path to warehouse.duckdb")
    ap.add_argument(
        "--include-same-day",
        action="store_true",
        help="Allow same-day archived picks to count as settled. Default is OFF to avoid live/in-progress false settlements.",
    )
    args = ap.parse_args()

    end = datetime.strptime(args.end, "%Y-%m-%d").date()
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
