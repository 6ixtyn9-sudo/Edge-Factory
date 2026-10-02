"""Shadow wiring contracts (SHADOW-01): picks_today drives all five shadow
sources through the same lane - capture, persist, conservative defaults,
failure isolation - without touching the production pick path.

The adapters themselves are covered per-source in test_shadow_sources.py,
test_betminer.py, test_pinnapi_odds.py and test_betbetter.py; these tests
fake capture_day/persist_shadow to pin the ORCHESTRATION only.
"""
from __future__ import annotations

import importlib

import scripts.picks_today as pt


def _adapter_modules():
    return {
        "futbolpronosticos": importlib.import_module("edgefactory.sources.futbolpronosticos"),
        "sportytrader_odds": importlib.import_module("edgefactory.sources.sportytrader_odds"),
        "betminer": importlib.import_module("edgefactory.sources.betminer"),
        "pinnapi_odds": importlib.import_module("edgefactory.sources.pinnapi_odds"),
        "betbetter": importlib.import_module("edgefactory.sources.betbetter"),
    }


def test_off_switch_disables_all_five(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_SHADOW_CAPTURE", "off")
    stats = pt._capture_shadow_candidates("2026-10-03")
    assert set(stats) == {
        "futbolpronosticos", "sportytrader_odds", "betminer", "pinnapi_odds", "betbetter"}
    assert all(entry["status"] == "disabled" for entry in stats.values())


def test_capture_wires_all_five_sources(monkeypatch, tmp_path):
    monkeypatch.delenv("EDGE_FACTORY_SHADOW_CAPTURE", raising=False)
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    persisted = []
    modules = _adapter_modules()
    counters = {
        "futbolpronosticos": {"status": "ok", "raw": 3, "scored": 3},
        "sportytrader_odds": {"status": "ok", "st_raw": 4, "st_matched": 4},
        "betminer": {"status": "ok", "bm_raw": 5, "bm_scored": 5},
        "pinnapi_odds": {"status": "ok", "pa_raw": 6, "pa_matched": 6},
        "betbetter": {"status": "ok", "bb_raw": 7, "bb_scored": 7},
    }
    for name, module in modules.items():
        monkeypatch.setattr(
            module, "capture_day",
            lambda day, _stats=counters[name]: ([], dict(_stats)))
        monkeypatch.setattr(
            module, "persist_shadow",
            lambda day, rows, stats, localdata=None, _name=name: persisted.append((_name, day)) or tmp_path / f"{_name}.json")
    stats = pt._capture_shadow_candidates("2026-10-03")
    assert set(stats) == set(counters)
    for name, entry in stats.items():
        assert entry["status"] == "ok", name
    assert sorted(persisted) == sorted((name, "2026-10-03") for name in counters)


def test_adapter_failure_is_isolated_and_conservative(monkeypatch, tmp_path):
    monkeypatch.delenv("EDGE_FACTORY_SHADOW_CAPTURE", raising=False)
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    modules = _adapter_modules()

    def boom(day, **_kwargs):
        raise ValueError("boom: adapter exploded")

    monkeypatch.setattr(modules["betminer"], "capture_day", boom)
    for name, module in modules.items():
        if name != "betminer":
            monkeypatch.setattr(
                module, "capture_day",
                lambda day, _name=name: ([], {"status": "ok"}))
            monkeypatch.setattr(
                module, "persist_shadow",
                lambda day, rows, stats, localdata=None, _name=name: tmp_path / f"{_name}.json")
    stats = pt._capture_shadow_candidates("2026-10-03")
    # The failing source reports unavailable + blocker, never raises.
    assert stats["betminer"]["status"] == "unavailable"
    assert "boom: adapter exploded" in stats["betminer"]["blocker"]
    # ...and every other source still captured.
    for name in ("futbolpronosticos", "sportytrader_odds", "pinnapi_odds", "betbetter"):
        assert stats[name]["status"] == "ok", name
