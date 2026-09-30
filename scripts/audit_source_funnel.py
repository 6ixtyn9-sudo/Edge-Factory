#!/usr/bin/env python3
"""Same-day source funnel audit — why N matches become M picks.

Provenance (2026-09-30 production run): the log said ``448 matches`` but
``ML-meta scored 21 fixture(s)``, ``-> 5 pick(s)``, then ``pre-match guard
skipped 8 (missing_kickoff_same_day=8)``, ``enriched=0`` and finally ``fresh
run yielded 0``. Capture looked healthy; the picks chain collapsed anyway.
``audit_source_availability`` (rows) and ``audit_source_settlement_coverage``
(historical prediction->score matching) both answer *other* questions. Neither
can say where TODAY's surface is lost.

This audit walks the same-day chain the real engine walks:

    raw source rows -> unique fixtures -> cross-source identity overlap
    -> kickoff present/trusted -> pre-match eligible -> 1X2/OU/BTTS signal
    -> consensus surface -> >=2 voters -> ML-meta scoreable -> candidates
    -> odds enrichment -> final buckets

It is READ-ONLY and NETWORK-FREE: it reads the capture caches in localdata and
reuses the REAL gate functions from ``scripts/picks_today.py``
(``source_team_key``, ``probs_1x2``, ``parse_kickoff_dt``,
``operational_pick_eligibility``, ``SOURCES_1X2`` ...) instead of
re-implementing them, so the funnel it reports cannot drift from the funnel the
engine executes. It never fetches, never writes source caches, never mutates
state, and it cannot create or promote a pick.

Usage (also wired into scripts/daily.py official mode as a soft step):

    PYTHONPATH=src python3 scripts/audit_source_funnel.py \\
        --date 2026-09-30 \\
        --output-json localdata/source_funnel_2026-09-30.json \\
        --output-md   localdata/source_funnel_2026-09-30.md
"""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

# Every source that can produce same-day prediction rows, including the ones
# the picks engine does NOT currently consume — that gap is a finding, not an
# omission, so they must appear in the table.
from edgefactory import source_registry

# Derived from the single capability registry so a captured source can never
# be silently invisible again (see test_source_registry.py).
SAME_DAY_SOURCES: tuple[str, ...] = tuple(
    c.name for c in source_registry.REGISTRY
    if {"1x2", "ou", "btts"} & set(c.markets)
) + ("bettingclosed",)

ODDS_SOURCES: tuple[str, ...] = tuple(source_registry.names(source_registry.TIER_PRICING))

DEFAULT_MIN_LEAD = 30


def load_picks_engine():
    """Import the live engine module so the audit shares its exact gates."""
    path = ROOT / "scripts" / "picks_today.py"
    spec = importlib.util.spec_from_file_location("edgefactory_picks_today_funnel", path)
    if spec is None or spec.loader is None:  # pragma: no cover - import guard
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # pragma: no cover - never let the audit break a run
        return None
    return module


# --------------------------------------------------------------------------
# Row loading (capture caches only — no network)
# --------------------------------------------------------------------------


def source_files(localdata: Path, source: str) -> list[Path]:
    monthly = sorted(localdata.glob(f"{source}_[0-9][0-9][0-9][0-9]-[0-9][0-9].csv.gz"))
    legacy = localdata / f"{source}.csv.gz"
    return ([legacy] if legacy.exists() else []) + monthly


def iter_rows(path: Path) -> Iterator[dict[str, str]]:
    try:
        with gzip.open(path, "rt", newline="", encoding="utf-8", errors="replace") as handle:
            yield from csv.DictReader(handle)
    except (OSError, csv.Error, UnicodeError):
        return


