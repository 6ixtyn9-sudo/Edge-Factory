"""
zulubet.py — Zulubet adapter (soccer, 1x2 probs + average odds + FT results).
History: date-addressable archives (tips-DD-MM-YYYY.html) back to ~2024.
"""
import re
from datetime import date, datetime, timedelta, timezone

from ..models import (NormalizedEvent, NormalizedOdds, NormalizedPrediction,
                      NormalizedResult)
from .base import SourceAdapter

BASE = "https://www.zulubet.com"

# one match row, non-greedy across the whole <tr>
ROW_RE = re.compile(
    r"<noscript>(\d{2}-\d{2}), (\d{2}:\d{2})</noscript>.*?"
    r'title="([^"]*)"[^>]*>\s*([^<]+?)\s*-\s*([^<]+?)</td>'
    r".*?1: (\d+)%.*?X: (\d+)%.*?2: (\d+)%"
    r".*?1: ([\d.]+)<br>X: ([\d.]+)<br>2: ([\d.]+)"
    r'.*?<td style="text-align: center;">([^<]*)</td>',
    re.S)

SCORE_RE = re.compile(r"^(\d+):(\d+)$")


class ZulubetSource(SourceAdapter):
    source_key = "zulubet"
    sport = "soccer"
    min_delay = 1.0          # be extra polite, plain PHP site

    def fetch_day(self, day: date) -> dict:
        url = f"{BASE}/tips-{day.strftime('%d-%m-%Y')}.html"
        return {"html": self.get(url).text, "url": url}

    def normalize(self, raw: dict, day: date) -> list[NormalizedEvent]:
        html = raw["html"]
        events = []
        # split per row to keep the regex anchored within one match
        chunks = html.split("<noscript>")
        for chunk in chunks[1:]:
            m = ROW_RE.search("<noscript>" + chunk[:4000])
            if not m:
                continue
            (dm, hhmm, league_title, home, away,
             p1, px, p2, o1, ox, o2, tail) = m.groups()

            # noscript time is UTC+1 on zulubet; date sanity: trust requested day
            try:
                hh, mm = map(int, hhmm.split(":"))
                dd, mo = map(int, dm.split("-"))
                start = datetime(day.year, mo, dd, hh, mm,
                                 tzinfo=timezone.utc) - timedelta(hours=1)
            except ValueError:
                continue

            country, _, league = league_title.partition(" ")
            home, away = home.strip(), away.strip()

            preds = [NormalizedPrediction("1x2", "home", int(p1) / 100),
                     NormalizedPrediction("1x2", "draw", int(px) / 100),
                     NormalizedPrediction("1x2", "away", int(p2) / 100)]
            odds = [NormalizedOdds("1x2", "home", float(o1), bookmaker="avg"),
                    NormalizedOdds("1x2", "draw", float(ox), bookmaker="avg"),
                    NormalizedOdds("1x2", "away", float(o2), bookmaker="avg")]

            result = None
            sm = SCORE_RE.match(tail.strip())
            if sm:
                fh, fa = int(sm.group(1)), int(sm.group(2))
                result = NormalizedResult(fh, fa, {"ft": [fh, fa]})

            ref = f"{day.isoformat()}:{home}:{away}"
            events.append(NormalizedEvent(
                source_ref=ref, sport=self.sport,
                competition_name=league.strip() or league_title,
                competition_ref=league_title, country=country,
                home_name=home, home_ref=home, away_name=away, away_ref=away,
                start_time=start, predictions=preds, odds=odds, result=result))
        return events
