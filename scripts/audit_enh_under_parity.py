#!/usr/bin/env python3
"""Read-only red team of cohort parity, NOT a validated/as-traded backtest.

Use archived cohort rates, never refit on today's warehouse; use only strictly
pre-decision, prematch, exact-identity captured prices. Retained daily/morning
archives are not full freeze-time universes; cohort training cutoffs are
unverified. This report cannot establish incremental ROI, regardless of returns.
No providers, state writes, synthetic odds, result-based selection or tuning.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import random
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(ROOT / "scripts")]
import auto_tickets as at
import scripts.picks_today as pt
from edgefactory.enh_pricing import MARKET_PRICE_MAP, ODDSPAPI_MIN_SCHEMA_VERSION
from edgefactory.enh_registry import check_enhancement_hit


def number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (ValueError, TypeError):
        return None


def instant(value):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc) if dt.tzinfo is not None else None
    except ValueError:
        return None


def name(value):
    # Full names, orientation preserved. No truncated/fuzzy/alias matching.
    return " ".join(str(value or "").casefold().split())


def identity(row):
    return str(row.get("date") or ""), name(row.get("home")), name(row.get("away"))


def legacy_thresholds():
    # Read the production table, not a second hand-maintained threshold policy.
    tree = ast.parse(inspect.getsource(pt.compute_dynamic_enhancement))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "LINE_THRESHOLDS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("production LINE_THRESHOLDS missing; audit must be updated")


def snapshot_rates(row):
    """Only archived all-outcome cohort rates. No stated/winner-only fallback."""
    rates = {}
    for entry in list(row.get("event_notes") or []) + list(row.get("enh_candidate_log") or []):
        rate = number(entry.get("cohort_rate"))
        market = entry.get("market")
        if rate is not None and 0 <= rate <= 1 and market:
            if market in rates and abs(rates[market] - rate) > 0.00015:
                return {}  # internally inconsistent snapshots: refuse the row
            rates[market] = rate
    market = row.get("recommended_enhancement")
    rate = number(row.get("enhancement_cohort_rate"))
    if market and rate is not None and 0 <= rate <= 1:
        if market in rates and abs(rates[market] - rate) > 0.00015:
            return {}
        rates[market] = rate
    # A half-goal under is exactly the complement of its archived over.
    for under, field in pt.COHORT_COMPLEMENT_KEYS.items():
        direct = next((m for m, f in pt.COHORT_DIRECT_KEYS.items() if f == field), None)
        if direct in rates:
            complement = 1 - rates[direct]
            if under in rates and abs(rates[under] - complement) > 0.00015:
                return {}
            rates.setdefault(under, complement)
    return rates


def valid_quote(raw, source, decision, kickoff):
    """Fail closed on provenance; stricter than legacy live fail-open timestamps."""
    price = number(raw.get("odds"))
    captured, ko = instant(raw.get("captured_at")), instant(raw.get("kickoff"))
    if raw.get("source") != source:
        return "source"
    if price is None or price <= 1:
        return "invalid_price"
    if not str(raw.get("bookmaker") or "").strip():
        return "no_book"
    if decision is None or kickoff is None or captured is None or ko is None:
        return "timestamp_missing"
    if ko != kickoff:
        return "kickoff_mismatch"
    if captured > decision:
        return "after_decision"
    if captured >= kickoff:
        return "after_kickoff"
    if source == "oddspapi":
        generation = number(raw.get("schema_version"))
        if generation is None or not generation.is_integer() or generation < ODDSPAPI_MIN_SCHEMA_VERSION:
            return "old_schema"
        if (kickoff - captured).total_seconds() > 6 * 3600:
            return "stale_oddspapi"
    return None


def quotes_for(row, raw_rows, counts):
    """Latest per named source/book/selection, then best available, never best-ever."""
    decision, kickoff = instant(row.get("as_of")), instant(row.get("kickoff_utc"))
    latest = {}
    for source, raw in raw_rows:
        reason = valid_quote(raw, source, decision, kickoff)
        if reason:
            counts[reason] += 1
            continue
        key = (raw["market"], raw["selection"], source, raw["bookmaker"])
        cap, price = instant(raw["captured_at"]), float(raw["odds"])
        old = latest.get(key)
        if old is None or cap > old[0]:
            latest[key] = (cap, price)
        elif cap == old[0] and price != old[1]:
            latest[key] = (cap, None)  # conflicting same-time quote: no guessing
    result = {}
    for (market, selection, source, book), (cap, price) in latest.items():
        if price is None:
            counts["same_time_conflict"] += 1
            continue
        key = (market, selection)
        if key not in result or price > result[key]["price"]:
            result[key] = {"price": price, "source": source, "book": book,
                           "captured_at": cap.isoformat()}
    return result


def choose(rates, quotes, thresholds, parity):
    """Legacy pool explainer only; performance replay uses production_choice.

    This old helper does not reproduce the production raw-candidate tie order.
    Kept for reproducing historical competition reports, not ticket evaluation.
    """
    candidates = []
    for market, rate in rates.items():
        if market == "match_under_45" and not parity:
            continue  # absent in the original candidate generator
        mapping = MARKET_PRICE_MAP.get(market)
        quote = quotes.get(mapping) if mapping else None
        threshold = 0.25 if parity else thresholds.get(market, 0.80)
        if (rate < threshold or not 0.25 <= rate <= 0.90 or not quote
                or quote["price"] < at.MIN_LEG_ODDS):
            continue
        candidates.append({"market": market, "rate": rate, **quote})
    return max(candidates, key=lambda c: (c["rate"], c["price"]), default=None)



def archived_cohort(row, rates):
    """Partial archived rates + witnessed n, never a new warehouse/model fit.

    Missing columns stay unknown. The production cohort resolver excludes them;
    model-prior calculations only supply unused labels, not eligible rates.
    """
    if row.get("pick") not in {"home", "away", "draw"} or number(row.get("avg_p")) is None:
        return None
    sizes = {e.get("cohort_n") for e in row.get("event_notes", [])
             if isinstance(e, dict) and e.get("cohort_n") is not None}
    if len(sizes) != 1:
        return None
    n = next(iter(sizes))
    if isinstance(n, bool) or not isinstance(n, int) or n < pt.HYBRID_MIN_N:
        return None
    identity = row.get("contract_id")
    notes = row.get("event_notes") or []
    if (row.get("contract_schema") != "post_forebet_v1" or not identity
            or any(e.get("cohort_contract_id") != identity
                   or e.get("cohort_as_of_exclusive") != row.get("date")
                   or e.get("engine") != "hybrid_cohort"
                   for e in notes if isinstance(e, dict))):
        return None
    cohort = {"n": n, "contract_id": identity, "as_of_exclusive": row["date"]}
    for market, rate in rates.items():
        field = pt.COHORT_DIRECT_KEYS.get(market)
        value = rate
        if field is None:
            field = pt.COHORT_COMPLEMENT_KEYS.get(market)
            value = 1 - rate
        if field is not None:
            if field in cohort and abs(cohort[field] - value) > .00015:
                return None
            cohort[field] = value
    return cohort


class _NoWarehouse:
    """No historical replay may read today's warehouse priors/results."""
    def execute(self, *args, **kwargs):
        return self

    def fetchone(self):
        return None

    def fetchall(self):
        return []


