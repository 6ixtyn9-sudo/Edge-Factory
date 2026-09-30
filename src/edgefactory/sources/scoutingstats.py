"""ScoutingStats.ai adapter — hidden JSON API, ML model with probs AND odds.

Endpoints:
  https://scoutingstats.ai/api/fixtures/YYYY-MM-DD      (finished/live/upcoming)
  https://scoutingstats.ai/api/odds?fixture_ids=1,2,3   (probs + odds, many markets)

History: thin before ~mid-2025 (11 matches on 2024-06-10, 52 on 2025-06-10,
164 on 2026-01-10) -> treat as capture-forward with shallow backfill.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request

from edgefactory.sources import public_relay

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
    "Accept": "application/json",
}
BASE = "https://scoutingstats.ai/api"
RELAY_BASE = "https://r.jina.ai/"
RELAY_MARKER = "Markdown Content:\n"


def _decode_json(raw: bytes | str):
    text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
    return json.loads(text)


def _direct_json(url: str):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return _decode_json(response.read())


def _relay_json(url: str):
    """Read a public API response through Jina, validating exact provenance.

    ScoutingStats abruptly closes TLS from GitHub-hosted runners, while Jina's
    public reader can still retrieve both API endpoints.  No credentials are
    involved.  Exact URL and wrapper checks prevent a relay error/challenge
    page from becoming source data.
    """
    req = urllib.request.Request(
        RELAY_BASE + url,
        headers={"User-Agent": "EdgeFactory/1.0", "Accept": "text/plain", "X-No-Cache": "true"},
    )
    with urllib.request.urlopen(req, timeout=35) as response:
        text = response.read().decode("utf-8", "replace")
    if text.count(RELAY_MARKER) != 1:
        raise ValueError("unexpected ScoutingStats relay wrapper")
    header, body = text.split(RELAY_MARKER, 1)
    source_lines = [line.removeprefix("URL Source: ").strip() for line in header.splitlines()
                    if line.startswith("URL Source: ")]
    if source_lines != [url]:
        raise ValueError("ScoutingStats relay source URL mismatch")
    return _decode_json(body.strip())


def _get_json(url: str, retries: int = 3):
    errors = []
    # Direct remains first for local/residential operation.  In Actions the
    # known-broken TLS route is skipped, avoiding three 30-second stalls.
    actions = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    transports = [] if actions else [_direct_json]

    # Prefer operator-owned relays in Actions. Cloudflare and Apps Script are
    # independently deployed and tried in configured order.
    for relay_name, raw in public_relay.fetches(url):
        try:
            return _decode_json(raw)
        except Exception as exc:  # noqa: BLE001 - try the next transport
            errors.append(f"operator:{relay_name}={type(exc).__name__}")

    transports.append(_relay_json)
    for request in transports:
        for attempt in range(retries):
            try:
                return request(url)
            except Exception as exc:  # noqa: BLE001 - move to retry/next transport
                errors.append(f"{request.__name__}={type(exc).__name__}")
                if attempt + 1 < retries:
                    time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"ScoutingStats fetch failed: {', '.join(errors)}")


def fetch_day(date: str) -> list[dict]:
    data = _get_json(f"{BASE}/fixtures/{date}")
    if not isinstance(data, dict):
        return []
    fixtures = []
    for status in ("finished", "live", "upcoming"):
        for league, matches in (data.get(status) or {}).items():
            for m in matches:
                fixtures.append((status, league, m))
    if not fixtures:
        return []

    # odds+probs in batches of 50
    odds_map: dict = {}
    ids = [str(m["fixture_id"]) for _, _, m in fixtures]
    for i in range(0, len(ids), 50):
        chunk = ids[i : i + 50]
        try:
            od = _get_json(f"{BASE}/odds?fixture_ids={','.join(chunk)}")
            odds_map.update((od or {}).get("odds", {}))
        except Exception:
            pass

    out = []
    for status, league, m in fixtures:
        fid = str(m["fixture_id"])
        o = odds_map.get(fid, {})
        out.append(
            {
                "date": date,
                "kickoff": m.get("starting_at"),
                "league": m.get("league_name") or league,
                "country": m.get("country_name"),
                "home": m.get("home_team_name"),
                "away": m.get("away_team_name"),
                "hs": m.get("home_score") if m.get("is_finished") else None,
                "gs": m.get("away_score") if m.get("is_finished") else None,
                "status": m.get("status_text"),
                # model probabilities (0-100)
                "p1": o.get("home_prob"),
                "px": o.get("draw_prob"),
                "p2": o.get("away_prob"),
                "p_o15": o.get("over_15_prob"),
                "p_o25": o.get("over_25_prob"),
                "p_o35": o.get("over_35_prob"),
                "p_gg": o.get("btts_yes_prob"),
                "p_ng": o.get("btts_no_prob"),
                # bookmaker odds
                "odd1": o.get("home_odds"),
                "oddx": o.get("draw_odds"),
                "odd2": o.get("away_odds"),
                "odd_o15": o.get("1.5_over"),
                "odd_u15": o.get("1.5_under"),
                "odd_o25": o.get("2.5_over"),
                "odd_u25": o.get("2.5_under"),
                "odd_o35": o.get("3.5_over"),
                "odd_u35": o.get("3.5_under"),
                "odd_gg": o.get("btts_yes_odds"),
                "odd_ng": o.get("btts_no_odds"),
            }
        )
    return out


COLUMNS = [
    "date", "kickoff", "league", "country", "home", "away", "hs", "gs", "status",
    "p1", "px", "p2", "p_o15", "p_o25", "p_o35", "p_gg", "p_ng",
    "odd1", "oddx", "odd2", "odd_o15", "odd_u15", "odd_o25", "odd_u25",
    "odd_o35", "odd_u35", "odd_gg", "odd_ng",
]
