"""WinDrawWin adapter — Cloudflare-protected, cracked via curl_cffi safari17_0.

Pages: /predictions/ (today, all leagues), /predictions/tomorrow/,
/predictions/future/YYYYMMDD/ (next few days). NO usable archive — the date
URLs render a generic league-list page, so this source is capture-forward only.
Per match: predicted outcome ('Home Win'/'Draw'/'Away Win'), stake size
(Small/Medium/Large = confidence), predicted scoreline.
"""
from __future__ import annotations

import re
from datetime import date as _date

from edgefactory.sources import public_relay

from .cffi_http import get as cffi_get

_ROW = re.compile(r'(?=<div class="wttr">)')
_FIX = re.compile(r'class="wtdesklnk">([^<]+?)\s*</a>')
_FIX2 = re.compile(r'wtfixt[^>]*>\s*<a[^>]*>([^<]+?)\s*</a>')
_PRD = re.compile(r'class="wttd wtprd[^"]*">([^<]*)<')
_STK = re.compile(r'class="wttd wtstk[^"]*">([^<]*)<')
_SC = re.compile(r'class="wttd wtsc[^"]*">([^<]*)<')
_LEAGUE = re.compile(r'href="https://www\.windrawwin\.com/predictions/[a-z0-9-]+/"[^>]*>([^<]{3,60})</a>')

PRED_MAP = {"home win": "home", "draw": "draw", "away win": "away"}


def _validate_html(html: str | None) -> str | None:
    if html is None:
        return None
    lower = html.lower()
    if "windrawwin" not in lower and "wttr" not in lower:
        raise RuntimeError("windrawwin: brand marker missing")
    return html


def _get(url: str) -> str | None:
    errors: list[str] = []
    try:
        return _validate_html(cffi_get(url))
    except Exception as exc:  # noqa: BLE001 - fall through to independent relays
        errors.append(f"direct={type(exc).__name__}")
    for relay_name, raw in public_relay.fetches(url):
        try:
            return _validate_html(raw.decode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001 - try next configured relay
            errors.append(f"operator:{relay_name}={type(exc).__name__}")
    raise RuntimeError(f"WinDrawWin GET failed {url}: {', '.join(errors)}")


def _parse(html: str, date: str) -> list[dict]:
    out = []
    league = None
    for chunk in _ROW.split(html):
        lm = _LEAGUE.findall(chunk)
        fix = _FIX.search(chunk) or _FIX2.search(chunk)
        prd = _PRD.search(chunk)
        if fix and prd:
            teams = re.split(r"\s+v\s+", fix.group(1).strip(), maxsplit=1)
            if len(teams) == 2 and teams[1]:
                stk = _STK.search(chunk)
                sc = _SC.search(chunk)
                out.append(
                    {
                        "date": date,
                        "league": league,
                        "home": teams[0].strip(),
                        "away": teams[1].strip(),
                        "pick": PRED_MAP.get(prd.group(1).strip().lower()),
                        "stake": stk.group(1).strip() if stk else None,
                        "pred_score": sc.group(1).strip() if sc else None,
                    }
                )
        if lm:
            cand = [x.strip() for x in lm
                    if x.strip().lower() not in ("reset filter", "today", "tomorrow")]
            if cand:
                league = cand[-1]
    return out


def fetch_day(date: str) -> list[dict]:
    """Capture-forward only: today/tomorrow/future dates. Past dates -> []."""
    today = _date.today().isoformat()
    if date < today:
        return []
    if date == today:
        urls = ["https://www.windrawwin.com/predictions/today/"]
    elif date == (_date.today() + __import__("datetime").timedelta(days=1)).isoformat():
        urls = ["https://www.windrawwin.com/predictions/tomorrow/"]
    else:
        urls = [f"https://www.windrawwin.com/predictions/future/{date.replace('-', '')}/"]
    for url in urls:
        html = _get(url)
        rows = _parse(html, date) if html else []
        if rows:
            return rows
    return []


COLUMNS = ["date", "league", "home", "away", "pick", "stake", "pred_score"]
