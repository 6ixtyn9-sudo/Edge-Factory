"""Same-fixture guard: one match must never ride a card twice.

Regression for 2026-10-13: the picks output carried "Inter vs Club Brugge KV"
and "Inter vs Club Brugge" for one match, and the guard's key did not treat the
two spellings as one fixture. Distinct squads (Arsenal / Arsenal W) must stay
distinct.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402


def _leg(home, away, date="2026-10-13", prob=0.75, odds=1.25):
    return {"match": f"{home} vs {away}", "pick": "HOME", "prob": prob,
            "odds": odds, "row": {"home": home, "away": away, "date": date}}


def test_kv_suffix_spelling_is_the_same_fixture():
    a = _leg("Inter", "Club Brugge KV", prob=0.751)
    b = _leg("Inter", "Club Brugge", prob=0.73)
    kept, dropped = at.dedup_fixture_legs([a, b])
    assert kept == [a]
    assert dropped == [b]


def test_club_and_structure_tokens_do_not_split_a_fixture():
    a = _leg("FC Porto", "Benfica")
    b = _leg("Porto", "Benfica")
    kept, dropped = at.dedup_fixture_legs([a, b])
    assert len(kept) == 1 and len(dropped) == 1


def test_distinct_squads_stay_distinct():
    a = _leg("Arsenal", "Lille")
    b = _leg("Arsenal W", "Lille W")
    kept, dropped = at.dedup_fixture_legs([a, b])
    assert len(kept) == 2 and dropped == []


def test_fc_porto_and_fc_porto_b_stay_distinct():
    a = _leg("FC Porto", "Benfica")
    b = _leg("FC Porto B", "Benfica")
    kept, dropped = at.dedup_fixture_legs([a, b])
    assert len(kept) == 2 and dropped == []


def test_same_teams_on_another_day_are_not_a_duplicate():
    a = _leg("Inter", "Club Brugge KV", date="2026-10-13")
    b = _leg("Inter", "Club Brugge KV", date="2026-10-20")
    kept, dropped = at.dedup_fixture_legs([a, b])
    assert len(kept) == 2 and dropped == []


def test_a_name_made_only_of_structure_tokens_is_kept_not_emptied():
    assert at._fixture_fold("FC") != ""
    assert at._fixture_fold("KV") != ""
