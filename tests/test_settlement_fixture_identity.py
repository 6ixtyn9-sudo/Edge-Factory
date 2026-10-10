"""A leg must not be lost because the fixture was respelled (WO-6).

Italy beat Türkiye on 2026-10-05. The acca never settled. The archive files
the fixture under "Türkiye"; the frozen slip says "Turkey":

    archive key : ('2026-10-05', 'italy', 'turkiye', 'HOME')
    slip key    : ('2026-10-05', 'italy', 'turkey',  'HOME')

Structure-stripping folds spelling. It cannot fold a RENAME: these are two
different words for one country. The curated exonym table in
edgefactory.identity already carried the pair - the settlement key simply
was not consulting it, because it called the alias-free base fold.

The deeper fault is architectural. The slip stored the fixture as free text
and settlement re-derived the lookup key by splitting that sentence apart
later, so ANY respelling between freeze and settlement orphaned the leg
permanently. Runs do rewrite archive rows during the day ("superseded 11
archived row(s) with fresh picks"), so the window is real. A slip now
carries a stable identifier captured at freeze time; the text path remains
as a fallback so slips frozen before the field existed still settle.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402


@pytest.fixture(autouse=True)
def _sandbox_state(tmp_path, monkeypatch):
    """settle_open_slips calls save_state internally -- never let a test
    touch the real localdata/auto_tickets_state.json."""
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    monkeypatch.setattr(at, "BUCKET_PNL_FILE", tmp_path / "bucket.json")


@pytest.fixture(autouse=True)
def settlement_clock(monkeypatch):
    """Identity controls run before expiry, independently of the CI date."""
    class Clock(datetime):
        instant = datetime(2026, 10, 6, 12, tzinfo=at.TZ)

        @classmethod
        def now(cls, tz=None):
            return cls.instant.astimezone(tz) if tz else cls.instant.replace(tzinfo=None)

    monkeypatch.setattr(at, "datetime", Clock)
    return Clock


# --- the rename is resolved -----------------------------------------------


def test_the_two_spellings_produce_one_key():
    archive = at._folded_leg_key("2026-10-05", "Italy", "Türkiye", "home")
    slip = at._folded_leg_key("2026-10-05", "Italy", "Turkey", "HOME")
    assert archive == slip == ("2026-10-05", "italy", "turkey", "HOME")


def test_the_alias_comes_from_the_curated_table_not_a_guess():
    """No new names are introduced here; the exonym pair already existed."""
    from edgefactory.identity import TEAM_KEY_ALIASES
    assert TEAM_KEY_ALIASES.get("turkiye") == "turkey"


def test_distinct_fixtures_still_produce_distinct_keys():
    """Alias resolution must unify a rename, never merge two real teams."""
    keys = {
        at._folded_leg_key("2026-10-05", "Italy", "Türkiye", "HOME"),
        at._folded_leg_key("2026-10-05", "Italy", "Turkmenistan", "HOME"),
        at._folded_leg_key("2026-10-05", "Italy", "Türkiye", "AWAY"),
        at._folded_leg_key("2026-10-06", "Italy", "Türkiye", "HOME"),
        at._folded_leg_key("2026-10-05", "Turkey", "Italy", "HOME"),
    }
    assert len(keys) == 5


# --- a frozen identifier beats free text ----------------------------------


def test_stored_key_is_preferred_over_the_match_string():
    stable = at.leg_lookup_key("2026-10-05", {
        "match": "COMPLETELY WRONG vs TEXT",
        "fixture_key": ("2026-10-05", "italy", "turkiye"), "pick": "HOME"})
    parsed = at.leg_lookup_key("2026-10-05", {
        "match": "Italy vs Türkiye", "pick": "HOME"})
    assert stable == parsed == ("2026-10-05", "italy", "turkey", "HOME")


def test_legacy_slip_without_a_stored_key_still_settles():
    """Slips frozen before the field existed must not be orphaned by the
    very change that stops future orphans."""
    assert at.leg_lookup_key("2026-10-05", {
        "match": "Italy vs Turkey", "pick": "HOME"}
    ) == ("2026-10-05", "italy", "turkey", "HOME")


def test_stored_key_as_a_list_survives_a_json_round_trip():
    """State is JSON: a tuple comes back as a list."""
    assert at.leg_lookup_key("2026-10-05", {
        "match": "x vs y", "fixture_key": ["2026-10-05", "Italy", "Türkiye"],
        "pick": "HOME"}) == ("2026-10-05", "italy", "turkey", "HOME")


@pytest.mark.parametrize("leg", [
    {"match": "no separator here", "pick": "HOME"},
    {"match": "", "pick": "HOME"},
    {"pick": "HOME"},
])
def test_unusable_leg_yields_no_key_rather_than_a_wrong_one(leg):
    """None means 'not found', and the existing void timer applies. Inventing
    a key would silently grade the leg against the wrong fixture."""
    assert at.leg_lookup_key("2026-10-05", leg) is None


def test_empty_stored_key_falls_back_to_the_text():
    assert at.leg_lookup_key("2026-10-05", {
        "match": "Italy vs Türkiye", "fixture_key": ["2026-10-05", "", ""],
        "pick": "HOME"}) == ("2026-10-05", "italy", "turkey", "HOME")


# --- identity is frozen with the slip -------------------------------------


def test_freeze_stamps_the_identity_from_the_archive_row():
    plan = [{"legs": [{"match": "Italy vs Turkey", "pick": "HOME",
                       "row": {"home": "Italy", "away": "Türkiye",
                               "date": "2026-10-05"}}]}]
    at._stamp_fixture_keys(plan, "2026-10-05")
    assert plan[0]["legs"][0]["fixture_key"] == ["2026-10-05", "Italy", "Türkiye"]


def test_freeze_falls_back_to_the_printed_text():
    plan = [{"legs": [{"match": "Italy vs Türkiye", "pick": "HOME"}]}]
    at._stamp_fixture_keys(plan, "2026-10-05")
    assert plan[0]["legs"][0]["fixture_key"] == ["2026-10-05", "Italy", "Türkiye"]


def test_freeze_never_rewrites_the_displayed_text():
    """Display text is the audit's provenance and stays exactly as printed."""
    plan = [{"legs": [{"match": "Italy vs Turkey", "pick": "HOME",
                       "row": {"home": "Italy", "away": "Türkiye"}}]}]
    at._stamp_fixture_keys(plan, "2026-10-05")
    assert plan[0]["legs"][0]["match"] == "Italy vs Turkey"


