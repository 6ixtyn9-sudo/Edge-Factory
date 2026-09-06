"""Kickoff-guard tests (incident #6, 2026-09-06 Vancouver) — TWO layers.

The 2026-09-06 review split the original one-layer rewrite into:

1. LIVE guard (`auto_tickets.live_kickoff_guard`, wired into cmd_today): a
   leg rides only when its kickoff is usable AND not already started. A row
   with NO usable kickoff date — bare "22:30" (the Vancouver incident row),
   missing, garbage — is undatable and DROPS, counted in the run's skip
   census. Rows carrying a full calendar date (naive "2026-09-06 15:30:00",
   "05-09, 22:30", or an explicit offset/Z instant) are compared on the
   feeds' UTC+2 rendering via parse_kickoff, and started legs drop too.
2. AUDIT contract (`auto_tickets.kickoff_contract`, reached only from
   `replay_harness.py --kickoff-contract`, off by default): the fail-closed
   proof standard — a leg rides only when its kickoff is PROVEN by the row
   itself (explicit offset/Z, or naive + row-carried ``kickoff_tz``) to be at
   least KICKOFF_MIN_LEAD_HOURS after build time. It sizes the data-side
   fix; it is NOT the live betting rule (the review: proof-or-drop threw
   away the dated majority that renders UTC+2).

The deleted machinery — the league-substring -> IANA zone table that read
Vancouver as New York time, and a SAST default for BARE times — must never
come back in any shape.

Cases pinned (the brief's list, mapped onto each layer):
  - a finished match            (dated kickoff in the past -> live drop /
                                audit drop)
  - a naive-timestamp match     (live: rides if still ahead on the UTC+2
                                rendering; audit: unproven -> drop)
  - a KO 13:00 no-date match    ("13:00" -> no usable date -> live drop /
                                audit drop)
  - a west-coast match          (Vancouver incident row -> live drop; an
                                offset row is judged on absolute time)
  - a genuine future match      (rides on both layers)
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402


@pytest.fixture(autouse=True)
def _sandbox_state(tmp_path, monkeypatch):
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)


def _leg(tag, odds=1.50, prob=0.65, **row_extra):
    row = {"home": f"Team {tag}", "away": f"Other {tag}", "pick": "home",
           "date": "2026-09-06"}
    row.update(row_extra)
    return {"match": f"Team {tag} vs Other {tag}", "pick": "HOME",
            "prob": prob, "odds": odds, "result": None, "row": row}


def _build09():
    """The canonical build instant used across these tests:
    2026-09-06 09:00 SAST (the freeze run)."""
    return at.canonical_build_instant("2026-09-06")


def _vancouver_leg():
    """The exact 2026-09-06 incident row: '22:30', no date, no offset, filed
    under 'USA,Major League Soccer'."""
    row = {"home": "Vancouver Whitecaps", "away": "St. Louis City",
           "pick": "home", "date": "2026-09-06", "kickoff": "22:30",
           "league": "USA,Major League Soccer", "odds_league": "Major League Soccer"}
    return {"match": "Vancouver Whitecaps vs St. Louis City", "pick": "HOME",
            "prob": 0.65, "odds": 1.45, "result": None, "row": row}


# ---------------- parse_kickoff_proven: proof, never assumption ----------------

def test_proven_parse_accepts_only_absolute_instants():
    p = _leg("A", kickoff="2026-09-06T20:15:00+02:00")["row"]
    kt = at.parse_kickoff_proven(p)
    assert kt is not None and kt.tzinfo is not None
    assert kt == datetime(2026, 9, 6, 18, 15, tzinfo=at._UTC)   # 20:15 SAST = 18:15 UTC

    pz = _leg("Z", kickoff="2026-09-06T02:30:00Z")["row"]
    assert at.parse_kickoff_proven(pz) == datetime(2026, 9, 6, 2, 30, tzinfo=at._UTC)

    poff = _leg("O", kickoff="2026-09-05T22:30:00-04:00")["row"]
    assert at.parse_kickoff_proven(poff) == datetime(2026, 9, 6, 2, 30, tzinfo=at._UTC)


def test_proven_parse_rejects_naive_without_row_carried_zone():
    """Naive timestamps are UNPROVEN unless the row itself names the zone.
    Never defaulted to Africa/Johannesburg (the incident's fault)."""
    assert at.parse_kickoff_proven(
        _leg("N", kickoff="2026-09-06 15:30:00")["row"]) is None
    # time-only, no date at all
    assert at.parse_kickoff_proven(
        _leg("T", kickoff="13:00")["row"]) is None
    # dd-mm day+month only, year inferred — still no zone, no proof
    assert at.parse_kickoff_proven(
        _leg("D", kickoff="05-09, 22:30")["row"]) is None
    # empty / missing
    assert at.parse_kickoff_proven(_leg("E", kickoff="")["row"]) is None
    row = _leg("M", kickoff="")["row"]
    row.pop("kickoff", None)
    assert at.parse_kickoff_proven(row) is None
    assert at.parse_kickoff_proven(_leg("G", kickoff="not a time")["row"]) is None
    # the OLD parser returned a SAST-stamped datetime for these — that
    # assumption is the bug class; pin that this path yields None.
    assert at.parse_kickoff_proven(
        _leg("V", kickoff="22:30", date="2026-09-06",
             league="USA,Major League Soccer")["row"]) is None


def test_proven_parse_uses_a_zone_carried_in_the_row_as_data():
    """A naive kickoff + explicit row-level IANA zone is PROVEN (the data
    fix path: a stadium/feed zone belongs in the row, not in a dict)."""
    row = _leg("W", kickoff="2026-09-06 19:30:00",
               kickoff_tz="America/Vancouver")["row"]
    kt = at.parse_kickoff_proven(row)
    # 19:30 PDT (UTC-7) = 2026-09-07 02:30 UTC
    assert kt == datetime(2026, 9, 7, 2, 30, tzinfo=at._UTC)

    # a bogus zone name is NOT proof
    bad = _leg("B", kickoff="2026-09-06 19:30:00",
               kickoff_tz="Not/AZone")["row"]
    assert at.parse_kickoff_proven(bad) is None

    # time-only strings stay unproven even with a zone (no calendar day)
    noon = _leg("P", kickoff="19:30", kickoff_tz="America/Vancouver")["row"]
    assert at.parse_kickoff_proven(noon) is None


# ---------------- live guard: usable date, started check, no zone guessing ----

def test_kickoff_has_usable_date_classifies_the_shapes():
    assert at.kickoff_has_usable_date(_leg("a", kickoff="2026-09-06T20:15:00+02:00")["row"])
    assert at.kickoff_has_usable_date(_leg("b", kickoff="2026-09-06 15:30:00")["row"])
    assert at.kickoff_has_usable_date(_leg("c", kickoff="05-09, 22:30")["row"])
    # bare time-only, missing, garbage: no usable date
    assert not at.kickoff_has_usable_date(_vancouver_leg()["row"])       # "22:30"
    assert not at.kickoff_has_usable_date(_leg("d", kickoff="13:00")["row"])
    assert not at.kickoff_has_usable_date(_leg("e", kickoff="")["row"])
    row = _leg("f", kickoff="")["row"]
    row.pop("kickoff", None)
    assert not at.kickoff_has_usable_date(row)
    assert not at.kickoff_has_usable_date(_leg("g", kickoff="not a time")["row"])


def test_live_guard_drops_the_vancouver_incident_row():
    """The exact incident shape ('22:30', no date) is undatable -> the live
    guard drops it before any comparison can go wrong."""
    pool = [_vancouver_leg()]
    kept, drops = at.live_kickoff_guard(pool, _build09())
    assert kept == []
    assert at.KO_SKIP_NO_DATE in drops
    assert drops[at.KO_SKIP_NO_DATE] == ["Vancouver Whitecaps vs St. Louis City"]


def test_live_guard_keeps_dated_naive_and_offset_future_rows():
    build = _build09()
    pool = [_leg("naive", kickoff="2026-09-06 15:30:00"),       # +6.5h, dated
            _leg("ddmm", kickoff="06-09, 15:30"),               # +6.5h, day-month
            _leg("off", kickoff="2026-09-06T20:15:00+02:00")]   # provable +11h
    kept, drops = at.live_kickoff_guard(pool, build)
    assert len(kept) == 3 and drops == {}


def test_live_guard_drops_started_dated_rows():
    build = _build09()
    pool = [_leg("pastnaive", kickoff="2026-09-06 08:00:00"),
            _leg("pastiso", kickoff="2026-09-06T02:30:00+00:00")]
    kept, drops = at.live_kickoff_guard(pool, build)
    assert kept == []
    assert at.KO_SKIP_STARTED in drops
    assert len(drops[at.KO_SKIP_STARTED]) == 2


def test_live_guard_drops_missing_and_garbage_rows():
    build = _build09()
    missing = _leg("gone", kickoff="")["row"]
    missing.pop("kickoff", None)
    pool = [{"match": "Team gone vs Other gone", "pick": "HOME",
             "prob": 0.65, "odds": 1.45, "result": None, "row": missing},
            _leg("junk", kickoff="next tuesday")]
    kept, drops = at.live_kickoff_guard(pool, build)
    assert kept == []
    assert at.KO_SKIP_NO_DATE in drops and len(drops[at.KO_SKIP_NO_DATE]) == 2


def test_live_guard_keeps_a_genuine_future_match():
    """A dated kickoff well ahead of the build rides on the live path (no
    4h lead buffer live; only already-started legs drop)."""
    pool = [_leg("zrin", kickoff="2026-09-06T20:15:00+02:00"),
            _leg("hearts", kickoff="2026-09-06T16:00:00+02:00")]
    kept, drops = at.live_kickoff_guard(pool, _build09())
    assert len(kept) == 2 and drops == {}


def test_live_guard_is_deliberately_weaker_than_the_audit_contract():
    """The review's split: naive-with-date rows are NOT dropped live (the
    feeds render them on a UTC+2 clock), while the audit contract — which
    sizes the data-side fix — still drops them as unproven."""
    build = _build09()
    pool = [_leg("naive", kickoff="2026-09-06 15:30:00")]
    live_kept, live_drops = at.live_kickoff_guard(pool, build)
    audit_kept, audit_drops = at.kickoff_contract(pool, build_at=build)
    assert len(live_kept) == 1 and live_drops == {}
    assert audit_kept == [] and at.KO_SKIP_UNPROVEN in audit_drops


# ---------------- audit contract: fail-closed proof standard ----------------

def test_finished_match_is_dropped():
    """A provable kickoff already in the past (02:30 UTC = the Vancouver
    incident's real kickoff) must not ride at the 09:00 build."""
    pool = [_leg("done", kickoff="2026-09-06T02:30:00+00:00")]
    kept, census = at.kickoff_contract(pool, _build09())
    assert kept == []
    assert len(census) == 1
    assert "already started" in next(iter(census))


def test_naive_timestamp_match_is_dropped_as_unproven():
    pool = [_leg("naive", kickoff="2026-09-06 15:30:00")]
    kept, census = at.kickoff_contract(pool, _build09())
    assert kept == []
    assert at.KO_SKIP_UNPROVEN in census


def test_no_date_ko_1300_is_dropped_as_unproven():
    pool = [_leg("timeno", kickoff="13:00")]
    kept, census = at.kickoff_contract(pool, _build09())
    assert kept == []
    assert at.KO_SKIP_UNPROVEN in census


def test_vancouver_incident_row_is_dropped_by_the_audit_contract():
    """The exact 2026-09-06 incident shape carries no proof at all; the
    fail-closed standard drops it (as does the live guard, via no-date)."""
    pool = [_vancouver_leg()]
    kept, census = at.kickoff_contract(pool, _build09())
    assert kept == []
    assert at.KO_SKIP_UNPROVEN in census


def test_west_coast_match_with_offset_is_judged_on_absolute_time():
    """A west-coast fixture whose row carries the real offset is PROVEN; the
    engine must compare in UTC, not guess New York/Toronto/Vancouver."""
    build = _build09()
    # 2026-09-06 19:30 PDT = 09-07 02:30 UTC — still ~17.5h ahead at 09:00 SAST
    future = [_leg("sea", kickoff="2026-09-06T19:30:00-07:00")]
    kept, census = at.kickoff_contract(future, build)
    assert len(kept) == 1 and census == {}

    # 2026-09-05 19:30 PDT = 09-06 02:30 UTC — already over at build time
    past = [_leg("sea", kickoff="2026-09-05T19:30:00-07:00")]
    kept2, census2 = at.kickoff_contract(past, build)
    assert kept2 == []
    assert len(census2) == 1 and "already started" in next(iter(census2))


def test_genuine_future_match_still_rides_the_audit_contract():
    """The audit standard must not throw the baby out: a proven kickoff well
    ahead of the build (Zrinjski, 20:15 SAST on the incident day) rides."""
    build = _build09()
    pool = [_leg("zrin", kickoff="2026-09-06T20:15:00+02:00"),
            _leg("hearts", kickoff="2026-09-06T16:00:00+02:00"),
            _leg("ghost", kickoff="22:30")]          # unprovable -> dropped
    kept, census = at.kickoff_contract(pool, build)
    assert len(kept) == 2
    assert [l["match"] for l in kept] == [
        "Team zrin vs Other zrin", "Team hearts vs Other hearts"]
    assert at.KO_SKIP_UNPROVEN in census and len(census[at.KO_SKIP_UNPROVEN]) == 1


def test_lead_buffer_boundary():
    """Audit contract: provable kickoffs inside the 4h lead buffer are
    dropped too (result feeds lag); the boundary is enforced."""
    build = _build09()
    def row_at(hours_ahead):
        kt = build.astimezone(at._UTC) + timedelta(hours=hours_ahead)
        iso = kt.isoformat(timespec="seconds")     # carries +00:00 offset
        return _leg(f"h{hours_ahead}", kickoff=iso)
    kept5, _ = at.kickoff_contract([row_at(5.0)], build)
    assert len(kept5) == 1
    kept3, census3 = at.kickoff_contract([row_at(3.0)], build)
    assert kept3 == [] and "already started" in next(iter(census3))
    kept0, census0 = at.kickoff_contract([row_at(-0.5)], build)
    assert kept0 == [] and "already started" in next(iter(census0))


def test_min_lead_hours_override():
    build = _build09()
    iso = (build.astimezone(at._UTC) + timedelta(hours=6)).isoformat(timespec="seconds")
    kept, _ = at.kickoff_contract([_leg("x", kickoff=iso)], build, min_lead_hours=8)
    assert kept == []
    kept2, _ = at.kickoff_contract([_leg("x", kickoff=iso)], build, min_lead_hours=4)
    assert len(kept2) == 1


def test_census_counts_and_limits_examples():
    pool = [_leg(f"n{i}", kickoff="13:00") for i in range(5)]
    kept, census = at.kickoff_contract(pool, _build09())
    assert kept == []
    assert len(census[at.KO_SKIP_UNPROVEN]) == 5
    lines = at.format_skip_census(7, 2, census, title="KICKOFF CONTRACT")
    assert any("5 " in ln and "unprovable" in ln for ln in lines)
    # at most three fixture names per reason line
    assert sum("Team n" in ln for ln in lines) <= 3


def test_skip_census_zero_drop_print():
    pool = [_leg("ok", kickoff="2026-09-06T20:15:00+02:00")]
    kept, census = at.live_kickoff_guard(pool, _build09())
    assert len(kept) == 1
    assert "0 dropped" in "\n".join(at.format_skip_census(1, 1, census))


def test_guard_source_has_no_zone_table_and_live_path_uses_the_live_guard():
    """The 2026-09-04 guard class is deleted: no league-substring zone dict
    may exist anywhere in auto_tickets.py, cmd_today must call the LIVE
    guard (not the audit contract), and the live guard must not use a
    SAST-defaulting parse on bare times."""
    src = (ROOT / "scripts" / "auto_tickets.py").read_text()
    assert "_AMERICAS_ZONES" not in src
    assert "_inferred_kickoff_utc" not in src and "_unprovable_future" not in src
    # zoneinfo is imported exactly once, at module top (never re-imported
    # inside cmd_today to build a lookup table)
    assert src.count("from zoneinfo import ZoneInfo") == 1
    assert at.parse_kickoff is not at.parse_kickoff_proven
    assert at.parse_kickoff.__doc__ and "NOT a bet-time proof" in at.parse_kickoff.__doc__
    # cmd_today wires the live guard; the audit contract is NOT on the live path
    body = src[src.index("def cmd_today"):src.index("def print_status")]
    assert "live_kickoff_guard(pool, now)" in body
    assert "kickoff_contract(pool" not in body
    guard_src = src[src.index("def live_kickoff_guard"):src.index("def parse_kickoff_proven")]
    assert "KO_SKIP_NO_DATE" in guard_src
    assert "KO_SKIP_STARTED" in guard_src


# ---------------- end-to-end: cmd_today on the incident-day shape ----------------

class _Clock(at.datetime):
    """Freeze 'now' at 2026-09-06 09:13 SAST (the incident build)."""
    @classmethod
    def now(cls, tz=None):
        return at.datetime(2026, 9, 6, 9, 13, tzinfo=tz or at.TZ)


def _slate_rows():
    """A synthetic picks_today.json echoing 2026-09-06's real shapes:
    tz-aware (Miami, started; Zrinjski + Hearts, future), naive-with-date
    (Wales 2), no-date (Rudes), and the Vancouver incident row."""
    rows = []
    for home, away, ko, odds in [
            ("Inter Miami", "Atlanta United FC", "2026-09-06T01:30:00+02:00", 1.33),
            ("Zrinjski", "Siroki Brijeg", "2026-09-06T20:15:00+02:00", 1.26),
            ("Heart of Midlothian", "Dundee", "2026-09-06T16:00:00+02:00", 1.47),
            ("Gresford Athletic", "Mold Alexandra", "2026-09-06 15:30:00", 1.45),
            ("Rudes", "HNK Hajduk Split", "16:00", 1.29),
            ("Vancouver Whitecaps", "St. Louis City", "22:30", 1.45),
    ]:
        rows.append({"date": "2026-09-06", "home": home, "away": away,
                     "kickoff": ko, "league": "x", "bucket": "CERTIFIED_CLEAN",
                     "market": "1x2", "pick": "home", "avg_p": 70.0, "odds": odds,
                     "quarantine": "none"})
    return rows


def test_cmd_today_live_guard_regression(tmp_path, monkeypatch):
    """cmd_today on the incident-day slate must drop Vancouver (bare, no
    usable date) and Rudes (bare), drop started Miami, KEEP the dated rows
    (Gresford rides — the naive-with-date majority is the feed's UTC+2
    rendering), print the census, and build the honest one-acca card."""
    monkeypatch.setattr(at, "datetime", _Clock)
    (at.LOCALDATA / "picks_today.json").write_text(
        json_dumps(_slate_rows()))
    st = at.fresh_state()
    args = SimpleNamespace(date="2026-09-06", force=False)
    rc = at.cmd_today(args, st)
    assert rc == 0
    txt = (at.LOCALDATA / "auto_tickets_2026-09-06.txt").read_text()
    ticket = txt.split("KICKOFF GUARD")[0]
    assert "Vancouver Whitecaps vs St. Louis City" not in ticket
    assert "Rudes vs HNK Hajduk Split" not in ticket
    assert "Heart of Midlothian vs Dundee" in ticket      # ranked 1
    assert "Gresford Athletic vs Mold Alexandra" in ticket  # dated-naive rides
    assert "Inter Miami vs Atlanta United FC" not in ticket  # started at 01:30 SAST
    assert "no usable kickoff date" in txt                # census: Vancouver+Rudes
    assert "already started" in txt                       # census: Miami
    # two kept legs pair into one acca; a single-ticket day risk
    assert "[ACCA #1]" in txt and "[ACCA #2]" not in txt
    # the 09:13 run is at/after the freeze hour -> the FINAL marker lands
    assert (at.LOCALDATA / "auto_tickets_2026-09-06.frozen").exists()
    # labels: the free-bank wording of Task 3 is on the ticket
    assert "free bank" in txt
    assert "total bank" in txt


import json as _json  # noqa: E402


def json_dumps(obj):
    return _json.dumps(obj, default=str)
