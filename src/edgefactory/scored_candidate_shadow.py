"""Absolute scored-candidate shadow grading ledger (AUDIT-ONLY).

Purpose: answer "were scored-but-dropped candidates genuinely bad inventory,
or bread left on the table?" from persisted state instead of human-readable
logs.  Every scored candidate gets a durable append-only JSONL record BEFORE
final pick/ticket selection, final selected/rejected status is appended after
selection, and a read-only report settles the ledger against existing result
facts.

Hard doctrine (mirrors the standing repo rules):

* OBSERVABILITY ONLY.  Nothing in this module may change ticket selection,
  staking, acca construction, odds floors, veto bands, ladder logic, source
  eligibility, kickoff guards, freeze behaviour, matching or any customer
  output.  Callers invoke the ``record_*`` entry points, which swallow every
  exception and report the audit failure on stderr; a ledger write failure
  must never alter betting behaviour.
* APPEND-ONLY.  Historical events are never rewritten; settlement is a
  read-time join (or an explicit, separate settlement event file).
* EXACT MATCHING ONLY for settlement: ``(date, norm_team(home),
  norm_team(away))`` exact lookups, no fuzzy matching, no alias scan, no
  reschedule window.  A candidate that cannot be matched safely stays
  ``pending``/``unmatched`` — never a loss.
* PRICE HONESTY.  The shadow ROI price is the price captured at decision
  time.  A candidate is "execution-safe" only when that price came from a
  currently registered, execution-eligible, NAMED-BOOK source, was not
  quarantined, was push-eligible, and is provably pre-kickoff.  Fair/model
  prices (Bet Better), average donor prices (Boggio) and unregistered or
  post-kickoff prices are recorded but excluded from execution-safe ROI.

Ledger files (gitignored with the rest of ``localdata/``; never commit):

    localdata/scored_candidate_shadow_YYYY-MM-DD.jsonl
    localdata/scored_candidate_shadow_settlement_YYYY-MM-DD.jsonl  (optional,
        written only by the report CLI's explicit --write-settlement flag)

Event types in the main file: ``scored_candidate``, ``candidate_status``,
``run_summary``.  Candidate events are routed to the file of their OWN
trading date so a status appended by the ticket builder always lands next to
the scored event it describes.

"scored=" reconciliation (one honest definition, documented):  the pipeline
log line ``coverage: scored=N picks=M`` in scripts/picks_today.py uses
``ml_scored_day or n_up`` — a FIXTURE-level count (ML-model-scored fixtures,
falling back to upcoming fixtures with >=2 sources).  Fixtures scored but
never emitted as a pick candidate carry no market/selection/price and
therefore cannot become candidate records.  The shadow ledger persists the
CANDIDATE-level scored universe: every emitted scored candidate row (one per
fixture/market/selection/rule) as of the moment the per-day slate is built,
before bucket promotion, operational collapse and ticket selection.  Both
numbers are persisted in the ``run_summary`` event and the report prints both
plus this explanation, so the reconciliation is explicit rather than faked.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from edgefactory import price_sources as psrc
from edgefactory.util import ledger_team_key, norm_league, norm_team

SCHEMA_VERSION = 1

EVENT_SCORED = "scored_candidate"
EVENT_STATUS = "candidate_status"
EVENT_RUN_SUMMARY = "run_summary"
EVENT_SETTLEMENT = "settlement"

STAGE_PICKS_BUILD = "picks_build"
STAGE_TICKET_BUILD = "ticket_build"

# Settlement dispositions. ``pending`` and ``unmatched`` are NEVER losses and
# are excluded from every ROI denominator.
SETTLE_WIN = "win"
SETTLE_LOSS = "loss"
SETTLE_VOID = "void"
SETTLE_PENDING = "pending"
SETTLE_UNMATCHED = "unmatched"

REASON_UNKNOWN = "rejection_reason_unknown"

# Quarantine states that disqualify a captured price from execution safety.
# Mirrors (does not replace) scripts/auto_tickets.py BAD_QUARANTINE.
_BAD_QUARANTINE = {"alias_fuzzy", "suspect", "suspect_alias_fuzzy"}
_SUSPECT_EVIDENCE = "SUSPECT_ALIAS_FUZZY"

_ENV_FLAG = "EDGE_FACTORY_SCORED_SHADOW"
_FALSEY = {"0", "false", "no", "off"}

_SETTLEABLE_MARKET = "1x2"
_SETTLEABLE_SIDES = {"home", "away", "draw"}


# --------------------------------------------------------------- plumbing --
def enabled() -> bool:
    """Audit ledger on/off switch (EDGE_FACTORY_SCORED_SHADOW). Default ON.

    Only the recorders consult this; it gates OBSERVABILITY, never betting
    behaviour — the parity tests prove ticket output is identical either way.
    """
    raw = str(os.environ.get(_ENV_FLAG, "")).strip().lower()
    if not raw:
        return True
    return raw not in _FALSEY


_enabled = enabled


def default_root() -> Path:
    env = os.environ.get("EDGE_FACTORY_LOCALDATA")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent.parent / "localdata"


def ledger_path(day: str, root: Path | None = None) -> Path:
    base = Path(root) if root is not None else default_root()
    return base / f"scored_candidate_shadow_{str(day)[:10]}.jsonl"


def settlement_path(day: str, root: Path | None = None) -> Path:
    base = Path(root) if root is not None else default_root()
    return base / f"scored_candidate_shadow_settlement_{str(day)[:10]}.jsonl"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def new_run_id(stage: str) -> str:
    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}-{stage}"


def _warn(msg: str) -> None:
    print(f"scored-candidate shadow (audit-only; betting unchanged): {msg}",
          file=sys.stderr)


def _append_events(day: str, events: Sequence[Mapping[str, Any]],
                   root: Path | None = None) -> int:
    """Append events to one day file. Raises on IO error (callers fail-soft)."""
    if not events:
        return 0
    path = ledger_path(day, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = "".join(json.dumps(dict(e), sort_keys=True, default=str) + "\n"
                    for e in events)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(lines)
    return len(events)


def _route_and_append(events: Iterable[Mapping[str, Any]],
                      root: Path | None = None) -> int:
    """Route each event to the ledger file of its own trading date."""
    by_day: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for e in events:
        by_day[str(e.get("trading_date") or "")[:10]].append(e)
    n = 0
    for day, evs in by_day.items():
        n += _append_events(day, evs, root)
    return n


# ---------------------------------------------------------------- identity --
def row_trading_date(row: Mapping[str, Any], fallback: str | None = None) -> str:
    return str(row.get("date") or row.get("_archive_day") or fallback or "")[:10]


def candidate_identity(row: Mapping[str, Any], trading_date: str) -> dict[str, str]:
    """Deterministic identity parts: enough to separate the same fixture
    across markets, selections, rule paths, leagues and dates. Never keys on
    display fixture text alone."""
    return {
        "trading_date": str(trading_date)[:10],
        "home_key": ledger_team_key(row.get("home"), width=24),
        "away_key": ledger_team_key(row.get("away"), width=24),
        "league_key": str(
            (row.get("ctx") or {}).get("league_key")
            if isinstance(row.get("ctx"), dict) else ""
        ) or norm_league(row.get("league")),
        "market": str(row.get("market") or "1x2").strip().lower(),
        "selection": str(row.get("pick") or row.get("selection") or "").strip().lower(),
        "rule": str(row.get("rule") or row.get("edge_rule") or "").strip(),
    }


def candidate_id(row: Mapping[str, Any], trading_date: str) -> str:
    parts = candidate_identity(row, trading_date)
    blob = "|".join(parts[k] for k in (
        "trading_date", "home_key", "away_key", "league_key",
        "market", "selection", "rule"))
    return "scs1-" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:20]


# ------------------------------------------------------------ price safety --
def _parse_instant(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        # A naive stamp proves nothing about pre-kickoff ordering. Fail closed.
        return None
    return parsed


def price_pre_kickoff(row: Mapping[str, Any]) -> tuple[bool | None, str]:
    """Was the captured price provably known BEFORE kickoff?

    Returns ``(True, detail)`` only when both the capture instant and
    kickoff_utc parse as timezone-aware instants and capture < kickoff.
    Anything unprovable returns ``(None, reason)`` and the candidate is
    excluded from execution-safe ROI (fail-closed, never loosened).
    """
    captured = _parse_instant(row.get("odds_captured_at") or row.get("as_of"))
    kickoff = _parse_instant(row.get("kickoff_utc"))
    if kickoff is None:
        return None, "pre_kickoff_unproven:no_parseable_kickoff_utc"
    if captured is None:
        return None, "pre_kickoff_unproven:no_parseable_capture_instant"
    if captured >= kickoff:
        return False, "post_kickoff_price"
    return True, "captured_before_kickoff"


def execution_safety(row: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate (never enforce) named-book execution safety of the captured
    price, mirroring the live gates: registered source, execution-eligible,
    named bookmaker, not quarantined, push-eligible, pre-kickoff."""
    out: dict[str, Any] = {
        "execution_safe_named_book_eligible": False,
        "execution_safe_reason": "",
        "price_valid_pre_kickoff": None,
    }
    try:
        odds = float(row.get("odds")) if row.get("odds") is not None else 0.0
    except (TypeError, ValueError):
        odds = 0.0
    if odds <= 1.0:
        out["execution_safe_reason"] = "no_captured_price"
        return out
    quarantine = str(row.get("price_quarantine_reason")
                     or row.get("quarantine") or "none").strip().lower()
    if quarantine in _BAD_QUARANTINE and not row.get("odds_replaced"):
        out["execution_safe_reason"] = f"price_quarantined:{quarantine}"
        return out
    if (str(row.get("price_evidence") or "").upper() == _SUSPECT_EVIDENCE
            and not row.get("odds_replaced")):
        out["execution_safe_reason"] = "price_quarantined:alias_fuzzy_evidence"
        return out
    source_name = str(row.get("odds_source") or "").strip()
    source = psrc.spec(source_name)
    if not psrc.known(source_name):
        out["execution_safe_reason"] = "price_source_unregistered"
        return out
    if not source.can_execute():
        out["execution_safe_reason"] = "price_source_not_execution_eligible"
        return out
    if not source.named_bookmaker:
        # Fair/model (Bet Better) and average donors (Boggio) are NOT
        # named-book execution prices under current policy.
        out["execution_safe_reason"] = "no_named_book_price"
        return out
    if row.get("price_push_eligible") is False:
        out["execution_safe_reason"] = "price_push_ineligible"
        return out
    pre, detail = price_pre_kickoff(row)
    out["price_valid_pre_kickoff"] = pre
    if pre is not True:
        out["execution_safe_reason"] = detail
        return out
    out["execution_safe_named_book_eligible"] = True
    out["execution_safe_reason"] = "named_book_pre_kickoff_execution_safe"
    return out


