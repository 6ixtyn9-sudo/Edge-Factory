"""The voter-row seam's abbreviation fold and the bare-spelling joins (A-2/A-3).

Context: the 2026-10-12 adjudication of the round-5 coverage report. The seam
(``identity.source_team_key``) is the key the form/H2H features read, and it
was splitting one club's record across spellings the feeds emit for the same
club ("Scunthorpe Utd" vs "Scunthorpe"; "Newcastle Utd" vs the archive's
"Newcastle"). The fix is two-layer by design:

* a deterministic one-token fold (``utd`` -> ``united``) in
  ``team_identity_words`` - a fold, not fuzz: the same word abbreviated;
* per-spelling pairs with printed evidence, in the seam table and in
  ``Config/entity_overrides.json``.

The corpus-scale tests read the committed monthly archives' name columns when
they are present and skip otherwise; the property they assert is the one the
adjudication asked for: **no two distinct clubs collapse into one seam key.**

Evidence and the full per-pair measurement:
``handoff/round5_form_h2h_2026-10-12/a_identity_checks.txt``.
"""
from __future__ import annotations

import csv
import glob
import gzip
from collections import defaultdict
from pathlib import Path

import pytest

from edgefactory import identity as ident
from edgefactory.util import canonical_team_key

ROOT = Path(__file__).resolve().parents[1]
RESULTS_GLOB = "betexplorer_results_2026-*.csv.gz"


# -- the fold ---------------------------------------------------------------

def test_utd_is_a_word_level_fold_to_united():
    assert ident.team_identity_words("Scunthorpe Utd") == \
        ident.team_identity_words("Scunthorpe United")
    assert ident.team_identity_words("Newcastle Utd U21") == "newcastle united u21"
    # a token that merely contains the letters is untouched
    assert ident.team_identity_words("Utdalen") == "utdalen"


def test_the_fold_joins_the_abbreviated_spelling_of_one_club():
    for abbr, full in (("Scunthorpe Utd", "Scunthorpe United"),
                       ("Man Utd", "Manchester United"),
                       ("Dundee Utd", "Dundee United"),
                       ("Maidstone Utd", "Maidstone United"),
                       ("Flint Town Utd", "Flint Town United")):
        assert ident.source_team_key(abbr) == ident.source_team_key(full), (abbr, full)


def test_the_fold_never_joins_two_different_clubs():
    for a, b in (("Manchester City", "Manchester Utd"),
                 ("Manchester City", "Manchester United"),
                 ("Newcastle Utd", "Newcastle Town"),
                 ("Newcastle United", "Newcastle Jets"),
                 ("Dundee Utd", "Dundee"),
                 ("Sheffield Utd", "Sheffield"),
                 ("Newcastle Utd W", "Newcastle Utd")):
        assert ident.source_team_key(a) != ident.source_team_key(b), (a, b)


# -- the bare-spelling joins, and the refusals ------------------------------

def test_bare_spellings_join_the_club_they_abbreviate():
    for bare, full in (("Newcastle", "Newcastle United"),
                       ("Charlton", "Charlton Athletic"),
                       ("Mallorca", "Real Mallorca"),
                       ("Betis", "Real Betis"),
                       ("Basel", "FC Basel 1893"),
                       ("Kidderminster", "Kidderminster Harriers"),
                       ("Kidderminster Ha", "Kidderminster Harriers"),
                       ("Zeljeznicar", "Zeljeznicar Sarajevo"),
                       ("Omonia Nicosia F", "Omonia Nicosia"),
                       ("Corvinul Hunedoa", "Corvinul Hunedoara"),
                       ("Aris Thessalonik", "Aris Thessalonikis"),
                       ("Flint Town", "Flint Town Utd"),
                       ("Accrington", "Accrington Stanley")):
        assert ident.source_team_key(bare) == ident.source_team_key(full), (bare, full)


def test_a_reserve_or_youth_side_never_joins_its_senior_club():
    """A-3: mark, never merge. The fold must not become a squad-marker fold."""
    for reserve, senior in (("Ludogorets III", "Ludogorets Razgrad"),
                            ("Ludogorets II", "Ludogorets Razgrad"),
                            ("Kongsvinger 2", "Kongsvinger"),
                            ("Kongsvinger II", "Kongsvinger"),
                            ("Betis B", "Real Betis"),
                            ("Betis W", "Real Betis"),
                            ("Basel II", "FC Basel 1893"),
                            ("Mallorca B", "Real Mallorca"),
                            ("Charlton U21", "Charlton Athletic"),
                            ("Charlton W", "Charlton Athletic"),
                            ("Botafogo U20", "Botafogo"),
                            ("Newcastle U23s", "Newcastle United"),
                            ("Newcastle Utd W", "Newcastle United")):
        assert ident.source_team_key(reserve) != ident.source_team_key(senior), (reserve, senior)


