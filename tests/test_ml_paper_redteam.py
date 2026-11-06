"""Adversarial paper-only accounting, quote, learning and runner-restore checks."""

import json
from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from test_ml_paper import DAY, FREEZE, NOW, candidate, capture, context, pick, receipt, run_capture
from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp
from edgefactory.consensus_contracts import enhancement_fixture_identity
from edgefactory.enh_pricing import load_prices_index


def sign(row):
    row = deepcopy(row)
    row["sha256"] = mp.digest({k: v for k, v in row.items() if k != "sha256"})
    return row


def save(root, row, draft=False):
    path = mp.state_path(root) if draft else mp.receipt_path(root, row["date"])
    path.parent.mkdir(parents=True, exist_ok=True)
    if draft:
        state = mp._read_state(root)
        state["pending_by_date"][row["date"]] = sign(row)
        mp._save_state(root, state)
    else:
        path.write_text(json.dumps(sign(row)))
    return path


def test_empty_acca_cannot_mint_paper_profit():
    r = receipt(DAY, [], [{"legs": [], "odds": 400.0, "stake_units": 100.0}])
    with pytest.raises(ValueError, match="fewer than two legs"):
        mp.performance([r], lambda c: None)


@pytest.mark.parametrize(
    "damage", ["price_product", "same_team", "overbudget", "mixed_book", "unselected", "nan_stake"]
)
def test_rehashed_but_internally_invalid_receipts_still_fail_closed(tmp_path, damage):
    r = capture(tmp_path)
    a = r["accas"][0]
    if damage == "price_product":
        a["odds"] *= 100
    elif damage == "same_team":
        a["legs"][1]["fixture"] = a["legs"][0]["fixture"]
    elif damage == "overbudget":
        a["stake_units"] = 101.0
    elif damage == "mixed_book":
        a["legs"][1]["book"] = "Different book"
    elif damage == "unselected":
        r["candidates"] = []
    else:
        # NaN is rejected at serialization/checksum, never turned into a bank.
        a["stake_units"] = float("nan")
        with pytest.raises(ValueError):
            sign(r)
        return
    save(tmp_path, r)
    with pytest.raises(ValueError):
        mp.receipts(tmp_path)


def test_rehashed_late_selection_is_not_a_valid_frozen_receipt(tmp_path):
    r = capture(tmp_path)
    r["captured_at"] = (FREEZE + timedelta(hours=2)).isoformat()
    r["draft_persisted_at"] = r["captured_at"]
    save(tmp_path, r)
    with pytest.raises(ValueError, match="pre-cutoff"):
        mp.receipts(tmp_path)


def test_partial_day_known_losses_cannot_disappear_from_drawdown():
    cs = [candidate(i) for i in range(6)]
    prior = receipt(
        "2026-11-01",
        cs[:4],
        [
            {"legs": cs[:2], "odds": 4.0, "stake_units": 40.0},
            {"legs": cs[2:4], "odds": 4.0, "stake_units": 1.0},
        ],
    )
    today = receipt(DAY, cs[4:], [{"legs": cs[4:], "odds": 4.0, "stake_units": 10.0}])

    def scores(c):
        i = int(c["candidate_id"])
        return (0, 1) if i == 0 else (2, 0) if i >= 4 else None

    r = mp.performance([prior, today], scores)
    assert r["paper_bank_units"] == 90.0
    assert r["paper_free_units"] == 89.0 and r["paper_committed_units"] == 1.0
    assert r["max_daily_close_drawdown_units"] == 40.0
    assert r["max_daily_close_drawdown_fraction"] == 0.4
    assert r["drawdown_has_pending_results"]
    assert "not_settlement_timeline" in r["drawdown_basis"]


def test_learning_saves_outcomes_needed_to_reproduce_the_frozen_fit():
    cs = [candidate(i, date="2026-11-01") for i in range(40)]
    r = receipt("2026-11-01", cs)
    learner = mp.learn([r], NOW, lambda c: (2, 0) if int(c["candidate_id"]) % 2 else (0, 1))
    assert len(learner["training_outcomes"]) == 40
    assert learner["training_outcomes_sha256"] == mp.digest(learner["training_outcomes"])
    outcomes = {e["candidate_id"]: tuple(e["score"]) for e in learner["training_outcomes"]}
    replay = mp.learn([r], NOW, lambda c: outcomes[c["candidate_id"]])
    assert replay == learner


def quote(row, price, minutes):
    return {
        "home": row["home"],
        "away": row["away"],
        "market": "1x2",
        "selection": "home",
        "odds": price,
        "bookmaker": "Pinnacle",
        "source": "pinnapi_odds",
        "captured_at": (NOW - timedelta(minutes=minutes)).isoformat(),
        "kickoff": row["kickoff_utc"],
    }


@pytest.mark.parametrize("reverse", [False, True])
def test_same_book_uses_latest_quote_not_first_or_largest_stale_price(tmp_path, reverse):
    rows = [pick(1), pick(2)]
    for r in rows:
        # Primary at -10 minutes must lose to a fresher board at -1.
        qs = [quote(r, 3.0, 5), quote(r, 1.9, 1)]
        r["price_board"] = list(reversed(qs)) if reverse else qs
    r = capture(tmp_path, rows)
    assert r["candidates"] and {c["odds"] for c in r["candidates"]} == {1.9}


