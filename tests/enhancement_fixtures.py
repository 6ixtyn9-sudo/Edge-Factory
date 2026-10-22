"""Explicit synthetic cohort provenance for isolated enhancement unit tests.

No production data/registry is patched; callers supply their own realized rate.
Integration tests must exercise real contract recreation instead of this helper.
"""
from unittest.mock import patch

IDENTITY = 'pfc_' + 'a' * 24
DAY = '2026-10-14'


def contract_pick(row):
    return dict(row, contract_schema='post_forebet_v1', contract_id=IDENTITY,
                date=row.get('date', DAY))


def with_evidence(row):
    row = contract_pick(row)
    rate = row['enhancement_probability']
    note = dict(market=row['recommended_enhancement'], engine='hybrid_cohort',
                cohort_rate=rate, cohort_n=200, cohort_contract_id=IDENTITY,
                cohort_as_of_exclusive=row['date'])
    return dict(row, event_notes=[note], enhancement_cohort_rate=rate,
                enhancement_cohort_n=200, enhancement_cohort_contract_id=IDENTITY,
                enhancement_cohort_as_of_exclusive=row['date'])


def compute_with_fixture_cohort(pt, con, row, prices):
    """Attach synthetic contract provenance to an already-stubbed cohort only."""
    row = contract_pick(row)
    original = pt.fetch_match_cohort
    def fetch(*args, **kwargs):
        result = original(*args, **kwargs)
        if result is None:
            return None
        return dict(result, contract_id=IDENTITY, as_of_exclusive=row['date'])
    with patch.object(pt, 'fetch_match_cohort', fetch):
        return pt.compute_dynamic_enhancement(con, row, prices)


def seed_price_records(root, rows):
    """Explicit synthetic all-win prior cells for lifecycle/quote-binding tests.

    Uses the real admission resolver, not a promotion mock. Production coverage
    must never be inferred from this deliberately favourable unit-test sample.
    """
    import json
    from datetime import datetime, timedelta
    from edgefactory.enh_registry import enhancement_price_context, registry_path
    path = registry_path(root)
    payload = json.loads(path.read_text()) if path.exists() else {'markets': {}}
    for row in rows:
        context = enhancement_price_context(row)
        if context is None:
            continue
        old_day = (datetime.fromisoformat(row['date']) - timedelta(days=2)).date().isoformat()
        old = dict(context, captured_at=f'{old_day}T04:00:00+00:00',
                   decision_at=f'{old_day}T05:00:00+00:00', kickoff=f'{old_day}T16:00:00+00:00')
        entry = payload['markets'].setdefault(row['recommended_enhancement'] + '@v1', {'records': []})
        # Repeated fixture/price cells need only one synthetic historical sample.
        if any(r.get('price_context') == old for r in entry['records']):
            continue
        entry['records'].extend(dict(date=old_day, home=f'Synthetic {i}', away='Prior Away',
            match=f'Synthetic {i} vs Prior Away', hit=True, price=context['price'], source=context['source'],
            price_context=old, recorded_at=f'{old_day}T20:00:00+00:00') for i in range(30))
        entry['n'] = len(entry['records'])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))
