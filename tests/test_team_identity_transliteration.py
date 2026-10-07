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
import json
import sys
from pathlib import Path

import pytest

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


# --- verdict inheritance across spellings (LIVE gating change) -------------

def _purity(team_entries):
    return {"contexts": {"league": {}, "team": team_entries, "odds_band": {},
                         "competition_type": {}, "niche": {}}}


def _ctx_pick(away):
    return {"home": "Italy", "away": away, "league": "World Cup",
            "market": "1x2", "pick": "home", "odds": 1.42,
            "edge_rule": "2way-unanimous avg_p>=60"}


def test_accented_spelling_inherits_canonical_team_verdict():
    """Türkiye and Turkey must resolve to ONE verdict, fail-closed.

    The live purity registry learned its keys under "turkiye" and has NO
    "turkey" entries, so before this change the two spellings carried
    different verdicts (VETO vs UNKNOWN). This is an intended LIVE gating
    change: a veto learned under any spelling now vetoes both.
    """
    pt = _load_picks_today()
    purity = _purity({
        "soccer|turkiye|*|1x2|away": {"verdict": "VETO", "n": 40},
    })
    for away in ("Türkiye", "Turkey"):
        ctx = pt.lookup_context(purity, _ctx_pick(away))
        assert ctx["away_norm"] == "turkey"
        assert ctx["team_a"] == "VETO", away


def test_verdict_merge_is_fail_closed_not_fail_open():
    pt = _load_picks_today()
    purity = _purity({
        "soccer|turkiye|*|1x2|away": {"verdict": "VETO", "n": 40},
        "soccer|turkey|*|1x2|away": {"verdict": "ALLOW", "n": 400},
    })
    # the restrictive verdict wins regardless of sample size or spelling
    for away in ("Türkiye", "Turkey"):
        assert pt.lookup_context(purity, _ctx_pick(away))["team_a"] == "VETO"


def test_unknown_never_displaces_an_existing_verdict():
    pt = _load_picks_today()
    purity = _purity({"soccer|turkiye|*|1x2|away": {"verdict": "ALLOW", "n": 40}})
    assert pt.lookup_context(purity, _ctx_pick("Turkey"))["team_a"] == "ALLOW"


def test_non_aliased_team_lookup_is_unchanged():
    pt = _load_picks_today()
    purity = _purity({"soccer|kongsvinger|*|1x2|away": {"verdict": "CAUTION", "n": 30}})
    ctx = pt.lookup_context(purity, {"home": "Moss", "away": "Kongsvinger",
                                     "league": "Norway 2", "market": "1x2",
                                     "pick": "home", "odds": 1.5,
                                     "edge_rule": "r"})
    assert ctx["team_a"] == "CAUTION"
    assert ctx["away_norm"] == "kongsvinger"


# --- alias table drift ------------------------------------------------------

def test_curated_alias_tables_do_not_drift():
    """identity.TEAM_KEY_RAW_ALIASES mirrors Config/entity_overrides.json.

    Every exonym pair expressed in the identity table must agree with the
    override file's canonicalization, so the two curated sources can never
    disagree about which spellings are the same team.
    """
    from edgefactory.entities import canonical_team
    from edgefactory.identity import TEAM_KEY_RAW_ALIASES

    from edgefactory.util import resolve_team_alias

    for alias, canonical in TEAM_KEY_RAW_ALIASES:
        a_override = resolve_team_alias(alias)[1]
        c_override = resolve_team_alias(canonical)[1]
        if a_override is None and c_override is None:
            continue  # identity-only club pair, not an override entry
        assert canonical_team(alias) == canonical_team(canonical), (
            f"identity alias {alias!r}->{canonical!r} disagrees with "
            "Config/entity_overrides.json")


# --- collapse edges ---------------------------------------------------------

def test_anchored_kickoffs_more_than_180_min_apart_never_merge():
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Türkiye", 1.42, "2026-10-05T14:00:00+02:00", 0.70, "zulubet"),
        _pick("Italy", "Turkey", 1.47, "2026-10-05T19:45:00+02:00", 0.64, "betexplorer"),
    ]
    out, removed = pt.collapse_final_operational_picks(rows)
    assert removed == 0 and len(out) == 2


