"""Forward-only ML paper lane, isolated from all live financial state."""

import hashlib
import json
from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest

import scripts.auto_tickets as at
import scripts.auto_tickets_grade as grade
from edgefactory import ml_paper as mp
from edgefactory.consensus_contracts import enhancement_fixture_identity
from edgefactory.enh_registry import enhancement_ml_probability, enhancement_ml_score_weights
from edgefactory.util import norm_team

DAY = "2026-11-02"
NOW = datetime(2026, 11, 2, 6, tzinfo=UTC)
FREEZE = datetime(2026, 11, 2, 7, tzinfo=UTC)


def pick(i=1, *, bucket="CAUTION", n=60):
    row = {
        "date": DAY,
        "home": f"Home Club {i}",
        "away": f"Away Club {i}",
        "sport": "soccer",
        "league": "Test League",
        "pick": "home",
        "market": "1x2",
        "avg_p": 75.0,
        "bucket": bucket,
        "contract_id": "pfc_" + "a" * 24,
        "contract_schema": "post_forebet_v1",
        "kickoff_utc": (NOW + timedelta(hours=4)).isoformat(),
        "as_of": NOW.isoformat(),
        "odds": 2.0,
        "bookmaker": "Pinnacle",
        "odds_source": "pinnapi_odds",
        "odds_captured_at": (NOW - timedelta(minutes=10)).isoformat(),
    }
    model = {
        "schema": "enh_score_logit_v2",
        "contract_id": row["contract_id"],
        "selection": "home",
        "as_of_exclusive": DAY,
        "train_last_date": "2026-11-01",
        "n": n,
        "feature_min": 0.1,
        "feature_max": 0.99,
        "feature_cols": ["confidence", "home_form_gf"],
        "feature_means": {"confidence": 0.7, "home_form_gf": 1.5},
        "feature_scales": {"confidence": 0.1, "home_form_gf": 0.5},
        "feature_observed_n": {"confidence": n, "home_form_gf": n},
        "classes": ["0:0", "1:0", "2:1", "0:1"],
        "coef": [[0.0, 0.0, 0.0]] * 4,
        "intercept": [
            -2.302585092994046,
            -1.6094379124341003,
            -0.6931471805599453,
            -1.6094379124341003,
        ],
    }
    model["model_key"] = hashlib.sha256(
        json.dumps(model, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    inp = {
        "fixture": enhancement_fixture_identity(row),
        "contract_id": row["contract_id"],
        "model_key": model["model_key"],
        "values": {"confidence": 0.75, "home_form_gf": 2.0},
    }
    row["statistical_profile"] = {
        "ml_model": model,
        "ml_inputs": inp,
        "n": n,
        "selection": "home",
        "contract_id": row["contract_id"],
        "as_of_exclusive": DAY,
    }
    return row


def context(rows):
    return {"lane": "main", "date": DAY, "build_at": NOW.isoformat(), "slate": rows}


def run_capture(tmp_path, ctx, *, now=NOW, lookup=lambda c: None, **kwargs):
    return mp.capture(
        ctx,
        root=tmp_path,
        score_lookup=lookup,
        kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection,
        min_leg_odds=1.0,
        freeze_hour=9,
        now=now,
        index=kwargs.pop("index", {}),
        **kwargs,
    )


def capture(tmp_path, rows=None, **kwargs):
    ctx = context(rows if rows is not None else [pick(1), pick(2), pick(3)])
    draft = run_capture(tmp_path, ctx, **kwargs)
    if draft is None:
        return None
    assert draft["status"] == "draft_not_yet_frozen"
    assert not mp.receipt_path(tmp_path, DAY).exists()
    return run_capture(tmp_path, {}, now=FREEZE)


def candidate(i, *, odds=2.0, p=0.7, market="1x2", bucket="CAUTION", book="Pinnacle", date=DAY):
    return {
        "candidate_id": str(i),
        "kickoff_utc": date + "T12:00:00+00:00",
        "date": date,
        "home": f"Home Club {i}",
        "away": f"Away Club {i}",
        "fixture": [date, f"homeclub{i}", f"awayclub{i}"],
        "market": market,
        "selection": "home",
        "bucket": bucket,
        "odds": odds,
        "base_probability": p,
        "probability": p,
        "book": book,
    }


def receipt(day, cs, accas=None):
    return {
        "schema": "autobets_ML_v1",
        "paper_available_at_decision": 100.0,
        "date": day,
        "captured_at": day + "T06:00:00+00:00",
        "draft_persisted_at": day + "T06:00:00+00:00",
        "freeze_at": day + "T09:00:00+02:00",
        "persisted_at": day + "T07:00:00+00:00",
        "draft_sha256": "0" * 64,
        "status": "paper_accas" if accas else "no_paper_bet",
        "candidates": cs,
        "models": {},
        "learning": {"status": "awaiting_prior_paper_results"},
        "accas": [dict(a, stake_units=a.get("stake_units", 1.0)) for a in (accas or [])],
    }


def test_capture_uses_bound_existing_ml_and_never_mutates_inputs(tmp_path):
    rows = [pick(i) for i in range(1, 7)]
    before = deepcopy(rows)
    r = capture(tmp_path, rows)
    assert rows == before
    assert r["status"] == "paper_accas" and r["accas"]
    assert all(a["stake_units"] > 0 for a in r["accas"])
    assert sum(a["stake_units"] for a in r["accas"]) <= 100.0
    assert r["policy"]["odds_band"] is None
    assert len({tuple(c["fixture"]) for a in r["accas"] for c in a["legs"]}) == 6
    assert r["learning"]["status"] == "awaiting_prior_paper_results"
    assert {p.name for p in tmp_path.glob("*state*")} == {mp.state_path(tmp_path).name}
    assert mp.receipts(tmp_path) == [r]
    assert not {"main_plan", "main_comparison", "bank", "stake_pct"} & r.keys()


def test_write_once_and_corrupt_history_is_not_reset(tmp_path):
    r = capture(tmp_path)
    path = mp.receipt_path(tmp_path, DAY)
    before = path.read_bytes()
    assert capture(tmp_path, [pick(9)]) is None
    assert path.read_bytes() == before
    data = json.loads(before)
    data["status"] = "tampered"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="invalid ML paper receipt"):
        mp.receipts(tmp_path)
    assert r["status"] == "paper_accas"


@pytest.mark.parametrize(
    "change",
    [
        {"date": "2026-11-01"},
        {"build_at": (NOW - timedelta(minutes=6)).isoformat()},
        {"build_at": (NOW + timedelta(seconds=1)).isoformat()},
    ],
)
def test_no_stale_or_future_context_capture(tmp_path, change):
    ctx = context([pick()])
    ctx.update(change)
    assert (
        mp.capture(
            ctx,
            root=tmp_path,
            score_lookup=lambda c: None,
            kickoff_fn=at.parse_kickoff_proven,
            source_guard=at.execution_source_rejection,
            min_leg_odds=1.3,
            freeze_hour=9,
            now=NOW,
            index={},
        )
        is None
    )
    assert not list(tmp_path.glob("*.json"))


def test_pre_freeze_draft_is_not_a_settled_card_or_performance_history(tmp_path):
    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    assert draft["status"] == "draft_not_yet_frozen"
    assert mp.state_path(tmp_path).exists()
    assert mp.receipts(tmp_path) == []
    assert mp.performance(mp.receipts(tmp_path), lambda c: (2, 0))["settled_accas"] == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("odds", float("nan")),
        ("odds", True),
        ("odds", 1.0),
        ("odds_source", "boggio"),
        ("bookmaker", ""),
        ("bookmaker", "Betfair Exchange"),
        ("odds_captured_at", None),
        ("odds_captured_at", (NOW + timedelta(seconds=1)).isoformat()),
        ("odds_captured_at", (NOW - timedelta(hours=13)).isoformat()),
        ("kickoff_utc", "14:00"),
        ("kickoff_utc", (NOW + timedelta(minutes=29)).isoformat()),
        ("bucket", "WATCHLIST_SUSPECT_PRICE"),
        ("bucket", "WATCHLIST_NO_ODDS"),
        ("price_evidence", "SUSPECT_ALIAS_FUZZY"),
    ],
)
def test_invalid_price_identity_or_time_never_gets_paper_legs(tmp_path, field, value):
    rows = [pick(i) for i in range(1, 4)]
    for row in rows:
        row[field] = value
    r = capture(tmp_path, rows)
    assert r["accas"] == [] and r["status"] == "no_paper_bet"


