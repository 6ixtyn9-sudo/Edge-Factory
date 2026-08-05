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

import html
import json
import math
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

BASE = "https://www.betexplorer.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

# Minimum seconds between consecutive requests to BetExplorer
_MIN_INTERVAL = 3.0
_last_request_time: float = 0.0

# In-memory cache for the daily match-list page (fetched once per date per run)
_match_cache: dict[str, list[dict]] = {}

BETEXPLORER_ODDS_SOURCE = "betexplorer_odds"


def _throttle():
    """Enforce minimum interval between requests."""
    global _last_request_time
    elapsed = time.monotonic() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_request_time = time.monotonic()


def _fetch(url: str, referer: str | None = None, retries: int = 3, timeout: int = 20) -> str:
    """Fetch a URL with throttling and retry on 429."""
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    for attempt in range(retries):
        _throttle()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                wait = 10.0 * (attempt + 1)
                print(f"  betexplorer_odds: 429 rate limit, waiting {wait:.0f}s (attempt {attempt+1}/{retries})", file=sys.stderr)
                time.sleep(wait)
                continue
            if exc.code == 404:
                return ""
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
            "match_url": full_url,
            "event_id": event_id,
        })
    return out


def fetch_day_matches(day: str) -> list[dict]:
    """Fetch and parse all matches for a given date from BetExplorer.

    Results are cached in-memory so multiple calls for the same date
    only hit BetExplorer once.
    """
    if day in _match_cache:
        return _match_cache[day]
    y, m, d = day.split("-")
    url = f"{BASE}/football/results/?year={y}&month={m}&day={d}"
    try:
        page = _fetch(url)
        matches = parse_results_page(page)
        _match_cache[day] = matches
        return matches
    except Exception as exc:
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


# --- per-run state ----------------------------------------------------------
_fetch_count: int = 0
_MAX_FETCHES_PER_RUN: int = 12


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
    if _fetch_count >= _MAX_FETCHES_PER_RUN:
        return []

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
        return []

    odds = fetch_match_odds(matched["match_url"], matched["event_id"])
    if odds is None:
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

    return rows


def reset_fetch_count():
    """Reset the fetch counter and match cache (call at the start of each pipeline run)."""
    global _fetch_count
    _fetch_count = 0
    _match_cache.clear()
