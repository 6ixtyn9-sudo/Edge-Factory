"""Operator pre-kickoff paper replacement (supersession): regression pin.

2026-11-16 evidence: receipt 1a902a22 (2026-11-13T09:13:03.978090Z) carries
the operator deed ``operator_pre_kickoff_paper_replacement_v1`` targeting acca
1 of receipt fdbe9fde (2026-11-12T22:36:42.381751Z) — a still-open double-draw
slip whose legs kicked off ~10.5h after the replacement froze. The replacement
reuses both fixtures while declaring ``prior_open_stake_micro_units: 0`` and
``paper_pending_reserved_at_decision: 0``; without supersession-aware grading
that is a committed-ledger mismatch, and without supersession-aware
performance accounting the replaced acca booked P&L it never risked.
"""

import json
from copy import deepcopy
from datetime import timedelta
from decimal import ROUND_CEILING
from pathlib import Path

import pytest
from test_ml_paper import NOW
from test_ml_paper_redteam import sign
from test_ml_paper_rolling import run

from edgefactory import ml_paper as mp
from edgefactory.odds_normalization import parse_zoned_timestamp

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS_DIR = ROOT / "localdata" / "phase5_reconciliation" / "ml_paper_receipts"
TARGET_SHA = "fdbe9fde2b5cc5f819d495357022510122dd04300de5a7ae242c8d564573a852"


def _replacement(root, first, hours=3):
    """Second rolling decision: identical accas on the same fixtures, captured
    later, declaring the operator deed that released first's acca pre-kickoff."""
    later = parse_zoned_timestamp(first["captured_at"]) + timedelta(hours=hours)
    row = deepcopy(first)
    row["decision_id"] = later.astimezone(mp.UTC).strftime("%Y%m%dT%H%M%S%fZ")
    for key in ("captured_at", "frozen_at", "persisted_at", "freeze_at", "window_start"):
        if key in row:
            row[key] = later.isoformat()
    assert later.astimezone(mp.LOCAL_TZ).date().isoformat() == row["date"]
    row["window_end"] = (later + timedelta(hours=24)).isoformat()
    row["prior_receipt_sha256s"] = [first["sha256"]]
    learning = deepcopy(row.get("learning") or {})
    if "as_of" in learning:
        learning["as_of"] = later.isoformat()
    if "model_key" in learning:  # the learner's own content digest covers as_of
        learning["model_key"] = mp.digest({k: v for k, v in learning.items()
                                           if k != "model_key"})
    row["learning"] = learning
    for c in row["candidates"]:  # each frozen forecast binds the learner digest
        if c.get("forecast_model_key") is not None and "model_key" in learning:
            c["forecast_model_key"] = learning["model_key"]
    # The deed released first's stakes before this decision: no commitments.
    row["paper_pending_reserved_at_decision"] = 0
    row["paper_available_at_decision"] = row.get("paper_bank_at_decision")
    row["supersession"] = {
        "policy": mp.SUPERSESSION_POLICY,
        "reason": "operator pre-kickoff paper replacement (synthetic test copy)",
        "targets": [{"receipt_sha256": first["sha256"], "acca_index": 1}],
    }
    row = sign(row)
    mp._write_once(mp.rolling_receipt_path(root, row), row)
    return row


def test_replacement_receipt_releases_superseded_fixture_budget(tmp_path):
    first = run(tmp_path)
    assert first["accas"] and first["freeze_basis"] == mp.ROLLING_FREEZE
    second = _replacement(tmp_path, first)
    assert second["supersession"]["targets"] == [
        {"receipt_sha256": first["sha256"], "acca_index": 1}
    ]
    # The committed-stakes check would see the replacement staking fixtures its
    # audit declares at prior 0 while first's stake still shows open — unless
    # the deed releases them. Integrity validation must pass.
    rows = mp.receipts(tmp_path)
    assert [r["sha256"] for r in rows] == [first["sha256"], second["sha256"]]
    assert mp._superseded_accas(rows) == {(first["sha256"], 1): second["sha256"]}


