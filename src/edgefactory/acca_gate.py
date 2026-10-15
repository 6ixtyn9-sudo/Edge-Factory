"""Dynamic acca price-evidence gate with hysteresis.

A price-evidence label is blocked from accumulators when its recent calibration
is clearly poor, and unblocked only after it recovers. Calibration is measured
as a z-score of hits against the implied probability of the odds taken:

    z = (wins - sum(1/odds)) / sqrt(sum(p * (1 - p)))

over settled legs in the trailing WINDOW_DAYS before the run date. Decisions use
only legs dated strictly before the run date.

Hysteresis: a label is blocked when z <= Z_BLOCK with at least MIN_N legs, and
stays blocked until z >= Z_UNBLOCK. With too few legs the previous state is
kept. The state is stepped at most once per run date, so repeated runs on the
same day do not flip decisions.

The settled ledger is the one written by scripts/audit_recent_picks.py earlier
in the same daily run. If that ledger is missing, unreadable, or not for the run
date, the stored state is used unchanged and nothing is written.
"""

from __future__ import annotations

import json
import math
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

WINDOW_DAYS = 30
MIN_N = 60
Z_BLOCK = -2.0
Z_UNBLOCK = 0.0

ROOT = Path(__file__).resolve().parent.parent.parent
LOCALDATA = ROOT / "localdata"
LEDGER_PATH = LOCALDATA / "picks_audit_rolling.json"
STATE_PATH = LOCALDATA / "acca_gate_state.json"


def _label(value: Any) -> str:
    text = str(value or "").strip().upper()
    return text or "UNKNOWN"


def label_stats(rows: Iterable[dict[str, Any]], as_of: str, window_days: int = WINDOW_DAYS) -> dict[str, dict[str, Any]]:
    """Per-label hit, implied and z statistics over the trailing window before as_of."""
    end = date.fromisoformat(as_of)
    start = end - timedelta(days=window_days)
    acc: dict[str, dict[str, float]] = {}
    for row in rows:
        day = str(row.get("date") or "")[:10]
        try:
            d = date.fromisoformat(day)
        except ValueError:
            continue
        if not (start <= d < end):
            continue
        odds = row.get("odds")
        won = row.get("won")
        if won is None or odds is None:
            continue
        try:
            odds = float(odds)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(odds) or odds <= 1.0:
            continue
        p = 1.0 / odds
        slot = acc.setdefault(_label(row.get("price_evidence")), {"n": 0.0, "wins": 0.0, "implied": 0.0, "var": 0.0, "pnl": 0.0})
        slot["n"] += 1
        slot["wins"] += 1.0 if won else 0.0
        slot["implied"] += p
        slot["var"] += p * (1.0 - p)
        slot["pnl"] += (odds - 1.0) if won else -1.0
    out: dict[str, dict[str, Any]] = {}
    for label, s in acc.items():
        n = int(s["n"])
        z = (s["wins"] - s["implied"]) / math.sqrt(s["var"]) if s["var"] > 0 else 0.0
        out[label] = {
            "n": n,
            "hit_rate": round(s["wins"] / n, 4),
            "implied_rate": round(s["implied"] / n, 4),
            "z": round(z, 3),
            "roi": round(s["pnl"] / n, 4),
        }
    return out


def step_blocked(prev_blocked: set[str], stats: dict[str, dict[str, Any]]) -> tuple[set[str], list[str]]:
    """Apply one hysteresis step. Returns the new blocked set and a list of transitions."""
    new_blocked = set(prev_blocked)
    changes: list[str] = []
    for label in sorted(set(prev_blocked) | set(stats)):
        st = stats.get(label)
        if st is None or st["n"] < MIN_N:
            continue
        z = st["z"]
        if label not in new_blocked and z <= Z_BLOCK:
            new_blocked.add(label)
            changes.append(f"BLOCK {label} (n={st['n']}, z={z:+.2f})")
        elif label in new_blocked and z >= Z_UNBLOCK:
            new_blocked.discard(label)
            changes.append(f"UNBLOCK {label} (n={st['n']}, z={z:+.2f})")
    return new_blocked, changes


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("as_of_last", None)
    data.setdefault("blocked", {})
    return data


def _blocked_set(state: dict[str, Any]) -> set[str]:
    return set((state.get("blocked") or {}).keys())


def refresh(
    as_of: str,
    *,
    ledger_path: Path = LEDGER_PATH,
    state_path: Path = STATE_PATH,
    write: bool = True,
) -> tuple[set[str], str]:
    """Return (blocked labels for as_of, one-line status). Steps the state when fresh data allows."""
    state = load_state(state_path)
    if state.get("as_of_last") == as_of:
        return _blocked_set(state), f"already stepped for {as_of}; {len(_blocked_set(state))} blocked"
    try:
        ledger = json.loads(ledger_path.read_text())
    except (OSError, ValueError) as exc:
        return _blocked_set(state), f"ledger unavailable ({type(exc).__name__}); state kept"
    if not isinstance(ledger, dict) or str(ledger.get("end") or "") != as_of:
        return _blocked_set(state), f"ledger end {ledger.get('end') if isinstance(ledger, dict) else None} != {as_of}; state kept"
    rows = ledger.get("settled_ledger") or []
    stats = label_stats(rows, as_of)
    new_blocked, changes = step_blocked(_blocked_set(state), stats)
    prev_blocked = state.get("blocked") or {}
    blocked_state: dict[str, Any] = {}
    for label in sorted(new_blocked):
        keep = prev_blocked.get(label) or {}
        blocked_state[label] = {"since": keep.get("since") or as_of, "z": stats.get(label, {}).get("z", keep.get("z"))}
    state = {
        "as_of_last": as_of,
        "blocked": blocked_state,
        "stats": stats,
        "params": {"window_days": WINDOW_DAYS, "min_n": MIN_N, "z_block": Z_BLOCK, "z_unblock": Z_UNBLOCK},
    }
    if write:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True))
    status = f"stepped for {as_of}; blocked={sorted(new_blocked) or 'none'}"
    if changes:
        status += "; " + "; ".join(changes)
    return new_blocked, status
