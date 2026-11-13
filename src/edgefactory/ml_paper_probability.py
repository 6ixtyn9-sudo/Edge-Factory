"""Chance-first PAPER selection, deliberately separate from Kelly/EV ranking.

The product is an independence-based model estimate, NOT a calibrated joint
probability. The v2 portfolio takes each exact best remaining pair in turn; it
is not a global matching, any-win, or profitability optimiser. Frozen v1
single-ticket policy remains independently readable without reinterpretation.
Source/quote/timing validation remains in the existing ML lane.
"""

from __future__ import annotations

import math
from collections import defaultdict

LEGACY_OBJECTIVE = "highest_ticket_hit_probability_v1"
OBJECTIVE = "highest_ticket_hit_probability_disjoint_v2"
OBJECTIVES = frozenset((LEGACY_OBJECTIVE, OBJECTIVE))
ACTIVATED_LOCAL_DATE = "2026-11-13"  # release boundary, not a backtest-selected date
PROBABILITY_BASIS = "product_assumes_cross_fixture_independence_not_validated"
STAKE_FRACTION = .001  # 0.1% of TOTAL bank SHARED per publication, not per acca
MIN_EVIDENCE_FIXTURES = 10  # retain the active pooled evidence requirement
SHARED_STAKING = "equal_share_of_shared_publication_bank_fraction_not_Kelly"
DISJOINT_RULE = "exact_best_remaining_pair_then_remove_all_quotes_for_used_fixtures_no_refill"


def policy(objective=OBJECTIVE):
    if objective not in OBJECTIVES:
        raise ValueError("unsupported chance-first policy")
    result = {
        "selection_objective": objective,
        "ranking": "model_joint_hit_probability_desc_price_tiebreak_only",
        "staking": "flat_fraction_of_total_paper_bank_not_Kelly",
        "paper_stake_fraction_of_total_bank": STAKE_FRACTION,
        "minimum_legs": 2,
        "leg_count_basis": "two_is_probability_maximum_when_all_leg_probabilities_below_one",
        "max_accas_per_publication": 1,
        "positive_ev_required": False,
        "probability_basis": PROBABILITY_BASIS,
    }
    if objective == OBJECTIVE:
        result.update(
            max_accas_per_publication=None,
            cross_acca_fixture_reuse=False,
            portfolio_selection=DISJOINT_RULE,
            ticket_count_basis="supported_disjoint_pairs_and_micro_unit_budget_not_a_daily_quota",
            minimum_ticket_hit_probability=None,
            staking=SHARED_STAKING,
            risk_budget_scope="one_publication_shared_across_all_accas",
            allocation_rounding="equal_split_integer_micro_units_remainder_to_highest_ranks",
        )
    return result


def supported(candidate):
    """Keep local evidence; do NOT confuse a price-edge veto with bad data.

    The old price-aware admission is still replayed and recorded verbatim.
    A negative estimated edge may compete here, but no evidence, zero support
    or malformed support may not. This never overrides quote/identity guards.
    """
    a = candidate.get("admission") or {}
    if not isinstance(a, dict):
        return False
    p, lower, n = candidate.get("probability"), a.get("probability_lower"), a.get("fixtures")
    return (
        a.get("policy") == "source_market_price_evidence_v1"
        and a.get("status") in {"eligible", "abstain"}
        and a.get("reason") in {"positive_conservative_edge", "edge_not_supported"}
        and type(n) is int and n >= MIN_EVIDENCE_FIXTURES
        and type(p) in (int, float) and math.isfinite(p) and 0 < p < 1
        and type(lower) in (int, float) and math.isfinite(lower) and 0 < lower <= p
    )


def _usable(candidate):
    if not isinstance(candidate, dict):
        return False
    odds, fixture = candidate.get("odds"), candidate.get("fixture")
    return (supported(candidate) and type(odds) in (int, float)
            and math.isfinite(odds) and odds > 1
            and isinstance(candidate.get("book"), str) and bool(candidate["book"].strip())
            and isinstance(candidate.get("candidate_id"), str) and bool(candidate["candidate_id"])
            and isinstance(fixture, (tuple, list)) and len(fixture) == 3
            and all(isinstance(v, str) and bool(v) for v in fixture)
            and len(set(fixture[1:])) == 2)


