"""Temporary development collector controls, not production acceptance."""
import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from edgefactory.ml_consensus_audit import TemporaryAudit, freeze, thaw, CaptureLimit, safe_capture
import picks_today as pt


def test_disabled_no_storage_or_factory(monkeypatch):
    monkeypatch.delenv('EDGE_FACTORY_MCP_AUDIT', raising=False)
    with tempfile.TemporaryDirectory() as unused:
        h = TemporaryAudit(None, trading_date='2026-06-01', invocation_id='test', code_sha='0'*40)
        safe_capture(h, 'inference', lambda: pytest.fail('OFF constructed payload'))
        assert h.state == 'DISABLED'
        assert not list(Path(unused).iterdir())


def test_copy_limits():
    source = {'x': [1.2, None]}
    private, charge, estimate = freeze(source)
    source['x'][0] = 9
    assert thaw(private) == {'x': [1.2, None]}
    assert charge > 0 and estimate > 0
    for invalid in [float('nan'), 'a'*1025, {'x': object()}, {'x': '\ud800'}]:
        with pytest.raises((CaptureLimit, UnicodeError)):
            freeze(invalid)
    cycle = []; cycle.append(cycle)
    with pytest.raises(CaptureLimit):
        freeze(cycle)


def test_inference_parity_and_close(monkeypatch):
    monkeypatch.setenv('EDGE_FACTORY_MCP_AUDIT', '1')
    monkeypatch.setattr(pt, 'load_ml_rules_and_model', lambda: ([], {'coef': [0.1], 'intercept': 0.0, 'feature_cols': ['fb_p']}))
    monkeypatch.setattr(pt, 'load_ml_fade_rules', lambda: [])
    monkeypatch.setattr(pt, 'get_rolling_hit_rate_last_14d', lambda day: .75)
    data = {s: {'fixture': {'home': 'Audit Home', 'away': 'Audit Away', 'league': 'Test League',
                          'p1': 70, 'px': 20, 'p2': 10}} for s in ('forebet', 'zulubet')}
    baseline = pt.eval_1x2('2026-06-01', data, {}, source_weights={})
    owner = tempfile.TemporaryDirectory()
    try:
        h = TemporaryAudit(owner, trading_date='2026-06-01', invocation_id='test', code_sha='0'*40)
        assert h.ready.wait(1) and h.state == 'READY'
        assert pt.eval_1x2('2026-06-01', data, {}, source_weights={}, mcp_audit=h) == baseline
        h.finish()
        assert h.state == 'CLOSED'
        records = [json.loads(line) for p in sorted(Path(owner.name).glob('*/records-*.jsonl')) for line in p.read_text().splitlines()]
        assert [r['record_type'] for r in records] == ['build_open', 'decision_observation', 'inference_observation', 'build_close']
        evidence = records[2]['body']['model_receipt']['value']
        assert evidence['x'] == [.7]
        assert records[-1]['body']['coverage'] == 'partial'
        class Broken:
            state = 'READY'
            def try_capture(self, *args):
                raise RuntimeError('audit only')
        assert pt.eval_1x2('2026-06-01', data, {}, source_weights={}, mcp_audit=Broken()) == baseline
    finally:
        owner.cleanup()


def test_fallback_actual_precedence():
    from edgefactory.phase5_k import feature_vector
    receipts = []
    model = {'feature_cols': ['fb_p', 'zb_p', 'sa_p', 'unknown'],
             'fallback_means': {'fb_p': .2, 'zb_p': .3, 'unknown': .8}}
    baseline = feature_vector({}, model, fallbacks={'fb_p': .4})
    actual = feature_vector({}, model, fallbacks={'fb_p': .4},
                            audit_receipt=lambda *v: receipts.append(v))
    assert actual == baseline
    assert [r[2] for r in receipts] == ['caller_override', 'payload_mean', 'default_fallback', 'unknown_column_zero']
    assert [r[1] for r in receipts] == actual[0]
    def broken(*args):
        raise RuntimeError('capture')
    assert feature_vector({}, model, fallbacks={'fb_p': .4}, audit_receipt=broken) == baseline


@pytest.fixture
def audit(monkeypatch):
    monkeypatch.setenv('EDGE_FACTORY_MCP_AUDIT', '1')
    owner = tempfile.TemporaryDirectory()
    handle = TemporaryAudit(owner, trading_date='2026-06-01', invocation_id='test', code_sha='0'*40)
    assert handle.ready.wait(1) and handle.state == 'READY'
    yield handle
    handle.finish()
    assert handle.done.wait(1)
    owner.cleanup()


def test_admission_before_factory_and_refund(audit):
    from edgefactory.ml_consensus_audit import CONTROL_BYTES, POOL_BYTES
    audit._producer.acquire()
    try:
        safe_capture(audit, 'emission', lambda: pytest.fail('contended factory'))
    finally:
        audit._producer.release()
    audit._reserved = POOL_BYTES
    safe_capture(audit, 'emission', lambda: pytest.fail('full factory'))
    audit._reserved = CONTROL_BYTES
    safe_capture(audit, 'emission', lambda: {'bad': object()})
    assert audit._reserved == CONTROL_BYTES and audit._count == 0
    audit.try_close()
    safe_capture(audit, 'emission', lambda: pytest.fail('closed factory'))


