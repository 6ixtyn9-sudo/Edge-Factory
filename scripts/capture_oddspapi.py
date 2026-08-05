#!/usr/bin/env python3
"""Bounded OddsPapi price capture for the enhancement overlay (Addendum 27.7).

Operator override 2026-08-05 authorizes OddsPapi as a real price source for
enhancement markets the other feeds do not price (team totals, double chance,
totals lines, btts, 1x2). This script performs BOUNDED, read-only capture of
OddsPapi odds into the unified schema used by `enh_pricing`:

    localdata/oddspapi_odds_YYYY-MM.csv.gz

Safety rails (operator-approved):
- FREE-TIER BOUNDED: OddsPapi free quota is small. Capture is limited to a
  bounded set of fixtures per run (--max-fixtures, default 20) and never
  broad-polls the whole day. Unmatched same-day picks are prioritized first,
  then enhancement-relevant fixtures.
- FLAG-GATED: this script is NOT in daily.py/capture_daily.py by default.
  It is meant to be run explicitly (or wired via
  EDGE_FACTORY_ODDSPAPI_PRICES=1). Fail-soft: any error degrades to "no
  rows" and never raises into a caller.
- KEYS STAY LOCAL: ODDSPAPI_API_KEYS is read from .env; never printed,
  logged, committed, or placed in Actions.
- WALK-FORWARD ONLY: rows accumulate from activation forward; no backfill,
  no retrospective validation.
- No selection / certification / source-weight / push change. This is a
  price source for the enhancement overlay only.

Usage:
  PYTHONPATH=src python3 scripts/capture_oddspapi.py --date 2026-08-05 [--max-fixtures 20]
  PYTHONPATH=src python3 scripts/capture_oddspapi.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from edgefactory.sources.oddspapi_odds import (
    api_keys,
    fetch_fixtures,
    fetch_odds,
    load_market_type_map,
    market_catalog,
    rows_from_odds_response,
)

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "localdata"

COLUMNS = ["source", "source_type", "sport", "date", "kickoff", "league",
           "home", "away", "market", "selection", "odds", "bookmaker",
           "captured_at"]


def _out_path(day: str) -> Path:
    return OUT_DIR / f"oddspapi_odds_{day[:7]}.csv.gz"


def _append_rows(rows: list[dict], day: str) -> int:
    """Append rows to the unified store, deduped on the full row (idempotent re-runs)."""
    path = _out_path(day)
    path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[tuple] = set()
    if path.exists():
        with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                seen.add(tuple(r.get(k) for k in COLUMNS))
    added = 0
    fresh = []
    for r in rows:
        key = tuple(str(r.get(k) or "") for k in COLUMNS)
        if key in seen:
            continue
        seen.add(key)
        fresh.append(r)
        added += 1
    if fresh:
        with gzip.open(path, "at", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS)
            if path.stat().st_size == 0:
                w.writeheader()
            for r in fresh:
                w.writerow({k: r.get(k) for k in COLUMNS})
    return added


def capture(day: str, max_fixtures: int = 20) -> dict:
    """Bounded capture for one day. Returns a stats dict; never raises."""
    stats = {"keys": 0, "fixtures": 0, "matched": 0, "rows": 0, "added": 0,
             "errors": [], "markets": {}}
    try:
        keys = api_keys()
        stats["keys"] = len(keys)
        if not keys:
            stats["errors"].append("no ODDSPAPI_API_KEYS configured")
            return stats
        fixtures = fetch_fixtures(day) or []
        stats["fixtures"] = len(fixtures)
        type_map = load_market_type_map()
        catalog = market_catalog()
        # Compact summary only — the full catalog is thousands of ids and
        # dumping it is bloat. Counts + a few (id, label) samples per type
        # let us verify classification (e.g. that "totals" are goal totals,
        # not corners/cards, and team totals are not folded into totals).
        by_type: dict[str, dict] = {}
        for mid, mtype in type_map.items():
            slot = by_type.setdefault(mtype, {"count": 0, "samples": []})
            slot["count"] += 1
            if len(slot["samples"]) < 5:
                slot["samples"].append({"id": mid, "label": catalog.get(mid, "?")})
        stats["type_map_summary"] = by_type
        for fx in fixtures[:max_fixtures]:
            fid = str(fx.get("fixtureId") or fx.get("id") or "")
            if not fid:
                continue
            try:
                odds = fetch_odds(fid)
            except Exception as exc:  # noqa: BLE001 - fail-soft
                stats["errors"].append(f"fetch {fid}: {type(exc).__name__}")
                continue
            # Payload-vs-emitted accounting: which market ids actually appear
            # in the fixture payload, and which rows we got. If a non-1x2 id
            # appears in the payload but no rows for it are emitted, the
            # parser is dropping it (name/line shape) — the sample shows why.
            if odds:
                books = (odds or {}).get("bookmakerOdds") or {}
                for _b, bd in books.items():
                    if not isinstance(bd, dict):
                        continue
                    for mid, mkt in (bd.get("markets") or {}).items():
                        mid_s = str(mid)
                        if type_map.get(mid_s, "1x2") == "1x2":
                            continue
                        stats["payload_non1x2"] = stats.get("payload_non1x2", 0) + 1
                        if stats.get("payload_non1x2") <= 5 and isinstance(mkt, dict):
                            oc = next(iter((mkt.get("outcomes") or {}).values()), None)
                            p0 = ((oc or {}).get("players") or {}).get("0") if isinstance(oc, dict) else None
                            stats.setdefault("non1x2_samples", []).append({
                                "market_id": mid_s,
                                "type": type_map.get(mid_s),
                                "label": catalog.get(mid_s),
                                "market_keys": sorted(mkt.keys()) if isinstance(mkt, dict) else None,
                                "market_non_outcome": {k: v for k, v in mkt.items() if k != "outcomes" and k != "players"} if isinstance(mkt, dict) else None,
                                "outcome_keys": sorted(oc.keys()) if isinstance(oc, dict) else None,
                                "player0_keys": sorted(p0.keys()) if isinstance(p0, dict) else None,
                                "player0_nonbet_fields": {k: v for k, v in p0.items() if k != "betslip"} if isinstance(p0, dict) else None,
                            })
            rows = rows_from_odds_response(odds, market_type_map=type_map) if odds else []
            if rows:
                stats["matched"] += 1
            stats["rows"] += len(rows)
            for r in rows:
                m = str(r.get("market") or "?")
                stats["markets"][m] = stats["markets"].get(m, 0) + 1
            stats["added"] += _append_rows(rows, day)
        return stats
    except Exception as exc:  # noqa: BLE001 - never raises
        stats["errors"].append(f"capture: {type(exc).__name__}: {exc}")
        return stats


def self_test() -> int:
    """Offline self-test of the write path with a synthetic payload."""
    failures: list[str] = []

    def check(label: str, cond: bool) -> None:
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            failures.append(label)

    sample = {
        "fixtureId": "fx_test_1",
        "participant1Name": "Halmstads BK",
        "participant2Name": "IK Sirius",
        "startTime": "2026-08-03T17:00:00Z",
        "tournamentName": "Allsvenskan",
        "categoryName": "Sweden",
        "bookmakerOdds": {
            "Pinnacle": {"markets": {
                "101": {"outcomes": {
                    "o1": {"players": {"0": {"bookmakerOutcomeId": "home", "price": 2.10}}},
                    "ox": {"players": {"0": {"bookmakerOutcomeId": "draw", "price": 3.40}}},
                    "o2": {"players": {"0": {"bookmakerOutcomeId": "away", "price": 3.25}}},
                }},
                "103": {"outcomes": {
                    "b1": {"players": {"0": {"name": "Yes", "price": 1.95}}},
                    "b2": {"players": {"0": {"name": "No", "price": 1.80}}},
                }},
                "108": {"outcomes": {
                    "d1": {"players": {"0": {"name": "HomeOrDraw", "price": 1.05}}},
                    "d2": {"players": {"0": {"name": "HomeOrAway", "price": 1.02}}},
                }},
                "115": {"outcomes": {
                    "t1": {"players": {"0": {"name": "Halmstads BK Over 1.5", "price": 1.30}}},
                    "t2": {"players": {"0": {"name": "IK Sirius Under 1.5", "price": 2.10}}},
                }},
                "107": {"outcomes": {
                    "t3": {"players": {"0": {"name": "Over 2.5", "price": 1.85}}},
                }},
            }},
        },
    }
    rows = rows_from_odds_response(sample, market_type_map={
        "101": "1x2", "103": "btts", "108": "double_chance",
        "115": "team_totals", "107": "totals",
    })
    check("10 rows parsed (3x 1x2 + 2x btts + 2x dc + 2x team_totals + 1x totals)",
          len(rows) == 10)
    markets = {(r["market"], r["selection"]) for r in rows}
    check("1x2 home/draw/away", {("1x2", "home"), ("1x2", "draw"), ("1x2", "away")} <= markets)
    check("btts yes/no", {("btts", "yes"), ("btts", "no")} <= markets)
    check("double chance 1x/12", {("dc", "1x"), ("dc", "12")} <= markets)
    check("team totals tt_home_1.5 over", ("tt_home_1.5", "over") in markets)
    check("team totals tt_away_1.5 under", ("tt_away_1.5", "under") in markets)
    check("totals ou_2.5 over", ("ou_2.5", "over") in markets)
    check("unified schema columns", all(set(COLUMNS) <= set(r.keys()) for r in rows))
    check("all source=oddspapi", all(r["source"] == "oddspapi" for r in rows))

    # write-path: append + dedupe
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # redirect OUT_DIR
        global OUT_DIR
        _orig = OUT_DIR
        OUT_DIR = Path(td)
        try:
            added1 = _append_rows(rows, "2026-08-03")
            added2 = _append_rows(rows, "2026-08-03")
        finally:
            OUT_DIR = _orig
        check("append adds 10 then dedupes to 0", added1 == 10 and added2 == 0)

    if failures:
        print(f"self-test: FAIL ({len(failures)} failures)")
        return 1
    print("self-test: PASS (0 failures)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    ap.add_argument("--max-fixtures", type=int, default=20)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    stats = capture(args.date, args.max_fixtures)
    print(json.dumps(stats, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
