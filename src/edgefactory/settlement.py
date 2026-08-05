"""Pure settlement-disposition helpers.

A missing final score is not itself a loss, a draw, or proof that an event was
postponed. These helpers map only positive terminal event-status evidence into
an audit disposition. Unknown/scheduled/live statuses remain non-terminal.
"""
from __future__ import annotations

import re

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
