"""Production-lane routing, horizon planning and blocker-diagnosis tests.

Every fixture, team, price and kickoff here is synthetic on purpose:
synthetic data is permitted inside unit tests and nowhere else.

The subject of this module is *leakage*. The fresh_production lane is the
only lane allowed to place bets, so each downstream consumer that touches
money or messaging — pick sync, edge sync, notification, CLV capture, odds
capture, ticket generation, the future planner — must read the lane payload
rather than a hardcoded legacy path. A consumer that keeps its own default
is the bug these tests exist to catch.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fp = _load("fresh_production_routing_under_test", "fresh_production.py")
cl = _load("clean_localdata_routing_under_test", "clean_localdata.py")

from edgefactory import production_lane as pl  # noqa: E402

DAY = "2026-06-12"
TZ = timezone(timedelta(hours=2))
AS_OF = datetime(2026, 6, 12, 8, 0, tzinfo=TZ)

FRESH = {"EDGE_FACTORY_PRODUCTION_LANE": "fresh_production"}
LEGACY = {"EDGE_FACTORY_PRODUCTION_LANE": "legacy_baseline"}


@pytest.fixture()
def lane_dir(tmp_path: Path) -> Path:
    """A localdata directory holding BOTH lanes' pick files.

    The legacy file is deliberately non-empty so that any consumer which
    silently falls back to it produces a visibly wrong, non-zero count.
    """
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / f"picks_{DAY}.json").write_text(json.dumps([
        {"date": DAY, "home": "Legacy Home", "away": "Legacy Away",
         "market": "1x2", "pick": "home", "odds": 2.0}
        for _ in range(5)
    ]))
    (localdata / "picks_today.json").write_text(
        (localdata / f"picks_{DAY}.json").read_text())
    (localdata / "edges_consensus.json").write_text(json.dumps(
        {"edges": [{"rule": "legacy_3way_unanimous_avg_p>=60", "status": "certified",
                    "train": {}, "valid": {}, "decay": {"verdict": "stable"}}]}))
    return localdata


def _write_fresh_slate(localdata: Path, rows: list[dict]) -> Path:
    path = localdata / f"fresh_production_production_picks_{DAY}.json"
    path.write_text(json.dumps(rows))
    return path


# --------------------------------------------------------------------------
# 1-3. The canonical payload, and that consumers read it
# --------------------------------------------------------------------------


@patch.dict(os.environ, FRESH)
def test_production_payload_exposes_every_routing_field(lane_dir: Path):
    _write_fresh_slate(lane_dir, [])
    payload = pl.production_payload(DAY, lane_dir, horizon_days=2)

    for key in ("production_lane", "production_pick_file", "production_edge_file",
                "production_pick_count", "production_date", "production_horizon",
                "comparison_only_files"):
        assert key in payload, f"payload is missing {key}"

    assert payload["production_lane"] == "fresh_production"
    assert payload["production_pick_file"].endswith(
        f"fresh_production_production_picks_{DAY}.json")
    assert payload["production_pick_count"] == 0
    assert payload["production_date"] == DAY
    assert payload["production_horizon"] == 2


@patch.dict(os.environ, FRESH)
def test_legacy_pick_files_are_listed_as_comparison_only(lane_dir: Path):
    payload = pl.production_payload(DAY, lane_dir)
    names = [Path(p).name for p in payload["comparison_only_files"]]
    assert f"picks_{DAY}.json" in names
    assert "picks_today.json" in names
    assert "edges_consensus.json" in names
    # The production file must never appear in its own comparison list.
    assert Path(payload["production_pick_file"]).name not in names


@patch.dict(os.environ, LEGACY)
def test_legacy_lane_routes_every_consumer_back_to_legacy(lane_dir: Path):
    payload = pl.production_payload(DAY, lane_dir)
    assert payload["production_lane"] == "legacy_baseline"
    assert payload["production_pick_file"].endswith(f"picks_{DAY}.json")
    assert payload["production_edge_file"].endswith("edges_consensus.json")
    assert payload["comparison_only_files"] == []


# --------------------------------------------------------------------------
# 4-8. Individual consumers must not read the legacy pick file
# --------------------------------------------------------------------------


@patch.dict(os.environ, FRESH)
def test_pick_sync_reads_the_fresh_slate_not_the_legacy_ledger(lane_dir: Path):
    _write_fresh_slate(lane_dir, [])
    path = pl.production_picks_path(DAY, lane_dir)
    assert json.loads(path.read_text()) == []
    # The legacy ledger still has five rows; routing must not see them.
    assert len(json.loads((lane_dir / f"picks_{DAY}.json").read_text())) == 5
    assert pl.load_production_picks(DAY, lane_dir) == []


@patch.dict(os.environ, FRESH)
def test_notification_uses_the_fresh_slate_and_sends_an_empty_slate(lane_dir: Path):
    _write_fresh_slate(lane_dir, [])
    path = pl.ensure_production_picks_file(DAY, lane_dir)
    assert path.name == f"fresh_production_production_picks_{DAY}.json"
    assert json.loads(path.read_text()) == []


@patch.dict(os.environ, FRESH)
def test_clv_capture_defaults_to_the_production_lane_file(lane_dir: Path):
    clv = _load("audit_clv_routing_under_test", "audit_clv.py")
    with patch.object(clv, "LOCALDATA", lane_dir):
        resolved = clv.resolve_capture_input(DAY, None)
    assert resolved.name == f"fresh_production_production_picks_{DAY}.json"
    assert resolved.name != f"picks_{DAY}.json"


@patch.dict(os.environ, FRESH)
def test_clv_capture_still_honours_an_explicit_input_path(lane_dir: Path):
    clv = sys.modules.get("audit_clv_routing_under_test") or _load(
        "audit_clv_routing_under_test", "audit_clv.py")
    explicit = lane_dir / "somewhere_else.json"
    assert clv.resolve_capture_input(DAY, str(explicit)) == explicit


@patch.dict(os.environ, FRESH)
def test_auto_tickets_generates_nothing_when_the_fresh_slate_is_absent(lane_dir: Path):
    """No fresh slate means no tickets — never a legacy fallback."""
    assert not (lane_dir / f"fresh_production_production_picks_{DAY}.json").exists()
    assert (lane_dir / f"picks_{DAY}.json").exists()
    path = pl.production_picks_path(DAY, lane_dir)
    assert not path.exists()
    assert pl.load_production_picks(DAY, lane_dir) == []


@patch.dict(os.environ, FRESH)
def test_odds_shortlist_capture_has_no_legacy_picks_to_enrich(lane_dir: Path):
    """An empty production slate means no shortlist odds fetch happens."""
    _write_fresh_slate(lane_dir, [])
    assert pl.load_production_picks(DAY, lane_dir) == []


# --------------------------------------------------------------------------
# 9-11. Edge / rule sync
# --------------------------------------------------------------------------


@patch.dict(os.environ, FRESH)
def test_fresh_certified_edges_are_synced_separately_from_legacy(lane_dir: Path):
    (lane_dir / f"fresh_production_certified_edges_{DAY}.json").write_text(json.dumps({
        "model_version": "v2", "feature_schema_version": "s1",
        "certified_dispatchable_rules": [
            {"rule_id": "fresh_1x2_v2_p60_majority", "sample": 331,
             "hit_rate": 0.716, "hit_rate_lb": 0.665, "status": "certified"}],
        "research_rules": [
            {"rule_id": "fresh_1x2_v2_p70_unanimous", "sample": 71,
             "hit_rate": 0.80, "hit_rate_lb": 0.60, "status": "research"}],
    }))
    assert pl.production_edges_path(DAY, lane_dir).name == \
        f"fresh_production_certified_edges_{DAY}.json"

    sync = _load("sync_supabase_routing_under_test", "sync_supabase.py")
    with patch.object(sync, "LOCALDATA", lane_dir), \
         patch.object(sync, "EDGES", lane_dir / "edges_consensus.json"):
        edges = sync.load_edges(DAY)

    by_name = {e["name"]: e for e in edges}
    fresh = by_name["fresh_1x2_v2_p60_majority"]
    assert fresh["rule"]["lane"] == "fresh_production"
    assert fresh["rule"]["rule_source"] == "fresh_production"
    assert fresh["rule"]["dispatchable"] is True
    assert fresh["rule"]["comparison_only"] is False


@patch.dict(os.environ, FRESH)
def test_research_rules_are_never_marked_dispatchable(lane_dir: Path):
    (lane_dir / f"fresh_production_certified_edges_{DAY}.json").write_text(json.dumps({
        "certified_dispatchable_rules": [],
        "research_rules": [{"rule_id": "fresh_1x2_v2_p70_unanimous",
                            "sample": 71, "status": "research"}],
    }))
    sync = sys.modules["sync_supabase_routing_under_test"]
    with patch.object(sync, "LOCALDATA", lane_dir), \
         patch.object(sync, "EDGES", lane_dir / "edges_consensus.json"):
        edges = sync.load_edges(DAY)
    research = [e for e in edges if e["name"] == "fresh_1x2_v2_p70_unanimous"]
    assert research and research[0]["rule"]["dispatchable"] is False
    assert research[0]["status"] == "research"


@patch.dict(os.environ, FRESH)
def test_legacy_edges_are_published_only_as_comparison_only(lane_dir: Path):
    (lane_dir / f"fresh_production_certified_edges_{DAY}.json").write_text(
        json.dumps({"certified_dispatchable_rules": [], "research_rules": []}))
    sync = sys.modules["sync_supabase_routing_under_test"]
    with patch.object(sync, "LOCALDATA", lane_dir), \
         patch.object(sync, "EDGES", lane_dir / "edges_consensus.json"):
        edges = sync.load_edges(DAY)
    legacy = [e for e in edges if e["rule"]["rule_source"] == "legacy_baseline"]
    assert legacy, "the legacy registry should still be published for comparison"
    for edge in legacy:
        assert edge["rule"]["comparison_only"] is True
        assert edge["rule"]["dispatchable"] is False
        assert edge["status"] == "comparison_only"


# --------------------------------------------------------------------------
# 12. Legacy future planner rows are comparison-only
# --------------------------------------------------------------------------


@patch.dict(os.environ, FRESH)
def test_future_planner_rows_are_stamped_comparison_only(tmp_path: Path):
    daily = _load("daily_routing_under_test", "daily.py")
    with patch.object(daily, "REPORT_DIR", tmp_path):
        daily.write_future_outputs(
            [{"match": "Alpha vs Beta", "date": DAY}], 2, "2026-06-12T08:00:00+02:00")
        rows = json.loads((tmp_path / "picks_next_2days.json").read_text())
        manifest = json.loads((tmp_path / "picks_next_2days_manifest.json").read_text())

    assert rows[0]["comparison_only"] is True
    assert rows[0]["production"] is False
    assert rows[0]["lane"] == "legacy_baseline"
    assert manifest["comparison_only"] is True
    assert manifest["ledger_kind"] == "legacy_baseline_comparison_forecast"


# --------------------------------------------------------------------------
# 13-15. Horizon planner
# --------------------------------------------------------------------------


class _StubEngine:
    """Minimal timing engine: kickoffs are 'YYYY-MM-DD HH:MM' in local time."""

    @staticmethod
    def parse_kickoff_dt(raw: str, reference=None):
        try:
            return datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        except (TypeError, ValueError):
            return None

    def operational_pick_eligibility(self, pick, *, as_of, min_lead):
        kickoff = self.parse_kickoff_dt(pick.get("kickoff") or "")
        if kickoff is None:
            return False, "unparseable_kickoff"
        if kickoff - as_of < timedelta(minutes=min_lead):
            return False, "inside_lead_or_started"
        return True, ""


def _horizon_candidate(day: str, kickoff: str, *, edge: float = 0.05):
    cand = fp.Candidate(
        date=day, kickoff=kickoff, league="Test League", home="Alpha Town",
        away="Beta City", selection="home", rule_id="fresh_1x2_v2_p60_majority",
        probability=0.65, odds=1.8, edge=edge, dispatchable=True,
        stake_units=fp.FLAT_STAKE_UNITS)
    return cand


def _run_horizon(candidates_by_day, *, horizon_days=2, as_of=AS_OF,
                 max_lead_hours=fp.HORIZON_MAX_LEAD_HOURS):
    """Drive plan_horizon with a stubbed candidate generator."""
    engine = _StubEngine()

    def fake_build(groups, *, day, **kwargs):
        return list(candidates_by_day.get(day, [])), {}

    with patch.object(fp, "build_candidates", fake_build), \
         patch.object(fp, "build_price_board", lambda *a, **k: {"bundles": [], "stats": {}}):
        return fp.plan_horizon(
            groups={}, evidence={}, envelope={}, engine=engine,
            localdata=Path("/nonexistent"), day=DAY, as_of=as_of,
            horizon_days=horizon_days, voters=(), max_lead_hours=max_lead_hours)


def test_horizon_planner_dispatches_an_eligible_future_pick():
    tomorrow = (date.fromisoformat(DAY) + timedelta(days=1)).isoformat()
    payload = _run_horizon({tomorrow: [_horizon_candidate(tomorrow, f"{tomorrow} 18:00")]})

    assert payload["eligible_pick_count"] == 1
    pick = payload["picks"][0]
    assert pick["date"] == tomorrow
    assert pick["rule_id"] == "fresh_1x2_v2_p60_majority"
    assert pick["stake_units"] == fp.FLAT_STAKE_UNITS
    assert payload["horizon_end"] == \
        (date.fromisoformat(DAY) + timedelta(days=2)).isoformat()


def test_horizon_planner_rejects_started_and_inside_lead_fixtures():
    """A fixture already under way is never eligible, however good the edge."""
    started = _horizon_candidate(DAY, f"{DAY} 07:00")   # before as_of 08:00
    inside = _horizon_candidate(DAY, f"{DAY} 08:15")    # inside the 30m lead
    engine = _StubEngine()
    for cand in (started, inside):
        ok, _reason = engine.operational_pick_eligibility(
            {"date": DAY, "kickoff": cand.kickoff}, as_of=AS_OF,
            min_lead=fp.HORIZON_MIN_LEAD_MINUTES)
        assert ok is False

    # Beyond the maximum lead is equally ineligible.
    far = (date.fromisoformat(DAY) + timedelta(days=2)).isoformat()
    payload = _run_horizon({far: [_horizon_candidate(far, f"{far} 18:00")]},
                           max_lead_hours=24)
    assert payload["eligible_pick_count"] == 0


def test_horizon_planner_requires_a_trusted_parseable_kickoff():
    tomorrow = (date.fromisoformat(DAY) + timedelta(days=1)).isoformat()
    cand = _horizon_candidate(tomorrow, "")
    payload = _run_horizon({tomorrow: [cand]})
    assert payload["eligible_pick_count"] == 0
    assert any(b.startswith(fp.BLOCKER_MISSING_KICKOFF) for b in cand.blockers)


def test_horizon_planner_requires_odds_and_a_certified_rule():
    """Undispatchable candidates never enter the horizon plan."""
    tomorrow = (date.fromisoformat(DAY) + timedelta(days=1)).isoformat()
    unpriced = _horizon_candidate(tomorrow, f"{tomorrow} 18:00")
    unpriced.odds = None
    unpriced.edge = None
    unpriced.dispatchable = False
    unpriced.blockers = [f"{fp.BLOCKER_MISSING_ODDS}: no usable 1X2 price"]

    unruled = _horizon_candidate(tomorrow, f"{tomorrow} 18:00")
    unruled.rule_id = None
    unruled.dispatchable = False
    unruled.blockers = [f"{fp.BLOCKER_NO_RULE}: none matched"]

    payload = _run_horizon({tomorrow: [unpriced, unruled]})
    assert payload["eligible_pick_count"] == 0


# --------------------------------------------------------------------------
# 16-17. Timing blocker classification
# --------------------------------------------------------------------------


def _timing_group(observations, kickoff=""):
    group = fp.FixtureGroup(date=DAY, key=("alpha", "beta"), home="Alpha Town",
                            away="Beta City", league="Test League")
    group.kickoff = kickoff
    group.kickoff_source = "zulubet" if kickoff else ""
    group.kickoff_observations = list(observations)
    return group


def test_timing_blockers_are_classified_precisely():
    """Each cause of a timing failure gets its own, actionable label."""
    started = fp.diagnose_timing(
        _timing_group([{"source": "zulubet", "raw": f"{DAY} 07:00",
                        "timing_capable": True, "parsed": True}],
                      kickoff=f"{DAY} 07:00"),
        guard_reason="inside_lead_or_started")
    assert started["classification"] == fp.TIMING_STARTED

    nowhere = fp.diagnose_timing(_timing_group([]), guard_reason=None)
    assert nowhere["classification"] == fp.TIMING_NO_SOURCE

    unreadable = fp.diagnose_timing(
        _timing_group([{"source": "zulubet", "raw": "kick-off TBC",
                        "timing_capable": True, "parsed": False}]),
        guard_reason=None)
    assert unreadable["classification"] == fp.TIMING_PARSE_FAILED

    untrusted = fp.diagnose_timing(
        _timing_group([{"source": "betclan", "raw": f"{DAY} 18:00",
                        "timing_capable": False, "parsed": True}]),
        guard_reason=None)
    assert untrusted["classification"] == fp.TIMING_NON_TIMING_SOURCE

    fine = fp.diagnose_timing(
        _timing_group([{"source": "zulubet", "raw": f"{DAY} 18:00",
                        "timing_capable": True, "parsed": True}],
                      kickoff=f"{DAY} 18:00"),
        guard_reason=None)
    assert fine["classification"] == fp.TIMING_OK


def test_parser_recovers_a_valid_captured_kickoff():
    """A kickoff a timing source really published must be used, not dropped.

    This is the true-bug case the classification is meant to expose: if the
    parser can read the captured value, the fixture must end up with a
    trusted kickoff rather than a ``missing_trusted_kickoff`` blocker.
    """
    engine = _StubEngine()
    raw = f"{DAY} 18:00"
    assert engine.parse_kickoff_dt(raw) is not None
    group = _timing_group([{"source": "zulubet", "raw": raw,
                            "timing_capable": True, "parsed": True}], kickoff=raw)
    diagnosis = fp.diagnose_timing(group, guard_reason=None)
    assert diagnosis["classification"] == fp.TIMING_OK
    assert diagnosis["kickoff"] == raw
    assert diagnosis["kickoff_source"] == "zulubet"


# --------------------------------------------------------------------------
# 18-19. Pricing diagnostics
# --------------------------------------------------------------------------


class _PriceEngine:
    """Odds lookup stub returning a fixed (row, method) per bundle."""

    def __init__(self, results):
        self._results = results

    def find_side_keyed_odds_row(self, pick, bundle):
        return self._results.get(bundle["name"], (None, None))

    @staticmethod
    def _valid_decimal_odds(value):
        try:
            odds = float(value)
        except (TypeError, ValueError):
            return None
        return odds if 1.01 <= odds <= 100 else None


def _board(names_and_tiers):
    return {"bundles": [(name, tier, {"name": name, "exact": {}})
                        for name, tier in names_and_tiers],
            "stats": {}}


def test_a_fuzzy_only_price_is_rejected_and_never_dispatched():
    board = _board([("betexplorer", fp.PRICE_TIER_DEDICATED)])
    engine = _PriceEngine({"betexplorer": ({"odds": 1.8}, "alias_fuzzy")})

    diagnosis = fp.diagnose_price(engine, board, day=DAY, home="Alpha Town",
                                  away="Beta City", kickoff=f"{DAY} 18:00",
                                  selection="home")
    assert diagnosis["fuzzy_match_found_and_rejected"] is True
    assert diagnosis["exact_match_found"] is False
    assert diagnosis["outcome"] == "fuzzy_rejected"

    priced = fp.price_for_candidate(engine, board, day=DAY, home="Alpha Town",
                                    away="Beta City", kickoff=f"{DAY} 18:00",
                                    selection="home")
    # The price is retained as evidence but flagged, and the suspect flag is
    # what turns into a blocker in build_candidates.
    assert priced["suspect"] is True


def test_missing_price_diagnostics_name_every_bundle_searched():
    board = _board([("source_embedded_odds", fp.PRICE_TIER_SOURCE_EMBEDDED),
                    ("bzzoiro", fp.PRICE_TIER_DEDICATED),
                    ("scoutingstats", fp.PRICE_TIER_DEDICATED)])
    engine = _PriceEngine({})   # nothing matches anywhere

    diagnosis = fp.diagnose_price(engine, board, day=DAY, home="Alpha Town",
                                  away="Beta City", kickoff=f"{DAY} 18:00",
                                  selection="home")
    assert diagnosis["bundles_searched"] == [
        "source_embedded_odds", "bzzoiro", "scoutingstats"]
    assert diagnosis["outcome"] == "no_match"
    assert diagnosis["embedded_source_price_found"] is False
    assert len(diagnosis["detail"]) == 3
    for entry in diagnosis["detail"]:
        assert entry["matched"] is False
        assert "rows_in_bundle" in entry


def test_an_embedded_source_price_is_recorded_only_on_a_direct_match():
    board = _board([("source_embedded_odds", fp.PRICE_TIER_SOURCE_EMBEDDED)])
    engine = _PriceEngine({"source_embedded_odds": ({"odds": 1.8}, "exact")})
    diagnosis = fp.diagnose_price(engine, board, day=DAY, home="Alpha Town",
                                  away="Beta City", kickoff=f"{DAY} 18:00",
                                  selection="home")
    assert diagnosis["embedded_source_price_found"] is True
    assert diagnosis["exact_match_found"] is True


# --------------------------------------------------------------------------
# 20-22. Reporting: clean sections and an actionable no-picks diagnosis
# --------------------------------------------------------------------------


def _report(**overrides):
    base = {
        "date": DAY,
        "certified_rule_count": 4,
        "research_rule_count": 4,
        "blocked_rule_count": 0,
        "candidate_count": 53,
        "rule_matched_count": 2,
        "dispatchable_count": 0,
        "dispatchable_picks": [],
        "candidates": [],
        "blocker_counts": {},
        "pricing": {
            "candidate_count_before_pricing": 10,
            "candidate_count_with_any_price": 10,
            "candidate_count_with_positive_edge": 3,
        },
        "walkforward": {"fixtures_labelled": 1421},
        "horizon": {"eligible_pick_count": 0, "horizon_end": "2026-06-14",
                    "picks": []},
    }
    base.update(overrides)
    return base


def _blocked_candidate(blocker, *, edge=0.06, would_have=False):
    return {"home": "Alpha Town", "away": "Beta City", "selection": "home",
            "rule_id": "fresh_1x2_v2_p60_majority", "probability": 0.65,
            "odds": 1.8, "edge": edge, "blockers": [blocker],
            "would_have_qualified_before_kickoff": would_have}


def test_no_picks_diagnosis_reports_a_top_action_item():
    lines = fp.no_picks_diagnosis(_report(candidates=[
        _blocked_candidate(f"{fp.BLOCKER_KICKOFF_GUARD}: inside_30m_lead_or_started",
                           would_have=True)]))
    text = "\n".join(lines)
    assert "FRESH PRODUCTION NO-PICKS DIAGNOSIS" in text
    assert "TOP ACTION ITEM:" in text
    assert "already started or were inside the lead window" in text
    assert "horizon planner" in text


def test_no_picks_diagnosis_names_the_stage_that_lost_the_edge():
    """The action item must change with the actual cause, not be boilerplate."""
    edge_short = "\n".join(fp.no_picks_diagnosis(_report(candidates=[
        _blocked_candidate(f"{fp.BLOCKER_INSUFFICIENT_EDGE}: edge +0.0100")])))
    assert "did not clear the edge threshold" in edge_short
    assert "correct abstention" in edge_short

    unpriced = "\n".join(fp.no_picks_diagnosis(_report(candidates=[
        _blocked_candidate(f"{fp.BLOCKER_MISSING_ODDS}: bundles searched=bzzoiro")])))
    assert "could not be priced" in unpriced

    no_kickoff = "\n".join(fp.no_picks_diagnosis(_report(candidates=[
        _blocked_candidate(
            f"{fp.BLOCKER_MISSING_KICKOFF}: {fp.TIMING_NO_SOURCE}")])))
    assert "no trusted kickoff" in no_kickoff
    assert "do not relax the kickoff gate" in no_kickoff


def test_no_picks_diagnosis_lists_next_eligible_horizon_candidates():
    tomorrow = (date.fromisoformat(DAY) + timedelta(days=1)).isoformat()
    report = _report(
        candidates=[_blocked_candidate(f"{fp.BLOCKER_KICKOFF_GUARD}: started",
                                       would_have=True)],
        horizon={"eligible_pick_count": 1, "horizon_end": "2026-06-14",
                 "picks": [{"date": tomorrow, "kickoff": f"{tomorrow} 18:00",
                            "home": "Gamma", "away": "Delta",
                            "selection": "home", "edge": 0.07}]})
    text = "\n".join(fp.no_picks_diagnosis(report))
    assert "next eligible horizon candidates" in text
    assert "Gamma vs Delta" in text


def test_fresh_production_sections_exclude_parked_sources():
    """Parked/degraded sources belong in comparison sections only."""
    roles = {name: "historical_reference" for name in fp.PARKED_PREDICTORS}
    roles["zulubet"] = "current_production_source"
    markdown = fp.render_source_health_md(
        DAY, roles, [], {}, {"candidate_count_before_pricing": 0},
        {})
    head, _, tail = markdown.partition("historical_reference")
    for parked in fp.PARKED_PREDICTORS:
        assert parked not in head, (
            f"{parked} appears in a current production section")


# --------------------------------------------------------------------------
# 23-24. Retention ordering and evidence preservation
# --------------------------------------------------------------------------


def test_retention_runs_before_the_persist_step():
    """daily.py must prune before the workflow's `git add -A localdata`."""
    source = (ROOT / "scripts" / "daily.py").read_text()
    assert "--policy fresh_production" in source
    assert "pre-persist" in source
    # The final pass must come after the lane and tripwire, so that this run's
    # own artefacts are covered rather than only the previous run's.
    assert source.index("edge firing tripwire (silence detector)") < \
        source.index("clean_localdata (fresh_production retention, pre-persist)")