def production_choice(row, rates, quotes, parity):
    """Run the actual selector, replacing ONLY archived inputs/local readers.

    No outcomes passed in; no fabricated prices/n/rates. Environment and module
    bindings are restored even on failure. Use in this single-process CLI only.
    """
    cohort = archived_cohort(row, rates)
    if cohort is None:
        raise ValueError("archived coherent cohort sample size and exact-contract provenance required")

    def attach(probe, index):
        quote = index.get(MARKET_PRICE_MAP.get(probe.get("recommended_enhancement")))
        probe["enhancement_priced"] = bool(quote)
        if quote:
            probe.update(enhancement_price=quote["price"],
                         enhancement_price_book=quote.get("book"),
                         enhancement_price_source=quote.get("source"))
        return probe

    fetched = []

    def fetch(*args, **kwargs):
        fetched.append(True)
        return cohort

    with patch.dict(os.environ, {pt.ENH_COHORT_PARITY_ENV: "1" if parity else "0",
                                 pt.ENV_FLAG: "0"}), patch.multiple(
            pt, fetch_match_cohort=fetch,
            attach_enhancement_price=attach,
            load_rolling_audit_hit_rates=lambda: {},
            load_enhancement_calibration=lambda *a, **k: {}):
        out = pt.compute_dynamic_enhancement(_NoWarehouse(), dict(row), quotes)
    if not fetched:
        raise ValueError("production selector did not consume archived cohort")
    market = out["recommended_enhancement"]
    if market is None:
        return None
    quote = quotes[MARKET_PRICE_MAP[market]]
    return {"market": market, "rate": pt.cohort_realized_rate(cohort, market),
            **quote, "price": out["enhancement_price"]}


