from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from edgefactory import phase5_shadow
from edgefactory.sources import betminer

ROOT = Path(__file__).resolve().parent.parent


def test_phase5_ledgers_are_allowlisted_for_existing_git_persistence():
    for name in (
        phase5_shadow.ROWS_NAME,
        phase5_shadow.ATTEMPTS_NAME,
        "status.json",
        "evaluation.json",
    ):
        path = f"localdata/{phase5_shadow.SHADOW_DIR}/{name}"
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-q", path],
            cwd=ROOT,
            check=False,
        )
        assert result.returncode == 1, f"{path} is still ignored by Git"


def _load_script(module_name: str, relpath: str):
    script = ROOT / relpath
    spec = importlib.util.spec_from_file_location(module_name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_capture_daily_opt_in_piggybacks_only_four_authorized_existing_jobs(
    monkeypatch, capsys
):
    capture = _load_script("phase5_test_capture_daily", "scripts/capture_daily.py")
    commands: list[list[str]] = []
    monkeypatch.setattr(capture, "reset_recent_state", lambda *_args, **_kwargs: None)

    def fake_run(command, *, cwd):
        commands.append(list(command))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(capture.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "capture_daily.py", "--skip-build", "--phase5-shadow", "--sources",
            "vitibet,bzzoiro,betclan,scoutingstats,zulubet",
        ],
    )

    capture.main()

    assert capture.PHASE5_BACKFILL_SOURCES == phase5_shadow.AUTHORIZED_SOURCES - {"betminer"}
    assert len(commands) == 5  # exactly the selected, pre-existing source jobs
    by_source = {command[2]: command for command in commands}
    assert set(by_source) == {"vitibet", "bzzoiro", "betclan", "scoutingstats", "zulubet"}
    for source in capture.PHASE5_BACKFILL_SOURCES:
        command = by_source[source]
        assert command.count("--phase5-shadow") == 1
        assert command[command.index("--capture-day") + 1] == phase5_shadow.local_capture_date()
    assert "--phase5-shadow" not in by_source["zulubet"]
    assert "Rebuilding warehouse" not in capsys.readouterr().out


def test_phase5_opt_in_rejects_a_control_only_capture_plan(monkeypatch):
    capture = _load_script("phase5_test_capture_daily_control", "scripts/capture_daily.py")
    monkeypatch.setattr(
        sys,
        "argv",
        ["capture_daily.py", "--skip-build", "--phase5-shadow", "--sources", "zulubet"],
    )
    with pytest.raises(SystemExit) as exc:
        capture.main()
    assert exc.value.code == 2


def test_local_backfill_writes_forward_rows_from_the_same_fetch_results(
    monkeypatch, tmp_path
):
    backfill = _load_script("phase5_test_local_backfill", "scripts/local_backfill.py")
    requested: list[str] = []
    source = types.ModuleType("edgefactory.sources.vitibet")
    source.COLUMNS = ["date", "home", "away", "p1", "px", "p2"]

    def fetch_day(day: str):
        requested.append(day)
        fixture_day = "2026-10-06" if day == "2026-10-06" else "2026-10-07"
        return [{
            "date": fixture_day,
            "home": f"Home {fixture_day}",
            "away": f"Away {fixture_day}",
            "p1": 0.75, "px": 0.15, "p2": 0.10,
            "kickoff": f"{fixture_day}T18:00:00+02:00",
        }]

    source.fetch_day = fetch_day
    monkeypatch.setitem(sys.modules, "edgefactory.sources.vitibet", source)
    monkeypatch.setattr(backfill, "LOCALDATA", tmp_path)
    monkeypatch.setenv("EDGE_FACTORY_PHASE5_RUN_CONTEXT", "official_daily_pipeline")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "local_backfill.py", "vitibet", "2026-10-06", "2026-10-07",
            "--max-seconds", "60", "--phase5-shadow", "--capture-day", "2026-10-07",
        ],
    )

    backfill.main()

    assert requested == ["2026-10-06", "2026-10-07"]  # no additional source call
    rows_path = tmp_path / phase5_shadow.SHADOW_DIR / phase5_shadow.ROWS_NAME
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["identity"]["date"] == "2026-10-07"
    assert rows[0]["capture_day"] == "2026-10-07"
    assert rows[0]["capture_context"] == "official_daily_pipeline"

    attempts_path = tmp_path / phase5_shadow.SHADOW_DIR / phase5_shadow.ATTEMPTS_NAME
    [attempt] = [json.loads(line) for line in attempts_path.read_text().splitlines()]
    assert attempt["status"] == "ok"
    assert attempt["requested_days"] == ["2026-10-06", "2026-10-07"]
    assert attempt["forward_days"] == ["2026-10-07"]
    assert attempt["capture_context"] == "official_daily_pipeline"
    assert attempt["rows_fetched"] == 1
    assert attempt["rows_appended"] == 1
    assert attempt["rows_bytes_appended"] == rows_path.stat().st_size
    assert attempt["rows_ignored_historical"] == 1


