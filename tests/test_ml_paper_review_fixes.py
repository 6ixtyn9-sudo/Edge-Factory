"""Independent-review regressions: real bugs, policy v2 and input feasibility.

All captures are mocked/temp-only. No provider request or live ledger writes.
"""

import importlib.util
import itertools
from datetime import timedelta

import numpy as np
import pytest
from scipy.optimize import minimize
from test_ml_paper import DAY, FREEZE, NOW, at, candidate, context, pick, receipt, run_capture

from edgefactory import ml_paper as mp


def _scores(c, day, score):
    return {
        (day, h, a): score
        for h, a, narrow in at._result_write_key_specs(c["home"], c["away"])
        if not narrow
    }


@pytest.mark.parametrize("old_score", [None, (0, 4)])
def test_next_day_kickoff_settles_only_on_event_day_end_to_end(old_score):
    cs = [candidate(i) for i in (1, 2)]
    for c in cs:
        c["kickoff_utc"] = "2026-11-03T00:30:00Z"  # 02:30 SAST, not card day
    scores = {}
    for c in cs:
        scores.update(_scores(c, "2026-11-03", (2, 0)))
        if old_score is not None:
            scores.update(_scores(c, DAY, old_score))
    r = receipt(DAY, cs, [{"legs": cs, "odds": 4.0, "stake_units": 2.0}])
    before = at.ml_paper_score_lookup(scores, now=FREEZE)
    assert mp.performance([r], before)["pending_accas"] == 1
    lookup = at.ml_paper_score_lookup(scores, now=FREEZE + timedelta(days=2))
    result = mp.performance([r], lookup)
    assert result["wins"] == 1 and result["paper_committed_units"] == 0
    assert result["profit_units"] == 6.0
    wrong_only = {k: v for k, v in scores.items() if k[0] == DAY}
    assert at.ml_paper_score_lookup(wrong_only, now=FREEZE + timedelta(days=2))(cs[0]) is None


def test_sast_midnight_date_never_uses_receipt_or_utc_day():
    c = candidate(1)
    c["kickoff_utc"] = "2026-11-02T22:30:00Z"  # Nov 3 in SAST
    scores = _scores(c, DAY, (9, 0))
    lookup = at.ml_paper_score_lookup(scores, now=FREEZE + timedelta(days=2))
    assert lookup(c) is None
    scores.update(_scores(c, "2026-11-03", (0, 2)))
    assert lookup(c) is None  # no donor timezone/event identity proof
    c["kickoff_utc"] = "22:30"
    assert lookup(c) is None


@pytest.mark.parametrize("available", [None, True, float("inf"), -1.0])
def test_nonempty_receipts_require_valid_capital(available):
    cs = [candidate(1), candidate(2)]
    r = receipt(DAY, cs, [{"legs": cs, "odds": 4.0, "stake_units": 5000.0}])
    if available is None:
        r.pop("paper_available_at_decision")
    else:
        r["paper_available_at_decision"] = available
    # Test the forged-checksum attack on the existing read/restore validator.
    r["sha256"] = mp.digest(r) if available != float("inf") else "unhashable-nonfinite"
    with pytest.raises(ValueError):
        mp.validate_record(r, DAY)


def test_mixed_negative_single_ev_acca_is_searchable_in_both_orders():
    for a, b in [
        (candidate(1, p=0.4), candidate(2, p=0.9)),
        (candidate(2, p=0.4), candidate(1, p=0.9)),
    ]:
        plan = mp.select_accas([a, b])
        assert len(plan) == 1
        assert plan[0]["estimated_ev"] == pytest.approx(0.44)
        assert plan[0]["stake_units"] > 0


def test_small_universe_proposals_match_independent_exhaustive_enumeration():
    rng = np.random.default_rng(614)
    for _ in range(25):
        rows = [
            candidate(i, p=float(rng.uniform(0.2, 0.95)), odds=float(rng.uniform(1.2, 4)))
            for i in range(7)
        ]
        expected = set()
        for n in range(2, 8):
            for subset in itertools.combinations(rows, n):
                if np.prod([c["probability"] * c["odds"] for c in subset]) > 1:
                    expected.add(tuple(sorted(c["candidate_id"] for c in subset)))
        actual = {
            tuple(sorted(c["candidate_id"] for c in a["legs"])) for a in mp.acca_proposals(rows)
        }
        assert actual == expected


