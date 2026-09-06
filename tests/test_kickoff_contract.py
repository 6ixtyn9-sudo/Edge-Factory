"""Kickoff-guard tests (incident #6, 2026-09-06 Vancouver) — TWO layers.

The 2026-09-06 review split the original one-layer rewrite into:

1. LIVE guard (`auto_tickets.live_kickoff_guard`, wired into cmd_today): a
   leg rides only when its kickoff is usable AND not already started. Drops,
   in order: missing/garbage kickoffs; CLOCK-ONLY kickoffs (bare "22:30" —
   the Vancouver incident row — or no-year "05-09, 22:30") whose league
   region's clock is far from SAST (Americas / Asia-Pacific — the region
   list never computes a kickoff, it only judges whether the SAST reading of
   the clock is trustworthy); and dated legs already started at build time
   (compared on the feeds' UTC+2 rendering via parse_kickoff). Clock-only
   rows from Europe/Africa ride.
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
    assert at.kickoff_has_usable_date(_leg("c", kickoff="05-09, 22:30")["row"])  # day-month
    # bare time-only, missing, garbage: no usable date
    assert not at.kickoff_has_usable_date(_vancouver_leg()["row"])       # "22:30"
    assert not at.kickoff_has_usable_date(_leg("d", kickoff="13:00")["row"])
    assert not at.kickoff_has_usable_date(_leg("e", kickoff="")["row"])
    row = _leg("f", kickoff="")["row"]
    row.pop("kickoff", None)
    assert not at.kickoff_has_usable_date(row)
    assert not at.kickoff_has_usable_date(_leg("g", kickoff="not a time")["row"])


def test_remote_clock_region_classifier_is_boolean_only():
    """The region list answers ONE question — is SAST rendering of this
    clock trustworthy? — and never computes a kickoff instant."""
    assert at.kickoff_clock_region_is_remote(
        _vancouver_leg()["row"])                                     # USA, MLS
    assert at.kickoff_clock_region_is_remote(
        _leg("sea", league="USA: MLS")["row"])
    assert at.kickoff_clock_region_is_remote(
        _leg("k", league_raw="South Korea,K-league 2")["row"])
    assert at.kickoff_clock_region_is_remote(
        _leg("aus", league_raw="Australia,Northern New South Wales")["row"])
    assert at.kickoff_clock_region_is_remote(
        _leg("mx", league="Mexico,Liga Mx Apertura")["row"])
    assert at.kickoff_clock_region_is_remote(
        _leg("sa", league_raw="International,Copa Sudamericana Knockout Stage")["row"])
    # Europe / Africa and unclassified-international rows are NOT remote
    assert not at.kickoff_clock_region_is_remote(
        _leg("hr", league_raw="Croatia,Hnl")["row"])
    assert not at.kickoff_clock_region_is_remote(
        _leg("eng", league_raw="England,National League")["row"])
    assert not at.kickoff_clock_region_is_remote(
        _leg("cl", league_raw="International,Champions League Playoff Round")["row"])


def test_live_guard_drops_the_vancouver_incident_row():
    """The exact incident shape ('22:30', no date, MLS) is a clock-only
    kickoff in a remote-clock region -> the live guard drops it before any
    comparison can go wrong."""
    pool = [_vancouver_leg()]
    kept, drops = at.live_kickoff_guard(pool, _build09())
    assert kept == []
    assert at.KO_SKIP_REMOTE_CLOCK in drops
    assert drops[at.KO_SKIP_REMOTE_CLOCK] == ["Vancouver Whitecaps vs St. Louis City"]


def test_live_guard_keeps_european_clock_only_rows():
    """A bare '16:00' Croatian clock read on the SAST slate day is right to
    within ~1h and historically safe (39 of 47 bare legs); it rides."""
    build = _build09()
    pool = [_leg("rudes", kickoff="16:00", league_raw="Croatia,Hnl"),
            _leg("dane", kickoff="15:00", league_raw="Denmark,Superligaen"),
            _leg("eng", kickoff="13:00", league_raw="England,National League")]
    kept, drops = at.live_kickoff_guard(pool, build)
    assert len(kept) == 3 and drops == {}
    # ...unless that European clock is ALREADY past at build time
    early = [_leg("no", kickoff="08:00", league_raw="Norway,1. Division")]
    kept2, drops2 = at.live_kickoff_guard(early, build)
    assert kept2 == [] and at.KO_SKIP_STARTED in drops2


def test_live_guard_drops_remote_region_clock_only_rows():
    """The eight named near-miss rows + the class: remote-region clock-only
    rows drop regardless of how 'future' the SAST reading looks."""
    build = _build09()
    cases = [
        ("Suwon Bluewings vs Gimhae City", "04:00", "South Korea,K-league 2"),
        ("Seattle Sounders vs Austin FC", "21:30", "USA,Major League Soccer"),
        ("Penarol vs Central Espanol", "22:30", "Uruguay,Liga Auf Clausura"),
        ("Toluca vs FC Juarez", "20:00", "Mexico,Liga Mx Apertura"),
        ("Broadmeadow Magic vs Charlestown Azzurri", "21:00",
         "Australia,Northern New South Wales"),
    ]
    pool = [_leg("x", kickoff=ko, league_raw=lg) for _, ko, lg in cases]
    kept, drops = at.live_kickoff_guard(pool, build)
    assert kept == []
    assert len(drops[at.KO_SKIP_REMOTE_CLOCK]) == len(cases)


def test_live_guard_keeps_dated_naive_and_offset_future_rows():
    build = _build09()
    pool = [_leg("naive", kickoff="2026-09-06 15:30:00"),       # +6.5h, dated
            _leg("ddmm", kickoff="06-09, 15:30"),               # +6.5h, day-month
            _leg("off", kickoff="2026-09-06T20:15:00+02:00")]   # provable +11h
    kept, drops = at.live_kickoff_guard(pool, build)
    assert len(kept) == 3 and drops == {}


def test_live_guard_drops_remote_region_yearless_day_month_rows():
    """Yearless 'DD-MM, HH:MM' in a remote-clock region is the same hazard as
    a bare clock (no year, no zone; clock read on the SAST slate day). In
    Europe it parses day-first (source convention) with the slate year."""
    build = _build09()
    aus = [_leg("aus", kickoff="04-07, 10:30", league_raw="Australia Queensland NPL")]
    kept, drops = at.live_kickoff_guard(aus, build)
    assert kept == [] and at.KO_SKIP_REMOTE_CLOCK in drops
    # Europe day-month rows ride and parse day-first: '06-09, 15:30' = 6 Sep.
    eur = [_leg("swe", kickoff="06-09, 15:30", league_raw="Sweden Allsvenskan")]
    kept2, drops2 = at.live_kickoff_guard(eur, build)
    assert len(kept2) == 1 and drops2 == {}
    parsed = at.parse_kickoff(kept2[0]["row"])
    assert parsed is not None and parsed.day == 6 and parsed.month == 9


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
    assert "KO_SKIP_REMOTE_CLOCK" in guard_src
    assert "KO_SKIP_STARTED" in guard_src
    # the region classifier is boolean-only: present, and used by the guard
    assert "_REMOTE_CLOCK_REGION_HINTS" in src
    assert "kickoff_clock_region_is_remote" in guard_src


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
    for home, away, ko, odds, league in [
            ("Inter Miami", "Atlanta United FC", "2026-09-06T01:30:00+02:00", 1.33, "x"),
            ("Zrinjski", "Siroki Brijeg", "2026-09-06T20:15:00+02:00", 1.26, "x"),
            ("Heart of Midlothian", "Dundee", "2026-09-06T16:00:00+02:00", 1.47, "x"),
            ("Gresford Athletic", "Mold Alexandra", "2026-09-06 15:30:00", 1.45, "x"),
            ("Rudes", "HNK Hajduk Split", "16:00", 1.29, "Croatia,Hnl"),
            ("Vancouver Whitecaps", "St. Louis City", "22:30", 1.45,
             "USA,Major League Soccer"),
    ]:
        rows.append({"date": "2026-09-06", "home": home, "away": away,
                     "kickoff": ko, "league": league, "bucket": "CERTIFIED_CLEAN",
                     "market": "1x2", "pick": "home", "avg_p": 70.0, "odds": odds,
                     "quarantine": "none"})
    return rows


def test_cmd_today_live_guard_regression(tmp_path, monkeypatch):
    """cmd_today on the incident-day slate must drop Vancouver (clock-only,
    MLS — remote-clock region) and started Miami, KEEP Rudes (clock-only but
    Croatia — Europe rides) and the dated rows (Gresford rides), print the
    census, and build the two-acca card from the four surviving legs."""
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
    assert "Inter Miami vs Atlanta United FC" not in ticket  # started at 01:30 SAST
    assert "Heart of Midlothian vs Dundee" in ticket      # ranked 1
    assert "Gresford Athletic vs Mold Alexandra" in ticket  # dated-naive rides
    assert "Rudes vs HNK Hajduk Split" in ticket          # Croatia clock-only rides
    assert "far from sast" in txt                         # census: Vancouver
    assert "already started" in txt                       # census: Miami
    # four kept legs pair into two accas (single-ticket-day risk split)
    assert "[ACCA #1]" in txt and "[ACCA #2]" in txt and "[ACCA #3]" not in txt
    # the 09:13 run is at/after the freeze hour -> the FINAL marker lands
    assert (at.LOCALDATA / "auto_tickets_2026-09-06.frozen").exists()
    # labels: the free-bank wording of Task 3 is on the ticket
    assert "free bank" in txt
    assert "total bank" in txt


# ---------------- Task A: ingest normalisation (kickoff_utc) ----------------
# picks_today.py emits kickoff_utc / kickoff_source / kickoff_witness per pick
# from explicit zone-bearing witnesses ONLY. No guesses, no SAST defaulting.

import picks_today as pt  # noqa: E402

_UTC_STR = "2026-09-06T02:30:00+00:00"


def _ss_row(home="Vancouver Whitecaps", away="St. Louis City", kickoff="2026-09-06T02:30:00Z"):
    """A fetch-time scoutingstats row for the Vancouver fixture (the real
    incident witness: starting_at carries the kickoff with a zone)."""
    return {"home": home, "away": away, "kickoff": kickoff, "league": "USA,Major League Soccer"}


def _fixture_data(*rows):
    by_key = {}
    for r in rows:
        k = (pt.source_team_key(r["home"]), pt.source_team_key(r["away"]))
        by_key[k] = r
    return {"scoutingstats": by_key, "statarea": by_key}  # eval-style fetch_all dict


def test_zoned_kickoff_to_utc_accepts_only_zone_bearing_strings():
    assert pt.zoned_kickoff_to_utc("2026-09-06T02:30:00Z") == _UTC_STR
    assert pt.zoned_kickoff_to_utc("2026-09-06T02:30:00+00:00") == _UTC_STR
    assert pt.zoned_kickoff_to_utc("2026-09-06T20:15:00+02:00") == "2026-09-06T18:15:00+00:00"
    # no-colon offset tolerated
    assert pt.zoned_kickoff_to_utc("2026-09-06T20:15:00+0200") == "2026-09-06T18:15:00+00:00"
    # naive strings name no zone -> None, never SAST-defaulted (incident class)
    assert pt.zoned_kickoff_to_utc("22:30") is None
    assert pt.zoned_kickoff_to_utc("06-09, 22:30") is None
    assert pt.zoned_kickoff_to_utc("2026-09-06 22:30") is None
    assert pt.zoned_kickoff_to_utc("2026-09-06T22:30:00") is None
    assert pt.zoned_kickoff_to_utc("") is None
    assert pt.zoned_kickoff_to_utc("not a time") is None
    assert pt.zoned_kickoff_to_utc(None) is None


def test_resolve_own_offset_kickoff_passthrough():
    pick = _vancouver_leg()["row"]
    pick["kickoff"] = "2026-09-06T20:15:00+02:00"      # Inter-Miami shape
    pt.resolve_kickoff_utc(pick, data={})
    assert pick["kickoff_utc"] == "2026-09-06T18:15:00+00:00"
    assert pick["kickoff_source"] == pt.KICKOFF_SRC_OFFSET
    assert "own kickoff" in pick["kickoff_witness"]
    assert pick["kickoff"] == "2026-09-06T20:15:00+02:00"   # raw never overwritten


def test_resolve_bare_time_without_witness_stays_unresolved():
    """The incident row alone ('22:30', MLS) has no zone witness -> unresolved.
    Crucially it must NOT be SAST-stamped into a kickoff_utc."""
    pick = _vancouver_leg()["row"]
    pt.resolve_kickoff_utc(pick, data={})
    assert pick["kickoff_utc"] is None
    assert pick["kickoff_source"] == pt.KICKOFF_SRC_UNRESOLVED
    assert pick["kickoff"] == "22:30"


def test_resolve_derives_from_zoned_sibling_source_row():
    """The Vancouver fix: the SAME fixture's scoutingstats row carried
    starting_at '2026-09-06T02:30:00Z' at fetch time. Normalisation uses it."""
    pick = _vancouver_leg()["row"]
    pt.resolve_kickoff_utc(pick, data=_fixture_data(_ss_row()))
    assert pick["kickoff_utc"] == _UTC_STR
    assert pick["kickoff_source"] == pt.KICKOFF_SRC_SIBLING
    assert "scoutingstats" in pick["kickoff_witness"]
    assert "02:30:00Z" in pick["kickoff_witness"]


def test_resolve_derives_from_matched_odds_row_at_enrichment():
    """Enrichment-time hook: odds rows fetched after the run-day scan can
    still carry a zoned kickoff (scoutingstats rows do)."""
    pick = _vancouver_leg()["row"]
    odds_row = {"home": "Vancouver Whitecaps", "away": "St. Louis City",
                "kickoff": "2026-09-06T02:30:00Z", "odds": 1.45,
                "captured_at": "2026-09-06T02:30:00Z"}
    pt.resolve_kickoff_utc(pick, data={}, odds_row=odds_row,
                           odds_provider="scoutingstats_odds")
    assert pick["kickoff_utc"] == _UTC_STR
    assert pick["kickoff_source"] == pt.KICKOFF_SRC_ODDS_ROW


def test_resolve_never_uses_a_capture_timestamp_as_a_kickoff_witness():
    """bzzoiro/betexplorer/theoddsapi odds rows carry TRUE capture timestamps
    (odds_captured_at / captured_at). Only the row's kickoff/time key may
    witness a kickoff — a capture instant is not a kickoff instant."""
    pick = _vancouver_leg()["row"]
    odds_row = {"home": "Vancouver Whitecaps", "away": "St. Louis City",
                "odds": 1.45, "captured_at": "2026-09-06T02:30:00+00:00",
                "bookmaker": "betexplorer"}          # no kickoff/time key
    pt.resolve_kickoff_utc(pick, data={}, odds_row=odds_row,
                           odds_provider="betexplorer_odds")
    assert pick["kickoff_utc"] is None
    assert pick["kickoff_source"] == pt.KICKOFF_SRC_UNRESOLVED


def test_resolve_conflicting_zoned_witnesses_stays_unresolved():
    """Two different absolute instants for one fixture (a rescheduled match,
    one stale row) -> unresolved; guessing which witness is right is the
    fault class. The guard's region fallback still covers the row."""
    pick = _vancouver_leg()["row"]
    key = (pt.source_team_key("Vancouver Whitecaps"),
           pt.source_team_key("St. Louis City"))
    data = {"scoutingstats": {key: _ss_row(kickoff="2026-09-06T02:30:00Z")},
            "vitibet": {key: _ss_row(kickoff="2026-09-06T03:30:00Z")}}
    pt.resolve_kickoff_utc(pick, data=data)
    assert pick["kickoff_utc"] is None
    assert pick["kickoff_source"] == pt.KICKOFF_SRC_UNRESOLVED
    assert "conflict" in pick["kickoff_witness"]


