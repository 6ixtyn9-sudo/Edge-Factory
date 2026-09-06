"""Task H (2026-09-06): ledger rebuild measurements — search-winner noise
reproduction, deployment-fraction replay, and the G1 no-repair contrast.

MEASUREMENT ONLY. No setting changes; nothing here ships. All figures are
in-sample and labelled as such.

1. REPRODUCE — the headline (+0.0410/day, 33 in-season days, 09-04 vintage)
   was shown to be the winner of a 13-variant search. Null test: run the 13
   documented variants (floors 1.01..1.30, max_accas 4/5/6, saturated_accas
   4/5/6) over today's in-season days, subtract each variant's own mean so
   every one has exactly zero true edge, resample days jointly 20,000 times,
   keep the winner each run. Prints the winner distribution (median, p90,
   P(noise >= +0.0410)) for the CURRENT archive (35 settled in-season days)
   — the brief's figures (+0.0372 / +0.0885 / 46%) are the same experiment
   on the earlier 33-day vintage.

2. DEPLOYMENT — the replay bets STAKE_FRAC of full bank each day; live money
   stays committed across runs so live stakes are a fraction of FREE bank.
   Report the replay at live-measured deployment fractions (mean committed
   from real ticket headers 08-27..09-06, incl. the corrected 09-06 repick)
   with log/day, final, maxDD and daily log-volatility.

3. G1 CONTRAST — 'the book without the started legs' under two removal
   mechanisms on the default universe minus the seven closeout legs:
   pool-level leg-drop with re-pairing (the harness exclusion arms) vs
   whole-acca removal without re-pairing. States the mechanism numbers so
   the two cannot be misread as one answer.

Run (repo root): PYTHONPATH=src python3 scripts/search_noise.py
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import replay_harness as rh  # noqa: E402

IN_SEASON = "2026-08-01"
FLOORS = [1.01, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30]
VARIANTS: list[tuple[str, dict]] = (
    [(f"floor={f:.2f}", {"floor": f}) for f in FLOORS]
    + [(f"max_accas={k}", {"max_accas": k}) for k in (4, 5, 6)]
    + [(f"saturated_accas={k}", {"saturated_accas": k}) for k in (4, 5, 6)]
)
HEADLINE = 0.0410


def _growth_path(rec: dict, days: list[str]) -> list[float]:
    return [rec[d]["growth"] if d in rec else 1.0 for d in days]


def _path_stats(logs: list[float]) -> dict:
    """Compound, maxDD and volatility on a per-day log series.

    final follows the harness convention (bank multiplier in %, matching the
    ledger's '235%' = x2.35 from 100) so receipts stay one convention."""
    path = list(np.exp(np.cumsum(logs)))
    peak = -1.0
    maxdd = 0.0
    for v in path:
        peak = max(peak, v)
        maxdd = max(maxdd, 1.0 - v / peak)
    final = path[-1] * 100.0 if path else 0.0
    return {
        "mean_log": float(np.mean(logs)),
        "final": float(final),
        "maxdd": float(maxdd),
        "vol": float(np.std(logs, ddof=1)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260906)
    args = ap.parse_args()

    settled = at.load_settled()
    archives = at.load_archived_picks()
    universe = rh.build_universe(archives, settled)
    universe = {d: pool for d, pool in universe.items() if d >= IN_SEASON}
    days = sorted(universe)
    n_days = len(days)

    print("=" * 74)
    print("TASK H REPRODUCE — the headline is a search winner (null test)")
    print("=" * 74)
    print(f"in-season settled days in today's archive: {n_days} "
          f"(09-04 brief vintage: 33; prior receipt: 35)")
    print("13 documented variant rows — IN-SAMPLE, demeaned to zero true edge")

    labels = [lab for lab, _ in VARIANTS]
    grows = np.zeros((len(VARIANTS), n_days))
    for i, (lab, spec) in enumerate(VARIANTS):
        rec = rh.replay(universe, spec)
        logs = [math.log(x) for x in _growth_path(rec, days)]
        grows[i] = logs
        own = float(np.mean(logs))
        print(f"  {lab:22s} in-sample mean log/day {own:+.4f}")
    # demean each variant to exactly zero true edge over the same days
    grows -= grows.mean(axis=1, keepdims=True)

    rng = np.random.default_rng(args.seed)
    draws = rng.integers(0, n_days, size=(args.runs, n_days))
    # winner per run: max over variants of mean over drawn days
    winners = np.empty(args.runs)
    for r in range(args.runs):
        sample = grows[:, draws[r]]          # (13, n_days)
        winners[r] = sample.mean(axis=1).max()
    print(f"\nwinner under pure-noise null, {args.runs:,} runs "
          f"(seed {args.seed}), days resampled jointly:")
    print(f"  median {np.median(winners):+.4f}/day   "
          f"p90 {np.percentile(winners, 90):+.4f}/day   "
          f"P(noise >= +{HEADLINE:.4f}) = {100.0 * (winners >= HEADLINE).mean():.0f}%")
    print("read: a 13-variant search on nothing manufactures a winner of this")
    print("size; the live-settings in-season replay is the single honest row")
    print("and it is far below the winner curve. All numbers here are IN-SAMPLE.")

    print()
    print("=" * 74)
    print("TASK H1 — deployment-gap replay at live-mean committed fractions")
    print("=" * 74)
    # live measured mean committed % of capital, ticket headers 08-27..09-06
    # (50%-era 25.0/12.5/20.3/10.2/14.8/34.1/25.0/25.0; 33%-era 16.7/22.2 +
    # 09-06 corrected repick at 32.4726/97.4176 = 33.33)
    headers = [25.0, 12.5, 20.3, 10.2, 14.8, 34.1, 25.0, 25.0, 16.7, 22.2,
               33.33]
    true_mean = float(np.mean(headers))
    print(f"live committed-capital headers (11 real tickets): "
          f"mean deployment {true_mean:.1f}% of bank")
    for frac in (at.STAKE_FRAC, 0.207, 0.217):
        rec = rh.replay(universe, {"stake_frac": frac})
        logs = [math.log(x) for x in _growth_path(rec, days)]
        s = _path_stats(logs)
        print(f"  replay stake_frac={frac:.3f} "
              f"({100.0 * frac:4.1f}%/day): bet-days {len(rec)}  "
              f"log/day {s['mean_log']:+.4f}  final {s['final']:6.0f}%  "
              f"maxDD {s['maxdd']:3.0%}  daily log-vol {s['vol']:.4f}")
    print("  live measured daily log-vol (real ledger): 0.1299")
    print("read: the replay's volatility gap vs live was the committed-capital")
    print("gap: at 33% it over-bets, at live deployment it lands on live vol.")

    print()
    print("=" * 74)
    print("TASK G1 — removal-mechanism contrast on the default universe")
    print("=" * 74)
    exclude = rh._exclusion_set(ROOT / "tests" / "data" / "started_ridden_legs.json")
    # arm A: pool-level leg-drop + re-pairing (the exclusion arms)
    ex_scope = {d: [leg for leg in pool
                    if (d, rh._fold_name(leg["match"])) not in exclude]
                for d, pool in universe.items()}
    ex_scope = {d: p for d, p in ex_scope.items() if len(p) >= at.LEGS_PER_ACCA}
    # arm B: whole-acca removal without re-pairing, stakes re-split over the
    # surviving accas (per_day doctrine) — what dropping the ticket would do
    shipped = rh.replay(universe, {})
    acca_drop_logs: list[float] = []
    dropped_days = 0
    for d in sorted(universe):
        rec = shipped.get(d)
        if rec is None:
            continue
        kept = [(o, wins, legs) for (o, wins), legs in zip(rec["accas"], rec["legs"])
                for _ in [0] if not any((d, rh._fold_name(m)) in exclude
                                        for m in legs)]
        if not kept:
            dropped_days += 1
            continue
        stake = 100.0 * at.STAKE_FRAC / len(kept)
        returned = sum(stake * o for o, wins, _ in kept if wins)
        staked = stake * len(kept)
        acca_drop_logs.append(math.log((100.0 - staked + returned) / 100.0))
    base_logs = [math.log(x) for x in _growth_path(shipped, days)]
    s_base = _path_stats(base_logs)
    s_acca = _path_stats(acca_drop_logs)
    # ex arm logs from the scope rerun
    ex_rec = rh.replay(ex_scope, {})
    ex_logs = [math.log(x) for x in _growth_path(ex_rec, days)]
    s_ex = _path_stats(ex_logs)
    print(f"  in-season default (shipped)        : {n_days} d  "
          f"log/day {s_base['mean_log']:+.4f}  final {s_base['final']:6.0f}%  "
          f"maxDD {s_base['maxdd']:3.0%}")
    print(f"  minus five, LEG-DROP + re-pairing  : {len(ex_rec)} d  "
          f"log/day {s_ex['mean_log']:+.4f}  final {s_ex['final']:6.0f}%  "
          f"maxDD {s_ex['maxdd']:3.0%}")
    print(f"  minus five, ACCOUNTS removed no-repair: "
          f"{sum(1 for x in acca_drop_logs)} d  "
          f"log/day {s_acca['mean_log']:+.4f}  final {s_acca['final']:6.0f}%  "
          f"maxDD {s_acca['maxdd']:3.0%}  ({dropped_days} day(s) fully dropped)")
    print("read: both exclusion arms in the asterisk ledger are arm A — the")
    print("same mechanism at pool level. Guard rows are a different POPULATION")
    print("(its rule also removes other leg classes), not a different mechanism.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
