"""Tests for the fresh_production lane.

Every fixture, team, score and price in this module is synthetic *on purpose*:
synthetic data is allowed inside unit tests and nowhere else. The production
path is separately asserted to refuse imputation and fabrication.
"""

from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fp = _load("fresh_production_under_test", "fresh_production.py")
cl = _load("clean_localdata_under_test", "clean_localdata.py")

from edgefactory import production_lane as pl  # noqa: E402

DAY = "2026-06-12"
AS_OF = datetime(2026, 6, 12, 8, 0, tzinfo=timezone(timedelta(hours=2)))


# ---------------------------------------------------------------- helpers


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _pred_rows(day, home, away, p1, px, p2, kickoff="18:00"):
    return {"date": day, "kickoff": kickoff, "league": "Test League",
            "home": home, "away": away, "p1": p1, "px": px, "p2": p2}


def _group(votes, *, kickoff="18:00", day=DAY, home="Alpha Town", away="Beta City"):
    g = fp.FixtureGroup(date=day, key=(fp.team_key(home), fp.team_key(away)),
                        home=home, away=away, league="Test League")
    g.votes = dict(votes)
    g.kickoff = kickoff
    g.kickoff_source = "zulubet" if kickoff else ""
    return g


def _history(tmp_path: Path, *, days: int = 120, per_day: int = 12,
             home_win_share: float = 0.9):
    """Deterministic synthetic history with two agreeing voters and labels.

    Two populations so the base rate and the rule hit rate differ:
    confident fixtures (consensus ~0.69 on home) that the home side wins
    ``home_win_share`` of the time, and coin-flip fixtures (consensus ~0.40)
    that no rule threshold can reach.
    """
    localdata = tmp_path / "localdata"
    localdata.mkdir(parents=True, exist_ok=True)
    zulu, star, results = [], [], []
    target = date.fromisoformat(DAY)
    for offset in range(1, days + 1):
        current = (target - timedelta(days=offset)).isoformat()
        for index in range(per_day):
            confident = index % 2 == 0
            prefix = "Home Team" if confident else "Coin Team"
            home, away = f"{prefix} {index:02d}", f"Away Team {index:02d}"
            p1, px, p2 = (70.0, 18.0, 12.0) if confident else (40.0, 32.0, 28.0)
            q1, qx, q2 = (68.0, 20.0, 12.0) if confident else (39.0, 33.0, 28.0)
            zulu.append(_pred_rows(current, home, away, p1, px, p2))
            star.append({"date": current, "time": "18:00", "league": "Test League",
                         "home": home, "away": away, "p1": q1, "px": qx, "p2": q2})
            share = home_win_share if confident else 0.4
            home_wins = (offset * per_day + index) % 10 < share * 10
            results.append({"date": current, "kickoff": "18:00", "country": "X",
                            "league": "Test League", "home": home, "away": away,
                            "hs": 2 if home_wins else 0, "gs": 0 if home_wins else 2,
                            "ht_hs": 1, "ht_gs": 0, "match_url": "",
                            "event_id": f"e{offset}-{index}", "fetched_at": ""})
    _write_csv(localdata / "zulubet.csv.gz",
               ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"], zulu)
    _write_csv(localdata / "statarea.csv.gz",
               ["date", "time", "league", "home", "away", "p1", "px", "p2"], star)
    _write_csv(localdata / "betexplorer_results_2026-06.csv.gz",
               ["date", "kickoff", "country", "league", "home", "away", "hs", "gs",
                "ht_hs", "ht_gs", "match_url", "event_id", "fetched_at"], results)
    return localdata


def _add_today(localdata: Path, *, with_odds: bool = True, odds: float = 2.50):
    """Append a today-dated fixture, optionally with a captured price.

    The price is written into the predictor rows themselves (``odd1``/
    ``oddx``/``odd2``), which is exactly how several existing sources
    publish it, so this exercises the ``source_embedded_price`` tier.
    """
    price = {"odd1": odds, "oddx": 3.4, "odd2": 4.2} if with_odds else {}
    for name, fields, row in (
        ("zulubet.csv.gz",
         ["date", "kickoff", "league", "home", "away", "p1", "px", "p2",
          "odd1", "oddx", "odd2"],
         {**_pred_rows(DAY, "Home Team 00", "Away Team 00", 70.0, 18.0, 12.0), **price}),
        ("statarea.csv.gz",
         ["date", "time", "league", "home", "away", "p1", "px", "p2"],
         {"date": DAY, "time": "18:00", "league": "Test League",
          "home": "Home Team 00", "away": "Away Team 00",
          "p1": 68.0, "px": 20.0, "p2": 12.0}),
    ):
        path = localdata / name
        existing = list(fp.iter_rows(path))
        _write_csv(path, fields, existing + [row])


def _run(localdata: Path, tmp_path: Path, **kwargs):
    return fp.run(localdata=localdata, day=DAY, output_dir=tmp_path / "out",
                  as_of=AS_OF, eval_days=90, train_days=30, **kwargs)


def _blockers(report) -> list[str]:
    return [b for c in report["candidates"] for b in c["blockers"]]


# ------------------------------------------------- 1. source universe


def test_fresh_production_excludes_parked_browser_dependent_predictors():
    voters = fp.fresh_production_voters()
    assert voters, "the fresh lane needs at least one current predictor"
    assert not (set(voters) & fp.PARKED_PREDICTORS)


def test_source_roles_label_pricing_and_donor_sources_separately():
    roles = fp.classify_source_roles()
    assert roles["betexplorer_odds"] == "pricing_provider"
    assert roles["betexplorer_results"] == "result_donor"
    assert roles["zulubet"] == "fresh_production_live_voter"
    assert roles["soccervista"] == "shadow_fresh_production_voter"


# ------------------------------------------------- 2. features


def test_feature_schema_contains_no_legacy_only_feature():
    names = [f["feature_name"] for f in fp.FEATURE_SCHEMA]
    assert fp.validate_feature_names(names) == []


def test_legacy_only_feature_names_are_detected_as_violations():
    # Regression guard for the exact legacy meta-model vector.
    assert fp.validate_feature_names(["fb_p", "top_probability", "goalsavg"]) == [
        "fb_p", "goalsavg"]


def test_features_require_two_current_source_voters():
    assert fp.build_features(_group({"zulubet": (0.7, 0.2, 0.1)})) is None


def test_features_are_computed_from_current_source_consensus():
    features = fp.build_features(_group({
        "zulubet": (0.70, 0.20, 0.10), "statarea": (0.60, 0.25, 0.15)}))
    assert features["number_of_1x2_voters"] == 2
    assert features["top_outcome"] == "home"
    assert features["top_probability"] == pytest.approx(0.65)
    assert features["margin_top_vs_second"] == pytest.approx(0.65 - 0.225)
    assert features["unanimous_outcome"] is True
    assert features["agreement_ratio"] == 1.0
    assert features["source_combination"] == "statarea+zulubet"


def test_disagreeing_voters_lower_the_agreement_ratio():
    features = fp.build_features(_group({
        "zulubet": (0.70, 0.15, 0.15), "statarea": (0.20, 0.20, 0.60)}))
    assert features["agreement_ratio"] == 0.5
    assert features["unanimous_outcome"] is False


def test_probability_parsing_refuses_partial_rows_instead_of_imputing():
    assert fp.probs_1x2({"p1": "50", "px": "", "p2": "20"}) is None
    assert fp.probs_1x2({"p1": "0", "px": "0", "p2": "0"}) is None
    assert fp.probs_1x2({"p1": "50", "px": "30", "p2": "20"}) == pytest.approx((0.5, 0.3, 0.2))


def test_schema_violations_reports_missing_required_features():
    features = fp.build_features(_group({
        "zulubet": (0.7, 0.2, 0.1), "statarea": (0.6, 0.25, 0.15)}))
    features["top_probability"] = None
    assert fp.schema_violations(features) == ["top_probability"]


# ------------------------------------------------- 3. labels


def test_settlement_labels_refuse_conflicting_donors(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / "settled_results.json").write_text(json.dumps({"rows": [
        {"date": DAY, "home": "Alpha Town", "away": "Beta City", "hs": 2, "gs": 0,
         "src": "overlay"}]}))
    _write_csv(localdata / "betexplorer_results_2026-06.csv.gz",
               ["date", "home", "away", "hs", "gs"],
               [{"date": DAY, "home": "Alpha Town", "away": "Beta City",
                 "hs": 0, "gs": 3}])
    labels = fp.load_settlement_labels(localdata, start="2026-01-01", end=DAY)
    assert labels == {}


def test_settlement_labels_accept_agreeing_donors(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / "settled_results.json").write_text(json.dumps({"rows": [
        {"date": DAY, "home": "Alpha Town", "away": "Beta City", "hs": 2, "gs": 0,
         "src": "overlay"}]}))
    _write_csv(localdata / "betexplorer_results_2026-06.csv.gz",
               ["date", "home", "away", "hs", "gs"],
               [{"date": DAY, "home": "Alpha Town", "away": "Beta City",
                 "hs": 2, "gs": 0}])
    labels = fp.load_settlement_labels(localdata, start="2026-01-01", end=DAY)
    label = labels[(DAY, (fp.team_key("Alpha Town"), fp.team_key("Beta City")))]
    assert label["outcome"] == "home" and label["donor_count"] == 2


# ------------------------------------------------- 4. identity safety


def test_same_source_spelling_collision_is_flagged_ambiguous(tmp_path):
    localdata = tmp_path / "localdata"
    _write_csv(localdata / "zulubet.csv.gz",
               ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"],
               [_pred_rows(DAY, "Alpha Town FC", "Beta City", 70, 20, 10),
                _pred_rows(DAY, "Alpha Town", "Beta City", 40, 30, 30)])
    groups = fp.load_fixture_groups(localdata, start=DAY, end=DAY,
                                    voters=("zulubet",), engine=None)
    assert any(g.ambiguous for g in groups.values())


def test_reversed_orientation_duplicate_is_flagged(tmp_path):
    localdata = tmp_path / "localdata"
    _write_csv(localdata / "zulubet.csv.gz",
               ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"],
               [_pred_rows(DAY, "Alpha Town", "Beta City", 70, 20, 10),
                _pred_rows(DAY, "Beta City", "Alpha Town", 70, 20, 10)])
    groups = fp.load_fixture_groups(localdata, start=DAY, end=DAY,
                                    voters=("zulubet",), engine=None)
    assert all(g.reversed_risk for g in groups.values())


def test_cross_source_spelling_differences_are_not_ambiguous(tmp_path):
    localdata = tmp_path / "localdata"
    _write_csv(localdata / "zulubet.csv.gz",
               ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"],
               [_pred_rows(DAY, "Alpha Town", "Beta City", 70, 20, 10)])
    _write_csv(localdata / "statarea.csv.gz",
               ["date", "time", "league", "home", "away", "p1", "px", "p2"],
               [{"date": DAY, "time": "18:00", "league": "L", "home": "Alpha Town FC",
                 "away": "Beta City", "p1": 65, "px": 22, "p2": 13}])
    groups = fp.load_fixture_groups(localdata, start=DAY, end=DAY,
                                    voters=("zulubet", "statarea"), engine=None)
    assert not any(g.ambiguous for g in groups.values())


# ------------------------------------------------- 5. walk-forward


def test_wilson_lower_bound_is_below_the_point_estimate():
    assert fp.wilson_lower_bound(70, 100) < 0.70
    assert fp.wilson_lower_bound(0, 0) == 0.0


def test_walk_forward_certifies_a_rule_on_strong_evidence(tmp_path):
    localdata = _history(tmp_path)
    report = _run(localdata, tmp_path, write=False)
    assert report["certified_rule_count"] >= 1
    assert report["walkforward"]["fixtures_labelled"] > 0


def test_walk_forward_certifies_nothing_on_a_thin_sample(tmp_path):
    localdata = _history(tmp_path, days=5, per_day=2)
    report = _run(localdata, tmp_path, write=False)
    assert report["certified_rule_count"] == 0
    evidence = report["_evidence"]
    blockers = {b.split(" ")[0] for ev in evidence.values() for b in ev.blockers}
    assert "insufficient_walkforward_sample" in blockers


def test_walk_forward_certifies_nothing_when_the_rule_has_no_lift(tmp_path):
    # Confident fixtures land at exactly the overall base rate: no lift,
    # so no rule may be certified however large the sample.
    localdata = _history(tmp_path, home_win_share=0.4)
    report = _run(localdata, tmp_path, write=False)
    assert report["certified_rule_count"] == 0
    assert any("insufficient_lift_over_base_rate" in b
               for ev in report["_evidence"].values() for b in ev.blockers)


def test_legacy_certified_edges_never_certify_fresh_production(tmp_path):
    localdata = _history(tmp_path, days=5, per_day=2)
    (localdata / "edges_consensus.json").write_text(json.dumps(
        {"certified": [{"rule_id": "legacy_rule", "certified": True}]}))
    report = _run(localdata, tmp_path, write=False)
    assert report["certified_rule_count"] == 0
    # No legacy rule may appear in the production lane's evidence, and every
    # production rule uses the canonical identifier form.
    assert "legacy_rule" not in report["_evidence"]
    assert all(ev.rule_id.startswith("1x2_") for ev in report["_evidence"].values())


def test_certification_registry_is_written_to_its_own_file(tmp_path):
    localdata = _history(tmp_path)
    _run(localdata, tmp_path, write=True)
    registry = json.loads((tmp_path / "out" / "fresh_production_certified_edges.json").read_text())
    assert registry["model_version"] == fp.MODEL_VERSION
    assert "legacy" not in json.dumps(registry["certified_dispatchable_rules"]).lower()
    for bucket in ("certified_dispatchable_rules", "research_rules", "blocked_rules"):
        assert bucket in registry


# ------------------------------------------------- 6. out-of-distribution


def test_out_of_distribution_guard_rejects_an_unseen_voter_count():
    envelope = {"empty": False, "voters_min": 2, "voters_max": 2,
                "top_probability_min": 0.5, "top_probability_max": 0.8,
                "agreement_ratio_min": 0.5, "agreement_ratio_max": 1.0,
                "source_combinations": ["statarea+zulubet"]}
    features = fp.build_features(_group({
        "zulubet": (0.7, 0.2, 0.1), "statarea": (0.7, 0.2, 0.1),
        "vitibet": (0.7, 0.2, 0.1)}))
    reasons = fp.out_of_distribution_reasons(features, envelope)
    assert any("voter count" in r for r in reasons)
    assert "unseen_source_combo" in reasons


def test_empty_envelope_blocks_everything():
    features = fp.build_features(_group({
        "zulubet": (0.7, 0.2, 0.1), "statarea": (0.7, 0.2, 0.1)}))
    reasons = fp.out_of_distribution_reasons(features, {"empty": True,
                                                        "source_combinations": []})
    assert reasons and reasons[0].startswith("blocked_out_of_distribution")


# ------------------------------------------------- 7. candidates and dispatch


def test_a_supported_candidate_becomes_a_dispatchable_pick(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    report = _run(localdata, tmp_path, write=False)
    picks = report["dispatchable_picks"]
    assert len(picks) == 1
    pick = picks[0]
    assert pick["selection"] == "home"
    # Rule IDs describe the rule, not a release, and carry no lane prefix.
    assert pick["rule_id"].startswith("1x2_")
    assert not pick["rule_id"].startswith("fresh_")
    assert pick["odds"] == 2.50
    assert pick["edge"] > 0
    assert pick["pricing_source"]
    assert pick["dispatch_method"] == fp.DISPATCH_RULE
    assert pick["price_tier"] in (fp.PRICE_TIER_DEDICATED,
                                  fp.PRICE_TIER_SOURCE_EMBEDDED)
    assert pick["internal_stake_units"] == fp.FLAT_STAKE_UNITS
    assert pick["model_health_status"] == "scored"
    assert pick["feature_schema_version"] == fp.FEATURE_SCHEMA_VERSION
    assert pick["blockers"] == []


def test_a_candidate_without_a_price_is_not_dispatchable(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, with_odds=False)
    report = _run(localdata, tmp_path, write=False)
    assert report["dispatchable_count"] == 0
    assert any(b.startswith(fp.BLOCKER_MISSING_ODDS)
               for c in report["candidates"] for b in c["blockers"])


def test_a_short_price_blocks_dispatch_on_insufficient_edge(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=1.05)
    report = _run(localdata, tmp_path, write=False)
    assert report["dispatchable_count"] == 0
    assert any(b.startswith(fp.BLOCKER_INSUFFICIENT_EDGE)
               for c in report["candidates"] for b in c["blockers"])


def test_a_single_voter_fixture_is_blocked_not_imputed(tmp_path):
    localdata = _history(tmp_path)
    path = localdata / "zulubet.csv.gz"
    rows = list(fp.iter_rows(path))
    rows.append(_pred_rows(DAY, "Lonely United", "Nobody FC", 80, 12, 8))
    _write_csv(path, ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"], rows)
    report = _run(localdata, tmp_path, write=False)
    lonely = [c for c in report["candidates"] if c["home"] == "Lonely United"]
    assert len(lonely) == 1
    assert lonely[0]["probability"] == 0.0
    assert any(b.startswith(fp.BLOCKER_VOTER_QUORUM) for b in lonely[0]["blockers"])
    assert not any(b.startswith(fp.BLOCKER_MISSING_FEATURE)
                   for b in lonely[0]["blockers"])
    assert lonely[0]["dispatchable"] is False


def test_dispatch_is_capped_per_day():
    assert fp.MAX_DISPATCH_PICKS_PER_DAY >= 1
    assert fp.MAX_TOTAL_EXPOSURE_UNITS >= fp.FLAT_STAKE_UNITS


def test_every_candidate_carries_provenance(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata)
    report = _run(localdata, tmp_path, write=False)
    for candidate in report["candidates"]:
        for field in ("date", "home", "away", "source_voters", "timing_source",
                      "identity_match_tier", "feature_schema_version", "model_version",
                      "model_health_status", "blockers"):
            assert field in candidate


# ------------------------------------------------- 8. health checks


def test_model_health_flags_a_legacy_feature_leak():
    warnings = fp.model_health_checks(
        candidates=[], evidence={}, envelope={"empty": False},
        feature_names=["top_probability", "kelly"])
    assert any("legacy-only predictor features" in w for w in warnings)
    assert all(w.startswith("MODEL_HEALTH:") for w in warnings)


def test_source_health_warns_when_nothing_is_dispatchable(tmp_path):
    warnings = fp.source_health_checks(
        groups={}, day=DAY, candidates=[], evidence={}, pricing={},
        roles=fp.classify_source_roles())
    assert any("no dispatchable picks" in w for w in warnings)
    assert all(w.startswith("SOURCE_HEALTH:") for w in warnings)


def test_health_warning_names_are_professional():
    banned = ("roach", "bug", "pest", "crisis", "panic", "nuke", "yolo")
    text = (Path(ROOT / "scripts" / "fresh_production.py").read_text().lower()
            + Path(ROOT / "scripts" / "clean_localdata.py").read_text().lower())
    assert not [word for word in banned if word in text]


# ------------------------------------------------- 9. artifacts


def test_run_writes_every_required_artifact(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata)
    _run(localdata, tmp_path, write=True)
    out = tmp_path / "out"
    for stem in ("fresh_production_walkforward", "fresh_production_certified_edges",
                 "fresh_production_candidate_picks", "fresh_production_dispatchable_picks",
                 "source_health", "model_health"):
        assert (out / f"{stem}_{DAY}.json").exists(), stem
        assert (out / f"{stem}_{DAY}.md").exists(), stem
    assert (out / "fresh_production_certified_edges.json").exists()
    schema = json.loads((out / fp.MODEL_DIR_NAME / "feature_schema.json").read_text())
    assert schema["version"] == fp.FEATURE_SCHEMA_VERSION
    assert (out / fp.MODEL_DIR_NAME / f"model_card_{DAY}.md").exists()


def test_no_picks_markdown_lists_exact_blockers(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, with_odds=False)
    _run(localdata, tmp_path, write=True)
    text = (tmp_path / "out" / f"fresh_production_dispatchable_picks_{DAY}.md").read_text()
    assert "FRESH PRODUCTION — NO PICKS" in text
    assert "missing_odds" in text


def test_picks_markdown_is_headed_fresh_production_picks(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    _run(localdata, tmp_path, write=True)
    text = (tmp_path / "out" / f"fresh_production_dispatchable_picks_{DAY}.md").read_text()
    assert text.startswith("# FRESH PRODUCTION PICKS")
    assert "never legacy_baseline" in text
    # Staking is the ticket layer's job; the pick report must not size bets.
    assert fp.STAKING_POLICY in text


def test_run_is_deterministic(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata)
    first = _run(localdata, tmp_path, write=False)
    second = _run(localdata, tmp_path, write=False)
    assert json.dumps(first["candidates"], sort_keys=True) == \
        json.dumps(second["candidates"], sort_keys=True)


def test_cli_runs_without_network_and_reports_abstention(tmp_path, capsys):
    localdata = _history(tmp_path, days=5, per_day=2)
    code = fp.main(["--date", DAY, "--mode", "official",
                    "--output-dir", str(tmp_path / "out"),
                    "--localdata", str(localdata),
                    "--as-of", AS_OF.isoformat()])
    assert code == 0
    assert "FRESH PRODUCTION — NO PICKS" in capsys.readouterr().out


# ------------------------------------------------- 10. data retention


def test_retention_policy_matches_only_known_generated_prefixes():
    assert cl.classify_fresh_production(f"fresh_production_walkforward_{DAY}.json")
    assert cl.classify_fresh_production(f"model_health_{DAY}.md")
    assert cl.classify_fresh_production("zulubet.csv.gz") is None
    assert cl.classify_fresh_production("settled_results.json") is None
    assert cl.classify_fresh_production("team_aliases.json") is None
    assert cl.classify_fresh_production("betexplorer_results_2026-06.csv.gz") is None


def test_retention_keeps_raw_evidence_and_unmatched_files(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    keep = ["zulubet.csv.gz", "settled_results.json", "team_aliases.json",
            "HANDOVER_copy.md", "betexplorer_results_2026-01.csv.gz",
            "something_unknown_2020-01-01.json"]
    for name in keep:
        (root / name).write_text("x")
    for day in ("2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"):
        (root / f"model_health_{day}.json").write_text("x")
    stale = cl.fresh_production_files_to_prune(root, keep_days=30, keep_latest=3,
                                               today=date(2026, 9, 30))
    assert [p.name for p in stale] == ["model_health_2020-01-01.json"]


def test_retention_keeps_the_latest_n_dates_per_prefix(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    for day in ("2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"):
        (root / f"source_health_{day}.json").write_text("x")
    stale = cl.fresh_production_files_to_prune(root, keep_days=30, keep_latest=3,
                                               today=date(2026, 9, 30))
    assert [p.name for p in stale] == ["source_health_2020-01-01.json"]


def test_retention_never_removes_the_current_target_date(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    for day in ("2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05"):
        (root / f"source_health_{day}.json").write_text("x")
    stale = cl.fresh_production_files_to_prune(
        root, keep_days=30, keep_latest=3, today=date(2026, 9, 30),
        target_date=date(2020, 1, 1))
    assert "source_health_2020-01-01.json" not in [p.name for p in stale]


def test_retention_manifest_records_files_and_bytes(tmp_path, capsys):
    root = tmp_path / "localdata"
    root.mkdir()
    (root / "model_health_2020-01-01.json").write_text("x" * 100)
    for day in ("2020-01-02", "2020-01-03", "2020-01-04"):
        (root / f"model_health_{day}.json").write_text("y")
    code = cl.main(["--policy", "fresh_production", "--keep-days", "30",
                    "--keep-latest", "3", "--write-manifest",
                    "--localdata", str(root), "--today", "2026-09-30"])
    assert code == 0
    manifest = json.loads((root / "artifact_manifest_2026-09-30.json").read_text())
    assert manifest["files_deleted"] == 1 and manifest["bytes_deleted"] == 100
    assert not (root / "model_health_2020-01-01.json").exists()
    assert (root / "artifact_manifest_2026-09-30.md").read_text().startswith(
        "# artifact_manifest")


def test_retention_dry_run_deletes_nothing(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    for day in ("2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"):
        (root / f"model_health_{day}.json").write_text("x")
    cl.main(["--policy", "fresh_production", "--localdata", str(root),
             "--today", "2026-09-30", "--dry-run"])
    assert (root / "model_health_2020-01-01.json").exists()


def test_default_telemetry_policy_is_unchanged(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    (root / "clv_report_2020-01-01.md").write_text("x")
    (root / "zulubet.csv.gz").write_text("x")
    stale = cl.files_to_prune(root, keep_days=30, today=date(2026, 9, 30))
    assert [p.name for p in stale] == ["clv_report_2020-01-01.md"]


# ------------------------------------------------- 11. production lane


def test_fresh_production_is_the_default_production_lane():
    assert pl.active_lane({}) == pl.LANE_FRESH_PRODUCTION
    assert pl.fresh_production_is_active({})
    assert pl.legacy_dispatch_allowed({}) is False


def test_lane_can_be_switched_back_to_legacy_baseline():
    env = {pl.ENV_VAR: "legacy_baseline"}
    assert pl.active_lane(env) == pl.LANE_LEGACY_BASELINE
    assert pl.legacy_dispatch_allowed(env) is True


def test_an_unknown_lane_value_falls_back_to_the_safe_default():
    assert pl.active_lane({pl.ENV_VAR: "nonsense"}) == pl.LANE_FRESH_PRODUCTION


def test_production_picks_path_points_at_the_fresh_lane(tmp_path, monkeypatch):
    monkeypatch.setenv(pl.ENV_VAR, "fresh_production")
    path = pl.production_picks_path(DAY, tmp_path)
    assert path.name == f"fresh_production_production_picks_{DAY}.json"


def test_legacy_picks_are_never_the_production_source_in_fresh_mode(tmp_path, monkeypatch):
    monkeypatch.setenv(pl.ENV_VAR, "fresh_production")
    (tmp_path / f"picks_{DAY}.json").write_text(json.dumps(
        [{"date": DAY, "home": "Legacy Home", "away": "Legacy Away", "pick": "home"}]))
    assert pl.load_production_picks(DAY, tmp_path) == []
    info = pl.describe(DAY, tmp_path)
    assert info["production_lane"] == "fresh_production"
    assert info["production_pick_count"] == 0
    assert info["fallback_to_other_lane"] is False


def test_zero_fresh_picks_publishes_an_explicit_empty_slate(tmp_path, monkeypatch):
    monkeypatch.setenv(pl.ENV_VAR, "fresh_production")
    (tmp_path / f"picks_{DAY}.json").write_text(json.dumps([{"date": DAY}]))
    path = pl.ensure_production_picks_file(DAY, tmp_path)
    assert path.exists() and json.loads(path.read_text()) == []


def test_fresh_dispatchable_picks_are_the_production_rows(tmp_path, monkeypatch):
    monkeypatch.setenv(pl.ENV_VAR, "fresh_production")
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    _run(localdata, tmp_path, write=True)
    rows = pl.load_production_picks(DAY, tmp_path / "out")
    assert len(rows) == 1
    assert rows[0]["lane"] == "fresh_production"
    assert rows[0]["home"] == "Home Team 00"
    assert rows[0]["bucket"] == "FRESH_PRODUCTION_CERTIFIED"


def test_production_pick_rows_are_written_even_when_empty(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, with_odds=False)
    _run(localdata, tmp_path, write=True)
    path = tmp_path / "out" / f"fresh_production_production_picks_{DAY}.json"
    assert json.loads(path.read_text()) == []


# ------------------------------------------------- 12. blocker precision


def test_missing_price_is_reported_as_missing_odds_not_missing_feature(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, with_odds=False)
    report = _run(localdata, tmp_path, write=False)
    target = [c for c in report["candidates"] if c["home"] == "Home Team 00"][0]
    assert any(b.startswith(fp.BLOCKER_MISSING_ODDS) for b in target["blockers"])
    assert not any(b.startswith(fp.BLOCKER_MISSING_FEATURE) for b in target["blockers"])


def test_missing_kickoff_is_reported_as_missing_trusted_kickoff(tmp_path):
    localdata = _history(tmp_path)
    for name, fields, row in (
        ("zulubet.csv.gz",
         ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"],
         {**_pred_rows(DAY, "Timeless United", "Clockless City", 70.0, 18.0, 12.0),
          "kickoff": ""}),
        ("statarea.csv.gz",
         ["date", "time", "league", "home", "away", "p1", "px", "p2"],
         {"date": DAY, "time": "", "league": "L", "home": "Timeless United",
          "away": "Clockless City", "p1": 68.0, "px": 20.0, "p2": 12.0}),
    ):
        path = localdata / name
        _write_csv(path, fields, list(fp.iter_rows(path)) + [row])
    report = _run(localdata, tmp_path, write=False)
    target = [c for c in report["candidates"] if c["home"] == "Timeless United"][0]
    assert any(b.startswith(fp.BLOCKER_MISSING_KICKOFF) for b in target["blockers"])
    assert not any(b.startswith(fp.BLOCKER_MISSING_FEATURE) for b in target["blockers"])


def test_ambiguous_identity_is_reported_as_an_identity_blocker(tmp_path):
    localdata = _history(tmp_path)
    path = localdata / "zulubet.csv.gz"
    fields = ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"]
    _write_csv(path, fields, list(fp.iter_rows(path)) + [
        _pred_rows(DAY, "Mirror Town", "Glass City", 70, 20, 10),
        _pred_rows(DAY, "Mirror Town FC", "Glass City", 40, 30, 30)])
    report = _run(localdata, tmp_path, write=False)
    target = [c for c in report["candidates"] if c["home"].startswith("Mirror Town")][0]
    assert any(b.startswith(fp.BLOCKER_IDENTITY) for b in target["blockers"])


def test_voter_quorum_blocker_is_not_a_missing_feature_blocker(tmp_path):
    localdata = _history(tmp_path)
    path = localdata / "zulubet.csv.gz"
    _write_csv(path, ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"],
               list(fp.iter_rows(path)) + [
                   _pred_rows(DAY, "Solo Rangers", "Silent Athletic", 80, 12, 8)])
    report = _run(localdata, tmp_path, write=False)
    target = [c for c in report["candidates"] if c["home"] == "Solo Rangers"][0]
    blocker = [b for b in target["blockers"] if b.startswith(fp.BLOCKER_VOTER_QUORUM)][0]
    assert "1 current-source 1X2 voter(s), 2 required" in blocker
    assert "zulubet" in blocker


def test_missing_required_feature_blocker_names_the_exact_features():
    features = fp.build_features(_group({
        "zulubet": (0.7, 0.2, 0.1), "statarea": (0.6, 0.25, 0.15)}))
    features["top_probability"] = None
    assert fp.schema_violations(features) == ["top_probability"]


def test_insufficient_edge_blocker_states_odds_implied_probability_and_edge(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=1.05)
    report = _run(localdata, tmp_path, write=False)
    target = [c for c in report["candidates"] if c["home"] == "Home Team 00"][0]
    blocker = [b for b in target["blockers"]
               if b.startswith(fp.BLOCKER_INSUFFICIENT_EDGE)][0]
    for fragment in ("probability", "implied", "odds 1.05", "edge", "threshold"):
        assert fragment in blocker
    assert target["odds"] == 1.05
    assert target["implied_probability"] is not None
    assert target["edge"] is not None


# ------------------------------------------------- 13. dispatch paths


def test_rule_dispatch_does_not_require_model_only_features(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    report = _run(localdata, tmp_path, write=False)
    pick = report["dispatchable_picks"][0]
    assert pick["dispatch_method"] == fp.DISPATCH_RULE
    # The rule needs strictly fewer features than the model schema.
    assert set(fp.RULE_INPUT_FEATURES) < set(fp.REQUIRED_FEATURES)


def test_a_rule_candidate_is_not_blocked_by_an_unseen_source_combination(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    report = _run(localdata, tmp_path, write=False)
    pick = report["dispatchable_picks"][0]
    assert not any(b.startswith(fp.BLOCKER_OOD) for b in pick["blockers"])
    assert "unseen_source_combo" not in pick["blockers"]


def test_model_dispatch_still_enforces_the_full_feature_schema():
    features = fp.build_features(_group({
        "zulubet": (0.7, 0.2, 0.1), "statarea": (0.6, 0.25, 0.15)}))
    features["probability_entropy"] = None
    assert "probability_entropy" in fp.schema_violations(features)


def test_artifacts_label_the_dispatch_method(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    _run(localdata, tmp_path, write=True)
    text = (tmp_path / "out" / f"fresh_production_dispatchable_picks_{DAY}.md").read_text()
    assert fp.DISPATCH_RULE in text


# ------------------------------------------------- 14. rule lifecycle


def test_rules_are_split_into_dispatchable_research_and_blocked(tmp_path):
    localdata = _history(tmp_path)
    report = _run(localdata, tmp_path, write=False)
    buckets = fp.rule_lifecycle(report["_evidence"])
    assert set(buckets) == {fp.RULE_CERTIFIED, fp.RULE_RESEARCH, fp.RULE_BLOCKED}
    total = sum(len(v) for v in buckets.values())
    assert total == len(report["_evidence"])
    assert report["certified_rule_count"] == len(buckets[fp.RULE_CERTIFIED])


def test_certified_means_dispatch_eligible(tmp_path):
    localdata = _history(tmp_path)
    report = _run(localdata, tmp_path, write=False)
    for ev in fp.rule_lifecycle(report["_evidence"])[fp.RULE_CERTIFIED]:
        assert ev.certified and not ev.blockers


def test_calibration_gates_the_model_path_not_the_rule_path():
    ev = fp.RuleEvidence(rule_id="r", sample=500, wins=340, recent_sample=60,
                         hit_rate=0.68, hit_rate_lb=0.64, base_rate=0.5, lift=0.18,
                         calibration=[{"bucket": "60-70%", "sample": 5,
                                       "mean_predicted": 0.65,
                                       "observed_hit_rate": 0.68,
                                       "sufficient_sample": False}])
    assert fp.rule_certification_blockers(ev, 100, 0) == []
    assert not any(b.startswith(fp.BLOCKER_CALIBRATION)
                   for b in fp.rule_certification_blockers(ev, 100, 0))


def test_a_rule_that_can_never_dispatch_is_not_counted_as_certified(tmp_path):
    localdata = _history(tmp_path, days=5, per_day=2)
    report = _run(localdata, tmp_path, write=False)
    assert report["certified_rule_count"] == 0
    registry = report["_certified_payload"]
    assert registry["certified_dispatchable_rules"] == []


# ------------------------------------------------- 15. pricing diagnostics


def test_pricing_diagnostics_count_candidates_before_and_after_pricing(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    report = _run(localdata, tmp_path, write=False)
    pricing = report["pricing"]
    assert pricing["candidate_count_before_pricing"] >= 1
    assert pricing["candidate_count_with_any_price"] >= 1
    assert pricing["candidate_count_with_positive_edge"] >= 1
    assert pricing["price_tiers_used"]


def test_pricing_diagnostics_count_missing_prices(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, with_odds=False)
    report = _run(localdata, tmp_path, write=False)
    assert report["pricing"]["candidate_count_missing_price"] >= 1
    assert report["pricing"]["candidate_count_with_any_price"] == 0


def test_source_embedded_prices_are_labelled_as_such(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    report = _run(localdata, tmp_path, write=False)
    pick = report["dispatchable_picks"][0]
    assert pick["price_tier"] == fp.PRICE_TIER_SOURCE_EMBEDDED
    assert pick["pricing_source"] == "source_embedded_odds"


# ------------------------------------------------- 16. summary output


def test_official_summary_prints_counts_and_top_blockers(tmp_path, capsys):
    localdata = _history(tmp_path)
    _add_today(localdata, with_odds=False)
    fp.main(["--date", DAY, "--output-dir", str(tmp_path / "out"),
             "--localdata", str(localdata), "--as-of", AS_OF.isoformat()])
    out = capsys.readouterr().out
    assert "FRESH PRODUCTION SUMMARY" in out
    assert "certified dispatchable rules:" in out
    assert "research rules:" in out
    assert "priced candidates:" in out
    assert "top blockers:" in out
    assert fp.BLOCKER_MISSING_ODDS in out
    assert "FRESH PRODUCTION — NO PICKS" in out


def test_official_summary_lists_picks_when_they_exist(tmp_path, capsys):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=2.50)
    fp.main(["--date", DAY, "--output-dir", str(tmp_path / "out"),
             "--localdata", str(localdata), "--as-of", AS_OF.isoformat()])
    out = capsys.readouterr().out
    assert "dispatchable picks:            1" in out
    assert "Home Team 00 vs Away Team 00" in out
    assert "staking=handled_by_auto_tickets" in out
    assert "stake=1.0u" not in out


# ------------------------------------------------- 17. report cleanliness


def test_fresh_reports_do_not_present_parked_sources_as_live(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata)
    _run(localdata, tmp_path, write=True)
    out = tmp_path / "out"
    health = (out / f"source_health_{DAY}.md").read_text()
    production_section = health.split("## legacy_baseline / historical_reference")[0]
    for parked in fp.PARKED_PREDICTORS:
        assert parked not in production_section
    payload = json.loads((out / f"source_health_{DAY}.json").read_text())
    for parked in fp.PARKED_PREDICTORS:
        assert parked not in payload["current_production_roles"]
        assert parked in payload["historical_reference"]


def test_model_card_does_not_name_parked_sources_in_the_universe(tmp_path):
    localdata = _history(tmp_path)
    _run(localdata, tmp_path, write=True)
    card = (tmp_path / "out" / fp.MODEL_DIR_NAME / f"model_card_{DAY}.md").read_text()
    universe = [line for line in card.splitlines() if line.startswith("- source universe:")]
    assert universe
    for parked in fp.PARKED_PREDICTORS:
        assert parked not in universe[0]


def test_no_legacy_only_feature_name_appears_in_fresh_artifacts(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata)
    _run(localdata, tmp_path, write=True)
    out = tmp_path / "out"
    for name in (f"fresh_production_candidate_picks_{DAY}.md",
                 f"fresh_production_dispatchable_picks_{DAY}.md",
                 f"model_health_{DAY}.md"):
        text = (out / name).read_text()
        for legacy in ("goalsavg", "pred_total", "sa_ht_p", "fb_p"):
            assert legacy not in text, f"{legacy} leaked into {name}"


# ------------------------------------------------- 18. retention reasons


def test_retention_manifest_records_a_reason_for_every_decision(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    for day in ("2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"):
        (root / f"model_health_{day}.json").write_text("x" * 10)
    (root / "zulubet.csv.gz").write_text("raw")
    plan = cl.fresh_production_retention_plan(root, keep_days=30, keep_latest=3,
                                              today=date(2026, 9, 30))
    assert all(entry["reason"] for entry in plan["delete"] + plan["keep"])
    assert plan["unmatched_files_left_alone"] == 1
    cl.write_artifact_manifest(plan, root=root, dry_run=True)
    manifest = json.loads((root / "artifact_manifest_2026-09-30.json").read_text())
    assert manifest["why_each_deleted"] and manifest["why_each_kept"]
    assert manifest["raw_evidence_preserved"]
    assert manifest["largest_generated_prefixes"]


def test_retention_manifest_explains_a_zero_removal_run(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    (root / f"model_health_{DAY}.json").write_text("x")
    plan = cl.fresh_production_retention_plan(root, keep_days=30, keep_latest=3,
                                              today=date.fromisoformat(DAY))
    cl.write_artifact_manifest(plan, root=root, dry_run=False)
    manifest = json.loads((root / f"artifact_manifest_{DAY}.json").read_text())
    assert manifest["files_deleted"] == 0
    assert manifest["no_files_removed_explanation"]


def test_retention_prunes_stale_daily_reports(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    for day in ("2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"):
        for name in (f"clv_report_{day}.md", f"official_run_{day}.json",
                     f"supabase_sync_manifest_{day}.json", f"picks_{day}.txt"):
            (root / name).write_text("x")
    stale = [p.name for p in cl.fresh_production_files_to_prune(
        root, keep_days=30, keep_latest=3, today=date(2026, 9, 30))]
    assert "clv_report_2026-01-01.md" in stale
    assert "official_run_2026-01-01.json" in stale
    assert "picks_2026-01-01.txt" in stale


def test_retention_never_touches_durable_pick_archives_or_ticket_slips(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    for day in ("2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"):
        (root / f"picks_{day}.json").write_text("x")
        (root / f"picks_morning_{day}.json").write_text("x")
        (root / f"auto_tickets_{day}.txt").write_text("x")
    assert cl.fresh_production_files_to_prune(
        root, keep_days=30, keep_latest=3, today=date(2026, 9, 30)) == []


def test_short_window_prefixes_are_pruned_sooner(tmp_path):
    root = tmp_path / "localdata"
    root.mkdir()
    today = date(2026, 9, 30)
    for offset in range(1, 12):
        day = (today - timedelta(days=offset)).isoformat()
        (root / f"theoddsapi_attempts_{day}.json").write_text("x")
        (root / f"clv_report_{day}.md").write_text("x")
    stale = [p.name for p in cl.fresh_production_files_to_prune(
        root, keep_days=30, keep_latest=3, today=today)]
    assert any(n.startswith("theoddsapi_attempts") for n in stale)
    assert not any(n.startswith("clv_report") for n in stale)