def plan_selected(selected, days):
    """One production recipe for both arms; results never enter selection."""
    plans, metadata = {}, {}
    for parity in (False, True):
        plans[parity], metadata[parity] = {}, {}
        for day in days:
            pool = at.enhancement_pool(at.enhancement_legs(selected[parity][day]))
            plans[parity][day] = at.plan_day(
                pool, 100, stake_frac=at.ENHANCEMENT_LANE.stake_frac,
                max_accas=at.ENH_MAX_ACCAS, rank=at.ENHANCEMENT_RANK)
            metadata[parity][day] = {(leg["match"], leg["pick"]): leg for leg in pool}
    return plans, metadata


def selected_row(row, choice):
    cohort = archived_cohort(row, {choice["market"]: choice["rate"]})
    if cohort is None:
        raise ValueError("cannot plan a replay leg without archived exact-cohort evidence")
    note = {"market": choice["market"], "engine": "hybrid_cohort",
            "cohort_rate": choice["rate"], "cohort_n": cohort["n"],
            "cohort_contract_id": cohort["contract_id"],
            "cohort_as_of_exclusive": cohort["as_of_exclusive"], "counterfactual": True}
    return {**row, "event_notes": [note],
            "enhancement_cohort_rate": choice["rate"],
            "enhancement_cohort_n": cohort["n"],
            "enhancement_cohort_contract_id": cohort["contract_id"],
            "enhancement_cohort_as_of_exclusive": cohort["as_of_exclusive"], "recommended_enhancement": choice["market"],
            "enhancement_label": choice["market"], "enhancement_price": choice["price"],
            "enhancement_probability": choice["rate"],
            "enhancement_price_book": choice.get("book"),
            "enhancement_price_source": choice.get("source")}


def reselect_price_stress(cases, days, results, haircut):
    """Haircut quotes BEFORE eligibility/ranking, rebuild cards, then settle.

    Distinct from settlement-only slippage: a price falling below 1.30 can
    displace a winner, admit a different market or turn a date into no-bet.
    """
    selected = {False: defaultdict(list), True: defaultdict(list)}
    changes = []
    for row, rates, quotes in cases:
        effective = {key: {**q, "price": q["price"] * (1-haircut)}
                     for key, q in quotes.items()}
        choices = {arm: production_choice(row, rates, effective, arm) for arm in (False, True)}
        if choices[False] != choices[True]:
            changes.append({"fixture": list(identity(row)), "baseline": choices[False],
                            "proposed": choices[True]})
        for arm, choice in choices.items():
            if choice:
                selected[arm][row["date"]].append(selected_row(row, choice))
    plans, metadata = plan_selected(selected, days)
    arms = {arm: {d: evaluate_card(plans[arm][d], metadata[arm][d], results) for d in days}
            for arm in (False, True)}
    changed_cards = [d for d in days if plans[False][d] != plans[True][d]]
    return {"decimal_price_haircut_before_selection": haircut,
            "changed_fixture_choices": changes, "changed_card_dates": changed_cards,
            "baseline": summarize(list(arms[False].values())),
            "proposed": summarize(list(arms[True].values())),
            "paired": paired_bootstrap(arms[False], arms[True], changed_days=changed_cards),
            "changed_card_net_difference_bounds": [
                sum(arms[True][d]["worst_net"] - arms[False][d]["best_net"] for d in changed_cards),
                sum(arms[True][d]["best_net"] - arms[False][d]["worst_net"] for d in changed_cards)],
            "plans": {d: {"baseline": plans[False][d], "proposed": plans[True][d]} for d in changed_cards},
            "by_day": {d: {"baseline": arms[False][d], "proposed": arms[True][d]} for d in days}}

