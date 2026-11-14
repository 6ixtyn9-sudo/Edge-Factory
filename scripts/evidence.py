#!/usr/bin/env python3
"""Standing evidence report: is the edge real, and which layer produces it?

This module MEASURES. It adopts nothing, changes no setting, and runs no
variant search. It exists so that on 01 October there is a pre-registered,
reproducible answer to three questions that are currently confounded:

  1. THE POOL     do the legs the engine admits beat their own prices?
  2. THE RANKING  does the engine's ordering of that pool predict anything?
  3. THE BUCKETS  do the bucket labels separate winners from losers?

They are separable and must be separated. A profitable pool with a useless
ranking is a different business from a useless pool with a sharp ranking,
and both look identical in a bank curve.

Every section reports the denominator, an 80% bootstrap interval, and the
sample size that would be needed to resolve the effect it just measured.
That last figure is the point: most of these questions cannot be answered
by October, and the report says so in the same breath as the estimate,
rather than leaving a tempting point estimate lying around unqualified.

Usage
-----
    PYTHONPATH=src python3 scripts/evidence.py                  # all regimes
    PYTHONPATH=src python3 scripts/evidence.py --since 2026-10-01
    PYTHONPATH=src python3 scripts/evidence.py --json out.json
    PYTHONPATH=src python3 scripts/evidence.py --preregistration
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import datetime as _dt
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = 20000
SEED = 2026
# The standing bar is "p10 > 0": the 10th percentile of the bootstrap must
# clear zero. For a roughly symmetric statistic that means the estimate has
# to exceed 1.2816 standard errors, which is what MIN_DETECTABLE_Z encodes.
MIN_DETECTABLE_Z = 1.2816
IN_SEASON_FROM = "2026-08-01"


def _load_engine():
    spec = importlib.util.spec_from_file_location(
        "engine_under_measurement", ROOT / "scripts" / "auto_tickets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- statistics
def roi_of(legs):
    """Return-on-stake for a flat 1 unit on every leg, in percent."""
    if not legs:
        return None
    staked = len(legs)
    returned = sum(l["odds"] for l in legs if l["result"] == "win")
    return (returned - staked) / staked * 100.0


def bootstrap_roi(legs, n=BOOTSTRAP, seed=SEED):
    """80% interval and P(<=0) for a leg population's ROI."""
    if len(legs) < 2:
        return None
    rng = random.Random(seed)
    point = roi_of(legs)
    draws = []
    k = len(legs)
    for _ in range(n):
        s = rng.choices(legs, k=k)
        draws.append((sum(x["odds"] for x in s if x["result"] == "win") - k) / k * 100.0)
    draws.sort()
    se = statistics.pstdev(draws)
    return {
        "roi": point,
        "p10": draws[int(0.10 * n)],
        "p90": draws[int(0.90 * n)],
        "se": se,
        "p_le_zero": sum(d <= 0 for d in draws) / n * 100.0,
        # smallest ROI that would clear the standing bar at THIS sample size
        "min_resolvable": MIN_DETECTABLE_Z * se,
        # legs needed for the observed point estimate to clear the bar
        "n_needed": (int(len(legs) * (MIN_DETECTABLE_Z * se / point) ** 2)
                     if point and point > 0 else None),
    }


def fmt_ci(b):
    if not b:
        return "n too small"
    return (f"{b['roi']:+.1f}%  (80% {b['p10']:+.1f}% to {b['p90']:+.1f}%, "
            f"P(<=0) {b['p_le_zero']:.0f}%)")


@contextlib.contextmanager
def _all_buckets(at):
    """Temporarily widen the bucket filter, then always put it back.

    Section 4 has to report on the full JUDGED population, not just the
    legs that rode. Measuring a subgroup only among legs you already
    accepted tells you nothing about the ones you rejected -- and "which
    buckets are we excluding, and were we right to?" is exactly the
    question the exclusions themselves make unanswerable.
    """
    original = list(at.BUCKETS)
    found = {r.get("bucket") for r in at.load_archived_picks() if r.get("bucket")}
    try:
        setattr(at, "BUCKETS", sorted(set(original) | found))
        yield original
    finally:
        setattr(at, "BUCKETS", original)


