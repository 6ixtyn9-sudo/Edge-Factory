"""SoccerVista adapter — capture-forward 1X2 picks from the rebuilt soccervista.com.

URL: https://www.soccervista.com/   (also resolves www.newsoccervista.com)
Coverage: TODAY ONLY. The legacy date-parameterized pages
(soccer_games.php/next_matches.php) are gone ("File not found") and the new
day picker is JS-driven with no plain-GET archive URL, so this source is
capture-forward — the same profile as betclan/afootballreport.

The homepage is a server-rendered table: league separator rows
("USA: MLS") followed by match rows of ten cells — kickoff, home form+name,
"View details for HOME vs AWAY" link cell, away name+form, 1/X/2 average odds,
1X2 pick, goals tip (O/U) and a predicted score. Every match cell links to
/event/<home-away>/<event_id>/ which provides a stable event id. The
"Matches by date <Mon DD>" calendar stamp is verified against the requested
date when present, so day-rollover drift can never stamp fixtures against the
wrong date (integrity), while an absent marker degrades to availability.

No probabilities and no final scores — pick + odds + tips only, so settlement
joins a results donor in the warehouse layer (windrawwin-style). The site is
Cloudflare-fronted, so the transport ladder is urllib -> curl_cffi
impersonation -> operator relays.
"""
from __future__ import annotations

import re
import time
import urllib.error
import urllib.request
from datetime import date as _date

from edgefactory.sources import public_relay

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://www.soccervista.com/",
    # Non-auth consent hints only; never sends identity/session cookies.
    "Cookie": "cookieconsent_status=dismiss; cookie_consent=accepted",
}
URL = "https://www.soccervista.com/"

_ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.I | re.S)
_CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.I | re.S)
_TAG = re.compile(r"<[^>]+>")
_ENTITY = re.compile(r"&(?:nbsp|#160);")
_TIME = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")
_DETAILS = re.compile(r"View details for (.+?) vs (.+?)(?=[\"<]|$)")
_EVENT = re.compile(r"/event/[a-z0-9-]+/([A-Za-z0-9]+)/")
_EVENT_URL = re.compile(r"href=[\"'](/event/[a-z0-9-]+/[A-Za-z0-9]+/)[\"']", re.I)
_PICKS = {"1": "home", "x": "draw", "2": "away"}
_GOALS = {"o": "over", "u": "under"}
_SCORE = re.compile(r"^\s*(\d+)\s*:\s*(\d+)\s*$")
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct",
     "nov", "dec"], start=1)}
# The day-picker marker as rendered next to the calendar: "Matches by date Sep 30".
_DAY_MARKER = re.compile(
    r"Matches by date.{0,400}?([A-Z][a-z]{2})[^A-Za-z0-9]{0,20}(\d{1,2})", re.I | re.S)

MAX_MATCHES = 400  # sanity bound: daily slates are well below this


class TransportValidationError(RuntimeError):
    """A transport returned a shell/challenge instead of the predictions page."""


def _validate_transport_html(html: str | None) -> str:
    if html is None:
        raise TransportValidationError("empty response")
    lower = html.lower()
    if "soccervista" not in lower:
        raise TransportValidationError("brand marker missing")
    if "<table" not in lower:
        raise TransportValidationError("predictions table not found")
    return html


def served_day(html: str) -> tuple[int, int] | None:
    """(month, day) the page says it renders, or None when the marker is absent.

    The calendar widget is server-rendered on the current build; when it is,
    a mismatched stamp means the site is serving a different local day than the
    requested one (near-midnight drift), so the capture must be dropped rather
    than stamp fixtures against the wrong date. A missing marker (JS-rendered
    widget) cannot verify either way and stays fail-open — same posture as the
    ProSoccer H1 check where absence trips, but here the table itself is the
    payload, so availability wins on absent evidence and integrity on
    contradicting evidence.
    """
    m = _DAY_MARKER.search(html)
    if not m:
        return None
    month = _MONTHS.get(m.group(1).lower())
    if month is None:
        return None
    return (month, int(m.group(2)))


def _clean(cell: str) -> str:
    text = _TAG.sub(" ", cell)
    text = _ENTITY.sub(" ", text)
    text = (text.replace("&amp;", "&").replace("&#8217;", "'").replace("&ndash;", "-"))
    return " ".join(text.split())


