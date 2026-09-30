"""Which lane is allowed to act as production.

Two lanes can generate picks:

``legacy_baseline``
    The original engine. Its feature vector is derived from a source universe
    that no longer produces same-day rows, so its output is retained for
    comparison and historical continuity.

``fresh_production``
    Rebuilt on the current source universe, walk-forward certified on its own
    evidence, with its own model health and its own dispatch gates.

Only ONE of them may be production at a time. "Production" means: the rows
that get upserted to the warehouse and the picks that get notified. This
module is the single place that decides, so no caller can quietly route the
other lane's picks into production.

The critical property is **no silent fallback**. When ``fresh_production`` is
the production lane and it produces zero dispatchable picks, production
publishes an explicit empty slate. It must never backfill from
``legacy_baseline``, because "the other lane had something" is not evidence
that today's fresh evidence supported a bet.

Selection is via ``EDGE_FACTORY_PRODUCTION_LANE``; the default is
``fresh_production``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

LANE_FRESH_PRODUCTION = "fresh_production"
LANE_LEGACY_BASELINE = "legacy_baseline"
VALID_LANES = (LANE_FRESH_PRODUCTION, LANE_LEGACY_BASELINE)

DEFAULT_LANE = LANE_FRESH_PRODUCTION
ENV_VAR = "EDGE_FACTORY_PRODUCTION_LANE"


def active_lane(env: dict[str, str] | None = None) -> str:
    """The lane currently allowed to publish production picks.

    An unrecognised value falls back to the default rather than raising: a
    typo in a workflow variable must not take the pipeline down, and the
    default is the safer, evidence-gated lane.
    """
    source = os.environ if env is None else env
    value = str(source.get(ENV_VAR, "") or "").strip().lower()
    return value if value in VALID_LANES else DEFAULT_LANE


def fresh_production_is_active(env: dict[str, str] | None = None) -> bool:
    return active_lane(env) == LANE_FRESH_PRODUCTION


def legacy_dispatch_allowed(env: dict[str, str] | None = None) -> bool:
    """True only when ``legacy_baseline`` may sync/notify as production."""
    return active_lane(env) == LANE_LEGACY_BASELINE


def production_edges_path(target_date: str, localdata: Path) -> Path:
    """The certified-rule registry the production edge sync must publish.

    In ``fresh_production`` mode this is the fresh lane's own registry. The
    legacy ``edges_consensus.json`` describes rules certified against a source
    universe that no longer produces same-day rows, so publishing it as
    production-active would tell a dashboard that retired rules are live.
    """
    localdata = Path(localdata)
    if fresh_production_is_active():
        dated = localdata / f"fresh_production_certified_edges_{target_date}.json"
        return dated if dated.exists() else (
            localdata / "fresh_production_certified_edges.json")
    return localdata / "edges_consensus.json"


def horizon_picks_path(target_date: str, localdata: Path) -> Path:
    return Path(localdata) / f"fresh_production_horizon_picks_{target_date}.json"


def comparison_only_files(target_date: str, localdata: Path) -> list[str]:
    """Artifacts that exist for comparison and must never drive production."""
    localdata = Path(localdata)
    if not fresh_production_is_active():
        return []
    names = [
        f"picks_{target_date}.json",
        f"picks_morning_{target_date}.json",
        "picks_today.json",
        "edges_consensus.json",
        "picks_next_2days.json",
        "picks_next_3days.json",
    ]
    return [str(localdata / name) for name in names]


def production_picks_path(target_date: str, localdata: Path) -> Path:
    """The file the production sync/notify step must read for ``target_date``."""
    if fresh_production_is_active():
        return Path(localdata) / f"fresh_production_production_picks_{target_date}.json"
    return Path(localdata) / f"picks_{target_date}.json"


def ensure_production_picks_file(target_date: str, localdata: Path) -> Path:
    """Return the production picks path, creating an explicit empty slate.

    If ``fresh_production`` is active but its run did not write a hand-off
    file (for example the step failed), an empty list is written. That is
    deliberate: a missing file could be mistaken for "use the other lane",
    while ``[]`` states plainly that the production lane published nothing.
    """
    path = production_picks_path(target_date, localdata)
    if fresh_production_is_active() and not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]")
    return path


def load_production_picks(target_date: str, localdata: Path) -> list[dict]:
    path = production_picks_path(target_date, localdata)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return payload if isinstance(payload, list) else []


def production_payload(target_date: str, localdata: Path, *,
                       horizon_days: int = 0) -> dict:
    """The one description of production every downstream consumer must read.

    Nothing downstream should hardcode a pick file. They ask here, so that
    switching lanes switches every consumer at once and no component can
    quietly keep reading the other lane's output.
    """
    lane = active_lane()
    rows = load_production_picks(target_date, localdata)
    return {
        "production_lane": lane,
        "production_pick_file": str(production_picks_path(target_date, localdata)),
        "production_edge_file": str(production_edges_path(target_date, localdata)),
        "production_pick_count": len(rows),
        "production_date": target_date,
        "production_horizon": horizon_days,
        "comparison_only_files": comparison_only_files(target_date, localdata),
        "legacy_dispatch_allowed": legacy_dispatch_allowed(),
        "fallback_to_other_lane": False,
    }


def describe(target_date: str, localdata: Path) -> dict:
    """Auditable snapshot of the lane decision, for logs and artifacts."""
    payload = production_payload(target_date, localdata)
    payload["production_picks_file"] = payload["production_pick_file"]
    payload["note"] = (
        "legacy_baseline reports still run for comparison; they are not "
        "synced, notified, ticketed, CLV-captured or published as production "
        "while fresh_production is active."
    ) if payload["production_lane"] == LANE_FRESH_PRODUCTION else (
        "legacy_baseline is the active production lane."
    )
    return payload
