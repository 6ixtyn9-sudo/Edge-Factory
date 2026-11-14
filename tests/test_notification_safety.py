import pytest
from edgefactory.notifier import (bet_alert_eligible, chunk_telegram_shadow,
    telegram_text_units, format_telegram_official, format_whatsapp_summary)


@pytest.mark.parametrize('receipt', [
    {'price_push_eligible': False},
    {'price_evidence': 'SOURCE_FALLBACK'},
    {'price_evidence': 'SCOUTINGSTATS_SOLE'},
    {'price_evidence': 'SUSPECT_ALIAS_FUZZY'},
    {'price_evidence': 'UNMATCHED'},
    {'price_quarantine_reason': 'alias_fuzzy'},
])
def test_explicit_refusals_survive_rendering(receipt):
    row = dict(match='Blocked vs Opponent', bucket='CERTIFIED_CLEAN', **receipt)
    assert not bet_alert_eligible(row)
    assert row['match'] not in format_telegram_official('2026-10-10', [row])
    assert row['match'] not in format_whatsapp_summary('2026-10-10', [row])


def test_large_shadow_all_cards_retained_with_research_context():
    rows = [dict(match=f'Unique {i:03d} 🏆 vs Opponent', bucket='SKIPPED_VETO',
                 avg_p=60, pick='home', odds=1.5) for i in range(200)]
    chunks = chunk_telegram_shadow('2026-10-10', rows)
    assert len(chunks) > 1
    for chunk in chunks:
        assert telegram_text_units(chunk) <= 3800
        assert 'NOT pushed as bets' in chunk
        assert 'SKIPPED_VETO' in chunk
    for row in rows:
        assert '\n'.join(chunks).count(row['match']) == 1


def test_oversized_single_card_no_silent_truncation():
    name = '🏆' * 5000
    chunks = chunk_telegram_shadow('2026-10-10', [dict(
        match=name, bucket='SKIPPED_VETO', avg_p=60, pick='home')])
    assert all(telegram_text_units(c) <= 3800 for c in chunks)
    assert sum(c.count('🏆') for c in chunks) == 5000
