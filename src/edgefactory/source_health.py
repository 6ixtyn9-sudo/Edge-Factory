"""Small, local-only source-health state helpers.

This module records operational observations; it never gates a pick and never
creates source rows. The persisted streak is intentionally separate from the
per-day source contract written by the daily orchestrator.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", ROOT / "localdata"))
STATE_PATH = LOCALDATA / "source_health_state.json"


def _empty_state() -> dict[str, Any]:
    return {"schema": 1, "updated_at": None, "sources": {}}


def load_state() -> dict[str, Any]:
    try:
        payload = json.loads(STATE_PATH.read_text())
        if isinstance(payload, dict) and isinstance(payload.get("sources"), dict):
            payload.setdefault("schema", 1)
            return payload
    except (OSError, ValueError, TypeError):
        pass
    return _empty_state()


def _write_state(payload: dict[str, Any]) -> None:
    LOCALDATA.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(STATE_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(STATE_PATH)


def record_bzzoiro_run(
    day: str,
    diagnostics: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Persist one upstream observation and return the Bzzoiro record.

    A run is all-zero only when all three upstream counters are zero. A
    cache-only enrichment does not advance or reset the streak because it did
    not observe the upstream today. This is visibility state, not a gate.
    """
    state = load_state()
    source = dict(state["sources"].get("bzzoiro") or {})
    status = str(diagnostics.get("status") or "unknown")
    attempted = status not in {"not_run", "cache_only", "unknown"}
    best_results = int(diagnostics.get("best_results") or 0)
    comparison_rows = int(diagnostics.get("comparison_rows") or 0)
    rows = int(diagnostics.get("rows") or 0)
    all_zero = attempted and best_results == 0 and comparison_rows == 0 and rows == 0
    if attempted:
        streak = int(source.get("zero_run_streak") or 0)
        streak = streak + 1 if all_zero else 0
        source.update({
            "zero_run_streak": streak,
            "last_run_day": str(day),
            "last_status": status,
            "last_all_zero": all_zero,
            "last_best_results": best_results,
            "last_comparison_rows": comparison_rows,
            "last_rows": rows,
            "last_http_statuses": list(diagnostics.get("http_statuses") or []),
            "last_errors": list(diagnostics.get("errors") or [])[:8],
            "last_quota_hint": diagnostics.get("quota_hint", "none"),
        })
    state["sources"]["bzzoiro"] = source
    state["updated_at"] = (now or datetime.now(timezone.utc)).isoformat()
    _write_state(state)
    return source


def bzzoiro_unavailable(*, threshold: int = 3) -> bool:
    record = load_state().get("sources", {}).get("bzzoiro", {})
    try:
        return int(record.get("zero_run_streak") or 0) >= threshold
    except (TypeError, ValueError):
        return False


def bzzoiro_status_line() -> str | None:
    record = load_state().get("sources", {}).get("bzzoiro", {})
    try:
        streak = int(record.get("zero_run_streak") or 0)
    except (TypeError, ValueError):
        streak = 0
    if streak >= 3:
        return f"bzz UNAVAILABLE — {streak} consecutive all-zero runs (visibility only; no gate change)"
    return None