def test_superseded_acca_is_void_for_grading_capital_and_reservations(tmp_path):
    first = run(tmp_path)
    second = _replacement(tmp_path, first)
    rows = mp.receipts(tmp_path)

    def win_lookup(c):
        return (2, 0) if c["selection"] == "home" else (0, 2)

    report = mp.performance(rows, win_lookup)
    assert report["superseded_tickets"] == 1
    acca = second["accas"][0]
    assert report["settled_accas"] == 1
    assert report["wins"] == 1
    assert report["profit_units"] == pytest.approx(acca["stake_units"] * (acca["odds"] - 1))
    # The superseded acca is neither settled nor pending: void.
    assert report["pending_accas"] == 0
    by_day = {d["date"]: d for d in report["history"]}
    assert len(by_day) == 1  # both decisions share the ticket date

    pending = mp.performance(rows, lambda c: None)
    assert pending["superseded_tickets"] == 1
    assert pending["settled_accas"] == 0
    assert pending["pending_accas"] == 1  # only the replacement acca
    fixtures = {tuple(c["fixture"]) for c in acca["legs"]}
    prior = mp._prior_open_fixture_micro_units(pending)
    mu = mp._decimal_micro_units(acca["stake_units"], "prior open stake",
                                 rounding=ROUND_CEILING)
    assert prior == {f: mu for f in fixtures}  # released stake reserves nothing


DEED_BASE = {
    "policy": "operator_pre_kickoff_paper_replacement_v1",
    "reason": "r",
    "targets": [{"receipt_sha256": "a" * 64, "acca_index": 1}],
}


def _deed_rows(deed):
    leg = {"kickoff_utc": "2026-11-13T19:45:00+00:00"}
    prior = {"sha256": "a" * 64, "captured_at": "2026-11-12T22:36:42+00:00",
             "accas": [{"legs": [leg, leg]}]}
    latter = {"sha256": "b" * 64, "captured_at": "2026-11-13T09:13:03+00:00",
              "frozen_at": "2026-11-13T09:15:47+00:00",
              "accas": [], "supersession": deed}
    return [prior, latter]


def test_recorded_operator_deed_is_pre_kickoff_and_single_targeted():
    assert mp._superseded_accas(_deed_rows(dict(DEED_BASE))) == {
        ("a" * 64, 1): "b" * 64
    }


@pytest.mark.parametrize("damage", [
    "policy", "target_unknown", "target_self", "index_zero", "index_range",
    "not_earlier", "after_kickoff", "duplicate_deed", "no_targets", "bad_index_type",
    "kickoff_during_build", "kickoff_at_freeze", "missing_kickoff", "empty_legs",
    "missing_freeze", "freeze_before_capture",
])
def test_malformed_supersession_deeds_fail_closed(damage):
    deed = dict(DEED_BASE)
    rows = _deed_rows(deed)
    if damage == "policy":
        deed["policy"] = "operator_post_kickoff_rewrite"
    if damage == "target_unknown":
        deed["targets"] = [{"receipt_sha256": "c" * 64, "acca_index": 1}]
    if damage == "target_self":
        deed["targets"] = [{"receipt_sha256": "b" * 64, "acca_index": 1}]
    if damage == "index_zero":
        deed["targets"] = [{"receipt_sha256": "a" * 64, "acca_index": 0}]
    if damage == "index_range":
        deed["targets"] = [{"receipt_sha256": "a" * 64, "acca_index": 2}]
    if damage == "not_earlier":
        rows[0]["captured_at"] = "2026-11-13T10:00:00+00:00"
    if damage == "after_kickoff":
        rows[0]["accas"][0]["legs"][0]["kickoff_utc"] = "2026-11-13T09:00:00+00:00"
    if damage == "kickoff_during_build":
        rows[0]["accas"][0]["legs"][0]["kickoff_utc"] = "2026-11-13T09:14:00+00:00"
    if damage == "kickoff_at_freeze":
        rows[0]["accas"][0]["legs"][0]["kickoff_utc"] = rows[1]["frozen_at"]
    if damage == "missing_kickoff":
        rows[0]["accas"][0]["legs"][0].pop("kickoff_utc")
    if damage == "empty_legs":
        rows[0]["accas"][0]["legs"] = []
    if damage == "missing_freeze":
        rows[1].pop("frozen_at")
    if damage == "freeze_before_capture":
        rows[1]["frozen_at"] = "2026-11-13T09:12:00+00:00"
    if damage == "duplicate_deed":
        third = dict(rows[1])
        third["sha256"] = "d" * 64
        third["captured_at"] = "2026-11-13T09:30:00+00:00"
        rows.append(third)
    if damage == "no_targets":
        deed["targets"] = []
    if damage == "bad_index_type":
        deed["targets"] = [{"receipt_sha256": "a" * 64, "acca_index": True}]
    for row in rows:
        row["supersession"] = row.get("supersession") and deed
    with pytest.raises(ValueError, match="supersession"):
        mp._superseded_accas(rows)


