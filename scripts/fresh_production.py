#!/usr/bin/env python3
"""fresh_production — a betting lane rebuilt on the current source universe.

Why this lane exists
--------------------
The legacy lane's serving model consumes source-specific feature columns from
a source universe that no longer produces same-day rows. Scoring current
fixtures through it means zero-filling those columns, which is unsupported
inference dressed up as confidence. ``fresh_production`` therefore starts
again: its own features, its own walk-forward evidence, its own certification
registry, its own picks. The legacy lane stays untouched as ``legacy_baseline``
for comparison only.

Design rules
------------
1. **No inherited trust.** Historical rows are raw evidence; legacy certified
   edges and the legacy model are never authority here.
2. **No legacy-only predictor features.** Enforced by a denylist and a test.
3. **No unsupported imputation.** A missing required feature blocks the
   candidate; it is never silently filled with 0 / 0.333 / 0.5.
4. **No synthetic anything** in production artifacts.
5. **Deterministic.** Fixed seed, recorded feature list, recorded training and
   evaluation ranges, recorded source universe, recorded thresholds.
6. **Abstention is success** when evidence is insufficient; unsupported
   confidence is failure.
7. **Read-only over source data**, no network, no parked/degraded fetch paths.

Rule mining (Option A / C): deterministic consensus rules are mined and
walk-forward certified by date. Any probabilistic scoring is reported as
research until the calibration sample clears its gate.

Usage::

    PYTHONPATH=src python3 scripts/fresh_production.py \\
        --date 2026-09-30 --mode official --output-dir localdata
"""

from __future__ import annotations

import argparse
import csv
import gzip
import importlib.util
import json
import math
import statistics
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

from edgefactory import source_registry  # noqa: E402

MODEL_DIR_NAME = "models/fresh_production"
FEATURE_SCHEMA_VERSION = "fresh_production_features_v1"
MODEL_VERSION = "fresh_production_rules_v1"
RANDOM_SEED = 20260930

# Legacy-only predictor feature names. A fresh-production feature must never
# be one of these: they encode the retired source universe.
LEGACY_ONLY_FEATURES: frozenset[str] = frozenset({
    "fb_p", "zb_p", "sa_p", "sa_ht_p", "ht_p", "ht_diff", "ht_total",
    "kelly", "pred_total", "pred_diff", "pred_hs", "pred_gs",
    "goalsavg", "p_ng", "p_under", "p_gg", "rolling_hit_rate",
})

# Sources whose live prediction path is parked/degraded: usable as historical
# reference only, never as a fresh-production voter.
PARKED_PREDICTORS: frozenset[str] = frozenset({"forebet"})

MIN_VOTERS = 2
DEFAULT_TRAIN_DAYS = 180
DEFAULT_EVAL_DAYS = 90

# Certification gates. Reported verbatim in the Markdown artifact.
GATES = {
    "min_walkforward_sample": 200,
    "min_recent_sample_30d": 25,
    "min_hit_rate_lower_bound": 0.55,   # Wilson 95% lower bound
    "min_lift_over_base_rate": 0.03,
    "min_calibration_bucket_sample": 50,
    "max_ambiguity_rate": 0.05,
}

MAX_DISPATCH_PICKS_PER_DAY = 5
MAX_TOTAL_EXPOSURE_UNITS = 5.0
MIN_EDGE_TO_DISPATCH = 0.02
FLAT_STAKE_UNITS = 1.0


# --------------------------------------------------------------------------
# Source universe
# --------------------------------------------------------------------------


def fresh_production_voters() -> tuple[str, ...]:
    """Current-source 1X2 voters: every registered predictor except parked."""
    return tuple(
        c.name for c in source_registry.REGISTRY
        if "1x2" in c.markets and c.name not in PARKED_PREDICTORS
    )


def classify_source_roles() -> dict[str, str]:
    roles: dict[str, str] = {}
    voters = set(fresh_production_voters())
    for cap in source_registry.REGISTRY:
        if cap.name in PARKED_PREDICTORS:
            roles[cap.name] = "blocked_predictor"
        elif cap.pricing_only:
            roles[cap.name] = "pricing_provider"
        elif cap.donor_only:
            roles[cap.name] = "result_donor"
        elif cap.name in voters and cap.tier == source_registry.TIER_LIVE:
            roles[cap.name] = "fresh_production_live_voter"
        elif cap.name in voters:
            roles[cap.name] = "shadow_fresh_production_voter"
        elif cap.provides_kickoff:
            roles[cap.name] = "timing_provider"
        else:
            roles[cap.name] = "not_applicable"
    return roles


# --------------------------------------------------------------------------
# Data loading (read-only, no network)
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


def _num(value: object) -> float | None:
    text = str(value if value is not None else "").strip()
    if text in {"", "None", "nan", "-"}:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    return out if math.isfinite(out) else None


def probs_1x2(row: dict) -> tuple[float, float, float] | None:
    """Normalized (home, draw, away). No imputation: partial rows are rejected."""
    trio = [_num(row.get(k)) for k in ("p1", "px", "p2")]
    if any(v is None for v in trio):
        return None
    total = sum(trio)  # type: ignore[arg-type]
    if total <= 0:
        return None
    return tuple(v / total for v in trio)  # type: ignore[return-value]


def _day(value: object) -> str | None:
    raw = str(value or "").strip()[:10]
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        return None


def team_key(name: object) -> str:
    from edgefactory.identity import source_team_key

    return source_team_key(name)


@dataclass
class FixtureGroup:
    date: str
    key: tuple[str, str]
    home: str
    away: str
    league: str = ""
    votes: dict[str, tuple[float, float, float]] = field(default_factory=dict)
    kickoff: str = ""
    kickoff_source: str = ""
    ambiguous: bool = False
    reversed_risk: bool = False
    raw_variants: dict[str, set[tuple[str, str]]] = field(default_factory=dict)


