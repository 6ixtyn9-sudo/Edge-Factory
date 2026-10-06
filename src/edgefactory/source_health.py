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


def _int_or_zero(value: object) -> int:
    """Coerce a reported counter to a non-negative int; never raise."""
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


PINNAPI_CONTRACT_FIELDS = (
    "sport_id", "event_type", "auth_mechanism", "auth_attempts",
    "zero_row_kind", "response_shape",
)


def pinnapi_contract_observation(stats: dict[str, Any]) -> dict[str, Any]:
    """Lift the request-contract discriminators out of the adapter stats.

    The caller builds the health observation by hand, field by field, so a
    field the adapter records is NOT in the health row unless it is named
    here. That is how the 2026-10-06 run lost the answer: the adapter wrote
    which auth mechanism replied, and nothing carried it across. Keeping the
    list in one place means the passthrough and the row agree by
    construction rather than by someone remembering both ends.
    """
    stats = stats or {}
    return {k: stats.get(k) for k in PINNAPI_CONTRACT_FIELDS}


SHARPAPI_BOARD_FIELDS = (
    "board_rows", "board_fixtures", "board_league_count", "board_leagues",
    "board_non_prematch_rows", "board_priced_rows", "board_truncated",
    "requested_limit", "league_filter_requested", "league_filter_effective",
)