def test_queue_no_overwrite_and_close(audit, monkeypatch):
    import threading
    entered, release = threading.Event(), threading.Event()
    original = audit._prepare
    def prepare(*args):
        entered.set()
        assert release.wait(1)
        return original(*args)
    monkeypatch.setattr(audit, '_prepare', prepare)
    audit.try_capture('emission', {'row': 0})
    assert entered.wait(1)
    for n in range(1, 6):
        audit.try_capture('emission', {'row': n})
    audit.try_close()
    release.set()
    audit.finish()
    records = [json.loads(line) for p in audit._directory.glob('records-*.jsonl') for line in p.read_text().splitlines()]
    assert [r['body']['row'] for r in records if r['record_type'] == 'emission_observation'] == list(range(6))
    assert audit._count == 0


def test_timeout_latched(audit, monkeypatch):
    import threading
    entered, release = threading.Event(), threading.Event()
    original = audit._prepare
    def prepare(*args):
        entered.set()
        release.wait(1)
        return original(*args)
    monkeypatch.setattr(audit, '_prepare', prepare)
    audit.try_capture('emission', {'row': 0})
    assert entered.wait(1)
    audit.finish(0)
    assert audit.state == 'ABORTED'
    release.set()
    assert audit.done.wait(1)
    assert audit.state == 'ABORTED'
    assert not (audit._directory / 'build-manifest.json').exists()


def test_disk_failure(audit, monkeypatch):
    def fail(*args):
        raise OSError('disk full')
    monkeypatch.setattr(audit, '_emit', fail)
    audit.try_capture('emission', {'row': 0})
    assert audit.done.wait(1)
    assert audit.state == 'FAILED' and audit._count == 0
    assert not (audit._directory / 'build-manifest.json').exists()


def test_collapse_per_ordering():
    from itertools import permutations
    rows = [dict(date='2026-06-01', home='Alpha', away='Beta', match='Alpha vs Beta',
                 market='1x2', pick='home', avg_p=70, rule=rule) for rule in ('a', 'b')]
    class Capture:
        state = 'READY'
        def __init__(self):
            self.receipts = []
        def try_capture(self, stage, payload):
            self.receipts.append((stage, payload))
    for order in permutations(rows):
        baseline = pt.collapse_final_operational_picks(list(order))
        capture = Capture()
        assert pt.collapse_final_operational_picks(list(order), capture) == baseline
        assert capture.receipts[0][1]['representative'] == 0
        assert capture.receipts[0][1]['members'] == [0, 1]


def test_all_emission_paths_parity(monkeypatch, audit):
    import copy
    monkeypatch.setattr(pt, 'load_ml_rules_and_model', lambda: (
        [{'rule': 'ml-meta avg_p>=50'}], {'coef': [.1], 'intercept': 2., 'feature_cols': ['fb_p']}))
    monkeypatch.setattr(pt, 'load_ml_fade_rules', lambda: [{'rule': 'ml-fade avg_p>=50'}])
    monkeypatch.setattr(pt, 'get_rolling_hit_rate_last_14d', lambda day: .75)
    data = {s: {'f': {'home': 'Alpha', 'away': 'Beta', 'league': 'Test League',
                     'p1': 75, 'px': 15, 'p2': 10, 'odd1': 1.5, 'odd2': 3.}} for s in ('forebet', 'zulubet', 'statarea')}
    thresholds = {3: {'n_way': 3, 'threshold': 60, 'rule': '3way-unanimous avg_p>=60', 'display_rule': '3way'}}
    before = copy.deepcopy(data)
    baseline = pt.eval_1x2('2026-06-01', data, thresholds, source_weights={})
    class Capture:
        state = 'READY'
        def __init__(self): self.receipts = []
        def try_capture(self, stage, payload):
            self.receipts.append((stage, copy.deepcopy(payload)))
    h = Capture()
    assert pt.eval_1x2('2026-06-01', data, thresholds, source_weights={}, mcp_audit=h) == baseline
    assert data == before
    emissions = [p for stage, p in h.receipts if stage == 'emission']
    assert [p['path'] for p in emissions] == ['ml_main', 'ml_fade', 'consensus_unanimous']
    assert [p['output'] for p in emissions] == [pt.emitted_fields(row) for row in baseline[0]]
    assert emissions[0]['score'] == emissions[1]['score']
    assert emissions[2]['probabilities'] == [.75, .75, .75]
    assert emissions[2]['score'] == 75
    assert pt.eval_1x2('2026-06-01', data, thresholds, source_weights={}, mcp_audit=audit) == baseline
    audit.finish()
    records = [json.loads(line) for p in audit._directory.glob('records-*.jsonl') for line in p.read_text().splitlines()]
    assert [r['body']['path'] for r in records if r['record_type'] == 'emission_observation'] == ['ml_main', 'ml_fade', 'consensus_unanimous']


