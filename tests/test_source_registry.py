"""Invariants for the central source capability registry.

The registry exists because the PR #17 resilience sources were captured,
warehoused and audited while being structurally invisible to the pick engine.
These tests make that class of failure loud.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from edgefactory import source_registry as reg

ROOT = Path(__file__).resolve().parent.parent

RESILIENCE_SOURCES = (
    "predictz", "windrawwin", "freesupertips", "afootballreport",
    "prosoccer", "soccervista", "bettingclosed",
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def picks_today():
    return _load("picks_today_registry_test", ROOT / "scripts" / "picks_today.py")


@pytest.fixture(scope="module")
def capture_daily():
    return _load("capture_daily_registry_test", ROOT / "scripts" / "capture_daily.py")


def test_every_captured_source_is_registered(capture_daily):
    """Regression guard: capture_daily must never outrun the registry."""
    captured = {str(job[0]) for job in capture_daily.JOBS}
    missing = sorted(captured - set(reg.BY_NAME))
    assert not missing, (
        f"sources captured but absent from the capability registry: {missing} — "
        "they would be invisible to the pick engine and the funnel audit"
    )
    assert reg.registry_coverage_warnings(captured) == []


def test_registry_coverage_warning_fires_for_unknown_source():
    warnings = reg.registry_coverage_warnings({"zulubet", "brand_new_scraper"})
    assert len(warnings) == 1
    assert "brand_new_scraper" in warnings[0]


def test_resilience_sources_are_registered_and_shadow_evaluated():
    for name in RESILIENCE_SOURCES:
        cap = reg.get(name)
        assert cap is not None, f"{name} missing from registry"
        assert cap.tier in {reg.TIER_SHADOW, reg.TIER_DONOR}
    shadow = set(reg.shadow_1x2_sources())
    # bettingclosed is a results donor, not a predictor; the rest must vote in shadow
    assert shadow >= set(RESILIENCE_SOURCES) - {"bettingclosed"}


def test_shadow_sources_are_never_live_dispatch_voters(picks_today):
    live = set(picks_today.SOURCES_1X2) | set(picks_today.ALL_SOURCES)
    for name in reg.shadow_1x2_sources():
        assert name not in live, f"shadow source {name} leaked into the live universe"


def test_picks_engine_lists_are_derived_from_the_registry(picks_today):
    """The engine's universe must equal the registry's live tier, exactly."""
    assert picks_today.SOURCES_1X2 == list(reg.live_1x2_sources())
    assert picks_today.SOURCES_OU == list(reg.live_market_sources("ou"))
    assert picks_today.SOURCES_BTTS == list(reg.live_market_sources("btts"))
    assert picks_today.ALL_SOURCES == list(reg.live_consumed_sources())


def test_live_universe_is_unchanged_by_the_registry_refactor(picks_today):
    """Byte-for-byte parity with the pre-refactor hardcoded lists."""
    assert picks_today.SOURCES_1X2 == [
        "forebet", "zulubet", "statarea", "vitibet", "betclan", "bzzoiro"]
    assert picks_today.SOURCES_OU == ["forebet", "statarea", "scoutingstats", "bzzoiro"]
    assert picks_today.SOURCES_BTTS == ["forebet", "scoutingstats", "bzzoiro"]
    assert picks_today.ALL_SOURCES == [
        "forebet", "zulubet", "statarea", "vitibet", "betclan", "bzzoiro", "scoutingstats"]
    assert picks_today.OU_COL == {
        "forebet": "p_over", "statarea": "p_o25", "scoutingstats": "p_o25", "bzzoiro": "p_o25"}
    assert picks_today.BTTS_COL == {
        "forebet": "p_gg", "scoutingstats": "p_gg", "bzzoiro": "p_gg"}


def test_ml_feature_support_is_capability_driven_not_name_driven():
    providers = set(reg.ml_feature_providers())
    assert providers, "the serving model needs at least one feature provider"
    assert reg.has_ml_feature_support(["zulubet", "betclan"]) is True
    assert reg.has_ml_feature_support(["vitibet", "betclan", "bzzoiro"]) is False
    assert reg.has_ml_feature_support([]) is False


def test_no_forebet_name_check_remains_in_the_ml_gate():
    source = (ROOT / "scripts" / "picks_today.py").read_text()
    assert "if ml_model and (fb or zb or sa)" not in source
    assert "source_registry.has_ml_feature_support" in source


def test_pricing_and_donor_sources_are_not_predictors():
    for name in ("bzzoiro_odds", "theoddsapi_odds", "oddspapi_odds", "betexplorer_odds"):
        cap = reg.get(name)
        assert cap is not None and cap.pricing_only
        assert not cap.votes_1x2_shadow
    donor = reg.get("bettingclosed")
    assert donor is not None and donor.donor_only
    assert not donor.votes_1x2_shadow


def test_kickoff_capability_matches_known_adapter_limitations():
    for name in ("betclan", "predictz", "windrawwin"):
        cap = reg.get(name)
        assert cap is not None and cap.provides_kickoff is False
    for name in ("forebet", "zulubet", "statarea", "vitibet"):
        assert reg.get(name).provides_kickoff is True


def test_backfill_modes_are_declared_for_every_source():
    for cap in reg.REGISTRY:
        assert cap.backfill in {
            reg.BACKFILL_HISTORICAL, reg.BACKFILL_D30,
            reg.BACKFILL_FORWARD_ONLY, reg.BACKFILL_UNKNOWN,
        }
    assert reg.get("windrawwin").backfill == reg.BACKFILL_FORWARD_ONLY
    assert reg.get("statarea").backfill == reg.BACKFILL_D30


def test_validation_states_are_read_only_evidence(tmp_path):
    (tmp_path / "source_settlement_coverage_2026-09-30.json").write_text(
        '{"sources": [{"source": "zulubet", "verdict": "review_required"}]}'
    )
    states = reg.load_validation_states(tmp_path, "2026-09-30")
    assert states["zulubet"] == "review_required"
    # missing artifact must not raise and must not invent a verdict
    assert reg.load_validation_states(tmp_path / "nope") == {}


def test_describe_marks_only_live_tier_dispatchable():
    rows = {row["source"]: row for row in reg.describe()}
    assert rows["zulubet"]["dispatchable"] is True
    for name in RESILIENCE_SOURCES:
        assert rows[name]["dispatchable"] is False


def test_source_health_warning_on_high_surface_low_scoring():
    warnings = reg.source_health_warnings(
        match_surface=448, scored_fixtures=21, live_candidates=5,
        shadow_candidates=0, sources_with_1x2_rows=["zulubet"],
    )
    assert any("raw same-day surface is 448" in w for w in warnings)


def test_source_health_warning_when_source_has_rows_but_cannot_vote():
    warnings = reg.source_health_warnings(
        match_surface=10, scored_fixtures=10, live_candidates=1,
        shadow_candidates=0, sources_with_1x2_rows=["bettingclosed", "mystery_source"],
    )
    assert any("bettingclosed" in w and "excludes it" in w for w in warnings)
    assert any("mystery_source" in w and "not in the capability registry" in w for w in warnings)


def test_source_health_warning_live_zero_shadow_nonzero_and_odds_zero():
    warnings = reg.source_health_warnings(
        match_surface=10, scored_fixtures=4, live_candidates=0,
        shadow_candidates=7, sources_with_1x2_rows=["zulubet"],
        candidates_before_odds=4, odds_enriched=0,
    )
    assert any("0 live candidates but 7 shadow" in w for w in warnings)
    assert any("odds" in w and "price identity" in w for w in warnings)


def test_no_forebet_browser_run_path_in_audit_or_registry():
    """Neither the registry nor the audits may reach the parked Browser Run."""
    for rel in ("src/edgefactory/source_registry.py",
                "scripts/audit_source_funnel.py",
                "scripts/audit_source_settlement_coverage.py"):
        text = (ROOT / rel).read_text()
        assert "forebet_getrs" not in text
        assert "page_access" not in text
        assert "browser" not in text.lower() or "Browser Run" in text
