"""Append-only forward shadow capture records for Phase 5.

This module is intentionally a WRITE-ONLY capture seam. It has no loader,
reader, scoring, consensus, or pick-emission API. Operational readers must not
import this module or the ``localdata/phase5_shadow`` files.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from edgefactory.identity import source_team_key
from edgefactory.util import squad_markers

SCHEMA = 1
SHADOW_DIR = "phase5_shadow"
ROWS_NAME = "rows.jsonl"
ATTEMPTS_NAME = "attempts.jsonl"
AUTHORIZED_SOURCES = frozenset({
    "vitibet", "bzzoiro", "betclan", "scoutingstats", "betminer",
})

# The aliases mirror fields already emitted by the five adapters. A field is
# copied only when present; absent probabilities are never filled with zero.
_PROBABILITY_FIELDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("1x2.home", ("p1", "home_probability", "home_prob", "prob_home", "home_win")),
    ("1x2.draw", ("px", "draw_probability", "draw_prob", "prob_draw", "draw")),
    ("1x2.away", ("p2", "away_probability", "away_prob", "prob_away", "away_win")),
    ("1x2.selected", ("1x2_probability",)),
    ("btts.yes", ("p_gg", "btts_yes_probability", "btts_yes_prob", "btts_probability", "btts")),
    ("btts.no", ("p_ng", "btts_no_probability", "btts_no_prob")),
    ("ou_2.5.over", ("p_o25", "over_25_probability", "over_25_prob", "ou_25_probability", "over_25")),
    ("ou_2.5.under", ("p_u25", "under_25_probability", "under_25_prob", "under_25")),
    ("ou_1.5.over", ("p_o15", "over_15_probability", "over_15_prob", "over_15")),
    ("ou_3.5.over", ("p_o35", "over_35_probability", "over_35_prob", "over_35")),
)
_PICK_FIELDS = (
    "1x2_selection", "tip", "winner", "predicted", "rec_winner",
    "rec_bet_favorite", "pick", "selection", "btts_selection",
    "ou_25_selection",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def local_capture_date(now: datetime | None = None) -> str:
    """Return the schedule day in the repo's fixed operator timezone."""
    from zoneinfo import ZoneInfo

    return (now or datetime.now(timezone.utc)).astimezone(
        ZoneInfo("Africa/Johannesburg")
    ).date().isoformat()


def _iso_date(value: object, fallback: str) -> str:
    text = str(value or "")[:10]
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return fallback


def _section4_name_key(value: object) -> str:
    """Reproduce Findings §4's exact name normalizer; no alias/fuzzy path."""
    decomposed = unicodedata.normalize("NFKD", str(value or ""))
    unmarked = "".join(char for char in decomposed if not unicodedata.combining(char))
    normalized = unmarked.replace("&", "and").replace(".", "")
    return " ".join(normalized.casefold().split())


def _as_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip().replace("%", "")
    if not text:
        return None
    try:
        result = float(text)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _normalize_probability(value: object) -> float | None:
    """Use the existing 0-1 / percent convention; invalid values stay absent."""
    result = _as_float(value)
    if result is None:
        return None
    if result > 1.5:
        result /= 100.0
    if result < 0.0 or result > 1.0:
        return None
    return round(result, 10)


def _nested_probability_values(row: dict[str, Any]) -> dict[str, Any]:
    nested = row.get("probabilities_raw")
    if not isinstance(nested, dict):
        nested = row.get("probabilities")
    if isinstance(nested, dict):
        return nested
    return {}


def _lookup_probability(row: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for key in aliases:
        value = row.get(key)
        if value not in (None, ""):
            return value
    nested = _nested_probability_values(row)
    for key in aliases:
        value = nested.get(key)
        if value not in (None, ""):
            return value
    return None


def _kickoff_fields(row: dict[str, Any]) -> tuple[object | None, str | None, str]:
    raw = next((row.get(k) for k in ("kickoff", "starting_at", "start_time", "time")
                if row.get(k) not in (None, "")), None)
    if raw is None:
        return None, None, "missing"
    text = str(raw).strip()
    # Only an explicit offset/Z proves an instant. Never assign a timezone to a
    # naive vendor clock or a bare HH:MM value.
    if not re.search(r"(?:Z|z|[+-]\d{2}:?\d{2})$", text):
        return text, None, "timezone_unresolved"
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text)
    except ValueError:
        return text, None, "invalid"
    if parsed.tzinfo is None:
        return text, None, "timezone_unresolved"
    return text, parsed.astimezone(timezone.utc).isoformat(timespec="seconds"), "exact_offset"


