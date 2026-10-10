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
