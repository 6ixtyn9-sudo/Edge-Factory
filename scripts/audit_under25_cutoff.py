#!/usr/bin/env python3
"""Read-only arithmetic/sampling audit of the 80% at 1.40 versus 85% example.

Expected returns are conditional arithmetic, not forecasts or a new EV gate.
Wilson intervals assume independent, representative binary observations; they
cannot repair leakage, duplicate fixtures, source-regime changes or calibration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src'), str(ROOT / 'scripts')]
from scripts.audit_enh_under_parity import identity, instant, legacy_thresholds, snapshot_rates
from edgefactory.enh_registry import wilson_lb


def finite(value):
    if isinstance(value, bool):
        raise ValueError('boolean is not a numeric probability or price')
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('expected a finite number') from exc
    if not math.isfinite(value):
        raise ValueError('expected a finite number')
    return value


def expected_return(probability, odds):
    p, price = finite(probability), finite(odds)
    if not 0 <= p <= 1 or price <= 1:
        raise ValueError('probability must be in [0, 1] and decimal odds > 1')
    return p * price - 1


def sampling_case(hits, n, odds):
    if (isinstance(n, bool) or isinstance(hits, bool) or not isinstance(n, int)
            or not isinstance(hits, int) or n <= 0 or not 0 <= hits <= n):
        raise ValueError('require integer 0 <= hits <= positive n')
    price = finite(odds)
    if price <= 1:
        raise ValueError('decimal odds must exceed 1')
    lower = wilson_lb(hits, n)
    upper = 1 - wilson_lb(n - hits, n)
    return {'hits': hits, 'n': n, 'observed_rate': hits/n,
            'wilson_two_sided_95pct': [lower, upper],
            'roi_at_lower_endpoint': expected_return(lower, price),
            'roi_at_lower_endpoint_after_5pct_price_haircut': expected_return(lower, price * .95)}


def min_hits_for_lower_bound(n, odds):
    """Sensitivity diagnostic, NOT an eligibility gate or power calculation."""
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        raise ValueError('n must be a positive integer')
    price = finite(odds)
    if price <= 1:
        raise ValueError('decimal odds must exceed 1')
    return next((h for h in range(n + 1) if wilson_lb(h, n) * price >= 1), None)


def archived_under25(root, since='2026-10-14', until='2026-10-18'):
    """Same retained snapshot conditions as the earlier audit; no odds invented."""
    snapshots, inputs = {}, {}
    for path in sorted((root / 'localdata').glob('picks_????-??-??.json')):
        day = path.stem[6:]
        if not since <= day <= until:
            continue
        inputs[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
        rows = json.loads(path.read_text())
        for row in rows if isinstance(rows, list) else []:
            decision, kickoff = instant(row.get('as_of')), instant(row.get('kickoff_utc'))
            if (row.get('date') != day or decision is None or kickoff is None
                    or (kickoff - decision).total_seconds() < 1800):
                continue
            rates = snapshot_rates(row)
            if not rates:
                continue
            key = identity(row)
            if key in snapshots and snapshots[key][0] <= decision:
                continue
            snapshots[key] = (decision, rates.get('match_under_25'))
    rates = [r for _, r in snapshots.values() if r is not None]
    return {'since': since, 'until': until, 'retained_cohort_snapshots': len(snapshots),
            'available_under25_rates': len(rates), 'minimum_rate': min(rates) if rates else None,
            'maximum_rate': max(rates) if rates else None,
            'at_least_80pct': sum(p >= .80 for p in rates),
            'at_least_85pct': sum(p >= .85 for p in rates),
            'newly_eligible_at_80_vs_85': sum(.80 <= p < .85 for p in rates),
            'limitations': 'Final snapshots, incomplete cohort/source coverage; not the full live/model universe or placed bets.',
            'input_sha256': inputs}


def build_report(root):
    odds = 1.40
    return {'schema': 1, 'verdict': '85_IS_A_LEGACY_FILTER_NOT_A_VALIDATED_UNIVERSAL_PROFIT_THRESHOLD',
            'legacy_threshold_values_changed': False,
            'default_cohort_eligibility': 'shared_25_to_90pct_min_odds_1.30',
            'legacy_under25_filter': legacy_thresholds()['match_under_25'],
            'example': {'observed_rate': .80, 'decimal_odds': odds,
                        'breakeven_probability': 1/odds, 'point_fair_odds': 1/.80,
                        'expected_roi_if_true_probability_is_80pct': expected_return(.80, odds)},
            'probability_and_price_stress': [
                {'true_probability_assumption': p, 'decimal_price_haircut': haircut,
                 'effective_odds': odds*(1-haircut),
                 'breakeven_probability': 1/(odds*(1-haircut)),
                 'expected_roi_if_assumptions_hold': expected_return(p, odds*(1-haircut))}
                for p in (.85, .80, .75, 1/odds, .70, .65) for haircut in (0, .02, .05, .10)],
            'sampling_stress': [sampling_case(int(n*.8), n, odds) for n in (100, 200, 400, 1000)],
            'lower_bound_crossing_diagnostic': [
                {'n': n, 'odds': price, 'minimum_hits': min_hits_for_lower_bound(n, price)}
                for n in (100, 200, 400, 1000) for price in (1.30, 1.33, 1.40)],
            '85pct_not_a_universal_safety_guarantee': {
                'n': 100, 'hits': 85, 'price': 1.30,
                'wilson_lower': wilson_lb(85, 100),
                'roi_at_lower_endpoint': expected_return(wilson_lb(85, 100), 1.30)},
            'archived_evidence': archived_under25(root),
            'interpretation': [
                'The example is hypothetical; it is not an identified 80%-rate quoted fixture.',
                'Operator-authorized shared cohort eligibility is now default ON; 85% applies only to legacy rollback/model fallback.',
                '80% historical frequency is not known true probability or a promise of +12% ROI.',
                'Wilson intervals require independent representative trials; real cohort effective n may be smaller.',
                'Lower-endpoint expected return is a sensitivity diagnostic, not a prediction interval for future cash ROI.',
                'No fixed 80% or 85% cutoff is established as optimal by this evidence.',
                'Minimum odds of 1.30, accumulator sizing, current band and hold remain unchanged.',
                'No external API calls, current-warehouse refit or outcome-based tuning; default eligibility changed by explicit operator authorization.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out and args.out.resolve().is_relative_to((args.root / 'localdata').resolve()):
        parser.error('write audit reports outside operational localdata')
    text = json.dumps(build_report(args.root), indent=2, allow_nan=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
