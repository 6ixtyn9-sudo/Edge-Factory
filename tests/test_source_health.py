"""Source-health observability contracts for PR #21."""
from __future__ import annotations

import io
import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory import source_health  # noqa: E402
from edgefactory.sources import bzzoiro_odds as bzz  # noqa: E402


@pytest.fixture(autouse=True)
def _state_file(tmp_path, monkeypatch):
    monkeypatch.setattr(source_health, "STATE_PATH", tmp_path / "source_health_state.json")
    monkeypatch.setattr(source_health, "LOCALDATA", tmp_path)
    yield


def test_bzzoiro_zero_streak_persists_and_resets_only_on_observed_nonzero():
    zero = {
        "status": "empty", "best_results": 0, "comparison_rows": 0, "rows": 0,
        "http_statuses": [], "errors": [], "quota_hint": "none_observed",
    }
    for day in ("2026-10-01", "2026-10-02", "2026-10-03"):
        record = source_health.record_bzzoiro_run(day, zero)
    assert record["zero_run_streak"] == 3
    assert source_health.bzzoiro_unavailable()
    assert "bzz UNAVAILABLE" in source_health.bzzoiro_status_line()

    source_health.record_bzzoiro_run(
        "2026-10-04",
        {**zero, "status": "ok", "best_results": 2, "rows": 3},
    )
    assert not source_health.bzzoiro_unavailable()

    # A cache-only enrichment did not observe upstream and must not change the
    # persisted streak in either direction.
    source_health.record_bzzoiro_run("2026-10-05", {"status": "cache_only"})
    assert source_health.load_state()["sources"]["bzzoiro"]["zero_run_streak"] == 0


def test_bzzoiro_empty_diagnostics_include_cap_and_zero_counters(monkeypatch):
    monkeypatch.setattr(bzz, "TOKEN", "test-token")
    monkeypatch.setattr(bzz, "_fetch_url", lambda *_args, **_kwargs: (0, []))
    monkeypatch.setattr(bzz, "_event_comparison_rows", lambda _day: [])

    assert bzz.fetch_day("2026-10-02") == []
    diag = bzz.diagnostics()
    assert diag["status"] == "empty"
    assert diag["best_results"] == 0
    assert diag["comparison_rows"] == 0
    assert diag["rows"] == 0
    assert diag["max_event_comparison"] == 20
    assert diag["quota_hint"] == "none_observed"


def test_bzzoiro_429_is_recorded_as_rate_limit_quota_hint(monkeypatch):
    bzz._reset_diagnostics()
    monkeypatch.setattr(bzz, "time", type("Clock", (), {"sleep": staticmethod(lambda _s: None)})())

    def urlopen(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://sports.bzzoiro.com/api/v2/odds/best/", 429,
            "Too Many Requests", {"Retry-After": "30"}, io.BytesIO(b""),
        )

    monkeypatch.setattr(bzz.urllib.request, "urlopen", urlopen)
    with pytest.raises(urllib.error.HTTPError):
        bzz._get("https://sports.bzzoiro.com/api/v2/odds/best/", retries=1)
    diag = bzz.diagnostics()
    assert diag["http_statuses"] == [429]
    assert diag["quota_hint"] == "rate_limit_or_quota"
    assert diag["requests"] == 1