def load_day_rows(localdata: Path, source: str, day: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in source_files(localdata, source):
        for row in iter_rows(path):
            if str(row.get("date") or "").strip()[:10] == day:
                rows.append(row)
    return rows


# --------------------------------------------------------------------------
# Section A — per-source same-day availability
# --------------------------------------------------------------------------


@dataclass
class SourceDay:
    source: str
    raw_rows: int = 0
    unique_fixtures: int = 0
    has_home_away_date: int = 0
    key_too_short: int = 0
    already_settled: int = 0
    has_kickoff: int = 0
    trusted_kickoff: int = 0
    pre_match_eligible: int = 0
    has_1x2_signal: int = 0
    has_ou_signal: int = 0
    has_btts_signal: int = 0
    in_consensus_surface: bool = False
    consumed_by_picks_engine: bool = False
    warehouse_table_present: bool = False
    notes: str = ""


def _has_value(row: dict, *keys: str) -> bool:
    return any(str(row.get(k) or "").strip() not in {"", "None", "-"} for k in keys)


def audit_source_day(
    source: str,
    rows: list[dict],
    *,
    engine,
    as_of: datetime,
    min_lead: int,
    warehouse_tables: set[str],
) -> tuple[SourceDay, dict[tuple[str, str], dict]]:
    out = SourceDay(source=source, raw_rows=len(rows))
    out.in_consensus_surface = source in set(getattr(engine, "SOURCES_1X2", ()) or ())
    out.consumed_by_picks_engine = source in set(getattr(engine, "ALL_SOURCES", ()) or ())
    out.warehouse_table_present = bool({source, f"{source}_settled"} & warehouse_tables)

    ou_col = (getattr(engine, "OU_COL", {}) or {}).get(source)
    btts_col = (getattr(engine, "BTTS_COL", {}) or {}).get(source)
    fixtures: dict[tuple[str, str], dict] = {}

    for row in rows:
        home, away = row.get("home"), row.get("away")
        if not home or not away:
            continue
        out.has_home_away_date += 1
        # Same exclusion the engine applies in fetch_all: settled rows are not
        # a same-day betting surface.
        if str(row.get("hs") or "").strip() not in {"", "None"}:
            out.already_settled += 1
            continue
        key = (engine.source_team_key(home), engine.source_team_key(away))
        if len(key[0]) < 4 or len(key[1]) < 4:
            out.key_too_short += 1
            continue
        fixtures[key] = row

    out.unique_fixtures = len(fixtures)

    for row in fixtures.values():
        ko_raw = row.get("kickoff") or row.get("time")
        if str(ko_raw or "").strip():
            out.has_kickoff += 1
        ko = engine.parse_kickoff_dt(ko_raw)
        if ko is not None:
            out.trusted_kickoff += 1
            if ko.tzinfo is None:
                ko = ko.replace(tzinfo=as_of.tzinfo)
            if (ko - as_of).total_seconds() / 60.0 >= min_lead:
                out.pre_match_eligible += 1
        if engine.probs_1x2(row) is not None:
            out.has_1x2_signal += 1
        if ou_col and _has_value(row, ou_col):
            out.has_ou_signal += 1
        if btts_col and _has_value(row, btts_col):
            out.has_btts_signal += 1

    notes: list[str] = []
    if out.raw_rows == 0:
        notes.append("no same-day rows captured")
    if out.unique_fixtures and not out.consumed_by_picks_engine:
        notes.append("NOT consumed by picks engine (captured but cannot vote)")
    elif out.unique_fixtures and not out.in_consensus_surface:
        notes.append("consumed for OU/BTTS only, not in SOURCES_1X2")
    if out.unique_fixtures and out.trusted_kickoff == 0:
        notes.append("no trusted kickoff -> same-day guard drops anything anchored here")
    if out.unique_fixtures and out.has_1x2_signal == 0:
        notes.append("no 1X2 probability signal")
    if out.key_too_short:
        notes.append(f"{out.key_too_short} rows dropped by <4-char identity key")
    out.notes = "; ".join(notes) or "-"
    return out, fixtures


# --------------------------------------------------------------------------
# Sections B/C/D/E — overlap, consensus, kickoff and odds funnels
# --------------------------------------------------------------------------


def _fold_key(engine, key: tuple[str, str]) -> tuple[str, str]:
    # source_team_key already folds+aliases; the exact tier is the raw
    # normalized pair, the alias tier collapses club-structure noise.
    return key


def build_overlap(
    per_source: dict[str, dict[tuple[str, str], dict]],
    *,
    engine,
    examples: int = 10,
) -> dict:
    exact: dict[tuple[str, str], set[str]] = defaultdict(set)
    for source, fixtures in per_source.items():
        for key in fixtures:
            exact[key].add(source)

    histogram = Counter(len(sources) for sources in exact.values())
    singletons = [
        {"fixture": f"{k[0]} vs {k[1]}", "source": sorted(s)[0]}
        for k, s in sorted(exact.items()) if len(s) == 1
    ]
    multi = [
        {"fixture": f"{k[0]} vs {k[1]}", "sources": ",".join(sorted(s))}
        for k, s in sorted(exact.items()) if len(s) >= 2
    ]

    # Orientation risk: another source holds the same pairing reversed.
    reversed_groups = []
    for key, sources in sorted(exact.items()):
        rev = exact.get((key[1], key[0]))
        if rev and key[0] < key[1]:
            reversed_groups.append({
                "fixture": f"{key[0]} vs {key[1]}",
                "sources": ",".join(sorted(sources)),
                "reversed_sources": ",".join(sorted(rev)),
            })

    return {
        "fixture_groups": len(exact),
        "groups_by_source_count": {str(k): v for k, v in sorted(histogram.items())},
        "single_source_groups": histogram.get(1, 0),
        "two_source_groups": histogram.get(2, 0),
        "three_plus_source_groups": sum(v for k, v in histogram.items() if k >= 3),
        "reversed_risk_groups": len(reversed_groups),
        "examples": {
            "singletons": singletons[:examples],
            "multi_source": multi[:examples],
            "reversed_risk": reversed_groups[:examples],
        },
    }


def build_consensus_funnel(
    per_source: dict[str, dict[tuple[str, str], dict]],
    *,
    engine,
    as_of: datetime,
    min_lead: int,
    examples: int = 10,
) -> dict:
    sources_1x2 = list(getattr(engine, "SOURCES_1X2", ()) or ())
    # ML-meta inference anchors (picks_today.eval_1x2: `if ml_model and (fb or zb or sa)`)
    ml_anchor_sources = ["forebet", "zulubet", "statarea"]

    surface: set[tuple[str, str]] = set()
    for source in sources_1x2:
        surface |= set(per_source.get(source, {}))

    voters_ok: set[tuple[str, str]] = set()
    ml_scoreable: set[tuple[str, str]] = set()
    drops: Counter = Counter()
    drop_examples: dict[str, list[dict]] = defaultdict(list)

    for key in sorted(surface):
        used = [
            s for s in sources_1x2
            if key in per_source.get(s, {}) and engine.probs_1x2(per_source[s][key]) is not None
        ]
        anchor_row = next(
            (per_source[s][key] for s in sources_1x2 if key in per_source.get(s, {})), {}
        )
        label = {
            "fixture": f"{anchor_row.get('home', key[0])} vs {anchor_row.get('away', key[1])}",
            "sources_with_1x2": ",".join(used) or "-",
        }
        if len(used) < 2:
            drops["fewer_than_2_voters_with_1x2"] += 1
            if len(drop_examples["fewer_than_2_voters_with_1x2"]) < examples:
                drop_examples["fewer_than_2_voters_with_1x2"].append(label)
            continue
        voters_ok.add(key)

        anchors = [s for s in ml_anchor_sources if key in per_source.get(s, {})]
        if not anchors:
            drops["no_ml_anchor_source_present"] += 1
            if len(drop_examples["no_ml_anchor_source_present"]) < examples:
                drop_examples["no_ml_anchor_source_present"].append(label)
            continue
        ml_scoreable.add(key)

    # Same-day kickoff eligibility on the ML-scoreable surface: this is the
    # gate that produced `missing_kickoff_same_day` in production.
    kickoff_ok = 0
    kickoff_drops: Counter = Counter()
    kickoff_examples: dict[str, list[dict]] = defaultdict(list)
    for key in sorted(ml_scoreable):
        row = next(
            (per_source[s][key] for s in sources_1x2 if key in per_source.get(s, {})), {}
        )
        # Fixture-group timing: a kickoff-less voter no longer poisons the
        # group if a timing-capable matched source supplies a trusted kickoff.
        agg = aggregate_fixture_kickoff(key, per_source, engine=engine)
        probe = {
            "date": str(row.get("date") or "")[:10],
            "kickoff": agg["kickoff"],
        }
        ok, reason = engine.operational_pick_eligibility(probe, as_of=as_of, min_lead=min_lead)
        if ok:
            kickoff_ok += 1
            continue
        kickoff_drops[reason or "unknown"] += 1
        if len(kickoff_examples[reason or "unknown"]) < examples:
            kickoff_examples[reason or "unknown"].append({
                "fixture": f"{row.get('home', key[0])} vs {row.get('away', key[1])}",
                "kickoff_raw": str(probe["kickoff"]) or "(none)",
                "kickoff_donors": ",".join(agg["kickoff_donors"]) or "none",
                "sources": ",".join(s for s in sources_1x2 if key in per_source.get(s, {})),
            })

    return {
        "sources_1x2": sources_1x2,
        "ml_anchor_sources": ml_anchor_sources,
        "match_surface": len(surface),
        "fixtures_with_2plus_voters": len(voters_ok),
        "fixtures_ml_scoreable": len(ml_scoreable),
        "fixtures_ml_scoreable_pre_match_eligible": kickoff_ok,
        "drops": dict(drops),
        "drop_examples": {k: v for k, v in drop_examples.items()},
        "kickoff_drops": dict(kickoff_drops),
        "kickoff_drop_examples": {k: v for k, v in kickoff_examples.items()},
    }


KICKOFF_CLASSES = (
    "trusted",            # parsed to a real datetime
    "clock_only",         # a time string that would not parse -> fail closed
    "date_only",          # date present, no time component
    "absent",             # source emits no kickoff/time value at all
)


def classify_kickoff(row: dict, *, engine) -> tuple[str, str]:
    """Classify one row's kickoff. Fails closed: anything unparseable is unsafe."""
    raw = row.get("kickoff") or row.get("time") or ""
    text = str(raw).strip()
    if not text:
        return "absent", ""
    if engine.parse_kickoff_dt(text) is not None:
        return "trusted", text
    # Present but unparseable (ambiguous clock, unknown timezone, junk).
    return ("date_only" if len(text) >= 8 and ":" not in text else "clock_only"), text


def aggregate_fixture_kickoff(
    key: tuple[str, str],
    per_source: dict[str, dict[tuple[str, str], dict]],
    *,
    engine,
) -> dict:
    """Fixture-group kickoff: any TIMING-CAPABLE matched source may supply it.

    A source with no kickoff column must not poison an otherwise valid fixture
    group — but it must not be allowed to supply timing either. Only sources
    the registry marks ``provides_kickoff`` can donate the timing anchor, and
    the value still has to parse. No trusted value anywhere => fail closed.
    """
    donors: list[str] = []
    classes: dict[str, str] = {}
    kickoff_value = ""
    for source, fixtures in per_source.items():
        row = fixtures.get(key)
        if row is None:
            continue
        kind, text = classify_kickoff(row, engine=engine)
        classes[source] = kind
        cap = source_registry.get(source)
        if kind == "trusted" and cap is not None and cap.provides_kickoff:
            donors.append(source)
            kickoff_value = kickoff_value or text
    return {
        "kickoff": kickoff_value,
        "kickoff_donors": donors,
        "trusted": bool(donors),
        "classes": classes,
    }


def classify_voters(
    per_source: dict[str, dict[tuple[str, str], dict]],
    rows_by_source: dict[str, "SourceDay"],
    *,
    engine,
) -> dict:
    """Every source with extractable 1X2 signal is live / shadow / blocked."""
    out: dict[str, dict] = {}
    for source, summary in rows_by_source.items():
        cap = source_registry.get(source)
        signal_rows = summary.has_1x2_signal
        if cap is None:
            role, blocker = "blocked", "not in source capability registry"
        elif cap.pricing_only:
            role, blocker = "not_a_voter", "pricing-only source"
        elif cap.donor_only:
            role, blocker = "not_a_voter", "settlement/result donor only"
        elif "1x2" not in cap.markets:
            role, blocker = "not_a_voter", "adapter exposes no 1X2 probability fields"
        elif signal_rows == 0:
            role, blocker = "blocked", (
                "no same-day rows captured" if summary.raw_rows == 0
                else "rows captured but no 1X2 probability fields parsed"
            )
        elif cap.tier == source_registry.TIER_LIVE:
            role, blocker = "live_voter", ""
        else:
            role, blocker = "shadow_voter", (
                "source tier is shadow: not settlement-validated for dispatch"
            )
        out[source] = {
            "role": role,
            "tier": cap.tier if cap else "unregistered",
            "raw_rows": summary.raw_rows,
            "normalized_fixtures": summary.unique_fixtures,
            "rows_with_1x2_signal": signal_rows,
            "blocker": blocker or "-",
            "caveats": list(cap.caveats) if cap else ["unregistered source"],
        }
    return out


def build_shadow_expansion(
    per_source: dict[str, dict[tuple[str, str], dict]],
    *,
    engine,
    examples: int = 10,
) -> dict:
    """What the voter pool WOULD look like if shadow sources could vote.

    Strictly diagnostic and NON-DISPATCH. It does not create picks, does not
    promote a source, and nothing downstream reads it. Its only job is to
    quantify whether the same-day collapse is caused by the certified voter
    pool being too small after Forebet's loss, or by something else.
    """
    certified = list(getattr(engine, "SOURCES_1X2", ()) or ())
    shadow = [
        s for s in per_source
        if s not in certified and any(
            engine.probs_1x2(row) is not None for row in per_source[s].values()
        )
    ]

    def voters(sources: list[str]) -> dict[tuple[str, str], list[str]]:
        table: dict[tuple[str, str], list[str]] = defaultdict(list)
        for source in sources:
            for key, row in per_source.get(source, {}).items():
                if engine.probs_1x2(row) is not None:
                    table[key].append(source)
        return table

    base = voters(certified)
    widened = voters(certified + shadow)
    base_ok = {k for k, v in base.items() if len(v) >= 2}
    wide_ok = {k for k, v in widened.items() if len(v) >= 2}
    gained = sorted(wide_ok - base_ok)

    return {
        "certified_voter_sources": certified,
        "shadow_sources_with_1x2_today": shadow,
        "fixtures_with_2plus_certified_voters": len(base_ok),
        "fixtures_with_2plus_voters_if_shadow_admitted": len(wide_ok),
        "fixtures_gained_if_shadow_admitted": len(gained),
        "dispatchable": False,
        "note": (
            "Diagnostic only. Admitting a shadow source is a certification "
            "decision requiring settlement-coverage evidence and operator "
            "sign-off; this audit never promotes anything."
        ),
        "examples": [
            {"fixture": f"{k[0]} vs {k[1]}", "voters": ",".join(widened[k])}
            for k in gained[:examples]
        ],
    }


def build_shadow_candidates(
    per_source: dict[str, dict[tuple[str, str], dict]],
    *,
    engine,
    as_of: datetime,
    min_lead: int,
    day: str,
    validation: dict[str, str],
    limit: int = 200,
) -> dict:
    """Non-dispatch shadow slate: what WOULD be evaluable on a wider universe.

    Every row carries ``dispatchable: false`` and an explicit blocker list.
    Nothing downstream reads this: it is an evidence artifact for the operator,
    not a pick source. It cannot become a CLEAN or CAUTION pick.
    """
    live = list(getattr(engine, "SOURCES_1X2", ()) or ())
    shadow = [s for s in source_registry.shadow_1x2_sources() if s in per_source]

    keys: set[tuple[str, str]] = set()
    for source in live + shadow:
        keys |= set(per_source.get(source, {}))

    rows: list[dict] = []
    blocker_counts: Counter = Counter()
    for key in sorted(keys):
        voters = [
            s for s in live + shadow
            if key in per_source.get(s, {})
            and engine.probs_1x2(per_source[s][key]) is not None
        ]
        if len(voters) < 2:
            continue
        live_voters = [s for s in voters if s in live]
        shadow_voters = [s for s in voters if s not in live]
        if not shadow_voters:
            continue  # already fully representable in the live funnel

        agg = aggregate_fixture_kickoff(key, per_source, engine=engine)
        anchor = next(per_source[s][key] for s in voters if key in per_source.get(s, {}))

        blockers: list[str] = []
        if len(live_voters) < 2:
            blockers.append("fewer_than_2_live_voters")
        if not source_registry.has_ml_feature_support(voters):
            blockers.append("no_ml_feature_provider_on_fixture")
        if not agg["trusted"]:
            blockers.append("no_trusted_kickoff_from_a_timing_capable_source")
        else:
            ok, reason = engine.operational_pick_eligibility(
                {"date": day, "kickoff": agg["kickoff"]}, as_of=as_of, min_lead=min_lead
            )
            if not ok:
                blockers.append(reason or "kickoff_guard")
        unvalidated = sorted(
            s for s in shadow_voters
            if validation.get(s, "unknown") not in {"settlement_validated"}
        )
        if unvalidated:
            blockers.append("shadow_sources_not_settlement_validated:" + ",".join(unvalidated))
        for b in blockers:
            blocker_counts[b.split(":")[0]] += 1

        rows.append({
            "date": day,
            "fixture": f"{anchor.get('home', key[0])} vs {anchor.get('away', key[1])}",
            "live_voters": live_voters,
            "shadow_voters": shadow_voters,
            "kickoff": agg["kickoff"] or None,
            "kickoff_donors": agg["kickoff_donors"],
            "dispatchable": False,
            "blockers": blockers,
        })

    return {
        "date": day,
        "dispatchable": False,
        "note": (
            "Shadow evaluation only. These rows are NEVER dispatched, never "
            "become CLEAN/CAUTION picks, and are not read by the pick engine. "
            "Promotion requires settlement-coverage evidence plus operator "
            "sign-off."
        ),
        "live_voter_sources": live,
        "shadow_voter_sources": shadow,
        "candidate_count": len(rows),
        "blocker_counts": dict(blocker_counts),
        "candidates": rows[:limit],
    }


def build_kickoff_funnel(rows_by_source: dict[str, SourceDay]) -> dict:
    return {
        source: {
            "unique_fixtures": row.unique_fixtures,
            "has_kickoff": row.has_kickoff,
            "trusted_kickoff": row.trusted_kickoff,
            "missing_kickoff": row.unique_fixtures - row.has_kickoff,
            "untrusted_kickoff": row.has_kickoff - row.trusted_kickoff,
            "pre_match_eligible": row.pre_match_eligible,
        }
        for source, row in rows_by_source.items()
        if row.unique_fixtures
    }


def build_odds_funnel(
    localdata: Path,
    day: str,
    consensus_keys: set[tuple[str, str]],
    *,
    engine,
    examples: int = 10,
    candidates_before_odds: int | None = None,
) -> dict:
    """Odds diagnostics that separate 'no candidates' from 'matching broken'."""
    out: dict = {
        "sources": {},
        "examples": {},
        "candidates_before_odds": candidates_before_odds,
        "diagnosis": None,
    }
    for source in ODDS_SOURCES:
        rows = load_day_rows(localdata, source, day)
        keys: set[tuple[str, str]] = set()
        for row in rows:
            home, away = row.get("home"), row.get("away")
            if not home or not away:
                continue
            keys.add((engine.source_team_key(home), engine.source_team_key(away)))
        overlap = keys & consensus_keys
        cap = source_registry.get(source)
        status = "ok"
        if not rows:
            status = "empty_no_rows_today"
        elif not keys:
            status = "rows_without_fixture_identity (event-id only feed)"
        elif not overlap and consensus_keys:
            status = "rows_present_but_zero_overlap_with_consensus_surface"
        out["sources"][source] = {
            "cached_rows": len(rows),
            "live_rows": 0 if not rows else None,
            "unique_fixtures": len(keys),
            "status": status,
            "backfill": cap.backfill if cap else "unknown",
            "overlap_with_consensus_surface": len(overlap),
            "coverage_pct_of_consensus": (
                round(100.0 * len(overlap) / len(consensus_keys), 2) if consensus_keys else 0.0
            ),
        }
        if consensus_keys:
            missing = sorted(consensus_keys - keys)[:examples]
            out["examples"][source] = [f"{h} vs {a}" for h, a in missing]

    any_price_rows = any(v["cached_rows"] for v in out["sources"].values())
    any_overlap = any(v["overlap_with_consensus_surface"] for v in out["sources"].values())
    if candidates_before_odds == 0:
        out["diagnosis"] = (
            "no_candidates_to_price — enrichment of 0 is a CONSEQUENCE of an "
            "empty candidate slate, not evidence that price matching is broken"
        )
    elif not any_price_rows:
        out["diagnosis"] = "no_price_rows_captured_today"
    elif not any_overlap:
        out["diagnosis"] = (
            "price_identity_broken — price rows exist for today but none share "
            "a fixture identity with the consensus surface"
        )
    else:
        out["diagnosis"] = "price_fixtures_overlap_the_surface"
    return out


# --------------------------------------------------------------------------
# Section G — backfill depth / retryable gaps
# --------------------------------------------------------------------------


def capture_windows() -> dict[str, tuple[str, str]]:
    path = ROOT / "scripts" / "capture_daily.py"
    spec = importlib.util.spec_from_file_location("edgefactory_capture_daily_funnel", path)
    if spec is None or spec.loader is None:
        return {}
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return {}
    return {str(job[0]): (str(job[1]), str(job[2])) for job in getattr(module, "JOBS", [])}


def build_backfill_depth(localdata: Path, day: str, sources: tuple[str, ...]) -> dict:
    windows = capture_windows()
    target = date.fromisoformat(day)
    d30 = {(target - timedelta(days=n)).isoformat() for n in range(31)}
    out: dict[str, dict] = {}
    for source in sources:
        days_seen: set[str] = set()
        for path in source_files(localdata, source):
            for row in iter_rows(path):
                value = str(row.get("date") or "").strip()[:10]
                if len(value) == 10:
                    days_seen.add(value)
        start, end = windows.get(source, ("-", "-"))
        failures: list[str] = []
        state_path = localdata / f"state_{source}.json"
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text())
                fails = state.get("failures", {})
                if isinstance(fails, dict):
                    failures = sorted(d for d in map(str, fails) if d in d30)
            except (OSError, json.JSONDecodeError, TypeError):
                failures = []
        # A window whose start is "today" means the adapter has no archive the
        # pipeline can reach: it is capture-forward only and deeper history is
        # NOT retrievable by re-running capture.
        capture_forward_only = start == day or start == "-"
        cap = source_registry.get(source)
        declared = cap.backfill if cap else "unknown"
        gaps = sorted(d30 - days_seen)
        if declared == source_registry.BACKFILL_FORWARD_ONLY:
            expectation = "thin history EXPECTED (capture-forward only adapter)"
        elif gaps and failures:
            expectation = "gap with retryable failures — retry, then re-audit"
        elif gaps:
            expectation = "GAP WITHOUT RECORDED FAILURE — investigate the job/adapter"
        else:
            expectation = "complete for D30"
        out[source] = {
            "declared_backfill_mode": declared,
            "gap_expectation": expectation,
            "first_local_date": min(days_seen) if days_seen else None,
            "latest_local_date": max(days_seen) if days_seen else None,
            "distinct_local_dates": len(days_seen),
            "capture_window": f"{start}..{end}",
            "capture_forward_only": capture_forward_only,
            "missing_dates_in_d30": sorted(d30 - days_seen)[:40],
            "missing_dates_in_d30_count": len(d30 - days_seen),
            "retryable_failure_dates": failures,
            "deeper_backfill_possible": (not capture_forward_only) and bool(d30 - days_seen),
        }
    return out


