"""Strict kickoff corroboration and timezone resolution engine.

Separates inferred clock conversions from verified authoritative kickoffs.
A bare clock from BetExplorer (or any provider) is never promoted to
an authoritative verified aware instant based on an assumed or guessed timezone.

Promotion to `verified_aware_iso` requires:
  1. An explicit aware ISO string directly from the source, OR
  2. Independent schedule witness corroboration: an aware UTC kickoff from an
     independent authoritative source (e.g. TheOddsAPI, Forebet, warehouse schedule)
     matching the fixture event within a strict tolerance window (+/- 5 minutes),
     guarded against circular self-corroboration.

When only an assumed or observed offset is evaluated (e.g. fixed UTC+1 vs Europe/Prague DST),
it is classified strictly as `inferred_unverified_offset` for research/diagnostics,
never as authoritative decision-time truth.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TZ_UTC = timezone.utc
TZ_PRAGUE = ZoneInfo("Europe/Prague")
TZ_FIXED_UTC_PLUS_1 = timezone(datetime.fromisoformat("2026-01-01T01:00:00+01:00").utcoffset())


def interpret_betexplorer_data_dt(data_dt: list[int] | tuple[int, ...], *, mode: str = "fixed_utc_plus_1") -> tuple[datetime | None, str]:
    """Evaluate a BetExplorer data_dt tuple [DD, MM, YYYY, HH, MM].

    mode:
      - 'fixed_utc_plus_1': fixed UTC+1 offset (measured on default cookie my_timezone=+1).
      - 'europe_prague': Prague local time (incorporates Central European Summer Time UTC+2).

    Returns (datetime in UTC, interpretation_label).
    NOTE: These conversions are strictly inferred; they are NOT authoritative proof
    unless independently witnessed.
    """
    if not isinstance(data_dt, (list, tuple)) or len(data_dt) != 5:
        return None, "invalid_shape"

    dd, mm, yyyy, hh, minute = data_dt
    try:
        if mode == "fixed_utc_plus_1":
            local_dt = datetime(yyyy, mm, dd, hh, minute, 0, tzinfo=TZ_FIXED_UTC_PLUS_1)
            utc_dt = local_dt.astimezone(TZ_UTC)
            return utc_dt, "inferred_fixed_utc_plus_1"
        elif mode == "europe_prague":
            local_dt = datetime(yyyy, mm, dd, hh, minute, 0, tzinfo=TZ_PRAGUE)
            utc_dt = local_dt.astimezone(TZ_UTC)
            return utc_dt, "inferred_europe_prague"
        else:
            return None, "unknown_mode"
    except Exception:
        return None, "invalid_date_values"


def corroborate_kickoff_witness(
    fixture_clock: str | None,
    witness_kickoff_utc: str | datetime | None,
    *,
    witness_source: str,
    fixture_source: str = "betexplorer",
    tolerance_minutes: float = 5.0,
    assumed_fixture_utc: datetime | None = None
) -> dict:
    """Corroborate a fixture's timing against an independent schedule witness.

    Guards:
      - Rejects circular corroboration (witness_source == fixture_source).
      - Rejects naive bookmaker / derivative feeds claiming to witness themselves.
      - Requires witness_kickoff_utc to be an aware instant.
    """
    out = {
        "corroborated": False,
        "authoritative_kickoff_utc": None,
        "provenance": "unverified_kickoff_timezone",
        "reason": "",
        "witness_source": witness_source,
    }

    if not witness_source or witness_source.strip().lower() == fixture_source.strip().lower():
        out["reason"] = "circular_corroboration_rejected"
        return out

    if witness_kickoff_utc is None:
        out["reason"] = "witness_kickoff_missing"
        return out

    w_dt: datetime | None = None
    if isinstance(witness_kickoff_utc, datetime):
        if witness_kickoff_utc.tzinfo is None:
            out["reason"] = "witness_kickoff_naive"
            return out
        w_dt = witness_kickoff_utc.astimezone(TZ_UTC)
    elif isinstance(witness_kickoff_utc, str):
        try:
            parsed = datetime.fromisoformat(witness_kickoff_utc.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                out["reason"] = "witness_kickoff_naive"
                return out
            w_dt = parsed.astimezone(TZ_UTC)
        except Exception:
            out["reason"] = "witness_kickoff_unparseable"
            return out
    else:
        out["reason"] = "witness_kickoff_invalid_type"
        return out

    if assumed_fixture_utc is not None:
        if assumed_fixture_utc.tzinfo is None:
            out["reason"] = "assumed_fixture_utc_naive"
            return out
        diff_minutes = abs((assumed_fixture_utc.astimezone(TZ_UTC) - w_dt).total_seconds()) / 60.0
        if diff_minutes > tolerance_minutes:
            out["reason"] = f"tolerance_exceeded_diff_{diff_minutes:.1f}_min"
            return out

    out["corroborated"] = True
    out["authoritative_kickoff_utc"] = w_dt.isoformat()
    out["provenance"] = "witness_corroborated_aware_iso"
    out["reason"] = f"witnessed_by_{witness_source}"
    return out
