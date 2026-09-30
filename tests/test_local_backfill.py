from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

from edgefactory.sources import prosoccer

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "local_backfill.py"
SPEC = importlib.util.spec_from_file_location("local_backfill", SCRIPT)
local_backfill = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(local_backfill)


def _install_source(monkeypatch, name: str, fetch_day):
    module = types.ModuleType(f"edgefactory.sources.{name}")
    module.COLUMNS = ["date", "home", "away"]
    module.fetch_day = fetch_day
    monkeypatch.setitem(sys.modules, f"edgefactory.sources.{name}", module)
    return module


def test_retryable_not_served_yet_leaves_day_open(monkeypatch, tmp_path, capsys):
    source = "unit_prosoccer_open"

    def fetch_day(day):
        raise prosoccer.NotServedYet(f"requested {day} but served yesterday")

    _install_source(monkeypatch, source, fetch_day)
    monkeypatch.setattr(local_backfill, "LOCALDATA", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["local_backfill.py", source, "2026-09-30", "2026-09-30", "--max-seconds", "60"],
    )

    local_backfill.main()

    state = json.loads((tmp_path / f"state_{source}.json").read_text())
    assert state["done"] == []
    assert "FAILED" in capsys.readouterr().out


def test_successful_empty_day_still_marks_done_for_other_sources(monkeypatch, tmp_path):
    source = "unit_empty_ok"
    _install_source(monkeypatch, source, lambda day: [])
    monkeypatch.setattr(local_backfill, "LOCALDATA", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["local_backfill.py", source, "2026-09-30", "2026-09-30", "--max-seconds", "60"],
    )

    local_backfill.main()

    state = json.loads((tmp_path / f"state_{source}.json").read_text())
    assert state["done"] == ["2026-09-30"]