def load_fixture_groups(
    localdata: Path,
    *,
    start: str,
    end: str,
    voters: tuple[str, ...],
    engine=None,
) -> dict[tuple[str, tuple[str, str]], FixtureGroup]:
    """Group current-source prediction rows into fixtures. No fabrication."""
    groups: dict[tuple[str, tuple[str, str]], FixtureGroup] = {}
    kickoff_capable = set(source_registry.kickoff_providers())
    for source in voters:
        cap = source_registry.get(source)
        for path in source_files(localdata, source):
            for row in iter_rows(path):
                day = _day(row.get("date"))
                if day is None or not (start <= day <= end):
                    continue
                home, away = row.get("home"), row.get("away")
                if not home or not away:
                    continue
                key = (team_key(home), team_key(away))
                if len(key[0]) < 4 or len(key[1]) < 4:
                    continue
                probs = probs_1x2(row)
                if probs is None:
                    continue
                gid = (day, key)
                group = groups.get(gid)
                if group is None:
                    group = FixtureGroup(date=day, key=key, home=str(home), away=str(away),
                                         league=str(row.get("league") or ""))
                    groups[gid] = group
                group.raw_variants.setdefault(source, set()).add((str(home), str(away)))
                if source in group.votes and group.votes[source] != probs:
                    group.ambiguous = True
                group.votes[source] = probs
                if not group.kickoff and cap is not None and cap.provides_kickoff:
                    raw = row.get("kickoff") or row.get("time") or ""
                    if str(raw).strip() and engine is not None:
                        if engine.parse_kickoff_dt(str(raw)) is not None:
                            group.kickoff = str(raw).strip()
                            group.kickoff_source = source

    # Orientation and identity safety.
    for (day, key), group in groups.items():
        # Different spellings ACROSS sources are expected and are what the
        # identity key exists to reconcile. Two different spellings from the
        # SAME source collapsing onto one key means that source contributed two
        # distinct fixtures to one group: that is genuinely ambiguous.
        if any(len(v) > 1 for v in group.raw_variants.values()):
            group.ambiguous = True
        if (day, (key[1], key[0])) in groups:
            group.reversed_risk = True
    return groups


# --------------------------------------------------------------------------
# Settlement labels (conflict-safe, independent donors only)
# --------------------------------------------------------------------------


def load_settlement_labels(localdata: Path, *, start: str, end: str) -> dict[tuple[str, tuple[str, str]], dict]:
    """Conflict-safe labels: a fixture with disagreeing donors gets no label."""
    scores: dict[tuple[str, tuple[str, str]], dict[str, tuple[int, int]]] = defaultdict(dict)

    overlay = localdata / "settled_results.json"
    if overlay.exists():
        try:
            payload = json.loads(overlay.read_text())
        except (OSError, json.JSONDecodeError):
            payload = {}
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            day = _day(row.get("date"))
            hs, gs = _num(row.get("hs")), _num(row.get("gs"))
            if day is None or hs is None or gs is None or not (start <= day <= end):
                continue
            key = (team_key(row.get("home")), team_key(row.get("away")))
            if len(key[0]) < 4 or len(key[1]) < 4:
                continue
            scores[(day, key)][str(row.get("src") or "overlay")] = (int(hs), int(gs))

    for donor in ("betexplorer_results", "bettingclosed"):
        for path in source_files(localdata, donor):
            for row in iter_rows(path):
                day = _day(row.get("date"))
                hs, gs = _num(row.get("hs")), _num(row.get("gs"))
                if day is None or hs is None or gs is None or not (start <= day <= end):
                    continue
                key = (team_key(row.get("home")), team_key(row.get("away")))
                if len(key[0]) < 4 or len(key[1]) < 4:
                    continue
                scores[(day, key)][f"{donor}_csv"] = (int(hs), int(gs))

    labels: dict[tuple[str, tuple[str, str]], dict] = {}
    for gid, donors in scores.items():
        distinct = set(donors.values())
        if len(distinct) != 1:
            continue  # donor conflict: refuse to label
        hs, gs = next(iter(distinct))
        labels[gid] = {
            "hs": hs,
            "gs": gs,
            "outcome": "home" if hs > gs else ("away" if gs > hs else "draw"),
            "donors": sorted(donors),
            "donor_count": len(donors),
        }
    return labels


# --------------------------------------------------------------------------
# Feature extraction — current sources only
# --------------------------------------------------------------------------

