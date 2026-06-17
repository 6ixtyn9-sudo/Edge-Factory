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

Failure cache
-------------
Terminal 404s are written to:
    localdata/betexplorer_odds_failures_YYYY-MM.csv.gz

Known terminal failures are skipped on later runs unless --retry-failures is
provided. This prevents the final stale BetExplorer URLs from being retried
forever.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import html
import json
import math
import random
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
BASE = "https://www.betexplorer.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

sys.path.insert(0, str(ROOT / "src"))
try:
    from edgefactory.util import norm_team  # type: ignore  # noqa: E402
except Exception:  # pragma: no cover - fallback for standalone script checks
    def norm_team(name: str, width: int = 9) -> str:  # type: ignore
        return re.sub(r"[^a-z]", "", str(name or "").lower())[:width]

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

FAILURE_COLUMNS = [
    "date", "event_id", "match_url", "home", "away", "error", "failed_at",
]


class TerminalFetchError(RuntimeError):
    """Non-retryable fetch failure, e.g. BetExplorer stale 404 match URL."""


@dataclass
class FetchStats:
    fetched: int = 0
    skipped: int = 0
    failed: int = 0
    terminal_failed: int = 0
    transient_failed: int = 0
    written: int = 0
    failures_written: int = 0


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def month_key(day: str) -> str:
    return day[:7]


def results_path(month: str) -> Path:
    return LOCALDATA / f"betexplorer_results_{month}.csv.gz"


def odds_path(month: str) -> Path:
    return LOCALDATA / f"betexplorer_odds_{month}.csv.gz"


def failures_path(month: str) -> Path:
    return LOCALDATA / f"betexplorer_odds_failures_{month}.csv.gz"


def _retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    value = exc.headers.get("Retry-After") if exc.headers else None
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None


def _nap(base: float, jitter: float) -> None:
    delay = max(0.0, base)
    if jitter > 0:
        delay += random.uniform(0.0, jitter)
    if delay:
        time.sleep(delay)


def fetch(
    url: str,
    *,
    referer: str | None = None,
    retries: int = 5,
    sleep: float = 1.0,
    jitter: float = 0.0,
) -> str:
    """Fetch URL with 429 Retry-After support and jittered backoff.

    404 is treated as terminal because BetExplorer result archives sometimes
    point at stale match URLs that no longer resolve.
    """
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
            if exc.code == 404:
                raise TerminalFetchError(f"HTTP 404: {url}") from exc
            if exc.code == 429:
                retry_after = _retry_after_seconds(exc)
                wait = retry_after if retry_after is not None else max(5.0, sleep * (attempt + 2) * 3)
                _nap(wait, jitter)
            elif attempt < retries - 1:
                _nap(sleep * (attempt + 1), jitter)
        except Exception as exc:  # noqa: BLE001 - data job should retry generic network errors
            last = exc
            if attempt < retries - 1:
                _nap(sleep * (attempt + 1), jitter)
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
        page = fetch(url, sleep=sleep, jitter=0.2)
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


def fetch_odds_for_result(row: dict, *, sleep: float, jitter: float) -> dict:
    match_url = str(row["match_url"])
    event_id = str(row["event_id"])
    _nap(sleep, jitter)
    match_html = fetch(match_url, referer=BASE, sleep=sleep, jitter=jitter)
    page_param = parse_page_param(match_html)
    odds_url = f"{BASE}/match-odds/{event_id}/{page_param}/1x2/bestOdds/?lang=en"
    _nap(sleep, jitter)
    data = json.loads(fetch(odds_url, referer=match_url, sleep=sleep, jitter=jitter))
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


def _avgp_sql(col: str = "avg_p") -> str:
    return f"CASE WHEN {col} > 1.5 THEN {col} ELSE {col}*100 END"


