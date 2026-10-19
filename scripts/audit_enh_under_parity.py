#!/usr/bin/env python3
"""Read-only red team of cohort parity, NOT a validated/as-traded backtest.

Use archived cohort rates, never refit on today's warehouse; use only strictly
pre-decision, prematch, exact-identity captured prices. Final daily archives are
not freeze-time snapshots and their cohort training cutoffs are unverified.
Consequently this report cannot approve live promotion, regardless of its ROI.
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
from pathlib import Path
import random
import sys

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
    return {"days": len(days), "bet_days": sum(bool(d["bets"]) for d in days),
            "accas": sum(d["bets"] for d in days), "resolved": sum(d["resolved"] for d in days),
            "unknown": sum(d["unknown"] for d in days),
            "stake": stake, "net": net, "roi": net / stake if stake else None,
            "worst_roi": sum(d["worst_net"] for d in days) / sum(d["stake"] for d in days)
                if sum(d["stake"] for d in days) else None,
            "best_roi": sum(d["best_net"] for d in days) / sum(d["stake"] for d in days)
                if sum(d["stake"] for d in days) else None,
            "mean_log_growth_per_resolved_bet_day": sum(logs) / len(logs) if logs else None,
            "markets": dict(sum((Counter(d["markets"]) for d in days), Counter()))}


def paired_bootstrap(a, b, *, reps=2000, seed=20261019):
    days = [d for d in sorted(set(a) & set(b)) if not a[d]["unknown"] and not b[d]["unknown"]]
    if a == b:
        return {"status": "NO_OP", "paired_fully_resolved_days": len(days),
                "valid_replicates": 0, "roi_gap_95pct": None}
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


def audit(root, since, until):
    counts = Counter()
    snapshots = {}
    inputs = []
    for path in sorted((root / "localdata").glob("picks_????-??-??.json")):
        day = path.stem[6:]
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
            key = identity(row)
            if key in snapshots:
                counts["duplicate_fixture_rows"] += 1
                if instant(snapshots[key][0]["as_of"]) <= decision:
                    continue  # deterministic earliest available final-archive row
            snapshots[key] = (row, rates)
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
    changes, evidence = [], []
    for key, (row, rates) in sorted(snapshots.items()):
        quotes = quotes_for(row, raw_by_fixture[key], counts)
        counts["snapshots_with_strict_quotes"] += bool(quotes)
        counts["snapshots"] += 1
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
            choice = choose(rates, quotes, thresholds, parity)
            choices[parity] = choice
            if choice:
                candidate = {**row, "recommended_enhancement": choice["market"],
                             "enhancement_label": choice["market"], "enhancement_price": choice["price"],
                             "enhancement_probability": choice["rate"],
                             "enhancement_price_book": choice["book"],
                             "enhancement_price_source": choice["source"]}
                selected[parity][key[0]].append(candidate)
        if choices[False] != choices[True]:
            changes.append({"fixture": list(key), "baseline": choices[False], "proposed": choices[True]})
        evidence.append({"fixture": list(key), "as_of": row["as_of"], "kickoff_utc": row["kickoff_utc"],
                         "cohort_rates": rates, "baseline": choices[False], "proposed": choices[True]})
    days = sorted({key[0] for key in snapshots})
    plans, metadata = {}, {}
    for parity in (False, True):
        plans[parity], metadata[parity] = {}, {}
        for day in days:
            legs = at.enhancement_legs(selected[parity][day])
            pool = at.enhancement_pool(legs)
            plans[parity][day] = at.plan_day(pool, 100, stake_frac=at.ENHANCEMENT_LANE.stake_frac,
                                            max_accas=at.ENH_MAX_ACCAS, rank=at.ENHANCEMENT_RANK)
            metadata[parity][day] = {(l["match"], l["pick"]): l for l in pool}
    stresses = []
    for haircut in (0, 0.02, 0.05, 0.10):
        arms = {parity: {d: evaluate_card(plans[parity][d], metadata[parity][d], results, haircut)
                         for d in days} for parity in (False, True)}
        stresses.append({"decimal_price_haircut": haircut,
                         "baseline": summarize(list(arms[False].values())),
                         "proposed": summarize(list(arms[True].values())),
                         "paired": paired_bootstrap(arms[False], arms[True]),
                         "by_day": {d: {"baseline": arms[False][d], "proposed": arms[True][d]} for d in days}})
    inputs += [root / "localdata/settled_results.json", root / "localdata/autobets_enh_tickets_performance.json"]
    inputs += [root / p for p in ("scripts/audit_enh_under_parity.py", "scripts/picks_today.py",
                                 "scripts/auto_tickets.py", "src/edgefactory/enh_registry.py")]
    manifest = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    return {"schema": 1, "verdict": "NOT_VALIDATED_DO_NOT_PROMOTE", "since": since, "until": until,
            "limitations": ["Final daily archives, not freeze-time universes; NOT an as-traded replay.",
                            "Archived cohort training cutoffs/voter-regime comparability unverified; no refit attempted.",
                            "Only exact-name same-day result joins, no fuzzy/rescheduled substitutions.",
                            "Only time-verifiable OddsPapi/TheOddsAPI prices; missing ScoutingStats history NOT inferred.",
                            "Rates only for archived markets or their exact complements; unknown rates excluded.",
                            "Counterfactual cards use current production recipe; not historic placement claims.",
                            "No bookmaker receipts. Small sample and policy chosen after observing history.",
                            "No parameter search, stake/bucket changes, synthetic prices, or betting-hold release."],
            "stored_lane": stored_performance(root), "coverage": dict(counts),
            "changed_fixture_choices": changes, "evidence": evidence,
            "stresses": stresses, "inputs_sha256": manifest,
            "settings": {"min_leg_odds": at.MIN_LEG_ODDS, "stake_frac": at.ENHANCEMENT_LANE.stake_frac,
                         "stake_mode": at.STAKE_MODE, "max_accas": at.ENH_MAX_ACCAS,
                         "rank": at.ENHANCEMENT_RANK, "seed": 20261019}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--since", default="2026-10-14")
    parser.add_argument("--until", default="2026-10-18")
    parser.add_argument("--out", type=Path, help="Optional report only; never point at operational state")
    args = parser.parse_args()
    if args.since > args.until:
        parser.error("since must be <= until")
    if args.out and args.out.resolve().is_relative_to((args.root / "localdata").resolve()):
        parser.error("report output must be outside operational localdata")
    report = audit(args.root.resolve(), args.since, args.until)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
