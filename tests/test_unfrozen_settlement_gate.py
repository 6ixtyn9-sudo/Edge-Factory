"""Only a card that reached its freeze can be a placed bet.

2026-10-26, the incident these rules exist for. The enhancement card was
drafted at 00:00 SAST by the 22:00Z run (target rolls to the new date, hour is
below ``FREEZE_HOUR``), so nothing was frozen. Both legs then finished
overnight and the 06:42 run settled the draft as a bet:

    settled 2026-10-26 acca @2.11 legs=['win', 'loss']: bank 39.0%

The operator never placed it ("i only placed main accas, i did not place enh"),
and the freeze book has no 2026-10-26 entry to this day. Three rules follow:

1. ``settle_open_slips`` settles only a FROZEN slip (freeze book, or the legacy
   ``.frozen`` marker for that lane). An unfrozen slip stays open and its date
   is named on every run, so a missed freeze is visible rather than becoming a
   phantom settlement.
2. No card leg may kick off before the card's own freeze hour: at 00:00 the
   legs are not final, so they cannot be staked (``freeze_floor``).
3. The NO BET line counts FIXTURES, not quotes — sixteen books pricing one
   match was reported as "16 eligible legs", which read like sixteen chances
   and was not even two.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402

DAY = "2026-10-26"
FROZEN_AT = datetime(2026, 10, 26, 9, 0, tzinfo=at.TZ)


@pytest.fixture(autouse=True)
def _sandbox_state(tmp_path, monkeypatch):
    """No test may touch the live lane state, bank or freeze book.

    ``ENHANCEMENT_LANE`` is bound at import time, so a test that merely patches
    STATE_FILE/LOCALDATA and then settles ``lane=ENHANCEMENT_LANE`` still writes
    the REAL localdata/enhancement_tickets_state.json. Point the lane itself at
    the temp dir. (Learned the hard way: a run of this file overwrote the live
    enhancement state.)
    """
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "BUCKET_PNL_FILE", tmp_path / "bucket_pnl.json")
    monkeypatch.setattr(at, "ENHANCEMENT_LANE", at.Lane(
        tmp_path / "enhancement_tickets_state.json", "autobets_enh_tickets",
        "ENHANCEMENT TICKETS (ROLLING)", at.STAKE_FRAC))
    at.SETTLED_KEY_NAMES.clear()
    yield
    at.SETTLED_KEY_NAMES.clear()


def _leg(home="Santa Clara", away="Benfica"):
    return {"match": f"{home} vs {away}", "pick": "over", "odds": 2.11,
            "label": "Match Over 2.5 Goals", "market": "match_over_25",
            "result": None}


def _state(*, frozen):
    st = at.fresh_state()
    st["bank"] = 43.7309
    st["base_pct"] = 100.0
    st["open_slips"] = [{"date": DAY, "staked_pct": 4.6937, "accas": [{
        "odds": 2.11, "stake_pct": 4.6937, "results": [None], "won": None,
        "legs": [_leg()]}]}]
    if frozen:
        at.record_freeze(st, DAY, FROZEN_AT)
    return st


def _scores():
    # the same fold the settlement snapshot uses
    return {(DAY, h, a): (1, 0)
            for h, a in at._result_write_keys("Santa Clara", "Benfica")}


def test_an_unfrozen_draft_is_never_settled(capsys):
    st = _state(frozen=False)
    before = st["bank"]
    lines = at.settle_open_slips(st, {}, archives=[], entries_by_date={},
                                 scores=_scores())
    assert st["bank"] == before          # no stake left the bank
    assert st["history"] == []           # no bet-day booked
    assert [s["date"] for s in st["open_slips"]] == [DAY]   # still on the book
    assert st["open_slips"][0]["accas"][0]["won"] is None
    assert any("never frozen" in line for line in lines)
    # and the withholding is on the run log, not only in the state
    assert f"settlement_unfrozen_withheld={DAY}" in capsys.readouterr().err


def test_the_same_slip_settles_once_it_is_frozen():
    st = _state(frozen=True)
    at.settle_open_slips(st, {}, archives=[], entries_by_date={}, scores=_scores())
    assert st["open_slips"] == []
    assert len(st["history"]) == 1
    assert st["history"][0]["accas"][0]["won"] is False     # 1-0 is Under 2.5


def test_a_legacy_frozen_marker_on_disk_also_counts():
    marker = at.LOCALDATA / f"autobets_enh_tickets_{DAY}.frozen"
    marker.write_text("2026-10-26T09:00:00+02:00")
    st = _state(frozen=False)
    at.settle_open_slips(st, {}, archives=[], entries_by_date={},
                         lane=at.ENHANCEMENT_LANE, scores=_scores())
    assert st["open_slips"] == [] and len(st["history"]) == 1


def test_the_withholding_is_printed_on_every_clean_run_too(capsys):
    at.settle_open_slips(_state(frozen=True), {}, archives=[], entries_by_date={},
                         scores=_scores())
    assert "settlement_unfrozen_withheld=none" in capsys.readouterr().err


# ---------------- rule 2: the freeze floor ----------------

def test_no_floor_once_the_freeze_hour_has_passed():
    after = datetime(2026, 10, 26, 10, 0, tzinfo=at.TZ)
    assert at.freeze_floor(DAY, after) is None


def test_the_floor_is_the_freeze_hour_on_the_target_date():
    before = datetime(2026, 10, 26, 0, 0, tzinfo=at.TZ)
    assert at.freeze_floor(DAY, before) == FROZEN_AT


def test_a_historical_target_has_no_floor():
    later = datetime(2026, 10, 27, 0, 30, tzinfo=at.TZ)
    assert at.freeze_floor(DAY, later) is None


def test_a_kickoff_before_the_freeze_hour_is_dropped_not_merely_started():
    """00:00 build, 02:00 SAST kickoff: the card is not final at kickoff."""
    now = datetime(2026, 10, 26, 0, 30, tzinfo=at.TZ)
    leg = {"match": "Alpha vs Beta", "pick": "home",
           "row": {"kickoff_utc": "2026-10-26T00:00:00+00:00"}}  # 02:00 SAST
    kept, drops = at.live_kickoff_guard([leg], now,
                                        freeze_floor_at=at.freeze_floor(DAY, now))
    assert kept == []
    assert drops[at.KO_SKIP_PRE_FREEZE] == ["Alpha vs Beta"]
    assert at.KO_SKIP_STARTED not in drops


def test_a_kickoff_after_the_freeze_hour_rides():
    now = datetime(2026, 10, 26, 0, 30, tzinfo=at.TZ)
    leg = {"match": "Gamma vs Delta", "pick": "home",
           "row": {"kickoff_utc": "2026-10-26T18:00:00+00:00"}}  # 20:00 SAST
    kept, drops = at.live_kickoff_guard([leg], now,
                                        freeze_floor_at=at.freeze_floor(DAY, now))
    assert kept == [leg] and drops == {}


def test_the_floor_never_shadows_a_started_leg_after_the_freeze():
    now = datetime(2026, 10, 26, 12, 0, tzinfo=at.TZ)
    leg = {"match": "Epsilon vs Zeta", "pick": "home",
           "row": {"kickoff_utc": "2026-10-26T09:00:00+00:00"}}  # 11:00 SAST
    kept, drops = at.live_kickoff_guard([leg], now,
                                        freeze_floor_at=at.freeze_floor(DAY, now))
    assert kept == [] and drops[at.KO_SKIP_STARTED] == ["Epsilon vs Zeta"]


# ---------------- rule 3: fixtures, not quotes ----------------

def test_the_no_bet_line_counts_fixtures_not_books():
    """Sixteen books quoting one match is one chance, not sixteen."""
    legs = [dict(_leg(), verdict="fire", fixture_key=[DAY, "Santa Clara", "Benfica"])
            for _ in range(16)]
    legs.append(dict(_leg("Other", "Match"), verdict="fire",
                     fixture_key=[DAY, "Other", "Match"]))
    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, [], FROZEN_AT,
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0)
    assert "2 eligible fixtures (17 priced quotes)" in txt


def test_one_fixture_from_sixteen_quotes_is_one_eligible_fixture():
    legs = [dict(_leg(), verdict="fire", fixture_key=[DAY, "Santa Clara", "Benfica"])
            for _ in range(16)]
    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, [], FROZEN_AT,
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0)
    assert "NO BET — only 1 eligible fixture (16 priced quotes), need 2 for an acca" in txt


def test_quotes_without_a_fixture_key_fall_back_to_the_match_text():
    legs = [{"match": "Santa Clara vs Benfica", "verdict": "fire"},
            {"match": "Santa Clara vs Benfica", "verdict": "fire"},
            {"match": "Porto vs Braga", "verdict": "fire"}]
    assert at._distinct_fixture_count(legs) == 2


# ---------------- the deliberate undo: a settled unplaced card ----------------

def _settled_state():
    """The 2026-10-26 shape: one settled day booked, bank already reduced."""
    st = at.fresh_state()
    st["base_pct"] = 100.0
    st["bank"] = 39.0372
    st["open_slips"] = []
    st["history"] = [
        {"date": "2026-10-24", "staked_pct": 13.1522, "returned_pct": 0.0,
         "bank_pct": 39.4565, "close_pct": 39.4565,
         "accas": [{"odds": 2.0, "won": False}]},
        {"date": "2026-10-25", "staked_pct": 9.864, "returned_pct": 14.1384,
         "bank_pct": 43.7309, "close_pct": 37.5495,
         "accas": [{"odds": 1.88, "won": True}]},
        {"date": "2026-10-26", "staked_pct": 4.6937, "returned_pct": 0.0,
         "bank_pct": 39.0372, "close_pct": 32.8558,
         "accas": [{"odds": 2.11, "won": False}]},
    ]
    return st


def _write_receipt(tmp_path, st, **overrides):
    row = [h for h in st["history"] if h["date"] == DAY][0]
    receipt = {
        "schema": 1,
        "action": "reconcile_unplaced_enhancement_settlement",
        "lane": "enh",
        "date": DAY,
        "confirmed_none_placed": True,
        "operator_confirmation": "i only placed main accas, i did not place enh.",
        "approved_at": "2026-10-26T07:07:47+02:00",
        "staked_pct": row["staked_pct"],
        "returned_pct": row["returned_pct"],
        "bank_before_reconcile": st["bank"],
        "bank_after_reconcile": round(st["bank"] - (row["returned_pct"] - row["staked_pct"]), 4),
        "history_row_sha256": at._history_row_digest(row),
    }
    receipt.update(overrides)
    path = tmp_path / f"autobets_enh_tickets_{DAY}_settled_reconciliation.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    return path


def test_a_confirmed_unplaced_settlement_is_reversed(tmp_path):
    st = _settled_state()
    _write_receipt(tmp_path, st)
    assert at._apply_settled_enhancement_reconciliations(st, tmp_path) is True
    assert [h["date"] for h in st["history"]] == ["2026-10-24", "2026-10-25"]
    assert st["bank"] == pytest.approx(43.7309)      # exactly the reversed stake
    # The surviving bet-day keeps its stored close: closes are day-level
    # evidence and are never re-derived from a later bank (the 01:11 regrade
    # moved the bank, not the 10-25 close). This is the pre-incident state.
    assert st["history"][-1]["close_pct"] == pytest.approx(37.5495)
    audit = st["settled_enhancement_reconciliations"][DAY]
    assert audit["bank_before_pct"] == pytest.approx(39.0372)
    assert audit["removed"]["staked_pct"] == pytest.approx(4.6937)


def test_the_same_receipt_never_applies_twice(tmp_path):
    st = _settled_state()
    _write_receipt(tmp_path, st)
    at._apply_settled_enhancement_reconciliations(st, tmp_path)
    bank = st["bank"]
    assert at._apply_settled_enhancement_reconciliations(st, tmp_path) is False
    assert st["bank"] == bank and len(st["history"]) == 2


def test_a_changed_row_refuses_the_reversal(tmp_path):
    st = _settled_state()
    path = _write_receipt(tmp_path, st)
    st["history"][-1]["staked_pct"] = 9.0          # row moved since approval
    with pytest.raises(ValueError, match="settled row changed"):
        at._apply_settled_enhancement_reconciliations(st, tmp_path)
    assert st["bank"] == pytest.approx(39.0372)    # nothing adjusted
    assert path.exists()


def test_a_documented_bank_that_does_not_match_refuses(tmp_path):
    st = _settled_state()
    _write_receipt(tmp_path, st, bank_after_reconcile=40.0)
    with pytest.raises(ValueError, match="reversal lands at"):
        at._apply_settled_enhancement_reconciliations(st, tmp_path)
    assert len(st["history"]) == 3


def test_a_missing_confirmation_refuses(tmp_path):
    st = _settled_state()
    _write_receipt(tmp_path, st, confirmed_none_placed=False)
    with pytest.raises(ValueError, match="invalid settled-enhancement reconciliation"):
        at._apply_settled_enhancement_reconciliations(st, tmp_path)
    assert st["bank"] == pytest.approx(39.0372)


def test_a_receipt_for_a_date_without_a_settled_row_refuses(tmp_path):
    st = _settled_state()
    path = _write_receipt(tmp_path, st)
    st["history"] = [h for h in st["history"] if h["date"] != DAY]
    with pytest.raises(ValueError, match="0 settled row"):
        at._apply_settled_enhancement_reconciliations(st, tmp_path)
    assert path.exists() and st["bank"] == pytest.approx(39.0372)


def test_the_withdrawal_receipt_still_refuses_settled_history(tmp_path):
    """The unplaced-card receipt cannot undo a settlement; that is this path."""
    st = _settled_state()
    (tmp_path / f"autobets_enh_tickets_{DAY}_reset.json").write_text(json.dumps({
        "schema": 1, "action": "reset_unplaced_enhancement", "lane": "enh",
        "date": DAY, "confirmed_none_placed": True,
        "approved_at": "2026-10-26T07:00:00+02:00",
        "withdrawn_ticket_sha256": "0" * 64,
    }))
    with pytest.raises(ValueError, match="reconciliation required"):
        at._apply_unplaced_enhancement_resets(st, tmp_path)
