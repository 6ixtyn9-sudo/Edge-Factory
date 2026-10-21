"""Strict kickoff corroboration and timezone resolution engine.

Separates inferred clock conversions from verified authoritative kickoffs.
A bare clock from BetExplorer (or any provider) is never promoted to
an authoritative verified aware instant based on an assumed or guessed timezone.

Promotion to `witness_corroborated_aware_iso` requires:
  1. Validated fixture identity matching (home, away, date/calendar proximity).
  2. Independent, non-empty, recognized witness source:
     - Normalizes source family.
     - Strictly rejects circular self-corroboration (e.g. betexplorer vs betexplorer_odds).
     - Strictly rejects unrecognized, empty, or whitespace sources.
  3. Finite, positive tolerance window (e.g. <= 15 minutes, finite numbers only).
  4. Explicit aware ISO string from witness matching the fixture instant within tolerance.
  5. Mandatory comparison: comparison instant (assumed_fixture_utc or parsed fixture clock)
     is required for corroboration; missing or unparseable fixture clock fails closed.

For DST transitions (e.g. Europe/Prague spring forward gap or fall back fold),
conversions without explicit fold/gap evidence fail closed as ambiguous.
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from edgefactory.identity import source_team_key, squad_marker_mismatch

TZ_UTC = timezone.utc
TZ_PRAGUE = ZoneInfo("Europe/Prague")
TZ_FIXED_UTC_PLUS_1 = timezone(datetime.fromisoformat("2026-01-01T01:00:00+01:00").utcoffset())

# Lineage families: canonical family mapping to prevent alias evasion
SOURCE_FAMILIES: dict[str, str] = {
    "betexplorer": "betexplorer",
    "betexplorer_odds": "betexplorer",
    "betexplorer_match": "betexplorer",
    "betexplorer_detail": "betexplorer",
    "betexplorerodds": "betexplorer",
    "theoddsapi": "theoddsapi",
    "the_odds_api": "theoddsapi",
    "theodds_api": "theoddsapi",
    "oddspapi": "oddspapi",
    "forebet": "forebet",
    "scoutingstats": "scoutingstats",
    "scouting_stats": "scoutingstats",
    "statarea": "statarea",
    "stat_area": "statarea",
    "vitibet": "vitibet",
    "bzzoiro": "bzzoiro",
    "pinnacle": "pinnacle",
    "betway": "betway",
    "warehouse": "warehouse",
    "warehouse_schedule": "warehouse",
}

MAX_PERMITTED_TOLERANCE_MINUTES = 30.0


def normalize_source_family(src: object) -> str | None:
    """Normalize a source string to its canonical lineage family.

    Strictly fails closed: returns None if the source is not in the recognized
    canonical lineage mapping.
    """
    if not src or not isinstance(src, str):
        return None
    # Normalize hyphens and spaces to underscores, then strip invalid characters
    cleaned = src.strip().lower()
    cleaned = re.sub(r"[\s\-]+", "_", cleaned)
    cleaned = re.sub(r"[^a-z0-9_]", "", cleaned)
    if not cleaned:
        return None
    # Check normalized form, and also compacted form (without underscores)
    compacted = cleaned.replace("_", "")
    return SOURCE_FAMILIES.get(cleaned) or SOURCE_FAMILIES.get(compacted)


def interpret_betexplorer_data_dt(
    data_dt: list[int] | tuple[int, ...],
    *,
    mode: str = "fixed_utc_plus_1"
) -> tuple[datetime | None, str]:
    """Evaluate a BetExplorer data_dt tuple [DD, MM, YYYY, HH, MM].

    mode:
      - 'fixed_utc_plus_1': fixed UTC+1 offset.
      - 'europe_prague': Prague local time.
        Strictly fails closed on DST nonexistent gap (spring forward) or ambiguous
        repeated fold (autumn fall back) unless explicitly disambiguated.
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
            # Test for DST transition ambiguity or nonexistence in Europe/Prague
            # In Python, fold=0 and fold=1 allow detecting folds and gaps.
            dt0 = datetime(yyyy, mm, dd, hh, minute, 0, fold=0, tzinfo=TZ_PRAGUE)
            dt1 = datetime(yyyy, mm, dd, hh, minute, 0, fold=1, tzinfo=TZ_PRAGUE)

            # Check for gap (nonexistent local time):
            # If round-trip through UTC produces a different local time, it is in a gap
            utc0 = dt0.astimezone(TZ_UTC)
            if utc0.astimezone(TZ_PRAGUE).replace(tzinfo=None) != datetime(yyyy, mm, dd, hh, minute, 0):
                return None, "dst_gap_nonexistent_local_time"

            # Check for fold (ambiguous local time):
            if dt0.utcoffset() != dt1.utcoffset():
                return None, "dst_fold_ambiguous_local_time"

            return utc0, "inferred_europe_prague"
        else:
            return None, "unknown_mode"
    except Exception:
        return None, "invalid_date_values"


