"""Engine-aware debias for 🔥 note probabilities (Addendum 19).

The pre-Addendum-19 loader damped every market by the tiny recommendation
overlay (``enhancements_audit.by_enhancement``, gate recommended>=5, n<=9).
This module reads the full-surface ``event_notes_audit.by_market`` (min-n gate)
plus the per-engine x per-market cells (``by_engine_by_market``) and resolves a
damp factor per (market, engine):

- ``hybrid_cohort`` notes are already cohort-shrunk; they are only damped when
  their own cell is provably worse than the ``model`` cell on the same market
  (|delta_hybrid| > |delta_model|), else gated at hr=1.0 (no double-damping).
- ``model`` / ``legacy`` notes use their own cell when it has enough evidence,
  else the pooled ``by_market`` cell, else 1.0 (never damp without evidence).
- A damp never exceeds 1.0 (realized >= promised is under-promising, which is
  not a reason to damp).

Audit-only: this module reads the rolling audit JSON and resolves numbers. It
has no side effects and no policy of its own — the caller decides when to use
it (see ``EDGE_FACTORY_ENGINE_AWARE_DEBIAS``).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ENV_FLAG = "EDGE_FACTORY_ENGINE_AWARE_DEBIAS"
MIN_MARKET_N = 15   # full-surface by_market evidence gate (Addendum 19)
MIN_ENGINE_N = 20   # per-engine x per-market cell evidence gate (was 5 — n=5..9
                    # cells are noise; a 6/6 btts_yes cell produced degenerate
                    # damps. Raised 2026-08-10 after data check: gate 20 keeps
                    # only hybrid 6 + legacy 4 cells; the rest fall back to the
                    # pooled by_market cell — the safe path.)


def _damp(slot: dict) -> float:
    """Damp factor for one calibration slot: realized/promised, capped at 1.0.

    Never boosts (under-promising markets stay 1.0), never negative, and any
    missing/zero promised value resolves to 1.0 (no evidence -> no damp).
    """
    realized = slot.get("realized")
    promised = slot.get("mean_promised")
    if realized is None or promised is None or promised <= 0:
        return 1.0
    return max(0.0, min(1.0, float(realized) / float(promised)))


def _abs_delta(slot: dict) -> float:
    """|realized - promised| for the hybrid-vs-model gate; inf when missing."""
    realized = slot.get("realized")
    promised = slot.get("mean_promised")
    if realized is None or promised is None:
        return math.inf
    return abs(float(realized) - float(promised))


def load_engine_aware_debias_map(audit_path: Path) -> dict[str, dict]:
    """Build {market: {"pooled": float|None, "engines": {engine: {"hr", "abs_delta"}}}}.

    Reads ONLY ``event_notes_audit.by_market`` and
    ``event_notes_audit.by_engine_by_market``. Returns {} on any missing,
    corrupt, or empty input (callers then resolve to 1.0 — safe default).
    """
    try:
        if not audit_path.exists():
            return {}
        data = json.loads(audit_path.read_text())
        notes = data.get("event_notes_audit", {})
        by_market = notes.get("by_market", {})
        by_engine_by_market = notes.get("by_engine_by_market", {})
    except Exception:
        return {}

    out: dict[str, dict] = {}
    for market, slot in by_market.items():
        if not isinstance(slot, dict) or int(slot.get("n", 0)) < MIN_MARKET_N:
            continue
        entry: dict[str, object] = {"pooled": _damp(slot), "engines": {}}
        for engine, cells in by_engine_by_market.items():
            cell = cells.get(market) if isinstance(cells, dict) else None
            if isinstance(cell, dict) and int(cell.get("n", 0)) >= MIN_ENGINE_N:
                entry["engines"][engine] = {
                    "hr": _damp(cell),
                    "abs_delta": _abs_delta(cell),
                }
        out[market] = entry
    return out


def resolve_debias_hr(market: str, engine: str, debias_map: dict) -> float:
    """Resolve the damp factor for one note.

    Rules (pinned in the module docstring):
    - market absent from the map (insufficient full-surface evidence) -> 1.0;
    - hybrid_cohort: gated at 1.0 unless its own cell is worse than the model
      cell on the same market (|delta_hybrid| > |delta_model|), or there is no
      model cell to compare against (no double-damping without proof);
    - model/legacy: own cell when present, else the pooled cell.
    """
    entry = debias_map.get(market)
    if not entry:
        return 1.0
    engines = entry.get("engines", {})
    if engine == "hybrid_cohort":
        hy = engines.get("hybrid_cohort")
        if hy is None:
            return 1.0
        model = engines.get("model")
        if model is None or hy["abs_delta"] <= model["abs_delta"]:
            return 1.0
        return float(hy["hr"])
    cell = engines.get(engine)
    if cell is not None:
        return float(cell["hr"])
    pooled = entry.get("pooled")
    return float(pooled) if pooled is not None else 1.0
