from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from edgefactory import phase5_shadow as shadow


def _prediction(day: str, home: str = "North FC U21", away: str = "South United U19") -> dict:
    return {
        "date": day,
        "kickoff": f"{day}T18:30:00+02:00",
        "home": home,
        "away": away,
        "league": "Test League",
        "p1": 82,
        "px": 10,
        "p2": 8,
        "tip": "1",
        "captured_at": "2026-10-07T12:00:00Z",
    }


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_normalizes_marker_aware_identity_probabilities_and_capture_timestamp(tmp_path):
    rows = shadow.append_shadow_rows(
        "vitibet",
        [_prediction("2026-10-08")],
        capture_day="2026-10-07",
        requested_day="2026-10-08",
        root=tmp_path,
    )

    assert rows == {
        "rows_seen": 1,
        "rows_appended": 1,
        "rows_bytes_appended": (tmp_path / shadow.SHADOW_DIR / shadow.ROWS_NAME).stat().st_size,
        "rows_ignored_historical": 0,
        "rows_rejected_identity": 0,
        "rows_rejected_signal": 0,
    }
    [record] = _jsonl(tmp_path / shadow.SHADOW_DIR / shadow.ROWS_NAME)
    assert record["record_type"] == "phase5_shadow_prediction"
    assert record["source"] == "vitibet"
    assert record["capture_day"] == "2026-10-07"
    assert record["capture_context"] == "manual_or_unspecified"
    assert datetime.fromisoformat(record["captured_at"].replace("Z", "+00:00"))
    assert record["source_timestamp"] == "2026-10-07T12:00:00Z"
    assert record["identity"]["home_key"] == shadow.source_team_key("North FC U21")
    assert record["identity"]["home_markers"] == ["u21"]
    assert record["identity"]["away_markers"] == ["u19"]
    assert record["identity"]["orientation"] == "home_away"
    assert record["probabilities_raw"]["1x2.home"] == 82
    assert record["probabilities"]["1x2.home"] == 0.82
    assert record["picks"]["tip"] == "1"
    assert record["kickoff_parse_status"] == "exact_offset"
    assert record["kickoff_at_utc"] == "2026-10-08T16:30:00+00:00"
    assert "stake_pct" not in record and "bank" not in record and "accas" not in record


def test_forward_capture_ignores_history_and_rejects_unusable_rows(tmp_path):
    results = shadow.append_shadow_rows(
        "betclan",
        [
            _prediction("2026-10-06", "History FC", "Past United"),
            _prediction("2026-10-07", "Today FC", "Today United"),
            {"date": "2026-10-08", "home": "Same Team", "away": "Same Team", "p1": 0.8},
            {"date": "2026-10-08", "home": "Signal FC", "away": "Signal United"},
        ],
        capture_day="2026-10-07",
        requested_day="2026-10-06",
        root=tmp_path,
    )

    assert results == {
        "rows_seen": 4,
        "rows_appended": 1,
        "rows_bytes_appended": (tmp_path / shadow.SHADOW_DIR / shadow.ROWS_NAME).stat().st_size,
        "rows_ignored_historical": 1,
        "rows_rejected_identity": 1,
        "rows_rejected_signal": 1,
    }
    records = _jsonl(tmp_path / shadow.SHADOW_DIR / shadow.ROWS_NAME)
    assert [row["identity"]["date"] for row in records] == ["2026-10-07"]


def test_era_pair_key_preserves_the_frozen_section4_identity_boundary(tmp_path):
    rows = shadow.append_shadow_rows(
        "vitibet",
        [_prediction("2026-10-08", home="FC Porto", away="Porto")],
        capture_day="2026-10-07",
        root=tmp_path,
    )
    assert rows["rows_appended"] == 1
    [record] = _jsonl(tmp_path / shadow.SHADOW_DIR / shadow.ROWS_NAME)
    identity = record["identity"]
    # The production source_team_key removes pure club-structure tokens, so it
    # must not be used for the contract's exact §4 era join.
    assert identity["home_key"] == identity["away_key"]
    assert identity["era_pair_key"][1] == "fc porto"
    assert identity["era_pair_key"][3] == "porto"
    assert identity["era_pair_normalizer"] == "FINDINGS-2026-10-07.md#4"


def test_capture_attempt_is_append_only_and_contains_no_headers_or_raw_error(tmp_path):
    first = shadow.append_capture_attempt(
        "bzzoiro",
        capture_day="2026-10-07",
        status="failed",
        started_at="2026-10-07T06:00:00+00:00",
        completed_at="2026-10-07T06:00:01+00:00",
        requested_days=["2026-10-07", "2026-10-08"],
        capture_context="official_daily_pipeline",
        rows_fetched=0,
        rows_bytes_appended=123,
        source_status="auth_or_quota",
        quota_hint="auth_or_quota",
        http_statuses=[403],
        error_classes=["retryable_zero_row"],
        root=tmp_path,
    )
    shadow.append_capture_attempt(
        "bzzoiro", capture_day="2026-10-08", status="ok", root=tmp_path
    )

    records = _jsonl(tmp_path / shadow.SHADOW_DIR / shadow.ATTEMPTS_NAME)
    assert len(records) == 2
    assert records[0]["attempt_id"] == first["attempt_id"]
    assert records[0]["requested_days"] == ["2026-10-07", "2026-10-08"]
    assert records[0]["capture_context"] == "official_daily_pipeline"
    assert records[0]["rows_bytes_appended"] == 123
    assert records[0]["http_statuses"] == [403]
    assert "headers" not in records[0]
    assert "request_headers" not in records[0]
    assert "Authorization" not in json.dumps(records[0])
    assert "RAPIDAPI_KEY" not in json.dumps(records[0])


def test_unapproved_source_is_rejected_even_for_empty_capture(tmp_path):
    with pytest.raises(ValueError, match="not authorized"):
        shadow.append_shadow_rows(
            "forebet", [], capture_day="2026-10-07", root=tmp_path
        )
    with pytest.raises(ValueError, match="not authorized"):
        shadow.append_capture_attempt(
            "forebet", capture_day="2026-10-07", status="ok", root=tmp_path
        )


def test_shadow_module_exposes_writers_but_no_reader_api():
    public_callables = {
        name for name, value in vars(shadow).items()
        if callable(value) and not name.startswith("_")
    }
    assert {"append_capture_attempt", "append_shadow_rows"} <= public_callables
    assert not any("read" in name.lower() or "load" in name.lower()
                   for name in public_callables)
