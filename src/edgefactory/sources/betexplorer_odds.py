"""BetExplorer live odds adapter — niche-league coverage for unmatched picks.

Fetches 1x2 odds from BetExplorer for matches that bzzoiro_odds and
scoutingstats_odds don't cover (Australian NPL, Belarus, Latvia, Kuwait,
Tanzania, etc.).

Usage pattern:
  1. fetch_day_matches(date) → list of all matches for that date
  2. match_pick_to_betexplorer(pick, matches) → matched match dict or None
  3. fetch_match_odds(match_url, event_id) → {odd1, oddx, odd2} or None

While doing (3) the adapter also retains, in ``LAST_MATCH_DETAIL``, what the
responses it already holds spell out: one comparison response per market
(1x2 and the O/U, AH, DNB, DC, BTTS tabs — one request each, the same hop the
page makes when the tab is clicked) with every handicap line, per-bookmaker
price, rank, movement, creation stamp and the page's own best-price flag, plus
the match page's H2H, last-results and standings blocks.  That detail is
written to a same-day ledger and is never read by pricing, cards or ML.

The picks_today.py enrichment layer calls betexplorer_enrich_unmatched()
for picks that failed bzzoiro + scoutingstats enrichment.  It only
fetches odds for the specific unmatched picks (typically 5-10 per day),
not the full BetExplorer universe.

Rate-limiting: BetExplorer returns 429 if you hit it too fast.  This
adapter enforces a 3-second minimum interval between requests and caches
the daily match-list page so it's fetched only once per run.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from edgefactory.identity import club_initial_words_for_comparison, squad_marker_mismatch
from edgefactory.util import strip_squad_markers

BASE = "https://www.betexplorer.com"
# A descriptive, cooperative identity; no evasion or browser impersonation is
# needed for this adapter. The site is queried only for bounded rescue rows.
UA = "EdgeFactory-cooperative-audit/1.0 (+operator review)"

# Minimum seconds between consecutive requests to BetExplorer
_MIN_INTERVAL = 3.0
_last_request_time: float = 0.0

# Single-flight transport: even if two callers enter through a future worker
# pool, only one request (and its backoff) can be in flight at a time.
_request_lock = threading.Lock()

# In-memory cache for the daily match-list page (fetched once per date per run)
_match_cache: dict[str, list[dict]] = {}
_fixture_cache: dict[str, list[dict]] = {}
# Fixture keys already re-read this run for their match detail (one try each).
_detail_attempted: set[str] = set()

BETEXPLORER_ODDS_SOURCE = "betexplorer_odds"
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))
CACHE_FRESHNESS_H = float(os.environ.get("EDGE_FACTORY_BE_CACHE_FRESHNESS_H", "24"))

# Per-run health/thermal state. It is deliberately reset only by
# reset_fetch_count(), which the picks enrichment calls once per run.
_be_429 = 0
_be_cooling_down = False
_be_cached = 0
# Row-level identity refusals for the current run, keyed by reason. Reset by
# reset_fetch_count() and surfaced through run_stats() so a refused row is
# visible in the run receipt (silently dropped prices are the failure mode the
# 2026-10-12 Forge vs York United receipt came from).
_be_rows_rejected: dict[str, int] = {}


def _record_row_rejections(rejected: dict[str, int]) -> None:
    for reason, count in (rejected or {}).items():
        _be_rows_rejected[reason] = _be_rows_rejected.get(reason, 0) + int(count)


# Network-attempt counters for the run: every attempt inside _fetch() counts,
# including retries, so the receipt shows what the site actually saw.
_request_count = 0
_market_requests = 0
_market_budget_stop = False

LAST_RESULTS_RECEIPT: dict[str, object] = {}
_LAST_RESPONSE_META: dict[str, object] = {}
_LAST_RESPONSE_BYTES: bytes = b""
_CHALLENGE_MARKERS = (
    "captcha",
    "verify you are human",
    "checking your browser",
    "security verification",
    "access denied",
    "age verification",
    "confirm your age",
    "cf-chl-",
)


class BetExplorerChallenge(RuntimeError):
    """The result page returned a challenge/verification surface."""


class BetExplorerCoolingDown(RuntimeError):
    """No more BetExplorer requests are permitted in this run."""


def last_response_bytes() -> bytes:
    """Return the most recent response bytes for an audit/raw receipt."""
    return _LAST_RESPONSE_BYTES


def run_stats() -> dict[str, int | bool]:
    """Return compact run-scoped BetExplorer diagnostics."""
    return {
        "be_429": _be_429,
        "be_cooling_down": _be_cooling_down,
        "be_cached": _be_cached,
        "be_rows_rejected": sum(_be_rows_rejected.values()),
        "be_rows_rejected_reasons": dict(_be_rows_rejected),
    }


def request_stats() -> dict[str, int | bool]:
    """Network-attempt counters for the run (priced lane + tab requests)."""
    return {"requests": _request_count,
            "market_requests": _market_requests,
            "market_budget_stop": _market_budget_stop}


def _retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    value = exc.headers.get("Retry-After") if exc.headers else None
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        try:
            when = parsedate_to_datetime(str(value))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return max(0.0, when.timestamp() - datetime.now(timezone.utc).timestamp())
        except (TypeError, ValueError, OverflowError):
            return None


def _throttle(min_interval: float | None = None):
    """Enforce minimum interval between requests (never below _MIN_INTERVAL)."""
    global _last_request_time
    interval = _MIN_INTERVAL if min_interval is None else max(_MIN_INTERVAL, float(min_interval))
    elapsed = time.monotonic() - _last_request_time
    if elapsed < interval:
        time.sleep(interval - elapsed)
    _last_request_time = time.monotonic()


def _fetch(url: str, referer: str | None = None, retries: int = 3, timeout: int = 20,
           *, min_interval: float | None = None) -> str:
    """Fetch one URL, single-flight, with respectful 429 handling.

    The first 429 sleeps for a default 30 seconds and a second retry sleeps
    for 60 seconds. An explicit Retry-After header wins (including values over
    60 seconds). The second 429 trips run-scoped cooling and raises before any
    third request can be attempted.
    """
    global _be_429, _be_cooling_down, _LAST_RESPONSE_META, _LAST_RESPONSE_BYTES, _request_count
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    with _request_lock:
        _LAST_RESPONSE_BYTES = b""
        _LAST_RESPONSE_META = {"url": url, "http_status": None, "response_bytes": 0, "sha256": None}
        for attempt in range(retries):
            if _be_cooling_down:
                raise BetExplorerCoolingDown("betexplorer_odds: run cooling down after 2 HTTP 429 responses")
            _throttle(min_interval)
            _request_count += 1
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                    _LAST_RESPONSE_BYTES = body
                    _LAST_RESPONSE_META = {
                        "url": url,
                        "http_status": int(getattr(r, "status", 200) or 200),
                        "response_bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest(),
                    }
                    return body.decode("utf-8", "replace")
            except urllib.error.HTTPError as exc:
                _LAST_RESPONSE_META = {
                    "url": url,
                    "http_status": int(exc.code),
                    "response_bytes": 0,
                    "sha256": None,
                }
                if exc.code == 403:
                    raise BetExplorerChallenge("betexplorer_odds: HTTP 403") from exc
                if exc.code == 429:
                    _be_429 += 1
                    if _be_429 >= 2:
                        _be_cooling_down = True
                        print(
                            "  betexplorer_odds: 2nd 429; cooling down for the rest of this run",
                            file=sys.stderr,
                        )
                        raise BetExplorerCoolingDown("betexplorer_odds: second 429") from exc
                    retry_after = _retry_after_seconds(exc)
                    # Default policy is 30-60s; a server Retry-After is
                    # authoritative and may be longer.
                    wait = retry_after if retry_after is not None else min(60.0, 30.0 * (attempt + 1))
                    print(
                        f"  betexplorer_odds: 429 rate limit, waiting {wait:.0f}s "
                        f"(Retry-After={retry_after!r})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue
                if exc.code == 404:
                    return ""
                raise
            except BetExplorerCoolingDown:
                raise
            except Exception:
                if attempt == retries - 1:
                    raise
                time.sleep(5.0 * (attempt + 1))
    raise RuntimeError(f"betexplorer_odds: failed after {retries} retries: {url}")


def _ffloat(x: object) -> float | None:
    try:
        v = float(str(x).strip())
        if math.isfinite(v) and v > 1.0:
            return v
    except Exception:
        pass
    return None


def parse_results_page(page: str) -> list[dict]:
    """Parse match entries from a BetExplorer results/schedule page."""
    out: list[dict] = []
    current_country: str | None = None
    current_league: str | None = None
    token_re = re.compile(
        r'(<tr class="js-tournament".*?</tr>|<tr data-dt=".*?</tr>)', re.S
    )
    for token in token_re.findall(page):
        if 'class="js-tournament"' in token:
            m = re.search(
                r'class="table-main__tournament"[^>]*>\s*(?:<i>.*?</i>)?\s*([^<]+)</a>',
                token, re.S,
            )
            label = re.sub(r"<[^>]+>", " ", html.unescape(m.group(1))).strip() if m else "UNKNOWN"
            if ":" in label:
                current_country, current_league = [x.strip() for x in label.split(":", 1)]
            else:
                current_country, current_league = None, label.strip() or "UNKNOWN"
            continue

        dt = re.search(r'data-dt="(\d+),(\d+),(\d+),(\d+),(\d+)"', token)
        link = re.search(
            r'<td class="table-main__tt">.*?<a href="([^"]+)">(.*?)</a>', token, re.S
        )
        if not (dt and link):
            continue
        match_text = re.sub(r"<[^>]+>", " ", html.unescape(link.group(2)))
        match_text = " ".join(match_text.split())
        if " - " not in match_text:
            continue
        home, away = [x.strip() for x in match_text.split(" - ", 1)]
        score = re.search(
            r'class="table-main__result"[^>]*>.*?(?:<strong[^>]*>)?\s*(\d+)\s*[:\-]\s*(\d+)',
            token,
            re.S,
        )
        from edgefactory.settlement import result_period_status
        result_cell = re.search(r'class="table-main__result"[^>]*>(.*?)</td>', token, re.S)
        period_status = result_period_status(html.unescape(result_cell.group(1))) if result_cell else ""
        dd, mm, yyyy, hh, minute = [int(x) for x in dt.groups()]
        event_id = link.group(1).rstrip("/").split("/")[-1]
        rel_url = html.unescape(link.group(1))
        full_url = rel_url if rel_url.startswith("http") else BASE + rel_url
        out.append({
            "date": f"{yyyy:04d}-{mm:02d}-{dd:02d}",
            "kickoff": f"{hh:02d}:{minute:02d}",
            "data_dt": [dd, mm, yyyy, hh, minute],
            "kickoff_date": f"{yyyy:04d}-{mm:02d}-{dd:02d}",
            "country": current_country,
            "league": current_league,
            "home": home,
            "away": away,
            "hs": score.group(1) if score else "",
            "gs": score.group(2) if score else "",
            "ht_hs": "",
            "ht_gs": "",
            "status": period_status,
            "match_url": full_url,
            "event_id": event_id,
        })
    return out


def fetch_day_matches(day: str) -> list[dict]:
    """Fetch and parse all matches for a given date from BetExplorer.

    Results are cached in-memory so multiple calls for the same date only hit
    BetExplorer once.  ``LAST_RESULTS_RECEIPT`` is populated for the bounded
    remine driver; the normal odds enrichment may ignore it.
    """
    global LAST_RESULTS_RECEIPT
    if day in _match_cache:
        return _match_cache[day]
    y, m, d = day.split("-")
    url = f"{BASE}/football/results/?year={y}&month={m}&day={d}"
    try:
        page = _fetch(url)
        lower = page.lower()
        if any(marker in lower for marker in _CHALLENGE_MARKERS):
            LAST_RESULTS_RECEIPT = {
                "status": "challenge",
                "url": url,
                **_LAST_RESPONSE_META,
            }
            raise BetExplorerChallenge("betexplorer_odds: challenge/verification page")
        matches = [row for row in parse_results_page(page) if row.get("date") == day]
        http_status = int(_LAST_RESPONSE_META.get("http_status", 200) or 200)
        LAST_RESULTS_RECEIPT = {
            # A 404 is a transport/status failure, not evidence that a
            # successfully fetched results page was empty.
            "status": "http_404" if http_status == 404 else ("success" if matches else "no_matches_day"),
            "url": url,
            "date": day,
            "rows": len(matches),
            **_LAST_RESPONSE_META,
        }
        _match_cache[day] = matches
        return matches
    except BetExplorerChallenge:
        # This is a source-level safety signal. Do not turn it into an
        # apparently empty day, which would poison the gap ledger.
        LAST_RESULTS_RECEIPT = {
            "status": "challenge",
            "url": url,
            "date": day,
            **_LAST_RESPONSE_META,
        }
        raise
    except BetExplorerCoolingDown:
        LAST_RESULTS_RECEIPT = {
            "status": "cooldown",
            "url": url,
            "date": day,
            **_LAST_RESPONSE_META,
        }
        raise
    except Exception as exc:
        LAST_RESULTS_RECEIPT = {
            "status": "transport_error",
            "url": url,
            "date": day,
            "error": f"{type(exc).__name__}: {exc}",
            **_LAST_RESPONSE_META,
        }
        print(f"  betexplorer_odds: failed to fetch match list for {day}: {exc}", file=sys.stderr)
        _match_cache[day] = []
        return []


def match_pick_to_betexplorer(
    pick: dict,
    matches: list[dict],
    *,
    norm_team_fn=None,
    norm_width: int = 9,
) -> dict | None:
    """Find a unique, pair- and schedule-consistent page for this pick.

    Legacy norm_width remains an interface argument, not identity proof: a
    shared short key or one matching opponent cannot identify a fixture.
    """
    pick_league = str(pick.get("league") or "")
    candidates = []
    for match in matches:
        straight, swapped = _team_pair_agreement(match, pick, norm_team_fn=norm_team_fn)
        if straight == swapped:  # neither agrees, or orientation is ambiguous
            continue
        if not row_belongs_to_pick(
                match, pick, str(pick.get("date") or match.get("date") or ""),
                norm_team_fn=norm_team_fn)[0]:
            continue
        candidates.append((0 if straight else 1, match))

    if not candidates:
        return None

    def sort_key(item):
        priority, match = item
        league = str(match.get("league") or match.get("country") or "").lower()
        league_match = 0 if pick_league.lower() in league or league in pick_league.lower() else 1
        return priority, league_match

    candidates.sort(key=sort_key)
    best = candidates[0]
    # Duplicate copies of one page are harmless; distinct equally plausible
    # events must not be resolved by input order (or arbitrary event ID).
    if any(match != best[1] for priority, match in candidates
           if sort_key((priority, match)) == sort_key(best)):
        return None
    return best[1]


def parse_best_1x2(odds_html: str) -> dict | None:
    """Best (max) 1x2 price across the comparison rows — the priced lane's contract.

    Unchanged: the row set is the ``best-odds-0`` tbody and the value kept is
    the maximum per column.
    """
    block = re.search(r'<tbody id="best-odds-0">(.*?)</tbody>', odds_html or "", re.S)
    if not block:
        return None

    best = [None, None, None]
    rows = re.findall(r"<tr\b.*?</tr>", block.group(1), re.S)
    for row in rows:
        cells = re.findall(r'data-odd="([0-9.]+)"', row)
        if len(cells) >= 3:
            for i in range(3):
                v = _ffloat(cells[i])
                if v is not None and (best[i] is None or v > best[i]):
                    best[i] = v

    if all(v is not None for v in best):
        return {"odd1": best[0], "oddx": best[1], "odd2": best[2]}
    return None


# --- retained match detail: the SAME two responses, more of what they hold ---
#
# Observed markup (public match-odds response, inspected 2026-10-12): every
# comparison row carries the bookmaker itself — data-bookie="stake.com" on the
# price elements, a <span class="in-bookmaker-logo ..." title="Stake.com"> in
# the narrow cell, and the link text in the wide cell — plus data-odd,
# data-created (dd,mm,yyyy,hh,mm), data-pos (rank of that price) and an
# icon__decreasing / icon__increasing movement arrow.  The response also
# carries the hidden all-bookmakers block (div.oddsComparisonAll__rowBookie)
# and the average line (div.oddsComparisonAll__average_text).  The priced lane
# keeps the best triple only; this parse keeps what the row markup spells out.
_MAX_BOOKS_RETAINED = 24
# The match page serves the whole H2H list and the whole league table; the
# "Show more matches" and "Show full table" controls only toggle them, so the
# caps bound a pathological page, not the page's own view.
_MAX_H2H_ROWS = 40
_MAX_LAST_RESULT_ROWS = 10
_MAX_STANDINGS_ROWS = 40

# One comparison response per market — exactly the AJAX hop the page makes when
# that tab is clicked (observed on the public match-odds endpoints 2026-10-12).
# Every handicap line of that market AND its hidden all-bookmakers block travel
# inside the single response, so the per-line and ALL/2.5/3.5 "clicks" the page
# shows are client-side toggles, not additional requests.
#: The page's own tab codes, in the page's own order (ha is DNB: the menu's
#: data attribute says dnb while its click code and the URL say ha).
MARKETS: tuple[str, ...] = ("1x2", "ou", "ah", "ha", "dc", "bts")
#: Everything beyond the priced 1x2 lane: fetched only for priced fixtures.
DETAIL_MARKETS: tuple[str, ...] = tuple(slug for slug in MARKETS if slug != "1x2")
MARKET_TABS_ENABLED = (os.environ.get("EDGE_FACTORY_BE_MARKET_TABS", "1")
                       not in {"0", "false", "False", "no"})
#: The priced path keeps the lane's 3s throttle; the opt-in tab requests take
#: the wider gap the operator's bounds used for additional collection.
_MARKET_INTERVAL = 5.1
_MAX_REQUESTS_PER_RUN = int(
    os.environ.get("EDGE_FACTORY_BE_MAX_REQUESTS_PER_RUN", "180") or 180)
#: Bounds for one market's retained rows: single-line markets keep up to 24
#: rows (all of their bookmakers), multi-line markets keep up to 10 lines
#: with up to 6 bookmakers each. Totals preserve supported 1.5/2.5/3.5/4.5
#: lines first; other markets keep lines nearest level. Labels come from
#: the response markup; nothing is padded, renamed or guessed.
_MAX_MARKET_ROWS = 48
_MAX_MARKET_LINES = 10
_MAX_MARKET_BOOKS_PER_LINE = 6

LAST_MATCH_DETAIL: dict | None = None

_ODDS_BLOCK_RE = re.compile(
    r'<(?:td|div)\b(?P<attrs>[^>]*\bdata-odd="[0-9]+(?:\.[0-9]+)?"[^>]*)>(?P<body>.*?)</(?:td|div)>',
    re.S,
)
_BEST_TBODY_RE = re.compile(
    r'<tbody\b[^>]*id="best-odds-(?P<hcap>[^"]+)"[^>]*>(?P<body>.*?)</tbody>', re.S)
# Rows are captured WITH their opening tag: the row-level data-bo flag and the
# data-bookie-id attribute live there, and the cells alone cannot show them.
_ROW_RE = re.compile(r"<tr\b[^>]*>.*?</tr>", re.S)
_ALL_ROW_RE = re.compile(
    r'<div class="oddsComparisonAll__rowBookie[^"]*"[^>]*>.*?'
    r'(?=<div class="oddsComparisonAll__rowBookie|\Z)',
    re.S,
)
_AVERAGE_RE = re.compile(r'class="oddsComparisonAll__average_text"[^>]*data-odd="([0-9.]+)"')
# Column labels are the table head's own odds columns, in order.
_TH_LABEL_RE = re.compile(
    r'<th\b[^>]*class="[^"]*table-main__detail-odds[^"]*"[^>]*>(.*?)</th>', re.S)
# Display name first (the site's own title/link label), the lowercase
# data-bookie key only as a fallback when neither display form is present.
_BOOK_LABEL_RES = (
    r'<span class="in-bookmaker-logo[^"]*"\s+title="([^"]+)"',
    r'class="in-bookmaker-logo-link[^"]*"[^>]*>([^<]+)</a>',
    r'data-bookie="([^"]+)"',
)
# The id the row markup attaches to the bookmaker itself: the bookie id on the
# row, or the name link's bid. The operation id in data-bookmaker-id (a
# different id space, e.g. 549 for bet365.us' 1105) is deliberately not used.
_BOOK_ID_RES = (
    r'data-bookie-id="([^"]+)"',
    r'class="in-bookmaker-logo-link[^"]*"[^>]*data-bid="([^"]+)"',
)


def _clean_attr(value: object) -> str:
    return html.unescape(str(value or "")).strip()


def _attr_map(attrs: str) -> dict:
    return {key: _clean_attr(value)
            for key, value in re.findall(r'data-([a-z0-9-]+)="([^"]*)"', attrs)}


def _created_stamp(raw: object) -> str | None:
    """'12,10,2026,05,52' -> '2026-10-12T05:52' (site-local stamp, no zone claim)."""
    parts = str(raw or "").split(",")
    if len(parts) != 5 or not all(part.strip().isdigit() for part in parts):
        return None
    day, month, year, hour, minute = (int(part) for part in parts)
    if not (1 <= month <= 12 and 1 <= day <= 31 and hour <= 23 and minute <= 59):
        return None
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}"


def _odds_cell(attrs: str, body: str) -> dict:
    data = _attr_map(attrs)
    movement = None
    if "icon__decreasing" in attrs or "icon__decreasing" in body:
        movement = "down"
    elif "icon__increasing" in attrs or "icon__increasing" in body:
        movement = "up"
    return {
        "odds": _ffloat(data.get("odd")),
        # Kept as the page spelled it: some markets use two-place codes
        # ("02"), so casting to int would invent a rank the page never wrote.
        "pos": data.get("pos") or None,
        "created": _created_stamp(data.get("created")),
        "movement": movement,
        "best": "archiveOddsMovement__odds_best" in attrs,
    }


def _book_field(segment: str, patterns: tuple) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, segment)
        if match:
            value = _clean_attr(match.group(1))
            if value:
                return value
    return None


def _line_label(raw: object) -> str | None:
    """Handicap label as the markup spells it ("handicap-0.50" -> "0.50")."""
    text = _clean_attr(raw).removeprefix("handicap-")
    return text or None


def _line_sort_key(label: str):
    try:
        value = float(str(label).replace("+", ""))
    except (TypeError, ValueError):
        return (1, 0.0, str(label))
    return (0, abs(value), value)


def _columns_from_thead(html_text: str) -> list[str]:
    """The market's own column labels, longest head wins."""
    columns: list[str] = []
    for thead in re.findall(r"<thead\b[^>]*>(.*?)</thead>", html_text, re.S):
        labels = [_clean_attr(re.sub(r"<[^>]+>", " ", cell))
                  for cell in _TH_LABEL_RE.findall(thead)]
        labels = [label for label in labels if label]
        if len(labels) > len(columns):
            columns = labels
    return columns


