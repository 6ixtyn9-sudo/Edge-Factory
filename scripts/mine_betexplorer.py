#!/usr/bin/env python3
"""Mine cached BetExplorer data locally.

Reads only local cache files:
  localdata/betexplorer_results_YYYY-MM.csv.gz
  localdata/betexplorer_odds_YYYY-MM.csv.gz

No web requests. No consensus levers. This is standalone/overlap proof only.

Modes:
  python3 scripts/mine_betexplorer.py START END
  python3 scripts/mine_betexplorer.py START END --warehouse localdata/warehouse.duckdb --overlap-certified
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
EDGES_PATH = LOCALDATA / "edges_consensus.json"
SELECTIONS = ("home", "draw", "away")
ODDS_BANDS = [
    (0.0, 1.10, "1.00-1.10"), (1.10, 1.20, "1.10-1.20"),
    (1.20, 1.35, "1.20-1.35"), (1.35, 1.50, "1.35-1.50"),
    (1.50, 1.75, "1.50-1.75"), (1.75, 2.00, "1.75-2.00"),
    (2.00, 2.50, "2.00-2.50"), (2.50, 999.0, "2.50+"),
]
QUALIFIED_TOKENS = (
    "min_p", "home-only", "away-only", "odds-", "bc-confirms",
    "predictz-confirms", "windrawwin-confirms", "freesupertips-confirms",
)

# Optional import: overlap mode uses the same legacy key as the warehouse joins.
sys.path.insert(0, str(ROOT / "src"))
try:
    from edgefactory.util import norm_team  # type: ignore  # noqa: E402
except Exception:  # pragma: no cover - script still works for standalone mode
    def norm_team(name: str, width: int = 9) -> str:  # type: ignore
        import re as _re
        return _re.sub(r"[^a-z]", "", str(name or "").lower())[:width]


def date_range(start: str, end: str) -> Iterable[str]:
    d = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    while d <= e:
        yield d.isoformat()
        d += timedelta(days=1)


def month_key(day: str) -> str:
    return day[:7]


def read_gzip_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with gzip.open(path, "rt", newline="") as fh:
        return list(csv.DictReader(fh))


def ffloat(x) -> float | None:
    try:
        v = float(str(x))
        if math.isfinite(v) and v > 1.0:
            return v
    except Exception:
        pass
    return None


def fint(x) -> int:
    try:
        return int(float(str(x)))
    except Exception:
        return 0


def outcome(row: dict) -> str | None:
    try:
        hs, gs = int(row["hs"]), int(row["gs"])
    except Exception:
        return None
    if hs > gs:
        return "home"
    if hs < gs:
        return "away"
    return "draw"


def odds_band(odds: float | None) -> str:
    if odds is None:
        return "NO_ODDS"
    for lo, hi, name in ODDS_BANDS:
        if lo <= odds < hi:
            return name
    return "2.50+"


def wilson_lb(wins: int, n: int, z: float = 1.96) -> float:
    if n <= 0:
        return 0.0
    phat = wins / n
    denom = 1 + z * z / n
    centre = phat + z * z / (2 * n)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)
    return (centre - margin) / denom


def load_rows(start: str, end: str) -> list[dict]:
    months = sorted({month_key(d) for d in date_range(start, end)})
    results: dict[str, dict] = {}
    odds: dict[str, dict] = {}
    for month in months:
        for r in read_gzip_csv(LOCALDATA / f"betexplorer_results_{month}.csv.gz"):
            if start <= str(r.get("date")) <= end and r.get("event_id"):
                results[str(r["event_id"])] = r
        for r in read_gzip_csv(LOCALDATA / f"betexplorer_odds_{month}.csv.gz"):
            if start <= str(r.get("date")) <= end and r.get("event_id"):
                odds[str(r["event_id"])] = r
    out = []
    for event_id, res in results.items():
        od = odds.get(event_id)
        if not od:
            continue
        row = {**res, **od}
        row["outcome"] = outcome(res)
        if row["outcome"]:
            out.append(row)
    return out


def selection_odds(row: dict, pick: str | None) -> float | None:
    if pick == "home":
        return ffloat(row.get("odd1"))
    if pick == "draw":
        return ffloat(row.get("oddx"))
    if pick == "away":
        return ffloat(row.get("odd2"))
    return None


def enrich(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        odds = [ffloat(r.get("odd1")), ffloat(r.get("oddx")), ffloat(r.get("odd2"))]
        valid = [(i, o) for i, o in enumerate(odds) if o is not None]
        if valid:
            fav_i, fav_odds = min(valid, key=lambda x: x[1])
            r["fav_pick"] = SELECTIONS[fav_i]
            r["fav_odds"] = fav_odds
            r["fav_pnl"] = (fav_odds - 1.0) if r["fav_pick"] == r["outcome"] else -1.0
            r["fav_band"] = odds_band(fav_odds)

        decs = [fint(r.get("dec1")), fint(r.get("decx")), fint(r.get("dec2"))]
        counts = [fint(r.get("n_odd1")), fint(r.get("n_oddx")), fint(r.get("n_odd2"))]
        cands = [(i, decs[i], counts[i], decs[i] / counts[i] if counts[i] else 0.0) for i in range(3)]
        si, dec, cnt, pct = max(cands, key=lambda x: (x[3], x[1]))
        if cnt and odds[si]:
            r["steam_pick"] = SELECTIONS[si]
            r["steam_odds"] = odds[si]
            r["steam_dec_count"] = dec
            r["steam_book_count"] = cnt
            r["steam_dec_pct"] = pct
            r["steam_pnl"] = (odds[si] - 1.0) if r["steam_pick"] == r["outcome"] else -1.0
        out.append(r)
    return out


def summarize(rows: list[dict], label: str, pick_col: str, odds_col: str, pnl_col: str) -> dict:
    usable = [r for r in rows if r.get(pick_col) and r.get(odds_col) and r.get(pnl_col) is not None]
    n = len(usable)
    wins = sum(1 for r in usable if r[pick_col] == r["outcome"])
    pnl = sum(float(r[pnl_col]) for r in usable)
    avg_odds = sum(float(r[odds_col]) for r in usable) / n if n else 0.0
    return {"label": label, "n": n, "wins": wins, "hit": wins / n if n else 0.0,
            "lb": wilson_lb(wins, n), "roi": pnl / n if n else 0.0, "avg_odds": avg_odds}


def print_line(s: dict) -> None:
    print(f"{s['label']:44s} n={s['n']:6d} hit={s['hit']:.1%} LB={s['lb']:.3f} ROI={s['roi']:+.1%} avg_odds={s['avg_odds']:.2f}")


def maybe_print(rows: list[dict], label: str, pick_col: str, odds_col: str, pnl_col: str, min_n: int) -> None:
    if len(rows) >= min_n:
        print_line(summarize(rows, label, pick_col, odds_col, pnl_col))


def print_standalone(rows: list[dict], min_n: int) -> None:
    print("\nMarket favorite")
    print("=" * 80)
    print_line(summarize(rows, "favorite all", "fav_pick", "fav_odds", "fav_pnl"))
    for _, _, band in ODDS_BANDS:
        sub = [r for r in rows if r.get("fav_band") == band]
        maybe_print(sub, f"favorite odds {band}", "fav_pick", "fav_odds", "fav_pnl", min_n)

    print("\nDropping odds proxy")
    print("=" * 80)
    for threshold in (0.50, 0.70, 0.90):
        sub = [r for r in rows if float(r.get("steam_dec_pct") or 0) >= threshold and int(r.get("steam_dec_count") or 0) >= 3]
        maybe_print(sub, f"steam dec_pct>={threshold:.0%}", "steam_pick", "steam_odds", "steam_pnl", min_n)
    for min_count in (3, 5, 10):
        sub = [r for r in rows if int(r.get("steam_dec_count") or 0) >= min_count]
        maybe_print(sub, f"steam dec_count>={min_count}", "steam_pick", "steam_odds", "steam_pnl", min_n)


def _rule_threshold(rule: str) -> float | None:
    m = re.search(r"avg_p\s*>=\s*([0-9.]+)", rule)
    return float(m.group(1)) if m else None


def _rule_n_way(rule: str) -> int | None:
    m = re.search(r"(\d+)\s*way", rule)
    return int(m.group(1)) if m else None


def _is_qualified_rule(rule: str) -> bool:
    r = rule.lower()
    return any(tok in r for tok in QUALIFIED_TOKENS)


def load_operational_thresholds() -> dict[int, float]:
    """Load unqualified certified 1x2 thresholds; fallback to canonical defaults."""
    thresholds = {2: 70.0, 3: 65.0}
    try:
        data = json.loads(EDGES_PATH.read_text())
    except Exception:
        return thresholds
    for e in data.get("edges", []):
        if e.get("status") != "certified" or e.get("market", "1x2") != "1x2":
            continue
        rule = e.get("rule", "")
        if _is_qualified_rule(rule):
            continue
        n_way = int(e.get("n_way") or _rule_n_way(rule) or 0)
        thr = _rule_threshold(rule)
        if n_way in (2, 3) and thr is not None:
            thresholds[n_way] = thr
    return thresholds


def _avgp_expr(col: str = "avg_p") -> str:
    return f"CASE WHEN {col} > 1.5 THEN {col} ELSE {col}*100 END"


def load_edge_candidates(warehouse: Path, start: str, end: str) -> list[dict]:
    import duckdb  # local import: standalone mode does not require duckdb

    con = duckdb.connect(str(warehouse), read_only=True)
    thresholds = load_operational_thresholds()
    out: list[dict] = []

    t2 = thresholds.get(2, 70.0)
    try:
        rows = con.execute(f"""
            SELECT date, home, away, outcome, fb_pick AS pick,
                   {_avgp_expr('avg_p')} AS edge_avg_p, pick_odds, league,
                   '2way' AS edge_family
            FROM consensus2
            WHERE date >= ? AND date <= ?
              AND fb_pick = zb_pick
              AND {_avgp_expr('avg_p')} >= ?
        """, [start, end, t2]).fetchall()
        for date_, home, away, outcome_, pick, avg_p, pick_odds, league, edge_family in rows:
            out.append({
                "date": str(date_)[:10], "home": home, "away": away, "outcome": outcome_,
                "edge_pick": pick, "edge_avg_p": float(avg_p or 0),
                "edge_pick_odds": pick_odds, "league": league, "edge_family": edge_family,
                "edge_rule": f"2way-unanimous avg_p>={t2:g}",
            })
    except Exception as exc:
        print(f"WARN: consensus2 overlap query failed: {exc}")

    t3 = thresholds.get(3, 65.0)
    try:
        rows = con.execute(f"""
            SELECT date, home, away, outcome, fb_pick AS pick,
                   {_avgp_expr('avg_p')} AS edge_avg_p, pick_odds, league,
                   '3way' AS edge_family
            FROM consensus3
            WHERE date >= ? AND date <= ?
              AND fb_pick = zb_pick AND zb_pick = sa_pick
              AND {_avgp_expr('avg_p')} >= ?
        """, [start, end, t3]).fetchall()
        for date_, home, away, outcome_, pick, avg_p, pick_odds, league, edge_family in rows:
            out.append({
                "date": str(date_)[:10], "home": home, "away": away, "outcome": outcome_,
                "edge_pick": pick, "edge_avg_p": float(avg_p or 0),
                "edge_pick_odds": pick_odds, "league": league, "edge_family": edge_family,
                "edge_rule": f"3way-unanimous avg_p>={t3:g}",
            })
    except Exception as exc:
        print(f"WARN: consensus3 overlap query failed: {exc}")

    # De-dupe candidate rows by date/team/pick, preferring higher n-way then avg_p.
    best: dict[tuple, dict] = {}
    for r in out:
        key = (r["date"], norm_team(r["home"]), norm_team(r["away"]), r["edge_pick"])
        incumbent = best.get(key)
        score = (3 if r["edge_family"] == "3way" else 2, r["edge_avg_p"])
        old_score = (0, 0.0) if incumbent is None else (3 if incumbent["edge_family"] == "3way" else 2, incumbent["edge_avg_p"])
        if incumbent is None or score > old_score:
            best[key] = r
    return list(best.values())


def join_betexplorer_to_edges(be_rows: list[dict], edge_rows: list[dict]) -> list[dict]:
    be_index: dict[tuple[str, str, str], dict] = {}
    for r in be_rows:
        be_index[(str(r["date"]), norm_team(str(r.get("home") or "")), norm_team(str(r.get("away") or "")))] = r

    out: list[dict] = []
    for edge in edge_rows:
        key = (edge["date"], norm_team(str(edge.get("home") or "")), norm_team(str(edge.get("away") or "")))
        be = be_index.get(key)
        if not be:
            continue
        row = {**be, **edge}
        edge_odds = selection_odds(be, edge.get("edge_pick"))
        row["edge_be_odds"] = edge_odds
        row["edge_be_band"] = odds_band(edge_odds)
        row["edge_be_pnl"] = (edge_odds - 1.0) if edge_odds and edge["edge_pick"] == row["outcome"] else (-1.0 if edge_odds else None)
        row["edge_agrees_fav"] = edge.get("edge_pick") == be.get("fav_pick")
        row["edge_agrees_steam"] = edge.get("edge_pick") == be.get("steam_pick")
        row["edge_steam_opposes"] = bool(be.get("steam_pick")) and edge.get("edge_pick") != be.get("steam_pick")
        out.append(row)
    return out


def print_overlap(rows: list[dict], min_n: int) -> None:
    print("\nEdge Factory overlap with BetExplorer")
    print("=" * 80)
    print_line(summarize(rows, "EF overlap all @ BE odds", "edge_pick", "edge_be_odds", "edge_be_pnl"))

    for family in ("2way", "3way"):
        sub = [r for r in rows if r.get("edge_family") == family]
        maybe_print(sub, f"EF {family} overlap", "edge_pick", "edge_be_odds", "edge_be_pnl", min_n)

    fav_yes = [r for r in rows if r.get("edge_agrees_fav")]
    fav_no = [r for r in rows if r.get("edge_agrees_fav") is False]
    maybe_print(fav_yes, "EF pick = BE favorite", "edge_pick", "edge_be_odds", "edge_be_pnl", min_n)
    maybe_print(fav_no, "EF pick != BE favorite", "edge_pick", "edge_be_odds", "edge_be_pnl", min_n)

    steam_yes = [r for r in rows if r.get("edge_agrees_steam")]
    steam_no = [r for r in rows if r.get("edge_steam_opposes")]
    maybe_print(steam_yes, "EF pick = BE steam proxy", "edge_pick", "edge_be_odds", "edge_be_pnl", min_n)
    maybe_print(steam_no, "EF pick opposed by BE steam", "edge_pick", "edge_be_odds", "edge_be_pnl", min_n)

    for _, _, band in ODDS_BANDS:
        sub = [r for r in rows if r.get("edge_be_band") == band]
        maybe_print(sub, f"EF BE odds {band}", "edge_pick", "edge_be_odds", "edge_be_pnl", min_n)


def main() -> None:
    ap = argparse.ArgumentParser(description="Mine cached BetExplorer odds/results. No web requests.")
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("--min-n", type=int, default=20, help="Minimum rows to print subgroup")
    ap.add_argument("--warehouse", default=None, help="DuckDB warehouse path for Edge Factory overlap mode")
    ap.add_argument("--overlap-certified", action="store_true", help="Mine overlap between operational consensus candidates and BetExplorer")
    args = ap.parse_args()

    rows = enrich(load_rows(args.start, args.end))
    print(f"Loaded joined BetExplorer rows: {len(rows)} ({args.start} -> {args.end})")
    if not rows:
        print("No joined rows. Run backfill_betexplorer.py results and odds first.")
        return

    print_standalone(rows, args.min_n)

    if args.overlap_certified:
        warehouse = Path(args.warehouse or (LOCALDATA / "warehouse.duckdb"))
        if not warehouse.exists():
            print(f"\nOverlap skipped: warehouse not found: {warehouse}")
            return
        edge_rows = load_edge_candidates(warehouse, args.start, args.end)
        overlap = join_betexplorer_to_edges(rows, edge_rows)
        print(f"\nLoaded EF operational candidates: {len(edge_rows)}; joined BetExplorer overlap: {len(overlap)}")
        print_overlap(overlap, args.min_n)


if __name__ == "__main__":
    main()