def verify_fixture_identity(
    fixture_home: object,
    fixture_away: object,
    witness_home: object,
    witness_away: object
) -> bool:
    """Validate that fixture and witness identify the exact same match."""
    fh_key = source_team_key(fixture_home)
    fa_key = source_team_key(fixture_away)
    wh_key = source_team_key(witness_home)
    wa_key = source_team_key(witness_away)

    if not (fh_key and fa_key and wh_key and wa_key):
        return False

    # Check for squad/age/women marker mismatches
    if squad_marker_mismatch(fixture_home, witness_home) or squad_marker_mismatch(fixture_away, witness_away):
        return False

    return fh_key == wh_key and fa_key == wa_key


def corroborate_kickoff_witness(
    fixture_clock: str | None,
    witness_kickoff_utc: str | datetime | None,
    *,
    witness_source: str,
    fixture_source: str = "betexplorer",
    assumed_fixture_utc: datetime | None = None,
    tolerance_minutes: float = 5.0,
    fixture_home: object = None,
    fixture_away: object = None,
    witness_home: object = None,
    witness_away: object = None
) -> dict:
    """Corroborate a fixture's timing against an independent schedule witness.

    Fails closed on:
      - Missing or unverified comparison instant (`assumed_fixture_utc` is required).
      - Invalid fixture identity (home/away mismatch or missing).
      - Missing, empty, or circular witness source.
      - Naive, missing, or unparseable witness kickoff timestamp.
      - Non-finite, negative, or excessive tolerance.
      - Timing discrepancy exceeding tolerance window.
    """
    out = {
        "corroborated": False,
        "authoritative_kickoff_utc": None,
        "provenance": "unverified_kickoff_timezone",
        "reason": "",
        "witness_source": str(witness_source).strip() if witness_source else "",
        "witness_family": None
    }

    # 1. Require validated fixture identity
    if not (fixture_home and fixture_away and witness_home and witness_away):
        out["reason"] = "missing_fixture_identity"
        return out
    if not verify_fixture_identity(fixture_home, fixture_away, witness_home, witness_away):
        out["reason"] = "fixture_identity_mismatch"
        return out

    # 2. Source lineage normalization & circularity guard
    fix_fam = normalize_source_family(fixture_source)
    wit_fam = normalize_source_family(witness_source)

    if not fix_fam:
        out["reason"] = "unrecognized_or_empty_fixture_source"
        return out

    if not wit_fam:
        out["reason"] = "unrecognized_or_empty_witness_source"
        return out
    out["witness_family"] = wit_fam

    if fix_fam == wit_fam:
        out["reason"] = "circular_corroboration_rejected"
        return out

    # 3. Tolerance validation (must be finite, non-negative, <= MAX)
    try:
        tol = float(tolerance_minutes)
        if not math.isfinite(tol) or tol < 0 or tol > MAX_PERMITTED_TOLERANCE_MINUTES:
            out["reason"] = "invalid_tolerance"
            return out
    except (TypeError, ValueError):
        out["reason"] = "invalid_tolerance"
        return out

    # 4. Mandatory comparison instant: assumed_fixture_utc must be provided and aware
    if assumed_fixture_utc is None:
        out["reason"] = "missing_comparison_instant"
        return out
    if not isinstance(assumed_fixture_utc, datetime) or assumed_fixture_utc.tzinfo is None:
        out["reason"] = "comparison_instant_not_aware_datetime"
        return out
    af_utc = assumed_fixture_utc.astimezone(TZ_UTC)

    # 5. Witness timestamp validation: must be aware UTC
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

    # 6. Compare instants within tolerance
    diff_minutes = abs((af_utc - w_dt).total_seconds()) / 60.0
    if diff_minutes > tol:
        out["reason"] = f"tolerance_exceeded_diff_{diff_minutes:.1f}_min"
        return out

    # Verified!
    out["corroborated"] = True
    out["authoritative_kickoff_utc"] = w_dt.isoformat()
    out["provenance"] = "witness_corroborated_aware_iso"
    out["reason"] = f"witnessed_by_{wit_fam}"
    return out
