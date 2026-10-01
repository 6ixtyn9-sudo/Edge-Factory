"""Cleanup of state created by the unapproved future-ticket path."""

from __future__ import annotations

import json

from edgefactory import ticket_state_cleanup as tc

RUN_DATE = "2026-10-01"


def _slip(date, *, staked=21.116, result=None, won=None):
    return {"date": date, "staked_pct": staked,
            "accas": [{"odds": 2.68, "stake_pct": staked, "won": won,
                       "legs": [{"match": "Belgium vs Turkey", "pick": "HOME",
                                 "odds": 1.45, "result": result}]}]}


def test_only_the_bad_future_draft_is_removed(tmp_path):
    """The exact shape found in auto_tickets_state.json."""
    legit = _slip("2026-09-27", staked=15.5364)
    (tmp_path / "auto_tickets_2026-09-27.txt").write_text("real slip")
    bad = _slip("2026-10-02")
    state = {"bank": 184.46, "open_slips": [legit, bad],
             "history": [{"date": "2026-09-27"}]}

    state, removed = tc.clean_state(state, run_date=RUN_DATE, localdata=tmp_path)

    assert [s["date"] for s in removed] == ["2026-10-02"]
    assert [s["date"] for s in state["open_slips"]] == ["2026-09-27"]


def test_a_past_open_slip_is_never_touched(tmp_path):
    state = {"open_slips": [_slip("2026-09-27", staked=15.5364)], "history": []}

    _state, removed = tc.clean_state(state, run_date=RUN_DATE, localdata=tmp_path)

    assert removed == [], "a stale-looking past slip is not this path's doing"


def test_a_future_slip_with_a_real_file_is_kept(tmp_path):
    (tmp_path / "auto_tickets_2026-10-02.txt").write_text("explicit --date run")
    state = {"open_slips": [_slip("2026-10-02")], "history": []}

    _state, removed = tc.clean_state(state, run_date=RUN_DATE, localdata=tmp_path)

    assert removed == []


def test_a_frozen_future_slip_is_kept(tmp_path):
    (tmp_path / "auto_tickets_2026-10-02.frozen").write_text("09:00")
    state = {"open_slips": [_slip("2026-10-02")], "history": []}

    _state, removed = tc.clean_state(state, run_date=RUN_DATE, localdata=tmp_path)

    assert removed == []


def test_a_settled_future_slip_is_kept(tmp_path):
    """Real money resolved against it; never delete that."""
    state = {"open_slips": [_slip("2026-10-02", result="W", won=True)],
             "history": []}

    _state, removed = tc.clean_state(state, run_date=RUN_DATE, localdata=tmp_path)

    assert removed == []


def test_a_slip_already_in_history_is_kept(tmp_path):
    state = {"open_slips": [_slip("2026-10-02")],
             "history": [{"date": "2026-10-02"}]}

    _state, removed = tc.clean_state(state, run_date=RUN_DATE, localdata=tmp_path)

    assert removed == []


def test_the_bank_total_is_not_rewritten(tmp_path):
    state = {"bank": 184.46, "open_slips": [_slip("2026-10-02")], "history": []}

    state, _removed = tc.clean_state(state, run_date=RUN_DATE, localdata=tmp_path)

    assert state["bank"] == 184.46, \
        "committed capital is derived from open_slips, not stored"


def test_only_the_bad_draft_slice_rows_are_dropped():
    lines = [
        json.dumps({"date": "2026-09-29", "src": "slip", "match": "keep me"}),
        json.dumps({"date": "2026-10-02", "src": "slip", "match": "Belgium vs Turkey"}),
        json.dumps({"date": "2026-10-02", "src": "slip", "match": "Hungary vs Georgia"}),
        json.dumps({"date": "2026-10-02", "src": "plan", "match": "not a slip row"}),
    ]

    keep, dropped = tc.clean_slice_ledger_lines(lines, {"2026-10-02"})

    assert dropped == 2
    assert len(keep) == 2
    assert "keep me" in keep[0] and "not a slip row" in keep[1]


def test_unparseable_history_is_never_discarded():
    keep, dropped = tc.clean_slice_ledger_lines(["{not json"], {"2026-10-02"})

    assert dropped == 0 and len(keep) == 1
