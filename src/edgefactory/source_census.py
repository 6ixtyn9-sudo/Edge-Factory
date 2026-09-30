"""Per-source, per-day fixture census — diagnostic only.

The funnel answers "how many rows did each source give us?". This answers
the question an operator actually asks when the slate looks thin:

    which matches does each source see, for each date, and why can't
    the production lane use them?

It is strictly read-only. It cannot dispatch, promote, certify, enable or
re-tier anything, and it never infers a probability, kickoff, odds value or
fixture identity that the audited normalization layer did not already
produce. A source with rows is reported as a source with rows — that is
capture, not validation, and the census says so.

Roles come from ``source_registry``, so a captured source can never be
silently missing from the report and no tier is hardcoded here.
"""

from __future__ import annotations

import csv
import gzip
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from . import selection_evidence
from . import source_registry

# ---------------------------------------------------------------------------
# production roles (derived, never hardcoded per source)
# ---------------------------------------------------------------------------

ROLE_LIVE_VOTER = "live_voter"
ROLE_SHADOW_VOTER = "shadow_voter"
ROLE_NOT_A_VOTER = "not_a_voter"
ROLE_DONOR_ONLY = "donor_only"
ROLE_ODDS_ONLY = "odds_only"
ROLE_BLOCKED = "blocked"
ROLE_UNAVAILABLE = "unavailable"

# objective blocker vocabulary
B_NO_ROWS = "no_rows"
B_NO_1X2 = "no_1x2_probability_fields"
B_NO_TRUSTED_KICKOFF = "no_trusted_kickoff"
B_INSIDE_LEAD = "inside_30m_lead_or_started"
B_TIER_NOT_DISPATCHABLE = "source_tier_not_dispatchable"
B_NOT_CONSUMED = "source_not_consumed_by_pick_engine"
B_DONOR = "settlement_donor_only"
B_ODDS_ONLY = "odds_only"
B_TRANSPORT = "transport_failure_if_known"
B_SETTLED = "already_settled"
B_IDENTITY_KEY = "identity_key_too_short"
B_NO_IDENTITY_COLUMNS = "no_fixture_identity_columns"
D_PRICE_JOIN_UNAVAILABLE = "price_source_carries_no_fixture_identity"

# thin-slate diagnosis vocabulary
D_FEWER_THAN_2_VOTERS = "fewer_than_2_live_voters"
D_NO_ML_ANCHOR = "no_ml_anchor_source_present"
D_MISSING_KICKOFF = "missing_trusted_kickoff"
D_INSIDE_LEAD = "inside_30m_lead_or_started"
D_TIER_NOT_DISPATCHABLE = "source_tier_not_dispatchable"
D_NO_PRICE = "no_price_coverage"
D_SINGLE_SOURCE = "fixture_seen_by_one_source_only"

DEFAULT_MIN_LEAD = 30


def census_sources() -> tuple[str, ...]:
    """Every source the census must report, including zero-row ones."""
    return tuple(c.name for c in source_registry.REGISTRY)


def production_role(source: str, *, raw_rows: int,
                    consumed_by_engine: bool,
                    in_consensus_surface: bool,
                    transport_failed: bool = False) -> str:
    """Role this source plays in production on this date.

    Derived from the capability registry plus what the engine actually
    consumes, so a shadow source can never be described as a live voter.
    """
    cap = source_registry.get(source)
    if cap is None:
        return ROLE_NOT_A_VOTER
    if cap.tier == source_registry.TIER_PRICING:
        return ROLE_ODDS_ONLY
    if cap.tier == source_registry.TIER_DONOR:
        return ROLE_DONOR_ONLY
    if transport_failed or raw_rows == 0:
        return ROLE_UNAVAILABLE
    if cap.tier == source_registry.TIER_SHADOW:
        return ROLE_SHADOW_VOTER
    # live tier
    if "1x2" not in cap.markets:
        return ROLE_NOT_A_VOTER          # e.g. OU/BTTS-only live source
    if not consumed_by_engine:
        return ROLE_BLOCKED
    if not in_consensus_surface:
        return ROLE_NOT_A_VOTER
    return ROLE_LIVE_VOTER


# ---------------------------------------------------------------------------
# row loading (capture caches only — no network, ever)
# ---------------------------------------------------------------------------


def source_files(localdata: Path, source: str) -> list[Path]:
    monthly = sorted(localdata.glob(
        f"{source}_[0-9][0-9][0-9][0-9]-[0-9][0-9].csv.gz"))
    legacy = localdata / f"{source}.csv.gz"
    return ([legacy] if legacy.exists() else []) + monthly


def iter_rows(path: Path) -> Iterator[dict[str, str]]:
    try:
        with gzip.open(path, "rt", newline="", encoding="utf-8",
                       errors="replace") as handle:
            yield from csv.DictReader(handle)
    except (OSError, csv.Error, UnicodeError):
        return


