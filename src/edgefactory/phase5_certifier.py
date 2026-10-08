"""Read-only Phase 5 maturity status and strict certification preflight.

This module only reads the forward shadow ledgers and writes research status
artifacts. It never imports production pick, vote, ticket, or bank paths. The
legacy miner cannot consume the era-local windows contract; when maturity is
reached, this module records that blocker instead of fitting a substitute.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

DECLARED_SOURCES = (
    "forebet", "zulubet", "statarea", "vitibet", "bzzoiro", "betclan",
    "scoutingstats", "betminer",
)
SHADOW_SOURCES = ("vitibet", "bzzoiro", "betclan", "scoutingstats", "betminer")
OFFICIAL_CONTEXT = "official_daily_pipeline"
LOCAL_TZ = ZoneInfo("Africa/Johannesburg")
MATURITY_DAYS = 90
MAX_CAPTURE_GAP_DAYS = 7
CAPTURE_SUCCESS_FLOOR = 0.95
PREKICKOFF_FLOOR = 0.99
FULL_EVAL_INTERVAL_DAYS = 7


class Phase5CertifierIsolationError(RuntimeError):
    """A certifier input/output path crossed the Phase 5 evidence boundary."""


def _phase5_shadow_directory(root: Path | str) -> Path:
    root_path = Path(root).resolve()
    directory = root_path / "phase5_shadow"
    if directory.is_symlink():
        raise Phase5CertifierIsolationError("phase5_shadow directory must not be a symlink")
    if directory.exists() and not directory.is_dir():
        raise Phase5CertifierIsolationError("phase5_shadow path must be a directory")
    resolved = directory.resolve(strict=False)
    if not resolved.is_relative_to(root_path):
        raise Phase5CertifierIsolationError("phase5_shadow directory escapes the configured root")
    return directory


def _phase5_shadow_file(root: Path | str, name: str) -> Path:
    if name not in {"rows.jsonl", "attempts.jsonl", "status.json", "evaluation.json"}:
        raise Phase5CertifierIsolationError(f"unsupported Phase 5 certifier path: {name}")
    directory = _phase5_shadow_directory(root)
    path = directory / name
    if path.is_symlink():
        raise Phase5CertifierIsolationError(f"Phase 5 certifier file must not be a symlink: {name}")
    if path.exists():
        metadata = path.stat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise Phase5CertifierIsolationError(
                f"Phase 5 certifier file must be a single-link regular file: {name}"
            )
    if not path.resolve(strict=False).is_relative_to(directory.resolve(strict=False)):
        raise Phase5CertifierIsolationError(
            f"Phase 5 certifier file escapes its evidence directory: {name}"
        )
    return path


def _validate_findings_path(path: Path | str) -> Path:
    findings = Path(path)
    if findings.suffix.lower() != ".md" or not findings.name.casefold().startswith("findings"):
        raise Phase5CertifierIsolationError(
            "certifier Findings output must be a Findings*.md document"
        )
    for component in (findings, *findings.parents):
        if component.is_symlink():
            raise Phase5CertifierIsolationError(
                "certifier Findings path must not traverse symlinks"
            )
    if findings.exists():
        metadata = findings.stat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise Phase5CertifierIsolationError(
                "certifier Findings output must be a single-link regular file"
            )
    return findings


def _checked_phase5_artifact_path(path: Path) -> tuple[Path, Path]:
    if path.name not in {"status.json", "evaluation.json"}:
        raise Phase5CertifierIsolationError(
            "certifier may write only its status/evaluation artifacts"
        )
    checked = _phase5_shadow_file(path.parent.parent, path.name)
    temporary = checked.with_suffix(checked.suffix + ".tmp")
    if temporary.is_symlink():
        raise Phase5CertifierIsolationError("certifier temporary output must not be a symlink")
    if temporary.exists():
        metadata = temporary.stat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise Phase5CertifierIsolationError(
                "certifier temporary output must be a single-link regular file"
            )
    if not temporary.resolve(strict=False).is_relative_to(checked.parent.resolve(strict=False)):
        raise Phase5CertifierIsolationError(
            "certifier temporary output escapes its evidence directory"
        )
    return checked, temporary


# These landmarks are a fail-closed preflight, not a replacement evaluator.
ERA_EVALUATION_BLOCKERS = (
    {
        "code_landmark": "scripts/mine_consensus.py::train_ml_meta_classifier:479-491",
        "reason": (
            "legacy query requires non-null fb_p, zb_p, and sa_p and reads the "
            "warehouse consensus3 view, so it cannot train the fixed forward-only K"
        ),
    },
    {
        "code_landmark": "scripts/mine_consensus.py::train_ml_meta_classifier:499-512,602-611",
        "reason": (
            "legacy trainer uses a single absolute split and hard-coded 500/300 row "
            "floors; it does not implement era-train / 30-day validation / trailing-30 test"
        ),
    },
    {
        "code_landmark": "scripts/mine_consensus.py::stats:152-174; evaluate:177-190",
        "reason": (
            "existing evaluator divides all dates only at one split and has no separate "
            "era validation, recent, paired Brier/logloss bootstrap, or coverage calculation"
        ),
    },
    {
        "code_landmark": "scripts/mine_consensus.py::train_ml_meta_classifier:633-637; main:902-913,1258-1262",
        "reason": (
            "the legacy path materializes ml_meta_predictions.csv.gz and passes its payload "
            "to write_registry; it cannot be invoked as a read-only era preflight"
        ),
    },
    {
        "code_landmark": "docs/operator/FINDINGS-2026-10-07.md §9.0 clause 3",
        "reason": (
            "the fixed 200-fixture identity audit keys / selection recipe are not yet "
            "materialized; no sample may be selected after inspecting outcomes"
        ),
    },
    {
        "code_landmark": "docs/operator/FINDINGS-2026-10-07.md §9.0 clauses 4 and 6; §9.3 clause-5 amendment",
        "reason": (
            "clause 5's comparator amendment does not define the incumbent-era paired-overlap "
            "or coverage-floor comparator when the true forward incumbent cannot materialize"
        ),
    },
    {
        "code_landmark": "docs/operator/FINDINGS-2026-10-07.md §9.0 clause 7",
        "reason": (
            "pairwise agreement is required against each existing source; Forebet has no "
            "authorized forward capture, so a 200-row Forebet overlap is unavailable"
        ),
    },
)


def _parse_day(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except (TypeError, ValueError):
        return None


def _strict_day(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if value == parsed.isoformat() else None


def _parse_timestamp(value: object) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    malformed = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return records, malformed
    for line in lines:
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except (TypeError, ValueError):
            malformed += 1
            continue
        if isinstance(record, dict):
            records.append(record)
        else:
            malformed += 1
    return records, malformed


def _date_range(first: date, last: date) -> list[date]:
    if last < first:
        return []
    return [first + timedelta(days=i) for i in range((last - first).days + 1)]


def _valid_official_row(row: dict[str, Any]) -> bool:
    identity = row.get("identity")
    if not isinstance(identity, dict):
        return False
    pair_key = identity.get("era_pair_key")
    fixture_day = _strict_day(identity.get("date"))
    return bool(
        row.get("record_type") == "phase5_shadow_prediction"
        and row.get("source") in SHADOW_SOURCES
        and _strict_day(row.get("capture_day")) is not None
        and fixture_day is not None
        and isinstance(pair_key, list) and len(pair_key) == 5
        and pair_key[0] == fixture_day.isoformat()
        and isinstance(pair_key[1], str) and pair_key[1]
        and isinstance(pair_key[2], list)
        and all(isinstance(marker, str) for marker in pair_key[2])
        and isinstance(pair_key[3], str) and pair_key[3]
        and isinstance(pair_key[4], list)
        and all(isinstance(marker, str) for marker in pair_key[4])
        and identity.get("era_pair_normalizer") == "FINDINGS-2026-10-07.md#4"
        and isinstance(row.get("probabilities"), dict)
        and isinstance(row.get("picks"), dict)
        and bool(row["probabilities"] or row["picks"])
    )


def _valid_official_attempt(attempt: dict[str, Any]) -> bool:
    return bool(
        attempt.get("record_type") == "phase5_shadow_capture_attempt"
        and attempt.get("source") in SHADOW_SOURCES
        and _strict_day(attempt.get("capture_day")) is not None
        and isinstance(attempt.get("status"), str) and attempt["status"]
    )


def _row_timing(row: dict[str, Any]) -> tuple[bool, bool]:
    capture = _parse_timestamp(row.get("captured_at"))
    kickoff = _parse_timestamp(row.get("kickoff_at_utc"))
    timestamp_valid = capture is not None
    return timestamp_valid, bool(timestamp_valid and kickoff and capture < kickoff)


def _source_metrics(
    source: str,
    rows: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    *,
    era_start: date | None,
    as_of: date,
) -> dict[str, Any]:
    source_rows = [
        row for row in rows
        if row.get("source") == source
        and row.get("capture_context") == OFFICIAL_CONTEXT
        and _valid_official_row(row)
        and (capture_day := _parse_day(row.get("capture_day"))) is not None
        and capture_day <= as_of
    ]
    source_attempts = [
        attempt for attempt in attempts
        if attempt.get("source") == source
        and attempt.get("capture_context") == OFFICIAL_CONTEXT
        and _valid_official_attempt(attempt)
        and (capture_day := _parse_day(attempt.get("capture_day"))) is not None
        and capture_day <= as_of
    ]
    attempt_by_day: dict[date, list[dict[str, Any]]] = {}
    for attempt in source_attempts:
        day = _parse_day(attempt.get("capture_day"))
        if day is not None:
            attempt_by_day.setdefault(day, []).append(attempt)

    if era_start is None or era_start > as_of:
        scheduled_days: list[date] = []
        trailing_days: list[date] = []
        success_days: set[date] = set()
        recent_rate = None
        longest_streak_start = None
        streak_span = 0
        max_gap = None
    else:
        scheduled_days = _date_range(era_start, as_of)
        trailing_start = max(era_start, as_of - timedelta(days=29))
        trailing_days = _date_range(trailing_start, as_of)
        success_days = {
            day for day, records in attempt_by_day.items()
            if any(record.get("status") == "ok" for record in records)
        }
        recent_successes = sum(day in success_days for day in trailing_days)
        recent_rate = recent_successes / len(trailing_days) if trailing_days else None

        source_successes = sorted(day for day in success_days if day in scheduled_days)
        longest_streak_start = source_successes[0] if source_successes else None
        previous = None
        max_gap_value = 0
        for day in source_successes:
            if previous is not None and (day - previous).days > MAX_CAPTURE_GAP_DAYS:
                longest_streak_start = day
            if previous is not None:
                max_gap_value = max(max_gap_value, (day - previous).days)
            previous = day
        if source_successes and (as_of - source_successes[-1]).days > MAX_CAPTURE_GAP_DAYS:
            longest_streak_start = None
        streak_span = (
            (as_of - longest_streak_start).days + 1
            if longest_streak_start is not None else 0
        )
        max_gap = max_gap_value if source_successes else None

    timestamp_valid = timing_pass = 0
    for row in source_rows:
        has_timestamp, pre_kickoff = _row_timing(row)
        timestamp_valid += int(has_timestamp)
        timing_pass += int(pre_kickoff)
    timestamp_rate = timestamp_valid / len(source_rows) if source_rows else None
    timing_rate = timing_pass / len(source_rows) if source_rows else None
    row_count = len(source_rows)
    membership = bool(
        row_count > 0 and recent_rate is not None
        and recent_rate >= CAPTURE_SUCCESS_FLOOR
    )
    timing_eligible = bool(
        membership and timestamp_rate == 1.0
        and timing_rate is not None and timing_rate >= PREKICKOFF_FLOOR
    )
    projected_maturity = None
    if membership and timing_eligible and longest_streak_start is not None:
        remaining = max(0, MATURITY_DAYS - streak_span)
        projected_maturity = (as_of + timedelta(days=remaining)).isoformat()

    return {
        "rows": row_count,
        "official_attempt_records": len(source_attempts),
        "scheduled_days_since_era_start": len(scheduled_days),
        "trailing_30_scheduled_days": len(trailing_days),
        "trailing_30_success_days": (
            sum(day in success_days for day in trailing_days) if trailing_days else 0
        ),
        "trailing_30_success_rate": round(recent_rate, 6) if recent_rate is not None else None,
        "missing_scheduled_attempt_days": sum(day not in attempt_by_day for day in scheduled_days),
        "successful_capture_days": len(success_days),
        "latest_success_day": max(success_days).isoformat() if success_days else None,
        "current_gap_aware_streak_days": streak_span,
        "max_gap_between_success_days": max_gap,
        "capture_timestamp_rate": round(timestamp_rate, 6) if timestamp_rate is not None else None,
        "pre_kickoff_rate": round(timing_rate, 6) if timing_rate is not None else None,
        "realized_membership": membership,
        "eligible_after_timing": timing_eligible,
        "projected_90_day_maturity": projected_maturity,
    }


def _clause_statuses(
    source_metrics: dict[str, dict[str, Any]],
    *,
    malformed_rows: int,
    malformed_attempts: int,
) -> tuple[dict[str, dict[str, Any]], list[str], list[str], str | None, bool]:
    realized = [
        source for source in SHADOW_SOURCES
        if source_metrics[source]["realized_membership"]
    ]
    timing_eligible = [
        source for source in realized
        if source_metrics[source]["eligible_after_timing"]
    ]
    maturity_states = [
        source_metrics[source]["current_gap_aware_streak_days"] >= MATURITY_DAYS
        and source_metrics[source]["trailing_30_success_rate"] is not None
        and source_metrics[source]["trailing_30_success_rate"] >= CAPTURE_SUCCESS_FLOOR
        for source in timing_eligible
    ]
    maturity_reached = bool(timing_eligible) and all(maturity_states)
    if malformed_rows or malformed_attempts:
        clause1_status = "failed"
    elif not timing_eligible:
        clause1_status = "not_yet_due"
    elif any(not value for value in maturity_states):
        clause1_status = "not_yet_due"
    else:
        clause1_status = "pass"

    if not realized:
        clause2_status = "not_yet_due"
    elif len(timing_eligible) < len(realized):
        # Clause 2 explicitly permits exclusion of a contaminated source.
        clause2_status = "pass_with_source_exclusions"
    else:
        clause2_status = "pass"

    clause34_status = "blocked_existing_era_evaluator" if maturity_reached else "not_yet_due"
    projected_dates = [
        source_metrics[source]["projected_90_day_maturity"]
        for source in timing_eligible
        if source_metrics[source]["projected_90_day_maturity"]
    ]
    projected_maturity = max(projected_dates) if projected_dates else None

    clauses = {
        "1": {
            "status": clause1_status,
            "reason": "90-day gap-aware capture, trailing-30 success, and 100% timestamps",
        },
        "2": {
            "status": clause2_status,
            "reason": "≥99% pre-kickoff timing; contaminated sources are excluded from S",
            "excluded_sources": [source for source in realized if source not in timing_eligible],
        },
        "3": {
            "status": "not_yet_due",
            "reason": "fixed 200-fixture marker-aware identity audit is not materialized",
            "sample_n": 0,
        },
        "4": {
            "status": clause34_status,
            "reason": "era-local gates cannot run until maturity and a compatible evaluator exists",
        },
        "5": {
            "status": clause34_status,
            "reason": "paired Brier/logloss bootstrap awaits the era-local evaluator",
        },
        "6": {
            "status": "blocked_incumbent_coverage_comparator" if maturity_reached else "not_yet_due",
            "reason": "coverage floor awaits a same-window incumbent/candidate scorecard",
        },
        "7": {
            "status": "blocked_forebet_overlap" if maturity_reached else "not_yet_due",
            "reason": "≥200 common rows are required for every existing source; Forebet is parked",
        },
        "8": {
            "status": "not_yet_due",
            "reason": "pre-activation revert dry run is not recorded",
        },
        "9": {
            "status": "not_yet_due",
            "reason": "no activation is authorized or recorded",
        },
    }
    if malformed_rows or malformed_attempts:
        clauses["1"]["malformed_records"] = {
            "rows": malformed_rows,
            "attempts": malformed_attempts,
        }
    return clauses, realized, timing_eligible, projected_maturity, maturity_reached


def _status_signature(status: dict[str, Any]) -> str:
    signature = {
        "overall": status["overall_status"],
        "realized_s": status["realized_s"],
        "eligible_s": status["eligible_s_after_timing"],
        "clauses": {key: value["status"] for key, value in status["clauses"].items()},
        "source": {
            source: {
                "membership": data["realized_membership"],
                "timing_eligible": data["eligible_after_timing"],
            }
            for source, data in status["source_metrics"].items()
        },
    }
    return hashlib.sha256(
        json.dumps(signature, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_daily_status(
    rows: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    *,
    as_of: date,
    malformed_rows: int = 0,
    malformed_attempts: int = 0,
) -> dict[str, Any]:
    malformed_rows += sum(
        row.get("capture_context") == OFFICIAL_CONTEXT and not _valid_official_row(row)
        for row in rows
    )
    malformed_attempts += sum(
        attempt.get("capture_context") == OFFICIAL_CONTEXT
        and not _valid_official_attempt(attempt)
        for attempt in attempts
    )
    official_attempts = [
        attempt for attempt in attempts
        if attempt.get("capture_context") == OFFICIAL_CONTEXT
        and _valid_official_attempt(attempt)
    ]
    official_run_days = [
        day for attempt in official_attempts
        if (day := _parse_day(attempt.get("capture_day"))) is not None and day <= as_of
    ]
    era_start = min(official_run_days) if official_run_days else None
    source_metrics = {
        source: _source_metrics(
            source, rows, official_attempts, era_start=era_start, as_of=as_of
        )
        for source in SHADOW_SOURCES
    }
    clauses, realized, eligible, projected, maturity_reached = _clause_statuses(
        source_metrics,
        malformed_rows=malformed_rows,
        malformed_attempts=malformed_attempts,
    )
    overall_status = (
        "blocked" if clauses["1"]["status"] == "failed" or maturity_reached
        else "not_yet_due"
    )
    failing_clauses = [
        clause for clause, detail in clauses.items()
        if detail["status"] == "failed" or detail["status"].startswith("blocked")
    ]
    not_yet_due_clauses = [
        clause for clause, detail in clauses.items()
        if detail["status"] == "not_yet_due"
    ]
    return {
        "schema": 1,
        "record_type": "phase5_daily_certifier_status",
        "as_of": as_of.isoformat(),
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "declared_s": list(DECLARED_SOURCES),
        "realized_s": realized,
        "absent_declared_s": [source for source in DECLARED_SOURCES if source not in realized],
        "eligible_s_after_timing": eligible,
        "source_metrics": source_metrics,
        "era_start": era_start.isoformat() if era_start else None,
        "projected_90_day_maturity": projected,
        "projected_first_certification": None,
        "projection_note": (
            "maturity estimate is based on measured gap-aware capture accrual; "
            "gate-n and settled-outcome projections are unavailable until the era evaluator runs"
        ),
        "clauses": clauses,
        "maturity_reached": maturity_reached,
        "overall_status": overall_status,
        "failing_clauses": failing_clauses,
        "not_yet_due_clauses": not_yet_due_clauses,
        "malformed_rows": malformed_rows,
        "malformed_attempts": malformed_attempts,
    }


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path, temporary = _checked_phase5_artifact_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _append_findings(path: Path, status: dict[str, Any]) -> None:
    path = _validate_findings_path(path)
    statuses = ", ".join(
        f"C{clause}={detail['status']}" for clause, detail in status["clauses"].items()
    )
    paragraph = (
        f"\n\n**Phase 5 status change ({status['as_of']}).** "
        f"Overall `{status['overall_status']}`; declared S={','.join(status['declared_s'])}; "
        f"realized S={','.join(status['realized_s']) or 'none'}; eligible after timing="
        f"{','.join(status['eligible_s_after_timing']) or 'none'}; {statuses}; "
        f"projected 90-day maturity={status['projected_90_day_maturity'] or 'unavailable'}; "
        "no candidate fit, cuts, registry write, or activation was performed."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(paragraph)


def _full_evaluation_due(status: dict[str, Any], evaluation_path: Path, as_of: date) -> bool:
    if not status.get("maturity_reached") or not status["eligible_s_after_timing"]:
        return False
    try:
        previous = json.loads(evaluation_path.read_text(encoding="utf-8"))
        previous_date = _parse_day(previous.get("attempted_on"))
    except (FileNotFoundError, ValueError, TypeError):
        previous_date = None
    if previous_date is None:
        return True
    return (as_of - previous_date).days >= FULL_EVAL_INTERVAL_DAYS


def update_status(
    root: Path,
    *,
    as_of: date,
    findings_path: Path,
    stage_findings: bool = False,
) -> dict[str, Any]:
    findings_path = _validate_findings_path(findings_path)
    rows, malformed_rows = _read_jsonl(_phase5_shadow_file(root, "rows.jsonl"))
    attempts, malformed_attempts = _read_jsonl(_phase5_shadow_file(root, "attempts.jsonl"))
    status = build_daily_status(
        rows, attempts, as_of=as_of,
        malformed_rows=malformed_rows,
        malformed_attempts=malformed_attempts,
    )
    status_path = _phase5_shadow_file(root, "status.json")
    evaluation_path = _phase5_shadow_file(root, "evaluation.json")
    try:
        previous = json.loads(status_path.read_text(encoding="utf-8"))
        previous_signature = previous.get("status_signature")
    except (FileNotFoundError, ValueError, TypeError):
        previous_signature = None
    signature = _status_signature(status)
    status["status_signature"] = signature
    if signature != previous_signature:
        _append_findings(findings_path, status)
        if stage_findings:
            subprocess.run(
                ["git", "add", "--", str(findings_path)],
                cwd=Path(__file__).resolve().parents[2],
                check=True,
            )
        status["findings_changed"] = True
    else:
        status["findings_changed"] = False

    if _full_evaluation_due(status, evaluation_path, as_of):
        _atomic_json(evaluation_path, {
            "schema": 1,
            "record_type": "phase5_full_evaluation_preflight",
            "attempted_on": as_of.isoformat(),
            "status": "blocked",
            "blockers": list(ERA_EVALUATION_BLOCKERS),
            "candidate_fit_performed": False,
            "registry_changed": False,
            "cuts_derived": False,
        })
        status["full_evaluation_status"] = "blocked_existing_procedure"
    else:
        status["full_evaluation_status"] = "not_run_not_due_or_weekly_cooldown"

    _atomic_json(status_path, status)
    return status


def run_status(
    root: Path,
    *,
    as_of: date | None = None,
    findings_path: Path | None = None,
    stage_findings: bool | None = None,
) -> dict[str, Any]:
    as_of = as_of or datetime.now(LOCAL_TZ).date()
    findings_path = findings_path or (
        Path(__file__).resolve().parents[2] / "docs" / "operator" / "FINDINGS-2026-10-07.md"
    )
    if stage_findings is None:
        stage_findings = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    return update_status(
        root, as_of=as_of, findings_path=findings_path,
        stage_findings=stage_findings,
    )
