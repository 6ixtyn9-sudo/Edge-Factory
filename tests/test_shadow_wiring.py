"""Shadow wiring contracts (SHADOW-01): picks_today drives all five shadow
sources through the same lane - capture, persist, conservative defaults,
failure isolation - without touching the production pick path.

The adapters themselves are covered per-source in test_shadow_sources.py,
test_betminer.py, test_pinnapi_odds.py and test_betbetter.py; these tests
fake capture_day/persist_shadow to pin the ORCHESTRATION only.
"""
from __future__ import annotations

import importlib
import pathlib

import scripts.picks_today as pt


def _adapter_modules():
    return {
        "futbolpronosticos": importlib.import_module("edgefactory.sources.futbolpronosticos"),
        "sportytrader_odds": importlib.import_module("edgefactory.sources.sportytrader_odds"),
        "betminer": importlib.import_module("edgefactory.sources.betminer"),
        "pinnapi_odds": importlib.import_module("edgefactory.sources.pinnapi_odds"),
        "betbetter": importlib.import_module("edgefactory.sources.betbetter"),
        "sharpapi_odds": importlib.import_module("edgefactory.sources.sharpapi_odds"),
        "boggio": importlib.import_module("edgefactory.sources.boggio"),
    }


def test_off_switch_disables_all_five(monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_SHADOW_CAPTURE", "off")
    stats = pt._capture_shadow_candidates("2026-10-03")
    assert set(stats) == {
        "futbolpronosticos", "sportytrader_odds", "betminer", "pinnapi_odds", "betbetter", "sharpapi_odds", "boggio"}
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
        "sharpapi_odds": {"status": "ok", "sa_raw": 8, "sa_matched": 8},
        "boggio": {"status": "ok", "bg_raw": 9, "bg_scored": 9},
    }
    for name, module in modules.items():
        monkeypatch.setattr(
            module, "capture_day",
            # **_kw: the sharpapi adapter now also receives our card and
            # the matcher to fold it with. A stub that refuses unknown
            # keywords would report a wiring change as a dead adapter.
            lambda day, _stats=counters[name], **_kw: ([], dict(_stats)))
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
                lambda day, _name=name, **_kw: ([], {"status": "ok"}))
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


def _call_keywords(tree, *, func_name, attr_of=None):
    """Keyword names (and simple value names) of a specific call."""
    import ast
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if attr_of is not None:
            if not (isinstance(func, ast.Attribute) and func.attr == func_name
                    and isinstance(func.value, ast.Name)
                    and func.value.id == attr_of):
                continue
        elif not (isinstance(func, ast.Name) and func.id == func_name):
            continue
        return {kw.arg: (kw.value.id if isinstance(kw.value, ast.Name) else None)
                for kw in node.keywords}
    return None


def test_the_pipeline_hands_sharpapi_our_card_and_its_own_matcher():
    """Asserts the wiring structurally, not by substring.

    The overlap number is only comparable with the price join downstream
    if both fold team names the same way. A private matcher inside the
    adapter would produce a number that looked like coverage and answered
    a different question.

    This was first written as a substring check and was VACUOUS: the same
    keyword already appeared elsewhere in the module for another source,
    so the assertion passed with the sharpapi wiring removed. Matching the
    call itself is the difference between a guard and a decoration.
    """
    import ast
    tree = ast.parse(pathlib.Path(pt.__file__).read_text(encoding="utf-8"))
    kwargs = _call_keywords(tree, func_name="capture_day", attr_of="sa")
    assert kwargs is not None, "no sharpapi capture call found in picks_today"
    assert "card" in kwargs, (
        "the sharpapi capture must receive the day's card; without it the "
        "adapter cannot say whether any of the board was about us")
    assert kwargs.get("team_key") == "odds_match_team_key", (
        "the sharpapi capture must fold the card with the same team key the "
        "price join uses, or the overlap is not comparable with it")


def test_the_shadow_capture_is_handed_the_days_card():
    import ast
    tree = ast.parse(pathlib.Path(pt.__file__).read_text(encoding="utf-8"))
    kwargs = _call_keywords(tree, func_name="_capture_shadow_candidates")
    assert kwargs is not None and "card" in kwargs, (
        "picks_today must pass the day's card into the shadow capture lane")
