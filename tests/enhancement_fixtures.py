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
