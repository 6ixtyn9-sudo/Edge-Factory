"""Scored-candidate shadow grading ledger — module contract tests.

Pins the audit-only doctrine: every scored candidate is persisted, price
evidence is classified honestly (fair/model/unregistered/post-kickoff prices
never become execution-safe), settlement is read-only exact-match-only
(pending is never a loss), draft reruns never inflate the default report,
multiple rejection reasons are preserved, and the report groups by every
required dimension.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory import scored_candidate_shadow as scs  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402

DAY = "2026-09-06"


def _row(home="Sporting CP", away="Portimonense", *, odds=1.50,
         odds_source="bzzoiro_odds", market="1x2", pick="home",
         rule="ml-consensus", bucket="CERTIFIED_CLEAN",
         kickoff_utc="2026-09-06T18:30:00+00:00",
         captured_at="2026-09-06T06:00:00+00:00", **extra):
    row = {
        "date": DAY, "home": home, "away": away,
        "league": "Portugal,Primeira Liga", "market": market, "pick": pick,
        "rule": rule, "bucket": bucket, "avg_p": 70.0, "w_score": 1.0,
        "odds": odds, "odds_source": odds_source, "bookmaker": "BookyBook",
        "price_evidence": "NAMED_BOOKMAKER_PRICE", "price_push_eligible": True,
        "quarantine": "none", "kickoff_utc": kickoff_utc,
        "as_of": captured_at,
    }
    row.update(extra)
    return row


def _settled(*entries):
    return {(d, norm_team(h), norm_team(a)): o for d, h, a, o in entries}


def _key_of(row):
    return (f"{row.get('home')} vs {row.get('away')}",
            str(row.get("pick") or "").upper())


def _record_statuses(tmp_path, rows, *, selected=None, staged=None,
                     default=("stake_ladder_not_selected", "not selected"),
                     final="frozen", run_id=None, gate=None):
    run_id = run_id or scs.new_run_id("ticket_build")
    scs.record_ticket_build(day=DAY, slate_rows=rows, root=tmp_path,
                            run_id=run_id)
    status_rows = scs.build_ticket_status_rows(
        rows, day=DAY, selected=selected or {}, staged=staged or {},
        default_rule=default, gate=gate, key_of=_key_of,
        final_ticket_status=final)
    scs.record_ticket_outcome(day=DAY, run_id=run_id, status_rows=status_rows,
                              final_ticket_status=final, root=tmp_path)
    return run_id


# ------------------------------------------------- 1. everything persisted --
def test_every_scored_candidate_is_persisted_including_in_build_drops(tmp_path):
    """3 scored candidates — 1 promoted to the slate, 1 dropped by bucket
    assignment, 1 dropped by the operational collapse — all 3 get durable
    scored records plus a status each."""
    kept = _row()
    collapsed = _row(rule="other-rule")           # same fixture, other rule
    bucket_dropped = _row(home="Benfica", away="Gil Vicente")
    out = scs.record_picks_build(
        day=DAY, scored_rows=[kept, collapsed, bucket_dropped],
        slate_rows=[kept], pre_collapse_rows=[kept, collapsed],
        pipeline_scored_log=29, price_supported_markets={"1x2"},
        root=tmp_path)
    assert out is not None and out["scored"] == 3
    events = scs.read_ledger(DAY, tmp_path)
    scored = [e for e in events if e["event_type"] == "scored_candidate"]
    statuses = [e for e in events if e["event_type"] == "candidate_status"]
    assert len(scored) == 3
    assert len(statuses) == 3
    by_cid = {s["candidate_id"]: s for s in statuses}
    assert by_cid[scs.candidate_id(kept, DAY)]["selected_as_pick"] is True
    coll = by_cid[scs.candidate_id(collapsed, DAY)]
    assert coll["selected_as_pick"] is False
    assert coll["rejection_reasons"][0]["code"] == "duplicate_fixture"
    assert coll["drop_stage"] == "operational_collapse"
    drop = by_cid[scs.candidate_id(bucket_dropped, DAY)]
    assert drop["rejection_reasons"][0]["code"] == "odds_floor"
    assert drop["drop_stage"] == "bucket_assignment"
    # run summary persists BOTH scored definitions for reconciliation
    summary = next(e for e in events if e["event_type"] == "run_summary")
    assert summary["pipeline_scored_log"] == 29
    assert summary["shadow_scored"] == 3
    assert "candidate" in summary["scored_definition"]


def test_disabled_flag_writes_nothing_and_returns_none(tmp_path, monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_SCORED_SHADOW", "0")
    out = scs.record_picks_build(day=DAY, scored_rows=[_row()],
                                 slate_rows=[_row()], root=tmp_path)
    assert out is None
    assert not scs.ledger_path(DAY, tmp_path).exists()


def test_write_failure_is_swallowed_not_raised(tmp_path, monkeypatch):
    """An audit write failure must never raise into the betting pipeline."""
    def boom(*a, **k):
        raise OSError("disk gone")
    monkeypatch.setattr(scs, "_append_events", boom)
    out = scs.record_picks_build(day=DAY, scored_rows=[_row()],
                                 slate_rows=[_row()], root=tmp_path)
    assert out is None  # reported on stderr, swallowed


# ----------------------------------------- 2/3. execution-safe rejected ROI --
def test_rejected_execution_safe_candidate_settles_into_rejected_roi(tmp_path):
    row = _row(odds=2.10)
    _record_statuses(tmp_path, [row], final="frozen")
    settled = _settled((DAY, "Sporting CP", "Portimonense", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    agg = report["roi"]["execution_safe_rejected"]
    assert agg["candidates"] == 1
    assert agg["wins"] == 1
    assert agg["flat_profit"] == pytest.approx(1.10)
    assert agg["flat_roi"] == pytest.approx(1.10)
    assert report["counts"]["execution_safe_rejected"] == 1
    # loses map to -1
    settled_loss = _settled((DAY, "Sporting CP", "Portimonense", "away"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled_loss)
    assert report["roi"]["execution_safe_rejected"]["flat_profit"] == pytest.approx(-1.0)


# -------------------------------------------------- 4. pending is not loss --
def test_unresolved_candidate_stays_pending_and_out_of_roi_denominator(tmp_path):
    _record_statuses(tmp_path, [_row()])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    agg = report["roi"]["all_scored_rejected"]
    assert report["counts"]["pending"] == 1
    assert agg["pending"] == 1
    assert agg["settled"] == 0
    assert agg["flat_roi"] is None
    assert agg["flat_profit"] == 0.0


# ------------------------------------- 5. no valid price = non-executable --
@pytest.mark.parametrize("mutation, reason", [
    ({"odds_source": "betbetter"}, "price_source_not_execution_eligible"),
    ({"odds_source": "boggio"}, "no_named_book_price"),
    ({"odds_source": "mystery_feed"}, "price_source_unregistered"),
    ({"odds": None}, "no_captured_price"),
    ({"price_push_eligible": False}, "price_push_ineligible"),
    ({"quarantine": "alias_fuzzy"}, "price_quarantined:alias_fuzzy"),
    ({"kickoff_utc": None}, "pre_kickoff_unproven:no_parseable_kickoff_utc"),
    ({"as_of": None}, "pre_kickoff_unproven:no_parseable_capture_instant"),
])
def test_non_execution_safe_prices_are_recorded_but_excluded(tmp_path, mutation, reason):
    row = _row(**mutation)
    safety = scs.execution_safety(row)
    assert safety["execution_safe_named_book_eligible"] is False
    assert safety["execution_safe_reason"] == reason
    _record_statuses(tmp_path, [row])
    settled = _settled((DAY, "Sporting CP", "Portimonense", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    assert report["counts"]["total_scored"] == 1          # recorded
    assert report["counts"]["execution_safe_scored"] == 0  # excluded
    assert report["roi"]["execution_safe_rejected"]["candidates"] == 0
    assert report["counts"]["no_execution_safe_price"] == 1


def test_fair_model_price_never_counts_as_bookmaker_execution():
    """Bet Better stays fair_stakeable=off; Boggio stays an average donor."""
    assert scs.execution_safety(_row(odds_source="betbetter"))[
        "execution_safe_named_book_eligible"] is False
    assert scs.execution_safety(_row(odds_source="boggio"))[
        "execution_safe_named_book_eligible"] is False


# --------------------------------------------------- 6. no post-kickoff odds --
def test_post_kickoff_price_evidence_is_never_execution_safe(tmp_path):
    row = _row(captured_at="2026-09-06T19:00:00+00:00",   # after 18:30 KO
               kickoff_utc="2026-09-06T18:30:00+00:00")
    safety = scs.execution_safety(row)
    assert safety["execution_safe_named_book_eligible"] is False
    assert safety["execution_safe_reason"] == "post_kickoff_price"
    assert safety["price_valid_pre_kickoff"] is False
    _record_statuses(tmp_path, [row])
    settled = _settled((DAY, "Sporting CP", "Portimonense", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    assert report["counts"]["execution_safe_scored"] == 0


# ------------------------------------------------------ 7. exact match only --
def test_similar_but_non_identical_fixture_does_not_settle(tmp_path):
    """The live grader resolves 'Hearts' <-> 'Heart of Midlothian' via the
    curated alias index and a fuzzy fallback; the shadow settler must use
    EXACT normalized keys only — similar/aliased spellings stay pending."""
    _record_statuses(tmp_path, [_row(home="Hearts", away="Hibernian")])
    settled = _settled((DAY, "Heart of Midlothian", "Hibernian", "home"))
    assert norm_team("Hearts") != norm_team("Heart of Midlothian")
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    cand = report["candidates"][0]
    assert cand["settlement_status"] == "pending"
    assert report["counts"]["settled_win"] == 0
    assert report["counts"]["settled_loss"] == 0
    # a reschedule window is also out of scope: the exact fixture on an
    # adjacent date must not settle a candidate filed for DAY
    settled_adjacent = _settled(("2026-09-07", "Hearts", "Hibernian", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled_adjacent)
    assert report["candidates"][0]["settlement_status"] == "pending"


def test_unsupported_market_or_side_is_unmatched_not_loss(tmp_path):
    rows = [_row(market="ou_2.5", pick="over"),
            _row(home="Braga", away="Rio Ave", pick="")]
    _record_statuses(tmp_path, rows)
    settled = _settled((DAY, "Sporting CP", "Portimonense", "home"),
                       (DAY, "Braga", "Rio Ave", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    assert report["counts"]["unmatched"] == 2
    assert report["counts"]["settled_loss"] == 0
    agg = report["roi"]["all_scored"]
    assert agg["settled"] == 0 and agg["unmatched"] == 2


def test_terminal_non_score_outcome_is_void_zero(tmp_path):
    _record_statuses(tmp_path, [_row(odds=2.0)])
    settled = _settled((DAY, "Sporting CP", "Portimonense", "POSTPONED"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    agg = report["roi"]["all_scored"]
    assert agg["voids"] == 1
    assert agg["flat_profit"] == 0.0


# --------------------------------------------------- 8. draft rerun dedupe --
def test_multiple_draft_runs_do_not_inflate_default_daily_roi(tmp_path):
    row = _row(odds=2.0)
    _record_statuses(tmp_path, [row], final="draft")
    _record_statuses(tmp_path, [row], final="draft")
    _record_statuses(tmp_path, [row], final="draft")
    settled = _settled((DAY, "Sporting CP", "Portimonense", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    assert report["counts"]["total_scored"] == 1          # deduped
    assert report["roi"]["all_scored"]["candidates"] == 1
    assert report["roi"]["all_scored"]["flat_profit"] == pytest.approx(1.0)
    assert report["snapshot_used"] == "draft"
    assert len(report["ticket_runs_seen"]) == 3


def test_frozen_snapshot_outranks_later_draft(tmp_path):
    row = _row(odds=2.0)
    selected = {_key_of(row): {"acca_id": "A1", "acca_leg_index": 0,
                               "stake_pct_of_capital": 8.0,
                               "price_used_if_selected": 2.0}}
    frozen_run = _record_statuses(tmp_path, [row], selected=selected,
                                  final="frozen")
    _record_statuses(tmp_path, [row], final="draft")      # later draft rerun
    report = scs.build_report(DAY, root=tmp_path, settled={})
    assert report["snapshot_used"] == "frozen"
    assert report["effective_ticket_run"] == frozen_run
    assert report["counts"]["ticketed_legs"] == 1


# ------------------------------------------- 9. multiple rejection reasons --
def test_multiple_rejection_reasons_are_preserved_and_reported(tmp_path):
    row = _row(odds=1.05)  # fails the live min-odds gate
    staged = {_key_of(row): ("kickoff_guard", "kickoff already passed")}

    def gate(r):
        return ("min_odds_floor", "decimal_odds=1.05 < floor=1.20")

    run_id = scs.new_run_id("ticket_build")
    scs.record_ticket_build(day=DAY, slate_rows=[row], root=tmp_path,
                            run_id=run_id)
    status_rows = scs.build_ticket_status_rows(
        [row], day=DAY, selected={}, staged=staged,
        default_rule=("stake_ladder_not_selected", "x"), gate=gate,
        key_of=_key_of, final_ticket_status="draft")
    assert [r["code"] for r in status_rows[0]["rejection_reasons"]] == [
        "min_odds_floor", "kickoff_guard"]
    scs.record_ticket_outcome(day=DAY, run_id=run_id, status_rows=status_rows,
                              final_ticket_status="draft", root=tmp_path)
    report = scs.build_report(DAY, root=tmp_path, settled={})
    by_reason = report["roi"]["by_rejection_reason"]
    assert "min_odds_floor" in by_reason
    assert "kickoff_guard" in by_reason


def test_unknown_rejection_reason_is_explicit_and_counted(tmp_path):
    # Scored event only — no status event ever recorded for the candidate.
    scs.record_ticket_build(day=DAY, slate_rows=[_row()], root=tmp_path)
    report = scs.build_report(DAY, root=tmp_path, settled={})
    assert report["counts"]["unknown_rejection_reason"] == 1
    assert "rejection_reason_unknown" in report["roi"]["by_rejection_reason"]


# ------------------------------------------------------ 10. report grouping --
def test_report_groups_by_every_required_dimension(tmp_path):
    ticketed = _row(odds=2.0)
    rejected = _row(home="Benfica", away="Gil Vicente", odds=1.8,
                    bucket="CAUTION", rule="2way-unanimous",
                    odds_source="theoddsapi")
    unsafe = _row(home="Porto", away="Estoril Praia",
                  odds_source="mystery_feed")
    selected = {_key_of(ticketed): {"acca_id": "A1", "acca_leg_index": 0,
                                    "stake_pct_of_capital": 8.0,
                                    "price_used_if_selected": 2.0}}
    _record_statuses(tmp_path, [ticketed, rejected, unsafe],
                     selected=selected, final="frozen")
    settled = _settled((DAY, "Sporting CP", "Portimonense", "home"),
                       (DAY, "Benfica", "Gil Vicente", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    roi = report["roi"]
    assert roi["selected_vs_rejected"]["selected"]["candidates"] == 1
    assert roi["selected_vs_rejected"]["rejected"]["candidates"] == 2
    assert set(roi["by_bucket"]) == {"CERTIFIED_CLEAN", "CAUTION"}
    assert "ml-consensus" in roi["by_rule"] and "2way-unanimous" in roi["by_rule"]
    assert "Portugal,Primeira Liga" in roi["by_league"]
    assert "1x2" in roi["by_market"]
    assert set(roi["by_price_source"]) == {"bzzoiro_odds", "theoddsapi",
                                           "mystery_feed"}
    assert "BookyBook" in roi["by_bookmaker"]
    assert roi["by_execution_safety"]["execution_safe"]["candidates"] == 2
    assert roi["by_execution_safety"]["not_execution_safe"]["candidates"] == 1
    assert "stake_ladder_not_selected" in roi["by_rejection_reason"]
    # the rendered report carries the headline sections
    text = scs.render_report(report)
    for needle in ("Total scored".lower(), "execution-safe rejected",
                   "BY REJECTION REASON", "RECONCILIATION"):
        assert needle.lower() in text.lower()


# --------------------------------------------------------- identity safety --
def test_candidate_id_separates_market_selection_rule_league_and_date():
    base = _row()
    assert scs.candidate_id(base, DAY) == scs.candidate_id(dict(base), DAY)
    assert scs.candidate_id(base, DAY) != scs.candidate_id(
        {**base, "market": "ou_2.5", "pick": "over"}, DAY)
    assert scs.candidate_id(base, DAY) != scs.candidate_id(
        {**base, "pick": "away"}, DAY)
    assert scs.candidate_id(base, DAY) != scs.candidate_id(
        {**base, "rule": "ml-meta"}, DAY)
    assert scs.candidate_id(base, DAY) != scs.candidate_id(
        {**base, "league": "Spain,Segunda"}, DAY)
    assert scs.candidate_id(base, DAY) != scs.candidate_id(base, "2026-09-07")


def test_settlement_events_are_append_only_derivation(tmp_path):
    _record_statuses(tmp_path, [_row(odds=2.0)])
    before = scs.ledger_path(DAY, tmp_path).read_text()
    settled = _settled((DAY, "Sporting CP", "Portimonense", "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    events = scs.settlement_events(report)
    assert events[0]["settlement_status"] == "win"
    assert events[0]["flat_stake_return"] == pytest.approx(1.0)
    assert events[0]["match_basis"] == "exact_normalized_fixture"
    # building the report mutated nothing
    assert scs.ledger_path(DAY, tmp_path).read_text() == before
