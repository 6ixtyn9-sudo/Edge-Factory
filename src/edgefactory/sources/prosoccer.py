"""ProSoccer adapter — rolling prediction week, 1X2 probs + odds + settled scores.

URL: https://www.prosoccer.gr/en/football/predictions/[yesterday|tomorrow|Weekday].html
Coverage: the rolling prediction week only (yesterday .. ~six days ahead). The
deep archive at /en/football/archive/ is offline ("migrating to SSL"), so this
source is capture-forward with yesterday settlement — no historical backfill.

Per match (table id="tblPredictions"): league code, kickoff (UTC), ML 1X2
probabilities (%), tip code, average bookmaker odds, two most-probable scores,
U/O 2.5 probabilities (%) and the final score once a match finishes — so the
yesterday page doubles as a results donor. Pagination is client-side JS: the
raw HTML holds every row, and the "out of N soccer matches" banner is used as
a partial-capture tripwire if the layout ever moves server-side.

The site is plain Apache (no Cloudflare), so plain urllib is the primary
transport; curl_cffi impersonation and the operator relays are fallbacks for
hostile egress environments (e.g. cloud datacenter IPs).
"""
from __future__ import annotations

import datetime as _dt
import re
import time
import urllib.error
import urllib.request

from edgefactory.sources import public_relay

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BASE = "https://www.prosoccer.gr/en/football/predictions/"
WINDOW_DAYS = 6  # weekday pages cover roughly this far ahead/behind today

_MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}

_H1 = re.compile(
    r"Intelligent Football Predictions for ([A-Za-z]+) (\d{1,2}) ([A-Za-z]+) (\d{4})")
_TABLE = re.compile(r'<table[^>]*id="tblPredictions"[^>]*>', re.I)
_ROW = re.compile(r"<tr[^>]*>(.*?)</(?:tr|TR)>", re.I | re.S)
_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.I | re.S)
_TAG = re.compile(r"<[^>]+>")
_ENTITY = re.compile(r"&(?:nbsp|#160);")
_COUNT = re.compile(r"out of (\d+) soccer matches")
_TIME = re.compile(r"^\s*(\d{1,2}:\d{2})\s*$")
_SCORE = re.compile(r"(\d+)\s*-\s*(\d+)")
_TEAMS_SPLIT = re.compile(r"\s+-\s+")


