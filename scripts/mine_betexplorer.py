#!/usr/bin/env python3
"""Mine cached BetExplorer data locally.

Reads only local cache files:
  localdata/betexplorer_results_YYYY-MM.csv.gz
  localdata/betexplorer_odds_YYYY-MM.csv.gz

No web requests. No consensus levers. This is standalone proof only.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
SELECTIONS = ("home", "draw", "away")
ODDS_BANDS = [
    (0.0, 1.10, "1.00-1.10"), (1.10, 1.20, "1.10-1.20"),
    (1.20, 1.35, "1.20-1.35"), (1.35, 1.50, "1.35-1.50"),
    (1.50, 1.75, "1.50-1.75"), (1.75, 2.00, "1.75-2.00"),
    (2.00, 2.50, "2.00-2.50"), (2.50, 999.0, "2.50+"),
]


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
    print(f"{s['label']:35s} n={s['n']:6d} hit={s['hit']:.1%} LB={s['lb']:.3f} ROI={s['roi']:+.1%} avg_odds={s['avg_odds']:.2f}")


def maybe_print(rows: list[dict], label: str, pick_col: str, odds_col: str, pnl_col: str, min_n: int) -> None:
    if len(rows) >= min_n:
        print_line(summarize(rows, label, pick_col, odds_col, pnl_col))


def main() -> None:
    ap = argparse.ArgumentParser(description="Mine cached BetExplorer odds/results. No web requests.")
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("--min-n", type=int, default=20, help="Minimum rows to print subgroup")
    args = ap.parse_args()

    rows = enrich(load_rows(args.start, args.end))
    print(f"Loaded joined BetExplorer rows: {len(rows)} ({args.start} -> {args.end})")
    if not rows:
        print("No joined rows. Run backfill_betexplorer.py results and odds first.")
        return

    print("\nMarket favorite")
    print("=" * 72)
    print_line(summarize(rows, "favorite all", "fav_pick", "fav_odds", "fav_pnl"))
    for _, _, band in ODDS_BANDS:
        sub = [r for r in rows if r.get("fav_band") == band]
        maybe_print(sub, f"favorite odds {band}", "fav_pick", "fav_odds", "fav_pnl", args.min_n)

    print("\nDropping odds proxy")
    print("=" * 72)
    for threshold in (0.50, 0.70, 0.90):
        sub = [r for r in rows if float(r.get("steam_dec_pct") or 0) >= threshold and int(r.get("steam_dec_count") or 0) >= 3]
        maybe_print(sub, f"steam dec_pct>={threshold:.0%}", "steam_pick", "steam_odds", "steam_pnl", args.min_n)
    for min_count in (3, 5, 10):
        sub = [r for r in rows if int(r.get("steam_dec_count") or 0) >= min_count]
        maybe_print(sub, f"steam dec_count>={min_count}", "steam_pick", "steam_odds", "steam_pnl", args.min_n)


if __name__ == "__main__":
    main()
