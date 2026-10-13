"""Dynamic per-slice floors (R2, 2026-10-12) — the derivation's own contract.

The floor hierarchy is market -> league -> team, derived from the settled
registry with the statistic the registry certifies with (``wilson_lb``). These
tests pin the rules that make it safe: inheritance, the evidence gate, the
tighten-only clamp, no lookahead, team slices never deviate, a floorless market
never gains a floor, and unattributed records inherit.
"""
import json
import math

from edgefactory.enh_registry import (ENHANCEMENT_PRICE_FLOORS, MIN_PRICED_N,
                                      UNATTRIBUTED_LEAGUE, clears_floor,
                                      derive_floors, floor_for_slice,
                                      record_outcome)


def _reg(markets):
    return {"version": 2, "markets": markets}


def _entry(recs, **extra):
    top = {"records": recs, "n": len(recs),
           "hits": sum(1 for r in recs if r.get("hit"))}
    top.update(extra)
    return top


def _rec(date_, hit, price=1.9, market="match_over_25@v1", **extra):
    rec = {"date": date_, "match": f"A vs B {date_}", "price": price,
           "hit": bool(hit), "source": "oddspapi", "multi_source": False,
           "bucket": "", "rule": "", "stated": None,
           "league": "", "home": "", "away": "", "home_key": "", "away_key": ""}
    rec.update(extra)
    return rec