def load_day_rows(localdata: Path, source: str, day: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in source_files(localdata, source):
        for row in iter_rows(path):
            if str(row.get("date") or "").strip()[:10] == day:
                rows.append(dict(row, _census_file=path.name))
    return rows


def _has_value(row: dict, *keys: str) -> bool:
    return any(str(row.get(k) or "").strip() not in {"", "None", "-", "nan"}
               for k in keys)


def _num(row: dict, *keys: str):
    for key in keys:
        raw = str(row.get(key) or "").strip()
        if raw in {"", "None", "-", "nan"}:
            continue
        try:
            return float(raw)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# per-fixture record
# ---------------------------------------------------------------------------


@dataclass
class FixtureRecord:
    event_date: str
    source: str
    source_file: str | None = None
    raw_home: str = ""
    raw_away: str = ""
    normalized_home: str = ""
    normalized_away: str = ""
    league: str | None = None
    kickoff_raw: str | None = None
    kickoff_parsed: str | None = None
    kickoff_trusted: bool = False
    has_1x2: bool = False
    has_ou: bool = False
    has_btts: bool = False
    has_price: bool = False
    home_probability: float | None = None
    draw_probability: float | None = None
    away_probability: float | None = None
    home_odds: float | None = None
    draw_odds: float | None = None
    away_odds: float | None = None
    odds_source: str | None = None
    price_evidence: str | None = None
    price_quarantine_reason: str | None = None
    odds_replaced: bool | None = None
    price_push_eligible: bool | None = None
    prematch_eligible: bool = False
    production_consumable: bool = False
    non_consumable_reasons: list[str] = field(default_factory=list)
    fixture_group_key: str = ""

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _fixture_record(source: str, row: dict, *, day: str, engine,
                    as_of: datetime, min_lead: int, role: str,
                    ou_col: str | None, btts_col: str | None) -> FixtureRecord:
    home = str(row.get("home") or "")
    away = str(row.get("away") or "")
    nh = engine.source_team_key(home)
    na = engine.source_team_key(away)

    rec = FixtureRecord(
        event_date=day, source=source, source_file=row.get("_census_file"),
        raw_home=home, raw_away=away, normalized_home=nh, normalized_away=na,
        league=(str(row.get("league") or row.get("competition") or "").strip()
                or None),
        fixture_group_key=f"{nh}|{na}",
    )

    ko_raw = row.get("kickoff") or row.get("time")
    rec.kickoff_raw = str(ko_raw).strip() if str(ko_raw or "").strip() else None
    # The fixture's own event date is the reference: "01-10, 06:10" is
    # 1 October, and must never be read against the wall-clock year or the
    # run date. Never guess a kickoff that does not parse.
    parsed = engine.parse_kickoff_dt(ko_raw, day) if rec.kickoff_raw else None
    if parsed is not None:
        rec.kickoff_trusted = True
        if parsed.tzinfo is None and as_of.tzinfo is not None:
            parsed = parsed.replace(tzinfo=as_of.tzinfo)
        rec.kickoff_parsed = parsed.isoformat()
        rec.prematch_eligible = (
            (parsed - as_of).total_seconds() / 60.0 >= min_lead)

    # Raw source opinion, reported verbatim and never derived.
    tip = str(row.get("tip") or row.get("prediction") or row.get("pick")
              or "").strip()
    rec.tip = tip or None
    pred_h, pred_a = row.get("pred_hs"), row.get("pred_gs")
    if str(pred_h or "").strip() and str(pred_a or "").strip():
        rec.projected_score = f"{str(pred_h).strip()}-{str(pred_a).strip()}"

    probs = engine.probs_1x2(row)
    if probs is not None:
        rec.has_1x2 = True
        rec.home_probability, rec.draw_probability, rec.away_probability = (
            round(p, 6) for p in probs)
    rec.has_ou = bool(ou_col and _has_value(row, ou_col))
    rec.has_btts = bool(btts_col and _has_value(row, btts_col))

    # "odd1/oddx/odd2" is the column spelling the captures actually use
    # (forebet, zulubet, betexplorer_odds); the others are alternates.
    rec.home_odds = _num(row, "odd1", "odds_home", "o1", "home_odds")
    rec.draw_odds = _num(row, "oddx", "odds_draw", "ox", "draw_odds")
    rec.away_odds = _num(row, "odd2", "odds_away", "o2", "away_odds")
    rec.has_price = any(v is not None for v in
                        (rec.home_odds, rec.draw_odds, rec.away_odds))
    if rec.has_price:
        rec.odds_source = str(row.get("provider") or source)
    for attr, key in (("price_evidence", "price_evidence"),
                      ("price_quarantine_reason", "price_quarantine_reason")):
        value = str(row.get(key) or "").strip()
        setattr(rec, attr, value or None)
    for attr, key in (("odds_replaced", "odds_replaced"),
                      ("price_push_eligible", "price_push_eligible")):
        raw = str(row.get(key) or "").strip().lower()
        if raw in {"true", "1", "yes"}:
            setattr(rec, attr, True)
        elif raw in {"false", "0", "no"}:
            setattr(rec, attr, False)

    reasons: list[str] = []
    if role == ROLE_ODDS_ONLY:
        reasons.append(B_ODDS_ONLY)
    elif role == ROLE_DONOR_ONLY:
        reasons.append(B_DONOR)
    elif role == ROLE_SHADOW_VOTER:
        reasons.append(B_TIER_NOT_DISPATCHABLE)
    elif role == ROLE_BLOCKED:
        reasons.append(B_NOT_CONSUMED)
    elif role == ROLE_NOT_A_VOTER:
        reasons.append(B_NO_1X2 if not rec.has_1x2 else B_TIER_NOT_DISPATCHABLE)
    if role in (ROLE_LIVE_VOTER,):
        if not rec.has_1x2:
            reasons.append(B_NO_1X2)
        if not rec.kickoff_trusted:
            reasons.append(B_NO_TRUSTED_KICKOFF)
        elif not rec.prematch_eligible:
            reasons.append(B_INSIDE_LEAD)
    rec.non_consumable_reasons = reasons
    rec.production_consumable = (role == ROLE_LIVE_VOTER and not reasons)
    return rec


# ---------------------------------------------------------------------------
# per source/day summary
# ---------------------------------------------------------------------------


def census_source_day(source: str, rows: list[dict], *, day: str, engine,
                      as_of: datetime, min_lead: int,
                      transport_failed: bool = False) -> dict:
    """Summarise one source on one date, plus every fixture it sees."""
    cap = source_registry.get(source)
    consumed = source in set(getattr(engine, "ALL_SOURCES", ()) or ())
    in_surface = source in set(getattr(engine, "SOURCES_1X2", ()) or ())
    role = production_role(source, raw_rows=len(rows),
                           consumed_by_engine=consumed,
                           in_consensus_surface=in_surface,
                           transport_failed=transport_failed)
    ou_col = (getattr(engine, "OU_COL", {}) or {}).get(source)
    btts_col = (getattr(engine, "BTTS_COL", {}) or {}).get(source)

    fixtures: dict[tuple[str, str], dict] = {}
    settled = short_key = no_identity = 0
    for row in rows:
        home, away = row.get("home"), row.get("away")
        if not home or not away:
            # e.g. betexplorer_odds is keyed by event_id with no team
            # columns, so it cannot be joined to a fixture at this layer.
            # That is a finding about price coverage, not an empty day.
            no_identity += 1
            continue
        if str(row.get("hs") or "").strip() not in {"", "None"}:
            settled += 1                     # finished match: not a surface
            continue
        key = (engine.source_team_key(home), engine.source_team_key(away))
        if len(key[0]) < 4 or len(key[1]) < 4:
            short_key += 1
            continue
        fixtures[key] = row

    records = [_fixture_record(source, row, day=day, engine=engine,
                              as_of=as_of, min_lead=min_lead, role=role,
                              ou_col=ou_col, btts_col=btts_col)
               for row in fixtures.values()]
    records.sort(key=lambda r: (r.kickoff_parsed or "~", r.raw_home))

    blockers: list[str] = []
    if not rows:
        blockers.append(B_TRANSPORT if transport_failed else B_NO_ROWS)
    if records and not any(r.has_1x2 for r in records):
        blockers.append(B_NO_1X2)
    if records and not any(r.kickoff_trusted for r in records):
        blockers.append(B_NO_TRUSTED_KICKOFF)
    if records and any(r.kickoff_trusted for r in records) and \
            not any(r.prematch_eligible for r in records):
        blockers.append(B_INSIDE_LEAD)
    if role == ROLE_SHADOW_VOTER:
        blockers.append(B_TIER_NOT_DISPATCHABLE)
    if role == ROLE_BLOCKED:
        blockers.append(B_NOT_CONSUMED)
    if role == ROLE_DONOR_ONLY:
        blockers.append(B_DONOR)
    if role == ROLE_ODDS_ONLY:
        blockers.append(B_ODDS_ONLY)
    if no_identity and not records:
        blockers.append(B_NO_IDENTITY_COLUMNS)
    # Settled rows and short identity keys are ordinary attrition; they are
    # reported as counts and only called blockers when they leave nothing.
    if settled and not records:
        blockers.append(B_SETTLED)
    if short_key and not records:
        blockers.append(B_IDENTITY_KEY)

    return {
        "event_date": day,
        "source": source,
        "production_role": role,
        "tier": cap.tier if cap else "unregistered",
        "markets": list(cap.markets) if cap else [],
        "ml_feature_provider": bool(cap and cap.ml_feature_provider),
        "provides_kickoff": bool(cap and cap.provides_kickoff),
        "consumed_by_pick_engine": consumed,
        "in_1x2_consensus_surface": in_surface,
        "raw_rows": len(rows),
        "fixture_count": len(records),
        "rows_with_1x2": sum(1 for r in records if r.has_1x2),
        "rows_with_ou": sum(1 for r in records if r.has_ou),
        "rows_with_btts": sum(1 for r in records if r.has_btts),
        "rows_with_kickoff_raw": sum(1 for r in records if r.kickoff_raw),
        "rows_with_parsed_kickoff": sum(1 for r in records if r.kickoff_trusted),
        "rows_with_trusted_kickoff": sum(1 for r in records if r.kickoff_trusted),
        "prematch_eligible_count": sum(1 for r in records if r.prematch_eligible),
        "rows_with_price": sum(1 for r in records if r.has_price),
        "already_settled_rows": settled,
        "identity_key_too_short": short_key,
        "rows_without_fixture_identity": no_identity,
        "blockers": sorted(set(blockers)),
        "fixtures": [r.as_dict() for r in records],
    }


# ---------------------------------------------------------------------------
# cross-source overlap — the number that actually explains a thin slate
# ---------------------------------------------------------------------------


def build_overlap(day_summaries: list[dict], *, day: str,
                  price_join_available: bool | None = None) -> list[dict]:
    """Group every source's fixtures by canonical key for one date.

    Raw source counts are misleading: 286 rows on one shadow source and 35
    on one live voter can still produce zero dispatchable fixtures if they
    never overlap. This is where that becomes visible.
    """
    if price_join_available is None:
        price_join_available = any(
            s["fixture_count"] for s in day_summaries
            if s["production_role"] == ROLE_ODDS_ONLY)
    groups: dict[str, dict] = {}
    for summary in day_summaries:
        role = summary["production_role"]
        for fx in summary["fixtures"]:
            key = fx["fixture_group_key"]
            group = groups.setdefault(key, {
                "event_date": day,
                "fixture_group_key": key,
                "fixture": f"{fx['raw_home']} vs {fx['raw_away']}",
                "league": fx.get("league"),
                "sources": [],
                "production_eligible_1x2_voters": [],
                "live_1x2_voters": [],
                "shadow_sources": [],
                "kickoff_sources": [],
                "odds_sources": [],
                "kickoffs": [],
            })
            group["sources"].append(summary["source"])
            # Quorum counts what the production lane counts: live and
            # shadow 1X2 predictors alike. live_1x2_voters is kept as a
            # subset so the shadow share of any quorum stays visible.
            if fx["has_1x2"] and selection_evidence.eligible_1x2_voters(
                    [summary["source"]]):
                group["production_eligible_1x2_voters"].append(
                    summary["source"])
                if role == ROLE_LIVE_VOTER:
                    group["live_1x2_voters"].append(summary["source"])
            if role in (ROLE_SHADOW_VOTER, ROLE_NOT_A_VOTER, ROLE_BLOCKED):
                group["shadow_sources"].append(summary["source"])
            if fx["kickoff_trusted"]:
                group["kickoff_sources"].append(summary["source"])
                group["kickoffs"].append(fx["kickoff_parsed"])
            if fx["has_price"]:
                group["odds_sources"].append(summary["source"])
            if fx.get("prematch_eligible"):
                group["prematch_eligible"] = True

    out = []
    for group in groups.values():
        for key in ("sources", "live_1x2_voters", "shadow_sources",
                    "kickoff_sources", "odds_sources"):
            group[key] = sorted(set(group[key]))
        group["production_eligible_1x2_voters"] = sorted(set(
            group["production_eligible_1x2_voters"]))
        group["voter_count_1x2"] = len(
            group["production_eligible_1x2_voters"])
        group["live_voter_count_1x2"] = len(group["live_1x2_voters"])
        group["quorum_met"] = group["voter_count_1x2"] >= 2
        group["ml_anchor_present"] = source_registry.has_ml_feature_support(
            group["sources"])
        group.setdefault("prematch_eligible", False)
        group["kickoff_trusted"] = bool(group["kickoff_sources"])
        group["has_price"] = bool(group["odds_sources"])
        # Diagnostic only: this is why the fixture cannot be a candidate. It
        # is never a licence to dispatch one that can.
        reasons = []
        if not group["quorum_met"]:
            reasons.append(D_FEWER_THAN_2_VOTERS)
        if len(group["sources"]) == 1:
            reasons.append(D_SINGLE_SOURCE)
        if not group["ml_anchor_present"]:
            reasons.append(D_NO_ML_ANCHOR)
        if not group["kickoff_trusted"]:
            reasons.append(D_MISSING_KICKOFF)
        elif not group["prematch_eligible"]:
            reasons.append(D_INSIDE_LEAD)
        if not group["has_price"] and price_join_available:
            # Silent when no pricing source can be joined at all: that is a
            # join-layer gap reported once, not 179 per-fixture verdicts.
            reasons.append(D_NO_PRICE)
        group["blockers"] = reasons
        group["dispatch_candidate"] = not reasons
        out.append(group)
    out.sort(key=lambda g: (-g["voter_count_1x2"], g["fixture"]))
    return out


def diagnose_thin_slate(overlap: list[dict], day_summaries: list[dict]) -> list[dict]:
    """Name the objective bottlenecks. Never recommend relaxing a gate."""
    total = len(overlap)
    findings: list[dict] = []

    def add(code: str, count: int, detail: str) -> None:
        if count:
            findings.append({"code": code, "fixtures_affected": count,
                             "detail": detail})

    add(D_FEWER_THAN_2_VOTERS,
        sum(1 for g in overlap if not g["quorum_met"]),
        "fixture is seen by fewer than 2 live 1X2 voters, so the consensus "
        "quorum cannot form")
    add(D_SINGLE_SOURCE,
        sum(1 for g in overlap if len(g["sources"]) == 1),
        "fixture appears on exactly one source, so nothing can corroborate it")
    add(D_NO_ML_ANCHOR,
        sum(1 for g in overlap if g["quorum_met"] and not g["ml_anchor_present"]),
        "fixture has quorum but carries no trained-feature provider, so "
        "ml-meta would score it off its calibrated distribution")
    add(D_MISSING_KICKOFF,
        sum(1 for g in overlap if not g["kickoff_trusted"]),
        "no source supplies a parseable kickoff, so the timing guard cannot "
        "clear the fixture")
    add(D_INSIDE_LEAD,
        sum(1 for g in overlap
            if g["kickoff_trusted"] and not g["prematch_eligible"]),
        "kickoff is inside the minimum lead or already passed at as_of")
    # Only call a fixture unpriced when a pricing source could in principle
    # have been joined to it. When every pricing source is identity-less on
    # this date, "no price" is a join-layer fact, not a per-fixture one.
    priced_sources = [s for s in day_summaries
                      if s["production_role"] == ROLE_ODDS_ONLY]
    joinable = [s for s in priced_sources if s["fixture_count"]]
    identity_less = [s for s in priced_sources
                     if s["raw_rows"] and not s["fixture_count"]]
    if joinable:
        add(D_NO_PRICE,
            sum(1 for g in overlap if not g["has_price"]),
            "no pricing source quotes this fixture, so no edge can be computed")
    elif identity_less:
        findings.append({
            "code": D_PRICE_JOIN_UNAVAILABLE,
            "fixtures_affected": len(overlap),
            "detail": "pricing rows exist ("
                      + ", ".join(f"{s['source']}={s['raw_rows']}"
                                  for s in identity_less)
                      + ") but carry no team columns, so they cannot be "
                        "joined to a fixture at this layer; price coverage "
                        "is unknown from this report alone",
        })

    blocked = sorted({s["source"] for s in day_summaries
                      if s["production_role"] in (ROLE_SHADOW_VOTER, ROLE_BLOCKED)
                      and s["fixture_count"]})
    if blocked:
        findings.append({
            "code": D_TIER_NOT_DISPATCHABLE,
            "fixtures_affected": sum(
                s["fixture_count"] for s in day_summaries
                if s["source"] in blocked),
            "detail": "rows captured from non-dispatchable tiers "
                      f"({', '.join(blocked)}); evidence decides promotion, "
                      "capture volume does not",
        })

    unavailable = sorted({s["source"] for s in day_summaries
                          if s["production_role"] == ROLE_UNAVAILABLE})
    if unavailable:
        findings.append({
            "code": "source_unavailable",
            "fixtures_affected": 0,
            "detail": f"no rows captured from {', '.join(unavailable)} on this "
                      "date; an absent source reduces coverage but is not "
                      "evidence of an empty fixture list",
        })
    for finding in findings:
        finding["share_of_fixtures"] = (
            round(finding["fixtures_affected"] / total, 4) if total else 0.0)
    return findings


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def horizon_dates(run_date: str, horizon_days: int) -> list[str]:
    start = datetime.strptime(run_date, "%Y-%m-%d").date()
    return [(start + timedelta(days=i)).isoformat()
            for i in range(max(1, horizon_days + 1))]


def build_census(*, run_date: str, localdata: Path, engine,
                 as_of: datetime, horizon_days: int = 2,
                 min_lead: int = DEFAULT_MIN_LEAD,
                 sources: tuple[str, ...] | None = None,
                 dispatch_plan: dict | None = None,
                 ticket_outcomes: dict | None = None,
                 ticket_status_is_current_run: bool = False) -> dict:
    """Read-only census of what every source sees on every covered date.

    ``ticket_status_is_current_run`` must stay False whenever the census
    runs ahead of auto_tickets: any status visible then belongs to an
    earlier run and is labelled as such.
    """
    localdata = Path(localdata)
    sources = sources or census_sources()
    dates = horizon_dates(run_date, horizon_days)

    per_date: dict[str, dict] = {}
    for day in dates:
        summaries = [
            census_source_day(source, load_day_rows(localdata, source, day),
                              day=day, engine=engine, as_of=as_of,
                              min_lead=min_lead)
            for source in sources
        ]
        overlap = build_overlap(summaries, day=day)
        per_date[day] = {
            "event_date": day,
            "sources": summaries,
            "fixture_groups": overlap,
            "diagnosis": diagnose_thin_slate(overlap, summaries),
            "totals": {
                "unique_fixture_groups": len(overlap),
                "live_voter_fixture_groups": sum(
                    1 for g in overlap if g["live_1x2_voters"]),
                "groups_with_quorum": sum(1 for g in overlap if g["quorum_met"]),
                "ml_scoreable_groups": sum(
                    1 for g in overlap
                    if g["quorum_met"] and g["ml_anchor_present"]),
                "prematch_eligible_ml_scoreable": sum(
                    1 for g in overlap
                    if g["quorum_met"] and g["ml_anchor_present"]
                    and g["prematch_eligible"]),
                "groups_with_price": sum(1 for g in overlap if g["has_price"]),
                "dispatch_candidates": sum(
                    1 for g in overlap if g["dispatch_candidate"]),
            },
        }

    # Annotate with what the production lane actually did, when available.
    plan = dispatch_plan or {}
    selections: dict[str, int] = {}
    for row in list(plan.get("same_day_picks") or []) + \
            list(plan.get("horizon_picks") or []):
        day = str(row.get("event_date") or row.get("date") or "")[:10]
        selections[day] = selections.get(day, 0) + 1
    for day, payload in per_date.items():
        payload["production_selections"] = selections.get(day, 0)
        payload["ticket_status"] = str(
            ((ticket_outcomes or {}).get(day) or {}).get("status") or "")

    return {
        "schema": "source_fixture_census/1",
        "ticket_status_is_current_run": bool(ticket_status_is_current_run),
        "run_date": run_date,
        "as_of": as_of.isoformat(),
        "min_lead_minutes": min_lead,
        "horizon_days": horizon_days,
        "dates": dates,
        "sources_covered": list(sources),
        "note": "Diagnostic only. This report cannot dispatch, promote, "
                "certify or enable any source. Captured rows are capture, "
                "not validation.",
        "per_date": per_date,
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return out


def render_markdown(census: dict) -> str:
    run_date = census["run_date"]
    lines = [
        f"# source fixture census — {run_date}",
        "",
        f"- run_date: {run_date}",
        f"- as_of: {census['as_of']}",
        f"- horizon dates covered: {', '.join(census['dates'])}",
        f"- minimum lead: {census['min_lead_minutes']} minutes",
        "",
        f"> {census['note']}",
        "",
        "## 1. Coverage by date",
        "",
    ]
    lines += _table(
        ["event_date", "fixture groups", "live-voter groups",
         ">=2 live 1X2 voters", "ML-scoreable", "pre-match eligible",
         "with price", "production selections", "ticket status"],
        [[d,
          p["totals"]["unique_fixture_groups"],
          p["totals"]["live_voter_fixture_groups"],
          p["totals"]["groups_with_quorum"],
          p["totals"]["ml_scoreable_groups"],
          p["totals"]["prematch_eligible_ml_scoreable"],
          p["totals"]["groups_with_price"],
          p.get("production_selections", 0),
          p.get("ticket_status") or "-"]
         for d, p in census["per_date"].items()])

    for day, payload in census["per_date"].items():
        lines += ["", f"## 2. {day} — per-source census", ""]
        lines += _table(
            ["source", "role", "tier", "raw rows", "fixtures", "1X2", "OU",
             "BTTS", "kickoff trusted", "pre-match", "price", "blockers"],
            [[s["source"], s["production_role"], s["tier"], s["raw_rows"],
              s["fixture_count"], s["rows_with_1x2"], s["rows_with_ou"],
              s["rows_with_btts"], s["rows_with_trusted_kickoff"],
              s["prematch_eligible_count"], s["rows_with_price"],
              ", ".join(s["blockers"]) or "-"]
             for s in payload["sources"]])

        groups = payload["fixture_groups"]
        lines += ["", f"### {day} — fixture overlap across sources", ""]
        if not groups:
            lines.append("_no fixtures seen by any source on this date._")
        else:
            lines += _table(
                ["fixture", "sources", "live 1X2 voters", "voters",
                 "ML anchor", "kickoff", "price", "blockers"],
                [[g["fixture"], ", ".join(g["sources"]) or "-",
                  ", ".join(g["live_1x2_voters"]) or "-",
                  g["voter_count_1x2"],
                  "yes" if g["ml_anchor_present"] else "no",
                  "yes" if g["kickoff_trusted"] else "no",
                  "yes" if g["has_price"] else "no",
                  ", ".join(g["blockers"]) or "-"]
                 for g in groups])

        lines += ["", f"### {day} — fixtures by source", ""]
        for summary in payload["sources"]:
            if not summary["fixtures"]:
                lines.append(
                    f"- **{summary['source']}** ({summary['production_role']}): "
                    f"no fixtures — {', '.join(summary['blockers']) or 'no rows'}")
                continue
            lines += ["", f"**{summary['source']}** "
                          f"({summary['production_role']}, "
                          f"{summary['fixture_count']} fixture(s))", ""]
            lines += _table(
                ["kickoff", "fixture", "markets", "consumable", "blockers"],
                [[f["kickoff_parsed"] or f["kickoff_raw"] or "-",
                  f"{f['raw_home']} vs {f['raw_away']}",
                  ", ".join(m for m, on in (("1X2", f["has_1x2"]),
                                            ("OU", f["has_ou"]),
                                            ("BTTS", f["has_btts"]),
                                            ("price", f["has_price"])) if on)
                  or "-",
                  "yes" if f["production_consumable"] else "no",
                  ", ".join(f["non_consumable_reasons"]) or "-"]
                 for f in summary["fixtures"]])

        lines += ["", f"### {day} — thin-slate diagnosis", ""]
        diagnosis = payload["diagnosis"]
        if not diagnosis:
            lines.append("_no objective bottleneck identified for this date._")
        else:
            lines += _table(
                ["bottleneck", "fixtures affected", "share", "detail"],
                [[f["code"], f["fixtures_affected"],
                  f"{f['share_of_fixtures']:.0%}", f["detail"]]
                 for f in diagnosis])
        lines += ["", "_Gates are not to be relaxed on the strength of this "
                      "report: it explains coverage, it does not license "
                      "dispatch._"]
    return "\n".join(lines) + "\n"


CSV_FIELDS = [
    "event_date", "source", "production_role", "raw_home", "raw_away",
    "normalized_home", "normalized_away", "league", "kickoff_raw",
    "kickoff_parsed", "kickoff_trusted", "has_1x2", "has_ou", "has_btts",
    "has_price", "home_probability", "draw_probability", "away_probability",
    "home_odds", "draw_odds", "away_odds", "odds_source",
    "prematch_eligible", "production_consumable", "non_consumable_reasons",
    "fixture_group_key",
]


def render_csv_rows(census: dict) -> list[dict]:
    rows = []
    for payload in census["per_date"].values():
        for summary in payload["sources"]:
            for fx in summary["fixtures"]:
                row = {k: fx.get(k) for k in CSV_FIELDS if k in fx}
                row["production_role"] = summary["production_role"]
                row["non_consumable_reasons"] = ";".join(
                    fx.get("non_consumable_reasons") or ())
                rows.append({k: row.get(k, "") for k in CSV_FIELDS})
    return rows


# ---------------------------------------------------------------------------
# operator log rendering
#
# The artifacts are complete, but an operator reading a GitHub Actions run
# should not have to download anything to see what each source said. These
# helpers emit the same data as a grouped, line-per-fixture log.
# ---------------------------------------------------------------------------

LOG_TITLE = "SOURCE FIXTURE CENSUS — DIAGNOSTIC ONLY"
LOG_NOTE = ("read-only source visibility; this report does not create picks "
            "or tickets")
CHUNK_LINES = 200


def _fmt(value: Any) -> str:
    """Absent means absent. Never render a guess as a value."""
    if value is None or value == "" or value == []:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, (list, tuple)):
        return ",".join(str(v) for v in value)
    return str(value)


def _aligned(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    out = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)).rstrip()]
    for row in rows:
        out.append("  ".join(c.ljust(widths[i])
                             for i, c in enumerate(row)).rstrip())
    return out


