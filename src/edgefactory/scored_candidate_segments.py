"""Segment analysis for the scored-candidate shadow ledger — AUDIT ONLY.

Turns the graded shadow ROI into an actionable, anti-overfit promotion map:
which scored-but-not-promoted segments made money, under which price class,
how robust the evidence is, and what the recommended (NON-LIVE) action is.

Doctrine:

* AUDIT RECOMMENDATION — NOT LIVE STAKING LOGIC. Nothing here changes
  ticket selection, staking, source eligibility, gates, vetoes, matching or
  freeze behavior. "Promotion candidate" is a label on a report, never an
  executed behavior change.
* Reads persisted ledger data only (via
  :func:`scored_candidate_shadow.build_report`): no new prices are fetched,
  no later odds are backfilled, no historical event is mutated.
* Two ROI populations are kept strictly separate:
  - ``captured_price_shadow``: fixture-level records graded at the odds the
    scorer saw (stale/unregistered/donor allowed and labelled; fair/model
    confined to its own price-kind value) — audit-only, never stakeable.
  - ``execution_safe``: candidate-level records that passed the strict
    named-book execution-safety gate. Only this population can ever yield
    an EXECUTION_SAFE_PROMOTION_CANDIDATE.
* Flat-stake convention inherited from the ledger: win=odds-1, loss=-1,
  void=0; pending/unmatched/no-price/no-selection/post-kickoff/timestamp-
  unknown are EXCLUDED — never losses.
* Anti-overfit: configurable sample thresholds, day/fixture/source
  concentration checks, stale-only-profit detection and a conservative
  lower confidence bound. These are promotion-candidate guards, not claims
  of statistical finality.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from . import scored_candidate_shadow as scs

ROI_CAPTURED = "captured_price_shadow"
ROI_EXEC_SAFE = "execution_safe"

TIER_BLOCKED = "BLOCKED_NEGATIVE"
TIER_INSUFFICIENT = "INSUFFICIENT_SAMPLE"
TIER_WATCHLIST = "WATCHLIST_POSITIVE"
TIER_PRICE_ENRICH = "PRICE_ENRICHMENT_CANDIDATE"
TIER_SHADOW_PROMO = "SHADOW_PROMOTION_CANDIDATE"
TIER_EXEC_PROMO = "EXECUTION_SAFE_PROMOTION_CANDIDATE"

ACTION_BY_TIER = {
    TIER_BLOCKED: ("KEEP_BLOCKED",
                   "negative ROI after settlement."),
    TIER_INSUFFICIENT: ("COLLECT_MORE_EVIDENCE",
                        "sample below audit thresholds; no action."),
    TIER_WATCHLIST: ("WATCH",
                     "positive but small/concentrated/stale-driven; keep "
                     "watching, do not promote."),
    TIER_PRICE_ENRICH: ("PRICE_ENRICHMENT",
                        "positive captured-price ROI, but lacks "
                        "execution-safe named-book coverage. Do not promote "
                        "to staking. Improve exact named-book capture for "
                        "this segment."),
    TIER_SHADOW_PROMO: ("PROMOTION_REVIEW_AUDIT_PRICES_ONLY",
                        "robust positive captured-price ROI on audit-only "
                        "prices; candidate for review/price-enrichment "
                        "work, NOT eligible for direct ticket promotion."),
    TIER_EXEC_PROMO: ("PROMOTION_REVIEW",
                      "execution-safe segment has positive ROI across "
                      "enough days. Candidate for a FUTURE ticket-builder "
                      "promotion proposal — no live behavior changed."),
}
ACTION_STALE_ARTIFACT = ("WATCH_STALE_ARTIFACT",
                         "ROI positive only under stale audit prices. Do "
                         "not promote until fresh/execution-safe evidence "
                         "confirms.")
ACTION_MATERIALIZATION_AUDIT = (
    "CANDIDATE_MATERIALIZATION_AUDIT",
    "scorer has positive fixture signal but records lack a gradeable "
    "candidate/price. Inspect why no operational candidate was emitted.")

AUDIT_BANNER = "AUDIT RECOMMENDATION — NOT LIVE STAKING LOGIC"
NO_BEHAVIOR_LINE = ("No live betting behavior changed. Promotion requires "
                    "separate explicit implementation and review.")

# ------------------------------------------------------------------- bands --
# Fixed, documented bands (deterministic across windows; quantile banding
# would re-draw boundaries per window and make segments non-comparable).
_ODDS_BANDS = ((1.30, "<1.30"), (1.50, "1.30-1.49"), (1.80, "1.50-1.79"),
               (2.20, "1.80-2.19"), (3.00, "2.20-2.99"))
_PROB_BANDS = ((0.50, "<0.50"), (0.60, "0.50-0.59"), (0.70, "0.60-0.69"),
               (0.80, "0.70-0.79"), (0.90, "0.80-0.89"))
_SCORE_BANDS = ((0.5, "<0.5"), (1.0, "0.5-0.99"), (2.0, "1.0-1.99"))


def odds_band(odds: object) -> str:
    try:
        o = float(odds)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "unknown"
    for limit, label in _ODDS_BANDS:
        if o < limit:
            return label
    return "3.00+"


def probability_band(p: object) -> str:
    try:
        v = float(p)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "unknown"
    for limit, label in _PROB_BANDS:
        if v < limit:
            return label
    return "0.90+"


def score_band(s: object) -> str:
    try:
        v = float(s)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "unknown"
    for limit, label in _SCORE_BANDS:
        if v < limit:
            return label
    return "2.0+"


def price_age_band(age_s: object) -> str:
    try:
        v = int(age_s)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "unknown"
    if v <= 0:
        return "fetched_this_run"
    if v <= 600:
        return "<=10m"
    if v <= 3600:
        return "<=1h"
    return ">1h"


def weekday_of(day10: str) -> str:
    try:
        return datetime.strptime(str(day10)[:10], "%Y-%m-%d").strftime("%a")
    except ValueError:
        return "unknown"


def date_range(day_from: str, day_to: str) -> list[str]:
    start = datetime.strptime(str(day_from)[:10], "%Y-%m-%d")
    end = datetime.strptime(str(day_to)[:10], "%Y-%m-%d")
    if end < start:
        start, end = end, start
    out = []
    cur = start
    while cur <= end:
        out.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return out


# ------------------------------------------------------------ record model --
def _promotion_state(promoted: bool, ticketed: bool) -> str:
    if ticketed:
        return "ticketed"
    if promoted:
        return "promoted_not_ticketed"
    return "scored_not_promoted"


def _fixture_record(f: Mapping[str, Any], day: str,
                    exec_safe_fids: set[str]) -> dict[str, Any]:
    gradeable = bool(f.get("shadow_price_gradeable"))
    status = f.get("settlement_status")
    odds = f.get("captured_odds")
    ret = (scs.flat_stake_return(str(status), odds) if gradeable else None)
    return {
        "roi_type": ROI_CAPTURED,
        "date": day,
        "weekday": weekday_of(day),
        "fixture_id": str(f.get("fixture_id") or ""),
        "promotion_state": _promotion_state(bool(f.get("promoted")),
                                            bool(f.get("ticketed"))),
        "reasons": list(f.get("audit_reason_codes") or ["unknown"]),
        "bucket": f.get("bucket"),
        "rule_model": f.get("kind"),
        "market": f.get("market"),
        "selection_side": f.get("selection_side"),
        "league": f.get("league"),
        "competition_key": f.get("league_key"),
        "country": f.get("country"),
        "price_source": f.get("shadow_price_source"),
        "bookmaker": f.get("shadow_price_bookmaker"),
        "price_kind": f.get("shadow_price_kind"),
        "stale": f.get("shadow_price_stale"),
        "registered_source": bool(f.get("shadow_price_registered_source")),
        "execution_safe": False,            # fixture shadow prices, always
        "gradeable": gradeable,
        "gradeable_reason": f.get("shadow_price_gradeable_reason"),
        "kickoff_proof": f.get("shadow_price_pre_kickoff_basis"),
        "odds_band": odds_band(odds) if gradeable else "unknown",
        "probability_band": probability_band(f.get("ml_probability")),
        "score_band": score_band(f.get("score")),
        "price_age_band": price_age_band(f.get("shadow_price_age_seconds")),
        "odds": odds,
        "status": status,
        "ret": ret,
        "exec_safe_support": str(f.get("fixture_id") or "") in exec_safe_fids,
    }


def _candidate_record(c: Mapping[str, Any], day: str) -> dict[str, Any]:
    status = c.get("settlement_status")
    odds = c.get("captured_odds")
    return {
        "roi_type": ROI_EXEC_SAFE,
        "date": day,
        "weekday": weekday_of(day),
        "fixture_id": str(c.get("fixture_id") or ""),
        "promotion_state": _promotion_state(bool(c.get("selected_as_pick")),
                                            bool(c.get("selected_on_ticket"))),
        "reasons": [str(r.get("code") or "unknown")
                    for r in (c.get("rejection_reasons") or [])] or ["none"],
        "bucket": c.get("bucket"),
        "rule_model": c.get("rule"),
        "market": c.get("market"),
        "selection_side": c.get("selection_side"),
        "league": c.get("league"),
        "competition_key": c.get("league_key"),
        "country": c.get("country"),
        "price_source": c.get("captured_price_source"),
        "bookmaker": c.get("captured_bookmaker"),
        "price_kind": c.get("price_odds_kind") or "named_book",
        "stale": False,                     # pre-kickoff proven by the gate
        "registered_source": bool(c.get("source_registered")),
        "execution_safe": True,
        "gradeable": True,
        "gradeable_reason": "execution_safe_named_book",
        "kickoff_proof": "instants_proven",
        "odds_band": odds_band(odds),
        "probability_band": probability_band(c.get("probability")),
        "score_band": score_band(c.get("score")),
        "price_age_band": "unknown",
        "odds": odds,
        "status": status,
        "ret": scs.flat_stake_return(str(status), odds),
        "exec_safe_support": True,
    }


def collect_records(days: Sequence[str], *, root: Path | None = None,
                    settled: Mapping[tuple, str] | None = None,
                    all_runs: bool = False) -> dict[str, Any]:
    """Flatten per-day shadow reports into segment-ready records.

    Reads persisted ledgers only (via build_report); days with no ledger
    file contribute nothing and are listed in ``days_without_ledger``.
    """
    captured: list[dict[str, Any]] = []
    exec_safe: list[dict[str, Any]] = []
    days_with, days_without = [], []
    for day in days:
        report = scs.build_report(day, root=root, settled=settled,
                                  all_runs=all_runs)
        fixtures = report.get("fixtures") or []
        candidates = report.get("candidates") or []
        if not fixtures and not candidates:
            days_without.append(day)
            continue
        days_with.append(day)
        exec_fids = {str(c.get("fixture_id") or "") for c in candidates
                     if c.get("execution_safe_named_book_eligible")}
        for f in fixtures:
            captured.append(_fixture_record(f, day, exec_fids))
        for c in candidates:
            if c.get("execution_safe_named_book_eligible"):
                exec_safe.append(_candidate_record(c, day))
    return {"captured": captured, "exec_safe": exec_safe,
            "days_requested": list(days), "days_with_ledger": days_with,
            "days_without_ledger": days_without}


# ------------------------------------------------------------- dimensions --
SINGLE_DIMENSIONS: tuple[str, ...] = (
    "promotion_state", "reason", "bucket", "rule_model", "market",
    "selection_side", "league", "competition_key", "country", "price_source",
    "bookmaker", "price_kind", "stale", "registered_source", "execution_safe",
    "gradeable_reason", "kickoff_proof", "odds_band", "probability_band",
    "score_band", "price_age_band", "trading_date", "weekday",
)
# Controlled compound pairs only (depth 2): unconstrained high-dimensional
# mining manufactures overfit segments by the thousand.
COMPOUND_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("reason", "bucket"), ("reason", "price_kind"), ("reason", "price_source"),
    ("bucket", "odds_band"), ("league", "bucket"), ("price_source", "stale"),
    ("price_source", "kickoff_proof"), ("execution_safe", "reason"),
    ("promotion_state", "bucket"),
)


def _dim_values(rec: Mapping[str, Any], dim: str) -> list[str]:
    if dim == "reason":
        return [str(v) for v in (rec.get("reasons") or ["unknown"])]
    if dim == "trading_date":
        return [str(rec.get("date"))]
    value = rec.get(dim)
    if value is None:
        return ["unknown"]
    if isinstance(value, bool):
        return [str(value).lower()]
    return [str(value)]


# --------------------------------------------------------------- segments --
def _seg_blank() -> dict[str, Any]:
    return {
        "total_records": 0, "gradeable_records": 0, "settled_records": 0,
        "wins": 0, "losses": 0, "voids": 0, "pending": 0, "unmatched": 0,
        "excluded_no_selection": 0, "excluded_no_price": 0,
        "excluded_post_kickoff": 0, "excluded_timestamp_unknown": 0,
        "flat_profit_units": 0.0, "flat_roi": None,
        "average_odds": None, "median_odds": None,
        "min_odds": None, "max_odds": None,
        "distinct_days": 0, "distinct_fixtures": 0, "distinct_leagues": 0,
        "distinct_sources": 0, "stale_count": 0, "fresh_count": 0,
        "execution_safe_count": 0, "captured_price_only_count": 0,
        "_odds": [], "_rets": [],
        "_days": set(), "_fixtures": set(), "_leagues": set(),
        "_sources": set(),
        "_day_settled": defaultdict(int), "_day_profit": defaultdict(float),
        "_fixture_settled": defaultdict(int),
        "_source_settled": defaultdict(int),
        "_source_profit": defaultdict(float),
        "_league_settled": defaultdict(int),
        "_stale_profit": 0.0, "_fresh_profit": 0.0,
    }


_EXCLUDED_KEY = {
    "no_selection_intent_available": "excluded_no_selection",
    "no_captured_price": "excluded_no_price",
    "post_kickoff_price": "excluded_post_kickoff",
    "price_timestamp_unknown": "excluded_timestamp_unknown",
}


def _seg_add(seg: dict[str, Any], rec: Mapping[str, Any]) -> None:
    seg["total_records"] += 1
    seg["_days"].add(rec["date"])
    if rec.get("fixture_id"):
        seg["_fixtures"].add(rec["fixture_id"])
    if rec.get("league"):
        seg["_leagues"].add(str(rec["league"]))
    src = rec.get("price_source")
    if src:
        seg["_sources"].add(str(src))
    if rec.get("execution_safe"):
        seg["execution_safe_count"] += 1
    elif rec.get("gradeable"):
        seg["captured_price_only_count"] += 1
    if not rec.get("gradeable"):
        key = _EXCLUDED_KEY.get(str(rec.get("gradeable_reason")))
        if key:
            seg[key] += 1
        return
    seg["gradeable_records"] += 1
    if rec.get("stale") is True:
        seg["stale_count"] += 1
    elif rec.get("stale") is False:
        seg["fresh_count"] += 1
    status = rec.get("status")
    if status == scs.SETTLE_PENDING:
        seg["pending"] += 1
        return
    if status == scs.SETTLE_UNMATCHED:
        seg["unmatched"] += 1
        return
    ret = rec.get("ret")
    if ret is None:
        seg["excluded_no_price"] += 1
        return
    seg["settled_records"] += 1
    seg["_rets"].append(float(ret))
    if rec.get("odds") is not None:
        seg["_odds"].append(float(rec["odds"]))
    if status == scs.SETTLE_WIN:
        seg["wins"] += 1
    elif status == scs.SETTLE_LOSS:
        seg["losses"] += 1
    elif status == scs.SETTLE_VOID:
        seg["voids"] += 1
    seg["flat_profit_units"] = round(seg["flat_profit_units"] + float(ret), 6)
    day, fid = str(rec["date"]), str(rec.get("fixture_id") or "unknown")
    seg["_day_settled"][day] += 1
    seg["_day_profit"][day] += float(ret)
    seg["_fixture_settled"][fid] += 1
    seg["_source_settled"][str(src or "unknown")] += 1
    seg["_source_profit"][str(src or "unknown")] += float(ret)
    seg["_league_settled"][str(rec.get("league") or "unknown")] += 1
    if rec.get("stale") is True:
        seg["_stale_profit"] += float(ret)
    else:
        seg["_fresh_profit"] += float(ret)


def _seg_close(seg: dict[str, Any]) -> dict[str, Any]:
    n = seg["settled_records"]
    if n > 0:
        seg["flat_roi"] = round(seg["flat_profit_units"] / n, 6)
    odds = sorted(seg.pop("_odds"))
    if odds:
        seg["average_odds"] = round(sum(odds) / len(odds), 4)
        mid = len(odds) // 2
        seg["median_odds"] = round(
            odds[mid] if len(odds) % 2 else (odds[mid - 1] + odds[mid]) / 2, 4)
        seg["min_odds"], seg["max_odds"] = round(odds[0], 4), round(odds[-1], 4)
    seg["distinct_days"] = len(seg.pop("_days"))
    seg["distinct_fixtures"] = len(seg.pop("_fixtures"))
    seg["distinct_leagues"] = len(seg.pop("_leagues"))
    seg["distinct_sources"] = len(seg.pop("_sources"))

    rets = seg.pop("_rets")
    day_settled = dict(seg.pop("_day_settled"))
    day_profit = dict(seg.pop("_day_profit"))
    fixture_settled = dict(seg.pop("_fixture_settled"))
    source_settled = dict(seg.pop("_source_settled"))
    source_profit = dict(seg.pop("_source_profit"))
    league_settled = dict(seg.pop("_league_settled"))
    stale_profit = seg.pop("_stale_profit")
    fresh_profit = seg.pop("_fresh_profit")

    day_rois = {d: day_profit[d] / c for d, c in day_settled.items() if c}
    lcb = None
    if n >= 2:
        mean = sum(rets) / n
        var = sum((r - mean) ** 2 for r in rets) / (n - 1)
        lcb = round(mean - 1.645 * math.sqrt(var / n), 6)
    elif n == 1:
        lcb = None  # one settled record proves nothing; stated, not faked
    seg["confidence"] = {
        "lower_confidence_bound_roi": lcb,
        "worst_day_roi": (round(min(day_rois.values()), 6)
                          if day_rois else None),
        "positive_days": sum(1 for v in day_rois.values() if v > 0),
        "settled_days": len(day_rois),
        "max_day_concentration": (round(max(day_settled.values()) / n, 6)
                                  if n else None),
        "max_fixture_concentration": (round(max(fixture_settled.values()) / n,
                                            6) if n else None),
        "max_source_concentration": (round(max(source_settled.values()) / n,
                                           6) if n else None),
        "max_league_concentration": (round(max(league_settled.values()) / n,
                                           6) if n else None),
        "stale_profit_units": round(stale_profit, 6),
        "fresh_profit_units": round(fresh_profit, 6),
        "top_source_profit_share": (
            round(max(source_profit.values()) / seg["flat_profit_units"], 6)
            if source_profit and seg["flat_profit_units"] > 0 else None),
    }
    return seg


def build_segments(records: Sequence[Mapping[str, Any]],
                   dims: Iterable[object]) -> dict[str, dict[str, Any]]:
    """Group records into segments keyed by ``dim=value[|dim=value]``."""
    segments: dict[str, dict[str, Any]] = {}
    dim_list = [(d,) if isinstance(d, str) else tuple(d) for d in dims]
    for rec in records:
        for dim_tuple in dim_list:
            value_lists = [_dim_values(rec, d) for d in dim_tuple]
            combos: list[list[str]] = [[]]
            for values in value_lists:
                combos = [c + [v] for c in combos for v in values]
            for combo in combos:
                key = "|".join(f"{d}={v}" for d, v in zip(dim_tuple, combo))
                seg = segments.setdefault(key, _seg_blank())
                _seg_add(seg, rec)
                seg["_dims"] = dict(zip(dim_tuple, combo))
    out = {}
    for key, seg in segments.items():
        dims_map = seg.pop("_dims")
        closed = _seg_close(seg)
        closed["segment_key"] = key
        closed["dimensions"] = dims_map
        out[key] = closed
    return out


# ------------------------------------------------------------------ tiers --
def classify_segment(seg: Mapping[str, Any], *, roi_type: str,
                     min_settled: int = 30, min_days: int = 3,
                     min_fixtures: int = 20, watch_min_settled: int = 10,
                     max_day_concentration: float = 0.6,
                     max_fixture_concentration: float = 0.5,
                     max_pending_share: float = 0.5,
                     ) -> dict[str, Any]:
    """Assign a promotion-readiness tier + action + warnings to a segment.

    Deterministic, documented decision tree — promotion candidates, not
    proven edges. Only ``execution_safe`` segments can ever reach
    EXECUTION_SAFE_PROMOTION_CANDIDATE; captured-price segments top out at
    SHADOW_PROMOTION_CANDIDATE / PRICE_ENRICHMENT_CANDIDATE by design.
    """
    warnings: list[str] = []
    settled = int(seg["settled_records"])
    roi = seg.get("flat_roi")
    conf = seg.get("confidence") or {}
    if roi_type == ROI_CAPTURED:
        warnings.append("audit_only_prices")
        if not seg.get("execution_safe_count"):
            warnings.append("not_execution_safe")
    gradeable = int(seg.get("gradeable_records") or 0)
    open_share = ((seg["pending"] + seg["unmatched"]) / gradeable
                  if gradeable else 0.0)
    if open_share > max_pending_share:
        warnings.append("high_pending_unmatched_share")
    stale_only = (seg["flat_profit_units"] > 0
                  and conf.get("stale_profit_units", 0.0) > 0
                  and conf.get("fresh_profit_units", 0.0) <= 0)
    if stale_only:
        warnings.append("stale_only_profit")
    day_conc = conf.get("max_day_concentration")
    fix_conc = conf.get("max_fixture_concentration")
    concentrated = ((day_conc is not None and day_conc > max_day_concentration
                     and settled > 1)
                    or (fix_conc is not None
                        and fix_conc > max_fixture_concentration
                        and settled > 1))
    if concentrated:
        warnings.append("concentration_day_or_fixture")
    src_share = conf.get("top_source_profit_share")
    if (src_share is not None and src_share >= 0.95
            and seg.get("distinct_sources", 0) > 1):
        warnings.append("single_source_profit_dominance")

    if settled == 0 or roi is None:
        tier = TIER_INSUFFICIENT
    elif roi <= 0:
        tier = TIER_BLOCKED
    else:
        thresholds_met = (settled >= min_settled
                          and seg["distinct_days"] >= min_days
                          and seg["distinct_fixtures"] >= min_fixtures)
        if not thresholds_met:
            tier = (TIER_WATCHLIST if settled >= watch_min_settled
                    else TIER_INSUFFICIENT)
        elif stale_only or concentrated or open_share > max_pending_share:
            tier = TIER_WATCHLIST
        elif roi_type == ROI_EXEC_SAFE:
            if "single_source_profit_dominance" in warnings:
                tier = TIER_WATCHLIST
            else:
                tier = TIER_EXEC_PROMO
        else:
            tier = (TIER_PRICE_ENRICH if not seg.get("execution_safe_count")
                    else TIER_SHADOW_PROMO)

    action, reason = ACTION_BY_TIER[tier]
    if tier == TIER_WATCHLIST and stale_only:
        action, reason = ACTION_STALE_ARTIFACT
    if (seg.get("excluded_no_selection", 0) + seg.get("excluded_no_price", 0)
            > 0 and tier in (TIER_PRICE_ENRICH, TIER_WATCHLIST)
            and seg["flat_profit_units"] > 0):
        # positive signal sitting next to ungradeable records of the same
        # segment: the drop point needs inspection, not promotion
        warnings.append("ungradeable_records_in_segment")
    return {"tier": tier, "action": action, "action_reason": reason,
            "warnings": warnings}


# ----------------------------------------------------------------- report --
_BASELINE_FILTERS: dict[str, Callable[[Mapping[str, Any]], bool]] = {
    "all_scored": lambda r: True,
    "scored_not_promoted": lambda r: r["promotion_state"] == "scored_not_promoted",
    "promoted_picks": lambda r: r["promotion_state"] != "scored_not_promoted",
    "ticketed_legs": lambda r: r["promotion_state"] == "ticketed",
}


def _pool_agg(records: Sequence[Mapping[str, Any]],
              filt: Callable[[Mapping[str, Any]], bool]) -> dict[str, Any]:
    seg = _seg_blank()
    for rec in records:
        if filt(rec):
            _seg_add(seg, rec)
    seg.pop("_dims", None)
    return _seg_close(seg)


def build_segment_report(days: Sequence[str], *, root: Path | None = None,
                         settled: Mapping[tuple, str] | None = None,
                         all_runs: bool = False,
                         min_settled: int = 30, min_days: int = 3,
                         min_fixtures: int = 20, watch_min_settled: int = 10,
                         max_day_concentration: float = 0.6,
                         max_fixture_concentration: float = 0.5,
                         max_pending_share: float = 0.5,
                         top_n: int = 15) -> dict[str, Any]:
    """Full segment analysis for a date window. AUDIT ONLY."""
    data = collect_records(days, root=root, settled=settled,
                           all_runs=all_runs)
    dims: list[object] = list(SINGLE_DIMENSIONS) + list(COMPOUND_DIMENSIONS)
    thresholds = dict(min_settled=min_settled, min_days=min_days,
                      min_fixtures=min_fixtures,
                      watch_min_settled=watch_min_settled,
                      max_day_concentration=max_day_concentration,
                      max_fixture_concentration=max_fixture_concentration,
                      max_pending_share=max_pending_share)

    out_segments: list[dict[str, Any]] = []
    baselines: dict[str, dict[str, Any]] = {}
    for roi_type, records in ((ROI_CAPTURED, data["captured"]),
                              (ROI_EXEC_SAFE, data["exec_safe"])):
        pools = {name: _pool_agg(records, filt)
                 for name, filt in _BASELINE_FILTERS.items()}
        baselines[roi_type] = {
            name: {k: pool[k] for k in
                   ("total_records", "settled_records", "flat_profit_units",
                    "flat_roi")}
            for name, pool in pools.items()}
        base = pools["all_scored"]
        base_roi = base.get("flat_roi")
        for key, seg in build_segments(records, dims).items():
            verdict = classify_segment(seg, roi_type=roi_type, **thresholds)
            seg_roi = seg.get("flat_roi")
            entry = dict(seg)
            entry.update(verdict)
            entry["roi_type"] = roi_type
            entry["baseline"] = "all_scored"
            entry["baseline_roi"] = base_roi
            entry["baseline_flat_units"] = base.get("flat_profit_units")
            entry["lift_vs_baseline"] = (
                round(seg_roi - base_roi, 6)
                if seg_roi is not None and base_roi is not None else None)
            out_segments.append(entry)

    out_segments.sort(key=lambda s: (-(s["flat_profit_units"]),
                                     s["segment_key"]))

    def _tops(roi_type: str) -> list[dict[str, Any]]:
        return [s for s in out_segments
                if s["roi_type"] == roi_type and (s.get("flat_roi") or 0) > 0
                and s["settled_records"] > 0][:top_n]

    def _tier(t: str) -> list[dict[str, Any]]:
        return [s for s in out_segments if s["tier"] == t][:top_n]

    quality_warnings = sorted({w for s in out_segments
                               for w in s.get("warnings", [])
                               if w in ("concentration_day_or_fixture",
                                        "single_source_profit_dominance",
                                        "stale_only_profit",
                                        "high_pending_unmatched_share")})
    return {
        "audit_banner": AUDIT_BANNER,
        "no_behavior_change": NO_BEHAVIOR_LINE,
        "window": {"from": min(days), "to": max(days)} if days else None,
        "days_requested": data["days_requested"],
        "days_with_ledger": data["days_with_ledger"],
        "days_without_ledger": data["days_without_ledger"],
        "thresholds": thresholds,
        "record_counts": {
            "captured_price_shadow": len(data["captured"]),
            "execution_safe": len(data["exec_safe"]),
        },
        "baselines": baselines,
        "segments": out_segments,
        "top_positive_captured": _tops(ROI_CAPTURED),
        "top_positive_execution_safe": _tops(ROI_EXEC_SAFE),
        "promotion_candidates": _tier(TIER_EXEC_PROMO),
        "shadow_promotion_candidates": _tier(TIER_SHADOW_PROMO),
        "price_enrichment_candidates": _tier(TIER_PRICE_ENRICH),
        "watchlist": _tier(TIER_WATCHLIST),
        "blocked_negative": _tier(TIER_BLOCKED),
        "quality_warnings": quality_warnings,
        "band_documentation": {
            "odds_band": "<1.30, 1.30-1.49, 1.50-1.79, 1.80-2.19, 2.20-2.99, 3.00+",
            "probability_band": "<0.50, 0.50-0.59, 0.60-0.69, 0.70-0.79, 0.80-0.89, 0.90+ (fixed, not quantile — deterministic across windows)",
            "score_band": "<0.5, 0.5-0.99, 1.0-1.99, 2.0+",
            "price_age_band": "fetched_this_run, <=10m, <=1h, >1h, unknown",
        },
    }


# ---------------------------------------------------------------- rolling --
# Per-window-length threshold profiles (reviewer-set): longer windows must
# clear HIGHER bars — an edge that only exists in the short window did not
# survive. Unlisted lengths scale linearly from the 7-day base (documented,
# deterministic). Explicit CLI threshold flags override ALL windows and the
# report says so — relaxation must be explicit and visible, never silent.
DEFAULT_WINDOW_PROFILES: dict[int, dict[str, int]] = {
    7: {"min_settled": 30, "min_days": 3, "min_fixtures": 20},
    14: {"min_settled": 50, "min_days": 5, "min_fixtures": 35},
    30: {"min_settled": 90, "min_days": 8, "min_fixtures": 60},
}


def window_profile(window_days: int) -> dict[str, int]:
    prof = DEFAULT_WINDOW_PROFILES.get(int(window_days))
    if prof:
        return dict(prof)
    scale = max(1.0, window_days / 7.0)
    return {"min_settled": max(30, round(30 * scale)),
            "min_days": max(3, round(3 * scale)),
            "min_fixtures": max(20, round(20 * scale))}


def build_rolling_report(to_day: str, *, windows: Sequence[int] = (7, 14, 30),
                         root: Path | None = None,
                         settled: Mapping[tuple, str] | None = None,
                         all_runs: bool = False,
                         threshold_overrides: Mapping[str, int] | None = None,
                         top_n: int = 15, **classify_kwargs) -> dict[str, Any]:
    """Rolling multi-window segment analysis with cross-window survival.

    AUDIT ONLY. A segment is ``promotion_proposal_ready`` (still only a
    label — no live behavior changes) ONLY when it is
    EXECUTION_SAFE_PROMOTION_CANDIDATE in EVERY requested window, each
    window judged against its own (stricter-with-length) thresholds.
    Exec-promo appearances that fail any window are listed as
    NOT_SURVIVED_ALL_WINDOWS — visible, never silently dropped.
    """
    to10 = str(to_day)[:10]
    window_reports: dict[str, dict[str, Any]] = {}
    for w in windows:
        start = (datetime.strptime(to10, "%Y-%m-%d")
                 - timedelta(days=int(w) - 1)).strftime("%Y-%m-%d")
        prof = window_profile(int(w))
        if threshold_overrides:
            prof.update({k: int(v) for k, v in threshold_overrides.items()})
        window_reports[f"{int(w)}d"] = build_segment_report(
            date_range(start, to10), root=root, settled=settled,
            all_runs=all_runs, top_n=top_n, **prof, **classify_kwargs)

    # cross-window survival of the ONLY ticket-relevant tier
    per_key: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for wname, rep in window_reports.items():
        for s in rep["segments"]:
            per_key[(s["roi_type"], s["segment_key"])][wname] = s
    survivors, non_survivors = [], []
    wnames = list(window_reports)
    for (roi_type, key), by_window in sorted(per_key.items()):
        tiers = {w: (by_window.get(w) or {}).get("tier") for w in wnames}
        if not any(t == TIER_EXEC_PROMO for t in tiers.values()):
            continue
        entry = {
            "roi_type": roi_type, "segment_key": key,
            "tiers_by_window": tiers,
            "windows": {w: {k: by_window[w][k] for k in
                            ("settled_records", "flat_profit_units",
                             "flat_roi", "distinct_days", "distinct_fixtures")}
                        for w in wnames if w in by_window},
        }
        if all(tiers.get(w) == TIER_EXEC_PROMO for w in wnames):
            entry["survival"] = "SURVIVES_ALL_WINDOWS"
            entry["action"] = "PROMOTION_PROPOSAL_REVIEW"
            entry["action_reason"] = (
                "EXECUTION_SAFE_PROMOTION_CANDIDATE in every requested "
                "window under per-window thresholds; eligible for a "
                "SEPARATE written promotion proposal — no live behavior "
                "changed by this report.")
            survivors.append(entry)
        else:
            entry["survival"] = "NOT_SURVIVED_ALL_WINDOWS"
            entry["action"] = "WATCH"
            entry["action_reason"] = (
                "exec-safe promotion tier reached in some windows only; "
                "the edge has not yet survived every window.")
            non_survivors.append(entry)
    return {
        "audit_banner": AUDIT_BANNER,
        "no_behavior_change": NO_BEHAVIOR_LINE,
        "to": to10,
        "windows": {w: window_reports[w]["window"] for w in wnames},
        "window_profiles": {w: {k: window_reports[w]["thresholds"][k]
                                for k in ("min_settled", "min_days",
                                          "min_fixtures")}
                            for w in wnames},
        "thresholds_overridden": bool(threshold_overrides),
        "window_reports": window_reports,
        "promotion_proposal_ready": survivors,
        "exec_promo_not_survived": non_survivors,
    }


def render_rolling_report(report: Mapping[str, Any]) -> str:
    lines = [
        f"ROLLING SEGMENT SURVIVAL — AUDIT ONLY — {AUDIT_BANNER}",
        "=" * 78,
        f"Anchor date: {report['to']}   windows: "
        + ", ".join(f"{w} {v['from']}..{v['to']}"
                    for w, v in report["windows"].items()),
        "Per-window thresholds: " + "; ".join(
            f"{w}: {p}" for w, p in report["window_profiles"].items())
        + ("   [THRESHOLDS EXPLICITLY OVERRIDDEN]"
           if report.get("thresholds_overridden") else ""),
        "",
        "PROMOTION PROPOSAL READY (EXEC-SAFE, SURVIVES ALL WINDOWS):",
    ]
    ready = report.get("promotion_proposal_ready") or []
    if not ready:
        lines.append("  (none — no execution-safe segment survived every "
                     "window; nothing to propose)")
    for e in ready:
        lines.append(f"  {e['segment_key']}")
        for w, stats in e["windows"].items():
            roi = stats.get("flat_roi")
            roi_s = f"{roi * 100.0:+.1f}%" if roi is not None else "n/a"
            lines.append(f"    {w}: settled={stats['settled_records']} "
                         f"flat={stats['flat_profit_units']:+.2f}u "
                         f"roi={roi_s} days={stats['distinct_days']} "
                         f"fixtures={stats['distinct_fixtures']}")
        lines.append(f"    ACTION: {e['action']} — {e['action_reason']}")
    lines += ["", "EXEC-PROMO IN SOME WINDOWS ONLY (NOT SURVIVED):"]
    missed = report.get("exec_promo_not_survived") or []
    if not missed:
        lines.append("  (none)")
    for e in missed:
        tier_s = ", ".join(f"{w}={t or 'absent'}"
                           for w, t in e["tiers_by_window"].items())
        lines.append(f"  {e['segment_key']}  [{tier_s}]")
    lines += ["", "Per-window detail follows.", ""]
    for w, rep in report["window_reports"].items():
        lines += [f"{'#' * 8} WINDOW {w} {'#' * 8}",
                  render_segment_report(rep), ""]
    lines += [AUDIT_BANNER, NO_BEHAVIOR_LINE]
    return "\n".join(lines)


# ----------------------------------------------------------------- render --
def _fmt_seg(s: Mapping[str, Any]) -> str:
    roi = s.get("flat_roi")
    roi_s = f"{roi * 100.0:+.1f}%" if roi is not None else "n/a"
    lift = s.get("lift_vs_baseline")
    lift_s = f"{lift * 100.0:+.1f}pp" if lift is not None else "n/a"
    conf = s.get("confidence") or {}
    warn = ",".join(s.get("warnings") or []) or "-"
    return (f"  {s['segment_key'][:58]:58s} n={s['total_records']:<4d} "
            f"settled={s['settled_records']:<4d} "
            f"W/L/V={s['wins']}/{s['losses']}/{s['voids']} "
            f"flat={s['flat_profit_units']:+.2f}u roi={roi_s:>7s} "
            f"lift={lift_s:>8s} days={s['distinct_days']} "
            f"dayconc={conf.get('max_day_concentration')} "
            f"tier={s['tier']} action={s['action']} warn={warn}")


def render_segment_report(report: Mapping[str, Any]) -> str:
    w = report.get("window") or {}
    rc = report["record_counts"]
    lines = [
        f"SEGMENT SUMMARY — AUDIT ONLY — {AUDIT_BANNER}",
        "=" * 78,
        f"Window: {w.get('from')}..{w.get('to')}  "
        f"days_with_ledger={len(report['days_with_ledger'])} "
        f"days_without_ledger={len(report['days_without_ledger'])}",
        f"Records: captured_price_shadow={rc['captured_price_shadow']} "
        f"execution_safe={rc['execution_safe']}",
        f"Thresholds: {report['thresholds']}",
        "",
        "SEGMENT BASELINE COMPARISON:",
    ]
    for roi_type, pools in report["baselines"].items():
        for name, pool in pools.items():
            roi = pool.get("flat_roi")
            roi_s = f"{roi * 100.0:+.1f}%" if roi is not None else "n/a"
            lines.append(f"  [{roi_type}] {name:24s} n={pool['total_records']:<4d} "
                         f"settled={pool['settled_records']:<4d} "
                         f"flat={pool['flat_profit_units']:+.2f}u roi={roi_s}")
    sections = (
        ("TOP POSITIVE SEGMENTS — CAPTURED-PRICE SHADOW ROI "
         "(AUDIT-ONLY — NOT STAKEABLE)", "top_positive_captured"),
        ("TOP POSITIVE SEGMENTS — EXECUTION-SAFE ROI",
         "top_positive_execution_safe"),
        ("PROMOTION CANDIDATES (EXECUTION_SAFE_PROMOTION_CANDIDATE)",
         "promotion_candidates"),
        ("SHADOW PROMOTION CANDIDATES (audit prices only — NOT ticket-eligible)",
         "shadow_promotion_candidates"),
        ("PRICE ENRICHMENT CANDIDATES", "price_enrichment_candidates"),
        ("WATCHLIST / STALE-ONLY POSITIVE", "watchlist"),
        ("NEGATIVE / KEEP BLOCKED", "blocked_negative"),
    )
    for title, key in sections:
        lines += ["", title + ":"]
        rows = report.get(key) or []
        if not rows:
            lines.append("  (none)")
        for s in rows:
            lines.append(_fmt_seg(s))
    lines += ["", "OVERFIT / QUALITY WARNINGS: "
              + (", ".join(report["quality_warnings"]) or "(none)"),
              "", AUDIT_BANNER, NO_BEHAVIOR_LINE]
    return "\n".join(lines)
