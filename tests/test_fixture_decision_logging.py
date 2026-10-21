"""Reason evidence must mirror real branches without changing bets or ROI universes."""
import ast
from copy import deepcopy
from datetime import datetime, timezone
import json
import random
import subprocess

import pytest

from scripts import picks_today as pt
from edgefactory import scored_candidate_shadow as scs

DAY = "2026-09-06"
MODEL = {"coef": [], "intercept": 0, "feature_cols": []}
EDGE = {2: {"n_way": 2, "threshold": 70, "rule": "2way-unanimous avg_p>=70",
            "display_rule": "2WAY-UNANIMOUS>=70"}}


@pytest.fixture(autouse=True)
def isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], None))
    monkeypatch.setattr(pt, "load_ml_fade_rules", lambda: [])
    monkeypatch.setattr(pt, "get_rolling_hit_rate_last_14d", lambda day: .75)
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    monkeypatch.setenv("EDGE_FACTORY_SCORED_SHADOW", "1")


def row(selection="home", probability=75, **extra):
    probabilities = {"home": (probability, 10, 90-probability),
                     "away": (90-probability, 10, probability),
                     "draw": (10, probability, 90-probability)}[selection]
    return {"home": "Sporting CP", "away": "Portimonense", "date": DAY,
            "league": "Portugal,Primeira Liga", "kickoff": f"{DAY}T20:30:00+00:00",
            "sport": "soccer", "ht_hs": 0, "ht_gs": 0, "p1": probabilities[0], "px": probabilities[1],
            "p2": probabilities[2], "odd1": 1.5, "oddx": 4, "odd2": 4, **extra}


def evaluate(data, edges=None):
    audit = []
    result = pt.eval_1x2(DAY, data, EDGE if edges is None else edges,
                          source_weights={}, fixture_audit=audit)
    return result, audit, next(e["decision_diagnostics"] for e in audit if e["kind"] == "upcoming_fixture")


@pytest.mark.parametrize("data,edges,reason", [
    ({"zulubet": {"key": row()}}, EDGE, "insufficient_probability_sources"),
    ({"zulubet": {"key": row()}, "statarea": {"key": row(p2=None)}}, EDGE,
     "insufficient_probability_sources"),
    ({"zulubet": {"key": row()}, "statarea": {"key": row("away")}}, EDGE, "voter_disagreement"),
    ({"zulubet": {"key": row(probability=60)}, "statarea": {"key": row(probability=60)}}, EDGE,
     "below_consensus_threshold"),
    ({"zulubet": {"key": row()}, "statarea": {"key": row()}}, {}, "no_consensus_rule_for_source_count"),
    ({"zulubet": {"key": row(league="Club Friendly")}, "statarea": {"key": row()}}, EDGE,
     "competition_requires_more_sources"),
    ({"forebet": {"key": row()}, "bzzoiro": {"key": row(kickoff="2026-09-09T20:30:00Z")}}, EDGE,
     "schedule_unstable"),
])
def test_first_failed_gate_is_logged_at_the_real_branch(data, edges, reason):
    result, audit, diagnostic = evaluate(data, edges)
    assert not result[0]
    assert diagnostic["primary_reason"] == reason
    assert diagnostic["consensus"]["reason"] == reason
    assert diagnostic["emitted_candidate_count"] == 0
    assert pt.eval_1x2(DAY, data, edges, source_weights={}) == result
    assert json.loads(json.dumps(audit, allow_nan=False))


def test_source_votes_missing_fields_and_actual_threshold_margin():
    _, _, d = evaluate({"zulubet": {"key": row(probability=60)},
                         "statarea": {"key": row(probability=60)}})
    assert d["consensus"]["observed_avg_probability_pct"] == 60
    assert d["consensus"]["effective_threshold_pct"] == 70
    assert d["consensus"]["shortfall_pct_points"] == 10
    assert [v["selection"] for v in d["source_votes"] if v["present"]] == ["home", "home"]
    _, _, d = evaluate({"zulubet": {"key": row()}, "statarea": {"key": row(p2=None, px="junk")}})
    source = next(v for v in d["source_votes"] if v["source"] == "statarea")
    assert source["missing_probability_fields"] == ["p2"]
    assert source["invalid_probability_fields"] == ["px"]