def test_a_different_club_with_a_shared_word_is_never_joined():
    for a, b in (("Newcastle Town", "Newcastle United"),
                 ("Newcastle Jets", "Newcastle United"),
                 ("Ferroviario", "Ferroviária SP"),          # Brazil: two different clubs
                 ("San Marino Calcio", "San Marino"),
                 ("Universitario de Vinto", "Universitatea Cluj"),
                 ("Universitatea Craiova", "Universitatea Cluj"),
                 ("Liverpool M.", "Liverpool"),
                 ("CSKA 1948 Sofia", "CSKA Sofia"),
                 ("Real Betis", "Betis B")):
        assert ident.source_team_key(a) != ident.source_team_key(b), (a, b)


def test_the_al_ittihad_pair_is_refused():
    """A-2: the 75 'Al Ittihad' rows span three countries' leagues.

    Saudi (27), Egyptian (22), plus cup and friendly rows and the Libyan
    'Al-Ittihad'. A bare alias would attach another club's history to our
    features, so the pair is deliberately NOT in the curated tables.
    """
    pairs = ident.TEAM_KEY_RAW_ALIASES + ident._curated_override_pairs()
    names = {tuple(sorted(pair)) for pair in pairs}
    assert ("Al-Ittihad Alexandria", "Al Ittihad") not in names
    assert ("Al-Ittihad Alexandria", "Al-Ittihad") not in names


def test_the_alias_map_is_a_fixed_point_and_acyclic():
    """A pair's target can itself be an alias in the curated file, so the map
    is resolved to a fixed point (measured 2026-10-12: only the one pair added
    that day moves; every other key is unchanged by the resolution)."""
    steps = ident._ALIAS_STEPS
    assert steps, "the alias map must not be empty"
    for key in steps:
        assert ident.TEAM_KEY_ALIASES.get(key, key) == ident._alias_fixed_point(key)
        # walking the raw steps must terminate (no cycle)
        seen, walk, hops = {key}, key, 0
        while walk in steps and steps[walk] != walk:  # a self-loop is a no-op entry
            walk = steps[walk]
            hops += 1
            assert walk not in seen, f"alias cycle at {walk!r}"
            seen.add(walk)
            assert hops < len(steps) + 1


def test_the_fold_does_not_move_the_operational_entity_key():
    """The purity/entity key layer keeps the historical spelling (byte-for-byte).

    ``canonical_team`` keys are persisted: the committed
    ``localdata/purity_registry.json`` carries keys such as
    ``soccer|afctelfordutd|*|1x2|home`` built before the fold existed. If the
    fold reached that layer, every stored verdict for a club spelled
    '... Utd' would be orphaned, which is a money-path change.
    """
    from edgefactory.entities import canonical_team

    for name, expected in (("AFC Telford Utd", "afctelfordutd"),
                           ("Boston Utd", "bostonutd"),
                           ("Dundee Utd", "dundeeutd"),
                           ("Nomme Utd", "nommeutd"),
                           ("Cambridge Utd", "cambridgeutd")):
        assert canonical_team(name) == expected, name
    # the rule is the historical one, i.e. the fold does not reach the layer
    from edgefactory.util import norm_entity_team

    for name in ("AFC Telford Utd", "Boston Utd", "Dundee Utd", "Nomme Utd"):
        historical = norm_entity_team(
            " ".join(w for w in ident.fold_identity_words(name).split() if w != "and"))
        assert canonical_team(name) == historical, name
    # the seam is where the fold lives, and there it does join them
    assert ident.source_team_key("Dundee Utd") == ident.source_team_key("Dundee United")
    assert canonical_team("Dundee") != canonical_team("Dundee Utd")


def test_the_ledger_key_layer_is_untouched_by_these_joins():
    """The operational ledger key is a different function (util), and the
    joins above are key-neutral there: it already truncated these spellings
    onto one stem. Pinned so a future change cannot move prices silently."""
    assert canonical_team_key("Newcastle") == canonical_team_key("Newcastle Utd")
    assert canonical_team_key("Mallorca") == canonical_team_key("Real Mallorca")
    assert canonical_team_key("Charlton") == canonical_team_key("Charlton Athletic")


# -- the corpus property ----------------------------------------------------