def load_warehouse_candidate_keys(warehouse: Path, start: str, end: str, threshold: float) -> set[tuple[str, str, str]]:
    """Return (date,hkey,akey) for broad EF consensus candidate rows.

    This is an odds-fetch prioritizer only. It intentionally uses a broad
    threshold (default 60) so BetExplorer odds are fetched for plausible EF
    overlap rows before fetching the whole BetExplorer universe. It does not
    certify or create edges.
    """
    try:
        import duckdb
    except Exception as exc:
        raise RuntimeError("--only-warehouse-candidates requires duckdb") from exc

    if not warehouse.exists():
        raise RuntimeError(f"warehouse not found: {warehouse}")

    con = duckdb.connect(str(warehouse), read_only=True)
    keys: set[tuple[str, str, str]] = set()

    queries = [
        (
            "consensus2",
            f"""
            SELECT date, home, away
            FROM consensus2
            WHERE date >= ? AND date <= ?
              AND fb_pick = zb_pick
              AND {_avgp_sql('avg_p')} >= ?
            """,
        ),
        (
            "consensus3",
            f"""
            SELECT date, home, away
            FROM consensus3
            WHERE date >= ? AND date <= ?
              AND fb_pick = zb_pick AND zb_pick = sa_pick
              AND {_avgp_sql('avg_p')} >= ?
            """,
        ),
    ]

    for name, sql in queries:
        try:
            for day, home, away in con.execute(sql, [start, end, threshold]).fetchall():
                keys.add((str(day)[:10], norm_team(str(home or "")), norm_team(str(away or ""))))
        except Exception as exc:
            print(f"  WARN: warehouse candidate query skipped for {name}: {exc}", file=sys.stderr)
    return keys


def load_existing_odds_ids(start: str, end: str) -> set[str]:
    months = sorted({month_key(d) for d in date_range(start, end)})
    ids: set[str] = set()
    for month in months:
        for row in read_gzip_csv(odds_path(month)):
            if row.get("event_id"):
                ids.add(str(row["event_id"]))
    return ids


def load_known_failure_ids(start: str, end: str) -> set[str]:
    months = sorted({month_key(d) for d in date_range(start, end)})
    ids: set[str] = set()
    for month in months:
        for row in read_gzip_csv(failures_path(month)):
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


def flush_failures(buffer: list[dict]) -> int:
    by_month: dict[str, list[dict]] = defaultdict(list)
    for row in buffer:
        by_month[month_key(str(row["date"]))].append(row)
    written = 0
    for month, rows in by_month.items():
        written += upsert_monthly(failures_path(month), rows, "event_id", FAILURE_COLUMNS)
    return written


def default_state_path(start: str, end: str) -> Path:
    return LOCALDATA / f"betexplorer_odds_state_{start}_{end}.json"


def write_state(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)


def failure_row(row: dict, exc: Exception) -> dict:
    return {
        "date": row.get("date"),
        "event_id": row.get("event_id"),
        "match_url": row.get("match_url"),
        "home": row.get("home"),
        "away": row.get("away"),
        "error": str(exc),
        "failed_at": now_iso(),
    }


