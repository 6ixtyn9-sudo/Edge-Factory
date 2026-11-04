"""Rolling admission honors the approved residual budget, not a fixture ban."""

import hashlib
import json
import math
from datetime import timedelta

import pytest
from test_ml_paper import NOW
from test_ml_paper_rolling import run, slate

from edgefactory import ml_paper as mp


def modest_edge_slate(now=NOW):
    rows = slate(now)
    for row in rows:
        model = row['statistical_profile']['ml_model']
        # Native model fixture: 55% home rather than 70%, preserving all guards.
        model['intercept'] = [math.log(p) for p in (.2, .2, .35, .25)]
        model.pop('model_key')
        model['model_key'] = hashlib.sha256(
            json.dumps(model, sort_keys=True, allow_nan=False).encode()).hexdigest()
        row['statistical_profile']['ml_inputs']['model_key'] = model['model_key']
    return rows


def test_reuse_consumes_only_remaining_budget_without_rewriting_positions(tmp_path):
    originals = {}
    for minute in range(3):
        now = NOW + timedelta(minutes=minute)
        row = run(tmp_path, now, modest_edge_slate(now))
        assert row and row['accas']
        path = mp.rolling_receipt_path(tmp_path, row)
        originals[path] = path.read_bytes()
        report = mp.performance(mp.receipts(tmp_path), lambda _: None)
        assert report['paper_bank_units'] == 100
        assert report['paper_committed_units'] <= 5
        prior = mp._prior_open_fixture_micro_units(report)
        assert len(prior) == 2 and all(v <= 5_000_000 for v in prior.values())
        if minute:
            assert all(e['prior_open_stake_micro_units'] > 0 for e in row['fixture_concentration']['fixtures'])
        assert all(p.read_bytes() == blob for p, blob in originals.items())
    assert report['paper_committed_units'] == pytest.approx(5, abs=1e-6)
    assert run(tmp_path, NOW + timedelta(minutes=3), modest_edge_slate(NOW + timedelta(minutes=3))) is None
    assert len(mp.receipts(tmp_path)) == 3
    assert all(p.read_bytes() == blob for p, blob in originals.items())


def test_same_decision_id_does_not_publish_twice_even_with_residual_budget(tmp_path):
    first = run(tmp_path, rows=modest_edge_slate())
    original = mp.rolling_receipt_path(tmp_path, first).read_bytes()
    assert run(tmp_path, rows=modest_edge_slate()) is None
    assert mp.receipts(tmp_path) == [first]
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == original


def test_settled_fixture_never_reopens_just_because_budget_is_released(tmp_path):
    first = run(tmp_path, rows=modest_edge_slate())
    original = mp.rolling_receipt_path(tmp_path, first).read_bytes()
    lookup = lambda _: (0, 1)
    assert mp.performance([first], lookup)['losses'] == 1
    assert run(tmp_path, NOW + timedelta(minutes=1), modest_edge_slate(NOW + timedelta(minutes=1)), lookup=lookup) is None
    assert mp.receipts(tmp_path) == [first]
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == original


def test_signed_reuse_cannot_understate_historical_prior_stakes(tmp_path):
    first = run(tmp_path, rows=modest_edge_slate())
    first_blob = mp.rolling_receipt_path(tmp_path, first).read_bytes()
    second = run(tmp_path, NOW + timedelta(minutes=1), modest_edge_slate(NOW + timedelta(minutes=1)))
    for entry in second['fixture_concentration']['fixtures']:
        entry['prior_open_stake_micro_units'] -= 1
        entry['residual_budget_micro_units'] += 1
        entry['total_open_stake_micro_units'] -= 1
        entry['idle_budget_micro_units'] += 1
    second.pop('sha256')
    second['sha256'] = mp.digest(second)
    # Even an internally consistent, correctly hashed declaration must account
    # for the independent prior receipt, not just its own claimed residual.
    mp.validate_record(second, second['date'])
    mp.rolling_receipt_path(tmp_path, second).write_text(json.dumps(second))
    with pytest.raises(ValueError, match='complete prior stake evidence'):
        mp.receipts(tmp_path)
    assert mp.rolling_receipt_path(tmp_path, first).read_bytes() == first_blob
