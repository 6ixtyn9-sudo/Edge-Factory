from __future__ import annotations

from collections import defaultdict
import re
from statistics import mean
from typing import Any


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slug(value: object) -> str:
    text = str(value or "").strip().lower()
    text = _SLUG_RE.sub("-", text)
    return text.strip("-") or "na"


def build_pick_id(match_date, home, away, market, pick, rule_name) -> str:
    return "|".join(
        [
            str(match_date or "")[:10],
            _slug(home),
            _slug(away),
            _slug(market),
            _slug(pick),
            _slug(rule_name),
        ]
    )


def odds_to_implied_prob(odds: float | None) -> float | None:
    try:
        value = float(odds)
    except (TypeError, ValueError):
        return None
    if value <= 1.0:
        return None
    return 1.0 / value


def raw_odds_delta(first_odds: float | None, last_odds: float | None) -> float | None:
    try:
        first = float(first_odds)
        last = float(last_odds)
    except (TypeError, ValueError):
        return None
    if first <= 1.0 or last <= 1.0:
        return None
    return last - first


def implied_prob_delta(first_odds: float | None, last_odds: float | None) -> float | None:
    first_ip = odds_to_implied_prob(first_odds)
    last_ip = odds_to_implied_prob(last_odds)
    if first_ip is None or last_ip is None:
        return None
    return last_ip - first_ip


def beat_later_price(first_odds: float | None, last_odds: float | None) -> bool | None:
    try:
        first = float(first_odds)
        last = float(last_odds)
    except (TypeError, ValueError):
        return None
    if first <= 1.0 or last <= 1.0:
        return None
    return last < first


def check_clv_protection(
    initial_odds: float | None,
    current_odds: float | None,
    steam_max: float = 0.15,
    drift_max: float = 0.20,
) -> str | None:
    """Return 'STEAM_VETO' if odds dropped too much, 'DRIFT_VETO' if rose too much, or None."""
    try:
        first = float(initial_odds)
        last = float(current_odds)
    except (TypeError, ValueError):
        return None
    if first <= 1.0 or last <= 1.0:
        return None

    if last < first * (1.0 - steam_max):
        return "STEAM_VETO"
    if last > first * (1.0 + drift_max):
        return "DRIFT_VETO"
    return None


def summarize_clv(rows: list[dict]) -> dict:
    total = len(rows)
    with_two_prices = 0
    raw_deltas: list[float] = []
    ip_deltas: list[float] = []
    beats = 0
    beat_den = 0

    for row in rows:
        first_odds = row.get("first_odds")
        last_odds = row.get("last_odds")
        raw_delta = raw_odds_delta(first_odds, last_odds)
        ip_delta = implied_prob_delta(first_odds, last_odds)
        beat = beat_later_price(first_odds, last_odds)
        if raw_delta is not None:
            with_two_prices += 1
            raw_deltas.append(raw_delta)
        if ip_delta is not None:
            ip_deltas.append(ip_delta)
        if beat is not None:
            beat_den += 1
            if beat:
                beats += 1

    return {
        "total_picks": total,
        "with_two_prices": with_two_prices,
        "avg_raw_odds_delta": round(mean(raw_deltas), 6) if raw_deltas else None,
        "avg_implied_prob_delta": round(mean(ip_deltas), 6) if ip_deltas else None,
        "beat_later_price_rate": round(beats / beat_den, 6) if beat_den else None,
        "beat_later_price_n": beat_den,
    }


def summarize_by(rows: list[dict], key: str) -> dict[str, dict]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key) or "UNKNOWN")].append(row)
    return {name: summarize_clv(group_rows) for name, group_rows in sorted(grouped.items())}