# ------------------------------------------------------------------ events --
def _country_hint(league: object) -> str | None:
    text = str(league or "")
    for sep in (":", ","):
        if sep in text:
            head = text.split(sep, 1)[0].strip()
            return head or None
    return None


def scored_event(row: Mapping[str, Any], *, trading_date: str, run_id: str,
                 stage: str, build_day: str | None = None) -> dict[str, Any]:
    ident = candidate_identity(row, trading_date)
    ctx = row.get("ctx") if isinstance(row.get("ctx"), dict) else {}
    safety = execution_safety(row)
    selection = ident["selection"]
    side = selection if selection in _SETTLEABLE_SIDES else None
    selection_team = None
    if side == "home":
        selection_team = row.get("home")
    elif side == "away":
        selection_team = row.get("away")
    try:
        odds = float(row.get("odds")) if row.get("odds") is not None else None
    except (TypeError, ValueError):
        odds = None
    try:
        probability = (float(row.get("avg_p")) / 100.0
                       if row.get("avg_p") is not None else None)
    except (TypeError, ValueError):
        probability = None
    source_name = str(row.get("odds_source") or "").strip()
    source = psrc.spec(source_name)
    return {
        "schema_version": SCHEMA_VERSION,
        "event_type": EVENT_SCORED,
        "candidate_id": candidate_id(row, trading_date),
        "run_id": run_id,
        "stage": stage,
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
        "git_sha": os.environ.get("GITHUB_SHA"),
        "trading_date": ident["trading_date"],
        "build_day": str(build_day or trading_date)[:10],
        "captured_at_utc": utc_now_iso(),
        "as_of_utc": row.get("as_of"),
        "fixture": str(row.get("match")
                       or f"{row.get('home')} vs {row.get('away')}"),
        "home_team": row.get("home"),
        "away_team": row.get("away"),
        "normalized_home_team": ident["home_key"],
        "normalized_away_team": ident["away_key"],
        "league": row.get("league"),
        "league_key": ident["league_key"],
        "country": _country_hint(row.get("league")),
        "kickoff_utc": row.get("kickoff_utc"),
        "kickoff_raw": row.get("kickoff"),
        "market": ident["market"],
        "selection": selection,
        "selection_side": side,
        "selection_team": selection_team,
        "rule": ident["rule"],
        "display_rule": row.get("display_rule"),
        "model_version": row.get("model_version"),
        "bucket": row.get("bucket"),
        "score": row.get("w_score"),
        "probability": probability,
        "confidence": row.get("confidence"),
        # No 1x2 model/fair price field exists on slate rows today; recorded
        # as None rather than inferred (fair donors stay fair donors).
        "model_price": row.get("fair_odds") or row.get("model_price"),
        "captured_odds": odds,
        "captured_price_source": source_name or None,
        "captured_bookmaker": row.get("bookmaker"),
        "odds_captured_at": row.get("odds_captured_at"),
        "price_evidence": row.get("price_evidence"),
        "price_odds_kind": row.get("price_odds_kind") or source.odds_kind,
        "price_push_eligible": row.get("price_push_eligible"),
        "price_quarantine_reason": row.get("price_quarantine_reason")
                                    or row.get("quarantine"),
        "source_registered": psrc.known(source_name),
        "source_execution_eligible": source.can_execute(),
        "source_named_bookmaker": bool(source.named_bookmaker),
        "edge_status": row.get("edge_status"),
        "decay_verdict": row.get("decay_verdict"),
        **safety,
    }