def best_acca(rows, *, diagnostics=None, objective=OBJECTIVE):
    """Exact maximum-probability compatible pair across all available books.

    For probabilities strictly between zero and one, any 3+ leg acca has a
    higher-probability two-leg subset. Thus pairs solve the existing minimum
    two-leg problem without an arbitrary odds band or beam/growth heuristic.
    Price only breaks an EXACT probability tie, then canonical IDs break ties.
    """
    if objective not in OBJECTIVES:
        raise ValueError("unsupported chance-first selection objective")
    books = defaultdict(list)
    for c in rows:
        if not _usable(c):
            continue
        books[c["book"].strip().casefold()].append(c)
    best, best_key, checks = None, None, 0
    for book in sorted(books):
        cs = sorted(books[book], key=lambda c: (-c["probability"], -c["odds"], c["candidate_id"]))
        for i, a in enumerate(cs[:-1]):
            if best is not None and a["probability"] * cs[i+1]["probability"] < best["probability_estimate"]:
                break  # only strictly worse probabilities; retain all price ties
            for b in cs[i+1:]:
                p = a["probability"] * b["probability"]
                if best is not None and p < best["probability_estimate"]:
                    break
                checks += 1
                if set(a["fixture"][1:]).intersection(b["fixture"][1:]):
                    continue
                odds = a["odds"] * b["odds"]
                if not math.isfinite(odds) or not 0 < p < 1:
                    continue
                legs = sorted((a, b), key=lambda c: c["candidate_id"])
                key = (-p, -odds, tuple(c["candidate_id"] for c in legs), book)
                if best_key is not None and key >= best_key:
                    continue
                best_key = key
                best = {
                    "legs": legs, "book": legs[0]["book"], "odds": odds,
                    "probability_estimate": p, "model_probability_estimate": p,
                    "evidence_probability_estimate": math.prod(c["admission"]["probability_lower"] for c in legs),
                    "estimated_ev": p * odds - 1,
                    "selection_objective": objective, "probability_basis": PROBABILITY_BASIS,
                    "odds_basis": "hypothetical_product_of_same_book_single_quotes",
                }
    if diagnostics is not None:
        diagnostics.update(
            selection_objective=objective, status="highest_probability_pair" if best else "no_supported_pair",
            search="exact_compatible_pairs_probability_first", pair_checks=checks,
            candidate_count=len(rows), supported_candidate_count=sum(map(len, books.values())),
            selection_optimality="exact_within_supported_available_candidate_pool_before_budget_projection",
            positive_ev_required=False,
        )
    return best


def ranked_accas(rows, *, diagnostics=None):
    """Take each exact best pair; exclude its fixtures at EVERY book/market.

    Preserve the strongest primary ticket, then the strongest remaining one.
    This deterministic greedy sequence need not maximise portfolio size, total
    probability, or chance of at least one win. There is no additional numeric
    probability floor and no promise that later tickets are likely to land.
    """
    remaining, result, checks = [c for c in rows if _usable(c)], [], 0
    initial = {}
    while remaining:
        step = {}
        best = best_acca(remaining, diagnostics=step)
        if not initial:
            initial = step
        checks += step["pair_checks"]
        if best is None:
            break
        best["selection_rank"] = len(result) + 1
        result.append(best)
        used = {tuple(c["fixture"]) for c in best["legs"]}
        remaining = [c for c in remaining if tuple(c.get("fixture") or ()) not in used]
    if diagnostics is not None:
        diagnostics.update(
            selection_objective=OBJECTIVE,
            status="ranked_fixture_disjoint_pairs" if result else "no_supported_pair",
            search="repeated_exact_compatible_pairs_probability_first",
            pair_checks=checks, candidate_count=len(rows),
            supported_candidate_count=initial.get("supported_candidate_count", 0),
            supported_acca_count=len(result),
            selection_optimality="each_best_remaining_pair_exact_not_global_portfolio_optimality",
            positive_ev_required=False, minimum_ticket_hit_probability=None,
        )
    return result


def budget_shares(count, budget_micro_units):
    """One equal-split publication budget; indivisible remainder favours rank.

    Zero shares are allowed in the input allocation but cannot be published.
    Reductions, withdrawals and replay drops NEVER redistribute these shares.
    """
    if type(count) is not int or count < 0 or type(budget_micro_units) is not int or budget_micro_units < 0:
        raise ValueError("invalid chance-first shared budget")
    if not count:
        return []
    base, remainder = divmod(budget_micro_units, count)
    return [base + (i < remainder) for i in range(count)]
