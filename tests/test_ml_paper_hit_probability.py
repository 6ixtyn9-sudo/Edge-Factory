"""Operator-approved chance-first PAPER selection and pre-kickoff replacement.

Synthetic fixtures exercise real learning, evidence, publication and accounting.
A higher hit estimate is not a claim of profitability or calibration.
"""

import itertools
import math
import random
from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from test_ml_paper import candidate, receipt
from test_ml_paper_admission import history, score
from test_ml_paper_rolling import run, slate

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp

OBJECTIVE = "highest_ticket_hit_probability_v1"
NOW = datetime(2026, 11, 13, 8, tzinfo=UTC)
DAY = "2026-11-13"


def supported(i, *, p=.9, odds=1.1, book="Book", lower=None):
    c = candidate(i, date=DAY, p=p, odds=odds, book=book)
    lower = p - .05 if lower is None else lower
    c["admission"] = {
        "policy": mp.ADMISSION_POLICY,
        "status": "eligible" if lower * odds > 1 else "abstain",
        "reason": "positive_conservative_edge" if lower * odds > 1 else "edge_not_supported",
        "fixtures": 74, "wins": 60, "probability_lower": lower,
        "joint_basis": "independent_leg_admission_lower_envelope",
    }
    return c


def choose(rows, *, bank=100., prior=None, available=None):
    diagnostics = {}
    plan = mp.select_accas(
        rows, bank if available is None else available, objective=OBJECTIVE,
        diagnostics=diagnostics,
        concentration={"total_bank_units": bank, "prior_open_fixture_micro_units": prior or {}},
    )
    return plan, diagnostics


def signature(a):
    return tuple(sorted(c["candidate_id"] for c in a["legs"]))


def test_hit_probability_beats_draw_lottery_even_when_favourites_have_negative_ev():
    rows = [supported(1, p=.95, odds=1.03), supported(2, p=.90, odds=1.05),
            supported(3, p=.209, odds=6.75, lower=.197),
            supported(4, p=.211, odds=5.3, lower=.197)]
    before = deepcopy(rows)
    plan, diagnostics = choose(rows)
    assert len(plan) == 1 and signature(plan[0]) == ("1", "2")
    assert len(plan[0]["legs"]) == 2
    assert plan[0]["probability_estimate"] == pytest.approx(.855)
    assert plan[0]["estimated_ev"] < 0  # price/value is NOT the selection gate
    assert plan[0]["stake_units"] == .1  # small flat PAPER risk, not Kelly/chasing payout
    assert diagnostics["selection_objective"] == OBJECTIVE
    assert rows == before


def test_no_extra_legs_or_weaker_extra_cards_to_manufacture_more_payout():
    rows = [supported(i, p=.99 - i / 1000, odds=10.) for i in range(1, 9)]
    plan, _ = choose(rows)
    assert len(plan) == 1 and signature(plan[0]) == ("1", "2")
    assert plan[0]["probability_estimate"] > math.prod(c["probability"] for c in rows)


def test_probability_precedes_price_and_price_only_breaks_exact_probability_ties():
    rows = [supported(1, p=.95, odds=1.01, book="Low payout"),
            supported(2, p=.95, odds=1.01, book="Low payout"),
            supported(3, p=.8, odds=100., book="Jackpot"),
            supported(4, p=.8, odds=100., book="Jackpot")]
    assert signature(choose(rows)[0][0]) == ("1", "2")
    rows[2]["probability"] = rows[3]["probability"] = .95
    assert signature(choose(rows)[0][0]) == ("3", "4")


def test_same_book_and_no_shared_team_still_apply():
    a, b, c = supported(1, p=.99), supported(2, p=.98), supported(3, p=.6)
    b["fixture"][1] = a["fixture"][1]
    plan, _ = choose([a, b, c, supported(4, p=.999, book="Other")])
    assert signature(plan[0]) == ("1", "3")
    assert not choose([a, supported(5, book="Other")])[0]


def test_exact_pair_search_matches_exhaustive_oracle_and_is_order_independent():
    rng = random.Random(1311)
    for _ in range(12):
        rows = [supported(i, p=rng.uniform(.2, .99), odds=rng.uniform(1.01, 12.),
                          book="A" if i % 3 else "B", lower=.1) for i in range(12)]
        rows[4]["fixture"][1] = rows[2]["fixture"][1]
        pairs = [pair for pair in itertools.combinations(rows, 2)
                 if pair[0]["book"] == pair[1]["book"]
                 and not set(pair[0]["fixture"][1:]) & set(pair[1]["fixture"][1:])]
        best = min(pairs, key=lambda pair: (
            -math.prod(c["probability"] for c in pair), -math.prod(c["odds"] for c in pair),
            tuple(sorted(c["candidate_id"] for c in pair))))
        expected = tuple(sorted(c["candidate_id"] for c in best))
        for _ in range(3):
            rng.shuffle(rows)
            assert signature(choose(rows)[0][0]) == expected


