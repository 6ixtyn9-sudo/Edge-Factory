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


def test_daily_source_health_schema_is_conservative_and_forebet_is_historical_only():
    payload = source_health.persist_daily_source_health(
        "2026-10-02",
        {
            "zulubet": {"fetched": True, "rows": 4, "can_vote": True, "freshness_h": 0},
            "futbolpronosticos": {
                "fetched": True, "rows": 1, "raw": 2, "scored": 1,
                "can_fetch_today": True, "can_vote": False,
            },
            "sportytrader_odds": {
                "fetched": True, "rows": 3, "st_raw": 1, "st_matched": 3,
                "can_fetch_today": True, "can_price": True, "can_vote": False,
            },
        },
    )
    assert payload["sources"]["zulubet"] == {
        "can_fetch_today": True,
        "can_price": False,
        "can_vote": True,
        "freshness_h": 0.0,
        "blocker": None,
        "reason": None,
        "status": None,
        # Rows fetched then discarded while parsing. Carried for every source
        # so a parser fault cannot hide behind a bare zero.
        "canonicalization_dropped": 0,
    }
    assert payload["sources"]["forebet"] == {
        "can_fetch_today": False,
        "can_price": False,
        "can_vote": False,
        "freshness_h": None,
        "blocker": "historical-only post-2026-06-12; no production pricing or weighting",
    }
    assert payload["sources"]["futbolpronosticos"]["raw"] == 2
    assert payload["sources"]["futbolpronosticos"]["scored"] == 1
    assert payload["sources"]["sportytrader_odds"]["st_raw"] == 1
    assert payload["sources"]["sportytrader_odds"]["st_matched"] == 3
    assert source_health.daily_status_block("2026-10-02").startswith("Source health 2026-10-02:")


def test_shadow01_sources_have_health_rows_counters_and_tokens(tmp_path):
    """SHADOW-01 T1: betminer/pinnapi_odds/betbetter are health rows with
    their own counter fields and compact status tokens, conservative when
    unobserved."""
    payload = source_health.persist_daily_source_health(
        "2026-10-03",
        {
            "betminer": {
                "fetched": True, "rows": 2, "bm_raw": 2, "bm_scored": 2,
                "can_fetch_today": True, "can_vote": False,
            },
            "pinnapi_odds": {
                "fetched": True, "rows": 5, "pa_raw": 7, "pa_matched": 5,
                "can_fetch_today": True, "can_price": True, "can_vote": False,
            },
            "betbetter": {
                "fetched": True, "rows": 3, "bb_raw": 4, "bb_scored": 3,
                "can_fetch_today": True, "can_vote": False,
            },
        },
    )
    assert payload["sources"]["betminer"]["bm_raw"] == 2
    assert payload["sources"]["betminer"]["bm_scored"] == 2
    assert payload["sources"]["pinnapi_odds"]["pa_raw"] == 7
    assert payload["sources"]["pinnapi_odds"]["pa_matched"] == 5
    assert payload["sources"]["betbetter"]["bb_raw"] == 4
    assert payload["sources"]["betbetter"]["bb_scored"] == 3
    line = source_health.daily_status_block("2026-10-03")
    assert "betminer=bm_raw2/bm_scored2" in line
    assert "pinnapi=pa_raw7/pa_matched5" in line
    assert "betbetter=bb_raw4/bb_scored3" in line


def test_shadow01_sources_unobserved_are_conservative(tmp_path):
    payload = source_health.persist_daily_source_health("2026-10-03", {})
    for name in ("betminer", "pinnapi_odds", "betbetter"):
        row = payload["sources"][name]
        assert row["can_fetch_today"] is False
        assert row["can_price"] is False
        assert row["can_vote"] is False
        assert row["blocker"]


def test_health_line_role_verdicts_are_per_role_not_all_three(tmp_path):
    """SHADOW-01 T0: role-limited sources must not print constant BLOCKED."""
    source_health.persist_daily_source_health(
        "2026-10-02",
        {
            # bzzoiro is a vote feed: fetch+vote with can_price False is healthy.
            "bzzoiro": {"fetched": True, "rows": 5, "can_fetch_today": True,
                        "can_price": False, "can_vote": True},
            # bzzoiro_odds is a price feed: fetch+price with can_vote False is healthy.
            "bzzoiro_odds": {"fetched": True, "rows": 5, "can_fetch_today": True,
                             "can_price": True, "can_vote": False},
            # betexplorer prices but never votes.
            "betexplorer": {"fetched": True, "rows": 2, "can_fetch_today": True,
                            "can_price": True, "can_vote": False},
            # scoutingstats is a full source: all three keys.
            "scoutingstats": {"fetched": True, "rows": 9, "can_fetch_today": True,
                              "can_price": True, "can_vote": True},
        },
    )
    line = source_health.daily_status_block("2026-10-02")
    assert "bzzoiro=fetch/vote" in line
    assert "bzzoiro_odds=fetch/price" in line
    assert "betexplorer=fetch/price" in line
    assert "scoutingstats=fetch/price/vote" in line


