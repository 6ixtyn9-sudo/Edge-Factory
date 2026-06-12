#!/usr/bin/env python3
"""
local_backfill.py — Supabase-free historical backfill to monthly CSV.gz.
Resumable via state file. Works with simple module sources (fetch_day -> list[dict]).

python3 scripts/local_backfill.py forebet 2024-01-01 2026-06-11 --max-seconds 1500
python3 scripts/local_backfill.py statarea 2017-01-01 2023-12-31 --max-seconds 1500
"""
from __future__ import annotations
import csv
import gzip
import importlib
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
LOCALDATA.mkdir(exist_ok=True)

def load_source(key: str):
    try:
        return importlib.import_module(f"edgefactory.sources.{key}")
    except ModuleNotFoundError as e:
        print(f"ERROR: source '{key}' not found", file=sys.stderr)
        sys.exit(2)

def dedup_key(row: dict, columns: list[str]):
    # Prefer event_id if present
    if "event_id" in row and row.get("event_id"):
        return str(row["event_id"])
    # fallback: date + home + away
    return (
        str(row.get("date", "")),
        str(row.get("home", "")).lower(),
        str(row.get("away", "")).lower(),
    )

def read_existing(path: Path):
    if not path.exists():
        return {}
    try:
        with gzip.open(path, "rt", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # build key map
            out = {}
            for r in rows:
                k = dedup_key(r, reader.fieldnames or [])
                out[k] = r
            return out
    except Exception:
        return {}

def main():
    if len(sys.argv) < 4:
        print("usage: local_backfill.py <source> <start YYYY-MM-DD> <end YYYY-MM-DD> [--max-seconds N] [--workers N]", file=sys.stderr)
        sys.exit(2)

    source_key, start_s, end_s = sys.argv[1], sys.argv[2], sys.argv[3]
    max_seconds = 10**9
    if "--max-seconds" in sys.argv:
        max_seconds = int(sys.argv[sys.argv.index("--max-seconds") + 1])
    # --workers is accepted for compatibility with capture_daily, ignored (single-process)

    sys.path.insert(0, str(ROOT / "src"))
    mod = load_source(source_key)

    if not hasattr(mod, "fetch_day"):
        print(f"ERROR: {source_key} has no fetch_day()", file=sys.stderr)
        sys.exit(2)

    columns = getattr(mod, "COLUMNS", None)
    if not columns:
        print(f"WARNING: {source_key} has no COLUMNS, will infer from first row", file=sys.stderr)

    state_path = LOCALDATA / f"state_{source_key}.json"
    done = set()
    if state_path.exists():
        try:
            done = set(json.loads(state_path.read_text()).get("done", []))
        except Exception:
            pass

    start, end = date.fromisoformat(start_s), date.fromisoformat(end_s)
    todo = []
    d = start
    while d <= end:
        if d.isoformat() not in done:
            todo.append(d)
        d += timedelta(days=1)

    print(f"{source_key}: {len(todo)} days to fetch ({len(done)} done)")

    t0 = time.time()
    buf: dict[str, list[dict]] = {}
    n = 0

    def flush():
        for month, rows in buf.items():
            if not rows:
                continue
            path = LOCALDATA / f"{source_key}_{month}.csv.gz"
            existing = read_existing(path)
            # merge
            file_columns = columns or sorted({k for r in rows for k in r.keys()})
            for r in rows:
                k = dedup_key(r, file_columns)
                # stringify all values for csv
                existing[k] = {col: "" if r.get(col) is None else str(r.get(col, "")) for col in file_columns}
            # write
            with gzip.open(path, "wt", newline="", compresslevel=6) as f:
                w = csv.DictWriter(f, fieldnames=file_columns)
                w.writeheader()
                for row in sorted(existing.values(), key=lambda x: (x.get("date",""), x.get("home",""), x.get("away",""))):
                    w.writerow(row)
        buf.clear()
        state_path.write_text(json.dumps({"done": sorted(done)}))

    try:
        for d in todo:
            if time.time() - t0 > max_seconds:
                print("time budget hit — flushing (resumable)")
                break
            try:
                rows = mod.fetch_day(d.isoformat())
                if rows:
                    # ensure date field is set
                    for r in rows:
                        if "date" not in r or not r["date"]:
                            r["date"] = d.isoformat()
                    month = d.strftime("%Y-%m")
                    buf.setdefault(month, []).extend(rows)
                done.add(d.isoformat())
                n += 1
                if n % 10 == 0:
                    flush()
                    el = time.time() - t0
                    print(f"  {d} | {n}/{len(todo)} | {el:.0f}s | ~{el/n:.1f}s/day")
            except Exception as e:
                msg = repr(e)
                # permanently gone?
                if "410" in msg or "404" in msg or "Gone" in msg:
                    done.add(d.isoformat())
                else:
                    print(f"  {d} FAILED: {e}")
                    # don't mark done, retry next run
        flush()
    finally:
        pass

    print(f"done this run: {n} days in {time.time()-t0:.0f}s; total {len(done)}")

if __name__ == "__main__":
    main()
