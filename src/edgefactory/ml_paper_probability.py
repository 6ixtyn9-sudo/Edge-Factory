"""Chance-first PAPER selection, deliberately separate from Kelly/EV ranking.

This is an operator objective, not a fitted strategy or a profitability claim.
The product is an independence-based model estimate, NOT a calibrated joint
probability. Source/quote/timing validation remains in the existing ML lane.
"""

from __future__ import annotations

import math
from collections import defaultdict

OBJECTIVE = "highest_ticket_hit_probability_v1"
ACTIVATED_LOCAL_DATE = "2026-11-13"  # release boundary, not a backtest-selected date
PROBABILITY_BASIS = "product_assumes_cross_fixture_independence_not_validated"
STAKE_FRACTION = .001  # small flat 0.1% of TOTAL paper bank; not a Kelly/EV allocation
MIN_EVIDENCE_FIXTURES = 10  # retain the active pooled evidence requirement


def policy():
    return {
        "selection_objective": OBJECTIVE,
        "ranking": "model_joint_hit_probability_desc_price_tiebreak_only",
        "staking": "flat_fraction_of_total_paper_bank_not_Kelly",
        "paper_stake_fraction_of_total_bank": STAKE_FRACTION,
        "minimum_legs": 2,
        "leg_count_basis": "two_is_probability_maximum_when_all_leg_probabilities_below_one",
        "max_accas_per_publication": 1,
        "positive_ev_required": False,
        "probability_basis": PROBABILITY_BASIS,
    }


def supported(candidate):
    """Keep local evidence; do NOT confuse a price-edge veto with bad data.

    The old price-aware admission is still replayed and recorded verbatim.
    A negative estimated edge may compete here, but no evidence, zero support
    or malformed support may not. This never overrides quote/identity guards.
    """
    a = candidate.get("admission") or {}
    p, lower, n = candidate.get("probability"), a.get("probability_lower"), a.get("fixtures")
    return (
        a.get("policy") == "source_market_price_evidence_v1"
        and a.get("status") in {"eligible", "abstain"}
        and a.get("reason") in {"positive_conservative_edge", "edge_not_supported"}
        and type(n) is int and n >= MIN_EVIDENCE_FIXTURES
        and type(p) in (int, float) and math.isfinite(p) and 0 < p < 1
        and type(lower) in (int, float) and math.isfinite(lower) and 0 < lower <= p
    )


def best_acca(rows, *, diagnostics=None):
    """Exact maximum-probability compatible pair across all available books.

    For probabilities strictly between zero and one, any 3+ leg acca has a
    higher-probability two-leg subset. Thus pairs solve the existing minimum
    two-leg problem without an arbitrary odds band or beam/growth heuristic.
    Price only breaks an EXACT probability tie, then canonical IDs break ties.
    No weaker extra cards are added to boost turnover or expected payout.
    """
    books = defaultdict(list)
    for c in rows:
        odds = c.get("odds")
        fixture = c.get("fixture")
        if (not supported(c) or type(odds) not in (int, float)
                or not math.isfinite(odds) or odds <= 1
                or not isinstance(c.get("book"), str) or not c["book"].strip()
                or not isinstance(c.get("candidate_id"), str) or not c["candidate_id"]
                or not isinstance(fixture, (tuple, list)) or len(fixture) != 3
                or any(not isinstance(v, str) or not v for v in fixture)
                or len(set(fixture[1:])) != 2):
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
                    "selection_objective": OBJECTIVE, "probability_basis": PROBABILITY_BASIS,
                    "odds_basis": "hypothetical_product_of_same_book_single_quotes",
                }
    if diagnostics is not None:
        diagnostics.update(
            selection_objective=OBJECTIVE, status="highest_probability_pair" if best else "no_supported_pair",
            search="exact_compatible_pairs_probability_first", pair_checks=checks,
            candidate_count=len(rows), supported_candidate_count=sum(map(len, books.values())),
            selection_optimality="exact_within_supported_available_candidate_pool_before_budget_projection",
            positive_ev_required=False,
        )
    return best