def test_same_time_same_book_price_conflict_is_not_cherry_picked(tmp_path):
    rows = [pick(1), pick(2)]
    for r in rows:
        r["price_board"] = [quote(r, 3.0, 10)]
    r = capture(tmp_path, rows)
    assert not r["candidates"] and not r["accas"]
    assert r["rejections"]["same_time_same_book_price_conflict"] == 2


def test_a_later_unambiguous_quote_can_resolve_an_older_price_conflict(tmp_path):
    rows = [pick(1), pick(2)]
    for r in rows:
        r["price_board"] = [quote(r, 3.0, 10), quote(r, 1.9, 1)]
    r = capture(tmp_path, rows)
    assert {c["odds"] for c in r["candidates"]} == {1.9}


def test_double_chance_uses_its_actual_supported_side_not_parent_pick(tmp_path):
    rows = [pick(1), pick(2)]
    index = {"fixture_quotes": {}}
    from edgefactory.util import norm_team

    for r in rows:
        q = (
            2.0,
            "Pinnacle",
            r["odds_captured_at"],
            "pinnapi_odds",
            r["kickoff_utc"],
            None,
            (r["home"], r["away"]),
        )
        index["fixture_quotes"][(norm_team(r["home"]), norm_team(r["away"]))] = {
            ("dc", "1x"): [q],
            ("dc", "x2"): [q],
            ("dc", "12"): [q],
        }
    r = capture(tmp_path, rows, index=index)
    dc = {c["selection"]: c for c in r["candidates"] if c["market"] == "double_chance"}
    assert set(dc) == {"1x", "x2", "12"}
    assert dc["1x"]["base_probability"] == pytest.approx(0.8)
    assert dc["x2"]["base_probability"] == pytest.approx(0.3)
    assert dc["12"]["base_probability"] == pytest.approx(0.9)
    assert mp.hit("double_chance", "12", 0, 0) is False
    assert mp.hit("double_chance", "x2", 0, 1) is True


def test_real_betexplorer_predecision_path_can_supply_non_parent_markets(tmp_path, monkeypatch):
    monkeypatch.setenv("EDGE_FACTORY_ENH_BOARD", "1")
    from test_betexplorer_board_admission import board_only
    from test_enh_pricing import BE_DAY, _be_pick

    _, fixture = board_only(tmp_path)
    row = _be_pick("match_over_25")
    model_row = pick()
    row.update(
        statistical_profile=deepcopy(model_row["statistical_profile"]), avg_p=75.0, bucket="CAUTION"
    )
    # Bind the actual fixture/day/contract, not a borrowed model input receipt.
    row["contract_id"] = model_row["contract_id"]
    row["pick"] = "home"
    row["league"] = fixture["league"]
    row["kickoff_utc"] = f"{BE_DAY}T20:00:00Z"
    row["as_of"] = f"{BE_DAY}T06:30:00Z"
    profile = row["statistical_profile"]
    model = profile["ml_model"]
    model.update(as_of_exclusive=BE_DAY, train_last_date="2026-10-11")
    import hashlib

    model["model_key"] = hashlib.sha256(
        json.dumps(
            {k: v for k, v in model.items() if k != "model_key"}, sort_keys=True, allow_nan=False
        ).encode()
    ).hexdigest()
    profile["as_of_exclusive"] = BE_DAY
    profile["ml_inputs"].update(
        fixture=enhancement_fixture_identity(row), model_key=model["model_key"]
    )
    now = datetime.fromisoformat(row["as_of"])
    cs, _, rejected = mp.candidates(
        [row],
        BE_DAY,
        now,
        load_prices_index(tmp_path, BE_DAY),
        kickoff_fn=at.parse_kickoff_proven,
        source_guard=at.execution_source_rejection,
        min_leg_odds=1.0,
        freeze_at=datetime.fromisoformat(f"{BE_DAY}T09:00:00+02:00"),
    )
    assert any(c["market"] == "btts_no" and c["price_source"] == "betexplorer" for c in cs), (
        rejected
    )
    assert all(c["price_provenance"]["selection"] == "no" for c in cs if c["market"] == "btts_no")
    assert fixture["home"] == row["home"]


