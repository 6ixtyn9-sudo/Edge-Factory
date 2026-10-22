"""Adversarial audit regressions: populations, retention, provenance and ENH finance."""
import hashlib
import importlib.util
import json
from pathlib import Path

import duckdb
import pytest

from edgefactory import enh_registry as er, consensus_contracts as cc
from scripts import assay_purity as assay, picks_today as pt, auto_tickets as at

ROOT = Path(__file__).resolve().parents[1]


def test_assay_unpriced_losses_cannot_change_roi_or_inflate_verdict_n():
    con = duckdb.connect()
    con.create_function('classify_competition', lambda s: 'league', return_type='VARCHAR')
    con.execute('CREATE TABLE sample(date DATE, home VARCHAR, away VARCHAR, league VARCHAR, pick VARCHAR, outcome VARCHAR, pick_odds DOUBLE)')
    # Three priced wins; 36 unpriced losses. A positive ROI is not enough to
    # turn these THREE priced observations into an ALLOW with n=39.
    con.execute("INSERT INTO sample SELECT CURRENT_DATE, 'Alpha', 'Bravo', 'Test', 'home', 'home', 2.1 FROM range(3)")
    con.execute("INSERT INTO sample SELECT CURRENT_DATE, 'Alpha', 'Bravo', 'Test', 'home', 'away', NULL FROM range(36)")
    league, team, odds, comp, niche = assay.assay_edge(con, {'view': 'sample', 'rule': 'test'}, 60)
    assert league and team and odds and comp and niche
    row = next(iter(league.values()))
    assert row['n'] == row['n_priced'] == 3
    assert row['n_settled'] == 39
    assert row['roi'] == pytest.approx(1.1)
    assert row['recent_roi'] is None
    assert row['verdict'] == 'UNKNOWN'
    for group in (team, comp):
        assert all(r['n'] == 3 and r['verdict'] == 'UNKNOWN' for r in group.values())
    con.close()


@pytest.mark.parametrize('price', [float('nan'), float('inf'), 1., -1.])
def test_invalid_prices_cannot_fund_purity_evidence(price):
    con = duckdb.connect()
    con.execute('CREATE TABLE sample(pick VARCHAR, outcome VARCHAR, pick_odds DOUBLE)')
    con.execute("INSERT INTO sample VALUES ('home','away',?)", [price])
    league, *_ = assay.assay_edge(con, {'view': 'sample'}, 60)
    row = next(iter(league.values()))
    assert row['n'] == 0 and row['roi'] is None and row['verdict'] == 'UNKNOWN'
    con.close()


def test_records_survive_more_than_old_cap_and_keys_remain_idempotent(tmp_path):
    path = er.registry_path(tmp_path)
    path.parent.mkdir(parents=True)
    records = [dict(date='2026-10-01', match=f'A{i} vs B', price=2., hit=True) for i in range(400)]
    entry = er._blank()
    entry.update(n=400, hits=400, records=records, inv_price_sum=200., multi_n=400)
    path.write_text(json.dumps({'markets': {er.versioned('match_over_25'): entry}}))
    er.record_outcome(tmp_path, date_='2026-10-02', match='Last vs B', market='match_over_25', price=2., hit=True, today='2026-10-03')
    row = json.loads(path.read_text())['markets'][er.versioned('match_over_25')]
    assert row['n'] == len(row['records']) == 401
    # Key absent from processed but retained in the ledger must not double count.
    assert not er.record_outcome(tmp_path, date_='2026-10-01', match='A0 vs B', market='match_over_25', price=2., hit=True)['recorded']


def test_incomplete_ledger_cannot_certify_or_derive_a_data_floor():
    entry = er._blank()
    entry.update(n=447, hits=447, status='ELIGIBLE', multi_n=447, inv_price_sum=223.5,
                 records=[dict(date='2026-10-01', price=2, hit=True)] * 400)
    er._evaluate(entry, '2026-10-21')
    assert entry['status'] == 'PAPER' and entry['records_truncated']
    result = er.derive_floors({'markets': {er.versioned('match_over_25'): entry}}, '2026-10-21', parent_floors={'match_over_25': 1.3}, margin=.02)
    assert result['coverage']['records'] == 0


