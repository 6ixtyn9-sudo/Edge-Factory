#!/usr/bin/env python3
"""AUDIT MARKET DEPTH REPLAY (Read-Only Observability & Witness Provenance).

Strictly read-only tool. Evaluates available BetExplorer detail files and existing
provider schedule archives and performs exact, rigorous, fail-closed verification:
  1. Authoritative vs Assumed-UTC Decision-Time Eligibility:
     - Replay screening requires a direct aware kickoff or independent pre-cutoff
       schedule witness corroborating a preserved page data_dt tuple.
     - Legacy missing page dates are NOT reconstructed from candidate/container dates.
     - Fixed UTC+1 and Prague are hypotheses tested separately, not site-wide defaults.
     - Capture-valid rows are NOT live admission, price freshness or selection/line validation.
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

import argparse
import csv
import gzip
import hashlib
import io
import json
import sys
import math
import re
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_SAST = ZoneInfo("Africa/Johannesburg")
TZ_UTC = ZoneInfo("UTC")

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT / "src"))

from edgefactory.identity import source_team_key
from edgefactory.kickoff_corroboration import (
    corroborate_kickoff_witness, interpret_betexplorer_data_dt,
    normalize_source_family, verify_fixture_identity,
)

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


def decision_cutoff_utc(day: str) -> datetime | None:
    """The explicit 09:00 Johannesburg decision on the ledger's decision day."""
    try:
        return datetime.combine(date.fromisoformat(day), time(9), TZ_SAST).astimezone(TZ_UTC)
    except (TypeError, ValueError):
        return None


def load_schedule_witnesses(fixtures: list[dict]) -> tuple[dict, list[dict]]:
    """Read existing provider archives, never cards, warehouse labels or the network.

    OddsPapi kickoff is provider startTime (oddspapi_odds.parse_odds_response).
    Legacy TheOddsAPI rows may inherit pick kickoff: require an explicit
    provider_commence_time origin before treating those rows as witnesses.
    Receipts identify the immutable archive bytes and original CSV row.
    """
    wanted = {(source_team_key(f.get("home")), source_team_key(f.get("away")))
              for f in fixtures}
    by_pair: dict[tuple, list[dict]] = {}
    receipts = []
    team_keys: dict[str, str] = {}
    for provider in ("oddspapi", "theoddsapi"):
        for path in sorted(LOCALDATA.glob(f"{provider}_odds_*.csv.gz")):
            # Bind the digest and parser to the SAME bytes, even if a capture
            # atomically replaces this archive while the audit is running.
            archive_bytes = path.read_bytes()
            receipt = {"file": path.name, "sha256": hashlib.sha256(archive_bytes).hexdigest(),
                       "source_family": provider, "rows_scanned": 0,
                       "matched_identity_rows": 0, "witness_records": 0,
                       "rejections": {}}
            receipts.append(receipt)
            seen = set()
            with gzip.open(io.BytesIO(archive_bytes), "rt", newline="") as handle:
                for ordinal, row in enumerate(csv.DictReader(handle), 1):
                    receipt["rows_scanned"] += 1
                    home, away = row.get("home", ""), row.get("away", "")
                    for name in (home, away):
                        if name not in team_keys:
                            team_keys[name] = source_team_key(name)
                    pair = (team_keys[home], team_keys[away])
                    if not all(pair) or pair not in wanted:
                        continue
                    receipt["matched_identity_rows"] += 1
                    reason = None
                    if normalize_source_family(row.get("source")) != provider:
                        reason = "archive_source_mismatch"
                    elif row.get("source_type") != "odds" or row.get("sport") != "soccer":
                        reason = "unsupported_record_contract"
                    elif provider == "theoddsapi" and row.get("kickoff_origin") != "provider_commence_time":
                        reason = "provider_kickoff_origin_unproven"
                    kickoff = parse_iso_utc(row.get("kickoff"))
                    observed = parse_iso_utc(row.get("captured_at"))
                    if reason is None and (kickoff is None or observed is None):
                        reason = "invalid_witness_timestamp"
                    if reason:
                        counts = receipt["rejections"]
                        counts[reason] = counts.get(reason, 0) + 1
                        continue
                    key = (home, away, kickoff, observed)
                    if key in seen:
                        continue  # outcomes/books repeat the same schedule observation
                    seen.add(key)
                    record = {"source": provider, "home": home, "away": away,
                              "league": row.get("league"),
                              "kickoff_utc": kickoff.isoformat(),
                              "observed_at_utc": observed.isoformat(),
                              "file": path.name, "file_sha256": receipt["sha256"],
                              "csv_data_row": ordinal,
                              "row_sha256": hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest(),
                              "kickoff_origin": ("provider_startTime" if provider == "oddspapi"
                                                 else "provider_commence_time")}
                    by_pair.setdefault(pair, []).append(record)
                    receipt["witness_records"] += 1
    return by_pair, receipts