def warehouse_tables(localdata: Path) -> set[str]:
    path = localdata / "warehouse.duckdb"
    if not path.exists():
        return set()
    try:
        import duckdb

        con = duckdb.connect(str(path), read_only=True)
        try:
            return {
                str(r[0])
                for r in con.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
                ).fetchall()
            }
        finally:
            con.close()
    except Exception:
        return set()


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------


def run_audit(
    *,
    localdata: Path,
    day: str,
    as_of: datetime | None = None,
    min_lead: int = DEFAULT_MIN_LEAD,
    examples: int = 10,
    sources: tuple[str, ...] = SAME_DAY_SOURCES,
) -> dict:
    engine = load_picks_engine()
    if engine is None:  # pragma: no cover - import guard
        return {"error": "could not import scripts/picks_today.py", "date": day}
    if as_of is None:
        as_of = engine.pick_run_as_of()

    tables = warehouse_tables(localdata)
    rows_by_source: dict[str, SourceDay] = {}
    per_source: dict[str, dict[tuple[str, str], dict]] = {}
    for source in sources:
        rows = load_day_rows(localdata, source, day)
        summary, fixtures = audit_source_day(
            source, rows, engine=engine, as_of=as_of, min_lead=min_lead,
            warehouse_tables=tables,
        )
        rows_by_source[source] = summary
        per_source[source] = fixtures

    validation = source_registry.load_validation_states(localdata, day)
    overlap = build_overlap(per_source, engine=engine, examples=examples)
    consensus = build_consensus_funnel(
        per_source, engine=engine, as_of=as_of, min_lead=min_lead, examples=examples
    )
    consensus_keys: set[tuple[str, str]] = set()
    for source in consensus["sources_1x2"]:
        consensus_keys |= set(per_source.get(source, {}))

    shadow_slate = build_shadow_candidates(
        per_source, engine=engine, as_of=as_of, min_lead=min_lead, day=day,
        validation=validation, limit=examples * 20,
    )
    voters = classify_voters(per_source, rows_by_source, engine=engine)
    odds = build_odds_funnel(
        localdata, day, consensus_keys, engine=engine, examples=examples,
        candidates_before_odds=consensus["fixtures_ml_scoreable_pre_match_eligible"],
    )
    warnings = source_registry.funnel_warnings(
        match_surface=consensus["match_surface"],
        scored_fixtures=consensus["fixtures_ml_scoreable"],
        live_candidates=consensus["fixtures_ml_scoreable_pre_match_eligible"],
        shadow_candidates=shadow_slate["candidate_count"],
        sources_with_1x2_rows=[
            s for s, r in rows_by_source.items() if r.has_1x2_signal
        ],
        candidates_before_odds=consensus["fixtures_ml_scoreable_pre_match_eligible"],
        odds_enriched=sum(
            v["overlap_with_consensus_surface"] for v in odds["sources"].values()
        ),
    )
    warnings += source_registry.registry_coverage_warnings(capture_windows())

    return {
        "schema": 1,
        "date": day,
        "as_of": as_of.isoformat(timespec="seconds"),
        "min_lead_minutes": min_lead,
        "per_source": {k: asdict(v) for k, v in rows_by_source.items()},
        "identity_overlap": overlap,
        "consensus_funnel": consensus,
        "kickoff_funnel": build_kickoff_funnel(rows_by_source),
        "shadow_expansion": build_shadow_expansion(per_source, engine=engine, examples=examples),
        "odds_funnel": odds,
        "voter_classification": voters,
        "shadow_candidates": shadow_slate,
        "source_registry": source_registry.describe(localdata, day),
        "warnings": warnings,
        "backfill_depth": build_backfill_depth(localdata, day, sources),
        "_rows": rows_by_source,
    }


