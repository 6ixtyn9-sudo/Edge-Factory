"""Country-less league names must not acquire country identity from a global alias."""

import json

import pytest

from edgefactory import entities
from edgefactory.sources import theoddsapi
from scripts import build_entity_registry as builder


@pytest.mark.parametrize('raw,target', [
    ('Ligue 1', 'france ligue 1'),
    ('Primera Division', 'argentina primera division'),
    ('Primera División', 'argentina primera division'),
    ('Serie A', 'italy serie a'),
])
def test_stale_learned_alias_cannot_invent_country(monkeypatch, raw, target):
    monkeypatch.setattr(entities, 'load_overrides', dict)
    monkeypatch.setattr(entities, 'load_registry', lambda: {
        'alias_index': {'leagues': {raw: target, entities.norm_league(raw): target}},
    })
    assert entities.canonical_league(raw) == entities.canonical_league_key(raw)
    assert entities.canonical_league(raw) != target


@pytest.mark.parametrize('raw,qualified', [
    ('Ligue 1', 'France Ligue 1'), ('Ligue 1', 'Algeria Ligue 1'),
    ('Primera Division', 'Argentina Primera Division'),
    ('Primera División', 'Peru Primera División'),
])
def test_builder_never_merges_generic_domestic_label(raw, qualified):
    assert builder.is_generic_league_label(raw)
    assert not builder.safe_league_alias_merge(raw, qualified)
    assert not builder.safe_league_alias_merge(qualified, raw)


def test_builder_does_not_reimport_poisoned_aliases(tmp_path, monkeypatch):
    registry = tmp_path / 'entity_registry.json'
    registry.write_text(json.dumps({'leagues': {
        'france ligue 1': {'aliases': ['Ligue 1', 'France Ligue 1', 'Fr1']},
        'argentina primera division': {'aliases': ['Primera Division']},
    }}))
    monkeypatch.setattr(builder, 'ENTITY_REGISTRY_PATH', registry)
    teams, leagues = builder.DSU(), builder.DSU()
    builder.load_existing_registry_aliases(teams, leagues)
    assert leagues.find('ligue 1') != leagues.find('france ligue 1')
    assert leagues.find('primera division') != leagues.find('argentina primera division')
    assert leagues.find('fr1') == leagues.find('france ligue 1')


@pytest.mark.parametrize('label', ['Ligue 1', 'Ligue 2', 'Primera Division', 'Primera División', 'Serie A'])
def test_provider_catalogue_cannot_supply_a_missing_country(label):
    sports = [
        {'key': 'soccer_argentina_primera_division', 'title': 'Primera Division', 'active': True},
        {'key': 'soccer_france_ligue_one', 'title': 'Ligue 1', 'active': True},
        {'key': 'soccer_italy_serie_a', 'title': 'Serie A', 'active': True},
    ]
    assert theoddsapi.sport_key_for_league(label, sports) is None


def test_qualified_labels_and_explicit_codes_still_resolve():
    sports = [{'key': 'soccer_argentina_primera_division', 'title': 'Primera Division', 'active': True},
              {'key': 'soccer_france_ligue_one', 'title': 'Ligue 1', 'active': True}]
    assert theoddsapi.sport_key_for_league('Argentina,Primera División', sports) == sports[0]['key']
    assert theoddsapi.sport_key_for_league('France Ligue 1', sports) == sports[1]['key']
    assert theoddsapi.sport_key_for_league('Fr1', sports) == sports[1]['key']
    assert theoddsapi.sport_key_for_league('Algeria,Ligue 1', sports) is None
    assert theoddsapi.sport_key_for_league('Peru,Primera Division', sports) is None
