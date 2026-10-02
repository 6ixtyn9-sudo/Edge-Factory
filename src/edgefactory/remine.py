"""Safety primitives for gap-aware historical re-mining.

This module contains no network client and no production-weight mutation. It is
used by the B0 inventory and by future source-specific crawl drivers.

The two duplicate fences are intentionally separate:

* coverage/row fence: only dates in the inventory's explicit gap list may be
  handed to a fetch function; held dates are never requested;
* signal fence: settled rows from a new source are compared with an existing
  donor before the new source can be shadow-scored. A convergent source is
  descriptive only and receives no new voice credit.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Callable, Iterable

from .identity import source_team_key


def _text(value: object) -> str:
    return str(value or "").strip().lower()


def _market(row: dict, market: str | None = None) -> str:
    if market is not None:
        return str(market)
    return str(row.get("market") or row.get("market_name") or "row")


def source_row_key(source: str, row: dict, market: str | None = None) -> str:
    """Return the immutable source/date/fixture/market collision key.

    ``source_team_key`` is the existing alias-aware identity seam. Event or
    match IDs are only fallbacks for rows that do not carry both team names.
    """
    day = _text(row.get("date") or row.get("match_date"))[:10]
    home = row.get("home") or row.get("home_team")
    away = row.get("away") or row.get("away_team")
    if home and away:
        fixture = f"{source_team_key(home)}::{source_team_key(away)}"
    elif row.get("event_id"):
        fixture = f"event:{_text(row['event_id'])}"
    elif row.get("match_id"):
        fixture = f"match:{_text(row['match_id'])}"
    else:
        fixture = "fixture:unknown"
    return f"{source}|{day}|{fixture}|{_market(row, market)}"


def _source_inventory(inventory: dict, source: str) -> dict:
    sources = inventory.get("sources", {})
    if source not in sources:
        raise KeyError(f"source not present in coverage inventory: {source}")
    return sources[source]


def held_days(inventory: dict, source: str) -> set[str]:
    """Return days already held for a source, regardless of committed/cache state."""
    return set(_source_inventory(inventory, source).get("per_day_row_counts", {}))


def gap_days(
    inventory: dict,
    source: str,
    requested_dates: Iterable[str] | None = None,
) -> list[str]:
    """Return only explicit inventory gaps, never a date-range expansion.

    A stale or hand-edited inventory that marks a held day as a gap fails
    closed rather than issuing a request.
    """
    data = _source_inventory(inventory, source)
    gaps = set(data.get("date_range", {}).get("missing_internal_days", []))
    held = held_days(inventory, source)
    overlap = gaps & held
    if overlap:
        raise ValueError(f"inventory invariant violated: held dates marked as gaps: {sorted(overlap)}")
    if requested_dates is not None:
        requested = {str(day)[:10] for day in requested_dates}
        gaps &= requested
    return sorted(gaps)


def fetch_gap_only(
    inventory: dict,
    source: str,
    requested_dates: Iterable[str] | None,
    fetch_day: Callable[[str], list[dict]],
    *,
    audit: list[dict] | None = None,
) -> dict[str, list[dict]]:
    """Call ``fetch_day`` only for explicit, unheld gap days.

    The callback is injected so tests can prove that no fetch is issued for a
    held day without opening a network transport. A real driver must pass its
    robots/challenge-aware fetch function here.
    """
    selected = gap_days(inventory, source, requested_dates)
    held = held_days(inventory, source)
    result: dict[str, list[dict]] = {}
    for day in selected:
        if day in held:  # defensive second fence; this branch is unreachable
            raise AssertionError(f"attempted fetch for held day: {source} {day}")
        if audit is not None:
            audit.append({"source": source, "date": day, "action": "fetch_gap"})
        result[day] = fetch_day(day)
    return result


def merge_existing_wins(
    source: str,
    existing_rows: Iterable[dict],
    incoming_rows: Iterable[dict],
    *,
    key_fn: Callable[[str, dict], str] = source_row_key,
) -> tuple[list[dict], dict]:
    """Merge incoming rows without replacing an existing committed row.

    The first existing row for a key is retained. Incoming collisions and
    duplicate incoming keys are skipped and counted. The function does not
    mutate either input row or list.
    """
    merged: list[dict] = []
    seen: set[str] = set()
    existing_keys: set[str] = set()
    incoming_keys: set[str] = set()
    audit = {
        "source": source,
        "existing_rows": 0,
        "incoming_rows": 0,
        "incoming_collision_rows_skipped": 0,
        "incoming_duplicate_rows_skipped": 0,
        "collision_keys": [],
    }
    for row in existing_rows:
        audit["existing_rows"] += 1
        key = key_fn(source, row)
        if key in seen:
            # Existing ledger duplicates are preserved for audit; this merge
            # never silently rewrites committed history.
            merged.append(dict(row))
            continue
        seen.add(key)
        existing_keys.add(key)
        merged.append(dict(row))
    for row in incoming_rows:
        audit["incoming_rows"] += 1
        key = key_fn(source, row)
        if key in existing_keys:
            audit["incoming_collision_rows_skipped"] += 1
            if key not in {item["key"] for item in audit["collision_keys"]}:
                audit["collision_keys"].append({"key": key, "action": "existing_wins"})
            continue
        if key in incoming_keys:
            audit["incoming_duplicate_rows_skipped"] += 1
            continue
        incoming_keys.add(key)
        seen.add(key)
        merged.append(dict(row))
    return merged, audit


def _pick(value: object) -> str | None:
    token = _text(value)
    return {
        "1": "home", "h": "home", "home": "home", "homewin": "home",
        "x": "draw", "d": "draw", "draw": "draw",
        "2": "away", "a": "away", "away": "away", "awaywin": "away",
    }.get(token)


def _hit(row: dict) -> bool | None:
    if row.get("hit") is not None:
        raw = row.get("hit")
        if isinstance(raw, bool):
            return raw
        if _text(raw) in {"1", "true", "yes", "win", "won"}:
            return True
        if _text(raw) in {"0", "false", "no", "loss", "lost"}:
            return False
    pick, outcome = _pick(row.get("pick")), _pick(row.get("outcome"))
    if pick is None or outcome is None:
        return None
    return pick == outcome


def _overlap_key(row: dict, source: str) -> str:
    # Unlike the immutable ledger key, an overlap key must be shared across
    # sources; the source labels remain in the report metadata.
    return source_row_key("overlap", row, market=str(row.get("market") or "1x2"))


def overlap_report(
    new_source: str,
    new_rows: Iterable[dict],
    donor_source: str,
    donor_rows: Iterable[dict],
    *,
    min_shared: int = 30,
    convergent_same_pick_rate: float = 0.90,
) -> dict:
    """Compare settled signals and return a joint-hit/phi convergence report."""
    new_by_key = {_overlap_key(row, new_source): row for row in new_rows if _hit(row) is not None}
    donor_by_key = {_overlap_key(row, donor_source): row for row in donor_rows if _hit(row) is not None}
    shared = sorted(set(new_by_key) & set(donor_by_key))
    counts: Counter[str] = Counter()
    same_pick = 0
    comparable_picks = 0
    for key in shared:
        nh, dh = _hit(new_by_key[key]), _hit(donor_by_key[key])
        counts[f"new_{'hit' if nh else 'miss'}__donor_{'hit' if dh else 'miss'}"] += 1
        npick, dpick = _pick(new_by_key[key].get("pick")), _pick(donor_by_key[key].get("pick"))
        if npick is not None and dpick is not None:
            comparable_picks += 1
            same_pick += npick == dpick
    a = counts["new_hit__donor_hit"]
    b = counts["new_hit__donor_miss"]
    c = counts["new_miss__donor_hit"]
    d = counts["new_miss__donor_miss"]
    denominator = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    phi = ((a * d - b * c) / denominator) if denominator else None
    same_pick_rate = same_pick / comparable_picks if comparable_picks else None
    eligible = len(shared) >= min_shared
    convergent = bool(
        eligible
        and same_pick_rate is not None
        and same_pick_rate >= convergent_same_pick_rate
    )
    return {
        "new_source": new_source,
        "donor_source": donor_source,
        "min_shared": min_shared,
        "shared_settled_fixtures": len(shared),
        "eligible": eligible,
        "joint_hit_table": {
            "new_hit__donor_hit": a,
            "new_hit__donor_miss": b,
            "new_miss__donor_hit": c,
            "new_miss__donor_miss": d,
        },
        "phi": phi,
        "same_pick_rate": same_pick_rate,
        "convergent": convergent,
        "voice_credit": 0 if convergent else "pending",
    }
