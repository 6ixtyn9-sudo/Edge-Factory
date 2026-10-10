import pytest
from edgefactory.context_rules import holds, parse_predicate


def test_vocabulary_is_explicit_and_missing_fails_closed():
    assert parse_predicate('h2h_dominance>=3') == ('h2h_dominance', '>=', 3.0)
    with pytest.raises(ValueError):
        parse_predicate('arbitrary>=1')
    row = {'identity_verified': True, 'captured_at': '2026-10-10T10:00:00+00:00', 'form_gap': 4}
    kickoff = '2026-10-10T12:00:00+00:00'
    assert holds('form_gap>=3', row, kickoff=kickoff)
    assert not holds('rest_days<=2', row, kickoff=kickoff)
    assert not holds('form_gap>=3', {**row, 'captured_at': kickoff}, kickoff=kickoff)
    assert not holds('form_gap>=3', {**row, 'identity_verified': False}, kickoff=kickoff)