def status_event(*, candidate_id_: str, trading_date: str, run_id: str,
                 stage: str, selected_as_pick: bool, selected_on_ticket: bool,
                 final_ticket_status: str,
                 rejection_reasons: Sequence[Mapping[str, str]] = (),
                 drop_stage: str | None = None,
                 acca_id: str | None = None,
                 acca_leg_index: int | None = None,
                 stake_pct_of_capital: float | None = None,
                 stake_fraction_of_capital: float | None = None,
                 stake_fraction_of_bank: float | None = None,
                 price_used_if_selected: float | None = None,
                 bookmaker_used_if_selected: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event_type": EVENT_STATUS,
        "candidate_id": candidate_id_,
        "trading_date": str(trading_date)[:10],
        "run_id": run_id,
        "stage": stage,
        "recorded_at_utc": utc_now_iso(),
        "selected_as_pick": bool(selected_as_pick),
        "selected_on_ticket": bool(selected_on_ticket),
        "final_ticket_status": final_ticket_status,
        "rejection_reasons": [dict(r) for r in rejection_reasons],
        "drop_stage": drop_stage,
        "acca_id": acca_id,
        "acca_leg_index": acca_leg_index,
        "stake_pct_of_capital": stake_pct_of_capital,
        "stake_fraction_of_capital": stake_fraction_of_capital,
        "stake_fraction_of_bank": stake_fraction_of_bank,
        "price_used_if_selected": price_used_if_selected,
        "bookmaker_used_if_selected": bookmaker_used_if_selected,
    }


# ------------------------------------------------------- recording (picks) --
def record_picks_build(*, day: str, scored_rows: Sequence[Mapping[str, Any]],
                       slate_rows: Sequence[Mapping[str, Any]],
                       pre_collapse_rows: Sequence[Mapping[str, Any]] | None = None,
                       pipeline_scored_log: int | None = None,
                       price_supported_markets: Iterable[str] = (),
                       root: Path | None = None,
                       run_id: str | None = None) -> dict[str, Any] | None:
    """Persist the per-day scored candidate universe from the picks build.

    ``scored_rows`` is the full scored candidate list for the day as it
    enters bucket assignment (BEFORE bucket promotion / collapse / ticket
    selection).  ``pre_collapse_rows`` and ``slate_rows`` let this function
    derive honest drop statuses for the two in-build drop points:

    * in ``scored_rows`` but not in ``pre_collapse_rows``: the bucket
      assignment loop's single drop (``bucket_pick`` returned ``None``: a
      CAUTION-bucket candidate under CAUTION_MIN_ODDS) -> ``odds_floor``;
    * in ``pre_collapse_rows`` but not in ``slate_rows``: operational
      duplicate collapse -> ``duplicate_fixture``.

    Fail-soft: every exception is swallowed and reported on stderr.
    """
    if not _enabled():
        return None
    try:
        rid = run_id or new_run_id(STAGE_PICKS_BUILD)
        supported = {str(m) for m in price_supported_markets}
        events: list[dict[str, Any]] = []
        slate_ids = set()
        pre_collapse_ids = set()
        for row in (pre_collapse_rows if pre_collapse_rows is not None
                    else slate_rows):
            pre_collapse_ids.add(candidate_id(row, row_trading_date(row, day)))
        for row in slate_rows:
            slate_ids.add(candidate_id(row, row_trading_date(row, day)))

        n_scored = 0
        for row in scored_rows:
            tdate = row_trading_date(row, day)
            cid = candidate_id(row, tdate)
            events.append(scored_event(row, trading_date=tdate, run_id=rid,
                                       stage=STAGE_PICKS_BUILD, build_day=day))
            n_scored += 1
            if cid in slate_ids:
                events.append(status_event(
                    candidate_id_=cid, trading_date=tdate, run_id=rid,
                    stage=STAGE_PICKS_BUILD, selected_as_pick=True,
                    selected_on_ticket=False,
                    final_ticket_status="pending_ticket_build"))
            elif cid in pre_collapse_ids:
                events.append(status_event(
                    candidate_id_=cid, trading_date=tdate, run_id=rid,
                    stage=STAGE_PICKS_BUILD, selected_as_pick=False,
                    selected_on_ticket=False,
                    final_ticket_status="not_selected",
                    drop_stage="operational_collapse",
                    rejection_reasons=[{
                        "code": "duplicate_fixture",
                        "detail": "collapsed as an operational duplicate of a "
                                  "higher-ranked twin (collapse_final_operational_picks)",
                    }]))
            else:
                events.append(status_event(
                    candidate_id_=cid, trading_date=tdate, run_id=rid,
                    stage=STAGE_PICKS_BUILD, selected_as_pick=False,
                    selected_on_ticket=False,
                    final_ticket_status="not_selected",
                    drop_stage="bucket_assignment",
                    rejection_reasons=[{
                        "code": "odds_floor",
                        "detail": "bucket_pick returned None (the loop's only "
                                  "drop: CAUTION bucket below CAUTION_MIN_ODDS)",
                    }]))
        written = _route_and_append(events, root)
        summary = {
            "schema_version": SCHEMA_VERSION,
            "event_type": EVENT_RUN_SUMMARY,
            "run_id": rid,
            "stage": STAGE_PICKS_BUILD,
            "trading_date": str(day)[:10],
            "build_day": str(day)[:10],
            "recorded_at_utc": utc_now_iso(),
            "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
            "git_sha": os.environ.get("GITHUB_SHA"),
            "shadow_scored": n_scored,
            "slate_total": len(slate_rows),
            "slate_price_supported": sum(
                1 for r in slate_rows
                if str(r.get("market") or "") in supported
                and row_trading_date(r, day) == str(day)[:10]) if supported else None,
            "pipeline_scored_log": pipeline_scored_log,
            "scored_definition": (
                "pipeline 'coverage: scored=' counts ML-scored fixtures "
                "(ml_scored_day) falling back to upcoming fixtures with >=2 "
                "sources (n_up); shadow_scored counts emitted scored candidate "
                "rows (one per fixture/market/selection/rule). Fixture-level "
                "and candidate-level counts differ by construction; both are "
                "persisted here."),
        }
        _append_events(str(day)[:10], [summary], root)
        return {"run_id": rid, "scored": n_scored, "events": written + 1}
    except Exception as exc:  # noqa: BLE001 - audit must never break the build
        _warn(f"picks-build ledger write failed: {exc}")
        return None


