"""Vitibet adapter — 1x2 probs + INDEX + predicted score + FT result, DATE ARCHIVE!

URL: https://www.vitibet.com/index.php?clanek=quicktips&sekce=fotbal&lang=en&date=YYYY-MM-DD
Archive verified back to at least 2018 (42 rows on 2018-06-05; 800+ rows/day 2019-2021).
CAVEAT: on past dates only ~1 row keeps probs rendered; predictions are wiped
after settlement. So: probs are capture-forward; FT results ARE served for any
date -> useful as a settlement source too.
"""
from __future__ import annotations

import re
import time
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

_ROW = re.compile(r"(?=<a href='/index\.php\?clanek=match-detail)")
_TEAM = re.compile(r"livescore-team-name'>([^<]+)<")
_PROB = re.compile(r"prob-val[^>]*>([^<]+)<")
_FT = re.compile(r"act-score-line[^>]*>(\d+)<")
_PRED_SC = re.compile(r"livescore-score-line'[^>]*>\s*(\d+)\s*<")
_TIP = re.compile(r"tip-indicator-circle'[^>]*>([12X])<")
_TIME = re.compile(r"data-time='([^']+)'")
_LEAGUE = re.compile(r"league-title'>([^<]+)<")
_STATUS = re.compile(r"data-status='(\w+)'")


def fetch_day(date: str, retries: int = 3) -> list[dict]:
    url = ("https://www.vitibet.com/index.php?clanek=quicktips"
           f"&sekce=fotbal&lang=en&date={date}")
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
        return []

    out = []
    league = None
    for chunk in _ROW.split(html):
        lm = _LEAGUE.findall(chunk)
        teams = _TEAM.findall(chunk)
        if len(teams) >= 2 and "livescore-match-row" in chunk:
            probs = _PROB.findall(chunk)  # [INDEX, p1, px, p2] when present
            idx = p1 = px = p2 = None
            if len(probs) >= 4:
                try:
                    idx = float(probs[0].replace("+", ""))
                    p1 = float(probs[1].rstrip("%"))
                    px = float(probs[2].rstrip("%"))
                    p2 = float(probs[3].rstrip("%"))
                except ValueError:
                    pass
            ft = _FT.findall(chunk)
            psc = _PRED_SC.findall(chunk)
            tip = _TIP.search(chunk)
            t = _TIME.search(chunk)
            st = _STATUS.search(chunk)
            out.append(
                {
                    "date": date,
                    "kickoff": t.group(1) if t else None,
                    "league": league,
                    "home": teams[0].strip(),
                    "away": teams[1].strip(),
                    "p1": p1, "px": px, "p2": p2, "index": idx,
                    "tip": tip.group(1) if tip else None,
                    "pred_hs": int(psc[0]) if len(psc) >= 2 else None,
                    "pred_gs": int(psc[1]) if len(psc) >= 2 else None,
                    "hs": int(ft[0]) if len(ft) >= 2 else None,
                    "gs": int(ft[1]) if len(ft) >= 2 else None,
                    "status": st.group(1) if st else None,
                }
            )
        if lm:
            league = lm[-1].strip()
    return out


COLUMNS = ["date", "kickoff", "league", "home", "away", "p1", "px", "p2",
           "index", "tip", "pred_hs", "pred_gs", "hs", "gs", "status"]
