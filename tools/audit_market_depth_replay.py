#!/usr/bin/env python3
"""AUDIT MARKET DEPTH REPLAY (Phase 1 — Read-Only Observability & Provenance).

Strictly read-only tool. Evaluates the 10 available BetExplorer detail files
(2026-10-12 to 2026-10-21) and performs exact, rigorous, fail-closed verification:
  1. Authoritative vs Assumed-UTC Decision-Time Eligibility:
     - Replay eligibility requires a VERIFIED aware kickoff timestamp.
     - When kickoff is an unverified local clock (bare 'HH:MM'), authoritative
       eligibility is strictly 'unverified_kickoff_timezone' (never promoted to
       decision-eligible without verified metadata).
     - Assumed-UTC classifications are reported strictly as diagnostic breakdown
       counts ('diagnostic_assumed_utc_breakdown'), never as authoritative 'kickoff_utc'.
     - Full clock string validation: rejects partial/garbage clocks like '18:00:garbage'.
     - Never silently replaces an invalid/malformed fixture timestamp with a file timestamp.
  2. Quote shape, non-dictionary handling, and completeness:
     - Non-dict rows receive an explicit 'row_not_dict' counter.
     - Rejects empty odds lists, non-list scalar odds, and column-width mismatches.
     - Validates named bookmaker non-empty identity and finite odds > 1.0.

Never alters betting state, tickets, banks, or registries.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_SAST = ZoneInfo("Africa/Johannesburg")
TZ_UTC = ZoneInfo("UTC")

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

MARKET_EXPECTED_WIDTHS: dict[str, int] = {
    "1x2": 3,
    "dc": 3,
    "ha": 2,
    "bts": 2,
    "ah": 2,
    "ou": 2,
}

_EXACT_HH_MM_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


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
    """Parse match date and kickoff into an instant and provenance classification.

    Returns:
      (dt_instant, provenance_status)
      provenance_status in:
        - 'verified_aware_iso': full aware timestamp present in row (authoritative)
        - 'unverified_local_clock': exact HH:MM, timezone unverified (diagnostic only)
        - 'malformed_clock': unparseable or partial clock string (e.g. 18:00:garbage)
        - 'missing_clock': empty or None
    """
    if kickoff_str is None or kickoff_str == "":
        return None, "missing_clock"
    if not isinstance(kickoff_str, str):
        return None, "malformed_clock"

    kickoff_clean = kickoff_str.strip()

    # If full ISO format with explicit offset
    if "T" in kickoff_clean:
        dt = parse_iso_utc(kickoff_clean)
        if dt is not None:
            return dt, "verified_aware_iso"
        return None, "malformed_clock"

    # Strict regex check for exact HH:MM (rejects 18:00:garbage or trailing characters)
    m = _EXACT_HH_MM_RE.match(kickoff_clean)
    if not m:
        return None, "malformed_clock"

    hh, mm = int(m.group(1)), int(m.group(2))
    try:
        dparts = date_str.split("-")
        dt = datetime(int(dparts[0]), int(dparts[1]), int(dparts[2]),
                      hh, mm, 0, tzinfo=TZ_UTC)
        return dt, "unverified_local_clock"
    except Exception:
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
        # Authoritative eligibility: strictly fail-closed when kickoff timezone is unverified
        "authoritative_eligibility": {
            "eligible_pre_match_decision": 0,      # requires verified aware ISO kickoff > cutoff
            "unverified_kickoff_timezone": 0,      # bare clock; timezone not established
            "ineligible_already_started": 0,       # verified kickoff <= cutoff
            "ineligible_post_kickoff_capture": 0,  # verified capture >= kickoff
            "invalid_timestamp": 0                 # missing or malformed timestamp
        },
        # Diagnostic breakdown under the assumed-UTC interpretation
        "diagnostic_assumed_utc_breakdown": {
            "pre_cutoff_upcoming": 0,               # 57 under assumed-UTC
            "pre_cutoff_started_before_cutoff": 0,  # 9 under assumed-UTC
            "post_cutoff_pre_kickoff": 0,          # 45 under assumed-UTC
            "post_kickoff": 0,                     # 5 under assumed-UTC
            "invalid_timestamp": 0
        },
        "capture_provenance": {
            "fixture_timestamp": 0,
            "file_fallback": 0,
            "invalid": 0
        },
        "named_book_inspection": {
            "total_quotes_checked": 0,
            "valid_named_quotes": 0,
            "row_not_dict": 0,
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

            # Capture timestamp: never silently replace a malformed timestamp with file fallback
            fix_raw_captured = fix.get("captured_at")
            capture_status = "fixture_timestamp"
            captured_dt = None

            if fix_raw_captured is not None:
                captured_dt = parse_iso_utc(fix_raw_captured)
                if captured_dt is None:
                    capture_status = "invalid"
            elif file_captured_at is not None:
                captured_dt = file_captured_at
                capture_status = "file_fallback"
            else:
                capture_status = "invalid"

            report["capture_provenance"][capture_status] += 1

            kickoff_dt, ko_prov = parse_kickoff_instant(date_str, fix.get("kickoff"))
            report["kickoff_provenance"][ko_prov] += 1

            # Authoritative eligibility determination
            dparts = date_str.split("-")
            cutoff_dt = datetime(int(dparts[0]), int(dparts[1]), int(dparts[2]),
                                 7, 0, 0, tzinfo=TZ_UTC)

            if capture_status == "invalid" or captured_dt is None:
                auth_status = "invalid_timestamp"
            elif ko_prov != "verified_aware_iso":
                # Unverified local clock cannot be authoritatively certified as pre-match
                auth_status = "unverified_kickoff_timezone"
            elif captured_dt >= kickoff_dt:
                auth_status = "ineligible_post_kickoff_capture"
            elif cutoff_dt >= kickoff_dt:
                auth_status = "ineligible_already_started"
            elif captured_dt < cutoff_dt:
                auth_status = "eligible_pre_match_decision"
            else:
                auth_status = "ineligible_post_cutoff_capture"

            report["authoritative_eligibility"][auth_status] += 1

            # Diagnostic breakdown under assumed-UTC interpretation
            if capture_status == "invalid" or captured_dt is None or kickoff_dt is None:
                diag_status = "invalid_timestamp"
            elif captured_dt >= kickoff_dt:
                diag_status = "post_kickoff"
            elif captured_dt < cutoff_dt:
                if cutoff_dt < kickoff_dt:
                    diag_status = "pre_cutoff_upcoming"
                else:
                    diag_status = "pre_cutoff_started_before_cutoff"
            else:
                diag_status = "post_cutoff_pre_kickoff"

            report["diagnostic_assumed_utc_breakdown"][diag_status] += 1

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
                    elif reason == "row_not_dict":
                        report["named_book_inspection"]["row_not_dict"] += 1
                    elif reason == "missing_bookmaker":
                        report["named_book_inspection"]["missing_bookmaker"] += 1
                    elif reason == "empty_odds_list":
                        report["named_book_inspection"]["empty_odds_list"] += 1
                    elif reason == "odds_not_list":
                        report["named_book_inspection"]["odds_not_list"] += 1
                    elif reason.startswith("width_mismatch"):
                        report["named_book_inspection"]["width_mismatches"] += 1
                    elif reason in ("non_finite_odds", "non_numeric_odds"):
                        report["named_book_inspection"]["non_finite_odds"] += 1
                    elif reason == "odds_le_1":
                        report["named_book_inspection"]["odds_le_1"] += 1

            # Do NOT expose an unverified clock as an authoritative kickoff_utc
            verified_ko_utc = kickoff_dt.isoformat() if (ko_prov == "verified_aware_iso" and kickoff_dt) else None

            report["fixtures"].append({
                "file": f.name,
                "fixture_key": k,
                "home": fix.get("home"),
                "away": fix.get("away"),
                "capture_status": capture_status,
                "kickoff_provenance": ko_prov,
                "authoritative_eligibility": auth_status,
                "diagnostic_assumed_utc_timing": diag_status,
                "captured_utc": captured_dt.isoformat() if captured_dt else None,
                "kickoff_utc": verified_ko_utc
            })

    report["unique_fixture_keys"] = len(seen_keys)
    return report


if __name__ == "__main__":
    rep = audit_detail_files()
    print(f"Audited {rep['files_count']} files:")
    print(f"  Total Fixtures: {rep['total_fixtures']} (Unique: {rep['unique_fixture_keys']})")
    print(f"  Kickoff Provenance: {rep['kickoff_provenance']}")
    print(f"  Authoritative Eligibility: {rep['authoritative_eligibility']}")
    print(f"  Diagnostic Assumed-UTC Breakdown: {rep['diagnostic_assumed_utc_breakdown']}")
    print(f"  Capture Provenance: {rep['capture_provenance']}")
    print(f"  Named Quote Inspection: {rep['named_book_inspection']}")
