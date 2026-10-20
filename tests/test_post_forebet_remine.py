"""Post-Forebet default miner: hermetic, exact identity, no live activation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import duckdb
import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts" / "mine_consensus.py"
SPEC = importlib.util.spec_from_file_location("post_forebet_miner_test", PATH)
miner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(miner)
START, SPLIT, END = "2026-06-13", "2026-09-21", "2026-10-19"


@pytest.fixture
def con():
    db = duckdb.connect(":memory:")
    yield db
    db.close()


def table(con, name, rows):
    import pandas as pd
    con.register("fixture_frame", pd.DataFrame(rows))
    con.execute(f"CREATE TABLE {name} AS SELECT * FROM fixture_frame")
    con.unregister("fixture_frame")


def row(day="2026-09-01", **extra):
    return {"date": day, "home": "Alpha Town", "away": "Bravo United", "league": "Test League",
            "p1": .7, "px": .2, "p2": .1, "hs": 2, "gs": 1,
            "odd1": 1.7, "oddx": 3.5, "odd2": 4.5, **extra}


def mine(con):
    return miner.remine_current_sources(con, start=START, split=SPLIT, as_of=END)


def edges(report, strategy, sources, threshold=0, market="1x2", follow=None):
    return [e for e in report["edges"] if e["strategy"] == strategy and e["sources"] == sorted(sources)
            and e["threshold"] == threshold and e["market"] == market
            and e["follow_source"] == follow]


def test_singles_pairs_majority_and_each_dissent_side_are_tested(con):
    for source, probs in [("zulubet", (.7, .2, .1)), ("statarea", (.7, .2, .1)),
                          ("vitibet", (.1, .2, .7))]:
        table(con, source + "_settled", [row(day, p1=probs[0], px=probs[1], p2=probs[2])
                                         for day in ("2026-09-01", "2026-10-01")])
    report = mine(con)
    assert edges(report, "single", ["zulubet"])[0]["valid"]["n"] == 1
    assert edges(report, "unanimous", ["statarea", "zulubet"])
    assert edges(report, "majority", ["statarea", "vitibet", "zulubet"])
    assert edges(report, "disagree_follow", ["vitibet", "zulubet"], follow="vitibet")[0]["valid"]["wins"] == 0
    assert edges(report, "disagree_follow", ["vitibet", "zulubet"], follow="zulubet")[0]["valid"]["wins"] == 1
    assert not edges(report, "majority", ["vitibet", "zulubet"])
    assert not any("forebet" in e["sources"] for e in report["edges"])
    assert all(e["status"] == "candidate" and e["view"] is None for e in report["edges"])


def test_forebet_is_neither_voter_nor_result_donor(con):
    table(con, "forebet_settled", [row()])
    table(con, "betclan", [row(hs=None, gs=None)])
    table(con, "results_donor", [row(result_source="forebet")])
    report = mine(con)
    assert report["sources"]["betclan"]["market_votes"]["1x2"] == 1
    assert report["settled_fixture_markets"] == 0
    assert report["edges"] == []
    assert "forebet" not in report["sources"]


def test_independent_results_settle_capture_forward_sources(con):
    table(con, "betclan", [row(hs=None, gs=None)])
    table(con, "betexplorer_settled", [row()])
    result = edges(mine(con), "single", ["betclan"])[0]
    assert result["train"]["wins"] == 1


def test_dates_are_exclusive_and_old_history_does_not_train_new_era(con):
    table(con, "zulubet_settled", [row(d) for d in
          ("2026-06-12", START, "2026-09-20", SPLIT, "2026-10-18", END, "2026-10-20")])
    result = edges(mine(con), "single", ["zulubet"])[0]
    assert result["train"]["n"] == 2
    assert result["valid"]["n"] == 2


def test_conflicting_scores_and_prediction_duplicates_are_quarantined(con):
    table(con, "zulubet_settled", [row()])
    table(con, "statarea_settled", [row(hs=0, gs=1)])
    assert mine(con)["conflicting_result_periods"] == 1
    assert mine(con)["edges"] == []
    con.execute("DROP TABLE statarea_settled")
    table(con, "betclan", [row(), row(p1=.1, p2=.7)])
    report = mine(con)
    assert report["ambiguous_source_market_observations"] == 1
    assert not any("betclan" in e["sources"] for e in report["edges"])


def test_exact_duplicates_do_not_multiply_samples(con):
    table(con, "zulubet_settled", [row(), row()])
    assert edges(mine(con), "single", ["zulubet"])[0]["train"]["n"] == 1


def test_new_identity_key_avoids_legacy_prefix_collision(con):
    table(con, "betclan", [row(home="Atletico Madrid", hs=None, gs=None)])
    table(con, "betexplorer_settled", [row(home="Real Madrid")])
    assert mine(con)["edges"] == []


def test_all_supported_markets_and_enhancement_totals_are_reported(con):
    r = row(p_o15=.8, p_o25=.7, p_o35=.2, p_o45=.1, p_gg=.7,
            p1_ht=.1, px_ht=.7, p2_ht=.2, p_o15_ht=.7, p_o25_ht=.1, ht_hs=1, ht_gs=1)
    table(con, "scoutingstats_settled", [r])
    report = mine(con)
    assert set(report["markets"]) == set(miner.REMINE_MARKETS)
    assert all(cell["tested_rules"] > 0 for cell in report["markets"].values())
    assert edges(report, "single", ["scoutingstats"], market="ou_3.5")[0]["train"]["wins"] == 1
    assert edges(report, "single", ["scoutingstats"], market="ht_1x2")[0]["train"]["wins"] == 1


def test_missing_half_time_scores_are_not_inferred_from_full_time(con):
    table(con, "statarea_settled", [row(p1_ht=.7, px_ht=.2, p2_ht=.1)])
    report = mine(con)
    assert report["markets"]["ht_1x2"]["usable_votes"] == 1
    assert report["markets"]["ht_1x2"]["tested_rules"] == 0


def test_binary_under_and_no_use_their_own_prices(con):
    table(con, "scoutingstats_settled", [row(p_o25=.2, p_gg=.1, odd_o25=1.2,
                                           odd_u25=3., odd_gg=1.1, odd_ng=4.)])
    report = mine(con)
    under = edges(report, "single", ["scoutingstats"], market="ou_2.5")[0]
    no = edges(report, "single", ["scoutingstats"], market="btts")[0]
    assert under["train"]["avg_odds"] == 3.
    assert no["train"]["avg_odds"] == 4.


def test_no_price_is_not_a_profitability_pass_even_with_large_hit_rate(con, monkeypatch):
    monkeypatch.setattr(miner, "GATES", SimpleNamespace(
        min_n_train=1, min_n_valid=1, min_roi_train=-.1, min_roi_valid=0.))
    table(con, "zulubet_settled", [row(day, odd1=None, oddx=None, odd2=None)
                                  for day in ("2026-09-01", "2026-10-01")])
    result = edges(mine(con), "single", ["zulubet"])[0]
    assert not result["statistical_gates_passed"]
    assert "valid_roi_unavailable" in result["holds"]
    assert result["valid"]["roi"] is None


def test_passing_small_test_gates_is_not_automatic_serving_authorization(con, monkeypatch):
    monkeypatch.setattr(miner, "GATES", SimpleNamespace(
        min_n_train=1, min_n_valid=1, min_roi_train=-.1, min_roi_valid=0.))
    table(con, "zulubet_settled", [row(day, home=f"Alpha Town {i}")
                                  for day in ("2026-09-01", "2026-10-01") for i in range(8)])
    result = edges(mine(con), "single", ["zulubet"])[0]
    assert result["statistical_gates_passed"]
    assert result["status"] == "candidate"
    assert result["holds"] == ["new_predicate_requires_serving_validation"]


def test_categorical_tips_are_not_fake_probabilities(con):
    table(con, "windrawwin", [row(p1=None, px=None, p2=None, pick="home", confidence=99)])
    table(con, "betexplorer_settled", [row()])
    report = mine(con)
    assert edges(report, "single", ["windrawwin"])[0]["train"]["n"] == 1
    assert edges(report, "single", ["windrawwin"], threshold=35)[0]["train"]["n"] == 0
    assert "ht_ou_2.5" in report["markets"]


@pytest.mark.parametrize("row_,market", [
    (row(p1=float("nan")), "1x2"),
    (row(p1=.9, px=.8, p2=.7), "1x2"),
    (row(p1=.4, px=.4, p2=.2), "1x2"),
    (row(p_o25=float("inf")), "ou_2.5"),
    (row(p_o25=1.1), "ou_2.5"),
])
def test_invalid_probabilities_are_not_usable(row_, market):
    assert miner._remine_signal(row_, market) is None


def test_probability_units_have_same_signal():
    normalized = row(p_o25=.8)
    percent = row(p1=70, px=20, p2=10, p_o25=80)
    for market in ("1x2", "ou_2.5"):
        assert miner._remine_signal(normalized, market) == miner._remine_signal(percent, market)


def test_empty_data_is_visible_not_fabricated_success(con):
    report = mine(con)
    assert report["edges"] == []
    assert all(c["status"] == "missing_table" for c in report["sources"].values())
    assert all(c["tested_rules"] == 0 for c in report["markets"].values())
    json.dumps(report, allow_nan=False)


def test_rejects_forebet_era_or_inverted_windows(con):
    with pytest.raises(ValueError):
        miner.remine_current_sources(con, start="2025-01-01", split=SPLIT, as_of=END)
    with pytest.raises(ValueError):
        miner.remine_current_sources(con, start=START, split=END, as_of=SPLIT)


def test_main_writes_existing_research_report_not_live_registry(con, tmp_path, monkeypatch, capsys):
    table(con, "zulubet_settled", [row()])
    db = tmp_path / "warehouse.duckdb"
    con.execute(f"ATTACH '{db}' AS persisted")
    con.execute("CREATE TABLE persisted.zulubet_settled AS SELECT * FROM zulubet_settled")
    con.execute("DETACH persisted")
    live = tmp_path / "edges_consensus.json"
    live.write_text('{"ml_model":{"frozen":true},"edges":[]}')
    before = live.read_bytes()
    research = tmp_path / "edges_consensus_research.json"
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    monkeypatch.setattr(miner, "DB", db)
    monkeypatch.setattr(miner, "OUT", live)
    monkeypatch.setattr(miner, "_print_k_coverage_diagnostic", lambda: None)
    monkeypatch.setattr(miner.sys, "argv", ["mine_consensus.py", "--as-of", END, "--output", str(research)])
    miner.main()
    payload = json.loads(research.read_text())
    assert payload["mining_era"] == "post_forebet"
    assert payload["edges"]
    assert live.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))
    assert "Post-Forebet re-mine" in summary.read_text()
    receipt, = notices(capsys.readouterr().out)
    assert receipt["tested_rules"] == len(payload["edges"])
    assert receipt["statistical_gates_passed"] == 0


def test_live_registry_cannot_be_selected_as_report_destination(tmp_path, monkeypatch):
    live = tmp_path / "edges_consensus.json"
    live.write_text("unchanged")
    monkeypatch.setattr(miner, "OUT", live)
    monkeypatch.setattr(miner.sys, "argv", ["mine_consensus.py", "--as-of", END, "--output", str(live)])
    with pytest.raises(SystemExit):
        miner.main()
    assert live.read_text() == "unchanged"


def test_cache_only_manual_execution_is_not_a_second_workflow():
    import yaml
    path = PATH.parent.parent / ".github/workflows/daily.yml"
    workflow = yaml.safe_load(path.read_text())
    steps = workflow["jobs"]["run-autonomous-agent"]["steps"]
    execution = next(step for step in steps if step["name"] == "Execute Autonomous Smart Schedule")["run"]
    branch = execution.split('elif [ "${{ inputs.mode }}" = "remine_only" ]; then')[1].split("\n  fi", 1)[0]
    assert "scripts/mine_consensus.py" in branch
    assert "scripts/daily.py" not in branch
    assert "capture_daily.py" not in branch
    for name in ("Enhancement tickets (generate/freeze)", "Enhancement performance report",
                 "Persist localdata State (Cache)", "Persist pipeline state to git (single source of truth)"):
        assert "inputs.mode != 'remine_only'" in next(s for s in steps if s["name"] == name)["if"]


def test_raw_predictions_precede_settled_subset_and_use_independent_results(con):
    # Both views exist in the production warehouse; prefer all captures, not
    # only the subset the legacy results-donor join happened to settle.
    table(con, "predictz_raw", [row(p1=None, px=None, p2=None, pick="home", hs=None, gs=None),
                               row(home="Gamma Town", p1=None, px=None, p2=None,
                                   pick="away", hs=None, gs=None)])
    table(con, "predictz_settled", [row(p1=None, px=None, p2=None, pick="home", result_source="forebet")])
    table(con, "betexplorer_settled", [row(), row(home="Gamma Town", hs=0, gs=2)])
    report = mine(con)
    assert report["sources"]["predictz"]["table"] == "predictz_raw"
    assert report["sources"]["predictz"]["rows"] == 2
    result = edges(report, "single", ["predictz"])[0]
    assert result["train"]["n"] == result["train"]["wins"] == 2


@pytest.fixture
def publication_report(con, monkeypatch):
    monkeypatch.setattr(miner, "GATES", SimpleNamespace(
        min_n_train=1, min_n_valid=1, min_roi_train=-.1, min_roi_valid=0.))
    table(con, "zulubet_settled", [
        row(day, home=f"Alpha Town {i}", p_o25=.8, p_gg=.8, odd_o25=1.7, odd_gg=1.7)
        for day in ("2026-09-01", "2026-10-01") for i in range(8)])
    return mine(con)


def notices(output):
    import zlib
    groups = {}
    for line in output.splitlines():
        if not line.startswith("::notice "):
            continue
        _, title, data = line.split("::", 2)
        group = title.rsplit(" fragment ", 1)[0]
        packet = json.loads(data)
        assert packet["encoding"] == "zlib-base16-ap"
        groups.setdefault(group, []).append(packet)
    decoded = []
    for packets in groups.values():
        packets.sort(key=lambda p: p["chunk"])
        assert [p["chunk"] for p in packets] == list(range(1, packets[0]["chunks"] + 1))
        assert all(p["chunks"] == len(packets) for p in packets)
        text = "".join(p["data"] for p in packets)
        assert set(text) <= set("ABCDEFGHIJKLMNOP")
        compressed = bytes.fromhex(text.translate(str.maketrans("ABCDEFGHIJKLMNOP", "0123456789abcdef")))
        decoded.append(json.loads(zlib.decompress(compressed)))
    return decoded


def test_passing_rules_are_readable_without_artifacts(publication_report, tmp_path, monkeypatch, capsys):
    import copy
    report = publication_report
    expected = [e for e in report["edges"] if e["statistical_gates_passed"]]
    assert {e["market"] for e in expected} == {"1x2", "ou_2.5", "btts"}
    # Force multiple annotation batches, not only the easy one-passing-rule case.
    report["edges"] = copy.deepcopy(report["edges"] * 8)
    expected = [e for e in report["edges"] if e["statistical_gates_passed"]]
    before = copy.deepcopy(report)
    summary = tmp_path / "summary.md"
    summary.write_text("Earlier step output\n")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    miner._publish_remine_results(report)
    output = capsys.readouterr().out
    receipt, *batches = notices(output)
    assert receipt["tested_rules"] == len(report["edges"])
    assert receipt["statistical_gates_passed"] == len(expected)
    assert receipt["split"] == SPLIT
    assert receipt["as_of_exclusive"] == END
    assert receipt["gates"] == report["gates"]
    assert receipt["markets"] == report["markets"]
    assert receipt["sources"] == report["sources"]
    assert receipt["excluded_voters"] == receipt["excluded_result_donors"] == ["forebet"]
    assert len(batches) > 1
    assert [b["part"] for b in batches] == list(range(1, len(batches) + 1))
    assert all(b["parts"] == len(batches) and b["research_only"] for b in batches)
    assert [e for b in batches for e in b["passing_candidates"]] == expected
    assert all(len(line.encode("utf-8")) < 3500 for line in output.splitlines())
    assert notices("\n".join(line[:4096] for line in output.replace("45", "***").replace("2.5", "***").splitlines())) == [receipt, *batches]
    text = summary.read_text()
    assert text.startswith("Earlier step output\n")
    assert "not approved live rules" in text
    assert "donor-price ROI is retrospective" in text
    for edge in expected:
        assert edge["rule"] in text
        assert all(hold in text for hold in edge["holds"])
    assert report == before  # Publication must not certify, clear holds or alter metrics.


def test_empty_passes_still_publish_coverage(con, tmp_path, monkeypatch, capsys):
    report = mine(con)
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    miner._publish_remine_results(report)
    receipt, = notices(capsys.readouterr().out)
    assert receipt["statistical_gates_passed"] == receipt["tested_rules"] == 0
    assert receipt["markets"] == report["markets"]
    assert "No candidates passed" in summary.read_text()


def test_notice_data_cannot_inject_workflow_commands(publication_report, tmp_path, monkeypatch, capsys):
    report = publication_report
    edge = next(e for e in report["edges"] if e["statistical_gates_passed"])
    edge["rule"] = "literal %0A %0D %25 | rule\n::error::not a command"
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    miner._publish_remine_results(report)
    output = capsys.readouterr().out
    assert "\n::error::" not in output
    recovered = [e for b in notices(output)[1:] for e in b["passing_candidates"]]
    assert edge in recovered
    assert "&#124;" in summary.read_text()


def test_missing_summary_destination_does_not_lose_api_receipt(publication_report, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "missing" / "summary.md"))
    miner._publish_remine_results(publication_report)
    output = capsys.readouterr().out
    assert "Could not write GitHub step summary" in output
    assert notices(output)[1]["passing_candidates"]


def test_local_execution_prints_passes_without_workflow_commands(publication_report, monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    miner._publish_remine_results(publication_report)
    output = capsys.readouterr().out
    assert "Passing research candidate:" in output
    assert "new_predicate_requires_serving_validation" in output
    assert "::notice" not in output


def test_incomplete_or_corrupted_notice_transport_is_rejected(publication_report, monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    miner._publish_remine_results(publication_report)
    lines = capsys.readouterr().out.splitlines()
    with pytest.raises((ValueError, AssertionError)):
        notices(lines[0][:-20])
    packet = json.loads(lines[0].split("::", 2)[2])
    packet["chunks"] += 1
    with pytest.raises(AssertionError):
        notices(lines[0].split("::", 2)[0] + "::" + lines[0].split("::", 2)[1] + "::" + json.dumps(packet))
