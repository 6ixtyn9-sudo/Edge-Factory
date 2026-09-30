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
    """Append a today-dated fixture (and optionally its price) to the fixture set."""
    for name, fields, row in (
        ("zulubet.csv.gz",
         ["date", "kickoff", "league", "home", "away", "p1", "px", "p2"],
         _pred_rows(DAY, "Home Team 00", "Away Team 00", 70.0, 18.0, 12.0)),
        ("statarea.csv.gz",
         ["date", "time", "league", "home", "away", "p1", "px", "p2"],
         {"date": DAY, "time": "18:00", "league": "Test League",
          "home": "Home Team 00", "away": "Away Team 00",
          "p1": 68.0, "px": 20.0, "p2": 12.0}),
    ):
        path = localdata / name
        existing = list(fp.iter_rows(path))
        _write_csv(path, fields, existing + [row])

    results_path = localdata / "betexplorer_results_2026-06.csv.gz"
    existing = list(fp.iter_rows(results_path))
    fields = list(existing[0]) if existing else []
    existing.append({**{k: "" for k in fields}, "date": DAY, "home": "Home Team 00",
                     "away": "Away Team 00", "event_id": "today-00",
                     "league": "Test League", "kickoff": "18:00"})
    _write_csv(results_path, fields, existing)

    if with_odds:
        _write_csv(localdata / "betexplorer_odds_2026-06.csv.gz",
                   ["date", "event_id", "match_url", "odd1", "oddx", "odd2"],
                   [{"date": DAY, "event_id": "today-00", "match_url": "",
                     "odd1": odds, "oddx": 3.4, "odd2": 4.2}])


def _run(localdata: Path, tmp_path: Path, **kwargs):
    return fp.run(localdata=localdata, day=DAY, output_dir=tmp_path / "out",
                  as_of=AS_OF, eval_days=90, train_days=30, **kwargs)


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
    assert all(ev.rule_id.startswith("fresh_") for ev in report["_evidence"].values())


def test_certification_registry_is_written_to_its_own_file(tmp_path):
    localdata = _history(tmp_path)
    _run(localdata, tmp_path, write=True)
    registry = json.loads((tmp_path / "out" / "fresh_production_certified_edges.json").read_text())
    assert registry["model_version"] == fp.MODEL_VERSION
    assert "legacy" not in json.dumps(registry["certified_rules"]).lower()


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
    assert pick["rule_id"].startswith("fresh_1x2_")
    assert pick["odds"] == 2.50
    assert pick["edge"] > 0
    assert pick["pricing_source"] == "betexplorer_odds"
    assert pick["stake_units"] == fp.FLAT_STAKE_UNITS
    assert pick["model_health_status"] == "scored"
    assert pick["feature_schema_version"] == fp.FEATURE_SCHEMA_VERSION
    assert pick["blockers"] == []


def test_a_candidate_without_a_price_is_not_dispatchable(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, with_odds=False)
    report = _run(localdata, tmp_path, write=False)
    assert report["dispatchable_count"] == 0
    blockers = [b for c in report["candidates"] for b in c["blockers"]]
    assert "missing_odds" in blockers


def test_a_short_price_blocks_dispatch_on_insufficient_edge(tmp_path):
    localdata = _history(tmp_path)
    _add_today(localdata, odds=1.05)
    report = _run(localdata, tmp_path, write=False)
    assert report["dispatchable_count"] == 0
    assert any(b.startswith("insufficient_edge_versus_price")
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
    assert any(b.startswith("blocked_missing_required_feature") for b in lonely[0]["blockers"])
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
        groups={}, day=DAY, candidates=[], evidence={}, odds_index={},
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
    assert "NOT legacy_baseline" in text


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
    assert manifest["files_removed"] == 1 and manifest["bytes_removed"] == 100
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
