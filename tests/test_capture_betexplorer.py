from __future__ import annotations

import json

import scripts.capture_betexplorer as capture


def test_candidate_reader_prefers_fresh_picks_today_and_confidence_order(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    # Stale archive has a higher-confidence fixture, but the fresh candidate
    # slate must win when it is same-day.
    (tmp_path / "picks_2026-10-03.json").write_text(json.dumps([
        {"date": "2026-10-03", "home": "Archive", "away": "Only", "market": "1x2", "avg_p": 99},
    ]))
    rows = [
        {"date": "2026-10-03", "home": "Bravo", "away": "Zulu", "market": "1x2", "avg_p": 60},
        {"date": "2026-10-03", "home": "Alpha", "away": "Beta", "market": "1x2", "avg_p": 80, "w_score": 0.1},
        {"date": "2026-10-03", "home": "Alpha", "away": "Beta", "market": "1x2", "avg_p": 70},
        {"date": "2026-10-03", "home": "Skip", "away": "Me", "market": "btts", "avg_p": 99},
        {"date": "2026-10-04", "home": "Tomorrow", "away": "No", "market": "1x2", "avg_p": 99},
    ]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    candidates = capture._candidate_rows("2026-10-03")
    assert [(row["home"], row["away"]) for row in candidates] == [
        ("Alpha", "Beta"), ("Bravo", "Zulu"),
    ]


def test_candidate_reader_falls_back_to_same_day_archive(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    (tmp_path / "picks_today.json").write_text(json.dumps([
        {"date": "2026-10-04", "home": "Stale", "away": "Slate", "market": "1x2", "avg_p": 99},
    ]))
    (tmp_path / "picks_2026-10-03.json").write_text(json.dumps([
        {"date": "2026-10-03", "home": "Archive", "away": "Fallback", "market": "1x2", "avg_p": 70},
    ]))
    candidates = capture._candidate_rows("2026-10-03")
    assert [(row["home"], row["away"]) for row in candidates] == [("Archive", "Fallback")]


def test_capture_respects_raised_ceiling_and_persists_fixture_receipt(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(capture, "MAX_FIXTURES_CEILING", 24)
    rows = [
        {"date": "2026-10-03", "home": f"Home{i}", "away": f"Away{i}", "market": "1x2", "avg_p": 100 - i}
        for i in range(30)
    ]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))

    from edgefactory.sources import betexplorer_odds as be

    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "reset_fetch_count", lambda: None)
    monkeypatch.setattr(
        be,
        "betexplorer_odds_rows_for_pick",
        lambda pick, day, norm_team_fn=None: [
            {"date": day, "home": pick["home"], "away": pick["away"], "market": "1x2", "selection": "home", "odds": 2.0}
        ],
    )
    monkeypatch.setattr(be, "run_stats", lambda: {"be_429": 0, "be_cooling_down": False, "be_cached": 0, "be_fetches": 0})
    receipt = capture.capture("2026-10-03", max_fixtures=99)
    assert receipt["attempted"] == 24
    assert receipt["fixtures_with_rows"] == 24
    payload = json.loads((tmp_path / "betexplorer_capture_2026-10-03.json").read_text())
    assert len(payload["attempted_fixtures"]) == 24
    assert payload["attempted_fixtures"][0]["home"] == "Home0"


