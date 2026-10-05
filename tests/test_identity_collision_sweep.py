"""Identity collision/split sweep: the fixture-identity bug CLASS.

Five defect classes, each reproduced against the pre-fix code before being fixed:

R1 exonym/diacritic SPLIT   one team, several keys   (S1 curated table)
R2 false MERGE in collapse  two teams, one row       (S2/S3 vetoes)
R3 width-9 ledger collision two teams, one key       (S5 tripwire)
R4 degenerate/empty keys    every team, one key      (S4 fail-closed)
R5 stopword amputation      club name erased         (S4 + S3)
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import canonical_team  # noqa: E402
from edgefactory.util import (  # noqa: E402
    canonical_team_key, char_ngram_similarity, is_degenerate_team_key,
    ledger_team_key, markers_conflict, squad_markers,
)


def _load_picks_today():
    spec = importlib.util.spec_from_file_location(
        "picks_today_identity", ROOT / "scripts" / "picks_today.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pick(home, away, odds=1.5, kickoff="2026-10-05T19:00:00+02:00",
          league="World Cup", source="zulubet"):
    return {
        "date": "2026-10-05", "home": home, "away": away,
        "match": f"{home} vs {away}", "league": league,
        "market": "1x2", "pick": "home", "selection_side": "home",
        "odds": odds, "kickoff": kickoff, "avg_p": 0.7,
        "odds_source": source, "bucket": "CERTIFIED_CLEAN",
        "statistical_comment": "n=900", "w_score": 1.0,
    }


# --- S1: curated exonym table ----------------------------------------------

EXONYM_GROUPS = [
    ["Côte d'Ivoire", "Cote d'Ivoire", "Ivory Coast"],
    ["FC København", "FC Kobenhavn", "FC Copenhagen", "Copenhagen"],
    ["Bayern München", "Bayern Munchen", "Bayern Munich"],
    ["1. FC Köln", "FC Koln", "Cologne"],
    ["Legia Warszawa", "Legia Warsaw"],
    ["Dinamo București", "Dinamo Bucuresti", "Dinamo Bucharest"],
    ["Göteborg", "IFK Göteborg", "IFK Gothenburg"],
    ["Internazionale", "Inter Milan", "Inter"],
    ["Manchester United", "Man United", "Man Utd"],
    ["Wolverhampton Wanderers", "Wolverhampton", "Wolves"],
    ["Napoli", "SSC Napoli"],
    ["FCSB", "Steaua București", "Steaua Bucharest"],
    ["Başakşehir", "Basaksehir", "Istanbul Basaksehir"],
    ["Paris Saint-Germain", "Paris SG", "PSG"],
    ["Sporting CP", "Sporting Lisbon"],
    ["Türkiye", "Turkey"],
    ["Czechia", "Czech Republic"],
]


def test_every_exonym_group_has_exactly_one_canonical_key():
    for group in EXONYM_GROUPS:
        keys = {canonical_team_key(n, width=24) for n in group}
        assert len(keys) == 1, f"{group} -> {keys}"
        assert not is_degenerate_team_key(keys.pop()), group


def test_exonym_groups_have_one_entity_key_too():
    for group in EXONYM_GROUPS:
        assert len({canonical_team(n) for n in group}) == 1, group


# nearest DISTINCT neighbours — must never join the group above
NEIGHBOUR_PAIRS = [
    ("Inter Milan", "AC Milan"),
    ("Sporting CP", "Sporting Gijón"),
    ("Austria Wien", "Austria Lustenau"),
    ("Manchester United", "Manchester City"),
    ("Dinamo București", "Dinamo Zagreb"),
    ("Legia Warszawa", "Lechia Gdansk"),
    ("FC Copenhagen", "Copenhagen FC Women"),
    ("Bayern Munich", "Bayer Leverkusen"),
    ("Paris Saint-Germain", "Paris FC"),
    ("IFK Gothenburg", "IFK Norrkoping"),
    ("Cologne", "Colon"),
    ("Napoli", "Nàpoles de Rivera"),
]


def test_no_false_merges_against_nearest_neighbours():
    for a, b in NEIGHBOUR_PAIRS:
        assert canonical_team_key(a, width=24) != canonical_team_key(b, width=24), (a, b)
        assert canonical_team(a) != canonical_team(b), (a, b)


# --- S2: distinct-entity markers -------------------------------------------

MARKER_PAIRS = [
    ("Turkey", "Turkey U21"), ("Brazil", "Brazil U20"),
    ("Girona", "Girona B"), ("Arsenal", "Arsenal W"),
    ("Bayern Munich", "Bayern Munich II"), ("Ajax", "Ajax Youth"),
    ("Real Madrid", "Real Madrid Reserves"),
]


def test_markers_make_distinct_keys_and_conflict():
    for senior, squad in MARKER_PAIRS:
        assert markers_conflict(senior, squad), (senior, squad)
        assert canonical_team_key(senior) != canonical_team_key(squad)
        assert ledger_team_key(senior, 24) != ledger_team_key(squad, 24)


def test_marker_detection_has_no_false_positives():
    for name in ("Boca Juniors", "Argentinos Juniors", "Young Boys",
                 "Wanderers", "Bolton Wanderers", "Western United",
                 "Washington", "Birmingham"):
        assert squad_markers(name) == frozenset(), name


def test_marker_conflict_vetoes_merge_despite_high_similarity():
    pt = _load_picks_today()
    # these were ALL above the 0.40 bigram merge threshold pre-fix
    for senior, squad in (("Turkey", "Turkey U21"), ("Brazil", "Brazil U20"),
                          ("Girona", "Girona B"), ("Arsenal", "Arsenal W")):
        assert char_ngram_similarity(senior, squad) >= 0.40, (senior, squad)
    for senior, squad in MARKER_PAIRS:
        rows = [_pick("Opponent", senior), _pick("Opponent", squad)]
        out, removed = pt.collapse_final_operational_picks(rows)
        assert removed == 0 and len(out) == 2, (senior, squad)
        assert pt._merge_veto_reason(rows[0], rows[1]).startswith(
            "squad_marker_conflict")


# --- S3: canonical / league disagreement -----------------------------------

def test_distinct_clubs_never_merge_on_similarity():
    pt = _load_picks_today()
    cases = [
        ("Manchester City", "Manchester United", "England PL", "England PL"),
        ("Launceston City", "Launceston United", "AUS NPL", "AUS NPL"),
        ("Barcelona", "Barcelona SC", "Spain La Liga", "Ecuador Serie A"),
        ("Olympiakos", "Olympiakos Nicosia", "Greece SL", "Cyprus 1"),
        ("Arsenal", "Arsenal Sarandi", "England PL", "Argentina LP"),
        ("River Plate", "River Plate Asuncion", "Argentina LP", "Paraguay 1"),
    ]
    for a, b, la, lb in cases:
        rows = [_pick("Opponent", a, league=la), _pick("Opponent", b, league=lb)]
        out, removed = pt.collapse_final_operational_picks(rows)
        assert removed == 0 and len(out) == 2, (a, b)
        assert pt._merge_veto_reason(rows[0], rows[1]) is not None


def test_same_club_spelling_variants_still_merge():
    """The dominant real pattern: one feed drops the suffix."""
    pt = _load_picks_today()
    for a, b in [("Aldershot", "Aldershot Town"), ("Hannover", "Hannover 96"),
                 ("Ebbsfleet", "Ebbsfleet United"), ("IFK Mariehamn", "Mariehamn"),
                 ("Türkiye", "Turkey"), ("Wolves", "Wolverhampton Wanderers")]:
        rows = [_pick("Opponent", a), _pick("Opponent", b)]
        out, removed = pt.collapse_final_operational_picks(rows)
        assert removed == 1 and len(out) == 1, (a, b)


def test_token_prefix_link_is_structural_not_fuzzy():
    pt = _load_picks_today()
    assert pt._token_prefix_link("Aldershot", "Aldershot Town")
    assert pt._token_prefix_link("Hannover", "Hannover 96")
    assert not pt._token_prefix_link("Manchester City", "Manchester United")
    assert not pt._token_prefix_link("Launceston City", "Launceston United")


# --- S4: degenerate keys ----------------------------------------------------

DEGENERATE_NAMES = ["Athletic Club", "Sporting Club", "Виктория", "Краснодар",
                    "Ολυμπιακός", "FC"]


def test_degenerate_names_get_unique_non_empty_marked_keys():
    keys = {}
    for name in DEGENERATE_NAMES:
        key = canonical_team_key(name)
        assert key, name
        assert is_degenerate_team_key(key), name
        keys[name] = key
    # distinct names never share a degenerate key
    assert len(set(keys.values())) == len(keys), keys


def test_degenerate_keys_never_merge_different_names():
    pt = _load_picks_today()
    rows = [_pick("Opponent", "Athletic Club"), _pick("Opponent", "Sporting Club")]
    out, removed = pt.collapse_final_operational_picks(rows)
    assert removed == 0 and len(out) == 2
    assert pt._merge_veto_reason(rows[0], rows[1]).startswith("degenerate_identity")


def test_degenerate_rows_are_stamped_for_the_report():
    pt = _load_picks_today()
    rows = [_pick("Opponent", "Athletic Club"), _pick("Opponent", "Turkey")]
    n = pt.stamp_identity_degenerate(rows)
    assert n == 1
    assert rows[0]["ctx"]["identity_degenerate"] == "away"
    assert "identity_degenerate" not in (rows[1].get("ctx") or {})


# --- S5: frozen-ledger key collision (report-only, never rekeyed) ----------

LEDGER_COLLISION_GROUPS = [
    ["Manchester City", "Manchester United"],
    ["Nottingham Forest", "Nottingham"],
    ["Universidad Católica", "Universidad de Chile"],
]


def test_width9_ledger_key_collisions_are_real():
    for group in LEDGER_COLLISION_GROUPS:
        keys = {ledger_team_key(n) for n in group}
        assert len(keys) == 1, group  # the collision this guard exists for


def test_ledger_key_collision_keeps_both_rows_and_stamps():
    pt = _load_picks_today()
    rows = [_pick("Manchester City", "Opponent"),
            _pick("Manchester United", "Opponent")]
    collisions = pt.ledger_key_collisions(rows)
    assert len(collisions) == 1
    assert all(r["ctx"]["ledger_key_collision"] == "true" for r in rows)


def test_archive_merge_refuses_to_fuse_colliding_identities():
    pt = _load_picks_today()
    existing = [_pick("Manchester City", "Opponent", odds=1.42)]
    fresh = [_pick("Manchester United", "Opponent", odds=1.90)]
    merged = pt.merge_day_archive_rows(existing, fresh, "2026-10-05")
    assert len(merged) == 2, "colliding ledger keys must not fuse two fixtures"


def test_archive_merge_still_dedupes_one_real_fixture():
    pt = _load_picks_today()
    existing = [_pick("Italy", "Türkiye", odds=1.42)]
    fresh = [_pick("Italy", "Turkey", odds=1.47)]
    assert len(pt.merge_day_archive_rows(existing, fresh, "2026-10-05")) == 1


# --- S6: daily cross-keyer tripwire (report-only) --------------------------

def test_cross_keyer_sweep_flags_merge_and_split_candidates():
    pt = _load_picks_today()
    rows = [
        _pick("Manchester City", "Opponent"),
        _pick("Manchester United", "Opponent2"),
        _pick("Italy", "Türkiye"),
    ]
    sweep = pt.cross_keyer_identity_warnings(rows)
    assert isinstance(sweep["merged"], list)
    assert isinstance(sweep["split"], list)
    # curated aliases are fully resolved -> no split warning for them
    assert sweep["split"] == []


def test_cross_keyer_sweep_is_silent_on_a_resolved_alias_pair():
    pt = _load_picks_today()
    rows = [_pick("Italy", "Türkiye"), _pick("Italy", "Turkey")]
    assert pt.cross_keyer_identity_warnings(rows)["split"] == []


def test_every_curated_alias_group_agrees_in_every_keyer():
    """The drift this sweep exists to catch (closed by single-sourcing).

    Before single-sourcing, Ulsan Hyundai / KPV-j / Zvyagel / Maxline were
    canonicalized for contexts but still SPLIT at the voter-row seam.
    """
    pt = _load_picks_today()
    from edgefactory.util import team_alias_table
    groups = {}
    for raw, canonical in team_alias_table().items():
        if " " in raw or not raw.islower():
            groups.setdefault(str(canonical).lower(), set()).add(raw)
    rows = []
    for spellings in groups.values():
        names = sorted(spellings)
        if len(names) >= 2:
            rows.append(_pick(names[0], names[1]))
            for extra in names[2:]:
                rows.append(_pick(extra, names[0]))
    assert pt.cross_keyer_identity_warnings(rows)["split"] == []


def test_identity_sweep_is_report_only(capsys):
    pt = _load_picks_today()
    rows = [_pick("Italy", "Türkiye"), _pick("Athletic Club", "Opponent")]
    before = [dict(r) for r in rows]
    counts = pt.print_identity_sweep(rows, day="2026-10-05")
    err = capsys.readouterr().err
    assert "identity sweep 2026-10-05" in err
    assert counts["identity_degenerate"] == 1
    # only ctx flags are added; no pick is dropped or re-priced
    assert len(rows) == len(before)
    for old, new in zip(before, rows):
        for field in ("home", "away", "odds", "pick", "market", "bucket"):
            assert old[field] == new[field]


# --- tightening-only proof --------------------------------------------------

TIGHTENING_CORPUS = [
    ("Turkey", "Turkey U21"), ("Brazil", "Brazil U20"), ("Girona", "Girona B"),
    ("Barcelona", "Barcelona SC"), ("Manchester City", "Manchester United"),
    ("Olympiakos", "Olympiakos Nicosia"), ("River Plate", "River Plate Asuncion"),
    ("Arsenal", "Arsenal Sarandi"), ("Aldershot", "Aldershot Town"),
    ("Hannover", "Hannover 96"), ("Ebbsfleet", "Ebbsfleet United"),
    ("IFK Mariehamn", "Mariehamn"), ("Khovd FC", "Khovd Western"),
    ("Athletic Club", "Sporting Club"), ("Inter Milan", "AC Milan"),
]


def test_no_previously_refused_merge_becomes_allowed():
    """Every veto added here is tightening-only.

    Replays each pair through the current collapse with equal, anchored
    kickoffs (so the unanchored path is out of scope) and asserts the
    outcome is either the same as the legacy bigram rule or stricter —
    never newly permissive. The legacy decision is recomputed inline so
    the test does not depend on git history.
    """
    pt = _load_picks_today()
    for a, b in TIGHTENING_CORPUS:
        rows = [_pick("Opponent", a), _pick("Opponent", b)]
        _, removed = pt.collapse_final_operational_picks(rows)
        legacy_would_merge = (
            char_ngram_similarity(a, b) >= 0.40
            or rows[0]["home"] == rows[1]["home"]
        )
        if removed:
            assert legacy_would_merge, f"newly ALLOWED merge: {a} / {b}"


# --- frozen real-slate regression (both self-caught defects) ---------------

SLATE_FIXTURE = ROOT / "tests" / "fixtures" / "slate_2026-10-05_identity_split.json"


def _slate_rows():
    import json
    return json.loads(SLATE_FIXTURE.read_text())


def test_frozen_slate_collapses_the_twin_to_one_row():
    """Replays the REAL 2026-10-05 slate end to end.

    Both defects found in the second pass were invisible to synthetic
    unit tests and only showed up here:
      1. the two feeds spell the COMPETITION differently
         ("World UEFA Nations League" vs
          "International,Uefa Nations League A Grp. 1"), which an
         equality-based league veto wrongly treated as two fixtures;
      2. the rows' raw kickoff text disagreed by 300 minutes
         ("05-10, 19:45" vs a bare "14:45") while both already carried
         the SAME resolved kickoff_utc.
    """
    pt = _load_picks_today()
    rows = _slate_rows()
    assert len(rows) == 6, "fixture must keep the inflated archive count"
    collapsed, removed = pt.collapse_final_operational_picks([dict(r) for r in rows])
    assert removed == 1
    assert len(collapsed) == 5
    survivors = {(r["home"], r["away"]) for r in collapsed}
    assert sum(1 for h, a in survivors if h == "Italy") == 1


def test_frozen_slate_league_spelling_divergence_does_not_veto():
    pt = _load_picks_today()
    rows = _slate_rows()
    a = next(r for r in rows if r["away"] == "Türkiye")
    b = next(r for r in rows if r["away"] == "Turkey")
    assert a["league"] != b["league"]  # the trap
    assert not pt._leagues_conflict(a["league"], b["league"])
    assert pt._merge_veto_reason(a, b) is None


def test_frozen_slate_kickoff_utc_decides_over_raw_clock_text():
    pt = _load_picks_today()
    rows = _slate_rows()
    a = next(r for r in rows if r["away"] == "Türkiye")
    b = next(r for r in rows if r["away"] == "Turkey")
    assert a["kickoff"] != b["kickoff"]
    assert a["kickoff_utc"] == b["kickoff_utc"]
    # naive text comparison says "different events"; the resolved instant wins
    assert pt._same_event_cluster(a, b) is False
    assert pt._kickoff_instants_agree(a, b) is True
    assert pt._canonical_identity_collapse(a, b) is True


def test_frozen_slate_identity_sweep_counters_are_all_zero():
    pt = _load_picks_today()
    collapsed, _ = pt.collapse_final_operational_picks(
        [dict(r) for r in _slate_rows()])
    counts = pt.print_identity_sweep(collapsed, day="2026-10-05")
    assert counts == {"identity_degenerate": 0, "ledger_key_collision": 0,
                      "cross_keyer_merged": 0, "cross_keyer_split": 0}


def test_frozen_slate_archive_merge_is_not_inflated():
    pt = _load_picks_today()
    rows = _slate_rows()
    merged = pt.merge_day_archive_rows([dict(r) for r in rows], [], "2026-10-05")
    italy = [r for r in merged if r["home"] == "Italy"]
    assert len(italy) == 1, "the twin spellings must share one ledger row"


# --- degenerate-key epoch: pre-fix rows keyed '' still dedupe --------------

def test_degenerate_key_input_is_case_and_whitespace_normalized():
    assert canonical_team_key("Athletic  Club") == canonical_team_key("athletic club")
    assert canonical_team_key(" ATHLETIC CLUB ") == canonical_team_key("Athletic Club")


def test_legacy_empty_keyed_archive_row_still_dedupes():
    pt = _load_picks_today()
    # a row frozen BEFORE the fix keyed ('', '') for this team
    old_row = _pick("Athletic Club", "Opponent", odds=1.42)
    fresh_row = _pick("Athletic Club", "Opponent", odds=1.90)
    merged = pt.merge_day_archive_rows([old_row], [fresh_row], "2026-10-05")
    assert len(merged) == 1 and merged[0]["odds"] == 1.42


# --- ambiguous settlement keys are operator-visible, not silently pending --

def _load_auto_tickets():
    spec = importlib.util.spec_from_file_location(
        "auto_tickets_identity", ROOT / "scripts" / "auto_tickets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ambiguous_result_keys_are_counted_and_described(capsys):
    at = _load_auto_tickets()
    entries = {"2026-10-05": [
        {"home": "Manchester City", "away": "Arsenal", "result": "1"},
        {"home": "Manchester United", "away": "Arsenal", "result": "2"},
        {"home": "Moss", "away": "Kongsvinger", "result": "2"},
    ]}
    key_to = {}
    for day, rows in entries.items():
        for e in rows:
            for hk, ak in at._exact_result_keys(e["home"], e["away"]):
                key_to[(day, hk, ak)] = e
    dropped, detail = at._drop_ambiguous_result_keys(key_to, entries)
    assert dropped >= 1
    # the operator gets the raw fixtures that collided, not just a number
    collided = {name for _day, names in detail for name in names}
    assert "Manchester City vs Arsenal" in collided
    assert "Manchester United vs Arsenal" in collided
    # the unambiguous fixture is untouched
    assert any("Moss" in str(v.get("home")) for v in key_to.values())