def test_competition_adjustments_logged_not_silently_treated_as_base_threshold():
    _, _, d = evaluate({"zulubet": {"key": row(probability=74, league="Portugal Cup")},
                         "statarea": {"key": row(probability=74)}})
    assert d["consensus"]["base_threshold_pct"] == 70
    assert d["consensus"]["effective_threshold_pct"] == 75
    assert d["consensus"]["shortfall_pct_points"] == 1


def test_no_certified_ml_rules_is_not_a_consensus_probability_failure(monkeypatch):
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], MODEL))
    _, audit, d = evaluate({"zulubet": {"key": row(probability=60)}, "statarea": {"key": row(probability=60)}})
    assert d["ml"]["reason"] == "no_certified_ml_rules"
    assert d["ml"]["probability"] == .5
    assert d["ml_fade"]["reason"] == "no_certified_fade_rules"
    assert d["consensus"]["reason"] == "below_consensus_threshold"
    ml_entry = next(e for e in audit if e["kind"] == "ml_scored_fixture")
    assert ml_entry["decision_diagnostics"] is d  # finalized after inference, not a stale copy


def test_ml_emission_survives_consensus_veto_and_is_not_reported_as_discarded(monkeypatch):
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([{"rule": "ml-meta avg_p>=40"}], MODEL))
    result, _, d = evaluate({"zulubet": {"key": row()}, "statarea": {"key": row("away")}})
    assert len(result[0]) == 1 and result[1] == 1
    assert d["primary_reason"] == "candidate_emitted"
    assert d["ml"]["status"] == "emitted"
    assert d["consensus"]["reason"] == "voter_disagreement"


def test_fade_draw_inverse_has_its_own_reason(monkeypatch):
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], MODEL))
    monkeypatch.setattr(pt, "load_ml_fade_rules", lambda: [{"rule": "ml-fade avg_p>=40"}])
    _, _, d = evaluate({"zulubet": {"key": row("draw", 60)}, "statarea": {"key": row("draw", 60)}})
    assert d["ml_fade"]["reason"] == "draw_has_no_binary_inverse"


def test_logging_failure_is_fail_soft_even_with_ml(monkeypatch):
    class BrokenAudit(list):
        def append(self, value):
            raise OSError("audit storage broken")
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], MODEL))
    data = {"zulubet": {"key": row()}, "statarea": {"key": row()}}
    base = pt.eval_1x2(DAY, data, EDGE, source_weights={})
    assert pt.eval_1x2(DAY, data, EDGE, source_weights={}, fixture_audit=BrokenAudit()) == base


def test_pre_match_log_preserves_exact_reason_and_does_not_mutate_rejected_pick():
    rejected = row(kickoff=f"{DAY}T10:00:00Z", market="1x2", pick="home", rule="rule")
    original = deepcopy(rejected)
    audit = []
    as_of = datetime(2026, 9, 6, 11, tzinfo=timezone.utc)
    a = pt.filter_operational_pre_match_picks([rejected], as_of=as_of, min_lead=30, rejection_audit=audit)
    b = pt.filter_operational_pre_match_picks([deepcopy(original)], as_of=as_of, min_lead=30)
    assert a == b and rejected == original
    assert audit[0]["reason"] == "inside_30m_lead_or_started"
    assert audit[0]["evidence"]["min_lead_minutes"] == 30


