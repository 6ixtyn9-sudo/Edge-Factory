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
    except ModuleNotFoundError:
        print(f"ERROR: source '{key}' not found", file=sys.stderr)
        sys.exit(2)

def dedup_key(row: dict, columns: list[str]):
    # Odds adapters emit multiple rows per event; preserve market/selection/bookmaker.
    # Include kickoff when available so same-day duplicate fixtures do not collapse.
    if row.get("market") or row.get("selection") or row.get("bookmaker"):
        return (
            str(row.get("date", "")),
            str(row.get("kickoff", "")).lower(),
            str(row.get("home", "")).lower(),
            str(row.get("away", "")).lower(),
            str(row.get("market", "")).lower(),
            str(row.get("selection", "")).lower(),
            str(row.get("bookmaker", "")).lower(),
        )
    # Prefer event_id if present for one-row-per-event prediction adapters.
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

# OP-01 T4(a) — a zero-row day is only "done" when the source actually saw an
# empty slate. Adapters that swallow transport/auth errors (bzzoiro_odds
# `_fetch_url` "never raises") return [] after an HTTP 403, which used to be
# recorded as a terminal success — the day was never retried again. Adapters
# that expose diagnostics() are asked; everything else is unchanged.
RETRYABLE_ZERO_ROW_STATUSES = {"auth", "quota", "unavailable", "blocked", "error"}


def inspect_retryable_statuses() -> set[str]:
    """The zero-row statuses that keep a day open (introspection/tests)."""
    return set(RETRYABLE_ZERO_ROW_STATUSES)


def zero_row_retry_reason(mod) -> str | None:
    """Reason string when a zero-row day must stay open, else None."""
    diag_fn = getattr(mod, "diagnostics", None)
    if not callable(diag_fn):
        return None
    try:
        diag = diag_fn() or {}
    except Exception:
        return None
    status = str(diag.get("status") or "").strip().lower()
    if status not in RETRYABLE_ZERO_ROW_STATUSES:
        return None
    codes = ",".join(str(c) for c in (diag.get("http_statuses") or [])) or "none"
    hint = str(diag.get("quota_hint") or "none")
    return (f"zero rows with status={status} http={codes} quota_hint={hint} "
            f"— not an empty slate; day stays retryable")



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
    failures: dict[str, str] = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
            done = set(state.get("done", []))
            if isinstance(state.get("failures"), dict):
                failures = {
                    str(day): str(message)
                    for day, message in state["failures"].items()
                }
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
    n_rows = 0

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
                    # Restrict every row to file_columns: legacy files captured by
                    # newer code may carry extra columns (e.g. kickoff_timezone,
                    # captured_at); writing them against this schema would raise
                    # "dict contains fields not in fieldnames". Drop extras.
                    w.writerow({col: row.get(col, "") for col in file_columns})
        buf.clear()
        state_path.write_text(json.dumps({
            "done": sorted(done),
            "failures": dict(sorted(failures.items())),
        }))

    failed_this_run: dict[str, str] = {}
    budget_hit = False

    try:
        for d in todo:
            if time.time() - t0 > max_seconds:
                budget_hit = True
                print("time budget hit — flushing (resumable; remaining dates stay open)")
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
                    n_rows += len(rows)
                else:
                    if source_key.endswith("_odds"):
                        print(f"  {d} | 0 rows")
                    reason = zero_row_retry_reason(mod)
                    if reason:
                        print(f"  {d} ZERO-ROW NOT DONE: {reason}")
                        failures[d.isoformat()] = reason
                        failed_this_run[d.isoformat()] = reason
                        continue
                done.add(d.isoformat())
                failures.pop(d.isoformat(), None)
                n += 1
                if n % 10 == 0:
                    flush()
                    el = time.time() - t0
                    print(f"  {d} | {n}/{len(todo)} | {el:.0f}s | ~{el/n:.1f}s/day")
            except Exception as e:
                msg = repr(e)
                # Permanently unavailable historical pages are an honest absence.
                if "410" in msg or "404" in msg or "Gone" in msg:
                    done.add(d.isoformat())
                    failures.pop(d.isoformat(), None)
                else:
                    concise = str(e).replace("\n", " ")[:500] or type(e).__name__
                    print(f"  {d} FAILED: {concise}")
                    failures[d.isoformat()] = concise
                    failed_this_run[d.isoformat()] = concise
                    # Do not mark done: challenge/layout/transport failures retry.
        flush()
    finally:
        pass

    print(f"done this run: {n} days, {n_rows} rows in {time.time()-t0:.0f}s; total {len(done)}")
    if failed_this_run or budget_hit:
        if failed_this_run:
            print(f"FAILED this run: {len(failed_this_run)} day(s); state remains retryable")
        if budget_hit:
            print("INCOMPLETE this run: time budget reached; unattempted dates remain retryable")
        sys.exit(1)

if __name__ == "__main__":
    main()