def test_resolve_is_idempotent_and_never_overwrites():
    pick = _vancouver_leg()["row"]
    pick["kickoff_utc"] = _UTC_STR
    pick["kickoff_source"] = pt.KICKOFF_SRC_SIBLING
    pick["kickoff_witness"] = "already set"
    # a later enrichment call must not overwrite the run-day verdict
    odds_row = {"home": "Vancouver Whitecaps", "away": "St. Louis City",
                "kickoff": "2026-09-06T09:00:00Z", "odds": 1.45}
    pt.resolve_kickoff_utc(pick, data=_fixture_data(), odds_row=odds_row,
                           odds_provider="scoutingstats_odds")
    assert pick["kickoff_utc"] == _UTC_STR
    assert pick["kickoff_source"] == pt.KICKOFF_SRC_SIBLING


# ---------------- Task A: guard keyed to kickoff_utc, region rule as fallback

def test_guard_rides_resolved_future_row_regardless_of_remote_clock():
    """A clock-only-region row (the Vancouver incident shape) that ingest
    normalisation resolved to a FUTURE absolute instant rides: the guard
    judges only the instant, no region guess."""
    leg = _vancouver_leg()
    leg["row"]["kickoff_utc"] = "2026-09-06T12:00:00+00:00"     # 14:00 SAST
    leg["row"]["kickoff_source"] = pt.KICKOFF_SRC_SIBLING
    kept, drops = at.live_kickoff_guard([leg], _build09())
    assert [l["match"] for l in kept] == ["Vancouver Whitecaps vs St. Louis City"]
    assert drops == {}


