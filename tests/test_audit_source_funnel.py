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
