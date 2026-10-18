"""Acca price-evidence gate: dynamic, live, with hysteresis.

Pins three things:
  1. the helper splits a pool by the blocked-label set it is given,
     case-insensitively;
  2. the live path wires the dynamic gate (source-level pin, so it cannot be
     silently removed) and sits before the live plan_day call;
  3. the replay recipe (plan_day / select_accas) does not call the gate, so the
     frozen replay baseline does not move.

Dynamic rule (edgefactory.acca_gate): z = (wins - sum(1/odds)) / sqrt(sum p(1-p))
over the trailing 30 days, block at z <= -2.0 with n >= 60, unblock at z >= 0.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory import acca_gate as ag  # noqa: E402


def _leg(match: str, label, odds: float = 1.7, prob: float = 0.7, bucket: str = "SKIPPED_VETO"):
    home, _, away = match.partition(" v ")
    row = {"bucket": bucket, "odds": odds, "avg_p": prob * 100.0,
           "home": home, "away": away, "date": "2026-10-15"}
    if label is not None:
        row["price_evidence"] = label
    return {"match": match, "pick": "HOME", "prob": prob, "odds": odds,
            "result": None, "row": row}


def _rows(label, n, wins, odds, day_start, span_days=20):
    """n settled legs for one label, 'wins' of them won, spread over span_days."""
    out = []
    base = date.fromisoformat(day_start)
    for i in range(n):
        out.append({"date": (base + timedelta(days=i % span_days)).isoformat(),
                    "price_evidence": label, "odds": odds, "won": i < wins})
    return out


# ---- helper split ---------------------------------------------------------

def test_helper_splits_by_supplied_label_set_case_insensitively():
    pool = [
        _leg("A v B", "SCOUTINGSTATS_SOLE"),
        _leg("C v D", "betexplorer_rescue"),
        _leg("E v F", "NAMED_BOOKMAKER_PRICE"),
        _leg("G v H", "BZZOIRO_PRIMARY"),
        _leg("I v J", None),
        _leg("K v L", "  scoutingstats_sole  "),
    ]
    kept, blocked = at.acca_price_evidence_gate(pool, {"SCOUTINGSTATS_SOLE", "BETEXPLORER_RESCUE"})
    assert [l["match"] for l in blocked] == ["A v B", "C v D", "K v L"]
    assert [l["match"] for l in kept] == ["E v F", "G v H", "I v J"]


def test_empty_blocked_set_blocks_nothing():
    pool = [_leg("A v B", "SCOUTINGSTATS_SOLE"), _leg("C v D", "BETEXPLORER_RESCUE")]
    kept, blocked = at.acca_price_evidence_gate(pool, frozenset())
    assert blocked == [] and len(kept) == 2


def test_missing_label_is_kept_not_blocked():
    kept, blocked = at.acca_price_evidence_gate([_leg("X v Y", None)], {"SCOUTINGSTATS_SOLE"})
    assert blocked == []
    assert len(kept) == 1


def test_static_constant_is_gone():
    assert not hasattr(at, "ACCA_BLOCKED_PRICE_EVIDENCE")


# ---- statistics -----------------------------------------------------------

def test_label_stats_excludes_same_day_and_out_of_window_legs():
    rows = [
        {"date": "2026-10-15", "price_evidence": "X", "odds": 2.0, "won": True},   # same day: excluded
        {"date": "2026-09-14", "price_evidence": "X", "odds": 2.0, "won": True},   # 31 days back: excluded
        {"date": "2026-09-15", "price_evidence": "X", "odds": 2.0, "won": False},  # 30 days back: included
        {"date": "2026-10-14", "price_evidence": "X", "odds": 2.0, "won": True},   # included
    ]
    st = ag.label_stats(rows, "2026-10-15")
    assert st["X"]["n"] == 2
    assert st["X"]["hit_rate"] == 0.5


def test_label_stats_skips_bad_odds_and_missing_outcome():
    rows = [
        {"date": "2026-10-10", "price_evidence": "X", "odds": 1.0, "won": True},
        {"date": "2026-10-10", "price_evidence": "X", "odds": None, "won": True},
        {"date": "2026-10-10", "price_evidence": "X", "odds": 2.0, "won": None},
        {"date": "2026-10-10", "price_evidence": "X", "odds": 2.0, "won": True},
    ]
    assert ag.label_stats(rows, "2026-10-15")["X"]["n"] == 1


def test_z_matches_hits_minus_implied_over_sd():
    # 60 legs at odds 1.5 (p = 2/3, var = 2/9). 30 wins: z = (30 - 40) / sqrt(60 * 2/9).
    rows = _rows("X", 60, 30, 1.5, "2026-10-01", span_days=10)  # all dated before 2026-10-15
    st = ag.label_stats(rows, "2026-10-15")["X"]
    assert st["n"] == 60
    expected = (30 - 60 * (1 / 1.5)) / (60 * (2 / 9)) ** 0.5
    assert abs(st["z"] - round(expected, 3)) < 1e-6


# ---- hysteresis -----------------------------------------------------------

def _stat(n, z):
    return {"n": n, "z": z}


def test_blocks_only_at_or_below_z_block_with_enough_legs():
    blocked, changes = ag.step_blocked(set(), {"X": _stat(60, -2.0)})
    assert blocked == {"X"} and changes and changes[0].startswith("BLOCK X")
    blocked, _ = ag.step_blocked(set(), {"X": _stat(60, -1.99)})
    assert blocked == set()


def test_thin_sample_never_blocks_and_keeps_prior_state():
    blocked, _ = ag.step_blocked(set(), {"X": _stat(59, -4.0)})
    assert blocked == set()
    blocked, _ = ag.step_blocked({"X"}, {"X": _stat(10, +3.0)})
    assert blocked == {"X"}


def test_hysteresis_band_holds_block_until_z_recovers_to_zero():
    b = {"X"}
    b, _ = ag.step_blocked(b, {"X": _stat(80, -1.0)})   # inside band: stays blocked
    assert b == {"X"}
    b, _ = ag.step_blocked(b, {"X": _stat(80, -0.01)})  # still below 0: stays blocked
    assert b == {"X"}
    b, changes = ag.step_blocked(b, {"X": _stat(80, 0.0)})  # recovered
    assert b == set() and changes[0].startswith("UNBLOCK X")


def test_unblocked_label_inside_band_stays_open():
    b, _ = ag.step_blocked(set(), {"X": _stat(80, -1.5)})
    assert b == set()


# ---- refresh: state file, freshness, idempotence -------------------------

def _ledger(tmp: Path, end: str, rows) -> Path:
    p = tmp / "picks_audit_rolling.json"
    p.write_text(json.dumps({"end": end, "settled_ledger": rows}))
    return p


def test_refresh_blocks_then_is_idempotent_for_the_same_day(tmp_path):
    rows = _rows("SCOUTINGSTATS_SOLE", 80, 40, 1.5, "2026-09-20")  # 40/80 vs implied 53: z far below -2
    lp = _ledger(tmp_path, "2026-10-15", rows)
    sp = tmp_path / "acca_gate_state.json"
    blocked, status = ag.refresh("2026-10-15", ledger_path=lp, state_path=sp)
    assert blocked == {"SCOUTINGSTATS_SOLE"} and "stepped" in status
    saved = json.loads(sp.read_text())
    assert saved["as_of_last"] == "2026-10-15"
    # second call the same day: no re-step, same answer
    blocked2, status2 = ag.refresh("2026-10-15", ledger_path=lp, state_path=sp)
    assert blocked2 == {"SCOUTINGSTATS_SOLE"} and "already stepped" in status2


def test_refresh_keeps_state_when_ledger_is_stale_or_missing(tmp_path):
    sp = tmp_path / "acca_gate_state.json"
    sp.write_text(json.dumps({"as_of_last": "2026-10-14", "blocked": {"X": {"since": "2026-10-10", "z": -2.5}}}))
    lp = _ledger(tmp_path, "2026-10-14", [])                  # ledger not for today
    blocked, status = ag.refresh("2026-10-15", ledger_path=lp, state_path=sp)
    assert blocked == {"X"} and "state kept" in status
    assert json.loads(sp.read_text())["as_of_last"] == "2026-10-14"  # untouched
    blocked, status = ag.refresh("2026-10-15", ledger_path=tmp_path / "nope.json", state_path=sp)
    assert blocked == {"X"} and "unavailable" in status


def test_refresh_with_no_state_and_no_ledger_blocks_nothing(tmp_path):
    blocked, _ = ag.refresh("2026-10-15", ledger_path=tmp_path / "nope.json", state_path=tmp_path / "s.json")
    assert blocked == set()


def test_refresh_write_false_does_not_touch_state(tmp_path):
    rows = _rows("X", 80, 40, 1.5, "2026-09-20")
    lp = _ledger(tmp_path, "2026-10-15", rows)
    sp = tmp_path / "acca_gate_state.json"
    blocked, _ = ag.refresh("2026-10-15", ledger_path=lp, state_path=sp, write=False)
    assert blocked == {"X"} and not sp.exists()


# ---- live wiring and replay parity ----------------------------------------

def test_live_path_wires_the_dynamic_gate_before_plan_day():
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    assert "gate_labels, gate_status = acca_gate.refresh(target)" in src
    assert "acca_price_evidence_gate(plan_pool, gate_labels)" in src
    assert '"ACCA PRICE-EVIDENCE GATE: blocked label"' in src
    assert 'print(f"ACCA PRICE-EVIDENCE GATE: {gate_status}")' in src
    i_bench = src.index("selection_ladder_bucket_benched")
    i_gate = src.index("acca_price_evidence_gate(plan_pool, gate_labels)")
    i_plan = src.index("plan = plan_day(plan_pool, bank_eff")
    assert i_bench < i_gate < i_plan


def test_seeded_pair_on_todays_stats_reopens_one_and_keeps_one_blocked():
    # Seed = the static pair. On the 2026-10-15 stats: SCOUTINGSTATS_SOLE z +0.23
    # (recovered, reopens), BETEXPLORER_RESCUE z -0.37 (inside the band, stays blocked).
    stats = {
        "SCOUTINGSTATS_SOLE": {"n": 165, "z": 0.234},
        "BETEXPLORER_RESCUE": {"n": 104, "z": -0.37},
    }
    blocked, changes = ag.step_blocked({"SCOUTINGSTATS_SOLE", "BETEXPLORER_RESCUE"}, stats)
    assert blocked == {"BETEXPLORER_RESCUE"}
    assert changes == ["UNBLOCK SCOUTINGSTATS_SOLE (n=165, z=+0.23)"]


def test_replay_recipe_is_unchanged_by_the_gate():
    # plan_day does not call the gate, so a leg with a currently blocked label
    # still rides a replayed acca and the frozen replay baseline does not move.
    pool = [
        _leg("A v B", "SCOUTINGSTATS_SOLE", odds=1.6, prob=0.80),
        _leg("C v D", "NAMED_BOOKMAKER_PRICE", odds=1.6, prob=0.78),
        _leg("E v F", "NAMED_BOOKMAKER_PRICE", odds=1.6, prob=0.76),
        _leg("G v H", "NAMED_BOOKMAKER_PRICE", odds=1.6, prob=0.74),
    ]
    plan = at.plan_day(pool, 100.0)
    used = {l["match"] for a in plan for l in a["legs"]}
    assert "A v B" in used


def test_gate_run_log_records_blocked_legs_and_empty_runs(tmp_path):
    """Every gate run appends one line: the status, the blocked label set, and each
    leg the gate removed. An empty block is still logged, so a quiet run is visible."""
    leg = {"match": "A vs B", "pick": "HOME", "odds": 1.8, "prob": 0.7,
           "row": {"price_evidence": "BETEXPLORER_RESCUE", "bucket": "SKIPPED_VETO"}}
    path = tmp_path / "acca_gate_log.jsonl"
    at.log_acca_gate_run("2026-10-17", "stepped for 2026-10-17", {"BETEXPLORER_RESCUE"}, [leg], path=path)
    at.log_acca_gate_run("2026-10-17", "already stepped", {"BETEXPLORER_RESCUE"}, [], path=path)
    lines = path.read_text().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["target"] == "2026-10-17"
    assert first["blocked_labels"] == ["BETEXPLORER_RESCUE"]
    assert first["blocked_legs"][0]["match"] == "A vs B"
    assert first["blocked_legs"][0]["label"] == "BETEXPLORER_RESCUE"
    assert json.loads(lines[1])["blocked_legs"] == []


def test_gate_run_log_records_pool_size_and_sast_time(tmp_path):
    """An empty blocked_legs is only readable next to pool_size: it means the gate
    checked that many legs and none carried a blocked label. run_at is SAST."""
    path = tmp_path / "acca_gate_log.jsonl"
    at.log_acca_gate_run("2026-10-18", "stepped for 2026-10-18", {"BETEXPLORER_RESCUE"}, [],
                         pool_size=7, path=path)
    rec = json.loads(path.read_text().splitlines()[0])
    assert rec["pool_size"] == 7
    assert rec["blocked_count"] == 0
    assert rec["blocked_legs"] == []
    assert rec["run_at"].endswith("+02:00")


def test_gate_log_write_failure_does_not_raise(tmp_path, capsys):
    """Logging must never stop ticket placement: a failed write only warns."""
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("x")
    bad_path = blocker / "acca_gate_log.jsonl"  # parent is a file, so the write fails
    at.log_acca_gate_run("2026-10-18", "stepped", {"BETEXPLORER_RESCUE"}, [], pool_size=3,
                         path=bad_path)  # must not raise
    assert "acca gate log not written" in capsys.readouterr().err
