#!/usr/bin/env python3
"""Read-only OddsPapi market-coverage probe for Edge Factory.

This is deliberately NOT a production odds adapter. It consumes a small list of
existing Edge Factory fixtures, asks whether OddsPapi can resolve them, and
summarizes bookmaker/market availability without changing picks, ledgers,
notifications, or the daily pipeline.

Examples
--------
PYTHONPATH=src python3 scripts/probe_oddspapi_markets.py --date 2026-08-05
PYTHONPATH=src python3 scripts/probe_oddspapi_markets.py --date 2026-08-05 --bookmaker betano,betway
PYTHONPATH=src python3 scripts/probe_oddspapi_markets.py --self-test

Credential contract
-------------------
ODDSPAPI_API_KEYS=key1,key2,key3,key4 is preferred. The helper tries the ring
sequentially only on auth/quota rejections. Values are never printed, written,
or included in output JSON.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from edgefactory.sources import oddspapi_odds  # noqa: E402
from edgefactory.util import fold_ascii  # noqa: E402

LOCALDATA = ROOT / "localdata"
CLUB_NOISE = {"fc", "cf", "sc", "ac", "as", "pfc", "ofc", "gnk", "fk", "afc", "club", "the"}


def _team_key(value: object) -> str:
    tokens = re.findall(r"[a-z0-9]+", fold_ascii(value))
    meaningful = [token for token in tokens if token not in CLUB_NOISE]
    return " ".join(meaningful)


def _fixture_names(fixture: dict[str, Any]) -> tuple[str, str]:
    home = fixture.get("participant1Name") or fixture.get("home") or fixture.get("homeTeam") or ""
    away = fixture.get("participant2Name") or fixture.get("away") or fixture.get("awayTeam") or ""
    return str(home), str(away)


def match_fixture(target: dict[str, Any], fixture: dict[str, Any]) -> str | None:
    """Exact normalized-pair match only. Coverage probe never claims a fuzzy
    fixture match; aliases/ambiguous names are reported unmatched for review."""
    th, ta = _team_key(target.get("home")), _team_key(target.get("away"))
    fh_raw, fa_raw = _fixture_names(fixture)
    fh, fa = _team_key(fh_raw), _team_key(fa_raw)
    if th and ta and th == fh and ta == fa:
        return "exact_pair"
    if th and ta and th == fa and ta == fh:
        return "exact_pair_swapped"
    return None


def load_targets(path: Path, start: str, days: int, limit: int) -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text())
    except Exception:
        raw = []
    if not isinstance(raw, list):
        return []
    end = (date.fromisoformat(start) + timedelta(days=max(0, days - 1))).isoformat()
    seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        day = str(row.get("date") or row.get("picked_for") or "")[:10]
        home, away = _team_key(row.get("home")), _team_key(row.get("away"))
        if not (start <= day <= end and home and away):
            continue
        key = (day, home, away)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "date": day,
            "home": row.get("home"),
            "away": row.get("away"),
            "match": row.get("match") or f"{row.get('home')} vs {row.get('away')}",
        })
    return out[:limit]


def _market_catalog_map(payload: Any) -> dict[str, str]:
    """Best-effort parser for the optional /markets endpoint. The probe remains
    useful if the plan/API does not expose market metadata."""
    if isinstance(payload, dict):
        rows = payload.get("data") or payload.get("markets") or []
    else:
        rows = payload
    out: dict[str, str] = {}
    if not isinstance(rows, list):
        return out
    for item in rows:
        if not isinstance(item, dict):
            continue
        ident = item.get("marketId") or item.get("id")
        label = item.get("marketName") or item.get("name") or item.get("label")
        if ident is not None and label:
            out[str(ident)] = str(label)
    return out


def _category(label: str) -> str:
    text = label.lower()
    if "team total" in text:
        return "team_totals"
    if "both teams" in text or "btts" in text:
        return "btts"
    if "draw no bet" in text:
        return "draw_no_bet"
    if "double chance" in text:
        return "double_chance"
    if "exact score" in text or "correct score" in text:
        return "exact_score"
    if "handicap" in text or "spread" in text:
        return "handicap"
    if "total" in text or "over" in text or "under" in text:
        return "totals"
    if "&" in text or "combo" in text or "same game" in text:
        return "combination"
    return "other"


def summarize_odds(payload: dict[str, Any], catalog: dict[str, str], wanted_books: set[str]) -> dict[str, Any]:
    fixture_id = str(payload.get("fixtureId") or "")
    home, away = _fixture_names(payload)
    books = payload.get("bookmakerOdds") or {}
    summaries: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    for bookmaker, data in books.items() if isinstance(books, dict) else []:
        if not isinstance(data, dict):
            continue
        markets = data.get("markets") or {}
        if not isinstance(markets, dict):
            continue
        market_ids = sorted(str(key) for key in markets)
        labels = [catalog.get(market_id, f"id:{market_id}") for market_id in market_ids]
        categories = sorted({_category(label) for label in labels})
        category_counts.update(categories)
        outcome_count = 0
        for market in markets.values():
            if isinstance(market, dict) and isinstance(market.get("outcomes"), dict):
                outcome_count += len(market["outcomes"])
        summaries.append({
            "bookmaker": str(bookmaker),
            "target_book": str(bookmaker).lower() in wanted_books if wanted_books else None,
            "market_count": len(market_ids),
            "outcome_count": outcome_count,
            "market_ids": market_ids,
            "market_labels": labels,
            "categories": categories,
            "fixture_path": data.get("fixturePath"),
        })
    summaries.sort(key=lambda row: (-row["market_count"], row["bookmaker"]))
    return {
        "fixture_id": fixture_id,
        "provider_home": home,
        "provider_away": away,
        "bookmaker_count": len(summaries),
        "bookmakers": summaries,
        "category_book_counts": dict(sorted(category_counts.items())),
    }


def _date_window(start: str, days: int) -> tuple[str, str]:
    end = (date.fromisoformat(start) + timedelta(days=max(0, days - 1))).isoformat()
    return f"{start}T00:00:00Z", f"{(date.fromisoformat(end) + timedelta(days=1)).isoformat()}T00:00:00Z"


def run_probe(start: str, days: int, picks_path: Path, limit: int, wanted_books: set[str]) -> dict[str, Any]:
    targets = load_targets(picks_path, start, days, limit)
    start_ts, end_ts = _date_window(start, days)
    fixtures_payload = oddspapi_odds.fetch_json(
        "/fixtures",
        {
            "sportId": oddspapi_odds.SPORT_ID_SOCCER,
            "from": start_ts,
            "to": end_ts,
            "statusId": 0,
            "hasOdds": "true",
        },
    )
    fixtures = fixtures_payload if isinstance(fixtures_payload, list) else []

    try:
        catalog_payload = oddspapi_odds.fetch_json(
            "/markets", {"sportId": oddspapi_odds.SPORT_ID_SOCCER, "language": "en"}
        )
    except Exception as exc:  # optional endpoint/plan; never abort coverage
        catalog_payload = {"_error": type(exc).__name__}
    catalog = _market_catalog_map(catalog_payload)

    matched: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    for target in targets:
        candidates = [(fixture, match_fixture(target, fixture)) for fixture in fixtures]
        candidates = [(fixture, method) for fixture, method in candidates if method]
        if len(candidates) != 1:
            unmatched.append({
                **target,
                "reason": "not_found" if not candidates else "ambiguous_exact_match",
                "candidate_count": len(candidates),
            })
            continue
        fixture, method = candidates[0]
        fixture_id = str(fixture.get("fixtureId") or "")
        if not fixture_id:
            unmatched.append({**target, "reason": "missing_fixture_id", "candidate_count": 1})
            continue
        odds_payload = oddspapi_odds.fetch_odds(fixture_id)
        summary = summarize_odds(odds_payload, catalog, wanted_books)
        matched.append({**target, "match_method": method, **summary})

    return {
        "probe_kind": "read_only_oddspapi_market_coverage",
        "key_count": len(oddspapi_odds.api_keys()),
        "start": start,
        "days": days,
        "targets_requested": len(targets),
        "fixtures_returned": len(fixtures),
        "market_catalog_labels": len(catalog),
        "wanted_bookmakers": sorted(wanted_books),
        "matched": matched,
        "unmatched": unmatched,
    }


def self_test() -> int:
    target = {"home": "AS Roma", "away": "GNK Dinamo Zagreb"}
    fixture = {"participant1Name": "Roma", "participant2Name": "Dinamo Zagreb"}
    assert match_fixture(target, fixture) == "exact_pair"
    payload = {
        "fixtureId": "f1",
        "participant1Name": "Roma",
        "participant2Name": "Dinamo Zagreb",
        "bookmakerOdds": {
            "book_a": {"markets": {"101": {"outcomes": {"a": {}, "b": {}}}, "900": {"outcomes": {"c": {}}}}}
        },
    }
    summary = summarize_odds(payload, {"101": "1X2", "900": "Away Team Total Goals"}, {"book_a"})
    assert summary["bookmaker_count"] == 1
    assert summary["bookmakers"][0]["target_book"] is True
    assert "team_totals" in summary["bookmakers"][0]["categories"]
    print("OddsPapi coverage probe self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat(), help="Probe start date (YYYY-MM-DD).")
    parser.add_argument("--days", type=int, default=2, help="Inclusive coverage window length (default: 2).")
    parser.add_argument("--picks", default=str(LOCALDATA / "picks_next_2days.json"), help="Existing picks JSON used only as fixture targets.")
    parser.add_argument("--limit", type=int, default=6, help="Maximum unique target fixtures (default: 6).")
    parser.add_argument("--bookmaker", default="", help="Optional comma-separated bookmaker slugs to flag in output.")
    parser.add_argument("--out", default=None, help="Optional JSON report path. Default is /tmp, never localdata.")
    parser.add_argument("--self-test", action="store_true", help="Offline parser/matcher self-test; no API calls.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not oddspapi_odds.enabled():
        print("No OddsPapi keys found. Set ODDSPAPI_API_KEYS in .env; values are never printed.", file=sys.stderr)
        return 2
    if args.days < 1 or args.limit < 1:
        parser.error("--days and --limit must be positive")

    wanted = {item.strip().lower() for item in args.bookmaker.split(",") if item.strip()}
    try:
        report = run_probe(args.date, args.days, Path(args.picks), args.limit, wanted)
    except Exception as exc:  # avoid leaking request URLs with apiKey parameters
        print(f"OddsPapi coverage probe failed: {type(exc).__name__}", file=sys.stderr)
        return 1

    out_path = Path(args.out) if args.out else Path("/tmp") / f"oddspapi_coverage_{args.date}.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"OddsPapi keys available: {report['key_count']} (values hidden)")
    print(f"Targets requested: {report['targets_requested']} | provider fixtures: {report['fixtures_returned']}")
    print(f"Matched exact pairs: {len(report['matched'])} | unmatched/ambiguous: {len(report['unmatched'])}")
    print(f"Market catalog labels resolved: {report['market_catalog_labels']}")
    for item in report["matched"]:
        top = item["bookmakers"][:5]
        print(f"\n{item['match']} -> fixture {item['fixture_id']} ({item['match_method']})")
        print(f"  bookmakers={item['bookmaker_count']} top market counts=" + ", ".join(
            f"{book['bookmaker']}:{book['market_count']}" for book in top
        ))
        print("  categories=" + ", ".join(sorted(item["category_book_counts"])))
        if wanted:
            hits = [book["bookmaker"] for book in item["bookmakers"] if book["target_book"]]
            print("  requested book hits=" + (", ".join(hits) if hits else "none"))
    for item in report["unmatched"]:
        print(f"UNMATCHED {item['match']}: {item['reason']} ({item['candidate_count']} candidate(s))")
    print(f"JSON report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
