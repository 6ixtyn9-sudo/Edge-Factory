"""Independent autobets_ML PAPER lane; no live state, real stakes, registry or network access.

Uses the retained, fixture-bound ENH score model (form + source forecasts),
existing local quote index, exact result keys and shared market outcomes. Its
own forward receipts dynamically train a regularised probability calibrator
on prior-day mistakes, including bucket/market effects, plus a bounded
success tilt toward groups beating their calibrated expectations. Learning
starts from the first resolved prior-day results; no history means the
*existing* model is used unchanged, not a fabricated probability.

Same-book paper accas choose their own leg count, card count and stakes.
No odds band, fixed stake or artificial acca/leg-count cap is imposed.
CAUTION and SKIPPED_VETO strategy labels are intentionally paper-eligible
(test_lower_probability_and_caution_bucket_can_win_paper_search); identity,
price-quality and timing guards still apply. This never overrides live gates.
New decisions use a rolling 24-hour kickoff horizon, at any existing run,
and freeze on publication. No 06:00/09:00 clock gate applies to rolling ML.
Legacy daily receipts/drafts remain readable and immutable; frozen receipts
supersede pending rows. Aggregate open exposure is capped at 25% of paper bank.
Learning is dynamic from the first resolved prior-day fixtures: the logistic
calibrator needs both outcome classes (a mathematical requirement, not an
evidence gate), and the bounded success tilt applies even before that.
Effects are recency-weighted (14-day half-life) and fitted only on prior-day
receipts, never on today's outcomes. Source-gap bands feed the success tilt.
Products of same-book single quotes are explicitly hypothetical acca payouts;
neither book acceptance nor independence/calibration of joint probabilities is
claimed. Positive estimated EV is a PAPER search objective, never a live gate.
Receipts are write-once; reports re-read regulation results without rewriting
predictions. No Main comparison, promotion, or notifications are implemented.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import tempfile
import zlib
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from heapq import heappush, heapreplace
from pathlib import Path
from zoneinfo import ZoneInfo

from . import price_sources as psrc
from .enh_pricing import (
    MARKET_PRICE_MAP,
    ODDSPAPI_MAX_AGE_H,
    _betexplorer_asof_index,
    betexplorer_price_rejection,
    load_prices_index,
)
from .enh_registry import (
    check_enhancement_hit,
    enhancement_ml_score_weights,
    enhancement_price_context,
)
from .identity import source_team_key, squad_marker_mismatch
from .odds_normalization import parse_zoned_timestamp
from .util import dated_artifact_path, norm_team

SCHEMA = "autobets_ML_v2"
READABLE_SCHEMAS = {"autobets_ML_v1", SCHEMA}
PREFIX = "autobets_ML"
RECEIPT_DIR = Path("phase5_reconciliation/ml_paper_receipts")
LOCAL_TZ = ZoneInfo("Africa/Johannesburg")
SEARCH_BEAM_WIDTH = 512  # computational search breadth, NOT a betting/leg/odds cap
BASE_PAPER_UNITS = 100.0
KELLY_MULTIPLIER = 0.25  # v2: quarter of robust portfolio Kelly; NOT a fixed stake
MAX_PAPER_EXPOSURE = 0.25  # shared aggregate ceiling; legacy free-bank sizing retained
MAX_FIXTURE_STAKE_FRACTION = 0.05  # NEW gross stake per canonical fixture / TOTAL paper bank
FIXTURE_CONCENTRATION_POLICY = "ml_paper_fixture_gross_stake_cap"
DYNAMIC_LEARNING_POLICY = "ml_paper_dynamic_calibration_success_tilt"
RECENCY_HALF_LIFE_DAYS = 14.0  # recency weighting for dynamic learning effects
SUCCESS_TILT_GROUP_LIMIT_LOGIT = 0.50  # max logit shift from one group effect
SUCCESS_TILT_TOTAL_LIMIT_LOGIT = 0.50  # correlated groups average, never stack past one group
# Evidence smoothing: total dynamic logit shift is scaled by
# fixtures / (fixtures + K), so the first results move probabilities gently
# and full strength is approached only as resolved evidence accumulates.
LEARNING_SMOOTHING_K_FIXTURES = 5.0
SUCCESS_TILT_FOLDS = 5  # fixture-grouped cross-fitting for out-of-sample tilt residuals
MICRO_UNITS = 1_000_000
EXACT_SEARCH_SIZE = 8
PORTFOLIO_ITERATIONS = 256
SEARCH_NODE_BUDGET = 250_000  # computation bound, never a leg/card count cap
# PAPER-only overnight collection allowance, measured at the scheduled freeze.
# This is an operational policy, not an ROI-tuned optimum or a live-price claim.
# A stricter source policy still wins; never retimestamp a quote to rescue it.
QUOTE_MAX_AGE = timedelta(hours=12)
ACTUAL_RUN_FREEZE = "first_run_actual_decision_v1"
ROLLING_FREEZE = "rolling_24h_actual_decision_v1"
MIN_LEAD = timedelta(minutes=30)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def receipt_path(root, day):
    datetime.strptime(day, "%Y-%m-%d")
    return Path(root) / RECEIPT_DIR / f"{PREFIX}_{day}.json"


def receipt_files(root):
    """Read both layouts during upgrades/cache restore; never treat loss as empty history."""
    root = Path(root)
    return sorted([
        *root.glob(f"{PREFIX}_????-??-??.json"),
        *(root / RECEIPT_DIR).glob(f"{PREFIX}_????-??-??.json"),
        *(root / RECEIPT_DIR).glob(f"{PREFIX}_????-??-??_*.json"),
    ])


def has_receipt(root, day):
    canonical = receipt_path(root, day)  # also validates the requested date
    # Migration publishes the internal copy before removing the legacy copy.
    return ((Path(root) / canonical.name).exists() or canonical.exists()
            or any((Path(root) / RECEIPT_DIR).glob(f"{PREFIX}_{day}_*.json")))


def _validate_bets(row):
    """Refuse internally inconsistent paper positions, not just bad checksums."""
    signatures = set()
    stake_total = 0.0
    candidates_by_id = {c["candidate_id"]: c for c in row["candidates"]}
    if len(candidates_by_id) != len(row["candidates"]):
        raise ValueError("duplicate paper candidate IDs")
    for acca in row["accas"]:
        legs = acca["legs"]
        if len(legs) < 2:
            raise ValueError("invalid paper acca: fewer than two legs")
        odds, stake = acca["odds"], acca["stake_units"]
        if (
            type(odds) not in (int, float)
            or not math.isfinite(odds)
            or odds <= 1
            or type(stake) not in (int, float)
            or not math.isfinite(stake)
            or stake <= 0
        ):
            raise ValueError("invalid paper price or stake")
        if len({c["book"].strip().casefold() for c in legs}) != 1:
            raise ValueError("mixed-book paper acca")
        signature = tuple(sorted(c["candidate_id"] for c in legs))
        if signature in signatures:
            raise ValueError("duplicate paper acca")
        signatures.add(signature)
        used = set()  # shared teams ACROSS accas are allowed, never within one
        for c in legs:
            teams = set(c["fixture"][1:])
            if (
                len(teams) != 2
                or used.intersection(teams)
                or c != candidates_by_id.get(c["candidate_id"])
                or not c["book"].strip()
                or type(c["odds"]) not in (int, float)
                or not math.isfinite(c["odds"])
                or c["odds"] <= 1
                or type(c["probability"]) not in (int, float)
                or not 0 < c["probability"] < 1
            ):
                raise ValueError("invalid or repeated paper leg")
            used.update(teams)
        if not math.isclose(odds, math.prod(c["odds"] for c in legs), rel_tol=1e-12):
            raise ValueError("paper acca price differs from original quote product")
        stake_total += stake
    available = row.get("paper_available_at_decision")
    if (row["accas"] and available is None) or (
        available is not None
        and (
            type(available) not in (int, float)
            or not math.isfinite(available)
            or available < 0
            or stake_total > available + 1e-6
        )
    ):
        raise ValueError("paper stakes exceed frozen available capital")
    if row.get("schema") == SCHEMA and stake_total > (available or 0) * MAX_PAPER_EXPOSURE + 1e-6:
        raise ValueError("paper stakes exceed declared v2 exposure limit")


def _validate_concentration_record(row, *, required=False):
    """Old evidence stays legacy; any new declaration is strict and fail-closed."""
    policy_container = row.get("policy")
    declared = isinstance(policy_container, dict) and "fixture_concentration" in policy_container
    has_audit = "fixture_concentration" in row
    if not declared and not has_audit:
        if required:
            raise ValueError("new ML paper publication lacks fixture concentration policy")
        return
    if not declared or not has_audit:
        raise ValueError("incomplete ML paper fixture concentration evidence")
    bank = _nonnegative_finite(row.get("paper_bank_at_decision"), "total paper bank")
    committed = _nonnegative_finite(row.get("paper_pending_reserved_at_decision"), "paper commitments")
    available = _nonnegative_finite(row.get("paper_available_at_decision"), "free paper bank")
    if not math.isclose(available, max(0.0, bank - committed), rel_tol=0, abs_tol=1e-9):
        raise ValueError("fixture concentration capital disagrees with bank")
    expected_policy = _fixture_concentration_policy(bank)
    if policy_container["fixture_concentration"] != expected_policy:
        raise ValueError("invalid or unsupported ML paper fixture concentration policy")
    audit = row["fixture_concentration"]
    expected_keys = {
        "input_stake_micro_units", "fixture_projected_stake_micro_units",
        "published_stake_micro_units", "released_stake_micro_units", "input_acca_count",
        "dropped_acca_count", "aggregate_budget_scale",
        "fixture_exposures_overlap_not_additive_bank_commitments",
        "fixtures",
    }
    if not isinstance(audit, dict) or set(audit) != expected_keys:
        raise ValueError("invalid fixture concentration audit schema")
    for key in expected_keys - {"aggregate_budget_scale", "fixtures",
                                "fixture_exposures_overlap_not_additive_bank_commitments"}:
        if type(audit[key]) is not int or audit[key] < 0:
            raise ValueError("invalid fixture concentration audit integer")
    scale = audit["aggregate_budget_scale"]
    if (type(scale) not in (int, float) or not math.isfinite(scale) or not 0 <= scale <= 1
            or audit["fixture_exposures_overlap_not_additive_bank_commitments"] is not True
            or not isinstance(audit["fixtures"], list)):
        raise ValueError("invalid fixture concentration audit values")
    if not (audit["input_stake_micro_units"] >= audit["fixture_projected_stake_micro_units"]
            >= audit["published_stake_micro_units"]):
        raise ValueError("fixture concentration audit increases stake")
    if audit["released_stake_micro_units"] != (
            audit["input_stake_micro_units"] - audit["published_stake_micro_units"]):
        raise ValueError("fixture concentration released stake mismatch")
    actual = _fixture_exposure_micro_units(row["accas"])
    total = sum(_stake_micro_units(a["stake_units"]) for a in row["accas"])
    headroom = _aggregate_headroom_micro_units(bank, committed)
    if (total != audit["published_stake_micro_units"] or total > headroom
            or total > _decimal_micro_units(available, "free paper bank")
            or audit["dropped_acca_count"] != audit["input_acca_count"] - len(row["accas"])):
        raise ValueError("published paper capital audit mismatch")
    expected_scale = (min(1.0, headroom / audit["fixture_projected_stake_micro_units"])
                      if audit["fixture_projected_stake_micro_units"] else 1.0)
    if not math.isclose(scale, expected_scale, rel_tol=1e-12, abs_tol=1e-15):
        raise ValueError("fixture concentration aggregate scale mismatch")
    limit = expected_policy["fixture_limit_micro_units"]
    seen = set()
    entry_keys = {
        "fixture", "prior_open_stake_micro_units", "residual_budget_micro_units",
        "input_stake_micro_units", "fixture_projected_stake_micro_units",
        "published_stake_micro_units", "total_open_stake_micro_units", "idle_budget_micro_units",
    }
    for entry in audit["fixtures"]:
        if not isinstance(entry, dict) or set(entry) != entry_keys:
            raise ValueError("invalid audited fixture schema")
        fixture = _fixture_key(entry["fixture"])
        if fixture in seen or entry["fixture"] != list(fixture):
            raise ValueError("duplicate or noncanonical audited fixture order")
        seen.add(fixture)
        for key in entry_keys - {"fixture"}:
            if type(entry[key]) is not int or entry[key] < 0:
                raise ValueError("invalid audited fixture integer")
        prior = entry["prior_open_stake_micro_units"]
        residual = max(0, limit - prior)
        final = actual.get(fixture, 0)
        if (entry["residual_budget_micro_units"] != residual
                or entry["published_stake_micro_units"] != final
                or final > residual
                or not entry["input_stake_micro_units"]
                >= entry["fixture_projected_stake_micro_units"] >= final
                or entry["total_open_stake_micro_units"] != prior + final
                or entry["idle_budget_micro_units"] != residual - final):
            raise ValueError("audited fixture exposure violates the approved budget")
    if set(actual) - seen:
        raise ValueError("published fixture missing from concentration audit")
    if [tuple(e["fixture"]) for e in audit["fixtures"]] != sorted(seen):
        raise ValueError("fixture concentration audit is not canonically ordered")
    for acca in row["accas"]:
        stake = _stake_micro_units(acca["stake_units"])
        fraction = acca.get("stake_fraction_of_free_bank")
        allocation = acca.get("portfolio_allocation")
        if (type(fraction) not in (int, float) or not math.isfinite(fraction)
                or not math.isclose(fraction, stake / MICRO_UNITS / available,
                                    rel_tol=1e-12, abs_tol=1e-15)
                or not isinstance(allocation, dict)
                or allocation.get("aggregate_budget_scale") != scale):
            raise ValueError("published acca sizing audit mismatch")
        for leg in acca["legs"]:
            if tuple(leg["fixture"]) != (leg["date"], source_team_key(leg["home"]),
                                         source_team_key(leg["away"])):
                raise ValueError("published leg lacks canonical fixture identity")


def validate_record(row, day, *, draft=False):
    """Shared read/restore validation; no rewriting or financial-state access."""
    if (
        row.get("schema") not in READABLE_SCHEMAS
        or row.get("date") != day
        or row.get("sha256") != digest({k: v for k, v in row.items() if k != "sha256"})
    ):
        raise ValueError("invalid autobets_ML evidence checksum/schema/date")
    captured = parse_zoned_timestamp(row.get("captured_at"))
    if captured is None or captured.astimezone(LOCAL_TZ).date().isoformat() != day:
        raise ValueError("invalid paper decision timestamp")
    if draft:
        freeze = datetime.fromisoformat(day).replace(tzinfo=LOCAL_TZ, hour=9)
        persisted = parse_zoned_timestamp(row.get("draft_persisted_at"))
        if (
            row.get("status") != "draft_not_yet_frozen"
            or persisted is None
            or not captured <= persisted < freeze
            or row.get("freeze_at") != freeze.isoformat()
        ):
            raise ValueError("invalid pre-cutoff paper draft")
    elif row.get("freeze_basis") == ROLLING_FREEZE:
        _validate_rolling_record(row, captured)
    else:
        freeze = datetime.fromisoformat(day).replace(tzinfo=LOCAL_TZ, hour=9)
        published = parse_zoned_timestamp(row.get("persisted_at"))
        if (
            row.get("status") not in {"paper_accas", "no_paper_bet", "missed_freeze_no_paper_bet"}
            or published is None
            or published < freeze
            or row.get("freeze_at") != freeze.isoformat()
        ):
            raise ValueError("unfrozen record cannot enter paper performance")
        if row["status"] == "missed_freeze_no_paper_bet":
            if captured < freeze or row["candidates"] or row["accas"]:
                raise ValueError("invalid missed-freeze evidence")
        elif row.get("freeze_basis") == ACTUAL_RUN_FREEZE:
            # New first-run freezes are decisions at actual runtime, not
            # backdated selections masquerading as a pre-09:00 saved draft.
            if (
                captured > published
                or published.astimezone(LOCAL_TZ).date().isoformat() != day
                or parse_zoned_timestamp(row.get("frozen_at")) != published
                or row.get("draft_persisted_at") is not None
                or row.get("draft_sha256") is not None
            ):
                raise ValueError("invalid actual-run paper freeze evidence")
        else:
            if row.get("freeze_basis") is not None:
                raise ValueError("unknown paper freeze basis")
            saved = parse_zoned_timestamp(row.get("draft_persisted_at"))
            draft_sha = row.get("draft_sha256")
            if (
                saved is None
                or not captured <= saved < freeze
                or not isinstance(draft_sha, str)
                or len(draft_sha) != 64
                or any(c not in "0123456789abcdef" for c in draft_sha)
            ):
                raise ValueError("frozen paper record lacks pre-cutoff evidence")
    if not draft and bool(row["accas"]) != (row["status"] == "paper_accas"):
        raise ValueError("paper receipt status/positions disagree")
    _validate_bets(row)
    _validate_concentration_record(row)


def receipts(root):
    """Corrupt evidence is an error, never an empty/reset performance history."""
    if (Path(root) / f"{PREFIX}_integrity_block.json").exists():
        raise ValueError("autobets_ML evidence conflict; paper lane blocked, live lanes unchanged")
    result = {}
    blobs = {}
    for path in receipt_files(root):
        try:
            blob = path.read_bytes()
        except FileNotFoundError:
            if path.parent != Path(root):
                raise
            # Another reader may have held the old directory listing while a
            # locked migration durably published, then unlinked, this legacy copy.
            path = receipt_path(root, path.stem.removeprefix(f"{PREFIX}_"))
            blob = path.read_bytes()  # absence still fails closed, never empty history
        row = json.loads(blob)
        unsigned = {k: v for k, v in row.items() if k != "sha256"}
        day = path.stem.removeprefix(f"{PREFIX}_")[:10]
        canonical = (rolling_receipt_path(root, row) if row.get("freeze_basis") == ROLLING_FREEZE
                     else receipt_path(root, day))
        if (
            row.get("schema") not in READABLE_SCHEMAS
            or row.get("sha256") != digest(unsigned)
            or row.get("date") != day
            or path not in (canonical, Path(root) / canonical.name)
        ):
            raise ValueError(f"invalid ML paper receipt: {path.name}")
        validate_record(row, row["date"])
        day = (row["date"], row.get("decision_id", ""))
        if day in blobs and blobs[day] != blob:
            raise ValueError(f"conflicting ML paper receipt layouts: {day}")
        blobs[day] = blob
        result[day] = row
    ordered = sorted(result.values(), key=lambda r: (parse_zoned_timestamp(r["captured_at"]), r.get("decision_id", "")))
    committed = defaultdict(int)
    prior_hashes = []
    for row in ordered:
        fixtures = {tuple(c["fixture"]) for a in row["accas"] for c in a["legs"]}
        if row.get("freeze_basis") == ROLLING_FREEZE:
            reused = set(committed).intersection(fixtures)
            if reused:
                audit = row.get("fixture_concentration") or {}
                prior = {tuple(e["fixture"]): e["prior_open_stake_micro_units"]
                         for e in audit.get("fixtures", [])}
                # The approved cap replaces the old unconditional fixture ban,
                # not the protection against missing/understated prior stakes.
                # Since settled fixtures never reopen, every earlier stake on
                # a reused fixture must be present in its frozen prior budget.
                if any(prior.get(f) != committed[f] for f in reused):
                    raise ValueError("rolling fixture reuse lacks complete prior stake evidence")
            if row.get("prior_receipt_sha256s") != prior_hashes:
                raise ValueError("rolling paper history fork or missing capital evidence")
        for acca in row["accas"]:
            stake = _decimal_micro_units(acca["stake_units"], "prior open stake", rounding=ROUND_CEILING)
            for fixture in {tuple(c["fixture"]) for c in acca["legs"]}:
                committed[fixture] += stake
        prior_hashes.append(row["sha256"])
    return ordered


def _migrate_frozen_receipts(root):
    """Caller holds the lane lock. Validate everything before moving exact bytes."""
    receipts(root)  # corruption, conflicts and integrity blocks must never disappear
    root = Path(root)
    moved = 0
    for legacy in sorted(root.glob(f"{PREFIX}_????-??-??.json")):
        blob = legacy.read_bytes()
        day = legacy.stem.removeprefix(f"{PREFIX}_")
        destination = receipt_path(root, day)
        _archive_bytes(root, destination.relative_to(root), blob)
        # The archive is nested two levels deep. Persist the new receipt-dir
        # entry in its audit parent as well, before unlinking the legacy copy.
        _sync_directory(destination.parent.parent)
        _sync_directory(root)
        if legacy.read_bytes() != blob:
            raise ValueError("ML paper receipt changed during migration")
        legacy.unlink()  # only after durable publication of identical bytes
        _sync_directory(root)
        moved += 1
    return moved


def migrate_receipts(root):
    """Storage-only migration: no selection, settlement, learning or receipt rewriting."""
    root = Path(root)
    if not root.exists():
        return 0
    with (root / f".{PREFIX}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _migrate_frozen_receipts(root)


def hit(market, selection, hs, gs):
    if market == "1x2":
        outcome = "home" if hs > gs else "away" if gs > hs else "draw"
        return outcome == selection if selection in {"home", "away", "draw"} else None
    if market == "double_chance":
        selection = {"1x": "home", "x2": "away", "12": "draw"}.get(selection, selection)
    return check_enhancement_hit(market, selection, hs, gs)


def probability(weights, market, selection):
    outcomes = [(hit(market, selection, h, a), w) for h, a, w in weights]
    if any(value is None for value, _ in outcomes):
        return None
    return sum(w for value, w in outcomes if value) / sum(w for _, w in outcomes)


def _same(a, b):
    return (
        bool(a)
        and bool(b)
        and source_team_key(a) == source_team_key(b)
        and not squad_marker_mismatch(a, b)
    )


def _quote_max_age(source):
    """ML's ceiling may tighten a source limit, never extend a stricter one."""
    if psrc.spec(source).family == psrc.spec("oddspapi").family:
        return min(QUOTE_MAX_AGE, timedelta(hours=ODDSPAPI_MAX_AGE_H))
    if psrc.spec(source).family == psrc.spec("betexplorer").family:
        from .sources.betexplorer_odds import CACHE_FRESHNESS_H
        if not math.isfinite(CACHE_FRESHNESS_H) or CACHE_FRESHNESS_H < 0:
            return timedelta(0)
        return min(QUOTE_MAX_AGE, timedelta(hours=CACHE_FRESHNESS_H))
    # Other source/index admission guards remain in their existing paths.
    return QUOTE_MAX_AGE