# ------------------------------------------------------ recording (tickets) --
def record_ticket_build(*, day: str, slate_rows: Sequence[Mapping[str, Any]],
                        root: Path | None = None,
                        run_id: str | None = None) -> dict[str, Any] | None:
    """Persist the target-day slate universe BEFORE ticket selection runs."""
    if not _enabled():
        return None
    try:
        rid = run_id or new_run_id(STAGE_TICKET_BUILD)
        day10 = str(day)[:10]
        events: list[dict[str, Any]] = []
        for row in slate_rows:
            if row_trading_date(row, day10) != day10:
                continue
            events.append(scored_event(row, trading_date=day10, run_id=rid,
                                       stage=STAGE_TICKET_BUILD, build_day=day10))
        _route_and_append(events, root)
        return {"run_id": rid, "scored": len(events)}
    except Exception as exc:  # noqa: BLE001
        _warn(f"ticket-build ledger write failed: {exc}")
        return None


def build_ticket_status_rows(slate_rows: Sequence[Mapping[str, Any]], *,
                             day: str,
                             selected: Mapping[tuple, Mapping[str, Any]] | None,
                             staged: Mapping[tuple, tuple[str, str]] | None,
                             default_rule: tuple[str, str],
                             gate: Callable[[Mapping[str, Any]],
                                            tuple[str, str] | None] | None,
                             key_of: Callable[[Mapping[str, Any]], tuple],
                             final_ticket_status: str,
                             bank_pct: float | None = None) -> list[dict[str, Any]]:
    """Pure assembly of per-candidate final status rows (no IO).

    Reasons are DERIVED from real state, never invented:
    * ``gate`` is the live candidate-gate predicate (the same single source
      of truth used by playable_legs / the operator rejection ledger);
    * ``staged`` carries decisions made after the gate (kickoff guard,
      tripwires, slice policy), keyed exactly like plan legs;
    * ``default_rule`` names the branch-level terminal decision.
    A candidate can therefore carry multiple reasons (gate + staged).  When
    nothing is derivable the explicit ``rejection_reason_unknown`` marker is
    recorded and surfaced by the report.
    """
    day10 = str(day)[:10]
    selected = selected or {}
    staged = staged or {}
    rows: list[dict[str, Any]] = []
    for row in slate_rows:
        if row_trading_date(row, day10) != day10:
            continue
        key = key_of(row)
        cid = candidate_id(row, day10)
        info = selected.get(key)
        if info is not None:
            stake_pct = info.get("stake_pct_of_capital")
            try:
                stake_pct_f = float(stake_pct) if stake_pct is not None else None
            except (TypeError, ValueError):
                stake_pct_f = None
            frac_capital = (stake_pct_f / 100.0) if stake_pct_f is not None else None
            frac_bank = None
            try:
                if stake_pct_f is not None and bank_pct:
                    frac_bank = stake_pct_f / float(bank_pct)
            except (TypeError, ValueError, ZeroDivisionError):
                frac_bank = None
            rows.append({
                "candidate_id": cid,
                "trading_date": day10,
                "selected_as_pick": True,
                "selected_on_ticket": True,
                "final_ticket_status": final_ticket_status,
                "rejection_reasons": [],
                "drop_stage": None,
                "acca_id": info.get("acca_id"),
                "acca_leg_index": info.get("acca_leg_index"),
                "stake_pct_of_capital": stake_pct_f,
                "stake_fraction_of_capital": frac_capital,
                "stake_fraction_of_bank": frac_bank,
                "price_used_if_selected": info.get("price_used_if_selected"),
                "bookmaker_used_if_selected": row.get("bookmaker"),
            })
            continue
        reasons: list[dict[str, str]] = []
        drop_stage = None
        gate_reason = gate(row) if gate is not None else None
        if gate_reason is not None:
            reasons.append({"code": str(gate_reason[0]),
                            "detail": str(gate_reason[1])})
            drop_stage = "candidate_gate"
        staged_reason = staged.get(key)
        if staged_reason is not None:
            reasons.append({"code": str(staged_reason[0]),
                            "detail": str(staged_reason[1])})
            drop_stage = drop_stage or "policy_stage"
        if not reasons:
            if default_rule and default_rule[0]:
                reasons.append({"code": str(default_rule[0]),
                                "detail": str(default_rule[1])})
                drop_stage = "final_selection"
            else:
                reasons.append({"code": REASON_UNKNOWN,
                                "detail": "no derivable rejection reason"})
                drop_stage = "unknown"
        rows.append({
            "candidate_id": cid,
            "trading_date": day10,
            "selected_as_pick": True,   # it reached the operational slate
            "selected_on_ticket": False,
            "final_ticket_status": "not_selected",
            "rejection_reasons": reasons,
            "drop_stage": drop_stage,
            "acca_id": None,
            "acca_leg_index": None,
            "stake_pct_of_capital": None,
            "stake_fraction_of_capital": None,
            "stake_fraction_of_bank": None,
            "price_used_if_selected": None,
            "bookmaker_used_if_selected": None,
        })
    return rows


