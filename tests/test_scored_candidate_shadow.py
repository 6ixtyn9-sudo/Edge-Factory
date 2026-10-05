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


# =================== fixture-level scored-universe capture ===================
# The original blind spot: `scored=29 picks=4 ticketed=2` with only the 4-6
# operational candidates graded. These tests pin that the ledger preserves
# the FULL fixture-level scored universe and reconciles it exactly.

def _teamcode(i):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return letters[i // 26] + letters[i % 26]


def _fixture_entry(i, *, kind="ml_scored_fixture"):
    # Letter-coded names: distinct under norm_team/ledger_team_key (digits
    # and club-noise words would collapse, which is exactly what the legacy
    # width-9 key does to lookalike names).
    e = {"kind": kind, "home": f"{_teamcode(i)}holm", "away": f"{_teamcode(i)}berg",
         "league": "Portugal,Primeira Liga", "kickoff": f"{DAY}T18:30:00+00:00",
         "sport": "soccer", "trading_date": DAY}
    if kind == "ml_scored_fixture":
        e.update({"ml_probability": 0.6, "ml_majority_pick": "home",
                  "sources_used": ["forebet", "zulubet"]})
    return e


def _cand_for_fixture(entry, **kw):
    return _row(home=entry["home"], away=entry["away"], **kw)


def test_scored_29_picks_4_ticketed_2_receipt_preserves_all_29(tmp_path):
    """THE acceptance gate: pipeline scored=29, 4 promoted, 2 ticketed ->
    the ledger/report preserves all 29 scored records and reports 25
    scored-but-not-promoted. The 25 dropped fixtures are visible, counted,
    and explicitly marked as carrying no decision-time price."""
    fixtures = [_fixture_entry(i) for i in range(29)]
    cands = [_cand_for_fixture(fixtures[i], odds=1.5 + i * 0.1)
             for i in range(4)]
    out = scs.record_picks_build(
        day=DAY, scored_rows=cands, slate_rows=cands,
        pipeline_scored_log=29, scored_fixtures=fixtures,
        ml_scored_day=29, n_up=35, price_supported_markets={"1x2"},
        root=tmp_path)
    assert out["fixtures"] == 29
    selected = {_key_of(c): {"acca_id": "A1", "acca_leg_index": j,
                             "stake_pct_of_capital": 8.0,
                             "price_used_if_selected": c["odds"]}
                for j, c in enumerate(cands[:2])}
    _record_statuses(tmp_path, cands, selected=selected, final="frozen")

    report = scs.build_report(DAY, root=tmp_path, settled={})
    rec = report["reconciliation"]
    ff = report["fixture_funnel"]
    assert rec["pipeline_scored_log"] == 29
    assert rec["shadow_scored_fixture_records"] == 29
    assert rec["missing_count"] == 0
    assert rec["reconciliation_ok"] is True
    assert ff["fixtures_materialized"] == 4
    assert ff["fixtures_promoted"] == 4
    assert ff["fixtures_ticketed"] == 2
    assert ff["fixtures_not_promoted"] == 25
    assert ff["fixtures_dropped_without_price_evidence"] == 25
    assert report["counts"]["promoted_picks"] == 4
    assert report["counts"]["ticketed_legs"] == 2
    assert report["counts"]["promoted_not_ticketed"] == 2
    # all 29 fixture records are durable rows in the report payload
    assert len(report["fixtures"]) == 29
    dropped = [f for f in report["fixtures"] if not f["candidate_materialized"]]
    assert len(dropped) == 25
    assert all(f["not_materialized_reason"] == "no_candidate_emitted"
               for f in dropped)
    text = scs.render_report(report)
    assert "pipeline_scored:                       29" in text
    assert "scored but not promoted (fixtures):    25" in text
    assert "reconciliation=ok" in text


def test_fixture_universe_mirrors_pipeline_ml_or_nup_expression(tmp_path):
    """`scored=` is ml_scored_day OR n_up — the persisted universe follows
    the same expression: ML entries when any exist, else upcoming entries."""
    ml = [_fixture_entry(i) for i in range(3)]
    up = [_fixture_entry(100 + i, kind="upcoming_fixture") for i in range(7)]
    out = scs.record_picks_build(day=DAY, scored_rows=[], slate_rows=[],
                                 pipeline_scored_log=3, scored_fixtures=ml + up,
                                 ml_scored_day=3, n_up=7, root=tmp_path)
    assert out["fixtures"] == 3                   # ML universe wins
    events = scs.read_ledger(DAY, tmp_path)
    kinds = {e["kind"] for e in events if e["event_type"] == "scored_fixture"}
    assert kinds == {"ml_scored_fixture"}

    # fallback day: no ML entries -> the n_up universe is persisted
    out2 = scs.record_picks_build(day="2026-09-07", scored_rows=[],
                                  slate_rows=[], pipeline_scored_log=7,
                                  scored_fixtures=[
                                      dict(e, trading_date="2026-09-07")
                                      for e in up],
                                  ml_scored_day=0, n_up=7, root=tmp_path)
    assert out2["fixtures"] == 7


def test_reconciliation_mismatch_is_flagged_not_hidden(tmp_path):
    fixtures = [_fixture_entry(i) for i in range(28)]   # one short of 29
    scs.record_picks_build(day=DAY, scored_rows=[], slate_rows=[],
                           pipeline_scored_log=29, scored_fixtures=fixtures,
                           ml_scored_day=29, n_up=30, root=tmp_path)
    report = scs.build_report(DAY, root=tmp_path, settled={})
    rec = report["reconciliation"]
    assert rec["missing_count"] == 1
    assert rec["reconciliation_ok"] is False
    assert "RECONCILIATION MISMATCH" in rec["note"]
    assert "reconciliation=MISMATCH" in scs.render_report(report)


def test_ticket_layer_only_ledger_declares_reconciliation_unavailable(tmp_path):
    """A ledger without scored_fixture events must say so loudly instead of
    relabeling the candidate layer as the full scored universe."""
    _record_statuses(tmp_path, [_row()])
    # fake a picks summary carrying the pipeline count but no fixture events
    scs._append_events(DAY, [{
        "schema_version": scs.SCHEMA_VERSION, "event_type": "run_summary",
        "run_id": scs.new_run_id("picks_build"), "stage": "picks_build",
        "trading_date": DAY, "build_day": DAY,
        "pipeline_scored_log": 29, "shadow_scored": 1,
        "scored_definition": "x"}], tmp_path)
    report = scs.build_report(DAY, root=tmp_path, settled={})
    rec = report["reconciliation"]
    assert rec["reconciliation_ok"] is None
    assert "RECONCILIATION UNAVAILABLE" in rec["note"]
    assert "NOT the full scored universe" in rec["note"]


def test_dropped_fixture_without_candidate_never_enters_any_roi(tmp_path):
    """A scored-but-never-materialized fixture has no selection and no
    decision-time price: it appears in the funnel but in no ROI denominator,
    and its result is never graded (no selection exists to grade)."""
    fixtures = [_fixture_entry(0), _fixture_entry(1)]
    cand = _cand_for_fixture(fixtures[0], odds=2.0)
    scs.record_picks_build(day=DAY, scored_rows=[cand], slate_rows=[cand],
                           pipeline_scored_log=2, scored_fixtures=fixtures,
                           ml_scored_day=2, n_up=2, root=tmp_path)
    settled = _settled((DAY, fixtures[1]["home"], fixtures[1]["away"], "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    assert report["fixture_funnel"]["fixtures_dropped_without_price_evidence"] == 1
    assert report["roi"]["all_scored"]["candidates"] == 1   # cand only
    assert report["counts"]["settled_win"] == 0             # fixture not graded


# ================= captured-price shadow grading (full universe) =============
# "Bread on the table": grade every scored item flat-stake at the odds the
# scorer itself saw, in an AUDIT-ONLY ROI class strictly separated from
# execution-safe ROI. Stale/unregistered/donor prices allowed and labelled;
# fair/model prices live only in their own bucket; post-kickoff/unknown-
# timestamp prices excluded; pending is never a loss; matching stays exact.

def _priced(i, **over):
    e = _fixture_entry(i)
    e.update({"market": "1x2", "selection": "home",
              "selection_team": e["home"],
              "shadow_price": 2.0, "shadow_price_source": "zulubet",
              "shadow_price_captured_at_utc": f"{DAY}T06:00:00+00:00",
              "shadow_price_as_of_basis": "fetched_this_run"})
    e.update(over)
    return e


def _build_priced_day(tmp_path, fixtures, *, n_promote=0, n_ticket=0,
                      pipeline=None):
    cands = [_cand_for_fixture(fixtures[i], odds=1.9)
             for i in range(n_promote)]
    scs.record_picks_build(
        day=DAY, scored_rows=cands, slate_rows=cands,
        pipeline_scored_log=pipeline if pipeline is not None else len(fixtures),
        scored_fixtures=fixtures, ml_scored_day=len(fixtures), n_up=0,
        price_supported_markets={"1x2"}, root=tmp_path)
    if cands:
        selected = {_key_of(c): {"acca_id": "A1", "acca_leg_index": j,
                                 "stake_pct_of_capital": 8.0,
                                 "price_used_if_selected": 1.9}
                    for j, c in enumerate(cands[:n_ticket])}
        _record_statuses(tmp_path, cands, selected=selected, final="frozen")
    return cands


def test_bread_on_table_29_4_2_captured_price_roi_answers_the_question(tmp_path):
    """pipeline scored=29, 4 promoted, 2 ticketed: the 25 non-promoted are
    GRADED at the captured odds, not hidden behind 'no_candidate_emitted'."""
    fixtures = [_priced(i) for i in range(29)]
    _build_priced_day(tmp_path, fixtures, n_promote=4, n_ticket=2)
    # 25 non-promoted fixtures: first 10 win at 2.0, next 10 lose, 5 pending
    settled = {}
    for i, f in enumerate(fixtures[4:24]):
        settled.update(_settled((DAY, f["home"], f["away"],
                                 "home" if i < 10 else "away")))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)

    sg = report["shadow_gradeability"]
    assert sg["records"] == 29
    assert sg["with_selection_intent"] == 29
    assert sg["with_captured_price"] == 29
    assert sg["shadow_gradeable"] == 29
    assert sg["fresh_price"] == 29 and sg["stale_price"] == 0

    cp = report["captured_price_shadow_roi"]
    snp = cp["scored_not_promoted"]
    assert snp["candidates"] == 25
    assert snp["settled"] == 20 and snp["wins"] == 10 and snp["losses"] == 10
    assert snp["pending"] == 5                    # pending excluded, not lost
    assert snp["flat_profit"] == 0.0              # 10*(2.0-1) + 10*(-1)
    assert snp["flat_roi"] == 0.0
    assert cp["all_scored_gradeable"]["candidates"] == 29
    assert cp["ticketed"]["candidates"] == 2
    assert cp["promoted_not_ticketed"]["candidates"] == 2
    # shadow prices never leak into the strict execution-safe class: the
    # exec-safe count equals the CANDIDATE-level named-book count (the 4
    # materialized rows), not the 29 shadow-priced fixtures
    assert report["counts"]["execution_safe_scored"] == 4
    assert report["shadow_gradeability"]["execution_safe_gradeable"] == 4
    # exec-safe rejected = the 2 promoted-but-not-ticketed candidates only;
    # none of the 25 shadow-priced dropped fixtures can enter this line
    assert report["roi"]["execution_safe_rejected"]["candidates"] == 2
    text = scs.render_report(report)
    assert "AUDIT-ONLY — NOT STAKEABLE" in text
    assert "scored but not promoted" in text


def test_stale_captured_price_grades_in_shadow_roi_only_and_is_labelled(tmp_path):
    stale = _priced(0, shadow_price_as_of_basis="",
                    shadow_price_as_of_utc=f"{DAY}T02:00:00+00:00")  # 4h old
    fresh = _priced(1)
    _build_priced_day(tmp_path, [stale, fresh])
    settled = _settled((DAY, stale["home"], stale["away"], "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    fx = {f["home_team"]: f for f in report["fixtures"]}
    s = fx[stale["home"]]
    assert s["shadow_price_stale"] is True
    assert s["shadow_price_age_seconds"] == 4 * 3600
    assert s["shadow_price_gradeable"] is True
    assert s["shadow_price_execution_safe"] is False
    cp = report["captured_price_shadow_roi"]
    assert cp["stale_price"]["candidates"] == 1
    assert cp["stale_price"]["wins"] == 1
    assert cp["stale_price"]["flat_profit"] == 1.0          # 2.0 - 1
    assert cp["fresh_price"]["candidates"] == 1
    # stale price NEVER becomes execution-safe anywhere
    assert report["counts"]["execution_safe_scored"] == 0
    assert report["shadow_gradeability"]["execution_safe_gradeable"] == 0


def test_no_selection_intent_counted_not_silently_ignored(tmp_path):
    no_intent = _fixture_entry(0, kind="ml_scored_fixture")  # no selection
    with_intent = _priced(1)
    _build_priced_day(tmp_path, [no_intent, with_intent])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    sg = report["shadow_gradeability"]
    assert sg["without_selection_intent"] == 1
    assert sg["shadow_gradeable"] == 1
    fx = {f["home_team"]: f for f in report["fixtures"]}
    assert (fx[no_intent["home"]]["shadow_price_gradeable_reason"]
            == "no_selection_intent_available")
    assert report["captured_price_shadow_roi"]["all_scored_gradeable"][
        "candidates"] == 1


def test_intent_without_captured_price_counted_as_ungradeable_no_price(tmp_path):
    no_price = _priced(0, shadow_price=None, shadow_price_source=None)
    _build_priced_day(tmp_path, [no_price, _priced(1)])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    sg = report["shadow_gradeability"]
    assert sg["intent_but_no_price"] == 1
    assert sg["without_captured_price"] == 1
    fx = {f["home_team"]: f for f in report["fixtures"]}
    assert (fx[no_price["home"]]["shadow_price_gradeable_reason"]
            == "no_captured_price")
    assert report["captured_price_shadow_roi"]["all_scored_gradeable"][
        "candidates"] == 1


def test_post_kickoff_captured_price_is_excluded(tmp_path):
    post = _priced(0, shadow_price_captured_at_utc=f"{DAY}T19:00:00+00:00")
    # kickoff is 18:30Z aware -> capture 19:00Z is provably post-kickoff
    _build_priced_day(tmp_path, [post, _priced(1)])
    settled = _settled((DAY, post["home"], post["away"], "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    sg = report["shadow_gradeability"]
    assert sg["post_kickoff_price_excluded"] == 1
    fx = {f["home_team"]: f for f in report["fixtures"]}
    p = fx[post["home"]]
    assert p["shadow_price_gradeable"] is False
    assert p["shadow_price_gradeable_reason"] == "post_kickoff_price"
    assert p["shadow_price_post_kickoff"] is True
    # a would-be winner at a post-kickoff price contributes NOTHING
    assert report["captured_price_shadow_roi"]["all_scored_gradeable"][
        "candidates"] == 1


def test_unknown_price_timestamp_is_excluded(tmp_path):
    unk = _priced(0, shadow_price_captured_at_utc=None,
                  shadow_price_as_of_basis="")
    _build_priced_day(tmp_path, [unk, _priced(1)])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    assert report["shadow_gradeability"]["timestamp_unknown_excluded"] == 1
    fx = {f["home_team"]: f for f in report["fixtures"]}
    assert (fx[unk["home"]]["shadow_price_gradeable_reason"]
            == "price_timestamp_unknown")


def test_fair_model_price_lives_only_in_its_own_labelled_bucket(tmp_path):
    fair = _priced(0, shadow_price_kind="fair_model",
                   shadow_price_source="betbetter_fair")
    real = _priced(1)
    _build_priced_day(tmp_path, [fair, real])
    settled = _settled((DAY, fair["home"], fair["away"], "home"),
                       (DAY, real["home"], real["away"], "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    cp = report["captured_price_shadow_roi"]
    assert cp["fair_model_only_audit"]["candidates"] == 1
    assert cp["fair_model_only_audit"]["wins"] == 1
    assert cp["all_scored_gradeable"]["candidates"] == 1   # fair excluded
    assert "fair_model" in cp["by_price_kind"]
    assert report["counts"]["execution_safe_scored"] == 0  # never exec-safe


def test_unregistered_source_price_shadow_only_and_labelled(tmp_path):
    f0 = _priced(0)   # zulubet -> unregistered_source
    _build_priced_day(tmp_path, [f0])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    fx = report["fixtures"][0]
    assert fx["shadow_price_kind"] == "unregistered_source"
    assert fx["shadow_price_registered_source"] is False
    assert fx["shadow_price_execution_safe"] is False
    assert "zulubet" in report["captured_price_shadow_roi"]["by_source"]
    assert report["counts"]["execution_safe_scored"] == 0


def test_donor_average_source_classified_as_donor_average(tmp_path):
    f0 = _priced(0, shadow_price_source="bzzoiro")
    _build_priced_day(tmp_path, [f0])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    assert report["fixtures"][0]["shadow_price_kind"] == "donor_average"
    assert "donor_average" in report["captured_price_shadow_roi"][
        "by_price_kind"]


def test_pending_fixture_is_never_a_loss_in_shadow_roi(tmp_path):
    _build_priced_day(tmp_path, [_priced(0)])
    report = scs.build_report(DAY, root=tmp_path, settled={})
    agg = report["captured_price_shadow_roi"]["all_scored_gradeable"]
    assert agg["pending"] == 1
    assert agg["settled"] == 0 and agg["losses"] == 0
    assert agg["flat_profit"] == 0.0 and agg["flat_roi"] is None


def test_near_match_fixture_does_not_settle_exact_only(tmp_path):
    f0 = _priced(0)
    _build_priced_day(tmp_path, [f0])
    settled = _settled((DAY, f0["home"] + "x", f0["away"], "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    fx = report["fixtures"][0]
    assert fx["settlement_status"] == "pending"
    assert fx["settlement_detail"] == "no_exact_result_match"


def test_shadow_roi_grouping_dimensions_all_present(tmp_path):
    fixtures = [_priced(0), _priced(1, selection="away",
                                    shadow_price_source="bzzoiro"),
                _priced(2, shadow_price_as_of_basis="",
                        shadow_price_as_of_utc=f"{DAY}T00:00:00+00:00")]
    _build_priced_day(tmp_path, fixtures, n_promote=1)
    report = scs.build_report(DAY, root=tmp_path, settled={})
    cp = report["captured_price_shadow_roi"]
    for key in ("by_price_kind", "by_source", "by_bookmaker", "by_bucket",
                "by_rule_model", "by_league", "by_promotion", "by_reason",
                "by_stale_fresh", "by_kickoff_proof"):
        assert key in cp, key
    assert cp["by_stale_fresh"]["stale"]["candidates"] == 1
    assert cp["by_stale_fresh"]["fresh"]["candidates"] == 2
    assert set(cp["by_source"]) == {"zulubet", "bzzoiro"}
    assert cp["by_promotion"]["not_promoted"]["candidates"] == 2
    assert "no_candidate_emitted" in cp["by_reason"]
    assert "instants_proven" in cp["by_kickoff_proof"]


def test_record_picks_build_fail_soft_with_priced_fixtures(tmp_path, monkeypatch):
    def _boom(*a, **k):
        raise OSError("disk went away")
    monkeypatch.setattr(scs, "_append_events", _boom)
    out = scs.record_picks_build(
        day=DAY, scored_rows=[], slate_rows=[],
        pipeline_scored_log=1, scored_fixtures=[_priced(0)],
        ml_scored_day=1, n_up=1, root=tmp_path)
    assert out is None    # swallowed, never raises into the build


def test_fixture_settlement_events_are_layer_labelled(tmp_path):
    f0 = _priced(0)
    _build_priced_day(tmp_path, [f0])
    settled = _settled((DAY, f0["home"], f0["away"], "home"))
    report = scs.build_report(DAY, root=tmp_path, settled=settled)
    events = scs.settlement_events(report)
    fixture_evts = [e for e in events if e.get("layer") == "scored_fixture"]
    assert len(fixture_evts) == 1
    assert fixture_evts[0]["settlement_status"] == "win"
    assert fixture_evts[0]["flat_stake_return"] == 1.0
    assert fixture_evts[0]["shadow_price_kind"] == "unregistered_source"
