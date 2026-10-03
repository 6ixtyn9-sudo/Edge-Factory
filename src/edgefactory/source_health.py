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


FOREBET_LIVE_LAST_DAY = "2026-06-12"

DAILY_SOURCES = (
    "bzzoiro", "bzzoiro_odds", "zulubet", "statarea", "vitibet",
    "scoutingstats", "betclan", "bettingclosed", "prosoccer", "predictz",
    "windrawwin", "freesupertips", "afootballreport", "soccervista",
    "betexplorer", "theoddsapi", "oddspapi_odds", "forebet",
    # Verified shadow-only candidates. They are explicit health rows, but
    # neither enters consensus weights nor the pick path by default.
    "futbolpronosticos", "sportytrader_odds",
    # SHADOW-01 shadow-only candidates (zero voice credit, zero price weight
    # until settled evidence and an explicit operator promotion):
    #   betminer     - RapidAPI voice shadow (odds carry no bookmaker identity)
    #   pinnapi_odds - Pinnacle named-book price shadow (never a vote)
    #   betbetter    - keyless CC BY 4.0 benchmark board (echo-test asset)
    "betminer", "pinnapi_odds", "betbetter", "sharpapi_odds", "boggio",
    # Convergent-tagged from day one - see CONVERGENT_SOURCES below.
    "predictiq",
)

# Convergent sources (SHADOW-01 T5, registry-level tag from day one).
#
# A source whose predictions are derived in part from market odds cannot be
# an independent voice: agreement with our price-corroborated consensus is
# expected by construction, so it earns ZERO voice credit permanently and
# NEVER corroborates a price. PredictIQ's ensemble includes devigged market
# odds (ECHO-MED-HIGH, docs/operator/SOURCE-HUNT-2026-10.md section 5.5).
# The tag is enforced fail-closed in build_daily_source_health: even if a
# future adapter reports can_vote/can_price observations, the registry
# refuses them. Fetching may be allowed later for echo testing only.
CONVERGENT_SOURCES: frozenset[str] = frozenset({"predictiq"})


def _freshness_value(observation: dict[str, Any]) -> float | None:
    value = observation.get("freshness_h")
    if value is None:
        return None
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


