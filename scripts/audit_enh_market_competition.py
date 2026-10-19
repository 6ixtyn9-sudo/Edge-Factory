#!/usr/bin/env python3
"""Read-only full-pool explanation of the retained parity audit's selections.

Reuse its strict timestamp/identity/price rules and verify its input hashes.
This is a competition diagnostic, not a new ROI backtest or live policy.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'src'), str(ROOT / 'scripts')]
from scripts import audit_enh_under_parity as audit


def competition(root=ROOT):
    source = root / 'docs/operator/audits/enh-under-redteam-2026-10-19.json'
    original = json.loads(source.read_text())
    for relative, expected in original['inputs_sha256'].items():
        if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Prior audit input changed: {relative}; rerun original audit first')
    evidence = {tuple(row['fixture']): row for row in original['evidence']}
    raw = defaultdict(list)
    for provider in ('oddspapi', 'theoddsapi'):
        for month in sorted({key[0][:7] for key in evidence}):
            path = root / 'localdata' / f'{provider}_odds_{month}.csv.gz'
            if path.exists():
                with gzip.open(path, 'rt') as handle:
                    for row in csv.DictReader(handle):
                        key = audit.identity(row)
                        if key in evidence:
                            raw[key].append((provider, row))
    counts, blockers, new_markets = Counter(), Counter(), Counter()
    winners = {False: Counter(), True: Counter()}
    details = []
    thresholds = audit.legacy_thresholds()
    for key, entry in sorted(evidence.items()):
        row = dict(zip(('date', 'home', 'away'), key),
                   as_of=entry['as_of'], kickoff_utc=entry['kickoff_utc'])
        quotes = audit.quotes_for(row, raw[key], Counter())
        rates = entry['cohort_rates']
        baseline = audit.choose(rates, quotes, thresholds, False)
        proposed = audit.choose(rates, quotes, thresholds, True)
        # Fail rather than explaining a population different from the old audit.
        if baseline != entry['baseline'] or proposed != entry['proposed']:
            raise ValueError(f'Choice mismatch: {key}')
        counts['snapshots'] += 1
        counts['changed_fixture_choices'] += baseline != proposed
        for arm, choice in ((False, baseline), (True, proposed)):
            if choice:
                winners[arm][choice['market']] += 1
        newly_admitted = []
        pool = []
        for market, rate in rates.items():
            quote = quotes.get(audit.MARKET_PRICE_MAP.get(market))
            if not .25 <= rate <= .90 or not quote or quote['price'] < audit.at.MIN_LEG_ODDS:
                continue
            legacy = market != 'match_under_45' and rate >= thresholds.get(market, .80)
            candidate = {'market': market, 'rate': rate, **quote, 'legacy_eligible': legacy}
            pool.append(candidate)
            counts['priced_in_band_candidates'] += 1
            if not legacy:
                newly_admitted.append(candidate)
                new_markets[market] += 1
                counts['newly_admitted_candidates'] += 1
                if 'under' in market:
                    counts['newly_admitted_under_candidates'] += 1
                if proposed and proposed['market'] != market:
                    blockers[proposed['market']] += 1
                    counts['new_candidates_shadowed_by_higher_rate'] += proposed['rate'] > rate
        if newly_admitted:
            counts['fixtures_with_new_candidates'] += 1
            details.append({'fixture': list(key), 'baseline': baseline, 'proposed': proposed,
                            'newly_admitted': newly_admitted,
                            'full_priced_in_band_pool': sorted(pool, key=lambda c: (c['rate'], c['price']), reverse=True)})
    return {'scope': 'All available archived cohort-backed markets compete within each retained fixture',
            'source_report_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'coverage': dict(counts), 'new_candidates_by_market': dict(new_markets),
            'winning_markets_shadowing_new_candidates': dict(blockers),
            'baseline_winning_markets': dict(winners[False]),
            'parity_winning_markets': dict(winners[True]), 'details': details,
            'limitations': original['limitations'],
            'verdict': 'NO_CHANGED_SELECTIONS_IN_RETAINED_FULL_POOL' if not counts['changed_fixture_choices'] else 'CHANGED_SELECTIONS_REQUIRE_PAIRED_CARD_EVALUATION',
            'production_changed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out and args.out.resolve().is_relative_to((ROOT / 'localdata').resolve()):
        parser.error('audit output must not overwrite operational localdata')
    text = json.dumps(competition(), indent=2, allow_nan=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end='')