def test_joint_solver_matches_independent_constrained_optimizer():
    rows = [
        candidate(2 * i + j, book=f"Book{i}", p=p**0.5, odds=1 / p)
        for i, p in enumerate((0.9, 0.6, 0.3))
        for j in range(2)
    ]
    proposals = mp.acca_proposals(rows)
    fractions, diag = mp.allocate_portfolio(proposals)
    ps = np.array([a["probability_estimate"] for a in proposals])
    odds = np.array([a["odds"] for a in proposals])
    edges = np.unique(np.r_[0.0, ps, 1.0])
    u = (edges[:-1] + edges[1:]) / 2
    returns = (u[:, None] < ps).astype(float) * odds - 1
    w = np.diff(edges)

    def utility(f):
        return float(w @ np.log(1 + returns @ f))

    reference = minimize(
        lambda f: -utility(f),
        np.zeros(len(ps)),
        method="SLSQP",
        bounds=[(0, 1 - 1e-9)] * len(ps),
        constraints=[{"type": "ineq", "fun": lambda f: 1 - 1e-9 - f.sum()}],
        options={"ftol": 1e-12, "maxiter": 1000},
    )
    assert reference.success
    full = np.array(fractions) / mp.KELLY_MULTIPLIER
    assert utility(full) == pytest.approx(-reference.fun, abs=2e-5)
    assert diag["duality_gap"] < 1e-4
    assert sum(fractions) <= mp.MAX_PAPER_EXPOSURE


def test_reusing_teams_across_accas_is_allowed_and_jointly_budgeted():
    rows = [
        candidate(i, p=p**0.5, odds=1 / p, book=f"B{k}")
        for k, p in enumerate((0.9, 0.3))
        for i in (2 * k, 2 * k + 1)
    ]
    rows[2]["fixture"][1] = rows[0]["fixture"][1]
    plan = mp.select_accas(rows)
    assert len(plan) == 2
    assert set(plan[0]["legs"][0]["fixture"][1:]) & set(plan[1]["legs"][0]["fixture"][1:])
    record = receipt(DAY, rows, plan)
    record["schema"] = mp.SCHEMA
    mp._validate_bets(record)
    assert sum(a["stake_units"] for a in plan) <= 25.0


def test_quarter_kelly_avoids_review_stress_full_kelly_overbet():
    a = mp.select_accas([candidate(1, p=0.8), candidate(2, p=0.8)])[0]
    assert a["model_kelly_fraction"] == pytest.approx(0.52)
    f = a["stake_fraction_of_free_bank"]
    assert f == pytest.approx(0.13, abs=1e-6)
    true_p = 0.65**2
    assert true_p * np.log1p(3 * f) + (1 - true_p) * np.log1p(-f) > 0
    assert true_p * np.log1p(3 * 0.52) + (1 - true_p) * np.log1p(-0.52) < 0


def test_invalid_json_draft_has_visible_missed_day_and_original_bytes(tmp_path):
    path = mp.state_path(tmp_path)
    path.write_bytes(b"{bad-json\x00")
    row = run_capture(tmp_path, {}, now=FREEZE)
    assert row["status"] == "missed_freeze_no_paper_bet"
    assert not row["accas"]
    saved = tmp_path / row["draft_integrity_error"]["quarantine"]
    assert saved.read_bytes() == path.read_bytes() == b"{bad-json\x00"
    assert mp.receipts(tmp_path) == [row]


def test_starvation_is_explicit_not_mislabeled_strategy_selectivity(tmp_path):
    rows = [pick(1), pick(2)]
    for row in rows:
        row["odds_captured_at"] = (FREEZE - timedelta(hours=6, seconds=1)).isoformat()
    blocked = run_capture(tmp_path, context(rows))
    assert blocked["coverage"]["candidate_count"] == 0
    assert blocked["coverage"]["status"] == "input_starved_not_strategy_selectivity"
    assert blocked["rejections"]["quote_or_probability_unavailable"] > 0
    # A controlled fresh batch exercises the SAME real admission path. This
    # proves plumbing, NOT actual provider coverage or historical opportunity.
    fresh = run_capture(tmp_path / "fresh", context([pick(1), pick(2)]))
    assert fresh["coverage"]["candidate_count"] == 2
    assert fresh["coverage"]["status"] == "inputs_available"
    assert fresh["accas"]


