from __future__ import annotations

import ast
import builtins
import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from edgefactory.phase5_certifier import (
    ERA_EVALUATION_BLOCKERS,
    OFFICIAL_CONTEXT,
    Phase5CertifierIsolationError,
    build_daily_status,
    run_status,
    update_status,
)

ROOT = Path(__file__).resolve().parent.parent


def _load_script():
    script = ROOT / "scripts" / "phase5_certify.py"
    spec = importlib.util.spec_from_file_location("phase5_certifier_cli_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _attempt(source: str, day: date, *, status: str = "ok", context: str = OFFICIAL_CONTEXT):
    return {
        "record_type": "phase5_shadow_capture_attempt",
        "source": source,
        "capture_day": day.isoformat(),
        "capture_context": context,
        "status": status,
    }


def _write_ledgers(root: Path, rows: list[dict], attempts: list[dict]) -> None:
    directory = root / "phase5_shadow"
    directory.mkdir(parents=True, exist_ok=True)
    for filename, records in (("rows.jsonl", rows), ("attempts.jsonl", attempts)):
        (directory / filename).write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)
        )


def _row(day: date, *, context: str = OFFICIAL_CONTEXT):
    return {
        "record_type": "phase5_shadow_prediction",
        "source": "vitibet",
        "capture_day": day.isoformat(),
        "capture_context": context,
        "captured_at": f"{day.isoformat()}T10:00:00+00:00",
        "kickoff_at_utc": f"{day.isoformat()}T20:00:00+00:00",
        "identity": {
            "date": day.isoformat(),
            "era_pair_key": [day.isoformat(), "home", [], "away", []],
            "era_pair_normalizer": "FINDINGS-2026-10-07.md#4",
        },
        "probabilities": {"home": 0.55},
        "picks": {},
    }


def test_empty_or_manual_only_ledger_is_not_yet_due_and_has_no_projection():
    today = date(2026, 10, 7)
    status = build_daily_status(
        [_row(today, context="manual_or_unspecified")],
        [_attempt("vitibet", today, context="manual_or_unspecified")],
        as_of=today,
    )
    assert status["overall_status"] == "not_yet_due"
    assert status["realized_s"] == []
    assert status["eligible_s_after_timing"] == []
    assert status["projected_90_day_maturity"] is None
    assert status["clauses"]["1"]["status"] == "not_yet_due"
    assert status["clauses"]["7"]["status"] == "not_yet_due"


def test_malformed_official_era_identity_fails_closed():
    today = date(2026, 10, 7)
    bad_row = _row(today)
    bad_row["identity"]["era_pair_key"] = None

    status = build_daily_status(
        [bad_row], [_attempt("vitibet", today)], as_of=today
    )

    assert status["malformed_rows"] == 1
    assert status["source_metrics"]["vitibet"]["rows"] == 0
    assert status["realized_s"] == []
    assert status["overall_status"] == "blocked"
    assert status["failing_clauses"] == ["1"]


def test_gap_aware_capture_maturity_blocks_at_existing_procedure_landmarks(tmp_path):
    first = date(2026, 7, 10)
    today = first + timedelta(days=89)  # 90 inclusive calendar capture days
    attempts = [
        _attempt("vitibet", first + timedelta(days=offset))
        for offset in range(90)
    ]
    status = build_daily_status(
        [_row(first)], attempts, as_of=today
    )

    assert status["maturity_reached"] is True
    assert status["overall_status"] == "blocked"
    assert status["realized_s"] == ["vitibet"]
    assert status["eligible_s_after_timing"] == ["vitibet"]
    assert status["source_metrics"]["vitibet"]["trailing_30_success_rate"] == 1.0
    assert status["source_metrics"]["vitibet"]["current_gap_aware_streak_days"] == 90
    assert status["clauses"]["1"]["status"] == "pass"
    assert status["clauses"]["4"]["status"] == "blocked_existing_era_evaluator"
    assert status["clauses"]["7"]["status"] == "blocked_forebet_overlap"

    findings = tmp_path / "FINDINGS.md"
    _write_ledgers(tmp_path, [_row(first)], attempts)
    first_status = update_status(
        tmp_path, as_of=today, findings_path=findings, stage_findings=False
    )
    evaluation = json.loads(
        (tmp_path / "phase5_shadow" / "evaluation.json").read_text()
    )
    assert first_status["full_evaluation_status"] == "blocked_existing_procedure"
    assert evaluation["status"] == "blocked"
    assert evaluation["candidate_fit_performed"] is False
    assert evaluation["registry_changed"] is False
    assert evaluation["cuts_derived"] is False
    assert evaluation["blockers"] == list(ERA_EVALUATION_BLOCKERS)
    assert all("code_landmark" in item for item in evaluation["blockers"])


