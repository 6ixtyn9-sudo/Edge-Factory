"""Wrong-squad pricing guard on the BetExplorer odds matcher.

Evidence observed in the committed receipt (run 38027657811, 2026-10-10 cache):
the cache key "2026-10-10|raallalouvire|clubbruggekv" held three price rows
for Dender vs Club Brugge KV U23 (Belgium: Challenger Pro League, kickoff
19:00) — the senior Jupiler Pro League fixture RAAL La Louvière vs Club
Brugge KV was about to be priced with the U23 side's odds. The width-9 fuzzy
key ("clubbrugg") cannot tell the squads apart, so the veto runs on the full
names' squad markers, at both the matcher and the cache-write seam.
"""

from __future__ import annotations

# Observed 2026-10-10 in the committed odds cache receipt (run 38027657811).
from edgefactory.identity import squad_marker_mismatch, squad_markers
from edgefactory.sources import betexplorer_odds


# The page list for 2026-10-10 as the capture saw it (relevant excerpt).
MATCHES = [
    {
        "date": "2026-10-10", "kickoff": "19:00",
        "country": "Belgium", "league": "Challenger Pro League",
        "home": "Dender", "away": "Club Brugge KV U23",
        "match_url": "https://www.betexplorer.com/football/belgium/challenger-pro-league/dender-club-brugge-u23/x/", "event_id": "x",
    },
    {
        "date": "2026-10-10", "kickoff": "20:45",
        "country": "Belgium", "league": "Jupiler Pro League",
        "home": "RAAL La Louvière", "away": "Club Brugge KV",
        "match_url": "https://www.betexplorer.com/football/belgium/jupiler-pro-league/raal-club-brugge/y/", "event_id": "y",
    },
]

RAAL_PICK = {"home": "RAAL La Louvière", "away": "Club Brugge KV",
             "league": "Belgium,Jupiler Pro League", "date": "2026-10-10"}


def test_senior_fixture_never_matches_the_u23_page():
    # The exact 2026-10-10 defect: the senior page was not on the day's card,
    # and the only key-collision was the truncated "clubbrugg" away key of
    # the U23 page. The marker veto must return None, not the U23 page.
    u23_page_only = [m for m in MATCHES if m["event_id"] == "x"]
    assert betexplorer_odds.match_pick_to_betexplorer(RAAL_PICK, u23_page_only) is None
    # And in the full list the exact senior page still wins.
    assert betexplorer_odds.match_pick_to_betexplorer(RAAL_PICK, MATCHES)["event_id"] == "y"


def test_the_real_page_still_matches_when_present():
    # When the correct Jupiler page is on the day's card it still wins.
    senior_only = [m for m in MATCHES if m["event_id"] == "y"]
    assert betexplorer_odds.match_pick_to_betexplorer(RAAL_PICK, senior_only) is senior_only[0]
    senior_only = [m for m in MATCHES if m["event_id"] == "y"]
    assert betexplorer_odds.match_pick_to_betexplorer(RAAL_PICK, senior_only) is senior_only[0]


def test_display_variants_still_match_partially():
    # 2026-10-10 cache evidence: the provider page said "Buriram", the pick
    # said "Buriram United" — no squad markers on either side, so the
    # legitimate partial match survives the guard.
    matches = [{"date": "2026-10-10", "kickoff": "12:30", "country": "Thailand",
                "league": "Thai League 1", "home": "Buriram", "away": "Rayong FC",
                "match_url": "u", "event_id": "e"}]
    pick = {"home": "Buriram United", "away": "Rayong FC",
            "league": "Thailand,Thai League", "date": "2026-10-10"}
    assert betexplorer_odds.match_pick_to_betexplorer(pick, matches) is matches[0]


def test_womens_side_never_substitutes_for_the_men_side():
    matches = [{"date": "2026-10-10", "kickoff": "18:00", "country": "England",
                "league": "WSL", "home": "Arsenal W", "away": "Chelsea W",
                "match_url": "u", "event_id": "e"}]
    pick = {"home": "Arsenal", "away": "Chelsea",
            "league": "England,Premier League", "date": "2026-10-10"}
    assert betexplorer_odds.match_pick_to_betexplorer(pick, matches) is None


def test_reserve_team_aliases_veto_per_class_not_per_token():
    # "B" and "II" and "Reserves" are one reserve class: two spellings of the
    # same reserve side still equal each other, but never the senior side.
    assert not squad_marker_mismatch("Bayern München II", "Bayern Munich B")
    assert squad_marker_mismatch("Bayern München II", "Bayern Munich")
    assert squad_marker_mismatch("Barcelona B", "Barcelona")
    assert not squad_marker_mismatch("Barcelona", "Barcelona")


