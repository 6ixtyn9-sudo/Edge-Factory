"""Forebet adapter — JSON endpoint, richest source (probs + best odds + FT/HT scores).

Endpoint: /scripts/getrs.php?ln=en&tp={1x2,uo,bts,ht}&in=DATE&ord=0&tz=0&tzs=&tze=
Needs UA + Referer + X-Requested-With. Serves nothing before 2024-01-01.
Response: [rows, meta]. The 1x2 payload already carries FT and HT scores,
so one merged wide row per match covers all markets.
"""
from __future__ import annotations

import json
import time
import urllib.request

BASE = "https://www.forebet.com/scripts/getrs.php"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://www.forebet.com/en/football-tips-and-predictions-for-today",
    "X-Requested-With": "XMLHttpRequest",
}
MIN_DATE = "2024-01-01"
DEFAULT_MARKETS = ("1x2", "uo", "bts")  # ht is certified charcoal; opt-in only


def _get(tp: str, date: str, retries: int = 3) -> list[dict]:
    url = f"{BASE}?ln=en&tp={tp}&in={date}&ord=0&tz=0&tzs=&tze="
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
            if isinstance(data, list) and data and isinstance(data[0], list):
                return data[0]
            return []
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    return []


def _f(v):
    try:
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def fetch_day(date: str, markets=DEFAULT_MARKETS, sleep: float = 0.15) -> list[dict]:
    """Fetch one calendar day, merge all market endpoints by match id."""
    if date < MIN_DATE:
        return []
    rows: dict[str, dict] = {}
    for tp in markets:
        try:
            payload = _get(tp, date)
        except Exception:
            payload = []
        for m in payload:
            mid = str(m.get("id"))
            row = rows.setdefault(
                mid,
                {
                    "date": date,
                    "kickoff": m.get("DATE_BAH"),
                    "league_id": m.get("league_id"),
                    "league": m.get("short_tag"),
                    "home": m.get("HOST_NAME"),
                    "away": m.get("GUEST_NAME"),
                    "hs": _i(m.get("Host_SC")),
                    "gs": _i(m.get("Guest_SC")),
                    "ht_hs": _i(m.get("Host_SC_HT")),
                    "ht_gs": _i(m.get("Guest_SC_HT")),
                    "status": m.get("comment"),
                },
            )
            if tp == "1x2":
                row.update(
                    p1=_f(m.get("Pred_1")), px=_f(m.get("Pred_X")), p2=_f(m.get("Pred_2")),
                    odd1=_f(m.get("best_odd_1")), oddx=_f(m.get("best_odd_X")),
                    odd2=_f(m.get("best_odd_2")), kelly=_f(m.get("kelly")),
                    pred_hs=_i(m.get("host_sc_pr")), pred_gs=_i(m.get("guest_sc_pr")),
                )
            elif tp == "uo":
                row.update(
                    p_under=_f(m.get("pr_under")), p_over=_f(m.get("pr_over")),
                    odd_under=_f(m.get("best_under")), odd_over=_f(m.get("best_over")),
                    goalsavg=_f(m.get("goalsavg")),
                )
            elif tp == "bts":
                row.update(
                    p_gg=_f(m.get("Pred_gg")), p_ng=_f(m.get("Pred_no_gg")),
                    odd_gg=_f(m.get("odds_gg_y")), odd_ng=_f(m.get("odds_gg_n")),
                )
            elif tp == "ht":
                row.update(
                    p1_ht=_f(m.get("Pred_1_HT")), px_ht=_f(m.get("Pred_X_HT")),
                    p2_ht=_f(m.get("Pred_2_HT")),
                )
        time.sleep(sleep)
    return list(rows.values())


COLUMNS = [
    "date", "kickoff", "league_id", "league", "home", "away",
    "hs", "gs", "ht_hs", "ht_gs", "status",
    "p1", "px", "p2", "odd1", "oddx", "odd2", "kelly", "pred_hs", "pred_gs",
    "p_under", "p_over", "odd_under", "odd_over", "goalsavg",
    "p_gg", "p_ng", "odd_gg", "odd_ng",
    "p1_ht", "px_ht", "p2_ht",
]
