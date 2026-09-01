"""Pure settlement-disposition helpers.

A missing final score is not itself a loss, a draw, or proof that an event was
postponed. These helpers map only positive terminal event-status evidence into
an audit disposition. Unknown/scheduled/live statuses remain non-terminal.

``load_verified_results`` reads operator-confirmed final scores (the
``verified_event_dispositions.json`` analogue for score facts). Verified rows
outrank every donor in both the audit and the auto-ticket grader, so a single
bad donor row can no longer hold a pick as an alias-outcome conflict.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

POSTPONED = "POSTPONED"
CANCELLED = "CANCELLED"
ABANDONED = "ABANDONED"

_TERMINAL_STATUS_PATTERNS = (
    (POSTPONED, re.compile(r"\b(postp(?:oned)?|postponed)\b", re.IGNORECASE)),
    (CANCELLED, re.compile(r"\b(cancel(?:led|ed)?|canc\.)\b", re.IGNORECASE)),
    (ABANDONED, re.compile(r"\b(abandon(?:ed)?|abnd\.)\b", re.IGNORECASE)),
)


def terminal_event_disposition(status: object) -> str | None:
    """Return a positive terminal no-score disposition, else ``None``.

    Deliberately does not map ``scheduled``, blank, live, suspended, or a
    missing score to a disposition. Those states are not proof that an original
    fixture was voided.
    """
    text = str(status or "").strip()
    if not text:
        return None
    for disposition, pattern in _TERMINAL_STATUS_PATTERNS:
        if pattern.search(text):
            return disposition
    return None


def is_void_disposition(value: object) -> bool:
    return str(value or "") in {POSTPONED, CANCELLED, ABANDONED}


def _verified_results_path() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    preferred = root / "Config" / "verified_results.json"
    if preferred.exists() or (root / "Config").exists():
        return preferred
    return root / "config" / "verified_results.json"


def load_verified_results(path: Path | None = None) -> list[dict]:
    """Load operator-verified final scores.

    These are authoritative score facts that outrank every donor. Invalid rows
    (missing date/teams/score, non-home-away-draw outcome) fail closed.
    """
    p = path or _verified_results_path()
    try:
        payload = json.loads(p.read_text())
        rows = payload.get("rows") or []
    except Exception:
        return []
    out: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        day = str(row.get("date") or "")[:10]
        home = str(row.get("home") or "")
        away = str(row.get("away") or "")
        try:
            hs = int(row["hs"])
            gs = int(row["gs"])
        except (KeyError, TypeError, ValueError):
            continue
        outcome = str(row.get("outcome") or "")
        if not day or not home or not away or outcome not in ("home", "away", "draw"):
            continue
        out.append({
            "date": day,
            "home": home,
            "away": away,
            "hs": hs,
            "gs": gs,
            "outcome": outcome,
            "src": str(row.get("src") or "operator_verified"),
        })
    return out
