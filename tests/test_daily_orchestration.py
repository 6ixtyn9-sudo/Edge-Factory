from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "daily.py"
SPEC = importlib.util.spec_from_file_location("daily", SCRIPT)
daily = importlib.util.module_from_spec(SPEC)
sys.modules["daily"] = daily
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(daily)


@patch("daily.run_soft")
@patch("daily.run_pipeline")
@patch("daily.official_run_marker_file")
@patch("daily.archived_picks_file")
def test_run_smart_auto_forecast_archive_without_marker_runs_heavy(
    mock_archived_file, mock_marker_file, mock_run_pipeline, mock_run_soft
):
    """A future-planner archive must not suppress today's heavy official run."""
    archive = MagicMock()
    archive.exists.return_value = True  # yesterday's forecast shortlist exists
    mock_archived_file.return_value = archive
    marker = MagicMock()
    marker.exists.return_value = False
    mock_marker_file.return_value = marker

    with patch("daily.datetime") as mock_dt:
        mock_dt.now.return_value.strftime.side_effect = lambda fmt: "2026-06-18" if "%Y" in fmt else "0600"
        mock_dt.now.return_value.hour = 6

        daily.run_smart_auto(future_days=2, backfill_days=30)

        mock_run_pipeline.assert_called_once_with(
            target_date="2026-06-18",
            mode="official",
            future_days=2,
            backfill_days=30,
            force_repick=True,
            picks_only=False,
        )
        assert any("edge_firing_tripwire.py" in call.args[0] for call in mock_run_soft.call_args_list)


@patch("daily.run_soft")
@patch("daily.run_pipeline")
@patch("daily.official_run_marker_file")
@patch("daily.archived_picks_file")
def test_run_smart_auto_marker_triggers_intraday(
    mock_archived_file, mock_marker_file, mock_run_pipeline, mock_run_soft
):
    """Only the heavy-run completion marker authorizes intraday mode."""
    archive = MagicMock()
    archive.exists.return_value = True
    mock_archived_file.return_value = archive
    marker = MagicMock()
    marker.exists.return_value = True
    mock_marker_file.return_value = marker

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
        assert any("edge_firing_tripwire.py" in call.args[0] for call in mock_run_soft.call_args_list)


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

    # promote_forecast re-serializes with heal_ledger_labels (indent=2,
    # sort_keys=True) — the written form is pretty-printed, not the compact
    # input. Assert the actual serialization the code writes.
    expected = json.dumps(dummy_picks, indent=2, sort_keys=True)
    mock_archive_dest.write_text.assert_called_once_with(expected)
    mock_picks_today_file.write_text.assert_called_once_with(expected)
    mock_gen_report.assert_called_once_with("2026-06-18")
    mock_run_soft.assert_called()
    assert any("sync_supabase" in call[0][0] for call in mock_run_soft.call_args_list)


def test_result_refresh_command_targets_yesterday_only():
    assert daily.result_refresh_day("2026-08-05") == "2026-08-04"
    assert daily.result_refresh_cmd("2026-08-05") == (
        "PYTHONPATH=src python3 scripts/refresh_result_sources.py --date 2026-08-04"
    )


def test_official_run_marker_is_atomic_and_independent_of_pick_archive(tmp_path):
    with patch.object(daily, "REPORT_DIR", tmp_path):
        # A future forecast archive may already exist; it is not the marker.
        daily.archived_picks_file("2026-08-20").write_text("[]")
        assert not daily.official_run_marker_file("2026-08-20").exists()

        path = daily.mark_official_run_complete(
            "2026-08-20", "2026-08-20T06:00:00+02:00"
        )
        payload = json.loads(path.read_text())

    assert payload["schema"] == 1
    assert payload["target_date"] == "2026-08-20"
    assert payload["pipeline"] == "official_heavy"
    assert payload["run_as_of"] == "2026-08-20T06:00:00+02:00"
    assert not path.with_suffix(".json.tmp").exists()


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

    merged, new_added, superseded = daily.autonomous_intraday_merge(existing, fresh)

    assert new_added == 1
    assert superseded == 1
    assert len(merged) == 2
    # Prefer-fresh: the duplicate fixture's FRESH row supersedes the archived
    # one (the old behavior of keeping the archived row silently hid newer,
    # more truthful picks — e.g. an ml-meta pick behind an archived 3way row).
    assert merged[0]["home"] == "AC Oulu"
    assert merged[0]["pick"] == "X"
    assert merged[0]["odds"] == 3.40

    # Verify brand new game is appended
    assert merged[1]["home"] == "HJK Helsinki"
    assert merged[1]["pick"] == "2"


