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

import json
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
    _frozen(st, "2026-10-05")
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
    _frozen(st, "2026-10-05")

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


# --- a key persisted before a WORD fold still resolves ---------------------


def test_a_key_stored_before_the_utd_fold_resolves_across_it():
    """A lane slip frozen before the 2026-10-12 fold stores the OLD key.

    ``enhancement_legs`` stamps ``fixture_key`` from ``_folded_leg_key``, so
    an enhancement leg carries glued seam keys, not display text - and
    re-folding a glued key cannot recover the current spelling (there is no
    separate ``utd`` token left to fold). The leg must still find its archive
    row: the primary key is the old spelling, the compatibility key is the
    current one, and the index is built with the current rule.
    """
    slip_date = "2026-10-05"
    leg = {"match": "Coventry vs Newcastle Utd", "pick": "AWAY", "market": "",
           "fixture_key": ["2026-10-05", "coventry", "newcastleutd", "AWAY"]}
    archive_key = at._folded_leg_key(slip_date, "Coventry", "Newcastle Utd", "AWAY")
    assert archive_key == ("2026-10-05", "coventry", "newcastleunited", "AWAY")

    primary = at.leg_lookup_key(slip_date, leg)
    assert primary == ("2026-10-05", "coventry", "newcastleutd", "AWAY")
    keys = at.leg_lookup_keys(slip_date, leg)
    assert keys[0] == primary and archive_key in keys[1:]
    index = {archive_key: {"home": "Coventry", "away": "Newcastle Utd"}}
    assert index.get(keys[0]) is None            # the old key alone misses
    assert next(index[k] for k in keys if k in index)["home"] == "Coventry"


def test_the_primary_key_stays_first_and_alone_when_nothing_moved():
    """A leg written after the fold, or one carrying raw spellings, gets the
    recomputed key and no extra candidates - settlement behaviour is
    unchanged wherever identity did not move."""
    raw = {"match": "Italy vs Turkey", "pick": "HOME",
           "fixture_key": ["2026-10-05", "Italy", "Türkiye"]}
    assert at.leg_lookup_keys("2026-10-05", raw) == [
        ("2026-10-05", "italy", "turkey", "HOME")]
    current = {"match": "Coventry vs Newcastle Utd", "pick": "AWAY",
               "fixture_key": ["2026-10-05", "coventry", "newcastleunited"]}
    assert at.leg_lookup_keys("2026-10-05", current) == [
        ("2026-10-05", "coventry", "newcastleunited", "AWAY")]


def test_a_leg_with_no_usable_identity_still_yields_no_keys():
    assert at.leg_lookup_keys("2026-10-05", {"pick": "HOME"}) == []
    assert at.leg_lookup_keys("2026-10-05", {"match": "no separator",
                                             "pick": "HOME"}) == []


def test_the_migration_is_bounded_to_the_folded_tail():
    from edgefactory.identity import migrate_folded_key
    assert migrate_folded_key("newcastleutd") == "newcastleunited"
    assert migrate_folded_key("ayrutd") == "ayrunited"
    assert migrate_folded_key("utd") == "utd"            # nothing before it
    assert migrate_folded_key("newcastleunited") == "newcastleunited"
    assert migrate_folded_key("scunthorpe") == "scunthorpe"
    assert migrate_folded_key("") == ""


