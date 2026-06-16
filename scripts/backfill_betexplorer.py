#!/usr/bin/env python3
"""BetExplorer historical cache builder.

Stages
------
results
    Fetch date-addressable football result archives and cache settled matches:
    localdata/betexplorer_results_YYYY-MM.csv.gz

odds
    Read cached result rows, fetch BetExplorer match odds JSON for each event_id,
    and cache 1X2 best odds + odds-table movement arrows:
    localdata/betexplorer_odds_YYYY-MM.csv.gz

all
    Run results then odds.

This is a data job only. It does not update warehouse, consensus, picks, or
Supabase. It is resumable by event_id and safe to stop/restart.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import html
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
BASE = "https://www.betexplorer.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

RESULT_COLUMNS = [
    "date", "kickoff", "country", "league", "home", "away", "hs", "gs",
    "ht_hs", "ht_gs", "match_url", "event_id", "fetched_at",
]

ODDS_COLUMNS = [
    "date", "event_id", "match_url", "odd1", "oddx", "odd2",
    "bookmaker_rows", "n_odd1", "n_oddx", "n_odd2",
    "dec1", "decx", "dec2", "inc1", "incx", "inc2",
    "page_param", "fetched_at",
]


@dataclass
class FetchStats:
    fetched: int = 0
    skipped: int = 0
    failed: int = 0
    written: int = 0


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def month_key(day: str) -> str:
    return day[:7]


def results_path(month: str) -> Path:
    return LOCALDATA / f"betexplorer_results_{month}.csv.gz"


def odds_path(month: str) -> Path:
    return LOCALDATA / f"betexplorer_odds_{month}.csv.gz"


def fetch(url: str, *, referer: str | None = None, retries: int = 4, sleep: float = 1.0) -> str:
    headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if referer:
        headers["Referer"] = referer
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 429:
                time.sleep(max(5.0, sleep * (attempt + 2) * 3))
            elif attempt < retries - 1:
                time.sleep(sleep * (attempt + 1))
        except Exception as exc:  # noqa: BLE001 - data job should retry generic network errors
            last = exc
            if attempt < retries - 1:
                time.sleep(sleep * (attempt + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return " ".join(html.unescape(s).split())


def ffloat(x: object) -> float | None:
    try:
        v = float(str(x).strip())
        if math.isfinite(v) and v > 1.0:
            return v
    except Exception:
        pass
    return None


def date_range(start: str, end: str) -> Iterable[str]:
    d = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    while d <= e:
        yield d.isoformat()
        d += timedelta(days=1)


def read_gzip_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with gzip.open(path, "rt", newline="") as fh:
        return list(csv.DictReader(fh))


def write_gzip_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("wt", delete=False, newline="", dir=str(path.parent), suffix=".tmp") as tmp:
        tmp_name = tmp.name
        with gzip.GzipFile(fileobj=tmp.buffer, mode="wb") as gz:  # type: ignore[attr-defined]
            pass
    # NamedTemporaryFile text+gzip is awkward; write direct temp path below.
    os.unlink(tmp_name)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(tmp_path, "wt", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp_path.replace(path)


def upsert_monthly(path: Path, new_rows: list[dict], key: str, fieldnames: list[str]) -> int:
    existing = read_gzip_csv(path)
    by_key = {str(r.get(key) or ""): r for r in existing if r.get(key)}
    before = len(by_key)
    for row in new_rows:
        k = str(row.get(key) or "")
        if k:
            by_key[k] = row
    rows = sorted(by_key.values(), key=lambda r: (str(r.get("date") or ""), str(r.get(key) or "")))
    write_gzip_csv(path, rows, fieldnames)
    return len(by_key) - before


def parse_event_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def parse_results_page(page: str) -> list[dict]:
    out: list[dict] = []
    current_country: str | None = None
    current_league: str | None = None
    token_re = re.compile(r'(<tr class="js-tournament".*?</tr>|<tr data-dt=".*?</tr>)', re.S)
    for token in token_re.findall(page):
        if 'class="js-tournament"' in token:
            m = re.search(r'class="table-main__tournament"[^>]*>\s*(?:<i>.*?</i>)?\s*([^<]+)</a>', token, re.S)
            label = strip_tags(m.group(1)) if m else "UNKNOWN"
            if ":" in label:
                current_country, current_league = [x.strip() for x in label.split(":", 1)]
            else:
                current_country, current_league = None, label.strip() or "UNKNOWN"
            continue

        dt = re.search(r'data-dt="(\d+),(\d+),(\d+),(\d+),(\d+)"', token)
        link = re.search(r'<td class="table-main__tt">.*?<a href="([^"]+)">(.*?)</a>', token, re.S)
        score = re.search(r'class="table-main__result".*?<strong>\s*(\d+)\s*:\s*(\d+)\s*</strong>', token, re.S)
        if not (dt and link and score):
            continue
        match_text = strip_tags(link.group(2))
        if " - " not in match_text:
            continue
        home, away = [x.strip() for x in match_text.split(" - ", 1)]
        dd, mm, yyyy, hh, minute = [int(x) for x in dt.groups()]
        match_date = date(yyyy, mm, dd).isoformat()
        rel_url = html.unescape(link.group(1))
        full_url = rel_url if rel_url.startswith("http") else BASE + rel_url
        partial = re.search(r'class="table-main__partial"[^>]*>\s*\((\d+)\s*:\s*(\d+)\s*,', token, re.S)
        out.append({
            "date": match_date,
            "kickoff": f"{hh:02d}:{minute:02d}",
            "country": current_country,
            "league": current_league,
            "home": home,
            "away": away,
            "hs": int(score.group(1)),
            "gs": int(score.group(2)),
            "ht_hs": int(partial.group(1)) if partial else None,
            "ht_gs": int(partial.group(2)) if partial else None,
            "match_url": full_url,
            "event_id": parse_event_id(full_url),
            "fetched_at": now_iso(),
        })
    return out


def backfill_results(start: str, end: str, *, sleep: float = 0.2) -> FetchStats:
    stats = FetchStats()
    by_month: dict[str, list[dict]] = defaultdict(list)
    for day in date_range(start, end):
        y, m, d = day.split("-")
        url = f"{BASE}/football/results/?year={y}&month={m}&day={d}"
        page = fetch(url, sleep=sleep)
        rows = parse_results_page(page)
        for row in rows:
            by_month[month_key(row["date"])].append(row)
        stats.fetched += 1
        print(f"  results {day}: {len(rows)} settled rows")
        time.sleep(sleep)
    for month, rows in sorted(by_month.items()):
        written = upsert_monthly(results_path(month), rows, "event_id", RESULT_COLUMNS)
        stats.written += written
        print(f"  wrote {results_path(month).name}: +{written} new/updated={len(rows)}")
    return stats


def parse_page_param(match_html: str) -> str:
    m = re.search(r"match_load_tabs\('\w+',\s*'1x2',\s*'[^']*',\s*'[^']*',\s*'([^']+)'", match_html)
    return m.group(1) if m else "1"


def parse_1x2_odds_html(odds_html: str) -> dict:
    m = re.search(r'<tbody id="best-odds-0">(.*?)</tbody>', odds_html, re.S)
    block = m.group(1) if m else odds_html
    rows = re.findall(r'<tr\b.*?</tr>', block, re.S)
    best = [None, None, None]
    counts = [0, 0, 0]
    dec = [0, 0, 0]
    inc = [0, 0, 0]
    bookmaker_rows = 0
    for row in rows:
        cells = re.findall(r'(<td\b[^>]*data-odd="[^"]+".*?</td>)', row, re.S)
        if len(cells) < 3:
            continue
        bookmaker_rows += 1
        for i, cell in enumerate(cells[:3]):
            om = re.search(r'data-odd="([0-9.]+)"', cell)
            odd = ffloat(om.group(1) if om else None)
            if odd is None:
                continue
            counts[i] += 1
            if best[i] is None or odd > best[i]:
                best[i] = odd
            if "icon__decreasing" in cell:
                dec[i] += 1
            if "icon__increasing" in cell:
                inc[i] += 1
    return {
        "odd1": best[0], "oddx": best[1], "odd2": best[2],
        "bookmaker_rows": bookmaker_rows,
        "n_odd1": counts[0], "n_oddx": counts[1], "n_odd2": counts[2],
        "dec1": dec[0], "decx": dec[1], "dec2": dec[2],
        "inc1": inc[0], "incx": inc[1], "inc2": inc[2],
    }


def fetch_odds_for_result(row: dict, *, sleep: float) -> dict:
    match_url = str(row["match_url"])
    event_id = str(row["event_id"])
    match_html = fetch(match_url, referer=BASE, sleep=sleep)
    page_param = parse_page_param(match_html)
    odds_url = f"{BASE}/match-odds/{event_id}/{page_param}/1x2/bestOdds/?lang=en"
    time.sleep(sleep)
    data = json.loads(fetch(odds_url, referer=match_url, sleep=sleep))
    odds = parse_1x2_odds_html(data.get("odds", ""))
    return {
        "date": row["date"],
        "event_id": event_id,
        "match_url": match_url,
        **odds,
        "page_param": page_param,
        "fetched_at": now_iso(),
    }


def load_result_rows(start: str, end: str) -> list[dict]:
    months = sorted({month_key(d) for d in date_range(start, end)})
    rows: list[dict] = []
    for month in months:
        for row in read_gzip_csv(results_path(month)):
            if start <= str(row.get("date")) <= end:
                rows.append(row)
    return rows


def load_existing_odds_ids(start: str, end: str) -> set[str]:
    months = sorted({month_key(d) for d in date_range(start, end)})
    ids: set[str] = set()
    for month in months:
        for row in read_gzip_csv(odds_path(month)):
            if row.get("event_id"):
                ids.add(str(row["event_id"]))
    return ids


def flush_odds(buffer: list[dict]) -> int:
    by_month: dict[str, list[dict]] = defaultdict(list)
    for row in buffer:
        by_month[month_key(str(row["date"]))].append(row)
    written = 0
    for month, rows in by_month.items():
        written += upsert_monthly(odds_path(month), rows, "event_id", ODDS_COLUMNS)
    return written


def backfill_odds(start: str, end: str, *, sleep: float, max_seconds: int, limit: int, flush_every: int) -> FetchStats:
    stats = FetchStats()
    rows = load_result_rows(start, end)
    if not rows:
        print("No cached BetExplorer results rows. Run: backfill_betexplorer.py results START END")
        return stats
    existing = load_existing_odds_ids(start, end)
    pending = [r for r in rows if str(r.get("event_id")) not in existing]
    if limit:
        pending = pending[:limit]
    print(f"odds pending: {len(pending)} / results rows={len(rows)} existing_odds={len(existing)}")
    started = time.monotonic()
    buffer: list[dict] = []
    for i, row in enumerate(pending, 1):
        if max_seconds and time.monotonic() - started >= max_seconds:
            print(f"max_seconds reached after {i-1} attempts")
            break
        try:
            buffer.append(fetch_odds_for_result(row, sleep=sleep))
            stats.fetched += 1
        except Exception as exc:  # noqa: BLE001 - resumable job continues
            stats.failed += 1
            if stats.failed <= 20:
                print(f"  WARN {row.get('date')} {row.get('home')} vs {row.get('away')}: {exc}", file=sys.stderr)
        if len(buffer) >= flush_every:
            stats.written += flush_odds(buffer)
            buffer.clear()
        if i % 25 == 0:
            print(f"  odds attempts {i}/{len(pending)} fetched={stats.fetched} failed={stats.failed}")
        time.sleep(sleep)
    if buffer:
        stats.written += flush_odds(buffer)
    print(f"odds done: fetched={stats.fetched} failed={stats.failed} written_new={stats.written}")
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill BetExplorer results and 1X2 odds caches")
    ap.add_argument("stage", choices=["results", "odds", "all"], help="Which stage to run")
    ap.add_argument("start", help="Start date YYYY-MM-DD")
    ap.add_argument("end", help="End date YYYY-MM-DD")
    ap.add_argument("--sleep", type=float, default=1.5, help="Sleep between requests (default 1.5; increase if 429)")
    ap.add_argument("--max-seconds", type=int, default=0, help="Stop odds stage after N seconds (0 = no limit)")
    ap.add_argument("--limit", type=int, default=0, help="Limit odds rows this run (0 = no limit)")
    ap.add_argument("--flush-every", type=int, default=25, help="Flush odds cache every N fetched rows")
    args = ap.parse_args()

    LOCALDATA.mkdir(exist_ok=True)
    if args.stage in ("results", "all"):
        print(f"BetExplorer results backfill: {args.start} -> {args.end}")
        backfill_results(args.start, args.end, sleep=min(args.sleep, 1.0))
    if args.stage in ("odds", "all"):
        print(f"BetExplorer odds backfill: {args.start} -> {args.end}")
        backfill_odds(args.start, args.end, sleep=args.sleep, max_seconds=args.max_seconds,
                      limit=args.limit, flush_every=args.flush_every)


if __name__ == "__main__":
    main()