def _row_from_segment(segment: str, *, line: str | None, source: str, width: int) -> dict | None:
    """One comparison row (bookmaker x line) from its own markup."""
    cells = [_odds_cell(match.group("attrs"), match.group("body"))
             for match in _ODDS_BLOCK_RE.finditer(segment)]
    if not cells:
        return None
    pad = max(0, width - len(cells))
    return {
        "bookmaker": _book_field(segment, _BOOK_LABEL_RES),
        "bookmaker_id": _book_field(segment, _BOOK_ID_RES),
        # The line comes from the section the row sits in (its own tbody id or
        # the data-all-handicap group), never from a guessed cell class.
        "line": line,
        "source": source,
        "odds": [cell["odds"] for cell in cells[:width]] + [None] * pad,
        "pos": [cell["pos"] for cell in cells[:width]] + [None] * pad,
        "created": [cell["created"] for cell in cells[:width]] + [None] * pad,
        "movement": [cell["movement"] for cell in cells[:width]] + [None] * pad,
        # The page's own flags: data-bo on the row ("offers a best price"),
        # or the best-price class on a price element.
        "best": 'data-bo="true"' in segment or any(cell["best"] for cell in cells[:width]),
    }


def _all_block_chunks(html_text: str) -> list[tuple[str | None, str]]:
    """(line label, chunk) per data-all-handicap section of the response."""
    parts = re.split(r'data-all-handicap="([^"]*)"', html_text)
    return [(_line_label(parts[index]), parts[index + 1])
            for index in range(1, len(parts) - 1, 2)]


