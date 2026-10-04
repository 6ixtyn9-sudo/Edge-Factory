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
            -score(row, "avg_p"), -score(row, "w_score"),
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


def capture(day: str, *, max_fixtures: int = DEFAULT_MAX_FIXTURES) -> dict:
    """Populate bounded fixture caches and return a secret-free receipt."""
    limit = max(0, min(MAX_FIXTURES_CEILING, int(max_fixtures)))
    receipt = {
        "schema": 1,
        "date": str(day)[:10],
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "candidate_fixtures": 0,
        "attempted": 0,
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
        for pick in candidates[:limit]:
            receipt["attempted"] += 1
            receipt["attempted_fixtures"].append(_fixture_receipt(pick))
            try:
                rows = source.betexplorer_odds_rows_for_pick(
                    pick, day, norm_team_fn=norm_team,
                )
            except Exception as exc:  # noqa: BLE001 — source is fail-soft
                receipt["errors"].append(type(exc).__name__)
                continue
            if rows:
                receipt["fixtures_with_rows"] += 1
                receipt["rows"] += len(rows)
                receipt["quoted_fixtures"].append(_fixture_receipt(pick))
        receipt.update({
            key: value for key, value in source.run_stats().items()
            if key in {"be_429", "be_cooling_down", "be_cached", "be_fetches"}
        })
        receipt["status"] = "ok" if receipt["rows"] else "empty"
    except Exception as exc:  # noqa: BLE001 — a missing adapter must not break daily
        receipt["status"] = "unavailable"
        receipt["errors"].append(type(exc).__name__)
    _write_receipt(day, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    parser.add_argument("--max-fixtures", type=int, default=DEFAULT_MAX_FIXTURES)
    args = parser.parse_args()
    receipt = capture(args.date, max_fixtures=args.max_fixtures)
    print(
        "betexplorer snapshot "
        f"{receipt['date']}: candidates={receipt['candidate_fixtures']} "
        f"attempted={receipt['attempted']} fixtures={receipt['fixtures_with_rows']} "
        f"rows={receipt['rows']} status={receipt['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
