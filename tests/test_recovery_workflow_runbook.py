"""Validate the complete copy/paste replacement without adding another workflow."""
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow():
    doc = (ROOT / 'docs/operator/POST-FOREBET-RECOVERY.md').read_text()
    text = doc.split('```yaml\n', 1)[1].rsplit('\n```', 1)[0]
    return yaml.safe_load(text)


def test_reference_restore_exact_original_path_and_current_state_restored_even_on_failure():
    wf = workflow()
    dispatch = wf.get('on', wf.get(True))['workflow_dispatch']
    assert 'recover_and_rebuild' in dispatch['inputs']['mode']['options']
    steps = wf['jobs']['run-autonomous-agent']['steps']
    ids = {s.get('id'): s for s in steps if s.get('id')}
    reference = ids['history_reference']
    assert reference['with'] == {'path': 'localdata', 'key': 'localdata-v2-39371954018'}
    merge = next(s for s in steps if 'history-recover' in s.get('run', ''))
    assert merge['if'].startswith('always()')
    assert 'history_stage.outcome' in merge['if']
    assert 'cache-hit' in merge['run']
    recovery = ids['recovery']['run']
    assert 'mine_consensus.py --activate' in recovery
    assert 'assay_purity.py' in recovery and 'decay_monitor.py' in recovery
    assert '--rebuild-unplaced' in recovery and '--no-settle' in recovery
    assert '--force' not in recovery and 'daily.py' not in recovery
    assert 'continue-on-error' not in ids['recovery']
    assert 'EDGE_FACTORY_ENH_COHORT_PARITY' in wf['jobs']['run-autonomous-agent']['env']
    for step in steps:
        if step.get('uses') == 'actions/cache/save@v4' or 'phase5_persistence.py persist' in step.get('run', ''):
            assert step['if'].startswith('success()')
    ordinary = next(s for s in steps if s['name'] == 'Execute Autonomous Smart Schedule')
    assert ordinary['if'] == "inputs.mode != 'recover_and_rebuild'"
    checks = [s for s in steps if s.get('run') == 'python3 scripts/phase5_persistence.py history-check']
    assert len(checks) >= 2


def test_all_inline_shell_and_summary_python_syntax_valid():
    for job in workflow()['jobs'].values():
        for step in job['steps']:
            if 'run' not in step:
                continue
            script = re.sub(r'\$\{\{.*?\}\}', 'TEST_VALUE', step['run'])
            result = subprocess.run(['bash', '-n'], input=script, text=True, capture_output=True)
            assert result.returncode == 0, (step['name'], result.stderr)
            if "<<'PY_EVIDENCE'" in script:
                inline = script.split("<<'PY_EVIDENCE'\n", 1)[1].rsplit('\nPY_EVIDENCE', 1)[0]
                compile(inline, '<workflow summary>', 'exec')
