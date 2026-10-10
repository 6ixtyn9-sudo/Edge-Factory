"""Synthetic paired evaluator/downstream controls; no network or live writes."""
import contextlib
import copy
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import tempfile
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import picks_today as pt
import auto_tickets as at
from edgefactory import ml_consensus_audit as audit
from edgefactory.ml_fade_research import FadeResearchCollector

DAY = '2026-06-01'
NOW = datetime(2026, 6, 1, 10, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def synthetic_runtime_admission(monkeypatch):
    # Exercise real worker/storage/parity paths on CI, NOT runtime calibration.
    # The unpatched admission policy has separate refusal/acceptance controls.
    from edgefactory import ml_consensus_audit
    monkeypatch.setattr(ml_consensus_audit, '_runtime_supported', lambda: True)


@pytest.mark.parametrize('mode', ['disabled', 'enabled', 'serialization', 'saturation', 'disk', 'startup', 'timeout'])
def test_paired_operational_artifacts(mode, monkeypatch, tmp_path):
    monkeypatch.setenv('EDGE_FACTORY_MCP_AUDIT', '1')
    monkeypatch.setattr(pt, 'load_ml_rules_and_model', lambda: (
        [{'rule': 'ml-meta avg_p>=50'}], {'coef': [.1], 'intercept': 2., 'feature_cols': ['fb_p']}))
    monkeypatch.setattr(pt, 'load_ml_fade_rules', lambda: [{'rule': 'ml-fade avg_p>=50'}])
    monkeypatch.setattr(pt, 'get_rolling_hit_rate_last_14d', lambda day: .75)
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path)
    monkeypatch.setattr(at, 'STATE_FILE', tmp_path / 'tickets.json')
    data = {s: {key: {'home': home, 'away': away, 'league': 'Test League',
                      'kickoff': DAY+'T18:00:00+00:00', 'p1': 75, 'px': 15, 'p2': 10,
                      'odd1': 1.5, 'odd2': 3.}
                for key, home, away in [('f1', 'Alpha', 'Beta'), ('f2', 'Gamma', 'Delta')]}
            for s in ('forebet', 'zulubet', 'statarea')}
    thresholds = {3: {'n_way': 3, 'threshold': 60, 'rule': '3way-unanimous avg_p>=60', 'display_rule': '3way'}}

    def exercise(handle):
        inputs = copy.deepcopy(data)
        research = FadeResearchCollector()
        fixture = []
        console = io.StringIO()
        with contextlib.redirect_stderr(console):
            rows, vetoes, upcoming = pt.eval_1x2(
                DAY, inputs, thresholds, source_weights={}, research_collector=research,
                fixture_audit=fixture, mcp_audit=handle)
        raw = copy.deepcopy(rows)
        kept, skips = pt.filter_operational_pre_match_picks(rows, as_of=NOW, min_lead=30)
        collapsed, removed = pt.collapse_final_operational_picks(kept, mcp_audit=handle)
        frozen = copy.deepcopy(collapsed[:1])
        frozen_bytes = json.dumps(frozen, sort_keys=True)
        archived = pt.merge_day_archive_rows(frozen, collapsed, DAY)
        assert json.dumps(frozen, sort_keys=True) == frozen_bytes
        legs = [{'match': r['match'], 'pick': r['pick'].upper(), 'prob': r['avg_p']/100,
                 'odds': r['odds'], 'row': r} for r in collapsed]
        accas = at.select_accas(legs, min_accas=1, max_accas=1, legs_per_acca=2)
        assert len(accas) == 1  # Non-vacuous ticket selection.
        plan = [{'legs': group, 'stake_pct': 10.0} for group in accas]
        state = at.fresh_state()
        at.upsert_slip(state, DAY, plan, freeze_at=NOW)
        ticket_bytes = at.STATE_FILE.read_bytes()
        freeze_before = copy.deepcopy(at.frozen_entry(state, DAY))
        at.record_freeze(state, DAY, NOW.replace(hour=12))
        assert at.frozen_entry(state, DAY) == freeze_before
        payload = {'raw': raw, 'collapsed': collapsed, 'archived': archived,
                   'sources': inputs, 'vetoes': vetoes, 'upcoming': upcoming,
                   'research': research.finalize(), 'fixture_audit': fixture,
                   'pre_match_skips': skips, 'removed': removed, 'ticket': state,
                   'console': console.getvalue(), 'freeze_footer': at.freeze_footer(freeze_before)}
        assert inputs == data
        return json.dumps(payload, sort_keys=True, allow_nan=False), ticket_bytes

    baseline = exercise(None)
    owner = tempfile.TemporaryDirectory()
    release = threading.Event()
    handle = None
    try:
        if mode == 'startup':
            from edgefactory.ml_consensus_storage import TemporarySpool
            with monkeypatch.context() as patch:
                def refused(*args): raise OSError('startup fault')
                patch.setattr(TemporarySpool, 'reserve', refused)
                handle = audit.TemporaryAudit(owner, trading_date=DAY, invocation_id=mode, code_sha='0'*40)
                assert handle.done.wait(1) and handle.state == 'FAILED'
        else:
            with monkeypatch.context() as patch:
                if mode == 'disabled': patch.delenv('EDGE_FACTORY_MCP_AUDIT')
                handle = audit.TemporaryAudit(owner, trading_date=DAY, invocation_id=mode, code_sha='0'*40)
            if mode != 'disabled': assert handle.ready.wait(1) and handle.state == 'READY'
        if mode == 'disk':
            def disk_fault(*args): raise OSError('disk fault')
            monkeypatch.setattr(handle, '_emit', disk_fault)
            handle.try_capture('emission', {'row': 0})
            assert handle.done.wait(1) and handle.state == 'FAILED'
        elif mode == 'saturation':
            from edgefactory.ml_consensus_audit import POOL_BYTES
            handle._reserved = POOL_BYTES
        elif mode == 'timeout':
            entered = threading.Event()
            original = handle._prepare
            def stalled(*args):
                entered.set()
                release.wait(2)
                return original(*args)
            monkeypatch.setattr(handle, '_prepare', stalled)
            handle.try_capture('emission', {'row': 0})
            assert entered.wait(1)
            handle.finish(0)
            assert handle.state == 'ABORTED'
        with monkeypatch.context() as patch:
            if mode == 'serialization':
                def invalid(*args): raise ValueError('serialization fault')
                patch.setattr(audit, 'canonical', invalid)
            actual = exercise(handle)
            if mode not in ('timeout', 'disabled'): handle.finish()
        assert actual == baseline
    finally:
        release.set()
        if handle is not None:
            handle.finish()
            if handle._thread: assert handle.done.wait(1)
        owner.cleanup()
