#!/usr/bin/env python3
"""Zero-credit theoddsapi matching probe for the frozen card.

Uses only the usage-free endpoints (/sports and /sports/{key}/events). It never
calls an odds endpoint, so it spends no credits. For every fixture on the
frozen card it says why the match did or did not resolve:

  - league not covered (no sport key for the league)
  - no event in the league's sport key, with the closest event names
  - matched, with the event it matched

Usage:
  PYTHONPATH=src python3 scripts/probe_theoddsapi_events.py --date 2026-10-13
  (--date defaults to today in SAST)
"""
from __future__ import annotations

import argparse
import difflib
import sys

from edgefactory.sources import theoddsapi as tha


def _name(ev: dict) -> str:
    return f"{ev.get('home_team')} v {ev.get('away_team')}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=None,
                    help="card date, YYYY-MM-DD (default: today in SAST)")
    args = ap.parse_args(argv)
    if not args.date:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        args.date = datetime.now(ZoneInfo("Africa/Johannesburg")).date().isoformat()

    if not tha.API_KEYS:
        print("theoddsapi events probe: no ODDS_API_KEYS set; nothing to do")
        return 1

    fixtures = tha.shortlist(args.date)
    print(f"theoddsapi events probe {args.date}: card fixtures={len(fixtures)} "
          f"keys={len(tha.API_KEYS)} (events endpoints only, 0 odds credits)")
    if not fixtures:
        print("no frozen card for this date (no picks archive); nothing to match")
        return 0

    sports = tha.load_sports(refresh=True)
    print(f"sports loaded={len(sports)}")

    events_by_key: dict[str, list[dict] | None] = {}
    tally: dict[str, int] = {}

    def bump(reason: str) -> None:
        tally[reason] = tally.get(reason, 0) + 1

    for p in fixtures:
        label = f"{p.get('home')} vs {p.get('away')} [{p.get('league')}]"
        key = tha.sport_key_for_league(p.get("league"), sports)
        if key is None:
            bump("league not covered")
            print(f"  {label}: league not covered")
            continue
        if key not in events_by_key:
            try:
                events_by_key[key] = tha.fetch_events(key)
            except Exception as exc:  # noqa: BLE001 - diagnostic probe
                events_by_key[key] = None
                print(f"  events fetch failed for {key}: {type(exc).__name__}: {exc}")
        events = events_by_key[key]
        if events is None:
            bump("events fetch failed")
            print(f"  {label}: events fetch failed for {key}")
            continue
        ev = tha.match_event(p, events)
        if ev:
            bump("matched")
            print(f"  {label}: matched {key} -> {_name(ev)}")
            continue
        bump("no event in league")
        query = f"{p.get('home')} v {p.get('away')}"
        close = difflib.get_close_matches(query, [_name(e) for e in events], n=2, cutoff=0.4)
        print(f"  {label}: no event in {key} (events={len(events)}); "
              f"closest={close or 'none'}")

    print("summary:", ", ".join(f"{k}={v}" for k, v in sorted(tally.items())) or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