def _collect_market_rows(html_text: str, width: int) -> list[dict]:
    rows: list[dict] = []
    for tbody in _BEST_TBODY_RE.finditer(html_text):
        line = _line_label(tbody.group("hcap"))
        for segment in _ROW_RE.findall(tbody.group("body")):
            row = _row_from_segment(segment, line=line, source="table", width=width)
            if row:
                rows.append(row)
    for chunk_line, chunk in _all_block_chunks(html_text):
        for match in _ALL_ROW_RE.finditer(chunk):
            row = _row_from_segment(match.group(0), line=chunk_line, source="all", width=width)
            if row:
                rows.append(row)
    return rows


def _cap_market_rows(rows: list[dict], *, totals: bool = False) -> tuple[list[dict], list[str]]:
    """Bound retained evidence, not betting eligibility or the request budget.

    Totals must not lose the supported half-goal ladder to low quarter lines.
    Handicap markets retain their existing nearest-level policy. Preserve the
    page's labels and per-line book order, with the same row/line/book caps.
    """
    lines: list[str] = []
    for row in rows:
        label = row.get("line")
        if label and label not in lines:
            lines.append(label)
    lines = sorted(lines, key=_line_sort_key)
    if len(lines) <= 1:
        return rows[:_MAX_BOOKS_RETAINED], lines

    # Reserve one original spelling of each supported numeric level before
    # allocating more rows to aliases such as "1.5" / "1.50" / "+1.50".
    # Do not rewrite the evidence or let aliases hide the other half lines.
    preferred = set()
    seen_levels = set()
    if totals:
        for label in sorted(lines, key=lambda label: (_line_sort_key(label), label)):
            try:
                value = float(label)
            except ValueError:
                continue
            if value in {1.5, 2.5, 3.5, 4.5} and value not in seen_levels:
                preferred.add(label)
                seen_levels.add(value)

    def retention_key(label):
        return (label not in preferred, _line_sort_key(label))

    keep_lines = sorted(lines, key=retention_key)[:_MAX_MARKET_LINES]
    kept: list[dict] = []
    for label in keep_lines:
        on_line = 0
        for row in rows:
            if row.get("line") != label:
                continue
            if on_line >= _MAX_MARKET_BOOKS_PER_LINE or len(kept) >= _MAX_MARKET_ROWS:
                break
            kept.append(row)
            on_line += 1
    # Report the lines that survived the cap: `lines` always describes what
    # `rows` holds, never a line whose rows the budget pushed out.
    kept_lines = [label for label in lines
                  if any(row.get("line") == label for row in kept)]
    kept.sort(key=lambda row: _line_sort_key(row["line"]))
    return kept, kept_lines