# ------------------------------------------------------------------ the pool
def gather(at, lo=None, hi=None):
    """day -> ranked list of settled, playable legs, within [lo, hi]."""
    arch = at.load_archived_picks()
    settled = at.load_settled()
    days = sorted({str(p.get("date") or p.get("_archive_day") or "")[:10]
                   for p in arch})
    out = {}
    for d in days:
        if not d or (lo and d < lo) or (hi and d > hi):
            continue
        legs = [l for l in at.playable_legs(arch, day=d, settled=settled)
                if l.get("result")]
        if legs:
            out[d] = at.rank_legs(legs)
    return out


def section_pool(pools, lines, blob):
    legs = [l for r in pools.values() for l in r]
    lines.append("\n1. THE POOL — do the admitted legs beat their own prices?")
    if not legs:
        lines.append("   no settled playable legs in this window")
        return
    b = bootstrap_roi(legs)
    n = len(legs)
    wins = sum(l["result"] == "win" for l in legs)
    avg_odds = sum(l["odds"] for l in legs) / n
    be = 100.0 / avg_odds
    lines.append(f"   denominator: {n} settled playable legs over {len(pools)} days")
    lines.append(f"   win {wins / n * 100:.1f}%  ·  avg odds {avg_odds:.2f}  "
                 f"·  break-even {be:.1f}%  ·  margin {wins / n * 100 - be:+.1f}pp")
    lines.append(f"   ROI {fmt_ci(b)}")
    lines.append(f"   smallest ROI this sample could prove: {b['min_resolvable']:.1f}%")
    if b["n_needed"]:
        lines.append(f"   legs needed to prove the observed {b['roi']:+.1f}%: "
                     f"{b['n_needed']:,}  (have {n:,})")
    else:
        lines.append("   observed ROI is not positive; nothing to prove")
    blob["pool"] = {"n": n, "win_pct": wins / n * 100, "avg_odds": avg_odds,
                    "break_even": be, **b}


# --------------------------------------------------------------- the ranking
def section_ranking(pools, lines, blob):
    lines.append("\n2. THE RANKING — does the engine's ordering predict?")
    byrank = collections.defaultdict(list)
    for r in pools.values():
        for i, l in enumerate(r):
            byrank[i].append(l)
    if not byrank:
        lines.append("   no data")
        return
    lines.append(f"   {'position':>10}{'n':>7}{'win%':>9}{'ROI':>10}")
    groups = [("1-2", range(0, 2)), ("3-4", range(2, 4)),
              ("5-6", range(4, 6)), ("7+", range(6, 999))]
    tiers = {}
    for name, rng in groups:
        sel = [l for i in rng for l in byrank.get(i, [])]
        if not sel:
            continue
        r = roi_of(sel)
        w = sum(l["result"] == "win" for l in sel) / len(sel) * 100
        lines.append(f"   {name:>10}{len(sel):7}{w:8.1f}%{r:+9.1f}%")
        tiers[name] = {"n": len(sel), "win_pct": w, "roi": r}

    # The decisive test: the engine's own top-2 against random pairs drawn
    # from the SAME pools on the SAME days. This holds the pool fixed, so
    # anything left over is attributable to the ordering and nothing else.
    top = [l for r in pools.values() for l in r[:2]]
    if len(top) < 2:
        return
    obs = roi_of(top)
    rng = random.Random(SEED)
    sims = []
    for _ in range(BOOTSTRAP):
        pick = [l for r in pools.values() for l in rng.sample(r, min(2, len(r)))]
        sims.append(roi_of(pick))
    sims.sort()
    beat = sum(s >= obs for s in sims) / len(sims) * 100
    lines.append(f"\n   engine top-2      : n={len(top)}  ROI {obs:+.1f}%")
    lines.append(f"   random 2 same pool: ROI {statistics.mean(sims):+.1f}%  "
                 f"(80% {sims[int(.1 * len(sims))]:+.1f}% to {sims[int(.9 * len(sims))]:+.1f}%)")
    lines.append(f"   -> random matches or beats the ranking {beat:.1f}% of the time")
    lines.append("   VERDICT: " + ("ranking indistinguishable from random"
                                   if beat > 10 else "ranking beats random at this n"))
    blob["ranking"] = {"tiers": tiers, "top2_roi": obs,
                       "random_mean_roi": statistics.mean(sims),
                       "p_random_beats": beat}