def test_full_source_union_does_not_inflate_ml_scored_or_roi_universe(monkeypatch, tmp_path):
    monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: ([], MODEL))
    data = {"zulubet": {"key": row(), "solo": row(home="Porto", away="Estoril Praia")},
            "statarea": {"key": row()}}
    result, audit, _ = evaluate(data)
    out = scs.record_picks_build(day=DAY, scored_rows=result[0], slate_rows=result[0],
        scored_fixtures=audit, n_up=2, pipeline_scored_log=1, ml_scored_day=1, root=tmp_path)
    assert out["fixtures"] == 1
    report = scs.build_report(DAY, root=tmp_path, settled={})
    assert report["reconciliation"]["reconciliation_ok"] is True
    assert len(report["fixtures"]) == 1 and len(report["fixture_decisions"]) == 2
    assert report["counts"]["total_scored"] == 1
    attrition = report["source_attrition"]
    assert attrition["reason_counts"] == {"candidate_emitted": 1, "insufficient_probability_sources": 1}
    assert attrition["reconciliation_ok"] is True
    assert attrition["source_probability_coverage"]["zulubet"]["complete_probabilities"] == 2
    assert attrition["source_probability_coverage"]["statarea"]["complete_probabilities"] == 1
    assert "insufficient_probability_sources: 1" in scs.render_report(report)
    # Diagnostic-only full-union rows never produce settlement events.
    assert all(e["layer"] != "fixture_decision" for e in scs.settlement_events(report))


def test_prematch_rejections_no_longer_vanish_and_keep_separate_stage(tmp_path):
    r = row(market="1x2", pick="home", rule="test")
    scs.record_picks_build(day=DAY, scored_rows=[], slate_rows=[], root=tmp_path,
        generation_rejections=[{"row": r, "stage": "pre_match_guard", "reason": "missing_kickoff_same_day",
                                "evidence": {"min_lead_minutes": 30}}])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    assert report["counts"]["total_scored"] == 1
    candidate = report["candidates"][0]
    assert not candidate["selected_as_pick"]
    assert candidate["drop_stage"] == "pre_match_guard"
    assert candidate["rejection_reasons"][0]["code"] == "missing_kickoff_same_day"
    assert report["source_attrition"]["operational_candidate_rejections"] == {
        "pre_match_guard:missing_kickoff_same_day": 1}


def test_historical_run_does_not_borrow_later_or_earlier_diagnostics(tmp_path):
    _, audit, _ = evaluate({"zulubet": {"key": row()}})
    scs.record_picks_build(day=DAY, scored_rows=[], slate_rows=[], scored_fixtures=audit,
                          n_up=1, root=tmp_path, run_id="new-diagnostics")
    scs.record_picks_build(day=DAY, scored_rows=[], slate_rows=[], root=tmp_path,
                          n_up=10, run_id="legacy-later-run")
    r = scs.build_report(DAY, root=tmp_path, settled={})
    assert not r["source_attrition"]["available"]
    assert r["source_attrition"]["reason_counts"] == {}
    assert "Reasons unavailable" in scs.render_report(r)


def test_calendar_routing_reconciles_target_day_not_entire_scan(tmp_path):
    _, audit, _ = evaluate({"zulubet": {"key": row(), "other": row(home="Porto", away="Estoril Praia")}})
    audit[0]["trading_date"] = DAY
    audit[1]["trading_date"] = "2026-09-07"
    scs.record_picks_build(day=DAY, scored_rows=[], slate_rows=[], scored_fixtures=audit,
                          n_up=2, root=tmp_path)
    r = scs.build_report(DAY, root=tmp_path, settled={})["source_attrition"]
    assert r["scan_source_keys"] == 2
    assert r["expected_target_day_records"] == r["observed_target_day_records"] == 1
    assert r["reconciliation_ok"]
    assert any(e["event_type"] == "fixture_decision" for e in scs.read_ledger("2026-09-07", tmp_path))