def test_missing_rolling_rate_never_becomes_perfect(monkeypatch, tmp_path):
    path = tmp_path / 'audit.json'
    path.write_text(json.dumps({'enhancements_audit': {'by_enhancement': {
        'missing': {'recommended': 10}, 'zero': {'recommended': 10, 'hit_rate': 0},
        'bad': {'recommended': 10, 'hit_rate': '1.0'}}}}))
    monkeypatch.setattr(pt, 'AUDIT_ROLLING_PATH', path)
    assert pt.load_rolling_audit_hit_rates() == {'zero': 0.}


def test_new_pick_output_does_not_publish_unknown_as_zero():
    picks = [{'enhancement_probability': 0.0}]
    pt.stamp_pick_evidence(picks, git_sha='measured-build', built_at='2026-10-21T00:00:00Z')
    assert picks[0]['enhancement_probability'] is None
    assert picks[0]['build_git_sha'] == 'measured-build'
    # An unprovable selection is WITHHELD from its row (evidence unavailable),
    # never published and never allowed to abort every other pick of the day.
    row = {'date': '2026-10-21', 'match': 'A vs B', 'recommended_enhancement': 'match_over_25',
           'enhancement_probability': .8, 'enhancement_label': 'Match Over 2.5 Goals'}
    out = pt.stamp_pick_evidence([row], git_sha='x', built_at='x')
    assert out == [('A vs B', 'match_over_25', 'no_valid_cohort_identity')]
    assert row['recommended_enhancement'] is None
    assert row['enhancement_probability'] is None
    assert row['enhancement_label'] is None
    assert 'no valid measured cohort identity' in row['enhancement_quarantined']


def test_new_snapshot_hash_is_order_independent_and_window_bound():
    def manifest(order):
        con = duckdb.connect()
        con.execute('CREATE TABLE scoutingstats(date DATE, home VARCHAR, away VARCHAR, p1 DOUBLE, px DOUBLE, p2 DOUBLE)')
        for home in order:
            con.execute("INSERT INTO scoutingstats VALUES ('2026-10-01',?,'Bravo',.6,.2,.2)", [home])
        coverage, *_ = cc.collect_observations(con, start='2026-10-01', as_of='2026-10-02', include_snapshot=True)
        con.close()
        return coverage['scoutingstats']
    left, right = manifest(['Alpha', 'Charlie']), manifest(['Charlie', 'Alpha'])
    assert left['observation_sha256'] == right['observation_sha256']
    assert left['rows'] == 2 and left['first_date'] == left['last_date'] == '2026-10-01'


def test_missing_financial_state_cannot_rebase_published_history(tmp_path):
    lane = at.ENHANCEMENT_LANE._replace(state_file=tmp_path / 'enhancement_tickets_state.json')
    (tmp_path / f'{lane.slip_prefix}_performance.json').write_text('{"bet_days":6}')
    with pytest.raises(RuntimeError, match='recovery required'):
        at.load_state(lane)
    lane.state_file.write_text('{broken')
    with pytest.raises(RuntimeError, match='unreadable financial state'):
        at.load_state(lane)


def test_enh_recovery_preserves_six_days_and_actual_later_stakes():
    audit = ROOT / 'docs/operator/audits/2026-10-21-enh-recovery'
    before = json.loads((audit / 'before-reset.json').read_text())
    after = json.loads((audit / 'after-reset.json').read_text())
    st = json.loads((ROOT / 'localdata/enhancement_tickets_state.json').read_text())
    assert st['history'][:6] == before['history']
    assert len(st['history']) >= 7
    # Oct 20 entry must match after-reset snapshot
    assert st['history'][6]['date'] == after['history'][-1]['date'] == '2026-10-20'
    assert st['history'][6]['staked_pct'] == after['history'][-1]['staked_pct'] == 12.5
    assert st['history'][6]['returned_pct'] == after['history'][-1]['returned_pct'] == 27.0
    # Day 7 (Oct 21) was subsequently settled live without rewriting past history
    if len(st['history']) >= 8:
        assert st['history'][7]['date'] == '2026-10-21'
        assert st['history'][7]['staked_pct'] == 14.3125
    assert st['integrity_recovery']['new_settlements_executed'] == 0
    assert hashlib.sha256((audit / 'before-reset.json').read_bytes()).hexdigest() == st['integrity_recovery']['before_reset_sha256']