def _quote_ok(
    row, quote, now, kickoff, source_guard, min_leg_odds, *, market, selection, freeze_at=None, rolling=False
):
    """Keep original quote evidence; require validity now AND at paper freeze."""
    side = {"1x": "home", "x2": "away", "12": "draw"}.get(selection, selection)
    probe = dict(row, as_of=now.isoformat(), pick=side, recommended_enhancement=market, **quote)
    source = probe.get("enhancement_price_source")
    if (
        source_guard(source) is not None
        or not psrc.resolvable(source)
        or not psrc.spec(source).named_bookmaker
        or probe.get("enhancement_priced") is not True
        or probe.get("enhancement_price_rejection")
    ):
        return False
    # The shared live validator expects a same-day decision. In rolling ML
    # only, its calendar field describes the ACTUAL decision day, not the
    # future fixture day. Original fixture identity/date and all timestamps
    # remain unchanged and are checked separately by candidates/receipts.
    context_probe = dict(probe, date=now.date().isoformat()) if rolling else probe
    context = enhancement_price_context(context_probe)
    if context is None:
        return False
    at = parse_zoned_timestamp(context["captured_at"])
    ku = parse_zoned_timestamp(context["kickoff"])
    age_at = max(now, freeze_at or now)
    if (
        ku != kickoff
        or not at <= now <= age_at < ku
        or age_at - at > _quote_max_age(source)
        or context["price"] < min_leg_odds
    ):
        return False
    if psrc.spec(source).family == psrc.spec("betexplorer").family:
        return betexplorer_price_rejection(probe, execution_at=age_at) is None
    return True


def _quote(price, book, at, source, kickoff, provenance=None):
    return {
        "enhancement_price": price,
        "enhancement_price_book": book,
        "enhancement_price_at": at,
        "enhancement_price_source": source,
        "enhancement_price_kickoff": kickoff,
        "enhancement_price_provenance": provenance,
        "enhancement_priced": True,
        "enhancement_price_rejection": None,
    }


def candidates(slate, day, now, index, *, kickoff_fn, source_guard, min_leg_odds, freeze_at=None, rolling=False):
    """All supported FT markets, not only the live lane's chosen enhancement.

    Full canonical pair/orientation/squad + identical proven kickoff required.
    Legacy truncated buckets/5-tuples, swaps, fuzzy joins and synthetic odds are
    unavailable. Models competing for one quote are chosen by training N, NOT
    by which prediction looks most profitable. Every qualified quote is saved.
    """
    rejected = Counter()
    result = {}
    models = {}
    eligible = []
    for row in slate:
        profile = row.get("statistical_profile") if isinstance(row, dict) else None
        model = profile.get("ml_model") if isinstance(profile, dict) else None
        if not isinstance(model, dict) or type(model.get("n")) is not int:
            rejected["fixture_bound_ml_unavailable"] += 1
            continue
        eligible.append(row)
    ordered = sorted(
        eligible,
        key=lambda r: (-r["statistical_profile"]["ml_model"]["n"], str(r.get("contract_id") or "")),
    )
    fixture_kickoffs = {}
    ambiguous_fixtures = set()
    inverse = {v: k for k, v in MARKET_PRICE_MAP.items() if v is not None and k != "double_chance"}
    # Same predecision materialisation used by the existing ENH price path.
    # Raw BE context is not itself an admitted quote, nor a reason to bypass it.
    index = _betexplorer_asof_index(index, now)
    ambiguous_quotes = {}
    for row in ordered:
        if row.get("date") != day or row.get("sport", "soccer") != "soccer":
            rejected["wrong_day_or_sport"] += 1
            continue
        observed = parse_zoned_timestamp(row.get("as_of"))
        built = parse_zoned_timestamp(row.get("built_at_utc")) if row.get("built_at_utc") else None
        if observed is None or observed > now or (built is not None and built > now):
            rejected["input_not_known_at_decision"] += 1
            continue
        bucket = str(row.get("bucket") or "")
        if (
            not bucket
            or "SUSPECT_PRICE" in bucket
            or "NO_ODDS" in bucket
            or row.get("price_evidence") == "SUSPECT_ALIAS_FUZZY"
            or str(row.get("price_quarantine_reason") or "").lower()
            in {"alias_fuzzy", "suspect", "suspect_alias_fuzzy"}
        ):
            rejected["data_quality"] += 1
            continue
        kickoff = kickoff_fn(row)
        if kickoff is None or kickoff < max(now, freeze_at or now) + MIN_LEAD:
            rejected["kickoff_unproven_or_too_close"] += 1
            continue
        # Date-only donor results cannot establish whether an overnight
        # UTC/SAST boundary belongs to one calendar day or the other. Do not
        # emit an unresolvable position or guess a neighbouring result date.
        if kickoff.astimezone(UTC).date() != kickoff.astimezone(LOCAL_TZ).date():
            rejected["settlement_calendar_ambiguous"] += 1
            continue
        fixture_key = (day, source_team_key(row.get("home")), source_team_key(row.get("away")))
        previous_kickoff = fixture_kickoffs.setdefault(fixture_key, kickoff)
        if previous_kickoff != kickoff:
            ambiguous_fixtures.add(fixture_key)
        profile = row.get("statistical_profile") or {}
        model = profile.get("ml_model") or {}
        # The alternative explicitly uses form/forecast-aware v2, not an old
        # confidence-only fit silently sold as the new paper experiment.
        weights = (
            enhancement_ml_score_weights(row)
            if model.get("schema") == "enh_score_logit_v2"
            else None
        )
        if weights is None:
            rejected["fixture_bound_ml_unavailable"] += 1
            continue
        key = (day, source_team_key(row.get("home")), source_team_key(row.get("away")))
        if min(len(key[1]), len(key[2])) < 4 or key[1] == key[2]:
            rejected["identity_unresolved"] += 1
            continue
        quotes = []
        # Existing full 1X2 board; primary quote only for the parent's side.
        primary = {
            "home": row.get("home"),
            "away": row.get("away"),
            "market": "1x2",
            "selection": row.get("pick"),
            "odds": row.get("odds"),
            "bookmaker": row.get("bookmaker"),
            "source": row.get("odds_source"),
            "captured_at": row.get("odds_captured_at"),
            "kickoff": row.get("kickoff_utc"),
        }
        for q in [primary, *(row.get("price_board") or [])]:
            if (
                q.get("market") != "1x2"
                or q.get("line") is not None
                or q.get("price_coherence")
                or not _same(q.get("home"), row.get("home"))
                or not _same(q.get("away"), row.get("away"))
            ):
                continue
            quotes.append(
                (
                    "1x2",
                    q.get("selection"),
                    _quote(
                        q.get("odds"),
                        q.get("bookmaker"),
                        q.get("captured_at"),
                        q.get("source"),
                        q.get("kickoff"),
                    ),
                )
            )
        # Same local quote index as ENH, but never its width-9/pair-only fallback.
        pair = (norm_team(row.get("home")), norm_team(row.get("away")))
        for mapping, rows in (index.get("fixture_quotes", {}).get(pair, {}) or {}).items():
            market = (
                "double_chance"
                if mapping in {("dc", "1x"), ("dc", "x2"), ("dc", "12")}
                else inverse.get(mapping)
            )
            if market is None:
                continue
            for q in rows:
                if (
                    len(q) < 7
                    or not isinstance(q[6], (tuple, list))
                    or len(q[6]) != 2
                    or not _same(q[6][0], row.get("home"))
                    or not _same(q[6][1], row.get("away"))
                ):
                    rejected["quote_identity_unproven"] += 1
                    continue
                quotes.append((market, mapping[1], _quote(*q[:6])))
        for market, selection, q in quotes:
            p = probability(weights, market, selection)
            if (
                p is None
                or not 0 < p < 1
                or not _quote_ok(
                    row,
                    q,
                    now,
                    kickoff,
                    source_guard,
                    min_leg_odds,
                    market=market,
                    selection=selection,
                    freeze_at=freeze_at, rolling=rolling,
                )
            ):
                rejected["quote_or_probability_unavailable"] += 1
                continue
            book = q["enhancement_price_book"].strip()
            identity = (*key, market, selection, book.casefold())
            quote_at = parse_zoned_timestamp(q["enhancement_price_at"])
            if identity in ambiguous_quotes:
                if quote_at <= ambiguous_quotes[identity]:
                    continue
                del ambiguous_quotes[identity]
            if identity in result:
                previous = result[identity]
                # Model ownership is selected by training N/contract ordering,
                # never by cherry-picking whichever model predicts best EV.
                if previous["model_key"] != model["model_key"]:
                    continue
                prior_at = parse_zoned_timestamp(previous["price_at"])
                quote_at = parse_zoned_timestamp(q["enhancement_price_at"])
                if quote_at < prior_at:
                    continue
                if quote_at == prior_at:
                    if previous["odds"] != q["enhancement_price"]:
                        del result[identity]
                        ambiguous_quotes[identity] = quote_at
                        rejected["same_time_same_book_price_conflict"] += 1
                    continue
            candidate = {
                "date": day,
                "home": row["home"],
                "away": row["away"],
                "fixture": list(key),
                "market": market,
                "selection": selection,
                "bucket": bucket,
                "odds": q["enhancement_price"],
                "book": book,
                "price_source": q["enhancement_price_source"],
                "price_at": q["enhancement_price_at"],
                "price_age_seconds_at_decision": (now - quote_at).total_seconds(),
                "price_age_seconds_at_freeze": (
                    max(now, freeze_at or now) - quote_at
                ).total_seconds(),
                "kickoff_utc": kickoff.isoformat(),
                "price_provenance": q.get("enhancement_price_provenance"),
                "base_probability": p,
                "probability": p,
                "model_key": model["model_key"],
                "contract_id": row["contract_id"],
                "ml_inputs": profile.get("ml_inputs"),
            }
            candidate["candidate_id"] = digest(identity)
            result[identity] = candidate
            models[model["model_key"]] = model
    if ambiguous_fixtures:
        rejected["fixture_schedule_conflict"] = len(ambiguous_fixtures)
    return (
        [c for c in result.values() if tuple(c["fixture"]) not in ambiguous_fixtures],
        models,
        dict(rejected),
    )


def _recency_weight(candidate, today):
    try:
        age_days = max(0, (today - datetime.strptime(candidate["date"], "%Y-%m-%d").date()).days)
    except (KeyError, TypeError, ValueError):
        return 1.0
    return 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)


def _valid_learning_candidate(candidate):
    """Shape guard: malformed historical candidates are skipped, never fatal."""
    if not isinstance(candidate, dict):
        return False
    p = candidate.get("base_probability")
    try:
        _fixture_key(candidate.get("fixture"))
    except (ValueError, TypeError):
        return False
    return (
        type(p) in (int, float) and math.isfinite(p) and 0 < p < 1
        and isinstance(candidate.get("date"), str)
        and isinstance(candidate.get("bucket"), str) and bool(candidate["bucket"])
        and isinstance(candidate.get("market"), str) and bool(candidate["market"])
        and isinstance(candidate.get("selection"), str) and bool(candidate["selection"])
    )


