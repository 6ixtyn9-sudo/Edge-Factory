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


def competition(root=ROOT, source=None):
    source = Path(source) if source is not None else root / 'docs/operator/audits/enh-under-redteam-2026-10-19.json'
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
    archives = {}
    for key, entry in sorted(evidence.items()):
        row = dict(zip(('date', 'home', 'away'), key),
                   as_of=entry['as_of'], kickoff_utc=entry['kickoff_utc'])
        quotes = audit.quotes_for(row, raw[key], Counter())
        rates = entry['cohort_rates']
        if original.get('schema', 1) >= 2:
            path = entry['archive']
            if path not in original['inputs_sha256']:
                raise ValueError(f'Archive is not in the source manifest: {path}')
            if path not in archives:
                archives[path] = json.loads((root / path).read_text())
            candidates = [r for r in archives[path] if audit.identity(r) == key and
                          r.get('as_of') == entry['as_of'] and audit.snapshot_rates(r) == rates]
            if not candidates:
                raise ValueError(f'Missing original decision snapshot: {key}')
            baseline = audit.production_choice(candidates[0], rates, quotes, False)
            proposed = audit.production_choice(candidates[0], rates, quotes, True)
        else:
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


def recover_evidence(root=ROOT, *, warehouse=None):
    """Read-only recovery of archive/quote/result links, NEVER certification.

    Reuse the authoritative morning/late-addition loader, strict API quote
    validator, and exact-parent validator. No retrospective contract assignment,
    outcome-time invention, registry writes, provider calls or ticket builds.
    """
    from scripts.audit_recent_picks import load_archived_picks_with_receipt
    from edgefactory.enh_registry import enhancement_cohort_evidence, enhancement_price_context
    from edgefactory.consensus_contracts import _remine_key, _score_pair

    root = Path(root)
    inputs = {}

    def read(path):
        raw = path.read_bytes()
        inputs[str(path.relative_to(root))] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    registry = read(root / 'localdata/enhancement_registry.json')
    records = [dict(r, market=k.split('@')[0]) for k, e in registry['markets'].items()
               for r in e.get('records', [])]
    if not records:
        return {'status': 'no_retained_records', 'inputs_sha256': inputs}
    start, end = min(r['date'] for r in records), max(r['date'] for r in records)
    rows, receipt = load_archived_picks_with_receipt(start, end, localdata=root / 'localdata')
    # Witness the actual input bytes, not just the reconstructed values.
    for pattern in ('picks_????-??-??.json', 'picks_morning_????-??-??.json'):
        for path in (root / 'localdata').glob(pattern):
            if start <= path.stem[-10:] <= end:
                read(path)
    by_fixture, raw_quotes = defaultdict(list), defaultdict(list)
    for row in rows:
        by_fixture[audit.identity(row)].append(row)
    for source in ('oddspapi', 'theoddsapi'):
        for month in sorted({r['date'][:7] for r in records}):
            path = root / 'localdata' / f'{source}_odds_{month}.csv.gz'
            if not path.exists():
                continue
            inputs[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
            with gzip.open(path, 'rt') as handle:
                for line, row in enumerate(csv.DictReader(handle), 2):
                    key = audit.identity(row)
                    if key in by_fixture:
                        raw_quotes[key].append((source, row, str(path.relative_to(root)), line))
    overlay = defaultdict(set)
    for row in read(root / 'localdata/settled_results.json').get('rows', []):
        pair = _score_pair(row)
        if pair is not None:
            overlay[audit.identity(row)].add(pair)
    direct = defaultdict(set)
    if warehouse is not None:
        import duckdb
        with duckdb.connect(str(warehouse), read_only=True) as con:
            tables = {r[0] for r in con.execute('SHOW TABLES').fetchall()}
            # Raw self-scoring sources only. No results_donor, Forebet, or
            # convenience *_settled views which may have inherited its scores.
            for source in ('zulubet', 'statarea', 'vitibet', 'scoutingstats',
                           'prosoccer', 'bettingclosed', 'betexplorer_settled'):
                if source not in tables:
                    continue
                cursor = con.execute(f'SELECT * FROM {source} WHERE TRY_CAST(date AS DATE) BETWEEN ? AND ?', [start, end])
                columns = [c[0] for c in cursor.description]
                for values in cursor.fetchall():
                    row = dict(zip(columns, values))
                    if str(row.get('result_source') or '').casefold().startswith('forebet'):
                        continue
                    pair, key = _score_pair(row), _remine_key(row)
                    if pair is not None and key is not None:
                        direct[key].add(pair)
    current = read(root / 'localdata/edges_consensus.json')
    active = {e.get('contract_id') for e in current.get('edges', []) if e.get('status') == 'certified'}
    counts, blockers, cells, pool_counts = Counter(), Counter(), defaultdict(set), Counter()
    details = []

    def link(row, candidate):
        key = audit.identity(row)
        decision, kickoff = audit.instant(row.get('as_of')), audit.instant(row.get('kickoff_utc'))
        if decision is None or kickoff is None or not decision < kickoff:
            return None, 'missing_or_late_decision'
        source, book = candidate.get('enhancement_price_source'), candidate.get('enhancement_price_book')
        if source not in ('oddspapi', 'theoddsapi'):
            return None, 'capture_source_not_covered'
        raw = [(s, r) for s, r, _, _ in raw_quotes[key] if s == source and r.get('bookmaker') == book]
        rejected = Counter()
        quotes = audit.quotes_for(row, raw, rejected)
        quote = quotes.get(audit.MARKET_PRICE_MAP.get(candidate.get('recommended_enhancement')))
        if not quote or quote['price'] != candidate.get('enhancement_price'):
            return None, 'no_exact_predecision_quote:' + (rejected.most_common(1)[0][0] if rejected else 'missing_or_price_changed')
        candidate = dict(candidate, enhancement_price_at=quote['captured_at'], enhancement_price_kickoff=row['kickoff_utc'])
        context = enhancement_price_context(candidate)
        witnesses = [{'file': path, 'csv_line': line} for s, r, path, line in raw_quotes[key]
                     if s == source and r.get('bookmaker') == book
                     and (r.get('market'), r.get('selection')) == audit.MARKET_PRICE_MAP.get(candidate['recommended_enhancement'])
                     and audit.number(r.get('odds')) == quote['price']
                     and audit.instant(r.get('captured_at')) == audit.instant(quote['captured_at'])]
        return dict(context=context, quote=quote, capture_witnesses=witnesses,
                    archive_row_sha256=hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest(),
                    overlay_scores=sorted(overlay[key]), raw_donor_scores=sorted(direct.get(_remine_key(row), set())),
                    exact_parent_cohort_valid=enhancement_cohort_evidence(candidate) is not None,
                    active_contract=row.get('contract_id') in active,
                    result_availability_before_decision=None), None

    def candidates(row):
        for note in row.get('event_notes') or []:
            yield dict(row, **{k: v for k, v in note.items() if k.startswith('enhancement_price')},
                       recommended_enhancement=note.get('market'), enhancement_probability=None,
                       enhancement_cohort_rate=note.get('cohort_rate'), enhancement_cohort_n=note.get('cohort_n'),
                       enhancement_cohort_contract_id=note.get('cohort_contract_id'),
                       enhancement_cohort_as_of_exclusive=note.get('cohort_as_of_exclusive'))
        if row.get('recommended_enhancement'):
            yield row

    for rec in records:
        key = audit.identity(rec)
        if not rec.get('home') and ' vs ' in rec.get('match', ''):
            home, away = rec['match'].split(' vs ', 1)
            key = rec['date'], audit.name(home), audit.name(away)
        stages, matches, reasons = set(), [], Counter()
        if by_fixture[key]:
            stages.add('archive_fixture_found')
        for row in by_fixture[key]:
            if row.get('contract_schema') == 'post_forebet_v1' and row.get('contract_id') == rec.get('rule'):
                stages.add('exact_parent_archive')
            for candidate in candidates(row):
                if (candidate.get('recommended_enhancement') != rec['market']
                        or candidate.get('enhancement_price') != rec['price']
                        or candidate.get('enhancement_price_source') != rec['source']
                        or not candidate.get('enhancement_price_book')):
                    continue
                stages.add('archive_price_book_source_match')
                match, reason = link(row, candidate)
                if reason:
                    reasons[reason] += 1
                    continue
                stages.add('predecision_quote_join')
                scores = match['overlay_scores']
                if len(scores) != 1 or audit.check_enhancement_hit(rec['market'], row.get('pick'), *scores[0]) != rec['hit']:
                    reasons['result_missing_conflicting_or_disagrees'] += 1
                    continue
                stages.add('overlay_result_agrees')
                if (match['context'] and match['context']['contract_id'] == rec.get('rule')
                        and match['exact_parent_cohort_valid']):
                    stages.add('exact_parent_context_linked')
                    if len(match['raw_donor_scores']) == 1 and match['raw_donor_scores'] == scores:
                        stages.add('raw_donor_result_agrees')
                if match not in matches:
                    matches.append(match)
        counts.update(stages)
        blockers.update(reasons)
        if str(rec.get('rule') or '').startswith('pfc_'):
            details.append(dict(date=rec['date'], match=rec['match'], market=rec['market'],
                                rule=rec['rule'], stages=sorted(stages), blockers=dict(reasons), links=matches))
    # Complete archived candidate pool, not just the six recorded recommendations.
    for row in rows:
        if row.get('contract_schema') != 'post_forebet_v1':
            continue
        seen = set()
        for candidate in candidates(row):
            market = candidate.get('recommended_enhancement')
            if market in seen or not candidate.get('enhancement_price'):
                continue
            seen.add(market)
            match, reason = link(row, candidate)
            if reason:
                pool_counts[reason] += 1
                continue
            context = match['context']
            if not context or not match['exact_parent_cohort_valid']:
                pool_counts['no_valid_exact_parent_context'] += 1
                continue
            pool_counts['linked_quote_and_parent'] += 1
            if len(match['raw_donor_scores']) != 1:
                pool_counts['raw_result_missing_or_conflicting'] += 1
                continue
            group = tuple(context[k] for k in ('contract_id', 'selection', 'league', 'book', 'source', 'price')) + (market,)
            cells[group].add(audit.identity(row))
    return dict(status='read_only_retrospective_links_not_certification', registry_records=len(records),
                registry_stages=dict(counts), registry_quote_blockers=dict(blockers),
                archive_receipt=receipt, post_forebet_records=details, candidate_pool=dict(pool_counts),
                largest_raw_result_exact_cell=max((len(v) for v in cells.values()), default=0) if warehouse is not None else None,
                raw_results_checked=warehouse is not None, inputs_sha256=inputs,
                limits=['API capture joins use full names/orientation; no fuzzy, truncated or outcome-based matching.',
                        'Overlay agreement alone does not establish independent score origin or historical availability.',
                        'No record was promoted, backdated, assigned a new contract, or written to the registry.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--source-report', type=Path, help='Schema 1 or 2 audit; all input hashes must match')
    args = parser.parse_args()
    if args.out and args.out.resolve().is_relative_to((ROOT / 'localdata').resolve()):
        parser.error('audit output must not overwrite operational localdata')
    text = json.dumps(competition(source=args.source_report), indent=2, allow_nan=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end='')
