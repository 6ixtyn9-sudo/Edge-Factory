"""Independent autobets_ML PAPER lane; no live state, real stakes, registry or network access.

Uses the retained, fixture-bound ENH score model (form + source forecasts),
existing local quote index, exact result keys and shared market outcomes. Its
own forward receipts train a regularised probability calibrator on prior-day
mistakes, including bucket/market effects. No history means the *existing*
model is used unchanged, not a fabricated probability or a new bootstrap fit.

Same-book paper accas choose their own leg count, card count and stakes.
No odds band, fixed stake or artificial acca/leg-count cap is imposed.
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
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from heapq import heappush, heapreplace
from pathlib import Path
from zoneinfo import ZoneInfo

from . import price_sources as psrc
from .enh_pricing import (
    MARKET_PRICE_MAP,
    _betexplorer_asof_index,
    betexplorer_price_rejection,
    load_prices_index,
)
from .enh_registry import (
    MIN_COHORT_N,
    check_enhancement_hit,
    enhancement_ml_score_weights,
    enhancement_price_context,
)
from .identity import source_team_key, squad_marker_mismatch
from .odds_normalization import parse_zoned_timestamp
from .util import norm_team

SCHEMA = "autobets_ML_v2"
READABLE_SCHEMAS = {"autobets_ML_v1", SCHEMA}
PREFIX = "autobets_ML"
LOCAL_TZ = ZoneInfo("Africa/Johannesburg")
SEARCH_BEAM_WIDTH = 512  # computational search breadth, NOT a betting/leg/odds cap
BASE_PAPER_UNITS = 100.0
KELLY_MULTIPLIER = 0.25  # v2: quarter of robust portfolio Kelly; NOT a fixed stake
MAX_PAPER_EXPOSURE = 0.25  # of available paper capital, never live capital
EXACT_SEARCH_SIZE = 8
PORTFOLIO_ITERATIONS = 256
SEARCH_NODE_BUDGET = 250_000  # computation bound, never a leg/card count cap
QUOTE_MAX_AGE = timedelta(hours=6)
MIN_LEAD = timedelta(minutes=30)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def receipt_path(root, day):
    datetime.strptime(day, "%Y-%m-%d")
    return Path(root) / f"{PREFIX}_{day}.json"


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
        else:
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


def receipts(root):
    """Corrupt evidence is an error, never an empty/reset performance history."""
    if (Path(root) / f"{PREFIX}_integrity_block.json").exists():
        raise ValueError("autobets_ML evidence conflict; paper lane blocked, live lanes unchanged")
    result = []
    for path in sorted(Path(root).glob(f"{PREFIX}_????-??-??.json")):
        row = json.loads(path.read_text())
        unsigned = {k: v for k, v in row.items() if k != "sha256"}
        if (
            row.get("schema") not in READABLE_SCHEMAS
            or row.get("sha256") != digest(unsigned)
            or path != receipt_path(root, row["date"])
        ):
            raise ValueError(f"invalid ML paper receipt: {path.name}")
        validate_record(row, row["date"])
        result.append(row)
    return result


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


def _quote_ok(row, quote, now, kickoff, source_guard, min_leg_odds, *, market, selection):
    """A quote can enter research only with its own original price/time/book."""
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
    context = enhancement_price_context(probe)
    if context is None:
        return False
    at = parse_zoned_timestamp(context["captured_at"])
    ku = parse_zoned_timestamp(context["kickoff"])
    if (
        ku != kickoff
        or not at <= now < ku
        or now - at > QUOTE_MAX_AGE
        or context["price"] < min_leg_odds
    ):
        return False
    if psrc.spec(source).family == psrc.spec("betexplorer").family:
        return betexplorer_price_rejection(probe, execution_at=now) is None
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


def candidates(slate, day, now, index, *, kickoff_fn, source_guard, min_leg_odds, freeze_at=None):
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
                )
                or max(now, freeze_at or now) - parse_zoned_timestamp(q["enhancement_price_at"])
                > QUOTE_MAX_AGE
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


def learn(history, now, score_lookup):
    """Refit only on this lane's immutable, prior-day forward observations.

    Repeated book/market quotes do not manufacture independent games: each
    fixture receives total sample weight one; feature eligibility counts unique
    fixtures. Bucket/market effects are regularised and unsupported groups
    remain absent. This fits prediction errors, not hindsight-winning buckets.
    """
    rows = []
    training_outcomes = []
    training_keys = set()
    today = now.astimezone(LOCAL_TZ).date().isoformat()
    for receipt in history:
        captured = parse_zoned_timestamp(receipt.get("captured_at"))
        if receipt["date"] >= today or captured is None or captured >= now:
            continue
        for c in receipt["candidates"]:
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
    }
    if len(fixtures) < MIN_COHORT_N or len({y for _, y in rows}) < 2:
        return result
    # Same regularised estimator and minimum-observation convention already
    # used by the existing feature model; never fitted on today's outcomes.
    import warnings

    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression

    group_counts = defaultdict(set)
    counts = Counter(tuple(c["fixture"]) for c, _ in rows)
    for c, _ in rows:
        for field in ("bucket", "market"):
            group_counts[f"{field}:{c[field]}"].add(tuple(c["fixture"]))
    columns = sorted(k for k, v in group_counts.items() if len(v) >= MIN_COHORT_N)
    vectors = [_vector(c, columns) for c, _ in rows]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
            model.fit(
                vectors,
                [y for _, y in rows],
                sample_weight=[1 / counts[tuple(c["fixture"])] for c, _ in rows],
            )
        result.update(
            status="fitted_prior_paper_errors",
            columns=columns,
            coef=model.coef_[0].tolist(),
            intercept=float(model.intercept_[0]),
        )
    except (ValueError, ArithmeticError, ConvergenceWarning):
        result["status"] = "learning_fit_unavailable_existing_model_retained"
    return result


def _vector(c, columns):
    p = c["base_probability"]
    return [
        math.log(p / (1 - p)),
        *[float(k in (f"bucket:{c['bucket']}", f"market:{c['market']}")) for k in columns],
    ]


def apply_learning(rows, model):
    for c in rows:
        if model["status"] != "fitted_prior_paper_errors":
            continue
        z = model["intercept"] + sum(
            w * x for w, x in zip(model["coef"], _vector(c, model["columns"]))
        )
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
    }


def select_accas(rows, available_units=BASE_PAPER_UNITS, *, diagnostics=None):
    """v2: joint robust portfolio sizing, quarter Kelly, <=25% of FREE paper bank.

    No band/count/leg cap, no negative-single-EV filter, no cross-acca team
    exclusion. Reusing teams across accas is allowed and allocated jointly.
    No refill or leverage; uncertainty in the acca marginals remains unproved.
    """
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
        stake = math.floor(available_units * fraction * 1e6) / 1e6
        if stake <= 0:
            continue
        plan.append(
            dict(
                a,
                stake_units=stake,
                stake_fraction_of_free_bank=fraction,
                portfolio_allocation=allocation,
            )
        )
    return plan


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
            return True
        except FileExistsError:
            return False
    finally:
        Path(name).unlink(missing_ok=True)


def draft_path(root, day):
    datetime.strptime(day, "%Y-%m-%d")
    return Path(root) / f"{PREFIX}_draft_{day}.json"


def _checked_draft(root, day, freeze_at):
    path = draft_path(root, day)
    if not path.exists():
        return None
    row = json.loads(path.read_text())
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
    freeze_hour=9,
    now=None,
    index=None,
):
    """Independent pre-09:00 draft, immutable scheduled-09:00 card (SAST).

    A run at/after the cutoff may ONLY seal an already persisted pre-cutoff
    draft, never select from later inputs/results. If no draft exists, record a
    missed freeze/no bet honestly. Persisted-at is actual runtime, never 09:00
    backdating. Requires a runner to save a draft before 09:00; this module is
    not a scheduler. No live plan/state/bank is read, compared or modified.
    """
    clock = (lambda: now) if now is not None else (lambda: datetime.now(UTC))
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    # Integrity conflicts block PAPER only, including its no-history startup.
    receipts(root)
    # One lock for draft updates AND first freeze prevents races across cutoff.
    with (root / f".{PREFIX}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = clock()
        day = current.astimezone(LOCAL_TZ).date().isoformat()
        freeze_at = datetime.fromisoformat(day).replace(tzinfo=LOCAL_TZ, hour=freeze_hour)
        path = receipt_path(root, day)
        if path.exists():
            receipts(root)  # corrupted frozen evidence is never silently ignored
            return None

        def seal(at):
            corruption = None
            try:
                draft = _checked_draft(root, day, freeze_at)
            except (ValueError, TypeError, KeyError, AttributeError):
                # Preserve original bytes and an explicit missed-day receipt;
                # never delete/rebuild the corrupt draft or select late inputs.
                blob = draft_path(root, day).read_bytes()
                sha = hashlib.sha256(blob).hexdigest()
                quarantine = root / f"{PREFIX}_conflicts" / f"draft_{day}.{sha}.bin"
                quarantine.parent.mkdir(parents=True, exist_ok=True)
                if quarantine.exists() and quarantine.read_bytes() != blob:
                    raise ValueError("paper draft quarantine conflict; refusing evidence loss")
                if not quarantine.exists():
                    fd, name = tempfile.mkstemp(dir=quarantine.parent)
                    try:
                        with os.fdopen(fd, "wb") as stream:
                            stream.write(blob)
                            stream.flush()
                            os.fsync(stream.fileno())
                        os.link(name, quarantine)
                    finally:
                        Path(name).unlink(missing_ok=True)
                corruption = {"sha256": sha, "quarantine": str(quarantine.relative_to(root))}
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
            payload["persisted_at"] = at.isoformat()
            payload["sha256"] = digest(payload)
            return payload if _write_once(path, payload) else None

        if current >= freeze_at:
            return seal(current)
        captured = parse_zoned_timestamp(context.get("build_at"))
        if (
            context.get("date") != day
            or captured is None
            or not timedelta(0) <= current - captured <= timedelta(minutes=5)
        ):
            return None
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
            if r["date"] < day and parse_zoned_timestamp(r["captured_at"]) < captured
        ]
        report = performance(prior, score_lookup)
        available = max(0.0, report["paper_free_units"])
        search_diagnostics = {}
        plan = select_accas(rows, available, diagnostics=search_diagnostics)
        persisted = clock()
        if persisted >= freeze_at:
            # A slow build that crosses 09:00 cannot sneak a late draft in.
            return seal(persisted)
        previous = _checked_draft(root, day, freeze_at)
        if previous and parse_zoned_timestamp(previous["captured_at"]) >= captured:
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
        payload["sha256"] = digest(payload)
        # Atomic draft replacement allowed BEFORE 09:00 only; frozen receipts
        # always use the separate write-once publisher and cannot be replaced.
        fd, name = tempfile.mkstemp(dir=root, prefix=".ml-paper-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(payload, stream, sort_keys=True, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            # Check again after fsync: only durably pre-cutoff evidence may win.
            if clock() >= freeze_at:
                return seal(clock())
            os.replace(name, draft_path(root, day))
        finally:
            Path(name).unlink(missing_ok=True)
        return payload


def calibration_diagnostics(history, score_lookup):
    """Paired prequential errors of frozen base vs calibrated probabilities.

    Includes unbet candidates. Repeated books/buckets do not manufacture more
    independent fixtures: each fixture contributes total weight one per day.
    Not a significance test; unresolved records stay absent and counts explicit.
    """
    samples = {}
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
            equity += sum(a["profit_units"] for a in daily if a["profit_units"] is not None)
            peak = max(peak, equity)
            drawdown = max(drawdown, peak - equity)
            drawdown_fraction = max(drawdown_fraction, (peak - equity) / (BASE_PAPER_UNITS + peak))
        days.append(
            {
                "date": receipt["date"],
                "status": receipt["status"],
                "accas": daily,
                "learning_status": receipt["learning"]["status"],
            }
        )
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
        "receipt_days": len(history),
        "bet_days": sum(bool(r["accas"]) for r in history),
        "no_bet_days": sum(not r["accas"] for r in history),
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
            "bankruptcy": "zero_free_capital_no_new_stakes_no_refill",
        },
        "by_bucket_market_leg_diagnostics": dict(groups),
        "history": days,
        "latest_learning": history[-1]["learning"] if history else None,
        "payout_basis": "hypothetical_same_book_singles_product_not_confirmed_acca_quote",
        "limitation": "paper forward experiment; no real-money promotion",
    }


def render_card(receipt):
    lines = [
        f"autobets_ML TICKETS — {receipt['date']}",
        "=" * 62,
        "PAPER ONLY — own legs, accas and model-sized stakes; no odds band.",
        f"FREEZE   {receipt.get('freeze_at', '09:00 SAST')} | {receipt['status']}",
        "Same-book single-price products; acca acceptance/payout unconfirmed.",
    ]
    if not receipt["accas"]:
        lines.append(
            "NO PAPER BET — missed 09:00 freeze; no late backfill."
            if receipt["status"] == "missed_freeze_no_paper_bet"
            else "NO PAPER BET — no qualifying model/price/capital combination."
        )
    for i, acca in enumerate(receipt["accas"], 1):
        lines.append(
            f"[PAPER ACCA #{i}] @{acca['odds']:.3f} — {acca['stake_units']:.6f} paper units — {acca['book']}"
        )
        for c in acca["legs"]:
            lines.append(
                f"   {c['home']} vs {c['away']} | {c['market']} {c['selection']} "
                f"@{c['odds']:.3f} | {c['bucket']} | ML {c['probability']:.1%}"
            )
    lines.append(f"COVERAGE  {receipt.get('coverage', {})}")
    lines.append(f"REJECTIONS  {receipt.get('rejections', {})}")
    lines.append(f"LEARNING  {receipt['learning']['status']}")
    return "\n".join(lines) + "\n"


def render_performance(report):
    roi = f"{report['roi']:+.1%}" if report["roi"] is not None else "not measured yet"
    return (
        "autobets_ML — performance (paper only; no real stakes)\n" + "=" * 62 + "\n"
        f"BANK     {report['paper_bank_units']:.3f} paper units · x{report['paper_multiple']:.3f} of 100-unit base\n"
        f"CAPITAL  {report['paper_free_units']:.3f} free / {report['paper_committed_units']:.3f} reserved paper units\n"
        f"RECORD   {report['wins']}W / {report['losses']}L · {report['pending_accas']} pending accas · {report['unresolved_result_legs']} unresolved leg results\n"
        f"PROFIT   {report['profit_units']:+.3f} paper units · ROI {roi}\n"
        f"DRAWDOWN {report['max_daily_close_drawdown_units']:.3f} paper units / {report['max_daily_close_drawdown_fraction']:.1%} (ticket-date marks; pending at cost)\n"
        f"DAYS     {report['bet_days']} bet / {report['no_bet_days']} no-bet · {report['missed_freeze_days']} missed freeze\n"
        "STAKING  model Kelly, own paper bank only; ROI is profit / settled stakes\n"
        "PAYOUT   hypothetical same-book singles product, not a confirmed acca quote\n"
        "Paper only. No real-money stakes or automatic promotion.\n"
    )


def latest_card(root, *, now=None):
    """Current draft/frozen card for adjacent display; never selects or settles."""
    now = now or datetime.now(LOCAL_TZ)
    today = now.astimezone(LOCAL_TZ).date().isoformat()
    if draft_path(root, today).exists() and not receipt_path(root, today).exists():
        freeze_at = datetime.fromisoformat(today).replace(tzinfo=LOCAL_TZ, hour=9)
        row = _checked_draft(root, today, freeze_at)
        if now >= freeze_at:
            row = dict(row, status="09:00_cutoff_passed_awaiting_publication_no_late_changes")
        return row
    history = receipts(root)
    return history[-1] if history else None


def publish(root, score_lookup):
    """Sibling card/performance files, read by the same existing lane-report CLI."""
    history = receipts(root)
    report = performance(history, score_lookup)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{PREFIX}_performance.json").write_text(json.dumps(report, indent=2, allow_nan=False))
    (root / f"{PREFIX}_performance.txt").write_text(render_performance(report))
    if history:
        (root / f"{PREFIX}_{history[-1]['date']}.txt").write_text(render_card(history[-1]))
    card = latest_card(root)
    if card is not None:
        (root / f"{PREFIX}_{card['date']}.txt").write_text(render_card(card))
    return report