def test_missing_evidence_is_not_rescued_by_high_probability():
    a, b, unsupported = supported(1, p=.8), supported(2, p=.7), supported(3, p=.999)
    unsupported["admission"].update(fixtures=0, probability_lower=0., reason="no_local_evidence")
    assert signature(choose([a, b, unsupported])[0][0]) == ("1", "2")
    assert not choose([unsupported, a])[0]


def test_flat_paper_stakes_keep_fixture_and_aggregate_headroom_and_no_refill():
    rows = [supported(1), supported(2), supported(3, p=.8)]
    prior = {tuple(rows[0]["fixture"]): 4_990_000}
    plan, _ = choose(rows, prior=prior)
    assert plan[0]["stake_units"] == .01
    assert signature(plan[0]) == ("1", "2")  # do not refill a capped stake elsewhere
    plan, _ = choose(rows, bank=20.)
    assert plan[0]["stake_units"] == .02
    assert not choose(rows, available=0.)[0]
    assert not choose(rows, bank=.0001)[0]  # never round tiny stakes up


def warm(root):
    r = deepcopy(history(n=20)[0])
    # Retain actual synthetic quotes in BOTH price bands. No unquoted
    # favourite is manufactured from the training fixtures' 2.0 prices.
    r["candidates"] += [dict(c, candidate_id="short-price-" + c["candidate_id"],
                             book="Short Quote Book", odds=1.05)
                        for c in r["candidates"]]
    r["sha256"] = mp.digest(r)
    assert mp._write_once(mp.receipt_path(root, r["date"]), r)
    return r


def new_slate(now=NOW, ids=(1, 2, 3)):
    rows = slate(now, ids=ids)
    for row, p in zip(rows, (.95, .90, .2)):
        row["odds"] = 1.01 if p > .8 else 8.
        values = row["statistical_profile"]["ml_inputs"]["values"]
        values.update(forecast_1x2_home_mean=p, forecast_1x2_draw_mean=(1-p)/3,
                      forecast_1x2_away_mean=(1-p)*2/3)
    return rows


def test_new_rolling_publication_replays_policy_and_publishes_joint_hit_and_miss(tmp_path):
    warm(tmp_path)
    row = run(tmp_path, NOW, new_slate(), lookup=score)
    assert row["accas"] and row["policy"]["selection_objective"] == OBJECTIVE
    assert len(row["accas"]) == 1 and len(row["accas"][0]["legs"]) == 2
    assert row["accas"][0]["estimated_ev"] < 0
    assert row["accas"][0]["stake_units"] == .1
    assert mp.receipts(tmp_path)[-1] == row
    before = deepcopy(row)
    text = mp.render_daily_card([row])
    assert "Chance-first" in text and "estimated hit" in text and "estimated miss" in text
    assert "independence assumed; not calibrated or guaranteed" in text
    assert row == before


@pytest.mark.parametrize("damage", ["objective", "probability", "stake", "legs"])
def test_rehashed_new_receipt_cannot_forge_chance_first_policy(tmp_path, damage):
    warm(tmp_path)
    row = run(tmp_path, NOW, new_slate(), lookup=score)
    bad = deepcopy(row)
    if damage == "objective":
        del bad["policy"]["selection_objective"]
    elif damage == "probability":
        bad["accas"][0]["probability_estimate"] = .999
    elif damage == "stake":
        bad["accas"][0]["stake_units"] = 1.
    else:
        bad["accas"][0]["selection_objective"] = "jackpot"
    bad["sha256"] = mp.digest({k: v for k, v in bad.items() if k != "sha256"})
    with pytest.raises(ValueError):
        mp.validate_record(bad, DAY)


def old_ticket(root):
    legs = [candidate(i, date=DAY, p=.21, odds=6.75 if i == 80 else 5.3) for i in (80, 81)]
    r = receipt(DAY, legs, [{"legs": legs, "odds": 35.775, "stake_units": .097512,
                              "book": "Pinnacle"}])
    r["sha256"] = mp.digest(r)
    assert mp._write_once(mp.receipt_path(root, DAY), r)
    return r