def _float(text: str) -> float | None:
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _teams_from_cells(cells: list[str]) -> tuple[str | None, str | None]:
    """Fallback team extraction from the form+name cells.

    Home cell runs form letters (W/D/L) then the name; the away cell runs the
    name then form letters. Works on whitespace-joined cell text only when the
    trailing/leading chunk is alphabetic form noise.
    """
    def _strip_form(text: str, side: str) -> str | None:
        words = text.split()
        if side == "home":
            while words and re.fullmatch(r"[WDL]+", words[0]):
                words.pop(0)
        else:
            while words and re.fullmatch(r"[WDL]+", words[-1]):
                words.pop()
        name = " ".join(words).strip("- ")
        return name or None

    home = _strip_form(cells[1], "home") if len(cells) > 1 else None
    away = _strip_form(cells[3], "away") if len(cells) > 3 else None
    return home, away


def _parse(html: str, date: str) -> list[dict]:
    out: list[dict] = []
    league = None
    for row_m in _ROW.finditer(html):
        row = row_m.group(1)
        cells = [_clean(c) for c in _CELL.findall(row)]
        if not cells:
            continue
        # Match rows have ~10 cells and start with a HH:MM kickoff cell; rows
        # without one (table header "1 X 2 1X2 Goals Score", ad slots) are
        # not fixtures, and single wide cells are league separators.
        t = _TIME.match(cells[0])
        if len(cells) < 9 or not t:
            joined = " ".join(cells).strip()
            if len(cells) <= 3 and joined and ":" in joined and "soccervista" not in joined.lower():
                league = joined
            continue
        kickoff = t.group(1) + ":" + t.group(2)
        details = _DETAILS.search(row)
        if details:
            home, away = details.group(1).strip(), details.group(2).strip()
        else:
            home, away = _teams_from_cells(cells)
        if not home or not away or len(out) >= MAX_MATCHES:
            continue
        pick = _PICKS.get(cells[7].strip().lower())
        goals_tip = _GOALS.get(cells[8].strip().lower())
        score_m = _SCORE.match(cells[9]) if len(cells) > 9 else None
        event = _EVENT.search(row)
        event_url = _EVENT_URL.search(row)
        out.append(
            {
                "date": date,
                "kickoff": kickoff,
                "league": league,
                "home": home,
                "away": away,
                "pick": pick,
                "goals_tip": goals_tip,
                "pred_score": f"{score_m.group(1)}:{score_m.group(2)}" if score_m else None,
                "odd1": _float(cells[4]) if len(cells) > 4 else None,
                "oddx": _float(cells[5]) if len(cells) > 5 else None,
                "odd2": _float(cells[6]) if len(cells) > 6 else None,
                "event_id": event.group(1) if event else None,
                "url": event_url.group(1) if event_url else None,
            }
        )
    return out


def _urllib_get(url: str) -> str | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return None
        raise


def _cffi_get(url: str, impersonate: str) -> str | None:
    from curl_cffi import requests as cr

    headers = {key: value for key, value in HEADERS.items() if key.lower() != "user-agent"}
    r = cr.get(url, impersonate=impersonate, timeout=30, headers=headers)
    if r.status_code in (404, 410):
        return None
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    return r.text


def _get(url: str, retries: int = 3) -> str:
    """urllib -> curl_cffi ladder, then operator relays.

    Only returns a page that already has the SoccerVista brand marker and at
    least one HTML table. Branded consent/anti-bot shells are transport
    failures here, before fetch_day parses date or rows.
    """
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
            return _validate_transport_html(request())
        except Exception as exc:  # noqa: BLE001 - retry with a distinct transport
            errors.append(f"{name}={type(exc).__name__}")
            if attempt + 1 < attempt_limit:
                time.sleep(1.5 * (attempt + 1))
    for relay_name, raw in public_relay.fetches(url):
        try:
            text = raw.decode("utf-8", "replace")
            return _validate_transport_html(text)
        except Exception as exc:  # noqa: BLE001 - try the next independent relay
            errors.append(f"operator:{relay_name}={type(exc).__name__}")
    raise RuntimeError(f"SoccerVista GET failed {url}: {', '.join(errors)}")


def fetch_day(date: str, retries: int = 3) -> list[dict]:
    """Today-only capture. Other dates are out of coverage (no network call)
    so the capture pipeline can include this source alongside backfillable
    ones without wasting requests."""
    if date != _date.today().isoformat():
        return []
    html = _get(URL, retries=retries)
    served = served_day(html)
    if served is not None and served != (_date.fromisoformat(date).month,
                                         _date.fromisoformat(date).day):
        # The site is mid-day-rollover (its local calendar behind/ahead of the
        # requested day): stamping these fixtures under ``date`` would corrupt
        # date-keyed settlement joins. Drop the capture; the next run re-tries.
        print(
            f"soccervista: page serves {served} but {date} was requested — "
            "skipping (day-rollover drift)",
            flush=True,
        )
        return []
    return _parse(html, date)


COLUMNS = [
    "date", "kickoff", "league", "home", "away",
    "pick", "goals_tip", "pred_score",
    "odd1", "oddx", "odd2", "event_id", "url",
]