_A_COLS = (
    ("source", "source"),
    ("raw", "raw_rows"),
    ("fixtures", "unique_fixtures"),
    ("kickoff", "has_kickoff"),
    ("ko_ok", "trusted_kickoff"),
    ("prematch", "pre_match_eligible"),
    ("1x2", "has_1x2_signal"),
    ("ou", "has_ou_signal"),
    ("btts", "has_btts_signal"),
    ("in_1x2", "in_consensus_surface"),
    ("used", "consumed_by_picks_engine"),
    ("wh", "warehouse_table_present"),
)


def render_markdown(report: dict) -> str:
    rows: dict[str, SourceDay] = report["_rows"]
    out: list[str] = [
        f"# Same-day source funnel — {report['date']}",
        "",
        f"as_of `{report['as_of']}`, min_lead {report['min_lead_minutes']}m. "
        "Read-only, no network; gates reused from scripts/picks_today.py.",
        "",
        "## A. Per-source same-day availability",
        "",
        "| " + " | ".join(h for h, _ in _A_COLS) + " |",
        "|" + "|".join("---" for _ in _A_COLS) + "|",
    ]
    for row in rows.values():
        out.append("| " + " | ".join(str(getattr(row, a)) for _, a in _A_COLS) + " |")
    out += ["", "Notes:"]
    out += [f"- **{r.source}**: {r.notes}" for r in rows.values()]

    ov = report["identity_overlap"]
    out += [
        "",
        "## B. Cross-source identity overlap",
        "",
        f"- fixture groups: {ov['fixture_groups']}",
        f"- single-source groups: {ov['single_source_groups']}",
        f"- two-source groups: {ov['two_source_groups']}",
        f"- three-plus-source groups: {ov['three_plus_source_groups']}",
        f"- reversed home/away risk groups: {ov['reversed_risk_groups']}",
        "",
    ]
    for kind, items in ov["examples"].items():
        if not items:
            continue
        out.append(f"Examples — {kind}:")
        out += [f"  - {', '.join(f'{k}={v}' for k, v in item.items())}" for item in items]

    cf = report["consensus_funnel"]
    out += [
        "",
        "## C. Consensus funnel",
        "",
        f"- match surface (union of {','.join(cf['sources_1x2'])}): **{cf['match_surface']}**",
        f"- fixtures with >=2 voters carrying 1X2 probs: **{cf['fixtures_with_2plus_voters']}**",
        f"- fixtures ML-meta can score (needs one of {','.join(cf['ml_anchor_sources'])}): "
        f"**{cf['fixtures_ml_scoreable']}**",
        f"- of those, pre-match eligible: **{cf['fixtures_ml_scoreable_pre_match_eligible']}**",
        "",
        "Drops:",
    ]
    out += [f"  - {k}: {v}" for k, v in sorted(cf["drops"].items())]
    for reason, items in cf["drop_examples"].items():
        out.append(f"Examples — {reason}:")
        out += [f"  - {', '.join(f'{k}={v}' for k, v in item.items())}" for item in items]

    out += ["", "## D. Kickoff / timing funnel", "",
            "| source | fixtures | has_kickoff | trusted | missing | untrusted | pre_match |",
            "|---|---:|---:|---:|---:|---:|---:|"]
    for source, k in report["kickoff_funnel"].items():
        out.append(
            f"| {source} | {k['unique_fixtures']} | {k['has_kickoff']} | {k['trusted_kickoff']} "
            f"| {k['missing_kickoff']} | {k['untrusted_kickoff']} | {k['pre_match_eligible']} |"
        )
    if cf["kickoff_drops"]:
        out += ["", "Same-day guard drops on the ML-scoreable surface:"]
        out += [f"  - {k}: {v}" for k, v in sorted(cf["kickoff_drops"].items())]
        for reason, items in cf["kickoff_drop_examples"].items():
            out.append(f"Examples — {reason}:")
            out += [f"  - {', '.join(f'{k}={v}' for k, v in item.items())}" for item in items]

    out += ["", "## A2. Voter classification", "",
            "| source | tier | role | raw | fixtures | 1x2 rows | blocker |",
            "|---|---|---|---:|---:|---:|---|"]
    for source, v in report["voter_classification"].items():
        out.append(
            f"| {source} | {v['tier']} | {v['role']} | {v['raw_rows']} | "
            f"{v['normalized_fixtures']} | {v['rows_with_1x2_signal']} | {v['blocker']} |"
        )

    sc = report["shadow_candidates"]
    out += [
        "",
        "## A3. Shadow candidates (NON-DISPATCH)",
        "",
        f"- shadow candidate fixtures: **{sc['candidate_count']}** (dispatchable: "
        f"{sc['dispatchable']})",
        f"- shadow voter sources today: {', '.join(sc['shadow_voter_sources']) or 'none'}",
        "",
        sc["note"],
        "",
    ]
    if sc["blocker_counts"]:
        out.append("Blockers:")
        out += [f"  - {k}: {v}" for k, v in sorted(sc["blocker_counts"].items())]

    if report["warnings"]:
        out += ["", "## A1. Roach detector warnings", ""]
        out += [f"- {w}" for w in report["warnings"]]

    sh = report["shadow_expansion"]
    out += [
        "",
        "## E0. Shadow voter expansion (diagnostic, NON-DISPATCH)",
        "",
        f"- certified voter sources: {','.join(sh['certified_voter_sources'])}",
        f"- shadow sources carrying 1X2 today: {','.join(sh['shadow_sources_with_1x2_today']) or 'none'}",
        f"- fixtures with >=2 certified voters: **{sh['fixtures_with_2plus_certified_voters']}**",
        f"- fixtures with >=2 voters if shadow admitted: "
        f"**{sh['fixtures_with_2plus_voters_if_shadow_admitted']}** "
        f"(+{sh['fixtures_gained_if_shadow_admitted']})",
        "",
        sh["note"],
    ]
    if sh["examples"]:
        out.append("Examples of fixtures that would gain a quorum:")
        out += [f"  - {e['fixture']} ({e['voters']})" for e in sh["examples"]]

    out += ["", "## E. Odds / pricing funnel", "",
            "| odds source | cached rows | fixtures | overlap with 1X2 surface | cov% |",
            "|---|---:|---:|---:|---:|"]
    for source, o in report["odds_funnel"]["sources"].items():
        out.append(
            f"| {source} | {o['cached_rows']} | {o['unique_fixtures']} | "
            f"{o['overlap_with_consensus_surface']} | {o['coverage_pct_of_consensus']} |"
        )
    out += ["", f"Diagnosis: **{report['odds_funnel']['diagnosis']}** "
            f"(candidates before odds: {report['odds_funnel']['candidates_before_odds']})"]
    for source, o in report["odds_funnel"]["sources"].items():
        if o["status"] != "ok":
            out.append(f"- {source}: {o['status']}")

    out += ["", "## F. Backfill depth / retryable gaps", "",
            "| source | first | latest | dates | capture window | fwd-only | missing in D30 | retryable | deeper possible |",
            "|---|---|---|---:|---|---|---:|---:|---|"]
    for source, b in report["backfill_depth"].items():
        out.append(
            f"| {source} | {b['first_local_date'] or '-'} | {b['latest_local_date'] or '-'} | "
            f"{b['distinct_local_dates']} | {b['capture_window']} | "
            f"{'yes' if b['capture_forward_only'] else 'no'} | {b['missing_dates_in_d30_count']} | "
            f"{len(b['retryable_failure_dates'])} | {'yes' if b['deeper_backfill_possible'] else 'no'} |"
        )
    out += ["", "Gap expectations:"]
    out += [f"  - {src}: {b['declared_backfill_mode']} — {b['gap_expectation']}"
            for src, b in report["backfill_depth"].items()]

    out += [
        "",
        "This audit is diagnostic only. It cannot create, promote or certify a pick, "
        "and a source appearing here with good numbers is NOT validated — see "
        "scripts/audit_source_settlement_coverage.py for settlement evidence.",
        "",
    ]
    return "\n".join(out)


