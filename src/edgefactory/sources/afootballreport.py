"""
afootballreport.py — AFootballReport adapter.
Tips are streak-based ("X have over 2.5 in their last N games"), not
probabilities — we encode tip + streak length as pseudo-confidence:
probability = min(0.5 + streak * 0.02, 0.95), capped, stored with the raw
streak in `extra` so the miner can grid on streak length directly.
Markets covered: ou_1.5 / ou_2.5 / btts from the under-over and btts pages.
Capture-forward only (no archive).
"""
import re
from datetime import date, datetime, timezone

from ..models import NormalizedEvent, NormalizedPrediction
from .base import SourceAdapter

BASE = "https://afootballreport.com"
PAGES = {
    "ou": f"{BASE}/predictions/under-over-goals",
    "btts": f"{BASE}/predictions/both-teams-to-score",
}

ROW_RE = re.compile(
    r'itemprop="startDate" content="([^"]+)"'
    r'.*?itemprop="name" content="([^"]+)"'      # location/country
    r'.*?itemprop="homeTeam"[^>]*>\s*<meta itemprop="name" content="([^"]+)"'
    r'.*?itemprop="awayTeam"[^>]*>\s*<meta itemprop="name" content="([^"]+)"',
    re.S)
TIP_RE = re.compile(r'class="tip[^"]*"[^>]*>\s*(?:<[^>]+>\s*)*([A-Za-z0-9 ./]+?)\s*<', re.S)
STREAK_RE = re.compile(r"last (\d+) games")


def tip_to_market(tip: str):
    t = tip.lower().strip()
    if "over 2.5" in t:
        return "ou_2.5", "over"
    if "under 2.5" in t:
        return "ou_2.5", "under"
    if "over 1.5" in t:
        return "ou_1.5", "over"
    if "both teams to score" in t or t in ("yes", "btts yes"):
        return "btts", "yes"
    if t in ("no", "btts no"):
        return "btts", "no"
    return None, None


class AFootballReportSource(SourceAdapter):
    source_key = "afootballreport"
    sport = "soccer"
    min_delay = 1.2

    def fetch_day(self, day: date) -> dict:
        return {k: self.get(url).text for k, url in PAGES.items()}

    def normalize(self, raw: dict, day: date) -> list[NormalizedEvent]:
        merged: dict[str, NormalizedEvent] = {}
        for page_html in raw.values():
            rows = page_html.split("<tr itemscope")
            for chunk in rows[1:]:
                chunk = chunk[:8000]
                m = ROW_RE.search(chunk)
                if not m:
                    continue
                start_s, country, home, away = m.groups()
                try:
                    start = datetime.fromisoformat(start_s)
                    if start.tzinfo is None:
                        start = start.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

                # tip text lives in the row's tip cell; streak in logic cell
                tip_m = re.search(r'<strong>([^<]+)</strong>', chunk)
                tip = tip_m.group(1) if tip_m else ""
                market, selection = tip_to_market(tip)
                if not market:
                    continue
                streak_m = STREAK_RE.search(chunk)
                streak = int(streak_m.group(1)) if streak_m else 0
                pseudo_prob = min(0.5 + streak * 0.02, 0.95)

                ref = f"{start.date().isoformat()}:{home}:{away}"
                ev = merged.get(ref)
                if ev is None:
                    ev = NormalizedEvent(
                        source_ref=ref, sport=self.sport,
                        competition_name=country, competition_ref=country,
                        country=country, home_name=home.strip(), home_ref=home.strip(),
                        away_name=away.strip(), away_ref=away.strip(),
                        start_time=start, predictions=[], odds=[], result=None)
                    merged[ref] = ev
                # dedupe: keep the strongest streak per (market, selection)
                existing = next((p for p in ev.predictions
                                 if p.market == market and p.selection == selection), None)
                if existing is None:
                    ev.predictions.append(NormalizedPrediction(
                        market, selection, pseudo_prob, {"streak": streak, "tip": tip}))
                elif streak > existing.extra.get("streak", 0):
                    existing.probability = pseudo_prob
                    existing.extra = {"streak": streak, "tip": tip}
        return list(merged.values())