def _averages_from_sections(html_text: str, columns: list[str]) -> tuple[list[float] | None, dict]:
    """The site's own average line — per handicap section, flat when unambiguous.

    Every hidden all-bookmakers section carries its own average figures, so a
    multi-line market reads the averages of each line; a flat ``average`` is
    only reported when the single line leaves no room for confusion.
    """
    width = len(columns)
    by_line: dict[str, list[float]] = {}
    flat: list[float] | None = None
    for line, chunk in _all_block_chunks(html_text):
        values = [value for value in (_ffloat(raw) for raw in _AVERAGE_RE.findall(chunk))
                  if value is not None]
        if not values or not width or len(values) != width:
            continue
        if line:
            by_line[line] = values
        if flat is None:
            flat = values
    if len(by_line) > 1:
        flat = None
    return flat, by_line


def parse_market_response(odds_html: str) -> dict:
    """Columns, handicap lines and per-book rows for one market's response.

    Everything is read from the response's own markup: column labels from the
    table head, the line from the section each row sits in (its tbody id or
    the data-all-handicap group), prices, ranks, movement and creation stamps
    from each price element, and the bookmaker from the row's own label
    markup. A row whose markup
    carries no bookmaker keeps ``bookmaker: None`` — a label is never invented
    from a position, an index or a lookalike. For a line the hidden
    all-bookmakers block covers, its rows win over the table's, because that
    block is the site's own "every bookmaker" view; what is left is
    deduplicated on (bookmaker, line, odds).
    """
    html_text = odds_html or ""
    columns = _columns_from_thead(html_text)
    width = len(columns) if len(columns) >= 2 else 3
    rows = _collect_market_rows(html_text, width)
    all_lines = {row["line"] for row in rows if row["source"] == "all" and row["line"]}

    deduped: dict[tuple, dict] = {}
    for row in rows:
        if row["source"] == "table" and row["line"] in all_lines:
            continue
        key = (row["bookmaker"], row["line"], tuple(row["odds"]))
        deduped.setdefault(key, row)

    kept, lines = _cap_market_rows(
        list(deduped.values()), totals=[c.lower() for c in columns] == ["over", "under"])
    average, average_by_line = _averages_from_sections(html_text, columns)
    return {
        "columns": columns,
        "lines": lines,
        "rows": kept,
        "rows_count": len(kept),
        "named_rows": sum(1 for row in kept if row["bookmaker"]),
        "bookmakers": sorted({row["bookmaker"] for row in kept if row["bookmaker"]}),
        "average": average,
        "average_by_line": average_by_line,
    }


def _market_rows_present(markets: dict) -> bool:
    """True when at least one market response produced retained rows."""
    return any(isinstance(market, dict) and market.get("rows") for market in markets.values())


def _market_url(event_id: str, page_param: str, slug: str) -> str:
    return f"{BASE}/match-odds/{event_id}/{page_param}/{slug}/bestOdds/?lang=en"