def test_missing_borrowed_tampered_or_future_model_has_no_fallback(tmp_path):
    rows = [pick(i) for i in range(1, 5)]
    rows[0]["statistical_profile"]["ml_inputs"]["fixture"][1] = "wrongteam"
    rows[1]["statistical_profile"]["ml_model"]["train_last_date"] = DAY
    rows[2]["statistical_profile"]["ml_model"]["coef"][0][0] = 1.0
    rows[3]["statistical_profile"] = {}
    assert capture(tmp_path, rows)["candidates"] == []


def test_paper_reuses_model_even_when_live_enh_ml_ordering_is_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ENH_ML", "0")
    assert enhancement_ml_probability(pick(), "match_over_25") is None
    assert enhancement_ml_score_weights(pick()) is not None
    assert capture(tmp_path)["accas"]


def test_secondary_totals_btts_and_team_totals_require_full_quote_identity(tmp_path):
    rows = [pick(i) for i in range(1, 3)]
    index = {"fixture_quotes": {}}
    for row in rows:
        pair = (norm_team(row["home"]), norm_team(row["away"]))
        q = (
            4.1,
            "Pinnacle",
            row["odds_captured_at"],
            "pinnapi_odds",
            row["kickoff_utc"],
            None,
            (row["home"], row["away"]),
        )
        index["fixture_quotes"][pair] = {
            ("ou_2.5", "over"): [q],
            ("btts", "no"): [q],
            ("tt_home_1.5", "over"): [q],
        }
    r = capture(tmp_path, rows, index=index)
    assert {"1x2", "match_over_25", "btts_no", "home_over_15"} == {
        c["market"] for c in r["candidates"]
    }
    assert any(c["market"] != "1x2" for a in r["accas"] for c in a["legs"])
    other = deepcopy(index)
    for mapping in other["fixture_quotes"].values():
        for key, qs in mapping.items():
            mapping[key] = [(*qs[0][:6], ("Another Club", "Another Opponent"))]
    bad = capture(tmp_path / "bad", rows, index=other)
    assert {c["market"] for c in bad["candidates"]} == {"1x2"}


