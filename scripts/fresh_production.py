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

from edgefactory import selection_evidence
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
# Single source of truth lives in the capability registry.
PARKED_PREDICTORS: frozenset[str] = source_registry.PARKED_PREDICTORS

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
# A selection must not be priced at a loss, but the SIZE of a positive
# edge is a grading question, not a gate. The old 0.02 floor vetoed
# thin-but-positive selections upstream, so the assayer, the bucket
# ladder and the P&L tripwire never saw them and could never learn
# whether a thin-edge bucket pays. Those mechanisms demote and bench a
# bucket that loses, which is the correct judge of a thin edge.
# Operator direction 2026-10-01: reject a negative edge only.
MIN_EDGE_TO_DISPATCH = 0.0

# Dispatch paths. A certified *rule* is a deterministic consensus threshold: it
# needs the inputs the rule itself reads, and nothing more. Requiring the full
# model feature vector from a rule-based pick was blocking candidates on
# evidence the rule never consults, so the two paths are now separate.
DISPATCH_RULE = "certified_rule"
DISPATCH_MODEL = "certified_model"

# The rule inputs. Only these are mandatory for certified_rule_dispatch.
RULE_INPUT_FEATURES: tuple[str, ...] = (
    "number_of_1x2_voters", "top_outcome", "top_probability", "unanimous_outcome",
)

# Blocker vocabulary. Every blocker string starts with one of these so the
# summary can count them and the operator never sees a generic reason.
BLOCKER_VOTER_QUORUM = "insufficient_voter_quorum"
BLOCKER_MISSING_FEATURE = "blocked_missing_required_feature"
BLOCKER_MISSING_ODDS = "missing_odds"
BLOCKER_SUSPECT_PRICE = "suspect_price"
BLOCKER_INSUFFICIENT_EDGE = "insufficient_edge_versus_price"
BLOCKER_MISSING_KICKOFF = "missing_trusted_kickoff"
BLOCKER_KICKOFF_GUARD = "kickoff_guard"
BLOCKER_IDENTITY = "ambiguous_or_missing_identity"
BLOCKER_ORIENTATION = "reversed_orientation_risk"
BLOCKER_NO_RULE = "no_certified_fresh_production_rule_matched"
BLOCKER_OOD = "blocked_out_of_distribution"
BLOCKER_CALIBRATION = "blocked_insufficient_calibration_sample"
BLOCKER_CAP = "daily_pick_cap_reached"

# Rule lifecycle. "certified" in the headline means dispatch-eligible.
RULE_CERTIFIED = "certified_dispatchable"
RULE_RESEARCH = "research"
RULE_BLOCKED = "blocked"

# Pricing tiers, most authoritative first.
PRICE_TIER_DEDICATED = "dedicated_pricing_feed"
PRICE_TIER_SOURCE_EMBEDDED = "source_embedded_price"
FLAT_STAKE_UNITS = 1.0
# The pick engine states who owns staking rather than sizing a bet itself.
#
# Buckets are the canonical taxonomy from the established engine. They key
# audits, CLV grouping, assayer context, bucket P&L, the selection ladder
# and historical comparability, so the production lane must not mint one of
# its own: a lane-specific bucket has no history, grades against nothing and
# splits every downstream comparison. Production identity travels in its own
# fields instead (see PRODUCTION_SCOPE below).
BUCKET_CERTIFIED_CLEAN = "CERTIFIED_CLEAN"
BUCKET_WATCHLIST_NO_ODDS = "WATCHLIST_NO_ODDS"
BUCKET_WATCHLIST_UNCORROBORATED_PRICE = "WATCHLIST_UNCORROBORATED_PRICE"
BUCKET_WATCHLIST_SUSPECT_PRICE = "WATCHLIST_SUSPECT_PRICE"

# What the lane records instead of a bucket, so a production selection stays
# identifiable everywhere without disturbing the taxonomy.
PRODUCTION_SCOPE = "production"


def canonical_bucket(*, odds, price_evidence=None,
                     price_quarantine_reason=None) -> str:
    """The canonical bucket for a production selection.

    This reproduces the price-integrity precedence of the engine's
    ``bucket_pick`` -- suspect fuzzy price, then sole-source price, then
    missing odds -- using only fields the production lane actually has.

    Documented limitation: the production lane computes no context
    (``ctx``), so the context-dependent outcomes of ``bucket_pick``
    (``CAUTION``, ``WATCHLIST_UNKNOWN_CTX``, ``SKIPPED_VETO``,
    ``SKIPPED_DEAD_EDGE``) cannot be reached from here. A selection that
    clears the lane's own gates and carries a clean price is therefore
    ``CERTIFIED_CLEAN``. Wiring the context resolver into this lane would
    change gating and is deliberately out of scope; until then this
    function must not be described as a full reimplementation of
    ``bucket_pick``.
    """
    reason = str(price_quarantine_reason or "")
    evidence = str(price_evidence or "")
    if reason == "alias_fuzzy" or evidence == "SUSPECT_ALIAS_FUZZY":
        return BUCKET_WATCHLIST_SUSPECT_PRICE
    if reason == "scoutingstats_sole_source" or \
            evidence == "SCOUTINGSTATS_SOLE":
        return BUCKET_WATCHLIST_UNCORROBORATED_PRICE
    if odds is None:
        return BUCKET_WATCHLIST_NO_ODDS
    return BUCKET_CERTIFIED_CLEAN
STAKING_POLICY = "handled_by_auto_tickets"
STAKING_OWNER = "auto_tickets"


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
    kickoff_observations: list[dict] = field(default_factory=list)
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
    record_timing_from: str | None = None,
) -> dict[tuple[str, tuple[str, str]], FixtureGroup]:
    """Group current-source prediction rows into fixtures. No fabrication."""
    groups: dict[tuple[str, tuple[str, str]], FixtureGroup] = {}
    # Timing observations are only kept for the dates we might bet on:
    # recording them across the whole training history would be noise.
    timing_from = record_timing_from or end
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
                raw = str(row.get("kickoff") or row.get("time") or "").strip()
                if raw and day >= timing_from:
                    # Record every kickoff any source offered for the target
                    # date, whether or not we are allowed to trust it. Without
                    # this the blocker cannot distinguish "nobody published a
                    # kickoff" from "we refused the one that was published".
                    trusted = cap is not None and cap.provides_kickoff
                    parsed = (engine.parse_kickoff_dt(raw, day) is not None
                              if engine is not None else None)
                    group.kickoff_observations.append(
                        {"source": source, "raw": raw,
                         "timing_capable": bool(trusted), "parsed": parsed})
                    if trusted and parsed and not group.kickoff:
                        group.kickoff = raw
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


# Rule identifiers describe the rule, not a release. The old ``v2``/``v3``
# suffix was never a version: it was the required voter count, which reads as
# a version number and invites the wrong question ("is v3 newer than v2?").
# The lane is also the production lane now, so a ``fresh_`` prefix
# distinguishes it from nothing.
VOTER_COUNT_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def rule_identifier(voters: int, threshold: float, unanimous: bool) -> str:
    """Canonical production rule ID, e.g. ``1x2_two_source_p55_unanimous``."""
    word = VOTER_COUNT_WORDS.get(voters, f"{voters}")
    return (f"1x2_{word}_source_p{int(round(threshold * 100))}"
            f"_{'unanimous' if unanimous else 'majority'}")


def legacy_rule_identifier(voters: int, threshold: float, unanimous: bool) -> str:
    """The retired identifier, kept only to read artifacts written before the
    rename. Never written to a new artifact and never displayed."""
    return (f"fresh_1x2_v{voters}_p{int(round(threshold * 100))}"
            f"_{'unanimous' if unanimous else 'majority'}")


def deprecated_rule_aliases() -> dict[str, str]:
    """Retired rule ID -> current rule ID.

    Internal compatibility only: it lets a stored artifact or warehouse row
    written before the rename resolve to the rule it actually means. Nothing
    reading this map may surface the retired identifier to an operator.
    """
    aliases = {}
    for voters in (2, 3, 4):
        for threshold in (0.55, 0.60, 0.65, 0.70):
            for unanimous in (False, True):
                aliases[legacy_rule_identifier(voters, threshold, unanimous)] = \
                    rule_identifier(voters, threshold, unanimous)
    return aliases


def resolve_rule_id(rule_id: str | None) -> str | None:
    """Map a possibly-retired rule ID onto the current one."""
    if not rule_id:
        return rule_id
    return deprecated_rule_aliases().get(rule_id, rule_id)