def test_300_seeded_outputs_equal_immutable_prelogging_selector(monkeypatch):
    """Compare entire pick dicts, vetoes, counts and research records to git HEAD."""
    try:
        source = subprocess.check_output(["git", "show", "9e52ed25086113e32e1a7c8f6f7f2e9b283a36a6:scripts/picks_today.py"],
                                         text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pytest.skip("immutable baseline commit unavailable in this shallow checkout")
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "eval_1x2")
    rng = random.Random(20261019)
    for i in range(300):
        model = MODEL if i % 3 else None
        rules = [{"rule": "ml-meta avg_p>=40"}] if model and i % 2 else []
        fades = [{"rule": "ml-fade avg_p>=40"}] if model and i % 5 == 0 else []
        monkeypatch.setattr(pt, "load_ml_rules_and_model", lambda: (rules, model))
        monkeypatch.setattr(pt, "load_ml_fade_rules", lambda: fades)
        data = {s: {"key": row(rng.choice(["home", "draw", "away"]), rng.randint(40, 88))}
                for s in pt.SOURCES_1X2 if rng.random() < .65}
        edges = EDGE if i % 7 else {}
        namespace = dict(pt.__dict__)
        exec(compile(ast.Module(body=[node], type_ignores=[]), "baseline_eval_1x2", "exec"), namespace)
        old_collector, new_collector = pt.FadeResearchCollector(), pt.FadeResearchCollector()
        baseline = namespace["eval_1x2"](DAY, data, edges, source_weights={}, research_collector=old_collector)
        audited = pt.eval_1x2(DAY, data, edges, source_weights={}, fixture_audit=[], research_collector=new_collector)
        # Only the intentionally retired missing-Forebet HT numeric stand-ins
        # differ. Preserve the immutable comparison for every other field.
        if not data.get("forebet"):
            for record in [*baseline[0], *old_collector.rows]:
                for field in ("ml_ht_diff", "ml_ht_total"):
                    if field in record:
                        assert record[field] == 0
                        record[field] = None
        assert audited == baseline, i
        assert new_collector.scored == old_collector.scored
        assert new_collector.rows == old_collector.rows
        assert new_collector.draw_excluded == old_collector.draw_excluded


def test_storage_failure_cannot_change_emitted_candidates(monkeypatch, tmp_path):
    result, audit, _ = evaluate({"zulubet": {"key": row()}, "statarea": {"key": row()}})
    original = deepcopy(result)
    def fail(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr(scs, "_route_and_append", fail)
    assert scs.record_picks_build(day=DAY, scored_rows=result[0], slate_rows=result[0],
                                  scored_fixtures=audit, root=tmp_path) is None
    assert result == original


def test_logging_disabled_has_no_betting_effect_or_ledger_writes(monkeypatch, tmp_path):
    result, audit, _ = evaluate({"zulubet": {"key": row()}, "statarea": {"key": row()}})
    monkeypatch.setenv("EDGE_FACTORY_SCORED_SHADOW", "0")
    assert scs.record_picks_build(day=DAY, scored_rows=result[0], slate_rows=result[0],
                                  scored_fixtures=audit, root=tmp_path) is None
    assert not scs.ledger_path(DAY, tmp_path).exists()
    assert pt.eval_1x2(DAY, {"zulubet": {"key": row()}, "statarea": {"key": row()}},
                       EDGE, source_weights={}) == result


def test_bucket_floor_diagnostic_is_not_mislabeled_as_source_disagreement(tmp_path):
    candidate = row(market="1x2", pick="home", rule="rule", odds=1.2,
                    bucket_drop_reason="unknown_odds_band_no_evidence")
    scs.record_picks_build(day=DAY, scored_rows=[candidate], slate_rows=[],
                          pre_collapse_rows=[], root=tmp_path)
    r = scs.build_report(DAY, root=tmp_path, settled={})
    assert r["source_attrition"]["operational_candidate_rejections"] == {
        "bucket_assignment:unknown_odds_band_no_evidence": 1}
    reason = r["candidates"][0]["rejection_reasons"][0]
    assert reason["observed_odds"] == 1.2


def test_live_main_threads_guard_rejections_into_existing_ledger_hook():
    import inspect
    tree = ast.parse(inspect.getsource(pt.main))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    guard = next(n for n in calls if isinstance(n.func, ast.Name)
                 and n.func.id == "filter_operational_pre_match_picks")
    ledger = next(n for n in calls if isinstance(n.func, ast.Attribute)
                  and n.func.attr == "record_picks_build")
    assert next(k.value.id for k in guard.keywords if k.arg == "rejection_audit") == "generation_rejections"
    assert next(k.value.id for k in ledger.keywords if k.arg == "generation_rejections") == "generation_rejections"