def test_startup_failure(monkeypatch):
    monkeypatch.setenv('EDGE_FACTORY_MCP_AUDIT', '1')
    owner = tempfile.TemporaryDirectory()
    try:
        def fail(*args, **kwargs): raise OSError('startup')
        monkeypatch.setattr(Path, 'mkdir', fail)
        h = TemporaryAudit(owner, trading_date='2026-06-01', invocation_id='test', code_sha='0'*40)
        assert h.done.wait(1)
        assert h.state == 'FAILED'
        safe_capture(h, 'emission', lambda: pytest.fail('failed factory'))
    finally:
        owner.cleanup()


def test_offline_inventory_integrity(audit):
    from edgefactory.ml_consensus_audit import read_temporary_build
    audit.try_capture('emission', {'row': 0})
    audit.finish()
    manifest, records = read_temporary_build(audit._directory)
    assert manifest['coverage'] == 'partial'
    assert len(records) == 3
    segment = audit._directory / manifest['files'][0]['name']
    segment.write_bytes(segment.read_bytes()[:-1])
    with pytest.raises(ValueError, match='size mismatch'):
        read_temporary_build(audit._directory)


def test_repeated_evaluation_ids_are_distinct(audit, monkeypatch):
    monkeypatch.setattr(pt, 'load_ml_rules_and_model', lambda: ([], {'coef': [.1], 'intercept': 0., 'feature_cols': ['fb_p']}))
    monkeypatch.setattr(pt, 'load_ml_fade_rules', lambda: [])
    monkeypatch.setattr(pt, 'get_rolling_hit_rate_last_14d', lambda day: .75)
    data = {source: {'f': {'home': 'Alpha', 'away': 'Beta', 'p1': 70, 'px': 20, 'p2': 10}}
            for source in ('forebet', 'zulubet')}
    for _ in range(2):
        pt.eval_1x2('2026-06-01', data, {}, source_weights={}, mcp_audit=audit)
    audit.finish()
    from edgefactory.ml_consensus_audit import read_temporary_build
    _, records = read_temporary_build(audit._directory)
    inferences = [r['body'] for r in records if r['record_type'] == 'inference_observation']
    assert len(inferences) == 2
    assert len({b['inference_id'] for b in inferences}) == 2
    assert len({b['occurrence_ref']['value']['id'] for b in inferences}) == 2


def test_termination_not_swallowed(audit):
    def terminate():
        raise SystemExit(17)
    with pytest.raises(SystemExit) as error:
        safe_capture(audit, 'emission', terminate)
    assert error.value.code == 17
    assert audit._count == 0


def test_serialization_estimate_violation_is_fatal(audit, monkeypatch):
    import edgefactory.ml_consensus_audit as module
    original = module.freeze
    def underestimated(value):
        private, charge, _ = original(value)
        return private, charge, 1
    monkeypatch.setattr(module, 'freeze', underestimated)
    audit.try_capture('emission', {'row': 0})
    assert audit.done.wait(1)
    assert audit.state == 'FAILED'
    assert not (audit._directory / 'build-manifest.json').exists()


def test_reader_checks_record_digest_not_only_file_inventory(audit):
    import hashlib
    from edgefactory.ml_consensus_audit import read_temporary_build, canonical
    audit.try_capture('emission', {'row': 0})
    audit.finish()
    manifest_file = audit._directory / 'build-manifest.json'
    manifest = json.loads(manifest_file.read_text())
    segment = audit._directory / manifest['files'][0]['name']
    records = [json.loads(line) for line in segment.read_text().splitlines()]
    records[1]['body']['row'] = 1
    raw = ''.join(canonical(r)+'\n' for r in records).encode()
    segment.write_bytes(raw)
    manifest['files'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
    manifest['files'][0]['size_bytes'] = len(raw)
    manifest_file.write_text(canonical(manifest)+'\n')
    with pytest.raises(ValueError, match='record digest mismatch'):
        read_temporary_build(audit._directory)


def test_capacity_contract_refuses_full_fallbacks():
    from edgefactory.phase5_k import feature_vector
    from edgefactory.ml_fade_research import FROZEN_FEATURE_COLS
    receipts = []
    def actual(col, value, origin):
        receipts.append({'feature_name': col, 'stage': 'vector_imputation', 'value': value,
                         'unit': None, 'origin': origin, 'dependency_name': 'feature_contract',
                         'origin_verification': 'observed'})
    feature_vector({}, {'feature_cols': list(FROZEN_FEATURE_COLS)}, audit_receipt=actual)
    assert len(receipts) == 26
    with pytest.raises(CaptureLimit, match='string limit'):
        freeze({'fallbacks': receipts})