def test_guard_drops_resolved_row_only_if_already_started():
    """Vancouver's real instant (02:30 UTC = 04:30 SAST) is before the 09:00
    build: normalisation does not resurrect it — it drops as STARTED (the
    true reason), never as a remote-clock guess."""
    leg = _vancouver_leg()
    leg["row"]["kickoff_utc"] = _UTC_STR
    leg["row"]["kickoff_source"] = pt.KICKOFF_SRC_SIBLING
    kept, drops = at.live_kickoff_guard([leg], _build09())
    assert kept == []
    assert at.KO_SKIP_STARTED in drops
    assert at.KO_SKIP_REMOTE_CLOCK not in drops


def test_guard_falls_back_to_region_rule_for_unresolved_rows():
    """No kickoff_utc (normalisation could not resolve) -> the previous
    region rule still applies to the incident shape. Behaviour unchanged
    for unresolved rows."""
    leg = _vancouver_leg()
    leg["row"]["kickoff_utc"] = None
    leg["row"]["kickoff_source"] = pt.KICKOFF_SRC_UNRESOLVED
    kept, drops = at.live_kickoff_guard([leg], _build09())
    assert kept == []
    assert drops[at.KO_SKIP_REMOTE_CLOCK] == ["Vancouver Whitecaps vs St. Louis City"]


