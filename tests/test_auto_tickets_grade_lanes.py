"""The rolling-performance grader reports either lane, and the main lane is unchanged.

The grader writes into localdata, so every path it touches is redirected to a
temp directory: the committed localdata and the real lane states are never read
or written by these tests.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402

grade = importlib.import_module("auto_tickets_grade")


def _history_state():
    st = at.fresh_state()
    st["bank"] = 150.0
    st["cycle_base"] = at.BASE_PCT
    st["history"] = [{
        "date": "2026-10-12",
        "accas": [{"odds": 2.0, "won": True}, {"odds": 3.0, "won": False}],
        "bank_pct": 150.0,
    }]
    return st


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    main_state = tmp_path / "auto_tickets_state.json"
    enh_state = tmp_path / "enhancement_tickets_state.json"
    monkeypatch.setattr(grade, "LOCALDATA", localdata)
    monkeypatch.setattr(at, "STATE_FILE", main_state)
    monkeypatch.setattr(at, "load_settled", lambda *a, **k: {})
    enh_lane = at.ENHANCEMENT_LANE._replace(state_file=enh_state)
    monkeypatch.setitem(grade.LANES, "enh", (enh_lane, "ENHANCEMENT TICKETS (ROLLING)",
                                             "autobets_enh_tickets_performance"))
    return {"localdata": localdata, "main_state": main_state, "enh_state": enh_state}


def test_enh_lane_writes_its_own_report(sandbox):
    sandbox["enh_state"].write_text(json.dumps(_history_state()))
    assert grade.main(["--lane", "enh"]) == 0

    txt = (sandbox["localdata"] / "autobets_enh_tickets_performance.txt").read_text()
    assert txt.startswith("ENHANCEMENT TICKETS (ROLLING) — performance")
    assert "BANK     150.0%" in txt
    assert "RECORD   1W / 1L" in txt

    data = json.loads((sandbox["localdata"] / "autobets_enh_tickets_performance.json").read_text())
    assert data["lane"] == "enh"
    assert data["bank_pct"] == 150.0
    assert data["accas"] == {"wins": 1, "losses": 1}
    # the main lane's report is not touched by an enhancement run
    assert not (sandbox["localdata"] / "auto_tickets_performance.txt").exists()


def test_main_lane_default_writes_main_report_only(sandbox):
    sandbox["main_state"].write_text(json.dumps(_history_state()))
    assert grade.main([]) == 0

    txt = (sandbox["localdata"] / "auto_tickets_performance.txt").read_text()
    assert txt.startswith("AUTO-TICKETS (ROLLING) — performance")
    assert "BANK     150.0%" in txt
    data = json.loads((sandbox["localdata"] / "auto_tickets_performance.json").read_text())
    assert data["lane"] == "main"
    assert not (sandbox["localdata"] / "autobets_enh_tickets_performance.txt").exists()


def test_enh_lane_with_no_state_writes_nothing(sandbox, capsys):
    assert grade.main(["--lane", "enh"]) == 0
    assert "nothing to report" in capsys.readouterr().out
    assert not list(sandbox["localdata"].iterdir())


def test_main_lane_with_no_state_keeps_original_message(sandbox, capsys):
    assert grade.main([]) == 0
    assert "no rolling state yet" in capsys.readouterr().out
    assert not list(sandbox["localdata"].iterdir())


def test_unknown_lane_is_rejected(sandbox):
    with pytest.raises(SystemExit):
        grade.main(["--lane", "bogus"])


def test_settled_acca_history_keeps_stake_return_and_each_leg_result():
    """A settled acca records what it staked, returned and how each leg resolved,
    so the report can say which leg decided it."""
    st = at.fresh_state()
    st["bank"] = 100.0
    acca = {"odds": 2.0, "won": False, "stake_pct": 10.0,
            "legs": [{"match": "Alpha vs Beta", "pick": "HOME", "odds": 1.3},
                     {"match": "Gamma vs Delta", "pick": "AWAY", "odds": 1.5}],
            "results": ["win", "loss"]}
    at._record_acca_settlement(st, "2026-10-12", acca)
    rec = st["history"][-1]["accas"][0]
    assert rec["stake_pct"] == 10.0 and rec["returned_pct"] == 0.0
    assert [(l["match"], l["result"]) for l in rec["legs"]] == [
        ("Alpha vs Beta", "win"), ("Gamma vs Delta", "loss")]


def test_report_names_the_leg_that_lost_an_acca_and_shows_held_accas():
    st = at.fresh_state()
    st["bank"] = 80.0
    st["base_pct"] = 100.0
    st["history"] = [{"date": "2026-10-12", "staked_pct": 10.0, "returned_pct": 0.0,
                      "bank_pct": 80.0,
                      "accas": [{"odds": 2.0, "won": False, "stake_pct": 10.0,
                                 "returned_pct": 0.0,
                                 "legs": [{"match": "Alpha vs Beta", "pick": "HOME",
                                           "odds": 1.3, "result": "win"},
                                          {"match": "Gamma vs Delta", "pick": "AWAY",
                                           "odds": 1.5, "result": "loss"}]}]}]
    held_acca = {"odds": 1.85, "won": None, "stake_pct": 5.0,
                 "legs": [{"match": "Eps vs Zeta", "pick": "HOME", "odds": 1.4},
                          {"match": "Eta vs Theta", "pick": "AWAY", "odds": 1.3}],
                 "results": ["win", "conflict"]}
    held = [({"date": "2026-10-12", "accas": [held_acca], "staked_pct": 5.0}, held_acca)]
    from auto_tickets_grade import render_lines
    txt = "\n".join(render_lines(st, "T", 15, held, [st["history"][0]["accas"][0]], 0,
                                 "2026-10-16T06:00:00"))
    assert "lost on: Gamma vs Delta" in txt
    assert "LOST" in txt and "net -10.0%" in txt
    assert "ACCA @1.85" in txt and "HELD (not settled)" in txt
    assert "reason: donor spellings disagree on the outcome of Eta vs Theta" in txt
    assert "bank 90.0% -> 80.0%" in txt


def test_main_report_layout_is_clean_and_flags_bank_breaks():
    """The main-lane text: summary block first, no trailing spaces, a visible flag where
    the stored bank does not carry over, and held accas in their own section."""
    from auto_tickets_grade import render_lines
    st = at.fresh_state()
    st["bank"] = 150.0
    st["base_pct"] = 100.0
    st["cycle_base"] = 100.0
    st["history"] = [
        {"date": "2026-10-12", "staked_pct": 10.0, "returned_pct": 20.0, "bank_pct": 110.0,
         "accas": [{"odds": 2.0, "won": True, "stake_pct": 10.0, "returned_pct": 20.0,
                    "legs": [{"match": "Alpha vs Beta", "pick": "HOME", "odds": 1.3,
                              "result": "win"},
                             {"match": "Gamma vs Delta", "pick": "AWAY", "odds": 1.5,
                              "result": "win"}]}]},
        # opens at 110 - 5 + 10 = 115 by its own numbers, but the day before closed at 110:
        # the stored 150.0 close is inconsistent with the chain, and the report must say so.
        {"date": "2026-10-13", "staked_pct": 10.0, "returned_pct": 5.0, "bank_pct": 150.0,
         "accas": [{"odds": 2.2, "won": False, "stake_pct": 10.0, "returned_pct": 0.0,
                    "legs": [{"match": "Eps vs Zeta", "pick": "HOME", "odds": 1.4,
                              "result": "loss"}]}]},
    ]
    held_acca = {"odds": 1.85, "won": None, "stake_pct": 5.0,
                 "legs": [{"match": "Eta vs Theta", "pick": "AWAY", "odds": 1.3}],
                 "results": ["open"]}
    held = [({"date": "2026-10-14", "accas": [held_acca], "staked_pct": 5.0}, held_acca)]
    lines = render_lines(st, "T", 15, held, [st["history"][0]["accas"][0]], 1,
                              "2026-10-14T06:00:00")
    txt = "\n".join(lines)
    assert txt.splitlines()[0].startswith("T — performance")
    assert not any(l != l.rstrip() for l in lines)
    assert txt.index("BANK") < txt.index("BET-DAYS")
    assert "SNAPSHOT NOTES" in txt
    assert "2026-10-13 to 2026-10-13: stored close +45.00 vs rebuild; no in-line day after 2026-10-13" in txt
    assert "HELD (not yet settled" in txt and "ACCA @1.85" in txt
    assert "lost on: Eps vs Zeta (HOME)" in txt
    # the flag goes on the day whose stored close is off, not on the consistent day
    seg = txt[txt.index("BET-DAYS"):]
    assert seg.index("2026-10-13") < seg.index("~ stored close +45.00") < seg.index("2026-10-12")


def test_day_close_does_not_depend_on_settlement_order():
    """Replays the 13/14 Oct settlement order from production: 14 Oct acca #1 lost
    before 13 Oct acca #2 won. The 13 Oct snapshot (bank_pct) carries the 14 Oct loss,
    but the chained close_pct and the grader's bank-break check do not."""
    st = at.fresh_state()
    st["bank"] = 201.4367
    st["cycle_base"] = 201.4367
    st["history"] = [{"date": "2026-10-12", "staked_pct": 50.9966, "returned_pct": 48.4468,
                      "accas": [], "bank_pct": 201.4367, "close_pct": 201.4367}]

    def settle(date, odds, stake, won):
        ret = round(stake * odds, 4) if won else 0.0
        at._apply_settlement(st, ret, stake, date)
        at._record_acca_settlement(st, date, {"odds": odds, "won": won, "stake_pct": stake,
                                              "legs": [], "results": []})

    settle("2026-10-13", 2.03, 25.1796, False)   # 13 Oct acca #1 lost
    settle("2026-10-14", 3.27, 18.8847, False)   # 14 Oct acca #1 lost (settles first)
    settle("2026-10-13", 1.60, 25.1796, True)    # 13 Oct acca #2 won (settles later)
    settle("2026-10-14", 1.85, 18.8847, True)    # 14 Oct acca #2 won

    by_date = {h["date"]: h for h in st["history"]}
    assert by_date["2026-10-13"]["bank_pct"] == pytest.approx(172.4802, abs=1e-3)
    assert by_date["2026-10-13"]["close_pct"] == pytest.approx(191.3649, abs=1e-3)
    assert by_date["2026-10-14"]["close_pct"] == pytest.approx(188.5322, abs=1e-3)
    assert st["bank"] == pytest.approx(188.5322, abs=1e-3)
    assert grade._snapshot_episodes(st["history"], 203.9865) == []


