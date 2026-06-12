"""
forebet.py — first adapter. Soccer, 4 markets via Forebet's JSON endpoint.
This is the reference implementation: copy this file to add a new source.
"""
from datetime import date, datetime, timezone

from ..models import (NormalizedEvent, NormalizedOdds, NormalizedPrediction,
                      NormalizedResult)
from .base import SourceAdapter

BASE = "https://www.forebet.com"
VOID_COMMENTS = {"Postp.", "Aban.", "Cancl.", "Awarded", "Int."}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class ForebetSource(SourceAdapter):
    source_key = "forebet"
    sport = "soccer"
    min_delay = 0.4

    MARKETS = ("1x2", "uo", "bts")

    def fetch_day(self, day: date) -> dict:
        ds = day.isoformat()
        tzs = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())
        out = {}
        for tp in self.MARKETS:
            url = (f"{BASE}/scripts/getrs.php?ln=en&tp={tp}&in={ds}"
                   f"&ord=0&tz=0&tzs={tzs}&tze={tzs + 100800}")
            resp = self.get(url, headers={
                "Referer": f"{BASE}/en/football-predictions/predictions-1x2/{ds}",
                "X-Requested-With": "XMLHttpRequest"})
            out[tp] = resp.json()
        return out

    def normalize(self, raw: dict, day: date) -> list[NormalizedEvent]:
        m1, leagues = (raw["1x2"] + [[], {}])[:2] if isinstance(raw["1x2"], list) else ([], {})
        uo = {m["id"]: m for m in (raw["uo"][0] or [])}
        bts = {m["id"]: m for m in (raw["bts"][0] or [])}

        events = []
        for m in (m1 or []):
            p1, px, p2 = _num(m.get("Pred_1")), _num(m.get("Pred_X")), _num(m.get("Pred_2"))
            if p1 is None:
                continue
            lg = leagues.get(str(m.get("league_id"))) or []
            try:
                start = datetime.strptime(m["DATE_BAH"], "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc)
            except (KeyError, ValueError, TypeError):
                continue

            preds = [
                NormalizedPrediction("1x2", "home", p1 / 100,
                                     {"pred_score": [m.get("host_sc_pr"), m.get("guest_sc_pr")],
                                      "avg_goals": m.get("goalsavg")}),
                NormalizedPrediction("1x2", "draw", (px or 0) / 100),
                NormalizedPrediction("1x2", "away", (p2 or 0) / 100),
            ]
            odds = []
            for sel, key in (("home", "best_odd_1"), ("draw", "best_odd_X"),
                             ("away", "best_odd_2")):
                if (o := _num(m.get(key))):
                    odds.append(NormalizedOdds("1x2", sel, o))

            u = uo.get(m["id"], {})
            if (pu := _num(u.get("pr_under"))) is not None:
                po = _num(u.get("pr_over")) or 0
                preds += [NormalizedPrediction("ou_2.5", "under", pu / 100),
                          NormalizedPrediction("ou_2.5", "over", po / 100)]
                for sel, key in (("under", "best_under"), ("over", "best_over")):
                    if (o := _num(u.get(key))):
                        odds.append(NormalizedOdds("ou_2.5", sel, o))

            b = bts.get(m["id"], {})
            if (pg := _num(b.get("Pred_gg"))) is not None:
                pn = _num(b.get("Pred_no_gg")) or 0
                preds += [NormalizedPrediction("btts", "yes", pg / 100),
                          NormalizedPrediction("btts", "no", pn / 100)]
                for sel, key in (("yes", "odds_gg_y"), ("no", "odds_gg_n")):
                    if (o := _num(b.get(key))):
                        odds.append(NormalizedOdds("btts", sel, o))

            result = None
            fh, fa = _num(m.get("Host_SC")), _num(m.get("Guest_SC"))
            comment = (m.get("comment") or "").strip()
            if comment in VOID_COMMENTS:
                result = NormalizedResult(None, None, {}, status="void")
            elif fh is not None and fa is not None:
                result = NormalizedResult(fh, fa, {
                    "ft": [fh, fa],
                    "ht": [_num(m.get("Host_SC_HT")), _num(m.get("Guest_SC_HT"))]})

            events.append(NormalizedEvent(
                source_ref=str(m["id"]), sport=self.sport,
                competition_name=lg[1] if len(lg) > 1 else "",
                competition_ref=str(m.get("league_id", "")),
                country=lg[0] if lg else "",
                home_name=m.get("HOST_NAME", ""), home_ref=str(m.get("host_id", "")),
                away_name=m.get("GUEST_NAME", ""), away_ref=str(m.get("guest_id", "")),
                start_time=start, predictions=preds, odds=odds, result=result))
        return events