def fixture_log_line(index: int, fixture: dict) -> str:
    """One fixture, one line, every field the source actually supplied."""
    markets = [name for name, key in (("1x2", "has_1x2"), ("ou", "has_ou"),
                                      ("btts", "has_btts"),
                                      ("price", "has_price"))
               if fixture.get(key)]
    probs = "/".join(_fmt(fixture.get(k)) for k in
                     ("home_probability", "draw_probability",
                      "away_probability"))
    odds = "/".join(_fmt(fixture.get(k)) for k in
                    ("home_odds", "draw_odds", "away_odds"))
    parts = [
        f"{index:03d}",
        _fmt(fixture.get("event_date")),
        _fmt(fixture.get("source")),
        f'ko_raw="{_fmt(fixture.get("kickoff_raw"))}"',
        f"ko_parsed={_fmt(fixture.get('kickoff_parsed'))}",
        f"trusted={_fmt(bool(fixture.get('kickoff_trusted')))}",
        f'league="{_fmt(fixture.get("league"))}"',
        f'raw="{_fmt(fixture.get("raw_home"))}" vs "{_fmt(fixture.get("raw_away"))}"',
        f'norm="{_fmt(fixture.get("normalized_home"))}" vs '
        f'"{_fmt(fixture.get("normalized_away"))}"',
        f"group={_fmt(fixture.get('fixture_group_key'))}",
        f"markets={','.join(markets) if markets else 'none'}",
        f"p={probs}",
        f"tip={_fmt(fixture.get('tip'))}",
        f"proj={_fmt(fixture.get('projected_score'))}",
        f"odds={odds}",
        f"odds_src={_fmt(fixture.get('odds_source'))}",
        f"price_ev={_fmt(fixture.get('price_evidence'))}",
        f"price_quar={_fmt(fixture.get('price_quarantine_reason'))}",
        f"odds_replaced={_fmt(fixture.get('odds_replaced'))}",
        f"price_push={_fmt(fixture.get('price_push_eligible'))}",
        f"consumable={_fmt(bool(fixture.get('production_consumable')))}",
        f"reasons={_fmt(fixture.get('non_consumable_reasons'))}",
        f"file={_fmt(fixture.get('source_file'))}",
    ]
    return " | ".join(parts)


