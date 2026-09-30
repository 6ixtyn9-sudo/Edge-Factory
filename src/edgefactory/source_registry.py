"""Single source of truth for what each captured source can and cannot do.

Provenance (2026-09-30 funnel audit): source truth was scattered across
``picks_today.SOURCES_1X2`` / ``SOURCES_OU`` / ``SOURCES_BTTS`` /
``ALL_SOURCES`` / ``OU_COL`` / ``BTTS_COL``, ``capture_daily.JOBS``,
``audit_source_availability.WAREHOUSE_RELATIONS`` and several audit scripts.
The result: the whole PR #17 resilience group was captured, warehoused and
audited while being structurally invisible to the pick engine — it could not
vote, and nothing in the codebase said so out loud.

This module states each source's capabilities ONCE. Consumers derive their
lists from it instead of re-declaring them, and a regression test fails if a
source is captured by ``capture_daily.py`` but missing here.

Tiers
-----
``live``    may vote in the dispatchable consensus (unchanged legacy set;
            membership here is a mirror of production behaviour, NOT a
            promotion mechanism).
``shadow``  evaluated in the non-dispatch shadow consensus only.
``pricing`` odds/prices only; never a prediction voter.
``donor``   settlement/result donor only.

Promotion from ``shadow`` to ``live`` is an operator decision backed by
``scripts/audit_source_settlement_coverage.py`` evidence. Editing a tier here
changes what the engine will bet, so treat this file as gate configuration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCALDATA = ROOT / "localdata"

TIER_LIVE = "live"
TIER_SHADOW = "shadow"
TIER_PRICING = "pricing"
TIER_DONOR = "donor"

# Backfill modes.
BACKFILL_HISTORICAL = "historical"   # deep archive reachable
BACKFILL_D30 = "d30"                 # rolling window the job re-pulls
BACKFILL_FORWARD_ONLY = "capture_forward_only"  # no reachable archive
BACKFILL_UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceCapability:
    name: str
    tier: str
    markets: tuple[str, ...] = ()          # 1x2 / ou / btts / odds / results
    ou_col: str | None = None
    btts_col: str | None = None
    provides_kickoff: bool = False         # may supply the timing anchor
    identity_anchor: bool = False          # may be the fixture's display anchor
    ml_feature_provider: bool = False      # supplies a trained model feature
    backfill: str = BACKFILL_UNKNOWN
    caveats: tuple[str, ...] = ()

    @property
    def votes_1x2_live(self) -> bool:
        return self.tier == TIER_LIVE and "1x2" in self.markets

    @property
    def votes_1x2_shadow(self) -> bool:
        return self.tier in {TIER_LIVE, TIER_SHADOW} and "1x2" in self.markets

    @property
    def pricing_only(self) -> bool:
        return self.tier == TIER_PRICING

    @property
    def donor_only(self) -> bool:
        return self.tier == TIER_DONOR


# NOTE ON ``ml_feature_provider``
# The serving ml-meta model's feature vector contains fb_p / zb_p / sa_p plus
# Forebet-derived columns (kelly, pred_hs/pred_gs, goalsavg, HT probabilities)
# and statarea's HT probabilities. A fixture with NONE of these sources present
# scores on a zero-filled feature vector, i.e. off the distribution the
# threshold was calibrated on. So the ml-meta gate is not merely a stale name
# list — it is a real model-input requirement. It is expressed here as a
# capability so the engine stops hardcoding source names, and so retraining on
# a wider feature set only needs this flag flipped.
REGISTRY: tuple[SourceCapability, ...] = (
    SourceCapability(
        "forebet", TIER_LIVE, ("1x2", "ou", "btts", "results"),
        ou_col="p_over", btts_col="p_gg",
        provides_kickoff=True, identity_anchor=True, ml_feature_provider=True,
        backfill=BACKFILL_HISTORICAL,
        caveats=("parked: upstream 403 HTML; Browser Run off",),
    ),
    SourceCapability(
        "zulubet", TIER_LIVE, ("1x2", "results"),
        provides_kickoff=True, identity_anchor=True, ml_feature_provider=True,
        backfill=BACKFILL_D30,
        caveats=("some rows carry no kickoff",),
    ),
    SourceCapability(
        "statarea", TIER_LIVE, ("1x2", "ou", "results"),
        ou_col="p_o25",
        provides_kickoff=True, identity_anchor=True, ml_feature_provider=True,
        backfill=BACKFILL_D30,
        caveats=("kickoff lives in the `time` column, not `kickoff`",),
    ),
    SourceCapability(
        "vitibet", TIER_LIVE, ("1x2", "results"),
        provides_kickoff=True, identity_anchor=True,
        backfill=BACKFILL_D30,
        caveats=("13 reversed-orientation candidates in the D90 audit",),
    ),
    SourceCapability(
        "betclan", TIER_LIVE, ("1x2",),
        provides_kickoff=False, identity_anchor=False,
        backfill=BACKFILL_FORWARD_ONLY,
        caveats=("no kickoff column: cannot anchor same-day timing",),
    ),
    SourceCapability(
        "scoutingstats", TIER_LIVE, ("ou", "btts", "results"),
        ou_col="p_o25", btts_col="p_gg",
        provides_kickoff=True, identity_anchor=False,
        backfill=BACKFILL_D30,
        caveats=("no 1X2 vote; OU/BTTS and price corroboration only",),
    ),
    SourceCapability(
        "bzzoiro", TIER_LIVE, ("1x2", "ou", "btts"),
        ou_col="p_o25", btts_col="p_gg",
        provides_kickoff=True, identity_anchor=False,
        backfill=BACKFILL_FORWARD_ONLY,
    ),
    # --- PR #17 resilience group: captured, shadow-evaluated, NOT dispatchable
    SourceCapability(
        "predictz", TIER_SHADOW, ("1x2",),
        provides_kickoff=False, backfill=BACKFILL_D30,
        caveats=("no kickoff column", "no source-supplied scores"),
    ),
    SourceCapability(
        "windrawwin", TIER_SHADOW, ("1x2",),
        provides_kickoff=False, backfill=BACKFILL_FORWARD_ONLY,
        caveats=("no kickoff column", "5.97% settlement coverage"),
    ),
    SourceCapability(
        "freesupertips", TIER_SHADOW, ("1x2",),
        provides_kickoff=False, backfill=BACKFILL_FORWARD_ONLY,
        caveats=("sample far too small (16 fixtures in D90)",),
    ),
    SourceCapability(
        "afootballreport", TIER_SHADOW, ("1x2",),
        provides_kickoff=True, backfill=BACKFILL_FORWARD_ONLY,
        caveats=("6.16% settlement coverage", "research tier"),
    ),
    SourceCapability(
        "prosoccer", TIER_SHADOW, ("1x2", "results"),
        provides_kickoff=True, backfill=BACKFILL_D30,
        caveats=("tiny same-day slate (43 fixtures in D90)",),
    ),
    SourceCapability(
        "soccervista", TIER_SHADOW, ("1x2",),
        provides_kickoff=True, backfill=BACKFILL_FORWARD_ONLY,
        caveats=("no usable data captured yet", "JS day picker, today-only"),
    ),
    SourceCapability(
        "bettingclosed", TIER_DONOR, ("results",),
        provides_kickoff=False, backfill=BACKFILL_D30,
        caveats=("confirmation/results donor, not a prediction voter",),
    ),
    # --- pricing only
    SourceCapability("bzzoiro_odds", TIER_PRICING, ("odds",), backfill=BACKFILL_FORWARD_ONLY),
    SourceCapability("theoddsapi_odds", TIER_PRICING, ("odds",), backfill=BACKFILL_FORWARD_ONLY),
    SourceCapability("oddspapi_odds", TIER_PRICING, ("odds",), backfill=BACKFILL_UNKNOWN),
    SourceCapability("betexplorer_odds", TIER_PRICING, ("odds",), backfill=BACKFILL_HISTORICAL),
    SourceCapability("betexplorer_results", TIER_DONOR, ("results",), backfill=BACKFILL_HISTORICAL),
)

BY_NAME: dict[str, SourceCapability] = {cap.name: cap for cap in REGISTRY}


def get(name: str) -> SourceCapability | None:
    return BY_NAME.get(name)


def names(tier: str | None = None) -> tuple[str, ...]:
    return tuple(c.name for c in REGISTRY if tier is None or c.tier == tier)


def live_1x2_sources() -> tuple[str, ...]:
    return tuple(c.name for c in REGISTRY if c.votes_1x2_live)


def shadow_1x2_sources() -> tuple[str, ...]:
    return tuple(c.name for c in REGISTRY if c.tier == TIER_SHADOW and "1x2" in c.markets)


def live_market_sources(market: str) -> tuple[str, ...]:
    return tuple(c.name for c in REGISTRY if c.tier == TIER_LIVE and market in c.markets)


def live_consumed_sources() -> tuple[str, ...]:
    """Every source the live pick engine reads (any prediction market).

    1X2 voters first (their order is the consensus iteration order), then the
    remaining live market sources.
    """
    first = live_1x2_sources()
    rest = tuple(
        c.name for c in REGISTRY
        if c.tier == TIER_LIVE and c.name not in first and {"ou", "btts"} & set(c.markets)
    )
    return first + rest


def ou_columns() -> dict[str, str]:
    return {c.name: c.ou_col for c in REGISTRY if c.ou_col}


def btts_columns() -> dict[str, str]:
    return {c.name: c.btts_col for c in REGISTRY if c.btts_col}


def ml_feature_providers() -> tuple[str, ...]:
    return tuple(c.name for c in REGISTRY if c.ml_feature_provider)


def kickoff_providers() -> tuple[str, ...]:
    return tuple(c.name for c in REGISTRY if c.provides_kickoff)


def has_ml_feature_support(present_sources) -> bool:
    """True when at least one trained-feature provider is on the fixture.

    Capability-driven replacement for the old ``if ml_model and (fb or zb or
    sa)`` name check. Same behaviour today by construction, but the engine no
    longer hardcodes source names and a retrain only needs the registry flag.
    """
    providers = set(ml_feature_providers())
    return any(str(s) in providers for s in present_sources)


# --------------------------------------------------------------------------
# Validation state (read-only overlay from the settlement coverage audit)
# --------------------------------------------------------------------------


def load_validation_states(localdata: Path | None = None, day: str | None = None) -> dict[str, str]:
    """Latest per-source verdict from the settlement coverage artifact.

    Read-only and best-effort: a missing artifact simply yields ``unknown`` for
    every source. Nothing in the engine gates on this — it is evidence shown to
    the operator, never an automatic promotion.
    """
    base = localdata or LOCALDATA
    candidates = sorted(base.glob("source_settlement_coverage_*.json"))
    if day:
        preferred = base / f"source_settlement_coverage_{day}.json"
        if preferred.exists():
            candidates = [preferred]
    if not candidates:
        return {}
    try:
        payload = json.loads(candidates[-1].read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, str] = {}
    for row in payload.get("sources") or []:
        if isinstance(row, dict) and row.get("source"):
            out[str(row["source"])] = str(row.get("verdict") or "unknown")
    return out


def describe(localdata: Path | None = None, day: str | None = None) -> list[dict]:
    """Registry + validation state, for reports and artifacts."""
    states = load_validation_states(localdata, day)
    rows = []
    for cap in REGISTRY:
        rows.append({
            "source": cap.name,
            "tier": cap.tier,
            "markets": list(cap.markets),
            "provides_kickoff": cap.provides_kickoff,
            "identity_anchor": cap.identity_anchor,
            "ml_feature_provider": cap.ml_feature_provider,
            "backfill": cap.backfill,
            "validation_state": states.get(cap.name, "unknown"),
            "caveats": list(cap.caveats),
            "dispatchable": cap.tier == TIER_LIVE,
        })
    return rows


# --------------------------------------------------------------------------
# Roach detector — invariants that catch silent structural collapse
# --------------------------------------------------------------------------


def registry_coverage_warnings(captured_sources) -> list[str]:
    """Sources captured by the pipeline but absent from this registry."""
    missing = sorted(set(map(str, captured_sources)) - set(BY_NAME))
    return [
        f"ROACH: source '{name}' is captured by capture_daily but missing from "
        "the source capability registry — it is invisible to the pick engine"
        for name in missing
    ]


def funnel_warnings(
    *,
    match_surface: int,
    scored_fixtures: int,
    live_candidates: int,
    shadow_candidates: int,
    sources_with_1x2_rows,
    odds_enriched: int | None = None,
    candidates_before_odds: int | None = None,
) -> list[str]:
    """Structural warnings for the same-day chain. Diagnostic, never fatal."""
    warnings: list[str] = []
    if match_surface >= 50 and scored_fixtures <= max(1, match_surface // 20):
        warnings.append(
            f"ROACH: raw same-day surface is {match_surface} but only "
            f"{scored_fixtures} fixture(s) were scoreable — the voter pool or "
            "identity join is collapsing, not the sources"
        )
    for source in sorted(set(map(str, sources_with_1x2_rows))):
        cap = get(source)
        if cap is None:
            warnings.append(
                f"ROACH: '{source}' has 1X2 rows today but is not in the "
                "capability registry"
            )
        elif not cap.votes_1x2_shadow:
            warnings.append(
                f"ROACH: '{source}' has 1X2 rows today but its tier "
                f"('{cap.tier}') excludes it from both live and shadow consensus"
            )
    if live_candidates == 0 and shadow_candidates > 0:
        warnings.append(
            f"ROACH: 0 live candidates but {shadow_candidates} shadow candidate(s) — "
            "the dispatchable source universe is the binding constraint today"
        )
    if candidates_before_odds and odds_enriched == 0:
        warnings.append(
            f"ROACH: {candidates_before_odds} candidate(s) existed but odds "
            "enrichment matched 0 — price identity may be broken (not merely "
            "an empty slate)"
        )
    return warnings