@pytest.mark.skipif(not RECEIPTS_DIR.exists(),
                    reason="frozen ML paper receipts are not in this checkout")
def test_historical_operator_deed_is_exactly_the_2026_11_13_replacement():
    rows = [json.loads(p.read_text()) for p in sorted(RECEIPTS_DIR.glob("autobets_ML_*.json"))]
    deeds = [r for r in rows if isinstance(r.get("supersession"), dict)]
    assert len(deeds) == 1
    deed = deeds[0]["supersession"]
    assert deed["policy"] == mp.SUPERSESSION_POLICY
    assert deed["targets"] == [{"receipt_sha256": TARGET_SHA, "acca_index": 1}]
    by_sha = {r.get("sha256"): r for r in rows}
    prior = by_sha[TARGET_SHA]
    captured = parse_zoned_timestamp(deeds[0]["captured_at"])
    frozen = parse_zoned_timestamp(deeds[0]["frozen_at"])
    assert parse_zoned_timestamp(prior["captured_at"]) < captured <= frozen
    acca = prior["accas"][0]
    assert all(parse_zoned_timestamp(c["kickoff_utc"]) > frozen
               for c in acca["legs"])


def test_superseded_ticket_display_is_released_not_held(tmp_path):
    first = run(tmp_path)
    second = _replacement(tmp_path, first)
    rows = mp.receipts(tmp_path)
    originals = deepcopy(rows)
    report = mp.performance(rows, lambda c: None)
    text = mp.render_performance(report)
    assert text.count("HELD (not settled)") == report["pending_accas"] == 1
    released = text.split("SUPERSEDED BEFORE KICKOFF", 1)[1].split("NOTES", 1)[0]
    assert first["sha256"] in released and second["sha256"] in released
    assert f"released {first['accas'][0]['stake_units']:.6f} paper units" in released
    assert report["paper_committed_units"] == second["accas"][0]["stake_units"]
    assert rows == originals


def test_cancelled_only_selection_remains_pool_evidence_not_selected(tmp_path):
    first = run(tmp_path)
    replacement = _replacement(tmp_path, first)
    replacement["accas"] = []
    replacement["status"] = "no_paper_bet"
    # Test diagnostics on a cancellation with no re-selection of its forecasts.
    diagnostic = mp.calibration_diagnostics([first, replacement], lambda c: (2, 0))
    assert diagnostic["all_candidates"]["resolved_observations"] > 0
    assert diagnostic["selected_candidates"]["resolved_observations"] == 0


@pytest.mark.parametrize("understate_intervening", [False, True])
def test_release_occurs_at_replacement_not_at_original_capture(tmp_path, understate_intervening):
    from test_ml_paper_rolling_residual_budget import modest_edge_slate

    first = run(tmp_path, rows=modest_edge_slate())
    if understate_intervening:
        # Internally consistent but dishonest before the later deed exists:
        # claims the first stake is already released an hour too early.
        middle = _replacement(tmp_path, first, hours=1)
        middle.pop("supersession")
        middle = sign(middle)
        mp.rolling_receipt_path(tmp_path, middle).write_text(json.dumps(middle))
    else:
        now = NOW + timedelta(hours=1)
        middle = run(tmp_path, now, modest_edge_slate(now))
    assert middle["accas"]
    replacement = _replacement(tmp_path, first, hours=3)
    replacement["prior_receipt_sha256s"] = [first["sha256"], middle["sha256"]]
    pending = mp.performance([middle], lambda c: None)
    replacement["paper_pending_reserved_at_decision"] = pending["paper_committed_units"]
    replacement["paper_available_at_decision"] = pending["paper_free_units"]
    plan, audit = mp.project_fixture_stakes(
        replacement["accas"], total_bank_units=100,
        prior_open_fixture_micro_units=mp._prior_open_fixture_micro_units(pending),
    )
    for acca in plan:
        acca["stake_fraction_of_free_bank"] = acca["stake_units"] / pending["paper_free_units"]
        acca["portfolio_allocation"]["aggregate_budget_scale"] = audit["aggregate_budget_scale"]
    replacement["accas"] = plan
    replacement["fixture_concentration"] = audit
    replacement = sign(replacement)
    mp.validate_record(replacement, replacement["date"])
    mp.rolling_receipt_path(tmp_path, replacement).write_text(json.dumps(replacement))
    if understate_intervening:
        with pytest.raises(ValueError, match="complete prior stake evidence"):
            mp.receipts(tmp_path)
    else:
        assert mp.receipts(tmp_path) == [first, middle, replacement]