def _ticket_status_label(census: dict, payload: dict) -> str:
    """Never present a stale status as this run's outcome.

    The census runs before auto_tickets, so any ticket status it can see
    was written by an earlier run. Reporting it bare would let a previous
    decline read as the current verdict.
    """
    status = payload.get("ticket_status")
    if not status:
        return "pending_auto_tickets"
    if census.get("ticket_status_is_current_run"):
        return str(status)
    return f"previous_status:{status}"


def render_log(census: dict, *, group_markers: bool = True,
               artifact_paths: list[str] | None = None) -> list[str]:
    """Render the whole census as operator-readable log lines.

    Every fixture of every source is emitted. Nothing is sampled: the
    emitted/omitted counters are printed so a truncation could never pass
    unnoticed.
    """
    out: list[str] = []
    add = out.append

    def group(title: str):
        if group_markers:
            add(f"::group::{title}")
        else:
            add(title)

    def endgroup():
        if group_markers:
            add("::endgroup::")

    # -- 1. header ---------------------------------------------------------
    add(LOG_TITLE)
    add(f"run_date: {census['run_date']}")
    add(f"as_of: {census['as_of']}")
    add(f"dates covered: {', '.join(census['dates'])}")
    add(f"min_lead: {census.get('min_lead_minutes', DEFAULT_MIN_LEAD)} minutes")
    add(f"note: {LOG_NOTE}")
    add("")

    # -- 2. date summary ---------------------------------------------------
    add("DATE SUMMARY")
    headers = ["event_date", "raw_rows", "fixture_groups", "live_groups",
               "quorum_2plus", "ml_scoreable", "prematch_ml", "selections",
               "auto_ticket"]
    rows = []
    for day in census["dates"]:
        payload = census["per_date"][day]
        totals = payload["totals"]
        rows.append([
            day,
            str(sum(s["raw_rows"] for s in payload["sources"])),
            str(totals["unique_fixture_groups"]),
            str(totals["live_voter_fixture_groups"]),
            str(totals["groups_with_quorum"]),
            str(totals["ml_scoreable_groups"]),
            str(totals["prematch_eligible_ml_scoreable"]),
            str(payload.get("production_selections", 0)),
            _fmt(_ticket_status_label(census, payload)),
        ])
    out.extend("  " + line for line in _aligned(headers, rows))
    add("")

    rows_total = rows_emitted = 0

    for day in census["dates"]:
        payload = census["per_date"][day]

        # -- 3. per-source summary ----------------------------------------
        group(f"SOURCE SUMMARY {day}")
        headers = ["source", "role", "tier", "raw_rows", "fixtures", "1x2",
                   "ou", "btts", "price", "ko_raw", "ko_parsed", "ko_trusted",
                   "prematch", "blockers"]
        srows = []
        for summary in payload["sources"]:
            srows.append([
                summary["source"], summary["production_role"],
                _fmt(summary.get("tier")),
                str(summary["raw_rows"]), str(summary["fixture_count"]),
                str(summary["rows_with_1x2"]), str(summary["rows_with_ou"]),
                str(summary["rows_with_btts"]),
                str(summary.get("rows_with_price", 0)),
                str(summary["rows_with_kickoff_raw"]),
                str(summary["rows_with_parsed_kickoff"]),
                str(summary["rows_with_trusted_kickoff"]),
                str(summary["prematch_eligible_count"]),
                _fmt(summary["blockers"]),
            ])
        out.extend("  " + line for line in _aligned(headers, srows))
        endgroup()

        # -- 4. full per-source fixture list ------------------------------
        for summary in payload["sources"]:
            source = summary["source"]
            fixtures = summary.get("fixtures") or []
            rows_total += len(fixtures)

            if not fixtures:
                # A source with no fixtures is stated outright, with its
                # reason. Silence is how a coverage gap stays invisible.
                reason = (summary["blockers"] or ["unknown"])[0]
                line = (f"  {source} | date={day} | rows="
                        f"{summary['raw_rows']} | fixture_count=0 | "
                        f"reason={reason}")
                if summary.get("rows_without_fixture_identity"):
                    line += " | price_coverage=unknown"
                group(f"SOURCE FIXTURES {day} {source} (0 fixtures)")
                add(line)
                endgroup()
                continue

            for start in range(0, len(fixtures), CHUNK_LINES):
                chunk = fixtures[start:start + CHUNK_LINES]
                suffix = ""
                if len(fixtures) > CHUNK_LINES:
                    suffix = (f" [{start + 1}-{start + len(chunk)} of "
                              f"{len(fixtures)}]")
                group(f"SOURCE FIXTURES {day} {source}"
                      f" ({len(fixtures)} fixtures){suffix}")
                for offset, fixture in enumerate(chunk):
                    add("  " + fixture_log_line(start + offset + 1, fixture))
                    rows_emitted += 1
                endgroup()

        # -- 5. overlap / quorum ------------------------------------------
        group(f"FIXTURE OVERLAP {day}")
        if not payload["fixture_groups"]:
            add(f"  {day} | no fixture groups on this date")
        for grp in payload["fixture_groups"]:
            add(f"  {day} | {grp['fixture']}")
            add(f"    sources: {_fmt(grp['sources'])}")
            add(f"    live_1x2_voters: {_fmt(grp['live_1x2_voters'])}")
            add(f"    shadow_sources: {_fmt(grp.get('shadow_sources'))}")
            add(f"    odds_sources: {_fmt(grp.get('odds_sources'))}")
            add(f"    kickoff_sources: {_fmt(grp.get('kickoff_sources'))}")
            add(f"    voter_count_1x2: {grp['voter_count_1x2']}")
            add(f"    ml_anchor_present: {_fmt(bool(grp['ml_anchor_present']))}")
            add(f"    prematch_eligible: "
                f"{_fmt(bool(grp.get('prematch_eligible')))}")
            candidate = bool(grp.get("dispatch_candidate"))
            add(f"    production_candidate: {_fmt(candidate)}")
            # Status is derived from what the census observed, never
            # asserted: a candidate is a candidate, not a selection.
            status = grp.get("production_status")
            if not status:
                status = "dispatch_candidate" if candidate else "blocked"
            add(f"    production_status: {_fmt(status)}")
            if grp.get("blockers"):
                add(f"    blocker: {_fmt(grp['blockers'])}")
            if grp.get("auto_ticket_status"):
                add(f"    auto_ticket_status: "
                    f"{_fmt(_ticket_status_label(census, grp))}")
        endgroup()

        # -- 6. thin-slate diagnosis --------------------------------------
        add(f"THIN-SLATE DIAGNOSIS {day}")
        total_groups = payload["totals"]["unique_fixture_groups"]
        raw_rows = sum(s["raw_rows"] for s in payload["sources"])
        if raw_rows == 0:
            add("  - no rows were captured from any source on this date")
        else:
            add(f"  - rows were present ({raw_rows}); "
                "this was not a total outage")
        for finding in payload["diagnosis"]:
            share = (f" ({finding['fixtures_affected'] * 100 // total_groups}%)"
                     if total_groups else "")
            add(f"  - {finding['code']}: {finding['fixtures_affected']}"
                f"/{total_groups}{share} — {finding['detail']}")
        add(f"  - production selections: "
            f"{payload.get('production_selections', 0)}")
        add(f"  - auto_tickets: {_ticket_status_label(census, payload)}")
        add("  - gates are not to be relaxed on the strength of this report; "
            "it explains coverage, it does not license dispatch")
        add("")

    # -- completeness accounting ------------------------------------------
    omitted = rows_total - rows_emitted
    add("CENSUS COMPLETENESS")
    add(f"  rows_total: {rows_total}")
    add(f"  rows_emitted: {rows_emitted}")
    add(f"  rows_omitted: {omitted}")
    if omitted:
        add("  WARNING: fixture rows were omitted from the log; the JSON "
            "artifact is the complete record")
    if artifact_paths:
        add("  artifacts:")
        for path in artifact_paths:
            add(f"    {path}")
    return out
