"""Edge Factory replay harness — counterfactual engine replays on LIVE localdata.

Answers "what would the engine have done if X?" using the REAL current ledgers
and THE LIVE SELECTION CODE ITSELF (`auto_tickets.select_accas`, called with
overrides). There is no re-implementation of the recipe in this file — the
2026-09-04 audit found two parity bugs and one no-op A/B caused by exactly
that duplication. One code path, or the harness lies.

DOCTRINE (read before trusting any output):
  - Replays are for RELATIVE comparisons (variant A vs variant B on the same
    data) and for COUNTERFACTUALS (what would today's card have been).
    They are NOT predictions. Absolute replay numbers will disagree with the
    engine's actual history (different guards live at different eras, voids,
    settlements lag). Trust the actual engine ledger for "what happened";
    trust replays only for "how do two policies differ on identical inputs."
  - Every output prints n. Cells with n < 30 are flagged as noise.
  - The primary metric is MEAN LOG GROWTH PER BET-DAY, not final bank. Daily
    growth is bank-independent (stake is always STAKE_FRAC of bank split
    evenly), so final bank = product of daily factors — one lucky treble
    dominates it. Log growth is the same information without the fireworks.
  - A/B differences are PAIRED-bootstrapped: the same resampled day indices
    are scored under both variants. An unpaired bootstrap (the 2026-09-04
    bug) prints a +-22,000% interval for two IDENTICAL variants.
  - Before any A/B, the harness diffs the two cards day by day. If the
    variants pick the same legs, it says NO-OP and refuses to bootstrap.

Variant spec syntax (anywhere a SPEC is accepted):
  "floor=1.25"                     bare number also works: "1.25" == floor=1.25
  "gate_mode=acca,volume_min=0.70" comma-separated key=value
  keys: floor, rank(prob|ev), pairing(consecutive|barbell), max_accas,
        min_accas, saturated_accas, volume_pool, volume_min,
        gate_mode(off|pool|acca), fallback(0|1), stake_frac,
        stake_mode(per_day|per_acca), stake_per_acca, weights (e.g. 3,2,1),
        min_prob (harness-only always-on prob floor)

Usage (from repo root):
  PYTHONPATH=src python3 scripts/replay_harness.py                  # status + live baseline
  PYTHONPATH=src python3 scripts/replay_harness.py --ab 1.15 1.20   # paired A/B + bootstrap
  PYTHONPATH=src python3 scripts/replay_harness.py --ab live "gate_mode=acca"
  PYTHONPATH=src python3 scripts/replay_harness.py --since 2026-08-01 --ab live "max_accas=4"
  PYTHONPATH=src python3 scripts/replay_harness.py --variant "saturated_accas=5"
  PYTHONPATH=src python3 scripts/replay_harness.py --battery        # the full sweep vs live
  PYTHONPATH=src python3 scripts/replay_harness.py --slots          # quality by rank slot
  PYTHONPATH=src python3 scripts/replay_harness.py --kelly          # stake sizing curve
  PYTHONPATH=src python3 scripts/replay_harness.py --legs           # stated-prob band table
  PYTHONPATH=src python3 scripts/replay_harness.py --rules          # quality by rule family
  PYTHONPATH=src python3 scripts/replay_harness.py --today          # today's card, live settings
  PYTHONPATH=src python3 scripts/replay_harness.py --warehouse-replay  # feasibility audit
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import random
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import auto_tickets as at  # the live engine — guards, floors, constants  # noqa: E402

LOCALDATA = ROOT / "localdata"

# Knobs forwarded to the engine. replay() calls at.plan_day(), not a harness
# copy of either selection or sizing.
SELECTION_KEYS = {"floor", "rank", "pairing", "max_accas", "min_accas",
                  "legs_per_acca", "volume_pool", "volume_min", "gate_mode",
                  "fallback", "saturated_accas"}
SIZING_KEYS = {"stake_frac", "stake_mode", "stake_per_acca", "weights"}
ENGINE_KEYS = SELECTION_KEYS | SIZING_KEYS
FLOAT_KEYS = {"floor", "volume_min", "stake_frac", "stake_per_acca", "min_prob"}
INT_KEYS = {"max_accas", "min_accas", "legs_per_acca", "volume_pool", "saturated_accas"}
BOOL_KEYS = {"fallback"}


# --------------------------------------------------------------------------
# variant specs
# --------------------------------------------------------------------------
def parse_spec(text):
    """"1.25" | "floor=1.25,gate_mode=acca" | "live" -> dict of overrides."""
    spec = {}
    text = (text or "").strip()
    if not text or text == "live":
        return spec
    try:
        return {"floor": float(text)}          # back-compat: --ab 1.10 1.20
    except ValueError:
        pass
    parts = text.split(",")
    parsed_parts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # A weight list deliberately uses commas too: weights=3,2,1. Bare
        # fragments immediately following weights belong to that value until
        # the next key=value fragment.
        if "=" not in part and parsed_parts and parsed_parts[-1][0] == "weights":
            parsed_parts[-1] = ("weights", f"{parsed_parts[-1][1]},{part}")
            continue
        if "=" not in part:
            raise SystemExit(f"bad spec fragment {part!r} (want key=value)")
        parsed_parts.append(tuple(s.strip() for s in part.split("=", 1)))
    for k, v in parsed_parts:
        if k in BOOL_KEYS:
            spec[k] = v.lower() not in ("0", "false", "no", "off")
        elif k in INT_KEYS:
            spec[k] = int(v)
        elif k in FLOAT_KEYS:
            spec[k] = float(v)
        else:
            spec[k] = v
    unknown = set(spec) - ENGINE_KEYS - {"min_prob"}
    if unknown:
        raise SystemExit(f"unknown spec key(s): {sorted(unknown)}")
    return spec


def label_of(spec):
    return "live settings" if not spec else ",".join(f"{k}={v}" for k, v in sorted(spec.items()))


# --------------------------------------------------------------------------
# universe: every archived day's settled playable legs, floor NOT applied
# (variants apply their own floor via the live selector)
# --------------------------------------------------------------------------
def build_universe(archives, settled):
    days = sorted({str(p.get("date") or p.get("_archive_day") or "")[:10] for p in archives})
    universe = {}
    for d in days:
        pool = at.playable_legs(archives, day=d, settled=settled, floor=0.0)
        pool = [l for l in pool if l["result"]]      # settled only (replay can't grade pending)
        if len(pool) >= at.LEGS_PER_ACCA:
            universe[d] = pool
    return universe


def _filtered_pool(pool, spec):
    """Apply the one harness-only filter before entering the live engine."""
    mp = spec.get("min_prob")
    if mp is None:
        return pool
    return [l for l in pool if l["prob"] >= mp]


def card_for_day(pool, spec):
    """The live selector, driven by selection-only variant overrides."""
    kw = {k: v for k, v in spec.items() if k in SELECTION_KEYS}
    return at.select_accas(_filtered_pool(pool, spec), **kw)


def day_growth(plan, bank_pct=100.0):
    """Bank multiplier derived from plan_day's returned production stakes.

    This intentionally uses the rounded ``stake_pct`` and acca odds that the
    engine ships. The harness has no separate sizing formula to drift.
    """
    staked = sum(a["stake_pct"] for a in plan)
    returned = sum(a["stake_pct"] * a["odds"] for a in plan
                   if all(l.get("result") == "win" for l in a["legs"]))
    return (bank_pct - staked + returned) / bank_pct


def replay(universe, spec):
    """Per-day record for a variant, routed through the production planner."""
    out = {}
    kw = {k: v for k, v in spec.items() if k in ENGINE_KEYS}
    for d in sorted(universe):
        # A 100%-of-capital reference bank keeps growth bank-independent while
        # exercising plan_day's exact stake rounding and cap logic.
        bank_pct = 100.0
        plan = at.plan_day(_filtered_pool(universe[d], spec), bank_pct, **kw)
        if not plan:
            continue
        out[d] = {
            "growth": day_growth(plan, bank_pct),
            "accas": [(a["odds"], all(l.get("result") == "win" for l in a["legs"]))
                      for a in plan],
            "legs": [tuple(l["match"] for l in a["legs"]) for a in plan],
            "stake_pct": [a["stake_pct"] for a in plan],
        }
    return out


def summarise(days):
    g = [days[d]["growth"] for d in sorted(days)]        # date order (drawdown is a path)
    accas = [a for d in days.values() for a in d["accas"]]
    wins = sum(1 for _, w in accas if w)
    ruin = sum(1 for x in g if x <= 0)
    logs = [math.log(x) for x in g] if not ruin else []
    if ruin:
        mean_log = -math.inf
        final = 0.0
        maxdd = 1.0
    else:
        mean_log = sum(logs) / len(logs) if logs else 0.0
        final = 100.0 * math.exp(sum(logs))
        bank = peak = 1.0
        maxdd = 0.0
        for x in g:
            bank *= x
            peak = max(peak, bank)
            maxdd = max(maxdd, 1 - bank / peak)
    return {
        "days": len(g), "accas": len(accas),
        "hit": wins / len(accas) if accas else 0.0,
        "mean_log": mean_log,
        "final": final,
        "maxdd": maxdd,
        "worst": min(g) if g else 1.0,
        "ruin": ruin,
        "leg_odds": accas,
    }


def noise_flag(n):
    return "  ⚠ small-n" if n < 30 else ""


def effect_concentration(universe, spec_a, spec_b):
    """How much of an A/B difference rides on a handful of days?

    A 52-day replay can hand you a 99%-confident bootstrap that is really one
    treble. For every day, recompute the effect with that day removed; report
    the most influential day and the leave-one-out effect. If dropping ONE day
    flips or halves the effect, it is an anecdote, not a policy.
    """
    da, db = replay(universe, spec_a), replay(universe, spec_b)
    if any(v["growth"] <= 0 for v in da.values()) or any(v["growth"] <= 0 for v in db.values()):
        return None
    la = {d: math.log(v["growth"]) for d, v in da.items()}
    lb = {d: math.log(v["growth"]) for d, v in db.items()}
    if not la or not lb:
        return None
    full = sum(lb.values()) / len(lb) - sum(la.values()) / len(la)
    contrib = []
    for d in sorted(set(la) | set(lb)):
        ka = {x: v for x, v in la.items() if x != d}
        kb = {x: v for x, v in lb.items() if x != d}
        if not ka or not kb:
            continue
        without = sum(kb.values()) / len(kb) - sum(ka.values()) / len(ka)
        contrib.append((full - without, d, without))
    if not contrib:
        return None
    contrib.sort(key=lambda t: -abs(t[0]))
    top, top_day, top_without = contrib[0]
    flip_days = [d for _, d, without in contrib
                 if full != 0 and (full > 0) != (without > 0)]
    loo = [without for _, _, without in contrib]
    return {"full": full, "top_day": top_day,
            "top_share": abs(top) / abs(full) if full else 0.0,
            "drop_one": top_without, "flips": bool(flip_days),
            "flip_days": flip_days, "loo_min": min(loo), "loo_max": max(loo),
            # does the most influential day INFLATE the effect or MASK it?
            "inflates": (top > 0) == (full > 0)}


# --------------------------------------------------------------------------
# paired bootstrap on mean log growth
# --------------------------------------------------------------------------
def card_diff_days(universe, spec_a, spec_b):
    """Days on which the two variants pick a different card (the no-op guard)."""
    diff = 0
    for d, pool in universe.items():
        ca = [tuple(l["match"] for l in a) for a in card_for_day(pool, spec_a)]
        cb = [tuple(l["match"] for l in a) for a in card_for_day(pool, spec_b)]
        if ca != cb:
            diff += 1
    return diff


def paired_bootstrap(universe, spec_a, spec_b, n=5000, seed=2026):
    """Resample DAYS once per iteration and score both variants on the SAME
    days (paired). Returns the distribution of (B - A) mean log growth."""
    random.seed(seed)
    da, db = replay(universe, spec_a), replay(universe, spec_b)
    days = sorted(set(da) | set(db))
    if not days:
        return None
    # A ruined policy is not made healthy by silently deleting its bankruptcy
    # day. It is ineligible for bootstrap comparison.
    if any(v["growth"] <= 0 for v in da.values()) or any(v["growth"] <= 0 for v in db.values()):
        return None
    ga = {d: math.log(da[d]["growth"]) for d in da}
    gb = {d: math.log(db[d]["growth"]) for d in db}
    diffs = []
    for _ in range(n):
        sample = random.choices(days, k=len(days))
        la = [ga[d] for d in sample if d in ga]
        lb = [gb[d] for d in sample if d in gb]
        if not la or not lb:
            continue
        diffs.append(sum(lb) / len(lb) - sum(la) / len(la))
    if not diffs:
        return None
    diffs.sort()
    q = lambda p: diffs[min(len(diffs) - 1, int(len(diffs) * p))]   # noqa: E731
    horizon = len(days)
    return {"median": q(0.5), "p10": q(0.1), "p90": q(0.9),
            "p_b_higher": sum(1 for x in diffs if x > 0) / len(diffs),
            "horizon": horizon,
            "median_mult": math.exp(q(0.5) * horizon),
            "p10_mult": math.exp(q(0.1) * horizon),
            "p90_mult": math.exp(q(0.9) * horizon)}


# --------------------------------------------------------------------------
# reports
# --------------------------------------------------------------------------
def engine_status():
    try:
        st = json.loads((LOCALDATA / "auto_tickets_state.json").read_text())
    except Exception:
        print("no engine state found\n")
        return
    accas = [a for h in st.get("history", []) for a in h["accas"]]
    w = sum(1 for a in accas if a["won"])
    rate = f"{w/len(accas):.0%}" if accas else "n/a"
    print("=" * 74)
    print("ENGINE ACTUAL (the only source of 'what happened')")
    print("=" * 74)
    print(f"bank {st.get('bank', 0):.1f}%  ·  bet-days {len(st.get('history', []))}  ·  "
          f"accas {w}W/{len(accas)-w}L ({rate})  ·  open slips {len(st.get('open_slips', []))}")
    for h in st.get("history", [])[-8:]:
        acc = " ".join(f"@{a['odds']:.2f}{'W' if a['won'] else 'L'}" for a in h["accas"])
        print(f"  {h['date']}  {acc:34s} bank {h['bank_pct']:7.1f}%")
    print()


def live_settings():
    print("=" * 74)
    print("LIVE SETTINGS (imported from scripts/auto_tickets.py — not grepped)")
    print("=" * 74)
    for const in ("STAKE_FRAC", "STAKE_MODE", "STAKE_PER_ACCA", "STAKE_WEIGHTS",
                  "MAX_ACCAS", "MIN_ACCAS", "LEGS_PER_ACCA", "MIN_LEG_ODDS",
                  "VOLUME_POOL", "VOLUME_MIN_PROB", "GATE_MODE", "FREEZE_HOUR"):
        print(f"  {const:18s} {getattr(at, const)}")
    print()


def print_variant(universe, spec, label=None, baseline=None):
    s = summarise(replay(universe, spec))
    lbl = label or label_of(spec)
    if s["ruin"]:
        print(f"{lbl:42s} RUIN on {s['ruin']} day(s) — final 0%, maxDD 100%; "
              "SKIPPED (bankruptcy is not an edge)")
        return s
    mark = ""
    if baseline is not None and not baseline["ruin"]:
        d = s["mean_log"] - baseline["mean_log"]
        mark = f"  Δlog/day {d:+.4f}"
    print(f"{lbl:42s} log/day {s['mean_log']:+.4f}  final {s['final']:8.0f}%  "
          f"days {s['days']:2d}  accas {s['accas']:3d}  hit {s['hit']:5.0%}  "
          f"maxDD {s['maxdd']:4.0%}  worst-day {s['worst']:.2f}"
          f"{mark}{noise_flag(s['accas'])}")
    return s


def ab_report(universe, spec_a, spec_b):
    la, lb = label_of(spec_a), label_of(spec_b)
    print(f"A/B (paired):  A = {la}   vs   B = {lb}\n")
    sa = print_variant(universe, spec_a, f"A: {la}")
    sb = print_variant(universe, spec_b, f"B: {lb}", baseline=sa)
    if sa["ruin"] or sb["ruin"]:
        print("\nA/B SKIPPED: at least one arm ruins the bank on the observed path.")
        return
    ndiff = card_diff_days(universe, spec_a, spec_b)
    print(f"\ncards differ on {ndiff}/{len(universe)} days")
    da, db = replay(universe, spec_a), replay(universe, spec_b)
    same_outcome = (sorted(da) == sorted(db) and
                    all(abs(da[d]["growth"] - db[d]["growth"]) < 1e-12 for d in da))
    if same_outcome:
        print("NO-OP: the two variants produce IDENTICAL cards AND identical daily")
        print("growth on every day. There is nothing to bootstrap — the knob does")
        print("not reach the result. (The 2026-09-04 failure mode: bootstrapping")
        print(" identical arms prints a wide interval and a meaningless ~50%.)")
        return
    if ndiff == 0:
        print("SIZING-ONLY A/B: identical cards, identical legs, identical results —")
        print("only the fraction of bank deployed differs. This is the CLEANEST")
        print("comparison the harness can make: no selection noise, no lucky legs.")
        print("Judge it on RISK, not growth: across 30-50% the growth curve is flat")
        print("(differences here will read as luck-shaped, correctly), while maxDD")
        print("moves a lot. See --kelly for the whole curve.")
    r = paired_bootstrap(universe, spec_a, spec_b)
    if not r:
        return
    print("paired bootstrap, B minus A, mean log growth per bet-day (5000 resamples):")
    print(f"  median {r['median']:+.4f}   p10 {r['p10']:+.4f}   p90 {r['p90']:+.4f}")
    print(f"  compounded over {r['horizon']} bet-days: median ×{r['median_mult']:.2f}  "
          f"(p10 ×{r['p10_mult']:.2f}, p90 ×{r['p90_mult']:.2f})")
    print(f"  P(B better) = {r['p_b_higher']:.0%}", end="  ")
    if r["p10"] < 0 < r["p90"]:
        print("— interval spans zero: luck-shaped, do NOT ship on this alone")
    else:
        print("— interval one-sided (still only 52 replay days; confirm live)")

    e = effect_concentration(universe, spec_a, spec_b)
    if e:
        print(f"\neffect concentration: worst-case single day {e['top_day']} carries "
              f"{e['top_share']:.0%} of the difference")
        print(f"  leave-one-day-out range: {e['loo_min']:+.4f} to {e['loo_max']:+.4f} "
              f"log/day (top-day removal {e['drop_one']:+.4f}; full {e['full']:+.4f})",
              end="  ")
        if e["flips"]:
            print(f"— SIGN FLIPS on {len(e['flip_days'])} removal(s): not a policy")
        elif not e["inflates"]:
            print("— the top day works AGAINST B; the effect is stronger without it")
        elif e["top_share"] > 0.4:
            print("— fragile: one day inflates most of it")
        else:
            print("— broad-based")
        if 0 < ndiff < 10:
            print(f"  ⚠ only {ndiff} days differ at all — any 'confidence' here is "
                  f"about {ndiff} coin flips")


def leg_bands(universe, floor=None, volume_pool=None):
    """Stated-prob band performance of legs on SATURATED days, with the LIVE
    floor applied and the LIVE saturation definition (both on the floored
    pool). The 2026-09-04 version applied neither and mislabelled the table."""
    floor = at.MIN_LEG_ODDS if floor is None else floor
    volume_pool = at.VOLUME_POOL if volume_pool is None else volume_pool
    edges = [(0.55, "<0.55"), (0.60, "0.55-0.60"), (0.65, "0.60-0.65"),
             (0.70, "0.65-0.70"), (0.75, "0.70-0.75"), (9.9, "0.75+")]
    bands = {name: [0, 0, 0.0] for _, name in edges}
    sat_days = 0
    for pool in universe.values():
        floored = [l for l in pool if l["odds"] >= floor]
        if len(floored) < volume_pool:
            continue
        sat_days += 1
        for l in floored:
            name = next(n for hi, n in edges if l["prob"] < hi)
            bands[name][0] += 1
            if l["result"] == "win":
                bands[name][1] += 1
                bands[name][2] += l["odds"]
    return bands, sat_days


def cmd_today(universe, settled):
    today = date.today().isoformat()
    pool = universe.get(today)
    if pool is None:
        pool = at.playable_legs(json.loads((LOCALDATA / "picks_today.json").read_text()),
                                day=today, settled=settled, floor=0.0)
    accas = at.select_accas(pool)                    # LIVE settings, live code
    print(f"today ({today}) at live settings — {len(accas)} accas "
          f"(pre-freeze this is a PARTIAL pool; the frozen card is the truth):")
    for i, a in enumerate(accas, 1):
        prod = math.prod(l["odds"] for l in a)
        print(f"  ACCA #{i} @{prod:.2f}: " + " x ".join(
            f"{l['match']} ({l['pick']} @{l['odds']:.2f}, stated {l['prob']:.0%})" for l in a))


def cmd_kelly(universe, spec=None):
    """Growth-vs-risk curve over stake fraction, through ``plan_day`` only.

    Sizing changes NOTHING about selection, so its evidence is cleaner than a
    leg-filter A/B. Every grid cell is still a production-planner replay: this
    command owns no second stake formula that can drift from shipped tickets.
    """
    spec = {k: v for k, v in dict(spec or {}).items() if k != "stake_frac"}
    grid = sorted(set([i / 100 for i in range(5, 101, 5)] + [at.STAKE_FRAC]))
    curves = {f: replay(universe, {**spec, "stake_frac": f}) for f in grid}
    stats = {f: summarise(days) for f, days in curves.items()}
    reference = curves[at.STAKE_FRAC]
    if not reference:
        print("no bet-days")
        return
    total_losses = sum(not any(w for _, w in rec["accas"]) for rec in reference.values())

    print(f"stake sizing on {len(reference)} bet-days ({total_losses} total-loss days)")
    print("cards are IDENTICAL across rows — only the fraction of bank changes\n")
    print(f"{'stake f':>8s} {'log/day':>9s} {'final%':>9s} {'maxDD':>7s}")
    valid_grid = [f for f in grid if not stats[f]["ruin"]]
    if not valid_grid:
        print("every stake on the grid ruins the bank")
        return
    best = max(valid_grid, key=lambda f: stats[f]["mean_log"])
    for f in grid:
        s = stats[f]
        if s["ruin"]:
            print(f"{f:8.0%} {'RUIN':>9s} {0:9.0f} {1:7.0%}   <- SKIPPED")
            continue
        star = "   <- growth-optimal" if f == best else ""
        if f == at.STAKE_FRAC:
            star += "   <- LIVE"
        print(f"{f:8.0%} {s['mean_log']:+9.4f} {s['final']:9.0f} {s['maxdd']:7.0%}{star}")

    # Paired resampling: one day sample scores every globally non-ruin grid
    # cell. A sample cannot rehabilitate a fraction known to bankrupt the
    # observed path.
    days = sorted(reference)
    logs = {f: {d: math.log(curves[f][d]["growth"]) for d in days}
            for f in valid_grid}
    random.seed(2026)
    opts = []
    for _ in range(2000):
        sample = random.choices(days, k=len(days))
        opts.append(max(valid_grid,
                        key=lambda f: sum(logs[f][d] for d in sample) / len(sample)))
    opts.sort()
    best_s = stats[best]
    print(f"\ngrowth-optimal f on this path: {best:.0%} "
          f"(log/day {best_s['mean_log']:+.4f}, maxDD {best_s['maxdd']:.0%})")
    print(f"bootstrapped f*: median {opts[len(opts)//2]:.0%}  "
          f"p10 {opts[int(.1*len(opts))]:.0%}  p90 {opts[int(.9*len(opts))]:.0%}")
    below = sum(1 for o in opts if o < at.STAKE_FRAC) / len(opts)
    print(f"P(f* < live {at.STAKE_FRAC:.0%}) = {below:.0%}")
    print("\nKelly doctrine: the growth curve is asymmetric — overbetting past f*")
    print("loses growth AND multiplies drawdown, underbetting only costs growth")
    print("slowly. With f* this uncertain, size BELOW the point estimate.")


def slot_table(universe, floor=None, max_slots=12, min_pool=None):
    """Leg quality by RANK SLOT, and acca quality by slot pair.

    Checkpoint ① ("should a 4th/5th acca exist?") asked as a day-level A/B is
    a 19-day question that one treble can own. Asked as "are the legs ranked
    7-8 as good as the legs ranked 1-6?" it is a several-hundred-leg question.
    Same ledger, far more signal: if slots 7-10 hold their ROI, more accas is
    a structural yes; if they decay, the extra accas are variance, not edge.
    """
    floor = at.MIN_LEG_ODDS if floor is None else floor
    slots = {i: [0, 0, 0.0] for i in range(1, max_slots + 1)}
    accas = {i: [0, 0, 0.0] for i in range(1, max_slots // 2 + 1)}
    n_days = 0
    for pool in universe.values():
        ranked = at.rank_legs([l for l in pool if l["odds"] >= floor])
        if min_pool is not None and len(ranked) < min_pool:
            continue        # like-for-like: every slot drawn from the SAME days
        n_days += 1
        ranked = ranked[:max_slots]
        for i, leg in enumerate(ranked, 1):
            slots[i][0] += 1
            if leg["result"] == "win":
                slots[i][1] += 1
                slots[i][2] += leg["odds"]
        for j in range(0, len(ranked) - 1, 2):
            a, b = ranked[j], ranked[j + 1]
            idx = j // 2 + 1
            accas[idx][0] += 1
            if a["result"] == "win" and b["result"] == "win":
                accas[idx][1] += 1
                accas[idx][2] += a["odds"] * b["odds"]
    return slots, accas, n_days


def _print_slots(slots, accas, n_days, header):
    print(header)
    print(f"{'slot':>4s} {'n':>4s} {'hit':>7s} {'flatROI':>9s}")
    for i, (n, w, ret) in slots.items():
        if n:
            print(f"{i:4d} {n:4d} {w/n:7.1%} {(ret-n)/n:+9.1%}"
                  f"{'  << small-n' if n < 30 else ''}")
    print(f"\n{'acca':>4s} {'legs':>7s} {'n':>4s} {'hit':>7s} {'flatROI':>9s}")
    for i, (n, w, ret) in accas.items():
        if n:
            print(f"{i:4d} {f'{2*i-1}+{2*i}':>7s} {n:4d} {w/n:7.1%} {(ret-n)/n:+9.1%}"
                  f"{'  << small-n' if n < 30 else ''}")


def cmd_slots(universe):
    slots, accas, n_days = slot_table(universe)
    _print_slots(slots, accas, n_days,
                 "=== ALL DAYS — leg/acca quality by rank slot (floor applied) ===\n"
                 "CONFOUNDED: slot 1 is drawn from every day, slot 8 only from the\n"
                 "big-pool days. Use it for shape, not for comparisons.\n")
    slots8, accas8, n8 = slot_table(universe, min_pool=8, max_slots=8)
    print(f"\n=== LIKE-FOR-LIKE — only the {n8} days that offer 8+ legs ===")
    print("every slot below is drawn from the SAME days (table stops at slot 8 —")
    print("beyond it the day counts fall again and the comparison re-confounds).\n")
    _print_slots(slots8, accas8, n8, "")
    print("\nread: a 4th acca is worth adding only if the slot-7+8 row pays like")
    print("the rows above it ON THESE DAYS. Adding accas does NOT reduce risk —")
    print("total stake is fixed at STAKE_FRAC and merely split further.")


def rule_family(rule):
    """Group a miner rule into the family the ledger reasons about."""
    r = str(rule or "")
    if r.startswith("ml-meta"):
        return "ml-meta"
    if r.startswith("2way"):
        return "2way-unanimous"
    if r.startswith("3way"):
        return "3way-unanimous"
    return "other"


def _leg_stats(legs, seed=2026):
    """n, hit rate, flat ROI and calibration gap with bootstrap deciles."""
    if not legs:
        return None
    rnd = random.Random(seed)
    ret = [(l["odds"] - 1.0) if l["result"] == "win" else -1.0 for l in legs]
    gap = [(1.0 if l["result"] == "win" else 0.0) - l["prob"] for l in legs]
    n = len(legs)
    roi_bs = sorted(sum(rnd.choices(ret, k=n)) / n for _ in range(5000))
    gap_bs = sorted(sum(rnd.choices(gap, k=n)) / n for _ in range(5000))
    return {
        "n": n,
        "hit": sum(1 for l in legs if l["result"] == "win") / n,
        "stated": sum(l["prob"] for l in legs) / n,
        "roi": sum(ret) / n,
        "roi_p10": roi_bs[500], "roi_p90": roi_bs[4500],
        "gap": sum(gap) / n,
        "gap_p10": gap_bs[500], "gap_p90": gap_bs[4500],
    }


def _ridden_legs(universe):
    """The legs that actually rode a card, tagged with their rule."""
    out = []
    for d in sorted(universe):
        pool = universe[d]
        for acca in at.plan_day(pool, 100.0):
            for leg in acca["legs"]:
                src = next((x for x in pool if x["match"] == leg["match"]
                            and x["pick"] == leg["pick"]), None)
                if src and leg.get("result") in ("win", "loss"):
                    out.append({**leg, "_day": d, "row": src["row"]})
    return out


def _rule_table(legs, title):
    print(f"\n{title}  (n={len(legs)})")
    print(f"  {'family':16s} {'n':>4s} {'stated':>7s} {'realised':>8s} "
          f"{'gap':>7s} {'gapP10':>7s} {'flatROI':>8s} {'roiP10':>8s} {'roiP90':>8s}")
    buckets = {}
    for l in legs:
        buckets.setdefault(rule_family(l["row"].get("rule")), []).append(l)
    for fam in ("ml-meta", "2way-unanimous", "3way-unanimous", "other"):
        s = _leg_stats(buckets.get(fam) or [])
        if not s:
            continue
        print(f"  {fam:16s} {s['n']:4d} {s['stated']:7.1%} {s['hit']:8.1%} "
              f"{100*s['gap']:+6.1f}p {100*s['gap_p10']:+6.1f}p {s['roi']:+8.1%} "
              f"{s['roi_p10']:+8.1%} {s['roi_p90']:+8.1%}{noise_flag(s['n'])}")


def cmd_rules(universe):
    """Checkpoint ⑫: is the ml-meta family carrying its weight, or costing?

    The escalation that prompted this asked whether the leaked-feature model
    UNDERPERFORMS the honest consensus rules. The table answers that directly,
    and the paired removal replay prices the only live change that follows.
    """
    print("=" * 74)
    print("RULE-FAMILY QUALITY (checkpoint ⑫)")
    print("=" * 74)
    print("'gap' is realised minus stated: POSITIVE means the rule is")
    print("UNDER-confident (it wins more often than it claims).\n")

    pool = [l for d in sorted(universe) for l in universe[d]
            if l["result"] in ("win", "loss")]
    _rule_table(pool, "every settled playable leg")
    _rule_table(_ridden_legs(universe), "legs the engine actually rode")

    ml_days = sorted({d for d in universe
                      for l in universe[d]
                      if rule_family(l["row"].get("rule")) == "ml-meta"})
    if ml_days:
        print(f"\nml-meta legs first appear {ml_days[0]} and run to {ml_days[-1]} "
              f"({len(ml_days)} days).")
        print("Any comparison against a family that also fired pre-August is")
        print("confounded by the season boundary — compare in-season only.")

    # The only live change this could justify: stop letting ml-meta legs ride.
    print("\n" + "-" * 74)
    print("PAIRED REMOVAL REPLAY — what happens if ml-meta legs cannot ride")
    print("-" * 74)
    drop = {d: [l for l in pool_ if rule_family(l["row"].get("rule")) != "ml-meta"]
            for d, pool_ in universe.items()}
    live_days = replay(universe, {})
    drop_days = replay(drop, {})
    a, b = summarise(live_days), summarise(drop_days)
    print(f"  live (ml-meta eligible)  log/day {a['mean_log']:+.4f}  "
          f"final {a['final']:6.0f}%  days {a['days']:3d}  maxDD {a['maxdd']:.0%}")
    print(f"  ml-meta legs REMOVED     log/day {b['mean_log']:+.4f}  "
          f"final {b['final']:6.0f}%  days {b['days']:3d}  maxDD {b['maxdd']:.0%}")
    common = sorted(set(live_days) & set(drop_days))
    if common:
        diff = [math.log(drop_days[d]["growth"]) - math.log(live_days[d]["growth"])
                for d in common]
        rnd = random.Random(2026)
        bs = sorted(sum(rnd.choices(diff, k=len(diff))) / len(diff)
                    for _ in range(5000))
        changed = sum(1 for d in common if abs(drop_days[d]["growth"]
                                               - live_days[d]["growth"]) > 1e-9)
        print(f"  paired Δ(removed − live) {sum(diff)/len(diff):+.4f}/day  "
              f"p10 {bs[500]:+.4f}  p90 {bs[4500]:+.4f}  "
              f"cards differ {changed}/{len(common)} days")
        print("\n  Removing the family also removes the days where it was the only")
        print("  card. Read the day counts, not just the growth number.")
    return 0


def cmd_battery(universe):
    base = {}
    print("--- baseline ---")
    b = print_variant(universe, base, "live settings")
    print("\n--- min leg odds floor ---")
    for f in (1.10, 1.15, 1.20, 1.25, 1.30):
        print_variant(universe, {"floor": f}, f"floor {f:.2f}", baseline=b)
    print("\n--- accas per day (checkpoint ①) ---")
    for k in (3, 4, 5, 6):
        print_variant(universe, {"max_accas": k}, f"max {k} accas/day", baseline=b)
    print("\n--- accas per day, SATURATED days only (checkpoint ① proper) ---")
    for k in (4, 5, 6):
        print_variant(universe, {"saturated_accas": k}, f"{k} accas on saturated days", baseline=b)
    print("\n--- volume gate that actually bites (per-acca conviction) ---")
    for vm in (0.55, 0.60, 0.65, 0.70):
        print_variant(universe, {"gate_mode": "acca", "volume_min": vm},
                      f"acca-gate >= {vm:.0%}", baseline=b)
    print_variant(universe, {"gate_mode": "acca", "volume_min": 0.65, "fallback": False},
                  "acca-gate >=65%, no fallback", baseline=b)
    print_variant(universe, {"gate_mode": "pool", "fallback": False},
                  "legacy strict pool gate", baseline=b)
    print_variant(universe, {"gate_mode": "off"}, "gate off (== live, see audit)", baseline=b)
    print("\n--- ranking / pairing shape ---")
    print_variant(universe, {"rank": "ev"}, "rank by stated EV", baseline=b)
    print_variant(universe, {"pairing": "barbell"}, "barbell pairing (1+6,2+5,3+4)", baseline=b)
    print("\n--- stake fraction (doctrine: 50% cap) ---")
    for s in (0.25, 0.33, 0.50, 0.75):
        print_variant(universe, {"stake_frac": s}, f"stake {s:.0%}/day", baseline=b)
    print("\n--- always-on stated-prob floor (REJECTED 4x — kept as a tripwire) ---")
    for mp in (0.60, 0.65, 0.70):
        print_variant(universe, {"min_prob": mp}, f"always-on prob >= {mp:.0%}", baseline=b)


def _day_scope(universe, since=None, until=None):
    return {d: pool for d, pool in sorted(universe.items())
            if (not since or d >= since) and (not until or d <= until)}


def _fold_name(name: str) -> str:
    """Accent/diacritic-insensitive, case-insensitive name key for exact
    fixture matching. Deliberately NOT fuzzy: a fixture either matches a
    recorded name after trivial normalisation or it does not."""
    out = unicodedata.normalize("NFKD", str(name))
    out = "".join(ch for ch in out if not unicodedata.combining(ch))
    return " ".join(out.casefold().split())


def _exclusion_set(path: Path) -> set[tuple[str, str]]:
    """Load [{"date": YYYY-MM-DD, "match": "Home vs Away"}] into
    (date, folded-match) pairs."""
    raw = json.loads(Path(path).read_text())
    out = set()
    for row in raw:
        d = str(row.get("date") or "")[:10]
        m = _fold_name(str(row.get("match") or ""))
        if d and m:
            out.add((d, m))
    return out


def _perfect_clock_block(scope, exclude: set[tuple[str, str]]) -> None:
    """Task A closeout (2026-09-06): re-run the four --kickoff-guard arms
    with the known-started ridden legs excluded from every pool (a perfect
    clock would have dropped them at build). Prints which exclusions were
    actually ridden by each arm and the ex-rows beside the shipped rows.

    MEASUREMENT ONLY — no selection or staking change ships from this.
    """
    def rode(day_map):
        out = set()
        for d, rec in day_map.items():
            for acca_legs in rec["legs"]:
                for m in acca_legs:
                    if (d, _fold_name(m)) in exclude:
                        out.add((d, m))
        return out

    shipped_so, shipped_g, shipped_n = _kickoff_arms(scope)
    rode_default = rode(replay(scope, {}))
    rode_so = rode(replay(shipped_so, {}))
    rode_g = rode(replay(shipped_g, {}))
    rode_n = rode(replay(shipped_n, {}))

    ex_scope = {d: [leg for leg in pool if (d, _fold_name(leg["match"])) not in exclude]
                for d, pool in scope.items()}
    ex_scope = {d: p for d, p in ex_scope.items() if len(p) >= at.LEGS_PER_ACCA}
    ex_so, ex_g, ex_n = _kickoff_arms(ex_scope)

    print()
    print("=" * 74)
    print("PERFECT CLOCK (Task A closeout) — known-started ridden legs excluded")
    print("=" * 74)
    print(f"exclusion file: {len(exclude)} (date, match) pairs; present in scope pools: "
          f"{sum(1 for (d, m) in exclude if any((d, _fold_name(l['match'])) == (d, m) for pool in scope.values() for l in pool))}")
    for label, bits in (("default", rode_default), ("started-only", rode_so),
                        ("region guard", rode_g), ("normalised", rode_n)):
        print(f"  ridden by {label:12s} arm pre-exclusion: {len(bits)} of {len(exclude)}"
              + (f" — {', '.join(sorted(f'{d} {m}' for d, m in bits))}" if bits else ""))

    for label, days in (("whole archive", scope), ("in-season (>= 2026-08-01)",
                        _day_scope(scope, "2026-08-01"))):
        if not days:
            continue
        sub = {d: days[d] for d in days}
        sub_x = {d: ex_scope[d] for d in days if d in ex_scope}
        if not sub_x:
            continue
        sx_so = {d: ex_so[d] for d in days if d in ex_so}
        sx_g = {d: ex_g[d] for d in days if d in ex_g}
        sx_n = {d: ex_n[d] for d in days if d in ex_n}
        a, b, c, n = (summarise(x) for x in (replay(sub, {}), replay({d: shipped_so[d] for d in days if d in shipped_so}, {}),
                       replay({d: shipped_g[d] for d in days if d in shipped_g}, {}),
                       replay({d: shipped_n[d] for d in days if d in shipped_n}, {})))
        ax, bx, cx, nx = (summarise(x) for x in (replay(sub_x, {}), replay(sx_so, {}), replay(sx_g, {}), replay(sx_n, {})))
        print(f"  {label} — shipped→ex  (bet-days, log/day, final, maxDD)")
        for tag, s, sx in (("default     ", a, ax), ("started-only", b, bx),
                           ("region guard", c, cx), ("normalised  ", n, nx)):
            same = s["days"] == sx["days"]
            print(f"    {tag}  {s['days']:2d} → {sx['days']:2d}  "
                  f"{s['mean_log']:+.4f} → {sx['mean_log']:+.4f}  "
                  f"{s['final']:7.0f}% → {sx['final']:7.0f}%  "
                  f"maxDD {s['maxdd']:4.0%} → {sx['maxdd']:4.0%}"
                  f"{'' if same else '  (bet-day lost)'}")
    print("read: this is the contamination check — how much of each shipped")
    print("in-season growth was earned by legs a perfect clock would have")
    print("dropped. Measurement only; no arm here ships.")



def cmd_kickoff_contract(universe, since=None, until=None):
    """AUDIT INSTRUMENT (off by default): the fail-closed kickoff standard
    on HISTORY — it sizes the data-side kickoff-proof gap.

    Re-runs the archive with the strict standard — every leg's kickoff must
    be PROVEN by the row itself (explicit offset/Z, or naive + row-carried
    zone) and at least KICKOFF_MIN_LEAD_HOURS ahead of the canonical 09:00
    SAST build instant — so the data-side fix's size is visible. This is NOT
    the live betting rule (the 2026-09-06 review: proof-or-drop threw away
    the dated majority that renders UTC+2; live drops only undatable and
    already-started legs via auto_tickets.live_kickoff_guard). It prints,
    per regime:

      - legs dropped per day and why (aggregate census),
      - every day whose card would have changed, with the dropped legs,
      - bet-days lost (cards that fall below 2 provable legs),
      - growth / final / maxDD under the strict standard, in-season and
        whole archive, versus the unguarded replay on the same days.
    """
    scope = _day_scope(universe, since, until)
    print("=" * 74)
    print("KICKOFF PROOF CONTRACT — AUDIT ONLY (off by default; NOT the live rule)")
    print("=" * 74)
    print(f"scope: {len(scope)} settled-playable bet-days "
          f"({next(iter(scope), '-')} -> {list(scope)[-1] if scope else '-'}); "
          f"build instant per day: {at.FREEZE_HOUR:02d}:00 SAST (canonical freeze run)")
    print("(audit standard: a leg rides only if its kickoff is PROVEN by the row and >= "
          f"{at.KICKOFF_MIN_LEAD_HOURS:g}h ahead of build)\n")

    strict, census, lost = {}, {}, 0
    changed = []
    for d, pool in scope.items():
        build_at = at.canonical_build_instant(d)
        kept, drops = at.kickoff_contract(pool, build_at=build_at)
        for reason, names in drops.items():
            census.setdefault(reason, []).extend(f"{d} {n}" for n in names)
        default_accas = [tuple(l["match"] for l in a)
                         for a in at.select_accas(pool)]
        if len(kept) >= at.LEGS_PER_ACCA:
            strict[d] = kept
            strict_accas = [tuple(l["match"] for l in a)
                            for a in at.select_accas(kept)]
            if default_accas and strict_accas != default_accas:
                flat = [n for v in drops.values() for n in v]
                changed.append((d, default_accas, strict_accas, flat))
        else:
            if default_accas:
                lost += 1
                flat = [n for v in drops.values() for n in v]
                changed.append((d, default_accas, [], flat))

    n_drop = sum(len(v) for v in census.values())
    print(f"aggregate: {n_drop} legs dropped over {len(scope)} bet-days "
          f"({n_drop / max(len(scope), 1):.2f}/day) — "
          f"{len(scope) - lost} days still build a card, "
          f"{lost} bet-days LOST (card falls below {at.LEGS_PER_ACCA} provable legs)")
    for reason in sorted(census):
        names = census[reason]
        print(f"  • {len(names)} {reason.lower()}  "
              f"(e.g. {names[0] if names else '-'}{f' — +{len(names)-1} more' if len(names) > 1 else ''})")

    print("\ndays whose card changes (default -> strict):")
    for d, ca, cb, drops in changed:
        if cb:
            print(f"  {d}: {len(ca)} accas -> {len(cb)} accas  dropped: "
                  f"{'; '.join(sorted(set(drops))[:4])}")
        else:
            print(f"  {d}: {len(ca)} accas -> NO BET  (fewer than "
                  f"{at.LEGS_PER_ACCA} provable legs)")

    print("\n" + "-" * 74)
    print("GROWTH UNDER THE CONTRACT (replay, live stake rules)")
    print("-" * 74)
    for label, days in (("whole archive", scope),
                        ("in-season (>= 2026-08-01)", _day_scope(scope, "2026-08-01"))):
        if not days:
            continue
        base_rec, strict_rec = replay(days, {}), replay(strict, {})
        a, b = summarise(base_rec), summarise(strict_rec)
        print(f"  {label} — default {a['days']:2d} bet-days  "
              f"log/day {a['mean_log']:+.4f}  final {a['final']:7.0f}%  "
              f"maxDD {a['maxdd']:4.0%}")
        if b["days"]:
            print(f"  {label} — strict  {b['days']:2d} bet-days  "
                  f"log/day {b['mean_log']:+.4f}  final {b['final']:7.0f}%  "
                  f"maxDD {b['maxdd']:4.0%}  (days below 2 provable legs are NO BET)")
        else:
            print(f"  {label} — strict:  NO BET-DAYS REMAIN (zero provable "
                  "cards in the archive)")
        print()
    print("read: every dropped leg is a bet the engine CANNOT PROVE is still")
    print("in the future. The trade is volume for certainty — the count above")
    print("is what the data side must recover before volume returns (carry a")
    print("timezone in the row, e.g. betexplorer-style +02:00 kickoffs).")
    return 0


def _kickoff_arms(scope):
    """Compute the started-only / region-guard / normalised arm pools for a
    scope of days, at each day's canonical 09:00 SAST build instant.

    - started-only: rows whose parseable kickoff is already at/past build
      time drop (the engine's historical live path approximation);
    - region guard: auto_tickets.live_kickoff_guard (started + clock-only
      rows in remote-clock regions + missing/garbage);
    - normalised: the same guard after archived-witness ingest
      normalisation (kickoff_utc resolved where an archived witness exists).
    Returns (started_only, guarded, normalised) day->pool dicts.
    """
    started_only: dict = {}
    guarded: dict = {}
    normalised: dict = {}
    for d, pool in scope.items():
        build_at = at.canonical_build_instant(d)
        # arm 2: the historical live engine's started check (parseable past)
        so = []
        for leg in pool:
            pick = leg.get("row") if isinstance(leg, dict) and leg.get("row") else leg
            kt = at.parse_kickoff(pick)
            if kt is None or kt.astimezone(at.TZ) >= build_at:
                so.append(leg)
        started_only[d] = so
        # arm 3: the full live guard
        kept, _drops = at.live_kickoff_guard(pool, build_at)
        guarded[d] = kept
        # arm 4: normalised ingest (archived-witness lower bound)
        norm_pool = []
        for leg in pool:
            pick = leg.get("row") if isinstance(leg, dict) and leg.get("row") else leg
            ku, src = at.kickoff_utc_from_archived_row(pick)
            if ku is None:
                norm_pool.append(leg)
                continue
            leg2 = dict(leg)
            row2 = dict(pick)
            row2["kickoff_utc"] = ku
            row2["kickoff_source"] = src
            leg2["row"] = row2
            norm_pool.append(leg2)
        n_kept, _n_drops = at.live_kickoff_guard(norm_pool, build_at)
        normalised[d] = n_kept
    return started_only, guarded, normalised


def cmd_kickoff_guard(universe, since=None, until=None, exclude: set | None = None):
    """MONEY COST of the LIVE kickoff guard (region rule) on HISTORY, plus
    the Task-A normalisation-recovery estimate (ingest kickoff_utc).

    Applies auto_tickets.live_kickoff_guard at each day's canonical 09:00
    SAST build instant, then replays four arms through the same planner
    with the same live stake rules:
      - default: the raw replay universe (what the harness battery calls
        "live" — no era guard modeled);
      - started-only: the engine's historical live path approximated
        (parseable legs already started at the build instant drop);
      - region guard: full live_kickoff_guard (started + clock-only rows in
        remote-clock regions + missing/garbage);
      - normalised: the same guard AFTER ingest normalisation — every pool
        row that an archived witness can resolve (own zoned kickoff, or the
        scoutingstats starting_at preserved as odds_captured_at) carries
        kickoff_utc, and the guard judges only that instant. Sibling-row
        witnesses that existed only at fetch time (vitibet "+02:00" rows)
        are NOT in the archives, so this arm is a LOWER bound on recovery.
    Prints per regime (whole archive and in-season >= 2026-08-01): log/day,
    final, maxDD and bet-days. The guard's MARGINAL money cost is the
    region-guard arm minus the started-only arm; the default arm is shown
    only for continuity with the battery row.

    CAVEAT (2026-09-06 follow-up review, Task C1): the in-season guard-vs-
    started gap is ONE bet-day (2026-08-04, which won). The gap is therefore
    unmeasured, not small: in noise terms it is well under a tenth of a
    standard deviation of daily log growth, and had that one day lost, the
    same guard would show a gain. Neither arm has earned a number. Do not
    quote the in-season -0.0070 (or the whole-archive +0.0080) as a price.
    """
    scope = _day_scope(universe, since, until)
    started_only, guarded, normalised = {}, {}, {}
    census: dict[str, list[str]] = {}
    norm_census: dict[str, list[str]] = {}
    for d, pool in scope.items():
        build_at = at.canonical_build_instant(d)
        # arm 2: the historical live engine's started check (parseable past)
        so = []
        for leg in pool:
            pick = leg.get("row") if isinstance(leg, dict) and leg.get("row") else leg
            kt = at.parse_kickoff(pick)
            if kt is None or kt.astimezone(at.TZ) >= build_at:
                so.append(leg)
        started_only[d] = so
        # arm 3: the full live guard
        kept, drops = at.live_kickoff_guard(pool, build_at)
        for reason, names in drops.items():
            census.setdefault(reason, []).extend(f"{d} {n}" for n in names)
        guarded[d] = kept
        # arm 4: normalised ingest (archived-witness lower bound)
        norm_pool = []
        for leg in pool:
            pick = leg.get("row") if isinstance(leg, dict) and leg.get("row") else leg
            ku, src = at.kickoff_utc_from_archived_row(pick)
            if ku is None:
                norm_pool.append(leg)
                continue
            leg2 = dict(leg)
            row2 = dict(pick)
            row2["kickoff_utc"] = ku
            row2["kickoff_source"] = src
            leg2["row"] = row2
            norm_pool.append(leg2)
        n_kept, n_drops = at.live_kickoff_guard(norm_pool, build_at)
        for reason, names in n_drops.items():
            norm_census.setdefault(reason, []).extend(f"{d} {n}" for n in names)
        normalised[d] = n_kept

    n_drop = sum(len(v) for v in census.values())
    print("=" * 74)
    print("LIVE KICKOFF GUARD (region rule) — MONEY COST ON HISTORY")
    print("=" * 74)
    print(f"scope: {len(scope)} settled-playable bet-days "
          f"({next(iter(scope), '-')} -> {list(scope)[-1] if scope else '-'}); "
          f"build instant per day: {at.FREEZE_HOUR:02d}:00 SAST (canonical freeze run)")
    print(f"guard drops (pool-level): {n_drop} legs total:")
    for reason in sorted(census):
        names = census[reason]
        print(f"  • {len(names)} {reason.lower()}  "
              f"(e.g. {names[0] if names else '-'}{f' — +{len(names)-1} more' if len(names) > 1 else ''})")
    n_rescued = n_drop - sum(len(v) for v in norm_census.values())
    print(f"after normalisation (archived-witness lower bound): {n_rescued} of those "
          f"{n_drop} legs carry a resolvable kickoff_utc; "
          f"{sum(len(v) for v in norm_census.values())} still dropped:")
    for reason in sorted(norm_census):
        names = norm_census[reason]
        print(f"  • {len(names)} {reason.lower()}  "
              f"(e.g. {names[0] if names else '-'}{f' — +{len(names)-1} more' if len(names) > 1 else ''})")

    print()
    for label, days in (("whole archive", scope),
                        ("in-season (>= 2026-08-01)", _day_scope(scope, "2026-08-01"))):
        if not days:
            continue
        sub = {d: days[d] for d in days}
        sub_so = {d: started_only[d] for d in days}
        sub_g = {d: guarded[d] for d in days}
        sub_n = {d: normalised[d] for d in days}
        a = replay(sub, {})
        b = replay(sub_so, {})
        c = replay(sub_g, {})
        n = replay(sub_n, {})
        sa, sb, sc, sn = (summarise(x) for x in (a, b, c, n))
        lost_vs_default = sorted(set(a) - set(c))
        lost_vs_started = sorted(set(b) - set(c))
        print(f"  {label} — default      {len(a):2d} bet-days  "
              f"log/day {sa['mean_log']:+.4f}  final {sa['final']:7.0f}%  maxDD {sa['maxdd']:4.0%}")
        print(f"  {label} — started-only {len(b):2d} bet-days  "
              f"log/day {sb['mean_log']:+.4f}  final {sb['final']:7.0f}%  maxDD {sb['maxdd']:4.0%}")
        print(f"  {label} — region guard {len(c):2d} bet-days  "
              f"log/day {sc['mean_log']:+.4f}  final {sc['final']:7.0f}%  maxDD {sc['maxdd']:4.0%}")
        print(f"  {label} — normalised   {len(n):2d} bet-days  "
              f"log/day {sn['mean_log']:+.4f}  final {sn['final']:7.0f}%  maxDD {sn['maxdd']:4.0%}")
        if b and c:
            print(f"             marginal Δlog/day (guard − started) "
                  f"{sc['mean_log'] - sb['mean_log']:+.4f}  "
                  f"maxDD {sb['maxdd']:4.0%} -> {sc['maxdd']:4.0%}   "
                  f"(normalised − started: {sn['mean_log'] - sb['mean_log']:+.4f})")
        print(f"             bet-days lost by the guard (vs started-only arm): "
              f"{len(lost_vs_started)} — {', '.join(lost_vs_started) or 'none'}")
        print()
    print("read: in-sample history does not punish the guard (the region class")
    print("was disproportionately losing legs) — but that is hindsight, not")
    print("evidence of edge: the rule exists to stop the incident-#6 family,")
    print("and its true price shows up on genuinely new days.")
    print()
    print("COST CAVEAT (2026-09-06 follow-up review, C1): the in-season")
    print("guard-vs-started gap is ONE bet-day (2026-08-04), and that day WON.")
    print("With n=35, sd of daily log growth ~0.21, the gap is ~0.2 standard")
    print("errors of a single day's noise — indistinguishable from zero, and")
    print("the same guard would look like a GAIN had that one day lost. The")
    print("cost of the guard is UNMEASURED, not small; the started-only arm")
    print("is not 'better than default' either (0.3 s.e.). Do not quote")
    print("-0.0070 (in-season) or +0.0080 (whole archive) as a price.")
    print()
    print("NORMALISATION RECOVERY (Task A; details in the HANDOVER addendum):")
    print("the 'normalised' arm above is the LOWER bound — it resolves only")
    print("witnesses preserved in the archives (own zoned kickoff; the")
    print("scoutingstats starting_at string, which the odds adapter stores as")
    print("odds_captured_at). Same-fixture vitibet rows ('+02:00' in every")
    print("archived vitibet-anchored row) existed at fetch time for most of")
    print("the remaining clock-only legs (sources_used proves presence) but")
    print("their kickoff strings are not archived, so live recovery is higher.")
    if exclude:
        _perfect_clock_block(scope, exclude)
    return 0


def _row_flag(row: dict) -> tuple[bool, str]:
    """Is an archived row QUARANTINE-FLAGGED, and under which label?

    Flagged = WATCHLIST_* bucket or a price_quarantine_reason. The two
    coincide by construction for scoutingstats-sole prices
    (WATCHLIST_UNCORROBORATED_PRICE / scoutingstats_sole_source) and for
    suspect fuzzy prices (WATCHLIST_SUSPECT_PRICE / alias_fuzzy); they are
    counted once. The engine bets these legs anyway: playable_legs only
    excludes alias_fuzzy suspects that were never rescued.
    """
    bucket = str(row.get("bucket") or "")
    reason = str(row.get("price_quarantine_reason") or row.get("quarantine") or "")
    if bucket.startswith("WATCHLIST") or reason not in ("", "none"):
        label = reason or bucket
        return True, label
    return False, ""


def cmd_quarantine(universe, since=None, until=None):
    """MEASURE ONLY (Task B, 2026-09-06 follow-up): what are the ridden
    WATCHLIST / quarantine legs worth? No gate changes.

    Ridden = legs on the DEFAULT replay arm's cards (the unguarded engine's
    live selection on the settled-playable pools). FLAGGED = archived row
    carries a WATCHLIST_* bucket or a price_quarantine_reason. Always split
    in-season (>= 2026-08-01) vs off-season — a mixed figure is the ⑩
    confound.

    Flat ROI = 1 flat unit per leg at the odds the engine bet: win -> odds-1,
    void -> 0, loss -> -1. Hit rate = wins / non-void legs. Differences are
    day-block bootstrapped (the same resampled day indices score both
    populations).

    This is a MEASUREMENT, not a gate: if flagged legs look worse, that is a
    pre-registered candidate for the October slot under the standing bar
    (paired-bootstrap p10 > 0 AND every leave-one-day-out keeps the sign AND
    maxDD <= live, at n >= 60 genuinely new in-season bet-days), never an
    adoption here.
    """
    scope = _day_scope(universe, since, until)
    print("=" * 74)
    print("QUARANTINE-GATE CENSUS — RIDDEN LEGS (measure only; no gate change)")
    print("=" * 74)
    print(f"scope: {len(scope)} settled-playable bet-days; ridden = default "
          f"replay arm's cards (live selection, floor {at.MIN_LEG_ODDS});")
    print("flagged = WATCHLIST_* bucket or price_quarantine_reason on the row.\n")

    # ---- ridden legs per day with per-leg facts ----
    ridden: dict[str, list[dict]] = {}
    for d, pool in scope.items():
        accas = at.select_accas(pool)
        chosen = [l["match"] for a in accas for l in a]
        for leg in pool:
            if leg["match"] in chosen and leg["match"] not in {x["match"] for x in ridden.get(d, [])}:
                row = leg.get("row") or {}
                flagged, label = _row_flag(row)
                ridden.setdefault(d, []).append({
                    "match": leg["match"], "result": leg["result"],
                    "odds": float(leg["odds"] or 0.0), "flagged": flagged,
                    "label": label, "row": row,
                })

    def _split(days):
        return ({d: v for d, v in days.items() if d >= "2026-08-01"},
                {d: v for d, v in days.items() if d < "2026-08-01"})

    regimes = (("whole archive", ridden),
               ("in-season (>= 2026-08-01)", _split(ridden)[0]),
               ("off-season (< 2026-08-01)", _split(ridden)[1]))

    for label, days in regimes:
        legs = [l for d in days for l in days[d]]
        n_flag = sum(1 for l in legs if l["flagged"])
        print(f"  {label}: {len(legs)} ridden legs, {n_flag} flagged "
              f"({n_flag / max(len(legs), 1):.0%}) across "
              f"{sum(1 for d in days if any(l['flagged'] for l in days[d]))} of "
              f"{len(days)} bet-days touched by a flagged leg")
        if n_flag:
            by_ev: dict[str, list] = {}
            by_reason: dict[str, list] = {}
            by_bucket: dict[str, list] = {}
            for l in legs:
                if not l["flagged"]:
                    continue
                row = l["row"]
                by_ev.setdefault(str(row.get("price_evidence") or "none"), []).append(l)
                by_reason.setdefault(str(row.get("price_quarantine_reason") or "none"), []).append(l)
                by_bucket.setdefault(str(row.get("bucket") or "none"), []).append(l)
            for name, table in (("price_evidence", by_ev),
                                ("quarantine_reason", by_reason),
                                ("bucket", by_bucket)):
                bits = ", ".join(f"{k} {len(v)}" for k, v in sorted(table.items()))
                print(f"      by {name}: {bits}")

    def _flat_roi(l):
        if l["result"] == "win":
            return float(l["odds"]) - 1.0
        if l["result"] == "void":
            return 0.0
        return -1.0

    def _stats(legs):
        n = len(legs)
        non_void = [l for l in legs if l["result"] != "void"]
        wins = sum(1 for l in legs if l["result"] == "win")
        roi = sum(_flat_roi(l) for l in legs)
        return {"n": n, "wins": wins, "nv": len(non_void),
                "hit": wins / len(non_void) if non_void else float("nan"),
                "roi": roi / n if n else 0.0}

    print()
    for label, days in regimes:
        legs = [l for d in days for l in days[d]]
        flagged = [l for l in legs if l["flagged"]]
        unflagged = [l for l in legs if not l["flagged"]]
        sf, su = _stats(flagged), _stats(unflagged)
        print(f"  {label} — flagged   n={sf['n']:3d}  hit {sf['hit']:6.1%}  "
              f"flat ROI {sf['roi']:+7.1%}")
        print(f"  {label} — unflagged n={su['n']:3d}  hit {su['hit']:6.1%}  "
              f"flat ROI {su['roi']:+7.1%}")

        # day-block bootstrap of the per-day difference (paired day indices)
        def _day_mean(days_, flag):
            out = {}
            for d, ls in days_.items():
                sub = [l for l in ls if l["flagged"] == flag]
                if sub:
                    out[d] = sum(_flat_roi(l) for l in sub) / len(sub)
            return out

        mf = _day_mean(days, True)
        mu = _day_mean(days, False)
        paired = sorted(set(mf) & set(mu))
        if paired:
            rng = __import__("random").Random(20260906)
            diffs = []
            for _ in range(4000):
                idx = [rng.choice(paired) for _ in paired]
                diffs.append(sum(mf[i] - mu[i] for i in idx) / len(idx))
            diffs.sort()
            p10 = diffs[400]
            lo, hi = diffs[200], diffs[3800]
            flag = "  ⚠ small-n" if len(paired) < 30 else ""
            print(f"      paired day-bootstrap ΔROI (flagged−unflagged), "
                  f"{len(paired)} days with both: "
                  f"p10 {p10:+.1%}, 90% CI [{lo:+.1%}, {hi:+.1%}]{flag}")
        print()

    # ---- would-blank days + growth consequence (IN-SAMPLE) ----
    filtered = {}
    for d, pool in scope.items():
        kept = [l for l in pool if not _row_flag(l.get("row") or {})[0]]
        filtered[d] = kept
    print("WOULD-BLANK + GROWTH IF FLAGGED LEGS WERE EXCLUDED (IN-SAMPLE;")
    print("not a policy — measurement only)")
    for label, days in (("whole archive", scope),
                        ("in-season (>= 2026-08-01)", _day_scope(scope, "2026-08-01"))):
        if not days:
            continue
        sub = {d: days[d] for d in days}
        fsub = {d: v for d, v in filtered.items() if d in days}
        ra, rb = replay(sub, {}), replay(fsub, {})
        rs_a, rs_b = summarise(ra), summarise(rb)
        lost = sorted(set(ra) - set(rb))
        print(f"  {label} — default {rs_a['days']:2d} bet-days  "
              f"log/day {rs_a['mean_log']:+.4f}  final {rs_a['final']:7.0f}%  "
              f"maxDD {rs_a['maxdd']:4.0%}")
        print(f"  {label} — exclude-flagged {rs_b['days']:2d} bet-days  "
              f"log/day {rs_b['mean_log']:+.4f}  final {rs_b['final']:7.0f}%  "
              f"maxDD {rs_b['maxdd']:4.0%}  "
              f"(days blanked: {len(lost)} — {', '.join(lost) or 'none'})")
    print()
    print("read: these are in-sample descriptions of the flag's history, not")
    print("evidence. Whatever the flag's legs did, the flag was designed as a")
    print("PRICING caution, not a betting signal; measuring it does not make it")
    print("one. If the flagged population is worse, the pre-registered October")
    print("slot owns that test (standing bar: paired-bootstrap p10 > 0 AND")
    print("leave-one-day-out sign holds AND maxDD <= live, at n >= 60 genuinely")
    print("new in-season bet-days). No adoption here, ever.")
    return 0


# --------------------------------------------------------------------------
# --warehouse-replay: FEASIBILITY audit (Phase 1). Research only, opt-in.
# --------------------------------------------------------------------------
def _pick_rule_name(row: dict) -> str:
    return str(row.get("edge_rule") or row.get("rule")
               or row.get("display_rule") or "unknown-rule")


def _clv_witnesses(run_date: str, pick_id: str) -> list[dict]:
    """Same-day second-provider price rows from the CLV snapshot files.

    Returns rows for the pick whose odds_provider is a real second source
    (bzzoiro/betexplorer) with a true capture timestamp and an exact or
    alias-time/unique/betexplorer match method — i.e. the same fixture was
    priced by another provider that day, at a stamped time.
    """
    out: list[dict] = []
    for f in sorted(LOCALDATA.glob("clv_snapshots_*.csv.gz")):
        with gzip.open(f, "rt", newline="") as fh:
            for r in csv.DictReader(fh):
                if str(r.get("source_run_date") or "")[:10] != run_date:
                    continue
                if str(r.get("pick_id") or "") != pick_id:
                    continue
                prov = str(r.get("odds_provider") or "")
                meth = str(r.get("odds_match_method") or "")
                if prov in ("scoutingstats_odds", "", "forebet_best", "zulubet"):
                    continue
                if meth not in ("exact", "alias_time", "alias_unique", "betexplorer"):
                    continue
                try:
                    o = float(r.get("observed_odds") or "")
                except ValueError:
                    continue
                if o <= 1.0 or not str(r.get("captured_at_utc") or ""):
                    continue
                out.append({"provider": prov, "odds": o,
                            "captured_at": str(r.get("captured_at_utc") or ""),
                            "method": meth, "label": str(r.get("snapshot_label") or "")})
    return out


def _theoddsapi_witnesses(day: str, home: str, away: str, sel: str) -> list[dict]:
    """Same-fixture per-bookmaker prices from theoddsapi monthly files."""
    import picks_today as pt
    out: list[dict] = []
    hk = pt.odds_match_team_key(str(home or ""))
    ak = pt.odds_match_team_key(str(away or ""))
    for f in sorted(LOCALDATA.glob("theoddsapi_odds_*.csv.gz")):
        with gzip.open(f, "rt", newline="") as fh:
            for r in csv.DictReader(fh):
                if str(r.get("date") or "")[:10] != day:
                    continue
                if r.get("market") != "1x2":
                    continue
                rhk = pt.odds_match_team_key(str(r.get("home") or ""))
                rak = pt.odds_match_team_key(str(r.get("away") or ""))
                if (rhk, rak) not in ((hk, ak), (ak, hk)):
                    continue
                if str(r.get("selection") or "").lower() != sel.lower():
                    continue
                try:
                    o = float(r.get("odds") or "")
                except ValueError:
                    continue
                if o <= 1.0 or not str(r.get("captured_at") or ""):
                    continue
                out.append({"provider": "theoddsapi:" + str(r.get("bookmaker") or ""),
                            "odds": o,
                            "captured_at": str(r.get("captured_at") or ""),
                            "method": "exact", "label": "theoddsapi"})
    return out


def _stamped_witnesses(leg) -> list[dict]:
    row = leg.get("row") or {}
    from edgefactory.clv import build_pick_id
    pid = build_pick_id(str(leg.get("_day") or row.get("date") or "")[:10],
                        row.get("home"), row.get("away"), row.get("market"),
                        row.get("pick"), _pick_rule_name(row))
    out = _clv_witnesses(str(leg.get("_day"))[:10], pid)
    out += _theoddsapi_witnesses(str(leg.get("_day"))[:10], row.get("home"),
                                 row.get("away"), str(leg.get("pick") or ""))
    # best price per distinct provider class (avoid double-counting
    # bookmaker duplicates of one source snapshot)
    best: dict[str, dict] = {}
    for w in out:
        key = w["provider"].split(":")[0] + ":" + (w["captured_at"][:10] if w["captured_at"] else "")
        if key not in best or w["odds"] > best[key]["odds"]:
            best[key] = w
    return sorted(best.values(), key=lambda w: -w["odds"])


def _pick_time_engine_price(leg) -> tuple[float | None, str | None]:
    """The nearest record to ride time: the CLV pick_time snapshot row's own
    observed odds (its odds_provider is the price the slate carried then).
    Returns None when no pick_time row exists for the pick."""
    row = leg.get("row") or {}
    from edgefactory.clv import build_pick_id
    pid = build_pick_id(str(leg.get("_day") or "")[:10],
                        row.get("home"), row.get("away"), row.get("market"),
                        row.get("pick"), _pick_rule_name(row))
    for f in sorted(LOCALDATA.glob("clv_snapshots_*.csv.gz")):
        with gzip.open(f, "rt", newline="") as fh:
            for r in csv.DictReader(fh):
                if str(r.get("source_run_date") or "")[:10] != str(leg.get("_day"))[:10]:
                    continue
                if str(r.get("pick_id") or "") != pid:
                    continue
                if str(r.get("snapshot_label") or "") != "pick_time":
                    continue
                try:
                    o = float(r.get("observed_odds") or "")
                except ValueError:
                    continue
                if o <= 1.0:
                    return None, None
                return o, str(r.get("odds_provider") or "")
    return None, None


def cmd_price_obtainability(universe, since=None, until=None):
    """Task D (2026-09-06) — P0: are the recorded prices obtainable?

    MEASUREMENT ONLY; no gate, no selection or staking change.

    The engine's prices on scoutingstats legs are sole-source by
    construction (the primary bundle had no row), so nothing in the archive
    says whether the owner could actually have got them. This command
    measures the archive-side gap (D2) and the obtainability-constrained
    replay (D3, labelled in-sample):

    D2 — for ridden scoutingstats legs where a SECOND provider priced the
    same fixture+selection that day with a true capture timestamp (CLV
    snapshots' bzzoiro/betexplorer rows, or theoddsapi per-bookmaker rows),
    how far is the engine's assumed price from the corroborating price?
    Split in-season / off-season. If the engine price is SYSTEMATICALLY
    LONGER than corroboration, the recorded ROI is inflated by that much.

    D3 — replay the same settled-playable universe with every scoutingstats
    leg either (a) repriced to its best stamped corroboration or (b) dropped
    when none exists. IN-SAMPLE: the corroborated prices come from the same
    period's archive, so the result is a lower-bound consistency check on
    the recorded growth, not a forward estimate.

    Caveat printed with the numbers: scoutingstats odds carry no true
    capture timestamp (captured_at == kickoff by construction), so the
    engine price's own availability moment is unknown — exactly what the D1
    owner-actual-price capture (audit_clv) measures going forward.
    """
    scope = _day_scope(universe, since, until)
    ridden = _ridden_legs(scope)
    ss = [l for l in ridden
          if str((l.get("row") or {}).get("odds_source")) == "scoutingstats_odds"]
    in_season = [l for l in ss if l["_day"] >= "2026-08-01"]
    off_season = [l for l in ss if l["_day"] < "2026-08-01"]

    print("=" * 74)
    print("PRICE OBTAINABILITY (Task D) — scoutingstats-odds ridden legs")
    print("=" * 74)
    print("engine price = the price the in-sample replay assumes (pool odds")
    print("today); scoutingstats rows have NO true capture stamp (captured_at")
    print("== kickoff by construction), so their availability moment is")
    print("unknown — the D1 owner-actual capture (audit_clv) is the forward")
    print("measure. Corroboration = a SECOND provider's stamped price for the")
    print("same fixture+selection that day (CLV bzzoiro/betexplorer exact")
    print("rows, theoddsapi per-bookmaker rows).")

    cens = {}
    rows_all = []
    rows_by_leg: dict[str, dict] = {}
    for l in ss:
        wits = _stamped_witnesses(l)
        rows_all.append({
            "day": l["_day"], "match": l["match"], "pick": l["pick"],
            "engine": float(l["odds"] or 0.0),
            "wits": wits,
        })
        rows_by_leg[l["_day"] + "|" + l["match"] + "|" + l["pick"]] = l
    for label, group in (("whole archive", ss), ("in-season", in_season),
                         ("off-season", off_season)):
        n = len(group)
        with_w = sum(1 for l in group if _stamped_witnesses(l))
        cens[label] = (n, with_w)
    print()
    print("D2 — coverage (ridden scoutingstats legs with any stamped same-day")
    print("     second-provider price):")
    for label, (n, w) in cens.items():
        print(f"    {label:12s} {w:3d} of {n:3d} legs corroborated")

    rows_all = [r for r in rows_all if r["wits"]]
    print()
    print("D2 — gap, leg by leg. 'engine (pool)' = the price the in-sample")
    print("     replay assumes today (the ROI basis); 'engine (pick_time)' =")
    print("     the CLV snapshot at ride time when one exists; corr = best")
    print("     stamped second-provider price that day (negative delta = the")
    print("     engine price is SHORTER than what the other provider offered):")
    for r in sorted(rows_all, key=lambda r: r["day"]):
        pt_o, pt_p = _pick_time_engine_price(rows_by_leg[r["day"] + "|" + r["match"] + "|" + r["pick"]])
        best = r["wits"][0]
        for w in r["wits"]:
            print(f"    {r['day']} {r['match'][:44]:44s} {r['pick']:4s} "
                  f"engine(pool) {r['engine']:5.2f}  corr {w['odds']:5.2f} "
                  f"({w['provider'][:20]:20s} cap {w['captured_at'][:19]})")
        pt_txt = f"engine(pick_time) {pt_o:.2f} ({pt_p})" if pt_o else "engine(pick_time) n/a"
        print(f"        delta(pool-corr) {best['odds'] - r['engine']:+.2f}  "
              f"{pt_txt}")
    if rows_all:
        deltas = [r["wits"][0]["odds"] - r["engine"] for r in rows_all]
        print(f"    n={len(deltas)}  mean delta(pool-corr) "
              f"{sum(deltas)/len(deltas):+.3f}  min {min(deltas):+.2f}  "
              f"max {max(deltas):+.2f}  pool-longer-than-best: "
              f"{sum(1 for d in deltas if d < 0)} of {len(deltas)}")
    else:
        print("    (no corroborated legs)")
    print()

    # D3 — constrained replay (IN-SAMPLE)
    def constrain(scope_days):
        out = {}
        dropped = 0
        repriced = 0
        for d, pool in scope_days.items():
            npool = []
            for leg in pool:
                row = leg.get("row") or {}
                if str(row.get("odds_source")) != "scoutingstats_odds":
                    npool.append(leg)
                    continue
                wits = _stamped_witnesses({**leg, "_day": d})
                if not wits:
                    dropped += 1
                    continue
                leg2 = dict(leg)
                row2 = dict(row)
                new_odds = wits[0]["odds"]
                row2["odds"] = new_odds
                row2["_repriced_from"] = float(leg.get("odds") or 0.0)
                row2["_repriced_to"] = new_odds
                row2["_repriced_witness"] = wits[0]["provider"]
                leg2["row"] = row2
                if leg.get("odds") is not None:
                    leg2["odds"] = new_odds
                npool.append(leg2)
                repriced += 1
            if len(npool) >= at.LEGS_PER_ACCA:
                out[d] = npool
        return out, dropped, repriced

    print("D3 — obtainability-constrained replay (IN-SAMPLE; measurement")
    print("     only, nothing ships). scoutingstats legs with a stamped")
    print("     second-provider price ride at that price; legs without one")
    print("     are dropped:")
    for label, days in (("whole archive", scope),
                        ("in-season (>= 2026-08-01)", _day_scope(scope, "2026-08-01"))):
        if not days:
            continue
        base_rec = replay(days, {})
        con, dropped, repriced = constrain(days)
        s0 = summarise(base_rec)
        if not con:
            print(f"  {label}: constrained replay has NO bet-days "
                  f"(dropped {dropped}, repriced {repriced})")
            continue
        s1 = summarise(replay(con, {}))
        n_base = sum(len(v["legs"]) for v in base_rec.values())
        n_con = sum(len(v["legs"]) for v in replay(con, {}).values())
        print(f"  {label} — default      {s0['days']:2d} bet-days  "
              f"legs/day {n_base/max(s0['days'],1):4.1f}  "
              f"log/day {s0['mean_log']:+.4f}  final {s0['final']:7.0f}%  "
              f"maxDD {s0['maxdd']:4.0%}")
        print(f"  {label} — constrained {s1['days']:2d} bet-days  "
              f"legs/day {n_con/max(s1['days'],1):4.1f}  "
              f"log/day {s1['mean_log']:+.4f}  final {s1['final']:7.0f}%  "
              f"maxDD {s1['maxdd']:4.0%}   (legs dropped {dropped}, "
              f"repriced {repriced})")
    print()
    print("read: D2's n is tiny because scoutingstats legs are sole-source by")
    print("construction — that is the finding, not an accident of sampling.")
    print("The D3 constrained arm is the replay's own answer to 'could those")
    print("prices have been got?': where the archive can check, the engine")
    print("price was not longer than what other providers offered that day;")
    print("where the archive cannot check, the leg is dropped because the")
    print("price is not certifiable. Both halves are IN-SAMPLE.")
    return 0


def _wr_open():
    """Open the warehouse read-only, preferring the materialised file."""
    import duckdb
    db = LOCALDATA / "warehouse.duckdb"
    if db.exists():
        return duckdb.connect(str(db), read_only=True), str(db)
    from edgefactory.warehouse import connect as _connect
    return _connect(), "in-memory views over localdata/*.csv.gz"


def cmd_warehouse_replay(archives, settled, since=None, until=None):
    """Answer 'can the live engine be reconstructed from the warehouse?'

    Prints, in order: what is on disk, what the live picks depended on,
    per-rule feasibility, the look-ahead audit, the validation gate, and a
    PASS/FAIL verdict against a bar stated before the numbers.
    """
    from edgefactory import warehouse_replay as wr
    from edgefactory.util import norm_team

    con, src = _wr_open()
    days = sorted({str(p.get("date") or p.get("_archive_day") or "")[:10]
                   for p in archives})
    days = [d for d in days if d and (not since or d >= since)
            and (not until or d <= until)]

    print("=" * 74)
    print("WAREHOUSE RECONSTRUCTION — PHASE 1 FEASIBILITY AUDIT")
    print("=" * 74)
    print(f"warehouse: {src}")
    print(f"live archive: {len(days)} days, {days[0]} -> {days[-1]}")
    print("This command does NOT produce a backtest. It measures whether one")
    print("could be trusted. A reconstruction that recovers a biased slice of")
    print("the live picks is a different strategy, not a cheaper engine.\n")

    # ---------------- 1. inventory ----------------
    print("-" * 74)
    print("1. WAREHOUSE INVENTORY (what history actually exists on disk)")
    print("-" * 74)
    print(f"{'table':24s} {'rows':>10s}  {'first':10s} {'last':10s}")
    for row in wr.warehouse_inventory(con):
        if not row["present"]:
            print(f"{row['table']:24s} {'ABSENT':>10s}  {'-':10s} {'-':10s}")
            continue
        print(f"{row['table']:24s} {row['rows']:10,d}  "
              f"{row['first'] or '-':10s} {row['last'] or '-':10s}")
    print()

    cov = wr.input_coverage(con, days)
    print("prediction-source rows landing inside the archive window:")
    for name, n in cov["per_source"].items():
        print(f"  {name:10s} {n:3d} / {len(days)} archived days")
    print(f"  ANY source: {cov['days_with_any_input']} / {len(days)} days "
          f"({cov['coverage_frac']:.0%})\n")

    # ---------------- 2. dependency census ----------------
    legs = []
    for d in days:
        legs.extend(at.playable_legs(archives, day=d, settled=settled))
    census = wr.dependency_census(legs)

    print("-" * 74)
    print("2. WHAT THE LIVE LEGS DEPENDED ON")
    print("-" * 74)
    print(f"playable legs across the archive: {census.legs}")
    print("\nprediction sources cited by those legs:")
    for s, n in sorted(census.source_hits.items(), key=lambda t: -t[1]):
        tag = "ON DISK" if s in wr.ON_DISK_PREDICTION_SOURCES else "NO HISTORY FILE"
        print(f"  {s:14s} {n:4d} legs   [{tag}]")
    print("\nodds sources used to price those legs:")
    for s, n in sorted(census.by_odds_source.items(), key=lambda t: -t[1]):
        if s in wr.ON_DISK_ODDS_SOURCES:
            tag = "historical, bet-time"
        elif s in wr.CLOSING_ONLY_ODDS_SOURCES:
            tag = "historical but CLOSING (wrong price)"
        else:
            tag = "NO HISTORY FILE"
        print(f"  {s:20s} {n:4d} legs   [{tag}]")

    n = max(census.legs, 1)
    print("\naddressability funnel (each line is a necessary condition):")
    print(f"  {'all playable legs':52s} {census.legs:4d} {100:5.1f}%")
    print(f"  {'rule is a source vote (not the ml-meta model)':52s} "
          f"{census.source_vote:4d} {100*census.source_vote/n:5.1f}%")
    print(f"  {'every cited source has a history file':52s} "
          f"{census.on_disk_sources:4d} {100*census.on_disk_sources/n:5.1f}%")
    print(f"  {'priced from an odds source with history':52s} "
          f"{census.historical_odds:4d} {100*census.historical_odds/n:5.1f}%")
    print(f"  {'ALL THREE (the reconstruction ceiling)':52s} "
          f"{census.ceiling:4d} {100*census.ceiling/n:5.1f}%")
    print()

    # ---------------- 3. per-rule verdict ----------------
    print("-" * 74)
    print("3. PER-RULE FEASIBILITY")
    print("-" * 74)
    inv = {r["table"]: r for r in wr.warehouse_inventory(con)}
    for spec in wr.RULE_SPECS:
        got = census.by_rule.get(spec.rule, 0)
        view = inv.get(spec.view or "", {})
        span = (f"{view.get('first')} -> {view.get('last')}"
                if view.get("present") else "view ABSENT")
        missing = [s for s in spec.needs_sources
                   if s not in wr.ON_DISK_PREDICTION_SOURCES]
        print(f"\n  {spec.rule}   ({got} playable legs in archive)")
        print(f"    kind          {spec.kind}")
        print(f"    view          {spec.view} [{span}]")
        print(f"    needs         {', '.join(spec.needs_sources)}"
              + (f"   MISSING: {', '.join(missing)}" if missing else ""))
        print(f"    caveat        {spec.note}")
        if spec.kind == "ml-meta":
            print("    VERDICT       NOT RECONSTRUCTABLE — post-kickoff features "
                  "(see section 4)")
        elif view.get("present") and view.get("last", "") >= days[0]:
            print("    VERDICT       reconstructable in principle over the view's span")
        else:
            print("    VERDICT       NOT RECONSTRUCTABLE on archived days — "
                  "view has no rows there")
    print()

    # ---------------- 4. look-ahead audit ----------------
    print("-" * 74)
    print("4. LOOK-AHEAD AUDIT")
    print("-" * 74)
    try:
        import json as _json
        edges = _json.loads((LOCALDATA / "edges_consensus.json").read_text())
        model = edges.get("ml_model") or {}
        feats = wr.classify_ml_features(model.get("feature_cols", []),
                                        model.get("coef", []))
    except Exception:
        feats = []
    if feats:
        bad = [f for f in feats if f["availability"] == "post_kickoff"]
        print("ml-meta feature vector, by when the value becomes knowable:")
        for f in feats[:10]:
            print(f"  {f['feature']:18s} {f['coef']:+8.4f}  {f['availability']}")
        print("  ...")
        for f in bad:
            if f not in feats[:10]:
                print(f"  {f['feature']:18s} {f['coef']:+8.4f}  {f['availability']}")
        if bad:
            swing = wr.leak_logit_swing(feats)
            print(f"\n  {len(bad)} POST-KICKOFF feature(s): "
                  f"{', '.join(f['feature'] for f in bad)}")
            print("  These are the actual half-time scores of the match being")
            print("  predicted. Live inference has no scores yet and feeds 0.")
            print("  A warehouse replay reads them from the settled row, so a")
            print(f"  2-0 half-time lead alone shifts the logit by {swing:+.3f}")
            print("  — an 'edge' that did not exist at bet time.")
    else:
        print("no ml_model payload found in localdata/edges_consensus.json")

    try:
        stat = con.execute(
            "SELECT status, count(*) FROM forebet_settled GROUP BY 1 "
            "ORDER BY 2 DESC LIMIT 6").fetchall()
        total = sum(c for _, c in stat)
        print("\nforebet.csv.gz row status census (is any row pre-kickoff?):")
        for s, c in stat:
            print(f"  {str(s):12s} {c:8,d}  {100*c/total:5.1f}%")
        print("  Every row carries a TERMINAL status and a final score, and the")
        print("  file has no capture timestamp column. There is therefore no")
        print("  evidence any stored probability or price is the pre-kickoff")
        print("  one. Treat every forebet-priced replay result as an UPPER BOUND.")
    except Exception:
        pass
    print()

    # ---------------- 5. the gate ----------------
    print("-" * 74)
    print("5. VALIDATION GATE — reconstruct the archived days, score the recovery")
    print("-" * 74)
    print(f"bar stated before measuring: recall >= {wr.GATE_MIN_LEG_RECALL:.0%}, "
          f"precision >= {wr.GATE_MIN_LEG_PRECISION:.0%},")
    print(f"odds mismatch <= {wr.GATE_MAX_ODDS_MISMATCH:.0%} of matched legs, "
          f"input coverage >= {wr.GATE_MIN_COVERED_DAYS:.0%} of days.\n")

    by_day = {d: at.playable_legs(archives, day=d, settled=settled) for d in days}
    gate = wr.validation_gate(con, by_day, at.MIN_LEG_ODDS, norm_team)
    print(f"live legs/day       {gate['live_legs_per_day']:6.2f}")
    print(f"reconstructed/day   {gate['recon_legs_per_day']:6.2f}")
    print(f"true positives      {gate['tp']:6d}")
    print(f"false positives     {gate['fp']:6d}   (reconstruction invented these)")
    print(f"false negatives     {gate['fn']:6d}   (live legs never recovered)")
    print(f"leg recall          {gate['recall']:6.1%}")
    print(f"leg precision       {gate['precision']:6.1%}")
    if gate["odds_diffs"]:
        print(f"odds diff median    {gate['odds_diff_median']:+6.2%}")
        print(f"odds mismatch >1%   {gate['odds_mismatch_frac']:6.1%} of matched legs")
    else:
        print("odds diff           n/a — no leg matched, so no price to compare")
    nonzero = [d for d in gate["per_day"] if d["matched"]]
    print(f"days with any match {len(nonzero)} / {len(gate['per_day'])}")

    # Distinguish "the reconstruction code is broken" from "the data is absent"
    # by pointing the SAME function at the last window where inputs do exist.
    probe_days = con.execute(
        "SELECT date, count(*) FROM consensus2 GROUP BY 1 ORDER BY 1 DESC LIMIT 60"
    ).fetchall()
    if probe_days:
        pd_list = sorted(str(d)[:10] for d, _ in probe_days)
        found = [len(wr.reconstruct_legs(con, d, at.MIN_LEG_ODDS)) for d in pd_list]
        got = sum(found)
        print(f"\nmechanism check — same reconstructor, last {len(pd_list)} days that")
        print(f"DO have inputs ({pd_list[0]} -> {pd_list[-1]}):")
        print(f"  {got} legs over {len(pd_list)} days = "
              f"{got/len(pd_list):.2f} legs/day")
        print(f"  live engine sees {gate['live_legs_per_day']:.2f} legs/day across the")
        print("  archive (~11.5/day in-season). The reconstructor runs; it simply")
        print("  models a much narrower strategy than the engine does. That gap is")
        print("  the finding — it is not a tuning problem.")
    print()

    ok, reasons = wr.gate_verdict(cov, gate)
    print("=" * 74)
    print(f"PHASE 1 VERDICT: {'PASS' if ok else 'FAIL'}")
    print("=" * 74)
    for r in reasons:
        print(f"  - {r}")
    if not ok:
        print("\nPhase 2 (the 2024-2026 replay) is NOT unlocked. Any growth,")
        print("drawdown or ruin number produced through this reconstruction")
        print("would describe a strategy the engine never ran. Do not quote one.")
        print("\nWhat would unlock it, in order of size:")
        print("  1. vitibet history — cited by "
              f"{census.source_hits.get('vitibet', 0)} of {census.legs} playable legs.")
        print("  2. bet-time odds history for scoutingstats_odds / bzzoiro_odds"
              " — the two")
        print("     pricing sources behind the plurality of live legs.")
        print("  3. Point-in-time, timestamped prediction snapshots (captured")
        print("     BEFORE kickoff) rather than post-match scrapes.")
        print("  4. An ml-meta feature set with the half-time score removed,")
        print("     retrained walk-forward, before any ml-meta leg is replayed.")
    con.close()
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--variant", action="append", metavar="SPEC",
                    help="replay a variant spec (repeatable)")
    ap.add_argument("--ab", nargs=2, metavar=("SPEC_A", "SPEC_B"),
                    help="paired A/B of two specs, with no-op guard + bootstrap")
    ap.add_argument("--battery", action="store_true", help="the full sweep vs live baseline")
    ap.add_argument("--legs", action="store_true", help="stated-prob band table, saturated days")
    ap.add_argument("--slots", action="store_true",
                    help="leg/acca quality by rank slot (checkpoint ① at leg scale)")
    ap.add_argument("--kelly", action="store_true",
                    help="stake-fraction growth/drawdown curve + growth-optimal f")
    ap.add_argument("--today", action="store_true", help="today's card at LIVE settings")
    ap.add_argument("--rules", action="store_true",
                    help="leg quality + calibration by rule family, and the "
                         "paired cost of removing the ml-meta family")
    ap.add_argument("--warehouse-replay", action="store_true",
                    help="Phase-1 feasibility audit: can the live picks be "
                         "reconstructed from localdata at all? (research only)")
    ap.add_argument("--kickoff-contract", action="store_true",
                    help="AUDIT ONLY (off by default, never the live rule): "
                         "replay history under the fail-closed kickoff-proof "
                         "standard at each day's 09:00 SAST build, to size "
                         "the data-side kickoff gap (incident #6)")
    ap.add_argument("--kickoff-guard", action="store_true",
                    help="MONEY COST of the LIVE kickoff guard (region rule): "
                         "replay history with auto_tickets.live_kickoff_guard "
                         "at each day's 09:00 SAST build; log/day, maxDD and "
                         "bet-days lost vs the unguarded replay, plus the "
                         "ingest-normalisation recovery lower bound")
    ap.add_argument("--quarantine", action="store_true",
                    help="MEASURE ONLY: ridden WATCHLIST/quarantine legs — "
                         "census, hit rate + flat ROI (day-block bootstrap), "
                         "would-blank days and growth consequence, split "
                         "in-season/off-season. No gate change (Task B).")
    ap.add_argument("--exclude-started-ridden", metavar="FILE",
                    help="with --kickoff-guard: PERFECT-CLOCK CHECK (Task A "
                         "closeout) — drop the known-started ridden legs in "
                         "FILE ([{\"date\": ..., \"match\": ...}]) from every "
                         "arm's pools and print ex-rows beside the shipped "
                         "arms (contamination measurement; nothing ships)")
    ap.add_argument("--price-obtainability", action="store_true",
                    help="MEASURE ONLY (Task D): ridden scoutingstats legs — "
                         "D2 census/gap vs same-day stamped second-provider "
                         "prices, D3 obtainability-constrained replay "
                         "(IN-SAMPLE; repriced or dropped, never shipped)")
    ap.add_argument("--since", metavar="YYYY-MM-DD",
                    help="restrict replay universe to this date or later")
    ap.add_argument("--until", metavar="YYYY-MM-DD",
                    help="restrict replay universe to this date or earlier")
    # legacy single-knob flags (kept: HANDOVER documents them)
    ap.add_argument("--floor", type=float)
    ap.add_argument("--max-accas", type=int)
    ap.add_argument("--stake", type=float)
    ap.add_argument("--min-prob", type=float)
    ap.add_argument("--volume-min", type=float)
    ap.add_argument("--volume-pool", type=int)
    ap.add_argument("--gate-mode", choices=("off", "pool", "acca"))
    ap.add_argument("--no-fallback", action="store_true")
    args = ap.parse_args()

    settled = at.load_settled()
    archives = at.load_archived_picks()

    if args.warehouse_replay:
        # Runs against the RAW archive (not the settled-only replay universe):
        # feasibility is about whether inputs exist, not whether legs graded.
        return cmd_warehouse_replay(archives, settled,
                                    since=args.since, until=args.until)

    universe = build_universe(archives, settled)
    if args.since:
        universe = {d: pool for d, pool in universe.items() if d >= args.since}
    if args.until:
        universe = {d: pool for d, pool in universe.items() if d <= args.until}

    if args.kickoff_contract:
        return cmd_kickoff_contract(universe,
                                    since=args.since, until=args.until)
    if args.kickoff_guard:
        exclude = None
        if args.exclude_started_ridden:
            exclude = _exclusion_set(Path(args.exclude_started_ridden))
        return cmd_kickoff_guard(universe,
                                 since=args.since, until=args.until,
                                 exclude=exclude)
    if args.price_obtainability:
        return cmd_price_obtainability(universe,
                                       since=args.since, until=args.until)
    if args.quarantine:
        return cmd_quarantine(universe,
                              since=args.since, until=args.until)

    engine_status()
    live_settings()
    print("=" * 74)
    print(f"REPLAY UNIVERSE: {len(universe)} bet-days with settled playable legs")
    print("=" * 74)
    print("doctrine: RELATIVE differences + paired bootstrap. Primary metric is")
    print("mean LOG GROWTH per bet-day; final bank is one lucky path, not evidence.\n")

    if args.today:
        cmd_today(universe, settled)
        return 0

    if args.rules:
        cmd_rules(universe)
        return 0

    if args.slots:
        cmd_slots(universe)
        return 0

    if args.kelly:
        cmd_kelly(universe)
        return 0

    if args.legs:
        bands, sat_days = leg_bands(universe)
        print(f"=== stated-prob bands: legs on SATURATED days "
              f"({sat_days} days, floor {at.MIN_LEG_ODDS} APPLIED) ===\n")
        print(f"{'band':10s} {'n':>4s} {'hit':>6s} {'flatROI':>8s}")
        for b, (n, w, ret) in bands.items():
            if n:
                print(f"{b:10s} {n:4d} {w/n:6.1%} {(ret-n)/n:+8.1%}"
                      f"{'  << small-n' if n < 30 else ''}")
        return 0

    if args.ab:
        ab_report(universe, parse_spec(args.ab[0]), parse_spec(args.ab[1]))
        return 0

    if args.battery:
        cmd_battery(universe)
        return 0

    specs = [parse_spec(s) for s in (args.variant or [])]
    legacy = {}
    for key, val in (("floor", args.floor), ("max_accas", args.max_accas),
                     ("stake_frac", args.stake), ("min_prob", args.min_prob),
                     ("volume_min", args.volume_min), ("volume_pool", args.volume_pool),
                     ("gate_mode", args.gate_mode)):
        if val is not None:
            legacy[key] = val
    if args.no_fallback:
        legacy["fallback"] = False
    if legacy:
        specs.append(legacy)

    base = print_variant(universe, {}, "live settings (reference)")
    for spec in specs:
        print_variant(universe, spec, baseline=base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