def test_no_swapped_or_legacy_width_nine_quote_admission(tmp_path):
    row = pick()
    q = (3.1, "Pinnacle", row["odds_captured_at"], "pinnapi_odds", row["kickoff_utc"], None)
    idx = {
        "fixture_quotes": {
            (norm_team(row["home"]), norm_team(row["away"])): {
                ("ou_2.5", "over"): [q, (*q, (row["away"], row["home"]))]
            }
        }
    }
    assert {c["market"] for c in capture(tmp_path, [row], index=idx)["candidates"]} == {"1x2"}


@pytest.mark.parametrize("odds", [1.21, 3.0, 10.0, 25.0, 400.0])
def test_no_acca_odds_band_or_live_minimum_leg_price(odds):
    # Authentic positive-EV quotes may sit below/at/above the removed band.
    leg = odds**0.5
    plan = mp.select_accas([candidate(1, odds=leg, p=0.99), candidate(2, odds=leg, p=0.99)])
    assert len(plan) == 1 and plan[0]["odds"] == pytest.approx(odds)
    assert plan[0]["stake_units"] > 0


def test_no_mixed_book_same_fixture_same_team_or_negative_ev_fallback():
    assert not mp.select_accas([candidate(1), candidate(2, book="Other Book")])
    a, b = candidate(1), candidate(2)
    b["fixture"] = a["fixture"]
    assert not mp.select_accas([a, b])
    b["fixture"] = [DAY, a["fixture"][1], "anotheropponent"]
    assert not mp.select_accas([a, b])
    assert not mp.select_accas([candidate(1, p=0.2), candidate(2, p=0.2)])
    assert not mp.select_accas([candidate(1)])