def fetch_market_responses(event_id: str, page_param: str, *,
                           referer: str | None = None) -> dict[str, dict | None]:
    """One comparison response per detail market tab, bounded and spaced.

    Each market costs exactly the request the page itself makes when that tab
    is clicked, and every handicap line of the market travels inside that one
    response — the collapsed per-line tables are client-side toggles. Tab
    requests take the wider spacing, stop at the run's request budget, and stop
    early when the lane is cooling down after repeated 429s. A market that
    answers with nothing is recorded as None, never as an empty market.
    """
    global _market_requests, _market_budget_stop
    markets: dict[str, dict | None] = {}
    if not MARKET_TABS_ENABLED:
        return markets
    for slug in DETAIL_MARKETS:
        if _be_cooling_down:
            break
        if _request_count >= _MAX_REQUESTS_PER_RUN:
            _market_budget_stop = True
            print(f"  betexplorer_odds: request budget reached "
                  f"({_MAX_REQUESTS_PER_RUN}); remaining markets skipped", file=sys.stderr)
            break
        _market_requests += 1
        try:
            payload = json.loads(_fetch(_market_url(event_id, page_param, slug),
                                        referer=referer, min_interval=_MARKET_INTERVAL))
        except BetExplorerCoolingDown:
            markets[slug] = None
            break
        except Exception as exc:  # noqa: BLE001 - one market never breaks the rest
            print(f"  betexplorer_odds: market {slug} unavailable: {exc}", file=sys.stderr)
            markets[slug] = None
            continue
        markets[slug] = parse_market_response(str(payload.get("odds") or ""))
    return markets


def _match_page_blocks(match_html: str, *, page_meta: dict | None = None) -> dict | None:
    """Bounded match-page text blocks plus the response digest, or None."""
    try:
        from edgefactory.sources.betexplorer_match_snapshot import parse_match_page_blocks
    except ImportError:  # pragma: no cover - the adapter stays usable standalone
        return None
    try:
        blocks = parse_match_page_blocks(match_html)
    except Exception:  # noqa: BLE001 - observation only; never break a capture
        return None
    meta = page_meta or {}
    blocks["page_sha256"] = meta.get("sha256")
    blocks["page_bytes"] = meta.get("response_bytes")
    lowered = match_html.lower()
    blocks["challenge"] = any(marker in lowered for marker in _CHALLENGE_MARKERS)
    return blocks


def fetch_match_odds_full(match_url: str, event_id: str) -> dict:
    """Fetch the match page and one comparison response per market.

    Two requests carry the priced lane: the match page (for ``page_param`` and
    the page's own blocks) and the 1x2 comparison response. The remaining
    market tabs (O/U, AH, DNB, DC, BTTS) each cost one more request — the same
    hop the page makes when the operator clicks that tab — spaced at the wider
    interval and bounded by the run's request budget. ``odds`` is the only
    field pricing reads; every market failure is contained to the detail.
    """
    out: dict = {"odds": None, "markets": {}, "page": None, "page_param": None}
    try:
        match_html = _fetch(match_url)
        if not match_html:
            return out
        out["page"] = _match_page_blocks(match_html, page_meta=dict(_LAST_RESPONSE_META))

        # Extract page_param for the odds response
        m = re.search(
            r"match_load_tabs\('\w+',\s*'1x2',\s*'[^']*',\s*'[^']*',\s*'([^']+)'",
            match_html,
        )
        page_param = m.group(1) if m else "1"
        out["page_param"] = page_param

        odds_url = f"{BASE}/match-odds/{event_id}/{page_param}/1x2/bestOdds/?lang=en"
        data = json.loads(_fetch(odds_url, referer=match_url))
        odds_html = data.get("odds", "")
        out["markets"] = {"1x2": parse_market_response(odds_html)}
        out["odds"] = parse_best_1x2(odds_html)
    except Exception as exc:
        print(f"  betexplorer_odds: failed to fetch odds for {match_url}: {exc}", file=sys.stderr)
    # Detail tabs only once the priced response proved the fixture answers,
    # and never at the cost of the priced lane.
    if out["page_param"] and (out["odds"] is not None or _market_rows_present(out["markets"])):
        try:
            out["markets"].update(
                fetch_market_responses(event_id, out["page_param"], referer=match_url))
        except Exception as exc:  # noqa: BLE001 - retention must never break a capture
            print(f"  betexplorer_odds: market tabs skipped: {exc}", file=sys.stderr)
    return out


