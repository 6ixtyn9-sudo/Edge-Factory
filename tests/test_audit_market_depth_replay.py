"""Adversarial and comprehensive tests for tools/audit_market_depth_replay.py (Phase 1)."""
from datetime import datetime
from zoneinfo import ZoneInfo
from tools.audit_market_depth_replay import (
    audit_detail_files,
    parse_iso_utc,
    parse_kickoff_instant,
    validate_quote_row,
    TZ_UTC
)


def test_parse_iso_utc_adversarial():
    # Valid UTC and offsets
    assert parse_iso_utc("2026-10-21T06:30:00Z") == datetime(2026, 10, 21, 6, 30, tzinfo=TZ_UTC)
    assert parse_iso_utc("2026-10-21T08:30:00+02:00") == datetime(2026, 10, 21, 6, 30, tzinfo=TZ_UTC)
    # Naive strings must be rejected as None (fail-closed)
    assert parse_iso_utc("2026-10-21 06:30:00") is None
    # Invalid strings / malformed / non-string
    assert parse_iso_utc("garbage") is None
    assert parse_iso_utc(None) is None
    assert parse_iso_utc(12345) is None
    assert parse_iso_utc("") is None


def test_parse_kickoff_instant_provenance_and_strict_regex():
    # Full ISO format
    dt, prov = parse_kickoff_instant("2026-10-21", "2026-10-21T18:00:00Z")
    assert dt == datetime(2026, 10, 21, 18, 0, tzinfo=TZ_UTC)
    assert prov == "verified_aware_iso"

    # Bare clock (HH:MM) - must be flagged as unverified_local_clock
    dt, prov = parse_kickoff_instant("2026-10-21", "18:00")
    assert dt == datetime(2026, 10, 21, 18, 0, tzinfo=TZ_UTC)
    assert prov == "unverified_local_clock"

    # Strict regex: partial / garbage clocks like 18:00:garbage must be rejected
    dt, prov = parse_kickoff_instant("2026-10-21", "18:00:garbage")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "99:99")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "invalid")
    assert dt is None and prov == "malformed_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", "")
    assert dt is None and prov == "missing_clock"

    dt, prov = parse_kickoff_instant("2026-10-21", None)
    assert dt is None and prov == "missing_clock"