FEATURE_SCHEMA: tuple[dict, ...] = (
    {"feature_name": "number_of_1x2_voters", "dtype": "int", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "timing_source_count", "dtype": "int", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "mean_home_prob", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "mean_draw_prob", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "mean_away_prob", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "min_top_prob", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "max_top_prob", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "std_top_prob", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "top_outcome", "dtype": "category", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "top_probability", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "second_probability", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "margin_top_vs_second", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "unanimous_outcome", "dtype": "bool", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "agreement_ratio", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "probability_entropy", "dtype": "float", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
    {"feature_name": "source_combination", "dtype": "category", "allowed_missing": False,
     "source": "current_source_consensus", "fresh_production_allowed": True},
)

REQUIRED_FEATURES: tuple[str, ...] = tuple(
    f["feature_name"] for f in FEATURE_SCHEMA if not f["allowed_missing"]
)


def build_features(group: FixtureGroup) -> dict | None:
    """Deterministic consensus features. Returns None when unsupported.

    Never imputes a missing probability: a fixture without at least
    ``MIN_VOTERS`` real voters simply has no feature vector.
    """
    if len(group.votes) < MIN_VOTERS:
        return None
    sources = sorted(group.votes)
    home = [group.votes[s][0] for s in sources]
    draw = [group.votes[s][1] for s in sources]
    away = [group.votes[s][2] for s in sources]
    means = {"home": statistics.fmean(home), "draw": statistics.fmean(draw),
             "away": statistics.fmean(away)}
    ordered = sorted(means.items(), key=lambda kv: kv[1], reverse=True)
    top_outcome, top_prob = ordered[0]
    second_prob = ordered[1][1]

    per_source_top = []
    for s in sources:
        trio = dict(zip(("home", "draw", "away"), group.votes[s]))
        per_source_top.append(max(trio, key=trio.get))
    agreement = per_source_top.count(top_outcome) / len(per_source_top)
    tops = [max(group.votes[s]) for s in sources]
    entropy = -sum(p * math.log(p) for p in means.values() if p > 0)

    return {
        "number_of_1x2_voters": len(sources),
        "timing_source_count": 1 if group.kickoff else 0,
        "mean_home_prob": means["home"],
        "mean_draw_prob": means["draw"],
        "mean_away_prob": means["away"],
        "min_top_prob": min(tops),
        "max_top_prob": max(tops),
        "std_top_prob": statistics.pstdev(tops) if len(tops) > 1 else 0.0,
        "top_outcome": top_outcome,
        "top_probability": top_prob,
        "second_probability": second_prob,
        "margin_top_vs_second": top_prob - second_prob,
        "unanimous_outcome": agreement == 1.0,
        "agreement_ratio": agreement,
        "probability_entropy": entropy,
        "source_combination": "+".join(sources),
    }


def validate_feature_names(names) -> list[str]:
    """Return any feature names that belong to the legacy-only bundle."""
    return sorted(set(map(str, names)) & LEGACY_ONLY_FEATURES)


def schema_violations(features: dict) -> list[str]:
    """Required-feature enforcement. No silent defaults."""
    missing = [name for name in REQUIRED_FEATURES if features.get(name) is None]
    return missing


# --------------------------------------------------------------------------
# Rules + walk-forward certification
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    rule_id: str
    min_voters: int
    min_top_probability: float
    require_unanimous: bool

    def matches(self, features: dict) -> bool:
        if features["number_of_1x2_voters"] < self.min_voters:
            return False
        if features["top_probability"] < self.min_top_probability:
            return False
        if self.require_unanimous and not features["unanimous_outcome"]:
            return False
        return True


def candidate_rules() -> tuple[Rule, ...]:
    rules = []
    for voters in (2, 3, 4):
        for threshold in (0.55, 0.60, 0.65, 0.70):
            for unanimous in (False, True):
                rules.append(Rule(
                    rule_id=(f"fresh_1x2_v{voters}_p{int(threshold * 100)}"
                             f"_{'unanimous' if unanimous else 'majority'}"),
                    min_voters=voters,
                    min_top_probability=threshold,
                    require_unanimous=unanimous,
                ))
    return tuple(rules)


def wilson_lower_bound(successes: int, total: int, z: float = 1.96) -> float:
    if total == 0:
        return 0.0
    p = successes / total
    denom = 1 + z * z / total
    centre = p + z * z / (2 * total)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return max(0.0, (centre - margin) / denom)


@dataclass
class RuleEvidence:
    rule_id: str
    sample: int = 0
    wins: int = 0
    recent_sample: int = 0
    recent_wins: int = 0
    hit_rate: float = 0.0
    hit_rate_lb: float = 0.0
    base_rate: float = 0.0
    lift: float = 0.0
    brier: float = 0.0
    calibration: list[dict] = field(default_factory=list)
    certified: bool = False
    blockers: list[str] = field(default_factory=list)


def walk_forward(
    groups: dict[tuple[str, tuple[str, str]], FixtureGroup],
    labels: dict[tuple[str, tuple[str, str]], dict],
    *,
    eval_start: str,
    eval_end: str,
    train_days: int,
) -> tuple[dict[str, RuleEvidence], dict]:
    """Date-based walk-forward. A fixture is only ever evaluated out-of-sample.

    For every evaluation day the rule set is fixed in advance (it is a static
    deterministic grid), and the day's outcomes are scored using ONLY labels
    for that day — no future information, no re-fitting on the evaluated day.
    The training window is recorded for provenance and is what a fitted model
    would consume; the rule grid itself carries no fitted parameters, which is
    exactly why it is safe to certify on out-of-sample results alone.
    """
    rules = candidate_rules()
    evidence = {r.rule_id: RuleEvidence(rule_id=r.rule_id) for r in rules}
    recent_cut = (date.fromisoformat(eval_end) - timedelta(days=30)).isoformat()

    scored_rows = 0
    labelled_rows = 0
    unlabelled_rows = 0
    conflicted = 0
    base_wins = 0
    base_total = 0
    per_rule_probs: dict[str, list[tuple[float, int]]] = defaultdict(list)

    for (day, _key), group in sorted(groups.items()):
        if not (eval_start <= day <= eval_end):
            continue
        if group.ambiguous or group.reversed_risk:
            conflicted += 1
            continue
        features = build_features(group)
        if features is None:
            continue
        scored_rows += 1
        label = labels.get((day, group.key))
        if label is None:
            unlabelled_rows += 1
            continue
        labelled_rows += 1
        won = 1 if label["outcome"] == features["top_outcome"] else 0
        base_wins += won
        base_total += 1
        for rule in rules:
            if not rule.matches(features):
                continue
            ev = evidence[rule.rule_id]
            ev.sample += 1
            ev.wins += won
            per_rule_probs[rule.rule_id].append((features["top_probability"], won))
            if day >= recent_cut:
                ev.recent_sample += 1
                ev.recent_wins += won

    base_rate = base_wins / base_total if base_total else 0.0

    for ev in evidence.values():
        if ev.sample:
            ev.hit_rate = ev.wins / ev.sample
            ev.hit_rate_lb = wilson_lower_bound(ev.wins, ev.sample)
            ev.base_rate = base_rate
            ev.lift = ev.hit_rate - base_rate
            pairs = per_rule_probs[ev.rule_id]
            ev.brier = sum((p - w) ** 2 for p, w in pairs) / len(pairs)
            buckets: dict[str, list[tuple[float, int]]] = defaultdict(list)
            for p, w in pairs:
                buckets[f"{int(p * 10) * 10}-{int(p * 10) * 10 + 10}%"].append((p, w))
            ev.calibration = [
                {
                    "bucket": name,
                    "sample": len(items),
                    "mean_predicted": round(statistics.fmean(p for p, _ in items), 4),
                    "observed_hit_rate": round(statistics.fmean(w for _, w in items), 4),
                    "sufficient_sample": len(items) >= GATES["min_calibration_bucket_sample"],
                }
                for name, items in sorted(buckets.items())
            ]
        ev.blockers = certification_blockers(ev, scored_rows, conflicted)
        ev.certified = not ev.blockers

    summary = {
        "evaluation_window": f"{eval_start}..{eval_end}",
        "training_window_days": train_days,
        "fixtures_with_features": scored_rows,
        "fixtures_labelled": labelled_rows,
        "fixtures_unlabelled": unlabelled_rows,
        "fixtures_rejected_ambiguous_or_reversed": conflicted,
        "base_rate_top_outcome": round(base_rate, 4),
        "labels_from_independent_donors": labelled_rows,
        "gates": GATES,
        "random_seed": RANDOM_SEED,
        "model_version": MODEL_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
    }
    return evidence, summary


def certification_blockers(ev: RuleEvidence, scored_rows: int, conflicted: int) -> list[str]:
    blockers: list[str] = []
    if ev.sample < GATES["min_walkforward_sample"]:
        blockers.append(
            f"insufficient_walkforward_sample ({ev.sample} < {GATES['min_walkforward_sample']})")
    if ev.recent_sample < GATES["min_recent_sample_30d"]:
        blockers.append(
            f"insufficient_recent_sample ({ev.recent_sample} < {GATES['min_recent_sample_30d']})")
    if ev.hit_rate_lb < GATES["min_hit_rate_lower_bound"]:
        blockers.append(
            f"hit_rate_lower_bound_below_gate ({ev.hit_rate_lb:.3f} < "
            f"{GATES['min_hit_rate_lower_bound']})")
    if ev.lift < GATES["min_lift_over_base_rate"]:
        blockers.append(
            f"insufficient_lift_over_base_rate ({ev.lift:.3f} < "
            f"{GATES['min_lift_over_base_rate']})")
    if not any(b["sufficient_sample"] for b in ev.calibration):
        blockers.append("blocked_insufficient_calibration_sample")
    total = scored_rows + conflicted
    if total and conflicted / total > GATES["max_ambiguity_rate"]:
        blockers.append("ambiguity_rate_above_gate")
    return blockers


# --------------------------------------------------------------------------
# Candidates and dispatch
# --------------------------------------------------------------------------


def load_event_identity(localdata: Path, day: str) -> dict[str, tuple[str, str]]:
    """event_id -> team key, from the result donor. Used to key donor prices.

    Some pricing feeds carry only an event identifier, no team names. Joining
    through the donor's own fixture list is an exact key join, never a fuzzy
    name match, so it cannot invent a fixture.
    """
    identity: dict[str, tuple[str, str]] = {}
    for path in source_files(localdata, "betexplorer_results"):
        for row in iter_rows(path):
            if _day(row.get("date")) != day:
                continue
            event_id = str(row.get("event_id") or "").strip()
            if not event_id:
                continue
            key = (team_key(row.get("home")), team_key(row.get("away")))
            if len(key[0]) < 4 or len(key[1]) < 4:
                continue
            identity[event_id] = key
    return identity


def load_odds_index(localdata: Path, day: str) -> dict[tuple[str, str], dict]:
    """Prices for the target date from existing pricing sources only.

    No price is ever synthesised: a fixture without a captured row simply has
    no entry, and the candidate is blocked on ``missing_odds``.
    """
    index: dict[tuple[str, str], dict] = {}
    identity = load_event_identity(localdata, day)
    for source in source_registry.names(source_registry.TIER_PRICING):
        for path in source_files(localdata, source):
            for row in iter_rows(path):
                if _day(row.get("date")) != day:
                    continue
                home, away = row.get("home"), row.get("away")
                if home and away:
                    key = (team_key(home), team_key(away))
                    method = "team_key"
                else:
                    key = identity.get(str(row.get("event_id") or "").strip())  # type: ignore[assignment]
                    method = "donor_event_id"
                if not key or len(key[0]) < 4 or len(key[1]) < 4:
                    continue
                index.setdefault(key, {"source": source, "row": row, "match_method": method})
    return index


def pick_odds(row: dict, outcome: str) -> float | None:
    column = {"home": "odd1", "draw": "oddx", "away": "odd2"}[outcome]
    value = _num(row.get(column))
    if value is None or value <= 1.0:
        return None
    return value


@dataclass
class Candidate:
    date: str
    kickoff: str | None
    league: str
    home: str
    away: str
    selection: str
    rule_id: str | None
    probability: float
    odds: float | None = None
    implied_probability: float | None = None
    edge: float | None = None
    source_voters: list[str] = field(default_factory=list)
    timing_source: str | None = None
    pricing_source: str | None = None
    identity_match_tier: str = "exact"
    settlement_label_source: str | None = None
    feature_schema_version: str = FEATURE_SCHEMA_VERSION
    model_version: str = MODEL_VERSION
    model_health_status: str = "unknown"
    walkforward_evidence: dict = field(default_factory=dict)
    dispatchable: bool = False
    blockers: list[str] = field(default_factory=list)
    stake_units: float = 0.0
    risk_label: str = "fresh_production_flat_stake"


def training_envelope(evidence: dict[str, RuleEvidence], groups, labels, *,
                      eval_start: str, eval_end: str) -> dict:
    """Observed feature ranges + seen source combinations, for the OOD guard."""
    voters: list[int] = []
    tops: list[float] = []
    agreements: list[float] = []
    combos: set[str] = set()
    for (day, _k), group in groups.items():
        if not (eval_start <= day <= eval_end):
            continue
        features = build_features(group)
        if features is None:
            continue
        voters.append(features["number_of_1x2_voters"])
        tops.append(features["top_probability"])
        agreements.append(features["agreement_ratio"])
        combos.add(features["source_combination"])
    if not voters:
        return {"empty": True, "source_combinations": []}
    return {
        "empty": False,
        "voters_min": min(voters), "voters_max": max(voters),
        "top_probability_min": min(tops), "top_probability_max": max(tops),
        "agreement_ratio_min": min(agreements), "agreement_ratio_max": max(agreements),
        "source_combinations": sorted(combos),
    }


def out_of_distribution_reasons(features: dict, envelope: dict) -> list[str]:
    if envelope.get("empty"):
        return ["blocked_out_of_distribution: no training envelope available"]
    reasons: list[str] = []
    if not (envelope["voters_min"] <= features["number_of_1x2_voters"] <= envelope["voters_max"]):
        reasons.append("blocked_out_of_distribution: voter count outside trained range")
    if not (envelope["top_probability_min"] <= features["top_probability"]
            <= envelope["top_probability_max"]):
        reasons.append("blocked_out_of_distribution: top_probability outside trained range")
    if not (envelope["agreement_ratio_min"] <= features["agreement_ratio"]
            <= envelope["agreement_ratio_max"]):
        reasons.append("blocked_out_of_distribution: agreement_ratio outside trained range")
    if features["source_combination"] not in set(envelope["source_combinations"]):
        reasons.append("unseen_source_combo")
    return reasons


def build_candidates(
    groups: dict[tuple[str, tuple[str, str]], FixtureGroup],
    *,
    day: str,
    evidence: dict[str, RuleEvidence],
    envelope: dict,
    odds_index: dict[tuple[str, str], dict],
    engine,
    as_of: datetime,
    min_lead: int,
    require_odds: bool = True,
) -> list[Candidate]:
    certified = [r for r in candidate_rules() if evidence.get(r.rule_id, RuleEvidence("")).certified]
    out: list[Candidate] = []

    for (gday, _key), group in sorted(groups.items()):
        if gday != day:
            continue
        features = build_features(group)
        cand = Candidate(
            date=day, kickoff=group.kickoff or None, league=group.league,
            home=group.home, away=group.away, selection="",
            rule_id=None, probability=0.0,
            source_voters=sorted(group.votes),
            timing_source=group.kickoff_source or None,
        )
        blockers: list[str] = []

        if features is None:
            blockers.append("blocked_missing_required_feature: fewer than "
                            f"{MIN_VOTERS} current-source 1X2 voters")
            cand.blockers = blockers
            cand.model_health_status = "abstained"
            out.append(cand)
            continue

        missing = schema_violations(features)
        if missing:
            blockers.append(f"blocked_missing_required_feature: {','.join(missing)}")

        cand.selection = features["top_outcome"]
        cand.probability = round(features["top_probability"], 4)

        if group.ambiguous:
            blockers.append("ambiguous_identity")
        if group.reversed_risk:
            blockers.append("reversed_orientation_risk")

        blockers.extend(out_of_distribution_reasons(features, envelope))

        matching = [r for r in certified if r.matches(features)]
        if matching:
            best = max(matching, key=lambda r: evidence[r.rule_id].hit_rate_lb)
            cand.rule_id = best.rule_id
            ev = evidence[best.rule_id]
            cand.walkforward_evidence = {
                "sample": ev.sample, "hit_rate": round(ev.hit_rate, 4),
                "hit_rate_lower_bound": round(ev.hit_rate_lb, 4),
                "recent_sample": ev.recent_sample, "brier": round(ev.brier, 4),
                "base_rate": round(ev.base_rate, 4),
            }
        else:
            blockers.append("no_certified_fresh_production_rule_matched")

        if not group.kickoff:
            blockers.append("missing_trusted_kickoff")
        else:
            ok, reason = engine.operational_pick_eligibility(
                {"date": day, "kickoff": group.kickoff}, as_of=as_of, min_lead=min_lead
            )
            if not ok:
                blockers.append(reason or "kickoff_guard")

        priced = odds_index.get(group.key)
        if priced:
            odds = pick_odds(priced["row"], features["top_outcome"])
            if odds:
                cand.odds = odds
                cand.pricing_source = priced["source"]
                cand.implied_probability = round(1.0 / odds, 4)
                cand.edge = round(features["top_probability"] - 1.0 / odds, 4)
                if cand.edge < MIN_EDGE_TO_DISPATCH:
                    blockers.append(
                        f"insufficient_edge_versus_price ({cand.edge:+.4f} < "
                        f"{MIN_EDGE_TO_DISPATCH})")
            else:
                blockers.append("missing_odds: no usable price for the selection")
        elif require_odds:
            blockers.append("missing_odds")

        cand.blockers = blockers
        cand.dispatchable = not blockers
        cand.model_health_status = "scored" if not blockers else "abstained"
        if cand.dispatchable:
            cand.stake_units = FLAT_STAKE_UNITS
        out.append(cand)

    dispatchable = [c for c in out if c.dispatchable]
    dispatchable.sort(key=lambda c: (-(c.edge or 0.0), -c.probability))
    cap = min(MAX_DISPATCH_PICKS_PER_DAY, int(MAX_TOTAL_EXPOSURE_UNITS // FLAT_STAKE_UNITS))
    for extra in dispatchable[cap:]:
        extra.dispatchable = False
        extra.stake_units = 0.0
        extra.blockers.append("daily_pick_cap_reached")
    return out


# --------------------------------------------------------------------------
# Health checks
# --------------------------------------------------------------------------


def model_health_checks(
    *, candidates: list[Candidate], evidence: dict[str, RuleEvidence], envelope: dict,
    feature_names,
) -> list[str]:
    warnings: list[str] = []
    leaked = validate_feature_names(feature_names)
    if leaked:
        warnings.append(
            f"MODEL_HEALTH: legacy-only predictor features present in the fresh lane: {leaked}")
    if envelope.get("empty"):
        warnings.append("MODEL_HEALTH: no training envelope — every candidate is out of distribution")
    scored = [c for c in candidates if c.model_health_status == "scored"]
    ood = [c for c in candidates if any(b.startswith("blocked_out_of_distribution") for b in c.blockers)]
    if ood:
        warnings.append(
            f"MODEL_HEALTH: {len(ood)} candidate(s) were out of distribution and were not dispatched")
    missing_feat = [c for c in candidates
                    if any(b.startswith("blocked_missing_required_feature") for b in c.blockers)]
    if missing_feat:
        warnings.append(
            f"MODEL_HEALTH: {len(missing_feat)} candidate(s) lacked required features and were not scored")
    if not any(ev.certified for ev in evidence.values()):
        warnings.append(
            "MODEL_HEALTH: no fresh_production rule is certified — the lane abstains by design")
    thin = [ev.rule_id for ev in evidence.values()
            if ev.sample and "blocked_insufficient_calibration_sample" in ev.blockers]
    if thin:
        warnings.append(
            f"MODEL_HEALTH: {len(thin)} rule(s) blocked on insufficient calibration sample")
    if scored and not any(c.dispatchable for c in candidates):
        warnings.append("MODEL_HEALTH: candidates were scored but none cleared dispatch gates")
    return warnings


def source_health_checks(
    *, groups, day: str, candidates: list[Candidate], evidence: dict[str, RuleEvidence],
    odds_index: dict, roles: dict[str, str],
) -> list[str]:
    warnings: list[str] = []
    today = [g for (d, _k), g in groups.items() if d == day]
    surface = len(today)
    with_quorum = sum(1 for g in today if len(g.votes) >= MIN_VOTERS)
    dispatchable = sum(1 for c in candidates if c.dispatchable)

    if surface >= 50 and with_quorum <= max(1, surface // 20):
        warnings.append(
            f"SOURCE_HEALTH: fresh_production surface is {surface} but only {with_quorum} "
            "fixture(s) reached a two-source quorum — identity overlap is the constraint")
    if with_quorum and not any(ev.certified for ev in evidence.values()):
        warnings.append(
            f"SOURCE_HEALTH: {with_quorum} fixture(s) have a current-source quorum but no "
            "fresh_production rule is certified yet — walk-forward evidence is the constraint")
    if any(ev.certified for ev in evidence.values()) and not any(c.rule_id for c in candidates):
        warnings.append(
            "SOURCE_HEALTH: certified fresh_production rules exist but no current candidate "
            "reaches them")
    if with_quorum and not odds_index:
        warnings.append(
            "SOURCE_HEALTH: fresh_production candidates exist but no pricing rows were captured "
            "for the target date")
    blocked = [name for name, role in roles.items() if role == "blocked_predictor"]
    if blocked:
        warnings.append(
            f"SOURCE_HEALTH: parked/degraded predictor(s) excluded from the fresh lane: "
            f"{','.join(sorted(blocked))}")
    if dispatchable == 0:
        warnings.append(
            "SOURCE_HEALTH: fresh_production produced no dispatchable picks — see the blocker "
            "table for the objective reason")
    return warnings


# --------------------------------------------------------------------------
# Artifacts
# --------------------------------------------------------------------------


def load_engine():
    path = ROOT / "scripts" / "picks_today.py"
    spec = importlib.util.spec_from_file_location("edgefactory_picks_today_fresh", path)
    if spec is None or spec.loader is None:  # pragma: no cover
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:  # pragma: no cover
        return None
    return module


def write_artifact(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload)
    tmp.replace(path)


def render_walkforward_md(summary: dict, evidence: dict[str, RuleEvidence]) -> str:
    out = [
        f"# fresh_production walk-forward — {summary['evaluation_window']}",
        "",
        f"- fixtures with features: {summary['fixtures_with_features']}",
        f"- fixtures labelled by independent donors: {summary['fixtures_labelled']}",
        f"- fixtures unlabelled: {summary['fixtures_unlabelled']}",
        f"- fixtures rejected (ambiguous/reversed): "
        f"{summary['fixtures_rejected_ambiguous_or_reversed']}",
        f"- base rate of the consensus top outcome: {summary['base_rate_top_outcome']}",
        f"- model version: `{summary['model_version']}`, feature schema "
        f"`{summary['feature_schema_version']}`, seed {summary['random_seed']}",
        "",
        "## Certification gates",
        "",
    ]
    out += [f"- `{k}`: {v}" for k, v in summary["gates"].items()]
    out += ["", "## Rule evidence", "",
            "| rule | sample | recent | hit rate | Wilson LB | lift | Brier | certified | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for ev in sorted(evidence.values(), key=lambda e: (-e.sample, e.rule_id)):
        if not ev.sample:
            continue
        out.append(
            f"| {ev.rule_id} | {ev.sample} | {ev.recent_sample} | {ev.hit_rate:.3f} | "
            f"{ev.hit_rate_lb:.3f} | {ev.lift:+.3f} | {ev.brier:.4f} | "
            f"{'yes' if ev.certified else 'no'} | {'; '.join(ev.blockers) or '-'} |"
        )
    out += ["", "Legacy certified edges are NOT authority here: this lane certifies "
            "independently on its own walk-forward evidence.", ""]
    return "\n".join(out)


def render_picks_md(day: str, candidates: list[Candidate], *, dispatch_only: bool) -> str:
    rows = [c for c in candidates if c.dispatchable] if dispatch_only else candidates
    title = "FRESH PRODUCTION PICKS" if dispatch_only else "FRESH PRODUCTION CANDIDATES"
    out = [f"# {title} — {day}", ""]
    if dispatch_only and not rows:
        out += ["## FRESH PRODUCTION — NO PICKS", "",
                "The lane abstained. Top rejected candidates and their exact blockers:", ""]
        ranked = sorted(candidates, key=lambda c: (len(c.blockers), -c.probability))[:10]
        out += ["| fixture | selection | prob | voters | kickoff | blockers |",
                "|---|---|---:|---|---|---|"]
        for c in ranked:
            out.append(
                f"| {c.home} vs {c.away} | {c.selection or '-'} | {c.probability:.3f} | "
                f"{','.join(c.source_voters) or '-'} | {c.kickoff or '-'} | "
                f"{'; '.join(c.blockers)} |")
        out += ["", "Abstention is the correct outcome when evidence is insufficient.", ""]
        return "\n".join(out)

    out += ["| fixture | league | kickoff | selection | prob | odds | implied | edge | rule | "
            "voters | timing | pricing | stake | model health | blockers |",
            "|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---:|---|---|"]
    for c in rows:
        out.append(
            f"| {c.home} vs {c.away} | {c.league or '-'} | {c.kickoff or '-'} | "
            f"{c.selection or '-'} | {c.probability:.3f} | {c.odds or '-'} | "
            f"{c.implied_probability or '-'} | {c.edge if c.edge is not None else '-'} | "
            f"{c.rule_id or '-'} | {','.join(c.source_voters) or '-'} | {c.timing_source or '-'} | "
            f"{c.pricing_source or '-'} | {c.stake_units} | {c.model_health_status} | "
            f"{'; '.join(c.blockers) or '-'} |")
    out += ["", f"Stake policy: flat {FLAT_STAKE_UNITS} unit, max "
            f"{MAX_DISPATCH_PICKS_PER_DAY} picks/day, max "
            f"{MAX_TOTAL_EXPOSURE_UNITS} units total exposure, fresh_production lane "
            "(NOT legacy_baseline).", ""]
    return "\n".join(out)


def render_model_health_md(day: str, summary: dict, warnings: list[str],
                           evidence: dict[str, RuleEvidence], envelope: dict) -> str:
    certified = [ev for ev in evidence.values() if ev.certified]
    out = [
        f"# model_health — fresh_production — {day}",
        "",
        "## Model card",
        "",
        f"- model version: `{MODEL_VERSION}`",
        f"- feature schema: `{FEATURE_SCHEMA_VERSION}`",
        f"- random seed: {RANDOM_SEED} (deterministic; no generative component)",
        f"- source universe: {', '.join(fresh_production_voters())}",
        f"- parked/degraded predictors excluded: {', '.join(sorted(PARKED_PREDICTORS))}",
        f"- evaluation window: {summary['evaluation_window']}",
        f"- training window: {summary['training_window_days']} days",
        f"- features: {', '.join(f['feature_name'] for f in FEATURE_SCHEMA)}",
        f"- certification gates: {json.dumps(summary['gates'])}",
        f"- certified rules: {len(certified)}",
        "",
        "## Distribution envelope",
        "",
        f"```json\n{json.dumps({k: v for k, v in envelope.items() if k != 'source_combinations'}, indent=2)}\n```",
        "",
        "## Calibration (certified rules)",
        "",
    ]
    if certified:
        out += ["| rule | bucket | sample | mean predicted | observed | sufficient |",
                "|---|---|---:|---:|---:|---|"]
        for ev in certified:
            for bucket in ev.calibration:
                out.append(
                    f"| {ev.rule_id} | {bucket['bucket']} | {bucket['sample']} | "
                    f"{bucket['mean_predicted']} | {bucket['observed_hit_rate']} | "
                    f"{'yes' if bucket['sufficient_sample'] else 'no'} |")
    else:
        out.append("No certified rule: no probability is used for dispatch.")
    out += ["", "## model_health_checks", ""]
    out += [f"- {w}" for w in warnings] or ["- none"]
    out += ["", "No generative model is used anywhere in this lane. Every number above "
            "derives from deterministic code over captured source rows.", ""]
    return "\n".join(out)


def render_source_health_md(day: str, roles: dict[str, str], warnings: list[str],
                            groups, odds_index: dict) -> str:
    today = [g for (d, _k), g in groups.items() if d == day]
    out = [
        f"# source_health — fresh_production — {day}",
        "",
        f"- fixture groups today: {len(today)}",
        f"- groups with >= {MIN_VOTERS} current-source voters: "
        f"{sum(1 for g in today if len(g.votes) >= MIN_VOTERS)}",
        f"- groups with a trusted kickoff: {sum(1 for g in today if g.kickoff)}",
        f"- groups flagged ambiguous: {sum(1 for g in today if g.ambiguous)}",
        f"- groups flagged reversed-orientation risk: {sum(1 for g in today if g.reversed_risk)}",
        f"- priced fixtures available: {len(odds_index)}",
        "",
        "## Source roles",
        "",
        "| source | role |",
        "|---|---|",
    ]
    out += [f"| {name} | {role} |" for name, role in sorted(roles.items())]
    out += ["", "## source_health_warnings", ""]
    out += [f"- {w}" for w in warnings] or ["- none"]
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def run(
    *,
    localdata: Path,
    day: str,
    output_dir: Path,
    train_days: int = DEFAULT_TRAIN_DAYS,
    eval_days: int = DEFAULT_EVAL_DAYS,
    as_of: datetime | None = None,
    min_lead: int = 30,
    write: bool = True,
) -> dict:
    engine = load_engine()
    if engine is None:  # pragma: no cover
        return {"error": "could not load the pick engine"}
    if as_of is None:
        as_of = engine.pick_run_as_of()

    target = date.fromisoformat(day)
    eval_start = (target - timedelta(days=eval_days)).isoformat()
    history_start = (target - timedelta(days=eval_days + train_days)).isoformat()

    voters = fresh_production_voters()
    roles = classify_source_roles()
    groups = load_fixture_groups(localdata, start=history_start, end=day,
                                 voters=voters, engine=engine)
    labels = load_settlement_labels(localdata, start=history_start, end=day)

    evidence, summary = walk_forward(
        groups, labels, eval_start=eval_start,
        eval_end=(target - timedelta(days=1)).isoformat(), train_days=train_days,
    )
    envelope = training_envelope(
        evidence, groups, labels, eval_start=eval_start,
        eval_end=(target - timedelta(days=1)).isoformat(),
    )
    odds_index = load_odds_index(localdata, day)
    candidates = build_candidates(
        groups, day=day, evidence=evidence, envelope=envelope, odds_index=odds_index,
        engine=engine, as_of=as_of, min_lead=min_lead,
    )

    feature_names = [f["feature_name"] for f in FEATURE_SCHEMA]
    model_warnings = model_health_checks(
        candidates=candidates, evidence=evidence, envelope=envelope, feature_names=feature_names)
    src_warnings = source_health_checks(
        groups=groups, day=day, candidates=candidates, evidence=evidence,
        odds_index=odds_index, roles=roles)

    certified_payload = {
        "schema": 1,
        "generated_for": day,
        "model_version": MODEL_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "note": (
            "fresh_production certification registry. Independent of the legacy "
            "certified-edges registry; legacy certification is never inherited."
        ),
        "gates": GATES,
        "certified_rules": [asdict(ev) for ev in evidence.values() if ev.certified],
        "rejected_rules": [asdict(ev) for ev in evidence.values()
                           if ev.sample and not ev.certified],
    }
    dispatchable = [c for c in candidates if c.dispatchable]

    report = {
        "schema": 1,
        "lane": "fresh_production",
        "date": day,
        "as_of": as_of.isoformat(timespec="seconds"),
        "source_universe": list(voters),
        "source_roles": roles,
        "parked_excluded": sorted(PARKED_PREDICTORS),
        "walkforward": summary,
        "envelope": envelope,
        "certified_rule_count": len(certified_payload["certified_rules"]),
        "candidate_count": len(candidates),
        "dispatchable_count": len(dispatchable),
        "model_health_warnings": model_warnings,
        "source_health_warnings": src_warnings,
        "feature_schema": list(FEATURE_SCHEMA),
        "candidates": [asdict(c) for c in candidates],
        "dispatchable_picks": [asdict(c) for c in dispatchable],
        "_evidence": evidence,
        "_certified_payload": certified_payload,
    }

    if write:
        out = output_dir
        model_dir = out / MODEL_DIR_NAME
        write_artifact(out / f"fresh_production_walkforward_{day}.json",
                       json.dumps({"summary": summary,
                                   "rules": [asdict(e) for e in evidence.values() if e.sample]},
                                  indent=2, sort_keys=True))
        write_artifact(out / f"fresh_production_walkforward_{day}.md",
                       render_walkforward_md(summary, evidence))
        write_artifact(out / f"fresh_production_certified_edges_{day}.json",
                       json.dumps(certified_payload, indent=2, sort_keys=True))
        write_artifact(out / "fresh_production_certified_edges.json",
                       json.dumps(certified_payload, indent=2, sort_keys=True))
        write_artifact(out / f"fresh_production_certified_edges_{day}.md",
                       render_walkforward_md(summary, evidence))
        write_artifact(out / f"fresh_production_candidate_picks_{day}.json",
                       json.dumps([asdict(c) for c in candidates], indent=2, sort_keys=True))
        write_artifact(out / f"fresh_production_candidate_picks_{day}.md",
                       render_picks_md(day, candidates, dispatch_only=False))
        write_artifact(out / f"fresh_production_dispatchable_picks_{day}.json",
                       json.dumps([asdict(c) for c in dispatchable], indent=2, sort_keys=True))
        write_artifact(out / f"fresh_production_dispatchable_picks_{day}.md",
                       render_picks_md(day, candidates, dispatch_only=True))
        write_artifact(out / f"model_health_{day}.json",
                       json.dumps({"warnings": model_warnings, "envelope": envelope,
                                   "model_version": MODEL_VERSION,
                                   "feature_schema_version": FEATURE_SCHEMA_VERSION,
                                   "random_seed": RANDOM_SEED,
                                   "source_universe": list(voters),
                                   "gates": GATES}, indent=2, sort_keys=True))
        write_artifact(out / f"model_health_{day}.md",
                       render_model_health_md(day, summary, model_warnings, evidence, envelope))
        write_artifact(out / f"source_health_{day}.json",
                       json.dumps({"roles": roles, "warnings": src_warnings}, indent=2,
                                  sort_keys=True))
        write_artifact(out / f"source_health_{day}.md",
                       render_source_health_md(day, roles, src_warnings, groups, odds_index))
        write_artifact(model_dir / "feature_schema.json",
                       json.dumps({"version": FEATURE_SCHEMA_VERSION,
                                   "features": list(FEATURE_SCHEMA),
                                   "legacy_only_denylist": sorted(LEGACY_ONLY_FEATURES)},
                                  indent=2, sort_keys=True))
        write_artifact(model_dir / f"model_card_{day}.md",
                       render_model_health_md(day, summary, model_warnings, evidence, envelope))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--mode", default="official", choices=("official", "research"))
    parser.add_argument("--output-dir", type=Path, default=LOCALDATA)
    parser.add_argument("--localdata", type=Path, default=LOCALDATA)
    parser.add_argument("--train-days", type=int, default=DEFAULT_TRAIN_DAYS)
    parser.add_argument("--eval-days", type=int, default=DEFAULT_EVAL_DAYS)
    parser.add_argument("--as-of")
    parser.add_argument("--min-lead", type=int, default=30)
    parser.add_argument("--no-write", action="store_true")
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

    report = run(localdata=args.localdata, day=day, output_dir=args.output_dir,
                 train_days=args.train_days, eval_days=args.eval_days, as_of=as_of,
                 min_lead=args.min_lead, write=not args.no_write)
    if "error" in report:
        print(report["error"], file=sys.stderr)
        return 1

    print(f"fresh_production {day}: source universe = {', '.join(report['source_universe'])}")
    print(f"  walk-forward: {report['walkforward']['fixtures_labelled']} labelled fixtures, "
          f"{report['certified_rule_count']} certified rule(s)")
    print(f"  candidates: {report['candidate_count']}, dispatchable: "
          f"{report['dispatchable_count']}")
    for warning in report["source_health_warnings"] + report["model_health_warnings"]:
        print(f"  {warning}", file=sys.stderr)
    if report["dispatchable_count"] == 0:
        print("  FRESH PRODUCTION — NO PICKS (see the candidate artifact for exact blockers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
