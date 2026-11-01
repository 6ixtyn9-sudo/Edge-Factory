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

SCHEMA = "autobets_ML_v1"
PREFIX = "autobets_ML"
LOCAL_TZ = ZoneInfo("Africa/Johannesburg")
SEARCH_BEAM_WIDTH = 128  # computational search breadth, NOT a betting/leg/odds cap
BASE_PAPER_UNITS = 100.0
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
    used = set()
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
    if available is not None and (
        type(available) not in (int, float)
        or not math.isfinite(available)
        or available < 0
        or stake_total > available + 1e-6
    ):
        raise ValueError("paper stakes exceed frozen available capital")


def validate_record(row, day, *, draft=False):
    """Shared read/restore validation; no rewriting or financial-state access."""
    if (
        row.get("schema") != SCHEMA
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
            row.get("schema") != SCHEMA
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


def select_accas(rows, available_units=BASE_PAPER_UNITS):
    """Autonomous paper accas/stakes, maximising estimated log-bank growth.

    Every supported candidate enters the search; no odds band, preset leg
    count, card count, bucket mix or fixed stake. Beam breadth bounds compute,
    not acca size. This is a deterministic heuristic, NOT a global optimum.
    Same-book/disjoint fixtures and teams keep the hypothetical payout honest.
    Kelly fractions come from this lane's probabilities; if their sum exceeds
    available paper capital they are proportionally rescaled, without leverage.
    Pending stakes are already reserved by the caller. Never top up a lost bank.
    """
    if not math.isfinite(available_units) or available_units <= 0:
        return []
    pool = sorted(
        (c for c in rows if _kelly(c["probability"], c["odds"]) is not None),
        key=lambda c: c["candidate_id"],
    )
    plan = []
    while len(pool) >= 2:
        books = defaultdict(list)
        for c in pool:
            books[c["book"].casefold()].append(c)
        best = None
        for book_rows in books.values():
            # (indices, used teams, odds, joint p); increasing indices avoid
            # permutations. All lengths can be explored, including >3 legs.
            beam = [((), frozenset(), 1.0, 1.0)]
            while beam:
                expanded = []
                for indices, used, odds, prob in beam:
                    for j in range(indices[-1] + 1 if indices else 0, len(book_rows)):
                        c = book_rows[j]
                        teams = frozenset(c["fixture"][1:])
                        if len(teams) != 2 or used.intersection(teams):
                            continue
                        d, p = odds * c["odds"], prob * c["probability"]
                        decision = _kelly(p, d)
                        if decision is None:
                            continue
                        fraction, growth = decision
                        ix = (*indices, j)
                        node = (ix, used | teams, d, p)
                        rank = (
                            growth,
                            p,
                            -len(ix),
                            tuple(book_rows[k]["candidate_id"] for k in ix),
                        )
                        if len(expanded) < SEARCH_BEAM_WIDTH:
                            heappush(expanded, (rank, node))
                        elif rank > expanded[0][0]:
                            heapreplace(expanded, (rank, node))
                        if len(ix) >= 2 and (best is None or rank > best[0]):
                            best = (rank, [book_rows[k] for k in ix], d, p, fraction)
                beam = [
                    node
                    for _, node in sorted(expanded, key=lambda x: x[0], reverse=True)[
                        :SEARCH_BEAM_WIDTH
                    ]
                ]
        if best is None:
            break
        rank, legs, odds, p, fraction = best
        plan.append(
            {
                "legs": legs,
                "odds": odds,
                "probability_estimate": p,
                "estimated_ev": p * odds - 1,
                "estimated_log_growth": rank[0],
                "model_kelly_fraction": fraction,
                "book": legs[0]["book"],
                "odds_basis": "hypothetical_product_of_same_book_single_quotes",
                "probability_basis": "product_assumes_cross_fixture_independence_not_validated",
            }
        )
        used = {team for c in legs for team in c["fixture"][1:]}
        pool = [c for c in pool if not used.intersection(c["fixture"][1:])]
    scale = max(1.0, sum(a["model_kelly_fraction"] for a in plan))
    remaining = available_units
    for a in plan:
        fraction = a["model_kelly_fraction"] / scale
        # Round down, not up: never spend more than the available paper bank.
        stake = min(remaining, math.floor(available_units * fraction * 1e6) / 1e6)
        a.update(stake_units=stake, stake_fraction_of_free_bank=fraction)
        remaining -= stake
    return [a for a in plan if a["stake_units"] > 0]


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
        row.get("schema") != SCHEMA
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
            draft = _checked_draft(root, day, freeze_at)
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
        plan = select_accas(rows, available)
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
                "staking": "model_Kelly_rescaled_to_available_paper_bank_without_leverage",
                "method": "existing_form_forecast_score_ml_plus_prior_paper_error_calibration",
                "objective": "estimated_log_bank_growth_not_a_profit_guarantee",
            },
            "paper_available_at_decision": available,
            "paper_bank_at_decision": report["paper_bank_units"],
            "paper_pending_reserved_at_decision": report["paper_committed_units"],
            "candidates": rows,
            "models": models,
            "learning": learner,
            "rejections": rejected,
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


def performance(history, score_lookup):
    """Own acca/unit ROI, drawdown, Brier error and market/bucket diagnostics.

    Exact regulation outcomes only. Missing/ambiguous scores stay pending.
    A known losing leg settles a loss; otherwise all legs must resolve. Frozen
    model-chosen stakes are PAPER accounting, never a live bank. Group figures are LEG diagnostics,
    not acca ROI and not summed across overlapping bucket/market categories.
    """
    days, accas, groups = [], [], defaultdict(lambda: {"settled": 0, "wins": 0, "profit": 0.0})
    brier = []
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
                unresolved_legs += y is None
                if y is not None:
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
