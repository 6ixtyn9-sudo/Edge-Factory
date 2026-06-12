"""
vitibet.py — Vitibet adapter (algorithmic 1x2 probs + index, FT results).
The quicktips page renders a livescore-style list; ~30 matches carry full
1/X/2 probability boxes daily. No date archive -> capture-forward source.
"""
import re
from datetime import date, datetime, timezone

from ..models import NormalizedEvent, NormalizedPrediction, NormalizedResult
from .base import SourceAdapter

URL = "https://www.vitibet.com/index.php?clanek=quicktips&sekce=fotbal&lang=en"

TIME_RE = re.compile(r"data-time='([^']+)'")
TEAM_RE = re.compile(r"livescore-team-name'>([^<]+)</span>")
PROB_RE = re.compile(
    r"prob-head'>1</div>\s*<div class='prob-val'>(\d+)%</div>"
    r".*?prob-head'>X</div>\s*<div class='prob-val'>(\d+)%</div>"
    r".*?prob-head'>2</div>\s*<div class='prob-val'>(\d+)%</div>", re.S)
FT_RE = re.compile(
    r"act-badge bg-ft'>FT</div>\s*<div class='act-scores'>\s*"
    r"<div class='act-score-line[^']*'>(\d+)</div>\s*"
    r"<div class='act-score-line[^']*'>(\d+)</div>", re.S)


class VitibetSource(SourceAdapter):
    source_key = "vitibet"
    sport = "soccer"
    min_delay = 1.0

    def fetch_day(self, day: date) -> dict:
        # no archive: always today's page; `day` recorded for bookkeeping
        return {"html": self.get(URL).text, "url": URL}

    def normalize(self, raw: dict, day: date) -> list[NormalizedEvent]:
        html = raw["html"]
        events = []
        # each match block starts at the time column
        blocks = re.split(r"(?=<div class='livescore-match-time-col'>)", html)
        for block in blocks[1:]:
            block = block[:6000]
            pm = PROB_RE.search(block)
            teams = TEAM_RE.findall(block)
            if not pm or len(teams) < 2:
                continue
            home, away = teams[0].strip(), teams[1].strip()

            start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            tmatch = TIME_RE.search(block)
            if tmatch:
                try:
                    start = datetime.fromisoformat(tmatch.group(1))
                    if start.tzinfo is None:
                        start = start.replace(tzinfo=timezone.utc)
                    start = start.astimezone(timezone.utc)
                except ValueError:
                    pass

            p1, px, p2 = (int(x) for x in pm.groups())
            preds = [NormalizedPrediction("1x2", "home", p1 / 100),
                     NormalizedPrediction("1x2", "draw", px / 100),
                     NormalizedPrediction("1x2", "away", p2 / 100)]

            result = None
            fm = FT_RE.search(block)
            if fm:
                fh, fa = int(fm.group(1)), int(fm.group(2))
                result = NormalizedResult(fh, fa, {"ft": [fh, fa]})

            ref = f"{start.date().isoformat()}:{home}:{away}"
            events.append(NormalizedEvent(
                source_ref=ref, sport=self.sport,
                competition_name="", competition_ref="vitibet-quicktips",
                country="", home_name=home, home_ref=home,
                away_name=away, away_ref=away,
                start_time=start, predictions=preds, odds=[], result=result))
        return events