def result_index(root):
    out = defaultdict(set)
    doc = json.loads((root / "localdata/settled_results.json").read_text())
    for row in doc.get("rows") or []:
        hs, gs = number(row.get("hs")), number(row.get("gs"))
        if hs is not None and gs is not None and hs >= 0 and gs >= 0 and hs.is_integer() and gs.is_integer():
            out[identity(row)].add((int(hs), int(gs)))
    return out


def evaluate_card(plan, metadata, results, haircut=0.0):
    """Choose the full card FIRST. Unknowns never removed to improve selection.

    Same-day simultaneous stakes add P&L, they do NOT compound ticket by ticket.
    """
    staked = returned = 0.0
    resolved_stake = resolved_return = 0.0
    unknown_stake = best_unknown_return = 0.0
    wins = resolved = 0
    markets = Counter()
    for acca in plan:
        verdicts, filled = [], 1.0
        for leg in acca["legs"]:
            rec = metadata[(leg["match"], leg["pick"])]
            markets[rec["market"]] += 1
            scores = results.get(identity(rec["row"]), set())
            pair = next(iter(scores)) if len(scores) == 1 else None
            verdicts.append(check_enhancement_hit(rec["market"], leg["pick"], *pair) if pair else None)
            filled *= max(1.0, leg["odds"] * (1 - haircut))
        # Production rounds the acca price to two decimals.
        odds = acca["odds"] if haircut == 0 else round(filled, 2)
        stake = acca["stake_pct"]
        staked += stake
        # A known loss resolves an accumulator even if another leg is pending.
        won = False if False in verdicts else (True if all(v is True for v in verdicts) else None)
        if won is None:
            unknown_stake += stake
            best_unknown_return += stake * odds
        else:
            resolved += 1
            wins += int(won)
            payout = stake * odds if won else 0.0
            resolved_stake += stake
            resolved_return += payout
            returned += payout
    return {"bets": len(plan), "resolved": resolved, "wins": wins,
            "stake": staked, "resolved_stake": resolved_stake,
            "resolved_return": resolved_return,
            "net": resolved_return - resolved_stake,
            "unknown": len(plan) - resolved,
            "worst_net": returned - staked,
            "best_net": returned + best_unknown_return - staked,
            "log_growth": (math.log(1 + (returned - staked) / 100)
                           if not unknown_stake else None), "markets": dict(markets)}


def summarize(days):
    stake = sum(d["resolved_stake"] for d in days)
    net = sum(d["net"] for d in days)
    logs = [d["log_growth"] for d in days if d["bets"] and d["log_growth"] is not None]
    return {"total_planned_stake": sum(d["stake"] for d in days),
            "total_net_bounds": [sum(d["worst_net"] for d in days), sum(d["best_net"] for d in days)],
            "resolved_subset_roi": net / stake if stake else None,
            "days": len(days), "bet_days": sum(bool(d["bets"]) for d in days),
            "accas": sum(d["bets"] for d in days), "resolved": sum(d["resolved"] for d in days),
            "unknown": sum(d["unknown"] for d in days),
            "stake": stake, "net": net, "roi": net / stake if stake else None,
            "worst_roi": sum(d["worst_net"] for d in days) / sum(d["stake"] for d in days)
                if sum(d["stake"] for d in days) else None,
            "best_roi": sum(d["best_net"] for d in days) / sum(d["stake"] for d in days)
                if sum(d["stake"] for d in days) else None,
            "mean_log_growth_per_resolved_bet_day": sum(logs) / len(logs) if logs else None,
            "markets": dict(sum((Counter(d["markets"]) for d in days), Counter()))}


