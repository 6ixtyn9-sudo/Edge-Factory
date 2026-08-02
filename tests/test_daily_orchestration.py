from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "daily.py"
SPEC = importlib.util.spec_from_file_location("daily", SCRIPT)
daily = importlib.util.module_from_spec(SPEC)
sys.modules["daily"] = daily
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(daily)


@patch("daily.run_pipeline")
@patch("daily.archived_picks_file")
def test_run_smart_auto_missing_archive(mock_archived_file, mock_run_pipeline):
    """Test that missing official archive triggers the official morning full run."""
    mock_path = MagicMock()
    mock_path.exists.return_value = False
    mock_archived_file.return_value = mock_path

    with patch("daily.datetime") as mock_dt:
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: "2026-06-18" if "%Y" in fmt else "0600"
        mock_dt.now.return_value.hour = 6

        daily.run_smart_auto(future_days=2, backfill_days=30)

        mock_run_pipeline.assert_called_once_with(
            target_date="2026-06-18",
            mode="official",
            future_days=2,
            backfill_days=30,
            force_repick=False,
            picks_only=False,
        )


@patch("daily.run_pipeline")
@patch("daily.archived_picks_file")
def test_run_smart_auto_existing_archive(mock_archived_file, mock_run_pipeline):
    """Test that existing official archive triggers an autonomous accumulating run."""
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_archived_file.return_value = mock_path

    with patch("daily.datetime") as mock_dt:
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: "2026-06-18" if "%Y" in fmt else "1100"
        mock_dt.now.return_value.hour = 11

        daily.run_smart_auto(future_days=2, backfill_days=30)

        mock_run_pipeline.assert_called_once_with(
            target_date="2026-06-18",
            mode="autonomous_intraday",
            future_days=2,
            backfill_days=30,
            force_repick=True,
            picks_only=True,
        )


@patch("daily.run_soft")
@patch("daily.run")
@patch("daily.generate_daily_report")
@patch("daily.archived_picks_file")
@patch("daily.PICKS_TODAY_FILE")
def test_promote_forecast(mock_picks_today_file, mock_archived_file, mock_gen_report, mock_run, mock_run_soft, tmp_path):
    """Test deliberate promotion of a forecast file to the official record."""
    forecast_file = tmp_path / "forecast_2026-06-18_1100.json"
    dummy_picks = [{"date": "2026-06-18T12:00:00", "home": "Team A", "away": "Team B", "pick": "1"}]
    forecast_file.write_text(json.dumps(dummy_picks))

    mock_archive_dest = MagicMock()
    mock_archived_file.return_value = mock_archive_dest

    daily.promote_forecast(str(forecast_file), "2026-06-18")

    mock_archive_dest.write_text.assert_called_once_with(json.dumps(dummy_picks))
    mock_picks_today_file.write_text.assert_called_once_with(json.dumps(dummy_picks))
    mock_gen_report.assert_called_once_with("2026-06-18")
    mock_run_soft.assert_called()
    assert any("sync_supabase" in call[0][0] for call in mock_run_soft.call_args_list)


def test_autonomous_intraday_merge():
    """Test that existing picks are fully preserved and brand new picks are appended."""
    existing = [
        {
            "date": "2026-06-18T10:00:00",
            "home": "AC Oulu",
            "away": "IFK Mariehamn",
            "market": "1x2",
            "pick": "1",
            "bucket": "CERTIFIED_CLEAN",
            "odds": 1.95,
            "w_score": 0.95,
        }
    ]
    
    fresh = [
        # Duplicate of existing game/market (maybe odds changed or picked X later)
        {
            "date": "2026-06-18T10:00:00",
            "home": "AC Oulu",
            "away": "IFK Mariehamn",
            "market": "1x2",
            "pick": "X",
            "bucket": "CAUTION",
            "odds": 3.40,
        },
        # Completely new game discovered on late slate
        {
            "date": "2026-06-18T15:00:00",
            "home": "HJK Helsinki",
            "away": "KuPS",
            "market": "1x2",
            "pick": "2",
            "bucket": "CERTIFIED_CLEAN",
            "odds": 2.80,
            "w_score": 0.85,
        }
    ]

    merged, new_added = daily.autonomous_intraday_merge(existing, fresh)
    
    assert new_added == 1
    assert len(merged) == 2
    # Verify exact morning pick is retained exactly
    assert merged[0]["home"] == "AC Oulu"
    assert merged[0]["pick"] == "1"
    assert merged[0]["odds"] == 1.95
    
    # Verify brand new game is appended
    assert merged[1]["home"] == "HJK Helsinki"
    assert merged[1]["pick"] == "2"


def test_stack_dispatch_never_drops_prior_bets(tmp_path):
    """Regression: a re-run whose fresh snapshot is missing a bet found in an
    earlier run must keep that bet in the stacked archive. This is the contract
    the official dispatch relies on (WhatsApp/report/CLV read the merged stack,
    not the fresh subset)."""
    with patch.object(daily, "REPORT_DIR", tmp_path):
        prior = [
            {
                "date": "2026-08-02",
                "home": "Dinamo Brest", "away": "Belshina",
                "match": "Dinamo Brest vs Belshina",
                "market": "1x2", "pick": "home",
                "kickoff": "2026-08-02T17:00:00+02:00",
                "bucket": "CAUTION", "odds": 1.31,
            },
            {
                "date": "2026-08-02",
                "home": "CSKA Sofia", "away": "Dunav Ruse",
                "match": "CSKA Sofia vs Dunav Ruse",
                "market": "1x2", "pick": "home",
                "kickoff": "2026-08-02T19:15:00+02:00",
                "bucket": "CAUTION", "odds": 1.31,
            },
        ]
        daily.archive_picks_by_kickoff(prior, "2026-08-02")
        archive_path = daily.archived_picks_file("2026-08-02")
        assert archive_path.exists()

        # Run 2: fresh snapshot only found ONE of the two bets (the other vanished).
        daily.archive_picks_by_kickoff([prior[0]], "2026-08-02")

        merged = json.loads(archive_path.read_text())
        matches = {p["match"] for p in merged}
        assert "CSKA Sofia vs Dunav Ruse" in matches, "prior bet was dropped from the stack"
        assert "Dinamo Brest vs Belshina" in matches
        cska = next(p for p in merged if p["match"] == "CSKA Sofia vs Dunav Ruse")
        assert cska["odds"] == 1.31, "prior bet must be retained exactly as emitted"