# --------------------------------------------------------------- the buckets
def section_buckets(full_pools, live_buckets, lines, blob, min_n=20):
    lines.append("\n4. THE BUCKETS — do the labels separate anything?")
    lines.append("   measured on the FULL judged population, bucket filter OFF,")
    lines.append("   so excluded buckets are visible and can be checked.")
    legs = [l for r in full_pools.values() for l in r]
    tagged = [(l, (l.get("row") or {}).get("bucket") or "UNLABELLED") for l in legs]
    groups = collections.defaultdict(list)
    for l, b in tagged:
        groups[b].append(l)
    big = {k: v for k, v in groups.items() if len(v) >= min_n}
    if len(big) < 2:
        lines.append(f"   fewer than 2 buckets with n>={min_n}; nothing to compare")
        return
    lines.append(f"   {'bucket':>34}{'in?':>5}{'n':>6}{'ROI':>9}   80% interval")
    rows = {}
    for name in sorted(big, key=lambda k: -roi_of(big[k])):
        b = bootstrap_roi(big[name])
        mark = "IN" if name in live_buckets else "out"
        lines.append(f"   {name:>34}{mark:>5}{len(big[name]):6}{b['roi']:+8.1f}%   "
                     f"{b['p10']:+.1f}% to {b['p90']:+.1f}%")
        rows[name] = {"n": len(big[name]), "admitted": name in live_buckets, **b}

    # Permutation null: shuffle the bucket labels and see how often chance
    # alone manufactures a spread this wide. This is the only honest way to
    # read a table of subgroup ROIs.
    obs_spread = max(r["roi"] for r in rows.values()) - min(r["roi"] for r in rows.values())
    pool_legs = [l for k in big for l in big[k]]
    sizes = [len(big[k]) for k in big]
    rng = random.Random(SEED)
    hits = 0
    for _ in range(BOOTSTRAP // 4):
        rng.shuffle(pool_legs)
        i, vals = 0, []
        for s in sizes:
            vals.append(roi_of(pool_legs[i:i + s]))
            i += s
        if max(vals) - min(vals) >= obs_spread:
            hits += 1
    p = hits / (BOOTSTRAP // 4) * 100
    small = {k: v for k, v in groups.items() if len(v) < min_n}
    if small:
        lines.append("   below the n>=%d floor, shown but not tested:" % min_n)
        for k in sorted(small, key=lambda k: -len(small[k])):
            mark = "IN" if k in live_buckets else "out"
            lines.append(f"   {k:>34}{mark:>5}{len(small[k]):6}"
                         f"{roi_of(small[k]):+8.1f}%")
    missing = [b for b in live_buckets if b not in groups]
    if missing:
        lines.append(f"   admitted but absent from this window: {missing}")
    lines.append(f"\n   best-minus-worst spread: {obs_spread:.1f}%")
    lines.append(f"   shuffling the labels reproduces it {p:.1f}% of the time")
    lines.append("   VERDICT: " + ("buckets are not distinguishable from random labels"
                                   if p > 10 else "buckets separate at this n"))
    blob["buckets"] = {"rows": rows, "spread": obs_spread, "p_shuffle": p}


# ------------------------------------------------------- what it actually bets
def _as_pseudo(accas):
    """An acca behaves like a leg: one stake, one price, one binary result."""
    out = []
    for a in accas:
        won = all(l.get("result") == "win" for l in a["legs"])
        out.append({"odds": a["odds"], "result": "win" if won else "loss"})
    return out


def section_engine(at, pools, lines, blob):
    """The pool is not the bet. This measures the legs actually selected.

    Section 1 scores every admitted leg, which is the right denominator for
    "is the filter any good" and the WRONG one for "is the engine any good":
    on a rich slate the engine never touches positions 7+. This section uses
    plan_day, so the population is exactly what a ticket would have carried.
    """
    lines.append("\n3. WHAT THE ENGINE ACTUALLY BETS")
    sel_legs = []
    by_slot = collections.defaultdict(list)
    for d in sorted(pools):
        for i, a in enumerate(at.plan_day(pools[d], 100.0)):
            by_slot[i].append(a)
            sel_legs.extend(a["legs"])
    if not sel_legs:
        lines.append("   no legs selected in this window")
        return
    b = bootstrap_roi(sel_legs)
    total_pool = sum(len(r) for r in pools.values())
    lines.append(f"   selected {len(sel_legs)} legs of {total_pool} admitted "
                 f"({len(sel_legs) / total_pool * 100:.0f}% of the pool)")
    lines.append(f"   leg-level ROI {fmt_ci(b)}")
    lines.append(f"   smallest ROI this sample could prove: {b['min_resolvable']:.1f}%")
    if b["n_needed"]:
        lines.append(f"   legs needed to prove it: {b['n_needed']:,} "
                     f"(have {len(sel_legs):,})")

    # The direct test of "the sauce is in the ranking": against random
    # draws of the SAME SIZE from the SAME pools on the SAME days. Section
    # 2 compares only the top 2; the engine bets up to MAX_ACCAS*LEGS.
    per_day = {}
    for d in sorted(pools):
        k = sum(len(a["legs"]) for a in at.plan_day(pools[d], 100.0))
        if k:
            per_day[d] = k
    if per_day:
        rng = random.Random(SEED)
        sims = []
        for _ in range(BOOTSTRAP // 4):
            draw = []
            for d, k in per_day.items():
                draw.extend(rng.sample(pools[d], min(k, len(pools[d]))))
            sims.append(roi_of(draw))
        sims.sort()
        obs = b["roi"]
        beat = sum(x >= obs for x in sims) / len(sims) * 100
        lines.append(f"\n   engine selection : ROI {obs:+.1f}% on {len(sel_legs)} legs")
        lines.append(f"   random same-size : ROI {statistics.mean(sims):+.1f}%  "
                     f"(80% {sims[int(.1 * len(sims))]:+.1f}% to "
                     f"{sims[int(.9 * len(sims))]:+.1f}%)")
        lines.append(f"   -> random matches or beats the ranking {beat:.1f}% of the time")
        lines.append("   VERDICT: " + (
            "the ranking does not beat a coin toss at this n" if beat > 10
            else "the ranking BEATS a same-size random draw"))
        blob["selection_vs_random"] = {"p_random_beats": beat,
                                       "random_mean": statistics.mean(sims)}

    # Per acca slot. This prices "three accas are a must" rather than
    # arguing about it: slot #3 is the marginal ticket, and if it cannot
    # pay for its own variance then the card is simply too wide.
    lines.append(f"\n   {'acca slot':>12}{'n':>6}{'win%':>9}{'ROI':>9}   80% interval")
    slots = {}
    for i in sorted(by_slot):
        ps = _as_pseudo(by_slot[i])
        bb = bootstrap_roi(ps)
        if not bb:
            continue
        w = sum(x["result"] == "win" for x in ps) / len(ps) * 100
        lines.append(f"   {'#' + str(i + 1):>12}{len(ps):6}{w:8.1f}%{bb['roi']:+8.1f}%   "
                     f"{bb['p10']:+.1f}% to {bb['p90']:+.1f}%")
        slots[i + 1] = {"n": len(ps), "win_pct": w, **bb}

    # Is the marginal acca genuinely worse, or is that a small-n mirage?
    if len(by_slot) >= 2:
        lo_i, hi_i = min(by_slot), max(by_slot)
        first, last = _as_pseudo(by_slot[lo_i]), _as_pseudo(by_slot[hi_i])
        if len(first) > 1 and len(last) > 1:
            gap = roi_of(first) - roi_of(last)
            pooled = first + last
            rng = random.Random(SEED)
            hits = 0
            for _ in range(BOOTSTRAP // 4):
                rng.shuffle(pooled)
                if roi_of(pooled[:len(first)]) - roi_of(pooled[len(first):]) >= gap:
                    hits += 1
            p = hits / (BOOTSTRAP // 4) * 100
            lines.append(f"\n   slot #{lo_i + 1} minus slot #{hi_i + 1}: {gap:+.1f}%")
            lines.append(f"   shuffling which slot a ticket sat in reproduces that "
                         f"{p:.1f}% of the time")
            lines.append("   VERDICT: " + (
                "the marginal acca is NOT measurably worse" if p > 10
                else "the marginal acca IS measurably worse"))
            blob["slot_gap"] = {"gap": gap, "p_shuffle": p}
    blob["engine_selection"] = {"n_legs": len(sel_legs), **b, "slots": slots}


# ----------------------------------------------------------------- the money
def section_money(at, pools, lines, blob):
    lines.append("\n5. THE MONEY — what the live recipe does on these days")
    bank, peak, dd, ruin = 100.0, 100.0, 0.0, 0
    sizes = collections.Counter()
    staked_total = 0.0
    nd = 0
    for d in sorted(pools):
        plan = at.plan_day(pools[d], bank)
        if not plan:
            continue
        nd += 1
        sizes[len(plan)] += 1
        s = sum(a["stake_pct"] for a in plan)
        staked_total += s
        ret = sum(a["stake_pct"] * a["odds"] for a in plan
                  if all(l.get("result") == "win" for l in a["legs"]))
        bank += ret - s
        if bank <= 0.01:
            ruin += 1
            bank = 0.0
            break
        peak = max(peak, bank)
        dd = max(dd, 1 - bank / peak)
    if not nd:
        lines.append("   no bet-days")
        return
    lg = math.log(bank / 100.0) / nd if bank > 0 else float("-inf")
    lines.append(f"   bet-days {nd}  ·  card sizes {dict(sorted(sizes.items()))}")
    lines.append(f"   final bank {bank:.0f}%  ·  log/day {lg:+.4f}  "
                 f"·  maxDD {dd:.0%}  ·  ruin {ruin}")
    lines.append(f"   total staked {staked_total:.0f}% of a starting bank")
    lines.append("   NOTE: harness stakes the full bank; live stakes effective_bank()")
    blob["money"] = {"bet_days": nd, "final": bank, "log_per_day": lg,
                     "maxdd": dd, "ruin": ruin, "card_sizes": dict(sizes)}


# -------------------------------------------------------------------- report
def report(at, lo, hi, label):
    pools = gather(at, lo, hi)
    blob = {"window": {"from": lo, "to": hi, "label": label},
            "days": len(pools)}
    lines = [f"\n{'=' * 74}",
             f"{label}   window {lo or 'start'} .. {hi or 'today'}   "
             f"{len(pools)} settled days",
             "=" * 74]
    if not pools:
        lines.append("   (no data in this window)")
        return "\n".join(lines), blob
    section_pool(pools, lines, blob)
    section_ranking(pools, lines, blob)
    section_engine(at, pools, lines, blob)
    with _all_buckets(at) as live_buckets:
        full_pools = gather(at, lo, hi)
    section_buckets(full_pools, live_buckets, lines, blob)
    section_money(at, pools, lines, blob)
    return "\n".join(lines), blob


def engine_fingerprint(at):
    keys = ("STAKE_FRAC", "STAKE_MODE", "STAKE_PER_ACCA", "STAKE_WEIGHTS",
            "MAX_ACCAS", "MIN_ACCAS", "LEGS_PER_ACCA", "MIN_LEG_ODDS",
            "VOLUME_POOL", "VOLUME_MIN_PROB", "GATE_MODE")
    fp = {k: getattr(at, k, None) for k in keys}
    fp["BUCKETS"] = list(getattr(at, "BUCKETS", []))
    return fp


PREREGISTRATION = """\
PRE-REGISTERED QUESTIONS — sealed 2026-09-08, readable 2026-10-01
=================================================================
Scored ONLY on bet-days dated 2026-10-01 or later. Days before that are
in-sample and may not be used to score any question below.

Standing bar for ADOPTION (all three, no exceptions):
  p10 > 0  AND  leave-one-day-out holds sign  AND  maxDD <= live
Report maxDD and ruin count beside every growth figure.

Q1  max_accas=4
    In-sample +0.0483/day, which is exactly what the largest noise
    artefact in this search space looks like. Retest on new days only.
    Requires n>=60 in-season bet-days.

Q2  MIN_LEG_ODDS floor 1.20
    A lone spike: 1.15 -> -0.0132, 1.20 -> +0.0244, 1.25 -> -0.0054.
    A real threshold does not look like that. Retest on new days only.
    Requires n>=60 in-season bet-days.

Q3  IS THE POOL +EV AT ALL?    (added 2026-09-08)
    H0: legs admitted by the live filters return 0% against their own
    quoted prices. Scored at LEG level, flat 1 unit, denominator stated.
    Decision: report the estimate and its 80% interval. NO adoption
    attaches to this question; it is diagnostic. If p10 < 0 at n>=600
    new legs, the honest conclusion is that no edge has been shown.

Q4  DOES THE RANKING BEAT THE POOL?    (added 2026-09-08)
    H0: the engine's top-2 legs perform no better than 2 legs drawn at
    random from the same day's pool. Permutation test, 20k draws.
    Decision: diagnostic only. Ranking is retained regardless, because
    something must order the pool; this measures whether it earns its
    keep, not whether to keep it.

Q5  DO BUCKET LABELS SEPARATE?    (added 2026-09-08)
    H0: bucket labels are exchangeable. Best-minus-worst ROI spread
    against 5k label shuffles, buckets with n>=20 only.
    Decision: diagnostic only. Bucket membership is an operator choice
    already taken; this measures whether it was informative.

Q6  DOES THE MARGINAL ACCA PAY FOR ITSELF?    (added 2026-09-08)
    H0: acca slot #3 performs no differently from slot #1. Permutation
    on which slot a ticket occupied, 5k shuffles, acca-level ROI.
    Motivated by the rank tiers: positions 5-6 (the third acca's legs)
    measured -12.8% in-season against +9.2% for positions 1-2, on the
    operator's live archive. That is an observation, not a result.
    Decision: DIAGNOSTIC. No adoption attaches. max_accas=2 risk-matched
    is on the do-not-reopen list and stays there; this question measures
    the cost of the operator's stated three-acca preference, it does not
    reopen the setting.

Q3-Q6 are DIAGNOSTIC and cost no adoption slot. Q1 and Q2 are the only
two adoption slots and both are spoken for. Any further A/B must
declare itself here BEFORE it is run.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", help="only score days on/after this date")
    ap.add_argument("--until", help="only score days on/before this date")
    ap.add_argument("--json", help="also write the machine-readable blob here")
    ap.add_argument("--preregistration", action="store_true",
                    help="print the sealed question list and its hash, then exit")
    args = ap.parse_args(argv)

    seal = hashlib.sha256(PREREGISTRATION.encode()).hexdigest()[:16]
    if args.preregistration:
        print(PREREGISTRATION)
        print(f"sha256[:16] = {seal}")
        return 0

    at = _load_engine()
    fp = engine_fingerprint(at)
    stamp = _dt.datetime.now().isoformat(timespec="seconds")
    out = [f"EVIDENCE REPORT   generated {stamp}",
           f"pre-registration seal: {seal}",
           "",
           "engine under measurement:"]
    for k, v in fp.items():
        out.append(f"   {k:18} {v}")

    blob = {"generated": stamp, "seal": seal, "engine": fp, "windows": {}}
    windows = []
    if args.since or args.until:
        windows.append((args.since, args.until, "REQUESTED WINDOW"))
    else:
        windows = [(None, None, "WHOLE ARCHIVE (in-sample, all regimes)"),
                   (IN_SEASON_FROM, None, "IN-SEASON (from 2026-08-01, in-sample)"),
                   ("2026-10-01", None, "OUT-OF-SAMPLE (from 2026-10-01)")]
    for lo, hi, label in windows:
        text, b = report(at, lo, hi, label)
        out.append(text)
        blob["windows"][label] = b

    out.append("\n" + "=" * 74)
    out.append("Read the resolution lines before the point estimates. A number "
               "whose\nsample cannot prove it is a hypothesis, not a finding.")
    out.append("=" * 74)
    text = "\n".join(out)
    print(text)
    if args.json:
        Path(args.json).write_text(json.dumps(blob, indent=2, default=str))
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
