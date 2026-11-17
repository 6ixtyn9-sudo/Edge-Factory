"""Reuse only the current locked operation; never memoize evidence or results."""

import json
from copy import deepcopy
from datetime import timedelta

import pytest

import scripts.auto_tickets as at
import scripts.auto_tickets_grade as grade
from edgefactory import ml_paper as mp
from test_ml_paper import NOW
from test_ml_paper_rolling import run, slate
from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo


def counted_history(monkeypatch):
    calls = {"loads": 0, "records": []}
    read, validate = mp.receipts, mp.validate_record

    def loading(*args, **kwargs):
        calls["loads"] += 1
        return read(*args, **kwargs)

    def validating(row, *args, **kwargs):
        calls["records"].append(row["sha256"])
        return validate(row, *args, **kwargs)

    monkeypatch.setattr(mp, "receipts", loading)
    monkeypatch.setattr(mp, "validate_record", validating)
    return calls


def test_grade_display_and_new_results_share_one_validation_but_not_a_result_cache(tmp_path, monkeypatch):
    row = run(tmp_path)
    originals = {p: p.read_bytes() for p in mp.receipt_files(tmp_path)}
    calls = counted_history(monkeypatch)
    with mp.paper_run(tmp_path) as operation:
        pending = operation.publish(lambda _: None)
        assert pending["pending_accas"] > 0
        assert operation.latest_card() == row
        assert operation.render_latest_card(pending) == mp.render_daily_card([row], pending)
        settled = operation.publish(lambda _: (2, 0))
        assert settled["pending_accas"] == 0
        assert settled["paper_bank_units"] != pending["paper_bank_units"]
    assert calls == {"loads": 1, "records": [row["sha256"]]}
    assert all(p.read_bytes() == raw for p, raw in originals.items())
    with pytest.raises(RuntimeError, match="closed"):
        operation.publish(lambda _: None)


def test_capture_grade_and_display_validate_old_and_new_records_once_each(tmp_path, monkeypatch):
    first = run(tmp_path)
    calls = counted_history(monkeypatch)
    now = NOW + timedelta(minutes=1)
    with mp.paper_run(tmp_path) as operation:
        second = operation.capture_rolling(
            {"build_at": now.isoformat(), "slate": slate(now, ids=(4, 5))},
            score_lookup=lambda _: None, kickoff_fn=at.parse_kickoff_proven,
            source_guard=at.execution_source_rejection, now=now, index={})
        assert second and second["prior_receipt_sha256s"] == [first["sha256"]]
        report = operation.publish(lambda _: None)
        assert report["receipt_days"] == 1
        assert operation.latest_card() == second
        assert operation.render_latest_card(report) == mp.render_daily_card([first, second], report)
    assert calls == {"loads": 1, "records": [first["sha256"], second["sha256"]]}
    assert mp.receipts(tmp_path) == [first, second]


@pytest.mark.parametrize("damage", ["checksum", "fork", "block"])
def test_a_new_operation_always_sees_changed_evidence(tmp_path, damage):
    row = run(tmp_path)
    with mp.paper_run(tmp_path) as operation:
        operation.publish(lambda _: None)
    path = mp.rolling_receipt_path(tmp_path, row)
    if damage == "block":
        (tmp_path / f"{mp.PREFIX}_integrity_block.json").write_text("{}")
    else:
        changed = deepcopy(row)
        if damage == "fork":
            changed["prior_receipt_sha256s"] = ["a" * 64]
            changed["sha256"] = mp.digest({k: v for k, v in changed.items() if k != "sha256"})
        else:
            changed["sha256"] = "0" * 64
        path.write_text(json.dumps(changed))
    with pytest.raises(ValueError):
        with mp.paper_run(tmp_path) as operation:
            operation.publish(lambda _: None)


def test_public_performance_still_validates_mutable_caller_rows(tmp_path):
    row = run(tmp_path)
    row["accas"][0]["stake_units"] = -1
    with pytest.raises(ValueError, match="price or stake"):
        mp.performance([row], lambda _: None)


def test_adjacent_grader_reads_and_validates_history_once(tmp_path, monkeypatch):
    first = run(tmp_path)
    calls = counted_history(monkeypatch)
    monkeypatch.setattr(grade, "LOCALDATA", tmp_path)
    monkeypatch.setattr(grade.at, "load_settled_scores", dict)
    grade.publish_ml_paper()
    assert calls == {"loads": 1, "records": [first["sha256"]]}


def test_restore_checks_history_chain_without_a_second_full_validation(tmp_path, monkeypatch):
    _seed_repo(tmp_path)
    root = tmp_path / "localdata"
    first = run(root)
    _git(tmp_path, "add", "-f", "localdata")
    _git(tmp_path, "commit", "-qm", "frozen paper history")
    calls = counted_history(monkeypatch)
    _persistence_module().restore_committed_localdata(tmp_path)
    assert calls == {"loads": 0, "records": [first["sha256"]]}
    assert not (root / f"{mp.PREFIX}_integrity_block.json").exists()


def test_restore_blocks_missing_capital_history_even_with_valid_record_checksums(tmp_path):
    _seed_repo(tmp_path)
    root = tmp_path / "localdata"
    row = run(root)
    row["prior_receipt_sha256s"] = ["a" * 64]
    row["sha256"] = mp.digest({k: v for k, v in row.items() if k != "sha256"})
    path = mp.rolling_receipt_path(root, row)
    path.write_text(json.dumps(row))
    mp.validate_record(row, row["date"])  # individually valid, history is NOT
    _persistence_module().restore_committed_localdata(tmp_path)
    marker = root / f"{mp.PREFIX}_integrity_block.json"
    assert "history_integrity_error" in marker.read_text()
    assert path.read_text() == json.dumps(row)
    with pytest.raises(ValueError, match="blocked"):
        mp.receipts(root)


def test_restore_still_checks_filename_binding_without_a_second_history_scan(tmp_path):
    _seed_repo(tmp_path)
    root = tmp_path / 'localdata'
    row = run(root)
    path = mp.rolling_receipt_path(root, row)
    original = path.read_bytes()
    different_id = (NOW + timedelta(seconds=1)).strftime('%Y%m%dT%H%M%S%fZ')
    wrong = path.with_name(f'{mp.PREFIX}_{row["date"]}_{different_id}.json')
    path.rename(wrong)
    _persistence_module().restore_committed_localdata(tmp_path)
    assert wrong.read_bytes() == original
    assert (root / f'{mp.PREFIX}_integrity_block.json').exists()