def test_autonomous_merge_repairs_duplicates_already_in_archive():
    """A corrupt prior archive must not keep duplicate aliases forever."""
    first = {
        "date": "2026-08-13",
        "home": "FC Nordsjaelland",
        "away": "Valur Reykjavik",
        "match": "FC Nordsjaelland vs Valur Reykjavik",
        "market": "1x2",
        "pick": "home",
        "odds": 1.12,
    }
    duplicate_alias = {
        **first,
        "home": "FC Nordsjælland",
        "match": "FC Nordsjælland vs Valur Reykjavik",
    }

    merged, new_added, superseded = daily.autonomous_intraday_merge(
        [first, duplicate_alias], []
    )

    assert len(merged) == 1
    assert new_added == 0
    assert superseded == 1
    assert merged[0] == first  # first-frozen wins when there is no fresh row


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


def test_match_market_key_folds_accents():
    """Accent variants of the same team must collapse to one ledger key, so a
    re-scrape spelling the fixture differently cannot double-enter the stack."""
    a = daily.match_market_key(
        {"home": "Strømmen", "away": "Kongsvinger", "market": "1x2"}
    )
    b = daily.match_market_key(
        {"home": "Strommen", "away": "Kongsvinger IL", "market": "1x2"}
    )
    assert a == b, f"accent variant produced different keys: {a} vs {b}"
    # And a genuinely different fixture must NOT collide with it.
    c = daily.match_market_key(
        {"home": "Strømsgodset", "away": "Kongsvinger", "market": "1x2"}
    )
    assert a != c


def test_match_market_key_ignores_date_field():
    """The ledger key must ignore the explicit date field (midnight-crossing
    guard): the same match scraped across two dates is still one bet."""
    a = daily.match_market_key(
        {"date": "2026-08-02", "home": "Dinamo Brest", "away": "Belshina", "market": "1x2"}
    )
    b = daily.match_market_key(
        {"date": "2026-08-03", "home": "Dinamo Brest", "away": "Belshina", "market": "1x2"}
    )
    assert a == b


def test_daily_report_renders_every_ledger_bucket(tmp_path):
    """The operator-facing TXT must match the audited JSON ledger row-for-row."""
    with patch.object(daily, "REPORT_DIR", tmp_path):
        picks = [
            {
                "date": "2026-08-06",
                "home": "Twente",
                "away": "Dunajska Streda",
                "match": "Twente vs Dunajska Streda",
                "market": "1x2",
                "pick": "home",
                "bucket": "WATCHLIST_UNCORROBORATED_PRICE",
                "avg_p": 72.5,
                "w_score": 1.0,
                "odds": 1.2,
                "odds_source": "scoutingstats_odds",
                "kickoff": "06-08, 18:00",
                "statistical_comment": (
                    "📊 Realized Stats: Avg Goals: 3.10 | Over 2.5: 65.0% | "
                    "Top Scores: 2-0 (16.0%), 1-0 (12.0%)"
                ),
                "ctx": {"league_key": "ecl", "league": "ALLOW", "odds_band_name": "1.20-1.35", "odds_band": "CAUTION"},
            },
            {
                "date": "2026-08-06",
                "home": "Ajax",
                "away": "Shelbourne",
                "match": "Ajax vs Shelbourne",
                "market": "1x2",
                "pick": "home",
                "bucket": "WATCHLIST_SUSPECT_PRICE",
                "avg_p": 68.0,
                "w_score": 1.0,
                "odds": 1.08,
                "kickoff": "06-08, 19:00",
                "ctx": {},
            },
        ]
        out = daily.generate_daily_report("2026-08-06", source_picks=picks)
        text = out.read_text()

    assert "WATCHLIST — UNCORROBORATED SCOUTINGSTATS PRICE" in text
    assert "Twente vs Dunajska Streda" in text
    assert "WATCHLIST — SUSPECT FUZZY PRICE MATCH" in text
    assert "Ajax vs Shelbourne" in text
    assert "Avg Goals: 3.10" in text
    assert "Top Scores" not in text
    assert "2-0 (16.0%)" not in text
    assert "Total archived picks in this report: 2" in text