def test_proven_parse_prefers_kickoff_utc_over_the_raw_string():
    """The audit contract reads the normalised absolute instant first: a row
    whose raw kickoff is the bare '22:30' but whose kickoff_utc is resolved
    IS provable (proven from the witness, not from the raw rendering)."""
    row = _vancouver_leg()["row"]
    row["kickoff_utc"] = _UTC_STR
    row["kickoff_source"] = pt.KICKOFF_SRC_SIBLING
    kt = at.parse_kickoff_proven(row)
    assert kt == datetime(2026, 9, 6, 2, 30, tzinfo=at._UTC)


def test_kickoff_utc_from_archived_row_accepts_only_archive_witnesses():
    """Replay-side reconstruction (replay_harness normalised arm)."""
    # own zoned ISO kickoff -> offset passthrough
    row = _vancouver_leg()["row"]
    row["kickoff"] = "2026-09-06T20:15:00+02:00"
    ku, src = at.kickoff_utc_from_archived_row(row)
    assert ku == "2026-09-06T18:15:00+00:00" and src == "offset_passthrough"
    # scoutingstats odds row: odds_captured_at IS the fixture's starting_at
    # (the adapter stores the kickoff string into captured_at)
    row2 = _vancouver_leg()["row"]
    row2["odds_source"] = "scoutingstats_odds"
    row2["odds_captured_at"] = "2026-09-06T02:30:00Z"
    ku2, src2 = at.kickoff_utc_from_archived_row(row2)
    assert ku2 == _UTC_STR and src2 == "derived_odds_row"
    # bzzoiro/betexplorer odds rows: captured_at is a TRUE capture stamp,
    # never a kickoff witness (Vancouver's own row had a betexplorer-style
    # match fallback in history — this pins the refusal).
    row3 = _vancouver_leg()["row"]
    row3["odds_source"] = "betexplorer_odds"
    row3["odds_captured_at"] = "2026-09-06T19:18:30.970025+00:00"
    ku3, src3 = at.kickoff_utc_from_archived_row(row3)
    assert ku3 is None and src3 is None
    # naive strings never resolve
    row4 = _vancouver_leg()["row"]
    row4["odds_source"] = "scoutingstats_odds"
    row4["odds_captured_at"] = "22:30"
    assert at.kickoff_utc_from_archived_row(row4) == (None, None)


import json as _json  # noqa: E402


def json_dumps(obj):
    return _json.dumps(obj, default=str)
