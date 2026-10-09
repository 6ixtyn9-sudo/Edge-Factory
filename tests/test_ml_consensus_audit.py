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
    with tempfile.TemporaryDirectory() as directory:
        # Retain the actual owner, not its string path.
        pass
    owner = tempfile.TemporaryDirectory()
    try:
        h = TemporaryAudit(owner, trading_date='2026-06-01', invocation_id='test', code_sha='0'*40)
        assert h.ready.wait(1) and h.state == 'READY'
        assert pt.eval_1x2('2026-06-01', data, {}, source_weights={}, mcp_audit=h) == baseline
        h.finish()
        assert h.state == 'CLOSED'
        records = [json.loads(line) for p in sorted(Path(owner.name).glob('*/records-*.jsonl')) for line in p.read_text().splitlines()]
        assert [r['record_type'] for r in records] == ['build_open', 'inference_observation', 'build_close']
        evidence = records[1]['body']['model_receipt']['value']
        assert evidence['x'] == [.7]
        assert records[-1]['body']['coverage'] == 'partial'
        class Broken:
            state = 'READY'
            def try_capture(self, *args):
                raise RuntimeError('audit only')
        assert pt.eval_1x2('2026-06-01', data, {}, source_weights={}, mcp_audit=Broken()) == baseline
    finally:
        owner.cleanup()
