"""Round-3 capture regressions: slate prioritisation, durable market census,
expected-vs-loss skip classification (scripts/capture_oddspapi.py).

Grounded in run 662c99f1: the 20-fixture budget went to provider-ordered
fixtures while the day's slate (57 picks) covered none of them, so the three
healthy rows landed in fixture_key_miss; the market-id enumeration existed
only in the masked run log; and outcome_inactive=10366 was reported next to
genuine defects with no distinction.
"""
from __future__ import annotations

import json
from pathlib import Path

import scripts.capture_oddspapi as cap
from edgefactory.sources import oddspapi_odds as op

FIXTURES = Path(__file__).parent / "fixtures"


def _odds_payload() -> dict:
    return json.loads((FIXTURES / "oddspapi_odds_documented_shape.json").read_text())


def _catalog() -> list:
    return json.loads((FIXTURES / "oddspapi_markets_catalog.json").read_text())


def _fixtures_list() -> list[dict]:
    return [
        {"fixtureId": "fx1", "participant1Name": "BK Forward",
         "participant2Name": "IK Sleipner"},
        {"fixtureId": "fx2", "participant1Name": "Croatia",
         "participant2Name": "England"},
        {"fixtureId": "fx3", "participant1Name": "Alpha FC",
         "participant2Name": "Beta FC"},
    ]


def _write_slate(tmp_path: Path, picks: list[dict]) -> None:
    (tmp_path / "picks_today.json").write_text(json.dumps(picks))


# ---------------------------------------------------------------------------
# Slate prioritisation
# ---------------------------------------------------------------------------