def replace(root, old, *, now=NOW, rows=None, lookup=score, index=1):
    return mp.capture_rolling(
        {"build_at": now.isoformat(), "slate": new_slate(now) if rows is None else rows},
        root=root, score_lookup=lookup,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection,
        index={}, now=now,
        supersede=[{"receipt_sha256": old["sha256"], "acca_index": index}],
        replacement_reason="Operator requested highest chance of landing instead of growth.",
    )


def test_explicit_pre_kickoff_replacement_changes_current_slip_and_releases_old_stake(tmp_path):
    warm(tmp_path)
    old = old_ticket(tmp_path)
    original = mp.receipt_path(tmp_path, DAY).read_bytes()
    row = replace(tmp_path, old)
    assert row["accas"] and row["supersession"]["targets"][0]["receipt_sha256"] == old["sha256"]
    assert row["paper_pending_reserved_at_decision"] == 0
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == original
    history_rows = mp.receipts(tmp_path)
    result = mp.performance(history_rows, score)
    assert result["paper_committed_units"] == .1
    assert result["pending_accas"] == 1 and result["superseded_accas"] == 1
    assert result["settled_accas"] == 0 and result["profit_units"] == 0
    daily = [r for r in history_rows if r["date"] == DAY]
    text = mp.render_daily_card(daily, result)
    active, audit_note = text.split("SUPERSEDED BEFORE KICKOFF", 1)
    assert "@35.775" not in active and "@35.775" in audit_note
    assert "0.097512" in audit_note and "not a win or loss" in audit_note
    mp.publish(tmp_path, score)
    assert (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text() == text
    assert mp.receipt_path(tmp_path, DAY).read_bytes() == original


def test_replacement_is_not_reversible_and_never_drops_old_losses_from_bank(tmp_path):
    warm(tmp_path)
    old = old_ticket(tmp_path)
    row = replace(tmp_path, old)
    before = {p: p.read_bytes() for p in mp.receipt_files(tmp_path)}
    with pytest.raises(ValueError, match="already superseded"):
        replace(tmp_path, old, now=NOW + timedelta(minutes=1))
    assert all(p.read_bytes() == blob for p, blob in before.items())
    # Later scores must not turn a pre-kickoff withdrawn ticket into P&L.
    result = mp.performance(mp.receipts(tmp_path), lambda c: (0, 2))
    assert result["losses"] == 1 and result["profit_units"] == -.1
    assert row["accas"][0]["stake_units"] == .1


@pytest.mark.parametrize("damage", ["started", "known_result", "missing_reference", "malformed_hash", "bad_index"])
def test_replacement_refuses_started_resolved_or_unknown_positions_atomically(tmp_path, damage):
    warm(tmp_path)
    old = old_ticket(tmp_path)
    before = {p: p.read_bytes() for p in mp.receipt_files(tmp_path)}
    at = NOW
    lookup = score
    if damage == "started":
        at = datetime.fromisoformat(old["accas"][0]["legs"][0]["kickoff_utc"])
    elif damage == "known_result":
        lookup = lambda c: (0, 2) if c["date"] == DAY else score(c)
    elif damage == "missing_reference":
        old = dict(old, sha256="f" * 64)
    elif damage == "malformed_hash":
        old = dict(old, sha256="not-a-hash")
    with pytest.raises(ValueError):
        replace(tmp_path, old, now=at, lookup=lookup, index=2 if damage == "bad_index" else 1)
    assert {p: p.read_bytes() for p in mp.receipt_files(tmp_path)} == before


def test_no_fresh_qualifying_replacement_means_withdrawn_not_fabricated_ticket(tmp_path):
    warm(tmp_path)
    old = old_ticket(tmp_path)
    row = replace(tmp_path, old, rows=[])
    assert not row["accas"] and row["supersession"]
    result = mp.performance(mp.receipts(tmp_path), score)
    assert result["paper_committed_units"] == 0 and result["pending_accas"] == 0
    assert result["superseded_accas"] == 1 and result["profit_units"] == 0
    assert "SUPERSEDED BEFORE KICKOFF" in mp.render_daily_card([old, row], result)


def test_replacement_preserves_existing_settled_loss_in_bank_and_history(tmp_path):
    warm(tmp_path)
    legs = [candidate(i, date="2026-11-07") for i in (90, 91)]
    loss = receipt("2026-11-07", legs, [{"legs": legs, "odds": 4., "stake_units": 3.}])
    loss["sha256"] = mp.digest(loss)
    mp._write_once(mp.receipt_path(tmp_path, loss["date"]), loss)
    old = old_ticket(tmp_path)
    lookup = lambda c: (0, 2) if c["date"] == loss["date"] else score(c)
    row = replace(tmp_path, old, lookup=lookup)
    result = mp.performance(mp.receipts(tmp_path), lookup)
    assert result["losses"] == 1 and result["profit_units"] == -3.
    assert result["paper_bank_units"] == 97.
    assert result["paper_committed_units"] == row["accas"][0]["stake_units"] == .097
    assert result["bet_days"] == 2 and result["superseded_accas"] == 1
    assert mp.receipt_path(tmp_path, loss["date"]).read_text() == json_dump(loss)


def json_dump(row):
    import json
    return json.dumps(row, sort_keys=True, allow_nan=False)


def test_concurrent_replacement_can_release_reservation_only_once(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    warm(tmp_path)
    old = old_ticket(tmp_path)

    def attempt(_):
        try:
            return replace(tmp_path, old)
        except ValueError as exc:
            assert "already superseded" in str(exc)
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sum(r is not None for r in results) == 1
    result = mp.performance(mp.receipts(tmp_path), score)
    assert result["paper_committed_units"] == .1 and result["superseded_accas"] == 1


@pytest.mark.parametrize("field,bad", [
    ("probability", True), ("probability", float("nan")), ("probability", 1.),
    ("odds", float("inf")), ("odds", True), ("odds", 1.), ("book", " "),
])
def test_bad_numbers_or_missing_book_are_not_rescued_by_chance_objective(field, bad):
    a, b = supported(1), supported(2)
    a[field] = bad
    assert not choose([a, b])[0]


def test_new_production_writer_requires_policy_even_for_a_stripped_empty_decision(tmp_path):
    warm(tmp_path)
    row = run(tmp_path, NOW, new_slate(), lookup=score)
    bad = deepcopy(row)
    bad.update(accas=[], status="no_paper_bet", search={})
    bad["policy"].pop("selection_objective")
    # Rebuild the empty concentration audit so this specifically exercises
    # the independent writer's objective check, not a mismatched stake total.
    _, bad["fixture_concentration"] = mp.project_fixture_stakes([], total_bank_units=100.)
    bad["sha256"] = mp.digest({k: v for k, v in bad.items() if k != "sha256"})
    with pytest.raises(ValueError, match="chance-first"):
        mp._publish_receipt(tmp_path / "not-published.json", bad)
    assert not (tmp_path / "not-published.json").exists()


def test_replacement_cli_uses_existing_source_bytes_without_retimestamps(tmp_path):
    from scripts.replace_ml_paper_ticket import load_existing_slate
    with pytest.raises(ValueError, match="no existing"):
        load_existing_slate(tmp_path)
    rows = new_slate()
    path = tmp_path / "picks_today.json"
    path.write_text(json_dump(rows))
    before = path.read_bytes()
    assert load_existing_slate(tmp_path) == rows
    assert path.read_bytes() == before
    path.write_text("{}")
    with pytest.raises(TypeError, match="forecast slate"):
        load_existing_slate(tmp_path)


def test_replacement_cli_prints_already_published_card_without_reloading_history(tmp_path, monkeypatch, capsys):
    from scripts import replace_ml_paper_ticket as cli
    root = tmp_path / "localdata"
    root.mkdir()
    (root / "picks_today.json").write_text("[]")
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli.at, "load_settled_scores", dict)
    monkeypatch.setattr(cli.at, "ml_paper_score_lookup", lambda _: lambda c: None)
    monkeypatch.setattr(cli.ml_paper, "capture_rolling", lambda *a, **kw: {"date": DAY})

    def publish(root, _):
        (root / f"{mp.PREFIX}_{DAY}.txt").write_text("Already published chance-first card\n")
        return {}

    def forbidden(*args, **kwargs):
        raise AssertionError("CLI must not reload the full frozen history after publish")

    monkeypatch.setattr(cli.ml_paper, "publish", publish)
    monkeypatch.setattr(cli.ml_paper, "render_latest_card", forbidden)
    assert cli.main(["--receipt-sha256", "a" * 64, "--acca-index", "1", "--reason", "test"]) == 0
    assert "Already published chance-first card" in capsys.readouterr().out


def test_current_daily_missing_draft_still_records_explicit_no_bet_with_new_objective(tmp_path):
    row = mp.capture(
        {}, root=tmp_path, now=NOW, index={}, score_lookup=lambda c: None,
        kickoff_fn=at.parse_kickoff_proven, source_guard=at.execution_source_rejection,
    )
    assert row["status"] == "missed_freeze_no_paper_bet" and not row["accas"]
    assert row["policy"]["selection_objective"] == OBJECTIVE
    assert mp.receipts(tmp_path) == [row]