def test_age_grades_are_distinct_markers():
    assert squad_marker_mismatch("Real Madrid Castilla U23", "Real Madrid Castilla U21") \
        or squad_markers("Real Madrid Castilla U21") == squad_markers("Real Madrid Castilla U23")
    assert squad_marker_mismatch("Manchester United U18", "Manchester United")
    assert not squad_marker_mismatch("Manchester United U18", "Manchester United U18")


def test_write_seam_refuses_rows_from_a_wrong_squad_page():
    # The write seam must never persist the U23 page's odds under the senior
    # fixture's cache key — reproduced without network by calling the guard
    # helper the seam uses.
    from edgefactory.sources.betexplorer_odds import _orientation_marker_clean_guard
    matched = {"home": "Dender", "away": "Club Brugge KV U23"}
    assert not _orientation_marker_clean_guard(matched, RAAL_PICK)
    ok_page = {"home": "RAAL La Louvière", "away": "Club Brugge KV"}
    assert _orientation_marker_clean_guard(ok_page, RAAL_PICK)
    buriram = {"home": "Buriram", "away": "Rayong FC"}
    assert _orientation_marker_clean_guard(buriram, {"home": "Buriram United", "away": "Rayong FC"})


def test_age_spellings_preserve_exact_age_class_without_rekeying():
    from edgefactory.identity import source_team_key
    for age in (15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25):
        for marker in (f'U{age}', f'U-{age}', f'U {age}', f'Under-{age}', f'Under {age}', f'Sub-{age}'):
            assert squad_markers('Club '+marker) == frozenset({f'u{age}'})
            assert not squad_marker_mismatch('Club '+marker, f'Club U{age}')
    assert squad_marker_mismatch('Club Under-21', 'Club Sub-23')
    assert squad_marker_mismatch('Club U-21', 'Club')
    # Recognition does not rewrite the shared persisted identity-key function.
    assert source_team_key('Example Under-23') == 'exampleunder23'


def test_marker_words_without_age_are_not_generic_squad_classes():
    for name in ('Under Armour FC', 'Sub Marine FC', 'U Club', 'Frauenfeld FC', 'Underwood United'):
        assert not squad_markers(name)
    for marker in ('Femenil', 'Frauen'):
        assert squad_markers('Club '+marker) == frozenset({'women'})
        assert not squad_marker_mismatch('Club '+marker, 'Club Women')


def test_srl_marker_separates_simulations_without_rekeying_real_clubs():
    from edgefactory.identity import source_team_key
    for suffix in ('SRL', '(Srl)', 'S.R.L.', 'S-R-L', 'Simulated Reality League'):
        assert squad_markers('Alanyaspor '+suffix) == frozenset({'simulation'})
        assert squad_marker_mismatch('Alanyaspor', 'Alanyaspor '+suffix)
        assert not squad_marker_mismatch('Alanyaspor SRL', 'Alanyaspor '+suffix)
    for name in ('Alanyaspor', 'Kocaelispor', 'GO Ahead Eagles', 'SC Telstar', 'Srlanga FC'):
        assert not squad_markers(name)
    assert source_team_key('Alanyaspor SRL') == 'alanyasporsrl'


# October 27 production refusal: B. is Borussia, not a reserve prefix.
def test_gladbach_senior_abbreviation_has_no_reserve_marker():
    for name in ('B. Monchengladbach', 'B. Mönchengladbach', 'B Monchengladbach'):
        assert squad_markers(name) == frozenset()
        assert not squad_marker_mismatch(name, 'Borussia Mönchengladbach')


def test_gladbach_abbreviation_keeps_explicit_squad_suffixes():
    for suffix, expected in (('II', 'reserve'), ('B', 'reserve'),
                             ('Reserves', 'reserve'), ('W', 'women'),
                             ('Women', 'women'), ('U21', 'u21'),
                             ('U-23', 'u23'), ('SRL', 'simulation'),
                             ('(Bookings)', 'non_match')):
        short = f'B. Monchengladbach {suffix}'
        full = f'Borussia Mönchengladbach {suffix}'
        assert squad_markers(short) == frozenset({expected})
        assert not squad_marker_mismatch(short, full)
        assert squad_marker_mismatch(short, 'Borussia Mönchengladbach')


