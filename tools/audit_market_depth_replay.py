#!/usr/bin/env python3
"""AUDIT MARKET DEPTH REPLAY (Phase 1 — Read-Only Observability & Provenance).

Strictly read-only tool. Evaluates the 10 available BetExplorer detail files
(2026-10-12 to 2026-10-21) and performs exact, rigorous, fail-closed verification:
  1. Capture timestamp vs decision cutoff (09:00 SAST = 07:00 UTC) and kickoff.
     - Never silently replaces an invalid/malformed fixture timestamp with a file timestamp.
     - Distinguishes 'pre_cutoff_upcoming' (captured < cutoff AND cutoff < kickoff)
       from 'pre_cutoff_started_before_cutoff' (kickoff <= cutoff) and 'post_cutoff'.
     - Accurately tracks kickoff timezone provenance: bare 'HH:MM' is explicitly
       recorded as 'unverified_local_clock' per betexplorer_odds.py:1198.
  2. Market-column completeness and shape enforcement:
     - Rejects empty odds lists, non-list scalar odds, and column-width mismatches.
     - Validates named bookmaker non-empty identity and finite odds > 1.0.

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

# Standard market column counts
MARKET_EXPECTED_WIDTHS: dict[str, int] = {
    "1x2": 3,
    "dc": 3,
    "ha": 2,
    "bts": 2,
    # ah and ou are line-based (home, away) or (over, under) = 2 per line
    "ah": 2,
    "ou": 2,
}


def parse_iso_utc(ts: object) -> datetime | None:
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


def parse_kickoff_instant(date_str: str, kickoff_str: object) -> tuple[datetime | None, str]:
    """Parse match date and kickoff into a UTC instant and provenance classification.

    Returns:
      (dt_utc, provenance_status)
      provenance_status in:
        - 'verified_aware_iso': full aware timestamp present in row
        - 'unverified_local_clock': bare HH:MM, timezone assumed/unverified
        - 'malformed_clock': non-HH:MM or unparseable string
        - 'missing_clock': empty or None
    """
    if kickoff_str is None or kickoff_str == "":
        return None, "missing_clock"
    if not isinstance(kickoff_str, str):
        return None, "malformed_clock"

    # If full ISO format with explicit offset
    if "T" in kickoff_str:
        dt = parse_iso_utc(kickoff_str)
        if dt is not None:
            return dt, "verified_aware_iso"
        return None, "malformed_clock"

    # If clock-only HH:MM (BetExplorer schema)
    parts = kickoff_str.strip().split(":")
    if len(parts) >= 2:
        try:
            hh, mm = int(parts[0]), int(parts[1])
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                return None, "malformed_clock"
            dparts = date_str.split("-")
            dt = datetime(int(dparts[0]), int(dparts[1]), int(dparts[2]),
                          hh, mm, 0, tzinfo=TZ_UTC)
            return dt, "unverified_local_clock"
        except Exception:
            return None, "malformed_clock"
    return None, "malformed_clock"


def validate_quote_row(market: str, row: object) -> tuple[bool, str]:
    """Strictly validate a quote row for non-empty bookmaker and shape completeness."""
    if not isinstance(row, dict):
        return False, "row_not_dict"

    book = row.get("bookmaker")
    if not isinstance(book, str) or not book.strip():
        return False, "missing_bookmaker"

    odds_list = row.get("odds")
    if not isinstance(odds_list, list):
        return False, "odds_not_list"
    if len(odds_list) == 0:
        return False, "empty_odds_list"

    expected_width = MARKET_EXPECTED_WIDTHS.get(market)
    if expected_width is not None and len(odds_list) != expected_width:
        return False, f"width_mismatch_expected_{expected_width}_got_{len(odds_list)}"

    for odd_val in odds_list:
        try:
            f_odd = float(odd_val)
            if not math.isfinite(f_odd):
                return False, "non_finite_odds"
            if f_odd <= 1.0:
                return False, "odds_le_1"
        except (TypeError, ValueError):
            return False, "non_numeric_odds"

    return True, "valid"


def audit_detail_files() -> dict:
    files = sorted(LOCALDATA.glob("betexplorer_match_detail_*.json"))
    report = {
        "files_count": len(files),
        "total_fixtures": 0,
        "unique_fixture_keys": 0,
        "market_counts": {"1x2": 0, "ah": 0, "dc": 0, "ou": 0, "bts": 0, "ha": 0},
        "kickoff_provenance": {
            "verified_aware_iso": 0,
            "unverified_local_clock": 0,
            "malformed_clock": 0,
            "missing_clock": 0
        },
        "timing_classification": {
            "pre_cutoff_upcoming": 0,               # captured < cutoff AND cutoff < kickoff (true decision candidate)
            "pre_cutoff_started_before_cutoff": 0,  # captured < cutoff BUT kickoff <= cutoff (cannot be pre-match decision)
            "post_cutoff_pre_kickoff": 0,          # captured >= cutoff BUT captured < kickoff (intraday pre-match)
            "post_kickoff": 0,                     # captured >= kickoff (lookahead/leakage)
            "invalid_timestamp": 0                 # unparseable / malformed / missing capture timestamp
        },
        "capture_provenance": {
            "fixture_timestamp": 0,
            "file_fallback": 0,
            "invalid": 0
        },
        "named_book_inspection": {
            "total_quotes_checked": 0,
            "valid_named_quotes": 0,
            "missing_bookmaker": 0,
            "empty_odds_list": 0,
            "odds_not_list": 0,
            "width_mismatches": 0,
            "non_finite_odds": 0,
            "odds_le_1": 0
        },
        "fixtures": []
    }

    seen_keys = set()
    for f in files:
        data = json.loads(f.read_text())
        fixtures = data.get("fixtures", {})
        file_captured_raw = data.get("captured_at")
        file_captured_at = parse_iso_utc(file_captured_raw)
        date_str = str(data.get("date") or f.name.replace("betexplorer_match_detail_", "").replace(".json", ""))[:10]

        for k, fix in fixtures.items():
            report["total_fixtures"] += 1
            seen_keys.add(k)

            mkts = fix.get("markets", {})
            for m in report["market_counts"]:
                if m in mkts:
                    report["market_counts"][m] += 1

            # Capture timestamp provenance: never silently heal malformed timestamps
            fix_raw_captured = fix.get("captured_at")
            capture_status = "fixture_timestamp"
            captured_dt = None

            if fix_raw_captured is not None:
                captured_dt = parse_iso_utc(fix_raw_captured)
                if captured_dt is None:
                    # Malformed fixture timestamp: explicit failure, do NOT fallback
                    capture_status = "invalid"
            elif file_captured_at is not None:
                captured_dt = file_captured_at
                capture_status = "file_fallback"
            else:
                capture_status = "invalid"

            report["capture_provenance"][capture_status] += 1

            # Kickoff instant and provenance
            kickoff_dt, ko_prov = parse_kickoff_instant(date_str, fix.get("kickoff"))
            report["kickoff_provenance"][ko_prov] += 1

            # Timing classification
            if capture_status == "invalid" or captured_dt is None or kickoff_dt is None:
                timing_status = "invalid_timestamp"
            elif captured_dt >= kickoff_dt:
                timing_status = "post_kickoff"
            else:
                # 09:00 SAST is 07:00 UTC on the scheduled date
                dparts = date_str.split("-")
                cutoff_dt = datetime(int(dparts[0]), int(dparts[1]), int(dparts[2]),
                                     7, 0, 0, tzinfo=TZ_UTC)
                if captured_dt < cutoff_dt:
                    if cutoff_dt < kickoff_dt:
                        timing_status = "pre_cutoff_upcoming"
                    else:
                        timing_status = "pre_cutoff_started_before_cutoff"
                else:
                    timing_status = "post_cutoff_pre_kickoff"

            report["timing_classification"][timing_status] += 1

            # Quote inspection
            for mkt_slug, mkt_data in mkts.items():
                if not isinstance(mkt_data, dict):
                    continue
                rows = mkt_data.get("rows") or []
                for row in rows:
                    report["named_book_inspection"]["total_quotes_checked"] += 1
                    is_valid, reason = validate_quote_row(mkt_slug, row)
                    if is_valid:
                        report["named_book_inspection"]["valid_named_quotes"] += 1
                    elif reason == "missing_bookmaker":
                        report["named_book_inspection"]["missing_bookmaker"] += 1
                    elif reason == "empty_odds_list":
                        report["named_book_inspection"]["empty_odds_list"] += 1
                    elif reason == "odds_not_list":
                        report["named_book_inspection"]["odds_not_list"] += 1
                    elif reason.startswith("width_mismatch"):
                        report["named_book_inspection"]["width_mismatches"] += 1
                    elif reason == "non_finite_odds" or reason == "non_numeric_odds":
                        report["named_book_inspection"]["non_finite_odds"] += 1
                    elif reason == "odds_le_1":
                        report["named_book_inspection"]["odds_le_1"] += 1

            report["fixtures"].append({
                "file": f.name,
                "fixture_key": k,
                "home": fix.get("home"),
                "away": fix.get("away"),
                "capture_status": capture_status,
                "kickoff_provenance": ko_prov,
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
    print(f"  Kickoff Provenance: {rep['kickoff_provenance']}")
    print(f"  Capture Provenance: {rep['capture_provenance']}")
    print(f"  Timing Classifications: {rep['timing_classification']}")
    print(f"  Named Quote Inspection: {rep['named_book_inspection']}")