def _source_capture_timestamp(source: str, row: dict[str, Any], captured_at: str | None) -> tuple[str, str | None]:
    """Separate observation time from publisher time.

    BetMiner stamps ``captured_at`` in its parser at response capture. Bzzoiro
    uses the same field for the vendor's ``created_at`` timestamp, so it is
    retained as ``source_timestamp`` and never mislabelled as our capture time.
    """
    source_timestamp = None
    if source == "betminer":
        raw_capture = row.get("captured_at")
        if raw_capture:
            try:
                parsed = datetime.fromisoformat(str(raw_capture).replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc).isoformat(timespec="seconds"), None
            except ValueError:
                pass
    for key in ("created_at", "published_at", "updated_at", "captured_at"):
        value = row.get(key)
        if value not in (None, ""):
            source_timestamp = str(value)
            break
    return captured_at or utc_now(), source_timestamp


def normalize_shadow_row(
    source: str,
    row: dict[str, Any],
    *,
    capture_day: str,
    captured_at: str | None = None,
    requested_day: str | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    """Create one source-tagged, marker-aware shadow row without scoring it."""
    if source not in AUTHORIZED_SOURCES:
        raise ValueError(f"source not authorized for Phase 5 shadow capture: {source}")
    home = str(row.get("home") or "").strip()
    away = str(row.get("away") or "").strip()
    home_key, away_key = source_team_key(home), source_team_key(away)
    home_exact_key, away_exact_key = _section4_name_key(home), _section4_name_key(away)
    home_markers, away_markers = sorted(squad_markers(home)), sorted(squad_markers(away))
    if (
        not home or not away or not home_exact_key or not away_exact_key
        or (home_exact_key, home_markers) == (away_exact_key, away_markers)
    ):
        return None, "identity_unusable"

    raw_probabilities: dict[str, Any] = {}
    probabilities: dict[str, float] = {}
    for path, aliases in _PROBABILITY_FIELDS:
        raw = _lookup_probability(row, aliases)
        if raw in (None, ""):
            continue
        raw_probabilities[path] = raw
        normalized = _normalize_probability(raw)
        if normalized is not None:
            probabilities[path] = normalized

    picks = {key: row.get(key) for key in _PICK_FIELDS
             if row.get(key) not in (None, "")}
    if not probabilities and not picks:
        return None, "no_probability_or_pick"

    fixture_date = _iso_date(row.get("date"), _iso_date(requested_day, capture_day))
    captured_at_value, source_timestamp = _source_capture_timestamp(source, row, captured_at)
    kickoff_raw, kickoff_utc, kickoff_status = _kickoff_fields(row)
    identity = {
        "date": fixture_date,
        "home_key": home_key,
        "home_markers": home_markers,
        "away_key": away_key,
        "away_markers": away_markers,
        "era_pair_key": [
            fixture_date, home_exact_key, home_markers,
            away_exact_key, away_markers,
        ],
        "orientation": "home_away",
        "normalizer": "edgefactory.identity.source_team_key",
        "era_pair_normalizer": "FINDINGS-2026-10-07.md#4",
    }
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "record_type": "phase5_shadow_prediction",
        "source": source,
        "capture_day": capture_day,
        "captured_at": captured_at_value,
        "source_timestamp": source_timestamp,
        "identity": identity,
        "raw_fixture": {"date": fixture_date, "home": home, "away": away},
        "kickoff_raw": kickoff_raw,
        "kickoff_at_utc": kickoff_utc,
        "kickoff_parse_status": kickoff_status,
        "probabilities_raw": raw_probabilities,
        "probabilities": probabilities,
        "picks": picks,
        "source_event_id": next((row.get(k) for k in
                                  ("event_id", "match_id", "fixture_id", "id")
                                  if row.get(k) not in (None, "")), None),
        "league": row.get("league"),
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
    record["row_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return record, None


def _append_jsonl(root: Path, name: str, records: Iterable[dict[str, Any]]) -> tuple[int, int]:
    records = list(records)
    if not records:
        return 0, 0
    directory = Path(root) / SHADOW_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    # These ledgers are append-only and their inode is never replaced, so the
    # file itself is a stable flock target across writers.
    with path.open("a", encoding="utf-8") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        except OSError:
            pass
        bytes_written = 0
        for record in records:
            line = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str) + "\n"
            fh.write(line)
            bytes_written += len(line.encode("utf-8"))
        fh.flush()
        os.fsync(fh.fileno())
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
    return len(records), bytes_written


def append_shadow_rows(
    source: str,
    rows: Iterable[dict[str, Any]] | None,
    *,
    capture_day: str,
    requested_day: str | None = None,
    captured_at: str | None = None,
    root: Path | str,
) -> dict[str, int]:
    """Append valid source predictions; never reads or feeds a production path."""
    if source not in AUTHORIZED_SOURCES:
        raise ValueError(f"source not authorized for Phase 5 shadow capture: {source}")
    capture_day = date.fromisoformat(str(capture_day)[:10]).isoformat()
    row_list = list(rows or [])
    valid: list[dict[str, Any]] = []
    rejected_identity = rejected_signal = ignored_historical = 0
    for row in row_list:
        if not isinstance(row, dict):
            rejected_signal += 1
            continue
        record, reason = normalize_shadow_row(
            source, row, capture_day=capture_day, captured_at=captured_at,
            requested_day=requested_day,
        )
        if record is None:
            if reason == "identity_unusable":
                rejected_identity += 1
            else:
                rejected_signal += 1
            continue
        # The existing daily adapter job includes a 30-day refresh. Do not
        # turn those historical responses into forward shadow observations;
        # fixture date, not request date, is the capture eligibility boundary.
        if record["identity"]["date"] < capture_day:
            ignored_historical += 1
            continue
        valid.append(record)
    appended, bytes_appended = _append_jsonl(Path(root), ROWS_NAME, valid)
    return {
        "rows_seen": len(row_list),
        "rows_appended": appended,
        "rows_bytes_appended": bytes_appended,
        "rows_ignored_historical": ignored_historical,
        "rows_rejected_identity": rejected_identity,
        "rows_rejected_signal": rejected_signal,
    }


def append_capture_attempt(
    source: str,
    *,
    capture_day: str,
    status: str,
    started_at: str | None = None,
    completed_at: str | None = None,
    requested_days: Iterable[str] = (),
    forward_days: Iterable[str] = (),
    capture_context: str = "manual_or_unspecified",
    rows_fetched: int = 0,
    rows_appended: int = 0,
    rows_bytes_appended: int = 0,
    rows_ignored_historical: int = 0,
    rows_rejected_identity: int = 0,
    rows_rejected_signal: int = 0,
    source_status: str | None = None,
    quota_hint: str | None = None,
    http_statuses: Iterable[object] = (),
    error_classes: Iterable[str] = (),
    root: Path | str,
) -> dict[str, Any]:
    """Append a scheduled-attempt event with no request headers or raw errors."""
    if source not in AUTHORIZED_SOURCES:
        raise ValueError(f"source not authorized for Phase 5 shadow capture: {source}")
    capture_day = date.fromisoformat(str(capture_day)[:10]).isoformat()
    capture_context = str(capture_context)
    if capture_context not in {"official_daily_pipeline", "manual_or_unspecified"}:
        capture_context = "other"
    record = {
        "schema": SCHEMA,
        "record_type": "phase5_shadow_capture_attempt",
        "source": source,
        "capture_day": capture_day,
        "capture_context": capture_context,
        "status": str(status),
        "source_status": str(source_status) if source_status else None,
        "quota_hint": str(quota_hint) if quota_hint else None,
        "http_statuses": [int(code) for code in http_statuses
                           if str(code).isdigit()],
        "started_at": started_at or utc_now(),
        "completed_at": completed_at or utc_now(),
        "requested_days": sorted({_iso_date(day, capture_day) for day in requested_days}),
        "forward_days": sorted({_iso_date(day, capture_day) for day in forward_days}),
        "rows_fetched": max(0, int(rows_fetched or 0)),
        "rows_appended": max(0, int(rows_appended or 0)),
        "rows_bytes_appended": max(0, int(rows_bytes_appended or 0)),
        "rows_ignored_historical": max(0, int(rows_ignored_historical or 0)),
        "rows_rejected_identity": max(0, int(rows_rejected_identity or 0)),
        "rows_rejected_signal": max(0, int(rows_rejected_signal or 0)),
        "error_classes": sorted({str(value)[:80] for value in error_classes if value}),
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
    record["attempt_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    _append_jsonl(Path(root), ATTEMPTS_NAME, [record])
    return record