def test_settlement_records_that_a_compatibility_key_answered(monkeypatch, tmp_path):
    """The migration must not be silent: a leg that settled through a stored
    pre-fold key is recorded, so the operator can see stored evidence ageing
    out of the current key space."""
    monkeypatch.setattr(at, "load_archived_picks", lambda: [
        {"date": "2026-10-05", "home": "Coventry", "away": "Newcastle Utd",
         "pick": "AWAY", "outcome": "away"}])
    monkeypatch.setattr(at, "load_settled_entries", lambda: {})
    monkeypatch.setattr(at, "load_settled_scores", lambda: {})
    # the archive row is the one the compat key must find; how it grades is
    # not this test's subject (grading it at all proves the row was reached)
    monkeypatch.setattr(at, "pick_result", lambda p, s: "win")
    at.LEGACY_KEY_HITS.clear()
    st = {"bank": 100.0, "base_pct": 10.0, "cycle_base": 10.0,
          "history": [], "events": [],
          "open_slips": [{"date": "2026-10-05", "staked_pct": 10.0, "accas": [{
              "odds": 1.47, "stake_pct": 10.0, "results": [None], "won": None,
              "legs": [{"match": "Coventry vs Newcastle Utd", "pick": "AWAY",
                        "prob": 0.64, "odds": 1.47, "result": None,
                        "fixture_key": ["2026-10-05", "coventry",
                                        "newcastleutd", "AWAY"]}]}]}]}
    _frozen(st, "2026-10-05")
    at.settle_open_slips(st, {})
    assert st["open_slips"] == []           # resolved, so the slip left the book
    assert st["history"][-1]["accas"][0]["won"] is True
    assert len(at.LEGACY_KEY_HITS) == 1
    record = at.LEGACY_KEY_HITS[0]
    assert record["slip_date"] == "2026-10-05"
    assert record["stored"][1:] == ("coventry", "newcastleutd", "AWAY")
    assert record["primary"][1:] == ("coventry", "newcastleutd", "AWAY")
    assert record["matched"][1:] == ("coventry", "newcastleunited", "AWAY")
    assert record["fixture"] == ["2026-10-05", "Coventry", "Newcastle Utd"]
    assert record["pick"] == "AWAY"
    at.LEGACY_KEY_HITS.clear()


# --- A1: the compatibility tier's guards -----------------------------------
#
# N-1(d)-(e) of the 2026-10-12 close-out: a hit must be a trail, not a
# counter; the tier must be refused when the matched row belongs to a
# different fixture; and the whole thing must have a removal criterion.

def _slip(day, stored, *, pick="AWAY", match="Coventry vs Newcastle Utd"):
    return {"date": day, "staked_pct": 10.0, "accas": [{
        "odds": 1.47, "stake_pct": 10.0, "results": [None], "won": None,
        "legs": [{"match": match, "pick": pick, "prob": 0.64, "odds": 1.47,
                  "result": None, "fixture_key": stored}]}]}


def _state(slip):
    st = {"bank": 100.0, "base_pct": 10.0, "cycle_base": 10.0,
          "history": [], "events": [], "open_slips": [slip]}
    # Only a frozen card is a placed bet, so a hand-built slip is frozen here.
    at.record_freeze(st, str(slip["date"]), datetime(2026, 10, 25, 9, 0, tzinfo=at.TZ))
    return st


def _frozen(st, *days):
    """Freeze hand-built slips (only a frozen card is a placed bet)."""
    for day in days:
        at.record_freeze(st, str(day), datetime(2026, 10, 25, 9, 0, tzinfo=at.TZ))
    return st


def _archive(day, home, away, *, pick="AWAY", outcome="away"):
    return {"date": day, "home": home, "away": away, "pick": pick,
            "outcome": outcome}


def _wire(monkeypatch, rows):
    monkeypatch.setattr(at, "load_archived_picks", lambda: rows)
    monkeypatch.setattr(at, "load_settled_entries", lambda: {})
    monkeypatch.setattr(at, "load_settled_scores", lambda: {})
    monkeypatch.setattr(at, "pick_result", lambda p, s: "win")
    at.LEGACY_KEY_HITS.clear()
    at.LEGACY_KEY_REFUSED.clear()


def test_a_compat_candidate_never_grades_another_fixture(monkeypatch, capsys):
    """A same-day pair whose keys collide: 'Newcastle Utd' and a different
    club 'Newcastle United' fold onto ONE key. The compat tier finds the
    other club's row - and must refuse it, because the row's own spelling
    does not reproduce the stored pre-fold key. The leg is held for the void
    timer instead, exactly like a missing row; nothing is re-attributed."""
    _wire(monkeypatch, [_archive("2026-10-05", "Coventry", "Newcastle United")])
    st = _state(_slip("2026-10-05",
                      ["2026-10-05", "coventry", "newcastleutd", "AWAY"]))
    lines = at.settle_open_slips(st, {})
    assert at.LEGACY_KEY_HITS == []                    # the other score was not taken
    assert len(at.LEGACY_KEY_REFUSED) == 1             # and the refusal is on the trail
    record = at.LEGACY_KEY_REFUSED[0]
    assert record["primary"][1:] == ("coventry", "newcastleutd", "AWAY")
    assert record["matched"][1:] == ("coventry", "newcastleunited", "AWAY")
    assert record["fixture"] == ["2026-10-05", "Coventry", "Newcastle United"]
    assert record["slip_date"] == "2026-10-05"
    assert "refused_because" in record
    assert st["open_slips"], "the leg must be held, never graded from another fixture"
    assert st["open_slips"][0]["accas"][0]["results"] == [None]
    assert any(line.startswith("compat key REFUSED") for line in lines)
    assert not any(line.startswith("compat key matched") for line in lines)