def test_enh_pricing_gaps_rank_ahead_of_parent_confidence(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    def row(home, confidence, gaps):
        return {"date": "2026-10-27", "home": home, "away": "Visitors",
                "market": "1x2", "avg_p": confidence, "enh_candidate_log": gaps}
    def gap(market, rate=.7, reason="unpriced"):
        return {"market": market, "cohort_rate": rate, "reason": reason}
    rows = [row("High parent", 99, []),
            row("Team only", 98, [gap("home_over_15")]),
            row("Out of band", 97, [gap("match_under_45", .95)]),
            row("Priced", 96, [gap("match_over_25", reason="below_min_leg_odds")]),
            row("One gap", 70, [gap("match_over_25")]),
            row("Two gaps", 65, [gap("match_under_35"), gap("match_under_45")])]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    assert [r["home"] for r in capture._candidate_rows("2026-10-27")][:2] == [
        "Two gaps", "One gap"]


def test_cached_empty_and_priced_fixtures_do_not_starve_fresh_capture(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    be.reset_fetch_count()
    day = "2026-10-27"
    rows = [{"date": day, "home": f"Home{i}", "away": f"Away{i}",
             "market": "1x2", "avg_p": 100-i} for i in range(16)]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    def odds(pick):
        return [{"date": day, "home": pick["home"], "away": pick["away"],
                 "market": "1x2", "selection": "home", "odds": 1.6}]
    # Twelve cache hits (including negative answers) previously consumed the
    # entire shortlist, so Home12+ never got a chance. Do not re-fetch negatives.
    for i, row in enumerate(rows[:12]):
        be._write_fixture_cache(row, day, [] if i % 2 else odds(row), detail=True)
    calls = []
    def fetch(pick, day, norm_team_fn=None):
        calls.append(pick["home"])
        return odds(pick)
    monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick", fetch)
    receipt = capture.capture(day, max_fixtures=2)
    assert calls == ["Home12", "Home13"]
    assert receipt["network_attempted"] == 2
    assert receipt["cache_only"] == 12
    assert receipt["deferred_fixtures"] == 2
    assert receipt["fixtures_with_rows"] == 8
    assert receipt["attempted"] == 14


def test_enh_gaps_ignore_malformed_or_duplicate_checks(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    rows = [{"date": "2026-10-27", "home": home, "away": "Visitors",
             "market": "1x2", "avg_p": confidence, "enh_candidate_log": notes}
            for home, confidence, notes in [
                ("Malformed", 99, [None, "bad", {}, {"reason": "unpriced", "market": "match_over_25", "cohort_rate": True}]),
                ("Repeated", 70, [{"reason": "unpriced", "market": "match_over_25", "cohort_rate": .7}] * 8),
                ("Two markets", 60, [{"reason": "unpriced", "market": market, "cohort_rate": .7}
                                     for market in ["match_over_25", "match_under_45"]])]]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    assert [r["home"] for r in capture._candidate_rows("2026-10-27")] == [
        "Two markets", "Repeated", "Malformed"]


def test_cached_rows_are_still_read_after_network_slots_are_exhausted(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    be.reset_fetch_count()
    day = "2026-10-27"
    rows = [{"date": day, "home": home, "away": "Visitors", "market": "1x2", "avg_p": 90-i}
            for i, home in enumerate(["Fresh", "Deferred", "Cached"])]
    monkeypatch.setattr(capture, "_candidate_rows", lambda day: rows)
    quote = dict(rows[2], selection="home", odds=1.6)
    be._write_fixture_cache(rows[2], day, [quote], detail=True)
    calls = []
    def fetch(pick, day, norm_team_fn=None):
        calls.append(pick["home"])
        return []
    monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick", fetch)
    receipt = capture.capture(day, max_fixtures=1)
    assert calls == ["Fresh"]
    assert receipt["cache_only"] == receipt["fixtures_with_rows"] == 1
    assert receipt["deferred_fixtures"] == 1


def test_zero_network_slots_never_fetch_or_reprice_poisoned_cache(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    be.reset_fetch_count()
    day = "2026-10-27"
    pick = {"date": day, "home": "Home", "away": "Away", "market": "1x2"}
    monkeypatch.setattr(capture, "_candidate_rows", lambda day: [pick])
    be._write_fixture_cache(pick, day, [dict(pick, home="Other Club", selection="home", odds=2)], detail=True)
    def forbidden(*args, **kwargs):
        raise AssertionError("zero budget must not fetch")
    monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick", forbidden)
    receipt = capture.capture(day, max_fixtures=0)
    assert receipt["network_attempted"] == 0
    assert receipt["fixtures_with_rows"] == 0
    assert receipt["be_rows_rejected"] == 1
    assert receipt["errors"] == []


def test_capture_preserves_adapter_cooldown(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    original_reset = be.reset_fetch_count
    def reset_with_cooldown():
        original_reset()
        be._be_cooling_down = True
    monkeypatch.setattr(be, "reset_fetch_count", reset_with_cooldown)
    monkeypatch.setattr(capture, "_candidate_rows", lambda day: [
        {"date": day, "home": "Home", "away": "Away", "market": "1x2"}])
    def forbidden(*args, **kwargs):
        raise AssertionError("cooldown must not request")
    monkeypatch.setattr(be, "_fetch", forbidden)
    receipt = capture.capture("2026-10-27", max_fixtures=2)
    assert receipt["requests"] == 0
    assert receipt["be_cooling_down"] is True
    assert receipt["errors"] == []


def test_cache_capture_classification_preserves_freshness_and_detail_upgrade(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    be.reset_fetch_count()
    day = "2026-10-27"
    pick = {"date": day, "home": "Home", "away": "Away", "market": "1x2"}
    quote = dict(pick, selection="home", odds=1.6)
    assert be.fixture_capture_needed(pick, day)
    be._write_fixture_cache(pick, day, [])
    assert not be.fixture_capture_needed(pick, day)
    be._write_fixture_cache(pick, day, [quote], detail=False)
    assert be.fixture_capture_needed(pick, day)  # existing one-time detail visit
    be._write_fixture_cache(pick, day, [quote], detail=True)
    assert not be.fixture_capture_needed(pick, day)
    cache = be._cache_path(day)
    payload = json.loads(cache.read_text())
    for entry in payload["fixtures"].values():
        entry["cached_at"] = "2000-01-01T00:00:00+00:00"
    cache.write_text(json.dumps(payload))
    assert be.fixture_capture_needed(pick, day)


# PR162 adversarial cases: each fails on the published a29ab1e patch.
def test_legacy_detail_upgrade_with_zero_budget_keeps_cached_quote(tmp_path, monkeypatch):
    _assert_deferred_legacy_quote(tmp_path, monkeypatch, budget=0)


def test_legacy_detail_upgrade_after_fresh_slot_keeps_cached_quote(tmp_path, monkeypatch):
    _assert_deferred_legacy_quote(tmp_path, monkeypatch, budget=1, fresh_first=True)


def test_legacy_detail_upgrade_during_cooldown_keeps_cached_quote(tmp_path, monkeypatch):
    _assert_deferred_legacy_quote(tmp_path, monkeypatch, budget=1, cooling=True)


def _assert_deferred_legacy_quote(tmp_path, monkeypatch, *, budget, fresh_first=False, cooling=False):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "MARKET_TABS_ENABLED", True)
    be.reset_fetch_count()
    day = "2026-10-27"
    legacy = {"date": day, "home": "Legacy", "away": "Visitors", "market": "1x2"}
    be._write_fixture_cache(legacy, day, [dict(legacy, selection="home", odds=1.6)], detail=False)
    picks = ([dict(legacy, home="Fresh")] if fresh_first else []) + [legacy]
    monkeypatch.setattr(capture, "_candidate_rows", lambda day: picks)
    reset = be.reset_fetch_count
    def reset_state():
        reset()
        be._be_cooling_down = cooling
    monkeypatch.setattr(be, "reset_fetch_count", reset_state)
    def fake_fetch(pick, day, **kwargs):
        assert pick["home"] == "Fresh", "a blocked detail upgrade must not request"
        return []
    if fresh_first:
        monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick", fake_fetch)
    else:
        monkeypatch.setattr(be, "_fetch", lambda *a, **kw: (_ for _ in ()).throw(AssertionError("no network")))
    receipt = capture.capture(day, max_fixtures=budget)
    assert receipt["fixtures_with_rows"] == 1
    assert receipt["cache_only"] == 1
    assert receipt["errors"] == []
    assert receipt["network_attempted"] == int(fresh_first)
    assert receipt["deferred_fixtures"] == 1
    assert be._read_fixture_cache(legacy, day)[0]["odds"] == 1.6


def test_capture_classification_failure_does_not_erase_other_fixtures(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    picks = [{"date": "2026-10-27", "home": home, "away": "Visitors", "market": "1x2"}
             for home in ["Broken", "Healthy"]]
    monkeypatch.setattr(capture, "_candidate_rows", lambda day: picks)
    def classify(pick, day):
        if pick["home"] == "Broken":
            raise ValueError("one malformed fixture")
        return True
    monkeypatch.setattr(be, "fixture_capture_needed", classify)
    monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick",
                        lambda pick, day, **kwargs: [dict(pick, selection="home", odds=1.6)])
    receipt = capture.capture("2026-10-27", max_fixtures=1)
    assert receipt["fixtures_with_rows"] == 1
    assert receipt["status"] == "ok"
    assert receipt["errors"] == ["ValueError"]


def test_oversized_optional_rate_cannot_abort_candidate_build(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    rows = [{"date": "2026-10-27", "home": home, "away": "Visitors", "market": "1x2",
             "avg_p": 70, "enh_candidate_log": [{"market": "match_over_25", "reason": "unpriced",
                                                   "cohort_rate": rate}]}
            for home, rate in [("Broken rate", 10**400), ("Valid rate", .7)]]
    (tmp_path / "picks_today.json").write_text(json.dumps(rows))
    assert [r["home"] for r in capture._candidate_rows("2026-10-27")] == ["Valid rate", "Broken rate"]


def test_nonfinite_parent_scores_do_not_make_order_depend_on_input(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    rows = [{"date": "2026-10-27", "home": home, "away": "Visitors", "market": "1x2", "avg_p": score}
            for home, score in [("NaN parent", "nan"), ("Finite parent", 80)]]
    for slate in [rows, rows[::-1]]:
        (tmp_path / "picks_today.json").write_text(json.dumps(slate))
        assert [r["home"] for r in capture._candidate_rows("2026-10-27")] == ["Finite parent", "NaN parent"]


def test_request_budget_exhaustion_keeps_legacy_and_never_attempts_fresh(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "MARKET_TABS_ENABLED", True)
    be.reset_fetch_count()
    day = "2026-10-27"
    legacy = {"date": day, "home": "Legacy", "away": "Visitors", "market": "1x2"}
    be._write_fixture_cache(legacy, day, [dict(legacy, selection="home", odds=1.6)], detail=False)
    monkeypatch.setattr(capture, "_candidate_rows", lambda day: [dict(legacy, home="Fresh"), legacy])
    reset = be.reset_fetch_count
    def reset_exhausted():
        reset()
        be._request_count = be._MAX_REQUESTS_PER_RUN
    monkeypatch.setattr(be, "reset_fetch_count", reset_exhausted)
    def forbidden(*args, **kwargs):
        raise AssertionError("exhausted transport budget must not be entered")
    monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick", forbidden)
    receipt = capture.capture(day, max_fixtures=2)
    assert receipt["network_attempted"] == 0
    assert receipt["cache_only"] == receipt["fixtures_with_rows"] == 1
    assert receipt["deferred_fixtures"] == 2
    assert receipt["errors"] == []


def test_cooldown_midpass_preserves_later_cached_quote(tmp_path, monkeypatch):
    from edgefactory.sources import betexplorer_odds as be
    monkeypatch.setattr(capture, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "LOCALDATA", tmp_path)
    monkeypatch.setattr(be, "MARKET_TABS_ENABLED", True)
    be.reset_fetch_count()
    day = "2026-10-27"
    picks = [{"date": day, "home": home, "away": "Visitors", "market": "1x2"}
             for home in ["Trigger", "Deferred", "Legacy"]]
    be._write_fixture_cache(picks[2], day, [dict(picks[2], selection="home", odds=1.6)], detail=False)
    monkeypatch.setattr(capture, "_candidate_rows", lambda day: picks)
    calls = []
    def fetch(pick, day, **kwargs):
        calls.append(pick["home"])
        be._be_cooling_down = True
        return []
    monkeypatch.setattr(be, "betexplorer_odds_rows_for_pick", fetch)
    receipt = capture.capture(day, max_fixtures=3)
    assert calls == ["Trigger"]
    assert receipt["network_attempted"] == 1
    assert receipt["fixtures_with_rows"] == receipt["cache_only"] == 1
    assert receipt["deferred_fixtures"] == 2
    assert receipt["errors"] == []