def test_lower_probability_and_caution_bucket_can_win_paper_search():
    a = candidate(1, odds=3.0, p=0.45, bucket="CAUTION")
    b = candidate(2, odds=2.0, p=0.65, bucket="SKIPPED_VETO")
    plan = mp.select_accas([a, b])
    assert len(plan) == 1 and plan[0]["odds"] == 6.0
    assert {c["bucket"] for c in plan[0]["legs"]} == {"CAUTION", "SKIPPED_VETO"}


def test_learning_uses_own_prior_results_and_fixture_weights_not_quote_count():
    yesterday = "2026-11-01"
    cs = [candidate(i, date=yesterday, p=0.8) for i in range(40)]
    # This bucket's 80% predictions have been wrong 75% of the time.
    history = [receipt(yesterday, cs), receipt(DAY, [candidate(999)])]
    lookup = lambda c: (2, 0) if int(c["candidate_id"]) % 4 == 0 else (0, 2)
    learner = mp.learn(history, NOW, lookup)
    assert learner["status"] == "fitted_prior_paper_errors"
    assert learner["fixtures"] == 40 and learner["training_last_date"] == yesterday
    before = deepcopy(history)
    next_rows = [candidate(50, p=0.8)]
    mp.apply_learning(next_rows, learner)
    assert next_rows[0]["probability"] < 0.8
    assert history == before
    duplicate = [receipt(yesterday, [dict(c, book=f"Book{j}") for c in cs[:2] for j in range(100)])]
    assert mp.learn(duplicate, NOW, lookup)["status"] == "awaiting_prior_paper_results"
    assert mp.learn([history[1]], NOW, lookup)["fixtures"] == 0
    assert mp.learn(history, NOW, lambda c: None)["fixtures"] == 0


def test_learning_bucket_and_market_columns_require_unique_fixture_evidence():
    yesterday = "2026-11-01"
    cs = [
        candidate(i, date=yesterday, p=0.8, bucket="CAUTION" if i < 35 else "RARE")
        for i in range(40)
    ]
    model = mp.learn(
        [receipt(yesterday, cs)], NOW, lambda c: (2, 0) if int(c["candidate_id"]) % 2 else (0, 1)
    )
    assert "bucket:CAUTION" in model["columns"]
    assert "bucket:RARE" not in model["columns"]
    assert model["observations"] == 40


def test_own_roi_bank_pending_losses_drawdown_and_no_bet_are_separate():
    c1, c2, c3, c4 = [candidate(i) for i in range(1, 5)]
    a1 = {"legs": [c1, c2], "odds": 4.0}
    a2 = {"legs": [c3, c4], "odds": 4.0}
    history = [
        receipt("2026-11-01", [c1, c2], [a1]),
        receipt(DAY, [c3, c4], [a2]),
        receipt("2026-11-03", []),
    ]
    before = deepcopy(history)

    def scores(c):
        return (
            (2, 0)
            if c["candidate_id"] in {"1", "2"}
            else (0, 1)
            if c["candidate_id"] == "3"
            else None
        )

    r = mp.performance(history, scores)
    assert (r["wins"], r["losses"], r["pending_accas"]) == (1, 1, 0)
    assert r["profit_units"] == 2.0 and r["roi"] == 1.0
    assert r["unresolved_result_legs"] == 1 and r["resolved_result_legs"] == 3
    assert r["history"][1]["accas"][0]["leg_outcomes"] == [False, None]
    assert r["paper_bank_units"] == 102.0 and r["max_daily_close_drawdown_units"] == 1.0
    assert r["no_bet_days"] == 1 and history == before
    missing = mp.performance(history, lambda c: None)
    assert missing["roi"] is None and missing["pending_accas"] == 2
    assert "Main" not in mp.render_performance(r)


def test_exact_settlement_adapter_refuses_narrow_and_conflicting_keys():
    c = candidate(1)
    specs = at._result_write_key_specs(c["home"], c["away"])
    narrow = {(DAY, h, a): (2, 0) for h, a, n in specs if n}
    assert at.ml_paper_score_lookup(narrow, now=FREEZE + timedelta(days=1))(c) is None
    keys = [(DAY, h, a) for h, a, n in specs if not n]
    scores = {k: (2, 0) for k in keys}
    assert at.ml_paper_score_lookup(scores, now=FREEZE + timedelta(days=1))(c) == (2, 0)
    assert at.ml_paper_score_lookup({(DAY, "otherhome", "otheraway"): (2, 0)}, now=FREEZE + timedelta(days=1))(c) is None