def test_validate_quote_row_adversarial_including_non_dict():
    # 1. Non-dict row must receive explicit row_not_dict reason
    ok, reason = validate_quote_row("1x2", "not_a_dict")
    assert ok is False and reason == "row_not_dict"

    ok, reason = validate_quote_row("1x2", None)
    assert ok is False and reason == "row_not_dict"

    # 2. Valid 1X2 row
    valid_row = {"bookmaker": "BetMGM", "odds": [1.5, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", valid_row)
    assert ok is True and reason == "valid"

    # 3. Empty odds list must be REJECTED
    empty_row = {"bookmaker": "BetMGM", "odds": []}
    ok, reason = validate_quote_row("1x2", empty_row)
    assert ok is False and reason == "empty_odds_list"

    # 4. Scalar odds (non-list) must be REJECTED, not raise TypeError
    scalar_row = {"bookmaker": "BetMGM", "odds": 1.5}
    ok, reason = validate_quote_row("1x2", scalar_row)
    assert ok is False and reason == "odds_not_list"

    # 5. Incomplete market (width mismatch) must be REJECTED
    incomplete_dc = {"bookmaker": "BetMGM", "odds": [1.15]} # DC requires 3 columns
    ok, reason = validate_quote_row("dc", incomplete_dc)
    assert ok is False and reason.startswith("width_mismatch")

    # 6. Missing / whitespace bookmaker name must be REJECTED
    missing_book = {"bookmaker": "   ", "odds": [1.5, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", missing_book)
    assert ok is False and reason == "missing_bookmaker"

    # 7. Non-finite / string / <= 1 odds must be REJECTED
    nan_row = {"bookmaker": "BetMGM", "odds": [1.5, float("nan"), 5.0]}
    ok, reason = validate_quote_row("1x2", nan_row)
    assert ok is False and reason == "non_finite_odds"

    le1_row = {"bookmaker": "BetMGM", "odds": [1.0, 3.2, 5.0]}
    ok, reason = validate_quote_row("1x2", le1_row)
    assert ok is False and reason == "odds_le_1"


def test_audit_detail_files_authoritative_vs_diagnostic():
    rep = audit_detail_files()
    assert rep["files_count"] == 10
    assert rep["total_fixtures"] == 116
    assert rep["unique_fixture_keys"] == 116

    # Verify kickoff provenance is explicitly tracked as unverified_local_clock (116)
    assert rep["kickoff_provenance"]["unverified_local_clock"] == 116
    assert rep["kickoff_provenance"]["verified_aware_iso"] == 0

    # CRITICAL: Authoritative eligibility must be fail-closed!
    # Because all 116 stored kickoffs are unverified clocks, ZERO fixtures are authoritatively eligible
    auth = rep["authoritative_eligibility"]
    assert auth["eligible_pre_match_decision"] == 0
    assert auth["unverified_kickoff_timezone"] == 116

    # Diagnostic assumed-UTC counts are strictly preserved as diagnostic only
    diag = rep["diagnostic_assumed_utc_breakdown"]
    assert diag["pre_cutoff_upcoming"] == 57
    assert diag["pre_cutoff_started_before_cutoff"] == 9
    assert diag["post_cutoff_pre_kickoff"] == 45
    assert diag["post_kickoff"] == 5
    assert sum(diag.values()) == 116

    # Fixture objects must NOT expose an unverified clock as authoritative kickoff_utc
    for fix in rep["fixtures"]:
        assert fix["kickoff_utc"] is None
        assert fix["authoritative_eligibility"] == "unverified_kickoff_timezone"

    # Verify capture provenance
    assert rep["capture_provenance"]["fixture_timestamp"] == 116
    assert rep["capture_provenance"]["file_fallback"] == 0

    # Verify quote row inspection
    named = rep["named_book_inspection"]
    assert named["total_quotes_checked"] == 5217
    assert named["valid_named_quotes"] == 5203
    assert named["row_not_dict"] == 0
    assert named["missing_bookmaker"] == 0
    assert named["empty_odds_list"] == 0
    assert named["odds_not_list"] == 0
    assert named["non_finite_odds"] == 14


def test_authoritative_eligibility_synthetic_branches(tmp_path, monkeypatch):
    import json
    from tools import audit_market_depth_replay as amdr

    # Construct synthetic detail payload with aware ISO kickoffs to exercise all authoritative branches
    synthetic_data = {
        "date": "2026-10-21",
        "captured_at": "2026-10-21T06:00:00Z",
        "fixtures": {
            # 1. Eligible: captured 06:00 < cutoff 07:00 < kickoff 12:00
            "fix_eligible": {
                "home": "Team A", "away": "Team B",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T06:00:00Z",
                "markets": {}
            },
            # 2. Ineligible post-cutoff capture: captured 08:00 >= cutoff 07:00, kickoff 12:00
            "fix_post_cutoff": {
                "home": "Team C", "away": "Team D",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T08:00:00Z",
                "markets": {}
            },
            # 3. Exactly at cutoff boundary: captured 07:00 == cutoff 07:00, kickoff 12:00
            "fix_exact_cutoff": {
                "home": "Team E", "away": "Team F",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T07:00:00Z",
                "markets": {}
            },
            # 4. Ineligible already started: kickoff 06:00 <= cutoff 07:00, captured 05:00
            "fix_already_started": {
                "home": "Team G", "away": "Team H",
                "kickoff": "2026-10-21T06:00:00Z",
                "captured_at": "2026-10-21T05:00:00Z",
                "markets": {}
            },
            # 5. Ineligible post kickoff capture: captured 13:00 >= kickoff 12:00
            "fix_post_kickoff": {
                "home": "Team I", "away": "Team J",
                "kickoff": "2026-10-21T12:00:00Z",
                "captured_at": "2026-10-21T13:00:00Z",
                "markets": {}
            }
        }
    }

    mock_file = tmp_path / "betexplorer_match_detail_2026-10-21.json"
    mock_file.write_text(json.dumps(synthetic_data))
    monkeypatch.setattr(amdr, "LOCALDATA", tmp_path)

    rep = amdr.audit_detail_files()
    auth = rep["authoritative_eligibility"]
    assert auth["eligible_pre_match_decision"] == 1
    assert auth["ineligible_post_cutoff_capture"] == 2  # fix_post_cutoff (08:00) and fix_exact_cutoff (07:00)
    assert auth["ineligible_already_started"] == 1      # fix_already_started
    assert auth["ineligible_post_kickoff_capture"] == 1 # fix_post_kickoff
    assert auth["unverified_kickoff_timezone"] == 0


# Phase 2 integrates only existing raw provider archives. Candidate cards are
# deliberately not a witness adapter: their timestamps may derive from BE.
def _schedule_audit(tmp_path, monkeypatch, *, updates=None, rows=None, day="2026-10-21"):
    import csv
    import gzip
    import json
    from tools import audit_market_depth_replay as audit

    fixture = {
        "home": "Aston Villa", "away": "Viking", "kickoff": "20:00",
        "data_dt": [21, 10, 2026, 20, 0], "kickoff_date": "2026-10-21",
        "captured_at": "2026-10-21T06:00:00Z",
        "markets": {"ou": {"rows": [
            {"bookmaker": "Book", "line": "2.5", "odds": [1.8, 2.1]},
            {"bookmaker": "Book", "line": "3.5", "odds": [None, 1.5]},
        ]}},
    }
    fixture.update(updates or {})
    (tmp_path / f"betexplorer_match_detail_{day}.json").write_text(json.dumps(
        {"date": day, "captured_at": "2026-10-21T06:30:00Z", "fixtures": {"event": fixture}}))
    default_row = {
        "source": "oddspapi", "source_type": "odds", "sport": "soccer",
        "home": "Aston Villa", "away": "Viking", "league": "Champions League",
        "kickoff": "2026-10-21T19:00:00Z", "captured_at": "2026-10-21T05:00:00Z",
    }
    rows = [default_row] if rows is None else [dict(default_row, **r) for r in rows]
    for provider in ("oddspapi", "theoddsapi"):
        selected = [r for r in rows if r.get("archive", provider) == provider
                    and (r.get("source") == provider or "archive" in r)]
        if not selected:
            continue
        selected = [{k: v for k, v in r.items() if k != "archive"} for r in selected]
        fields = sorted({k for row in selected for k in row})
        with gzip.open(tmp_path / f"{provider}_odds_2026-10.csv.gz", "wt", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(selected)
    monkeypatch.setattr(audit, "LOCALDATA", tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    report = audit.audit_detail_files()
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    return report


def test_schedule_witness_promotes_with_traceable_receipt(tmp_path, monkeypatch):
    import hashlib
    import json
    rep = _schedule_audit(tmp_path, monkeypatch)
    assert rep["authoritative_eligibility"]["eligible_pre_match_decision"] == 1
    fix, = rep["fixtures"]
    assert fix["kickoff_utc"] == "2026-10-21T19:00:00+00:00"
    assert fix["kickoff_provenance"] == "witness_corroborated_aware_iso"
    resolution = fix["kickoff_resolution"]
    assert resolution["interpretations"] == ["inferred_fixed_utc_plus_1"]
    witness, = resolution["witnesses"]
    path = tmp_path / witness["file"]
    assert witness["file_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert witness["csv_data_row"] == 1 and len(witness["row_sha256"]) == 64
    assert witness["kickoff_origin"] == "provider_startTime"
    assert rep["capture_valid_named_rows"] == 1
    assert rep["capture_valid_named_rows_by_market"]["ou"] == 1
    assert fix["capture_valid_quote_rows"][0]["line"] == "2.5"
    assert rep["named_book_inspection"]["non_finite_odds"] == 1
    assert rep["live_quote_activation"] is False
    assert json.loads((tmp_path / "betexplorer_match_detail_2026-10-21.json").read_text())["fixtures"]["event"]["kickoff"] == "20:00"


def test_schedule_prague_is_a_separate_hypothesis(tmp_path, monkeypatch):
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[{"kickoff": "2026-10-21T18:00:00Z"}])
    fix, = rep["fixtures"]
    assert fix["kickoff_utc"] == "2026-10-21T18:00:00+00:00"
    assert fix["kickoff_resolution"]["interpretations"] == ["inferred_europe_prague"]


def test_schedule_midnight_uses_page_date_not_container_day(tmp_path, monkeypatch):
    rep = _schedule_audit(tmp_path, monkeypatch, day="2026-10-20",
                          updates={"data_dt": [21, 10, 2026, 0, 30], "kickoff": "00:30",
                                   "captured_at": "2026-10-20T05:00:00Z"},
                          rows=[{"kickoff": "2026-10-20T23:30:00Z", "captured_at": "2026-10-20T04:00:00Z"}])
    fix, = rep["fixtures"]
    assert fix["kickoff_utc"] == "2026-10-20T23:30:00+00:00"
    assert fix["authoritative_eligibility"] == "eligible_pre_match_decision"
    assert fix["decision_cutoff_utc"] == "2026-10-20T07:00:00+00:00"


def test_schedule_legacy_missing_tuple_is_not_reconstructed(tmp_path, monkeypatch):
    rep = _schedule_audit(tmp_path, monkeypatch, updates={"data_dt": None, "kickoff_date": None})
    fix, = rep["fixtures"]
    assert fix["kickoff_utc"] is None
    assert fix["kickoff_resolution"]["reason"] == "missing_raw_page_datetime"
    assert fix["authoritative_eligibility"] == "unverified_kickoff_timezone"
    assert rep["capture_valid_named_rows"] == 0


def test_schedule_conflicts_never_pick_the_hypothesis_that_fits(tmp_path, monkeypatch):
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[{}, {"kickoff": "2026-10-21T18:00:00Z"}])
    fix, = rep["fixtures"]
    assert fix["kickoff_resolution"]["reason"] == "conflicting_schedule_witnesses"
    assert fix["kickoff_utc"] is None
    assert rep["capture_valid_named_rows"] == 0


import pytest


@pytest.mark.parametrize("row", [
    {"captured_at": "2026-10-21T07:00:00Z"},
    {"captured_at": "2026-10-21T08:00:00Z"},
    {"captured_at": "garbage"},
    {"captured_at": "2026-10-21T05:00:00"},
    {"kickoff": "2026-10-21T19:00:00"},
    {"home": "Aston Villa U23"},
    {"home": "Arsenal"},
    {"home": "Viking", "away": "Aston Villa"},
    {"source": "betexplorer_odds", "archive": "oddspapi"},
    {"source": "warehouse_schedule", "archive": "oddspapi"},
    {"source": "unknown", "archive": "oddspapi"},
    {"source": "theoddsapi"},  # legacy producer may fall back to pick kickoff
    {"kickoff": "2026-10-22T19:00:00Z"},  # different day's event
])
def test_schedule_unproven_witnesses_fail_closed(tmp_path, monkeypatch, row):
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[row])
    fix, = rep["fixtures"]
    assert fix["kickoff_utc"] is None
    assert rep["authoritative_eligibility"]["eligible_pre_match_decision"] == 0
    assert rep["capture_valid_named_rows"] == 0


def test_schedule_explicit_theoddsapi_origin_can_corroborate(tmp_path, monkeypatch):
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[
        {"source": "theoddsapi", "kickoff_origin": "provider_commence_time",
         "fixture_identity_origin": "provider_participants", "provider_event_id": "test-event-id",
         "provider_commence_time": "2026-10-21T19:00:00Z"}])
    fix, = rep["fixtures"]
    witness, = fix["kickoff_resolution"]["witnesses"]
    assert witness["source"] == "theoddsapi"
    assert rep["capture_valid_named_rows"] == 1


@pytest.mark.parametrize("capture,status", [
    ("2026-10-21T07:00:00Z", "ineligible_post_cutoff_capture"),
    ("2026-10-21T08:00:00Z", "ineligible_post_cutoff_capture"),
    ("2026-10-21T19:00:00Z", "ineligible_post_kickoff_capture"),
    ("garbage", "invalid_timestamp"),
])
def test_schedule_verification_does_not_override_quote_capture(tmp_path, monkeypatch, capture, status):
    rep = _schedule_audit(tmp_path, monkeypatch, updates={"captured_at": capture})
    fix, = rep["fixtures"]
    assert fix["kickoff_utc"] == "2026-10-21T19:00:00+00:00"
    assert fix["authoritative_eligibility"] == status
    assert rep["capture_valid_named_rows"] == 0


@pytest.mark.parametrize("updates", [
    {"kickoff_date": "2026-10-22"},
    {"kickoff": "20:00:garbage"},
    {"data_dt": [21, 10, 2026, 19, 0]},
    {"data_dt": [21, 10, 2026, 99, 0]},
    {"data_dt": [21, 10, 2026, 20]},
    {"data_dt": [True, 10, 2026, 20, 0]},
])
def test_schedule_inconsistent_raw_evidence_fails_closed(tmp_path, monkeypatch, updates):
    rep = _schedule_audit(tmp_path, monkeypatch, updates=updates)
    assert rep["fixtures"][0]["kickoff_utc"] is None
    assert rep["capture_valid_named_rows"] == 0


def test_schedule_late_conflict_is_not_used_as_asof_information(tmp_path, monkeypatch):
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[
        {}, {"kickoff": "2026-10-21T18:00:00Z", "captured_at": "2026-10-21T08:00:00Z"}])
    assert rep["authoritative_eligibility"]["eligible_pre_match_decision"] == 1
    assert rep["fixtures"][0]["kickoff_resolution"]["late_witness_records"] == 1


def test_schedule_cards_alone_do_not_establish_a_witness(tmp_path, monkeypatch):
    import json
    (tmp_path / "picks_today.json").write_text(json.dumps([
        {"home": "Aston Villa", "away": "Viking", "kickoff_utc": "2026-10-21T19:00:00Z",
         "kickoff_source": "derived_sibling_row", "kickoff_witness": "warehouse schedule"}]))
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[])
    assert rep["fixtures"][0]["kickoff_utc"] is None
    assert rep["capture_valid_named_rows"] == 0


@pytest.mark.parametrize("kickoff,eligible", [
    ("2026-10-21T19:05:00Z", True),
    ("2026-10-21T19:05:01Z", False),
])
def test_schedule_tolerance_boundary(tmp_path, monkeypatch, kickoff, eligible):
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[{"kickoff": kickoff}])
    assert rep["authoritative_eligibility"]["eligible_pre_match_decision"] == int(eligible)
    assert rep["capture_valid_named_rows"] == int(eligible)


def test_schedule_source_rows_are_deduplicated_not_votes(tmp_path, monkeypatch):
    rep = _schedule_audit(tmp_path, monkeypatch, rows=[{}, {}, {}])
    fix, = rep["fixtures"]
    assert len(fix["kickoff_resolution"]["witnesses"]) == 1
    assert rep["capture_valid_named_rows"] == 1


def test_schedule_no_witness_mode_preserves_phase1(tmp_path, monkeypatch):
    from tools import audit_market_depth_replay as audit
    _schedule_audit(tmp_path, monkeypatch)
    rep = audit.audit_detail_files(corroborate_schedules=False)
    assert rep["fixtures"][0]["kickoff_utc"] is None
    assert rep["authoritative_eligibility"]["eligible_pre_match_decision"] == 0
    assert rep["capture_valid_named_rows"] == 0
    assert rep["witness_corroboration"]["archives"] == []