def record_ticket_outcome(*, day: str, run_id: str,
                          status_rows: Sequence[Mapping[str, Any]],
                          final_ticket_status: str,
                          root: Path | None = None,
                          bank_pct: float | None = None) -> dict[str, Any] | None:
    """Append final selection/rejection status events + a run summary."""
    if not _enabled():
        return None
    try:
        day10 = str(day)[:10]
        events = []
        n_pick = n_ticket = 0
        for srow in status_rows:
            if srow.get("selected_as_pick"):
                n_pick += 1
            if srow.get("selected_on_ticket"):
                n_ticket += 1
            events.append(status_event(
                candidate_id_=str(srow.get("candidate_id")),
                trading_date=str(srow.get("trading_date") or day10),
                run_id=run_id, stage=STAGE_TICKET_BUILD,
                selected_as_pick=bool(srow.get("selected_as_pick")),
                selected_on_ticket=bool(srow.get("selected_on_ticket")),
                final_ticket_status=str(srow.get("final_ticket_status")),
                rejection_reasons=srow.get("rejection_reasons") or (),
                drop_stage=srow.get("drop_stage"),
                acca_id=srow.get("acca_id"),
                acca_leg_index=srow.get("acca_leg_index"),
                stake_pct_of_capital=srow.get("stake_pct_of_capital"),
                stake_fraction_of_capital=srow.get("stake_fraction_of_capital"),
                stake_fraction_of_bank=srow.get("stake_fraction_of_bank"),
                price_used_if_selected=srow.get("price_used_if_selected"),
                bookmaker_used_if_selected=srow.get("bookmaker_used_if_selected"),
            ))
        summary = {
            "schema_version": SCHEMA_VERSION,
            "event_type": EVENT_RUN_SUMMARY,
            "run_id": run_id,
            "stage": STAGE_TICKET_BUILD,
            "trading_date": day10,
            "build_day": day10,
            "recorded_at_utc": utc_now_iso(),
            "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
            "git_sha": os.environ.get("GITHUB_SHA"),
            "card_status": final_ticket_status,
            "status_rows": len(events),
            "selected_on_ticket": n_ticket,
            "bank_pct": bank_pct,
        }
        _route_and_append(events, root)
        _append_events(day10, [summary], root)
        return {"run_id": run_id, "statuses": len(events)}
    except Exception as exc:  # noqa: BLE001
        _warn(f"ticket-outcome ledger write failed: {exc}")
        return None


# ------------------------------------------------------------------ reading --
def read_ledger(day: str, root: Path | None = None) -> list[dict[str, Any]]:
    path = ledger_path(day, root)
    events: list[dict[str, Any]] = []
    if not path.exists():
        return events
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            obj["_order"] = idx
            events.append(obj)
    return events


def load_settled_overlay(root: Path | None = None) -> dict[tuple, str]:
    """Exact settled-fact map from the shared overlay file ONLY (fallback
    when the full warehouse loader is unavailable). Exact keys, no fuzz."""
    base = Path(root) if root is not None else default_root()
    try:
        data = json.loads((base / "settled_results.json").read_text())
    except (OSError, ValueError, TypeError):
        return {}
    out: dict[tuple, str] = {}
    for r in data.get("rows", []) if isinstance(data, dict) else []:
        day = str(r.get("date") or "")[:10]
        out.setdefault((day, norm_team(r.get("home")), norm_team(r.get("away"))),
                       str(r.get("outcome")))
    return out


# -------------------------------------------------------------- settlement --
def settle_candidate(cand: Mapping[str, Any],
                     settled: Mapping[tuple, str]) -> dict[str, Any]:
    """Read-only settlement of one scored-candidate payload.

    EXACT normalized matching only: ``(trading_date, norm_team(home),
    norm_team(away))``.  No fuzzy matching, no alias scan, no reschedule
    window, no kickoff-tolerance change.  Non-1x2 markets and non
    home/away/draw sides are ``unmatched`` (not safely settleable here),
    missing results stay ``pending`` — never losses.
    """
    market = str(cand.get("market") or "").lower()
    side = str(cand.get("selection_side") or cand.get("selection") or "").lower()
    if market != _SETTLEABLE_MARKET or side not in _SETTLEABLE_SIDES:
        return {"settlement_status": SETTLE_UNMATCHED,
                "settlement_detail": "market_or_side_not_safely_settleable",
                "outcome": None}
    home = cand.get("home_team")
    away = cand.get("away_team")
    day = str(cand.get("trading_date") or "")[:10]
    if not day or not str(home or "").strip() or not str(away or "").strip():
        return {"settlement_status": SETTLE_UNMATCHED,
                "settlement_detail": "missing_fixture_identity",
                "outcome": None}
    outcome = settled.get((day, norm_team(home), norm_team(away)))
    if outcome is None:
        return {"settlement_status": SETTLE_PENDING,
                "settlement_detail": "no_exact_result_match",
                "outcome": None}
    if outcome not in _SETTLEABLE_SIDES:
        return {"settlement_status": SETTLE_VOID,
                "settlement_detail": f"terminal_non_score_outcome:{outcome}",
                "outcome": str(outcome)}
    status = SETTLE_WIN if outcome == side else SETTLE_LOSS
    return {"settlement_status": status, "settlement_detail": "exact_match",
            "outcome": str(outcome)}


def flat_stake_return(settlement_status: str, odds: float | None) -> float | None:
    """Flat 1-unit stake convention: win=odds-1, loss=-1, void=0.
    Pending/unmatched (and missing odds) return None: excluded from ROI."""
    if settlement_status == SETTLE_VOID:
        return 0.0
    if settlement_status == SETTLE_LOSS:
        return -1.0
    if settlement_status == SETTLE_WIN:
        if odds is None or odds <= 1.0:
            return None
        return float(odds) - 1.0
    return None