def test_health_line_role_verdicts_fail_when_role_key_fails(tmp_path):
    source_health.persist_daily_source_health(
        "2026-10-02",
        {
            # Vote feed that lost its vote capability: BLOCKED.
            "bzzoiro": {"fetched": True, "rows": 0, "can_fetch_today": True,
                        "can_price": False, "can_vote": False},
            # Price feed with zero priced rows: BLOCKED.
            "bzzoiro_odds": {"fetched": True, "rows": 0, "can_fetch_today": True,
                             "can_price": False, "can_vote": False},
            # Fetched but nothing to price: BLOCKED.
            "betexplorer": {"fetched": True, "rows": 0, "can_fetch_today": True,
                            "can_price": False, "can_vote": False},
            # Full source missing its price capability: BLOCKED.
            "scoutingstats": {"fetched": True, "rows": 3, "can_fetch_today": True,
                              "can_price": False, "can_vote": True},
        },
    )
    line = source_health.daily_status_block("2026-10-02")
    assert "bzzoiro=BLOCKED" in line
    assert "bzzoiro_odds=BLOCKED" in line
    assert "betexplorer=BLOCKED" in line
    assert "scoutingstats=BLOCKED" in line


def test_health_line_role_verdicts_fail_when_fetch_fails(tmp_path):
    source_health.persist_daily_source_health(
        "2026-10-02",
        {
            "bzzoiro": {"fetched": False, "rows": 0, "can_fetch_today": False,
                        "can_price": False, "can_vote": True},
            "scoutingstats": {"fetched": False, "rows": 0, "can_fetch_today": False,
                              "can_price": True, "can_vote": True},
        },
    )
    line = source_health.daily_status_block("2026-10-02")
    assert "bzzoiro=BLOCKED" in line
    assert "scoutingstats=BLOCKED" in line


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


def test_convergent_source_never_earns_voice_or_price_credit(tmp_path):
    """SHADOW-01 T5: the PredictIQ convergent tag is enforced at the registry.

    Even if a future adapter reports healthy observations with can_vote and
    can_price claimed True, the daily contract refuses them: a convergent
    source (ensemble includes devigged market odds) earns zero voice credit
    permanently and never corroborates a price.
    """
    payload = source_health.persist_daily_source_health(
        "2026-10-02",
        {
            "predictiq": {
                "fetched": True, "rows": 50, "can_fetch_today": True,
                "can_price": True, "can_vote": True, "freshness_h": 0.5,
            },
        },
    )
    row = payload["sources"]["predictiq"]
    assert row["can_fetch_today"] is True   # fetching for echo testing is fine
    assert row["can_price"] is False        # never a corroborator
    assert row["can_vote"] is False         # zero voice credit permanently
    assert "convergent" in str(row["blocker"])
    assert "never corroborates" in str(row["blocker"])


def test_convergent_source_unobserved_is_conservative(tmp_path):
    payload = source_health.build_daily_source_health("2026-10-02", {})
    row = payload["sources"]["predictiq"]
    assert row["can_fetch_today"] is False
    assert row["can_price"] is False
    assert row["can_vote"] is False
    assert row["blocker"]


def test_sharpapi_health_token_renders_on_health_line(tmp_path):
    source_health.persist_daily_source_health(
        "2026-10-02",
        {"sharpapi_odds": {"fetched": True, "rows": 4, "sa_raw": 4,
                           "sa_matched": 4, "can_fetch_today": True,
                           "can_price": True, "can_vote": False}},
    )
    line = source_health.daily_status_block("2026-10-02")
    assert "sharpapi=sa_raw4/sa_matched4" in line


def test_boggio_health_token_has_zero_reason_suffix(tmp_path):
    source_health.persist_daily_source_health(
        "2026-10-02", {"boggio": {"fetched": True, "rows": 0, "bg_raw": 0,
        "bg_scored": 0, "status": "auth", "blocker": "HTTP 403", "can_fetch_today": False}}
    )
    assert "boggio=bg_raw0/bg_scored0(auth403)" in source_health.daily_status_block("2026-10-02")


def test_convergent_source_renders_echo_only_on_health_line(tmp_path):
    source_health.persist_daily_source_health(
        "2026-10-02",
        {"predictiq": {"fetched": True, "rows": 50, "can_fetch_today": True,
                       "can_price": True, "can_vote": True}},
    )
    line = source_health.daily_status_block("2026-10-02")
    assert "predictiq=echo/only" in line