@pytest.fixture
def capture_module():
    spec = importlib.util.spec_from_file_location("ml_review_capture", "scripts/capture_theodds.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stale_quote_refresh_is_bounded_and_leaves_default_auto_unchanged(capture_module):
    mod = capture_module
    f = {"home": "Alpha", "away": "Bravo", "date": DAY}
    kickoff = FREEZE + timedelta(hours=5)
    rows = [
        dict(
            f,
            kickoff=kickoff.isoformat(),
            captured_at=(FREEZE - timedelta(hours=7)).isoformat(),
            bookmaker="Pinnacle",
        )
    ]
    attempts = {"Alpha|Bravo": {"first_at": rows[0]["captured_at"], "capture_scope": "same"}}
    kwargs = {
        "now": NOW,
        "kickoff_fn": lambda f: kickoff,
        "match_fn": lambda a, b: a == b,
        "requested_scope": "same",
    }
    assert not mod.plan_auto([f], rows, attempts, **kwargs)[0]
    due, updates, _ = mod.plan_auto([f], rows, attempts, ml_freeze=FREEZE, **kwargs)
    assert due == [f] and updates == {"Alpha|Bravo": "ml_pre_freeze_at"}
    mod.record_attempts(due, updates, attempts, [f], lambda a, b: a == b, "same", NOW.isoformat())
    assert not mod.plan_auto([f], rows, attempts, ml_freeze=FREEZE, **kwargs)[0]


@pytest.mark.parametrize(
    "case", ["fresh", "fail_cooldown", "close_fail_cooldown", "after", "early", "close"]
)
def test_refresh_does_not_repeat_or_bypass_time_and_failure_guards(capture_module, case):
    mod = capture_module
    kickoff = FREEZE + timedelta(hours=5)
    f = {"home": "Alpha", "away": "Bravo", "date": DAY}
    row = dict(
        f,
        kickoff=kickoff.isoformat(),
        captured_at=(FREEZE - timedelta(hours=7)).isoformat(),
        bookmaker="Pinnacle",
    )
    rec = {"first_at": row["captured_at"], "capture_scope": "same"}
    now = NOW
    if case == "fresh":
        row["captured_at"] = NOW.isoformat()
    if case == "fail_cooldown":
        rec["fail_at"] = NOW.isoformat()
    if case == "close_fail_cooldown":
        rec["close_fail_at"] = NOW.isoformat()
    if case == "after":
        now = FREEZE
    if case == "early":
        now = FREEZE - timedelta(hours=7)
    if case == "close":
        kickoff = FREEZE + timedelta(minutes=29)
        row["kickoff"] = kickoff.isoformat()
    _, updates, _ = mod.plan_auto(
        [f],
        [row],
        {"Alpha|Bravo": rec},
        now=now,
        kickoff_fn=lambda f: kickoff,
        match_fn=lambda a, b: a == b,
        requested_scope="same",
        ml_freeze=FREEZE,
    )
    assert "ml_pre_freeze_at" not in updates.values()


def test_final_card_is_consumed_before_future_planner_or_archive_restore(monkeypatch):
    spec = importlib.util.spec_from_file_location("ml_review_daily", "scripts/daily.py")
    daily = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(daily)
    events = []
    for name in (
        "capture_theodds_snapshot",
        "capture_oddspapi_snapshot",
        "capture_betexplorer_snapshot",
        "capture_card_enrich_snapshot",
    ):
        monkeypatch.setattr(daily, name, lambda *a, n=name, **kw: events.append(n))
    monkeypatch.setattr(daily, "run", lambda *a: events.append("final_card"))
    monkeypatch.setattr(daily, "run_ml_paper", lambda: events.append("ml_draft"))
    daily.finalize_priced_candidate_slate(DAY)
    assert events[-2:] == ["final_card", "ml_draft"]
    assert events[0] == "capture_theodds_snapshot"


def test_only_candidate_snapshot_can_request_ml_refresh(monkeypatch):
    spec = importlib.util.spec_from_file_location("ml_review_daily_flags", "scripts/daily.py")
    daily = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(daily)
    commands = []
    monkeypatch.setattr(daily, "run_soft", lambda cmd, *a: commands.append(cmd))
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "1")
    daily.capture_theodds_snapshot(DAY, "candidate_price_snapshot")
    daily.capture_theodds_snapshot(DAY, "end_of_run")
    monkeypatch.setenv("EDGE_FACTORY_ML_PAPER", "0")
    daily.capture_theodds_snapshot(DAY, "candidate_price_snapshot")
    assert "--ml-precutoff" in commands[0]
    assert all("--ml-precutoff" not in cmd for cmd in commands[1:])


def test_betexplorer_all_double_chance_sides_with_real_receipt_path(tmp_path, monkeypatch):
    from datetime import datetime

    from test_betexplorer_board_admission import ALL_BE_MARKETS, board_only
    from test_enh_pricing import BE_DAY, _be_pick

    from edgefactory.enh_pricing import _betexplorer_asof_index, load_prices_index
    from edgefactory.util import norm_team

    monkeypatch.setenv("EDGE_FACTORY_ENH_BOARD", "1")
    _, fixture = board_only(tmp_path, markets=ALL_BE_MARKETS)
    row = _be_pick("double_chance", pick="home")
    row.update(league=fixture["league"], contract_id="review-fixture")
    row["kickoff_utc"] = f"{BE_DAY}T20:00:00Z"
    now = datetime.fromisoformat(row["as_of"])
    kickoff = at.parse_kickoff_proven(row)
    index = _betexplorer_asof_index(load_prices_index(tmp_path, BE_DAY), now)
    pair = (norm_team(row["home"]), norm_team(row["away"]))
    for side in ("1x", "12", "x2"):
        quotes = index["fixture_quotes"][pair][("dc", side)]
        quote = next(q for q in quotes if q[3] == "betexplorer")
        assert mp._quote_ok(
            row,
            mp._quote(*quote[:6]),
            now,
            kickoff,
            at.execution_source_rejection,
            1.0,
            market="double_chance",
            selection=side,
        )