def resolve_schedule_witness(fixture: dict, cutoff: datetime, witnesses: dict) -> dict:
    """Corroborate preserved page evidence against independent, as-of witnesses.

    Try BOTH documented interpretations without selecting a site-wide default.
    Legacy container/pick dates are never substituted for the missing page date.
    Any conflicting same-fixture pre-cutoff schedule records leave it unresolved.
    A witness found after cutoff cannot retroactively establish replay eligibility.
    """
    out = {"status": "unresolved", "reason": "missing_raw_page_datetime",
           "kickoff_utc": None, "provenance": None, "witnesses": [],
           "interpretations": [], "late_witness_records": 0}
    raw = fixture.get("data_dt")
    if not isinstance(raw, (list, tuple)) or len(raw) != 5 or any(type(v) is not int for v in raw):
        return out
    dd, mm, year, hour, minute = raw
    try:
        raw_date = date(year, mm, dd).isoformat()
    except (ValueError, OverflowError):
        out["reason"] = "invalid_raw_page_datetime"
        return out
    if fixture.get("kickoff_date") not in (None, raw_date):
        out["reason"] = "raw_page_date_conflict"
        return out
    if fixture.get("kickoff") != f"{hour:02d}:{minute:02d}":
        out["reason"] = "raw_page_clock_conflict"
        return out
    interpretations = []
    for mode in ("fixed_utc_plus_1", "europe_prague"):
        instant, label = interpret_betexplorer_data_dt(raw, mode=mode)
        if instant is not None:
            interpretations.append((instant, label))
    if not interpretations:
        out["reason"] = "invalid_raw_page_datetime"
        return out
    pair = (source_team_key(fixture.get("home")), source_team_key(fixture.get("away")))
    matches = []
    for witness in witnesses.get(pair, []):
        if not verify_fixture_identity(fixture.get("home"), fixture.get("away"),
                                       witness["home"], witness["away"]):
            continue
        kickoff = parse_iso_utc(witness["kickoff_utc"])
        observed = parse_iso_utc(witness["observed_at_utc"])
        # Separate repeated fixtures on other dates; not a team-only join.
        if kickoff is None or abs((kickoff.date() - date.fromisoformat(raw_date)).days) > 1:
            continue
        if observed is None or observed >= kickoff:
            continue
        if observed >= cutoff:
            out["late_witness_records"] += 1
            continue
        matches.append(witness)
    if not matches:
        out["reason"] = "no_independent_pre_cutoff_witness"
        return out
    # Never choose whichever provider/observation happens to fit our hypothesis.
    if len({w["kickoff_utc"] for w in matches}) != 1:
        out["reason"] = "conflicting_schedule_witnesses"
        out["witnesses"] = matches
        return out
    accepted = []
    modes = set()
    for witness in matches:
        for assumed, label in interpretations:
            result = corroborate_kickoff_witness(
                fixture.get("kickoff"), witness["kickoff_utc"],
                witness_source=witness["source"], assumed_fixture_utc=assumed,
                fixture_home=fixture.get("home"), fixture_away=fixture.get("away"),
                witness_home=witness["home"], witness_away=witness["away"],
                tolerance_minutes=5.0)
            if result["corroborated"]:
                if witness not in accepted:
                    accepted.append(witness)
                modes.add(label)
    if not accepted:
        out["reason"] = "page_clock_witness_disagreement"
        out["witnesses"] = matches
        return out
    out.update(status="corroborated", reason="independent_pre_cutoff_schedule_witness",
               kickoff_utc=accepted[0]["kickoff_utc"],
               provenance="witness_corroborated_aware_iso", witnesses=accepted,
               interpretations=sorted(modes))
    return out


