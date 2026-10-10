from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path

import pytest

from edgefactory.sources import futbolpronosticos as fp
from edgefactory.sources import sportytrader_odds as st

FIXTURES = Path(__file__).parent / "fixtures"


def test_futbolpronosticos_fixture_parses_slate_and_markets():
    slate = (FIXTURES / "futbolpronosticos_slate.html").read_text()
    links = fp.parse_slate(slate)
    assert [row["url"] for row in links] == [
        "https://www.futbolpronosticos.com/pronostico-real-betis-villarreal"
    ]

    page = (FIXTURES / "futbolpronosticos_match.html").read_text()
    row = fp.parse_fixture(page, day="2026-10-02", url=links[0]["url"])
    assert row is not None
    assert (row["home"], row["away"], row["date"]) == ("Real Betis", "Villarreal", "2026-10-02")
    assert {item["market"] for item in row["markets"]} == {
        "1x2", "ou_1.5", "ou_3.5", "btts", "correct_score"
    }
    assert row["predicted_score"] == "2:1"
    assert row["1x2_selection"] == "home"
    assert row["ou_3.5_selection"] == "under"


def test_futbolpronosticos_settlement_coverage_flags_backfill_mismatch():
    captured = [
        {"date": "2026-10-02", "home": "Alpha", "away": "Beta"},
        {"date": "2026-10-02", "home": "Gamma", "away": "Delta"},
    ]
    settled = [{"date": "2026-10-02", "home": "Alpha", "away": "Beta", "hs": 1, "gs": 0}]
    coverage = fp.settlement_coverage(captured, settled)
    assert coverage["settled"] == 1
    assert coverage["unmatched"] == 1
    assert coverage["mismatch"] is True
    assert coverage["settlement_source"] == "existing warehouse-score backfill"


def test_futbolpronosticos_robots_is_conservative():
    assert fp.robots_allows("https://www.futbolpronosticos.com/predicciones-de-futbol", "User-agent: *\nDisallow: /private")
    assert not fp.robots_allows("https://www.futbolpronosticos.com/private/x", "User-agent: *\nDisallow: /private")


def test_futbolpronosticos_capture_persists_raw_and_scored(monkeypatch, tmp_path):
    slate = (FIXTURES / "futbolpronosticos_slate.html").read_text()
    match = (FIXTURES / "futbolpronosticos_match.html").read_text()
    monkeypatch.setattr(fp, "_get", lambda url: slate if url.endswith("predicciones-de-futbol") else match)
    rows, stats = fp.capture_day("2026-10-02")
    assert stats["raw"] == 1
    assert stats["scored"] == 1
    path = fp.persist_shadow("2026-10-02", rows, stats, localdata=tmp_path)
    payload = json.loads(path.read_text())
    assert payload["stats"]["raw"] == 1
    assert payload["stats"]["scored"] == 1


def test_futbolpronosticos_429_aborts_without_followup(monkeypatch):
    calls = []

    def fail(url):
        calls.append(url)
        raise urllib.error.HTTPError(url, 429, "Too Many Requests", {}, io.BytesIO())

    monkeypatch.setattr(fp, "_raw_get", fail)
    fp._ROBOTS.clear()
    rows, stats = fp.capture_day("2026-10-02")
    assert rows == []
    assert stats["status"] == "blocked"
    assert "429" in stats["blocker"]
    assert len(calls) == 1


def test_sportytrader_hard_blocks_all_nine_disallowed_prefixes():
    for prefix in st.DISALLOWED_PREFIXES:
        assert not st.allowed_url(f"https://www.sportytrader.es{prefix}anything")
    assert st.allowed_url("https://www.sportytrader.es/pronosticos/futbol/")
    assert st.allowed_url("https://www.sportytrader.com/pt-br/pronosticos/futbol/")
    assert st.allowed_url("https://www.sportytrader.fr/pronostics/football/")
    assert not st.allowed_url("https://www.sportytrader.es/en-gb/pronosticos/futbol/")


def test_sportytrader_fixture_captures_named_bookmaker_rows():
    listing = (FIXTURES / "sportytrader_listing.html").read_text()
    links = st.parse_listing(listing)
    assert links == ["https://www.sportytrader.es/pronosticos/real-betis-villarreal-123456/"]
    page = (FIXTURES / "sportytrader_match.html").read_text()
    rows = st.parse_match_page(page, day="2026-10-02", url=links[0])
    assert len(rows) == 4
    assert all(row["book"] and row["bookmaker"] for row in rows)
    assert {row["market"] for row in rows} == {"1x2", "ou_2.5"}
    assert {row["selection"] for row in rows} >= {"home", "draw", "away"}


def test_sportytrader_429_sets_cooldown_and_honors_retry_after(monkeypatch):
    st.reset_state()
    monkeypatch.setattr(st.time, "sleep", lambda _seconds: None)

    def rate_limited(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://www.sportytrader.es/pronosticos/futbol/", 429,
            "Too Many Requests", {"Retry-After": "30"}, io.BytesIO(b""),
        )

    monkeypatch.setattr(st.urllib.request, "urlopen", rate_limited)
    with pytest.raises(st.RateLimited):
        st._raw_get("https://www.sportytrader.es/pronosticos/futbol/")
    assert st._COOLING is True
    assert st._429S == 1


def test_sportytrader_challenge_switches_training_only(monkeypatch):
    st.reset_state()
    monkeypatch.setattr(st, "allowed_url", lambda _url: True)

    def challenge(_url):
        raise st.ChallengeWalled("Cloudflare /cdn-cgi challenge")

    monkeypatch.setattr(st, "_get", challenge)
    rows, stats = st.capture_day("2026-10-02")
    assert rows == []
    assert stats["status"] == "training_only"
    assert stats["training_only"] is True


def test_sportytrader_capture_persists_st_raw_and_matched(monkeypatch, tmp_path):
    listing = (FIXTURES / "sportytrader_listing.html").read_text()
    page = (FIXTURES / "sportytrader_match.html").read_text()
    # capture_day persists its HTML cache under LOCALDATA; point it at the
    # test tmp dir so the repo's operational localdata/ stays untouched, and
    # clear the module cache so this run cannot inherit (or feed) other
    # tests' fetched pages.
    monkeypatch.setattr(st, "LOCALDATA", tmp_path)
    monkeypatch.setattr(st, "_HTML_CACHE", {})
    monkeypatch.setattr(st, "_get", lambda url: listing if "/pronosticos/futbol" in url else page)
    rows, stats = st.capture_day("2026-10-02")
    assert stats["st_raw"] == 1
    assert stats["st_matched"] == 4
    # the HTML cache lands in tmp, beside the shadow ledger — not in localdata/
    assert (tmp_path / "sportytrader_odds_html_cache_2026-10-02.json").exists()
    path = st.persist_shadow("2026-10-02", rows, stats, localdata=tmp_path)
    payload = json.loads(path.read_text())
    assert payload["stats"]["st_raw"] == 1
    assert payload["stats"]["st_matched"] == 4
    assert payload["rows"][0]["bookmaker"] == "Bet365"
