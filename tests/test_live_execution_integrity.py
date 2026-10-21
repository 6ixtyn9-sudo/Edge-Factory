"""Live admission, not a shadow gate: use existing source policy in both lanes."""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from scripts import auto_tickets as at
from enhancement_fixtures import with_evidence


def enhanced(**changes):
    return with_evidence(dict(
        date='2026-10-21', home='Alpha Town', away='Bravo Town',
        pick='home', bucket='SKIPPED_VETO', recommended_enhancement='home_under_15',
        enhancement_probability=.74, enhancement_price=1.43,
        enhancement_price_source='oddspapi', enhancement_price_book='Example Book',
        **changes))


def verdict(row, *, live=True):
    return at.enhancement_legs([row], execution_safe=live)[0]['verdict']


@pytest.mark.parametrize('price', [float('nan'), float('inf'), float('-inf'), 'nan', 'inf'])
def test_main_rejects_nonfinite_prices_before_pool_or_staking(price):
    row = dict(date='2026-10-21', market='1x2', pick='home', avg_p=70,
               odds=price, odds_source='oddspapi', bucket='CERTIFIED_CLEAN')
    assert at.playable_leg_rejection(row, execution_safe=True)[0] == 'invalid_odds'
    assert at.playable_legs([row], execution_safe=True) == []


@pytest.mark.parametrize('source, expected', [
    ('', 'price_source_unregistered'),
    ('not_a_registered_source', 'price_source_unregistered'),
    ('zulubet', 'price_source_not_execution_eligible'),
    ('sportytrader_odds', 'price_source_not_execution_eligible'),
])
def test_enhancement_live_guard_applies_existing_main_source_policy(source, expected):
    row = enhanced(); row['enhancement_price_source'] = source
    assert verdict(row) == expected
    assert at.enhancement_pool(at.enhancement_legs([row], execution_safe=True)) == []
    # Historical inspection is not silently re-written by the live correction.
    assert verdict(row, live=False) == 'fire'


@pytest.mark.parametrize('changes', [
    {'enhancement_priced': False},
    {'enhancement_price_rejection': 'no_matching_kickoff_and_capture_witness'},
])
def test_persisted_price_cannot_override_its_own_rejection(changes):
    row = enhanced(); row.update(changes)
    assert verdict(row) == 'price_evidence_rejected'


@pytest.mark.parametrize('book', [None, '', '   ', True])
def test_named_source_must_have_an_actual_bookmaker_identity(book):
    row = enhanced(); row['enhancement_price_book'] = book
    assert verdict(row) == 'price_bookmaker_missing'


def test_valid_leg_still_fires_no_pause_new_ev_or_goal_filter():
    row = enhanced()
    row.update(recommended_market='avoid_raw_1x2', draw_risk_flag='EXTREME',
               statistical_profile={'avg_goals': 3.5}, enhancement_edge_sample=-.5,
               odds_source='not_a_registered_source', price_push_eligible=False)
    assert verdict(row) == 'fire'  # enhancement has its OWN eligible price
    pool = at.enhancement_pool(at.enhancement_legs([row], execution_safe=True))
    assert len(pool) == 1 and pool[0]['odds'] == 1.43
    assert at.MIN_LEG_ODDS == 1.30


def test_shared_source_guard_respects_existing_runtime_policy(monkeypatch):
    row = enhanced(); row['enhancement_price_source'] = 'boggio'
    monkeypatch.setattr(at.psrc, 'average_price_donor_enabled', lambda: False)
    assert verdict(row) == 'price_source_not_execution_eligible'


def test_audit_only_scoutingstats_alias_stays_non_executable():
    row = enhanced(); row['enhancement_price_source'] = 'scoutingstats'
    assert at.psrc.spec('scoutingstats') is at.psrc.spec('scoutingstats_odds')
    assert verdict(row) == 'price_source_not_execution_eligible'


def test_actual_live_builder_enables_guard_before_selection(tmp_path, monkeypatch):
    from edgefactory import enh_registry, enh_team_floors
    row = enhanced(); row['enhancement_price_source'] = 'not_a_registered_source'
    (tmp_path / 'picks_today.json').write_text(json.dumps([row]))
    monkeypatch.setattr(at, 'LOCALDATA', tmp_path)
    monkeypatch.setattr(at, 'enhancement_board_enabled', lambda: True)
    monkeypatch.setattr(at, 'is_frozen', lambda *a: False)
    monkeypatch.setattr(at, '_frozen_text_on_disk', lambda *a: False)
    monkeypatch.setattr(enh_registry, 'derive_floors_for_day', lambda *a: {})
    monkeypatch.setattr(enh_team_floors, 'team_under_floors', lambda *a: {})
    original = at.enhancement_legs
    class GuardReached(Exception):
        pass
    def verify(*args, **kwargs):
        assert kwargs.get('execution_safe') is True
        assert original(*args, **kwargs)[0]['verdict'] == 'price_source_unregistered'
        raise GuardReached
    monkeypatch.setattr(at, 'enhancement_legs', verify)
    args = SimpleNamespace(date='2026-10-21', force=False)
    with pytest.raises(GuardReached):
        at.cmd_enhancement(args, {'open_slips': [], 'history': [], 'bank': 100})
    assert sorted(p.name for p in tmp_path.iterdir()) == ['picks_today.json']


def test_real_enhancement_source_alias_is_same_spec_not_new_independence():
    psrc = at.psrc
    assert psrc.known('oddspapi') and psrc.resolvable('oddspapi')
    assert psrc.spec('oddspapi') is psrc.spec('oddspapi_odds')
    assert psrc.spec('oddspapi').family == 'oddspapi_bookmaker'
    assert psrc.price_donor_names().count('oddspapi_odds') == 1