# ------------------------------------------------------------------ report --
def _pick_effective_runs(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Default snapshot policy (draft/freeze gotcha):

    * if any ticket-build run recorded a frozen/superseded card, use the
      LATEST such run's statuses (the final card of record);
    * otherwise use the latest ticket-build run and mark the report draft;
    * candidates with no ticket-run status fall back to their latest
      picks-build status (they never reached the slate/ticket stage).
    """
    run_order: dict[str, int] = {}
    run_card: dict[str, str] = {}
    run_stage: dict[str, str] = {}
    for e in events:
        rid = str(e.get("run_id") or "")
        if not rid:
            continue
        run_order[rid] = max(run_order.get(rid, -1), int(e.get("_order", 0)))
        run_stage.setdefault(rid, str(e.get("stage") or ""))
        if e.get("event_type") == EVENT_RUN_SUMMARY and e.get("card_status"):
            run_card[rid] = str(e.get("card_status"))
        elif (e.get("event_type") == EVENT_STATUS
              and e.get("selected_on_ticket")
              and str(e.get("final_ticket_status")) in ("frozen", "draft")):
            run_card.setdefault(rid, str(e.get("final_ticket_status")))
    ticket_runs = [r for r, s in run_stage.items() if s == STAGE_TICKET_BUILD]
    frozen_like = [r for r in ticket_runs
                   if run_card.get(r) in ("frozen", "superseded_no_bet")]
    effective = None
    snapshot = "none"
    if frozen_like:
        effective = max(frozen_like, key=lambda r: run_order[r])
        snapshot = run_card.get(effective, "frozen")
    elif ticket_runs:
        effective = max(ticket_runs, key=lambda r: run_order[r])
        snapshot = run_card.get(effective, "draft")
    return {"effective_ticket_run": effective, "snapshot": snapshot,
            "ticket_runs": sorted(ticket_runs,
                                  key=lambda r: run_order.get(r, 0)),
            "run_order": run_order}


def _blank_agg() -> dict[str, Any]:
    return {"candidates": 0, "settled": 0, "wins": 0, "losses": 0, "voids": 0,
            "pending": 0, "unmatched": 0, "no_price": 0,
            "flat_profit": 0.0, "flat_roi": None}


def _agg_add(agg: dict[str, Any], cand: Mapping[str, Any]) -> None:
    agg["candidates"] += 1
    status = cand.get("settlement_status")
    odds = cand.get("captured_odds")
    if status == SETTLE_PENDING:
        agg["pending"] += 1
        return
    if status == SETTLE_UNMATCHED:
        agg["unmatched"] += 1
        return
    ret = flat_stake_return(str(status), odds)
    if ret is None:
        # settled but no usable captured price -> cannot grade a stake
        agg["no_price"] += 1
        return
    agg["settled"] += 1
    if status == SETTLE_WIN:
        agg["wins"] += 1
    elif status == SETTLE_LOSS:
        agg["losses"] += 1
    elif status == SETTLE_VOID:
        agg["voids"] += 1
    agg["flat_profit"] = round(agg["flat_profit"] + ret, 6)


def _agg_close(agg: dict[str, Any]) -> dict[str, Any]:
    if agg["settled"] > 0:
        agg["flat_roi"] = round(agg["flat_profit"] / agg["settled"], 6)
    return agg


def build_report(day: str, *, root: Path | None = None,
                 settled: Mapping[tuple, str] | None = None,
                 all_runs: bool = False) -> dict[str, Any]:
    """Assemble the read-only shadow grading report for one trading date."""
    day10 = str(day)[:10]
    events = read_ledger(day10, root)
    settled = settled if settled is not None else load_settled_overlay(root)

    scored_by_cid: dict[str, dict[str, Any]] = {}
    status_by_run: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    picks_status_by_cid: dict[str, dict[str, Any]] = {}
    run_summaries: list[dict[str, Any]] = []
    for e in events:
        etype = e.get("event_type")
        if etype == EVENT_SCORED and str(e.get("trading_date")) == day10:
            cid = str(e.get("candidate_id"))
            prev = scored_by_cid.get(cid)
            # keep the latest capture, but never let a later event ERASE an
            # earlier captured price with None (draft reruns must not launder
            # price evidence away)
            if prev is None:
                scored_by_cid[cid] = dict(e)
            else:
                merged = dict(e)
                if merged.get("captured_odds") is None and prev.get("captured_odds") is not None:
                    for k in ("captured_odds", "captured_price_source",
                              "captured_bookmaker", "price_evidence",
                              "price_odds_kind", "price_push_eligible",
                              "odds_captured_at",
                              "execution_safe_named_book_eligible",
                              "execution_safe_reason", "price_valid_pre_kickoff"):
                        merged[k] = prev.get(k)
                scored_by_cid[cid] = merged
        elif etype == EVENT_STATUS and str(e.get("trading_date")) == day10:
            cid = str(e.get("candidate_id"))
            if str(e.get("stage")) == STAGE_TICKET_BUILD:
                status_by_run[str(e.get("run_id"))][cid] = dict(e)
            else:
                picks_status_by_cid[cid] = dict(e)
        elif etype == EVENT_RUN_SUMMARY:
            run_summaries.append(dict(e))

    policy = _pick_effective_runs(events)
    effective_run = policy["effective_ticket_run"]
    effective_statuses = status_by_run.get(effective_run, {}) if effective_run else {}

    unknown_reason_count = 0
    candidates: list[dict[str, Any]] = []
    for cid, payload in scored_by_cid.items():
        cand = dict(payload)
        status = effective_statuses.get(cid) or picks_status_by_cid.get(cid)
        if status is None:
            cand["selected_as_pick"] = False
            cand["selected_on_ticket"] = False
            cand["final_ticket_status"] = "no_status_recorded"
            cand["rejection_reasons"] = [{
                "code": REASON_UNKNOWN,
                "detail": "no selection/rejection status event recorded"}]
            cand["drop_stage"] = "unknown"
        else:
            cand["selected_as_pick"] = bool(status.get("selected_as_pick"))
            cand["selected_on_ticket"] = bool(status.get("selected_on_ticket"))
            cand["final_ticket_status"] = status.get("final_ticket_status")
            cand["rejection_reasons"] = status.get("rejection_reasons") or []
            cand["drop_stage"] = status.get("drop_stage")
            cand["acca_id"] = status.get("acca_id")
            cand["stake_pct_of_capital"] = status.get("stake_pct_of_capital")
        if any(r.get("code") == REASON_UNKNOWN
               for r in cand["rejection_reasons"]):
            unknown_reason_count += 1
        cand.update(settle_candidate(cand, settled))
        candidates.append(cand)

    candidates.sort(key=lambda c: (str(c.get("fixture")), str(c.get("market")),
                                   str(c.get("selection"))))

    def agg_of(filt: Callable[[Mapping[str, Any]], bool]) -> dict[str, Any]:
        agg = _blank_agg()
        for c in candidates:
            if filt(c):
                _agg_add(agg, c)
        return _agg_close(agg)

    def group_by(key_fn: Callable[[Mapping[str, Any]], object],
                 filt: Callable[[Mapping[str, Any]], bool] = lambda c: True,
                 ) -> dict[str, dict[str, Any]]:
        groups: dict[str, dict[str, Any]] = {}
        for c in candidates:
            if not filt(c):
                continue
            key = str(key_fn(c) or "unknown")
            groups.setdefault(key, _blank_agg())
            _agg_add(groups[key], c)
        return {k: _agg_close(v) for k, v in sorted(groups.items())}

    def by_reason(filt: Callable[[Mapping[str, Any]], bool]) -> dict[str, dict[str, Any]]:
        groups: dict[str, dict[str, Any]] = {}
        for c in candidates:
            if not filt(c):
                continue
            codes = [r.get("code") or "unknown"
                     for r in (c.get("rejection_reasons") or [])] or ["none"]
            for code in codes:
                groups.setdefault(str(code), _blank_agg())
                _agg_add(groups[str(code)], c)
        return {k: _agg_close(v) for k, v in sorted(groups.items())}

    is_ticketed = lambda c: c["selected_on_ticket"]                      # noqa: E731
    is_promoted = lambda c: c["selected_as_pick"]                        # noqa: E731
    is_rejected = lambda c: not c["selected_on_ticket"]                  # noqa: E731
    is_exec_safe = lambda c: bool(c.get("execution_safe_named_book_eligible"))  # noqa: E731

    picks_summary = next(
        (s for s in sorted(run_summaries, key=lambda s: s.get("_order", 0),
                           reverse=True)
         if s.get("stage") == STAGE_PICKS_BUILD
         and str(s.get("trading_date")) == day10), None)
    ticket_summary = None
    if effective_run:
        ticket_summary = next((s for s in run_summaries
                               if s.get("run_id") == effective_run
                               and s.get("event_type") == EVENT_RUN_SUMMARY), None)

    shadow_scored = len(candidates)
    shadow_selected_as_pick = sum(1 for c in candidates if c["selected_as_pick"])
    reconciliation = {
        "shadow_scored": shadow_scored,
        "shadow_selected_as_pick": shadow_selected_as_pick,
        "shadow_selected_on_ticket": sum(1 for c in candidates
                                         if c["selected_on_ticket"]),
        "pipeline_scored_log": (picks_summary or {}).get("pipeline_scored_log"),
        "pipeline_slate_price_supported":
            (picks_summary or {}).get("slate_price_supported"),
        "scored_definition": (picks_summary or {}).get(
            "scored_definition",
            "no picks-build run summary persisted for this date; shadow counts "
            "come from ticket-build capture of the slate only, so fixture-level "
            "pipeline scored= counts cannot be reconciled for this date"),
        "note": None,
    }
    pl = reconciliation["pipeline_scored_log"]
    if pl is not None and int(pl) != shadow_scored:
        reconciliation["note"] = (
            f"pipeline scored={pl} is a FIXTURE-level count while "
            f"shadow_scored={shadow_scored} is candidate-level (see "
            "scored_definition); fixtures scored without an emitted candidate "
            "row have no market/selection and cannot be graded.")

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "date": day10,
        "generated_at_utc": utc_now_iso(),
        "snapshot_used": policy["snapshot"],
        "effective_ticket_run": effective_run,
        "ticket_runs_seen": policy["ticket_runs"],
        "dedupe_policy": (
            "candidates deduped by candidate_id across draft reruns; statuses "
            "come from the latest frozen/superseded ticket run when one "
            "exists, else the latest draft ticket run (report marked draft), "
            "else the picks-build status"),
        "counts": {
            "total_scored": shadow_scored,
            "promoted_picks": shadow_selected_as_pick,
            "ticketed_legs": sum(1 for c in candidates if c["selected_on_ticket"]),
            "promoted_not_ticketed": sum(
                1 for c in candidates
                if c["selected_as_pick"] and not c["selected_on_ticket"]),
            "scored_not_promoted": sum(
                1 for c in candidates if not c["selected_as_pick"]),
            "execution_safe_scored": sum(1 for c in candidates if is_exec_safe(c)),
            "execution_safe_rejected": sum(
                1 for c in candidates if is_exec_safe(c) and is_rejected(c)),
            "pending": sum(1 for c in candidates
                           if c["settlement_status"] == SETTLE_PENDING),
            "unmatched": sum(1 for c in candidates
                             if c["settlement_status"] == SETTLE_UNMATCHED),
            "no_execution_safe_price": sum(
                1 for c in candidates if not is_exec_safe(c)),
            "unknown_rejection_reason": unknown_reason_count,
            "settled_win": sum(1 for c in candidates
                               if c["settlement_status"] == SETTLE_WIN),
            "settled_loss": sum(1 for c in candidates
                                if c["settlement_status"] == SETTLE_LOSS),
            "settled_void": sum(1 for c in candidates
                                if c["settlement_status"] == SETTLE_VOID),
        },
        "roi": {
            "ticketed_legs": agg_of(is_ticketed),
            "promoted_not_ticketed": agg_of(
                lambda c: is_promoted(c) and not is_ticketed(c)),
            "all_scored": agg_of(lambda c: True),
            "all_scored_rejected": agg_of(is_rejected),
            "execution_safe_rejected": agg_of(
                lambda c: is_exec_safe(c) and is_rejected(c)),
            "execution_safe_all": agg_of(is_exec_safe),
            "selected_vs_rejected": {
                "selected": agg_of(is_ticketed),
                "rejected": agg_of(is_rejected),
            },
            "by_rejection_reason": by_reason(is_rejected),
            "by_rejection_reason_execution_safe": by_reason(
                lambda c: is_exec_safe(c) and is_rejected(c)),
            "by_bucket": group_by(lambda c: c.get("bucket")),
            "by_rule": group_by(lambda c: c.get("rule")),
            "by_league": group_by(lambda c: c.get("league")),
            "by_market": group_by(lambda c: c.get("market")),
            "by_price_source": group_by(lambda c: c.get("captured_price_source")),
            "by_bookmaker": group_by(lambda c: c.get("captured_bookmaker")),
            "by_execution_safety": {
                "execution_safe": agg_of(is_exec_safe),
                "not_execution_safe": agg_of(lambda c: not is_exec_safe(c)),
            },
        },
        "reconciliation": reconciliation,
        "ticket_run_summary": ticket_summary,
        "candidates": candidates,
    }
    if all_runs:
        report["all_runs"] = {
            rid: {
                "statuses": len(stat_map),
                "selected_on_ticket": sum(1 for s in stat_map.values()
                                          if s.get("selected_on_ticket")),
            }
            for rid, stat_map in status_by_run.items()
        }
    return report


def settlement_events(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Derive explicit append-only settlement events from a built report."""
    out = []
    for c in report.get("candidates", []):
        out.append({
            "schema_version": SCHEMA_VERSION,
            "event_type": EVENT_SETTLEMENT,
            "candidate_id": c.get("candidate_id"),
            "trading_date": c.get("trading_date"),
            "recorded_at_utc": utc_now_iso(),
            "settlement_status": c.get("settlement_status"),
            "settlement_detail": c.get("settlement_detail"),
            "outcome": c.get("outcome"),
            "match_basis": "exact_normalized_fixture",
            "flat_stake_return": flat_stake_return(
                str(c.get("settlement_status")), c.get("captured_odds")),
        })
    return out


def _fmt_agg(name: str, agg: Mapping[str, Any]) -> str:
    roi = agg.get("flat_roi")
    roi_s = f"{roi * 100.0:+.1f}%" if roi is not None else "n/a"
    return (f"  {name:42s} n={agg['candidates']:<3d} settled={agg['settled']:<3d} "
            f"W/L/V={agg['wins']}/{agg['losses']}/{agg['voids']} "
            f"pending={agg['pending']} unmatched={agg['unmatched']} "
            f"no_price={agg['no_price']} flat={agg['flat_profit']:+.2f}u "
            f"roi={roi_s}")


def render_report(report: Mapping[str, Any]) -> str:
    c = report["counts"]
    r = report["roi"]
    rec = report["reconciliation"]
    lines = [
        f"SCORED-CANDIDATE SHADOW GRADING — {report['date']} (read-only audit)",
        "=" * 70,
        f"snapshot_used={report['snapshot_used']} "
        f"effective_ticket_run={report['effective_ticket_run'] or 'none'}",
        f"dedupe: {report['dedupe_policy']}",
        "",
        "COUNTS:",
        f"  total scored:               {c['total_scored']}",
        f"  promoted picks (slate):     {c['promoted_picks']}",
        f"  ticketed legs:              {c['ticketed_legs']}",
        f"  promoted but not ticketed:  {c['promoted_not_ticketed']}",
        f"  scored but not promoted:    {c['scored_not_promoted']}",
        f"  execution-safe scored:      {c['execution_safe_scored']}",
        f"  execution-safe rejected:    {c['execution_safe_rejected']}",
        f"  pending/unsettled:          {c['pending']}",
        f"  unmatched settlement:       {c['unmatched']}",
        f"  no execution-safe price:    {c['no_execution_safe_price']}",
        f"  unknown rejection reason:   {c['unknown_rejection_reason']}",
        f"  settled win/loss/void:      {c['settled_win']}/{c['settled_loss']}/{c['settled_void']}",
        "",
        "FLAT-STAKE ROI (win=odds-1, loss=-1, void=0; pending/unmatched/no-price",
        "excluded from the denominator; non-executable prices never enter the",
        "execution-safe lines):",
        _fmt_agg("ticketed selected legs", r["ticketed_legs"]),
        _fmt_agg("promoted picks not ticketed", r["promoted_not_ticketed"]),
        _fmt_agg("all scored", r["all_scored"]),
        _fmt_agg("all scored rejected", r["all_scored_rejected"]),
        _fmt_agg("execution-safe rejected ONLY", r["execution_safe_rejected"]),
        _fmt_agg("execution-safe all", r["execution_safe_all"]),
        "",
        "BY REJECTION REASON (rejected candidates; multi-reason rows count",
        "under each of their reasons):",
    ]
    for code, agg in r["by_rejection_reason"].items():
        lines.append(_fmt_agg(code, agg))
    lines += ["", "BY REJECTION REASON (execution-safe rejected only):"]
    for code, agg in r["by_rejection_reason_execution_safe"].items():
        lines.append(_fmt_agg(code, agg))
    for title, key in (("BY BUCKET:", "by_bucket"), ("BY RULE:", "by_rule"),
                       ("BY LEAGUE:", "by_league"), ("BY MARKET:", "by_market"),
                       ("BY PRICE SOURCE:", "by_price_source"),
                       ("BY BOOKMAKER:", "by_bookmaker")):
        lines += ["", title]
        for name, agg in r[key].items():
            lines.append(_fmt_agg(name, agg))
    lines += [
        "",
        "SELECTED vs REJECTED:",
        _fmt_agg("selected (ticketed)", r["selected_vs_rejected"]["selected"]),
        _fmt_agg("rejected", r["selected_vs_rejected"]["rejected"]),
        "",
        "EXECUTION-SAFE vs NOT:",
        _fmt_agg("execution-safe", r["by_execution_safety"]["execution_safe"]),
        _fmt_agg("not execution-safe", r["by_execution_safety"]["not_execution_safe"]),
        "",
        "RECONCILIATION:",
        f"  shadow_scored={rec['shadow_scored']} "
        f"shadow_selected_as_pick={rec['shadow_selected_as_pick']} "
        f"shadow_selected_on_ticket={rec['shadow_selected_on_ticket']}",
        f"  pipeline_scored_log={rec['pipeline_scored_log']} "
        f"pipeline_slate_price_supported={rec['pipeline_slate_price_supported']}",
        f"  scored_definition: {rec['scored_definition']}",
    ]
    if rec.get("note"):
        lines.append(f"  note: {rec['note']}")
    return "\n".join(lines)
