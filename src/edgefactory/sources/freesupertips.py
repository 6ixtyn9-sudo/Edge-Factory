"""FreeSuperTips adapter — Next.js site, predictions embedded in __NEXT_DATA__.

URL: https://www.freesupertips.com/predictions/
Per match: expert tips with title ('Win To Nil', 'Both Teams To Score'...),
odds (decimal), confidence (1-3), stake suggestion, reasoning text.
Capture-forward only (today/upcoming).
"""
from __future__ import annotations

import json
import re
import time
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
URL = "https://www.freesupertips.com/predictions/"

_NEXT = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def fetch_day(date: str, retries: int = 3) -> list[dict]:
    html = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", "replace")
            break
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    m = _NEXT.search(html or "")
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
        days = data["props"]["pageProps"]["responses"]["predictions"]
    except (KeyError, json.JSONDecodeError):
        return []
    out = []
    for day in days:
        for comp in day.get("competitions", []):
            for p in comp.get("predictions", []):
                start = (p.get("startString") or "")[:10]
                if start != date:
                    continue
                teams = p.get("teams", [])
                home = teams[0]["name"] if len(teams) > 0 else None
                away = teams[1]["name"] if len(teams) > 1 else None
                for tip in p.get("tips", []):
                    out.append(
                        {
                            "date": date,
                            "kickoff": p.get("startString"),
                            "league": comp.get("name"),
                            "home": home,
                            "away": away,
                            "tip": tip.get("title"),
                            "odds": tip.get("odds"),
                            "confidence": tip.get("confidence"),
                            "stake": tip.get("stake"),
                        }
                    )
    return out


COLUMNS = ["date", "kickoff", "league", "home", "away", "tip", "odds",
           "confidence", "stake"]
