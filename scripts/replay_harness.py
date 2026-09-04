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
        saturated_accas, volume_pool, volume_min, gate_mode(off|pool|acca),
        fallback(0|1), stake_frac, min_prob (harness-only always-on prob floor)

Usage (from repo root):
  PYTHONPATH=src python3 scripts/replay_harness.py                  # status + live baseline
  PYTHONPATH=src python3 scripts/replay_harness.py --ab 1.15 1.20   # paired A/B + bootstrap
  PYTHONPATH=src python3 scripts/replay_harness.py --ab live "gate_mode=acca"
  PYTHONPATH=src python3 scripts/replay_harness.py --variant "saturated_accas=5"
  PYTHONPATH=src python3 scripts/replay_harness.py --battery        # the full sweep vs live
  PYTHONPATH=src python3 scripts/replay_harness.py --slots          # quality by rank slot
  PYTHONPATH=src python3 scripts/replay_harness.py --kelly          # stake sizing curve
  PYTHONPATH=src python3 scripts/replay_harness.py --legs           # stated-prob band table
  PYTHONPATH=src python3 scripts/replay_harness.py --today          # today's card, live settings
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

# knobs forwarded to at.select_accas (everything else is harness-level)
ENGINE_KEYS = {"floor", "rank", "pairing", "max_accas", "legs_per_acca",
               "volume_pool", "volume_min", "gate_mode", "fallback",
               "saturated_accas"}
FLOAT_KEYS = {"floor", "volume_min", "stake_frac", "min_prob"}
INT_KEYS = {"max_accas", "legs_per_acca", "volume_pool", "saturated_accas"}
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
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise SystemExit(f"bad spec fragment {part!r} (want key=value)")
        k, v = (s.strip() for s in part.split("=", 1))
        if k in BOOL_KEYS:
            spec[k] = v.lower() not in ("0", "false", "no", "off")
        elif k in INT_KEYS:
            spec[k] = int(v)
        elif k in FLOAT_KEYS:
            spec[k] = float(v)
        else:
            spec[k] = v
    unknown = set(spec) - ENGINE_KEYS - {"stake_frac", "min_prob"}
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


def card_for_day(pool, spec):
    """The live selector, driven by a variant spec. Returns list of accas."""
    kw = {k: v for k, v in spec.items() if k in ENGINE_KEYS}
    mp = spec.get("min_prob")
    if mp is not None:
        pool = [l for l in pool if l["prob"] >= mp]
    return at.select_accas(pool, **kw)


def day_growth(accas, stake_frac):
    """Bank-multiplier for one bet-day. Bank-independent: stake is
    stake_frac of bank split evenly, so growth = 1 + f*(mean(odds*win) - 1)."""
    n = len(accas)
    ret = 0.0
    for a in accas:
        if all(l["result"] == "win" for l in a):
            prod = 1.0
            for l in a:
                prod *= l["odds"]
            ret += prod
    return 1.0 + stake_frac * (ret / n - 1.0)


def replay(universe, spec):
    """Per-day record for a variant. Order-independent by construction."""
    stake_frac = spec.get("stake_frac", at.STAKE_FRAC)
    out = {}
    for d in sorted(universe):
        accas = card_for_day(universe[d], spec)
        if not accas:
            continue
        out[d] = {
            "growth": day_growth(accas, stake_frac),
            "accas": [(round(math.prod(l["odds"] for l in a), 4),
                       all(l["result"] == "win" for l in a)) for a in accas],
            "legs": [tuple(l["match"] for l in a) for a in accas],
        }
    return out