def test_unanchored_merge_is_flagged_for_audit():
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Türkiye", 1.42, "05-10, 19:45", 0.70, "zulubet"),
        _pick("Italy", "Turkey", 1.47, "14:45", 0.64, "betexplorer"),
    ]
    out, removed = pt.collapse_final_operational_picks(rows)
    assert removed == 1
    assert out[0]["ctx"]["duplicate_kickoff_unanchored"] == "true"


def test_anchored_merge_is_not_flagged_unanchored():
    pt = _load_picks_today()
    rows = [
        _pick("Italy", "Türkiye", 1.42, "2026-10-05T19:45:00+02:00", 0.70, "zulubet"),
        _pick("Italy", "Turkey", 1.47, "2026-10-05T19:45:00+02:00", 0.64, "betexplorer"),
    ]
    out, removed = pt.collapse_final_operational_picks(rows)
    assert removed == 1
    assert "duplicate_kickoff_unanchored" not in out[0]["ctx"]


# --- frozen research-ledger identity ---------------------------------------

def test_research_ledger_identity_is_frozen_pre_alias():
    """The ml-fade research ledger persists event_key and reconciles on it.

    It must keep the pre-2026-10-05 operational key (transliteration, no
    curated alias) or historical rows would be orphaned by re-keying.
    """
    from edgefactory.util import fold_ascii as _fold
    from edgefactory.util import research_ledger_team_key

    for raw in ("Türkiye", "Nordsjælland", "Beşiktaş", "Turkey"):
        # byte-identical to the pre-fix ledger_team_key definition
        assert research_ledger_team_key(raw) == norm_team_legacy(_fold(raw))
    # explicitly NOT canonicalized by the alias layer
    assert research_ledger_team_key("Türkiye") == "turkiye"
    assert research_ledger_team_key("Türkiye") != canonical_team_key("Türkiye")


def test_ml_fade_event_key_unchanged_for_accented_names():
    from edgefactory.ml_fade_research import event_key

    assert (event_key("ml-fade", "2026-10-05", "Italy", "Türkiye")
            == "2026-10-05|italy|turkiye|ml-fade|1x2")


# --- curated alias layer (Config/entity_overrides.json -> teams) ------------
#
# Every curated pair must fold at EVERY key seam, and — where the odds-matching
# maps carry the same fold — must join a donor price as ``exact``.  Coverage is
# derived from the curated table itself, so a newly curated team is covered by
# construction instead of needing a test of its own.
#
# 2026-10-07 SharpAPI receipt: the vendor's "Urawa Red Diamonds" against our
# card's "Urawa" missed the exact key, fell through to the bigram matcher, and
# quarantined the pick as SUSPECT_ALIAS_FUZZY (push_eligible=False).


def _curated_team_pairs():
    teams = json.loads((ROOT / "Config" / "entity_overrides.json").read_text())["teams"]
    return sorted((raw, str(canon)) for raw, canon in teams.items() if raw != canon)


@pytest.mark.parametrize("raw,canonical", _curated_team_pairs())
def test_curated_alias_folds_every_identity_seam(raw, canonical):
    from edgefactory.entities import canonical_team

    assert canonical_team_key(raw) == canonical_team_key(canonical)
    assert ledger_team_key(raw, width=24) == ledger_team_key(canonical, width=24)
    assert canonical_team(raw) == canonical_team(canonical)
    assert source_team_key(raw) == source_team_key(canonical)