def _clean(cell: str) -> str:
    """Strip tags/comments and normalize entities+whitespace from a cell."""
    text = _TAG.sub(" ", cell)
    text = _ENTITY.sub(" ", text)
    text = (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&quot;", '"').replace("&#8211;", "-").replace("&ndash;", "-"))
    return " ".join(text.split())


def page_date(html: str) -> str | None:
    """ISO date asserted by the page H1, else None (layout shift detector)."""
    m = _H1.search(html)
    if not m:
        return None
    month = _MONTHS.get(m.group(3).lower())
    if month is None:
        return None
    try:
        return _dt.date(int(m.group(4)), month, int(m.group(2))).isoformat()
    except ValueError:
        return None


def _score_pair(cell: str) -> tuple[int | None, int | None]:
    m = _SCORE.search(cell)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def _pct(text: str) -> float | None:
    try:
        v = float(text.rstrip("%"))
    except (TypeError, ValueError):
        return None
    return v if 0.0 <= v <= 100.0 else None


def _price(text: str) -> float | None:
    try:
        v = float(text)
    except (TypeError, ValueError):
        return None
    return v if v >= 1.0 else None


def _parse(html: str, date: str) -> list[dict]:
    """Parse the predictions table. Raises on missing table (layout shift /
    challenge page) so the day stays retryable instead of masquerading as a
    zero-fixture slate."""
    table_open = _TABLE.search(html)
    if not table_open:
        if "Page not found" in html:
            return []
        raise RuntimeError("prosoccer: tblPredictions table not found in page")
    close = html.find("</table>", table_open.end())
    body = html[table_open.end(): close if close != -1 else len(html)]

    out = []
    for row_m in _ROW.finditer(body):
        cells = [_clean(c) for c in _CELL.findall(row_m.group(1))]
        # match rows carry 15 columns: league, time, match, p1,px,p2, tip,
        # odd1,oddx,odd2, pred1, pred2, u25, o25, final. Require the core 10.
        if len(cells) < 10:
            continue
        t = _TIME.match(cells[1])
        teams = _TEAMS_SPLIT.split(cells[2], maxsplit=1)
        p1, px, p2 = _pct(cells[3]), _pct(cells[4]), _pct(cells[5])
        if not t or len(teams) != 2 or not teams[0] or not teams[1]:
            continue
        if p1 is None or px is None or p2 is None:
            continue
        pred1 = pred2 = None
        if len(cells) > 10:
            ph, pg = _score_pair(cells[10])
            pred1 = f"{ph}-{pg}" if ph is not None else None
        if len(cells) > 11:
            ph, pg = _score_pair(cells[11])
            pred2 = f"{ph}-{pg}" if ph is not None else None
        p_u25 = _pct(cells[12]) if len(cells) > 12 else None
        p_o25 = _pct(cells[13]) if len(cells) > 13 else None
        hs = gs = None
        status = None
        if len(cells) > 14 and cells[14]:
            hs, gs = _score_pair(cells[14])
            status = "FT" if hs is not None else cells[14] or None
        out.append(
            {
                "date": date,
                "kickoff": t.group(1),
                "league": cells[0] or None,
                "home": teams[0].strip(),
                "away": teams[1].strip(),
                "p1": p1, "px": px, "p2": p2,
                "tip": cells[6] or None,
                "odd1": _price(cells[7]), "oddx": _price(cells[8]),
                "odd2": _price(cells[9]),
                "pred_score1": pred1, "pred_score2": pred2,
                "p_u25": p_u25, "p_o25": p_o25,
                "hs": hs, "gs": gs, "status": status,
            }
        )

    banner = _COUNT.search(html)
    if banner and len(out) < int(banner.group(1)):
        print(
            f"prosoccer {date}: parsed {len(out)} of {banner.group(1)} rows "
            "(layout may have shifted to server-side pagination)",
            flush=True,
        )
    return out


def url_for(date: str, today: str | None = None) -> str | None:
    """Deterministic URL for a target date, or None when out of coverage.

    ProSoccer only serves the rolling prediction week: today, yesterday,
    tomorrow and ``{Weekday}.html`` for nearby days. The H1 date check in
    fetch_day is the final guard against a stale or mis-routed page.
    """
    today_d = _dt.date.fromisoformat(today) if today else _dt.date.today()
    target = _dt.date.fromisoformat(date)
    delta = (target - today_d).days
    if delta == 0:
        return BASE
    if delta == -1:
        return BASE + "yesterday.html"
    if delta == 1:
        return BASE + "tomorrow.html"
    if abs(delta) <= WINDOW_DAYS:
        return BASE + target.strftime("%A") + ".html"
    return None


def _urllib_get(url: str) -> str | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            # force_date / stale weekday pages redirect back to the plain today
            # page; the H1 date check in fetch_day catches that mismatch.
            html = r.read().decode("utf-8", "replace")
            if "Page not found" in html:
                return None
            return html
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return None
        raise


def _cffi_get(url: str, impersonate: str) -> str | None:
    from curl_cffi import requests as cr

    r = cr.get(url, impersonate=impersonate, timeout=30,
               headers={"Accept-Language": "en-US,en;q=0.9"})
    if r.status_code in (404, 410):
        return None
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    if "Page not found" in r.text:
        return None
    return r.text


def _get(url: str, retries: int = 3) -> str | None:
    """urllib -> curl_cffi ladder, then operator relays. Returns None when the
    page legitimately does not exist; raises when every transport failed."""
    from . import cffi_http

    transports: list[tuple[str, object]] = [("urllib", lambda: _urllib_get(url))]
    for identity in (cffi_http.IMPERSONATE, cffi_http.FALLBACK):
        transports.append(
            (f"curl_cffi:{identity}", lambda identity=identity: _cffi_get(url, identity))
        )
    errors: list[str] = []
    attempt_limit = max(1, min(int(retries), len(transports)))
    for attempt, (name, request) in enumerate(transports[:attempt_limit]):
        try:
            return request()
        except Exception as exc:  # noqa: BLE001 - retry with a distinct transport
            errors.append(f"{name}={type(exc).__name__}")
            if attempt + 1 < attempt_limit:
                time.sleep(1.5 * (attempt + 1))
    relay_errors = []
    for relay_name, raw in public_relay.fetches(url):
        try:
            text = raw.decode("utf-8", "replace")
            if "tblPredictions" in text or "Page not found" in text:
                return None if "Page not found" in text else text
            relay_errors.append(f"operator:{relay_name}=unvalidated")
        except Exception as exc:  # noqa: BLE001 - try the next independent relay
            relay_errors.append(f"operator:{relay_name}={type(exc).__name__}")
    if relay_errors or not errors:
        errors.extend(relay_errors or ["no transport available"])
    raise RuntimeError(f"ProSoccer GET failed {url}: {', '.join(errors)}")


def fetch_day(date: str, retries: int = 3) -> list[dict]:
    """Fetch one calendar day inside the rolling prediction week.

    Returns [] for out-of-coverage dates (no network) and for dates whose
    served page asserts a different H1 date (guards pipeline determinism when
    the site re-routes stale weekday pages back to today).
    """
    url = url_for(date)
    if url is None:
        return []
    html = _get(url, retries=retries)
    if not html:
        return []
    served = page_date(html)
    if served is None:
        raise RuntimeError("prosoccer: page H1 date missing (layout shift)")
    if served != date:
        # e.g. a weekday page outside the prediction week falls back to today
        return []
    return _parse(html, date)


COLUMNS = [
    "date", "kickoff", "league", "home", "away",
    "p1", "px", "p2", "tip", "odd1", "oddx", "odd2",
    "pred_score1", "pred_score2", "p_u25", "p_o25",
    "hs", "gs", "status",
]
