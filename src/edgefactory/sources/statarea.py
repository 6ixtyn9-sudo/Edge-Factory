"""Statarea adapter — best solo model. Archive reaches 2015-2017!

URL: https://old.statarea.com/predictions/YYYY-MM-DD
Per match: 1x2 probs, HT 1x2 probs, OU 1.5/2.5/3.5 probs, FT+HT result
in a tooltip cell: '<span class="tool">2:4<span class="tip">Half time results: 0:0</span></span>'.
"""
from __future__ import annotations

import re
import time
import urllib.error
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

_HOST = re.compile(r'results_t\.php\?team_host=([^"]+?)\s*"\s*>([^<]+)</a>&nbsp;-')
_GUEST = re.compile(r'results_t\.php\?team_host=([^"]+?)\s*"\s*>([^<]+)</a></td>')
_PCT = re.compile(r"align=\"center\">(\d+)%</td>")
_RESULT = re.compile(
    r'class="tool">(\d+):(\d+)<span class="tip">Half time results: (\d+):(\d+)'
)
_RESULT_PLAIN = re.compile(r'width="40" align="center"[^>]*>\s*(\d+):(\d+)\s*<')
_LEAGUE = re.compile(r"&nbsp<b>([^<]+)</b>")
_TIME = re.compile(r'<td width="35" align="center">(\d{2}:\d{2})</td>')
_TIPS = re.compile(r"images/prd([12X])\.gif")


def fetch_day(date: str, retries: int = 3) -> list[dict]:
    url = f"https://old.statarea.com/predictions/{date}"
    html = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as r:
                html = r.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return []
            if attempt == retries - 1:
                raise
            time.sleep(2.0 * (attempt + 1))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2.0 * (attempt + 1))
    if not html:
        return []

    out = []
    league = None
    # split into per-match chunks on the kickoff-time cell
    chunks = re.split(r'(?=<td width="35" align="center">\d{2}:\d{2}</td>)', html)
    for chunk in chunks:
        lm = _LEAGUE.findall(chunk)
        host = _HOST.search(chunk)
        guest = _GUEST.search(chunk)
        if host is None or guest is None:
            if lm:
                league = lm[-1].strip()
            continue
        pcts = _PCT.findall(chunk)
        # expected order: 1, X, 2, H1, HX, H2, ou1.5, ou2.5, ou3.5, (hc1, hcX, hc2)
        if len(pcts) < 9:
            if lm:
                league = lm[-1].strip()
            continue
        res = _RESULT.search(chunk)
        if res:
            hs, gs, hths, htgs = (int(res.group(i)) for i in range(1, 5))
        else:
            rp = _RESULT_PLAIN.search(chunk)
            hs, gs = (int(rp.group(1)), int(rp.group(2))) if rp else (None, None)
            hths = htgs = None
        t = _TIME.search(chunk)
        tips = _TIPS.findall(chunk)
        p = [float(x) for x in pcts[:9]]
        out.append(
            {
                "date": date,
                "time": t.group(1) if t else None,
                "league": league,
                "home": host.group(2).strip(),
                "away": guest.group(2).strip(),
                "home_full": host.group(1).strip(),
                "away_full": guest.group(1).strip(),
                "tip": "".join(tips) or None,
                "p1": p[0], "px": p[1], "p2": p[2],
                "p1_ht": p[3], "px_ht": p[4], "p2_ht": p[5],
                "p_o15": p[6], "p_o25": p[7], "p_o35": p[8],
                "hs": hs, "gs": gs, "ht_hs": hths, "ht_gs": htgs,
            }
        )
        if lm:
            league = lm[-1].strip()
    return out


COLUMNS = [
    "date", "time", "league", "home", "away", "home_full", "away_full", "tip",
    "p1", "px", "p2", "p1_ht", "px_ht", "p2_ht", "p_o15", "p_o25", "p_o35",
    "hs", "gs", "ht_hs", "ht_gs",
]