def sharpapi_board_observation(stats: dict[str, Any]) -> dict[str, Any]:
    """Lift the board-shape context out of the adapter stats.

    Same hand-built-observation hazard as the pinnapi passthrough above, and
    the same remedy: one list, named in one place, so the adapter and the
    committed row cannot drift apart.

    This context is what makes a zero readable. Without it a page that
    filled with in-play games before reaching our fixtures, a competition
    filter the server ignored, and a genuinely empty slate are the same
    bare zero with three opposite remedies. The configured filter VALUE is
    deliberately not among these fields - it arrives from a deployment
    secret, and this row is committed.
    """
    stats = stats or {}
    return {k: stats.get(k) for k in SHARPAPI_BOARD_FIELDS}


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
            # Rows the adapter fetched and then discarded while parsing.
            # Several adapters already counted this and wrote it only into a
            # per-source ledger nobody opens, so a source could discard every
            # row it fetched and still print a bare zero -- indistinguishable
            # from a provider with nothing on. Carried for every source.
            "canonicalization_dropped": _int_or_zero(
                obs.get("canonicalization_dropped")),
        }
        # Candidate-specific counters are deliberately retained in the daily
        # contract so an operator can distinguish an empty slate from a parser
        # mismatch without treating either as a production gate.
        if name == "betexplorer":
            row.update({
                "be_raw": int(obs.get("be_raw") or 0),
                "be_usable": int(obs.get("be_usable") or 0),
                "be_matched": int(obs.get("be_matched") or 0),
            })
        elif name == "futbolpronosticos":
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
        elif name == "oddspapi_odds":
            row.update({
                "op_raw": int(obs.get("op_raw") or 0),
                "op_usable": int(obs.get("op_usable") or 0),
                "op_matched": int(obs.get("op_matched") or 0),
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
            # The request-contract discriminators. These decide what a zero
            # MEANS - which auth mechanism answered, and which kind of zero
            # it was - and until now they existed only in the per-date
            # shadow ledger, which .gitignore excludes. The 2026-10-06 run
            # proved the cost: the vendor answered, and the answer did not
            # survive the run. Small, scrubbed fields only; never the key.
            shape = obs.get("response_shape") or {}
            row.update({
                "sport_id": obs.get("sport_id"),
                "event_type": obs.get("event_type"),
                "auth_mechanism": obs.get("auth_mechanism"),
                "auth_attempts": [
                    {"auth": a.get("auth"), "status": a.get("status")}
                    for a in (obs.get("auth_attempts") or [])
                    if isinstance(a, dict)
                ],
                "zero_row_kind": obs.get("zero_row_kind"),
                "response_shape_summary": {
                    k: shape.get(k) for k in
                    ("event_count", "events_with_teams", "events_with_markets",
                     "envelope_found", "events_key", "markets_type",
                     "error_blames_credential")
                    if shape.get(k) is not None
                } or None,
            })
        elif name == "sharpapi_odds":
            row.update({
                "sa_raw": int(obs.get("sa_raw") or 0),
                "sa_scored": int(obs.get("sa_scored") or obs.get("sa_matched") or 0),
                "sa_matched": int(obs.get("sa_matched") or 0),
            })
            # Board context, so a zero says which zero it was. Counts and
            # vendor-supplied competition names only; never the configured
            # filter value and never a payload sample.
            board = {k: obs.get(k) for k in SHARPAPI_BOARD_FIELDS
                     if obs.get(k) is not None}
            if board:
                row["board_summary"] = board
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
        if obs.get("join_miss_counts") is not None:
            # Fixed reason vocabulary plus invalid_price; values are counts
            # only, so the receipt cannot retain provider payloads or secrets.
            allowed = {
                "date_mismatch", "out_of_window", "fixture_key_miss",
                "market_unmapped", "market_unsupported",
                "selection_unmapped", "selection_unsupported",
                "no_pick_for_fixture", "timestamp_rejected", "invalid_price",
                "fixture_identity_missing",
            }
            row["join_miss_counts"] = {
                str(reason): int(count or 0)
                for reason, count in dict(obs.get("join_miss_counts") or {}).items()
                if str(reason) in allowed
            }
            row["join_matched_rows"] = int(obs.get("join_matched_rows") or 0)
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
    "oddspapi_odds": ("can_price",),
    "scoutingstats": ("can_price", "can_vote"),
}


# Reason tokens must state what was OBSERVED, never infer a cause the
# evidence cannot carry. A label that asserts a cause sends the operator to
# fix the wrong thing, and -- worse -- stops them looking at the right one.
REASON_HTTP_401_AUTH = "http_401_auth"
# 403 means "refused", not "bad key". A live credential hitting an endpoint
# outside its plan returns the same code as a dead one.
REASON_HTTP_403_PLAN_OR_AUTH = "http_403_plan_or_auth"
# Replaces the former "valid empty" token, which asserted the provider
# genuinely had nothing. All that is actually observed is: it answered, and
# no rows survived parsing. Those are different claims with opposite fixes.
REASON_HTTP_200_ZERO_ROWS = "http_200_zero_rows_after_parse"
# A source that was rate-limited must say so on its own health line rather
# than printing a bare zero.
REASON_HTTP_429_QUOTA = "http_429_quota"


def zero_row_reason(
    status: object,
    http_statuses: object = (),
    quota_hint: object = None,
) -> str | None:
    """Deterministic zero-row reason token for a credential-blocked source.

    Operator-facing triage only: the token names the transport outcome, never
    a key, a header, a URL or any part of a payload.

    * ``http_401_auth`` - the credential was rejected outright.
    * ``http_403_plan_or_auth`` - 403 is ambiguous and must stay ambiguous
      here. It is returned both for a dead credential AND for a live
      credential calling an endpoint its plan does not include. Bzzoiro
      demonstrated the second case: the same token returned best_results=12
      on a sibling call in the same run while the comparison endpoint 403'd.
      Reporting that as plain "auth" sends the operator to rotate a key that
      is already fine.
    * ``credential_rejected_auth`` - auth failure with no observed code.
    * ``http_200_zero_rows_after_parse`` - authenticated, answered, and
      nothing survived parsing. States the OBSERVATION only. The previous
      "valid empty" token asserted a CAUSE - that the provider legitimately
      had nothing - which this evidence cannot support and which was wrong
      for Pinnacle for days while its parser discarded every row. A
      zero-row 200 and a genuinely empty slate are the same transport
      outcome and opposite faults.
    * ``http_429_quota`` / ``quota_exhausted`` - rate/plan limit.
    """
    state = str(status or "").strip().lower()
    codes = [int(code) for code in (http_statuses or []) if str(code).isdigit()]
    if state == "auth":
        # 401 is unambiguous: the credential was rejected. 403 is not, and the
        # label must not pretend otherwise - see the docstring.
        if 401 in codes:
            return REASON_HTTP_401_AUTH
        if 403 in codes:
            return REASON_HTTP_403_PLAN_OR_AUTH
        return "credential_rejected_auth"
    if state == "quota":
        return "http_429_quota" if 429 in codes else "quota_exhausted"
    if state == "cooldown":
        return "cooldown_after_429"
    if state == "empty":
        return REASON_HTTP_200_ZERO_ROWS if (200 in codes or not codes) else "empty_response"
    if state == "not_run":
        return "credential_absent_not_run"
    if state == "unavailable":
        for code in codes:
            if code >= 400:
                return f"http_{code}_unavailable"
        hint = str(quota_hint or "").strip().lower()
        return f"unavailable_{hint}" if hint and hint not in {"none", "none_observed"} else "unavailable"
    return None


def _status_token(name: str, row: dict[str, Any]) -> str:
    if name in CONVERGENT_SOURCES:
        return f"{name}=echo/only"
    roles = ROLE_VERDICT_SOURCES.get(name, ("can_price", "can_vote"))
    healthy = bool(row.get("can_fetch_today")) and all(row.get(k) for k in roles)
    label = "fetch/" + "/".join(role.removeprefix("can_") for role in roles)
    if healthy:
        return f"{name}={label}"
    # A bare "BLOCKED" does not tell an operator whether to check the key,
    # the plan or the endpoint. Attach the deterministic reason when one is
    # known; never guess one.
    reason = str(row.get("reason") or "")
    return f"{name}=BLOCKED" + (f"[reason={reason}]" if reason else "")


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


def _dropped_token(row: dict[str, Any]) -> str:
    """``/dropped<N>`` when rows were discarded during parsing, else "".

    Several adapters already counted their own discards and wrote the number
    into a per-source ledger nobody opens. Pinnacle was discarding every row
    it fetched for days while its health line printed a bare zero, which is
    indistinguishable from a provider with nothing on. Surfacing the count
    where the operator actually looks is the whole point: a source that
    fetched plenty and kept none is a parser fault, not a quiet slate.
    """
    try:
        dropped = int(row.get("canonicalization_dropped") or 0)
    except (TypeError, ValueError):
        return ""
    return f"/dropped{dropped}" if dropped > 0 else ""


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
        "bzzoiro", "bzzoiro_odds", "scoutingstats", "betexplorer", "theoddsapi", "oddspapi_odds", "forebet",
        "futbolpronosticos", "sportytrader_odds",
        "betminer", "pinnapi_odds", "betbetter", "sharpapi_odds", "boggio", "predictiq",
    ):
        row = sources.get(name, {})
        if name == "betexplorer" and str(row.get("status") or "") == "cache_only":
            tokens.append(
                f"betexplorer=raw{row.get('be_raw', 0)}/usable{row.get('be_usable', 0)}"
                f"/matched{row.get('be_matched', 0)}"
            )
            continue
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
        if name == "oddspapi_odds":
            # oddspapi printed a bare "raw0" through four days of hard 429s
            # with no reason attached, which is why nobody looked at it.
            reason = _zero_reason({**row, '_source_name': 'oddspapi_odds'},
                                  int(row.get('op_raw') or 0))
            tokens.append(
                f"oddspapi=raw{row.get('op_raw', 0)}/usable{row.get('op_usable', 0)}"
                f"{reason}{_dropped_token(row)}/matched{row.get('op_matched', 0)}"
            )
            continue
        if name == "betminer":
            tokens.append(f"betminer=bm_raw{row.get('bm_raw', 0)}/bm_scored{row.get('bm_scored', 0)}{_zero_reason({**row, '_source_name': 'betminer'}, int(row.get('bm_raw') or 0))}{_dropped_token(row)}/bm_matched{row.get('bm_matched', 0)}")
            continue
        if name == "pinnapi_odds":
            reason = _zero_reason({**row, '_source_name': 'pinnapi_odds'}, int(row.get('pa_raw') or 0))
            tokens.append(
                f"pinnapi=pa_raw{row.get('pa_raw', 0)}/pa_matched{row.get('pa_matched', 0)}"
                f"{reason}{_dropped_token(row)}/pa_scored{row.get('pa_scored', 0)}"
            )
            continue
        if name == "betbetter":
            tokens.append(f"betbetter=bb_raw{row.get('bb_raw', 0)}/bb_scored{row.get('bb_scored', 0)}{_zero_reason({**row, '_source_name': 'betbetter'}, int(row.get('bb_raw') or 0))}{_dropped_token(row)}/bb_matched{row.get('bb_matched', 0)}")
            continue
        if name == "sharpapi_odds":
            tokens.append(f"sharpapi=sa_raw{row.get('sa_raw', 0)}/sa_matched{row.get('sa_matched', 0)}{_zero_reason({**row, '_source_name': 'sharpapi_odds'}, int(row.get('sa_raw') or 0))}{_dropped_token(row)}/sa_scored{row.get('sa_scored', 0)}")
            continue
        if name == "boggio":
            tokens.append(f"boggio=bg_raw{row.get('bg_raw', 0)}/bg_scored{row.get('bg_scored', 0)}{_zero_reason({**row, '_source_name': 'boggio'}, int(row.get('bg_raw') or 0))}{_dropped_token(row)}/bg_matched{row.get('bg_matched', 0)}")
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