def audit_detail_files(*, corroborate_schedules: bool = True) -> dict:
    files = sorted(LOCALDATA.glob("betexplorer_match_detail_*.json"))
    documents, detail_receipts = [], []
    for path in files:
        raw_document = path.read_bytes()
        documents.append((path, json.loads(raw_document)))
        detail_receipts.append({"file": path.name, "sha256": hashlib.sha256(raw_document).hexdigest()})
    witnesses, archive_receipts = ({}, [])
    if corroborate_schedules:
        witnesses, archive_receipts = load_schedule_witnesses(
            [fix for _, doc in documents for fix in doc.get("fixtures", {}).values()])
    report = {
        "scope": "read_only_capture_time_replay_screen",
        "live_quote_activation": False,
        "witness_corroboration": {"enabled": corroborate_schedules,
                                  "archives": archive_receipts, "resolution_counts": {}},
        "capture_valid_named_rows": 0,
        "capture_valid_named_rows_by_market": {m: 0 for m in MARKET_EXPECTED_WIDTHS},
        "files_count": len(files),
        "detail_files": detail_receipts,
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
            "ineligible_post_cutoff_capture": 0,   # verified kickoff > cutoff, but captured >= cutoff
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
    for f, data in documents:
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

            cutoff_dt = decision_cutoff_utc(date_str)
            raw_ko_prov = ko_prov
            # Keep diagnostic bare-clock calculations separate from resolved time.
            diagnostic_kickoff = kickoff_dt
            resolution = {"status": "not_attempted", "reason": ("direct_aware_kickoff" if cutoff_dt else "invalid_decision_date"),
                          "witnesses": [], "interpretations": []}
            if ko_prov != "verified_aware_iso" and cutoff_dt is not None:
                if corroborate_schedules:
                    resolution = resolve_schedule_witness(fix, cutoff_dt, witnesses)
                    if resolution["status"] == "corroborated":
                        kickoff_dt = parse_iso_utc(resolution["kickoff_utc"])
                        ko_prov = "witness_corroborated_aware_iso"
                else:
                    resolution["reason"] = "witness_resolution_disabled"
            reasons = report["witness_corroboration"]["resolution_counts"]
            reasons[resolution["reason"]] = reasons.get(resolution["reason"], 0) + 1

            # Authoritative eligibility determination
            if capture_status == "invalid" or captured_dt is None or cutoff_dt is None:
                auth_status = "invalid_timestamp"
            elif ko_prov not in ("verified_aware_iso", "witness_corroborated_aware_iso"):
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
            if capture_status == "invalid" or captured_dt is None or diagnostic_kickoff is None or cutoff_dt is None:
                diag_status = "invalid_timestamp"
            elif captured_dt >= diagnostic_kickoff:
                diag_status = "post_kickoff"
            elif captured_dt < cutoff_dt:
                if cutoff_dt < diagnostic_kickoff:
                    diag_status = "pre_cutoff_upcoming"
                else:
                    diag_status = "pre_cutoff_started_before_cutoff"
            else:
                diag_status = "post_cutoff_pre_kickoff"

            report["diagnostic_assumed_utc_breakdown"][diag_status] += 1

            # Capture-time screening only: not price/line/execution admission.
            capture_valid_rows = []
            for mkt_slug, mkt_data in mkts.items():
                if not isinstance(mkt_data, dict):
                    continue
                rows = mkt_data.get("rows") or []
                for row_index, row in enumerate(rows):
                    report["named_book_inspection"]["total_quotes_checked"] += 1
                    is_valid, reason = validate_quote_row(mkt_slug, row)
                    if is_valid:
                        report["named_book_inspection"]["valid_named_quotes"] += 1
                        if auth_status == "eligible_pre_match_decision" and mkt_slug in MARKET_EXPECTED_WIDTHS:
                            report["capture_valid_named_rows"] += 1
                            report["capture_valid_named_rows_by_market"][mkt_slug] += 1
                            capture_valid_rows.append({"market": mkt_slug, "row_index": row_index,
                                                       "bookmaker": row["bookmaker"], "line": row.get("line"),
                                                       "odds": row["odds"]})
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
            verified_ko_utc = kickoff_dt.isoformat() if (ko_prov in ("verified_aware_iso", "witness_corroborated_aware_iso") and kickoff_dt) else None

            report["fixtures"].append({
                "file": f.name,
                "fixture_key": k,
                "home": fix.get("home"),
                "away": fix.get("away"),
                "capture_status": capture_status,
                "kickoff_provenance": ko_prov,
                "raw_kickoff_provenance": raw_ko_prov,
                "decision_cutoff_utc": cutoff_dt.isoformat() if cutoff_dt else None,
                "kickoff_resolution": resolution,
                "capture_valid_quote_rows": capture_valid_rows,
                "authoritative_eligibility": auth_status,
                "diagnostic_assumed_utc_timing": diag_status,
                "captured_utc": captured_dt.isoformat() if captured_dt else None,
                "kickoff_utc": verified_ko_utc
            })

    report["unique_fixture_keys"] = len(seen_keys)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the complete audit and witness receipts")
    parser.add_argument("--no-witnesses", action="store_true", help="Reproduce the Phase 1 baseline")
    args = parser.parse_args()
    rep = audit_detail_files(corroborate_schedules=not args.no_witnesses)
    if args.json:
        print(json.dumps(rep, indent=2, sort_keys=True))
        raise SystemExit(0)
    print(f"Audited {rep['files_count']} files:")
    print(f"  Total Fixtures: {rep['total_fixtures']} (Unique: {rep['unique_fixture_keys']})")
    print(f"  Kickoff Provenance: {rep['kickoff_provenance']}")
    print(f"  Authoritative Eligibility: {rep['authoritative_eligibility']}")
    print(f"  Diagnostic Assumed-UTC Breakdown: {rep['diagnostic_assumed_utc_breakdown']}")
    print(f"  Capture Provenance: {rep['capture_provenance']}")
    print(f"  Named Quote Inspection: {rep['named_book_inspection']}")
    print(f"  Witness Resolution: {rep['witness_corroboration']['resolution_counts']}")
    print(f"  Capture-valid Named Rows (NOT live admission): {rep['capture_valid_named_rows']}")
