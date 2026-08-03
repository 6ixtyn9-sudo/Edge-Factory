"""Tests for WhatsApp notify anti-spam + heartbeat logic (offline, no dispatch)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

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
