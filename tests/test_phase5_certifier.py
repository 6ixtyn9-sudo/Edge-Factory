from __future__ import annotations

import ast
import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path

from edgefactory.phase5_certifier import (
    ERA_EVALUATION_BLOCKERS,
    OFFICIAL_CONTEXT,
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