def test_curated_alias_donor_spelling_joins_the_card_pick_exactly():
    """Where both curated layers carry the fold, the price join is exact."""
    pt = _load_picks_today()
    from edgefactory import price_sources as psrc

    folded = [(raw, canon) for raw, canon in _curated_team_pairs()
              if pt.odds_team_key(raw) == pt.odds_team_key(canon)
              and pt.odds_match_team_key(raw) == pt.odds_match_team_key(canon)]
    # the 2026-10-07 receipt must stay in the set the fold actually reaches
    assert ("Urawa Red Diamonds", "urawa") in folded

    day, away = "2026-10-07", "Omiya Ardija"
    for vendor_home, card_home in folded:
        pick = {"date": day, "home": card_home, "away": away, "match": f"{card_home} vs {away}",
                "kickoff": "07-10, 10:00", "kickoff_utc": f"{day}T09:00:00+00:00",
                "market": "1x2", "pick": "home"}
        row = {"source": "sharpapi_odds", "date": day, "home": vendor_home, "away": away,
               "market": "1x2", "selection": "home", "odds": 1.741,
               "bookmaker": "draftkings", "odds_kind": "bookmaker",
               "kickoff": f"{day}T09:00Z", "captured_at": f"{day}T04:21:52+00:00"}
        bundle = pt._odds_bundle_from_rows(
            [psrc.annotate_row(dict(row), source="sharpapi_odds")], provider="sharpapi_odds")
        _, method = pt.find_odds_row(pick, bundle)
        assert method == "exact", (vendor_home, card_home)


@pytest.mark.parametrize("raw,canonical", _curated_team_pairs())
def test_curated_alias_never_carries_a_marked_squad_onto_the_senior_key(raw, canonical):
    """The alias canonicalizes the CLUB, never the squad (2026-10-07 fix).

    The width-9 odds key space strips a distinct-entity marker before
    truncating, so ``"Urawa Red Diamonds W"`` and ``"Urawa Red Diamonds"``
    both key as ``urawaredd`` — an alias lookup on that key resolves a
    women's/reserve spelling onto the SENIOR side's canonical key. The
    entity layer already refuses this (``entities.canonical_team``
    re-attaches the marker suffix, ``urawa_w``); the odds layer did not,
    and handed a women's row our card's byte-identical exact join key.
    Measured at the defect: 17 of 157 curated pairs were alias-bridged
    across the marker, all released by this guard; the wider hazard is
    older and only partly fixed — 87 marked variants collapsed onto their
    canonical at the defect and 70 still do by truncation/stripping alone,
    with no alias involved. Measured before/after the guard.
    """
    pt = _load_picks_today()
    marked = f"{raw} W"
    assert pt.odds_team_key(marked) == norm_team(fold_ascii(marked))


def test_curated_alias_marked_squad_never_joins_the_card_pick_exactly():
    """The rule above, at the join: fail-closed means never ``exact``.

    Before the guard, a vendor's women's spelling keyed byte-identically to
    our card row and ``find_odds_row`` returned "exact" — the most trusted
    verdict, no quarantine. A marked donor row may still be picked up by
    the similarity fallback (quarantined SUSPECT_ALIAS_FUZZY, never
    push-eligible); it must not reach the exact tier.
    """
    pt = _load_picks_today()
    from edgefactory import price_sources as psrc

    # Pairs where ONLY an alias could bridge the marked spelling: the fold
    # reaches the unmarked pair, and the marked spelling's unaliased key
    # differs from the canonical's key.
    bridged = [(raw, canon) for raw, canon in _curated_team_pairs()
               if pt.odds_team_key(raw) == pt.odds_team_key(canon)
               and norm_team(fold_ascii(f"{raw} W")) != pt.odds_team_key(canon)]
    assert ("Urawa Red Diamonds", "urawa") in bridged
    assert bridged  # the defect class must stay reachable by this test

    day, away = "2026-10-07", "Omiya Ardija"
    for vendor_home, card_home in bridged:
        pick = {"date": day, "home": card_home, "away": away,
                "match": f"{card_home} vs {away}", "kickoff": "07-10, 10:00",
                "kickoff_utc": f"{day}T09:00:00+00:00",
                "market": "1x2", "pick": "home"}
        row = {"source": "sharpapi_odds", "date": day, "home": f"{vendor_home} W",
               "away": away, "market": "1x2", "selection": "home", "odds": 1.741,
               "bookmaker": "draftkings", "odds_kind": "bookmaker",
               "kickoff": f"{day}T09:00Z", "captured_at": f"{day}T04:21:52+00:00"}
        bundle = pt._odds_bundle_from_rows(
            [psrc.annotate_row(dict(row), source="sharpapi_odds")], provider="sharpapi_odds")
        _, method = pt.find_odds_row(pick, bundle)
        assert method != "exact", (vendor_home, card_home)
