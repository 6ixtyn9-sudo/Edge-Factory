"""Name audit 2026-10-21: truncation map, form-archive joins, alias cases, classifier.

Fix 1: a 16-character archive spelling resolves to its unique longer spelling.
Fix 2: same-club alias pairs found on the fixture date resolve to one key.
Fix 3: the form archive joins truncated and aliased spellings to their club.
Fix 4 (classifier): name_audit separates matched / name_variant /
partner_differs / no_result_row, and matches a home/away swap.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for extra in ("src", "scripts"):
    if str(ROOT / extra) not in sys.path:
        sys.path.insert(0, str(ROOT / extra))

from edgefactory import form_intel as fi  # noqa: E402
from edgefactory.identity import source_team_key, truncation_key_map  # noqa: E402

import name_audit as na  # noqa: E402


# -- fix 1: truncation map -------------------------------------------------

def test_truncated_sixteen_char_spelling_maps_to_full_name():
    m = truncation_key_map(["Hapoel Beer Shev", "Hapoel Beer Sheva"])
    assert m == {source_team_key("Hapoel Beer Shev"): source_team_key("Hapoel Beer Sheva")}


def test_truncation_refused_when_two_longer_clubs_share_the_prefix():
    names = ["Borussia Dortmun", "Borussia Dortmund", "Borussia Dortmun Ii"]
    # The reserve side carries a squad marker, so the senior side is the only candidate.
    m = truncation_key_map(names)
    assert m.get(source_team_key("Borussia Dortmun")) == source_team_key("Borussia Dortmund")
    ambiguous = truncation_key_map(["Enugu Rangers In", "Enugu Rangers Int", "Enugu Rangers Inland"])
    assert source_team_key("Enugu Rangers In") not in ambiguous


def test_truncation_refused_across_squad_markers():
    # A reserve side never folds onto the senior club it was cut from.
    assert truncation_key_map(["Sporting Cristal", "Sporting Cristal II"]) == {}


def test_only_exact_sixteen_character_names_are_truncations():
    assert truncation_key_map(["Vikingur Reyk", "Vikingur Reykjavik"]) == {}


# -- fix 2: same-club alias pairs ------------------------------------------

def test_alias_pairs_resolve_to_one_key():
    pairs = [
        ("Sarpsborg 08", "Sarpsborg FK"),
        ("AS Monaco", "Monaco"),
        ("Atalanta BC", "Atalanta"),
        ("Genclerbirligi", "Gençlerbirliği S.K."),
        ("Grasshopper Zürich", "Grasshoppers"),
        ("Qabala", "Gabala"),
        ("Sporting KC", "Sporting Kansas City"),
    ]
    for alias, canonical in pairs:
        assert source_team_key(alias) == source_team_key(canonical), (alias, canonical)


def test_alias_pairs_do_not_merge_different_clubs():
    assert source_team_key("Viimsi") != source_team_key("FC Tallinn")
    assert source_team_key("Kolos Kovalivka II") != source_team_key("Kolos Kovalivka")


# -- fix 3: the form archive uses the truncation map ----------------------

def _row(day, home, away, hs, gs):
    return {"date": day, "home": home, "away": away, "hs": hs, "gs": gs,
            "league": "Test", "source": "unit"}


def test_form_archive_joins_truncated_spelling_to_full_club():
    rows = [
        _row("2026-08-01", "Hapoel Beer Shev", "Maccabi Haifa", 2, 1),
        _row("2026-08-09", "Hapoel Beer Sheva", "Bnei Yehuda", 0, 0),
    ]
    archive = fi.ResultsArchive(rows, trunc=truncation_key_map(
        [r["home"] for r in rows] + [r["away"] for r in rows]))
    hist = archive.team_rows("Hapoel Beer Sheva")
    assert len(hist) == 2
    assert {r["date"] for r in hist} == {"2026-08-01", "2026-08-09"}


def test_form_archive_without_map_keeps_legacy_join():
    rows = [_row("2026-08-01", "Hapoel Beer Shev", "Maccabi Haifa", 2, 1)]
    archive = fi.ResultsArchive(rows, trunc={})
    assert archive.team_rows("Hapoel Beer Sheva") == []


# -- fix 4: classifier -----------------------------------------------------

def test_classifier_matches_home_away_swap():
    results = [("Wolfsburg", "Heidenheim")]
    assert na.classify("Heidenheim", "Wolfsburg", results) == "matched"


def test_classifier_name_variant_needs_similar_text_on_both_sides():
    results = [("Hapoel Beer Sheva", "Maccabi Haifa")]
    assert na.classify("Hapoel Be'er Sheva", "Maccabi Haifa", results) == "matched"
    results = [("Hapoel Beer Shev", "Maccabi Haifa FC")]
    assert na.classify("Hapoel Beer Sheva", "Maccabi Haifa", results) == "name_variant"


def test_classifier_partner_differs_when_only_one_club_appears():
    results = [("Sparta Praha", "Slavia Praha")]
    assert na.classify("Sparta Prague", "Plzen", results) == "partner_differs"


def test_classifier_no_result_row_when_neither_club_appears():
    assert na.classify("Kufstein", "Imst", [("Rapid Wien", "Salzburg")]) == "no_result_row"
