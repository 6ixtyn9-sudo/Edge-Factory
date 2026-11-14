"""A cached failure must not outlive the condition it described (WO-2).

The probe receipt is named by the date it was asking about, and the pipeline
plans two days ahead. A probe that ran on Monday wrote a receipt for
Wednesday; that receipt then suppressed Wednesday's real probe forever. The
failure cached itself and blocked the observation that would have shown it had
ended. Deleting the file did not help: the next run re-persisted it.

Staleness is judged by when the probe RAN, never by the date it targeted.
"""
from __future__ import annotations

import datetime as dt

import pytest

from edgefactory.sources import betminer as bm

NOW = dt.datetime(2026, 10, 7, 12, 0, tzinfo=dt.timezone.utc)


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    """capture_day is inert without a key; these tests are about the receipt."""
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key-material")


def _receipt(**over):
    base = {"schema": 2, "http_status": 404,
            "probed_at": "2026-10-07T11:00:00+00:00"}
    base.update(over)
    return base


# --- failure receipts expire ---------------------------------------------


def test_fresh_failure_receipt_still_suppresses():
    """The free-tier cap is real; a recent failure must not be re-probed."""
    assert bm._probe_receipt_is_binding(_receipt(), now=NOW) is True


def test_two_day_old_failure_receipt_no_longer_suppresses():
    stale = _receipt(probed_at="2026-10-05T22:22:50+00:00")
    assert bm._probe_receipt_is_binding(stale, now=NOW) is False


def test_expiry_is_measured_from_when_the_probe_ran():
    """Not from the target date: that is what let Monday block Wednesday."""
    receipt = _receipt(probed_at="2026-10-05T22:22:50+00:00", day="2026-10-07")
    assert bm._probe_receipt_is_binding(receipt, now=NOW) is False


def test_target_date_cannot_rescue_a_stale_receipt():
    for day in ("2026-10-07", "2026-10-08", "2026-10-09"):
        receipt = _receipt(probed_at="2026-10-01T00:00:00+00:00", day=day)
        assert bm._probe_receipt_is_binding(receipt, now=NOW) is False


@pytest.mark.parametrize("hours,binding", [(0, True), (1, True), (23, True),
                                           (25, False), (48, False)])
def test_suppression_window_boundaries(hours, binding):
    probed = NOW - dt.timedelta(hours=hours)
    receipt = _receipt(probed_at=probed.isoformat())
    assert bm._probe_receipt_is_binding(receipt, now=NOW) is binding


# --- confirmed contracts are durable facts --------------------------------


def test_confirmed_contract_receipt_suppresses_indefinitely():
    """A working contract is a durable fact, not a perishable observation."""
    old = _receipt(http_status=200, probed_at="2026-01-01T00:00:00+00:00")
    assert bm._probe_receipt_is_binding(old, now=NOW) is True


def test_explicit_contract_confirmed_flag_is_honoured():
    old = _receipt(contract_confirmed=True,
                   probed_at="2026-01-01T00:00:00+00:00")
    assert bm._probe_receipt_is_binding(old, now=NOW) is True


# --- unusable receipts must not bind --------------------------------------


def test_receipt_without_a_timestamp_cannot_bind():
    """It cannot prove it is recent. Re-probing costs one call; a wrong
    permanent block costs the source entirely."""
    assert bm._probe_receipt_is_binding(_receipt(probed_at=None), now=NOW) is False


def test_receipt_with_unparseable_timestamp_cannot_bind():
    bad = _receipt(probed_at="last Tuesday")
    assert bm._probe_receipt_is_binding(bad, now=NOW) is False


def test_receipt_stamped_in_the_future_cannot_bind():
    future = _receipt(probed_at="2026-12-25T00:00:00+00:00")
    assert bm._probe_receipt_is_binding(future, now=NOW) is False


def test_non_dict_receipt_is_not_binding():
    assert bm._probe_receipt_is_binding(None, now=NOW) is False


def test_naive_and_zulu_timestamps_are_both_read():
    for stamp in ("2026-10-07T11:00:00", "2026-10-07T11:00:00Z"):
        assert bm._probe_receipt_is_binding(_receipt(probed_at=stamp),
                                            now=NOW) is True


# --- end to end through capture_day ---------------------------------------


def _write_receipt(tmp_path, day, probed_at):
    import json
    path = tmp_path / f"betminer_probe_{day}.json"
    path.write_text(json.dumps(_receipt(probed_at=probed_at, date=day)))
    return path


def test_stale_receipt_lets_the_probe_run_again(monkeypatch, tmp_path):
    _write_receipt(tmp_path, "2026-10-07", "2026-10-01T00:00:00+00:00")
    calls = []

    def probe(url, timeout=30):
        calls.append(url)
        return 404, None, {}

    monkeypatch.setattr(bm, "get_json", probe)
    bm.capture_day("2026-10-07", localdata=tmp_path)
    assert calls, "a week-old failure receipt still blocked the re-probe"


def test_fresh_receipt_still_short_circuits_transport(monkeypatch, tmp_path):
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    _write_receipt(tmp_path, "2026-10-07", stamp)

    def should_not_probe(url, timeout=30):
        raise AssertionError("a fresh receipt must short-circuit transport")

    monkeypatch.setattr(bm, "get_json", should_not_probe)
    rows, stats = bm.capture_day("2026-10-07", localdata=tmp_path)
    assert rows == []
    assert stats["probe_receipt"] is True
    assert stats["requests"] == 0
