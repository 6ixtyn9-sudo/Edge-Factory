"""Exact opportunity replay is not a new bet; fresh evidence may reuse budget."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta

import pytest

from edgefactory import ml_paper as mp
from test_ml_paper import NOW
from test_ml_paper_rolling import run
from test_ml_paper_rolling_residual_budget import modest_edge_slate


def test_repeated_scans_of_identical_inputs_do_not_fill_fixture_cap(tmp_path):
    rows = modest_edge_slate()
    first = run(tmp_path, rows=rows)
    original = mp.rolling_receipt_path(tmp_path, first).read_bytes()
    stake = first["accas"][0]["stake_units"]
    for minutes in (2, 3, 60, 120):
        scan = run(tmp_path, NOW + timedelta(minutes=minutes), deepcopy(rows))
        if scan is not None:
            assert not scan["accas"]
            assert scan["search"]["opportunity_replay"]["dropped_acca_count"] == 1
    report = mp.performance(mp.receipts(tmp_path), lambda _: None)
    assert report["paper_committed_units"] == stake < 5
    assert report["pending_accas"] == 1
    audit = mp.render_daily_card(mp.receipts(tmp_path), report, audit=True)
    assert "Exact opportunity replay:" in audit
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == original


def test_context_noise_and_leg_order_are_not_new_opportunities(tmp_path):
    rows = modest_edge_slate()
    first = run(tmp_path, rows=rows)
    changed_context = [*reversed(rows), deepcopy(rows[0])]
    scan = run(tmp_path, NOW + timedelta(minutes=2), changed_context)
    assert scan is not None and not scan["accas"]
    assert mp._acca_opportunity_key(first["accas"][0]) == mp._acca_opportunity_key(
        dict(first["accas"][0], legs=list(reversed(first["accas"][0]["legs"])), stake_units=.001))


def test_concurrent_later_scans_reserve_identical_opportunity_once(tmp_path):
    rows = modest_edge_slate()
    first = run(tmp_path, rows=rows)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda i: run(tmp_path, NOW + timedelta(minutes=1), rows), range(3)))
    assert all(r is None or not r["accas"] for r in results)
    report = mp.performance(mp.receipts(tmp_path), lambda _: None)
    assert report["pending_accas"] == 1
    assert report["paper_committed_units"] == first["accas"][0]["stake_units"]


@pytest.mark.parametrize("change", ["quote_timestamp", "price", "forecast"])
def test_new_evidence_can_reuse_remaining_fixture_budget(tmp_path, change):
    rows = modest_edge_slate()
    first = run(tmp_path, rows=rows)
    original = mp.rolling_receipt_path(tmp_path, first).read_bytes()
    updated = deepcopy(rows)
    if change == "quote_timestamp":
        for row in updated:
            row["odds_captured_at"] = NOW.isoformat()
    elif change == "price":
        for row in updated:
            row["odds"] += .01
    else:
        for row in updated:
            row["statistical_profile"]["ml_inputs"]["values"]["forecast_1x2_home_mean"] = .56
    second = run(tmp_path, NOW + timedelta(minutes=2), updated)
    assert second and second["accas"]
    assert all(e["prior_open_stake_micro_units"] > 0 for e in second["fixture_concentration"]["fixtures"])
    assert mp.performance(mp.receipts(tmp_path), lambda _: None)["paper_committed_units"] <= 5
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == original


def test_replay_drop_does_not_refill_other_allocations():
    legs = [{"fixture": ["2026-11-06", "homeclub1", "awayclub1"], "book": "A"},
            {"fixture": ["2026-11-06", "homeclub2", "awayclub2"], "book": "A"}]
    prior = {"legs": legs, "stake_units": 1, "profit_units": None}
    another = {"legs": [dict(c, market="btts_yes", selection="yes") for c in legs], "stake_units": .5}
    plan = [dict(prior, stake_units=.9), another]
    before = deepcopy(plan)
    diagnostics = {}
    kept = mp._without_replayed_accas(plan, {"history": [{"accas": [prior]}]}, diagnostics)
    assert kept == [another] and another["stake_units"] == .5
    assert plan == before
    assert diagnostics["opportunity_replay"]["released_stake_units"] == .9
