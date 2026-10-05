"""Squad-level fixture identity hardening.

The settlement key space is deterministic only: transliteration, curated
aliases, club-stem marker stripping, and explicit squad suffixes.  No fuzzy
matching is introduced here.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.scored_candidate_shadow import (  # noqa: E402
    _settlement_key_specs,
    settle_candidate,
)
from edgefactory.util import (  # noqa: E402
    canonical_team_key,
    squad_markers,
    strip_squad_markers,
)


def _load_auto_tickets():
    spec = importlib.util.spec_from_file_location(
        "auto_tickets_squad_identity", ROOT / "scripts" / "auto_tickets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pick(home: str, away: str, selection: str = "home") -> dict:
    return {"date": "2026-10-05", "home": home, "away": away, "pick": selection}


# --- marker vocabulary + club-stem keys -----------------------------------


def test_marker_vocabulary_builds_keys_from_club_stem_plus_suffix():
    cases = {
        "Turkey U-21": (frozenset({"u21"}), "turkey", "turkey_u21"),
        "Turkey Under 21": (frozenset({"u21"}), "turkey", "turkey_u21"),
        "Brazil Sub 20": (frozenset({"u20"}), "brazil", "brazil_u20"),
        "Atl. San Luis U2": (frozenset({"u2x"}), "atl san luis", "atlsanlui_u2x"),
        "Jong Ajax": (frozenset({"youth"}), "ajax", "ajax_youth"),
        "Ajax Youth": (frozenset({"youth"}), "ajax", "ajax_youth"),
        "Milan Primavera": (frozenset({"youth"}), "milan", "milan_youth"),
        "Bayern Amateure": (frozenset({"res"}), "bayern", "bayern_res"),
        "Bayern Frauen": (frozenset({"w"}), "bayern", "bayern_w"),
        "Los Angeles FC 2": (frozenset({"b"}), "los angeles fc", "losangele_b"),
        "Ha Noi 2 W": (frozenset({"b", "w"}), "ha noi", "hanoi_b_w"),
    }
    for name, (markers, stem, key) in cases.items():
        assert squad_markers(name) == markers, name
        assert strip_squad_markers(name) == stem, name
        assert canonical_team_key(name) == key, name


def test_primavera_senior_clubs_and_marker_exemptions_do_not_gain_markers():
    for name in ("Primavera", "Primavera EC", "Primavera SP", "B 1903",
                 "B36 Tórshavn", "W Connection"):
        assert squad_markers(name) == frozenset(), name


# --- settlement cannot cross the senior/squad boundary --------------------


def test_auto_ticket_senior_result_never_grades_youth_leg_and_vice_versa():
    at = _load_auto_tickets()
    senior_settled = {
        ("2026-10-05", hk, ak): "home"
        for hk, ak in at._result_write_keys("Turkey", "Spain")
    }
    youth_settled = {
        ("2026-10-05", hk, ak): "home"
        for hk, ak in at._result_write_keys("Turkey U21", "Spain U21")
    }

    assert at.pick_result(_pick("Turkey", "Spain"), senior_settled) == "win"
    assert at.pick_result(_pick("Turkey U21", "Spain U21"), senior_settled) is None
    assert at.pick_result(_pick("Turkey", "Spain"), youth_settled) is None
    assert at.pick_result(_pick("Turkey U21", "Spain U21"), youth_settled) == "win"


def test_shadow_settlement_senior_result_never_grades_youth_candidate():
    senior_settled = {
        ("2026-10-05", hk, ak): "home"
        for hk, ak in _settlement_key_specs("Turkey", "Spain")
    }
    youth = {"market": "1x2", "selection_side": "home",
             "home_team": "Turkey U21", "away_team": "Spain U21",
             "trading_date": "2026-10-05"}
    assert settle_candidate(youth, senior_settled)["settlement_status"] == "pending"


def test_legacy_blind_lookup_keys_are_tagged_and_not_written_for_squad_rows():
    at = _load_auto_tickets()
    assert at._result_write_keys("Turkey U21", "Spain U21") == [
        ("turkey_u21", "spain_u21")]
    lookup = at._exact_result_lookup_specs("Turkey U21", "Spain U21")
    assert ("turkey", "spain", True) in lookup
    # The public/write-safe surface never returns the pre-suffix blind key.
    assert ("turkey", "spain") not in at._exact_result_keys("Turkey U21", "Spain U21")


# --- second-team level tolerance is uniqueness-guarded --------------------


def test_level_tolerant_lookup_links_truncated_u2_to_unique_u21_result():
    at = _load_auto_tickets()
    settled = {
        ("2026-10-05", hk, ak): "home"
        for hk, ak in at._result_write_keys("Atl. San Luis U21", "Cruz Azul U21")
    }
    assert at.pick_result(
        _pick("Atl. San Luis U2", "Cruz Azul U21"), settled) == "win"


def test_level_tolerant_lookup_fails_closed_on_disagreeing_second_teams():
    at = _load_auto_tickets()
    settled = {}
    for home, outcome in (("Club U20", "home"), ("Club U23", "away")):
        for hk, ak in at._result_write_keys(home, "Opponent U20"):
            settled[("2026-10-05", hk, ak)] = outcome
    assert at.pick_result(_pick("Club Youth", "Opponent U20"), settled) is None


def test_level_tolerant_lookup_never_synthesizes_senior_boundary_key():
    at = _load_auto_tickets()
    senior = {
        ("2026-10-05", hk, ak): "home"
        for hk, ak in at._result_write_keys("Club", "Opponent")
    }
    assert at.pick_result(_pick("Club U23", "Opponent U23"), senior) is None

# --- curated residual-ambiguity aliases -----------------------------------


def test_curated_archive_truncation_aliases_are_explicit_and_marker_safe():
    alias_pairs = [
        ("Charleston", "Charleston Battery"),
        ("Charlotte Independ.", "Charlotte Independence"),
        ("Neftci Baku W", "Neftçi Bakı W"),
        ("Buducnost W", "Budućnost Podgorica W"),
        ("Ulricehamn W", "Ulricehamns IFK W"),
        ("A.D. Isidro Meta", "AD Isidro Metapan"),
        ("Al-Arabi Club(KU", "Al Arabi Kuwait"),
        ("St Patricks Dublin", "St. Patricks Athletic"),
        ("Giravanz K.", "Giravanz Kitakyu"),
        ("Ellas Syrou", "Ellas Syros"),
        ("Egnatia Rrogozhi", "Egnatia Rrogozhine"),
    ]
    at = _load_auto_tickets()
    for a, b in alias_pairs:
        assert canonical_team_key(a, width=24) == canonical_team_key(b, width=24), (a, b)
        assert at._same_club_names(a, b), (a, b)


def test_same_club_name_link_compares_club_stems_after_equal_markers():
    at = _load_auto_tickets()
    assert at._same_club_names("Hegelmann II", "Hegelmann Litauen 2")
    assert at._same_club_names("Minnesota 2", "Minnesota United II")
    assert not at._same_club_names("Minnesota United", "Minnesota United II")

# --- verified-result precedence and ambiguity live coverage ----------------


def test_verified_result_overrides_canonical_donor_key(tmp_path, monkeypatch):
    """Operator-verified scores outrank donor rows in every exact key space.

    This pins the Pafos/Dinamo Tirana case: Forebet carried a 2-2 draw on the
    canonical fixture key, while the operator-verified score is 4-2 home.
    The verified row must overwrite the canonical key, not only the historical
    norm_team key, so any donor conflict resolves for an explicit provenance
    reason rather than by accidental key drift.
    """
    import duckdb
    import edgefactory.settlement as settlement_mod

    at = _load_auto_tickets()
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    con = duckdb.connect(str(tmp_path / "warehouse.duckdb"))
    con.execute("CREATE TABLE forebet_settled "
                "(date VARCHAR, home VARCHAR, away VARCHAR, hs INTEGER, gs INTEGER, outcome VARCHAR)")
    con.execute("INSERT INTO forebet_settled VALUES "
                "('2026-08-27','Pafos','Dinamo Tirana',2,2,'draw')")
    con.execute("CREATE TABLE bettingclosed_settled "
                "(date VARCHAR, home VARCHAR, away VARCHAR, hs INTEGER, gs INTEGER, outcome VARCHAR)")
    con.execute("INSERT INTO bettingclosed_settled VALUES "
                "('2026-08-27','Pafos','KS Dinamo Tirana',4,2,'home')")
    con.close()

    verified = [{"date": "2026-08-27", "home": "Pafos", "away": "Dinamo Tirana",
                 "hs": 4, "gs": 2, "outcome": "home", "src": "operator_verified"}]
    monkeypatch.setattr(settlement_mod, "load_verified_results", lambda: verified)

    settled = at.load_settled()
    canonical_key = ("2026-08-27", canonical_team_key("Pafos"),
                     canonical_team_key("Dinamo Tirana"))
    assert settled[canonical_key] == "home"
    assert at.pick_result(
        {"date": "2026-08-27", "home": "Pafos", "away": "Dinamo Tirana",
         "pick": "home"},
        settled,
    ) == "win"


def test_ambiguity_detector_still_drops_distinct_width_collision():
    at = _load_auto_tickets()
    entries = {"2026-10-05": [
        {"home": "Manchester City", "away": "Arsenal", "result": "home"},
        {"home": "Manchester United", "away": "Arsenal", "result": "away"},
    ]}
    key_to = {}
    for day, rows in entries.items():
        for row in rows:
            for hk, ak in at._result_write_keys(row["home"], row["away"]):
                key_to[(day, hk, ak)] = row["result"]

    dropped, detail = at._drop_ambiguous_result_keys(key_to, entries)
    assert dropped >= 1
    collided = {name for _day, names in detail for name in names}
    assert "Manchester City vs Arsenal" in collided
    assert "Manchester United vs Arsenal" in collided
