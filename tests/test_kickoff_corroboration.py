"""Adversarial unit tests for kickoff corroboration and timezone interpretation."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pytest

from edgefactory.kickoff_corroboration import (
    interpret_betexplorer_data_dt,
    corroborate_kickoff_witness,
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


def test_interpret_invalid_data_dt():
    dt, reason = interpret_betexplorer_data_dt([])
    assert dt is None and reason == "invalid_shape"

    dt, reason = interpret_betexplorer_data_dt([21, 10, 2026])
    assert dt is None and reason == "invalid_shape"

    dt, reason = interpret_betexplorer_data_dt([99, 99, 2026, 99, 99])
    assert dt is None and reason == "invalid_date_values"


def test_corroborate_circular_rejection():
    # BetExplorer cannot witness itself
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="betexplorer",
        fixture_source="betexplorer"
    )
    assert res["corroborated"] is False
    assert res["reason"] == "circular_corroboration_rejected"
    assert res["authoritative_kickoff_utc"] is None


def test_corroborate_naive_witness_rejection():
    # Naive timestamp without explicit timezone must be rejected
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21 19:00:00",
        witness_source="independent_feed"
    )
    assert res["corroborated"] is False
    assert res["reason"] == "witness_kickoff_naive"


def test_corroborate_tolerance_exceeded():
    # Inferred clock is 19:00 UTC, but witness says 18:00 UTC (60 min diff > 5 min tolerance)
    assumed_utc = datetime(2026, 10, 21, 19, 0, 0, tzinfo=TZ_UTC)
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T18:00:00Z",
        witness_source="theoddsapi",
        tolerance_minutes=5.0,
        assumed_fixture_utc=assumed_utc
    )
    assert res["corroborated"] is False
    assert "tolerance_exceeded" in res["reason"]


def test_corroborate_valid_witness():
    # Match within tolerance from independent source (theoddsapi)
    assumed_utc = datetime(2026, 10, 21, 19, 0, 0, tzinfo=TZ_UTC)
    res = corroborate_kickoff_witness(
        fixture_clock="20:00",
        witness_kickoff_utc="2026-10-21T19:00:00Z",
        witness_source="theoddsapi",
        tolerance_minutes=5.0,
        assumed_fixture_utc=assumed_utc
    )
    assert res["corroborated"] is True
    assert res["provenance"] == "witness_corroborated_aware_iso"
    assert res["authoritative_kickoff_utc"] == "2026-10-21T19:00:00+00:00"