def summarise(days):
    g = [days[d]["growth"] for d in sorted(days)]        # date order (drawdown is a path)
    accas = [a for d in days.values() for a in d["accas"]]
    wins = sum(1 for _, w in accas if w)
    logs = [math.log(x) for x in g if x > 0]
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
        "mean_log": sum(logs) / len(logs) if logs else 0.0,
        "final": final,
        "maxdd": maxdd,
        "worst": min(g) if g else 1.0,
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
    la = {d: math.log(v["growth"]) for d, v in da.items() if v["growth"] > 0}
    lb = {d: math.log(v["growth"]) for d, v in db.items() if v["growth"] > 0}
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
        contrib.append((full - without, d))
    if not contrib:
        return None
    contrib.sort(key=lambda t: -abs(t[0]))
    top, top_day = contrib[0]
    return {"full": full, "top_day": top_day, "top_share": abs(top) / abs(full) if full else 0.0,
            "drop_one": full - top, "flips": (full > 0) != ((full - top) > 0),
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
    ga = {d: math.log(da[d]["growth"]) for d in da if da[d]["growth"] > 0}
    gb = {d: math.log(db[d]["growth"]) for d in db if db[d]["growth"] > 0}
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
    for const in ("STAKE_FRAC", "MAX_ACCAS", "LEGS_PER_ACCA", "MIN_LEG_ODDS",
                  "VOLUME_POOL", "VOLUME_MIN_PROB", "GATE_MODE", "FREEZE_HOUR"):
        print(f"  {const:18s} {getattr(at, const)}")
    print()


def print_variant(universe, spec, label=None, baseline=None):
    s = summarise(replay(universe, spec))
    lbl = label or label_of(spec)
    mark = ""
    if baseline is not None:
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
    print_variant(universe, spec_b, f"B: {lb}", baseline=sa)
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
        print(f"  leave-one-day-out effect: {e['drop_one']:+.4f} log/day "
              f"(full {e['full']:+.4f})", end="  ")
        if e["flips"]:
            print("— SIGN FLIPS: this is one day, not a policy")
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
    """Growth-vs-risk curve over the stake fraction, on identical cards.

    Sizing is the one lever that changes NOTHING about selection, so its
    evidence is far cleaner than any leg-filter A/B: the same days, the same
    accas, only the fraction of bank deployed. Prints the growth-optimal f
    (full-Kelly-equivalent for this card distribution) and how stable it is.
    """
    spec = dict(spec or {})
    days = replay(universe, {k: v for k, v in spec.items() if k != "stake_frac"})
    # per-day acca-return multiple: mean(odds * won) over the day's accas
    R = [sum(o for o, w in rec["accas"] if w) / len(rec["accas"])
         for rec in days.values()]
    if not R:
        print("no bet-days")
        return
    grid = sorted(set([i / 100 for i in range(5, 96, 5)] + [round(at.STAKE_FRAC, 4)]))

    def growth(f, sample=None):
        s = R if sample is None else sample
        return sum(math.log(1 + f * (r - 1)) for r in s) / len(s)

    def maxdd(f):
        bank = peak = 1.0
        worst = 0.0
        for d in sorted(days):
            rec = days[d]
            r = sum(o for o, w in rec["accas"] if w) / len(rec["accas"])
            bank *= 1 + f * (r - 1)
            peak = max(peak, bank)
            worst = max(worst, 1 - bank / peak)
        return worst

    print(f"stake sizing on {len(R)} bet-days ({sum(1 for r in R if r == 0)} total-loss days)")
    print("cards are IDENTICAL across rows — only the fraction of bank changes\n")
    print(f"{'stake f':>8s} {'log/day':>9s} {'final%':>9s} {'maxDD':>7s}")
    best = max(grid, key=growth)
    live_f = round(at.STAKE_FRAC, 4)
    for f in grid:
        star = "   <- growth-optimal" if f == best else ""
        if f == live_f:
            star += "   <- LIVE"
        print(f"{f:8.0%} {growth(f):+9.4f} {100*math.exp(growth(f)*len(R)):9.0f} "
              f"{maxdd(f):7.0%}{star}")
    random.seed(2026)
    opts = []
    for _ in range(2000):
        sample = random.choices(R, k=len(R))          # ONE resample per iteration
        opts.append(max(grid, key=lambda f: growth(f, sample)))
    opts.sort()
    print(f"\ngrowth-optimal f on this path: {best:.0%} (log/day {growth(best):+.4f}, "
          f"maxDD {maxdd(best):.0%})")
    print(f"bootstrapped f*: median {opts[len(opts)//2]:.0%}  p10 {opts[int(.1*len(opts))]:.0%}  "
          f"p90 {opts[int(.9*len(opts))]:.0%}")
    print(f"P(f* < live {at.STAKE_FRAC:.0%}) = {sum(1 for o in opts if o < at.STAKE_FRAC)/len(opts):.0%}")
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
    universe = build_universe(at.load_archived_picks(), settled)

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