def build_daily_source_health(
    day: str,
    observations: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the hard per-source daily contract from explicit observations.

    Missing observations are conservative: unavailable for today's production
    use, with a blocker. This prevents an absent health measurement from being
    mistaken for a healthy source.
    """
    observations = observations or {}
    sources: dict[str, dict[str, Any]] = {}
    for name in DAILY_SOURCES:
        obs = dict(observations.get(name) or {})
        if name == "forebet" and str(day)[:10] > FOREBET_LIVE_LAST_DAY:
            sources[name] = {
                "can_fetch_today": False,
                "can_price": False,
                "can_vote": False,
                "freshness_h": None,
                "blocker": "historical-only post-2026-06-12; no production pricing or weighting",
            }
            continue
        fetched = bool(obs.get("fetched", False))
        rows = int(obs.get("rows") or 0)
        can_fetch = bool(obs.get("can_fetch_today", fetched))
        # Price/vote capability is source-specific; never infer either from a
        # non-empty response. Adapters must make those claims explicitly.
        can_price = bool(obs.get("can_price", False))
        can_vote = bool(obs.get("can_vote", False))
        blocker = obs.get("blocker")
        if name in CONVERGENT_SOURCES:
            # Registry-level convergent tag: zero voice credit permanently,
            # never a corroborator - enforced here, not left to the adapter.
            can_price = False
            can_vote = False
            blocker = (
                "convergent echo-candidate: zero voice credit permanently, "
                "never corroborates (SOURCE-HUNT-2026-10 section 5.5)"
            )
        if not blocker and not can_fetch:
            blocker = "not reliably fetched/observed today"
        elif not blocker and rows == 0:
            blocker = "fetch returned zero rows"
        row = {
            "can_fetch_today": can_fetch,
            "can_price": can_price,
            "can_vote": can_vote,
            "freshness_h": _freshness_value(obs),
            "blocker": str(blocker) if blocker else None,
            # Deterministic adapter reason (e.g. http_404_endpoint_contract).
            # Reasons are generated from status codes only - never from a URL,
            # a header or a payload - so they can never carry a credential.
            "reason": str(obs.get("reason")) if obs.get("reason") else None,
            "status": str(obs.get("status")) if obs.get("status") else None,
        }
        # Candidate-specific counters are deliberately retained in the daily
        # contract so an operator can distinguish an empty slate from a parser
        # mismatch without treating either as a production gate.
        if name == "futbolpronosticos":
            row.update({
                "raw": int(obs.get("raw") or 0),
                "scored": int(obs.get("scored") or 0),
            })
        elif name == "sportytrader_odds":
            row.update({
                "st_raw": int(obs.get("st_raw") or 0),
                "st_matched": int(obs.get("st_matched") or 0),
            })
        elif name == "theoddsapi":
            row.update({
                "oa_raw": int(obs.get("oa_raw") or 0),
                "oa_usable": int(obs.get("oa_usable") or 0),
                "oa_matched": int(obs.get("oa_matched") or 0),
            })
        elif name == "betminer":
            row.update({
                "bm_raw": int(obs.get("bm_raw") or 0),
                "bm_scored": int(obs.get("bm_scored") or 0),
                "bm_matched": int(obs.get("bm_matched") or 0),
            })
        elif name == "pinnapi_odds":
            row.update({
                "pa_raw": int(obs.get("pa_raw") or 0),
                "pa_scored": int(obs.get("pa_scored") or obs.get("pa_matched") or 0),
                "pa_matched": int(obs.get("pa_matched") or 0),
            })
        elif name == "sharpapi_odds":
            row.update({
                "sa_raw": int(obs.get("sa_raw") or 0),
                "sa_scored": int(obs.get("sa_scored") or obs.get("sa_matched") or 0),
                "sa_matched": int(obs.get("sa_matched") or 0),
            })
        elif name == "boggio":
            row.update({
                "bg_raw": int(obs.get("bg_raw") or 0),
                "bg_scored": int(obs.get("bg_scored") or 0),
                "bg_matched": int(obs.get("bg_matched") or 0),
            })
        elif name == "betbetter":
            row.update({
                "bb_raw": int(obs.get("bb_raw") or 0),
                "bb_scored": int(obs.get("bb_scored") or 0),
                "bb_matched": int(obs.get("bb_matched") or 0),
            })
        sources[name] = row
    return {"schema": 1, "date": str(day), "sources": sources}


def persist_daily_source_health(
    day: str,
    observations: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Persist ``source_health_YYYY-MM-DD.json`` atomically and return it."""
    payload = build_daily_source_health(day, observations)
    path = LOCALDATA / f"source_health_{str(day)[:10]}.json"
    LOCALDATA.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    return payload


# Role verdicts for the compact health line (SHADOW-01 T0).
#
# The old all-of(fetch, price, vote) check could never pass for role-limited
# sources: bzzoiro is a tips/vote feed that never prices, while bzzoiro_odds
# and betexplorer are price feeds that never vote. They printed a constant
# misleading BLOCKED. A source is healthy on the health line when fetch AND
# every capability key of *its own role* hold; sources not listed here keep
# the full three-key contract.
ROLE_VERDICT_SOURCES: dict[str, tuple[str, ...]] = {
    "bzzoiro": ("can_vote",),
    "bzzoiro_odds": ("can_price",),
    "betexplorer": ("can_price",),
    "theoddsapi": ("can_price",),
    "scoutingstats": ("can_price", "can_vote"),
}


def _status_token(name: str, row: dict[str, Any]) -> str:
    if name in CONVERGENT_SOURCES:
        return f"{name}=echo/only"
    roles = ROLE_VERDICT_SOURCES.get(name, ("can_price", "can_vote"))
    healthy = bool(row.get("can_fetch_today")) and all(row.get(k) for k in roles)
    label = "fetch/" + "/".join(role.removeprefix("can_") for role in roles)
    return f"{name}={label if healthy else 'BLOCKED'}"


#: Price role of each promoted source, printed so the health line can never
#: imply that every source returning a number is a bookmaker source.
SOURCE_ROLE_LABELS: dict[str, str] = {
    "bzzoiro_odds": "named-book price source",
    "betexplorer": "named-book price source",
    "theoddsapi": "named-book price source",
    "oddspapi_odds": "named-book price source",
    "pinnapi_odds": "named-book price source",
    "sharpapi_odds": "named-book price source",
    "boggio": "average-bookmaker price donor",
    "betbetter": "fair-price donor",
    "betminer": "prediction vote donor / conditional provider-price donor",
    "scoutingstats": "audit-only price source",
}

#: Deterministic reason suffix attached to a HEALTHY promoted donor, so an
#: operator can see at a glance WHAT KIND of rows the source contributed.
_HEALTHY_ROLE_REASON: dict[str, str] = {
    "boggio": "average_price_donor",
    "betbetter": "fair_price_donor",
}


def _zero_reason(row: dict[str, Any], raw: int) -> str:
    """Compact deterministic reason for shadow/donor observations.

    Non-zero rows now also carry a reason for the promoted donors
    (``[reason=average_price_donor]``), because "20 rows" alone does not say
    whether those rows were bookmaker prices, average prices or fair prices.
    A reason never contains a key, a header or a URL.
    """
    name = str(row.get("_source_name") or "")
    if raw:
        role_reason = _HEALTHY_ROLE_REASON.get(name)
        return f"[reason={role_reason}]" if role_reason else ""
    explicit = str(row.get("reason") or "")
    if explicit:
        return f"[reason={explicit}]"
    status = str(row.get("status") or "")
    if status in {"not_run", "cache_only", "ok", "empty"}:
        return ""
    blocker = str(row.get("blocker") or "")
    import re
    code = re.search(r"HTTP\s+(\d{3})", blocker)
    if code:
        return f"({('auth' if code.group(1) in {'401', '403'} else 'http')}{code.group(1)})"
    if status in {"auth", "quota", "cooldown"}:
        return f"({status})"
    return "(unavailable)"


def source_role_lines(day: str) -> list[str]:
    """Deterministic ``name: health + role`` lines for the operator log."""
    path = LOCALDATA / f"source_health_{str(day)[:10]}.json"
    try:
        sources = json.loads(path.read_text()).get("sources", {})
    except (OSError, ValueError, TypeError):
        sources = {}
    out: list[str] = []
    for name, role in SOURCE_ROLE_LABELS.items():
        row = sources.get(name)
        if row is None:
            continue
        # A time-qualified cache is price-available but not a same-stage
        # network fetch.  Keep that distinction in the receipt/status field
        # without falsely calling a usable cached named-book board unavailable.
        healthy = bool(row.get("can_price")) and (
            bool(row.get("can_fetch_today")) or str(row.get("status") or "") == "cache_only"
        )
        out.append(f"{name}: {'healthy' if healthy else 'unavailable'} {role}")
    return out


def daily_status_block(day: str) -> str:
    """One compact, deterministic status line for the card/run log."""
    path = LOCALDATA / f"source_health_{str(day)[:10]}.json"
    try:
        payload = json.loads(path.read_text())
        sources = payload.get("sources", {})
    except (OSError, ValueError, TypeError):
        return f"Source health {day}: unavailable (health contract not persisted)"
    tokens = []
    for name in (
        "bzzoiro", "bzzoiro_odds", "scoutingstats", "betexplorer", "theoddsapi", "forebet",
        "futbolpronosticos", "sportytrader_odds",
        "betminer", "pinnapi_odds", "betbetter", "sharpapi_odds", "boggio", "predictiq",
    ):
        row = sources.get(name, {})
        if name == "futbolpronosticos":
            tokens.append(f"futbolpronosticos=raw{row.get('raw', 0)}/scored{row.get('scored', 0)}")
            continue
        if name == "sportytrader_odds":
            tokens.append(f"sportytrader=st_raw{row.get('st_raw', 0)}/st_matched{row.get('st_matched', 0)}")
            continue
        if name == "theoddsapi":
            tokens.append(
                f"theoddsapi=raw{row.get('oa_raw', 0)}/usable{row.get('oa_usable', 0)}"
                f"/matched{row.get('oa_matched', 0)}"
            )
            continue
        if name == "betminer":
            tokens.append(f"betminer=bm_raw{row.get('bm_raw', 0)}/bm_scored{row.get('bm_scored', 0)}{_zero_reason({**row, '_source_name': 'betminer'}, int(row.get('bm_raw') or 0))}/bm_matched{row.get('bm_matched', 0)}")
            continue
        if name == "pinnapi_odds":
            reason = _zero_reason({**row, '_source_name': 'pinnapi_odds'}, int(row.get('pa_raw') or 0))
            tokens.append(
                f"pinnapi=pa_raw{row.get('pa_raw', 0)}/pa_matched{row.get('pa_matched', 0)}"
                f"{reason}/pa_scored{row.get('pa_scored', 0)}"
            )
            continue
        if name == "betbetter":
            tokens.append(f"betbetter=bb_raw{row.get('bb_raw', 0)}/bb_scored{row.get('bb_scored', 0)}{_zero_reason({**row, '_source_name': 'betbetter'}, int(row.get('bb_raw') or 0))}/bb_matched{row.get('bb_matched', 0)}")
            continue
        if name == "sharpapi_odds":
            tokens.append(f"sharpapi=sa_raw{row.get('sa_raw', 0)}/sa_matched{row.get('sa_matched', 0)}{_zero_reason({**row, '_source_name': 'sharpapi_odds'}, int(row.get('sa_raw') or 0))}/sa_scored{row.get('sa_scored', 0)}")
            continue
        if name == "boggio":
            tokens.append(f"boggio=bg_raw{row.get('bg_raw', 0)}/bg_scored{row.get('bg_scored', 0)}{_zero_reason({**row, '_source_name': 'boggio'}, int(row.get('bg_raw') or 0))}/bg_matched{row.get('bg_matched', 0)}")
            continue
        if name == "forebet":
            tokens.append(
                "forebet=historical-only"
                if "historical-only" in str(row.get("blocker") or "")
                else "forebet=available"
            )
            continue
        tokens.append(_status_token(name, row))
    return f"Source health {day}: " + " ".join(tokens)


def bzzoiro_status_line() -> str | None:
    record = load_state().get("sources", {}).get("bzzoiro", {})
    try:
        streak = int(record.get("zero_run_streak") or 0)
    except (TypeError, ValueError):
        streak = 0
    if streak >= 3:
        return f"bzz UNAVAILABLE — {streak} consecutive all-zero runs (visibility only; no gate change)"
    return None