def test_held_purity_verdicts_are_not_reused():
    pick = dict(contract_schema=cc.SCHEMA, edge_rule='pfc_uncovered')
    ctx = pt.lookup_context({'roi_population_status': 'unverified_legacy_population'}, pick)
    # The hold is declared, not silent: the status names the mode, and with no
    # negative verdict present every dimension stays UNKNOWN (never promoted).
    assert ctx['purity_evidence_status'] == 'hold_negative_only'
    assert ctx['league'] == ctx['odds_band'] == 'UNKNOWN'


def test_legacy_consensus_normalizes_each_vector_and_filters_identity(tmp_path, monkeypatch):
    import csv, gzip
    from edgefactory import warehouse
    cols = ('date home away hs gs p1 px p2 odd1 oddx odd2 ht_hs ht_gs p_under p_over odd_under odd_over p_gg p_ng odd_gg odd_ng p1_ht px_ht p2_ht kelly pred_hs pred_gs goalsavg league status tip p_o15 p_o25 p_o35').split()
    for source, probs in [('forebet', [60, 25, 15]), ('zulubet', [.6, .25, .15]), ('statarea', [60, 25, 15])]:
        with gzip.open(tmp_path / f'{source}_2026-10.csv.gz', 'wt') as f:
            writer = csv.DictWriter(f, fieldnames=cols); writer.writeheader()
            for home in ['Alpha Town', 'A']:
                row = dict.fromkeys(cols, '')
                row.update(date='2026-10-01', home=home, away='Bravo United', hs=2, gs=1,
                           p1=probs[0], px=probs[1], p2=probs[2], odd1=2., oddx=3., odd2=4., league='Test')
                writer.writerow(row)
    monkeypatch.setattr(warehouse, 'LOCALDATA', tmp_path)
    con = warehouse.connect()
    assert con.execute('SELECT count(*) FROM forebet').fetchone()[0] == 2
    assert con.execute('SELECT count(*) FROM forebet_settled').fetchone()[0] == 1
    assert con.execute('SELECT avg_p FROM consensus2').fetchone()[0] == pytest.approx(60)
    assert con.execute('SELECT avg_p FROM consensus3').fetchone()[0] == pytest.approx(60)
    con.close()


