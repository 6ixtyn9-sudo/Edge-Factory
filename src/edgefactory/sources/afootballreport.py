"""aFootballReport adapter — streak-based tips (OU 1.5/2.5, BTTS).

Pages: /predictions/over-1.5-goals, /predictions/over-2.5-goals,
       /predictions/both-teams-to-score   (today's tips; capture-forward)
Rows are schema.org SportsEvent <tr> blocks with a [tip] and [logic-tip]
("X have over 1.5 goals in 100% of their games in the last 2 months (total games 6)").
Pseudo-prob convention (Session #1): 0.5 + streak_games * 0.02, raw fields kept.
"""
from __future__ import annotations

import re
import time
import urllib.request
from datetime import date as _date

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PAGES = {
    "ou_1.5": "https://afootballreport.com/predictions/over-1.5-goals",
    "ou_2.5": "https://afootballreport.com/predictions/over-2.5-goals",
    "btts": "https://afootballreport.com/predictions/both-teams-to-score",
}

_ROW = re.compile(r"<tr itemscope[^>]*>(.*?)</tr>", re.S)
_HOME = re.compile(r'itemprop="homeTeam"[^>]*>\s*<meta itemprop="name" content="([^"]+)"')
_AWAY = re.compile(r'itemprop="awayTeam"[^>]*>\s*<meta itemprop="name" content="([^"]+)"')
_START = re.compile(r'itemprop="startDate" content="([^"]+)"')
_LEAGUE = re.compile(r'itemprop="address" content="([^"]+)"')
_TIP = re.compile(r'class="tip"[^>]*>(.*?)</td>', re.S)
_LOGIC = re.compile(r'class="logic-tip"[^>]*>(.*?)</td>', re.S)
_PCT = re.compile(r"(\d+)% of their games")
_TOTAL = re.compile(r"total games (\d+)")


def _txt(s: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", s).split())


def fetch_day(date: str, retries: int = 3) -> list[dict]:
    """Today-only source: returns [] for any other date."""
    if date != _date.today().isoformat():
        return []
    out = []
    for market, url in PAGES.items():
        html = None
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=30) as r:
                    html = r.read().decode("utf-8", "replace")
                break
            except Exception:
                if attempt == retries - 1:
                    raise
                time.sleep(1.5 * (attempt + 1))
        if not html:
            continue
        for row in _ROW.findall(html):
            home, away = _HOME.search(row), _AWAY.search(row)
            tip = _TIP.search(row)
            if not (home and away and tip):
                continue
            logic = _LOGIC.search(row)
            logic_text = _txt(logic.group(1)) if logic else ""
            pct = _PCT.search(logic_text)
            tot = _TOTAL.search(logic_text)
            streak = int(tot.group(1)) if tot else None
            pseudo = round(0.5 + streak * 0.02, 3) if streak else None
            start = _START.search(row)
            league = _LEAGUE.search(row)
            out.append(
                {
                    "date": date,
                    "kickoff": start.group(1) if start else None,
                    "league": league.group(1) if league else None,
                    "home": home.group(1).strip(),
                    "away": away.group(1).strip(),
                    "market": market,
                    "tip": _txt(tip.group(1)),
                    "streak_pct": int(pct.group(1)) if pct else None,
                    "streak_n": streak,
                    "pseudo_prob": pseudo,
                }
            )
    return out


COLUMNS = ["date", "kickoff", "league", "home", "away", "market", "tip",
           "streak_pct", "streak_n", "pseudo_prob"]