def _mass(n, hits, market="match_over_25@v1", **extra):
    """`n` records dated across 2026-07/08/09 with exactly `hits` hits."""
    months = ("07", "08", "09")
    recs = []
    for i in range(n):
        month = months[i % len(months)]
        day = (i // len(months)) % 28 + 1
        recs.append(_rec(f"2026-{month}-{day:02d}", hit=(i < hits), market=market, **extra))
    return recs


def _derive(registry, as_of="2026-10-12", margin=0.10):
    return derive_floors(registry, as_of, parent_floors=ENHANCEMENT_PRICE_FLOORS,
                         margin=margin)


def _rows(derived, level, market=None):
    return [r for r in derived["rows"]
            if r["level"] == level and (market is None or r["market"] == market)]


# --- level 1: the market root ------------------------------------------------

def test_thin_market_inherits_the_operator_floor():
    reg = _reg({"match_over_25@v1": _entry([_rec("2026-09-01", True)])})
    row = _rows(_derive(reg), "market", "match_over_25")[0]
    assert row["gate"] is False
    assert row["floor"] == ENHANCEMENT_PRICE_FLOORS["match_over_25"]
    assert row["basis"] == "inherited"
    assert "thin" in row["reason"]


def test_market_evidence_tightens_the_operator_floor():
    # 350 priced, 231 hits: the real match_over_25 slice. Wilson LB 0.6089 ->
    # 1/0.6089 + 0.10 = 1.7424 > the operator's 1.60.
    reg = _reg({"match_over_25@v1": _entry(_mass(350, 231))})
    row = _rows(_derive(reg), "market", "match_over_25")[0]
    assert row["gate"] is True
    assert row["floor"] > ENHANCEMENT_PRICE_FLOORS["match_over_25"]
    assert row["basis"] == "market"
    assert math.isclose(row["floor"], 1.0 / row["wilson_lb"] + 0.10, rel_tol=1e-12)


def test_a_slice_can_never_land_below_its_parent():
    # A very high hit rate gives a candidate BELOW the operator's floor: the
    # clamp keeps the parent and the row says so. (Tighten-only.)
    recs = [_rec(f"2026-09-{d:02d}", hit=True) for d in range(1, 29)]
    recs += [_rec("2026-09-29", False), _rec("2026-09-30", True)]
    reg = _reg({"match_over_25@v1": _entry(recs)})
    row = _rows(_derive(reg), "market", "match_over_25")[0]
    assert row["gate"] is True
    assert row["candidate_floor"] < ENHANCEMENT_PRICE_FLOORS["match_over_25"]
    assert row["floor"] == ENHANCEMENT_PRICE_FLOORS["match_over_25"]
    assert row["basis"] == "inherited"
    assert "clamped" in row["reason"]


def test_floorless_market_never_gains_a_floor():
    # `match_over_45` has no operator floor. Strong evidence must NOT create one:
    # a market with no threshold cannot fire, and inventing a number would be
    # exactly the unvalidated betting the registry exists to prevent.
    reg = _reg({"match_over_45@v1": _entry(_mass(40, 38, market="match_over_45@v1"))})
    derived = _derive(reg)
    row = _rows(derived, "market", "match_over_45")[0]
    assert row["n"] >= MIN_PRICED_N
    assert row["floor"] is None and row["parent_floor"] is None
    assert row["basis"] == "inherited"
    assert "floorless" in row["reason"]
    assert derived["floors"]["match_over_45"]["floor"] is None
    assert clears_floor("match_over_45", 99.0, floor=row["floor"]) is False


# --- level 2: the league slice ----------------------------------------------

def test_league_slice_tightens_above_the_market_floor():
    # The market as a whole is strong (120 priced, 95 hits: Wilson LB ~0.72 ->
    # candidate ~1.49 under the operator's 1.60, so the market root stays at
    # 1.60). The weak league inside it (40 records, 18 hits: LB ~0.30 ->
    # candidate ~3.48) is the slice that tightens.
    weak = _mass(40, 18, league="Be1")
    strong = _mass(80, 77, league="England,Premier League")
    reg = _reg({"match_over_25@v1": _entry(weak + strong)})
    derived = _derive(reg)
    market_row = _rows(derived, "market", "match_over_25")[0]
    weak_row = [r for r in _rows(derived, "league", "match_over_25")
                if r["league"] == "Be1"][0]
    other_row = [r for r in _rows(derived, "league", "match_over_25")
                 if r["league"] == "England,Premier League"][0]
    assert market_row["basis"] == "inherited"
    assert weak_row["gate"] is True
    assert weak_row["floor"] > market_row["floor"]
    assert weak_row["basis"] == "league"
    assert floor_for_slice(derived, "match_over_25", "Be1") == (
        weak_row["floor"], "league")
    # A league whose own candidate is under the market floor keeps the market
    # floor (clamped) - the market's APPLIED floor, never the operator's root.
    assert other_row["floor"] == market_row["floor"]
    assert other_row["basis"] == "inherited"
    # ...and an unknown league falls back to the market root the same way
    assert floor_for_slice(derived, "match_over_25", "Nowhere,League") == (
        market_row["floor"], "inherited")


def test_thin_slice_self_disables_even_with_a_lucky_record():
    # n=6 with a lucky 5/6: the Wilson LB is wide, the slice stays on its
    # parent's floor. This is the pack's proof 2, at the derivation level.
    recs = _mass(6, 5, league="Scotland,Premiership")
    reg = _reg({"match_over_25@v1": _entry(recs)})
    row = [r for r in _rows(_derive(reg), "league", "match_over_25")
           if r["league"] == "Scotland,Premiership"][0]
    assert row["n"] == 6
    assert row["rate"] == 5 / 6
    assert row["gate"] is False
    assert row["floor"] == ENHANCEMENT_PRICE_FLOORS["match_over_25"]
    assert row["basis"] == "inherited"
    assert "thin" in row["reason"]


def test_unattributed_records_inherit_and_never_deviate():
    reg = _reg({"match_over_25@v1": _entry(_mass(40, 39))})   # no league on any record
    derived = _derive(reg)
    row = [r for r in _rows(derived, "league", "match_over_25")
           if r["league"] == UNATTRIBUTED_LEAGUE][0]
    assert row["gate"] is False and row["candidate_floor"] is None
    assert row["floor"] == _rows(derived, "market", "match_over_25")[0]["floor"]
    assert row["basis"] == "inherited"
    assert "no league recorded" in row["reason"]


# --- level 3: the team slice (report-only) ----------------------------------

def test_team_slice_never_deviates_but_reports_its_evidence():
    recs = _mass(35, 32, league="England,Premier League",
                 home="Team A", away="Team B", home_key="teama", away_key="teamb")
    reg = _reg({"match_over_25@v1": _entry(recs)})
    derived = _derive(reg)
    team_rows = [r for r in _rows(derived, "team", "match_over_25")
                 if r["team"] == "teama"]
    assert len(team_rows) == 1
    row = team_rows[0]
    assert row["gate"] is True and row["candidate_floor"] is not None
    assert row["basis"] == "team"                    # labelled: its own evidence
    league_row = [r for r in _rows(derived, "league", "match_over_25")
                  if r["league"] == "England,Premier League"][0]
    assert row["floor"] == league_row["floor"]        # ...but the floor is inherited
    assert "not applied" in row["reason"]
    # A team slice is never consulted for a leg's applied floor.
    assert floor_for_slice(derived, "match_over_25", "England,Premier League")[0] == \
        league_row["floor"]


# --- the two hard rules: no lookahead, determinism --------------------------

def test_no_lookahead_same_day_records_do_not_move_the_table():
    recs = _mass(10, 8)
    reg = _reg({"match_over_25@v1": _entry(recs)})
    before = _derive(reg, as_of="2026-10-12")
    reg2 = _reg({"match_over_25@v1": _entry(recs + [
        _rec("2026-10-12", True, market="match_over_25@v1"),
        _rec("2026-10-13", True, market="match_over_25@v1")])})
    after = _derive(reg2, as_of="2026-10-12")
    assert json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)


