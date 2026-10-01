"""Remove ticket state created by the unapproved future-ticket path.

The 2026-10-01 run carded 2026-10-02 because ``HORIZON_TICKET_POLICY``
defaulted to ``event_date_cards``. That card skipped the build-hour and
freeze gates (both written ``target == today``) and entered the state
file as a live open slip staking 21.116% of capital. ``free_bank`` is
``bank`` minus committed stakes across every open date, so the draft
locked a fifth of the bank a day before the event.

This module removes only slips that path created. It is deliberately
conservative: a slip is removed only when it is dated after the run that
created it AND has no slip file, no frozen marker, no settled leg and no
history entry. Anything else is legitimate operation and is left alone,
including slips that merely look stale.

Nothing here reimplements staking, settlement or ticket formation. It
deletes bad rows; it never writes new ones and never adjusts the bank,
which is a stored total with committed stakes derived from the open
slips at read time.
"""

from __future__ import annotations

from pathlib import Path


def slip_is_unapproved_future_draft(slip: dict, *, run_date: str,
                                    localdata: Path,
                                    history_dates: set | None = None) -> bool:
    """True only for a slip the default daily run should never have made."""
    date = str(slip.get("date") or "")[:10]
    if not date or date <= str(run_date)[:10]:
        return False                      # same-day or past: not this path
    if (Path(localdata) / f"auto_tickets_{date}.txt").exists():
        return False                      # a real slip file backs it
    if (Path(localdata) / f"auto_tickets_{date}.frozen").exists():
        return False                      # it froze, so it was today once
    if date in (history_dates or set()):
        return False                      # already recorded as a bet day
    for acca in slip.get("accas") or []:
        if acca.get("won") is not None:
            return False                  # settled: real money resolved
        for leg in acca.get("legs") or []:
            if leg.get("result") is not None:
                return False
    return True


def clean_state(state: dict, *, run_date: str, localdata: Path) -> tuple[dict, list]:
    """Drop unapproved future drafts from ``state``.

    Returns the state and the slips removed. The bank is untouched:
    committed capital is derived from ``open_slips``, so removing the
    draft releases its stake with no recomputation.
    """
    history_dates = {str(h.get("date") or "")[:10]
                     for h in state.get("history") or []}
    keep, removed = [], []
    for slip in state.get("open_slips") or []:
        if slip_is_unapproved_future_draft(
                slip, run_date=run_date, localdata=localdata,
                history_dates=history_dates):
            removed.append(slip)
        else:
            keep.append(slip)
    state["open_slips"] = keep
    return state, removed


def clean_slice_ledger_lines(lines, removed_dates: set) -> tuple[list, int]:
    """Drop slice-ledger rows belonging to a removed future draft."""
    import json

    keep, dropped = [], 0
    for line in lines:
        text = line.strip()
        if not text:
            continue
        try:
            row = json.loads(text)
        except ValueError:
            keep.append(line)             # never discard unparseable history
            continue
        if str(row.get("date") or "")[:10] in removed_dates \
                and row.get("src") == "slip":
            dropped += 1
            continue
        keep.append(line)
    return keep, dropped
