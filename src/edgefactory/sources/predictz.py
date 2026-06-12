"""PredictZ adapter — Cloudflare-protected, cracked via curl_cffi safari17_0.

URL: https://www.predictz.com/predictions/YYYYMMDD/   (archive reaches ~2026-01-01)
Per match: predicted outcome + scoreline ("Home 2-1"), 1X2 odds, league.
No probabilities — prediction is categorical. Settle by joining scores from
forebet/statarea/zulubet on (date, norm(home), norm(away)).
"""
from __future__ import annotations

import re

from .cffi_http import get

MIN_DATE = "2026-01-01"  # archive serves nothing before ~this

_BLOCK = re.compile(r'(?=<div class="pttr ptcnt">)')
_LEAGUE = re.compile(r'<div class="pttd ptlg">.*?<h2><a[^>]*>([^<]+)</a></h2>', re.S)
_GAME = re.compile(r'class="pttd ptgame"><a[^>]*>([^<]+?) v ([^<]+?)</a>')
_PRED = re.compile(r'ptpredboxsml">([^<]+)<')
_ODDS = re.compile(r'class="pttd ptodds"><a[^>]*>([\d.]+)</a>')


def _parse_pred(text: str) -> tuple[str | None, str | None]:
    """'Home 2-1' -> ('home', '2-1'); 'Draw 1-1' -> ('draw', '1-1')."""
    m = re.match(r"(Home|Draw|Away)\s*([\d-]*)", text.strip())
    if not m:
        return None, None
    return m.group(1).lower(), m.group(2) or None


def fetch_day(date: str) -> list[dict]:
    if date < MIN_DATE:
        return []
    ymd = date.replace("-", "")
    html = get(f"https://www.predictz.com/predictions/{ymd}/")
    if not html:
        return []
    out = []
    league = None
    # league headers appear in the chunk BEFORE each table's rows
    for chunk in _BLOCK.split(html):
        lm = _LEAGUE.findall(chunk)
        game = _GAME.search(chunk)
        if game:
            pred_m = _PRED.search(chunk)
            odds = _ODDS.findall(chunk)
            sel, score = _parse_pred(pred_m.group(1)) if pred_m else (None, None)
            out.append(
                {
                    "date": date,
                    "league": league,
                    "home": game.group(1).strip(),
                    "away": game.group(2).strip(),
                    "pick": sel,
                    "pred_score": score,
                    "odd1": float(odds[0]) if len(odds) > 0 else None,
                    "oddx": float(odds[1]) if len(odds) > 1 else None,
                    "odd2": float(odds[2]) if len(odds) > 2 else None,
                }
            )
        if lm:
            league = lm[-1].strip().removesuffix(" Tips")
    return out


COLUMNS = ["date", "league", "home", "away", "pick", "pred_score",
           "odd1", "oddx", "odd2"]
