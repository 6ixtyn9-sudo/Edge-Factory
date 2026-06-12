"""
local_backfill.py — Supabase-free historical backfill to monthly CSV.gz.
Used for deep backtests before the DB is wired. Resumable via state file.

    python3 scripts/local_backfill.py zulubet 2024-01-01 2026-06-11 --max-seconds 1500
    python3 scripts/local_backfill.py statarea 2019-01-01 2026-06-11 --max-seconds 1500
"""
import csv
import gzip
import io
import json
import os
import sys
import time
import types
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.modules.setdefault("supabase", types.ModuleType("supabase"))

from edgefactory.sources import get_source  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "localdata")
FIELDS = ["date", "source", "start", "country", "league", "home", "away",
          "market", "selection", "prob", "odds", "ft_h", "ft_a"]


def rows_of(events, source_key, day):
    out = []
    for e in events:
        ft_h = e.result.outcome_home if e.result else ""
        ft_a = e.result.outcome_away if e.result else ""
        odds_map = {(o.market, o.selection): o.odds for o in e.odds}
        for p in e.predictions:
            out.append({
                "date": day.isoformat(), "source": source_key,
                "start": e.start_time.isoformat(),
                "country": e.country, "league": e.competition_name,
                "home": e.home_name, "away": e.away_name,
                "market": p.market, "selection": p.selection,
                "prob": round(p.probability, 4),
                "odds": odds_map.get((p.market, p.selection), ""),
                "ft_h": ft_h, "ft_a": ft_a})
    return out


def main():
    source_key, start_s, end_s = sys.argv[1], sys.argv[2], sys.argv[3]
    max_seconds = 10 ** 9
    if "--max-seconds" in sys.argv:
        max_seconds = int(sys.argv[sys.argv.index("--max-seconds") + 1])

    os.makedirs(HERE, exist_ok=True)
    state_path = os.path.join(HERE, f"state_{source_key}.json")
    done = set()
    if os.path.exists(state_path):
        done = set(json.load(open(state_path))["done"])

    start, end = date.fromisoformat(start_s), date.fromisoformat(end_s)
    todo = []
    d = start
    while d <= end:
        if d.isoformat() not in done:
            todo.append(d)
        d += timedelta(days=1)
    print(f"{source_key}: {len(todo)} days to fetch ({len(done)} done)")

    src = get_source(source_key)
    t0 = time.time()
    buf = {}
    n = 0

    def flush():
        for month, rows in buf.items():
            path = os.path.join(HERE, f"{source_key}_{month}.csv.gz")
            existing = []
            if os.path.exists(path):
                with gzip.open(path, "rt", newline="") as f:
                    existing = list(csv.DictReader(f))
            key = lambda r: (r["date"], r["home"], r["away"], r["market"], r["selection"])
            merged = {key(r): r for r in existing}
            for r in rows:
                merged[key({k: str(v) for k, v in r.items()})] = {k: str(v) for k, v in r.items()}
            s = io.StringIO()
            w = csv.DictWriter(s, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(sorted(merged.values(), key=lambda r: (r["date"], r["home"])))
            with gzip.open(path, "wt", compresslevel=6) as f:
                f.write(s.getvalue())
        buf.clear()
        json.dump({"done": sorted(done)}, open(state_path, "w"))

    for d in todo:
        if time.time() - t0 > max_seconds:
            print("time budget hit — flushing (resumable)")
            break
        try:
            ev = src.normalize(src.fetch_day(d), d)
            rs = rows_of(ev, source_key, d)
            buf.setdefault(d.strftime("%Y-%m"), []).extend(rs)
            done.add(d.isoformat())
            n += 1
            if n % 25 == 0:
                flush()
                el = time.time() - t0
                print(f"  {d} | {n}/{len(todo)} | {el:.0f}s | ~{el/n:.1f}s/day")
        except Exception as e:
            msg = repr(e)
            if "410" in msg or "404" in msg or "Gone" in msg:
                done.add(d.isoformat())  # permanently gone, don't retry
            else:
                print(f"  {d} FAILED: {msg[:60]}")
    flush()
    src.close()
    print(f"done this run: {n} days in {time.time()-t0:.0f}s; total {len(done)}")


if __name__ == "__main__":
    main()