def test_financial_cache_cannot_discard_committed_history(tmp_path):
    import subprocess
    from scripts import phase5_persistence as persistence
    def git(*args):
        return subprocess.run(['git', *args], cwd=tmp_path, check=True, capture_output=True)
    git('init', '-q'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.invalid')
    p = tmp_path / persistence.ENH_STATE; p.parent.mkdir()
    first = {'date': '2026-10-19', 'staked_pct': 10, 'returned_pct': 0, 'accas': []}
    second = {'date': '2026-10-20', 'staked_pct': 12.5, 'returned_pct': 27, 'accas': []}
    head = {'bank': 104.5, 'history': [first, second], 'open_slips': []}
    p.write_text(json.dumps(head)); git('add', '.'); git('commit', '-qm', 'financial fixture')
    p.write_text(json.dumps({'bank': 114.5, 'history': [second], 'open_slips': []}))
    recovered = json.loads(persistence._retain_financial_state(tmp_path))
    assert recovered['bank'] == 104.5 and len(recovered['history']) == 2
    # A genuinely newer full ledger survives; no rollback on checkout.
    third = {'date': '2026-10-21', 'staked_pct': 5, 'returned_pct': 0, 'accas': []}
    p.write_text(json.dumps({'bank': 99.5, 'history': [first, second, third], 'open_slips': []}))
    assert json.loads(persistence._retain_financial_state(tmp_path))['bank'] == 99.5
    p.write_text(json.dumps({'bank': 123, 'history': [first, second, third], 'open_slips': []}))
    with pytest.raises(persistence.EvidenceMergeError, match='bank does not reconcile'):
        persistence._retain_financial_state(tmp_path)


def test_restored_registry_matches_all_original_counters():
    # 1. Verify archived recovery snapshot itself matches all original counters
    audit = ROOT / 'docs/operator/audits/2026-10-21-enh-recovery'
    receipt = json.loads((audit / 'registry-record-recovery.json').read_text())
    assert receipt['retained_after'] == 447
    assert receipt['verification']['hits'] == 293
    assert receipt['verification']['multi_n'] == 84

    # 2. Verify live registry preserves all recovered records and internally matches
    reg = json.loads((ROOT / 'localdata/enhancement_registry.json').read_text())
    row = reg['markets']['match_over_25@v1']
    records = row['records']
    assert len(records) == row['n'] >= 447
    assert len({(r['date'], r['match']) for r in records}) == row['n']
    assert sum(bool(r['hit']) for r in records) == row['hits']
    assert sum(bool(r.get('multi_source')) for r in records) == row['multi_n']
    assert sum((r['price'] - 1) if r['hit'] else -1 for r in records) == pytest.approx(row['profit'])
    assert sum(1 / r['price'] for r in records) == pytest.approx(row['inv_price_sum'])
    assert er.evidence_complete(row)

    # 3. All 47 recovered records from the recovery audit must remain present
    recovered_keys = {(r['date'], r['match']) for r in receipt['recovered_records']}
    live_keys = {(r['date'], r['match']) for r in records}
    assert recovered_keys.issubset(live_keys)


def test_cache_can_extend_a_partially_settled_day(tmp_path):
    import subprocess
    from scripts import phase5_persistence as persistence
    def git(*args):
        return subprocess.run(['git', *args], cwd=tmp_path, check=True, capture_output=True)
    git('init', '-q'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.invalid')
    p = tmp_path / persistence.ENH_STATE; p.parent.mkdir()
    a = {'stake_pct': 5, 'returned_pct': 0, 'won': False}
    h = {'date': '2026-10-20', 'staked_pct': 5, 'returned_pct': 0, 'accas': [a]}
    p.write_text(json.dumps({'bank': 95, 'history': [h], 'open_slips': []}))
    git('add', '.'); git('commit', '-qm', 'partial settlement fixture')
    b = {'stake_pct': 5, 'returned_pct': 10, 'won': True}
    h2 = dict(h, staked_pct=10, returned_pct=10, accas=[a, b])
    p.write_text(json.dumps({'bank': 100, 'history': [h2], 'open_slips': []}))
    assert json.loads(persistence._retain_financial_state(tmp_path))['bank'] == 100


def test_legacy_vector_guard_rejects_out_of_range_and_incoherent_inputs():
    from edgefactory.warehouse import _pmax_pct
    con = duckdb.connect()
    for vector in [(1.04, 0, 0), (70, 70, 0), (float('nan'), .2, .2)]:
        result = con.execute(f'SELECT {_pmax_pct("v")} FROM (SELECT ?::DOUBLE p1, ?::DOUBLE px, ?::DOUBLE p2, ?::DOUBLE pmax) v', [*vector, max(vector)]).fetchone()[0]
        assert result is None
    con.close()


def test_no_price_column_is_unknown_not_a_synthetic_loss():
    con = duckdb.connect()
    con.execute("CREATE TABLE sample AS SELECT 'home' pick, 'away' outcome")
    league, *_ = assay.assay_edge(con, {'view': 'sample'}, 60)
    row = next(iter(league.values()))
    assert row['n_settled'] == 1 and row['n_priced'] == row['n'] == 0
    assert row['roi'] is None and row['verdict'] == 'UNKNOWN'
    con.close()


@pytest.mark.parametrize('bank', [float('nan'), float('inf'), True])
def test_corrupt_bank_cannot_be_loaded_as_financial_state(tmp_path, bank):
    lane = at.ENHANCEMENT_LANE._replace(state_file=tmp_path / 'enhancement_tickets_state.json')
    state = at.fresh_state()
    state['bank'] = bank
    lane.state_file.write_text(json.dumps(state))
    with pytest.raises(RuntimeError, match='invalid financial state'):
        at.load_state(lane)


# ---- fail-closed purity hold (2026-10-21 second pass) -----------------------
def _hold_pick(rule='v_consensus2_base'):
    """A pick whose ONLY known contexts are promotions (ALLOW/BOOST)."""
    return dict(date='2026-10-21', market='1x2', pick='away', odds=1.42,
                league='il1', home='Alpha Town', away='Beta Town',
                sport='soccer', rule=rule, edge_rule=rule, bucket='CERTIFIED_CLEAN')


def _hold_registry(status):
    return {
        'roi_population_status': status,
        'contexts': {
            'league': {'soccer|il1|1x2|v_consensus2_base|away':
                       {'n': 40, 'roi': .05, 'verdict': 'ALLOW'}},
            'odds_band': {'soccer|1x2|v_consensus2_base|1.35-1.50':
                          {'n': 60, 'roi': .04, 'verdict': 'ALLOW'}},
            'team': {}, 'competition_type': {}, 'niche': {},
        },
        'contract_contexts': {},
    }


def test_held_registry_cannot_promote_a_pick_into_a_staked_bucket():
    pick = _hold_pick()
    active = pt.lookup_context(_hold_registry('priced_only'), pick)
    assert active['league'] == 'ALLOW' and active['odds_band'] == 'ALLOW'
    assert pt.bucket_pick(dict(pick), active, decay_verdict='HEALTHY') == 'CERTIFIED_CLEAN'

    held = pt.lookup_context(_hold_registry('unverified_legacy_population'), pick)
    assert held['purity_evidence_status'] == 'hold_negative_only'
    assert held['league'] == 'UNKNOWN' and held['odds_band'] == 'UNKNOWN'
    # UNKNOWN evidence may never reach the pushable "certified clean" bucket.
    assert pt.bucket_pick(dict(pick), held, decay_verdict='HEALTHY') == 'CAUTION'


def test_held_registry_never_releases_a_recorded_veto():
    pick = _hold_pick()
    reg = _hold_registry('unverified_legacy_population')
    reg['contexts']['league']['soccer|il1|1x2|v_consensus2_base|away'] = {
        'n': 39, 'roi': -8.23, 'verdict': 'VETO'}
    ctx = pt.lookup_context(reg, pick)
    assert ctx['league'] == 'VETO'
    assert pt.bucket_pick(dict(pick), ctx, decay_verdict='HEALTHY') == 'SKIPPED_VETO'


def test_hold_helper_keeps_negatives_and_drops_promotions():
    from edgefactory.veto_resolution import hold_to_negative_only, is_held, load_registry
    reg = _hold_registry('unverified_legacy_population')
    reg['contexts']['league']['soccer|x|1x2|r|home'] = {'n': 5, 'roi': .9, 'verdict': 'BOOST'}
    reg['contexts']['league']['soccer|y|1x2|r|home'] = {'n': 9, 'roi': -.2, 'verdict': 'CAUTION'}
    out = hold_to_negative_only(reg)
    verdicts = {k.split('|')[1]: v['verdict'] for k, v in out['contexts']['league'].items()}
    # il1 (ALLOW) and x (BOOST) are promotions -> dropped; y (CAUTION) stays.
    assert verdicts == {'y': 'CAUTION'}
    assert is_held(reg) and not is_held({'roi_population_status': 'priced_only'})
