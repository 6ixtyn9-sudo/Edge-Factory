"""Adversarial (red-team) identity inputs.

Every test here is an attack that was RUN against the branch before it
was written: Unicode normalization forms, homoglyphs, invisible
characters, Turkish dotted I, real clubs whose names begin with a squad
marker, the degenerate-key sentinel, kickoff sufficiency, epoch-boundary
settlement shadowing, and the proof methodology itself. Findings table:
docs/operator/FIXTURE-IDENTITY-SPLIT-2026-10-05.md section 12.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import canonical_team  # noqa: E402
from edgefactory.identity import source_team_key  # noqa: E402
from edgefactory.util import (  # noqa: E402
    ALIAS_CONFIG_WARNINGS, DEGENERATE_KEY_PREFIX, canonical_team_key,
    clear_team_alias_cache, is_degenerate_team_key, norm_team,
    script_anomaly, squad_markers, team_alias_table,
)


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pt():
    return _load("picks_today_adversarial", "scripts/picks_today.py")


def _keys(name):
    return (norm_team(name), canonical_team_key(name),
            source_team_key(name), canonical_team(name))


def _row(home, away, **kw):
    row = {"date": "2026-10-05", "home": home, "away": away,
           "match": f"{home} vs {away}", "league": kw.get("league", "World Cup"),
           "market": "1x2", "pick": "home", "selection_side": "home",
           "odds": kw.get("odds", 1.5), "avg_p": 0.7, "source": "zulubet",
           "kickoff": kw.get("kickoff", "2026-10-05T19:00:00+02:00")}
    if kw.get("kickoff_utc"):
        row["kickoff_utc"] = kw["kickoff_utc"]
    return row


# --- Class 1: Unicode adversaries -----------------------------------------

def test_1a_nfc_and_nfd_spellings_key_identically():
    probes = ["Türkiye", "Beşiktaş", "Atlético Madrid", "Mönchengladbach",
              "Strømsgodset", "Nõmme United", "Nordsjælland"]
    for name in probes:
        assert _keys(unicodedata.normalize("NFC", name)) == \
               _keys(unicodedata.normalize("NFD", name)), name


def test_1a_every_curated_alias_spelling_is_normalization_form_invariant():
    teams = json.loads((ROOT / "Config" / "entity_overrides.json").read_text())["teams"]
    for raw in teams:
        assert _keys(unicodedata.normalize("NFC", raw)) == \
               _keys(unicodedata.normalize("NFD", raw)), raw


def test_1b_homoglyph_name_is_flagged_and_never_silently_merged():
    cyrillic = "Sp\u0430rt\u0430k"  # two Cyrillic 'а'
    assert cyrillic != "Spartak"
    # the fold cannot repair it (that would need a transliteration table
    # for every script) — so it MUST be visible instead.
    assert canonical_team_key(cyrillic) != canonical_team_key("Spartak")
    assert script_anomaly(cyrillic) == "mixed_script_cyrillic"
    assert script_anomaly("Spartak") is None
    assert script_anomaly("Σπάρτακ") is None  # wholly non-Latin: not mixed


def test_1b_sweep_reports_mixed_script_names():
    pt = _pt()
    picks = [_row("Sp\u0430rt\u0430k", "Zenit"), _row("Spartak", "Lokomotiv")]
    counts = pt.print_identity_sweep(picks, day="2026-10-05")
    assert counts["mixed_script_name"] == 1
    flagged = pt.mixed_script_names(picks)
    assert flagged[0]["anomaly"] == "mixed_script_cyrillic"


def test_1c_invisible_characters_do_not_change_any_key():
    for ch in ("\u200b", "\u00a0", "\u00ad", "\u200f", "\u200e", "\ufeff"):
        assert _keys(f"Spar{ch}tak") == _keys("Spartak"), repr(ch)
        assert _keys(f"{ch}Spartak{ch}") == _keys("Spartak"), repr(ch)


def test_1d_turkish_dotted_i_keys_like_ascii():
    for a, b in [("İstanbul Başakşehir", "Istanbul Basaksehir"),
                 ("DİYARBAKIR", "Diyarbakir"),
                 ("Fenerbahçe", "Fenerbahce")]:
        assert _keys(a) == _keys(b), (a, b)


# --- Class 2: marker-veto false positives on real clubs -------------------

def test_2_real_clubs_starting_with_a_marker_token_are_exempt():
    for name in ["W Connection", "W Connection FC", "B 1903", "B36 Tórshavn"]:
        assert squad_markers(name) == frozenset(), name
    # and genuine squad markers still fire
    assert squad_markers("Bayern Munich W") == frozenset({"w"})
    assert squad_markers("Keila II") == frozenset({"b"})


def test_2_same_club_variants_still_merge():
    pt = _pt()
    for a, b in [("W Connection", "W Connection FC"),
                 ("Degerfors IF", "Degerfors"),
                 ("B 1903", "B 1903 Copenhagen"),
                 ("B36 Tórshavn", "B36 Torshavn")]:
        assert pt._merge_veto_reason(_row(a, "X"), _row(b, "X")) is None, (a, b)


def test_2_numeric_club_names_get_a_real_key_not_a_sentinel():
    assert canonical_team_key("B 1903") == "b1903"
    assert not is_degenerate_team_key(canonical_team_key("B 1903"))
    # all-structure names stay fail-closed sentinels
    assert is_degenerate_team_key(canonical_team_key("Athletic Club"))


# --- Class 3: sentinel integrity ------------------------------------------

def test_3_no_natural_name_can_be_mistaken_for_a_sentinel():
    assert DEGENERATE_KEY_PREFIX == "deg~"
    for name in ["Degerfors", "Degerfors IF", "Degenhardt FC", "Deg",
                 "deg12345678", "Degerfors B"]:
        key = canonical_team_key(name)
        assert "~" not in key, (name, key)
        assert not is_degenerate_team_key(key) or len(key.split("_")[0]) < 3


def test_3_sentinel_uses_an_out_of_alphabet_character():
    key = canonical_team_key("Athletic Club")
    assert key.startswith("deg~")
    # keys are built from [a-z0-9] only, so "~" cannot collide
    assert not any(c == "~" for c in canonical_team_key("Degerfors"))


def test_3_legacy_sentinel_form_is_still_recognised_on_read():
    assert is_degenerate_team_key("deg8e878717")
    assert is_degenerate_team_key("deg8e878717_b")
    assert not is_degenerate_team_key("degerfors")


# --- Class 4: kickoff agreement is necessary, never sufficient ------------

def test_4_same_kickoff_blank_leagues_cannot_merge_distinct_clubs():
    pt = _pt()
    ku = "2026-10-05T18:45:00+00:00"
    cases = [("Barcelona", "Barcelona SC", "curated_distinct_clubs"),
             ("Manchester City", "Manchester United", "canonical_team_disagreement"),
             ("Bayern Munich", "Bayern Munich W", "squad_marker_conflict")]
    for a, b, expected in cases:
        ra = _row(a, "Opponent", league="", kickoff_utc=ku)
        rb = _row(b, "Opponent", league="", kickoff_utc=ku, odds=1.9)
        assert pt._kickoff_instants_agree(ra, rb) is True
        assert (pt._merge_veto_reason(ra, rb) or "").startswith(expected), (a, b)
        out, removed = pt.collapse_final_operational_picks([ra, rb])
        assert len(out) == 2 and removed == 0, (a, b)


def test_4_curated_distinct_pairs_are_explicit_not_heuristic():
    pt = _pt()
    assert pt._curated_distinct_clubs("Barcelona", "Barcelona SC")
    assert not pt._curated_distinct_clubs("Barcelona", "Barcelona")
    # a visually similar pair NOT on the curated list is not vetoed here
    assert not pt._curated_distinct_clubs("Girona", "Girona B")


# --- Class 5: epoch-boundary settlement shadowing -------------------------

def _settled(rows):
    at = _load("auto_tickets_adversarial", "scripts/auto_tickets.py")
    entries = {"2026-10-05": rows}
    key_to = {}
    for day, rs in entries.items():
        for e in rs:
            for hk, ak in at._exact_result_keys(e["home"], e["away"]):
                key_to[(day, hk, ak)] = e.get("result")
    at._drop_ambiguous_result_keys(key_to, entries)
    at.SETTLED_KEY_NAMES.clear()
    for day, rs in entries.items():
        for e in rs:
            for hk, ak in at._exact_result_keys(e["home"], e["away"]):
                at.SETTLED_KEY_NAMES.setdefault((day, hk, ak), set()).add(
                    (e["home"], e["away"]))
    return at, key_to


def test_5_senior_result_can_never_settle_a_youth_leg():
    at, settled = _settled([{"home": "Turkey", "away": "Spain", "result": "home"}])
    senior = {"date": "2026-10-05", "home": "Turkey", "away": "Spain", "pick": "home"}
    youth = {"date": "2026-10-05", "home": "Turkey U21", "away": "Spain U21",
             "pick": "home"}
    assert at.pick_result(senior, settled) == "win"
    assert at.pick_result(youth, settled) is None  # stays pending, never graded


def test_5_youth_result_can_never_settle_a_senior_leg():
    at, settled = _settled([{"home": "Turkey U21", "away": "Spain U21",
                             "result": "home"}])
    senior = {"date": "2026-10-05", "home": "Turkey", "away": "Spain", "pick": "home"}
    assert at.pick_result(senior, settled) is None


def test_5_width9_legacy_collision_cannot_cross_settle():
    at, settled = _settled([
        {"home": "Manchester City", "away": "Arsenal", "result": "home"},
        {"home": "Manchester United", "away": "Arsenal", "result": "away"},
    ])
    city = {"date": "2026-10-05", "home": "Manchester City", "away": "Arsenal",
            "pick": "home"}
    united = {"date": "2026-10-05", "home": "Manchester United", "away": "Arsenal",
              "pick": "home"}
    # "mancheste" covers both: the ambiguous key is dropped, so neither leg
    # is graded from the colliding key.
    assert at.pick_result(city, settled) in (None, "win")
    assert at.pick_result(united, settled) in (None, "loss")
    assert not (at.pick_result(city, settled) == "win"
                and at.pick_result(united, settled) == "win")


# --- Class 6: proof methodology -------------------------------------------

def test_6a_historical_merge_clusters_still_collapse():
    """Archived rows are survivors: the pairs that did NOT merge.

    Correct historical merges only survive as duplicate_matches_collapsed
    metadata, so they are replayed from the frozen fixture here (the live
    archive replay lives in the incident doc, section 12).
    """
    pt = _pt()
    cluster = [_row("England", "Congo DR"), _row("England", "DR Congo")]
    out, removed = pt.collapse_final_operational_picks(cluster)
    assert len(out) == 1 and removed == 1


def test_6b_missing_alias_config_degrades_loudly_never_half_applied(tmp_path, monkeypatch):
    import edgefactory.util as util
    monkeypatch.setattr(util, "_overrides_path", lambda: None)
    clear_team_alias_cache()
    try:
        assert team_alias_table() == {}          # all-or-nothing, never partial
        assert ALIAS_CONFIG_WARNINGS, "degradation must be announced"
        assert "ZERO curated aliases" in ALIAS_CONFIG_WARNINGS[0]
    finally:
        monkeypatch.undo()
        clear_team_alias_cache()


def test_6b_malformed_alias_config_degrades_loudly(tmp_path, monkeypatch):
    import edgefactory.util as util
    broken = tmp_path / "entity_overrides.json"
    broken.write_text('{"teams": {"Türkiye": ')
    monkeypatch.setattr(util, "_overrides_path", lambda: broken)
    clear_team_alias_cache()
    try:
        assert team_alias_table() == {}
        assert any("malformed" in w for w in ALIAS_CONFIG_WARNINGS)
    finally:
        monkeypatch.undo()
        clear_team_alias_cache()


def test_6b_alias_layer_recovers_after_the_config_returns():
    clear_team_alias_cache()
    assert team_alias_table(), "baseline config must load"
    assert canonical_team_key("Türkiye") == canonical_team_key("Turkey")


def test_6c_collapse_is_idempotent_on_the_frozen_slate():
    pt = _pt()
    rows = json.loads(
        (ROOT / "tests" / "fixtures"
         / "slate_2026-10-05_identity_split.json").read_text())
    first, removed1 = pt.collapse_final_operational_picks([dict(r) for r in rows])
    second, removed2 = pt.collapse_final_operational_picks([dict(r) for r in first])
    assert removed1 == 1 and removed2 == 0
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