def test_legacy_rows_without_close_pct_still_report_the_break():
    """Rows written before close_pct existed have only the snapshot. Rebuilt from the
    base, the stored 13 Oct close (172.48) sits 18.88 below the day-attributed 191.36."""
    history = [
        {"date": "2026-10-12", "staked_pct": 50.9966, "returned_pct": 48.4468,
         "accas": [], "bank_pct": 201.4367},
        {"date": "2026-10-13", "staked_pct": 50.3592, "returned_pct": 40.2874,
         "accas": [], "bank_pct": 172.4802},
    ]
    episodes = grade._snapshot_episodes(history, 203.9865)
    assert len(episodes) == 1
    e = episodes[0]
    assert (e["first"], e["last"], e["resumed"]) == ("2026-10-13", "2026-10-13", None)
    assert e["offset"] == pytest.approx(-18.8847, abs=1e-3)


def test_snapshot_episode_ends_when_the_day_is_back_in_line():
    """A late settlement is one run of off-line days, and the run closes on the first
    day that is back in line with the rebuild."""
    history = [
        {"date": "2026-09-10", "staked_pct": 0.0, "returned_pct": 10.0, "accas": [], "bank_pct": 110.0},
        {"date": "2026-09-11", "staked_pct": 0.0, "returned_pct": 0.0, "accas": [], "bank_pct": 125.0},
        {"date": "2026-09-12", "staked_pct": 15.0, "returned_pct": 0.0, "accas": [], "bank_pct": 110.0},
        {"date": "2026-09-13", "staked_pct": 0.0, "returned_pct": 0.0, "accas": [], "bank_pct": 95.0},
    ]
    rebuilt = grade._day_attributed_closes(history, 100.0)
    assert rebuilt == {"2026-09-10": 110.0, "2026-09-11": 110.0,
                       "2026-09-12": 95.0, "2026-09-13": 95.0}
    episodes = grade._snapshot_episodes(history, 100.0)
    assert episodes == [{"first": "2026-09-11", "last": "2026-09-12",
                         "offset": 15.0, "resumed": "2026-09-13"}]
