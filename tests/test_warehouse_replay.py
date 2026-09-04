"""Tests for the warehouse-reconstruction feasibility auditor + engine parity.

Two jobs:

1. Pin the research knob OFF and keep it off the live path. Nothing in this
   family may ever be reachable from ``scripts/auto_tickets.py``.
2. Assert engine parity the way the 2026-09-04 post-merge correction says it
   must be asserted: ZERO leg-selection differences against the previous main
   on every archived day, and total staked within 0.01pp. Byte-equality is the
   wrong test — stakes round to 4 decimals and the day cap redistributes the
   remainder, so a strict byte check cries wolf on a good change.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgefactory import warehouse_replay as wr  # noqa: E402

BASELINE = ROOT / "tests" / "data" / "engine_parity_baseline.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def at():
    return _load(ROOT / "scripts" / "auto_tickets.py", "at_under_test")


# --------------------------------------------------------------------------
# 1. the research knob defaults OFF and stays off the live path
# --------------------------------------------------------------------------
def test_feasibility_audit_defaults_off():
    assert wr.ENABLED_BY_DEFAULT is False


def test_auto_tickets_does_not_import_the_research_module():
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    assert "warehouse_replay" not in src


def test_daily_pipeline_does_not_invoke_the_audit():
    for name in ("daily.py", "auto_tickets.py", "picks_today.py"):
        src = (ROOT / "scripts" / name).read_text()
        assert "--warehouse-replay" not in src


def test_audit_flag_is_opt_in_only():
    src = (ROOT / "scripts" / "replay_harness.py").read_text()
    # present as a flag...
    assert '"--warehouse-replay"' in src
    # ...and guarded by an explicit truthiness check, never a default branch
    assert "if args.warehouse_replay:" in src


def test_live_recipe_constants_unchanged(at):
    """The feasibility work must not have moved a single live setting."""
    assert at.STAKE_FRAC == pytest.approx(1.0 / 3.0)
    assert at.STAKE_MODE == "per_day"
    assert at.STAKE_PER_ACCA is None
    assert at.STAKE_WEIGHTS is None
    assert at.MAX_ACCAS == 3
    assert at.MIN_ACCAS == 1
    assert at.LEGS_PER_ACCA == 2
    assert at.MIN_LEG_ODDS == 1.20
    assert at.VOLUME_POOL == 12
    assert at.VOLUME_MIN_PROB == 0.65
    assert at.GATE_MODE == "off"


# --------------------------------------------------------------------------
# 2. engine parity — the assertion the post-merge correction demands
# --------------------------------------------------------------------------
def _snapshot(mod, archives, days):
    out = {}
    for d in days:
        pool = mod.playable_legs(archives, day=d)
        plan = mod.plan_day(pool, 100.0)
        out[d] = {
            "legs": [[[l["match"], l["pick"], round(l["odds"], 4)] for l in a["legs"]]
                     for a in plan],
            "staked": round(sum(a["stake_pct"] for a in plan), 6),
        }
    return out


@pytest.fixture(scope="module")
def parity(at):
    baseline = json.loads(BASELINE.read_text())
    archives = at.load_archived_picks()
    days = sorted(baseline["days"])
    return baseline, _snapshot(at, archives, days), days


def test_parity_baseline_covers_the_whole_archive(parity):
    baseline, _, days = parity
    assert len(days) == 80, "the archive is 80 days; baseline must cover all of them"
    assert baseline["base_commit"]


def test_zero_leg_selection_differences_vs_previous_main(parity):
    baseline, current, days = parity
    diffs = [d for d in days if current[d]["legs"] != baseline["days"][d]["legs"]]
    assert diffs == [], (
        f"{len(diffs)} archived day(s) changed leg selection: {diffs[:5]}. "
        "Live behaviour must be identical; selection is not a research knob.")


def test_total_staked_within_one_hundredth_of_a_percentage_point(parity):
    baseline, current, days = parity
    worst_day, worst = None, 0.0
    for d in days:
        delta = abs(current[d]["staked"] - baseline["days"][d]["staked"])
        if delta > worst:
            worst_day, worst = d, delta
    assert worst <= 0.01, (
        f"total staked moved {worst:.6f}pp on {worst_day}; the parity tolerance "
        "is 0.01pp (one cent on a R100 bank).")


# --------------------------------------------------------------------------
# 3. the auditor's own logic
# --------------------------------------------------------------------------
def test_missing_sources_are_named_not_assumed():
    assert "vitibet" in wr.MISSING_PREDICTION_SOURCES
    assert "vitibet" not in wr.ON_DISK_PREDICTION_SOURCES
    assert "scoutingstats_odds" in wr.MISSING_ODDS_SOURCES


def test_closing_odds_are_not_treated_as_bet_time_prices():
    """BetExplorer is closing; the engine bets ~30+ min before kickoff."""
    assert "betexplorer_odds" in wr.CLOSING_ONLY_ODDS_SOURCES
    assert "betexplorer_odds" not in wr.ON_DISK_ODDS_SOURCES


def test_half_time_score_features_are_flagged_post_kickoff():
    assert wr.ML_META_FEATURE_AVAILABILITY["ht_diff"] == "post_kickoff"
    assert wr.ML_META_FEATURE_AVAILABILITY["ht_total"] == "post_kickoff"


def test_leak_swing_is_positive_for_a_home_half_time_lead():
    feats = wr.classify_ml_features(
        ["ht_diff", "ht_total", "is_home"], [0.2395, 0.1910, 0.7791])
    swing = wr.leak_logit_swing(feats, ht_diff=2.0, ht_total=2.0)
    assert swing == pytest.approx(0.861, abs=1e-3)
    # a pre-kickoff feature must never contribute to the leak estimate
    assert wr.leak_logit_swing(
        wr.classify_ml_features(["is_home"], [0.7791])) == 0.0


def test_dependency_census_counts_the_ceiling_conjunctively():
    legs = [
        # reconstructable: source vote, on-disk sources, historical odds
        {"row": {"rule": "2way-unanimous avg_p>=70",
                 "sources_used": ["forebet", "zulubet"],
                 "odds_source": "forebet_best"}},
        # ml-meta: excluded even though its inputs are on disk
        {"row": {"rule": "ml-meta avg_p>=55",
                 "sources_used": ["forebet", "statarea"],
                 "odds_source": "forebet_best"}},
        # missing source
        {"row": {"rule": "2way-unanimous avg_p>=70",
                 "sources_used": ["statarea", "vitibet"],
                 "odds_source": "forebet_best"}},
        # missing odds history
        {"row": {"rule": "2way-unanimous avg_p>=70",
                 "sources_used": ["forebet", "zulubet"],
                 "odds_source": "scoutingstats_odds"}},
    ]
    c = wr.dependency_census(legs)
    assert c.legs == 4
    assert c.source_vote == 3
    assert c.on_disk_sources == 3
    assert c.historical_odds == 3
    assert c.ceiling == 1
    assert c.source_hits["vitibet"] == 1


def test_gate_verdict_fails_on_absent_inputs():
    cov = {"coverage_frac": 0.0}
    gate = {"recall": 0.0, "precision": 0.0, "odds_mismatch_frac": None}
    ok, reasons = wr.gate_verdict(cov, gate)
    assert ok is False
    assert any("input coverage" in r for r in reasons)
    assert any("recall" in r for r in reasons)


def test_gate_verdict_passes_only_on_a_clean_sweep():
    cov = {"coverage_frac": 1.0}
    gate = {"recall": 0.97, "precision": 0.96, "odds_mismatch_frac": 0.01}
    ok, reasons = wr.gate_verdict(cov, gate)
    assert ok is True
    assert reasons == ["all bar criteria met"]


def test_gate_verdict_fails_on_odds_mismatch_alone():
    cov = {"coverage_frac": 1.0}
    gate = {"recall": 0.99, "precision": 0.99, "odds_mismatch_frac": 0.30}
    ok, reasons = wr.gate_verdict(cov, gate)
    assert ok is False
    assert any("odds mismatch" in r for r in reasons)


def test_validation_gate_scores_a_synthetic_perfect_recovery():
    from edgefactory.util import norm_team

    class FakeCon:
        def execute(self, sql, params=None):
            self._sql = sql
            return self

        def fetchall(self):
            if "consensus2" in self._sql:
                return [("Alpha FC", "Beta United", "home", 74.0, 1.45)]
            return []

    live = {"2026-01-01": [{"match": "Alpha FC vs Beta United",
                            "pick": "HOME", "prob": 0.74, "odds": 1.45}]}
    res = wr.validation_gate(FakeCon(), live, 1.20, norm_team)
    assert res["tp"] == 1 and res["fp"] == 0 and res["fn"] == 0
    assert res["recall"] == 1.0 and res["precision"] == 1.0
    assert res["odds_mismatch_frac"] == 0.0


def test_validation_gate_counts_a_side_flip_as_a_miss():
    from edgefactory.util import norm_team

    class FakeCon:
        def execute(self, sql, params=None):
            self._sql = sql
            return self

        def fetchall(self):
            if "consensus2" in self._sql:
                return [("Alpha FC", "Beta United", "away", 74.0, 1.45)]
            return []

    live = {"2026-01-01": [{"match": "Alpha FC vs Beta United",
                            "pick": "HOME", "prob": 0.74, "odds": 1.45}]}
    res = wr.validation_gate(FakeCon(), live, 1.20, norm_team)
    assert res["tp"] == 0 and res["fp"] == 1 and res["fn"] == 1


# --------------------------------------------------------------------------
# 4. checkpoint ⑫ — the rule-family report is read-only research
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def rh():
    return _load(ROOT / "scripts" / "replay_harness.py", "rh_under_test")


def test_rules_command_is_opt_in_and_changes_no_default():
    src = (ROOT / "scripts" / "replay_harness.py").read_text()
    assert '"--rules"' in src
    assert "if args.rules:" in src
    for name in ("daily.py", "auto_tickets.py", "picks_today.py"):
        assert "--rules" not in (ROOT / "scripts" / name).read_text()


def test_rule_family_grouping(rh):
    assert rh.rule_family("ml-meta avg_p>=55") == "ml-meta"
    assert rh.rule_family("ml-meta avg_p>=60") == "ml-meta"
    assert rh.rule_family("2way-unanimous avg_p>=70") == "2way-unanimous"
    assert rh.rule_family("2way+bc-confirms avg_p>=60") == "2way-unanimous"
    assert rh.rule_family("3way-unanimous home-only avg_p>=65") == "3way-unanimous"
    assert rh.rule_family("ou25-unanimous-2way-sa avg_p>=70") == "other"
    assert rh.rule_family(None) == "other"


def test_leg_stats_reports_underconfidence_with_the_right_sign(rh):
    """gap = realised - stated; POSITIVE must mean 'wins more than it claims'."""
    legs = [{"prob": 0.60, "odds": 2.0, "result": "win"} for _ in range(80)]
    legs += [{"prob": 0.60, "odds": 2.0, "result": "loss"} for _ in range(20)]
    s = rh._leg_stats(legs)
    assert s["n"] == 100
    assert s["hit"] == pytest.approx(0.80)
    assert s["stated"] == pytest.approx(0.60)
    assert s["gap"] == pytest.approx(0.20)      # under-confident by 20pp
    assert s["gap_p10"] > 0
    assert s["roi"] == pytest.approx(0.60)      # 80 * 1.0 - 20 * 1.0 over 100


def test_leg_stats_flags_overconfidence_negatively(rh):
    legs = [{"prob": 0.90, "odds": 1.10, "result": "win"} for _ in range(50)]
    legs += [{"prob": 0.90, "odds": 1.10, "result": "loss"} for _ in range(50)]
    s = rh._leg_stats(legs)
    assert s["gap"] == pytest.approx(-0.40)
    assert s["roi"] < 0


def test_leg_stats_handles_the_empty_family(rh):
    assert rh._leg_stats([]) is None


# --------------------------------------------------------------------------
# 5. checkpoint ⑫ tripwire — the ml-meta serve-time contract
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def pt():
    return _load(ROOT / "scripts" / "picks_today.py", "pt_under_test")


def test_contract_features_are_the_two_post_kickoff_ones(pt):
    assert pt.ML_META_CONSTANT_FEATURES == ("ht_diff", "ht_total")


def test_contract_holds_silently_for_normal_pre_kickoff_picks(pt):
    """The all-zero case is every run to date: no breach, no noise."""
    picks = [
        {"rule": "ml-meta avg_p>=55", "match": "A vs B",
         "ml_ht_diff": 0, "ml_ht_total": 0},
        {"rule": "ml-meta avg_p>=60", "match": "C vs D",
         "ml_ht_diff": 0.0, "ml_ht_total": 0.0},
        {"rule": "2way-unanimous avg_p>=70", "match": "E vs F"},
    ]
    assert pt.ml_meta_contract_breaches(picks) == []


def test_contract_catches_an_in_match_score_reaching_the_model(pt):
    picks = [{"rule": "ml-meta avg_p>=55", "match": "A vs B", "date": "2026-09-05",
              "ml_ht_diff": 2, "ml_ht_total": 2}]
    breaches = pt.ml_meta_contract_breaches(picks)
    assert len(breaches) == 1
    assert breaches[0]["match"] == "A vs B"
    assert breaches[0]["features"] == {"ht_diff": 2, "ht_total": 2}


def test_contract_catches_a_lone_nonzero_total(pt):
    """A 1-1 half-time has ht_diff 0 but ht_total 2 — must still trip."""
    picks = [{"rule": "ml-meta avg_p>=55", "match": "A vs B",
              "ml_ht_diff": 0, "ml_ht_total": 2}]
    breaches = pt.ml_meta_contract_breaches(picks)
    assert len(breaches) == 1
    assert breaches[0]["features"] == {"ht_total": 2}


def test_contract_ignores_non_ml_meta_rules(pt):
    """Only the ml-meta operating point depends on the constant."""
    picks = [{"rule": "2way-unanimous avg_p>=70", "match": "A vs B",
              "ml_ht_diff": 3, "ml_ht_total": 5}]
    assert pt.ml_meta_contract_breaches(picks) == []


def test_contract_is_checked_after_the_pre_match_guard(pt):
    """Checked earlier it would fire daily on already-kicked-off fixtures."""
    src = (ROOT / "scripts" / "picks_today.py").read_text()
    guard = src.index("filter_operational_pre_match_picks(\n            picks,")
    check = src.index("_breaches = ml_meta_contract_breaches(picks)")
    assert guard < check, "the tripwire must run on bettable picks only"


def test_breached_picks_are_withheld_not_merely_logged():
    src = (ROOT / "scripts" / "picks_today.py").read_text()
    body = src[src.index("_breaches = ml_meta_contract_breaches(picks)"):]
    assert "picks = [p for p in picks" in body[:600], "must fail closed"


# --------------------------------------------------------------------------
# 6. checkpoint ⑬ — the 3way research rank defaults OFF
# --------------------------------------------------------------------------
def test_rule3way_rank_is_not_the_default(at):
    legs = [
        {"prob": 0.80, "odds": 1.50, "row": {"rule": "ml-meta avg_p>=55"}},
        {"prob": 0.60, "odds": 2.00, "row": {"rule": "3way-unanimous avg_p>=65"}},
    ]
    # live ranking is by stated probability — the ml-meta leg leads
    assert at.rank_legs(legs)[0]["prob"] == 0.80
    assert at.rank_legs(legs, "prob")[0]["prob"] == 0.80
    # only the explicit research rank promotes the 3way leg
    assert at.rank_legs(legs, "rule3way")[0]["prob"] == 0.60


def test_rule3way_rank_tolerates_legs_without_an_archived_row(at):
    legs = [{"prob": 0.70, "odds": 1.40}, {"prob": 0.60, "odds": 2.00}]
    assert [l["prob"] for l in at.rank_legs(legs, "rule3way")] == [0.70, 0.60]