def test_slate_fixtures_are_prioritised_stably(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    _write_slate(tmp_path, [{
        "date": "2026-10-03", "home": "England", "away": "Croatia",
        "market": "1x2", "pick": "home",
    }])
    ordered, slate_n = cap._prioritise_slate_fixtures(_fixtures_list(), "2026-10-03")
    assert slate_n == 1
    assert ordered[0]["fixtureId"] == "fx2", "slate fixture first"
    assert [f["fixtureId"] for f in ordered[1:]] == ["fx1", "fx3"], "stable order"


def test_slate_match_tolerates_club_noise_and_orientation(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    _write_slate(tmp_path, [{
        "date": "2026-10-03", "home": "Croatia FC", "away": "England FC",
        "market": "1x2", "pick": "home",
    }])
    ordered, slate_n = cap._prioritise_slate_fixtures(_fixtures_list(), "2026-10-03")
    assert slate_n == 1
    assert ordered[0]["fixtureId"] == "fx2"


def test_other_day_picks_fall_back_to_same_day_archive(tmp_path, monkeypatch):
    """First run of a day: picks_today can still be yesterday's slate."""
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    _write_slate(tmp_path, [{
        "date": "2026-10-04", "home": "England", "away": "Croatia",
        "market": "1x2", "pick": "home",
    }])
    (tmp_path / "picks_2026-10-03.json").write_text(json.dumps([{
        "date": "2026-10-03", "home": "England", "away": "Croatia",
        "market": "1x2", "pick": "home", "avg_p": 92,
    }]))
    ordered, slate_n = cap._prioritise_slate_fixtures(_fixtures_list(), "2026-10-03")
    assert slate_n == 1
    assert ordered[0]["fixtureId"] == "fx2"


def test_slate_priority_uses_pick_confidence(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    _write_slate(tmp_path, [
        {"date": "2026-10-03", "home": "Alpha", "away": "Beta", "avg_p": 70},
        {"date": "2026-10-03", "home": "England", "away": "Croatia", "avg_p": 90},
    ])
    ordered, slate_n = cap._prioritise_slate_fixtures(_fixtures_list(), "2026-10-03")
    assert slate_n == 2
    assert [f["fixtureId"] for f in ordered[:2]] == ["fx2", "fx3"]


def test_no_slate_file_leaves_provider_order_untouched(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    ordered, slate_n = cap._prioritise_slate_fixtures(_fixtures_list(), "2026-10-03")
    assert slate_n == 0
    assert ordered == _fixtures_list()


# ---------------------------------------------------------------------------
# Expected-vs-loss classification
# ---------------------------------------------------------------------------


def test_provider_state_flags_are_expected_not_loss():
    split = cap._classify_parse_skips({
        "outcome_inactive": 10366,
        "market_inactive": 913,
        "alt_line_skipped": 40,
        "market_id_unknown": 5433,
        "unresolved_1x2": 238,
        "ambiguous_1x2": 7,
        "published_after_capture": 1,
    })
    assert split["expected"] == {
        "outcome_inactive": 10366, "market_inactive": 913, "alt_line_skipped": 40}
    assert split["loss_or_diagnosis"] == {
        "market_id_unknown": 5433, "unresolved_1x2": 238,
        "ambiguous_1x2": 7, "published_after_capture": 1}


# ---------------------------------------------------------------------------
# The census artefact
# ---------------------------------------------------------------------------


def test_capture_persists_the_market_census(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    catalog = op._market_catalog_entries(_catalog())
    type_map = {mid: op._classify_catalog_entry(e) for mid, e in catalog.items()}
    # The /fixtures record whose teams match the mocked /odds payload, as in
    # production (capture passes the fixture identity into the parser).
    fixture_record = {"fixtureId": "fx2", "participant1Name": "Croatia",
                      "participant2Name": "England"}
    monkeypatch.setattr(cap, "fetch_fixtures", lambda day: [fixture_record])
    monkeypatch.setattr(cap, "fetch_odds", lambda fid: _odds_payload())
    monkeypatch.setattr(cap, "load_market_type_map", lambda: type_map)
    monkeypatch.setattr(cap, "market_catalog", lambda: op._market_catalog_map(_catalog()))
    monkeypatch.setattr(cap, "market_catalog_entries", lambda: catalog)
    monkeypatch.setattr(cap, "api_keys", lambda: ("k",))
    monkeypatch.setattr(cap, "_append_rows", lambda rows, day: 0)

    stats = cap.capture("2026-10-03", max_fixtures=1)

    census_path = tmp_path / "oddspapi_market_census_2026-10.json"
    assert census_path.exists()
    census = json.loads(census_path.read_text())
    markets = census["markets"]
    # Every id present in the payload is enumerated with its classification.
    assert set(markets) >= {"101", "10194", "10262", "10701", "99999"}
    assert markets["101"]["type"] == "1x2"
    assert markets["101"]["label"] == "Full Time Result"
    assert markets["101"]["catalog"] is True
    assert markets["101"]["handicap"] == 0
    assert markets["10194"]["handicap"] == 2.5
    assert markets["10262"]["type"] == "unsupported_period"
    assert markets["99999"]["type"] is None
    assert markets["99999"]["catalog"] is False
    assert markets["99999"]["count"] == 1
    # Expected skips are separated from defects in the artefact: this
    # fixture carries no inactive flags; the demo feed exclusion is the
    # only expected skip, everything else is a defect/coverage signal.
    assert census["parse_skips"]["expected"] == {"internal_feed_bookmaker": 1}
    loss = census["parse_skips"]["loss_or_diagnosis"]
    assert loss["market_id_unknown"] == 1
    assert loss["ambiguous_1x2"] == 1
    assert loss["market_unsupported_period"] == 1
    assert loss["market_unsupported_handicap"] == 1
    # The ambiguity sample names the exact provider tuple.
    samples = census["unresolved_1x2_samples"]
    assert samples and samples[0]["market_id"] == "101"
    assert samples[0]["player_name"] == "England"
    # And the stats surface the census location + counts.
    assert stats["market_census"] == "oddspapi_market_census_2026-10.json"
    assert stats["market_census_distinct"] == len(markets)
    assert stats["slate_priority_fixtures"] == 0  # no slate file in tmp_path
    assert stats["attempted"] == 1
    receipt = json.loads((tmp_path / "oddspapi_capture_2026-10-03.json").read_text())
    assert receipt["attempted"] == 1
    assert receipt["attempted_fixtures"][0]["home"] == "Croatia"
    assert receipt["quoted_fixtures"][0]["away"] == "England"
    assert "apiKey" not in json.dumps(receipt) and "http" not in json.dumps(receipt)
    # The served catalog is persisted for source_health, provider data only.
    vocab_path = tmp_path / "source_health" / "odds_vocabulary" / "2026-10-03+oddspapi.json"
    assert vocab_path.exists()
    vocab = json.loads(vocab_path.read_text())
    assert vocab["catalog_size"] == len(catalog)
    assert vocab["markets"]["101"]["outcomes"] == {"101": "1", "102": "X", "103": "2"}
    assert stats["odds_vocabulary"] == "written"
    assert "http" not in vocab_path.read_text() and "apiKey" not in vocab_path.read_text()


def test_vocabulary_snapshot_is_content_deduped(tmp_path, monkeypatch):
    """An unchanged served catalog must not duplicate a snapshot per day."""
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    catalog = op._market_catalog_entries(_catalog())
    assert cap._persist_vocabulary_snapshot("2026-10-03", catalog) == "written"
    assert cap._persist_vocabulary_snapshot("2026-10-04", catalog) == "unchanged"
    vdir = tmp_path / "source_health" / "odds_vocabulary"
    assert [p.name for p in sorted(vdir.glob("*+oddspapi.json"))] == [
        "2026-10-03+oddspapi.json"]
    # A catalog that changed (new market) writes a new snapshot.
    grown = dict(catalog)
    grown["108"] = {"name": "Draw No Bet", "marketType": "x", "period": "fulltime",
                    "handicap": None, "playerProp": False, "outcomes": {}}
    assert cap._persist_vocabulary_snapshot("2026-10-04", grown) == "written"
    assert len(list((vdir).glob("*+oddspapi.json"))) == 2


def test_vocabulary_snapshot_absent_without_a_catalog(tmp_path, monkeypatch):
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    assert cap._persist_vocabulary_snapshot("2026-10-03", {}) == "absent"
    assert not (tmp_path / "source_health" / "odds_vocabulary").exists()


def test_census_and_vocabulary_are_state_commit_persistable():
    """Run 37138618268 wrote both artefacts and the state commit kept
    neither: `git add -A localdata/` silently skips ignored files, and
    ``localdata/*`` ignored them. Without these negations the census exists
    only in the 7-day Actions artifact and dies with the runner cache."""
    gitignore = (Path(__file__).resolve().parents[1] / ".gitignore").read_text()
    lines = {ln.strip() for ln in gitignore.splitlines()}
    assert "!localdata/theoddsapi_capture_20*.json" in lines
    assert "!localdata/oddspapi_capture_20*.json" in lines
    assert "!localdata/oddspapi_market_census_*.json" in lines
    assert "!localdata/source_health/" in lines
    assert "!localdata/source_health/**" in lines
    # And the negation actually wins over the localdata/* ignore.
    import subprocess
    for path in ("localdata/theoddsapi_capture_2026-10-03.json",
                 "localdata/oddspapi_capture_2026-10-03.json",
                 "localdata/oddspapi_market_census_2026-10.json",
                 "localdata/source_health/odds_vocabulary/2026-10-03+oddspapi.json"):
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-v", path],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True)
        # check-ignore -v prints "<file>:<line>:<pattern>\t<pathname>".
        decided = (result.stdout.split("\t")[0].rsplit(":", 1)[-1].strip()
                   if result.returncode == 0 else "")
        assert decided.startswith("!"), (
            f"{path} is ignored (git check-ignore said: "
            f"{result.stdout.strip() or result.stderr.strip() or '<no output>'}); "
            "the state commit would silently drop it")


def test_census_file_is_provider_data_only(tmp_path, monkeypatch):
    """The census must never carry credentials or request URLs."""
    monkeypatch.setattr(cap, "OUT_DIR", tmp_path)
    cap._persist_market_census(
        "2026-10-03",
        {"101": {"count": 3, "type": "1x2"}},
        {"outcome_inactive": 2, "unresolved_1x2": 1},
        [{"reason": "unresolved_1x2", "market_id": "101", "outcome_key": "101",
          "bookmaker_outcome_id": "", "player_name": "", "home": "A", "away": "B"}],
        {}, {},
    )
    text = (tmp_path / "oddspapi_market_census_2026-10.json").read_text()
    assert "apiKey" not in text and "http" not in text
