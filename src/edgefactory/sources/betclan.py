"""BetClan adapter — listing page + per-match detail pages with probabilities.

List: https://www.betclan.com/todays-football-predictions/ (also tomorrow's URL)
Detail pages carry Winner pick + vote/probability bars (home/draw/away %).
Capture-forward. We fetch the listing then a capped number of detail pages.
"""
from __future__ import annotations

import re
import time
from datetime import date as _date, timedelta

from .cffi_http import get

_LIST_LINK = re.compile(
    r"href='(https://www\.betclan\.com/predictionsdetails/football/[^']+)'")
_LIST_ROW = re.compile(
    r"<div class='bchome right'>([^<]+)</div>\s*<div class='bcversus[^']*'>vs</div>"
    r"\s*<div class='bcaway left'>([^<]+)</div>")
_WINNER = re.compile(r"<h4[^>]*>Winner</h4><h5[^>]*>([^<]+)</h5>")
_BAR = re.compile(r"width:\s*(\d+)%;min-width")
_LEAGUE_T = re.compile(r"title='([^']+) Predictions'")

MAX_DETAILS = 60  # politeness cap per day


def fetch_day(date: str, detail_limit: int = MAX_DETAILS) -> list[dict]:
    today = _date.today().isoformat()
    tomorrow = (_date.today() + timedelta(days=1)).isoformat()
    if date == today:
        url = "https://www.betclan.com/todays-football-predictions/"
    elif date == tomorrow:
        url = "https://www.betclan.com/tomorrow-football-predictions/"
    else:
        return []
    html = get(url)
    if not html:
        return []
    links = _LIST_LINK.findall(html)
    seen, out = set(), []
    for link in links:
        if link in seen or len(out) >= detail_limit:
            continue
        seen.add(link)
        try:
            d = get(link)
        except Exception:
            continue
        if not d:
            continue
        # teams from URL slug: .../ceara-v-avai-prediction-...
        m = re.search(r"/(\d+)/([a-z0-9-]+)-v-([a-z0-9-]+)-prediction", link)
        winner = _WINNER.search(d)
        bars = _BAR.findall(d)
        # first three bars on the page are the 1x2 vote/prob bars
        p1 = float(bars[0]) if len(bars) >= 1 else None
        p2 = float(bars[2]) if len(bars) >= 3 else None
        px = float(bars[1]) if len(bars) >= 2 else None
        out.append(
            {
                "date": date,
                "match_id": m.group(1) if m else None,
                "home": (m.group(2).replace("-", " ").title() if m else None),
                "away": (m.group(3).replace("-", " ").title() if m else None),
                "winner": winner.group(1).strip() if winner else None,
                "p1": p1, "px": px, "p2": p2,
                "url": link,
            }
        )
        time.sleep(0.3)
    return out


COLUMNS = ["date", "match_id", "home", "away", "winner", "p1", "px", "p2", "url"]
