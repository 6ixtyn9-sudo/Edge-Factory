"""Hermetic local calibration/capacity probe, not a production profile.

Run with .venv/bin/python docs/operator/controls/audit_resource_control.py.
Outputs JSON to stdout; no repository data is written.
"""
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
from edgefactory.ml_consensus_audit import freeze, thaw, canonical, CaptureLimit
from edgefactory.ml_fade_research import FROZEN_FEATURE_COLS
from edgefactory.phase5_k import feature_vector


def sizeof_tree(value):
    if type(value) is tuple:
        return sys.getsizeof(value) + sum(sizeof_tree(v) for v in value)
    return sys.getsizeof(value)


def capture_measure(value):
    times = []
    for _ in range(2000):
        start = time.perf_counter_ns()
        private, charge, estimate = freeze(value)
        times.append(time.perf_counter_ns() - start)
    tracemalloc.start()
    copied = thaw(private)
    encoded = canonical(copied).encode('utf-8')
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {'retained_actual_upper': sizeof_tree(private), 'retained_charge': charge,
            'serialized_bytes': len(encoded), 'serialized_estimate': estimate,
            'writer_copy_json_peak': peak, 'capture_p99_us': sorted(times)[1979]/1000,
            'samples': len(times)}


def main():
    numeric = {'x': [float(i) for i in range(512)]}
    # Actual supported feature names; every vector input is legitimately
    # missing in this synthetic dark-source capacity control. The contract
    # requires one full seven-member fallback receipt for each imputation.
    fallbacks = []
    def actual_fallback(col, value, origin):
        fallbacks.append({'feature_name': col, 'stage': 'vector_imputation', 'value': value,
            'unit': {'state': 'missing', 'value': None, 'reason': 'receipt_not_exposed'},
            'origin': {'default_fallback': 'code_default',
                       'unknown_column_zero': 'unknown_column_zero_default'}[origin],
            'dependency_name': 'feature_contract', 'origin_verification': 'observed'})
    feature_vector({}, {'feature_cols': list(FROZEN_FEATURE_COLS)}, audit_receipt=actual_fallback)
    receipt = {'fallbacks': fallbacks}
    def strings(v):
        if type(v) is str: return len(v)
        if type(v) is dict: return sum(len(k)+strings(x) for k,x in v.items())
        if type(v) in (tuple,list): return sum(strings(x) for x in v)
        return 0
    try:
        freeze(receipt)
        state = 'admitted'
    except CaptureLimit as error:
        state = str(error)
    result = {'runtime': sys.version, 'platform': platform.platform(),
              'numeric_512': capture_measure(numeric),
              'full_fallback_capacity': {'features': len(fallbacks),
                  'required_string_codepoints': strings(receipt), 'allowed_codepoints': 1024,
                  'result': state, 'fixture_sha256': hashlib.sha256(canonical(receipt).encode()).hexdigest()},
              'scope': 'synthetic copy/JSON calibration only; no RSS or whole-hook p99 claim'}
    assert result['numeric_512']['retained_actual_upper'] <= result['numeric_512']['retained_charge']
    assert result['numeric_512']['writer_copy_json_peak'] <= 2*1024*1024
    assert state == 'string limit'
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
