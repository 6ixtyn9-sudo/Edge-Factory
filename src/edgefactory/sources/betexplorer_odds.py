"""BetExplorer live odds adapter — niche-league coverage for unmatched picks.

Fetches 1x2 odds from BetExplorer for matches that bzzoiro_odds and
scoutingstats_odds don't cover (Australian NPL, Belarus, Latvia, Kuwait,
Tanzania, etc.).

Usage pattern:
  1. fetch_day_matches(date) → list of all matches for that date
  2. match_pick_to_betexplorer(pick, matches) → matched match dict or None
  3. fetch_match_odds(match_url, event_id) → {odd1, oddx, odd2} or None

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

from edgefactory.identity import squad_marker_mismatch

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

BETEXPLORER_ODDS_SOURCE = "betexplorer_odds"
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))
CACHE_FRESHNESS_H = float(os.environ.get("EDGE_FACTORY_BE_CACHE_FRESHNESS_H", "24"))

# Per-run health/thermal state. It is deliberately reset only by
# reset_fetch_count(), which the picks enrichment calls once per run.
_be_429 = 0
_be_cooling_down = False
_be_cached = 0

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
    }


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


def _throttle():
    """Enforce minimum interval between requests."""
    global _last_request_time
    elapsed = time.monotonic() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def _fetch(url: str, referer: str | None = None, retries: int = 3, timeout: int = 20) -> str:
    """Fetch one URL, single-flight, with respectful 429 handling.

    The first 429 sleeps for a default 30 seconds and a second retry sleeps
    for 60 seconds. An explicit Retry-After header wins (including values over
    60 seconds). The second 429 trips run-scoped cooling and raises before any
    third request can be attempted.
    """
    global _be_429, _be_cooling_down, _LAST_RESPONSE_META, _LAST_RESPONSE_BYTES
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    with _request_lock:
        _LAST_RESPONSE_BYTES = b""
        _LAST_RESPONSE_META = {"url": url, "http_status": None, "response_bytes": 0, "sha256": None}
        for attempt in range(retries):
            if _be_cooling_down:
                raise BetExplorerCoolingDown("betexplorer_odds: run cooling down after 2 HTTP 429 responses")
            _throttle()
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
        dd, mm, yyyy, hh, minute = [int(x) for x in dt.groups()]
        event_id = link.group(1).rstrip("/").split("/")[-1]
        rel_url = html.unescape(link.group(1))
        full_url = rel_url if rel_url.startswith("http") else BASE + rel_url
        out.append({
            "date": f"{yyyy:04d}-{mm:02d}-{dd:02d}",
            "kickoff": f"{hh:02d}:{minute:02d}",
            "country": current_country,
            "league": current_league,
            "home": home,
            "away": away,
            "hs": score.group(1) if score else "",
            "gs": score.group(2) if score else "",
            "ht_hs": "",
            "ht_gs": "",
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
    """Find the BetExplorer match corresponding to a pick.

    Uses norm_team() keys at the given width for fuzzy matching.
    Returns the match dict or None if no unique match found.
    """
    if norm_team_fn is None:
        try:
            from edgefactory.util import norm_team as _norm
            norm_team_fn = _norm
        except ImportError:
            norm_team_fn = lambda n, width=9: re.sub(r"[^a-z]", "", str(n or "").lower())[:width]

    pick_home = str(pick.get("home") or "")
    pick_away = str(pick.get("away") or "")
    pick_league = str(pick.get("league") or "")

    pick_hk = norm_team_fn(pick_home, width=norm_width)
    pick_ak = norm_team_fn(pick_away, width=norm_width)

    candidates = []
    for m in matches:
        m_hk = norm_team_fn(m.get("home", ""), width=norm_width)
        m_ak = norm_team_fn(m.get("away", ""), width=norm_width)

        # Squad-marker veto BEFORE any branch can accept: wherever a
        # truncated fuzzy key treats a provider name as one of the pick's
        # teams, the full names must carry the same squad markers. Without
        # this, "Club Brugge KV U23" shares the width-9 key of "Club Brugge
        # KV" and the reserve side's page gets priced as the senior side
        # (receipt 2026-10-10: Dender vs Club Brugge KV U23 rows cached under the
        # RAAL La Louvière vs Club Brugge KV key).
        if m_hk == pick_hk and squad_marker_mismatch(m.get("home", ""), pick_home):
            continue
        if m_hk == pick_ak and squad_marker_mismatch(m.get("home", ""), pick_away):
            continue
        if m_ak == pick_hk and squad_marker_mismatch(m.get("away", ""), pick_home):
            continue
        if m_ak == pick_ak and squad_marker_mismatch(m.get("away", ""), pick_away):
            continue

        # Exact team-key match (both sides)
        if m_hk == pick_hk and m_ak == pick_ak:
            candidates.append((0, m))
        # Reverse match (home/away swapped)
        elif m_hk == pick_ak and m_ak == pick_hk:
            candidates.append((1, m))
        # Partial match (one side matches)
        elif m_hk == pick_hk or m_ak == pick_ak:
            candidates.append((2, m))

    if not candidates:
        return None

    # Prefer exact, then partial. Among ties, prefer same league.
    def sort_key(item):
        priority, m = item
        m_league = str(m.get("league", "") or m.get("country", "") or "").lower()
        league_match = 0 if pick_league.lower() in m_league or m_league in pick_league.lower() else 1
        return (priority, league_match)

    candidates.sort(key=sort_key)

    # Only return if best candidate is exact or reversed
    if candidates[0][0] <= 1:
        return candidates[0][1]
    # Partial match: only accept if there's exactly one candidate
    partials = [c for c in candidates if c[0] == 2]
    if len(partials) == 1:
        return partials[0][1]
    return None


def fetch_match_odds(match_url: str, event_id: str) -> dict | None:
    """Fetch best 1x2 odds for a single match from BetExplorer.

    Returns {"odd1": float, "oddx": float, "odd2": float} or None.
    """
    try:
        match_html = _fetch(match_url)
        if not match_html:
            return None

        # Extract page_param for odds API
        m = re.search(
            r"match_load_tabs\('\w+',\s*'1x2',\s*'[^']*',\s*'[^']*',\s*'([^']+)'",
            match_html,
        )
        page_param = m.group(1) if m else "1"

        odds_url = f"{BASE}/match-odds/{event_id}/{page_param}/1x2/bestOdds/?lang=en"
        data = json.loads(_fetch(odds_url, referer=match_url))
        odds_html = data.get("odds", "")

        # Parse best odds from the first tbody
        block = re.search(r'<tbody id="best-odds-0">(.*?)</tbody>', odds_html, re.S)
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
    except Exception as exc:
        print(f"  betexplorer_odds: failed to fetch odds for {match_url}: {exc}", file=sys.stderr)
        return None


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


def _write_fixture_cache(pick: dict, day: str, rows: list[dict]) -> None:
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
        }
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
        tmp.replace(path)
    except OSError as exc:
        print(f"  betexplorer_odds: cache write skipped: {exc}", file=sys.stderr)


def cached_odds_rows_for_pick(pick: dict, day: str) -> list[dict]:
    """Return only a fresh cached fixture, without making a network request."""
    global _be_cached
    key = _fixture_cache_key(pick, day)
    if key in _fixture_cache:
        _be_cached += 1
        return list(_fixture_cache[key])
    rows = _read_fixture_cache(pick, day)
    if rows is None:
        return []
    _fixture_cache[key] = list(rows)
    _be_cached += 1
    return list(rows)


def _orientation_marker_clean_guard(matched: dict, pick: dict) -> bool:
    """True when the matched page can stand for the pick in either orientation.

    Module-level so the write-seam refusal is unit-testable without network.
    """
    matched_home = str(matched.get("home") or "")
    matched_away = str(matched.get("away") or "")
    pick_home = str(pick.get("home") or "")
    pick_away = str(pick.get("away") or "")
    return (not squad_marker_mismatch(matched_home, pick_home)
            and not squad_marker_mismatch(matched_away, pick_away)) or \
           (not squad_marker_mismatch(matched_home, pick_away)
            and not squad_marker_mismatch(matched_away, pick_home))


def betexplorer_odds_rows_for_pick(
    pick: dict,
    day: str,
    *,
    norm_team_fn=None,
) -> list[dict]:
    """Fetch BetExplorer odds for a single unmatched pick.

    Searches the pick date, the day before, and the day after (to handle
    timezone offsets where Australian matches appear on the previous
    UTC date on BetExplorer).

    Returns a list of odds rows in the standard format:
      {date, kickoff, league, home, away, market, selection, odds,
       bookmaker, captured_at}
    """
    global _fetch_count
    if _be_cooling_down or _fetch_count >= _MAX_FETCHES_PER_RUN:
        return []

    cache_key = _fixture_cache_key(pick, day)
    if cache_key in _fixture_cache:
        global _be_cached
        _be_cached += 1
        return list(_fixture_cache[cache_key])
    cached = _read_fixture_cache(pick, day)
    if cached is not None:
        _fixture_cache[cache_key] = list(cached)
        _be_cached += 1
        return list(cached)

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
    # team names must not carry squad markers the pick's names lack, in
    # EITHER orientation. Marker classes deliberately allow display variants
    # ("Buriram" vs "Buriram United") and reject squad swaps ("Club Brugge KV
    # U23" for "Club Brugge KV"). A refusal here must never write rows under
    # the pick's key: wrong-fixture prices are worse than an absent cache.
    if not _orientation_marker_clean_guard(matched, pick):
        print(
            f"  betexplorer_odds: refused matched page "
            f"{matched.get('home')} vs {matched.get('away')} for pick "
            f"{pick.get('home')} vs {pick.get('away')}: squad-marker mismatch; "
            f"no rows cached",
            file=sys.stderr,
        )
        _fixture_cache[cache_key] = []
        _write_fixture_cache(pick, day, [])
        return []

    odds = fetch_match_odds(matched["match_url"], matched["event_id"])
    if odds is None:
        _fixture_cache[cache_key] = []
        _write_fixture_cache(pick, day, [])
        return []

    _fetch_count += 1
    captured_at = datetime.now(timezone.utc).isoformat()

    base = {
        "date": pick_date,
        "kickoff": matched["kickoff"],
        "league": f"{matched.get('country', '')}: {matched.get('league', '')}",
        "home": matched["home"],
        "away": matched["away"],
        "bookmaker": "betexplorer_best",
        "captured_at": captured_at,
    }

    rows = []
    for market, mapping in (
        ("1x2", {"home": "odd1", "draw": "oddx", "away": "odd2"}),
    ):
        for selection, col in mapping.items():
            v = odds.get(col)
            if v is not None:
                rows.append({**base, "market": market, "selection": selection, "odds": v})

    _fixture_cache[cache_key] = list(rows)
    _write_fixture_cache(pick, day, rows)
    return rows


def reset_fetch_count():
    """Reset all run-scoped state before one enrichment run."""
    global _fetch_count, _last_request_time, _be_429, _be_cooling_down, _be_cached, _LAST_RESPONSE_BYTES
    _fetch_count = 0
    _last_request_time = 0.0
    _be_429 = 0
    _be_cooling_down = False
    _be_cached = 0
    _LAST_RESPONSE_BYTES = b""
    _match_cache.clear()
    _fixture_cache.clear()