def test_derivation_is_pure_and_does_not_mutate_the_registry():
    reg = _reg({"match_over_25@v1": _entry([
        _rec("2026-09-01", True, market="match_over_25@v1", league="De1"),
        _rec("2026-09-02", False, market="match_over_25@v1", league="De1")])})
    snapshot = json.dumps(reg, sort_keys=True)
    first = _derive(reg)
    second = _derive(reg)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert json.dumps(reg, sort_keys=True) == snapshot
    assert first["as_of"] == "2026-10-12" and first["margin"] == 0.10
    assert first["min_n"] == MIN_PRICED_N


def test_every_row_carries_a_reason_and_a_known_basis():
    reg = _reg({"match_over_25@v1": _entry([
        _rec("2026-09-01", True, market="match_over_25@v1", league="De1",
             home="Team A", away="Team B", home_key="teama", away_key="teamb")])})
    derived = _derive(reg)
    assert derived["rows"], "the derivation must emit rows"
    for row in derived["rows"]:
        assert row["basis"] in {"inherited", "market", "league", "team"}
        assert isinstance(row["reason"], str) and row["reason"]
        assert row["level"] in {"market", "league", "team"}


# --- the gate itself --------------------------------------------------------

def test_clears_floor_with_a_derived_floor_keeps_the_one_validity_rule():
    assert clears_floor("match_over_25", 1.80, floor=1.742374077011006) is True
    assert clears_floor("match_over_25", 1.70, floor=1.742374077011006) is False
    for junk in (True, "1.8", None, float("nan"), float("inf"), 1.0, 0.5):
        assert clears_floor("match_over_25", junk, floor=1.742374077011006) is False
    for bad_floor in (True, "1.6", float("nan")):
        assert clears_floor("match_over_25", 9.0, floor=bad_floor) is False
    # The default path is the operator's table, unchanged.
    assert clears_floor("match_over_25", 1.60) is True
    assert clears_floor("match_over_45", 9.0) is False


def test_unknown_versions_and_junk_registries_yield_no_rows():
    for junk in ({}, {"markets": None}, {"markets": {"x": {"records": None}}},
                 {"markets": {"x": {"records": ["nope", {"price": "1.9"}]}}}):
        derived = _derive(junk)
        assert derived["rows"] == [] or all(not r["gate"] for r in derived["rows"])
        assert derived["coverage"]["priced"] == 0


# --- settle-time recording (the plumbing) ----------------------------------

def test_record_outcome_records_league_and_team_keys_additively(tmp_path):
    res = record_outcome(tmp_path, date_="2026-10-11", match="Team A vs Team B",
                         market="match_over_25", price=1.9, hit=True,
                         source="oddspapi", league="England,Premier League",
                         home="Team A", away="Team B")
    assert res["recorded"] is True
    reg = json.loads((tmp_path / "localdata" / "enhancement_registry.json").read_text())
    rec = reg["markets"]["match_over_25@v1"]["records"][0]
    assert rec["league"] == "England,Premier League"
    assert rec["home"] == "Team A" and rec["away"] == "Team B"
    assert rec["home_key"] and rec["away_key"]
    # dedup key unchanged: the same outcome is still one record
    again = record_outcome(tmp_path, date_="2026-10-11", match="Team A vs Team B",
                           market="match_over_25", price=1.9, hit=True,
                           source="oddspapi", league="England,Premier League",
                           home="Team A", away="Team B")
    assert again["recorded"] is False
    assert len(reg["markets"]["match_over_25@v1"]["records"]) == 1


def test_records_without_slice_fields_still_record(tmp_path):
    res = record_outcome(tmp_path, date_="2026-10-11", match="Team A vs Team B",
                         market="match_over_25", price=1.9, hit=True)
    assert res["recorded"] is True
    reg = json.loads((tmp_path / "localdata" / "enhancement_registry.json").read_text())
    rec = reg["markets"]["match_over_25@v1"]["records"][0]
    assert rec["league"] == "" and rec["home_key"] == ""