def _success_groups(candidate):
    """Groups whose recent success may tilt a candidate's probability."""
    groups = [f"bucket:{candidate['bucket']}", f"market:{candidate['market']}"]
    source = source_forecast_probability(candidate)
    if source is None:
        groups.append("gap:source_unavailable")
    else:
        gap_pp = (candidate["base_probability"] - source) * 100
        if gap_pp < 0:
            groups.append("gap:negative")
        elif gap_pp < 10:
            groups.append("gap:0_to_10pp")
        elif gap_pp < 20:
            groups.append("gap:10_to_20pp")
        else:
            groups.append("gap:20pp_plus")
    return groups


def _reference_probability(candidate, model):
    """Calibrated probability when the logistic fit exists, else the base."""
    if model.get("status") != "fitted_prior_paper_errors":
        return candidate["base_probability"]
    z = model["intercept"] + sum(
        w * x for w, x in zip(model["coef"], _vector(candidate, model["columns"]))
    )
    return 1 / (1 + math.exp(-max(-700.0, min(700.0, z))))


def _fit_logistic_calibrator(rows, weights, columns):
    """(calibration | None, sklearn_available). Failure degrades, never raises."""
    import warnings

    try:
        from sklearn.exceptions import ConvergenceWarning
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        return None, False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
            model.fit([_vector(c, columns) for c, _ in rows],
                      [y for _, y in rows], sample_weight=weights)
    except (ValueError, ArithmeticError, ConvergenceWarning):
        return None, True
    return {"columns": columns, "coef": model.coef_[0].tolist(),
            "intercept": float(model.intercept_[0])}, True


def _crossfit_references(rows, weights, columns):
    """Out-of-sample reference per row: fit on other fixtures, predict held-out.

    Fixtures are fold-grouped (a fixture never predicts itself), folds are a
    stable CRC of the canonical fixture key — deterministic across processes.
    Held-out rows whose training folds lack both classes, or whose fit is
    unavailable, fall back to the base probability.
    """
    folds = [zlib.crc32(repr(tuple(c["fixture"])).encode()) % SUCCESS_TILT_FOLDS
             for c, _ in rows]
    references = [c["base_probability"] for c, _ in rows]
    used = False
    for fold in sorted(set(folds)):
        train = [i for i in range(len(rows)) if folds[i] != fold]
        held = [i for i in range(len(rows)) if folds[i] == fold]
        if len({rows[i][1] for i in train}) < 2:
            continue
        calibration, _ = _fit_logistic_calibrator(
            [rows[i] for i in train], [weights[i] for i in train], columns)
        if calibration is None:
            continue
        model = dict(calibration, status="fitted_prior_paper_errors")
        for i in held:
            references[i] = _reference_probability(rows[i][0], model)
        used = True
    return references, used


def learn(history, now, score_lookup):
    """Dynamic learning on this lane's immutable, prior-day forward observations.

    Two separately auditable layers, refit at every decision from the first
    resolved prior-day results (no evidence gate):
    1. a regularised, recency-weighted logistic calibrator on
       logit(base probability) plus bucket/market effects — it needs both
       outcome classes, a mathematical requirement, not an evidence gate;
    2. a bounded success tilt shifting probabilities toward bucket/market/
       source-gap groups beating their reference (calibrated or base)
       expectations, and away from groups trailing them.
    The combined shift is evidence-smoothed, scaled by
    fixtures/(fixtures+5): dynamic from the first result, gentle early,
    full strength only as resolved evidence accumulates. The tilt judges
    success against expectation (hit rate minus reference rate), never raw
    hit rate, so heavy favourites cannot look successful merely by hitting.
    Repeated book/market quotes do not manufacture independent games: each
    fixture receives total sample weight one before recency weighting.
    Never fitted on today's outcomes (prior-day receipts only).
    """
    rows = []
    training_outcomes = []
    training_keys = set()
    today = now.astimezone(LOCAL_TZ).date().isoformat()
    for receipt in history:
        captured = parse_zoned_timestamp(receipt.get("captured_at"))
        if receipt["date"] >= today or captured is None or captured >= now:
            continue
        for c in receipt.get("candidates") or []:
            if not _valid_learning_candidate(c) or c["date"] >= today:
                continue
            score = score_lookup(c)
            if score is None:
                continue
            y = hit(c["market"], c["selection"], *score)
            if y is not None:
                # Book/price variants have identical calibration features and
                # outcomes. Counting them would reweight a market merely for
                # having broader bookmaker coverage, even with fixture weights.
                training_key = (
                    tuple(c["fixture"]),
                    c["market"],
                    c["selection"],
                    c["bucket"],
                    c["base_probability"],
                    c.get("model_key"),
                )
                if training_key in training_keys:
                    continue
                training_keys.add(training_key)
                rows.append((c, int(y)))
                training_outcomes.append(
                    {
                        "receipt_sha256": receipt.get("sha256"),
                        "candidate_id": c["candidate_id"],
                        "date": c["date"],
                        "fixture": c["fixture"],
                        "score": list(score),
                        "hit": int(y),
                    }
                )
    fixtures = {tuple(c["fixture"]) for c, _ in rows}
    result = {
        "status": "awaiting_prior_paper_results",
        "fixtures": len(fixtures),
        "observations": len(rows),
        "training_sha256": digest(rows),
        "training_outcomes": training_outcomes,
        "training_outcomes_sha256": digest(training_outcomes),
        "training_last_date": max((c["date"] for c, _ in rows), default=None),
        "learning_policy": DYNAMIC_LEARNING_POLICY,
        "evidence_gate": "none_from_first_resolved_prior_day_results_evidence_smoothed",
        "smoothing_k_fixtures": LEARNING_SMOOTHING_K_FIXTURES,
        "smoothing_factor": (len(fixtures) / (len(fixtures) + LEARNING_SMOOTHING_K_FIXTURES)
                             if fixtures else 0.0),
        "recency_half_life_days": RECENCY_HALF_LIFE_DAYS,
        "success_tilt_total_limit_logit": SUCCESS_TILT_TOTAL_LIMIT_LOGIT,
        "success_tilt": {},
    }
    if not rows:
        return result
    today_date = now.astimezone(LOCAL_TZ).date()
    counts = Counter(tuple(c["fixture"]) for c, _ in rows)
    weights = [1 / counts[tuple(c["fixture"])] * _recency_weight(c, today_date)
               for c, _ in rows]
    fitted = False
    if len({y for _, y in rows}) >= 2:
        # Same regularised estimator already used by the existing feature
        # model; dynamic now: every observed bucket/market is a column.
        # A missing/broken sklearn degrades to tilt-only, never lane failure.
        columns = sorted({f"{field}:{c[field]}" for c, _ in rows
                          for field in ("bucket", "market")})
        calibration, _available = _fit_logistic_calibrator(rows, weights, columns)
        if calibration is not None:
            result.update(status="fitted_prior_paper_errors", **calibration)
            fitted = True
        else:
            result["status"] = "learning_fit_unavailable_existing_model_retained"
    else:
        columns = sorted({f"{field}:{c[field]}" for c, _ in rows
                          for field in ("bucket", "market")})
    # Success tilt: per-group recency-weighted hit rate versus CROSS-FITTED
    # (out-of-sample) reference expectation — never the in-sample residuals
    # of the calibration just fitted on the same rows.
    references, crossfit_used = _crossfit_references(rows, weights, columns)
    result["success_tilt_reference"] = (
        "cross_fitted_calibration_out_of_sample" if crossfit_used else "base_probability")
    result["success_tilt_folds"] = SUCCESS_TILT_FOLDS
    groups = {}
    for (c, y), weight, reference in zip(rows, weights, references):
        for key in _success_groups(c):
            entry = groups.setdefault(key, {"weight": 0.0, "hits": 0.0,
                                            "expected": 0.0, "fixtures": set()})
            entry["weight"] += weight
            entry["hits"] += weight * y
            entry["expected"] += weight * reference
            entry["fixtures"].add(tuple(c["fixture"]))
    result["success_tilt"] = {
        key: {
            "fixtures": len(entry["fixtures"]),
            "weighted_observations": entry["weight"],
            "weighted_hit_rate": entry["hits"] / entry["weight"],
            "weighted_reference_rate": entry["expected"] / entry["weight"],
            "excess": entry["hits"] / entry["weight"] - entry["expected"] / entry["weight"],
            "tilt_logit": max(-SUCCESS_TILT_GROUP_LIMIT_LOGIT,
                              min(SUCCESS_TILT_GROUP_LIMIT_LOGIT,
                                  2.0 * (entry["hits"] / entry["weight"]
                                         - entry["expected"] / entry["weight"]))),
        }
        for key, entry in sorted(groups.items()) if entry["weight"] > 0
    }
    if not fitted and result["status"] == "awaiting_prior_paper_results":
        result["status"] = "dynamic_success_tilt_only"
    return result


def _vector(c, columns):
    p = c["base_probability"]
    return [
        math.log(p / (1 - p)),
        *[float(k in (f"bucket:{c['bucket']}", f"market:{c['market']}")) for k in columns],
    ]


def apply_learning(rows, model):
    """Calibration layer first, then the bounded success tilt, both dynamic.

    The combined dynamic shift (calibration move + success tilt) is scaled by
    the evidence smoothing factor fixtures/(fixtures+K): early wins/losses
    move probabilities gently, full strength only as evidence accumulates.
    Learner records without a smoothing factor (older receipts) apply at 1.0.
    """
    tilt = model.get("success_tilt") or {}
    fitted = model.get("status") == "fitted_prior_paper_errors"
    if not fitted and not tilt:
        return
    smoothing = model.get("smoothing_factor", 1.0)
    for c in rows:
        if not _valid_learning_candidate(c):
            continue
        base_logit = math.log(c["base_probability"] / (1 - c["base_probability"]))
        p = _reference_probability(c, model) if fitted else c["base_probability"]
        # Bucket/market/gap tilts are driven by largely the same fixtures, so
        # they are averaged, not summed: correlated evidence cannot stack.
        group_tilts = [tilt[key]["tilt_logit"] for key in _success_groups(c) if key in tilt]
        shift = sum(group_tilts) / len(group_tilts) if group_tilts else 0.0
        shift = max(-SUCCESS_TILT_TOTAL_LIMIT_LOGIT,
                    min(SUCCESS_TILT_TOTAL_LIMIT_LOGIT, shift))
        dynamic_shift = (math.log(p / (1 - p)) - base_logit) + shift
        if not dynamic_shift:
            continue
        z = base_logit + smoothing * dynamic_shift
        c["probability"] = 1 / (1 + math.exp(-max(-700.0, min(700.0, z))))


def _kelly(p, odds):
    """Model-implied log-bank growth; uncertainty is NOT a guaranteed edge."""
    if not (math.isfinite(p) and math.isfinite(odds) and 0 < p < 1 and odds > 1):
        return None
    fraction = (p * odds - 1) / (odds - 1)
    if not 0 < fraction < 1:
        return None
    growth = p * math.log1p(fraction * (odds - 1)) + (1 - p) * math.log1p(-fraction)
    return fraction, growth


def acca_proposals(rows, *, beam_width=SEARCH_BEAM_WIDTH, diagnostics=None):
    """Exact small-universe enumeration; bounded beam for larger universes.

    Negative-EV singles and prefixes remain searchable. Only completed accas
    need positive joint Kelly. The bound below prunes only prefixes that cannot
    possibly become positive even if every remaining favourable leg is added.
    No greedy removal of teams/fixtures across proposals or across accas.
    """
    books = defaultdict(list)
    for c in sorted(rows, key=lambda c: c["candidate_id"]):
        if (
            type(c["odds"]) in (int, float)
            and type(c["probability"]) in (int, float)
            and math.isfinite(c["odds"])
            and c["odds"] > 1
            and math.isfinite(c["probability"])
            and 0 < c["probability"] < 1
        ):
            books[c["book"].casefold()].append(c)
    proposals = []
    searched = 0
    budget_exhausted = False
    for book_rows in books.values():
        suffix = [0.0] * (len(book_rows) + 1)
        for j in range(len(book_rows) - 1, -1, -1):
            c = book_rows[j]
            suffix[j] = suffix[j + 1] + max(0.0, math.log(c["odds"]) + math.log(c["probability"]))
        beam = [((), frozenset(), 1.0, 1.0)]
        retained = []
        exact = len(book_rows) <= EXACT_SEARCH_SIZE
        while beam:
            expanded = []
            for indices, used, odds, prob in beam:
                for j in range(indices[-1] + 1 if indices else 0, len(book_rows)):
                    searched += 1
                    if searched > SEARCH_NODE_BUDGET:
                        budget_exhausted = True
                        break
                    c = book_rows[j]
                    teams = frozenset(c["fixture"][1:])
                    if len(teams) != 2 or used.intersection(teams):
                        continue
                    d, p = odds * c["odds"], prob * c["probability"]
                    if not math.isfinite(d) or p <= 0:
                        continue
                    optimistic_ev = math.log(d) + math.log(p) + suffix[j + 1]
                    if optimistic_ev <= 0:
                        continue
                    ix = (*indices, j)
                    decision = _kelly(p, d)
                    growth = decision[1] if decision else 0.0
                    # Search breadth is computational, not a cap on acca size.
                    rank = (
                        growth,
                        optimistic_ev,
                        p,
                        tuple(book_rows[k]["candidate_id"] for k in ix),
                    )
                    node = (ix, used | teams, d, p)
                    if exact:
                        expanded.append((rank, node))
                    elif len(expanded) < beam_width:
                        heappush(expanded, (rank, node))
                    elif rank > expanded[0][0]:
                        heapreplace(expanded, (rank, node))
                if budget_exhausted:
                    break
            beam = [node for _, node in sorted(expanded, reverse=True)]
            for ix, _, d, p in beam:
                decision = _kelly(p, d)
                if len(ix) < 2 or decision is None:
                    continue
                f, growth = decision
                legs = [book_rows[k] for k in ix]
                a = {
                    "legs": legs,
                    "odds": d,
                    "probability_estimate": p,
                    "estimated_ev": p * d - 1,
                    "estimated_log_growth": growth,
                    "model_kelly_fraction": f,
                    "book": legs[0]["book"],
                    "odds_basis": "hypothetical_product_of_same_book_single_quotes",
                    "probability_basis": "product_assumes_cross_fixture_independence_not_validated",
                }
                rank = (growth, tuple(c["candidate_id"] for c in legs))
                if exact:
                    retained.append((rank, a))
                elif len(retained) < beam_width:
                    heappush(retained, (rank, a))
                elif rank > retained[0][0]:
                    heapreplace(retained, (rank, a))
            if budget_exhausted:
                break
        proposals.extend(a for _, a in sorted(retained, reverse=True))
        if budget_exhausted:
            break
    if diagnostics is not None:
        diagnostics.update(
            node_expansions=min(searched, SEARCH_NODE_BUDGET),
            node_budget=SEARCH_NODE_BUDGET,
            beam_width=beam_width,
            budget_exhausted=budget_exhausted,
            approximation="exact_small_books_otherwise_bounded_beam",
            candidate_count=len(rows),
        )
    return proposals