def test_weekly_preflight_cooldown_and_findings_only_on_status_change(tmp_path):
    first = date(2026, 7, 10)
    today = first + timedelta(days=89)
    attempts = [_attempt("vitibet", first + timedelta(days=i)) for i in range(90)]
    findings = tmp_path / "FINDINGS.md"
    _write_ledgers(tmp_path, [_row(first)], attempts)

    one = update_status(tmp_path, as_of=today, findings_path=findings)
    original_findings = findings.read_text()
    two = update_status(tmp_path, as_of=today, findings_path=findings)
    assert one["findings_changed"] is True
    assert two["findings_changed"] is False
    assert findings.read_text() == original_findings
    assert two["full_evaluation_status"] == "not_run_not_due_or_weekly_cooldown"


def test_gap_over_seven_days_restarts_the_maturity_projection():
    first = date(2026, 7, 1)
    today = first + timedelta(days=99)
    successful_days = list(range(10)) + list(range(20, 100))
    attempts = [
        _attempt("vitibet", first + timedelta(days=offset))
        for offset in successful_days
    ]
    status = build_daily_status([_row(first)], attempts, as_of=today)
    metrics = status["source_metrics"]["vitibet"]
    assert status["maturity_reached"] is False
    assert metrics["current_gap_aware_streak_days"] == 80
    assert metrics["max_gap_between_success_days"] == 11
    assert metrics["projected_90_day_maturity"] == (today + timedelta(days=10)).isoformat()
    assert status["overall_status"] == "not_yet_due"


def test_hostile_monthly_warehouse_and_legacy_prediction_exports_cannot_accrue(
    tmp_path,
):
    """Only the eligible sidecar ledgers count; cache-shaped inputs are inert."""
    import gzip

    # These look rich enough to imply maturity, but none has capture context,
    # source-sidecar provenance, or an eligible scheduled attempt.
    with gzip.open(tmp_path / "vitibet_2026-10.csv.gz", "wt", encoding="utf-8") as handle:
        handle.write("date,home,away,p1,px,p2\n")
        for index in range(120):
            handle.write(f"2026-10-{index % 28 + 1:02d},Home {index},Away {index},0.8,0.1,0.1\n")
    with gzip.open(tmp_path / "ml_meta_predictions.csv.gz", "wt", encoding="utf-8") as handle:
        handle.write("date,home,away,ml_p,pick\n2026-10-07,A,B,0.99,home\n")
    (tmp_path / "warehouse.duckdb").write_bytes(b"hostile cache fixture; not opened")
    (tmp_path / "predictions_2026-10-07.json").write_text(
        json.dumps([{"source": "vitibet", "p1": 0.99, "capture_day": "2026-10-07"}])
    )
    findings = tmp_path / "FINDINGS.md"

    status = run_status(
        tmp_path, as_of=date(2026, 10, 7), findings_path=findings, stage_findings=False
    )

    assert status["realized_s"] == []
    assert status["eligible_s_after_timing"] == []
    assert status["projected_90_day_maturity"] is None
    assert status["overall_status"] == "not_yet_due"
    assert status["source_metrics"]["vitibet"]["rows"] == 0
    assert status["source_metrics"]["vitibet"]["official_attempt_records"] == 0