def fetch_match_odds(match_url: str, event_id: str) -> dict | None:
    """Best 1x2 odds for a single match (unchanged contract).

    Returns {"odd1": float, "oddx": float, "odd2": float} or None, and leaves
    the retained detail — one comparison response per market and the match
    page's own blocks — in the module receipt ``LAST_MATCH_DETAIL`` for the
    same-day ledger.
    """
    global LAST_MATCH_DETAIL
    full = fetch_match_odds_full(match_url, event_id)
    markets = full.get("markets") or {}
    page = full.get("page") or {}
    if _market_rows_present(markets) or page.get("blocks") or page.get("challenge"):
        LAST_MATCH_DETAIL = {
            "markets": markets,
            "page": page or None,
            "page_param": full.get("page_param"),
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        LAST_MATCH_DETAIL = None
    return full.get("odds")


# --- bounded per-run state and same-day fixture cache ----------------------
_fetch_count: int = 0
_MAX_FETCHES_PER_RUN: int = 12


def _team_cache_key(name: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(name or "").lower())


def _fixture_cache_key(pick: dict, day: str) -> str:
    return "|".join((str(day)[:10], _team_cache_key(pick.get("home")),
                      _team_cache_key(pick.get("away"))))


def _cache_path(day: str) -> Path:
    return LOCALDATA / f"betexplorer_odds_cache_{str(day)[:10]}.json"


def _cache_fresh(stamp: object, *, now: float | None = None) -> bool:
    try:
        when = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        age = (now or datetime.now(timezone.utc).timestamp()) - when.timestamp()
        return 0.0 <= age <= CACHE_FRESHNESS_H * 3600.0
    except (TypeError, ValueError, OverflowError):
        return False


def _read_fixture_cache(pick: dict, day: str) -> list[dict] | None:
    """Read a fresh per-fixture cache entry; stale entries are ignored."""
    path = _cache_path(day)
    try:
        payload = json.loads(path.read_text())
        entry = (payload.get("fixtures") or {}).get(_fixture_cache_key(pick, day))
        if isinstance(entry, dict) and _cache_fresh(entry.get("cached_at")):
            rows = entry.get("rows")
            if isinstance(rows, list):
                return [dict(row) for row in rows if isinstance(row, dict)]
    except (OSError, ValueError, TypeError):
        pass
    return None


def _write_fixture_cache(pick: dict, day: str, rows: list[dict], *, detail: bool = False) -> None:
    """Atomically persist one same-day fixture result without synthetic rows."""
    path = _cache_path(day)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict = {"schema": 1, "date": str(day)[:10], "fixtures": {}}
        if path.exists():
            try:
                loaded = json.loads(path.read_text())
                if isinstance(loaded, dict) and isinstance(loaded.get("fixtures"), dict):
                    payload.update({k: loaded[k] for k in ("schema", "date") if k in loaded})
                    payload["fixtures"] = loaded["fixtures"]
            except (OSError, ValueError, TypeError):
                pass
        payload["fixtures"][_fixture_cache_key(pick, day)] = {
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "home": pick.get("home"),
            "away": pick.get("away"),
            "rows": rows,
            # True when a live visit ran under the detail tabs. Such an entry is
            # served from cache for the rest of the day; it is not re-visited.
            "detail": bool(detail),
        }
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
        tmp.replace(path)
    except OSError as exc:
        print(f"  betexplorer_odds: cache write skipped: {exc}", file=sys.stderr)


def cached_fixture_present(pick: dict, day: str) -> bool:
    """True when this fixture already has a cache entry for `day`.

    An EMPTY entry is a cached answer (a refusal, or a day with no odds on the
    page), not a miss — the caller must not re-request a fixture it already
    resolved. Distinguishing the two is what keeps the reordered enrichment loop
    byte-for-byte identical to the old short-circuit on empty entries.
    """
    return (_fixture_cache_key(pick, day) in _fixture_cache
            or _read_fixture_cache(pick, day) is not None)


def _match_detail_path(day: str) -> Path:
    return LOCALDATA / f"betexplorer_match_detail_{str(day)[:10]}.json"


def _market_block(market: object) -> dict | None:
    """One market's retained evidence, or None when the response held none."""
    if not isinstance(market, dict):
        return None
    rows = [row for row in (market.get("rows") or []) if isinstance(row, dict)]
    columns = [str(column) for column in (market.get("columns") or []) if column]
    if not rows and not columns:
        return None
    return {
        "columns": columns,
        "lines": [str(line) for line in (market.get("lines") or []) if line is not None],
        "rows": rows,
        "rows_count": len(rows),
        "named_rows": sum(1 for row in rows if row.get("bookmaker")),
        "bookmakers": sorted({str(row["bookmaker"]) for row in rows if row.get("bookmaker")}),
        "average": market.get("average"),
        "average_by_line": market.get("average_by_line") or None,
    }


def _persist_match_detail(pick: dict, day: str, matched: dict, detail: dict,
                          odds: dict | None) -> None:
    """Merge one fixture's retained detail into the same-day ledger.

    Evidence only, from the responses this fixture's fetch already holds: the
    match page's own blocks (H2H, last results, a bounded standings excerpt)
    and one comparison response per market — 1x2 and the detail tabs — each
    with its own column labels, handicap lines and bounded per-bookmaker
    rows. The match page's H2H list and league table are kept as the page
    served them (the "Show more matches" / "Show full table" controls are
    client-side toggles), not as their collapsed views. No raw HTML is stored,
    every list is capped, and nothing in this file is read by pricing, cards,
    or ML.
    """
    markets = detail.get("markets") or {}
    blocks: dict[str, dict] = {}
    failures: list[str] = []
    for slug, market in markets.items():
        block = _market_block(market)
        if block is None:
            failures.append(str(slug))
        else:
            blocks[str(slug)] = block
    page = detail.get("page") or {}
    page_block = None
    if page:
        page_block = {
            "page_sha256": page.get("page_sha256"),
            "page_bytes": page.get("page_bytes"),
            "challenge": bool(page.get("challenge")),
            "blocks": page.get("blocks", []),
            "h2h_meetings": page.get("h2h_meetings"),
            "h2h_record": page.get("h2h_record"),
            "h2h_rows": (page.get("h2h_rows") or [])[:_MAX_H2H_ROWS],
            "last_results_rows": (page.get("last_results_rows") or [])[:_MAX_LAST_RESULT_ROWS],
            "standings_columns": (page.get("standings_columns") or [])[:12],
            "standings_rows": (page.get("standings_rows") or [])[:_MAX_STANDINGS_ROWS],
            "standings_rows_count": len((page.get("standings_rows") or [])[:_MAX_STANDINGS_ROWS]),
        }
    entry = {
        "event_id": matched.get("event_id"),
        "match_url": matched.get("match_url"),
        "kickoff": matched.get("kickoff"),
        "data_dt": matched.get("data_dt"),
        "kickoff_date": matched.get("kickoff_date") or matched.get("date"),
        "home": matched.get("home"),
        "away": matched.get("away"),
        "league": f"{matched.get('country', '')}: {matched.get('league', '')}".strip(": "),
        "captured_at": detail.get("captured_at"),
        "page_param": detail.get("page_param"),
        "best_1x2": odds,
        "markets": blocks,
        "market_failures": sorted(failures),
        "page": page_block,
    }
    path = _match_detail_path(day)
    payload: dict = {"schema": 2, "date": str(day)[:10], "fixtures": {}}
    if path.exists():
        try:
            loaded = json.loads(path.read_text())
            if isinstance(loaded, dict) and isinstance(loaded.get("fixtures"), dict):
                payload["fixtures"] = loaded["fixtures"]
        except (OSError, ValueError, TypeError):
            pass
    payload["captured_at"] = datetime.now(timezone.utc).isoformat()
    payload["fixtures"][_fixture_cache_key(pick, day)] = entry
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
        tmp.replace(path)
    except OSError as exc:
        print(f"  betexplorer_odds: match detail write skipped: {exc}", file=sys.stderr)


def cached_odds_rows_for_pick(pick: dict, day: str) -> list[dict]:
    """Return only a fresh cached fixture, without making a network request.

    Identity-guarded: a cached row whose teams or date do not belong to this
    pick is dropped and censused rather than returned (2026-10-12 receipt — the
    "forge|yorkunited" key held Forge vs Inter Toronto rows).
    """
    global _be_cached
    key = _fixture_cache_key(pick, day)
    if key in _fixture_cache:
        _be_cached += 1
        rows = list(_fixture_cache[key])
    else:
        rows = _read_fixture_cache(pick, day)
        if rows is None:
            return []
        _fixture_cache[key] = list(rows)
        _be_cached += 1
    kept, rejected = filter_rows_for_pick(rows, pick, day)
    _record_row_rejections(rejected)
    return kept


def _team_pair_agreement(row: dict, pick: dict, *, norm_team_fn=None) -> tuple[bool, bool]:
    """Bind names AND squad markers in the same orientation at every seam."""
    rh, ra = row.get("home"), row.get("away")
    ph, pa = pick.get("home"), pick.get("away")
    straight = (team_names_agree(rh, ph, norm_team_fn=norm_team_fn)
                and team_names_agree(ra, pa, norm_team_fn=norm_team_fn))
    swapped = (team_names_agree(rh, pa, norm_team_fn=norm_team_fn)
               and team_names_agree(ra, ph, norm_team_fn=norm_team_fn))
    return straight, swapped


def _orientation_marker_clean_guard(matched: dict, pick: dict) -> bool:
    """The page must identify both clubs and their squads in ONE orientation.

    Retain the write-seam helper/interface, but a bag of matching marker
    classes alone is not proof of the corresponding club's squad identity.
    """
    straight, swapped = _team_pair_agreement(matched, pick)
    return straight != swapped


# ---------------------------------------------------------------------------
# Row-level fixture-identity guard (2026-10-12).
#
# Receipt: the committed 2026-10-12 odds cache held the key
# "2026-10-12|forge|yorkunited" (fixture home "Forge", away "York United") whose
# three rows are Forge vs INTER TORONTO 1.35/4.80/6.40 — a different match. The
# cache key is built from the PICK's teams, but the rows are built from the
# matched PAGE's teams. Historically a one-sided partial match let the wrong
# fixture's prices land under the right key: marker-only checks could not see
# that York United and Inter Toronto are simply different clubs.
#
# Matcher, pre-fetch/write seam and cached-row admission now share the same
# two-club, same-orientation relation. Raw rows still pass this guard even after
# a successful page match: cache metadata or a future matcher change must never
# stand in for the identity actually attached to the quoted prices. Observed
# display variants (Buriram / Buriram United, Arda / Arda Kardzhali) remain valid.
# ---------------------------------------------------------------------------
ROW_REJECT_TEAMS = "row teams do not both match the pick"
ROW_REJECT_DATE = "row date outside the pick's +/-1 day window"

# Shortest normalised form allowed to match by prefix containment. "Arda" for
# "Arda Kardzhali" is a real same-date receipt (2026-10-12, captured 01:06Z) and
# must survive; it is 4 characters, which is why the full-stem prefix relation
# accepts from 4 and not from the 5 the token-subset rule uses.
_TEAM_PREFIX_MIN = 4
# The fetch path deliberately searches the pick date and its neighbours for
# timezone offsets (Australian fixtures land on the previous UTC date), so a row
# dated within one day of the pick is in-window by construction.
_DATE_WINDOW_DAYS = 1


def _default_norm_team(name: object, width: int = 9) -> str:
    try:
        from edgefactory.util import norm_team as _norm
        return _norm(name, width=width)
    except Exception:
        return re.sub(r"[^a-z]", "", str(name or "").lower())[:width]


def team_names_agree(row_name: object, pick_name: object, *, norm_team_fn=None) -> bool:
    """Full-name equivalence with a hard squad veto, never a short-key proof.

    Preserve existing affix/subset and full-stem prefix relations (including
    Arda / Arda Kardzhali), but not nine-character collisions between clubs.
    """
    if squad_marker_mismatch(row_name, pick_name):
        return False  # Must precede EVERY alias, subset and fallback branch.
    row_words = club_initial_words_for_comparison(row_name)
    pick_words = club_initial_words_for_comparison(pick_name)
    if not row_words or not pick_words:
        return False
    if row_words == pick_words:
        return True
    # Conflicting club numbers are identity (B 1903 != B 1908, '31 != '32).
    # A feed may omit the year (observed Darmstadt / Darmstadt 98), so absence
    # alone is not a contradiction. Strip parsed squad markers first, so
    # reserve "2" remains compatible with "II"; the hard squad veto above
    # still refuses a numeric second side donating to the senior team.
    row_digits = re.findall(r"\d+", strip_squad_markers(row_words))
    pick_digits = re.findall(r"\d+", strip_squad_markers(pick_words))
    if row_digits and pick_digits and row_digits != pick_digits:
        return False
    try:
        from edgefactory.sources.theoddsapi import _team_names_match
        if _team_names_match(pick_words, row_words, allow_truncated=False):
            return True
    except Exception:
        pass
    # Use untruncated stems. Keep norm_team_fn as an interface argument only:
    # an injected short-key normalizer is not evidence of full-name identity.
    width = max(len(row_words), len(pick_words))
    na = _default_norm_team(pick_words, width=width)
    nb = _default_norm_team(row_words, width=width)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = sorted((str(na), str(nb)), key=len)
    return len(shorter) >= _TEAM_PREFIX_MIN and longer.startswith(shorter)


def _kickoff_agrees(row: dict, pick: dict) -> bool:
    """Kickoff agreement, judged ONLY when both sides are provable instants.

    BetExplorer rows carry a bare ``HH:MM`` kickoff, and bare times are
    region-relative in this pipeline (see picks_today's
    ``_REMOTE_CLOCK_REGION_HINTS`` / ``kickoff_clock_region_is_remote``): the
    same fixture legitimately reads "18:00" on the page and "13:00" on the pick
    row. Judging those would drop the same-day Ludogorets/Elfsborg rows this
    guard exists to protect, so an unprovable pair fails OPEN (never a
    rejection basis) exactly like ``_fresh_row`` in enh_pricing.
    """
    row_ko = str(row.get("kickoff_utc") or row.get("kickoff") or "")
    pick_ko = str(pick.get("kickoff_utc") or pick.get("kickoff") or "")
    if "T" not in row_ko or "T" not in pick_ko:
        return True
    try:
        r = datetime.fromisoformat(row_ko.replace("Z", "+00:00"))
        p = datetime.fromisoformat(pick_ko.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return True
    if r.tzinfo is None or p.tzinfo is None:
        return True
    return r == p


def row_belongs_to_pick(row: dict, pick: dict, day: str, *,
                        norm_team_fn=None) -> tuple[bool, str]:
    """(ok, reason) — may this row price this pick?

    Requires both teams to agree in one orientation (home/home + away/away, or
    the swapped orientation), the row's date to sit inside the pick's
    +/-1-day window, and — when both are provable instants — the kickoff to
    agree. ``reason`` is "" when the row is accepted.
    """
    straight, swapped = _team_pair_agreement(row, pick, norm_team_fn=norm_team_fn)
    if straight == swapped:
        return False, ROW_REJECT_TEAMS
    # `day` is a capture/cache partition; tomorrow's fixture may be collected
    # today. Anchor to the pick when supplied. Explicit invalid dates are not
    # missing evidence and cannot silently become a zero-day difference.
    reference = str(pick.get("date") or day)[:10]
    row_day = str(row.get("date") or "")[:10]
    try:
        pick_day = date.fromisoformat(reference) if reference else None
        observed_day = date.fromisoformat(row_day) if row_day else None
    except ValueError:
        return False, ROW_REJECT_DATE
    if observed_day and (pick_day is None or
                         abs((observed_day - pick_day).days) > _DATE_WINDOW_DAYS):
        return False, ROW_REJECT_DATE
    if not _kickoff_agrees(row, pick):
        return False, ROW_REJECT_DATE
    return True, ""


def filter_rows_for_pick(rows: list[dict], pick: dict, day: str, *,
                         norm_team_fn=None) -> tuple[list[dict], dict[str, int]]:
    """Keep only rows that belong to `pick`; return (kept, rejection census).

    The census is folded into ``run_stats()`` so a refused row is visible in the
    run receipt instead of vanishing.
    """
    kept: list[dict] = []
    rejected: dict[str, int] = {}
    for row in rows or []:
        try:
            ok, reason = row_belongs_to_pick(row, pick, day, norm_team_fn=norm_team_fn)
        except Exception:
            ok, reason = False, ROW_REJECT_TEAMS
        if ok:
            kept.append(row)
        else:
            rejected[reason] = rejected.get(reason, 0) + 1
    return kept, rejected


def _entry_detail_visited(pick: dict, day: str) -> bool:
    """True when this fixture's cache entry came from a visit under the detail tabs."""
    try:
        payload = json.loads(_cache_path(day).read_text())
        entry = (payload.get("fixtures") or {}).get(_fixture_cache_key(pick, day))
        return isinstance(entry, dict) and entry.get("detail") is True
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def _detail_refetch_due(pick: dict, day: str) -> bool:
    """A priced cache entry written before its match detail was retained.

    Cache hits return before the match page is fetched, so a price cached by an
    earlier run (before the detail tabs existed) never gets its O/U, BTTS or DC
    tabs retained. Such an entry gets one re-read; entries written by a visit
    under the detail tabs are served from cache, which keeps the one-visit-per-
    fixture-per-day bound. Only identity-valid priced entries qualify: empty
    or poisoned entries cannot buy another network attempt. A re-read is attempted at most once per run.
    """
    if not MARKET_TABS_ENABLED:
        return False
    key = _fixture_cache_key(pick, day)
    if key in _detail_attempted:
        return False
    rows = _fixture_cache[key] if key in _fixture_cache else _read_fixture_cache(pick, day)
    if not rows or not filter_rows_for_pick(rows, pick, day)[0]:
        return False
    return not _entry_detail_visited(pick, day)


def fixture_capture_needed(pick: dict, day: str) -> bool:
    """Whether this fixture needs a bounded network slot rather than a free read.

    Fresh negative answers are cached too. Priced legacy entries may still
    need their existing one-time detail visit; this does not bypass cooldown,
    freshness, identity validation or either network budget.
    """
    return not cached_fixture_present(pick, day) or _detail_refetch_due(pick, day)


def _refetch_for_detail(pick: dict, day: str, *, norm_team_fn=None) -> list[dict]:
    """Re-read a cached priced fixture so its match detail is retained.

    The cached price is the fallback: if the live re-read yields nothing (a
    failed request, budget stop, or a refusal), the prior cache entry is restored
    rather than overwritten with an empty answer.
    """
    key = _fixture_cache_key(pick, day)
    _detail_attempted.add(key)
    prior = list(_fixture_cache[key]) if key in _fixture_cache else (
        _read_fixture_cache(pick, day) or [])
    rows = betexplorer_odds_rows_for_pick(
        pick, day, norm_team_fn=norm_team_fn, refresh_detail=True)
    if rows:
        return rows
    _fixture_cache[key] = list(prior)
    _write_fixture_cache(pick, day, prior)
    return cached_odds_rows_for_pick(pick, day)


def betexplorer_odds_rows_for_pick(
    pick: dict,
    day: str,
    *,
    norm_team_fn=None,
    refresh_detail: bool = False,
) -> list[dict]:
    """Fetch BetExplorer odds for a single unmatched pick.

    Searches the pick date, the day before, and the day after (to handle
    timezone offsets where Australian matches appear on the previous
    UTC date on BetExplorer).

    Returns a list of odds rows in the standard format:
      {date, kickoff, league, home, away, market, selection, odds,
       bookmaker, captured_at}
    """
    global _fetch_count, LAST_MATCH_DETAIL
    # A detail re-read (refresh_detail) is bounded by the day's priced cache
    # entries and by the request budget, not by the fixture budget: the cache
    # check below returns nothing once that budget is spent, so letting re-reads
    # use it would blank the prices of fixtures not yet read.
    if _be_cooling_down or (_fetch_count >= _MAX_FETCHES_PER_RUN and not refresh_detail):
        return []

    # Cached rows take the SAME identity-guarded, network-free reader the
    # caller's cache seam uses — one code path for cached rows, so a poisoned
    # key cannot price a pick through this door either.
    cache_key = _fixture_cache_key(pick, day)
    if not refresh_detail and (
            cache_key in _fixture_cache or _read_fixture_cache(pick, day) is not None):
        if _detail_refetch_due(pick, day):
            return _refetch_for_detail(pick, day, norm_team_fn=norm_team_fn)
        return cached_odds_rows_for_pick(pick, day)

    # Search adjacent dates for the match (timezone offset)
    pick_date = str(pick.get("date") or day)[:10]
    try:
        pd = date.fromisoformat(pick_date)
        search_dates = [
            (pd - timedelta(days=1)).isoformat(),
            pd.isoformat(),
            (pd + timedelta(days=1)).isoformat(),
        ]
    except ValueError:
        search_dates = [pick_date]

    if norm_team_fn is None:
        try:
            from edgefactory.util import norm_team as _norm
            norm_team_fn = _norm
        except ImportError:
            norm_team_fn = lambda n, width=9: re.sub(r"[^a-z]", "", str(n or "").lower())[:width]

    matched = None
    for d in search_dates:
        matches = fetch_day_matches(d)
        m = match_pick_to_betexplorer(pick, matches, norm_team_fn=norm_team_fn)
        if m is not None:
            matched = m
            break

    if matched is None:
        _fixture_cache[cache_key] = []
        _write_fixture_cache(pick, day, [])
        return []

    # Second, write-seam identity check (defense in depth against future
    # matcher changes and caller-supplied norm functions): the matched page's
    # both team names and their squad markers must agree with the pick in
    # ONE orientation. Comparisons deliberately allow display variants
    # ("Buriram" vs "Buriram United") and reject squad swaps ("Club Brugge KV
    # U23" for "Club Brugge KV"). A refusal here must never write rows under
    # the pick's key: wrong-fixture prices are worse than an absent cache.
    if not _orientation_marker_clean_guard(matched, pick):
        print(
            f"  betexplorer_odds: refused matched page "
            f"{matched.get('home')} vs {matched.get('away')} for pick "
            f"{pick.get('home')} vs {pick.get('away')}: team/squad identity mismatch; "
            f"no rows cached",
            file=sys.stderr,
        )
        _fixture_cache[cache_key] = []
        _write_fixture_cache(pick, day, [])
        return []

    # Defense in depth against a future matcher regression: validate observed
    # schedule BEFORE fetching/persisting any detail under the pick's key.
    page_ok, reason = row_belongs_to_pick(matched, pick, day, norm_team_fn=norm_team_fn)
    if not page_ok:
        _record_row_rejections({reason: 1})
        _fixture_cache[cache_key] = []
        _write_fixture_cache(pick, day, [])
        return []

    # Clear the receipt before the fetch so a stub, a cache path, or a failed
    # request can never leave a previous fixture's detail behind.
    LAST_MATCH_DETAIL = None
    odds = fetch_match_odds(matched["match_url"], matched["event_id"])
    detail = LAST_MATCH_DETAIL
    if detail is not None:
        try:
            _persist_match_detail(pick, day, matched, detail, odds)
        except Exception as exc:  # noqa: BLE001 - retention must never break a capture
            print(f"  betexplorer_odds: match detail skipped: {exc}", file=sys.stderr)
    if odds is None:
        _fixture_cache[cache_key] = []
        _write_fixture_cache(pick, day, [])
        return []

    if not refresh_detail:
        _fetch_count += 1
    captured_at = datetime.now(timezone.utc).isoformat()

    base = {
        "date": matched.get("date") or pick_date,
        "kickoff": matched["kickoff"],
        "league": f"{matched.get('country', '')}: {matched.get('league', '')}",
        "home": matched["home"],
        "away": matched["away"],
        "bookmaker": "betexplorer_best",
        "captured_at": captured_at,
    }
    if matched.get("kickoff_utc"):
        base["kickoff_utc"] = matched["kickoff_utc"]

    rows = []
    for market, mapping in (
        ("1x2", {"home": "odd1", "draw": "oddx", "away": "odd2"}),
    ):
        for selection, col in mapping.items():
            v = odds.get(col)
            if v is not None:
                rows.append({**base, "market": market, "selection": selection, "odds": v})

    # Final identity gate before these rows are cached or returned: the matcher
    # may have accepted a one-sided partial match, and the rows carry the PAGE's
    # teams. Refuse rather than persist a wrong-fixture price (2026-10-12 Forge
    # vs York United receipt).
    rows, rejected = filter_rows_for_pick(rows, pick, day, norm_team_fn=norm_team_fn)
    if rejected:
        _record_row_rejections(rejected)
        print(
            f"  betexplorer_odds: refused {sum(rejected.values())} row(s) for "
            f"{pick.get('home')} vs {pick.get('away')}: "
            f"{', '.join(f'{v}x {k}' for k, v in sorted(rejected.items()))}",
            file=sys.stderr,
        )

    _fixture_cache[cache_key] = list(rows)
    _write_fixture_cache(pick, day, rows, detail=True)
    return rows


def reset_fetch_count():
    """Reset all run-scoped state before one enrichment run."""
    global _fetch_count, _last_request_time, _be_429, _be_cooling_down, _be_cached, _LAST_RESPONSE_BYTES, LAST_MATCH_DETAIL
    global _request_count, _market_requests, _market_budget_stop
    _fetch_count = 0
    _detail_attempted.clear()
    _last_request_time = 0.0
    _be_429 = 0
    _be_cooling_down = False
    _be_cached = 0
    _be_rows_rejected.clear()
    _request_count = 0
    _market_requests = 0
    _market_budget_stop = False
    _LAST_RESPONSE_BYTES = b""
    LAST_MATCH_DETAIL = None
    _match_cache.clear()
    _fixture_cache.clear()