def allocate_portfolio(proposals):
    """Joint concave log-utility allocation under worst-case acca dependence.

    For fixed acca win marginals, comonotonic payouts minimise expected log
    wealth: this deliberately does NOT assume independent overlapping accas.
    Marginals inside each acca still assume cross-fixture independence. A
    simplex Frank-Wolfe solve reports its remaining dual gap; neither beam nor
    numerical optimisation is represented as a global strategy optimum.
    """
    import numpy as np
    from scipy.optimize import minimize_scalar
    from threadpoolctl import threadpool_limits

    if not proposals:
        return [], {"status": "no_positive_joint_ev_proposals"}
    ps = np.array([a["probability_estimate"] for a in proposals])
    odds = np.array([a["odds"] for a in proposals])
    edges = np.unique(np.r_[0.0, ps, 1.0])
    weights = np.diff(edges)
    u = (edges[:-1] + edges[1:]) / 2
    order = np.argsort(ps, kind="stable")
    first_winner = np.searchsorted(ps[order], u, side="right")
    winning_states = np.searchsorted(u, ps, side="left")

    def payout(f):
        suffix = np.r_[np.cumsum((f * odds)[order][::-1])[::-1], 0.0]
        return suffix[first_winner] - f.sum()

    def derivatives(wealth):
        cumulative = np.r_[0.0, np.cumsum(weights / wealth)]
        return odds * cumulative[winning_states] - cumulative[-1]

    fractions = np.zeros(len(proposals))
    wealth = np.ones(len(weights))
    gap = float("inf")
    # Reproducible fixed computational budget, not a count/leg/stake recipe.
    with threadpool_limits(limits=1, user_api="blas"):
        for iteration in range(PORTFOLIO_ITERATIONS):
            gradient = derivatives(wealth)
            best = int(np.argmax(gradient))
            vertex = np.zeros(len(proposals))
            if gradient[best] > 0:
                vertex[best] = 1 - 1e-9
            delta = vertex - fractions
            change = payout(delta)
            gap = max(0.0, float(gradient @ delta))
            if gap < 1e-9:
                break

            def objective(alpha, wealth=wealth, change=change):
                return -float(weights @ np.log(wealth + alpha * change))

            result = minimize_scalar(
                objective, bounds=(0.0, 1.0), method="bounded", options={"xatol": 1e-10}
            )
            alpha = float(result.x)
            fractions += alpha * delta
            wealth += alpha * change
        gradient = derivatives(wealth)
        gap = max(0.0, float(max(0.0, gradient.max()) * (1 - 1e-9) - gradient @ fractions))
        full_growth = float(weights @ np.log(wealth))
    scale = min(KELLY_MULTIPLIER, MAX_PAPER_EXPOSURE / max(float(fractions.sum()), 1e-300))
    return (fractions * scale).tolist(), {
        "status": "robust_portfolio_Kelly",
        "dependence": "worst_case_comonotonic_acca_payouts_given_model_marginals",
        "iterations": iteration + 1,
        "duality_gap": gap,
        "full_kelly_estimated_log_growth": full_growth,
        "kelly_multiplier": KELLY_MULTIPLIER,
        "max_free_bank_exposure": MAX_PAPER_EXPOSURE,
        "proposal_count": len(proposals),
        "search": "exact_per_book_up_to_8_candidates_otherwise_512_beam_approximate",
        "diagnostics_scope": "unconstrained_pre_projection_solver_not_published_optimality",
        "published_portfolio_optimality_proven": False,
    }


def _nonnegative_finite(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"invalid {name}")
    return value


def _decimal_micro_units(value, name, *, rounding=ROUND_FLOOR):
    _nonnegative_finite(value, name)
    return int((Decimal(str(value)) * MICRO_UNITS).to_integral_value(rounding=rounding))


def _stake_micro_units(value):
    """New stakes live on the existing downward-floored 1e-6 unit grid."""
    _nonnegative_finite(value, "paper stake")
    scaled = Decimal(str(value)) * MICRO_UNITS
    if scaled != scaled.to_integral_value():
        raise ValueError("paper stake is not on the micro-unit grid")
    return int(scaled)


def _fixture_limit_micro_units(total_bank_units):
    _nonnegative_finite(total_bank_units, "total paper bank")
    # Decimal avoids rounding 4.59015985 up to 4.590160 at a grid boundary.
    limit = (Decimal(str(total_bank_units)) * Decimal(str(MAX_FIXTURE_STAKE_FRACTION))
             * MICRO_UNITS)
    return int(limit.to_integral_value(rounding=ROUND_FLOOR))


def _aggregate_headroom_micro_units(bank, committed):
    _nonnegative_finite(bank, "total paper bank")
    _nonnegative_finite(committed, "paper commitments")
    remaining = (Decimal(str(bank)) * Decimal(str(MAX_PAPER_EXPOSURE))
                 - Decimal(str(committed)))
    return max(0, int((remaining * MICRO_UNITS).to_integral_value(rounding=ROUND_FLOOR)))


def _fixture_key(value):
    """The already-canonical (SAST fixture day, home key, away key), without aliases."""
    if (not isinstance(value, (list, tuple)) or len(value) != 3
            or any(not isinstance(part, str) or not part for part in value)):
        raise ValueError("invalid canonical fixture identity")
    key = tuple(value)
    datetime.strptime(key[0], "%Y-%m-%d")
    return key


def _acca_fixtures(acca):
    return sorted({_fixture_key(c["fixture"]) for c in acca["legs"]})


def _prior_open_fixture_micro_units(report):
    """Reuse performance()'s settled/pending items, not a second settlement rule.

    A known loss is settled even if other legs lack scores; only profit_units=None
    remains reserved. Historical non-grid stakes are rounded UP for this prior
    reservation, never down, so sub-micro precision cannot create extra budget.
    """
    prior = defaultdict(int)
    for day in report["history"]:
        for acca in day["accas"]:
            if acca["profit_units"] is None:
                stake = _decimal_micro_units(
                    acca["stake_units"], "prior open stake", rounding=ROUND_CEILING
                )
                for fixture in _acca_fixtures(acca):
                    prior[fixture] += stake
    return dict(sorted(prior.items()))


def _fixture_concentration_policy(total_bank_units):
    limit = _fixture_limit_micro_units(total_bank_units)
    return {
        "id": FIXTURE_CONCENTRATION_POLICY,
        "max_fixture_stake_fraction": MAX_FIXTURE_STAKE_FRACTION,
        "denominator": "total_paper_bank_at_decision",
        "fixture_limit_micro_units": limit,
        "fixture_limit_units": limit / MICRO_UNITS,
        "rounding": "floor_to_micro_units",
        "fixture_identity": ["fixture_day", "canonical_home_key", "canonical_away_key"],
        "counting": "full_acca_stake_once_per_distinct_fixture_all_markets_sides_books_contracts_no_netting",
        "prior_exposure_basis": "performance_profit_units_is_none_prior_stakes_ceiling_to_micro_units",
        "projection": "canonical_sorted_fixtures_integer_proportional_downward_only_no_refill",
        "grandfathering": "existing_positions_unchanged_over_cap_prior_leaves_zero_new_budget",
    }


def _normalise_prior_fixtures(prior):
    if not isinstance(prior, dict):
        raise ValueError("invalid prior fixture exposure")  # noqa: TRY004 - evidence validation
    result = {}
    for key, stake in prior.items():
        fixture = _fixture_key(key)
        if fixture in result or type(stake) is not int or stake < 0:
            raise ValueError("invalid prior fixture micro-unit exposure")
        result[fixture] = stake
    return result


def _fixture_exposure_micro_units(accas):
    exposure = defaultdict(int)
    for acca in accas:
        stake = _stake_micro_units(acca["stake_units"])
        for fixture in _acca_fixtures(acca):
            exposure[fixture] += stake
    return exposure


def _exclusivity_priority(acca):
    """Book-neutral priority: largest allocated stake first, canonical tiebreak.

    Allocator order is book-grouped, so first-come-wins would systematically
    favour whichever book happened to be iterated first. Stake descending
    with a leg-signature tiebreak is deterministic for any input ordering.
    """
    stake = acca.get("stake_units")
    stake = stake if type(stake) in (int, float) and math.isfinite(stake) else 0.0
    signature = tuple(sorted(
        str(c.get("candidate_id") or "") for c in acca.get("legs", [])))
    return (-stake, signature)


def _mutually_exclusive_accas(accas):
    """Pairwise fixture-disjoint subset of a publication; highest stake wins.

    Downward-only: an acca sharing any canonical fixture with a kept acca is
    dropped, kept stakes are never changed, and dropped stake is never
    refilled or redistributed. Kept accas are returned in priority order.
    This is a publication-level rule; legs inside one acca were already
    fixture-distinct.
    """
    kept, used, dropped = [], set(), 0
    for acca in sorted(accas, key=_exclusivity_priority):
        fixtures = set(_acca_fixtures(acca))
        if fixtures & used:
            dropped += 1
            continue
        used |= fixtures
        kept.append(acca)
    return kept, dropped


def _require_mutually_exclusive(accas):
    seen = set()
    for acca in accas:
        fixtures = set(_acca_fixtures(acca))
        if fixtures & seen:
            raise ValueError("new ML paper accas are not mutually exclusive by fixture")
        seen |= fixtures


def _concentration_audit(fixtures_by_acca, input_stakes, projected_stakes, published,
                         prior, limit, *, aggregate_scale=1.0):
    affected = defaultdict(list)
    for index, fixtures in enumerate(fixtures_by_acca):
        for fixture in fixtures:
            affected[fixture].append(index)
    final_exposure = _fixture_exposure_micro_units(published)
    entries = []
    for fixture in sorted(set(affected) | set(prior)):
        indices = affected.get(fixture, [])
        before = sum(input_stakes[i] for i in indices)
        projected = sum(projected_stakes[i] for i in indices)
        final = final_exposure.get(fixture, 0)
        reserved = prior.get(fixture, 0)
        residual = max(0, limit - reserved)
        if not before >= projected >= final or final > residual:
            raise ValueError("fixture projection increased stake or exceeded residual budget")
        entries.append({
            "fixture": list(fixture),
            "prior_open_stake_micro_units": reserved,
            "residual_budget_micro_units": residual,
            "input_stake_micro_units": before,
            "fixture_projected_stake_micro_units": projected,
            "published_stake_micro_units": final,
            "total_open_stake_micro_units": reserved + final,
            "idle_budget_micro_units": residual - final,
        })
    before, projected_total = sum(input_stakes), sum(projected_stakes)
    final_total = sum(_stake_micro_units(a["stake_units"]) for a in published)
    return {
        "input_stake_micro_units": before,
        "fixture_projected_stake_micro_units": projected_total,
        "published_stake_micro_units": final_total,
        "released_stake_micro_units": before - final_total,
        "input_acca_count": len(input_stakes),
        "dropped_acca_count": len(input_stakes) - len(published),
        "aggregate_budget_scale": aggregate_scale,
        "fixture_exposures_overlap_not_additive_bank_commitments": True,
        "fixtures": entries,
    }


def project_fixture_stakes(accas, *, total_bank_units, prior_open_fixture_micro_units=None):
    """Conservative post-allocation projection; never re-optimise or redistribute.

    Each canonical fixture scales ALL affected current tickets by the same
    integer floor ratio. Later passes can only decrease earlier exposures.
    Public helper callers opt in explicitly; immutable publication always does.
    """
    limit = _fixture_limit_micro_units(total_bank_units)
    prior = _normalise_prior_fixtures(prior_open_fixture_micro_units or {})
    fixtures_by_acca = [_acca_fixtures(a) for a in accas]
    stakes = [_stake_micro_units(a["stake_units"]) for a in accas]
    affected = defaultdict(list)
    for index, fixtures in enumerate(fixtures_by_acca):
        for fixture in fixtures:
            affected[fixture].append(index)
    for fixture in sorted(affected):
        indices = affected[fixture]
        exposure = sum(stakes[i] for i in indices)
        residual = max(0, limit - prior.get(fixture, 0))
        if exposure > residual:
            for index in indices:
                stakes[index] = stakes[index] * residual // exposure
    projected = list(stakes)
    published = [dict(a, stake_units=stake / MICRO_UNITS)
                 for a, stake in zip(accas, stakes) if stake > 0]
    return published, _concentration_audit(
        fixtures_by_acca, [_stake_micro_units(a["stake_units"]) for a in accas],
        projected, published, prior, limit,
    )