def backfill_odds(
    start: str,
    end: str,
    *,
    sleep: float,
    jitter: float,
    max_seconds: int,
    limit: int,
    flush_every: int,
    workers: int,
    state_file: Path | None,
    retry_failures: bool,
    warehouse_candidates: Path | None,
    candidate_threshold: float,
) -> FetchStats:
    """Backfill odds concurrently, resumable by CSV event_id and failure cache."""
    stats = FetchStats()
    rows = load_result_rows(start, end)
    if not rows:
        print("No cached BetExplorer results rows. Run: backfill_betexplorer.py results START END")
        return stats

    candidate_keys: set[tuple[str, str, str]] | None = None
    if warehouse_candidates is not None:
        candidate_keys = load_warehouse_candidate_keys(warehouse_candidates, start, end, candidate_threshold)
        before = len(rows)
        rows = [
            r for r in rows
            if (str(r.get("date"))[:10], norm_team(str(r.get("home") or "")), norm_team(str(r.get("away") or "")))
            in candidate_keys
        ]
        print(
            f"warehouse candidate filter: {len(rows)} / {before} results rows "
            f"matched consensus2/3 threshold>={candidate_threshold:g} from {warehouse_candidates}"
        )

    existing = load_existing_odds_ids(start, end)
    known_failures = set() if retry_failures else load_known_failure_ids(start, end)
    pending = [
        r for r in rows
        if str(r.get("event_id")) not in existing
        and str(r.get("event_id")) not in known_failures
    ]
    if limit:
        pending = pending[:limit]
    state_path = state_file or default_state_path(start, end)
    workers = max(1, int(workers))
    if workers > 64:
        print(f"WARNING: --workers {workers} is very high; consider 24-32 unless you are intentionally stress-testing.")
    print(
        f"odds pending: {len(pending)} / results rows={len(rows)} existing_odds={len(existing)} "
        f"known_failures={len(known_failures)} workers={workers} sleep={sleep} jitter={jitter}"
    )

    started = time.monotonic()
    buffer: list[dict] = []
    failure_buffer: list[dict] = []
    attempted = 0
    submitted = 0
    completed = 0
    failures: list[dict] = []

    def state_payload() -> dict:
        elapsed = round(time.monotonic() - started, 1)
        return {
            "stage": "odds",
            "start": start,
            "end": end,
            "updated_at": now_iso(),
            "elapsed_seconds": elapsed,
            "workers": workers,
            "sleep": sleep,
            "jitter": jitter,
            "results_rows": len(rows),
            "warehouse_candidates": str(warehouse_candidates) if warehouse_candidates else None,
            "candidate_threshold": candidate_threshold if warehouse_candidates else None,
            "candidate_keys": len(candidate_keys) if candidate_keys is not None else None,
            "existing_odds_at_start": len(existing),
            "known_failures_at_start": len(known_failures),
            "pending_at_start": len(pending),
            "submitted": submitted,
            "completed": completed,
            "fetched": stats.fetched,
            "failed": stats.failed,
            "terminal_failed": stats.terminal_failed,
            "transient_failed": stats.transient_failed,
            "written_new": stats.written,
            "failures_written": stats.failures_written,
            "remaining_estimate": max(0, len(pending) - completed),
            "recent_failures": failures[-20:],
        }

    def flush_if_needed(force: bool = False) -> None:
        if buffer and (force or len(buffer) >= flush_every):
            stats.written += flush_odds(buffer)
            buffer.clear()
        if failure_buffer and (force or len(failure_buffer) >= flush_every):
            stats.failures_written += flush_failures(failure_buffer)
            failure_buffer.clear()
        if force:
            write_state(state_path, state_payload())

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        in_flight: dict[concurrent.futures.Future, dict] = {}
        iterator = iter(pending)

        def submit_more() -> None:
            nonlocal submitted
            while len(in_flight) < workers * 2:
                if max_seconds and time.monotonic() - started >= max_seconds:
                    return
                try:
                    row = next(iterator)
                except StopIteration:
                    return
                fut = ex.submit(fetch_odds_for_result, row, sleep=sleep, jitter=jitter)
                in_flight[fut] = row
                submitted += 1

        submit_more()
        max_printed = False
        while in_flight:
            if max_seconds and time.monotonic() - started >= max_seconds and not max_printed:
                print("max_seconds reached; waiting for in-flight requests to finish")
                max_printed = True
            done, _ = concurrent.futures.wait(
                in_flight,
                timeout=1.0,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            if not done:
                if max_seconds and time.monotonic() - started >= max_seconds:
                    break
                continue
            for fut in done:
                row = in_flight.pop(fut)
                completed += 1
                attempted += 1
                try:
                    buffer.append(fut.result())
                    stats.fetched += 1
                except TerminalFetchError as exc:
                    stats.failed += 1
                    stats.terminal_failed += 1
                    fr = failure_row(row, exc)
                    failure_buffer.append(fr)
                    failures.append(fr)
                    if stats.terminal_failed <= 20:
                        print(f"  WARN terminal {row.get('date')} {row.get('home')} vs {row.get('away')}: {exc}", file=sys.stderr)
                except Exception as exc:  # noqa: BLE001 - transient job continues but is not cached as terminal
                    stats.failed += 1
                    stats.transient_failed += 1
                    fr = failure_row(row, exc)
                    failures.append(fr)
                    if stats.transient_failed <= 20:
                        print(f"  WARN transient {row.get('date')} {row.get('home')} vs {row.get('away')}: {exc}", file=sys.stderr)
                if len(buffer) >= flush_every or len(failure_buffer) >= flush_every:
                    flush_if_needed(force=True)
                if attempted % 25 == 0:
                    write_state(state_path, state_payload())
                    print(
                        f"  odds attempts {attempted}/{len(pending)} submitted={submitted} "
                        f"fetched={stats.fetched} failed={stats.failed} "
                        f"terminal={stats.terminal_failed} transient={stats.transient_failed} "
                        f"written_new={stats.written} failures_written={stats.failures_written}"
                    )
            if not (max_seconds and time.monotonic() - started >= max_seconds):
                submit_more()

        # Harvest any already-finished in-flight futures after max_seconds stop.
        for fut, row in list(in_flight.items()):
            if fut.done():
                try:
                    buffer.append(fut.result())
                    stats.fetched += 1
                except TerminalFetchError as exc:
                    stats.failed += 1
                    stats.terminal_failed += 1
                    failure_buffer.append(failure_row(row, exc))
                except Exception:
                    stats.failed += 1
                    stats.transient_failed += 1

    flush_if_needed(force=True)
    print(f"state -> {state_path}")
    print(
        f"odds done: fetched={stats.fetched} failed={stats.failed} "
        f"terminal={stats.terminal_failed} transient={stats.transient_failed} "
        f"written_new={stats.written} failures_written={stats.failures_written}"
    )
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill BetExplorer results and 1X2 odds caches")
    ap.add_argument("stage", choices=["results", "odds", "all"], help="Which stage to run")
    ap.add_argument("start", help="Start date YYYY-MM-DD")
    ap.add_argument("end", help="End date YYYY-MM-DD")
    ap.add_argument("--sleep", type=float, default=1.0, help="Base sleep per request inside each worker (default 1.0)")
    ap.add_argument("--jitter", type=float, default=0.75, help="Random extra sleep per request, seconds (default 0.75)")
    ap.add_argument("--workers", type=int, default=4, help="Concurrent odds workers (default 4)")
    ap.add_argument("--max-seconds", type=int, default=0, help="Stop odds stage after N seconds (0 = no limit)")
    ap.add_argument("--limit", type=int, default=0, help="Limit odds rows this run (0 = no limit)")
    ap.add_argument("--flush-every", type=int, default=50, help="Flush odds/failure cache every N fetched rows")
    ap.add_argument("--state-file", default=None, help="JSON state file path (default localdata/betexplorer_odds_state_START_END.json)")
    ap.add_argument("--retry-failures", action="store_true", help="Retry event_ids in betexplorer_odds_failures_YYYY-MM.csv.gz")
    ap.add_argument(
        "--only-warehouse-candidates",
        nargs="?",
        const=str(LOCALDATA / "warehouse.duckdb"),
        default=None,
        help=(
            "Odds stage only: fetch odds only for BetExplorer results matching broad "
            "consensus2/3 candidates in the given DuckDB warehouse. If no path is "
            "provided, defaults to localdata/warehouse.duckdb."
        ),
    )
    ap.add_argument(
        "--candidate-threshold",
        type=float,
        default=60.0,
        help="Broad avg_p threshold for --only-warehouse-candidates (default: 60)",
    )
    args = ap.parse_args()

    LOCALDATA.mkdir(exist_ok=True)
    if args.stage in ("results", "all"):
        print(f"BetExplorer results backfill: {args.start} -> {args.end}")
        backfill_results(args.start, args.end, sleep=min(args.sleep, 1.0))
    if args.stage in ("odds", "all"):
        print(f"BetExplorer odds backfill: {args.start} -> {args.end}")
        backfill_odds(
            args.start,
            args.end,
            sleep=args.sleep,
            jitter=args.jitter,
            max_seconds=args.max_seconds,
            limit=args.limit,
            flush_every=args.flush_every,
            workers=args.workers,
            state_file=Path(args.state_file) if args.state_file else None,
            retry_failures=args.retry_failures,
            warehouse_candidates=Path(args.only_warehouse_candidates) if args.only_warehouse_candidates else None,
            candidate_threshold=args.candidate_threshold,
        )


if __name__ == "__main__":
    main()