def test_grade_paper_never_loads_or_saves_financial_state(tmp_path, monkeypatch, capsys):
    capture(tmp_path)
    monkeypatch.setattr(grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(grade.at, "load_settled_scores", dict)

    def forbidden(*a, **k):
        raise AssertionError("financial state touched")

    for engine in (at, grade.at):
        monkeypatch.setattr(engine, "load_state", forbidden)
        monkeypatch.setattr(engine, "save_state", forbidden)
        monkeypatch.setattr(engine, "settle_open_slips", forbidden)
    assert grade.main(["--lane", "autobets_ML"]) == 0
    output = capsys.readouterr().out
    assert "autobets_ML" in output and "PAPER ONLY" in output
    assert (tmp_path / "autobets_ML_performance.json").exists()
    assert {p.name for p in tmp_path.glob("*state*")} == {mp.state_path(tmp_path).name}


def test_existing_enh_report_shows_sibling_paper_card_without_comparison(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(grade.at, "load_state", lambda lane: None)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    assert grade.main(["--lane", "enh", "--no-settle"]) == 0
    out = capsys.readouterr().out
    assert "autobets_ML — performance" in out
    assert "comparison" not in out.lower()
    assert not list(tmp_path.iterdir())


def test_paper_failure_cannot_change_live_state_or_abort(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")

    def fail(*a, **k):
        raise ValueError("broken paper evidence")

    monkeypatch.setattr(mp, "receipts", fail)

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW

    monkeypatch.setattr(at, "datetime", Clock)
    at._run_ml_paper()
    assert "live lanes unchanged" in capsys.readouterr().err
    assert not list(tmp_path.glob("*state*"))


def test_receipts_are_persistable_but_not_pick_archives(tmp_path):
    import subprocess

    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"],
        input=(
            "localdata/autobets_ML_2026-11-02.json\n"
            "localdata/autobets_ML_performance.json\n"
            "localdata/autobets_ML_state.json\n"
        ),
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1 and not result.stdout
    assert not mp.receipt_path(tmp_path, DAY).name.startswith("picks_")


def test_prior_mistakes_can_change_bucket_preference_without_touching_live_rules():
    yesterday = "2026-11-01"
    cs = [
        candidate(i, date=yesterday, p=0.7, bucket="CAUTION" if i < 40 else "CERTIFIED_CLEAN")
        for i in range(80)
    ]

    def result(c):
        i = int(c["candidate_id"])
        return (2, 0) if i < 28 or 40 <= i < 48 else (0, 1)

    model = mp.learn([receipt(yesterday, cs)], NOW, result)
    next_rows = [candidate(100, bucket="CAUTION"), candidate(101, bucket="CERTIFIED_CLEAN")]
    live_options = deepcopy(at.ticket_planner_options("main"))
    mp.apply_learning(next_rows, model)
    assert next_rows[0]["probability"] > next_rows[1]["probability"]
    assert at.ticket_planner_options("main") == live_options


def test_report_refresh_cannot_rewrite_forward_predictions(tmp_path):
    r = capture(tmp_path)
    path = mp.receipt_path(tmp_path, DAY)
    before = path.read_bytes()
    state_before = mp.state_path(tmp_path).read_bytes()
    pending = mp.publish(tmp_path, lambda c: None)
    graded = mp.publish(tmp_path, lambda c: (2, 0))
    assert pending["pending_accas"] and graded["settled_accas"]
    assert path.read_bytes() == before
    assert mp.state_path(tmp_path).read_bytes() == state_before
    assert (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text() == mp.render_card(r)
    assert {p.name for p in tmp_path.glob("*state*")} == {mp.state_path(tmp_path).name}


@pytest.mark.parametrize("field", ["as_of", "built_at_utc"])
def test_future_input_timestamp_cannot_be_used(tmp_path, field):
    rows = [pick(i) for i in range(1, 4)]
    for row in rows:
        row[field] = (NOW + timedelta(seconds=1)).isoformat()
    r = capture(tmp_path, rows)
    assert r["status"] == "no_paper_bet"
    assert r["rejections"]["input_not_known_at_decision"] == 3


def test_own_leg_count_above_three_and_more_than_two_accas():
    rows = [candidate(4*i+j, book=f"Book{i}", p=p**.25, odds=p**-.5)
            for i, p in enumerate((.9, .6, .3)) for j in range(4)]
    plan = mp.select_accas(rows)
    assert len(plan) > 2
    assert any(len(a["legs"]) > 3 and a["odds"] > 10 for a in plan)
    assert len({c["candidate_id"] for a in plan for c in a["legs"]}) == 12
    large = mp.select_accas([candidate(i, p=0.99) for i in range(8)])
    assert max(len(a["legs"]) for a in large) == 8


def test_model_chooses_unequal_stakes_and_rescales_without_leverage():
    rows = [candidate(2*i+j, book=f"Book{i}", p=p**.5, odds=1/p)
            for i, p in enumerate((.9, .3)) for j in range(2)]
    before = deepcopy(rows)
    plan = mp.select_accas(rows)
    assert len(plan) == 2 and rows == before
    assert plan[0]["stake_units"] > plan[1]["stake_units"] > 1.0
    assert all(a["model_kelly_fraction"] > 0 for a in plan)
    assert 0 < sum(a["stake_units"] for a in plan) <= 25.0
    assert all(a["portfolio_allocation"]["kelly_multiplier"] == .25 for a in plan)
    smaller = mp.select_accas(rows, 25.0)
    for large, small in zip(plan, smaller):
        assert small["stake_units"] == pytest.approx(large["stake_units"] / 4, abs=1e-6)
    assert not mp.select_accas(rows, 0)
    assert not mp.select_accas(rows, -1)


def test_card_count_is_not_capped_even_when_budget_is_rescaled():
    rows = [candidate(2*i+j, book=f"Book{i}", p=p**.5, odds=1/p)
            for i, p in enumerate((.9, .75, .6, .45, .3, .15)) for j in range(2)]
    plan = mp.select_accas(rows)
    assert len(plan) == 6
    assert sum(a["stake_units"] for a in plan) <= 100.0
    assert all(a["stake_units"] > 0 for a in plan)


def test_latest_pre_cutoff_draft_freezes_without_reading_late_inputs_or_results(tmp_path):
    first = run_capture(tmp_path, context([pick(1), pick(2)]))
    last_at = FREEZE - timedelta(microseconds=1)
    last_ctx = dict(context([pick(3), pick(4)]), build_at=last_at.isoformat())
    last = run_capture(tmp_path, last_ctx, now=last_at)
    assert first["accas"] != last["accas"]
    draft_bytes = mp.state_path(tmp_path).read_bytes()

    def forbidden(*args):
        raise AssertionError("post-cutoff results must not change frozen stakes or picks")

    frozen = run_capture(tmp_path, {"slate": "DO NOT READ"}, now=FREEZE, lookup=forbidden)
    assert frozen["accas"] == last["accas"]
    assert frozen["candidates"] == last["candidates"]
    assert frozen["captured_at"] == last_at.isoformat()
    assert frozen["persisted_at"] == FREEZE.isoformat()
    assert frozen["freeze_at"] == "2026-11-02T09:00:00+02:00"
    before = mp.receipt_path(tmp_path, DAY).read_bytes()
    assert (
        run_capture(tmp_path, context([pick(9), pick(10)]), now=FREEZE + timedelta(hours=3)) is None
    )
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == before
    assert mp.state_path(tmp_path).read_bytes() == draft_bytes


def test_missed_freeze_is_no_bet_not_a_backdated_late_card(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("no late candidate generation, learning or selection")

    monkeypatch.setattr(mp, "candidates", forbidden)
    monkeypatch.setattr(mp, "learn", forbidden)
    late = FREEZE + timedelta(hours=4)
    r = run_capture(tmp_path, context([pick(1), pick(2)]), now=late, lookup=forbidden)
    assert r["status"] == "missed_freeze_no_paper_bet"
    assert not r["accas"] and not r["candidates"]
    assert r["captured_at"] == r["persisted_at"] == late.isoformat()
    assert "missed 09:00 freeze" in mp.render_card(r)
    assert run_capture(tmp_path, context([pick(3), pick(4)]), now=late) is None


def test_draft_cannot_regress_to_an_earlier_observation(tmp_path):
    later = NOW + timedelta(minutes=20)
    ctx = dict(context([pick(3), pick(4)]), build_at=later.isoformat())
    run_capture(tmp_path, ctx, now=later)
    before = mp.state_path(tmp_path).read_bytes()
    assert run_capture(tmp_path, context([pick(1), pick(2)])) is None
    assert mp.state_path(tmp_path).read_bytes() == before


@pytest.mark.parametrize("tamper", ["hash", "post_cutoff_persist"])
def test_invalid_draft_never_becomes_a_frozen_card(tmp_path, tamper):
    run_capture(tmp_path, context([pick(1), pick(2)]))
    path = mp.state_path(tmp_path)
    state = json.loads(path.read_text())
    row = state["pending_by_date"][DAY]
    if tamper == "hash":
        row["accas"][0]["stake_units"] *= 2
    else:
        row["draft_persisted_at"] = FREEZE.isoformat()
        row["sha256"] = mp.digest({k: v for k, v in row.items() if k != "sha256"})
    path.write_text(json.dumps(state))
    damaged = path.read_bytes()
    sealed = run_capture(tmp_path, {}, now=FREEZE)
    assert sealed["status"] == "missed_freeze_no_paper_bet"
    assert not sealed["accas"] and not sealed["candidates"]
    assert sealed["rejections"] == {"corrupt_pre_cutoff_draft": 1}
    assert path.read_bytes() == damaged
    assert (tmp_path / sealed["draft_integrity_error"]["quarantine"]).read_bytes() == damaged
    mp.validate_record(sealed, DAY)


def test_build_crossing_cutoff_cannot_persist_a_new_draft(tmp_path, monkeypatch):
    original = run_capture(tmp_path, context([pick(1), pick(2)]))
    times = iter([NOW + timedelta(minutes=30), FREEZE])

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(times)

    monkeypatch.setattr(mp, "datetime", Clock)
    ctx = dict(context([pick(3), pick(4)]), build_at=(NOW + timedelta(minutes=30)).isoformat())
    r = run_capture(tmp_path, ctx, now=None)
    assert r["accas"] == original["accas"]
    assert r["draft_sha256"] == original["sha256"]


def test_concurrent_freeze_keeps_one_unchanged_card(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: run_capture(tmp_path, {}, now=FREEZE), range(2)))
    assert sum(r is not None for r in results) == 1
    assert mp.receipts(tmp_path)[0]["accas"] == draft["accas"]


@pytest.mark.parametrize("lead,allowed", [(29, False), (30, True)])
def test_kickoff_lead_is_relative_to_nine_not_earlier_draft(tmp_path, lead, allowed):
    rows = [pick(1), pick(2)]
    for row in rows:
        row["kickoff_utc"] = (FREEZE + timedelta(minutes=lead)).isoformat()
    r = capture(tmp_path, rows)
    assert bool(r["accas"]) is allowed


def test_quote_must_still_be_within_age_limit_at_scheduled_freeze(tmp_path):
    rows = [pick(1), pick(2)]
    for row in rows:
        row["odds_captured_at"] = (NOW - timedelta(hours=11, minutes=30)).isoformat()
    r = capture(tmp_path, rows)
    assert not r["accas"]


@pytest.mark.parametrize("outcome,available", [(None, 0.0), ((0, 1), 0.0), ((2, 0), 400.0)])
def test_own_bank_compounds_reserves_pending_and_never_tops_up(tmp_path, outcome, available):
    cs = [candidate(90, date="2026-11-01"), candidate(91, date="2026-11-01")]
    prior = receipt("2026-11-01", cs, [{"legs": cs, "odds": 4.0, "stake_units": 100.0}])
    prior["sha256"] = mp.digest(prior)
    mp._write_once(mp.receipt_path(tmp_path, prior["date"]), prior)
    r = run_capture(tmp_path, context([pick(1), pick(2)]), lookup=lambda c: outcome)
    assert r["paper_available_at_decision"] == available
    if available:
        total = sum(a["stake_units"] for a in r["accas"])
        assert 0 < total <= available * mp.MAX_PAPER_EXPOSURE
        baseline = run_capture(tmp_path / "fresh", context([pick(1), pick(2)]))
        assert total == pytest.approx(sum(a["stake_units"] for a in baseline["accas"]) * 4, abs=5e-6)
    else:
        assert not r["accas"]
    assert r["paper_pending_reserved_at_decision"] == (100.0 if outcome is None else 0.0)
    assert {p.name for p in tmp_path.glob("*state*")} == {mp.state_path(tmp_path).name}


def test_variable_stakes_roi_is_weighted_and_missing_stakes_fail_closed():
    cs = [candidate(i) for i in range(4)]
    history = [
        receipt(
            DAY,
            cs,
            [
                {"legs": cs[:2], "odds": 4.0, "stake_units": 10.0},
                {"legs": cs[2:], "odds": 4.0, "stake_units": 2.0},
            ],
        )
    ]
    report = mp.performance(history, lambda c: (2, 0) if int(c["candidate_id"]) < 2 else (0, 1))
    assert report["profit_units"] == 28.0
    assert report["settled_stake_units"] == 12.0
    assert report["roi"] == pytest.approx(28 / 12)
    assert report["paper_bank_units"] == report["paper_free_units"] == 128.0
    assert report["paper_committed_units"] == 0.0
    del history[0]["accas"][0]["stake_units"]
    with pytest.raises(KeyError):
        mp.performance(history, lambda c: (2, 0))


def test_paper_cli_is_standalone_and_cannot_touch_financial_state(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at.sys, "argv", ["auto_tickets.py", "--autobets-ml"])
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    called = []
    monkeypatch.setattr(at, "_run_ml_paper", lambda: called.append("paper"))

    def forbidden(*a, **k):
        raise AssertionError("live state touched")

    monkeypatch.setattr(at, "load_state", forbidden)
    monkeypatch.setattr(at, "save_state", forbidden)
    monkeypatch.setattr(at, "settle_open_slips", forbidden)
    assert at.main() == 0 and called == ["paper"]
    monkeypatch.setattr(at.sys, "argv", ["auto_tickets.py", "--autobets-ml", "--force"])
    with pytest.raises(SystemExit):
        at.main()
    assert called == ["paper"]


def test_daily_runs_paper_independently_next_to_existing_tickets():
    import ast
    from pathlib import Path

    source = Path("scripts/daily.py").read_text()
    tree = ast.parse(source)
    commands = [
        n.args[0].value
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "run_soft"
        and n.args
        and isinstance(n.args[0], ast.Constant)
    ]
    assert commands.count("PYTHONPATH=src python3 scripts/auto_tickets.py --autobets-ml") == 1
    finalizer = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                     and n.name == "finalize_priced_candidate_slate")
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "run_ml_paper" for n in ast.walk(finalizer))
    assert commands.count("PYTHONPATH=src python3 scripts/auto_tickets.py") == 2
    assert "_capture_ml_paper(decision_context" not in Path("scripts/auto_tickets.py").read_text()


def test_future_receipt_cannot_supply_paper_capital_or_learning(tmp_path):
    future = "2026-11-03"
    cs = [candidate(90, date=future), candidate(91, date=future)]
    r = receipt(future, cs, [{"legs": cs, "odds": 4.0, "stake_units": 100.0}])
    r["sha256"] = mp.digest(r)
    mp._write_once(mp.receipt_path(tmp_path, future), r)
    draft = run_capture(tmp_path, context([pick(1), pick(2)]), lookup=lambda c: (2, 0))
    assert draft["paper_available_at_decision"] == 100.0
    assert draft["learning"]["fixtures"] == 0


def test_paper_draft_is_visible_without_becoming_a_performance_bet(tmp_path):
    draft = run_capture(tmp_path, context([pick(1), pick(2)]))
    before = mp.state_path(tmp_path).read_bytes()
    assert mp.latest_card(tmp_path, now=NOW) == draft
    after_cutoff = mp.latest_card(tmp_path, now=FREEZE)
    assert "awaiting_publication" in after_cutoff["status"]
    assert after_cutoff["accas"] == draft["accas"]
    assert mp.state_path(tmp_path).read_bytes() == before
    assert mp.receipts(tmp_path) == []
