"""Synthetic, forward-only paper admission checks; no provider calls/ROI tuning."""

import json
from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from test_ml_paper import DAY, FREEZE, NOW, capture, context, pick, run_capture

import scripts.auto_tickets as at
from edgefactory import ml_paper as mp
from edgefactory.enh_pricing import _betexplorer_asof_index, load_prices_index
from edgefactory.util import norm_team
from test_ml_paper import synthetic_oddspapi_provenance


def offer(row, source, stamp):
    return {
        "home": row["home"], "away": row["away"], "market": "1x2", "selection": "home",
        "odds": row["odds"], "bookmaker": row["bookmaker"], "source": source,
        "captured_at": stamp, "kickoff": row["kickoff_utc"],
        "provenance": row.get("odds_provenance"),
    }


@pytest.mark.parametrize("source", ["pinnapi_odds", "theoddsapi", "bzzoiro_odds", "sharpapi_odds"])
@pytest.mark.parametrize("path", ["primary", "board", "fixture_index"])
@pytest.mark.parametrize("age,allowed", [
    (timedelta(hours=6, minutes=20), True),
    (timedelta(hours=8, minutes=44), True),
    (timedelta(hours=12), True),
    (timedelta(hours=12, seconds=1), False),
])
def test_overnight_quotes_have_a_bounded_chance_on_every_admission_path(
    tmp_path, source, path, age, allowed
):
    rows = [pick(1), pick(2)]
    original_stamp = (FREEZE - age).isoformat()
    index = {"fixture_quotes": {}}
    for row in rows:
        row.update(odds_source=source, odds_captured_at=original_stamp)
        if path == "board":
            row["price_board"] = [offer(row, source, original_stamp)]
            row["odds"] = None
        elif path == "fixture_index":
            pair = (norm_team(row["home"]), norm_team(row["away"]))
            # Existing non-parent market; exact original names and kickoff.
            index["fixture_quotes"][pair] = {("ou_2.5", "over"): [
                (row["odds"], row["bookmaker"], original_stamp, source,
                 row["kickoff_utc"], None, (row["home"], row["away"]))
            ]}
            row["odds"] = None
    before = deepcopy(rows)
    draft = run_capture(tmp_path, context(rows), index=index)
    assert rows == before
    assert bool(draft["candidates"]) is allowed
    assert draft["policy"]["quote_max_age_hours"] == 12
    assert draft["policy"]["stricter_source_limits_retained"] is True
    for c in draft["candidates"]:
        assert c["price_at"] == original_stamp  # no rescue by retimestamping
        assert c["price_age_seconds_at_freeze"] == age.total_seconds()
        assert c["price_age_seconds_at_decision"] == (NOW - (FREEZE - age)).total_seconds()
    sealed = run_capture(tmp_path, {}, now=FREEZE)
    assert sealed["candidates"] == draft["candidates"]
    assert sealed["accas"] == draft["accas"]
    if path != "fixture_index":
        # Healthy synthetic inputs exercise selection AND independent paper stakes.
        assert bool(sealed["accas"]) is allowed
    assert mp.receipts(tmp_path) == [sealed]


@pytest.mark.parametrize("source", ["oddspapi", "oddspapi_odds"])
@pytest.mark.parametrize("path", ["primary", "board", "fixture_index"])
@pytest.mark.parametrize("age,allowed", [
    (timedelta(hours=6), True),
    (timedelta(hours=6, seconds=1), False),
    (timedelta(hours=8), False),
])
def test_oddspapi_aliases_keep_six_hours_at_freeze_on_all_paths(
    tmp_path, source, path, age, allowed
):
    row = pick()
    stamp = (FREEZE - age).isoformat()
    row.update(odds_source=source, odds_captured_at=stamp)
    row["odds_provenance"] = synthetic_oddspapi_provenance(row)
    index = {}
    if path == "board":
        row["price_board"] = [offer(row, source, stamp)]
        row["odds"] = None
    elif path == "fixture_index":
        pair = (norm_team(row["home"]), norm_team(row["away"]))
        index = {"fixture_quotes": {pair: {("ou_2.5", "over"): [
            (2.0, "Pinnacle", stamp, source, row["kickoff_utc"], row["odds_provenance"],
             (row["home"], row["away"]))
        ]}}}
        row["odds"] = None
    draft = run_capture(tmp_path, context([row]), index=index)
    assert bool(draft["candidates"]) is allowed
    assert mp._quote_max_age(source) == timedelta(hours=6)