def _corpus_names() -> set[str]:
    names: set[str] = set()
    for path in sorted(glob.glob(str(ROOT / "localdata" / RESULTS_GLOB))):
        with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                for key in ("home", "away"):
                    name = (row.get(key) or "").strip()
                    if name:
                        names.add(name)
    settled = ROOT / "localdata" / "settled_results.json"
    if settled.exists():
        import json

        for row in (json.loads(settled.read_text()).get("rows") or []):
            for key in ("home", "away"):
                name = str(row.get(key) or "").strip()
                if name:
                    names.add(name)
    return names


def _key_with_folds(folds: dict[str, str]):
    """The seam key as it would be built with ``folds`` as the token table."""
    saved = ident.TEAM_TOKEN_FOLDS
    try:
        ident.TEAM_TOKEN_FOLDS = folds
        aliases = {}
        for alias, canonical in ident.TEAM_KEY_RAW_ALIASES + ident._curated_override_pairs():
            a, c = ident.source_team_key_base(alias), ident.source_team_key_base(canonical)
            if a and c:
                aliases[a] = c

        def key(name: str) -> str:
            base = ident.source_team_key_base(name)
            return aliases.get(base, base)

        return key
    finally:
        ident.TEAM_TOKEN_FOLDS = saved


def _club_string(name: str) -> str:
    """The name's club words: spacing, structure tokens and United spelling gone.

    A truncated token ("Unite", "Utd") is the same word as "United" here, and
    the word breaks are removed because the feed truncates at a character
    count, not at a word boundary ("North East Utd" / "NorthEast United").
    """
    words = [w for w in ident.team_identity_words(name).split()
             if w not in ident.TEAM_STRUCTURE_NOISE]
    return "".join("united" if w == "utd" or w.startswith("unit") else w for w in words)


def _same_club_by_words(a: str, b: str) -> bool:
    """One club when either club string is a prefix of the other.

    The archive's spellings of one club are character-count truncations of each
    other ("Scunthorpe" / "Scunthorpe Unite" / "Scunthorpe United"), so a
    prefix relation is the yardstick. It is applied only *within* a seam key
    group; different clubs with prefix names (Dundee / Dundee United) are
    separate keys and are pinned by their own tests.
    """
    if a == b:
        return True
    return len(a) >= 4 and len(b) >= 4 and (a.startswith(b) or b.startswith(a))


def test_every_group_the_abbreviation_fold_touches_is_one_club():
    """The gate for the fold: every key group holding a United/Utd spelling
    is one club, once word breaks, club-structure tokens and the United
    spelling are set aside.

    The set is the whole class, not just what the fold itself merges: the
    curated pairs added beside it cover most of the class, and a later pair
    must not slip a wrong group in behind them. Full group list:
    handoff/round5_form_h2h_2026-10-12/a_identity_checks.txt.
    """
    # measured 2026-10-12: 70 such groups, 0 wrong by the club-string test
    names = _corpus_names()
    if not names:
        pytest.skip("committed monthly archive not present")
    key = _key_with_folds(ident.TEAM_TOKEN_FOLDS)
    groups: dict[str, set[str]] = defaultdict(set)
    for name in names:
        groups[key(name)].add(name)
    utd_groups = {k: sorted(m) for k, m in groups.items()
                  if len(m) > 1 and any("utd" in n.lower().split() for n in m)}
    assert len(utd_groups) >= 40, f"only {len(utd_groups)} groups hold a Utd spelling"
    wrong = {}
    for key, members in utd_groups.items():
        strings = [_club_string(m) for m in members]
        if not all(_same_club_by_words(x, y)
                   for i, x in enumerate(strings) for y in strings[i + 1:]):
            wrong[key] = members
    assert wrong == {}, f"{len(wrong)} groups join different clubs: {wrong}"


def test_known_collision_barcelona_sc_is_reported_not_fixed():
    """A pre-existing over-merge: 'SC' is a structure token, so Ecuador's
    Barcelona SC folds onto FC Barcelona's key. Measured 2026-10-12 while
    gating the fold above; reported to the operator as a defect rather than
    fixed here, because removing a structure token (or keying by country)
    is an identity-layer decision with a corpus-wide blast radius. This test
    pins the current state so the report and the code agree; the day it is
    fixed, this assertion flips and the record must be updated.
    """
    assert ident.source_team_key("Barcelona SC") == ident.source_team_key("Barcelona")


def test_the_archive_spelling_of_this_rounds_fixture_now_joins():
    """The concrete failure this round found: 'Newcastle Utd' on the pick
    surface and 'Newcastle' in the archive were two keys, so the 43 archive
    rows behind this round's own worked fixture were invisible to the
    features. See handoff/round5_form_h2h_2026-10-12/w4_page_vs_archive.txt.
    """
    assert ident.source_team_key("Newcastle Utd") == ident.source_team_key("Newcastle")
