"""
scoutingstats.py — ScoutingStats.ai adapter (ML model, JSON API).
  /api/fixtures/<YYYY-MM-DD>      -> finished/live/upcoming by league
  /api/odds?fixture_ids=1,2,3     -> model probs + odds for many markets
Markets: 1x2, btts, ou_1.5, ou_2.5, ou_3.5 (probs AND odds).
"""
from datetime import date, datetime, timezone

from ..models import (NormalizedEvent, NormalizedOdds, NormalizedPrediction,
                      NormalizedResult)
from .base import SourceAdapter

BASE = "https://scoutingstats.ai"
ODDS_BATCH = 40


class ScoutingStatsSource(SourceAdapter):
    source_key = "scoutingstats"
    sport = "soccer"
    min_delay = 0.6

    def fetch_day(self, day: date) -> dict:
        fx = self.get(f"{BASE}/api/fixtures/{day.isoformat()}",
                      headers={"Accept": "application/json"}).json()
        fixtures = []
        for section in ("finished", "live", "upcoming"):
            for league, matches in (fx.get(section) or {}).items():
                for m in matches:
                    m["_section"] = section
                    fixtures.append(m)
        ids = [str(m["fixture_id"]) for m in fixtures]
        odds = {}
        for i in range(0, len(ids), ODDS_BATCH):
            batch = ",".join(ids[i:i + ODDS_BATCH])
            try:
                resp = self.get(f"{BASE}/api/odds?fixture_ids={batch}",
                                headers={"Accept": "application/json"}).json()
                odds.update(resp.get("odds") or {})
            except Exception:
                continue
        return {"fixtures": fixtures, "odds": odds}

    def normalize(self, raw: dict, day: date) -> list[NormalizedEvent]:
        events = []
        for m in raw["fixtures"]:
            fid = str(m["fixture_id"])
            o = raw["odds"].get(fid) or {}
            if not o:
                continue

            start = None
            for key in ("starting_at", "start_time", "kickoff"):
                if m.get(key):
                    try:
                        start = datetime.fromisoformat(
                            str(m[key]).replace("Z", "+00:00"))
                        if start.tzinfo is None:
                            start = start.replace(tzinfo=timezone.utc)
                    except ValueError:
                        pass
                    break
            if start is None:
                start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)

            preds, odds = [], []

            def add(market, sel, prob_key, odd_key):
                p = o.get(prob_key)
                if p is not None:
                    preds.append(NormalizedPrediction(market, sel, float(p) / 100))
                d = o.get(odd_key)
                if d:
                    odds.append(NormalizedOdds(market, sel, float(d)))

            add("1x2", "home", "home_prob", "home_odds")
            add("1x2", "draw", "draw_prob", "draw_odds")
            add("1x2", "away", "away_prob", "away_odds")
            add("btts", "yes", "btts_yes_prob", "btts_yes_odds")
            add("btts", "no", "btts_no_prob", "btts_no_odds")
            for line in ("1.5", "2.5", "3.5"):
                lk = line.replace(".", "")
                add(f"ou_{line}", "over", f"over_{lk}_prob", f"{line}_over")
                add(f"ou_{line}", "under", f"under_{lk}_prob", f"{line}_under")

            result = None
            if m.get("is_finished"):
                fh, fa = m.get("home_score"), m.get("away_score")
                if fh is not None and fa is not None:
                    result = NormalizedResult(float(fh), float(fa),
                                              {"ft": [fh, fa]})

            events.append(NormalizedEvent(
                source_ref=fid, sport=self.sport,
                competition_name=m.get("league_name", ""),
                competition_ref=str(m.get("league_id", "")),
                country=m.get("country_name", ""),
                home_name=m.get("home_team_name", ""),
                home_ref=str(m.get("home_team_id", "")),
                away_name=m.get("away_team_name", ""),
                away_ref=str(m.get("away_team_id", "")),
                start_time=start, predictions=preds, odds=odds, result=result))
        return events
