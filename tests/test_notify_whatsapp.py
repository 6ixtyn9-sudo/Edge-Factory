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


def _shadow_e2e_picks(tmp_path, date):
    fp = tmp_path / "picks.json"

    def mk(m, b):
        return {"date": date, "match": m, "home": m.split(" vs ")[0], "away": m.split(" vs ")[1],
                "pick": "home", "bucket": b, "avg_p": 80.0, "odds": 1.5, "market": "1x2",
                "display_rule": "2way-unanimous avg_p>=70"}
    fp.write_text(json.dumps([mk("T1 vs T2", "SKIPPED_VETO"), mk("T3 vs T4", "WATCHLIST_UNKNOWN_CTX")]))
    return fp


def test_shadow_ledger_barrier_end_to_end(monkeypatch, tmp_path):
    date = "2099-03-03"
    ledger = notify.LOCALDATA / f"whatsapp_shadow_sent_ledger_{date}.json"
    try:
        ledger.unlink(missing_ok=True)
        fp = _shadow_e2e_picks(tmp_path, date)
        monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: False)
        monkeypatch.setattr(sys, "argv", ["notify_whatsapp.py", "--picks", str(fp), "--date", date, "--force"])
        assert notify.main() == 0
        assert not ledger.exists()  # total failure: nothing deduped, whole slate re-sends next run
        monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: True)
        assert notify.main() == 0
        assert ledger.exists()
        assert len(json.loads(ledger.read_text())) == 2
        monkeypatch.setattr(sys, "argv", ["notify_whatsapp.py", "--picks", str(fp), "--date", date])
        sent = []
        monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: (sent.append(kw), True)[1])
        assert notify.main() == 0
        assert not any("Shadow Slate" in str(k.get("message_text")) for k in sent)
    finally:
        ledger.unlink(missing_ok=True)


def test_shadow_kill_switch_blocks_dispatch(monkeypatch, tmp_path):
    date = "2099-03-04"
    ledger = notify.LOCALDATA / f"whatsapp_shadow_sent_ledger_{date}.json"
    try:
        ledger.unlink(missing_ok=True)
        fp = _shadow_e2e_picks(tmp_path, date)
        sent = []
        monkeypatch.setattr(notify, "_dispatch_message", lambda **kw: (sent.append(kw), True)[1])
        monkeypatch.setenv("EDGE_FACTORY_NOTIFY_SHADOW", "0")
        monkeypatch.setattr(sys, "argv", ["notify_whatsapp.py", "--picks", str(fp), "--date", date, "--force"])
        assert notify.main() == 0
        assert not any("Shadow Slate" in str(k.get("message_text")) for k in sent)
    finally:
        monkeypatch.delenv("EDGE_FACTORY_NOTIFY_SHADOW", raising=False)
        ledger.unlink(missing_ok=True)
