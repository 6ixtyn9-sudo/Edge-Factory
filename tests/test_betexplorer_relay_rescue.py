"""BetExplorer operator-relay rescue (2026-11-14 repair).

On 2026-11-15 the shared CI runner's egress IP was already throttled before
the run started: the FIRST BetExplorer request returned 429, the 30-second
backoff retry returned 429 again, and the run-scoped cooldown spent the rest
of the run refusing requests - 0 rows, 50 picks deferred. A 429/403 from the
site edge is a statement about the egress ADDRESS, not the request, so when
the operator relays (``EDGE_FACTORY_RELAY_URLS``) are configured the adapter
now tries the same URL through them once before treating the refusal as
authoritative, and once a rescue succeeds the relay is asked FIRST for the
rest of the run instead of burning a refused direct attempt (plus its 30-60s
penalty) in front of every remaining page.

Pinned here:

* a first-attempt 429 with a working relay serves the page, keeps the run
  out of cooldown, and leaves ``be_429`` honest about what the site showed;
* relay mode is sticky for the rest of the run (no more direct attempts);
* a 403 challenge surface is rescued the same way;
* a missing or failing relay falls back to the pre-repair refusal policy:
  Retry-After-respecting waits, then run-scoped cooldown - the relay can
  never LOWER politeness toward the site.

All transport is monkeypatched; nothing here touches the network.
"""
from __future__ import annotations

import io
import urllib.error

import pytest

from edgefactory.sources import betexplorer_odds as be

URL = "https://www.betexplorer.com/football/example"


@pytest.fixture(autouse=True)
def _reset_be(tmp_path, monkeypatch):
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.delenv("EDGE_FACTORY_RELAY_URLS", raising=False)
    monkeypatch.delenv("EDGE_FACTORY_RELAY_TOKEN", raising=False)
    monkeypatch.setattr(be, "_throttle", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(be.time, "sleep", lambda _seconds: None)
    be.reset_fetch_count()
    yield
    be.reset_fetch_count()


def _http_error(code: int):
    reason = {403: "Forbidden", 429: "Too Many Requests"}[code]
    return urllib.error.HTTPError(URL, code, reason, {}, io.BytesIO(b""))


def _configure_relay(monkeypatch, pages: dict[str, bytes], *, ok: bool = True):
    """Stand in for EDGE_FACTORY_RELAY_URLS with validated in-memory pages."""
    monkeypatch.setattr(be.public_relay, "configured", lambda: ok)

    def fetches(source_url, *, timeout=40):
        yield from pages.items()

    monkeypatch.setattr(be.public_relay, "fetches", fetches)


def test_first_429_is_rescued_by_the_relay_without_cooling_down(monkeypatch):
    direct_calls = []

    def urlopen(_request, timeout=20):
        direct_calls.append(1)
        raise _http_error(429)

    _configure_relay(monkeypatch, {"relay:test": b"<html>odds page</html>"})
    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)

    assert be._fetch(URL) == "<html>odds page</html>"
    # One direct attempt, honestly reported; the refusal did not cascade
    # into the 30-60s penalty ladder because the relay served the page.
    assert direct_calls == [1]
    stats = be.run_stats()
    assert stats["be_429"] == 1
    assert stats["be_cooling_down"] is False
    assert stats["be_relay_fetches"] == 1
    assert stats["be_relay_mode"] is True
    assert be.request_stats()["requests"] == 1


def test_relay_mode_is_sticky_and_skips_direct_attempts(monkeypatch):
    def urlopen(_request, timeout=20):
        raise _http_error(429)

    _configure_relay(monkeypatch, {"relay:test": b"<html>page</html>"})
    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)

    be._fetch(URL)
    assert be.run_stats()["be_relay_mode"] is True

    def forbidden(*_args, **_kwargs):
        raise AssertionError("relay mode must not spend refused direct attempts")

    monkeypatch.setattr(be.urllib.request, "urlopen", forbidden)
    assert be._fetch(URL + "?tab=1") == "<html>page</html>"
    assert be.run_stats()["be_relay_fetches"] == 2


def test_relay_miss_falls_back_to_the_existing_429_policy(monkeypatch):
    """A relay that cannot serve the page must not lower politeness: the
    second 429 still trips the run-scoped cooldown before any third request."""
    direct_calls = []

    def urlopen(_request, timeout=20):
        direct_calls.append(1)
        raise _http_error(429)

    _configure_relay(monkeypatch, {})  # configured, but yields nothing
    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)

    with pytest.raises(be.BetExplorerCoolingDown):
        be._fetch(URL, retries=3)
    assert len(direct_calls) == 2
    stats = be.run_stats()
    assert stats["be_429"] == 2
    assert stats["be_cooling_down"] is True
    assert stats["be_relay_fetches"] == 0


def test_unconfigured_relay_keeps_the_pre_repair_policy(monkeypatch):
    monkeypatch.setattr(be.public_relay, "configured", lambda: False)

    def urlopen(_request, timeout=20):
        raise _http_error(429)

    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)
    with pytest.raises(be.BetExplorerCoolingDown):
        be._fetch(URL, retries=3)
    assert be.run_stats()["be_relay_fetches"] == 0


def test_403_challenge_is_rescued_by_the_relay(monkeypatch):
    def urlopen(_request, timeout=20):
        raise _http_error(403)

    _configure_relay(monkeypatch, {"relay:test": b"<html>board</html>"})
    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)

    assert be._fetch(URL) == "<html>board</html>"
    assert be.run_stats()["be_relay_mode"] is True


def test_403_with_a_failing_relay_raises_the_challenge(monkeypatch):
    def urlopen(_request, timeout=20):
        raise _http_error(403)

    _configure_relay(monkeypatch, {})
    monkeypatch.setattr(be.urllib.request, "urlopen", urlopen)

    with pytest.raises(be.BetExplorerChallenge):
        be._fetch(URL)
    assert be.run_stats()["be_relay_fetches"] == 0


def test_relay_rescue_never_runs_without_credentials(monkeypatch):
    """The rescue path must degrade to None, not to an unauthenticated POST."""
    called = []

    def fetches(source_url, *, timeout=40):
        called.append(source_url)
        return iter(())

    monkeypatch.setattr(be.public_relay, "configured", lambda: False)
    monkeypatch.setattr(be.public_relay, "fetches", fetches)
    assert be._relay_rescue(URL) is None
    assert called == []
