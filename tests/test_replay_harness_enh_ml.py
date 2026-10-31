"""The ENH replay must order legs with the LIVE ML selector, not a lookalike.

2026-10-26 audit. ``enh_day_growth`` ranked every enhancement leg on the
realized cohort rate and built its pool without ``ml_rank_probability``, so
``auto_tickets.select_accas``' ML branch — which engages only when some leg
carries a finite model score — was False on every replayed day. The harness
therefore reported "the lane's own code" while running the pre-ML ordering.

The fix reuses the shipped machinery instead of re-deriving anything:

* ``enhancement_ml_probability(pick, market)`` is the same pure function
  ``picks_today`` and ``auto_tickets.enhancement_legs`` call;
* the parent pick row comes from the archived slate, matched on the registry
  record's own contract id + fixture;
* a leg with no model (or a model that fails its own hash/date/cohort guards)
  gets ``None``, exactly as live, and ranks in the cohort group behind the
  scored legs;
* ``enh_day_plans`` is the single place a replay card is built, so the parity
  report cannot grade a card the P&L arm did not build.

The coverage is tiny by construction — the retained model exists only on the
2026-10-25 and 2026-10-26 slates — so these tests prove the WIRING, and the
``--enh-ml`` report states the sample honestly rather than claiming an A/B.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory import enh_registry  # noqa: E402

import replay_harness as h  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_cache(monkeypatch):
    # These are explicit ML-on and captured pre-floor recipe regressions.
    monkeypatch.setenv("EDGE_FACTORY_ENH_ML", "1")
    h._SLATE_CACHE.clear()
    yield
    h._SLATE_CACHE.clear()


def _record(match, market, price, *, contract="pfc_" + "a" * 24, cohort=0.7, hit=True):
    home, away = match.split(" vs ")
    return {"date": "2026-10-25", "match": match, "home": home, "away": away,
            "market": market, "price": price, "hit": hit, "cohort_rate": cohort,
            "price_context": {"contract_id": contract, "book": "pinnacle",
                              "source": "pinnapi_odds"}}


def _parent(match, market, contract="pfc_" + "a" * 24, *, score=0.5):
    """An archived pick row the live ML function can score."""
    home, away = match.split(" vs ")
    return {"home": home, "away": away, "contract_id": contract,
            "date": "2026-10-25", "pick": "over", "avg_p": 70.0,
            "statistical_profile": {"ml_model": {"score": score}}}


def test_no_archived_parent_scores_nothing(monkeypatch):
    """A record with no parent row is unscored — never a fabricated score."""
    monkeypatch.setattr(h, "_slate_rows", lambda root, day: [])
    rec = _record("A vs B", "home_over_15", 1.5)
    assert h.archived_parent(ROOT, "2026-10-25", rec) is None
    assert h.enh_ml_probability(ROOT, "2026-10-25", rec) is None


def test_the_replay_score_delegates_to_the_shipped_function(monkeypatch):
    """The harness must CALL the shipped selector, never re-derive a score."""
    calls = []

    def fake(pick, market):
        calls.append((pick, market))
        return 0.42

    monkeypatch.setattr(h, "_slate_rows",
                        lambda root, day: [_parent("A vs B", "home_over_15")])
    monkeypatch.setattr(enh_registry, "enhancement_ml_probability", fake)
    rec = _record("A vs B", "home_over_15", 1.5)

    assert h.enh_ml_probability(ROOT, "2026-10-25", rec) == 0.42
    assert calls and calls[0][1] == "home_over_15"
    assert calls[0][0]["contract_id"] == "pfc_" + "a" * 24


def test_the_parent_is_matched_on_the_contract_id_not_just_the_fixture(monkeypatch):
    """Two markets on one fixture are two parents; the contract id decides."""
    monkeypatch.setattr(h, "_slate_rows", lambda root, day: [
        _parent("A vs B", "home_over_15", contract="pfc_" + "b" * 24),
        _parent("A vs B", "match_over_25", contract="pfc_" + "a" * 24),
    ])
    rec = _record("A vs B", "match_over_25", 1.5)
    assert h.archived_parent(ROOT, "2026-10-25", rec)["contract_id"] == "pfc_" + "a" * 24


def test_a_slate_without_a_model_scores_nothing(monkeypatch):
    """Pre-2026-10-25 archives carry no retained model: the live call is None."""
    row = _parent("A vs B", "home_over_15")
    row["statistical_profile"] = {}
    monkeypatch.setattr(h, "_slate_rows", lambda root, day: [row])
    rec = _record("A vs B", "home_over_15", 1.5)
    assert h.enh_ml_probability(ROOT, "2026-10-25", rec) is None


def test_a_tampered_model_key_scores_nothing(monkeypatch):
    """The shipped hash guard still applies through the replay path."""
    row = _parent("A vs B", "home_over_15")
    model = {"schema": "enh_score_logit_v1", "model_key": "0" * 64,
             "contract_id": row["contract_id"], "selection": "over",
             "as_of_exclusive": row["date"], "train_last_date": "2026-10-24",
             "n": 500, "classes": ["0:0", "1:0"], "coef": [[0.1], [0.1]],
             "intercept": [0.0, 0.0], "feature_min": 0.0, "feature_max": 1.0}
    row["statistical_profile"] = {"contract_id": row["contract_id"],
                                  "selection": "over",
                                  "as_of_exclusive": row["date"],
                                  "n": 1000, "ml_model": model}
    monkeypatch.setattr(h, "_slate_rows", lambda root, day: [row])
    assert h.enh_ml_probability(ROOT, "2026-10-25", _record("A vs B", "home_over_15", 1.5)) is None


def test_coverage_is_keyed_by_day_contract_and_market(monkeypatch):
    rows = [_parent("A vs B", "home_over_15", contract="pfc_" + "c" * 24),
            _parent("C vs D", "match_over_25", contract="pfc_" + "d" * 24)]
    for row in rows:
        row["statistical_profile"] = {"ml_model": {"score": 0.5}}
    monkeypatch.setattr(h, "_slate_rows", lambda root, day: rows)

    def fake(pick, market):
        return 0.6 if pick["contract_id"] == "pfc_" + "c" * 24 else None

    monkeypatch.setattr(enh_registry, "enhancement_ml_probability", fake)
    records = [_record("A vs B", "home_over_15", 1.5, contract="pfc_" + "c" * 24),
               _record("C vs D", "match_over_25", 1.7, contract="pfc_" + "d" * 24)]
    scores, stats = h.enh_ml_coverage(records, root=ROOT)

    assert scores[h._enh_score_key(records[0])] == 0.6
    assert h._enh_score_key(records[1]) not in scores
    assert (stats["legs"], stats["scored"]) == (2, 1)
    assert stats["scored_days"] == {"2026-10-25"}
    assert (stats["first_day"], stats["last_day"]) == ("2026-10-25", "2026-10-25")


def _evidence(book="pinnacle", source="pinnapi_odds"):
    return {"basis": "cohort_payout_bound",
            "price_context": {"book": book, "source": source}}


def _pool_leg(match, market, prob, odds, ml=None):
    return {"match": match, "pick": market, "prob": prob, "odds": odds,
            "market": market, "cohort_evidence": _evidence(),
            "ml_rank_probability": ml, "row": {"home": match.split(" vs ")[0],
                                               "away": match.split(" vs ")[1]}}


def test_an_ml_score_can_change_which_legs_the_card_takes():
    """Positive control: the selector really engages, and it can reorder."""
    pool = [_pool_leg("A vs B", "match_over_25", 0.90, 1.40, ml=0.10),
            _pool_leg("C vs D", "match_over_25", 0.89, 1.40, ml=0.11),
            _pool_leg("E vs F", "match_over_25", 0.70, 1.40, ml=0.90),
            _pool_leg("G vs H", "match_over_25", 0.69, 1.40, ml=0.91)]

    cohort_pool = [dict(l, ml_rank_probability=None) for l in pool]
    cohort = at.plan_day(cohort_pool, 100.0, stake_frac=0.125, max_accas=1,
                         rank="prob", enhancements=True)
    # With no model score the recipe takes the two best cohort rates …
    assert {l["match"] for a in cohort for l in a["legs"]} == {"A vs B", "C vs D"}

    scored = at.plan_day(pool, 100.0, stake_frac=0.125, max_accas=1, rank="prob",
                         enhancements=True)
    # ML-promoted legs are the top of the pool, and the card takes them.
    taken = {l["match"] for a in scored for l in a["legs"]}
    assert taken == {"E vs F", "G vs H"}, taken


def test_without_ml_scores_the_cohort_order_is_untouched():
    pool = [_pool_leg("A vs B", "match_over_25", 0.90, 1.40),
            _pool_leg("C vs D", "match_over_25", 0.89, 1.40),
            _pool_leg("E vs F", "match_over_25", 0.70, 1.40),
            _pool_leg("G vs H", "match_over_25", 0.69, 1.40)]
    plan = at.plan_day(pool, 100.0, stake_frac=0.125, max_accas=1, rank="prob",
                       enhancements=True)
    assert {l["match"] for a in plan for l in a["legs"]} == {"A vs B", "C vs D"}


def test_a_zero_model_score_is_scored_not_missing():
    """Live keeps two rank groups; a 0.0 score still counts as model output."""
    pool = [_pool_leg("A vs B", "match_over_25", 0.90, 1.40, ml=0.0),
            _pool_leg("C vs D", "match_over_25", 0.89, 1.40, ml=None)]
    plan = at.plan_day(pool, 100.0, stake_frac=0.125, max_accas=1, rank="prob",
                       enhancements=True)
    assert "A vs B" in {l["match"] for a in plan for l in a["legs"]}


def test_the_card_is_built_in_exactly_one_place(monkeypatch):
    """``enh_cards_for`` and ``enh_day_growth`` must share ``enh_day_plans``."""
    records = [_record("A vs B", "match_over_15", 1.50, cohort=0.80),
               _record("C vs D", "match_over_25", 1.60, cohort=0.75)]
    floors = {"match_over_15": 1.30, "match_over_25": 1.30}
    monkeypatch.setattr(h, "_slate_rows", lambda root, day: [])
    plans = h.enh_day_plans(records, floors, supported=False, root=ROOT)
    cards = h.enh_cards_for(records, floors, supported=False, root=ROOT)

    plan, _pool = plans["2026-10-25"]
    assert cards["2026-10-25"] == [
        frozenset((h._fold_name(l["match"]), round(float(l["odds"]), 2)) for l in a["legs"])
        for a in plan]
    # …and the P&L arm scores the same day, not a different one.
    days = h.enh_day_growth(records, floors, supported=False, root=ROOT)
    assert set(days) == set(plans)


def test_the_ml_arm_engages_the_selector(monkeypatch):
    """``ml_scores`` must turn the ML branch on, or the arm is a silent no-op.

    ``select_accas`` only orders by the model behind ``enhancements=True``. An
    arm that passed scores while leaving it False would report "no card change"
    for a selector it never ran, so the flag is asserted directly.
    """
    calls = []

    def recorder(pool, bank, **kwargs):
        calls.append(kwargs)
        return []

    monkeypatch.setattr(at, "plan_day", recorder)
    records = [_record("A vs B", "match_over_15", 1.50, cohort=0.80),
               _record("C vs D", "match_over_25", 1.60, cohort=0.75)]
    floors = {"match_over_15": 1.30, "match_over_25": 1.30}
    scores = {h._enh_score_key(records[0]): 0.2}

    h.enh_day_plans(records, floors, ml_scores=scores, root=ROOT)
    assert calls and calls[0]["enhancements"] is True

    calls.clear()
    h.enh_day_plans(records, floors, root=ROOT)
    assert calls and calls[0]["enhancements"] is False

    # …and the score itself reaches the leg the selector reads.
    pool_seen = {}
    real_plan = at.plan_day

    def capture(pool, bank, **kwargs):
        pool_seen.update({l["match"]: l["ml_rank_probability"] for l in pool})
        return real_plan(pool, bank, **kwargs)

    monkeypatch.setattr(at, "plan_day", capture)
    h.enh_day_plans(records, floors, ml_scores=scores, root=ROOT)
    assert pool_seen["A vs B"] == 0.2
    assert pool_seen["C vs D"] is None


def test_the_shipped_selector_recomputes_on_the_real_archived_slate():
    """Integration: the live function still scores a committed 10-25 row.

    This is the ONLY day in the repository whose slate carries the retained
    model, which is exactly why the report refuses to call the arm an A/B.
    """
    slate = ROOT / "localdata" / "picks_morning_2026-10-25.json"
    if not slate.exists():                                   # pragma: no cover
        pytest.skip("archived 2026-10-25 slate not present")
    rows = json.loads(slate.read_text())
    scored = 0
    for row in rows:
        for note in row.get("event_notes") or []:
            market = note.get("market")
            if not market:
                continue
            parent = dict(row, recommended_enhancement=market)
            if enh_registry.enhancement_ml_probability(parent, market) is not None:
                scored += 1
    assert scored > 0, "the retained model must still score the 2026-10-25 slate"


def test_coverage_cannot_overwrite_another_fixture_on_the_same_contract(monkeypatch):
    rows = [_parent('A vs B','match_over_25'), _parent('C vs D','match_over_25')]
    for row in rows:
        row['statistical_profile']['ml_model'].update(schema='enh_score_logit_v2',model_key=row['home'])
    monkeypatch.setattr(h,'_slate_rows',lambda root,day:rows)
    monkeypatch.setattr(enh_registry,'enhancement_ml_probability',lambda row,market: .2 if row['home']=='A' else .8)
    records=[_record('A vs B','match_over_25',1.5), _record('C vs D','match_over_25',1.5)]
    scores,stats=h.enh_ml_coverage(records,root=ROOT)
    assert scores[h._enh_score_key(records[0])] == .2
    assert scores[h._enh_score_key(records[1])] == .8
    assert stats['schemas']=={'enh_score_logit_v2':2}
    assert all(p['decision_time_status']=='UNPROVEN_ARCHIVE' for p in stats['provenance'])
    assert [p['model_key'] for p in stats['provenance']] == ['A','C']


def test_shared_archive_resolution_keeps_morning_and_late_additions_without_enrichment(tmp_path):
    import json
    base=tmp_path/'localdata';base.mkdir()
    morning=dict(_parent('A vs B','match_over_25'),built_at_utc='2026-10-25T05:00:00Z')
    later=dict(morning,built_at_utc='2026-10-25T20:00:00Z',recommended_enhancement='match_over_25')
    addition=_parent('C vs D','match_over_25')
    (base/'picks_morning_2026-10-25.json').write_text(json.dumps([morning]))
    (base/'picks_2026-10-25.json').write_text(json.dumps([later,addition]))
    rows=h._slate_rows(tmp_path,'2026-10-25')
    assert rows == [morning,addition]
    assert 'recommended_enhancement' not in rows[0]  # no later model/evidence laundering


def _comparison_context():
    pool=[_pool_leg('A vs B','match_over_25',.9,1.4,.2),
          _pool_leg('C vs D','match_over_25',.89,1.4,.21),
          _pool_leg('E vs F','match_over_25',.7,1.4,.9),
          _pool_leg('G vs H','match_over_25',.69,1.4,.91)]
    for leg in pool:
        leg.update(ml_model_schema='enh_score_logit_v2',ml_model_key='key')
    options=at.ticket_planner_options('enh');options.update(max_accas=1, model_min_prob=0., ml_enabled=True)
    return dict(lane='enh',date='2026-10-25',bank_eff=80.,options=options),dict(pool=pool)


def test_same_receipt_comparison_is_read_only_and_does_not_guess_counterfactual_results():
    import copy
    context,prepared=_comparison_context()
    before=copy.deepcopy((context,prepared))
    plan=at.plan_ticket_decision(context,prepared=prepared)
    history=[dict(date=context['date'],accas=[dict(plan[0],legs=[dict(l,result='win') for l in plan[0]['legs']])])]
    report=h.enh_decision_comparison(context,prepared,history=history,allow_outcomes=True)
    on,off=report['arms']['ml_on'],report['arms']['ml_off']
    assert on['total_stake']==off['total_stake']==10.
    assert report['removed_from_ml_off']==report['added_to_ml_on']==2
    assert report['execution_leg_symmetric_difference']==4
    assert on['returned']==19.6 and off['returned'] is None
    assert off['resolved_legs']==0 and report['status']=='INCOMPLETE_OUTCOMES'
    assert 'No joint expected return' in report['caveat']
    assert report['schemas']=={'enh_score_logit_v2':4}
    assert (context,prepared)==before
    draft=h.enh_decision_comparison(context,prepared,history=history)
    assert draft['arms']['ml_on']['returned'] is None  # no draft money attribution


def test_counterfactual_void_and_early_loss_use_existing_grading_rules():
    context,prepared=_comparison_context()
    plan=at.plan_ticket_decision(context,prepared=prepared)
    legs=plan[0]['legs']
    history=[dict(date=context['date'],accas=[dict(legs=[dict(legs[0],result='win'),dict(legs[1],result='void')])])]
    result=h.enh_decision_comparison(context,prepared,history=history,allow_outcomes=True)
    assert result['arms']['ml_on']['returned']==14.
    history[0]['accas'][0]['legs']=[dict(legs[0],result='loss')]
    result=h.enh_decision_comparison(context,prepared,history=history,allow_outcomes=True)
    assert result['arms']['ml_on']['returned']==0.
    assert result['arms']['ml_off']['returned'] is None


def test_descriptive_scoring_reports_schema_fixture_and_missing_denominators():
    common=dict(match='A vs B',result='win',prob=.7,ml_rank_probability=.8,
                ml_model_key='k',ml_model_schema='enh_score_logit_v2')
    rows=[dict(date='2026-10-25',accas=[dict(legs=[common,dict(common,market='btts_yes'),
         dict(match='C vs D',result='loss')])])]
    report=h._attributed_ml_scores(rows)
    assert report['eligible_binary_legs']==3 and report['missing_attribution']==1
    scores=report['by_schema']['enh_score_logit_v2']
    assert scores['records']==2 and scores['fixtures']==1
    assert scores['model_brier']==pytest.approx(.04)
    assert scores['cohort_brier']==pytest.approx(.09)
    assert 'No significance claim' in report['caveat']


def test_mixed_schema_legacy_report_suppresses_pooled_delta(monkeypatch,capsys):
    from types import SimpleNamespace
    records=[_record('A vs B','match_over_25',1.5)]
    monkeypatch.setattr(h,'enh_records',lambda:records)
    monkeypatch.setattr(h,'enh_day_growth',lambda *a,**kw:{})
    summary=dict(days=0,bets=0,hits=0,rate=0,mean_log_growth=0,no_bet_days=0,
                 firing_days=0,no_bet_freq=0,_days_detail={})
    monkeypatch.setattr(h,'enh_arm',lambda *a,**kw:dict(summary))
    stats=dict(first_day='2026-10-25',last_day='2026-10-26',scored=2,legs=2,
               scored_days={'2026-10-25','2026-10-26'},days={'2026-10-25','2026-10-26'},
               schemas={'enh_score_logit_v1':1,'enh_score_logit_v2':1},provenance=[])
    monkeypatch.setattr(h,'enh_ml_coverage',lambda *a,**kw:({},stats))
    assert h.cmd_enhancements(SimpleNamespace(ab=None,enh_ml=True,root=ROOT))==0
    output=capsys.readouterr().out
    assert 'MIXED SCHEMAS: pooled ML delta suppressed' in output
    assert 'vs supported cohort ordering:' not in output
    assert 'single-feature logistic on the same avg_p' not in output


def test_capacity_rescue_is_visible_in_same_pool_comparison():
    slots=[('A','X'),('B','X'),('A','Y'),('C','Y'),('B','Z'),('D','Z'),('E','W'),('F','W')]
    rates=dict(A=.7,B=.7,C=.9,D=.89,E=.85,F=.84)
    pool=[]
    for name,book in slots:
        leg=_pool_leg(f'{name} vs Opponent','match_over_25',rates[name],2.,{'A':.95,'B':.94}.get(name))
        leg['cohort_evidence']=_evidence(book=book)
        leg.update(price_book=book,price_source='pinnapi_odds')
        pool.append(leg)
    context=dict(lane='enh',date='2026-10-25',bank_eff=100.,options=at.ticket_planner_options('enh'))
    context['options']['model_min_prob'] = 0.  # captured pre-floor capacity recipe
    report=h.enh_decision_comparison(context,dict(pool=pool))
    on,off=report['arms']['ml_on'],report['arms']['ml_off']
    assert len(on['accas'])==len(off['accas'])==3
    assert on['selector_trace']['capacity_rescue_checked'] is True
    assert on['selector_trace']['capacity_rescue_changed'] is True
    assert off['selector_trace']['capacity_rescue_checked'] is False
    assert off['selector_trace']['capacity_rescue_changed'] is False


def test_counterfactual_uses_shared_scores_without_changing_saved_decision():
    import copy
    context, prepared = _comparison_context()
    before = copy.deepcopy((context, prepared))
    # Cohort-only A/B and C/D are absent from the actual ML ticket's history.
    facts = at._SettledOutcomes({}, {}, {
        (context['date'], hk, ak): score
        for home, away, score in [('A', 'B', (2, 1)), ('C', 'D', (0, 1))]
        for hk, ak in at._result_write_keys(home, away)
    })
    report = h.enh_decision_comparison(context, prepared, allow_outcomes=True, settled=facts)
    off = report['arms']['ml_off']
    assert off['returned'] == 0.0
    assert off['resolved_legs'] == 2
    assert [l['result'] for l in off['accas'][0]['legs']] == ['win', 'loss']
    assert {l['outcome_source'] for l in off['accas'][0]['legs']} == {'shared_settlement_facts'}
    assert (context, prepared) == before
    # A draft must not acquire returns merely because final scores now exist.
    draft = h.enh_decision_comparison(context, prepared, settled=facts)
    assert draft['arms']['ml_off']['returned'] is None


def test_shared_score_fallback_preserves_ledger_conflicts_and_missing_results():
    context, prepared = _comparison_context()
    leg = prepared['pool'][0]
    history = [dict(date=context['date'], accas=[dict(legs=[
        dict(leg, result='win'), dict(leg, result='loss')])])]
    facts = at._SettledOutcomes({}, {}, {
        (context['date'], hk, ak): (3, 0) for hk, ak in at._result_write_keys('A', 'B')})
    report = h.enh_decision_comparison(context, prepared, history=history,
                                      allow_outcomes=True, settled=facts)
    legs = report['arms']['ml_off']['accas'][0]['legs']
    assert [l['result'] for l in legs] == [None, None]
    assert legs[0]['unresolved_reason'] == 'ledger_outcome_conflict'
    assert legs[1]['unresolved_reason'] == 'missing_final_score'
    assert report['arms']['ml_off']['returned'] is None


def test_early_loss_ledger_unknown_leg_can_use_later_shared_score():
    context, prepared = _comparison_context()
    leg = prepared['pool'][0]
    history = [dict(date=context['date'], accas=[dict(legs=[dict(leg, result=None)])])]
    facts = at._SettledOutcomes({}, {}, {
        (context['date'], hk, ak): (3, 0) for hk, ak in at._result_write_keys('A', 'B')})
    report = h.enh_decision_comparison(context, prepared, history=history,
                                      allow_outcomes=True, settled=facts)
    resolved = report['arms']['ml_off']['accas'][0]['legs'][0]
    assert resolved['result'] == 'win'
    assert resolved['outcome_source'] == 'shared_settlement_facts'
    assert history[0]['accas'][0]['legs'][0]['result'] is None
