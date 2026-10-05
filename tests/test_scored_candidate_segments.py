"""Segment analysis for the shadow ledger — AUDIT ONLY contracts.

Pins: aggregation by single/compound dimensions, promotion-readiness tiers
(EXECUTION_SAFE_PROMOTION_CANDIDATE reachable only from the execution-safe
population), anti-overfit guards (sample thresholds, day/fixture/source
concentration, stale-only-profit), pending/unmatched never losses,
baseline lift, machine-readable JSON output, and graceful behavior when
no ledger exists. Nothing here touches live betting behavior.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory import scored_candidate_segments as seg  # noqa: E402
from edgefactory import scored_candidate_shadow as scs  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402

D1, D2, D3 = "2026-09-04", "2026-09-05", "2026-09-06"

SMALL = dict(min_settled=4, min_days=2, min_fixtures=3,
             watch_min_settled=2, max_day_concentration=0.9,
             max_fixture_concentration=0.5, max_pending_share=0.5)


def _rec(date=D1, *, roi_type=seg.ROI_CAPTURED, fixture="fx", league="L1",
         source="zulubet", status="win", odds=2.0, stale=False,
         gradeable=True, gradeable_reason="captured_pre_kickoff_proven",
         promotion_state="scored_not_promoted", reasons=("no_candidate_emitted",),
         bucket="B1", price_kind="unregistered_source", exec_safe=None,
         exec_safe_support=False, **over):
    exec_safe = (roi_type == seg.ROI_EXEC_SAFE) if exec_safe is None else exec_safe
    ret = None
    if gradeable and status in ("win", "loss", "void"):
        ret = {"win": odds - 1.0, "loss": -1.0, "void": 0.0}[status]
    r = {
        "roi_type": roi_type, "date": date, "weekday": seg.weekday_of(date),
        "fixture_id": f"{fixture}-{date}", "promotion_state": promotion_state,
        "reasons": list(reasons), "bucket": bucket, "rule_model": "ml",
        "market": "1x2", "selection_side": "home", "league": league,
        "competition_key": league.lower(), "country": "PT",
        "price_source": source, "bookmaker": None, "price_kind": price_kind,
        "stale": stale, "registered_source": False,
        "execution_safe": exec_safe, "gradeable": gradeable,
        "gradeable_reason": gradeable_reason,
        "kickoff_proof": "instants_proven", "odds_band": seg.odds_band(odds),
        "probability_band": "0.60-0.69", "score_band": "unknown",
        "price_age_band": "fetched_this_run", "odds": odds if gradeable else None,
        "status": status if gradeable else None, "ret": ret,
        "exec_safe_support": exec_safe or exec_safe_support,
    }
    r.update(over)
    return r


def _spread(n, *, days=(D1, D2, D3), status_fn=lambda i: "win", **kw):
    """n records spread over days and distinct fixtures."""
    return [_rec(days[i % len(days)], fixture=f"fx{i}",
                 status=status_fn(i), **kw) for i in range(n)]


# --------------------------------------------------- aggregation contracts --
def test_single_dimension_aggregation():
    recs = [_rec(league="L1", status="win"), _rec(league="L1", status="loss",
                                                  fixture="fx2"),
            _rec(league="L2", status="win", fixture="fx3")]
    segs = seg.build_segments(recs, ["league"])
    l1 = segs["league=L1"]
    assert l1["total_records"] == 2 and l1["settled_records"] == 2
    assert l1["wins"] == 1 and l1["losses"] == 1
    assert l1["flat_profit_units"] == 0.0 and l1["flat_roi"] == 0.0
    l2 = segs["league=L2"]
    assert l2["wins"] == 1 and l2["flat_profit_units"] == 1.0
    assert l2["flat_roi"] == 1.0


def test_compound_dimension_aggregation_depth_two():
    recs = [_rec(reasons=["kickoff_guard"], bucket="A"),
            _rec(reasons=["kickoff_guard"], bucket="B", fixture="fx2"),
            _rec(reasons=["odds_floor", "kickoff_guard"], bucket="A",
                 fixture="fx3")]
    segs = seg.build_segments(recs, [("reason", "bucket")])
    assert segs["reason=kickoff_guard|bucket=A"]["total_records"] == 2
    assert segs["reason=kickoff_guard|bucket=B"]["total_records"] == 1
    # multi-reason records fan out into each reason segment (never dropped)
    assert segs["reason=odds_floor|bucket=A"]["total_records"] == 1
    assert segs["reason=kickoff_guard|bucket=A"]["dimensions"] == {
        "reason": "kickoff_guard", "bucket": "A"}


def test_metrics_include_odds_and_distincts():
    recs = [_rec(odds=1.5), _rec(odds=2.5, fixture="fx2", date=D2,
                                 league="L2", source="bzzoiro")]
    s = seg.build_segments(recs, ["market"])["market=1x2"]
    assert s["average_odds"] == 2.0 and s["median_odds"] == 2.0
    assert s["min_odds"] == 1.5 and s["max_odds"] == 2.5
    assert s["distinct_days"] == 2 and s["distinct_fixtures"] == 2
    assert s["distinct_leagues"] == 2 and s["distinct_sources"] == 2
    assert s["fresh_count"] == 2 and s["stale_count"] == 0


# ------------------------------------------------------------- tier logic --
def _classify(recs, roi_type=seg.ROI_CAPTURED, **over):
    segs = seg.build_segments(recs, ["market"])
    params = dict(SMALL)
    params.update(over)
    s = segs["market=1x2"]
    return s, seg.classify_segment(s, roi_type=roi_type, **params)


def test_captured_positive_thresholds_met_no_exec_support_is_price_enrichment():
    recs = _spread(6)
    _, v = _classify(recs)
    assert v["tier"] == seg.TIER_PRICE_ENRICH
    assert v["action"] == "PRICE_ENRICHMENT"
    assert "not_execution_safe" in v["warnings"]
    assert "audit_only_prices" in v["warnings"]


def test_captured_positive_with_exec_support_is_shadow_promotion_candidate():
    recs = _spread(6, exec_safe_support=True)
    for r in recs:
        r["exec_safe_support"] = True
    # exec support counted via execution_safe_count on candidate overlap:
    segs = seg.build_segments(recs, ["market"])
    s = segs["market=1x2"]
    s["execution_safe_count"] = 3   # overlap with exec-safe candidates
    v = seg.classify_segment(s, roi_type=seg.ROI_CAPTURED, **SMALL)
    assert v["tier"] == seg.TIER_SHADOW_PROMO
    assert v["action"] == "PROMOTION_REVIEW_AUDIT_PRICES_ONLY"


def test_captured_positive_below_thresholds_is_watchlist():
    recs = _spread(3, days=(D1, D2))        # settled=3 < min_settled=4
    _, v = _classify(recs)
    assert v["tier"] == seg.TIER_WATCHLIST


def test_small_sample_high_roi_stays_insufficient_sample():
    recs = [_rec(odds=9.0, status="win")]   # +800% ROI, n=1
    _, v = _classify(recs)
    assert v["tier"] == seg.TIER_INSUFFICIENT
    assert v["action"] == "COLLECT_MORE_EVIDENCE"


def test_negative_segment_is_blocked():
    recs = _spread(6, status_fn=lambda i: "loss")
    _, v = _classify(recs)
    assert v["tier"] == seg.TIER_BLOCKED
    assert v["action"] == "KEEP_BLOCKED"


def test_exec_safe_positive_spread_becomes_promotion_candidate():
    recs = _spread(6, roi_type=seg.ROI_EXEC_SAFE,
                   gradeable_reason="execution_safe_named_book")
    _, v = _classify(recs, roi_type=seg.ROI_EXEC_SAFE)
    assert v["tier"] == seg.TIER_EXEC_PROMO
    assert v["action"] == "PROMOTION_REVIEW"
    assert "audit_only_prices" not in v["warnings"]


def test_captured_population_can_never_reach_exec_promo_tier():
    recs = _spread(12)                       # robust, positive, multi-day
    _, v = _classify(recs)
    assert v["tier"] != seg.TIER_EXEC_PROMO  # by construction


def test_stale_only_positive_is_watch_stale_artifact_never_promotable():
    recs = _spread(6, stale=True)
    _, v = _classify(recs)
    assert v["tier"] == seg.TIER_WATCHLIST
    assert "stale_only_profit" in v["warnings"]
    assert v["action"] == "WATCH_STALE_ARTIFACT"


def test_stale_profit_with_fresh_confirmation_is_not_flagged_stale_only():
    recs = _spread(4, stale=True) + _spread(4, stale=False)
    # distinct fixtures across both halves
    for i, r in enumerate(recs):
        r["fixture_id"] = f"u{i}-{r['date']}"
    _, v = _classify(recs)
    assert "stale_only_profit" not in v["warnings"]


def test_unregistered_source_positive_never_execution_safe_tier():
    recs = _spread(6, price_kind="unregistered_source")
    _, v = _classify(recs)
    assert v["tier"] in (seg.TIER_PRICE_ENRICH, seg.TIER_SHADOW_PROMO,
                         seg.TIER_WATCHLIST)
    assert v["tier"] != seg.TIER_EXEC_PROMO


def test_fair_model_segment_labelled_audit_only_never_exec():
    recs = _spread(6, price_kind="fair_model", source="betbetter_fair")
    segs = seg.build_segments(recs, ["price_kind"])
    s = segs["price_kind=fair_model"]
    v = seg.classify_segment(s, roi_type=seg.ROI_CAPTURED, **SMALL)
    assert v["tier"] != seg.TIER_EXEC_PROMO
    assert "audit_only_prices" in v["warnings"]


def test_pending_records_never_counted_as_losses():
    recs = _spread(4) + [_rec(status="pending", ret=None, fixture="fxp"),
                         _rec(status="pending", ret=None, fixture="fxq")]
    s, _ = _classify(recs)
    assert s["pending"] == 2
    assert s["losses"] == 0
    assert s["settled_records"] == 4
    assert s["flat_profit_units"] == 4.0        # 4 wins at 2.0


def test_unmatched_records_never_counted_as_losses():
    recs = _spread(4) + [_rec(status="unmatched", ret=None, fixture="fxu")]
    s, _ = _classify(recs)
    assert s["unmatched"] == 1 and s["losses"] == 0
    assert s["settled_records"] == 4


def test_single_day_domination_gets_concentration_warning_blocks_promo():
    recs = [_rec(D1, fixture=f"fx{i}", roi_type=seg.ROI_EXEC_SAFE)
            for i in range(5)] + [_rec(D2, fixture="fxx",
                                       roi_type=seg.ROI_EXEC_SAFE)]
    _, v = _classify(recs, roi_type=seg.ROI_EXEC_SAFE,
                     max_day_concentration=0.6)
    assert "concentration_day_or_fixture" in v["warnings"]
    assert v["tier"] == seg.TIER_WATCHLIST      # not EXEC_PROMO


def test_single_fixture_domination_blocks_promo():
    recs = [_rec(D1 if i % 2 else D2, fixture="samefx",
                 roi_type=seg.ROI_EXEC_SAFE) for i in range(6)]
    for r in recs:
        r["fixture_id"] = "samefx"              # all settled on one fixture
    _, v = _classify(recs, roi_type=seg.ROI_EXEC_SAFE)
    assert "concentration_day_or_fixture" in v["warnings"]
    assert v["tier"] != seg.TIER_EXEC_PROMO


def test_high_pending_share_blocks_promo():
    recs = _spread(4, roi_type=seg.ROI_EXEC_SAFE) + [
        _rec(status="pending", ret=None, fixture=f"fxp{i}",
             roi_type=seg.ROI_EXEC_SAFE) for i in range(8)]
    _, v = _classify(recs, roi_type=seg.ROI_EXEC_SAFE)
    assert "high_pending_unmatched_share" in v["warnings"]
    assert v["tier"] == seg.TIER_WATCHLIST


# ----------------------------------------------- ledger integration window --
def _teamcode(i):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return letters[i // 26] + letters[i % 26]


def _fx(day, i, **over):
    e = {"kind": "ml_scored_fixture", "home": f"{_teamcode(i)}holm",
         "away": f"{_teamcode(i)}berg", "league": "Portugal,Primeira Liga",
         "kickoff": f"{day}T18:30:00+00:00", "sport": "soccer",
         "trading_date": day, "ml_probability": 0.65,
         "ml_majority_pick": "home", "sources_used": ["zulubet"],
         "market": "1x2", "selection": "home",
         "selection_team": f"{_teamcode(i)}holm", "shadow_price": 2.0,
         "shadow_price_source": "zulubet",
         "shadow_price_captured_at_utc": f"{day}T06:00:00+00:00",
         "shadow_price_as_of_basis": "fetched_this_run"}
    e.update(over)
    return e


def _ledger_window(tmp_path):
    settled = {}
    for day in (D1, D2, D3):
        fixtures = [_fx(day, i) for i in range(6)]
        scs.record_picks_build(day=day, scored_rows=[], slate_rows=[],
                               pipeline_scored_log=6, scored_fixtures=fixtures,
                               ml_scored_day=6, n_up=6, root=tmp_path)
        for i, f in enumerate(fixtures):
            settled[(day, norm_team(f["home"]), norm_team(f["away"]))] = (
                "home" if i < 4 else "away")   # 4 wins / 2 losses per day
    return settled


def test_window_report_baseline_lift_and_sections(tmp_path):
    settled = _ledger_window(tmp_path)
    report = seg.build_segment_report(
        seg.date_range(D1, D3), root=tmp_path, settled=settled, **SMALL)
    # baseline: 18 settled, 12 wins at 2.0, 6 losses -> +6u, roi=+33.3%
    base = report["baselines"][seg.ROI_CAPTURED]["all_scored"]
    assert base["settled_records"] == 18
    assert base["flat_profit_units"] == 6.0
    assert round(base["flat_roi"], 4) == round(6.0 / 18, 4)
    # a full-pool segment has zero lift vs its own baseline
    full = next(s for s in report["segments"]
                if s["segment_key"] == "market=1x2"
                and s["roi_type"] == seg.ROI_CAPTURED)
    assert full["lift_vs_baseline"] == 0.0
    assert full["baseline_roi"] == base["flat_roi"]
    # required sections present
    for key in ("top_positive_captured", "top_positive_execution_safe",
                "promotion_candidates", "shadow_promotion_candidates",
                "price_enrichment_candidates", "watchlist",
                "blocked_negative", "quality_warnings", "baselines"):
        assert key in report, key
    # robust multi-day captured-price segment -> price enrichment candidate
    assert any(s["segment_key"] == "market=1x2"
               for s in report["price_enrichment_candidates"])
    text = seg.render_segment_report(report)
    assert seg.AUDIT_BANNER in text
    assert seg.NO_BEHAVIOR_LINE in text
    assert "PROMOTION CANDIDATES (EXECUTION_SAFE_PROMOTION_CANDIDATE)" in text
    assert "PRICE ENRICHMENT CANDIDATES" in text


def test_json_output_is_machine_readable(tmp_path):
    settled = _ledger_window(tmp_path)
    report = seg.build_segment_report([D1, D2, D3], root=tmp_path,
                                      settled=settled, **SMALL)
    payload = json.loads(json.dumps(report, default=str))
    s = payload["price_enrichment_candidates"][0]
    for key in ("segment_key", "dimensions", "roi_type", "tier", "action",
                "action_reason", "warnings", "settled_records", "flat_roi",
                "flat_profit_units", "baseline_roi", "lift_vs_baseline",
                "confidence"):
        assert key in s, key
    assert s["tier"] == "PRICE_ENRICHMENT_CANDIDATE"
    conf = s["confidence"]
    for key in ("worst_day_roi", "positive_days", "max_day_concentration",
                "max_fixture_concentration", "max_source_concentration",
                "lower_confidence_bound_roi"):
        assert key in conf, key
    assert payload["audit_banner"] == seg.AUDIT_BANNER
    assert payload["no_behavior_change"] == seg.NO_BEHAVIOR_LINE


def test_empty_root_degrades_gracefully_no_behavior_impact(tmp_path):
    report = seg.build_segment_report([D1, D2], root=tmp_path, settled={},
                                      **SMALL)
    assert report["days_without_ledger"] == [D1, D2]
    assert report["segments"] == []
    assert report["promotion_candidates"] == []
    text = seg.render_segment_report(report)
    assert "(none)" in text
    assert seg.NO_BEHAVIOR_LINE in text


def test_reading_ledger_never_mutates_it(tmp_path):
    settled = _ledger_window(tmp_path)
    paths = sorted(tmp_path.glob("scored_candidate_shadow_*.jsonl"))
    before = [p.read_bytes() for p in paths]
    seg.build_segment_report([D1, D2, D3], root=tmp_path, settled=settled,
                             **SMALL)
    after = [p.read_bytes() for p in paths]
    assert before == after                     # byte-identical, read-only


# ------------------------- end-to-end exec-promo + rolling survival ---------
def _exec_cand(day, i, *, odds=2.0):
    """Named-book execution-safe candidate row (ledger-real shape)."""
    return {
        "date": day, "home": f"{_teamcode(i)}holm", "away": f"{_teamcode(i)}berg",
        "league": "Portugal,Primeira Liga", "market": "1x2", "pick": "home",
        "rule": "ml-consensus", "bucket": "CERTIFIED_CLEAN", "avg_p": 70.0,
        "w_score": 1.0, "odds": odds, "odds_source": "bzzoiro_odds",
        "bookmaker": "BookyBook", "price_evidence": "NAMED_BOOKMAKER_PRICE",
        "price_push_eligible": True, "quarantine": "none",
        "kickoff_utc": f"{day}T18:30:00+00:00",
        "as_of": f"{day}T06:00:00+00:00",
    }


def _exec_ledger(tmp_path, days=(D1, D2, D3), per_day=4):
    settled = {}
    for day in days:
        cands = [_exec_cand(day, i) for i in range(per_day)]
        scs.record_picks_build(day=day, scored_rows=cands, slate_rows=cands,
                               pipeline_scored_log=per_day,
                               price_supported_markets={"1x2"}, root=tmp_path)
        for c in cands:
            settled[(day, norm_team(c["home"]), norm_team(c["away"]))] = "home"
    return settled


def test_exec_promo_reachable_end_to_end_through_real_ledger(tmp_path):
    """The reviewer's verification: EXECUTION_SAFE_PROMOTION_CANDIDATE must
    actually be REACHABLE from the execution-safe population in real report
    output (not only in classifier unit tests) — while remaining
    structurally unreachable for every captured-price segment in the same
    report."""
    settled = _exec_ledger(tmp_path)
    report = seg.build_segment_report(
        seg.date_range(D1, D3), root=tmp_path, settled=settled, **SMALL)
    promo = report["promotion_candidates"]
    assert promo, "exec-safe promotion tier must be reachable end-to-end"
    assert all(s["roi_type"] == seg.ROI_EXEC_SAFE for s in promo)
    full = next(s for s in promo if s["segment_key"] == "market=1x2")
    assert full["settled_records"] == 12 and full["flat_roi"] == 1.0
    assert full["action"] == "PROMOTION_REVIEW"
    # and in the SAME report no captured-price segment reaches the tier
    assert all(s["tier"] != seg.TIER_EXEC_PROMO
               for s in report["segments"]
               if s["roi_type"] == seg.ROI_CAPTURED)
    text = seg.render_segment_report(report)
    assert "PROMOTION CANDIDATES (EXECUTION_SAFE_PROMOTION_CANDIDATE)" in text
    assert seg.NO_BEHAVIOR_LINE in text


def test_window_profiles_scale_with_length():
    assert seg.window_profile(7) == {"min_settled": 30, "min_days": 3,
                                     "min_fixtures": 20}
    assert seg.window_profile(14) == {"min_settled": 50, "min_days": 5,
                                      "min_fixtures": 35}
    assert seg.window_profile(30) == {"min_settled": 90, "min_days": 8,
                                      "min_fixtures": 60}
    # unlisted lengths: linear from the 7-day base, never BELOW it
    p10 = seg.window_profile(10)
    assert p10 == {"min_settled": 43, "min_days": 4, "min_fixtures": 29}
    assert seg.window_profile(2) == {"min_settled": 30, "min_days": 3,
                                     "min_fixtures": 20}


def test_rolling_survivor_under_overrides_is_exploratory_only(tmp_path):
    """Operator rule: overridden thresholds can NEVER mint promotion-
    proposal material — an all-window survivor under overrides is labelled
    exploratory and promotion_proposal_ready stays empty."""
    settled = _exec_ledger(tmp_path)          # data on D1..D3
    overrides = dict(min_settled=4, min_days=3, min_fixtures=3)
    # both windows span all 3 data days -> survives, but under overrides
    rep = seg.build_rolling_report(D3, windows=(3, 4), root=tmp_path,
                                   settled=settled,
                                   threshold_overrides=overrides,
                                   watch_min_settled=2)
    assert rep["promotion_proposal_ready"] == []
    entry = next(e for e in rep["exploratory_survivors"]
                 if e["segment_key"] == "market=1x2")
    assert entry["survival"] == "SURVIVES_ALL_WINDOWS_EXPLORATORY"
    assert entry["action"] == "EXPLORATORY_REVIEW_ONLY"
    assert "NOT promotion-proposal material" in entry["action_reason"]
    assert set(entry["tiers_by_window"]) == {"3d", "4d"}
    assert all(t == seg.TIER_EXEC_PROMO
               for t in entry["tiers_by_window"].values())
    assert rep["thresholds_overridden"] is True
    text = seg.render_rolling_report(rep)
    assert "EXPLORATORY SURVIVORS (OVERRIDDEN THRESHOLDS" in text
    assert "[THRESHOLDS EXPLICITLY OVERRIDDEN]" in text
    assert seg.NO_BEHAVIOR_LINE in text


def test_rolling_survivor_under_unrelaxed_profiles_is_proposal_ready(tmp_path):
    """The real gate: enough genuine evidence under the UNRELAXED 7d
    profile (30 settled / 3 days / 20 fixtures) -> PROMOTION PROPOSAL
    READY with no override flag anywhere."""
    days = [f"2026-09-0{d}" for d in range(1, 8)]      # 7 days x 6 = 42
    settled = _exec_ledger(tmp_path, days=days, per_day=6)
    rep = seg.build_rolling_report(days[-1], windows=(7,), root=tmp_path,
                                   settled=settled)
    ready = rep["promotion_proposal_ready"]
    entry = next(e for e in ready if e["segment_key"] == "market=1x2")
    assert entry["survival"] == "SURVIVES_ALL_WINDOWS"
    assert entry["action"] == "PROMOTION_PROPOSAL_REVIEW"
    assert entry["windows"]["7d"]["settled_records"] == 42
    assert rep["thresholds_overridden"] is False
    assert rep["exploratory_survivors"] == []
    text = seg.render_rolling_report(rep)
    assert "PROMOTION PROPOSAL READY" in text
    assert "[THRESHOLDS EXPLICITLY OVERRIDDEN]" not in text


def test_rolling_short_window_only_edge_is_not_survivor(tmp_path):
    settled = _exec_ledger(tmp_path)          # data on D1..D3
    overrides = dict(min_settled=4, min_days=3, min_fixtures=3)
    # 2d window sees only D2..D3 (2 days < min_days=3) -> fails there
    rep = seg.build_rolling_report(D3, windows=(2, 3), root=tmp_path,
                                   settled=settled,
                                   threshold_overrides=overrides,
                                   watch_min_settled=2)
    assert not any(e["segment_key"] == "market=1x2"
                   for e in rep["promotion_proposal_ready"])
    missed = next(e for e in rep["exec_promo_not_survived"]
                  if e["segment_key"] == "market=1x2")
    assert missed["survival"] == "NOT_SURVIVED_ALL_WINDOWS"
    assert missed["tiers_by_window"]["3d"] == seg.TIER_EXEC_PROMO
    assert missed["tiers_by_window"]["2d"] != seg.TIER_EXEC_PROMO
    text = seg.render_rolling_report(rep)
    assert "NOT SURVIVED" in text


def test_rolling_default_profiles_make_tiny_samples_unpromotable(tmp_path):
    """Without explicit overrides the real profiles apply: 12 settled over
    3 days can NEVER be proposal-ready (7d bar is 30 settled/20 fixtures).
    Relaxation must be explicit — never a silent default."""
    settled = _exec_ledger(tmp_path)
    rep = seg.build_rolling_report(D3, windows=(7,), root=tmp_path,
                                   settled=settled)
    assert rep["promotion_proposal_ready"] == []
    assert rep["thresholds_overridden"] is False
    assert rep["window_profiles"]["7d"]["min_settled"] == 30