def _scale_aggregate_stakes(accas, audit, *, bank, committed, available):
    """Existing shared 25% headroom, applied AFTER projection, downward only."""
    _nonnegative_finite(available, "free paper bank")
    headroom = _aggregate_headroom_micro_units(bank, committed)
    stakes = [_stake_micro_units(a["stake_units"]) for a in accas]
    total = sum(stakes)
    scale = min(1.0, headroom / total) if total else 1.0
    final_stakes = [stake * headroom // total if total > headroom else stake for stake in stakes]
    if any(final_stakes) and available <= 0:
        raise ValueError("nonzero paper stakes without free capital")
    published = []
    for acca, before, stake in zip(accas, stakes, final_stakes):
        if stake <= 0:
            continue
        if stake > before:
            raise ValueError("aggregate scaling increased a paper stake")
        published.append(dict(
            acca, stake_units=stake / MICRO_UNITS,
            stake_fraction_of_free_bank=stake / MICRO_UNITS / available,
            portfolio_allocation=dict(acca.get("portfolio_allocation", {}),
                                      aggregate_budget_scale=scale),
        ))
    entries = {tuple(e["fixture"]): e for e in audit["fixtures"]}
    final_exposure = _fixture_exposure_micro_units(published)
    fixtures = []
    for fixture, entry in sorted(entries.items()):
        final = final_exposure.get(fixture, 0)
        if final > entry["fixture_projected_stake_micro_units"]:
            raise ValueError("aggregate scaling refilled a fixture")
        fixtures.append(dict(
            entry, published_stake_micro_units=final,
            total_open_stake_micro_units=entry["prior_open_stake_micro_units"] + final,
            idle_budget_micro_units=entry["residual_budget_micro_units"] - final,
        ))
    final_total = sum(stake for stake in final_stakes if stake > 0)
    if final_total > headroom or final_total > _decimal_micro_units(available, "free paper bank"):
        raise ValueError("final paper reservation exceeds capital headroom")
    audit = dict(
        audit, fixtures=fixtures, published_stake_micro_units=final_total,
        released_stake_micro_units=audit["input_stake_micro_units"] - final_total,
        dropped_acca_count=audit["dropped_acca_count"] + len(accas) - len(published),
        aggregate_budget_scale=scale,
    )
    return published, audit


def _size_publication_accas(rows, report, diagnostics):
    """All fresh-production sizing: allocator -> fixture projection -> aggregate."""
    bank, committed = report["paper_bank_units"], report["paper_committed_units"]
    available = max(0.0, report["paper_free_units"])
    concentration = {
        "total_bank_units": bank,
        "prior_open_fixture_micro_units": _prior_open_fixture_micro_units(report),
    }
    if _aggregate_headroom_micro_units(bank, committed) > 0 and available > 0:
        plan = select_accas(rows, available, diagnostics=diagnostics, concentration=concentration)
        audit = diagnostics.pop("fixture_concentration")
    else:
        plan, audit = project_fixture_stakes([], **concentration)
    return _scale_aggregate_stakes(
        plan, audit, bank=bank, committed=committed, available=available
    )


def _attach_concentration_policy(payload, audit):
    payload["policy"] = dict(payload.get("policy") or {},
                             fixture_concentration=_fixture_concentration_policy(
                                 payload["paper_bank_at_decision"]))
    payload["fixture_concentration"] = audit
    return payload


def _concentrate_sealed_draft(payload, history, score_lookup):
    """A pre-policy draft is not frozen evidence: seal only a capped reduction.

    Keep its picks/probabilities/learning and original draft hash. Re-read validated
    prior capital under the caller's lock; never resize any historical receipt.
    """
    captured = parse_zoned_timestamp(payload["captured_at"])
    prior = [r for r in history if r["date"] <= payload["date"]
             and parse_zoned_timestamp(r["captured_at"]) < captured]
    report = performance(prior, score_lookup)
    bank, committed = report["paper_bank_units"], report["paper_committed_units"]
    available = max(0.0, report["paper_free_units"])
    exclusive_accas, exclusivity_dropped = _mutually_exclusive_accas(payload["accas"])
    plan, audit = project_fixture_stakes(
        exclusive_accas, total_bank_units=bank,
        prior_open_fixture_micro_units=_prior_open_fixture_micro_units(report),
    )
    plan, audit = _scale_aggregate_stakes(
        plan, audit, bank=bank, committed=committed, available=available
    )
    payload.update(
        accas=plan, paper_bank_at_decision=bank,
        paper_pending_reserved_at_decision=committed, paper_available_at_decision=available,
        search=dict(payload.get("search") or {},
                    diagnostics_scope="unconstrained_pre_projection_solver_not_published_optimality",
                    published_portfolio_optimality_proven=False,
                    mutual_exclusivity={"rule": "pairwise_fixture_disjoint_highest_stake_first_no_refill",
                                        "dropped_acca_count": exclusivity_dropped}),
    )
    if payload["status"] != "missed_freeze_no_paper_bet":
        payload["status"] = "paper_accas" if plan else "no_paper_bet"
    return _attach_concentration_policy(payload, audit)


def select_accas(rows, available_units=BASE_PAPER_UNITS, *, diagnostics=None,
                 concentration=None):
    """Joint comonotonic-acca sizing, quarter Kelly and downward free-bank flooring.

    ``concentration`` is an explicit replay/helper opt-in containing total bank
    and prior open fixture micro-units. Production sizing ALWAYS supplies it;
    immutable writers independently require the approved policy. The default
    preserves the old helper's unconstrained semantics, not production policy.
    With concentration supplied (production), accas are additionally mutually
    exclusive: pairwise fixture-disjoint, highest allocated stake wins
    (canonical tiebreak), no refill. No leverage, confidence gate or change to the allocator/oracle.
    """
    if concentration is not None:
        if (not isinstance(concentration, dict)
                or set(concentration) != {"total_bank_units", "prior_open_fixture_micro_units"}):
            raise ValueError("invalid fixture concentration inputs")
        _fixture_limit_micro_units(concentration["total_bank_units"])
        _normalise_prior_fixtures(concentration["prior_open_fixture_micro_units"])
    if not math.isfinite(available_units) or available_units <= 0:
        return []
    search = {}
    proposals = acca_proposals(rows, diagnostics=search)
    fractions, allocation = allocate_portfolio(proposals)
    allocation["search_work"] = search
    if diagnostics is not None:
        diagnostics.update(allocation)
    plan = []
    for a, fraction in zip(proposals, fractions):
        stake = math.floor(available_units * fraction * 1e6)
        if stake <= 0:
            continue
        plan.append(
            dict(
                a,
                stake_units=stake / MICRO_UNITS,
                stake_fraction_of_free_bank=fraction,
                portfolio_allocation=allocation,
            )
        )
    if concentration is not None:
        input_count = len(plan)
        plan, exclusivity_dropped = _mutually_exclusive_accas(plan)
        exclusive_count = len(plan)
        plan, audit = project_fixture_stakes(plan, **concentration)
        for acca in plan:
            acca["stake_fraction_of_free_bank"] = acca["stake_units"] / available_units
        if diagnostics is not None:
            diagnostics["mutual_exclusivity"] = {
                "rule": "pairwise_fixture_disjoint_highest_stake_first_no_refill",
                "input_acca_count": input_count,
                "kept_acca_count": exclusive_count,
                "dropped_acca_count": exclusivity_dropped,
            }
            diagnostics["fixture_concentration"] = audit
    return plan


def _publish_receipt(path, payload):
    """The only production decision writer: require policy BEFORE atomic creation.

    _write_once remains a byte-storage primitive for validated historical replay.
    A production caller cannot use that primitive's legacy tolerance to publish
    an undeclared or over-budget new portfolio. Caller holds the lane lock.
    """
    validate_record(payload, payload["date"])
    _validate_concentration_record(payload, required=True)
    _require_mutually_exclusive(payload["accas"])
    return _write_once(path, payload)


def _write_once(path, payload):
    """Atomic publication with no replacement, including concurrent builds."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".ml-paper-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(payload, stream, sort_keys=True, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(name, path)
            _sync_directory(path.parent)
            return True
        except FileExistsError:
            return False
    finally:
        Path(name).unlink(missing_ok=True)


def state_path(root):
    """One lane state file, like Main/ENH; daily files are frozen receipts."""
    return Path(root) / f"{PREFIX}_state.json"


def validate_state(state):
    if state.get("schema") != "autobets_ML_state_v1" or not isinstance(
        state.get("pending_by_date"), dict
    ):
        raise ValueError("invalid ML paper lane state; refusing reset")
    # Retain pending witnesses after freeze deliberately: do not prune merely
    # on date/file existence. Compaction needs verified receipt equivalence.
    if not isinstance(state.get("recoveries", {}), dict):
        raise TypeError("invalid ML pending-state recovery witnesses")
    for sha, proof in state.get("recoveries", {}).items():
        if not isinstance(proof, dict) or not isinstance(sha, str) or len(sha) != 64:
            raise ValueError("invalid ML state recovery proof")
        at = parse_zoned_timestamp(proof.get("recovered_at"))
        day = proof.get("date")
        receipt_sha = proof.get("receipt_sha256")
        if (not isinstance(day, str) or at is None
                or not isinstance(receipt_sha, str) or len(receipt_sha) != 64
                or at.astimezone(LOCAL_TZ).date().isoformat() <= day):
            raise ValueError("invalid ML state recovery proof timestamp")
        datetime.strptime(day, "%Y-%m-%d")
    for day, row in state["pending_by_date"].items():
        datetime.strptime(day, "%Y-%m-%d")
        validate_record(row, day, draft=True)
    return state


def _read_state(root):
    path = state_path(root)
    if not path.exists():
        return {"schema": "autobets_ML_state_v1", "pending_by_date": {}}
    return validate_state(json.loads(path.read_text()))


def _save_state(root, state):
    """Atomic mutable lane state; immutable daily receipts remain separate."""
    validate_state(state)
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".ml-paper-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(state, stream, sort_keys=True, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        _sync_directory(path.parent)
    finally:
        Path(name).unlink(missing_ok=True)


def merge_pending_states(head, cache):
    """Union pre-cutoff evidence, never regress or guess equal-time conflicts."""
    validate_state(head)
    validate_state(cache)
    merged = {"schema": "autobets_ML_state_v1", "pending_by_date": dict(head["pending_by_date"])}
    for day, row in cache["pending_by_date"].items():
        previous = merged["pending_by_date"].get(day)
        if previous is None:
            merged["pending_by_date"][day] = row
        elif previous["sha256"] != row["sha256"]:
            old = parse_zoned_timestamp(previous["draft_persisted_at"])
            new = parse_zoned_timestamp(row["draft_persisted_at"])
            if old == new:
                raise ValueError("conflicting equal-time ML pending cards")
            if parse_zoned_timestamp(previous["captured_at"]) == parse_zoned_timestamp(row["captured_at"]):
                raise ValueError("conflicting equal-capture-time ML pending cards")
            newer, older = (row, previous) if new > old else (previous, row)
            if parse_zoned_timestamp(newer["captured_at"]) < parse_zoned_timestamp(older["captured_at"]):
                raise ValueError("regressing ML pending decision timestamp")
            merged["pending_by_date"][day] = newer
    recoveries = dict(head.get("recoveries") or {})
    for sha, proof in (cache.get("recoveries") or {}).items():
        if sha in recoveries and recoveries[sha] != proof:
            raise ValueError("conflicting ML state recovery witnesses")
        recoveries[sha] = proof
    if recoveries:
        merged["recoveries"] = recoveries
    return merged


def _sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _archive_bytes(root, relative, blob):
    """Durable exact-byte archive; never replace a conflicting witness."""
    path = Path(root) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != blob:
            raise ValueError("paper evidence archive conflict")
        with path.open("rb") as stream:
            os.fsync(stream.fileno())
        _sync_directory(path.parent)
        _sync_directory(Path(root))
        return
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(name, path)
        except FileExistsError:
            if path.read_bytes() != blob:
                raise ValueError("paper evidence archive conflict")
        _sync_directory(path.parent)
        _sync_directory(Path(root))
    finally:
        Path(name).unlink(missing_ok=True)


def _quarantine_state(root, day):
    blob = state_path(root).read_bytes()
    sha = hashlib.sha256(blob).hexdigest()
    relative = f"{PREFIX}_conflicts/draft_{day}.{sha}.bin"
    _archive_bytes(root, relative, blob)
    return {"sha256": sha, "quarantine": relative}


def acknowledged_state_damage(root, blob):
    """Exact corrupt bytes pinned by a valid immutable missed-freeze receipt."""
    sha = hashlib.sha256(blob).hexdigest()
    try:
        history = receipts(root)
    except (ValueError, TypeError, KeyError, AttributeError):
        return None
    for row in history:
        proof = row.get("draft_integrity_error") or {}
        relative = f"{PREFIX}_conflicts/draft_{row['date']}.{sha}.bin"
        if (row["status"] == "missed_freeze_no_paper_bet"
                and proof == {"sha256": sha, "quarantine": relative}
                and (Path(root) / relative).is_file()
                and (Path(root) / relative).read_bytes() == blob):
            return row
    return None


def state_recovery_acknowledges(root, state, blob):
    """Restore may accept a repaired pending store, never a reset bank/history."""
    validate_state(state)
    sealed = acknowledged_state_damage(root, blob)
    if sealed is None:
        return False
    sha = hashlib.sha256(blob).hexdigest()
    proof = (state.get("recoveries") or {}).get(sha) or {}
    at = parse_zoned_timestamp(proof.get("recovered_at"))
    return (proof.get("receipt_sha256") == sealed["sha256"]
            and proof.get("date") == sealed["date"] and at is not None
            and at.astimezone(LOCAL_TZ).date().isoformat() > sealed["date"]
            and all(day > sealed["date"] for day in state["pending_by_date"]))


def _recover_acknowledged_state(root, day, at):
    try:
        _read_state(root)
        return
    except (ValueError, TypeError, KeyError, AttributeError):
        blob = state_path(root).read_bytes()
    sealed = acknowledged_state_damage(root, blob)
    if sealed is None or sealed["date"] >= day:
        return  # Today stays no-bet; recovery can only affect later dates.
    sha = hashlib.sha256(blob).hexdigest()
    state = {"schema": "autobets_ML_state_v1", "pending_by_date": {}, "recoveries": {
        sha: {"date": sealed["date"], "receipt_sha256": sealed["sha256"],
              "recovered_at": at.isoformat()}}}
    _save_state(root, state)
    print(f"autobets_ML pending-state recovery: {sha}; exact bytes quarantined; "
          "frozen history and paper capital unchanged")


def _migrate_legacy_drafts(root):
    """Migrate pending evidence; archive obsolete drafts only after a valid freeze.

    No fresh decisions/timestamps are manufactured. Frozen daily receipts
    supersede pending rows; exact legacy bytes are archived before unlinking.
    Unfrozen conflicts and failed writes still fail closed with originals kept.
    """
    pending = []
    for path in sorted(Path(root).glob(f"{PREFIX}_draft_????-??-??.json")):
        day = path.stem.removeprefix(f"{PREFIX}_draft_")
        frozen = receipt_path(root, day)
        if frozen.exists():
            validate_record(json.loads(frozen.read_text()), day)
            blob = path.read_bytes()
            sha = hashlib.sha256(blob).hexdigest()
            _archive_bytes(root, f"{PREFIX}_conflicts/legacy_superseded_{day}.{sha}.bin", blob)
            path.unlink()
        else:
            pending.append((path, day))
    if not pending:
        return
    state = _read_state(root)
    for path, day in pending:
        row = json.loads(path.read_text())
        validate_record(row, day, draft=True)
        state = merge_pending_states(
            state, {"schema": "autobets_ML_state_v1", "pending_by_date": {day: row}}
        )
    _save_state(root, state)
    for path, _ in pending:
        path.unlink()


def _checked_draft(root, day, freeze_at):
    row = _read_state(root)["pending_by_date"].get(day)
    if row is None:
        return None
    captured = parse_zoned_timestamp(row.get("captured_at"))
    persisted = parse_zoned_timestamp(row.get("draft_persisted_at"))
    if (
        row.get("schema") not in READABLE_SCHEMAS
        or row.get("date") != day
        or row.get("sha256") != digest({k: v for k, v in row.items() if k != "sha256"})
        or captured is None
        or persisted is None
        or not captured <= persisted < freeze_at
        or row.get("freeze_at") != freeze_at.isoformat()
    ):
        raise ValueError("invalid or post-cutoff ML paper draft; refusing backfill")
    validate_record(row, day, draft=True)
    return row


def capture(
    context,
    *,
    root,
    score_lookup,
    kickoff_fn,
    source_guard,
    min_leg_odds=1.0,
    generate_hour=6,
    freeze_hour=9,
    now=None,
    index=None,
):
    """06:00 drafts / first eligible run at or after 09:00 freezes (SAST).

    Like Main/ENH, an unfrozen day may select from current eligible inputs at
    actual runtime after 09:00. Never backdate that decision or revise a frozen
    card. Legacy saved drafts can still be sealed when fresh context is absent;
    missing context AND missing prior evidence remains an explicit no-bet.
    No live plan/state/bank is read, compared or modified.
    """
    clock = (lambda: now) if now is not None else (lambda: datetime.now(UTC))
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    # Integrity conflicts block PAPER only, including its no-history startup.
    receipts(root)
    # One lock for draft updates AND first freeze prevents races across cutoff.
    with (root / f".{PREFIX}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _migrate_frozen_receipts(root)
        current = clock()
        if current.astimezone(LOCAL_TZ).hour < generate_hour:
            return None
        day = current.astimezone(LOCAL_TZ).date().isoformat()
        freeze_at = datetime.fromisoformat(day).replace(tzinfo=LOCAL_TZ, hour=freeze_hour)
        path = receipt_path(root, day)
        if path.exists():
            receipts(root)  # corrupted frozen evidence is never silently ignored
            _migrate_legacy_drafts(root)
            return None

        def seal(at):
            corruption = None
            try:
                draft = _checked_draft(root, day, freeze_at)
            except (ValueError, TypeError, KeyError, AttributeError):
                # Preserve original bytes and an explicit missed-day receipt;
                # never delete/rebuild the corrupt draft or select late inputs.
                corruption = _quarantine_state(root, day)
                draft = None
            if draft is None:
                payload = {
                    "schema": SCHEMA,
                    "date": day,
                    "captured_at": at.isoformat(),
                    "freeze_at": freeze_at.isoformat(),
                    "mode": "paper_only_no_real_stakes",
                    "status": "missed_freeze_no_paper_bet",
                    "candidates": [],
                    "models": {},
                    "learning": {"status": "missed_freeze_no_late_training"},
                    "accas": [],
                    "rejections": {"no_pre_cutoff_draft": 1},
                }
            else:
                payload = {k: v for k, v in draft.items() if k != "sha256"}
                payload["draft_sha256"] = draft["sha256"]
                payload["status"] = "paper_accas" if draft["accas"] else "no_paper_bet"
            if corruption is not None:
                payload["draft_integrity_error"] = corruption
                payload["rejections"] = {"corrupt_pre_cutoff_draft": 1}
            history = receipts(root)
            payload_captured = parse_zoned_timestamp(payload.get("captured_at"))
            # A sealed draft is a backdated receipt: history is ordered by
            # captured_at (legacy rows sort first on ties), so any rolling
            # publication captured at or after the draft was necessarily
            # written without this receipt in its prior_receipt_sha256s.
            # Publishing now would ignore those intervening commitments in
            # the aggregate/fixture budgets and fork the rolling chain,
            # making the whole history unreadable. Fail closed instead:
            # publish nothing, preserve the draft and every frozen receipt,
            # and let later publications account for the true history.
            intervening_rolling = [
                row for row in history
                if row.get("freeze_basis") == ROLLING_FREEZE
                and (
                    payload_captured is None
                    or parse_zoned_timestamp(row["captured_at"]) >= payload_captured
                )
            ]
            if intervening_rolling:
                print(
                    f"autobets_ML stale pre-cutoff draft not sealed: {day} "
                    f"superseded by {len(intervening_rolling)} intervening "
                    "rolling publication(s); draft preserved, no backdated "
                    "receipt published"
                )
                return None
            payload = _concentrate_sealed_draft(payload, history, score_lookup)
            payload["persisted_at"] = at.isoformat()
            payload["sha256"] = digest(payload)
            return payload if _publish_receipt(path, payload) else None

        _recover_acknowledged_state(root, day, current)
        try:
            _read_state(root)
        except (ValueError, TypeError, KeyError, AttributeError):
            _quarantine_state(root, day)
            if current < freeze_at:
                # Never publish/backdate a freeze before 09:00. Preserve the
                # damaged store, visibly quarantine now, seal NO BET at cutoff.
                print(f"autobets_ML corrupt pending state: {day} quarantined; "
                      "no build; awaiting 09:00 missed-freeze publication")
                return None
            return seal(current)
        _migrate_legacy_drafts(root)
        captured = parse_zoned_timestamp(context.get("build_at"))
        if (
            context.get("date") != day
            or captured is None
            or not timedelta(0) <= current - captured <= timedelta(minutes=5)
            or not isinstance(context.get("slate"), list)
        ):
            return seal(current) if current >= freeze_at else None
        if current >= freeze_at:
            captured = current  # actual first-freeze decision, never 09:00 backdating
        history = receipts(root)
        quotes = index if index is not None else load_prices_index(root.parent, day)
        rows, models, rejected = candidates(
            context["slate"],
            day,
            captured,
            quotes,
            kickoff_fn=kickoff_fn,
            source_guard=source_guard,
            min_leg_odds=min_leg_odds,
            freeze_at=freeze_at,
        )
        learner = learn(history, captured, score_lookup)
        apply_learning(rows, learner)
        # Neither training nor stake capital may use future-dated receipts.
        prior = [
            r
            for r in history
            if r["date"] <= day and parse_zoned_timestamp(r["captured_at"]) < captured
        ]
        report = performance(prior, score_lookup)
        available = max(0.0, report["paper_free_units"])
        search_diagnostics = {}
        plan, concentration_audit = _size_publication_accas(rows, report, search_diagnostics)
        persisted = clock()
        if persisted.astimezone(LOCAL_TZ).date().isoformat() != day or persisted < captured:
            return None  # no cross-day/backdated publication
        previous = _checked_draft(root, day, freeze_at)
        if (persisted < freeze_at and previous
                and parse_zoned_timestamp(previous["captured_at"]) >= captured):
            return None
        payload = {
            "schema": SCHEMA,
            "date": day,
            "captured_at": captured.isoformat(),
            "draft_persisted_at": persisted.isoformat(),
            "freeze_at": freeze_at.isoformat(),
            "mode": "paper_only_no_real_stakes",
            "status": "draft_not_yet_frozen",
            "policy": {
                "quote_max_age_hours": QUOTE_MAX_AGE.total_seconds() / 3600,
                "quote_age_basis": "later_of_decision_and_scheduled_freeze_original_capture",
                "stricter_source_limits_retained": True,
                "odds_band": None,
                "max_accas": None,
                "max_legs": None,
                "minimum_legs": 2,
                "search_beam_width": SEARCH_BEAM_WIDTH,
                "staking": "joint_worst_case_dependence_portfolio_quarter_Kelly",
                "kelly_multiplier": KELLY_MULTIPLIER,
                "max_free_bank_exposure": MAX_PAPER_EXPOSURE,
                "cross_acca_team_reuse": True,
                "method": "existing_form_forecast_score_ml_plus_prior_paper_error_calibration",
                "objective": "robust_estimated_log_bank_growth_not_a_profit_guarantee",
            },
            "paper_available_at_decision": available,
            "paper_bank_at_decision": report["paper_bank_units"],
            "paper_pending_reserved_at_decision": report["paper_committed_units"],
            "candidates": rows,
            "models": models,
            "learning": learner,
            "coverage": {
                "slate_rows": len(context["slate"]),
                "candidate_count": len(rows),
                "candidate_fixtures": len({tuple(c["fixture"]) for c in rows}),
                "status": "inputs_available" if rows else "input_starved_not_strategy_selectivity",
            },
            "rejections": rejected,
            "search": search_diagnostics,
            "accas": plan,
        }
        _attach_concentration_policy(payload, concentration_audit)

        def freeze_current(at):
            if at < captured or at.astimezone(LOCAL_TZ).date().isoformat() != day:
                return None
            # Do not carry a quote/kickoff across expiry during a slow build.
            # Probabilities/learning remain bound to the original decision;
            # only remove ineligible quotes and resize the own-paper portfolio.
            eligible = [c for c in rows
                        if at - parse_zoned_timestamp(c["price_at"])
                        <= _quote_max_age(c["price_source"])
                        and parse_zoned_timestamp(c["kickoff_utc"]) >= at + MIN_LEAD]
            final_plan, final_audit = plan, concentration_audit
            if len(eligible) != len(rows):
                rejected["quote_or_kickoff_expired_during_build"] = len(rows) - len(eligible)
                final_plan, final_audit = _size_publication_accas(
                    eligible, report, search_diagnostics
                )
            for c in eligible:
                c["price_age_seconds_at_freeze"] = (
                    at - parse_zoned_timestamp(c["price_at"])
                ).total_seconds()
            frozen = {k: v for k, v in payload.items()
                      if k not in {"sha256", "draft_persisted_at"}}
            frozen.update(
                status="paper_accas" if final_plan else "no_paper_bet",
                candidates=eligible,
                accas=final_plan,
                fixture_concentration=final_audit,
                coverage=dict(payload["coverage"], candidate_count=len(eligible),
                              candidate_fixtures=len({tuple(c["fixture"]) for c in eligible}),
                              status="inputs_available" if eligible
                              else "input_starved_not_strategy_selectivity"),
                freeze_basis=ACTUAL_RUN_FREEZE,
                frozen_at=at.isoformat(),
                persisted_at=at.isoformat(),
            )
            frozen["sha256"] = digest(frozen)
            return frozen if _publish_receipt(path, frozen) else None

        if persisted >= freeze_at:
            return freeze_current(persisted)
        payload["sha256"] = digest(payload)
        # Like the other lanes: pending cards live in one mutable lane state,
        # not separate dated draft files. Keep earlier dates' exact evidence.
        state = _read_state(root)
        state["pending_by_date"][day] = payload
        fd, name = tempfile.mkstemp(dir=root, prefix=".ml-paper-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(state, stream, sort_keys=True, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            # A build crossing 09:00 becomes an actual-time frozen card,
            # never a post-cutoff draft or a backdated pre-cutoff receipt.
            durable_at = clock()
            if durable_at >= freeze_at:
                return freeze_current(durable_at)
            os.replace(name, state_path(root))
        finally:
            Path(name).unlink(missing_ok=True)
        return payload


def rolling_receipt_path(root, receipt):
    """One immutable decision per publication, inside the existing internal store."""
    captured = parse_zoned_timestamp(receipt.get("captured_at"))
    if captured is None:
        raise ValueError("missing rolling decision timestamp")
    identity = captured.astimezone(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    if receipt.get("decision_id") != identity:
        raise ValueError("invalid rolling decision identity")
    return receipt_path(root, receipt["date"]).with_name(
        f"{PREFIX}_{receipt['date']}_{identity}.json")


def _validate_rolling_record(row, captured):
    published = parse_zoned_timestamp(row.get("persisted_at"))
    end = parse_zoned_timestamp(row.get("window_end"))
    if (published is None or published < captured
            or published.astimezone(LOCAL_TZ).date().isoformat() != row["date"]
            or parse_zoned_timestamp(row.get("frozen_at")) != published
            or parse_zoned_timestamp(row.get("freeze_at")) != published
            or parse_zoned_timestamp(row.get("window_start")) != captured
            or end != captured + timedelta(hours=24)
            or row.get("status") not in ("paper_accas", "no_paper_bet")
            or row.get("draft_sha256") is not None
            or row.get("draft_persisted_at") is not None):
        raise ValueError("invalid rolling paper freeze")
    rolling_receipt_path(Path("."), row)
    bank, committed = row.get("paper_bank_at_decision"), row.get("paper_pending_reserved_at_decision")
    if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in (bank, committed)):
        raise ValueError("invalid rolling paper capital")
    if not math.isclose(row["paper_available_at_decision"], max(0, bank - committed), abs_tol=1e-9):
        raise ValueError("rolling free capital disagrees with commitments")
    if sum(a["stake_units"] for a in row["accas"]) > max(0, bank * MAX_PAPER_EXPOSURE - committed) + 1e-6:
        raise ValueError("rolling aggregate exposure exceeded")
    for c in row["candidates"]:
        kickoff = parse_zoned_timestamp(c.get("kickoff_utc"))
        quote = parse_zoned_timestamp(c.get("price_at"))
        model = row["models"].get(c.get("model_key"), {})
        if (kickoff is None or quote is None or not quote <= captured <= published
                or not published + MIN_LEAD <= kickoff <= end
                or published - quote > _quote_max_age(c.get("price_source"))
                or kickoff.astimezone(UTC).date() != kickoff.astimezone(LOCAL_TZ).date()
                or c["date"] != kickoff.astimezone(LOCAL_TZ).date().isoformat()
                or c["fixture"] != [c["date"], source_team_key(c["home"]), source_team_key(c["away"])]
                or not model.get("train_last_date", "9999") < row["date"]):
            raise ValueError("rolling candidate timing/model evidence invalid")


def capture_rolling(context, *, root, score_lookup, kickoff_fn, source_guard,
                    min_leg_odds=1.0, now=None, index=None):
    """Next-24h PAPER decisions at every existing run; no daily clock gate.

    Never edits old receipts, spends live capital, or invents future inputs.
    Quarter-Kelly remains unchanged; remaining aggregate commitment headroom
    can only reduce a new allocation. Pending fixtures may reuse residual budget;
    settled fixtures never re-enter.
    """
    clock = (lambda: now) if now is not None else (lambda: datetime.now(UTC))
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    with (root / f".{PREFIX}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _migrate_frozen_receipts(root)
        captured = clock()
        day = captured.astimezone(LOCAL_TZ).date().isoformat()
        _recover_acknowledged_state(root, day, captured)
        _read_state(root)  # corruption is not permission to restart paper capital
        _migrate_legacy_drafts(root)
        built = parse_zoned_timestamp(context.get("build_at"))
        if (built is None or not timedelta(0) <= captured - built <= timedelta(minutes=5)
                or not isinstance(context.get("slate"), list)):
            return None  # missing context never seals a fictitious daily NO BET
        history = receipts(root)
        if any(parse_zoned_timestamp(r["persisted_at"]) > captured for r in history):
            raise ValueError("future paper evidence cannot fund a rolling decision")
        report = performance(history, score_lookup)
        prior_open = _prior_open_fixture_micro_units(report)
        fixture_limit = _fixture_limit_micro_units(report["paper_bank_units"])
        # Never reopen settled evidence (including an acca already lost with
        # unresolved other legs). Pending fixtures may reuse residual budget.
        settled = {tuple(c["fixture"]) for r in report["history"] for a in r["accas"]
                   if a["profit_units"] is not None for c in a["legs"]}
        end = captured + timedelta(hours=24)
        eligible = defaultdict(list)
        rejected = Counter()
        for row in context["slate"]:
            kickoff = kickoff_fn(row) if isinstance(row, dict) else None
            if kickoff is None or not captured + MIN_LEAD <= kickoff <= end:
                rejected["outside_rolling_window_or_unproven_kickoff"] += 1
                continue
            fixture_day = kickoff.astimezone(LOCAL_TZ).date().isoformat()
            fixture = (fixture_day, source_team_key(row.get("home")), source_team_key(row.get("away")))
            if fixture in settled:
                rejected["previously_settled_fixture"] += 1
                continue
            if prior_open.get(fixture, 0) >= fixture_limit:
                rejected["fixture_budget_exhausted"] += 1
                continue
            profile = row.get("statistical_profile")
            model = profile.get("ml_model") if isinstance(profile, dict) else None
            last_train = model.get("train_last_date") if isinstance(model, dict) else None
            if (row.get("date") != fixture_day or not isinstance(last_train, str)
                    or not last_train < day):
                rejected["fixture_date_or_prior_model_unproven"] += 1
                continue
            eligible[fixture_day].append(row)
        rows, models = [], {}
        for fixture_day, slate in sorted(eligible.items()):
            quotes = index if index is not None else load_prices_index(root.parent, fixture_day)
            found, bound_models, failures = candidates(
                slate, fixture_day, captured, quotes, kickoff_fn=kickoff_fn,
                source_guard=source_guard, min_leg_odds=min_leg_odds, freeze_at=captured, rolling=True)
            rows.extend(found)
            models.update(bound_models)
            rejected.update(failures)
        learner = learn(history, captured, score_lookup)
        apply_learning(rows, learner)
        available = max(0.0, report["paper_free_units"])
        if not rows and history:
            return None  # no new eligible opportunity, not another daily seal
        search = {}
        # Timestamp AFTER search/sizing and recheck every guard at publication.
        # If a slow search crosses expiry, rebuild only the surviving candidates.
        for _ in range(3):
            plan, concentration_audit = _size_publication_accas(rows, report, search)
            persisted = clock()
            if persisted < captured or persisted.astimezone(LOCAL_TZ).date().isoformat() != day:
                return None
            final_rows = [c for c in rows
                          if persisted - parse_zoned_timestamp(c["price_at"]) <= _quote_max_age(c["price_source"])
                          and persisted + MIN_LEAD <= parse_zoned_timestamp(c["kickoff_utc"]) <= end]
            if len(final_rows) == len(rows):
                break
            rejected["quote_or_kickoff_expired_during_build"] += len(rows) - len(final_rows)
            rows = final_rows
        else:
            return None  # continuously expiring inputs are not publishable
        snapshot = digest({
            "date": day, "candidates": [{k: v for k, v in c.items()
                if not k.startswith("price_age_seconds_")} for c in rows],
            "learning": learner, "bank": report["paper_bank_units"],
            "committed": report["paper_committed_units"], "rejections": dict(rejected),
            # Policy/prior exposure participate in deduplication identity. Equal
            # bank totals do not imply equal per-fixture residual budgets.
            "fixture_concentration": {
                "policy": _fixture_concentration_policy(report["paper_bank_units"]),
                "prior_open_fixture_micro_units": [
                    [e["fixture"], e["prior_open_stake_micro_units"]]
                    for e in concentration_audit["fixtures"]
                    if e["prior_open_stake_micro_units"]
                ],
            },
        })
        if any(r.get("snapshot_sha256") == snapshot for r in history):
            return None
        for c in rows:
            c["price_age_seconds_at_freeze"] = (persisted - parse_zoned_timestamp(c["price_at"])).total_seconds()
        receipt = {
            "schema": SCHEMA, "date": day, "mode": "paper_only_no_real_stakes",
            "decision_id": captured.astimezone(UTC).strftime("%Y%m%dT%H%M%S%fZ"),
            "captured_at": captured.isoformat(), "persisted_at": persisted.isoformat(),
            "frozen_at": persisted.isoformat(), "freeze_at": persisted.isoformat(),
            "freeze_basis": ROLLING_FREEZE, "window_start": captured.isoformat(), "window_end": end.isoformat(),
            "prior_receipt_sha256s": [r["sha256"] for r in history],
            "snapshot_sha256": snapshot, "status": "paper_accas" if plan else "no_paper_bet",
            "paper_available_at_decision": available, "paper_bank_at_decision": report["paper_bank_units"],
            "paper_pending_reserved_at_decision": report["paper_committed_units"],
            "candidates": rows, "models": models, "learning": learner, "accas": plan,
            "fixture_concentration": concentration_audit,
            "search": search, "rejections": dict(rejected),
            "coverage": {"candidate_count": len(rows), "candidate_fixtures": len({tuple(c["fixture"]) for c in rows}),
                         "slate_rows": len(context["slate"]), "status": "inputs_available" if rows else "input_starved_not_strategy_selectivity"},
            "policy": {"window_hours": 24, "kelly_multiplier": KELLY_MULTIPLIER,
                       "max_aggregate_bank_exposure": MAX_PAPER_EXPOSURE, "odds_band": None,
                       "quote_max_age_hours": QUOTE_MAX_AGE.total_seconds() / 3600,
                       "stricter_source_limits_retained": True, "minimum_legs": 2,
                       "probability_basis": "product_assumes_cross_fixture_independence_not_validated",
                       "fixture_concentration": _fixture_concentration_policy(
                           report["paper_bank_units"])},
        }
        receipt["sha256"] = digest(receipt)
        return receipt if _publish_receipt(rolling_receipt_path(root, receipt), receipt) else None


def source_forecast_probability(candidate):
    """Market/side-matched frozen source aggregate, not odds or a calibrated truth.

    Complements are valid for binary FT markets; double chance sums the two
    named 1X2 outcomes. Unsupported markets, invalid values and missing inputs
    stay unavailable. Never substitute another market's confidence or xG.
    """
    inputs = candidate.get("ml_inputs")
    values = inputs.get("values") if isinstance(inputs, dict) else None
    if not isinstance(values, dict):
        return None

    def value(key):
        p = values.get(key)
        return p if type(p) in (int, float) and math.isfinite(p) and 0 <= p <= 1 else None

    market, side = candidate.get("market"), candidate.get("selection")
    if market == "1x2" and side in ("home", "draw", "away"):
        return value(f"forecast_1x2_{side}_mean")
    if market == "double_chance":
        sides = {"home": ("home", "draw"), "1x": ("home", "draw"),
                 "away": ("away", "draw"), "x2": ("away", "draw"),
                 "draw": ("home", "away"), "12": ("home", "away")}.get(side)
        if sides is None:
            return None
        parts = [value(f"forecast_1x2_{s}_mean") for s in sides]
        return sum(parts) if all(p is not None for p in parts) and sum(parts) <= 1 else None
    if market in ("btts_yes", "btts_no") and side == market.removeprefix("btts_"):
        p = value("forecast_btts_yes_mean")
        return (p if side == "yes" else 1 - p) if p is not None else None
    for line in ("1.5", "2.5", "3.5", "4.5"):
        for outcome in ("over", "under"):
            if market == f"match_{outcome}_{line.replace('.', '')}" and side == outcome:
                p = value(f"forecast_ou_{line}_over_mean")
                return (p if side == "over" else 1 - p) if p is not None else None
    return None


def quote_age_at_decision(candidate, receipt):
    """Original quote age at original decision, never age at report refresh."""
    quoted = parse_zoned_timestamp(candidate.get("price_at"))
    decision = parse_zoned_timestamp(receipt.get("captured_at"))
    if quoted is None or decision is None or quoted > decision:
        return None
    return (decision - quoted).total_seconds()


def _paired_source_stats(records):
    """Descriptive, fixture-weighted paired errors; no tuning or significance claim."""
    paired = [r for r in records if r["source"] is not None]
    missing = [r for r in records if r["source"] is None]
    counts = Counter(r["fixture"] for r in paired)
    stats = {
        "paired_fixtures": len(counts),
        "paired_observations": len(paired),
        "missing_source_fixtures": len({r["fixture"] for r in missing}),
        "missing_source_observations": len(missing),
    }
    for field in ("base", "model", "source"):
        brier = logloss = 0.0
        for r in paired:
            p = r[field]
            clipped = min(1 - 1e-12, max(1e-12, p))
            weight = 1 / counts[r["fixture"]]
            brier += weight * (p - r["hit"]) ** 2
            logloss -= weight * (r["hit"] * math.log(clipped)
                                 + (1 - r["hit"]) * math.log1p(-clipped))
        stats[f"{field}_brier"] = brier / len(counts) if counts else None
        stats[f"{field}_logloss"] = logloss / len(counts) if counts else None
    return stats


def _source_comparisons(records):
    bands = {"lt_10pp": [], "10_to_lt_20pp": [], "ge_20pp": [], "unavailable": []}
    buckets = defaultdict(list)
    for r in records:
        # Rounding only stabilises display-band boundaries, never model outputs.
        gap = round(abs(r["model"] - r["source"]) * 100, 10) if r["source"] is not None else None
        band = ("unavailable" if gap is None else "lt_10pp" if gap < 10
                else "10_to_lt_20pp" if gap < 20 else "ge_20pp")
        bands[band].append(r)
        for bucket in r["buckets"]:
            buckets[bucket].append(r)
    return {
        "basis": "frozen_market_matched_source_forecasts_not_independent_ground_truth",
        "weighting": "one_total_weight_per_fixture_within_each_group",
        "limitation": "descriptive_only_overlapping_groups_not_additive_no_significance_or_rule_changes",
        "all_candidates": _paired_source_stats(records),
        "selected_candidates": _paired_source_stats([r for r in records if r["selected"]]),
        "by_model_source_gap": {k: _paired_source_stats(v) for k, v in bands.items()},
        "by_board_bucket": {k: _paired_source_stats(v) for k, v in sorted(buckets.items())},
    }


def calibration_diagnostics(history, score_lookup):
    """Paired prequential errors of frozen base vs calibrated probabilities.

    Includes unbet candidates. Repeated books/buckets do not manufacture more
    independent fixtures: each fixture contributes total weight one per day.
    Not a significance test; unresolved records stay absent and counts explicit.
    """
    samples = {}
    comparisons = {}
    for receipt in history:
        selected = {c["candidate_id"] for a in receipt["accas"] for c in a["legs"]}
        for c in receipt["candidates"]:
            score = score_lookup(c)
            y = hit(c["market"], c["selection"], *score) if score is not None else None
            if y is None:
                continue
            key = (
                tuple(c["fixture"]),
                c["market"],
                c["selection"],
                c.get("model_key"),
                c.get("base_probability", c["probability"]),
                c["probability"],
            )
            record = samples.setdefault(
                key,
                {
                    "fixture": tuple(c["fixture"]),
                    "base": c.get("base_probability", c["probability"]),
                    "calibrated": c["probability"],
                    "hit": int(y),
                    "selected": False,
                },
            )
            record["selected"] |= c["candidate_id"] in selected
            source = source_forecast_probability(c)
            comparison_key = (*key, source)
            comparison = comparisons.setdefault(comparison_key, {
                "fixture": tuple(c["fixture"]),
                "base": c.get("base_probability", c["probability"]),
                "model": c["probability"],
                "source": source,
                "buckets": set(),
                "hit": int(y),
                "selected": False,
            })
            comparison["buckets"].add(c["bucket"])
            comparison["selected"] |= c["candidate_id"] in selected
    groups = {}
    for name, values in (
        ("all_candidates", list(samples.values())),
        ("selected_candidates", [r for r in samples.values() if r["selected"]]),
    ):
        counts = Counter(r["fixture"] for r in values)
        stats = {"resolved_fixtures": len(counts), "resolved_observations": len(values)}
        for field in ("base", "calibrated"):
            brier = logloss = 0.0
            for r in values:
                p = min(1 - 1e-12, max(1e-12, r[field]))
                weight = 1 / counts[r["fixture"]]
                brier += weight * (p - r["hit"]) ** 2
                logloss -= weight * (r["hit"] * math.log(p) + (1 - r["hit"]) * math.log1p(-p))
            stats[field + "_brier"] = brier / len(counts) if counts else None
            stats[field + "_logloss"] = logloss / len(counts) if counts else None
        groups[name] = stats
    groups["source_comparison"] = _source_comparisons(list(comparisons.values()))
    return groups


def performance(history, score_lookup):
    """Own acca/unit ROI, drawdown, Brier error and market/bucket diagnostics.

    Exact regulation outcomes only. Missing/ambiguous scores stay pending.
    A known losing leg settles a loss; otherwise all legs must resolve. Frozen
    model-chosen stakes are PAPER accounting, never a live bank. Group figures are LEG diagnostics,
    not acca ROI and not summed across overlapping bucket/market categories.
    """
    days, accas, groups = [], [], defaultdict(lambda: {"settled": 0, "wins": 0, "profit": 0.0})
    brier = []
    seen_legs = set()
    acca_calibration = defaultdict(lambda: {"resolved": 0, "wins": 0, "predicted_wins": 0.0})
    unresolved_legs = 0
    equity = peak = drawdown = drawdown_fraction = 0.0
    day_marks = defaultdict(float)
    for receipt in history:
        _validate_bets(receipt)
        daily = []
        for acca in receipt["accas"]:
            outcomes = []
            for c in acca["legs"]:
                score = score_lookup(c)
                y = hit(c["market"], c["selection"], *score) if score is not None else None
                outcomes.append(y)
                unique_leg = (receipt["date"], c["candidate_id"])
                fresh_leg = unique_leg not in seen_legs
                seen_legs.add(unique_leg)
                unresolved_legs += fresh_leg and y is None
                if y is not None and fresh_leg:
                    brier.append((c["probability"] - int(y)) ** 2)
                    for group in (f"bucket:{c['bucket']}", f"market:{c['market']}"):
                        g = groups[group]
                        g["settled"] += 1
                        g["wins"] += int(y)
                        g["profit"] += c["odds"] - 1 if y else -1
            settled = False in outcomes or all(y is not None for y in outcomes)
            stake = acca["stake_units"]
            if not math.isfinite(stake) or stake <= 0:
                raise ValueError("invalid frozen paper stake")
            profit = (
                stake * (acca["odds"] - 1)
                if settled and all(outcomes)
                else -stake
                if settled
                else None
            )
            item = {
                "odds": acca["odds"],
                "stake_units": stake,
                "leg_outcomes": outcomes,
                "status": "pending" if not settled else "win" if all(outcomes) else "loss",
                "profit_units": profit,
                "legs": acca["legs"],
            }
            accas.append(item)
            daily.append(item)
            if all(y is not None for y in outcomes):
                group = acca_calibration[str(len(outcomes))]
                group["resolved"] += 1
                group["wins"] += int(all(outcomes))
                group["predicted_wins"] += acca.get(
                    "probability_estimate", math.prod(c["probability"] for c in acca["legs"])
                )
        # Ticket-date marks of latest known results; pending stakes held at
        # cost. Never omit a known loss just because another acca is pending.
        # This is NOT observed settlement-time or intraday drawdown.
        if daily:
            day_marks[receipt["date"]] += sum(a["profit_units"] for a in daily if a["profit_units"] is not None)
        days.append(
            {
                "date": receipt["date"],
                "status": receipt["status"],
                "accas": daily,
                "learning_status": receipt["learning"]["status"],
                **({"decision_id": receipt["decision_id"], "captured_at": receipt["captured_at"],
                    "frozen_at": receipt["frozen_at"]} if receipt.get("freeze_basis") == ROLLING_FREEZE else {}),
            }
        )
    for day in sorted(day_marks):
        equity += day_marks[day]
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
        drawdown_fraction = max(drawdown_fraction, (peak - equity) / (BASE_PAPER_UNITS + peak))
    graded = [a for a in accas if a["profit_units"] is not None]
    profit = sum(a["profit_units"] for a in graded)
    staked = sum(a["stake_units"] for a in graded)
    committed = sum(a["stake_units"] for a in accas if a["profit_units"] is None)
    return {
        "lane": "autobets_ML",
        "paper_only": True,
        "unit": "model_chosen_paper_stakes_compounding_own_bank",
        "base_paper_units": BASE_PAPER_UNITS,
        "paper_bank_units": BASE_PAPER_UNITS + profit,
        "paper_multiple": (BASE_PAPER_UNITS + profit) / BASE_PAPER_UNITS,
        "paper_committed_units": committed,
        "paper_free_units": BASE_PAPER_UNITS + profit - committed,
        "settled_stake_units": staked,
        "receipt_days": len({r["date"] for r in history}),
        "decision_receipts": len(history),
        "bet_days": len({r["date"] for r in history if r["accas"]}),
        "no_bet_days": len({r["date"] for r in history} - {r["date"] for r in history if r["accas"]}),
        "missed_freeze_days": sum(r["status"] == "missed_freeze_no_paper_bet" for r in history),
        "settled_accas": len(graded),
        "wins": sum(a["status"] == "win" for a in graded),
        "losses": sum(a["status"] == "loss" for a in graded),
        "hit_rate": sum(a["status"] == "win" for a in graded) / len(graded) if graded else None,
        "pending_accas": len(accas) - len(graded),
        "unresolved_result_legs": unresolved_legs,
        "resolved_result_legs": len(brier),
        "profit_units": profit,
        "roi": profit / staked if staked else None,
        "max_daily_close_drawdown_units": drawdown,
        "max_daily_close_drawdown_fraction": drawdown_fraction,
        "drawdown_basis": "ticket_date_latest_known_result_marks_pending_at_cost_not_settlement_timeline",
        "drawdown_has_pending_results": unresolved_legs > 0,
        "selected_leg_brier_score": sum(brier) / len(brier) if brier else None,
        "calibration": calibration_diagnostics(history, score_lookup),
        "acca_calibration_by_length": dict(acca_calibration),
        "current_risk_policy": {
            "schema": SCHEMA,
            "kelly_multiplier": KELLY_MULTIPLIER,
            "max_free_bank_exposure": MAX_PAPER_EXPOSURE,
            "max_aggregate_bank_exposure_for_rolling": MAX_PAPER_EXPOSURE,
            "max_new_fixture_stake_fraction_of_total_bank": MAX_FIXTURE_STAKE_FRACTION,
            "accas_mutually_exclusive_within_new_publications": True,
            "fixture_concentration_policy": FIXTURE_CONCENTRATION_POLICY,
            "fixture_concentration_applies_to": "new_publications_only_existing_positions_unchanged",
            "bankruptcy": "zero_free_capital_no_new_stakes_no_refill",
        },
        "by_bucket_market_leg_diagnostics": dict(groups),
        "history": days,
        "latest_learning": history[-1]["learning"] if history else None,
        "payout_basis": "hypothetical_same_book_singles_product_not_confirmed_acca_quote",
        "limitation": "paper forward experiment; no real-money promotion",
    }


def render_card(receipt):
    """Readable TXT card; the JSON receipt remains the machine/audit record."""
    lines = [
        f"autobets_ML TICKETS — {receipt['date']}",
        "=" * 62,
        "PAPER ONLY — own legs, accas and model-sized stakes; no odds band.",
        "Same-book single-price products; acca acceptance/payout unconfirmed.",
    ]
    if receipt.get("freeze_basis") == ROLLING_FREEZE:
        lines.append(f"DECISION {receipt['decision_id']} · next 24 hours · frozen on publication")
    lines.append("")
    if not receipt["accas"]:
        lines.append(
            "NO PAPER BET — missed 09:00 freeze; no late backfill."
            if receipt["status"] == "missed_freeze_no_paper_bet"
            else "NO PAPER BET — no qualifying model/price/capital combination."
        )
        lines.append("")
    for i, acca in enumerate(receipt["accas"], 1):
        lines.append(
            f"[PAPER ACCA #{i}] @{acca['odds']:.3f} — {acca['stake_units']:.6f} paper units — {acca['book']}"
        )
        for leg_index, c in enumerate(acca["legs"]):
            if leg_index:
                lines.append("")  # one blank line between legs
            # Matchup with its kickoff next to it on the same line: one header
            # line per leg, so legs are countable at a glance.
            leg_lines = [f"   {c['home']} vs {c['away']}"]
            if receipt.get("freeze_basis") == ROLLING_FREEZE:
                kickoff = parse_zoned_timestamp(c["kickoff_utc"]).astimezone(LOCAL_TZ)
                leg_lines[0] += f" · KICKOFF {kickoff:%Y-%m-%d %H:%M} SAST"
            source = source_forecast_probability(c)
            age = quote_age_at_decision(c, receipt)
            comparison = (f"Source forecast {source:.1%} · gap {(c['probability'] - source) * 100:+.1f} pp"
                          if source is not None else "Source forecast unavailable")
            quote_age = f"quote age {age / 3600:.2f}h at decision" if age is not None else "quote age unavailable"
            leg_lines.extend([
                (f"      {c['market']} {c['selection']} @{c['odds']:.3f}"
                 f" · ML {c['probability']:.1%} · {c['bucket']}"),
                f"      {comparison} · {quote_age}",
            ])
            lines.extend(leg_lines)
        lines.append("")
    concentration = receipt.get("fixture_concentration")
    if concentration is not None:
        policy = receipt["policy"]["fixture_concentration"]
        lines.extend([
            "FIXTURE STAKE BUDGET (gross; overlapping exposures are not additive bank commitments)",
            (f"   {policy['max_fixture_stake_fraction']:.1%} of TOTAL paper bank at decision"
             f" · {policy['fixture_limit_units']:.6f} units per canonical fixture"),
            "   Full acca stake counted once per fixture across markets, sides, books and contracts; no netting.",
            (f"   Reservation {concentration['input_stake_micro_units'] / MICRO_UNITS:.6f}"
             f" -> {concentration['published_stake_micro_units'] / MICRO_UNITS:.6f} units"
             f" · released/idle {concentration['released_stake_micro_units'] / MICRO_UNITS:.6f} units; no refill."),
        ])
        for entry in concentration["fixtures"]:
            if not entry["input_stake_micro_units"]:
                continue
            day, home, away = entry["fixture"]
            lines.append(
                f"   {day} {home} vs {away}: new {entry['published_stake_micro_units'] / MICRO_UNITS:.6f}"
                f" + prior open {entry['prior_open_stake_micro_units'] / MICRO_UNITS:.6f}"
                f" · unused new budget {entry['idle_budget_micro_units'] / MICRO_UNITS:.6f} units"
            )
        lines.extend(["   Existing over-cap positions are grandfathered, not resized.", ""])
    elif receipt["accas"]:
        lines.extend([
            "LEGACY STAKING — no fixture-cap policy is declared on this frozen receipt.",
            "   Historical stakes are preserved; the new gross fixture budget applies to new publications.",
            "",
        ])
    for heading, details in (
        ("COVERAGE", receipt.get("coverage", {})),
        ("REJECTIONS", receipt.get("rejections", {})),
    ):
        lines.append(heading)
        if details:
            lines.extend(
                f"   {key.replace('_', ' ').capitalize()}: {value}"
                for key, value in details.items()
            )
        else:
            lines.append("   None recorded")
        lines.append("")
    lines.extend([
        "ADMISSION  CAUTION / SKIPPED_VETO are intentionally paper-eligible; data-quality guards remain.",
        "",
        f"LEARNING  {receipt['learning']['status']}",
        "",
        f"FREEZE   {receipt.get('frozen_at') or receipt.get('freeze_at', '09:00 SAST')} | {receipt['status']}",
    ])
    return "\n".join(lines) + "\n"



def _paper_market_label(leg):
    """Display only: never infer a selection from a market's name."""
    market, selection = leg["market"], leg["selection"]
    if market == "1x2" and selection in {"home", "draw", "away"}:
        return {"home": "Home Win", "draw": "Draw", "away": "Away Win"}[selection] + " (1X2)"
    if market == "double_chance":
        label = {"home": "Home or Draw (1X)", "1x": "Home or Draw (1X)",
                 "away": "Draw or Away (X2)", "x2": "Draw or Away (X2)",
                 "draw": "No Draw (12)", "12": "No Draw (12)"}.get(selection)
        if label:
            return "Double Chance — " + label
    if market in {"btts_yes", "btts_no"} and selection == market.removeprefix("btts_"):
        return "Both Teams To Score — " + selection.capitalize()
    mapped = MARKET_PRICE_MAP.get(market)
    if mapped and mapped[1] == selection and selection in {"over", "under"}:
        slot = mapped[0]
        for prefix, subject in (("ou_", "Match"), ("tt_home_", "Home Team"), ("tt_away_", "Away Team")):
            if slot.startswith(prefix):
                return f"{subject} {selection.capitalize()} {slot.removeprefix(prefix)} Goals"
    return f"{market} {selection}"  # unknown/mismatched contracts stay explicit


def _paper_publication_time(receipt):
    stamp = parse_zoned_timestamp(receipt.get("frozen_at") or receipt.get("persisted_at"))
    return stamp.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S SAST") if stamp else "time unavailable"


def render_daily_card(history, report=None, *, audit=False):
    """One day's rolling publications; labels are views, never receipt identity.

    No deduplication of legs/fixtures, selection, staking or settlement occurs.
    Full receipt ids and receipt-local indices remain in publication references.
    The verbose audit view is opt-in; no diagnostic evidence is discarded.
    Empty scans do not cancel earlier tickets or consume acca numbers.
    """
    rows = sorted(history, key=lambda r: (parse_zoned_timestamp(r["captured_at"]), r.get("decision_id", "")))
    if not rows or len({r["date"] for r in rows}) != 1:
        raise ValueError("daily card requires receipts for exactly one date")
    count = sum(len(r["accas"]) for r in rows)
    lines = [f"autobets_ML TICKETS — {rows[0]['date']}", "=" * 62]
    if report is not None:
        lines.append(
            f"CURRENT PAPER BANK (all dates): {report['paper_bank_units']:.3f} units"
            f" · free {report['paper_free_units']:.3f} / reserved {report['paper_committed_units']:.3f}"
        )
    lines.extend([
        (f"{count} paper accas · {sum(bool(r['accas']) for r in rows)} ticket publications"
         f" · {sum(not r['accas'] for r in rows)} scans without tickets · times in SAST"),
        "PAPER ONLY — hypothetical same-book singles products; acca acceptance/payout unconfirmed.",
        "Rolling publications use the next 24 hours; frozen tickets retain their original decision basis.", "",
    ])
    if not count:
        lines.extend(["NO PAPER BET — no tickets published for this date; reasons in the audit report.", ""])
    diagnostics = []
    references = []
    number = 1
    had_tickets = False
    for publication, row in enumerate(rows, 1):
        leg_diagnostics = []
        first = number
        for original_index, acca in enumerate(row["accas"], 1):
            lines.extend([
                f"[PAPER ACCA #{number}] @{acca['odds']:.3f} — {acca['stake_units']:.6f} paper units — {acca['book']}",
                f"   Published {_paper_publication_time(row)} · reference P{publication}/{original_index}",
            ])
            for leg_index, leg in enumerate(acca["legs"], 1):
                if leg_index > 1:
                    lines.append("")
                kickoff = parse_zoned_timestamp(leg.get("kickoff_utc"))
                kickoff_text = (kickoff.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M SAST")
                                if kickoff else "unavailable")
                lines.extend([
                    f"   {leg['home']} vs {leg['away']} · KICKOFF {kickoff_text}",
                    f"      {_paper_market_label(leg)} @{leg['odds']:.3f} · ML {leg['probability']:.1%} · {leg['bucket']}",
                ])
                source = source_forecast_probability(leg)
                comparison = (f"source forecast {source:.1%} · gap {(leg['probability'] - source) * 100:+.1f} pp"
                              if source is not None else "source forecast unavailable")
                age = quote_age_at_decision(leg, row)
                quote_age = f"quote age {age / 3600:.2f}h at decision" if age is not None else "quote age unavailable"
                leg_diagnostics.append(f"   ACCA #{number} / leg {leg_index}: {comparison} · {quote_age}")
            lines.append("")
            number += 1
        if row["accas"]:
            result = f"ACCA #{first}" if first == number - 1 else f"ACCA #{first}–#{number - 1}"
        else:
            result = "No additional tickets" if had_tickets else "No tickets at this publication"
        had_tickets = had_tickets or bool(row["accas"])
        identity = row.get("decision_id") or row.get("sha256") or "legacy daily receipt"
        if row["accas"]:
            references.append(
                f"P{publication} · {_paper_publication_time(row)} · {result} · receipt {identity}"
            )
        if not audit:
            continue
        diagnostics.extend([
            f"P{publication} · {_paper_publication_time(row)} · {result}",
            f"   Receipt {identity} · status {row['status']}",
            (f"   Frozen at {row.get('frozen_at') or row.get('persisted_at', 'unavailable')}"
             f" · basis {row.get('freeze_basis', 'legacy daily freeze')}"),
        ])
        if row.get("sha256"):
            diagnostics.append(f"   SHA256 {row['sha256']}")
        if row.get("window_start") and row.get("window_end"):
            diagnostics.append(f"   Decision window {row['window_start']} → {row['window_end']}")
        for field, label in (("paper_bank_at_decision", "Bank at decision"),
                             ("paper_available_at_decision", "Available at decision"),
                             ("paper_pending_reserved_at_decision", "Reserved at decision")):
            if field in row:
                diagnostics.append(f"   {label}: {row[field]:.6f} paper units")
        concentration = row.get("fixture_concentration")
        if concentration is not None:
            policy = row["policy"]["fixture_concentration"]
            diagnostics.extend([
                (f"   Fixture budget: {policy['max_fixture_stake_fraction']:.1%} of TOTAL bank at decision"
                 f" · {policy['fixture_limit_units']:.6f} units per canonical fixture"),
                (f"   Reservation {concentration['input_stake_micro_units'] / MICRO_UNITS:.6f}"
                 f" → {concentration['published_stake_micro_units'] / MICRO_UNITS:.6f} units"
                 f" · released/idle {concentration['released_stake_micro_units'] / MICRO_UNITS:.6f}; no refill"),
            ])
            for entry in concentration["fixtures"]:
                if entry["input_stake_micro_units"]:
                    day, home, away = entry["fixture"]
                    diagnostics.append(
                        f"   {day} {home} vs {away}: new {entry['published_stake_micro_units'] / MICRO_UNITS:.6f}"
                        f" + prior open {entry['prior_open_stake_micro_units'] / MICRO_UNITS:.6f}"
                        f" · unused new budget {entry['idle_budget_micro_units'] / MICRO_UNITS:.6f} units"
                    )
        elif row["accas"]:
            diagnostics.append("   LEGACY STAKING — no fixture-cap policy declared; historical stakes unchanged.")
        for key in ("coverage", "rejections"):
            detail = "; ".join(f"{k.replace('_', ' ')}: {v}" for k, v in row.get(key, {}).items())
            diagnostics.append(f"   {key.capitalize()}: {detail or 'None recorded'}")
        diagnostics.extend([*leg_diagnostics, f"   Learning: {row['learning']['status']}", ""])
    if audit:
        lines.extend([
            "PUBLICATION & LEG DETAILS",
            "Daily acca numbers are display labels; P/publication-local index maps to the frozen receipt.",
            "Rejection counts are checks, not unique fixtures; checks can recur across scans.",
            *diagnostics,
        ])
    else:
        empty_count = sum(not r["accas"] for r in rows)
        if empty_count:
            latest_empty = next(r for r in reversed(rows) if not r["accas"])
            after_tickets = bool(count) and not rows[-1]["accas"]
            label = "No additional tickets" if after_tickets else "Scans without tickets"
            lines.extend([
                f"{label}: {empty_count} scan(s); latest empty scan {_paper_publication_time(latest_empty)}.",
                "Existing tickets are unchanged; empty scans do not cancel positions.", "",
            ])
        lines.extend([
            "PUBLICATION REFERENCES",
            "P/publication-local index maps each displayed acca to its immutable receipt.",
            *(references or ["No ticket publications."]), "",
            f"Full scan/leg diagnostics: {RECEIPT_DIR.as_posix()}/reports/{PREFIX}_{rows[0]['date']}_audit.txt",
            "Frozen JSON receipts remain alongside that reports directory.", "",
        ])
    lines.extend([
        "ADMISSION  CAUTION / SKIPPED_VETO remain paper-eligible; data-quality guards unchanged.",
        "STAKING    Gross fixture exposure counts the full acca stake once per fixture; no netting.",
        "           Fixture subtotals overlap; do not add them to bank commitments.",
        "           Decision-specific limits are in the audit report; old positions are not resized.",
        "Paper only. No real-money stakes or automatic promotion.",
    ])
    return "\n".join(lines) + "\n"



def _paper_performance_history_lines(report):
    """Group existing marked outcomes for display, not a settlement-time ledger."""
    base = report["base_paper_units"]
    if not math.isfinite(base) or base <= 0:
        raise ValueError("paper performance requires a positive finite base")
    by_day = defaultdict(list)
    for publication in report["history"]:
        for original_index, acca in enumerate(publication["accas"], 1):
            by_day[publication["date"]].append((publication, original_index, acca))
    lines = [f"BET-DAYS, oldest first ({len(by_day)} of {len(by_day)})",
             "  Staked/returned/net cover settled accas only; pending stakes are separate."]
    bank_mark = base
    held = []
    for day, entries in sorted(by_day.items()):
        settled = [a for _, _, a in entries if a["profit_units"] is not None]
        pending = [a for _, _, a in entries if a["profit_units"] is None]
        staked = sum(a["stake_units"] for a in settled)
        profit = sum(a["profit_units"] for a in settled)
        returned = staked + profit
        bank_mark += profit
        wins = sum(a["status"] == "win" for a in settled)
        losses = sum(a["status"] == "loss" for a in settled)
        # Missing returns are not zero returns: a wholly pending day is ungraded.
        returns_text = f"{100 * returned / base:6.1f}%" if settled else "      —"
        profit_text = f"{100 * profit / base:+6.1f}%" if settled else "      —"
        lines.append(
            f"  {day}   {wins}W/{losses}L   staked {100 * staked / base:6.1f}%"
            f"   returned {returns_text}   net {profit_text}"
            f"   pending {100 * sum(a['stake_units'] for a in pending) / base:6.1f}%"
            f"   bank* {100 * bank_mark / base:6.1f}%"
        )
        for daily_index, (publication, original_index, acca) in enumerate(entries, 1):
            if acca["profit_units"] is not None:
                continue
            held.extend([
                (f"  {day}   ACCA #{daily_index} @{acca['odds']:.3f}"
                 f"   stake {100 * acca['stake_units'] / base:.1f}%"
                 f" ({acca['stake_units']:.6f} paper units)   HELD (not settled)"),
            ])
            if publication.get("decision_id"):
                held.append(f"      Receipt {publication['decision_id']} / publication-local ticket {original_index}")
            for leg in acca["legs"]:
                kickoff = parse_zoned_timestamp(leg.get("kickoff_utc"))
                when = (" · " + kickoff.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M SAST")
                        if kickoff else " · kickoff unavailable")
                held.extend([
                    f"      {leg['home']} vs {leg['away']}{when}",
                    f"         {_paper_market_label(leg)} @{leg['odds']:.3f}",
                ])
    if not by_day:
        lines.append("  No bet days recorded.")
    lines.extend(["", "HELD (not yet settled; stake counted as committed)", *(held or ["  None."])])
    lines.extend([
        "", "NOTES",
        f"  Percentages of capital use the initial {base:g}-paper-unit base, not today's free bank.",
        "  bank* is reconstructed from latest known results by ticket date; pending is held at cost.",
        "  These are not stored historical daily closes or a settlement-time equity curve.",
        "  A known losing leg settles its acca as a loss even if other leg results are unresolved.",
        "  All retained history is included; no regime reset or old-loss exclusion.",
    ])
    return "\n".join(lines) + "\n"


def render_performance(report):
    roi = f"{report['roi']:+.1%}" if report["roi"] is not None else "not measured yet"
    calibration = report.get("calibration", {})
    selected = calibration.get("selected_candidates", {})
    pool = calibration.get("all_candidates", {})
    paired = calibration.get("source_comparison", {}).get("all_candidates", {})
    learning = report.get("latest_learning") or {}
    evidence = (
        f"EVIDENCE {selected.get('resolved_observations', 0)} resolved selected observations / "
        f"{selected.get('resolved_fixtures', 0)} fixtures · pool {pool.get('resolved_fixtures', 0)} resolved fixtures\n"
        f"LEARNING last decision: {learning.get('fixtures', 0)} resolved prior-day fixtures; "
        "dynamic calibration + success tilt from first results, not an automatic review/promotion trigger\n"
    )
    if paired.get("paired_observations", 0):
        evidence += (
            f"PAIRED   {paired['paired_fixtures']} fixtures / {paired['paired_observations']} observations · "
            f"Brier model {paired['model_brier']:.4f} / source {paired['source_brier']:.4f}\n"
        )
    else:
        evidence += "PAIRED   no resolved market-matched source pairs yet\n"
    base = report["base_paper_units"]
    history_text = _paper_performance_history_lines(report)
    hit_rate = f"{report['hit_rate']:.1%} hit" if report["hit_rate"] is not None else "hit rate not measured yet"
    return (
        "autobets_ML — performance, percent of capital (PAPER ONLY)\n" + "=" * 62 + "\n\n"
        f"BANK     {100 * report['paper_bank_units'] / base:.1f}%   x{report['paper_multiple']:.3f} of the initial base"
        f" · {report['paper_bank_units']:.3f} paper units\n"
        f"CAPITAL  {100 * report['paper_free_units'] / base:.1f}% free / {100 * report['paper_committed_units'] / base:.1f}% reserved"
        f" · {report['paper_free_units']:.3f} free / {report['paper_committed_units']:.3f} reserved paper units\n\n"
        f"RECORD   {report['wins']}W / {report['losses']}L   ({hit_rate})   over {report['bet_days']} bet-days\n"
        f"OPEN     {report['pending_accas']} held accas · {report['unresolved_result_legs']} unresolved leg results\n"
        f"PROFIT   {100 * report['profit_units'] / base:+.1f}% of capital · {report['profit_units']:+.3f} paper units · ROI {roi}\n"
        f"DRAWDOWN {report['max_daily_close_drawdown_units']:.3f} paper units / {report['max_daily_close_drawdown_fraction']:.1%} (ticket-date marks; pending at cost)\n"
        f"DAYS     {report['bet_days']} bet / {report['no_bet_days']} no-bet · {report['missed_freeze_days']} missed freeze\n\n"
        + history_text + "\nLEARNING & EVIDENCE\n" + evidence + "\n"
        "STAKING  quarter Kelly, own paper bank only; ROI is profit / settled stakes\n"
        f"FIXTURES new publications: gross stake <= {MAX_FIXTURE_STAKE_FRACTION:.1%} of TOTAL paper bank per canonical fixture;\n"
        "         downward-only, no refill; existing frozen positions remain unchanged\n"
        "PAYOUT   hypothetical same-book singles product, not a confirmed acca quote\n"
        "\nPaper only. No real-money stakes or automatic promotion.\n"
    )


def latest_card(root, *, now=None):
    """Current draft/frozen card for adjacent display; never selects or settles."""
    now = now or datetime.now(LOCAL_TZ)
    today = now.astimezone(LOCAL_TZ).date().isoformat()
    history = receipts(root)
    if history and history[-1].get("freeze_basis") == ROLLING_FREEZE:
        return history[-1]
    if state_path(root).exists() and not has_receipt(root, today):
        freeze_at = datetime.fromisoformat(today).replace(tzinfo=LOCAL_TZ, hour=9)
        row = _checked_draft(root, today, freeze_at)
        if row is not None:
            if now >= freeze_at:
                row = dict(row, status="09:00_cutoff_passed_awaiting_publication")
            return row
    return history[-1] if history else None


def render_latest_card(root, report=None, *, card=None):
    """Adjacent report uses the same daily view, retaining legacy/draft behavior."""
    card = latest_card(root) if card is None else card
    if card is None:
        return ""
    if card.get("freeze_basis") != ROLLING_FREEZE:
        return render_card(card)
    daily = [r for r in receipts(root) if r["date"] == card["date"]]
    return render_daily_card(daily, report)


def publish(root, score_lookup):
    """Sibling card/performance files, read by the same existing lane-report CLI."""
    migrate_receipts(root)
    history = receipts(root)
    report = performance(history, score_lookup)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{PREFIX}_performance.json").write_text(json.dumps(report, indent=2, allow_nan=False))
    (root / f"{PREFIX}_performance.txt").write_text(render_performance(report))
    if history:
        latest_day = history[-1]["date"]
        daily = [r for r in history if r["date"] == latest_day]
        text = (render_daily_card(daily, report) if any(r.get("freeze_basis") == ROLLING_FREEZE for r in daily)
                else "\n".join(render_card(r) for r in daily))
        dated_artifact_path(root, f"{PREFIX}_{latest_day}.txt").write_text(text)
        if any(r.get("freeze_basis") == ROLLING_FREEZE for r in daily):
            audit_path = root / RECEIPT_DIR / "reports" / f"{PREFIX}_{latest_day}_audit.txt"
            audit_path.parent.mkdir(parents=True, exist_ok=True)
            audit_path.write_text(render_daily_card(daily, report, audit=True))
    card = latest_card(root)
    if card is not None and card.get("freeze_basis") != ROLLING_FREEZE:
        dated_artifact_path(root, f"{PREFIX}_{card['date']}.txt").write_text(render_card(card))
    return report
