"""OP-01 T2 — the daily freeze lock lives in ticket state, write-once.

Contract pinned here:

1. write-once   — once a date is in ``frozen_by_date`` it can never be
                  rewritten, by any path, including ``--force``;
2. compat       — a legacy ``localdata/auto_tickets_<date>.frozen`` sidecar
                  still locks the date on read, is adopted (not re-timed) on
                  first state write, and is never deleted;
3. no new files — a freeze no longer creates a sidecar;
4. ordering     — the freeze entry is written in the SAME state persist as the
                  slip, and no later phase rewrites it;
5. footer       — the human artifact ends with ``FROZEN AT HH:MM - FINAL``.
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402


def _clock(y, m, d, hh, mi):
    class _C(at.datetime):
        @classmethod
        def now(cls, tz=None):
            return at.datetime(y, m, d, hh, mi, tzinfo=tz or at.TZ)
    return _C


def _slate(day="2026-09-06"):
    rows = []
    for home, away, ko, odds in [
            ("Heart of Midlothian", "Dundee", f"{day}T16:00:00+02:00", 1.47),
            ("Gresford Athletic", "Mold Alexandra", f"{day} 15:30:00", 1.45),
            ("Zrinjski", "Siroki Brijeg", f"{day}T20:15:00+02:00", 1.26),
            ("Rudes", "HNK Hajduk Split", f"{day}T16:00:00+02:00", 1.29),
    ]:
        rows.append({"date": day, "home": home, "away": away, "kickoff": ko,
                     "league": "x", "bucket": "CERTIFIED_CLEAN", "market": "1x2",
                     "pick": "home", "avg_p": 70.0, "odds": odds,
                     "quarantine": "none", "odds_source": "bzzoiro_odds",
                     "price_push_eligible": True})
    return rows


@pytest.fixture
def lane(tmp_path, monkeypatch):
    """A sandboxed ticket lane whose state and slips live in tmp_path."""
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "tickets_state.json")
    monkeypatch.setattr(at, "BUCKET_PNL_FILE", tmp_path / "bucket_pnl.json")
    monkeypatch.setattr(at, "SLICE_LEDGER_FILENAME", "slice-ledger.jsonl")
    monkeypatch.setattr(at, "SLICE_TRIPWIRE_FILENAME", "slice-tripwire.json")
    (tmp_path / "picks_today.json").write_text(json.dumps(_slate()))
    return tmp_path


DAY = "2026-09-06"


def _run(day=DAY, force=False):
    st = at.fresh_state()
    assert at.cmd_today(SimpleNamespace(date=day, force=force), st) == 0
    return st


# ---------------- 1. write-once ----------------

def test_freeze_entry_is_write_once_even_against_force(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    st = _run()
    first = dict(at.frozen_entry(st, DAY))
    assert first["final"] is True and first["lock_source"] == "state"

    # A later run on the same date, even at a different time, cannot re-time it.
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 18, 45))
    assert at.record_freeze(st, DAY, at.datetime(2026, 9, 6, 18, 45, tzinfo=at.TZ)) == first
    assert at.frozen_entry(st, DAY) == first

    # --force rebuilds the card but must never rewrite the lock.
    assert at.cmd_today(SimpleNamespace(date=DAY, force=True), st) == 0
    assert at.frozen_entry(st, DAY) == first
    on_disk = json.loads((lane / "tickets_state.json").read_text())
    assert on_disk["frozen_by_date"][DAY] == first


def test_frozen_date_is_never_rebuilt_on_a_later_run(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    st = _run()
    slip = lane / f"auto_tickets_{DAY}.txt"
    before = slip.read_text()
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 21, 0))
    assert at.cmd_today(SimpleNamespace(date=DAY, force=False), st) == 0
    assert slip.read_text() == before          # re-print, never a rewrite


def test_force_no_bet_supersedes_card_without_reprinting_its_prices(lane, monkeypatch, capsys):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    st = _run()
    slip = lane / f"auto_tickets_{DAY}.txt"
    before = slip.read_text()
    frozen = dict(at.frozen_entry(st, DAY))

    # Simulate the corrected source gate rejecting every stale/unverified
    # price. The force recut may write state metadata, but never the frozen
    # slip or its write-once timestamp.
    monkeypatch.setattr(at, "playable_legs", lambda *args, **kwargs: [])
    assert at.cmd_today(SimpleNamespace(date=DAY, force=True), st) == 0
    assert slip.read_text() == before
    assert at.frozen_entry(st, DAY) == frozen
    assert at.superseded_entry(st, DAY)["result"] == "NO BET"

    capsys.readouterr()
    assert at.cmd_today(SimpleNamespace(date=DAY, force=False), st) == 0
    output = capsys.readouterr().out
    assert "TICKETS SUPERSEDED" in output
    assert "do not place the superseded selections" in output
    assert "PRICE SUPPLY:" not in output
    assert "REJECTION LEDGER:" not in output
    assert '"rule": "superseded_card_locked"' not in output
    assert "[ACCA #" not in output
    assert "@1.47" not in output


def test_default_ticket_text_uses_the_concise_customer_contract(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    _run()
    text = (lane / f"auto_tickets_{DAY}.txt").read_text()

    assert text.startswith(f"AUTO TICKETS (ROLLING) — {DAY}\n" + "=" * 62)
    assert "PERFORMANCE:" in text
    assert "SELECTION LADDER SLICE" in text
    assert "[ACCA #1] @" in text
    assert "deploying 25% of free bank today" in text
    assert "Bet only what you can afford to lose." in text
    for diagnostic in (
        "P&L TRIPWIRE", "SELECTION LADDER:", "PRICE SUPPLY:",
        "donor capture/match counters", "REJECTION LEDGER:",
        "FORCE RE-CUT", "price:", "unregistered source", "TRIPWIRE-DEMOTED",
    ):
        assert diagnostic not in text


# ---------------- 2./3. legacy compat, no new sidecars ----------------

def test_legacy_marker_file_still_locks_and_is_never_deleted(lane, monkeypatch):
    legacy = lane / f"auto_tickets_{DAY}.frozen"
    legacy.write_text("2026-09-06T09:13:00+02:00")
    st = at.fresh_state()
    assert at.is_frozen(st, DAY) is True
    assert at.frozen_entry(st, DAY) is None     # state book is still empty

    # Adopting it keeps the legacy timestamp rather than minting a new one.
    entry = at.record_freeze(st, DAY, at.datetime(2026, 9, 6, 23, 59, tzinfo=at.TZ))
    assert entry["frozen_at"] == "2026-09-06T09:13:00+02:00"
    assert entry["lock_source"] == "legacy_marker_file"
    assert at.freeze_footer(entry) == "FROZEN AT 09:13 - FINAL"

    # cmd_today honours the legacy lock and leaves the file alone.
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 21, 0))
    (lane / f"auto_tickets_{DAY}.txt").write_text("legacy slip\n")
    assert at.cmd_today(SimpleNamespace(date=DAY, force=False), at.fresh_state()) == 0
    assert legacy.exists()
    assert (lane / f"auto_tickets_{DAY}.txt").read_text() == "legacy slip\n"


def test_freeze_creates_no_new_sidecar_file(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    _run()
    assert not (lane / f"auto_tickets_{DAY}.frozen").exists()
    assert not list(lane.glob("*.frozen"))


def test_writer_source_has_no_frozen_file_write(lane):
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    body = src[src.index("def cmd_today"):src.index("def print_status")]
    assert "frozen.write_text" not in body
    assert ".frozen\"" not in body               # no sidecar path built here


# ---------------- 4. ordering: lock lands with the state persist ----------------

def test_freeze_is_colocated_with_state_persist_and_not_rewritten_later(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    snapshots = []
    real_save = at.save_state

    def spy(st, lane=None):
        snapshots.append((lane, json.loads(json.dumps(
            (st.get("frozen_by_date") or {}), default=str))))
        real_save(st, lane)

    monkeypatch.setattr(at, "save_state", spy)
    st = _run()
    assert snapshots, "cmd_today must persist state"
    # The main lane's own writes are never routed into a lane's state file.
    assert all(save_lane is None for save_lane, _ in snapshots)
    snapshots = [snap for _, snap in snapshots]
    # The very first persist that carries the card already carries the lock...
    locked = [i for i, s in enumerate(snapshots) if DAY in s]
    assert locked, "freeze entry never reached a state write"
    first = snapshots[locked[0]][DAY]
    # ...and every later persist in the run carries it byte-identical.
    for s in snapshots[locked[0]:]:
        assert s[DAY] == first
    # The slip on disk is the last artifact and agrees with the persisted lock.
    assert at.freeze_footer(first) in (lane / f"auto_tickets_{DAY}.txt").read_text()
    assert json.loads((lane / "tickets_state.json").read_text())["frozen_by_date"][DAY] == first


def test_state_write_carries_slip_and_lock_together(lane, monkeypatch):
    """The persist that first contains the lock also contains the open slip —
    a card can never be staked for a date whose lock lands in a later write."""
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    seen = []
    real_save = at.save_state
    monkeypatch.setattr(at, "save_state", lambda st, lane=None: (
        seen.append((bool((st.get("frozen_by_date") or {}).get(DAY)),
                     [s["date"] for s in st.get("open_slips") or []])),
        real_save(st, lane))[-1])
    _run()
    locked = [slips for has, slips in seen if has]
    assert locked and DAY in locked[0]


# ---------------- 5. footer ----------------

def test_slip_footer_is_the_final_line_when_frozen(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    _run()
    txt = (lane / f"auto_tickets_{DAY}.txt").read_text()
    assert txt.rstrip().endswith("FROZEN AT 09:13 - FINAL")
    assert txt.count("FROZEN AT") == 1


def test_draft_slip_has_no_footer(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 7, 5))
    _run()
    txt = (lane / f"auto_tickets_{DAY}.txt").read_text()
    assert "FROZEN AT" not in txt
    assert at.frozen_entry(at.load_state(), DAY) is None


def test_freeze_footer_formats_from_the_recorded_stamp():
    assert at.freeze_footer({"frozen_at": "2026-10-02T06:07:08+02:00"}) == \
        "FROZEN AT 06:07 - FINAL"
    assert at.freeze_footer({"frozen_at": "garbage"}) == "FROZEN AT ??:?? - FINAL"


# ---------------- 6. --force on a frozen date: recut report, never a rewrite ----------------

def test_force_on_a_frozen_date_keeps_the_placed_slip_and_writes_a_recut(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    st = _run()
    slip = lane / f"auto_tickets_{DAY}.txt"
    before_text = slip.read_text()
    before_open = json.loads(json.dumps(st["open_slips"]))
    assert before_open, "the frozen card must be an open slip"

    # Same slate, so a plan exists. The old path replaced the open slip here.
    assert at.cmd_today(SimpleNamespace(date=DAY, force=True), st) == 0
    assert slip.read_text() == before_text
    assert st["open_slips"] == before_open
    recut = (lane / f"auto_tickets_{DAY}_force_recut.txt").read_text()
    assert recut.startswith(f"AUTO TICKETS FORCE RE-CUT — {DAY}")
    assert "The frozen slip was NOT edited" in recut
    assert "[ACCA #1]" in recut
    assert "STAKED on the frozen card, NOT on the re-cut" in recut


def test_an_ordinary_run_after_a_main_recut_shows_the_frozen_card_and_the_notice(lane, monkeypatch, capsys):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    st = _run()
    slip = lane / f"auto_tickets_{DAY}.txt"
    before_text = slip.read_text()
    assert at.cmd_today(SimpleNamespace(date=DAY, force=True), st) == 0
    capsys.readouterr()
    assert at.cmd_today(SimpleNamespace(date=DAY, force=False), st) == 0
    out = capsys.readouterr().out
    assert before_text in out
    assert "SUPERSEDED — a forced re-cut was recorded" in out
    assert f"auto_tickets_{DAY}_force_recut.txt" in out


def test_the_recut_diff_separates_staked_legs_from_the_re_cut():
    frozen = (
        "AUTO TICKETS (ROLLING) — 2026-09-06\n"
        "[ACCA #1] @2.13 — stake 12.5% of capital (12.5% of free bank)\n"
        "   Heart of Midlothian vs Dundee                  HOME  @ 1.47  (stated 70%)\n"
        "   Gresford Athletic vs Mold Alexandra            HOME  @ 1.45  (stated 70%)\n"
        "   [NO BET] Rudes vs HNK Hajduk Split  HOME  @ 1.29 — refused\n"
        "\nFROZEN AT 09:13 - FINAL"
    )
    recut = {
        "Heart of Midlothian vs Dundee HOME": "Heart of Midlothian vs Dundee  HOME @ 1.47",
        "Zrinjski vs Siroki Brijeg HOME": "Zrinjski vs Siroki Brijeg  HOME @ 1.26",
    }
    out = at._recut_diff_lines(frozen, recut)
    assert out[0] == "  STAKED on the frozen card, NOT on the re-cut (1) — still graded as placed:"
    assert "Gresford Athletic vs Mold Alexandra" in out[1]
    assert out[2] == "  ON THE RE-CUT ONLY (1) — not on the frozen card:"
    assert "Zrinjski vs Siroki Brijeg" in out[3]
    assert not any("Rudes" in line for line in out)          # refused legs are not staked
    assert at._recut_diff_lines("", recut) == ["  frozen slip text missing; leg diff not computed"]


def test_real_main_builder_records_replayable_freeze_not_force_or_reprint(lane, monkeypatch):
    import replay_harness as rh
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 9, 13))
    state = _run()
    receipt = at.decision_receipt_path(DAY)
    assert receipt.exists()
    payload = json.loads(receipt.read_text())
    assert payload["status"] == "frozen"
    assert payload["context"]["bank_state"]["bank"] == state["bank"]
    context = payload["context"]
    replayed = at.plan_ticket_decision(context)
    assert at.ticket_card_identity(replayed) == at.ticket_card_identity(payload["plan"])
    assert rh._ledger_ticket_core(state["open_slips"][0]["accas"], "main") == rh._ledger_ticket_core(replayed, "main")
    before = receipt.read_bytes()
    at.cmd_today(SimpleNamespace(date=DAY, force=False), state, settled={})
    at.cmd_today(SimpleNamespace(date=DAY, force=True), state, settled={})
    assert receipt.read_bytes() == before
    # A historical freeze without evidence must not be retroactively invented.
    receipt.unlink()
    at.cmd_today(SimpleNamespace(date=DAY, force=False), state, settled={})
    at.cmd_today(SimpleNamespace(date=DAY, force=True), state, settled={})
    assert not receipt.exists()


def test_main_no_bet_records_empty_decision_without_financial_change(lane, monkeypatch):
    monkeypatch.setattr(at, "datetime", _clock(2026, 9, 6, 8, 0))
    (lane / "picks_today.json").write_text("[]")
    state = at.fresh_state()
    before = json.dumps(state, sort_keys=True)
    at.cmd_today(SimpleNamespace(date=DAY, force=False), state, settled={})
    receipt = json.loads(at.decision_receipt_path(DAY).read_text())
    assert receipt["status"] == "no_bet" and receipt["plan"] == []
    assert json.dumps(state, sort_keys=True) == before
