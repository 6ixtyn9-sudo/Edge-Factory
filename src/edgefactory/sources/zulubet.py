"""Zulubet adapter — plain HTML, 1x2 probs + average odds + FT score.

URL: https://www.zulubet.com/tips-DD-MM-YYYY.html
History: 410 Gone before ~2023-12-25.
"""
from __future__ import annotations

import re
import time
import urllib.error
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
MIN_DATE = "2023-12-25"

_ROWSPLIT = re.compile(r'<tr style="background-color:#(?:EFEFEF|FFFFFF)">')
_LEAGUE = re.compile(r'title="([^"]*)"')
_TEAMS = re.compile(r'height="11"\s*/?>\s*([^<]+?)\s*-\s*([^<]+?)</td>')
_PROBS = re.compile(r'class="prob prediction_full"[^>]*>(\d+)%</td>')
_TIP = re.compile(r"<span style=\"color:green\"><b>([^<]+)</b></span>")
_ODDS = re.compile(r'class="aver_odds_full">([\d.]+)</td>')
_SCORE = re.compile(r'<td style="text-align: center;">(\d+):(\d+)</td>')
_TIME = re.compile(r"<noscript>([\d-]+, [\d:]+)</noscript>")


def fetch_day(date: str, retries: int = 3) -> list[dict]:
    """date is ISO YYYY-MM-DD; zulubet wants DD-MM-YYYY."""
    if date < MIN_DATE:
        return []
    y, m, d = date.split("-")
    url = f"https://www.zulubet.com/tips-{d}-{m}-{y}.html"
    html = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return []
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    if not html:
        return []
    out = []
    for chunk in _ROWSPLIT.split(html)[1:]:
        teams = _TEAMS.search(chunk)
        probs = _PROBS.findall(chunk)
        if not teams or len(probs) < 3:
            continue
        league = _LEAGUE.search(chunk)
        tip = _TIP.search(chunk)
        odds = _ODDS.findall(chunk)
        score = _SCORE.search(chunk)
        t = _TIME.search(chunk)
        out.append(
            {
                "date": date,
                "kickoff": t.group(1) if t else None,
                "league": league.group(1) if league else None,
                "home": teams.group(1).strip(),
                "away": teams.group(2).strip(),
                "p1": float(probs[0]), "px": float(probs[1]), "p2": float(probs[2]),
                "tip": tip.group(1) if tip else None,
                "odd1": float(odds[0]) if len(odds) > 0 else None,
                "oddx": float(odds[1]) if len(odds) > 1 else None,
                "odd2": float(odds[2]) if len(odds) > 2 else None,
                "hs": int(score.group(1)) if score else None,
                "gs": int(score.group(2)) if score else None,
            }
        )
    return out


COLUMNS = [
    "date", "kickoff", "league", "home", "away",
    "p1", "px", "p2", "tip", "odd1", "oddx", "odd2", "hs", "gs",
]
