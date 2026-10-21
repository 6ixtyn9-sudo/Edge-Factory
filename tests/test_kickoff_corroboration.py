"""Adversarial unit tests for kickoff corroboration and timezone interpretation."""
from datetime import datetime, timezone
import pytest

from edgefactory.kickoff_corroboration import (
    interpret_betexplorer_data_dt,
    corroborate_kickoff_witness,
    verify_fixture_identity,
    TZ_UTC
)


def test_interpret_fixed_utc_plus_1_vs_europe_prague_dst():
    # On 2026-10-21:
    # Europe/Prague is in Central European Summer Time (CEST, UTC+2).
    # Fixed UTC+1 is UTC+1.
    # Therefore, a 20:00 page clock translates to:
    #   - fixed UTC+1: 19:00 UTC
    #   - Europe/Prague: 18:00 UTC
    data_dt = [21, 10, 2026, 20, 0]

    utc_fixed, mode_fixed = interpret_betexplorer_data_dt(data_dt, mode="fixed_utc_plus_1")
    assert mode_fixed == "inferred_fixed_utc_plus_1"
    assert utc_fixed == datetime(2026, 10, 21, 19, 0, 0, tzinfo=TZ_UTC)

    utc_prague, mode_prague = interpret_betexplorer_data_dt(data_dt, mode="europe_prague")
    assert mode_prague == "inferred_europe_prague"
    assert utc_prague == datetime(2026, 10, 21, 18, 0, 0, tzinfo=TZ_UTC)

    # Prove they differ by exactly 1 hour on 21 October 2026
    diff_hours = (utc_fixed - utc_prague).total_seconds() / 3600.0
    assert diff_hours == 1.0


def test_interpret_date_rollover():
    # 00:30 on 21 Oct in UTC+1 translates to 23:30 on 20 Oct UTC
    data_dt = [21, 10, 2026, 0, 30]
    utc_fixed, _ = interpret_betexplorer_data_dt(data_dt, mode="fixed_utc_plus_1")
    assert utc_fixed == datetime(2026, 10, 20, 23, 30, 0, tzinfo=TZ_UTC)


def test_interpret_dst_gap_and_fold():
    # In Europe/Prague in 2026:
    # Spring forward: 2026-03-29 02:00 -> 03:00 (02:30 does not exist!)
    gap_dt = [29, 3, 2026, 2, 30]
    dt_gap, reason_gap = interpret_betexplorer_data_dt(gap_dt, mode="europe_prague")
    assert dt_gap is None
    assert reason_gap == "dst_gap_nonexistent_local_time"

    # Fall back: 2026-10-25 03:00 -> 02:00 (02:30 is ambiguous!)
    fold_dt = [25, 10, 2026, 2, 30]
    dt_fold, reason_fold = interpret_betexplorer_data_dt(fold_dt, mode="europe_prague")
    assert dt_fold is None
    assert reason_fold == "dst_fold_ambiguous_local_time"


def test_interpret_invalid_data_dt():
    dt, reason = interpret_betexplorer_data_dt([])
    assert dt is None and reason == "invalid_shape"

    dt, reason = interpret_betexplorer_data_dt([21, 10, 2026])
    assert dt is None and reason == "invalid_shape"

    dt, reason = interpret_betexplorer_data_dt([99, 99, 2026, 99, 99])
    assert dt is None and reason == "invalid_date_values"


def test_fixture_identity_matching():
    # Exact match
    assert verify_fixture_identity("Aston Villa", "Viking", "Aston Villa", "Viking") is True
    # Word variants / case insensitive
    assert verify_fixture_identity("Newcastle Utd", "Coventry", "Newcastle United", "Coventry") is True
    # Squad marker mismatch fails closed
    assert verify_fixture_identity("Club Brugge", "Lens", "Club Brugge U23", "Lens") is False
    # Team mismatch fails closed
    assert verify_fixture_identity("Aston Villa", "Viking", "Arsenal", "Viking") is False


def test_corroborate_blocking_findings():
    assumed_utc = datetime(2026, 10, 21, 19, 0, 0, tzinfo=TZ_UTC)

    # 1. Missing comparison instant fails closed
    res = corroborate_kickoff_witness(
        fixture_clock="garbage",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="theoddsapi",
        assumed_fixture_utc=None,
        fixture_home="Aston Villa", fixture_away="Viking",
        witness_home="Aston Villa", witness_away="Viking"
    )
    assert res["corroborated"] is False
    assert res["reason"] == "missing_comparison_instant"

    # 2. Lineage family aliases (betexplorer_odds vs betexplorer) are recognized and rejected as circular
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="betexplorer_odds",
        fixture_source="betexplorer",
        assumed_fixture_utc=assumed_utc,
        fixture_home="Aston Villa", fixture_away="Viking",
        witness_home="Aston Villa", witness_away="Viking"
    )
    assert res["corroborated"] is False
    assert res["reason"] == "circular_corroboration_rejected"

    # Whitespace-only witness source fails closed
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="   ",
        assumed_fixture_utc=assumed_utc,
        fixture_home="Aston Villa", fixture_away="Viking",
        witness_home="Aston Villa", witness_away="Viking"
    )
    assert res["corroborated"] is False
    assert res["reason"] == "invalid_or_empty_witness_source"

    # 3. Missing or mismatched fixture identity fails closed
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="theoddsapi",
        assumed_fixture_utc=assumed_utc,
        fixture_home="Aston Villa", fixture_away="Viking",
        witness_home="Real Madrid", witness_away="RB Leipzig"
    )
    assert res["corroborated"] is False
    assert res["reason"] == "fixture_identity_mismatch"

    # 4. Non-finite or negative tolerance fails closed
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="theoddsapi",
        assumed_fixture_utc=assumed_utc,
        tolerance_minutes=float("nan"),
        fixture_home="Aston Villa", fixture_away="Viking",
        witness_home="Aston Villa", witness_away="Viking"
    )
    assert res["corroborated"] is False
    assert res["reason"] == "invalid_tolerance"

    # 5. Out of tolerance (> 5 min) fails closed
    diff_utc = datetime(2026, 10, 21, 18, 0, 0, tzinfo=TZ_UTC)
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="theoddsapi",
        assumed_fixture_utc=diff_utc,
        tolerance_minutes=5.0,
        fixture_home="Aston Villa", fixture_away="Viking",
        witness_home="Aston Villa", witness_away="Viking"
    )
    assert res["corroborated"] is False
    assert "tolerance_exceeded" in res["reason"]

    # 6. Valid independent corroboration succeeds
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="theoddsapi",
        assumed_fixture_utc=assumed_utc,
        tolerance_minutes=5.0,
        fixture_home="Aston Villa", fixture_away="Viking",
        witness_home="Aston Villa", witness_away="Viking"
    )
    assert res["corroborated"] is True
    assert res["provenance"] == "witness_corroborated_aware_iso"
    assert res["authoritative_kickoff_utc"] == "2026-10-21T19:00:00+00:00"
    assert res["witness_family"] == "theoddsapi"
