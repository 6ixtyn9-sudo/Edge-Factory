"""Short provider league codes must resolve to the sport keys that exist.

`sport_key_for_league` rejects any label shorter than 4 characters after
`_league_code` unless it appears in `SHORT_LEAGUE_KEYS` (stage 1). The archives
are full of 2-3 character provider codes -- `EPL`, `L1`, `Nl1`, `Us1` -- none
of which were listed, so each resolved to None and every fixture in them was
reported `league not covered` even though the provider sells the competition.

Measured over the 30 committed attempt ledgers: 111 of 657 unpriced
shortlisted fixtures (17%) sat in competitions whose sport key was already in
`localdata/theoddsapi_sports.json`.

The safety property that matters more than the recovery: a code must resolve
to the RIGHT competition and the RIGHT TIER, or to None. None is always
preferred over a wrong-competition key (2026-08-06 incident).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.sources.theoddsapi import (  # noqa: E402
    SHORT_LEAGUE_KEYS,
    _league_code,
    sport_key_for_league,
)

SPORTS_PATH = ROOT / "localdata" / "theoddsapi_sports.json"


def _sports():
    raw = json.loads(SPORTS_PATH.read_text())
    if isinstance(raw, list):
        return raw
    return raw.get("sports", raw.get("data", []))


SPORTS = _sports()
CATALOGUE = {s.get("key") for s in SPORTS}


# --------------------------------------------------------------------------
# the recovery
# --------------------------------------------------------------------------

RECOVERED = {
    "EPL": "soccer_epl",
    "L1": "soccer_england_league1",
    "L2": "soccer_england_league2",
    "Sc1": "soccer_spl",
    "De1": "soccer_germany_bundesliga",
    "De2": "soccer_germany_bundesliga2",
    "De3": "soccer_germany_liga3",
    "It1": "soccer_italy_serie_a",
    "It2": "soccer_italy_serie_b",
    "Es1": "soccer_spain_la_liga",
    "Es2": "soccer_spain_segunda_division",
    "Fr1": "soccer_france_ligue_one",
    "Fr2": "soccer_france_ligue_two",
    "Nl1": "soccer_netherlands_eredivisie",
    "Pt1": "soccer_portugal_primeira_liga",
    "Be1": "soccer_belgium_first_div",
    "At1": "soccer_austria_bundesliga",
    "Ch1": "soccer_switzerland_superleague",
    "Pl1": "soccer_poland_ekstraklasa",
    "No1": "soccer_norway_eliteserien",
    "Se1": "soccer_sweden_allsvenskan",
    "Dk1": "soccer_denmark_superliga",
    "Tr1": "soccer_turkey_super_league",
    "Gr1": "soccer_greece_super_league",
    "Ru1": "soccer_russia_premier_league",
    "Us1": "soccer_usa_mls",
    "Mx1": "soccer_mexico_ligamx",
    "Br1": "soccer_brazil_campeonato",
    "Br2": "soccer_brazil_serie_b",
    "Ar1": "soccer_argentina_primera_division",
    "Cl1": "soccer_chile_campeonato",
    "Jp1": "soccer_japan_j_league",
    "Kr1": "soccer_korea_kleague1",
    "Cn1": "soccer_china_superleague",
    "Sa1": "soccer_saudi_arabia_pro_league",
    "Au1": "soccer_australia_aleague",
}


@pytest.mark.parametrize("label,expected", sorted(RECOVERED.items()))
def test_short_code_resolves_to_its_catalogue_key(label, expected):
    assert sport_key_for_league(label, SPORTS) == expected


def test_epl_resolves():
    """The headline regression: the largest league in the world, present in
    the catalogue, previously resolved to None."""
    assert sport_key_for_league("EPL", SPORTS) == "soccer_epl"


def test_case_insensitive():
    for variant in ("epl", "EPL", "Epl"):
        assert sport_key_for_league(variant, SPORTS) == "soccer_epl"


# --------------------------------------------------------------------------
# the safety properties
# --------------------------------------------------------------------------

def test_every_mapped_key_exists_in_the_catalogue():
    """A code may never point at a key the provider does not list."""
    for code, keys in SHORT_LEAGUE_KEYS.items():
        assert any(k in CATALOGUE for k in keys), (
            f"{code} -> {keys}: none present in theoddsapi_sports.json")


def test_tiers_never_collapse():
    """Digits carry the tier. A second tier must never inherit its top tier."""
    pairs = [
        ("De1", "De2"), ("De2", "De3"), ("It1", "It2"),
        ("Es1", "Es2"), ("Fr1", "Fr2"), ("Br1", "Br2"),
        ("L1", "L2"), ("Se1", "Se2"),
    ]
    for top, lower in pairs:
        a = sport_key_for_league(top, SPORTS)
        b = sport_key_for_league(lower, SPORTS)
        assert a is not None and b is not None, f"{top}/{lower} unresolved"
        assert a != b, f"{top} and {lower} collapsed onto {a}"


def test_ambiguous_efl_stays_unmapped():
    """`EFL` could be the Championship or the EFL Cup. None is preferred over
    a coin flip."""
    assert "efl" not in SHORT_LEAGUE_KEYS


def test_uncovered_competitions_still_return_none():
    """The 2026-10-06 slate. These are genuinely absent from the catalogue and
    must NOT acquire a key -- that would fabricate wrong-competition prices."""
    for label in (
        "International,Friendlies", "World Friendlies",
        "International,Africa Cup Of Nations Qualification Grp. B",
        "World CONCACAF Nations League", "England,National League",
        "Norway,1. Division", "Bg1", "Ng1", "De4", "Se4", "Cz4", "Wl1",
    ):
        assert sport_key_for_league(label, SPORTS) is None, (
            f"{label} must stay uncovered")


def test_unknown_short_code_is_none_not_a_guess():
    for label in ("Zz9", "Qq1", "Xy2"):
        assert sport_key_for_league(label, SPORTS) is None


def test_key_absent_from_a_live_catalogue_is_not_returned():
    """`_first_listed` verifies against the live sports list: when the
    provider stops listing a competition, the code must stop resolving.

    (With an EMPTY list the documented contract is different -- the chain
    head is trusted, because an empty list means 'no cache to verify
    against', not 'the provider sells nothing'. That contract predates this
    change and is asserted separately below.)
    """
    catalogue_without_epl = [s for s in SPORTS if s.get("key") != "soccer_epl"]
    assert catalogue_without_epl, "fixture precondition"
    assert sport_key_for_league("EPL", catalogue_without_epl) is None
    # unaffected neighbours still resolve
    assert sport_key_for_league("It1", catalogue_without_epl) == "soccer_italy_serie_a"


def test_empty_catalogue_trusts_the_chain_head_as_documented():
    """Pre-existing contract in `_first_listed`, pinned so this change is not
    later blamed for it."""
    assert sport_key_for_league("EPL", []) == "soccer_epl"
    assert sport_key_for_league("UCL", []) == "soccer_uefa_champs_league"


def test_codes_are_normalised_and_digit_preserving():
    assert _league_code("Nl1") == "nl1"
    assert _league_code("EPL") == "epl"
    assert all(c == c.lower() for c in SHORT_LEAGUE_KEYS)