def paired_bootstrap(a, b, *, reps=2000, seed=20261019, changed_days=None):
    days = [d for d in sorted(set(a) & set(b)) if not a[d]["unknown"] and not b[d]["unknown"]
            and (a[d]["bets"] or b[d]["bets"])]
    if (changed_days is None and a == b) or changed_days == []:
        return {"status": "NO_OP", "paired_fully_resolved_days": len(days),
                "valid_replicates": 0, "roi_gap_95pct": None}
    changed = set(changed_days if changed_days is not None else
                  [d for d in sorted(set(a) & set(b)) if a[d] != b[d]])
    settled_changed = changed.intersection(days)
    if changed - settled_changed:
        return {"status": "INCOMPLETE_CHANGED_CARDS", "paired_fully_resolved_days": len(days),
                "settled_changed_days": len(settled_changed), "valid_replicates": 0, "roi_gap_95pct": None}
    if len(settled_changed) < 2:
        return {"status": "INSUFFICIENT_CHANGED_DAY_SUPPORT", "paired_fully_resolved_days": len(days),
                "settled_changed_days": len(settled_changed), "valid_replicates": 0, "roi_gap_95pct": None}
    rng = random.Random(seed)
    gaps = []
    for _ in range(reps):
        sample = rng.choices(days, k=len(days)) if days else []
        aa, bb = summarize([a[d] for d in sample]), summarize([b[d] for d in sample])
        if aa["roi"] is not None and bb["roi"] is not None:
            gaps.append(bb["roi"] - aa["roi"])
    gaps.sort()
    return {"status": "DIAGNOSTIC_ONLY", "paired_fully_resolved_days": len(days), "valid_replicates": len(gaps),
            "roi_gap_95pct": ([gaps[int(0.025 * (len(gaps)-1))], gaps[int(0.975 * (len(gaps)-1))]]
                              if gaps else None)}


def stored_performance(root):
    doc = json.loads((root / "localdata/autobets_enh_tickets_performance.json").read_text())
    rows = doc.get("history") or []
    stake = sum(r["staked_pct"] for r in rows)
    returned = sum(r["returned_pct"] for r in rows)
    accas = [a for r in rows for a in r.get("accas", [])]
    rng = random.Random(20261019)
    rois = []
    for _ in range(5000):
        sampled = rng.choices(rows, k=len(rows)) if rows else []
        sampled_stake = sum(r["staked_pct"] for r in sampled)
        if sampled_stake:
            rois.append(sum(r["returned_pct"] for r in sampled) / sampled_stake - 1)
    rois.sort()
    return {"bet_days": len(rows), "accas": len(accas),
            "wins": sum(a["won"] for a in accas), "staked_capital_points": stake,
            "returned_capital_points": returned, "stake_weighted_roi": returned/stake-1 if stake else None,
            "flat_acca_roi": sum(a["odds"] if a["won"] else 0 for a in accas)/len(accas)-1 if accas else None,
            "bank_pct": doc["bank_pct"],
            "day_bootstrap_roi_95pct": [rois[int(.025*(len(rois)-1))], rois[int(.975*(len(rois)-1))]] if rois else None,
            "accas_without_leg_identity": sum(not a.get("legs") for a in accas),
            "placement_receipts_verified": False}


def archived_snapshots(root, since, until, *, snapshot_mode="final"):
    if snapshot_mode not in {"final", "morning", "earliest"}:
        raise ValueError("unknown snapshot mode")
    counts = Counter()
    snapshots, blocked = {}, {}
    inputs = []
    paths = []
    if snapshot_mode in {"final", "earliest"}:
        paths += list((root / "localdata").glob("picks_????-??-??.json"))
    if snapshot_mode in {"morning", "earliest"}:
        paths += list((root / "localdata").glob("picks_morning_????-??-??.json"))
    for path in sorted(paths):
        day = path.stem[-10:]
        if not since <= day <= until:
            continue
        inputs.append(path)
        rows = json.loads(path.read_text())
        for row in rows if isinstance(rows, list) else []:
            counts["archived_rows"] += 1
            if row.get("date") != day:
                counts["out_of_day"] += 1
                continue
            decision, kickoff = instant(row.get("as_of")), instant(row.get("kickoff_utc"))
            if decision is None or kickoff is None:
                counts["missing_pick_timestamp"] += 1
                continue
            if (kickoff - decision).total_seconds() < 30 * 60:
                counts["late_snapshot"] += 1
                continue
            rates = snapshot_rates(row)
            if not rates:
                counts["no_archived_cohort_rates"] += 1
                continue
            if archived_cohort(row, rates) is None:
                counts["missing_or_invalid_archived_cohort_evidence"] += 1
                continue
            key = identity(row)
            if key in blocked:
                if decision >= blocked[key]:
                    counts["snapshot_blocked_by_earlier_conflict"] += 1
                    continue
                del blocked[key]  # a witnessed earlier decision is still usable
            if key in snapshots:
                counts["duplicate_fixture_rows"] += 1
                previous, previous_rates = snapshots[key]
                previous_at = instant(previous["as_of"])
                if previous_at == decision and (
                        rates != previous_rates or
                        archived_cohort(row, rates) != archived_cohort(previous, previous_rates) or
                        row.get("pick") != previous.get("pick") or row.get("avg_p") != previous.get("avg_p") or
                        kickoff != instant(previous.get("kickoff_utc"))):
                    counts["conflicting_same_time_snapshot"] += 1
                    del snapshots[key]
                    blocked[key] = decision
                    continue
                if previous_at <= decision:
                    continue  # earliest available coherent snapshot, never merge vintages
            snapshots[key] = ({**row, "_replay_archive": str(path.relative_to(root))}, rates)
    return snapshots, counts, inputs