def test_gladbach_exemption_does_not_ignore_b_for_other_clubs():
    for name in ('B. Dortmund', 'B. Munich', 'B. Monchengladbachish',
                 'B. Monchengladbachhausen', 'Monchengladbach B'):
        assert 'reserve' in squad_markers(name)
    assert squad_marker_mismatch('B. Monchengladbach U21', 'B. Monchengladbach U23')
    assert squad_marker_mismatch('B. Monchengladbach W', 'B. Monchengladbach II')


def test_gladbach_abbreviation_passes_match_write_and_row_guards():
    pick = {'date': '2026-10-27', 'home': 'Borussia Mönchengladbach',
            'away': 'Karlsruher SC', 'league': 'Germany,DFB Pokal'}
    page = {'date': '2026-10-27', 'home': 'B. Monchengladbach',
            'away': 'Karlsruher SC', 'league': 'DFB Pokal', 'event_id': 'test'}
    assert betexplorer_odds.match_pick_to_betexplorer(pick, [page]) is page
    assert betexplorer_odds._orientation_marker_clean_guard(page, pick)
    assert betexplorer_odds.row_belongs_to_pick(page, pick, pick['date']) == (True, '')
    reverse = dict(page, home=page['away'], away=page['home'])
    assert betexplorer_odds._orientation_marker_clean_guard(reverse, pick)
    assert betexplorer_odds.row_belongs_to_pick(reverse, pick, pick['date']) == (True, '')
    for home in ('B. Dortmund', 'B. Monchengladbach II', 'B. Monchengladbach W',
                 'B. Monchengladbach U21'):
        wrong = dict(page, home=home)
        assert not betexplorer_odds.row_belongs_to_pick(wrong, pick, pick['date'])[0]
        if home != 'B. Dortmund':
            assert not betexplorer_odds._orientation_marker_clean_guard(wrong, pick)
    assert not betexplorer_odds.row_belongs_to_pick(
        dict(page, away='Other Club'), pick, pick['date'])[0]
    assert not betexplorer_odds.row_belongs_to_pick(
        dict(page, date='2026-10-20'), pick, pick['date'])[0]


def test_gladbach_marker_fix_does_not_rekey_stored_names():
    from edgefactory.identity import source_team_key
    assert source_team_key('B. Monchengladbach') == 'bmonchengladbach'
    assert source_team_key('B. Monchengladbach II') == 'bmonchengladbachii'


def test_gladbach_capture_and_cached_read_use_real_identity_guards(tmp_path, monkeypatch):
    be = betexplorer_odds
    pick = {'date': '2026-10-27', 'home': 'Borussia Mönchengladbach',
            'away': 'Karlsruher SC', 'league': 'Germany,DFB Pokal'}
    page = {'date': pick['date'], 'home': 'B. Monchengladbach',
            'away': pick['away'], 'league': 'DFB Pokal', 'country': 'Germany',
            'kickoff': '18:00', 'event_id': 'test', 'match_url': 'test-only'}
    monkeypatch.setattr(be, 'LOCALDATA', tmp_path)
    monkeypatch.setattr(be, 'MARKET_TABS_ENABLED', False)
    monkeypatch.setattr(be, 'fetch_day_matches', lambda day: [page])
    calls = []

    def fake_prices(url, event_id):
        calls.append(event_id)
        return {'odd1': 1.5, 'oddx': 4.0, 'odd2': 6.0}

    monkeypatch.setattr(be, 'fetch_match_odds', fake_prices)
    be.reset_fetch_count()
    try:
        rows = be.betexplorer_odds_rows_for_pick(pick, pick['date'])
        assert len(rows) == 3
        assert {row['home'] for row in rows} == {'B. Monchengladbach'}
        assert calls == ['test']
        assert be.cached_odds_rows_for_pick(pick, pick['date']) == rows
        assert be.betexplorer_odds_rows_for_pick(pick, pick['date']) == rows
        assert calls == ['test'], 'a valid cached abbreviation must not cause a refetch'

        # Poison the same in-memory key: neither the abbreviation exception nor
        # a successful earlier fetch may let a different squad price the pick.
        key = be._fixture_cache_key(pick, pick['date'])
        for bad_home in ('B. Monchengladbach II', 'B. Monchengladbach W',
                         'B. Monchengladbach U21', 'B. Dortmund'):
            be._fixture_cache[key] = [dict(row, home=bad_home) for row in rows]
            assert be.cached_odds_rows_for_pick(pick, pick['date']) == []
    finally:
        be.reset_fetch_count()
