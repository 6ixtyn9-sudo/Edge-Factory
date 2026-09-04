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
  PYTHONPATH=src python3 scripts/replay_harness.py --today          # today's card, live settings
  PYTHONPATH=src python3 scripts/replay_harness.py --warehouse-replay  # feasibility audit
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
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


# --------------------------------------------------------------------------
# --warehouse-replay: FEASIBILITY audit (Phase 1). Research only, opt-in.
# --------------------------------------------------------------------------
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
    ap.add_argument("--warehouse-replay", action="store_true",
                    help="Phase-1 feasibility audit: can the live picks be "
                         "reconstructed from localdata at all? (research only)")
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
