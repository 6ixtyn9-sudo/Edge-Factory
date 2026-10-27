#!/usr/bin/env python3
"""Capture a bounded BetExplorer snapshot for the final pricing pass.

The daily pipeline creates a non-ticketable candidate slate first. This script
uses that slate to populate the adapter's per-fixture cache before the final
priced card is built. It never emits a ticket and never alters picks itself.

The adapter has its own cache, cooldown, and bounded-fetch protections. This
wrapper adds a durable, secret-free receipt describing what was attempted so a
later final pass can distinguish absent source supply from an unmatched quote.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA") or (ROOT / "localdata"))
DEFAULT_MAX_FIXTURES = 12
# Hard safety ceiling for cooperative BetExplorer calls.  The default remains
# 12; this only lets an operator deliberately spend more of the 30s/cache-rich
# window without editing the workflow.  The adapter still cools down on 429.
MAX_FIXTURES_CEILING = int(os.environ.get("EDGE_FACTORY_BETEXPLORER_MAX_CEILING", "24") or 24)


def _slate_paths(day: str) -> tuple[Path, ...]:
    d = str(day)[:10]
    return (LOCALDATA / "picks_today.json", LOCALDATA / f"picks_{d}.json")


def _read_same_day_rows(day: str) -> list[dict]:
    """Prefer the fresh candidate slate; fall back to the same-day archive.

    ``picks_today.json`` can hold yesterday's slate on standalone first-run
    invocations.  In that case the same-day archive is the safe fallback.
    """
    day10 = str(day)[:10]
    for path in _slate_paths(day10):
        try:
            raw = json.loads(path.read_text())
        except (OSError, ValueError, TypeError):
            continue
        rows = raw if isinstance(raw, list) else (
            raw.get("picks") if isinstance(raw, dict) else None)
        if not isinstance(rows, list):
            continue
        same_day = [r for r in rows if isinstance(r, dict)
                    and str(r.get("date") or "")[:10] == day10]
        if same_day:
            return same_day
    return []


def _enh_pricing_gap_count(row: dict) -> int:
    """Count distinct in-band missing markets this adapter can actually supply.

    This orders bounded collection only; it does not admit a leg or invent a
    quote. Team totals are not supplied by the existing BetExplorer tabs.
    """
    from edgefactory.enh_pricing import MARKET_PRICE_MAP

    notes = row.get("enh_candidate_log")
    if not isinstance(notes, list):
        return 0
    markets = set()
    for note in notes:
        if not isinstance(note, dict) or note.get("reason") != "unpriced":
            continue
        market, rate = note.get("market"), note.get("cohort_rate")
        if not isinstance(market, str):
            continue
        mapping = MARKET_PRICE_MAP.get(market)
        if (mapping and (mapping[0].startswith("ou_") or mapping[0] in {"btts", "dc"})
                and isinstance(rate, (int, float)) and not isinstance(rate, bool)
                and math.isfinite(rate) and 0.60 <= rate <= 0.90):
            markets.add(market)
    return len(markets)


def _candidate_rows(day: str) -> list[dict]:
    rows = _read_same_day_rows(day)
    if not rows:
        return []
    # The adapter supports 1X2. Keep the capture order deterministic and do
    # not spend its bounded budget on markets it cannot return.
    candidates = [
        dict(row) for row in rows
        if isinstance(row, dict)
        and str(row.get("date") or "")[:10] == str(day)[:10]
        and str(row.get("market") or "") == "1x2"
        and str(row.get("home") or "").strip()
        and str(row.get("away") or "").strip()
    ]
    def score(row: dict, key: str) -> float:
        try:
            return float(row.get(key) or 0.0)
        except (TypeError, ValueError):
            return 0.0

    candidates.sort(
        key=lambda row: (
            -_enh_pricing_gap_count(row), -score(row, "avg_p"), -score(row, "w_score"),
            str(row.get("home") or ""), str(row.get("away") or ""),
        )
    )
    # One request per fixture, not one request per selection.
    unique: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for row in candidates:
        key = (str(row.get("home") or ""), str(row.get("away") or ""))
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


# Receipt stat whitelist: which of the adapter's run and request counters reach
# the capture receipt. The row-refusal census (`be_rows_rejected` and its
# reasons) belongs here beside the request counters: it is the evidence the
# 2026-10-12 row-join guard is audited from (round-2 §2.2), and in the
# delivered patch the whitelist dropped it, so the census never reached the
# receipt. Everything not listed stays in the run log only.
RECEIPT_STAT_KEYS = frozenset({
    "be_429", "be_cooling_down", "be_cached", "be_fetches",
    "requests", "market_requests", "market_budget_stop",
    "be_rows_rejected", "be_rows_rejected_reasons",
})


def _receipt_path(day: str) -> Path:
    return LOCALDATA / f"betexplorer_capture_{str(day)[:10]}.json"


def _write_receipt(day: str, payload: dict) -> None:
    LOCALDATA.mkdir(parents=True, exist_ok=True)
    path = _receipt_path(day)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)


def _fixture_receipt(pick: dict) -> dict:
    return {
        "date": str(pick.get("date") or "")[:10],
        "home": pick.get("home") or "",
        "away": pick.get("away") or "",
        "league": pick.get("league") or "",
        "market": pick.get("market") or "",
        "pick": pick.get("pick") or "",
        "avg_p": pick.get("avg_p"),
        "w_score": pick.get("w_score"),
    }


def _detail_summary(day: str) -> dict:
    """Counts for the same-day retained-detail ledger the adapter writes.

    Read-only: this wrapper never writes the ledger, and a missing or
    unreadable file reports zeros rather than failing a capture run. Counts
    per market: retained markets, retained rows, named rows and the distinct
    bookmakers each market names.
    """
    empty = {"fixtures": 0, "markets": 0, "market_rows": 0, "named_rows": 0,
             "bookmakers": 0, "standings_rows": 0, "with_h2h": 0,
             "with_last_results": 0, "with_standings": 0, "challenge_pages": 0}
    path = LOCALDATA / f"betexplorer_match_detail_{str(day)[:10]}.json"
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError, TypeError):
        return empty
    fixtures = payload.get("fixtures") if isinstance(payload, dict) else None
    if not isinstance(fixtures, dict):
        return empty
    summary = dict(empty)
    for entry in fixtures.values():
        if not isinstance(entry, dict):
            continue
        summary["fixtures"] += 1
        markets = entry.get("markets") if isinstance(entry.get("markets"), dict) else {}
        for market in markets.values():
            if not isinstance(market, dict):
                continue
            summary["markets"] += 1
            rows = market.get("rows") if isinstance(market.get("rows"), list) else []
            summary["market_rows"] += len(rows)
            summary["named_rows"] += int(market.get("named_rows") or 0)
            summary["bookmakers"] += len(market.get("bookmakers") or [])
        page = entry.get("page") or {}
        blocks = set(page.get("blocks") or [])
        summary["standings_rows"] += len(page.get("standings_rows") or [])
        summary["with_h2h"] += 1 if "h2h" in blocks else 0
        summary["with_last_results"] += 1 if "last_results" in blocks else 0
        summary["with_standings"] += 1 if "standings" in blocks else 0
        summary["challenge_pages"] += 1 if page.get("challenge") else 0
    return summary


def capture(day: str, *, max_fixtures: int = DEFAULT_MAX_FIXTURES) -> dict:
    """Capture up to max_fixtures network candidates plus free cache reads."""
    limit = max(0, min(MAX_FIXTURES_CEILING, int(max_fixtures)))
    receipt = {
        "schema": 1,
        "date": str(day)[:10],
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "candidate_fixtures": 0,
        "attempted": 0,
        "network_attempted": 0,
        "cache_only": 0,
        "deferred_fixtures": 0,
        "fixtures_with_rows": 0,
        "rows": 0,
        "max_fixtures": limit,
        "status": "empty",
        "errors": [],
        "attempted_fixtures": [],
        "quoted_fixtures": [],
    }
    try:
        from edgefactory.sources import betexplorer_odds as source
        from edgefactory.util import norm_team

        candidates = _candidate_rows(day)
        receipt["candidate_fixtures"] = len(candidates)
        source.reset_fetch_count()
        source._MAX_FETCHES_PER_RUN = limit
        for pick in candidates:
            # Negative cache entries remain answers: never retry them just to
            # fill a card. Free reads must not consume fresh fixture slots.
            needs_capture = source.fixture_capture_needed(pick, day)
            if needs_capture and receipt["network_attempted"] >= limit:
                receipt["deferred_fixtures"] += 1
                continue
            receipt["attempted"] += 1
            receipt["attempted_fixtures"].append(_fixture_receipt(pick))
            try:
                if needs_capture:
                    receipt["network_attempted"] += 1
                    rows = source.betexplorer_odds_rows_for_pick(
                        pick, day, norm_team_fn=norm_team,
                    )
                else:
                    receipt["cache_only"] += 1
                    rows = source.cached_odds_rows_for_pick(pick, day)
            except Exception as exc:  # noqa: BLE001 — source is fail-soft
                receipt["errors"].append(type(exc).__name__)
                continue
            if rows:
                receipt["fixtures_with_rows"] += 1
                receipt["rows"] += len(rows)
                receipt["quoted_fixtures"].append(_fixture_receipt(pick))
        receipt.update({
            key: value
            for stats in (source.run_stats(), source.request_stats())
            for key, value in stats.items()
            if key in RECEIPT_STAT_KEYS
        })
        receipt["match_detail"] = _detail_summary(day)
        receipt["status"] = "ok" if receipt["rows"] else "empty"
    except Exception as exc:  # noqa: BLE001 — a missing adapter must not break daily
        receipt["status"] = "unavailable"
        receipt["errors"].append(type(exc).__name__)
    _write_receipt(day, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    parser.add_argument("--max-fixtures", type=int, default=DEFAULT_MAX_FIXTURES,
                        help="maximum network fixture attempts; cache-only reads are free")
    args = parser.parse_args()
    receipt = capture(args.date, max_fixtures=args.max_fixtures)
    detail = receipt.get("match_detail") or {}
    print(
        "betexplorer snapshot "
        f"{receipt['date']}: candidates={receipt['candidate_fixtures']} "
        f"attempted={receipt['attempted']} network_attempted={receipt['network_attempted']} "
        f"cache_only={receipt['cache_only']} deferred={receipt['deferred_fixtures']} "
        f"fixtures={receipt['fixtures_with_rows']} "
        f"rows={receipt['rows']} detail={detail.get('fixtures', 0)}fixtures/"
        f"{detail.get('markets', 0)}markets/{detail.get('market_rows', 0)}rows "
        f"status={receipt['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