def test_genuine_official_ledger_is_the_positive_maturity_membership_control(tmp_path):
    from edgefactory.phase5_shadow import append_capture_attempt, append_shadow_rows

    day = "2026-10-07"
    append_shadow_rows(
        "vitibet",
        [{
            "date": day,
            "home": "Eligible Home FC",
            "away": "Eligible Away FC",
            "p1": 0.70, "px": 0.20, "p2": 0.10,
            "kickoff": f"{day}T20:00:00Z",
        }],
        capture_day=day,
        captured_at=f"{day}T10:00:00Z",
        capture_context=OFFICIAL_CONTEXT,
        root=tmp_path,
    )
    append_capture_attempt(
        "vitibet",
        capture_day=day,
        status="ok",
        requested_days=[day],
        forward_days=[day],
        capture_context=OFFICIAL_CONTEXT,
        rows_fetched=1,
        rows_appended=1,
        root=tmp_path,
    )

    status = run_status(
        tmp_path,
        as_of=date.fromisoformat(day),
        findings_path=tmp_path / "FINDINGS.md",
        stage_findings=False,
    )

    assert status["realized_s"] == ["vitibet"]
    assert status["eligible_s_after_timing"] == ["vitibet"]
    assert status["source_metrics"]["vitibet"]["rows"] == 1
    assert status["source_metrics"]["vitibet"]["successful_capture_days"] == 1


def test_certifier_rejects_symlinked_inputs_outputs_and_findings_redirection(tmp_path):
    today = date(2026, 10, 7)
    root = tmp_path / "localdata"
    shadow_dir = root / "phase5_shadow"
    shadow_dir.mkdir(parents=True)
    production_file = root / "edges_consensus.json"
    production_file.write_text('{"ml_model":{"sentinel":true}}\n', encoding="utf-8")
    production_before = production_file.read_bytes()
    outside_rows = tmp_path / "outside_rows.jsonl"
    outside_rows.write_text('{"record_type":"phase5_shadow_prediction"}\n', encoding="utf-8")
    (shadow_dir / "rows.jsonl").symlink_to(outside_rows)

    with pytest.raises(Phase5CertifierIsolationError, match="symlink"):
        update_status(
            root, as_of=today, findings_path=tmp_path / "FINDINGS.md", stage_findings=False
        )
    assert production_file.read_bytes() == production_before
    assert not (tmp_path / "FINDINGS.md").exists()

    (shadow_dir / "rows.jsonl").unlink()
    (shadow_dir / "status.json").symlink_to(production_file)
    with pytest.raises(Phase5CertifierIsolationError, match="symlink"):
        update_status(
            root, as_of=today, findings_path=tmp_path / "FINDINGS.md", stage_findings=False
        )
    assert production_file.read_bytes() == production_before
    assert not (tmp_path / "FINDINGS.md").exists()

    (shadow_dir / "status.json").unlink()
    shadow_dir.rmdir()
    external_shadow = tmp_path / "external_shadow"
    external_shadow.mkdir()
    (external_shadow / "rows.jsonl").write_text("", encoding="utf-8")
    shadow_dir.symlink_to(external_shadow, target_is_directory=True)
    with pytest.raises(Phase5CertifierIsolationError, match="directory must not be a symlink"):
        update_status(
            root, as_of=today, findings_path=tmp_path / "FINDINGS.md", stage_findings=False
        )
    assert production_file.read_bytes() == production_before
    assert not (tmp_path / "FINDINGS.md").exists()

    shadow_dir.unlink()
    shadow_dir.mkdir()
    (shadow_dir / "rows.jsonl").hardlink_to(production_file)
    with pytest.raises(Phase5CertifierIsolationError, match="single-link regular file"):
        update_status(
            root, as_of=today, findings_path=tmp_path / "FINDINGS.md", stage_findings=False
        )
    assert production_file.read_bytes() == production_before
    assert not (tmp_path / "FINDINGS.md").exists()

    (shadow_dir / "rows.jsonl").unlink()
    (shadow_dir / "attempts.jsonl").write_text("", encoding="utf-8")
    with pytest.raises(Phase5CertifierIsolationError, match="Findings\\*\\.md"):
        update_status(
            root, as_of=today, findings_path=production_file, stage_findings=False
        )
    assert production_file.read_bytes() == production_before


