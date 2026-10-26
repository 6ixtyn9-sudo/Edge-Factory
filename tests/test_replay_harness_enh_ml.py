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
def _clean_cache():
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

    assert scores[("2026-10-25", "pfc_" + "c" * 24, "home_over_15")] == 0.6
    assert ("2026-10-25", "pfc_" + "d" * 24, "match_over_25") not in scores
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
    scores = {("2026-10-25", "pfc_" + "a" * 24, "match_over_15"): 0.2}

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
