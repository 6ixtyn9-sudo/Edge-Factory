"""Small helpers for verified candidate shadow captures.

These helpers keep shadow ledgers and price boards out of the consensus source
registry. They are intentionally boring: missing/blocked captures remain
visible and never become synthetic rows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_shadow_rows(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError, TypeError):
        return [], {}
    rows = payload.get("rows") if isinstance(payload, dict) else []
    stats = payload.get("stats") if isinstance(payload, dict) else {}
    return (
        [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else [],
        stats if isinstance(stats, dict) else {},
    )


def append_price_board_rows(
    pick: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    source: str,
    team_key,
) -> int:
    """Append exact-fixture named-price rows without changing chosen odds."""
    pick_date = str(pick.get("date") or "")
    home_key = team_key(str(pick.get("home") or ""))
    away_key = team_key(str(pick.get("away") or ""))
    board = list(pick.get("price_board") or [])
    seen = {
        (str(entry.get("source") or ""), str(entry.get("bookmaker") or ""),
         str(entry.get("market") or ""), str(entry.get("selection") or ""),
         entry.get("odds"), str(entry.get("captured_at") or ""))
        for entry in board
    }
    added = 0
    for row in rows:
        if str(row.get("date") or "") != pick_date:
            continue
        if (team_key(str(row.get("home") or "")), team_key(str(row.get("away") or ""))) != (home_key, away_key):
            continue
        try:
            odds = float(row.get("odds"))
        except (TypeError, ValueError):
            continue
        if odds <= 1.0 or not row.get("bookmaker"):
            continue
        entry = {
            "source": source,
            "book": row.get("book") or row.get("bookmaker"),
            "bookmaker": row.get("book") or row.get("bookmaker"),
            "odds": odds,
            "captured_at": row.get("captured_at"),
            "league": row.get("league"),
            "kickoff": row.get("kickoff"),
            "market": row.get("market"),
            "selection": row.get("selection"),
            "home": row.get("home"),
            "away": row.get("away"),
        }
        key = (source, str(entry.get("bookmaker") or ""), str(entry.get("market") or ""),
               str(entry.get("selection") or ""), entry["odds"], str(entry.get("captured_at") or ""))
        if key in seen:
            continue
        seen.add(key)
        board.append(entry)
        added += 1
    board.sort(key=lambda entry: (
        str(entry.get("source") or ""),
        str(entry.get("market") or ""),
        str(entry.get("selection") or ""),
        -(float(entry.get("odds") or 0.0)),
    ))
    pick["price_board"] = board
    return added
