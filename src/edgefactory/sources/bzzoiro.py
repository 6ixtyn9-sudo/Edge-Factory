"""bzzoiro adapter — real ML model API (CatBoost, xG), source #12.

Auth: Authorization: Token <key>   (Bearer/X-API-Key DO NOT work)

Endpoint: /api/v2/predictions/ — paginated, ~490 upcoming predictions at a
time, published up to ~7 weeks ahead. Capture-forward: snapshot ALL upcoming
daily; settle later via /api/v2/events/?event_id= (scores) or forebet join.

fetch_day(date) returns predictions whose event_date == date, but the daily
capture job should call fetch_all() once and bucket rows by event day.
"""

from __future__ import annotations
import json
import os
import time
import urllib.request

TOKEN = os.environ.get("BZZOIRO_TOKEN")
BASE = "https://sports.bzzoiro.com/api/v2"

def _get(url: str, retries: int = 3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"Authorization": f"Token {TOKEN}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))

def _row(p: dict) -> dict:
    ev = p.get("event", {})
    mk = p.get("markets", {})
    mr = mk.get("match_result", {})
    ou = mk.get("over_under", {})
    xg = mk.get("expected_goals", {})
    rec = p.get("recommendations", {})
    model = p.get("model", {})

    return {
        "date": (ev.get("event_date") or "")[:10],
        "kickoff": ev.get("event_date"),
        "captured_at": p.get("created_at"),
        "league": ev.get("league_name"),
        "home": ev.get("home_team"),
        "away": ev.get("away_team"),
        "event_id": ev.get("id"),
        "p1": mr.get("prob_home"),
        "px": mr.get("prob_draw"),
        "p2": mr.get("prob_away"),
        "predicted": mr.get("predicted"),
        "xg_home": xg.get("home"),
        "xg_away": xg.get("away"),
        "p_o15": ou.get("prob_over_15"),
        "p_o25": ou.get("prob_over_25"),
        "p_o35": ou.get("prob_over_35"),
        "p_gg": (mk.get("btts") or {}).get("prob_yes"),
        "pred_score": (mk.get("score") or {}).get("most_likely"),
        "rec_bet_favorite": rec.get("bet_favorite"),
        "rec_winner": rec.get("winner"),
        "confidence": model.get("confidence"),
        "model_version": model.get("version"),
    }

def fetch_all() -> list[dict]:
    """Pull every available prediction (paginated)."""
    out, url = [], f"{BASE}/predictions/?limit=50"
    while url:
        d = _get(url)
        out.extend(_row(p) for p in d.get("results", []))
        url = d.get("next")
    return out

def fetch_day(date: str) -> list[dict]:
    """Snapshot-day semantics: on 'today', capture EVERYTHING upcoming
    (rows keep their own event date); other dates return []."""
    from datetime import date as _d
    if date != _d.today().isoformat():
        return []
    return fetch_all()

COLUMNS = ["date", "kickoff", "captured_at", "league", "home", "away",
           "event_id", "p1", "px", "p2", "predicted", "xg_home", "xg_away",
           "p_o15", "p_o25", "p_o35", "p_gg", "pred_score",
           "rec_bet_favorite", "rec_winner", "confidence", "model_version"]