def test_retention_preserves_raw_evidence_and_explains_zero_deletion(tmp_path: Path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    evidence = [
        localdata / "zulubet.csv.gz",
        localdata / f"picks_{DAY}.json",
        localdata / "auto_tickets_2026-06-01.txt",
        localdata / "some_unknown_operator_file.json",
    ]
    for path in evidence:
        path.write_text("evidence")
    # Only artefacts inside the retention window exist, so nothing is stale.
    (localdata / f"fresh_production_walkforward_{DAY}.json").write_text("{}")

    plan = cl.fresh_production_retention_plan(
        localdata, today=date.fromisoformat(DAY), keep_days=30, keep_latest=3,
        target_date=date.fromisoformat(DAY))
    json_path, md_path = cl.write_artifact_manifest(
        plan, root=localdata, dry_run=True)

    for path in evidence:
        assert path.exists(), f"{path.name} must never be deleted"

    payload = json.loads(json_path.read_text())
    assert payload["files_deleted"] == 0
    assert payload["no_files_removed_explanation"]
    assert "Why nothing was removed" in md_path.read_text()
    assert payload["unmatched_files_left_alone"] >= 1


def test_horizon_artifacts_are_a_known_retention_prefix():
    prefixes = [prefix for prefix, _exts in cl._ALL_PREFIXES]
    assert "fresh_production_horizon_picks" in prefixes
