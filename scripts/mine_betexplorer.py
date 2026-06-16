#!/usr/bin/env python3
"""BetExplorer historical odds miner (standalone probe/miner).

Purpose
-------
Mine BetExplorer *before* adding any consensus levers.

Method mirrors the existing Edge Factory data moat:

1. Walk date-addressable football results pages:
   https://www.betexplorer.com/football/results/?year=YYYY&month=MM&day=DD
2. Parse settled matches, scores, leagues, and match URLs.
3. For each match URL, call BetExplorer's own match odds JSON endpoint:
   /match-odds/<event_id>/<page_param>/1x2/bestOdds/?lang=en
4. Extract best 1/X/2 odds and bookmaker movement arrows from the odds table.
5. Report standalone historical performance. No certified levers are created.

This is intentionally not wired into daily.py or mine_consensus.py yet.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
BASE = "https://www.betexplorer.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

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

SELECTIONS = ("home", "draw", "away")


@dataclass
class MatchRow:
    date: str
    kickoff: str | None
    country: str | None
    league: str | None
    home: str
    away: str
    hs: int
    gs: int
    ht_hs: int | None
    ht_gs: int | None
    url: str
    event_id: str


def fetch(url: str, *, referer: str | None = None, retries: int = 3, sleep: float = 0.5) -> str:
    headers = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if referer:
        headers["Referer"] = referer
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001 - network scraping probe
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


def date_range(start: str, end: str) -> Iterable[str]:
    d = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    while d <= e:
        yield d.isoformat()
        d += timedelta(days=1)


def parse_event_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def parse_results_page(day: str, page: str) -> list[MatchRow]:
    out: list[MatchRow] = []
    current_country: str | None = None
    current_league: str | None = None

    # Walk tournament headers and match rows in page order.
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
        hs, gs = int(score.group(1)), int(score.group(2))

        partial = re.search(r'class="table-main__partial"[^>]*>\s*\((\d+)\s*:\s*(\d+)\s*,', token, re.S)
        ht_hs = int(partial.group(1)) if partial else None
        ht_gs = int(partial.group(2)) if partial else None

        dd, mm, yyyy, hh, minute = [int(x) for x in dt.groups()]
        match_date = date(yyyy, mm, dd).isoformat()
        kickoff = f"{hh:02d}:{minute:02d}"
        rel_url = html.unescape(link.group(1))
        full_url = rel_url if rel_url.startswith("http") else BASE + rel_url
        out.append(MatchRow(
            date=match_date,
            kickoff=kickoff,
            country=current_country,
            league=current_league,
            home=home,
            away=away,
            hs=hs,
            gs=gs,
            ht_hs=ht_hs,
            ht_gs=ht_gs,
            url=full_url,
            event_id=parse_event_id(full_url),
        ))
    return out


def parse_page_param(match_html: str) -> str:
    # match_load_tabs('A9HV9kJr', '1x2', 'SW9...', 'nBI...', '1', true, ...)
    m = re.search(r"match_load_tabs\('\w+',\s*'1x2',\s*'[^']*',\s*'[^']*',\s*'([^']+)'", match_html)
    return m.group(1) if m else "1"


def fetch_match_odds(match: MatchRow, *, sleep: float = 0.25) -> dict:
    match_html = fetch(match.url, referer=BASE)
    page_param = parse_page_param(match_html)
    odds_url = f"{BASE}/match-odds/{match.event_id}/{page_param}/1x2/bestOdds/?lang=en"
    time.sleep(sleep)
    data = json.loads(fetch(odds_url, referer=match.url))
    odds_html = data.get("odds", "")
    return parse_1x2_odds_html(odds_html)


def parse_1x2_odds_html(odds_html: str) -> dict:
    # Limit to the first/best 1X2 table.
    m = re.search(r'<tbody id="best-odds-0">(.*?)</tbody>', odds_html, re.S)
    block = m.group(1) if m else odds_html
    rows = re.findall(r'<tr\b.*?</tr>', block, re.S)

    best = [None, None, None]
    counts = [0, 0, 0]
    decreasing = [0, 0, 0]
    increasing = [0, 0, 0]
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
                decreasing[i] += 1
            if "icon__increasing" in cell:
                increasing[i] += 1

    return {
        "odd1": best[0],
        "oddx": best[1],
        "odd2": best[2],
        "bookmaker_rows": bookmaker_rows,
        "n_odd1": counts[0],
        "n_oddx": counts[1],
        "n_odd2": counts[2],
        "dec1": decreasing[0],
        "decx": decreasing[1],
        "dec2": decreasing[2],
        "inc1": increasing[0],
        "incx": increasing[1],
        "inc2": increasing[2],
    }


def outcome(match: MatchRow) -> str:
    if match.hs > match.gs:
        return "home"
    if match.hs < match.gs:
        return "away"
    return "draw"


def enrich_row(match: MatchRow, odds: dict) -> dict:
    row = {
        "date": match.date,
        "kickoff": match.kickoff,
        "country": match.country,
        "league": match.league,
        "home": match.home,
        "away": match.away,
        "hs": match.hs,
        "gs": match.gs,
        "ht_hs": match.ht_hs,
        "ht_gs": match.ht_gs,
        "outcome": outcome(match),
        "match_url": match.url,
        "event_id": match.event_id,
        **odds,
    }
    odds_list = [odds.get("odd1"), odds.get("oddx"), odds.get("odd2")]
    valid = [(i, o) for i, o in enumerate(odds_list) if o is not None]
    if valid:
        fav_i, fav_odds = min(valid, key=lambda x: x[1])
        row["fav_pick"] = SELECTIONS[fav_i]
        row["fav_odds"] = fav_odds
        row["fav_won"] = int(row["fav_pick"] == row["outcome"])
        row["fav_pnl"] = (fav_odds - 1.0) if row["fav_won"] else -1.0
        row["fav_odds_band"] = odds_band(fav_odds)
    else:
        row["fav_pick"] = row["fav_odds"] = row["fav_won"] = row["fav_pnl"] = row["fav_odds_band"] = None

    # Historical dropping-odds proxy: use bookmaker movement arrows in the odds table.
    decs = [odds.get("dec1", 0), odds.get("decx", 0), odds.get("dec2", 0)]
    counts = [odds.get("n_odd1", 0), odds.get("n_oddx", 0), odds.get("n_odd2", 0)]
    candidates = [(i, decs[i], counts[i], decs[i] / counts[i] if counts[i] else 0.0) for i in range(3)]
    steam_i, steam_dec, steam_n, steam_pct = max(candidates, key=lambda x: (x[3], x[1]))
    steam_odds = odds_list[steam_i]
    row["steam_pick"] = SELECTIONS[steam_i] if steam_n else None
    row["steam_odds"] = steam_odds
    row["steam_dec_count"] = steam_dec
    row["steam_book_count"] = steam_n
    row["steam_dec_pct"] = round(steam_pct, 4) if steam_n else None
    row["steam_won"] = int(row["steam_pick"] == row["outcome"]) if steam_n and steam_odds else None
    row["steam_pnl"] = ((steam_odds - 1.0) if row["steam_won"] else -1.0) if steam_n and steam_odds else None
    row["steam_odds_band"] = odds_band(steam_odds) if steam_odds else None
    return row


def summarize(rows: list[dict], label: str, pred_col: str, odds_col: str, pnl_col: str) -> dict:
    usable = [r for r in rows if r.get(pred_col) and r.get(odds_col) and r.get(pnl_col) is not None]
    n = len(usable)
    wins = sum(1 for r in usable if r[pred_col] == r["outcome"])
    pnl = sum(float(r[pnl_col]) for r in usable)
    avg_odds = sum(float(r[odds_col]) for r in usable) / n if n else None
    return {
        "label": label,
        "n": n,
        "wins": wins,
        "hit": wins / n if n else 0.0,
        "wilson_lb": wilson_lb(wins, n),
        "roi": pnl / n if n else 0.0,
        "avg_odds": avg_odds,
    }


def print_summary(rows: list[dict]) -> None:
    def line(s: dict) -> None:
        print(f"{s['label']:35s} n={s['n']:5d} hit={s['hit']:.1%} LB={s['wilson_lb']:.3f} ROI={s['roi']:+.1%} avg_odds={(s['avg_odds'] or 0):.2f}")

    print("\nBetExplorer standalone performance")
    print("=" * 72)
    line(summarize(rows, "favorite all", "fav_pick", "fav_odds", "fav_pnl"))
    for _, _, band in ODDS_BANDS:
        sub = [r for r in rows if r.get("fav_odds_band") == band]
        if sub:
            line(summarize(sub, f"favorite odds {band}", "fav_pick", "fav_odds", "fav_pnl"))

    print("\nDropping-odds proxy from historical odds-table movement arrows")
    print("=" * 72)
    for threshold in (0.50, 0.70, 0.90):
        sub = [r for r in rows if (r.get("steam_dec_pct") or 0) >= threshold and (r.get("steam_dec_count") or 0) >= 3]
        if sub:
            line(summarize(sub, f"steam dec_pct>={threshold:.0%}", "steam_pick", "steam_odds", "steam_pnl"))
    for min_count in (3, 5, 10):
        sub = [r for r in rows if (r.get("steam_dec_count") or 0) >= min_count]
        if sub:
            line(summarize(sub, f"steam dec_count>={min_count}", "steam_pick", "steam_odds", "steam_pnl"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Mine BetExplorer historical 1X2 odds/results standalone")
    ap.add_argument("start", help="Start date YYYY-MM-DD")
    ap.add_argument("end", help="End date YYYY-MM-DD")
    ap.add_argument("--max-matches", type=int, default=0, help="Limit match-page odds fetches for probing")
    ap.add_argument("--sleep", type=float, default=1.0, help="Sleep between match odds requests (default: 1.0; raise if 429s appear)")
    ap.add_argument("--out", default=None, help="CSV output path (default localdata/betexplorer_mined_START_END.csv)")
    args = ap.parse_args()

    all_matches: list[MatchRow] = []
    print(f"BetExplorer results archive scan: {args.start} -> {args.end}")
    for day in date_range(args.start, args.end):
        y, m, d = day.split("-")
        url = f"{BASE}/football/results/?year={y}&month={m}&day={d}"
        page = fetch(url)
        matches = parse_results_page(day, page)
        all_matches.extend(matches)
        print(f"  {day}: {len(matches)} settled result rows")

    if args.max_matches:
        all_matches = all_matches[: args.max_matches]
    print(f"Fetching odds for {len(all_matches)} settled matches...")

    rows: list[dict] = []
    failures = 0
    for i, match in enumerate(all_matches, 1):
        try:
            odds = fetch_match_odds(match, sleep=args.sleep)
            rows.append(enrich_row(match, odds))
        except Exception as exc:  # noqa: BLE001 - standalone miner should continue
            failures += 1
            if failures <= 10:
                print(f"  WARN {match.date} {match.home} vs {match.away}: {exc}", file=sys.stderr)
        if i % 25 == 0:
            print(f"  odds fetched: {i}/{len(all_matches)} rows={len(rows)} failures={failures}")

    LOCALDATA.mkdir(exist_ok=True)
    out_path = Path(args.out) if args.out else LOCALDATA / f"betexplorer_mined_{args.start}_{args.end}.csv"
    if rows:
        fieldnames = sorted({k for row in rows for k in row})
        with out_path.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {out_path} ({len(rows)} rows, failures={failures})")
        print_summary(rows)
    else:
        print(f"No odds rows mined; failures={failures}")


if __name__ == "__main__":
    main()
