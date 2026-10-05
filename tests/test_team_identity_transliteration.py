"""Regression tests for the 2026-10-05 Türkiye/Turkey fixture-identity split.

Root cause (both confirmed in the repo before the fix):

1. ``norm_team`` DELETED diacritics instead of transliterating them
   (``norm_team("Türkiye") == "trkiye"``), so it disagreed with
   ``ledger_team_key`` ("turkiye") and with the plain ASCII spelling
   ("turkey") — three keys for one team.
2. No curated exonym alias Türkiye<->Turkey existed, so even perfect
   transliteration could not join the 2022 rename.

Result: one real match ("Italy vs Türkiye" / "Italy vs Turkey") scored,
reported, ledgered and nearly staked twice.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.identity import source_team_key  # noqa: E402
from edgefactory.util import (  # noqa: E402
    canonical_team_key,
    fold_ascii,
    explain_team_key,
    ledger_team_key,
    norm_team,
    norm_team_legacy,
    norm_team_sql,
    norm_team_sql_legacy,
)


def _load_picks_today():
    spec = importlib.util.spec_from_file_location(
        "picks_today_translit", ROOT / "scripts" / "picks_today.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- 1. transliteration -----------------------------------------------------

ACCENTED_CORPUS = {
    "Türkiye": "turkiye",
    "Beşiktaş": "besiktas",
    "Nordsjælland": "nordsjael",
    "Strømsgodset": "stromsgod",
    "Nõmme United": "nommeunit",
    "América": "america",
    "Bayern München": "bayernmun",
    "Córdoba": "cordoba",
    "Göztepe": "goztepe",
}


ACCENTED_TO_ASCII_SPELLING = {
    "Türkiye": "Turkiye",
    "Beşiktaş": "Besiktas",
    "Atlético Madrid": "Atletico Madrid",
    "Nordsjælland": "Nordsjaelland",
    "Strømsgodset": "Stromsgodset",
    "Bayern München": "Bayern Munchen",
    "Fenerbahçe": "Fenerbahce",
}


def test_norm_team_transliterates_instead_of_deleting():
    for raw, expected in ACCENTED_CORPUS.items():
        assert norm_team(raw) == expected, raw
        # no letters silently vanish any more
        assert norm_team(raw) != norm_team_legacy(raw) or raw.isascii()


def test_accented_spelling_keys_exactly_like_its_ascii_spelling():
    """The fix makes an accented name behave as its ASCII spelling does.

    It inherits that spelling's behaviour, including the PRE-EXISTING
    width-9 noise-token collision class (norm_team strips "atletico",
    "real", "u21"...). That class is documented in edgefactory/identity.py
    and is deliberately NOT touched here; identity seams use the
    collision-safe source_team_key instead.
    """
    for accented, ascii_spelling in ACCENTED_TO_ASCII_SPELLING.items():
        assert norm_team(accented) == norm_team(ascii_spelling), accented
        assert norm_team(accented) == norm_team_legacy(ascii_spelling), accented


def test_norm_team_and_ledger_team_key_agree_on_accented_corpus():
    for raw in ACCENTED_CORPUS:
        if explain_team_key(raw)["alias_matched_key"]:
            continue  # alias layer deliberately re-points these (Türkiye)
        assert norm_team(raw) == ledger_team_key(raw), raw


def test_legacy_key_is_frozen_for_historical_reads():
    assert norm_team_legacy("Türkiye") == "trkiye"
    assert norm_team_legacy("Beşiktaş") == "beikta"
    assert norm_team_legacy("Turkey") == "turkey"
    # the frozen SQL mirror matches the frozen python form
    assert "lower(" in norm_team_sql_legacy("home")
    # the live SQL mirror ASCII-folds, like the live python form
    assert "replace(" in norm_team_sql("home")


# --- 2. curated exonym alias ------------------------------------------------

def test_turkiye_and_turkey_share_one_canonical_key():
    assert canonical_team_key("Türkiye") == canonical_team_key("Turkey") == "turkey"
    assert ledger_team_key("Türkiye", width=24) == ledger_team_key("Turkey", width=24)
    assert source_team_key("Türkiye") == source_team_key("Turkey")


def test_alias_is_explicit_curated_and_visible():
    info = explain_team_key("Türkiye")
    assert info["alias_source"] == "Config/entity_overrides.json:teams"
    assert info["alias_canonical_name"] == "Turkey"
    assert info["canonical_team_key"] == "turkey"
    # no alias invented for an unknown name
    assert explain_team_key("Jupiter Rovers")["alias_matched_key"] is None


def test_other_curated_exonyms():
    assert canonical_team_key("Czechia") == canonical_team_key("Czech Republic")
    assert canonical_team_key("Cabo Verde") == canonical_team_key("Cape Verde")


# --- 5. no false merges -----------------------------------------------------

DISTINCT_TEAMS = [
    "Türkiye", "Turkmenistan", "Turkey U21", "Italy", "Israel",
    "Beşiktaş", "Besiktas JK", "Bestikas",  # near-spellings
    "Göztepe", "Gaziantep", "Galatasaray", "Fenerbahçe",
    "Strømsgodset", "Stromsgodset IF", "Sandefjord", "Sarpsborg 08",
    "Nordsjælland", "Nordsjaelland", "Norrkoping", "Nõmme United",
    "América Mineiro", "America MG", "Americano", "Athletico PR",
    "Czechia", "Czech Republic", "Chechnya",
]


def test_transliteration_does_not_merge_previously_distinct_teams():
    """Tightening-safety: the fold must not collapse two REAL teams.

    Pairs that already shared a legacy key keep sharing it (that is the
    separate, documented width-9 collision class, untouched here); the
    test fails only on NEW merges introduced by transliteration/aliasing.
    """
    new_merges = []
    for i, a in enumerate(DISTINCT_TEAMS):
        for b in DISTINCT_TEAMS[i + 1:]:
            merged_now = canonical_team_key(a, width=24) == canonical_team_key(b, width=24)
            # baseline = the PRE-FIX operational key
            # (old ledger_team_key == norm_team_legacy(fold_ascii(x)))
            merged_before = (norm_team_legacy(fold_ascii(a), 24)
                             == norm_team_legacy(fold_ascii(b), 24))
            if merged_now and not merged_before:
                new_merges.append((a, b))
    # The ONLY intended new merges are the curated alias pairs.
    intended = {("Türkiye", "Turkey"), ("Türkiye", "Turkey U21"),
                ("Czechia", "Czech Republic"),
                ("América Mineiro", "America MG")}
    unexpected = [p for p in new_merges if p not in intended]
    assert unexpected == [], f"unexpected merges: {unexpected}"
    # ("Türkiye", "Turkey U21") is the PRE-EXISTING width-9 squad-token
    # collision ("Turkey U21" -> "turkey" long before this fix) inherited
    # via the curated alias. The collision-safe identity key keeps the
    # senior and U21 sides apart, which is where it matters.
    assert source_team_key("Türkiye") != source_team_key("Turkey U21")


# --- 3./4. end-to-end dedupe + tripwire ------------------------------------

def _pick(home, away, odds, kickoff, avg_p, source):
    return {
        "date": "2026-10-05", "home": home, "away": away,
        "match": f"{home} vs {away}", "league": "World Cup",
        "market": "match_winner", "pick": "home", "selection_side": "home",
        "odds": odds, "kickoff": kickoff, "avg_p": avg_p,
        "odds_source": source, "bucket": "CERTIFIED_CLEAN",
        "statistical_comment": "n=900", "w_score": 1.0,
    }


def test_end_to_end_dedupe_of_turkiye_turkey_pair():
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Türkiye", 1.42, "05-10, 19:45", 0.70, "zulubet"),
        _pick("Italy", "Turkey", 1.47, "14:45", 0.64, "betexplorer"),
    ]
    out, removed = pt.collapse_final_operational_picks(rows)
    assert len(out) == 1
    assert removed == 1
    assert out[0]["ctx"]["duplicate_alias_collapse"] == "true"
    # one canonical identity for both spellings
    assert (pt.canonical_fixture_identity(rows[0])
            == pt.canonical_fixture_identity(rows[1])
            == ("2026-10-05", "italy", "turkey"))


def test_tripwire_silent_once_alias_resolves_the_pair():
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Türkiye", 1.42, "05-10, 19:45", 0.70, "zulubet"),
        _pick("Italy", "Turkey", 1.47, "14:45", 0.64, "betexplorer"),
    ]
    collapsed, _ = pt.collapse_final_operational_picks(rows)
    assert pt.near_duplicate_fixture_warnings(collapsed) == []


def test_tripwire_fires_when_no_alias_can_join_and_merges_nothing():
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Greece", 1.42, "05-10, 19:45", 0.70, "zulubet"),
        _pick("Italy", "Portugal", 1.47, "05-10, 19:45", 0.64, "betexplorer"),
    ]
    collapsed, removed = pt.collapse_final_operational_picks(rows)
    assert removed == 0 and len(collapsed) == 2  # nothing auto-merged
    warnings = pt.near_duplicate_fixture_warnings(collapsed)
    assert len(warnings) == 1
    assert warnings[0]["shared_side"] == "home"


def test_tripwire_prints_loud_block(capsys):
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Greece", 1.42, "05-10, 19:45", 0.70, "zulubet"),
        _pick("Italy", "Portugal", 1.47, "05-10, 19:45", 0.64, "betexplorer"),
    ]
    n = pt.print_near_duplicate_fixture_tripwire(rows, day="2026-10-05")
    err = capsys.readouterr().err
    assert n == 1
    assert "NEAR-DUPLICATE FIXTURE TRIPWIRE" in err
    assert "Italy vs Greece" in err and "Italy vs Portugal" in err


def test_distinct_fixtures_are_not_collapsed():
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Türkiye", 1.42, "05-10, 19:45", 0.70, "zulubet"),
        _pick("Italy", "Israel", 1.47, "05-10, 19:45", 0.64, "betexplorer"),
    ]
    out, removed = pt.collapse_final_operational_picks(rows)
    assert removed == 0 and len(out) == 2


# --- 6./7. settlement + shadow identity coherence --------------------------

def test_settlement_joins_across_spellings():
    from edgefactory.scored_candidate_shadow import settle_candidate

    settled = {("2026-10-05", canonical_team_key("Italy"),
                canonical_team_key("Turkey")): "home"}
    cand = {"market": "1x2", "selection_side": "home",
            "home_team": "Italy", "away_team": "Türkiye",
            "trading_date": "2026-10-05"}
    out = settle_candidate(cand, settled)
    assert out["settlement_status"] == "win"


def test_settlement_still_reads_legacy_keyed_results():
    from edgefactory.scored_candidate_shadow import settle_candidate

    legacy = {("2026-10-05", norm_team_legacy("Beşiktaş"),
               norm_team_legacy("Göztepe")): "home"}
    cand = {"market": "1x2", "selection_side": "home",
            "home_team": "Beşiktaş", "away_team": "Göztepe",
            "trading_date": "2026-10-05"}
    assert settle_candidate(cand, legacy)["settlement_status"] == "win"


def test_shadow_fixture_identity_is_single_for_the_pair():
    from edgefactory.scored_candidate_shadow import (
        candidate_id, fixture_id, fixture_occurrence_identity)

    a = {"home": "Italy", "away": "Türkiye", "market": "match_winner",
         "pick": "home", "kickoff": "2026-10-05T19:45:00+02:00",
         "league": "World Cup"}
    b = dict(a, away="Turkey")
    assert fixture_id(a, "2026-10-05") == fixture_id(b, "2026-10-05")
    assert candidate_id(a, "2026-10-05") == candidate_id(b, "2026-10-05")
    assert (fixture_occurrence_identity(a, "2026-10-05")["fixture_occurrence_id"]
            == fixture_occurrence_identity(b, "2026-10-05")["fixture_occurrence_id"])


# --- archived count not inflated -------------------------------------------

def test_day_archive_merge_does_not_double_count_spellings():
    pt = _load_picks_today()
    existing = [_pick("Italy", "Türkiye", 1.42, "05-10, 19:45", 0.70, "zulubet")]
    fresh = [_pick("Italy", "Turkey", 1.47, "14:45", 0.64, "betexplorer")]
    merged = pt.merge_day_archive_rows(existing, fresh, "2026-10-05")
    assert len(merged) == 1
    # first-frozen-wins is preserved
    assert merged[0]["odds"] == 1.42
    # engine ledger key and audit key agree on identity
    from scripts import audit_recent_picks as audit
    assert (pt._day_archive_row_key(existing[0], "2026-10-05")
            == audit._archive_pick_key(fresh[0], "2026-10-05"))
