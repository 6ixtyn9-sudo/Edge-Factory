"""Tests for the same-day source funnel audit.

The audit reuses the live gates from scripts/picks_today.py, so these tests
assert the funnel semantics (identity overlap, kickoff trust, voter quorum,
odds overlap, backfill depth) rather than re-testing the engine internals.
"""
from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit_source_funnel.py"
SPEC = importlib.util.spec_from_file_location("audit_source_funnel", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
funnel = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = funnel
SPEC.loader.exec_module(funnel)

SAST = timezone(timedelta(hours=2))
DAY = "2026-09-30"
AS_OF = datetime(2026, 9, 30, 8, 0, tzinfo=SAST)

FIELDS = ["date", "kickoff", "home", "away", "p1", "px", "p2", "hs", "gs", "p_o25", "p_gg"]


def _write(localdata: Path, source: str, rows: list[dict]) -> None:
    localdata.mkdir(parents=True, exist_ok=True)
    path = localdata / f"{source}_2026-09.csv.gz"
    with gzip.open(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def _row(home, away, *, kickoff="19:30", p1="60", px="25", p2="15", **kw) -> dict:
    return {"date": DAY, "kickoff": kickoff, "home": home, "away": away,
            "p1": p1, "px": px, "p2": p2, **kw}


def _audit(localdata: Path, **kw):
    return funnel.run_audit(localdata=localdata, day=DAY, as_of=AS_OF, examples=5, **kw)


def test_source_with_rows_but_no_kickoff(tmp_path):
    _write(tmp_path, "betclan", [_row("Alpha United", "Beta Rovers", kickoff="")])
    report = _audit(tmp_path)
    row = report["per_source"]["betclan"]
    assert row["raw_rows"] == 1
    assert row["unique_fixtures"] == 1
    assert row["has_kickoff"] == 0
    assert row["trusted_kickoff"] == 0
    assert row["pre_match_eligible"] == 0
    assert "no trusted kickoff" in row["notes"]


def test_source_with_kickoff_is_pre_match_eligible(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", kickoff="19:30")])
    row = _audit(tmp_path)["per_source"]["zulubet"]
    assert row["has_kickoff"] == 1
    assert row["trusted_kickoff"] == 1
    assert row["pre_match_eligible"] == 1


def test_kickoff_already_started_is_not_pre_match_eligible(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", kickoff="07:00")])
    row = _audit(tmp_path)["per_source"]["zulubet"]
    assert row["trusted_kickoff"] == 1
    assert row["pre_match_eligible"] == 0


def test_two_sources_exact_match_one_fixture(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers")])
    report = _audit(tmp_path)
    overlap = report["identity_overlap"]
    assert overlap["fixture_groups"] == 1
    assert overlap["two_source_groups"] == 1
    assert overlap["single_source_groups"] == 0
    assert report["consensus_funnel"]["fixtures_with_2plus_voters"] == 1


def test_two_sources_alias_match_same_fixture(tmp_path):
    # "FC Alpha United" vs "Alpha United" fold to one identity key.
    _write(tmp_path, "zulubet", [_row("FC Alpha United", "Beta Rovers")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers")])
    report = _audit(tmp_path)
    assert report["identity_overlap"]["fixture_groups"] == 1
    assert report["identity_overlap"]["two_source_groups"] == 1


def test_singleton_fixture_drops_for_lack_of_quorum(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    report = _audit(tmp_path)
    cf = report["consensus_funnel"]
    assert report["identity_overlap"]["single_source_groups"] == 1
    assert cf["match_surface"] == 1
    assert cf["fixtures_with_2plus_voters"] == 0
    assert cf["drops"]["fewer_than_2_voters_with_1x2"] == 1
    assert cf["drop_examples"]["fewer_than_2_voters_with_1x2"]


def test_reversed_home_away_group_is_flagged(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "statarea", [_row("Beta Rovers", "Alpha United")])
    overlap = _audit(tmp_path)["identity_overlap"]
    assert overlap["reversed_risk_groups"] == 1
    assert overlap["examples"]["reversed_risk"]


def test_source_without_prediction_signal(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", p1="", px="", p2="")])
    row = _audit(tmp_path)["per_source"]["zulubet"]
    assert row["unique_fixtures"] == 1
    assert row["has_1x2_signal"] == 0
    assert "no 1X2 probability signal" in row["notes"]


def test_settled_rows_are_not_a_same_day_surface(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", hs="1", gs="0")])
    row = _audit(tmp_path)["per_source"]["zulubet"]
    assert row["already_settled"] == 1
    assert row["unique_fixtures"] == 0


def test_ml_anchor_requirement_drops_non_anchored_fixtures(tmp_path):
    # vitibet + betclan agree, but neither is a forebet/zulubet/statarea anchor.
    _write(tmp_path, "vitibet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "betclan", [_row("Alpha United", "Beta Rovers")])
    cf = _audit(tmp_path)["consensus_funnel"]
    assert cf["fixtures_with_2plus_voters"] == 1
    assert cf["fixtures_ml_scoreable"] == 0
    assert cf["drops"]["no_ml_anchor_source_present"] == 1


def test_candidate_dropped_by_missing_kickoff_on_scoreable_surface(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", kickoff="")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers", kickoff="")])
    cf = _audit(tmp_path)["consensus_funnel"]
    assert cf["fixtures_ml_scoreable"] == 1
    assert cf["fixtures_ml_scoreable_pre_match_eligible"] == 0
    assert cf["kickoff_drops"]["missing_kickoff_same_day"] == 1
    assert cf["kickoff_drop_examples"]["missing_kickoff_same_day"][0]["kickoff_raw"] == "(none)"


def test_odds_exact_match_and_missing_odds(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers"),
                                 _row("Gamma City", "Delta Town")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers"),
                                  _row("Gamma City", "Delta Town")])
    _write(tmp_path, "bzzoiro_odds", [_row("Alpha United", "Beta Rovers")])
    odds = _audit(tmp_path)["odds_funnel"]
    assert odds["sources"]["bzzoiro_odds"]["unique_fixtures"] == 1
    assert odds["sources"]["bzzoiro_odds"]["overlap_with_consensus_surface"] == 1
    assert odds["sources"]["bzzoiro_odds"]["coverage_pct_of_consensus"] == 50.0
    assert odds["examples"]["bzzoiro_odds"]  # the unpriced fixture is listed
    assert odds["sources"]["theoddsapi_odds"]["cached_rows"] == 0


def test_captured_but_unused_source_is_reported_not_silently_ignored(tmp_path):
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers")])
    row = _audit(tmp_path)["per_source"]["predictz"]
    assert row["unique_fixtures"] == 1
    assert row["consumed_by_picks_engine"] is False
    assert "NOT consumed by picks engine" in row["notes"]


def test_shadow_expansion_is_diagnostic_and_never_dispatchable(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers")])
    report = _audit(tmp_path)
    sh = report["shadow_expansion"]
    assert sh["fixtures_with_2plus_certified_voters"] == 0
    assert sh["fixtures_with_2plus_voters_if_shadow_admitted"] == 1
    assert sh["fixtures_gained_if_shadow_admitted"] == 1
    assert sh["dispatchable"] is False
    # the real funnel is unchanged: nothing was promoted
    assert report["consensus_funnel"]["fixtures_with_2plus_voters"] == 0


def test_backfill_depth_reports_gaps_and_forward_only(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    depth = _audit(tmp_path)["backfill_depth"]["zulubet"]
    assert depth["first_local_date"] == DAY
    assert depth["latest_local_date"] == DAY
    assert depth["missing_dates_in_d30_count"] == 30
    assert depth["retryable_failure_dates"] == []


def test_backfill_depth_surfaces_retryable_failures(tmp_path):
    _write(tmp_path, "soccervista", [])
    (tmp_path / "state_soccervista.json").write_text(json.dumps({
        "done": [], "failures": {DAY: "rc=1", "2025-01-01": "old"},
    }))
    depth = _audit(tmp_path)["backfill_depth"]["soccervista"]
    assert depth["retryable_failure_dates"] == [DAY]
    assert depth["first_local_date"] is None


def test_cli_writes_artifacts(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers")])
    out_json = tmp_path / "out" / "funnel.json"
    out_md = tmp_path / "out" / "funnel.md"
    rc = funnel.main([
        "--date", DAY, "--as-of", AS_OF.isoformat(), "--localdata", str(tmp_path),
        "--output-json", str(out_json), "--output-md", str(out_md),
    ])
    assert rc == 0
    payload = json.loads(out_json.read_text())
    assert payload["consensus_funnel"]["match_surface"] == 1
    text = out_md.read_text()
    assert "Same-day source funnel" in text
    assert "Consensus funnel" in text
    assert "NON-DISPATCH" in text


def test_audit_is_read_only(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    before = {p.name: p.stat().st_mtime_ns for p in tmp_path.iterdir()}
    _audit(tmp_path)
    after = {p.name: p.stat().st_mtime_ns for p in tmp_path.iterdir()}
    assert before == after, "the funnel audit must never mutate localdata"


# --------------------------------------------------------------------------
# Fixture-group kickoff aggregation, shadow slate, odds diagnosis
# --------------------------------------------------------------------------


def test_statarea_time_column_is_classified_as_trusted_kickoff(tmp_path):
    rows = [{"date": DAY, "time": "19:30", "home": "Alpha United", "away": "Beta Rovers",
             "p1": "60", "px": "25", "p2": "15"}]
    localdata = tmp_path
    localdata.mkdir(parents=True, exist_ok=True)
    with gzip.open(localdata / "statarea_2026-09.csv.gz", "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "time", "home", "away", "p1", "px", "p2"])
        writer.writeheader()
        writer.writerows(rows)
    row = _audit(localdata)["per_source"]["statarea"]
    assert row["has_kickoff"] == 1
    assert row["trusted_kickoff"] == 1
    assert row["pre_match_eligible"] == 1


def test_kickoffless_voter_joins_fixture_with_trusted_kickoff_from_another_source(tmp_path):
    # betclan has no kickoff; zulubet (a timing-capable source) supplies it.
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", kickoff="19:30")])
    _write(tmp_path, "betclan", [_row("Alpha United", "Beta Rovers", kickoff="")])
    cf = _audit(tmp_path)["consensus_funnel"]
    assert cf["fixtures_with_2plus_voters"] == 1
    assert cf["fixtures_ml_scoreable"] == 1
    # the kickoff-less voter no longer poisons the group
    assert cf["fixtures_ml_scoreable_pre_match_eligible"] == 1
    assert cf["kickoff_drops"] == {}


def test_kickoffless_sources_alone_cannot_make_a_fixture_dispatchable(tmp_path):
    _write(tmp_path, "betclan", [_row("Alpha United", "Beta Rovers", kickoff="")])
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers", kickoff="")])
    report = _audit(tmp_path)
    cf = report["consensus_funnel"]
    # betclan alone is one live voter -> no live quorum at all
    assert cf["fixtures_ml_scoreable_pre_match_eligible"] == 0
    shadow = report["shadow_candidates"]
    assert shadow["candidate_count"] == 1
    row = shadow["candidates"][0]
    assert row["dispatchable"] is False
    assert "no_trusted_kickoff_from_a_timing_capable_source" in row["blockers"]


def test_kickoff_donor_must_be_a_timing_capable_source(tmp_path):
    # predictz carries a clock but the registry says it cannot supply timing.
    _write(tmp_path, "betclan", [_row("Alpha United", "Beta Rovers", kickoff="")])
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers", kickoff="19:30")])
    agg = funnel.aggregate_fixture_kickoff(
        ("alphaunited", "betarovers"),
        {
            "betclan": {("alphaunited", "betarovers"): {"kickoff": ""}},
            "predictz": {("alphaunited", "betarovers"): {"kickoff": "19:30"}},
        },
        engine=funnel.load_picks_engine(),
    )
    assert agg["trusted"] is False
    assert agg["kickoff_donors"] == []


def test_unparseable_kickoff_fails_closed(tmp_path):
    engine = funnel.load_picks_engine()
    assert funnel.classify_kickoff({"kickoff": ""}, engine=engine)[0] == "absent"
    assert funnel.classify_kickoff({"kickoff": "19:30"}, engine=engine)[0] == "trusted"
    assert funnel.classify_kickoff({"kickoff": "tbd"}, engine=engine)[0] in {
        "clock_only", "date_only"}


def test_shadow_quorum_is_reported_but_never_dispatchable(tmp_path):
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers", kickoff="")])
    _write(tmp_path, "windrawwin", [_row("Alpha United", "Beta Rovers", kickoff="")])
    report = _audit(tmp_path)
    shadow = report["shadow_candidates"]
    assert shadow["dispatchable"] is False
    assert shadow["candidate_count"] == 1
    row = shadow["candidates"][0]
    assert row["live_voters"] == []
    assert sorted(row["shadow_voters"]) == ["predictz", "windrawwin"]
    assert "fewer_than_2_live_voters" in row["blockers"]
    assert "no_ml_feature_provider_on_fixture" in row["blockers"]
    assert any(b.startswith("shadow_sources_not_settlement_validated") for b in row["blockers"])
    # the live funnel is untouched by the shadow evaluation
    assert report["consensus_funnel"]["fixtures_with_2plus_voters"] == 0


def test_shadow_candidate_with_live_partner_still_blocked_on_validation(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", kickoff="19:30")])
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers", kickoff="")])
    row = _audit(tmp_path)["shadow_candidates"]["candidates"][0]
    assert row["live_voters"] == ["zulubet"]
    assert row["kickoff_donors"] == ["zulubet"]
    assert "fewer_than_2_live_voters" in row["blockers"]
    assert row["dispatchable"] is False


def test_voter_classification_covers_every_role(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "bettingclosed", [_row("Alpha United", "Beta Rovers")])
    voters = _audit(tmp_path)["voter_classification"]
    assert voters["zulubet"]["role"] == "live_voter"
    assert voters["predictz"]["role"] == "shadow_voter"
    assert "not settlement-validated" in voters["predictz"]["blocker"]
    assert voters["bettingclosed"]["role"] == "not_a_voter"
    assert voters["soccervista"]["role"] == "blocked"
    assert voters["soccervista"]["blocker"] == "no same-day rows captured"


def test_odds_diagnosis_no_candidates_to_price(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers", kickoff="")])
    report = _audit(tmp_path)
    assert report["consensus_funnel"]["fixtures_ml_scoreable_pre_match_eligible"] == 0
    assert report["odds_funnel"]["diagnosis"].startswith("no_candidates_to_price")


def test_odds_diagnosis_price_identity_broken(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "bzzoiro_odds", [_row("Totally Other", "Different Club")])
    odds = _audit(tmp_path)["odds_funnel"]
    assert odds["candidates_before_odds"] == 1
    assert odds["diagnosis"].startswith("price_identity_broken")
    assert odds["sources"]["bzzoiro_odds"]["status"] == (
        "rows_present_but_zero_overlap_with_consensus_surface")


def test_bzzoiro_zero_live_rows_is_not_reported_as_clean_success(tmp_path):
    _write(tmp_path, "zulubet", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers")])
    odds = _audit(tmp_path)["odds_funnel"]
    assert odds["sources"]["bzzoiro_odds"]["cached_rows"] == 0
    assert odds["sources"]["bzzoiro_odds"]["status"] == "empty_no_rows_today"
    assert odds["diagnosis"] != "price_fixtures_overlap_the_surface"


def test_backfill_gap_expectation_distinguishes_expected_from_bug(tmp_path):
    _write(tmp_path, "windrawwin", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "statarea", [_row("Alpha United", "Beta Rovers")])
    depth = _audit(tmp_path)["backfill_depth"]
    assert depth["windrawwin"]["declared_backfill_mode"] == "capture_forward_only"
    assert "EXPECTED" in depth["windrawwin"]["gap_expectation"]
    assert depth["statarea"]["declared_backfill_mode"] == "d30"
    assert "GAP WITHOUT RECORDED FAILURE" in depth["statarea"]["gap_expectation"]


def test_source_health_warnings_are_surfaced_in_the_report(tmp_path):
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "windrawwin", [_row("Alpha United", "Beta Rovers")])
    report = _audit(tmp_path)
    assert any("0 live candidates" in w for w in report["warnings"])
    assert "Source health warnings" in funnel.render_markdown(report)


def test_source_registry_is_embedded_in_the_artifact(tmp_path):
    report = _audit(tmp_path)
    rows = {r["source"]: r for r in report["source_registry"]}
    assert rows["predictz"]["dispatchable"] is False
    assert rows["zulubet"]["dispatchable"] is True


def test_shadow_markdown_is_marked_non_dispatch(tmp_path):
    _write(tmp_path, "predictz", [_row("Alpha United", "Beta Rovers")])
    _write(tmp_path, "windrawwin", [_row("Alpha United", "Beta Rovers")])
    text = funnel.render_shadow_markdown(_audit(tmp_path))
    assert "NON-DISPATCH" in text
    assert "dispatchable: **False**" in text
    assert "never dispatched" in text
