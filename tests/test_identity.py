"""Shared identity fold: properties, goldens, and no-merge invariants."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for extra in ("src", "scripts"):
    if str(ROOT / extra) not in sys.path:
        sys.path.insert(0, str(ROOT / extra))

from edgefactory.identity import (
    LEAGUE_ALIASES,
    canonical_league_key,
    fold_identity_words,
    fold_league_identity,
    team_identity_words,
)


def test_ampersand_and_and_spelling_fold_equal():
    # The 2026-09-22 Dagenham incident pair.
    assert (
        team_identity_words("Dagenham & Redbridge")
        == team_identity_words("Dagenham and Redbridge")
        == "dagenham redbridge"
    )


def test_fold_is_deterministic_and_idempotent():
    samples = [
        "East Kilbride vs Kelty Hearts",
        "1. FC Heidenheim",
        "FK Radnički Niš",
        "Strømsgodset IF",
        "A & B & C",
        "!!!",
        "",
    ]
    for s in samples:
        once = fold_identity_words(s)
        assert fold_identity_words(once) == once
        assert fold_identity_words(s) == fold_identity_words(s)


def test_different_teams_do_not_collapse():
    # Real, distinctive pairs from recent fixtures; the fold must keep
    # every pair's two keys apart (no-merge landmine guard).
    pairs = [
        ("Dagenham & Redbridge", "Waltham Abbey"),
        ("East Kilbride", "Kelty Hearts"),
        ("Alloa Athletic", "Montrose"),
        ("Seniors FC", "Senior FC"),
        ("Landscapes FC", "Landscape FC"),
        ("FC Andean Rovers", "Andean Rovers"),
        ("Hamilton Academical", "Hamilton Academical U21"),
        ("Ajax", "Ajax U21"),
        ("Nordsjælland", "FC Nordsjælland U19"),
    ]
    for a, b in pairs:
        ka, kb = team_identity_words(a), team_identity_words(b)
        assert ka != kb, (a, b, ka)


def test_accent_safe_for_team_key_input():
    assert team_identity_words("Nõmme Kalju") == "nomme kalju"
    assert team_identity_words("FC Nordsjælland") == "fc nordsjaelland"


def test_word_level_and_only():
    # "and" inside a longer word must survive.
    assert team_identity_words("Sunderland") == "sunderland"


def test_league_fold_keeps_tokens():
    assert fold_league_identity("England,Fa Cup") == "england fa cup"
    assert fold_league_identity("FA") == "fa"


def test_league_alias_pairs_resolve_to_registry_keys():
    assert canonical_league_key("England,Fa Cup") == "fa"
    assert canonical_league_key("FA") == "fa"
    assert (
        canonical_league_key("England,National League South")
        == "nls"
    )
    # Unaliased leagues pass through folded, untouched.
    assert canonical_league_key("Scotland,Championship") == "scotland championship"


def test_alias_keys_are_all_folded_and_idempotent():
    for key, target in LEAGUE_ALIASES.items():
        assert fold_league_identity(key) == key
        assert canonical_league_key(target) == target


def test_alias_targets_exist_in_purity_registry_league_keyspace():
    """Tripwire (red-team follow-up): alias targets are registry pool keys.
    If a future registry rebuild renames a sponsored competition (e.g. the
    "enterprise national league south" sponsor changes), this test fails
    loudly instead of silently re-orphaning the alias."""
    import json

    reg_path = ROOT / "localdata" / "purity_registry.json"
    if not reg_path.exists():
        return  # fresh clones have no registry state; nothing to guard
    reg = json.loads(reg_path.read_text())
    keyspace = {
        k.split("|")[1]
        for k in (reg.get("contexts", {}) or {}).get("league", {})
        if "|" in k
    }
    if not keyspace:
        return
    for target in LEAGUE_ALIASES.values():
        assert target in keyspace, f"alias target {target!r} missing from registry"


def _pt_source_team_key():
    if "picks_today" not in sys.modules:
        import picks_today  # noqa: F401
    return sys.modules["picks_today"].source_team_key


def test_source_team_key_merges_incident_spellings():
    key = _pt_source_team_key()
    a = key("Dagenham & Redbridge")
    b = key("Dagenham and Redbridge")
    assert a == b, (a, b)


def test_source_team_key_alias_map_intact():
    key = _pt_source_team_key()
    # Legacy alias pairs still unify (raw-name space, key-derived).
    assert key("Thunder SC") == key("Dandenong Thunder")
    assert key("Dila") == key("Dila Gori")
    assert key("Neftchi") == key("Neftchi Fergana")
    assert key("Hobart Zebras") == key("Clarence Zebras")
    # Accent/case/punctuation variants unify.
    assert key("FC Zürich") == key("Zurich")
    assert key("Málaga CF") == key("Malaga")


def test_source_team_key_same_club_pairs_from_redteam():
    # Same-club pairs audited in the 2026-09-22 red-team pass.
    for a, b in (
        ("Borussia M'gladbach", "Borussia Mönchengladbach"),
        ("Rodina Moscow", "Rodina Moskva"),
        ("Grasshopper-Club", "Grasshoppers"),
        ("Ferencvaros", "Ferencvarosi TC"),
        ("Ludogorets", "Ludogorets Razgrad"),
        ("Bayern Munich", "FC Bayern München"),
        ("Sandnes ULF", "Sandnes Ulf"),
        ("Stromsgodset", "Stromsgodset IF"),
        ("Lillestrom", "Lillestrom SK"),
    ):
        assert _pt_source_team_key()(a) == _pt_source_team_key()(b), (a, b)


def test_pinnapi_probe_2026_10_10_run4_aliases_and_negative_control():
    # Both sides and senior/reserve league were printed for each fixture.
    key = _pt_source_team_key()
    pairs = (
        ("Tottenham", "Tottenham Hotspur"),
        ("Rizespor", "Caykur Rizespor"),
        ("SC Paderborn 07", "Paderborn"),
        ("VfB Stuttgart", "Stuttgart"),
        ("Leeds", "Leeds United"),
        ("1899 Hoffenheim", "Hoffenheim"),
        ("Scunthorpe", "Scunthorpe United"),
        ("Zhetysu", "Zhetysu Taldykorgan"),
        ("Kortrijk", "KV Kortrijk"),
        ("Red Bull Salzburg", "Salzburg"),
        ("Al-Tadhamon", "Al Tadamon"),
        ("Al-Qadsia", "Qadsia SC"),
        ("York", "York City"),
        ("Northampton", "Northampton Town"),
        ("Club Brugge KV", "Club Brugge"),
        ("Vilzing", "DJK Vilzing"),
        ("FC Porto B", "Porto II"),
        ("Dunajska Streda", "DAC 1904"),
    )
    for a, b in pairs:
        assert key(a) == key(b), (a, b)
    assert key("Kristianstad FC") != key("Kristiansund")
    assert key("FC Porto B") != key("FC Porto")
    assert key("Club Brugge KV U23") != key("Club Brugge KV")


def test_source_team_key_disambiguates_squads():
    key = _pt_source_team_key()
    distinct_pairs = [
        ("Real Madrid", "Atletico Madrid"),
        ("Arsenal", "Arsenal W"),
        ("FC Porto", "FC Porto B"),
        ("Juventus", "Juventus W"),
        ("Gornik Zabrze", "Gornik Zabrze II"),
        ("Rigas FS", "Rigas FS II"),
        ("America W", "Club America"),
        ("Freiburg", "SC Freiburg II"),
        ("Manchester City", "Manchester United"),
        ("Lokomotiv Moscow", "Lokomotiv Sofia"),
        ("Slavia Praha", "Slavia Praha B"),
    ]
    for a, b in distinct_pairs:
        assert key(a) != key(b), (a, b, key(a))
    # and every key carries more information than the legacy width-9 —
    # a 24-char ceiling means near-identical prefixes no longer collapse.
    assert key("Los Angeles FC") != key("Los Angeles Galaxy")


# --- curated league table (Config/entity_overrides.json -> leagues) --------
#
# Coverage is derived from the curated table, so a newly curated competition
# is covered by construction rather than needing a test of its own. Added with
# the 2026-10-07 declarations of "Japan Emperor Cup" and "Algeria: Ligue 1",
# the two the run reported as UNKNOWN league verdicts.


def _curated_league_pairs():
    leagues = json.loads(
        (ROOT / "Config" / "entity_overrides.json").read_text())["leagues"]
    return sorted((raw, str(canon)) for raw, canon in leagues.items() if raw != canon)


@pytest.mark.parametrize("raw,canonical", _curated_league_pairs())
def test_curated_league_entry_resolves_to_its_declared_canonical(raw, canonical):
    from edgefactory.entities import canonical_league

    assert canonical_league(raw) == canonical_league(canonical)


def test_curated_cup_canonical_stays_distinct_from_its_league():
    """A cup is not its league: the Japan cup must never key as ``jp1``.

    The curated table is the only thing standing between "the two Japanese
    competitions we know by name" and a future edit that folds the cup onto
    the J1 League key, which would hand the cup that league's purity pool.
    """
    from edgefactory.entities import canonical_league

    assert canonical_league("Japan Emperor Cup") == "japan emperor cup"
    assert canonical_league("Japan Emperor Cup") != canonical_league("Japan J1 League")


@pytest.mark.parametrize("label", [
    "England,National League South", "Enterprise National League South",
    "NLs", "NlS", "nls",
])
def test_national_league_south_uses_existing_registry_code(label):
    from edgefactory.entities import canonical_league

    assert canonical_league_key(label) == canonical_league(label) == "nls"


@pytest.mark.parametrize("kind", ["override", "learned"])
def test_stale_sponsor_alias_outputs_cannot_orphan_registry_contexts(monkeypatch, kind):
    from edgefactory import entities

    label = "provider south label"
    target = "Enterprise National League South"
    monkeypatch.setattr(entities, "load_overrides", lambda: {
        "leagues": {label: target} if kind == "override" else {}})
    monkeypatch.setattr(entities, "load_registry", lambda: {
        "alias_index": {"leagues": {label: target} if kind == "learned" else {}}})
    assert entities.canonical_league(label) == "nls"
    assert entities.canonical_league(target) == "nls"


@pytest.mark.parametrize("other", [
    "England,National League North", "NLn", "England,National League",
    "England,National League South Women", "England,National League South U21",
    "England,National League South Playoff",
])
def test_south_alias_does_not_merge_other_competitions(other):
    from edgefactory.entities import canonical_league

    assert canonical_league_key(other) != "nls"
    assert canonical_league(other) != "nls"


@pytest.mark.parametrize("label", [
    "England,National League South", "Enterprise National League South", "NLs",
])
def test_assay_and_exact_contract_lookup_share_south_key_and_preserve_veto(label):
    import duckdb
    from scripts import assay_purity, picks_today
    from edgefactory.entities import classify_competition

    rule = "test_exact_south_contract"
    with duckdb.connect() as con:
        con.create_function("classify_competition", classify_competition)
        con.execute("""
            CREATE TABLE south_assay AS
            SELECT ? AS league, 'home' AS pick, 'away' AS outcome,
                   2.0 AS pick_odds, DATE '2026-10-19' AS date,
                   'Home Team' AS home, 'Away Team' AS away
            FROM range(40)
        """, [label])
        contexts = assay_purity.assay_edge(con, dict(
            rule=rule, view="south_assay", market="1x2", sport="soccer",
            contract_schema="post_forebet_v1"), window_days=36500)
    league = contexts[0]
    key = f"soccer|nls|1x2|{rule}|home"
    assert league[key]["n"] == 40
    assert league[key]["roi"] == -1.0
    assert league[key]["verdict"] == "VETO"
    purity = {"contract_contexts": {rule: dict(zip(
        ("league", "team", "odds_band", "competition_type", "niche"), contexts))}}
    pick = dict(league=label, market="1x2", rule=rule, pick="home",
                contract_schema="post_forebet_v1", home="Home Team", away="Away Team")
    for spelling in ("NLs", "England,National League South", "Enterprise National League South"):
        ctx = picks_today.lookup_context(purity, {**pick, "league": spelling})
        assert ctx["league_key"] == "nls"
        assert ctx["league"] == "VETO"
    for other in ("NLn", "England,National League North", "Unknown Competition"):
        ctx = picks_today.lookup_context(purity, {**pick, "league": other})
        assert ctx["league"] == "UNKNOWN"  # no cross-league/fuzzy evidence borrowing


@pytest.mark.parametrize("target", ["Custom & League", "Åland / Cup", "!!!",
                                    "National League South Playoff"])
@pytest.mark.parametrize("kind", ["override", "learned"])
def test_alias_output_fix_preserves_unrelated_persisted_league_keys(monkeypatch, target, kind):
    from edgefactory import entities
    from edgefactory.util import norm_league

    label = "provider other label"
    monkeypatch.setattr(entities, "load_overrides", lambda: {
        "leagues": {label: target} if kind == "override" else {}})
    monkeypatch.setattr(entities, "load_registry", lambda: {
        "alias_index": {"leagues": {label: target} if kind == "learned" else {}}})
    assert entities.canonical_league(label) == norm_league(target)