@pytest.mark.parametrize("source,hours", [("theoddsapi", 12), ("oddspapi_odds", 6)])
def test_quote_fresh_at_draft_but_expired_by_freeze_cannot_enter(tmp_path, source, hours):
    rows = [pick(1), pick(2)]
    for row in rows:
        row.update(
            odds_source=source,
            odds_captured_at=(NOW - timedelta(hours=hours - 1, minutes=30)).isoformat(),
        )
    r = capture(tmp_path, rows)
    assert not r["candidates"] and not r["accas"]


@pytest.mark.parametrize("stamp", [None, "", "2026-11-01T22:16:00", (NOW + timedelta(seconds=1)).isoformat()])
def test_relaxation_never_supplies_or_repairs_missing_unzoned_future_times(tmp_path, stamp):
    rows = [pick(1), pick(2)]
    for row in rows:
        row["odds_captured_at"] = stamp
    r = capture(tmp_path, rows)
    assert not r["candidates"] and not r["accas"]


@pytest.mark.parametrize("source", ["betolimp", "unknown", "boggio", "scoutingstats", "sportytrader_odds"])
def test_relaxation_does_not_admit_unavailable_unnamed_or_disabled_sources(tmp_path, source):
    rows = [pick(1), pick(2)]
    for row in rows:
        row.update(odds_source=source, odds_captured_at="2026-11-01T22:16:00+00:00")
    r = capture(tmp_path, rows)
    assert not r["candidates"] and not r["accas"]


@pytest.mark.parametrize("source", ["betexplorer", "betexplorer_odds"])
@pytest.mark.parametrize("age,source_hours,allowed", [
    (timedelta(hours=8, minutes=44), 24, True),
    (timedelta(hours=12), 24, True),
    (timedelta(hours=12, seconds=1), 24, False),
    (timedelta(hours=6), 6, True),
    (timedelta(hours=6, seconds=1), 6, False),
    (timedelta(hours=8), 6, False),
])
def test_betexplorer_real_admission_receipt_keeps_source_limit_at_freeze(
    tmp_path, monkeypatch, source, age, source_hours, allowed
):
    from test_betexplorer_board_admission import ALL_BE_MARKETS, board_only
    from test_enh_pricing import BE_DAY, _be_pick

    from edgefactory.sources import betexplorer_odds as be

    monkeypatch.setenv("EDGE_FACTORY_ENH_BOARD", "1")
    monkeypatch.setattr(be, "CACHE_FRESHNESS_H", source_hours)
    _, fixture = board_only(tmp_path, markets=ALL_BE_MARKETS)
    freeze = datetime.fromisoformat(f"{BE_DAY}T09:00:00+02:00")
    stamp = (freeze - age).astimezone(UTC).isoformat()
    # Synthetic original capture in the actual retained ledger, not a forged
    # source string/boolean or manually constructed admission receipt.
    path = tmp_path / "localdata" / f"betexplorer_match_detail_{BE_DAY}.json"
    ledger = json.loads(path.read_text())
    for item in ledger["fixtures"].values():
        item["captured_at"] = stamp
    path.write_text(json.dumps(ledger))
    row = _be_pick("match_over_25", pick="home", league=fixture["league"], contract_id="freshness-test")
    now = datetime.fromisoformat(row["as_of"])
    kickoff = at.parse_kickoff_proven(row)
    index = _betexplorer_asof_index(load_prices_index(tmp_path, BE_DAY), now)
    pair = (norm_team(row["home"]), norm_team(row["away"]))
    q = next(q for q in index["fixture_quotes"][pair][("ou_2.5", "over")] if q[3] == "betexplorer")
    quote = mp._quote(*q[:6])
    quote["enhancement_price_source"] = source
    assert mp._quote_ok(
        row, quote, now, kickoff, at.execution_source_rejection, 1.0,
        market="match_over_25", selection="over", freeze_at=freeze,
    ) is allowed
    assert quote["enhancement_price_at"] == stamp
    quote["enhancement_price_provenance"] = None
    assert not mp._quote_ok(
        row, quote, now, kickoff, at.execution_source_rejection, 1.0,
        market="match_over_25", selection="over", freeze_at=freeze,
    )


def test_new_policy_never_reselects_or_relabels_an_existing_frozen_day(tmp_path, monkeypatch):
    frozen = capture(tmp_path)
    path = mp.receipt_path(tmp_path, DAY)
    before = path.read_bytes()
    # A future policy deployment must not reinterpret/rewrite existing cards.
    monkeypatch.setattr(mp, "QUOTE_MAX_AGE", timedelta(hours=24))
    assert run_capture(tmp_path, context([pick(99)]), now=FREEZE + timedelta(hours=1)) is None
    assert path.read_bytes() == before
    assert mp.receipts(tmp_path) == [frozen]