def test_certifier_direct_file_io_stays_inside_shadow_evidence_and_findings(tmp_path, monkeypatch):
    root = tmp_path / "localdata"
    _write_ledgers(root, [], [])
    findings = tmp_path / "FINDINGS.md"
    production_paths = {
        root / "edges_consensus.json": b'{"edges":[]}\\n',
        root / "ml_meta_predictions.csv.gz": b"legacy export sentinel",
        root / "vitibet_2026-10.csv.gz": b"monthly source sentinel",
        root / "warehouse.duckdb": b"warehouse sentinel",
        root / "picks_2026-10-07.json": b"[]",
        root / "auto_tickets_state.json": b'{"bank":100}\\n',
        root / "phase5_shadow" / "nested_source.csv.gz": b"nested hostile sentinel",
    }
    for path, payload in production_paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    before = {path: path.read_bytes() for path in production_paths}

    shadow_dir = root / "phase5_shadow"
    allowed_reads = {
        (shadow_dir / "rows.jsonl").resolve(),
        (shadow_dir / "attempts.jsonl").resolve(),
        (shadow_dir / "status.json").resolve(),
        (shadow_dir / "evaluation.json").resolve(),
    }
    allowed_writes = {
        findings.resolve(),
        (shadow_dir / "status.json.tmp").resolve(),
        (shadow_dir / "evaluation.json.tmp").resolve(),
    }
    accesses: list[tuple[Path, str]] = []
    original_path_open = Path.open
    original_builtin_open = builtins.open

    def check_access(file: object, mode: str) -> None:
        if isinstance(file, bytes):
            path = Path(file.decode("utf-8")).resolve(strict=False)
        elif isinstance(file, (str, Path)):
            path = Path(file).resolve(strict=False)
        else:
            return
        accesses.append((path, mode))
        if any(flag in mode for flag in ("w", "a", "x", "+")):
            assert path in allowed_writes, f"certifier write escaped its boundary: {path}"
        else:
            assert path in allowed_reads, f"certifier read escaped its boundary: {path}"

    def guarded_path_open(self, mode="r", *args, **kwargs):
        check_access(self, mode)
        return original_path_open(self, mode, *args, **kwargs)

    def guarded_builtin_open(file, mode="r", *args, **kwargs):
        check_access(file, mode)
        return original_builtin_open(file, mode, *args, **kwargs)

    with monkeypatch.context() as guard:
        guard.setattr(Path, "open", guarded_path_open)
        guard.setattr(builtins, "open", guarded_builtin_open)
        status = run_status(
            root,
            as_of=date(2026, 10, 7),
            findings_path=findings,
            stage_findings=False,
        )

    assert status["overall_status"] == "not_yet_due"
    assert accesses
    assert all(path in allowed_reads | allowed_writes for path, _mode in accesses)
    read_paths = {
        path for path, mode in accesses
        if not any(flag in mode for flag in ("w", "a", "x", "+"))
    }
    write_paths = {
        path for path, mode in accesses
        if any(flag in mode for flag in ("w", "a", "x", "+"))
    }
    assert read_paths <= allowed_reads
    assert write_paths <= allowed_writes
    assert (shadow_dir / "status.json").is_file()
    assert findings.is_file()
    assert {path: path.read_bytes() for path in production_paths} == before


def test_certifier_code_is_structurally_separate_from_pick_and_ticket_paths():
    for path in (
        ROOT / "src" / "edgefactory" / "phase5_certifier.py",
        ROOT / "scripts" / "phase5_certify.py",
    ):
        tree = ast.parse(path.read_text())
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        assert not any(
            "picks_today" in name or "auto_tickets" in name or "consensus" in name
            for name in imported
        )

    cli = _load_script()
    assert callable(cli.main)
