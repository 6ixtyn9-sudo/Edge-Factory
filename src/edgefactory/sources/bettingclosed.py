"""BettingClosed adapter — ★ DEEP ARCHIVE TO 2012, self-settling ★

URL: https://www.bettingclosed.com/predictions/date-matches/YYYY-MM-DD[/bet-type/M]
Markets: 1x2 (incl. double chance picks), under-over (2.5), gol-nogol (btts),
correct-scores. Each row: teams, FT result, pick, book odd of the pick, and a
tooltip with full 1X2+OU odds. Result is ON the page -> no settlement join
needed. ~180 rows/day (2012) to ~600/day (2024+). curl_cffi safari17_0.
"""
from __future__ import annotations

import re

from .cffi_http import get

MIN_DATE = "2012-01-01"
MARKETS = ("1x2", "under-over", "gol-nogol")

_ROW = re.compile(r'(?=<tr class="rowincontri)')
_TEAMS = re.compile(r'<a href="/prediction/\d+/[^"]*">(?:<span[^>]*>[^<]*</span>)?\s*'
                    r"([^<]+?)\s*-\s*([^<]+?)\s*<span")
_RESULT = re.compile(r'class="resultMt">([^<]*)<')
_PRED = re.compile(r'class="predMt"><a[^>]*>([^<]+)</a>')
_PRED_FREE = re.compile(r'class="predMt">([^<]+)<')
_ODD = re.compile(r'class="oddPredBook">([^<]*)<')
_ODDS_TIP = re.compile(r'title="Odds: 1\(([^)]*)\),X\(([^)]*)\),2\(([^)]*)\),'
                       r"Under\(([^)]*)\),Over\(([^)]*)\)")
_LEAGUE = re.compile(r'class="myLG"[^>]*>(?:<[^>]+>)*([^<]*)<')


def _f(s):
    try:
        return float(s) if s and s.strip() else None
    except ValueError:
        return None


def _parse_score(s: str):
    m = re.match(r"(\d+)-(\d+)", (s or "").strip())
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def fetch_day(date: str) -> list[dict]:
    if date < MIN_DATE:
        return []
    merged: dict[tuple, dict] = {}
    for market in MARKETS:
        url = (f"https://www.bettingclosed.com/predictions/date-matches/{date}"
               f"/bet-type/{market}")
        html = get(url)
        if not html:
            continue
        for chunk in _ROW.split(html)[1:]:
            t = _TEAMS.search(chunk)
            if not t:
                continue
            home, away = t.group(1).strip(), t.group(2).strip()
            key = (home, away)
            res = _RESULT.search(chunk)
            hs, gs = _parse_score(res.group(1) if res else "")
            pred = _PRED.search(chunk) or _PRED_FREE.search(chunk)
            odd = _ODD.search(chunk)
            tip = _ODDS_TIP.search(chunk)
            row = merged.setdefault(key, {
                "date": date, "home": home, "away": away,
                "hs": hs, "gs": gs,
            })
            if row["hs"] is None and hs is not None:
                row["hs"], row["gs"] = hs, gs
            if tip and "odd1" not in row:
                row.update(odd1=_f(tip.group(1)), oddx=_f(tip.group(2)),
                           odd2=_f(tip.group(3)), odd_under=_f(tip.group(4)),
                           odd_over=_f(tip.group(5)))
            p = pred.group(1).strip().lower() if pred else None
            if market == "1x2":
                row["pick_1x2"] = p
                row["odd_pick_1x2"] = _f(odd.group(1)) if odd else None
            elif market == "under-over":
                row["pick_ou"] = p
                row["odd_pick_ou"] = _f(odd.group(1)) if odd else None
            elif market == "gol-nogol":
                row["pick_btts"] = p
                row["odd_pick_btts"] = _f(odd.group(1)) if odd else None
    return list(merged.values())


COLUMNS = ["date", "home", "away", "hs", "gs",
           "odd1", "oddx", "odd2", "odd_under", "odd_over",
           "pick_1x2", "odd_pick_1x2", "pick_ou", "odd_pick_ou",
           "pick_btts", "odd_pick_btts"]
