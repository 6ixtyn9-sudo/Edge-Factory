"""Tests for WhatsApp notify anti-spam + heartbeat logic (offline, no dispatch)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "notify_whatsapp.py"
spec = importlib.util.spec_from_file_location("notify_whatsapp", SCRIPT)
notify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notify)


DATE = "2026-08-02"
CSKA = {"match": "cska sofia vs dunav ruse", "date": DATE, "market": "1x2",
        "bucket": "WATCHLIST_NO_ODDS", "home": "CSKA Sofia", "away": "Dunav Ruse"}
NOAH = {"match": "noah vs syunik", "date": DATE, "market": "1x2",
        "bucket": "WATCHLIST_UNKNOWN_CTX", "home": "Noah", "away": "Syunik"}


def _keys(*picks, date=DATE):
    return {notify._build_match_dedupe_key(p, date) for p in picks}


def test_discovery_suppressed_when_already_messaged_as_pick():
    # CSKA was in the morning bet-alert (main sent ledger) but the discovery
    # ledger was lost (cache eviction / stale committed copy): must NOT re-alert.
    main_sent = _keys(CSKA)
    out = notify._filter_discoveries([CSKA, NOAH], DATE, set(), main_sent)
    assert out == [NOAH] or (len(out) == 1 and out[0] is NOAH)


def test_discovery_suppressed_by_own_ledger():
    own = _keys(NOAH)
    out = notify._filter_discoveries([CSKA, NOAH], DATE, own, set())
    assert len(out) == 1 and out[0] is CSKA


def test_discovery_passes_when_nothing_seen():
    out = notify._filter_discoveries([CSKA, NOAH], DATE, set(), set())
    assert len(out) == 2


def test_heartbeat_marker_roundtrip():
    keys = set()
    assert notify._heartbeat_pending(keys, DATE)
    keys.add(notify._heartbeat_key(DATE))
    assert not notify._heartbeat_pending(keys, DATE)
    # heartbeat for a DIFFERENT day is still pending (1/day semantics)
    assert notify._heartbeat_pending(keys, "2026-08-03")


def test_heartbeat_marker_never_matches_pick_keys():
    # a real pick key must never accidentally suppress the heartbeat and vice versa
    pkey = notify._build_match_dedupe_key(CSKA, DATE)
    hkey = notify._heartbeat_key(DATE)
    assert pkey != hkey and not pkey.startswith(notify.HEARTBEAT_MARKER_PREFIX)


def test_dedupe_key_is_stable_identity():
    # rule/odds/prob churn between regenerations must not change the dedupe key
    a = dict(CSKA, rule="3way-unanimous avg_p>=65", odds=1.31, avg_p=70)
    b = dict(CSKA, rule="2way-unanimous avg_p>=65", odds=1.35, avg_p=68)
    assert notify._build_match_dedupe_key(a, DATE) == notify._build_match_dedupe_key(b, DATE)


# --- Addendum 25.1: chunk dispatch semantics (committed, not battery-only) ----

_KW = dict(meta_token=None, meta_phone_id=None, meta_recipient=None, meta_template=None,
           twilio_sid=None, twilio_token=None, twilio_number=None,
           callmebot_key=None, callmebot_phone=None)


def test_shadow_chunks_abort_on_failure(monkeypatch):
    attempts = []
    monkeypatch.setattr(notify, "_dispatch_message",
                        lambda **kw: (attempts.append(kw["message_text"]), len(attempts) < 2)[1])
    ok = notify._dispatch_shadow_chunks(["c1", "c2", "c3"], force=False, **_KW)
    assert ok is False
    assert len(attempts) == 2  # c3 never attempted


def test_shadow_chunks_force_attempts_all_but_failure_returns_false(monkeypatch):
    attempts = []
    monkeypatch.setattr(notify, "_dispatch_message",
                        lambda **kw: (attempts.append(kw["message_text"]), False)[1])
    ok = notify._dispatch_shadow_chunks(["c1", "c2", "c3"], force=True, **_KW)
    assert ok is False          # Addendum 25.1: force cannot fake success
    assert len(attempts) == 3   # but diagnostics attempt everything


def test_shadow_chunks_success_requires_every_chunk(monkeypatch):
    monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: True)
    assert notify._dispatch_shadow_chunks(["c1", "c2"], force=False, **_KW) is True
    seq = iter([True, False, True])
    monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: next(seq))
    assert notify._dispatch_shadow_chunks(["c1", "c2", "c3"], force=True, **_KW) is False


# --- Addendum 25.1.1: hermetic end-to-end dispatch semantics ------------------
#
# Receipt-backed fixes: e2e notify tests must NEVER depend on a real .env or
# real credentials (the Addendum 25.1 versions passed on the operator Mac only
# because live CallMeBot credentials existed there; a clean no-.env checkout
# short-circuits main() at the credential gate — reproduced: 1 failed, 133
# passed). They must NEVER write ledgers into the repo's real localdata (the
# old tests created/unlinked shadow_sent_ledger_2099-*.json there).
# And they must pin the GLOBAL force semantics: --force is a ledger-READ
# bypass only; any failed dispatch means non-zero exit + no ledger write, in
# EVERY message family.


def _mk(date, m, b):
    return {"date": date, "match": m, "home": m.split(" vs ")[0], "away": m.split(" vs ")[1],
            "pick": "home", "bucket": b, "avg_p": 80.0, "odds": 1.5, "market": "1x2",
            "display_rule": "2way-unanimous avg_p>=70"}


def _shadow_rows(date):
    return [_mk(date, "T1 vs T2", "SKIPPED_VETO"), _mk(date, "T3 vs T4", "WATCHLIST_UNKNOWN_CTX")]


def _picks_file(tmp_path, rows):
    fp = tmp_path / "picks.json"
    fp.write_text(json.dumps(rows))
    return fp


def _wire_e2e(monkeypatch, tmp_path, dispatch):
    """Hermetic e2e rig. Dummy credentials via env — enough to pass the
    credential gate on ANY machine, with or without a real .env; delivery
    itself is stubbed, so the network is never touched. Ledgers are redirected
    to tmp_path / "localdata" — never the repo's real localdata. `dispatch`
    is a bool or a callable(message_text) -> bool. Returns the list of
    attempted message texts."""
    monkeypatch.setenv("CALLMEBOT_APIKEY", "dummy-key")
    monkeypatch.setenv("CALLMEBOT_PHONE", "27000000000")
    monkeypatch.setenv("EDGE_FACTORY_SHADOW_CHUNK_DELAY", "0")  # keep the suite instant
    monkeypatch.setattr(notify, "LOCALDATA", tmp_path / "localdata")
    sent = []

    def fake_dispatch(**kw):
        sent.append(kw["message_text"])
        return dispatch(kw["message_text"]) if callable(dispatch) else bool(dispatch)

    monkeypatch.setattr(notify, "_dispatch_message", fake_dispatch)
    return sent


def _run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["notify_whatsapp.py", *argv])
    return notify.main()


def test_shadow_ledger_barrier_end_to_end(monkeypatch, tmp_path):
    """Hermetic e2e: (b) forced TOTAL shadow failure ⇒ non-zero main return +
    no shadow ledger; (e) successful recovery writes ONLY the intended
    ledger; rerun without force is deduped silent."""
    date = "2099-03-03"
    ld = tmp_path / "localdata"
    shadow_ledger = ld / f"shadow_sent_ledger_{date}.json"
    fp = _picks_file(tmp_path, _shadow_rows(date))
    state = {"ok": False}
    sent = _wire_e2e(monkeypatch, tmp_path, lambda _msg: state["ok"])

    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force")
    assert rc != 0                                  # 25.1.1: force cannot fake success
    assert any("Shadow Slate" in m for m in sent)   # chunks genuinely attempted
    assert not shadow_ledger.exists()               # total failure: nothing deduped

    state["ok"] = True                              # recovery: whole slate re-sends
    sent.clear()
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force")
    assert rc == 0
    assert shadow_ledger.exists()
    assert len(json.loads(shadow_ledger.read_text())) == 2
    # (e) only the intended ledger was written — no phantom ledgers
    assert not (ld / f"sent_ledger_{date}.json").exists()
    assert not (ld / f"discovery_sent_ledger_{date}.json").exists()

    sent.clear()                                    # third run, no force: deduped silent
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date)
    assert rc == 0
    assert not any("Shadow Slate" in m for m in sent)


def test_force_main_failure_writes_no_ledger(monkeypatch, tmp_path):
    """(c, main family) forced failed bet-alert ⇒ non-zero + no main ledger."""
    date = "2099-03-05"
    ld = tmp_path / "localdata"
    fp = _picks_file(tmp_path, [_mk(date, "M1 vs M2", notify.BUCKET_CLEAN)])
    sent = _wire_e2e(monkeypatch, tmp_path, False)
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force")
    assert rc != 0
    assert sent                                     # the message was attempted
    assert not (ld / f"sent_ledger_{date}.json").exists()


def test_force_discovery_failure_writes_no_ledger(monkeypatch, tmp_path):
    """(c, discovery family) forced failed discovery ⇒ non-zero + no discovery
    ledger. Shadow family killed to isolate the discovery path."""
    date = "2099-03-06"
    ld = tmp_path / "localdata"
    monkeypatch.setenv("EDGE_FACTORY_NOTIFY_DISCOVERY_WATCHLIST", "1")
    monkeypatch.setenv("EDGE_FACTORY_NOTIFY_SHADOW", "0")
    fp = _picks_file(tmp_path, [_mk(date, "D1 vs D2", "WATCHLIST_NO_ODDS")])
    _wire_e2e(monkeypatch, tmp_path, False)
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force")
    assert rc != 0
    assert not (ld / f"discovery_sent_ledger_{date}.json").exists()
    assert not (ld / f"sent_ledger_{date}.json").exists()


def test_force_heartbeat_failure_writes_no_marker(monkeypatch, tmp_path):
    """(c, heartbeat family) forced failed heartbeat ⇒ non-zero + no marker in
    the main ledger."""
    date = "2099-03-07"
    ld = tmp_path / "localdata"
    fp = _picks_file(tmp_path, [])                   # empty slate ⇒ heartbeat intended
    _wire_e2e(monkeypatch, tmp_path, False)
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force", "--heartbeat")
    assert rc != 0
    assert not (ld / f"sent_ledger_{date}.json").exists()


def test_successful_family_does_not_mask_failed_family(monkeypatch, tmp_path):
    """(f) main OK + shadow fail ⇒ non-zero exit; main ledger written, shadow
    ledger NOT written (whole shadow slate retries next run)."""
    date = "2099-03-08"
    ld = tmp_path / "localdata"
    rows = [_mk(date, "M1 vs M2", notify.BUCKET_CLEAN)] + _shadow_rows(date)
    fp = _picks_file(tmp_path, rows)
    _wire_e2e(monkeypatch, tmp_path, lambda msg: "Shadow Slate" not in msg)
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force")
    assert rc != 0
    main_ledger = ld / f"sent_ledger_{date}.json"
    assert main_ledger.exists() and len(json.loads(main_ledger.read_text())) == 1
    assert not (ld / f"shadow_sent_ledger_{date}.json").exists()


# --- Addendum 25.2: inter-chunk spacing + ack-rejection e2e --------------------

_KW_CMB = dict(_KW, callmebot_key="k", callmebot_phone="p")


def test_shadow_chunks_spacing_between_callmebot_chunks(monkeypatch):
    sleeps = []
    monkeypatch.setattr(notify.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setenv("EDGE_FACTORY_SHADOW_CHUNK_DELAY", "2.5")
    monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: True)
    assert notify._dispatch_shadow_chunks(["c1", "c2", "c3"], force=False, **_KW_CMB) is True
    assert sleeps == [2.5, 2.5]  # between chunks only — never after the last


def test_shadow_chunks_spacing_defaults_to_4s(monkeypatch):
    sleeps = []
    monkeypatch.setattr(notify.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.delenv("EDGE_FACTORY_SHADOW_CHUNK_DELAY", raising=False)
    monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: True)
    assert notify._dispatch_shadow_chunks(["c1", "c2"], force=False, **_KW_CMB) is True
    assert sleeps == [4.0]


def test_shadow_chunks_no_spacing_without_callmebot_or_when_disabled(monkeypatch):
    sleeps = []
    monkeypatch.setattr(notify.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: True)
    notify._dispatch_shadow_chunks(["c1", "c2"], force=False, **_KW)   # no CallMeBot configured
    assert sleeps == []
    monkeypatch.setenv("EDGE_FACTORY_SHADOW_CHUNK_DELAY", "0")
    notify._dispatch_shadow_chunks(["c1", "c2"], force=False, **_KW_CMB)
    assert sleeps == []


class _ErrResp:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return b"<b>ERROR</b>: apikey invalid"


def test_callmebot_200_error_body_fails_dispatch_end_to_end(monkeypatch, tmp_path):
    """25.2: HTTP-200 with an error-class ack body ⇒ dispatch failure:
    non-zero exit, NO shadow ledger (the 2026-08-04 incident class)."""
    date = "2099-03-09"
    ld = tmp_path / "localdata"
    fp = _picks_file(tmp_path, _shadow_rows(date))
    monkeypatch.setenv("CALLMEBOT_APIKEY", "dummy-key")
    monkeypatch.setenv("CALLMEBOT_PHONE", "27000000000")
    monkeypatch.setenv("EDGE_FACTORY_SHADOW_CHUNK_DELAY", "0")
    monkeypatch.setattr(notify, "LOCALDATA", ld)
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: _ErrResp())
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force")
    assert rc != 0
    assert not (ld / f"shadow_sent_ledger_{date}.json").exists()


def test_shadow_kill_switch_blocks_dispatch(monkeypatch, tmp_path):
    """(g) kill-switch intact — hermetically: nothing intended ⇒ silence exit 0."""
    date = "2099-03-04"
    ld = tmp_path / "localdata"
    fp = _picks_file(tmp_path, _shadow_rows(date))
    monkeypatch.setenv("EDGE_FACTORY_NOTIFY_SHADOW", "0")
    sent = _wire_e2e(monkeypatch, tmp_path, True)
    rc = _run(monkeypatch, "--picks", str(fp), "--date", date, "--force")
    assert rc == 0
    assert not any("Shadow Slate" in m for m in sent)
    assert not (ld / f"shadow_sent_ledger_{date}.json").exists()
