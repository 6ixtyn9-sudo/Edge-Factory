"""Edge Factory replay harness — counterfactual engine replays on LIVE localdata.

Answers "what would the engine have done if X?" using the REAL current ledgers,
the REAL current guards (imported from scripts/auto_tickets.py on main), and
the REAL state history. Unlike my sandbox snapshots, this sees everything.

DOCTRINE (read before trusting any output):
  - Replays are for RELATIVE comparisons (variant A vs variant B on the same
    data) and for COUNTERFACTUALS (what would today's card have been).
    They are NOT predictions. Absolute replay numbers will disagree with the
    engine's actual history (different guards live at different eras, voids,
    settlements lag). Trust the actual engine ledger for "what happened";
    trust replays only for "how do two policies differ on identical inputs."
  - Every output prints n. Cells with n < 30 are flagged as noise.
  - Bootstrap confidence is printed for any A-vs-B difference. If the 10th
    percentile of the difference spans 0, the difference is luck-shaped.

Usage (Codespace, from repo root):
  PYTHONPATH=src python3 scripts/replay_harness.py                     # status + last-30d audit
  PYTHONPATH=src python3 scripts/replay_harness.py --floor 1.10        # replay at a floor
  PYTHONPATH=src python3 scripts/replay_harness.py --ab 1.10 1.20      # A/B two floors + bootstrap
  PYTHONPATH=src python3 scripts/replay_harness.py --max-accas 5       # replay with 5 accas/day
  PYTHONPATH=src python3 scripts/replay_harness.py --stake 0.25        # replay at 25%/day
  PYTHONPATH=src python3 scripts/replay_harness.py --min-prob 0.65     # always-on prob floor
  PYTHONPATH=src python3 scripts/replay_harness.py --today             # today's card at live settings
  PYTHONPATH=src python3 scripts/replay_harness.py --all               # the full battery
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import auto_tickets as at  # the live engine — guards, floors, constants  # noqa: E402

LOCALDATA = ROOT / "localdata"


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------
def load_settings():
    p = LOCALDATA / "auto_tickets_state.json"
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


# --------------------------------------------------------------------------
# build the day-by-day candidate universe ONCE from the real archive,
# honoring every live guard, then re-filter per variant below.
# --------------------------------------------------------------------------
def build_universe(archives, settled):
    """For each archive day: playable legs (live guards) with settled results,
    sorted prob-desc — exactly what plan_day sees."""
    days = sorted({str(p.get("date") or p.get("_archive_day") or "")[:10] for p in archives})
    universe = {}
    for d in days:
        pool = at.playable_legs(archives, day=d, settled=settled)
        pool = [l for l in pool if l["result"]]          # settled only (replay can't grade pending)
        if len(pool) >= at.LEGS_PER_ACCA:
            universe[d] = sorted(pool, key=lambda l: (l["prob"], l["odds"]), reverse=True)
    return universe


def plan_for_day(pool, *, floor, max_accas, min_prob, volume_pool, volume_min):
    """plan_day re-implemented with overridable knobs (mirrors live logic)."""
    pool = [l for l in pool if l["odds"] >= floor]
    if min_prob is not None:
        pool = [l for l in pool if l["prob"] >= min_prob]
    if len(pool) >= volume_pool:
        pool = [l for l in pool if l["prob"] >= volume_min]
    legs = pool[: max_accas * 2]
    pairs = [legs[i : i + 2] for i in range(0, len(legs) - 1, 2)][:max_accas]
    return [p for p in pairs if len(p) == 2]


def replay(universe, *, floor, max_accas, min_prob, stake_frac,
           volume_pool=None, volume_min=None, start_bank=100.0):
    """Compound replay. Returns (final_bank, per-day list)."""
    volume_pool = at.VOLUME_POOL if volume_pool is None else volume_pool
    volume_min = at.VOLUME_MIN_PROB if volume_min is None else volume_min
    bank = start_bank
    days = []
    for d in sorted(universe):
        pairs = plan_for_day(universe[d], floor=floor, max_accas=max_accas,
                             min_prob=min_prob, volume_pool=volume_pool, volume_min=volume_min)
        if not pairs:
            continue
        stake = bank * stake_frac / len(pairs)
        ret = 0.0
        for a in pairs:
            if a[0]["result"] == "win" and a[1]["result"] == "win":
                ret += stake * a[0]["odds"] * a[1]["odds"]
        bank += ret - stake * len(pairs)
        days.append({
            "date": d,
            "accas": [(round(a[0]["odds"] * a[1]["odds"], 2),
                       a[0]["result"] == "win" and a[1]["result"] == "win") for a in pairs],
            "bank": round(bank, 2),
        })
    return bank, days


def acca_rate(days):
    """Per-day list-of-acca-outcomes for bootstrap sampling."""
    return [(d["date"], d["accas"]) for d in days]


def bootstrap_ab(univ, a_kw, b_kw, n=3000, seed=2026):
    """Bootstrap the difference in final bank between two variants."""
    random.seed(seed)
    _, days_a = replay(univ, **a_kw)
    _, days_b = replay(univ, **b_kw)
    la, lb = acca_rate(days_a), acca_rate(days_b)
    if not la or not lb:
        return None
    def compound(sample):
        bank = 100.0
        for _, accas in sample:
            stake = bank * 0.5 / len(accas)
            ret = 0.0
            for o, w in accas:
                if w:
                    ret += stake * o
            bank += ret - stake * len(accas)
        return bank
    diffs = []
    for _ in range(n):
        sa = random.choices(la, k=len(la))
        sb = random.choices(lb, k=len(lb))
        diffs.append(compound(sb) - compound(sa))
    diffs.sort()
    q = lambda p: diffs[int(len(diffs) * p)]  # noqa: E731
    return {
        "median": q(0.5), "p10": q(0.1), "p90": q(0.9),
        "p_b_higher": sum(1 for x in diffs if x > 0) / len(diffs),
        "n_days_a": len(la), "n_days_b": len(lb),
    }


def noise_flag(n):
    return "  ⚠ small-n" if n < 30 else ""


# --------------------------------------------------------------------------
# reports
# --------------------------------------------------------------------------
def engine_status():
    st = load_settings()
    if not st:
        print("no engine state found")
        return
    accas = [a for h in st.get("history", []) for a in h["accas"]]
    w = sum(1 for a in accas if a["won"])
    rate = f"{w/len(accas):.0%}" if accas else "n/a"
    print("=" * 70)
    print("ENGINE ACTUAL (the only source of 'what happened')")
    print("=" * 70)
    print(f"bank {st.get('bank', 0):.1f}%  ·  bet-days {len(st.get('history', []))}  ·  "
          f"accas {w}W/{len(accas)-w}L ({rate})  ·  open slips {len(st.get('open_slips', []))}")
    for h in st.get("history", [])[-8:]:
        acc = " ".join(f"@{a['odds']:.2f}{'W' if a['won'] else 'L'}" for a in h["accas"])
        print(f"  {h['date']}  {acc:34s} bank {h['bank_pct']:7.1f}%")
    print()


def live_settings():
    print("=" * 70)
    print("LIVE SETTINGS (from scripts/auto_tickets.py on this checkout)")
    print("=" * 70)
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    import re
    for const in ("STAKE_FRAC", "MAX_ACCAS", "LEGS_PER_ACCA", "VOLUME_POOL",
                  "VOLUME_MIN_PROB", "FREEZE_HOUR"):
        m = re.search(rf"^{const}\s*=\s*([0-9.]+)", src, re.M)
        if m:
            print(f"  {const:18s} {m.group(1)}")
    m = re.search(r"if odds < ([0-9.]+):", src)
    print(f"  {'MIN_LEG_ODDS':18s} {m.group(1) if m else 'none found'}")
    print()


def variant_replay(universe, label, **kw):
    floor = kw.get("floor", 1.20)
    max_accas = kw.get("max_accas", at.MAX_ACCAS)
    stake = kw.get("stake_frac", at.STAKE_FRAC)
    min_prob = kw.get("min_prob")
    bank, days = replay(universe, **kw)
    n_accas = sum(len(d["accas"]) for d in days)
    w = sum(1 for d in days for _, win in d["accas"] if win)
    print(f"{label:44s} final {bank:7.0f}%  days {len(days):2d}  accas {n_accas:3d}  "
          f"hit {w/n_accas:5.0%}{noise_flag(n_accas)}")
    return bank, days


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--floor", type=float, default=None, help="replay with a min leg odds floor")
    ap.add_argument("--max-accas", type=int, default=None, help="replay with N accas/day")
    ap.add_argument("--stake", type=float, default=None, help="replay with X fraction of bank/day")
    ap.add_argument("--min-prob", type=float, default=None, help="always-on stated-prob floor")
    ap.add_argument("--volume-pool", type=int, default=None, help="saturation threshold")
    ap.add_argument("--ab", nargs=2, type=float, metavar=("FLOOR_A", "FLOOR_B"),
                    help="A/B two floors with bootstrap confidence")
    ap.add_argument("--today", action="store_true", help="print today's card at LIVE settings")
    ap.add_argument("--all", action="store_true", help="the full battery")
    args = ap.parse_args()

    settled = at.load_settled()
    archives = at.load_archived_picks()
    universe = build_universe(archives, settled)

    engine_status()
    live_settings()

    print("=" * 70)
    print(f"REPLAY UNIVERSE: {len(universe)} bet-days with settled playable legs")
    print("=" * 70)
    print("doctrine: trust RELATIVE differences + bootstrap, not absolute numbers\n")

    base_kw = dict(floor=1.20, max_accas=at.MAX_ACCAS, min_prob=None, stake_frac=at.STAKE_FRAC)
    live_kw = dict(floor=1.20, max_accas=at.MAX_ACCAS, min_prob=None, stake_frac=at.STAKE_FRAC)

    if args.today:
        today = date.today().isoformat()
        pool = universe.get(today) or at.playable_legs(
            json.loads((LOCALDATA / "picks_today.json").read_text()),
            day=today, settled=settled)
        pool = sorted([l for l in pool if l["result"] is None or l["result"]],
                      key=lambda l: (l["prob"], l["odds"]), reverse=True)
        pairs = plan_for_day(pool, floor=1.20, max_accas=at.MAX_ACCAS,
                             min_prob=None, volume_pool=at.VOLUME_POOL, volume_min=at.VOLUME_MIN_PROB)
        print(f"today ({today}) at live settings — {len(pairs)} accas:")
        for i, a in enumerate(pairs, 1):
            prod = a[0]["odds"] * a[1]["odds"]
            print(f"  ACCA #{i} @{prod:.2f}: {a[0]['match']} ({a[0]['pick']} @{a[0]['odds']:.2f}) "
                  f"x {a[1]['match']} ({a[1]['pick']} @{a[1]['odds']:.2f})")
        return 0

    if args.ab:
        fa, fb = args.ab
        print(f"A/B: floor {fa} vs floor {fb} (identical everything else)\n")
        variant_replay(universe, f"floor {fa}", **{**base_kw, "floor": fa})
        variant_replay(universe, f"floor {fb}", **{**base_kw, "floor": fb})
        r = bootstrap_ab(universe, {**base_kw, "floor": fa}, {**base_kw, "floor": fb})
        if r:
            print(f"\nbootstrap (B minus A, final bank): median {r['median']:+.0f}%  "
                  f"10th {r['p10']:+.0f}%  90th {r['p90']:+.0f}%")
            print(f"P(floor {fb} higher) = {r['p_b_higher']:.0%}  "
                  f"(spans zero = luck-shaped; decide on 30d+ real data)")
        return 0

    if args.all:
        print("--- floor sweep ---")
        for f in (1.10, 1.15, 1.20, 1.25, 1.30):
            variant_replay(universe, f"floor {f:.2f}", **{**base_kw, "floor": f})
        print("\n--- accas-per-day sweep (heavy-day question) ---")
        for k in (3, 4, 5, 6):
            variant_replay(universe, f"max {k} accas/day", **{**base_kw, "max_accas": k})
        print("\n--- stake sweep ---")
        for s in (0.25, 0.33, 0.50, 0.75):
            variant_replay(universe, f"stake {s:.0%}/day", **{**base_kw, "stake_frac": s})
        print("\n--- always-on prob floor (your B-spec from Sept) ---")
        for mp in (0.60, 0.65, 0.70):
            variant_replay(universe, f"min stated-prob {mp:.0%}", **{**base_kw, "min_prob": mp})
        return 0

    # default: single replay at requested (or live) settings
    kw = dict(base_kw)
    if args.floor is not None: kw["floor"] = args.floor
    if args.max_accas is not None: kw["max_accas"] = args.max_accas
    if args.stake is not None: kw["stake_frac"] = args.stake
    if args.min_prob is not None: kw["min_prob"] = args.min_prob
    if args.volume_pool is not None: kw["volume_pool"] = args.volume_pool
    variant_replay(universe, "requested variant", **kw)
    variant_replay(universe, "live settings (reference)", **live_kw)
    return 0


if __name__ == "__main__":
    sys.exit(main())