def candidate_rules() -> tuple[Rule, ...]:
    rules = []
    for voters in (2, 3, 4):
        for threshold in (0.55, 0.60, 0.65, 0.70):
            for unanimous in (False, True):
                rules.append(Rule(
                    rule_id=rule_identifier(voters, threshold, unanimous),
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
    calibration_sample: int = 0
    status: str = RULE_BLOCKED
    certified: bool = False          # dispatch-eligible for certified_rule
    model_eligible: bool = False     # additionally passes the calibration gate
    blockers: list[str] = field(default_factory=list)
    model_blockers: list[str] = field(default_factory=list)


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
        ev.calibration_sample = max((b["sample"] for b in ev.calibration), default=0)
        ev.blockers = rule_certification_blockers(ev, scored_rows, conflicted)
        ev.model_blockers = list(ev.blockers)
        if not any(b["sufficient_sample"] for b in ev.calibration):
            ev.model_blockers.append(
                f"{BLOCKER_CALIBRATION} (largest bucket {ev.calibration_sample} < "
                f"{GATES['min_calibration_bucket_sample']})")
        ev.certified = not ev.blockers
        ev.model_eligible = not ev.model_blockers
        ev.status = classify_rule(ev)

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


def classify_rule(ev: RuleEvidence) -> str:
    """Honest three-way lifecycle.

    ``certified_dispatchable`` means the rule may produce a real bet today,
    subject only to candidate-specific gates (price, kickoff, identity).
    ``research`` means it shows promise but has not cleared every gate, so it
    is reported and tracked but can never dispatch. ``blocked`` means it has
    no usable evidence. A rule that can never dispatch is never counted as
    certified.
    """
    if ev.certified:
        return RULE_CERTIFIED
    if ev.sample and ev.lift > 0 and ev.hit_rate_lb > ev.base_rate:
        return RULE_RESEARCH
    return RULE_BLOCKED


def rule_certification_blockers(ev: RuleEvidence, scored_rows: int,
                                conflicted: int) -> list[str]:
    """Gates for certified_rule dispatch.

    The calibration-bucket gate is deliberately NOT here: a threshold rule
    emits a decision, not a calibrated probability, so a thin probability
    bucket cannot invalidate it. That gate lives in ``model_blockers`` and
    governs certified_model dispatch only.
    """
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
    total = scored_rows + conflicted
    if total and conflicted / total > GATES["max_ambiguity_rate"]:
        blockers.append("ambiguity_rate_above_gate")
    return blockers


# --------------------------------------------------------------------------
# Candidates and dispatch
# --------------------------------------------------------------------------


def _source_embedded_price_rows(localdata: Path, day: str,
                                voters: tuple[str, ...]) -> list[dict]:
    """1X2 prices already present inside captured predictor rows.

    Several predictor sources publish the bookmaker price next to their
    forecast (``odd1``/``oddx``/``odd2``). That is a real captured price from
    an existing source — not a new feed, not a fetch, not a fabrication — so
    it is offered as a lower-priority pricing tier behind the dedicated feeds
    and is always labelled ``source_embedded_price`` on the pick.
    """
    rows: list[dict] = []
    for source in voters:
        for path in source_files(localdata, source):
            for row in iter_rows(path):
                if _day(row.get("date")) != day:
                    continue
                if not row.get("home") or not row.get("away"):
                    continue
                base = {
                    "date": day,
                    "kickoff": row.get("kickoff") or row.get("time") or "",
                    "league": row.get("league") or "",
                    "home": row.get("home"), "away": row.get("away"),
                    "captured_at": "", "bookmaker": f"{source}_embedded",
                }
                for selection, column in (("home", "odd1"), ("draw", "oddx"),
                                          ("away", "odd2")):
                    value = _num(row.get(column))
                    if value is None or value <= 1.0:
                        continue
                    rows.append({**base, "market": "1x2", "selection": selection,
                                 "odds": value})
    return rows


def build_price_board(engine, localdata: Path, day: str,
                      voters: tuple[str, ...]) -> dict:
    """Assemble every existing price source into engine-shaped bundles.

    Reuses the pick engine's own audited join (exact key, alias-time,
    orientation-checked fuzzy) rather than reimplementing matching. Nothing
    here fetches: only rows already captured on disk are read.
    """
    board: list[tuple[str, str, dict]] = []
    stats: dict[str, dict] = {}

    # The engine reads its caches from its own module-level LOCALDATA. Point
    # it at the directory this run was given so ``--localdata`` is honoured
    # and tests stay isolated from the real repository data.
    previous_localdata = getattr(engine, "LOCALDATA", None)
    try:
        engine.LOCALDATA = Path(localdata)
        _collect_cached_bundles(engine, day, board, stats)
    finally:
        if previous_localdata is not None:
            engine.LOCALDATA = previous_localdata

    embedded = _source_embedded_price_rows(localdata, day, voters)
    stats["source_embedded"] = {"raw_rows": len(embedded)}
    if embedded:
        board.append((
            "source_embedded_odds", PRICE_TIER_SOURCE_EMBEDDED,
            engine._odds_bundle_from_rows(embedded, provider="source_embedded_odds",
                                          stats=stats["source_embedded"]),
        ))
    return {"bundles": board, "stats": stats}


def _collect_cached_bundles(engine, day: str, board: list, stats: dict) -> None:
    """Cached dedicated pricing feeds. Never fetches."""
    for name, builder in (
        ("bzzoiro_odds", lambda: engine.bzzoiro_odds_bundle(day, live=False,
                                                            stats=stats.setdefault("bzzoiro_odds", {}))),
        ("scoutingstats_odds", lambda: engine.scoutingstats_odds_bundle(
            day, stats=stats.setdefault("scoutingstats_odds", {}))),
    ):
        try:
            board.append((name, PRICE_TIER_DEDICATED, builder()))
        except Exception as exc:  # a missing cache must never abort the lane
            stats.setdefault(name, {})["error"] = str(exc)


# Timing blocker taxonomy. Each value names a distinct, actionable cause.
TIMING_OK = "trusted_kickoff_present"
TIMING_STARTED = "already_started_or_inside_lead"
TIMING_NO_SOURCE = "missing_kickoff_in_all_sources"
TIMING_PARSE_FAILED = "kickoff_present_but_parser_missed"
TIMING_NON_TIMING_SOURCE = "kickoff_present_from_non_timing_source"


def diagnose_timing(group: FixtureGroup, *, guard_reason: str | None) -> dict:
    """Why this fixture does or does not have usable timing.

    Distinguishes the four causes that need different responses: a late run
    (run earlier), no published kickoff anywhere (source coverage), a
    published kickoff the parser could not read (a defect to repair), and a
    kickoff published only by a source not trusted for timing (policy).
    """
    observations = group.kickoff_observations
    if group.kickoff:
        return {
            "classification": TIMING_STARTED if guard_reason else TIMING_OK,
            "kickoff": group.kickoff,
            "kickoff_source": group.kickoff_source,
            "guard_reason": guard_reason,
            "observations": observations,
        }
    if not observations:
        classification = TIMING_NO_SOURCE
    elif any(o["timing_capable"] and o["parsed"] is False for o in observations):
        classification = TIMING_PARSE_FAILED
    elif any(not o["timing_capable"] for o in observations):
        classification = TIMING_NON_TIMING_SOURCE
    else:
        classification = TIMING_NO_SOURCE
    return {
        "classification": classification,
        "kickoff": None,
        "kickoff_source": None,
        "guard_reason": None,
        "observations": observations,
    }


def diagnose_price(engine, board: dict, *, day: str, home: str, away: str,
                   kickoff: str, selection: str) -> dict:
    """Full record of the price search for one selection.

    Written for every candidate, priced or not, so a ``missing_odds`` blocker
    can be read without guessing which bundles were consulted or which join
    stage failed.
    """
    pick = {"date": day, "home": home, "away": away, "kickoff": kickoff,
            "market": "1x2", "pick": selection}
    searched: list[dict] = []
    for provider, tier, bundle in board["bundles"]:
        row, method = engine.find_side_keyed_odds_row(pick, bundle)
        odds = engine._valid_decimal_odds(row.get("odds")) if row else None
        searched.append({
            "bundle": provider,
            "tier": tier,
            "rows_in_bundle": len(bundle.get("exact", {})),
            "matched": bool(row),
            "match_method": method,
            "usable_odds": odds,
            "rejected_as_fuzzy": method == "alias_fuzzy",
        })
    any_exact = any(b["match_method"] == "exact" for b in searched)
    any_alias = any(b["match_method"] in ("alias_time", "alias_unique")
                    for b in searched)
    any_fuzzy = any(b["rejected_as_fuzzy"] for b in searched)
    embedded = any(b["tier"] == PRICE_TIER_SOURCE_EMBEDDED and b["matched"]
                   for b in searched)
    return {
        "bundles_searched": [b["bundle"] for b in searched],
        "detail": searched,
        "exact_match_found": any_exact,
        "alias_match_found": any_alias,
        "fuzzy_match_found_and_rejected": any_fuzzy and not (any_exact or any_alias),
        "embedded_source_price_found": embedded,
        "outcome": ("exact" if any_exact else "alias" if any_alias
                    else "fuzzy_rejected" if any_fuzzy else "no_match"),
    }


def price_for_candidate(engine, board: dict, *, day: str, home: str, away: str,
                        kickoff: str, selection: str) -> dict:
    """Best available price for one selection, with its provenance.

    Returns the tier, provider, match method and odds, or an empty result.
    A fuzzy (``alias_fuzzy``) join is retained but marked suspect: it is
    evidence, not a licence to bet.
    """
    pick = {"date": day, "home": home, "away": away, "kickoff": kickoff,
            "market": "1x2", "pick": selection}
    for provider, tier, bundle in board["bundles"]:
        row, method = engine.find_side_keyed_odds_row(pick, bundle)
        if not row:
            continue
        odds = engine._valid_decimal_odds(row.get("odds"))
        if odds is None:
            continue
        return {"odds": odds, "provider": row.get("provider") or provider,
                "tier": tier, "match_method": method or "exact",
                "bookmaker": row.get("bookmaker"),
                "suspect": method == "alias_fuzzy"}
    return {}


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
    dispatch_method: str | None = None
    odds: float | None = None
    price_tier: str | None = None
    price_match_method: str | None = None
    bookmaker: str | None = None
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
    notes: list[str] = field(default_factory=list)
    walkforward_evidence: dict = field(default_factory=dict)
    dispatchable: bool = False
    blockers: list[str] = field(default_factory=list)
    timing_diagnosis: dict = field(default_factory=dict)
    price_diagnosis: dict = field(default_factory=dict)
    # Price-integrity provenance, carried so the ticket engine's
    # execution-safe gate can judge the quote. A gate that cannot see the
    # evidence is a gate that cannot fire.
    price_quarantine_reason: str | None = None
    price_evidence: str | None = None
    odds_replaced: bool = False
    price_push_eligible: bool = True
    would_have_qualified_before_kickoff: bool = False
    # Staking is NOT the pick engine's job. auto_tickets owns bankroll and
    # stake sizing, so a pick carries the delegation marker and nothing else.
    # ``internal_stake_units`` exists only to compute the exposure cap and to
    # order picks; it is never displayed and never published as a stake.
    internal_stake_units: float = 0.0
    staking_policy: str = STAKING_POLICY
    staking_owner: str = STAKING_OWNER


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
    engine,
    board: dict,
    as_of: datetime,
    min_lead: int,
) -> tuple[list[Candidate], dict]:
    """Turn today's fixture groups into candidates with exact blockers.

    Two dispatch paths. ``certified_rule`` needs the rule's own inputs plus
    the operational gates (identity, kickoff, price, value). ``certified_model``
    additionally needs the full feature schema, the distribution envelope and
    a calibrated probability bucket. A rule-based pick is never blocked by a
    model-only requirement.
    """
    rules = candidate_rules()
    certified_rules = [r for r in rules
                       if evidence.get(r.rule_id, RuleEvidence("")).certified]
    pricing = {
        "candidate_count_before_pricing": 0,
        "candidate_count_with_any_price": 0,
        "candidate_count_exact_price": 0,
        "candidate_count_alias_price": 0,
        "candidate_count_suspect_price_rejected": 0,
        "candidate_count_missing_price": 0,
        "candidate_count_with_positive_edge": 0,
        "candidate_count_with_negative_edge": 0,
        "price_tiers_used": {},
    }
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

        # --- identity first: an unsafe fixture is not a candidate at all.
        if group.ambiguous:
            blockers.append(
                f"{BLOCKER_IDENTITY}: the same source contributed two different "
                "fixtures to this identity group")
        if group.reversed_risk:
            blockers.append(
                f"{BLOCKER_ORIENTATION}: a mirrored home/away listing exists for "
                "this fixture on the same date")

        # --- voter quorum. This is a source-coverage fact, not a schema fault.
        if features is None:
            blockers.append(
                f"{BLOCKER_VOTER_QUORUM}: {len(group.votes)} current-source 1X2 "
                f"voter(s), {MIN_VOTERS} required "
                f"({','.join(sorted(group.votes)) or 'none'})")
            cand.blockers = blockers
            cand.model_health_status = "not_scored"
            out.append(cand)
            continue

        cand.selection = features["top_outcome"]
        cand.probability = round(features["top_probability"], 4)

        # --- rule inputs are the only mandatory schema for rule dispatch.
        missing_rule_inputs = [name for name in RULE_INPUT_FEATURES
                               if features.get(name) is None]
        if missing_rule_inputs:
            blockers.append(
                f"{BLOCKER_MISSING_FEATURE}: {','.join(missing_rule_inputs)}")

        matching = [r for r in certified_rules if r.matches(features)]
        if matching:
            best = max(matching, key=lambda r: evidence[r.rule_id].hit_rate_lb)
            ev = evidence[best.rule_id]
            cand.rule_id = best.rule_id
            cand.dispatch_method = DISPATCH_RULE
            cand.walkforward_evidence = {
                "sample": ev.sample, "hit_rate": round(ev.hit_rate, 4),
                "hit_rate_lower_bound": round(ev.hit_rate_lb, 4),
                "recent_sample": ev.recent_sample, "brier": round(ev.brier, 4),
                "base_rate": round(ev.base_rate, 4), "status": ev.status,
                "model_eligible": ev.model_eligible,
            }
            # Out-of-distribution is a model concern. For a rule it is a note:
            # the rule's own thresholds already bound its inputs.
            for reason in out_of_distribution_reasons(features, envelope):
                cand.notes.append(f"{reason} (advisory for {DISPATCH_RULE})")
            if not ev.model_eligible:
                cand.notes.append(
                    f"{BLOCKER_CALIBRATION} — rule dispatched on its hit rate, "
                    "not on a calibrated probability")
        else:
            blockers.append(
                f"{BLOCKER_NO_RULE}: {len(certified_rules)} certified rule(s), "
                f"none matched voters={features['number_of_1x2_voters']} "
                f"top_probability={features['top_probability']:.3f} "
                f"unanimous={features['unanimous_outcome']}")
            # Could the model path have rescued it? Only if fully supported.
            missing_all = schema_violations(features)
            if missing_all:
                blockers.append(f"{BLOCKER_MISSING_FEATURE}: {','.join(missing_all)}")
            else:
                for reason in out_of_distribution_reasons(features, envelope):
                    blockers.append(reason)

        # --- kickoff. The gate is unchanged; only the explanation improves.
        guard_reason = None
        if group.kickoff:
            ok, guard_reason = engine.operational_pick_eligibility(
                {"date": day, "kickoff": group.kickoff}, as_of=as_of, min_lead=min_lead
            )
            if ok:
                guard_reason = None
        timing = diagnose_timing(group, guard_reason=guard_reason)
        cand.timing_diagnosis = timing
        if not group.kickoff:
            trusted_obs = [o for o in timing["observations"] if o["timing_capable"]]
            untrusted_obs = [o for o in timing["observations"]
                             if not o["timing_capable"]]
            blockers.append(
                f"{BLOCKER_MISSING_KICKOFF}: {timing['classification']} "
                f"({len(trusted_obs)} observation(s) from timing providers"
                + (f" [{','.join(sorted({o['source'] for o in trusted_obs}))}]"
                   if trusted_obs else "")
                + f", {len(untrusted_obs)} from non-timing sources"
                + (f" [{','.join(sorted({o['source'] for o in untrusted_obs}))}]"
                   if untrusted_obs else "") + ")")
        elif guard_reason:
            blockers.append(
                f"{BLOCKER_KICKOFF_GUARD}: {guard_reason} "
                f"[{timing['classification']}]")

        # --- price.
        pricing["candidate_count_before_pricing"] += 1
        cand.price_diagnosis = diagnose_price(
            engine, board, day=day, home=group.home, away=group.away,
            kickoff=group.kickoff or "", selection=features["top_outcome"])
        priced = price_for_candidate(
            engine, board, day=day, home=group.home, away=group.away,
            kickoff=group.kickoff or "", selection=features["top_outcome"])
        if priced:
            pricing["candidate_count_with_any_price"] += 1
            tier = priced["tier"]
            pricing["price_tiers_used"][tier] = \
                pricing["price_tiers_used"].get(tier, 0) + 1
            if priced["match_method"] == "exact":
                pricing["candidate_count_exact_price"] += 1
            else:
                pricing["candidate_count_alias_price"] += 1
            cand.odds = priced["odds"]
            cand.pricing_source = priced["provider"]
            cand.price_tier = tier
            cand.price_match_method = priced["match_method"]
            cand.bookmaker = priced.get("bookmaker")
            if priced["suspect"]:
                cand.price_quarantine_reason = "alias_fuzzy"
                cand.price_evidence = "SUSPECT_ALIAS_FUZZY"
            cand.price_push_eligible = bool(priced.get("push_eligible", True))
            cand.implied_probability = round(1.0 / priced["odds"], 4)
            cand.edge = round(features["top_probability"] - cand.implied_probability, 4)
            if cand.edge > 0:
                pricing["candidate_count_with_positive_edge"] += 1
            else:
                pricing["candidate_count_with_negative_edge"] += 1
            if priced["suspect"]:
                pricing["candidate_count_suspect_price_rejected"] += 1
                blockers.append(
                    f"{BLOCKER_SUSPECT_PRICE}: fuzzy fixture join "
                    f"({priced['provider']}), price kept as evidence only")
            elif cand.edge < MIN_EDGE_TO_DISPATCH:
                blockers.append(
                    f"{BLOCKER_INSUFFICIENT_EDGE}: probability "
                    f"{features['top_probability']:.4f} vs implied "
                    f"{cand.implied_probability:.4f} at odds {priced['odds']} "
                    f"({priced['provider']}) gives edge {cand.edge:+.4f}, "
                    f"threshold {MIN_EDGE_TO_DISPATCH}")
        else:
            pricing["candidate_count_missing_price"] += 1
            diag = cand.price_diagnosis
            blockers.append(
                f"{BLOCKER_MISSING_ODDS}: no usable 1X2 price for this "
                f"selection; bundles searched="
                f"{','.join(diag['bundles_searched']) or 'none'}; "
                f"exact={diag['exact_match_found']} "
                f"alias={diag['alias_match_found']} "
                f"fuzzy_rejected={diag['fuzzy_match_found_and_rejected']} "
                f"embedded_source_price={diag['embedded_source_price_found']}")

        cand.blockers = blockers
        cand.dispatchable = not blockers
        # A pick that failed ONLY on timing was a real edge we were too late
        # to take. Reported separately so a late run is never mistaken for a
        # weak slate.
        timing_families = (BLOCKER_KICKOFF_GUARD, BLOCKER_MISSING_KICKOFF)
        cand.would_have_qualified_before_kickoff = bool(
            blockers and all(b.startswith(timing_families) for b in blockers))
        cand.model_health_status = "scored" if features is not None else "not_scored"
        if cand.dispatchable:
            cand.internal_stake_units = FLAT_STAKE_UNITS
        out.append(cand)

    dispatchable = [c for c in out if c.dispatchable]
    dispatchable.sort(key=lambda c: (-(c.edge or 0.0), -c.probability))
    cap = min(MAX_DISPATCH_PICKS_PER_DAY, int(MAX_TOTAL_EXPOSURE_UNITS // FLAT_STAKE_UNITS))
    for extra in dispatchable[cap:]:
        extra.dispatchable = False
        extra.internal_stake_units = 0.0
        extra.blockers.append(f"{BLOCKER_CAP}: {cap} pick(s)/day")
    return out, pricing


def blocker_counts(candidates: list[Candidate]) -> dict[str, int]:
    """Count candidates per blocker family, in a stable reporting order."""
    families = (BLOCKER_VOTER_QUORUM, BLOCKER_MISSING_ODDS, BLOCKER_INSUFFICIENT_EDGE,
                BLOCKER_MISSING_KICKOFF, BLOCKER_KICKOFF_GUARD, BLOCKER_NO_RULE,
                BLOCKER_MISSING_FEATURE, BLOCKER_IDENTITY, BLOCKER_ORIENTATION,
                BLOCKER_OOD, BLOCKER_SUSPECT_PRICE, BLOCKER_CALIBRATION,
                BLOCKER_CAP)
    counts = {family: 0 for family in families}
    for candidate in candidates:
        for family in families:
            if any(b.startswith(family) for b in candidate.blockers):
                counts[family] += 1
    return {k: v for k, v in counts.items() if v}


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
    ood = [c for c in candidates if any(b.startswith(BLOCKER_OOD) for b in c.blockers)]
    if ood:
        warnings.append(
            f"MODEL_HEALTH: {len(ood)} candidate(s) were out of distribution and were not dispatched")
    missing_feat = [c for c in candidates
                    if any(b.startswith(BLOCKER_MISSING_FEATURE) for b in c.blockers)]
    if missing_feat:
        warnings.append(
            f"MODEL_HEALTH: {len(missing_feat)} candidate(s) were missing a required "
            "feature; the exact feature names are on each candidate's blocker")
    quorum = [c for c in candidates
              if any(b.startswith(BLOCKER_VOTER_QUORUM) for b in c.blockers)]
    if quorum:
        warnings.append(
            f"MODEL_HEALTH: {len(quorum)} fixture(s) had too few current-source voters "
            "to score — source coverage, not a model or schema fault")
    buckets = rule_lifecycle(evidence) if evidence else {
        RULE_CERTIFIED: [], RULE_RESEARCH: [], RULE_BLOCKED: []}
    if not buckets[RULE_CERTIFIED]:
        warnings.append(
            "MODEL_HEALTH: no fresh_production rule is certified dispatchable — "
            "the lane abstains by design")
    if buckets[RULE_RESEARCH]:
        warnings.append(
            f"MODEL_HEALTH: {len(buckets[RULE_RESEARCH])} rule(s) are research-only and "
            "can never dispatch; they are not counted as certified")
    thin = [ev.rule_id for ev in buckets[RULE_CERTIFIED] if not ev.model_eligible]
    if thin:
        warnings.append(
            f"MODEL_HEALTH: {len(thin)} certified rule(s) lack a sufficient calibration "
            f"bucket, so they dispatch via {DISPATCH_RULE} on hit rate and are not "
            f"eligible for {DISPATCH_MODEL}")
    if scored and not any(c.dispatchable for c in candidates):
        warnings.append("MODEL_HEALTH: candidates were scored but none cleared dispatch gates")
    return warnings


def source_health_checks(
    *, groups, day: str, candidates: list[Candidate], evidence: dict[str, RuleEvidence],
    pricing: dict, roles: dict[str, str],
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
    scored = pricing.get("candidate_count_before_pricing", 0)
    priced = pricing.get("candidate_count_with_any_price", 0)
    if scored and not priced:
        warnings.append(
            f"SOURCE_HEALTH: {scored} scored candidate(s) but zero captured prices — "
            "pricing coverage is the binding constraint, not the model")
    elif scored and priced < scored:
        warnings.append(
            f"SOURCE_HEALTH: {scored - priced} of {scored} scored candidate(s) had no "
            "captured 1X2 price")
    if pricing.get("candidate_count_suspect_price_rejected"):
        warnings.append(
            f"SOURCE_HEALTH: {pricing['candidate_count_suspect_price_rejected']} "
            "candidate(s) matched a price only through a fuzzy fixture join and were "
            "rejected for dispatch")
    if dispatchable == 0:
        warnings.append(
            "SOURCE_HEALTH: fresh_production produced no dispatchable picks — see the blocker "
            "table for the objective reason")
    return warnings


# --------------------------------------------------------------------------
# Artifacts
# --------------------------------------------------------------------------


CURRENT_PRODUCTION_ROLES = frozenset({
    "fresh_production_live_voter", "shadow_fresh_production_voter",
    "pricing_provider", "result_donor", "timing_provider",
})


def rule_lifecycle(evidence: dict[str, RuleEvidence]) -> dict[str, list[RuleEvidence]]:
    """Group rules by their honest lifecycle status."""
    buckets: dict[str, list[RuleEvidence]] = {
        RULE_CERTIFIED: [], RULE_RESEARCH: [], RULE_BLOCKED: []}
    for ev in evidence.values():
        buckets[ev.status].append(ev)
    for items in buckets.values():
        items.sort(key=lambda e: (-e.sample, e.rule_id))
    return buckets


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
    buckets = rule_lifecycle(evidence)
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
        "## Rule lifecycle",
        "",
        f"- **certified dispatchable rules: {len(buckets[RULE_CERTIFIED])}** "
        "(may produce a real bet today, subject to candidate gates)",
        f"- research rules: {len(buckets[RULE_RESEARCH])} "
        "(promising, tracked, never dispatched)",
        f"- blocked rules: {len(buckets[RULE_BLOCKED])} (no usable evidence)",
        "",
        "A rule is only called *certified* when it is genuinely dispatch-eligible.",
        "",
        "## Certification gates",
        "",
    ]
    out += [f"- `{k}`: {v}" for k, v in summary["gates"].items()]
    out += ["",
            "`min_calibration_bucket_sample` gates certified_model dispatch only: a "
            "threshold rule emits a decision, not a calibrated probability.",
            "", "## Rule evidence", "",
            "| rule | status | model eligible | sample | recent | calib. n | hit rate | "
            "Wilson LB | lift | Brier | blockers |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for ev in sorted(evidence.values(), key=lambda e: (-e.sample, e.rule_id)):
        if not ev.sample:
            continue
        out.append(
            f"| {ev.rule_id} | {ev.status} | {'yes' if ev.model_eligible else 'no'} | "
            f"{ev.sample} | {ev.recent_sample} | {ev.calibration_sample} | "
            f"{ev.hit_rate:.3f} | {ev.hit_rate_lb:.3f} | {ev.lift:+.3f} | "
            f"{ev.brier:.4f} | {'; '.join(ev.blockers) or '-'} |"
        )
    out += ["", "Legacy certified edges are NOT authority here: this lane certifies "
            "independently on its own walk-forward evidence.", ""]
    return "\n".join(out)


def render_picks_md(day: str, candidates: list[Candidate], *, dispatch_only: bool,
                    pricing: dict | None = None) -> str:
    rows = [c for c in candidates if c.dispatchable] if dispatch_only else candidates
    title = "FRESH PRODUCTION PICKS" if dispatch_only else "FRESH PRODUCTION CANDIDATES"
    out = [f"# {title} — {day}", ""]

    if dispatch_only and not rows:
        counts = blocker_counts(candidates)
        out += ["## FRESH PRODUCTION — NO PICKS", "",
                "The lane abstained. Blocker counts across "
                f"{len(candidates)} candidate(s):", ""]
        out += ["| blocker | candidates |", "|---|---:|"]
        out += [f"| `{name}` | {count} |" for name, count in counts.items()]
        if pricing:
            out += ["", "### Candidate-to-bet conversion", "",
                    "| stage | count |", "|---|---:|"]
            out += [f"| {k} | {v} |" for k, v in pricing.items()
                    if not isinstance(v, dict)]
            if pricing.get("price_tiers_used"):
                out += ["", "Price tiers used: " + ", ".join(
                    f"`{k}` × {v}" for k, v in pricing["price_tiers_used"].items())]
        out += ["", "### Top rejected candidates", "",
                "| fixture | selection | prob | odds | implied | edge | rule | blockers |",
                "|---|---|---:|---:|---:|---:|---|---|"]
        ranked = sorted(candidates, key=lambda c: (len(c.blockers), -c.probability))[:10]
        for c in ranked:
            out.append(
                f"| {c.home} vs {c.away} | {c.selection or '-'} | {c.probability:.3f} | "
                f"{c.odds or '-'} | {c.implied_probability or '-'} | "
                f"{c.edge if c.edge is not None else '-'} | {c.rule_id or '-'} | "
                f"{'; '.join(c.blockers)} |")
        out += ["", "Abstention is the correct outcome when evidence is insufficient.", ""]
        return "\n".join(out)

    out += ["| fixture | league | kickoff | selection | prob | odds | implied | edge | "
            "dispatch | rule | voters | timing | pricing | price tier | match | "
            "model health | blockers |",
            "|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|---|---:|---|---|"]
    for c in rows:
        out.append(
            f"| {c.home} vs {c.away} | {c.league or '-'} | {c.kickoff or '-'} | "
            f"{c.selection or '-'} | {c.probability:.3f} | {c.odds or '-'} | "
            f"{c.implied_probability or '-'} | {c.edge if c.edge is not None else '-'} | "
            f"{c.dispatch_method or '-'} | {c.rule_id or '-'} | "
            f"{','.join(c.source_voters) or '-'} | {c.timing_source or '-'} | "
            f"{c.pricing_source or '-'} | {c.price_tier or '-'} | "
            f"{c.price_match_method or '-'} | {c.model_health_status} | "
            f"{'; '.join(c.blockers) or '-'} |")
    out += ["", f"Staking: {STAKING_POLICY} (owner: {STAKING_OWNER}). The pick "
                f"engine sizes nothing. Dispatch cap: at most "
                f"{MAX_DISPATCH_PICKS_PER_DAY} pick(s) per day, production lane "
                "only (never legacy_baseline).", ""]
    return "\n".join(out)


def render_model_health_md(day: str, summary: dict, warnings: list[str],
                           evidence: dict[str, RuleEvidence], envelope: dict) -> str:
    buckets = rule_lifecycle(evidence)
    certified = buckets[RULE_CERTIFIED]
    out = [
        f"# model_health — fresh_production — {day}",
        "",
        "## Model card",
        "",
        f"- model version: `{MODEL_VERSION}`",
        f"- feature schema: `{FEATURE_SCHEMA_VERSION}`",
        f"- random seed: {RANDOM_SEED} (deterministic; no generative component)",
        f"- source universe: {', '.join(fresh_production_voters())}",
        f"- evaluation window: {summary['evaluation_window']}",
        f"- training window: {summary['training_window_days']} days",
        f"- features: {', '.join(f['feature_name'] for f in FEATURE_SCHEMA)}",
        f"- certification gates: {json.dumps(summary['gates'])}",
        f"- certified dispatchable rules: {len(certified)}",
        f"- research rules: {len(buckets[RULE_RESEARCH])}",
        f"- blocked rules: {len(buckets[RULE_BLOCKED])}",
        "",
        "## Dispatch paths",
        "",
        f"- `{DISPATCH_RULE}`: requires "
        f"{', '.join(f'`{n}`' for n in RULE_INPUT_FEATURES)} plus identity, kickoff, "
        "price and value gates. Model-only evidence is advisory here.",
        f"- `{DISPATCH_MODEL}`: additionally requires the full feature schema, the "
        "distribution envelope and a sufficient calibration bucket.",
        "",
        "## Distribution envelope",
        "",
        "```json",
        json.dumps({k: v for k, v in envelope.items()
                    if k != "source_combinations"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Calibration (certified dispatchable rules)",
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
        out.append("No certified dispatchable rule: no probability is used for dispatch.")
    out += ["", "## model_health_checks", ""]
    out += [f"- {w}" for w in warnings] or ["- none"]
    out += ["", "No generative model is used anywhere in this lane. Every number above "
            "derives from deterministic code over captured source rows.", ""]
    return "\n".join(out)


def render_source_health_md(day: str, roles: dict[str, str], warnings: list[str],
                            groups, pricing: dict, board_stats: dict) -> str:
    today = [g for (d, _k), g in groups.items() if d == day]
    live = {n: r for n, r in roles.items() if r in CURRENT_PRODUCTION_ROLES}
    reference = {n: r for n, r in roles.items() if r not in CURRENT_PRODUCTION_ROLES}
    out = [
        f"# source_health — fresh_production — {day}",
        "",
        f"- fixture groups today: {len(today)}",
        f"- groups with >= {MIN_VOTERS} current-source voters: "
        f"{sum(1 for g in today if len(g.votes) >= MIN_VOTERS)}",
        f"- groups with a trusted kickoff: {sum(1 for g in today if g.kickoff)}",
        f"- groups flagged ambiguous: {sum(1 for g in today if g.ambiguous)}",
        f"- groups flagged reversed-orientation risk: "
        f"{sum(1 for g in today if g.reversed_risk)}",
        "",
        "## Current production source universe",
        "",
        "| source | role |",
        "|---|---|",
    ]
    out += [f"| {name} | {role} |" for name, role in sorted(live.items())]
    out += ["", "## pricing_health", "", "| stage | count |", "|---|---:|"]
    out += [f"| {k} | {v} |" for k, v in pricing.items() if not isinstance(v, dict)]
    if pricing.get("price_tiers_used"):
        out += ["", "Price tiers used: " + ", ".join(
            f"`{k}` × {v}" for k, v in pricing["price_tiers_used"].items())]
    out += ["", "| pricing bundle | rows |", "|---|---:|"]
    out += [f"| {name} | {stats.get('raw_rows', stats.get('valid_rows', 0))} |"
            for name, stats in sorted(board_stats.items())]
    out += ["", "## source_health_warnings", ""]
    out += [f"- {w}" for w in warnings] or ["- none"]
    out += ["", "## legacy_baseline / historical_reference", "",
            "Sources below are NOT part of the fresh production universe. They are "
            "listed only so their exclusion is auditable.", "",
            "| source | classification |", "|---|---|"]
    out += [f"| {name} | {role} |" for name, role in sorted(reference.items())]
    out.append("")
    return "\n".join(out)


def render_summary(report: dict) -> str:
    """The concise official-run block. The operator should need nothing else."""
    wf = report["walkforward"]
    pricing = report["pricing"]
    lines = [
        "FRESH PRODUCTION SUMMARY",
        f"  date:                          {report['date']}",
        f"  labelled fixtures:             {wf['fixtures_labelled']}",
        f"  certified dispatchable rules:  {report['certified_rule_count']}",
        f"  research rules:                {report['research_rule_count']}",
        f"  blocked rules:                 {report['blocked_rule_count']}",
        f"  candidates:                    {report['candidate_count']}",
        f"  priced candidates:             {pricing['candidate_count_with_any_price']}"
        f" of {pricing['candidate_count_before_pricing']} scored",
        f"  candidates matching a rule:    {report['rule_matched_count']}",
        f"  positive-edge candidates:      {pricing['candidate_count_with_positive_edge']}",
        f"  dispatchable picks:            {report['dispatchable_count']}",
        f"  eligible horizon picks:        {report.get('horizon_eligible_count', 0)}"
        f" through {(report.get('horizon') or {}).get('horizon_end', '-')}",
        "  top blockers:",
    ]
    counts = report["blocker_counts"]
    lines += [f"    {name}: {count}" for name, count in counts.items()] or \
             ["    none"]
    if report["dispatchable_count"]:
        lines.append("  picks:")
        for pick in report["dispatchable_picks"]:
            lines.append(
                f"    {pick['home']} vs {pick['away']} | {pick['selection']} | "
                f"{pick['rule_id']} | p={pick['probability']} | "
                f"odds={pick['odds']} ({pick['pricing_source']}) | "
                f"edge={pick['edge']:+.4f} | staking={STAKING_POLICY}")
    else:
        lines.append("  top rejected candidates:")
        ranked = sorted(report["candidates"],
                        key=lambda c: (len(c["blockers"]), -c["probability"]))[:5]
        for c in ranked:
            lines.append(
                f"    {c['home']} vs {c['away']} | {c['selection'] or '-'} | "
                f"{c['rule_id'] or 'no rule'} | p={c['probability']} | "
                f"odds={c['odds'] or '-'} | "
                f"edge={c['edge'] if c['edge'] is not None else '-'} | "
                f"{c['blockers'][0] if c['blockers'] else '-'}")
        lines.append("  FRESH PRODUCTION — NO PICKS")
        lines.append("")
        lines += no_picks_diagnosis(report)
    plan = report.get("dispatch_plan")
    if plan:
        lines += [""] + render_dispatch_plan_summary(plan, report)
        # Show the evidence behind every selection, and every selection
        # withheld because its rule claim could not be reconstructed.
        lines += [""] + selection_evidence.render_lineage_lines(
            [p["evidence_lineage"] for p in
             (plan.get("same_day_picks") or []) + (plan.get("horizon_picks") or [])
             if p.get("evidence_lineage")])
        for blocked in plan.get("blocked_selections") or []:
            lines.append(
                f"  WITHHELD {blocked.get('event_date')} "
                f"{blocked.get('home')} vs {blocked.get('away')} | "
                f"{blocked.get('dispatch_blocked_reason')}")
            for detail in blocked.get("dispatch_blocked_detail") or []:
                lines.append(f"    {detail}")
    return "\n".join(lines)


def render_dispatch_plan_summary(plan: dict, report: dict) -> list[str]:
    """PRE-TICKET planning block, emitted while the pick engine is still running.

    This runs before auto_tickets, Supabase, CLV and notification, so it
    states only what the pick engine itself knows: which selections were
    produced and for which event dates. It deliberately carries no
    auto-ticket action, ticket status, assayer verdict, publish count or
    capture count — at this point those are unknown, and printing a guess
    produced an operator-facing audit defect: an evaluated selection was
    reported as "not evaluated". The authoritative verdict is the final
    summary rendered by edgefactory.production_summary after the downstream
    stages have actually run.
    """
    counts = report.get("blocker_counts", {})
    total = plan["same_day_pick_count"] + plan["horizon_pick_count"]
    lines = [
        "PRODUCTION DISPATCH PLAN — PRELIMINARY (pre-ticket)",
        f"  production selections:         {total}",
        f"  same-day selections:           {plan['same_day_pick_count']}",
        f"  future-dated selections:       {plan['horizon_pick_count']}",
        f"  event dates:                   "
        f"{', '.join(plan['event_dates']) or 'none'}",
        f"  planned notification action:   {plan['notification_action']}",
        f"  staking owner:                 {STAKING_OWNER}",
        f"  staking policy:                {STAKING_POLICY}",
        "  auto-ticket action:            pending (auto_tickets has not run yet)",
        "  NOTE: this is planning output, not the dispatch verdict. See the "
        "FINAL PRODUCTION SUMMARY after auto_tickets/Supabase/CLV/notification.",
    ]
    for row in plan["horizon_picks"]:
        lines.append(
            f"    FUTURE {row['event_date']} {row.get('kickoff') or '-'} "
            f"{row['home']} vs {row['away']} | {row.get('pick')} | "
            f"odds={row.get('odds')} | edge={(row.get('edge') or 0):+.4f} | "
            f"{row.get('edge_rule')} | staking={STAKING_POLICY}")
    if not total:
        lines.append("  top blockers if none:")
        lines += [f"    {name}: {count}" for name, count in counts.items()] or \
                 ["    none"]
    return lines


def no_picks_diagnosis(report: dict) -> list[str]:
    """Explain a zero-pick day precisely enough to act on it.

    Abstention is a valid outcome, but "no picks" on its own is not an
    answer. This states which stage the slate died at and what the operator
    should change.
    """
    pricing = report["pricing"]
    candidates = report["candidates"]
    horizon = report.get("horizon") or {}

    def blocked_on(family: str) -> list[dict]:
        return [c for c in candidates
                if (c.get("edge") or 0) > 0
                and any(b.startswith(family) for b in c["blockers"])]

    timing = blocked_on(BLOCKER_KICKOFF_GUARD)
    no_kickoff = blocked_on(BLOCKER_MISSING_KICKOFF)
    price = blocked_on(BLOCKER_MISSING_ODDS) + blocked_on(BLOCKER_SUSPECT_PRICE)
    no_rule = blocked_on(BLOCKER_NO_RULE)
    edge_short = blocked_on(BLOCKER_INSUFFICIENT_EDGE)
    would_have = [c for c in candidates
                  if c.get("would_have_qualified_before_kickoff")]

    lines = [
        "FRESH PRODUCTION NO-PICKS DIAGNOSIS",
        f"  certified dispatchable rules:            {report['certified_rule_count']}",
        f"  candidates scored:                       {pricing['candidate_count_before_pricing']}",
        f"  candidates priced:                       {pricing['candidate_count_with_any_price']}",
        f"  candidates with positive edge:           {pricing['candidate_count_with_positive_edge']}",
        f"  positive-edge blocked by timing guard:   {len(timing)}",
        f"  positive-edge blocked by missing kickoff:{len(no_kickoff)}",
        f"  positive-edge blocked by price quality:  {len(price)}",
        f"  positive-edge below edge threshold:      {len(edge_short)}",
        f"  positive-edge with no certified rule:    {len(no_rule)}",
        f"  would have qualified before kickoff:     {len(would_have)}",
    ]
    if horizon:
        lines.append(
            f"  next eligible horizon candidates:        "
            f"{horizon.get('eligible_pick_count', 0)} "
            f"through {horizon.get('horizon_end', '-')}")
        for pick in horizon.get("picks", [])[:5]:
            lines.append(
                f"    {pick['date']} {pick.get('kickoff') or '-'} "
                f"{pick['home']} vs {pick['away']} | {pick['selection']} | "
                f"edge={(pick.get('edge') or 0):+.4f}")

    # A single top action item, chosen by which stage lost the most edge.
    if would_have:
        action = ("No same-day dispatch because the qualifying fixtures had "
                  "already started or were inside the lead window. Run "
                  "earlier, or take these from the fresh-production horizon "
                  "planner on the preceding day.")
    elif no_kickoff:
        action = ("No dispatch because positive-edge fixtures had no trusted "
                  "kickoff. Extend timing-provider coverage for these "
                  "competitions; do not relax the kickoff gate.")
    elif price:
        action = ("No dispatch because positive-edge candidates could not be "
                  "priced from a trusted exact or alias join. Widen pricing "
                  "capture coverage; fuzzy joins stay rejected.")
    elif edge_short:
        action = ("No dispatch because priced certified candidates did not "
                  "clear the edge threshold. This is a correct abstention — "
                  "the market was not mispriced enough.")
    elif no_rule:
        action = ("No dispatch because priced candidates matched no certified "
                  "dispatchable rule. Certification needs more settled "
                  "samples, not a lower bar.")
    elif not pricing["candidate_count_with_any_price"]:
        action = ("No dispatch because no candidate could be priced at all. "
                  "Check that same-day pricing capture ran before this lane.")
    else:
        action = ("No dispatch because no candidate reached the scoring stage "
                  "with a quorum of current sources. Source coverage, not the "
                  "gates, is the limit.")
    lines += ["", f"  TOP ACTION ITEM: {action}"]
    return lines


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def horizon_pick_rows(horizon: dict) -> list[dict]:
    """Shape eligible horizon picks for production dispatch.

    A horizon pick has already passed every same-day gate plus the lead
    bounds, so the only thing that distinguishes it from a same-day pick is
    that its event date is in the future. It is dated by its EVENT date, not
    by the run date, so the warehouse and the dashboard place the bet on the
    day it is actually played.
    """
    rows = []
    for pick in horizon.get("picks", []):
        if not pick.get("dispatchable"):
            continue
        row = {
            "run_date": horizon.get("generated_for"),
            "event_date": pick["date"],
            "date": pick["date"],          # event date: what the warehouse keys on
            "kickoff": pick.get("kickoff"),
            "league": pick.get("league"),
            "home": pick["home"],
            "away": pick["away"],
            "market": "1x2",
            "pick": pick["selection"],
            "selection": pick["selection"],
            "odds": pick.get("odds"),
            "probability": pick.get("probability"),
            "avg_p": round((pick.get("probability") or 0) * 100, 2),
            "implied_probability": pick.get("implied_probability"),
            "edge": pick.get("edge"),
            "bucket": canonical_bucket(
                odds=pick.get("odds"),
                price_evidence=pick.get("price_evidence"),
                price_quarantine_reason=pick.get("price_quarantine_reason")),
            # Production identity as metadata, never as a bucket.
            "selection_scope": PRODUCTION_SCOPE,
            "production_certified": True,
            "production_lane": True,
            # Price-integrity provenance must travel with the selection.
            # auto_tickets' execution-safe gate reads these fields; if the
            # row builder drops them the gate silently cannot fire and a
            # quarantined or audit-only quote would reach a ticket.
            "price_quarantine_reason": pick.get("price_quarantine_reason"),
            "price_evidence": pick.get("price_evidence"),
            "odds_replaced": pick.get("odds_replaced"),
            "price_push_eligible": pick.get("price_push_eligible", True),
            "edge_rule": pick.get("rule_id"),
            "rule_id": pick.get("rule_id"),
            "display_rule": f"{pick.get('dispatch_method')}:{pick.get('rule_id')}",
            "edge_status": "certified",
            "lane": "fresh_production",
            "horizon_pick": True,
            "dispatch_method": pick.get("dispatch_method"),
            "odds_source": pick.get("pricing_source"),
            "pricing_source": pick.get("pricing_source"),
            "timing_source": pick.get("timing_source"),
            "bookmaker": pick.get("bookmaker"),
            "odds_match_method": pick.get("price_match_method"),
            "price_tier": pick.get("price_tier"),
            "staking_policy": pick.get("staking_policy") or STAKING_POLICY,
            "staking_owner": pick.get("staking_owner") or STAKING_OWNER,
            "model_version": pick.get("model_version"),
            "feature_schema_version": pick.get("feature_schema_version"),
            "source_voters": pick.get("source_voters"),
            "walkforward_evidence": pick.get("walkforward_evidence"),
        }
        rows.append(row)
    return rows


def build_dispatch_plan(*, run_date: str, same_day_rows: list[dict],
                        horizon_rows: list[dict], horizon: dict) -> dict:
    """The single statement of what production should publish and announce.

    Same-day and future-dated picks are kept in separate lists because they
    have different replace semantics: the run date's slate is authoritative
    for that date, whereas a future date must only be touched when this run
    actually produced picks for it.
    """
    # A rule_id makes a claim about its own evidence. Before anything is
    # published, check that the claim can be reconstructed from
    # production-eligible voters; a selection that cannot support its own
    # rule name is withheld rather than dispatched with a false label.
    blocked_selections: list[dict] = []

    def _admissible(rows: list[dict]) -> list[dict]:
        kept = []
        for row in rows:
            lineage = selection_evidence.build_lineage(row)
            if lineage["status"] in selection_evidence.BLOCKING_STATUSES:
                blocked = dict(row)
                blocked["dispatch_blocked_reason"] = lineage["status"]
                blocked["dispatch_blocked_detail"] = lineage["reasons"]
                blocked["evidence_lineage"] = lineage
                blocked_selections.append(blocked)
                continue
            row["evidence_lineage"] = lineage
            kept.append(row)
        return kept

    same_day_rows = _admissible(list(same_day_rows))
    horizon_rows = _admissible(list(horizon_rows))

    for row in same_day_rows:
        row.setdefault("run_date", run_date)
        row.setdefault("event_date", row.get("date"))
        row.setdefault("horizon_pick", False)

    future_rows = [r for r in horizon_rows if r["event_date"] != run_date]
    # A horizon pick whose event date IS the run date is simply a same-day
    # pick; it must not be double-counted.
    same_day_keys = {(r.get("date"), r.get("home"), r.get("away"), r.get("pick"))
                     for r in same_day_rows}
    for row in horizon_rows:
        if row["event_date"] == run_date:
            key = (row.get("date"), row.get("home"), row.get("away"), row.get("pick"))
            if key not in same_day_keys:
                same_day_rows.append(row)
                same_day_keys.add(key)

    event_dates = sorted({r["event_date"] for r in same_day_rows + future_rows})
    future_dates = sorted({r["event_date"] for r in future_rows})

    if same_day_rows:
        action = "same_day_pick"
    elif future_rows:
        action = "future_pick"
    else:
        action = "empty_slate"

    return {
        "schema": 1,
        "lane": "fresh_production",
        "run_date": run_date,
        "blocked_selections": blocked_selections,
        "blocked_selection_count": len(blocked_selections),
        "same_day_picks": same_day_rows,
        "horizon_picks": future_rows,
        "same_day_pick_count": len(same_day_rows),
        "horizon_pick_count": len(future_rows),
        "event_dates": event_dates,
        "future_event_dates": future_dates,
        # The run date is always authoritative for itself, so it is always
        # replaceable. A future date is replaceable only because this run
        # produced picks for it.
        "sync_dates": sorted({run_date} | set(event_dates)),
        "replaceable_dates": sorted({run_date} | set(future_dates)),
        "notification_action": action,
        "horizon_window": {
            "horizon_end": horizon.get("horizon_end"),
            "min_lead_minutes": horizon.get("min_lead_minutes"),
            "max_lead_hours": horizon.get("max_lead_hours"),
        },
        "note": (
            "Future-dated picks are dispatched under their EVENT date. A run "
            "replaces its own run date unconditionally and a future date only "
            "when that date appears in this plan, so an empty same-day slate "
            "can never delete an already-dispatched future pick."
        ),
    }


def render_dispatch_plan_md(plan: dict) -> str:
    lines = [
        f"# FRESH PRODUCTION DISPATCH PLAN — run date {plan['run_date']}",
        "",
        f"- same-day dispatchable picks: {plan['same_day_pick_count']}",
        f"- horizon dispatchable picks: {plan['horizon_pick_count']}",
        f"- event dates: {', '.join(plan['event_dates']) or 'none'}",
        f"- sync dates: {', '.join(plan['sync_dates'])}",
        f"- notification action: {plan['notification_action']}",
        "",
    ]
    for title, rows in (("Same-day picks", plan["same_day_picks"]),
                        ("Future-dated horizon picks", plan["horizon_picks"])):
        lines += [f"## {title}", ""]
        if not rows:
            lines += ["None.", ""]
            continue
        lines += ["| event date | kickoff | fixture | selection | prob | odds | "
                  "implied | edge | rule | staking |",
                  "|---|---|---|---|---:|---:|---:|---:|---|---|"]
        for r in rows:
            prob = r.get("probability")
            if prob is None and r.get("avg_p") is not None:
                prob = r["avg_p"] / 100
            lines.append(
                f"| {r['event_date']} | {r.get('kickoff') or '-'} | "
                f"{r['home']} vs {r['away']} | {r.get('pick')} | "
                f"{prob if prob is None else format(prob, '.3f')} | "
                f"{r.get('odds') or '-'} | "
                f"{r.get('implied_probability') or '-'} | "
                f"{(r.get('edge') or 0):+.4f} | {r.get('edge_rule') or '-'} | "
                f"{r.get('staking_policy') or STAKING_POLICY} |")
        lines.append("")
    lines += [plan["note"], ""]
    return "\n".join(lines)


def production_pick_rows(candidates: list[Candidate]) -> list[dict]:
    """Shape dispatchable picks for the production sync/notify path.

    Only ``fresh_production`` dispatchable picks ever reach this function.
    An empty list is a legitimate, explicit result: it tells the sync step to
    publish zero rows rather than fall back to another lane.
    """
    rows = []
    for c in candidates:
        if not c.dispatchable:
            continue
        rows.append({
            "date": c.date,
            "kickoff": c.kickoff,
            "league": c.league,
            "home": c.home,
            "away": c.away,
            "market": "1x2",
            "pick": c.selection,
            "odds": c.odds,
            "avg_p": round(c.probability * 100, 2),
            "implied_probability": c.implied_probability,
            "edge": c.edge,
            "bucket": canonical_bucket(
                odds=c.odds,
                price_evidence=c.price_evidence,
                price_quarantine_reason=c.price_quarantine_reason),
            # Production identity as metadata, never as a bucket.
            "selection_scope": PRODUCTION_SCOPE,
            "production_certified": True,
            "production_lane": True,
            # Price-integrity provenance must travel with the selection.
            # auto_tickets' execution-safe gate reads these fields; if the
            # row builder drops them the gate silently cannot fire and a
            # quarantined or audit-only quote would reach a ticket.
            "price_quarantine_reason": c.price_quarantine_reason,
            "price_evidence": c.price_evidence,
            "odds_replaced": c.odds_replaced,
            "price_push_eligible": c.price_push_eligible,
            "edge_rule": c.rule_id,
            "display_rule": f"{c.dispatch_method}:{c.rule_id}",
            "edge_status": "certified",
            "lane": "fresh_production",
            "dispatch_method": c.dispatch_method,
            "odds_source": c.pricing_source,
            "bookmaker": c.bookmaker,
            "odds_match_method": c.price_match_method,
            "price_tier": c.price_tier,
            "staking_policy": c.staking_policy,
            "staking_owner": c.staking_owner,
            "model_version": c.model_version,
            "feature_schema_version": c.feature_schema_version,
            "source_voters": c.source_voters,
            "walkforward_evidence": c.walkforward_evidence,
        })
    return rows


# Horizon planning. Conservative by construction: a bet may only be taken
# between MIN_LEAD (too close to kickoff to trust the price) and MAX_LEAD
# (too far out for today's evidence to still describe the fixture).
HORIZON_MIN_LEAD_MINUTES = 30
HORIZON_MAX_LEAD_HOURS = 48
DEFAULT_HORIZON_DAYS = 2


def plan_horizon(
    *, groups, evidence, envelope, engine, localdata: Path, day: str,
    as_of: datetime, horizon_days: int = DEFAULT_HORIZON_DAYS,
    voters: tuple[str, ...] = (), min_lead: int = HORIZON_MIN_LEAD_MINUTES,
    max_lead_hours: int = HORIZON_MAX_LEAD_HOURS,
) -> dict:
    """Eligible bets on upcoming dates, not only the target date.

    Same gates as same-day dispatch — trusted kickoff, captured odds, a
    certified dispatchable rule, positive edge above threshold, stake caps —
    plus a maximum lead so we never price a fixture the current evidence is
    too old to describe.
    """
    target = date.fromisoformat(day)
    horizon_end = (target + timedelta(days=max(0, horizon_days))).isoformat()
    max_lead = timedelta(hours=max_lead_hours)
    per_day: list[dict] = []
    picks: list[Candidate] = []
    candidates_all: list[Candidate] = []

    for offset in range(0, max(1, horizon_days + 1)):
        this_day = (target + timedelta(days=offset)).isoformat()
        board = build_price_board(engine, localdata, this_day, voters)
        day_candidates, _pricing = build_candidates(
            groups, day=this_day, evidence=evidence, envelope=envelope,
            engine=engine, board=board, as_of=as_of, min_lead=min_lead)
        candidates_all.extend(day_candidates)

        eligible: list[Candidate] = []
        for cand in day_candidates:
            if not cand.dispatchable:
                continue
            kickoff_dt = (engine.parse_kickoff_dt(cand.kickoff, cand.date)
                          if cand.kickoff else None)
            if kickoff_dt is None:
                cand.dispatchable = False
                cand.blockers.append(
                    f"{BLOCKER_MISSING_KICKOFF}: horizon planning requires a "
                    "parseable trusted kickoff")
                continue
            lead = kickoff_dt - as_of
            # Re-check the lower bound here as well. build_candidates already
            # applies the pre-match guard, but this is the path that puts
            # money on a future fixture, so it verifies both bounds itself
            # rather than trusting an upstream flag.
            if lead < timedelta(minutes=min_lead):
                cand.dispatchable = False
                cand.internal_stake_units = 0.0
                cand.blockers.append(
                    f"{BLOCKER_KICKOFF_GUARD}: kickoff is "
                    f"{lead.total_seconds() / 60:.0f} minute(s) away, inside "
                    f"the {min_lead}-minute minimum lead")
                continue
            if lead > max_lead:
                cand.dispatchable = False
                cand.blockers.append(
                    f"{BLOCKER_KICKOFF_GUARD}: kickoff is "
                    f"{lead.total_seconds() / 3600:.1f}h away, beyond the "
                    f"{max_lead_hours}h horizon limit")
                continue
            cand.notes.append(
                f"horizon lead {lead.total_seconds() / 3600:.1f}h")
            eligible.append(cand)

        per_day.append({"date": this_day, "candidates": len(day_candidates),
                        "eligible": len(eligible)})
        picks.extend(eligible)

    picks.sort(key=lambda c: (-(c.edge or 0.0), c.date, -c.probability))
    cap = min(MAX_DISPATCH_PICKS_PER_DAY,
              int(MAX_TOTAL_EXPOSURE_UNITS // FLAT_STAKE_UNITS))
    for extra in picks[cap:]:
        extra.dispatchable = False
        extra.internal_stake_units = 0.0
        extra.blockers.append(f"{BLOCKER_CAP}: {cap} pick(s) across the horizon")
    picks = picks[:cap]

    return {
        "schema": 1,
        "lane": "fresh_production_horizon",
        "generated_for": day,
        "horizon_end": horizon_end,
        "horizon_days": horizon_days,
        "as_of": as_of.isoformat(timespec="seconds"),
        "min_lead_minutes": min_lead,
        "max_lead_hours": max_lead_hours,
        "per_day": per_day,
        "eligible_pick_count": len(picks),
        "picks": [asdict(c) for c in picks],
        "note": (
            "Horizon picks satisfy every same-day dispatch gate plus a "
            f"{min_lead}-minute minimum and {max_lead_hours}-hour maximum "
            "lead. They are published as dated candidates: dispatch happens "
            "on each fixture's own run date, because the downstream sync and "
            "notification path publishes one target date at a time and does "
            "not yet accept future-dated rows."
        ),
    }


def render_horizon_md(payload: dict) -> str:
    lines = [
        f"# FRESH PRODUCTION HORIZON PLAN — {payload['generated_for']} "
        f"through {payload['horizon_end']}",
        "",
        f"As of: {payload['as_of']}",
        f"Lead window: {payload['min_lead_minutes']} minutes to "
        f"{payload['max_lead_hours']} hours before kickoff.",
        "",
        "| date | candidates | eligible |",
        "|---|---:|---:|",
    ]
    for row in payload["per_day"]:
        lines.append(f"| {row['date']} | {row['candidates']} | {row['eligible']} |")
    lines.append("")
    picks = payload["picks"]
    if not picks:
        lines += ["## No eligible horizon picks", "",
                  "No upcoming fixture cleared every dispatch gate inside the "
                  "lead window.", ""]
    else:
        lines += [f"## {len(picks)} eligible horizon pick(s)", "",
                  "| date | kickoff | fixture | selection | prob | odds | edge | rule | staking |",
                  "|---|---|---|---|---:|---:|---:|---|---|"]
        for pick in picks:
            lines.append(
                f"| {pick['date']} | {pick.get('kickoff') or '-'} | "
                f"{pick['home']} vs {pick['away']} | {pick['selection']} | "
                f"{pick['probability']:.3f} | {pick.get('odds') or '-'} | "
                f"{(pick.get('edge') or 0):+.4f} | {pick.get('rule_id') or '-'} | "
                f"{pick.get('staking_policy') or STAKING_POLICY} |")
        lines.append("")
    lines += [payload["note"], ""]
    return "\n".join(lines)


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
    horizon_days: int = DEFAULT_HORIZON_DAYS,
) -> dict:
    engine = load_engine()
    if engine is None:  # pragma: no cover
        return {"error": "could not load the pick engine"}
    if as_of is None:
        as_of = engine.pick_run_as_of()

    target = date.fromisoformat(day)
    eval_start = (target - timedelta(days=eval_days)).isoformat()
    history_start = (target - timedelta(days=eval_days + train_days)).isoformat()
    eval_end = (target - timedelta(days=1)).isoformat()

    voters = fresh_production_voters()
    roles = classify_source_roles()
    # Load through the end of the horizon so upcoming fixtures are available
    # to the horizon planner, and keep timing observations from the target
    # date onward.
    horizon_end = (target + timedelta(days=max(0, horizon_days))).isoformat()
    groups = load_fixture_groups(localdata, start=history_start,
                                 end=horizon_end, voters=voters, engine=engine,
                                 record_timing_from=day)
    labels = load_settlement_labels(localdata, start=history_start, end=day)

    evidence, summary = walk_forward(
        groups, labels, eval_start=eval_start, eval_end=eval_end, train_days=train_days)
    envelope = training_envelope(
        evidence, groups, labels, eval_start=eval_start, eval_end=eval_end)

    board = build_price_board(engine, localdata, day, voters)
    candidates, pricing = build_candidates(
        groups, day=day, evidence=evidence, envelope=envelope, engine=engine,
        board=board, as_of=as_of, min_lead=min_lead)

    horizon = plan_horizon(
        groups=groups, evidence=evidence, envelope=envelope, engine=engine,
        localdata=localdata, day=day, as_of=as_of, horizon_days=horizon_days,
        voters=voters, min_lead=min_lead)

    dispatch_plan = build_dispatch_plan(
        run_date=day,
        same_day_rows=production_pick_rows(candidates),
        horizon_rows=horizon_pick_rows(horizon),
        horizon=horizon)

    buckets = rule_lifecycle(evidence)
    feature_names = [f["feature_name"] for f in FEATURE_SCHEMA]
    model_warnings = model_health_checks(
        candidates=candidates, evidence=evidence, envelope=envelope,
        feature_names=feature_names)
    src_warnings = source_health_checks(
        groups=groups, day=day, candidates=candidates, evidence=evidence,
        pricing=pricing, roles=roles)

    certified_payload = {
        "schema": 2,
        "generated_for": day,
        "model_version": MODEL_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "note": (
            "fresh_production certification registry. Independent of the legacy "
            "certified-edges registry; legacy certification is never inherited. "
            "'certified_dispatchable_rules' are the only rules allowed to bet."
        ),
        "gates": GATES,
        "certified_dispatchable_rules": [asdict(ev) for ev in buckets[RULE_CERTIFIED]],
        "research_rules": [asdict(ev) for ev in buckets[RULE_RESEARCH]],
        "blocked_rules": [asdict(ev) for ev in buckets[RULE_BLOCKED] if ev.sample],
    }
    dispatchable = [c for c in candidates if c.dispatchable]

    report = {
        "schema": 2,
        "lane": "fresh_production",
        "date": day,
        "as_of": as_of.isoformat(timespec="seconds"),
        "source_universe": list(voters),
        "source_roles": roles,
        "historical_reference_only": sorted(PARKED_PREDICTORS),
        "walkforward": summary,
        "envelope": envelope,
        "certified_rule_count": len(buckets[RULE_CERTIFIED]),
        "research_rule_count": len(buckets[RULE_RESEARCH]),
        "blocked_rule_count": len([e for e in buckets[RULE_BLOCKED] if e.sample]),
        "candidate_count": len(candidates),
        "rule_matched_count": sum(1 for c in candidates if c.rule_id),
        "dispatchable_count": len(dispatchable),
        "horizon": horizon,
        "horizon_eligible_count": horizon["eligible_pick_count"],
        "pricing": pricing,
        "pricing_bundle_stats": board["stats"],
        "blocker_counts": blocker_counts(candidates),
        "model_health_warnings": model_warnings,
        "source_health_warnings": src_warnings,
        "feature_schema": list(FEATURE_SCHEMA),
        "candidates": [asdict(c) for c in candidates],
        "dispatchable_picks": [asdict(c) for c in dispatchable],
        "production_pick_rows": production_pick_rows(candidates),
        "dispatch_plan": dispatch_plan,
        "_evidence": evidence,
        "_certified_payload": certified_payload,
    }

    if write:
        out = output_dir
        model_dir = out / MODEL_DIR_NAME
        dumps = lambda obj: json.dumps(obj, indent=2, sort_keys=True, default=str)
        write_artifact(out / f"fresh_production_walkforward_{day}.json",
                       dumps({"summary": summary,
                              "lifecycle": {k: [e.rule_id for e in v]
                                            for k, v in buckets.items()},
                              "rules": [asdict(e) for e in evidence.values() if e.sample]}))
        write_artifact(out / f"fresh_production_walkforward_{day}.md",
                       render_walkforward_md(summary, evidence))
        write_artifact(out / f"fresh_production_certified_edges_{day}.json",
                       dumps(certified_payload))
        write_artifact(out / "fresh_production_certified_edges.json",
                       dumps(certified_payload))
        write_artifact(out / f"fresh_production_certified_edges_{day}.md",
                       render_walkforward_md(summary, evidence))
        write_artifact(out / f"fresh_production_candidate_picks_{day}.json",
                       dumps([asdict(c) for c in candidates]))
        write_artifact(out / f"fresh_production_candidate_picks_{day}.md",
                       render_picks_md(day, candidates, dispatch_only=False,
                                       pricing=pricing))
        write_artifact(out / f"fresh_production_dispatchable_picks_{day}.json",
                       dumps([asdict(c) for c in dispatchable]))
        write_artifact(out / f"fresh_production_dispatchable_picks_{day}.md",
                       render_picks_md(day, candidates, dispatch_only=True,
                                       pricing=pricing))
        # The production hand-off file. Always written, even when empty: an
        # explicit zero-row slate is what stops any other lane backfilling it.
        write_artifact(out / f"fresh_production_horizon_picks_{day}.json",
                       json.dumps(horizon, indent=2, sort_keys=True))
        write_artifact(out / f"fresh_production_horizon_picks_{day}.md",
                       render_horizon_md(horizon))
        write_artifact(out / f"fresh_production_production_picks_{day}.json",
                       dumps(dispatch_plan["same_day_picks"]))
        # The dispatch plan is the hand-off for future-dated dispatch: it
        # carries each pick under its own event date.
        write_artifact(out / f"fresh_production_dispatch_plan_{day}.json",
                       dumps(dispatch_plan))
        write_artifact(out / f"fresh_production_dispatch_plan_{day}.md",
                       render_dispatch_plan_md(dispatch_plan))
        write_artifact(out / f"model_health_{day}.json",
                       dumps({"warnings": model_warnings, "envelope": envelope,
                              "model_version": MODEL_VERSION,
                              "feature_schema_version": FEATURE_SCHEMA_VERSION,
                              "random_seed": RANDOM_SEED,
                              "source_universe": list(voters),
                              "dispatch_paths": {
                                  DISPATCH_RULE: list(RULE_INPUT_FEATURES),
                                  DISPATCH_MODEL: list(REQUIRED_FEATURES)},
                              "certified_dispatchable_rules": len(buckets[RULE_CERTIFIED]),
                              "research_rules": len(buckets[RULE_RESEARCH]),
                              "blocked_rules": len(buckets[RULE_BLOCKED]),
                              "gates": GATES}))
        write_artifact(out / f"model_health_{day}.md",
                       render_model_health_md(day, summary, model_warnings,
                                              evidence, envelope))
        write_artifact(out / f"source_health_{day}.json",
                       dumps({"current_production_roles":
                              {n: r for n, r in roles.items()
                               if r in CURRENT_PRODUCTION_ROLES},
                              "historical_reference":
                              {n: r for n, r in roles.items()
                               if r not in CURRENT_PRODUCTION_ROLES},
                              "pricing_health": pricing,
                              "pricing_bundles": board["stats"],
                              "warnings": src_warnings}))
        write_artifact(out / f"source_health_{day}.md",
                       render_source_health_md(day, roles, src_warnings, groups,
                                               pricing, board["stats"]))
        write_artifact(model_dir / "feature_schema.json",
                       dumps({"version": FEATURE_SCHEMA_VERSION,
                              "features": list(FEATURE_SCHEMA),
                              "rule_dispatch_required": list(RULE_INPUT_FEATURES),
                              "model_dispatch_required": list(REQUIRED_FEATURES),
                              "legacy_only_denylist": sorted(LEGACY_ONLY_FEATURES)}))
        write_artifact(model_dir / f"model_card_{day}.md",
                       render_model_health_md(day, summary, model_warnings,
                                              evidence, envelope))
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
    parser.add_argument("--min-lead", type=int, default=HORIZON_MIN_LEAD_MINUTES)
    parser.add_argument("--horizon-days", type=int, default=DEFAULT_HORIZON_DAYS,
                        help="Plan eligible bets this many days beyond --date.")
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
                 min_lead=args.min_lead, write=not args.no_write,
                 horizon_days=args.horizon_days)
    if "error" in report:
        print(report["error"], file=sys.stderr)
        return 1

    print(render_summary(report))
    for warning in report["source_health_warnings"] + report["model_health_warnings"]:
        print(f"  {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
