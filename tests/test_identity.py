"""Shared identity fold: properties, goldens, and no-merge invariants."""

import sys
from pathlib import Path

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
        == "enterprise national league south"
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
    # Existing explicit aliases keep working on their own key shapes.
    assert key("Thunder SC") == "dandenong"
    assert key("Dila") == "dilagori"
    # and clean keys are stable/unified across accent & case variants.
    assert key("Dandenong Thunder") == key("Thunder SC")
