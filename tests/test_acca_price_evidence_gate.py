"""Acca price-evidence gate (2026-10-15).

Pins the operator-approved gate: legs whose price evidence is
SCOUTINGSTATS_SOLE or BETEXPLORER_RESCUE are blocked from ACCAS only.

Evidence (warehouse-backed audit, 2026-06-01..2026-10-14, SKIPPED_VETO legs at
1.50-1.99): SCOUTINGSTATS_SOLE n=105 hit 50.5% vs implied 60.5% (ROI -16.4%);
BETEXPLORER_RESCUE n=48 hit 52.1% vs implied 59.9% (ROI -13.9%).

These tests pin three things:
  1. the helper splits the pool by label, case-insensitively;
  2. the live path wires the gate (source-level pin, so it cannot be silently
     removed);
  3. the replay recipe (plan_day / select_accas) is unchanged, so the frozen
     replay baseline does not move.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402


def _leg(match: str, label, odds: float = 1.7, prob: float = 0.7, bucket: str = "SKIPPED_VETO"):
    home, _, away = match.partition(" v ")
    row = {"bucket": bucket, "odds": odds, "avg_p": prob * 100.0,
           "home": home, "away": away, "date": "2026-10-15"}
    if label is not None:
        row["price_evidence"] = label
    return {"match": match, "pick": "HOME", "prob": prob, "odds": odds,
            "result": None, "row": row}


def test_blocked_labels_are_exactly_the_audited_pair():
    assert at.ACCA_BLOCKED_PRICE_EVIDENCE == frozenset(
        {"SCOUTINGSTATS_SOLE", "BETEXPLORER_RESCUE"})


def test_helper_splits_by_label_and_is_case_insensitive():
    pool = [
        _leg("A v B", "SCOUTINGSTATS_SOLE"),
        _leg("C v D", "betexplorer_rescue"),
        _leg("E v F", "NAMED_BOOKMAKER_PRICE"),
        _leg("G v H", "BZZOIRO_PRIMARY"),
        _leg("I v J", None),
        _leg("K v L", "  scoutingstats_sole  "),
    ]
    kept, blocked = at.acca_price_evidence_gate(pool)
    assert [l["match"] for l in blocked] == ["A v B", "C v D", "K v L"]
    assert [l["match"] for l in kept] == ["E v F", "G v H", "I v J"]


def test_missing_label_is_kept_not_blocked():
    # Absence of a label is not evidence of a weak price; the gate only acts
    # on the two audited labels.
    kept, blocked = at.acca_price_evidence_gate([_leg("X v Y", None)])
    assert blocked == []
    assert len(kept) == 1


def test_live_path_wires_the_gate_with_census_and_ledger():
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    assert "plan_pool, price_gate_blocked = acca_price_evidence_gate(plan_pool)" in src
    assert '"acca_price_evidence_gate"' in src
    assert '"ACCA PRICE-EVIDENCE GATE: blocked label"' in src
    # The gate must sit after the slice bench and before the live plan_day call.
    i_bench = src.index("selection_ladder_bucket_benched")
    i_gate = src.index("acca_price_evidence_gate(plan_pool)")
    i_plan = src.index("plan = plan_day(plan_pool, bank_eff")
    assert i_bench < i_gate < i_plan


def test_replay_recipe_is_unchanged_by_the_gate():
    # plan_day / select_accas do not call the gate: a blocked-label leg still
    # rides a replayed acca, so the frozen replay baseline does not move.
    pool = [
        _leg("A v B", "SCOUTINGSTATS_SOLE", odds=1.6, prob=0.80),
        _leg("C v D", "NAMED_BOOKMAKER_PRICE", odds=1.6, prob=0.78),
        _leg("E v F", "NAMED_BOOKMAKER_PRICE", odds=1.6, prob=0.76),
        _leg("G v H", "NAMED_BOOKMAKER_PRICE", odds=1.6, prob=0.74),
    ]
    plan = at.plan_day(pool, 100.0)
    used = {l["match"] for a in plan for l in a["legs"]}
    assert "A v B" in used