def test_pinnapi_request_contract_survives_into_the_committed_health_row():
    """A zero is only readable with the discriminators beside it.

    auth_mechanism and zero_row_kind decide what a zero MEANS. They used to
    live only in the per-date shadow ledger, which .gitignore excludes, so
    the 2026-10-06 production run answered the question and the answer did
    not survive the run. The committed health row carries them now.
    """
    payload = source_health.build_daily_source_health("2026-10-06", {
        "pinnapi_odds": {
            "status": "empty", "pa_raw": 0, "pa_matched": 0,
            "sport_id": 1, "event_type": "prematch",
            "auth_mechanism": "header",
            "auth_attempts": [
                {"auth": "header", "status": 200, "error_envelope": None},
            ],
            "zero_row_kind": "no_usable_rows",
            "response_shape": {
                "event_count": 42, "events_with_teams": 42,
                "events_with_markets": 0, "envelope_found": True,
                "drop_reasons": {},
            },
        },
    })
    row = payload["sources"]["pinnapi_odds"]
    assert row["auth_mechanism"] == "header"
    assert row["zero_row_kind"] == "no_usable_rows"
    assert row["sport_id"] == 1
    assert row["auth_attempts"] == [{"auth": "header", "status": 200}]
    assert row["response_shape_summary"]["events_with_markets"] == 0
    assert row["response_shape_summary"]["event_count"] == 42
    # the full payload sample is NOT dragged into the committed row
    assert "response_shape" not in row


def test_pinnapi_contract_helper_names_every_discriminator():
    """One list, so the passthrough and the row cannot drift apart."""
    out = source_health.pinnapi_contract_observation({
        "sport_id": 1, "event_type": "prematch", "auth_mechanism": "query",
        "auth_attempts": [{"auth": "header", "status": 401}],
        "zero_row_kind": "empty_board", "response_shape": {"event_count": 0},
    })
    assert set(out) == set(source_health.PINNAPI_CONTRACT_FIELDS)
    assert out["auth_mechanism"] == "query"
    # absent fields are present as None rather than missing, so a reader can
    # tell "not recorded" from "key never existed"
    assert source_health.pinnapi_contract_observation({})["auth_mechanism"] is None


def test_the_caller_actually_forwards_the_pinnapi_contract_fields():
    """The gap that cost the 2026-10-06 answer.

    The health observation for this source is hand-built field by field, so
    a field the adapter records reaches the committed row only if the
    caller forwards it. The row-level passthrough passed its own test while
    the real pipeline still dropped everything, because the test fed the
    builder directly. This asserts the wiring, not the capability.
    """
    src = (ROOT / "scripts" / "picks_today.py").read_text(encoding="utf-8")
    assert "pinnapi_contract_observation(pa_shadow_stats)" in src, (
        "picks_today must forward the pinnapi request-contract fields into "
        "the health observation; without this the discriminators exist only "
        "in the gitignored shadow ledger and leave with the runner"
    )


def test_sharpapi_board_helper_names_every_board_field():
    """One list, so the passthrough and the committed row cannot drift."""
    out = source_health.sharpapi_board_observation({
        "board_rows": 100, "board_fixtures": 100, "board_league_count": 7,
        "board_leagues": {"lg_0": 15}, "board_non_prematch_rows": 100,
        "board_priced_rows": 0, "board_truncated": True,
        "requested_limit": 100, "league_filter_requested": False,
        "league_filter_effective": None,
    })
    assert set(out) == set(source_health.SHARPAPI_BOARD_FIELDS)
    assert out["board_truncated"] is True
    assert source_health.sharpapi_board_observation({})["board_rows"] is None


def test_the_sharpapi_board_summary_reaches_the_committed_row():
    row = source_health.build_daily_source_health("2026-10-06", {
        "sharpapi_odds": {
            "fetched": True, "rows": 0, "sa_raw": 0, "sa_matched": 0,
            "can_fetch_today": True, "can_price": False, "can_vote": False,
            "status": "empty", "reason": "board_truncated_live_first",
            "board_rows": 100, "board_fixtures": 100, "board_truncated": True,
            "board_league_count": 7, "board_leagues": {"lg_0": 15},
            "board_non_prematch_rows": 100, "board_priced_rows": 0,
            "requested_limit": 100, "league_filter_requested": False,
        },
    })["sources"]["sharpapi_odds"]
    assert row["board_summary"]["board_rows"] == 100
    assert row["board_summary"]["board_truncated"] is True
    assert row["reason"] == "board_truncated_live_first"


def test_the_caller_actually_forwards_the_sharpapi_board_fields():
    """Same gap that cost the 2026-10-06 pinnacle answer, same guard.

    The health observation is hand-built field by field, so board context
    the adapter records reaches the committed row only if the caller
    forwards it. A row-level test passes happily while the real pipeline
    drops everything. This asserts the wiring, not the capability.
    """
    src = (ROOT / "scripts" / "picks_today.py").read_text(encoding="utf-8")
    assert "sharpapi_board_observation(sa_shadow_stats)" in src, (
        "picks_today must forward the sharpapi board-shape fields into the "
        "health observation; without this a zero names no action and the "
        "context leaves with the runner"
    )
