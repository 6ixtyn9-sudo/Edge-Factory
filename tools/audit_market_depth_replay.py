#!/usr/bin/env python3
"""AUDIT MARKET DEPTH REPLAY (Phase 1 — Read-Only Observability & Provenance).

Strictly read-only tool. Evaluates the 10 available BetExplorer detail files
(2026-10-12 to 2026-10-21) and performs exact, rigorous verification:
  1. Capture timestamp vs decision cutoff (09:00 SAST = 07:00 UTC) and kickoff.
  2. Exact market availability (1x2, ah, dc, ou, bts, ha).
  3. Real named-book price inspection (non-empty bookmaker, finite odds > 1.0).
  4. Classification of every quote:
       - 'pre_cutoff': captured before 09:00 SAST and before kickoff
       - 'post_cutoff_pre_kickoff': captured on/after 09:00 SAST but before kickoff
       - 'post_kickoff': captured on/after kickoff (unusable / lookahead)
       - 'invalid_timestamp': missing, non-UTC, or unparseable timestamps

Never alters betting state, tickets, banks, or registries.
"""
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_SAST = ZoneInfo("Africa/Johannesburg")
TZ_UTC = ZoneInfo("UTC")

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"


def parse_iso_utc(ts: str | None) -> datetime | None:
    """Parse an ISO-8601 string into an aware UTC datetime, or None."""
    if not ts or not isinstance(ts, str):
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return None
        return dt.astimezone(TZ_UTC)
    except Exception:
        return None


def parse_kickoff_instant(date_str: str, kickoff_str: str | None) -> datetime | None:
    """Parse match date (YYYY-MM-DD) and kickoff (HH:MM or ISO) into UTC instant."""
    if not kickoff_str or not isinstance(kickoff_str, str):
        return None
    # If full ISO format
    dt = parse_iso_utc(kickoff_str)
    if dt is not None:
        return dt
    # If clock-only HH:MM
    parts = kickoff_str.strip().split(":")
    if len(parts) >= 2:
        try:
            hh, mm = int(parts[0]), int(parts[1])
            # BetExplorer lists times in UTC or match local; in this schema it is UTC
            dparts = date_str.split("-")
            return datetime(int(dparts[0]), int(dparts[1]), int(dparts[2]),
                            hh, mm, 0, tzinfo=TZ_UTC)
        except Exception:
            return None
    return None


def audit_detail_files() -> dict:
    files = sorted(LOCALDATA.glob("betexplorer_match_detail_*.json"))
    report = {
        "files_count": len(files),
        "total_fixtures": 0,
        "unique_fixture_keys": 0,
        "market_counts": {"1x2": 0, "ah": 0, "dc": 0, "ou": 0, "bts": 0, "ha": 0},
        "timing_classification": {
            "pre_cutoff": 0,              # captured before 07:00 UTC (09:00 SAST) and before KO
            "post_cutoff_pre_kickoff": 0, # captured after 07:00 UTC but before KO (intraday)
            "post_kickoff": 0,            # captured after KO (lookahead/leakage)
            "invalid_timestamp": 0        # unparseable / missing
        },
        "named_book_inspection": {
            "total_quotes_checked": 0,
            "valid_named_quotes": 0,
            "missing_bookmaker": 0,
            "non_finite_odds": 0,
            "odds_le_1": 0
        },
        "fixtures": []
    }

    seen_keys = set()
    for f in files:
        data = json.loads(f.read_text())
        fixtures = data.get("fixtures", {})
        file_captured_at = parse_iso_utc(data.get("captured_at"))
        date_str = str(data.get("date") or f.name.replace("betexplorer_match_detail_", "").replace(".json", ""))[:10]

        for k, fix in fixtures.items():
            report["total_fixtures"] += 1
            seen_keys.add(k)

            mkts = fix.get("markets", {})
            for m in report["market_counts"]:
                if m in mkts:
                    report["market_counts"][m] += 1

            # Determine capture timestamp
            captured_dt = parse_iso_utc(fix.get("captured_at")) or file_captured_at
            kickoff_dt = parse_kickoff_instant(date_str, fix.get("kickoff"))

            # Timing classification
            if captured_dt is None or kickoff_dt is None:
                timing_status = "invalid_timestamp"
            elif captured_dt >= kickoff_dt:
                timing_status = "post_kickoff"
            else:
                # 09:00 SAST is 07:00 UTC
                cutoff_dt = datetime(kickoff_dt.year, kickoff_dt.month, kickoff_dt.day,
                                     7, 0, 0, tzinfo=TZ_UTC)
                if captured_dt < cutoff_dt:
                    timing_status = "pre_cutoff"
                else:
                    timing_status = "post_cutoff_pre_kickoff"

            report["timing_classification"][timing_status] += 1

            # Named book quote inspection across all markets
            for mkt_slug, mkt_data in mkts.items():
                if not isinstance(mkt_data, dict):
                    continue
                rows = mkt_data.get("rows") or []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    report["named_book_inspection"]["total_quotes_checked"] += 1
                    book = row.get("bookmaker")
                    odds_list = row.get("odds") or []

                    if not isinstance(book, str) or not book.strip():
                        report["named_book_inspection"]["missing_bookmaker"] += 1
                        continue

                    # Validate individual odds values in the row
                    valid_row = True
                    for odd_val in odds_list:
                        try:
                            f_odd = float(odd_val)
                            if not math.isfinite(f_odd):
                                report["named_book_inspection"]["non_finite_odds"] += 1
                                valid_row = False
                                break
                            if f_odd <= 1.0:
                                report["named_book_inspection"]["odds_le_1"] += 1
                                valid_row = False
                                break
                        except (TypeError, ValueError):
                            report["named_book_inspection"]["non_finite_odds"] += 1
                            valid_row = False
                            break

                    if valid_row:
                        report["named_book_inspection"]["valid_named_quotes"] += 1

            report["fixtures"].append({
                "file": f.name,
                "fixture_key": k,
                "home": fix.get("home"),
                "away": fix.get("away"),
                "timing_status": timing_status,
                "captured_utc": captured_dt.isoformat() if captured_dt else None,
                "kickoff_utc": kickoff_dt.isoformat() if kickoff_dt else None
            })

    report["unique_fixture_keys"] = len(seen_keys)
    return report


if __name__ == "__main__":
    rep = audit_detail_files()
    print(f"Audited {rep['files_count']} files:")
    print(f"  Total Fixtures: {rep['total_fixtures']} (Unique: {rep['unique_fixture_keys']})")
    print(f"  Markets Available: {rep['market_counts']}")
    print(f"  Timing Classifications: {rep['timing_classification']}")
    print(f"  Named Bookmaker Quotes Inspected: {rep['named_book_inspection']}")