def test_calibration_counts_unbet_candidates_and_deduplicates_reused_legs():
    rows = [candidate(i) for i in range(3)]
    rows[0]["base_probability"] = 0.9
    rows[0]["probability"] = 0.7
    accas = [
        {"legs": rows[:2], "odds": 4.0, "stake_units": 1.0},
        {"legs": [rows[0], rows[2]], "odds": 4.0, "stake_units": 1.0},
    ]
    unbet = candidate(4)
    r = receipt(DAY, [*rows, unbet], accas)
    result = mp.performance([r], lambda c: (2, 0))
    assert result["resolved_result_legs"] == 3
    assert result["calibration"]["all_candidates"]["resolved_fixtures"] == 4
    assert result["calibration"]["selected_candidates"]["resolved_fixtures"] == 3
    assert result["calibration"]["all_candidates"]["base_logloss"] is not None


def test_search_budget_is_explicit_and_does_not_create_an_implicit_stake(tmp_path, monkeypatch):
    monkeypatch.setattr(mp, "SEARCH_NODE_BUDGET", 5)
    diag = {}
    plan = mp.select_accas([candidate(i) for i in range(40)], diagnostics=diag)
    assert diag["search_work"]["budget_exhausted"]
    assert diag["search_work"]["node_expansions"] == 5
    assert not plan  # no positive acca was reached; no forced paper bet


def test_committed_morning_archive_has_a_genuine_pre_cutoff_opportunity():
    """Feasibility only: no outcome read, no plan/backfill, no ROI measurement.

    This fixed real example also guards against confusing 12 bookmaker/market
    quotes with 12 independent fixtures. Most other recent days are starved.
    """
    import json
    from datetime import datetime
    from pathlib import Path

    from edgefactory.enh_pricing import load_prices_index

    root = Path(__file__).resolve().parents[1]
    day = "2026-10-29"
    rows = json.loads((root / "localdata" / f"picks_morning_{day}.json").read_text())
    now = datetime.fromisoformat(day + "T06:00:00Z")
    freeze = datetime.fromisoformat(day + "T09:00:00+02:00")
    cs, _, _ = mp.candidates(
        rows,
        day,
        now,
        load_prices_index(root, day),
        kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection,
        min_leg_odds=1.0,
        freeze_at=freeze,
    )
    assert cs
    assert len({tuple(c["fixture"]) for c in cs}) >= 2
    assert all(datetime.fromisoformat(c["price_at"]) <= now for c in cs)
    assert all(freeze - datetime.fromisoformat(c["price_at"]) <= timedelta(hours=6) for c in cs)


@pytest.mark.parametrize("tamper_quarantine", [False, True])
def test_damaged_draft_restore_requires_acknowledged_missed_day_and_exact_bytes(
    tmp_path, tamper_quarantine
):
    from test_ml_paper_redteam import _persistence_module, _seed_repo

    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    local = repo / "localdata"
    path = mp.state_path(local)
    path.write_bytes(b"{damaged-draft")
    sealed = run_capture(local, {}, now=FREEZE)
    if tamper_quarantine:
        (local / sealed["draft_integrity_error"]["quarantine"]).write_bytes(b"not-original")
    _persistence_module().restore_committed_localdata(repo)
    marker = local / "autobets_ML_integrity_block.json"
    assert path.read_bytes() == b"{damaged-draft"
    if tamper_quarantine:
        assert marker.exists()
        with pytest.raises(ValueError, match="paper lane blocked"):
            mp.receipts(local)
    else:
        assert not marker.exists()
        assert mp.receipts(local) == [sealed]


def test_ambiguous_result_calendar_cannot_create_never_settling_new_positions(tmp_path):
    rows = [pick(1), pick(2)]
    for row in rows:
        row["kickoff_utc"] = DAY + "T22:30:00Z"
    draft = run_capture(tmp_path, context(rows))
    assert not draft["candidates"] and not draft["accas"]
    assert draft["rejections"]["settlement_calendar_ambiguous"] == 2