def render_shadow_markdown(report: dict) -> str:
    sc = report["shadow_candidates"]
    out = [
        f"# Shadow candidates — {report['date']} (NON-DISPATCH)",
        "",
        f"dispatchable: **{sc['dispatchable']}**. {sc['note']}",
        "",
        f"- live voter sources: {', '.join(sc['live_voter_sources'])}",
        f"- shadow voter sources today: {', '.join(sc['shadow_voter_sources']) or 'none'}",
        f"- shadow candidate fixtures: **{sc['candidate_count']}**",
        "",
    ]
    if sc["blocker_counts"]:
        out += ["Blockers:", ""]
        out += [f"- {k}: {v}" for k, v in sorted(sc["blocker_counts"].items())]
        out.append("")
    if sc["candidates"]:
        out += ["| fixture | live voters | shadow voters | kickoff | blockers |",
                "|---|---|---|---|---|"]
        for row in sc["candidates"]:
            out.append(
                f"| {row['fixture']} | {','.join(row['live_voters']) or '-'} | "
                f"{','.join(row['shadow_voters'])} | {row['kickoff'] or '-'} | "
                f"{'; '.join(row['blockers']) or '-'} |"
            )
    else:
        out.append("No shadow candidate reached a two-voter quorum today.")
    out += ["", "These rows are evidence only. They are never dispatched and the "
            "pick engine does not read this file."]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat(), help="target date YYYY-MM-DD")
    parser.add_argument("--as-of", help="operational as_of ISO timestamp (default: engine's)")
    parser.add_argument("--min-lead", type=int, default=DEFAULT_MIN_LEAD)
    parser.add_argument("--examples", type=int, default=10)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-shadow-json", type=Path)
    parser.add_argument("--output-shadow-md", type=Path)
    parser.add_argument("--localdata", type=Path, default=LOCALDATA, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        day = date.fromisoformat(args.date).isoformat()
    except ValueError as exc:
        parser.error(str(exc))

    as_of = None
    if args.as_of:
        try:
            as_of = datetime.fromisoformat(args.as_of)
        except ValueError as exc:
            parser.error(str(exc))

    report = run_audit(
        localdata=args.localdata, day=day, as_of=as_of,
        min_lead=args.min_lead, examples=args.examples,
    )
    if "error" in report:
        print(report["error"], file=sys.stderr)
        return 1
    markdown = render_markdown(report)
    print(markdown)
    report.pop("_rows", None)

    for warning in report.get("warnings", []):
        print(warning, file=sys.stderr)

    shadow_md = render_shadow_markdown(report)
    for path, payload in (
        (args.output_json, json.dumps(report, indent=2, sort_keys=True)),
        (args.output_md, markdown),
        (args.output_shadow_json, json.dumps(report["shadow_candidates"], indent=2, sort_keys=True)),
        (args.output_shadow_md, shadow_md),
    ):
        if not path:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(payload)
        tmp.replace(path)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