def test_freeze_does_not_overwrite_an_existing_identity():
    plan = [{"legs": [{"match": "a vs b", "pick": "HOME",
                       "fixture_key": ["2026-10-05", "italy", "turkiye"],
                       "row": {"home": "Other", "away": "Team"}}]}]
    at._stamp_fixture_keys(plan, "2026-10-05")
    assert plan[0]["legs"][0]["fixture_key"] == ["2026-10-05", "italy", "turkiye"]


# --- end to end: the stuck acca settles -----------------------------------


def _archive_row(home, away, pick, date="2026-10-05"):
    return {"date": date, "home": home, "away": away, "pick": pick,
            "avg_p": 64.0, "odds": 1.47}


def test_the_stuck_italy_turkiye_acca_settles(monkeypatch):
    """The real slip shape: text says Turkey, archive says Türkiye."""
    st = {"bank": 167.1157, "base_pct": 10.0, "cycle_base": 10.0,
          "history": [], "events": [],
          "open_slips": [{"date": "2026-10-05", "staked_pct": 20.8895, "accas": [{
              "odds": 2.57, "stake_pct": 20.8895, "results": [None, "win"],
              "won": None,
              "legs": [{"match": "Italy vs Turkey", "pick": "HOME",
                        "prob": 0.64, "odds": 1.47, "result": None},
                       {"match": "Moss vs Kongsvinger", "pick": "AWAY",
                        "prob": 0.62, "odds": 1.75, "result": None}]}]}]}
    archives = [_archive_row("Italy", "Türkiye", "home"),
                _archive_row("Moss", "Kongsvinger", "away")]
    settled = {("2026-10-05", "italy", "turkiye"): "home",
               ("2026-10-05", "moss", "kongsvinger"): "away"}
    monkeypatch.setattr(at, "pick_result", lambda p, s: "win")

    lines = at.settle_open_slips(st, settled, archives=archives,
                                 entries_by_date={})
    assert st["open_slips"] == [], f"leg still orphaned: {lines}"
    assert st["history"], "nothing was booked"
    assert st["history"][-1]["accas"][0]["won"] is True


def test_an_unrelated_fixture_is_not_grabbed_by_the_alias(monkeypatch):
    """The acca must stay open when the archive genuinely lacks the leg."""
    st = {"bank": 100.0, "base_pct": 10.0, "cycle_base": 10.0,
          "history": [], "events": [],
          "open_slips": [{"date": "2026-10-05", "staked_pct": 10.0, "accas": [{
              "odds": 1.47, "stake_pct": 10.0, "results": [None], "won": None,
              "legs": [{"match": "Italy vs Türkiye", "pick": "HOME",
                        "prob": 0.64, "odds": 1.47, "result": None}]}]}]}
    archives = [_archive_row("Italy", "Turkmenistan", "home")]
    def reject_unrelated_grading(*args):
        pytest.fail("unrelated archive fixture reached pick_result")

    monkeypatch.setattr(at, "pick_result", reject_unrelated_grading)

    at.settle_open_slips(st, {}, archives=archives, entries_by_date={})
    assert st["open_slips"], "a different fixture was matched by mistake"
    assert st["open_slips"][0]["accas"][0]["results"] == [None]
    assert st["bank"] == 100.0
    assert st["history"] == []


@pytest.mark.parametrize("offset,expires", [
    (timedelta(days=5) - timedelta(seconds=1), False),
    (timedelta(days=5), True),
    (timedelta(days=6), True),
])
def test_unmatched_fixture_expiry_is_not_an_alias_match(
        monkeypatch, settlement_clock, offset, expires):
    """Missing evidence ages to void, never to the unrelated donor's win."""
    settlement_clock.instant = datetime(2026, 10, 5, tzinfo=at.TZ) + offset
    st = {"bank": 100.0, "base_pct": 10.0, "cycle_base": 10.0,
          "history": [], "events": [],
          "open_slips": [{"date": "2026-10-05", "staked_pct": 10.0, "accas": [{
              "odds": 1.47, "stake_pct": 10.0, "results": [None], "won": None,
              "legs": [{"match": "Italy vs Türkiye", "pick": "HOME",
                        "prob": 0.64, "odds": 1.47, "result": None}]}]}]}

    def reject_unrelated_grading(*args):
        pytest.fail("unrelated archive fixture reached pick_result")

    monkeypatch.setattr(at, "pick_result", reject_unrelated_grading)
    lines = at.settle_open_slips(st, {}, archives=[
        _archive_row("Italy", "Turkmenistan", "home")], entries_by_date={})
    if expires:
        assert st["open_slips"] == []
        acca = st["history"][-1]["accas"][0]
        assert any("legs=['void']" in line for line in lines)
        assert st["history"][-1]["returned_pct"] == 10.0
        assert acca["odds"] == 1.0
    else:
        assert st["open_slips"][0]["accas"][0]["results"] == [None]
        assert st["history"] == []
    assert st["bank"] == 100.0