def test_the_same_collision_settles_when_the_row_is_the_leg_s_own_fixture(monkeypatch):
    """The control for the test above: the guard refuses the OTHER club, not
    compatibility in general. The identical slip settles when the archive row
    is its own fixture ('Newcastle Utd' - the spelling the fold moved)."""
    _wire(monkeypatch, [_archive("2026-10-05", "Coventry", "Newcastle Utd")])
    st = _state(_slip("2026-10-05",
                      ["2026-10-05", "coventry", "newcastleutd", "AWAY"]))
    lines = at.settle_open_slips(st, {})
    assert len(at.LEGACY_KEY_HITS) == 1 and at.LEGACY_KEY_REFUSED == []
    assert st["open_slips"] == []                      # settled
    matched = [line for line in lines if line.startswith("compat key matched")]
    assert len(matched) == 1
    # the journal names BOTH keys and the resolved fixture identity
    assert "newcastleutd" in matched[0] and "newcastleunited" in matched[0]
    assert "Newcastle Utd" in matched[0] and "2026-10-05" in matched[0]


def test_the_compat_tier_leaves_stored_keys_untouched(monkeypatch):
    """A1(c): the tier is read-only. The lookup must not mutate the leg, and
    the migrated spelling must never reach a state file - it is a candidate
    for comparison, never a value that gets written back."""
    leg = {"match": "Coventry vs Newcastle Utd", "pick": "AWAY", "prob": 0.64,
           "odds": 1.47, "result": None,
           "fixture_key": ["2026-10-05", "coventry", "newcastleutd", "AWAY"]}
    before = json.loads(json.dumps(leg))
    keys = at.leg_lookup_keys("2026-10-05", leg)
    assert keys[0][1:] == ("coventry", "newcastleutd", "AWAY")
    assert keys[1][1:] == ("coventry", "newcastleunited", "AWAY")
    assert leg == before, "the lookup must never rewrite the stored identity"

    _wire(monkeypatch, [_archive("2026-10-05", "Coventry", "Newcastle Utd")])
    st = _state(_slip("2026-10-05",
                      ["2026-10-05", "coventry", "newcastleutd", "AWAY"]))
    at.settle_open_slips(st, {})
    written = at.STATE_FILE.read_text()
    assert "newcastleunited" not in written, "the candidate was written back"
    assert "newcastleutd" in written or st["open_slips"] == []


def test_every_settlement_run_prints_a_compat_summary(monkeypatch, capsys):
    """A1(e): the sunset criterion is 'no hits for N consecutive runs', which
    is only checkable if every run states its count. The scalar prints even
    when there was no compatibility work at all, and the human trail stays out
    of `lines` unless a leg actually used the tier."""
    _wire(monkeypatch, [_archive("2026-10-05", "Coventry", "Newcastle Utd")])
    st = _state(_slip("2026-10-05", None))          # a text-path leg: no stored key
    lines = at.settle_open_slips(st, {})
    assert "settlement_compat_key_hits=0 refused=0" in capsys.readouterr().err
    assert not any(line.startswith("compat key") for line in lines)


def test_the_compat_tier_carries_a_dated_sunset_criterion():
    """A1(e): the criterion is written where the tier lives, not in a memo."""
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    assert "Sunset (dated TODO, 2026-10-12)" in src
    assert "0 hit(s) for 14" in src
    assert "no open slip's stored fixture_key fails the current fold" in src