def test_untracked_paper_draft_and_freeze_survive_real_runner_cache_clean(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    local = repo / "localdata"
    r = capture(local)
    path = mp.receipt_path(local, DAY)
    frozen_bytes = path.read_bytes()
    draft_bytes = mp.state_path(local).read_bytes()
    _persistence_module().restore_committed_localdata(repo)
    assert path.read_bytes() == frozen_bytes
    assert mp.state_path(local).read_bytes() == draft_bytes
    assert mp.receipts(local) == [r]


def test_newer_valid_cached_draft_survives_tracked_head_restore(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    local = repo / "localdata"
    run_capture(local, context([pick(1), pick(2)]))
    path = mp.state_path(local)
    _git(repo, "add", str(path.relative_to(repo)))
    _git(repo, "commit", "-qm", "paper morning draft")
    later = NOW + timedelta(minutes=20)
    run_capture(local, dict(context([pick(3), pick(4)]), build_at=later.isoformat()), now=later)
    expected = path.read_bytes()
    _persistence_module().restore_committed_localdata(repo)
    assert path.read_bytes() == expected
    assert run_capture(local, {}, now=FREEZE)["accas"] == json.loads(expected)["pending_by_date"][DAY]["accas"]


def test_divergent_frozen_cache_is_preserved_blocks_only_paper_and_never_replaces_head(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    local = repo / "localdata"
    capture(local)
    path = mp.receipt_path(local, DAY)
    committed = path.read_bytes()
    _git(repo, "add", str(path.relative_to(repo)))
    _git(repo, "commit", "-qm", "paper frozen")
    changed = json.loads(committed)
    changed["accas"][0]["stake_units"] /= 2
    save(local, changed)
    cached = path.read_bytes()
    ordinary = local / "edges_consensus.json"
    original = ordinary.read_bytes()
    ordinary.write_text('{"dirty":true}')
    _persistence_module().restore_committed_localdata(repo)
    assert path.read_bytes() == committed
    assert ordinary.read_bytes() == original  # ordinary/live restore still proceeds
    assert (local / "autobets_ML_integrity_block.json").exists()
    assert any(p.read_bytes() == cached for p in (local / "autobets_ML_conflicts").glob("*.json"))
    with pytest.raises(ValueError, match="paper lane blocked"):
        mp.receipts(local)
    with pytest.raises(ValueError, match="paper lane blocked"):
        run_capture(local, {}, now=FREEZE)
    # A later restore must not silently clear the review block or evidence.
    marker = (local / "autobets_ML_integrity_block.json").read_bytes()
    _persistence_module().restore_committed_localdata(repo)
    assert (local / "autobets_ML_integrity_block.json").read_bytes() == marker


def test_selected_leg_cannot_diverge_from_retained_candidate_evidence(tmp_path):
    r = capture(tmp_path)
    a = r["accas"][0]
    a["legs"][0]["probability"] = 0.999
    save(tmp_path, r)
    with pytest.raises(ValueError, match="invalid or repeated"):
        mp.receipts(tmp_path)


def test_malformed_one_row_model_cannot_disable_other_valid_fixtures(tmp_path):
    bad = pick(3)
    bad["statistical_profile"]["ml_inputs"]["sources"] = None
    r = capture(tmp_path, [pick(1), bad, pick(2), None])
    assert r["accas"] and len(r["candidates"]) == 2
    assert r["rejections"]["fixture_bound_source_inputs_unavailable"] == 2


@pytest.mark.parametrize("future", [False, True])
def test_known_same_pair_different_kickoffs_are_ambiguous_but_future_rows_cannot_veto(
    tmp_path, future
):
    original = pick(1)
    changed = deepcopy(original)
    changed["kickoff_utc"] = (NOW + timedelta(hours=5)).isoformat()
    changed["statistical_profile"]["ml_inputs"]["fixture"] = enhancement_fixture_identity(changed)
    if future:
        changed["as_of"] = (NOW + timedelta(seconds=1)).isoformat()
    r = capture(tmp_path, [original, changed, pick(2)])
    assert bool(r["accas"]) is future
    assert r["rejections"].get("fixture_schedule_conflict", 0) == (0 if future else 1)


def test_corrupt_previous_block_marker_cannot_abort_live_restore_or_erase_evidence(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    local = repo / "localdata"
    capture(local)
    path = mp.receipt_path(local, DAY)
    path.write_text('{"corrupt":true}')
    marker = local / "autobets_ML_integrity_block.json"
    marker.write_text("BROKEN MARKER")
    _persistence_module().restore_committed_localdata(repo)
    assert json.loads(marker.read_text())["status"] == "blocked_pending_evidence_review"
    assert any(
        p.read_text() == "BROKEN MARKER" for p in (local / "autobets_ML_conflicts").glob("*.json")
    )
    with pytest.raises(ValueError, match="paper lane blocked"):
        mp.receipts(local)


def test_book_replication_cannot_reweight_calibration_towards_one_market():
    cs = []
    for i in range(40):
        home = candidate(i, date="2026-11-01")
        home["ml_inputs"]["values"]["forecast_btts_yes_mean"] = .6
        btts = dict(home, candidate_id=f"btts{i}", market="btts_no", selection="no")
        cs.extend([home, btts])
    original = mp.learn([receipt("2026-11-01", cs)], NOW, lambda c: (2, 1))
    duplicates = [
        dict(c, book=f"Book{j}", candidate_id=f"quote-{j}-{c['candidate_id']}")
        for c in cs
        if c["market"] == "1x2"
        for j in range(20)
    ]
    replicated = mp.learn([receipt("2026-11-01", cs + duplicates)], NOW, lambda c: (2, 1))
    assert original["status"] == "fitted_source_market_temperature"
    assert replicated == original
    assert replicated["observations"] == 80 and replicated["fixtures"] == 40
