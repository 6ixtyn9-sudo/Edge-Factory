"""
statarea.py — Statarea (old site) adapter.
Markets per match: 1x2, half-time 1x2, over 1.5/2.5/3.5 — plus FT score.
Date-addressable: /predictions/YYYY-MM-DD
"""
import re
from datetime import date, datetime, timezone

from ..models import NormalizedEvent, NormalizedPrediction, NormalizedResult
from .base import SourceAdapter

BASE = "https://old.statarea.com"

ROW_RE = re.compile(
    r'<td width="35" align="center">(\d{2}:\d{2})</td>'
    r'.*?team_host=([^("]+)\(([^)]*)\)\s*">([^<]+)</a>'
    r'.*?team_host=([^("]+)\([^)]*\)\s*">([^<]+)</a>'
    r'.*?<td width="40" align="center">([^<]*)</td>'
    r'((?:.*?>(?:\d+%|&nbsp;|-)</td>){0,1})'
    r'(.*?)(?=<td width="35" align="center">\d{2}:\d{2}</td>|$)',
    re.S)

PCT_RE = re.compile(r'>(\d+)%</td>')


class StatareaSource(SourceAdapter):
    source_key = "statarea"
    sport = "soccer"
    min_delay = 1.0

    def fetch_day(self, day: date) -> dict:
        url = f"{BASE}/predictions/{day.isoformat()}"
        return {"html": self.get(url).text, "url": url}

    def normalize(self, raw: dict, day: date) -> list[NormalizedEvent]:
        html = raw["html"]
        events = []
        # Split rows on the time cell; each chunk holds one match's tds.
        parts = re.split(r'(?=<td width="35" align="center">\d{2}:\d{2}</td>)', html)
        for part in parts[1:]:
            tm = re.match(r'<td width="35" align="center">(\d{2}:\d{2})</td>', part)
            teams = re.findall(
                r'team_host=([^("&]+)\(([^)]*)\)\s*"\s*>([^<]+)</a>', part[:1500])
            if not tm or len(teams) < 2:
                continue
            hh, mm = map(int, tm.group(1).split(":"))
            start = datetime(day.year, day.month, day.day, hh, mm,
                             tzinfo=timezone.utc)
            home_full, country, home = teams[0]
            away_full, _, away = teams[1]
            home, away = home.strip(), away.strip()

            pcts = [int(p) for p in PCT_RE.findall(part[:6000])]
            if len(pcts) < 3:
                continue
            preds = [
                NormalizedPrediction("1x2", "home", pcts[0] / 100),
                NormalizedPrediction("1x2", "draw", pcts[1] / 100),
                NormalizedPrediction("1x2", "away", pcts[2] / 100)]
            if len(pcts) >= 6:   # half-time 1x2
                preds += [
                    NormalizedPrediction("ht_1x2", "home", pcts[3] / 100),
                    NormalizedPrediction("ht_1x2", "draw", pcts[4] / 100),
                    NormalizedPrediction("ht_1x2", "away", pcts[5] / 100)]
            if len(pcts) >= 9:   # over 1.5 / 2.5 / 3.5
                preds += [
                    NormalizedPrediction("ou_1.5", "over", pcts[6] / 100),
                    NormalizedPrediction("ou_1.5", "under", 1 - pcts[6] / 100),
                    NormalizedPrediction("ou_2.5", "over", pcts[7] / 100),
                    NormalizedPrediction("ou_2.5", "under", 1 - pcts[7] / 100),
                    NormalizedPrediction("ou_3.5", "over", pcts[8] / 100),
                    NormalizedPrediction("ou_3.5", "under", 1 - pcts[8] / 100)]

            result = None
            # score cell looks like: '2:0Half time results: 1:0' (FT + optional HT)
            sm = re.search(r'>\s*(\d+):(\d+)\s*(?:<[^>]*>)*\s*Half time results?:\s*(\d+):(\d+)',
                           part[:3000])
            if not sm:
                sm = re.search(r'<td[^>]*>\s*(\d+):(\d+)\s*</td>', part[:3000])
            if sm:
                fh, fa = int(sm.group(1)), int(sm.group(2))
                sd = {"ft": [fh, fa]}
                if sm.lastindex and sm.lastindex >= 4:
                    sd["ht"] = [int(sm.group(3)), int(sm.group(4))]
                result = NormalizedResult(fh, fa, sd)

            ref = f"{day.isoformat()}:{home}:{away}"
            events.append(NormalizedEvent(
                source_ref=ref, sport=self.sport,
                competition_name=country.strip(), competition_ref=country.strip(),
                country=country.strip(),
                home_name=home, home_ref=home_full.strip(),
                away_name=away, away_ref=away_full.strip(),
                start_time=start, predictions=preds, odds=[], result=result))
        return events
