#!/usr/bin/env python3
"""Offline evidence report for SportyTrader's 7% corroboration gate.

The report only reads archived ``picks_morning_YYYY-MM-DD.json`` boards and
saved SportyTrader shadow ledgers. It never fetches the network and never
changes a pick or an odds value.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_DEV = 0.07


def _key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _load_json(path: Path, fallback):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError, TypeError):
        return fallback


def _money_relevant(pick: dict[str, Any]) -> bool:
    try:
        odds = float(pick.get("odds"))
    except (TypeError, ValueError):
        return False
    return odds > 1.0 and pick.get("price_push_eligible") is not False and pick.get("bucket") != "SKIPPED_VETO"


def _shadow_rows(localdata: Path, days: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for day in days:
        payload = _load_json(localdata / f"sportytrader_odds_shadow_{day}.json", {})
        if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
            rows.extend(row for row in payload["rows"] if isinstance(row, dict))
    return rows


def _matches(pick: dict[str, Any], row: dict[str, Any]) -> bool:
    return (
        (not row.get("date") or str(row.get("date")) == str(pick.get("date") or ""))
        and _key(row.get("home")) == _key(pick.get("home"))
        and _key(row.get("away")) == _key(pick.get("away"))
        and str(row.get("market") or "") == str(pick.get("market") or "")
        and str(row.get("selection") or "") == str(pick.get("pick") or "")
        and bool(row.get("bookmaker"))
    )


def build_report(localdata: Path, n: int = 14) -> dict[str, Any]:
    archives = sorted(localdata.glob("picks_morning_*.json"))[-max(0, int(n)):]
    days = [path.stem.removeprefix("picks_morning_") for path in archives]
    shadow = _shadow_rows(localdata, days)
    candidates: list[dict[str, Any]] = []
    money_relevant = 0
    gained = 0
    for archive in archives:
        payload = _load_json(archive, [])
        if not isinstance(payload, list):
            continue
        for pick in payload:
            if not isinstance(pick, dict) or not _money_relevant(pick):
                continue
            money_relevant += 1
            odds = float(pick["odds"])
            quotes = [row for row in shadow if _matches(pick, row)]
            # Archived boards can carry a quote even when the separate shadow
            # ledger was pruned; accept that as evidence but keep source/book.
            quotes.extend(
                entry for entry in (pick.get("price_board") or [])
                if isinstance(entry, dict) and str(entry.get("source") or "") == "sportytrader_odds"
                and _matches(pick, entry)
            )
            seen = set()
            valid = []
            for quote in quotes:
                try:
                    quote_odds = float(quote.get("odds"))
                except (TypeError, ValueError):
                    continue
                identity = (str(quote.get("bookmaker")), quote_odds, str(quote.get("captured_at")))
                if quote_odds > 1.0 and identity not in seen:
                    seen.add(identity)
                    valid.append({"bookmaker": quote.get("bookmaker"), "odds": quote_odds, "captured_at": quote.get("captured_at")})
            close = [quote for quote in valid if abs(quote["odds"] / odds - 1.0) <= MAX_DEV]
            got = bool(close)
            gained += got
            candidates.append({
                "date": pick.get("date"), "home": pick.get("home"), "away": pick.get("away"),
                "market": pick.get("market"), "selection": pick.get("pick"), "chosen_odds": odds,
                "corroborators": close, "gained": got,
            })
    rate = gained / money_relevant if money_relevant else None
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window_days": days,
        "n_archives": len(archives),
        "money_relevant": money_relevant,
        "gained_sportytrader_within_7pct": gained,
        "rate": rate,
        "test_7pct": {"eligible": money_relevant, "gained": gained, "rate": rate, "max_deviation": MAX_DEV},
        "integration_recommendation": "remain_off" if not gained else "operator_review_required",
        "legs": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=14)
    parser.add_argument("--localdata", type=Path, default=ROOT / "localdata")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(args.localdata, args.n)
    output = args.output or args.localdata / "sportytrader_7pct_report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True))
    test = report["test_7pct"]
    print(
        f"test_7pct eligible={test['eligible']} gained={test['gained']} "
        f"rate={test['rate'] if test['rate'] is not None else 'n/a'} "
        f"max_deviation={test['max_deviation']:.0%}"
    )
    print(f"report={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