def audit(root, since, until, *, snapshot_mode="final"):
    snapshots, counts, inputs = archived_snapshots(root, since, until, snapshot_mode=snapshot_mode)
    raw_by_fixture = defaultdict(list)
    months = {key[0][:7] for key in snapshots}
    for source in ("oddspapi", "theoddsapi"):
        for month in sorted(months):
            path = root / "localdata" / f"{source}_odds_{month}.csv.gz"
            if not path.exists():
                counts["missing_price_files"] += 1
                continue
            inputs.append(path)
            with gzip.open(path, "rt") as f:
                for raw in csv.DictReader(f):
                    key = identity(raw)
                    if key in snapshots:
                        raw_by_fixture[key].append((source, raw))
    results = result_index(root)
    thresholds = legacy_thresholds()
    selected = {False: defaultdict(list), True: defaultdict(list)}
    changes, evidence, cases = [], [], []
    newly_admitted_markets = Counter()
    for key, (row, rates) in sorted(snapshots.items()):
        quotes = quotes_for(row, raw_by_fixture[key], counts)
        cases.append((row, rates, quotes))
        counts["snapshots_with_strict_quotes"] += bool(quotes)
        counts["snapshots"] += 1
        counts["known_market_rates"] += len(rates)
        newly_admitted_here = False
        for market, rate in rates.items():
            q = quotes.get(MARKET_PRICE_MAP.get(market))
            counts["known_rates_with_strict_quote"] += bool(q)
            if q and q["price"] >= at.MIN_LEG_ODDS and .25 <= rate <= .90:
                counts["priced_in_band_candidate_occurrences"] += 1
                legacy = market != "match_under_45" and rate >= thresholds.get(market, .80)
                counts["legacy_eligible_candidate_occurrences"] += legacy
                if not legacy:
                    counts["newly_admitted_candidate_occurrences"] += 1
                    newly_admitted_markets[market] += 1
                    newly_admitted_here = True
        counts["fixtures_with_newly_admitted_candidates"] += newly_admitted_here
        for market, rate in rates.items():
            if "under" not in market or not 0.25 <= rate <= 0.90:
                continue
            counts["under_rates_in_band"] += 1
            quote = quotes.get(MARKET_PRICE_MAP.get(market))
            if quote and quote["price"] >= at.MIN_LEG_ODDS:
                counts["under_quotes_at_minimum"] += 1
                counts["under_newly_admitted"] += (market == "match_under_45" or rate < thresholds.get(market, .80))
        choices = {}
        for parity in (False, True):
            choice = production_choice(row, rates, quotes, parity)
            choices[parity] = choice
            if choice:
                selected[parity][key[0]].append(selected_row(row, choice))
        if choices[False] != choices[True]:
            changes.append({"fixture": list(key), "baseline": choices[False], "proposed": choices[True]})
        evidence.append({"fixture": list(key), "as_of": row["as_of"], "kickoff_utc": row["kickoff_utc"],
                         "archive": row["_replay_archive"], "cohort_n": archived_cohort(row, rates)["n"],
                         "cohort_rates": rates, "baseline": choices[False], "proposed": choices[True]})
    days = sorted({key[0] for key in snapshots})
    plans, metadata = plan_selected(selected, days)
    stresses = []
    for haircut in (0, 0.02, 0.05, 0.10):
        arms = {parity: {d: evaluate_card(plans[parity][d], metadata[parity][d], results, haircut)
                         for d in days} for parity in (False, True)}
        stresses.append({"decimal_price_haircut": haircut,
                         "baseline": summarize(list(arms[False].values())),
                         "proposed": summarize(list(arms[True].values())),
                         "paired": paired_bootstrap(arms[False], arms[True]),
                         "by_day": {d: {"baseline": arms[False][d], "proposed": arms[True][d]} for d in days}})
    selection_stresses = [reselect_price_stress(cases, days, results, h) for h in (0, .02, .05, .10)]
    inputs += [root / "localdata/settled_results.json", root / "localdata/autobets_enh_tickets_performance.json"]
    inputs += [root / p for p in ("scripts/audit_enh_under_parity.py", "scripts/picks_today.py",
                                 "scripts/auto_tickets.py", "src/edgefactory/enh_registry.py",
                                 "src/edgefactory/enh_pricing.py")]
    manifest = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    return {"schema": 2, "verdict": "LIMITED_ARCHIVED_INPUT_REPLAY_NOT_AS_TRADED",
            "snapshot_mode": snapshot_mode, "since": since, "until": until,
            "selector": "production compute_dynamic_enhancement, explicit env 0 vs 1",
            "limitations": ["Retained snapshots, not complete freeze-time universes; NOT an as-traded replay.",
                            "Archived cohort training cutoffs/voter-regime comparability unverified; no refit attempted.",
                            "Only exact-name same-day result joins, no fuzzy/rescheduled substitutions.",
                            "Only time-verifiable OddsPapi/TheOddsAPI prices; missing ScoutingStats history NOT inferred.",
                            "Rates only for archived markets or exact complements; unknown rates excluded; archived rates may be rounded.",
                            "Rows without a witnessed, coherent n>=100 or valid original pick/avg_p cannot run the production cohort path.",
                            "ROI/roi/stake/net fields describe the resolved subset only; total_planned_stake/net bounds include unknowns.",
                            "Haircuts are hypothetical decimal-price stresses, not claimed executable historical quotes.",
                            "No-op arms have zero improvement; unknown results prevent a paired ROI inference on changed cards.",
                            "Counterfactual cards use current production recipe, reset 100/date, no freeze/rolling-bank/parent-veto lifecycle replay.",
                            "No bookmaker receipts. Small sample and policy chosen after observing history.",
                            "No parameter search, stake/bucket changes, synthetic prices, or betting-hold release."],
            "stored_lane": stored_performance(root), "coverage": dict(counts),
            "changed_fixture_choices": changes, "evidence": evidence,
            "newly_admitted_candidates_by_market": dict(newly_admitted_markets),
            "stresses": stresses, "reselection_stresses": selection_stresses, "inputs_sha256": manifest,
            "settings": {"bankroll_basis": "100 capital points reset each date, not an as-traded rolling bank",
                         "main_lane_parent_veto_replayed": False, "freeze_lifecycle_replayed": False,
                         "min_leg_odds": at.MIN_LEG_ODDS, "stake_frac": at.ENHANCEMENT_LANE.stake_frac,
                         "stake_mode": at.STAKE_MODE, "max_accas": at.ENH_MAX_ACCAS,
                         "rank": at.ENHANCEMENT_RANK, "seed": 20261019}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--since", default="2026-10-14")
    parser.add_argument("--until", default="2026-10-18")
    parser.add_argument("--snapshot-mode", choices=("final", "morning", "earliest"), default="final")
    parser.add_argument("--out", type=Path, help="Optional report only; never point at operational state")
    args = parser.parse_args()
    if args.since > args.until:
        parser.error("since must be <= until")
    if args.out and args.out.resolve().is_relative_to((args.root / "localdata").resolve()):
        parser.error("report output must be outside operational localdata")
    report = audit(args.root.resolve(), args.since, args.until, snapshot_mode=args.snapshot_mode)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
