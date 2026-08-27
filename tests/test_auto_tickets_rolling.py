"""Contract tests for the ROLLING auto-tickets engine — PERCENT-ONLY edition.

Pins: no-filter playable legs, top-6 by stated prob, consecutive 2-leg accas
(max 3), 50% of bank per day (stakes in % of capital), volume regime
(>=12 legs -> prob>=65% only), committed-stake accounting, settlement moves
the bank in %, and the TAKE-PROFIT NOTIFICATION (performance-based: fires at
+100% per cycle, moves no amounts, resets the cycle baseline).
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402


@pytest.fixture(autouse=True)
def _sandbox_state(tmp_path, monkeypatch):
    """EVERY test here must write state to a temp file — save_state() is
    called deep inside settle/backfill, so patch STATE_FILE/LOCALDATA
    unconditionally (an earlier version leaked a test slip into the real
    localdata/auto_tickets_state.json)."""
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)


def _leg(tag, prob, odds, result=None):
    return {"match": f"Team {tag} vs Other {tag}", "pick": "HOME",
            "prob": prob, "odds": odds, "result": result,
            "row": {"home": f"Team {tag}", "away": f"Other {tag}", "pick": "home"}}


# ---------------- planning (percent stakes) ----------------

def test_plan_day_top6_consecutive_pairs_and_stake_pct():
    pool = [_leg(i, 0.60 + i / 100, 1.10 + i / 10) for i in range(9)]
    plan = at.plan_day(pool, bank_pct=100.0)
    assert len(plan) == at.MAX_ACCAS
    assert all(len(a["legs"]) == at.LEGS_PER_ACCA for a in plan)
    assert plan[0]["legs"][0]["prob"] >= plan[0]["legs"][1]["prob"] >= plan[1]["legs"][0]["prob"]
    # stake = 50% of bank split across 3 accas -> 16.67% of capital each
    assert plan[0]["stake_pct"] == pytest.approx(100.0 * at.STAKE_FRAC / at.MAX_ACCAS, abs=1e-3)
    assert plan[0]["odds"] == pytest.approx(
        plan[0]["legs"][0]["odds"] * plan[0]["legs"][1]["odds"], abs=0.01)
    assert "stake" not in plan[0] and "stake_pct" in plan[0]   # percent-only contract


def test_plan_day_volume_regime_filters_low_prob():
    pool = [_leg(f"lo{i}", 0.55, 1.9) for i in range(6)] + \
           [_leg(f"hi{i}", 0.72, 1.3) for i in range(8)]      # 14 legs -> volume regime
    plan = at.plan_day(pool, bank_pct=100.0)
    legs = [l for a in plan for l in a["legs"]]
    assert legs and all(l["prob"] >= at.VOLUME_MIN_PROB for l in legs)


def test_plan_day_too_few_legs_or_busted_bank():
    assert at.plan_day([_leg("a", 0.7, 1.2)], 100.0) == []
    assert at.plan_day([_leg("a", 0.7, 1.2), _leg("b", 0.7, 1.3)], 0.0) == []


# ---------------- settlement + take-profit notification ----------------

def _one_acca_slip(date, legs_spec, stake_pct, odds):
    return {"date": date, "staked_pct": stake_pct,
            "accas": [{"odds": odds, "stake_pct": stake_pct,
                       "legs": [_leg(t, 0.75, o, r) for t, o, r in legs_spec]}]}


def _archives_for(date, legs_spec):
    return [{"date": date, "home": f"Team {t}", "away": f"Other {t}", "pick": "home",
             "bucket": "SKIPPED_VETO", "quarantine": "none", "odds": o,
             "avg_p": 75.0, "edge_rule": "r"} for t, o, r in legs_spec]


def _settled_for(date, legs_spec):
    return {(date, norm_team(f"Team {t}"), norm_team(f"Other {t}")):
            ("home" if r == "win" else "away") for t, o, r in legs_spec}


def test_settle_losing_day_moves_bank_no_notification():
    st = at.fresh_state()   # bank 100%
    spec = [("a", 1.4, "win"), ("b", 1.43, "loss")]
    st["open_slips"].append(_one_acca_slip("2026-08-20", spec, 50.0, 2.0))
    at.settle_open_slips(st, _settled_for("2026-08-20", spec),
                         archives=_archives_for("2026-08-20", spec))
    assert st["bank"] == pytest.approx(50.0)
    assert st["events"] == []
    assert st["open_slips"] == []


def test_settle_winning_day_below_target_no_notification():
    st = at.fresh_state()
    spec = [("w1", 1.5, "win"), ("w2", 1.67, "win")]
    st["open_slips"].append(_one_acca_slip("2026-08-21", spec, 50.0, 2.5))
    at.settle_open_slips(st, _settled_for("2026-08-21", spec),
                         archives=_archives_for("2026-08-21", spec))
    # 100 - 50 + 125 = 175% — below the 200% target: bank moves, NO notification
    assert st["bank"] == pytest.approx(175.0)
    assert st["events"] == []
    assert st["cycle_base"] == pytest.approx(100.0)


def test_take_profit_notification_fires_moves_no_amounts_and_resets_cycle():
    st = at.fresh_state()
    st["bank"] = 260.0   # performance arrived via wins
    st["cycle_base"] = 100.0
    events = at._apply_settlement(st, ret_pct=100.0, staked_pct=0.0, when="2026-08-22")
    # bank 360 >= target 200 -> NOTIFICATION; bank unchanged; baseline resets
    assert st["bank"] == pytest.approx(360.0)
    assert st["cycle_base"] == pytest.approx(360.0)
    assert at.take_profit_target(st) == pytest.approx(720.0)
    assert st["events"] and st["events"][0]["action"] == "TAKE_PROFIT_NOTIFICATION"
    assert st["events"][0]["gain_pct"] == pytest.approx(260.0)
    assert any("TAKE-PROFIT" in e for e in events)
    # marker file written (the notification artifact)
    assert (at.LOCALDATA / "auto_tickets_takeprofit_2026-08-22.json").exists()


def test_settle_keeps_unresolved_slips_open_and_stakes_committed():
    st = at.fresh_state()
    spec = [("p", 1.4, None), ("q", 1.43, None)]
    st["open_slips"].append(_one_acca_slip("2026-08-22", spec, 50.0, 2.0))
    done = at.settle_open_slips(st, {}, archives=_archives_for("2026-08-22", spec))
    assert done == []
    assert len(st["open_slips"]) == 1
    assert st["bank"] == pytest.approx(100.0)          # stakes leave only at settlement
    assert at.effective_bank(st) == pytest.approx(50.0)  # but are committed


# ---------------- playable-leg filter ----------------

def test_playable_legs_bucket_and_quarantine_and_price_filters():
    rows = [
        {"date": "2026-08-20", "home": "A", "away": "B", "pick": "home",
         "bucket": "SKIPPED_VETO", "quarantine": "none", "odds": 1.3, "avg_p": 75.0},
        {"date": "2026-08-20", "home": "C", "away": "D", "pick": "home",
         "bucket": "CAUTION", "quarantine": "none", "odds": 1.3, "avg_p": 75.0},
        {"date": "2026-08-20", "home": "E", "away": "F", "pick": "home",
         "bucket": "SKIPPED_VETO", "quarantine": "alias_fuzzy", "odds": 1.3, "avg_p": 75.0},
        {"date": "2026-08-20", "home": "G", "away": "H", "pick": "home",
         "bucket": "SKIPPED_VETO", "quarantine": "none", "odds": None, "avg_p": 75.0},
    ]
    legs = at.playable_legs(rows, day="2026-08-20")
    assert [l["match"] for l in legs] == ["A vs B"]


# ---------------- backfill end-to-end (percent arithmetic) ----------------

def test_backfill_end_to_end(tmp_path, monkeypatch):
    days = {"2026-08-01": [("Ah", "Bh", 1.25, 80.0, "home"), ("Ch", "Dh", 1.6, 75.0, "home")],
            "2026-08-02": [("Eh", "Fh", 1.3, 78.0, "home"), ("Gh", "Hh", 1.4, 72.0, "away")]}
    archives, settled = [], {}
    for d, rows in days.items():
        for h, a, o1, ap, outcome in rows:
            archives.append({"date": d, "home": h, "away": a, "pick": "home",
                             "bucket": "SKIPPED_VETO", "quarantine": "none",
                             "odds": o1, "avg_p": ap, "edge_rule": "r"})
            settled[(d, norm_team(h), norm_team(a))] = outcome
    monkeypatch.setattr(at, "load_archived_picks", lambda: archives)
    monkeypatch.setattr(at, "load_settled", lambda: settled)
    args = SimpleNamespace(from_=None, to="2026-08-03", reset=True)
    at.cmd_backfill(args, at.load_state())
    st = at.load_state()
    assert len(st["history"]) == 2
    # day1: one acca @2.00 (1.25*1.6), stake 50% -> bank 100-50+100 = 150%
    assert st["history"][0]["bank_pct"] == pytest.approx(150.0, abs=0.01)
    assert st["events"] == []                       # 150% < 200% target
    # day2: stake = 50% of 150 = 75%, acca loses -> bank 75%
    assert st["history"][1]["bank_pct"] == pytest.approx(75.0, abs=0.05)
    assert st["cycle_base"] == pytest.approx(100.0)  # unchanged — no notification fired