def test_retryable_forward_zero_row_is_recorded_as_a_failed_attempt(
    monkeypatch, tmp_path
):
    backfill = _load_script("phase5_test_local_backfill_failed", "scripts/local_backfill.py")
    requested: list[str] = []
    source = types.ModuleType("edgefactory.sources.vitibet")
    source.COLUMNS = ["date", "home", "away"]

    def fetch_day(day: str):
        requested.append(day)
        return []

    source.fetch_day = fetch_day
    source.diagnostics = lambda: {
        "status": "auth", "http_statuses": [403], "quota_hint": "auth_or_quota"
    }
    monkeypatch.setitem(sys.modules, "edgefactory.sources.vitibet", source)
    monkeypatch.setattr(backfill, "LOCALDATA", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "local_backfill.py", "vitibet", "2026-10-07", "2026-10-07",
            "--max-seconds", "60", "--phase5-shadow", "--capture-day", "2026-10-07",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        backfill.main()
    assert exc.value.code == 1
    assert requested == ["2026-10-07"]
    attempts_path = tmp_path / phase5_shadow.SHADOW_DIR / phase5_shadow.ATTEMPTS_NAME
    [attempt] = [json.loads(line) for line in attempts_path.read_text().splitlines()]
    assert attempt["status"] == "failed"
    assert attempt["source_status"] == "auth"
    assert attempt["http_statuses"] == [403]
    assert attempt["error_classes"] == ["retryable_zero_row"]
    assert "request_headers" not in attempt
    assert "Authorization" not in json.dumps(attempt)


def test_betminer_existing_capture_response_is_persisted_separately_only_when_opted_in(
    monkeypatch, tmp_path
):
    picks = _load_script("phase5_test_picks_today", "scripts/picks_today.py")
    monkeypatch.setattr(picks, "LOCALDATA", tmp_path)
    monkeypatch.setattr(betminer, "diagnostics", lambda: {"status": "ok", "http_statuses": [200]})
    monkeypatch.setattr(
        betminer,
        "capture_day",
        lambda *_args, **_kwargs: pytest.fail("Phase 5 persistence must not issue another capture"),
    )
    capture_day = phase5_shadow.local_capture_date()
    response_rows = [{
        "date": capture_day,
        "home": "BetMiner Home U21",
        "away": "BetMiner Away U19",
        "kickoff": f"{capture_day}T20:00:00Z",
        "probabilities_raw": {"home_win": 0.72, "draw": 0.18, "away_win": 0.10},
        "1x2_selection": "home",
        "1x2_probability": 0.72,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }]

    monkeypatch.delenv("EDGE_FACTORY_PHASE5_SHADOW", raising=False)
    picks._record_phase5_betminer_capture(
        capture_day, rows=response_rows, stats={"status": "ok"},
        started_at="2026-10-07T06:00:00+00:00",
    )
    assert not (tmp_path / phase5_shadow.SHADOW_DIR).exists()

    monkeypatch.setenv("EDGE_FACTORY_PHASE5_SHADOW", "1")
    monkeypatch.setenv("EDGE_FACTORY_PHASE5_RUN_CONTEXT", "official_daily_pipeline")
    picks._record_phase5_betminer_capture(
        capture_day, rows=response_rows, stats={"status": "ok", "http_statuses": [200]},
        started_at="2026-10-07T06:00:00+00:00",
    )

    rows_path = tmp_path / phase5_shadow.SHADOW_DIR / phase5_shadow.ROWS_NAME
    attempts_path = tmp_path / phase5_shadow.SHADOW_DIR / phase5_shadow.ATTEMPTS_NAME
    [row] = [json.loads(line) for line in rows_path.read_text().splitlines()]
    [attempt] = [json.loads(line) for line in attempts_path.read_text().splitlines()]
    assert row["source"] == "betminer"
    assert row["capture_context"] == "official_daily_pipeline"
    assert row["identity"]["home_markers"] == ["u21"]
    assert attempt["source"] == "betminer"
    assert attempt["status"] == "ok"
    assert attempt["capture_context"] == "official_daily_pipeline"
    assert attempt["rows_appended"] == 1
    assert attempt["rows_bytes_appended"] == rows_path.stat().st_size
